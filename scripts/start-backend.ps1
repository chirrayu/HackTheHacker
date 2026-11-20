# ==============================================================================
# HACK THE HACKER — Start Backend API Server
# ==============================================================================
param(
    [string]$HostAddress = "0.0.0.0",
    [int]$Port = 8000,
    [switch]$Reload = $true
)

$projectRoot = Split-Path -Parent $PSScriptRoot
$backendDir = "$projectRoot\backend"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " HACK THE HACKER — Launching FastAPI Engine" -ForegroundColor Cyan
Write-Host " Listening on: http://$HostAddress`:$Port" -ForegroundColor Cyan
Write-Host " Interactive API Docs: http://localhost:$Port/docs" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

Set-Location $backendDir

# If virtual environment exists, activate it
if (Test-Path "$backendDir\venv\Scripts\Activate.ps1") {
    & "$backendDir\venv\Scripts\Activate.ps1"
}

if ($Reload) {cd
    & python -m uvicorn app.main:app --host $HostAddress --port $Port --reload
} else {
    & python -m uvicorn app.main:app --host $HostAddress --port $Port
}
