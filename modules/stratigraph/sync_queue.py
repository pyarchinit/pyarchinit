# -*- coding: utf-8 -*-
"""
Persistent sync queue for StratiGraph bundles.

Uses a dedicated SQLite database to store bundle upload jobs.
Thread-safe: each operation opens its own connection.
"""
import json
import os
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Optional

from qgis.core import QgsMessageLog, Qgis

TAG = "StratiGraph"
MAX_ATTEMPTS = 5

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS sync_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bundle_path TEXT NOT NULL,
    bundle_hash TEXT NOT NULL,
    created_at TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('pending','uploading','completed','failed')),
    attempts INTEGER DEFAULT 0,
    last_attempt_at TEXT,
    last_error TEXT,
    metadata TEXT
);
"""


@dataclass
class QueueEntry:
    id: int
    bundle_path: str
    bundle_hash: str
    created_at: str
    status: str
    attempts: int = 0
    last_attempt_at: Optional[str] = None
    last_error: Optional[str] = None
    metadata: dict = field(default_factory=dict)


def _row_to_entry(row: sqlite3.Row) -> QueueEntry:
    """Convert a sqlite3.Row to a QueueEntry."""
    meta = row["metadata"]
    try:
        meta_dict = json.loads(meta) if meta else {}
    except (json.JSONDecodeError, TypeError):
        meta_dict = {}
    return QueueEntry(
        id=row["id"],
        bundle_path=row["bundle_path"],
        bundle_hash=row["bundle_hash"],
        created_at=row["created_at"],
        status=row["status"],
        attempts=row["attempts"],
        last_attempt_at=row["last_attempt_at"],
        last_error=row["last_error"],
        metadata=meta_dict,
    )


class SyncQueue:
    """Persistent FIFO queue backed by SQLite.

    Default database location:
        ``$PYARCHINIT_HOME/stratigraph_sync_queue.sqlite``
    """

    def __init__(self, db_path: str = None):
        if db_path is None:
            home = os.environ.get("PYARCHINIT_HOME", "")
            db_path = os.path.join(home, "stratigraph_sync_queue.sqlite")
        self._db_path = db_path
        self._ensure_schema()

    # -- connection helper ---------------------------------------------------

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        return conn

    def _ensure_schema(self):
        conn = self._connect()
        try:
            conn.execute(CREATE_TABLE_SQL)
            conn.commit()
        finally:
            conn.close()

    # -- public API ----------------------------------------------------------

    def enqueue(self, bundle_path: str, bundle_hash: str,
                metadata: dict = None) -> int:
        """Add a bundle to the queue. Returns the new entry id."""
        now = datetime.now(timezone.utc).isoformat()
        meta_json = json.dumps(metadata) if metadata else None
        conn = self._connect()
        try:
            cur = conn.execute(
                "INSERT INTO sync_queue "
                "(bundle_path, bundle_hash, created_at, status, attempts, metadata) "
                "VALUES (?, ?, ?, 'pending', 0, ?)",
                (bundle_path, bundle_hash, now, meta_json))
            conn.commit()
            entry_id = cur.lastrowid
            QgsMessageLog.logMessage(
                f"Bundle enqueued: id={entry_id}, path={bundle_path}",
                TAG, Qgis.MessageLevel.Info)
            return entry_id
        finally:
            conn.close()

    def dequeue(self) -> Optional[QueueEntry]:
        """Take the oldest pending entry and mark it 'uploading'.

        Returns None if no pending entries exist.
        """
        now = datetime.now(timezone.utc).isoformat()
        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT * FROM sync_queue WHERE status = 'pending' "
                "ORDER BY created_at ASC LIMIT 1").fetchone()
            if row is None:
                return None
            conn.execute(
                "UPDATE sync_queue SET status = 'uploading', "
                "last_attempt_at = ?, attempts = attempts + 1 "
                "WHERE id = ?", (now, row["id"]))
            conn.commit()
            # Re-read updated row
            updated = conn.execute(
                "SELECT * FROM sync_queue WHERE id = ?",
                (row["id"],)).fetchone()
            return _row_to_entry(updated)
        finally:
            conn.close()

    def mark_completed(self, entry_id: int):
        """Mark an entry as completed."""
        conn = self._connect()
        try:
            conn.execute(
                "UPDATE sync_queue SET status = 'completed' WHERE id = ?",
                (entry_id,))
            conn.commit()
            QgsMessageLog.logMessage(
                f"Bundle completed: id={entry_id}", TAG, Qgis.MessageLevel.Info)
        finally:
            conn.close()

    def mark_failed(self, entry_id: int, error: str):
        """Mark an entry as failed.

        If attempts < MAX_ATTEMPTS, status reverts to 'pending' for retry.
        Otherwise it stays 'failed'.
        """
        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT attempts FROM sync_queue WHERE id = ?",
                (entry_id,)).fetchone()
            if row is None:
                return
            new_status = "pending" if row["attempts"] < MAX_ATTEMPTS else "failed"
            conn.execute(
                "UPDATE sync_queue SET status = ?, last_error = ? WHERE id = ?",
                (new_status, error, entry_id))
            conn.commit()
            QgsMessageLog.logMessage(
                f"Bundle failed: id={entry_id}, attempts={row['attempts']}, "
                f"new_status={new_status}, error={error}",
                TAG, Qgis.MessageLevel.Warning)
        finally:
            conn.close()

    def retry_failed(self, entry_id: int):
        """Reset a failed entry back to pending."""
        conn = self._connect()
        try:
            conn.execute(
                "UPDATE sync_queue SET status = 'pending', last_error = NULL "
                "WHERE id = ? AND status = 'failed'",
                (entry_id,))
            conn.commit()
        finally:
            conn.close()

    def get_pending(self) -> list:
        """Return all pending entries ordered by creation time."""
        conn = self._connect()
        try:
            rows = conn.execute(
                "SELECT * FROM sync_queue WHERE status = 'pending' "
                "ORDER BY created_at ASC").fetchall()
            return [_row_to_entry(r) for r in rows]
        finally:
            conn.close()

    def get_all(self) -> list:
        """Return all entries ordered by creation time (newest first)."""
        conn = self._connect()
        try:
            rows = conn.execute(
                "SELECT * FROM sync_queue ORDER BY created_at DESC"
            ).fetchall()
            return [_row_to_entry(r) for r in rows]
        finally:
            conn.close()

    def cleanup_completed(self, older_than_days: int = 7):
        """Remove completed entries older than *older_than_days*."""
        cutoff = (datetime.now(timezone.utc) -
                  timedelta(days=older_than_days)).isoformat()
        conn = self._connect()
        try:
            cur = conn.execute(
                "DELETE FROM sync_queue "
                "WHERE status = 'completed' AND created_at < ?",
                (cutoff,))
            conn.commit()
            if cur.rowcount > 0:
                QgsMessageLog.logMessage(
                    f"Cleaned up {cur.rowcount} completed entries",
                    TAG, Qgis.MessageLevel.Info)
        finally:
            conn.close()

    def get_stats(self) -> dict:
        """Return counts by status."""
        conn = self._connect()
        try:
            rows = conn.execute(
                "SELECT status, COUNT(*) as cnt FROM sync_queue "
                "GROUP BY status").fetchall()
            stats = {"pending": 0, "uploading": 0,
                     "completed": 0, "failed": 0}
            for r in rows:
                stats[r["status"]] = r["cnt"]
            return stats
        finally:
            conn.close()
