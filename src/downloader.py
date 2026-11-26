"""
downloader.py - Download logic, URL resolution, platform detection, and
metadata helpers. The module has no direct Flet UI dependencies except shared
color constants used by the library view.
"""

from datetime import datetime
import json
import os
import re
import shutil
import sys
import time
from typing import Any

import flet as ft

PLATFORM_COLOR = {
    "TikTok": ft.Colors.PINK_900,
    "Instagram": ft.Colors.PURPLE_700,
    "YouTube": ft.Colors.RED_700,
    "Twitter/X": ft.Colors.BLUE_GREY_800,
    "Facebook": ft.Colors.BLUE_800,
    "Snapchat": ft.Colors.AMBER_800,
    "Reddit": ft.Colors.DEEP_ORANGE_700,
    "Pinterest": ft.Colors.RED_800,
    "Threads": ft.Colors.GREY_900,
    "Video": ft.Colors.BLUE_700,
}
PLATFORM_CHIP_COLOR = {
    "TikTok": ft.Colors.PINK_100,
    "Instagram": ft.Colors.PURPLE_100,
    "YouTube": ft.Colors.RED_100,
    "Twitter/X": ft.Colors.BLUE_GREY_100,
    "Facebook": ft.Colors.BLUE_100,
    "Snapchat": ft.Colors.AMBER_100,
    "Reddit": ft.Colors.DEEP_ORANGE_100,
    "Pinterest": ft.Colors.RED_100,
    "Threads": ft.Colors.GREY_200,
    "Video": ft.Colors.BLUE_100,
}

VIDEO_EXTENSIONS = (".mp4", ".mkv", ".mov", ".avi", ".webm", ".m4v", ".3gp")


def detect_platform(url: str) -> str:
    u = url.lower()
    if "tiktok.com" in u:
        return "TikTok"
    if "instagram.com" in u or "instagr.am" in u:
        return "Instagram"
    if "youtube.com" in u or "youtu.be" in u:
        return "YouTube"
    if "twitter.com" in u or "x.com" in u or "t.co/" in u:
        return "Twitter/X"
    if "facebook.com" in u or "fb.com" in u or "fb.watch" in u:
        return "Facebook"
    if "snapchat.com" in u:
        return "Snapchat"
    if "reddit.com" in u or "redd.it" in u:
        return "Reddit"
    if "pinterest.com" in u or "pin.it" in u:
        return "Pinterest"
    if "threads.net" in u or "threads.com" in u:
        return "Threads"
    return "Video"


