<#
.SYNOPSIS
  Make the progress terminal survive reboots: drops a shortcut to
  tools\Progress-Terminal.cmd into the current user's Startup folder (no admin
  needed) and starts it now if it is not already running.  -Uninstall removes it.
#>
param([switch]$Uninstall)
$Cmd     = Join-Path $PSScriptRoot "Progress-Terminal.cmd"
$Startup = [Environment]::GetFolderPath("Startup")
$Lnk     = Join-Path $Startup "OneTake Revit Progress Terminal.lnk"

if ($Uninstall) {
    if (Test-Path $Lnk) { Remove-Item $Lnk -Force }
    Write-Host "removed $Lnk"
    exit 0
}
$ws = New-Object -ComObject WScript.Shell
$sc = $ws.CreateShortcut($Lnk)
$sc.TargetPath       = $Cmd
$sc.WorkingDirectory = $PSScriptRoot
$sc.Description      = "OneTake Revit live progress terminal (auto-saves checkpoints)"
$sc.Save()
Write-Host "installed: $Lnk  (runs at every logon)" -ForegroundColor Green

$running = $false
$pidFile = Join-Path (Split-Path $PSScriptRoot -Parent) "progress\terminal.pid"
if (Test-Path $pidFile) { try { $running = [bool](Get-Process -Id ([int](Get-Content $pidFile)) -ErrorAction SilentlyContinue) } catch {} }
if (-not $running) {
    Start-Process -FilePath $Cmd -WorkingDirectory $PSScriptRoot
    Write-Host "started the terminal now"
} else { Write-Host "terminal already running" }
