@echo off
rem Double-click launcher for the live progress terminal.
rem Supervisor loop: if the PowerShell process ever exits for any reason other
rem than the user pressing [q] (exit code 0), it restarts after 3 seconds.
title OneTake Revit - progress terminal (supervisor)
:loop
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0progress-terminal.ps1" %*
if "%ERRORLEVEL%"=="0" goto end
echo.
echo [supervisor] terminal exited with code %ERRORLEVEL% - restarting in 3s (Ctrl+C twice to stop)
timeout /t 3 /nobreak >nul
goto loop
:end
echo [supervisor] clean exit.
