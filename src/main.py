"""
main.py - Vidsaver app entry point.
"""

import asyncio
from datetime import datetime
import os
import tempfile
import time
from urllib.parse import urlparse

import flet as ft
import theme

VIDEO_EXTENSIONS = (".mp4", ".mkv", ".mov", ".avi", ".webm", ".m4v", ".3gp")

VIDEO_DOMAINS = (
    "tiktok.com",
    "vm.tiktok.com",
    "vt.tiktok.com",
    "instagram.com",
    "instagr.am",
    "youtube.com",
    "youtu.be",
    "twitter.com",
    "x.com",
    "t.co",
    "facebook.com",
    "fb.com",
    "fb.watch",
    "snapchat.com",
    "reddit.com",
    "v.redd.it",
    "redd.it",
    "pinterest.com",
    "pin.it",
    "threads.net",
    "threads.com",
    "vimeo.com",
    "dailymotion.com",
    "dai.ly",
    "twitch.tv",
    "linkedin.com",
    "likee.video",
    "snackvideo.com",
    "bilibili.com",
    "b23.tv",
)


def is_android_page(page: ft.Page) -> bool:
    platform = getattr(page, "platform", None)
    platform_value = getattr(platform, "value", platform)
    return platform == ft.PagePlatform.ANDROID or platform_value == "android"


def is_http_url(text: str) -> bool:
    if not text:
        return False
    parsed = urlparse(text.strip())
    return parsed.scheme.lower() in ("http", "https") and bool(parsed.netloc)


def is_video_url(text: str) -> bool:
    if not is_http_url(text):
        return False
    value = text.strip().lower()
    return any(domain in value for domain in VIDEO_DOMAINS)


def ensure_storage_paths(page: ft.Page):
    download_dir = getattr(page, "_download_dir", None)
    metadata_path = getattr(page, "_metadata_path", None)
    if download_dir and metadata_path:
        return download_dir, metadata_path

    # FLET_APP_STORAGE_DATA is the writable data dir in built apps and flet run
    # (0.86+: app bundle is read-only, cwd = data dir in both modes)
    data_dir = os.environ.get("FLET_APP_STORAGE_DATA") or os.getcwd()
    metadata_path = os.path.join(data_dir, "metadata.json")
    if is_android_page(page):
        download_dir = os.path.join(tempfile.gettempdir(), "vidsaver-staging")
    else:
        # Use os.environ.get to avoid KeyError on non-Windows platforms
        user_profile = os.environ.get("USERPROFILE") or os.environ.get("HOME") or ""
        download_dir = (
            os.path.join(user_profile, "Downloads", "VidSaver")
            if user_profile
            else "./downloads"
        )

    os.makedirs(download_dir, exist_ok=True)
    setattr(page, "_download_dir", download_dir)
    setattr(page, "_metadata_path", metadata_path)
    return download_dir, metadata_path


async def init_storage_paths(page: ft.Page):
    """Initialize stable metadata and temporary staging paths."""
    download_dir = getattr(page, "_download_dir", None)
    metadata_path = getattr(page, "_metadata_path", None)
    if download_dir and metadata_path:
        return download_dir, metadata_path

    # FLET_APP_STORAGE_DATA is the writable data dir in both built apps and
    # flet run dev mode (0.86+: app bundle is read-only; cwd = data dir).
    data_dir = os.environ.get("FLET_APP_STORAGE_DATA") or os.getcwd()
    if is_android_page(page):
        try:
            storage_paths = getattr(page, "storage_paths", None)
            if storage_paths:
                temp_dir = await storage_paths.get_temporary_directory()
            else:
                sp = ft.StoragePaths()
                page.services.append(sp)
                temp_dir = await sp.get_temporary_directory()
        except Exception:
            temp_dir = tempfile.gettempdir()
        metadata_path = os.path.join(data_dir, "metadata.json")
        download_dir = os.path.join(temp_dir, "vidsaver-staging")
    else:
        metadata_path = os.path.join(data_dir, "metadata.json")
        # Use os.environ.get to avoid KeyError on non-Windows platforms
        user_profile = os.environ.get("USERPROFILE") or os.environ.get("HOME") or ""
        download_dir = (
            os.path.join(user_profile, "Downloads", "VidSaver")
            if user_profile
            else "./downloads"
        )

    os.makedirs(os.path.dirname(metadata_path), exist_ok=True)
    os.makedirs(download_dir, exist_ok=True)
    setattr(page, "_download_dir", download_dir)
    setattr(page, "_metadata_path", metadata_path)
    return download_dir, metadata_path


