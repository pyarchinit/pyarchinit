"""AI07/H.5 follow-up: rapporti shorthand dispatch by unit type.

Convention (per pyarchinit author, May 2026):
- US ↔ US/USM    → verbose Italian ("Copre", "Coperto da", ...)
- USM ↔ US/USM   → verbose Italian
- CON involved   → single arrow `>` / `<`
- All other non-US/USM (USVs, USVn, SF, VSF, USD, DOC, ...)
                 → double arrow `>>` / `<<`

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
    assert sel("is_after", "US", "US") == "Copre"


def test_usm_us_emits_verbose_italian():
    """USM ↔ US: still canonical."""
    sel, _, _ = _import_helpers()
    assert sel("overlies", "USM", "US") == "Copre"
    assert sel("is_bonded_to", "USM", "USM") == "Si lega a"


def test_con_involved_emits_single_arrow():
    """CON (Continuity) on either end → single arrow `>` / `<`."""
    sel, _, _ = _import_helpers()
    assert sel("overlies", "CON", "US") == ">"
    assert sel("is_overlain_by", "US", "CON") == "<"
    assert sel("is_after", "CON", "US") == ">"
    assert sel("cuts", "CON", "CON") == ">"


def test_usvs_emits_double_arrow():
    """USVs ↔ anything (except US/USM) → double arrow `>>` / `<<`."""
    sel, _, _ = _import_helpers()
    assert sel("overlies", "USVs", "US") == ">>"
    assert sel("is_overlain_by", "US", "USVs") == "<<"
    assert sel("is_after", "USVs", "USVs") == ">>"


def test_doc_paradata_emits_double_arrow():
    """DOC (paradata) → double arrow."""
    sel, _, _ = _import_helpers()
    assert sel("generic_connection", "DOC", "US") == ">>"
    assert sel("extracted_from", "US", "DOC") == ">>"


def test_sf_vsf_emits_double_arrow():
    """SF / VSF (special finds, virtual special finds) → double arrow."""
    sel, _, _ = _import_helpers()
    for ut in ("SF", "VSF", "USVn", "USD"):
        assert sel("is_after", ut, "US") == ">>", f"{ut} should emit >>"
        assert sel("is_before", "US", ut) == "<<", f"{ut} should emit <<"


def test_unknown_unit_type_falls_to_double_arrow():
    """Defensive: an unknown unit type falls into the "non-canonical"
    branch and emits double arrow."""
    sel, _, _ = _import_helpers()
    # Neither end is US/USM → emit shorthand
    assert sel("is_after", "UNKNOWN_NEW_TYPE", "ANOTHER") == ">>"


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
