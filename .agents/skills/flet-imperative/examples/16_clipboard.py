# -*- coding: utf-8 -*-
"""
Flet Clipboard Operations Example
Demonstrates copy, paste and other clipboard features

Target version: Flet >= 0.83.0 (Flet 1.0+)

Breaking changes:
  - ❌ Flet 0.x: page.clipboard is deprecated → Flet 1.0+: use ft.Clipboard() class instead
  - ✅ Flet 1.0+: clipboard operations must use async def + await (asynchronous)
  - ✅ Flet 1.0+: clipboard.set(text) to set content
  - ✅ Flet 1.0+: await clipboard.get() to get content
"""

import flet as ft
import asyncio


async def main(page: ft.Page):
    page.title = "Clipboard Operations Example"
    page.window.width = 500
    page.window.height = 450

    # Create clipboard instance (Flet 1.0+: use ft.Clipboard() instead of page.clipboard)
    clipboard = ft.Clipboard()

    # Input field
    copy_input = ft.TextField(
        label="Content to copy",
        multiline=True,
        min_lines=3,
        max_lines=5,
        value="This is the text to copy to the clipboard!\nSupports multi-line text.",
    )

    # Display clipboard content
    paste_display = ft.TextField(
        label="Pasted content",
        multiline=True,
        min_lines=3,
        max_lines=5,
        read_only=True,
    )

    # Status display
    status_text = ft.Text(value="", size=14, color=ft.Colors.GREEN)

    async def on_copy(e):
        """Copy to clipboard"""
        if copy_input.value:
            await clipboard.set(copy_input.value)
            status_text.value = f"Copied {len(copy_input.value)} characters"
            status_text.color = ft.Colors.GREEN
        else:
            status_text.value = "Nothing to copy"
            status_text.color = ft.Colors.RED
        page.update()

    async def on_paste(e):
        """Paste from clipboard"""
        content = await clipboard.get()
        if content:
            paste_display.value = content
            status_text.value = f"Pasted {len(content)} characters"
            status_text.color = ft.Colors.BLUE
        else:
            paste_display.value = ""
            status_text.value = "Clipboard is empty"
            status_text.color = ft.Colors.ORANGE
        page.update()

    async def on_copy_from_paste(e):
        """Copy from paste area"""
        if paste_display.value:
            await clipboard.set(paste_display.value)
            status_text.value = f"Copied paste area content: {len(paste_display.value)} characters"
            status_text.color = ft.Colors.GREEN
        page.update()

    async def on_clear_clipboard(e):
        """Clear clipboard"""
        await clipboard.set("")
        status_text.value = "Clipboard cleared"
        status_text.color = ft.Colors.ORANGE
        page.update()

    # Quick copy buttons row
    quick_copy_buttons = ft.Row([
        ft.Button(
            content=ft.Text("Copy Email"),
            on_click=lambda e: asyncio.create_task(quick_copy("example@email.com")),
        ),
        ft.Button(
            content=ft.Text("Copy Phone"),
            on_click=lambda e: asyncio.create_task(quick_copy("138-0000-0000")),
        ),
        ft.Button(
            content=ft.Text("Copy Address"),
            on_click=lambda e: asyncio.create_task(quick_copy("123 Main Street, Suite 456")),
        ),
    ])

    async def quick_copy(text):
        """Quick copy preset text"""
        await clipboard.set(text)
        status_text.value = f"Copied: {text}"
        status_text.color = ft.Colors.GREEN
        page.update()

    page.add(
        ft.Text("Clipboard Operations Example", size=24, weight=ft.FontWeight.BOLD),
        ft.Divider(),

        ft.Text("Quick Copy:", weight=ft.FontWeight.W_500),
        quick_copy_buttons,
        ft.Divider(),

        ft.Row([
            ft.Column([
                ft.Text("Copy Area:", weight=ft.FontWeight.W_500),
                copy_input,
                ft.Button(
                    content=ft.Row([
                        ft.Icon(ft.Icons.CONTENT_COPY, size=18),
                        ft.Text("Copy to Clipboard"),
                    ]),
                    style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE),
                    on_click=on_copy,
                ),
            ], expand=True),
            ft.VerticalDivider(),
            ft.Column([
                ft.Text("Paste Area:", weight=ft.FontWeight.W_500),
                paste_display,
                ft.Row([
                    ft.Button(
                        content=ft.Row([
                            ft.Icon(ft.Icons.CONTENT_PASTE, size=18),
                            ft.Text("Paste"),
                        ]),
                        style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE),
                        on_click=on_paste,
                    ),
                    ft.Button(
                        content=ft.Text("Copy This Content"),
                        on_click=on_copy_from_paste,
                    ),
                ]),
            ], expand=True),
        ], expand=True),

        ft.Divider(),
        ft.Row([
            status_text,
            ft.Button(
                content=ft.Text("Clear Clipboard"),
                style=ft.ButtonStyle(bgcolor=ft.Colors.RED_100),
                on_click=on_clear_clipboard,
            ),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
    )

    # Listen for keyboard shortcuts
    def on_keyboard(e: ft.KeyboardEvent):
        if e.ctrl and e.key == "C":
            asyncio.create_task(on_copy(None))
        elif e.ctrl and e.key == "V":
            asyncio.create_task(on_paste(None))

    page.on_keyboard_event = on_keyboard

ft.run(main)
