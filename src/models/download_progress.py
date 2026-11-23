"""Per-task progress snapshot."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DownloadProgress:
    percent: float | None = None  # 0–100
    downloaded_bytes: int = 0
    total_bytes: int | None = None
    speed_bytes_per_sec: float | None = None
    eta_seconds: float | None = None
    fragment_index: int | None = None
    fragment_count: int | None = None
    status_text: str = ""

    def format_size(self, n: int | None) -> str:
        if n is None or n < 0:
            return "—"
        for unit in ("B", "KB", "MB", "GB"):
            if n < 1024:
                return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
            n /= 1024  # type: ignore[assignment]
        return f"{n:.1f} TB"

    @property
    def size_label(self) -> str:
        done = self.format_size(self.downloaded_bytes)
        total = self.format_size(self.total_bytes)
        return f"{done} / {total}"

    @property
    def speed_label(self) -> str:
        if not self.speed_bytes_per_sec:
            return "—"
        return f"{self.format_size(int(self.speed_bytes_per_sec))}/s"

    @property
    def eta_label(self) -> str:
        if self.eta_seconds is None:
            return "—"
        s = int(self.eta_seconds)
        if s < 60:
            return f"{s}s"
        m, s = divmod(s, 60)
        if m < 60:
            return f"{m}m {s}s"
        h, m = divmod(m, 60)
        return f"{h}h {m}m"
