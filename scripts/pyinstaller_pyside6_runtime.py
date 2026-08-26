"""Prioriza las DLL de Qt incluidas junto al ejecutable de PyInstaller en Windows."""

from __future__ import annotations

import os
import sys
from pathlib import Path


if getattr(sys, "frozen", False):
    bundle_root = Path(sys._MEIPASS)
    for folder in (bundle_root / "PySide6", bundle_root / "shiboken6"):
        if folder.is_dir():
            os.add_dll_directory(str(folder))
            os.environ["PATH"] = f"{folder}{os.pathsep}{os.environ.get('PATH', '')}"
