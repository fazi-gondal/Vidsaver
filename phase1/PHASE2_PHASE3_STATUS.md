# Phase 2 complete · Phase 3 started

## Phase 2 (complete)

- Folder structure under `src/` (config, models, views, components, utils, services)
- Fonts: Inter + Space Grotesk in `src/assets/fonts/`
- Theme tokens + font registration (`config/theme.py`)
- Settings model + JSON persistence
- Domain models for tasks/media
- Exactly **four** bottom tabs (Home / Downloading / Completed / Settings)
- Shared page settings + theme apply on startup
- Player still full-screen overlay (existing `PlayerView`)
- Utils: validators, formatting, paths, platform
- Empty state component
- Existing downloader / library / MediaStore preserved

## Phase 3 (in progress — Home foundation)

Done:
- `analyze_media()` in `downloader.py` (metadata + formats, no download)
- Optional `format_selector` on `run_download()`
- New `views/home_view.py`: URL + paste, Analyze, Quick download
- Media preview card (title, platform, duration, thumbnail, quality)
- Quality bottom sheet from available heights
- Playlist detection: list entries with per-item download
- Primary/processing accent colors on Home actions

Still optional later in Phase 3 polish:
- Richer format matrix (fps / codec) if needed
- Thumbnail caching
- Wire selected defaults from Settings (`default_quality`)

## Run

```bash
cd Vidsaver
uv sync
uv run flet run
```

Flow: paste URL → **Analyze** → preview → **Quality** (optional) → **Quick download**.
