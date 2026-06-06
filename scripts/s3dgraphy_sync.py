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
    # AI06: --group-by CSV → groups list
    groups_arg = None
    if getattr(args, "group_by", None):
        groups_arg = [g.strip() for g in args.group_by.split(",")
                      if g.strip()]
    out_path = args.graphml
    try:
        result = export_graphml(
            db_path=Path(args.db),
            mapping=args.mapping,
            output_path=Path(out_path),
            site_filter=args.sito,
            groups=groups_arg,
        )
    except (EmptyGraphError, GraphMLExportError) as e:
        print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    print(f"OK — {out_path}")
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

    # Copy mode: regenerate node_uuids so the ingest does NOT match (and
    # rewrite the sito of) existing rows — it INSERTs a fresh copy under
    # --sito instead. Without this, re-importing an export carries the
    # original node_uuids and populate_list renames the source site.
    if getattr(args, "copy", False):
        from modules.utility.rapporti_check import regenerate_node_uuids
        n = regenerate_node_uuids(graph)
        print(f"[copy mode] regenerated {n} node_uuids — importing as a new "
              f"copy into sito={args.sito!r} (existing rows untouched)")

    g = GraphIngestor()
    try:
        result = g.populate_list(
            graph,
            db_path=Path(args.db),
            sito=args.sito,
            dry_run=not args.apply,
            create_missing_epochs=args.create_epochs,
            graphml_path=Path(args.graphml),
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


def cmd_paradata(args) -> int:
    _setup_path()
    from modules.s3dgraphy.sync.paradata_store import (
        ParadataStore, ParadataStoreError,
    )
    from modules.s3dgraphy.sync.group_store import (
        GroupStore, GroupStoreError,
    )
    sub = args.paradata_action
    try:
        if sub == "add-author":
            store = ParadataStore(Path(args.db), args.sito)
            uuid = store.add_author(args.name, orcid=args.orcid,
                                     role=args.role)
            print(f"OK — author {uuid}")
        elif sub == "list-authors":
            store = ParadataStore(Path(args.db), args.sito)
            for a in store.list_authors():
                print(f"{a['node_uuid']}\t{a['name']}\t{a.get('orcid','')}\t{a.get('role','')}")
        elif sub == "add-license":
            store = ParadataStore(Path(args.db), args.sito)
            uuid = store.add_license(args.spdx, url=args.url)
            print(f"OK — license {uuid}")
        elif sub == "list-licenses":
            store = ParadataStore(Path(args.db), args.sito)
            for li in store.list_licenses():
                print(f"{li['node_uuid']}\t{li['spdx_id']}\t{li.get('url','')}")
        elif sub == "add-embargo":
            store = ParadataStore(Path(args.db), args.sito)
            uuid = store.add_embargo(args.until, reason=args.reason)
            print(f"OK — embargo {uuid}")
        elif sub == "list-embargos":
            store = ParadataStore(Path(args.db), args.sito)
            for e in store.list_embargos():
                print(f"{e['node_uuid']}\t{e['until_date']}\t{e.get('reason','')}")
        elif sub == "remove":
            store = ParadataStore(Path(args.db), args.sito)
            store.remove(args.uuid)
            print(f"OK — removed {args.uuid}")
        elif sub == "add-group":
            gstore = GroupStore(Path(args.db), args.sito)
            members = list(args.us_uuid or [])
            uuid = gstore.add_group(
                args.name,
                group_kind=args.kind,
                member_us_uuids=members,
            )
            print(f"OK — group {uuid}")
        elif sub == "list-groups":
            gstore = GroupStore(Path(args.db), args.sito)
            for g in gstore.list_groups():
                members_csv = ",".join(g.get("member_us_uuids", []))
                print(f"{g['group_uuid']}\t{g['name']}\t"
                      f"{g.get('group_kind', '')}\t{members_csv}")
        elif sub == "add-us-to-group":
            gstore = GroupStore(Path(args.db), args.sito)
            gstore.add_us_to_group(args.group_uuid, args.us_uuid)
            print(f"OK — added {args.us_uuid} to {args.group_uuid}")
        elif sub == "remove-group":
            gstore = GroupStore(Path(args.db), args.sito)
            gstore.remove_group(args.uuid)
            print(f"OK — removed {args.uuid}")
        else:
            print(f"ERROR: unknown paradata action: {sub}", file=sys.stderr)
            return 2
    except (ParadataStoreError, GroupStoreError) as e:
        print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="s3dgraphy_sync",
        description="PyArchInit ↔ s3dgraphy bridge CLI (AI04).")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_exp = sub.add_parser("export", help="DB → GraphML")
    p_exp.add_argument("--db", required=True)
    # --graphml and --output are aliases (same dest); either is required.
    grp_out = p_exp.add_mutually_exclusive_group(required=True)
    grp_out.add_argument("--graphml", dest="graphml")
    grp_out.add_argument("--output", dest="graphml")
    p_exp.add_argument("--sito", required=True)
    p_exp.add_argument("--mapping", default="pyarchinit_us_mapping")
    p_exp.add_argument("--group-by", dest="group_by",
                       help="CSV of grouping dimensions: "
                            "area,struttura,attivita,settore,ambient,"
                            "saggio,quad_par,adhoc")
    p_exp.set_defaults(func=cmd_export)

    p_imp = sub.add_parser("import", help="GraphML → DB")
    p_imp.add_argument("--db", required=True)
    p_imp.add_argument("--graphml", required=True)
    p_imp.add_argument("--sito", required=True)
    p_imp.add_argument("--apply", action="store_true",
                       help="actually write to DB (default: dry-run)")
    p_imp.add_argument("--create-epochs", action="store_true",
                       help="auto-create missing periodizzazione rows")
    p_imp.add_argument("--copy", action="store_true",
                       help="import as a COPY into --sito: regenerate every "
                            "node_uuid so the ingest INSERTs new rows instead "
                            "of matching/renaming existing ones")
    p_imp.set_defaults(func=cmd_import)

    p_para = sub.add_parser("paradata", help="Manage paradata.graphml")
    para_sub = p_para.add_subparsers(dest="paradata_action", required=True)

    p_aa = para_sub.add_parser("add-author")
    p_aa.add_argument("--db", required=True)
    p_aa.add_argument("--sito", required=True)
    p_aa.add_argument("--name", required=True)
    p_aa.add_argument("--orcid")
    p_aa.add_argument("--role")
    p_aa.set_defaults(func=cmd_paradata)

    p_la = para_sub.add_parser("list-authors")
    p_la.add_argument("--db", required=True)
    p_la.add_argument("--sito", required=True)
    p_la.set_defaults(func=cmd_paradata)

    p_al = para_sub.add_parser("add-license")
    p_al.add_argument("--db", required=True)
    p_al.add_argument("--sito", required=True)
    p_al.add_argument("--spdx", required=True)
    p_al.add_argument("--url")
    p_al.set_defaults(func=cmd_paradata)

    p_ll = para_sub.add_parser("list-licenses")
    p_ll.add_argument("--db", required=True)
    p_ll.add_argument("--sito", required=True)
    p_ll.set_defaults(func=cmd_paradata)

    p_ae = para_sub.add_parser("add-embargo")
    p_ae.add_argument("--db", required=True)
    p_ae.add_argument("--sito", required=True)
    p_ae.add_argument("--until", required=True)
    p_ae.add_argument("--reason")
    p_ae.set_defaults(func=cmd_paradata)

    p_le = para_sub.add_parser("list-embargos")
    p_le.add_argument("--db", required=True)
    p_le.add_argument("--sito", required=True)
    p_le.set_defaults(func=cmd_paradata)

    p_rm = para_sub.add_parser("remove")
    p_rm.add_argument("--db", required=True)
    p_rm.add_argument("--sito", required=True)
    p_rm.add_argument("--uuid", required=True)
    p_rm.set_defaults(func=cmd_paradata)

    # AI06 — group sub-subcommands
    p_ag = para_sub.add_parser("add-group")
    p_ag.add_argument("--db", required=True)
    p_ag.add_argument("--sito", required=True)
    p_ag.add_argument("--name", required=True)
    p_ag.add_argument("--kind", default="adhoc")
    p_ag.add_argument("--us-uuid", action="append", dest="us_uuid")
    p_ag.set_defaults(func=cmd_paradata)

    p_lg = para_sub.add_parser("list-groups")
    p_lg.add_argument("--db", required=True)
    p_lg.add_argument("--sito", required=True)
    p_lg.set_defaults(func=cmd_paradata)

    p_aug = para_sub.add_parser("add-us-to-group")
    p_aug.add_argument("--db", required=True)
    p_aug.add_argument("--sito", required=True)
    p_aug.add_argument("--group-uuid", required=True, dest="group_uuid")
    p_aug.add_argument("--us-uuid", required=True, dest="us_uuid")
    p_aug.set_defaults(func=cmd_paradata)

    p_rg = para_sub.add_parser("remove-group")
    p_rg.add_argument("--db", required=True)
    p_rg.add_argument("--sito", required=True)
    p_rg.add_argument("--uuid", required=True)
    p_rg.set_defaults(func=cmd_paradata)

    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.WARNING)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
