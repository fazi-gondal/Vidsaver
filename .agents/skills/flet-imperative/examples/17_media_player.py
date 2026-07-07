# -*- coding: utf-8 -*-
"""
Flet Audio/Video Playback Example
Demonstrates audio and video control playback features

⚠️ Important: ft.Audio control has been completely removed in Flet 1.0+ (>=0.82.0)!
This example is kept as a historical reference, but audio functionality is no longer available.

Breaking changes:
  - ❌ Flet 0.x: ft.Audio control available  →  Flet 1.0+: Audio control completely removed
  - ❌ Flet 1.0+: no official replacement, use third-party libraries (e.g., pygame, pydub, etc.)
  - ✅ Flet 1.0+: use ft.run(main) to launch
"""

import flet as ft


def main(page: ft.Page):
    page.title = "Audio/Video Playback Example (Deprecated)"
    page.window.width = 600
    page.window.height = 400

    page.add(
        ft.Text("Audio/Video Playback Example", size=24, weight=ft.FontWeight.BOLD),
        ft.Divider(),

        ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.WARNING_AMBER, size=60, color=ft.Colors.ORANGE),
                ft.Text(
                    "⚠️ Audio Control Removed",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.RED,
                ),
                ft.Text(
                    "ft.Audio control has been completely removed in Flet 1.0+ (>=0.82.0)",
                    size=14,
                ),
                ft.Divider(),
                ft.Text("Breaking Change Details:", weight=ft.FontWeight.W_500),
                ft.Text("• Flet 0.x: ft.Audio(src='...') was available", color=ft.Colors.GREY_700),
                ft.Text("• Flet 1.0+: ft.Audio has been completely removed", color=ft.Colors.GREY_700),
                ft.Divider(),
                ft.Text("Alternatives:", weight=ft.FontWeight.W_500),
                ft.Text("• Use third-party audio libraries: pygame, pydub, simpleaudio", color=ft.Colors.GREY_700),
                ft.Text("• Use Web Audio API (for web apps)", color=ft.Colors.GREY_700),
                ft.Text("• Use system commands to invoke a player", color=ft.Colors.GREY_700),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
            ),
            bgcolor=ft.Colors.ORANGE_50,
            padding=30,
            border_radius=10,
            alignment=ft.Alignment.CENTER,
        ),

        ft.Divider(),

        ft.Text("Third-party Library Example Code:", weight=ft.FontWeight.W_500),
        ft.Container(
            content=ft.Markdown("""
```python
# Play audio with pygame
import pygame
pygame.mixer.init()
pygame.mixer.music.load("audio.mp3")
pygame.mixer.music.play()

# Play audio with pydub
from pydub import AudioSegment
from pydub.playback import play
audio = AudioSegment.from_file("audio.mp3")
play(audio)
```
            """, selectable=True),
            bgcolor=ft.Colors.GREY_100,
            padding=15,
            border_radius=10,
        ),
    )


ft.run(main)
