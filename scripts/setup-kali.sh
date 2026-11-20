#!/usr/bin/env bash
# ==============================================================================
# HACK THE HACKER — Kali Linux Attacker VM Setup Script
# Target Lab: VirtualBox Isolated Host-Only Network (192.168.56.0/24)
# Kali IP: 192.168.56.20 | Target IP: 192.168.56.30 | Host IP: 192.168.56.1
# ==============================================================================
set -Eeuo pipefail

LAB_IFACE="${LAB_IFACE:-eth1}"
LAB_IP="${LAB_IP:-192.168.56.20/24}"
TARGET_IP="${TARGET_IP:-192.168.56.30}"
HOST_IP="${HOST_IP:-192.168.56.1}"

if [[ "${EUID}" -ne 0 ]]; then
  echo "[-] ERROR: This script must be run as root: sudo -E bash $0"
  exit 1
fi

log() { printf '\n[+] %s\n' "$*"; }
warn() { printf '\n[!] %s\n' "$*" >&2; }
trap 'warn "Setup encountered an error at line $LINENO."' ERR

log "Detecting network interfaces on Kali Linux..."
ip -br link

# If LAB_IFACE doesn't exist, try eth0 or let user know
if ! ip link show "$LAB_IFACE" >/dev/null 2>&1; then
  if ip link show "eth0" >/dev/null 2>&1; then
    warn "Interface '$LAB_IFACE' not found. Falling back to 'eth0'."
    LAB_IFACE="eth0"
  else
    warn "Specified interface not found. Available interfaces:"
    ip -br link
    echo "Rerun with: sudo -E LAB_IFACE=<interface_name> bash $0"
    exit 1
  fi
fi

log "Configuring interface $LAB_IFACE with static IP $LAB_IP..."
ip link set "$LAB_IFACE" up
ip addr replace "$LAB_IP" dev "$LAB_IFACE"

log "Creating lab workspace at /opt/hack-the-hacker..."
mkdir -p /opt/hack-the-hacker/{scripts,logs,captures}

# 1. Verification Script
cat > /opt/hack-the-hacker/scripts/verify-lab.sh <<'EOF'
#!/usr/bin/env bash
# Verification of lab connectivity from Kali Linux
set -u

HOST_IP="192.168.56.1"
TARGET_IP="192.168.56.30"
KALI_IP="192.168.56.20"

# Auto-detect target IP if DHCP leased (192.168.56.101 vs static 192.168.56.30)
if ! ping -c 1 -W 1 "$TARGET_IP" >/dev/null 2>&1 && ping -c 1 -W 1 "192.168.56.101" >/dev/null 2>&1; then
  TARGET_IP="192.168.56.101"
fi

echo "=========================================================="
echo " HACK THE HACKER — Kali Network Verification"
echo "=========================================================="
echo "[*] Active IP Addresses:"
ip -br addr
echo
echo "[*] Routing Table:"
ip route
echo
echo "[*] Testing Reachability to Lab Machines..."

# Ping Windows Host
if ping -c 2 -W 2 "$HOST_IP" >/dev/null 2>&1; then
  echo "[+] [OK] Windows Host ($HOST_IP) is REACHABLE."
else
  echo "[-] [WARN] Windows Host ($HOST_IP) did NOT respond to ping."
  echo "    (Windows Firewall may block ICMP by default on Host-Only adapter)."
fi

# Ping Metasploitable Target
if ping -c 2 -W 2 "$TARGET_IP" >/dev/null 2>&1; then
  echo "[+] [OK] Metasploitable Target ($TARGET_IP) is REACHABLE."
else
  echo "[-] [FAIL] Metasploitable Target ($TARGET_IP) did NOT respond."
  echo "    Ensure Target VM is booted and configured on 192.168.56.30."
fi

echo
echo "[*] Checking Target Open Ports (Fast probe)..."
if command -v nc >/dev/null 2>&1; then
  for port in 21 22 80 445; do
    if nc -z -w 1 "$TARGET_IP" "$port" 2>/dev/null; then
      echo "    -> Port $port/TCP on $TARGET_IP: OPEN"
    else
      echo "    -> Port $port/TCP on $TARGET_IP: CLOSED / UNREACHABLE"
    fi
  done
fi
echo "=========================================================="
EOF
chmod +x /opt/hack-the-hacker/scripts/verify-lab.sh

# 2. Controlled Traffic Generation Script for Detection Validation
cat > /opt/hack-the-hacker/scripts/simulate-attack.sh <<'EOF'
#!/usr/bin/env bash
# ==============================================================================
# HACK THE HACKER — Controlled Attack Traffic Simulation
# Generates observable, standardized telemetry for SOC detection testing.
# Only targets the isolated Metasploitable 2 VM (192.168.56.30).
# ==============================================================================
set -u

