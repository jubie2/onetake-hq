# Approved ADU Set — Reference Standard (Cuong House, PRJ-1133219)

The office's city-approved ADU package. Use it as the checklist for every future ADU submittal
(Keeler and beyond). Approved by City of San Diego; printed 2/4/2026.

- **PDF:** `Dropbox\2024\RESIDENTIAL\Cuong House\PLAN PDF\Approved Plan\Building Construction Plans - Issued PRJ-1133219.PDF` (vector, searchable)
- **Revit model behind it:** `Cuong House ADU REV-2.rvt` (saved 2/4/2026, same day as print)

## The approved 20-sheet structure
| # | Title | Notes |
|---|---|---|
| A01 | Title Page | index, vicinity, abbreviations, symbols, 3D, PROJECT DATA + BUILDING CODE DATA + SCOPE OF WORK blocks |
| A02 | Site Plan | |
| A03 | Nailing Schedule & Notes | GENERAL NOTES / FOOTNOTE / CONNECTION schedules + drafting view |
| A04 | BMP Notes | one big text note on the sheet |
| A05 | General Notes | FLOOR PLAN GENERAL NOTE + MECH General Notes legends |
| A06–A07 | Cal-Green | one raster image per sheet |
| A101 | Floor Plan | **door + window schedules ON this sheet**, W1/W2/W3 wall tags, keynotes, smoke/CO |
| A102 | Sections | keynoted |
| A103 | Roof Plan | |
| A104 | Elevations | keynoted, incl. exterior light |
| A105–A107 | TITLE-24 | energy consultant's stamped forms — per-project, must be ordered |
| A200 | Mechanical Plan | |
| A201 | Electrical Plan | |
| S101 | Foundation / Framing Plan | |
| SD0 | Structure Notes | **empty title block — approved anyway** |
| SD1–SD2 | Structure Details | detail views |

Title block on every sheet: **Drawn By FRANCIS N., Check By JAMES WENG** (or "-"), real drawing date,
job number. Index sheet id "RS-1-7" = the zone (RS-1-7), not a sheet.

## Facts that transfer to any project from this office template
- The Keeler model already contains every "paper" sheet equivalent (same template lineage):
  A03 notes/nailing schedules, A04/A05 CALGREEN rasters, A06 BMP, SD0-SD2. **Nothing needs importing.**
- Title pages carry PROJECT DATA (name/address/owner/legal/zone/APN/year/sprinkler), BUILDING CODE DATA
  (V-B, R-3, 2022 CA codes), SCOPE OF WORK, BUILDING ANALYSIS (area table), DEFERRED SUBMITTAL (solar PV).
- Title-24 is the one package piece nobody in-house can produce.

## Keeler corrections made against this standard (2026-08-24)
- A01 was half Logan-Ave (old project): title, address, scope, building analysis, vicinity map all stale.
  All replaced; parcel data (BLK F*LOT 7*MAP 001899, RS-1-7, APN 551-183-07-00, built 1941) was already right.
- Verified address: **4439 Keeler Ave, San Diego, CA 92113** (geocoded; lat 32.693748, lon -117.098973).
- New vicinity map generated from OpenStreetMap tiles with SITE marker + street labels
  (`revit/reference/keeler-vicinity.png/.pdf`, builder script in scratchpad `make_vicinity3.py` pattern).

## Revit raster-on-sheet gotchas (hard-won, do not re-derive)
1. Revit sizes an imported PNG at **72 DPI regardless of pHYs metadata** — build the PNG at
   `inches*72` pixels. Do NOT set ImageInstance.Width afterward; renders go inconsistent.
2. Wrap the PNG in a **PDF** (pymupdf, page = target inches at 72pt/in) and import that — matches the
   proven CALGREEN pattern.
3. Set **Draw Layer = 0 (Foreground)** or any viewport raster (e.g. a 3D view) paints over it in
   print/export while the bbox still claims it is visible.
4. On-sheet rasters **draw offset (+0.085, +0.085) ft** from where the API places/reports them = the
   36x24-paper-to-titleblock margin. Place at target − 0.085 in both axes.
5. `ExportImage` PNGs of a sheet with an off-position raster grow the canvas — pixel forensics on them
   mislead; verify with native `doc.Export` PDF (`PDFExportOptions`) instead. The PDF output is a tile
   mosaic (raster), so read placement by rendering, not by PDF image objects.

## Keeler step 3-4 outcomes (2026-08-24)
- Titleblock fields set on ADU-1..8: Drawn By FRANCIS N., Checked By "-". Project Issue Date
  ("Drawing Date" on every titleblock) was stale 08.16.23 → 08.24.26.
