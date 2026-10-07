"""L1: group folders in an imported file → SQL state.

Pins D5 (configurable, default safe) + AC-12 + AC-13 + AC-14.

A4 (spec 2026-10-07): the GraphML writer retired, but foldered files
still reach the one-time import — from yEd and from old exports — so
the tests fabricate the foldered GraphML directly: pyarchinit.* <key>
declarations, yfiles.foldertype="group" folders carrying the group
kind/name, members identified by pyarchinit.node_uuid. That is exactly
the surface _apply_group_folders_to_sql reads."""
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


def _uuids_by_struttura(db, sito):
    conn = sqlite3.connect(db)
    rows = list(conn.execute(
        "SELECT node_uuid, struttura FROM us_table WHERE sito=?", (sito,)))
    conn.close()
    out: dict = {}
    for uuid, s in rows:
        out.setdefault(s or "", []).append(uuid)
    return out


def _write_foldered_graphml(path, sito, folders):
    """A minimal pyarchinit-projected file with group folders.

    *folders* = [(kind_or_None, name, [member node_uuids])] — kind None
    means an ad-hoc folder with only a label (no SQL-backed data key).
    """
    G = "http://graphml.graphdrawing.org/xmlns"
    Y = "http://www.yworks.com/xml/graphml"
    root = ET.Element(f"{{{G}}}graphml", nsmap={None: G, "y": Y})
    keys = {}
    for i, attr in enumerate(
            ["node_uuid", "us", "area", "sito",
             "struttura", "attivita"]):
        k = ET.SubElement(root, f"{{{G}}}key")
        k.set("id", "d%d" % i)
        k.set("for", "node")
        k.set("attr.name", "pyarchinit." + attr)
        k.set("attr.type", "string")
        keys[attr] = "d%d" % i
    g = ET.SubElement(root, f"{{{G}}}graph")
    g.set("edgedefault", "directed")
    for fi, (kind, name, members) in enumerate(folders):
        folder = ET.SubElement(g, f"{{{G}}}node")
        folder.set("id", "grp_%d" % fi)
        folder.set("yfiles.foldertype", "group")
        if kind is not None:
            d = ET.SubElement(folder, f"{{{G}}}data")
            d.set("key", keys[kind])
            d.text = name
        gn = ET.SubElement(
            ET.SubElement(folder, f"{{{G}}}data"), f"{{{Y}}}GroupNode")
        nl = ET.SubElement(gn, f"{{{Y}}}NodeLabel")
        nl.text = name
        inner = ET.SubElement(folder, f"{{{G}}}graph")
        inner.set("edgedefault", "directed")
        for mi, uuid in enumerate(members):
            m = ET.SubElement(inner, f"{{{G}}}node")
            m.set("id", "grp_%d::n%d" % (fi, mi))
            d = ET.SubElement(m, f"{{{G}}}data")
            d.set("key", keys["node_uuid"])
            d.text = uuid
    ET.ElementTree(root).write(str(path), encoding="UTF-8",
                               xml_declaration=True)
    return path


def test_default_no_sql_update_on_import(mini_volterra, tmp_path):
    """AC-12: default safe — no SQL update even when folders in import."""
    from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor
    sito = _read_sito(mini_volterra)
    _seed(mini_volterra, sito, "struttura", "basilica", 3)
    by = _uuids_by_struttura(mini_volterra, sito)
    # A folder that WOULD move every basilica US to "chiesa"...
    out = _write_foldered_graphml(
        tmp_path / "out.graphml", sito,
        [("struttura", "chiesa", by.get("basilica", []))])

    rows_before = _select_struttura_rows(mini_volterra, sito)
    # ...imported with the default flag (False)
    GraphIngestor().populate_list(
        out, db_path=mini_volterra, sito=sito)
    rows_after = _select_struttura_rows(mini_volterra, sito)
    assert rows_before == rows_after  # SQL untouched


def test_sql_update_when_flag_enabled(mini_volterra, tmp_path):
    """AC-13: flag-on, a US sits in a different group's folder in the
    imported file → SQL UPDATE applied."""
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

    by = _uuids_by_struttura(mini_volterra, sito)
    basilica = by.get("basilica", [])
    chiesa = by.get("chiesa", [])
    # The file moves one US from basilica into chiesa's folder.
    out = _write_foldered_graphml(
        tmp_path / "out.graphml", sito,
        [("struttura", "basilica", basilica[1:]),
         ("struttura", "chiesa", chiesa + basilica[:1])])

    # Import with flag ON
    result = GraphIngestor().populate_list(
        out, db_path=mini_volterra, sito=sito,
        sql_apply_groups=True)
    assert result.applied >= 1  # at least one UPDATE
    rows_after = _select_struttura_rows(mini_volterra, sito)
    basilica_count = sum(1 for _, s in rows_after if s == "basilica")
    chiesa_count = sum(1 for _, s in rows_after if s == "chiesa")
    assert basilica_count == 1  # was 2, now 1
    assert chiesa_count >= 2     # was 1, now 2


def test_adhoc_groups_never_touch_sql(mini_volterra, tmp_path):
    """AC-14: an ad-hoc folder (label only, no SQL-backed kind) never
    triggers SQL UPDATE even with the flag on."""
    from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor
    sito = _read_sito(mini_volterra)
    conn = sqlite3.connect(mini_volterra)
    us_row = conn.execute(
        "SELECT node_uuid FROM us_table WHERE sito=? LIMIT 1",
        (sito,)).fetchone()
    conn.close()

    out = _write_foldered_graphml(
        tmp_path / "out.graphml", sito,
        [(None, "restauri-2023", [us_row[0]])])

    rows_before = _select_struttura_rows(mini_volterra, sito)
    GraphIngestor().populate_list(
        out, db_path=mini_volterra, sito=sito,
        sql_apply_groups=True)
    rows_after = _select_struttura_rows(mini_volterra, sito)
    assert rows_before == rows_after
