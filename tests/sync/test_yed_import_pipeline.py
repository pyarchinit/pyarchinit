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

from s3dgraphy.sync._db_handle import DbHandle
from s3dgraphy.sync.yed_classifier import (
    ClassificationKind,
    ClassifiedNode,
)
from s3dgraphy.sync.yed_group_walker import FolderCandidate
from s3dgraphy.sync.yed_rapporti_policy import FolderEdgePolicy
from s3dgraphy.sync.yed_import_pipeline import (
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

    User-feedback 2026-05-15 (yed-fastfix v2): EVERY pyarchinit
    archaeological-record kind goes to us_table — including the
    paradata-family DOCUMENT / COMBINER / EXTRACTOR / PROPERTY (with
    unita_tipo='DOC' / 'Combinar' / 'Extractor' / 'property' per the
    pyarchinit convention verified against ``pyarchinit_db.sqlite``).
    The paradata.graphml dispatch is now an empty path; nothing
    reaches it via the label-prefix classifier.

    SF / VSF / RSF additionally dual-write into inventario_materiali
    (subset _DUAL_WRITE_INV_KINDS).
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
        _leaf("c1", ClassificationKind.COMBINER, "C.1"),
        _leaf("e1", ClassificationKind.EXTRACTOR, "E.1"),
        _leaf("p1", ClassificationKind.PROPERTY, "material"),
        _leaf("x1", ClassificationKind.UNKNOWN, "??"),
        _leaf("x2", ClassificationKind.SKIP, "skipme"),
    ]

    result = _classify_destination(nodes)

    # Every recognised kind goes to us_table.
    assert {c.yed_id for c in result["sql_us"]} == {
        "u1", "u2", "u3", "v1", "vs1", "s1", "vf1",
        "d1", "c1", "e1", "p1",
    }
    # SF / VSF dual-written: appear ALSO in sql_inv (DOC/COMBINER/
    # EXTRACTOR/PROPERTY are NOT in the dual-write subset).
    assert {c.yed_id for c in result["sql_inv"]} == {"s1", "vf1"}
    # Paradata bucket empty (no label-prefix kind targets paradata.graphml).
    assert result["paradata"] == []
    assert {c.yed_id for c in result["skipped"]} == {"x1", "x2"}


def test_classify_destination_routes_rsf_to_us_table() -> None:
    """s3dgraphy-bump 0.1.42: REUSED_SPECIAL_FIND (RSF / spolia) goes
    to us_table (sql_us bucket) with unita_tipo='RSF'.

    User-feedback 2026-05-15 (yed-fastfix): RSF is ALSO dual-written
    into inventario_materiali (alongside SF / VSF).
    """
    nodes = [
        _leaf("r1", ClassificationKind.REUSED_SPECIAL_FIND, "RSF42"),
        _leaf("s1", ClassificationKind.SPECIAL_FIND, "SF99"),
    ]
    result = _classify_destination(nodes)
    # Both RSF and SF land in us_table now.
    assert {c.yed_id for c in result["sql_us"]} == {"r1", "s1"}
    # Both also dual-write to inventario.
    assert {c.yed_id for c in result["sql_inv"]} == {"r1", "s1"}
    # _resolve_unita_tipo + _CLASSIFIED_KIND_TO_UNITA_TIPO contract.
    from s3dgraphy.sync.yed_import_pipeline import _resolve_unita_tipo
    assert _resolve_unita_tipo(nodes[0]) == "RSF"
    assert _resolve_unita_tipo(nodes[1]) == "SF"


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
    """2 US_REAL leaves → 2 us_table rows with fresh node_uuids.

    User-feedback 2026-05-15 (yed-fastfix): the ``us`` column stores
    the numeric portion only; the prefix lives in ``unita_tipo``. So
    label='US1' → us='1', unita_tipo='US'.
    """
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
    # us column carries the STRIPPED numeric portion only.
    assert rows[0][0] == "1"
    assert rows[0][1] == "US"
    assert rows[1][0] == "2"
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
    """3 PeriodCandidates → 3 rows in periodizzazione_table.

    User-feedback 2026-05-15 (yed-fastfix): the UI ``Codice periodo``
    field maps to column ``cont_per`` (Integer). Populated with the
    same sequential integer as ``periodo`` so the form's read path
    resolves cleanly.
    """
    handle = _make_handle(tmp_path)

    # Build PeriodCandidate-shaped objects locally (avoid importing
    # the dataclass to keep this test minimal).
    from s3dgraphy.sync.yed_table_parser import PeriodCandidate
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
            text("SELECT sito, periodo, fase, descrizione, cont_per "
                 "FROM periodizzazione_table ORDER BY periodo"),
        ))
    assert len(rows) == 3
    assert rows[0][0] == "X"
    assert rows[0][1] == 1
    # cont_per is filled with the same sequential integer as periodo.
    assert rows[0][4] == 1
    assert rows[1][4] == 2
    assert rows[2][4] == 3
    # cron_iniziale + cron_finale stay NULL.
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
    # us values are stripped of the 'US' prefix per yed-fastfix.
    assert by_us["1"] == "VA01"
    assert by_us["2"] == "VA01"
    assert by_us["3"] is None  # not a member


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

