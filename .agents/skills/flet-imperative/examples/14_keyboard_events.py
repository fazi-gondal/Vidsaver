# -*- coding: utf-8 -*-
"""
Flet Keyboard Events Example
Demonstrates keyboard shortcuts and event handling

Target version: Flet >= 0.83.0 (Flet 1.0+)

Breaking changes:
  - ✅ Flet 1.0+: use page.on_keyboard_event to handle keyboard events
  - ✅ Flet 1.0+: use ft.run(main) to launch
  - Note: Keyboard event API remains stable in Flet 1.0+, no major breaking changes
"""

import flet as ft


def main(page: ft.Page):
    page.title = "Keyboard Events Example"
    page.window.width = 600
    page.window.height = 500

    # Display area
    key_display = ft.Text(value="Press any key...", size=20)
    shortcut_display = ft.Text(value="", size=16, color=ft.Colors.BLUE)

    # Input field example
    input_field = ft.TextField(
        label="Input field (supports Ctrl+A select all, Ctrl+C copy)",
        multiline=True,
        min_lines=3,
        max_lines=5,
    )

    # Shortcut hints
    shortcuts_info = ft.Column([
        ft.Text("Shortcut Keys:", weight=ft.FontWeight.BOLD),
        ft.Text("Ctrl+S: Save"),
        ft.Text("Ctrl+N: New"),
        ft.Text("Ctrl+Q: Quit"),
        ft.Text("Escape: Clear"),
        ft.Text("Arrow Keys: Move indicator"),
    ])

    # Movement indicator
    indicator = ft.Container(
        content=ft.Icon(ft.Icons.ARROW_RIGHT, color=ft.Colors.WHITE),
        bgcolor=ft.Colors.BLUE,
        width=30,
        height=30,
        border_radius=15,
        alignment=ft.Alignment.CENTER,
        left=100,
        top=100,
        animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
    )

    indicator_container = ft.Container(
        content=ft.Stack([indicator], width=200, height=200),
        bgcolor=ft.Colors.GREY_100,
        border_radius=10,
        width=200,
        height=200,
    )

    def on_keyboard(e: ft.KeyboardEvent):
        # Display key info
        modifiers = []
        if e.shift:
            modifiers.append("Shift")
        if e.ctrl:
            modifiers.append("Ctrl")
        if e.alt:
            modifiers.append("Alt")
        if e.meta:
            modifiers.append("Meta")

        modifier_str = " + ".join(modifiers) + " + " if modifiers else ""
        key_display.value = f"Key: {modifier_str}{e.key}"

        # Handle shortcuts
        if e.ctrl and e.key == "S":
            shortcut_display.value = "Action: Save"
            shortcut_display.color = ft.Colors.GREEN
        elif e.ctrl and e.key == "N":
            shortcut_display.value = "Action: New"
            shortcut_display.color = ft.Colors.GREEN
        elif e.ctrl and e.key == "Q":
            shortcut_display.value = "Action: Quit"
            shortcut_display.color = ft.Colors.RED
            page.window.close()
        elif e.key == "Escape":
            shortcut_display.value = "Action: Clear"
            shortcut_display.color = ft.Colors.ORANGE
            input_field.value = ""
        # Arrow key movement
        elif e.key == "Arrow Up":
            indicator.top = max(0, indicator.top - 10)
            shortcut_display.value = "Move Up"
        elif e.key == "Arrow Down":
            indicator.top = min(170, indicator.top + 10)
            shortcut_display.value = "Move Down"
        elif e.key == "Arrow Left":
            indicator.left = max(0, indicator.left - 10)
            shortcut_display.value = "Move Left"
        elif e.key == "Arrow Right":
            indicator.left = min(170, indicator.left + 10)
            shortcut_display.value = "Move Right"
        else:
            shortcut_display.value = ""

        page.update()

    # Bind keyboard event
    page.on_keyboard_event = on_keyboard

    page.add(
        ft.Text("Keyboard Events Example", size=24, weight=ft.FontWeight.BOLD),
        ft.Divider(),
        ft.Row([
            ft.Column([
                key_display,
                shortcut_display,
                ft.Divider(),
                input_field,
            ], expand=True),
            ft.VerticalDivider(),
            ft.Column([
                shortcuts_info,
                ft.Divider(),
                ft.Text("Arrow Key Test:"),
                indicator_container,
            ]),
        ], expand=True),
        ft.Text("Tip: Click anywhere on the page first, then press keyboard keys", color=ft.Colors.GREY_500),
    )


ft.run(main)
