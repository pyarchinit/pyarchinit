"""PG-Bv2 (5.7.9-alpha): tests for the SQLAlchemy-native PG importer
that replaces the upstream PyArchInitImporter (SQLite-only) in
graph_projector.populate_graph() when backend is PG.

2 L0 tests run everywhere (no PG runtime needed). 2 L2 PG tests
skip cleanly when psycopg2 missing or PG offline.
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Import pg_with_volterra fixture explicitly — conftest_pg.py is not
# auto-discovered (file is named conftest_pg not conftest).
# pg_with_volterra yields a SQLAlchemy Engine seeded with mini_volterra data.
from tests.sync.conftest_pg import pg_engine, pg_with_volterra  # noqa: F401


# ---------------------------------------------------------------------
# L0 — no PG runtime needed
# ---------------------------------------------------------------------

def test_pg_importer_mapping_json_resolves():
    """``_load_mapping`` must find pyarchinit_us_mapping.json and
    return a dict with the expected schema (table_settings,
    column_mappings keys)."""
    from modules.s3dgraphy.sync.pyarchinit_pg_importer import (
        _load_mapping,
    )
    mapping = _load_mapping("pyarchinit_us_mapping")
    assert isinstance(mapping, dict)
    assert "table_settings" in mapping
    assert mapping["table_settings"].get("table_name") == "us_table"
    assert "column_mappings" in mapping
    # At least one is_id column and at least one PropertyNode column.
    cols = mapping["column_mappings"]
    assert any(spec.get("is_id") for spec in cols.values()), (
        "no is_id column in mapping — importer cannot identify nodes"
    )
    assert any(
        spec.get("node_type") == "PropertyNode"
        for spec in cols.values()
    ), "no PropertyNode columns in mapping — nothing to build"


def test_pg_importer_builds_strat_node_from_mock_row():
    """``import_from_pg`` must build a StratigraphicNode named
    after the is_id column value and PropertyNodes for each
    PropertyNode-typed column. Uses mocked DbHandle to avoid PG
    runtime."""
    from modules.s3dgraphy.sync.pyarchinit_pg_importer import (
        import_from_pg,
    )

    # Mock handle.engine.connect().execute().mappings().all()
    fake_row = {
        "us": "1",
        "sito": "S",
        "d_stratigrafica": "test layer",
        "d_interpretativa": "test interp",
        "attivita": "AC1",
        "struttura": "STR1",
        "unita_tipo": "US",
        "node_uuid": "abc-123",
    }
    fake_cm = MagicMock()
    fake_cm.execute.return_value.mappings.return_value.all.return_value = (
        [fake_row]
    )
    fake_engine = MagicMock()
    fake_engine.connect.return_value.__enter__.return_value = fake_cm
    fake_engine.connect.return_value.__exit__.return_value = None
    handle = MagicMock()
    handle.is_postgres = True
    handle.engine = fake_engine

    graph = import_from_pg(handle, sito="S",
                           mapping_name="pyarchinit_us_mapping")

    node_names = [getattr(n, "name", None) for n in graph.nodes]
    assert "1" in node_names, (
        f"StratigraphicNode named '1' missing — got {node_names}"
    )

    # Each PropertyNode-typed column from the mapping should produce a
    # node whose name is the property_name (e.g. 'Interpretation').
    from modules.s3dgraphy.sync.pyarchinit_pg_importer import (
        _load_mapping,
    )
    mapping = _load_mapping("pyarchinit_us_mapping")
    prop_names_expected = {
        spec["property_name"]
        for spec in mapping["column_mappings"].values()
        if spec.get("node_type") == "PropertyNode"
    }
    found_prop_names = {
        getattr(n, "name", None)
        for n in graph.nodes
        if type(n).__name__ == "PropertyNode"
    }
    assert prop_names_expected.issubset(found_prop_names), (
        f"missing PropertyNodes: expected ⊇ {prop_names_expected}, "
        f"got {found_prop_names}"
    )


# ---------------------------------------------------------------------
# L2 PG — skip when psycopg2 missing or PG offline
# ---------------------------------------------------------------------

def test_pg_export_graphml_end_to_end(pg_with_volterra, tmp_path):
    """End-to-end: populate_graph on PG produces a non-empty Graph,
    then graphml_writer.export_graphml writes a real file with the
    expected stratigraphic node markup."""
    pytest.importorskip("psycopg2")
    from modules.s3dgraphy.sync.graph_projector import GraphProjector
    from modules.s3dgraphy.sync.graphml_writer import export_graphml
    from modules.s3dgraphy.sync._db_handle import DbHandle

    # pg_with_volterra yields a SQLAlchemy Engine — wrap in DbHandle.
    handle = DbHandle.from_engine(pg_with_volterra,
                                  str(pg_with_volterra.url))
    projector = GraphProjector()
    graph = projector.populate_graph(
        handle,
        sito="Volterra",
        include_paradata=False,
        strict_schema=False,
    )
    assert len(graph.nodes) > 0, "empty graph on PG (PG-Bv2 regression)"

    out_file = tmp_path / "pg_bv2_end_to_end.graphml"
    result = export_graphml(
        db_path=handle,
        mapping="pyarchinit_us_mapping",
        output_path=str(out_file),
        site_filter="Volterra",
        persist_auxiliary=False,
        language="it",
    )
    assert out_file.exists()
    content = out_file.read_text(encoding="utf-8")
    assert "<graphml" in content
    assert "<node" in content
    # Stratigraphic nodes get id attribute, format depends on writer.
    assert content.count("<node") > 1, (
        f"expected >1 nodes in graphml, got: {content.count('<node')}"
    )


def test_pg_export_graphml_structural_match_sqlite(
    pg_with_volterra, tmp_path,
):
    """SQLite vs PG output structural equivalence: load same Volterra
    fixture into both backends, export both as graphml, assert
    node count + edge type distribution match. Not byte-identical
    (IDs may differ); structural."""
    pytest.importorskip("psycopg2")
    from modules.s3dgraphy.sync.graphml_writer import export_graphml
    from modules.s3dgraphy.sync._db_handle import DbHandle
    import re

    # PG side — use the pg_with_volterra fixture.
    handle = DbHandle.from_engine(pg_with_volterra,
                                  str(pg_with_volterra.url))
    pg_out = tmp_path / "volterra_pg.graphml"
    export_graphml(
        db_path=handle,
        mapping="pyarchinit_us_mapping",
        output_path=str(pg_out),
        site_filter="Volterra",
        persist_auxiliary=False,
        language="it",
    )
    pg_content = pg_out.read_text(encoding="utf-8")

    # SQLite side — use the same source-of-truth mini_volterra fixture.
    sqlite_fixture = (
        Path(__file__).resolve().parent
        / "fixtures"
        / "mini_volterra.sqlite"
    )
    if not sqlite_fixture.exists():
        pytest.skip(f"Volterra fixture missing: {sqlite_fixture}")
    sqlite_out = tmp_path / "volterra_sqlite.graphml"
    export_graphml(
        db_path=sqlite_fixture,
        mapping="pyarchinit_us_mapping",
        output_path=str(sqlite_out),
        site_filter="Volterra",
        persist_auxiliary=False,
        language="it",
    )
    sqlite_content = sqlite_out.read_text(encoding="utf-8")

    # Structural equivalence: same node count, same edge source set.
    pg_node_count = pg_content.count("<node ")
    sqlite_node_count = sqlite_content.count("<node ")
    assert pg_node_count == sqlite_node_count, (
        f"node count mismatch: PG={pg_node_count}, "
        f"SQLite={sqlite_node_count}"
    )
    pg_edges = set(re.findall(r'<edge[^>]+source="([^"]+)"', pg_content))
    sqlite_edges = set(re.findall(
        r'<edge[^>]+source="([^"]+)"', sqlite_content,
    ))
    assert pg_edges == sqlite_edges, (
        f"edge source set differs: PG-only={pg_edges - sqlite_edges}, "
        f"SQLite-only={sqlite_edges - pg_edges}"
    )