def ensure_media_scanner(page: ft.Page):
    """Initialize the local media service on Android only."""
    if hasattr(page, "_media_scanner"):
        return getattr(page, "_media_scanner")

    if not is_android_page(page):
        setattr(page, "_media_scanner", None)
        setattr(page, "_media_scanner_error", "")
        return None

    try:
        from flet_media_scanner import MediaScanner

        scanner = MediaScanner()
        page.services.append(scanner)
        setattr(page, "_media_scanner", scanner)
        setattr(page, "_media_scanner_error", "")
        page.update()
        print("[VidSaver] MediaStore service initialized")
    except Exception as e:
        setattr(page, "_media_scanner_error", str(e))
        print(f"[VidSaver] MediaStore service init failed: {e}")
        setattr(page, "_media_scanner", None)

    return getattr(page, "_media_scanner")


def get_clipboard(page: ft.Page) -> ft.Clipboard:
    """Return a stable Clipboard service instance (created once per session)."""
    clipboard = getattr(page, "_clipboard", None)
    if clipboard is None:
        clipboard = ft.Clipboard()
        setattr(page, "_clipboard", clipboard)
    return clipboard


async def publish_download_result(page: ft.Page, download_result: dict, metadata_path: str):
    """Publish staged downloads to MediaStore on Android and update metadata."""
    from downloader import load_metadata, save_metadata

    if not download_result or not download_result.get("paths"):
        return False, "No video file was saved."

    meta = load_metadata(metadata_path)
    published = 0
    last_error = ""

    for path in download_result["paths"]:
        file_name = os.path.basename(path)
        size = os.path.getsize(path) if os.path.exists(path) else 0
        entry = {
            "platform": download_result["platform"],
            "url": download_result["url"],
            "date": download_result["date"],
            "created_at": time.time(),
            "source_path": path,
            "size": size,
        }

        android = is_android_page(page)
        scanner = ensure_media_scanner(page) if android else None
        if android and scanner is None:
            init_error = getattr(page, "_media_scanner_error", "")
            last_error = (
                f"MediaStore service is not available: {init_error}"
                if init_error
                else "MediaStore service is not available."
            )
            continue

        if scanner is not None:
            result = await scanner.save_video(path, file_name=file_name, album="Vidsaver")
            if not result.success:
                last_error = result.error or "MediaStore save failed."
                continue

            display_name = result.display_name or file_name
            entry.update(
                {
                    "content_uri": result.content_uri,
                    "display_name": display_name,
                    "mime_type": result.mime_type,
                    "relative_path": result.relative_path,
                    "size": result.size or size,
                }
            )
            meta[display_name] = entry
            try:
                os.remove(path)
            except Exception:
                pass
        else:
            meta[file_name] = entry

        published += 1

    if published:
        save_metadata(metadata_path, meta)
        return True, ""
    return False, last_error or "Unable to publish video to Gallery."


async def delete_saved_video(page: ft.Page, info: dict) -> bool:
    """Delete a saved video from Android MediaStore or local filesystem."""
    content_uri = info.get("content_uri") or ""
    source_path = info.get("source_path") or info.get("file_path") or ""

    if is_android_page(page) and content_uri:
        scanner = ensure_media_scanner(page)
        if scanner is None:
            return False
        return await scanner.delete_video(content_uri)

    if source_path and os.path.exists(source_path):
        try:
            os.remove(source_path)
            return True
        except Exception:
            return False

    return not content_uri and not source_path


