import os
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from downloader import analyze_media, run_download


class DownloaderTests(unittest.TestCase):
    def test_analysis_timeout_returns_user_facing_error(self):
        class FailingYDL:
            def __init__(self, _options):
                pass

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def extract_info(self, _url, download):
                if download:
                    raise AssertionError("Analysis must not download media.")
                raise TimeoutError("connection timed out")

        with patch.dict(sys.modules, {"yt_dlp": SimpleNamespace(YoutubeDL=FailingYDL)}):
            result = analyze_media("https://www.tiktok.com/@user/video/123", "")

        self.assertFalse(result["ok"])
        self.assertEqual(
            result["error"],
            "Connection to TikTok timed out. Check your internet connection and try again.",
        )

    def test_download_without_cookie_file_uses_yt_dlp(self):
        captured_options = {}

        class FakeYDL:
            def __init__(self, options):
                captured_options.update(options)

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def extract_info(self, _url, download):
                if not download:
                    raise AssertionError("Download extraction must enable downloading.")
                output = os.path.join(captured_options["outtmpl"].split("%(")[0], "video.mp4")
                with open(output, "wb") as file:
                    file.write(b"video")
                return {"filepath": output}

        with tempfile.TemporaryDirectory() as target_dir:
            with patch.dict(sys.modules, {"yt_dlp": SimpleNamespace(YoutubeDL=FakeYDL)}):
                result = run_download(
                    "https://example.com/video",
                    target_dir,
                    os.path.join(target_dir, "missing-cookies.txt"),
                    "",
                    lambda _message: None,
                    lambda _progress: None,
                    lambda: None,
                    lambda _error: None,
                    SimpleNamespace(update=lambda: None),
                )

        self.assertTrue(result["paths"])
        self.assertNotIn("cookiefile", captured_options)


if __name__ == "__main__":
    unittest.main()
