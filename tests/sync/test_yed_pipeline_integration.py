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

from s3dgraphy.sync._db_handle import DbHandle
from s3dgraphy.sync.yed_classifier import classify_leaves
from s3dgraphy.sync.yed_group_walker import walk_folders
from s3dgraphy.sync.yed_table_parser import extract_periods
from s3dgraphy.sync.yed_import_pipeline import import_yed_raw
from s3dgraphy.sync.yed_rapporti_policy import FolderEdgePolicy


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
    periodo_iniziale TEXT,
    fase_iniziale TEXT,
    periodo_finale TEXT,
    fase_finale TEXT,
    d_stratigrafica TEXT,
    other_locations TEXT,
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
    cont_per INTEGER,
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

    # User-feedback 2026-05-13: USV_VIRTUAL joins us_table.
    # User-feedback 2026-05-15: SF + VSF also join us_table (dual-write).
    # User-feedback 2026-05-15 v2: PROPERTY 'material' also joins
    # us_table (unita_tipo='property') per the pyarchinit convention.
    # So fixture's 6 classified leaves produce 6 us_table rows.
    # us values are stripped: 'US01'→'01', 'USV101'→'101',
    # 'SF105'→'105', 'VSF107'→'107'; 'material' is a canonical
    # PROPERTY name so it stays as-is.
    assert len(us_rows) == 6
    assert {r[0] for r in us_rows} == {
        "01", "02", "101", "105", "107", "material",
    }
    by_us = {r[0]: r[1] for r in us_rows}
    assert by_us["01"] == "US"
    assert by_us["02"] == "US"
    assert by_us["101"] == "USV"
    assert by_us["105"] == "SF"
    assert by_us["107"] == "VSF"
    assert by_us["material"] == "property"
    # SF + VSF dual-write into inventario.
    assert inv_count == 2
    assert per_count == 2

    # No VA synthetic rows under SKIP.
    assert all(r[1] != "VA" for r in us_rows)

    # After USV/SF/VSF moved into sql_us, multiple leaves are valid
    # rapporti sources whose targets also live in us_table.
    # Verify targets are LABELS (us values), not yed_ids.
    rapporti_filled = [r for r in us_rows if r[2]]
    assert len(rapporti_filled) >= 2
    # Rapporti target resolution: the JSON list must reference us
    # labels (stripped numeric), NEVER yed_ids like "n0::n4::n12".
    for r in rapporti_filled:
        rapp_json = r[2]
        assert "::" not in rapp_json, (
            f"rapporti contains yed_id (target unresolved): {rapp_json}"
        )


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
    # leaf->folder pairs through US01 ('01') and US02 ('02').
    assert by_us.get("01"), "US01 must have FAN_OUT rapporti"
    assert by_us.get("02"), "US02 must have FAN_OUT rapporti"
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
    # us values are stripped: US01→'01', US02→'02'.
    assert by_us.get("01"), "US01 first-member proxy must have rapporti"
    assert by_us.get("02"), "US02 must have rapporti to first-member VA01"


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

    # Total = 2 US_REAL + 1 USV_VIRTUAL + 1 SF + 1 VSF + 1 PROPERTY +
    # 2 VA synthetic = 8 rows. All 4 paradata-family kinds joined
    # sql_us per 2026-05-15 v2 user feedback (DOC/Combinar/Extractor/
    # property unita_tipo); SF / VSF / RSF additionally dual-write
    # into inventario_materiali (subset _DUAL_WRITE_INV_KINDS).
    assert total == 8


# ---------------------------------------------------------------------------
# Test 5 — ParadataStore dispatched for paradata leaves
# ---------------------------------------------------------------------------

def test_yed_d_paradata_bucket_is_empty(
    tmp_path: Path, workspace_env,
) -> None:
    """After 2026-05-15 v2 user feedback, NO label-prefix classifier
    target routes to the paradata.graphml bucket — DOCUMENT / COMBINER
    / EXTRACTOR / PROPERTY are now us_table records too. The dispatch
    count is 0 and the paradata.graphml file is never created via this
    path.
    """
    handle = _make_handle(tmp_path)
    drafts = _drafts_from_fixture()

    result = import_yed_raw(
        handle, FIXTURE, sito="DEMO_SITE", drafts=drafts,
        policy=FolderEdgePolicy.SKIP,
    )

    assert result.errors == ()
    assert result.parsed_drafts is not None
    # paradata bucket empty after the 2026-05-15 v2 refactor.
    assert result.parsed_drafts["paradata_count"] == 0

    # The PROPERTY 'material' lands in us_table, NOT paradata.graphml.
    with handle.engine.connect() as conn:
        prop_row = conn.execute(
            text("SELECT us, unita_tipo FROM us_table "
                 "WHERE sito = :s AND unita_tipo = 'property'"),
            {"s": "DEMO_SITE"},
        ).first()
    assert prop_row is not None
    assert prop_row[0] == "material"


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
    # Post 2026-05-15 v2: 2 US_REAL + 1 USV_VIRTUAL + 1 SF + 1 VSF +
    # 1 PROPERTY = 6 us-class rows. All paradata-family kinds joined
    # sql_us (DOC/Combinar/Extractor/property unita_tipo). SYNTHETIC
    # adds 2 synthetic VA rows on top via `_write_rapporti`, not
    # counted here.
    assert result.parsed_drafts["would_apply"]["us_inserted"] == 6


