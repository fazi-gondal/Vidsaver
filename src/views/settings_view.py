"""Settings tab — theme and download preferences."""

from __future__ import annotations

import flet as ft

from config.constants import (
    APP_VERSION,
    DEFAULT_MAX_CONCURRENT,
    REPO_URL,
    RESOLUTION_PRESETS,
    VIDEO_CONTAINERS,
)
from config.settings import AppSettings
from config.theme import FONT_BODY, FONT_HEADING, PRIMARY


@ft.component
def SettingsView(
    settings: AppSettings,
    on_settings_changed,
    on_clear_finished=None,
    data_dir: str = "",
    on_request_notification_permission=None,
):
    """Vertically scrolling mobile settings. Persists via on_settings_changed."""

    theme_mode, set_theme_mode = ft.use_state(settings.theme_mode)
    max_concurrent, set_max_concurrent = ft.use_state(str(settings.max_concurrent))
    concurrent_fragments, set_concurrent_fragments = ft.use_state(
        str(getattr(settings, "concurrent_fragments", 4))
    )
    retry_count, set_retry_count = ft.use_state(str(getattr(settings, "retry_count", 5)))
    rate_limit, set_rate_limit = ft.use_state(str(getattr(settings, "rate_limit_kbps", 0)))
    clipboard_auto, set_clipboard_auto = ft.use_state(settings.clipboard_auto_paste)
    notifications_on, set_notifications_on = ft.use_state(settings.notifications_enabled)
    background_on, set_background_on = ft.use_state(
        getattr(settings, "background_downloads_enabled", True)
    )
    default_quality, set_default_quality = ft.use_state(settings.default_quality or "best")
    default_container, set_default_container = ft.use_state(settings.default_container or "mp4")
    download_mode, set_download_mode = ft.use_state(settings.default_download_mode or "video")
    write_subs, set_write_subs = ft.use_state(getattr(settings, "write_subtitles", False))

    def persist(**kwargs):
        for k, v in kwargs.items():
            setattr(settings, k, v)
        on_settings_changed(settings)

    def on_theme(mode: str):
        set_theme_mode(mode)
        persist(theme_mode=mode)

    def clamp_int(raw: str, default: int, lo: int, hi: int) -> int:
        try:
            return max(lo, min(hi, int(raw)))
        except ValueError:
            return default

    def section(title: str, *controls):
        return ft.Column(
            [
                ft.Text(
                    title,
                    size=13,
                    weight=ft.FontWeight.W_600,
                    color=PRIMARY,
                    font_family=FONT_HEADING,
                ),
                *controls,
            ],
            spacing=8,
        )

    def tile(title: str, subtitle: str, trailing):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(title, size=14, weight=ft.FontWeight.W_500, font_family=FONT_BODY),
                            ft.Text(subtitle, size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    trailing,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(12, 10, 12, 10),
            border_radius=12,
            bgcolor=ft.Colors.with_opacity(0.04, ft.Colors.ON_SURFACE),
        )

    def quality_dd_value():
        dq = default_quality
        if dq in ("best", "Best available", ""):
            return "best"
        digits = "".join(c for c in str(dq) if c.isdigit())
        return digits or "best"

    return ft.Container(
        content=ft.Column(
            [
                section(
                    "Appearance",
                    ft.SegmentedButton(
                        selected={theme_mode},
                        allow_multiple_selection=False,
                        segments=[
                            ft.Segment(value="system", label=ft.Text("System"), icon=ft.Icon(ft.Icons.BRIGHTNESS_AUTO)),
                            ft.Segment(value="light", label=ft.Text("Light"), icon=ft.Icon(ft.Icons.LIGHT_MODE)),
                            ft.Segment(value="dark", label=ft.Text("Dark"), icon=ft.Icon(ft.Icons.DARK_MODE)),
                        ],
                        on_change=lambda e: on_theme(next(iter(e.control.selected))),
                    ),
                ),
                section(
                    "Download preferences",
                    tile(
                        "Default quality",
                        "Applied after Analyze when the height is available.",
                        ft.Dropdown(
                            value=quality_dd_value(),
                            width=120,
                            dense=True,
                            options=[
                                ft.dropdown.Option("best", "Best"),
                                ft.dropdown.Option("1080", "1080p"),
                                ft.dropdown.Option("720", "720p"),
                                ft.dropdown.Option("480", "480p"),
                                ft.dropdown.Option("360", "360p"),
                            ],
                            on_change=lambda e: (
                                set_default_quality(e.control.value or "best"),
                                persist(default_quality=e.control.value or "best"),
                            ),
                        ),
                    ),
                    tile(
                        "Default container",
                        "Preferred file container for merges.",
                        ft.Dropdown(
                            value=default_container if default_container in VIDEO_CONTAINERS else "mp4",
                            width=100,
                            dense=True,
                            options=[ft.dropdown.Option(c) for c in VIDEO_CONTAINERS],
                            on_change=lambda e: (
                                set_default_container(e.control.value or "mp4"),
                                persist(default_container=e.control.value or "mp4"),
                            ),
                        ),
                    ),
                    tile(
                        "Download mode",
                        "Video (A/V) or audio-only default.",
                        ft.Dropdown(
                            value=download_mode if download_mode in ("video", "audio") else "video",
                            width=110,
                            dense=True,
                            options=[
                                ft.dropdown.Option("video", "Video"),
                                ft.dropdown.Option("audio", "Audio"),
                            ],
                            on_change=lambda e: (
                                set_download_mode(e.control.value or "video"),
                                persist(default_download_mode=e.control.value or "video"),
                            ),
                        ),
                    ),
                    tile(
                        "Max concurrent",
                        "Parallel downloads (1–4).",
                        ft.TextField(
                            value=max_concurrent,
                            width=64,
                            dense=True,
                            text_align=ft.TextAlign.CENTER,
                            keyboard_type=ft.KeyboardType.NUMBER,
                            on_blur=lambda e: (
                                set_max_concurrent(e.control.value or "1"),
                                persist(
                                    max_concurrent=clamp_int(
                                        e.control.value or "1", DEFAULT_MAX_CONCURRENT, 1, 4
                                    )
                                ),
                            ),
                        ),
                    ),
                    tile(
                        "Fragment concurrency",
                        "Parallel fragments per download (1–8).",
                        ft.TextField(
                            value=concurrent_fragments,
                            width=64,
                            dense=True,
                            text_align=ft.TextAlign.CENTER,
                            keyboard_type=ft.KeyboardType.NUMBER,
                            on_blur=lambda e: (
                                set_concurrent_fragments(e.control.value or "4"),
                                persist(
                                    concurrent_fragments=clamp_int(e.control.value or "4", 4, 1, 8)
                                ),
                            ),
                        ),
                    ),
                    tile(
                        "Retries",
                        "Network retries per download (0–15).",
                        ft.TextField(
                            value=retry_count,
                            width=64,
                            dense=True,
                            text_align=ft.TextAlign.CENTER,
                            keyboard_type=ft.KeyboardType.NUMBER,
                            on_blur=lambda e: (
                                set_retry_count(e.control.value or "5"),
                                persist(retry_count=clamp_int(e.control.value or "5", 5, 0, 15)),
                            ),
                        ),
                    ),
                    tile(
                        "Rate limit (KB/s)",
                        "0 = unlimited.",
                        ft.TextField(
                            value=rate_limit,
                            width=72,
                            dense=True,
                            text_align=ft.TextAlign.CENTER,
                            keyboard_type=ft.KeyboardType.NUMBER,
                            on_blur=lambda e: (
                                set_rate_limit(e.control.value or "0"),
                                persist(rate_limit_kbps=clamp_int(e.control.value or "0", 0, 0, 100000)),
                            ),
                        ),
                    ),
                    tile(
                        "Write subtitles",
                        "Ask yt-dlp for subtitles when available.",
                        ft.Switch(
                            value=write_subs,
                            on_change=lambda e: (
                                set_write_subs(e.control.value),
                                persist(write_subtitles=e.control.value),
                            ),
                        ),
                    ),
                    tile(
                        "Clipboard auto-paste",
                        "Detect video URLs when the app resumes.",
                        ft.Switch(
                            value=clipboard_auto,
                            on_change=lambda e: (
                                set_clipboard_auto(e.control.value),
                                persist(clipboard_auto_paste=e.control.value),
                            ),
                        ),
                    ),
                ),
                section(
                    "Background",
                    tile(
                        "Notifications",
                        "Progress and completion (needs flet-notifications on device).",
                        ft.Switch(
                            value=notifications_on,
                            on_change=lambda e: (
                                set_notifications_on(e.control.value),
                                persist(notifications_enabled=e.control.value),
                                (
                                    on_request_notification_permission()
                                    if e.control.value and on_request_notification_permission
                                    else None
                                ),
                            ),
                        ),
                    ),
                    tile(
                        "Background downloads",
                        "Keep workers running while the app is open.",
                        ft.Switch(
                            value=background_on,
                            on_change=lambda e: (
                                set_background_on(e.control.value),
                                persist(background_downloads_enabled=e.control.value),
                            ),
                        ),
                    ),
                ),
                section(
                    "Storage",
                    ft.Text(
                        f"Data: {data_dir or '(app storage)'}",
                        size=11,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                        font_family=FONT_BODY,
                    ),
                    ft.OutlinedButton(
                        content="Clear finished download tasks",
                        icon=ft.Icons.CLEANING_SERVICES_OUTLINED,
                        on_click=lambda e: on_clear_finished and on_clear_finished(),
                        disabled=on_clear_finished is None,
                    ),
                ),
                section(
                    "About",
                    ft.Text(f"Vidsaver v{APP_VERSION}", size=13, font_family=FONT_BODY),
                    ft.TextButton(
                        content="GitHub project",
                        url=REPO_URL,
                        icon=ft.Icons.OPEN_IN_NEW,
                    ),
                ),
            ],
            spacing=20,
            scroll=ft.ScrollMode.ADAPTIVE,
        ),
        padding=16,
        expand=True,
    )
