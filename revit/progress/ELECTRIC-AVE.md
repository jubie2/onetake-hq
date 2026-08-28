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
