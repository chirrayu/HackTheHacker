# ==============================================================================
# HACK THE HACKER — Full System Health & Component Verification
# ==============================================================================
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " HACK THE HACKER — Diagnostic Health Check" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Python check
try {
    $py = & python --version 2>&1
    Write-Host "[+] Python: $py" -ForegroundColor Green
} catch {
    Write-Host "[-] Python: NOT FOUND" -ForegroundColor Red
}

# 2. Node.js check
try {
    $node = & node --version 2>&1
    Write-Host "[+] Node.js: $node" -ForegroundColor Green
} catch {
    Write-Host "[-] Node.js: NOT FOUND" -ForegroundColor Red
}

# 3. VirtualBox check
$vbox = "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
if (Test-Path $vbox) {
    $vbVer = & $vbox --version 2>&1
    Write-Host "[+] VirtualBox: Installed ($vbVer)" -ForegroundColor Green
} else {
    Write-Host "[-] VirtualBox: VBoxManage not found at standard path" -ForegroundColor Yellow
}

# 4. Wireshark / TShark
$tshark = "C:\Program Files\Wireshark\tshark.exe"
if (Test-Path $tshark) {
    Write-Host "[+] Packet Sniffer: TShark installed at $tshark" -ForegroundColor Green
} else {
    Write-Host "[!] Packet Sniffer: TShark not found (Install Wireshark + Npcap)" -ForegroundColor Yellow
}

# 5. Check API connectivity if backend is currently running
try {
    $res = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/health" -Method Get -TimeoutSec 2 -ErrorAction Stop
    Write-Host "[+] Backend API: ONLINE ($($res.status))" -ForegroundColor Green
} catch {
    Write-Host "[*] Backend API: Not currently running (Run .\scripts\start-backend.ps1)" -ForegroundColor Gray
}

Write-Host "==========================================================" -ForegroundColor Cyan
