#!/usr/bin/env bash
# Build a standalone Optimize Images X app with PyInstaller.
# PyInstaller does not cross-compile: run this on the OS you're targeting.
set -euo pipefail
cd "$(dirname "$0")"

PYTHON="${PYTHON:-python3.14}"

if ! command -v "$PYTHON" >/dev/null 2>&1; then
    echo "$PYTHON not found (PyInstaller doesn't support 3.15 yet)." >&2
    echo "Set PYTHON=/path/to/python3.14 to point at a specific interpreter." >&2
    exit 1
fi

# If more than one python3.14 is on PATH (e.g. Homebrew's alongside python.org's),
# `command -v` picks whichever comes first, which may lack Tcl/Tk support — the
# build would then silently produce an app that can't even launch tkinter.
if ! "$PYTHON" -c "import tkinter" >/dev/null 2>&1; then
    echo "$PYTHON has no Tcl/Tk support ('import tkinter' fails in it)." >&2
    echo "The built app would fail to launch. Point PYTHON at a build that" >&2
    echo "includes Tcl/Tk, e.g.: PYTHON=/path/to/other/python3.14 ./build.sh" >&2
    exit 1
fi

if [ ! -d venv-build ]; then
    "$PYTHON" -m venv venv-build
fi

source venv-build/bin/activate
pip install .
pip install tkinterdnd2
pip install pyinstaller
python -m PyInstaller optimize-images-x.spec
