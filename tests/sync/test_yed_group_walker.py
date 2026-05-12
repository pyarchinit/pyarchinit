"""yE-C Parsers: L0 unit tests for walk_folders().

Verifies empty result on no folders, mini-fixture detection,
TableNode exclusion, label-description split, unknown prefix
fallback, nested folder membership, cycle detection.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from modules.s3dgraphy.sync.graph_ingestor import CycleDetectedError
from modules.s3dgraphy.sync.yed_group_walker import (
    FolderCandidate,
    walk_folders,
)


def _make_graphml_no_folders(tmp_path: Path) -> Path:
    """Graphml with leaf nodes only, no folders."""
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns"
         xmlns:y="http://www.yworks.com/xml/graphml">
  <key for="node" id="d6" yfiles.type="nodegraphics"/>
  <graph edgedefault="directed" id="G">
    <node id="n0">
      <data key="d6"><y:ShapeNode>
        <y:NodeLabel>US01</y:NodeLabel>
      </y:ShapeNode></data>
    </node>
  </graph>
</graphml>
"""
    path = tmp_path / "no_folders.graphml"
    path.write_text(xml)
    return path


def _make_graphml_one_folder(tmp_path: Path, label: str) -> Path:
    """Graphml with one folder containing one leaf."""
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns"
         xmlns:y="http://www.yworks.com/xml/graphml">
  <key for="node" id="d6" yfiles.type="nodegraphics"/>
  <graph edgedefault="directed" id="G">
    <node id="n0" yfiles.foldertype="group">
      <data key="d6">
        <y:ProxyAutoBoundsNode>
          <y:Realizers active="0">
            <y:GroupNode>
              <y:NodeLabel>{label}</y:NodeLabel>
            </y:GroupNode>
          </y:Realizers>
        </y:ProxyAutoBoundsNode>
      </data>
      <graph edgedefault="directed" id="n0:">
        <node id="n0::n0">
          <data key="d6"><y:ShapeNode><y:NodeLabel>X</y:NodeLabel></y:ShapeNode></data>
        </node>
      </graph>
    </node>
  </graph>
</graphml>
"""
    path = tmp_path / "one_folder.graphml"
    path.write_text(xml)
    return path


def test_no_folders_returns_empty(tmp_path):
    """Graphml without any folders -> []."""
    path = _make_graphml_no_folders(tmp_path)
    result = walk_folders(path)
    assert result == []


def test_walk_em_demo_02_mini_finds_2_folders():
    """Run on yE-A reference fixture -> 2 folders (VA01, AR01)."""
    fixture = Path(__file__).parent / "fixtures" / "em_demo_02_mini.graphml"
    result = walk_folders(fixture)
    assert len(result) == 2
    values = {f.auto_value for f in result}
    assert values == {"VA01", "AR01"}


def test_top_level_tablenode_excluded_from_folders():
    """Mini fixture has 'Archaeological Context' as the swimlane
    TableNode (technically yfiles.foldertype='group'). It MUST NOT
    appear in walk_folders result."""
    fixture = Path(__file__).parent / "fixtures" / "em_demo_02_mini.graphml"
    result = walk_folders(fixture)
    labels = {f.full_label for f in result}
    assert "Archaeological Context" not in labels


def test_label_with_description_extracts_prefix(tmp_path):
    """'VA01-foundation example' -> auto_value='VA01',
    extra_attrs['description']='foundation example'."""
    path = _make_graphml_one_folder(tmp_path, "VA01-foundation example")
    result = walk_folders(path)
    assert len(result) == 1
    assert result[0].auto_value == "VA01"
    assert result[0].auto_dimension == "attivita"
    assert result[0].extra_attrs.get("description") == "foundation example"


def test_unrecognized_prefix_uses_full_label_as_auto_value(tmp_path):
    """Folder labeled 'Foundation Area' has no prefix match ->
    auto_dimension=None, auto_value='Foundation Area' (no
    description extracted because no prefix)."""
    path = _make_graphml_one_folder(tmp_path, "Foundation Area")
    result = walk_folders(path)
    assert len(result) == 1
    assert result[0].auto_dimension is None
    assert result[0].auto_value == "Foundation Area"
    assert result[0].extra_attrs == {}


def test_nested_folder_membership_split(tmp_path):
    """Folder A -> folder B -> leaf X. A.member_yed_ids excludes X
    (direct children only); A.nested_folder_ids includes B.yed_id;
    B.member_yed_ids includes X; B.parent_folder_id == A.yed_id."""
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns"
         xmlns:y="http://www.yworks.com/xml/graphml">
  <key for="node" id="d6" yfiles.type="nodegraphics"/>
  <graph edgedefault="directed" id="G">
    <node id="A" yfiles.foldertype="group">
      <data key="d6"><y:ProxyAutoBoundsNode><y:Realizers active="0">
        <y:GroupNode><y:NodeLabel>VA01</y:NodeLabel></y:GroupNode>
      </y:Realizers></y:ProxyAutoBoundsNode></data>
      <graph edgedefault="directed" id="A:">
        <node id="B" yfiles.foldertype="group">
          <data key="d6"><y:ProxyAutoBoundsNode><y:Realizers active="0">
            <y:GroupNode><y:NodeLabel>AR01</y:NodeLabel></y:GroupNode>
          </y:Realizers></y:ProxyAutoBoundsNode></data>
          <graph edgedefault="directed" id="B:">
            <node id="X">
              <data key="d6"><y:ShapeNode><y:NodeLabel>US01</y:NodeLabel></y:ShapeNode></data>
            </node>
          </graph>
        </node>
      </graph>
    </node>
  </graph>
</graphml>
"""
    path = tmp_path / "nested.graphml"
    path.write_text(xml)
    result = walk_folders(path)
    # Walker is depth-first, so B is recorded before A returns
    by_id = {f.yed_id: f for f in result}
    assert "A" in by_id and "B" in by_id
    a = by_id["A"]
    b = by_id["B"]
    assert "X" not in a.member_yed_ids
    assert "B" in a.nested_folder_ids
    assert "X" in b.member_yed_ids
    assert b.parent_folder_id == "A"
    assert a.parent_folder_id is None


def test_cycle_detection_raises_cycle_detected_error(tmp_path):
    """Synthetic graphml where folder A's child folder B contains
    a node with id=A again (impossible in real yEd but the walker's
    visited set must catch the cycle)."""
    # We simulate a cycle by having two folders with the same id
    # nested inside each other. lxml parses this fine; the walker
    # raises when it re-visits.
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns"
         xmlns:y="http://www.yworks.com/xml/graphml">
  <key for="node" id="d6" yfiles.type="nodegraphics"/>
  <graph edgedefault="directed" id="G">
    <node id="A" yfiles.foldertype="group">
      <data key="d6"><y:ProxyAutoBoundsNode><y:Realizers active="0">
        <y:GroupNode><y:NodeLabel>VA01</y:NodeLabel></y:GroupNode>
      </y:Realizers></y:ProxyAutoBoundsNode></data>
      <graph edgedefault="directed" id="A:">
        <node id="A" yfiles.foldertype="group">
          <data key="d6"><y:ProxyAutoBoundsNode><y:Realizers active="0">
            <y:GroupNode><y:NodeLabel>VA01-inner</y:NodeLabel></y:GroupNode>
          </y:Realizers></y:ProxyAutoBoundsNode></data>
          <graph edgedefault="directed" id="A2:"/>
        </node>
      </graph>
    </node>
  </graph>
</graphml>
"""
    path = tmp_path / "cycle.graphml"
    path.write_text(xml)
    with pytest.raises(CycleDetectedError):
        walk_folders(path)
