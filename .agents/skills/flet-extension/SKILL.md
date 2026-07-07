---
name: flet-extension
description: "Expert knowledge for creating Flet extension packages (Service Controls and UI Controls). Covers Python/Dart integration, type mapping, events, compound widgets, @control/@value decorators, Prop descriptor, project configuration, publishing, and awareness of companion extensions (flet-video screenshot + configurable controls, flet-audio AudioRecorder PCM16 streaming). Flet 0.85.x+."
---

# Flet Extension Development — Complete Reference

> Flet 0.85.x | Validated against real production extensions (flet-onesignal, flet-vibration, flet-video, flet-audio)

## Flet 0.85.x context for extensions

- Companion extensions evolved in lockstep with 0.85.0:
  - **`flet-video`** — Configurable player controls (show/hide play/pause, seek bar, fullscreen, etc.) and an async `take_screenshot()` method on the player control
  - **`flet-audio`** — New `AudioRecorder` with PCM16 streaming and direct upload to backend
- Core APIs your extension may want to integrate with:
  - `page.take_screenshot()` / `page.take_animation()` and the new top-level `Screenshot` control (`flet.controls.core.screenshot.Screenshot`)
  - `ft.Router` outlets — if your extension renders a navigator/host, expose hooks for `use_route_params` / `use_view_path` interop
  - `ft.use_dialog` — for UI controls that surface dialogs, prefer this hook over imperative `page.show_dialog`
- The deprecated `DragTargetEvent.x/y/offset` properties (replaced by `local_position` / `global_position` in 0.85.0) affect any extension that re-emits or wraps drag targets — update before 0.88.0.

---

## Extension Architecture Overview

### Two Extension Types

| Aspect | `ft.Service` | `ft.LayoutControl` |
|--------|-------------|-------------------|
| Has UI | No | Yes |
| Base class (Python) | `ft.Service` | `ft.LayoutControl` |
| Base class (Dart) | `FletService` | `StatefulWidget` |
| Add to app | `page.services.append()` | `page.add()` / controls list |
| Extension handler | `createService(control)` | `createWidget(control)` |
| width/height | No | Yes (inherited) |
| expand | No | Yes (inherited) |
| Examples | Push notifications, audio, geolocation | WebView, video player, map |

### When to Use Which

- **Service**: SDKs that run in background, platform APIs (push, permissions, location, audio)
- **UI Control**: Widgets that render on screen and occupy visual space (players, maps, charts)

### Directory Structure

```
flet-my-extension/
├── pyproject.toml                    # Python package config
├── README.md
├── CHANGELOG.md
├── LICENSE
├── tests/
│   └── test_my_extension.py
├── examples/
│   └── flet_my_extension_example/
│       ├── pyproject.toml            # Example app config
│       └── src/
│           └── main.py
└── src/
    ├── flet_my_extension/            # Python code
    │   ├── __init__.py               # Public exports
    │   ├── my_service.py             # Main control (ft.Service or ft.LayoutControl)
    │   ├── sub_module_a.py           # Sub-module A (pure Python class)
    │   ├── sub_module_b.py           # Sub-module B (pure Python class)
    │   └── types.py                  # Enums, events, dataclasses
    └── flutter/flet_my_extension/    # Flutter/Dart code
        ├── pubspec.yaml
        └── lib/
            ├── flet_my_extension.dart  # Only exports Extension
            └── src/
                ├── extension.dart      # Extension registration
                └── my_service.dart     # Flutter implementation
```

### Extension Registration Pattern

```dart
// lib/flet_my_extension.dart
library flet_my_extension;
export 'src/extension.dart' show Extension;
```

```dart
// lib/src/extension.dart — FOR SERVICES
import 'package:flet/flet.dart';
import 'my_service.dart';

class Extension extends FletExtension {
  @override
  void ensureInitialized() {
    debugPrint("MyPlugin: ensureInitialized");
  }

  @override
  FletService? createService(Control control) {
    switch (control.type) {
      case "MyService":  // Must match @ft.control("MyService")
        return MyServiceImpl(control: control);
      default:
        return null;
    }
  }
}
```

```dart
// lib/src/extension.dart — FOR UI CONTROLS
import 'package:flet/flet.dart';
import 'my_widget.dart';

class Extension extends FletExtension {
  @override
  Widget? createWidget(Control control) {
    switch (control.type) {
      case "MyWidget":  // Must match @ft.control("MyWidget")
        return MyWidgetWidget(control: control);
      default:
        return null;
    }
  }
}
```

**Critical rule:** `control.type` must be identical to the string in `@ft.control("MyService")`.

---

## flet-pkg CLI Tool

### Overview

`flet-pkg` is a CLI tool that scaffolds Flet extension packages with auto-generated code from Flutter package analysis.

### Usage

```bash
# Auto-analyze a Flutter package from pub.dev and generate code
flet-pkg create my-extension --analyze

# Skip analysis (manual implementation)
flet-pkg create my-extension --no-analyze

# Use a local Dart package instead of pub.dev
flet-pkg create my-extension --local-package /path/to/dart/pkg

# Choose extension type
flet-pkg create my-extension --type service     # ft.Service
flet-pkg create my-extension --type ui_control  # ft.LayoutControl
```

### Pipeline: download → parse → analyze → generate

1. **Download**: Fetches Flutter package source from pub.dev (cached in `~/.cache/flet-pkg/`)
2. **Parse**: Extracts Dart API (classes, methods, properties, enums) from source files
3. **Analyze**: Creates a `GenerationPlan` with Python↔Dart mappings, type conversions, invoke keys
4. **Generate**: Produces Python control, types, init, and Dart service files from templates

### When to Use flet-pkg vs Manual

- **flet-pkg**: When wrapping an existing Flutter/Dart package — auto-generates type mappings, method stubs, enum definitions
- **Manual**: When creating a novel extension or when the Flutter package is very complex with custom patterns

---

## Service Control Pattern (Python)

### Main Control Class

