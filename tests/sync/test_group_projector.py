"""L1 fixture-based tests for group_projector.

Pins decisions D1 (all 7 dims), D2 (preselect populated), D4
(ActivityNodeGroup + group_kind), AC-7 (deterministic UUID5).
"""
from __future__ import annotations
import shutil
import sqlite3
import sys
from pathlib import Path

import pytest
import pandas  # noqa: F401
from lxml import etree as _e  # noqa: F401
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
    add_columns(dst); backfill_uuids(dst)
    return dst


def _read_sito(db):
    conn = sqlite3.connect(db)
    s = conn.execute(
        "SELECT DISTINCT sito FROM us_table LIMIT 1").fetchone()[0]
    conn.close()
    return s


def _seed_dimension(db, sito, col, value, n_rows=2):
    """Set us_table.<col>=value for the first n_rows of sito."""
    conn = sqlite3.connect(db)
    rows = list(conn.execute(
        "SELECT id_us FROM us_table WHERE sito=? LIMIT ?",
        (sito, n_rows)))
    for (id_us,) in rows:
        conn.execute(
            f"UPDATE us_table SET {col}=? WHERE id_us=?",
            (value, id_us))
    conn.commit()
    conn.close()


def test_dimensions_with_data_returns_only_populated(mini_volterra):
    """D2: only the dimensions with at least 1 non-empty value."""
    from modules.s3dgraphy.sync.group_projector import dimensions_with_data
    sito = _read_sito(mini_volterra)
    # Mini volterra fixture is mostly empty for grouping cols.
    # Seed: struttura on 2 rows, leave rest empty.
    _seed_dimension(mini_volterra, sito, "struttura", "basilica", 2)
    found = dimensions_with_data(mini_volterra, sito)
    assert "struttura" in found
    # Ambient/saggio/quad_par must NOT appear (empty)
    assert "ambient" not in found
    assert "saggio" not in found
    assert "quad_par" not in found


def test_dimensions_with_data_empty_for_unpopulated_sito(mini_volterra):
    """All dimensions empty → empty list."""
    from modules.s3dgraphy.sync.group_projector import dimensions_with_data
    # Ensure all grouping cols are empty (default fixture state)
    conn = sqlite3.connect(mini_volterra)
    for col in ("area", "struttura", "attivita", "settore",
                "ambient", "saggio", "quad_par"):
        conn.execute(
            f"UPDATE us_table SET {col}=NULL WHERE sito=?",
            (_read_sito(mini_volterra),))
    conn.commit()
    conn.close()

    sito = _read_sito(mini_volterra)
    found = dimensions_with_data(mini_volterra, sito)
    assert found == []


def test_build_groups_handles_all_seven_dimensions(mini_volterra):
    """D1: every one of the 7 dims must be a valid input."""
    from modules.s3dgraphy.sync.group_projector import build_groups_from_sql
    sito = _read_sito(mini_volterra)
    # Seed at least one row per dimension
    for col, val in [("area", "A1"), ("struttura", "basilica"),
                      ("attivita", "1"), ("settore", "N"),
                      ("ambient", "stanza-1"), ("saggio", "S1"),
                      ("quad_par", "Q1")]:
        _seed_dimension(mini_volterra, sito, col, val, 1)
    specs = build_groups_from_sql(
        mini_volterra, sito,
        dimensions=["area", "struttura", "attivita", "settore",
                    "ambient", "saggio", "quad_par"])
    kinds = {s.group_kind for s in specs}
    # All 7 dimensions produced at least one GroupSpec
    assert kinds == {"area", "struttura", "attivita", "settore",
                     "ambient", "saggio", "quad_par"}


def test_build_groups_skips_unknown_dimension(mini_volterra):
    """Unknown dim name (typo) is silently dropped, no exception."""
    from modules.s3dgraphy.sync.group_projector import build_groups_from_sql
    sito = _read_sito(mini_volterra)
    _seed_dimension(mini_volterra, sito, "struttura", "basilica", 2)
    specs = build_groups_from_sql(
        mini_volterra, sito,
        dimensions=["struttura", "bogus_dimension"])
    assert all(s.group_kind == "struttura" for s in specs)


def test_group_uuid_deterministic_across_exports(mini_volterra):
    """AC-7: SQL-derived UUID5 stable across exports."""
    from modules.s3dgraphy.sync.group_projector import build_groups_from_sql
    sito = _read_sito(mini_volterra)
    _seed_dimension(mini_volterra, sito, "struttura", "basilica", 3)
    specs1 = build_groups_from_sql(
        mini_volterra, sito, dimensions=["struttura"])
    specs2 = build_groups_from_sql(
        mini_volterra, sito, dimensions=["struttura"])
    assert {s.group_uuid for s in specs1} == {s.group_uuid for s in specs2}


def test_build_groups_collects_member_us_uuids(mini_volterra):
    """Each GroupSpec.member_us_uuids has the node_uuid (Phase 1
    UUID) of every US in that group."""
    from modules.s3dgraphy.sync.group_projector import build_groups_from_sql
    sito = _read_sito(mini_volterra)
    _seed_dimension(mini_volterra, sito, "struttura", "basilica", 3)
    specs = build_groups_from_sql(
        mini_volterra, sito, dimensions=["struttura"])
    basilica = next(s for s in specs if s.name == "basilica")
    assert len(basilica.member_us_uuids) == 3
    # All UUIDs should be non-empty Phase 1 node_uuid values
    assert all(isinstance(u, str) and len(u) >= 32
               for u in basilica.member_us_uuids)