async def sync_saved_videos(page: ft.Page, metadata_path: str) -> None:
    """Restore app metadata from Android MediaStore after app updates."""
    if not is_android_page(page):
        return

    scanner = ensure_media_scanner(page)
    if scanner is None:
        return

    from downloader import load_metadata, save_metadata

    videos = await scanner.list_videos(album="Vidsaver")
    if not videos:
        return

    meta = load_metadata(metadata_path)
    changed = False
    for video in videos:
        display_name = str(video.get("display_name") or "")
        content_uri = str(video.get("content_uri") or "")
        if not display_name or not content_uri:
            continue

        created_at = float(video.get("date_added") or video.get("date_modified") or time.time())
        existing = meta.get(display_name, {})
        restored = {
            **existing,
            "platform": existing.get("platform") or "Video",
            "url": existing.get("url") or "",
            "date": existing.get("date")
            or datetime.fromtimestamp(created_at).strftime("%d %b %Y"),
            "created_at": existing.get("created_at") or created_at,
            "content_uri": content_uri,
            "display_name": display_name,
            "mime_type": str(video.get("mime_type") or "video/mp4"),
            "relative_path": str(video.get("relative_path") or "Movies/Vidsaver"),
            "size": int(video.get("size") or existing.get("size") or 0),
        }
        if meta.get(display_name) != restored:
            meta[display_name] = restored
            changed = True

    if changed:
        save_metadata(metadata_path, meta)


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

        status_controls: list[ft.Control] = [
            ft.Row(
                controls=[
                    status_icon,
                    ft.Text(
                        value=status_text_val or "Working...",
                        style=ft.TextStyle(
                            font_family=theme.FONT_BODY_SEMIBOLD,
                            size=14,
                            weight=ft.FontWeight.W_600,
                            color=theme.PILL_RED if is_error else ft.Colors.ON_SURFACE,
                        ),
                        max_lines=2,
                        overflow=ft.TextOverflow.ELLIPSIS,
                        expand=True,
                    ),
                    theme.status_pill(pill_label, pill_color),
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )
        ]
        if progress_visible:
            status_controls.append(
                ft.ProgressBar(
                    height=8,
                    value=progress_val,
                    color=pill_color,
                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                    border_radius=ft.BorderRadius.all(theme.RADIUS_PILL),
                )
            )
            if progress_val is not None:
                status_controls.append(
                    ft.Text(
                        f"{float(progress_val) * 100:.0f} %",
                        style=theme.data_style(ft.Colors.ON_SURFACE_VARIANT),
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
            content=ft.Column(controls=status_controls, spacing=10),
            padding=16,
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
                    border=ft.InputBorder.NONE,
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


@ft.component
def App(page: ft.Page):
    """Root declarative App component."""
    active_tab, set_active_tab = ft.use_state(0)
    playing_file, set_playing_file = ft.use_state(None)

    status_text, set_status_text = ft.use_state("")
    progress_val, set_progress_val = ft.use_state(None)
    progress_visible, set_progress_visible = ft.use_state(False)
    download_disabled, set_download_disabled = ft.use_state(False)
    download_completed, set_download_completed = ft.use_state(False)

    refresh_trigger, set_refresh_trigger = ft.use_state(0)
    scroll_offset, set_scroll_offset = ft.use_state(0)

    def sync_page_ui():
        if page.appbar:
            page.appbar.visible = not playing_file

        if playing_file:
            page.navigation_bar = None
        else:
            page.navigation_bar = ft.NavigationBar(
                selected_index=active_tab,
                on_change=lambda e: set_active_tab(e.control.selected_index),
                destinations=[
                    ft.NavigationBarDestination(
                        icon=ft.Icons.HOME_OUTLINED,
                        selected_icon=ft.Icons.HOME_ROUNDED,
                        label="Home",
                    ),
                    ft.NavigationBarDestination(
                        icon=ft.Icons.VIDEO_LIBRARY_OUTLINED,
                        selected_icon=ft.Icons.VIDEO_LIBRARY_ROUNDED,
                        label="Downloads",
                    ),
                ],
            )
        page.update()

    ft.use_effect(sync_page_ui, dependencies=[playing_file, active_tab])

    def set_download_busy(message: str):
        set_download_completed(False)
        set_progress_val(None)
        set_progress_visible(True)
        set_download_disabled(True)
        set_status_text(message)

    def finish_download(is_done: bool):
        set_progress_visible(False)
        set_download_disabled(False)
        set_refresh_trigger(lambda prev: prev + 1)
        if is_done:
            page.show_dialog(
                ft.SnackBar(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.CHECK_CIRCLE, size=18, color=theme.PILL_GREEN),
                            ft.Text(
                                "Video saved to Gallery",
                                style=theme.body_md(ft.Colors.ON_SURFACE),
                                expand=True,
                            ),
                        ],
                        spacing=10,
                    ),
                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
                    action="View",
                    on_action=lambda _: set_active_tab(1),
                    duration=3500,
                    behavior=ft.SnackBarBehavior.FLOATING,
                    margin=ft.Margin(left=16, top=0, right=16, bottom=10),
                )
            )

    def start_download(url: str):
        if not url:
            set_status_text("Please enter a valid URL!")
            return

        if not is_http_url(url):
            set_status_text("Not a recognized or supported video link.")
            return

        async def download_flow():
            set_download_busy("Fetching video...")

            directory, metadata = ensure_storage_paths(page)
            cookie_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cookies.txt")
            from downloader import run_download

            had_error = [False]

            # Use default-arg capture to avoid late-binding lambda bugs
            def on_status(message, _set=set_status_text):
                page.loop.call_soon_threadsafe(_set, message)

            def on_progress(value, _set=set_progress_val):
                page.loop.call_soon_threadsafe(_set, value)

            def on_error(message, _had=had_error, _set=set_status_text):
                _had[0] = True
                page.loop.call_soon_threadsafe(set_download_completed, False)
                page.loop.call_soon_threadsafe(_set, f"Error: {message}")

            def on_finish():
                pass

            class DummyPage:
                def update(self):
                    pass

            download_result = await asyncio.to_thread(
                run_download,
                url,
                directory,
                cookie_path,
                metadata,
                on_status,
                on_progress,
                on_finish,
                on_error,
                DummyPage(),
                None,
            )

            is_done = False
            if download_result and not had_error[0]:
                try:
                    ok, error = await publish_download_result(page, download_result, metadata)
                except Exception as exc:
                    ok, error = False, str(exc)
                if ok:
                    engine = (download_result or {}).get("engine", "yt-dlp")
                    set_download_completed(True)
                    set_status_text(f"Video saved to Gallery ({engine}).")
                    is_done = True
                else:
                    set_download_completed(False)
                    set_status_text(f"Error: {error}")

            finish_download(is_done)

        asyncio.create_task(download_flow())

    if playing_file:
        from downloader import load_metadata
        from player import PlayerView

        _, metadata = ensure_storage_paths(page)
        info = load_metadata(metadata).get(playing_file, {})
        playable_path = (
            info.get("content_uri")
            or info.get("source_path")
            or info.get("file_path")
            or playing_file
        )
        content_view = PlayerView(
            file_path=playable_path,
            on_close=lambda e: set_playing_file(None),
        )
    elif active_tab == 0:
        content_view = HomeView(
            status_text_val=status_text,
            progress_val=progress_val,
            progress_visible=progress_visible,
            download_disabled=download_disabled,
            on_download_click=start_download,
            on_open_downloads=lambda: set_active_tab(1),
            page=page,
        )
    else:
        from library import LibraryView

        directory, metadata = ensure_storage_paths(page)
        content_view = LibraryView(
            download_dir=directory,
            metadata_path=metadata,
            on_play=set_playing_file,
            initial_scroll=scroll_offset,
            on_scroll_change=set_scroll_offset,
            refresh_trigger=refresh_trigger,
            delete_from_storage=lambda info: delete_saved_video(page, info),
            sync_from_storage=lambda: sync_saved_videos(page, metadata),
            on_go_home=lambda: set_active_tab(0),
        )

    return ft.SafeArea(content=content_view, expand=True)


