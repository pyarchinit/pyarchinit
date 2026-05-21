"""Library for the inventario_materiali_table "schedatore fields" migration.

Five TEXT columns (``schedatore``, ``date_scheda``, ``punto_rinv``,
``negativo_photo``, ``diapositiva``) were added to the SQLAlchemy
entity (`modules/db/structures/`) but the auto-migration in
``modules/db/pyarchinit_db_update.py:446-459`` did not run on every
existing DB (it silently skips when ``safe_load_table`` returns None,
which happens for DBs imported from backups or created by older
plugin versions). Result: the form crashes with::

    sqlite3.OperationalError: no such column: inventario_materiali_table.schedatore

This standalone migration applies the 5 ``ADD COLUMN`` statements
idempotently via the DbHandle shim, so it works transparently on
both SQLite and PostgreSQL.
"""
from __future__ import annotations

from sqlalchemy import text

from modules.s3dgraphy.sync._db_handle import DbHandle, _columns_of


SCHEDATORE_COLUMNS = (
    "schedatore",
    "date_scheda",
    "punto_rinv",
    "negativo_photo",
    "diapositiva",
)


def add_schedatore_columns(handle: DbHandle) -> dict[str, int]:
    """Add the 5 schedatore fields to ``inventario_materiali_table``.

    Returns a dict mapping column name to ``1`` if the column was
    added by this run or ``0`` if it was already present (idempotent).
    """
    present = set(_columns_of(handle.engine, "inventario_materiali_table"))
    result: dict[str, int] = {}
    with handle.engine.begin() as conn:
        for col in SCHEDATORE_COLUMNS:
            if col in present:
                result[col] = 0
                continue
            conn.execute(text(
                f"ALTER TABLE inventario_materiali_table ADD COLUMN {col} TEXT"
            ))
            result[col] = 1
    return result
