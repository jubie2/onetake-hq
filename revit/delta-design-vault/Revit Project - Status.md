# Revit Project — Status

*Last updated: 2026-08-17 (cloud Claude session — starter kit built)*

## Done
- [x] Decided architecture: typed verb layer over pyRevit routes (not raw
      code injection)
- [x] Verified version facts: Revit 2025 / .NET 8 / pyRevit supported /
      IronPython 2.7.7 required
- [x] Built starter kit in repo `onetake-hq`, folder `revit/`:
      CLAUDE.md, SETUP.md, OneTake.extension/startup.py, HANDOFF.md
- [x] Pushed to branch `claude/trusting-thompson-232391`
- [x] Fixed GitHub app write permission (was read-only)
- [x] Created "delta design" Obsidian vault

## In progress
- [ ] Install Claude Code locally on the Revit machine (Jubie, step 4)
- [ ] Local Claude runs SETUP.md steps 1–3 (pyRevit install, config,
      smoke tests) — see HANDOFF.md for the exact prompt

## Next up
- [ ] Smoke test passes: 30×20 ft room of walls drawn via curl
- [ ] Point local Claude at the old injector file on the desktop — keep
      anything useful, retire the rest
- [ ] Try revit-mcp-server on a real project of Dad's; list what's missing
- [ ] First real layout: program → solver → verbs pipeline

## Blockers
- (none currently)

## Decisions log
- 2026-08-17: Stay on Claude (vs Codex) — model isn't the bottleneck;
  Revit access + API knowledge gap are
- 2026-08-17: Local Claude Code on the Revit machine is the primary driver;
  cloud sessions for planning/review
- 2026-08-17: Keep Revit work in onetake-hq repo (Jubie doesn't use it for
  anything else)
