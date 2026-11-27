"""Unit tests for downloader.py (offline, no network)."""

import json
import sys
import types

import downloader


def test_detect_platform():
    assert downloader.detect_platform("https://www.tiktok.com/@user/video/123") == "TikTok"
    assert downloader.detect_platform("https://vt.tiktok.com/ZSYabc/") == "TikTok"
    assert downloader.detect_platform("https://www.instagram.com/reel/abc/") == "Instagram"
    assert downloader.detect_platform("https://youtu.be/dQw4w9WgXcQ") == "YouTube"
    assert downloader.detect_platform("https://x.com/user/status/123") == "Twitter/X"
    assert downloader.detect_platform("https://fb.watch/abc/") == "Facebook"
    assert downloader.detect_platform("https://www.snapchat.com/spotlight/123") == "Snapchat"
    assert downloader.detect_platform("https://v.redd.it/abc") == "Reddit"
    assert downloader.detect_platform("https://pin.it/abc") == "Pinterest"
    assert downloader.detect_platform("https://www.threads.net/@u/post/1") == "Threads"
    assert downloader.detect_platform("https://example.com/video.mp4") == "Video"


def test_clean_ansi():
    assert downloader.clean_ansi("\x1b[0;94m 42.5%\x1b[0m") == " 42.5%"


def test_metadata_roundtrip(tmp_path):
    meta_file = tmp_path / "metadata.json"
    assert downloader.load_metadata(str(meta_file)) == {}

    sample = {"clip.mp4": {"platform": "TikTok", "size": 1024}}
    downloader.save_metadata(str(meta_file), sample)
    assert json.loads(meta_file.read_text(encoding="utf-8")) == sample
    assert downloader.load_metadata(str(meta_file)) == sample


def test_collect_downloaded_paths_deduplicates():
    info = {
        "filepath": "/tmp/a.mp4",
        "requested_downloads": [{"filepath": "/tmp/a.mp4"}, {"filename": "/tmp/b.mp4"}],
        "entries": [{"_filename": "/tmp/c.mp4"}],
    }
    assert downloader.collect_downloaded_paths(info) == [
        "/tmp/a.mp4",
        "/tmp/b.mp4",
        "/tmp/c.mp4",
    ]


def test_resolve_short_url_skips_full_urls(monkeypatch):
    called = False

    def fake_head(*args, **kwargs):
        nonlocal called
        called = True
        raise AssertionError("requests.head should not be called for full URLs")

    import requests

    monkeypatch.setattr(requests, "head", fake_head)
    full_url = "https://www.tiktok.com/@user/video/123456"
    assert downloader.resolve_short_url(full_url) == full_url
    assert not called


def test_resolve_short_url_follows_shorteners(monkeypatch):
    class FakeResp:
        url = "https://www.tiktok.com/@user/video/999"

    import requests

    monkeypatch.setattr(requests, "head", lambda *a, **kw: FakeResp())
    assert (
        downloader.resolve_short_url("https://vt.tiktok.com/ZSY123/")
        == "https://www.tiktok.com/@user/video/999"
    )


def test_run_download_cookieless_and_format_selection(monkeypatch, tmp_path):
    captured_opts = {}
    out_file = tmp_path / "Sample Video.mp4"

    class FakeYDL:
        def __init__(self, opts):
            captured_opts.update(opts)

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def extract_info(self, url, download=True):
            out_file.write_bytes(b"mp4-data")
            return {"filepath": str(out_file)}

    fake_yt_dlp = types.ModuleType("yt_dlp")
    setattr(fake_yt_dlp, "YoutubeDL", FakeYDL)
    monkeypatch.setitem(sys.modules, "yt_dlp", fake_yt_dlp)
    monkeypatch.setattr(downloader.shutil, "which", lambda name: None)

    statuses = []
    errors = []
    res = downloader.run_download(
        url="https://www.instagram.com/reel/abc/",
        target_dir=str(tmp_path),
        cookie_path="ignored_cookies.txt",
        metadata_path="",
        on_status=statuses.append,
        on_progress=lambda _: None,
        on_finish=lambda: None,
        on_error=errors.append,
        page=None,
    )

    assert not errors
    assert res is not None
    assert res["platform"] == "Instagram"
    assert res["engine"] == "yt-dlp"
    assert res["paths"] == [str(out_file)]
    assert "cookiefile" not in captured_opts
    assert captured_opts["format"] == "b[ext=mp4]/b"
    assert captured_opts["js_runtimes"] == {}
    assert captured_opts["cachedir"] is False