```python
# src/flet_my_extension/my_service.py

from dataclasses import field
from typing import Any, Optional

import flet as ft

from flet_my_extension.sub_module_a import SubModuleA
from flet_my_extension.types import (
    MyEvent,
    MyLogLevel,
    ErrorEvent,
)


@ft.control("MyService")  # Name must correspond to Flutter side
class MyService(ft.Service):
    """
    Integration service for XYZ SDK.

    Add to `page.services` — do NOT use `page.overlay`.

    Example:
        ```python
        service = MyService(app_id="your-id")
        page.services.append(service)
        await service.do_something("param")
        ```
    """

    # ── Public properties (sent to Flutter) ─────────────────────────────
    app_id: str = ""
    log_level: Optional[MyLogLevel] = None
    require_consent: bool = False

    # ── Public events ────────────────────────────────────────────────────
    on_event: Optional[ft.EventHandler[MyEvent]] = None
    on_error: Optional[ft.EventHandler[ErrorEvent]] = None

    # ── Internal fields (NOT sent to Flutter) ────────────────────────────
    _sub_a: SubModuleA = field(default=None, init=False, metadata={"skip": True})

    # ── Lifecycle ────────────────────────────────────────────────────────
    def init(self):
        """Called when the control is mounted in the Flutter tree."""
        super().init()
        self._sub_a = SubModuleA(self)

    # ── Properties (lazy init for robustness) ────────────────────────────
    @property
    def sub_a(self) -> SubModuleA:
        if self._sub_a is None:
            self._sub_a = SubModuleA(self)
        return self._sub_a

    # ── Public methods (call Flutter via _invoke_method) ─────────────────
    async def login(self, user_id: str) -> None:
        await self._invoke_method("login", {"user_id": user_id})

    async def logout(self) -> None:
        await self._invoke_method("logout")

    async def get_status(self, timeout: float = 10.0) -> bool:
        result = await self._invoke_method("get_status", timeout=timeout)
        return result == "true"

    async def get_tags(self) -> dict:
        import json
        result = await self._invoke_method("get_tags")
        return json.loads(result) if result else {}

    # ── Platform validation ──────────────────────────────────────────────
    def _is_supported_platform(self) -> bool:
        """Validate before calling methods (NOT in before_update)."""
        if not self.page:
            return False
        return self.page.platform in (
            ft.PagePlatform.ANDROID,
            ft.PagePlatform.IOS,
        )

    async def _invoke_method(
        self,
        method_name: str,
        arguments: Optional[dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> Any:
        """Override to add platform validation."""
        if not self._is_supported_platform():
            platform = self.page.platform.value if self.page else "unknown"
            raise ft.FletUnsupportedPlatformException(
                f"MyService only supports Android and iOS. "
                f"Current platform: {platform}."
            )
        effective_timeout = timeout if timeout is not None else 25.0
        return await super()._invoke_method(
            method_name=method_name,
            arguments=arguments or {},
            timeout=effective_timeout,
        )
```

### Sub-Module (Pure Python Class)

```python
# src/flet_my_extension/sub_module_a.py

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from flet_my_extension.my_service import MyService


class SubModuleA:
    """
    Sub-module A — Namespace for functionality.

    Does not inherit from ft.Service. Delegates _invoke_method to parent service.
    Mirrors the modular architecture of third-party SDKs.
    """

    def __init__(self, service: "MyService"):
        self._service = service

    async def do_something(self, param: str) -> Optional[str]:
        result = await self._service._invoke_method(
            "sub_a_do_something",
            {"param": param},
        )
        return result if result else None

    async def get_value(self, timeout: float = 25) -> bool:
        result = await self._service._invoke_method(
            "sub_a_get_value",
            timeout=timeout,
        )
        return result == "true"
```

---

## Service Control Pattern (Dart)

### FletService Implementation

