"""Library for the node_uuid backfill migration (spec §4.5).

Adds a ``node_uuid TEXT`` column + a partial unique index
(``WHERE node_uuid IS NOT NULL``) to the three Phase 1 target tables, then
assigns a UUID v7 to every existing row whose ``node_uuid`` is NULL.

Both ``add_columns`` and ``backfill_uuids`` are idempotent. Split from the
CLI script so tests can import the logic without invoking argparse.

PostgreSQL path: same logic via SQLAlchemy ``text()`` will land in Phase 2
when the GraphProjector ships; for now SQLite-only (Phase 1).
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

from modules.s3dgraphy.sync.uuid7 import uuid7

#: Tables that need a stable node identity for the s3dgraphy bridge.
TABLES: tuple[str, ...] = (
    "us_table",
    "inventario_materiali_table",
    "periodizzazione_table",
)


def _has_column(conn: sqlite3.Connection, table: str, col: str) -> bool:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return any(r[1] == col for r in rows)


def add_columns(db_path: Path) -> None:
    """Add ``node_uuid TEXT`` + partial unique index on each target table.

    The partial unique index uses ``WHERE node_uuid IS NOT NULL`` so that
    multiple NULLs do not collide during a partial-failure recovery (we may
    add the column on N tables but only finish backfilling N-1 before a
    crash; rolling forward must not be blocked by spurious uniqueness
    violations on the unfilled rows).
    """
    db_path = Path(db_path)
    conn = sqlite3.connect(db_path)
    try:
        for table in TABLES:
            if not _has_column(conn, table, "node_uuid"):
                conn.execute(
                    f"ALTER TABLE {table} ADD COLUMN node_uuid TEXT")
            conn.execute(
                f"CREATE UNIQUE INDEX IF NOT EXISTS "
                f"ix_{table}_node_uuid ON {table}(node_uuid) "
                f"WHERE node_uuid IS NOT NULL"
            )
        conn.commit()
    finally:
        conn.close()


def backfill_uuids(db_path: Path) -> dict[str, int]:
    """Assign ``uuid7()`` to every NULL ``node_uuid``; return per-table counts."""
    db_path = Path(db_path)
    counts: dict[str, int] = {}
    conn = sqlite3.connect(db_path)
    try:
        for table in TABLES:
            # Discover the table's PK column. Most pyarchinit tables follow
            # the ``id_<short>`` convention; rely on PRAGMA so the migration
            # works for any of them.
            pk_col = None
            for cid, name, _ctype, _nn, _dflt, pk in conn.execute(
                    f"PRAGMA table_info({table})").fetchall():
                if pk:
                    pk_col = name
                    break
            if pk_col is None:
                # Fall back to rowid if no declared PK.
                pk_col = "rowid"

            ids = conn.execute(
                f"SELECT {pk_col} FROM {table} WHERE node_uuid IS NULL"
            ).fetchall()
            for (row_id,) in ids:
                conn.execute(
                    f"UPDATE {table} SET node_uuid = ? WHERE {pk_col} = ?",
                    (str(uuid7()), row_id),
                )
            counts[table] = len(ids)
        conn.commit()
    finally:
        conn.close()
    return counts
