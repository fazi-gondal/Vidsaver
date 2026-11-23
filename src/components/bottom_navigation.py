"""Material 3 bottom navigation for the four primary tabs."""

from __future__ import annotations

import flet as ft

from config.constants import TAB_COMPLETED, TAB_DOWNLOADING, TAB_HOME, TAB_SETTINGS
from config.theme import PRIMARY


def build_navigation_bar(
    *,
    selected_index: int,
    on_change,
    downloading_badge: int = 0,
) -> ft.NavigationBar:
    """Four-tab bar. Badge on Downloading when active/queued tasks exist."""

    def dest(icon, label, badge: int = 0):
        if badge > 0:
            return ft.NavigationBarDestination(
                icon=icon,
                label=label,
                # Flet badge support varies; label encodes count as fallback
            )
        return ft.NavigationBarDestination(icon=icon, label=label)

    downloading_label = (
        f"Downloading ({downloading_badge})" if downloading_badge > 0 else "Downloading"
    )

    return ft.NavigationBar(
        selected_index=selected_index,
        on_change=on_change,
        bgcolor=ft.Colors.SURFACE,
        indicator_color=ft.Colors.with_opacity(0.15, PRIMARY),
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icons.HOME_OUTLINED,
                selected_icon=ft.Icons.HOME_FILLED,
                label="Home",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.DOWNLOAD_OUTLINED,
                selected_icon=ft.Icons.DOWNLOAD_ROUNDED,
                label=downloading_label,
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.VIDEO_LIBRARY_OUTLINED,
                selected_icon=ft.Icons.VIDEO_LIBRARY,
                label="Completed",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.SETTINGS_OUTLINED,
                selected_icon=ft.Icons.SETTINGS,
                label="Settings",
            ),
        ],
    )


# Re-export indices for callers
__all__ = [
    "build_navigation_bar",
    "TAB_HOME",
    "TAB_DOWNLOADING",
    "TAB_COMPLETED",
    "TAB_SETTINGS",
]
