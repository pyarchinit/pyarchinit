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
    from modules.s3dgraphy.sync._db_handle import DbHandle
    from sqlalchemy import create_engine
    eng = create_engine("sqlite:///:memory:")
    h = DbHandle(engine=eng, is_postgres=False, sqlite_path=None,
                 conn_str="sqlite:///:memory:")
    with pytest.raises(Exception):  # FrozenInstanceError or AttributeError
        h.engine = None  # type: ignore[misc]


def test_db_handle_from_path_creates_sqlite_engine(tmp_path):
    """from_path() builds a SQLite engine and records the Path."""
    from modules.s3dgraphy.sync._db_handle import DbHandle
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
    from modules.s3dgraphy.sync._db_handle import DbHandle
    from sqlalchemy import create_engine
    sqlite_eng = create_engine("sqlite:///:memory:")
    h_sqlite = DbHandle.from_engine(sqlite_eng, "sqlite:///:memory:")
    assert h_sqlite.is_postgres is False
    assert h_sqlite.sqlite_path is None  # in-memory has no path
