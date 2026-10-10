from __future__ import annotations
import pytest
from modules.utility import rapporti_check as RC


class _N:
    def __init__(self, nid, ut, rap=None, us=None, node_type="US"):
        self.node_id = nid
        self.name = nid
        self.node_type = node_type
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
    def find_node_by_id(self, nid):
        return next((n for n in self.nodes if n.node_id == nid), None)


# ---------------------------------------------------------------------------
# Task 1: detection
# ---------------------------------------------------------------------------

def test_detects_self_loop():
    g = _G([_N("a", "US", rap="[['copre','1','1','S']]", us="1")],
           [_E("a", "a", "overlies")])
    rep = RC.check_rapporti(g, sito="S")
    kinds = [i.kind for i in rep.issues]
    assert RC.SELF_LOOP in kinds


def test_synthetic_placeholder_excluded_from_reciprocity():
    """A real US related to a projector-synthesized placeholder (us=None,
    e.g. ``_synth_BR_654``) must NOT raise a missing-reciprocity issue — the
    fix would otherwise write a rapporto into a non-existent us_table row."""
    g = _G([_N("a", "US", rap="[['copre','2','1','S']]", us="1"),
            _N("b", "US")],   # us=None -> synthetic placeholder
           [_E("a", "b", "overlies")])
    rep = RC.check_rapporti(g, sito="S")
    assert not any(i.kind == RC.MISSING_RECIPROCITY for i in rep.issues)
    # And a self-loop on a synthetic node is not reported either.
    g2 = _G([_N("s", "US")], [_E("s", "s", "overlies")])
    rep2 = RC.check_rapporti(g2, sito="S")
    assert not any(i.kind == RC.SELF_LOOP for i in rep2.issues)


def test_detects_missing_reciprocity():
    # A covers B; B says nothing -> B is missing "covered by A"
    g = _G([_N("a", "US", rap="[['copre','2','1','S']]", us="1"),
            _N("b", "US", us="2")],
           [_E("a", "b", "overlies")])
    rep = RC.check_rapporti(g, sito="S")
    assert any(i.kind == RC.MISSING_RECIPROCITY for i in rep.issues)


def test_no_issue_when_reciprocity_present():
    g = _G([_N("a", "US", rap="[['copre','2','1','S']]", us="1"),
            _N("b", "US", rap="[['coperto da','1','1','S']]", us="2")],
           [_E("a", "b", "overlies"), _E("b", "a", "is_overlain_by")])
    rep = RC.check_rapporti(g, sito="S")
    assert not any(i.kind == RC.MISSING_RECIPROCITY for i in rep.issues)


# ---------------------------------------------------------------------------
# Task 2: edit computation
# ---------------------------------------------------------------------------

def _inv(label):
    from modules.utility.pyarchinit_i18n_stratigraphic import get_inverse_relationship
    return get_inverse_relationship(label)


def test_selfloop_edit_removes_entry():
    g = _G([_N("a", "US", rap="[['Copre','1','1','S']]", us="1")],
           [_E("a", "a", "overlies")])
    rep = RC.check_rapporti(g, sito="S")
    iss = next(i for i in rep.issues if i.kind == RC.SELF_LOOP)
    assert iss.auto and iss.edits
    e = iss.edits[0]
    assert e.us == "1" and ("Copre", "1", "1", "S") in e.remove


def test_missing_reciprocity_edit_creates_inverse():
    g = _G([_N("a", "US", rap="[['Copre','2','1','S']]", us="1"),
            _N("b", "US", us="2")],
           [_E("a", "b", "overlies")])
    rep = RC.check_rapporti(g, sito="S")
    iss = next(i for i in rep.issues if i.kind == RC.MISSING_RECIPROCITY)
    assert iss.auto and iss.edits
    e = iss.edits[0]
    # the inverse of "Copre" is "Coperto da", added to US 2 pointing at US 1
    assert e.us == "2"
    assert (_inv("Copre"), "1", "1", "S") in e.add


def test_english_reciprocity_localized():
    g = _G([_N("a", "SU", rap="[['Covered by','2','1','S']]", us="1"),
            _N("b", "SU", us="2")],
           [_E("a", "b", "is_overlain_by")])
    rep = RC.check_rapporti(g, sito="S")
    iss = next(i for i in rep.issues if i.kind == RC.MISSING_RECIPROCITY)
    e = iss.edits[0]
    assert (_inv("Covered by"), "1", "1", "S") in e.add  # -> "Covers"


