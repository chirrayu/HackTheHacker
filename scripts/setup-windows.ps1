# ==============================================================================
# HACK THE HACKER — Windows Host Environment & Host-Only Adapter Setup
# ==============================================================================
# Run from PowerShell (Run as Administrator if adapter configuration is required)
# ==============================================================================
[CmdletBinding()]
param(
    [string]$ExpectedHostIP = "192.168.56.1",
    [string]$SubnetMask = "255.255.255.0",
    [string]$AdapterName = "VirtualBox Host-Only Ethernet Adapter"
)

$ErrorActionPreference = "Continue"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " HACK THE HACKER — Windows Host Lab Setup" -ForegroundColor Cyan
Write-Host " Host IP Target: $ExpectedHostIP" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Check Python
Write-Host "`n[*] Checking Python installation..." -ForegroundColor Yellow
try {
    $pyVersion = & python --version 2>&1
    Write-Host "[+] Found Python: $pyVersion" -ForegroundColor Green
} catch {
    Write-Host "[-] Python not found on PATH. Please ensure Python 3.11+ is installed." -ForegroundColor Red
}

# 2. Check VirtualBox & VBoxManage
Write-Host "`n[*] Checking VirtualBox..." -ForegroundColor Yellow
$vboxPaths = @(
    "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe",
    "C:\Program Files (x86)\Oracle\VirtualBox\VBoxManage.exe"
)
$vboxExe = $null
foreach ($path in $vboxPaths) {
    if (Test-Path $path) {
        $vboxExe = $path
        break
    }
}

if ($vboxExe) {
    $vbVersion = & $vboxExe --version 2>&1
    Write-Host "[+] Found VirtualBox ($vbVersion) at: $vboxExe" -ForegroundColor Green
} else {
    Write-Host "[!] VBoxManage.exe not found in standard paths." -ForegroundColor Yellow
}

# 3. Check Network Adapter
Write-Host "`n[*] Inspecting VirtualBox Host-Only Network Adapter on Windows..." -ForegroundColor Yellow
try {
    $adapters = Get-NetAdapter -ErrorAction SilentlyContinue | Where-Object { 
        $_.InterfaceDescription -like "*VirtualBox*" -or $_.Name -like "*VirtualBox*" 
    }
    
    if ($adapters) {
        foreach ($adapter in $adapters) {
            Write-Host "[+] Found Adapter: $($adapter.Name) ($($adapter.InterfaceDescription)) - Status: $($adapter.Status)" -ForegroundColor Green
            $ipConfig = Get-NetIPAddress -InterfaceIndex $adapter.InterfaceIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue
            if ($ipConfig) {
                Write-Host "    IPv4 Address: $($ipConfig.IPAddress)/$($ipConfig.PrefixLength)" -ForegroundColor Cyan
                if ($ipConfig.IPAddress -eq $ExpectedHostIP) {
                    Write-Host "    [OK] Configured with expected IP $ExpectedHostIP" -ForegroundColor Green
                } else {
                    Write-Host "    [!] IP is $($ipConfig.IPAddress), expected $ExpectedHostIP" -ForegroundColor Yellow
                    Write-Host "    To set to $ExpectedHostIP run as Admin:" -ForegroundColor Yellow
                    Write-Host "    New-NetIPAddress -InterfaceIndex $($adapter.InterfaceIndex) -IPAddress $ExpectedHostIP -PrefixLength 24" -ForegroundColor Gray
                }
            } else {
                Write-Host "    [!] No IPv4 assigned. Assigning static IP may be required." -ForegroundColor Yellow
            }
        }
    } else {
        Write-Host "[-] No VirtualBox Host-Only adapter found via Get-NetAdapter." -ForegroundColor Yellow
        Write-Host "    You can create one via VirtualBox GUI (Tools -> Network -> Host-only Networks -> Create)" -ForegroundColor Gray
        Write-Host "    Or using VBoxManage: & '$vboxExe' hostonlyif create" -ForegroundColor Gray
    }
} catch {
    Write-Host "[-] Note: Run as Administrator to query or configure network adapters directly." -ForegroundColor Gray
}

# 4. Check Wireshark / TShark / Npcap
Write-Host "`n[*] Checking Packet Capture Capabilities (Npcap / TShark)..." -ForegroundColor Yellow
$tsharkPath = "C:\Program Files\Wireshark\tshark.exe"
if (Test-Path $tsharkPath) {
    Write-Host "[+] Wireshark TShark found at $tsharkPath" -ForegroundColor Green
} else {
    Write-Host "[!] Wireshark/tshark not found at $tsharkPath." -ForegroundColor Yellow
    Write-Host "    Install Wireshark with Npcap (promiscuous mode enabled) for live capture." -ForegroundColor Gray
}

# 5. Create local directories for data, captures, and logs
Write-Host "`n[*] Ensuring project data directories exist..." -ForegroundColor Yellow
$projectRoot = Split-Path -Parent $PSScriptRoot
$dirs = @(
    "$projectRoot\monitoring\captures",
    "$projectRoot\monitoring\suricata",
    "$projectRoot\data\pcap_uploads",
    "$projectRoot\logs"
)
foreach ($d in $dirs) {
    if (-not (Test-Path $d)) {
        New-Item -ItemType Directory -Path $d -Force | Out-Null
        Write-Host "[+] Created: $d" -ForegroundColor Green
    } else {
        Write-Host "[+] Exists: $d" -ForegroundColor Gray
    }
}

Write-Host "`n==========================================================" -ForegroundColor Cyan
Write-Host " Setup check completed." -ForegroundColor Cyan
Write-Host " Next: run .\scripts\verify-network.ps1 to test connectivity to VMs." -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