```dart
// lib/src/my_service.dart
import 'dart:convert';
import 'package:flet/flet.dart';
import 'package:flutter/foundation.dart';
import 'package:third_party_sdk/third_party_sdk.dart';

class MyServiceImpl extends FletService {
  MyServiceImpl({required super.control});

  bool _initialized = false;
  bool _listenersSetup = false;

  // ── Lifecycle ─────────────────────────────────────────────────────────

  @override
  void init() {
    super.init();
    debugPrint("MyService.init: type=${control.type}");

    // Register invoke method handler BEFORE initializing
    control.addInvokeMethodListener(_onInvokeMethod);

    // Initialize SDK with current control properties
    _initializeSdk();
  }

  @override
  Future<void> update() async {
    // Called when Python properties change
    final appId = control.getString("app_id");
    if (appId != null && !_initialized) {
      _initializeSdk();
    }
  }

  @override
  void dispose() {
    // Clean up listeners and resources on unmount
    super.dispose();
  }

  // ── SDK Initialization ────────────────────────────────────────────────

  void _initializeSdk() {
    final appId = control.getString("app_id");
    if (appId == null || appId.isEmpty) {
      debugPrint("MyService: app_id not provided");
      return;
    }

    try {
      // Configure BEFORE initializing (read SDK docs)
      final logLevel = control.getString("log_level");
      if (logLevel != null) {
        _configureLog(logLevel);
      }

      final requireConsent = control.getBool("require_consent", false)!;
      if (requireConsent) {
        Sdk.consentRequired(true);
      }

      Sdk.initialize(appId);
      _initialized = true;

      // Set up listeners AFTER initialization
      _setupListeners();
    } catch (error, stackTrace) {
      _handleError("_initializeSdk", error, stackTrace);
    }
  }

  // ── SDK Listeners → Python Events ─────────────────────────────────────

  void _setupListeners() {
    if (_listenersSetup) return;  // Guard against duplicates
    _listenersSetup = true;

    Sdk.addListener((event) {
      try {
        control.triggerEvent("event", {
          "data": event.data,
          "success": true,
        });
      } catch (error, stackTrace) {
        _handleError("event_listener", error, stackTrace);
      }
    });

    debugPrint("MyService._setupListeners: ready");
  }

  // ── Invoke Method Handler (Python → Dart) ─────────────────────────────

  Future<dynamic> _onInvokeMethod(String methodName, dynamic args) async {
    try {
      // IMPORTANT: Convert args to Map<String, dynamic>
      // Can arrive as _Map<dynamic, dynamic> from Flet
      Map<String, dynamic> arguments = {};
      if (args != null && args is Map) {
        arguments = Map<String, dynamic>.from(args);
      }

      debugPrint("MyService._onInvokeMethod: method=$methodName, args=$arguments");

      // Use switch expression (Dart 3+)
      return switch (methodName) {
        "login"              => await _login(arguments),
        "logout"             => await _logout(),
        "get_status"         => _getStatus(),
        "get_tags"           => await _getTags(),
        "sub_a_do_something" => await _subADoSomething(arguments),
        "sub_a_get_value"    => _subAGetValue(),
        _                    => throw Exception("Unknown method: $methodName"),
      };
    } catch (error, stackTrace) {
      _handleError(methodName, error, stackTrace);
      return null;
    }
  }

  // ── Method Implementations ────────────────────────────────────────────

  Future<String?> _login(Map<String, dynamic> args) async {
    final userId = args["user_id"] as String?;
    if (userId != null) {
      await Sdk.login(userId);
    }
    return null;  // Return null for void methods
  }

  Future<String?> _logout() async {
    await Sdk.logout();
    return null;
  }

  String _getStatus() {
    // Return "true"/"false" for booleans
    // Python does: result == "true"
    return Sdk.getStatus().toString();
  }

  Future<String?> _getTags() async {
    final tags = await Sdk.getTags();
    // Return as JSON string — Python does json.loads()
    return jsonEncode(tags);
  }

  Future<String?> _subADoSomething(Map<String, dynamic> args) async {
    final param = args["param"] as String?;
    if (param != null) {
      await Sdk.doSomething(param);
    }
    return null;
  }

  String _subAGetValue() {
    return Sdk.getValue().toString();
  }

  // ── Error Handling ────────────────────────────────────────────────────

  void _handleError(String method, Object error, StackTrace stackTrace) {
    debugPrint("MyService ERROR in $method: $error");
    FlutterError.reportError(FlutterErrorDetails(
      exception: error,
      stack: stackTrace,
      library: 'flet_my_extension',
      context: ErrorDescription('while executing method "$method"'),
    ));
    // Trigger error event for Python
    control.triggerEvent("error", {
      "method": method,
      "message": error.toString(),
      "stack_trace": stackTrace.toString(),
    });
  }

  // ── Configuration Helpers ─────────────────────────────────────────────

  void _configureLog(String level) {
    final sdkLevel = switch (level.toLowerCase()) {
      "none"  => LogLevel.none,
      "debug" => LogLevel.debug,
      "info"  => LogLevel.info,
      "warn"  => LogLevel.warn,
      "error" => LogLevel.error,
      _       => LogLevel.warn,
    };
    Sdk.setLogLevel(sdkLevel);
  }
}
```

---

## UI Control Pattern (Python)

### Main Control Class

```python
# src/flet_my_widget/my_widget.py

from typing import Optional
import flet as ft
from flet_my_widget.types import MyWidgetEvent, MyWidgetConfig


@ft.control("MyWidget")  # Name for Flutter registration
class MyWidget(ft.LayoutControl):
    """
    Visual widget for displaying custom content.

    Inherits from ft.LayoutControl (has width, height, expand, etc.)

    Example:
        ```python
        widget = MyWidget(
            url="https://example.com",
            width=400,
            height=300,
            on_load=lambda e: print("Loaded!"),
        )
        page.add(widget)
        ```
    """

    # Properties (sent to Flutter via automatic serialization)
    url: str = ""
    """URL or content source."""

    auto_play: bool = False
    """If True, starts automatically."""

    config: Optional[MyWidgetConfig] = None
    """Advanced configuration."""

    # Events
    on_load: Optional[ft.EventHandler[MyWidgetEvent]] = None
    """Called when content finishes loading."""

    on_error: Optional[ft.EventHandler[ft.ControlEvent]] = None
    """Called when an error occurs."""

    # Methods invoked on Flutter
    async def play(self) -> None:
        await self._invoke_method("play")

    async def pause(self) -> None:
        await self._invoke_method("pause")

    async def get_duration(self, timeout: float = 10) -> Optional[float]:
        result = await self._invoke_method("get_duration", timeout=timeout)
        return float(result) if result else None

    async def seek(self, position_seconds: float) -> None:
        await self._invoke_method("seek", {"position": position_seconds})

    # Platform validation (optional for UI controls)
    def before_update(self):
        super().before_update()
        if self.page and self.page.web and not self._supports_web():
            raise ft.FletUnsupportedPlatformException("MyWidget doesn't support web.")

    def _supports_web(self) -> bool:
        return False
```

### New 0.81.0 LayoutControl Properties

All inherited automatically by any UI Control:

| Property | Type | Description |
|----------|------|-------------|
| `transform` | `Transform` | Generic Matrix4 transform (translate, rotate, scale, skew) |
| `aspect_ratio` | `Number` | Automatic width/height ratio |
| `animate_size` | `AnimationValue` | Implicit size animation |
| `on_size_change` | `EventHandler[LayoutSizeChangeEvent]` | Event when dimensions change |
| `size_change_interval` | `int` | Sampling interval in ms (default: 10) |

```python
@ft.control("MyWidget")
class MyWidget(ft.LayoutControl):
    url: str = ""
    # Can now use Matrix4 transforms (inherited):
    # widget = MyWidget(url="...", transform=Matrix4.rotation_z(0.5))
    # widget = MyWidget(url="...", on_size_change=handle_resize)
```

### @ft.control New Parameters (0.81.0)

```python
# isolated=True: excludes control from parent updates
@ft.control("MyWidget", isolated=True)
class MyWidget(ft.LayoutControl):
    ...

# post_init_args: for controls with InitVar
@ft.control("MyWidget", post_init_args=1)
class MyWidget(ft.LayoutControl):
    ...
```

---

## UI Control Pattern (Dart)

### StatefulWidget Implementation

