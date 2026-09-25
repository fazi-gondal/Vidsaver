"""Data models for downloaded videos."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class VideoEntry:
    """One saved video as stored in metadata.json / MediaStore."""

    display_name: str
    platform: str = "Video"
    url: str = ""
    date: str = ""
    created_at: float = 0.0
    content_uri: str = ""
    source_path: str = ""
    file_path: str = ""
    mime_type: str = "video/mp4"
    relative_path: str = "Movies/Vidsaver"
    size: int = 0
    # Path to thumbnail image stored in the app's private data dir (not gallery)
    thumbnail_path: str = ""

    @classmethod
    def from_dict(cls, name: str, data: dict[str, Any]) -> VideoEntry:
        return cls(
            display_name=name,
            platform=data.get("platform") or "Video",
            url=data.get("url") or "",
            date=data.get("date") or "",
            created_at=float(data.get("created_at") or 0),
            content_uri=data.get("content_uri") or "",
            source_path=data.get("source_path") or data.get("file_path") or "",
            file_path=data.get("file_path") or "",
            mime_type=data.get("mime_type") or "video/mp4",
            relative_path=data.get("relative_path") or "Movies/Vidsaver",
            size=int(data.get("size") or 0),
            thumbnail_path=data.get("thumbnail_path") or "",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "platform": self.platform,
            "url": self.url,
            "date": self.date,
            "created_at": self.created_at,
            "content_uri": self.content_uri,
            "source_path": self.source_path,
            "file_path": self.file_path,
            "mime_type": self.mime_type,
            "relative_path": self.relative_path,
            "size": self.size,
            "display_name": self.display_name,
            "thumbnail_path": self.thumbnail_path,
        }

    @property
    def playable_path(self) -> str:
        return self.content_uri or self.source_path or self.file_path or self.display_name


@dataclass
class DownloadResult:
    """Result returned by the download service after yt-dlp finishes."""

    paths: list[str] = field(default_factory=list)
    platform: str = "Video"
    url: str = ""
    date: str = ""
    error: str = ""
    # Map of video path -> private thumbnail path
    thumbnails: dict[str, str] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return bool(self.paths) and not self.error
