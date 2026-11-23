"""Display formatting helpers."""

from __future__ import annotations


def format_bytes(n: int | float | None) -> str:
    if n is None or n < 0:
        return "—"
    value = float(n)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024 or unit == "TB":
            if unit == "B":
                return f"{int(value)} {unit}"
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{value:.1f} TB"


def format_duration(seconds: float | int | None) -> str:
    if seconds is None:
        return "—"
    try:
        s = int(float(seconds))
    except (TypeError, ValueError):
        return "—"
    if s < 0:
        return "—"
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    if h:
        return f"{h}:{m:02d}:{sec:02d}"
    return f"{m}:{sec:02d}"


def format_percent(value: float | None) -> str:
    if value is None:
        return "—"
    return f"{value * 100:.0f}%" if value <= 1 else f"{value:.0f}%"
