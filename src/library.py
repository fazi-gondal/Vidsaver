"""
library.py - Declarative downloads library view (Nocturnal Studio design).
"""

import asyncio
import os

import flet as ft

from downloader import load_metadata, save_metadata
import theme

VIDEO_EXTENSIONS = (".mp4", ".mkv", ".mov", ".avi", ".webm", ".m4v", ".3gp")


@ft.component
def VideoCard(file_name: str, meta: dict, on_play, on_delete):
    """Tonal card component representing one saved video."""
    info = meta.get(file_name, {})
    platform = info.get("platform", "Video")
    date_str = info.get("date", "")
    pill_color = theme.PLATFORM_PILL_COLORS.get(platform, theme.PILL_CORAL)
    source_path = info.get("source_path") or info.get("file_path") or ""

    thumb = ft.Container(
        width=84,
        height=52,
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
        border_radius=ft.BorderRadius.all(8),
        border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
        content=ft.Icon(
            ft.Icons.PLAY_ARROW_ROUNDED,
            color=pill_color,
            size=26,
        ),
        alignment=ft.Alignment.CENTER,
    )

    size = info.get("size") or 0
    if not size and source_path:
        try:
            size = os.path.getsize(source_path)
        except Exception:
            size = 0
    meta_parts = []
    if size:
        meta_parts.append(f"{size / (1024 * 1024):.1f} MB")
    if date_str:
        meta_parts.append(date_str)
    meta_text = "  ·  ".join(meta_parts)

    name_without_ext = os.path.splitext(file_name)[0]

    info_col = ft.Column(
        controls=[
            ft.Text(
                name_without_ext,
                style=ft.TextStyle(
                    font_family=theme.FONT_BODY_SEMIBOLD,
                    size=15,
                    weight=ft.FontWeight.W_600,
                    color=ft.Colors.ON_SURFACE,
                ),
                max_lines=1,
                overflow=ft.TextOverflow.ELLIPSIS,
            ),
            ft.Row(
                controls=[
                    theme.status_pill(platform, pill_color),
                    *(
                        [
                            ft.Text(
                                meta_text,
                                style=theme.data_style(ft.Colors.ON_SURFACE_VARIANT),
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            )
                        ]
                        if meta_text
                        else []
                    ),
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        ],
        spacing=6,
        expand=True,
    )

    return ft.Container(
        content=theme.surface_card(
            content=ft.Row(
                controls=[
                    thumb,
                    info_col,
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
                        icon_size=20,
                        icon_color=ft.Colors.ON_SURFACE_VARIANT,
                        tooltip="Delete",
                        on_click=lambda e, fn=file_name: on_delete(fn),
                    ),
                ],
                spacing=14,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=14, right=8, top=12, bottom=12),
            on_click=lambda e, fn=file_name: on_play(fn),
            ink=True,
        ),
        margin=ft.Margin(left=16, right=16, top=4, bottom=4),
    )


def _filter_pill(label: str, active: bool, on_click) -> ft.Container:
    return ft.Container(
        content=ft.Text(
            label,
            style=ft.TextStyle(
                font_family=theme.FONT_BODY_MEDIUM if active else theme.FONT_BODY,
                size=13,
                weight=ft.FontWeight.W_600 if active else ft.FontWeight.W_400,
                color=ft.Colors.ON_SURFACE if active else ft.Colors.ON_SURFACE_VARIANT,
            ),
        ),
        padding=ft.Padding.symmetric(vertical=6, horizontal=14),
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH if active else None,
        border=ft.Border.all(1, ft.Colors.OUTLINE if active else ft.Colors.TRANSPARENT),
        border_radius=ft.BorderRadius.all(theme.RADIUS_PILL),
        on_click=on_click,
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
    on_go_home=None,
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
    active_filter, set_active_filter = ft.use_state("All")
    list_ref = ft.use_memo(lambda: ft.Ref[ft.ListView](), dependencies=[])

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
            title=ft.Text("Delete video?", style=theme.headline_md()),
            content=ft.Text(
                f'Are you sure you want to delete "{deleting_file}"?',
                style=theme.body_md(ft.Colors.ON_SURFACE_VARIANT),
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: set_deleting_file(None)),
                ft.TextButton("Delete", on_click=lambda _: asyncio.create_task(confirm_delete())),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        if deleting_file
        else None
    )

    platforms_present = []
    for fn in files:
        plat = meta.get(fn, {}).get("platform", "Video")
        if plat not in platforms_present:
            platforms_present.append(plat)

    q = search_query.strip().lower()
    filtered_files = [
        fn
        for fn in files
        if (active_filter == "All" or meta.get(fn, {}).get("platform", "Video") == active_filter)
        and (
            not q
            or q in fn.lower()
            or q in str(meta.get(fn, {}).get("platform", "")).lower()
        )
    ]

    header_controls: list[ft.Control] = []
    if files:
        search_bar = theme.inset_input_box(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.SEARCH_ROUNDED, size=18, color=ft.Colors.ON_SURFACE_VARIANT),
                    ft.TextField(
                        value=search_query,
                        on_change=lambda e: set_search_query(e.control.value),
                        hint_text="Search by title or platform...",
                        hint_style=theme.body_md(ft.Colors.ON_SURFACE_VARIANT),
                        text_style=theme.body_md(),
                        border=ft.NoInputBorder(),
                        dense=True,
                        expand=True,
                    ),
                    *(
                        [
                            ft.IconButton(
                                icon=ft.Icons.CLOSE_ROUNDED,
                                icon_size=18,
                                icon_color=ft.Colors.ON_SURFACE_VARIANT,
                                tooltip="Clear search",
                                on_click=lambda _: set_search_query(""),
                            )
                        ]
                        if search_query
                        else []
                    ),
                ],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=14, right=6, top=2, bottom=2),
            radius=theme.RADIUS_PILL,
        )

        filter_row = (
            ft.Row(
                controls=[
                    _filter_pill("All", active_filter == "All", lambda _: set_active_filter("All")),
                    *[
                        _filter_pill(
                            plat,
                            active_filter == plat,
                            lambda _, p=plat: set_active_filter(p),
                        )
                        for plat in platforms_present
                    ],
                ],
                spacing=6,
                scroll=ft.ScrollMode.AUTO,
            )
            if len(platforms_present) > 1
            else None
        )

        header_controls.append(
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Text("Downloads", style=theme.headline_xl()),
                                ft.Text(
                                    f"{len(filtered_files)} video{'s' if len(filtered_files) != 1 else ''}",
                                    style=theme.data_style(ft.Colors.ON_SURFACE_VARIANT),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.BASELINE,
                        ),
                        search_bar,
                        *([filter_row] if filter_row else []),
                    ],
                    spacing=12,
                ),
                padding=ft.Padding(left=16, right=16, top=16, bottom=8),
            )
        )

    list_controls: list[ft.Control] = []
    if not files:
        cta = (
            ft.OutlinedButton(
                "Download a video",
                icon=ft.Icons.DOWNLOAD_ROUNDED,
                on_click=lambda _: on_go_home(),
            )
            if on_go_home
            else None
        )
        list_controls.append(
            theme.empty_state(
                icon=ft.Icons.VIDEO_LIBRARY_OUTLINED,
                title="No downloads yet",
                subtitle="Downloaded videos will appear here.",
                action=cta,
            )
        )
    elif not filtered_files:
        list_controls.append(
            theme.empty_state(
                icon=ft.Icons.SEARCH_OFF_ROUNDED,
                title="No matching videos",
                subtitle="Try a different search term or filter.",
                compact=True,
            )
        )
    else:
        for file_name in filtered_files:
            list_controls.append(
                VideoCard(
                    file_name=file_name,
                    meta=meta,
                    on_play=on_play,
                    on_delete=set_deleting_file,
                )
            )

    return ft.Column(
        controls=[
            *header_controls,
            ft.ListView(
                ref=list_ref,
                controls=list_controls,
                expand=True,
                spacing=0,
                padding=ft.Padding(left=0, right=0, top=4, bottom=16),
                on_scroll=lambda e: on_scroll_change(e.pixels) if on_scroll_change else None,
            ),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        spacing=0,
        expand=True,
    )
