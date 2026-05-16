"""Tests for GraphProjector. Pins:
- D2 — wrap pattern (calls _enrich_pyarchinit_graph)
- D6 — sito parameter mandatory
- AC-1 — non-empty graph, filtered by sito
"""
from __future__ import annotations
import sys
from pathlib import Path

import pytest
import pandas  # noqa: F401
from lxml import etree as _etree  # noqa: F401
PLUGIN_ROOT = Path(__file__).resolve().parents[2]
_EXT_LIBS = str(PLUGIN_ROOT / "ext_libs")
if _EXT_LIBS in sys.path:
    sys.path.remove(_EXT_LIBS)
sys.path.insert(0, _EXT_LIBS)
for _mod in [m for m in list(sys.modules)
             if m == "s3dgraphy" or m.startswith("s3dgraphy.")]:
    del sys.modules[_mod]

FIXTURE_DB = (PLUGIN_ROOT / "tests" / "sync" / "fixtures"
              / "mini_volterra.sqlite")


@pytest.fixture
def mini_volterra(tmp_path):
    import shutil
    dst = tmp_path / "mini_volterra.sqlite"
    shutil.copy2(FIXTURE_DB, dst)
    # Apply Phase 1 node_uuid migration (idempotent) — required by
    # GraphProjector.populate_graph().
    from scripts.migrations._2026_05_node_uuid_backfill_lib import (
        add_columns, backfill_uuids)
    add_columns(dst)
    backfill_uuids(dst)
    return dst


def test_populate_graph_requires_sito(mini_volterra):
    """D6 — empty sito is rejected."""
    from modules.s3dgraphy.sync.graph_projector import (
        GraphProjector, ProjectionError)
    p = GraphProjector()
    with pytest.raises(ProjectionError, match="sito"):
        p.populate_graph(mini_volterra, sito="")


def test_populate_graph_missing_db_raises(tmp_path):
    from modules.s3dgraphy.sync.graph_projector import (
        GraphProjector, ProjectionError)
    p = GraphProjector()
    with pytest.raises(ProjectionError, match="not found"):
        p.populate_graph(tmp_path / "nope.sqlite", sito="X")


def test_populate_graph_missing_node_uuid_column_raises(tmp_path):
    """SchemaMismatchError-equivalent: node_uuid column required."""
    import sqlite3
    from modules.s3dgraphy.sync.graph_projector import (
        GraphProjector, ProjectionError)
    db = tmp_path / "x.sqlite"
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE us_table (id_us INTEGER PRIMARY KEY, "
                 "sito TEXT, us TEXT)")  # no node_uuid
    conn.commit()
    conn.close()
    p = GraphProjector()
    with pytest.raises(ProjectionError, match="node_uuid"):
        p.populate_graph(db, sito="X")


def test_projector_returns_filtered_graph(mini_volterra):
    """AC-1 — non-empty graph, every strat node matches sito."""
    from modules.s3dgraphy.sync.graph_projector import GraphProjector
    p = GraphProjector()
    # Find the sito present in the fixture
    import sqlite3
    conn = sqlite3.connect(mini_volterra)
    sito = conn.execute(
        "SELECT DISTINCT sito FROM us_table LIMIT 1").fetchone()[0]
    conn.close()
    graph = p.populate_graph(mini_volterra, sito=sito)
    assert len(graph.nodes) > 0
    # Every node with sito attribute must match — EpochNodes have no sito.
    for n in graph.nodes:
        attrs = getattr(n, "attributes", None) or {}
        if "sito" in attrs:
            assert attrs["sito"] == sito


def test_projector_delegates_to_enrich_method(mini_volterra, monkeypatch):
    """D2 — verify GraphProjector.populate_graph calls the private
    ``_enrich_into`` method.

    AI04 originally wrapped a standalone ``_enrich_pyarchinit_graph``
    function in ``graphml_writer`` (Strategy D). AI05 Group C promotes
    the projector to a proper class (Strategy A): the body now lives
    on ``GraphProjector._enrich_into`` and the standalone function is
    deleted. This test pins the new delegation contract.
    """
    from modules.s3dgraphy.sync import graph_projector as gp_mod
    calls = []
    original = gp_mod.GraphProjector._enrich_into

    def spy(self, graph, db_path, sito_filter=None):
        calls.append((db_path, sito_filter))
        return original(self, graph, db_path, sito_filter=sito_filter)
    monkeypatch.setattr(
        gp_mod.GraphProjector, "_enrich_into", spy, raising=True)

    import sqlite3
    conn = sqlite3.connect(mini_volterra)
    sito = conn.execute(
        "SELECT DISTINCT sito FROM us_table LIMIT 1").fetchone()[0]
    conn.close()

    p = gp_mod.GraphProjector()
    p.populate_graph(mini_volterra, sito=sito)
    assert len(calls) == 1, (
        "GraphProjector must call its own _enrich_into method")
    assert calls[0][1] == sito, "sito_filter must be propagated"


