"""URL field with paste affordance."""

from __future__ import annotations

import flet as ft

from config.theme import PRIMARY


@ft.component
def UrlInput(
    *,
    value: str,
    on_change,
    on_submit,
    on_paste_click,
    on_focus=None,
    disabled: bool = False,
):
    return ft.Row(
        [
            ft.TextField(
                value=value,
                on_change=lambda e: on_change(e.control.value or ""),
                on_submit=on_submit,
                on_focus=on_focus,
                label="Paste video link",
                expand=True,
                dense=True,
                disabled=disabled,
                border=ft.OutlineInputBorder(
                    border_radius=ft.BorderRadius(12, 12, 12, 12)
                ),
                filled=True,
                prefix_icon=ft.Icons.LINK,
            ),
            ft.IconButton(
                icon=ft.Icons.CONTENT_PASTE_ROUNDED,
                tooltip="Paste",
                on_click=on_paste_click,
                disabled=disabled,
                icon_color=PRIMARY,
            ),
        ],
        spacing=4,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )
