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

## Cut-off elevations on sheet A105 (2026-08-21)
User reported "the east elevation, west elevation adu is cut off" on the PRE-EXISTING sheet **A105
Elevations** (not our ADU-2). Cause: `East Elev.` and `West Elev.` were cropped to only ~24.5 ft of
world Y (-149..-124.7 and -150.1..-125.6) and Z ~26, while the ADU is **44 ft deep and 28 ft to the
ridge** — so both lost ~10 ft off one side, ~6 ft off the other, and the roof.
Fix: `copy_crop.py` copies a crop rectangle from a source view to a target view of the same
ViewDirection (maps source-local -> world -> target-local, so it works even between different views).
Copied `ADU - East/West Elevation` -> `East Elev.` / `West Elev.` = 44 x 35 ft, Z -4..31. Then
`anno_crop.py` (both were OFF) and `trim_levels2.py` brought the viewport boxes from 2.27/1.17 to
1.02/0.94 ft. `North Elev. (Bldg-1)` / `South Elev. (Bldg-1)` on that sheet were left alone.

## The general datum-trim fix — `set_datums.py`
Supersedes `trim_levels2.py`. Earlier attempts failed with *"The curve is unbound or not coincident
with the original one of the datum"* because they built the replacement line from **view-local** X and
the existing curve's **model** Y/Z — a line that is not in the datum's plane. The working recipe:
1. take the datum's existing curve in the view (model space), `p0` and unit direction `d`;
2. project the crop's four world corners onto `d` to get the needed span;
3. rebuild the line as `p0 + d*(tmin-pad) .. p0 + d*(tmax+pad)` — exactly collinear, so Revit accepts it.
Still fails when a level has **no curve in that view at all** (`GetCurvesInView` empty both for
ViewSpecific and Model): `1st Floor Level` / `2nd FLoor Plan` in `ADU - North Elevation` and all three
in `ADU - Section 2`. Those stay hidden via `hide_outliers.py`, so those two views carry no level tags.

## Sheet clean-up pass (2026-08-21)
- **Viewport titles were off-sheet** because old compensating `Viewport.LabelOffset` values survived the
  box fix: North Elevation **-5.04 ft**, Section 2 **-5.10**, East Elevation **-1.54**.
  `reset_labels.py` zeroes them; do this whenever a viewport box changes size.
- **The real plan-viewport inflator was annotation categories, not the crop.** Hiding **Sections** and
  **Elevations** categories in the ADU plan views dropped the boxes from 1.16 x 1.29 to 0.85 x 0.94
  (those markers belong to the main house). `tidy_plans.py` does category hides + label nudges.
  `hide_each.py` hides outliers one element at a time — `View.HideElements` fails the WHOLE batch if any
  single id is un-hideable (Cameras, group members), so never hide in bulk.
- Dashed rectangle in `ADU - Section 2` = a **Callout** boundary, not the crop and not the imported CAD.
  Hidden via the Callouts category. Imported CAD (`Crystal Design - Comanche Dr.7-14-16.dwg`, 10-13
  instances per view) was also bleeding into every ADU view — `hide_imports.py`.
- Final layout: ADU-1 plans side by side at (0.62/1.62, 1.25), legend (2.45,1.30), notes (0.52,0.40);
  ADU-2 and ADU-3 in a 2x2 at x 0.62/1.80, y 1.33/0.45, legend (2.52,1.60).
## Roof plan annotation — `roof_notes.py` (2026-08-21)
ADU-4 had no slope/ridge annotation, so `roof_notes.py` derives it from the roof solid instead of
hard-coded numbers: walks the geometry, keeps planar faces with `FaceNormal.Z > 0.05` and area > 20 sf,
and reads pitch + direction off each face normal. ADU roof = **5:12 gable**, ridge running east-west at
**Y -138.0 from X 1156.4 to 1188.0**, ridge-to-eave run **13.8 ft** each side, eaves at Y -151.8/-124.2.
Places, per slope: a 9 ft shaft + two barbs as the arrowhead (detail lines), a `5:12` label, an
`EAVE, TYP.` label 1.7 ft inside the eave; plus one `RIDGE` label on the ridge.
`roof_clear.py` lists/deletes what it made (text matching the labels + detail curves under 12 ft).

