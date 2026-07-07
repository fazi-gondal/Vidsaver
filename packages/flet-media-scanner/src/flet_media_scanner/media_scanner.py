import flet as ft
from typing import Optional, Any

@ft.control("MediaScanner")
class MediaScanner(ft.Service):
    """
    A Flet Service that triggers Android's native MediaScannerConnection.
    """
    on_scanned: Optional[ft.EventHandler[Any]] = None

    def _is_supported_platform(self) -> bool:
        if not self.page:
            return False
        return self.page.platform == ft.PagePlatform.ANDROID

    async def scan_media(self, file_path: str) -> bool:
        """
        Scan a media file asynchronously to make it visible in the Gallery.
        """
        if not self._is_supported_platform():
            return False
        result = await self._invoke_method("scan_media", {"path": file_path})
        return result == "true"
