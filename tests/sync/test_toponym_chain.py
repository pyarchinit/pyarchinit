"""AI07 Group D: _emit_toponym_chain and cross-site dedupe."""
# NB (2026-10-08): dalla 5.13.43 ``populate_graph`` NON porta piu i gruppi di
# luogo nel grafo che esce — la vista Matrix di EMStudio, finche nel file c'e
# un arco ``is_in_location``, ammucchia tutte le unita nella prima fascia.
# I gruppi si costruiscono ancora: queste prove li chiedono con
# ``location_groups=True``, che e esattamente quello che vogliono provare.
# Il default nuovo e fissato in tests/sync/test_graph_projector_multisite.py.

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
    graph = proj.populate_graph(db_path=TOPONYM_DB, sito="Volterra", location_groups=True)
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
    graph = proj.populate_graph(db_path=TOPONYM_DB, sito="Pompei_test", location_groups=True)
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


def _place_ids(db, sito):
    """L'id che la libreria assegna al luogo del sito: site_table.entity_uuid
    quando c'è, altrimenti l'hash del nome."""
    from s3dgraphy.hdto import site_place_id
    conn = sqlite3.connect(str(db))
    try:
        row = conn.execute("SELECT entity_uuid FROM site_table WHERE sito=?",
                           (sito,)).fetchone()
    finally:
        conn.close()
    return site_place_id(sito, row[0] if row else None)


def _toponyms(graph, level=None):
    return [n for n in graph.nodes
            if type(n).__name__ == "LocationNodeGroup"
            and getattr(n, "kind", None) == "toponym"
            and (level is None or n.attributes.get("level") == level)]


def test_two_sites_same_comune_share_node(tmp_path):
    """AC-20: Volterra and Volterra2 both have comune='Volterra' → il livello
    amministrativo «comune» è UN nodo condiviso; dalla dev43 ogni sito ha in
    più il proprio luogo (kind toponym, level «sito»), distinto per sito."""
    proj = GraphProjector()
    g1 = proj.populate_graph(db_path=TOPONYM_DB, sito="Volterra", location_groups=True)
    g2 = proj.populate_graph(db_path=TOPONYM_DB, sito="Volterra2", location_groups=True)
    volterra_uuid_1 = _toponym_uuid("Volterra")

    # il comune: un nodo, lo stesso id nei due grafi
    comuni_1 = [n for n in _toponyms(g1, "comune") if n.name == "Volterra"]
    comuni_2 = [n for n in _toponyms(g2, "comune") if n.name == "Volterra"]
    assert len(comuni_1) == 1
    assert len(comuni_2) == 1
    assert comuni_1[0].node_id == comuni_2[0].node_id == volterra_uuid_1

    # il sito: un luogo per grafo, con l'id annunciato da site_place_id,
    # diverso da quello del comune anche quando il nome coincide
    siti_1, siti_2 = _toponyms(g1, "sito"), _toponyms(g2, "sito")
    assert len(siti_1) == 1 and len(siti_2) == 1
    assert siti_1[0].kind == "toponym"
    assert siti_1[0].attributes["level"] == "sito"
    assert siti_1[0].name == "Volterra" and siti_2[0].name == "Volterra2"
    assert siti_1[0].node_id == _place_ids(TOPONYM_DB, "Volterra")
    assert siti_2[0].node_id == _place_ids(TOPONYM_DB, "Volterra2")
    assert siti_1[0].node_id != volterra_uuid_1
    assert siti_1[0].node_id != siti_2[0].node_id

    # il sito sta nel livello amministrativo più profondo
    archi = {(e.edge_source, e.edge_target) for e in g1.edges
             if e.edge_type == "is_in_location"}
    assert (siti_1[0].node_id, volterra_uuid_1) in archi


def test_us_connects_to_deepest_level_only(tmp_path):
    """Each US has exactly one is_in_location edge into the toponym
    chain (the deepest non-empty level), with is_primary=false.
    """
    proj = GraphProjector()
    graph = proj.populate_graph(db_path=TOPONYM_DB, sito="Volterra", location_groups=True)
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
    """Con i quattro livelli amministrativi vuoti non c'è catena
    amministrativa, ma dalla dev43 il luogo del sito esiste comunque: un
    solo LocationNodeGroup (kind toponym, level «sito»), senza archi di
    catena (non ha un livello sopra) e senza archi US → luogo."""
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
    graph = proj.populate_graph(db_path=db, sito="NoToponym", location_groups=True)
    toponyms = _toponyms(graph)
    # nessun livello amministrativo...
    assert [n for n in toponyms if n.attributes.get("level") != "sito"] == []
    # ...ma il luogo del sito sì, con l'id annunciato
    assert len(toponyms) == 1
    place = toponyms[0]
    assert place.attributes["level"] == "sito"
    assert place.name == "NoToponym"
    assert place.node_id == _place_ids(db, "NoToponym")
    assert not [e for e in graph.edges
                if e.edge_type == "is_in_location"
                and place.node_id in (e.edge_source, e.edge_target)]


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
    proj.populate_graph(db_path=db, sito="Volterra", location_groups=True)
    conn = sqlite3.connect(str(db))
    try:
        after = conn.execute(
            "SELECT sito, nazione, regione, provincia, comune FROM site_table "
            "ORDER BY sito"
        ).fetchall()
    finally:
        conn.close()
    assert before == after, "projector must not mutate site_table"
