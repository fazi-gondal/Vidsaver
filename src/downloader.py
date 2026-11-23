"""
downloader.py - Download logic, URL resolution, platform detection, and
metadata helpers. The module has no direct Flet UI dependencies except shared
color constants used by the library view.
"""

from datetime import datetime
import json
import os
import re
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
    "Video": ft.Colors.BLUE_700,
}
PLATFORM_CHIP_COLOR = {
    "TikTok": ft.Colors.PINK_100,
    "Instagram": ft.Colors.PURPLE_100,
    "YouTube": ft.Colors.RED_100,
    "Twitter/X": ft.Colors.BLUE_GREY_100,
    "Facebook": ft.Colors.BLUE_100,
    "Video": ft.Colors.BLUE_100,
}

VIDEO_EXTENSIONS = (".mp4", ".mkv", ".mov", ".avi", ".webm", ".m4v", ".3gp")


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


def resolve_short_url(url: str) -> str:
    """Leave short-link resolution to yt-dlp to avoid an extra network request."""
    return url


def preload_heavy_modules():
    """Kept for compatibility; downloads import network packages on demand."""
    return


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



def analyze_media(url: str, cookie_path: str) -> dict | None:
    """
    Extract metadata and available formats without downloading.
    Returns a dict suitable for Home preview UI, or None on failure.
    """
    url = resolve_short_url(url)
    platform = detect_platform(url)

    is_likely_playlist = any(
        token in url.lower()
        for token in ("list=", "/playlist", "/sets/", "playlist?")
    )
    ydl_opts: Any = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "noplaylist": not is_likely_playlist,
        "socket_timeout": 15,
        "http_headers": {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        },
    }
    if cookie_path and os.path.exists(cookie_path):
        ydl_opts["cookiefile"] = cookie_path

    try:
        from yt_dlp import YoutubeDL

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception as exc:
        error = str(exc)
        if "timed out" in error.lower() or "timeout" in error.lower():
            error = f"Connection to {platform} timed out. Check your internet connection and try again."
        return {
            "ok": False,
            "error": error,
            "url": url,
            "platform": platform,
        }

    if not info:
        return {"ok": False, "error": "No media information returned.", "url": url, "platform": platform}

    # Playlist: return entries summary for Phase 3 selection
    if info.get("_type") == "playlist" or info.get("entries"):
        entries = list(info.get("entries") or [])
        items = []
        for e in entries[:50]:
            if not e:
                continue
            items.append(
                {
                    "id": e.get("id") or "",
                    "title": e.get("title") or "Untitled",
                    "url": e.get("webpage_url") or e.get("url") or url,
                    "duration": e.get("duration"),
                    "thumbnail": e.get("thumbnail") or "",
                }
            )
        return {
            "ok": True,
            "is_playlist": True,
            "url": url,
            "platform": platform,
            "title": info.get("title") or "Playlist",
            "entries": items,
            "entry_count": len(items),
        }

    formats_raw = info.get("formats") or []
    quality_options: list[dict] = []
    seen_heights: set[int] = set()
    best_by_height: dict[int, dict] = {}
    for f in formats_raw:
        height = f.get("height")
        if not height:
            continue
        vcodec = f.get("vcodec") or "none"
        if vcodec == "none":
            continue
        h = int(height)
        tbr = float(f.get("tbr") or 0)
        prev = best_by_height.get(h)
        if prev is None or tbr >= float(prev.get("tbr") or 0):
            fps = f.get("fps")
            label = f"{h}p"
            if fps:
                try:
                    label = f"{h}p · {int(float(fps))}fps"
                except (TypeError, ValueError):
                    pass
            best_by_height[h] = {
                "height": h,
                "format_id": str(f.get("format_id") or ""),
                "ext": f.get("ext") or "mp4",
                "label": label,
                "tbr": f.get("tbr"),
                "fps": fps,
                "vcodec": vcodec,
                "acodec": f.get("acodec") or "none",
            }
    quality_options = sorted(best_by_height.values(), key=lambda x: x["height"], reverse=True)

    # Always offer a sensible default "best" option at the top
    quality_options.insert(
        0,
        {
            "height": 0,
            "format_id": "",
            "ext": "mp4",
            "label": "Best available",
            "tbr": None,
            "fps": None,
            "vcodec": "",
            "acodec": "",
        },
    )
    # Audio-only convenience
    quality_options.append(
        {
            "height": -1,
            "format_id": "bestaudio",
            "ext": "m4a",
            "label": "Audio only",
            "tbr": None,
            "fps": None,
            "vcodec": "none",
            "acodec": "best",
            "audio_only": True,
        },
    )

    thumb = info.get("thumbnail") or ""
    if not thumb and info.get("thumbnails"):
        try:
            thumb = info["thumbnails"][-1].get("url") or ""
        except Exception:
            thumb = ""

    return {
        "ok": True,
        "is_playlist": False,
        "url": url,
        "platform": platform,
        "title": info.get("title") or "Video",
        "duration": info.get("duration"),
        "thumbnail": thumb,
        "uploader": info.get("uploader") or info.get("channel") or "",
        "quality_options": quality_options,
        "webpage_url": info.get("webpage_url") or url,
    }


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
    format_selector: str | None = None,
    retries: int | None = None,
    concurrent_fragments: int | None = None,
    rate_limit: str | None = None,
    writesubtitles: bool = False,
    subtitle_langs: str = "en",
    timeout_seconds: int = 30,
    audio_format: str = "m4a",
    embed_thumbnail: bool = True,
    embed_metadata: bool = True,
    keep_originals: bool = False,
    container: str = "mp4",
):
    """
    Execute a yt-dlp download synchronously in a worker thread.

    Returns staged video data for the async app layer to publish through
    MediaStore. The metadata_path, on_finish, and schedule_media_scan_later
    arguments are retained for call-site compatibility.
    """
    del metadata_path, on_finish, schedule_media_scan_later

    # yt-dlp handles shortened URLs directly, without a separate preflight request.
    url = resolve_short_url(url)

    downloaded_paths = []

    def _hook(d):
        if d["status"] == "downloading":
            raw = d.get("_percent_str", "0%")
            pct_str = clean_ansi(raw).replace("%", "").strip()
            try:
                fraction = float(pct_str) / 100.0
            except ValueError:
                fraction = 0.0
            # Prefer numeric fields when yt-dlp provides them
            downloaded = d.get("downloaded_bytes") or 0
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            speed = d.get("speed")
            eta = d.get("eta")
            try:
                on_progress(
                    {
                        "fraction": fraction,
                        "downloaded_bytes": int(downloaded or 0),
                        "total_bytes": int(total) if total else None,
                        "speed_bytes_per_sec": float(speed) if speed else None,
                        "eta_seconds": float(eta) if eta is not None else None,
                    }
                )
            except TypeError:
                # Legacy callbacks that only accept a float
                try:
                    on_progress(fraction)
                except Exception:
                    pass
            on_status(f"Downloading: {raw.strip()}")
        elif d["status"] == "finished":
            filename = d.get("filename")
            if filename:
                downloaded_paths.append(filename)
            try:
                on_progress({"fraction": 1.0})
            except TypeError:
                on_progress(1.0)
            on_status("Preparing file...")

    os.makedirs(target_dir, exist_ok=True)

    ydl_opts: Any = {
        "outtmpl": os.path.join(target_dir, "%(title).100s.%(ext)s"),
        "progress_hooks": [_hook],
        "updatetime": False,
        "format": format_selector
        or "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/bv*+ba/b/best",
        "writesubtitles": bool(writesubtitles),
        "writeautomaticsub": bool(writesubtitles),
        "writethumbnail": bool(embed_thumbnail),
        "embedthumbnail": bool(embed_thumbnail),
        "subtitleslangs": [
            value.strip()
            for value in str(subtitle_langs or "en").split(",")
            if value.strip()
        ],
        "keepvideo": bool(keep_originals),
        "noplaylist": True,
        "sleep_interval": 0,
        "max_sleep_interval": 0,
        "socket_timeout": max(5, min(300, int(timeout_seconds or 30))),
        "retries": retries if retries is not None else 2,
        "fragment_retries": retries if retries is not None else 2,
        "concurrent_fragment_downloads": concurrent_fragments if concurrent_fragments is not None else 4,
        "merge_output_format": container if container in ("mp4", "mkv", "webm") else "mp4",
        "quiet": True,
        "no_warnings": True,
        **({"ratelimit": rate_limit} if rate_limit else {}),
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
    if cookie_path and os.path.exists(cookie_path):
        ydl_opts["cookiefile"] = cookie_path
    postprocessors: list[dict] = []
    if embed_metadata:
        postprocessors.append({"key": "FFmpegMetadata"})
    if embed_thumbnail:
        postprocessors.append(
            {"key": "EmbedThumbnail", "already_have_thumbnail": False}
        )
    if format_selector and "bestaudio" in format_selector:
        postprocessors.append(
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": str(audio_format or "m4a"),
                "preferredquality": "192",
            }
        )
        ydl_opts["keepvideo"] = bool(keep_originals)
    if postprocessors:
        ydl_opts["postprocessors"] = postprocessors

    before = {
        f: os.path.getmtime(os.path.join(target_dir, f))
        for f in os.listdir(target_dir)
        if f.lower().endswith(VIDEO_EXTENSIONS)
    }

    try:
        if "yt_dlp" not in sys.modules:
            on_status("Preparing downloader (first run only)...")
            page.update()

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
            on_error(
                "No video file was saved. Instagram may require fresh cookies, "
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
