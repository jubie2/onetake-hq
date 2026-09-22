# Ace Crab - 2844 Main St #B, San Diego - Revit build handoff (09.22.26)

Existing-conditions floor plan for the client, built the Grossmont way: Revit model through the
pyRevit routes server, prelim PDF on the Delta title block, a PRELIM CHECK note when done.
Commercial restaurant TI base drawing. Files under `Dropbox/2026/Ace Crab 2844 Main St #B San Diego/`.

**Source:** Polycam room scan 9/18/26 (`[Polycam Floor Plan] 9_18_2026 (2).zip` in the project
folder, and 188 site photos in `Photos/`). The DXF is vector, in feet, cleanly layered, so the
geometry below was parsed straight from it - no tracing. Converter: `revit/tools/dxf-to-walls.py`.
Output: `revit/progress/ace-crab-walls.json` (walls, openings, rooms, equipment, printed dims).
Check drawing: `revit/progress/ace-crab-check.svg` (10 px/ft, plan orientation).

Address on the drawings: **2844 Main St #B, San Diego, CA 92113**. The scan is geotagged
2842 Main St; Jubie says 2844 #B. Put "VERIFY APN" on A01 until SanGIS is checked.

## 1. What the scan established

| Item | Value |
|---|---|
| Footprint | L-shape, 50'-9" x 53'-8" overall (matches Polycam's printed dims exactly) |
| Area | 2,060 sf gross / 1,961 sf net (Polycam) |
| Ceiling | 8'-0" everywhere (closet 7'-6") |
| Walls | 21 wall lines, 308 ft total (Polycam: 309'-4"); 8 exterior, 13 interior |
| Openings | 8 doors, 2 storefront windows, 4 cased openings - every one has a host wall |
| Rooms | 9 |
| Wall thickness | 4" on every wall - **a Polycam SETTING, not measured.** Interior faces are real; exterior walls are certainly thicker (photos decide). |
| Orientation | Geometry left in plan orientation. Plan-up has compass heading 87.9 deg, so true north is toward plan-LEFT (west wall side). Set Revit True North = 87.9 deg. |
| Origin | (0,0) = outer SW corner of the bounding box, X right, Y up on the plan |

Coordinates below are decimal feet from that origin, wall centrelines.

### Walls (`revit_walls` in the JSON has these as `{"id","type","a","b","ext"}`)

Exterior (one side has no room):

| id | dir | line | extent | length | what |
|---|---|---|---|---|---|
| W01 | V | x 0.17 | y 0.17-53.50 | 53'-4" | west wall (opening 201) |
| W02 | H | y 0.17 | x 0.17-50.58 | 50'-5" | south wall (pilaster stub W21 at x 30.58) |
| W03 | V | x 50.58 | y 0.17-34.42 | 34'-3" | **storefront** - windows 01, 02; doors 104, 105 |
| W04 | H | y 34.42 | x 20.25-50.58 | 30'-4" | dining north wall (printed 30'-4") |
| W05 | V | x 14.33 | y 39.25-53.50 | 14'-3" | restroom-block east wall - doors 102, 103 open OUT of it |
| W06 | H | y 53.50 | x 0.17-14.25 | 14'-1" | north wall (printed 14'-5" outer) |
| W07 | H | y 39.17 | x 14.25-20.25 | 6'-0" | corridor north, east part (printed 5'-11") - door 108 |
| W08 | V | x 20.25 | y 34.42-39.25 | 4'-10" | corridor east end (printed 4'-8") |

Interior:

| id | dir | line | extent | length | what |
|---|---|---|---|---|---|
| W09 | V | x 16.17 | y 18.83-34.42 | 15'-7" | kitchen / dining - opening 202 |
| W10 | H | y 34.42 | x 4.92-20.25 | 15'-4" | corridor south / kitchen north - doors 106, 107 |
| W11 | V | x 14.33 | y 3.83-18.83 | 15'-0" | kitchen / prep divider |
| W12 | H | y 39.17 | x 0.17-14.25 | 14'-1" | corridor north / restroom block - opening 203 |
| W13 | H | y 46.25 | x 0.17-14.25 | 14'-1" | restroom 1 / restroom 2 - opening 204 |
| W14 | V | x 10.00 | y 39.25-46.08 | 6'-10" | restroom 1 east - door 101 |
| W15 | H | y 32.50 | x 0.17-4.92 | 4'-9" | corridor SW jog (printed 4'-9") |
| W16 | H | y 18.92 | x 12.42-16.08 | 3'-8" | kitchen pass-through stub |
| W17 | H | y 22.92 | x 12.42-16.08 | 3'-8" | kitchen pass-through stub |
| W18 | V | x 8.08 | y 43.42-46.08 | 2'-8" | fridge closet |
| W19 | V | x 4.92 | y 32.50-34.42 | 1'-11" | corridor jog |
| W20 | H | y 43.42 | x 8.08-9.92 | 1'-10" | fridge closet |
| W21 | V | x 30.58 | y 0.17-1.25 | 1'-1" | pilaster on south wall |

### Openings (marks are provisional; doors 1xx, windows 0x, cased openings 2xx)

| mark | kind | host | position | width | notes |
|---|---|---|---|---|---|
| 101 | door | W14 | x 10.03, y 39.48-42.30 | 2'-10" | restroom 1 - swing drawn in scan |
| 102 | door | W05 EXT | x 14.29, y 39.39-42.37 | 3'-0" | storage -> void east of restroom block |
| 103 | door | W05 EXT | x 14.29, y 46.63-49.48 | 2'-10" | storage/office -> same void |
| 104 | door | W03 EXT | x 50.59, y 16.97-21.28 | 4'-4" | **main entry**, storefront |
| 105 | door | W03 EXT | x 50.59, y 12.19-14.62 | 2'-5" | prep area, storefront wall - too narrow for an exit |
| 106 | door | W10 | y 34.45, x 10.32-13.23 | 2'-11" | corridor <-> kitchen - swing drawn |
| 107 | door | W10 | y 34.45, x 16.60-19.57 | 3'-0" | corridor <-> dining |
| 108 | door | W07 EXT | y 39.15, x 16.99-19.80 | 2'-10" | corridor north wall -> outside |
| 01 | window | W03 EXT | x 50.59, y 1.31-11.17 | 9'-10" | storefront glazing, prep (Polycam: 9'-11" x 5'-8") |
| 02 | window | W03 EXT | x 50.59, y 29.25-33.78 | 4'-6" | storefront glazing, dining (4'-7" x 5'-11") |
| 201 | opening | W01 EXT | x 0.16, y 35.00-38.92 | 3'-11" | **corridor west end, exterior** - a doorway with no door in the scan |
| 202 | opening | W09 | x 16.13, y 19.17-22.65 | 3'-6" | kitchen <-> dining pass |
| 203 | opening | W12 | y 39.15, x 10.27-14.06 | 3'-9" | corridor -> storage |
| 204 | opening | W13 | y 46.22, x 10.27-14.06 | 3'-9" | storage -> storage/office |

