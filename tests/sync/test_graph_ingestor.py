"""Exception-hierarchy tests for graph_ingestor module.

Group C onwards adds tests for the GraphIngestor class itself.
"""
import pytest


def test_graph_sync_error_is_base_class():
    from modules.s3dgraphy.sync.graph_ingestor import (
        GraphSyncError, GraphIngestError)
    assert issubclass(GraphIngestError, GraphSyncError)


def test_specific_errors_inherit_graph_ingest_error():
    from modules.s3dgraphy.sync.graph_ingestor import (
        GraphIngestError,
        SchemaMismatchError,
        UnknownUnitaTipoError,
        SiteMismatchError,
        MissingEpochError,
    )
    for cls in (SchemaMismatchError, UnknownUnitaTipoError,
                SiteMismatchError, MissingEpochError):
        assert issubclass(cls, GraphIngestError), (
            f"{cls.__name__} must inherit GraphIngestError")


def test_mapped_columns_constant_present():
    from modules.s3dgraphy.sync.graph_ingestor import MAPPED_COLUMNS
    # The 12 columns spec §3.2 + risk row 5 enumerate.
    expected = {
        "us", "d_stratigrafica", "d_interpretativa", "attivita",
        "struttura", "sito", "area", "unita_tipo",
        "periodo_iniziale", "fase_iniziale", "rapporti", "node_uuid",
    }
    assert set(MAPPED_COLUMNS) == expected
    assert isinstance(MAPPED_COLUMNS, tuple)  # immutable


def test_missing_epoch_error_carries_epoch_list():
    from modules.s3dgraphy.sync.graph_ingestor import MissingEpochError
    err = MissingEpochError(missing=[(2, "3.1"), (3, "1")])
    assert err.missing == [(2, "3.1"), (3, "1")]
    assert "(2, '3.1')" in str(err) or "[(2," in str(err)


# ---------------------------------------------------------------------------
# Group C tests — GraphIngestor class
# ---------------------------------------------------------------------------
import sys
from pathlib import Path
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
    # Apply Phase 1 node_uuid migration (idempotent).
    from scripts.migrations._2026_05_node_uuid_backfill_lib import (
        add_columns, backfill_uuids)
    add_columns(dst)
    backfill_uuids(dst)
    return dst


def _read_sito(db_path):
    import sqlite3
    conn = sqlite3.connect(db_path)
    sito = conn.execute(
        "SELECT DISTINCT sito FROM us_table LIMIT 1").fetchone()[0]
    conn.close()
    return sito


def test_ingestor_construction():
    """Ingestor accepts an optional ConflictResolver."""
    from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor
    from modules.s3dgraphy.sync.conflict_resolver import ConflictResolver
    g = GraphIngestor()
    assert g._resolver is not None
    g2 = GraphIngestor(conflict_resolver=ConflictResolver())
    assert g2._resolver is not None


def test_populate_list_requires_sito_match(mini_volterra):
    """D6 — graph nodes whose sito differs from the parameter raise."""
    from modules.s3dgraphy.sync.graph_projector import GraphProjector
    from modules.s3dgraphy.sync.graph_ingestor import (
        GraphIngestor, SiteMismatchError)
    sito = _read_sito(mini_volterra)
    graph = GraphProjector().populate_graph(mini_volterra, sito=sito)
    g = GraphIngestor()
    with pytest.raises(SiteMismatchError):
        g.populate_list(graph, mini_volterra, sito="WRONG_SITE")


def test_populate_list_schema_check_raises(tmp_path):
    """node_uuid column missing → SchemaMismatchError."""
    import sqlite3
    from modules.s3dgraphy.sync.graph_ingestor import (
        GraphIngestor, SchemaMismatchError)
    from s3dgraphy import Graph
    db = tmp_path / "x.sqlite"
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE us_table (id_us INTEGER, sito TEXT, us TEXT)")
    conn.commit()
    conn.close()
    g = GraphIngestor()
    with pytest.raises(SchemaMismatchError):
        g.populate_list(Graph(graph_id="X"), db, sito="X")
