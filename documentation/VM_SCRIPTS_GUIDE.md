# Virtual Machine Scripts & Operational Guide

This document explains the purpose and usage of all scripts generated for the VirtualBox lab machines.

---

## 1. Network Topology

| Machine | Role | Operating System | IP Address | Netmask | Default Gateway |
|---|---|---|---|---|---|
| **Host** | SOC Dashboard & Analytics | Windows 11 | `192.168.56.1` | `255.255.255.0` | None |
| **Kali Linux** | Attacker Simulation | Kali Rolling | `192.168.56.20` | `255.255.255.0` | None (or `192.168.56.1`) |
| **Metasploitable 2** | Intentionally Vulnerable Target | Linux 2.6 / Ubuntu 8.04 | `192.168.56.30` | `255.255.255.0` | **None** (Strictly isolated) |

> [!CAUTION]
> Both VMs must be attached to the **VirtualBox Host-Only Ethernet Adapter** (`vboxnet0` or `VirtualBox Host-Only Network`). Do **NOT** use Bridged networking for Metasploitable 2.

---

## 2. Scripts for Kali Linux (Attacker VM)

Location in repo: [`scripts/setup-kali.sh`](file:///C:/Users/monik/Desktop/project/HackTheHacker/scripts/setup-kali.sh)

### Running on Kali:
Copy `setup-kali.sh` into your Kali VM (or create it with `nano setup-kali.sh`) and execute:
```bash
sudo LAB_IFACE=eth1 bash setup-kali.sh
```
*(If Kali has only one adapter, it defaults to `eth0` or specify `LAB_IFACE=eth0`).*

### What it does:
1. Configures the network adapter to static IP `192.168.56.20/24`.
2. Creates `/opt/hack-the-hacker/scripts/verify-lab.sh` to check ping and TCP port reachability to both the Windows Host (`192.168.56.1`) and the Metasploitable Target (`192.168.56.30`).
3. Creates `/opt/hack-the-hacker/scripts/simulate-attack.sh`: An interactive menu that generates realistic, observable network attack telemetry for the SOC dashboard:
   - **Scenario 1:** ICMP Ping Sweep / Host Discovery
   - **Scenario 2:** Stealth TCP SYN Port Scanning (`nmap -sS`)
   - **Scenario 3:** Service & Banner Grabbing (`nmap -sV`)
   - **Scenario 4:** FTP Authentication Failure / Brute-force behavior
   - **Scenario 5:** Web directory probing (HTTP reconnaissance)
   - **Scenario 6:** Complete multi-stage attack sequence

---

## 3. Scripts for Metasploitable 2 (Target VM)

Location in repo: [`scripts/setup-target.sh`](file:///C:/Users/monik/Desktop/project/HackTheHacker/scripts/setup-target.sh)

### Running on Metasploitable 2:
Copy or write `setup-target.sh` on Metasploitable (default login: `msfadmin` / `msfadmin`) and execute:
```bash
sudo LAB_IFACE=eth0 bash setup-target.sh
```

### What it does:
1. Configures the network interface to static IP `192.168.56.30/24`.
2. **Enforces Strict Isolation:** Explicitly flushes any default gateway to guarantee the vulnerable target cannot communicate outside the host-only virtual switch.
3. Creates `/opt/hack-the-hacker/scripts/verify-target.sh` to verify its own listening services (FTP on 21, SSH on 22, HTTP on 80, SMB on 445, MySQL on 3306, etc.) and ping reachability from Kali and Windows.

---

## 4. Scripts for Windows 11 (Monitoring Host)

### Setup Check:
[`scripts/setup-windows.ps1`](file:///C:/Users/monik/Desktop/project/HackTheHacker/scripts/setup-windows.ps1)
Run from PowerShell:
```powershell
.\scripts\setup-windows.ps1
```
Verifies Python, VirtualBox, Host-Only Adapter IP (`192.168.56.1`), and creates necessary data directories for PCAP storage and logs.

### Network & Visibility Verification:
[`scripts/verify-network.ps1`](file:///C:/Users/monik/Desktop/project/HackTheHacker/scripts/verify-network.ps1)
Run from PowerShell:
```powershell
.\scripts\verify-network.ps1
```
Pings both VMs, verifies target ports, inspects the local ARP table, and documents guest-to-guest packet capture methods.

### Automated Packet Capture:
[`scripts/capture-traffic.ps1`](file:///C:/Users/monik/Desktop/project/HackTheHacker/scripts/capture-traffic.ps1)
Runs TShark or Dumpcap to capture network traffic on the Host-Only adapter into timestamped `.pcap` files in `monitoring/captures/`.
