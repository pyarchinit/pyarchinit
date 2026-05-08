"""L1 round-trip: groups → re-import → SQL state.

Pins D5 (configurable, default safe) + AC-12 + AC-13 + AC-14."""
from __future__ import annotations
import shutil
import sqlite3
import sys
from pathlib import Path

import pytest
import pandas  # noqa: F401
from lxml import etree as ET
PLUGIN_ROOT = Path(__file__).resolve().parents[2]
_EXT_LIBS = str(PLUGIN_ROOT / "ext_libs")
if _EXT_LIBS in sys.path:
    sys.path.remove(_EXT_LIBS)
sys.path.insert(0, _EXT_LIBS)
for _mod in [m for m in list(sys.modules)
             if m == "s3dgraphy" or m.startswith("s3dgraphy.")]:
    del sys.modules[_mod]

NS = "{http://graphml.graphdrawing.org/xmlns}"
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


def _seed(db, sito, col, value, n=2):
    conn = sqlite3.connect(db)
    rows = list(conn.execute(
        "SELECT id_us FROM us_table WHERE sito=? LIMIT ?", (sito, n)))
    for (id_us,) in rows:
        conn.execute(
            f"UPDATE us_table SET {col}=? WHERE id_us=?",
            (value, id_us))
    conn.commit()
    conn.close()


def _select_struttura_rows(db, sito):
    conn = sqlite3.connect(db)
    rows = list(conn.execute(
        "SELECT id_us, struttura FROM us_table WHERE sito=?", (sito,)))
    conn.close()
    return rows


def test_default_no_sql_update_on_import(mini_volterra, tmp_path):
    """AC-12: default safe — no SQL update even when groups in import."""
    from modules.s3dgraphy.sync.graphml_writer import export_graphml
    from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor
    sito = _read_sito(mini_volterra)
    _seed(mini_volterra, sito, "struttura", "basilica", 3)

    out = tmp_path / "out.graphml"
    export_graphml(db_path=mini_volterra, mapping="pyarchinit_us_mapping",
                   output_path=out, site_filter=sito,
                   groups=["struttura"])

    rows_before = _select_struttura_rows(mini_volterra, sito)
    # Import with default flag (False)
    GraphIngestor().populate_list(
        out, db_path=mini_volterra, sito=sito)
    rows_after = _select_struttura_rows(mini_volterra, sito)
    assert rows_before == rows_after  # SQL untouched


def test_sql_update_when_flag_enabled(mini_volterra, tmp_path):
    """AC-13: flag-on, manually move a US to a different group's
    inner <graph> in the GraphML, re-import → SQL UPDATE applied."""
    from modules.s3dgraphy.sync.graphml_writer import export_graphml
    from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor
    sito = _read_sito(mini_volterra)
    # Seed 2 US in basilica + 1 in chiesa
    _seed(mini_volterra, sito, "struttura", "basilica", 2)
    conn = sqlite3.connect(mini_volterra)
    rows = list(conn.execute(
        "SELECT id_us FROM us_table WHERE sito=? "
        "AND (struttura IS NULL OR struttura='') LIMIT 1", (sito,)))
    if rows:
        conn.execute("UPDATE us_table SET struttura='chiesa' "
                     "WHERE id_us=?", (rows[0][0],))
    conn.commit()
    conn.close()

    out = tmp_path / "out.graphml"
    export_graphml(db_path=mini_volterra, mapping="pyarchinit_us_mapping",
                   output_path=out, site_filter=sito,
                   groups=["struttura"])

    # Manually mutate output: move first US from basilica to chiesa
    tree = ET.parse(str(out))
    root = tree.getroot()
    folders = [n for n in root.iter(f"{NS}node")
               if n.get("yfiles.foldertype") == "group"
               and n.get("id", "").startswith("grp_")]
    # Find label text "basilica" and "chiesa"
    folder_basilica = next(
        f for f in folders
        if any((nl.text or "").strip() == "basilica"
               for nl in f.iter("{http://www.yworks.com/xml/graphml}NodeLabel"))
    )
    folder_chiesa = next(
        f for f in folders
        if any((nl.text or "").strip() == "chiesa"
               for nl in f.iter("{http://www.yworks.com/xml/graphml}NodeLabel"))
    )
    inner_basilica = folder_basilica.find(f"{NS}graph")
    inner_chiesa = folder_chiesa.find(f"{NS}graph")
    # Take 1 US from basilica, move to chiesa
    moving_us = inner_basilica.findall(f"{NS}node")[0]
    inner_basilica.remove(moving_us)
    inner_chiesa.append(moving_us)
    tree.write(str(out), encoding="UTF-8", xml_declaration=True)

    # Import with flag ON
    result = GraphIngestor().populate_list(
        out, db_path=mini_volterra, sito=sito,
        sql_apply_groups=True)
    assert result.applied >= 1  # at least one UPDATE
    # Verify struttura count for basilica decreased
    rows_after = _select_struttura_rows(mini_volterra, sito)
    basilica_count = sum(1 for _, s in rows_after if s == "basilica")
    chiesa_count = sum(1 for _, s in rows_after if s == "chiesa")
    assert basilica_count == 1  # was 2, now 1
    assert chiesa_count >= 2     # was 1, now 2


def test_adhoc_groups_never_touch_sql(mini_volterra, tmp_path):
    """AC-14: ad-hoc group_kind never triggers SQL UPDATE even with
    flag on — only updates GroupStore."""
    from modules.s3dgraphy.sync.graphml_writer import export_graphml
    from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor
    from modules.s3dgraphy.sync.group_store import GroupStore
    sito = _read_sito(mini_volterra)

    # Add 1 ad-hoc group
    store = GroupStore(mini_volterra, sito)
    # Pick a real US to attach
    conn = sqlite3.connect(mini_volterra)
    us_row = conn.execute(
        "SELECT node_uuid FROM us_table WHERE sito=? LIMIT 1",
        (sito,)).fetchone()
    conn.close()
    us_uuid = us_row[0]
    store.add_group("restauri-2023", group_kind="adhoc",
                    member_us_uuids=[us_uuid])

    out = tmp_path / "out.graphml"
    export_graphml(db_path=mini_volterra, mapping="pyarchinit_us_mapping",
                   output_path=out, site_filter=sito,
                   groups=["adhoc"])

    rows_before = _select_struttura_rows(mini_volterra, sito)
    # Import with flag ON — ad-hoc must NOT touch SQL
    GraphIngestor().populate_list(
        out, db_path=mini_volterra, sito=sito,
        sql_apply_groups=True)
    rows_after = _select_struttura_rows(mini_volterra, sito)
    assert rows_before == rows_after
