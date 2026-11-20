#!/usr/bin/env python3
"""
HACK THE HACKER — Live Capture & Ingestion Daemon
===================================================
Continuously captures network traffic from VirtualBox VMs via NIC tracing,
parses packets in real-time, ingests them into the backend database,
runs detection rules, and correlates attack sessions — all automatically.

The SOC Dashboard (which polls every 3-5 seconds) will show attacks LIVE.

Usage:
    cd backend
    .\\venv\\Scripts\\python.exe ..\\scripts\\live_capture_daemon.py

Press Ctrl+C to stop.
"""

import os
import sys
import time
import json
import shutil
import signal
import logging
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# Add backend to path so we can import app modules
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
BACKEND_DIR = PROJECT_DIR / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.config import get_settings
from app.database.connection import SessionLocal, init_db
from app.ingestion.event_ingestor import EventIngestor
from app.detection.rule_engine import DetectionEngine
from app.intelligence.correlation import EventCorrelationEngine

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
settings = get_settings()

VBOXMANAGE = settings.VBOXMANAGE_PATH
VM_NAME = "Metasploitable 2"
KALI_VM_NAME = "kali-linux-2026.3-virtualbox-amd64"
CAPTURE_DIR = PROJECT_DIR / "monitoring" / "captures"
CAPTURE_DIR.mkdir(parents=True, exist_ok=True)

# How often to harvest the pcap (seconds)
POLL_INTERVAL = 4

# Lab IP mapping — the PCAP may show DHCP-assigned IPs instead of static ones
# Map them back to the canonical lab IPs for consistent dashboard display
IP_ALIAS_MAP = {
    "192.168.56.101": "192.168.56.30",   # Metasploitable alternate
    "192.168.56.102": "192.168.56.20",   # Kali alternate
    "192.168.56.103": "192.168.56.20",   # Kali alternate (DHCP)
}

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("live_capture")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
running = True

def signal_handler(sig, frame):
    global running
    log.info("Shutdown signal received. Cleaning up...")
    running = False

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def vbox_cmd(*args):
    """Run a VBoxManage command and return (success, output)."""
    cmd = [VBOXMANAGE] + list(args)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return result.returncode == 0, result.stdout.strip()
    except Exception as e:
        return False, str(e)


def enable_nictrace(vm_name, nic_num, pcap_path):
    """Enable NIC tracing on a VM."""
    ok1, _ = vbox_cmd("controlvm", vm_name, f"nictracefile{nic_num}", str(pcap_path))
    ok2, _ = vbox_cmd("controlvm", vm_name, f"nictrace{nic_num}", "on")
    return ok1 and ok2


def disable_nictrace(vm_name, nic_num):
    """Disable NIC tracing on a VM."""
    vbox_cmd("controlvm", vm_name, f"nictrace{nic_num}", "off")


def resolve_ip(ip):
    """Map DHCP-assigned IPs back to canonical lab IPs."""
    return IP_ALIAS_MAP.get(ip, ip)


