---
name: flet-imperative
description: "Expert knowledge for building Flet apps in imperative/procedural mode (page.add, page.update). Covers auto-update mechanism, smart update logic, 85+ breaking changes from Flet 0.x, critical API traps, error troubleshooting, 19+ new controls, customizable scrollbars, expanded SharedPreferences, page.navigate / pop_views_until / take_animation, Screenshot control, DragTargetEvent migration, and 20 verified examples. Flet 0.85.x+."
---

# Flet Imperative Mode — Complete Reference

> Flet 0.85.x+ | Imperative (procedural) mode | All APIs verified against Flet 0.85.0 source

---

## What's New in Flet 0.85.x (Imperative-Relevant)

| Feature | Details |
|---------|---------|
| **`page.navigate(route)`** | Sync wrapper for `page.push_route()` — use in `on_click` and other sync callbacks |
| **`page.pop_views_until(route, result=None)`** | Pop views to a target route. Result delivered via new `on_views_pop_until` (`ViewsPopUntilEvent`) |
| **`page.take_animation(name, frame_delays_ms, pixel_ratio)`** | Capture animated PNG sequence in one round-trip; requires `page.enable_screenshots = True` |
| **`Screenshot` control** | New control with `content` + async `capture()` for subtree screenshots |
| **`DragTargetEvent` deprecations** | `.x`, `.y`, `.offset` deprecated (removal in 0.88.0) — use `local_position` / `global_position` |
| **`ft.Router` (also imperative-friendly)** | While `ft.Router` lives in components, you can still mount one inside `page.render(App)` from imperative code |

## Flet 0.83.x Foundations

| Feature | Details |
|---------|---------|
| **6.7x faster diffing** | `Prop` descriptor tracks only modified properties — imperative apps benefit directly |
| **Smart update()** | If you call `.update()` explicitly, the framework skips automatic post-handler update (no double renders) |
| **Customizable scrollbars** | `Scrollbar(thumb_visibility=, thickness=, radius=, interactive=, orientation=)` on `Column`, `Row`, `ListView`, `GridView`, `ExpansionPanelList` |
| **Scrollable ExpansionPanelList** | Now inherits `ScrollableControl` |
| **SharedPreferences expanded** | Now supports `int`, `float`, `bool`, `list[str]` (not just `str`) |
| **Padding functions removed** | `ft.padding.all()` / `.symmetric()` / `.only()` removed — use `ft.Padding.all()` class methods |
| **Field validation** | Controls use `Annotated[type, V.rule()]` for declarative constraints |
| **Desktop packaging** | Desktop binaries moved from PyPI to GitHub Releases, cached at `~/.flet/client/` |

---

## When to Use This Skill

- Building Flet apps using imperative mode (`page.add`, `page.update`)
- Migrating from Flet 0.x to 1.0+
- Encountering API errors (Tabs, Badge, BorderRadius, Colors, Keyboard, etc.)
- Quick prototyping without the declarative component system

For declarative mode (`@ft.component`, `page.render`), see the **flet-app** skill.

---

## Fundamentals

### Entry Point

```python
import flet as ft

def main(page: ft.Page):
    page.title = "My App"
    page.add(ft.Text("Hello, Flet!"))

ft.run(main)    # NEVER ft.app(target=main)
```

### Auto-Update Mechanism (Flet 1.0+)

Flet automatically calls `page.update()` after event handlers and `main()`.

```python
def button_click(e):
    page.controls.append(ft.Text("Clicked!"))
    # No page.update() needed — auto-update handles it

page.add(ft.Button(content=ft.Text("Click"), on_click=button_click))
```

**Smart update logic (0.83+)** — the framework tracks whether `page.update()` was called during event handler execution. If explicit `.update()` occurs, the automatic framework-level update is skipped, eliminating redundant updates and visual glitches.

**Batch optimization** — disable auto-update for bulk operations:
```python
def add_many(e):
    ft.context.disable_auto_update()
    for i in range(100):
        page.controls.append(ft.Text(f"Item {i}"))
    page.update()  # Single update instead of 100
```

### Project Setup

```bash
flet create          # Generates pyproject.toml + src/main.py + src/assets/
flet run             # Run the app
```

**Project structure:**
```
my_app/
├── pyproject.toml   # Dependencies
└── src/
    ├── main.py      # Entry point
    └── assets/      # Static files
```

---

## Critical API Traps

**Most error-prone APIs — always verify before using:**

| API | Wrong | Correct |
|-----|-------|---------|
| Launch | `ft.app(target=main)` | `ft.run(main)` |
| Colors | `ft.colors.BLUE` | `ft.Colors.BLUE` (uppercase C) |
| Alignment | `ft.alignment.center` | `ft.Alignment.CENTER` (uppercase A) |
| BorderRadius | `ft.border_radius.all(10)` | `ft.BorderRadius.all(10)` (uppercase B) |
| BorderRadius | `tl=5, tr=5` | `top_left=5, top_right=5` (full names) |
| Border | `ft.border.all(...)` | `ft.Border.all(...)` (uppercase B) |
| Buttons | `ft.ElevatedButton(...)` | `ft.Button(content=...)` or `ft.FilledButton(...)` |
| Icon | `ft.Icon(name=...)` | `ft.Icon(icon=...)` |
| Tabs | `ft.Tabs(tabs=[...])` | `Tabs(content=Column([TabBar(...), TabBarView(...)]), length=N)` |
| TabBarView | no height | Must set `height=` |
| Dialog | `page.open(dialog)` | `page.show_dialog(dialog)` / `page.pop_dialog()` |
| SnackBar | `page.snack_bar = ...` | `page.overlay.append(sb); sb.open = True; page.update()` |
| Keyboard | `page.on_key_down` | `page.on_keyboard_event` only |
| Badge | `label_style=, small=` | Only `label=` |

