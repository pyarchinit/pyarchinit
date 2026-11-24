"""AI07/H.5 follow-up: rapporti label dispatch.

Convention since s3dgraphy 1.6.0.dev139 (MICRO-LG7, E.D. 22 Nov 2026,
«Time stays time towards pyArchInit»): the token depends on the KIND of
the relation, no longer on the unit type of its ends.
- physical relation (overlies, cuts, abuts, bonded…) → verbose Italian
  ("Copre", "Taglia", …) for EVERY unit type
- temporal relation (is_after / is_before) → `>` / `<` for every unit
  type — never «Copre»: a fact of time is not a fact of the ground
- paradata chain (DOC, extractor, generic_connection…) → `>>` / `<<`
- has_same_time → no pyArchInit voice (None): left out, and counted in
  the log by the writers

(Until dev138 the dispatch followed the unit type — the May 2026
convention: US/USM verbose, CON `>`, everything else `>>` — and an
``is_after`` between two US was written as «Copre».)

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
    # temporal precedence is not a cover (MICRO-LG7)
    assert sel("is_after", "US", "US") == ">"


def test_usm_us_emits_verbose_italian():
    """USM ↔ US: still canonical."""
    sel, _, _ = _import_helpers()
    assert sel("overlies", "USM", "US") == "Copre"
    assert sel("is_bonded_to", "USM", "USM") == "Si lega a"


def test_con_involved_physical_keeps_voice_temporal_is_arrow():
    """CON (Continuity): a physical relation keeps its voice, a temporal
    one is the single arrow — as for every other unit type."""
    sel, _, _ = _import_helpers()
    assert sel("overlies", "CON", "US") == "Copre"
    assert sel("is_overlain_by", "US", "CON") == "Coperto da"
    assert sel("is_after", "CON", "US") == ">"
    assert sel("cuts", "CON", "CON") == "Taglia"


def test_usvs_physical_keeps_voice_temporal_is_arrow():
    """USVs: physical relation verbose, temporal relation `>` / `<`."""
    sel, _, _ = _import_helpers()
    assert sel("overlies", "USVs", "US") == "Copre"
    assert sel("is_overlain_by", "US", "USVs") == "Coperto da"
    assert sel("is_after", "USVs", "USVs") == ">"


def test_doc_paradata_emits_double_arrow():
    """DOC (paradata) → double arrow."""
    sel, _, _ = _import_helpers()
    assert sel("generic_connection", "DOC", "US") == ">>"
    assert sel("extracted_from", "US", "DOC") == ">>"


def test_sf_vsf_temporal_is_single_arrow():
    """SF / VSF / USVn / USD: temporal precedence is `>` / `<` — the double
    arrow is kept for the paradata chain only."""
    sel, _, _ = _import_helpers()
    for ut in ("SF", "VSF", "USVn", "USD"):
        assert sel("is_after", ut, "US") == ">", f"{ut} should emit >"
        assert sel("is_before", "US", ut) == "<", f"{ut} should emit <"


def test_unknown_unit_type_temporal_is_single_arrow():
    """Defensive: an unknown unit type follows the relation kind too."""
    sel, _, _ = _import_helpers()
    assert sel("is_after", "UNKNOWN_NEW_TYPE", "ANOTHER") == ">"


def test_has_same_time_has_no_pyarchinit_voice():
    """Contemporaneity has no rapporto in pyArchInit yet: no label, so the
    writers leave it out and say so in the log (MICRO-LG7)."""
    sel, _, _ = _import_helpers()
    assert sel("has_same_time", "US", "US") is None


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
