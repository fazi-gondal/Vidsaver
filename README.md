# Vidsaver

Cross-platform video downloader built with **Python 3.14** and **Flet 1.0**.  
Paste a link, download in the background, browse your library, and play videos — with a fast Home screen and a clean mobile-first UI.

**Download TikTok and Instagram reels without watermark in Full HD.**

---

## Features

- Download from platforms supported by `yt-dlp` (TikTok, Instagram, YouTube, X/Twitter, Facebook, and more)
- **Instant Home paint** — heavy work (`yt-dlp` import, MediaScanner) runs after the first frame
- **Declarative routing** (`/`, `/downloads`, `/player`) with bottom NavigationBar and system Back support
- Android saves via MediaStore to `Movies/Vidsaver` (Gallery-visible, no broad storage permission)
- Downloads library: platform chips, size, date, play, delete with confirmation
- Built-in player (`flet-video`) with ±10s seek controls
- Clipboard auto-paste when a supported video URL is on the clipboard
- Light / dark mode toggle in the AppBar
- Skeleton loading on the library tab
- Optional `cookies.txt` for sites that need a session (not required for every site)

### Mobile Demo

![Demo](/src/assets/demo.jpg)

### Windows Demo

![Demo](/src/assets/demo1.png)
![Demo](/src/assets/demo2.png)
![Demo](/src/assets/demo3.png)

---

## Tech Stack

| Component | Version / notes |
|-----------|------------------|
| Python | 3.14+ |
| [Flet](https://flet.dev) | 1.0 (declarative UI + Router) |
| [flet-video](https://pypi.org/project/flet-video/) | 1.0 |
| [flet-media-scanner](https://pypi.org/project/flet-media-scanner/) | 1.0.2 (Android MediaStore) |
| yt-dlp | latest |
| Package manager | [uv](https://docs.astral.sh/uv/) |

---

## Architecture

Layered layout inspired by a maintainable service/UI split. See [ARCHITECTURE.md](ARCHITECTURE.md) for details.

```text
src/
├── main.py                          # thin entry → ft.run(main)
└── vidsaver/
    ├── config/                      # constants, platform colours
    ├── core/                        # errors
    ├── models/                      # VideoEntry, DownloadResult
    ├── services/
    │   ├── download_service.py      # yt-dlp (thread-safe, no page.update)
    │   ├── media_store.py           # flet-media-scanner facade
    │   └── library_service.py       # metadata.json + list/delete/sync
    ├── ui/
    │   ├── app.py                   # Router, AppLayout, routes, lazy warm-up
    │   ├── theme.py                 # light/dark palette tokens
    │   ├── components/              # VideoCard, EmptyState, Skeleton, toast
    │   └── views/                   # Home, Library, Player
    └── utils/                       # paths, platform helpers
tests/                               # pytest unit tests
packages/
├── flet-media-scanner/              # custom Flet extension
└── windows/installer.iss
```

**Startup path**

1. `main()` sets theme + storage paths only  
2. `page.render_views(App)` paints Home immediately  
3. Background: MediaScanner init, `import yt_dlp`, optional library sync  

**Routes**

| Path | Screen |
|------|--------|
| `/` | Home (paste + download) |
| `/downloads` | Library |
| `/player` | Full-screen player |

---

## Project Structure (repo root)

```text
.
├── .github/workflows/          # Windows + Android CI/CD
├── packages/
│   ├── flet-media-scanner/
│   └── windows/installer.iss
├── src/
│   ├── assets/
│   ├── cookies.txt             # optional session cookies for yt-dlp
│   ├── main.py
│   └── vidsaver/               # application package
├── tests/
├── ARCHITECTURE.md
├── pyproject.toml
└── README.md
```

Legacy flat modules under `src/` (`downloader.py`, `library.py`, `player.py`) are kept for reference only and are **not** imported by the app.

---

## Run Locally

```bash
# Install dependencies
uv sync

# Desktop
uv run flet run

# Web
uv run flet run --web
```

---

## Testing & Code Quality

```bash
# Unit tests
uv run pytest

# Lint + format check
uv run ruff check src/vidsaver tests
uv run ruff format --check src/vidsaver tests
```

Tests cover models, download helpers, library metadata, and platform URL detection. A lightweight Flet stub is used when Flet is not installed in the test environment.

---

## Android Permissions

Android 13+ download flow does **not** request broad storage or media permissions. Files stage in app-private storage, then publish through MediaStore.

```toml
[tool.flet.android.permission]
"android.permission.INTERNET" = true
```

---

## Build Locally

**Android arm64 APK**

```bash
uv run flet build apk --split-per-abi --arch arm64-v8a --source-packages packages/flet-media-scanner --yes --verbose
```

**Windows**

```bash
uv run flet build windows --source-packages packages/flet-media-scanner
```

GitHub Releases typically attach:

```text
Vidsaver-vX.Y.Z-Windows.zip              # portable
Vidsaver-vX.Y.Z-Windows-setup.exe        # Inno Setup installer
Vidsaver-vX.Y.Z-Android-arm64-v8a.apk
Vidsaver-vX.Y.Z-Android-arm64-v8a.zip
```

---

## Download Behaviour

1. Progress UI updates immediately when a link is submitted  
2. `yt-dlp` runs in a worker thread (UI stays responsive; no `page.update()` from the worker)  
3. Progress and status are marshalled onto the UI loop  
4. On Android, the finished file is published to MediaStore under `Movies/Vidsaver`  
5. A floating snackbar confirms completion  

Filenames use the video title (no platform IDs appended).

---

## Cookies

`src/cookies.txt` is optional. When present, it is passed to `yt-dlp` for sites that need a logged-in session. Update it if a platform starts blocking anonymous downloads.

---

## FFmpeg (optional)

For merge/remux or post-processing on mobile builds, Flet hosts native wheels on [pypi.flet.dev](https://pypi.flet.dev), including **`flet-libffmpeg`**. Desktop can use a system or bundled FFmpeg binary. Vidsaver does not require FFmpeg for the default `b[ext=mp4]/b` download path.

---

## Troubleshooting

### `ModuleNotFoundError: certifi`

Ensure the APK was built after `certifi`, `charset-normalizer`, `idna`, and `urllib3` were listed in `pyproject.toml`.

### APK installs as 32-bit

Use the arm64 release asset:

```text
Vidsaver-vX.Y.Z-Android-arm64-v8a.apk
```

### New version will not install over old version

Usually a different signing key or ABI. Uninstall the old build once, or keep a stable signing key in CI secrets.

### Video does not appear in Gallery

Files are under `Movies/Vidsaver`. Some Gallery apps need a moment to refresh.

### Slow first download

The first run may import `yt-dlp` in the background after Home paints. Later downloads reuse the imported module.

---

## Useful Links

- [Flet documentation](https://flet.dev/docs/)
- [Flet Router](https://flet.dev/docs/cookbook/router/)
- [Flet Android packaging](https://flet.dev/docs/publish/android/)
- [Binary packages (Android/iOS)](https://flet.dev/docs/reference/binary-packages-android-ios/)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [flet-media-scanner on PyPI](https://pypi.org/project/flet-media-scanner/)

---

<p align="center">
  Crafted with care by <strong>Fazi Gondal</strong>
</p>
