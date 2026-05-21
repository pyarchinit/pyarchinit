"""CLI wrapper for the full schema repair migration.

Audits a pyarchinit DB against the SQLAlchemy structure definitions
and applies any drift fix (missing tables + known missing columns).
Idempotent: safe to re-run.

Usage:
    python scripts/migrations/2026_05_schema_repair.py --apply --db <path>
    python scripts/migrations/2026_05_schema_repair.py --apply --conn-str <pg_uri>
    python scripts/migrations/2026_05_schema_repair.py --dry-run --db <path>
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
from scripts.migrations._2026_05_schema_repair_lib import (
    _collect_canonical_tables,
    _existing_table_names,
    repair_schema,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Full schema repair: create missing tables + add missing "
            "columns on legacy pyarchinit DBs. Idempotent."
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
        canonical, failed = _collect_canonical_tables()
        present = _existing_table_names(handle.engine)
        missing_tables = sorted(set(canonical) - present)
        print(f"dry_run: tables_in_db={len(present)} "
              f"canonical={len(canonical)} missing={len(missing_tables)}")
        if failed:
            print(f"  WARNING: {len(failed)} structure modules failed to "
                  f"import (run inside QGIS for a complete audit):")
            for name, reason in failed:
                print(f"    - {name}: {reason}")
        for t in missing_tables:
            print(f"  MISSING TABLE: {t}")
        return 0

    report = repair_schema(handle)
    created = report["tables_created"]
    cols = report["columns_added"]
    print(f"applied: tables_created={len(created)}")
    for t in created:
        print(f"  +TABLE {t}")
    for table_name, col_map in cols.items():
        for c, added in col_map.items():
            print(f"  +COLUMN {table_name}.{c} (added={added})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
