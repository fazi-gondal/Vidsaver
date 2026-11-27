"""
storage.py - Storage paths, URL validation, and Android MediaStore helpers.
"""

from datetime import datetime
import os
import tempfile
import time
from urllib.parse import urlparse

import flet as ft

VIDEO_DOMAINS = (
    "tiktok.com",
    "vm.tiktok.com",
    "vt.tiktok.com",
    "instagram.com",
    "instagr.am",
    "youtube.com",
    "youtu.be",
    "twitter.com",
    "x.com",
    "t.co",
    "facebook.com",
    "fb.com",
    "fb.watch",
    "snapchat.com",
    "reddit.com",
    "v.redd.it",
    "redd.it",
    "pinterest.com",
    "pin.it",
    "threads.net",
    "threads.com",
    "vimeo.com",
    "dailymotion.com",
    "dai.ly",
    "twitch.tv",
    "linkedin.com",
    "likee.video",
    "snackvideo.com",
    "bilibili.com",
    "b23.tv",
)


def is_android_page(page: ft.Page) -> bool:
    platform = getattr(page, "platform", None)
    platform_value = getattr(platform, "value", platform)
    return platform == ft.PagePlatform.ANDROID or platform_value == "android"


def is_http_url(text: str) -> bool:
    if not text:
        return False
    parsed = urlparse(text.strip())
    return parsed.scheme.lower() in ("http", "https") and bool(parsed.netloc)


def is_video_url(text: str) -> bool:
    if not is_http_url(text):
        return False
    value = text.strip().lower()
    return any(domain in value for domain in VIDEO_DOMAINS)


def ensure_storage_paths(page: ft.Page):
    download_dir = getattr(page, "_download_dir", None)
    metadata_path = getattr(page, "_metadata_path", None)
    if download_dir and metadata_path:
        return download_dir, metadata_path

    data_dir = os.environ.get("FLET_APP_STORAGE_DATA") or os.getcwd()
    metadata_path = os.path.join(data_dir, "metadata.json")
    if is_android_page(page):
        download_dir = os.path.join(tempfile.gettempdir(), "vidsaver-staging")
    else:
        user_profile = os.environ.get("USERPROFILE") or os.environ.get("HOME") or ""
        download_dir = (
            os.path.join(user_profile, "Downloads", "VidSaver")
            if user_profile
            else "./downloads"
        )

    os.makedirs(download_dir, exist_ok=True)
    setattr(page, "_download_dir", download_dir)
    setattr(page, "_metadata_path", metadata_path)
    return download_dir, metadata_path


async def init_storage_paths(page: ft.Page):
    """Initialize stable metadata and temporary staging paths."""
    download_dir = getattr(page, "_download_dir", None)
    metadata_path = getattr(page, "_metadata_path", None)
    if download_dir and metadata_path:
        return download_dir, metadata_path

    data_dir = os.environ.get("FLET_APP_STORAGE_DATA") or os.getcwd()
    if is_android_page(page):
        try:
            storage_paths = getattr(page, "storage_paths", None)
            if storage_paths:
                temp_dir = await storage_paths.get_temporary_directory()
            else:
                sp = ft.StoragePaths()
                page.services.append(sp)
                temp_dir = await sp.get_temporary_directory()
        except Exception:
            temp_dir = tempfile.gettempdir()
        metadata_path = os.path.join(data_dir, "metadata.json")
        download_dir = os.path.join(temp_dir, "vidsaver-staging")
    else:
        metadata_path = os.path.join(data_dir, "metadata.json")
        user_profile = os.environ.get("USERPROFILE") or os.environ.get("HOME") or ""
        download_dir = (
            os.path.join(user_profile, "Downloads", "VidSaver")
            if user_profile
            else "./downloads"
        )

    os.makedirs(os.path.dirname(metadata_path), exist_ok=True)
    os.makedirs(download_dir, exist_ok=True)
    setattr(page, "_download_dir", download_dir)
    setattr(page, "_metadata_path", metadata_path)
    return download_dir, metadata_path


