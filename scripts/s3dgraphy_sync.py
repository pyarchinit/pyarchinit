#!/usr/bin/env python3
"""CLI helper for the AI04 bidirectional bridge.

Usage:
    python scripts/s3dgraphy_sync.py export \\
        --db DB --graphml OUT --sito SITO

    python scripts/s3dgraphy_sync.py import \\
        --db DB --graphml IN --sito SITO
        [--apply]                  # default is dry-run
        [--create-epochs]
        [--mapping NAME]           # default: pyarchinit_us_mapping

Default for `import` is dry-run; pass `--apply` to actually write.

Exit codes:
    0  success
    1  GraphSyncError (any subclass) or expected validation failure
    2  argparse error / unknown command
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
# Ensure modules.* resolves when invoked directly
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))


def _setup_path() -> None:
    """Import pandas + lxml from the system FIRST so the broken
    vendored pandas in ext_libs doesn't shadow them. Then put
    ext_libs at the front of sys.path so the vendored s3dgraphy
    0.1.40 wins over any older site-packages copy. Finally evict
    any pre-loaded older s3dgraphy from sys.modules."""
    import pandas  # noqa: F401
    from lxml import etree as _etree  # noqa: F401
    ext_libs = str(PLUGIN_ROOT / "ext_libs")
    if ext_libs in sys.path:
        sys.path.remove(ext_libs)
    sys.path.insert(0, ext_libs)
    for mod in [m for m in list(sys.modules)
                if m == "s3dgraphy" or m.startswith("s3dgraphy.")]:
        del sys.modules[mod]


def cmd_export(args) -> int:
    _setup_path()
    from modules.s3dgraphy.sync.graphml_writer import (
        export_graphml, EmptyGraphError, GraphMLExportError)
    try:
        result = export_graphml(
            db_path=Path(args.db),
            mapping=args.mapping,
            output_path=Path(args.graphml),
            site_filter=args.sito,
        )
    except (EmptyGraphError, GraphMLExportError) as e:
        print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    print(f"OK — {args.graphml}")
    print(f"   {result.node_count} nodes, {result.edge_count} edges, "
          f"{result.epoch_count} epochs, "
          f"{result.tred_removed_edges} redundancies removed")
    return 0


def cmd_import(args) -> int:
    _setup_path()
    from s3dgraphy.importer.import_graphml import GraphMLImporter
    from modules.s3dgraphy.sync.graph_ingestor import (
        GraphIngestor, GraphSyncError)

    try:
        graph = GraphMLImporter(filepath=str(args.graphml)).parse()
    except Exception as e:
        print(f"ERROR: failed to load graph from {args.graphml}: {e}",
              file=sys.stderr)
        return 1

    g = GraphIngestor()
    try:
        result = g.populate_list(
            graph,
            db_path=Path(args.db),
            sito=args.sito,
            dry_run=not args.apply,
            create_missing_epochs=args.create_epochs,
        )
    except GraphSyncError as e:
        print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        return 1

    label = "DRY-RUN" if result.dry_run else "WRITTEN"
    print(f"OK [{label}] — applied={result.applied} "
          f"(inserted={result.inserted}, updated={result.updated}, "
          f"skipped={result.skipped}), epochs_created={result.epochs_created}")
    if result.conflicts:
        print(f"   {len(result.conflicts)} conflicts:")
        for c in result.conflicts[:10]:
            print(f"     - {c.node_uuid[:8]}.{c.field}: "
                  f"DB={c.db_value!r} → graph={c.graph_value!r}")
        if len(result.conflicts) > 10:
            print(f"     ({len(result.conflicts) - 10} more)")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="s3dgraphy_sync",
        description="PyArchInit ↔ s3dgraphy bridge CLI (AI04).")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_exp = sub.add_parser("export", help="DB → GraphML")
    p_exp.add_argument("--db", required=True)
    p_exp.add_argument("--graphml", required=True)
    p_exp.add_argument("--sito", required=True)
    p_exp.add_argument("--mapping", default="pyarchinit_us_mapping")
    p_exp.set_defaults(func=cmd_export)

    p_imp = sub.add_parser("import", help="GraphML → DB")
    p_imp.add_argument("--db", required=True)
    p_imp.add_argument("--graphml", required=True)
    p_imp.add_argument("--sito", required=True)
    p_imp.add_argument("--apply", action="store_true",
                       help="actually write to DB (default: dry-run)")
    p_imp.add_argument("--create-epochs", action="store_true",
                       help="auto-create missing periodizzazione rows")
    p_imp.set_defaults(func=cmd_import)

    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.WARNING)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
