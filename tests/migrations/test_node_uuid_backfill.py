"""Tests for the node_uuid backfill migration (spec §4.5).

The migration adds a ``node_uuid TEXT`` column + a partial unique index
(``WHERE node_uuid IS NOT NULL``) to ``us_table``,
``inventario_materiali_table`` and ``periodizzazione_table``, then assigns a
UUID v7 to every existing row whose ``node_uuid`` is NULL.
"""
from __future__ import annotations

import re
import sqlite3
from pathlib import Path

from scripts.migrations._2026_05_node_uuid_backfill_lib import (
    TABLES,
    add_columns,
    backfill_uuids,
)


def _seed_db(p: Path):
    """Create the three target tables with one row each, no node_uuid yet."""
    conn = sqlite3.connect(p)
    conn.execute("""
        CREATE TABLE us_table (
            id_us INTEGER PRIMARY KEY,
            sito TEXT, area TEXT, us TEXT
        )""")
    conn.execute("""
        CREATE TABLE inventario_materiali_table (
            id_invmat INTEGER PRIMARY KEY,
            sito TEXT, numero_inventario TEXT
        )""")
    conn.execute("""
        CREATE TABLE periodizzazione_table (
            id_perfas INTEGER PRIMARY KEY,
            sito TEXT, periodo TEXT
        )""")
    conn.execute("INSERT INTO us_table VALUES (1, 'S', '1', '1')")
    conn.execute("INSERT INTO us_table VALUES (2, 'S', '1', '2')")
    conn.execute("INSERT INTO inventario_materiali_table VALUES (1, 'S', 'A1')")
    conn.execute("INSERT INTO periodizzazione_table VALUES (1, 'S', 'I')")
    conn.commit()
    conn.close()


def _column_names(db: Path, table: str) -> list[str]:
    conn = sqlite3.connect(db)
    try:
        rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    finally:
        conn.close()
    return [r[1] for r in rows]


def test_add_columns_adds_node_uuid_to_each_table(tmp_path: Path):
    db = tmp_path / "x.sqlite"
    _seed_db(db)
    add_columns(db)
    for table in TABLES:
        assert "node_uuid" in _column_names(db, table)
    # Verify the partial unique index exists for each table.
    conn = sqlite3.connect(db)
    try:
        indexes = conn.execute(
            "SELECT name, sql FROM sqlite_master WHERE type='index'"
        ).fetchall()
    finally:
        conn.close()
    index_by_name = {name: sql or "" for name, sql in indexes}
    for table in TABLES:
        idx = f"ix_{table}_node_uuid"
        assert idx in index_by_name, f"missing index {idx}"
        sql = index_by_name[idx]
        assert "UNIQUE" in sql.upper()
        assert "node_uuid IS NOT NULL" in sql


def test_add_columns_idempotent(tmp_path: Path):
    db = tmp_path / "x.sqlite"
    _seed_db(db)
    add_columns(db)
    add_columns(db)  # second run must be a no-op
    for table in TABLES:
        cols = _column_names(db, table)
        assert cols.count("node_uuid") == 1


def test_backfill_assigns_uuid_v7(tmp_path: Path):
    db = tmp_path / "x.sqlite"
    _seed_db(db)
    add_columns(db)
    counts = backfill_uuids(db)
    assert counts["us_table"] == 2
    assert counts["inventario_materiali_table"] == 1
    assert counts["periodizzazione_table"] == 1
    # Every row now carries a 36-char UUID v7 (version nibble at index 14).
    pattern = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
    )
    conn = sqlite3.connect(db)
    try:
        for table in TABLES:
            rows = conn.execute(
                f"SELECT node_uuid FROM {table}").fetchall()
            for (val,) in rows:
                assert val is not None
                assert len(val) == 36
                assert pattern.match(val), f"not UUID v7: {val}"
    finally:
        conn.close()


def test_backfill_idempotent(tmp_path: Path):
    db = tmp_path / "x.sqlite"
    _seed_db(db)
    add_columns(db)
    backfill_uuids(db)
    second = backfill_uuids(db)
    for table in TABLES:
        assert second[table] == 0


def test_argv_db_and_conn_str_mutex():
    """parse_argv: --db and --conn-str cannot be passed together."""
    import pytest
    from scripts.migrations._common import parse_argv
    with pytest.raises(SystemExit):
        parse_argv(["--db", "/tmp/x.sqlite",
                    "--conn-str", "postgresql://x:y@h/d",
                    "--apply"])


def test_argv_conn_str_sqlite_accepted():
    """parse_argv: --conn-str sqlite:///... is accepted (not just PG)."""
    from scripts.migrations._common import parse_argv
    args = parse_argv(["--conn-str", "sqlite:///tmp/x.sqlite", "--apply"])
    assert args.conn_str == "sqlite:///tmp/x.sqlite"
    assert args.db is None
    assert args.apply is True


def test_auto_backup_postgres_when_pg_dump_missing(tmp_path, monkeypatch):
    """auto_backup_postgres returns None + raises BackupSkipped when
    pg_dump is missing from PATH."""
    import pytest
    pytest.importorskip("psycopg2")
    from sqlalchemy import create_engine
    from scripts.migrations._common import (
        BackupSkipped, auto_backup_postgres,
    )
    monkeypatch.setattr("shutil.which", lambda name: None)
    engine = create_engine(
        "postgresql+psycopg2://postgres:postgres@localhost:5433/dummy"
    )
    with pytest.raises(BackupSkipped):
        auto_backup_postgres(engine, tag="x", dest_dir=tmp_path)
