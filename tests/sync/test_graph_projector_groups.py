"""L1 fixture-based: populate_graph(groups=...) kwarg semantics.

Pins D4 (ActivityNodeGroup + group_kind), D7 (default empty),
AC-4, AC-5.
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


def _seed(db, sito, col, value, n=2):
    conn = sqlite3.connect(db)
    rows = list(conn.execute(
        "SELECT id_us FROM us_table WHERE sito=? LIMIT ?", (sito, n)))
    for (id_us,) in rows:
        conn.execute(
            f"UPDATE us_table SET {col}=? WHERE id_us=?",
            (value, id_us))
    conn.commit()
    conn.close()


def test_default_groups_empty_no_group_nodes(mini_volterra):
    """D7: default groups=None / [] -> no GroupNode in graph."""
    from modules.s3dgraphy.sync.graph_projector import GraphProjector
    sito = _read_sito(mini_volterra)
    graph = GraphProjector().populate_graph(mini_volterra, sito=sito)
    types = [type(n).__name__ for n in graph.nodes]
    assert "ActivityNodeGroup" not in types


def test_groups_arg_materializes_activity_node_group(mini_volterra):
    """D4 / AC-4: groups=['struttura'] yields ActivityNodeGroup
    instances with attributes['group_kind']='struttura'."""
    from modules.s3dgraphy.sync.graph_projector import GraphProjector
    sito = _read_sito(mini_volterra)
    _seed(mini_volterra, sito, "struttura", "basilica", 3)

    graph = GraphProjector().populate_graph(
        mini_volterra, sito=sito, groups=["struttura"])
    groups = [n for n in graph.nodes
              if type(n).__name__ == "ActivityNodeGroup"]
    assert len(groups) >= 1
    g = groups[0]
    attrs = getattr(g, "attributes", None) or {}
    assert attrs.get("group_kind") == "struttura"


def test_groups_arg_adds_is_in_activity_edges(mini_volterra):
    """AC-5: edges from each US member to its group, type
    is_in_activity."""
    from modules.s3dgraphy.sync.graph_projector import GraphProjector
    sito = _read_sito(mini_volterra)
    _seed(mini_volterra, sito, "struttura", "basilica", 3)

    graph = GraphProjector().populate_graph(
        mini_volterra, sito=sito, groups=["struttura"])
    group_ids = {n.node_id for n in graph.nodes
                 if type(n).__name__ == "ActivityNodeGroup"}
    rel_edges = [e for e in graph.edges
                 if getattr(e, "edge_target", None) in group_ids
                 and getattr(e, "edge_type", "") == "is_in_activity"]
    assert len(rel_edges) >= 3
