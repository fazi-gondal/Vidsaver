# Flet 1.0+ API Traps & Quick Reference

> High-frequency APIs verified with `inspect`. Always verify uncertain APIs before using.

---

## Critical API Traps

| API | Common Mistake | Correct Usage |
|-----|---------------|---------------|
| **Threading UI** | `asyncio.run()` + `await page.run_task()` | Plain `def` + `time.sleep()` + `page.run_task()` (fire-and-forget) |
| **Border.all()** | `ft.border.all()` | `ft.Border.all()` (uppercase B, >= 0.80.0) |
| **Padding.symmetric()** | `ft.padding.symmetric()` | `ft.Padding.symmetric()` (uppercase P, >= 0.80.0) |
| **KeyboardEvent** | `page.on_key_down` / `page.on_key_up` | `page.on_keyboard_event` only (no separate down/up) |
| **KeyboardEvent** | `e.event_type` or `e.type` | No such attribute. Events repeat while key is pressed |
| **BorderRadius** | `ft.border_radius.all()` | `ft.BorderRadius.all()` (uppercase B, >= 0.80.0) |
| **BorderRadius** | `tl=, tr=, bl=, br=` | Full names: `top_left=, top_right=, bottom_left=, bottom_right=` |
| **Colors** | `DARK_RED`, `DARK_BLUE` | Material Design: `RED_900`, `BLUE_900` |
| **Tabs** | `tabs=[]` parameter | Three-part: `Tabs(content=..., length=N)` + `TabBar` + `TabBarView` |
| **TabBarView** | Omit `height` | Must set `height` — unbounded height crashes |
| **Icon** | `name=` parameter | `icon=` parameter |
| **Badge** | `label_style` or `small` | Only `label=` parameter |
| **Radio** | Standalone | Must wrap in `RadioGroup` |
| **App Launch** | `ft.app(target=main)` | `ft.run(main)` |
| **Colors** | `ft.colors` (lowercase) | `ft.Colors` (uppercase C) |
| **Alignment** | `ft.alignment.center` | `ft.Alignment.CENTER` (uppercase A) |
| **Buttons** | `ft.ElevatedButton` | `ft.Button(content=...)` or `ft.FilledButton(content=...)` |
| **Dialog** | `page.open(dialog)` | `page.show_dialog(dialog)` / `page.pop_dialog()` |
| **SnackBar** | `page.snack_bar = ...` | `page.overlay.append(snackbar); snackbar.open = True` |
| **Icons** | `ft.Icons.ROBOT` | Does not exist. Use `ft.Icons.ANDROID` or `ft.Icons.SMART_TOY` |

---

## KeyboardEvent

**Attributes**: `key` (str), `shift` (bool), `ctrl` (bool), `alt` (bool), `meta` (bool)

```python
def on_keyboard(e: ft.KeyboardEvent):
    if e.key == "W":
        # handle W key
    if e.ctrl and e.key == "S":
        # handle Ctrl+S

page.on_keyboard_event = on_keyboard

# NO: page.on_key_down, page.on_key_up, e.event_type, e.type
```

---

## BorderRadius

**Signature**: `(top_left, top_right, bottom_left, bottom_right)` — all 4 required

```python
ft.BorderRadius(top_left=5, top_right=5, bottom_left=0, bottom_right=0)
ft.BorderRadius.all(10)  # Shorthand — uppercase B
```

---

## Colors

```python
ft.Colors.BLUE           # Standard
ft.Colors.RED_900        # Dark (not DARK_RED)
ft.Colors.BLUE_100       # Light (not LIGHT_BLUE)
"#FF5722"                # Hex also works

# Material shade scale: _50 (lightest) to _900 (darkest)
```

---

## Alignment

```python
ft.Alignment.CENTER          ft.Alignment.TOP_LEFT
ft.Alignment.TOP_CENTER      ft.Alignment.TOP_RIGHT
ft.Alignment.CENTER_LEFT     ft.Alignment.CENTER_RIGHT
ft.Alignment.BOTTOM_LEFT     ft.Alignment.BOTTOM_CENTER
ft.Alignment.BOTTOM_RIGHT    ft.Alignment(x=0.5, y=0.5)
```

