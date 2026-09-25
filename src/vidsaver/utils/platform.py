"""Platform detection helpers."""

from __future__ import annotations

import flet as ft

from vidsaver.config.constants import VIDEO_DOMAINS


def is_android_page(page: ft.Page) -> bool:
    platform = getattr(page, "platform", None)
    platform_value = getattr(platform, "value", platform)
    return platform == ft.PagePlatform.ANDROID or platform_value == "android"


def is_video_url(text: str) -> bool:
    if not text:
        return False
    value = text.strip()
    return value.startswith(("http://", "https://")) and any(
        domain in value for domain in VIDEO_DOMAINS
    )