```dart
// lib/src/my_widget.dart
import 'package:flet/flet.dart';
import 'package:flutter/widgets.dart';
import 'package:third_party_sdk/third_party_sdk.dart';

class MyWidgetWidget extends StatefulWidget {
  final Control control;
  const MyWidgetWidget({super.key, required this.control});

  @override
  State<MyWidgetWidget> createState() => _MyWidgetWidgetState();
}

class _MyWidgetWidgetState extends State<MyWidgetWidget> {
  late final SdkController _controller;

  @override
  void initState() {
    super.initState();
    _controller = SdkController();

    // Register handler for Python method invocations
    widget.control.addInvokeMethodListener(_onInvokeMethod);

    // Setup listeners
    _setupListeners();
  }

  @override
  void didUpdateWidget(MyWidgetWidget oldWidget) {
    super.didUpdateWidget(oldWidget);
    // React to changes in Python properties
    final url = widget.control.getString("url");
    if (url != null) {
      _controller.loadUrl(url);
    }
  }

  void _setupListeners() {
    _controller.onLoad = () {
      widget.control.triggerEvent("load", {
        "status": "ready",
        "duration": _controller.duration,
      });
    };

    _controller.onError = (error) {
      widget.control.triggerEvent("error", {
        "status": "error",
        "message": error,
      });
    };
  }

  Future<dynamic> _onInvokeMethod(String name, dynamic args) async {
    Map<String, dynamic> arguments = {};
    if (args != null && args is Map) {
      arguments = Map<String, dynamic>.from(args);
    }

    return switch (name) {
      "play"         => _controller.play(),
      "pause"        => _controller.pause(),
      "get_duration" => _controller.duration?.toString(),
      "seek"         => _controller.seek(
                          Duration(
                            milliseconds: ((arguments["position"] as double) * 1000).toInt(),
                          )
                        ),
      _              => throw Exception("Unknown method: $name"),
    };
  }

  @override
  Widget build(BuildContext context) {
    return ConstrainedBox(
      constraints: BoxConstraints(
        minWidth: widget.control.getDouble("width") ?? 0,
        minHeight: widget.control.getDouble("height") ?? 0,
      ),
      child: SdkWidget(controller: _controller),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }
}
```

---

## Python ↔ Flutter Communication

### Overview

```
Python (ft.Service)               Flutter (FletService)
─────────────────────             ─────────────────────
Properties (fields)      →→→→→→   control.getString("field")
                                  control.getBool("field", default)

await _invoke_method()   →→→→→→   control.addInvokeMethodListener()
        ↑                                    ↓
    returns value        ←←←←←←   return "value"

ft.EventHandler[Type]   ←←←←←←   control.triggerEvent("name", data)
```

### 1. Python → Flutter: Properties

```python
# Python declaration
@ft.control("MyService")
class MyService(ft.Service):
    app_id: str = ""
    log_level: Optional[MyLogLevel] = None
    require_consent: bool = False
```

```dart
// Dart reading
final appId = control.getString("app_id");
final logLevel = control.getString("log_level");
final requireConsent = control.getBool("require_consent", false)!;
```

**Enums are serialized as their `.value` (string):**

```python
# Python
class MyLogLevel(Enum):
    DEBUG = "debug"

# Dart receives: "debug"
final levelStr = control.getString("log_level");  // "debug"
```

### 2. Python → Flutter: Invoke Methods

```python
# Python — basic call (no return)
await self._invoke_method("logout")

# With arguments
await self._invoke_method("login", {"user_id": user_id})

# With return + custom timeout
result = await self._invoke_method("get_status", timeout=10.0)
return result == "true"

# Complex data return (JSON)
result = await self._invoke_method("get_tags")
return json.loads(result) if result else {}
```

```dart
// Dart — handler
control.addInvokeMethodListener(_onInvokeMethod);

Future<dynamic> _onInvokeMethod(String methodName, dynamic args) async {
    // ALWAYS convert args
    Map<String, dynamic> arguments = {};
    if (args != null && args is Map) {
        arguments = Map<String, dynamic>.from(args);
    }

    return switch (methodName) {
        "logout"     => await _logout(),
        "login"      => await _login(arguments),
        "get_status" => _getStatus(),
        "get_tags"   => await _getTags(),
        _            => throw Exception("Unknown method: $methodName"),
    };
}
```

### 3. Flutter → Python: Events

```dart
// Dart — trigger event
control.triggerEvent("permission_change", {
    "permission": true,
});

// Error event (standard pattern)
control.triggerEvent("error", {
    "method": "method_name",
    "message": error.toString(),
    "stack_trace": stackTrace.toString(),
});
```

```python
# Python — receive event
@dataclass
class PermissionChangeEvent(ft.Event["MyService"]):
    permission: bool = False

@ft.control("MyService")
class MyService(ft.Service):
    on_permission_change: Optional[ft.EventHandler[PermissionChangeEvent]] = None

# Usage
service = MyService(
    on_permission_change=lambda e: print(f"Permission: {e.permission}"),
)
```

**Event name mapping:**

| Dart `triggerEvent(name, ...)` | Python `on_name: EventHandler` |
|-------------------------------|-------------------------------|
| `"permission_change"` | `on_permission_change` |
| `"notification_click"` | `on_notification_click` |
| `"error"` | `on_error` |

**Rule:** `triggerEvent("snake_case_name")` → `on_snake_case_name`

### 4. Internal Fields (NOT Sent to Flutter)

```python
from dataclasses import field

@ft.control("MyService")
class MyService(ft.Service):
    # Normal field → sent to Flutter
    app_id: str = ""

    # Internal field → NOT sent to Flutter
    _sub_module: SubModule = field(
        default=None,
        init=False,
        metadata={"skip": True}  # This excludes it from serialization
    )
```

### 5. Timeout

```python
# Default: 25 seconds
await self._invoke_method("login", {"user_id": uid})

# Custom timeout for fast operations
result = await self._invoke_method("get_permission", timeout=10.0)

# Custom timeout for slow operations (e.g., permission request with UI)
result = await self._invoke_method(
    "request_permission",
    {"fallback_to_settings": True},
    timeout=30.0,
)
```

