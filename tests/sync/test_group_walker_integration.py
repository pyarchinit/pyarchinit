"""yE-C Parsers: L1 integration test for walk_folders() on the
yE-A reference fixture (em_demo_02_mini.graphml)."""
from __future__ import annotations

from pathlib import Path

import pytest

from s3dgraphy.sync.yed_group_walker import walk_folders

FIXTURES = Path(__file__).parent / "fixtures"


def test_walk_folders_em_demo_02_mini():
    """Mini fixture has 2 group folders:
      - VA01-foundation example (attivita, 4 direct leaves)
      - AR01-area example (area, 2 direct leaves)
    Top-level TableNode 'Archaeological Context' must be excluded.
    """
    fixture = FIXTURES / "em_demo_02_mini.graphml"
    assert fixture.exists(), f"Expected yE-A fixture at {fixture}"

    folders = walk_folders(fixture)
    assert len(folders) == 2

    by_value = {f.auto_value: f for f in folders}
    assert "VA01" in by_value
    assert "AR01" in by_value

    va01 = by_value["VA01"]
    assert va01.full_label == "VA01-foundation example"
    assert va01.auto_dimension == "attivita"
    assert va01.user_dimension == "attivita"
    assert va01.extra_attrs.get("description") == "foundation example"
    assert len(va01.member_yed_ids) == 4

    ar01 = by_value["AR01"]
    assert ar01.full_label == "AR01-area example"
    assert ar01.auto_dimension == "area"
    assert ar01.extra_attrs.get("description") == "area example"
    assert len(ar01.member_yed_ids) == 2

    # Top-level TableNode "Archaeological Context" must NOT appear.
    labels = {f.full_label for f in folders}
    assert "Archaeological Context" not in labels
