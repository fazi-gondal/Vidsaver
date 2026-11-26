"""Nocturnal Studio design system for VidSaver: palettes, themes, typography, and tonal components.

Tonal layering instead of Material shadows: hierarchy comes from stacking
surfaces (base -> elevated -> highest) separated by 1px subtle borders.
Coral is the primary accent (downloads / CTAs); teal identifies post-processing.
"""

from __future__ import annotations

from dataclasses import dataclass

import flet as ft

FONT_HEADLINE = "Space Grotesk"
FONT_HEADLINE_BOLD = "Space Grotesk Bold"
FONT_BODY = "Inter"
FONT_BODY_MEDIUM = "Inter Medium"
FONT_BODY_SEMIBOLD = "Inter SemiBold"

RADIUS_CARD = 16
RADIUS_CONTROL = 10
RADIUS_PILL = 999

# Mid-tone semantic colors that hold AA contrast on both dark and light
# tinted backgrounds (pill text is the saturated color itself).
PILL_CORAL = "#FF5C49"
PILL_TEAL = "#2BB3A8"
PILL_GREEN = "#4CAF50"
PILL_RED = "#EF5350"
PILL_AMBER = "#F59E0B"
PILL_BLUE = "#42A5F5"
PILL_PURPLE = "#AB7DF6"
PILL_GREY = "#9BA1A6"

PLATFORM_PILL_COLORS: dict[str, str] = {
    "YouTube": PILL_RED,
    "TikTok": PILL_TEAL,
    "Instagram": "#E1306C",
    "Facebook": PILL_BLUE,
    "X / Twitter": PILL_GREY,
    "Snapchat": PILL_AMBER,
    "Reddit": "#FF6B35",
    "Pinterest": PILL_RED,
    "Threads": PILL_PURPLE,
    "Vimeo": PILL_BLUE,
    "Dailymotion": PILL_BLUE,
    "Twitch": PILL_PURPLE,
    "LinkedIn": PILL_BLUE,
    "Bilibili": PILL_TEAL,
}


@dataclass(frozen=True)
class Palette:
    """Raw design tokens for one brightness mode."""

    window_bg: str
    surface_base: str
    surface_elevated: str
    surface_highest: str
    surface_inset: str
    border_subtle: str
    border_strong: str
    text: str
    text_muted: str
    accent: str
    accent_hover: str
    on_accent: str
    teal: str
    teal_bright: str
    on_teal: str
    success: str
    error: str
    warning: str
    info: str


DARK = Palette(
    window_bg="#111318",
    surface_base="#16181D",
    surface_elevated="#1E2127",
    surface_highest="#2A2D35",
    surface_inset="#121418",
    border_subtle=ft.Colors.with_opacity(0.08, "#FFFFFF"),
    border_strong=ft.Colors.with_opacity(0.15, "#FFFFFF"),
    text="#E2E2E9",
    text_muted="#9BA1A6",
    accent="#FF5C49",
    accent_hover="#FF7261",
    on_accent="#FFFFFF",
    teal="#32A097",
    teal_bright="#71D7CD",
    on_teal="#00302C",
    success="#4CAF50",
    error="#EF5350",
    warning="#FF9800",
    info="#2196F3",
)

LIGHT = Palette(
    window_bg="#F8F9FF",
    surface_base="#F8F9FF",
    surface_elevated="#FFFFFF",
    surface_highest="#E7E8EE",
    surface_inset="#EDEDF4",
    border_subtle=ft.Colors.with_opacity(0.08, "#000000"),
    border_strong=ft.Colors.with_opacity(0.16, "#000000"),
    text="#1A1C1E",
    text_muted="#44474E",
    accent="#FF5C49",
    accent_hover="#E84A38",
    on_accent="#FFFFFF",
    teal="#006A62",
    teal_bright="#006A62",
    on_teal="#FFFFFF",
    success="#2E7D32",
    error="#C62828",
    warning="#B26A00",
    info="#1565C0",
)


