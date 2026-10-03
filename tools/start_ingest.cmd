@echo off
rem One-click: pull the feeds NOW, then register the 5-minute background ingest (per-user, no admin).
rem Safe without config.json - watchlist auto-trigger defaults to dry-run (logs only, spends nothing).
setlocal
cd /d "%~dp0.."
python -c "import sys; sys.exit(0 if sys.version_info>=(3,12) else 1)" 2>nul
if errorlevel 1 (
  echo.
  echo  Python 3.12 or newer was not found on PATH.
  echo  Install it from python.org ^(tick "Add python.exe to PATH"^), then double-click this file again.
  echo.
  pause
  exit /b 1
)
echo [1/3] Pulling all feeds now ^(takes up to a minute^)...
python pipeline\ingest.py
echo.
echo [2/3] Registering the background task "GT-Analyst Ingest" ^(every 5 minutes^)...
powershell -NoProfile -ExecutionPolicy Bypass -File "tools\register_task.ps1"
echo.
echo [3/3] Health check - last lines of logs\ingest.log:
powershell -NoProfile -Command "Get-Content -Tail 3 'logs\ingest.log'; Get-ScheduledTask -TaskName 'GT-Analyst Ingest' | Get-ScheduledTaskInfo | Format-List LastRunTime,NextRunTime,LastTaskResult"
echo  New items accumulate in inbox\latest.md. To stop: tools\unregister_task.ps1
echo.
pause
