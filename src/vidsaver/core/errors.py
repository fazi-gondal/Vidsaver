"""Application-specific exceptions."""


class DownloadError(Exception):
    """Raised when a download fails for a user-visible reason."""


class MediaStoreError(Exception):
    """Raised when Android MediaStore operations fail."""
