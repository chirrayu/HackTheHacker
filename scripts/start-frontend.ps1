# ==============================================================================
# HACK THE HACKER — Start React SOC Dashboard
# ==============================================================================
param(
    [int]$Port = 3000
)

$projectRoot = Split-Path -Parent $PSScriptRoot
$frontendDir = "$projectRoot\frontend"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " HACK THE HACKER — Launching React SOC Dashboard" -ForegroundColor Cyan
Write-Host " Dashboard URL: http://localhost:$Port" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

Set-Location $frontendDir

# On Windows, invoke npm.cmd directly to avoid the known Node.js npm.ps1 call-operator '&' parsing bug
$npmExe = "npm.cmd"
if (-not (Get-Command "npm.cmd" -ErrorAction SilentlyContinue)) {
    $npmExe = "npm"
}

if (-not (Test-Path "$frontendDir\node_modules")) {
    Write-Host "[*] First time run detected: Installing dependencies with npm..." -ForegroundColor Yellow
    & $npmExe install
}

& $npmExe run dev
