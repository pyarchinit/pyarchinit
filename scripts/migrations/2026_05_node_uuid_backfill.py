#!/usr/bin/env python3
"""One-shot migration: add ``node_uuid TEXT`` + backfill UUID v7 (spec §4.5).

Adds the column to ``us_table``, ``inventario_materiali_table`` and
``periodizzazione_table``, plus a partial unique index, then fills every
NULL ``node_uuid`` with a fresh UUID v7. Idempotent. Auto-backups the DB
before --apply.
"""
from __future__ import annotations

import logging
import shutil
import sqlite3
import sys
from pathlib import Path

from scripts.migrations._common import auto_backup_sqlite, parse_argv
from scripts.migrations._2026_05_node_uuid_backfill_lib import (
    TABLES,
    add_columns,
    backfill_uuids,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("node_uuid_backfill")


def _dry_run(db: Path) -> int:
    log.info("Dry-run plan for %s:", db)
    conn = sqlite3.connect(db)
    try:
        for table in TABLES:
            cols = [r[1] for r in conn.execute(
                f"PRAGMA table_info({table})").fetchall()]
            if "node_uuid" not in cols:
                log.info("  %-30s needs ALTER TABLE + backfill (no col)",
                         table)
                continue
            n = conn.execute(
                f"SELECT COUNT(*) FROM {table} WHERE node_uuid IS NULL"
            ).fetchone()[0]
            log.info("  %-30s %d row(s) need backfill", table, n)
    finally:
        conn.close()
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_argv(argv)
    db = Path(args.db)
    if not db.exists():
        log.error("DB not found: %s", db)
        return 2

    if args.dry_run:
        return _dry_run(db)

    if args.apply:
        backup = auto_backup_sqlite(db, tag="node_uuid_backfill")
        log.info("Backup created: %s", backup)
        add_columns(db)
        log.info("Schema OK on: %s", ", ".join(TABLES))
        counts = backfill_uuids(db)
        log.info("Backfill applied to %s:", db)
        for table, n in counts.items():
            log.info("  %-30s %d row(s) updated", table, n)
        return 0

    if args.rollback:
        backup = Path(args.rollback)
        if not backup.exists():
            log.error("Backup not found: %s", backup)
            return 2
        shutil.copy2(backup, db)
        log.info("Rolled back %s ← %s", db, backup)
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
