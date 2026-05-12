"""yE-B Classifier: L0 unit tests for classify_leaves().

Verifies the regex map ordering, case insensitivity, unknown fallback,
and document-order preservation. Each test builds a synthetic graphml
in tmp_path and exercises classify_leaves() against it.

Tests are independent (no shared state, no fixture files modified).
"""
from __future__ import annotations

from pathlib import Path

import pytest

from modules.s3dgraphy.sync.yed_classifier import (
    ClassificationKind,
    classify_leaves,
)


def _make_graphml(tmp_path: Path, labels: list[str]) -> Path:
    """Build a minimal yEd-styled graphml with one leaf per label."""
    nodes_xml = []
    for i, lbl in enumerate(labels):
        nodes_xml.append(
            f'<node id="n{i}">'
            f'<data key="d6">'
            f'<y:ShapeNode>'
            f'<y:NodeLabel>{lbl}</y:NodeLabel>'
            f'</y:ShapeNode>'
            f'</data>'
            f'</node>'
        )
    xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
        '<graphml xmlns="http://graphml.graphdrawing.org/xmlns" '
        'xmlns:y="http://www.yworks.com/xml/graphml">\n'
        '  <key for="node" id="d6" yfiles.type="nodegraphics"/>\n'
        '  <graph edgedefault="directed" id="G">\n'
        f'    {"".join(nodes_xml)}\n'
        '  </graph>\n'
        '</graphml>\n'
    )
    path = tmp_path / "test.graphml"
    path.write_text(xml)
    return path


def test_classify_us_prefix(tmp_path):
    """US01 -> US_REAL."""
    path = _make_graphml(tmp_path, ["US01"])
    result = classify_leaves(path)
    assert len(result) == 1
    assert result[0].auto_kind == ClassificationKind.US_REAL
    assert result[0].label == "US01"
    assert result[0].user_kind == ClassificationKind.US_REAL


def test_classify_usv_prefix(tmp_path):
    """USV101 -> USV_VIRTUAL."""
    path = _make_graphml(tmp_path, ["USV101"])
    result = classify_leaves(path)
    assert len(result) == 1
    assert result[0].auto_kind == ClassificationKind.USV_VIRTUAL


def test_classify_usm_prefix_wins_over_us(tmp_path):
    """USM6 matches USM\\d+ (US_MASONRY), NOT US\\d+ (US_REAL).
    Verifies the order-sensitive regex list: USM precedes US."""
    path = _make_graphml(tmp_path, ["USM6"])
    result = classify_leaves(path)
    assert len(result) == 1
    assert result[0].auto_kind == ClassificationKind.US_MASONRY


def test_classify_special_find(tmp_path):
    """SF105 -> SPECIAL_FIND."""
    path = _make_graphml(tmp_path, ["SF105"])
    result = classify_leaves(path)
    assert len(result) == 1
    assert result[0].auto_kind == ClassificationKind.SPECIAL_FIND


def test_classify_virtual_find_wins_over_special(tmp_path):
    """VSF107 matches VSF\\d+ (VIRTUAL_FIND), NOT SF\\d+ (SPECIAL_FIND).
    Verifies the order-sensitive regex list: VSF precedes SF."""
    path = _make_graphml(tmp_path, ["VSF107"])
    result = classify_leaves(path)
    assert len(result) == 1
    assert result[0].auto_kind == ClassificationKind.VIRTUAL_FIND


def test_classify_document_with_subdots(tmp_path):
    """D.01.03 -> DOCUMENT (regex ^D\\.\\d+ matches the leading D.NN
    portion; trailing .03 is allowed)."""
    path = _make_graphml(tmp_path, ["D.01.03"])
    result = classify_leaves(path)
    assert len(result) == 1
    assert result[0].auto_kind == ClassificationKind.DOCUMENT


def test_classify_property_case_insensitive(tmp_path):
    """material / Material / MATERIAL / Heigth all -> PROPERTY."""
    path = _make_graphml(tmp_path,
                         ["material", "Material", "MATERIAL", "Heigth"])
    result = classify_leaves(path)
    assert len(result) == 4
    for node in result:
        assert node.auto_kind == ClassificationKind.PROPERTY, (
            f"Expected PROPERTY for {node.label!r}, got {node.auto_kind}"
        )


def test_classify_unknown_falls_through(tmp_path):
    """Foundation_01 has no prefix match -> UNKNOWN."""
    path = _make_graphml(tmp_path, ["Foundation_01"])
    result = classify_leaves(path)
    assert len(result) == 1
    assert result[0].auto_kind == ClassificationKind.UNKNOWN


def test_classify_uses_yed_document_order(tmp_path):
    """Returned list preserves yEd <node id=> document order."""
    path = _make_graphml(tmp_path,
                         ["US01", "USV101", "SF105", "D.01"])
    result = classify_leaves(path)
    assert len(result) == 4
    assert [n.label for n in result] == ["US01", "USV101", "SF105", "D.01"]
    assert [n.yed_id for n in result] == ["n0", "n1", "n2", "n3"]
