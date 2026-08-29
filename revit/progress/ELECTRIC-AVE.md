# 6633 Electric Ave ADU — sheet set build log

Model: `Dropbox/2025/RESIDENTIAL/6633 Electric Ave/6633 Electric Ave MDU - Johnsons Version (Full Sheet Plan).rvt`
Delivery PDF: `Dropbox/2025/RESIDENTIAL/6633 Electric Ave/6633 Electric Ave ADU - Plan Set 08.27.26.pdf` (30 pages)

## Project facts (verified sources)
- Owner **Steven Truong**, 6633 Electric Ave, La Jolla, CA 92037 — Coastal Zone (proposal PDF in project folder).
- Scope: demolish existing detached garage (~400 SF); new detached two-story **Duplex ADU**
  w/ attached garages + roof deck (dad's site plan labels it "Proposed Duplex ADU").
- Survey (LEBL LSM 25143): **APN 351-493-10**, POR. LOT 10, HYMAN'S ADDITION, MAP NO. 1808,
  DOC NO. 2019-0311700. PL bearings N75°02'E 82.03 / N03°05'W 71.54 / N8°51'40"W 70.40 / N75°02'E 89.24.
- Areas from model rooms: 1st floor living 900 SF + garages 228/222 SF; 2nd floor living 1,093 SF
  + deck 263 SF; roof deck 1,148 SF; total living 1,993 SF.
- New ADU geometry lives at world (1126–1192, 71–122); OLD Logan Ave buildings still modeled
  around (940–1030, −160..−80) — every stale sheet was pointing there.

## Session 2026-08-27 — full set rebuilt to Keeler standard
- **ProjectInformation** set (name/address/owner/job 022225/date 08.27.26) → all titleblocks.
- **A01**: header, scope, project data (APN/legal/owner/coastal), building analysis from real room
  areas, vicinity labels (ELECTRIC AVE / LA JOLLA BLVD / COLIMA ST), old strike-out X removed.
- **A02**: Site viewport was parked off-sheet → placed; plumbing fixture calc rewritten
  (existing res no-change + duplex ADU per-unit fixtures); John Vo signature curves deleted;
  empty rev cloud deleted.
- **A101**: fixed 2nd-floor crop to match 1st (4-corner transform map), both plans 3/16" side by
  side, stale "BLDG 3&4" note deleted, north arrows re-anchored. Door marks **101–114 / 201–210**
  (CCW from entry), window marks **01–07 / 21–33**; all doors/windows tagged; Comments=ADU.
- **A102**: both schedules filtered Comments=ADU → overlap gone, only ADU rows.
- **A103**: 4 NEW sections cut on the ADU (2 cross, 2 long), keynote-tagged both sides, legend
  reworded for flat roof (Class A roof deck; joists per plan).
- **A104**: Roof Deck Level view placed as Roof Plan (3/16"); shingle/attic-vent notes replaced
  with roof-deck membrane / guardrail / trellis / drainage notes. Old truss layout removed.
- **A105**: 4 NEW elevations (section-type) of the ADU, tagged (guardrail/trellis/windows/stucco/
  lights/doors/garage doors/ext stair), legend rebuilt w/ item 8 added.
- **A200**: two NEW mech plan views (room tags + keynote bubbles 1–14), mini-split design
  (no attic on flat roof → dropped FAU/attic access/return grille; kept EF/dryer/kitchen/WH
  keynotes; SD/CO as keynotes 12/13 on mech only). Furnace schedule removed; attic section removed.
- **A201**: two NEW elec plan views; placed 23 recessed cans, 15 GFI (kitchen counters ~2 ft,
  baths, garage), 12 duplex outlets, 14 switches (wall-hosted, nearest-wall snapped).
- **A06**: new "BMP Site Plan - Electric" (fiber roll perimeter, TC-1 entrance, WM-8 washout,
  WM-9 toilet, SE-4 note) swapped in at 1:160.
- **L1**: stale old-site "Landscaping Plan Copy 1" viewport removed.

## Session 2026-08-28 — sections/elevations re-cut SQUARE to the building
Francis: "the elevation and section cuts are incorrect its not straight and diagonal to the plan".
- **Root cause:** the ADU sits at **14.3 deg** in world coords (468 ft of walls at 14.3, 386 ft at
  104.3). The first pass cut all 8 views along world X/Y, so every cut sliced the building
  diagonally. Verified with `ev_wall_angles.py` (direction histogram: only 14.3 / 104.3 exist).
- Defined a building frame u = 14.3 deg (bldg east), v = 104.3 deg (bldg north) and re-cut all
  4 elevations + 4 sections with `bx` along the frame (`ev_recut2.py`). Cut stations, in the
  building frame relative to the footprint centre: Section 1 s=-20 (bedrooms), Section 2 s=+18
  (garage), Section 3 t=+11 (north rooms), Section 4 t=-3 (south rooms).
- **First re-cut used a wrong centre**: the oriented bbox from "all walls in the region box"
  caught neighbouring site walls, giving t +/-19.6. The TRUE footprint, taken from opening
  stations, is **s -31..+27, t -7..+20.5** (58 x 27 ft), centre world (1157.520,104.868).
  Tag leaders aimed at t=-13..-15 landed in blank space until this was corrected.
- Re-tagged all 8 views (`ev_retag2.py`): tag parks at the paper edge on the same side as its
  target (side chosen from `(target-origin).RightDirection`), leader End on the real element.
- Sheet layout: rows at y=1.55 / y=0.40, keynote legend re-centred at (1.24,0.95) in the clear
  band between them; A103 right legend column re-anchored (5.58,7.58); A105 keynote 8 bubble
  circle copied from bubble 7 (a legend "bubble" is a TextNote + a separate small CurveElement -
  copying the text alone leaves a naked number).

## Session 2026-08-28b — roof framing plan + mech keynotes made real
Francis: "do the roof framing plan and for the mechanical plan the keynotes aren't actually
pointing to anything".
- **Why the mech keynotes pointed at nothing:** the first pass placed keynote tags at guessed
  coordinates, but **no mechanical devices were ever modelled** in the new building
  (census: MechEquip 0, AirTerminal 0). Leaders ended in empty space.
- `ev_mech_devices.py` now DRAWS the devices in each mech view (detail lines/arcs, view-owned so
  they don't pollute the arch plans) and tags them: thermostat, 3 mini-split heads/floor,
  condensing unit on pad, ceiling exhaust fans, dryer + kitchen duct runs w/ terminations,
  kitchen hood, IAQ fan; plus real `Smoke` annotation symbols for SD/CO. Keynotes 1-14 all now
  land on something. Water heater / dryer / cooktop keynotes point at the **existing families**
  (WH 2192006 & 2241258, dryer 2192532, cooktops 2194496 & 2207534).
- **'Smoke' family types are INVERTED vs graphics here too** (type `CARBONMONOXIDE` draws "SD",
  type `Smoke Detector[1]` draws the CO circle) - same gotcha as Keeler; `ev_mech_fix.py` swaps.
- Tag placement rule that worked: park the bubble 3.2 ft radially outward from the footprint
  centre, leader End on the device. SD/CO bubbles then nudged 2 ft further out so they clear the
  room-name tags.
- **Roof framing plan** (`ev_roof_framing.py`): new view "ADU Roof Framing Plan" duplicated from
  Roof Deck Level, joists at 16" o.c. drawn in the two blocks with spans in the SHORT direction -
  main block (s -27.7..8.2, t -6.0..19.6) spans t with a 4x12 beam at mid-t; east wing
  (s 8.2..22.5, t -1.4..16.6) spans s. Note: sizes/connections per structural engineer.
  Placed on **A104** beside the roof plan; A104 renamed "Roof / Framing Plan" (the A01 index is a
  live **Drawing List schedule**, so it re-titles itself - no manual index edit needed).

## CRASH: Revit stack-overflows on this model
Three crashes on 8/27 were traced to `/schedule-read` of the Pho Hung schedule (see memory
`revit-schedule-read-crash`); `checkpoint.ps1` is now gated and that is fixed. On 8/28 Revit
stack-overflowed **twice more**, both times while `ev_bldg_frame.py` ran - the only script that
**iterates `OfCategory(OST_Rooms)`** - with an Area Plan view active. Dump exception both times:
`0xC00000FD STACK_OVERFLOW`. Walls-only (`ev_frame_walls.py`) and walls+FamilyInstances
(`ev_faces_frame.py`) run fine on the same model.
**Rule: do not collect Rooms/Areas in this model - derive geometry from walls + family
instances.** Face classification: `FamilyInstance.FacingOrientation` is unreliable here (it
labelled the t=+19.6 face 'S'); classify by the element's station instead.
Crash triage: `%LOCALAPPDATA%\CrashDumps\Revit.exe.<pid>.dmp` (parse minidump stream type 6 for
the exception code) + latest `Journals\journal.*.txt` tail for the active view / last add-in call.

## Flags for dad / Francis (not resolvable from the model)
- **S / S101 / SD0–SD3**: S is empty; S101 foundation/framing still shows the OLD Logan bldg —
  no structural model exists for the new ADU (structure engineer scope). SD details generic.
- **A104**: no roof framing plan for the flat roof yet (engineer/truss calc per proposal).
- **Zone + Year Built** on A01 left "-" (not in any source doc). Coastal zone noted YES.
- Vicinity map cross-street "COLIMA ST." — eyeball check.
- A02 grading quantities / disturbance 1900 SF / impervious 1783 SF inherited from Logan — confirm.
- L2/L3/L22/L33 landscaping details/calcs still old-site; Title-24 A106–A110/A301 = consultant.
- A201 electrical layout is a first-pass draft (device counts/locations reasonable but review).
- Mech general notes column still duct/furnace-flavored boilerplate.

## API gotchas learned this session (also in vault)
- **Dependent views**: 718579 "1st Floor Plan" is a DEPENDENT of view 32. Duplicating a dependent
  yields another dependent — annotations + category visibility are SHARED. Check GetPrimaryViewId
  before duplicating; duplicate the primary for independent copies.
- Rotated plan views: crop transform ≠ world. Setting CropBox ignores the assigned Transform.
  To rotate a fresh view's crop: reveal crop element (toggle CropBoxVisible, diff FEC ids),
  ElementTransformUtils.RotateElement it, then set min/max via 4-corner world mapping.
- ViewSection.CreateSection: visible region = +BasisZ side of the cut plane; final
  ViewDirection/RightDirection are NEGATED from the passed basis.
- Wall Location.Curve lives at the wall's base Z — project XY targets at the curve's own Z or
  distances include the height (silent all-miss).
- parcel DXF import + camera showed in new views → HideElements per view; viewport outline
  inflated by out-of-crop annotations → enable annotation crop (VIEWER_ANNOTATION_CROP_ACTIVE).
- Viewport.Create may pick a titleless viewport type — ChangeTypeId from a sibling viewport.
- Routes server response got crossed once with the progress terminal's snapshot (got walls JSON
  for a dev/run) — re-run the script and verify effects before assuming failure.
