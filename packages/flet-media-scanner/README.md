# flet-media-scanner

A [Flet](https://flet.dev) extension for Android **MediaStore** integration — save, list, and delete videos in the device Gallery without requiring broad storage permissions.

## Requirements

- **Platform**: Android only (no-op on other platforms)
- **Android**: API 23+ (minSdk 23)
- **Flet**: >= 0.86.0

## Installation

```bash
pip install flet-media-scanner
```

## Setup

Register the extension in your `pyproject.toml`:

```toml
[tool.flet.extensions]
flet_media_scanner = "flet_media_scanner.Extension"
```

## Usage

```python
import flet as ft
from flet_media_scanner import MediaScanner, SaveResult

async def main(page: ft.Page):
    scanner = MediaScanner()
    page.services.append(scanner)
    page.update()

    # Save a video to the Gallery (Movies/MyApp folder)
    result: SaveResult = await scanner.save_video(
        "/data/user/0/com.example.app/cache/video.mp4",
        file_name="my_video.mp4",
        album="MyApp",
    )
    if result.success:
        print(f"Saved: {result.content_uri}")
    else:
        print(f"Error: {result.error}")

    # List videos in the album
    videos = await scanner.list_videos(album="MyApp")
    for v in videos:
        print(v["display_name"], v["content_uri"])

    # Delete a video by content URI
    deleted = await scanner.delete_video("content://media/external/video/media/123")
    print("Deleted:", deleted)

ft.run(main)
```

## API

### `MediaScanner` (Service)

Add to `page.services` before calling any methods.

#### `await save_video(file_path, file_name=None, album="MyApp") → SaveResult`

Copies a private app file into Android MediaStore (`Movies/<album>`). Works on Android 10+ without broad storage permissions.

| Parameter | Type | Description |
|---|---|---|
| `file_path` | `str` | Absolute path to the source video file |
| `file_name` | `str \| None` | Display name in Gallery (defaults to basename) |
| `album` | `str` | Subfolder inside `Movies/` |

#### `await list_videos(album="MyApp") → list[dict]`

Returns all videos previously saved to the album. Each dict contains: `display_name`, `content_uri`, `mime_type`, `relative_path`, `size`, `date_added`.

#### `await delete_video(content_uri) → bool`

Deletes a MediaStore item by its `content://` URI.

#### `await scan_media(file_path) → bool`

*(Legacy)* Triggers a media scan for a file that already exists in public storage. Use `save_video()` for new downloads instead.

---

### `SaveResult` (dataclass)

| Field | Type | Description |
|---|---|---|
| `success` | `bool` | Whether the operation succeeded |
| `content_uri` | `str` | MediaStore `content://` URI |
| `display_name` | `str` | File name as shown in Gallery |
| `mime_type` | `str` | e.g. `video/mp4` |
| `relative_path` | `str` | e.g. `Movies/MyApp/` |
| `size` | `int` | File size in bytes |
| `error` | `str` | Error message if `success=False` |

## License

MIT
