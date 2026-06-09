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


# ---------------------------------------------------------------------------
# Task 3: detect_temporal + localized summaries
# ---------------------------------------------------------------------------

def _node_us_map(graph):
    m = {}
    for n in getattr(graph, "nodes", None) or []:
        u = _real_us(n)
        if u is not None:
            m[n.node_id] = str(u)
    return m


def _periodo(us, unit_periods):
    p = unit_periods.get(us)
    return p[0] if p and p[0] else "?"


def detect_temporal(graph, chrono, unit_periods, *, sito, lang="it"):
    """Return temporal-paradox Issues (no edits yet — see solve_fixes).

    *sito* is accepted as a keyword-only parameter for API symmetry with
    callers that pre-filter ``unit_periods`` and ``chrono`` by site before
    calling this function.  It is not read inside the function body because
    the data dictionaries are already site-scoped by their loaders
    (``load_unit_periods`` / ``build_chronology``).  Reserved for a future
    refactor where loading would happen intra-function.
    """
    issues = []
    if not chrono:
        return issues
    id_to_us = _node_us_map(graph)
    seen = set()

    def span(us):
        return unit_span(unit_periods.get(us), chrono)

    for (s, t, et) in _strat_edges(graph):
        rel = _classify_relation(et)
        if rel is None:
            continue
        us_s, us_t = id_to_us.get(s), id_to_us.get(t)
        if not us_s or not us_t or us_s == us_t:
            continue
        if rel == "contemp":
            key = ("c", frozenset((us_s, us_t)))
            if key in seen:
                continue
            seen.add(key)
            sp_s, sp_t = span(us_s), span(us_t)
            if sp_s is None or sp_t is None:
                # dated + undated → cannot evaluate overlap; both undated → skip
                if sp_s is None and sp_t is None:
                    continue
                issues.append(Issue(
                    TEMPORAL_UNEVALUABLE, [us_s, us_t], False,
                    _t(lang, "s_temporal_uneval").format(
                        a=_utok(us_s, lang), b=_utok(us_t, lang))))
                continue
            if sp_s[1] < sp_t[0] or sp_t[1] < sp_s[0]:
                issues.append(Issue(
                    TEMPORAL_CONTEMPORANEITY, [us_s, us_t], False,
                    _t(lang, "s_temporal_contemp").format(
                        a=_utok(us_s, lang), pa=_periodo(us_s, unit_periods),
                        b=_utok(us_t, lang), pb=_periodo(us_t, unit_periods))))
            continue
        # order relation → normalize to (later, earlier)
        later, earlier = (us_s, us_t) if rel == "later" else (us_t, us_s)
        key = ("i", later, earlier)
        if key in seen:
            continue
        seen.add(key)
        sp_l, sp_e = span(later), span(earlier)
        if sp_l is None or sp_e is None:
            # only actionable if one side is dated (hint to date the other)
            if sp_l is None and sp_e is None:
                continue
            issues.append(Issue(
                TEMPORAL_UNEVALUABLE, [later, earlier], False,
                _t(lang, "s_temporal_uneval").format(
                    a=_utok(later, lang), b=_utok(earlier, lang))))
            continue
        if sp_l[1] <= sp_e[0]:   # later ends at or before earlier starts → inversion
            issues.append(Issue(
                TEMPORAL_INVERSION, [later, earlier], False,
                _t(lang, "s_temporal_inv").format(
                    a=_utok(later, lang), pa=_periodo(later, unit_periods),
                    b=_utok(earlier, lang), pb=_periodo(earlier, unit_periods))))
    return issues


# ---------------------------------------------------------------------------
# Task 4: solve_fixes (majority heuristic + target period)
# ---------------------------------------------------------------------------

def _build_adjacency(graph, id_to_us):
    """us -> list of (neighbor_us, role) where role describes us vs neighbor:
    'later' (us is later than nb), 'earlier', or 'contemp'."""
    adj = {}
    for (s, t, et) in _strat_edges(graph):
        rel = _classify_relation(et)
        if rel is None:
            continue
        us_s, us_t = id_to_us.get(s), id_to_us.get(t)
        if not us_s or not us_t or us_s == us_t:
            continue
        if rel == "contemp":
            adj.setdefault(us_s, []).append((us_t, "contemp"))
            adj.setdefault(us_t, []).append((us_s, "contemp"))
        else:
            later, earlier = (us_s, us_t) if rel == "later" else (us_t, us_s)
            adj.setdefault(later, []).append((earlier, "later"))
            adj.setdefault(earlier, []).append((later, "earlier"))
    return adj


