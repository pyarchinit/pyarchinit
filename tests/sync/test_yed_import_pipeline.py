"""yE-D Group B: L0 unit tests for yed_import_pipeline module.

8 tests cover the pipeline's helpers + write functions in isolation
against a temp SQLite DB. We build minimal table schemas inline so
the tests don't depend on the full pyarchinit Base (which would
pull in optional dependencies).

The orchestrator ``import_yed_raw`` is exercised twice:
* dry-run rollback via the _DryRunRollback sentinel.
* atomic rollback on UNIQUE-constraint violation (forced by
  duplicate INSERT into us_table).

Tests:
1. test_classify_destination_splits_correctly
2. test_flatten_members_recursive
3. test_write_us_rows_assigns_node_uuid
4. test_write_inventario_rows_uses_special_find_kind
5. test_write_periodizzazione_rows_creates_one_per_period
6. test_apply_yed_folder_dimensions_updates_attivita_column
7. test_dry_run_rollback_sentinel_works
8. test_atomic_rollback_on_integrity_error
"""
from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy import text

from modules.s3dgraphy.sync._db_handle import DbHandle
from modules.s3dgraphy.sync.yed_classifier import (
    ClassificationKind,
    ClassifiedNode,
)
from modules.s3dgraphy.sync.yed_group_walker import FolderCandidate
from modules.s3dgraphy.sync.yed_rapporti_policy import FolderEdgePolicy
from modules.s3dgraphy.sync.yed_import_pipeline import (
    _DryRunRollback,
    _apply_yed_folder_dimensions,
    _classify_destination,
    _flatten_members,
    _write_inventario_rows,
    _write_periodizzazione_rows,
    _write_us_rows,
    import_yed_raw,
)


# ---------------------------------------------------------------------------
# Fixtures
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
    area_dim TEXT,
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


def _make_handle(tmp_path: Path) -> DbHandle:
    """Build a DbHandle wrapping a fresh temp SQLite + all 3 tables."""
    dbfile = tmp_path / "test_pipeline.sqlite"
    handle = DbHandle.from_path(dbfile)
    with handle.engine.begin() as conn:
        conn.execute(text(_US_TABLE_DDL))
        conn.execute(text(_INVENTARIO_DDL))
        conn.execute(text(_PERIODIZZAZIONE_DDL))
    return handle


def _leaf(yed_id: str, kind: ClassificationKind,
          label: str | None = None) -> ClassifiedNode:
    """Build a minimal ClassifiedNode for tests."""
    return ClassifiedNode(
        yed_id=yed_id,
        label=label or yed_id,
        auto_kind=kind,
        user_kind=kind,
    )


def _folder(yed_id: str, label: str, *,
            members: list[str] | None = None,
            nested: list[str] | None = None,
            auto_dim: str | None = "attivita",
            value: str | None = None) -> FolderCandidate:
    """Build a minimal FolderCandidate for tests."""
    return FolderCandidate(
        yed_id=yed_id,
        full_label=label,
        auto_dimension=auto_dim,
        user_dimension=auto_dim,
        auto_value=value or label.split("-")[0],
        user_value=value or label.split("-")[0],
        member_yed_ids=list(members or []),
        nested_folder_ids=list(nested or []),
        parent_folder_id=None,
    )


# ---------------------------------------------------------------------------
# Test 1 — _classify_destination
# ---------------------------------------------------------------------------

