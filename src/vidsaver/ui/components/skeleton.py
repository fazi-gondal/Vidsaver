"""Skeleton loading placeholders for the library list."""

from __future__ import annotations

import flet as ft

from vidsaver.ui.theme import current


@ft.component
def SkeletonCard():
    palette = current()
    bone = palette.surface_variant if hasattr(palette, "surface_variant") else "#E0E0E0"
    highlight = palette.border

    def bar(width: float, height: int = 12) -> ft.Container:
        return ft.Container(
            width=width,
            height=height,
            bgcolor=bone,
            border_radius=6,
        )

    return ft.Card(
        elevation=0,
        content=ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(
                        width=72,
                        height=72,
                        bgcolor=bone,
                        border_radius=10,
                    ),
                    ft.Column(
                        controls=[
                            bar(160, 14),
                            ft.Row(
                                controls=[bar(56, 18), bar(40, 12), bar(48, 12)],
                                spacing=8,
                            ),
                        ],
                        spacing=10,
                        expand=True,
                    ),
                ],
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(12, 12, 12, 12),
            border=ft.Border.all(1, highlight),
            border_radius=14,
        ),
    )


@ft.component
def SkeletonList(count: int = 5):
    return ft.ListView(
        controls=[SkeletonCard() for _ in range(count)],
        expand=True,
        spacing=10,
        padding=ft.Padding(12, 12, 12, 16),
    )
