"""yE-B Classifier: L0 unit tests for classify_leaves().

Verifies the regex map ordering, case insensitivity, unknown fallback,
and document-order preservation. Each test builds a synthetic graphml
in tmp_path and exercises classify_leaves() against it.

Tests are independent (no shared state, no fixture files modified).
"""
from __future__ import annotations

from pathlib import Path

import pytest

from s3dgraphy.sync.yed_classifier import (
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


def test_classify_reused_special_find(tmp_path):
    """s3dgraphy-bump 0.1.42: RSF42 (Reused Special Find / spolia) →
    REUSED_SPECIAL_FIND. Regex `^RSF\\d+` matches before the generic
    SF rule (which starts with S, not R, so no real collision; the
    test pins explicit recognition)."""
    path = _make_graphml(tmp_path, ["RSF42"])
    result = classify_leaves(path)
    assert len(result) == 1
    assert result[0].auto_kind == ClassificationKind.REUSED_SPECIAL_FIND


def test_classify_document_with_subdots(tmp_path):
    """Bug I (2026-05-15 user feedback): in the Extended Matrix
    convention, ``D.NN.MM`` is an ExtractorNode (extraction MM from
    document NN), NOT a DocumentNode. The classifier reads BPMN
    properties first; in their absence it falls back to label depth:
    a ``D.`` label with TWO dots (multi-level path after the prefix)
    is treated as Extractor. Before this fix the regex matched
    ``^D\\.\\d+`` for both labels and the us_table dedup collapsed
    extractor + document into one row, dropping edges as self-loops.
    """
    path = _make_graphml(tmp_path, ["D.01.03"])
    result = classify_leaves(path)
    assert len(result) == 1
    assert result[0].auto_kind == ClassificationKind.EXTRACTOR


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


def test_classify_usvs_usvn_formal_wins_over_usv_generic(tmp_path):
    """USVs / USVn (bare or numbered) match USV_FORMAL, NOT USV_VIRTUAL.

    Verifies the order-sensitive regex list: USV_FORMAL (^USVs\\d*$ |
    ^USVn\\d*$) precedes USV_VIRTUAL (^USV\\d+). Labels like USVs01,
    USVn05 are common in archaeological field practice for formal
    virtual stratigraphic units (structural / negative) and must NOT
    be classified as generic USV.
    """
    # Bare forms
    bare_dir = tmp_path / "bare"
    bare_dir.mkdir()
    path_bare = _make_graphml(bare_dir, ["USVs", "USVn"])
    result_bare = classify_leaves(path_bare)
    assert len(result_bare) == 2
    assert result_bare[0].auto_kind == ClassificationKind.USV_FORMAL
    assert result_bare[1].auto_kind == ClassificationKind.USV_FORMAL

    # Numbered forms (the regression caught by code review)
    num_dir = tmp_path / "num"
    num_dir.mkdir()
    path_num = _make_graphml(num_dir, ["USVs01", "USVn05"])
    result_num = classify_leaves(path_num)
    assert len(result_num) == 2
    assert result_num[0].auto_kind == ClassificationKind.USV_FORMAL
    assert result_num[1].auto_kind == ClassificationKind.USV_FORMAL

    # USV + digits stays as USV_VIRTUAL
    virt_dir = tmp_path / "virt"
    virt_dir.mkdir()
    path_virt = _make_graphml(virt_dir, ["USV101"])
    result_virt = classify_leaves(path_virt)
    assert len(result_virt) == 1
    assert result_virt[0].auto_kind == ClassificationKind.USV_VIRTUAL


def test_classify_rules_override_parameter(tmp_path):
    """Caller can pass rules= to override DEFAULT_CLASSIFIER_RULES.
    This is the MVP extension point for future config-driven classification
    (yE-Closure or iteration 2)."""
    import re
    custom = [
        (re.compile(r"^FOO\d+"), ClassificationKind.SKIP),
        (re.compile(r"^BAR\d+"), ClassificationKind.UNKNOWN),
    ]
    path = _make_graphml(tmp_path, ["FOO42", "BAR7", "US01"])
    result = classify_leaves(path, rules=custom)
    assert len(result) == 3
    assert result[0].auto_kind == ClassificationKind.SKIP, \
        f"FOO42 should match custom rule -> SKIP, got {result[0].auto_kind}"
    assert result[1].auto_kind == ClassificationKind.UNKNOWN, \
        f"BAR7 should match custom rule -> UNKNOWN, got {result[1].auto_kind}"
    # US01 doesn't match any of the custom rules -> default UNKNOWN
    # (the default rules are NOT applied when rules= is provided)
    assert result[2].auto_kind == ClassificationKind.UNKNOWN, \
        f"US01 with custom rules-only should be UNKNOWN, got {result[2].auto_kind}"
