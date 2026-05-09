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
    """AC-9: dashed border, NodeLabel top + bg #EBEBEB.

    Note: AI08-F2 replaced the AI06 single-color rendering with a
    per-dimension palette; struttura now uses fill #FFE6CC80 and
    border #C66B33 (D2-C). Label background and geometry remain as
    AI06."""
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
    # AI08-F2: struttura → #FFE6CC80 (pastel-soft orange, 50% alpha)
    assert fill.get("color") == "#FFE6CC80"

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


# ---------------------------------------------------------------------------
# AI08-F2 — Per-dimension visual style
# ---------------------------------------------------------------------------

@pytest.fixture
def expected_palette():
    """The pinned palette from spec §3.1 (D1-A pastel-soft + D2-C 50% alpha)."""
    return {
        "area":      ("#FFE0E680", "#C84A5F"),
        "struttura": ("#FFE6CC80", "#C66B33"),
        "attivita":  ("#FFF5CC80", "#A89A33"),
        "settore":   ("#E6FFCC80", "#6BC633"),
        "ambient":   ("#CCFFE680", "#33A86B"),
        "saggio":    ("#CCF5FF80", "#3389A8"),
        "quad_par":  ("#E0CCFF80", "#6633C6"),
        "adhoc":     ("#F5F5F580", "#666666"),
    }


def _seed_all_dimensions(db, sito):
    """Set us_table.<col>=<value> for one row each of the 7 SQL dimensions.

    The mini_volterra fixture pre-populates `area="1"` on all 5 rows;
    we must clear it first so the per-row seeded values don't collide
    with the attivita="1" label below."""
    conn = sqlite3.connect(db)
    # Clear pre-existing dimension values so each seeded row owns its
    # group label exclusively (no label collisions across group_kinds).
    for col in ("area", "struttura", "attivita",
                "settore", "ambient", "saggio", "quad_par"):
        conn.execute(
            f"UPDATE us_table SET {col}='' WHERE sito=?", (sito,))
    rows = list(conn.execute(
        "SELECT id_us FROM us_table WHERE sito=? LIMIT 7", (sito,)))
    pairs = [
        ("area",      "A1"),
        ("struttura", "basilica"),
        ("attivita",  "1"),
        ("settore",   "N"),
        ("ambient",   "stanza-1"),
        ("saggio",    "S1"),
        ("quad_par",  "Q1"),
    ]
    for (id_us,), (col, val) in zip(rows, pairs):
        conn.execute(
            f"UPDATE us_table SET {col}=? WHERE id_us=?",
            (val, id_us))
    conn.commit()
    conn.close()


def test_per_dimension_fill_color(mini_volterra, tmp_path, expected_palette):
    """AC-1 + AC-4: each rendered group folder's <y:Fill color> matches the
    palette entry for its group_kind, and the alpha suffix is always '80'
    (50% transparency, D2-C)."""
    sito = _read_sito(mini_volterra)
    _seed_all_dimensions(mini_volterra, sito)

    out = tmp_path / "out.graphml"
    _export_with_groups(
        mini_volterra, sito, out,
        ["area", "struttura", "attivita", "settore",
         "ambient", "saggio", "quad_par"])

    tree = ET.parse(str(out))
    folders = [n for n in tree.iter(f"{NS}node")
               if n.get("yfiles.foldertype") == "group"
               and n.get("id", "").startswith("grp_")]
    # mini_volterra has 5 US rows; the zip in _seed_all_dimensions
    # therefore seeds only the first 5 dimensions (area / struttura /
    # attivita / settore / ambient). saggio + quad_par are NOT seeded.
    assert len(folders) >= 5, (
        f"expected >=5 group folders (one per seeded dim), got "
        f"{len(folders)}")

    # For each folder: read <y:NodeLabel> text (group name) and verify
    # its <y:Fill color> matches one of the expected palette entries.
    fills_by_label = {}
    for folder in folders:
        nl = folder.find(f".//{Y}GroupNode/{Y}NodeLabel")
        fill = folder.find(f".//{Y}GroupNode/{Y}Fill")
        assert nl is not None and fill is not None
        fills_by_label[(nl.text or "").strip()] = fill.get("color")

    # Each label maps to a known seeded value; resolve back to dim:
    label_to_dim = {
        "A1":       "area",
        "basilica": "struttura",
        "1":        "attivita",
        "N":        "settore",
        "stanza-1": "ambient",
        "S1":       "saggio",
        "Q1":       "quad_par",
    }
    for label, color in fills_by_label.items():
        dim = label_to_dim.get(label)
        if dim is None:
            continue  # unrelated folder (shouldn't happen)
        expected_fill, _ = expected_palette[dim]
        assert color == expected_fill, (
            f"folder '{label}' (group_kind={dim}): "
            f"expected fill={expected_fill}, got {color}")
        # AC-4: alpha suffix == '80'
        assert color.endswith("80"), (
            f"fill {color} is missing the 50% alpha suffix '80'")


