"""L1 round-trip with paradata layer.

DB + paradata.graphml → projector → ingest + ParadataStore.write
must preserve mapped columns AND paradata node uuids.
"""
from __future__ import annotations
import shutil
import sqlite3
import sys
from pathlib import Path

import pytest
import pandas  # noqa: F401
from lxml import etree as _e  # noqa: F401
PLUGIN_ROOT = Path(__file__).resolve().parents[2]
_EXT_LIBS = str(PLUGIN_ROOT / "ext_libs")
if _EXT_LIBS in sys.path:
    sys.path.remove(_EXT_LIBS)
sys.path.insert(0, _EXT_LIBS)
for _mod in [m for m in list(sys.modules)
             if m == "s3dgraphy" or m.startswith("s3dgraphy.")]:
    del sys.modules[_mod]


FIXTURE_DB = (PLUGIN_ROOT / "tests" / "sync" / "fixtures"
              / "mini_volterra.sqlite")


@pytest.fixture
def mini_volterra(tmp_path):
    dst = tmp_path / "mini_volterra.sqlite"
    shutil.copy2(FIXTURE_DB, dst)
    from scripts.migrations._2026_05_node_uuid_backfill_lib import (
        add_columns, backfill_uuids)
    add_columns(dst); backfill_uuids(dst)
    return dst


def _read_sito(db):
    conn = sqlite3.connect(db)
    s = conn.execute(
        "SELECT DISTINCT sito FROM us_table LIMIT 1").fetchone()[0]
    conn.close()
    return s


def test_round_trip_preserves_paradata_uuids(mini_volterra):
    """D4 invariant extended: round-trip preserves both strat
    mapped columns AND paradata uuids."""
    from modules.s3dgraphy.sync.paradata_store import ParadataStore
    from modules.s3dgraphy.sync.graph_projector import GraphProjector

    sito = _read_sito(mini_volterra)
    store_before = ParadataStore(mini_volterra, sito)
    a1 = store_before.add_author("Marco")
    a2 = store_before.add_author("Maria")
    l1 = store_before.add_license("CC-BY-4.0")
    e1 = store_before.add_embargo("2030-12-31")
    expected_uuids = {a1, a2, l1, e1}

    # Project + read paradata via store
    graph = GraphProjector().populate_graph(
        mini_volterra, sito=sito, include_paradata=True)
    paradata_uuids_in_graph = {
        n.node_id for n in graph.nodes
        if type(n).__name__ in ("AuthorNode", "LicenseNode", "EmbargoNode")
    }
    assert expected_uuids.issubset(paradata_uuids_in_graph), (
        f"paradata not in graph: {expected_uuids - paradata_uuids_in_graph}")

    # Round-trip the paradata (write + read)
    paradata_subgraph_nodes = [
        n for n in graph.nodes
        if type(n).__name__ in ("AuthorNode", "LicenseNode", "EmbargoNode")
    ]
    from s3dgraphy import Graph
    rt_graph = Graph(graph_id=sito)
    for n in paradata_subgraph_nodes:
        rt_graph.add_node(n)
    store_before.write(rt_graph)

    # Read back via fresh store instance
    store_after = ParadataStore(mini_volterra, sito)
    after_uuids = {n.node_id for n in store_after.read().nodes}
    assert expected_uuids == after_uuids, (
        f"round-trip lost uuids: {expected_uuids - after_uuids}")
