"""Stratigraphic-rapporti validation + conservative auto-fix (pyArchInit).

Qt-free application logic. Builds the site graph with GraphProjector, runs
s3dgraphy's validators (cycle detection + connection legality) plus a
reciprocity scan derived from the same stratigraphic edges, and emits
``Issue`` objects each carrying the exact ``rapporti``-column edits for its
fix. See docs/superpowers/specs/2026-06-06-rapporti-validation-autofix-design.md.
"""
from __future__ import annotations
from dataclasses import dataclass, field

from modules.s3dgraphy.sync.rapporti import (
    NON_RAPPORTI_EDGE_TYPES,
    RAPPORTI_TO_EDGE_TYPE,
    _coerce_to_list,
    strip_us_prefix,
)

# Issue kinds
SELF_LOOP = "self_loop"
MISSING_RECIPROCITY = "missing_reciprocity"
CONTRADICTION_REDUNDANT = "contradiction_redundant"   # auto
CONTRADICTION_AMBIGUOUS = "contradiction_ambiguous"   # manual
CYCLE = "cycle"                                        # manual
ILLEGAL_CONNECTION = "illegal_connection"             # report-only

#: Canonical edge-type inverse. Symmetric relations map to themselves.
_EDGE_TYPE_INVERSE = {
    "overlies": "is_overlain_by", "is_overlain_by": "overlies",
    "cuts": "is_cut_by", "is_cut_by": "cuts",
    "fills": "is_filled_by", "is_filled_by": "fills",
    "abuts": "is_abutted_by", "is_abutted_by": "abuts",
    "is_physically_equal_to": "is_physically_equal_to",
    "is_bonded_to": "is_bonded_to",
}


@dataclass(frozen=True)
class Edit:
    """One change to a single US's ``rapporti`` column. ``add``/``remove``
    hold ``(label, target_us, area, sito)`` 4-tuples."""
    us: str
    add: tuple = ()
    remove: tuple = ()


@dataclass
class Issue:
    kind: str
    us_path: list           # involved US numbers (1=self-loop, 2=contradiction, N=cycle)
    auto: bool              # True when the fix is unambiguous
    summary: str
    edits: list = field(default_factory=list)   # the fix (auto) OR suggested (manual)


@dataclass
class RapportiReport:
    sito: str
    issues: list = field(default_factory=list)


def _us_of(node):
    if node is None:
        return None
    a = getattr(node, "attributes", None) or {}
    return a.get("us") or strip_us_prefix(str(getattr(node, "name", "") or ""))


def _real_us(node):
    """STRICT real-US identity: the ``us`` attribute set by GraphProjector for
    an actual us_table row. Returns ``None`` for projector-synthesized
    placeholder nodes (e.g. ``_synth_BR_654`` targets, group/epoch nodes),
    which carry ``us=None`` — those must NOT drive a DB-writing fix."""
    if node is None:
        return None
    a = getattr(node, "attributes", None) or {}
    us = a.get("us")
    if us is None or str(us).strip() == "" or str(us).startswith("_synth"):
        return None
    return str(us)


def _strat_edges(graph):
    out = []
    for e in getattr(graph, "edges", None) or []:
        et = getattr(e, "edge_type", None)
        if not et or et in NON_RAPPORTI_EDGE_TYPES:
            continue
        s = getattr(e, "edge_source", None)
        t = getattr(e, "edge_target", None)
        if s and t:
            out.append((s, t, et))
    return out


