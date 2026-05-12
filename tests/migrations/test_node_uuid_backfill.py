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


# ---------------------------------------------------------------------
# PG-UUIDFix (5.7.8.1-alpha) regression tests
# ---------------------------------------------------------------------

def test_canonical_pk_mapping_covers_all_target_tables():
    """``_CANONICAL_PK`` must declare a column for every entry in
    ``TABLES``. PG-UUIDFix depends on this mapping when a legacy PG
    dump lacks the ``PRIMARY KEY`` constraint declared by the
    SQLAlchemy structures."""
    from scripts.migrations._2026_05_node_uuid_backfill_lib import (
        _CANONICAL_PK,
    )
    for table in TABLES:
        assert table in _CANONICAL_PK, (
            f"{table} missing from _CANONICAL_PK — backfill_uuids "
            f"cannot auto-add PRIMARY KEY on legacy PG dumps without it"
        )
        assert _CANONICAL_PK[table].startswith("id_"), (
            f"_CANONICAL_PK[{table!r}] = {_CANONICAL_PK[table]!r} "
            f"breaks the id_<short> convention"
        )


def test_backfill_auto_pk_source_inspection():
    """Source-inspection guard: confirm the PG branch of
    ``backfill_uuids`` auto-adds the PRIMARY KEY constraint and runs
    the duplicate-check that protects against silently dropping
    rows. Belt-and-braces for the L2 PG fixture which may not run
    in every environment."""
    import inspect
    from scripts.migrations import _2026_05_node_uuid_backfill_lib as lib
    src = inspect.getsource(lib.backfill_uuids)
    assert "ADD CONSTRAINT" in src, (
        "PG-UUIDFix auto-PK ALTER TABLE missing from backfill_uuids"
    )
    assert "PRIMARY KEY" in src
    assert "HAVING COUNT(*) > 1" in src, (
        "duplicate-pk-value check missing — auto-adding the constraint "
        "would crash on dupes"
    )
    assert "no primary key declared on PostgreSQL" in src, (
        "fallback error message removed — should still raise when no "
        "canonical id column is available"
    )


def test_backfill_pg_legacy_schema_auto_adds_pk():
    """L2 integration: simulate a legacy PG dump where
    ``periodizzazione_table`` has no ``PRIMARY KEY``. ``backfill_uuids``
    must (a) auto-add ``periodizzazione_table_pkey`` on ``id_perfas``
    and (b) populate ``node_uuid``. Skips cleanly when PG offline or
    psycopg2 missing.

    Uses an isolated PG engine (NOT the shared ``pg_engine`` fixture)
    so the schema mutation doesn't bleed into other tests."""
    import pytest
    pytest.importorskip("psycopg2")
    from sqlalchemy import create_engine, inspect as sa_inspect, text
    PG_CONN_STR = (
        "postgresql+psycopg2://postgres:postgres@localhost:5433/"
        "pyarchinit_test_pg"
    )
    try:
        engine = create_engine(PG_CONN_STR)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        pytest.skip(f"PG unreachable: {e}")

    test_table = "periodizzazione_table_legacy_uuidfix"
    try:
        with engine.begin() as conn:
            conn.execute(text(f"DROP TABLE IF EXISTS {test_table}"))
            # No PRIMARY KEY — mimics khutm2.sql legacy dump shape.
            conn.execute(text(f"""
                CREATE TABLE {test_table} (
                    id_perfas BIGINT NOT NULL,
                    sito TEXT,
                    periodo INTEGER,
                    fase TEXT
                )
            """))
            conn.execute(text(
                f"INSERT INTO {test_table} (id_perfas, sito, periodo, fase) "
                "VALUES (1, 'S', 1, 'I'), (2, 'S', 2, 'II')"
            ))

        # Patch TABLES + _CANONICAL_PK to point at the throwaway table
        # so we exercise the auto-PK branch without disturbing the
        # shared fixture's periodizzazione_table.
        from unittest.mock import patch
        from scripts.migrations import (
            _2026_05_node_uuid_backfill_lib as lib,
        )
        from modules.s3dgraphy.sync._db_handle import DbHandle
        handle = DbHandle.from_engine(engine, PG_CONN_STR)

        with patch.object(lib, "TABLES", (test_table,)), \
             patch.dict(lib._CANONICAL_PK, {test_table: "id_perfas"}):
            lib.add_columns(handle)
            counts = lib.backfill_uuids(handle)

        assert counts[test_table] == 2, (
            f"expected 2 rows backfilled, got {counts[test_table]}"
        )

        inspector = sa_inspect(engine)
        pk = inspector.get_pk_constraint(test_table)["constrained_columns"]
        assert pk == ["id_perfas"], (
            f"PRIMARY KEY not added: get_pk_constraint returned {pk}"
        )

        with engine.connect() as conn:
            rows = conn.execute(
                text(f"SELECT id_perfas, node_uuid FROM {test_table} "
                     "ORDER BY id_perfas")
            ).fetchall()
        assert len(rows) == 2
        for (_id, node_uuid) in rows:
            assert node_uuid is not None
            assert len(node_uuid) == 36

    finally:
        with engine.begin() as conn:
            conn.execute(text(f"DROP TABLE IF EXISTS {test_table}"))