**The bug worth remembering: a roof plane's outward normal tilts TOWARD the downhill side.** So the
downslope direction is `+horizontal component of the normal`, NOT its negation — the first pass negated
it and every arrow pointed uphill with the labels landing past the ridge on the wrong slope. Sanity
check any slope annotation by confirming the arrow tip is farther from the ridge than its tail.

Two more gotchas from that pass:
- Each sloping face spans the FULL ridge-to-eave run; halving it (mistaking it for a gable half-span)
  gives 2 ft arrows on a 13.8 ft slope.
- `Mesh` has no `.Vertex(i)` in IronPython — use `list(mesh.Vertices)`.
- Text type: use **`ARCH TEXT 12 1/8"`** (0.125 in), what the ROOF LEGEND and the rest of the set use.
  Plain `ARCH TEXT` renders far too small at 1/4" = 1'-0".

## Round 2 — gap-filling against the existing 31 sheets (2026-08-21)
`sheet_audit.py` dumps every sheet with its viewports/schedules; that comparison drove this round.

**ADU-7 Door & Window Schedule** (`adu_schedules.py`, `build_adu7.py`). The ADU's 20 doors / 16 windows
sit on the SAME levels and phase as the main house, so neither can isolate them. Instead **Comments =
"ADU"** is stamped on all 36 (the field was empty, and Comments is already a column in both schedules),
`DOOR SCHEDULE`/`WINDOWS SCHEDULE` are duplicated and filtered `Comments Equal ADU`, and the originals
gained `Comments NotEqual ADU`. **Note this changed A102** — it had been listing the ADU's doors and
windows mixed in with the main house's all along.

**Drawing List needed nothing.** All 37 sheets have `Appears In Sheet List` ON except A301, AD1, L22,
L33, S, SD3, and ADU-1..6 were already in the index. Read the rows with
`GetTableData().GetSectionData(SectionType.Body)` + `GetCellText` — passing an int for SectionType throws.

**ADU-5 / ADU-6 were empty plans** — no lights, outlets, switches, detectors or equipment anywhere in
the ADU footprint. `adu_devices.py` + `adu_annos.py` placed 80 devices over both floors, reusing the
families the main building uses: `Outlet-Duplex`/`Outlet-GFI`/`Switch-Single` hosted on room boundary
walls (outlets 0.8125 ft, switches 3.8125 ft above level — read off existing instances, not invented),
`Supply Register-Floor 2 way`, `Water Heater`, and view-specific Generic Annotations for the ceiling
lights (`High_efficacy_Light`), vanity light, smoke and CO.
- **The `Smoke` family's type names are misleading**: type `CARBONMONOXIDE` draws the SD marker and type
  `Smoke%20Detector[1]` draws the C marker. Verified on screen; don't trust the names.
- Generic annotations are VIEW-SPECIFIC. The first pass put both floors' symbols in one view and they
  stacked invisibly on top of each other. The ADU only had a single MEP plan while A200/A201 each carry
  two, so `adu_mep_views.py` renamed them `ADU - 1st Floor Mechanical/Electrical Plan` and built matching
  2nd-floor views; annotations are now routed by the room's level.
- **Two different views are both named `ELECTRICAL LEGEND`** (id 1182820, the small one A201 uses, and id
  1019342, a full-page symbol table). Match by id, not name. `del_vp.py` removes a viewport by view id.

**ADU-8 Foundation & Framing** (`adu_framing.py`, `framing_notes.py`). There is no structural framing or
foundation modelled anywhere near the ADU (6 structural foundations model-wide, 0 framing), and S101 is
itself **drafted** — 262 detail lines, 138 detail items, 39 text notes. So the ADU sheet is drafted the
same way: ADU exterior footprint **X 1157.9..1186.5, Y -150.3..-125.7 (28.6 x 24.6 ft)**; 15" continuous
footing as a pair of offset lines, 21 floor joists @ 16" o.c., 14 roof trusses @ 24" o.c., plus notes.
`framing_fix.py` hides Rooms/Casework/fixtures so the framing reads.
- **Note placement in a rotated plan view:** these plans are rotated 90 degrees, so world X runs vertically
  on the sheet and world Y horizontally. Stack a note block by stepping **X**, and anchor it OUTSIDE the
  building's X range (X < 1157.9) or it overlaps the drawing. Stepping X also means the list renders
  bottom-up — reverse it.

## Round 3 — matching the office's sheet conventions (2026-08-21)
Driven by comparing each ADU sheet against its main-building counterpart.

