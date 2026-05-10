# tests/sync/test_node_uuid_backfill_pg.py
"""PG-A: L2 PostgreSQL tests for the node_uuid backfill migration.

Skipped cleanly when PG is unreachable at localhost:5433 or when
psycopg2 is not installed. Reuses the pg_engine session fixture from
tests/sync/conftest_pg.py (Foundation).
"""
from __future__ import annotations

import re

import pytest
from sqlalchemy import inspect, text

# Import pg_engine fixture explicitly - conftest_pg.py is not auto-discovered
from tests.sync.conftest_pg import pg_engine  # noqa: F401


UUID_V7_REGEX = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)


@pytest.fixture
def clean_pg_with_seed(pg_engine):
    """Truncate the 3 tables, insert 1 row per table with NULL node_uuid."""
    with pg_engine.begin() as conn:
        conn.execute(text(
            "TRUNCATE us_table, site_table, periodizzazione_table "
            "RESTART IDENTITY CASCADE"
        ))
        # inventario_materiali_table doesn't exist in conftest_pg's minimal
        # schema, so create it idempotently for this test module
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS inventario_materiali_table (
                id_invmat SERIAL PRIMARY KEY,
                sito TEXT,
                numero_inventario TEXT,
                node_uuid TEXT
            )
        """))
        conn.execute(text(
            "TRUNCATE inventario_materiali_table RESTART IDENTITY CASCADE"
        ))
        conn.execute(text(
            "INSERT INTO us_table (sito, area, us) VALUES ('S', '1', '1')"
        ))
        conn.execute(text(
            "INSERT INTO inventario_materiali_table (sito, numero_inventario) "
            "VALUES ('S', 'A1')"
        ))
        conn.execute(text(
            "INSERT INTO periodizzazione_table (sito, periodo, fase) "
            "VALUES ('S', 1, 'I')"
        ))
    yield pg_engine


def test_add_columns_idempotent_on_pg(clean_pg_with_seed):
    """Run #1 adds 3 columns + 3 indexes; run #2 is no-op."""
    from modules.s3dgraphy.sync._db_handle import DbHandle, _columns_of
    from scripts.migrations._2026_05_node_uuid_backfill_lib import (
        TABLES, add_columns,
    )
    handle = DbHandle.from_engine(clean_pg_with_seed,
                                   str(clean_pg_with_seed.url))
    add_columns(handle)
    for table in TABLES:
        assert "node_uuid" in _columns_of(clean_pg_with_seed, table)
    # Second run = no-op
    add_columns(handle)
    for table in TABLES:
        cols = _columns_of(clean_pg_with_seed, table)
        # Still exactly one node_uuid column (no duplicates)
        assert "node_uuid" in cols


def test_backfill_uuids_assigns_uuid7_on_pg(clean_pg_with_seed):
    """Every row has a valid UUID v7 after backfill; counts are accurate."""
    from modules.s3dgraphy.sync._db_handle import DbHandle
    from scripts.migrations._2026_05_node_uuid_backfill_lib import (
        TABLES, add_columns, backfill_uuids,
    )
    handle = DbHandle.from_engine(clean_pg_with_seed,
                                   str(clean_pg_with_seed.url))
    add_columns(handle)
    counts = backfill_uuids(handle)
    assert counts["us_table"] == 1
    assert counts["inventario_materiali_table"] == 1
    assert counts["periodizzazione_table"] == 1
    with clean_pg_with_seed.connect() as conn:
        for table in TABLES:
            rows = conn.execute(
                text(f"SELECT node_uuid FROM {table}")
            ).fetchall()
            for (val,) in rows:
                assert val is not None, f"NULL node_uuid in {table}"
                assert UUID_V7_REGEX.match(val), f"not UUID v7 in {table}: {val}"


