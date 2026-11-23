"""
main.py - Vidsaver app entry point.
"""

import asyncio
from datetime import datetime
import os
import tempfile
import time

import flet as ft

VIDEO_EXTENSIONS = (".mp4", ".mkv", ".mov", ".avi", ".webm", ".m4v", ".3gp")

VIDEO_DOMAINS = (
    "tiktok.com",
    "vm.tiktok.com",
    "vt.tiktok.com",
    "instagram.com",
    "youtube.com",
    "youtu.be",
    "twitter.com",
    "x.com",
    "facebook.com",
    "fb.com",
)


def is_android_page(page: ft.Page) -> bool:
    platform = getattr(page, "platform", None)
    platform_value = getattr(platform, "value", platform)
    return platform == ft.PagePlatform.ANDROID or platform_value == "android"


def is_video_url(text: str) -> bool:
    if not text:
        return False
    value = text.strip()
    return value.startswith(("http://", "https://")) and any(
        domain in value for domain in VIDEO_DOMAINS
    )


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


# HomeView lives in views/home_view.py (Phase 3)


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

    analysis, set_analysis = ft.use_state(None)
    quality_label, set_quality_label = ft.use_state("Best available")
    tasks_tick, set_tasks_tick = ft.use_state(0)

    refresh_trigger, set_refresh_trigger = ft.use_state(0)
    scroll_offset, set_scroll_offset = ft.use_state(0)

    def sync_page_ui():
        if page.appbar:
            page.appbar.visible = not playing_file

        if playing_file:
            page.navigation_bar = None
        else:
            from components.bottom_navigation import build_navigation_bar

            mgr = getattr(page, "_download_manager", None)
            badge = mgr.active_count() if mgr else 0
            page.navigation_bar = build_navigation_bar(
                selected_index=active_tab,
                on_change=lambda e: set_active_tab(e.control.selected_index),
                downloading_badge=badge,
            )
        page.update()

    ft.use_effect(sync_page_ui, dependencies=[playing_file, active_tab, tasks_tick])

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
            # Flet 1.0.0: show SnackBar via overlay.append + open=True + page.update()
            snack = ft.SnackBar(
                content=ft.Text("Video download complete"),
                open=True,
                duration=2500,
                behavior=ft.SnackBarBehavior.FLOATING,
                margin=ft.Margin(left=16, top=0, right=16, bottom=10),
            )
            page.overlay.append(snack)
            page.update()


    def bump_tasks(_n=None):
        # Force Downloading tab / badge to refresh (counter on page avoids stale closure)
        n = int(getattr(page, "_tasks_tick_counter", 0)) + 1
        setattr(page, "_tasks_tick_counter", n)
        set_tasks_tick(n)

    def get_download_manager():
        mgr = getattr(page, "_download_manager", None)
        if mgr is not None:
            return mgr
        from services.download_manager import DownloadManager

        def staging():
            directory, _ = ensure_storage_paths(page)
            return directory

        cookie_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cookies.txt")
        settings = getattr(page, "_app_settings", None)
        max_c = getattr(settings, "max_concurrent", 1) if settings else 1

        def on_task_changed(task):
            # Bump tick on UI thread so DownloadingView re-renders
            try:
                page.loop.call_soon_threadsafe(bump_tasks)
                from models.download_state import DownloadState

                state = getattr(task, "state", None)

                def _notify_ui():
                    nsvc = getattr(page, "_notification_service", None)
                    if nsvc is None:
                        return
                    active = 0
                    mgr2 = getattr(page, "_download_manager", None)
                    if mgr2:
                        active = sum(
                            1
                            for t in mgr2.list_tasks()
                            if t.is_active or t.state is DownloadState.PENDING
                        )
                    if state is DownloadState.DOWNLOADING and active:
                        asyncio.create_task(
                            nsvc.start_download_session(task.title or "Vidsaver")
                        )
                        pct = task.progress.percent
                        body = f"{task.title or 'Download'}: {pct:.0f}%" if pct is not None else (task.title or "Downloading…")
                        asyncio.create_task(nsvc.update_progress(body))
                    elif state is DownloadState.COMPLETED:
                        asyncio.create_task(nsvc.notify_completed(task.title or "Video saved"))
                        if active <= 1:
                            asyncio.create_task(nsvc.stop_download_session())
                    elif state in (DownloadState.FAILED, DownloadState.CANCELLED):
                        if active <= 1:
                            asyncio.create_task(nsvc.stop_download_session())

                page.loop.call_soon_threadsafe(_notify_ui)

                if state is DownloadState.COMPLETED:

                    def _refresh():
                        n = int(getattr(page, "_lib_refresh", 0)) + 1
                        setattr(page, "_lib_refresh", n)
                        set_refresh_trigger(n)

                    page.loop.call_soon_threadsafe(_refresh)
            except Exception:
                pass

        def publish_sync(result: dict):
            # Bridge async publish into worker via concurrent future
            import concurrent.futures

            fut: concurrent.futures.Future = concurrent.futures.Future()

            async def _pub():
                try:
                    _, metadata = ensure_storage_paths(page)
                    ok, err = await publish_download_result(page, result, metadata)
                    fut.set_result((ok, err))
                except Exception as exc:
                    fut.set_result((False, str(exc)))

            try:
                page.loop.call_soon_threadsafe(lambda: asyncio.create_task(_pub()))
                return fut.result(timeout=300)
            except Exception as exc:
                return False, str(exc)

        from config.constants import TASKS_DB_FILENAME
        from services.task_store import TaskStore

        data_dir = os.environ.get("FLET_APP_STORAGE_DATA") or os.getcwd()
        store = TaskStore(os.path.join(data_dir, TASKS_DB_FILENAME))

        def ydl_option_provider():
            s = getattr(page, "_app_settings", None)
            if s is None:
                return {}
            rate = int(getattr(s, "rate_limit_kbps", 0) or 0)
            return {
                "retries": int(getattr(s, "retry_count", 5) or 5),
                "concurrent_fragments": int(getattr(s, "concurrent_fragments", 4) or 4),
                "rate_limit": str(rate * 1024) if rate > 0 else None,
                "writesubtitles": bool(getattr(s, "write_subtitles", False)),
            }

        mgr = DownloadManager(
            max_concurrent=max_c,
            cookie_path=cookie_path,
            get_staging_dir=staging,
            on_task_changed=on_task_changed,
            publish_result=publish_sync,
            task_store=store,
            ydl_option_provider=ydl_option_provider,
        )
        mgr.restore_from_store()
        setattr(page, "_download_manager", mgr)
        setattr(page, "_task_store", store)
        bump_tasks()
        return mgr

    def start_download(url: str, format_selector: str | None = None):
        if not url:
            set_status_text("Please enter a valid URL!")
            return

        if not is_video_url(url):
            set_status_text("Not a recognized or supported video link.")
            return

        mgr = get_download_manager()
        settings = getattr(page, "_app_settings", None)
        if settings:
            mgr.set_max_concurrent(getattr(settings, "max_concurrent", 1))

        title = ""
        platform = "Video"
        thumb = ""
        if analysis and isinstance(analysis, dict) and analysis.get("ok"):
            title = analysis.get("title") or ""
            platform = analysis.get("platform") or "Video"
            thumb = analysis.get("thumbnail") or ""

        task = mgr.enqueue(
            url,
            format_selector=format_selector,
            title=title,
            platform=platform,
            thumbnail_url=thumb,
        )
        set_status_text(f"Queued: {title or url}")
        bump_tasks()
        # Switch user attention to Downloading tab
        set_active_tab(1)


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
        from views.home_view import HomeView

        async def do_analyze(u: str):
            from downloader import analyze_media

            cookie_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cookies.txt")
            result = await asyncio.to_thread(analyze_media, u, cookie_path)
            set_analysis(result)
            if result and result.get("ok") and not result.get("is_playlist"):
                set_quality_label("Best available")
                setattr(page, "_selected_format_selector", None)
                settings = getattr(page, "_app_settings", None)
                default_q = getattr(settings, "default_quality", "best") if settings else "best"
                if default_q and default_q != "best":
                    # Match e.g. "1080" or "1080p" against option heights
                    digits = "".join(c for c in str(default_q) if c.isdigit())
                    if digits:
                        want = int(digits)
                        for opt in result.get("quality_options") or []:
                            if opt.get("height") == want:
                                set_quality_label(opt.get("label") or f"{want}p")
                                setattr(
                                    page,
                                    "_selected_format_selector",
                                    f"bv*[height<={want}]+ba/b[height<={want}]/best",
                                )
                                break
            return result

        def select_quality(opt: dict):
            set_quality_label(opt.get("label") or "Best available")
            height = opt.get("height") or 0
            fid = opt.get("format_id") or ""
            if opt.get("audio_only") or height == -1:
                setattr(page, "_selected_format_selector", "bestaudio/best")
            elif not height:
                setattr(page, "_selected_format_selector", None)
            elif fid:
                setattr(
                    page,
                    "_selected_format_selector",
                    f"{fid}+bestaudio/best[height<={height}]/best",
                )
            else:
                setattr(
                    page,
                    "_selected_format_selector",
                    f"bv*[height<={height}]+ba/b[height<={height}]/best",
                )

        content_view = HomeView(
            page=page,
            status_text_val=status_text,
            progress_val=progress_val,
            progress_visible=progress_visible,
            download_disabled=download_disabled,
            on_download=start_download,
            on_analyze=do_analyze,
            analysis=analysis,
            selected_quality_label=quality_label,
            on_select_quality=select_quality,
            on_clear_analysis=lambda: set_analysis(None),
        )
    elif active_tab == 1:
        from views.downloading_view import DownloadingView

        mgr = getattr(page, "_download_manager", None)
        tasks = mgr.list_tasks() if mgr else []
        # reference tasks_tick so UI refreshes when downloads progress
        _ = tasks_tick
        content_view = DownloadingView(
            tasks=tasks,
            on_cancel=lambda tid: (mgr.cancel(tid) if mgr else None, bump_tasks()),
            on_retry=lambda tid: (mgr.retry(tid) if mgr else None, bump_tasks()),
        )
    elif active_tab == 2:
        from library import LibraryView

        directory, metadata = ensure_storage_paths(page)

        async def share_item(file_name: str, url: str):
            if not url:
                return
            try:
                # Prefer system share when Share service exists
                share = getattr(page, "_share", None)
                if share is None and hasattr(ft, "Share"):
                    share = ft.Share()
                    setattr(page, "_share", share)
                    try:
                        page.services.append(share)
                    except Exception:
                        pass
                if share is not None and hasattr(share, "share"):
                    await share.share(url, subject=file_name)
                    return
            except Exception:
                pass
            try:
                clip = getattr(page, "_clipboard", None)
                if clip is None:
                    clip = ft.Clipboard()
                    setattr(page, "_clipboard", clip)
                await clip.set(url)
                snack = ft.SnackBar(
                    content=ft.Text("Link copied to clipboard"),
                    open=True,
                    duration=2000,
                    behavior=ft.SnackBarBehavior.FLOATING,
                )
                page.overlay.append(snack)
                page.update()
            except Exception:
                pass

        content_view = LibraryView(
            download_dir=directory,
            metadata_path=metadata,
            on_play=set_playing_file,
            initial_scroll=scroll_offset,
            on_scroll_change=set_scroll_offset,
            refresh_trigger=refresh_trigger,
            delete_from_storage=lambda info: delete_saved_video(page, info),
            sync_from_storage=lambda: sync_saved_videos(page, metadata),
            on_share=lambda fn, u: asyncio.create_task(share_item(fn, u)),
        )
    else:
        from config.settings import AppSettings, SettingsRepository
        from views.settings_view import SettingsView

        data_dir = os.environ.get("FLET_APP_STORAGE_DATA") or os.getcwd()
        repo = SettingsRepository(data_dir)
        app_settings = getattr(page, "_app_settings", None)
        if app_settings is None:
            app_settings = repo.load()
            setattr(page, "_app_settings", app_settings)
            setattr(page, "_settings_repo", repo)

        def on_settings_changed(s):
            setattr(page, "_app_settings", s)
            repo.save(s)
            try:
                from config.theme import apply_theme_mode

                apply_theme_mode(page, s.theme_mode)
            except Exception:
                pass
            nsvc = getattr(page, "_notification_service", None)
            if nsvc is not None:
                nsvc.set_enabled(getattr(s, "notifications_enabled", True))
            page.update()

        def clear_finished():
            mgr = getattr(page, "_download_manager", None)
            if mgr is None:
                return
            mgr.clear_finished()
            bump_tasks()

        def request_notif_perm():
            nsvc = getattr(page, "_notification_service", None)
            if nsvc is None:
                return
            asyncio.create_task(nsvc.request_permission())

        content_view = SettingsView(
            settings=app_settings,
            on_settings_changed=on_settings_changed,
            on_clear_finished=clear_finished,
            data_dir=data_dir,
            on_request_notification_permission=request_notif_perm,
        )

    return ft.SafeArea(content=content_view, expand=True)


