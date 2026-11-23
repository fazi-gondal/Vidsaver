"""Application-wide constants for Vidsaver mobile upgrade."""

from __future__ import annotations

APP_NAME = "Vidsaver"
APP_AUTHOR = "Fazi-Gondal"
APP_TITLE = "Vidsaver"
APP_VERSION = "1.5.0"

DEVELOPER_NAME = "Faizan Gondal"
DEVELOPER_GITHUB_URL = "https://github.com/fazi-gondal"
REPO_URL = "https://github.com/fazi-gondal/Vidsaver"
REPO_ISSUES_URL = f"{REPO_URL}/issues"
APP_LICENSE = "MIT"

# Gallery album used by flet-media-scanner on Android
MEDIA_ALBUM = "Vidsaver"

# Staging subdirectory under temp storage
STAGING_DIR_NAME = "vidsaver-staging"

# Persistence filenames (under app data dir)
METADATA_FILENAME = "metadata.json"
SETTINGS_FILENAME = "settings.json"
TASKS_DB_FILENAME = "downloads.db"

# Download defaults (conservative for mobile)
DEFAULT_MAX_CONCURRENT = 1
DEFAULT_CONCURRENT_FRAGMENTS = 4
DEFAULT_RETRY_COUNT = 5
DEFAULT_QUALITY = "best"
DEFAULT_CONTAINER = "mp4"
DEFAULT_DOWNLOAD_MODE = "video"

# Supported URL domains (mirrors main.py / downloader)
VIDEO_DOMAINS = (
    "tiktok.com",
    "vm.tiktok.com",
    "vt.tiktok.com",
    "instagram.com",
    "youtube.com",
    "youtu.be",
    "twitter.com",
    "x.com",
    "facebook.com",
    "fb.com",
)

VIDEO_EXTENSIONS = (".mp4", ".mkv", ".mov", ".avi", ".webm", ".m4v", ".3gp")

RESOLUTION_PRESETS: dict[str, int | None] = {
    "Best available": None,
    "1080p": 1080,
    "720p": 720,
    "480p": 480,
    "360p": 360,
}

VIDEO_CONTAINERS = ["mp4", "mkv", "webm"]
AUDIO_FORMATS = ["mp3", "m4a", "aac", "opus"]

# Navigation tab indices
TAB_HOME = 0
TAB_DOWNLOADING = 1
TAB_COMPLETED = 2
TAB_SETTINGS = 3

TAB_LABELS = ("Home", "Downloading", "Completed", "Settings")
