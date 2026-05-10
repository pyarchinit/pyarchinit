"""Shared helpers for one-shot migrations.

All migrations expose the same CLI: --dry-run | --apply | --rollback <path>.
Auto-backup is invoked at the start of any --apply run.

PG-A (5.7.0-alpha) added:
- ``--conn-str`` flag mutually exclusive with ``--db``.
- ``auto_backup_postgres()`` for PG backends (wraps ``pg_dump`` subprocess).
- ``BackupSkipped`` exception so callers can surface a "pg_dump not found"
  dialog and let the user decide whether to proceed without a backup.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from sqlalchemy.engine import Engine


class BackupSkipped(Exception):
    """Raised by ``auto_backup_postgres`` when ``pg_dump`` is unavailable.

    The CLI / GUI catches this and offers the user a choice between
    proceeding without a backup (logged) and cancelling the migration.
    """


def auto_backup_sqlite(db_path: Path, tag: str) -> Path:
    """Copy db_path to <db>.pre_<tag>_<UTC timestamp>; return new path."""
    db_path = Path(db_path)
    stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    backup = db_path.with_name(f"{db_path.name}.pre_{tag}_{stamp}")
    shutil.copy2(db_path, backup)
    return backup


def auto_backup_postgres(engine: Engine, tag: str, dest_dir: Path) -> Path:
    """Run ``pg_dump`` on the engine's database; return path of the dump file.

    Discovers ``pg_dump`` via ``shutil.which``. If missing, raises
    ``BackupSkipped`` so the caller can surface a "skip backup at your own
    risk" dialog.

    Output path: ``<dest_dir>/<dbname>.sql.pre_<tag>_<ts>``.
    Subprocess is invoked with PGPASSWORD in env (never on the command line).
    Subprocess timeout is 5 minutes.
    """
    pg_dump = shutil.which("pg_dump")
    if pg_dump is None:
        raise BackupSkipped(
            "pg_dump not found on PATH. Install PostgreSQL client tools "
            "or skip the backup explicitly."
        )
    url = engine.url
    dbname = url.database or "unknown"
    stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    out = dest_dir / f"{dbname}.sql.pre_{tag}_{stamp}"
    cmd = [
        pg_dump,
        "-h", str(url.host or "localhost"),
        "-p", str(url.port or 5432),
        "-U", str(url.username or "postgres"),
        "-d", dbname,
        "-f", str(out),
    ]
    env = {"PGPASSWORD": str(url.password or ""), "PATH": os.environ.get("PATH", "")}
    proc = subprocess.run(cmd, env=env, timeout=300, check=False,
                          capture_output=True, text=True)
    if proc.returncode != 0:
        raise BackupSkipped(
            f"pg_dump exited {proc.returncode}: {proc.stderr.strip()}"
        )
    return out


def parse_argv(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI args. ``--db`` (SQLite path) and ``--conn-str`` (any DSN)
    are mutually exclusive; exactly one of them must be present."""
    p = argparse.ArgumentParser()
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--db", help="Path to SQLite file")
    src.add_argument("--conn-str", dest="conn_str",
                     help="SQLAlchemy conn string (sqlite:/// or postgresql://)")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true",
                   help="Report what would change; do not mutate")
    g.add_argument("--apply", action="store_true",
                   help="Apply the migration (auto-backup first)")
    g.add_argument("--rollback", metavar="BACKUP_PATH",
                   help="Restore the DB from a previous --apply backup")
    return p.parse_args(argv)
