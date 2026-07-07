# -*- coding: utf-8 -*-
"""
Flet Chart Bindng Example
Demonstrates simple data visualization

Target version: Flet >= 0.83.0 (Flet 1.0+)

Breaking changes:
  - ✅ Flet 1.0+: Flet has no built-in chart controls; use Container composition or Canvas custom drawing
  - ✅ Flet 1.0+: use ft.run(main) to launch
  - ✅ Flet 1.0+: colors use ft.Colors.XXX (capital C)
  - Note: Chart drawing API has no breaking changes in Flet 1.0+
"""

import flet as ft
import flet.canvas as cv
import asyncio
import random


def main(page: ft.Page):
    page.title = "Data Visualization Example"
    page.window.width = 700
    page.window.height = 600
    page.scroll = ft.ScrollMode.AUTO

    # Sample data
    chart_data = [
        {"label": "Jan", "value": 65},
        {"label": "Feb", "value": 85},
        {"label": "Mar", "value": 45},
        {"label": "Apr", "value": 92},
        {"label": "May", "value": 78},
        {"label": "Jun", "value": 60},
    ]

    # Bar chart container (with Y axis)
    chart_height = 150
    y_axis_labels = ft.Column(
        list[ft.Control]([ft.Text(f"{i}", size=10, color=ft.Colors.GREY_600, width=25) for i in [100, 75, 50, 25, 0]]),
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        height=chart_height,
    )
    bar_chart = ft.Row(alignment=ft.MainAxisAlignment.SPACE_EVENLY)
    bar_chart_with_axis = ft.Row(
        list[ft.Control]([
            y_axis_labels,
            ft.Column(
                list[ft.Control]([
                    bar_chart,
                    ft.Divider(height=1, color=ft.Colors.GREY_400),
                    ft.Row(
                        list[ft.Control]([ft.Text(str(d["label"]), size=10, width=45, text_align=ft.TextAlign.CENTER) for d in chart_data]),
                        alignment=ft.MainAxisAlignment.SPACE_AROUND,
                    ),
                ])
            ),
        ]),
        vertical_alignment=ft.CrossAxisAlignment.END
    )

    # Maximum value (for calculating proportions)
    max_value = max(d["value"] for d in chart_data)

    def create_bar_chart():
        bar_chart.controls.clear()
        for item in chart_data:
            height = (item["value"] / 100) * chart_height
            bar_chart.controls.append(
                ft.Container(
                    content=ft.Text(f"{item['value']}", size=11, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                    bgcolor=ft.Colors.BLUE,
                    width=40,
                    height=height,
                    border_radius=ft.BorderRadius(top_left=5, top_right=5, bottom_left=0, bottom_right=0),
                    alignment=ft.Alignment.CENTER,
                    animate=ft.Animation(500, ft.AnimationCurve.EASE_OUT),
                )
            )

    create_bar_chart()

    # Progress bar chart
    progress_bars = ft.Column(spacing=10)

    progress_data = [
        {"label": "CPU Usage", "value": 0.75, "color": ft.Colors.RED},
        {"label": "Memory Usage", "value": 0.60, "color": ft.Colors.ORANGE},
        {"label": "Disk Usage", "value": 0.45, "color": ft.Colors.GREEN},
        {"label": "Network Bandwidth", "value": 0.85, "color": ft.Colors.BLUE},
    ]

    def create_progress_bars():
        progress_bars.controls.clear()
        for item in progress_data:
            progress_bars.controls.append(
                ft.Column([
                    ft.Row([
                        ft.Text(item["label"], width=100),
                        ft.Text(f"{int(item['value'] * 100)}%", width=40),
                    ]),
                    ft.ProgressBar(
                        value=item["value"],
                        bar_height=10,
                        color=item["color"],
                        bgcolor=ft.Colors.GREY_200,
                        width=300,
                    ),
                ])
            )

    create_progress_bars()

    # Real-time data update
    is_updating = [False]

    async def toggle_realtime(e):
        is_updating[0] = not is_updating[0]
        realtime_btn.content = ft.Text("Stop Update" if is_updating[0] else "Real-time Update")
        page.update()

        while is_updating[0]:
            # Update progress bar data
            for item in progress_data:
                item["value"] = random.uniform(0.3, 1.0)
            create_progress_bars()

            # Update bar chart data
            for item in chart_data:
                item["value"] = random.randint(30, 100)
            create_bar_chart()
            draw_line_chart()

            page.update()
            await asyncio.sleep(1)

    # Circular progress indicators
    circular_indicators = ft.Row(
        [
            ft.Column([
                ft.ProgressRing(value=0.7, width=60, height=60, color=ft.Colors.BLUE),
                ft.Text("70%"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Column([
                ft.ProgressRing(value=0.5, width=60, height=60, color=ft.Colors.GREEN),
                ft.Text("50%"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Column([
                ft.ProgressRing(value=0.3, width=60, height=60, color=ft.Colors.RED),
                ft.Text("30%"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Column([
                ft.ProgressRing(value=None, width=60, height=60),  # Indeterminate progress
                ft.Text("Loading"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        ],
        alignment=ft.MainAxisAlignment.SPACE_EVENLY,
    )

    # Draw simple line chart using Canvas (with scale and values)
    canvas = cv.Canvas(width=380, height=180)

    def draw_line_chart():
        canvas.shapes.clear()

        # Drawing area parameters
        left_margin, right_margin = 45, 20
        top_margin, bottom_margin = 20, 30
        plot_width = 380 - left_margin - right_margin
        plot_height = 180 - top_margin - bottom_margin

        # Draw Y-axis grid lines and labels
        for i, val in enumerate([100, 75, 50, 25, 0]):
            y = top_margin + (i / 4) * plot_height
            # Grid line
            canvas.shapes.append(
                cv.Line(x1=left_margin, y1=y, x2=380 - right_margin, y2=y,
                       paint=ft.Paint(color=ft.Colors.GREY_200, stroke_width=1))
            )
            # Label value
            canvas.shapes.append(
                cv.Text(x=left_margin - 35, y=y - 6, value=str(val),
                       style=ft.TextStyle(size=9, color=ft.Colors.GREY_600))
            )

        # Draw coordinate axes
        canvas.shapes.append(
            cv.Line(x1=left_margin, y1=180 - bottom_margin, x2=380 - right_margin, y2=180 - bottom_margin,
                   paint=ft.Paint(color=ft.Colors.GREY_500, stroke_width=1.5))
        )
        canvas.shapes.append(
            cv.Line(x1=left_margin, y1=top_margin, x2=left_margin, y2=180 - bottom_margin,
                   paint=ft.Paint(color=ft.Colors.GREY_500, stroke_width=1.5))
        )

        # Draw line and data points
        points = []
        x_step = plot_width / (len(chart_data) - 1)
        for i, item in enumerate(chart_data):
            x = left_margin + i * x_step
            y = 180 - bottom_margin - (item["value"] / 100) * plot_height
            points.append((x, y))

            # X-axis labels
            canvas.shapes.append(
                cv.Text(x=x - 15, y=180 - bottom_margin + 8, value=item["label"][:3],
                       style=ft.TextStyle(size=9, color=ft.Colors.GREY_600))
            )

            # Data points
            canvas.shapes.append(
                cv.Circle(x=x, y=y, radius=5,
                         paint=ft.Paint(color=ft.Colors.BLUE, style=ft.PaintingStyle.FILL))
            )
            # Data values
            canvas.shapes.append(
                cv.Text(x=x - 10, y=y - 18, value=str(item["value"]),
                       style=ft.TextStyle(size=9, color=ft.Colors.BLUE, weight=ft.FontWeight.BOLD))
            )

        # Connect line segments
        path = cv.Path(
            paint=ft.Paint(color=ft.Colors.BLUE, stroke_width=2, style=ft.PaintingStyle.STROKE),
            elements=[
                cv.Path.MoveTo(x=points[0][0], y=points[0][1]),
            ] + [cv.Path.LineTo(x=px, y=py) for px, py in points[1:]],
        )
        canvas.shapes.append(path)

        page.update()

    draw_line_chart()

    realtime_btn = ft.Button(
        content=ft.Text("Real-time Update"),
        style=ft.ButtonStyle(bgcolor=ft.Colors.PURPLE, color=ft.Colors.WHITE),
        on_click=toggle_realtime,
    )

    page.add(
        ft.Text("Data Visualization Example", size=24, weight=ft.FontWeight.BOLD),
        ft.Divider(),

        ft.Text("Bar Chart (using Container):", weight=ft.FontWeight.W_500),
        ft.Container(
            content=bar_chart_with_axis,
            bgcolor=ft.Colors.GREY_50,
            padding=ft.Padding(20, 15, 20, 5),
            border_radius=10,
        ),

        ft.Divider(),
        ft.Text("Line Chart (using Canvas):", weight=ft.FontWeight.W_500),
        ft.Container(
            content=canvas,
            bgcolor=ft.Colors.GREY_50,
            border_radius=10,
            padding=15,
        ),

        ft.Divider(),
        ft.Text("Progress Bars:", weight=ft.FontWeight.W_500),
        progress_bars,

        ft.Divider(),
        ft.Text("Circular Progress Indicators:", weight=ft.FontWeight.W_500),
        circular_indicators,

        ft.Divider(),
        realtime_btn,

        ft.Text("Tip: For complex charts, use libraries like plotly or matplotlib to generate images",
                size=12, color=ft.Colors.GREY_500),
    )


ft.run(main)
