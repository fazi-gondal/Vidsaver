"""Persistent application settings (JSON under app data dir)."""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, fields
from pathlib import Path

from config.constants import (
    DEFAULT_CONCURRENT_FRAGMENTS,
    DEFAULT_CONTAINER,
    DEFAULT_DOWNLOAD_MODE,
    DEFAULT_MAX_CONCURRENT,
    DEFAULT_QUALITY,
    DEFAULT_RETRY_COUNT,
    SETTINGS_FILENAME,
)

logger = logging.getLogger(__name__)


@dataclass
class AppSettings:
    theme_mode: str = "system"  # system | light | dark

    max_concurrent: int = DEFAULT_MAX_CONCURRENT
    concurrent_fragments: int = DEFAULT_CONCURRENT_FRAGMENTS

    default_quality: str = DEFAULT_QUALITY
    default_container: str = DEFAULT_CONTAINER
    default_download_mode: str = DEFAULT_DOWNLOAD_MODE

    download_dir: str = ""
    retry_count: int = DEFAULT_RETRY_COUNT
    rate_limit_kbps: int = 0

    notifications_enabled: bool = True
    background_downloads_enabled: bool = True
    clipboard_auto_paste: bool = True

    write_subtitles: bool = False
    subtitle_langs: str = "en"
    audio_format: str = "m4a"
    timeout_seconds: int = 30
    embed_thumbnail: bool = True
    embed_metadata: bool = True
    keep_originals: bool = False


class SettingsRepository:
    """Load/save AppSettings as JSON next to metadata.json."""

    def __init__(self, data_dir: str | Path) -> None:
        self._path = Path(data_dir) / SETTINGS_FILENAME

    @property
    def path(self) -> Path:
        return self._path

    def load(self) -> AppSettings:
        try:
            raw = json.loads(self._path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return AppSettings()
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Could not read settings (%s); using defaults", exc)
            return AppSettings()

        known = {f.name for f in fields(AppSettings)}
        filtered = {k: v for k, v in raw.items() if k in known}
        try:
            settings = AppSettings(**filtered)
        except (TypeError, ValueError) as exc:
            logger.warning("Invalid settings (%s); using defaults", exc)
            return AppSettings()
        settings.max_concurrent = max(1, min(4, int(settings.max_concurrent or 1)))
        settings.concurrent_fragments = max(
            1,
            min(
                8,
                int(
                    settings.concurrent_fragments
                    if settings.concurrent_fragments is not None
                    else 4
                ),
            ),
        )
        settings.retry_count = max(0, min(15, int(settings.retry_count or 0)))
        settings.rate_limit_kbps = max(0, int(settings.rate_limit_kbps or 0))
        settings.timeout_seconds = max(5, min(300, int(settings.timeout_seconds or 30)))
        if settings.theme_mode not in ("system", "light", "dark"):
            settings.theme_mode = "system"
        if settings.default_container not in ("mp4", "mkv", "webm"):
            settings.default_container = "mp4"
        if settings.default_download_mode not in ("video", "audio"):
            settings.default_download_mode = "video"
        if settings.audio_format not in ("mp3", "m4a", "aac", "opus"):
            settings.audio_format = "m4a"
        return settings

    def save(self, settings: AppSettings) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = asdict(settings)
        self._path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
