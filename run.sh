#!/usr/bin/env bash
# DePalencify launcher for Mac and Linux. First run creates a private environment (.venv_unix) and installs what is needed.
cd "$(dirname "$0")" || exit 1

pause() { echo; read -r -p "Press Enter to close this window..." _; }

PY=""
for candidate in python3 python; do
    if command -v "$candidate" >/dev/null 2>&1 && "$candidate" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)' >/dev/null 2>&1; then
        PY="$candidate"; break
    fi
done
if [ -z "$PY" ]; then
    echo "Python 3.9 or newer was not found."
    echo "Mac:   install it from https://www.python.org/downloads/"
    echo "Linux: install it with your package manager, e.g.  sudo apt install python3 python3-venv python3-pip"
    pause; exit 1
fi

if [ ! -x ".venv_unix/bin/python" ]; then
    echo "First run: setting things up. This takes a minute or two and needs internet."
    if ! "$PY" -m venv .venv_unix; then
        echo
        echo "Could not create the environment. On Ubuntu/Debian try:  sudo apt install python3-venv"
        rm -rf .venv_unix; pause; exit 1
    fi
    if ! .venv_unix/bin/python -m pip install --quiet --upgrade pip \
       || ! .venv_unix/bin/python -m pip install --quiet numpy pandas matplotlib xlsxwriter openpyxl; then
        echo
        echo "Setup failed. Check your internet connection and try again."
        rm -rf .venv_unix; pause; exit 1
    fi
    echo "Setup finished."
    echo
fi

.venv_unix/bin/python DePalencify.py
pause