def test_classify_destination_splits_correctly() -> None:
    """Mixed kinds split into sql_us / sql_inv / paradata / skipped.

    User-feedback 2026-05-13: virtual stratigraphic units (USV*) are
    "unità tipo" and belong to us_table, NOT paradata. The pipeline's
    destination map was corrected to route USV_VIRTUAL + USV_FORMAL
    into the sql_us bucket alongside US_REAL / US_MASONRY / US_DOCUMENTARY.
    """
    nodes = [
        _leaf("u1", ClassificationKind.US_REAL, "US1"),
        _leaf("u2", ClassificationKind.US_MASONRY, "USM1"),
        _leaf("u3", ClassificationKind.US_DOCUMENTARY, "USD1"),
        _leaf("s1", ClassificationKind.SPECIAL_FIND, "SF1"),
        _leaf("v1", ClassificationKind.USV_VIRTUAL, "USV1"),
        _leaf("vs1", ClassificationKind.USV_FORMAL, "USVs1"),
        _leaf("vf1", ClassificationKind.VIRTUAL_FIND, "VSF1"),
        _leaf("d1", ClassificationKind.DOCUMENT, "D.1"),
        _leaf("p1", ClassificationKind.PROPERTY, "material"),
        _leaf("x1", ClassificationKind.UNKNOWN, "??"),
        _leaf("x2", ClassificationKind.SKIP, "skipme"),
    ]

    result = _classify_destination(nodes)

    # USV_* now joins us_table alongside the US family.
    assert {c.yed_id for c in result["sql_us"]} == {
        "u1", "u2", "u3", "v1", "vs1",
    }
    assert {c.yed_id for c in result["sql_inv"]} == {"s1"}
    assert {c.yed_id for c in result["paradata"]} == {
        "vf1", "d1", "p1",
    }
    assert {c.yed_id for c in result["skipped"]} == {"x1", "x2"}


def test_classify_destination_routes_rsf_to_us_table() -> None:
    """s3dgraphy-bump 0.1.42: REUSED_SPECIAL_FIND (RSF / spolia) goes
    to us_table (sql_us bucket) with unita_tipo='RSF', NOT to
    inventario_materiali nor paradata."""
    nodes = [
        _leaf("r1", ClassificationKind.REUSED_SPECIAL_FIND, "RSF42"),
        _leaf("s1", ClassificationKind.SPECIAL_FIND, "SF99"),
    ]
    result = _classify_destination(nodes)
    assert {c.yed_id for c in result["sql_us"]} == {"r1"}
    assert {c.yed_id for c in result["sql_inv"]} == {"s1"}
    # _resolve_unita_tipo + _CLASSIFIED_KIND_TO_UNITA_TIPO contract.
    from modules.s3dgraphy.sync.yed_import_pipeline import _resolve_unita_tipo
    assert _resolve_unita_tipo(nodes[0]) == "RSF"


# ---------------------------------------------------------------------------
# Test 2 — _flatten_members recursive
# ---------------------------------------------------------------------------

def test_flatten_members_recursive() -> None:
    """A folder with nested folders flattens to all member ids."""
    inner = _folder(
        "inner",
        "VA02-inner",
        members=["leaf_c", "leaf_d"],
    )
    outer = _folder(
        "outer",
        "VA01-outer",
        members=["leaf_a", "leaf_b"],
        nested=["inner"],
    )
    all_folders = [outer, inner]

    members = _flatten_members(outer, all_folders)

    # Direct + nested members combined.
    assert set(members) == {"leaf_a", "leaf_b", "leaf_c", "leaf_d"}
    # Direct members come first per the walker.
    assert members[0] in {"leaf_a", "leaf_b"}
    assert members[1] in {"leaf_a", "leaf_b"}


# ---------------------------------------------------------------------------
# Test 3 — _write_us_rows assigns node_uuid
# ---------------------------------------------------------------------------

def test_write_us_rows_assigns_node_uuid(tmp_path: Path) -> None:
    """2 US_REAL leaves → 2 us_table rows with fresh node_uuids."""
    handle = _make_handle(tmp_path)
    leaves = [
        _leaf("y1", ClassificationKind.US_REAL, "US1"),
        _leaf("y2", ClassificationKind.US_REAL, "US2"),
    ]

    with handle.engine.begin() as conn:
        count, uuid_map = _write_us_rows(conn, leaves, sito="X")

    assert count == 2
    assert set(uuid_map.keys()) == {"y1", "y2"}
    for nu in uuid_map.values():
        # uuid7().hex is 32 hex chars
        assert len(nu) == 32
        assert all(ch in "0123456789abcdef" for ch in nu)

    with handle.engine.connect() as conn:
        rows = list(conn.execute(
            text("SELECT us, unita_tipo, node_uuid FROM us_table "
                 "WHERE sito = :s ORDER BY us"),
            {"s": "X"},
        ))
    assert len(rows) == 2
    assert rows[0][0] == "US1"
    assert rows[0][1] == "US"
    assert rows[1][0] == "US2"
    assert rows[0][2] == uuid_map["y1"]
    assert rows[1][2] == uuid_map["y2"]


