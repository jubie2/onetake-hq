# Revit Project — Gotchas (hard-won, don't re-learn)

- **Dad's setup:** Revit 2025, Windows, .NET 8. Record the exact build number.
  **Don't auto-update Revit** — Autodesk is moving 2025/2026 to .NET 10 and a
  point update can break pyRevit.
- **Python inside Revit is IronPython 2.7.7 = Python 2 syntax.** No f-strings,
  `print` is a statement. External scripts are normal Python 3 — only
  in-Revit code is Python 2.
- **Never use the IronPython 3.4 engine** — the routes server silently breaks
  on it (empty responses). This looks like a network problem; it isn't.
- **Revit's internal units are decimal feet, always.** mm → ft is `mm / 304.8`.
  Wrong units = silently wrong geometry, the #1 bug.
- **Every model change needs a Transaction** and must run on Revit's main
  thread. Routes handlers are safe (pyRevit marshals them); raw sockets are not.
- Walls need an existing Level + WallType; family symbols must be **activated**
  before placing instances.
- After editing `startup.py`: **reload pyRevit** (pyRevit tab → Reload).
  Routes only register at startup.
- Routes server: port **48884**, API root `onetake-v1`.
  Alive check: `curl http://localhost:48884/onetake-v1/status`
- Each verb = one transaction = one Ctrl+Z in Revit. Safe to experiment.
- When unsure about an API call, check **revitapidocs.com/2025** — signatures
  change between Revit versions and AI memory of them is unreliable.
