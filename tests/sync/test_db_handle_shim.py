# tests/sync/test_db_handle_shim.py
"""PG-Compat Foundation: unit tests for the DbHandle dataclass (Group A).

Group B will append tests for the `_resolve_db_handle` shim, and
Group C will append tests for the `_columns_of` introspection helper.
"""
from __future__ import annotations

from pathlib import Path

import pytest


def test_db_handle_is_frozen_dataclass():
    """DbHandle must be immutable (frozen=True)."""
    from s3dgraphy.sync._db_handle import DbHandle
    from sqlalchemy import create_engine
    eng = create_engine("sqlite:///:memory:")
    h = DbHandle(engine=eng, is_postgres=False, sqlite_path=None,
                 conn_str="sqlite:///:memory:")
    with pytest.raises(Exception):  # FrozenInstanceError or AttributeError
        h.engine = None  # type: ignore[misc]


def test_db_handle_from_path_creates_sqlite_engine(tmp_path):
    """from_path() builds a SQLite engine and records the Path."""
    from s3dgraphy.sync._db_handle import DbHandle
    p = tmp_path / "dummy.sqlite"
    p.touch()
    h = DbHandle.from_path(p)
    assert h.is_postgres is False
    assert h.sqlite_path == p
    assert h.conn_str == f"sqlite:///{p}"
    # Engine works
    from sqlalchemy import text
    with h.engine.connect() as conn:
        assert conn.execute(text("SELECT 1")).scalar() == 1


def test_db_handle_from_engine_detects_postgres():
    """from_engine() honours the dialect (sqlite vs postgresql)."""
    from s3dgraphy.sync._db_handle import DbHandle
    from sqlalchemy import create_engine
    sqlite_eng = create_engine("sqlite:///:memory:")
    h_sqlite = DbHandle.from_engine(sqlite_eng, "sqlite:///:memory:")
    assert h_sqlite.is_postgres is False
    assert h_sqlite.sqlite_path is None  # in-memory has no path


def test_resolve_from_path(tmp_path):
    """Path → SQLite engine via shim, with DeprecationWarning."""
    from s3dgraphy.sync._db_handle import _resolve_db_handle
    p = tmp_path / "x.sqlite"
    p.touch()
    with pytest.warns(DeprecationWarning):
        h = _resolve_db_handle(p)
    assert h.is_postgres is False
    assert h.sqlite_path == p


def test_resolve_from_sqlite_conn_str(tmp_path):
    """str starting with 'sqlite:' → engine."""
    from s3dgraphy.sync._db_handle import _resolve_db_handle
    h = _resolve_db_handle("sqlite:///:memory:")
    assert h.is_postgres is False


def test_resolve_from_postgresql_conn_str():
    """str starting with 'postgresql:' → engine (PG dialect detected).

    Skipped when psycopg2 is not installed: SQLAlchemy 1.4 eagerly imports
    the DBAPI driver at create_engine() time, so this test requires
    psycopg2 in the env. Group E adds psycopg2-binary to requirements.txt.
    """
    pytest.importorskip("psycopg2")
    from s3dgraphy.sync._db_handle import _resolve_db_handle
    h = _resolve_db_handle("postgresql+psycopg2://x:y@localhost/z")
    assert h.is_postgres is True
    assert h.sqlite_path is None


def test_resolve_from_db_manager():
    """DbManager → use existing .engine attribute."""
    from s3dgraphy.sync._db_handle import _resolve_db_handle
    from sqlalchemy import create_engine

    class FakeDbManager:
        engine = create_engine("sqlite:///:memory:")
        conn_str = "sqlite:///:memory:"

    h = _resolve_db_handle(FakeDbManager())
    assert h.is_postgres is False
    assert h.engine is FakeDbManager.engine


def test_resolve_from_engine():
    """SQLAlchemy Engine → wrap as DbHandle."""
    from s3dgraphy.sync._db_handle import _resolve_db_handle
    from sqlalchemy import create_engine
    eng = create_engine("sqlite:///:memory:")
    h = _resolve_db_handle(eng)
    assert h.is_postgres is False
    assert h.engine is eng


def test_resolve_from_db_handle_passthrough(tmp_path):
    """DbHandle → return as-is (idempotent)."""
    from s3dgraphy.sync._db_handle import (
        DbHandle, _resolve_db_handle,
    )
    p = tmp_path / "y.sqlite"
    p.touch()
    original = DbHandle.from_path(p)
    h = _resolve_db_handle(original)
    assert h is original


def test_resolve_unknown_str_raises():
    """str with unknown dialect prefix → UnsupportedBackendError."""
    from s3dgraphy.sync._db_handle import (
        _resolve_db_handle, UnsupportedBackendError,
    )
    with pytest.raises(UnsupportedBackendError):
        _resolve_db_handle("mysql://foo/bar")


def test_columns_of_sqlite(tmp_path):
    """_columns_of() returns column names from SQLite via PRAGMA."""
    from s3dgraphy.sync._db_handle import _columns_of
    from sqlalchemy import create_engine, text
    p = tmp_path / "x.sqlite"
    engine = create_engine(f"sqlite:///{p}")
    with engine.begin() as conn:
        conn.execute(text(
            "CREATE TABLE foo (id INTEGER PRIMARY KEY, "
            "name TEXT NOT NULL, node_uuid TEXT)"
        ))
    cols = _columns_of(engine, "foo")
    assert cols == {"id", "name", "node_uuid"}


def test_columns_of_returns_empty_for_missing_table(tmp_path):
    """_columns_of() on a non-existent table returns empty set (not raise)."""
    from s3dgraphy.sync._db_handle import _columns_of
    from sqlalchemy import create_engine
    p = tmp_path / "y.sqlite"
    engine = create_engine(f"sqlite:///{p}")
    cols = _columns_of(engine, "nonexistent_table")
    assert cols == set()
