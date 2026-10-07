"""yE-F round-trip integration test.

Imports the shipped ``em_demo_02_mini.graphml`` fixture, snapshots the
``us_table`` state, then re-imports the same drafts with the same
policy and verifies the DB state is byte-identical across the
idempotent cycle.

Sanity-checks paradata rows that have non-empty ``other_locations``:
  * the column is valid JSON
  * it decodes to a list[str]
  * the primary ``attivita`` is NOT in the secondary list

This is the yE-F closure test — the yE-F fold/fan-out logic must be
idempotent: re-importing identical drafts must NOT mutate any row
(no duplicate ``other_locations`` entries, no flipping of primary
``attivita``, no orphan inserts).
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from sqlalchemy import text

from s3dgraphy.sync._db_handle import DbHandle


FIXTURE = (
    Path(__file__).parent / "fixtures" / "em_demo_02_mini.graphml"
)


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


def _make_handle(tmp_path: Path) -> DbHandle:
    """Build a DbHandle on a fresh SQLite + the 3 inline tables."""
    dbfile = tmp_path / "yef_roundtrip.sqlite"
    handle = DbHandle.from_path(dbfile)
    with handle.engine.begin() as conn:
        conn.execute(text(_US_TABLE_DDL))
        conn.execute(text(_INVENTARIO_DDL))
        conn.execute(text(_PERIODIZZAZIONE_DDL))
    return handle


@pytest.fixture
def workspace_env(tmp_path, monkeypatch):
    """Point ParadataStore at an isolated workspace under tmp_path so
    it doesn't try to write into the user's real workspace directory.
    """
    workspace_root = tmp_path / "_workspace"
    workspace_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("PYARCHINIT_WORKSPACE_DIR", str(workspace_root))
    return workspace_root


@pytest.mark.skipif(
    not FIXTURE.exists(),
    reason="em_demo_02_mini.graphml fixture absent",
)
def test_yef_round_trip_em_demo_02_mini(
    tmp_path: Path, workspace_env,
) -> None:
    """Import fixture, snapshot DB, re-import same drafts, assert
    DB state identical (cardinality + other_locations content).

    Also sanity-checks the secondary-locations invariant on any
    paradata row that carries a non-empty ``other_locations``.
    """
    # Import locally so module-load errors don't suppress the skip.
    from s3dgraphy.sync.yed_classifier import classify_leaves
    from s3dgraphy.sync.yed_group_walker import walk_folders
    from s3dgraphy.sync.yed_table_parser import extract_periods
    from s3dgraphy.sync.yed_import_pipeline import import_yed_raw
    from s3dgraphy.sync.yed_rapporti_policy import FolderEdgePolicy

    handle = _make_handle(tmp_path)
    drafts = {
        "classified": classify_leaves(FIXTURE),
        "periods":    extract_periods(FIXTURE),
        "folders":    walk_folders(FIXTURE),
    }

    # ---- First import --------------------------------------------------
    r1 = import_yed_raw(
        handle, FIXTURE, sito="DEMO_SITE", drafts=drafts,
        policy=FolderEdgePolicy.SKIP,
    )
    assert r1.errors == ()

    with handle.engine.connect() as conn:
        rows_1 = list(conn.execute(text(
            "SELECT us, unita_tipo, attivita, other_locations "
            "FROM us_table WHERE sito = 'DEMO_SITE' "
            "ORDER BY unita_tipo, us"
        )))

    # ---- Second import (identical drafts) -----------------------------
    r2 = import_yed_raw(
        handle, FIXTURE, sito="DEMO_SITE", drafts=drafts,
        policy=FolderEdgePolicy.SKIP,
    )
    assert r2.errors == ()

    with handle.engine.connect() as conn:
        rows_2 = list(conn.execute(text(
            "SELECT us, unita_tipo, attivita, other_locations "
            "FROM us_table WHERE sito = 'DEMO_SITE' "
            "ORDER BY unita_tipo, us"
        )))

    # ---- Idempotency assertion ----------------------------------------
    assert rows_1 == rows_2, (
        f"DB state changed between identical imports.\n"
        f"first: {rows_1}\nsecond: {rows_2}"
    )

    # ---- Secondary-locations invariant on paradata rows ---------------
    paradata_with_secondaries = [
        r for r in rows_1
        if r[1] in ("DOC", "Combinar", "Extractor", "property")
        and r[3] and r[3] != "[]"
    ]
    for r in paradata_with_secondaries:
        parsed = json.loads(r[3])
        assert isinstance(parsed, list)
        assert all(isinstance(s, str) for s in parsed)
        # The primary attivita must never appear in other_locations.
        assert r[2] not in parsed, (
            f"primary attivita {r[2]!r} leaked into other_locations "
            f"of row {r!r}"
        )
