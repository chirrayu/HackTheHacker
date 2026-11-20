# ==============================================================================
# HACK THE HACKER — Packet Capture Automation Script
# ==============================================================================
[CmdletBinding()]
param(
    [string]$Interface = "VirtualBox Host-Only Network",
    [int]$DurationSeconds = 60,
    [string]$OutputFile = ""
)

$projectRoot = Split-Path -Parent $PSScriptRoot
$captureDir = "$projectRoot\monitoring\captures"
if (-not (Test-Path $captureDir)) {
    New-Item -ItemType Directory -Path $captureDir -Force | Out-Null
}

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
if (-not $OutputFile) {
    $OutputFile = "$captureDir\capture_$timestamp.pcap"
}

$tsharkPath = "C:\Program Files\Wireshark\tshark.exe"
$dumpcapPath = "C:\Program Files\Wireshark\dumpcap.exe"

$captureTool = $null
if (Test-Path $dumpcapPath) {
    $captureTool = $dumpcapPath
} elseif (Test-Path $tsharkPath) {
    $captureTool = $tsharkPath
}

if (-not $captureTool) {
    Write-Host "[-] dumpcap/tshark not found in C:\Program Files\Wireshark." -ForegroundColor Red
    Write-Host "[*] You can manually capture with Wireshark GUI on the 'VirtualBox Host-Only Ethernet Adapter'" -ForegroundColor Yellow
    Write-Host "    and save the output to: $OutputFile" -ForegroundColor Yellow
    exit 1
}

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " HACK THE HACKER — Starting Packet Capture" -ForegroundColor Cyan
Write-Host " Output: $OutputFile" -ForegroundColor Cyan
Write-Host " Duration: $DurationSeconds seconds" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# List interfaces if needed
Write-Host "[*] Executing capture tool: $captureTool"
& $captureTool -i 1 -a duration:$DurationSeconds -w $OutputFile
Write-Host "[+] Capture finished: $OutputFile" -ForegroundColor Green
