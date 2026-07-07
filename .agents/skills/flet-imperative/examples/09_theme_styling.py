# -*- coding: utf-8 -*-
"""
Flet Theme and Color Scheme Example
Demonstrates Theme, ColorScheme, dark mode, and other theme settings

Target version: Flet >= 0.83.0 (Flet 1.0+)

Breaking changes:
  - ❌ Flet 0.x: page.theme = ft.Theme(primary_swatch=...)  →  Flet 1.0+: removed
  - ✅ Flet 1.0+: Use page.theme = ft.Theme(color_scheme_seed=ft.Colors.XXX)
  - ❌ Flet 0.x: ft.Radio(value="1", label="...") used standalone  →  Flet 1.0+: raises "Radio must be enclosed within RadioGroup"
  - ✅ Flet 1.0+: Must wrap with ft.RadioGroup(content=ft.Radio(...))
  - ❌ Flet 0.x: TabBarView without height  →  Flet 1.0+: raises "height is unbounded"
  - ✅ Flet 1.0+: TabBarView must have height set directly (e.g. height=120)
  - ✅ Flet 1.0+: Use ft.run(main) to start
"""

import flet as ft


def main(page: ft.Page):
    """Theme and color scheme example main function"""
    page.title = "Theme and Color Scheme Example"
    page.window.width = 800
    page.window.height = 700
    page.padding = 20

    # ===== Theme State =====
    is_dark_mode = [False]
    current_theme_seed = [ft.Colors.BLUE]

    # ===== Color Seed Options =====
    theme_colors = [
        ("Blue", ft.Colors.BLUE),
        ("Red", ft.Colors.RED),
        ("Green", ft.Colors.GREEN),
        ("Purple", ft.Colors.PURPLE),
        ("Orange", ft.Colors.ORANGE),
        ("Teal", ft.Colors.TEAL),
        ("Pink", ft.Colors.PINK),
        ("Indigo", ft.Colors.INDIGO),
    ]

    def apply_theme():
        """Apply the theme"""
        # ✅ Use color_scheme_seed to replace the removed primary_swatch
        page.theme = ft.Theme(
            color_scheme_seed=current_theme_seed[0],
            use_material3=True,  # Use Material 3 design
        )

        page.dark_theme = ft.Theme(
            color_scheme_seed=current_theme_seed[0],
            use_material3=True,
        )

        page.theme_mode = ft.ThemeMode.DARK if is_dark_mode[0] else ft.ThemeMode.LIGHT
        page.update()

    def toggle_theme(e):
        """Toggle dark/light mode"""
        is_dark_mode[0] = not is_dark_mode[0]
        theme_toggle.selected = is_dark_mode[0]
        apply_theme()

    def change_theme_color(e):
        """Change the theme color"""
        current_theme_seed[0] = e.control.data
        apply_theme()

    # ===== Theme Toggle Control =====
    theme_toggle = ft.IconButton(
        icon=ft.Icons.LIGHT_MODE,
        selected_icon=ft.Icons.DARK_MODE,
        selected=False,
        on_click=toggle_theme,
        tooltip="Toggle Dark/Light Mode",
    )

    # ===== Color Picker =====
    def create_color_buttons():
        """Create color selection buttons"""
        buttons = []
        for name, color in theme_colors:
            buttons.append(
                ft.IconButton(
                    icon=ft.Icons.PALETTE,
                    icon_color=color,
                    data=color,
                    on_click=change_theme_color,
                    tooltip=name,
                )
            )
        return buttons

    # ===== Sample Controls Showcase =====
    def create_sample_controls():
        """Create sample controls to showcase theme effects"""
        return ft.Column([
            ft.Text("Theme Effect Preview", size=18, weight=ft.FontWeight.BOLD),
            ft.Divider(),

            # Buttons
            ft.Row([
                ft.Button(content=ft.Text("Primary Button"), style=ft.ButtonStyle()),
                ft.Button(
                    content=ft.Text("Custom Button"),
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.RED,
                    ),
                ),
                ft.Button(
                    content=ft.Text("Outlined Button"),
                    style=ft.ButtonStyle(
                        side=ft.BorderSide(2, ft.Colors.BLUE),
                        color=ft.Colors.BLUE,
                    ),
                ),
            ], spacing=10),

            ft.Container(height=10),

            # Text field
            ft.TextField(
                label="Text Field",
                hint_text="Enter content",
                width=300,
            ),

            ft.Container(height=10),

            # Card
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.ALBUM),
                            title=ft.Text("Card Title"),
                            subtitle=ft.Text("This is the card subtitle description"),
                        ),
                        ft.Row([
                            ft.Button(content=ft.Text("Action")),
                            ft.Button(content=ft.Text("Cancel")),
                        ], alignment=ft.MainAxisAlignment.END, spacing=10),
                    ]),
                    padding=10,
                ),
                elevation=4,
            ),

            ft.Container(height=10),

            # Progress indicators
            ft.Column([
                ft.Text("Progress Indicators:"),
                ft.ProgressBar(width=300, value=0.7),
                ft.Container(height=5),
                ft.ProgressRing(width=40, height=40, value=0.5),
            ]),

            ft.Container(height=10),

            # Switch and checkbox
            ft.Row([
                ft.Switch(label="Switch"),
                ft.Checkbox(label="Checkbox", value=True),
                ft.RadioGroup(
                    value="1",
                    content=ft.Radio(value="1", label="Radio"),
                ),
            ], spacing=20),

            ft.Container(height=10),

            # Dropdown
            ft.Dropdown(
                label="Dropdown Select",
                width=200,
                options=[
                    ft.DropdownOption(key="1", text="Option 1"),
                    ft.DropdownOption(key="2", text="Option 2"),
                    ft.DropdownOption(key="3", text="Option 3"),
                ],
            ),

            ft.Container(height=10),

            # Slider
            ft.Slider(
                label="Slider: {value}",
                min=0,
                max=100,
                value=50,
                width=300,
            ),

            ft.Container(height=10),

            # Tabs (Flet 1.0+ new API: Tabs + TabBar + TabBarView)
            ft.Tabs(
                content=ft.Column([
                    ft.TabBar(
                        tabs=[
                            ft.Tab(
                                label=ft.Row([
                                    ft.Icon(ft.Icons.HOME, size=16),
                                    ft.Text("Home"),
                                ], spacing=5),
                            ),
                            ft.Tab(
                                label=ft.Row([
                                    ft.Icon(ft.Icons.SETTINGS, size=16),
                                    ft.Text("Settings"),
                                ], spacing=5),
                            ),
                            ft.Tab(
                                label=ft.Row([
                                    ft.Icon(ft.Icons.INFO, size=16),
                                    ft.Text("About"),
                                ], spacing=5),
                            ),
                        ],
                    ),
                    ft.TabBarView(
                        height=120,
                        controls=[
                            ft.Container(
                                content=ft.Text("This is the Home content area", color=ft.Colors.GREY_700),
                                padding=20,
                            ),
                            ft.Container(
                                content=ft.Text("This is the Settings content area", color=ft.Colors.GREY_700),
                                padding=20,
                            ),
                            ft.Container(
                                content=ft.Text("This is the About content area", color=ft.Colors.GREY_700),
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

    # ===== ColorScheme Customization =====
    def create_color_scheme_section():
        """ColorScheme customization notes"""
        return ft.Column([
            ft.Text("ColorScheme Customization", size=18, weight=ft.FontWeight.BOLD),
            ft.Divider(),

            ft.Text(
                "✅ Recommended in new version: Use color_scheme_seed to auto-generate color schemes",
                color=ft.Colors.GREEN,
            ),
            ft.Container(height=10),

            ft.Text("Code example:"),
            ft.Container(
                content=ft.Column([
                    ft.Text("page.theme = ft.Theme(", font_family="monospace", size=12),
                    ft.Text("    color_scheme_seed=ft.Colors.BLUE,", font_family="monospace", size=12),
                    ft.Text("    use_material3=True,", font_family="monospace", size=12),
                    ft.Text(")", font_family="monospace", size=12),
                ]),
                bgcolor=ft.Colors.GREY_200 if not is_dark_mode[0] else ft.Colors.GREY_800,
                padding=15,
                border_radius=8,
            ),

            ft.Container(height=15),

            ft.Text("❌ Removed properties:", color=ft.Colors.RED),
            ft.Container(
                content=ft.Column([
                    ft.Text("primary_swatch → use color_scheme_seed", font_family="monospace", size=12),
                    ft.Text("primary_color → use ColorScheme.primary", font_family="monospace", size=12),
                    ft.Text("primary_color_dark → removed", font_family="monospace", size=12),
                    ft.Text("primary_color_light → removed", font_family="monospace", size=12),
                    ft.Text("shadow_color → use ColorScheme.shadow", font_family="monospace", size=12),
                    ft.Text("divider_color → use DividerTheme.color", font_family="monospace", size=12),
                ]),
                bgcolor=ft.Colors.RED_50 if not is_dark_mode[0] else ft.Colors.RED_900,
                padding=15,
                border_radius=8,
            ),
        ])

    # ===== Advanced Theme Customization =====
    def create_advanced_theme_section():
        """Advanced theme customization"""
        return ft.Column([
            ft.Text("Advanced Theme Customization", size=18, weight=ft.FontWeight.BOLD),
            ft.Divider(),

            ft.Text("Custom control themes:"),
            ft.Container(
                content=ft.Column([
                    ft.Text("# Button Theme", weight=ft.FontWeight.BOLD),
                    ft.Text("page.theme.floating_action_button_theme =", font_family="monospace", size=11),
                    ft.Text("    ft.FloatingActionButtonTheme(bgcolor=ft.Colors.RED)", font_family="monospace", size=11),
                    ft.Text(""),
                    ft.Text("# Card Theme", weight=ft.FontWeight.BOLD),
                    ft.Text("page.theme.card_theme =", font_family="monospace", size=11),
                    ft.Text("    ft.CardTheme(elevation=8, shape=ft.RoundedRectangleBorder(radius=10))", font_family="monospace", size=11),
                    ft.Text(""),
                    ft.Text("# Input Field Theme", weight=ft.FontWeight.BOLD),
                    ft.Text("page.theme.input_decoration_theme =", font_family="monospace", size=11),
                    ft.Text("    ft.InputDecorationTheme(filled=True, fillColor=ft.Colors.GREY_100)", font_family="monospace", size=11),
                ]),
                bgcolor=ft.Colors.GREY_200 if not is_dark_mode[0] else ft.Colors.GREY_800,
                padding=15,
                border_radius=8,
            ),

            ft.Container(height=10),

            # Example card
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.INFO, color=ft.Colors.BLUE),
                            title=ft.Text("Theme Inheritance Note"),
                            subtitle=ft.Text("Child controls automatically inherit the parent's theme settings"),
                        ),
                    ]),
                    padding=10,
                ),
            ),
        ])

    # ===== Page Layout =====
    page.add(
        ft.Column([
            # Title bar
            ft.Row([
                ft.Text(
                    "Theme and Color Scheme Example",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_700,
                ),
                theme_toggle,
                *create_color_buttons(),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

            ft.Divider(),

            # Content area
            ft.Row([
                ft.Column([
                    create_sample_controls(),
                ], scroll=ft.ScrollMode.AUTO, expand=True),

                ft.VerticalDivider(),

                ft.Column([
                    create_color_scheme_section(),
                    ft.Divider(),
                    create_advanced_theme_section(),
                ], scroll=ft.ScrollMode.AUTO, width=350),
            ], expand=True),
        ], expand=True)
    )

    # Initialize theme
    apply_theme()


if __name__ == "__main__":
    ft.run(main)
