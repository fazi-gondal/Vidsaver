# -*- coding: utf-8 -*-
"""
Flet Local Storage Example - SharedPreferences
Demonstrates data persistence using shared_preferences in Flet 1.0+

Target version: Flet >= 0.83.0 (Flet 1.0+)

Breaking changes:
  - ❌ Flet 0.x: page.client_storage  →  Flet 1.0+: removed
  - ❌ Flet 0.x: page.shared_preferences  →  Flet 1.0+: removed
  - ✅ Flet 1.0+: Use ft.SharedPreferences() class, first page.services.append(prefs) then use it
  - ✅ Flet 1.0+: Use ft.run(main) to start
"""

import flet as ft
import asyncio


def main(page: ft.Page):
    """SharedPreferences example main function"""
    page.title = "Local Storage Example"
    page.window.width = 600
    page.window.height = 500
    page.padding = 30

    # ✅ Create SharedPreferences instance (Flet 1.0+ new approach)
    prefs = ft.SharedPreferences()
    page.services.append(prefs)

    # Status display
    status_text = ft.Text(
        value="Ready",
        size=14,
        color=ft.Colors.GREY_600,
    )

    # Input controls
    key_field = ft.TextField(
        label="Key",
        hint_text="Enter storage key",
        width=250,
    )

    value_field = ft.TextField(
        label="Value",
        hint_text="Enter storage value",
        width=250,
    )

    # Data type selector
    data_type = ft.Dropdown(
        label="Data Type",
        width=150,
        value="string",
        options=[
            ft.DropdownOption(key="string", text="String"),
            ft.DropdownOption(key="int", text="Integer"),
            ft.DropdownOption(key="float", text="Float"),
            ft.DropdownOption(key="bool", text="Boolean"),
            ft.DropdownOption(key="list", text="List (v0.82.2+)"),
        ],
    )

    # Stored data list
    stored_data = ft.Column(scroll=ft.ScrollMode.AUTO, height=150)

    async def refresh_data_list():
        """Refresh the stored data list"""
        try:
            # ✅ get_keys() requires a key_prefix argument; empty string gets all keys
            keys = await prefs.get_keys("")

            stored_data.controls.clear()

            if not keys:
                stored_data.controls.append(
                    ft.Text("No stored data", color=ft.Colors.GREY_500, italic=True)
                )
            else:
                for key in keys:
                    value = await prefs.get(key)
                    stored_data.controls.append(
                        ft.Row(
                            [
                                ft.Icon(ft.Icons.STORAGE, size=16, color=ft.Colors.BLUE),
                                ft.Text(f"{key}:", weight=ft.FontWeight.BOLD, width=100),
                                ft.Text(str(value), expand=True),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE,
                                    icon_size=18,
                                    tooltip="Delete",
                                    on_click=lambda e, k=key: asyncio.create_task(delete_key(k)),
                                ),
                            ],
                            spacing=10,
                        )
                    )

            page.update()
        except Exception as ex:
            status_text.value = f"Failed to refresh list: {str(ex)}"
            status_text.color = ft.Colors.RED
            page.update()

    async def save_value(e):
        """Save a value"""
        try:
            key = key_field.value.strip()
            value = value_field.value

            if not key:
                status_text.value = "Please enter a key"
                status_text.color = ft.Colors.RED
                page.update()
                return

            if not value:
                status_text.value = "Please enter a value"
                status_text.color = ft.Colors.RED
                page.update()
                return

            # Convert and save based on type (with input validation)
            data_type_val = data_type.value

            try:
                if data_type_val == "string":
                    await prefs.set(key, value)
                elif data_type_val == "int":
                    await prefs.set(key, int(value))
                elif data_type_val == "float":
                    await prefs.set(key, float(value))
                elif data_type_val == "bool":
                    await prefs.set(key, value.lower() in ("true", "1", "yes"))
                elif data_type_val == "list":
                    # v0.82.2+ supports string lists
                    # Input format: comma-separated, e.g. "a,b,c"
                    list_value = [item.strip() for item in value.split(",") if item.strip()]
                    await prefs.set(key, list_value)

                status_text.value = f"[OK] Saved: {key}"
                status_text.color = ft.Colors.GREEN

                # Clear inputs
                key_field.value = ""
                value_field.value = ""

                # Refresh list
                await refresh_data_list()

            except ValueError as ve:
                status_text.value = f"Type conversion failed: please enter a valid {data_type_val} value"
                status_text.color = ft.Colors.RED
                page.update()

        except Exception as ex:
            status_text.value = f"Save failed: {str(ex)}"
            status_text.color = ft.Colors.RED
            page.update()

    async def get_value(e):
        """Retrieve a value"""
        try:
            key = key_field.value.strip()

            if not key:
                status_text.value = "Please enter a key"
                status_text.color = ft.Colors.RED
                page.update()
                return

            value = await prefs.get(key)

            if value is not None:
                value_field.value = str(value)
                status_text.value = f"[OK] Retrieved: {key} = {value}"
                status_text.color = ft.Colors.GREEN
            else:
                status_text.value = f"Key '{key}' does not exist"
                status_text.color = ft.Colors.ORANGE

            page.update()

        except Exception as ex:
            status_text.value = f"Read failed: {str(ex)}"
            status_text.color = ft.Colors.RED
            page.update()

    async def delete_key(key: str):
        """Delete a specific key"""
        try:
            await prefs.remove(key)
            status_text.value = f"[OK] Deleted: {key}"
            status_text.color = ft.Colors.GREEN
            await refresh_data_list()
        except Exception as ex:
            status_text.value = f"Delete failed: {str(ex)}"
            status_text.color = ft.Colors.RED
            page.update()

    async def clear_all(e):
        """Clear all data"""
        try:
            await prefs.clear()
            status_text.value = "[OK] All data cleared"
            status_text.color = ft.Colors.GREEN
            await refresh_data_list()
        except Exception as ex:
            status_text.value = f"Clear failed: {str(ex)}"
            status_text.color = ft.Colors.RED
            page.update()

    # Page layout
    page.add(
        ft.Column(
            [
                ft.Text(
                    "SharedPreferences Local Storage",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(
                    "Persistent Data Storage Example",
                    size=14,
                    color=ft.Colors.GREY_600,
                ),
                ft.Divider(),

                # Input area
                ft.Row(
                    [key_field, value_field, data_type],
                    spacing=10,
                ),

                # Button area
                ft.Row(
                    [
                        ft.Button(
                            content=ft.Row(
                                [ft.Icon(ft.Icons.SAVE), ft.Text("Save")],
                                spacing=8,
                            ),
                            on_click=lambda e: asyncio.create_task(save_value(e)),
                        ),
                        ft.Button(
                            content=ft.Row(
                                [ft.Icon(ft.Icons.READ_MORE), ft.Text("Read")],
                                spacing=8,
                            ),
                            style=ft.ButtonStyle(
                                color=ft.Colors.WHITE,
                                bgcolor=ft.Colors.GREEN,
                            ),
                            on_click=lambda e: asyncio.create_task(get_value(e)),
                        ),
                        ft.Button(
                            content=ft.Row(
                                [ft.Icon(ft.Icons.REFRESH), ft.Text("Refresh List")],
                                spacing=8,
                            ),
                            style=ft.ButtonStyle(
                                color=ft.Colors.WHITE,
                                bgcolor=ft.Colors.BLUE,
                            ),
                            on_click=lambda e: asyncio.create_task(refresh_data_list()),
                        ),
                        ft.Button(
                            content=ft.Row(
                                [ft.Icon(ft.Icons.DELETE_FOREVER), ft.Text("Clear All")],
                                spacing=8,
                            ),
                            style=ft.ButtonStyle(
                                color=ft.Colors.RED,
                            ),
                            on_click=lambda e: asyncio.create_task(clear_all(e)),
                        ),
                    ],
                    wrap=True,
                    spacing=10,
                ),

                ft.Divider(),
                status_text,
                ft.Divider(),

                ft.Text("Stored Data:", weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=stored_data,
                    border=ft.Border.all(1, ft.Colors.GREY_300),
                    border_radius=8,
                    padding=10,
                    bgcolor=ft.Colors.GREY_50,
                ),
            ],
            spacing=15,
        )
    )

    # Refresh list on initialization
    asyncio.create_task(refresh_data_list())


if __name__ == "__main__":
    ft.run(main)
