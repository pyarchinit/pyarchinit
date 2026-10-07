"""yE-C Parsers: L0 unit tests for extract_periods().

Verifies TableNode detection, row-ordinal numbering, Y-coordinate
membership, header exclusion, empty-label placeholder, empty result
on no TableNode. Each test builds a synthetic graphml in tmp_path.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from s3dgraphy.sync.yed_table_parser import (
    PeriodCandidate,
    extract_periods,
)


def _make_table_graphml(
    tmp_path: Path,
    rows: list[tuple[str, str, float]],  # (row_id, label, height)
    leaves: list[tuple[str, float]],     # (yed_id, y_coord)
    table_y: float = 0.0,
    header_height: float = 30.0,
) -> Path:
    """Build a synthetic graphml with a TableNode + rows + leaves."""
    row_label_xml = ""
    row_geom_xml = ""
    for rid, label, height in rows:
        row_label_xml += (
            f'<y:NodeLabel>{label}'
            f'<y:LabelModel><y:RowNodeLabelModel offset="3.0"/></y:LabelModel>'
            f'<y:ModelParameter>'
            f'<y:RowNodeLabelModelParameter id="{rid}" inside="true"/>'
            f'</y:ModelParameter>'
            f'</y:NodeLabel>'
        )
        row_geom_xml += f'<y:Row id="{rid}" height="{height}"/>'

    leaf_xml = ""
    for nid, y in leaves:
        leaf_xml += (
            f'<node id="{nid}">'
            f'<data key="d6"><y:ShapeNode>'
            f'<y:Geometry height="40.0" width="80.0" x="50.0" y="{y}"/>'
            f'<y:NodeLabel>{nid}</y:NodeLabel>'
            f'</y:ShapeNode></data>'
            f'</node>'
        )

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns"
         xmlns:y="http://www.yworks.com/xml/graphml">
  <key for="node" id="d6" yfiles.type="nodegraphics"/>
  <graph edgedefault="directed" id="G">
    <node id="n0" yfiles.foldertype="group">
      <data key="d6">
        <y:TableNode configuration="YED_TABLE_NODE">
          <y:Geometry height="600.0" width="800.0" x="0.0" y="{table_y}"/>
          {row_label_xml}
          <y:Table>
            <y:Insets top="{header_height}"/>
            <y:Rows>{row_geom_xml}</y:Rows>
          </y:Table>
        </y:TableNode>
      </data>
      <graph edgedefault="directed" id="n0:">
        {leaf_xml}
      </graph>
    </node>
  </graph>
</graphml>
"""
    path = tmp_path / "test_table.graphml"
    path.write_text(xml)
    return path


def _make_graphml_no_table(tmp_path: Path) -> Path:
    """Graphml without any TableNode."""
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns"
         xmlns:y="http://www.yworks.com/xml/graphml">
  <key for="node" id="d6" yfiles.type="nodegraphics"/>
  <graph edgedefault="directed" id="G">
    <node id="n0">
      <data key="d6"><y:ShapeNode>
        <y:Geometry height="40.0" width="80.0" x="50.0" y="100.0"/>
        <y:NodeLabel>US01</y:NodeLabel>
      </y:ShapeNode></data>
    </node>
  </graph>
</graphml>
"""
    path = tmp_path / "no_table.graphml"
    path.write_text(xml)
    return path


def test_no_table_node_returns_empty(tmp_path):
    """Graphml without any TableNode -> []."""
    path = _make_graphml_no_table(tmp_path)
    result = extract_periods(path)
    assert result == []


def test_extract_em_demo_02_mini_2_periods():
    """Run on the yE-A reference fixture -> 2 periods (Period01, Period02)."""
    fixture = Path(__file__).parent / "fixtures" / "em_demo_02_mini.graphml"
    result = extract_periods(fixture)
    assert len(result) == 2
    assert result[0].auto_label == "Period01"
    assert result[1].auto_label == "Period02"


def test_period_ordinal_from_row_order(tmp_path):
    """row_0 -> periodo=1, row_1 -> periodo=2, row_2 -> periodo=3."""
    path = _make_table_graphml(
        tmp_path,
        rows=[("row_0", "P1", 100.0), ("row_1", "P2", 100.0),
              ("row_2", "P3", 100.0)],
        leaves=[],
    )
    result = extract_periods(path)
    assert len(result) == 3
    assert result[0].auto_periodo == 1
    assert result[1].auto_periodo == 2
    assert result[2].auto_periodo == 3
    # auto_fase always 1
    assert all(p.auto_fase == 1 for p in result)


def test_member_assignment_by_y_coordinate(tmp_path):
    """Leaves at y=50 and y=150 with rows [0-100) and [100-200) ->
    leaf at 50 in row 0, leaf at 150 in row 1.
    Note: table_y=0, header_height=0 for this test for simple math."""
    path = _make_table_graphml(
        tmp_path,
        rows=[("row_0", "P1", 100.0), ("row_1", "P2", 100.0)],
        leaves=[("L0", 50.0), ("L1", 150.0)],
        table_y=0.0,
        header_height=0.0,
    )
    result = extract_periods(path)
    assert len(result) == 2
    assert "L0" in result[0].member_yed_ids
    assert "L1" in result[1].member_yed_ids


def test_member_assignment_excludes_header_area(tmp_path):
    """Leaf at y=10 with header at [0-30) and row at [30-130) ->
    leaf is in the header area, NOT in any row's member_yed_ids."""
    path = _make_table_graphml(
        tmp_path,
        rows=[("row_0", "P1", 100.0)],
        leaves=[("L_header", 10.0), ("L_row", 50.0)],
        table_y=0.0,
        header_height=30.0,
    )
    result = extract_periods(path)
    assert len(result) == 1
    assert "L_header" not in result[0].member_yed_ids
    assert "L_row" in result[0].member_yed_ids


def test_empty_row_label_uses_placeholder(tmp_path):
    """A row with empty <NodeLabel> -> auto_label = 'row_{index}'."""
    # We can't easily put an empty NodeLabel via the helper since the
    # helper always inserts the label text. Build raw XML instead.
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns"
         xmlns:y="http://www.yworks.com/xml/graphml">
  <key for="node" id="d6" yfiles.type="nodegraphics"/>
  <graph edgedefault="directed" id="G">
    <node id="n0" yfiles.foldertype="group">
      <data key="d6">
        <y:TableNode configuration="YED_TABLE_NODE">
          <y:Geometry height="200.0" width="800.0" x="0.0" y="0.0"/>
          <y:Table>
            <y:Insets top="0"/>
            <y:Rows>
              <y:Row id="row_0" height="100.0"/>
              <y:Row id="row_1" height="100.0"/>
            </y:Rows>
          </y:Table>
        </y:TableNode>
      </data>
      <graph edgedefault="directed" id="n0:"/>
    </node>
  </graph>
</graphml>
"""
    path = tmp_path / "empty_labels.graphml"
    path.write_text(xml)
    result = extract_periods(path)
    assert len(result) == 2
    assert result[0].auto_label == "row_0"
    assert result[1].auto_label == "row_1"
