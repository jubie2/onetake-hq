<#
.SYNOPSIS
  Render the OneTake layout (walls, doors, equipment bboxes with item numbers, rooms)
  from the live Revit model into a PNG so it can be compared with the drawing.
  Region defaults to the Pho Hung layout (x -2..70, y -28..66 ft).
.EXAMPLE
  .\render-plan.ps1 -Out C:\temp\plan.png
#>
param(
    [string]$Out = "$PSScriptRoot\..\progress\model-plan.png",
    [double]$X0 = -2, [double]$X1 = 70, [double]$Y0 = -28, [double]$Y1 = 66,
    [double]$Scale = 14,        # px per ft
    [string]$Base = "http://localhost:48884/onetake-v1",
    [string]$ItemsJson = ""     # optional eq_items.json (item -> ids) to label equipment
)
Add-Type -AssemblyName System.Drawing
$W = [int](($X1 - $X0) * $Scale); $H = [int](($Y1 - $Y0) * $Scale)
$bmp = New-Object System.Drawing.Bitmap $W, $H
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode = 'AntiAlias'; $g.Clear([System.Drawing.Color]::White)
function PX($x) { [float](($x - $X0) * $Scale) }
function PY($y) { [float](($Y1 - $y) * $Scale) }
$penWall = New-Object System.Drawing.Pen ([System.Drawing.Color]::Black), 3
$penThin = New-Object System.Drawing.Pen ([System.Drawing.Color]::Black), 1.5
$penGlass = New-Object System.Drawing.Pen ([System.Drawing.Color]::SteelBlue), 2
$penLow  = New-Object System.Drawing.Pen ([System.Drawing.Color]::Gray), 2
$penEq   = New-Object System.Drawing.Pen ([System.Drawing.Color]::DarkRed), 1.5
$penDoor = New-Object System.Drawing.Pen ([System.Drawing.Color]::DarkGreen), 2
$penGrid = New-Object System.Drawing.Pen ([System.Drawing.Color]::FromArgb(230,230,230)), 1
$font = New-Object System.Drawing.Font 'Arial', 9
$fontS = New-Object System.Drawing.Font 'Arial', 7
$fontB = New-Object System.Drawing.Font 'Arial', 8, ([System.Drawing.FontStyle]::Bold)
$brush = [System.Drawing.Brushes]::Black; $brushR = [System.Drawing.Brushes]::DarkRed; $brushB = [System.Drawing.Brushes]::Navy
# grid every 10 ft
for ($x = [Math]::Ceiling($X0/10)*10; $x -le $X1; $x += 10) { $g.DrawLine($penGrid, (PX $x), 0, (PX $x), $H); $g.DrawString("$x", $fontS, [System.Drawing.Brushes]::Gray, (PX $x)+2, 2) }
for ($y = [Math]::Ceiling($Y0/10)*10; $y -le $Y1; $y += 10) { $g.DrawLine($penGrid, 0, (PY $y), $W, (PY $y)); $g.DrawString("$y", $fontS, [System.Drawing.Brushes]::Gray, 2, (PY $y)-10) }
# walls
$walls = (Invoke-RestMethod "$Base/walls" -TimeoutSec 120).walls | Where-Object { $_.start[0] -ge $X0 -and $_.start[0] -le $X1 -and $_.start[1] -ge $Y0 -and $_.start[1] -le $Y1 }
foreach ($w in $walls) {
    $pen = $penWall
    if ($w.type -match 'Storefront|Curtain') { $pen = $penGlass }
    elseif ($w.type -match 'walkin') { $pen = $penThin }
    elseif ($w.type -match '5"') { $pen = $penThin }
    $g.DrawLine($pen, (PX $w.start[0]), (PY $w.start[1]), (PX $w.end[0]), (PY $w.end[1]))
}
# patio low walls are Generic - 6" ... drawn same; fine
# equipment + doors
$ids = @()
$labels = @{}
if ($ItemsJson -and (Test-Path $ItemsJson)) {
    $items = Get-Content $ItemsJson -Raw | ConvertFrom-Json
    foreach ($p in $items.PSObject.Properties) { foreach ($i in $p.Value.ids) { $ids += [long]$i; $labels["$i"] = $p.Name } }
}
if ($ids.Count) {
    $e = Invoke-RestMethod "$Base/element-info" -Method Post -ContentType application/json -Body (@{ids=$ids;params=@()}|ConvertTo-Json) -TimeoutSec 120
    foreach ($el in $e.elements) {
        if (-not $el.bbox) { continue }
        $r = New-Object System.Drawing.RectangleF (PX $el.bbox[0]), (PY $el.bbox[3]), (($el.bbox[2]-$el.bbox[0])*$Scale), (($el.bbox[3]-$el.bbox[1])*$Scale)
        $g.DrawRectangle($penEq, $r.X, $r.Y, $r.Width, $r.Height)
        $lab = $labels["$($el.id)"]
        $g.DrawString($lab, $fontB, $brushR, $r.X + $r.Width/2 - 7, $r.Y + $r.Height/2 - 6)
    }
}
# doors: everything of category Doors in region -> from /walls? we don't have a list verb; caller passes via ItemsJson "_doors"
if ($items -and $items._doors) {
    $e = Invoke-RestMethod "$Base/element-info" -Method Post -ContentType application/json -Body (@{ids=@($items._doors);params=@()}|ConvertTo-Json) -TimeoutSec 120
    foreach ($el in $e.elements) { if ($el.bbox) { $g.DrawRectangle($penDoor, (PX $el.bbox[0]), (PY $el.bbox[3]), (($el.bbox[2]-$el.bbox[0])*$Scale), (($el.bbox[3]-$el.bbox[1])*$Scale)) } }
}
# rooms (name + area at centroid unknown -> list only)
$rooms = (Invoke-RestMethod "$Base/rooms" -TimeoutSec 120).rooms | Where-Object { $_.level -eq '1st Floor Level' -and $_.area_sf -gt 0 }
$yy = 12
foreach ($rm in ($rooms | Where-Object { [int]$_.number -ge 37 })) { $g.DrawString(("{0}  {1:N0} SF" -f $rm.name, $rm.area_sf), $fontS, $brushB, $W-330, $yy); $yy += 11 }
$g.Dispose()
$dir = Split-Path $Out -Parent; if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Force $dir | Out-Null }
$bmp.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png); $bmp.Dispose()
Write-Host "wrote $Out ($W x $H)"