def ensure_media_scanner(page: ft.Page):
    """Initialize the local media service on Android only."""
    if hasattr(page, "_media_scanner"):
        return getattr(page, "_media_scanner")

    if not is_android_page(page):
        setattr(page, "_media_scanner", None)
        setattr(page, "_media_scanner_error", "")
        return None

    try:
        from flet_media_scanner import MediaScanner

        scanner = MediaScanner()
        page.services.append(scanner)
        setattr(page, "_media_scanner", scanner)
        setattr(page, "_media_scanner_error", "")
        page.update()
        print("[VidSaver] MediaStore service initialized")
    except Exception as e:
        setattr(page, "_media_scanner_error", str(e))
        print(f"[VidSaver] MediaStore service init failed: {e}")
        setattr(page, "_media_scanner", None)

    return getattr(page, "_media_scanner")


def get_clipboard(page: ft.Page) -> ft.Clipboard:
    """Return a stable Clipboard service instance (created once per session)."""
    clipboard = getattr(page, "_clipboard", None)
    if clipboard is None:
        clipboard = ft.Clipboard()
        setattr(page, "_clipboard", clipboard)
    return clipboard


async def publish_download_result(page: ft.Page, download_result: dict, metadata_path: str):
    """Publish staged downloads to MediaStore on Android and update metadata."""
    from downloader import load_metadata, save_metadata

    if not download_result or not download_result.get("paths"):
        return False, "No video file was saved."

    meta = load_metadata(metadata_path)
    published = 0
    last_error = ""

    for path in download_result["paths"]:
        file_name = os.path.basename(path)
        size = os.path.getsize(path) if os.path.exists(path) else 0
        entry = {
            "platform": download_result["platform"],
            "url": download_result["url"],
            "date": download_result["date"],
            "created_at": time.time(),
            "source_path": path,
            "size": size,
        }

        android = is_android_page(page)
        scanner = ensure_media_scanner(page) if android else None
        if android and scanner is None:
            init_error = getattr(page, "_media_scanner_error", "")
            last_error = (
                f"MediaStore service is not available: {init_error}"
                if init_error
                else "MediaStore service is not available."
            )
            continue

        if scanner is not None:
            result = await scanner.save_video(path, file_name=file_name, album="Vidsaver")
            if not result.success:
                last_error = result.error or "MediaStore save failed."
                continue

            display_name = result.display_name or file_name
            entry.update(
                {
                    "content_uri": result.content_uri,
                    "display_name": display_name,
                    "mime_type": result.mime_type,
                    "relative_path": result.relative_path,
                    "size": result.size or size,
                }
            )
            meta[display_name] = entry
            try:
                os.remove(path)
            except Exception:
                pass
        else:
            meta[file_name] = entry

        published += 1

    if published:
        save_metadata(metadata_path, meta)
        return True, ""
    return False, last_error or "Unable to publish video to Gallery."


async def delete_saved_video(page: ft.Page, info: dict) -> bool:
    """Delete a saved video from Android MediaStore or local filesystem."""
    content_uri = info.get("content_uri") or ""
    source_path = info.get("source_path") or info.get("file_path") or ""

    if is_android_page(page) and content_uri:
        scanner = ensure_media_scanner(page)
        if scanner is None:
            return False
        return await scanner.delete_video(content_uri)

    if source_path and os.path.exists(source_path):
        try:
            os.remove(source_path)
            return True
        except Exception:
            return False

    return not content_uri and not source_path


async def sync_saved_videos(page: ft.Page, metadata_path: str) -> bool:
    """Restore app metadata from Android MediaStore after app updates."""
    if not is_android_page(page):
        return False

    scanner = ensure_media_scanner(page)
    if scanner is None:
        return False

    from downloader import load_metadata, save_metadata

    videos = await scanner.list_videos(album="Vidsaver")
    if not videos:
        return False

    meta = load_metadata(metadata_path)
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
        save_metadata(metadata_path, meta)
    return changed
