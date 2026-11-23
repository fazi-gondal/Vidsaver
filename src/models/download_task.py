"""Independent download task model."""

from __future__ import annotations

import threading
import time
import uuid
from dataclasses import dataclass, field

from models.download_progress import DownloadProgress
from models.download_request import DownloadRequest
from models.download_state import DownloadState


@dataclass
class DownloadTask:
    request: DownloadRequest
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    title: str = ""
    platform: str = "Video"
    thumbnail_url: str = ""
    state: DownloadState = DownloadState.PENDING
    progress: DownloadProgress = field(default_factory=DownloadProgress)
    output_path: str = ""
    error: str = ""
    created_at: float = field(default_factory=time.time)
    finished_at: float | None = None
    cancel_event: threading.Event = field(default_factory=threading.Event, repr=False)

    @property
    def is_terminal(self) -> bool:
        return self.state.is_terminal

    @property
    def is_active(self) -> bool:
        return self.state.is_active

    def mark(self, state: DownloadState, *, error: str = "") -> None:
        self.state = state
        if error:
            self.error = error
        if state.is_terminal:
            self.finished_at = time.time()
