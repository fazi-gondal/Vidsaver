from dataclasses import dataclass
import json
import os
from typing import Any, Optional

import flet as ft


@dataclass
class SaveResult:
    success: bool = False
    content_uri: str = ""
    display_name: str = ""
    mime_type: str = ""
    relative_path: str = ""
    source_path: str = ""
    size: int = 0
    error: str = ""


@ft.control("MediaScanner")
class MediaScanner(ft.Service):
    """
    Android media service for publishing videos through MediaStore.

    New downloads should use save_video(). scan_media() is kept only for
    legacy files that already exist in public storage and need Gallery indexing.
    """

    on_saved: Optional[ft.EventHandler[Any]] = None
    on_scanned: Optional[ft.EventHandler[Any]] = None

    async def save_video(
        self,
        file_path: str,
        file_name: str | None = None,
        album: str = "Vidsaver",
    ) -> SaveResult:
        """
        Copy an app-private video into Android MediaStore.Video.

        On Android 10+ this publishes to Movies/<album> without requiring
        broad storage permissions or a media scan.
        """
        if not file_path or not os.path.exists(file_path):
            return SaveResult(error=f"file does not exist: {file_path}")

        try:
            result = await self._invoke_method(
                "save_video",
                {
                    "path": file_path,
                    "file_name": file_name or os.path.basename(file_path),
                    "album": album,
                },
                timeout=60.0,
            )
            payload = json.loads(result) if result else {}
            return SaveResult(
                success=bool(payload.get("success")),
                content_uri=str(payload.get("content_uri") or ""),
                display_name=str(payload.get("display_name") or ""),
                mime_type=str(payload.get("mime_type") or ""),
                relative_path=str(payload.get("relative_path") or ""),
                source_path=str(payload.get("source_path") or file_path),
                size=int(payload.get("size") or 0),
                error=str(payload.get("error") or ""),
            )
        except Exception as e:
            return SaveResult(error=str(e), source_path=file_path)

    async def scan_media(self, file_path: str) -> bool:
        """
        Scan a legacy public media file so it appears in Gallery/Photos.

        New downloads should use save_video() instead; MediaStore inserts do
        not need this scan.
        """
        if not file_path or not os.path.exists(file_path):
            print(f"[MediaScanner] scan_media: file does not exist: {file_path}")
            return False
        try:
            result = await self._invoke_method(
                "scan_media",
                {"path": file_path},
                timeout=15.0,
            )
            success = result == "true"
            print(f"[MediaScanner] scan_media: {file_path} -> result={result} success={success}")
            return success
        except Exception as e:
            print(f"[MediaScanner] scan_media error: {file_path}: {e}")
            return False

    async def delete_video(self, content_uri: str) -> bool:
        """Delete a MediaStore item by its content URI."""
        if not content_uri:
            return False
        try:
            result = await self._invoke_method(
                "delete_video",
                {"content_uri": content_uri},
                timeout=15.0,
            )
            payload = json.loads(result) if result else {}
            return bool(payload.get("success"))
        except Exception as e:
            print(f"[MediaScanner] delete_video error: {content_uri}: {e}")
            return False

    async def list_videos(self, album: str = "Vidsaver") -> list[dict]:
        """List videos previously saved to the MediaStore album."""
        try:
            result = await self._invoke_method(
                "list_videos",
                {"album": album},
                timeout=15.0,
            )
            payload = json.loads(result) if result else {}
            videos = payload.get("videos") or []
            return videos if isinstance(videos, list) else []
        except Exception as e:
            print(f"[MediaScanner] list_videos error: {e}")
            return []
