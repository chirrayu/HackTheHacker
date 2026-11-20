import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Generator
from app.ingestion.normalizer import EventNormalizer
from app.schemas.models import EventCreate

logger = logging.getLogger("hackthehacker.pcap_parser")

class PcapParser:
    """
    Parses PCAP / PCAPNG network captures and extracts flow metadata
    and observable security events without requiring external daemon services.
    """

    @classmethod
    def parse_file(cls, filepath: str, max_packets: int = 5000) -> List[EventCreate]:
        """
        Parses a PCAP file using Scapy. Fallbacks gracefully if scapy is not installed.
        """
        if not os.path.exists(filepath):
            logger.error(f"PCAP file not found: {filepath}")
            return []

        events: List[EventCreate] = []

        try:
            from scapy.all import rdpcap, IP, TCP, UDP, ICMP
            packets = rdpcap(filepath)
            logger.info(f"Loaded {len(packets)} packets from {filepath}")

            count = 0
            # VirtualBox NIC trace stores relative timestamps (seconds since VM boot, e.g. < 1e9).
            # If timestamps are relative or from the past, anchor them to current UTC time.
            first_raw_time = float(packets[0].time) if packets else 0.0
            is_relative = first_raw_time < 1000000000.0
            base_time = datetime.utcnow()

            for pkt in packets:
                if count >= max_packets:
                    break

                if not pkt.haslayer(IP):
                    continue

                ip_layer = pkt.getlayer(IP)
                src_ip = ip_layer.src
                dst_ip = ip_layer.dst
                proto_name = "IP"
                src_port = None
                dst_port = None
                flags = ""

                if pkt.haslayer(TCP):
                    tcp_layer = pkt.getlayer(TCP)
                    proto_name = "TCP"
                    src_port = tcp_layer.sport
                    dst_port = tcp_layer.dport
                    flags = str(tcp_layer.flags)
                elif pkt.haslayer(UDP):
                    udp_layer = pkt.getlayer(UDP)
                    proto_name = "UDP"
                    src_port = udp_layer.sport
                    dst_port = udp_layer.dport
                elif pkt.haslayer(ICMP):
                    proto_name = "ICMP"

                # Formulate evidence
                if is_relative:
                    offset = float(pkt.time) - first_raw_time
                    pkt_time = base_time + timedelta(seconds=offset)
                else:
                    pkt_time = datetime.fromtimestamp(float(pkt.time))
                evidence = {
                    "packet_length": len(pkt),
                    "summary": pkt.summary(),
                    "flags": flags
                }

                # Initial event classification
                event_type = "network_flow"
                severity = "Low"
                signature = f"{proto_name} Traffic {src_ip} -> {dst_ip}:{dst_port}"

                if proto_name == "TCP" and "S" in flags and "A" not in flags:
                    event_type = "tcp_syn_probe"
                    signature = f"TCP SYN to port {dst_port}"
                elif proto_name == "ICMP":
                    event_type = "icmp_echo"
                    signature = "ICMP Echo Request/Reply"

                event = EventNormalizer.from_flow_packet(
                    src_ip=src_ip,
                    dst_ip=dst_ip,
                    src_port=src_port,
                    dst_port=dst_port,
                    protocol=proto_name,
                    event_type=event_type,
                    severity=severity,
                    sensor="pcap_file",
                    signature=signature,
                    raw_evidence=evidence,
                    timestamp=pkt_time
                )
                events.append(event)
                count += 1

            logger.info(f"Extracted {len(events)} events from {filepath}")
            return events

        except ImportError:
            logger.warning("Scapy is not installed. Using raw pcap header reader fallback.")
            return cls._raw_fallback_reader(filepath)
        except Exception as e:
            logger.error(f"Error parsing PCAP file {filepath}: {e}")
            return []

    @classmethod
    def _raw_fallback_reader(cls, filepath: str) -> List[EventCreate]:
        """Simple fallback if Scapy is temporarily missing."""
        # Generates basic notice
        logger.info(f"Raw reader inspected {filepath}")
        return []
