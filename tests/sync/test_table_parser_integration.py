"""yE-C Parsers: L1 integration test for extract_periods() on the
yE-A reference fixture (em_demo_02_mini.graphml)."""
from __future__ import annotations

from pathlib import Path

import pytest

from s3dgraphy.sync.yed_table_parser import extract_periods

FIXTURES = Path(__file__).parent / "fixtures"


def test_extract_periods_em_demo_02_mini():
    """Mini fixture has TableNode with 2 rows (Period01, Period02).
    Each row is 300px tall with header_height=30 (default).
    Row 0: y=[30, 330), 4 leaves at y=100/160/220/100.
    Row 1: y=[330, 630), 2 leaves at y=400/460.
    """
    fixture = FIXTURES / "em_demo_02_mini.graphml"
    assert fixture.exists(), f"Expected yE-A fixture at {fixture}"

    periods = extract_periods(fixture)
    assert len(periods) == 2

    p0 = periods[0]
    assert p0.auto_label == "Period01"
    assert p0.auto_periodo == 1
    assert p0.auto_fase == 1
    assert p0.user_label == p0.auto_label
    assert p0.user_periodo == 1
    assert p0.user_fase == 1

    p1 = periods[1]
    assert p1.auto_label == "Period02"
    assert p1.auto_periodo == 2
    assert p1.auto_fase == 1

    # Y-coord membership: total members <= 6 leaves in fixture.
    total_members = sum(len(p.member_yed_ids) for p in periods)
    assert 0 <= total_members <= 6, f"got {total_members} members"
