"""Test bootstrap: stub flet if not installed so pure-logic modules can import."""

from __future__ import annotations

import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

# Ensure src is on path
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

try:
    import flet  # noqa: F401
except ImportError:
    # Minimal stub so modules that `import flet as ft` can load
    ft = types.ModuleType("flet")
    ft.Page = MagicMock
    ft.PagePlatform = types.SimpleNamespace(ANDROID="android")
    ft.Colors = MagicMock()
    ft.Icons = MagicMock()
    ft.ThemeMode = types.SimpleNamespace(DARK="dark", LIGHT="light", SYSTEM="system")
    ft.component = lambda f: f
    ft.use_state = MagicMock()
    ft.use_effect = MagicMock()
    ft.use_ref = MagicMock()
    ft.use_memo = MagicMock()
    ft.use_dialog = MagicMock()
    ft.context = types.SimpleNamespace(page=MagicMock())
    sys.modules["flet"] = ft
