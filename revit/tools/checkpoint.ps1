<#
.SYNOPSIS
  Save a progress checkpoint: live Revit state + git state + equipment schedule.
  Writes revit/progress/state.json, schedule-latest.csv, log.md and refreshes the
  header of PROGRESS.md.  Safe to run any time; Revit being closed is not an error.

.EXAMPLE
  .\checkpoint.ps1                 # snapshot only
  .\checkpoint.ps1 -Commit         # snapshot + git commit (+ push if remote reachable)
  .\checkpoint.ps1 -Note "placed hoods 05/13"   # add a line to the log
#>
[CmdletBinding()]
param(
    [switch]$Commit,
    [switch]$NoPush,
    [string]$Note = "",
    [switch]$SessionNote,      # also add the note under "## Session notes" in PROGRESS.md
    [string]$Schedule = "EQUIPMENT SCHEDULE (E) - PHO HUNG",
    [switch]$Quiet
)
$ErrorActionPreference = "Continue"
$Root     = Split-Path -Parent (Split-Path -Parent $PSCommandPath)   # ...\revit
$Prog     = Join-Path $Root "progress"
$Base     = "http://localhost:48884/onetake-v1"
$Now      = Get-Date
$Stamp    = $Now.ToString("yyyy-MM-dd HH:mm:ss")
New-Item -ItemType Directory -Force $Prog | Out-Null

