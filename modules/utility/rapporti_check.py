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
    _REL_INDEX_EDGE_TYPE,
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


# ---------------------------------------------------------------------------
# Localisation (report messages follow the QGIS UI language)
# ---------------------------------------------------------------------------
# Relationship WORDS come from pyArchInit's i18n RELATIONSHIPS table (all 10
# languages). The surrounding template phrases are provided for the Latin-
# script UI languages; any other language falls back to English (the
# relationship words stay localised regardless).
_EDGE_TYPE_TO_REL_INDEX = {et: i for i, et in enumerate(_REL_INDEX_EDGE_TYPE)}

_L = {
    "it": {
        "t_self_loop": "Self-loop (US in relazione con sé stessa)",
        "t_missing_reciprocity": "Reciprocità mancante (verrà creata)",
        "t_contradiction_redundant": "Contraddizione ridondante",
        "t_contradiction_ambiguous": "Contraddizione diretta (scelta manuale)",
        "t_cycle": "Ciclo stratigrafico (scelta manuale)",
        "t_illegal_connection": "Tipo relazione non valido (solo segnalazione)",
        "s_self": "{us} è in relazione con sé stessa",
        "s_recip": "Manca il reciproco su {b} per {a} (rapporto «{rel}»)",
        "s_contr": "Contraddizione: {a} «{lab1}» {b}  ⇄  {b} «{lab2}» {a} "
                   "— tieni una sola direzione, elimina l'altra",
        "s_cycle": "Ciclo: {chain} — spezza l'anello eliminando il rapporto errato",
        "s_illegal": "Tipo relazione non valido: {a} → {b}",
    },
    "en": {
        "t_self_loop": "Self-loop (US related to itself)",
        "t_missing_reciprocity": "Missing reciprocity (will be created)",
        "t_contradiction_redundant": "Redundant contradiction",
        "t_contradiction_ambiguous": "Direct contradiction (manual choice)",
        "t_cycle": "Stratigraphic cycle (manual choice)",
        "t_illegal_connection": "Invalid relationship type (report only)",
        "s_self": "{us} is related to itself",
        "s_recip": "Missing reciprocal on {b} for {a} (relationship “{rel}”)",
        "s_contr": "Contradiction: {a} “{lab1}” {b}  ⇄  {b} “{lab2}” {a} "
                   "— keep one direction, remove the other",
        "s_cycle": "Cycle: {chain} — break the loop by removing the wrong relationship",
        "s_illegal": "Invalid relationship type: {a} → {b}",
    },
    "de": {
        "t_self_loop": "Self-loop (US in Beziehung zu sich selbst)",
        "t_missing_reciprocity": "Fehlende Reziprozität (wird erstellt)",
        "t_contradiction_redundant": "Redundanter Widerspruch",
        "t_contradiction_ambiguous": "Direkter Widerspruch (manuelle Wahl)",
        "t_cycle": "Stratigraphischer Zyklus (manuelle Wahl)",
        "t_illegal_connection": "Ungültiger Beziehungstyp (nur Hinweis)",
        "s_self": "{us} steht in Beziehung zu sich selbst",
        "s_recip": "Fehlende Reziprozität bei {b} für {a} (Beziehung „{rel}“)",
        "s_contr": "Widerspruch: {a} „{lab1}“ {b}  ⇄  {b} „{lab2}“ {a} "
                   "— eine Richtung behalten, die andere entfernen",
        "s_cycle": "Zyklus: {chain} — die Schleife durch Entfernen der falschen "
                   "Beziehung auflösen",
        "s_illegal": "Ungültiger Beziehungstyp: {a} → {b}",
    },
    "es": {
        "t_self_loop": "Self-loop (US relacionada consigo misma)",
        "t_missing_reciprocity": "Reciprocidad ausente (se creará)",
        "t_contradiction_redundant": "Contradicción redundante",
        "t_contradiction_ambiguous": "Contradicción directa (elección manual)",
        "t_cycle": "Ciclo estratigráfico (elección manual)",
        "t_illegal_connection": "Tipo de relación no válido (solo aviso)",
        "s_self": "{us} está relacionada consigo misma",
        "s_recip": "Falta el recíproco en {b} para {a} (relación «{rel}»)",
        "s_contr": "Contradicción: {a} «{lab1}» {b}  ⇄  {b} «{lab2}» {a} "
                   "— conserva una dirección, elimina la otra",
        "s_cycle": "Ciclo: {chain} — rompe el bucle eliminando la relación errónea",
        "s_illegal": "Tipo de relación no válido: {a} → {b}",
    },
    "fr": {
        "t_self_loop": "Self-loop (US en relation avec elle-même)",
        "t_missing_reciprocity": "Réciprocité manquante (sera créée)",
        "t_contradiction_redundant": "Contradiction redondante",
        "t_contradiction_ambiguous": "Contradiction directe (choix manuel)",
        "t_cycle": "Cycle stratigraphique (choix manuel)",
        "t_illegal_connection": "Type de relation non valide (signalement)",
        "s_self": "{us} est en relation avec elle-même",
        "s_recip": "Réciproque manquant sur {b} pour {a} (relation «{rel}»)",
        "s_contr": "Contradiction : {a} «{lab1}» {b}  ⇄  {b} «{lab2}» {a} "
                   "— gardez une direction, supprimez l'autre",
        "s_cycle": "Cycle : {chain} — brisez la boucle en supprimant la relation "
                   "erronée",
        "s_illegal": "Type de relation non valide : {a} → {b}",
    },
    "pt": {
        "t_self_loop": "Self-loop (US relacionada consigo mesma)",
        "t_missing_reciprocity": "Reciprocidade ausente (será criada)",
        "t_contradiction_redundant": "Contradição redundante",
        "t_contradiction_ambiguous": "Contradição direta (escolha manual)",
        "t_cycle": "Ciclo estratigráfico (escolha manual)",
        "t_illegal_connection": "Tipo de relação inválido (apenas aviso)",
        "s_self": "{us} está relacionada consigo mesma",
        "s_recip": "Falta o recíproco em {b} para {a} (relação «{rel}»)",
        "s_contr": "Contradição: {a} «{lab1}» {b}  ⇄  {b} «{lab2}» {a} "
                   "— mantenha uma direção, remova a outra",
        "s_cycle": "Ciclo: {chain} — quebre o ciclo removendo a relação errada",
        "s_illegal": "Tipo de relação inválido: {a} → {b}",
    },
}


