"""yE-D Group C: L1 integration tests for the yEd-raw import pipeline.

7 tests exercise the full ``import_yed_raw`` orchestrator against
the shipped fixture ``em_demo_02_mini.graphml``, asserting the end-
to-end behaviour of each of the 4 policies + dry-run + idempotency +
ParadataStore dispatch.

Tests are SQLite-only — Group A + B already exercise the PG paths at
unit level via DbHandle; reproducing the full graphml fixture against
PG would be heavyweight and is covered by smoke + L2 PG fixtures
elsewhere.

Fixture geometry (verified inline before pinning):
  * 6 classified leaves:
      - n0::n0::n0   US_REAL        US01
      - n0::n0::n1   US_REAL        US02
      - n0::n0::n2   USV_VIRTUAL    USV101
      - n0::n0::n3   PROPERTY       material
      - n0::n1::n0   SPECIAL_FIND   SF105
      - n0::n1::n1   VIRTUAL_FIND   VSF107
  * 2 periods (TableNode rows)
  * 2 folders:
      - n0::n0  VA01-foundation example (attivita=VA01,
                members=[n0::n0::n0..n3])
      - n0::n1  AR01-area example       (area=AR01,
                members=[n0::n1::n0..n1])
  * 5 edges:
      - 2 leaf-to-leaf:
          (n0::n0::n0 -> n0::n0::n1, None)   [both US_REAL]
          (n0::n0::n2 -> n0::n0::n0, None)   [USV_VIRTUAL -> US_REAL]
      - 3 folder-touching:
          (folder n0::n0 -> leaf   n0::n0::n0, None)
          (leaf   n0::n0::n1 -> folder n0::n0, None)
          (folder n0::n0 -> folder n0::n1,         None)

Buckets after _classify_destination:
  sql_us   = 2 rows  (US01, US02)
  sql_inv  = 1 row   (SF105)
  paradata = 3 nodes (USV101, material, VSF107)
"""
from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy import text

from modules.s3dgraphy.sync._db_handle import DbHandle
from modules.s3dgraphy.sync.yed_classifier import classify_leaves
from modules.s3dgraphy.sync.yed_group_walker import walk_folders
from modules.s3dgraphy.sync.yed_table_parser import extract_periods
from modules.s3dgraphy.sync.yed_import_pipeline import import_yed_raw
from modules.s3dgraphy.sync.yed_rapporti_policy import FolderEdgePolicy


# ---------------------------------------------------------------------------
# Fixture path (shipped in yE-C)
# ---------------------------------------------------------------------------
FIXTURE = (
    Path(__file__).parent / "fixtures" / "em_demo_02_mini.graphml"
)


# ---------------------------------------------------------------------------
# DB schema (inline so the test stays independent of pyarchinit Base)
# ---------------------------------------------------------------------------

_US_TABLE_DDL = """
CREATE TABLE us_table (
    id_us INTEGER PRIMARY KEY AUTOINCREMENT,
    sito TEXT,
    area TEXT,
    us TEXT,
    unita_tipo TEXT,
    rapporti TEXT,
    attivita TEXT,
    struttura TEXT,
    settore TEXT,
    ambient TEXT,
    saggio TEXT,
    quad_par TEXT,
    node_uuid TEXT,
    UNIQUE (sito, area, us, unita_tipo)
)
"""

_INVENTARIO_DDL = """
CREATE TABLE inventario_materiali_table (
    id_invmat INTEGER PRIMARY KEY AUTOINCREMENT,
    sito TEXT,
    numero_inventario INTEGER,
    sub_inv TEXT,
    tipo_reperto TEXT,
    definizione TEXT,
    area TEXT,
    us TEXT,
    UNIQUE (sito, numero_inventario, sub_inv)
)
"""

