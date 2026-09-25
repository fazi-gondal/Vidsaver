# -*- coding: utf-8 -*-
"""
Flet Custom Painting Example
Demonstrates drawing features of the Canvas control

Target version: Flet >= 0.83.0 (Flet 1.0+)

Breaking changes:
  - ❌ Flet 0.x: Dropdown uses on_change  →  Flet 1.0+: use on_select instead
  - ❌ Flet 0.x: PaintStyle enum  →  Flet 1.0+: use PaintingStyle instead
  - ❌ Flet 0.x: Paint stroke_dash  →  Flet 1.0+: use stroke_dash_pattern instead
  - ❌ Flet 0.x: Path method calls (move_to/line_to) → Flet 1.0+: use elements list instead
  - ❌ Flet 0.x: Polygon control  →  Flet 1.0+: use Path instead
  - ✅ Flet 1.0+: recommended to import flet.canvas as cv for Canvas-related classes
  - ✅ Flet 1.0+: use ft.run(main) to launch
"""

import flet as ft
import flet.canvas as cv
import math


def main(page: ft.Page):
    page.title = "Custom Painting Example"
    page.window.width = 700
    page.window.height = 600

    # Drawing type selection
    draw_type = ft.RadioGroup(
        content=ft.Row([
            ft.Radio(value="shapes", label="Shapes"),
            ft.Radio(value="text", label="Text"),
            ft.Radio(value="lines", label="Lines"),
            ft.Radio(value="combined", label="Combined"),
        ]),
        value="shapes",
        on_change=lambda e: update_canvas(),
    )

    # Color selection
    color_picker = ft.Dropdown(
        label="Color",
        width=150,
        value="blue",
        options=[
            ft.DropdownOption(key="blue", text="Blue"),
            ft.DropdownOption(key="red", text="Red"),
            ft.DropdownOption(key="green", text="Green"),
            ft.DropdownOption(key="purple", text="Purple"),
            ft.DropdownOption(key="orange", text="Orange"),
        ],
        on_select=lambda e: update_canvas(),
    )

    # Canvas
    canvas = cv.Canvas(
        width=600,
        height=400,
        resize_interval=10,
        on_resize=lambda e: print(f"Canvas resized: {e.width}x{e.height}"),
    )

    def update_canvas():
        canvas.shapes.clear()
        selected_color = color_picker.value

        color_map = {
            "blue": ft.Colors.BLUE,
            "red": ft.Colors.RED,
            "green": ft.Colors.GREEN,
            "purple": ft.Colors.PURPLE,
            "orange": ft.Colors.ORANGE,
        }
        color = color_map.get(selected_color, ft.Colors.BLUE)

        if draw_type.value == "shapes":
            # Draw rectangle
            canvas.shapes.append(
                ft.canvas.Rect(
                    x=50, y=50, width=100, height=80,
                    paint=ft.Paint(color=color, stroke_width=2, style=ft.PaintingStyle.STROKE),
                )
            )

            # Draw filled rectangle
            canvas.shapes.append(
                ft.canvas.Rect(
                    x=200, y=50, width=100, height=80,
                    paint=ft.Paint(color=color, style=ft.PaintingStyle.FILL),
                )
            )

            # Draw circle
            canvas.shapes.append(
                ft.canvas.Circle(
                    x=100, y=200, radius=50,
                    paint=ft.Paint(color=color, stroke_width=3, style=ft.PaintingStyle.STROKE),
                )
            )

            # Draw filled circle
            canvas.shapes.append(
                ft.canvas.Circle(
                    x=250, y=200, radius=50,
                    paint=ft.Paint(color=color, style=ft.PaintingStyle.FILL),
                )
            )

            # Draw ellipse
            canvas.shapes.append(
                ft.canvas.Oval(
                    x=400, y=150, width=150, height=100,
                    paint=ft.Paint(color=color, stroke_width=2, style=ft.PaintingStyle.STROKE),
                )
            )

            # Draw rounded rectangle
            canvas.shapes.append(
                ft.canvas.Rect(
                    x=50, y=300, width=120, height=80,
                    border_radius=15,
                    paint=ft.Paint(color=color, style=ft.PaintingStyle.FILL),
                )
            )

            # Draw polygon (using Path)
            canvas.shapes.append(
                ft.canvas.Path(
                    elements=[
                        ft.canvas.Path.MoveTo(450, 50),
                        ft.canvas.Path.LineTo(500, 100),
                        ft.canvas.Path.LineTo(480, 150),
                        ft.canvas.Path.LineTo(420, 150),
                        ft.canvas.Path.LineTo(400, 100),
                        ft.canvas.Path.Close(),
                    ],
                    paint=ft.Paint(color=color, style=ft.PaintingStyle.FILL),
                )
            )

        elif draw_type.value == "text":
            # Draw text
            canvas.shapes.append(
                ft.canvas.Text(
                    x=50, y=50,
                    value="Flet Canvas Text Drawing",
                    style=ft.TextStyle(
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=color,
                    ),
                )
            )

            # Rotated text
            canvas.shapes.append(
                ft.canvas.Text(
                    x=100, y=200,
                    value="Rotated 30°",
                    style=ft.TextStyle(size=18, color=color),
                    rotate=math.radians(30),
                )
            )

            # Large text
            canvas.shapes.append(
                ft.canvas.Text(
                    x=200, y=300,
                    value="CANVAS",
                    style=ft.TextStyle(
                        size=48,
                        weight=ft.FontWeight.BOLD,
                        color=color,
                    ),
                )
            )

        elif draw_type.value == "lines":
            # Draw straight line
            canvas.shapes.append(
                ft.canvas.Line(
                    x1=50, y1=50, x2=250, y2=150,
                    paint=ft.Paint(color=color, stroke_width=3),
                )
            )

            # Draw dashed line
            canvas.shapes.append(
                ft.canvas.Line(
                    x1=50, y1=200, x2=250, y2=300,
                    paint=ft.Paint(
                        color=color,
                        stroke_width=2,
                        stroke_dash_pattern=[10, 5],  # Dash pattern
                    ),
                )
            )

            # Draw path
            path = ft.canvas.Path(
                elements=[
                    ft.canvas.Path.MoveTo(300, 50),
                    ft.canvas.Path.LineTo(400, 100),
                    ft.canvas.Path.LineTo(350, 200),
                    ft.canvas.Path.LineTo(450, 150),
                    ft.canvas.Path.Close(),
                ],
                paint=ft.Paint(color=color, stroke_width=2, style=ft.PaintingStyle.STROKE),
            )
            canvas.shapes.append(path)

            # Draw arc
            arc = ft.canvas.Arc(
                x=400, y=250, width=150, height=150,
                start_angle=0, sweep_angle=math.pi * 1.5,
                paint=ft.Paint(color=color, stroke_width=3, style=ft.PaintingStyle.STROKE),
            )
            canvas.shapes.append(arc)

        elif draw_type.value == "combined":
            # Combined drawing
            # Background gradient rectangle
            canvas.shapes.append(
                ft.canvas.Rect(
                    x=50, y=50, width=200, height=150,
                    paint=ft.Paint(
                        color=color,
                        style=ft.PaintingStyle.FILL,
                    ),
                )
            )

            # Border
            canvas.shapes.append(
                ft.canvas.Rect(
                    x=50, y=50, width=200, height=150,
                    paint=ft.Paint(
                        color=ft.Colors.WHITE,
                        stroke_width=3,
                        style=ft.PaintingStyle.STROKE,
                    ),
                )
            )

            # Text overlay
            canvas.shapes.append(
                ft.canvas.Text(
                    x=80, y=110,
                    value="Combined Shape",
                    style=ft.TextStyle(
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE,
                    ),
                )
            )

            # Decorative circles
            canvas.shapes.append(
                ft.canvas.Circle(
                    x=400, y=125, radius=60,
                    paint=ft.Paint(color=color, style=ft.PaintingStyle.FILL),
                )
            )
            canvas.shapes.append(
                ft.canvas.Circle(
                    x=400, y=125, radius=40,
                    paint=ft.Paint(color=ft.Colors.WHITE, style=ft.PaintingStyle.FILL),
                )
            )
            canvas.shapes.append(
                ft.canvas.Circle(
                    x=400, y=125, radius=20,
                    paint=ft.Paint(color=color, style=ft.PaintingStyle.FILL),
                )
            )

            # Coordinate axes
            canvas.shapes.append(
                ft.canvas.Line(
                    x1=50, y1=350, x2=550, y2=350,
                    paint=ft.Paint(color=ft.Colors.GREY_400, stroke_width=1),
                )
            )
            canvas.shapes.append(
                ft.canvas.Line(
                    x1=50, y1=250, x2=50, y2=350,
                    paint=ft.Paint(color=ft.Colors.GREY_400, stroke_width=1),
                )
            )

        page.update()

    # Initial drawing
    update_canvas()

    page.add(
        ft.Text("Custom Painting Example", size=24, weight=ft.FontWeight.BOLD),
        ft.Divider(),
        ft.Row([draw_type, color_picker]),
        ft.Divider(),
        ft.Container(
            content=canvas,
            bgcolor=ft.Colors.GREY_50,
            border=ft.Border.all(1, ft.Colors.GREY_300),
            border_radius=10,
            padding=10,
        ),
        ft.Divider(),
        ft.Text("Canvas drawing components: Rect, Circle, Oval, Line, Arc, Path, Polygon, Text",
                size=12, color=ft.Colors.GREY_500),
    )


ft.run(main)
