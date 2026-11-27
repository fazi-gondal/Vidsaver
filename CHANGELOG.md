# Changelog

All notable changes to **Vidsaver** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.6.0] - 2026-11-27

### Added
- **Nocturnal Studio UI/UX Redesign** (`src/theme.py`, `src/assets/fonts/`):
  - Bundled `Space Grotesk` and `Inter` (`Regular`, `Medium`, `SemiBold`) fonts.
  - Added tonal `DARK` and `LIGHT` palettes with `1px` subtle borders, Coral (`#FF5C49`) primary accent, and Teal (`#2BB3A8`) secondary accent.
  - Added custom `BottomNavBar` inside `ft.BottomAppBar` with reference icons (`HOME_FILLED`, `DOWNLOAD_ROUNDED` / `DOWNLOAD` in red), active indicator pill, hover highlights, and `180ms` ease-out animations.
  - Added declarative moon/sun (`DARK_MODE_OUTLINED` / `LIGHT_MODE_OUTLINED`) theme toggle in the top `AppBar`.
  - Added sunken borderless URL input (`inset_input_box`), uppercase platform `status_pill`, compact progress card with left-to-right gradient fill, and floating `SnackBar` notifications.
  - Added search bar, horizontal platform filter pills, hover animations on `VideoCard`, and `empty_state` placeholders in `Downloads`.
- **Expanded Platform Support** (`src/downloader.py`, `src/storage.py`):
  - Added domain detection, short-link resolution, and platform chips for Snapchat, Reddit (`v.redd.it`, `redd.it`), Pinterest (`pin.it`), Threads, Vimeo, Dailymotion (`dai.ly`), Twitch, LinkedIn, Likee, SnackVideo, and Bilibili (`b23.tv`).
- **Modularization, Tests & CI** (`src/home.py`, `src/storage.py`, `tests/`, `.github/workflows/ci.yml`):
  - Extracted `HomeView` into `src/home.py` and storage/MediaStore helpers into `src/storage.py`.
  - Added `pytest` offline unit tests (`tests/test_downloader.py`, `tests/test_storage.py`, `tests/test_theme.py`), `ruff` linting, and `[tool.flet.compile]` bytecode pre-compilation in `pyproject.toml`.
  - Added `.github/workflows/ci.yml` to run `py_compile`, `ruff`, and `pytest` on every push and PR to `main`.
- **Repository Documentation**:
  - Added `CHANGELOG.md`, `CONTRIBUTING.md`, `LICENSE`, and GitHub issue templates.

### Changed
- **Instant Launch & Non-Blocking Pre-Warming** (`src/main.py`, `src/downloader.py`):
  - Deferred `init_storage_paths()` and `ensure_media_scanner()` until after `page.render_views()` so the first UI screen paints immediately.
  - Pre-imported `yt_dlp` and `requests` on a background daemon thread after first paint without blocking the UI thread.
- **Instant Downloads Library** (`src/main.py`, `src/library.py`):
  - Kept `LibraryView` mounted inside `ft.Stack` so switching tabs or returning from `PlayerView` is instant without reloading.
  - Rendered cached `metadata.json` immediately before running a one-time background MediaStore sync.
  - Removed download date from `VideoCard` metadata for a cleaner layout.
- **Fast Cookieless Downloads** (`src/downloader.py`):
  - Switched to a cookie-free `yt-dlp` path by default, added `js_runtimes={}`, `extractor_args` (`youtube:player_client=default,web_embedded,-android_vr`), `cachedir=False`, and restricted `resolve_short_url()` to actual shortener domains.

### Fixed
- Placed `BottomNavBar` inside `ft.BottomAppBar` so it stays beneath the soft keyboard when typing on Android.
- Switched to `page.render_views` with `page.on_view_pop` so the Android Back button closes `PlayerView` instead of exiting the app.
- Managed theme toggle state declaratively inside `App` to prevent `RuntimeError: Frozen controls cannot be updated.`.
- Removed deprecated `InputBorder.NONE` in favor of `NoInputBorder()`, removed unsupported `action_color` from `ft.SnackBar`, and removed thread-unsafe `page.update()` inside `run_download()`.

## [1.5.0]

### Added
- Declarative Flet `1.1.2` app architecture (`@ft.component`) across `src/main.py`, `src/library.py`, and `src/player.py`.
- Bumped `flet-media-scanner` to `1.0.3` with Python `3.14` support.

### Fixed
- **Mobile Downloads Without `ffmpeg`**: Detected `ffmpeg` via `shutil.which()` and switched to pre-muxed `b[ext=mp4]/b` when unavailable (resolving Instagram and mobile download failures).
- **Android CI Build**: Bumped `compileSdkVersion` to `34` in `flet_media_scanner`, prefetched Python runtimes, and disabled Gradle parallel workers to prevent `etags.json` corruption.

## [1.4.0]

### Added
- Native Android MediaStore integration via `packages/flet-media-scanner` for saving, listing, and deleting videos in `Movies/Vidsaver`.
- GitHub Actions workflows for automated Windows (`.zip` + Inno Setup `.exe`) and signed Android (`arm64-v8a` `.apk` + `.zip`) builds.
