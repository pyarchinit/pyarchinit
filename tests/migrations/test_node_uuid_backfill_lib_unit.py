# tests/migrations/test_node_uuid_backfill_lib_unit.py
"""L0 unit tests for the PG-A migration lib refactor.

Verifies that add_columns / backfill_uuids accept either a DbHandle
or a Path (backward compat) and that PK discovery works via
SQLAlchemy Inspector across SQLite. PG path tested in
tests/sync/test_node_uuid_backfill_pg.py.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path


def _seed_db(p: Path) -> None:
    """Create the three target tables with one row each, no node_uuid yet."""
    conn = sqlite3.connect(p)
    conn.execute("CREATE TABLE us_table (id_us INTEGER PRIMARY KEY, sito TEXT)")
    conn.execute(
        "CREATE TABLE inventario_materiali_table "
        "(id_invmat INTEGER PRIMARY KEY, sito TEXT)"
    )
    conn.execute(
        "CREATE TABLE periodizzazione_table "
        "(id_perfas INTEGER PRIMARY KEY, sito TEXT)"
    )
    conn.execute("INSERT INTO us_table VALUES (1, 'S')")
    conn.execute("INSERT INTO inventario_materiali_table VALUES (1, 'S')")
    conn.execute("INSERT INTO periodizzazione_table VALUES (1, 'S')")
    conn.commit()
    conn.close()


def test_add_columns_accepts_dbhandle(tmp_path):
    """add_columns(db_handle) works with a DbHandle, not just Path."""
    from modules.s3dgraphy.sync._db_handle import DbHandle
    from scripts.migrations._2026_05_node_uuid_backfill_lib import (
        TABLES, add_columns,
    )
    db = tmp_path / "x.sqlite"
    _seed_db(db)
    handle = DbHandle.from_path(db)
    add_columns(handle)
    # Verify via the engine on the handle (not via raw sqlite3)
    from sqlalchemy import text
    with handle.engine.connect() as conn:
        for table in TABLES:
            rows = conn.execute(
                text(f"PRAGMA table_info({table})")
            ).fetchall()
            cols = {r[1] for r in rows}
            assert "node_uuid" in cols


def test_backfill_uuids_accepts_dbhandle_returns_counts(tmp_path):
    """backfill_uuids(db_handle) → returns dict[str, int] of rows updated."""
    from modules.s3dgraphy.sync._db_handle import DbHandle
    from scripts.migrations._2026_05_node_uuid_backfill_lib import (
        TABLES, add_columns, backfill_uuids,
    )
    db = tmp_path / "x.sqlite"
    _seed_db(db)
    handle = DbHandle.from_path(db)
    add_columns(handle)
    counts = backfill_uuids(handle)
    assert set(counts.keys()) == set(TABLES)
    for table in TABLES:
        assert counts[table] == 1, (
            f"expected 1 row updated for {table}, got {counts[table]}"
        )


def test_pk_discovery_via_inspector(tmp_path):
    """SQLAlchemy Inspector.get_pk_constraint returns the PK col list."""
    from sqlalchemy import create_engine, inspect, text
    db = tmp_path / "x.sqlite"
    _seed_db(db)
    engine = create_engine(f"sqlite:///{db}")
    inspector = inspect(engine)
    for table, expected_pk in [
        ("us_table", ["id_us"]),
        ("inventario_materiali_table", ["id_invmat"]),
        ("periodizzazione_table", ["id_perfas"]),
    ]:
        pk = inspector.get_pk_constraint(table)["constrained_columns"]
        assert pk == expected_pk, f"{table}: expected {expected_pk}, got {pk}"
