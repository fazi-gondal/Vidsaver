"""Downloads library tab."""

from __future__ import annotations

import asyncio

import flet as ft

from vidsaver.models.video import VideoEntry
from vidsaver.services.library_service import LibraryService
from vidsaver.ui.components.empty_state import EmptyState
from vidsaver.ui.components.skeleton import SkeletonList
from vidsaver.ui.components.video_card import VideoCard


@ft.component
def LibraryView(
    library: LibraryService,
    on_play,
    refresh_trigger: int,
    initial_scroll: float = 0,
    on_scroll_change=None,
):
    init_items = library.list_entries()
    entries, set_entries = ft.use_state(init_items)
    loading, set_loading = ft.use_state(lambda: not bool(init_items))
    deleting, set_deleting = ft.use_state(None)  # VideoEntry | None
    list_ref = ft.use_ref()

    async def load():
        data = await asyncio.to_thread(library.list_entries)
        set_entries(data)
        set_loading(False)
        try:
            await asyncio.wait_for(library.sync_from_mediastore(), timeout=2.0)
            synced = await asyncio.to_thread(library.list_entries)
            if len(synced) != len(data):
                set_entries(synced)
        except Exception:
            pass

    ft.use_effect(
        lambda: asyncio.create_task(load()),
        dependencies=[refresh_trigger],
    )

    def restore_scroll():
        if list_ref.current and initial_scroll:
            try:
                list_ref.current.scroll_to(offset=initial_scroll, duration=0)
            except Exception:
                pass

    ft.use_effect(restore_scroll, dependencies=[entries])

    async def confirm_delete():
        entry = deleting
        set_deleting(None)
        if entry is None:
            return
        ok = await library.delete_entry(entry)
        if ok:
            set_entries([e for e in entries if e.display_name != entry.display_name])

    ft.use_dialog(
        ft.AlertDialog(
            modal=True,
            title=ft.Text("Delete video?"),
            content=ft.Text(
                f'Are you sure you want to delete "{deleting.display_name if deleting else ""}"?'
            ),
            actions=[
                ft.TextButton("No", on_click=lambda _: set_deleting(None)),
                ft.TextButton(
                    "OK",
                    on_click=lambda _: asyncio.create_task(confirm_delete()),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        if deleting
        else None
    )

    if loading and not entries:
        content = SkeletonList(count=5)
    elif not entries:
        content = EmptyState()
    else:
        content = ft.ListView(
            ref=list_ref,
            controls=[
                VideoCard(
                    entry=e,
                    on_play=on_play,
                    on_delete=set_deleting,
                )
                for e in entries
            ],
            expand=True,
            spacing=10,
            padding=ft.Padding(12, 12, 12, 16),
            on_scroll=lambda e: on_scroll_change(e.pixels) if on_scroll_change else None,
        )

    return ft.Column(
        controls=[content],
        expand=True,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
    )
