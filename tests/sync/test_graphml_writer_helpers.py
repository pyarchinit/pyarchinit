"""Unit tests for graphml_writer helpers (no QGIS, no real DB)."""
from __future__ import annotations

import pytest


def test_export_result_holds_metrics():
    from modules.s3dgraphy.sync.graphml_writer import ExportResult
    r = ExportResult(
        output_path="/tmp/x.graphml",
        node_count=10,
        edge_count=15,
        epoch_count=2,
        tred_removed_edges=3,
        warnings=[],
    )
    assert r.output_path == "/tmp/x.graphml"
    assert r.node_count == 10
    assert r.edge_count == 15
    assert r.epoch_count == 2
    assert r.tred_removed_edges == 3
    assert r.warnings == []


def test_export_result_warnings_default_empty_list():
    from modules.s3dgraphy.sync.graphml_writer import ExportResult
    r = ExportResult(
        output_path="/tmp/x.graphml",
        node_count=1,
        edge_count=0,
        epoch_count=0,
        tred_removed_edges=0,
    )
    assert r.warnings == []
    # Two instances must NOT share the same default list (the classic
    # mutable-default trap — frozen dataclass + field(default_factory=list)).
    r2 = ExportResult(
        output_path="/tmp/y.graphml",
        node_count=2,
        edge_count=0,
        epoch_count=0,
        tred_removed_edges=0,
    )
    r.warnings.append("test")
    assert r2.warnings == [], (
        "ExportResult instances share warnings list — mutable default bug")


def test_graphml_export_error_categorises_stage():
    from modules.s3dgraphy.sync.graphml_writer import GraphMLExportError
    inner = ValueError("bad json mapping")
    e = GraphMLExportError("import", inner)
    assert e.stage == "import"
    assert e.original is inner
    assert "import" in str(e)
    assert "ValueError" in str(e)


def test_graphml_export_error_accepts_only_known_stages():
    from modules.s3dgraphy.sync.graphml_writer import (
        GraphMLExportError,
        VALID_STAGES,
    )
    assert "import" in VALID_STAGES
    assert "filter" in VALID_STAGES
    assert "export" in VALID_STAGES
    assert "write" in VALID_STAGES
    with pytest.raises(ValueError, match="unknown stage"):
        GraphMLExportError("nonsense", ValueError("x"))


def test_empty_graph_error_is_value_error():
    from modules.s3dgraphy.sync.graphml_writer import EmptyGraphError
    assert issubclass(EmptyGraphError, ValueError)
    e = EmptyGraphError("no rows for site Volterra")
    assert "Volterra" in str(e)


def _make_test_graph():
    """Build a minimal s3dgraphy Graph for filter testing.

    2 stratigraphic units (one per site), 2 epoch nodes,
    has_first_epoch edges connecting them.

    Note: ext_libs is appended (not inserted) to sys.path so the system
    pandas (vendored ext_libs/pandas can be broken on some installs)
    wins on import resolution. s3dgraphy itself is only available under
    ext_libs/, so it still resolves correctly.
    """
    import sys
    ext_libs = (
        "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/"
        "default/python/plugins/pyarchinit/ext_libs")
    if ext_libs not in sys.path:
        sys.path.append(ext_libs)
    from s3dgraphy.graph import Graph
    from s3dgraphy.nodes.stratigraphic_node import StratigraphicUnit
    from s3dgraphy.nodes.epoch_node import EpochNode

    g = Graph(graph_id="test")
    us_a = StratigraphicUnit(node_id="us_a", name="US-A", description="")
    us_a.attributes["sito"] = "SiteA"
    us_b = StratigraphicUnit(node_id="us_b", name="US-B", description="")
    us_b.attributes["sito"] = "SiteB"
    epoch_1 = EpochNode(node_id="ep_1", name="Epoch1", start_time=0, end_time=100)
    epoch_2 = EpochNode(node_id="ep_2", name="Epoch2", start_time=100, end_time=200)
    g.add_node(us_a)
    g.add_node(us_b)
    g.add_node(epoch_1)
    g.add_node(epoch_2)
    # NOTE: Graph.add_edge takes 4 positional strings, not an Edge object.
    g.add_edge("e1", "us_a", "ep_1", "has_first_epoch")
    g.add_edge("e2", "us_b", "ep_2", "has_first_epoch")
    return g


def test_filter_by_site_keeps_only_matching_strat_nodes():
    from modules.s3dgraphy.sync.graphml_writer import _filter_by_site
    g = _make_test_graph()
    out = _filter_by_site(g, "SiteA")
    strat_ids = {n.node_id for n in out.nodes
                 if hasattr(n, "attributes") and n.attributes.get("sito")}
    assert strat_ids == {"us_a"}, f"expected only us_a, got {strat_ids!r}"


def test_filter_by_site_retains_reachable_epoch_nodes():
    from modules.s3dgraphy.sync.graphml_writer import _filter_by_site
    from s3dgraphy.nodes.epoch_node import EpochNode
    g = _make_test_graph()
    out = _filter_by_site(g, "SiteA")
    epoch_ids = {n.node_id for n in out.nodes if isinstance(n, EpochNode)}
    # ep_1 is reachable from us_a; ep_2 is reachable only from the
    # discarded us_b, so it must NOT survive the filter.
    assert epoch_ids == {"ep_1"}, f"expected {{ep_1}}, got {epoch_ids!r}"


def test_filter_by_site_prunes_orphan_edges():
    from modules.s3dgraphy.sync.graphml_writer import _filter_by_site
    g = _make_test_graph()
    out = _filter_by_site(g, "SiteA")
    edge_ids = {e.edge_id for e in out.edges}
    # e2 connected discarded us_b → discarded ep_2; must be pruned.
    assert edge_ids == {"e1"}, f"expected {{e1}}, got {edge_ids!r}"


def test_filter_by_site_returns_unfiltered_when_none():
    from modules.s3dgraphy.sync.graphml_writer import _filter_by_site
    g = _make_test_graph()
    out = _filter_by_site(g, None)
    assert len(out.nodes) == len(g.nodes)
    assert len(out.edges) == len(g.edges)
