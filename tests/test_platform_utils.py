"""Unit tests for platform helpers."""

from __future__ import annotations

from unittest.mock import MagicMock

from vidsaver.utils.platform import is_android_page, is_video_url


def test_is_video_url():
    assert is_video_url("https://tiktok.com/@x/video/1") is True
    assert is_video_url("https://www.instagram.com/reel/abc") is True
    assert is_video_url("https://youtu.be/xyz") is True
    assert is_video_url("not a url") is False
    assert is_video_url("") is False
    assert is_video_url("https://example.com/page") is False


def test_is_android_page_string_value():
    page = MagicMock()
    page.platform = MagicMock()
    page.platform.value = "android"
    assert is_android_page(page) is True


def test_is_android_page_false():
    page = MagicMock()
    page.platform = "windows"
    # platform.value may not exist; getattr chain should not match ANDROID enum
    page.platform = MagicMock(value="windows")
    assert is_android_page(page) is False