def _violated(role, su, sn):
    """Return True when the candidate span *su* violates the constraint imposed
    by *role* with neighbor span *sn*.

    The boundary condition uses strict ordering (``<=``): periods that only
    touch at a single point are still considered non-overlapping and therefore
    still violating.  This ensures that ``_best_target_period`` picks a period
    that genuinely precedes/follows the neighbor rather than merely touching it.

    Examples:
      - role='later', su=(0,100), sn=(100,200) → su[1]=100 <= sn[0]=100 → True
        (period touching the neighbor's start is not "after" it)
      - role='later', su=(100,200), sn=(100,200) → 200 <= 100 → False  (same period OK)
    """
    if su is None or sn is None:
        return False
    if role == "later":
        return su[1] <= sn[0]
    if role == "earlier":
        return sn[1] <= su[0]
    if role == "contemp":
        return su[1] < sn[0] or sn[1] < su[0]
    return False


def _is_mono(us, unit_periods):
    p = unit_periods.get(us)
    return p is not None and bool(p[0]) and p[0] == p[2]


def _best_target_period(m, adj, work, chrono):
    """Pick the (periodo, fase) satisfying ALL of m's constraints against
    neighbors' CURRENT spans, with the smallest chronological shift. None if
    no candidate satisfies."""
    cur = unit_span(work.get(m), chrono)
    cur_ini = cur[0] if cur else None
    best, best_dist = None, None
    for (periodo, fase), (ci, cf) in chrono.items():
        if ci is None or cf is None:
            continue
        cand = (ci, cf)
        ok = True
        for (nb, role) in adj.get(m, ()):
            if _violated(role, cand, unit_span(work.get(nb), chrono)):
                ok = False
                break
        if not ok:
            continue
        dist = abs(ci - cur_ini) if cur_ini is not None else abs(ci)
        if best is None or dist < best_dist:
            best, best_dist = (periodo, fase), dist
    return best


def _set_fields_for(periodo, fase):
    return (("periodo_iniziale", periodo), ("fase_iniziale", fase),
            ("periodo_finale", periodo), ("fase_finale", fase))


def solve_fixes(issues, graph, chrono, unit_periods, *, sito):
    """Populate iss.edits (auto) where resolvable; leave suggestions otherwise.
    Greedy single pass: each accepted move updates an in-memory period map so
    later decisions see its effect. Mutates the Issue objects in place."""
    work = dict(unit_periods)
    id_to_us = _node_us_map(graph)
    adj = _build_adjacency(graph, id_to_us)

    def span_work(us):
        return unit_span(work.get(us), chrono)

    def conflict_score(us):
        return sum(1 for (nb, role) in adj.get(us, ())
                   if _violated(role, span_work(us), span_work(nb)))

    # Build set of contemp pairs from the adjacency map for gap-fill detection.
    # A TEMPORAL_UNEVALUABLE issue arising from a contemp edge (one side undated)
    # is gap-fillable: assign the undated unit the dated neighbour's period.
    contemp_pairs = frozenset(
        frozenset((us, nb))
        for us, neighbors in adj.items()
        for (nb, role) in neighbors
        if role == "contemp"
    )

    targetable = [i for i in issues
                  if i.kind in (TEMPORAL_INVERSION, TEMPORAL_CONTEMPORANEITY,
                                TEMPORAL_UNEVALUABLE)]
    targetable.sort(key=lambda i: -sum(conflict_score(u) for u in i.us_path))

    for iss in targetable:
        a, b = iss.us_path[0], iss.us_path[1]
        sp_a, sp_b = span_work(a), span_work(b)

        # gap-fill: one side undated, connected by a contemporaneity edge
        is_contemp_pair = frozenset((a, b)) in contemp_pairs
        if is_contemp_pair and (sp_a is None) != (sp_b is None):
            dated, undated = (a, b) if sp_a is not None else (b, a)
            dp = work.get(dated)
            if dp and dp[0]:
                work[undated] = (dp[0], dp[1], dp[0], dp[1])
                iss.kind = TEMPORAL_CONTEMPORANEITY
                iss.auto = True
                iss.edits = [Edit(us=undated,
                                  set_fields=_set_fields_for(dp[0], dp[1]))]
            continue

        if sp_a is None or sp_b is None:
            continue
        if iss.kind == TEMPORAL_UNEVALUABLE:
            continue                      # order-edge unevaluable, no fix
        ca, cb = conflict_score(a), conflict_score(b)
        if ca == cb:
            # Tie — but check if a prior move already resolved this inversion.
            # If neither unit violates the other any more, the issue was fixed
            # as a side effect; mark auto=True with an empty edits list.
            if iss.kind == TEMPORAL_INVERSION and not _violated("later", sp_a, sp_b):
                iss.auto = True
            continue
        m = a if ca > cb else b
        if not _is_mono(m, unit_periods):
            continue                      # multi-period -> suggestion
        target = _best_target_period(m, adj, work, chrono)
        if target is None:
            continue                      # no valid period -> suggestion
        periodo, fase = target
        work[m] = (periodo, fase, periodo, fase)
        iss.auto = True
        iss.edits = [Edit(us=m, set_fields=_set_fields_for(periodo, fase))]
