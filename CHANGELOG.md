# Changelog

All notable changes to **Vidsaver** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Nocturnal Studio UI/UX Redesign** (`src/theme.py`, `src/assets/fonts/`):
  - Bundled `Space Grotesk` and `Inter` (`Regular`, `Medium`, `SemiBold`) fonts.
  - Added tonal `DARK` and `LIGHT` palettes with `1px` subtle borders, Coral (`#FF5C49`) primary accent, and Teal (`#2BB3A8`) secondary accent.
  - Added custom `BottomNavBar` with reference icons (`HOME_FILLED`, `DOWNLOAD_ROUNDED` / `DOWNLOAD`), active indicator pill, hover highlights, and `180ms` ease-out animations.
  - Added moon/sun (`DARK_MODE_OUTLINED` / `LIGHT_MODE_OUTLINED`) theme toggle in the top `AppBar`.
  - Added sunken borderless URL input (`inset_input_box`), uppercase platform `status_pill`, left-to-right progress gradient fill on the download status card, and floating `SnackBar` notifications.
  - Added search bar, horizontal platform filter pills, hover animations on `VideoCard`, and `empty_state` placeholders in `Downloads`.
- **Expanded Platform Support** (`src/downloader.py`, `src/main.py`):
  - Added domain detection, short-link resolution, and platform chips for Snapchat, Reddit (`v.redd.it`, `redd.it`), Pinterest (`pin.it`), Threads, Vimeo, Dailymotion (`dai.ly`), Twitch, LinkedIn, Likee, SnackVideo, and Bilibili (`b23.tv`).
- **Repository Documentation**:
  - Added `CHANGELOG.md`, `CONTRIBUTING.md`, `LICENSE`, and GitHub issue templates.

### Fixed
- Removed deprecated `InputBorder.NONE` in favor of `NoInputBorder()` for Flet 1.1.2 compatibility.
- Removed unsupported `action_color` keyword argument from `ft.SnackBar`.
- Switched `SnackBar` presentation to `page.show_dialog()` and added `Video.on_error` playback fallback in `src/player.py`.
- Made `src/cookies.txt` optional so downloads without a cookie file do not fail.

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