# ---------------------------------------------------------------------------
# Test 4 — _write_inventario_rows uses SPECIAL_FIND
# ---------------------------------------------------------------------------

def test_write_inventario_rows_uses_special_find_kind(
    tmp_path: Path,
) -> None:
    """1 SPECIAL_FIND leaf → 1 inventario_materiali_table row."""
    handle = _make_handle(tmp_path)
    leaves = [
        _leaf("sf1", ClassificationKind.SPECIAL_FIND, "SF1"),
    ]

    with handle.engine.begin() as conn:
        count = _write_inventario_rows(conn, leaves, sito="X")

    assert count == 1
    with handle.engine.connect() as conn:
        rows = list(conn.execute(
            text("SELECT sito, tipo_reperto, definizione "
                 "FROM inventario_materiali_table"),
        ))
    assert len(rows) == 1
    assert rows[0][0] == "X"
    assert rows[0][1] == "SF"
    assert rows[0][2] == "SF1"


# ---------------------------------------------------------------------------
# Test 5 — _write_periodizzazione_rows creates one per period
# ---------------------------------------------------------------------------

def test_write_periodizzazione_rows_creates_one_per_period(
    tmp_path: Path,
) -> None:
    """3 PeriodCandidates → 3 rows in periodizzazione_table."""
    handle = _make_handle(tmp_path)

    # Build PeriodCandidate-shaped objects locally (avoid importing
    # the dataclass to keep this test minimal).
    from modules.s3dgraphy.sync.yed_table_parser import PeriodCandidate
    periods = [
        PeriodCandidate(
            yed_row_id=f"r{i}",
            auto_label=f"Phase {i}",
            user_label=f"Phase {i}",
            auto_periodo=i,
            auto_fase=1,
            user_periodo=i,
            user_fase=1,
        )
        for i in (1, 2, 3)
    ]

    with handle.engine.begin() as conn:
        count = _write_periodizzazione_rows(conn, periods, sito="X")

    assert count == 3
    with handle.engine.connect() as conn:
        rows = list(conn.execute(
            text("SELECT sito, periodo, fase, descrizione "
                 "FROM periodizzazione_table ORDER BY periodo"),
        ))
    assert len(rows) == 3
    assert rows[0][0] == "X"
    assert rows[0][1] == 1
    # cron_iniziale + cron_finale stay NULL (verified by absence in
    # the SELECT list above; defensive double-check below).
    with handle.engine.connect() as conn:
        nulls = conn.execute(
            text("SELECT cron_iniziale, cron_finale "
                 "FROM periodizzazione_table"),
        ).first()
    assert nulls[0] is None
    assert nulls[1] is None


# ---------------------------------------------------------------------------
# Test 6 — _apply_yed_folder_dimensions UPDATEs attivita column
# ---------------------------------------------------------------------------

