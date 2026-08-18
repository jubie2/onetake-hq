<#
.SYNOPSIS
  Live progress terminal.  Refreshes every N seconds, shows Revit + git + where
  we left off, and auto-saves a checkpoint whenever something changes (and at
  least every -SaveEvery minutes).  Ctrl+C / q saves a final checkpoint and exits.

  Keys while running:  c = checkpoint now   g = checkpoint + git commit/push
                       n = add a note       o = open PROGRESS.md      q = quit
.EXAMPLE
  .\progress-terminal.ps1
  .\progress-terminal.ps1 -Refresh 15 -SaveEvery 5 -AutoCommit
#>
param(
    [int]$Refresh = 30,          # seconds between screen refreshes
    [int]$SaveEvery = 10,        # minutes: force a checkpoint at least this often
    [switch]$AutoCommit          # also git commit+push on each auto checkpoint
)
$Root  = Split-Path -Parent (Split-Path -Parent $PSCommandPath)
$Tools = Join-Path $Root "tools"
$Prog  = Join-Path $Root "progress"
$Base  = "http://localhost:48884/onetake-v1"
try { $Host.UI.RawUI.WindowTitle = "OneTake Revit - progress terminal" } catch {}

function Ping-Revit {
    try { $s = Invoke-RestMethod "$Base/status" -TimeoutSec 4; if ($s.ok) { return $s } } catch {}
    return $null
}
function Save-Checkpoint([string]$note = "", [switch]$commit, [switch]$session) {
    $a = @{ Quiet = $true }
    if ($note)   { $a.Note = $note }
    if ($session) { $a.SessionNote = $true }
    if ($commit -or $AutoCommit) { $a.Commit = $true }
    & (Join-Path $Tools "checkpoint.ps1") @a
}
function Read-State {
    $f = Join-Path $Prog "state.json"
    if (Test-Path $f) { try { return Get-Content $f -Raw | ConvertFrom-Json } catch {} }
    return $null
}
function Get-Section([string]$text, [string]$heading, [int]$max = 8) {
    $m = [regex]::Match($text, "(?ms)^## $([regex]::Escape($heading))\s*\r?\n(.*?)(?=^## |\z)")
    if (-not $m.Success) { return @() }
    return @($m.Groups[1].Value -split "\r?\n" | Where-Object { $_.Trim() } | Select-Object -First $max)
}
function Render($state, $revitNow, $msg) {
    Clear-Host
    $w = 100
    try { $w = [Math]::Max(60, $Host.UI.RawUI.WindowSize.Width - 1) } catch {}
    $bar = "".PadRight($w, "=")
    Write-Host $bar -ForegroundColor DarkCyan
    Write-Host ("  ONETAKE / REVIT - PROGRESS TERMINAL   {0}" -f (Get-Date -Format "ddd yyyy-MM-dd HH:mm:ss")) -ForegroundColor Cyan
    Write-Host $bar -ForegroundColor DarkCyan
    if ($revitNow) {
        Write-Host ("  Revit   : UP  {0} build {1}  pyRevit {2}" -f $revitNow.revit_version, $revitNow.revit_build, $revitNow.pyrevit_version) -ForegroundColor Green
    } else {
        Write-Host  "  Revit   : NOT RUNNING (routes :48884 unreachable) - open Revit 2025 + a project" -ForegroundColor Yellow
    }
    if ($state -and $state.revit.up) {
        Write-Host ("  Model   : '{0}'   walls={1}   schedule '{2}' = {3} rows (id {4})" -f `
            $state.revit.doc_title, $state.revit.wall_count, $state.revit.schedule.name, $state.revit.schedule.rows, $state.revit.schedule.id)
    }
    if ($state) {
        $dirtyColor = "Green"; if ([int]$state.git.dirty -gt 0) { $dirtyColor = "Yellow" }
        Write-Host ("  Git     : {0} @ {1}   uncommitted files: {2}" -f $state.git.branch, $state.git.head, $state.git.dirty) -ForegroundColor $dirtyColor
        $ac = ""; if ($AutoCommit) { $ac = ", +git commit" }
        Write-Host ("  Saved   : last checkpoint {0}   (auto every {1} min or on change{2})" -f $state.checkpoint_at, $SaveEvery, $ac) -ForegroundColor DarkGray
    }
    Write-Host $bar -ForegroundColor DarkCyan
    $pf = Join-Path $Prog "PROGRESS.md"
    if (Test-Path $pf) {
        $txt = [IO.File]::ReadAllText($pf, [Text.Encoding]::UTF8)
        Write-Host "  WHERE WE LEFT OFF" -ForegroundColor White
        Get-Section $txt "Where we left off" 6 | ForEach-Object { Write-Host "   $_" }
        Write-Host "  NEXT UP" -ForegroundColor White
        Get-Section $txt "Next up" 8 | ForEach-Object { Write-Host "   $_" -ForegroundColor Gray }
        Write-Host "  RECENT NOTES" -ForegroundColor White
        Get-Section $txt "Session notes (newest first)" 4 | ForEach-Object { Write-Host "   $_" -ForegroundColor DarkGray }
    } else {
        Write-Host "  (no progress/PROGRESS.md yet - run checkpoint.ps1)" -ForegroundColor Yellow
    }
    Write-Host $bar -ForegroundColor DarkCyan
    if ($msg) { Write-Host "  $msg" -ForegroundColor Magenta }
    Write-Host "  [c] checkpoint  [g] checkpoint+commit/push  [n] note  [o] open PROGRESS.md  [q] quit   (refresh ${Refresh}s)" -ForegroundColor DarkGray
}

# ---- main loop -----------------------------------------------------------
Save-Checkpoint "progress terminal started"
$lastSave = Get-Date
$lastSig  = ""
$msg = "started - checkpoint saved"
$quit = $false
try {
    while (-not $quit) {
      try {
        $revitNow = Ping-Revit
        $state = Read-State
        $head  = git -C $Root rev-parse --short HEAD 2>$null
        $dirty = @(git -C $Root status --porcelain 2>$null).Count
        $sig = "$([bool]$revitNow)|$head|$dirty"
        $due = ((Get-Date) - $lastSave).TotalMinutes -ge $SaveEvery
        if (($lastSig -ne "" -and $sig -ne $lastSig) -or $due) {
            Save-Checkpoint
            $lastSave = Get-Date
            $state = Read-State
            $msg = "auto-checkpoint saved $(Get-Date -Format HH:mm:ss)"
        }
        $lastSig = $sig
        Render $state $revitNow $msg
        $deadline = (Get-Date).AddSeconds($Refresh)
        while ((Get-Date) -lt $deadline) {
            $keyHit = $false
            try { $keyHit = $Host.UI.RawUI.KeyAvailable } catch {}
            if ($keyHit) {
                $k = [string]$Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown").Character
                switch ($k.ToLower()) {
                    'c' { Save-Checkpoint; $lastSave = Get-Date; $msg = "checkpoint saved" }
                    'g' { Save-Checkpoint -commit; $lastSave = Get-Date; $msg = "checkpoint + git commit/push done" }
                    'n' { $n = Read-Host "  note"; if ($n) { Save-Checkpoint $n -session; $msg = "note saved" } }
                    'o' { Start-Process (Join-Path $Prog "PROGRESS.md"); $msg = "opened PROGRESS.md" }
                    'q' { $quit = $true }
                }
                break
            }
            Start-Sleep -Milliseconds 250
        }
      } catch {
        # never die: log and keep going
        try { Add-Content -Encoding utf8 (Join-Path $Prog "terminal-errors.log") ("{0} {1}" -f (Get-Date -Format s), $_.Exception.Message) } catch {}
        $msg = "recovered from error: $($_.Exception.Message)"
        Start-Sleep -Seconds 2
      }
    }
} finally {
    Write-Host "`n  saving final checkpoint..." -ForegroundColor Cyan
    Save-Checkpoint "progress terminal closed"
    Write-Host "  done - pick up next time from revit/progress/PROGRESS.md" -ForegroundColor Green
}
# exit code tells the .cmd supervisor whether this was a deliberate quit
if ($quit) { exit 0 } else { exit 1 }
