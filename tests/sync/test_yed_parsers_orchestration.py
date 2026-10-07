"""yE-C Parsers: L1 cross-parser orchestration test.

Verifies that yE-B classifier + yE-C table parser + yE-C group
walker produce mutually consistent state on the same fixture.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from s3dgraphy.sync.yed_classifier import classify_leaves
from s3dgraphy.sync.yed_group_walker import walk_folders
from s3dgraphy.sync.yed_table_parser import extract_periods

FIXTURES = Path(__file__).parent / "fixtures"


def test_classifier_periods_folders_consistent_on_em_demo_02_mini():
    """Cross-parser consistency on the yE-A reference fixture.

    Mini fixture has 6 leaves total, distributed across 2 group
    folders (VA01 has 4, AR01 has 2). 2 periods. Classifier sees
    only the 6 leaves (folders excluded); walker sees 2 folders
    (TableNode excluded); periods see all 6 leaves distributed by
    Y-coordinate.
    """
    fixture = FIXTURES / "em_demo_02_mini.graphml"
    assert fixture.exists()

    classified = classify_leaves(fixture)
    periods = extract_periods(fixture)
    folders = walk_folders(fixture)

    # Counts
    assert len(classified) == 6, f"got {len(classified)} classified"
    assert len(periods) == 2, f"got {len(periods)} periods"
    assert len(folders) == 2, f"got {len(folders)} folders"

    # No leaf yed_id appears as a folder (folders are NOT leaves).
    classified_ids = {n.yed_id for n in classified}
    folder_ids = {f.yed_id for f in folders}
    assert classified_ids.isdisjoint(folder_ids), \
        f"Overlap: {classified_ids & folder_ids}"

    # Every classified leaf appears in at least one folder's
    # member list.
    all_members: set = set()
    for f in folders:
        all_members.update(f.member_yed_ids)
    assert classified_ids.issubset(all_members), \
        f"Leaves not accounted for: {classified_ids - all_members}"

    # Folder labels don't leak into classified labels.
    classified_labels = {n.label for n in classified}
    folder_labels = {f.full_label for f in folders}
    assert classified_labels.isdisjoint(folder_labels)
