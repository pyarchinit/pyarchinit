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

from sqlalchemy import create_engine, text
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


def _resolve_db_handle(arg) -> DbHandle:
    """Backward-compat shim — accept any of:

      - Path: SQLite file path (emits DeprecationWarning)
      - str: SQLAlchemy conn string (sqlite:// or postgresql://)
      - DbManager: pyarchinit Pyarchinit_db_management instance
                   (uses existing .engine + .conn_str)
      - Engine: SQLAlchemy engine (constructs DbHandle around it)
      - DbHandle: passthrough (idempotent)

    Raises UnsupportedBackendError for str with unknown dialect prefix.
    """
    import warnings

    # Order matters: check DbHandle FIRST (it's a dataclass — could
    # accidentally match other branches via duck-typing).
    if isinstance(arg, DbHandle):
        return arg

    if isinstance(arg, Path):
        warnings.warn(
            "Passing db_path: Path to the s3dgraphy bridge is "
            "deprecated since 5.7.0 — pass db_manager (the "
            "Pyarchinit_db_management instance) instead. The Path "
            "argument will continue to work via this shim but will "
            "be removed in a future release. See "
            "docs/superpowers/specs/2026-05-10-postgres-compat-design.md",
            DeprecationWarning,
            stacklevel=3,
        )
        return DbHandle.from_path(arg)

    if isinstance(arg, str):
        if arg.startswith("sqlite:") or arg.startswith("postgresql"):
            engine = create_engine(arg)
            return DbHandle.from_engine(engine, arg)
        raise UnsupportedBackendError(
            f"unrecognised conn string dialect: {arg!r} "
            f"(expected 'sqlite://...' or 'postgresql://...')"
        )

    if isinstance(arg, Engine):
        # Best-effort conn_str reconstruction from engine URL
        return DbHandle.from_engine(arg, str(arg.url))

    # DbManager duck-typing: has .engine attribute (SQLAlchemy Engine)
    # and either .conn_str string or default to engine URL string
    if hasattr(arg, "engine") and isinstance(arg.engine, Engine):
        conn_str = getattr(arg, "conn_str", None) or str(arg.engine.url)
        return DbHandle.from_engine(arg.engine, conn_str)

    raise DbHandleError(
        f"cannot resolve db_handle from {type(arg).__name__}: {arg!r} "
        f"(expected Path, str, DbManager, Engine, or DbHandle)"
    )


def _columns_of(engine: Engine, table: str) -> set[str]:
    """Backend-agnostic column-name introspection.

    Dispatches on engine.dialect.name:
      - sqlite → PRAGMA table_info(table)
      - postgresql → information_schema.columns
      - other → uses SQLAlchemy reflection as fallback

    Returns an empty set if the table does not exist (does not raise).
    """
    dialect = engine.dialect.name
    if dialect == "sqlite":
        try:
            with engine.connect() as conn:
                rows = conn.execute(
                    text(f"PRAGMA table_info({table})")
                ).fetchall()
                return {r[1] for r in rows}
        except Exception:
            return set()
    if dialect == "postgresql":
        try:
            with engine.connect() as conn:
                rows = conn.execute(
                    text(
                        "SELECT column_name FROM information_schema.columns "
                        "WHERE table_name = :t "
                        "AND table_schema = current_schema()"
                    ),
                    {"t": table},
                ).fetchall()
                return {r[0] for r in rows}
        except Exception:
            return set()
    # Other dialects: reflection fallback
    try:
        from sqlalchemy import inspect
        inspector = inspect(engine)
        return {col["name"] for col in inspector.get_columns(table)}
    except Exception:
        return set()