async def main(page: ft.Page):
    await init_storage_paths(page)
    ensure_media_scanner(page)

    try:
        from services.notification_service import NotificationService

        nsvc = NotificationService(page)
        nsvc.attach(page)
        setattr(page, "_notification_service", nsvc)
        settings = getattr(page, "_app_settings", None)
        if settings is not None:
            nsvc.set_enabled(getattr(settings, "notifications_enabled", True))
    except Exception:
        pass

    page.title = "Vidsaver"
    page.padding = 0
    page.spacing = 0
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.navigation_bar = None

    # Theme + fonts (Phase 2)
    data_dir = os.environ.get("FLET_APP_STORAGE_DATA") or os.getcwd()
    try:
        from config.settings import SettingsRepository
        from config.theme import PRIMARY, apply_theme_mode

        repo = SettingsRepository(data_dir)
        app_settings = repo.load()
        setattr(page, "_app_settings", app_settings)
        setattr(page, "_settings_repo", repo)
        apply_theme_mode(page, app_settings.theme_mode)
        page.appbar = ft.AppBar(
            title=ft.Text("Vidsaver", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
            center_title=True,
            bgcolor=PRIMARY,
        )
    except Exception:
        page.theme = ft.Theme(
            scrollbar_theme=ft.ScrollbarTheme(
                thickness=6,
                radius=4,
                interactive=True,
            )
        )
        page.appbar = ft.AppBar(
            title=ft.Text("Vidsaver", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
            center_title=True,
            bgcolor=ft.Colors.BLUE_700,
        )

    page.render(App, page=page)


ft.run(main)