def clean_ansi(text: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*[mGKH]", "", text)


def load_metadata(metadata_path: str) -> dict:
    try:
        if os.path.exists(metadata_path):
            with open(metadata_path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def save_metadata(metadata_path: str, meta: dict):
    try:
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


SHORT_URL_HOSTS = (
    "vm.tiktok.com",
    "vt.tiktok.com",
    "fb.watch",
    "facebook.com/share/",
    "t.co/",
    "t.snapchat.com",
    "snapchat.com/t/",
    "instagr.am",
    "pin.it",
    "redd.it",
    "dai.ly",
)


def resolve_short_url(url: str) -> str:
    """Follow redirects for short share links (vm/vt.tiktok.com, fb.watch, t.snapchat.com, etc.)."""
    u = url.lower()
    if any(host in u for host in SHORT_URL_HOSTS):
        import requests

        try:
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            }
            response = requests.head(url, headers=headers, allow_redirects=True, timeout=5)
            if response.url and response.url.startswith(("http://", "https://")):
                return response.url
        except Exception:
            pass
    return url


def preload_heavy_modules():
    """Pre-import yt_dlp and requests on a background thread after first UI paint."""
    try:
        import requests  # noqa: F401
        import yt_dlp  # noqa: F401
    except Exception:
        pass


def mark_files_recent(paths: list[str]) -> None:
    """Make Android media pickers sort newly downloaded files as recent."""
    now = time.time()
    for path in paths:
        if path and os.path.isfile(path):
            try:
                os.utime(path, (now, now))
            except Exception:
                pass


def collect_downloaded_paths(info) -> list[str]:
    """Return final downloaded file paths from yt-dlp info dictionaries."""
    seen = {}

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


def download_tiktok_direct(url: str, target_dir: str, on_status, on_progress) -> list[str] | None:
    """Fallback HD TikTok downloader via TikWM API (used if yt-dlp fails or is blocked)."""
    import requests

    try:
        on_status("Fetching HD video via backup service...")
        api_url = f"https://www.tikwm.com/api/?url={url}&hd=1"
        res = requests.get(api_url, timeout=10).json()
        if res.get("code") != 0 or "data" not in res:
            return None
        data = res["data"]
        # Prefer hdplay for highest quality, fallback to play or wmplay
        play_url = data.get("hdplay") or data.get("play") or data.get("wmplay")
        if not play_url:
            return None

        raw_title = data.get("title") or "tiktok_video"
        safe_title = re.sub(r'[\\/*?:"<>|]', "", raw_title)[:80].strip() or "tiktok_video"
        filename = f"{safe_title}.mp4"
        filepath = os.path.join(target_dir, filename)

        counter = 1
        base, ext = os.path.splitext(filepath)
        while os.path.exists(filepath):
            filepath = f"{base}_{counter}{ext}"
            counter += 1

        on_status("Downloading HD video...")
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        with requests.get(play_url, headers=headers, stream=True, timeout=25) as r:
            r.raise_for_status()
            total_size = int(r.headers.get("content-length") or data.get("hd_size") or data.get("size") or 0)
            downloaded = 0
            with open(filepath, "wb") as f:
                for chunk in r.iter_content(chunk_size=65536):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            pct = min(downloaded / total_size, 0.99)
                            on_progress(pct)
                            on_status(f"Downloading: {int(pct * 100)}%")

        on_progress(1.0)
        on_status("Preparing file...")
        return [filepath]
    except Exception:
        return None


def run_download(
    url: str,
    target_dir: str,
    cookie_path: str,
    metadata_path: str,
    on_status,
    on_progress,
    on_finish,
    on_error,
    page,
    schedule_media_scan_later=None,
):
    """
    Execute a yt-dlp download synchronously in a worker thread.

    Returns staged video data for the async app layer to publish through
    MediaStore. The metadata_path, on_finish, and schedule_media_scan_later
    arguments are retained for call-site compatibility.
    """
    del metadata_path, on_finish, schedule_media_scan_later

    # Resolve shortened/share URLs (e.g. vt.tiktok.com, fb.watch, facebook.com/share, t.snapchat.com)
    url = resolve_short_url(url)

    downloaded_paths = []

    def _hook(d):
        if d["status"] == "downloading":
            raw = d.get("_percent_str", "0%")
            pct_str = clean_ansi(raw).replace("%", "").strip()
            try:
                on_progress(float(pct_str) / 100.0)
            except ValueError:
                pass
            on_status(f"Downloading: {raw.strip()}")
            # NOTE: page.update() must NOT be called from a worker thread.
            # The on_status/on_progress callbacks dispatch via call_soon_threadsafe.
        elif d["status"] == "finished":
            filename = d.get("filename")
            if filename:
                downloaded_paths.append(filename)
            on_progress(1.0)
            on_status("Preparing file...")
            # NOTE: page.update() removed — thread-unsafe here.

    os.makedirs(target_dir, exist_ok=True)

    has_ffmpeg = shutil.which("ffmpeg") is not None
    # On mobile or systems without ffmpeg, always request pre-muxed video (b[ext=mp4]/b)
    # so yt-dlp downloads the complete HD video directly without requiring an ffmpeg merge pass.
    if has_ffmpeg:
        format_spec = "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/bv*+ba/b/best"
    else:
        format_spec = "b[ext=mp4]/b"

    ydl_opts: Any = {
        "outtmpl": os.path.join(target_dir, "%(title).100s.%(ext)s"),
        "progress_hooks": [_hook],
        "updatetime": False,
        "format": format_spec,
        "writesubtitles": False,
        "writeautomaticsub": False,
        "writethumbnail": False,
        "noplaylist": True,
        "cachedir": False,
        "js_runtimes": {},
        "extractor_args": {
            "youtube": {
                "player_client": ["default", "web_embedded", "-android_vr"],
            }
        },
        "sleep_interval": 0,
        "max_sleep_interval": 0,
        "socket_timeout": 10,
        "retries": 2,
        "fragment_retries": 2,
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
    del cookie_path  # Cookie-free path avoids stale cookie blocks and parsing overhead.

    before = {
        f: os.path.getmtime(os.path.join(target_dir, f))
        for f in os.listdir(target_dir)
        if f.lower().endswith(VIDEO_EXTENSIONS)
    }

    try:
        if "yt_dlp" not in sys.modules:
            on_status("Preparing downloader (first run only)...")

        from yt_dlp import YoutubeDL

        on_status("Analyzing video...")
        with YoutubeDL(ydl_opts) as ydl:
            on_status("Downloading video...")
            info = ydl.extract_info(url, download=True)
            downloaded_paths.extend(collect_downloaded_paths(info))

        after = {
            f: os.path.getmtime(os.path.join(target_dir, f))
            for f in os.listdir(target_dir)
            if f.lower().endswith(VIDEO_EXTENSIONS)
        }
        new_files = set(after) - set(before)
        updated_files = {
            f for f, mtime in after.items()
            if f in before and mtime > before[f]
        }
        detected_paths = [
            path
            for path in downloaded_paths
            if path and os.path.exists(path) and path.lower().endswith(VIDEO_EXTENSIONS)
        ]
        detected_files = {os.path.basename(path) for path in detected_paths}
        saved_files = sorted(new_files | updated_files | detected_files)

        if not saved_files:
            if detect_platform(url) == "TikTok":
                on_status("Retrying with backup HD downloader...")
                fallback_files = download_tiktok_direct(url, target_dir, on_status, on_progress)
                if fallback_files:
                    mark_files_recent(fallback_files)
                    on_status("Publishing video to Gallery...")
                    print("[VidSaver] Download succeeded via Backup HD API (fallback)")
                    return {
                        "paths": fallback_files,
                        "platform": "TikTok",
                        "url": url,
                        "date": datetime.now().strftime("%d %b %Y"),
                        "engine": "Backup HD API",
                    }
            platform = detect_platform(url)
            on_error(
                f"No video file was saved. {platform} may require fresh cookies, "
                "login access, or the link may not contain a downloadable video."
            )
            return None

        staged_paths = [os.path.join(target_dir, fname) for fname in saved_files]
        mark_files_recent(staged_paths)
        on_status("Publishing video to Gallery...")
        print("[VidSaver] Download succeeded via yt-dlp")
        return {
            "paths": staged_paths,
            "platform": detect_platform(url),
            "url": url,
            "date": datetime.now().strftime("%d %b %Y"),
            "engine": "yt-dlp",
        }
    except Exception as exc:
        err_msg = str(exc)
        # If yt-dlp fails (e.g. timeout / ISP block on vt.tiktok.com), use the HD API as fallback
        if detect_platform(url) == "TikTok":
            on_status("Retrying with backup HD downloader...")
            fallback_files = download_tiktok_direct(url, target_dir, on_status, on_progress)
            if fallback_files:
                mark_files_recent(fallback_files)
                on_status("Publishing video to Gallery...")
                print("[VidSaver] Download succeeded via Backup HD API (fallback)")
                return {
                    "paths": fallback_files,
                    "platform": "TikTok",
                    "url": url,
                    "date": datetime.now().strftime("%d %b %Y"),
                    "engine": "Backup HD API",
                }

        if "timed out" in err_msg.lower():
            platform = detect_platform(url)
            on_error(f"Connection to {platform} timed out. If {platform} is blocked or restricted in your region, please enable a VPN and try again.")
        else:
            on_error(err_msg)
        return None