function Get-Json($url, $body, $timeout = 20) {
    try {
        if ($null -ne $body) {
            return Invoke-RestMethod -Uri $url -Method Post -ContentType "application/json" `
                -Body ($body | ConvertTo-Json -Compress) -TimeoutSec $timeout
        }
        return Invoke-RestMethod -Uri $url -Method Get -TimeoutSec $timeout
    } catch { return $null }
}

# ---- Revit ---------------------------------------------------------------
$status = Get-Json "$Base/status" $null 5
$revit  = [ordered]@{ up = $false }
$rows   = $null
if ($status -and $status.ok) {
    $revit.up = $true
    $revit.revit_version   = $status.revit_version
    $revit.revit_build     = $status.revit_build
    $revit.pyrevit_version = $status.pyrevit_version
    $doc = Get-Json "$Base/doc" $null 20
    if ($doc -and $doc.ok) {
        $revit.doc_title  = $doc.title
        $revit.levels     = @($doc.levels | ForEach-Object { $_.name })
        $revit.wall_types = @($doc.wall_types).Count
    }
    $walls = Get-Json "$Base/walls" $null 30
    if ($walls -and $walls.ok) { $revit.wall_count = @($walls.walls).Count }
    $sch = Get-Json "$Base/schedule-read" @{ name = $Schedule } 30
    if ($sch -and $sch.ok) {
        $rows = @($sch.rows)
        $revit.schedule = [ordered]@{ name = $Schedule; id = $sch.schedule_id; rows = $rows.Count }
        # CSV export (rows are string arrays; first two rows = title + header)
        $csv = foreach ($r in $rows) {
            ($r | ForEach-Object { '"' + (([string]$_) -replace '"', '""') + '"' }) -join ","
        }
        $csv | Out-File -Encoding utf8 (Join-Path $Prog "schedule-latest.csv")
    }
}

# ---- Git -----------------------------------------------------------------
$git = [ordered]@{}
try {
    Push-Location $Root
    $git.branch = (git rev-parse --abbrev-ref HEAD 2>$null)
    $git.head   = (git rev-parse --short HEAD 2>$null)
    $git.dirty  = @(git status --porcelain 2>$null).Count
    Pop-Location
} catch { $git.error = "$_" }

# ---- state.json ----------------------------------------------------------
$prev = $null
$stateFile = Join-Path $Prog "state.json"
if (Test-Path $stateFile) { try { $prev = Get-Content $stateFile -Raw | ConvertFrom-Json } catch {} }
$state = [ordered]@{
    checkpoint_at = $Stamp
    machine       = $env:COMPUTERNAME
    revit         = $revit
    git           = $git
    note          = $Note
}
($state | ConvertTo-Json -Depth 6) | Out-File -Encoding utf8 $stateFile

# ---- log.md (append; only when something changed, or a note was given) ---
$logFile = Join-Path $Prog "log.md"
if (-not (Test-Path $logFile)) { "# Checkpoint log`n" | Out-File -Encoding utf8 $logFile }
$sig = "$($revit.up)|$($revit.doc_title)|$($revit.wall_count)|$($revit.schedule.rows)|$($git.head)|$($git.dirty)"
$prevSig = if ($prev) { "$($prev.revit.up)|$($prev.revit.doc_title)|$($prev.revit.wall_count)|$($prev.revit.schedule.rows)|$($prev.git.head)|$($prev.git.dirty)" } else { "" }
$changed = ($sig -ne $prevSig)
if ($changed -or $Note) {
    $line = "- $Stamp | revit=" + $(if ($revit.up) { "up '$($revit.doc_title)' walls=$($revit.wall_count) sched_rows=$($revit.schedule.rows)" } else { "down" }) +
            " | git $($git.branch)@$($git.head) dirty=$($git.dirty)" + $(if ($Note) { " | $Note" } else { "" })
    Add-Content -Encoding utf8 $logFile $line
}

# ---- PROGRESS.md header refresh -----------------------------------------
$progFile = Join-Path $Prog "PROGRESS.md"
if (Test-Path $progFile) {
    $txt = [IO.File]::ReadAllText($progFile, [Text.Encoding]::UTF8)
    $hdr = "<!-- auto --> **Last checkpoint:** $Stamp | Revit: " +
           $(if ($revit.up) { "up, '$($revit.doc_title)', $($revit.wall_count) walls, schedule $($revit.schedule.rows) rows" } else { "not running" }) +
           " | git $($git.branch)@$($git.head), $($git.dirty) uncommitted"
    if ($txt -match '(?m)^<!-- auto -->.*$') { $txt = $txt -replace '(?m)^<!-- auto -->.*$', $hdr }
    else { $txt = $txt -replace '(?m)^(# .*\r?\n)', "`$1`n$hdr`n" }
    if ($Note -and $SessionNote) {
        $txt = $txt -replace '(?m)^(## Session notes \(newest first\)\r?\n)', "`$1- $Stamp - $Note`n"
    }
    [IO.File]::WriteAllText($progFile, $txt, (New-Object Text.UTF8Encoding $false))
}

# ---- git commit ----------------------------------------------------------
if ($Commit) {
    Push-Location $Root
    git add -A . 2>$null | Out-Null
    $pending = @(git status --porcelain 2>$null).Count
    if ($pending -gt 0) {
        $msg = "checkpoint $Stamp" + $(if ($Note) { " - $Note" } else { "" })
        git commit -q -m $msg 2>$null | Out-Null
        if (-not $Quiet) { Write-Host "committed: $msg" -ForegroundColor Green }
        if (-not $NoPush) {
            $env:GCM_INTERACTIVE = "never"
            git push -q 2>$null | Out-Null
            if ($LASTEXITCODE -eq 0) { if (-not $Quiet) { Write-Host "pushed" -ForegroundColor Green } }
            else { if (-not $Quiet) { Write-Host "push failed (offline / auth) - commit is safe locally" -ForegroundColor Yellow } }
        }
    } elseif (-not $Quiet) { Write-Host "nothing to commit" }
    Pop-Location
}

if (-not $Quiet) {
    Write-Host "checkpoint $Stamp saved -> $Prog" -ForegroundColor Cyan
    if ($revit.up) { Write-Host "  Revit: '$($revit.doc_title)'  walls=$($revit.wall_count)  schedule rows=$($revit.schedule.rows)" }
    else           { Write-Host "  Revit: not running (routes 48884 unreachable)" -ForegroundColor DarkYellow }
    Write-Host "  git: $($git.branch)@$($git.head), $($git.dirty) uncommitted file(s)"
}
