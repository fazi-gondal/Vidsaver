# Phase 3 complete · Phase 4 started

## Phase 3 (complete)

- Analyze URL with richer quality list (height · fps, Best, Audio only)
- Playlist detection when URL looks like a playlist
- Media preview + quality bottom sheet
- Settings: default quality / container / mode; clipboard gate
- Default quality applied after Analyze when height matches
- Platform chips on Home
- Quick download still works without Analyze

## Phase 4 (started — usable)

- `services/download_manager.py`: queue, worker pool, cancel, retry
- Independent `DownloadTask` progress/state
- Home download **enqueues** a task and switches to Downloading tab
- Downloading tab shows active + recent task cards (cancel / retry)
- Nav badge count for active/queued tasks
- Configurable `max_concurrent` from Settings (1–4)
- Gallery publish still uses existing MediaStore path (bridged from worker)

### Not yet (later phases)

- SQLite task persistence / recovery (Phase 8)
- Foreground notifications (Phase 7)
- Full ETA/speed from yt-dlp hooks
- Multi-select playlist bulk enqueue UI polish

## Run

```bash
cd Vidsaver
uv sync
uv run flet run
```

Analyze → quality → download → watch **Downloading** tab for live cards.