# ---------------------------------------------------------------------------
# Task 3: apply + rollback
# ---------------------------------------------------------------------------

def _temp_db(tmp_path, rows):
    import sqlite3
    db = tmp_path / "r.sqlite"
    con = sqlite3.connect(db)
    con.execute("CREATE TABLE us_table (id_us INTEGER PRIMARY KEY, sito TEXT, "
                "us TEXT, area TEXT, unita_tipo TEXT, rapporti TEXT, node_uuid TEXT)")
    for i, (us, rap) in enumerate(rows, 1):
        con.execute("INSERT INTO us_table VALUES (?,?,?,?,?,?,?)",
                    (i, "S", us, "1", "US", rap, f"uuid-{us}"))
    con.commit(); con.close()
    return db


def test_apply_and_rollback(tmp_path):
    from pathlib import Path
    from s3dgraphy.sync._db_handle import DbHandle
    db = _temp_db(tmp_path, [("1", "[['Copre','2','1','S']]"), ("2", "[]")])
    handle = DbHandle.from_path(Path(str(db)))
    edits = [RC.Edit(us="2", add=(("Coperto da", "1", "1", "S"),))]
    token = RC.apply_edits(edits, handle)
    import sqlite3
    con = sqlite3.connect(db)
    got = con.execute("SELECT rapporti FROM us_table WHERE us='2'").fetchone()[0]
    assert "Coperto da" in got and "1" in got
    RC.rollback(token, handle)
    got2 = con.execute("SELECT rapporti FROM us_table WHERE us='2'").fetchone()[0]
    con.close()
    assert got2 == "[]"   # restored


# ---------------------------------------------------------------------------
# Regression: abuts reciprocity fix must write a round-trippable inverse
# (the "dialog claims 113 fixes but only ~6 stick" bug). The inverse of
# "abuts" is is_abutted_by; s3dgraphy lacked an English label for it, so the
# fix wrote "Supports" which parse_rapporti silently dropped → the reciprocal
# edge never formed and the issue re-appeared on every re-scan.
# ---------------------------------------------------------------------------

def test_abuts_reciprocity_fix_label_round_trips():
    from s3dgraphy.rapporti import parse_rapporti
    g = _G([_N("a", "US", rap="[['abuts','2','1','S']]", us="1"),
            _N("b", "US", us="2")],
           [_E("a", "b", "abuts")])
    rep = RC.check_rapporti(g, sito="S")
    recs = [i for i in rep.issues if i.kind == RC.MISSING_RECIPROCITY]
    assert recs and recs[0].auto and recs[0].edits, \
        "abuts missing-reciprocity must be auto-fixable"
    inv_label = recs[0].edits[0].add[0][0]
    parsed = parse_rapporti("[['%s','1','1','S']]" % inv_label)
    assert parsed and parsed[0][0] == "is_abutted_by", \
        "inverse label %r does not round-trip to is_abutted_by" % inv_label


def test_parse_rapporti_knows_multilingual_is_abutted_by():
    """The reciprocal of 'abuts' (is_abutted_by) must parse in every
    pyArchInit language — its canonical labels are the index-9 terms of the
    i18n RELATIONSHIPS table (EN 'Supports', IT 'Gli si appoggia',
    DE 'Wird gestützt von', EL 'Υποστηρίζει', PT 'Apoiado por', ...)."""
    from s3dgraphy.rapporti import parse_rapporti
    for label in ("Supports", "supports", "Gli si appoggia",
                  "Wird gestützt von", "Υποστηρίζει", "Apoiado por"):
        parsed = parse_rapporti("[['%s','1','1','S']]" % label)
        assert parsed and parsed[0][0] == "is_abutted_by", label


# ---------------------------------------------------------------------------
# Localized, directional summaries for cycles/contradictions (QGIS language).
# ---------------------------------------------------------------------------

