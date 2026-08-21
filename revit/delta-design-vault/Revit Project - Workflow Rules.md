# Revit Project — Workflow Rules

How to get accurate, fast results. Read before starting a work session.

## The dev loop (avoid reloads)
- **Never** edit `startup.py` to try something out. Editing it costs a
  pyRevit reload = 1–3 minutes of dead time.
- Develop in `dev_scripts/*.py`, run it with `POST /onetake-v1/dev/run`.
  Runs instantly inside the live Revit session. Iterate as many times as needed.
- Only **promote** proven code into `startup.py` as a permanent verb, and
  **batch promotions** — one reload for several finished verbs.

## Batching
- Every verb takes a **list**, never a single element. 35 tags = 1 call with
  35 ids in 1 transaction, not 35 calls.
- Reason: each call waits for Revit to be idle. The wait, not the work,
  is the cost.

## Accuracy: close the visual loop
- Revit work is visual; text responses can't confirm it looks right.
- Use the `/screenshot` verb (export current view to PNG) after any
  geometry change, then LOOK at the image before continuing.
- Rule: **create → screenshot → verify → continue.** Never chain three
  geometry operations without looking.

## Accuracy: never guess the model
- Always `GET /doc` (levels, wall types) before creating anything.
- Use `GET /verbs` to see available endpoints + parameters. Don't guess
  endpoint names or parameter spellings.
- Dimensions come from the drawing's printed numbers, not from measuring
  pixels. Cross-check against stated room areas.

## Safety
- Wrap multi-step operations in a **transaction group** so the whole
  operation is one Ctrl+Z, not 35.
- Ask for a **dry run** (report what would change) before large or
  destructive changes.
- Save the Revit file before letting a big batch run.

## Keeping Revit responsive
- Close schedule views / extra windows not in use (an active view can't be
  modified or deleted — this caused a failure once).
- Don't click around in Revit while a batch runs; routes wait for idle.
- Server silent >5 min = probably a **modal dialog open in Revit**. Go look.
- Only one Revit instance, or they fight over port 48884.

## Prompt template (use this shape every time)
```
GOAL: <one sentence, the end state>
CONTEXT: read CLAUDE.md + Status note first
CONSTRAINTS: <units, which level, what not to touch>
METHOD: use dev_scripts + /dev/run; batch into single calls
VERIFY: screenshot the view and show me before saying it's done
STOP IF: <the condition where you should ask instead of guessing>
```

## Session hygiene
- Start: "read CLAUDE.md and Revit Project - Status.md, then continue."
- End: "update the Status note and push to GitHub."
- Push after every working session — the machine is not the backup.
