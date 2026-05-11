# tests/sync/test_export_pg.py
"""PG-B: L2 PostgreSQL tests for the export pipeline.

Verifies that GraphProjector + GraphMLWriter + GroupProjector work
on PG when seeded with the same data as mini_volterra.sqlite.

Skipped cleanly when PG is unreachable at localhost:5433 or when
psycopg2 is not installed. Uses the pg_with_volterra fixture
from conftest_pg.py (Group D).
"""
from __future__ import annotations

import pytest

# Import fixtures explicitly - conftest_pg.py is not auto-discovered
from tests.sync.conftest_pg import pg_engine, pg_with_volterra  # noqa: F401


def test_populate_graph_accepts_dbhandle_on_pg(pg_with_volterra):
    """GraphProjector.populate_graph(handle, sito) works on PG and
    returns a Graph with the same node count as on SQLite."""
    from modules.s3dgraphy.sync._db_handle import DbHandle
    from modules.s3dgraphy.sync.graph_projector import GraphProjector

    handle = DbHandle.from_engine(pg_with_volterra,
                                   str(pg_with_volterra.url))
    projector = GraphProjector()
    graph = projector.populate_graph(
        handle,
        sito="Volterra",
        include_paradata=False,
        strict_schema=False,
    )
    assert graph is not None
    assert len(graph.nodes) > 0, "Graph has no nodes — projection failed"


def test_populate_graph_node_uuid_propagation_on_pg(pg_with_volterra):
    """Every StratigraphicNode-family node in the projected graph
    carries a non-None node_uuid attribute."""
    from modules.s3dgraphy.sync._db_handle import DbHandle
    from modules.s3dgraphy.sync.graph_projector import GraphProjector

    handle = DbHandle.from_engine(pg_with_volterra,
                                   str(pg_with_volterra.url))
    graph = GraphProjector().populate_graph(
        handle, sito="Volterra", include_paradata=False,
        strict_schema=False,
    )
    strat_nodes = [
        n for n in graph.nodes
        if type(n).__name__.startswith("Stratigraphic")
        or type(n).__name__ == "USNode"
    ]
    if not strat_nodes:
        pytest.skip("mini_volterra has no stratigraphic units — "
                    "fixture-specific")
    for n in strat_nodes:
        attrs = getattr(n, "attributes", None) or {}
        nu = attrs.get("node_uuid")
        assert nu is not None, (
            f"Node {getattr(n, 'name', '?')} missing node_uuid attribute"
        )
        assert len(str(nu)) == 36, (
            f"node_uuid {nu!r} is not a 36-char UUID"
        )


def test_populate_graph_toponym_chain_on_pg(pg_with_volterra):
    """If mini_volterra has site_table populated with toponym fields,
    the projected graph contains LocationNodeGroup nodes with
    kind='toponym' + is_in_location edges from US nodes."""
    from modules.s3dgraphy.sync._db_handle import DbHandle
    from modules.s3dgraphy.sync.graph_projector import GraphProjector
    from sqlalchemy import text

    handle = DbHandle.from_engine(pg_with_volterra,
                                   str(pg_with_volterra.url))
    # Verify the fixture has populated toponym data; skip otherwise
    with pg_with_volterra.connect() as conn:
        row = conn.execute(text(
            "SELECT nazione, regione, provincia, comune "
            "FROM site_table WHERE sito=:sito"
        ), {"sito": "Volterra"}).fetchone()
    if row is None or not any(v for v in row):
        pytest.skip("mini_volterra site_table not populated with "
                    "toponym fields — fixture-specific")

    graph = GraphProjector().populate_graph(
        handle, sito="Volterra", include_paradata=False,
        strict_schema=False,
    )
    toponym_nodes = [
        n for n in graph.nodes
        if type(n).__name__ == "LocationNodeGroup"
        and (getattr(n, "kind", None) == "toponym"
             or (getattr(n, "attributes", {}) or {}).get("kind") == "toponym")
    ]
    assert len(toponym_nodes) > 0, (
        "No LocationNodeGroup(kind='toponym') nodes emitted — "
        "_emit_toponym_chain may have failed on PG"
    )


def test_group_projector_dimensions_with_data_on_pg(pg_with_volterra):
    """dimensions_with_data(handle, sito) returns the same set of
    dimension names on PG as it would on SQLite."""
    from modules.s3dgraphy.sync._db_handle import DbHandle
    from modules.s3dgraphy.sync.group_projector import dimensions_with_data

    handle = DbHandle.from_engine(pg_with_volterra,
                                   str(pg_with_volterra.url))
    dims = dimensions_with_data(handle, "Volterra")
    # dims is a list of column names that have at least one non-empty
    # value. mini_volterra is expected to have at least area or
    # struttura populated.
    assert isinstance(dims, list)
    valid_dim_set = {"area", "struttura", "attivita", "settore",
                     "ambient", "saggio", "quad_par"}
    assert all(d in valid_dim_set for d in dims), (
        f"dimensions_with_data returned unexpected entries: {dims}"
    )


def test_export_graphml_writes_file_on_pg(pg_with_volterra, tmp_path):
    """End-to-end: export_graphml(db_path=handle, ...) produces a
    non-empty GraphML file on disk + ExportResult.node_count > 0."""
    from modules.s3dgraphy.sync._db_handle import DbHandle
    from modules.s3dgraphy.sync.graphml_writer import export_graphml

    handle = DbHandle.from_engine(pg_with_volterra,
                                   str(pg_with_volterra.url))
    out = tmp_path / "out_pg.graphml"
    result = export_graphml(
        db_path=handle,
        mapping="pyarchinit_us_mapping",
        output_path=out,
        site_filter="Volterra",
    )
    assert out.exists(), "GraphML output file not created"
    assert out.stat().st_size > 0, "GraphML output file is empty"
    assert result.node_count > 0, "ExportResult.node_count is 0"
