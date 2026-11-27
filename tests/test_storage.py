"""Unit tests for storage.py (URL checks and local/MediaStore helpers)."""

import asyncio
from types import SimpleNamespace

import flet as ft

import storage


def test_url_validation():
    assert storage.is_http_url("https://www.tiktok.com/@a/video/1")
    assert storage.is_http_url("http://example.com/v.mp4")
    assert not storage.is_http_url("ftp://example.com/v.mp4")
    assert not storage.is_http_url("not a url")
    assert not storage.is_http_url("")

    assert storage.is_video_url("https://www.instagram.com/reel/123/")
    assert storage.is_video_url("https://www.snapchat.com/spotlight/123")
    assert not storage.is_video_url("https://example.com/article")


def test_is_android_page():
    assert storage.is_android_page(SimpleNamespace(platform=ft.PagePlatform.ANDROID))
    assert storage.is_android_page(SimpleNamespace(platform="android"))
    assert not storage.is_android_page(SimpleNamespace(platform=ft.PagePlatform.WINDOWS))


def test_publish_and_delete_desktop(tmp_path):
    video = tmp_path / "clip.mp4"
    video.write_bytes(b"video-bytes")
    meta_path = tmp_path / "metadata.json"
    page = SimpleNamespace(platform=ft.PagePlatform.WINDOWS)

    ok, err = asyncio.run(
        storage.publish_download_result(
            page,
            {
                "paths": [str(video)],
                "platform": "TikTok",
                "url": "https://www.tiktok.com/@u/video/1",
                "date": "27 Nov 2026",
            },
            str(meta_path),
        )
    )
    assert ok and err == ""
    assert meta_path.exists()

    deleted = asyncio.run(storage.delete_saved_video(page, {"source_path": str(video)}))
    assert deleted
    assert not video.exists()