**Full trap list**: See [references/api-traps.md](../flet-app/references/api-traps.md)

---

## Core Patterns

### Service Controls

```python
file_picker = ft.FilePicker()
page.services.append(file_picker)    # NOT page.add() or page.overlay
```

### Async Event Handlers

```python
async def on_click(e):
    await file_picker.pick_files()     # Async API calls need async def

async def delayed_action(e):
    await asyncio.sleep(0.5)           # Use asyncio.sleep, NOT time.sleep
```

### Dialogs

```python
dialog = ft.AlertDialog(
    title=ft.Text("Confirm"),
    content=ft.Text("Are you sure?"),
    actions=[
        ft.Button(content=ft.Text("Yes"), on_click=lambda e: page.pop_dialog()),
        ft.Button(content=ft.Text("No"), on_click=lambda e: page.pop_dialog()),
    ],
)
page.show_dialog(dialog)    # NOT page.open()
page.pop_dialog()           # NOT page.close()
```

### SnackBar / BottomSheet

```python
snackbar = ft.SnackBar(content=ft.Text("Done!"), bgcolor=ft.Colors.GREEN)
page.overlay.append(snackbar)
snackbar.open = True
page.update()
```

### Tabs (Three-Part Pattern)

```python
ft.Tabs(
    content=ft.Column([
        ft.TabBar(tabs=[
            ft.Tab(label="Home", icon=ft.Icons.HOME),
            ft.Tab(label="Settings", icon=ft.Icons.SETTINGS),
        ]),
        ft.TabBarView(
            height=200,   # REQUIRED
            controls=[
                ft.Container(content=ft.Text("Home"), padding=20),
                ft.Container(content=ft.Text("Settings"), padding=20),
            ],
        ),
    ]),
    length=2,
)
```

### Keyboard Events

```python
def on_keyboard(e: ft.KeyboardEvent):
    if e.key == "Escape":
        print("Escape pressed")
    if e.ctrl and e.key == "S":
        print("Ctrl+S")

page.on_keyboard_event = on_keyboard
# NO: page.on_key_down, page.on_key_up, e.event_type, e.type
```

---

## API Verification (Mandatory for Uncertain APIs)

```bash
python -c "import inspect; import flet as ft; print(inspect.signature(ft.BorderRadius.__init__))"
python -c "import flet as ft; print(hasattr(ft, 'CircleAvatar'))"
python -c "import flet as ft; print([m for m in dir(ft.Page) if not m.startswith('_')])"
```

---

## Development Checklist

- [ ] Use `flet create` for new projects (generates standard structure)
- [ ] Use `ft.run(main)` — NOT `ft.app()`
- [ ] Use `ft.Colors.XXX` (uppercase C)
- [ ] Use `ft.Alignment.CENTER` (uppercase A)
- [ ] Use `icon=` for Icon (not `name=`)
- [ ] BorderRadius: `top_left/top_right/bottom_left/bottom_right` (not abbreviations)
- [ ] Set `height` on TabBarView
- [ ] Verify uncertain APIs with `inspect`
- [ ] Service controls go in `page.services`, NOT `page.add()`

---

## Resources

### Reference Documentation

- **[Architecture](../flet-app/references/architecture.md)** — Clean architecture pattern for production apps
- **[API Traps](../flet-app/references/api-traps.md)** — Critical API pitfalls
- **[Breaking Changes](../flet-app/references/breaking-changes.md)** — 82+ changes from 0.x
- **[Error Guide](../flet-app/references/error-guide.md)** — Error lookup table
- **[New Controls](../flet-app/references/new-controls.md)** — 19 new controls

### Example Code (20 verified examples)

- `examples/01_basic_app.py` — Basic structure
- `examples/02_async_clock.py` — Async real-time updates
- `examples/03_form_validation.py` — Form validation
- `examples/04_file_picker_service.py` — FilePicker service
- `examples/05_shared_preferences.py` — Local storage
- `examples/06_animation_effects.py` — Animations
- `examples/07_dialog_example.py` — Dialogs
- `examples/08_layout_responsive.py` — Responsive layout
- `examples/09_theme_styling.py` — Tabs three-part pattern
- `examples/10_navigation_menu.py` — Navigation
- `examples/11_data_table.py` — DataTable
- `examples/12_window_controls.py` — Window control
- `examples/13_drag_drop.py` — Drag and drop
- `examples/14_keyboard_events.py` — Keyboard events
- `examples/15_gestures.py` — Gestures
- `examples/16_clipboard.py` — Clipboard
- `examples/17_media_player.py` — Media
- `examples/18_canvas_custom_paint.py` — Canvas
- `examples/19_file_operations.py` — File I/O
- `examples/20_charts_canvas_visualization.py` — Charts

---

**Applicable Version**: Flet >= 0.83.0
**Breaking Changes**: 82+