async def main(page: ft.Page):
    await init_storage_paths(page)
    ensure_media_scanner(page)

    page.title = "VidSaver"
    page.padding = 0
    page.spacing = 0
    page.fonts = {
        theme.FONT_HEADLINE: "/fonts/SpaceGrotesk-SemiBold.ttf",
        theme.FONT_HEADLINE_BOLD: "/fonts/SpaceGrotesk-Bold.ttf",
        theme.FONT_BODY: "/fonts/Inter-Regular.ttf",
        theme.FONT_BODY_MEDIUM: "/fonts/Inter-Medium.ttf",
        theme.FONT_BODY_SEMIBOLD: "/fonts/Inter-SemiBold.ttf",
    }
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.theme = theme.light_theme()
    page.dark_theme = theme.dark_theme()

    def toggle_theme(_):
        page.theme_mode = (
            ft.ThemeMode.LIGHT
            if page.theme_mode == ft.ThemeMode.DARK
            else ft.ThemeMode.DARK
        )
        page.update()

    page.navigation_bar = None
    page.appbar = ft.AppBar(
        title=ft.Row(
            controls=[
                ft.Text("Vid", style=theme.headline_md()),
                ft.Text("Saver", style=theme.headline_md(ft.Colors.PRIMARY)),
            ],
            spacing=0,
            tight=True,
        ),
        center_title=False,
        bgcolor=ft.Colors.SURFACE,
        elevation=0,
        actions=[
            ft.IconButton(
                icon=ft.Icons.CONTRAST_ROUNDED,
                icon_color=ft.Colors.ON_SURFACE_VARIANT,
                tooltip="Toggle light/dark theme",
                on_click=toggle_theme,
            )
        ],
    )

    page.render(App, page=page)


ft.run(main, assets_dir="assets")
