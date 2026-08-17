# Setup — Claude drives Revit 2025 (Windows machine)

Do these in order on the machine with Revit 2025. ~30 minutes.

## 1. Install pyRevit
1. Download the latest installer from https://github.com/pyrevitlabs/pyRevit/releases
   (the `pyRevit_x.x.x_signed.exe` asset).
2. Run it, start Revit 2025 — you should see a **pyRevit** tab in the ribbon.
3. pyRevit tab → **Settings**:
   - Engine: **IronPython 2.7.7** (NOT 3.4 — routes server is broken on 3.4)
   - **Routes** section: enable the routes server. Default port **48884**.
4. Note your exact Revit build (Help → About) somewhere. Don't auto-update Revit.

## 2. Install this extension
1. Get this repo onto the machine:
   `git clone https://github.com/jubie2/onetake-hq && cd onetake-hq && git checkout claude/trusting-thompson-232391`
2. pyRevit tab → Settings → **Custom Extension Directories** → add the
   `onetake-hq/revit` folder (the folder that CONTAINS `OneTake.extension`).
3. **Reload pyRevit** (pyRevit tab → Reload). Routes register at startup —
   after every edit to `startup.py`, reload again.

## 3. Smoke test
Open any project (or a new empty one) in Revit, then in a terminal:

```
curl http://localhost:48884/onetake-v1/status
curl http://localhost:48884/onetake-v1/doc
```

First command should return Revit/pyRevit versions. Second lists levels and
wall types. Then the real test — a closed 30x20 ft room outline:

```
curl -X POST http://localhost:48884/onetake-v1/walls -H "Content-Type: application/json" -d "{\"points\": [[0,0],[30,0],[30,20],[0,20]], \"closed\": true, \"level\": \"Level 1\", \"height_ft\": 10}"
```

Four walls should appear in the model. Ctrl+Z undoes them (each verb is one
transaction).

## 4. Install Claude Code locally
1. Install from https://claude.com/claude-code (Windows installer or VS Code extension).
2. Open a terminal in the `onetake-hq/revit` folder and run `claude` —
   it reads `CLAUDE.md` automatically and starts with the project facts loaded.
3. First prompt to try:
   *"Read the injector file on my desktop at <path>, tell me what it does,
   and what from it is worth keeping over the routes verbs in this repo."*

## 5. Optional: revit-mcp-server (48 ready-made verbs)
https://github.com/Demolinator/revit-mcp-server — same architecture
(pyRevit routes + external MCP), already covering create/query/modify/analyze.
Read its README, wire it into local Claude Code as an MCP server. Use it on a
real project first; whatever it can't do is what we build next in this extension.

## When something fails
- `curl` refuses connection → routes server not enabled, or Revit not running,
  or pyRevit didn't load (check pyRevit tab exists).
- Empty response → you're on the IronPython 3.4 engine; switch to 2.7.7.
- JSON error from a verb → that's by design; paste it to Claude verbatim.
