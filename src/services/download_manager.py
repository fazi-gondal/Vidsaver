"""Queue + worker pool for independent download tasks.

Workers never touch Flet controls. Callers register callbacks that schedule
UI updates on the event loop (e.g. page.loop.call_soon_threadsafe).
"""

from __future__ import annotations

import logging
import os
import queue
import threading
import time
from collections.abc import Callable
from typing import Any

from models.download_progress import DownloadProgress
from models.download_request import DownloadRequest
from models.download_state import DownloadState
from models.download_task import DownloadTask

logger = logging.getLogger(__name__)

Listener = Callable[[DownloadTask], None]


class DownloadManager:
    def __init__(
        self,
        *,
        max_concurrent: int = 1,
        cookie_path: str = "cookies.txt",
        get_staging_dir: Callable[[], str] | None = None,
        on_task_changed: Listener | None = None,
        publish_result: Callable[[dict], Any] | None = None,
        task_store: Any | None = None,
        ydl_option_provider: Callable[[], dict] | None = None,
    ) -> None:
        self._max_concurrent = max(1, max_concurrent)
        self._cookie_path = cookie_path
        self._get_staging_dir = get_staging_dir or (lambda: os.getcwd())
        self._on_task_changed = on_task_changed
        self._publish_result = publish_result
        self._task_store = task_store
        self._ydl_option_provider = ydl_option_provider

        self._queue: queue.Queue[DownloadTask | None] = queue.Queue()
        self._tasks: dict[str, DownloadTask] = {}
        self._lock = threading.Lock()
        self._workers: list[threading.Thread] = []
        self._shutdown = threading.Event()
        self._last_notify_at: dict[str, float] = {}

    # ------------------------------------------------------------------ API

    def set_max_concurrent(self, n: int) -> None:
        self._max_concurrent = max(1, min(4, int(n)))
        self._ensure_workers()

    def set_callbacks(
        self,
        *,
        on_task_changed: Listener | None = None,
        publish_result: Callable[[dict], Any] | None = None,
    ) -> None:
        if on_task_changed is not None:
            self._on_task_changed = on_task_changed
        if publish_result is not None:
            self._publish_result = publish_result

    def enqueue(
        self,
        url: str,
        *,
        format_selector: str | None = None,
        title: str = "",
        platform: str = "Video",
        thumbnail_url: str = "",
    ) -> DownloadTask:
        request = DownloadRequest(
            url=url,
            extra_ydl_opts={"format": format_selector} if format_selector else {},
        )
        task = DownloadTask(
            request=request,
            title=title or url,
            platform=platform,
            thumbnail_url=thumbnail_url,
        )
        with self._lock:
            self._tasks[task.id] = task
        self._notify(task)
        self._set_state(task, DownloadState.PENDING)
        self._ensure_workers()
        self._queue.put(task)
        logger.info("Queued %s %s", task.id, url)
        return task

    def cancel(self, task_id: str) -> None:
        task = self.get(task_id)
        if task is None or task.is_terminal:
            return
        task.cancel_event.set()
        if task.state is DownloadState.PENDING:
            self._set_state(task, DownloadState.CANCELLED)

    def retry(self, task_id: str) -> DownloadTask | None:
        task = self.get(task_id)
        if task is None:
            return None
        if task.state not in (DownloadState.FAILED, DownloadState.CANCELLED):
            return None
        task.cancel_event = threading.Event()
        task.error = ""
        task.finished_at = None
        task.progress = DownloadProgress()
        self._set_state(task, DownloadState.PENDING)
        self._ensure_workers()
        self._queue.put(task)
        return task

    def get(self, task_id: str) -> DownloadTask | None:
        with self._lock:
            return self._tasks.get(task_id)

    def list_tasks(self) -> list[DownloadTask]:
        with self._lock:
            tasks = list(self._tasks.values())
        # Active first, then pending, then terminal by created_at desc
        def sort_key(t: DownloadTask):
            if t.is_active:
                return (0, -t.created_at)
            if t.state is DownloadState.PENDING:
                return (1, -t.created_at)
            return (2, -t.created_at)

        return sorted(tasks, key=sort_key)

    def active_count(self) -> int:
        return sum(1 for t in self.list_tasks() if t.is_active or t.state is DownloadState.PENDING)

    def restore_from_store(self) -> int:
        """Load tasks from SQLite. Interrupted active tasks become failed."""
        if self._task_store is None:
            return 0
        restored = self._task_store.load_all()
        count = 0
        with self._lock:
            for task in restored:
                self._tasks[task.id] = task
                count += 1
                if task.state is DownloadState.PENDING:
                    self._queue.put(task)
        if count:
            self._ensure_workers()
        logger.info("Restored %s tasks from store", count)
        return count

    def clear_finished(self) -> int:
        removed = 0
        with self._lock:
            drop = [
                tid
                for tid, t in self._tasks.items()
                if t.state
                in (
                    DownloadState.COMPLETED,
                    DownloadState.FAILED,
                    DownloadState.CANCELLED,
                )
            ]
            for tid in drop:
                self._tasks.pop(tid, None)
                removed += 1
        if self._task_store is not None:
            try:
                self._task_store.delete_terminal()
            except Exception:
                logger.exception("task_store.delete_terminal failed")
        return removed

    def shutdown(self) -> None:
        self._shutdown.set()
        for _ in self._workers:
            self._queue.put(None)

    # ------------------------------------------------------------------ internal

    def _notify(self, task: DownloadTask) -> None:
        if self._task_store is not None:
            try:
                self._task_store.upsert(task)
            except Exception:
                logger.exception("task_store.upsert failed")
        cb = self._on_task_changed
        if cb:
            try:
                cb(task)
            except Exception:
                logger.exception("on_task_changed failed")

    def _set_state(self, task: DownloadTask, state: DownloadState, *, error: str = "") -> None:
        task.mark(state, error=error)
        self._notify(task)

    def _ensure_workers(self) -> None:
        with self._lock:
            alive = [w for w in self._workers if w.is_alive()]
            self._workers = alive
            need = self._max_concurrent - len(alive)
            for i in range(max(0, need)):
                t = threading.Thread(
                    target=self._worker_loop,
                    name=f"vidsaver-dl-{i}-{time.time_ns() % 10000}",
                    daemon=True,
                )
                self._workers.append(t)
                t.start()

    def _worker_loop(self) -> None:
        from downloader import run_download

        while not self._shutdown.is_set():
            try:
                task = self._queue.get(timeout=0.5)
            except queue.Empty:
                continue
            if task is None:
                break
            if task.cancel_event.is_set() or task.state is DownloadState.CANCELLED:
                self._set_state(task, DownloadState.CANCELLED)
                continue

            self._run_one(task, run_download)

    def _run_one(self, task: DownloadTask, run_download) -> None:
        self._set_state(task, DownloadState.PREPARING)
        staging = self._get_staging_dir()
        cookie_path = self._cookie_path
        format_selector = None
        extra = task.request.extra_ydl_opts or {}
        if extra.get("format"):
            format_selector = str(extra["format"])

        def on_status(message: str) -> None:
            if task.cancel_event.is_set():
                return
            task.progress.status_text = message
            if task.state is DownloadState.PREPARING:
                self._set_state(task, DownloadState.DOWNLOADING)
            else:
                self._notify(task)

        def on_progress(value) -> None:
            if task.cancel_event.is_set():
                return
            if isinstance(value, dict):
                frac = value.get("fraction")
                if frac is not None:
                    task.progress.percent = float(frac) * 100.0
                if value.get("downloaded_bytes") is not None:
                    task.progress.downloaded_bytes = int(value["downloaded_bytes"])
                if value.get("total_bytes") is not None:
                    task.progress.total_bytes = int(value["total_bytes"])
                if value.get("speed_bytes_per_sec") is not None:
                    task.progress.speed_bytes_per_sec = float(value["speed_bytes_per_sec"])
                if value.get("eta_seconds") is not None:
                    task.progress.eta_seconds = float(value["eta_seconds"])
            else:
                task.progress.percent = float(value) * 100.0
            if task.state is not DownloadState.DOWNLOADING:
                self._set_state(task, DownloadState.DOWNLOADING)
            else:
                now = time.time()
                last = self._last_notify_at.get(task.id, 0)
                if now - last >= 0.25:
                    self._last_notify_at[task.id] = now
                    self._notify(task)

        def on_error(message: str) -> None:
            task.error = message

        def on_finish() -> None:
            pass

        class DummyPage:
            def update(self) -> None:
                pass

        if task.cancel_event.is_set():
            self._set_state(task, DownloadState.CANCELLED)
            return

        extra_opts: dict = {}
        if self._ydl_option_provider:
            try:
                extra_opts = self._ydl_option_provider() or {}
            except Exception:
                extra_opts = {}
        try:
            result = run_download(
                task.request.url,
                staging,
                cookie_path,
                "",
                on_status,
                on_progress,
                on_finish,
                on_error,
                DummyPage(),
                None,
                format_selector,
                extra_opts.get("retries"),
                extra_opts.get("concurrent_fragments"),
                extra_opts.get("rate_limit"),
                bool(extra_opts.get("writesubtitles")),
            )
        except Exception as exc:
            self._set_state(task, DownloadState.FAILED, error=str(exc))
            return

        if task.cancel_event.is_set():
            self._set_state(task, DownloadState.CANCELLED)
            return

        if task.error:
            self._set_state(task, DownloadState.FAILED, error=task.error)
            return

        if not result or not result.get("paths"):
            self._set_state(task, DownloadState.FAILED, error="Download produced no files.")
            return

        # Optional title enrichment
        if not task.title or task.title == task.request.url:
            # keep url title
            pass
        task.platform = result.get("platform") or task.platform
        paths = result.get("paths") or []
        task.output_path = paths[0] if paths else ""

        if self._publish_result:
            self._set_state(task, DownloadState.PUBLISHING_TO_GALLERY)
            try:
                published = self._publish_result(result)
                # publish may be async-incompatible; support bool/tuple return
                if published is False:
                    self._set_state(task, DownloadState.FAILED, error="Gallery publish failed.")
                    return
                if isinstance(published, tuple) and not published[0]:
                    self._set_state(
                        task,
                        DownloadState.FAILED,
                        error=str(published[1] if len(published) > 1 else "Publish failed"),
                    )
                    return
            except Exception as exc:
                self._set_state(task, DownloadState.FAILED, error=str(exc))
                return

        task.progress.percent = 100.0
        self._set_state(task, DownloadState.COMPLETED)
