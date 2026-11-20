# ==============================================================================
# HACK THE HACKER — Network Connectivity & Visibility Verification
# ==============================================================================
# Verifies connectivity between Windows Host (192.168.56.1), Kali (192.168.56.20),
# and Metasploitable (192.168.56.30), and documents packet capture feasibility.
# ==============================================================================
[CmdletBinding()]
param(
    [string]$HostIP = "192.168.56.1",
    [string]$KaliIP = "192.168.56.20",
    [string]$TargetIP = "192.168.56.30"
)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " HACK THE HACKER — Network & Packet Visibility Diagnostic" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Ping Tests & Smart IP Discovery
function Resolve-LabIP {
    param([string]$PreferredIP, [string]$FallbackIP, [string]$Label)
    if (Test-Connection -ComputerName $PreferredIP -Count 1 -Quiet -ErrorAction SilentlyContinue) {
        Write-Host "[+] $Label ($PreferredIP)... REACHABLE [OK]" -ForegroundColor Green
        return $PreferredIP
    } elseif (Test-Connection -ComputerName $FallbackIP -Count 1 -Quiet -ErrorAction SilentlyContinue) {
        Write-Host "[+] $Label ($FallbackIP - DHCP leased)... REACHABLE [OK]" -ForegroundColor Green
        return $FallbackIP
    } else {
        Write-Host "[-] $Label ($PreferredIP / $FallbackIP)... UNREACHABLE [FAIL]" -ForegroundColor Red
        return $PreferredIP
    }
}

$activeKali = Resolve-LabIP -PreferredIP $KaliIP -FallbackIP "192.168.56.102" -Label "Kali Attacker VM"
$activeTarget = Resolve-LabIP -PreferredIP $TargetIP -FallbackIP "192.168.56.101" -Label "Metasploitable Target VM"

# 2. Port Reachability Check to Target Services
Write-Host "`n[*] Probing Essential Services on Target ($activeTarget)..." -ForegroundColor Yellow
$ports = @(
    @{ Port = 21; Service = "FTP" },
    @{ Port = 22; Service = "SSH" },
    @{ Port = 80; Service = "HTTP (Apache)" },
    @{ Port = 445; Service = "SMB / Samba" },
    @{ Port = 3306; Service = "MySQL" }
)

foreach ($p in $ports) {
    try {
        $tcp = New-Object System.Net.Sockets.TcpClient
        $iar = $tcp.BeginConnect($activeTarget, $p.Port, $null, $null)
        $wait = $iar.AsyncWaitHandle.WaitOne(800, $false)
        if ($wait -and $tcp.Connected) {
            $tcp.EndConnect($iar)
            Write-Host "    [+] Port $($p.Port) ($($p.Service)): OPEN" -ForegroundColor Green
        } else {
            Write-Host "    [-] Port $($p.Port) ($($p.Service)): CLOSED / TIMEOUT" -ForegroundColor Gray
        }
        $tcp.Close()
    } catch {
        Write-Host "    [-] Port $($p.Port) ($($p.Service)): ERROR" -ForegroundColor Gray
    }
}

# 3. ARP Cache Check
Write-Host "`n[*] Inspecting Local ARP Table for Lab MAC Addresses..." -ForegroundColor Yellow
$arpOutput = arp -a | Select-String "192.168.56."
if ($arpOutput) {
    foreach ($line in $arpOutput) {
        Write-Host "    $line" -ForegroundColor Cyan
    }
} else {
    Write-Host "    [!] No 192.168.56.x entries in local ARP table yet." -ForegroundColor Gray
}

# 4. Critical Packet Capture Visibility Analysis
Write-Host "`n==========================================================" -ForegroundColor Cyan
Write-Host " PACKET CAPTURE VISIBILITY & ARCHITECTURE NOTICE" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host @"
[IMPORTANT NETWORK ARCHITECTURE NOTE]
In VirtualBox Host-Only networking:
- Host-to-Guest traffic (Windows <-> Kali, Windows <-> Target) IS visible to Npcap on the host.
- Broadcast/Multicast traffic (ARP requests, etc.) IS visible to the host.
- Guest-to-Guest unicast traffic (Kali -> Target):
  VirtualBox's internal virtual switch routes packets directly between guest NICs without
  necessarily copying unicast frames to the Windows host adapter unless specific capture
  forwarding is enabled.

RECOMMENDED CAPTURE METHODS:
Method A (Primary - VirtualBox Internal NIC Trace):
  VirtualBox provides built-in per-adapter packet dumping to PCAP:
  VBoxManage controlvm "<VM-Name>" nictrace1 on
  VBoxManage controlvm "<VM-Name>" nictracefile1 "C:\path\to\HackTheHacker\monitoring\captures\vm_traffic.pcap"

Method B (Live Agent / Forwarder on Kali or Host):
  Run tcpdump on Kali to log attack execution directly to shared pcap or stream via netcat:
  sudo tcpdump -i eth1 -w /opt/hack-the-hacker/captures/attack.pcap

Method C (Promiscuous Mode on Host-Only Adapter):
  In VirtualBox VM settings -> Network -> Advanced:
  Set 'Promiscuous Mode: Allow All' on both VMs.

The HACK THE HACKER ingestion engine supports both live Npcap capture and offline/streaming PCAP files.
"@ -ForegroundColor Yellow

Write-Host "==========================================================" -ForegroundColor Cyan
