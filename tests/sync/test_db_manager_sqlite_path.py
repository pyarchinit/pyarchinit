"""Unit tests for ``_resolve_sqlite_path`` (AI03 / Phase 2 / Group D).

The pure helper is tested directly from its sibling module
``modules.db._sqlite_path`` so the path-extraction logic can be exercised
without instantiating ``Pyarchinit_db_management`` (which transitively
pulls in QGIS / SQLAlchemy / psycopg2 / a live engine — none available
in the unit-test environment).

The canonical import path
``from modules.db.pyarchinit_db_manager import _resolve_sqlite_path``
also resolves (it's re-exported there) for production callers that have
QGIS available.
"""

from __future__ import annotations

from pathlib import Path

from modules.db._sqlite_path import _resolve_sqlite_path


def test_get_sqlite_path_extracts_sqlite_url():
    """An absolute sqlite:/// URL yields a Path to the underlying file."""
    conn_str = "sqlite:///path/to/foo.sqlite"
    result = _resolve_sqlite_path(conn_str)
    assert result == Path("path/to/foo.sqlite")


def test_get_sqlite_path_returns_none_for_postgres():
    """A PostgreSQL conn_str is not a SQLite URL -> None."""
    conn_str = "postgresql://user:pwd@localhost:5432/dbname"
    assert _resolve_sqlite_path(conn_str) is None


def test_get_sqlite_path_handles_relative_path():
    """Relative paths after the sqlite:/// marker are preserved verbatim."""
    conn_str = "sqlite:///./rel.sqlite"
    result = _resolve_sqlite_path(conn_str)
    assert result == Path("./rel.sqlite")


def test_get_sqlite_path_returns_none_on_garbage():
    """Empty / None / nonsense conn_str values resolve to None, not crash."""
    assert _resolve_sqlite_path(None) is None
    assert _resolve_sqlite_path("") is None
    assert _resolve_sqlite_path("not a url at all") is None
