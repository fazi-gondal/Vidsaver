# -*- coding: utf-8 -*-
"""
Flet Async Real-Time Update Example - Digital Clock
Demonstrates how to use asyncio for reliable real-time updates

Target version: Flet >= 0.83.0 (Flet 1.0+)

Breaking changes:
  - ❌ Flet 0.x: Use ft.app(target=main) to start  →  Flet 1.0+: raises error
  - ✅ Flet 1.0+: Use ft.run(main) to start
  - ✅ Flet 1.0+: Delays in event handlers must use await asyncio.sleep(), not time.sleep()
  - ✅ Flet 1.0+: All colors use ft.Colors.XXX (uppercase C)
"""

import flet as ft
import asyncio
from datetime import datetime


def main(page: ft.Page):
    """Clock application main function"""
    page.title = "Digital Clock"
    page.window.width = 600
    page.window.height = 400
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 20

    # Weekday name mapping
    weekday_map = {
        0: "Monday",
        1: "Tuesday",
        2: "Wednesday",
        3: "Thursday",
        4: "Friday",
        5: "Saturday",
        6: "Sunday",
    }

    # Create display controls
    clock_text = ft.Text(
        value="00:00:00",
        size=80,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.BLUE_700,
    )

    date_text = ft.Text(
        value="",
        size=24,
        color=ft.Colors.GREY_600,
    )

    # Add controls to the page
    page.add(
        ft.Column(
            [
                clock_text,
                ft.Container(height=20),  # Spacing
                date_text,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )

    # Async clock update
    async def update_clock():
        """Update the clock every second"""
        while True:
            now = datetime.now()
            clock_text.value = now.strftime("%H:%M:%S")
            date_text.value = (
                f"{now.strftime('%Y-%m-%d')} {weekday_map[now.weekday()]}"
            )
            page.update()
            await asyncio.sleep(1)  # Use await asyncio.sleep

    # Start async task
    asyncio.create_task(update_clock())


if __name__ == "__main__":
    ft.run(main)
