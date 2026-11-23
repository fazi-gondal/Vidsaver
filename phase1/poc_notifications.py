"""
Phase 1 PoC — flet-notifications foreground service smoke test.

Desktop: shows that the package imports (FGS is Android-only).
Android: request permission, start dataSync FGS, update, stop.

Add to pyproject before building APK (see phase1/PHASE1_STATUS.md):
    flet-notifications==1.1.2
    POST_NOTIFICATIONS, FOREGROUND_SERVICE, FOREGROUND_SERVICE_DATA_SYNC

Run (desktop import check):
    uv run python phase1/poc_notifications.py

For full Android test, wire this into a temporary Flet page or use
the entry below with: uv run flet run phase1/poc_notifications.py
"""

from __future__ import annotations

import asyncio
import sys


async def run_android_poc(page) -> None:
    import flet as ft
    import flet_notifications as ftn

    status = ft.Text("Ready", size=16)
    log = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, height=240)

    def add_log(msg: str) -> None:
        log.controls.append(ft.Text(msg, size=12))
        page.update()

    notifications = ftn.Notifications()
    page.services.append(notifications)

    async def on_request_perm(_):
        try:
            # API may vary slightly by flet-notifications version
            result = await notifications.request_permissions()
            status.value = f"Permission result: {result}"
            add_log(f"request_permissions -> {result}")
        except Exception as e:
            status.value = f"Permission error: {e}"
            add_log(str(e))
        page.update()

    async def on_start(_):
        try:
            await notifications.start_foreground_service(
                1,  # id must not be 0
                title="Vidsaver download",
                body="Phase 1 PoC — active",
                service_types=[ftn.AndroidForegroundServiceType.DATA_SYNC],
            )
            status.value = "Foreground service started"
            add_log("start_foreground_service OK")
        except Exception as e:
            status.value = f"Start error: {e}"
            add_log(str(e))
        page.update()

    async def on_progress(_):
        try:
            # Update ongoing notification if API supports show/update
            await notifications.show(
                1,
                title="Vidsaver download",
                body="Phase 1 PoC — 50%",
            )
            status.value = "Progress notification updated"
            add_log("progress update OK")
        except Exception as e:
            status.value = f"Update error: {e}"
            add_log(str(e))
        page.update()

    async def on_stop(_):
        try:
            await notifications.stop_foreground_service()
            status.value = "Foreground service stopped"
            add_log("stop_foreground_service OK")
        except Exception as e:
            status.value = f"Stop error: {e}"
            add_log(str(e))
        page.update()

    page.add(
        ft.SafeArea(
            ft.Column(
                [
                    ft.Text("Phase 1 — Notifications PoC", size=20, weight=ft.FontWeight.BOLD),
                    status,
                    ft.Button("1. Request notification permission", on_click=on_request_perm),
                    ft.Button("2. Start dataSync FGS", on_click=on_start),
                    ft.Button("3. Update progress", on_click=on_progress),
                    ft.Button("4. Stop FGS", on_click=on_stop),
                    ft.Divider(),
                    log,
                ],
                spacing=12,
                expand=True,
            )
        )
    )


def main(page=None):
    """Flet entry or CLI import check."""
    if page is None:
        # CLI smoke: import only
        print("=== Vidsaver Phase 1: Notifications PoC (import check) ===")
        print(f"Python: {sys.version}")
        try:
            import flet_notifications as ftn

            print(f"[OK] import flet_notifications")
            print(f"[INFO] AndroidForegroundServiceType available: {hasattr(ftn, 'AndroidForegroundServiceType')}")
            print("[PASS] Import OK. Run under Flet on Android for full FGS test.")
            return 0
        except Exception as e:
            print(f"[FAIL] import: {e}")
            return 1

    # Flet page mode
    import flet as ft

    page.title = "Vidsaver Phase 1 — Notifications"
    asyncio.create_task(run_android_poc(page))


if __name__ == "__main__":
    # Pure import test when run as script
    raise SystemExit(main())
