# HACK THE HACKER — Virtual Lab Safety & Isolation Guidelines

This cybersecurity research platform operates with an intentionally vulnerable target machine (**Metasploitable 2**). Strict containment rules must be followed at all times.

---

## 1. Network Containment Rules

1. **Host-Only Networking Only:**
   - Attach all lab virtual machines (`Kali`, `Metasploitable 2`) strictly to the **VirtualBox Host-Only Ethernet Adapter** (`192.168.56.0/24`).
   - **NEVER** configure Bridged Networking for Metasploitable 2.
   - **NEVER** configure NAT or NAT Network with port forwarding to Metasploitable 2.

2. **No Default Gateway on Target:**
   - The setup script [`scripts/setup-target.sh`](file:///C:/Users/monik/Desktop/project/HackTheHacker/scripts/setup-target.sh) flushes all default routes.
   - This prevents any vulnerable service on Metasploitable 2 from communicating with the internet or external home/corporate LANs.

3. **Restricted IP Scope:**
   - All tests and traffic simulations are strictly bounded to:
     - Windows Host: `192.168.56.1`
     - Kali Linux: `192.168.56.20`
     - Metasploitable 2: `192.168.56.30`
   - Testing against external or third-party IP addresses is strictly prohibited.

---

## 2. Safe Traffic Generation

1. Use only the authorized simulation scripts provided in [`scripts/setup-kali.sh`](file:///C:/Users/monik/Desktop/project/HackTheHacker/scripts/setup-kali.sh) (`/opt/hack-the-hacker/scripts/simulate-attack.sh`).
2. Do not install destructive exploit automation, persistence rootkits, or botnet agents.
3. Keep PCAP capture file uploads bounded within the configured `MAX_PCAP_SIZE_MB` limit (100 MB).
