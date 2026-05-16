"""yE-F per-folder edge resolver tests — _resolve_target_for_folder
picks the right copy of a multi-folder paradata target node."""
from __future__ import annotations
import pytest


def _make_node(node_id, attivita, canonical=None):
    """Build a minimal StratigraphicUnit-shaped node for resolver tests."""
    from s3dgraphy.nodes.stratigraphic_node import StratigraphicUnit
    n = StratigraphicUnit(node_id=node_id, name="material", description="")
    n.attributes = {"attivita": attivita}
    if canonical:
        n.attributes["_yef_canonical_uuid"] = canonical
    return n


def test_resolver_picks_copy_with_matching_attivita():
    """source in VA04 → resolver returns the copy with attivita='VA04'."""
    from s3dgraphy import Graph
    from modules.s3dgraphy.sync.graph_projector import _resolve_target_for_folder

    primary = _make_node("uuid-mat", "VA01", "uuid-mat")
    copy_va04 = _make_node("uuid-mat_loc_1", "VA04", "uuid-mat")
    copy_va05 = _make_node("uuid-mat_loc_2", "VA05", "uuid-mat")
    g = Graph(graph_id="t")
    g.add_node(primary)
    g.add_node(copy_va04)
    g.add_node(copy_va05)
    g.attributes = {
        "_yef_copies_by_canonical": {
            "uuid-mat": [primary, copy_va04, copy_va05],
        }
    }

    target = _resolve_target_for_folder(
        primary, source_folder="VA04", graph=g,
    )
    assert target.node_id == "uuid-mat_loc_1"


def test_resolver_falls_back_to_primary_when_no_match():
    """source in VA99 (no matching copy) → resolver returns primary."""
    from s3dgraphy import Graph
    from modules.s3dgraphy.sync.graph_projector import _resolve_target_for_folder

    primary = _make_node("uuid-mat", "VA01", "uuid-mat")
    copy_va04 = _make_node("uuid-mat_loc_1", "VA04", "uuid-mat")
    g = Graph(graph_id="t")
    g.add_node(primary)
    g.add_node(copy_va04)
    g.attributes = {
        "_yef_copies_by_canonical": {
            "uuid-mat": [primary, copy_va04],
        }
    }

    target = _resolve_target_for_folder(
        primary, source_folder="VA99", graph=g,
    )
    assert target.node_id == "uuid-mat"  # primary fallback


def test_resolver_returns_target_directly_when_not_multifolder():
    """Target without _yef_copies entry → returned unchanged."""
    from s3dgraphy import Graph
    from modules.s3dgraphy.sync.graph_projector import _resolve_target_for_folder

    us = _make_node("uuid-us01", "VA01")
    g = Graph(graph_id="t")
    g.add_node(us)
    g.attributes = {"_yef_copies_by_canonical": {}}

    target = _resolve_target_for_folder(us, source_folder="VA04", graph=g)
    assert target.node_id == "uuid-us01"
