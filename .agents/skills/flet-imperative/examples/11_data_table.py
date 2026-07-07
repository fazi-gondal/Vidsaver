# -*- coding: utf-8 -*-
"""
Flet Data Table Example
Demonstrates data display controls including DataTable, ListView, and GridView

Target version: Flet >= 0.83.0 (Flet 1.0+)

Breaking changes:
  - ❌ Flet 0.x: list_view.scroll_to(key="item_1")  →  Flet 1.0+: parameter renamed to scroll_key
  - ✅ Flet 1.0+: use list_view.scroll_to(scroll_key="item_1")
  - ✅ Flet 1.0+: use ft.run(main) to launch
"""

import flet as ft


def main(page: ft.Page):
    """Data table example main function"""
    page.title = "Data Table Example"
    page.window.width = 900
    page.window.height = 700
    page.padding = 20

    # ===== 1. DataTable =====
    def create_datatable_section():
        """Data table"""
        return ft.Column([
            ft.Text("1. DataTable", size=18, weight=ft.FontWeight.BOLD),
            ft.Divider(),

            ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("ID", weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Name", weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Age", weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("City", weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Actions", weight=ft.FontWeight.BOLD)),
                ],
                rows=[
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text("001")),
                            ft.DataCell(ft.Text("Alice")),
                            ft.DataCell(ft.Text("25")),
                            ft.DataCell(ft.Text("Beijing")),
                            ft.DataCell(
                                ft.Row([
                                    ft.IconButton(icon=ft.Icons.EDIT, icon_size=18, tooltip="Edit"),
                                    ft.IconButton(icon=ft.Icons.DELETE, icon_size=18, tooltip="Delete", icon_color=ft.Colors.RED),
                                ], spacing=0)
                            ),
                        ],
                    ),
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text("002")),
                            ft.DataCell(ft.Text("Bob")),
                            ft.DataCell(ft.Text("30")),
                            ft.DataCell(ft.Text("Shanghai")),
                            ft.DataCell(
                                ft.Row([
                                    ft.IconButton(icon=ft.Icons.EDIT, icon_size=18, tooltip="Edit"),
                                    ft.IconButton(icon=ft.Icons.DELETE, icon_size=18, tooltip="Delete", icon_color=ft.Colors.RED),
                                ], spacing=0)
                            ),
                        ],
                    ),
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text("003")),
                            ft.DataCell(ft.Text("Charlie")),
                            ft.DataCell(ft.Text("28")),
                            ft.DataCell(ft.Text("Guangzhou")),
                            ft.DataCell(
                                ft.Row([
                                    ft.IconButton(icon=ft.Icons.EDIT, icon_size=18, tooltip="Edit"),
                                    ft.IconButton(icon=ft.Icons.DELETE, icon_size=18, tooltip="Delete", icon_color=ft.Colors.RED),
                                ], spacing=0)
                            ),
                        ],
                    ),
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text("004")),
                            ft.DataCell(ft.Text("Diana")),
                            ft.DataCell(ft.Text("35")),
                            ft.DataCell(ft.Text("Shenzhen")),
                            ft.DataCell(
                                ft.Row([
                                    ft.IconButton(icon=ft.Icons.EDIT, icon_size=18, tooltip="Edit"),
                                    ft.IconButton(icon=ft.Icons.DELETE, icon_size=18, tooltip="Delete", icon_color=ft.Colors.RED),
                                ], spacing=0)
                            ),
                        ],
                    ),
                ],
                border=ft.Border.all(1, ft.Colors.GREY_300),
                border_radius=10,
                vertical_lines=ft.BorderSide(1, ft.Colors.GREY_200),
                horizontal_lines=ft.BorderSide(1, ft.Colors.GREY_200),
                heading_row_color=ft.Colors.GREY_100,
                heading_row_height=50,
                data_row_min_height=45,
                data_row_max_height=60,
            ),
        ])

    # ===== 2. ListView =====
    list_view = ft.ListView(
        spacing=5,
        padding=10,
        item_extent=60,  # Fixed item height for better performance
        height=250,
        width=400,
    )

    # Add initial data
    for i in range(50):
        list_view.controls.append(
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.PERSON, color=ft.Colors.BLUE),
                    ft.Text(f"User {i + 1}"),
                    ft.Icon(ft.Icons.CHEVRON_RIGHT, color=ft.Colors.GREY_400, size=16),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=10,
                bgcolor=ft.Colors.GREY_50,
                border_radius=5,
                on_click=lambda e, idx=i: print(f"Clicked User {idx + 1}"),
            )
        )

    def create_listview_section():
        """ListView list"""
        return ft.Column([
            ft.Text("2. ListView (Virtual Scrolling)", size=18, weight=ft.FontWeight.BOLD),
            ft.Divider(),

            ft.Text("Suitable for long lists, supports virtual scrolling for better performance", color=ft.Colors.GREY_600, size=12),

            ft.Row([
                list_view,
                ft.Column([
                    ft.Button(
                        content=ft.Row([ft.Icon(ft.Icons.ARROW_UPWARD), ft.Text("Scroll to Top")]),
                        on_click=lambda e: scroll_to_top(),
                    ),
                    ft.Button(
                        content=ft.Row([ft.Icon(ft.Icons.ARROW_DOWNWARD), ft.Text("Scroll to Bottom")]),
                        on_click=lambda e: scroll_to_bottom(),
                    ),
                ], spacing=10),
            ]),
        ])

    def scroll_to_top():
        """Scroll to top"""
        # ✅ Flet 1.0+ uses scroll_key parameter
        list_view.scroll_to(offset=0, duration=500)
        page.update()

    def scroll_to_bottom():
        """Scroll to bottom"""
        list_view.scroll_to(offset=-1, duration=500)
        page.update()

    # ===== 3. GridView =====
    def create_gridview_section():
        """GridView grid"""
        return ft.Column([
            ft.Text("3. GridView", size=18, weight=ft.FontWeight.BOLD),
            ft.Divider(),

            ft.GridView(
                [
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.Icons.IMAGE, size=40, color=ft.Colors.GREY_400),
                            ft.Text(f"Image {i + 1}", size=12),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                        bgcolor=ft.Colors.GREY_100,
                        border_radius=10,
                        alignment=ft.Alignment.CENTER,
                    )
                    for i in range(20)
                ],
                runs_count=4,
                max_extent=120,
                child_aspect_ratio=1.0,
                spacing=10,
                run_spacing=10,
                height=300,
                width=500,
            ),
        ])

    # ===== 4. ExpansionTile Expandable List =====
    def create_expansion_section():
        """Expandable list"""
        return ft.Column([
            ft.Text("4. ExpansionTile Expandable List", size=18, weight=ft.FontWeight.BOLD),
            ft.Divider(),

            ft.Column([
                ft.ExpansionTile(
                    title=ft.Text("Group 1: Basic Info"),
                    subtitle=ft.Text("Contains basic user profile"),
                    leading=ft.Icon(ft.Icons.INFO),
                    trailing=ft.Icon(ft.Icons.EXPAND_MORE),
                    controls=[
                        ft.ListTile(title=ft.Text("Name: Alice")),
                        ft.ListTile(title=ft.Text("Age: 25")),
                        ft.ListTile(title=ft.Text("City: Beijing")),
                    ],
                ),
                ft.ExpansionTile(
                    title=ft.Text("Group 2: Contact Info"),
                    subtitle=ft.Text("Contains contact details"),
                    leading=ft.Icon(ft.Icons.CONTACT_PHONE),
                    trailing=ft.Icon(ft.Icons.EXPAND_MORE),
                    controls=[
                        ft.ListTile(title=ft.Text("Phone: 138****1234")),
                        ft.ListTile(title=ft.Text("Email: test@example.com")),
                    ],
                ),
                ft.ExpansionTile(
                    title=ft.Text("Group 3: Settings"),
                    subtitle=ft.Text("Application settings"),
                    leading=ft.Icon(ft.Icons.SETTINGS),
                    trailing=ft.Icon(ft.Icons.EXPAND_MORE),
                    controls=[
                        ft.Switch(label="Notifications"),
                        ft.Switch(label="Auto Update"),
                        ft.Switch(label="Dark Mode"),
                    ],
                ),
            ], spacing=5),
        ])

    # ===== 5. Pagination Example =====
    current_page = [1]
    items_per_page = 5
    total_items = 47

    def get_page_items(page_num: int) -> list:
        """Get data for the specified page"""
        start = (page_num - 1) * items_per_page
        end = start + items_per_page
        return [f"Data Item {i + 1}" for i in range(start, min(end, total_items))]

    page_list = ft.Column(spacing=5)

    def update_page_list():
        """Update the page list"""
        page_list.controls.clear()
        for item in get_page_items(current_page[0]):
            page_list.controls.append(
                ft.Container(
                    content=ft.Text(item),
                    padding=10,
                    bgcolor=ft.Colors.GREY_50,
                    border_radius=5,
                )
            )
        page_info.value = f"Page {current_page[0]} / {(total_items + items_per_page - 1) // items_per_page}"
        page.update()

    def prev_page(e):
        """Previous page"""
        if current_page[0] > 1:
            current_page[0] -= 1
            update_page_list()

    def next_page(e):
        """Next page"""
        max_page = (total_items + items_per_page - 1) // items_per_page
        if current_page[0] < max_page:
            current_page[0] += 1
            update_page_list()

    page_info = ft.Text()

    def create_pagination_section():
        """Pagination example"""
        return ft.Column([
            ft.Text("5. Pagination Example", size=18, weight=ft.FontWeight.BOLD),
            ft.Divider(),

            ft.Container(
                content=page_list,
                height=200,
                width=300,
            ),

            ft.Row([
                ft.Button(
                    content=ft.Icon(ft.Icons.CHEVRON_LEFT),
                    on_click=prev_page,
                ),
                page_info,
                ft.Button(
                    content=ft.Icon(ft.Icons.CHEVRON_RIGHT),
                    on_click=next_page,
                ),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
        ])

    # ===== Initialize pagination =====
    update_page_list()

    # ===== Page layout =====
    page.add(
        ft.Column([
            ft.Text(
                "Data Table Example",
                size=28,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.BLUE_700,
            ),
            ft.Divider(),

            ft.Row([
                ft.Column([
                    create_datatable_section(),
                    ft.Divider(),
                    create_listview_section(),
                ], scroll=ft.ScrollMode.AUTO, expand=True),

                ft.VerticalDivider(),

                ft.Column([
                    create_gridview_section(),
                    ft.Divider(),
                    create_expansion_section(),
                    ft.Divider(),
                    create_pagination_section(),
                ], scroll=ft.ScrollMode.AUTO, expand=True),
            ], expand=True),
        ], expand=True)
    )


if __name__ == "__main__":
    ft.run(main)
