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


def test_populate_list_overrides_sito_to_target(mini_volterra):
    """AI04.1 (formerly D6 strict): the sito parameter is now
    AUTHORITATIVE — graph nodes' sito attribute is overridden to the
    parameter value. This supports the "import this graph into a NEW
    sito" workflow that emerged from the H.4 manual smoke gate."""
    from modules.s3dgraphy.sync.graph_projector import GraphProjector
    from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor
    sito = _read_sito(mini_volterra)
    graph = GraphProjector().populate_graph(mini_volterra, sito=sito)
    # Importing into a different sito must NOT raise — instead the
    # ingestor rewrites sito on every node to the target value.
    # create_missing_epochs=True so the new-sito periodizzazione gets
    # auto-populated (otherwise MissingEpochError raises since the
    # new sito has no period rows yet).
    result = GraphIngestor().populate_list(
        graph, mini_volterra, sito="DIFFERENT_TARGET",
        dry_run=True, create_missing_epochs=True)
    # Dry-run still does the detection; non-zero counters mean the
    # nodes were processed (not skipped by a SiteMismatchError raise).
    assert result.inserted + result.updated + result.skipped > 0


def test_populate_list_empty_sito_still_raises():
    """Empty sito parameter is always invalid."""
    from s3dgraphy import Graph
    from modules.s3dgraphy.sync.graph_ingestor import (
        GraphIngestor, SiteMismatchError)
    g = GraphIngestor()
    with pytest.raises(SiteMismatchError):
        g.populate_list(Graph(graph_id="X"), "/nope.sqlite", sito="")


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


def test_populate_list_dry_run_no_writes(mini_volterra):
    """D3 — dry_run=True must not change the DB (sha256 invariant)."""
    import hashlib
    from modules.s3dgraphy.sync.graph_projector import GraphProjector
    from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor
    sito = _read_sito(mini_volterra)
    graph = GraphProjector().populate_graph(mini_volterra, sito=sito)
    sha_before = hashlib.sha256(mini_volterra.read_bytes()).hexdigest()
    g = GraphIngestor()
    result = g.populate_list(graph, mini_volterra, sito=sito, dry_run=True)
    sha_after = hashlib.sha256(mini_volterra.read_bytes()).hexdigest()
    assert sha_before == sha_after, "dry_run modified the DB"
    assert result.dry_run is True
    assert result.applied == 0


def test_populate_list_dry_run_counts_skipped_when_unchanged(mini_volterra):
    """Round-trip the projector → ingestor: every node should be
    'skipped' (no diff vs the source)."""
    from modules.s3dgraphy.sync.graph_projector import GraphProjector
    from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor
    sito = _read_sito(mini_volterra)
    graph = GraphProjector().populate_graph(mini_volterra, sito=sito)
    result = GraphIngestor().populate_list(
        graph, mini_volterra, sito=sito, dry_run=True)
    # Every projected node is already in DB, no value differences →
    # all skipped.
    n_strat = sum(1 for n in graph.nodes
                  if (getattr(n, "attributes", None) or {}).get("us") is not None)
    assert result.skipped == n_strat
    assert result.inserted == 0
    assert result.updated == 0
    assert len(result.conflicts) == 0


def _make_graph_with_extra_epoch(mini_volterra, periodo, fase):
    """Project mini_volterra and inject an extra EpochNode."""
    from modules.s3dgraphy.sync.graph_projector import GraphProjector
    from s3dgraphy.nodes.epoch_node import EpochNode
    sito = _read_sito(mini_volterra)
    graph = GraphProjector().populate_graph(mini_volterra, sito=sito)
    # Add a synthetic epoch missing from periodizzazione_table
    epoch = EpochNode(
        node_id=f"epoch_{periodo}_{fase}_synthetic",
        name=f"Synthetic Period {periodo} Phase {fase}",
        start_time=0.0, end_time=0.0)
    epoch.attributes = {"periodo": periodo, "fase": fase}
    graph.add_node(epoch)
    return graph, sito


def test_missing_epoch_strict_raises(mini_volterra):
    """D5-A — strict (default) raises MissingEpochError."""
    from modules.s3dgraphy.sync.graph_ingestor import (
        GraphIngestor, MissingEpochError)
    graph, sito = _make_graph_with_extra_epoch(
        mini_volterra, periodo=99, fase="9.9")
    g = GraphIngestor()
    with pytest.raises(MissingEpochError) as excinfo:
        g.populate_list(graph, mini_volterra, sito=sito, dry_run=True)
    assert (99, "9.9") in excinfo.value.missing


def test_missing_epoch_create_inserts_period(mini_volterra):
    """D5-B — opt-in counts the would-be inserts; dry-run no writes."""
    from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor
    graph, sito = _make_graph_with_extra_epoch(
        mini_volterra, periodo=99, fase="9.9")
    g = GraphIngestor()
    result = g.populate_list(graph, mini_volterra, sito=sito,
                              dry_run=True, create_missing_epochs=True)
    assert result.epochs_created == 1


