"""RAPPORTI_TO_EDGE_TYPE must cover pyArchInit's full i18n relationship
vocabulary in EVERY language the UI supports, so a graph projected from a
non-IT/EN site builds the right edges and the reciprocity auto-fix's inverse
label round-trips.

The 10×10 table is *duplicated* inside ``modules.s3dgraphy.sync.rapporti``
(not imported) to keep that package free of ``pyarchinit.*`` imports. These
tests fail loudly if the duplicate ever drifts from the i18n source of truth.
"""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_embedded_table_matches_pyarchinit_i18n_exactly():
    from modules.utility.pyarchinit_i18n_stratigraphic import RELATIONSHIPS
    from modules.s3dgraphy.sync.rapporti import _REL_TERMS_BY_LANG
    assert set(_REL_TERMS_BY_LANG) == set(RELATIONSHIPS), (
        "language sets diverged: "
        f"{set(_REL_TERMS_BY_LANG) ^ set(RELATIONSHIPS)}")
    for lang, terms in RELATIONSHIPS.items():
        assert list(_REL_TERMS_BY_LANG[lang]) == list(terms), (
            f"relationship terms diverged for {lang!r}")


def test_every_i18n_term_maps_to_correct_edge_type():
    from modules.utility.pyarchinit_i18n_stratigraphic import RELATIONSHIPS
    from modules.s3dgraphy.sync.rapporti import (
        RAPPORTI_TO_EDGE_TYPE, _REL_INDEX_EDGE_TYPE)
    for lang, terms in RELATIONSHIPS.items():
        for i, t in enumerate(terms):
            assert RAPPORTI_TO_EDGE_TYPE.get(t.lower()) == _REL_INDEX_EDGE_TYPE[i], (
                f"{lang}[{i}]={t!r} -> {RAPPORTI_TO_EDGE_TYPE.get(t.lower())!r} "
                f"(expected {_REL_INDEX_EDGE_TYPE[i]!r})")


def test_reciprocal_edge_types_consistent_with_inverse_pairs():
    """i18n inverse pairs (index a↔b, e.g. 8↔9 = abuts/supports) must map to
    edge types that are each other's inverse in the detector's
    ``_EDGE_TYPE_INVERSE`` — otherwise the auto-fix's inverse label, though it
    parses, would not satisfy the reciprocity check."""
    from modules.utility.pyarchinit_i18n_stratigraphic import _INVERSE_PAIRS
    from modules.s3dgraphy.sync.rapporti import _REL_INDEX_EDGE_TYPE
    from modules.utility.rapporti_check import _EDGE_TYPE_INVERSE
    for a, b in _INVERSE_PAIRS:
        et_a, et_b = _REL_INDEX_EDGE_TYPE[a], _REL_INDEX_EDGE_TYPE[b]
        assert _EDGE_TYPE_INVERSE.get(et_a) == et_b, (
            f"i18n pair ({a},{b}) -> ({et_a},{et_b}) but "
            f"_EDGE_TYPE_INVERSE[{et_a}]={_EDGE_TYPE_INVERSE.get(et_a)!r}")