- **Notes views duplicated for the ADU**: `ADU - KEY NOTES Floor Plan` (from A101) on ADU-1,
  `ADU - GREEN CODE NOTES` (from A102) on ADU-7, `ADU - ATTIC SECTION` (from A200) on ADU-5.
  Drafting views live on one sheet only, so they must be duplicated - these are independent copies and
  will NOT track edits to the originals.
- **Schedules CANNOT be duplicated through the API** — `View.Duplicate` throws "View cannot be
  duplicated" and `CanViewBeDuplicated` returns False for every ViewSchedule. But Revit DOES allow the
  same schedule on more than one sheet, so `place_sched.py` places the ORIGINALS: TABLE 4.303.2 on ADU-1,
  furnace / dryer / exhaust fan / water heater on ADU-5, Electrical Notes on ADU-6, shear wall on ADU-8.
  One source of truth — editing them updates both the main sheet and the ADU sheet.
- **Door + window tags** (`adu_tags.py`): 36 tags on the ADU floor plans so ADU-7's schedule can be
  cross-referenced. Note A101 has NO door/window tags — this is a departure from the office convention,
  added deliberately.
- **ADU - Section 4** (`adu_section4b.py`): a second transverse cut at **X = 1168.0** looking west,
  giving 4 sections to match A103.
  - `ElementTransformUtils.MoveElement` on a ViewSection does NOT move the cut plane, and neither does
    rewriting `CropBox.Transform` — both silently leave `view.Origin` unchanged. Build the section with
    `ViewSection.CreateSection(doc, typeId, bbox)` instead. Frame: `BasisX` = right, `BasisY` = (0,0,1),
    `BasisZ = right.CrossProduct(up)`; Min/Max `(-22,-17.5,0)..(22,17.5,30)` gives the same 44 x 35 crop
    as the others, and the resulting ViewDirection came out (-1,0,0).
  - Rooms behind a freshly created section are not "visible" to `FilteredElementCollector(doc, view.Id)`
    even with the Rooms category on, so `room_labels.py` returns 0. `sec4_labels.py` places the labels
    from room centres projected onto the section plane instead.

## Section keynotes — why the tags were blank (2026-08-22)
User: "i don't see any keynotes for the sections still." Correct — the tags `tag_sections.py` placed
rendered as **empty circles**, and the only numbered tags on the ADU sections were strays inherited from
the duplicated source view, floating outside the building.

Root cause, in order of discovery:
1. The tags were element keynotes hosted on ADU walls/roofs. Those types DO carry a Keynote value
   (`Generic - 6"` roof = '1', `Generic - 6" NEW 2` = '4', `Generic - 6"` wall = '11').
2. But **the loaded keynote table is Revit's default US CSI file** (keys like `01000`, `09250.E1`,
   `09820.A8`). It contains none of this office's keynote list, so '1' / '4' / '11' resolve to nothing
   and the tag draws an empty bubble. `KeynoteTable.GetKeynoteTable(doc)` → entries confirm this.
3. The office's working tags are **User keynotes**: `Key Source = 'User'` (read-only) and
   `Key Value = '6'` typed by hand. The numbers come from the drafted `KEYNOTES SECTION` legend view,
   not from any keynote table.
4. **The API cannot create a user keynote.** `IndependentTag.Create` with a Reference always produces an
   element keynote; `Key Source` is read-only, and setting `Key Value` on such a tag stores the value but
   displays nothing (verified: Key Value = '9', still renders blank).

Fix: `section_bubbles.py` draws the bubbles directly — a leader line, two semicircle detail arcs
(`Arc.Create` twice; a full-circle arc is rejected), and the number as a TextNote in `ARCH TEXT 12 1/8"`.
Numbers match the legend: 1 roof shingle, 9 roof truss, 7 double top plate, 2 stucco, 4 gyp bd,
6 PT bottom plate, 3 slab on grade, 12 footing. Targets are taken from each element's bounding box in
VIEW coordinates and pulled to the **right-hand end** of the element, with the bubble column at
`cropMax.X - 5.2`, so the leaders stay short and parallel instead of crossing the drawing.
For the roof use the bbox BOTTOM (`min.Y + 0.5`) — the top-right corner of a sloped roof's bbox is in
mid-air.

