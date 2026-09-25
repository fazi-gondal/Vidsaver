"""Lightweight design tokens inspired by Video-Downloader's surface hierarchy."""

from __future__ import annotations

from dataclasses import dataclass

import flet as ft


@dataclass(frozen=True)
class Palette:
    accent: str
    accent_container: str
    on_accent: str
    surface: str
    surface_variant: str
    text: str
    text_muted: str
    border: str
    success: str
    error: str
    card_elevation: int
    appbar: str
    nav_bg: str


LIGHT = Palette(
    accent="#1976D2",
    accent_container="#BBDEFB",
    on_accent="#FFFFFF",
    surface="#FFFFFF",
    surface_variant="#EEEEEE",
    text="#212121",
    text_muted="#757575",
    border="#E0E0E0",
    success="#2E7D32",
    error="#C62828",
    card_elevation=2,
    appbar="#1565C0",
    nav_bg="#FFFFFF",
)

DARK = Palette(
    accent="#42A5F5",
    accent_container="#0D47A1",
    on_accent="#FFFFFF",
    surface="#1E1E1E",
    surface_variant="#2C2C2C",
    text="#E8E8E8",
    text_muted="#9E9E9E",
    border="#3A3A3A",
    success="#66BB6A",
    error="#EF5350",
    card_elevation=1,
    appbar="#0D47A1",
    nav_bg="#121212",
)


def current(page: ft.Page | None = None) -> Palette:
    """Return the active palette for the given page (or the current Flet context)."""
    if page is None:
        try:
            page = ft.context.page  # type: ignore[attr-defined]
        except Exception:
            page = None

    if page is not None and getattr(page, "theme_mode", None) == ft.ThemeMode.DARK:
        return DARK
    return LIGHT


def app_theme() -> ft.Theme:
    return ft.Theme(
        color_scheme_seed=ft.Colors.BLUE,
        scrollbar_theme=ft.ScrollbarTheme(
            thickness=6,
            radius=4,
            interactive=True,
        ),
    )
