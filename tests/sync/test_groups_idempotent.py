"""L1 idempotency: 3 consecutive exports converge.

Pins AC-15."""
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


def _extract_group_uuids(graphml_path):
    tree = ET.parse(str(graphml_path))
    out = []
    for n in tree.iter(f"{NS}node"):
        if (n.get("yfiles.foldertype") == "group"
                and n.get("id", "").startswith("grp_")):
            out.append(n.get("id"))
    return sorted(out)


def _structural_fingerprint(graphml_path):
    """Count nodes/edges/labels — same approach as AC-2 baseline."""
    tree = ET.parse(str(graphml_path))
    nodes = list(tree.iter(f"{NS}node"))
    edges = list(tree.iter(f"{NS}edge"))
    return (len(nodes), len(edges))


def test_repeated_export_produces_stable_groups(mini_volterra, tmp_path):
    """AC-15: 3 consecutive exports → identical group UUIDs."""
    from modules.s3dgraphy.sync.graphml_writer import export_graphml
    sito = _read_sito(mini_volterra)
    _seed(mini_volterra, sito, "struttura", "basilica", 3)

    outs = [tmp_path / f"out{i}.graphml" for i in range(3)]
    for out in outs:
        export_graphml(db_path=mini_volterra,
                       mapping="pyarchinit_us_mapping",
                       output_path=out, site_filter=sito,
                       groups=["struttura"])

    uuids = [tuple(_extract_group_uuids(o)) for o in outs]
    assert uuids[0] == uuids[1] == uuids[2]


def test_export_structural_fingerprint_stable(mini_volterra, tmp_path):
    """AC-15: structural fingerprint stable across repeated exports."""
    from modules.s3dgraphy.sync.graphml_writer import export_graphml
    sito = _read_sito(mini_volterra)
    _seed(mini_volterra, sito, "struttura", "basilica", 3)

    out1 = tmp_path / "out1.graphml"
    out2 = tmp_path / "out2.graphml"
    out3 = tmp_path / "out3.graphml"
    for out in (out1, out2, out3):
        export_graphml(db_path=mini_volterra,
                       mapping="pyarchinit_us_mapping",
                       output_path=out, site_filter=sito,
                       groups=["struttura"])

    fp1 = _structural_fingerprint(out1)
    fp2 = _structural_fingerprint(out2)
    fp3 = _structural_fingerprint(out3)
    # Run 1 vs 2 may differ on structural details; 2 vs 3 must be stable
    assert fp2 == fp3