def headline_xl(color: str = ft.Colors.ON_SURFACE) -> ft.TextStyle:
    return ft.TextStyle(
        font_family=FONT_HEADLINE,
        size=28,
        weight=ft.FontWeight.W_700,
        letter_spacing=0,
        color=color,
    )


def headline_lg(color: str = ft.Colors.ON_SURFACE) -> ft.TextStyle:
    return ft.TextStyle(
        font_family=FONT_HEADLINE,
        size=24,
        weight=ft.FontWeight.W_600,
        color=color,
    )


def headline_md(color: str = ft.Colors.ON_SURFACE) -> ft.TextStyle:
    return ft.TextStyle(
        font_family=FONT_HEADLINE,
        size=18,
        weight=ft.FontWeight.W_600,
        color=color,
    )


def body_lg(color: str = ft.Colors.ON_SURFACE) -> ft.TextStyle:
    return ft.TextStyle(font_family=FONT_BODY, size=16, color=color)


def body_md(color: str = ft.Colors.ON_SURFACE) -> ft.TextStyle:
    return ft.TextStyle(font_family=FONT_BODY, size=14, color=color)


def body_sm(color: str = ft.Colors.ON_SURFACE) -> ft.TextStyle:
    return ft.TextStyle(font_family=FONT_BODY, size=13, color=color)


def label_md(color: str = ft.Colors.ON_SURFACE) -> ft.TextStyle:
    return ft.TextStyle(
        font_family=FONT_BODY_MEDIUM,
        size=12,
        weight=ft.FontWeight.W_500,
        letter_spacing=0.6,
        color=color,
    )


def data_style(color: str = ft.Colors.ON_SURFACE) -> ft.TextStyle:
    """Live metrics (progress, sizes, dates). Always Inter, never Space Grotesk."""
    return ft.TextStyle(
        font_family=FONT_BODY_MEDIUM,
        size=13,
        weight=ft.FontWeight.W_500,
        color=color,
    )


def _color_scheme(p: Palette) -> ft.ColorScheme:
    return ft.ColorScheme(
        primary=p.accent,
        on_primary=p.on_accent,
        primary_container=ft.Colors.with_opacity(0.15, p.accent),
        on_primary_container=p.accent,
        secondary=p.teal,
        on_secondary=p.on_teal,
        secondary_container=ft.Colors.with_opacity(0.18, p.teal),
        on_secondary_container=p.teal_bright,
        tertiary=p.warning,
        on_tertiary="#FFFFFF",
        error=p.error,
        on_error="#FFFFFF",
        error_container=ft.Colors.with_opacity(0.15, p.error),
        on_error_container=p.error,
        surface=p.surface_base,
        on_surface=p.text,
        on_surface_variant=p.text_muted,
        surface_container_lowest=p.surface_inset,
        surface_container_low=p.surface_elevated,
        surface_container=p.surface_elevated,
        surface_container_high=p.surface_highest,
        surface_container_highest=p.surface_highest,
        surface_dim=p.window_bg,
        surface_bright=p.surface_highest,
        outline=p.border_strong,
        outline_variant=p.border_subtle,
        surface_tint=ft.Colors.TRANSPARENT,
        inverse_surface=p.text,
        on_inverse_surface=p.surface_base,
        inverse_primary=p.accent,
        shadow=ft.Colors.TRANSPARENT,
    )


def _text_theme(p: Palette) -> ft.TextTheme:
    return ft.TextTheme(
        headline_large=headline_xl(p.text),
        headline_medium=headline_lg(p.text),
        headline_small=headline_md(p.text),
        title_large=headline_lg(p.text),
        title_medium=headline_md(p.text),
        title_small=ft.TextStyle(
            font_family=FONT_HEADLINE,
            size=15,
            weight=ft.FontWeight.W_600,
            color=p.text,
        ),
        body_large=body_lg(p.text),
        body_medium=body_md(p.text),
        body_small=body_sm(p.text),
        label_large=ft.TextStyle(
            font_family=FONT_BODY_MEDIUM,
            size=14,
            weight=ft.FontWeight.W_500,
            color=p.text,
        ),
        label_medium=label_md(p.text),
        label_small=ft.TextStyle(
            font_family=FONT_BODY_MEDIUM,
            size=11,
            weight=ft.FontWeight.W_500,
            letter_spacing=0.5,
            color=p.text,
        ),
    )


