# modules/s3dgraphy/sync/_db_handle.py
"""PG-Compat Foundation: backend-agnostic DbHandle value object + exceptions.

This module is the single entry point through which the s3dgraphy bridge
layer will access the underlying database. The `DbHandle` value object
wraps a SQLAlchemy engine and tracks the backend dialect (sqlite vs
postgresql). The accompanying exception hierarchy reports failures from
the resolver shim added in Group B.

Foundation milestone (5.6.2-alpha) introduces this machinery WITHOUT
changing any caller. PG-A through PG-D milestones progressively
replace direct `sqlite3.connect()` call sites in the bridge with
`DbHandle.engine` access.

Spec: docs/superpowers/specs/2026-05-10-postgres-compat-design.md
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from .graph_ingestor import GraphSyncError


class DbHandleError(GraphSyncError):
    """Failure resolving a db_handle argument."""


class UnsupportedBackendError(DbHandleError):
    """Conn string dialect not in {sqlite, postgresql}."""


class PgConnectionError(DbHandleError):
    """PG engine constructed but TCP connection failed."""


@dataclass(frozen=True)
class DbHandle:
    """Backend-agnostic handle wrapping a SQLAlchemy engine.

    Use the factory classmethods (`from_path`, `from_engine`) rather
    than constructing directly. For higher-level resolution from a
    DbManager / Path / conn-string / Engine input, use the
    module-level `_resolve_db_handle()` shim added in Group B.
    """
    engine: Engine                      # Always set
    is_postgres: bool
    sqlite_path: Optional[Path]         # Set only when backend is SQLite + file-backed
    conn_str: str                       # Original conn string for slug derivation

    @classmethod
    def from_path(cls, p: Path) -> "DbHandle":
        """Build a DbHandle from a SQLite file path."""
        conn_str = f"sqlite:///{p}"
        engine = create_engine(conn_str)
        return cls(engine=engine, is_postgres=False, sqlite_path=p,
                   conn_str=conn_str)

    @classmethod
    def from_engine(cls, engine: Engine, conn_str: str) -> "DbHandle":
        """Wrap an existing SQLAlchemy engine. Detects backend from
        engine.dialect.name."""
        is_pg = engine.dialect.name == "postgresql"
        sqlite_path: Optional[Path] = None
        if conn_str.startswith("sqlite:///") and not conn_str.endswith(":memory:"):
            sqlite_path = Path(conn_str[len("sqlite:///"):])
        return cls(engine=engine, is_postgres=is_pg, sqlite_path=sqlite_path,
                   conn_str=conn_str)
