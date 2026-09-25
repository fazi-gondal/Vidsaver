# -*- coding: utf-8 -*-
"""
Flet Gesture Recognition Example
Demonstrates tap, double tap, long press, pinch-to-zoom and other gestures

Target version: Flet >= 0.83.0 (Flet 1.0+)

Breaking changes:
  - ❌ Flet 0.x: DragUpdateEvent uses e.local_x/local_y  →  Flet 1.0+: use e.local_position.x/y instead
  - ✅ Flet 1.0+: use GestureDetector's on_tap, on_double_tap, on_long_press events
  - ✅ Flet 1.0+: InteractiveViewer for zoom/pan (scrollable parameter name may have changed)
  - ✅ Flet 1.0+: use ft.run(main) to launch
"""

import flet as ft


def main(page: ft.Page):
    page.title = "Gesture Recognition Example"
    page.window.width = 900
    page.window.height = 640

    # Gesture status display
    gesture_info = ft.Text(value="Perform a gesture...", size=16)
    tap_count = ft.Text(value="Tap count: 0", size=14)

    counter = [0]  # Use list to store mutable count

    # Double tap detection
    last_click_time = [0.0]

    def on_double_tap_area_click(e):
        import time
        current_time = time.time()
        if current_time - last_click_time[0] < 0.3:
            update_info("Double Tap!")
            last_click_time[0] = 0
        else:
            last_click_time[0] = current_time
            # Delayed single tap display
            time.sleep(0.35)
            if last_click_time[0] == current_time:
                update_info("Single Tap")

    # Tap area
    tap_area = ft.Container(
        content=ft.Column([
            ft.Icon(ft.Icons.TOUCH_APP, size=40, color=ft.Colors.BLUE),
            ft.Text("Tap / Double Tap / Long Press"),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        bgcolor=ft.Colors.BLUE_50,
        width=200,
        height=120,
        border_radius=10,
        alignment=ft.Alignment.CENTER,
        ink=True,
        on_click=on_double_tap_area_click,
        on_long_press=lambda: update_info("Long Press"),
    )

    def update_info(text):
        gesture_info.value = f"Gesture: {text}"
        counter[0] += 1
        tap_count.value = f"Tap count: {counter[0]}"
        page.update()

    # GestureDetector example
    gesture_detector = ft.GestureDetector(
        on_tap=lambda e: update_info("GestureDetector: Tap"),
        on_double_tap=lambda e: update_info("GestureDetector: Double Tap"),
        on_long_press_start=lambda e: update_info("GestureDetector: Long Press Start"),
        on_long_press_end=lambda e: update_info("GestureDetector: Long Press End"),
        on_pan_update=lambda e: update_info(f"GestureDetector: Drag ({e.local_position.x:.0f}, {e.local_position.y:.0f})"),
        drag_interval=50,
        content=ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.GESTURE, size=40, color=ft.Colors.GREEN),
                ft.Text("GestureDetector Area"),
                ft.Text("Supports tap/double tap/long press/drag", size=12, color=ft.Colors.GREY_500),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=ft.Colors.GREEN_50,
            width=200,
            height=120,
            border_radius=10,
            alignment=ft.Alignment.CENTER,
        ),
    )

    # InteractiveViewer zoom example
    interactive_viewer = ft.InteractiveViewer(
        content=ft.Container(
            content=ft.Image(
                src="https://picsum.photos/300/200",
                fit=ft.BoxFit.CONTAIN,
                width=300,
                height=200,
            ),
            bgcolor=ft.Colors.GREY_200,
            padding=10,
        ),
        min_scale=0.5,
        max_scale=3.0,
        boundary_margin=ft.Margin.all(1000),
        expand=True,
        on_interaction_start=lambda e: update_info("Interaction Start"),
        on_interaction_end=lambda e: update_info("Interaction End"),
        on_interaction_update=lambda e: update_info(f"Scale: {e.scale:.2f}x"),
    )

    # Horizontal swipe detection (with animation)
    swipe_offset = [0.0]  # Use list to store mutable offset

    swipe_area = ft.Container(
        content=ft.Column([
            ft.Icon(ft.Icons.SWIPE, size=40, color=ft.Colors.PURPLE),
            ft.Text("Horizontal Swipe Detection"),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        bgcolor=ft.Colors.PURPLE_50,
        width=200,
        height=80,
        border_radius=10,
        alignment=ft.Alignment.CENTER,
    )

    def on_swipe_start(e):
        swipe_area.bgcolor = ft.Colors.PURPLE_100
        swipe_area.update()
        update_info("Horizontal Swipe Start")

    def on_swipe_update(e):
        # Update offset for swipe animation
        swipe_offset[0] += e.primary_delta or 0
        swipe_area.offset = ft.Offset(swipe_offset[0] / 100, 0)
        swipe_area.update()
        update_info(f"Horizontal Swipe: {swipe_offset[0]:.1f}px")

    def on_swipe_end(e):
        swipe_area.bgcolor = ft.Colors.PURPLE_50
        # Reset animation
        swipe_offset[0] = 0
        swipe_area.offset = ft.Offset(0, 0)
        swipe_area.animate_offset = 300  # 300ms reset animation
        swipe_area.update()
        update_info("Horizontal Swipe End")

    swipe_detector = ft.Container(
        content=ft.GestureDetector(
            on_horizontal_drag_start=on_swipe_start,
            on_horizontal_drag_update=on_swipe_update,
            on_horizontal_drag_end=on_swipe_end,
            content=swipe_area,
        ),
        width=400,  # Larger container allows swiping
        height=100,
        alignment=ft.Alignment.CENTER,
    )

    page.add(
        ft.Text("Gesture Recognition Example", size=24, weight=ft.FontWeight.BOLD),
        ft.Divider(),
        ft.Row([
            gesture_info,
            tap_count,
        ]),
        ft.Divider(),
        ft.Row([
            ft.Column([
                ft.Text("Container Gestures:", weight=ft.FontWeight.W_500),
                tap_area,
            ]),
            ft.Column([
                ft.Text("GestureDetector:", weight=ft.FontWeight.W_500),
                gesture_detector,
            ]),
            ft.Column([
                ft.Text("Swipe Detection:", weight=ft.FontWeight.W_500),
                swipe_detector,
            ]),
        ], spacing=20),
        ft.Divider(),
        ft.Text("InteractiveViewer (Zoom/Pan):", weight=ft.FontWeight.W_500),
        # Use Row + expand=True to fill the full width
        ft.Row([
            ft.Container(
                content=interactive_viewer,
                bgcolor=ft.Colors.GREY_100,
                border_radius=10,
                padding=10,
                height=250,
                expand=True,
            ),
        ], expand=True),
    )


ft.run(main)
