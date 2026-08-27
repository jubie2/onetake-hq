# Revit / OneTake — PROGRESS (read this first)

<!-- auto --> **Last checkpoint:** 2026-08-26 20:12:54 | Revit: up, '', 1 walls, schedule 1 rows | git claude/trusting-thompson-232391@1a04774, 5 uncommitted

This file is the single "where did we leave off" note. The header line above is
rewritten by `tools/checkpoint.ps1`; the sections below are edited by hand (or by
Claude at the end of a session). Machine snapshot lives next to it in
`state.json`, the equipment schedule export in `schedule-latest.csv`, and the
append-only history in `log.md`.

## Where we left off
- 2026-08-21 — **File identity check.** Revit had been reopened on `Pho Hung El cajon REV-1.0001.rvt` (a Revit BACKUP file, a snapshot from 8/18 ~01:30: curtain walls 4977749/4977659 still present, old restroom W wall 4978049, no wok range, 26 schedule items, 309 walls). Saved + closed it and reopened **`Pho Hung El cajon REV-1.rvt`** = our real model (315 walls, wok 4984262, restroom walls 4983947-54, S wall 4981922, curtain walls gone). Item 04 (W-entry air curtain) had gone missing from it, so re-placed as **4984843** on wall 4978041 at (6.3,41.9) with params + tag -> schedule back to **29 items**, tag audit 35/35. Saved. RULE: always confirm the open doc via GET /docs before editing — `.000N.rvt` names are Revit backups, not our file.
- 2026-08-18 03:40 — Polish pass: exterior walls -> Generic 6" (pdf thickness); wok range 06 replaced by real family `Wok_Range_Gas_12` type PH-06 9FT (4984262, x 29.2-38.2 exactly per pdf; Generic Models + OneTake Generic Model Tag); floor sinks/drains at the pdf F.S./F.D. label spots (4982000-4,4984244-7); cashier counter 34" high, kitchen counter 2-6 deep (type PH-COUNTER 30in); dims added 14 (cooler) / 7 (cooler depth) / 10 (service run) / 33-1 restored. Audit: 29 rows, 35 tags OK. Saved. Remaining nits: hood 05/13 plan symbol includes duct (type says 12x4/7x4), shelf 22 family fixed 4 ft (pdf 5 ft), dining room areas differ from pdf 500/500 (geometry follows dims).
- 2026-08-18 03:10 — **PDF-line-registered rebuild + full audit.** `tools/pdf-overlay.py` registers the vector PDF (origin pt 297.4,1223.2; 18 pt/ft) to model feet, draws `progress/pdf-vs-model-overlay.png`, lists PDF lines w/o model wall (`progress/pdf-gaps.json`). Walls corrected: wing E wall jogs to x 33.25 above y 48.5 (walls 4983953/4983954), women block y 41.5/47.35/53.15 w/ chase 24.9-26.6 (4983947-4983952), men W 25.8 (4983949), diagonal end (33.25,63.7), kitchen S wall y 15.25 x 28.6-56.15, alcove x 56.15/y 8.25, cooler 42.2-55.8 x 16.9-23.5 door .8, W wall segs 12.75/26.5/40.4/43.4, rooms N wall 12.75. Doors 4983956 (women) 4983957 (men). Items 04/29 re-placed (4984121/4984122). Audit: 29 schedule rows, 35 tags reseated, all doors swing/hinge per pdf, rooms valid (women 93, men 57). Dims 52-7/49-3/30-1/28-10/33-1/30-7 present. Saved REV-1.
- 2026-08-18 02:30 — **Vector PDF acquired**: `revit/reference/pho-hung-el-cajon-plans.pdf` (8 sheets; Equipment Plan = page index 3). `tools/pdf-extract.py` (run with pyRevit CPython, PyMuPDF in tools/pylib) renders it (`reference/equipment-plan.png`, 10368x6912) and dumps 4748 line segments + 703 words to `reference/equipment-plan-lines.json` (PDF points; 1/4"=1ft -> 18 pt/ft). NEXT: locate the plan origin in that file, convert to feet, and overlay/diff against the model walls exactly (no more screenshot guessing).
- 2026-08-18 02:20 — Restroom block reshaped to pdf: women W wall 4983939 (24.9, 40.7-52.6) w/ door 4983940 (hinge 47.7, swings W); men W wall 4983935 (25.6, 52.6-59.12) w/ door 4983941 (hinge 53.8); men S wall 4978051 (24.9-34.75 @ 52.6); vestibule/alcove partitions 4983936 (31.1, 49.4-52.6) + 4983937 (29.6-34.75 @ 46.6); women WC in alcove (32.6,50.5) facing S. Saved.
- 2026-08-18 02:00 — **Curtain walls replaced by solid Generic 8" walls + Fixed2 windows** (S: 4981922 w/ windows 12-19.1, 21.9-32.6, 36.2-46.7, 52.5-62.5; W: 4981923/4981924 w/ 13.9 & 6.45 ft windows; diagonal 4981925 w/ two 9 ft windows). S doors = Single-Glass 36x80 at 20.5 (hinge W) + pair 46.7-52.7 (hinges outer), all swing out; air curtain 28 = 4981953. All door swings/hinges + toilets set per pdf (dev_scripts/facing.py). Added: stub wall 4981977 (29.4, 22.9-26.3), 2 electrical panels, 5 floor drains/sinks. **Dimensions in view read like the pdf**: 52-7, 49-3, 30-1, 28-10, 33-1, 30-7 (centerline refs via dev_scripts/dims.py / dims_rp.py / dim_diag.py) + counter 3 & 14, kitchen counter 2-1. Model saved (REV-1). Real view export: `progress/views/proposed-floor-plan.png`.
- 2026-08-18 01:20 — verification pass vs pdf: overlay `progress/model-vs-pdf-overlay.png` (model drawn over the pdf at
  the same scale) — perimeter, patio, kitchen/alcove walls, restroom block, cooler, doors and equipment coincide; restroom
  fixtures repositioned; tag audit 35/35 correct; wall centerlines = printed dims (52-7, 49-3, 30-1, 28-10, 33-1, 30-7).
  Model SAVED via new `POST /save` (REV-1.rvt). Dimension annotations were NOT added: the /dimensions verb measures faces
  (reads 30-4 / 28-4) — needs a centerline-reference option to print the pdf numbers.
- 2026-08-18 00:55 — model file is now **Pho Hung El cajon REV-1.rvt** (Dropbox/2026/Pho Hung El Cajon); routes server on Revit PID 8720.
  S storefront doors re-gridded to exact plan positions (single 19.2-21.8, double 46.8-52.4), air curtain 28 over it,
  locker 11 rotated into alcove, stray N exit door removed. Rendered check: `progress/model-plan.png` (tools/render-plan.ps1).
  Verbs added: /views, /open-view {name}. "Proposed Floor Plan" = view id 718579 (Project Browser > Floor Plans).
- **2026-08-18 layout matched to the EQUIPMENT PLAN pdf** (see `layout-walls.json` for every id/coordinate):
  W wall straightened to x=6.3 (storefront 25.9-49.25 w/ entry door 04 at y 41.3), kitchen S wall moved to
  y=15.8 + freezer alcove (x 56.5-63.6, y 7.9-15.8), janitor/restroom block rebuilt (x 25.3-34.75; women 40.7-52.4,
  men 52.4-diag; janitor S at 30.08), roof-access/elec rooms top y=11.2 + 2nd door, cooler 42.4-56.1 x 16.5-23 + door,
  PATIO low walls (x 6.55-24.9, y 0 to -24) + room 399 SF, cashier counter 3x13.5 at x 20.1-23.1, kitchen counter,
  all 29 items repositioned per plan (bboxes recorded), 3 stranded hand/mop sinks re-hosted, tags redone (35), rooms
  renamed to plan names, separation lines rebuilt. New verbs: move (dx/dy/to/rotate/flip), wall-move, curtain-grid,
  curtain-door panel_id, docs/close-doc; `tools/render-plan.ps1` renders the model to PNG for comparison.
- Project open in Revit: **Pho Hung El cajon** (Revit 2025.4.2, pyRevit 6.4, routes :48884 OK)
- Rough draft of the El Cajon plan built via `onetake-v1` verbs on level `1st Floor Level`
  (walls 10 ft; geometry in `revit/layout-walls.json`, sketch `revit/layout-sketch.svg`)
- **Equipment schedule:** view `EQUIPMENT SCHEDULE (E) - PHO HUNG` (id 4980444) — cloned from the project's
  `EQUIPMENT SCHEDULE` (3965108) so it has the SAME 11 columns (ITEM, Count, DESCRIPTION(s), MFG, MODEL,
  ELECTRICAL, WATER, WASTE, TOTAL BTU, GAS SIZE, REMARKS) + hidden Comments=EXISTING filter; 29 items 01–29.
  Data lives on instance params (Item, Description(s), MFG, MODEL, REMARKS…) of the 35 elements.
  Old 6-column version (4980435) deleted.
- **Floor plan labels:** all 35 items tagged 01–29 in `Proposed Floor Plan` (Type-Mark tags: OneTake
  Specialty Equipment/Furniture/Casework/Mechanical Equipment Tag + stock Plumbing Fixture Tag).
  Live export: `progress/schedule-latest.csv`. Re-read any time with
  `POST /onetake-v1/schedule-read {"name":"EQUIPMENT SCHEDULE (E) - PHO HUNG"}`
- Verb layer `OneTake.extension/startup.py` has 19 routes: status, doc, levels, walls GET/POST,
  delete, families, load-family, place, room-lines, rooms GET/POST, dimensions, room-tags,
  curtain-door, set-params, schedule, schedule-read, warnings

## Next up
- [ ] Review the El Cajon rough draft in Revit; fix anything off, then re-checkpoint
- [ ] Equipment schedule: fill ELECTRICAL / GAS SIZE / BTU cells that were unknown (only description-derived values set); add (N) items if scope needs
- [ ] Place (E) schedule on sheet A09 next to the source if wanted
- [ ] Dimension strings: add centerline-reference support to /dimensions so 52-7 / 49-3 / 30-1 / 28-10 / 33-1 / 30-7 / 3 / 14 / 10 / 2-6 print like the pdf
- [ ] Hood families 05/13 draw oversize (12x4 / 7x4 needed); wok range family is a 6-burner (plan 108x42)
- [ ] SETUP.md smoke-test hard-codes `"Level 1"` — default to lowest level or document
- [ ] Try revit-mcp-server on a real project; list what's missing vs our verbs
- [ ] First real layout: program → solver → verbs pipeline

## Blockers
- (none)

## Session notes (newest first)
- 2026-08-20 20:13:15 - d reconcile it with what we actually built — correct anything stale.
- 2026-08-20 20:13:14 - -vault/Revit Project - Workflow Rules.md (I just pushed it)
- 2026-08-20 20:13:09 - ever a single element — one call, one transaction.
- 2026-08-20 20:13:06 - tinuing. Never chain three geometry ops without looking.
- 2026-08-20 20:13:03 - Y geometry change: call /export-view and actually READ the PNG to
- 2026-08-20 20:13:02 -  instead of reading startup.py.
- 2026-08-20 20:12:53 -  update CLAUDE.md's Workflow section with these rules:
- 2026-08-20 20:12:53 - do-able group, and use it in the multi-element verbs.
- 2026-08-20 20:12:52 - saction-group helper so multi-step operations commit as one
- 2026-08-20 20:12:50 -  never drift out of date.
- 2026-08-20 20:12:48 - d its docstring. Introspect the api object rather than hardcoding a list,
- 2026-08-20 20:12:47 - etake-v1/verbs — returns every registered route: path, method,
- 2026-08-20 20:12:41 - ts, both via dev_scripts first, then promote together in ONE reload:
- 2026-08-18 — Windows instead of curtain walls; door/toilet facings; pdf dimensions; panels/drains — all via dev_scripts (no reloads).
- 2026-08-18 — Added /dev/run (dev_scripts/ runner, no-reload dev loop), /export-view, /save, /views, /open-view.
  RULE: new Revit code goes in dev_scripts/ first; batch promotions to startup.py.
- 2026-08-18 — Finished storefront doors + render check on REV-1; Revit relaunched by Claude on REV-1.
- 2026-08-18 — Layout matched to pdf (walls, patio, equipment positions, rooms). Revit got licence-paused at the very end; storefront door re-grid + render check pending.
- 2026-08-17 — (E) schedule rebuilt to match project EQUIPMENT SCHEDULE columns (id 4980444); 35 elements
  tagged 01–29 on Proposed Floor Plan; new verbs schedules, schedule-clone, element-info, tags,
  tag-family-from, docs, close-doc; `delta` command installed (resume Claude + progress terminal).
- 2026-08-17 — Progress system added: `tools/checkpoint.ps1`, `tools/progress-terminal.ps1`
  (double-click `tools/Progress-Terminal.cmd`; self-restarting; `install-autostart.ps1` for logon),
  Claude Code hooks (session start prints this file; every turn end saves a checkpoint).
  Located the equipment schedule (view id 4980435, 29 rows).

## How to resume (any machine)
1. `git pull` on branch `claude/trusting-thompson-232391`
2. Open Revit 2025 → the Pho Hung project (keep ONE Revit instance open)
3. Double-click `revit/tools/Progress-Terminal.cmd` (live status + auto-save), or run
   `powershell -File revit/tools/checkpoint.ps1`
4. Start Claude Code in `revit/` — the session-start hook prints this file
