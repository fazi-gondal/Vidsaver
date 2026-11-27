"""
main.py - Vidsaver app entry point and View router.
"""

import asyncio
import threading

import flet as ft

from home import HomeView
from storage import (
    delete_saved_video,
    ensure_media_scanner,
    ensure_storage_paths,
    init_storage_paths,
    is_http_url,
    publish_download_result,
    sync_saved_videos,
)
import theme


@ft.component
def NavBarItem(
    label: str,
    icon: ft.IconData,
    selected_icon: ft.IconData,
    active: bool,
    on_click,
    icon_color: str | None = None,
):
    """Bottom navigation item with Nocturnal Studio hover and active animations."""
    hovered, set_hovered = ft.use_state(False)

    if active:
        bg = ft.Colors.SURFACE_CONTAINER_HIGH
    elif hovered:
        bg = ft.Colors.with_opacity(0.6, ft.Colors.SURFACE_CONTAINER_HIGH)
    else:
        bg = None

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(
                    width=28 if active else 0,
                    height=3,
                    bgcolor=ft.Colors.PRIMARY if active else ft.Colors.TRANSPARENT,
                    border_radius=ft.BorderRadius.all(theme.RADIUS_PILL),
                    animate=ft.Animation(180, ft.AnimationCurve.EASE_OUT),
                ),
                ft.Row(
                    controls=[
                        ft.Icon(
                            selected_icon if active else icon,
                            size=21,
                            color=icon_color or (ft.Colors.PRIMARY if active else ft.Colors.ON_SURFACE_VARIANT),
                        ),
                        ft.Text(
                            label,
                            style=ft.TextStyle(
                                font_family=theme.FONT_BODY_SEMIBOLD if active else theme.FONT_BODY,
                                size=13.5,
                                weight=ft.FontWeight.W_600 if active else ft.FontWeight.W_400,
                                color=ft.Colors.ON_SURFACE if active else ft.Colors.ON_SURFACE_VARIANT,
                            ),
                            no_wrap=True,
                        ),
                    ],
                    spacing=8,
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ],
            spacing=5,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            tight=True,
        ),
        padding=ft.Padding.symmetric(vertical=8, horizontal=18),
        border_radius=ft.BorderRadius.all(theme.RADIUS_CONTROL),
        bgcolor=bg,
        animate=ft.Animation(180, ft.AnimationCurve.EASE_OUT),
        on_hover=lambda e: set_hovered(e.data is True or e.data == "true"),
        on_click=on_click,
        expand=True,
        alignment=ft.Alignment.CENTER,
    )


@ft.component
def BottomNavBar(active_tab: int, on_select):
    """Tonal bottom navigation bar matching Nocturnal Studio's sidebar items."""
    return ft.Container(
        content=ft.Row(
            controls=[
                NavBarItem(
                    label="Home",
                    icon=ft.Icons.HOME_FILLED,
                    selected_icon=ft.Icons.HOME_FILLED,
                    active=active_tab == 0,
                    on_click=lambda _: on_select(0),
                ),
                NavBarItem(
                    label="Downloads",
                    icon=ft.Icons.DOWNLOAD_ROUNDED,
                    selected_icon=ft.Icons.DOWNLOAD,
                    active=active_tab == 1,
                    on_click=lambda _: on_select(1),
                    icon_color=theme.PILL_RED,
                ),
            ],
            spacing=8,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
        border=ft.Border(top=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT)),
        padding=ft.Padding(left=12, right=12, top=8, bottom=10),
    )