def _t(lang, key):
    """Localised template string (falls back to English)."""
    return _L.get(lang, _L["en"]).get(key) or _L["en"][key]


def kind_title(kind, lang="it"):
    """Localised group title for an issue *kind* (used by the report UI)."""
    return _t(lang, "t_" + kind)


def _unit_prefix(lang):
    try:
        from modules.utility.pyarchinit_i18n_stratigraphic import UNIT_TYPE_ABBREV
        return UNIT_TYPE_ABBREV.get(lang, UNIT_TYPE_ABBREV.get("en", ("US",)))[0]
    except Exception:
        return "US"


def _utok(us, lang):
    """US display token in the UI language, e.g. 'US 661' / 'SU 661' / 'SE 661'."""
    return f"{_unit_prefix(lang)} {us}"


def _rel_label(et, lang):
    """Localised rapporti word for an edge type (e.g. overlies → Copre / Covers)."""
    try:
        from modules.utility.pyarchinit_i18n_stratigraphic import RELATIONSHIPS
        terms = RELATIONSHIPS.get(lang) or RELATIONSHIPS.get("en")
    except Exception:
        terms = None
    idx = _EDGE_TYPE_TO_REL_INDEX.get(et)
    if terms is not None and idx is not None:
        return terms[idx]
    if terms is not None and et == "is_after":
        return terms[2]      # temporal precedence shown as "covers"
    if terms is not None and et == "is_before":
        return terms[3]      # "covered by"
    return et or "→"


def check_rapporti(graph, *, sito, lang="it", validate=True,
                   inverse_label=None) -> RapportiReport:
    """Detect rapporti inconsistencies. *lang* (2-letter QGIS UI locale)
    localises every issue ``summary``. Edit computation is in
    :func:`_fill_edits`."""
    rep = RapportiReport(sito=sito)
    edges = _strat_edges(graph)
    edge_set = {(s, t, et) for (s, t, et) in edges}

    # Direction lookup over ALL graph edges so cycle/contradiction summaries
    # can name the actual relationship of each step (overlies→Copre/Covers…).
    all_dir = {}
    for e in getattr(graph, "edges", None) or []:
        es = getattr(e, "edge_source", None)
        et2 = getattr(e, "edge_target", None)
        ety = getattr(e, "edge_type", None)
        if es and et2 and ety:
            all_dir.setdefault((es, et2), ety)

    def _step(x, y):
        ety = all_dir.get((x, y)) or all_dir.get((y, x))
        return _rel_label(ety, lang) if ety else "→"

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
        n = len(cyc)
        if n == 1:
            rep.issues.append(Issue(
                SELF_LOOP, us_path, True,
                _t(lang, "s_self").format(us=_utok(us_path[0], lang))))
        elif n == 2:
            rep.issues.append(Issue(
                CONTRADICTION_AMBIGUOUS, us_path, False,
                _t(lang, "s_contr").format(
                    a=_utok(us_path[0], lang), b=_utok(us_path[1], lang),
                    lab1=_step(cyc[0], cyc[1]), lab2=_step(cyc[1], cyc[0]))))
        else:
            # "US102 «Copre» US103 «Coperto da» US101 … US102"
            parts = [f"{_utok(us_real[i], lang)} «{_step(cyc[i], cyc[(i + 1) % n])}»"
                     for i in range(n)]
            chain = " ".join(parts) + f" {_utok(us_real[0], lang)}"
            rep.issues.append(Issue(
                CYCLE, us_path, False,
                _t(lang, "s_cycle").format(chain=chain)))

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
            _t(lang, "s_recip").format(
                a=_utok(a_us, lang), b=_utok(b_us, lang),
                rel=_rel_label(et, lang))))

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
                    _t(lang, "s_illegal").format(
                        a=_utok(_us_of(sn), lang), b=_utok(_us_of(tn), lang))
                    + f"  («{_rel_label(et, lang)}»)"))

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
