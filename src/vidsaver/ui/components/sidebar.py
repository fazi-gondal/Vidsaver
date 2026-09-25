"""Desktop left sidebar navigation (Home / Downloads)."""

from __future__ import annotations

import flet as ft

from vidsaver.ui.theme import current

SIDEBAR_WIDTH = 220


@ft.component
def Sidebar(selected_index: int, on_select, dark_mode: bool, on_toggle_theme):
    palette = current()

    def item(index: int, icon: str, selected_icon: str, label: str) -> ft.Control:
        active = selected_index == index
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(
                        width=3.5,
                        height=22,
                        bgcolor=palette.accent if active else ft.Colors.TRANSPARENT,
                        border_radius=999,
                    ),
                    ft.Icon(
                        selected_icon if active else icon,
                        size=22,
                        color=palette.accent if active else palette.text_muted,
                    ),
                    ft.Text(
                        label,
                        size=14,
                        weight=ft.FontWeight.W_600 if active else ft.FontWeight.W_400,
                        color=palette.text if active else palette.text_muted,
                    ),
                ],
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=12, top=12, right=12, bottom=12),
            border_radius=12,
            bgcolor=ft.Colors.with_opacity(0.12, palette.accent) if active else None,
            ink=True,
            on_click=lambda e, i=index: on_select(i),
        )

    return ft.Container(
        width=SIDEBAR_WIDTH,
        bgcolor=palette.surface_variant,
        border=ft.Border(right=ft.BorderSide(1, palette.border)),
        padding=ft.Padding(12, 16, 12, 16),
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.PLAY_CIRCLE_FILL, color=palette.accent, size=28),
                        ft.Text(
                            "Vidsaver",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=palette.text,
                        ),
                    ],
                    spacing=10,
                ),
                ft.Container(height=16),
                item(0, ft.Icons.HOME_MAX_ROUNDED, ft.Icons.HOME, "Home"),
                item(
                    1,
                    ft.Icons.VIDEO_LIBRARY_OUTLINED,
                    ft.Icons.VIDEO_LIBRARY,
                    "Downloads",
                ),
                ft.Container(expand=True),
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(
                                ft.Icons.DARK_MODE if not dark_mode else ft.Icons.LIGHT_MODE,
                                size=20,
                                color=palette.text_muted,
                            ),
                            ft.Text(
                                "Dark mode" if not dark_mode else "Light mode",
                                size=13,
                                color=palette.text_muted,
                            ),
                        ],
                        spacing=10,
                    ),
                    padding=12,
                    border_radius=12,
                    ink=True,
                    on_click=on_toggle_theme,
                ),
            ],
            spacing=4,
            expand=True,
        ),
    )
