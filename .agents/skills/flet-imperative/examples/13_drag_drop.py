# -*- coding: utf-8 -*-
"""
Flet Drag and Drop Example
Demonstrates usage of DragTarget and Draggable controls

Target version: Flet >= 0.83.0 (Flet 1.0+)

Breaking changes:
  - ❌ Flet 0.x: DragTarget event uses e.data to accept drag  →  Flet 1.0+: use e.accept instead
  - ❌ Flet 0.x: Draggable uses on_drag_end  →  Flet 1.0+: use on_drag_complete instead
  - ✅ Flet 1.0+: use e.accept() in on_accept event handler to accept drag
  - ✅ Flet 1.0+: use ft.run(main) to launch
"""

import flet as ft


def main(page: ft.Page):
    page.title = "Drag and Drop Example"
    page.window.width = 600
    page.window.height = 500

    # Source data
    items = ["Apple", "Banana", "Orange", "Grape", "Watermelon"]

    # Result display
    result_text = ft.Text(value="Drag items to the right area", size=16)

    # Received items list
    received_items = ft.Column(scroll=ft.ScrollMode.AUTO)

    def make_draggable(item_name: str, index: int):
        """Create a draggable item"""

        def on_drag_start(e):
            e.control.content.opacity = 0.5
            e.control.update()

        def on_drag_complete(e):
            e.control.content.opacity = 1.0
            e.control.update()

        return ft.Draggable(
            group="fruits",
            content=ft.Container(
                content=ft.Text(item_name, size=14),
                bgcolor=ft.Colors.BLUE_100,
                padding=10,
                border_radius=5,
                width=100,
            ),
            content_when_dragging=ft.Container(
                content=ft.Text(item_name, size=14),
                bgcolor=ft.Colors.BLUE_50,
                padding=10,
                border_radius=5,
                opacity=0.5,
                width=100,
            ),
            on_drag_start=on_drag_start,
            on_drag_complete=on_drag_complete,
        )

    def make_drop_target():
        """Create a drop target area"""

        def on_drag_accept(e):
            # Flet 1.0+: use e.control to get the target control
            # Source control obtained via page.get_control(e.src_id)
            src = page.get_control(e.src_id)
            if src and src.content and src.content.content:
                item_text = src.content.content.value

                # Add to received list
                received_items.controls.append(
                    ft.Container(
                        content=ft.Text(item_text, size=14),
                        bgcolor=ft.Colors.GREEN_100,
                        padding=10,
                        border_radius=5,
                    )
                )
                result_text.value = f"Received: {item_text}"

                # Update target area style
                e.control.content.bgcolor = ft.Colors.GREEN_200
                e.control.update()
                page.update()

        def on_drag_will_accept(e):
            # Flet 1.0+: use e.accept instead of e.data
            if e.accept:
                e.control.content.bgcolor = ft.Colors.BLUE_200
            else:
                e.control.content.bgcolor = ft.Colors.GREY_200
            e.control.update()

        def on_drag_leave(e):
            # Flet 1.0+: use e.src_id to get source control ID
            e.control.content.bgcolor = ft.Colors.GREY_100
            e.control.update()

        return ft.DragTarget(
            group="fruits",
            content=ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.DOWNLOAD, size=40, color=ft.Colors.GREY_400),
                    ft.Text("Drop here", color=ft.Colors.GREY_500),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor=ft.Colors.GREY_100,
                width=200,
                height=200,
                border_radius=10,
                alignment=ft.Alignment.CENTER,
            ),
            on_accept=on_drag_accept,
            on_will_accept=on_drag_will_accept,
            on_leave=on_drag_leave,
        )

    # Source items list
    source_items = ft.Column(
        [make_draggable(item, i) for i, item in enumerate(items)],
        spacing=10,
    )

    # Layout
    page.add(
        ft.Text("Drag and Drop Example", size=24, weight=ft.FontWeight.BOLD),
        ft.Divider(),
        ft.Row([
            ft.Column([
                ft.Text("Draggable Items", size=14, weight=ft.FontWeight.W_500),
                source_items,
            ]),
            ft.VerticalDivider(),
            ft.Column([
                ft.Text("Drop Zone", size=14, weight=ft.FontWeight.W_500),
                make_drop_target(),
            ]),
            ft.VerticalDivider(),
            ft.Column([
                ft.Text("Received Items", size=14, weight=ft.FontWeight.W_500),
                received_items,
            ], expand=True),
        ], expand=True),
        ft.Divider(),
        result_text,
    )


ft.run(main)