**Caveat:** `clear_bubbles.py` deletes every CurveElement in those views, which also removes leader lines
that came with the duplicated source section. Re-running the pair is safe but non-restoring.

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

## Keynotes on the rest of the sheets + roof plan finish (2026-08-22)
`plan_bubbles.py` extends the drawn-bubble approach to elevations and floor plans.
- **ADU-2 elevations** use ELEVATION KEYNOTES 1-6. Targets are filtered to the face being looked at:
  `LIMIT = nearest-wall depth + 3.0` in view-local Z, so North/South get 1,2,4 while East/West also get
  3 (gable louver) and West gets 6 (exterior door). Numbers that are not visible on a face are correctly
  skipped. Roofs are exempt from the depth filter - a roof spans the whole depth by definition.
  The depth filter is meaningless in a plan view, so it is disabled for the plan group.
- **ADU-1 floor plans** use KEY NOTES 1 (egress landing at the entry door) and 2 (bathroom backing).
  **Every ADU door reports an Interior host wall**, so `extdoor` found nothing - the entry reads as an
  opening in the model. Falls back to `perimdoor`: the widest door closest to the perimeter rectangle.
- Bubbles are parked beside their target (+3.0, +2.2 ft, flipped if that leaves the crop) rather than in
  a column, because long diagonal leaders made it impossible to tell what was being keyed.
- **ROOF LEGEND and MECHANICAL KEYNOTES are note lists, not numbered keynotes** - nothing to bubble.

**Roof plan: it IS the ADU's roof** - 31.6 x 27.6 ft over the 28.6 x 24.6 ft ADU footprint, a uniform
**1'-6" overhang**. It was NOT finished: floor registers, stairs, railings, floors and rooms were all
showing through, and there were no material notes. `roof_finish.py` hides 14 clutter categories and adds
shingle / sheathing / fascia / overhang / attic-ventilation notes.

**Still open:** the Floor Plan Legend defines wall types W1/W2/W3, but nothing tags walls on the ADU
plans - and A101 does not tag them either (0 wall tags). The ADU's main exterior type
`Generic - 6" NEW 2` has **no Type Mark at all**, so tagging it would first need a mark assigned, and
that type is shared with 49 walls outside the ADU.

## Wall tags + full keynote coverage (2026-08-22)
- `wall_tags.py` assigns the missing **Type Mark `W2`** to `Generic - 6" NEW 2` (the ADU's exterior
  type had none) and tags the longest wall of each marked type on both floor plans.
  `prune_walltags.py` then dropped the W3 tag: the only `Generic - 6"` wall near the ADU is at
  **Y -158.7, outside the building rectangle** (it is the stair-landing wall), so the ADU itself uses
  only **W1 interior and W2 exterior**. Note the Type Mark change also affects 49 walls elsewhere in the
  model - harmless, since nothing tags walls on the main sheets.
- Section keynotes went from 8 to the full **12**: added 5 weep screed, 8 studs, 10 R-15, 11 R-30.

**Which keynotes land on a real element, and which only mark the right location** — worth knowing before
anyone redlines them:
- *Real element:* 1 roof, 2 stucco (wall face), 4 gyp bd (inner face), 3 slab, 12 footing,
  and on elevations 2 window, 3 gable louver, 6 exterior door.
- *Approximate - the component is not modelled*: 9 roof truss, 7 double top plate, 6 PT bottom plate,
  5 weep screed, 8 studs, 10 R-15 and 11 R-30 insulation. The walls are generic single-layer types with
  no studs or insulation layers, and there are no trusses or plates in the model, so the leaders point at
  where each item belongs rather than at an element.
- *Not keyed at all:* elevation keynote **5 EXTERIOR LIGHT** - no exterior light fixture exists on the ADU.
- Floor-plan keynote 1 points at door 238, the door nearest the perimeter. **Every ADU door reports an
  Interior host wall**, so the model has no true exterior door to key.

## Full elevation keynote coverage (2026-08-22)
All six ELEVATION KEYNOTES now appear on ADU-2. Two things had to be fixed first:
- **Keynote 5 EXTERIOR LIGHT had nothing to point at** - the ADU had zero lighting fixtures.
  `ext_lights.py` places 4 `Antique_Doorwall_lamp_10251` sconces (east wall by the entry, west wall by
  the stair, both floors) at 6'-6" above each level.
