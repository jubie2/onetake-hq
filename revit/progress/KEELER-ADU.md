# 4439 Keeler Ave ADU — sheet set

Model: `C:\Users\francis nguyen\Dropbox\2025\RESIDENTIAL\4439 Keeler Ave\4439 Keeler Ave (Johnson Version).rvt`
The ADU was already modelled; this job was **building the sheets**, not geometry. Saved 2026-08-21.

## What exists in the file
- 31 pre-existing sheets (A01…SD2) for the main building — use them as the pattern.
- ADU sits at roughly **x 1151…1195, y −159…−119** (project coords).
- Titleblock used: `D 24 x 36 HorizontalNEWLOGO` type **311500** (same as A101). Sheet drawing area
  measures **x 0.04…2.80, y 0.04…1.80 ft** (22x34 block).
- Reusable legends (can sit on many sheets): Floor Plan Legend 1133721, Floor Plan Notes 1620013,
  ELEVATION KEYNOTES 1143900, KEYNOTES SECTION 1143766, ROOF LEGEND 1181019,
  MECHANICAL KEYNOTES 1183388, ELECTRICAL LEGEND 1182820.

## Sheets created (ADU-1 … ADU-6)
| Sheet | Name | Views |
|---|---|---|
| ADU-1 | 4439 Keeler Ave ADU - Floor Plans | ADU 1st + 2nd Floor Plan, Floor Plan Legend, Floor Plan Notes |
| ADU-2 | … Elevations | ADU N/S/E/W Elevation + ELEVATION KEYNOTES |
| ADU-3 | … Sections | ADU Section 1/2/3 + KEYNOTES SECTION |
| ADU-4 | … Roof Plan | ADU Roof Plan + ROOF LEGEND |
| ADU-5 | … Mechanical Plan | ADU Mechanical Plan + MECHANICAL KEYNOTES |
| ADU-6 | … Electrical Plan | ADU Electrical Plan + ELECTRICAL LEGEND |

Every view is a **duplicate** (WithDetailing) of the corresponding existing view, renamed `ADU - …`,
scale 48 (1/4"=1'-0"), crop ON and tightened to the ADU. Duplicates are required because a view can
only live on one sheet.

**Project Name changed** from "John Vo Res-New Duplex ADU" to **"4439 Keeler Ave ADU"** — that is the big
vertical title on the titleblock, so it now reads that way on ALL sheets in the file (the old value was
stale — it named Logan Ave). Revert with `set_project_info.py` if unwanted. Project Address is still the
old Logan Ave text.

## Scripts written for this (dev_scripts/)
`survey.py` (views/sheets/titleblocks/levels), `find_crops.py`, `sheet_info.py`, `build_sheets.py`
(duplicate+crop+create sheet+place), `sheet_layout.py` (auto-pack viewports inside the titleblock),
`normalize_views.py`, `set_crops.py`, `anno_crop.py`, `fix_wide.py`, `label_len.py`, `move_vp.py`,
`replace_vp.py`, `vp_debug.py`, `vp_types.py`, `tb_params.py`, `set_project_info.py`.

## Follow-up pass (user review)
- Elevation / section crops were clipping the roof: they topped out at world Z 25.9..27.3 but Top of Ridge
  is 28.0. `crop_height.py` now sets all ADU elevations+sections to world Z **-4 .. 31** — full house shows.
- Sections had no keynotes/room names. `tag_sections.py` places one keynote tag per distinct
  KEYNOTE_PARAM value found on the visible roofs/walls/floors (model already carries values: roof=1,
  walls=4). `room_labels.py` writes the room name as a TextNote placed on the view plane
  (`NewRoomTag` silently produces nothing in section views — the tag never appears in the view).
  Result: Section 1 = 6 keynote tags / 5 labels, Sections 2 and 3 = 2 tags / 6 labels each.
- **Oversized viewport boxes SOLVED.** `view_outliers.py` lists every element in a view whose bbox
  (converted to view-local coords) sticks out past the crop. Culprit: the **Levels** `1st Floor Level` and
  `2nd FLoor Plan` ran from local X -266 to -159, i.e. 244 ft left of the crop = the missing 5.08 ft of
  paper (244/48). Annotation crop does NOT clip datum extents.
  Fix: `trim_levels2.py` re-points each level to the crop width via
  `SetDatumExtentType(DatumEnds.End0/End1, view, ViewSpecific)` then `SetCurveInView(...)`.
  Note the signature: DatumEnds first, DatumExtentType last - the obvious ordering throws
  "expected DatumEnds, got DatumExtentType".
  Two combinations refuse the trim ("curve is unbound or not coincident with the datum plane"):
  1st Floor Level / 2nd FLoor Plan in `ADU - North Elevation` and `ADU - Section 2`. For those the levels
  are hidden per view instead (`hide_outliers.py`; hide Levels ONLY - the {3D} Camera cannot be hidden and
  one bad id fails the whole `HideElements` call). Cost: those two views show no level datum tags.
  All seven views now have viewport boxes of 0.94-1.02 ft, real view titles, and a clean 2x2 layout.

## Gotchas found
- Viewport size ≠ crop size. Two things inflate it: the **view title line** (set `Viewport.LabelLineLength`)
  and the **annotation crop** (`BuiltInParameter.VIEWER_ANNOTATION_CROP_ACTIVE` = 1).
- Even with both fixed, `ADU - North Elevation`, `ADU - East Elevation` and `ADU - Section 2` report a
  viewport box ~6 ft wide while the drawing is only 0.92 ft, and the drawing sits at the RIGHT end of the
  box. Cause not identified (crop 44 ft, scale 48, anno crop on, label 0.95). Worked around by offsetting
  the viewport centre left by (box/2 − drawing/2). If it needs a real fix, look for an element in those
  views that escapes both crops.
- Sheet coordinates: the titleblock spans x 0…2.83, y 0…1.83 ft. Placing a viewport at negative Y puts it
  off the sheet (that was the first attempt's mistake — copied from A101's stored positions).
