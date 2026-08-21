#!/usr/bin/env python3
"""Repair: remove blank ['', '', '', ''] rows from us_table.rapporti/rapporti2.

Left behind by plugin versions 4.9.7–4.9.9 / 5.x before 2026-08 (see
``_2026_08_rapporti_blank_rows_lib`` for the story). Idempotent.
Auto-backups the DB before --apply (SQLite copy / pg_dump).

Usage:
    python scripts/migrations/2026_08_rapporti_blank_rows.py --dry-run --db <path>
    python scripts/migrations/2026_08_rapporti_blank_rows.py --apply   --db <path>
    python scripts/migrations/2026_08_rapporti_blank_rows.py --apply   --conn-str <pg_uri>
    python scripts/migrations/2026_08_rapporti_blank_rows.py --rollback <backup> --db <path>
"""
from __future__ import annotations

import logging
import shutil
import sys
from pathlib import Path

# Ensure plugin root on sys.path when run as standalone script.
_PLUGIN_ROOT = Path(__file__).resolve().parents[2]
if str(_PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(_PLUGIN_ROOT))

from modules.s3dgraphy.sync._db_handle import DbHandle  # noqa: E402
from scripts.migrations._common import (  # noqa: E402
    BackupSkipped, auto_backup_postgres, auto_backup_sqlite, parse_argv,
)
from scripts.migrations._2026_08_rapporti_blank_rows_lib import (  # noqa: E402
    repair_blank_rapporti,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("rapporti_blank_rows")

TAG = "rapporti_blank_rows"


def _handle(args) -> DbHandle:
    if args.db:
        return DbHandle.from_path(Path(args.db))
    from sqlalchemy import create_engine
    return DbHandle.from_engine(create_engine(args.conn_str), args.conn_str)


def _log_details(result) -> None:
    for d in result.details:
        log.info("  US %s (sito=%s area=%s) %s: %d -> %d righe",
                 d.us, d.sito, d.area, d.column, d.before_rows, d.after_rows)


def main(argv: list[str] | None = None) -> int:
    args = parse_argv(argv)

    if args.rollback:
        if not args.db:
            log.error("--rollback è supportato solo con --db (SQLite)")
            return 2
        backup, db = Path(args.rollback), Path(args.db)
        if not backup.exists():
            log.error("Backup non trovato: %s", backup)
            return 2
        shutil.copy2(backup, db)
        log.info("Ripristinato %s ← %s", db, backup)
        return 0

    if args.db and not Path(args.db).exists():
        log.error("DB non trovato: %s", args.db)
        return 2
    handle = _handle(args)

    if args.dry_run:
        result = repair_blank_rapporti(handle, dry_run=True)
        log.info(result.summary())
        _log_details(result)
        return 0

    # --apply
    try:
        if handle.is_postgres:
            backup = auto_backup_postgres(handle.engine, TAG, Path.cwd())
        else:
            backup = auto_backup_sqlite(handle.sqlite_path, TAG)
        log.info("Backup creato: %s", backup)
    except BackupSkipped as e:
        log.warning("Backup saltato (%s): procedo senza backup", e)
    result = repair_blank_rapporti(handle, dry_run=False)
    log.info(result.summary())
    _log_details(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
