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
