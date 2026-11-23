"""
library.py - Declarative downloads library view.
"""

import asyncio
import os

import flet as ft

from downloader import PLATFORM_CHIP_COLOR, PLATFORM_COLOR, load_metadata, save_metadata

VIDEO_EXTENSIONS = (".mp4", ".mkv", ".mov", ".avi", ".webm", ".m4v", ".3gp")


@ft.component
def VideoCard(file_name: str, meta: dict, on_play, on_delete, on_share=None):
    """Styled card component representing one saved video."""
    info = meta.get(file_name, {})
    platform = info.get("platform", "Video")
    date_str = info.get("date", "")
    thumb_color = PLATFORM_COLOR.get(platform, ft.Colors.BLUE_700)
    chip_color = PLATFORM_CHIP_COLOR.get(platform, ft.Colors.BLUE_100)
    source_path = info.get("source_path") or info.get("file_path") or ""
    source_url = str(info.get("url") or "")

    thumb = ft.Container(
        width=72,
        height=72,
        bgcolor=thumb_color,
        border_radius=8,
        content=ft.Icon(
            ft.Icons.PLAY_CIRCLE_FILL_ROUNDED,
            color=ft.Colors.with_opacity(0.85, ft.Colors.WHITE),
            size=32,
        ),
        alignment=ft.Alignment(0, 0),
    )

    chip = ft.Container(
        content=ft.Text(platform, size=10, weight=ft.FontWeight.W_600, color=thumb_color),
        bgcolor=chip_color,
        border_radius=20,
        padding=ft.Padding(left=8, right=8, top=3, bottom=3),
    )

    size = info.get("size") or 0
    if not size and source_path:
        try:
            size = os.path.getsize(source_path)
        except Exception:
            size = 0
    size_str = f"{size / (1024 * 1024):.1f} MB" if size else ""
    name_without_ext = os.path.splitext(file_name)[0]

    info_col = ft.Column(
        controls=[
            ft.Text(
                name_without_ext,
                size=13,
                weight=ft.FontWeight.W_600,
                max_lines=2,
                overflow=ft.TextOverflow.ELLIPSIS,
            ),
            ft.Row(
                controls=[
                    chip,
                    ft.Text(size_str, size=11, color=ft.Colors.GREY_500),
                    ft.Text(date_str, size=11, color=ft.Colors.GREY_500),
                ],
                spacing=6,
            ),
        ],
        spacing=4,
        expand=True,
    )

    return ft.Card(
        elevation=2,
        content=ft.Container(
            content=ft.Row(
                controls=[
                    thumb,
                    info_col,
                    ft.IconButton(
                        icon=ft.Icons.SHARE_OUTLINED,
                        icon_color=ft.Colors.GREY_600,
                        tooltip="Share link",
                        visible=bool(source_url),
                        on_click=lambda e, fn=file_name, u=source_url: on_share(fn, u) if on_share else None,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_color=ft.Colors.RED_400,
                        tooltip="Delete",
                        on_click=lambda e, fn=file_name: on_delete(fn),
                    ),
                ],
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=12, right=4, top=10, bottom=10),
            on_click=lambda e, fn=file_name: on_play(fn),
            ink=True,
        ),
        margin=ft.Margin(left=8, right=8, top=4, bottom=4),
    )


