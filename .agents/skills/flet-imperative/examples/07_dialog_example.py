# -*- coding: utf-8 -*-
"""
Flet Dialog Example
Demonstrates the new dialog display methods in Flet 1.0+

Target version: Flet >= 0.83.0 (Flet 1.0+)

Breaking changes:
  - ❌ Flet 0.x: page.bottom_sheet = xxx  →  Flet 1.0+: removed (page has no such attribute)
  - ❌ Flet 0.x: page.snack_bar = xxx      →  Flet 1.0+: removed
  - ✅ Flet 1.0+: Must use page.overlay.append(control) and set open=True to display
  - ✅ Flet 1.0+: Use ft.run(main) to start (not ft.app)
"""

import flet as ft


def main(page: ft.Page):
    """Dialog example main function"""
    page.title = "Dialog Example"
    page.window.width = 700
    page.window.height = 600
    page.padding = 30

    # Result display
    result_text = ft.Text(
        value="Click a button to show a dialog",
        size=16,
        color=ft.Colors.GREY_600,
    )

    # ===== Example 1: Simple Alert Dialog =====
    def show_alert_dialog(e):
        """Show an alert dialog"""

        def close_dialog(e):
            # ✅ Flet 1.0+ uses pop_dialog() to close
            page.pop_dialog()

        alert_dialog = ft.AlertDialog(
            title=ft.Text("Notice"),
            content=ft.Text("This is a simple alert dialog."),
            actions=[
                ft.Button(
                    content=ft.Text("OK"),
                    on_click=close_dialog,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        # ✅ Flet 1.0+ uses show_dialog() to display
        page.show_dialog(alert_dialog)
        result_text.value = "Showed alert dialog"
        result_text.color = ft.Colors.BLUE
        page.update()

    # ===== Example 2: Confirmation Dialog =====
    def show_confirm_dialog(e):
        """Show a confirmation dialog"""

        def handle_confirm(e):
            page.pop_dialog()
            result_text.value = "✓ User clicked Confirm"
            result_text.color = ft.Colors.GREEN
            page.update()

        def handle_cancel(e):
            page.pop_dialog()
            result_text.value = "✗ User clicked Cancel"
            result_text.color = ft.Colors.RED
            page.update()

        confirm_dialog = ft.AlertDialog(
            title=ft.Row(
                [
                    ft.Icon(ft.Icons.HELP_OUTLINE, color=ft.Colors.BLUE),
                    ft.Text("Confirm Action"),
                ]
            ),
            content=ft.Text("Are you sure you want to perform this action?"),
            actions=[
                ft.Button(
                    content=ft.Text("Cancel"),
                    on_click=handle_cancel,
                ),
                ft.Button(
                    content=ft.Text("Confirm"),
                    on_click=handle_confirm,
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.BLUE,
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        page.show_dialog(confirm_dialog)
        result_text.value = "Showed confirmation dialog"
        result_text.color = ft.Colors.BLUE
        page.update()

    # ===== Example 3: Input Dialog =====
    def show_input_dialog(e):
        """Show an input dialog"""

        input_field = ft.TextField(
            label="Enter content",
            hint_text="Type here...",
            autofocus=True,
        )

        def handle_submit(e):
            value = input_field.value
            page.pop_dialog()
            if value:
                result_text.value = f"✓ Input content: {value}"
                result_text.color = ft.Colors.GREEN
            else:
                result_text.value = "✗ No content entered"
                result_text.color = ft.Colors.ORANGE
            page.update()

        def handle_cancel(e):
            page.pop_dialog()
            result_text.value = "✗ Input cancelled"
            result_text.color = ft.Colors.RED
            page.update()

        input_dialog = ft.AlertDialog(
            title=ft.Text("Enter Information"),
            content=input_field,
            actions=[
                ft.Button(
                    content=ft.Text("Cancel"),
                    on_click=handle_cancel,
                ),
                ft.Button(
                    content=ft.Text("Submit"),
                    on_click=handle_submit,
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.BLUE,
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        page.show_dialog(input_dialog)
        result_text.value = "Showed input dialog"
        result_text.color = ft.Colors.BLUE
        page.update()

    # ===== Example 4: Bottom Sheet =====
    # Flet 1.0+ BottomSheet usage: add to page.overlay and set open=True
    def show_bottom_sheet(e):
        """Show a bottom sheet"""

        def handle_close(e):
            bottom_sheet.open = False
            page.update()

        def handle_option_selected(option: str):
            bottom_sheet.open = False
            result_text.value = f"✓ Selected: {option}"
            result_text.color = ft.Colors.GREEN
            page.update()

        bottom_sheet = ft.BottomSheet(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            "Choose Action",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Divider(),
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.SHARE),
                            title=ft.Text("Share"),
                            on_click=lambda e: handle_option_selected("Share"),
                        ),
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.COPY),
                            title=ft.Text("Copy"),
                            on_click=lambda e: handle_option_selected("Copy"),
                        ),
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.DELETE, color=ft.Colors.RED),
                            title=ft.Text("Delete", color=ft.Colors.RED),
                            on_click=lambda e: handle_option_selected("Delete"),
                        ),
                        ft.Divider(),
                        ft.Button(
                            content=ft.Text("Cancel"),
                            on_click=handle_close,
                            width=400,
                        ),
                    ],
                    tight=True,
                ),
                padding=20,
            ),
        )
        # ✅ Flet 1.0+ adds BottomSheet to page.overlay
        page.overlay.append(bottom_sheet)
        bottom_sheet.open = True
        page.update()
        result_text.value = "Showed bottom sheet"
        result_text.color = ft.Colors.BLUE
        page.update()

    # ===== Example 5: SnackBar Notification =====
    # Flet 1.0+ SnackBar usage: add to page.overlay and set open=True
    def show_snackbar(e):
        """Show a SnackBar"""
        snackbar = ft.SnackBar(
            content=ft.Text("This is a SnackBar notification!"),
            action=ft.SnackBarAction(
                label="Undo",
                on_click=lambda e: print("Undo action"),
            ),
            bgcolor=ft.Colors.GREY_800,
        )
        # ✅ Flet 1.0+ adds SnackBar to page.overlay
        page.overlay.append(snackbar)
        snackbar.open = True
        page.update()
        result_text.value = "Showed SnackBar"
        result_text.color = ft.Colors.BLUE
        page.update()

    # Button group
    buttons = ft.Row(
        [
            ft.Button(
                content=ft.Row(
                    [ft.Icon(ft.Icons.INFO), ft.Text("Alert Dialog")],
                    spacing=8,
                ),
                on_click=show_alert_dialog,
            ),
            ft.Button(
                content=ft.Row(
                    [ft.Icon(ft.Icons.HELP), ft.Text("Confirm Dialog")],
                    spacing=8,
                ),
                style=ft.ButtonStyle(
                    color=ft.Colors.WHITE,
                    bgcolor=ft.Colors.BLUE,
                ),
                on_click=show_confirm_dialog,
            ),
            ft.Button(
                content=ft.Row(
                    [ft.Icon(ft.Icons.EDIT), ft.Text("Input Dialog")],
                    spacing=8,
                ),
                style=ft.ButtonStyle(
                    color=ft.Colors.WHITE,
                    bgcolor=ft.Colors.GREEN,
                ),
                on_click=show_input_dialog,
            ),
            ft.Button(
                content=ft.Row(
                    [ft.Icon(ft.Icons.MENU), ft.Text("Bottom Sheet")],
                    spacing=8,
                ),
                style=ft.ButtonStyle(
                    color=ft.Colors.WHITE,
                    bgcolor=ft.Colors.PURPLE,
                ),
                on_click=show_bottom_sheet,
            ),
            ft.Button(
                content=ft.Row(
                    [ft.Icon(ft.Icons.NOTIFICATIONS), ft.Text("SnackBar")],
                    spacing=8,
                ),
                style=ft.ButtonStyle(
                    color=ft.Colors.WHITE,
                    bgcolor=ft.Colors.ORANGE,
                ),
                on_click=show_snackbar,
            ),
        ],
        wrap=True,
        spacing=10,
    )

    # Info box
    info_box = ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    "Flet 1.0+ Dialog/BottomSheet/SnackBar API Changes",
                    weight=ft.FontWeight.BOLD,
                    size=16,
                ),
                ft.Text("• AlertDialog show: page.show_dialog(dialog)"),
                ft.Text("• AlertDialog close: page.pop_dialog()"),
                ft.Text("• BottomSheet: page.overlay.append(sheet) + sheet.open = True"),
                ft.Text("• SnackBar: page.overlay.append(snackbar) + snackbar.open = True"),
                ft.Text("• No longer used: page.bottom_sheet / page.snack_bar properties"),
            ]
        ),
        bgcolor=ft.Colors.BLUE_50,
        padding=15,
        border_radius=8,
    )

    # Page layout
    page.add(
        ft.Column(
            [
                ft.Text(
                    "Dialog Example",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Divider(),
                info_box,
                ft.Divider(),
                buttons,
                ft.Divider(),
                ft.Text("Action Result:", weight=ft.FontWeight.BOLD),
                result_text,
            ],
            spacing=15,
        )
    )


if __name__ == "__main__":
    ft.run(main)
