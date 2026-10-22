@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
title Chamber data converter

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
    ".venv\Scripts\python.exe" -m pip install --quiet numpy pandas matplotlib xlsxwriter openpyxl
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
