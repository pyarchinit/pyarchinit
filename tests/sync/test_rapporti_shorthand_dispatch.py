"""AI07/H.5 follow-up: rapporti shorthand dispatch by unit type.

Convention (per pyarchinit author, May 2026), refined by the rule
«time stays time, physical stays physical» (em_native_import, 17 Oct
2026; s3dgraphy 1.6.0.dev139, MICRO-LG7):
- a physical relation keeps its word for every pair of unit types
  ("Copre", "Coperto da", "Taglia", ...), CON / USVs / SF / USD included;
- `is_after` / `is_before` → single arrow `>` / `<` for every pair
  (no more "Copre" between two US: "later than" is not "covers");
- `>>` / `<<` only for the paradata chain (DOC, extractor, ...);
- an edge that is not a rapporto (`has_same_time`, `changed_from`) → None.

These tests pin `_select_rapporti_label` (the dispatch helper) and a
focused integration check via `_build_rapporti_from_edges` against an
in-memory s3dgraphy.Graph carrying mixed unit types.
"""
from __future__ import annotations

import pytest


def _import_helpers():
    from modules.s3dgraphy.sync.graph_ingestor import (
        _select_rapporti_label,
        _resolve_unita_tipo_for_dispatch,
        _build_rapporti_from_edges,
    )
    return (_select_rapporti_label,
            _resolve_unita_tipo_for_dispatch,
            _build_rapporti_from_edges)


# --- _select_rapporti_label unit tests ---


def test_us_us_emits_verbose_italian():
    """US ↔ US: classic Harris terminology."""
    sel, _, _ = _import_helpers()
    assert sel("overlies", "US", "US") == "Copre"
    assert sel("is_overlain_by", "US", "US") == "Coperto da"
    assert sel("cuts", "US", "US") == "Taglia"
    # dev139: time stays time («dopo» non è «copre»)
    assert sel("is_after", "US", "US") == ">"
    assert sel("is_before", "US", "US") == "<"


def test_usm_us_emits_verbose_italian():
    """USM ↔ US: still canonical."""
    sel, _, _ = _import_helpers()
    assert sel("overlies", "USM", "US") == "Copre"
    assert sel("is_bonded_to", "USM", "USM") == "Si lega a"


def test_con_involved_time_arrow_physical_word():
    """CON (Continuity): time is `>` / `<`; a physical relation keeps
    its word (dev139: it no longer becomes an arrow)."""
    sel, _, _ = _import_helpers()
    assert sel("overlies", "CON", "US") == "Copre"
    assert sel("is_overlain_by", "US", "CON") == "Coperto da"
    assert sel("is_after", "CON", "US") == ">"
    assert sel("cuts", "CON", "CON") == "Taglia"


def test_usvs_keeps_physical_words_and_single_arrow():
    """USVs: until dev113 every relation became `>>` / `<<` and came back
    as a generic paradata link. dev139: physical words and `>` for time;
    `>>` stays for the paradata only (see the DOC test below)."""
    sel, _, _ = _import_helpers()
    assert sel("overlies", "USVs", "US") == "Copre"
    assert sel("is_overlain_by", "US", "USVs") == "Coperto da"
    assert sel("is_after", "USVs", "USVs") == ">"


def test_doc_paradata_emits_double_arrow():
    """DOC (paradata) → double arrow."""
    sel, _, _ = _import_helpers()
    assert sel("generic_connection", "DOC", "US") == ">>"
    assert sel("extracted_from", "US", "DOC") == ">>"


def test_sf_vsf_time_is_single_arrow():
    """SF / VSF (special finds, virtual special finds) → double arrow."""
    sel, _, _ = _import_helpers()
    for ut in ("SF", "VSF", "USVn", "USD"):
        # dev139: time is `>` / `<` for every unit type, not paradata
        assert sel("is_after", ut, "US") == ">", f"{ut} should emit >"
        assert sel("is_before", "US", ut) == "<", f"{ut} should emit <"


def test_unknown_unit_type_time_is_single_arrow():
    """Defensive: an unknown unit type falls into the "non-canonical"
    branch and emits double arrow."""
    sel, _, _ = _import_helpers()
    # Neither end is US/USM: time is still time (dev139)
    assert sel("is_after", "UNKNOWN_NEW_TYPE", "ANOTHER") == ">"


def test_an_edge_that_is_not_a_rapporto_has_no_label():
    """dev139: select_rapporti_label returns None (no more the raw edge
    name); em_native_import skips it."""
    sel, _, _ = _import_helpers()
    assert sel("has_same_time", "US", "US") is None
    assert sel("changed_from", "US", "US") is None


# --- _resolve_unita_tipo_for_dispatch ---


def test_resolve_unita_tipo_from_attributes():
    _, resolve, _ = _import_helpers()

    class FakeNode:
        attributes = {"unita_tipo": "USVs"}

    assert resolve(FakeNode()) == "USVs"


def test_resolve_unita_tipo_from_class_name_fallback():
    """When no `unita_tipo` attribute, derive from s3dgraphy class
    name via _S3DGRAPHY_TYPE_TO_UNITA_TIPO."""
    _, resolve, _ = _import_helpers()

    class StratigraphicUnit:
        attributes = {}

    assert resolve(StratigraphicUnit()) == "US"


def test_resolve_unita_tipo_returns_none_for_unknown():
    _, resolve, _ = _import_helpers()

    class CompletelyUnknown:
        attributes = {}

    assert resolve(CompletelyUnknown()) is None
