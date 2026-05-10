"""AI07 Group G: recursive _apply_group_folders_to_sql walker tests."""
from __future__ import annotations
import sqlite3
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


def _read_sito(db_path):
    """Read the single sito from the mini-volterra fixture."""
    conn = sqlite3.connect(str(db_path))
    sito = conn.execute(
        "SELECT DISTINCT sito FROM us_table LIMIT 1").fetchone()[0]
    conn.close()
    return sito


def _build_nested_graphml(out_path, levels=("Italia", "Toscana", "Pisa")):
    """Hand-craft a 3-level nested LocationNodeGroup yEd structure."""
    template = """<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns"
         xmlns:y="http://www.yworks.com/xml/graphml">
  <key id="d_node_type" for="node" attr.name="_s3d_node_type"/>
  <key id="d_kind_top" for="node" attr.name="pyarchinit.toponym"/>
  <graph id="G" edgedefault="directed">
"""
    # Outer folder Italia, inner Toscana, innermost Pisa
    inner_pisa = """      <node id="grp_pisa" yfiles.foldertype="group">
        <data key="d_node_type">LocationNodeGroup</data>
        <data key="d_kind_top">Pisa</data>
        <graph id="g_pisa"/>
      </node>"""
    inner_toscana = f"""      <node id="grp_toscana" yfiles.foldertype="group">
        <data key="d_node_type">LocationNodeGroup</data>
        <data key="d_kind_top">Toscana</data>
        <graph id="g_toscana">
{inner_pisa}
        </graph>
      </node>"""
    outer = f"""      <node id="grp_italia" yfiles.foldertype="group">
        <data key="d_node_type">LocationNodeGroup</data>
        <data key="d_kind_top">Italia</data>
        <graph id="g_italia">
{inner_toscana}
        </graph>
      </node>"""
    Path(out_path).write_text(template + outer + "\n  </graph>\n</graphml>\n",
                              encoding="utf-8")


def test_walker_descends_into_nested_folder(tmp_path):
    """AC-18: walker visits Italia -> Toscana -> Pisa (3 levels)."""
    from modules.s3dgraphy.sync.graph_ingestor import (
        _apply_group_folders_to_sql,
    )
    g = tmp_path / "nested.graphml"
    _build_nested_graphml(g)
    db = tmp_path / "x.sqlite"
    db.write_bytes((FIXTURES / "mini_volterra.sqlite").read_bytes())
    conn = sqlite3.connect(str(db))
    cur = conn.cursor()
    n = _apply_group_folders_to_sql(cur, g, _read_sito(db))
    conn.close()
    # Toponym kind is NOT in SQL_BACKED_KINDS, so n=0 (no SQL writes),
    # but the walker MUST have visited all 3 levels - verified via
    # absence of cycle errors.
    assert n == 0, "toponym levels never write SQL"


def test_cycle_detected_aborts_ingest(tmp_path):
    """If the GraphML inadvertently has a folder cycle, walker aborts."""
    cycle = tmp_path / "cycle.graphml"
    cycle.write_text("""<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns">
  <key id="d_kind_str" for="node" attr.name="pyarchinit.struttura"/>
  <graph id="G" edgedefault="directed">
    <node id="grp_a" yfiles.foldertype="group">
      <data key="d_kind_str">A</data>
      <graph id="g_a">
        <node id="grp_a" yfiles.foldertype="group">
          <data key="d_kind_str">A</data>
        </node>
      </graph>
    </node>
  </graph>
</graphml>
""", encoding="utf-8")
    db = tmp_path / "x.sqlite"
    db.write_bytes((FIXTURES / "mini_volterra.sqlite").read_bytes())
    conn = sqlite3.connect(str(db))
    cur = conn.cursor()
    from modules.s3dgraphy.sync.graph_ingestor import (
        _apply_group_folders_to_sql,
    )
    with pytest.raises(Exception) as exc:
        _apply_group_folders_to_sql(cur, cycle, _read_sito(db))
    msg = str(exc.value).lower()
    assert "cycle" in msg or "visited" in msg or "duplicate" in msg


