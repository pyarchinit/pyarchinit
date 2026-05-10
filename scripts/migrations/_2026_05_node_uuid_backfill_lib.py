"""Library for the node_uuid backfill migration (PG-A milestone).

Adds a ``node_uuid TEXT`` column + a partial unique index
(``WHERE node_uuid IS NOT NULL``) to the three Phase 1 target tables, then
assigns a UUID v7 to every existing row whose ``node_uuid`` is NULL.

Both ``add_columns`` and ``backfill_uuids`` are idempotent. Split from the
CLI script so tests can import the logic without invoking argparse.

Cross-backend (SQLite + PostgreSQL) since 5.7.0-alpha. Public API accepts
either a ``DbHandle`` or a legacy ``Path`` (backward compat) via the
``_resolve_db_handle()`` shim from Foundation.
"""
from __future__ import annotations

from pathlib import Path
from typing import Union

from sqlalchemy import inspect, text

from modules.s3dgraphy.sync._db_handle import (
    DbHandle, _columns_of, _resolve_db_handle,
)
from modules.s3dgraphy.sync.uuid7 import uuid7

#: Tables that need a stable node identity for the s3dgraphy bridge.
TABLES: tuple[str, ...] = (
    "us_table",
    "inventario_materiali_table",
    "periodizzazione_table",
)

#: Type alias for the public migration API.
#: NOTE: ``_resolve_db_handle()`` itself accepts more (``str`` conn-strings,
#: SQLAlchemy ``Engine``, any DbManager-shaped object). ``DbInput`` is
#: deliberately narrowed to the two shapes the migration scripts and tests
#: actually pass; widen here when a caller needs more.
DbInput = Union[DbHandle, Path]


def add_columns(db: DbInput) -> None:
    """Add ``node_uuid TEXT`` + partial unique index on each target table.

    The partial unique index uses ``WHERE node_uuid IS NOT NULL`` so that
    multiple NULLs do not collide during a partial-failure recovery (we may
    add the column on N tables but only finish backfilling N-1 before a
    crash; rolling forward must not be blocked by spurious uniqueness
    violations on the unfilled rows).

    Accepts a ``DbHandle`` or a legacy ``Path`` (resolved via the
    ``_resolve_db_handle`` shim). ``engine.begin()`` provides DML
    atomicity on both backends and DDL atomicity on PostgreSQL only;
    SQLite executes ``ALTER TABLE`` outside the transaction so a
    crash mid-loop leaves any already-added columns in place. The
    ``_columns_of`` guard makes a re-run safe (idempotent), and the
    partial unique index allows recovery from partial backfill.
    """
    handle = _resolve_db_handle(db)
    with handle.engine.begin() as conn:
        for table in TABLES:
            cols = _columns_of(handle.engine, table)
            if "node_uuid" not in cols:
                conn.execute(
                    text(f"ALTER TABLE {table} ADD COLUMN node_uuid TEXT")
                )
            conn.execute(text(
                f"CREATE UNIQUE INDEX IF NOT EXISTS "
                f"ix_{table}_node_uuid ON {table}(node_uuid) "
                f"WHERE node_uuid IS NOT NULL"
            ))


def backfill_uuids(db: DbInput) -> dict[str, int]:
    """Assign ``uuid7()`` to every NULL ``node_uuid``; return per-table counts.

    Idempotent: a second invocation returns ``{table: 0, ...}`` because every
    row now carries a value. Atomic via SQLAlchemy ``engine.begin()``.
    """
    handle = _resolve_db_handle(db)
    counts: dict[str, int] = {}
    inspector = inspect(handle.engine)
    with handle.engine.begin() as conn:
        for table in TABLES:
            pks = inspector.get_pk_constraint(table)["constrained_columns"]
            if pks:
                pk_col = pks[0]
            elif handle.is_postgres:
                # PG has no rowid fallback — every pyarchinit table has a PK
                # by design, but defend explicitly.
                raise RuntimeError(
                    f"{table}: no primary key declared on PostgreSQL — "
                    "cannot backfill safely"
                )
            else:
                pk_col = "rowid"
            rows = conn.execute(
                text(f"SELECT {pk_col} FROM {table} WHERE node_uuid IS NULL")
            ).fetchall()
            for (row_id,) in rows:
                conn.execute(
                    text(f"UPDATE {table} SET node_uuid = :uuid "
                         f"WHERE {pk_col} = :id"),
                    {"uuid": str(uuid7()), "id": row_id},
                )
            counts[table] = len(rows)
    return counts
