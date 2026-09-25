# -*- coding: utf-8 -*-
"""
Flet Form Validation Example
Demonstrates form input, validation, and submission

Target version: Flet >= 0.83.0 (Flet 1.0+)

Breaking changes:
  - ❌ Flet 0.x: ft.app(target=main)  →  Flet 1.0+: raises error
  - ✅ Flet 1.0+: Use ft.run(main) to start
  - ✅ Flet 1.0+: All colors use ft.Colors.XXX (uppercase C)
"""

import flet as ft
import re


def main(page: ft.Page):
    """Form application main function"""
    page.title = "User Registration Form"
    page.window.width = 500
    page.window.height = 600
    page.padding = 30

    # Form controls
    name_field = ft.TextField(
        label="Name",
        hint_text="Enter your name",
        width=400,
        prefix_icon=ft.Icons.PERSON,
    )

    email_field = ft.TextField(
        label="Email",
        hint_text="Enter a valid email address",
        width=400,
        prefix_icon=ft.Icons.EMAIL,
    )

    password_field = ft.TextField(
        label="Password",
        hint_text="At least 8 characters, including letters and numbers",
        width=400,
        prefix_icon=ft.Icons.LOCK,
        password=True,
        can_reveal_password=True,
    )

    confirm_password_field = ft.TextField(
        label="Confirm Password",
        hint_text="Re-enter your password",
        width=400,
        prefix_icon=ft.Icons.LOCK_OUTLINE,
        password=True,
    )

    # Error message
    error_text = ft.Text(
        color=ft.Colors.RED,
        size=14,
        weight=ft.FontWeight.W_500,
    )

    # Success message
    success_text = ft.Text(
        color=ft.Colors.GREEN,
        size=14,
        weight=ft.FontWeight.W_500,
    )

    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def validate_password(password: str) -> bool:
        """Validate password strength"""
        if len(password) < 8:
            return False
        has_letter = any(c.isalpha() for c in password)
        has_number = any(c.isdigit() for c in password)
        return has_letter and has_number

    def validate_and_submit(e):
        """Validate form and submit"""
        errors = []

        # Validate name
        if not name_field.value or not name_field.value.strip():
            errors.append("• Name cannot be empty")

        # Validate email
        if not email_field.value:
            errors.append("• Email cannot be empty")
        elif not validate_email(email_field.value):
            errors.append("• Please enter a valid email address")

        # Validate password
        if not password_field.value:
            errors.append("• Password cannot be empty")
        elif not validate_password(password_field.value):
            errors.append("• Password must be at least 8 characters with letters and numbers")

        # Validate confirm password
        if password_field.value != confirm_password_field.value:
            errors.append("• Passwords do not match")

        # Display results
        if errors:
            error_text.value = "\n".join(errors)
            success_text.value = ""
        else:
            error_text.value = ""
            success_text.value = "✓ Registration successful!"
            print(f"Registration info: {name_field.value}, {email_field.value}")

        page.update()

    def reset_form(e):
        """Reset the form"""
        name_field.value = ""
        email_field.value = ""
        password_field.value = ""
        confirm_password_field.value = ""
        error_text.value = ""
        success_text.value = ""
        page.update()

    # Buttons
    submit_button = ft.Button(
        content=ft.Row(
            [
                ft.Icon(ft.Icons.CHECK, size=18),
                ft.Text("Submit Registration"),
            ],
            spacing=8,
        ),
        width=400,
        height=45,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.BLUE,
        ),
        on_click=validate_and_submit,
    )

    reset_button = ft.Button(
        content=ft.Text("Reset"),
        width=400,
        height=45,
        on_click=reset_form,
    )

    # Assemble the form
    page.add(
        ft.Column(
            [
                ft.Text(
                    "User Registration",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_700,
                ),
                ft.Divider(),
                name_field,
                email_field,
                password_field,
                confirm_password_field,
                ft.Container(height=10),
                error_text,
                success_text,
                ft.Container(height=10),
                submit_button,
                reset_button,
            ],
            spacing=15,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )


if __name__ == "__main__":
    ft.run(main)
