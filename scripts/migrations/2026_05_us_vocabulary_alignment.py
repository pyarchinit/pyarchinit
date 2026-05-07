#!/usr/bin/env python3
"""One-shot migration: USVA/USVB → USVs, USVC → USVn.

Per spec §4.4. Idempotent. Auto-backups DB before --apply.
"""
from __future__ import annotations

import logging
import shutil
import sys
from pathlib import Path

from scripts.migrations._common import auto_backup_sqlite, parse_argv
from scripts.migrations._2026_05_us_vocabulary_alignment_lib import (
    apply_changes,
    plan_changes,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("us_vocabulary_alignment")


def main(argv: list[str] | None = None) -> int:
    args = parse_argv(argv)
    db = Path(args.db)
    if not db.exists():
        log.error("DB not found: %s", db)
        return 2

    if args.dry_run:
        plan = plan_changes(db)
        log.info("Dry-run plan for %s:", db)
        for k, v in plan.items():
            log.info("  %-30s %d", k, v)
        return 0

    if args.apply:
        backup = auto_backup_sqlite(db, tag="us_vocab_alignment")
        log.info("Backup created: %s", backup)
        applied = apply_changes(db)
        log.info("Applied to %s:", db)
        for k, v in applied.items():
            log.info("  %s -> %d row(s) updated", k, v)
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
