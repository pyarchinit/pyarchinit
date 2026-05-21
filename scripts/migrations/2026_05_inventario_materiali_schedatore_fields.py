"""CLI wrapper for the inventario_materiali schedatore fields migration.

Usage:
    python scripts/migrations/2026_05_inventario_materiali_schedatore_fields.py --apply --db <path>
    python scripts/migrations/2026_05_inventario_materiali_schedatore_fields.py --apply --conn-str <pg_uri>
    python scripts/migrations/2026_05_inventario_materiali_schedatore_fields.py --dry-run --db <path>
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure plugin root on sys.path when run as standalone script.
_PLUGIN_ROOT = Path(__file__).resolve().parents[2]
if str(_PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(_PLUGIN_ROOT))

from modules.s3dgraphy.sync._db_handle import DbHandle
from scripts.migrations._2026_05_inventario_materiali_schedatore_fields_lib import (
    SCHEDATORE_COLUMNS,
    add_schedatore_columns,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Add 5 missing TEXT columns (schedatore, date_scheda, "
            "punto_rinv, negativo_photo, diapositiva) to "
            "inventario_materiali_table on legacy DBs."
        ),
    )
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--db", help="SQLite file path")
    target.add_argument("--conn-str", help="PostgreSQL connection URI")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    if args.db:
        handle = DbHandle.from_path(Path(args.db))
    else:
        from sqlalchemy import create_engine
        engine = create_engine(args.conn_str)
        handle = DbHandle.from_engine(engine, args.conn_str)

    if args.dry_run:
        from modules.s3dgraphy.sync._db_handle import _columns_of
        present = set(_columns_of(handle.engine, "inventario_materiali_table"))
        for col in SCHEDATORE_COLUMNS:
            status = "present" if col in present else "MISSING"
            print(f"dry_run: {col:18s} {status}")
        return 0

    result = add_schedatore_columns(handle)
    for col, added in result.items():
        print(f"applied: {col:18s} added={added}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
