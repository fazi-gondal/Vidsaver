# Phases 6–8 status

## Phase 6 (complete)

- Theme, quality, container, mode
- Max concurrent, **fragment concurrency**, **retries**, **rate limit**
- Subtitles toggle, clipboard auto-paste
- Notifications + background downloads toggles
- Storage path + clear finished tasks
- Settings applied to yt-dlp via `ydl_option_provider`

## Phase 7 (complete for code path)

- `NotificationService` (optional dependency)
- Request permission when enabling notifications
- FGS start / progress / complete / stop on task lifecycle
- `pyproject.toml` documents Android permission keys (commented until PoC)

**Device:** enable `flet-notifications` + uncomment permissions after Phase 1 PoC.

## Phase 8 (complete)

- `TaskStore` SQLite (`downloads.db`)
- Upsert on every task change
- Restore on manager init
- Interrupted active tasks → FAILED with retry message
- PENDING tasks re-queued after restart
- Clear finished removes memory + DB rows

## Still later (plan)

- Phase 9+: FFmpeg merge/transcode after media PoC
- Windows packaging unchanged
- README refresh once device-validated

## Run

```bash
cd Vidsaver
uv sync
uv run flet run
```
