# Launches the GT-Analyst dashboard and opens it in your browser.
# Double-click this file, or run:  powershell -ExecutionPolicy Bypass -File tools\start_dashboard.ps1
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$py = (Get-Command python).Source
$port = 8787
Start-Process "http://127.0.0.1:$port"
Write-Host "GT-Analyst dashboard -> http://127.0.0.1:$port   (close this window or Ctrl+C to stop)"
& $py "$root\pipeline\dashboard.py" $port
