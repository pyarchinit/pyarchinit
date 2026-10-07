"""yE-B Classifier: L1 integration test on em_demo_02_mini fixture.

Runs classify_leaves on the yE-A reference fixture and verifies
the count breakdown matches the known structure of the fixture.
This catches regex-vs-fixture mismatches that pure L0 unit tests
on synthetic input cannot.
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path

import pytest

from s3dgraphy.sync.yed_classifier import (
    ClassificationKind,
    classify_leaves,
)

FIXTURES = Path(__file__).parent / "fixtures"


def test_classify_em_demo_02_mini_smoke():
    """End-to-end: classify_leaves on em_demo_02_mini.graphml.

    Mini fixture has 6 leaves (from yE-A):
      - 2 US (US01, US02)        -> US_REAL
      - 1 USV (USV101)           -> USV_VIRTUAL
      - 1 SF (SF105)             -> SPECIAL_FIND
      - 1 VSF (VSF107)           -> VIRTUAL_FIND
      - 1 Property (material)    -> PROPERTY

    Folder nodes (VA01-foundation example, AR01-area example)
    must be EXCLUDED from the classified list -- they're handled
    by yE-C yed_group_walker.
    """
    fixture = FIXTURES / "em_demo_02_mini.graphml"
    assert fixture.exists(), f"Expected yE-A fixture at {fixture}"

    classified = classify_leaves(fixture)

    # Count breakdown
    counts = Counter(n.auto_kind for n in classified)
    assert counts[ClassificationKind.US_REAL]      == 2, f"Got {counts}"
    assert counts[ClassificationKind.USV_VIRTUAL]  == 1, f"Got {counts}"
    assert counts[ClassificationKind.SPECIAL_FIND] == 1, f"Got {counts}"
    assert counts[ClassificationKind.VIRTUAL_FIND] == 1, f"Got {counts}"
    assert counts[ClassificationKind.PROPERTY]     == 1, f"Got {counts}"

    # Total leaves count
    assert len(classified) == 6, f"Expected 6 leaves, got {len(classified)}"

    # Folder labels MUST NOT appear in the classified list
    labels = {n.label for n in classified}
    assert "VA01-foundation example" not in labels, \
        f"Folder VA01 leaked into classified leaves: {labels}"
    assert "AR01-area example" not in labels, \
        f"Folder AR01 leaked into classified leaves: {labels}"

    # All user_kind should equal auto_kind (no dialog override in yE-B)
    for n in classified:
        assert n.user_kind == n.auto_kind, (
            f"user_kind {n.user_kind} != auto_kind {n.auto_kind} "
            f"for {n.label}"
        )