def test_contradiction_summary_is_localized_and_directional():
    g = _G([_N("a", "US", rap="[['copre','2','1','S']]", us="1"),
            _N("b", "US", rap="[['copre','1','1','S']]", us="2")],
           [_E("a", "b", "overlies"), _E("b", "a", "overlies")])
    it = RC.check_rapporti(g, sito="S", lang="it")
    c = [i for i in it.issues if i.kind == RC.CONTRADICTION_AMBIGUOUS]
    assert c, "no contradiction detected"
    assert "Contraddizione" in c[0].summary and "Copre" in c[0].summary
    en = RC.check_rapporti(g, sito="S", lang="en")
    c2 = [i for i in en.issues if i.kind == RC.CONTRADICTION_AMBIGUOUS]
    assert "Contradiction" in c2[0].summary and "Covers" in c2[0].summary
    assert "SU 1" in c2[0].summary  # unit prefix follows language (US/SU)


def test_kind_title_localized_with_fallback():
    assert RC.kind_title(RC.CYCLE, "it").startswith("Ciclo")
    assert RC.kind_title(RC.CYCLE, "en").startswith("Stratigraphic cycle")
    assert RC.kind_title(RC.CYCLE, "zz") == RC.kind_title(RC.CYCLE, "en")


# ---------------------------------------------------------------------------
# Fix: apply_edits must write set_fields (period columns) to DB + rollback
# ---------------------------------------------------------------------------

def _apply_db(tmp_path):
    import sqlite3
    from pathlib import Path
    from s3dgraphy.sync._db_handle import DbHandle
    p = tmp_path / "apply.sqlite"
    c = sqlite3.connect(p)
    c.execute("CREATE TABLE us_table (sito TEXT, us TEXT, rapporti TEXT,"
              " periodo_iniziale TEXT, fase_iniziale TEXT,"
              " periodo_finale TEXT, fase_finale TEXT)")
    c.execute("INSERT INTO us_table VALUES ('S','US5','[]','1','1','1','1')")
    c.commit(); c.close()
    return DbHandle.from_path(p)


def test_apply_set_fields_writes_period_and_rolls_back(tmp_path):
    from sqlalchemy import text
    h = _apply_db(tmp_path)
    e = RC.Edit(us="US5", set_fields=(("periodo_iniziale", "3"),
                                      ("fase_iniziale", "1"),
                                      ("periodo_finale", "3"),
                                      ("fase_finale", "1")))
    tok = RC.apply_edits([e], h, sito="S")
    with h.engine.connect() as c:
        row = c.execute(text("SELECT periodo_iniziale, periodo_finale "
                             "FROM us_table WHERE us='US5'")).fetchone()
    assert row == ("3", "3"), f"expected ('3','3'), got {row}"
    RC.rollback(tok, h)
    with h.engine.connect() as c:
        row = c.execute(text("SELECT periodo_iniziale, periodo_finale "
                             "FROM us_table WHERE us='US5'")).fetchone()
    assert row == ("1", "1"), f"rollback failed, got {row}"


def test_apply_mixed_rapporti_and_fields(tmp_path):
    from sqlalchemy import text
    h = _apply_db(tmp_path)
    e = RC.Edit(us="US5", add=(("Copre", "7", "1", "S"),),
                set_fields=(("periodo_iniziale", "2"),))
    RC.apply_edits([e], h, sito="S")
    with h.engine.connect() as c:
        rap, pi = c.execute(text("SELECT rapporti, periodo_iniziale "
                                 "FROM us_table WHERE us='US5'")).fetchone()
    assert "Copre" in rap, f"rapporti not updated: {rap}"
    assert pi == "2", f"periodo_iniziale not updated: {pi}"


def test_set_fields_only_no_rapporti_unchanged(tmp_path):
    """When Edit has only set_fields (no add/remove), rapporti column must be
    left untouched — the old apply_edits always rewrote rapporti even when
    set_fields was the only change."""
    import sqlite3
    from sqlalchemy import text
    h = _apply_db(tmp_path)
    original_rap = "[]"
    e = RC.Edit(us="US5", set_fields=(("periodo_iniziale", "2"),))
    RC.apply_edits([e], h, sito="S")
    with h.engine.connect() as c:
        rap = c.execute(text("SELECT rapporti FROM us_table WHERE us='US5'")).scalar()
    assert rap == original_rap, (
        f"rapporti was rewritten when only set_fields was present: {rap!r}")


