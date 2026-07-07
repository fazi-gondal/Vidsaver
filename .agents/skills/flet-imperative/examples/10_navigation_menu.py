# -*- coding: utf-8 -*-
"""
Flet Navigation Menu Example
Demonstrates NavigationRail, NavigationDrawer, AppBar, and other navigation controls

Target version: Flet >= 0.83.0 (Flet 1.0+)

Breaking changes:
  - ❌ Flet 0.x: ft.Tabs(tabs=[ft.Tab(text=..., content=...)])  →  Flet 1.0+: raises "unexpected keyword argument 'tabs'"
  - ❌ Flet 0.x: ft.Tab(content=...)  →  Flet 1.0+: raises "unexpected keyword argument 'content'"
  - ✅ Flet 1.0+: Use ft.Tabs(content=..., length=N) + ft.TabBar(tabs=[...]) + ft.TabBarView(controls=[...])
  - ✅ Flet 1.0+: TabBarView must have height set directly (e.g. height=120)
  - ❌ Flet 0.x: NavigationDrawer has position property  →  Flet 1.0+: removed
  - ✅ Flet 1.0+: Must use page.drawer = drawer to set (cannot use page.overlay.append)
  - ❌ Flet 0.x / incorrect usage: page.drawer.open = True  →  Flet 1.0+: 'NavigationDrawer' object has no attribute 'open'
  - ✅ Flet 1.0+: Use await page.show_drawer() / await page.close_drawer() to control open/close
  - ✅ Flet 1.0+: Use page.end_drawer for right-side drawer
  - ❌ Flet 0.x: ft.PopupMenuItem(text="...")  →  Flet 1.0+: raises "unexpected keyword argument 'text'"
  - ✅ Flet 1.0+: Use ft.PopupMenuItem(content=ft.Text("..."))

Feature description:
  - Click the menu button at the top-left: collapse/expand the left NavigationRail sidebar
  - NavigationRail.extended property controls whether label text is shown
"""

import flet as ft
import asyncio


