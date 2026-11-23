"""
player.py — Declarative video player view.
"""

import os
import flet as ft
import flet_video as ftv


@ft.component
def PlayerView(file_path: str, on_close):
    """
    Declarative full-screen video player view.
    Handles its own lifecycle and unmounts cleanly when removed from the tree.

    The Video control is memoized so it survives re-renders without restarting
    playback. ft.use_memo only recreates it when file_path changes.
    """
    file_name = os.path.basename(file_path)

    # Memoize the Video control — prevents recreation (and playback reset)
    # on every re-render triggered by parent state changes.
    video_control = ft.use_memo(
        lambda: ftv.Video(
            expand=True,
            autoplay=True,
            playlist=[ftv.VideoMedia(file_path)],
        ),
        dependencies=[file_path],
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
                ),
            ],
            expand=True,
        ),
        padding=ft.Padding(left=10, right=10, top=8, bottom=30),
        expand=True,
    )
