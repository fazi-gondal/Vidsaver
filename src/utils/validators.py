"""URL and input validation."""

from __future__ import annotations

from config.constants import VIDEO_DOMAINS


def is_video_url(text: str) -> bool:
    if not text:
        return False
    value = text.strip()
    return value.startswith(("http://", "https://")) and any(
        domain in value for domain in VIDEO_DOMAINS
    )


def normalize_url(text: str) -> str:
    return (text or "").strip()
