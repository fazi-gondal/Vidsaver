"""App shell with declarative Router, responsive nav, and lazy service warm-up."""

from __future__ import annotations

import asyncio
import logging
import os
import threading
import time

import flet as ft

from vidsaver.config.constants import APP_TITLE
from vidsaver.models.video import VideoEntry
from vidsaver.services.download_service import DownloadService
from vidsaver.services.library_service import LibraryService
from vidsaver.services.media_store import MediaStoreService
from vidsaver.ui.components.sidebar import Sidebar
from vidsaver.ui.components.toast import show_toast
from vidsaver.ui.theme import app_theme, current
from vidsaver.ui.views.home_view import HomeView
from vidsaver.ui.views.library_view import LibraryView
from vidsaver.ui.views.player_view import PlayerView
from vidsaver.utils.paths import ensure_storage_paths
from vidsaver.utils.platform import is_android_page

logger = logging.getLogger(__name__)

# Desktop uses sidebar when width is at least this many logical pixels
_DESKTOP_BREAKPOINT = 720


class AppContext:
    def __init__(self, page: ft.Page) -> None:
        self.page = page
        self.download_dir, self.metadata_path = ensure_storage_paths(page)
        self._media_store: MediaStoreService | None = None
        self._library: LibraryService | None = None
        self._downloader = DownloadService()
        self.playing: VideoEntry | None = None
        # Bumped on every theme toggle so child routes re-render with new palette
        self.theme_version: int = 0
        self.selected_tab: int = 0

    @property
    def media_store(self) -> MediaStoreService:
        if self._media_store is None:
            self._media_store = MediaStoreService(self.page)
        return self._media_store

    @property
    def library(self) -> LibraryService:
        if self._library is None:
            self._library = LibraryService(self.metadata_path, self.media_store)
        return self._library

    @property
    def downloader(self) -> DownloadService:
        return self._downloader


_CTX: AppContext | None = None


def get_ctx() -> AppContext:
    assert _CTX is not None
    return _CTX


class DownloadUIState:
    status_text: str = ""
    progress_val: float | None = None
    progress_visible: bool = False
    download_disabled: bool = False
    refresh_trigger: int = 0


_DL = DownloadUIState()


def _is_desktop_layout(page: ft.Page) -> bool:
    """Sidebar on desktop/wide windows; bottom nav on phone/Android."""
    if is_android_page(page):
        return False
    width = getattr(page, "width", None) or 0
    if width and width >= _DESKTOP_BREAKPOINT:
        return True
    # Prefer desktop for non-mobile platforms even before width is known
    platform = getattr(page, "platform", None)
    value = getattr(platform, "value", platform)
    if value in ("windows", "macos", "linux", "macOS", "Windows", "Linux"):
        return True
    if platform in (
        getattr(ft, "PagePlatform", type("", (), {})).WINDOWS
        if hasattr(ft, "PagePlatform")
        else None,
        getattr(ft.PagePlatform, "MACOS", None) if hasattr(ft, "PagePlatform") else None,
        getattr(ft.PagePlatform, "LINUX", None) if hasattr(ft, "PagePlatform") else None,
    ):
        return True
    return False


