"""
player.py — Declarative video player view (Nocturnal Studio design).
"""

import os
import flet as ft
import flet_video as ftv

import theme


@ft.component
def PlayerView(file_path: str, on_close):
    """
    Declarative full-screen video player view.
    Handles its own lifecycle and unmounts cleanly when removed from the tree.

    The Video control is memoized so it survives re-renders without restarting
    playback. ft.use_memo only recreates it when file_path changes.
    """
    file_name = os.path.basename(file_path)
    play_error, set_play_error = ft.use_state("")

    video_control = ft.use_memo(
        lambda: ftv.Video(
            expand=True,
            autoplay=True,
            playlist=[ftv.VideoMedia(file_path)],
            on_error=lambda e: set_play_error(str(getattr(e, "data", "") or "Unable to play video.")),
        ),
        dependencies=[file_path],
    )

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.IconButton(
                                icon=ft.Icons.ARROW_BACK_ROUNDED,
                                icon_color=ft.Colors.WHITE,
                                tooltip="Back",
                                on_click=on_close,
                            ),
                            ft.Text(
                                value=file_name,
                                style=ft.TextStyle(
                                    font_family=theme.FONT_BODY_SEMIBOLD,
                                    size=15,
                                    weight=ft.FontWeight.W_600,
                                    color=ft.Colors.WHITE,
                                ),
                                expand=True,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                        ],
                        spacing=4,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.Padding(left=4, right=12, top=6, bottom=6),
                ),
                ft.Container(
                    content=(
                        ft.Column(
                            controls=[
                                ft.Icon(ft.Icons.ERROR_OUTLINE_ROUNDED, size=40, color=theme.PILL_RED),
                                ft.Text(
                                    f"Playback error: {play_error}",
                                    style=theme.body_md(theme.PILL_RED),
                                    text_align=ft.TextAlign.CENTER,
                                ),
                                ft.OutlinedButton("Go Back", on_click=on_close),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=12,
                        )
                        if play_error
                        else video_control
                    ),
                    alignment=ft.Alignment.CENTER if play_error else None,
                    expand=True,
                    bgcolor=ft.Colors.BLACK,
                ),
            ],
            spacing=0,
            expand=True,
        ),
        bgcolor=ft.Colors.BLACK,
        expand=True,
    )
