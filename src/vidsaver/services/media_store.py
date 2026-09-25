"""Android MediaStore facade. Lazy-initialised; no-op on desktop."""

from __future__ import annotations

import logging
from typing import Any

import flet as ft

from vidsaver.config.constants import ALBUM_NAME
from vidsaver.utils.platform import is_android_page

logger = logging.getLogger(__name__)


class MediaStoreService:
    """Thin wrapper around flet-media-scanner.MediaScanner."""

    def __init__(self, page: ft.Page) -> None:
        self._page = page
        self._scanner: Any | None = None
        self._error: str = ""
        self._tried = False

    @property
    def available(self) -> bool:
        return self._scanner is not None

    @property
    def last_error(self) -> str:
        return self._error

    def ensure(self) -> Any | None:
        """Initialise the scanner once. Safe to call repeatedly."""
        if self._tried:
            return self._scanner
        self._tried = True

        if not is_android_page(self._page):
            self._scanner = None
            return None

        try:
            from flet_media_scanner import MediaScanner

            scanner = MediaScanner()
            self._page.services.append(scanner)
            self._scanner = scanner
            self._error = ""
            logger.info("MediaStore service initialised")
        except Exception as exc:
            self._error = str(exc)
            self._scanner = None
            logger.warning("MediaStore init failed: %s", exc)

        return self._scanner

    async def save_video(self, path: str, file_name: str) -> dict[str, Any]:
        """Publish a staged file to MediaStore. Returns result dict or raises."""
        scanner = self.ensure()
        if scanner is None:
            raise RuntimeError(self._error or "MediaStore not available")

        result = await scanner.save_video(path, file_name=file_name, album=ALBUM_NAME)
        if not result.success:
            raise RuntimeError(result.error or "MediaStore save failed")

        return {
            "content_uri": result.content_uri,
            "display_name": result.display_name or file_name,
            "mime_type": result.mime_type or "video/mp4",
            "relative_path": result.relative_path or f"Movies/{ALBUM_NAME}",
            "size": result.size or 0,
        }

    async def delete_video(self, content_uri: str) -> bool:
        scanner = self.ensure()
        if scanner is None:
            return False
        return await scanner.delete_video(content_uri)

    async def list_videos(self) -> list[dict[str, Any]]:
        scanner = self.ensure()
        if scanner is None:
            return []
        videos = await scanner.list_videos(album=ALBUM_NAME)
        return list(videos or [])
