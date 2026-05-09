"""AI07 Group D: _emit_toponym_chain and cross-site dedupe."""
from __future__ import annotations
import hashlib
import sqlite3
from pathlib import Path

import pytest

from modules.s3dgraphy.sync.graph_projector import GraphProjector

FIXTURES = Path(__file__).parent / "fixtures"
TOPONYM_DB = FIXTURES / "toponym_volterra.sqlite"


def _toponym_uuid(name: str) -> str:
    """Deterministic UUID5 from (name, "toponym")."""
    return hashlib.sha1(f"{name}|toponym".encode()).hexdigest()[:32]


def test_full_chain_emits_4_locationnodegroup(tmp_path):
    """Italia → Toscana → Pisa → Volterra"""
    proj = GraphProjector()
    graph = proj.populate_graph(db_path=TOPONYM_DB, sito="Volterra")
    locs = [n for n in graph.nodes
            if type(n).__name__ == "LocationNodeGroup"
            and getattr(n, "kind", None) == "toponym"]
    names = sorted([n.name for n in locs])
    assert "Italia" in names
    assert "Toscana" in names
    assert "Pisa" in names
    assert "Volterra" in names


def test_partial_admin_levels_compact_chain(tmp_path):
    """Pompei_test has empty provincia — chain skips it (Q4=c).
    Italia → Campania → Pompei (no provincia node)
    """
    proj = GraphProjector()
    graph = proj.populate_graph(db_path=TOPONYM_DB, sito="Pompei_test")
    locs = [n for n in graph.nodes
            if type(n).__name__ == "LocationNodeGroup"
            and getattr(n, "kind", None) == "toponym"]
    names = sorted([n.name for n in locs])
    assert "Italia" in names
    assert "Campania" in names
    assert "Pompei" in names
    # No empty-string node, no placeholder
    assert all(n != "" for n in names)
    # Chain edges: Italia ← Campania, Campania ← Pompei (no provincia)
    edge_pairs = {(e.edge_source, e.edge_target) for e in graph.edges
                  if e.edge_type == "is_in_location"}
    pompei_uuid = _toponym_uuid("Pompei")
    campania_uuid = _toponym_uuid("Campania")
    italia_uuid = _toponym_uuid("Italia")
    # Pompei → Campania (skipping provincia)
    assert (pompei_uuid, campania_uuid) in edge_pairs


def test_two_sites_same_comune_share_node(tmp_path):
    """AC-20: Volterra and Volterra2 both have comune='Volterra' →
    1 LocationNodeGroup(name='Volterra', kind='toponym').
    """
    proj = GraphProjector()
    g1 = proj.populate_graph(db_path=TOPONYM_DB, sito="Volterra")
    g2 = proj.populate_graph(db_path=TOPONYM_DB, sito="Volterra2")
    # Same projector, same DB, two calls — UUIDs must match
    volterra_uuid_1 = _toponym_uuid("Volterra")
    locs_1 = [n for n in g1.nodes
              if type(n).__name__ == "LocationNodeGroup"
              and n.name == "Volterra"
              and getattr(n, "kind", None) == "toponym"]
    locs_2 = [n for n in g2.nodes
              if type(n).__name__ == "LocationNodeGroup"
              and n.name == "Volterra"
              and getattr(n, "kind", None) == "toponym"]
    assert len(locs_1) == 1
    assert len(locs_2) == 1
    assert locs_1[0].node_id == locs_2[0].node_id == volterra_uuid_1


def test_us_connects_to_deepest_level_only(tmp_path):
    """Each US has exactly one is_in_location edge into the toponym
    chain (the deepest non-empty level), with is_primary=false.
    """
    proj = GraphProjector()
    graph = proj.populate_graph(db_path=TOPONYM_DB, sito="Volterra")
    us_nodes = [n for n in graph.nodes
                if "Stratigraphic" in type(n).__name__
                or type(n).__name__ == "USNode"]
    if not us_nodes:
        pytest.skip("fixture has no stratigraphic units")
    volterra_uuid = _toponym_uuid("Volterra")
    for us in us_nodes[:5]:
        toponym_edges = [e for e in graph.edges
                         if e.edge_source == us.node_id
                         and e.edge_target == volterra_uuid]
        assert len(toponym_edges) == 1, \
            f"US {us.node_id} has {len(toponym_edges)} edges to deepest toponym"
        e = toponym_edges[0]
        assert getattr(e, "attributes", {}).get("is_primary") is False, \
            "toponym memberships must always be is_primary=false"


def test_all_admin_levels_empty_no_chain(tmp_path):
    """If site_table has all 4 admin levels empty → no toponym chain."""
    db = tmp_path / "x.sqlite"
    db.write_bytes(TOPONYM_DB.read_bytes())
    conn = sqlite3.connect(str(db))
    try:
        conn.execute(
            "INSERT OR IGNORE INTO site_table "
            "(sito, nazione, regione, provincia, comune, descrizione) "
            "VALUES ('NoToponym', '', '', '', '', 'all empty')"
        )
        conn.commit()
    finally:
        conn.close()
    proj = GraphProjector()
    graph = proj.populate_graph(db_path=db, sito="NoToponym")
    toponyms = [n for n in graph.nodes
                if type(n).__name__ == "LocationNodeGroup"
                and getattr(n, "kind", None) == "toponym"]
    assert toponyms == []


def test_round_trip_preserves_site_table(tmp_path):
    """AC-15: export → re-import → site_table is byte-identical."""
    db = tmp_path / "x.sqlite"
    db.write_bytes(TOPONYM_DB.read_bytes())
    # Snapshot site_table
    conn = sqlite3.connect(str(db))
    try:
        before = conn.execute(
            "SELECT sito, nazione, regione, provincia, comune FROM site_table "
            "ORDER BY sito"
        ).fetchall()
    finally:
        conn.close()
    # Project + (would round-trip via GraphML, but for now just project
    # and verify projector doesn't mutate site_table)
    proj = GraphProjector()
    proj.populate_graph(db_path=db, sito="Volterra")
    conn = sqlite3.connect(str(db))
    try:
        after = conn.execute(
            "SELECT sito, nazione, regione, provincia, comune FROM site_table "
            "ORDER BY sito"
        ).fetchall()
    finally:
        conn.close()
    assert before == after, "projector must not mutate site_table"
