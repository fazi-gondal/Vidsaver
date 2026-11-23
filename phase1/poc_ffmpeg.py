"""
Phase 1 PoC — FFmpeg / PyAV smoke test for Vidsaver.

Run on desktop first:
    uv run python phase1/poc_ffmpeg.py

On Android (after adding flet-libffmpeg + av and building APK):
    Use a temporary entry or embed this check in a debug screen.

Success = import works and we can open a small media file / report streams.
"""

from __future__ import annotations

import sys
import traceback
from pathlib import Path


def main() -> int:
    print("=== Vidsaver Phase 1: FFmpeg / PyAV PoC ===")
    print(f"Python: {sys.version}")
    print(f"Platform: {sys.platform}")

    # --- 1. Import av (PyAV) ---
    try:
        import av

        print(f"[OK] import av  version={getattr(av, '__version__', '?')}")
    except Exception as e:
        print(f"[FAIL] import av: {e}")
        traceback.print_exc()
        return 1

    # --- 2. Optional: check flet-libffmpeg presence (Android) ---
    try:
        # flet-libffmpeg primarily provides native libs; may not expose a pure-Python API
        import importlib.util

        spec = importlib.util.find_spec("flet_libffmpeg")
        if spec is not None:
            print("[OK] flet_libffmpeg module discoverable")
        else:
            print("[INFO] flet_libffmpeg not importable as Python module (libs may still load)")
    except Exception as e:
        print(f"[INFO] flet_libffmpeg check: {e}")

    # --- 3. Open a sample file if present ---
    candidates = [
        Path("src/assets/demo.jpg"),  # not video — will fail open, still tests import path
        Path("phase1/sample.mp4"),
        Path("sample.mp4"),
    ]
    media = next((p for p in candidates if p.exists() and p.suffix.lower() in {".mp4", ".mkv", ".webm", ".mov"}), None)

    if media is None:
        print("[INFO] No sample video found. Create phase1/sample.mp4 for full open test.")
        print("[PASS] Import-only PoC succeeded. Add a short mp4 for stream inspection.")
        return 0

    try:
        container = av.open(str(media))
        print(f"[OK] opened {media}")
        for i, stream in enumerate(container.streams):
            print(
                f"  stream[{i}] type={stream.type} "
                f"codec={getattr(stream.codec_context, 'name', '?')} "
                f"duration={stream.duration}"
            )
        container.close()
        print("[PASS] PyAV open + stream list OK")
        return 0
    except Exception as e:
        print(f"[FAIL] av.open: {e}")
        traceback.print_exc()
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