- **Deviation kept:** door/window schedules stay on ADU-7 — they physically do not fit ADU-1 at
  readable size (approved A101 manages it by *referencing* the CalGreen table instead of placing it).
- Content parity vs approved confirmed for floor plans / sections / elevations / mech / elec
  (same office legends). Added to close real gaps: FUTURE SOLAR PANELS label + shingle
  manufacturer/CRRC spec on the roof plan; ROOF FRAMING NOTE block (truss mfr deferred, 24" o.c.,
  heel 3 15/16", tail 24" 2x4) on the framing plan.
- **Flagged, unchanged:** KEYNOTES SECTION legend says R-30 ceiling batt where the approved set used
  R-38 — Title-24 will dictate the real value; the "MECH General Notes" legend from approved A05 does
  not exist in the Keeler model (would need to be drafted or copied if wanted).
- Note-stacking in these rotated plan views: rows step world-X and render bottom-up — always
  `reversed(lines)`, and keep rows within ~x 1147.5+ or they fall off the crop.

## Keynote tag standard (2026-08-25, Francis-approved pattern)
- Keynote bubbles are the **TAG LABEL generic-annotation family** (one family everywhere; TEXT
  param = keynote number). Never drawn arcs/text: those were retired.
- Each tag gets a **bent leader** pointing INTO its element: `AnnotationSymbol.addLeader()`, then
  set `Leader.End` on the element (~1 ft inside a window pane, on the roof surface, on the lamp),
  `Leader.Elbow` horizontally offset at tag height. Tag sits ~2-4 ft clear of the element.
- **Only keynotes that exist on that face** — no parking unused numbers in the sky (drop 3/6 where
  a face has no louver/door). Repeated elements may repeat the tag (each window its own 2).
- **View names are compass-flipped vs geometry** in the Keeler model: "ADU - West Elevation" shows
  the east face (doors), "South" shows the north face, etc. Match by view name, not by compass.
- API gotcha: TEXT set immediately after `NewFamilyInstance` may not stick (keeps family default
  "5"). Regenerate, re-set, verify — `dev_scripts/retag.py` pattern (also does wipe + copy_from).

## Section keynote layout (2026-08-26, per approved A102)
- 12 tags per section, balanced: LEFT column top-to-bottom 1 shingle / 7 top plate / 2 stucco /
  6 PT bottom plate / 5 weep screed; RIGHT column 9 truss / 11 ceiling batt / 8 studs / 4 gyp bd /
  10 wall batt / 12 footing; 3 slab tagged from BELOW center with a short vertical leader.
- Tag columns sit ~3 ft outside the wall faces; leaders end ON the element.
- Compute building extent from the ADU **roof bbox minus the 1'-6" overhang** — wall-based extents
  pick up stray fragments. Section-view local Y = world Z + offset; get the offset via
  `inv.OfPoint(worldPt)`, never assume 0. (`dev_scripts/section_retag.py`)

## Floor plan numbering standard (2026-08-26, per approved A101)
- **Door marks: 101, 102, ... on 1st floor; 201+ on 2nd — counterclockwise starting at the unit
  entry door.** Window marks: 01+ (1st) / 21+ (2nd), same CCW order. Set the instance Mark; the
  existing Door Tags + schedules pick it up automatically.
- Window tags: the office "Window Tag" family shows the TYPE mark (E/KK/32) — switch tags to
  **"Window Tag - Number"** (ChangeTypeId) to show the instance Mark like the approved set.
- The ADU DOOR/WINDOW SCHEDULES filter on Comments=ADU, so reusing 101/201/01/21 marks that the
  main house also uses only raises duplicate-mark warnings, nothing breaks.
- Plan keynotes (ADU-1 KEYNOTES list: 1 = egress landing, 2 = bath reinforcement) are TAG LABEL
  tags: 1 at each entry landing, 2 near each bath toilet — both floors are separate entry-level
  units here.
- Keeler rotated plan paper orientation: paper-right = world north (+y), paper-down = world east
  (+x). CCW in world = CCW on paper (rotation, no mirror).
- Overlapping door-pair tags (bifold pairs, adjacent doors): nudge `IndependentTag.TagHeadPosition`
  apart along paper-x (`dev_scripts/move_heads.py`).

## Roof sheet layout (2026-08-26, per approved A103)
- Roof sheet carries BOTH the Roof Plan and the **Roof Framing Plan** side by side (framing moved
  off the foundation sheet). Right side: attic-vent note + ROOF LEGEND + roof shingle spec block.
