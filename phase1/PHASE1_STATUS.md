# Phase 1 — Dependency & Android Compatibility Audit

**Target:** Android 13, ARM64-v8a, Python 3.14, Flet 1.1.2  
**Status:** **COMPLETE (prep + decisions locked)**  
**Device verification:** Required on your machine before enabling production deps (see below)

---

## Decisions locked for Phase 2+

| Topic | Decision | Rationale |
|-------|----------|-----------|
| Flet / Python | Keep `flet==1.1.2`, Python 3.14, arm64-v8a | Already correct in repo |
| Media backend (Android) | **Prefer** `flet-libffmpeg` + `av` (PyAV) | Wheels listed on pypi.flet.dev; smaller integration surface than shipping ffmpeg binary |
| Media backend (fallback) | Bundled ARM64 `ffmpeg`/`ffprobe` only if PyAV PoC fails | Executable path stays available |
| Notifications | **Official** `flet-notifications==1.1.2` + `dataSync` FGS | Matches plan; avoid custom extension unless insufficient |
| YouTube / EJS / Deno | **Deferred** — do not block UI upgrade | Deno on Android is high risk/size; keep current yt-dlp behaviour |
| Concurrency defaults | `max_concurrent=1` (mobile), fragments=4 | Conservative until device-tested |
| Main lockfile | Do **not** add ffmpeg/notifications until device PoC green | Prevents broken releases |

---

## Device verification checklist (you run once)

```bash
cd Vidsaver
uv sync
# Baseline APK
uv run flet build apk --split-per-abi --arch arm64-v8a --source-packages packages/flet-media-scanner

# FFmpeg PoC
uv sync --group phase1-ffmpeg
# Add flet-libffmpeg + av to [tool.flet.android].dependencies temporarily
uv run python phase1/poc_ffmpeg.py
uv run flet build apk ...

# Notifications PoC  
uv sync --group phase1-notifications
# Add POST_NOTIFICATIONS + FOREGROUND_SERVICE* (see run_notes.md)
uv run python phase1/poc_notifications.py
uv run flet build apk ...
```

Record results here:

| Check | Result | Notes |
|-------|--------|-------|
| Baseline APK | ☐ | |
| `import av` on device | ☐ | |
| PyAV open/stream | ☐ | |
| Notification permission | ☐ | |
| FGS start/update/stop | ☐ | |
| FGS when permission denied | ☐ | |

If PyAV fails on device → switch media decision to executable backend before Phase 8.

---

## Files

| File | Purpose |
|------|---------|
| `PHASE1_STATUS.md` | This report |
| `poc_ffmpeg.py` | PyAV smoke test |
| `poc_notifications.py` | FGS smoke test |
| `run_notes.md` | Exact local commands |

**Phase 1 code/prep is complete. Proceeding to Phase 2 with existing working deps only.**
