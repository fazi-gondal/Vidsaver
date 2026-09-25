# -*- coding: utf-8 -*-
"""
Flet Layout and Responsiveness Example
Demonstrates Row, Column, Stack, expand, scroll, and other layout features

Target version: Flet >= 0.83.0 (Flet 1.0+)

Breaking changes:
  - ❌ Flet 0.x: ft.alignment.center  →  Flet 1.0+: raises "no attribute 'center'"
  - ✅ Flet 1.0+: Use ft.Alignment.CENTER (uppercase A)
  - ❌ Flet 0.x: ft.Badge(label_style=...) or ft.Badge(small=True)  →  Flet 1.0+: raises error
  - ✅ Flet 1.0+: Badge can only use ft.Badge(label="text")
  - ✅ Flet 1.0+: TabBarView must have height set, otherwise "height is unbounded"
"""

import flet as ft


def main(page: ft.Page):
    """Layout example main function"""
    page.title = "Layout and Responsiveness Example"
    page.window.width = 900
    page.window.height = 700
    page.padding = 20

    # ===== 1. Row and Column Layout =====
    def create_layout_section():
        """Basic row and column layout"""
        return ft.Column([
            ft.Text("1. Row and Column Layout", size=18, weight=ft.FontWeight.BOLD),
            ft.Divider(),

            # Row horizontal layout
            ft.Text("Row (Horizontal Layout):", weight=ft.FontWeight.W_500),
            ft.Row(
                [
                    ft.Container(
                        content=ft.Text("Item 1", color=ft.Colors.WHITE),
                        bgcolor=ft.Colors.BLUE,
                        padding=20,
                        border_radius=8,
                        alignment=ft.Alignment.CENTER,
                    ),
                    ft.Container(
                        content=ft.Text("Item 2", color=ft.Colors.WHITE),
                        bgcolor=ft.Colors.GREEN,
                        padding=20,
                        border_radius=8,
                        alignment=ft.Alignment.CENTER,
                    ),
                    ft.Container(
                        content=ft.Text("Item 3", color=ft.Colors.WHITE),
                        bgcolor=ft.Colors.ORANGE,
                        padding=20,
                        border_radius=8,
                        alignment=ft.Alignment.CENTER,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_AROUND,  # Main axis alignment
                vertical_alignment=ft.CrossAxisAlignment.CENTER,  # Cross axis alignment
                spacing=10,  # Spacing
            ),

            ft.Container(height=15),

            # Column vertical layout
            ft.Text("Column (Vertical Layout):", weight=ft.FontWeight.W_500),
            ft.Column(
                [
                    ft.Container(
                        content=ft.Text("Top", color=ft.Colors.WHITE),
                        bgcolor=ft.Colors.PURPLE,
                        padding=15,
                        border_radius=8,
                        alignment=ft.Alignment.CENTER,
                    ),
                    ft.Container(
                        content=ft.Text("Middle", color=ft.Colors.WHITE),
                        bgcolor=ft.Colors.PINK,
                        padding=15,
                        border_radius=8,
                        alignment=ft.Alignment.CENTER,
                    ),
                    ft.Container(
                        content=ft.Text("Bottom", color=ft.Colors.WHITE),
                        bgcolor=ft.Colors.CYAN,
                        padding=15,
                        border_radius=8,
                        alignment=ft.Alignment.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
                scroll=ft.ScrollMode.AUTO,  # Auto scroll
                height=150,
            ),
        ])

    # ===== 2. expand Adaptive Sizing =====
    def create_expand_section():
        """expand adaptive sizing"""
        return ft.Column([
            ft.Text("2. expand Adaptive Sizing", size=18, weight=ft.FontWeight.BOLD),
            ft.Divider(),

            ft.Text("Use expand=True to let controls fill available space:", color=ft.Colors.GREY_700),

            ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Text("expand=1", color=ft.Colors.WHITE),
                            bgcolor=ft.Colors.RED_400,
                            padding=20,
                            border_radius=8,
                            expand=1,  # Takes 1 share
                            alignment=ft.Alignment.CENTER,
                        ),
                        ft.Container(
                            content=ft.Text("expand=2", color=ft.Colors.WHITE),
                            bgcolor=ft.Colors.BLUE_400,
                            padding=20,
                            border_radius=8,
                            expand=2,  # Takes 2 shares
                            alignment=ft.Alignment.CENTER,
                        ),
                        ft.Container(
                            content=ft.Text("expand=1", color=ft.Colors.WHITE),
                            bgcolor=ft.Colors.GREEN_400,
                            padding=20,
                            border_radius=8,
                            expand=1,  # Takes 1 share
                            alignment=ft.Alignment.CENTER,
                        ),
                    ],
                    spacing=10,
                ),
                border=ft.Border.all(1, ft.Colors.GREY_300),
                border_radius=10,
                padding=10,
            ),

            ft.Container(height=10),

            ft.Text("Vertical expand:", color=ft.Colors.GREY_700),
            ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Container(
                                        content=ft.Text("Top", color=ft.Colors.WHITE),
                                        bgcolor=ft.Colors.INDIGO,
                                        padding=15,
                                        border_radius=8,
                                        alignment=ft.Alignment.CENTER,
                                    ),
                                    ft.Container(
                                        content=ft.Text("expand=True", color=ft.Colors.WHITE),
                                        bgcolor=ft.Colors.TEAL,
                                        padding=15,
                                        border_radius=8,
                                        alignment=ft.Alignment.CENTER,
                                        expand=True,  # Fill remaining space
                                    ),
                                ],
                                spacing=5,
                            ),
                            expand=1,
                        ),
                        ft.Container(
                            content=ft.Text("Fixed Width", color=ft.Colors.WHITE),
                            bgcolor=ft.Colors.AMBER,
                            padding=20,
                            border_radius=8,
                            alignment=ft.Alignment.CENTER,
                            width=120,
                        ),
                    ],
                    spacing=10,
                    expand=True,
                ),
                height=200,
                border=ft.Border.all(1, ft.Colors.GREY_300),
                border_radius=10,
                padding=10,
            ),
        ])

    # ===== 3. Stack Overlay Layout =====
    def create_stack_section():
        """Stack overlay layout"""
        return ft.Column([
            ft.Text("3. Stack Overlay Layout", size=18, weight=ft.FontWeight.BOLD),
            ft.Divider(),

            ft.Stack(
                [
                    # Bottom layer - background card
                    ft.Container(
                        width=300,
                        height=150,
                        bgcolor=ft.Colors.BLUE_100,
                        border_radius=15,
                    ),
                    # Middle layer - image
                    ft.Container(
                        content=ft.Icon(ft.Icons.PEOPLE, size=60, color=ft.Colors.BLUE_300),
                        left=20,
                        top=20,
                    ),
                    # Top layer - text
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Card Title", size=20, weight=ft.FontWeight.BOLD),
                            ft.Text("This is the card description text", color=ft.Colors.GREY_700),
                        ]),
                        left=100,
                        top=30,
                    ),
                    # Top-right badge (using Container + Text instead of Badge)
                    ft.Container(
                        content=ft.Text(
                            "New",
                            color=ft.Colors.WHITE,
                            size=12,
                            weight=ft.FontWeight.BOLD,
                        ),
                        bgcolor=ft.Colors.RED,
                        border_radius=10,
                        padding=ft.Padding(left=8, right=8, top=4, bottom=4),
                        right=10,
                        top=10,
                    ),
                ],
                width=300,
                height=150,
            ),
        ])

    # ===== 4. ResponsiveRow Responsive Layout =====
    def create_responsive_section():
        """ResponsiveRow responsive layout"""
        return ft.Column([
            ft.Text("4. ResponsiveRow Responsive Layout", size=18, weight=ft.FontWeight.BOLD),
            ft.Divider(),

            ft.Text(
                "Automatically adjusts columns based on screen width (resize the window to see the effect)",
                color=ft.Colors.GREY_700,
                size=12,
            ),

            ft.ResponsiveRow(
                [
                    ft.Container(
                        content=ft.Text("col={sm:6, md:4, lg:3}", color=ft.Colors.WHITE),
                        bgcolor=ft.Colors.BLUE,
                        padding=20,
                        border_radius=8,
                        col={"sm": 6, "md": 4, "lg": 3},  # Responsive column width
                    ),
                    ft.Container(
                        content=ft.Text("col={sm:6, md:4, lg:3}", color=ft.Colors.WHITE),
                        bgcolor=ft.Colors.GREEN,
                        padding=20,
                        border_radius=8,
                        col={"sm": 6, "md": 4, "lg": 3},
                    ),
                    ft.Container(
                        content=ft.Text("col={sm:6, md:4, lg:3}", color=ft.Colors.WHITE),
                        bgcolor=ft.Colors.ORANGE,
                        padding=20,
                        border_radius=8,
                        col={"sm": 6, "md": 4, "lg": 3},
                    ),
                    ft.Container(
                        content=ft.Text("col={sm:6, md:4, lg:3}", color=ft.Colors.WHITE),
                        bgcolor=ft.Colors.PURPLE,
                        padding=20,
                        border_radius=8,
                        col={"sm": 6, "md": 4, "lg": 3},
                    ),
                    ft.Container(
                        content=ft.Text("col=6 (fixed)", color=ft.Colors.WHITE),
                        bgcolor=ft.Colors.RED,
                        padding=20,
                        border_radius=8,
                        col=6,  # Fixed at 6 columns (out of 12 total)
                    ),
                    ft.Container(
                        content=ft.Text("col=6 (fixed)", color=ft.Colors.WHITE),
                        bgcolor=ft.Colors.TEAL,
                        padding=20,
                        border_radius=8,
                        col=6,
                    ),
                ],
                spacing=10,
                run_spacing=10,  # Spacing when wrapping
            ),

            ft.Container(height=10),

            ft.Text("Responsive breakpoint reference:", weight=ft.FontWeight.W_500),
            ft.Text("sm < 576px | md >= 576px | lg >= 768px | xl >= 992px | xxl >= 1200px",
                   color=ft.Colors.GREY_600, size=12),
        ])

    # ===== 5. Scroll Control =====
    def create_scroll_section():
        """Scroll control"""
        return ft.Column([
            ft.Text("5. Scroll Control", size=18, weight=ft.FontWeight.BOLD),
            ft.Divider(),

            ft.Row([
                # ScrollMode.ADAPTIVE - auto-show scrollbar
                ft.Column([
                    ft.Text("ADAPTIVE", weight=ft.FontWeight.W_500, size=12),
                    ft.Container(
                        content=ft.ListView(
                            [ft.Text(f"Item {i}") for i in range(20)],
                            scroll=ft.ScrollMode.ADAPTIVE,  # Adaptive scroll
                        ),
                        width=150,
                        height=150,
                        border=ft.Border.all(1, ft.Colors.GREY_300),
                        border_radius=8,
                    ),
                ]),

                # ScrollMode.AUTO - scroll when content overflows
                ft.Column([
                    ft.Text("AUTO", weight=ft.FontWeight.W_500, size=12),
                    ft.Container(
                        content=ft.ListView(
                            [ft.Text(f"Item {i}") for i in range(20)],
                            scroll=ft.ScrollMode.AUTO,
                        ),
                        width=150,
                        height=150,
                        border=ft.Border.all(1, ft.Colors.GREY_300),
                        border_radius=8,
                    ),
                ]),

                # ScrollMode.HIDDEN - hide scrollbar
                ft.Column([
                    ft.Text("HIDDEN", weight=ft.FontWeight.W_500, size=12),
                    ft.Container(
                        content=ft.ListView(
                            [ft.Text(f"Item {i}") for i in range(20)],
                            scroll=ft.ScrollMode.HIDDEN,
                        ),
                        width=150,
                        height=150,
                        border=ft.Border.all(1, ft.Colors.GREY_300),
                        border_radius=8,
                    ),
                ]),

                # ScrollMode.ALWAYS - always show scrollbar
                ft.Column([
                    ft.Text("ALWAYS", weight=ft.FontWeight.W_500, size=12),
                    ft.Container(
                        content=ft.ListView(
                            [ft.Text(f"Item {i}") for i in range(20)],
                            scroll=ft.ScrollMode.ALWAYS,
                        ),
                        width=150,
                        height=150,
                        border=ft.Border.all(1, ft.Colors.GREY_300),
                        border_radius=8,
                    ),
                ]),
            ], spacing=20),
        ])

    # ===== 6. GridView Grid Layout =====
    def create_grid_section():
        """GridView grid layout"""
        return ft.Column([
            ft.Text("6. GridView Grid Layout", size=18, weight=ft.FontWeight.BOLD),
            ft.Divider(),

            ft.GridView(
                [
                    ft.Container(
                        content=ft.Text(f"{i}", size=20, color=ft.Colors.WHITE),
                        bgcolor=[
                            ft.Colors.BLUE,
                            ft.Colors.GREEN,
                            ft.Colors.ORANGE,
                            ft.Colors.PURPLE,
                            ft.Colors.RED,
                            ft.Colors.TEAL,
                            ft.Colors.CYAN,
                            ft.Colors.INDIGO,
                            ft.Colors.PINK,
                            ft.Colors.AMBER,
                            ft.Colors.LIME,
                            ft.Colors.DEEP_ORANGE,
                        ][i],
                        border_radius=10,
                        alignment=ft.Alignment.CENTER,
                    )
                    for i in range(12)
                ],
                runs_count=4,  # Number of items per row
                max_extent=150,  # Maximum width per item
                child_aspect_ratio=1.0,  # Aspect ratio
                spacing=10,
                run_spacing=10,
                height=250,
            ),
        ])

    # ===== Page Layout =====
    # Put all content in a layout supporting both horizontal and vertical scrolling
    main_content = ft.Column(
        [
            ft.Text(
                "Flet Layout and Responsiveness Example",
                size=28,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.BLUE_700,
            ),
            ft.Divider(),

            create_layout_section(),
            ft.Divider(),
            create_expand_section(),
            ft.Divider(),
            create_stack_section(),
            ft.Divider(),
            create_responsive_section(),
            ft.Divider(),
            create_scroll_section(),
            ft.Divider(),
            create_grid_section(),
        ],
        spacing=20,
    )

    # Wrap content in a Container, set minimum width to trigger horizontal scrolling
    scrollable_content = ft.Container(
        content=main_content,
        padding=20,
        # Do not set a fixed width; let the content adapt
    )

    # Main layout: ListView provides vertical scrolling; content inside Column triggers horizontal scrolling when overflowing
    page.add(
        ft.Column(
            [scrollable_content],
            expand=True,
            scroll=ft.ScrollMode.AUTO,  # Vertical scroll
        )
    )

    # Enable page-level horizontal scrolling
    page.scroll = ft.ScrollMode.AUTO


if __name__ == "__main__":
    ft.run(main)
