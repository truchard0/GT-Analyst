# Registers the 5-minute GT-Analyst ingest as a per-user scheduled task (no admin).
# pythonw.exe = no console popups; all output goes to logs\ingest.log
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$py = Join-Path (Split-Path -Parent (Get-Command python).Source) "pythonw.exe"
if (-not (Test-Path $py)) { $py = (Get-Command python).Source }  # fallback: console python

$action = New-ScheduledTaskAction -Execute $py -Argument "`"$root\pipeline\ingest.py`"" -WorkingDirectory $root
# 10-year repetition window: [TimeSpan]::MaxValue overflows the task XML on Win11
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) `
    -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration (New-TimeSpan -Days 3650)
$settings = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 10) -StartWhenAvailable

Register-ScheduledTask -TaskName "GT-Analyst Ingest" -Action $action -Trigger $trigger -Settings $settings -Force
Write-Host "Registered 'GT-Analyst Ingest' (every 5 min, $py). Health: $root\logs\ingest.log"
