# Vidsaver Architecture (v1.5)

Rebuilt for **Flet 1.0** with a layered design inspired by
[Video-Downloader](https://github.com/fazi-gondal/Video-Downloader),
optimised for **instant Home-screen startup**.

## Goals achieved

| Goal | How |
|------|-----|
| Instant Home paint | `main()` only sets theme + AppBar, then `page.render(App)`. Heavy work runs in `after_first_paint`. |
| Lazy loading | `yt-dlp` imported on a daemon thread; MediaScanner initialised only when first needed. |
| Thread-safe UI | Worker thread never calls `page.update()`. Progress/status marshalled via `loop.call_soon_threadsafe`. |
| Optional cookies | `cookiefile` is only passed to yt-dlp when the file exists. |
| Clean separation | UI never imports yt-dlp; services own all I/O. |
| Polished UI | Shared palette, platform-coloured chips, empty state, floating toasts. |

## Package layout

```
src/
├── main.py                     # thin entry → ft.run(main)
└── vidsaver/
    ├── config/constants.py     # domains, album name, platform colours
    ├── core/errors.py
    ├── models/video.py         # VideoEntry, DownloadResult
    ├── services/
    │   ├── download_service.py # yt-dlp runner (thread-safe)
    │   ├── media_store.py      # flet-media-scanner facade
    │   └── library_service.py  # metadata.json + delete/sync
    ├── ui/
    │   ├── app.py              # AppContext + App component + after_first_paint
    │   ├── theme.py            # light/dark palette tokens
    │   ├── components/         # VideoCard, EmptyState, toast
    │   └── views/              # HomeView, LibraryView, PlayerView
    └── utils/                  # paths, platform helpers
```

## Startup sequence

1. `main(page)` → `ensure_storage_paths` (cheap) + theme + AppBar.
2. `page.render(App)` → first frame paints **Home**.
3. `use_effect(after_first_paint)`:
   - yields once (`await asyncio.sleep(0)`)
   - initialises MediaScanner (Android only)
   - starts background thread: `import yt_dlp`
   - optional MediaStore → metadata sync

## Download flow

```
HomeView → start_download(url)
  → set busy UI state
  → asyncio.to_thread(DownloadService.run, ...)
       callbacks → call_soon_threadsafe(set_status / set_progress)
  → on success: MediaStore.save_video (Android) or keep local file
  → LibraryService.upsert
  → toast + refresh library tab
```

## Migrating from the old flat modules

The previous `src/downloader.py`, `library.py`, `player.py` are left in place
for reference but are **no longer imported**. All logic now lives under
`vidsaver/`.

## Running

```bash
cd Vidsaver
uv sync
uv run flet run
```
