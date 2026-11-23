"""Download task lifecycle states."""

from __future__ import annotations

from enum import Enum


class DownloadState(str, Enum):
    PENDING = "pending"
    PREPARING = "preparing"
    DOWNLOADING = "downloading"
    PROCESSING = "processing"
    PUBLISHING_TO_GALLERY = "publishing_to_gallery"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

    @property
    def is_terminal(self) -> bool:
        return self in (
            DownloadState.COMPLETED,
            DownloadState.FAILED,
            DownloadState.CANCELLED,
        )

    @property
    def is_active(self) -> bool:
        return self in (
            DownloadState.PREPARING,
            DownloadState.DOWNLOADING,
            DownloadState.PROCESSING,
            DownloadState.PUBLISHING_TO_GALLERY,
        )

    @property
    def label(self) -> str:
        return {
            DownloadState.PENDING: "Pending",
            DownloadState.PREPARING: "Preparing",
            DownloadState.DOWNLOADING: "Downloading",
            DownloadState.PROCESSING: "Processing",
            DownloadState.PUBLISHING_TO_GALLERY: "Saving to Gallery",
            DownloadState.COMPLETED: "Completed",
            DownloadState.FAILED: "Failed",
            DownloadState.CANCELLED: "Cancelled",
        }[self]
