# -*- coding: utf-8 -*-
"""
Flet File System Operations Example
Demonstrates file read/write, directory browsing and other features

Target version: Flet >= 0.83.0 (Flet 1.0+)

Breaking changes:
  - ❌ Flet 0.x: page.add(FilePicker())  →  Flet 1.0+: no longer works
  - ✅ Flet 1.0+: FilePicker must be registered via page.services.append(file_picker) before use
  - ✅ Flet 1.0+: use ft.run(main) to launch
  - ✅ Flet 1.0+: all async operations must use async def + await
"""

import flet as ft
import asyncio
import os


async def main(page: ft.Page):
    page.title = "File System Operations Example"
    page.window.width = 650
    page.window.height = 550

    # File picker
    file_picker = ft.FilePicker()
    page.services.append(file_picker)

    # Result display
    result_text = ft.TextField(
        label="Operation Result",
        multiline=True,
        min_lines=5,
        max_lines=10,
        read_only=True,
    )

    # File content display
    file_content = ft.TextField(
        label="File Content",
        multiline=True,
        min_lines=5,
        max_lines=10,
    )

    # Currently selected path
    current_path = ft.Text(value="No path selected", size=12, color=ft.Colors.GREY_500)

    async def pick_single_file(e):
        """Pick a single file"""
        files = await file_picker.pick_files(
            dialog_title="Select File",
            allowed_extensions=["txt", "py", "md", "json"],
            allow_multiple=False,
        )
        if files:
            current_path.value = files[0].path
            result_text.value = f"File name: {files[0].name}\nPath: {files[0].path}\nSize: {files[0].size} bytes"
        else:
            result_text.value = "No file selected"
        page.update()

    async def pick_multiple_files(e):
        """Pick multiple files"""
        files = await file_picker.pick_files(
            dialog_title="Select Multiple Files",
            allow_multiple=True,
        )
        if files:
            result_text.value = f"Selected {len(files)} files:\n"
            for f in files:
                result_text.value += f"  - {f.name} ({f.size} bytes)\n"
        else:
            result_text.value = "No files selected"
        page.update()

    async def pick_directory(e):
        """Pick a directory"""
        dir_path = await file_picker.get_directory_path(
            dialog_title="Select Directory",
        )
        if dir_path:
            current_path.value = dir_path
            # List directory contents
            try:
                items = os.listdir(dir_path)
                result_text.value = f"Directory: {dir_path}\n\nContents ({len(items)} items):\n"
                for item in items[:20]:  # Show at most 20 items
                    full_path = os.path.join(dir_path, item)
                    if os.path.isdir(full_path):
                        result_text.value += f"  📁 {item}/\n"
                    else:
                        result_text.value += f"  📄 {item}\n"
                if len(items) > 20:
                    result_text.value += f"  ... and {len(items) - 20} more items"
            except Exception as ex:
                result_text.value = f"Cannot read directory: {ex}"
        else:
            result_text.value = "No directory selected"
        page.update()

    async def save_file(e):
        """Save file"""
        save_path = await file_picker.save_file(
            dialog_title="Save File",
            file_name="new_file.txt",
            allowed_extensions=["txt"],
        )
        if save_path:
            current_path.value = save_path
            try:
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(file_content.value or "# New File\n")
                result_text.value = f"File saved to:\n{save_path}"
            except Exception as ex:
                result_text.value = f"Save failed: {ex}"
        else:
            result_text.value = "Save cancelled"
        page.update()

    async def read_file(e):
        """Read the file at current path"""
        path = current_path.value
        if path and path != "No path selected":
            try:
                with open(path, "r", encoding="utf-8") as f:
                    file_content.value = f.read()
                result_text.value = f"File read: {path}"
            except Exception as ex:
                result_text.value = f"Read failed: {ex}"
        else:
            result_text.value = "Please select a file first"
        page.update()

    page.add(
        ft.Text("File System Operations Example", size=24, weight=ft.FontWeight.BOLD),
        ft.Divider(),

        ft.Text("File Selection:", weight=ft.FontWeight.W_500),
        ft.Row([
            ft.Button(
                content=ft.Row([
                    ft.Icon(ft.Icons.INSERT_DRIVE_FILE, size=18),
                    ft.Text("Select File"),
                ]),
                on_click=pick_single_file,
            ),
            ft.Button(
                content=ft.Row([
                    ft.Icon(ft.Icons.FOLDER_OPEN, size=18),
                    ft.Text("Select Directory"),
                ]),
                on_click=pick_directory,
            ),
            ft.Button(
                content=ft.Row([
                    ft.Icon(ft.Icons.LIBRARY_ADD, size=18),
                    ft.Text("Select Multiple"),
                ]),
                on_click=pick_multiple_files,
            ),
        ]),

        ft.Divider(),
        current_path,

        ft.Row([
            ft.Column([
                ft.Text("Operation Result:", weight=ft.FontWeight.W_500),
                ft.Container(
                    content=result_text,
                    width=280,
                ),
            ]),
            ft.VerticalDivider(),
            ft.Column([
                ft.Text("File Content:", weight=ft.FontWeight.W_500),
                file_content,
                ft.Row([
                    ft.Button(
                        content=ft.Text("Read File"),
                        on_click=read_file,
                    ),
                    ft.Button(
                        content=ft.Row([
                            ft.Icon(ft.Icons.SAVE, size=18),
                            ft.Text("Save File"),
                        ]),
                        style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE),
                        on_click=save_file,
                    ),
                ]),
            ], expand=True),
        ], expand=True),

        ft.Divider(),
        ft.Text("Note: FilePicker must be added to page.services",
                size=12, color=ft.Colors.GREY_500),
    )


ft.run(main)
