"""Polished empty-state placeholder (inspired by Video-Downloader)."""

from __future__ import annotations

import flet as ft

from vidsaver.ui.theme import current


@ft.component
def EmptyState(
    icon: str = ft.Icons.VIDEO_LIBRARY_OUTLINED,
    title: str = "No downloads yet",
    subtitle: str = "Paste a link on the Home tab to get started",
):
    palette = current()
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Icon(icon, size=56, color=palette.text_muted),
                ft.Text(
                    title,
                    size=16,
                    weight=ft.FontWeight.W_600,
                    color=palette.text,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    subtitle,
                    size=13,
                    color=palette.text_muted,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        ),
        alignment=ft.Alignment(0, 0),
        expand=True,
        padding=40,
    )