### Naming Conventions

| Side | Convention |
|------|-----------|
| Python: property field | `snake_case` (`app_id`, `log_level`) |
| Python: method | `snake_case` async (`login`, `get_status`) |
| Python: event | `on_snake_case` (`on_permission_change`) |
| Dart: `triggerEvent(name)` | `"snake_case"` (`"permission_change"`) |
| Dart: `_onInvokeMethod(name)` | `"snake_case"` (`"login"`, `"get_status"`) |
| `@ft.control("Name")` | `PascalCase` (`"MyService"`, `"OneSignal"`) |
| Dart: `control.type` switch | Same PascalCase (`"MyService"`) |

---

## Type Mapping (Dart → Python)

### Standard Type Mappings

| Dart Type | Python Type (Service) | Python Type (UI Control) |
|-----------|----------------------|-------------------------|
| `String` | `str` | `str` |
| `bool` | `bool` | `bool` |
| `int` | `int` | `int` |
| `double` | `float` | `ft.Number` |
| `num` | `float` | `ft.Number` |
| `void` | `None` | `None` |
| `dynamic` | `Any` | `Any` |
| `Object` | `Any` | `Any` |
| `Color` | `str` | `ft.Color` |
| `Duration` | `int` | `int` |
| `DateTime` | `str` | `str` |
| `Uint8List` | `bytes` | `bytes` |
| `Uri` | `str` | `str` |

### Generic Type Mappings

| Dart Generic | Python Type |
|-------------|-------------|
| `List<String>` | `list[str]` |
| `List<int>` | `list[int]` |
| `Set<String>` | `set[str]` |
| `Map<String, dynamic>` | `dict[str, Any]` |
| `Map<String, String>` | `dict[str, str]` |
| `Future<T>` | Unwrapped to `T` |
| `Iterable<T>` | `list[T]` |

### Nullable Types

| Dart | Python |
|------|--------|
| `String?` | `str \| None` |
| `int?` | `int \| None` |
| `List<String>?` | `list[str] \| None` |

### Flet-Aware Mappings (UI Controls)

These use native Flet types for richer UI integration:

| Dart Type | Flet Python Type | Dart Getter |
|-----------|-----------------|-------------|
| `Alignment` | `ft.Alignment` | `control.getAlignment("name")` |
| `BoxFit` | `ft.BoxFit` | `control.getBoxFit("name")` |
| `Color` | `ft.Color` | `control.getString("name")` |
| `double` / `num` | `ft.Number` | `control.getDouble("name")` |
| `Widget` | `ft.Control` | `buildWidget("name")` |
| `TextStyle` | `ft.TextStyle` | `control.getTextStyle("name", Theme.of(context))` |
| `Rect` | `ft.Rect` | `control.getRect("name")` |
| `Key` | *skipped* | N/A |

### Flutter Enum Mappings

Common Flutter enums are mapped to `str` for serialization:

| Dart Enum | Python Type |
|-----------|-------------|
| `TextDirection` | `str` |
| `Axis` | `str` |
| `MainAxisAlignment` | `str` |
| `CrossAxisAlignment` | `str` |
| `TextAlign` | `str` |
| `FontWeight` | `str` |
| `BoxFit` | `str` (service) / `ft.BoxFit` (UI) |
| `Alignment` | `str` (service) / `ft.Alignment` (UI) |
| `Clip` | `str` |
| `Curve` | `str` |
| `Brightness` | `str` |

### Return Type Conventions

| Python Type | Dart Return | Python Conversion |
|-------------|------------|-------------------|
| `None` | `return null` | — |
| `bool` | `return result.toString()` → `"true"/"false"` | `result == "true"` |
| `str` | `return value` | `result if result else None` |
| `dict` | `return jsonEncode(map)` | `json.loads(result)` |
| `int`/`float` | `return value.toString()` | `int(result)` / `float(result)` |

---

## Types, Events & Enums

### Enum Pattern

```python
from enum import Enum

class MyLogLevel(Enum):
    """Log levels for the SDK."""
    NONE = "none"
    DEBUG = "debug"
    INFO = "info"
    WARN = "warn"
    ERROR = "error"
```

**Serialization:** Sub-modules send `param.value` (the string), not the raw enum object.

### Event Dataclass Pattern

```python
from dataclasses import dataclass
from typing import Optional
import flet as ft


@dataclass
class MyEvent(ft.Event["MyService"]):
    """Event triggered by the SDK.

    The type parameter of ft.Event is the parent control class.
    """
    data: str = ""
    success: bool = False


@dataclass
class ErrorEvent(ft.Event["MyService"]):
    """Standard error event."""
    method: Optional[str] = None
    message: Optional[str] = None
    stack_trace: Optional[str] = None
```

### Standard ErrorEvent Pattern

Every extension should include an `ErrorEvent` and `on_error` handler:

```python
# types.py
@dataclass
class ErrorEvent(ft.Event["MyService"]):
    method: Optional[str] = None
    message: Optional[str] = None
    stack_trace: Optional[str] = None

# my_service.py
@ft.control("MyService")
class MyService(ft.Service):
    on_error: Optional[ft.EventHandler[ErrorEvent]] = None
```

```dart
// my_service.dart
void _handleError(String method, Object error, StackTrace stackTrace) {
    debugPrint("MyService ERROR in $method: $error");
    FlutterError.reportError(FlutterErrorDetails(
      exception: error,
      stack: stackTrace,
      library: 'flet_my_extension',
      context: ErrorDescription('while executing method "$method"'),
    ));
    control.triggerEvent("error", {
      "method": method,
      "message": error.toString(),
      "stack_trace": stackTrace.toString(),
    });
}
```

---

## Project Configuration

### pyproject.toml (Extension)

