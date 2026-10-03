# Registers the GT-Analyst DAILY ANALYST as a per-user scheduled task (no admin).
# Default: twice a day at 06:30 and 18:30 local. One run a day:  -Times "07:00"
# The run PROPOSES only - nothing enters the ledger until you approve (tools\review_proposals.cmd).
param([string[]]$Times = @("06:30", "18:30"))
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$py = Join-Path (Split-Path -Parent (Get-Command python).Source) "pythonw.exe"
if (-not (Test-Path $py)) { $py = (Get-Command python).Source }

$action = New-ScheduledTaskAction -Execute $py -Argument "`"$root\pipeline\analyst.py`" run" -WorkingDirectory $root
$triggers = $Times | ForEach-Object { New-ScheduledTaskTrigger -Daily -At $_ }
# 90-minute limit: the analyst's own timeout is 60. StartWhenAvailable catches a run missed while asleep.
$settings = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 90) -StartWhenAvailable `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask -TaskName "GT-Analyst Daily Analyst" -Action $action -Trigger $triggers -Settings $settings -Force
Write-Host "Registered 'GT-Analyst Daily Analyst' at $($Times -join ', ') local. Health: $root\logs\analyst.log"
Write-Host "Daily cap and model live in config.json -> analyst {max_runs_per_day, model}."
