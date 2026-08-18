# Revit / OneTake — PROGRESS (read this first)

<!-- auto --> **Last checkpoint:** 2026-08-18 01:33:04 | Revit: up, 'Pho Hung El cajon REV-1', 309 walls, schedule 29 rows | git claude/trusting-thompson-232391@3e69d88, 6 uncommitted

This file is the single "where did we leave off" note. The header line above is
rewritten by `tools/checkpoint.ps1`; the sections below are edited by hand (or by
Claude at the end of a session). Machine snapshot lives next to it in
`state.json`, the equipment schedule export in `schedule-latest.csv`, and the
append-only history in `log.md`.

## Where we left off
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