---

## Buttons

```python
ft.Button(content=ft.Text("Click"))
ft.FilledButton(content=ft.Text("Save"), icon=ft.Icons.SAVE)
ft.OutlinedButton(content=ft.Text("Cancel"))
ft.TextButton("Text")
ft.Button(content=ft.Text("Styled"), style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.BLUE))
```

---

## Tabs (Three-Part Pattern)

```python
ft.Tabs(
    content=ft.Column([
        ft.TabBar(tabs=[ft.Tab(label="Tab1"), ft.Tab(label="Tab2")]),
        ft.TabBarView(height=120, controls=[ft.Text("Content1"), ft.Text("Content2")]),
    ]),
    length=2,
)
```

---

## Dialogs

```python
dialog = ft.AlertDialog(
    title=ft.Text("Title"),
    content=ft.Text("Message"),
    actions=[ft.Button(content=ft.Text("OK"), on_click=lambda e: page.pop_dialog())],
)
page.show_dialog(dialog)
page.pop_dialog()
```

---

## SnackBar / BottomSheet

```python
snackbar = ft.SnackBar(content=ft.Text("Success"), bgcolor=ft.Colors.GREEN)
page.overlay.append(snackbar)
snackbar.open = True
page.update()
```

---

## Icon

```python
ft.Icon(icon=ft.Icons.HOME, size=24, color=ft.Colors.BLUE)
# Common: ADD, DELETE, EDIT, SETTINGS, SEARCH, PERSON, ANDROID, SMART_TOY
```

---

## Container (Full Example)

```python
ft.Container(
    content=ft.Text("Content"),
    bgcolor=ft.Colors.WHITE,
    border_radius=ft.BorderRadius.all(10),
    padding=ft.Padding(left=10, top=5, right=10, bottom=5),
    margin=ft.Margin(left=10, top=5, right=10, bottom=5),
    shadow=ft.BoxShadow(spread_radius=1, blur_radius=15, color=ft.Colors.GREY_300, offset=ft.Offset(0, 2)),
    on_click=lambda e: print("clicked"),
)
```

---

## API Verification Commands

```bash
# Verify constructor signature
python -c "import inspect; import flet as ft; print(inspect.signature(ft.BorderRadius.__init__))"

# Check if control exists
python -c "import flet as ft; print(hasattr(ft, 'CircleAvatar'))"

# List all public methods
python -c "import flet as ft; print([m for m in dir(ft.Page) if not m.startswith('_')])"
```

---

---

## Padding Factory Functions (Removed in 0.83.0)

```python
# OLD (removed in 0.83.0)
ft.padding.all(10)
ft.padding.symmetric(vertical=5, horizontal=10)
ft.padding.only(left=5, top=10)

# NEW — use class methods
ft.Padding.all(10)
ft.Padding.symmetric(vertical=5, horizontal=10)
ft.Padding.only(left=5, top=10)
```

---

## SharedPreferences (Expanded in 0.83.0)

```python
# 0.82.x — string only
await prefs.set("key", "value")

# 0.83.x — supports int, float, bool, list[str]
await prefs.set("count", 42)
await prefs.set("ratio", 3.14)
await prefs.set("enabled", True)
await prefs.set("tags", ["python", "flet"])
```

---

## Customizable Scrollbars (New in 0.83.0)

```python
from flet.controls.scrollable_control import Scrollbar, ScrollbarOrientation

# Any scrollable control accepts a Scrollbar instance
ft.Column(
    scroll=Scrollbar(
        thumb_visibility=True,
        track_visibility=True,
        thickness=8,
        radius=4,
        interactive=True,
        orientation=ScrollbarOrientation.RIGHT,
    ),
    controls=[...],
)
```

---

**Version**: Flet >= 0.83.0
**All examples verified with `inspect`**
