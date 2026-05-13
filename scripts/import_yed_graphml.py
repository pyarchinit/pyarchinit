#!/usr/bin/env python3
"""CLI wrapper for yEd-aware graphml import (yE-D milestone, 5.8.0-alpha).

Imports a yEd-raw graphml (authored externally — no pyarchinit.* data
keys) into the pyarchinit DB:
- Stratigraphic leaves → us_table.
- Special-find leaves → inventario_materiali_table.
- TableNode rows → periodizzazione_table.
- USV / VirtualFind / Document / Combiner / Property leaves →
  paradata.graphml (via ParadataStore).
- Folder-touching edges resolved per --policy.

Cross-backend (SQLite + PostgreSQL) since yE-D ships with the
DbHandle pattern. Pass either ``--db <sqlite_path>`` or
``--conn-str postgresql://...``; mutually exclusive.
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

# Plugin runs this with PYTHONPATH=plugin_root (same as sibling migration
# CLIs); when invoked directly from another cwd, callers can prepend that
# path manually.
from modules.s3dgraphy.sync._db_handle import _resolve_db_handle
from modules.s3dgraphy.sync.yed_classifier import classify_leaves
from modules.s3dgraphy.sync.yed_group_walker import walk_folders
from modules.s3dgraphy.sync.yed_import_pipeline import import_yed_raw
from modules.s3dgraphy.sync.yed_rapporti_policy import FolderEdgePolicy
from modules.s3dgraphy.sync.yed_table_parser import extract_periods


logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("import_yed_graphml")


_POLICY_MAP = {
    "skip":           FolderEdgePolicy.SKIP,
    "fan_out":        FolderEdgePolicy.FAN_OUT,
    "representative": FolderEdgePolicy.REPRESENTATIVE,
    "synthetic":      FolderEdgePolicy.SYNTHETIC,
}


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description=(
            "Import a yEd-raw graphml file into a pyarchinit database. "
            "Stratigraphic, special-find, period, folder and paradata "
            "content is dispatched to the correct destinations."
        )
    )
    p.add_argument(
        "graphml",
        type=Path,
        help="Source .graphml file (yEd-raw).",
    )
    p.add_argument(
        "--site", required=True,
        help="Target site name (forced onto every row).",
    )
    target = p.add_mutually_exclusive_group(required=True)
    target.add_argument(
        "--db", type=Path, default=None,
        help="Path to a SQLite pyarchinit DB.",
    )
    target.add_argument(
        "--conn-str", default=None,
        help="PostgreSQL conn string (postgresql://user:pwd@host:port/db).",
    )
    p.add_argument(
        "--policy", choices=tuple(_POLICY_MAP), default="skip",
        help="Folder-edge policy (default: skip).",
    )
    p.add_argument(
        "--auto-defaults", action="store_true",
        help=(
            "Non-interactive mode: use classifier/period/folder auto_* "
            "values without user overrides. yE-D ships with auto-defaults "
            "as the only mode; user overrides come with yE-E dialog. This "
            "flag is accepted for forward-compat and currently a no-op."
        ),
    )
    p.add_argument(
        "--dry-run", action="store_true",
        help="Execute pipeline in a transaction, then roll back.",
    )
    p.add_argument(
        "-v", "--verbose", action="store_true",
        help="Raise log level to DEBUG.",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if not args.graphml.exists():
        log.error("graphml not found: %s", args.graphml)
        return 2

    # Resolve backend handle.
    if args.db is not None:
        if not args.db.exists():
            log.error("DB not found: %s", args.db)
            return 2
        handle = _resolve_db_handle(args.db)
    else:
        handle = _resolve_db_handle(args.conn_str)

    log.info("Backend: %s", "PostgreSQL" if handle.is_postgres else "SQLite")
    log.info("Source:  %s", args.graphml)
    log.info("Site:    %s", args.site)
    log.info("Policy:  %s", args.policy)
    if args.dry_run:
        log.info("Mode:    dry-run (will roll back)")

    # Build drafts via yE-A/B/C parsers (same as graph_ingestor branch hook).
    drafts = {
        "classified": classify_leaves(args.graphml),
        "periods":    extract_periods(args.graphml),
        "folders":    walk_folders(args.graphml),
    }
    log.info(
        "Parsed: %d leaves, %d periods, %d folders",
        len(drafts["classified"]), len(drafts["periods"]),
        len(drafts["folders"]),
    )

    result = import_yed_raw(
        handle,
        args.graphml,
        args.site,
        drafts,
        policy=_POLICY_MAP[args.policy],
        dry_run=args.dry_run,
    )

    # Print result summary.
    print(f"applied: {result.applied}")
    print(f"inserted: {result.inserted}")
    print(f"updated: {result.updated}")
    print(f"skipped: {result.skipped}")
    print(f"dry_run: {result.dry_run}")
    if result.errors:
        print(f"errors: {len(result.errors)}")
        for e in result.errors:
            print(f"  - {e}")
        return 1
    if result.parsed_drafts:
        # Compact breakdown.
        pd = result.parsed_drafts
        print(
            f"parsed_drafts: classified={len(pd.get('classified', []))} "
            f"periods={len(pd.get('periods', []))} "
            f"folders={len(pd.get('folders', []))}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
