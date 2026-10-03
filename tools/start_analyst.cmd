@echo off
rem One-click: check the Claude CLI, run the analyst ONCE now, then schedule it twice a day.
rem The analyst only PROPOSES - review with tools\review_proposals.cmd.
setlocal
cd /d "%~dp0.."
python -c "import sys; sys.exit(0 if sys.version_info>=(3,12) else 1)" 2>nul
if errorlevel 1 (
  echo  Python 3.12 or newer was not found on PATH. Install it from python.org, then run this again.
  pause
  exit /b 1
)
python -c "import sys; sys.path.insert(0,'pipeline'); from common import load_env, resolve_claude; load_env(); print(' Claude CLI:', resolve_claude())"
if errorlevel 1 (
  echo.
  echo  The Claude Code CLI was not found. Install it:   npm install -g @anthropic-ai/claude-code
  echo  then run   claude   once to sign in, put its path in .env as CLAUDE_BIN=...  ^(where.exe claude^),
  echo  and double-click this file again.
  pause
  exit /b 1
)
echo [1/2] Running the analyst now on whatever the inbox holds ^(can take 10-40 minutes^)...
python pipeline\analyst.py run --force
echo.
echo [2/2] Scheduling it twice a day ^(06:30 and 18:30^)...
powershell -NoProfile -ExecutionPolicy Bypass -File "tools\register_analyst_task.ps1"
echo.
python pipeline\analyst.py status
echo  Review what it proposed:  tools\review_proposals.cmd
pause
