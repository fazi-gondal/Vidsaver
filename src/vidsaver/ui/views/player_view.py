"""Full-screen video player with ±10s seek controls."""

from __future__ import annotations

import asyncio
import os

import flet as ft
import flet_video as ftv

from vidsaver.ui.theme import current

SEEK_MS = 10_000  # 10 seconds


@ft.component
def PlayerView(file_path: str, on_close, page: ft.Page | None = None):
    file_name = os.path.basename(file_path) if file_path else "Video"
    palette = current(page)
    video_ref = ft.use_ref()

    # Flet 0.85+: show_controls is deprecated — leave default controls visible.
    # Do not pass show_controls=True/False.
    video_control = ft.use_memo(
        lambda: ftv.Video(
            ref=video_ref,
            expand=True,
            autoplay=True,
            playlist=[ftv.VideoMedia(file_path)],
        ),
        dependencies=[file_path],
    )

    async def seek_relative(delta_ms: int):
        video = video_ref.current
        if video is None:
            return
        try:
            pos = await video.get_current_position()
            current_ms = int(getattr(pos, "in_milliseconds", pos) or 0)
            target = max(0, current_ms + delta_ms)
            await video.seek(target)
        except Exception:
            try:
                await video.seek(max(0, delta_ms))
            except Exception:
                pass

    def on_back(_e=None):
        asyncio.create_task(seek_relative(-SEEK_MS))

    def on_forward(_e=None):
        asyncio.create_task(seek_relative(SEEK_MS))

    control_btn_style = ft.ButtonStyle(
        shape=ft.CircleBorder(),
        padding=12,
        bgcolor=ft.Colors.with_opacity(0.55, ft.Colors.BLACK),
        color=ft.Colors.WHITE,
    )

    controls_bar = ft.Container(
        content=ft.Row(
            controls=[
                ft.IconButton(
                    icon=ft.Icons.REPLAY_10,
                    icon_size=32,
                    icon_color=ft.Colors.WHITE,
                    tooltip="Back 10s",
                    on_click=on_back,
                    style=control_btn_style,
                ),
                ft.IconButton(
                    icon=ft.Icons.FORWARD_10,
                    icon_size=32,
                    icon_color=ft.Colors.WHITE,
                    tooltip="Forward 10s",
                    on_click=on_forward,
                    style=control_btn_style,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=28,
        ),
        padding=ft.Padding(0, 8, 0, 4),
    )

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text(
                            value=file_name,
                            weight=ft.FontWeight.BOLD,
                            size=16,
                            expand=True,
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                            color=palette.text if page else ft.Colors.WHITE,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE,
                            icon_color=ft.Colors.RED_ACCENT_400,
                            on_click=on_close,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Container(
                    content=video_control,
                    expand=True,
                    bgcolor=ft.Colors.BLACK,
                    border_radius=10,
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                ),
                controls_bar,
            ],
            expand=True,
            spacing=6,
        ),
        padding=ft.Padding(left=10, right=10, top=8, bottom=20),
        expand=True,
        bgcolor=palette.surface if page else None,
    )
