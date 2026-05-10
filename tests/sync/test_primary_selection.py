"""AI07 Group E: compute_primary unit tests.

Already implemented in graph_projector.py (Group C); this file pins
its behaviour with focused unit tests.
"""
from __future__ import annotations

from modules.s3dgraphy.sync.graph_projector import (
    DEFAULT_PRIMARY_PRIORITY,
    compute_primary,
)


def test_default_priority_struttura_first():
    """When US has both struttura and area, struttura wins."""
    memberships = [
        {"us_id": "U1", "group_uuid": "g_struttura", "group_kind": "struttura"},
        {"us_id": "U1", "group_uuid": "g_area",      "group_kind": "area"},
    ]
    primaries = compute_primary(memberships, DEFAULT_PRIMARY_PRIORITY)
    assert primaries == {"U1": "g_struttura"}


def test_override_changes_primary():
    """Custom priority puts area first."""
    memberships = [
        {"us_id": "U1", "group_uuid": "g_struttura", "group_kind": "struttura"},
        {"us_id": "U1", "group_uuid": "g_area",      "group_kind": "area"},
    ]
    custom_order = ["area", "struttura"]  # area first
    primaries = compute_primary(memberships, custom_order)
    assert primaries == {"U1": "g_area"}


def test_toponym_excluded_from_primary():
    """Even with priority list including 'toponym', toponym is never primary."""
    memberships = [
        {"us_id": "U1", "group_uuid": "g_top", "group_kind": "toponym"},
        {"us_id": "U1", "group_uuid": "g_str", "group_kind": "struttura"},
    ]
    primaries = compute_primary(
        memberships, ["toponym", "struttura"]  # toponym first in order!
    )
    assert primaries == {"U1": "g_str"}, \
        "toponym must never be primary regardless of priority order"


def test_fallback_to_adhoc_when_no_spatial():
    """If US has only adhoc + toponym, adhoc wins as fallback."""
    memberships = [
        {"us_id": "U1", "group_uuid": "g_adhoc", "group_kind": "adhoc"},
        {"us_id": "U1", "group_uuid": "g_top",   "group_kind": "toponym"},
    ]
    primaries = compute_primary(memberships, DEFAULT_PRIMARY_PRIORITY)
    assert primaries == {"U1": "g_adhoc"}


def test_us_with_no_eligible_membership_excluded():
    """US with only toponym membership has no entry in primaries."""
    memberships = [
        {"us_id": "U1", "group_uuid": "g_top", "group_kind": "toponym"},
    ]
    primaries = compute_primary(memberships, DEFAULT_PRIMARY_PRIORITY)
    assert primaries == {}