@ft.component
def HomeRoute():
    page = ft.context.page
    ctx = get_ctx()
    # Depend on theme_version so palette updates after toggle
    _theme_ver, set_theme_ver = ft.use_state(ctx.theme_version)

    def sync_theme():
        if _theme_ver != ctx.theme_version:
            set_theme_ver(ctx.theme_version)

    ft.use_effect(sync_theme, dependencies=[ctx.theme_version])

    status, set_status = ft.use_state(_DL.status_text)
    progress, set_progress = ft.use_state(_DL.progress_val)
    progress_vis, set_progress_vis = ft.use_state(_DL.progress_visible)
    disabled, set_disabled = ft.use_state(_DL.download_disabled)

    def start_download(url: str):
        if not url:
            set_status("Please enter a valid URL!")
            _DL.status_text = "Please enter a valid URL!"
            return

        set_disabled(True)
        set_progress_vis(True)
        set_progress(None)
        set_status("Starting...")
        _DL.download_disabled = True
        _DL.progress_visible = True
        _DL.progress_val = None
        _DL.status_text = "Starting..."

        loop = asyncio.get_event_loop()

        def on_status(msg: str):
            def _apply():
                set_status(msg)
                _DL.status_text = msg

            loop.call_soon_threadsafe(_apply)

        def on_progress(pct: float):
            def _apply():
                set_progress(pct)
                _DL.progress_val = pct

            loop.call_soon_threadsafe(_apply)

        async def flow():
            is_done = False
            try:
                result = await asyncio.to_thread(
                    ctx.downloader.run,
                    url,
                    ctx.download_dir,
                    on_status,
                    on_progress,
                )
                if not result.ok:
                    set_status(f"Error: {result.error}")
                    _DL.status_text = f"Error: {result.error}"
                    return

                set_status("Saving...")
                _DL.status_text = "Saving..."
                published = 0
                last_error = ""
                for path in result.paths:
                    file_name = os.path.basename(path)
                    size = os.path.getsize(path) if os.path.exists(path) else 0
                    thumb_b64 = (result.thumbnails or {}).get(path, "")
                    entry = VideoEntry(
                        display_name=file_name,
                        platform=result.platform,
                        url=result.url,
                        date=result.date,
                        created_at=time.time(),
                        source_path=path,
                        size=size,
                        thumbnail_b64=thumb_b64,
                    )
                    try:
                        if ctx.media_store.ensure() is not None:
                            meta = await ctx.media_store.save_video(path, file_name)
                            entry.content_uri = meta.get("content_uri", "")
                            entry.display_name = meta.get("display_name", file_name)
                            entry.mime_type = meta.get("mime_type", "video/mp4")
                            entry.relative_path = meta.get(
                                "relative_path", "Movies/Vidsaver"
                            )
                            entry.size = meta.get("size") or size
                            try:
                                os.remove(path)
                            except Exception:
                                pass
                    except Exception as exc:
                        last_error = str(exc)

                    ctx.library.upsert(entry)
                    published += 1

                if published:
                    set_status("Video saved to Gallery.")
                    _DL.status_text = "Video saved to Gallery."
                    is_done = True
                    show_toast(page, "Video download complete")
                else:
                    msg = f"Error: {last_error or 'Unable to save video'}"
                    set_status(msg)
                    _DL.status_text = msg
            except Exception as exc:
                set_status(f"Error: {exc}")
                _DL.status_text = f"Error: {exc}"
            finally:
                set_progress_vis(False)
                set_disabled(False)
                _DL.progress_visible = False
                _DL.download_disabled = False
                if is_done:
                    _DL.refresh_trigger += 1

        asyncio.create_task(flow())

    return HomeView(
        status_text=status,
        progress_val=progress,
        progress_visible=progress_vis,
        download_disabled=disabled,
        on_download=start_download,
        page=page,
    )


@ft.component
def DownloadsRoute():
    ctx = get_ctx()
    refresh, set_refresh = ft.use_state(_DL.refresh_trigger)
    scroll, set_scroll = ft.use_state(0.0)
    _theme_ver, set_theme_ver = ft.use_state(ctx.theme_version)

    def sync():
        if refresh != _DL.refresh_trigger:
            set_refresh(_DL.refresh_trigger)
        if _theme_ver != ctx.theme_version:
            set_theme_ver(ctx.theme_version)

    ft.use_effect(sync, dependencies=[_DL.refresh_trigger, ctx.theme_version])

    def on_play(entry: VideoEntry):
        ctx.selected_tab = 1
        ctx.playing = entry
        ft.context.page.navigate("/player")

    return LibraryView(
        library=ctx.library,
        on_play=on_play,
        refresh_trigger=refresh,
        initial_scroll=scroll,
        on_scroll_change=set_scroll,
    )


@ft.component
def PlayerRoute():
    ctx = get_ctx()
    page = ft.context.page
    entry = ctx.playing

    def close_player(_e=None):
        ctx.playing = None
        page.navigate("/")

    if entry is None:
        page.navigate("/")
        return ft.Container()

    return PlayerView(
        file_path=entry.playable_path,
        on_close=close_player,
        page=page,
    )


