"""Multilingual US/USM dispatch + localized d13 labels (khutm fix, 2026-06).

pyArchInit localises the US / USM ``unita_tipo`` codes per UI language
(``pyarchinit_i18n_stratigraphic.UNIT_TYPE_ABBREV``: SU/WSU=en, SE/MSE=de,
UE/UEM=es·ca·pt, USZ=ro, ΣΜ/ΤΣΜ=el). Before this fix the d13
``physical_relationships`` dispatch in ``s3dgraphy.sync.rapporti`` only
recognised the Italian "US"/"USM" codes, so a non-Italian site (e.g. an
English DB using "SU"/"WSU") fell through to the ``>>`` / ``<<`` shorthand
even for real Harris units.

These tests pin:
  1. multilingual US/USM endpoints take the verbose branch (not shorthand);
  2. ``serialize_rapporti_from_edges`` emits the label from the source
     node's own ``rapporti`` column, capitalized (Covers / Copre / …),
     so the d13 string matches the DB verbatim in the site's UI language;
  3. virtual units (USVs/SF/…) and continuity (CON) keep their shorthand;
  4. a node without a usable ``rapporti`` attribute (e.g. a yEd-imported
     graph) falls back to the canonical verbose label.
"""
from __future__ import annotations

import pytest


def _R():
    import modules.s3dgraphy.sync.rapporti as R
    return R


# --- 1. multilingual canonical recognition --------------------------------

@pytest.mark.parametrize(
    "ut",
    ["US", "USM",            # it / fr
     "SU", "WSU",            # en / ar
     "SE", "MSE",            # de
     "UE", "UEM",            # es / ca / pt
     "USZ",                  # ro
     "ΣΜ", "ΤΣΜ"],  # el: ΣΜ / ΤΣΜ
)
def test_multilingual_us_usm_takes_verbose_branch(ut):
    R = _R()
    label = R.select_rapporti_label("overlies", ut, ut)
    assert label not in (">", "<", ">>", "<<"), (
        f"unita_tipo {ut!r} should be canonical (verbose), got {label!r}")


def test_virtual_and_continuity_keep_shorthand():
    R = _R()
    assert R.select_rapporti_label("overlies", "USVs", "US") == ">>"
    assert R.select_rapporti_label("is_overlain_by", "US", "USVs") == "<<"
    assert R.select_rapporti_label("overlies", "CON", "US") == ">"
    assert R.select_rapporti_label("is_overlain_by", "US", "CON") == "<"


# --- 2-4. serialize_rapporti_from_edges (d13) -----------------------------

class _N:
    def __init__(self, nid, name, ut, rap=None, us=None):
        self.node_id = nid
        self.name = name
        self.attributes = {"unita_tipo": ut}
        if rap is not None:
            self.attributes["rapporti"] = rap
        if us is not None:
            self.attributes["us"] = us


class _E:
    def __init__(self, s, t, et):
        self.edge_source = s
        self.edge_target = t
        self.edge_type = et


class _G:
    def __init__(self, nodes, edges):
        self.nodes = nodes
        self.edges = edges


def _two_us(ut, rap):
    """Source US *ut* with rapporti column *rap* → target US '2'."""
    n1 = _N("a", "n1", ut, rap=rap, us="1")
    n2 = _N("b", "n2", ut, us="2")
    return _G([n1, n2], [_E("a", "b", "overlies")])


def test_d13_english_label_localized_and_capitalized():
    """English DB ("SU" + lowercase 'covers') → 'Covers' (the khutm bug)."""
    R = _R()
    out = R.serialize_rapporti_from_edges(
        _two_us("SU", "[['covers', '2', '1', 'x']]"), "Al-Khutm")
    assert out["a"] == [["Covers", "2", "1", "Al-Khutm"]]


def test_d13_italian_label_capitalized():
    R = _R()
    out = R.serialize_rapporti_from_edges(
        _two_us("US", "[['copre', '2', '1', 'x']]"), "Site")
    assert out["a"] == [["Copre", "2", "1", "Site"]]


def test_d13_falls_back_to_canonical_without_column():
    """yEd-style node with no rapporti attribute → canonical verbose."""
    R = _R()
    n1 = _N("a", "n1", "SU", us="1")  # no 'rapporti' attribute
    n2 = _N("b", "n2", "SU", us="2")
    out = R.serialize_rapporti_from_edges(_G([n1, n2], [_E("a", "b", "overlies")]),
                                          "Site")
    assert out["a"] == [["Copre", "2", "1", "Site"]]


def test_d13_virtual_unit_keeps_shorthand_even_with_verbose_column():
    """A virtual unit must stay ``>>`` regardless of its column text."""
    R = _R()
    out = R.serialize_rapporti_from_edges(
        _two_us("USVs", "[['copre', '2', '1', 'x']]"), "Site")
    assert out["a"] == [[">>", "2", "1", "Site"]]
