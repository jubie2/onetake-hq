# Revit Project — Overview

**What this is:** Claude drives Revit 2025 to help Dad with floorplans and
layouts. Jubie prompts; AI does the heavy lifting.

**How it works (one paragraph):** A small web server runs *inside* Revit
(via pyRevit "routes"). Claude sends it simple commands over HTTP —
"list the levels", "draw walls along these points" — and the server does the
actual Revit work safely. Claude never writes raw Revit code directly; it
calls a menu of pre-tested commands ("verbs"). Bugs get fixed once in the
verb, not over and over in generated scripts.

**Where everything lives:**
- Repo: `github.com/jubie2/onetake-hq`, branch `claude/trusting-thompson-232391`, folder `revit/`
- `revit/CLAUDE.md` — cheat-sheet of Revit gotchas (auto-loaded by Claude Code)
- `revit/SETUP.md` — install checklist for the Revit machine
- `revit/OneTake.extension/startup.py` — the in-Revit server + first verbs
- `revit/HANDOFF.md` — the first prompt to give local Claude Code

**The layout plan (why this beats "AI draws a floorplan"):** LLMs are bad at
inventing coordinates (overlapping rooms, walls that don't close). So: Claude
produces the *program* — room list, sizes, which rooms touch which — and
regular deterministic code turns that into clean rectangles. The solved
geometry then goes into Revit through the verbs. AI does judgment; math does
geometry.

**Ready-made shortcut:** `revit-mcp-server`
(github.com/Demolinator/revit-mcp-server) already has 48 commands on this
same architecture. Plan: use it on a real project, note what's missing,
build only the missing parts.
