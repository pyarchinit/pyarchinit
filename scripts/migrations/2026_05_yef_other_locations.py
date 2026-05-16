"""CLI wrapper for the yE-F other_locations migration.

Usage:
    python scripts/migrations/2026_05_yef_other_locations.py --apply --db <path>
    python scripts/migrations/2026_05_yef_other_locations.py --apply --conn-str <pg_uri>
    python scripts/migrations/2026_05_yef_other_locations.py --dry-run --db <path>
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
from scripts.migrations._2026_05_yef_other_locations_lib import (
    add_other_locations_column,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="yE-F other_locations column migration",
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
        present = "other_locations" in _columns_of(handle.engine, "us_table")
        print(f"dry_run: other_locations present={present}")
        return 0

    added = add_other_locations_column(handle)
    print(f"applied: rows_changed={added}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
