"""D4-B (AC-6): semantic round-trip invariant.

DB → GraphProjector → Graph → GraphIngestor → DB' must preserve
every column in MAPPED_COLUMNS for every row that participates.
Non-mapped columns may differ (UPDATE selettivo never touches them
but in principle the schema is free to add timestamps etc.).
"""
from __future__ import annotations
import shutil
import sqlite3
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
    dst = tmp_path / "mini_volterra.sqlite"
    shutil.copy2(FIXTURE_DB, dst)
    from scripts.migrations._2026_05_node_uuid_backfill_lib import (
        add_columns, backfill_uuids)
    add_columns(dst)
    backfill_uuids(dst)
    return dst


def _read_sito(db):
    conn = sqlite3.connect(db)
    sito = conn.execute(
        "SELECT DISTINCT sito FROM us_table LIMIT 1").fetchone()[0]
    conn.close()
    return sito


def _read_canonical(db, sito):
    """Return rows as a dict keyed by node_uuid → MAPPED_COLUMNS values."""
    from modules.s3dgraphy.sync.graph_ingestor import MAPPED_COLUMNS
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cols = ", ".join(MAPPED_COLUMNS)
    cur.execute(f"SELECT {cols} FROM us_table WHERE sito = ?", (sito,))
    rows = {row[MAPPED_COLUMNS.index("node_uuid")]:
            dict(zip(MAPPED_COLUMNS, row))
            for row in cur.fetchall()}
    conn.close()
    return rows


def test_round_trip_preserves_mapped_fields(tmp_path, mini_volterra):
    """D4-B / AC-6 — DB → Graph → DB' is identity on MAPPED_COLUMNS."""
    sito = _read_sito(mini_volterra)
    before = _read_canonical(mini_volterra, sito)

    from modules.s3dgraphy.sync.graph_projector import GraphProjector
    from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor
    graph = GraphProjector().populate_graph(mini_volterra, sito=sito)

    rt = tmp_path / "rt.sqlite"
    shutil.copy2(mini_volterra, rt)
    GraphIngestor().populate_list(graph, rt, sito=sito, dry_run=False)

    after = _read_canonical(rt, sito)
    assert set(before.keys()) == set(after.keys()), \
        "round-trip lost / gained rows"
    for uuid, before_row in before.items():
        after_row = after[uuid]
        for col in before_row:
            assert before_row[col] == after_row[col], (
                f"round-trip mutated {col} for {uuid}: "
                f"before={before_row[col]!r}, after={after_row[col]!r}")
