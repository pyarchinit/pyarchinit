# tests/sync/test_ingest_pg.py
"""PG-C: L2 PostgreSQL tests for the ingest pipeline.

Verifies that GraphIngestor.populate_list works on PG when seeded
via the pg_with_volterra fixture (from PG-B's conftest_pg.py).

Skipped cleanly when PG is unreachable at localhost:5433 or when
psycopg2 is not installed.
"""
from __future__ import annotations

import pytest

# Import fixtures explicitly - conftest_pg.py is not auto-discovered
from tests.sync.conftest_pg import pg_engine, pg_with_volterra  # noqa: F401


def _make_test_graph_with_us(sito="Volterra", us_count=3):
    """Build a minimal s3dgraphy Graph with us_count StratigraphicNodes.

    Each node has a fresh node_uuid, the requested sito, and a numeric
    'us' value (1, 2, 3, ...). Used as input for populate_list tests
    that don't need to round-trip a real GraphML file.
    """
    import uuid
    from s3dgraphy import Graph
    from s3dgraphy.nodes.stratigraphic_node import StratigraphicNode

    graph = Graph(graph_id="test_graph")
    for i in range(1, us_count + 1):
        node_uuid = str(uuid.uuid4())
        node = StratigraphicNode(
            node_id=node_uuid,
            name=str(i),
            description="",
            data={},
        )
        if not hasattr(node, "attributes") or node.attributes is None:
            node.attributes = {}
        node.attributes["node_uuid"] = node_uuid
        node.attributes["us"] = str(i)
        node.attributes["sito"] = sito
        node.attributes["area"] = "1"
        node.attributes["unita_tipo"] = "US"
        graph.add_node(node)
    return graph


def test_populate_list_accepts_dbhandle_on_pg(pg_engine):
    """populate_list(graph, handle, sito) works on PG and inserts US rows.

    Uses a fresh PG (DDL-only, no data) so insertions are unambiguous.
    """
    from modules.s3dgraphy.sync._db_handle import DbHandle
    from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor
    from sqlalchemy import text

    # Truncate to start clean
    with pg_engine.begin() as conn:
        conn.execute(text(
            "TRUNCATE us_table, site_table, periodizzazione_table "
            "RESTART IDENTITY CASCADE"
        ))

    handle = DbHandle.from_engine(pg_engine, str(pg_engine.url))
    graph = _make_test_graph_with_us(sito="TestSite", us_count=3)

    result = GraphIngestor().populate_list(
        graph=graph, db_path=handle, sito="TestSite", dry_run=False,
    )
    # Newly inserted rows: 3
    assert result.inserted == 3, f"expected 3 inserted, got {result.inserted!r}"
    # Verify rows are actually present on PG
    with pg_engine.connect() as conn:
        count = conn.execute(
            text("SELECT COUNT(*) FROM us_table WHERE sito=:s"),
            {"s": "TestSite"},
        ).scalar()
    assert count == 3, f"expected 3 us_table rows, got {count}"


def test_populate_list_dry_run_no_changes_on_pg(pg_engine):
    """dry_run=True returns IngestResult but commits NO changes.

    THE critical test for _DryRunRollback pattern."""
    from modules.s3dgraphy.sync._db_handle import DbHandle
    from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor
    from sqlalchemy import text

    with pg_engine.begin() as conn:
        conn.execute(text(
            "TRUNCATE us_table, site_table, periodizzazione_table "
            "RESTART IDENTITY CASCADE"
        ))

    handle = DbHandle.from_engine(pg_engine, str(pg_engine.url))
    graph = _make_test_graph_with_us(sito="TestSite", us_count=3)

    result = GraphIngestor().populate_list(
        graph=graph, db_path=handle, sito="TestSite", dry_run=True,
    )
    # IngestResult still reports the would-be inserts (3) in detection
    assert result.inserted == 3, (
        f"dry_run should still detect 3 inserts, got {result.inserted!r}"
    )
    # But the DB has NO new rows because _DryRunRollback fired
    with pg_engine.connect() as conn:
        count = conn.execute(
            text("SELECT COUNT(*) FROM us_table WHERE sito=:s"),
            {"s": "TestSite"},
        ).scalar()
    assert count == 0, (
        f"dry_run should have 0 us_table rows after rollback, got {count}"
    )


