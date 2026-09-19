# GT-Analyst — start the dashboard in LAN mode (reachable from any device on this wifi).
# Loopback-only is the default; this script opts into LAN exposure via GT_LAN=1.
# Usage:  powershell -File tools\start_lan.ps1
$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
$py = "C:\Users\hudso\AppData\Local\Programs\Python\Python312\pythonw.exe"

# stop any running instance
Get-CimInstance Win32_Process -Filter "Name like 'python%'" |
  Where-Object { $_.CommandLine -like "*dashboard.py*" } |
  ForEach-Object { Stop-Process -Id $_.ProcessId -Force -Confirm:$false }
Start-Sleep -Seconds 1

$env:GT_LAN = "1"
Start-Process -FilePath $py -ArgumentList "pipeline\dashboard.py","8787" -WorkingDirectory $root
Start-Sleep -Seconds 2

$ip = (Get-NetIPAddress -AddressFamily IPv4 |
  Where-Object { $_.InterfaceAlias -match 'Wi-Fi|Ethernet' -and $_.IPAddress -notlike '169.*' } |
  Select-Object -First 1).IPAddress
Write-Host ""
Write-Host "GT-Analyst dashboard is LAN-accessible:" -ForegroundColor Green
Write-Host "  This PC:            http://127.0.0.1:8787" -ForegroundColor Cyan
Write-Host "  Other wifi devices: http://$ip`:8787" -ForegroundColor Cyan
Write-Host ""
Write-Host "If other devices can't connect, run the firewall command (once, as admin):" -ForegroundColor Yellow
Write-Host "  New-NetFirewallRule -DisplayName 'GT-Analyst 8787' -Direction Inbound -LocalPort 8787 -Protocol TCP -Action Allow -Profile Private"
