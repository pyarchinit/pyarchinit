"""yE-F render fan-out tests — _clone_node_for_location + _apply_yef_fan_out."""
from __future__ import annotations
import pytest


def test_clone_node_for_location_creates_copy_with_canonical_uuid():
    """Cloning a primary node yields a new node with fresh node_id
    but inherits class, name, description, and stamps the canonical
    UUID on attributes['node_uuid'] for round-trip identity."""
    from s3dgraphy.nodes.stratigraphic_node import StratigraphicUnit
    from modules.s3dgraphy.sync.graphml_writer import (
        _clone_node_for_location,
    )

    primary = StratigraphicUnit(
        node_id="canonical-uuid-1234",
        name="material", description="",
    )
    primary.attributes = {
        "sito": "test", "unita_tipo": "property",
        "attivita": "VA01", "d_stratigrafica": "material",
        "node_uuid": "canonical-uuid-1234",
    }

    copy = _clone_node_for_location(
        primary, location="VA04", idx=1,
        canonical_uuid="canonical-uuid-1234",
    )

    assert copy.node_id == "canonical-uuid-1234_loc_1"
    assert copy.name == "material"
    assert type(copy).__name__ == "StratigraphicUnit"
    assert copy.attributes["attivita"] == "VA04"
    assert copy.attributes["unita_tipo"] == "property"
    assert copy.attributes["d_stratigrafica"] == "material"
    assert copy.attributes["sito"] == "test"
    assert copy.attributes["_yef_canonical_uuid"] == "canonical-uuid-1234"
    assert copy.attributes["_yef_is_copy"] is True
    assert copy.attributes["node_uuid"] == "canonical-uuid-1234"
    copy.attributes["attivita"] = "X-CHANGED"
    assert primary.attributes["attivita"] == "VA01"


def test_apply_yef_fan_out_creates_n_copies():
    """Row with other_locations=['VA04','VA05'] → 3 nodes in graph
    after fan-out (1 primary + 2 copies). All share canonical uuid via
    attributes['node_uuid'] + _yef_canonical_uuid."""
    from s3dgraphy import Graph
    from s3dgraphy.nodes.stratigraphic_node import StratigraphicUnit
    from modules.s3dgraphy.sync.graphml_writer import _apply_yef_fan_out

    g = Graph(graph_id="t")
    primary = StratigraphicUnit(
        node_id="uuid-mat", name="material", description="",
    )
    primary.attributes = {
        "sito": "test", "unita_tipo": "property",
        "attivita": "VA01", "d_stratigrafica": "material",
        "node_uuid": "uuid-mat",
        "other_locations": '["VA04","VA05"]',
    }
    g.add_node(primary)

    _apply_yef_fan_out(g)

    paradata_nodes = [
        n for n in g.nodes
        if type(n).__name__ == "StratigraphicUnit"
        and (getattr(n, "attributes", None) or {}).get("d_stratigrafica") == "material"
    ]
    assert len(paradata_nodes) == 3

    locations = sorted(
        (n.attributes or {}).get("attivita") for n in paradata_nodes
    )
    assert locations == ["VA01", "VA04", "VA05"]

    canonical_uuids = {
        (n.attributes or {}).get("node_uuid") for n in paradata_nodes
    }
    assert canonical_uuids == {"uuid-mat"}

    copies_map = (getattr(g, "attributes", None) or {}).get(
        "_yef_copies_by_canonical", {}
    )
    assert "uuid-mat" in copies_map
    assert len(copies_map["uuid-mat"]) == 3


def test_apply_yef_fan_out_skipped_for_non_paradata():
    """Stratigraphic row without other_locations → no clones."""
    from s3dgraphy import Graph
    from s3dgraphy.nodes.stratigraphic_node import StratigraphicUnit
    from modules.s3dgraphy.sync.graphml_writer import _apply_yef_fan_out

    g = Graph(graph_id="t")
    us = StratigraphicUnit(node_id="u1", name="01", description="")
    us.attributes = {
        "sito": "test", "unita_tipo": "US", "attivita": "VA01",
    }
    g.add_node(us)
    initial_count = len(g.nodes)

    _apply_yef_fan_out(g)

    assert len(g.nodes) == initial_count


def test_apply_yef_fan_out_empty_other_locations_is_no_op():
    """other_locations='[]' (empty JSON list) → no fan-out."""
    from s3dgraphy import Graph
    from s3dgraphy.nodes.stratigraphic_node import StratigraphicUnit
    from modules.s3dgraphy.sync.graphml_writer import _apply_yef_fan_out

    g = Graph(graph_id="t")
    prop = StratigraphicUnit(node_id="p1", name="material", description="")
    prop.attributes = {
        "sito": "test", "unita_tipo": "property",
        "attivita": "VA01", "other_locations": "[]",
    }
    g.add_node(prop)
    initial_count = len(g.nodes)

    _apply_yef_fan_out(g)

    assert len(g.nodes) == initial_count
