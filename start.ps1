# WorkSight — start backend + frontend in visible windows
# Run:  right-click → Run with PowerShell,  or:  powershell -File start.ps1
$root = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "Starting WorkSight..." -ForegroundColor Cyan

# Backend (FastAPI) — visible window so it stays alive while you work
Start-Process powershell -ArgumentList '-NoExit', '-Command', "Set-Location '$root\backend'; Write-Host 'WorkSight BACKEND — keep this window open' -ForegroundColor Green; python -m uvicorn app.main:app --port 8000"

Start-Sleep -Seconds 3

# Frontend (Vite dev server) — visible window
Start-Process powershell -ArgumentList '-NoExit', '-Command', "Set-Location '$root\frontend'; Write-Host 'WorkSight FRONTEND — keep this window open' -ForegroundColor Green; npm run dev"

Write-Host ""
Write-Host "Backend : http://localhost:8000/api/health" -ForegroundColor Yellow
Write-Host "Frontend: http://localhost:5173" -ForegroundColor Yellow
Write-Host "Keep both windows open. Closing a window stops that server." -ForegroundColor Gray
