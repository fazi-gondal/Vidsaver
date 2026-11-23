# Phase 2 — Project foundation (started)

## Done

- Theme tokens + font registration (`config/theme.py`)
- Constants + settings model + JSON repo (`config/`)
- Download/media models (`models/`)
- Four-tab bottom navigation (`components/bottom_navigation.py`)
- Downloading placeholder view
- Settings view (theme, concurrency, clipboard, notifications toggle)
- `main.py` routes: Home | Downloading | Completed (existing library) | Settings
- Primary accent `#FF5C49` on AppBar
- Existing downloader / library / player / MediaStore **unchanged**

## Not yet (later phases)

- Independent download manager + task cards
- Home quality/format sheet
- Real badge counts on Downloading tab
- SQLite task store
- Notifications integration
- FFmpeg processing services

## How to run

```bash
cd Vidsaver
uv sync
uv run flet run
```

Switch tabs on device/desktop. Settings theme should persist in `settings.json` under app data.
