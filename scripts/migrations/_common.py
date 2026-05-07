"""Shared helpers for one-shot migrations.

All migrations expose the same CLI: --dry-run | --apply | --rollback <path>.
Auto-backup is invoked at the start of any --apply run.
"""
from __future__ import annotations

import argparse
import shutil
from datetime import datetime
from pathlib import Path


def auto_backup_sqlite(db_path: Path, tag: str) -> Path:
    """Copy db_path to <db>.pre_<tag>_<UTC timestamp>; return new path."""
    db_path = Path(db_path)
    stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    backup = db_path.with_name(f"{db_path.name}.pre_{tag}_{stamp}")
    shutil.copy2(db_path, backup)
    return backup


def parse_argv(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--db", required=True, help="Path to SQLite (or DSN for PG)")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true",
                   help="Report what would change; do not mutate")
    g.add_argument("--apply", action="store_true",
                   help="Apply the migration (auto-backup first)")
    g.add_argument("--rollback", metavar="BACKUP_PATH",
                   help="Restore the DB from a previous --apply backup")
    return p.parse_args(argv)
