@echo off
title WorkSight - Start All
echo ============================================
echo   WorkSight - starting backend + frontend
echo ============================================

REM ---- Backend (FastAPI on http://localhost:8000) ----
start "WorkSight Backend" cmd /k "cd /d d:\WorkSight\backend && python -m uvicorn app.main:app --port 8000"

REM ---- Frontend (Vite dev server on http://localhost:5173) ----
start "WorkSight Frontend" cmd /k "cd /d d:\WorkSight\frontend && npm run dev"

REM ---- Open the app in the default browser ----
timeout /t 6 /nobreak >nul
start http://localhost:5173

echo.
echo Backend window : FastAPI  -> http://localhost:8000/api/health
echo Frontend window: Vite dev -> http://localhost:5173
echo Browser will open automatically in a few seconds.
echo Keep both windows open while working. Close them to stop.
pause
