"""Storage path helpers. Paths are resolved lazily and cached on the page."""

from __future__ import annotations

import os
import tempfile
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import flet as ft

from vidsaver.utils.platform import is_android_page


def ensure_storage_paths(page: ft.Page) -> tuple[str, str]:
    """Return (download_dir, metadata_path), creating dirs as needed.

    Safe to call from the first frame; does not touch MediaScanner.
    """
    if getattr(page, "_download_dir", None):
        return page._download_dir, page._metadata_path  # type: ignore[attr-defined]

    data_dir = os.environ.get("FLET_APP_STORAGE_DATA") or os.getcwd()
    metadata_path = os.path.join(data_dir, "metadata.json")

    if is_android_page(page):
        download_dir = os.path.join(tempfile.gettempdir(), "vidsaver-staging")
    else:
        user_profile = os.environ.get("USERPROFILE") or os.environ.get("HOME") or ""
        download_dir = (
            os.path.join(user_profile, "Downloads", "VidSaver")
            if user_profile
            else os.path.join(".", "downloads")
        )

    os.makedirs(os.path.dirname(metadata_path) or ".", exist_ok=True)
    os.makedirs(download_dir, exist_ok=True)

    page._download_dir = download_dir  # type: ignore[attr-defined]
    page._metadata_path = metadata_path  # type: ignore[attr-defined]
    return download_dir, metadata_path


def get_thumbnails_dir() -> str:
    """Return the app-private thumbnails directory (never scanned by the gallery).

    Stored inside FLET_APP_STORAGE_DATA alongside metadata.json so it is
    invisible to Android MediaStore / Windows Explorer photo views.
    """
    data_dir = os.environ.get("FLET_APP_STORAGE_DATA") or os.getcwd()
    thumb_dir = os.path.join(data_dir, "thumbnails")
    os.makedirs(thumb_dir, exist_ok=True)
    return thumb_dir


def get_cookie_path() -> str:
    """Path to cookies.txt (next to the app entry or in data dir)."""
    # Prefer the traditional location used by the original project
    candidates = [
        os.path.join(os.path.dirname(__file__), "..", "..", "cookies.txt"),
        os.path.join(os.environ.get("FLET_APP_STORAGE_DATA") or os.getcwd(), "cookies.txt"),
        os.path.join(os.getcwd(), "cookies.txt"),
        os.path.join(os.getcwd(), "src", "cookies.txt"),
    ]
    for path in candidates:
        path = os.path.normpath(path)
        if os.path.isfile(path):
            return path
    # Return a default even if missing — cookies are now optional
    return os.path.normpath(candidates[0])