@ft.component
def AppLayout():
    """Shared chrome: desktop sidebar OR mobile NavigationBar + persistent tabs."""
    page = ft.context.page
    ctx = get_ctx()

    selected, set_selected = ft.use_state(ctx.selected_tab)
    dark_mode, set_dark_mode = ft.use_state(page.theme_mode == ft.ThemeMode.DARK)
    theme_ver, set_theme_ver = ft.use_state(ctx.theme_version)
    use_sidebar, set_use_sidebar = ft.use_state(_is_desktop_layout(page))

    def toggle_theme(_e=None):
        new_dark = not dark_mode
        page.theme_mode = ft.ThemeMode.DARK if new_dark else ft.ThemeMode.LIGHT
        ctx.theme_version += 1
        set_dark_mode(new_dark)
        set_theme_ver(ctx.theme_version)

    def setup_resize():
        old_handler = page.on_resize

        def handle_resize(e=None):
            if callable(old_handler):
                try:
                    old_handler(e)
                except Exception:
                    pass
            desktop = _is_desktop_layout(page)
            set_use_sidebar(desktop)

        page.on_resize = handle_resize
        return lambda: setattr(page, "on_resize", old_handler)

    ft.use_effect(setup_resize, dependencies=[])

    palette = current(page)

    def on_nav_change(index: int):
        ctx.selected_tab = index
        set_selected(index)

    # Retain both tab views in memory to eliminate re-rendering/reloading flash
    content_area = ft.Stack(
        controls=[
            ft.Container(
                content=HomeRoute(),
                visible=(selected == 0),
                expand=True,
            ),
            ft.Container(
                content=DownloadsRoute(),
                visible=(selected == 1),
                expand=True,
            ),
        ],
        expand=True,
    )

    # --- Desktop: left sidebar ---
    if use_sidebar:
        body = ft.Row(
            controls=[
                Sidebar(
                    selected_index=selected,
                    on_select=on_nav_change,
                    dark_mode=dark_mode,
                    on_toggle_theme=toggle_theme,
                ),
                ft.Container(
                    content=content_area,
                    expand=True,
                    bgcolor=palette.surface,
                    padding=ft.Padding(24, 20, 24, 20),
                ),
            ],
            expand=True,
            spacing=0,
        )
        return ft.View(
            route="/",
            can_pop=False,
            appbar=None,
            navigation_bar=None,
            bgcolor=palette.surface,
            controls=[ft.SafeArea(content=body, expand=True)],
        )

    # --- Mobile: AppBar + bottom NavigationBar ---
    return ft.View(
        route="/",
        can_pop=False,
        appbar=ft.AppBar(
            title=ft.Text(
                APP_TITLE,
                color=ft.Colors.WHITE,
                weight=ft.FontWeight.BOLD,
            ),
            center_title=True,
            bgcolor=palette.appbar,
            actions=[
                ft.IconButton(
                    icon=ft.Icons.DARK_MODE if not dark_mode else ft.Icons.LIGHT_MODE,
                    icon_color=ft.Colors.WHITE,
                    tooltip="Toggle dark mode",
                    on_click=toggle_theme,
                ),
            ],
        ),
        navigation_bar=ft.NavigationBar(
            bgcolor=palette.nav_bg,
            selected_index=selected,
            on_change=lambda e: on_nav_change(e.control.selected_index),
            destinations=[
                ft.NavigationBarDestination(
                    icon=ft.Icons.HOME_OUTLINED,
                    selected_icon=ft.Icons.HOME,
                    label="Home",
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.VIDEO_LIBRARY_OUTLINED,
                    selected_icon=ft.Icons.VIDEO_LIBRARY,
                    label="Downloads",
                ),
            ],
        ),
        bgcolor=palette.surface,
        controls=[
            ft.SafeArea(
                content=ft.Container(content=content_area, expand=True),
                expand=True,
            )
        ],
    )


@ft.component
def PlayerLayout():
    page = ft.context.page
    palette = current(page)
    return ft.View(
        route="/player",
        appbar=None,
        navigation_bar=None,
        bgcolor=palette.surface,
        controls=[
            ft.SafeArea(content=PlayerRoute(), expand=True),
        ],
    )


@ft.component
def App():
    return ft.Router(
        [
            ft.Route(path="/", component=AppLayout),
            ft.Route(path="player", component=PlayerLayout),
        ],
        manage_views=True,
    )


async def main(page: ft.Page):
    global _CTX
    ensure_storage_paths(page)
    _CTX = AppContext(page)

    page.title = APP_TITLE
    page.padding = 0
    page.spacing = 0
    page.theme = app_theme()
    page.dark_theme = app_theme()
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme_animation_style = ft.AnimationStyle.no_animation()
    page.window.min_width = 400
    page.window.min_height = 500

    async def after_first_paint():
        await asyncio.sleep(0)
        try:
            _CTX.media_store.ensure()
        except Exception as exc:
            logger.debug("MediaStore warm failed: %s", exc)
        threading.Thread(target=_CTX.downloader.warm, daemon=True).start()
        try:
            await _CTX.library.sync_from_mediastore()
        except Exception:
            pass

    page.run_task(after_first_paint)
    page.render_views(App)