- Roof plan callouts are horizontal text OUTSIDE the roof with a leader arrow in:
  "FUTURE SOLAR PANELS (SEPARATE PERMIT)" on one slope, "NEW ROOF SHINGLE" on the other
  (drawn line + 17-degree barbs + ARCH TEXT 12 1/8", the roof_notes.py arrow pattern).
- Shingle spec block text (ours, not Cuong's product IDs): OWENS CORNING (OR EQ.), CLASS 'A',
  ICC-ESR LISTED / CRRC RATED, OVER (1) LAYER 30# FELT.
- GOTCHA: two earlier shingle-spec TextNotes sat OUTSIDE the roof plan crop - present in the model,
  never printed. `FEC(doc, view.Id)` does NOT return annotations outside the annotation crop, so
  find_text.py (doc-wide TextNote grep by OwnerViewId) is the way to catch orphans.

## Mechanical / Electrical sheets (2026-08-26, per approved A200/A201)
- Mechanical: numbered circles (TAG LABEL, no leaders) sit directly beside each device on both
  floor plans, matching a numbered MECHANICAL KEY NOTES legend. Keeler numbering 1-15:
  1 thermostat, 2 clg diffuser, 3 wall diffuser, 4 bath EF, 5/6 dryer duct+termination,
  7/8/9 kitchen hood/duct/termination, 10 WH P&T, 11 WH flue (2nd flr), 12 attic access (2nd),
  13 return grille, 14 FAU-1 (2nd), 15 IAQ fan. Both floors are separate units - most numbers
  repeat on each floor.
- The MECHANICAL KEYNOTES legend was two description-only TextNotes with NO numbers - rebuilt as
  15 individual notes + TAG LABEL circles, two columns (mech_fix.py). TextNote.Create's width arg
  did NOT wrap at legend scale - use manual \n line breaks for long items.
- Electrical (per approved A201): NO numbered keynotes - symbols + wiring arcs + ELECTRICAL NOTES
  list only. Keeler's electrical legend/notes are an imported DWG (E LEGEND.dwg) citing 2005 NEC /
  2007 CEC - text not editable via API; added a superseding ELECTRICAL CODE NOTE on ADU-6 stating
  2023 NEC / 2022 CEC govern.
- CLEANUP found: ~38 drawn duct/fan symbol curves in the mech plan views sat far outside the crop
  (invisible junk from an early annotation pass) - deleted. Same off-crop-annotation gotcha as the
  roof sheet.

## Sheet numbering standard (2026-08-26, per approved index + office habit)
- Discipline letters: A=architectural, S=structural (SD=structure details), plus A200-series for
  MEP. Approved Cuong index: A01 title, A02 site, A03 nailing, A04 BMP, A05 general notes,
  A06/A07 Cal-Green, A101 Floor Plan, A102 Sections, A103 Roof Plan, A104 Elevations,
  A105-A107 Title-24, A200 Mechanical, A201 Electrical, S101 Foundation/Framing, SD0 notes,
  SD1/SD2 details.
- Keeler ADU sheets renumbered to match: ADU-1->A101 Floor Plan, ADU-3->A102 Sections,
  ADU-4->A103 Roof Plan, ADU-2->A104 Elevations, ADU-7->A105 Door-Windows Schedule & Notes,
  ADU-5->A200 Mechanical Plan, ADU-6->A201 Electrical Plan, ADU-8->S101 Foundation / Framing Plan.
  Sheet NAMES shortened to the approved style (long "4439 Keeler Ave ADU - ..." titles overlapped
  the Drawing Date field in the titleblock).
- The old parallel sheets that held those numbers are PARKED as X-A101...X-S101 (reversible:
  strip the X- prefix) and hidden from the sheet list (Appears In Sheet List = off). When the
  consultant's Title-24 arrives it can take A106+.
- Sheet numbers must be unique doc-wide - park the old holder first, then renumber.

## Mech plan completeness rules (2026-08-26, Francis)
- Attic access goes AGAINST A WALL or OVER A CLOSET, never mid-room; drawn as a dashed 22"x30"
  rectangle + keynote 12. Kitchen/dining supply vents MAY sit mid-room; bedroom vents go at walls
  or over closets. Every restroom gets an exhaust fan symbol (circle + X blades + "EF").
- Mech plans carry ROOM TAGS (NewRoomTag at room centers). Note: Room class can't be collected
  directly - collect SpatialElement and isinstance-filter.
