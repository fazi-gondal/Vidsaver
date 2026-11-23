import tempfile
import unittest

from models.download_progress import DownloadProgress
from models.download_request import DownloadRequest
from models.download_state import DownloadState
from models.download_task import DownloadTask
from services.task_store import TaskStore


class TaskStoreTests(unittest.TestCase):
    def test_pending_task_restores_and_is_requeued(self):
        with tempfile.TemporaryDirectory() as directory:
            store = TaskStore(directory + "/downloads.db")
            task = DownloadTask(
                request=DownloadRequest(url="https://example.com/video"),
                title="Example",
                state=DownloadState.PENDING,
            )
            store.upsert(task)

            restored = store.load_all()

            self.assertEqual(1, len(restored))
            self.assertEqual(DownloadState.PENDING, restored[0].state)

    def test_active_task_becomes_failed_for_retry(self):
        with tempfile.TemporaryDirectory() as directory:
            store = TaskStore(directory + "/downloads.db")
            task = DownloadTask(
                request=DownloadRequest(url="https://example.com/video"),
                state=DownloadState.DOWNLOADING,
                progress=DownloadProgress(percent=42.0),
            )
            store.upsert(task)

            restored = store.load_all()

            self.assertEqual(DownloadState.FAILED, restored[0].state)
            self.assertIn("Interrupted", restored[0].error)


if __name__ == "__main__":
    unittest.main()
