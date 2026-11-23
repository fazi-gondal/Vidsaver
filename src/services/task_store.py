"""SQLite persistence for download tasks (Phase 8)."""

from __future__ import annotations

import json
import logging
import sqlite3
import threading
import time
from pathlib import Path

from models.download_progress import DownloadProgress
from models.download_request import DownloadRequest
from models.download_state import DownloadState
from models.download_task import DownloadTask

logger = logging.getLogger(__name__)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS download_tasks (
    id TEXT PRIMARY KEY,
    url TEXT NOT NULL,
    title TEXT,
    platform TEXT,
    thumbnail_url TEXT,
    state TEXT NOT NULL,
    format_selector TEXT,
    output_path TEXT,
    error TEXT,
    progress_json TEXT,
    created_at REAL,
    finished_at REAL
);
CREATE INDEX IF NOT EXISTS idx_tasks_state ON download_tasks(state);
CREATE INDEX IF NOT EXISTS idx_tasks_created ON download_tasks(created_at DESC);
"""


class TaskStore:
    def __init__(self, db_path: str | Path) -> None:
        self._path = Path(db_path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self._path), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._lock:
            conn = self._connect()
            try:
                conn.executescript(_SCHEMA)
                conn.commit()
            finally:
                conn.close()

    def upsert(self, task: DownloadTask) -> None:
        fmt = ""
        extra = task.request.extra_ydl_opts or {}
        if extra.get("format"):
            fmt = str(extra["format"])
        progress = {
            "percent": task.progress.percent,
            "downloaded_bytes": task.progress.downloaded_bytes,
            "total_bytes": task.progress.total_bytes,
            "speed_bytes_per_sec": task.progress.speed_bytes_per_sec,
            "eta_seconds": task.progress.eta_seconds,
            "status_text": task.progress.status_text,
        }
        row = (
            task.id,
            task.request.url,
            task.title,
            task.platform,
            task.thumbnail_url,
            task.state.value,
            fmt,
            task.output_path,
            task.error,
            json.dumps(progress),
            task.created_at,
            task.finished_at,
        )
        with self._lock:
            conn = self._connect()
            try:
                conn.execute(
                    """
                    INSERT INTO download_tasks (
                        id, url, title, platform, thumbnail_url, state,
                        format_selector, output_path, error, progress_json,
                        created_at, finished_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        url=excluded.url,
                        title=excluded.title,
                        platform=excluded.platform,
                        thumbnail_url=excluded.thumbnail_url,
                        state=excluded.state,
                        format_selector=excluded.format_selector,
                        output_path=excluded.output_path,
                        error=excluded.error,
                        progress_json=excluded.progress_json,
                        created_at=excluded.created_at,
                        finished_at=excluded.finished_at
                    """,
                    row,
                )
                conn.commit()
            finally:
                conn.close()

    def delete(self, task_id: str) -> None:
        with self._lock:
            conn = self._connect()
            try:
                conn.execute("DELETE FROM download_tasks WHERE id = ?", (task_id,))
                conn.commit()
            finally:
                conn.close()

    def delete_terminal(self) -> int:
        with self._lock:
            conn = self._connect()
            try:
                cur = conn.execute(
                    "DELETE FROM download_tasks WHERE state IN (?, ?, ?)",
                    (
                        DownloadState.COMPLETED.value,
                        DownloadState.FAILED.value,
                        DownloadState.CANCELLED.value,
                    ),
                )
                conn.commit()
                return cur.rowcount or 0
            finally:
                conn.close()

    def load_all(self) -> list[DownloadTask]:
        with self._lock:
            conn = self._connect()
            try:
                rows = conn.execute(
                    "SELECT * FROM download_tasks ORDER BY created_at DESC"
                ).fetchall()
            finally:
                conn.close()

        tasks: list[DownloadTask] = []
        for row in rows:
            try:
                tasks.append(self._row_to_task(row))
            except Exception:
                logger.exception("Failed to restore task %s", row["id"])
        return tasks

    def _row_to_task(self, row: sqlite3.Row) -> DownloadTask:
        progress_raw = {}
        try:
            progress_raw = json.loads(row["progress_json"] or "{}")
        except json.JSONDecodeError:
            progress_raw = {}

        fmt = row["format_selector"] or ""
        request = DownloadRequest(
            url=row["url"],
            extra_ydl_opts={"format": fmt} if fmt else {},
        )
        state_val = row["state"] or DownloadState.PENDING.value
        try:
            state = DownloadState(state_val)
        except ValueError:
            state = DownloadState.FAILED

        # Active states after crash become failed so user can retry
        if state.is_active or state is DownloadState.PENDING:
            if state.is_active:
                state = DownloadState.FAILED
                error = row["error"] or "Interrupted — open Retry to resume."
            else:
                error = row["error"] or ""
        else:
            error = row["error"] or ""

        task = DownloadTask(
            request=request,
            id=row["id"],
            title=row["title"] or "",
            platform=row["platform"] or "Video",
            thumbnail_url=row["thumbnail_url"] or "",
            state=state,
            progress=DownloadProgress(
                percent=progress_raw.get("percent"),
                downloaded_bytes=int(progress_raw.get("downloaded_bytes") or 0),
                total_bytes=progress_raw.get("total_bytes"),
                speed_bytes_per_sec=progress_raw.get("speed_bytes_per_sec"),
                eta_seconds=progress_raw.get("eta_seconds"),
                status_text=progress_raw.get("status_text") or "",
            ),
            output_path=row["output_path"] or "",
            error=error,
            created_at=float(row["created_at"] or time.time()),
            finished_at=row["finished_at"],
        )
        return task
