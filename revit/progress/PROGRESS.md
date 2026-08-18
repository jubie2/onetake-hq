# Revit / OneTake — PROGRESS (read this first)

<!-- auto --> **Last checkpoint:** 2026-08-17 22:09:53 | Revit: up, 'Pho Hung El cajon', 305 walls, schedule 32 rows | git claude/trusting-thompson-232391@335ede6, 7 uncommitted

This file is the single "where did we leave off" note. The header line above is
rewritten by `tools/checkpoint.ps1`; the sections below are edited by hand (or by
Claude at the end of a session). Machine snapshot lives next to it in
`state.json`, the equipment schedule export in `schedule-latest.csv`, and the
append-only history in `log.md`.

## Where we left off
- Project open in Revit: **Pho Hung El cajon** (Revit 2025.4.2, pyRevit 6.4, routes :48884 OK)
- Rough draft of the El Cajon plan built via `onetake-v1` verbs on level `1st Floor Level`
  (walls 10 ft; geometry in `revit/layout-walls.json`, sketch `revit/layout-sketch.svg`)
- **Equipment schedule created:** view `EQUIPMENT SCHEDULE (E) - PHO HUNG` (id 4980435),
  29 items 01–29, all STATUS=EXISTING; columns ITEM / DESCRIPTION / QTY / MANUFACTURER / MODEL / STATUS.
  Live export: `progress/schedule-latest.csv`. Re-read any time with
  `POST /onetake-v1/schedule-read {"name":"EQUIPMENT SCHEDULE (E) - PHO HUNG"}`
- Verb layer `OneTake.extension/startup.py` has 19 routes: status, doc, levels, walls GET/POST,
  delete, families, load-family, place, room-lines, rooms GET/POST, dimensions, room-tags,
  curtain-door, set-params, schedule, schedule-read, warnings

## Next up
- [ ] Review the El Cajon rough draft in Revit; fix anything off, then re-checkpoint
- [ ] Equipment schedule: add (N) items if scope includes new equipment; add PLUMBING/ELEC columns if needed
- [ ] SETUP.md smoke-test hard-codes `"Level 1"` — default to lowest level or document
- [ ] Try revit-mcp-server on a real project; list what's missing vs our verbs
- [ ] First real layout: program → solver → verbs pipeline

## Blockers
- (none)

## Session notes (newest first)
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
