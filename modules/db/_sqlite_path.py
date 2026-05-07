"""Pure-Python SQLite-path helper for ``Pyarchinit_db_management``.

This sub-module exists solely so the path-extraction logic can be unit-
tested without dragging in the QGIS / SQLAlchemy / psycopg2 surface area
that ``modules/db/pyarchinit_db_manager.py`` pulls in at import time.

The canonical import path remains
``from modules.db.pyarchinit_db_manager import _resolve_sqlite_path``
(re-exported there). Tests use the direct import from this module to
keep the test runtime QGIS-free.

Used by AI03's ``graphml_writer`` to decide whether to attempt
s3dgraphy-based GraphML export (SQLite-only in 5.2.0-alpha; PG support
deferred to AI04).
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional


def _resolve_sqlite_path(conn_str: Optional[str]) -> Optional[Path]:
    """Return the SQLite file path encoded in *conn_str*, or None.

    Examples:
        'sqlite:///path/to/foo.sqlite' -> Path('path/to/foo.sqlite')
        'sqlite:///./rel.sqlite'       -> Path('./rel.sqlite')
        'postgresql://...'             -> None
        None / ''                      -> None
    """
    if not conn_str or "sqlite" not in conn_str.lower():
        return None
    marker = "sqlite:///"
    if marker not in conn_str:
        return None
    return Path(conn_str.split(marker, 1)[1])
