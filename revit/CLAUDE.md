# Revit Automation — Project Facts (READ FIRST)

Hard-won constraints for this project. Do not re-derive these; they are verified.

## Environment
- **Revit 2025** on Windows, .NET 8 runtime.
- **pyRevit** latest release; loader targets `net8.0-windows` for Revit 2025–2026.
- Autodesk plans to migrate Revit 2025/2026 to .NET 10 (before Nov 2026, when
  .NET 8 support ends). **Do not auto-update Revit mid-project** — a point
  release that swaps the runtime can break pyRevit attachment (pyRevit maps
  runtime by Revit *year*, not build). Record the exact Revit build before updating.

## Python engine — CRITICAL
- Scripts inside Revit run on **IronPython 2.7.7**. That is **Python 2 syntax**:
  - `print` is a statement, NOT a function
  - **No f-strings.** Use `.format()` or `%`
  - No `pathlib`, limited stdlib; `unicode` vs `str` exists
- Do NOT switch to the IronPython 3.4 engine: the pyRevit **routes server is
  broken on IPy 3.4** (requests return ERR_EMPTY_RESPONSE). Stay on 2.7.7.
- CPython is not fully supported inside pyRevit. External tooling (MCP server,
  test clients) is normal Python 3 — only in-Revit code is IronPython 2.7.

## Revit API rules
- **Internal units are DECIMAL FEET. Always.** Millimeter/meter inputs must be
  converted (`mm / 304.8`). This is the #1 source of silent wrong-geometry bugs.
- **Every model change needs a `Transaction`** (`t.Start()` … `t.Commit()`),
  and must run in a valid API context on Revit's main thread. Never call the
  API from a raw socket callback or background thread — pyRevit routes handlers
  are safe because pyRevit marshals them via ExternalEvent.
- Element creation preconditions that generated code always forgets:
  - Walls need an existing **Level** (ElementId) and a **WallType** present in the doc
  - Placing family instances requires the **FamilySymbol to be activated**
    (`symbol.Activate()` inside a transaction) if not already
- API signatures change between Revit versions. When unsure, check the Revit
  **2025** API docs (revitapidocs.com/2025), not memory.

## Architecture
- **Typed verb layer over pyRevit routes** — Claude calls hand-verified HTTP
  verbs; it does not generate raw Revit API code. Raw-code exec is a last-resort
  escape hatch only.
- Routes server: runs inside Revit, default port **48884**. Our API root: `onetake-v1`.
  Smoke test: `curl http://localhost:48884/onetake-v1/status`
- Layout generation pattern: LLM produces the *program* (room list, areas,
  adjacencies); deterministic code solves it into coordinates; solved geometry
  goes through the verbs. LLMs must not invent raw coordinates.
- `revit-mcp-server` (github.com/Demolinator/revit-mcp-server) provides 48
  ready verbs on this same architecture — prefer extending over duplicating.

## Workflow
- **Develop new Revit functionality in `OneTake.extension/dev_scripts/` and run it via
  `POST /onetake-v1/dev/run {"file":"x.py"}` (no reload; returns full traceback). Promote proven
  code into `startup.py` as verbs in batches — reload once per several verbs, not per verb.
- Before reloading: `powershell -File tools/check-startup.ps1` (syntax check; a bad reload kills ALL routes).
- Edit `startup.py` → **reload pyRevit** (routes are registered at startup;
  a plain script re-run does not re-register them) → curl the endpoint.
- Return errors as JSON from handlers so the calling agent can read them.

## Progress / resume (READ `progress/PROGRESS.md` FIRST)
- `progress/PROGRESS.md` = where we left off + next steps. Update its
  "Where we left off" / "Next up" / "Session notes" sections at the end of a session.
- `tools/checkpoint.ps1` snapshots Revit + git + the equipment schedule into
  `progress/` (`state.json`, `schedule-latest.csv`, `log.md`); `-Commit` also
  git-commits/pushes. A Stop hook runs it after every Claude turn.
- `tools/Progress-Terminal.cmd` = live, self-restarting terminal (auto-saves on
  change / every 10 min); `tools/install-autostart.ps1` puts it in the Startup folder.
- Equipment schedule for Pho Hung: Revit view `EQUIPMENT SCHEDULE (E) - PHO HUNG` (id 4980444).
