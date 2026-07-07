# Flet 1.0+ Breaking Changes Guide

> Complete list of breaking changes in Flet 1.0+ (>= 0.83.0). All deprecated APIs from Flet 0.x have been removed.

---

## 0. BorderRadius Creation (>= 0.80.0)

```python
# OLD (deprecated, removed in 0.83.0)
border_radius=ft.border_radius.all(10)

# NEW
border_radius=ft.BorderRadius.all(10)          # Uppercase B
border_radius=ft.BorderRadius(top_left=5, top_right=5, bottom_left=0, bottom_right=0)
```

**Note**: `border_radius.only()` and `border_radius.symmetric()` still work. Only `all()` requires the uppercase form.

---

## 1. App Launch

```python
# OLD
ft.app(target=main)

# NEW
ft.run(main)
ft.run(main, view=ft.AppView.FLET_APP)
```

---

## 2. Buttons

```python
# REMOVED
ft.ElevatedButton(...)   # NameError

# NEW
ft.Button(content=ft.Text("Click"))           # Standard button
ft.FilledButton(content=ft.Text("Save"))      # Primary action
ft.OutlinedButton(content=ft.Text("Cancel"))  # Secondary action
ft.TextButton("Text button")                  # Text-only button
```

**Button with style:**
```python
ft.Button(
    content=ft.Text("Save"),
    style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.GREEN),
)
```

---

## 3. Alignment

```python
# OLD
ft.alignment.center        # AttributeError

# NEW
ft.Alignment.CENTER        # Uppercase A
ft.Alignment.TOP_LEFT
ft.Alignment.BOTTOM_RIGHT
ft.Alignment(x=0.5, y=0.5)  # Custom
```

---

## 4. BoxFit

```python
# OLD
fit="contain"
fit=ft.ImageFit.CONTAIN

# NEW
fit=ft.BoxFit.CONTAIN   # COVER, FILL, FIT_WIDTH, FIT_HEIGHT
```

---

## 5. Border

```python
# OLD (deprecated)
ft.border.all(1, ft.Colors.GREY_300)

# NEW
ft.Border.all(1, ft.Colors.GREY_300)    # Uppercase B
ft.Border(left=ft.BorderSide(2, ft.Colors.BLUE))
```

---

## 6. Colors

```python
# OLD
ft.colors.BLUE             # AttributeError (lowercase)
ft.Colors.DARK_RED         # AttributeError (doesn't exist)
ft.Colors.values()         # AttributeError (no iteration)

# NEW
ft.Colors.BLUE             # Uppercase C
ft.Colors.RED_900          # Use Material shades instead of DARK_RED
ft.Colors.BLUE_100         # Instead of LIGHT_BLUE

# Color iteration requires manual list
COLOR_PALETTE = [ft.Colors.RED, ft.Colors.BLUE, ft.Colors.GREEN, ...]
```

**Material Design shade scale**: `_50` (lightest) to `_900` (darkest). Standard color (no suffix) = `_500`.

---

## 7. Animation

```python
# OLD
animate=ft.Animation(300, "easeInOut")

# NEW
animate=300                                          # Simple: milliseconds
animate=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT)  # With curve
```

---

## 8. Padding / Margin

```python
# OLD
ft.Padding.symmetric(0, 10)         # Positional args may fail

# NEW
ft.Padding(left=10, top=5, right=10, bottom=5)
ft.Padding(vertical=10, horizontal=20)
ft.Padding.symmetric(vertical=10, horizontal=20)
padding=10                           # Shorthand: all sides equal
```

---

## 9. Icon

```python
# OLD
ft.Icon(name=ft.Icons.HOME)    # name= removed

# NEW
ft.Icon(icon=ft.Icons.HOME, size=24, color=ft.Colors.BLUE)
```

**Note**: `ft.Icons.ROBOT` does not exist. Use `ft.Icons.ANDROID` or `ft.Icons.SMART_TOY`.

---

## 10. Badge

```python
# OLD — all removed
ft.Badge(label="5", label_style=..., small=True, bgcolor=..., text_color=...)

# NEW — only label= is supported
ft.Badge(label="5")

# Badge in Stack: use Container + Text instead
ft.Container(
    content=ft.Text("5", color=ft.Colors.WHITE, size=12),
    bgcolor=ft.Colors.RED,
    border_radius=10,
    padding=ft.Padding(left=8, right=8, top=4, bottom=4),
)
```

---

## 11. Tabs (Complete Rewrite)

The old `ft.Tabs(tabs=[...])` API is **100% removed**. New API uses a three-part pattern:

