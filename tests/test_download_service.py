"""Unit tests for download helpers (no network)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vidsaver.services.download_service import (
    clean_ansi,
    collect_downloaded_paths,
    detect_platform,
)


def test_detect_platform():
    assert detect_platform("https://www.tiktok.com/@u/video/1") == "TikTok"
    assert detect_platform("https://instagram.com/reel/x") == "Instagram"
    assert detect_platform("https://youtu.be/abc") == "YouTube"
    assert detect_platform("https://youtube.com/watch?v=1") == "YouTube"
    assert detect_platform("https://x.com/status/1") == "Twitter/X"
    assert detect_platform("https://twitter.com/status/1") == "Twitter/X"
    assert detect_platform("https://facebook.com/watch?v=1") == "Facebook"
    assert detect_platform("https://example.com/v") == "Video"


def test_clean_ansi():
    raw = "\x1b[0;32m12.5%\x1b[0m"
    assert clean_ansi(raw) == "12.5%"
    assert clean_ansi("plain") == "plain"


def test_collect_downloaded_paths_simple():
    info = {
        "filepath": "/tmp/out.mp4",
        "requested_downloads": [{"filepath": "/tmp/out.mp4"}],
    }
    paths = collect_downloaded_paths(info)
    assert "/tmp/out.mp4" in paths


def test_collect_downloaded_paths_entries():
    info = {
        "entries": [
            {"filepath": "/a.mp4"},
            {"filename": "/b.webm"},
        ]
    }
    paths = collect_downloaded_paths(info)
    assert "/a.mp4" in paths
    assert "/b.webm" in paths
