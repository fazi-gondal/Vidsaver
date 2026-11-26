# Contributing to Vidsaver

Thank you for your interest in contributing to **Vidsaver**!

## Prerequisites

- **Python 3.14+**
- **[uv](https://docs.astral.sh/uv/)** for dependency and virtual environment management
- **Git**
- Optional (for local builds):
  - **Android SDK / NDK** for `flet build apk`
  - **[Inno Setup](https://jrsoftware.org/isinfo.php)** for building the Windows installer

## Local Setup

1. Fork and clone the repository:

   ```bash
   git clone https://github.com/fazi-gondal/Vidsaver.git
   cd Vidsaver
   ```

2. Install dependencies:

   ```bash
   uv sync
   ```

3. Run the app locally:

   ```bash
   uv run flet run
   ```

   Or test on an Android device over the network:

   ```bash
   uv run flet run --android
   ```

## Project Conventions

- **Flet 1.1.2 API**: Keep all UI code compatible with Flet `1.1.2` declarative components (`@ft.component`). Avoid deprecated APIs (for example, use `ft.NoInputBorder()` instead of `ft.InputBorder.NONE`, `page.show_dialog()` for `SnackBar`, and `ft.Button` / `ft.FilledButton` instead of `ElevatedButton`).
- **Design System**: Use tokens and helpers from `src/theme.py` (`surface_card`, `inset_input_box`, `status_pill`, `empty_state`, typography helpers, and semantic `PILL_*` colors) rather than hardcoding ad-hoc colors.
- **Non-blocking I/O**: Keep `yt-dlp` downloads and file/metadata I/O off the UI event loop using `asyncio.to_thread(...)`.
- **Mobile Compatibility**: Never assume `ffmpeg` is installed on mobile devices. Preserve the `shutil.which("ffmpeg")` check and `b[ext=mp4]/b` fallback in `src/downloader.py`.

## Verification Before Opening a PR

Run a compile check across all Python source files:

```bash
uv run python -m py_compile src/theme.py src/main.py src/library.py src/player.py src/downloader.py
```

Verify the theme and modules import cleanly:

```bash
uv run python -c "import sys; sys.path.insert(0, 'src'); import theme, library, player, downloader; theme.light_theme(); theme.dark_theme(); print('OK')"
```

## Pull Request Guidelines

- Keep PRs focused on a single feature or bug fix.
- Use clear, descriptive commit messages (e.g., `feat(ui): ...`, `fix(downloader): ...`, `docs: ...`).
- Update `CHANGELOG.md` under `[Unreleased]` if your change affects user-facing behavior.
- Do not commit personal `cookies.txt` session data or local build artifacts.
