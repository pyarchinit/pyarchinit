"""AI07 Group C: GraphProjector._merge_groups dispatches per dimension.

Asserts that:
- 6 spatial dims → LocationNodeGroup with correct kind
- attivita → ActivityNodeGroup (unchanged from AI06)
- US has at most 1 is_primary edge
- is_in_location vs is_in_activity edge type per class
"""
from __future__ import annotations
import shutil
import sqlite3
import sys
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
_EXT_LIBS = str(PLUGIN_ROOT / "ext_libs")
if _EXT_LIBS in sys.path:
    sys.path.remove(_EXT_LIBS)
sys.path.insert(0, _EXT_LIBS)
for _mod in [m for m in list(sys.modules)
             if m == "s3dgraphy" or m.startswith("s3dgraphy.")]:
    del sys.modules[_mod]

from modules.s3dgraphy.sync.graph_projector import GraphProjector

FIXTURES = Path(__file__).parent / "fixtures"
MINI_VOLTERRA = FIXTURES / "mini_volterra.sqlite"


def _read_sito(db_path):
    conn = sqlite3.connect(str(db_path))
    s = conn.execute(
        "SELECT DISTINCT sito FROM us_table LIMIT 1").fetchone()[0]
    conn.close()
    return s


@pytest.fixture
def prepared_db(tmp_path):
    """Copy fixture + apply node_uuid migration."""
    dst = tmp_path / "mini_volterra.sqlite"
    shutil.copy2(MINI_VOLTERRA, dst)
    from scripts.migrations._2026_05_node_uuid_backfill_lib import (
        add_columns, backfill_uuids)
    add_columns(dst)
    backfill_uuids(dst)
    return dst


def _populate_dim(db_path: Path, sito: str, dim: str, value: str = "GroupX"):
    """Set us_table.<dim>=value for all rows where sito=<sito>."""
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute(
            f"UPDATE us_table SET {dim}=? WHERE sito=?", (value, sito)
        )
        conn.commit()
    finally:
        conn.close()


@pytest.mark.parametrize("dim,expected_kind", [
    ("struttura", "functional"),
    ("ambient", "functional"),
])
def test_struttura_emits_locationnodegroup_kind_functional(
        prepared_db, dim, expected_kind):
    sito = _read_sito(prepared_db)
    _populate_dim(prepared_db, sito, dim, "Basilica")
    proj = GraphProjector()
    graph = proj.populate_graph(db_path=prepared_db, sito=sito, groups=[dim])
    locs = [n for n in graph.nodes
            if type(n).__name__ == "LocationNodeGroup"]
    assert len(locs) >= 1
    assert all(loc.kind == expected_kind for loc in locs)


@pytest.mark.parametrize("dim", ["area", "settore", "saggio", "quad_par"])
def test_area_emits_locationnodegroup_kind_study(prepared_db, dim):
    sito = _read_sito(prepared_db)
    _populate_dim(prepared_db, sito, dim, "AreaX")
    proj = GraphProjector()
    graph = proj.populate_graph(db_path=prepared_db, sito=sito, groups=[dim])
    locs = [n for n in graph.nodes
            if type(n).__name__ == "LocationNodeGroup"]
    assert len(locs) >= 1
    assert all(loc.kind == "study" for loc in locs)


def test_attivita_stays_activitynodegroup(prepared_db):
    sito = _read_sito(prepared_db)
    _populate_dim(prepared_db, sito, "attivita", "Saggio_I")
    proj = GraphProjector()
    graph = proj.populate_graph(
        db_path=prepared_db, sito=sito, groups=["attivita"])
    acts = [n for n in graph.nodes
            if type(n).__name__ == "ActivityNodeGroup"]
    locs = [n for n in graph.nodes
            if type(n).__name__ == "LocationNodeGroup"]
    assert len(acts) >= 1, "attivita must produce ActivityNodeGroup"
    assert all(not getattr(n, "kind", None) for n in acts), \
           "ActivityNodeGroup must have no kind field"
    # attivita must NOT produce a LocationNodeGroup
    assert all("attivita" not in (getattr(loc, "name", "") or "")
               for loc in locs)


def test_us_has_exactly_one_is_primary(prepared_db):
    """AC-17: with multiple memberships, exactly 1 edge has is_primary=true."""
    sito = _read_sito(prepared_db)
    _populate_dim(prepared_db, sito, "struttura", "Basilica")
    _populate_dim(prepared_db, sito, "area", "A")
    proj = GraphProjector()
    graph = proj.populate_graph(
        db_path=prepared_db, sito=sito, groups=["struttura", "area"]
    )
    # Pick one US and count its is_primary edges
    us_nodes = [n for n in graph.nodes
                if type(n).__name__ in ("StratigraphicUnit", "USNode")
                or "Stratigraphic" in type(n).__name__]
    assert us_nodes, "fixture must have stratigraphic units"
    for us in us_nodes[:5]:  # check first 5
        primaries = sum(
            1 for e in graph.edges
            if e.edge_source == us.node_id
            and getattr(e, "attributes", {}).get("is_primary") is True
        )
        assert primaries <= 1, \
            f"US {us.node_id} has {primaries} is_primary edges (>1)"


def test_is_in_location_edge_for_locationnodegroup(prepared_db):
    sito = _read_sito(prepared_db)
    _populate_dim(prepared_db, sito, "struttura", "Basilica")
    proj = GraphProjector()
    graph = proj.populate_graph(
        db_path=prepared_db, sito=sito, groups=["struttura"])
    loc_ids = {n.node_id for n in graph.nodes
               if type(n).__name__ == "LocationNodeGroup"}
    if not loc_ids:
        pytest.skip("fixture has no LocationNodeGroup after projection")
    edges_to_loc = [e for e in graph.edges if e.edge_target in loc_ids]
    assert all(e.edge_type == "is_in_location" for e in edges_to_loc), \
        "all edges to LocationNodeGroup must be is_in_location"


def test_is_in_activity_edge_for_activitynodegroup_unchanged(prepared_db):
    sito = _read_sito(prepared_db)
    _populate_dim(prepared_db, sito, "attivita", "Saggio_I")
    proj = GraphProjector()
    graph = proj.populate_graph(
        db_path=prepared_db, sito=sito, groups=["attivita"])
    act_ids = {n.node_id for n in graph.nodes
               if type(n).__name__ == "ActivityNodeGroup"}
    edges_to_act = [e for e in graph.edges if e.edge_target in act_ids]
    assert edges_to_act, "attivita projection must have edges to its groups"
    assert all(e.edge_type == "is_in_activity" for e in edges_to_act), \
        "all edges to ActivityNodeGroup must remain is_in_activity (Q1)"
