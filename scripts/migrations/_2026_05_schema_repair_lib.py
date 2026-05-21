"""Library for the full schema repair migration.

Audits a pyarchinit DB against the SQLAlchemy structure definitions
in ``modules/db/structures/*.py`` and applies any drift fix:

- **Missing tables**: created via ``MetaData.create_all`` (idempotent).
- **Known missing columns**: delegated to the existing granular
  migrations (``add_schedatore_columns``, ``add_other_locations_column``).

This is the "go-to" repair tool for any pyarchinit DB whose
auto-migration in ``modules/db/pyarchinit_db_update.py`` silently
skipped some tables (typical of DBs imported from backups or created
by very old plugin versions).
"""
from __future__ import annotations

import importlib
import inspect
import pkgutil
from typing import TYPE_CHECKING

from sqlalchemy import MetaData, Table, inspect as sa_inspect

from modules.s3dgraphy.sync._db_handle import DbHandle

if TYPE_CHECKING:
    from sqlalchemy.engine import Engine


def _discover_structure_modules() -> list[str]:
    """Return importable module names for every file in
    ``modules.db.structures.*`` (excluding ``__init__``)."""
    from modules.db import structures  # imported lazily for QGIS env
    names: list[str] = []
    for info in pkgutil.iter_modules(structures.__path__):
        if info.ispkg:
            continue
        names.append(f"modules.db.structures.{info.name}")
    return names


def _collect_canonical_tables() -> tuple[dict[str, Table], list[tuple[str, str]]]:
    """Walk all structure modules and collect ``{table_name: Table}``.

    Returns a 2-tuple ``(canonical, failed_imports)`` where ``failed_imports``
    is a list of ``(module_name, reason)`` for modules that could not be
    imported. Under QGIS the failure list should be empty; under a
    standalone CLI (no QGIS env) the structure modules that import
    ``modules.db.pyarchinit_conn_strings.Connection`` will typically
    fail — the audit is then partial and the caller MUST warn.
    """
    canonical: dict[str, Table] = {}
    failed: list[tuple[str, str]] = []
    for module_name in _discover_structure_modules():
        try:
            mod = importlib.import_module(module_name)
        except Exception as e:
            failed.append((module_name, f"{type(e).__name__}: {e}"))
            continue
        for _cls_name, cls in inspect.getmembers(mod, inspect.isclass):
            if cls.__module__ != mod.__name__:
                continue
            for _attr_name, attr in inspect.getmembers(cls):
                if isinstance(attr, Table) and attr.name not in canonical:
                    canonical[attr.name] = attr
    return canonical, failed


def _existing_table_names(engine: "Engine") -> set[str]:
    return set(sa_inspect(engine).get_table_names())


def create_missing_tables(handle: DbHandle) -> list[str]:
    """Create any canonical table that isn't already in the DB.

    Returns the list of table names that were actually created
    (empty list if the DB was already complete).
    """
    canonical, _failed = _collect_canonical_tables()
    present = _existing_table_names(handle.engine)
    missing = [t for name, t in canonical.items() if name not in present]
    if not missing:
        return []
    # Group by source MetaData so create_all binds correctly.
    by_metadata: dict[MetaData, list[Table]] = {}
    for t in missing:
        by_metadata.setdefault(t.metadata, []).append(t)
    created: list[str] = []
    with handle.engine.begin() as conn:
        for md, tables in by_metadata.items():
            md.create_all(bind=conn, tables=tables, checkfirst=True)
            created.extend(sorted(t.name for t in tables))
    return sorted(created)


def repair_schema(handle: DbHandle) -> dict[str, list | dict]:
    """Full audit + repair. Returns a report dict::

        {
            "tables_created": ["tomba_table", ...],
            "columns_added": {
                "inventario_materiali_table": {"schedatore": 1, ...},
                "us_table": {"other_locations": 1},
            },
        }

    All operations are idempotent: re-running is a no-op.
    """
    report: dict[str, list | dict] = {
        "tables_created": create_missing_tables(handle),
        "columns_added": {},
    }

    # Delegate known column-drift fixes to the existing granular
    # migrations so each one keeps its own focused responsibility.
    from scripts.migrations._2026_05_inventario_materiali_schedatore_fields_lib import (
        add_schedatore_columns,
    )
    from scripts.migrations._2026_05_yef_other_locations_lib import (
        add_other_locations_column,
    )
    sched_result = add_schedatore_columns(handle)
    if any(sched_result.values()):
        report["columns_added"]["inventario_materiali_table"] = sched_result
    yef_result = add_other_locations_column(handle)
    if yef_result:
        report["columns_added"]["us_table"] = {"other_locations": yef_result}
    return report