```toml
[project]
name = "flet-my-extension"
version = "0.1.0"
description = "My Flet extension."
requires-python = ">=3.10"
readme = "README.md"
authors = [{ name = "Your Name", email = "you@email.com" }]
license = "MIT"

classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
]

dependencies = ["flet>=0.80.0"]

[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"

# CRITICAL: Includes Flutter/Dart code in the Python wheel
[tool.setuptools.package-data]
"flutter.flet_my_extension" = ["**/*"]

[dependency-groups]
dev = [
    "flet[all]>=0.80.0",
    "pytest>=7.2.0",
    "pytest-cov>=7.0.0",
]

[tool.ruff]
target-version = "py312"
line-length = 100
src = ["src", "tests"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --tb=short"
```

**Why `[tool.setuptools.package-data]` is critical:** The Flet build system locates Dart code inside the installed Python package. Without this, the wheel won't contain the Dart files and `flet build` will fail.

### pubspec.yaml (Flutter)

```yaml
name: flet_my_extension
description: "My Flet extension."
version: 0.1.0
publish_to: none  # Do NOT publish to pub.dev separately

environment:
  sdk: ^3.5.2
  flutter: ">=3.29.0"

dependencies:
  flutter:
    sdk: flutter
  flet: ^0.80.5
  third_party_sdk: ^5.0.0

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^5.0.0
```

### Example App pyproject.toml

```toml
[project]
name = "flet-my-extension-example"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "flet>=0.80.0",
    "flet-my-extension @ file://../../../",  # Local dev dependency
]

[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"

# CRITICAL for src/ layout
[tool.flet.app]
path = "src"
```

### Extension Registration in App

```toml
# pyproject.toml of the APP (not the extension)
[tool.flet.extensions]
flet_my_extension = "flet_my_extension.Extension"
```

---

## Advanced Patterns

### Compound Widgets / Sub-Controls

When a Flutter widget accepts typed sub-widget parameters (e.g., `ActionPane?`), these become sub-controls:

```python
# Parent control
@ft.control("MySlider")
class MySlider(ft.LayoutControl):
    thumb: Optional["MyThumb"] = None  # Sub-control
    track: Optional["MyTrack"] = None  # Sub-control

# Sub-control
@ft.control("MyThumb")
class MyThumb(ft.Control):
    color: str = ""
    size: float = 20.0
```

List patterns (`List<BarItem>`) are also supported:

```python
items: list["BarItem"] = field(default_factory=list)
```

### Sub-Modules (Namespace Classes)