def test_per_dimension_border_color(mini_volterra, tmp_path, expected_palette):
    """AC-2: each rendered group folder's <y:BorderStyle color> matches
    the palette entry for its group_kind."""
    sito = _read_sito(mini_volterra)
    _seed_all_dimensions(mini_volterra, sito)

    out = tmp_path / "out.graphml"
    _export_with_groups(
        mini_volterra, sito, out,
        ["area", "struttura", "attivita", "settore",
         "ambient", "saggio", "quad_par"])

    tree = ET.parse(str(out))
    folders = [n for n in tree.iter(f"{NS}node")
               if n.get("yfiles.foldertype") == "group"
               and n.get("id", "").startswith("grp_")]

    label_to_dim = {
        "A1": "area", "basilica": "struttura", "1": "attivita",
        "N": "settore", "stanza-1": "ambient", "S1": "saggio",
        "Q1": "quad_par",
    }
    for folder in folders:
        nl = folder.find(f".//{Y}GroupNode/{Y}NodeLabel")
        bs = folder.find(f".//{Y}GroupNode/{Y}BorderStyle")
        assert nl is not None and bs is not None
        label = (nl.text or "").strip()
        dim = label_to_dim.get(label)
        if dim is None:
            continue
        _, expected_border = expected_palette[dim]
        assert bs.get("color") == expected_border, (
            f"folder '{label}' (group_kind={dim}): "
            f"expected border={expected_border}, got {bs.get('color')}")
        assert bs.get("type") == "dashed"


def test_unknown_group_kind_falls_back_to_default(mini_volterra, tmp_path):
    """AC-3: a group with an unrecognized group_kind gets the default
    (#F5F5F580 fill + #000000 border). Synthesized via direct call to
    _inject_group_folders with a fake snapshot — bypasses the projector."""
    from modules.s3dgraphy.sync.graphml_writer import (
        _inject_group_folders, _GROUP_KIND_PALETTE,
        _GROUP_DEFAULT_FILL, _GROUP_DEFAULT_BORDER,
    )
    # Sanity: the default values match the spec §3.1
    assert _GROUP_DEFAULT_FILL == "#F5F5F580"
    assert _GROUP_DEFAULT_BORDER == "#000000"
    # And "totally_bogus" is not in the palette
    assert "totally_bogus" not in _GROUP_KIND_PALETTE

    # First do a real export so we have a valid GraphML to inject into
    sito = _read_sito(mini_volterra)
    _seed(mini_volterra, sito, "struttura", "basilica", 3)
    out = tmp_path / "out.graphml"
    _export_with_groups(mini_volterra, sito, out, ["struttura"])

    # Read the EMIDs of 2 strat US already in the output (member candidates)
    tree = ET.parse(str(out))
    NS_local = "{http://graphml.graphdrawing.org/xmlns}"
    Y_local = "{http://www.yworks.com/xml/graphml}"
    emid_kid = None
    for k in tree.getroot().findall(f"{NS_local}key"):
        if k.get("attr.name") == "EMID":
            emid_kid = k.get("id")
            break
    assert emid_kid is not None
    emids = []
    for n in tree.iter(f"{NS_local}node"):
        for d in n.findall(f"{NS_local}data"):
            if d.get("key") == emid_kid and d.text:
                emids.append(d.text.strip())
    candidate_emids = [e for e in emids
                        if not (e or "").startswith("grp_")][:2]
    assert len(candidate_emids) >= 2

    # Build a fake snapshot with an unknown group_kind
    class _FakeNode:
        def __init__(self):
            self.node_id = "test-bogus-uuid"
            self.name = "BogusGroup"
            self.attributes = {
                "group_kind": "totally_bogus",
                "sito":       sito,
                "name":       "BogusGroup",
            }
    fake_snapshot = [_FakeNode()]
    fake_members = {"test-bogus-uuid": candidate_emids}

    # Inject into a fresh copy
    out2 = tmp_path / "out_bogus.graphml"
    import shutil
    shutil.copy2(out, out2)
    # Strip pre-existing grp_* folder so the inject finds clean strat
    tree2 = ET.parse(str(out2))
    parent_of = {c: p for p in tree2.iter() for c in p}
    for f in list(tree2.iter(f"{NS_local}node")):
        if f.get("id", "").startswith("grp_"):
            par = parent_of.get(f)
            if par is not None:
                par.remove(f)
    tree2.write(str(out2), encoding="UTF-8",
                xml_declaration=True, pretty_print=True)

    _inject_group_folders(fake_snapshot, fake_members, out2)

    # Read back the output and verify default colors applied
    tree3 = ET.parse(str(out2))
    bogus_folders = [n for n in tree3.iter(f"{NS_local}node")
                     if n.get("yfiles.foldertype") == "group"
                     and n.get("id", "") == "grp_test-bogus-uuid"]
    assert len(bogus_folders) == 1
    folder = bogus_folders[0]
    fill = folder.find(f".//{Y_local}GroupNode/{Y_local}Fill")
    bs = folder.find(f".//{Y_local}GroupNode/{Y_local}BorderStyle")
    assert fill is not None and bs is not None
    assert fill.get("color") == _GROUP_DEFAULT_FILL
    assert bs.get("color") == _GROUP_DEFAULT_BORDER


def test_locationnodegroup_palette_keyed_by_kind():
    """AI07 A.2: LocationNodeGroup folders pick fill/border from kind enum."""
    from modules.s3dgraphy.sync.graphml_writer import (
        _GROUP_KIND_PALETTE,
        _resolve_group_visual,
    )
    # The 8 existing entries (AI06 + F2) are dimension-keyed.
    assert "struttura" in _GROUP_KIND_PALETTE  # functional
    assert "area" in _GROUP_KIND_PALETTE       # study
    # AI07 also indexes by kind enum value:
    assert "toponym" in _GROUP_KIND_PALETTE
    fill, border = _GROUP_KIND_PALETTE["toponym"]
    assert fill.endswith("80"), f"toponym fill must be 50% alpha, got {fill}"
    # Resolver helper picks dimension first, falls back to kind
    assert _resolve_group_visual(group_kind="struttura", kind="functional") == \
           _GROUP_KIND_PALETTE["struttura"]
    assert _resolve_group_visual(group_kind="<unknown>", kind="toponym") == \
           _GROUP_KIND_PALETTE["toponym"]
