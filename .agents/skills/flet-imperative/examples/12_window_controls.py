# -*- coding: utf-8 -*-
"""
Flet Window Controls Example
Demonstrates window size, position, and state control features

Target version: Flet >= 0.83.0 (Flet 1.0+)

Breaking changes:
  - ❌ Flet 0.x: page.on_resized event  →  Flet 1.0+: event renamed to on_resize
  - ✅ Flet 1.0+: use page.on_resize to capture window size changes
  - ✅ Flet 1.0+: use page.window properties to control the window (consistent API)
"""

import asyncio
import flet as ft


def main(page: ft.Page):
    """Window controls example main function"""
    page.title = "Window Controls Example"
    page.window.width = 800
    page.window.height = 600

    # ===== Window status display =====
    window_info = ft.Column()

    def update_window_info():
        """Update window info display"""
        window_info.controls = [
            ft.Text("Window Status:", size=16, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Text(f"Width: {page.window.width} px"),
            ft.Text(f"Height: {page.window.height} px"),
            ft.Text(f"Position X: {page.window.left} px"),
            ft.Text(f"Position Y: {page.window.top} px"),
            ft.Text(f"Title: {page.title}"),
            ft.Text(f"Resizable: {page.window.resizable}"),
            ft.Text(f"Movable: {page.window.movable}"),
            ft.Text(f"Always on Top: {page.window.always_on_top}"),
            ft.Text(f"Full Screen: {page.window.full_screen}"),
            ft.Text(f"Maximized: {page.window.maximized}"),
            ft.Text(f"Minimized: {page.window.minimized}"),
            ft.Text(f"Visible: {page.window.visible}"),
            # Note: transparent property has been removed in Flet 1.0+
            ft.Divider(),
            ft.Text("Screen Info:", size=16, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Text(f"Screen Width: {page.window.max_width} px"),
            ft.Text(f"Screen Height: {page.window.max_height} px"),
        ]
        page.update()

    # ✅ Flet 1.0+ uses on_resize instead of on_resized
    def on_window_resize(e):
        """Window resize event"""
        update_window_info()

    page.on_resize = on_window_resize

    # ===== Window size controls =====
    size_input_width = ft.TextField(
        label="Width",
        value=str(int(page.window.width or 800)),
        width=120,
        keyboard_type=ft.KeyboardType.NUMBER,
    )
    size_input_height = ft.TextField(
        label="Height",
        value=str(int(page.window.height or 600)),
        width=120,
        keyboard_type=ft.KeyboardType.NUMBER,
    )

    def resize_window(e):
        """Resize the window"""
        try:
            width = int(size_input_width.value)
            height = int(size_input_height.value)
            page.window.width = width
            page.window.height = height
            update_window_info()
        except ValueError:
            print("Please enter valid numbers")

    # ===== Preset sizes =====
    def create_size_buttons():
        """Create preset size buttons"""
        presets = [
            ("800x600", 800, 600),
            ("1024x768", 1024, 768),
            ("1280x720", 1280, 720),
            ("Full Screen", None, None),
        ]

        buttons = []
        for name, w, h in presets:
            buttons.append(
                ft.Button(
                    content=ft.Text(name, size=12),
                    on_click=lambda e, w=w, h=h: set_preset_size(w, h),
                )
            )
        return buttons

    def set_preset_size(width, height):
        """Set preset size"""
        if width is None and height is None:
            page.window.full_screen = True
        else:
            page.window.full_screen = False
            page.window.width = width
            page.window.height = height
        update_window_info()

    # ===== Window state controls =====
    def create_state_buttons():
        """Create window state buttons"""
        return ft.Column([
            ft.Text("Window State:", weight=ft.FontWeight.W_500),
            ft.Row([
                ft.Button(
                    content=ft.Row([ft.Icon(ft.Icons.CHECK_BOX_OUTLINE_BLANK), ft.Text("Maximize")]),
                    on_click=lambda e: toggle_maximize(),
                ),
                ft.Button(
                    content=ft.Row([ft.Icon(ft.Icons.MINIMIZE), ft.Text("Minimize")]),
                    on_click=lambda e: minimize_window(),
                ),
                ft.Button(
                    content=ft.Row([ft.Icon(ft.Icons.FULLSCREEN), ft.Text("Full Screen")]),
                    on_click=lambda e: toggle_fullscreen(),
                ),
            ], wrap=True, spacing=10),

            ft.Container(height=10),

            ft.Text("Window Properties:", weight=ft.FontWeight.W_500),
            ft.Row([
                ft.Button(
                    content=ft.Text("Always on Top"),
                    on_click=lambda e: toggle_always_on_top(),
                ),
                ft.Button(
                    content=ft.Text("Disable Resize"),
                    on_click=lambda e: toggle_resizable(),
                ),
                ft.Button(
                    content=ft.Text("Disable Move"),
                    on_click=lambda e: toggle_movable(),
                ),
            ], wrap=True, spacing=10),

            ft.Container(height=10),

            ft.Text("Dangerous Operations:", weight=ft.FontWeight.W_500, color=ft.Colors.RED),
            ft.Row([
                ft.Button(
                    content=ft.Text("Hide Window"),
                    style=ft.ButtonStyle(color=ft.Colors.RED),
                    on_click=lambda e: hide_window(),
                ),
                ft.Button(
                    content=ft.Text("Close Window"),
                    style=ft.ButtonStyle(color=ft.Colors.RED),
                    on_click=lambda e: asyncio.create_task(close_window()),
                ),
            ], spacing=10),
        ])

    def toggle_maximize():
        """Toggle maximize"""
        page.window.maximized = not page.window.maximized
        update_window_info()

    def minimize_window():
        """Minimize window"""
        page.window.minimized = True
        update_window_info()

    def toggle_fullscreen():
        """Toggle full screen"""
        page.window.full_screen = not page.window.full_screen
        update_window_info()

    def toggle_always_on_top():
        """Toggle always on top"""
        page.window.always_on_top = not page.window.always_on_top
        update_window_info()

    def toggle_resizable():
        """Toggle resizable"""
        page.window.resizable = not page.window.resizable
        update_window_info()

    def toggle_movable():
        """Toggle movable"""
        page.window.movable = not page.window.movable
        update_window_info()

    def hide_window():
        """Hide window"""
        page.window.visible = False
        # Show again after 3 seconds
        import asyncio
        async def show_after_delay():
            await asyncio.sleep(3)
            page.window.visible = True
            update_window_info()
        asyncio.create_task(show_after_delay())

    async def close_window():
        """Close window"""
        await page.window.close()

    # ===== Window position controls =====
    def create_position_buttons():
        """Create position control buttons"""
        return ft.Column([
            ft.Text("Window Position:", weight=ft.FontWeight.W_500),
            ft.Row([
                ft.Button(content=ft.Text("Center"), on_click=lambda e: asyncio.create_task(center_window())),
                ft.Button(content=ft.Text("Top Left"), on_click=lambda e: move_to_corner("top_left")),
                ft.Button(content=ft.Text("Bottom Right"), on_click=lambda e: move_to_corner("bottom_right")),
            ], spacing=10),
        ])

    async def center_window():
        """Center window"""
        await page.window.center()
        update_window_info()

    def move_to_corner(corner: str):
        """Move to corner"""
        if corner == "top_left":
            page.window.left = 0
            page.window.top = 0
        elif corner == "bottom_right":
            # Screen size may be None, use default values
            max_w = page.window.max_width or 1920
            max_h = page.window.max_height or 1080
            win_w = page.window.width or 800
            win_h = page.window.height or 600
            page.window.left = max_w - win_w
            page.window.top = max_h - win_h
        update_window_info()

    # ===== Title bar controls =====
    def create_title_section():
        """Title bar controls"""
        title_input = ft.TextField(
            label="Window Title",
            value=page.title,
            width=300,
        )

        def change_title(e):
            page.title = title_input.value
            update_window_info()

        return ft.Column([
            ft.Text("Window Title:", weight=ft.FontWeight.W_500),
            ft.Row([
                title_input,
                ft.Button(content=ft.Text("Apply"), on_click=change_title),
            ], spacing=10),
        ])

    # ===== Transparent window example =====
    def create_transparency_section():
        """Transparent window notes"""
        return ft.Container(
            content=ft.Column([
                ft.Text("Transparent Window Notes:", weight=ft.FontWeight.W_500),
                ft.Markdown("""
⚠️ **Flet 1.0+ Breaking Change**: `page.window.transparent` property has been removed

Old configuration (no longer works):
- ❌ `page.window.transparent = True`
- ❌ `ft.run(main, transparent_window=True)`

New alternatives:
- Use `page.bgcolor = ft.Colors.TRANSPARENT` with platform-specific configuration
- Note: Transparent window functionality may have limitations or platform differences in Flet 1.0+
                """, selectable=True),
            ]),
            bgcolor=ft.Colors.GREY_100,
            padding=15,
            border_radius=10,
        )

    # ===== Page layout =====
    page.add(
        ft.Column([
            ft.Text(
                "Window Controls Example",
                size=28,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.BLUE_700,
            ),
            ft.Text("Demonstrates various Flet window control features", color=ft.Colors.GREY_600),
            ft.Divider(),

            ft.Row([
                # Left side - Window status
                ft.Container(
                    content=window_info,
                    bgcolor=ft.Colors.GREY_50,
                    padding=15,
                    border_radius=10,
                    width=250,
                ),

                ft.VerticalDivider(),

                # Right side - Control panel
                ft.Column([
                    ft.Text("Window Size:", weight=ft.FontWeight.W_500),
                    ft.Row([
                        size_input_width,
                        size_input_height,
                        ft.Button(content=ft.Text("Apply"), on_click=resize_window),
                    ], spacing=10),

                    ft.Row(create_size_buttons(), spacing=10),
                    ft.Divider(),

                    create_state_buttons(),
                    ft.Divider(),

                    create_position_buttons(),
                    ft.Divider(),

                    create_title_section(),
                    ft.Divider(),

                    create_transparency_section(),
                ], scroll=ft.ScrollMode.AUTO, expand=True),
            ], expand=True),
        ], expand=True)
    )

    # Initialize display
    update_window_info()


if __name__ == "__main__":
    ft.run(main)
