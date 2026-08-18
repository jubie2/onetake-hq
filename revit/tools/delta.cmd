@echo off
rem ============================================================
rem  delta  - pick up exactly where we left off (type it like "claude")
rem
rem    delta            resume the last Claude Code session in revit\
rem                     (starts the progress terminal too if it's not up)
rem    delta new        start a fresh Claude Code session (still shows PROGRESS.md)
rem    delta term       just (re)open the live progress terminal
rem    delta status     save a checkpoint and print where we left off
rem    delta open       open PROGRESS.md in your editor
rem ============================================================
setlocal
set "REVIT_DIR=C:\dev\onetake-hq\revit"
set "TOOLS=%REVIT_DIR%\tools"
set "CMD=%~1"
if "%CMD%"=="" set "CMD=resume"

if /i "%CMD%"=="term"   goto term
if /i "%CMD%"=="status" goto status
if /i "%CMD%"=="open"   goto open
if /i "%CMD%"=="new"    goto new
if /i "%CMD%"=="resume" goto resume
if /i "%CMD%"=="help"   goto help
goto help

:term
call :ensure_terminal
goto :eof

:status
powershell -NoProfile -ExecutionPolicy Bypass -File "%TOOLS%\checkpoint.ps1"
powershell -NoProfile -ExecutionPolicy Bypass -Command "[Console]::OutputEncoding=[Text.Encoding]::UTF8; Get-Content -Encoding UTF8 -Raw '%REVIT_DIR%\progress\PROGRESS.md'"
goto :eof

:open
start "" "%REVIT_DIR%\progress\PROGRESS.md"
goto :eof

:new
call :ensure_terminal
cd /d "%REVIT_DIR%"
claude %2 %3 %4 %5 %6 %7 %8 %9
goto :eof

:resume
call :ensure_terminal
cd /d "%REVIT_DIR%"
echo [delta] resuming last Claude Code session in %REVIT_DIR% ...
claude --continue %2 %3 %4 %5 %6 %7 %8 %9
if errorlevel 1 (
  echo [delta] no previous session to continue - starting a new one
  claude %2 %3 %4 %5 %6 %7 %8 %9
)
goto :eof

:ensure_terminal
rem start the self-restarting progress terminal only if it is not already running
powershell -NoProfile -ExecutionPolicy Bypass -Command "$f='%REVIT_DIR%\progress\terminal.pid'; if (Test-Path $f) { if (Get-Process -Id ([int](Get-Content $f)) -ErrorAction SilentlyContinue) { exit 0 } }; exit 1"
if errorlevel 1 (
  echo [delta] starting progress terminal...
  start "OneTake progress" /d "%TOOLS%" "%TOOLS%\Progress-Terminal.cmd"
) else (
  echo [delta] progress terminal already running
)
exit /b 0

:help
echo delta            resume last Claude Code session (revit\) + progress terminal
echo delta new        fresh Claude Code session
echo delta term       (re)open the live progress terminal
echo delta status     save checkpoint + print PROGRESS.md
echo delta open       open PROGRESS.md
goto :eof
