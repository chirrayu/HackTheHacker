#!/usr/bin/env bash
# ==============================================================================
# HACK THE HACKER — Metasploitable 2 Target VM Setup Script
# Target Lab: VirtualBox Isolated Host-Only Network (192.168.56.0/24)
# Metasploitable IP: 192.168.56.30 | Subnet: 255.255.255.0
# Kali: 192.168.56.20 | Windows Host: 192.168.56.1
# ==============================================================================
# Compatible with legacy Linux 2.6 / Ubuntu 8.04 LTS userspace.
# Does NOT require internet, does NOT upgrade packages, NO default gateway.
# ==============================================================================
set -Eeuo pipefail

LAB_IFACE="${LAB_IFACE:-eth0}"
LAB_IP="${LAB_IP:-192.168.56.30}"
LAB_NETMASK="${LAB_NETMASK:-255.255.255.0}"
LAB_BROADCAST="${LAB_BROADCAST:-192.168.56.255}"

if [[ "${EUID}" -ne 0 ]]; then
  echo "[-] ERROR: This script must be run as root: sudo bash $0"
  exit 1
fi

log() { printf '\n[+] %s\n' "$*"; }
warn() { printf '\n[!] %s\n' "$*" >&2; }
trap 'warn "Setup encountered an error at line $LINENO."' ERR

log "Checking network interface '$LAB_IFACE'..."
if ! ifconfig "$LAB_IFACE" >/dev/null 2>&1 && ! ip link show "$LAB_IFACE" >/dev/null 2>&1; then
  echo "[-] Interface '$LAB_IFACE' not found. Available interfaces:"
  if command -v ifconfig >/dev/null 2>&1; then
    ifconfig -a | grep -E "^[a-zA-Z0-9]+" || true
  else
    ip -br link || true
  fi
  echo "Rerun with: sudo LAB_IFACE=<interface> bash $0"
  exit 1
fi

log "Creating lab workspace at /opt/hack-the-hacker..."
mkdir -p /opt/hack-the-hacker/{scripts,logs}

# Create verification script
cat > /opt/hack-the-hacker/scripts/verify-target.sh <<'EOF'
#!/usr/bin/env bash
set -u
echo "=========================================================="
echo " HACK THE HACKER — Target VM Verification (Metasploitable)"
echo "=========================================================="
echo "[*] Active Network Addresses:"
if command -v ip >/dev/null 2>&1; then
  ip -br addr
else
  ifconfig -a | grep -E "inet addr|Link encap"
fi

echo
echo "[*] Active Routing Table (Should NOT have default gateway):"
if command -v ip >/dev/null 2>&1; then
  ip route
else
  route -n
fi

echo
echo "[*] Connectivity to Lab Nodes:"
for node in "192.168.56.1 (Windows Host)" "192.168.56.20 (Kali Attacker)"; do
  ip=$(echo "$node" | cut -d' ' -f1)
  name=$(echo "$node" | cut -d' ' -f2-)
  if ping -c 2 -W 2 "$ip" >/dev/null 2>&1; then
    echo "  [+] $ip $name: REACHABLE"
  else
    echo "  [-] $ip $name: NO RESPONSE"
  fi
done

echo
echo "[*] Key Listening Services on Metasploitable:"
netstat -tlpn 2>/dev/null | grep -E "(:21 |:22 |:23 |:25 |:80 |:445 |:3306 |:5432 )" || true
echo "=========================================================="
EOF
chmod +x /opt/hack-the-hacker/scripts/verify-target.sh

log "Configuring static IP $LAB_IP on $LAB_IFACE..."
if command -v ifconfig >/dev/null 2>&1; then
  ifconfig "$LAB_IFACE" down || true
  ifconfig "$LAB_IFACE" "$LAB_IP" netmask "$LAB_NETMASK" broadcast "$LAB_BROADCAST" up
elif command -v ip >/dev/null 2>&1; then
  ip link set "$LAB_IFACE" down || true
  ip addr flush dev "$LAB_IFACE" || true
  ip addr add "$LAB_IP/24" broadcast "$LAB_BROADCAST" dev "$LAB_IFACE"
  ip link set "$LAB_IFACE" up
fi

# Ensure NO default gateway exists to keep target strictly isolated
log "Enforcing isolation: removing default routes if any exist..."
if command -v route >/dev/null 2>&1; then
  route del default dev "$LAB_IFACE" 2>/dev/null || true
  route del default 2>/dev/null || true
fi

# Add local subnet route if missing
if command -v route >/dev/null 2>&1; then
  route add -net 192.168.56.0 netmask 255.255.255.0 dev "$LAB_IFACE" 2>/dev/null || true
fi

cat > /opt/hack-the-hacker/README.txt <<EOF
==============================================================================
HACK THE HACKER — Target VM (Metasploitable 2)
==============================================================================
Assigned IP:     192.168.56.30/24
Kali Attacker:   192.168.56.20
Windows Monitor: 192.168.56.1

CRITICAL SAFETY:
  - This VM is attached ONLY to VirtualBox Host-Only Ethernet Adapter.
  - NEVER attach this VM to Bridged or NAT network.
  - Default gateway is purposefully omitted to prevent internet egress.

VERIFICATION:
  Run: sudo /opt/hack-the-hacker/scripts/verify-target.sh
==============================================================================
EOF

log "Metasploitable setup finished successfully!"
echo "------------------------------------------------------------------"
echo "Configured IP: $LAB_IP on $LAB_IFACE"
echo "Isolated: No default gateway configured."
echo "Test verification: sudo /opt/hack-the-hacker/scripts/verify-target.sh"
echo "------------------------------------------------------------------"