def _build_theme(p: Palette) -> ft.Theme:
    control_shape = ft.RoundedRectangleBorder(radius=RADIUS_CONTROL)
    return ft.Theme(
        use_material3=True,
        font_family=FONT_BODY,
        color_scheme=_color_scheme(p),
        text_theme=_text_theme(p),
        scaffold_bgcolor=p.window_bg,
        divider_color=p.border_subtle,
        hover_color=ft.Colors.with_opacity(0.05, p.text),
        splash_color=ft.Colors.with_opacity(0.08, p.text),
        highlight_color=ft.Colors.with_opacity(0.06, p.text),
        card_theme=ft.CardTheme(
            color=p.surface_elevated,
            elevation=0,
            shape=ft.RoundedRectangleBorder(radius=RADIUS_CARD),
            margin=ft.Margin.all(0),
        ),
        filled_button_theme=ft.FilledButtonTheme(
            style=ft.ButtonStyle(
                bgcolor={
                    ft.ControlState.DEFAULT: p.accent,
                    ft.ControlState.HOVERED: p.accent_hover,
                    ft.ControlState.DISABLED: p.surface_highest,
                },
                color={
                    ft.ControlState.DEFAULT: p.on_accent,
                    ft.ControlState.DISABLED: p.text_muted,
                },
                icon_color={
                    ft.ControlState.DEFAULT: p.on_accent,
                    ft.ControlState.DISABLED: p.text_muted,
                },
                overlay_color=ft.Colors.TRANSPARENT,
                elevation=0,
                shape=control_shape,
                padding=ft.Padding.symmetric(vertical=14, horizontal=22),
                text_style=ft.TextStyle(
                    font_family=FONT_HEADLINE,
                    size=15,
                    weight=ft.FontWeight.W_600,
                ),
            )
        ),
        outlined_button_theme=ft.OutlinedButtonTheme(
            style=ft.ButtonStyle(
                color=p.text,
                icon_color=p.text_muted,
                bgcolor={
                    ft.ControlState.DEFAULT: ft.Colors.TRANSPARENT,
                    ft.ControlState.HOVERED: p.surface_highest,
                },
                overlay_color=ft.Colors.TRANSPARENT,
                side=ft.BorderSide(1, p.border_strong),
                shape=control_shape,
                padding=ft.Padding.symmetric(vertical=14, horizontal=18),
                text_style=ft.TextStyle(
                    font_family=FONT_BODY_MEDIUM,
                    size=14,
                    weight=ft.FontWeight.W_500,
                ),
            )
        ),
        text_button_theme=ft.TextButtonTheme(
            style=ft.ButtonStyle(
                color=p.accent,
                shape=control_shape,
                text_style=ft.TextStyle(
                    font_family=FONT_BODY_MEDIUM,
                    size=14,
                    weight=ft.FontWeight.W_500,
                ),
            )
        ),
        icon_button_theme=ft.IconButtonTheme(
            style=ft.ButtonStyle(
                shape=control_shape,
                overlay_color=ft.Colors.with_opacity(0.08, p.text),
            )
        ),
        progress_indicator_theme=ft.ProgressIndicatorTheme(
            color=p.accent,
            linear_track_color=p.surface_highest,
            border_radius=ft.BorderRadius.all(RADIUS_PILL),
        ),
        scrollbar_theme=ft.ScrollbarTheme(
            thumb_color={ft.ControlState.DEFAULT: ft.Colors.with_opacity(0.25, p.text)},
            radius=8,
            thickness={ft.ControlState.DEFAULT: 6},
        ),
        navigation_bar_theme=ft.NavigationBarTheme(
            bgcolor=p.surface_base,
            indicator_color=ft.Colors.with_opacity(0.15, p.accent),
            elevation=0,
            label_text_style=ft.TextStyle(
                font_family=FONT_BODY_MEDIUM,
                size=12,
                weight=ft.FontWeight.W_500,
            ),
        ),
    )


