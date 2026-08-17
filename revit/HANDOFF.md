# Handoff — paste this to local Claude Code as your first message

> Read revit/CLAUDE.md and revit/SETUP.md in this repo first. Then do
> SETUP.md steps 1–3 for me, hands-on:
>
> 1. Install pyRevit — try `winget install pyRevit.pyRevit` (or
>    `pyrevit-cli` + `pyrevit attach`); fall back to downloading the latest
>    signed installer from github.com/pyrevitlabs/pyRevit/releases and
>    running it. Verify with `pyrevit env` if the CLI is available.
> 2. Configure it: IronPython 2.7.7 engine, routes server enabled
>    (port 48884). Prefer editing pyRevit's config via CLI
>    (`pyrevit configs`) over telling me to click through settings; only
>    ask me to click when there is no CLI path.
> 3. Register the extension: add this repo's `revit` folder to pyRevit's
>    extension search paths, then tell me to start Revit 2025 and open any
>    project. When I say it's open, run the smoke tests from SETUP.md
>    (curl /status, /doc, then the 30x20 walls test) and show me the results.
>
> Also: I have an Obsidian vault called "delta design". Find it on this
> machine (search common locations: iCloud Drive Obsidian folder, Documents,
> and Obsidian's config at %APPDATA%/obsidian/obsidian.json which lists
> vault paths). Copy the notes from revit/delta-design-vault/ in this repo
> into the vault root, keeping their filenames. Then update
> "Revit Project - Status.md" with what you actually did and what's left.
>
> Rules: don't update Revit itself, don't switch pyRevit to the IronPython
> 3.4 engine, and if a smoke test fails, show me the raw error and your fix
> before re-running.
