#!/usr/bin/env python3
"""One-shot migration: add ``node_uuid TEXT`` + backfill UUID v7.

Adds the column to ``us_table``, ``inventario_materiali_table`` and
``periodizzazione_table``, plus a partial unique index, then fills every
NULL ``node_uuid`` with a fresh UUID v7. Idempotent. Auto-backups the DB
before --apply.

Cross-backend (SQLite + PostgreSQL) since 5.7.0-alpha. Pass either
``--db <sqlite_path>`` or ``--conn-str postgresql://...``; mutually exclusive.
"""
from __future__ import annotations

import logging
import shutil
import sys
from pathlib import Path

from sqlalchemy import text

from modules.s3dgraphy.sync._db_handle import _resolve_db_handle
from scripts.migrations._common import (
    BackupSkipped, auto_backup_postgres, auto_backup_sqlite, parse_argv,
)
from scripts.migrations._2026_05_node_uuid_backfill_lib import (
    TABLES, add_columns, backfill_uuids,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("node_uuid_backfill")


def _resolve_input(args):
    """Return a DbHandle from the CLI args (--db or --conn-str)."""
    if args.db is not None:
        db_path = Path(args.db)
        if not db_path.exists():
            log.error("DB not found: %s", db_path)
            sys.exit(2)
        return _resolve_db_handle(db_path)
    return _resolve_db_handle(args.conn_str)


def _dry_run(handle) -> int:
    """Report which tables need ALTER + how many rows need backfill."""
    log.info("Dry-run plan for %s:", handle.conn_str)
    from modules.s3dgraphy.sync._db_handle import _columns_of
    with handle.engine.connect() as conn:
        for table in TABLES:
            cols = _columns_of(handle.engine, table)
            if "node_uuid" not in cols:
                log.info("  %-30s needs ALTER TABLE + backfill (no col)",
                         table)
                continue
            n = conn.execute(text(
                f"SELECT COUNT(*) FROM {table} WHERE node_uuid IS NULL"
            )).scalar()
            log.info("  %-30s %d row(s) need backfill", table, n)
    return 0


def _apply(handle, args) -> int:
    """Run auto_backup + add_columns + backfill_uuids."""
    if handle.is_postgres:
        try:
            backup = auto_backup_postgres(
                handle.engine,
                tag="node_uuid_backfill",
                dest_dir=Path.home() / "pyarchinit" / "pyarchinit_DB_folder"
                                       / "_pga_backups",
            )
            log.info("PG backup created: %s", backup)
        except BackupSkipped as e:
            log.warning("PG backup skipped: %s", e)
            log.warning("Proceeding WITHOUT a backup (CLI mode = no prompt)")
    else:
        backup = auto_backup_sqlite(handle.sqlite_path, tag="node_uuid_backfill")
        log.info("SQLite backup created: %s", backup)
    add_columns(handle)
    log.info("Schema OK on: %s", ", ".join(TABLES))
    counts = backfill_uuids(handle)
    log.info("Backfill applied to %s:", handle.conn_str)
    for table, n in counts.items():
        log.info("  %-30s %d row(s) updated", table, n)
    return 0


def _rollback(args) -> int:
    """Restore SQLite DB from a backup file. PG rollback is manual via psql."""
    if args.conn_str is not None:
        log.error("--rollback is SQLite-only. For PG, restore manually with "
                  "'psql -d <db> -f <backup>'")
        return 2
    backup = Path(args.rollback)
    if not backup.exists():
        log.error("Backup not found: %s", backup)
        return 2
    db = Path(args.db)
    shutil.copy2(backup, db)
    log.info("Rolled back %s ← %s", db, backup)
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_argv(argv)
    if args.rollback:
        return _rollback(args)
    handle = _resolve_input(args)
    if args.dry_run:
        return _dry_run(handle)
    if args.apply:
        return _apply(handle, args)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