For complex SDKs with multiple namespaces (like OneSignal's User, Notifications, Debug):

```python
class User:
    """User namespace — pure Python class, delegates to parent service."""

    def __init__(self, service: "MyService"):
        self._service = service

    async def set_tag(self, key: str, value: str) -> None:
        await self._service._invoke_method(
            "user_set_tag", {"key": key, "value": value}
        )

    async def get_tags(self) -> dict:
        import json
        result = await self._service._invoke_method("user_get_tags")
        return json.loads(result) if result else {}
```

### Stream Getters → Event Handlers

Dart `Stream<T> get onXxx` patterns are detected and converted to event handlers:

```dart
// Dart
Stream<PermissionState> get onPermissionChange => ...
```

```python
# Python
on_permission_change: Optional[ft.EventHandler[PermissionChangeEvent]] = None
```

---

## Anti-Patterns

### Python Anti-Patterns

```python
# WRONG: _set_attr in __init__ (pre-0.80.x pattern)
class MyService(ft.Service):
    def __init__(self, app_id, **kwargs):
        super().__init__(**kwargs)
        self._set_attr("appId", app_id)  # AttributeError in 0.80.x
# CORRECT: dataclass fields
@ft.control("MyService")
class MyService(ft.Service):
    app_id: str = ""

# WRONG: @ft.control without string name
@ft.control
class MyService(ft.Service): ...  # ValueError: must have type_name
# CORRECT:
@ft.control("MyService")
class MyService(ft.Service): ...

# WRONG: import from flet.core (structure changed)
from flet.core.control_event import ControlEvent  # ModuleNotFoundError
# CORRECT:
import flet as ft  # ft.ControlEvent, ft.EventHandler, ft.Event

# WRONG: add Service to page.add() or overlay
page.add(my_service)             # Service has no UI
page.overlay.append(my_service)  # Not a dialog/overlay
# CORRECT:
page.services.append(my_service)

# WRONG: add LayoutControl to page.services
page.services.append(my_widget)  # Widget has UI, not a service
# CORRECT:
page.add(my_widget)

# WRONG: invoke methods without platform validation
async def login(self, user_id):
    await self._invoke_method("login", {"user_id": user_id})
    # Will throw AttributeError on desktop
# CORRECT:
async def _invoke_method(self, method, args=None, timeout=None):
    if not self._is_supported():
        raise ft.FletUnsupportedPlatformException(...)
    return await super()._invoke_method(...)

# WRONG: internal field without metadata skip
_sub_module: SubModule = field(default=None, init=False)
# CORRECT:
_sub_module: SubModule = field(default=None, init=False, metadata={"skip": True})
```

### Dart Anti-Patterns

```dart
// WRONG: not converting args (ClassCastException: _Map<dynamic, dynamic>)
Future<dynamic> _onInvokeMethod(String name, dynamic args) async {
    final userId = args["user_id"] as String;  // May fail
// CORRECT:
    Map<String, dynamic> arguments = {};
    if (args != null && args is Map) {
        arguments = Map<String, dynamic>.from(args);
    }
    final userId = arguments["user_id"] as String?;

// WRONG: returning bool without converting to String
String _hasVibrator() {
    return Vibration.hasVibrator();  // Returns bool, not String
// CORRECT:
String _hasVibrator() {
    return Vibration.hasVibrator().toString();  // "true" or "false"

// WRONG: control.type mismatch with @ft.control
// Python: @ft.control("myservice")  |  Dart: case "MyService"
// CORRECT: use EXACTLY the same string
// Python: @ft.control("MyService")  |  Dart: case "MyService"

// WRONG: duplicate listeners on every update()
@override
Future<void> update() async {
    _setupListeners();  // Adds listeners repeatedly
// CORRECT:
bool _listenersSetup = false;
void _setupListeners() {
    if (_listenersSetup) return;
    _listenersSetup = true;
    // ...
}

// WRONG: no error handling in SDK listeners
Sdk.addListener((event) {
    control.triggerEvent("event", event.toMap());
    // If event.toMap() throws, the Flutter app crashes
// CORRECT:
Sdk.addListener((event) {
    try {
        control.triggerEvent("event", event.toMap());
    } catch (error, stackTrace) {
        _handleError("listener_event", error, stackTrace);
    }
});
```

### Common Errors Table

| Error | Cause | Solution |
|-------|-------|---------|
| `ModuleNotFoundError: flet.core` | Old internal import path | `import flet as ft` |
| `AttributeError: _set_attr` | Pre-0.80.x property pattern | Use dataclass fields |
| `AttributeError: invoke_method_async` | Call on unsupported platform | Validate `page.platform` |
| `ValueError: must have type_name` | `@ft.control` without string | `@ft.control("PascalCase")` |
| `ClassCastException: _Map<dynamic>` | Dart args not converted | `Map<String, dynamic>.from(args)` |
| `control.type` never matches | Case mismatch with @ft.control | Use identical string |
| Internal field sent to Flutter | Missing metadata skip | `metadata={"skip": True}` |
| Dart code not in wheel | Missing package-data | Add `[tool.setuptools.package-data]` |
| Duplicate events fired | Listeners added on every update | Guard with `_listenersSetup` flag |

---

## Complete Service Extension Template

### Vibration Service Example

**types.py:**

```python
from dataclasses import dataclass
from enum import Enum
from typing import Optional
import flet as ft


class VibrationPattern(Enum):
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"
    DOUBLE = "double"
    SOS = "sos"


@dataclass
class VibrationEvent(ft.Event["Vibration"]):
    pattern: str = ""
    duration_ms: int = 0
    success: bool = True


@dataclass
class VibrationErrorEvent(ft.Event["Vibration"]):
    method: Optional[str] = None
    message: Optional[str] = None
```

**vibration.py:**

```python
from dataclasses import field
from typing import Any, Optional
import flet as ft
from flet_vibration.types import VibrationErrorEvent, VibrationEvent, VibrationPattern


@ft.control("Vibration")
class Vibration(ft.Service):
    on_vibrated: Optional[ft.EventHandler[VibrationEvent]] = None
    on_error: Optional[ft.EventHandler[VibrationErrorEvent]] = None

    async def vibrate(self, pattern: VibrationPattern = VibrationPattern.SHORT) -> None:
        await self._call("vibrate", {"pattern": pattern.value})

    async def vibrate_duration(self, duration_ms: int) -> None:
        duration_ms = max(1, min(10000, duration_ms))
        await self._call("vibrate_duration", {"duration_ms": duration_ms})

    async def cancel(self) -> None:
        await self._call("cancel")

    async def has_vibrator(self) -> bool:
        result = await self._call("has_vibrator", timeout=5.0)
        return result == "true"

    def _is_supported(self) -> bool:
        if not self.page:
            return False
        return self.page.platform in (ft.PagePlatform.ANDROID, ft.PagePlatform.IOS)

    async def _call(self, method: str, args: Optional[dict[str, Any]] = None,
                    timeout: Optional[float] = None) -> Any:
        if not self._is_supported():
            platform = self.page.platform.value if self.page else "unknown"
            raise ft.FletUnsupportedPlatformException(
                f"Vibration only supported on Android/iOS. Current: {platform}"
            )
        return await super()._invoke_method(
            method_name=method, arguments=args or {},
            timeout=timeout if timeout is not None else 10.0,
        )
```

**__init__.py:**

```python
from flet_vibration.vibration import Vibration
from flet_vibration.types import VibrationErrorEvent, VibrationEvent, VibrationPattern

__all__ = ["Vibration", "VibrationEvent", "VibrationErrorEvent", "VibrationPattern"]
__version__ = "0.1.0"
```

**Dart — extension.dart:**

```dart
import 'package:flet/flet.dart';
import 'vibration_service.dart';

class Extension extends FletExtension {
  @override
  void ensureInitialized() {}

  @override
  FletService? createService(Control control) {
    switch (control.type) {
      case "Vibration":
        return VibrationService(control: control);
      default:
        return null;
    }
  }
}
```

**Dart — vibration_service.dart:**

```dart
import 'package:flet/flet.dart';
import 'package:flutter/foundation.dart';
import 'package:vibration/vibration.dart';

class VibrationService extends FletService {
  VibrationService({required super.control});

  @override
  void init() {
    super.init();
    control.addInvokeMethodListener(_onInvokeMethod);
  }

  @override
  void dispose() {
    Vibration.cancel();
    super.dispose();
  }

  Future<dynamic> _onInvokeMethod(String methodName, dynamic args) async {
    try {
      Map<String, dynamic> arguments = {};
      if (args != null && args is Map) {
        arguments = Map<String, dynamic>.from(args);
      }

      return switch (methodName) {
        "vibrate"          => await _vibrate(arguments),
        "vibrate_duration" => await _vibrateDuration(arguments),
        "cancel"           => await _cancel(),
        "has_vibrator"     => await _hasVibrator(),
        _ => throw Exception("Unknown method: $methodName"),
      };
    } catch (error, stackTrace) {
      _handleError(methodName, error, stackTrace);
      return null;
    }
  }

  Future<String?> _vibrate(Map<String, dynamic> args) async {
    final pattern = args["pattern"] as String? ?? "short";
    final durationMs = _patternDuration(pattern);
    await Vibration.vibrate(duration: durationMs);

    control.triggerEvent("vibrated", {
      "pattern": pattern,
      "duration_ms": durationMs,
      "success": true,
    });
    return null;
  }

  Future<String?> _vibrateDuration(Map<String, dynamic> args) async {
    final durationMs = args["duration_ms"] as int? ?? 300;
    await Vibration.vibrate(duration: durationMs);

    control.triggerEvent("vibrated", {
      "pattern": "custom",
      "duration_ms": durationMs,
      "success": true,
    });
    return null;
  }

  Future<String?> _cancel() async {
    await Vibration.cancel();
    return null;
  }

  Future<String> _hasVibrator() async {
    final has = await Vibration.hasVibrator() ?? false;
    return has.toString();
  }

  int _patternDuration(String pattern) {
    return switch (pattern) {
      "short"  => 100,
      "medium" => 300,
      "long"   => 600,
      "double" => 300,
      "sos"    => 1200,
      _        => 300,
    };
  }

  void _handleError(String method, Object error, StackTrace stackTrace) {
    debugPrint("VibrationService ERROR in $method: $error");
    control.triggerEvent("error", {
      "method": method,
      "message": error.toString(),
    });
  }
}
```

**Example app:**

```python
import flet as ft
import flet_vibration as fv


async def main(page: ft.Page):
    page.title = "Vibration Demo"

    vibration = fv.Vibration(
        on_vibrated=lambda e: print(f"Vibrated! Pattern: {e.pattern}, {e.duration_ms}ms"),
        on_error=lambda e: print(f"Error: {e.message}"),
    )
    page.services.append(vibration)

    async def vibrate_pattern(pattern: fv.VibrationPattern):
        try:
            await vibration.vibrate(pattern)
        except ft.FletUnsupportedPlatformException as e:
            print(f"Not supported: {e}")

    page.add(
        ft.Text("Vibration Demo", size=24, weight=ft.FontWeight.BOLD),
        ft.Wrap([
            ft.FilledButton("Short", on_click=lambda _: vibrate_pattern(fv.VibrationPattern.SHORT)),
            ft.FilledButton("Medium", on_click=lambda _: vibrate_pattern(fv.VibrationPattern.MEDIUM)),
            ft.FilledButton("Long", on_click=lambda _: vibrate_pattern(fv.VibrationPattern.LONG)),
        ], spacing=8),
    )

ft.run(main)
```

---

## Testing Extensions

### Unit Tests

```python
# tests/test_my_extension.py
import pytest
from flet_my_extension import MyService, MyEvent, MyLogLevel, ErrorEvent


def test_service_creation():
    service = MyService(app_id="test-id", log_level=MyLogLevel.DEBUG)
    assert service.app_id == "test-id"
    assert service.log_level == MyLogLevel.DEBUG


def test_enum_values():
    assert MyLogLevel.DEBUG.value == "debug"
    assert MyLogLevel.ERROR.value == "error"


def test_event_creation():
    event = MyEvent(data="test", success=True)
    assert event.data == "test"
    assert event.success is True


def test_error_event():
    event = ErrorEvent(method="login", message="failed")
    assert event.method == "login"
    assert event.message == "failed"


def test_default_values():
    service = MyService()
    assert service.app_id == ""
    assert service.log_level is None
    assert service.on_error is None


def test_exports():
    """Verify all public API is exported."""
    from flet_my_extension import __all__
    assert "MyService" in __all__
    assert "MyEvent" in __all__
    assert "ErrorEvent" in __all__
```

### Integration Testing

```bash
# Run example app on device/emulator
cd examples/flet_my_extension_example
flet run  # Tests on current platform

# Build for target platform
flet build apk  # Android
flet build ipa  # iOS
```

---

## Publishing

### PyPI Publishing Checklist

1. Update `version` in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Verify `[tool.setuptools.package-data]` includes Dart files
4. Build: `python -m build`
5. Check wheel contents: `unzip -l dist/*.whl | grep flutter`
6. Upload: `twine upload dist/*`

### pub.dev Considerations

- Extensions use `publish_to: none` in `pubspec.yaml`
- Dart code is distributed inside the Python wheel, NOT on pub.dev
- The Flet build system extracts Dart code from installed Python packages

### Version Management

- Keep `version` in sync between `pyproject.toml` and `pubspec.yaml`
- Follow semantic versioning (MAJOR.MINOR.PATCH)
- Track Flet compatibility: `flet>=0.80.0`

---

## Breaking Changes Reference (Pre-0.80.x)

| Before | After (0.80.x+) |
|--------|-----------------|
| `_set_attr("appId", value)` | `app_id: str = ""` (dataclass field) |
| `from flet.core.control_event import ...` | `import flet as ft` |
| `page.overlay.append(service)` | `page.services.append(service)` |
| `ft.app(target=main)` | `ft.run(main)` |
| `ft.colors.BLUE` | `ft.Colors.BLUE` |
| `ft.icons.HOME` | `ft.Icons.HOME` |
| `await method_async()` | `await method()` |
| `page.platform == "android"` | `page.platform == ft.PagePlatform.ANDROID` |

---

## Implementation Checklist

### Python Side
- [ ] `@ft.control("PascalCaseName")` with explicit string name
- [ ] Correct base class: `ft.Service` or `ft.LayoutControl`
- [ ] `metadata={"skip": True}` on all internal fields
- [ ] Events typed as `Optional[ft.EventHandler[EventType]]`
- [ ] Event classes extend `ft.Event["ControlClassName"]`
- [ ] Enums with string values
- [ ] Platform validation in `_invoke_method` override
- [ ] `__init__.py` with `__all__` exports
- [ ] `ErrorEvent` and `on_error` handler

### Dart Side
- [ ] `control.type` case matches `@ft.control("Name")` exactly
- [ ] `control.addInvokeMethodListener` in `init()`
- [ ] Args converted: `Map<String, dynamic>.from(args)`
- [ ] Booleans returned as `.toString()`
- [ ] All listeners wrapped in try/catch → `_handleError()`
- [ ] Listener setup guarded with `_listenersSetup` flag
- [ ] `_handleError` with `FlutterError.reportError` + `triggerEvent("error")`
- [ ] `dispose()` cleans up resources
- [ ] Service: `createService()` | UI: `createWidget()` in extension.dart

### Project Configuration
- [ ] `[tool.setuptools.package-data]` in pyproject.toml
- [ ] `publish_to: none` in pubspec.yaml
- [ ] Example app with `[tool.flet.app] path = "src"`
- [ ] `flet>=0.80.0` in dependencies
