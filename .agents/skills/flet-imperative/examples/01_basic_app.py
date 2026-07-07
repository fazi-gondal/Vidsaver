# -*- coding: utf-8 -*-
"""
Flet Basic Application Example
Demonstrates the most basic Flet app structure and startup method

Target version: Flet >= 0.83.0 (Flet 1.0+)

Breaking changes:
  - ❌ Flet 0.x: ft.app(target=main)  →  Flet 1.0+: raises "missing required argument: 'target'"
  - ✅ Flet 1.0+: Use ft.run(main) to start the app
  - ✅ Flet 1.0+: All colors use ft.Colors.XXX (uppercase C), not ft.colors.XXX (lowercase s)
"""

import flet as ft


def main(page: ft.Page):
    """Main application function"""
    # Basic page settings
    page.title = "Basic App Example"
    page.window.width = 600
    page.window.height = 400
    page.padding = 20

    # Add content
    page.add(
        ft.Column(
            [
                ft.Text("Hello, Flet!", size=30, weight=ft.FontWeight.BOLD),
                ft.Text("This is a basic app example", size=16, color=ft.Colors.GREY_600),
                ft.Divider(),
                ft.Button(
                    content=ft.Text("Click Me"),
                    on_click=lambda e: print("Button was clicked!"),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )


# Use ft.run() to start the app
if __name__ == "__main__":
    ft.run(main)
