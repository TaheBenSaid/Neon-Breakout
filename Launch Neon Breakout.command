#!/bin/bash
# Double-click this file to launch Neon Breakout.
cd "$(dirname "$0")" || exit 1

# Pick the first available python interpreter.
if command -v python3 >/dev/null 2>&1; then
    PY=python3
elif command -v python >/dev/null 2>&1; then
    PY=python
else
    echo "Python 3 is not installed. Install it from https://www.python.org/downloads/"
    read -n 1 -s -r -p "Press any key to close..."
    exit 1
fi

# Install pygame quietly if it's missing.
if ! "$PY" -c "import pygame" >/dev/null 2>&1; then
    echo "Installing pygame (one-time setup)..."
    "$PY" -m pip install --user pygame
fi

echo "Starting Neon Breakout..."
"$PY" main.py
