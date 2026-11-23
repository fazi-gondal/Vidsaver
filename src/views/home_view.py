"""Home tab — URL input, analyze, preview, quality, download."""

from __future__ import annotations

import asyncio

import flet as ft

from components.media_card import MediaPreviewCard
from components.url_input import UrlInput
from config.theme import FONT_BODY, FONT_HEADING, PRIMARY, PROCESSING
from utils.validators import is_video_url, normalize_url


SUPPORTED_HINT = "TikTok · Instagram · YouTube · X · Facebook"


@ft.component
def HomeView(
    *,
    page: ft.Page,
    status_text_val: str,
    progress_val: float | None,
    progress_visible: bool,
    download_disabled: bool,
    on_download,  # (url: str, format_selector: str | None) -> None
    on_analyze,  # async (url: str) -> dict | None  scheduled via callback that returns analysis
    analysis: dict | None,
    selected_quality_label: str,
    on_select_quality,  # (option: dict) -> None
    on_clear_analysis,
):
    url, set_url = ft.use_state("")
    analyzing, set_analyzing = ft.use_state(False)
    analyze_error, set_analyze_error = ft.use_state("")

    async def try_paste_clipboard():
        settings = getattr(page, "_app_settings", None)
        if settings is not None and not getattr(settings, "clipboard_auto_paste", True):
            return
        try:
            clipboard = getattr(page, "_clipboard", None)
            if clipboard is None:
                clipboard = ft.Clipboard()
                setattr(page, "_clipboard", clipboard)
            clip = await clipboard.get()
            if clip and is_video_url(clip) and clip.strip() != url.strip():
                set_url(clip.strip())
        except Exception:
            pass

    def setup_lifecycle():
        def on_lifecycle(e):
            if e.state == ft.AppLifecycleState.RESUME:
                asyncio.create_task(try_paste_clipboard())

        old_handler = page.on_app_lifecycle_state_change
        page.on_app_lifecycle_state_change = on_lifecycle
        return lambda: setattr(page, "on_app_lifecycle_state_change", old_handler)

    ft.use_effect(setup_lifecycle, dependencies=[url])

    async def on_url_focus(_e):
        if not url:
            await try_paste_clipboard()

    async def do_paste(_e):
        await try_paste_clipboard()

    def handle_analyze(_e=None):
        value = normalize_url(url)
        if not value:
            set_analyze_error("Paste a video link first.")
            return
        if not is_video_url(value):
            set_analyze_error("Unsupported or invalid URL.")
            return
        set_analyze_error("")
        set_analyzing(True)
        on_clear_analysis()

        async def _run():
            try:
                result = await on_analyze(value)
                if not result or not result.get("ok"):
                    set_analyze_error(
                        (result or {}).get("error") or "Could not analyze this link."
                    )
            except Exception as exc:
                set_analyze_error(str(exc))
            finally:
                set_analyzing(False)

        asyncio.create_task(_run())

    def handle_quick(_e=None):
        value = normalize_url(url)
        if analysis and analysis.get("ok") and not analysis.get("is_playlist"):
            value = analysis.get("webpage_url") or analysis.get("url") or value
        fmt = None
        # selected format stored on page by parent via analysis selection
        sel = getattr(page, "_selected_format_selector", None)
        if sel:
            fmt = sel
        if value:
            on_download(value, fmt)

    def open_quality_sheet(_e=None):
        if not analysis or not analysis.get("quality_options"):
            return
        options = analysis["quality_options"]

        def pick(opt):
            on_select_quality(opt)
            asyncio.create_task(page.pop_dialog())

        sheet = ft.BottomSheet(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            "Select quality",
                            size=16,
                            weight=ft.FontWeight.W_600,
                            font_family=FONT_HEADING,
                        ),
                        ft.Column(
                            [
                                ft.ListTile(
                                    title=ft.Text(opt["label"]),
                                    subtitle=ft.Text(
                                        f"format {opt['format_id']}"
                                        if opt.get("format_id")
                                        else "yt-dlp best"
                                    ),
                                    on_click=lambda e, o=opt: pick(o),
                                )
                                for opt in options
                            ],
                            tight=True,
                            scroll=ft.ScrollMode.AUTO,
                            height=280,
                        ),
                    ],
                    tight=True,
                    spacing=8,
                ),
                padding=16,
            ),
            open=True,
        )
        asyncio.create_task(page.show_dialog(sheet))

    # Playlist list + bulk enqueue
    playlist_block = None
    if analysis and analysis.get("ok") and analysis.get("is_playlist"):
        entries = analysis.get("entries") or []

        def download_entry(entry):
            on_download(entry.get("url") or "", None)

        def download_all(_e=None):
            for ent in entries[:30]:
                u = ent.get("url") or ""
                if u:
                    on_download(u, None)

        playlist_block = ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(
                            f"Playlist · {analysis.get('entry_count', len(entries))} items",
                            size=14,
                            weight=ft.FontWeight.W_600,
                            font_family=FONT_HEADING,
                            expand=True,
                        ),
                        ft.Button(
                            "Queue all",
                            icon=ft.Icons.PLAYLIST_ADD_CHECK,
                            style=ft.ButtonStyle(bgcolor=PRIMARY, color=ft.Colors.WHITE),
                            disabled=download_disabled or analyzing,
                            on_click=download_all,
                        ),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Column(
                    [
                        ft.ListTile(
                            title=ft.Text(ent.get("title") or "Item", max_lines=1),
                            trailing=ft.IconButton(
                                icon=ft.Icons.DOWNLOAD_ROUNDED,
                                icon_color=PRIMARY,
                                on_click=lambda e, ent=ent: download_entry(ent),
                            ),
                        )
                        for ent in entries[:30]
                    ],
                    scroll=ft.ScrollMode.AUTO,
                    height=220,
                ),
            ],
            spacing=4,
        )

    preview = None
    if analysis and analysis.get("ok") and not analysis.get("is_playlist"):
        preview = MediaPreviewCard(
            title=analysis.get("title") or "Video",
            platform=analysis.get("platform") or "Video",
            duration=analysis.get("duration"),
            thumbnail=analysis.get("thumbnail") or "",
            uploader=analysis.get("uploader") or "",
            quality_label=selected_quality_label or "Best available",
            on_quick_download=handle_quick,
            on_change_quality=open_quality_sheet,
            busy=download_disabled or analyzing,
        )

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    "Vidsaver",
                    size=22,
                    weight=ft.FontWeight.BOLD,
                    font_family=FONT_HEADING,
                    color=PRIMARY,
                ),
                ft.Text(
                    SUPPORTED_HINT,
                    size=12,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                    font_family=FONT_BODY,
                ),
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Text(name, size=10, weight=ft.FontWeight.W_600),
                            padding=ft.Padding(8, 4, 8, 4),
                            border_radius=12,
                            bgcolor=ft.Colors.with_opacity(0.08, PRIMARY),
                        )
                        for name in ("TikTok", "Instagram", "YouTube", "X", "Facebook")
                    ],
                    spacing=6,
                    wrap=True,
                ),
                UrlInput(
                    value=url,
                    on_change=set_url,
                    on_submit=handle_analyze,
                    on_paste_click=lambda e: asyncio.create_task(do_paste(e)),
                    on_focus=lambda e: asyncio.create_task(on_url_focus(e)),
                    disabled=download_disabled or analyzing,
                ),
                ft.Row(
                    [
                        ft.Button(
                            "Analyze",
                            icon=ft.Icons.SEARCH_ROUNDED,
                            expand=True,
                            style=ft.ButtonStyle(bgcolor=PROCESSING, color=ft.Colors.WHITE),
                            disabled=download_disabled or analyzing,
                            on_click=handle_analyze,
                        ),
                        ft.Button(
                            "Quick download",
                            icon=ft.Icons.FLASH_ON_ROUNDED,
                            expand=True,
                            style=ft.ButtonStyle(bgcolor=PRIMARY, color=ft.Colors.WHITE),
                            disabled=download_disabled or analyzing,
                            on_click=handle_quick,
                        ),
                    ],
                    spacing=8,
                ),
                ft.ProgressBar(
                    height=4,
                    value=progress_val,
                    visible=progress_visible or analyzing,
                    color=PRIMARY,
                    bgcolor=ft.Colors.with_opacity(0.15, PRIMARY),
                    border_radius=4,
                ),
                ft.Text(
                    value=analyze_error or status_text_val,
                    color=ft.Colors.ERROR if analyze_error else ft.Colors.ON_SURFACE_VARIANT,
                    size=12,
                    font_family=FONT_BODY,
                ),
                preview,
                playlist_block,
                ft.Container(expand=True),
                ft.Text(
                    "Made with love by Fazi Gondal",
                    size=12,
                    color=ft.Colors.OUTLINE,
                    text_align=ft.TextAlign.CENTER,
                    font_family=FONT_BODY,
                ),
            ],
            spacing=12,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True,
        ),
        padding=ft.Padding(left=20, right=20, top=16, bottom=16),
        expand=True,
    )
