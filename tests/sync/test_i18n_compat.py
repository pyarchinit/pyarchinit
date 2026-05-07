"""Backwards-compat regression: pyarchinit_i18n_stratigraphic exports
must keep working after the VocabProvider adapter refactor."""
from __future__ import annotations


def test_common_items_importable():
    from modules.utility.pyarchinit_i18n_stratigraphic import _COMMON_ITEMS
    # Spec §4.4: post-migration USVA/USVB → USVs, USVC → USVn. The compat
    # shim continues to expose the legacy abbrevs so old code keeps
    # working; the migration is the only place where they get rewritten.
    assert "USVA" in _COMMON_ITEMS or "USVs" in _COMMON_ITEMS
    assert "DOC" in _COMMON_ITEMS


def test_unit_type_abbrev_importable():
    from modules.utility.pyarchinit_i18n_stratigraphic import UNIT_TYPE_ABBREV
    assert "it" in UNIT_TYPE_ABBREV
    assert UNIT_TYPE_ABBREV["it"] == ("US", "USM")


def test_get_unit_type_items_returns_iterable():
    from modules.utility.pyarchinit_i18n_stratigraphic import get_unit_type_items
    items = get_unit_type_items("it")
    assert "US" in items
    assert "USM" in items


def test_is_us_type_recognises_legacy():
    from modules.utility.pyarchinit_i18n_stratigraphic import is_us_type
    assert is_us_type("US")
    assert is_us_type("SU")  # English


def test_all_us_abbrevs_exposed():
    from modules.utility.pyarchinit_i18n_stratigraphic import ALL_US_ABBREVS
    assert "US" in ALL_US_ABBREVS
