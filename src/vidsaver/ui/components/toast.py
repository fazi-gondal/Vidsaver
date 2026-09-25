"""Simple floating snackbar helper compatible with Flet 1.0."""

from __future__ import annotations

import flet as ft


def show_toast(page: ft.Page, message: str, duration: int = 2500) -> None:
    snack = ft.SnackBar(
        content=ft.Text(message),
        duration=duration,
        behavior=ft.SnackBarBehavior.FLOATING,
        margin=ft.Margin(left=16, top=0, right=16, bottom=10),
    )
    page.show_dialog(snack)
