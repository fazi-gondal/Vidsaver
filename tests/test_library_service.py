"""Unit tests for library metadata persistence."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vidsaver.models.video import VideoEntry
from vidsaver.services.library_service import (
    LibraryService,
    load_metadata,
    save_metadata,
)


def test_load_missing_metadata(tmp_path):
    path = tmp_path / "missing.json"
    assert load_metadata(str(path)) == {}


def test_save_and_load_metadata(tmp_path):
    path = tmp_path / "meta.json"
    data = {"a.mp4": {"platform": "TikTok", "size": 10}}
    save_metadata(str(path), data)
    loaded = load_metadata(str(path))
    assert loaded["a.mp4"]["platform"] == "TikTok"


def test_library_list_upsert_remove(tmp_path):
    path = tmp_path / "meta.json"
    lib = LibraryService(str(path), media_store=None)
    assert lib.list_entries() == []

    entry = VideoEntry(
        display_name="clip.mp4",
        platform="YouTube",
        created_at=200.0,
        size=1024,
    )
    lib.upsert(entry)
    entries = lib.list_entries()
    assert len(entries) == 1
    assert entries[0].platform == "YouTube"

    older = VideoEntry(display_name="old.mp4", created_at=50.0)
    lib.upsert(older)
    ordered = lib.list_entries()
    assert ordered[0].display_name == "clip.mp4"  # newest first

    lib.remove("clip.mp4")
    left = lib.list_entries()
    assert len(left) == 1
    assert left[0].display_name == "old.mp4"
