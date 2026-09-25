"""yt-dlp download service. Runs work in a thread; never calls page.update()."""

from __future__ import annotations

import base64
import os
import re
import subprocess
import sys
import time
from collections.abc import Callable
from datetime import datetime

from vidsaver.config.constants import VIDEO_EXTENSIONS
from vidsaver.models.video import DownloadResult
from vidsaver.utils.paths import get_cookie_path


def extract_thumbnail_b64(video_path: str, timestamp: str = "00:00:01") -> str:
    """Extract a single frame from *video_path* via ffmpeg and return it as
    a base64-encoded JPEG string.  Returns "" on any failure."""
    if not os.path.isfile(video_path):
        return ""
    try:
        result = subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-ss", timestamp,
                "-i", video_path,
                "-vframes", "1",
                "-f", "image2",
                "-vcodec", "mjpeg",
                "pipe:1",   # write JPEG bytes to stdout
            ],
            capture_output=True,
            timeout=8,
            check=False,
        )
        if result.returncode == 0 and result.stdout:
            return base64.b64encode(result.stdout).decode()
    except Exception:
        pass
    return ""


def detect_platform(url: str) -> str:
    u = url.lower()
    if "tiktok.com" in u:
        return "TikTok"
    if "instagram.com" in u:
        return "Instagram"
    if "youtube.com" in u or "youtu.be" in u:
        return "YouTube"
    if "twitter.com" in u or "x.com" in u:
        return "Twitter/X"
    if "facebook.com" in u or "fb.com" in u:
        return "Facebook"
    return "Video"


def clean_ansi(text: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*[mGKH]", "", text)


def resolve_short_url(url: str) -> str:
    """Follow redirects for short TikTok links. Lazy-imports requests."""
    if "tiktok.com" not in url:
        return url
    try:
        import requests

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        response = requests.head(url, headers=headers, allow_redirects=True, timeout=10)
        return response.url
    except Exception:
        return url


def mark_files_recent(paths: list[str]) -> None:
    now = time.time()
    for path in paths:
        if path and os.path.isfile(path):
            try:
                os.utime(path, (now, now))
            except Exception:
                pass


def collect_downloaded_paths(info) -> list[str]:
    seen: dict[str, None] = {}

    def add_from(item):
        if not isinstance(item, dict):
            return
        for download in item.get("requested_downloads") or []:
            path = download.get("filepath") or download.get("filename")
            if path:
                seen[path] = None
        for key in ("filepath", "_filename", "filename"):
            path = item.get(key)
            if path:
                seen[path] = None
        for entry in item.get("entries") or []:
            add_from(entry)

    add_from(info)
    return list(seen.keys())


class DownloadService:
    """Synchronous download runner intended for asyncio.to_thread."""

    def __init__(self) -> None:
        self._ytdlp_ready = False

    def warm(self) -> None:
        """Import yt-dlp in background so the first download is fast."""
        if self._ytdlp_ready:
            return
        try:
            import yt_dlp  # noqa: F401

            self._ytdlp_ready = True
        except Exception:
            pass

    def run(
        self,
        url: str,
        target_dir: str,
        on_status: Callable[[str], None] | None = None,
        on_progress: Callable[[float], None] | None = None,
    ) -> DownloadResult:
        """
        Execute yt-dlp download synchronously.

        Callbacks are invoked from the worker thread — callers must marshal
        them onto the UI loop (e.g. via page.run_task or call_soon_threadsafe).
        """
        status = on_status or (lambda _: None)
        progress = on_progress or (lambda _: None)

        url = resolve_short_url(url)
        cookie_path = get_cookie_path()
        os.makedirs(target_dir, exist_ok=True)

        downloaded_paths: list[str] = []

        def _hook(d: dict) -> None:
            if d.get("status") == "downloading":
                raw = d.get("_percent_str", "0%")
                pct_str = clean_ansi(str(raw)).replace("%", "").strip()
                try:
                    progress(float(pct_str) / 100.0)
                except ValueError:
                    pass
                status(f"Downloading: {clean_ansi(str(raw)).strip()}")
            elif d.get("status") == "finished":
                filename = d.get("filename")
                if filename:
                    downloaded_paths.append(filename)
                progress(1.0)
                status("Preparing file...")

        ydl_opts: dict = {
            "outtmpl": os.path.join(target_dir, "%(title).100s.%(ext)s"),
            "progress_hooks": [_hook],
            "updatetime": False,
            "format": "b[ext=mp4]/b",
            "writesubtitles": False,
            "writeautomaticsub": False,
            # Thumbnails are extracted in-memory by ffmpeg — no separate file.
            "writethumbnail": False,
            "noplaylist": True,
            "sleep_interval": 0,
            "max_sleep_interval": 0,
            "socket_timeout": 15,
            "retries": 5,
            "fragment_retries": 5,
            "concurrent_fragment_downloads": 4,
            "quiet": True,
            "no_warnings": True,
            "http_headers": {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                "Accept": (
                    "text/html,application/xhtml+xml,application/xml;"
                    "q=0.9,image/avif,image/webp,*/*;q=0.8"
                ),
                "Accept-Language": "en-US,en;q=0.5",
            },
        }

        # Cookies are optional — only pass if the file exists
        if os.path.isfile(cookie_path):
            ydl_opts["cookiefile"] = cookie_path

        before = {
            f: os.path.getmtime(os.path.join(target_dir, f))
            for f in os.listdir(target_dir)
            if f.lower().endswith(VIDEO_EXTENSIONS)
        }

        try:
            if "yt_dlp" not in sys.modules:
                status("Preparing downloader (first run only)...")
                # Do NOT call page.update() here — we are on a worker thread.

            from yt_dlp import YoutubeDL

            status("Analyzing video...")
            with YoutubeDL(ydl_opts) as ydl:
                status("Downloading video...")
                info = ydl.extract_info(url, download=True)
                downloaded_paths.extend(collect_downloaded_paths(info))

            after = {
                f: os.path.getmtime(os.path.join(target_dir, f))
                for f in os.listdir(target_dir)
                if f.lower().endswith(VIDEO_EXTENSIONS)
            }
            new_files = set(after) - set(before)
            updated_files = {f for f, mtime in after.items() if f in before and mtime > before[f]}
            detected_paths = [
                path
                for path in downloaded_paths
                if path and os.path.exists(path) and path.lower().endswith(VIDEO_EXTENSIONS)
            ]
            detected_files = {os.path.basename(path) for path in detected_paths}
            saved_files = sorted(new_files | updated_files | detected_files)

            if not saved_files:
                return DownloadResult(
                    error=(
                        "No video file was saved. Instagram may require fresh cookies, "
                        "login access, or the link may not contain a downloadable video."
                    )
                )

            staged_paths = [os.path.join(target_dir, fname) for fname in saved_files]
            mark_files_recent(staged_paths)

            # Extract one frame per video in-memory (no file written to disk)
            status("Extracting thumbnails...")
            thumbs: dict[str, str] = {}
            for path in staged_paths:
                b64 = extract_thumbnail_b64(path)
                if b64:
                    thumbs[path] = b64

            status("Publishing video...")
            return DownloadResult(
                paths=staged_paths,
                platform=detect_platform(url),
                url=url,
                date=datetime.now().strftime("%d %b %Y"),
                thumbnails=thumbs,
            )
        except Exception as exc:
            return DownloadResult(error=str(exc))