# ---------------------------------------------------------------------------
# La reciprocità si legge nelle SCHEDE, non negli archi (2026-10-10)
# ---------------------------------------------------------------------------
# Enzo: «il fix automatico dice corretti ma non applica i fix». Misurato sul
# sito di esempio: 81 problemi «manca il reciproco», e **tutti e 81** avevano
# il rapporto già scritto nella scheda. Il projector fonde una coppia
# reciproca in UN arco canonico — US1 «Copre 2» e US2 «Coperto da 1» danno un
# solo `overlies` — mentre il controllo cercava i due versi nel grafo, e il
# verso inverso non c'è mai. Il «fix» aggiungeva poi un doppione a quattro
# elementi di un rapporto già presente in forma corta, su 38 righe, a ogni
# clic. La reciprocità è una proprietà di quello che è SCRITTO.

def test_the_short_form_already_written_is_reciprocity():
    """Il caso che faceva 81 falsi positivi: la scheda di B porta il
    reciproco nella forma corta a due elementi, senza area né sito."""
    g = _G([_N("a", "US", rap="[['Copre','2']]", us="1"),
            _N("b", "US", rap="[['Coperto da','1']]", us="2")],
           [_E("a", "b", "overlies")])   # un arco solo: il projector fonde
    rep = RC.check_rapporti(g, sito="S")
    assert not any(i.kind == RC.MISSING_RECIPROCITY for i in rep.issues), \
        [i.summary for i in rep.issues]


def test_one_canonical_edge_is_not_a_missing_reciprocal():
    """Anche in forma lunga: quello che conta è che le due schede si
    rispondano, non che il grafo porti due archi."""
    g = _G([_N("a", "US", rap="[['Copre','2','1','S']]", us="1"),
            _N("b", "US", rap="[['Coperto da','1','1','S']]", us="2")],
           [_E("a", "b", "overlies")])
    rep = RC.check_rapporti(g, sito="S")
    assert not any(i.kind == RC.MISSING_RECIPROCITY for i in rep.issues)


def test_a_reciprocal_written_with_a_different_word_still_counts():
    """«Coperto da» e «Covered by» sono lo stesso rapporto: il confronto va
    fatto sul tipo di arco, non sulla parola."""
    g = _G([_N("a", "US", rap="[['Copre','2']]", us="1"),
            _N("b", "SU", rap="[['Covered by','1']]", us="2")],
           [_E("a", "b", "overlies")])
    rep = RC.check_rapporti(g, sito="S")
    assert not any(i.kind == RC.MISSING_RECIPROCITY for i in rep.issues)


def test_a_reciprocal_towards_another_unit_is_not_the_one_asked_for():
    """B risponde, ma a un'altra US: il reciproco manca lo stesso."""
    g = _G([_N("a", "US", rap="[['Copre','2']]", us="1"),
            _N("b", "US", rap="[['Coperto da','9']]", us="2"),
            _N("c", "US", us="9")],
           [_E("a", "b", "overlies")])
    rep = RC.check_rapporti(g, sito="S")
    assert any(i.kind == RC.MISSING_RECIPROCITY for i in rep.issues)


def test_apply_does_not_duplicate_a_relation_already_there(tmp_path):
    """Il doppione a quattro elementi di un rapporto già scritto in forma
    corta: `['Coperto da','1']` e `['Coperto da','1','1','S']` sono lo stesso
    rapporto, e appenderlo sporcava la scheda a ogni clic."""
    import sqlite3

    from s3dgraphy.sync._db_handle import _resolve_db_handle

    db = tmp_path / "x.sqlite"
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE us_table (id_us INTEGER PRIMARY KEY, "
                 "sito TEXT, area TEXT, us TEXT, unita_tipo TEXT, "
                 "rapporti TEXT, periodo_iniziale TEXT, fase_iniziale TEXT, "
                 "periodo_finale TEXT, fase_finale TEXT)")
    conn.execute("INSERT INTO us_table (sito, area, us, unita_tipo, rapporti) "
                 "VALUES ('S','1','2','US',\"[['Coperto da', '1']]\")")
    conn.commit(); conn.close()

    handle = _resolve_db_handle("sqlite:///%s" % db)
    RC.apply_edits([RC.Edit(us="2", add=(("Coperto da", "1", "1", "S"),))],
                   handle, sito="S")

    conn = sqlite3.connect(db)
    scritto = conn.execute(
        "SELECT rapporti FROM us_table WHERE us='2'").fetchone()[0]
    conn.close()
    import ast
    voci = [list(map(str, x)) for x in ast.literal_eval(scritto)]
    verso_1 = [v for v in voci if v[0] == "Coperto da" and v[1] == "1"]
    assert len(verso_1) == 1, "rapporto duplicato: %r" % voci