- **That lamp family never renders in an elevation** - not in the ADU's and not in the main building's
  either. It shows in plan, 3D and section views only (`lamp_vis.py` proves it: 5 pre-existing lamps,
  visible in 8 plan/3D views and in `ADU - Section 4`, and in no elevation at all). Flipping the
  instance does not help. So `plan_bubbles.py` pulls the lamps straight from the document and projects
  them into the view by hand instead of relying on the view's element set - the fixture really is there,
  it just does not draw on an elevation with this family. **Swap the family if the sconce must be
  visible on the elevations.**
- Also relaxed `extdoor`: it briefly required an Exterior host wall, which matches nothing here because
  every ADU door reports an Interior host.

Coverage by face (each elevation keys only what is actually on it, which is the correct convention):
South 1,2,4 · North 1,2,4,5 · East 1,2,3,4,5 · West 1,2,3,4,5,6.
The "grilles" in the middle of the north/south walls are the 36"x16" **bathroom windows**, not louvers -
keynote 2 is the right call there. The gable louvers only exist on the east and west gable ends.

**Update:** user wants every legend item keyed on EVERY elevation, not only on the face where it is
visible. `LIMIT` is now unbounded for the elevation group (`FACE = nearD + 3.0` is kept only for
choosing a blank patch of the wall we are actually looking at for keynote 4). All four elevations now
carry 1-6. Trade-off, deliberate and at the user's direction: on the north and south elevations the
louver and exterior door leaders point at the correct part of the building, but those items are on the
gable ends and so are not drawn on that face.

## Audit: which elevation keynotes have nothing drawn under them (2026-08-22)
`keynote_audit.py` reports, per elevation, the element each keynote points at, its depth past the face
being viewed, and whether it is in that view's drawn element set.

**Keynote 5 EXTERIOR LIGHT - nothing drawn, on all four elevations.** The fixture exists at the right
spot, but the lamp mounts on the INSIDE face of the wall (centre 1185.63 against an east wall face at
1186.29-1186.71) so the wall hides it. Tried and failed: `flipFacing()` (no movement), deleting and
re-placing with the insertion point outside the wall (Revit snaps it back to 1185.63 every time), and
swapping to `Emergency Wall Light` (still 0 visible). **No elevation anywhere in this model draws a
lighting fixture** - `lamp_vis.py` shows all 9 lamps appearing only in plan, 3D and `ADU - Section 4`.

**Keynotes 3 louver and 6 exterior door - nothing drawn on NORTH and SOUTH.** They sit 9-12 ft behind
the face being viewed (gable ends / other walls), so the leader is at the right position but the near
wall hides the item. On east and west they are on the face (louver -0.1 ft, door +2.3/+3.7) and read
correctly.

Keynotes 1 roof, 2 window and 4 stucco land on drawn geometry on all four elevations.

For context, the main building's own elevations carry **almost no keynotes at all**: North/East/West
have zero tags, South has two (both "1"). The ADU set is now more thoroughly keyed than A105.

## A105 also needed the keynotes (2026-08-22)
The user was looking at **A105**, the pre-existing elevation sheet, while all the keynote work had gone
onto **ADU-2**. Both sheets show the same ADU (A105's four elevation views were re-cropped to it earlier
in this job), so `plan_bubbles.py` gained an `a105` group covering
`North Elev. (Bldg-1)`, `South Elev. (Bldg-1)`, `East Elev.`, `West Elev.` - all four now carry 1-6.
Lesson: when the user says "the elevation sheet", check WHICH sheet - this model has two of them for the
same building.

## Round 4 — corrections against the approved Cuong set (2026-08-24)
Reference: `delta-design-vault/Approved ADU Set - Reference Standard.md` (full analysis + gotchas).
- Step 1 (import paper sheets): **nothing to import** - Keeler already has all equivalents; the
  approved set even shipped SD0 empty.
- Step 2 (title page + site plan): fixed A01's stale Logan-Ave content (title, address, scope,
  building analysis, project data owner/name), added verified ZIP 92113 everywhere incl. Project
  Address, and replaced the Logan vicinity map with a generated OSM map of the real site.
  A02 site plan already covers the ADU (13 dims near it).
- Steps 3-4 pending: door/window schedules onto ADU-1 per approved A101 convention, titleblock
  Drawn/Check/date fields, then a sheet-by-sheet gap pass against the approved PDF.
- User is mid-touch-up on some sheets - ASK WHICH before modifying existing ADU sheets.
