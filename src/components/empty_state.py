"""Reusable empty / placeholder state."""

from __future__ import annotations

import flet as ft

from config.theme import FONT_BODY, FONT_HEADING


@ft.component
def EmptyState(
    *,
    icon: str = ft.Icons.INBOX_OUTLINED,
    title: str = "Nothing here yet",
    subtitle: str = "",
):
    controls = [
        ft.Icon(icon, size=56, color=ft.Colors.OUTLINE),
        ft.Text(
            title,
            size=18,
            weight=ft.FontWeight.W_600,
            font_family=FONT_HEADING,
            text_align=ft.TextAlign.CENTER,
        ),
    ]
    if subtitle:
        controls.append(
            ft.Text(
                subtitle,
                size=13,
                color=ft.Colors.ON_SURFACE_VARIANT,
                text_align=ft.TextAlign.CENTER,
                font_family=FONT_BODY,
            )
        )
    return ft.Container(
        content=ft.Column(
            controls,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
        ),
        alignment=ft.Alignment.CENTER,
        expand=True,
        padding=32,
    )
