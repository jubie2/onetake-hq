# dev_scripts — develop Revit verbs WITHOUT reloading pyRevit

`POST /onetake-v1/dev/run {"file": "name.py", "args": {...}}` execfile()s the script with
`doc`, `uidoc`, `uiapp`, `args`, `result` as globals and returns `result` (or the full traceback).

Workflow: write/edit a script here → run it via /dev/run → iterate → once proven, promote it
into `startup.py` as a permanent verb, batching several promotions per reload.
Rules: IronPython 2.7 syntax; every model change inside a Transaction (`_prep(t)` before `t.Start()`);
units are decimal feet.