_PERIODIZZAZIONE_DDL = """
CREATE TABLE periodizzazione_table (
    id_perfas INTEGER PRIMARY KEY AUTOINCREMENT,
    sito TEXT,
    periodo INTEGER,
    fase TEXT,
    cron_iniziale INTEGER,
    cron_finale INTEGER,
    descrizione TEXT,
    datazione_estesa TEXT,
    UNIQUE (sito, periodo, fase)
)
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_handle(tmp_path: Path) -> DbHandle:
    """Build a DbHandle on a fresh SQLite + 3 inline tables."""
    dbfile = tmp_path / "yed_d_integration.sqlite"
    handle = DbHandle.from_path(dbfile)
    with handle.engine.begin() as conn:
        conn.execute(text(_US_TABLE_DDL))
        conn.execute(text(_INVENTARIO_DDL))
        conn.execute(text(_PERIODIZZAZIONE_DDL))
    return handle


def _drafts_from_fixture() -> dict:
    """Build drafts dict from the shipped em_demo_02_mini fixture."""
    return {
        "classified": classify_leaves(FIXTURE),
        "periods":    extract_periods(FIXTURE),
        "folders":    walk_folders(FIXTURE),
    }


@pytest.fixture
def workspace_env(tmp_path, monkeypatch):
    """Point ParadataStore at an isolated workspace under tmp_path so it
    doesn't try to write into the user's real workspace directory.
    """
    workspace_root = tmp_path / "_workspace"
    workspace_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("PYARCHINIT_WORKSPACE_DIR", str(workspace_root))
    return workspace_root


# ---------------------------------------------------------------------------
# Test 1 — SKIP policy end-to-end
# ---------------------------------------------------------------------------

def test_yed_d_end_to_end_skip_policy(tmp_path: Path, workspace_env) -> None:
    """Full import on em_demo_02_mini with SKIP policy.

    Asserts:
      * us_table has 2 rows (US01, US02 — US_REAL leaves only).
      * inventario_materiali_table has 1 row (SF105).
      * periodizzazione_table has 2 rows.
      * us_table.rapporti contains only the leaf-to-leaf edge with
        an US source — i.e. exactly 1 rapporti row written.
      * No 'VA' unita_tipo rows present (SKIP doesn't synthesise).
    """
    handle = _make_handle(tmp_path)
    drafts = _drafts_from_fixture()

    result = import_yed_raw(
        handle, FIXTURE, sito="DEMO_SITE", drafts=drafts,
        policy=FolderEdgePolicy.SKIP,
    )

    assert result.errors == ()
    assert result.dry_run is False

    with handle.engine.connect() as conn:
        us_rows = list(conn.execute(
            text("SELECT us, unita_tipo, rapporti FROM us_table "
                 "WHERE sito = :s ORDER BY us"),
            {"s": "DEMO_SITE"},
        ))
        inv_count = conn.execute(
            text("SELECT COUNT(*) FROM inventario_materiali_table "
                 "WHERE sito = :s"),
            {"s": "DEMO_SITE"},
        ).scalar()
        per_count = conn.execute(
            text("SELECT COUNT(*) FROM periodizzazione_table "
                 "WHERE sito = :s"),
            {"s": "DEMO_SITE"},
        ).scalar()

    assert len(us_rows) == 2
    assert {r[0] for r in us_rows} == {"US01", "US02"}
    assert all(r[1] == "US" for r in us_rows)
    assert inv_count == 1
    assert per_count == 2

    # No VA synthetic rows under SKIP.
    assert all(r[1] != "VA" for r in us_rows)

    # Exactly one us_table row has rapporti written (US01 — source of
    # the only leaf-to-leaf edge whose source lives in us_table).
    rapporti_filled = [r for r in us_rows if r[2]]
    assert len(rapporti_filled) == 1


# ---------------------------------------------------------------------------
# Test 2 — FAN_OUT policy end-to-end
# ---------------------------------------------------------------------------

def test_yed_d_end_to_end_fan_out_policy(
    tmp_path: Path, workspace_env,
) -> None:
    """FAN_OUT explodes folder-touching edges to N x M leaf pairs.

    The fixture has 3 folder-touching edges; after FAN_OUT expansion
    plus the 2 leaf-to-leaf edges, _write_rapporti will produce
    rapporti for any source that has an us_table row. We assert both
    US01 and US02 have non-null rapporti (FAN_OUT expansion routes
    edges through them).
    """
    handle = _make_handle(tmp_path)
    drafts = _drafts_from_fixture()

    result = import_yed_raw(
        handle, FIXTURE, sito="DEMO_SITE", drafts=drafts,
        policy=FolderEdgePolicy.FAN_OUT,
    )

    assert result.errors == ()

    with handle.engine.connect() as conn:
        us_rows = list(conn.execute(
            text("SELECT us, rapporti FROM us_table "
                 "WHERE sito = :s ORDER BY us"),
            {"s": "DEMO_SITE"},
        ))

    by_us = {us: rapp for us, rapp in us_rows}
    # Both US_REAL rows touched: FAN_OUT routes folder->leaf and
    # leaf->folder pairs through US01 and US02 respectively.
    assert by_us.get("US01"), "US01 must have FAN_OUT rapporti"
    assert by_us.get("US02"), "US02 must have FAN_OUT rapporti"
    # FAN_OUT must produce strictly more rapporti routed through us_table
    # than SKIP (which produced only US01).
    filled = sum(1 for v in by_us.values() if v)
    assert filled >= 2


# ---------------------------------------------------------------------------
# Test 3 — REPRESENTATIVE policy end-to-end
# ---------------------------------------------------------------------------

def test_yed_d_end_to_end_representative_policy(
    tmp_path: Path, workspace_env,
) -> None:
    """REPRESENTATIVE collapses folders to their first leaf member.

    First member of VA01 folder is n0::n0::n0 (US01); first member of
    AR01 folder is n0::n1::n0 (SF105 — sql_inv, not in uuid_map).
    Edges:
      * VA01 -> n0::n0::n0 -> (US01, US01) self-loop dropped
      * n0::n0::n1 -> VA01 -> (US02 yed_id, US01) — src is US02
      * VA01 -> AR01 -> (US01, n0::n1::n0) — src is US01
    Plus 2 leaf-to-leaf. The leaf-to-leaf with src=USV_VIRTUAL is
    not in uuid_map and dropped.

    We assert: US01 has rapporti (multiple), US02 has rapporti.
    """
    handle = _make_handle(tmp_path)
    drafts = _drafts_from_fixture()

    result = import_yed_raw(
        handle, FIXTURE, sito="DEMO_SITE", drafts=drafts,
        policy=FolderEdgePolicy.REPRESENTATIVE,
    )

    assert result.errors == ()

    with handle.engine.connect() as conn:
        us_rows = list(conn.execute(
            text("SELECT us, rapporti FROM us_table "
                 "WHERE sito = :s ORDER BY us"),
            {"s": "DEMO_SITE"},
        ))

    by_us = {us: rapp for us, rapp in us_rows}
    assert by_us.get("US01"), "US01 first-member proxy must have rapporti"
    assert by_us.get("US02"), "US02 must have rapporti to first-member VA01"


# ---------------------------------------------------------------------------
# Test 4 — SYNTHETIC policy end-to-end
# ---------------------------------------------------------------------------

def test_yed_d_end_to_end_synthetic_policy(
    tmp_path: Path, workspace_env,
) -> None:
    """SYNTHETIC inserts one VA row per folder appearing in folder-edges.

    Both VA01 and AR01 appear in folder_touching edges, so 2 synthetic
    rows are expected (unita_tipo='VA'). Folder edges are rewired
    through the synthetic anchors so US01 + US02 rapporti reference
    them.
    """
    handle = _make_handle(tmp_path)
    drafts = _drafts_from_fixture()

    result = import_yed_raw(
        handle, FIXTURE, sito="DEMO_SITE", drafts=drafts,
        policy=FolderEdgePolicy.SYNTHETIC,
    )

    assert result.errors == ()

    with handle.engine.connect() as conn:
        va_rows = list(conn.execute(
            text("SELECT us, unita_tipo, node_uuid FROM us_table "
                 "WHERE sito = :s AND unita_tipo = 'VA' "
                 "ORDER BY us"),
            {"s": "DEMO_SITE"},
        ))
        total = conn.execute(
            text("SELECT COUNT(*) FROM us_table WHERE sito = :s"),
            {"s": "DEMO_SITE"},
        ).scalar()

    # 2 synthetic VA rows inserted (one per unique folder in
    # folder-touching edges).
    assert len(va_rows) == 2
    # Labels follow folder full_label.
    labels = {r[0] for r in va_rows}
    assert any("VA01" in lbl for lbl in labels)
    assert any("AR01" in lbl for lbl in labels)

    # Total = 2 US_REAL + 2 VA synthetic = 4 rows.
    assert total == 4


# ---------------------------------------------------------------------------
# Test 5 — ParadataStore dispatched for paradata leaves
# ---------------------------------------------------------------------------

def test_yed_d_paradata_written_via_store(
    tmp_path: Path, workspace_env,
) -> None:
    """The fixture has 3 paradata leaves (USV101, material, VSF107);
    `_write_paradata_via_store` is invoked for each, and the count
    reported in parsed_drafts must match.

    Note: ParadataStore lacks several add_* methods (PG-D era only
    added a few); the dispatch logs a skip for missing methods but
    still increments the attempted counter (spec § 6 line 307).
    """
    handle = _make_handle(tmp_path)
    drafts = _drafts_from_fixture()

    result = import_yed_raw(
        handle, FIXTURE, sito="DEMO_SITE", drafts=drafts,
        policy=FolderEdgePolicy.SKIP,
    )

    assert result.errors == ()
    assert result.parsed_drafts is not None
    # 3 paradata leaves attempted (USV_VIRTUAL + PROPERTY + VIRTUAL_FIND).
    assert result.parsed_drafts["paradata_count"] == 3


# ---------------------------------------------------------------------------
# Test 6 — dry_run rolls back the whole transaction
# ---------------------------------------------------------------------------

def test_yed_d_dry_run_rolls_back(tmp_path: Path, workspace_env) -> None:
    """dry_run=True executes every write under the transaction then
    raises ``_DryRunRollback`` so nothing commits.
    """
    handle = _make_handle(tmp_path)
    drafts = _drafts_from_fixture()

    result = import_yed_raw(
        handle, FIXTURE, sito="DEMO_SITE", drafts=drafts,
        policy=FolderEdgePolicy.SYNTHETIC,
        dry_run=True,
    )

    assert result.dry_run is True
    assert result.applied == 0

    with handle.engine.connect() as conn:
        for tbl in (
            "us_table", "inventario_materiali_table",
            "periodizzazione_table",
        ):
            cnt = conn.execute(
                text(f"SELECT COUNT(*) FROM {tbl}"),
            ).scalar()
            assert cnt == 0, f"{tbl} should be empty after dry-run"

    # Counts that WOULD have been applied are reported in parsed_drafts.
    assert result.parsed_drafts is not None
    assert "would_apply" in result.parsed_drafts
    assert result.parsed_drafts["would_apply"]["us_inserted"] == 2


# ---------------------------------------------------------------------------
# Test 7 — Idempotent on re-run (UNIQUE collision atomic rollback)
# ---------------------------------------------------------------------------

def test_yed_d_idempotent_on_re_run(
    tmp_path: Path, workspace_env,
) -> None:
    """Running the pipeline twice against the same SQLite + sito must
    leave the DB in the first-run state.

    Mechanism: the second run hits the UNIQUE (sito, area, us,
    unita_tipo) constraint when inserting US01 again — the whole
    transaction rolls back so we never see partial second-run data.
    """
    handle = _make_handle(tmp_path)
    drafts = _drafts_from_fixture()

    # First run — populates the DB.
    first = import_yed_raw(
        handle, FIXTURE, sito="DEMO_SITE", drafts=drafts,
        policy=FolderEdgePolicy.SKIP,
    )
    assert first.errors == ()
    assert first.applied > 0

    with handle.engine.connect() as conn:
        us_after_first = list(conn.execute(
            text("SELECT us FROM us_table "
                 "WHERE sito = :s ORDER BY us"),
            {"s": "DEMO_SITE"},
        ))
        period_after_first = conn.execute(
            text("SELECT COUNT(*) FROM periodizzazione_table"),
        ).scalar()

    # Second run — must error out with UNIQUE violation, atomic.
    second = import_yed_raw(
        handle, FIXTURE, sito="DEMO_SITE", drafts=drafts,
        policy=FolderEdgePolicy.SKIP,
    )
    assert second.applied == 0
    assert len(second.errors) >= 1

    # First run's data must be intact.
    with handle.engine.connect() as conn:
        us_after_second = list(conn.execute(
            text("SELECT us FROM us_table "
                 "WHERE sito = :s ORDER BY us"),
            {"s": "DEMO_SITE"},
        ))
        period_after_second = conn.execute(
            text("SELECT COUNT(*) FROM periodizzazione_table"),
        ).scalar()

    assert us_after_second == us_after_first
    assert period_after_second == period_after_first