```python
ft.Tabs(
    content=ft.Column([
        ft.TabBar(
            tabs=[
                ft.Tab(label="Home", icon=ft.Icons.HOME),
                ft.Tab(label="Settings", icon=ft.Icons.SETTINGS),
            ],
        ),
        ft.TabBarView(
            height=120,   # REQUIRED — unbounded height causes crash
            controls=[
                ft.Container(content=ft.Text("Home content"), padding=20),
                ft.Container(content=ft.Text("Settings content"), padding=20),
            ],
        ),
    ]),
    length=2,             # Must match Tab count
    selected_index=0,
)
```

| Old API | New API |
|---------|---------|
| `ft.Tabs(tabs=[...])` | `ft.Tabs(content=..., length=N)` |
| `ft.Tab(text=..., content=...)` | `ft.Tab(label=..., icon=...)` |
| (none) | `ft.TabBar(tabs=[...])` |
| (none) | `ft.TabBarView(height=N, controls=[...])` |

---

## 12. Scroll Methods

```python
# OLD
list_view.scroll_to(key="item_1")

# NEW
list_view.scroll_to(scroll_key="item_1")
```

---

## 13. Keyboard Events

```python
# OLD (removed)
page.on_key_down = callback    # AttributeError
page.on_key_up = callback      # AttributeError

# NEW — single event, repeats while key is held
page.on_keyboard_event = callback

# KeyboardEvent attributes: key, shift, ctrl, alt, meta
# NO event_type or type attribute — cannot distinguish keydown/keyup
```

For key-hold detection, use timestamps:
```python
import time
key_timestamps = {}

def on_keyboard(e: ft.KeyboardEvent):
    key_timestamps[e.key.upper()] = time.time()

# In game loop: if time.time() - key_timestamps.get("W", 0) < 0.1: move()
```

---

## 14. Dialogs

```python
# OLD (removed)
page.open(dialog)     # AttributeError
page.close(dialog)    # AttributeError

# NEW
page.show_dialog(dialog)
page.pop_dialog()
```

---

## 15. SnackBar / BottomSheet

```python
# OLD (removed)
page.snack_bar = snackbar       # AttributeError
page.bottom_sheet = bottom_sheet # AttributeError

# NEW
page.overlay.append(snackbar)
snackbar.open = True
page.update()
```

---

## 16. NavigationDrawer

```python
# OLD (removed)
drawer.open = True   # AttributeError

# NEW
page.drawer = drawer
await page.show_drawer()
await page.close_drawer()
```

---

## 17. Window Methods (Now Async)

```python
# OLD
page.window.center()   # coroutine never awaited

# NEW
await page.window.center()
await page.window.close()
```

---

## 18. Clipboard

```python
# OLD (deprecated since 0.80.0)
page.clipboard

# NEW
clipboard = ft.Clipboard()
page.services.append(clipboard)
```

---

## 19. SharedPreferences (replaces client_storage)

```python
# OLD (removed)
page.client_storage   # AttributeError

# NEW
prefs = ft.SharedPreferences()
page.services.append(prefs)
await prefs.set("key", "value")
value = await prefs.get("key")
```

---

## 20. Dropdown

```python
# OLD
ft.Dropdown(on_change=callback)

# NEW
ft.Dropdown(on_select=callback)
```

---

## 21. Canvas / Paint

```python
# OLD
ft.PaintStyle.FILL          # AttributeError
ft.canvas.Polygon(...)      # AttributeError
paint.stroke_dash = [5, 3]  # AttributeError
path.move_to(x, y)          # AttributeError

# NEW
ft.PaintingStyle.FILL
ft.canvas.Path(elements=[...])         # Use Path instead of Polygon
paint.stroke_dash_pattern = [5, 3]
path = ft.canvas.Path(elements=[ft.canvas.Path.MoveTo(x, y), ...])
```

---

## 22. Draggable Events

```python
# OLD
on_drag_end=callback
e.local_x, e.local_y

# NEW
on_drag_complete=callback
e.local_position.x, e.local_position.y
```

---

## 23. Hover Events

```python
# OLD
if e.data == "true":   # String comparison

# NEW
if e.data:             # Boolean in Flet 1.0+
```

---

## 24. Window Properties

```python
# REMOVED (no replacement)
page.window.transparent   # AttributeError

# NULLABLE — use defaults
width = page.window.max_width or 1920
height = page.window.max_height or 1080
```

---

## 25. Audio

```python
# REMOVED
ft.Audio(...)   # AttributeError — use third-party libraries (pygame, pydub)
```

---

## 26. Threading + UI Updates

```python
# WRONG — causes RuntimeError: dictionary changed size during iteration
def background_task():
    time.sleep(1)
    text.value = "Done"  # Direct UI mutation from thread

# CORRECT — use page.run_task for UI updates from background
async def update_ui():
    text.value = "Done"

page.run_task(update_ui)  # Must pass async def
```

---

**Applicable Version**: Flet >= 0.82.0
**Total Breaking Changes**: 82+ (continuously updated)
