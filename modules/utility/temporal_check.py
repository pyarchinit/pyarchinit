"""Temporal/stratigraphic paradox detection for Verifica rapporti (pyArchInit).

Qt-free. Detects when stratigraphic relations contradict period/phase ordering,
using periodizzazione_table chronology (cron_iniziale/finale). Stratigraphy is
the observed reference; auto-fixes move PERIODS (not relations). See
docs/superpowers/specs/2026-06-09-temporal-paradox-detection-design.md.

Import note: imports helpers from rapporti_check at module level. Future tasks
will wire this module into check_rapporti; no circular-import risk exists
because rapporti_check has no back-reference to this module.
"""
from __future__ import annotations

from modules.utility.rapporti_check import (  # noqa: F401  # pre-staged for Task 2+
    Edit, Issue, _real_us, _strat_edges, _utok, _t,
)

# Issue kinds
TEMPORAL_INVERSION = "temporal_inversion"
TEMPORAL_CONTEMPORANEITY = "temporal_contemporaneity"
TEMPORAL_UNEVALUABLE = "temporal_unevaluable"

#: source is MORE RECENT than target
_LATER = frozenset({"overlies", "cuts", "fills", "abuts", "is_after"})
#: source is MORE ANCIENT than target
_EARLIER = frozenset({"is_overlain_by", "is_cut_by", "is_filled_by",
                      "is_abutted_by", "is_before"})
#: contemporaneous (same period required)
_CONTEMP = frozenset({"is_physically_equal_to", "is_bonded_to"})


def _classify_relation(et):
    """Map an edge type to 'later' | 'earlier' | 'contemp' | None."""
    if et in _LATER:
        return "later"
    if et in _EARLIER:
        return "earlier"
    if et in _CONTEMP:
        return "contemp"
    return None
