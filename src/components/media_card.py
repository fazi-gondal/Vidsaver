"""Media preview card shown after URL analysis."""

from __future__ import annotations

import flet as ft

from config.theme import FONT_BODY, FONT_HEADING, PRIMARY
from utils.formatting import format_duration


@ft.component
def MediaPreviewCard(
    *,
    title: str,
    platform: str,
    duration=None,
    thumbnail: str = "",
    uploader: str = "",
    quality_label: str = "Best available",
    on_quick_download=None,
    on_change_quality=None,
    busy: bool = False,
):
    thumb = (
        ft.Image(
            src=thumbnail,
            width=96,
            height=72,
            fit=ft.BoxFit.COVER,
            border_radius=8,
        )
        if thumbnail
        else ft.Container(
            width=96,
            height=72,
            bgcolor=ft.Colors.with_opacity(0.12, PRIMARY),
            border_radius=8,
            content=ft.Icon(ft.Icons.PLAY_CIRCLE_FILL_ROUNDED, color=PRIMARY, size=32),
            alignment=ft.Alignment.CENTER,
        )
    )

    meta_bits = [platform]
    dur = format_duration(duration)
    if dur != "—":
        meta_bits.append(dur)
    if uploader:
        meta_bits.append(uploader[:40])

    return ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        thumb,
                        ft.Column(
                            [
                                ft.Text(
                                    title,
                                    size=14,
                                    weight=ft.FontWeight.W_600,
                                    max_lines=2,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                    font_family=FONT_HEADING,
                                ),
                                ft.Text(
                                    " · ".join(meta_bits),
                                    size=12,
                                    color=ft.Colors.ON_SURFACE_VARIANT,
                                    font_family=FONT_BODY,
                                ),
                                ft.Text(
                                    f"Quality: {quality_label}",
                                    size=12,
                                    color=PRIMARY,
                                    font_family=FONT_BODY,
                                ),
                            ],
                            spacing=4,
                            expand=True,
                        ),
                    ],
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
                ft.Row(
                    [
                        ft.Button(
                            content="Quick download",
                            icon=ft.Icons.DOWNLOAD_ROUNDED,
                            expand=True,
                            style=ft.ButtonStyle(
                                bgcolor=PRIMARY,
                                color=ft.Colors.WHITE,
                            ),
                            disabled=busy,
                            on_click=on_quick_download,
                        ),
                        ft.OutlinedButton(
                            "Quality",
                            icon=ft.Icons.HIGH_QUALITY_OUTLINED,
                            disabled=busy,
                            on_click=on_change_quality,
                        ),
                    ],
                    spacing=8,
                ),
            ],
            spacing=12,
        ),
        padding=14,
        border_radius=14,
        bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.ON_SURFACE),
        border=ft.Border.all(1, ft.Colors.with_opacity(0.08, ft.Colors.ON_SURFACE)),
    )