def test_apply_yed_folder_dimensions_updates_attivita_column(
    tmp_path: Path,
) -> None:
    """Folder VA01 (attivita) with 2 leaf members → 2 UPDATEs."""
    handle = _make_handle(tmp_path)

    # Insert 3 us_table rows; only 2 of them are folder members.
    sql_us = [
        _leaf("n1", ClassificationKind.US_REAL, "US1"),
        _leaf("n2", ClassificationKind.US_REAL, "US2"),
        _leaf("n3", ClassificationKind.US_REAL, "US3"),
    ]
    with handle.engine.begin() as conn:
        _, uuid_map = _write_us_rows(conn, sql_us, sito="X")

    folder = _folder(
        "F1", "VA01-foundation",
        members=["n1", "n2"],
        auto_dim="attivita",
        value="VA01",
    )

    with handle.engine.begin() as conn:
        updated = _apply_yed_folder_dimensions(
            conn, [folder], sito="X", uuid_map=uuid_map,
        )

    assert updated == 2
    with handle.engine.connect() as conn:
        rows = list(conn.execute(
            text("SELECT us, attivita FROM us_table "
                 "WHERE sito = :s ORDER BY us"),
            {"s": "X"},
        ))
    by_us = {us: attivita for us, attivita in rows}
    assert by_us["US1"] == "VA01"
    assert by_us["US2"] == "VA01"
    assert by_us["US3"] is None  # not a member


# ---------------------------------------------------------------------------
# Test 7 — dry_run rollback sentinel works
# ---------------------------------------------------------------------------

def test_dry_run_rollback_sentinel_works(tmp_path: Path) -> None:
    """import_yed_raw with dry_run=True must not commit anything."""
    handle = _make_handle(tmp_path)

    drafts = {
        "classified": [
            _leaf("y1", ClassificationKind.US_REAL, "US1"),
            _leaf("y2", ClassificationKind.US_REAL, "US2"),
        ],
        "periods": [],
        "folders": [],
    }

    # Pass a non-existent path so analyze_edges returns empty (no
    # edges to write).
    result = import_yed_raw(
        handle,
        graphml_path=tmp_path / "nonexistent.graphml",
        sito="X",
        drafts=drafts,
        policy=FolderEdgePolicy.SKIP,
        dry_run=True,
    )

    assert result.dry_run is True
    assert result.applied == 0
    # DB stays empty
    with handle.engine.connect() as conn:
        cnt = conn.execute(
            text("SELECT COUNT(*) FROM us_table"),
        ).scalar()
    assert cnt == 0

    # parsed_drafts is populated even on dry_run
    assert result.parsed_drafts is not None
    assert "classified" in result.parsed_drafts
    assert "would_apply" in result.parsed_drafts
    assert result.parsed_drafts["would_apply"]["us_inserted"] == 2


# ---------------------------------------------------------------------------
# Test 8 — atomic rollback on IntegrityError
# ---------------------------------------------------------------------------

def test_atomic_rollback_on_integrity_error(tmp_path: Path) -> None:
    """A draft that forces a UNIQUE-constraint violation must commit
    nothing — earlier inserts must roll back."""
    handle = _make_handle(tmp_path)

    # Pre-populate us_table with one row that will collide on the
    # second draft insert (same sito + area + us + unita_tipo).
    with handle.engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO us_table "
                "(sito, area, us, unita_tipo, node_uuid) "
                "VALUES (:s, :a, :u, :t, :n)"
            ),
            {"s": "X", "a": "1", "u": "DUP", "t": "US", "n": "deadbeef"},
        )

    drafts = {
        # First leaf would insert clean. Second leaf collides with the
        # pre-existing 'DUP' row → IntegrityError → rollback the whole
        # transaction → "fresh" leaf does NOT survive.
        "classified": [
            _leaf("y_fresh", ClassificationKind.US_REAL, "FRESH"),
            _leaf("y_dup", ClassificationKind.US_REAL, "DUP"),
        ],
        "periods": [],
        "folders": [],
    }

    result = import_yed_raw(
        handle,
        graphml_path=tmp_path / "nonexistent.graphml",
        sito="X",
        drafts=drafts,
        policy=FolderEdgePolicy.SKIP,
        dry_run=False,
    )

    assert result.applied == 0
    assert len(result.errors) == 1
    # Only the pre-existing DUP row survives — FRESH must be rolled back.
    with handle.engine.connect() as conn:
        rows = [
            r[0] for r in conn.execute(
                text("SELECT us FROM us_table WHERE sito = :s"),
                {"s": "X"},
            )
        ]
    assert rows == ["DUP"]
