"""PG-D Workspace path resolution for ParadataStore + GroupStore.

For SQLite: workspace = parent dir of the .sqlite file (legacy behaviour).
For PostgreSQL: workspace = ~/pyarchinit/pyarchinit_DB_folder/<conn_slug>/<sito>/

Created on-demand via mkdir(parents=True, exist_ok=True).

_conn_slug() is the single source of truth for the PG connection slug
used as a filesystem-safe directory name. Future code (e.g.,
Consolidation 5.7.4) may adopt this helper for other paths.
"""
from __future__ import annotations

import re
from pathlib import Path

from ._db_handle import DbHandle


def _conn_slug(handle: DbHandle) -> str:
    """Produce a deterministic filesystem-safe slug from a PG handle's URL.

    Format: <host>_<port>_<dbname>, with non-[a-zA-Z0-9_-] chars replaced
    by underscores. Always returns a non-empty string.

    Raises ValueError for non-PG handles.
    """
    if not handle.is_postgres:
        raise ValueError("_conn_slug only applies to PostgreSQL handles")
    url = handle.engine.url
    host = url.host or "unknown_host"
    port = str(url.port or "5432")
    dbname = url.database or "unknown_db"
    raw = f"{host}_{port}_{dbname}"
    return re.sub(r"[^a-zA-Z0-9_-]", "_", raw)


def _resolve_workspace_dir(handle: DbHandle, sito: str) -> Path:
    """Resolve the per-site workspace directory for paradata/group files.

    SQLite: parent dir of the .sqlite file (legacy behaviour, byte-identical
    to the pre-PG-D `self._db_path.parent` access).

    PostgreSQL: `~/pyarchinit/pyarchinit_DB_folder/<conn_slug>/<sito>/`,
    created via `mkdir(parents=True, exist_ok=True)`.

    Raises:
        ValueError: SQLite handle with no `sqlite_path` (e.g., `:memory:`).
    """
    if not handle.is_postgres:
        if handle.sqlite_path is None:
            raise ValueError(
                "In-memory SQLite has no parent dir for workspace; "
                "ParadataStore / GroupStore require a file-backed DB"
            )
        return handle.sqlite_path.parent

    slug = _conn_slug(handle)
    # Sanitize sito for directory use (same pattern as conn_slug)
    sito_safe = re.sub(r"[^a-zA-Z0-9_-]", "_", sito)
    workspace = (
        Path.home()
        / "pyarchinit"
        / "pyarchinit_DB_folder"
        / slug
        / sito_safe
    )
    workspace.mkdir(parents=True, exist_ok=True)
    return workspace
