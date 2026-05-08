"""D4-C (AC-7): external-graph ingestion converges after one iteration.

Three consecutive populate_list() runs against the same external
GraphML must produce identical IngestResult counts (skipped grows,
inserted/updated drop to 0 from run 2 onwards).
"""
from __future__ import annotations
import shutil
import sys
from pathlib import Path

import pytest
import pandas  # noqa: F401
from lxml import etree as _etree  # noqa: F401
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
EXTERNAL_GRAPHML = (PLUGIN_ROOT / "tests" / "sync" / "fixtures"
                    / "mini_volterra_external.graphml")


@pytest.fixture
def mini_volterra(tmp_path):
    dst = tmp_path / "mini_volterra.sqlite"
    shutil.copy2(FIXTURE_DB, dst)
    from scripts.migrations._2026_05_node_uuid_backfill_lib import (
        add_columns, backfill_uuids)
    add_columns(dst)
    backfill_uuids(dst)
    return dst


def _load_graph(graphml_path):
    from s3dgraphy.importer.import_graphml import GraphMLImporter
    importer = GraphMLImporter(filepath=str(graphml_path))
    return importer.parse()


def _read_sito(db):
    import sqlite3
    conn = sqlite3.connect(db)
    sito = conn.execute(
        "SELECT DISTINCT sito FROM us_table LIMIT 1").fetchone()[0]
    conn.close()
    return sito


def test_external_graph_ingest_idempotent(mini_volterra):
    """D4-C / AC-7 — three runs converge."""
    sito = _read_sito(mini_volterra)
    from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor

    graph = _load_graph(EXTERNAL_GRAPHML)
    g = GraphIngestor()
    r1 = g.populate_list(graph, mini_volterra, sito=sito, dry_run=False)
    r2 = g.populate_list(graph, mini_volterra, sito=sito, dry_run=False)
    r3 = g.populate_list(graph, mini_volterra, sito=sito, dry_run=False)

    # Convergence: r2 and r3 must look the same.
    # Allow r1 to insert/update; r2 onwards should be idempotent.
    assert r2.inserted == 0, f"r2 still inserting: {r2}"
    assert r2.updated == 0, f"r2 still updating: {r2}"
    assert r3.applied == r2.applied, \
        f"r3 != r2: r2={r2.applied}, r3={r3.applied}"
    assert r3.skipped == r2.skipped, \
        f"r3 skipped != r2: r2={r2.skipped}, r3={r3.skipped}"