@ft.component
def LibraryView(
    download_dir: str,
    metadata_path: str,
    on_play,
    initial_scroll=0,
    on_scroll_change=None,
    refresh_trigger=0,
    delete_from_storage=None,
    sync_from_storage=None,
    on_share=None,
):
    """
    Declarative component for the downloads library.

    Android MediaStore saves are listed from app metadata, not by scanning a
    public directory.
    """
    files, set_files = ft.use_state([])
    meta, set_meta = ft.use_state({})
    deleting_file, set_deleting_file = ft.use_state(None)
    search_query, set_search_query = ft.use_state("")
    platform_filter, set_platform_filter = ft.use_state("All")
    sort_mode, set_sort_mode = ft.use_state("newest")  # newest | oldest | name
    list_ref = ft.use_ref()

    def sort_key(item, loaded_meta):
        info = loaded_meta.get(item, {})
        created_at = info.get("created_at") or 0
        if created_at:
            return created_at
        source_path = info.get("source_path") or info.get("file_path") or ""
        try:
            return os.path.getmtime(source_path)
        except Exception:
            return 0

    async def read_data_async():
        """Load and sort metadata off the event loop to keep the UI responsive."""
        def _load():
            loaded_meta = load_metadata(metadata_path)
            valid_files = [
                name
                for name in loaded_meta
                if name.lower().endswith(VIDEO_EXTENSIONS)
            ]
            valid_files.sort(key=lambda item: sort_key(item, loaded_meta), reverse=True)
            return loaded_meta, valid_files

        loaded_meta, valid_files = await asyncio.to_thread(_load)
        set_meta(loaded_meta)
        set_files(valid_files)

    async def load_data():
        if sync_from_storage:
            try:
                await sync_from_storage()
            except Exception:
                pass
        await read_data_async()

    ft.use_effect(load_data, dependencies=[refresh_trigger])

    async def restore_scroll():
        if initial_scroll > 0 and list_ref.current:
            await asyncio.sleep(0.05)
            try:
                await list_ref.current.scroll_to(offset=initial_scroll, duration=0)
                # No manual .update() needed — Flet declarative reconciliation handles it
            except Exception:
                pass

    ft.use_effect(restore_scroll, dependencies=[files])

    async def confirm_delete():
        file_name = deleting_file
        set_deleting_file(None)
        loaded_meta = await asyncio.to_thread(load_metadata, metadata_path)
        info = loaded_meta.get(file_name, {})
        source_path = info.get("source_path") or info.get("file_path") or ""
        deleted = False

        if delete_from_storage:
            try:
                deleted = await delete_from_storage(info)
            except Exception:
                deleted = False
        elif source_path and os.path.exists(source_path):
            try:
                os.remove(source_path)
                deleted = True
            except Exception:
                deleted = False
        else:
            deleted = not source_path and not info.get("content_uri")

        if not deleted:
            return

        loaded_meta.pop(file_name, None)
        await asyncio.to_thread(save_metadata, metadata_path, loaded_meta)
        await read_data_async()

    ft.use_dialog(
        ft.AlertDialog(
            modal=True,
            title=ft.Text("Delete video?"),
            content=ft.Text(f'Are you sure you want to delete "{deleting_file}"?'),
            actions=[
                ft.TextButton("No", on_click=lambda _: set_deleting_file(None)),
                ft.TextButton("OK", on_click=lambda _: asyncio.create_task(confirm_delete())),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        if deleting_file
        else None
    )

    q = (search_query or "").strip().lower()
    filtered = []
    platforms = {"All"}
    for file_name in files:
        info = meta.get(file_name, {})
        plat = str(info.get("platform") or "Video")
        platforms.add(plat)
        if platform_filter and platform_filter != "All" and plat != platform_filter:
            continue
        if q:
            title = os.path.splitext(file_name)[0].lower()
            hay = f"{title} {plat} {info.get('url', '')}".lower()
            if q not in hay:
                continue
        filtered.append(file_name)

    def _name_key(fn):
        return os.path.splitext(fn)[0].lower()

    def _date_key(fn):
        return sort_key(fn, meta)

    if sort_mode == "oldest":
        filtered.sort(key=_date_key)
    elif sort_mode == "name":
        filtered.sort(key=_name_key)
    else:
        filtered.sort(key=_date_key, reverse=True)

    list_controls = []
    if not files:
        list_controls.append(
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(
                            ft.Icons.VIDEO_LIBRARY_OUTLINED,
                            size=48,
                            color=ft.Colors.GREY_400,
                        ),
                        ft.Text("No downloads yet", color=ft.Colors.GREY, size=14),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                ),
                alignment=ft.Alignment(0, 0),
                expand=True,
                padding=40,
            )
        )
    elif not filtered:
        list_controls.append(
            ft.Container(
                content=ft.Text("No matches", color=ft.Colors.GREY, size=14),
                alignment=ft.Alignment(0, 0),
                padding=24,
            )
        )
    else:
        for file_name in filtered:
            list_controls.append(
                VideoCard(
                    file_name=file_name,
                    meta=meta,
                    on_play=on_play,
                    on_delete=set_deleting_file,
                    on_share=on_share,
                )
            )

    platform_options = sorted(platforms, key=lambda p: (p != "All", p))

    return ft.Column(
        controls=[
            ft.Container(
                content=ft.Column(
                    [
                        ft.TextField(
                            value=search_query,
                            label="Search",
                            prefix_icon=ft.Icons.SEARCH,
                            dense=True,
                            on_change=lambda e: set_search_query(e.control.value or ""),
                            border=ft.OutlineInputBorder(
                                border_radius=ft.BorderRadius(12, 12, 12, 12)
                            ),
                        ),
                        ft.Row(
                            [
                                ft.Dropdown(
                                    value=platform_filter if platform_filter in platform_options else "All",
                                    dense=True,
                                    width=130,
                                    label="Platform",
                                    options=[ft.dropdown.Option(p) for p in platform_options],
                                    on_change=lambda e: set_platform_filter(e.control.value or "All"),
                                ),
                                ft.Dropdown(
                                    value=sort_mode,
                                    dense=True,
                                    width=130,
                                    label="Sort",
                                    options=[
                                        ft.dropdown.Option("newest", "Newest"),
                                        ft.dropdown.Option("oldest", "Oldest"),
                                        ft.dropdown.Option("name", "Name"),
                                    ],
                                    on_change=lambda e: set_sort_mode(e.control.value or "newest"),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                    ],
                    spacing=8,
                ),
                padding=ft.Padding(left=12, right=12, top=8, bottom=4),
            ),
            ft.ListView(
                ref=list_ref,
                controls=list_controls,
                expand=True,
                spacing=0,
                padding=0,
                on_scroll=lambda e: on_scroll_change(e.pixels) if on_scroll_change else None,
            ),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True,
    )
