"""Unit tests for video models."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vidsaver.models.video import DownloadResult, VideoEntry


def test_video_entry_from_dict_defaults():
    entry = VideoEntry.from_dict("clip.mp4", {})
    assert entry.display_name == "clip.mp4"
    assert entry.platform == "Video"
    assert entry.url == ""
    assert entry.size == 0


def test_video_entry_from_dict_full():
    data = {
        "platform": "TikTok",
        "url": "https://tiktok.com/x",
        "date": "25 Sep 2026",
        "created_at": 1000.5,
        "content_uri": "content://media/1",
        "source_path": "/tmp/a.mp4",
        "size": 2048,
    }
    entry = VideoEntry.from_dict("a.mp4", data)
    assert entry.platform == "TikTok"
    assert entry.playable_path == "content://media/1"
    assert entry.size == 2048


def test_video_entry_playable_path_fallback():
    entry = VideoEntry(display_name="x.mp4", source_path="/tmp/x.mp4")
    assert entry.playable_path == "/tmp/x.mp4"
    entry2 = VideoEntry(display_name="y.mp4")
    assert entry2.playable_path == "y.mp4"


def test_video_entry_roundtrip():
    entry = VideoEntry(
        display_name="v.mp4",
        platform="YouTube",
        url="https://youtu.be/1",
        size=100,
    )
    d = entry.to_dict()
    restored = VideoEntry.from_dict("v.mp4", d)
    assert restored.platform == "YouTube"
    assert restored.size == 100


def test_download_result_ok():
    assert DownloadResult(paths=["/a.mp4"]).ok is True
    assert DownloadResult(error="fail").ok is False
    assert DownloadResult().ok is False
