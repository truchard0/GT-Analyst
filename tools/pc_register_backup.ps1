# One-time setup on the Windows PC: stop running GT-Analyst here and keep only a weekly backup download.
#
#   powershell -ExecutionPolicy Bypass -File tools\pc_register_backup.ps1
#   powershell -ExecutionPolicy Bypass -File tools\pc_register_backup.ps1 -Server user@my-server   # also fetch .env/config
#
# It (1) removes the old 5-minute ingest task and stops any local dashboard, (2) copies the backup script into the
# backup folder, so it keeps working after this checkout is deleted, (3) registers a weekly task (Sunday 10:00; a
# missed run starts when the PC is next on), and (4) runs the first backup now and reports whether it verified.
# It does NOT delete this checkout. Do that yourself after it prints "Backup verified".
param(
  [string]$Dest       = "$env:USERPROFILE\GT-Analyst-backup",
  [string]$Server     = "",
  [string]$ServerPath = "~/GT-Analyst",
  [string]$Day        = "Sunday",
  [string]$At         = "10:00"
)
$ErrorActionPreference = "Stop"
$task = "GT-Analyst Weekly Backup"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Split-Path -Parent $here

# 1. nothing may keep running on this PC
foreach ($old in @("GT-Analyst Ingest")) {
  if (Get-ScheduledTask -TaskName $old -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $old -Confirm:$false
    Write-Host "Removed scheduled task '$old'."
  }
}
Get-CimInstance Win32_Process -Filter "Name='python.exe' OR Name='pythonw.exe' OR Name='py.exe'" |
  Where-Object { $_.CommandLine -like "*dashboard.py*" -or $_.CommandLine -like "*server_loop.py*" -or $_.CommandLine -like "*pipeline\ingest.py*" } |
  ForEach-Object { Stop-Process -Id $_.ProcessId -Force; Write-Host ("Stopped local GT-Analyst process {0}." -f $_.ProcessId) }

# 2. the backup script lives in the backup folder, not in this checkout
New-Item -ItemType Directory -Force -Path $Dest | Out-Null
$script = Join-Path $Dest "pc_weekly_backup.ps1"
Copy-Item (Join-Path $here "pc_weekly_backup.ps1") $script -Force

# 3. weekly task
$taskArgs = "-NoProfile -ExecutionPolicy Bypass -File `"$script`" -Dest `"$Dest`""
if ($Server) { $taskArgs += " -Server `"$Server`" -ServerPath `"$ServerPath`"" }
$action   = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $taskArgs
$trigger  = New-ScheduledTaskTrigger -Weekly -DaysOfWeek $Day -At $At
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Minutes 30)
Register-ScheduledTask -TaskName $task -Action $action -Trigger $trigger -Settings $settings -Description "Weekly download of the GT-Analyst repository (and server-only files) as a backup. GT-Analyst runs on the server." -Force | Out-Null
Write-Host "Registered '$task': every $Day at $At, into $Dest."

# 4. first backup now
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $script -Dest $Dest -Server $Server -ServerPath $ServerPath
if ($LASTEXITCODE -eq 0) {
  Write-Host ""
  Write-Host "Backup verified. This PC no longer runs GT-Analyst." -ForegroundColor Green
  Write-Host "Before deleting this checkout ($root):"
  Write-Host "  - copy .env and config.json to the server if they are not there yet (they are not in git)"
  Write-Host "  - then delete the folder: Remove-Item -Recurse -Force `"$root`""
  Write-Host "Open the dashboard from the server: ssh -L 8787:127.0.0.1:8787 <user>@<server>  then http://localhost:8787"
} else {
  Write-Host "The first backup FAILED. See $Dest\backup.log. Do not delete this checkout yet." -ForegroundColor Red
  exit 1
}