def light_theme() -> ft.Theme:
    return _build_theme(LIGHT)


def dark_theme() -> ft.Theme:
    return _build_theme(DARK)


def status_pill(text: str, color: str = PILL_GREY) -> ft.Container:
    """Uppercase tinted pill badge per Nocturnal Studio design system."""
    return ft.Container(
        content=ft.Text(
            text.upper(),
            style=ft.TextStyle(
                size=10.5,
                weight=ft.FontWeight.W_600,
                color=color,
                font_family=FONT_BODY_SEMIBOLD,
                letter_spacing=0.8,
            ),
        ),
        bgcolor=ft.Colors.with_opacity(0.15, color),
        border=ft.Border.all(1, ft.Colors.with_opacity(0.3, color)),
        border_radius=ft.BorderRadius.all(RADIUS_PILL),
        padding=ft.Padding.symmetric(vertical=3, horizontal=10),
    )


def surface_card(
    content: ft.Control,
    padding: ft.PaddingValue = 16,
    border_color: str | None = None,
    gradient: ft.Gradient | None = None,
    on_click=None,
    ink: bool = False,
) -> ft.Container:
    """Level-1 tonal surface card with 1px subtle border, zero shadows."""
    return ft.Container(
        content=content,
        padding=padding,
        bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
        border=ft.Border.all(1, border_color or ft.Colors.OUTLINE_VARIANT),
        border_radius=ft.BorderRadius.all(RADIUS_CARD),
        gradient=gradient,
        on_click=on_click,
        ink=ink,
    )


def inset_input_box(
    content: ft.Control,
    padding: ft.PaddingValue | None = None,
    radius: int = RADIUS_CONTROL + 2,
) -> ft.Container:
    """Sunken surface container for borderless TextField inputs and search bars."""
    if padding is None:
        padding = ft.Padding.symmetric(vertical=4, horizontal=12)
    return ft.Container(
        content=content,
        padding=padding,
        bgcolor=ft.Colors.SURFACE_CONTAINER_LOWEST,
        border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
        border_radius=ft.BorderRadius.all(radius),
    )


def empty_state(
    icon: ft.IconData,
    title: str,
    subtitle: str | None = None,
    action: ft.Control | None = None,
    compact: bool = False,
) -> ft.Container:
    """Centered empty-state placeholder with circular icon badge."""
    controls: list[ft.Control] = [
        ft.Container(
            content=ft.Icon(icon, size=36, color=ft.Colors.ON_SURFACE_VARIANT),
            width=72,
            height=72,
            alignment=ft.Alignment.CENTER,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
            border_radius=ft.BorderRadius.all(RADIUS_PILL),
            opacity=0.85,
        ),
        ft.Text(
            title,
            style=headline_md(),
            text_align=ft.TextAlign.CENTER,
        ),
    ]
    if subtitle:
        controls.append(
            ft.Text(
                subtitle,
                style=body_sm(ft.Colors.ON_SURFACE_VARIANT),
                text_align=ft.TextAlign.CENTER,
            )
        )
    if action is not None:
        controls.append(ft.Container(content=action, padding=ft.Padding(top=4, bottom=0, left=0, right=0)))

    return ft.Container(
        content=ft.Column(
            controls=controls,
            spacing=10,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        alignment=ft.Alignment.CENTER,
        padding=ft.Padding.symmetric(vertical=24 if compact else 48, horizontal=20),
        expand=not compact,
    )