def parse_pcap_incremental(filepath, last_count=0):
    """Parse a PCAP file and return only packets after last_count."""
    try:
        from scapy.all import rdpcap, IP, TCP, UDP, ICMP
    except ImportError:
        log.error("Scapy not installed! Run: pip install scapy")
        return [], 0

    if not os.path.exists(filepath) or os.path.getsize(filepath) < 50:
        return [], last_count

    try:
        packets = rdpcap(str(filepath))
    except Exception as e:
        log.debug(f"PCAP read error (file may be in use): {e}")
        return [], last_count

    total = len(packets)
    if total <= last_count:
        return [], last_count

    new_packets = packets[last_count:]
    events = []
    now = datetime.utcnow()

    # Determine timestamp anchoring
    first_raw = float(packets[0].time) if packets else 0.0
    is_relative = first_raw < 1_000_000_000.0

    for pkt in new_packets:
        if not pkt.haslayer(IP):
            continue

        ip_layer = pkt.getlayer(IP)
        src_ip = resolve_ip(ip_layer.src)
        dst_ip = resolve_ip(ip_layer.dst)
        proto = "IP"
        src_port = None
        dst_port = None
        flags = ""

        if pkt.haslayer(TCP):
            tcp = pkt.getlayer(TCP)
            proto = "TCP"
            src_port = tcp.sport
            dst_port = tcp.dport
            flags = str(tcp.flags)
        elif pkt.haslayer(UDP):
            udp = pkt.getlayer(UDP)
            proto = "UDP"
            src_port = udp.sport
            dst_port = udp.dport
        elif pkt.haslayer(ICMP):
            proto = "ICMP"

        # Compute timestamp
        if is_relative:
            offset = float(pkt.time) - first_raw
            pkt_time = now + timedelta(seconds=offset - (float(packets[-1].time) - first_raw))
        else:
            pkt_time = datetime.fromtimestamp(float(pkt.time))

        # Classify
        event_type = "network_flow"
        severity = "Low"
        signature = f"{proto} Traffic {src_ip} -> {dst_ip}:{dst_port}"

        if proto == "TCP":
            if "S" in flags and "A" not in flags:
                event_type = "tcp_syn_probe"
                severity = "Moderate"
                signature = f"TCP SYN Probe to port {dst_port}"
            elif dst_port in (21, 22, 23, 25, 445, 3306, 5432):
                event_type = "service_connection"
                severity = "Moderate"
                signature = f"Connection to service port {dst_port}"
        elif proto == "ICMP":
            event_type = "icmp_echo"
            signature = f"ICMP Echo {src_ip} -> {dst_ip}"
        elif proto == "UDP":
            event_type = "udp_traffic"

        # Suspicious ports get elevated severity
        if dst_port in (1524, 6667, 2121, 3632, 8009):
            severity = "Critical"
            event_type = "suspicious_port_access"
            signature = f"Access to high-risk port {dst_port}"
        elif dst_port in (21, 22, 23, 445):
            if event_type == "tcp_syn_probe":
                severity = "High"

        evidence = {
            "packet_length": len(pkt),
            "summary": pkt.summary(),
            "flags": flags,
            "sensor": "live_capture"
        }

        events.append({
            "src_ip": src_ip,
            "dst_ip": dst_ip,
            "src_port": src_port,
            "dst_port": dst_port,
            "protocol": proto,
            "event_type": event_type,
            "severity": severity,
            "signature": signature,
            "evidence": evidence,
            "timestamp": pkt_time,
        })

    return events, total


