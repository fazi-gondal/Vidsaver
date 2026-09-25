# -*- coding: utf-8 -*-
"""
Flet File Picker as Service Example
Demonstrates the FilePicker service usage in Flet 1.0+

Target version: Flet >= 0.83.0 (Flet 1.0+)

Breaking changes:
  - ❌ Flet 0.x: page.add(FilePicker())  →  Flet 1.0+: no longer works
  - ✅ Flet 1.0+: FilePicker must be registered to page.services: page.services.append(file_picker)
  - ✅ Flet 1.0+: Use ft.run(main) to start (not ft.app)
  - ✅ Flet 1.0+: Event handlers must use async def + await asyncio.sleep()
"""

import flet as ft
import asyncio


def main(page: ft.Page):
    """File picker example main function"""
    page.title = "File Picker Example"
    page.window.width = 600
    page.window.height = 400
    page.padding = 30

    # Result display area
    selected_files_text = ft.Text(
        value="No files selected yet",
        size=16,
        color=ft.Colors.GREY_600,
    )

    # ✅ Create FilePicker and add to page.services (Flet 1.0+ new approach)
    file_picker = ft.FilePicker()
    page.services.append(file_picker)

    # Async file selection function
    async def pick_files(e):
        """Select files"""
        try:
            # ✅ pick_files() directly returns list[FilePickerFile], not result.files
            files = await file_picker.pick_files(
                allow_multiple=True,
                file_type=ft.FilePickerFileType.ANY,
            )

            if files:
                file_names = [f.name for f in files]
                selected_files_text.value = f"Selected {len(file_names)} file(s):\n" + "\n".join(file_names)
                selected_files_text.color = ft.Colors.GREEN
            else:
                selected_files_text.value = "No files selected"
                selected_files_text.color = ft.Colors.GREY_600

            page.update()
        except Exception as ex:
            selected_files_text.value = f"Error selecting files: {str(ex)}"
            selected_files_text.color = ft.Colors.RED
            page.update()

    async def pick_images(e):
        """Select images"""
        try:
            # ✅ pick_files() directly returns list[FilePickerFile]
            files = await file_picker.pick_files(
                allow_multiple=False,
                file_type=ft.FilePickerFileType.IMAGE,
                dialog_title="Select Image",
            )

            if files:
                file = files[0]
                selected_files_text.value = f"Selected image: {file.name}\nPath: {file.path}"
                selected_files_text.color = ft.Colors.BLUE
            else:
                selected_files_text.value = "No image selected"
                selected_files_text.color = ft.Colors.GREY_600

            page.update()
        except Exception as ex:
            selected_files_text.value = f"Error selecting image: {str(ex)}"
            selected_files_text.color = ft.Colors.RED
            page.update()

    async def save_file(e):
        """Save file"""
        try:
            # ✅ save_file() directly returns str | None (path string)
            path = await file_picker.save_file(
                file_name="my_document.txt",
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["txt", "md", "py"],
            )

            if path:
                selected_files_text.value = f"Saved to: {path}"
                selected_files_text.color = ft.Colors.GREEN
            else:
                selected_files_text.value = "Save cancelled"
                selected_files_text.color = ft.Colors.GREY_600

            page.update()
        except Exception as ex:
            selected_files_text.value = f"Error saving file: {str(ex)}"
            selected_files_text.color = ft.Colors.RED
            page.update()

    async def get_directory(e):
        """Select directory"""
        try:
            # ✅ get_directory_path() directly returns str | None (path string)
            path = await file_picker.get_directory_path(
                dialog_title="Select Folder",
            )

            if path:
                selected_files_text.value = f"Selected directory: {path}"
                selected_files_text.color = ft.Colors.BLUE
            else:
                selected_files_text.value = "No directory selected"
                selected_files_text.color = ft.Colors.GREY_600

            page.update()
        except Exception as ex:
            selected_files_text.value = f"Error selecting directory: {str(ex)}"
            selected_files_text.color = ft.Colors.RED
            page.update()

    # Buttons
    buttons = ft.Row(
        [
            ft.Button(
                content=ft.Row(
                    [ft.Icon(ft.Icons.FILE_OPEN), ft.Text("Select Files")],
                    spacing=8,
                ),
                on_click=lambda e: asyncio.create_task(pick_files(e)),
            ),
            ft.Button(
                content=ft.Row(
                    [ft.Icon(ft.Icons.IMAGE), ft.Text("Select Image")],
                    spacing=8,
                ),
                on_click=lambda e: asyncio.create_task(pick_images(e)),
            ),
            ft.Button(
                content=ft.Row(
                    [ft.Icon(ft.Icons.SAVE), ft.Text("Save File")],
                    spacing=8,
                ),
                on_click=lambda e: asyncio.create_task(save_file(e)),
            ),
            ft.Button(
                content=ft.Row(
                    [ft.Icon(ft.Icons.FOLDER_OPEN), ft.Text("Select Directory")],
                    spacing=8,
                ),
                on_click=lambda e: asyncio.create_task(get_directory(e)),
            ),
        ],
        wrap=True,
        spacing=10,
    )

    # Page layout
    page.add(
        ft.Column(
            [
                ft.Text(
                    "File Picker Service Example",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(
                    "Flet 1.0+ FilePicker used as a service",
                    size=14,
                    color=ft.Colors.GREY_600,
                ),
                ft.Divider(),
                buttons,
                ft.Divider(),
                ft.Text("Selection Result:", weight=ft.FontWeight.BOLD),
                selected_files_text,
            ],
            spacing=15,
        )
    )


if __name__ == "__main__":
    ft.run(main)
