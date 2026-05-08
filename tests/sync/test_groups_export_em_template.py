"""L4 EM template compliance: structural lxml tests on the GraphML
output, comparing against the EM canonical layout (EM_demo_02.graphml
reference). Pins AC-8, AC-9, AC-10, AC-11."""
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
Y = "{http://www.yworks.com/xml/graphml}"
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


def _export_with_groups(db, sito, out, groups):
    from modules.s3dgraphy.sync.graphml_writer import export_graphml
    export_graphml(
        db_path=db, mapping="pyarchinit_us_mapping",
        output_path=out, site_filter=sito, groups=groups,
    )


def test_group_node_uses_yfiles_foldertype_group(mini_volterra, tmp_path):
    """AC-8: <node yfiles.foldertype='group'> with <y:GroupNode>
    realizer (NOT TableNode — that's the swimlane)."""
    sito = _read_sito(mini_volterra)
    _seed(mini_volterra, sito, "struttura", "basilica", 3)
    out = tmp_path / "out.graphml"
    _export_with_groups(mini_volterra, sito, out, ["struttura"])

    tree = ET.parse(str(out))
    folders = [n for n in tree.iter(f"{NS}node")
               if n.get("yfiles.foldertype") == "group"
               and n.get("id", "").startswith("grp_")]
    assert len(folders) >= 1
    folder = folders[0]
    realizer = folder.find(f".//{Y}GroupNode")
    assert realizer is not None
    table = folder.find(f".//{Y}TableNode")
    assert table is None  # not the swimlane


def test_group_visual_matches_em_template(mini_volterra, tmp_path):
    """AC-9: dashed border, fill #F5F5F5, NodeLabel top + bg #EBEBEB."""
    sito = _read_sito(mini_volterra)
    _seed(mini_volterra, sito, "struttura", "basilica", 3)
    out = tmp_path / "out.graphml"
    _export_with_groups(mini_volterra, sito, out, ["struttura"])

    tree = ET.parse(str(out))
    folder = next(n for n in tree.iter(f"{NS}node")
                  if n.get("yfiles.foldertype") == "group"
                  and n.get("id", "").startswith("grp_"))
    realizer = folder.find(f".//{Y}GroupNode")

    border = realizer.find(f"{Y}BorderStyle")
    assert border.get("type") == "dashed"
    fill = realizer.find(f"{Y}Fill")
    assert fill.get("color") == "#F5F5F5"

    label = realizer.find(f"{Y}NodeLabel")
    assert label.get("backgroundColor") == "#EBEBEB"
    assert label.get("modelPosition") == "t"
    assert (label.text or "").strip() == "basilica"


def test_group_geometry_spans_member_us_bbox(mini_volterra, tmp_path):
    """AC-10: group Geometry contains bbox of all member US."""
    sito = _read_sito(mini_volterra)
    _seed(mini_volterra, sito, "struttura", "basilica", 3)
    out = tmp_path / "out.graphml"
    _export_with_groups(mini_volterra, sito, out, ["struttura"])

    tree = ET.parse(str(out))
    folder = next(n for n in tree.iter(f"{NS}node")
                  if n.get("yfiles.foldertype") == "group"
                  and n.get("id", "").startswith("grp_"))
    g_geom = folder.find(f".//{Y}GroupNode/{Y}Geometry")
    gx, gy = float(g_geom.get("x")), float(g_geom.get("y"))
    gw, gh = float(g_geom.get("width")), float(g_geom.get("height"))

    # Find inner graph + member US Geometries
    inner = folder.find(f"{NS}graph")
    assert inner is not None
    member_geoms = []
    for me in inner.findall(f"{NS}node"):
        ug = me.find(f".//{Y}Geometry")
        if ug is None:
            continue
        member_geoms.append((
            float(ug.get("x")), float(ug.get("y")),
            float(ug.get("width")), float(ug.get("height"))))
    assert member_geoms, "no member US with Geometry"

    min_x = min(g[0] for g in member_geoms)
    min_y = min(g[1] for g in member_geoms)
    max_x = max(g[0] + g[2] for g in member_geoms)
    max_y = max(g[1] + g[3] for g in member_geoms)

    # Group bbox contains member bbox (+ small margin allowed)
    assert gx <= min_x
    assert gy <= min_y
    assert gx + gw >= max_x
    assert gy + gh >= max_y


def test_group_children_are_us_member_nodes(mini_volterra, tmp_path):
    """AC-11: inner <graph> contains exactly the member US nodes."""
    sito = _read_sito(mini_volterra)
    _seed(mini_volterra, sito, "struttura", "basilica", 3)
    out = tmp_path / "out.graphml"
    _export_with_groups(mini_volterra, sito, out, ["struttura"])

    tree = ET.parse(str(out))
    folder = next(n for n in tree.iter(f"{NS}node")
                  if n.get("yfiles.foldertype") == "group"
                  and n.get("id", "").startswith("grp_"))
    inner = folder.find(f"{NS}graph")
    inner_nodes = list(inner.findall(f"{NS}node"))
    # Must be 3 member US nodes (matching the seeded count)
    assert len(inner_nodes) == 3


def test_default_groups_empty_preserves_ac2_baseline(mini_volterra, tmp_path):
    """D7-A: default no-groups export has no grp_* node — preserves
    the AI03 AC-2 baseline byte-identical guarantee structurally."""
    sito = _read_sito(mini_volterra)
    out = tmp_path / "out.graphml"
    _export_with_groups(mini_volterra, sito, out, None)

    tree = ET.parse(str(out))
    folders = [n for n in tree.iter(f"{NS}node")
               if n.get("id", "").startswith("grp_")]
    assert folders == []