def test_populate_graph_accepts_db_manager_on_sqlite(mini_volterra):
    """Regression 2026-05-13 (post PG-Bv2): when the bridge passes a
    Pyarchinit_db_management instance instead of a Path, the SQLite
    branch of populate_graph used to do ``Path(db_path)`` and
    ``str(db_path)`` directly on the object, raising
    ``TypeError: expected str, bytes or os.PathLike object,
    not Pyarchinit_db_management``. The fix derives the filesystem path
    from ``handle.sqlite_path`` (set by DbHandle.from_engine). This
    test pins the contract: a fake DbManager whose .conn_str points to
    a real SQLite file must work end-to-end.
    """
    from sqlalchemy import create_engine
    from modules.s3dgraphy.sync.graph_projector import GraphProjector

    class FakeDbManager:
        def __init__(self, db_path):
            self.conn_str = f"sqlite:///{db_path}"
            self.engine = create_engine(self.conn_str)

    import sqlite3
    conn = sqlite3.connect(mini_volterra)
    sito = conn.execute(
        "SELECT DISTINCT sito FROM us_table LIMIT 1").fetchone()[0]
    conn.close()

    mgr = FakeDbManager(mini_volterra)
    graph = GraphProjector().populate_graph(mgr, sito=sito)
    assert len(graph.nodes) > 0, (
        "DbManager input must work the same as a Path input")


def test_projector_handles_paradata_name_collisions(tmp_path):
    """Bug K (2026-05-15 user feedback): the s3dgraphy bridge's
    ``_find_node_by_name`` collapses us_table rows that share the
    same ``us`` value across different ``unita_tipo``. Before this
    fix the projector indexed nodes by name alone — paradata rows
    (DOC / Combinar / Extractor / property) at the same name as a
    stratigraphic row got silently dropped on re-export.

    This test builds a minimal DB with 3 rows all named '01'
    (US / DOC / Combinar) plus 1 each at '02' (Extractor + property)
    and asserts the projected graph contains EXACTLY one node per
    (us, unita_tipo) tuple, of the right s3dgraphy class.
    """
    from collections import Counter
    from sqlalchemy import text
    from modules.s3dgraphy.sync._db_handle import DbHandle
    from modules.s3dgraphy.sync.graph_projector import GraphProjector

    db = tmp_path / "paradata_collisions.sqlite"
    handle = DbHandle.from_path(db)
    with handle.engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE us_table (
                id_us INTEGER PRIMARY KEY AUTOINCREMENT,
                sito TEXT, area TEXT DEFAULT '1', us TEXT,
                unita_tipo TEXT, node_uuid TEXT,
                rapporti TEXT, periodo_iniziale TEXT, fase_iniziale TEXT,
                periodo_finale TEXT, fase_finale TEXT,
                d_stratigrafica TEXT, d_interpretativa TEXT,
                attivita TEXT, struttura TEXT, settore TEXT,
                ambient TEXT, saggio TEXT, quad_par TEXT,
                documentazione TEXT,
                UNIQUE(sito, area, us, unita_tipo)
            )
        """))
        conn.execute(text("""
            CREATE TABLE periodizzazione_table (
                id_perfas INTEGER PRIMARY KEY AUTOINCREMENT,
                sito TEXT, periodo INTEGER, fase TEXT,
                cron_iniziale INTEGER, cron_finale INTEGER,
                descrizione TEXT, datazione_estesa TEXT, cont_per INTEGER
            )
        """))
        # 3 rows at '01' (paradata BEFORE stratigraphic in rowid order —
        # this reproduces yEd document order interleaving that caused the
        # original bug).
        rows = [
            ("01", "DOC",       "uuid-01-doc"),
            ("01", "Combinar",  "uuid-01-cmb"),
            ("01", "US",        "uuid-01-us"),
            ("02", "Extractor", "uuid-02-ext"),
            ("02", "property",  "uuid-02-prop"),
        ]
        for us, ut, uu in rows:
            conn.execute(
                text("INSERT INTO us_table (sito, area, us, unita_tipo, "
                     "node_uuid) VALUES (:s, '1', :u, :t, :n)"),
                {"s": "S", "u": us, "t": ut, "n": uu},
            )

    proj = GraphProjector()
    graph = proj.populate_graph(db, sito="S")

    by_class_and_ut = Counter()
    for n in graph.nodes:
        cls = type(n).__name__
        ut = (getattr(n, "attributes", None) or {}).get("unita_tipo", "")
        by_class_and_ut[(cls, ut)] += 1

    # Bug P (2026-05-15 v2): row-paradata are StratigraphicNode-class
    # instances (StratigraphicUnit) with ``attributes['unita_tipo']``
    # carrying the EM semantic identity. The writer dispatches BPMN
    # shape / colour by unita_tipo, not by Python class.
    assert by_class_and_ut[("StratigraphicUnit", "DOC")] == 1
    assert by_class_and_ut[("StratigraphicUnit", "Combinar")] == 1
    assert by_class_and_ut[("StratigraphicUnit", "Extractor")] == 1
    assert by_class_and_ut[("StratigraphicUnit", "property")] == 1
    assert by_class_and_ut[("StratigraphicUnit", "US")] == 1
    # No duplicates: total row-derived StratigraphicUnit nodes = 5.
    row_derived = sum(
        v for (cls, ut), v in by_class_and_ut.items()
        if cls == "StratigraphicUnit" and ut
    )
    assert row_derived == 5
