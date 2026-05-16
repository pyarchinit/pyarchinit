"""Library for the yE-F other_locations migration (idempotent ADD COLUMN).

The library accepts a DbHandle (Foundation 5.6.2-alpha shim) so it
works transparently on both SQLite and PostgreSQL. Backwards-compat
is preserved: pre-migration DBs have no column → reader handles
absence gracefully via try/except in graph_projector.
"""
from __future__ import annotations

from sqlalchemy import text

from modules.s3dgraphy.sync._db_handle import DbHandle, _columns_of


def add_other_locations_column(handle: DbHandle) -> int:
    """Add ``us_table.other_locations TEXT`` if not already present.

    Returns ``1`` if the column was added, ``0`` if it was already
    present (idempotent re-run).
    """
    if "other_locations" in _columns_of(handle.engine, "us_table"):
        return 0
    with handle.engine.begin() as conn:
        conn.execute(text(
            "ALTER TABLE us_table ADD COLUMN other_locations TEXT"
        ))
    return 1
