"""Path helpers for app data and staging (platform-agnostic strings)."""

from __future__ import annotations

import os
from pathlib import Path

from config.constants import METADATA_FILENAME, SETTINGS_FILENAME, STAGING_DIR_NAME, TASKS_DB_FILENAME


def app_data_dir() -> Path:
    return Path(os.environ.get("FLET_APP_STORAGE_DATA") or os.getcwd())


def metadata_path(data_dir: Path | None = None) -> Path:
    return (data_dir or app_data_dir()) / METADATA_FILENAME


def settings_path(data_dir: Path | None = None) -> Path:
    return (data_dir or app_data_dir()) / SETTINGS_FILENAME


def tasks_db_path(data_dir: Path | None = None) -> Path:
    return (data_dir or app_data_dir()) / TASKS_DB_FILENAME


def staging_dir(temp_root: str | Path) -> Path:
    path = Path(temp_root) / STAGING_DIR_NAME
    path.mkdir(parents=True, exist_ok=True)
    return path
