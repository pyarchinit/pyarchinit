"""Tests for GraphProjector. Pins:
- D2 — wrap pattern (calls _enrich_pyarchinit_graph)
- D6 — sito parameter mandatory
- AC-1 — non-empty graph, filtered by sito
"""
from __future__ import annotations
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


@pytest.fixture
def mini_volterra(tmp_path):
    import shutil
    dst = tmp_path / "mini_volterra.sqlite"
    shutil.copy2(FIXTURE_DB, dst)
    # Apply Phase 1 node_uuid migration (idempotent) — required by
    # GraphProjector.populate_graph().
    from scripts.migrations._2026_05_node_uuid_backfill_lib import (
        add_columns, backfill_uuids)
    add_columns(dst)
    backfill_uuids(dst)
    return dst


def test_populate_graph_requires_sito(mini_volterra):
    """D6 — empty sito is rejected."""
    from modules.s3dgraphy.sync.graph_projector import (
        GraphProjector, ProjectionError)
    p = GraphProjector()
    with pytest.raises(ProjectionError, match="sito"):
        p.populate_graph(mini_volterra, sito="")


def test_populate_graph_missing_db_raises(tmp_path):
    from modules.s3dgraphy.sync.graph_projector import (
        GraphProjector, ProjectionError)
    p = GraphProjector()
    with pytest.raises(ProjectionError, match="not found"):
        p.populate_graph(tmp_path / "nope.sqlite", sito="X")


def test_populate_graph_missing_node_uuid_column_raises(tmp_path):
    """SchemaMismatchError-equivalent: node_uuid column required."""
    import sqlite3
    from modules.s3dgraphy.sync.graph_projector import (
        GraphProjector, ProjectionError)
    db = tmp_path / "x.sqlite"
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE us_table (id_us INTEGER PRIMARY KEY, "
                 "sito TEXT, us TEXT)")  # no node_uuid
    conn.commit()
    conn.close()
    p = GraphProjector()
    with pytest.raises(ProjectionError, match="node_uuid"):
        p.populate_graph(db, sito="X")


def test_projector_returns_filtered_graph(mini_volterra):
    """AC-1 — non-empty graph, every strat node matches sito."""
    from modules.s3dgraphy.sync.graph_projector import GraphProjector
    p = GraphProjector()
    # Find the sito present in the fixture
    import sqlite3
    conn = sqlite3.connect(mini_volterra)
    sito = conn.execute(
        "SELECT DISTINCT sito FROM us_table LIMIT 1").fetchone()[0]
    conn.close()
    graph = p.populate_graph(mini_volterra, sito=sito)
    assert len(graph.nodes) > 0
    # Every node with sito attribute must match — EpochNodes have no sito.
    for n in graph.nodes:
        attrs = getattr(n, "attributes", None) or {}
        if "sito" in attrs:
            assert attrs["sito"] == sito


def test_projector_delegates_to_enrich_function(mini_volterra, monkeypatch):
    """D2 — verify GraphProjector calls _enrich_pyarchinit_graph
    (Strategy D wrap pattern)."""
    from modules.s3dgraphy.sync import graph_projector as gp_mod
    calls = []
    # Monkey-patch the local reference in graphml_writer (the module
    # graph_projector imports the function from); we need to patch
    # the binding inside GraphProjector.populate_graph at call-time.
    from modules.s3dgraphy.sync import graphml_writer
    original = graphml_writer._enrich_pyarchinit_graph

    def spy(graph, db_path, sito_filter=None):
        calls.append((db_path, sito_filter))
        return original(graph, db_path, sito_filter=sito_filter)
    monkeypatch.setattr(graphml_writer, "_enrich_pyarchinit_graph", spy)

    import sqlite3
    conn = sqlite3.connect(mini_volterra)
    sito = conn.execute(
        "SELECT DISTINCT sito FROM us_table LIMIT 1").fetchone()[0]
    conn.close()

    p = gp_mod.GraphProjector()
    p.populate_graph(mini_volterra, sito=sito)
    assert len(calls) == 1, "GraphProjector must call _enrich_pyarchinit_graph"
    assert calls[0][1] == sito, "sito_filter must be propagated"
