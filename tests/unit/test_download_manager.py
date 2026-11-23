import unittest

from models.download_state import DownloadState
from services.download_manager import DownloadManager


class DownloadManagerTests(unittest.TestCase):
    def test_cancel_and_retry(self):
        manager = DownloadManager(max_concurrent=1)
        task = manager.enqueue("https://example.com/video", title="Example")

        manager.cancel(task.id)
        self.assertEqual(DownloadState.CANCELLED, task.state)

        retried = manager.retry(task.id)
        self.assertIsNotNone(retried)
        self.assertEqual(DownloadState.PENDING, retried.state)

    def test_clear_finished_removes_terminal_tasks_only(self):
        manager = DownloadManager(max_concurrent=1)
        active = manager.enqueue("https://example.com/active")
        terminal = manager.enqueue("https://example.com/terminal")
        manager.cancel(terminal.id)

        removed = manager.clear_finished()

        self.assertEqual(1, removed)
        self.assertIsNotNone(manager.get(active.id))
        self.assertIsNone(manager.get(terminal.id))


if __name__ == "__main__":
    unittest.main()
