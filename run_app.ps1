Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "          Starting SmartCode AI Server             " -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

$BackendDir = Join-Path $PSScriptRoot "backend"
Set-Location $BackendDir

Write-Host "Installing/Verifying Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host "`nStarting FastAPI Web Server at http://localhost:8000" -ForegroundColor Green
Start-Process "http://localhost:8000"
python main.py