def check_rapporti(graph, *, sito, validate=True, inverse_label=None) -> RapportiReport:
    """Detect rapporti inconsistencies. Edit computation is filled in by
    :func:`_fill_edits` (Task 2)."""
    rep = RapportiReport(sito=sito)
    edges = _strat_edges(graph)
    edge_set = {(s, t, et) for (s, t, et) in edges}

    # Cycles + self-loops (s3dgraphy SCC detector). Only report cycles whose
    # members are ALL real us_table-backed US nodes; skip any cycle that
    # threads a projector-synthesized placeholder (graph artifact, not a real
    # stratigraphic contradiction the user can act on).
    from s3dgraphy.diagnostics import detect_stratigraphic_cycles
    for cyc in detect_stratigraphic_cycles(graph):
        us_real = [_real_us(graph.find_node_by_id(x)) for x in cyc]
        if any(u is None for u in us_real):
            continue
        us_path = us_real
        if len(cyc) == 1:
            rep.issues.append(Issue(SELF_LOOP, us_path, True,
                                    f"US {us_path[0]} è in relazione con sé stessa"))
        elif len(cyc) == 2:
            rep.issues.append(Issue(CONTRADICTION_AMBIGUOUS, us_path, False,
                                    f"Contraddizione diretta {us_path[0]} ↔ {us_path[1]}"))
        else:
            rep.issues.append(Issue(CYCLE, us_path, False,
                                    "Ciclo: " + " → ".join(us_path + [us_path[0]])))

    # Missing reciprocity: for A→B(ET) with no B→A(inverse ET). ONLY between
    # two real us_table-backed US nodes — the fix writes a rapporto into the
    # target row, so a synthesized placeholder (us=None) must never be a
    # source or target (it has no DB row and would yield a bogus entry).
    for (s, t, et) in edges:
        inv = _EDGE_TYPE_INVERSE.get(et)
        if inv is None:
            continue
        if (t, s, inv) in edge_set:
            continue
        a_us = _real_us(graph.find_node_by_id(s))
        b_us = _real_us(graph.find_node_by_id(t))
        if a_us is None or b_us is None:
            continue
        rep.issues.append(Issue(
            MISSING_RECIPROCITY, [a_us, b_us], True,
            f"Manca il reciproco su US {b_us} per US {a_us}"))

    # Connection-type legality (report-only).
    if validate:
        from s3dgraphy.graph import Graph
        for (s, t, et) in edges:
            sn = graph.find_node_by_id(s)
            tn = graph.find_node_by_id(t)
            if sn is None or tn is None:
                continue
            if _real_us(sn) is None or _real_us(tn) is None:
                continue
            try:
                ok = Graph.validate_connection(
                    getattr(sn, "node_type", None),
                    getattr(tn, "node_type", None), et)
            except Exception:
                ok = True
            if not ok:
                rep.issues.append(Issue(
                    ILLEGAL_CONNECTION,
                    [str(_us_of(sn)), str(_us_of(tn))], False,
                    f"Tipo relazione non valido: {getattr(sn,'node_type',None)} "
                    f"--{et}--> {getattr(tn,'node_type',None)}"))

    _fill_edits(rep, graph, inverse_label=inverse_label)
    return rep


def _source_term(graph, src_id, target_us):
    """The source row's own rapporti label for target_us (capitalized)."""
    n = graph.find_node_by_id(src_id)
    a = getattr(n, "attributes", None) or {}
    for entry in _coerce_to_list(a.get("rapporti")):
        if isinstance(entry, (list, tuple)) and len(entry) >= 2:
            if str(entry[1]).strip() == str(target_us):
                lbl = str(entry[0]).strip()
                if lbl:
                    return lbl.capitalize(), entry
    return None, None


