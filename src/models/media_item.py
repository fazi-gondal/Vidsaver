"""Completed library media item (mirrors metadata.json entries)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class MediaItem:
    display_name: str
    platform: str = "Video"
    url: str = ""
    date: str = ""
    created_at: float = 0.0
    content_uri: str = ""
    source_path: str = ""
    mime_type: str = "video/mp4"
    relative_path: str = "Movies/Vidsaver"
    size: int = 0

    @property
    def playable_path(self) -> str:
        return self.content_uri or self.source_path or self.display_name

    @classmethod
    def from_metadata(cls, file_name: str, info: dict[str, Any]) -> MediaItem:
        return cls(
            display_name=str(info.get("display_name") or file_name),
            platform=str(info.get("platform") or "Video"),
            url=str(info.get("url") or ""),
            date=str(info.get("date") or ""),
            created_at=float(info.get("created_at") or 0),
            content_uri=str(info.get("content_uri") or ""),
            source_path=str(info.get("source_path") or info.get("file_path") or ""),
            mime_type=str(info.get("mime_type") or "video/mp4"),
            relative_path=str(info.get("relative_path") or "Movies/Vidsaver"),
            size=int(info.get("size") or 0),
        )
