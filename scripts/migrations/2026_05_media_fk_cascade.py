#!/usr/bin/env python3
"""One-shot CLI: heal legacy PG DBs that still carry the killer triggers
on ``media_thumb_table`` (``delete_media_table`` +
``delete_media_to_entity_table``).

Three operation modes (mutually exclusive):
  --detect    Report which legacy triggers are present, how many orphan
              rows exist in thumb + MTE tables, and whether the
              replacement FKs are already installed. Read-only.
  --dry-run   Execute the full migration inside a transaction, then roll
              back. Returns the result dict (what *would* have happened).
              No state change.
  --apply     Auto-backup the PG database via ``pg_dump`` first
              (raises ``BackupSkipped`` if ``pg_dump`` is missing —
              CLI proceeds without backup and logs a warning), then
              apply the migration for real.

PG-only — pass ``--conn-str postgresql://...``. ``--db`` is rejected at
parse time (an SQLite path makes no sense for this migration).

Pattern: mirrors ``2026_05_node_uuid_backfill.py`` (PG-A 5.7.0-alpha)
for argparse layout + auto-backup integration. See the spec at
``docs/superpowers/specs/2026-05-13-media-fk-migration-design.md``.
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from modules.s3dgraphy.sync._db_handle import _resolve_db_handle
from scripts.migrations._common import (
    BackupSkipped, auto_backup_postgres,
)
from scripts.migrations._2026_05_media_fk_cascade_lib import (
    apply_migration, count_orphans, detect_killer_triggers,
    verify_post_migration,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("media_fk_cascade")


def _build_parser() -> argparse.ArgumentParser:
    """Return the argparse parser. Extracted so the L0 source-inspection
    test can verify the three operation modes + the --db/--conn-str
    mutex without executing main()."""
    p = argparse.ArgumentParser(
        description=(
            "Heal PG pyarchinit databases by dropping the killer "
            "triggers on media_thumb_table and installing FK "
            "ON DELETE CASCADE in their place."
        )
    )
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument(
        "--db",
        help=(
            "Path to SQLite file. Rejected by this migration "
            "(PG-only) — kept for parser symmetry with sibling "
            "migration scripts."
        ),
    )
    src.add_argument(
        "--conn-str", dest="conn_str",
        help="PostgreSQL conn string (postgresql://user:pwd@host:port/db)",
    )
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--detect", action="store_true",
        help="Report current state (read-only).",
    )
    mode.add_argument(
        "--dry-run", dest="dry_run", action="store_true",
        help="Execute migration in a transaction, then roll back.",
    )
    mode.add_argument(
        "--apply", action="store_true",
        help="Auto-backup + apply for real.",
    )
    return p


def _resolve_handle(args: argparse.Namespace):
    """Resolve the args.conn_str into a PG ``DbHandle``. Reject --db
    (this migration is PG-only)."""
    if args.db is not None:
        log.error(
            "--db is not supported by this migration (PG-only). "
            "Pass --conn-str postgresql://... instead."
        )
        sys.exit(2)
    if not args.conn_str.startswith("postgresql"):
        log.error(
            "media-fk-migration is PG-only; got conn string: %s",
            args.conn_str,
        )
        sys.exit(2)
    return _resolve_db_handle(args.conn_str)


def _print_dict(title: str, d: dict) -> None:
    """Plain key: value lines, easy for humans + ``awk``-friendly."""
    log.info("%s:", title)
    for k, v in d.items():
        log.info("  %s: %s", k, v)


def _run_detect(handle) -> int:
    """Read-only report. Returns 0 if clean, 1 if dirty (triggers /
    orphans / missing FKs found). Useful as a smoke check."""
    triggers = detect_killer_triggers(handle)
    orphans = count_orphans(handle)
    verify = verify_post_migration(handle)
    _print_dict("triggers", triggers)
    _print_dict(
        "orphans",
        {
            "thumb_orphans": orphans["thumb_orphans"],
            "mte_orphans": orphans["mte_orphans"],
            "thumb_samples": orphans["thumb_samples"],
            "mte_samples": orphans["mte_samples"],
        },
    )
    _print_dict("verify", verify)
    return 0 if verify["is_clean"] else 1


def _run_dry_run(handle) -> int:
    """Roll-back simulation. Logs what would happen, leaves DB unchanged."""
    result = apply_migration(handle, dry_run=True)
    _print_dict("dry_run_result", result)
    return 0


def _run_apply(handle) -> int:
    """Auto-backup, then apply for real, then verify."""
    try:
        backup = auto_backup_postgres(
            handle.engine,
            tag="media_fk_cascade",
            dest_dir=Path.home() / "pyarchinit" / "pyarchinit_DB_folder"
                                   / "_media_fk_backups",
        )
        log.info("PG backup created: %s", backup)
    except BackupSkipped as e:
        log.error(
            "PG backup failed: %s — aborting --apply to protect the DB. "
            "Run with --dry-run to preview, or fix pg_dump availability.",
            e,
        )
        return 1
    result = apply_migration(handle, dry_run=False)
    _print_dict("apply_result", result)
    verify = verify_post_migration(handle)
    _print_dict("verify", verify)
    return 0 if verify["is_clean"] else 1


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    handle = _resolve_handle(args)
    if args.detect:
        return _run_detect(handle)
    if args.dry_run:
        return _run_dry_run(handle)
    if args.apply:
        return _run_apply(handle)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
