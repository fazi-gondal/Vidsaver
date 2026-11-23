# Phase 5 complete · Phase 6 polish · Phase 7 started

## Phase 5 (complete)

- Completed search + platform filter + **sort** (newest / oldest / name)
- **Share** original URL (system Share when available, else clipboard)
- Playback + delete confirmation + MediaStore sync unchanged
- Downloading cards: % · size · speed · ETA

## Phase 6 (complete)

- Theme / concurrency / quality / container / mode / clipboard / notifications
- Storage section: data path + clear finished tasks
- Settings persist via settings.json

## Phase 7 (started)

- `NotificationService` wraps flet-notifications when installed
- No-ops if package missing (safe before PoC)
- Hooks: start FGS while active, update progress text, complete notification, stop when idle
- Enable via Settings → Notifications

**Device note:** add `flet-notifications==1.1.2` + Android permissions from `phase1/run_notes.md` after baseline PoC.

## Next

- Phase 8: SQLite task persistence / recovery
- Optional: FFmpeg processing services after media PoC
