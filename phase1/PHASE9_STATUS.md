# Phase 9 — Testing and stabilization

## Automated coverage

- Download task cancellation and retry
- Terminal-task cleanup
- Settings save/load with invalid-value validation
- SQLite pending-task restoration
- SQLite interrupted active-task recovery

## Verification

- Python source and test suite compile successfully
- Unit suite passes
- Dependency resolution and `uv sync` complete successfully
- Web app starts and responds with HTTP 200

## Device validation still required

The following items need real Android 13/ARM64 verification:

- Foreground service and notification permission behavior
- Downloads while minimized and screen-locked
- Process termination and task recovery
- MediaStore Gallery publishing
- PyAV/FFmpeg processing backend
- yt-dlp YouTube JavaScript/EJS compatibility
