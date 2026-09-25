"""Polished video card with real thumbnail when available."""

from __future__ import annotations

import os

import flet as ft

from vidsaver.config.constants import PLATFORM_COLORS
from vidsaver.models.video import VideoEntry
from vidsaver.ui.theme import current


@ft.component
def VideoCard(entry: VideoEntry, on_play, on_delete):
    palette = current()
    colors = PLATFORM_COLORS.get(entry.platform, PLATFORM_COLORS["Video"])
    thumb_color, chip_bg = colors

    size = entry.size
    if not size and entry.source_path:
        try:
            size = os.path.getsize(entry.source_path)
        except Exception:
            size = 0
    size_str = f"{size / (1024 * 1024):.1f} MB" if size else ""
    name_without_ext = os.path.splitext(entry.display_name)[0]

    # Thumbnail is stored in the app's private data dir — never in the gallery
    has_thumb = bool(entry.thumbnail_path and os.path.isfile(entry.thumbnail_path))

    if has_thumb:
        thumb_body = ft.Stack(
            controls=[
                ft.Image(
                    src=entry.thumbnail_path,
                    width=80,
                    height=80,
                    fit=ft.BoxFit.COVER,
                    border_radius=12,
                ),
                ft.Container(
                    content=ft.Icon(
                        ft.Icons.PLAY_CIRCLE_FILL_ROUNDED,
                        color=ft.Colors.with_opacity(0.9, ft.Colors.WHITE),
                        size=28,
                    ),
                    alignment=ft.Alignment(0, 0),
                    expand=True,
                ),
            ]
        )
    else:
        thumb_body = ft.Stack(
            controls=[
                ft.Container(
                    expand=True,
                    gradient=ft.LinearGradient(
                        begin=ft.Alignment(-1, -1),
                        end=ft.Alignment(1, 1),
                        colors=[thumb_color, ft.Colors.with_opacity(0.75, thumb_color)],
                    ),
                ),
                ft.Container(
                    content=ft.Icon(
                        ft.Icons.PLAY_CIRCLE_FILL_ROUNDED,
                        color=ft.Colors.with_opacity(0.92, ft.Colors.WHITE),
                        size=36,
                    ),
                    alignment=ft.Alignment(0, 0),
                    expand=True,
                ),
            ]
        )

    thumb = ft.Container(
        width=80,
        height=80,
        border_radius=12,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        content=thumb_body,
        bgcolor=palette.surface_variant,
    )

    chip = ft.Container(
        content=ft.Text(
            entry.platform,
            size=10,
            weight=ft.FontWeight.W_600,
            color=thumb_color,
        ),
        bgcolor=chip_bg,
        border_radius=20,
        padding=ft.Padding(left=8, right=8, top=3, bottom=3),
    )

    meta_bits = []
    if size_str:
        meta_bits.append(ft.Text(size_str, size=11, color=palette.text_muted))
    if entry.date:
        meta_bits.append(ft.Text(entry.date, size=11, color=palette.text_muted))

    info_col = ft.Column(
        controls=[
            ft.Text(
                name_without_ext,
                size=14,
                weight=ft.FontWeight.W_600,
                max_lines=2,
                overflow=ft.TextOverflow.ELLIPSIS,
                color=palette.text,
            ),
            ft.Row(
                controls=[chip, *meta_bits],
                spacing=8,
                wrap=True,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        ],
        spacing=6,
        expand=True,
        alignment=ft.MainAxisAlignment.CENTER,
    )

    return ft.Container(
        content=ft.Row(
            controls=[
                thumb,
                info_col,
                ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
                    icon_color=palette.text_muted,
                    icon_size=22,
                    tooltip="Delete",
                    on_click=lambda e: on_delete(entry),
                    style=ft.ButtonStyle(shape=ft.CircleBorder(), padding=8),
                ),
            ],
            spacing=14,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding(14, 12, 8, 12),
        bgcolor=palette.surface,
        border=ft.Border.all(1, palette.border),
        border_radius=16,
        ink=True,
        on_click=lambda e: on_play(entry),
        shadow=ft.BoxShadow(
            blur_radius=8,
            color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK),
            offset=ft.Offset(0, 2),
        ),
    )