def test_populate_list_conflict_resolution_graph_wins_on_pg(pg_engine):
    """When DB has a US row and graph has the same US with different
    column values, populate_list updates the row (GRAPH_WINS policy)
    and IngestResult.conflicts captures the diff."""
    import uuid as _uuid
    from modules.s3dgraphy.sync._db_handle import DbHandle
    from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor
    from s3dgraphy import Graph
    from s3dgraphy.nodes.stratigraphic_node import StratigraphicNode
    from sqlalchemy import text

    with pg_engine.begin() as conn:
        conn.execute(text(
            "TRUNCATE us_table, site_table, periodizzazione_table "
            "RESTART IDENTITY CASCADE"
        ))
        # Seed: one US row with node_uuid X and d_stratigrafica="OLD"
        my_uuid = str(_uuid.uuid4())
        conn.execute(text(
            "INSERT INTO us_table (sito, area, us, unita_tipo, "
            "d_stratigrafica, node_uuid) "
            "VALUES ('TestSite', '1', '1', 'US', 'OLD', :uuid)"
        ), {"uuid": my_uuid})

    handle = DbHandle.from_engine(pg_engine, str(pg_engine.url))
    graph = Graph(graph_id="g")
    node = StratigraphicNode(
        node_id=my_uuid, name="1", description="", data={}
    )
    node.attributes = {
        "node_uuid": my_uuid, "us": "1", "sito": "TestSite",
        "area": "1", "unita_tipo": "US",
        "d_stratigrafica": "NEW",  # the diff
    }
    graph.add_node(node)

    result = GraphIngestor().populate_list(
        graph=graph, db_path=handle, sito="TestSite", dry_run=False,
    )
    assert result.updated == 1, (
        f"expected 1 update, got {result.updated!r}"
    )
    assert any(c.field == "d_stratigrafica" for c in result.conflicts), (
        f"conflicts should contain d_stratigrafica diff, got "
        f"{result.conflicts!r}"
    )
    # Verify the actual DB value is "NEW"
    with pg_engine.connect() as conn:
        val = conn.execute(
            text("SELECT d_stratigrafica FROM us_table WHERE node_uuid=:u"),
            {"u": my_uuid},
        ).scalar()
    assert val == "NEW", f"expected d_stratigrafica='NEW', got {val!r}"


def test_populate_list_missing_epoch_error_on_pg(pg_engine):
    """MissingEpochError raised + transaction rolled back when graph
    has EpochNode whose (periodo, fase) is not in periodizzazione_table
    and create_missing_epochs=False."""
    from modules.s3dgraphy.sync._db_handle import DbHandle
    from modules.s3dgraphy.sync.graph_ingestor import (
        GraphIngestor, MissingEpochError,
    )
    from s3dgraphy import Graph
    from s3dgraphy.nodes.epoch_node import EpochNode
    from sqlalchemy import text

    with pg_engine.begin() as conn:
        conn.execute(text(
            "TRUNCATE us_table, site_table, periodizzazione_table "
            "RESTART IDENTITY CASCADE"
        ))

    handle = DbHandle.from_engine(pg_engine, str(pg_engine.url))
    graph = Graph(graph_id="g")
    epoch = EpochNode(
        node_id="epoch_99_x",
        name="Period 99 Phase x",
        start_time=0.0, end_time=0.0,
    )
    if not hasattr(epoch, "attributes") or epoch.attributes is None:
        epoch.attributes = {}
    epoch.attributes["periodo"] = "99"
    epoch.attributes["fase"] = "x"
    graph.add_node(epoch)

    with pytest.raises(MissingEpochError):
        GraphIngestor().populate_list(
            graph=graph, db_path=handle, sito="TestSite",
            dry_run=False, create_missing_epochs=False,
        )

    # Atomic rollback: site_table should NOT have been written either
    with pg_engine.connect() as conn:
        count = conn.execute(text(
            "SELECT COUNT(*) FROM site_table WHERE sito=:s"
        ), {"s": "TestSite"}).scalar()
    assert count == 0, (
        f"site_table should be empty (rolled back), got {count}"
    )