def test_populate_list_atomic_on_failure(mini_volterra):
    """D8 — any mid-loop exception ROLLBACKs (DB sha256 unchanged).

    Inject a resolver that raises on the first conflict.
    """
    import hashlib
    from modules.s3dgraphy.sync.graph_projector import GraphProjector
    from modules.s3dgraphy.sync.graph_ingestor import (
        GraphIngestor, GraphIngestError)
    from modules.s3dgraphy.sync.conflict_resolver import ConflictResolver

    class BombResolver(ConflictResolver):
        def resolve(self, db_row, graph_value, field):
            raise RuntimeError("simulated failure")

    sito = _read_sito(mini_volterra)
    graph = GraphProjector().populate_graph(mini_volterra, sito=sito)
    # Force a conflict: mutate one node's d_stratigrafica
    for n in graph.nodes:
        attrs = getattr(n, "attributes", None) or {}
        if attrs.get("us"):
            attrs["d_stratigrafica"] = "MUTATED FOR TEST"
            break

    sha_before = hashlib.sha256(mini_volterra.read_bytes()).hexdigest()
    g = GraphIngestor(conflict_resolver=BombResolver())
    with pytest.raises(GraphIngestError):
        g.populate_list(graph, mini_volterra, sito=sito, dry_run=False)
    sha_after = hashlib.sha256(mini_volterra.read_bytes()).hexdigest()
    assert sha_before == sha_after, "atomic rollback failed: DB changed"


def test_populate_list_inserts_new_rows(mini_volterra):
    """A graph node not present in DB → INSERT in write mode."""
    import sqlite3, uuid
    from s3dgraphy import Graph
    from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor

    sito = _read_sito(mini_volterra)
    new_uuid = str(uuid.uuid4())

    # Build a graph with one synthetic node not in DB
    class _Node:
        def __init__(self, **kw):
            self.node_id = kw["node_id"]
            self.name = kw["name"]
            self.attributes = kw["attributes"]
    graph = Graph(graph_id=sito)
    n = _Node(node_id=new_uuid, name="999",
              attributes={"us": "999", "sito": sito,
                          "unita_tipo": "US", "node_uuid": new_uuid})
    graph.add_node(n)

    GraphIngestor().populate_list(
        graph, mini_volterra, sito=sito, dry_run=False)

    # Verify the INSERT happened
    conn = sqlite3.connect(mini_volterra)
    row = conn.execute(
        "SELECT us, sito, unita_tipo FROM us_table WHERE node_uuid = ?",
        (new_uuid,)).fetchone()
    conn.close()
    assert row is not None
    assert row[0] == "999"
    assert row[1] == sito
    assert row[2] == "US"


def test_update_preserves_unmapped_columns(mini_volterra):
    """D3 — UPDATE selettivo preserves columns not in MAPPED_COLUMNS.

    Set descrizione (NOT in MAPPED_COLUMNS) on a row, run a graph
    that mutates d_stratigrafica (mapped) on the same row, verify
    descrizione survived intact.
    """
    import sqlite3
    from modules.s3dgraphy.sync.graph_projector import GraphProjector
    from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor

    sito = _read_sito(mini_volterra)

    # Set descrizione on the first row
    conn = sqlite3.connect(mini_volterra)
    # Detect descrizione column (may be named differently across schemas)
    cols = {r[1] for r in conn.execute(
        "PRAGMA table_info(us_table)").fetchall()}
    if "descrizione" not in cols:
        pytest.skip("us_table has no descrizione column on this schema")
    target_uuid = conn.execute(
        "SELECT node_uuid FROM us_table WHERE sito = ? LIMIT 1",
        (sito,)).fetchone()[0]
    conn.execute(
        "UPDATE us_table SET descrizione = ? WHERE node_uuid = ?",
        ("PRESERVED_BY_AI04", target_uuid))
    conn.commit()
    conn.close()

    # Project + mutate d_stratigrafica + ingest
    graph = GraphProjector().populate_graph(mini_volterra, sito=sito)
    found = False
    for n in graph.nodes:
        attrs = getattr(n, "attributes", None) or {}
        # Projector-built graphs carry node_uuid in attrs (node_id is
        # a separate surrogate). Match either, for forward-compat with
        # graphs constructed outside the projector.
        nuid = attrs.get("node_uuid") or getattr(n, "node_id", None)
        if nuid == target_uuid:
            attrs["d_stratigrafica"] = "AI04_NEW_VALUE"
            found = True
            break
    assert found, "test setup: target node not found in graph"
    GraphIngestor().populate_list(graph, mini_volterra, sito=sito,
                                   dry_run=False)

    # Verify descrizione survived
    conn = sqlite3.connect(mini_volterra)
    descr, dstrat = conn.execute(
        "SELECT descrizione, d_stratigrafica FROM us_table "
        "WHERE node_uuid = ?", (target_uuid,)).fetchone()
    conn.close()
    assert descr == "PRESERVED_BY_AI04", \
        f"unmapped column overwritten (got {descr!r})"
    assert dstrat == "AI04_NEW_VALUE", "mapped column not updated"
