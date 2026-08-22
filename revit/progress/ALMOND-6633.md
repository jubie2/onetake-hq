# 6633 Electric Ave MDU — Almond Orchard "Plan 3-C" build

Second project (separate from Pho Hung). Read with `progress/PROGRESS.md`.

## Source
- PDF: `C:\Users\francis nguyen\Dropbox\2026\RESIDENTIAL\Nha BS Duc\plan 3-C  Lot 215 for 15070 Almond Orchard Ln.pdf`
- **It is a photo-scan, not vector**: 16 pages, embedded JPEGs ~4813×3482 = 300 dpi of a *reduced*
  16″×11.6″ sheet. Rendering above ~4.5× gains nothing — that is the accuracy ceiling.
- Sheets: **p0 = A3-19 FIRST FLOOR PLAN 'C'**, **p1 = A3-20 SECOND FLOOR PLAN 'C'**,
  p2–p4 elevations (A3-21/22/23), p5–p15 standard details (AD-1…AD-12).
- **Both plan sheets are shell-only**: "FOR INTERIOR NOTES AND DIMENSIONS SEE STANDARD PLAN A".
  Standard Plan A is NOT in this PDF and NOT in the folder (folder holds only this PDF + the .rvt).
  So interior partitions/room sizes cannot be sourced from this set — they must come from
  Standard Plan A or be drafted.

## Revit context (verified, do not re-derive)
- Doc `6633 Electric Ave MDU` = `...\Nha BS Duc\6633 Electric Ave MDU.rvt` (only doc open).
- User's crop region (active AreaPlan "2nd FLoor Level"): **x 740.92…861.74, y −347.06…−246.00**
  (120.81 × 101.06 ft). House is 72.5 × 85 ft, so it fits.
- Levels: Grade −1.50, **1st Floor 0.67**, **2nd FLoor 11.67**, 2nd Ceiling 21.67, Roof Deck 22.67.
- **Plan views are rotated 14.295°** (crop transform) — `1st Floor Plan` id 718579,
  `2nd FLoor Level` FloorPlan id 1715860. Existing building walls: 192 at 0°, 118 at 90°, 94 at 14.3°.
  Axis-aligned new walls therefore render tilted in those views. Rotating the new house by
  14.295° is a one-shot `ElementTransformUtils.RotateElements` if that reading is wanted.

## Scale calibration (first-floor sheet) — verified
Crop box (1299,187)-(3794,3382) of the 4.5× render; **origin px (198.6, 2887); 28.63 px/ft**.
Check: printed bottom chain 21'-0" + 27'-6" + 24'-0" = 72'-6" lands on detected walls at
x = 799 / 1586 / 2273 px (measured 803 / 1589 / 2274). Overall trace = x 0…72.50 ft ✓, y 0…85.0 ft.

## Built so far (NOT saved — user has the file open)
- **Orientation FIXED**: both floors rotated **14.295°** about (801.26, −290.52) then dy −6.0, so they read
  square in the project plan views. Apply that exact transform to anything built later (casita, openings).
- **Floor 2 (A3-20) traced and placed** on `2nd FLoor Level`, height 10 ft, 41 walls after stub cleanup.
  Sheet-to-sheet alignment solved automatically by wall-line correlation: **dx −7.00 ft, dy −2.75 ft**
  (page1 calibration: origin px 197.72, 2862.42; 28.503 px/ft). Check: aligned floor-2 extent
  x 9.34..72.58, y −0.42..84.90 vs floor-1 x 0..72.50, y 0..85.00 — right/top/bottom edges match within
  ~1 in, and the 2nd storey correctly starts 9.3 ft in from the garage face.
- The user's crop region = AreaPlan `2nd FLoor Level` **id 1844391** (x 740.9..861.7, y −347.1..−246.0,
  120.8 × 101.1, rot 0). Crop toggle was off; now switched ON.
- USER CONFIRMED (2026-08-21): build the **Almond Plan 3-C** here, not the existing MDU unit type.

## Earlier state
- 89 walls traced from A3-19 placed on **1st Floor Level**, house origin **(765, −333)**,
  height 11.0 ft, types Generic 6"/5" by traced thickness (4.6–7.1" ≈ 2x4/2x6).
- 45 short trace-noise stubs (<2.6 ft, from text/hatch) deleted → **44 walls** remain.
- Result = a recognisable but **incomplete** shell: gaps where the scan draws walls thin or
  broken by window/door symbols.

## Tooling added (reusable)
`tools/`: `crop.py`, `grid-overlay.py` (labelled pixel grid), `trace-plan.py` (line profiles),
`trace-segments.py` (ink-run segment extractor; `MINTHICK` env filters to wall-weight lines),
`draw-segs.py` (overlay trace on source), `segs-to-walls.py`, `close-shell.py` (cluster collinear
+ extend ends to perpendiculars), `pdf-extract.py`, `pdf-overlay.py`.
`dev_scripts/`: `context.py` (doc/view/crop/levels/wall types), `screenshot.py` (crop → PNG → restore),
`make_walls.py` (list → walls, **safe failure handler**), `clean_stubs.py` (dry-run first),
`view_angle.py`, `audit.py`, `restore_items.py`.

## Next up
- [ ] Close the shell: re-trace with lower thickness threshold per wall run, or hand-fix the
      ~10 gap segments against the sheet; verify overall = 72'-6" × 85'-0".
- [ ] Openings from the sheet callouts (3050 SH, 4050 SH, 5050 SL, 16x8 sectional garage doors,
      2668/2680 doors) — all are labelled on A3-19/A3-20.
- [ ] Second floor (A3-20) on 2nd FLoor Level, then OPT. CASITA (left of both sheets).
- [ ] Drafted interior (user approved a draft), then rooms/areas.
- [ ] Decide orientation: axis-aligned (fits crop) vs rotated 14.295° (reads straight in the
      project's plan views, matches part of the existing building).