def main(page: ft.Page):
    """Navigation menu example main function"""
    page.title = "Navigation Menu Example"
    page.window.width = 900
    page.window.height = 650

    # Currently selected page index
    selected_index = [0]

    # ===== Page Content =====
    def get_page_content(index: int) -> ft.Control:
        """Get page content by index"""
        contents = [
            # Home
            ft.Column([
                ft.Icon(ft.Icons.HOME, size=60, color=ft.Colors.BLUE),
                ft.Text("Home", size=24, weight=ft.FontWeight.BOLD),
                ft.Text("Welcome to the home page", color=ft.Colors.GREY_600),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),

            # Search
            ft.Column([
                ft.Icon(ft.Icons.SEARCH, size=60, color=ft.Colors.GREEN),
                ft.Text("Search", size=24, weight=ft.FontWeight.BOLD),
                ft.TextField(
                    label="Search",
                    hint_text="Enter search keywords",
                    width=300,
                    prefix_icon=ft.Icons.SEARCH,
                ),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),

            # Favorites
            ft.Column([
                ft.Icon(ft.Icons.FAVORITE, size=60, color=ft.Colors.RED),
                ft.Text("Favorites", size=24, weight=ft.FontWeight.BOLD),
                ft.Text("Your favorited content will appear here", color=ft.Colors.GREY_600),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),

            # Settings
            ft.Column([
                ft.Icon(ft.Icons.SETTINGS, size=60, color=ft.Colors.PURPLE),
                ft.Text("Settings", size=24, weight=ft.FontWeight.BOLD),
                ft.Switch(label="Dark Mode"),
                ft.Switch(label="Notifications"),
                ft.Switch(label="Auto Update"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
        ]
        return contents[index] if index < len(contents) else contents[0]

    # ===== AppBar Top Navigation Bar =====
    page.appbar = ft.AppBar(
        leading=ft.IconButton(
            icon=ft.Icons.MENU,
            tooltip="Collapse/Expand Sidebar",
            on_click=lambda e: toggle_rail(),  # ✅ Toggle NavigationRail collapse/expand
        ),
        leading_width=40,
        title=ft.Text("Navigation Menu Example", weight=ft.FontWeight.BOLD),
        center_title=False,
        bgcolor=ft.Colors.BLUE_700,
        color=ft.Colors.WHITE,
        actions=[
            ft.IconButton(icon=ft.Icons.SEARCH, tooltip="Search"),
            ft.IconButton(icon=ft.Icons.NOTIFICATIONS, tooltip="Notifications"),
            ft.PopupMenuButton(
                items=[
                    ft.PopupMenuItem(content=ft.Text("Profile")),  # ✅ Flet 1.0+: use content, not text
                    ft.PopupMenuItem(content=ft.Text("Account Settings")),
                    ft.PopupMenuItem(),  # Separator
                    ft.PopupMenuItem(content=ft.Text("Sign Out")),
                ],
                icon=ft.Icons.MORE_VERT,
            ),
        ],
    )

    # ===== NavigationDrawer Side Drawer =====
    # ✅ Flet 1.0+: NavigationDrawer must be set via page.drawer (not overlay)
    drawer = ft.NavigationDrawer(
        controls=[
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.ACCOUNT_CIRCLE, size=60, color=ft.Colors.BLUE),
                    ft.Text("Username", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text("user@example.com", color=ft.Colors.GREY_600, size=12),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=20,
                bgcolor=ft.Colors.BLUE_50,
            ),
            ft.Divider(),
            ft.NavigationDrawerDestination(
                icon=ft.Icons.HOME_OUTLINED,
                selected_icon=ft.Icons.HOME,
                label="Home",
            ),
            ft.NavigationDrawerDestination(
                icon=ft.Icons.SEARCH_OUTLINED,
                selected_icon=ft.Icons.SEARCH,
                label="Search",
            ),
            ft.NavigationDrawerDestination(
                icon=ft.Icons.FAVORITE_BORDER,
                selected_icon=ft.Icons.FAVORITE,
                label="Favorites",
            ),
            ft.Divider(),
            ft.NavigationDrawerDestination(
                icon=ft.Icons.SETTINGS_OUTLINED,
                selected_icon=ft.Icons.SETTINGS,
                label="Settings",
            ),
            ft.NavigationDrawerDestination(
                icon=ft.Icons.HELP_OUTLINE,
                selected_icon=ft.Icons.HELP,
                label="Help",
            ),
        ],
        on_change=lambda e: on_drawer_change(e),
    )

    # Set to page.drawer (must use page.drawer to control the open property)
    page.drawer = drawer

    def toggle_rail():
        """Toggle NavigationRail collapse/expand"""
        # ✅ Toggle extended property to collapse/expand
        rail.extended = not rail.extended
        rail.update()

    async def on_drawer_change(e):
        """Drawer navigation change"""
        selected_index[0] = e.control.selected_index
        content_container.content = get_page_content(selected_index[0])
        await page.close_drawer()  # ✅ Flet 1.0+: use await page.close_drawer()

    # ===== NavigationRail Side Navigation Bar =====
    # ✅ Supports extended property to control collapse/expand
    rail = ft.NavigationRail(
        selected_index=0,
        extended=True,  # Initially expanded
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=56,
        min_extended_width=150,
        leading=ft.FloatingActionButton(
            content=ft.Icon(ft.Icons.ADD),
            on_click=lambda e: print("Add button clicked"),
        ),
        trailing=ft.IconButton(
            icon=ft.Icons.SETTINGS_OUTLINED,
            on_click=lambda e: print("Settings clicked"),
        ),
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icons.HOME_OUTLINED,
                selected_icon=ft.Icons.HOME,
                label="Home",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.SEARCH_OUTLINED,
                selected_icon=ft.Icons.SEARCH,
                label="Search",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.FAVORITE_BORDER,
                selected_icon=ft.Icons.FAVORITE,
                label="Favorites",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.SETTINGS_OUTLINED,
                selected_icon=ft.Icons.SETTINGS,
                label="Settings",
            ),
        ],
        on_change=lambda e: on_rail_change(e),
    )

    def on_rail_change(e):
        """Rail navigation change"""
        selected_index[0] = e.control.selected_index
        content_container.content = get_page_content(selected_index[0])
        page.update()

    # ===== Bottom Navigation Bar =====
    bottom_nav = ft.NavigationBar(
        selected_index=0,
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icons.HOME_OUTLINED,
                selected_icon=ft.Icons.HOME,
                label="Home",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.SEARCH_OUTLINED,
                selected_icon=ft.Icons.SEARCH,
                label="Search",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.FAVORITE_BORDER,
                selected_icon=ft.Icons.FAVORITE,
                label="Favorites",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.SETTINGS_OUTLINED,
                selected_icon=ft.Icons.SETTINGS,
                label="Settings",
            ),
        ],
        on_change=lambda e: on_bottom_nav_change(e),
    )

    def on_bottom_nav_change(e):
        """Bottom navigation change"""
        selected_index[0] = e.control.selected_index
        content_container.content = get_page_content(selected_index[0])
        rail.selected_index = selected_index[0]
        page.update()

    # ===== Content Area =====
    content_container = ft.Container(
        content=get_page_content(0),
        expand=True,
        alignment=ft.Alignment.CENTER,
    )

    # ===== Tabs Navigation =====
    def create_tabs_section():
        """Tabs navigation (Flet 1.0+ new API)"""
        return ft.Column([
            ft.Text("Tabs Navigation", size=16, weight=ft.FontWeight.BOLD),
            ft.Tabs(
                content=ft.Column([
                    ft.TabBar(
                        tabs=[
                            ft.Tab(
                                label=ft.Row([
                                    ft.Icon(ft.Icons.INFO, size=16),
                                    ft.Text("Info"),
                                ], spacing=5),
                            ),
                            ft.Tab(
                                label=ft.Row([
                                    ft.Icon(ft.Icons.LIST, size=16),
                                    ft.Text("List"),
                                ], spacing=5),
                            ),
                            ft.Tab(
                                label=ft.Row([
                                    ft.Icon(ft.Icons.SETTINGS, size=16),
                                    ft.Text("Settings"),
                                ], spacing=5),
                            ),
                        ],
                    ),
                    ft.TabBarView(
                        height=120,  # ✅ Flet 1.0+: must set a fixed height
                        controls=[
                            ft.Container(
                                content=ft.Text("Info tab content", color=ft.Colors.GREY_700),
                                padding=20,
                            ),
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("List Item 1"),
                                    ft.Text("List Item 2"),
                                    ft.Text("List Item 3"),
                                ]),
                                padding=20,
                            ),
                            ft.Container(
                                content=ft.Text("Settings tab content", color=ft.Colors.GREY_700),
                                padding=20,
                            ),
                        ],
                    ),
                ]),
                length=3,
                selected_index=0,
                width=400,
            ),
        ])

    # ===== Usage Instructions =====
    def create_info_section():
        """Usage instructions"""
        return ft.Container(
            content=ft.Column([
                ft.Text("Navigation Controls Usage Guide", size=16, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Markdown("""
**AppBar** - Top Navigation Bar
- Set using the `page.appbar` property
- Supports title, icon buttons, menus, etc.

**NavigationRail** - Side Navigation Bar
- Suitable for desktop side navigation
- Supports collapse/expand mode

**NavigationBar** - Bottom Navigation Bar
- Suitable for mobile bottom navigation
- Up to 5 destinations

**NavigationDrawer** - Side Drawer
- ✅ **Flet 1.0+ change**: Use `page.overlay.append(drawer)` instead of `page.drawer`
- Supports left or right drawer

**Tabs** - Tab Navigation
- ✅ **Flet 1.0+ change**: Use `label` instead of `text` and `tab_content`
                """, selectable=True),
            ]),
            bgcolor=ft.Colors.BLUE_50,
            padding=15,
            border_radius=10,
            width=400,
        )

    # ===== Main Layout =====
    page.add(
        ft.Row([
            rail,
            ft.VerticalDivider(width=1),
            ft.Column([
                content_container,
                ft.Divider(),
                ft.Row([
                    create_tabs_section(),
                    create_info_section(),
                ], spacing=20),
            ], expand=True, scroll=ft.ScrollMode.AUTO),
        ], expand=True)
    )

    # Set bottom navigation (optional, commented out to avoid conflict with rail)
    # page.bottom_navigation_bar = bottom_nav


if __name__ == "__main__":
    ft.run(main)