@ft.component
def App(page: ft.Page):
    """Root declarative App component returning View stack for native Back navigation."""
    def _initial_dark() -> bool:
        if page.theme_mode == ft.ThemeMode.DARK:
            return True
        if page.theme_mode == ft.ThemeMode.LIGHT:
            return False
        return page.platform_brightness != ft.Brightness.LIGHT

    is_dark, set_is_dark = ft.use_state(_initial_dark)
    active_tab, set_active_tab = ft.use_state(0)
    playing_file, set_playing_file = ft.use_state(None)
    playing_file_ref = ft.use_ref(playing_file)
    playing_file_ref.current = playing_file

    status_text, set_status_text = ft.use_state("")
    progress_val, set_progress_val = ft.use_state(None)
    progress_visible, set_progress_visible = ft.use_state(False)
    download_disabled, set_download_disabled = ft.use_state(False)

    refresh_trigger, set_refresh_trigger = ft.use_state(0)
    scroll_offset, set_scroll_offset = ft.use_state(0)

    def setup_view_pop():
        def handle_view_pop(e):
            if playing_file_ref.current:
                set_playing_file(None)

        old_handler = page.on_view_pop
        page.on_view_pop = handle_view_pop
        return lambda: setattr(page, "on_view_pop", old_handler)

    ft.use_effect(setup_view_pop, dependencies=[])

    def set_download_busy(message: str):
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

            directory, metadata = await init_storage_paths(page)
            cookie_path = ""
            from downloader import run_download

            had_error = [False]

            def on_status(message, _set=set_status_text):
                page.loop.call_soon_threadsafe(_set, message)

            def on_progress(value, _set=set_progress_val):
                page.loop.call_soon_threadsafe(_set, value)

            def on_error(message, _had=had_error, _set=set_status_text):
                _had[0] = True
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
                    set_status_text(f"Video saved to Gallery ({engine}).")
                    is_done = True
                else:
                    set_status_text(f"Error: {error}")

            finish_download(is_done)

        asyncio.create_task(download_flow())

    from library import LibraryView

    directory, metadata = ensure_storage_paths(page)
    main_content = ft.Stack(
        controls=[
            ft.Container(
                content=HomeView(
                    status_text_val=status_text,
                    progress_val=progress_val,
                    progress_visible=progress_visible,
                    download_disabled=download_disabled,
                    on_download_click=start_download,
                    on_open_downloads=lambda: set_active_tab(1),
                    page=page,
                ),
                visible=active_tab == 0,
                expand=True,
            ),
            ft.Container(
                content=LibraryView(
                    download_dir=directory,
                    metadata_path=metadata,
                    on_play=set_playing_file,
                    initial_scroll=scroll_offset,
                    on_scroll_change=set_scroll_offset,
                    refresh_trigger=refresh_trigger,
                    delete_from_storage=lambda info: delete_saved_video(page, info),
                    sync_from_storage=lambda: sync_saved_videos(page, metadata),
                    on_go_home=lambda: set_active_tab(0),
                ),
                visible=active_tab == 1,
                expand=True,
            ),
        ],
        expand=True,
    )

    def toggle_theme(_):
        new_dark = not is_dark
        page.theme_mode = ft.ThemeMode.DARK if new_dark else ft.ThemeMode.LIGHT
        page.update()
        set_is_dark(new_dark)

    appbar = ft.AppBar(
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
                icon=ft.Icons.DARK_MODE_OUTLINED if is_dark else ft.Icons.LIGHT_MODE_OUTLINED,
                icon_color=ft.Colors.ON_SURFACE_VARIANT,
                tooltip="Toggle light/dark theme",
                on_click=toggle_theme,
            )
        ],
    )

    views: list[ft.View] = [
        ft.View(
            route="/",
            appbar=appbar,
            bottom_appbar=ft.BottomAppBar(
                content=BottomNavBar(active_tab=active_tab, on_select=set_active_tab),
                bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
                padding=0,
                elevation=0,
                height=68,
            ),
            controls=[ft.SafeArea(content=main_content, expand=True)],
            can_pop=(active_tab == 0),
            on_confirm_pop=lambda _: set_active_tab(0),
            padding=0,
            spacing=0,
        )
    ]

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
        views.append(
            ft.View(
                route="/player",
                controls=[
                    ft.SafeArea(
                        content=PlayerView(
                            file_path=playable_path,
                            on_close=lambda e: set_playing_file(None),
                        ),
                        expand=True,
                    )
                ],
                padding=0,
                spacing=0,
                bgcolor=ft.Colors.BLACK,
            )
        )

    return views


async def main(page: ft.Page):
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

    page.render_views(App, page=page)

    async def _post_launch_init() -> None:
        await asyncio.sleep(0)
        await init_storage_paths(page)
        ensure_media_scanner(page)
        from downloader import preload_heavy_modules

        threading.Thread(target=preload_heavy_modules, daemon=True).start()

    asyncio.create_task(_post_launch_init())


ft.run(main, assets_dir="assets")
