"""Home tab — paste link and download."""

from __future__ import annotations

import asyncio

import flet as ft

from vidsaver.ui.theme import current
from vidsaver.utils.platform import is_video_url


@ft.component
def HomeView(
    status_text: str,
    progress_val: float | None,
    progress_visible: bool,
    download_disabled: bool,
    on_download,
    page: ft.Page,
):
    url, set_url = ft.use_state("")
    palette = current(page)

    async def try_paste_clipboard():
        try:
            if not hasattr(page, "_clipboard"):
                page._clipboard = ft.Clipboard()  # type: ignore[attr-defined]
            clip = await page._clipboard.get()  # type: ignore[attr-defined]
            if clip and is_video_url(clip) and clip.strip() != url.strip():
                set_url(clip.strip())
        except Exception:
            pass

    def setup_lifecycle():
        def on_lifecycle(e):
            if e.state == ft.AppLifecycleState.RESUME:
                asyncio.create_task(try_paste_clipboard())

        old = page.on_app_lifecycle_state_change
        page.on_app_lifecycle_state_change = on_lifecycle
        return lambda: setattr(page, "on_app_lifecycle_state_change", old)

    ft.use_effect(setup_lifecycle, dependencies=[])

    async def on_url_focus(_e):
        if not url:
            await try_paste_clipboard()

    def handle_submit(_e=None):
        value = url.strip()
        if value:
            on_download(value)

    return ft.Container(
        bgcolor=palette.surface,
        content=ft.Column(
            controls=[
                ft.Text(
                    "Download any video",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=palette.text,
                ),
                ft.Text(
                    "TikTok · Instagram · YouTube · X · Facebook",
                    size=12,
                    color=palette.text_muted,
                ),
                ft.Container(height=8),
                ft.TextField(
                    value=url,
                    on_change=lambda e: set_url(e.control.value or ""),
                    on_focus=lambda e: asyncio.create_task(on_url_focus(e)),
                    on_submit=handle_submit,
                    label="Paste video link",
                    border=ft.OutlineInputBorder(border_radius=ft.BorderRadius(12, 12, 12, 12)),
                    filled=True,
                    prefix_icon=ft.Icons.LINK,
                    autofocus=False,
                ),
                ft.Button(
                    content="Download",
                    icon=ft.Icons.DOWNLOAD_ROUNDED,
                    height=44,
                    style=ft.ButtonStyle(
                        bgcolor=palette.accent,
                        color=palette.on_accent,
                        shape=ft.RoundedRectangleBorder(radius=12),
                    ),
                    disabled=download_disabled,
                    on_click=handle_submit,
                ),
                ft.ProgressBar(
                    height=4,
                    value=progress_val,
                    visible=progress_visible,
                    color=palette.accent,
                    bgcolor=palette.accent_container,
                    border_radius=4,
                ),
                ft.Text(
                    value=status_text,
                    color=palette.text_muted,
                    size=12,
                ),
                ft.Container(expand=True),
                ft.Text(
                    "Vidsaver made with love by Fazi Gondal",
                    size=12,
                    color=palette.text_muted,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            spacing=12,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            expand=True,
        ),
        padding=ft.Padding(left=24, right=24, top=20, bottom=24),
        expand=True,
    )
