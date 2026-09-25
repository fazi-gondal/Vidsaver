"""Metadata persistence and library listing."""

from __future__ import annotations

import json
import os
import time
from datetime import datetime
from typing import Any

from vidsaver.models.video import VideoEntry
from vidsaver.services.media_store import MediaStoreService
from vidsaver.services.download_service import extract_thumbnail_b64


def load_metadata(metadata_path: str) -> dict[str, Any]:
    try:
        if os.path.exists(metadata_path):
            with open(metadata_path, encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def save_metadata(metadata_path: str, meta: dict[str, Any]) -> None:
    try:
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


class LibraryService:
    def __init__(self, metadata_path: str, media_store: MediaStoreService | None = None) -> None:
        self.metadata_path = metadata_path
        self.media_store = media_store

    def _get_thumbnail_b64(self, entry: VideoEntry) -> str:
        """Extract a frame from the video file and return it as base64.
        No file is ever written to disk."""
        candidates = []
        if entry.source_path:
            candidates.append(entry.source_path)
        meta_dir = os.path.dirname(self.metadata_path)
        if meta_dir:
            candidates.append(os.path.join(meta_dir, entry.display_name))

        for video_path in candidates:
            if os.path.isfile(video_path):
                b64 = extract_thumbnail_b64(video_path)
                if b64:
                    return b64
        return ""

    def list_entries(self) -> list[VideoEntry]:
        meta = load_metadata(self.metadata_path)
        changed = False
        entries: list[VideoEntry] = []
        for name, data in meta.items():
            entry = VideoEntry.from_dict(name, data)
            if not entry.thumbnail_b64:
                b64 = self._get_thumbnail_b64(entry)
                if b64:
                    entry.thumbnail_b64 = b64
                    data["thumbnail_b64"] = b64
                    changed = True
            entries.append(entry)
        if changed:
            save_metadata(self.metadata_path, meta)
        # Newest first
        entries.sort(key=lambda e: e.created_at or 0, reverse=True)
        return entries

    def upsert(self, entry: VideoEntry) -> None:
        meta = load_metadata(self.metadata_path)
        meta[entry.display_name] = entry.to_dict()
        save_metadata(self.metadata_path, meta)

    def remove(self, display_name: str) -> None:
        meta = load_metadata(self.metadata_path)
        meta.pop(display_name, None)
        save_metadata(self.metadata_path, meta)

    async def sync_from_mediastore(self) -> None:
        """Restore metadata from Android MediaStore after app updates."""
        if self.media_store is None or not self.media_store.available:
            return

        videos = await self.media_store.list_videos()
        if not videos:
            return

        meta = load_metadata(self.metadata_path)
        changed = False
        for video in videos:
            display_name = str(video.get("display_name") or "")
            content_uri = str(video.get("content_uri") or "")
            if not display_name or not content_uri:
                continue

            created_at = float(video.get("date_added") or video.get("date_modified") or time.time())
            existing = meta.get(display_name, {})
            restored = {
                **existing,
                "platform": existing.get("platform") or "Video",
                "url": existing.get("url") or "",
                "date": existing.get("date")
                or datetime.fromtimestamp(created_at).strftime("%d %b %Y"),
                "created_at": existing.get("created_at") or created_at,
                "content_uri": content_uri,
                "display_name": display_name,
                "mime_type": str(video.get("mime_type") or "video/mp4"),
                "relative_path": str(video.get("relative_path") or "Movies/Vidsaver"),
                "size": int(video.get("size") or existing.get("size") or 0),
            }
            if meta.get(display_name) != restored:
                meta[display_name] = restored
                changed = True

        if changed:
            save_metadata(self.metadata_path, meta)

    async def delete_entry(self, entry: VideoEntry) -> bool:
        """Delete from MediaStore or filesystem and remove metadata."""
        deleted = False
        if entry.content_uri and self.media_store:
            deleted = await self.media_store.delete_video(entry.content_uri)
        elif entry.source_path and os.path.exists(entry.source_path):
            try:
                os.remove(entry.source_path)
                deleted = True
            except Exception:
                deleted = False
        else:
            deleted = not entry.content_uri and not entry.source_path

        if deleted:
            self.remove(entry.display_name)
        return deleted
