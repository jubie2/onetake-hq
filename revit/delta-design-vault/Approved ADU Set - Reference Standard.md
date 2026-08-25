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