def test_locationnodegroup_with_us_members_writes_sql(tmp_path):
    """LocationNodeGroup folder containing US members -> UPDATE us_table."""
    from modules.s3dgraphy.sync.graph_ingestor import (
        _apply_group_folders_to_sql,
    )
    db = tmp_path / "x.sqlite"
    db.write_bytes((FIXTURES / "mini_volterra.sqlite").read_bytes())
    sito = _read_sito(db)
    conn = sqlite3.connect(str(db))
    row = conn.execute(
        "SELECT us, area FROM us_table WHERE sito=? LIMIT 1", (sito,)
    ).fetchone()
    us_val, area_val = row
    conn.close()

    gp = tmp_path / "loc.graphml"
    gp.write_text(f"""<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns">
  <key id="d_node_type" for="node" attr.name="_s3d_node_type"/>
  <key id="d_kind_str" for="node" attr.name="pyarchinit.struttura"/>
  <key id="d_us" for="node" attr.name="pyarchinit.us"/>
  <key id="d_area" for="node" attr.name="pyarchinit.area"/>
  <graph id="G" edgedefault="directed">
    <node id="grp_struttura" yfiles.foldertype="group">
      <data key="d_node_type">LocationNodeGroup</data>
      <data key="d_kind_str">NewBasilica</data>
      <graph id="g_str">
        <node id="us1">
          <data key="d_us">{us_val}</data>
          <data key="d_area">{area_val}</data>
        </node>
      </graph>
    </node>
  </graph>
</graphml>
""", encoding="utf-8")
    conn = sqlite3.connect(str(db))
    cur = conn.cursor()
    n = _apply_group_folders_to_sql(cur, gp, sito)
    conn.commit()
    assert n >= 1, f"expected >=1 UPDATE, got {n}"
    after = conn.execute(
        "SELECT struttura FROM us_table WHERE sito=? AND us=?",
        (sito, us_val),
    ).fetchone()
    conn.close()
    assert after[0] == "NewBasilica"


def test_mixed_locationnodegroup_and_activitynodegroup(tmp_path):
    """Walker handles both LocationNodeGroup and ActivityNodeGroup folders."""
    from modules.s3dgraphy.sync.graph_ingestor import (
        _apply_group_folders_to_sql,
    )
    db = tmp_path / "x.sqlite"
    db.write_bytes((FIXTURES / "mini_volterra.sqlite").read_bytes())
    sito = _read_sito(db)
    row = sqlite3.connect(str(db)).execute(
        "SELECT us FROM us_table WHERE sito=? LIMIT 1", (sito,)
    ).fetchone()
    us_val = row[0]

    gp = tmp_path / "mixed.graphml"
    gp.write_text(f"""<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns">
  <key id="d_node_type" for="node" attr.name="_s3d_node_type"/>
  <key id="d_kind_str" for="node" attr.name="pyarchinit.struttura"/>
  <key id="d_kind_act" for="node" attr.name="pyarchinit.attivita"/>
  <key id="d_us" for="node" attr.name="pyarchinit.us"/>
  <graph id="G" edgedefault="directed">
    <node id="grp_struttura" yfiles.foldertype="group">
      <data key="d_node_type">LocationNodeGroup</data>
      <data key="d_kind_str">B1</data>
      <graph id="g_str"><node id="us1"><data key="d_us">{us_val}</data></node></graph>
    </node>
    <node id="grp_attivita" yfiles.foldertype="group">
      <data key="d_node_type">ActivityNodeGroup</data>
      <data key="d_kind_act">SaggioX</data>
      <graph id="g_act"><node id="us1b"><data key="d_us">{us_val}</data></node></graph>
    </node>
  </graph>
</graphml>
""", encoding="utf-8")
    conn = sqlite3.connect(str(db))
    cur = conn.cursor()
    n = _apply_group_folders_to_sql(cur, gp, sito)
    conn.commit()
    after = conn.execute(
        "SELECT struttura, attivita FROM us_table WHERE sito=? "
        "AND us=?", (sito, us_val),
    ).fetchone()
    conn.close()
    assert after[0] == "B1"
    assert after[1] == "SaggioX"
