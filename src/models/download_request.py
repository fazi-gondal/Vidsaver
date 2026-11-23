"""User-selected download options for a task."""

from __future__ import annotations

from dataclasses import dataclass, field

from config.constants import DEFAULT_CONTAINER, DEFAULT_DOWNLOAD_MODE, DEFAULT_QUALITY


@dataclass
class DownloadRequest:
    url: str
    quality: str = DEFAULT_QUALITY
    container: str = DEFAULT_CONTAINER
    mode: str = DEFAULT_DOWNLOAD_MODE  # video | audio
    format_id: str | None = None
    extra_ydl_opts: dict = field(default_factory=dict)
