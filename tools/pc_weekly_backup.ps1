# GT-Analyst weekly backup download (Windows). GT-Analyst itself runs on the server; this PC keeps only a backup.
#
# What it downloads, once a week (registered by tools\pc_register_backup.ps1):
#   1. the whole git repository from GitHub, as a mirror (every branch, the full history): code, the prediction
#      ledger, the timeline, reports, skills and data
#   2. a dated zip snapshot of the working branch, so a backup can be opened without git
#   3. optionally (-Server), the server's weekly archive of the files git does not carry (.env, config.json, the
#      news dedup cache), copied with scp
# Nothing here runs GT-Analyst. Exit code 0 = backup verified, 1 = failed (see backup.log in the backup folder).
param(
  [string]$Dest       = "$env:USERPROFILE\GT-Analyst-backup",
  [string]$Repo       = "https://github.com/truchard0/GT-Analyst.git",
  [string]$Branch     = "claude/gracious-lamport-6wef9u",
  [string]$Server     = "",                  # e.g. user@my-server ; empty = skip the server-only archive
  [string]$ServerPath = "~/GT-Analyst",      # the GT-Analyst folder on the server
  [int]$Keep          = 8                    # dated snapshots to keep
)
$ErrorActionPreference = "Stop"
$mirror = Join-Path $Dest "repo.git"
$snaps  = Join-Path $Dest "snapshots"
$srvdir = Join-Path $Dest "server-only"
$log    = Join-Path $Dest "backup.log"
New-Item -ItemType Directory -Force -Path $Dest, $snaps | Out-Null
function Log($msg) { $line = "{0} {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $msg; Add-Content -Path $log -Value $line; Write-Host $line }

try {
  if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw "git is not installed or not on PATH" }

  # 1. mirror: first run clones, later runs update
  if (Test-Path (Join-Path $mirror "HEAD")) {
    git --git-dir="$mirror" fetch --prune --quiet origin
    if ($LASTEXITCODE -ne 0) { throw "git fetch failed (exit $LASTEXITCODE)" }
  } else {
    git clone --mirror --quiet "$Repo" "$mirror"
    if ($LASTEXITCODE -ne 0) { throw "git clone --mirror failed (exit $LASTEXITCODE)" }
  }

  # 2. verify the branch and the ledger are really in the mirror, then write a dated zip
  $head = (git --git-dir="$mirror" rev-parse --short "refs/heads/$Branch")
  if ($LASTEXITCODE -ne 0 -or -not $head) { throw "branch $Branch is not in the mirror" }
  $ledger = (git --git-dir="$mirror" ls-tree -l "refs/heads/$Branch" "ledger/ledger.db")
  if (-not $ledger) { throw "ledger/ledger.db is missing from $Branch" }
  $when = (git --git-dir="$mirror" log -1 --format=%cI "refs/heads/$Branch")
  $zip  = Join-Path $snaps ("gt-analyst_{0}_{1}.zip" -f (Get-Date -Format "yyyyMMdd"), $head)
  git --git-dir="$mirror" archive --format=zip -o "$zip" "refs/heads/$Branch"
  if ($LASTEXITCODE -ne 0 -or -not (Test-Path $zip) -or (Get-Item $zip).Length -lt 100000) { throw "snapshot zip was not written or is too small" }
  Get-ChildItem $snaps -Filter "gt-analyst_*.zip" | Sort-Object LastWriteTime -Descending | Select-Object -Skip $Keep | Remove-Item -Force

  # 3. optional: the server's weekly archive of files git does not carry
  $srvNote = "server-only archive skipped (no -Server given)"
  if ($Server) {
    New-Item -ItemType Directory -Force -Path $srvdir | Out-Null
    scp "${Server}:${ServerPath}/backups/gt_server_only_*.tar.gz" "$srvdir\"
    if ($LASTEXITCODE -ne 0) { throw "scp from $Server failed (exit $LASTEXITCODE); the repository backup itself succeeded" }
    Get-ChildItem $srvdir -Filter "gt_server_only_*.tar.gz" | Sort-Object Name -Descending | Select-Object -Skip $Keep | Remove-Item -Force
    $srvNote = "server-only archive copied from $Server"
  }

  $age = [int]((Get-Date) - [datetime]$when).TotalHours
  $stale = ""
  if ($age -gt 72) { $stale = " WARNING: the server last pushed $age hours ago; check that it is running." }
  Log ("OK branch {0} at {1} (last server push {2}); snapshot {3} ({4:N1} MB); {5}.{6}" -f $Branch, $head, $when, (Split-Path $zip -Leaf), ((Get-Item $zip).Length / 1MB), $srvNote, $stale)
  exit 0
} catch {
  Log ("FAILED: " + $_.Exception.Message)
  exit 1
}