def test_auto_backup_postgres_default_timeout_is_1800s():
    """PG-UUIDFix follow-up: ``auto_backup_postgres`` default timeout
    must be 30 minutes, not the old 300 seconds that aborted the
    user's khutm2 backup on a remote PG (2026-05-12).
    Source-inspection guard."""
    import inspect
    from scripts.migrations import _common
    src = inspect.getsource(_common)
    assert "_DEFAULT_PG_DUMP_TIMEOUT_SECONDS = 1800" in src, (
        "default pg_dump timeout regression — must stay 1800s"
    )
    assert "PYARCHINIT_PG_DUMP_TIMEOUT" in src, (
        "env-var override missing — power users on huge DBs can't tune"
    )


def test_auto_backup_postgres_env_override(monkeypatch, tmp_path):
    """PG-UUIDFix follow-up: ``PYARCHINIT_PG_DUMP_TIMEOUT`` env var
    overrides the default timeout. Passing ``timeout`` kwarg takes
    precedence over the env var.

    Uses a SQLite URL for the SQLAlchemy ``Engine`` (the function only
    reads URL fields, doesn't connect) so the test runs without
    requiring psycopg2 to be installed locally."""
    from sqlalchemy import create_engine
    from scripts.migrations._common import (
        auto_backup_postgres,
        _DEFAULT_PG_DUMP_TIMEOUT_SECONDS,
    )
    import subprocess

    # The default must be 30 minutes regardless of monkeypatching the
    # env var (sanity).
    assert _DEFAULT_PG_DUMP_TIMEOUT_SECONDS == 1800

    captured = {}

    def fake_run(cmd, **kwargs):
        captured["timeout"] = kwargs.get("timeout")
        class P:
            returncode = 0
            stderr = ""
        return P()

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr("shutil.which", lambda name: "/usr/bin/pg_dump")
    engine = create_engine("sqlite:///:memory:")

    # 1) No env var → default 1800.
    monkeypatch.delenv("PYARCHINIT_PG_DUMP_TIMEOUT", raising=False)
    auto_backup_postgres(engine, tag="x", dest_dir=tmp_path)
    assert captured["timeout"] == 1800

    # 2) Env var set → use it.
    monkeypatch.setenv("PYARCHINIT_PG_DUMP_TIMEOUT", "3600")
    auto_backup_postgres(engine, tag="x", dest_dir=tmp_path)
    assert captured["timeout"] == 3600

    # 3) Explicit kwarg takes precedence over env var.
    auto_backup_postgres(engine, tag="x", dest_dir=tmp_path, timeout=900)
    assert captured["timeout"] == 900

    # 4) Garbage env var falls back to default.
    monkeypatch.setenv("PYARCHINIT_PG_DUMP_TIMEOUT", "garbage")
    auto_backup_postgres(engine, tag="x", dest_dir=tmp_path)
    assert captured["timeout"] == 1800