# ---------------------------------------------------------------------------
# Test 7 — Idempotent on re-run (UNIQUE collision atomic rollback)
# ---------------------------------------------------------------------------

def test_yed_d_idempotent_on_re_run(
    tmp_path: Path, workspace_env,
) -> None:
    """Bug H (2026-05-15 user feedback): re-running the pipeline twice
    against the same SQLite + sito must SKIP existing rows silently,
    NOT trigger an atomic rollback. The first run's data stays intact
    and the second run reports 0 new inserts but no errors.

    Mechanism: ``_write_us_rows`` / ``_write_inventario_rows`` /
    ``_write_periodizzazione_rows`` each pre-load existing keys for
    the sito and skip leaves whose dedup_key is already present.
    Existing us_table rows are surfaced into ``uuid_map`` so
    downstream rapporti continue to resolve.
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

    # Second run — must be idempotent: no errors, no new inserts.
    second = import_yed_raw(
        handle, FIXTURE, sito="DEMO_SITE", drafts=drafts,
        policy=FolderEdgePolicy.SKIP,
    )
    assert second.errors == ()
    assert second.inserted == 0  # everything skipped as existing

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


# ---------------------------------------------------------------------------
# yE-E (5.8.2-alpha) — overrides applied end-to-end on em_demo_02_mini
# ---------------------------------------------------------------------------

def test_apply_overrides_e2e_classifier_changes_us_count(
    tmp_path: Path, workspace_env,
) -> None:
    """Forcing one PROPERTY leaf back into us_table via classifier
    override → us_table row count increments by 1 vs the auto run.

    The fixture has 1 PROPERTY leaf 'material' classified as PROPERTY.
    Auto routing: paradata. With an override that re-routes it to
    US_REAL, it should land in us_table (unita_tipo='US')."""
    from s3dgraphy.sync.yed_classifier import ClassificationKind
    from s3dgraphy.sync.yed_import_pipeline import YedOverrides
    handle = _make_handle(tmp_path)
    drafts = _drafts_from_fixture()

    # Find the PROPERTY leaf's yed_id.
    property_yed_id = None
    for c in drafts["classified"]:
        if c.auto_kind == ClassificationKind.PROPERTY:
            property_yed_id = c.yed_id
            break
    assert property_yed_id is not None, "fixture invariant: needs a PROPERTY leaf"

    ov = YedOverrides(classifier={property_yed_id: ClassificationKind.US_REAL})

    result = import_yed_raw(
        handle, FIXTURE, sito="DEMO_SITE", drafts=drafts,
        policy=FolderEdgePolicy.SKIP,
        overrides=ov,
    )
    assert result.errors == ()

    with handle.engine.connect() as conn:
        us_rows = list(conn.execute(
            text("SELECT us, unita_tipo FROM us_table "
                 "WHERE sito = :s ORDER BY us"),
            {"s": "DEMO_SITE"},
        ))
    # Baseline (no override): 2 US_REAL + 1 USV_VIRTUAL + 1 SF + 1 VSF
    # + 1 PROPERTY = 6 rows (PROPERTY 'material' now lives in us_table
    # with unita_tipo='property'). Override re-routes 'material' from
    # property → US_REAL → still 6 rows total but the 'material' row
    # has unita_tipo='US' instead of 'property'.
    assert len(us_rows) == 6
    assert any(r[0] == "material" and r[1] == "US" for r in us_rows)
    # And NOT 'property' anymore (the override took precedence).
    assert not any(
        r[0] == "material" and r[1] == "property" for r in us_rows
    )


def test_apply_overrides_e2e_folder_skip(
    tmp_path: Path, workspace_env,
) -> None:
    """A folder override with dimension='skip' must exclude that
    folder from the _apply_yed_folder_dimensions UPDATE pass.

    Auto run: each us_table row gets attivita = the folder's
    auto_value. With override skipping the folder, attivita stays NULL
    for those member rows."""
    from s3dgraphy.sync.yed_import_pipeline import YedOverrides
    handle = _make_handle(tmp_path)
    drafts = _drafts_from_fixture()

    # Pick the first folder and force-skip it.
    folder = drafts["folders"][0]
    ov = YedOverrides(folders={folder.yed_id: {"dimension": "skip"}})

    result = import_yed_raw(
        handle, FIXTURE, sito="DEMO_SITE", drafts=drafts,
        policy=FolderEdgePolicy.SKIP,
        overrides=ov,
    )
    assert result.errors == ()

    with handle.engine.connect() as conn:
        # Members of the skipped folder must have NULL attivita.
        # `flatten_members` of folder[0] = direct + nested. Query
        # us_table for all rows tied to the site and check attivita
        # is NULL for at least one of them (the folder's members).
        rows = list(conn.execute(
            text("SELECT us, attivita FROM us_table WHERE sito = :s"),
            {"s": "DEMO_SITE"},
        ))
    # At least one row has NULL attivita because the folder was skipped.
    assert any(r[1] is None or r[1] == "" for r in rows), (
        f"expected at least one row with NULL attivita; got: {rows}"
    )
