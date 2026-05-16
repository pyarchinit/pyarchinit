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
