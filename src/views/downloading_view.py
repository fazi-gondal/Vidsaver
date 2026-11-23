"""Downloading tab — active, queued, and recent tasks."""

from __future__ import annotations

import flet as ft

from components.download_task_card import DownloadTaskCard
from components.empty_state import EmptyState
from config.theme import FONT_BODY, FONT_HEADING, PRIMARY
from models.download_state import DownloadState
from models.download_task import DownloadTask


@ft.component
def DownloadingView(
    *,
    tasks: list[DownloadTask] | None = None,
    on_cancel=None,
    on_retry=None,
    on_details=None,
    active_count: int = 0,
    queued_count: int = 0,
):
    tasks = tasks or []
    active = [t for t in tasks if t.is_active or t.state is DownloadState.PENDING]
    done = [t for t in tasks if t.is_terminal]

    if not tasks:
        return EmptyState(
            icon=ft.Icons.DOWNLOAD_ROUNDED,
            title="No downloads yet",
            subtitle="Start a download from Home. Each task keeps its own progress here.",
        )

    sections = []
    if active:
        sections.append(
            ft.Text(
                f"In progress ({len(active)})",
                size=13,
                weight=ft.FontWeight.W_600,
                color=PRIMARY,
                font_family=FONT_HEADING,
            )
        )
        sections.extend(
            DownloadTaskCard(
                task=t,
                on_cancel=on_cancel,
                on_retry=on_retry,
                on_details=on_details,
            )
            for t in active
        )
    if done:
        sections.append(
            ft.Text(
                f"Recent ({len(done)})",
                size=13,
                weight=ft.FontWeight.W_600,
                font_family=FONT_HEADING,
            )
        )
        sections.extend(
            DownloadTaskCard(
                task=t,
                on_cancel=on_cancel,
                on_retry=on_retry,
                on_details=on_details,
            )
            for t in done[:20]
        )

    return ft.Container(
        content=ft.Column(
            sections,
            spacing=10,
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True,
        ),
        padding=12,
        expand=True,
    )
