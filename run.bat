@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
title DePalencify

rem --- auto-update from GitHub (only if this folder is a git clone) ---------
if not exist ".git" goto :after_update
if defined DEPALENCIFY_UPDATED goto :after_update
where git >nul 2>&1
if errorlevel 1 goto :after_update
echo Checking for updates...
git fetch --quiet >nul 2>&1
if errorlevel 1 (
    echo (No connection, skipping update check.)
    goto :after_update
)
set "BEHIND=0"
for /f %%i in ('git rev-list --count HEAD..@{u} 2^>nul') do set "BEHIND=%%i"
if "%BEHIND%"=="0" goto :after_update
echo Update found. Installing...
git pull --ff-only --quiet
if errorlevel 1 (
    echo (Could not update, probably because files were edited here. Running the current version.)
    goto :after_update
)
echo Updated. Restarting...
set "DEPALENCIFY_UPDATED=1"
(goto) 2>nul & "%~f0"
:after_update

rem --- desktop and Start menu icon (created once, and again if this folder is moved) ---
set "SEEN="
if exist ".shortcut_made" set /p SEEN=<".shortcut_made"
if not "%SEEN%"=="%CD%" if exist "launchers\make_shortcut.ps1" powershell -NoProfile -ExecutionPolicy Bypass -File "launchers\make_shortcut.ps1" "%CD%"

rem --- find Python -------------------------------------------------------
set "PY="
py -3 --version >nul 2>&1 && set "PY=py -3"
if not defined PY (
    python --version >nul 2>&1 && set "PY=python"
)
if not defined PY (
    echo Python 3 was not found. Please install it from https://www.python.org/downloads/
    echo and tick "Add Python to PATH" during the installation, then run this again.
    pause
    exit /b 1
)

rem --- first run: create a private environment and install what is needed ---
if not exist ".venv\Scripts\python.exe" (
    echo First run: setting things up. This takes a minute or two and needs internet.
    %PY% -m venv .venv
    if errorlevel 1 goto :setup_failed
    ".venv\Scripts\python.exe" -m pip install --quiet --upgrade pip
    ".venv\Scripts\python.exe" -m pip install --quiet numpy pandas scipy matplotlib xlsxwriter openpyxl
    if errorlevel 1 goto :setup_failed
    echo Setup finished.
    echo.
)

".venv\Scripts\python.exe" DePalencify.py
echo.
pause
exit /b 0

:setup_failed
echo.
echo Setup failed. Check your internet connection and try again.
rmdir /s /q ".venv" >nul 2>&1
pause
exit /b 1
