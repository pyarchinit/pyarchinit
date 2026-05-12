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

#: Canonical primary key column per target table, as declared in the
#: pyarchinit SQLAlchemy structures (``modules/db/structures/*.py``).
#: Used by ``backfill_uuids`` to auto-add a missing ``PRIMARY KEY``
#: constraint on legacy PostgreSQL dumps that were created from older
#: schema definitions or via paths that lost the constraint
#: (PG-UUIDFix 5.7.8.1-alpha — legacy dumps like ``khutm2.sql`` lacked
#: ``periodizzazione_table_pkey``).
_CANONICAL_PK: dict[str, str] = {
    "us_table": "id_us",
    "inventario_materiali_table": "id_invmat",
    "periodizzazione_table": "id_perfas",
}

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
                # PG-UUIDFix (5.7.8.1-alpha): legacy PG dumps may lack the
                # PRIMARY KEY constraint that the pyarchinit SQLAlchemy
                # schema declares (e.g. ``khutm2.sql`` from a pre-2018
                # template). Auto-add it before the backfill: look up the
                # canonical id column for the table, verify there are no
                # duplicate values (which would block the constraint),
                # then ``ALTER TABLE ... ADD PRIMARY KEY``. All inside
                # the same ``engine.begin()`` so PG-A's auto-backup
                # protects the user on failure.
                pk_col = _CANONICAL_PK.get(table)
                if pk_col is None or pk_col not in _columns_of(
                        handle.engine, table):
                    raise RuntimeError(
                        f"{table}: no primary key declared on PostgreSQL "
                        f"and no canonical id column found — cannot "
                        f"backfill safely"
                    )
                dupes = conn.execute(
                    text(f"SELECT {pk_col} FROM {table} "
                         f"GROUP BY {pk_col} HAVING COUNT(*) > 1 "
                         f"ORDER BY {pk_col} LIMIT 5")
                ).fetchall()
                if dupes:
                    sample = ", ".join(str(r[0]) for r in dupes)
                    raise RuntimeError(
                        f"{table}: column {pk_col} has duplicate values "
                        f"(sample: {sample}) — cannot auto-add PRIMARY "
                        f"KEY. Resolve duplicates manually then re-run."
                    )
                conn.execute(text(
                    f"ALTER TABLE {table} ADD CONSTRAINT "
                    f"{table}_pkey PRIMARY KEY ({pk_col})"
                ))
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
