# flet-media-scanner

A [Flet](https://flet.dev) extension for native Android **MediaStore** integration — save, list, and delete videos in the device Gallery without requiring broad storage permissions.

Built with **100% native Android Kotlin** (`MediaStore` & `MediaScannerConnection`) and pure Dart Flet service bindings, with zero third-party Flutter plugin dependencies.

---

## Features

- 📱 **Android MediaStore Scoped Storage**: Save videos directly to `Movies/<Album>` without `WRITE_EXTERNAL_STORAGE` on Android 10+ (API 29+).
- 🖼️ **Instant Gallery Visibility**: Media is immediately visible in Google Photos and device Gallery apps via native `ContentResolver` publishing and `MediaScannerConnection`.
- 📋 **List & Query**: Query videos belonging to your app's custom album.
- 🗑️ **Content URI Deletion**: Cleanly delete media using Android `content://` URIs.
- ⚡ **Zero Third-Party Dependencies**: No external Flutter packages needed.

---

## Requirements

- **Platform**: Android only (no-op / unsupported on desktop & iOS)
- **Android**: API 21+ (minSdk 21; Scoped Storage optimized for API 29+)
- **Flet**: `>= 1.0.0`
- **Python**: `>= 3.10`

---

## Installation

```bash
pip install flet-media-scanner
```

Or when developing locally in a workspace:

```toml
[tool.flet.extensions]
flet_media_scanner = "flet_media_scanner.Extension"

[tool.flet.dev_packages]
flet-media-scanner = "packages/flet-media-scanner"
```

---

## Setup

Register the extension in your application's `pyproject.toml`:

```toml
[tool.flet.extensions]
flet_media_scanner = "flet_media_scanner.Extension"
```

---

## Usage

```python
import flet as ft
from flet_media_scanner import MediaScanner, SaveResult

async def main(page: ft.Page):
    # Initialize and register the service
    scanner = MediaScanner()
    page.services.append(scanner)
    page.update()

    # 1. Save a downloaded video to Gallery (Movies/MyVideos folder)
    result: SaveResult = await scanner.save_video(
        file_path="/data/user/0/com.example.app/cache/video.mp4",
        file_name="awesome_video.mp4",
        album="MyVideos",
    )

    if result.success:
        print(f"Saved successfully: {result.content_uri}")
        print(f"Gallery relative path: {result.relative_path}")
    else:
        print(f"Failed to save: {result.error}")

    # 2. List all videos in the custom album
    videos = await scanner.list_videos(album="MyVideos")
    for v in videos:
        print(f"Video: {v['display_name']} | URI: {v['content_uri']}")

    # 3. Delete a video by content URI
    if result.content_uri:
        deleted = await scanner.delete_video(result.content_uri)
        print("Deleted:", deleted)

    # 4. Trigger legacy media scanner for existing public files
    scanned = await scanner.scan_media("/storage/emulated/0/Movies/MyVideos/awesome_video.mp4")
    print("Scanned:", scanned)

ft.run(main)
```

---

## API Reference

### `MediaScanner` (Service)

Inherits from `ft.Service`. Must be added to `page.services` before invoking methods.

#### `await save_video(file_path: str, file_name: str | None = None, album: str = "Vidsaver") -> SaveResult`
Copies an app-private cache or temp video file into Android `MediaStore.Video.Media` (`Movies/<album>`).
- **`file_path`** *(str)*: Absolute filesystem path to the source video.
- **`file_name`** *(str | None)*: Target file name in the Gallery (defaults to the file basename).
- **`album`** *(str)*: Subdirectory name inside `Movies/` (defaults to `"Vidsaver"`).
- **Returns**: [`SaveResult`](#saveresult-dataclass).

#### `await list_videos(album: str = "Vidsaver") -> list[dict]`
Queries all videos previously registered in the specified album.
- **`album`** *(str)*: Album subfolder inside `Movies/`.
- **Returns**: List of dictionaries with keys:
  - `display_name` *(str)*: File name shown in Gallery.
  - `content_uri` *(str)*: Android `content://` URI.
  - `mime_type` *(str)*: Video MIME type (e.g. `video/mp4`).
  - `relative_path` *(str)*: Directory path in storage (e.g. `Movies/Vidsaver`).
  - `size` *(int)*: File size in bytes.
  - `date_added` *(int)*: Unix timestamp added.
  - `date_modified` *(int)*: Unix timestamp modified.

#### `await delete_video(content_uri: str) -> bool`
Deletes a media item from MediaStore using its `content://` URI.
- **`content_uri`** *(str)*: Android MediaStore content URI.
- **Returns**: `True` if deleted, `False` otherwise.

#### `await scan_media(file_path: str) -> bool`
Triggers Android native `MediaScannerConnection.scanFile` to index a file that already resides in public storage.
- **`file_path`** *(str)*: Absolute path to the file.
- **Returns**: `True` if successfully indexed, `False` otherwise.

---

### `SaveResult` (Dataclass)

| Field | Type | Description |
|---|---|---|
| `success` | `bool` | `True` if the video was successfully saved and published. |
| `content_uri` | `str` | Android MediaStore `content://` URI for the saved media. |
| `display_name` | `str` | Display name of the file in the Gallery. |
| `mime_type` | `str` | MIME type (e.g., `video/mp4`). |
| `relative_path` | `str` | Destination relative path (e.g., `Movies/Vidsaver`). |
| `source_path` | `str` | Original source path passed into `save_video`. |
| `size` | `int` | Size of the saved file in bytes. |
| `error` | `str` | Error description if `success` is `False`. |

---

## Related Project

If your application needs more comprehensive media library functionality such as **browsing albums, querying photos/videos/audio, thumbnails, permissions, media mutations, and live media change notifications**, see **[flet-media-library](https://github.com/fazi-gondal/Flet-media-library)**.

`flet-media-scanner` is intentionally focused on Android `MediaStore` operations for saving, listing, deleting, and scanning videos.

## Used in Vidsaver

`flet-media-scanner` is used in **[Vidsaver](https://github.com/fazi-gondal/Vidsaver)** to handle Android media-library operations for downloaded videos.

Vidsaver uses the package to integrate downloaded media with Android's native **MediaStore**, allowing videos to be saved, scanned, listed, and managed without relying on a separate media-management layer.

This makes `flet-media-scanner` part of a real-world Flet application and demonstrates how the package can be used for native Android media integration in production-style projects.

**Vidsaver:** https://github.com/fazi-gondal/Vidsaver

---

## License

[MIT](LICENSE)