TARGET="192.168.56.30"
if ! ping -c 1 -W 1 "$TARGET" >/dev/null 2>&1 && ping -c 1 -W 1 "192.168.56.101" >/dev/null 2>&1; then
  TARGET="192.168.56.101"
fi

echo "=========================================================="
echo " HACK THE HACKER — Simulated Attack Traffic Generator"
echo " Target: $TARGET (Metasploitable 2)"
echo "=========================================================="
echo "Select scenario to simulate:"
echo " 1) ICMP Ping Sweep / Host Discovery"
echo " 2) TCP Port Scan (SYN Stealth Scan - Nmap)"
echo " 3) Service & Version Enumeration"
echo " 4) FTP Brute-Force Behavior Simulation"
echo " 5) HTTP Web Path Reconnaissance"
echo " 6) Run Full Multi-Stage Attack Chain"
echo " 0) Exit"
echo "----------------------------------------------------------"
read -rp "Enter choice [1-6]: " choice

case "$choice" in
  1)
    echo "[+] Running ICMP Discovery on 192.168.56.0/24..."
    nmap -sn -PE 192.168.56.0/24 -oN /opt/hack-the-hacker/logs/recon_icmp.log
    ;;
  2)
    echo "[+] Running TCP Port Scan against $TARGET..."
    nmap -sS -p 21,22,23,25,53,80,111,139,445,512,513,514,1099,1524,2049,2121,3306,5432,5900,6000,6667,8009,8180 \
         -T4 "$TARGET" -oN /opt/hack-the-hacker/logs/scan_ports.log
    ;;
  3)
    echo "[+] Running Service & Banner Enumeration against $TARGET..."
    nmap -sV -p 21,22,80,445 "$TARGET" -oN /opt/hack-the-hacker/logs/enum_services.log
    ;;
  4)
    echo "[+] Simulating FTP Authentication Failures against $TARGET:21..."
    for user in admin root guest test administrator sysadmin; do
      for pass in 123456 password toor admin; do
        echo "[*] Attempting FTP login: $user:$pass"
        curl -s -m 2 --user "$user:$pass" "ftp://$TARGET/" >/dev/null 2>&1 || true
        sleep 0.2
      done
    done
    echo "[+] FTP Brute Force simulation complete."
    ;;
  5)
    echo "[+] Simulating HTTP Web Directory Enumeration against $TARGET:80..."
    for path in "" "admin" "login" "phpmyadmin" "twiki" "mutillidae" "dvwa" "cgi-bin" "test" "uploads"; do
      echo "[*] HTTP GET http://$TARGET/$path"
      curl -s -o /dev/null -w "%{http_code}\n" "http://$TARGET/$path" || true
      sleep 0.1
    done
    echo "[+] HTTP Recon complete."
    ;;
  6)
    echo "[+] Executing Complete Multi-Stage Attack Sequence..."
    echo "--- Stage 1: Host Discovery ---"
    ping -c 3 "$TARGET"
    sleep 1
    echo "--- Stage 2: Port Scanning ---"
    nmap -sS -p 21,22,23,80,445,3306,5432 -T4 "$TARGET"
    sleep 2
    echo "--- Stage 3: Service Banner Grabbing ---"
    nmap -sV -p 21,80 "$TARGET"
    sleep 2
    echo "--- Stage 4: Web Directory Probing ---"
    for p in admin login dvwa phpmyadmin; do
      curl -s "http://$TARGET/$p" >/dev/null 2>&1 || true
    done
    echo "[+] Multi-stage sequence finished. Check SOC Dashboard for alerts!"
    ;;
  *)
    echo "Exiting."
    exit 0
    ;;
esac
EOF
chmod +x /opt/hack-the-hacker/scripts/simulate-attack.sh

# 3. Readme file on Kali
cat > /opt/hack-the-hacker/README.txt <<EOF
==============================================================================
HACK THE HACKER — Kali Linux Attacker Node
==============================================================================
Lab Subnet: 192.168.56.0/24 (VirtualBox Host-Only Network)
Kali IP:    192.168.56.20
Target:     192.168.56.30 (Metasploitable 2)
Windows:    192.168.56.1  (SOC Dashboard & Sensor)

SCRIPTS:
  1. /opt/hack-the-hacker/scripts/verify-lab.sh
     Verify network reachability to Windows and Metasploitable.

  2. /opt/hack-the-hacker/scripts/simulate-attack.sh
     Generate controlled reconnaissance, port scans, and auth traffic
     to validate the SOC detection pipeline.
==============================================================================
EOF

log "Kali setup finished successfully!"
echo "------------------------------------------------------------------"
echo "Configured IP: $LAB_IP on $LAB_IFACE"
echo "Test verification: sudo /opt/hack-the-hacker/scripts/verify-lab.sh"
echo "Simulate traffic:  sudo /opt/hack-the-hacker/scripts/simulate-attack.sh"
echo "------------------------------------------------------------------"
