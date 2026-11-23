"""Card for a single download task on the Downloading tab."""

from __future__ import annotations

import flet as ft

from config.theme import FONT_BODY, FONT_HEADING, PRIMARY, status_color
from models.download_state import DownloadState
from models.download_task import DownloadTask


@ft.component
def DownloadTaskCard(
    task: DownloadTask,
    *,
    on_cancel=None,
    on_retry=None,
):
    pct = task.progress.percent
    progress_value = None if pct is None else max(0.0, min(1.0, pct / 100.0))
    color = status_color(task.state.value)

    actions = []
    if not task.is_terminal:
        actions.append(
            ft.IconButton(
                icon=ft.Icons.CLOSE_ROUNDED,
                tooltip="Cancel",
                icon_color=ft.Colors.ERROR,
                on_click=lambda e: on_cancel and on_cancel(task.id),
            )
        )
    if task.state in (DownloadState.FAILED, DownloadState.CANCELLED):
        actions.append(
            ft.IconButton(
                icon=ft.Icons.REFRESH_ROUNDED,
                tooltip="Retry",
                icon_color=PRIMARY,
                on_click=lambda e: on_retry and on_retry(task.id),
            )
        )

    thumb = ft.Container(
        width=64,
        height=48,
        border_radius=8,
        bgcolor=ft.Colors.with_opacity(0.12, color),
        content=ft.Icon(ft.Icons.MOVIE_CREATION_OUTLINED, color=color, size=24),
        alignment=ft.Alignment.CENTER,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
    )
    if task.thumbnail_url:
        thumb = ft.Container(
            width=64,
            height=48,
            border_radius=8,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            content=ft.Image(src=task.thumbnail_url, fit=ft.BoxFit.COVER, width=64, height=48),
        )

    metrics = []
    if pct is not None:
        metrics.append(f"{pct:.0f}%")
    size_label = task.progress.size_label
    if size_label and size_label != "— / —":
        metrics.append(size_label)
    speed = task.progress.speed_label
    if speed and speed != "—":
        metrics.append(speed)
    eta = task.progress.eta_label
    if eta and eta != "—":
        metrics.append(f"ETA {eta}")

    return ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        thumb,
                        ft.Column(
                            [
                                ft.Text(
                                    task.title or task.request.url,
                                    size=13,
                                    weight=ft.FontWeight.W_600,
                                    max_lines=2,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                    font_family=FONT_HEADING,
                                ),
                                ft.Text(
                                    f"{task.platform} · {task.state.label}",
                                    size=11,
                                    color=color,
                                    font_family=FONT_BODY,
                                ),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                        *actions,
                    ],
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.ProgressBar(
                    value=progress_value,
                    height=4,
                    color=color,
                    bgcolor=ft.Colors.with_opacity(0.12, color),
                    border_radius=4,
                ),
                ft.Row(
                    [
                        ft.Text(
                            " · ".join(metrics) if metrics else "—",
                            size=11,
                            color=ft.Colors.ON_SURFACE_VARIANT,
                            expand=True,
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                        ft.Text(
                            task.progress.status_text or "",
                            size=11,
                            color=ft.Colors.ON_SURFACE_VARIANT,
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                    ],
                ),
                ft.Text(
                    task.error,
                    size=11,
                    color=ft.Colors.ERROR,
                    visible=bool(task.error),
                ),
            ],
            spacing=6,
        ),
        padding=12,
        border_radius=12,
        bgcolor=ft.Colors.with_opacity(0.04, ft.Colors.ON_SURFACE),
        border=ft.Border.all(1, ft.Colors.with_opacity(0.06, ft.Colors.ON_SURFACE)),
    )