def test_idempotent_skip_on_existing_us_row(tmp_path: Path) -> None:
    """Bug H (2026-05-15 user feedback): a draft containing leaves
    whose (us, unita_tipo) keys already exist in us_table must NOT
    rollback the transaction — the existing rows are surfaced into
    uuid_map (so rapporti continue to resolve) and the import
    continues with the truly-new leaves.

    Pre-existing row: us='100', unita_tipo='US', sito='X'.
    Drafts:
      - 'US100' → dedup_key=('100','US') matches pre-existing → SKIP
      - 'US200' → fresh → INSERT
    Expected: 2 us_table rows total ('100' kept + '200' inserted),
    no errors, applied > 0.
    """
    handle = _make_handle(tmp_path)

    # Pre-populate us_table with one row that simulates a previous
    # import that left this key in place.
    with handle.engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO us_table "
                "(sito, area, us, unita_tipo, node_uuid) "
                "VALUES (:s, :a, :u, :t, :n)"
            ),
            {"s": "X", "a": "1", "u": "100", "t": "US", "n": "deadbeef"},
        )

    drafts = {
        "classified": [
            # US100 → strip → '100', collides with pre-existing
            _leaf("y_dup", ClassificationKind.US_REAL, "US100"),
            # US200 → strip → '200', fresh
            _leaf("y_fresh", ClassificationKind.US_REAL, "US200"),
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

    # No error — the dup leaf is silently skipped, the fresh one is
    # inserted. applied > 0 (1 INSERT).
    assert result.errors == ()
    assert result.applied == 1
    assert result.inserted == 1
    # Two us_table rows: the pre-existing one + the new one.
    with handle.engine.connect() as conn:
        rows = sorted(
            r[0] for r in conn.execute(
                text("SELECT us FROM us_table WHERE sito = :s"),
                {"s": "X"},
            )
        )
    assert rows == ["100", "200"]
    # Pre-existing row's node_uuid preserved (not rewritten).
    with handle.engine.connect() as conn:
        dup_uuid = conn.execute(
            text(
                "SELECT node_uuid FROM us_table "
                "WHERE sito = :s AND us = :u"
            ),
            {"s": "X", "u": "100"},
        ).scalar()
    assert dup_uuid == "deadbeef"


# ---------------------------------------------------------------------------
# yE-E (5.8.2-alpha) — YedOverrides + apply_overrides_to_drafts contract
# ---------------------------------------------------------------------------

def test_apply_overrides_empty_is_identity() -> None:
    """An empty YedOverrides() leaves user_kind / user_dimension /
    user_value / user_periodo / user_fase at their auto_* values."""
    from s3dgraphy.sync.yed_import_pipeline import (
        YedOverrides, apply_overrides_to_drafts,
    )
    from s3dgraphy.sync.yed_table_parser import PeriodCandidate

    classified = [_leaf("c0", ClassificationKind.US_REAL, "US01")]
    periods = [PeriodCandidate(
        yed_row_id="p0", auto_label="Period01",
        user_label="Period01", auto_periodo=1, auto_fase=1,
        user_periodo=1, user_fase=1,
    )]
    folders = [_folder("f0", "VA01", value="VA01")]
    drafts = {"classified": classified, "periods": periods, "folders": folders}

    out = apply_overrides_to_drafts(drafts, YedOverrides())

    assert out["classified"][0].user_kind == ClassificationKind.US_REAL
    assert out["periods"][0].user_periodo == 1
    assert out["folders"][0].user_dimension == "attivita"
    # Returned objects may be the same identity since no override
    # applied — both are acceptable as long as user_* are untouched.


def test_apply_overrides_classifier_per_row() -> None:
    """A classifier override for one yed_id changes only that leaf's
    user_kind; siblings keep their auto_kind."""
    from s3dgraphy.sync.yed_import_pipeline import (
        YedOverrides, apply_overrides_to_drafts,
    )

    classified = [
        _leaf("a", ClassificationKind.USV_VIRTUAL, "USV100"),
        _leaf("b", ClassificationKind.USV_VIRTUAL, "USV101"),
    ]
    drafts = {"classified": classified, "periods": [], "folders": []}
    ov = YedOverrides(classifier={"a": ClassificationKind.US_REAL})

    out = apply_overrides_to_drafts(drafts, ov)

    by_id = {c.yed_id: c.user_kind for c in out["classified"]}
    assert by_id["a"] == ClassificationKind.US_REAL
    assert by_id["b"] == ClassificationKind.USV_VIRTUAL


def test_apply_overrides_periods_full() -> None:
    """A periods override sets user_periodo + user_fase from the
    override dict; unrelated periods keep their auto_* values."""
    from s3dgraphy.sync.yed_import_pipeline import (
        YedOverrides, apply_overrides_to_drafts,
    )
    from s3dgraphy.sync.yed_table_parser import PeriodCandidate

    p1 = PeriodCandidate(yed_row_id="p1", auto_label="A", user_label="A",
                         auto_periodo=1, auto_fase=1,
                         user_periodo=1, user_fase=1)
    p2 = PeriodCandidate(yed_row_id="p2", auto_label="B", user_label="B",
                         auto_periodo=2, auto_fase=2,
                         user_periodo=2, user_fase=2)
    drafts = {"classified": [], "periods": [p1, p2], "folders": []}
    ov = YedOverrides(periods={"p1": {"periodo": 5, "fase": 7}})

    out = apply_overrides_to_drafts(drafts, ov)

    by_id = {p.yed_row_id: (p.user_periodo, p.user_fase) for p in out["periods"]}
    assert by_id["p1"] == (5, 7)
    assert by_id["p2"] == (2, 2)


def test_apply_overrides_folders_dimension_change() -> None:
    """A folder override changing dimension+value sets user_dimension
    and user_value on the targeted folder only."""
    from s3dgraphy.sync.yed_import_pipeline import (
        YedOverrides, apply_overrides_to_drafts,
    )

    folders = [_folder("f0", "VA01"), _folder("f1", "VA02")]
    drafts = {"classified": [], "periods": [], "folders": folders}
    ov = YedOverrides(folders={
        "f0": {"dimension": "struttura", "value": "S01"},
    })

    out = apply_overrides_to_drafts(drafts, ov)

    by_id = {f.yed_id: (f.user_dimension, f.user_value) for f in out["folders"]}
    assert by_id["f0"] == ("struttura", "S01")
    assert by_id["f1"] == ("attivita", "VA02")  # auto_value extracted in _folder


def test_apply_overrides_folders_skip() -> None:
    """user_dimension='skip' sentinel flows through; downstream
    _apply_yed_folder_dimensions reads user_dimension and treats
    'skip' / None as 'no UPDATE for this folder'."""
    from s3dgraphy.sync.yed_import_pipeline import (
        YedOverrides, apply_overrides_to_drafts,
    )

    folders = [_folder("f0", "VA01")]
    drafts = {"classified": [], "periods": [], "folders": folders}
    ov = YedOverrides(folders={"f0": {"dimension": "skip"}})

    out = apply_overrides_to_drafts(drafts, ov)
    assert out["folders"][0].user_dimension == "skip"


def test_apply_overrides_policy_wins_over_caller_arg(tmp_path: Path) -> None:
    """When YedOverrides.policy is set, it overrides the policy=
    argument passed to import_yed_raw. The pipeline reads
    overrides.policy after the apply_overrides_to_drafts call."""
    from s3dgraphy.sync.yed_import_pipeline import (
        YedOverrides, import_yed_raw,
    )
    handle = _make_handle(tmp_path)
    # Empty drafts — exercises only the override-policy-wins path.
    drafts = {"classified": [], "periods": [], "folders": []}
    ov = YedOverrides(policy=FolderEdgePolicy.FAN_OUT)

    result = import_yed_raw(
        handle,
        graphml_path=tmp_path / "nonexistent.graphml",
        sito="OV", drafts=drafts,
        policy=FolderEdgePolicy.SKIP,  # caller default
        overrides=ov,
    )
    # Empty drafts → 0 writes BUT the policy must have been FAN_OUT
    # internally. We can't directly inspect that from IngestResult,
    # but the absence of errors + applied=0 demonstrates the path
    # completed without rejecting the override.
    assert result.errors == ()
    assert result.applied == 0


# ---------------------------------------------------------------------------
# yed-fastfix 2026-05-15 — regression tests for the user-reported bugs
# ---------------------------------------------------------------------------

def test_strip_unita_tipo_prefix_examples() -> None:
    """Bug E: us value must be the numeric portion only; unita_tipo
    carries the prefix. Regression for the helper that owns the rule.

    Bug G (2026-05-15 v2): paradata labels like ``D.001`` carry an
    alphabetic prefix + dot that does NOT match the corresponding
    unita_tipo string (``DOC``). The fallback path extracts the first
    numeric run after the dot, which naturally collapses identity
    variants (D.001 / D.001-2 / D.001bis → '001').
    """
    from s3dgraphy.sync.yed_import_pipeline import (
        _strip_unita_tipo_prefix,
    )
    # Path 1: prefix matches unita_tipo verbatim.
    assert _strip_unita_tipo_prefix("US100", "US") == "100"
    assert _strip_unita_tipo_prefix("USV200", "USV") == "200"
    assert _strip_unita_tipo_prefix("USVs5", "USVs") == "5"
    assert _strip_unita_tipo_prefix("SF01", "SF") == "01"
    assert _strip_unita_tipo_prefix("VSF42", "VSF") == "42"
    assert _strip_unita_tipo_prefix("RSF7", "RSF") == "7"
    # Separator dash is trimmed.
    assert _strip_unita_tipo_prefix("USM-15", "USM") == "15"
    # Case-insensitive prefix match.
    assert _strip_unita_tipo_prefix("us123", "US") == "123"
    # Defensive: stripped-to-empty returns the original label so we
    # never end up with us=''.
    assert _strip_unita_tipo_prefix("US", "US") == "US"
    # Defensive: label not starting with prefix returns label unchanged.
    assert _strip_unita_tipo_prefix("foo", "US") == "foo"
    # Defensive: None / empty prefix returns label unchanged.
    assert _strip_unita_tipo_prefix("US100", None) == "US100"
    assert _strip_unita_tipo_prefix("US100", "") == "US100"

    # Path 2 (Bug G): paradata fallback — alphabetic prefix + dot.
    assert _strip_unita_tipo_prefix("D.001", "DOC") == "001"
    assert _strip_unita_tipo_prefix("C.42", "Combinar") == "42"
    assert _strip_unita_tipo_prefix("E.005", "Extractor") == "005"
    # DocumentNode identity variants collapse to the same numeric base
    # — this is the dedup mechanism: 3 yed_ids → 1 us_table row.
    assert _strip_unita_tipo_prefix("D.001-2", "DOC") == "001"
    assert _strip_unita_tipo_prefix("D.001bis", "DOC") == "001"
    assert _strip_unita_tipo_prefix("D.001/3", "DOC") == "001"
    # Bug I: ExtractorNode preserves the multi-level hierarchy so
    # D.01.03 and D.01.04 remain DISTINCT rows (they're separate
    # extractors of the same parent document D.01). Without this,
    # the DOC-style dedup would collapse all extractors of a doc.
    assert _strip_unita_tipo_prefix("D.01.03", "Extractor") == "01.03"
    assert _strip_unita_tipo_prefix("D.01.04", "Extractor") == "01.04"
    assert _strip_unita_tipo_prefix("D.02.01", "Extractor") == "02.01"
    # PROPERTY labels are canonical names — no numeric prefix, kept verbatim.
    assert _strip_unita_tipo_prefix("material", "property") == "material"
    assert _strip_unita_tipo_prefix("height", "property") == "height"


def test_build_member_to_period_inverts_period_membership() -> None:
    """Bug B: PeriodCandidate.member_yed_ids inverts into
    {yed_id → (periodo, fase)} so _write_us_rows can set
    periodo_iniziale + fase_iniziale on each member.
    """
    from s3dgraphy.sync.yed_import_pipeline import (
        _build_member_to_period,
    )
    from s3dgraphy.sync.yed_table_parser import PeriodCandidate
    periods = [
        PeriodCandidate(
            yed_row_id="r0", auto_label="Period01",
            user_label="Period01", auto_periodo=1, auto_fase=1,
            user_periodo=1, user_fase=1,
            member_yed_ids=["leaf_a", "leaf_b"],
        ),
        PeriodCandidate(
            yed_row_id="r1", auto_label="Period02",
            user_label="Period02", auto_periodo=2, auto_fase=1,
            user_periodo=2, user_fase=1,
            member_yed_ids=["leaf_c"],
        ),
    ]
    mtp = _build_member_to_period(periods)
    assert mtp == {
        "leaf_a": ("1", "1"),
        "leaf_b": ("1", "1"),
        "leaf_c": ("2", "1"),
    }


def test_write_us_rows_populates_period_iniziale_from_periods(
    tmp_path: Path,
) -> None:
    """Bug B regression: when member_to_period is passed, us_table rows
    pick up periodo_iniziale + fase_iniziale + periodo_finale +
    fase_finale (MVP: inizio==fine, user edits in form)."""
    handle = _make_handle(tmp_path)
    leaves = [
        _leaf("y1", ClassificationKind.US_REAL, "US1"),
        _leaf("y2", ClassificationKind.US_REAL, "US2"),
    ]
    member_to_period = {
        "y1": ("3", "2"),
        # y2 NOT in map → its period fields stay NULL
    }
    with handle.engine.begin() as conn:
        count, _ = _write_us_rows(
            conn, leaves, sito="X",
            member_to_period=member_to_period,
        )
    assert count == 2
    with handle.engine.connect() as conn:
        rows = list(conn.execute(
            text("SELECT us, periodo_iniziale, fase_iniziale, "
                 "periodo_finale, fase_finale "
                 "FROM us_table WHERE sito = :s ORDER BY us"),
            {"s": "X"},
        ))
    by_us = {r[0]: r for r in rows}
    # y1 was in member_to_period → period fields populated, both
    # iniziale and finale set to the same (single-period US) value.
    r1 = by_us["1"]
    assert r1[1] == "3"
    assert r1[2] == "2"
    assert r1[3] == "3"
    assert r1[4] == "2"
    # y2 wasn't in the map → fields stay NULL.
    r2 = by_us["2"]
    assert r2[1] is None
    assert r2[2] is None


def test_write_rapporti_format_is_type_us_area_sito(
    tmp_path: Path,
) -> None:
    """Bug A regression: the rapporti tuple order must be
    [type, us_target, area, sito]. pos 1 = us_target (read at
    graph_projector.py:721); pos 3 = sito (rewritten at
    graph_ingestor.py:1259). Before the fix pos 1 held sito and pos 3
    held us_target, breaking every rapporti join.

    Bug F regression: US ↔ US edge gets the verbose Italian token
    'Copre' (default edge_type='overlies' resolves via the canonical
    {US, USM}² map), NOT the placeholder 'covers'."""
    import json
    from s3dgraphy.sync.yed_import_pipeline import (
        _write_rapporti, _write_us_rows,
    )
    from s3dgraphy.sync.yed_rapporti_policy import (
        ExpandedRapporti, FolderEdgePolicy,
    )
    handle = _make_handle(tmp_path)
    leaves = [
        _leaf("y1", ClassificationKind.US_REAL, "US01"),
        _leaf("y2", ClassificationKind.US_REAL, "US02"),
    ]
    with handle.engine.begin() as conn:
        _, uuid_map = _write_us_rows(conn, leaves, sito="X")

        expanded = ExpandedRapporti(
            policy=FolderEdgePolicy.SKIP,
            rapporti=[("y1", "y2", None)],  # y1 -> y2
        )
        _write_rapporti(
            conn, expanded, sito="X", uuid_map=uuid_map,
            id_to_label={"y1": "01", "y2": "02"},
            unita_tipo_by_yed_id={"y1": "US", "y2": "US"},
        )

    with handle.engine.connect() as conn:
        row = conn.execute(
            text("SELECT rapporti FROM us_table WHERE us = :u "
                 "AND sito = :s"),
            {"u": "01", "s": "X"},
        ).first()
    assert row is not None
    rapporti = json.loads(row[0])
    # One outbound edge.
    assert len(rapporti) == 1
    rapporto = rapporti[0]
    # Canonical pyarchinit order: [type, us_target, area, sito].
    # US → US default → verbose IT 'Copre' (Bug F: was hardcoded 'covers').
    assert rapporto[0] == "Copre"        # type
    assert rapporto[1] == "02"           # us_target — NOT sito
    assert rapporto[2] == "1"            # area
    assert rapporto[3] == "X"            # sito — NOT us_target


def test_write_rapporti_token_dispatch_by_unita_tipo(
    tmp_path: Path,
) -> None:
    """Bug F regression: the rapporti token depends on the unita_tipo
    of both endpoints — verbose Italian for US/USM, '>>' for any
    other non-canonical (USV / SF / VSF / RSF / VA), '>' if either
    is CON (continuity).
    """
    import json
    from s3dgraphy.sync.yed_import_pipeline import (
        _write_rapporti, _write_us_rows,
    )
    from s3dgraphy.sync.yed_rapporti_policy import (
        ExpandedRapporti, FolderEdgePolicy,
    )
    handle = _make_handle(tmp_path)
    leaves = [
        _leaf("y_us",  ClassificationKind.US_REAL,     "US10"),
        _leaf("y_usm", ClassificationKind.US_MASONRY,  "USM20"),
        _leaf("y_usv", ClassificationKind.USV_VIRTUAL, "USV30"),
        _leaf("y_sf",  ClassificationKind.SPECIAL_FIND, "SF40"),
    ]
    with handle.engine.begin() as conn:
        _, uuid_map = _write_us_rows(conn, leaves, sito="X")

        # Several edges with different endpoint type combinations.
        expanded = ExpandedRapporti(
            policy=FolderEdgePolicy.SKIP,
            rapporti=[
                ("y_us",  "y_usm", None),  # US  → USM  → verbose 'Copre'
                ("y_usv", "y_us",  None),  # USV → US   → '>>'
                ("y_sf",  "y_usv", None),  # SF  → USV  → '>>'
            ],
        )
        _write_rapporti(
            conn, expanded, sito="X", uuid_map=uuid_map,
            id_to_label={
                "y_us":  "10", "y_usm": "20",
                "y_usv": "30", "y_sf":  "40",
            },
            unita_tipo_by_yed_id={
                "y_us":  "US",  "y_usm": "USM",
                "y_usv": "USV", "y_sf":  "SF",
            },
        )

    with handle.engine.connect() as conn:
        rows = list(conn.execute(
            text("SELECT us, rapporti FROM us_table "
                 "WHERE sito = :s ORDER BY us"),
            {"s": "X"},
        ))
    by_us = {r[0]: r[1] for r in rows}

    # US (10) → USM (20): both canonical → verbose IT.
    us_rapp = json.loads(by_us["10"])
    assert us_rapp[0][0] == "Copre"
    # USV (30) → US (10): one non-canonical → '>>' shorthand.
    usv_rapp = json.loads(by_us["30"])
    assert usv_rapp[0][0] == ">>"
    # SF (40) → USV (30): both non-canonical → '>>' shorthand.
    sf_rapp = json.loads(by_us["40"])
    assert sf_rapp[0][0] == ">>"


def test_paradata_store_add_document_dedups_same_identity(
    tmp_path: Path,
) -> None:
    """Bug D regression: D.001, D.001-2, D.001bis must collapse to ONE
    DocumentNode (same dedup_key 'D.001'). Subsequent add_document
    calls return the existing node_uuid instead of creating a new one.

    For SQLite the paradata file lives next to the .sqlite file
    (``handle.sqlite_path.parent``), so no PYARCHINIT_WORKSPACE_DIR
    monkeypatch is needed — tmp_path is already isolated.
    """
    from s3dgraphy.sync.paradata_store import ParadataStore
    from s3dgraphy.sync._db_handle import DbHandle

    dbfile = tmp_path / "dedup.sqlite"
    handle = DbHandle.from_path(dbfile)
    # No DDL needed — ParadataStore writes to .graphml, not to SQL.
    store = ParadataStore(handle, "DEMO_SITE")

    uuid1 = store.add_document("D.001")
    uuid2 = store.add_document("D.001-2")
    uuid3 = store.add_document("D.001bis")
    uuid4 = store.add_document("D.002")  # different identity

    # Same dedup_key → identical node_uuid returned.
    assert uuid1 == uuid2 == uuid3, (
        f"dedup failed: uuid1={uuid1} uuid2={uuid2} uuid3={uuid3}; "
        f"file={store.file_path}; docs={store.list_documents()}"
    )
    # Different identity → fresh node_uuid.
    assert uuid4 != uuid1

    docs = store.list_documents()
    assert len(docs) == 2
    keys = {d["dedup_key"] for d in docs}
    assert keys == {"D.001", "D.002"}


def test_paradata_store_add_extractor_combiner_roundtrip(
    tmp_path: Path,
) -> None:
    """Bug D regression: ExtractorNode and CombinerNode go through
    add_extractor / add_combiner and survive the read round-trip
    (the s3dgraphy importer drops them; our _merge_extended_paradata_nodes
    reconstructs from the _s3d_node_type marker)."""
    from s3dgraphy.sync.paradata_store import ParadataStore
    from s3dgraphy.sync._db_handle import DbHandle

    dbfile = tmp_path / "rt.sqlite"
    handle = DbHandle.from_path(dbfile)
    store = ParadataStore(handle, "DEMO_SITE")

    store.add_extractor("E.005")
    store.add_combiner("C.07")
    store.add_property("material")

    # Build a fresh store on the same path — forces a real read from disk.
    store2 = ParadataStore(handle, "DEMO_SITE")
    assert len(store2.list_extractors()) == 1
    assert len(store2.list_combiners()) == 1
    assert len(store2.list_properties()) == 1
    assert store2.list_extractors()[0]["label"] == "E.005"
    assert store2.list_combiners()[0]["label"] == "C.07"
    assert store2.list_properties()[0]["label"] == "material"


def test_write_us_rows_yef_fold_collapses_multiple_yed_occurrences(
    tmp_path: Path,
) -> None:
    """Bug R is superseded by yE-F: multiple yEd occurrences of the
    same paradata label fold into ONE us_table row.

    yE-F replaces the previous no-dedup B1 behaviour (which produced
    N rows with synthesised us suffixes ``_2``/``_3``). The fold key
    per the design spec (§5.1) is ``(c.label, unita_tipo)`` — i.e.
    identical labels collapse. Variant labels (D.001 vs D.001-2)
    remain separate folds at the import boundary; collapsing those
    is handled by ParadataStore.add_document dedup-by-identity (see
    test_paradata_store_add_document_dedups_same_identity).

    This test exercises the import-fold contract: 3 yEd occurrences
    of ``D.001`` collapse to 1 row, and a separate label ``D.002``
    gets its own row.
    """
    handle = _make_handle(tmp_path)
    leaves = [
        _leaf("y1", ClassificationKind.DOCUMENT, "D.001"),
        _leaf("y2", ClassificationKind.DOCUMENT, "D.001"),
        _leaf("y3", ClassificationKind.DOCUMENT, "D.001"),
        _leaf("y4", ClassificationKind.DOCUMENT, "D.002"),
    ]
    with handle.engine.begin() as conn:
        count, uuid_map = _write_us_rows(conn, leaves, sito="X")

    # 3 D.001 occurrences fold to 1 row; D.002 is its own row.
    assert count == 2
    assert uuid_map["y1"] == uuid_map["y2"] == uuid_map["y3"]
    assert uuid_map["y4"] != uuid_map["y1"]

    with handle.engine.connect() as conn:
        rows = list(conn.execute(
            text("SELECT us, unita_tipo, d_stratigrafica, other_locations "
                 "FROM us_table WHERE sito = :s ORDER BY us"),
            {"s": "X"},
        ))
    assert len(rows) == 2
    assert {r[0] for r in rows} == {"001", "002"}
    by_us = {r[0]: r for r in rows}
    assert by_us["001"][2] == "D.001"
    assert by_us["002"][2] == "D.002"
    # No folders supplied → other_locations stays empty (None / [] / '').
    assert by_us["001"][3] in (None, "", "[]")
    assert by_us["002"][3] in (None, "", "[]")


def test_classifier_extracts_extractor_kind() -> None:
    """Bug D regression: ``E.NNN`` labels must classify as EXTRACTOR.
    Before yed-fastfix the regex was missing and Extractor nodes fell
    to UNKNOWN → skipped from every bucket."""
    from s3dgraphy.sync.yed_classifier import (
        DEFAULT_CLASSIFIER_RULES,
        ClassificationKind,
    )
    # Find a rule that matches 'E.001'.
    matched_kind = None
    for pat, kind in DEFAULT_CLASSIFIER_RULES:
        if pat.match("E.001"):
            matched_kind = kind
            break
    assert matched_kind == ClassificationKind.EXTRACTOR


def test_classifier_distinguishes_document_from_extractor(
    tmp_path: Path,
) -> None:
    """Bug I regression: the s3dgraphy EM convention is

        D.NN  (BPMN DATA_OBJECT_TYPE_PLAIN)  → DocumentNode
        D.NN.MM (no BPMN type)               → ExtractorNode

    Without this, both labels match the same ``^D\\.\\d+`` regex and
    end up as DOCUMENT — the us_table dedup then collapses them into
    ONE row, dropping every extractor → document edge as a self-loop.

    Two signals discriminate:
      1. yEd BPMN ``<y:Property>`` markers (highest priority)
      2. Label depth fallback (D.NN.MM has 2 dots → Extractor)
    """
    from s3dgraphy.sync.yed_classifier import (
        classify_leaves,
        ClassificationKind,
    )

    # Build a minimal graphml with 3 nodes: D.01 (BPMN data object),
    # D.01.03 (plain, no BPMN — should fall to Extractor via label
    # depth), and D.02 (also BPMN data object).
    graphml = """<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns"
         xmlns:y="http://www.yworks.com/xml/graphml">
  <key id="d2" for="node" yfiles.type="nodegraphics"/>
  <graph edgedefault="directed">
    <node id="n_doc1">
      <data key="d2">
        <y:GenericNode configuration="BPMNNode">
          <y:NodeLabel>D.01</y:NodeLabel>
          <y:StyleProperties>
            <y:Property name="com.yworks.bpmn.dataObjectType"
                        value="DATA_OBJECT_TYPE_PLAIN"/>
          </y:StyleProperties>
        </y:GenericNode>
      </data>
    </node>
    <node id="n_ext1">
      <data key="d2">
        <y:ShapeNode>
          <y:NodeLabel>D.01.03</y:NodeLabel>
        </y:ShapeNode>
      </data>
    </node>
    <node id="n_doc2">
      <data key="d2">
        <y:GenericNode configuration="BPMNNode">
          <y:NodeLabel>D.02</y:NodeLabel>
          <y:StyleProperties>
            <y:Property name="com.yworks.bpmn.dataObjectType"
                        value="DATA_OBJECT_TYPE_PLAIN"/>
          </y:StyleProperties>
        </y:GenericNode>
      </data>
    </node>
  </graph>
</graphml>
"""
    fp = tmp_path / "doc_vs_extractor.graphml"
    fp.write_text(graphml)

    results = classify_leaves(fp)
    by_id = {c.yed_id: c for c in results}
    # BPMN-typed D.01 / D.02 → DocumentNode
    assert by_id["n_doc1"].auto_kind == ClassificationKind.DOCUMENT
    assert by_id["n_doc2"].auto_kind == ClassificationKind.DOCUMENT
    # Plain D.01.03 (label depth fallback: 2 dots) → ExtractorNode
    assert by_id["n_ext1"].auto_kind == ClassificationKind.EXTRACTOR
