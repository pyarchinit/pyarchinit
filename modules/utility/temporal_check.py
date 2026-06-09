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


# ---------------------------------------------------------------------------
# Task 2: chronology readers + unit_span
# ---------------------------------------------------------------------------

def build_chronology(handle, sito):
    """(periodo, fase) -> (cron_iniziale, cron_finale) for *sito*."""
    from sqlalchemy import text
    out = {}
    with handle.engine.connect() as conn:
        rows = conn.execute(text(
            "SELECT periodo, fase, cron_iniziale, cron_finale "
            "FROM periodizzazione_table WHERE sito = :s"), {"s": sito}).fetchall()
    for periodo, fase, ci, cf in rows:
        key = ("" if periodo is None else str(periodo),
               "" if fase is None else str(fase))
        out[key] = (None if ci is None else int(ci),
                    None if cf is None else int(cf))
    return out


def load_unit_periods(handle, sito):
    """us -> (periodo_iniziale, fase_iniziale, periodo_finale, fase_finale)."""
    from sqlalchemy import text
    out = {}
    with handle.engine.connect() as conn:
        rows = conn.execute(text(
            "SELECT us, periodo_iniziale, fase_iniziale, periodo_finale, "
            "fase_finale FROM us_table WHERE sito = :s"), {"s": sito}).fetchall()
    for us, pi, fi, pf, ff in rows:
        if us is None:
            continue
        out[str(us)] = ("" if pi is None else str(pi),
                        "" if fi is None else str(fi),
                        "" if pf is None else str(pf),
                        "" if ff is None else str(ff))
    return out


def _cron_of(periodo, fase, chrono, which):
    """cron_iniziale (which='ini') or cron_finale (which='fin') of (periodo,
    fase). Falls back to aggregating over all fasi of the periodo when the
    exact (periodo, fase) row is absent (blank fase tolerance)."""
    rec = chrono.get((str(periodo), str(fase)))
    if rec is not None:
        return rec[0] if which == "ini" else rec[1]
    vals = [v[0 if which == "ini" else 1]
            for (p, _f), v in chrono.items()
            if p == str(periodo) and v[0 if which == "ini" else 1] is not None]
    if not vals:
        return None
    return min(vals) if which == "ini" else max(vals)


def unit_span(periods, chrono):
    """periods = (pi, fi, pf, ff) -> (cron_ini, cron_fin) or None if undatable."""
    if periods is None:
        return None
    pi, fi, pf, ff = periods
    if not pi or not pf:
        return None
    ci = _cron_of(pi, fi, chrono, "ini")
    cf = _cron_of(pf, ff, chrono, "fin")
    if ci is None or cf is None:
        return None
    return (ci, cf)
