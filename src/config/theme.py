"""Nocturnal Studio design tokens adapted for Vidsaver mobile.

Typography and palette follow the Video-Downloader reference;
layout targets compact mobile cards and Material 3 navigation.
"""

from __future__ import annotations

import flet as ft

# --- Brand colors (reference) ---
PRIMARY = "#FF5C49"
PROCESSING = "#32A097"
DARK_BG = "#111318"
DARK_SURFACE = "#1E2127"
LIGHT_BG = "#F8F9FF"
LIGHT_SURFACE = "#FFFFFF"

# Semantic
SUCCESS = "#2E7D32"
WARNING = "#ED6C02"
ERROR = "#D32F2F"
ON_PRIMARY = "#FFFFFF"

# Font family names registered via page.fonts
FONT_HEADING = "SpaceGrotesk"
FONT_BODY = "Inter"


def register_fonts(page: ft.Page) -> None:
    """Register Inter + Space Grotesk from src/assets/fonts/."""
    page.fonts = {
        FONT_BODY: "fonts/Inter-Regular.ttf",
        "InterMedium": "fonts/Inter-Medium.ttf",
        "InterSemiBold": "fonts/Inter-SemiBold.ttf",
        FONT_HEADING: "fonts/SpaceGrotesk-SemiBold.ttf",
        "SpaceGroteskBold": "fonts/SpaceGrotesk-Bold.ttf",
    }


def build_theme(*, dark: bool) -> ft.Theme:
    """Material 3 theme with Vidsaver accent."""
    return ft.Theme(
        color_scheme_seed=PRIMARY,
        font_family=FONT_BODY,
        visual_density=ft.VisualDensity.STANDARD,
        scrollbar_theme=ft.ScrollbarTheme(
            thickness=6,
            radius=4,
            interactive=True,
        ),
    )


def apply_theme_mode(page: ft.Page, mode: str) -> None:
    """
    Apply theme mode: system | light | dark.
    Persists only via caller (settings); this only updates the page.
    """
    register_fonts(page)
    if mode == "light":
        page.theme_mode = ft.ThemeMode.LIGHT
        page.theme = build_theme(dark=False)
        page.dark_theme = build_theme(dark=True)
        page.bgcolor = LIGHT_BG
    elif mode == "dark":
        page.theme_mode = ft.ThemeMode.DARK
        page.theme = build_theme(dark=False)
        page.dark_theme = build_theme(dark=True)
        page.bgcolor = DARK_BG
    else:
        page.theme_mode = ft.ThemeMode.SYSTEM
        page.theme = build_theme(dark=False)
        page.dark_theme = build_theme(dark=True)
        page.bgcolor = None


APP_TITLE_SAFE = "Vidsaver"


def primary_app_bar(*, title: str = APP_TITLE_SAFE) -> ft.AppBar:
    return ft.AppBar(
        title=ft.Text(
            title,
            color=ON_PRIMARY,
            weight=ft.FontWeight.BOLD,
            font_family=FONT_HEADING,
        ),
        center_title=True,
        bgcolor=PRIMARY,
    )


# Avoid circular import of constants in module-level default
def status_color(state: str) -> str:
    """Map download state name to accent color."""
    s = (state or "").lower()
    if s in ("completed", "complete", "success"):
        return SUCCESS
    if s in ("failed", "error"):
        return ERROR
    if s in ("cancelled", "canceled"):
        return WARNING
    if s in ("processing", "merging", "publishing_to_gallery", "preparing"):
        return PROCESSING
    if s in ("downloading", "pending"):
        return PRIMARY
    return PRIMARY
