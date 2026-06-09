"""Tests for modules.utility.temporal_check (temporal paradox detection)."""
from modules.utility import temporal_check as TC


def test_classify_relation():
    for et in ("overlies", "cuts", "fills", "abuts", "is_after"):
        assert TC._classify_relation(et) == "later"
    for et in ("is_overlain_by", "is_cut_by", "is_filled_by",
               "is_abutted_by", "is_before"):
        assert TC._classify_relation(et) == "earlier"
    for et in ("is_physically_equal_to", "is_bonded_to"):
        assert TC._classify_relation(et) == "contemp"
    assert TC._classify_relation("generic_connection") is None
    assert TC._classify_relation(None) is None