def test_populate_list_creates_missing_epochs_on_pg(pg_engine):
    """create_missing_epochs=True inserts the new epoch + returns
    IngestResult.epochs_created=1."""
    from modules.s3dgraphy.sync._db_handle import DbHandle
    from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor
    from s3dgraphy import Graph
    from s3dgraphy.nodes.epoch_node import EpochNode
    from sqlalchemy import text

    with pg_engine.begin() as conn:
        conn.execute(text(
            "TRUNCATE us_table, site_table, periodizzazione_table "
            "RESTART IDENTITY CASCADE"
        ))

    handle = DbHandle.from_engine(pg_engine, str(pg_engine.url))
    graph = Graph(graph_id="g")
    epoch = EpochNode(
        node_id="epoch_99_x",
        name="Period 99 Phase x",
        start_time=1500.0, end_time=1600.0,
    )
    epoch.attributes = {"periodo": "99", "fase": "x"}
    graph.add_node(epoch)

    result = GraphIngestor().populate_list(
        graph=graph, db_path=handle, sito="TestSite",
        dry_run=False, create_missing_epochs=True,
    )
    assert result.epochs_created == 1, (
        f"expected 1 epoch created, got {result.epochs_created!r}"
    )
    # Verify the row is in periodizzazione_table
    with pg_engine.connect() as conn:
        row = conn.execute(text(
            "SELECT periodo, fase FROM periodizzazione_table WHERE sito=:s"
        ), {"s": "TestSite"}).fetchone()
    assert row is not None
    assert str(row[0]) == "99"
    assert str(row[1]) == "x"


def test_populate_list_atomic_rollback_on_pg(pg_engine, monkeypatch):
    """Mock text() to raise RuntimeError mid-transaction. Verify that
    engine.begin() rolls back: no partial writes survive."""
    from modules.s3dgraphy.sync._db_handle import DbHandle
    from modules.s3dgraphy.sync import graph_ingestor as gi_mod
    from sqlalchemy import text

    with pg_engine.begin() as conn:
        conn.execute(text(
            "TRUNCATE us_table, site_table, periodizzazione_table "
            "RESTART IDENTITY CASCADE"
        ))

    handle = DbHandle.from_engine(pg_engine, str(pg_engine.url))
    graph = _make_test_graph_with_us(sito="TestSite", us_count=3)

    # Patch text() inside graph_ingestor to raise on the INSERT INTO
    # us_table statement (after site_table INSERT, so we know SOMETHING
    # was attempted and the rollback has to clean it up).
    original_text = gi_mod.text
    call_count = {"n": 0}

    def fake_text(stmt):
        call_count["n"] += 1
        if "INSERT INTO us_table" in stmt:
            raise RuntimeError("simulated mid-transaction failure")
        return original_text(stmt)

    monkeypatch.setattr(gi_mod, "text", fake_text)

    with pytest.raises(Exception):
        from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor
        GraphIngestor().populate_list(
            graph=graph, db_path=handle, sito="TestSite", dry_run=False,
        )

    # site_table INSERT must have been rolled back too
    with pg_engine.connect() as conn:
        count = conn.execute(text(
            "SELECT COUNT(*) FROM site_table WHERE sito=:s"
        ), {"s": "TestSite"}).scalar()
    assert count == 0, (
        f"site_table.sito='TestSite' should be 0 after rollback, got {count}"
    )