### Rooms (Polycam names are residential; use the commercial names)

| no. | name on drawing | Polycam | net sf (CSV) | centroid |
|---|---|---|---|---|
| 101 | DINING | Dining Room | 657 | 24.8, 24.3 |
| 102 | PREP / BACK OF HOUSE | Kitchen 1 | 541 | 26.5, 5.5 |
| 103 | KITCHEN | Kitchen 2 | 483 | 10.2, 18.4 |
| 104 | CORRIDOR | Hallway | 95 | 10.1, 36.1 |
| 105 | RESTROOM 1 | Bathroom 1 | 59 | 6.1, 42.9 |
| 106 | RESTROOM 2 | Bathroom 2 | 54 | 4.1, 49.9 |
| 107 | STORAGE / OFFICE | Other 1 | 42 | 11.0, 49.1 |
| 108 | STORAGE | Other 2 | 27 | 11.7, 42.8 |
| 109 | CLOSET (fridge) | Other 3 | 4 | 9.1, 44.8 |

Room polygons in the JSON run to wall centrelines, so their areas read 2-10% above the CSV
net areas. Use the CSV numbers on the sheet. **There is no wall between 106 and 107 in the
scan** - Polycam split one space into two; it is either a stall partition or a counter. Verify.

### Equipment (29 bounding boxes in `equipment`, 27 matched to the Polycam inventory)

Kitchen (103): 4 sinks along the west wall and on the island, stove + oven together at the SW
corner (E12, 4'-0" x 2'-10", unlabelled because Polycam lists them as two items), 3 cabinets,
1 table. Prep (102): fridge, cabinet, desk, table, chair, TV, and one 7'-5" x 11'-2" run of
counters/shelving mid-room (E19, several cabinets merged). Dining (101): 2 cabinet/counter
runs, table, desk, chairs. Restroom 1: WC + lav. Restroom 2: **WC only, no lavatory.**
Closet 109: fridge. Nothing that looks like a hood, walk-in, or grease interceptor.

### Printed dimensions (Polycam exterior strings) - use as the dimension anchors

50'-9" (south), 53'-8" (west), 34'-7" (east storefront), 30'-4" (dining north), 4'-8" (corridor
east end), 5'-11" (corridor north, east part), 14'-4" (restroom block east), 14'-5" (north).

## 2. Build steps on the PC (Revit + pyRevit routes, port 48884)

```
git pull --no-rebase        # branch claude/trusting-thompson-232391; this adds 4 new files only
```
Read `revit/CLAUDE.md` first. Then:

1. New project from the Pho Hung setup (commercial) or the office template with the code block
   swapped. Save as `Dropbox/2026/Ace Crab 2844 Main St #B San Diego/Ace Crab 2844 Main St.rvt`.
   Confirm it is the open doc: `GET /docs`.