def test_partial_unique_index_allows_null_collision(clean_pg_with_seed):
    """The WHERE node_uuid IS NOT NULL clause permits multiple NULLs.

    Required for partial-failure recovery: if add_columns succeeded on
    table A but crashed mid-backfill, a re-run must not blow up on the
    rows still carrying NULL.
    """
    from modules.s3dgraphy.sync._db_handle import DbHandle
    from scripts.migrations._2026_05_node_uuid_backfill_lib import add_columns
    handle = DbHandle.from_engine(clean_pg_with_seed,
                                   str(clean_pg_with_seed.url))
    add_columns(handle)
    # Insert two more rows with NULL node_uuid - if the index were full
    # unique, the second INSERT would raise.
    with clean_pg_with_seed.begin() as conn:
        conn.execute(text(
            "INSERT INTO us_table (sito, area, us) VALUES ('S', '1', '2')"
        ))
        conn.execute(text(
            "INSERT INTO us_table (sito, area, us) VALUES ('S', '1', '3')"
        ))
        n_null = conn.execute(text(
            "SELECT COUNT(*) FROM us_table WHERE node_uuid IS NULL"
        )).scalar()
        assert n_null == 3, f"expected 3 NULL node_uuid rows, got {n_null}"


def test_pk_discovery_on_pg_via_inspector(clean_pg_with_seed):
    """SQLAlchemy Inspector returns the declared PK column on PG."""
    inspector = inspect(clean_pg_with_seed)
    for table, expected in [
        ("us_table", ["id_us"]),
        ("periodizzazione_table", ["id_perfas"]),
        ("inventario_materiali_table", ["id_invmat"]),
    ]:
        pk = inspector.get_pk_constraint(table)["constrained_columns"]
        assert pk == expected, f"{table}: expected {expected}, got {pk}"


def test_atomic_rollback_on_alter_failure(clean_pg_with_seed, monkeypatch):
    """If text() raises mid-add_columns, engine.begin() rolls back -
    no partial column added on the second/third table."""
    from modules.s3dgraphy.sync._db_handle import DbHandle, _columns_of
    from scripts.migrations import _2026_05_node_uuid_backfill_lib as lib

    handle = DbHandle.from_engine(clean_pg_with_seed,
                                   str(clean_pg_with_seed.url))

    # Patch text() inside the lib module to raise on the second call
    # (after us_table got its column added but before inventario gets it).
    original_text = lib.text
    call_count = {"n": 0}

    def fake_text(stmt):
        call_count["n"] += 1
        if "ALTER TABLE inventario_materiali_table" in stmt:
            raise RuntimeError("simulated mid-flight failure")
        return original_text(stmt)

    monkeypatch.setattr(lib, "text", fake_text)

    with pytest.raises(RuntimeError, match="simulated mid-flight failure"):
        lib.add_columns(handle)

    # Critical assertion: us_table's ALTER must have been ROLLED BACK
    # because engine.begin() wraps the whole loop in a single transaction
    cols = _columns_of(clean_pg_with_seed, "us_table")
    assert "node_uuid" not in cols, (
        "us_table.node_uuid should NOT exist after rollback; "
        "engine.begin() failed to roll back atomically"
    )


def test_auto_backup_postgres_invokes_pg_dump(tmp_path, monkeypatch):
    """Mock subprocess.run to verify pg_dump invocation argv + env."""
    pytest.importorskip("psycopg2")
    from sqlalchemy import create_engine
    from scripts.migrations._common import auto_backup_postgres

    captured = {}

    def fake_run(cmd, env=None, timeout=None, check=False, **kw):
        captured["cmd"] = cmd
        captured["env"] = env
        # Simulate success
        class R:
            returncode = 0
            stdout = ""
            stderr = ""
        return R()

    monkeypatch.setattr("scripts.migrations._common.subprocess.run", fake_run)
    monkeypatch.setattr("shutil.which",
                        lambda name: "/usr/bin/pg_dump" if name == "pg_dump"
                        else None)

    engine = create_engine(
        "postgresql+psycopg2://postgres:secret@localhost:5433/mydb"
    )
    out = auto_backup_postgres(engine, tag="t1", dest_dir=tmp_path)

    assert captured["cmd"][0] == "/usr/bin/pg_dump"
    assert "-h" in captured["cmd"] and "localhost" in captured["cmd"]
    assert "-p" in captured["cmd"] and "5433" in captured["cmd"]
    assert "-U" in captured["cmd"] and "postgres" in captured["cmd"]
    assert "-d" in captured["cmd"] and "mydb" in captured["cmd"]
    assert "-f" in captured["cmd"]
    assert captured["env"]["PGPASSWORD"] == "secret"
    assert "PATH" in captured["env"]  # PATH propagated for pg_dump's libs
    assert tmp_path in out.parents
