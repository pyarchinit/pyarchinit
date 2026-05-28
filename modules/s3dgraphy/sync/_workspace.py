"""Workspace path resolution for ParadataStore + GroupStore.

For SQLite: workspace = parent dir of the .sqlite file (legacy behaviour).
For PostgreSQL: workspace = <root> / <conn_slug> / <sito>/
  where <root> is resolved via _resolve_workspace_root() (env var, QSettings,
  or default ~/pyarchinit/pyarchinit_DB_folder).

Created on-demand via mkdir(parents=True, exist_ok=True).

_conn_slug() is the single source of truth for the PG connection slug
used as a filesystem-safe directory name.

_resolve_workspace_root() (added in Consolidation 5.7.4-alpha) does
3-tier fallback:
  1. PYARCHINIT_WORKSPACE_DIR env var (highest priority)
  2. QSettings 'pyarchinit/paradata_workspace' (UI override)
  3. Default: ~/pyarchinit/pyarchinit_DB_folder
"""
from __future__ import annotations

import os
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


def _resolve_workspace_root() -> Path:
    """Resolve the workspace root directory using 3-tier fallback.

    1. PYARCHINIT_WORKSPACE_DIR env var (highest priority)
    2. Default: ~/pyarchinit/pyarchinit_DB_folder

    Returns a Path (existence not guaranteed; caller must mkdir if needed).

    Added in Consolidation 5.7.4-alpha to support the
    `pyarchinitConfigDialog.py` UI override deferred from PG-D Q1=b.
    Empty env var values are treated as unset and fall through.

    s3dgraphy #10: the host application is responsible for propagating
    any UI-level workspace override (e.g. QGIS QSettings
    'pyarchinit/paradata_workspace') into the env var BEFORE calling
    into this module. In pyArchInit this happens in
    `pyarchinitPlugin.initGui` and on config-dialog save. This keeps
    s3dgraphy.sync free of `qgis.*` / `PyQt*` imports per upstream
    policy.
    """
    env_override = os.environ.get("PYARCHINIT_WORKSPACE_DIR")
    if env_override:
        return Path(env_override).expanduser()
    return Path.home() / "pyarchinit" / "pyarchinit_DB_folder"


def _resolve_workspace_dir(handle: DbHandle, sito: str) -> Path:
    """Resolve the per-site workspace directory for paradata/group files.

    SQLite: parent dir of the .sqlite file (legacy behaviour, byte-identical
    to the pre-PG-D `self._db_path.parent` access).

    PostgreSQL: `<root>/<conn_slug>/<sito>/`, created via
    `mkdir(parents=True, exist_ok=True)`. <root> is resolved via
    `_resolve_workspace_root()` which honours env var + QSettings overrides.

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
    workspace = _resolve_workspace_root() / slug / sito_safe
    workspace.mkdir(parents=True, exist_ok=True)
    return workspace