def test_auto_backup_postgres_timeout_raises_skipped(monkeypatch, tmp_path):
    """When pg_dump exceeds the timeout, the function must raise
    ``BackupSkipped`` with a helpful message naming
    ``PYARCHINIT_PG_DUMP_TIMEOUT`` and cleanup the partial .sql file.

    Uses a SQLite engine URL for ``create_engine`` (the function only
    reads URL fields, doesn't connect) so the test runs in non-PG
    environments too."""
    import pytest
    from sqlalchemy import create_engine
    from scripts.migrations._common import (
        BackupSkipped, auto_backup_postgres,
    )
    import subprocess

    def fake_run(cmd, **kwargs):
        # Touch the output file to simulate a partial pg_dump write,
        # then raise TimeoutExpired so the cleanup path runs.
        out_path = Path(cmd[cmd.index("-f") + 1])
        out_path.write_text("partial garbage\n")
        raise subprocess.TimeoutExpired(cmd, timeout=kwargs.get("timeout"))

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr("shutil.which", lambda name: "/usr/bin/pg_dump")
    engine = create_engine("sqlite:///:memory:")

    with pytest.raises(BackupSkipped, match="PYARCHINIT_PG_DUMP_TIMEOUT"):
        auto_backup_postgres(engine, tag="x", dest_dir=tmp_path, timeout=1)

    # Partial dump must be cleaned up so a future retry doesn't see a
    # half-written .sql we can't trust.
    leftovers = list(tmp_path.glob("*.pre_x_*"))
    assert leftovers == [], (
        f"partial pg_dump output not cleaned up: {leftovers}"
    )


def test_backfill_pg_legacy_rejects_duplicate_ids():
    """L2 integration: legacy PG dump with duplicate ``id_perfas``
    values cannot be auto-PK'd safely. ``backfill_uuids`` must raise
    a clear ``RuntimeError`` naming the duplicate sample, NOT silently
    drop or corrupt data."""
    import pytest
    pytest.importorskip("psycopg2")
    from sqlalchemy import create_engine, text
    PG_CONN_STR = (
        "postgresql+psycopg2://postgres:postgres@localhost:5433/"
        "pyarchinit_test_pg"
    )
    try:
        engine = create_engine(PG_CONN_STR)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        pytest.skip(f"PG unreachable: {e}")

    test_table = "periodizzazione_table_dupes_uuidfix"
    try:
        with engine.begin() as conn:
            conn.execute(text(f"DROP TABLE IF EXISTS {test_table}"))
            conn.execute(text(f"""
                CREATE TABLE {test_table} (
                    id_perfas BIGINT,
                    sito TEXT
                )
            """))
            conn.execute(text(
                f"INSERT INTO {test_table} VALUES (1, 'S'), (1, 'S'), (2, 'T')"
            ))

        from unittest.mock import patch
        from scripts.migrations import (
            _2026_05_node_uuid_backfill_lib as lib,
        )
        from modules.s3dgraphy.sync._db_handle import DbHandle
        handle = DbHandle.from_engine(engine, PG_CONN_STR)

        with patch.object(lib, "TABLES", (test_table,)), \
             patch.dict(lib._CANONICAL_PK, {test_table: "id_perfas"}):
            lib.add_columns(handle)
            with pytest.raises(RuntimeError, match="duplicate values"):
                lib.backfill_uuids(handle)

    finally:
        with engine.begin() as conn:
            conn.execute(text(f"DROP TABLE IF EXISTS {test_table}"))
