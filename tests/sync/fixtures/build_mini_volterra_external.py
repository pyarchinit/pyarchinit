"""Generate the AI04 external-graph test fixtures.

Reads mini_volterra.sqlite, projects it via GraphProjector, then
emits two GraphML files:

1. mini_volterra_external.graphml — projection with one node's
   d_stratigrafica mutated; ingesting this back should produce
   exactly one ConflictRecord and one updated row.

2. mini_volterra_external_with_new_epoch.graphml — projection plus
   one synthetic EpochNode (periodo=99, fase='9.9') NOT in
   periodizzazione_table; used by the create-missing-epochs test.

Run: python tests/sync/fixtures/build_mini_volterra_external.py
Idempotent — re-running produces structurally identical files.

The fixture mini_volterra.sqlite needs the Phase 1 node_uuid
migration applied; this script applies it to a temp copy so the
on-disk fixture stays unchanged.
"""
from __future__ import annotations
import shutil
import sys
import tempfile
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[3]
# Ensure plugin root is on path so `modules.*` resolves.
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))
# Pre-import system pandas / lxml BEFORE ext_libs goes on sys.path,
# so the bundled (often platform-mismatched) pandas in ext_libs does
# not shadow the working system pandas.
import pandas  # noqa: F401
from lxml import etree as _etree  # noqa: F401
# Now make ext_libs available so `s3dgraphy` (vendored) resolves.
_EXT_LIBS = str(PLUGIN_ROOT / "ext_libs")
if _EXT_LIBS in sys.path:
    sys.path.remove(_EXT_LIBS)
sys.path.insert(0, _EXT_LIBS)
for _mod in [m for m in list(sys.modules)
             if m == "s3dgraphy" or m.startswith("s3dgraphy.")]:
    del sys.modules[_mod]

from modules.s3dgraphy.sync.graph_projector import GraphProjector

FIX = PLUGIN_ROOT / "tests" / "sync" / "fixtures"
SRC = FIX / "mini_volterra.sqlite"


def _migrated_copy() -> Path:
    """Copy SRC to a tmp path with the Phase 1 node_uuid migration applied."""
    from scripts.migrations._2026_05_node_uuid_backfill_lib import (
        add_columns, backfill_uuids)
    tmp = Path(tempfile.mkdtemp()) / "mini_volterra.sqlite"
    shutil.copy2(SRC, tmp)
    add_columns(tmp)
    backfill_uuids(tmp)
    return tmp


def _write_graphml(graph, out: Path) -> None:
    """Serialise via s3dgraphy GraphMLExporter, then run the
    _embed_pyarchinit_data_keys post-processor so the fixture
    carries the data keys AI04 import can recover."""
    from s3dgraphy.exporter.graphml.graphml_exporter import GraphMLExporter
    from modules.s3dgraphy.sync.graphml_writer import (
        _embed_pyarchinit_data_keys)
    exporter = GraphMLExporter(graph)
    exporter.export(str(out), persist_auxiliary=False)
    _embed_pyarchinit_data_keys(graph, out)


def main() -> int:
    import sqlite3
    db = _migrated_copy()
    conn = sqlite3.connect(db)
    sito = conn.execute(
        "SELECT DISTINCT sito FROM us_table LIMIT 1").fetchone()[0]
    conn.close()

    p = GraphProjector()

    # 1. base external graph (mutate one d_stratigrafica)
    graph = p.populate_graph(db, sito=sito)
    for n in graph.nodes:
        attrs = getattr(n, "attributes", None) or {}
        if attrs.get("us"):
            attrs["d_stratigrafica"] = "EXT_GRAPH_VALUE"
            break
    _write_graphml(graph, FIX / "mini_volterra_external.graphml")
    print("OK — mini_volterra_external.graphml written")

    # 2. external with new epoch
    graph2 = p.populate_graph(db, sito=sito)
    from s3dgraphy.nodes.epoch_node import EpochNode
    e = EpochNode(node_id="epoch_99_9_9_synthetic",
                  name="Synthetic Period 99 Phase 9.9",
                  start_time=0.0, end_time=0.0)
    e.attributes = {"periodo": 99, "fase": "9.9"}
    graph2.add_node(e)
    _write_graphml(graph2,
                   FIX / "mini_volterra_external_with_new_epoch.graphml")
    print("OK — mini_volterra_external_with_new_epoch.graphml written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
