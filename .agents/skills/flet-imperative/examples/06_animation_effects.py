# -*- coding: utf-8 -*-
"""
Flet Animation Effects Example
Demonstrates various animation effects and interactions

Target version: Flet >= 0.83.0 (Flet 1.0+)

Breaking changes:
  - ❌ Flet 0.x: animate parameter for opacity/rotation/scale  →  Flet 1.0+: no effect
  - ✅ Flet 1.0+: Use container.animate_opacity, container.animate_rotation, container.animate_scale separately
  - ❌ Flet 0.x: ft.alignment.center  →  Flet 1.0+: raises "no attribute 'center'"
  - ✅ Flet 1.0+: Use ft.Alignment.CENTER
  - ✅ Flet 1.0+: Delays in event handlers must use await asyncio.sleep(), not page.wait() or time.sleep()
"""

import flet as ft
import asyncio
import math


def main(page: ft.Page):
    """Animation example main function"""
    page.title = "Animation Effects Example"
    page.window.width = 800
    page.window.height = 600
    page.padding = 30

    # ===== Example 1: Hover Animation =====
    # Key point: Hover event handlers must be async def
    # Flet 1.0+ uses on_hover event, parameter e.data is boolean (True/False)
    hover_container = ft.Container(
        content=ft.Text("Hover to See Effect", size=20, weight=ft.FontWeight.BOLD),
        width=200,
        height=100,
        bgcolor=ft.Colors.BLUE_100,
        border_radius=10,
        animate=300,  # 300ms animation
        alignment=ft.Alignment.CENTER,
    )

    async def on_hover(e):
        # In Flet 1.0+, e.data is boolean True/False (not string "true"/"false")
        if e.data:  # Mouse entered (e.data is True)
            hover_container.bgcolor = ft.Colors.BLUE_700
            hover_container.width = 250
            hover_container.height = 120
            hover_container.content = ft.Text(
                "Hovering!",
                size=24,
                color=ft.Colors.WHITE,
                weight=ft.FontWeight.BOLD,
            )
            hover_container.shadow = ft.BoxShadow(
                spread_radius=2,
                blur_radius=15,
                color=ft.Colors.BLUE_200,
            )
        else:  # Mouse left (e.data is False)
            hover_container.bgcolor = ft.Colors.BLUE_100
            hover_container.width = 200
            hover_container.height = 100
            hover_container.content = ft.Text(
                "Hover to See Effect",
                size=20,
                weight=ft.FontWeight.BOLD,
            )
            hover_container.shadow = None
        page.update()

    hover_container.on_hover = on_hover

    # ===== Example 2: Click Scale Animation =====
    # Key point: Delayed recovery must use asyncio.sleep(), not page.run_task + page.wait()
    scale_container = ft.Container(
        content=ft.Icon(ft.Icons.FAVORITE, size=50, color=ft.Colors.RED),
        width=100,
        height=100,
        bgcolor=ft.Colors.RED_50,
        border_radius=50,
        alignment=ft.Alignment.CENTER,
        animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
    )

    async def on_click_scale(e):
        # Scale down animation
        scale_container.scale = 0.8
        page.update()

        # Wait briefly then restore
        await asyncio.sleep(0.1)  # 100ms

        # Restore animation
        scale_container.scale = 1.0
        page.update()

    scale_container.on_click = on_click_scale

    # ===== Example 3: Color Transition Animation =====
    color_container = ft.Container(
        content=ft.Text("Click to Change Color", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
        width=200,
        height=100,
        bgcolor=ft.Colors.PURPLE,
        border_radius=10,
        alignment=ft.Alignment.CENTER,
        animate=500,  # 500ms animation
    )

    colors = [
        ft.Colors.PURPLE,
        ft.Colors.BLUE,
        ft.Colors.GREEN,
        ft.Colors.ORANGE,
        ft.Colors.RED,
    ]
    color_index = [0]  # Use list to store mutable state

    async def on_click_color(e):
        color_index[0] = (color_index[0] + 1) % len(colors)
        color_container.bgcolor = colors[color_index[0]]
        page.update()

    color_container.on_click = on_click_color

    # ===== Example 4: Rotation Animation =====
    # Key point: Use math.radians() or radians directly; set animate_rotation for the rotate property
    rotation_container = ft.Container(
        content=ft.Icon(ft.Icons.REFRESH, size=40, color=ft.Colors.WHITE),
        width=80,
        height=80,
        bgcolor=ft.Colors.TEAL,
        border_radius=40,
        alignment=ft.Alignment.CENTER,
        animate_rotation=ft.Animation(800, ft.AnimationCurve.EASE_IN_OUT),
    )

    rotation_angle = [0]

    async def on_click_rotate(e):
        rotation_angle[0] += 360
        # Use math.radians to convert degrees to radians
        rotation_container.rotate = math.radians(rotation_angle[0])
        page.update()

    rotation_container.on_click = on_click_rotate

    # ===== Example 5: Position Movement Animation =====
    position_container = ft.Container(
        content=ft.Icon(ft.Icons.DIRECTIONS_RUN, size=30, color=ft.Colors.WHITE),
        width=60,
        height=60,
        bgcolor=ft.Colors.AMBER,
        border_radius=30,
        alignment=ft.Alignment.CENTER,
        animate=ft.Animation(400, ft.AnimationCurve.BOUNCE_OUT),
    )

    positions = [
        {"left": 0, "top": 0},
        {"left": 150, "top": 0},
        {"left": 150, "top": 100},
        {"left": 0, "top": 100},
    ]
    position_index = [0]

    async def on_click_position(e):
        position_index[0] = (position_index[0] + 1) % len(positions)
        pos = positions[position_index[0]]
        position_container.left = pos["left"]
        position_container.top = pos["top"]
        page.update()

    position_stack = ft.Stack(
        [
            ft.Container(
                width=210,
                height=160,
                border=ft.Border.all(2, ft.Colors.GREY_300),  # Use ft.Border.all()
                border_radius=10,
            ),
            position_container,
        ],
        width=210,
        height=160,
    )

    # ===== Example 6: Opacity Animation =====
    # Key point: Opacity animation requires the animate_opacity property
    opacity_container = ft.Container(
        content=ft.Text("Fade In/Out", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
        width=200,
        height=100,
        bgcolor=ft.Colors.INDIGO,
        border_radius=10,
        alignment=ft.Alignment.CENTER,
        opacity=1.0,
        animate_opacity=ft.Animation(600, ft.AnimationCurve.EASE_IN_OUT),  # Use animate_opacity
    )

    async def on_click_opacity(e):
        opacity_container.opacity = 0.2 if opacity_container.opacity == 1.0 else 1.0
        page.update()

    opacity_container.on_click = on_click_opacity

    # Page layout
    page.add(
        ft.Column(
            [
                ft.Text(
                    "Flet Animation Effects Example",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Divider(),

                # First row
                ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text("Hover Animation", weight=ft.FontWeight.BOLD),
                                hover_container,
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        ft.Column(
                            [
                                ft.Text("Click to Scale", weight=ft.FontWeight.BOLD),
                                scale_container,
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        ft.Column(
                            [
                                ft.Text("Color Transition", weight=ft.FontWeight.BOLD),
                                color_container,
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                    ],
                    spacing=30,
                    alignment=ft.MainAxisAlignment.SPACE_AROUND,
                ),

                ft.Divider(),

                # Second row
                ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text("Rotation (Click)", weight=ft.FontWeight.BOLD),
                                rotation_container,
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        ft.Column(
                            [
                                ft.Text("Position Move (Click)", weight=ft.FontWeight.BOLD),
                                position_stack,
                                ft.Button(
                                    content=ft.Text("Move"),
                                    on_click=on_click_position,
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        ft.Column(
                            [
                                ft.Text("Opacity Animation", weight=ft.FontWeight.BOLD),
                                opacity_container,
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                    ],
                    spacing=30,
                    alignment=ft.MainAxisAlignment.SPACE_AROUND,
                ),

                ft.Divider(),

                # Tip information
                ft.Container(
                    content=ft.Text(
                        "Tip: Hover over or click the cards above to see the animation effects",
                        color=ft.Colors.GREY_600,
                        size=14,
                    ),
                    bgcolor=ft.Colors.BLUE_50,
                    padding=15,
                    border_radius=8,
                ),
            ],
            spacing=20,
        )
    )


if __name__ == "__main__":
    ft.run(main)
