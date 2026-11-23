"""Optional notifications / foreground service wrapper.

Uses flet-notifications when installed. Degrades to no-ops otherwise so the
app keeps working before the Phase 1 device PoC enables the dependency.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, page: Any | None = None) -> None:
        self._page = page
        self._api = None
        self._enabled = True
        self._permission_ok = False
        self._fgs_running = False

    def attach(self, page: Any) -> None:
        self._page = page
        try:
            import flet_notifications as ftn

            self._api = ftn
            notifications = ftn.Notifications()
            page.services.append(notifications)
            setattr(page, "_notifications", notifications)
            logger.info("flet-notifications attached")
        except Exception as exc:
            logger.info("Notifications unavailable: %s", exc)
            self._api = None

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = bool(enabled)

    async def request_permission(self) -> bool:
        if not self._enabled or self._page is None:
            return False
        notifications = getattr(self._page, "_notifications", None)
        if notifications is None:
            return False
        try:
            result = await notifications.request_permissions()
            self._permission_ok = bool(result)
            return self._permission_ok
        except Exception as exc:
            logger.warning("request_permissions failed: %s", exc)
            return False

    async def start_download_session(self, title: str = "Vidsaver") -> None:
        if not self._enabled:
            return
        notifications = getattr(self._page, "_notifications", None) if self._page else None
        if notifications is None:
            return
        try:
            ftn = self._api
            types = []
            if ftn is not None:
                try:
                    types = [ftn.AndroidForegroundServiceType.DATA_SYNC]
                except Exception:
                    types = []
            await notifications.start_foreground_service(
                1,
                title=title,
                body="Download in progress",
                service_types=types or None,
            )
            self._fgs_running = True
        except Exception as exc:
            logger.warning("start_foreground_service failed: %s", exc)

    async def update_progress(self, body: str) -> None:
        if not self._enabled or not self._fgs_running:
            return
        notifications = getattr(self._page, "_notifications", None) if self._page else None
        if notifications is None:
            return
        try:
            await notifications.show(1, title="Vidsaver", body=body)
        except Exception:
            pass

    async def stop_download_session(self) -> None:
        notifications = getattr(self._page, "_notifications", None) if self._page else None
        if notifications is None:
            self._fgs_running = False
            return
        try:
            await notifications.stop_foreground_service()
        except Exception:
            pass
        self._fgs_running = False

    async def notify_completed(self, title: str) -> None:
        if not self._enabled:
            return
        notifications = getattr(self._page, "_notifications", None) if self._page else None
        if notifications is None:
            return
        try:
            await notifications.show(
                2,
                title="Download complete",
                body=title or "Video saved",
            )
        except Exception:
            pass
