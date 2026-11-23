# Phase 1 — Commands to run on your machine

The sandbox cannot build Android APKs or run Flet mobile. Use these steps locally (or in your existing CI).

## 0. Baseline (no new deps)

```bash
cd Vidsaver
uv sync
uv run flet build apk --split-per-abi --arch arm64-v8a --source-packages packages/flet-media-scanner
```

Install the APK on an Android 13+ ARM64 device. Confirm download + gallery publish still work.

---

## 1. FFmpeg PoC

Edit `pyproject.toml` **temporarily**:

```toml
dependencies = [
    "flet==1.1.2",
    "flet-video==1.1.2",
    "flet-media-scanner==1.0.3",
    "yt-dlp",
    "requests",
    "certifi",
    "charset-normalizer",
    "idna",
    "urllib3",
    "flet-libffmpeg",
    "av",
]

[tool.flet.android]
# ... keep existing ...
dependencies = [
    "certifi",
    "charset-normalizer",
    "idna",
    "requests",
    "urllib3",
    "yt-dlp",
    "flet-media-scanner",
    "flet-libffmpeg",
    "av",
]
```

Then:

```bash
uv lock
uv sync
# Desktop import / open test
uv run python phase1/poc_ffmpeg.py

# Android build
uv run flet build apk --split-per-abi --arch arm64-v8a --source-packages packages/flet-media-scanner
```

Record in `PHASE1_STATUS.md`:
- Build succeeded? Y/N
- `import av` on device? Y/N
- APK size before/after
- Any codec / library load errors

Revert the dependency changes if the PoC fails, or keep them if green and document the decision.

---

## 2. Notifications PoC

Edit `pyproject.toml` **temporarily** (can combine with FFmpeg PoC once both are green):

```toml
dependencies = [
    # ... existing + optional ffmpeg ...
    "flet-notifications==1.1.2",
]

[tool.flet.android.permission]
"android.permission.INTERNET" = true
"android.permission.POST_NOTIFICATIONS" = true
"android.permission.FOREGROUND_SERVICE" = true
"android.permission.FOREGROUND_SERVICE_DATA_SYNC" = true
```

Service block (verify against current docs if build complains):

```toml
[tool.flet.android.service."com.dexterous.flutterlocalnotifications.ForegroundService"]
exported = false
foregroundServiceType = "dataSync"
```

```bash
uv lock
uv sync
uv run python phase1/poc_notifications.py   # import check

# Point a temporary main or:
# uv run flet run phase1/poc_notifications.py   # if entry adapted
uv run flet build apk --split-per-abi --arch arm64-v8a --source-packages packages/flet-media-scanner
```

On device:
1. Request permission → grant
2. Start FGS → persistent notification
3. Update progress
4. Stop FGS
5. Repeat with permission **denied** and note behaviour

---

## 3. After both PoCs

Update `phase1/PHASE1_STATUS.md` checklist.

Only then:
- Lock production media backend choice
- Decide YouTube / Deno strategy (keep deferred for now)
- Start Phase 2 (4-tab shell, theme, models) with proven deps

---

## Reference links

- Flet binary packages: https://flet.dev/docs/reference/binary-packages-android-ios
- flet-notifications: https://flet.dev/docs/services/notifications/
- Android FGS types: https://flet.dev/docs/services/notifications/types/androidforegroundservicetype
- yt-dlp EJS: https://github.com/yt-dlp/yt-dlp/wiki/EJS
