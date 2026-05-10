"""AI07 Group F: on-read up-conversion of legacy 5.5.x ActivityNodeGroup.

These tests exercise ``_promote_legacy_activitynodegroup`` directly on
in-memory ``s3dgraphy.Graph`` objects. We don't go through GraphMLImporter
because s3dgraphy's importer determines group-node subclass from yEd
background colour, not from data keys, so a hand-crafted GraphML without
yEd graphics decays into plain ``GroupNode`` regardless of intent. The
production call site (``GraphIngestor.populate_list``) operates on
already-parsed Graphs, so the test surface matches reality.

The :file:`fixtures/legacy_5_5_x.graphml` file is committed alongside as
a reference for what AI06-era exports look like on disk.
"""
from __future__ import annotations

import warnings
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"
LEGACY = FIXTURES / "legacy_5_5_x.graphml"


def _build_legacy_graph():
    """Construct a Graph mimicking AI06 output: 4 ActivityNodeGroup
    nodes whose ``attributes['group_kind']`` is set to one of the 7
    SQL-derived dimensions (only attivita stays as ActivityNodeGroup
    after promotion; the 3 spatial ones must be promoted to
    LocationNodeGroup).
    """
    from s3dgraphy import Graph
    from s3dgraphy.nodes.group_node import ActivityNodeGroup
    g = Graph(graph_id="test_legacy")

    specs = [
        ("grp_attivita", "Saggio_I", "attivita"),
        ("grp_struttura", "Basilica", "struttura"),
        ("grp_area", "A", "area"),
        ("grp_settore", "Settore_N", "settore"),
    ]
    for nid, name, kind in specs:
        n = ActivityNodeGroup(node_id=nid, name=name)
        n.attributes["group_kind"] = kind
        g.add_node(n)
    return g


def test_legacy_5_5_x_fixture_exists():
    """Smoke: the on-disk fixture is committed to fixtures/."""
    assert LEGACY.exists(), f"missing {LEGACY}"
    assert LEGACY.stat().st_size > 0


def test_legacy_5_5_x_promoted_in_memory():
    """3 of 4 ActivityNodeGroup nodes promoted to LocationNodeGroup."""
    from modules.s3dgraphy.sync.graph_ingestor import (
        _promote_legacy_activitynodegroup,
    )
    g = _build_legacy_graph()
    n_before_act = sum(1 for n in g.nodes
                       if type(n).__name__ == "ActivityNodeGroup")
    assert n_before_act == 4, f"fixture must have 4 ANG, got {n_before_act}"
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        _promote_legacy_activitynodegroup(g)
    n_after_act = sum(1 for n in g.nodes
                      if type(n).__name__ == "ActivityNodeGroup")
    n_after_loc = sum(1 for n in g.nodes
                      if type(n).__name__ == "LocationNodeGroup")
    assert n_after_act == 1, f"only attivita stays as ANG, got {n_after_act}"
    assert n_after_loc == 3, f"3 spatial promoted to LNG, got {n_after_loc}"


def test_attivita_stays_activitynodegroup():
    """attivita group_kind must NOT be promoted."""
    from modules.s3dgraphy.sync.graph_ingestor import (
        _promote_legacy_activitynodegroup,
    )
    g = _build_legacy_graph()
    _promote_legacy_activitynodegroup(g)
    activities = [n for n in g.nodes
                  if type(n).__name__ == "ActivityNodeGroup"]
    assert len(activities) == 1
    assert getattr(activities[0], "node_id", None) == "grp_attivita"


def test_warning_emitted_once_per_call():
    """One DeprecationWarning per _promote call, not per node."""
    from modules.s3dgraphy.sync.graph_ingestor import (
        _promote_legacy_activitynodegroup,
    )
    g = _build_legacy_graph()
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        _promote_legacy_activitynodegroup(g)
    deprec = [x for x in w if issubclass(x.category, DeprecationWarning)]
    assert len(deprec) == 1, \
        f"expected 1 DeprecationWarning, got {len(deprec)}"
    assert "legacy" in str(deprec[0].message).lower()
    assert ("5.6.0" in str(deprec[0].message)
            or "AI07" in str(deprec[0].message))


def test_unknown_group_kind_left_as_activitynodegroup():
    """ActivityNodeGroup with custom group_kind (not in
    SQL_BACKED_KINDS_SPATIAL) stays untouched and emits no warning."""
    from s3dgraphy import Graph
    from s3dgraphy.nodes.group_node import ActivityNodeGroup
    from modules.s3dgraphy.sync.graph_ingestor import (
        _promote_legacy_activitynodegroup,
    )
    g = Graph(graph_id="test_unknown_kind")
    n = ActivityNodeGroup(node_id="x", name="X")
    n.attributes["group_kind"] = "custom_dim_2026"
    g.add_node(n)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        _promote_legacy_activitynodegroup(g)
    survivors = [m for m in g.nodes
                 if type(m).__name__ == "ActivityNodeGroup"]
    assert len(survivors) == 1
    # No deprecation warning emitted (nothing to promote)
    deprec = [x for x in w if issubclass(x.category, DeprecationWarning)]
    assert len(deprec) == 0
