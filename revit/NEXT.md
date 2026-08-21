# NEXT — current task for local Claude

Do both changes in `dev_scripts/` first, then promote them together in ONE reload.

## 1. Verb catalog
Add `GET /onetake-v1/verbs` — returns every registered route: path, method, and
its docstring. Introspect the `api` object rather than hardcoding a list, so it
can never drift out of date.

## 2. Transaction groups
Add a transaction-group helper so a multi-step operation commits as one
undo-able group, and use it in the multi-element verbs.

## 3. Update CLAUDE.md — Workflow section
Add these rules:
- Call `GET /verbs` at the start of a session instead of reading `startup.py`.
- After ANY geometry change: call `/export-view` and actually READ the PNG to
  verify before continuing. Never chain three geometry operations without looking.
- Every verb takes a list, never a single element — one call, one transaction.

## 4. Reconcile the vault notes
Read `delta-design-vault/Revit Project - Workflow Rules.md` and correct anything
stale against what we actually built (e.g. it may describe things as missing that
already exist).

## 5. Finish
Commit and push. Update `progress/PROGRESS.md` and
`delta-design-vault/Revit Project - Status.md`.
