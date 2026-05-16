"""yE-F schema migration tests — ADD COLUMN other_locations TEXT
idempotent on both SQLite and PG (PG paths skipped if psycopg2 missing)."""
from __future__ import annotations
from pathlib import Path
from sqlalchemy import text
import pytest

from modules.s3dgraphy.sync._db_handle import DbHandle, _columns_of


def _make_sqlite_handle(tmp_path: Path) -> DbHandle:
    """Build a DbHandle on a fresh SQLite DB with the minimal us_table
    schema MINUS the other_locations column (the migration target).
    """
    dbfile = tmp_path / "yef_migration.sqlite"
    handle = DbHandle.from_path(dbfile)
    with handle.engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE us_table (
                id_us INTEGER PRIMARY KEY AUTOINCREMENT,
                sito TEXT, area TEXT, us TEXT,
                unita_tipo TEXT, node_uuid TEXT,
                UNIQUE (sito, area, us, unita_tipo)
            )
        """))
    return handle


def test_add_other_locations_column_inserts_when_missing(tmp_path):
    """First call adds the column → returns 1."""
    from scripts.migrations._2026_05_yef_other_locations_lib import (
        add_other_locations_column,
    )
    handle = _make_sqlite_handle(tmp_path)
    assert "other_locations" not in _columns_of(handle.engine, "us_table")

    inserted = add_other_locations_column(handle)

    assert inserted == 1
    assert "other_locations" in _columns_of(handle.engine, "us_table")


def test_add_other_locations_column_no_op_when_present(tmp_path):
    """Second call returns 0 (idempotent)."""
    from scripts.migrations._2026_05_yef_other_locations_lib import (
        add_other_locations_column,
    )
    handle = _make_sqlite_handle(tmp_path)
    add_other_locations_column(handle)  # first call

    inserted = add_other_locations_column(handle)  # second call

    assert inserted == 0
    assert "other_locations" in _columns_of(handle.engine, "us_table")


# --- L2 PG test (skipped cleanly when PG is unreachable) ---

try:
    import psycopg2  # noqa: F401
    _HAS_PSYCOPG2 = True
except ImportError:
    _HAS_PSYCOPG2 = False

# Import pg_engine fixture explicitly - conftest_pg.py is not auto-discovered
if _HAS_PSYCOPG2:
    from tests.sync.conftest_pg import pg_engine  # noqa: F401


@pytest.mark.skipif(
    not _HAS_PSYCOPG2,
    reason="psycopg2 not installed - PG L2 test unreachable",
)
def test_add_other_locations_column_on_pg(pg_engine):
    """L2 PG: idempotent ADD COLUMN works on PostgreSQL too.

    Uses the shared ``pg_engine`` fixture from conftest_pg.py which
    is skipped automatically when PG is not reachable at the
    configured port. Mirrors the pattern from
    tests/sync/test_node_uuid_backfill_pg.py.
    """
    from scripts.migrations._2026_05_yef_other_locations_lib import (
        add_other_locations_column,
    )

    handle = DbHandle.from_engine(pg_engine, str(pg_engine.url))

    # Reset us_table to a minimal shape WITHOUT other_locations.
    with handle.engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS us_table CASCADE"))
        conn.execute(text("""
            CREATE TABLE us_table (
                id_us SERIAL PRIMARY KEY,
                sito TEXT, area TEXT, us TEXT,
                unita_tipo TEXT, node_uuid TEXT,
                UNIQUE (sito, area, us, unita_tipo)
            )
        """))

    # First call adds the column.
    assert "other_locations" not in _columns_of(handle.engine, "us_table")
    inserted = add_other_locations_column(handle)
    assert inserted == 1
    assert "other_locations" in _columns_of(handle.engine, "us_table")

    # Second call is a no-op.
    inserted_again = add_other_locations_column(handle)
    assert inserted_again == 0

    # Cleanup.
    with handle.engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS us_table CASCADE"))