2. `GET /doc` -> real level + wall-type names. Replace the placeholder `type` strings in
   `revit_walls` (`EXT 0'-4"` -> the exterior type; `Generic - 4"` -> the partition type).
   Wall height: 10 ft (ceiling is 8'-0"; structure height unknown).
3. `POST /dev/run {"file":"make_walls.py","args":{"level":"<level>","height_ft":10,"walls":[...revit_walls...]}}`
   Keep the returned `made[].id` against each `W##` - the openings reference hosts by `W##`.
4. `clean_stubs.py` dry run, then `POST /export-view` and LOOK at the PNG before continuing.
5. Doors / windows / cased openings: `POST /place` per opening with `host_wall_id` from step 3,
   `x,y` = opening midpoint, family = the template's door/window/opening symbols by width
   (`w_ftin` in the JSON). Storefront W03: change to the `Storefront` wall type like Pho Hung
   and put windows 01/02 in as curtain panels if that reads better.
6. `POST /room-lines` for the two pass-throughs (202 line, and the 106/107 boundary), then
   `POST /rooms` with the 9 names above, `tag: true`.
7. `POST /dimensions`: the 8 printed strings above + the room-defining interior strings.
8. Equipment: `POST /place` from `equipment[].center` using Pho Hung `PH-xx` families where one
   exists (sink, WC, lav, fridge, range); generic box + label for the rest. Label all "(E)".
   `/schedule-clone` the Pho Hung equipment schedule rather than building one.
9. `build_sheets.py`: A01 Title Page, A100 Existing Floor Plan (1/4" = 1'-0"). Equipment
   schedule sheet only if the client asks.
10. `ev_pdf_export.py` -> `Ace Crab 2844 Main St - EXISTING PLAN 09.xx.26.pdf`.
11. Write `Ace Crab 2844 Main St - PRELIM CHECK 09.xx.26.md` (same sections as Grossmont's).
12. Record element ids in `revit/ace-crab-walls.json` in the `layout-walls.json` ledger shape.

## 3. A01 code block (commercial - no template for this yet)

- Governing code: **2025 CBC** (not CRC) + CEC / CMC / CPC / Energy / CalGreen.
- Occupant load, CBC Table 1004.5, from the net areas: dining 657 / 15 = 44; kitchens 1,024 / 200
  = 6; storage 73 / 300 = 1; **total 51**. That is over the 49 line, so **A-2** with two exits
  required (1006.2.1). If the client seats fewer, B may hold - designer's call. Write both on A01.
- Exits found in the scan: door 104 (4'-4", storefront) and opening 201 (3'-11", corridor west
  end) or door 108 (2'-10", corridor north). Door 105 at 2'-5" is not an exit.
- Plumbing, CPC Table 422.1 at 51 occupants: 2 WC + 2 lav minimum. Scan has 2 WC, **1 lav**.
- Construction type, sprinklers, year built, APN: VERIFY - from photos, SanGIS, and the lease.
- County DEH food-facility plan check is a separate submittal; not this drawing.

## 4. Open items for Dad (goes on the PRELIM CHECK)

1. Exterior wall construction and thickness - the scan draws 4"; photos decide (CMU? stud + stucco?).
2. What is east of the restroom block (x > 14.33, y > 39.25)? Doors 102 and 103 open into it.
   Neighbor unit, yard, or an unscanned back room?
3. Opening 201 at the corridor west end: is there a door? It is the likely second exit.
4. No partition between Restroom 2 and Storage/Office in the scan. Stall? Counter? Nothing?
5. Restroom 2 has no lavatory. Both restrooms are 54-59 sf - check accessible clearances.
6. Hood, grease interceptor, water heater, electrical panel: none visible in the scan.
7. Address: 2844 #B vs the scan's 2842. Confirm from the lease before A01 is printed.

## 5. Photos - not reviewed here

This session's network policy blocks the Dropbox content hosts (403), so none of the 188 HEIC
photos (IMG_5858 through IMG_6045, `Photos/`) could be opened. On the PC, open the ones taken
at the storefront, the corridor west end, the restroom-block east side, and the cook line, and
answer items 1-6 above from them before the PRELIM CHECK is written.

## 6. Notes on the converter

- Polycam splits every wall at each junction and each opening. The converter merges collinear
  pieces (touching, or with an opening between them) into one Revit wall, and never merges an
  exterior piece with an interior one, so W04/W10 and W05/W11 stay separate on shared lines.
- `tools/rationalize.py` was not used: its dedupe keeps only the longest of two touching
  collinear walls, which drops length. The same clustering / inch-snap / anchor logic is inline.
- Re-run: `python tools/dxf-to-walls.py <dxf> <csv> progress/ace-crab-walls.json progress/ace-crab-check.svg [check.png]`
