# Revit Project — Status

*Last updated: 2026-08-17 (local Claude session on Revit machine — setup steps 1–3 done, ALL SMOKE TESTS PASS)*

## Done
- [x] 2026-08-17 local: pyRevit already installed — **pyRevit 6.4.0** at
      `%APPDATA%\pyRevit-Master`, attached to Revit 2025 with engine
      **DEFAULT = IronPython 2.7.12** (`IPY2712PR`; pyRevit 6.x has no
      separate 2.7.7 build — this IS the IronPython 2 engine; IPY342 not used)
- [x] 2026-08-17 local: routes enabled via CLI (`pyrevit configs routes enable`,
      `pyrevit configs routes port 48884`) → `pyRevit_config.ini` `[routes]
      enabled=true, port=48884`
- [x] 2026-08-17 local: extension path registered
      (`pyrevit extensions paths add C:\dev\onetake-hq\revit`)
- [x] 2026-08-17 local: Revit build recorded — **Revit 2025.4.2, build
      20250515_1515(x64)**, version 25.4.20.11 (do not auto-update)
- [x] 2026-08-17 local: vault notes copied into `Delta Design` vault root
      (`C:\Users\francis nguyen\OneDrive\Documents\Delta Design`)
- [x] Decided architecture: typed verb layer over pyRevit routes (not raw
      code injection)
- [x] Verified version facts: Revit 2025 / .NET 8 / pyRevit supported /
      IronPython 2.7.7 required
- [x] Built starter kit in repo `onetake-hq`, folder `revit/`:
      CLAUDE.md, SETUP.md, OneTake.extension/startup.py, HANDOFF.md
- [x] Pushed to branch `claude/trusting-thompson-232391`
- [x] Fixed GitHub app write permission (was read-only)
- [x] Created "delta design" Obsidian vault
- [x] 2026-08-17 local: **bug fixed in `startup.py`** — it imported
      `pyrevit.__version__`, which doesn't exist in pyRevit 6.4 → ImportError
      → no routes registered (`RouteHandlerNotDefinedException` on every
      verb; runtime log: "Startup script returned non-zero result ... OneTake").
      Now uses `versionmgr.get_pyrevit_version().get_formatted()`.
      *(Fix is in the working tree, NOT yet committed/pushed.)*
- [x] 2026-08-17 local: enabled routes **coreapi** so pyRevit can be reloaded
      by `curl -X POST http://localhost:48884/pyrevit-core/sessions/`
- [x] 2026-08-17 local: **SMOKE TESTS PASS** (Revit 2025.4.2, real project
      "Pho Hung El cajon" open):
      - `GET /onetake-v1/status` → 200 `{"ok":true,"revit_version":"2025",
        "revit_build":"20250515_1515(x64)","pyrevit_version":"6.4.0.26100+0515"}`
      - `GET /onetake-v1/doc` → 200, 7 levels + 17 wall types listed
      - `POST /onetake-v1/walls` with `"level":"Level 1"` → clean 404 JSON
        (that project has no "Level 1" — error path works as designed)
      - `POST /onetake-v1/walls` 30×20 closed on `"1st Floor Level"`, 10 ft →
        200, `wall_ids 4977585–4977588`, count 4 (Ctrl+Z to remove them)
- [x] Install Claude Code locally on the Revit machine (step 4) — done, it
      ran this session

- [x] 2026-08-17 local: `startup.py` fix committed + pushed (`2484df4`) —
      needed a repo-local git identity (`jubie2 <johnson7848@gmail.com>`) and
      a one-time GCM browser sign-in (session shell sets
      `GCM_INTERACTIVE=never`; override with `$env:GCM_INTERACTIVE="always"`)
- [x] 2026-08-17 local: added verb **`POST /onetake-v1/delete`**
      `{"ids":[...]}` (one transaction, returns deleted/not_found); reloaded
      pyRevit via `POST /pyrevit-core/sessions/` (works from curl);
      deleted the 4 test walls (`deleted_ids 4977585–4977588`) — model clean

## In progress
- [ ] Commit + push the `/delete` verb (working tree)
- [ ] Two Revit 2025 processes were open with the same project (PIDs 35736 /
      35760); only 35760 owns port 48884. First `/delete` call hung ~2 min
      (server blocked until Revit went idle) then cleared — keep ONE Revit
      instance open when driving via routes

## Next up
- [ ] SETUP.md smoke-test command hard-codes `"Level 1"` — note that real
      projects need the level name from `/doc`, or let the verb default to
      the lowest level
- [ ] Point local Claude at the old injector file on the desktop — keep
      anything useful, retire the rest
- [ ] Try revit-mcp-server on a real project of Dad's; list what's missing
- [ ] First real layout: program → solver → verbs pipeline

## Blockers
- (none currently)

## Notes for future sessions
- pyRevit 6.4's IronPython 2 engine is 2.7.**12**, not 2.7.7 — same Python 2
  rules apply; the "2.7.7" in older notes means "the IronPython 2 engine".
- Startup-script tracebacks go to the in-Revit pyRevit output window; the file
  `%APPDATA%\pyRevit\2025\pyRevit_2025_<PID>_runtime.log` only says
  "non-zero result". Check imports against
  `%APPDATA%\pyRevit-Master\pyrevitlib\pyrevit` when a verb 500s with
  `RouteHandlerNotDefinedException`.

## Decisions log
- 2026-08-17: Stay on Claude (vs Codex) — model isn't the bottleneck;
  Revit access + API knowledge gap are
- 2026-08-17: Local Claude Code on the Revit machine is the primary driver;
  cloud sessions for planning/review
- 2026-08-17: Keep Revit work in onetake-hq repo (Jubie doesn't use it for
  anything else)