def _fill_edits(rep, graph, *, inverse_label=None):
    if inverse_label is None:
        from modules.utility.pyarchinit_i18n_stratigraphic import (
            get_inverse_relationship as inverse_label)
    by_us_node = {}
    for n in graph.nodes:
        u = _us_of(n)
        if u is not None:
            by_us_node.setdefault(str(u), n)

    for iss in rep.issues:
        if iss.kind == SELF_LOOP:
            us = iss.us_path[0]
            n = by_us_node.get(us)
            a = getattr(n, "attributes", None) or {}
            rem = tuple(tuple(str(x) for x in e)
                        for e in _coerce_to_list(a.get("rapporti"))
                        if isinstance(e, (list, tuple)) and len(e) >= 2
                        and str(e[1]).strip() == us)
            iss.edits = [Edit(us=us, remove=rem)] if rem else []
        elif iss.kind == MISSING_RECIPROCITY:
            a_us, b_us = iss.us_path
            # source term on A for B; build the inverse on B for A
            src_id = next((nid for nid in
                           (getattr(n, "node_id", None) for n in graph.nodes)
                           if str(_us_of(graph.find_node_by_id(nid))) == a_us), None)
            term, entry = _source_term(graph, src_id, b_us) if src_id else (None, None)
            if term is None:
                iss.auto = False
                iss.edits = []
                continue
            area = str(entry[2]) if len(entry) > 2 else "1"
            sito = str(entry[3]) if len(entry) > 3 else rep.sito
            inv = inverse_label(term) or term
            # Honesty guard: only auto-fix when the inverse label round-trips
            # to the correct inverse edge type. Otherwise parse_rapporti
            # silently drops it (the projector never builds the reciprocal
            # edge), so the fix could never satisfy reciprocity and the issue
            # re-appears on every re-scan — the bug where the dialog claimed
            # "113 fixes" but only ~6 stuck (abuts → "Supports", which had no
            # edge-type mapping). Surface non-round-tripping cases as manual.
            et = RAPPORTI_TO_EDGE_TYPE.get(str(term).lower())
            inv_et = _EDGE_TYPE_INVERSE.get(et) if et else None
            if (inv_et is None
                    or RAPPORTI_TO_EDGE_TYPE.get(str(inv).lower()) != inv_et):
                iss.auto = False
                iss.edits = []
                continue
            iss.edits = [Edit(us=b_us, add=((inv, a_us, area, sito),))]
        # CONTRADICTION_AMBIGUOUS / CYCLE / ILLEGAL_CONNECTION: no auto edits
    return rep


# ---------------------------------------------------------------------------
# Task 3: apply + rollback (backend-agnostic)
# ---------------------------------------------------------------------------
import ast as _ast
from dataclasses import dataclass as _dc


@_dc
class RollbackToken:
    sito: str
    snapshot: dict   # us -> original rapporti string


def _read_rapporti(conn, text, sito, us):
    row = conn.execute(
        text("SELECT rapporti FROM us_table WHERE sito = :s AND us = :u"),
        {"s": sito, "u": us}).fetchone()
    return (row[0] if row else None)


def apply_edits(edits, handle, *, sito=None) -> RollbackToken:
    from sqlalchemy import text
    # group edits by us
    by_us = {}
    for e in edits:
        by_us.setdefault(str(e.us), []).append(e)
    snapshot = {}
    with handle.engine.begin() as conn:
        for us, us_edits in by_us.items():
            cur = _read_rapporti(conn, text, sito, us) if sito else None
            if sito is None:
                row = conn.execute(text(
                    "SELECT sito, rapporti FROM us_table WHERE us = :u"),
                    {"u": us}).fetchone()
                row_sito = row[0] if row else None
                cur = row[1] if row else None
            else:
                row_sito = sito
            snapshot[us] = (row_sito, cur)
            lst = _coerce_to_list(cur)
            lst = [list(map(str, x)) for x in lst
                   if isinstance(x, (list, tuple))]
            for e in us_edits:
                for r in e.remove:
                    rr = list(map(str, r))
                    lst = [x for x in lst if x != rr]
                for ad in e.add:
                    aa = list(map(str, ad))
                    if aa not in lst:
                        lst.append(aa)
            conn.execute(text(
                "UPDATE us_table SET rapporti = :r WHERE sito = :s AND us = :u"),
                {"r": str(lst), "s": row_sito, "u": us})
    return RollbackToken(sito=sito or "", snapshot=snapshot)


def rollback(token, handle):
    from sqlalchemy import text
    with handle.engine.begin() as conn:
        for us, (row_sito, original) in token.snapshot.items():
            conn.execute(text(
                "UPDATE us_table SET rapporti = :r WHERE sito = :s AND us = :u"),
                {"r": original, "s": row_sito, "u": us})


# ---------------------------------------------------------------------------
# Task 4: import copy-mode — regenerate_node_uuids
# ---------------------------------------------------------------------------

def regenerate_node_uuids(graph) -> int:
    """Assign a fresh uuid7 to every node's ``attributes['node_uuid']`` so a
    copy-import does not match (and overwrite) existing DB rows. Returns the
    count changed."""
    from modules.s3dgraphy.sync.uuid7 import uuid7
    n = 0
    for node in getattr(graph, "nodes", None) or []:
        attrs = getattr(node, "attributes", None)
        if attrs is None:
            continue
        attrs["node_uuid"] = str(uuid7())
        n += 1
    return n
