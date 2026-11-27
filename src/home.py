"""
home.py - Declarative home view component (Nocturnal Studio design).
"""

import asyncio

import flet as ft

from storage import get_clipboard, is_http_url, is_video_url
import theme


@ft.component
def HomeView(
    status_text_val: str,
    progress_val: float | None,
    progress_visible: bool,
    download_disabled: bool,
    on_download_click,
    on_open_downloads,
    page: ft.Page,
):
    """Declarative home view component for downloading videos."""
    from downloader import detect_platform

    url, set_url = ft.use_state("")
    url_ref = ft.use_ref(url)
    url_ref.current = url

    async def try_paste_clipboard(force: bool = False):
        try:
            clip = await get_clipboard(page).get()
            if not clip:
                return
            cleaned = clip.strip()
            current_url = (url_ref.current or "").strip()
            if force and is_http_url(cleaned):
                set_url(cleaned)
            elif is_video_url(cleaned) and cleaned != current_url:
                set_url(cleaned)
        except Exception:
            pass

    def setup_lifecycle():
        def on_lifecycle(e):
            if e.state == ft.AppLifecycleState.RESUME:
                asyncio.create_task(try_paste_clipboard())

        old_handler = page.on_app_lifecycle_state_change
        page.on_app_lifecycle_state_change = on_lifecycle
        return lambda: setattr(page, "on_app_lifecycle_state_change", old_handler)

    ft.use_effect(setup_lifecycle, dependencies=[])

    async def on_url_focus(e):
        if not url:
            await try_paste_clipboard()

    def handle_submit(e):
        if url.strip() and not download_disabled:
            on_download_click(url.strip())

    has_url = bool(url.strip())
    valid_url = is_http_url(url)
    detected_platform = detect_platform(url) if valid_url else ""
    is_error = status_text_val.startswith("Error:")
    is_saved = status_text_val.startswith("Video saved")

    platform_color = theme.PLATFORM_PILL_COLORS.get(detected_platform, theme.PILL_CORAL)
    platform_badge = (
        ft.Row(
            controls=[
                theme.status_pill(detected_platform, platform_color),
                ft.Text(
                    "Ready to download",
                    style=theme.body_sm(ft.Colors.ON_SURFACE_VARIANT),
                ),
            ],
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        if valid_url
        else None
    )

    status_card = None
    if progress_visible or status_text_val:
        if is_error:
            pill_label, pill_color = "Error", theme.PILL_RED
            status_icon = ft.Icon(ft.Icons.ERROR_OUTLINE_ROUNDED, size=18, color=theme.PILL_RED)
            card_gradient = None
            card_border = ft.Colors.with_opacity(0.4, theme.PILL_RED)
        elif is_saved:
            pill_label, pill_color = "Saved", theme.PILL_GREEN
            status_icon = ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE_ROUNDED, size=18, color=theme.PILL_GREEN)
            card_gradient = None
            card_border = None
        else:
            pill_label = "Downloading" if progress_val is not None else "Preparing"
            pill_color = theme.PILL_CORAL
            status_icon = ft.Icon(ft.Icons.DOWNLOADING_ROUNDED, size=18, color=theme.PILL_CORAL)
            card_border = None
            if progress_val is not None and progress_val > 0:
                p = min(max(float(progress_val), 0.0), 1.0)
                fill = ft.Colors.with_opacity(0.08, theme.PILL_CORAL)
                card_gradient = ft.LinearGradient(
                    begin=ft.Alignment.CENTER_LEFT,
                    end=ft.Alignment.CENTER_RIGHT,
                    colors=[fill, fill, ft.Colors.TRANSPARENT, ft.Colors.TRANSPARENT],
                    stops=[0, p, p, 1],
                )
            else:
                card_gradient = None

        if is_error or is_saved:
            header_row = ft.Row(
                controls=[
                    status_icon,
                    ft.Text(
                        value=status_text_val or "Working...",
                        style=ft.TextStyle(
                            font_family=theme.FONT_BODY_SEMIBOLD,
                            size=13.5,
                            weight=ft.FontWeight.W_600,
                            color=theme.PILL_RED if is_error else ft.Colors.ON_SURFACE,
                        ),
                        max_lines=2,
                        overflow=ft.TextOverflow.ELLIPSIS,
                        expand=True,
                    ),
                    theme.status_pill(pill_label, pill_color),
                ],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )
        elif progress_val is not None:
            header_row = ft.Row(
                controls=[
                    status_icon,
                    theme.status_pill(pill_label, pill_color),
                    ft.Container(expand=True),
                    ft.Text(
                        f"{float(progress_val) * 100:.0f} %",
                        style=theme.data_style(ft.Colors.ON_SURFACE_VARIANT),
                    ),
                ],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )
        else:
            header_row = ft.Row(
                controls=[
                    status_icon,
                    ft.Text(
                        value=status_text_val or "Working...",
                        style=ft.TextStyle(
                            font_family=theme.FONT_BODY_SEMIBOLD,
                            size=13.5,
                            weight=ft.FontWeight.W_600,
                            color=ft.Colors.ON_SURFACE,
                        ),
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS,
                        expand=True,
                    ),
                    theme.status_pill(pill_label, pill_color),
                ],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )

        status_controls: list[ft.Control] = [header_row]
        if progress_visible:
            status_controls.append(
                ft.ProgressBar(
                    height=6,
                    value=progress_val,
                    color=pill_color,
                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                    border_radius=ft.BorderRadius.all(theme.RADIUS_PILL),
                )
            )
        if is_saved:
            status_controls.append(
                ft.Row(
                    controls=[
                        ft.TextButton(
                            "Open Downloads",
                            icon=ft.Icons.VIDEO_LIBRARY_ROUNDED,
                            on_click=lambda _: on_open_downloads(),
                        )
                    ],
                    alignment=ft.MainAxisAlignment.END,
                )
            )
        status_card = theme.surface_card(
            content=ft.Column(controls=status_controls, spacing=8),
            padding=12,
            border_color=card_border,
            gradient=card_gradient,
        )

    suffix_btn = (
        ft.IconButton(
            icon=ft.Icons.CLOSE_ROUNDED,
            icon_size=20,
            icon_color=ft.Colors.ON_SURFACE_VARIANT,
            tooltip="Clear link",
            on_click=lambda _: set_url(""),
        )
        if has_url
        else ft.IconButton(
            icon=ft.Icons.CONTENT_PASTE_ROUNDED,
            icon_size=20,
            icon_color=ft.Colors.ON_SURFACE_VARIANT,
            tooltip="Paste from clipboard",
            on_click=lambda _: asyncio.create_task(try_paste_clipboard(force=True)),
        )
    )

    url_input = theme.inset_input_box(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.LINK_ROUNDED, size=20, color=ft.Colors.ON_SURFACE_VARIANT),
                ft.TextField(
                    value=url,
                    on_change=lambda e: set_url(e.control.value),
                    on_focus=lambda e: asyncio.create_task(on_url_focus(e)),
                    on_submit=handle_submit,
                    hint_text="Paste video URL (https://...)",
                    hint_style=theme.body_md(ft.Colors.ON_SURFACE_VARIANT),
                    text_style=theme.body_lg(),
                    border=ft.NoInputBorder(),
                    expand=True,
                ),
                suffix_btn,
            ],
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding(left=14, right=6, top=4, bottom=4),
        radius=theme.RADIUS_CONTROL + 2,
    )

    services_row = ft.Column(
        controls=[
            ft.Text(
                "SUPPORTED PLATFORMS",
                style=theme.label_md(ft.Colors.ON_SURFACE_VARIANT),
                text_align=ft.TextAlign.CENTER,
            ),
            ft.Row(
                controls=[
                    ft.Row(
                        [
                            ft.Icon(icon, size=16, color=ft.Colors.ON_SURFACE_VARIANT),
                            ft.Text(name, style=theme.body_sm(ft.Colors.ON_SURFACE_VARIANT)),
                        ],
                        spacing=5,
                        tight=True,
                    )
                    for name, icon in [
                        ("YouTube", ft.Icons.SMART_DISPLAY_OUTLINED),
                        ("TikTok", ft.Icons.MUSIC_NOTE_OUTLINED),
                        ("Instagram", ft.Icons.PHOTO_CAMERA_OUTLINED),
                        ("Facebook", ft.Icons.PUBLIC_OUTLINED),
                        ("X / Twitter", ft.Icons.TAG_ROUNDED),
                        ("Snapchat", ft.Icons.BOLT_OUTLINED),
                    ]
                ],
                wrap=True,
                spacing=18,
                run_spacing=8,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ],
        spacing=10,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        opacity=0.75,
    )

    main_column = ft.Column(
        col={"xs": 12, "sm": 10, "md": 7, "lg": 5},
        controls=[
            ft.Column(
                controls=[
                    ft.Text(
                        spans=[
                            ft.TextSpan("Save any ", style=theme.headline_xl()),
                            ft.TextSpan("video", style=theme.headline_xl(ft.Colors.PRIMARY)),
                        ],
                    ),
                    ft.Text(
                        "Drop a link below to save it straight to your device.",
                        style=theme.body_md(ft.Colors.ON_SURFACE_VARIANT),
                    ),
                ],
                spacing=6,
            ),
            theme.surface_card(
                content=ft.Column(
                    controls=[
                        url_input,
                        *([platform_badge] if platform_badge else []),
                        ft.FilledButton(
                            "Downloading..." if download_disabled else "Download Video",
                            icon=ft.Icons.DOWNLOAD_ROUNDED,
                            height=48,
                            disabled=download_disabled,
                            on_click=handle_submit,
                        ),
                    ],
                    spacing=14,
                    horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                ),
                padding=18,
            ),
            *([status_card] if status_card else []),
            ft.Container(content=services_row, padding=ft.Padding(top=12, bottom=4, left=0, right=0)),
            ft.Container(
                content=ft.Text(
                    "VidSaver • Made by Fazi Gondal",
                    style=theme.label_md(ft.Colors.ON_SURFACE_VARIANT),
                    text_align=ft.TextAlign.CENTER,
                    opacity=0.65,
                ),
                padding=ft.Padding(top=4, bottom=8, left=0, right=0),
                alignment=ft.Alignment(0, 0),
            ),
        ],
        spacing=18,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
    )

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.ResponsiveRow(
                    controls=[main_column],
                    alignment=ft.MainAxisAlignment.CENTER,
                )
            ],
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True,
        ),
        padding=ft.Padding(left=20, right=20, top=24, bottom=20),
        expand=True,
    )