def ingest_events(parsed_events):
    """Ingest parsed events into the database and run detection."""
    if not parsed_events:
        return 0, 0, 0

    db = SessionLocal()
    try:
        ingestor = EventIngestor(db)
        from app.schemas.models import EventCreate

        ingested = 0
        for ev in parsed_events:
            try:
                event_create = EventCreate(
                    source_ip=ev["src_ip"],
                    destination_ip=ev["dst_ip"],
                    source_port=ev["src_port"],
                    destination_port=ev["dst_port"],
                    protocol=ev["protocol"],
                    event_type=ev["event_type"],
                    severity=ev["severity"],
                    sensor="live_capture",
                    signature=ev["signature"],
                    raw_evidence=json.dumps(ev["evidence"]),
                    timestamp=ev["timestamp"],
                )
                ingestor.ingest_single_event(event_create)
                ingested += 1
            except Exception as e:
                db.rollback()
                log.debug(f"Ingest error for event: {e}")

        # Run detection engine
        detector = DetectionEngine()
        alerts = detector.run_all(db)

        # Correlate sessions
        sessions = EventCorrelationEngine.correlate_sessions(db)

        return ingested, len(alerts), len(sessions)
    except Exception as e:
        log.error(f"Database error: {e}")
        db.rollback()
        return 0, 0, 0
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Main Daemon Loop
# ---------------------------------------------------------------------------
def main():
    global running

    print("=" * 64)
    print("  HACK THE HACKER — Live Capture & Ingestion Daemon")
    print("=" * 64)
    print(f"  VBoxManage  : {VBOXMANAGE}")
    print(f"  Target VM   : {VM_NAME}")
    print(f"  Kali VM     : {KALI_VM_NAME}")
    print(f"  Capture Dir : {CAPTURE_DIR}")
    print(f"  Poll Rate   : Every {POLL_INTERVAL}s")
    print("=" * 64)

    # Check VBoxManage exists
    if not os.path.exists(VBOXMANAGE):
        log.error(f"VBoxManage not found at {VBOXMANAGE}")
        sys.exit(1)

    # Initialize database
    init_db()
    log.info("Database connection verified.")

    # Disable any existing traces first
    disable_nictrace(VM_NAME, 1)
    disable_nictrace(KALI_VM_NAME, 2)
    time.sleep(1)

    # Set up unique capture files for this session
    session_id = int(time.time())
    target_pcap = CAPTURE_DIR / f"live_target_{session_id}.pcap"
    kali_pcap = CAPTURE_DIR / f"live_kali_{session_id}.pcap"

    # Enable NIC tracing
    log.info(f"Enabling NIC trace on {VM_NAME} (NIC 1)...")
    if enable_nictrace(VM_NAME, 1, target_pcap):
        log.info(f"  -> Tracing to {target_pcap}")
    else:
        log.warning(f"  -> Failed to enable trace on {VM_NAME}")

    # Kali uses NIC 2 for host-only
    log.info(f"Enabling NIC trace on Kali (NIC 2)...")
    if enable_nictrace(KALI_VM_NAME, 2, kali_pcap):
        log.info(f"  -> Tracing to {kali_pcap}")
    else:
        log.warning(f"  -> Failed to enable trace on Kali")

    print()
    log.info("LIVE CAPTURE ACTIVE — Run attacks from Kali and watch the dashboard!")
    log.info("Press Ctrl+C to stop.\n")

    target_last_count = 0
    kali_last_count = 0
    total_ingested = 0
    total_alerts = 0
    cycle = 0

    try:
        while running:
            time.sleep(POLL_INTERVAL)
            cycle += 1

            all_events = []

            # Harvest target VM packets
            evts, target_last_count = parse_pcap_incremental(
                str(target_pcap), target_last_count
            )
            all_events.extend(evts)

            # Harvest Kali VM packets
            evts, kali_last_count = parse_pcap_incremental(
                str(kali_pcap), kali_last_count
            )
            all_events.extend(evts)

            if all_events:
                ingested, alerts, sessions = ingest_events(all_events)
                total_ingested += ingested
                total_alerts += alerts

                # Summary per cycle
                severity_counts = {}
                for e in all_events:
                    s = e["severity"]
                    severity_counts[s] = severity_counts.get(s, 0) + 1

                sev_str = ", ".join(f"{k}: {v}" for k, v in sorted(severity_counts.items()))
                log.info(
                    f"[Cycle {cycle}] "
                    f"+{ingested} events ingested | "
                    f"+{alerts} alerts | "
                    f"{sessions} sessions | "
                    f"Severity: [{sev_str}] | "
                    f"Total: {total_ingested} events, {total_alerts} alerts"
                )
            else:
                if cycle % 5 == 0:  # Print status every 5 quiet cycles
                    log.info(
                        f"[Cycle {cycle}] Listening... "
                        f"(Total: {total_ingested} events, {total_alerts} alerts)"
                    )

    except KeyboardInterrupt:
        pass
    finally:
        log.info("Stopping NIC traces...")
        disable_nictrace(VM_NAME, 1)
        disable_nictrace(KALI_VM_NAME, 2)
        log.info("NIC traces disabled.")
        print()
        print("=" * 64)
        print(f"  Session Summary: {total_ingested} events ingested, {total_alerts} alerts generated")
        print("=" * 64)


if __name__ == "__main__":
    main()
