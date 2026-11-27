"""Unit tests for theme.py (Nocturnal Studio design system)."""

import flet as ft

import theme


def test_themes_instantiate():
    light = theme.light_theme()
    dark = theme.dark_theme()
    assert isinstance(light, ft.Theme)
    assert isinstance(dark, ft.Theme)


def test_ui_helpers():
    pill = theme.status_pill("Instagram", theme.PILL_CORAL)
    assert isinstance(pill, ft.Container)

    card = theme.surface_card(ft.Text("Hello"))
    assert isinstance(card, ft.Container)

    box = theme.inset_input_box(ft.TextField(border=ft.NoInputBorder()))
    assert isinstance(box, ft.Container)

    empty = theme.empty_state(
        icon=ft.Icons.VIDEO_LIBRARY_OUTLINED,
        title="No downloads yet",
        subtitle="Downloaded videos will appear here.",
        action=ft.OutlinedButton("Download a video"),
    )
    assert isinstance(empty, ft.Container)
