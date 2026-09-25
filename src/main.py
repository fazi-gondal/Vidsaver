"""
Vidsaver entry point — thin bootstrap for Flet 1.0.

Heavy work (yt-dlp import, MediaScanner, metadata sync) is deferred until
after the first frame so the Home screen appears instantly.
"""

from __future__ import annotations

import flet as ft

from vidsaver.ui.app import main

if __name__ == "__main__":
    ft.run(main)
