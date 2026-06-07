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
    from modules.s3dgraphy.sync._db_handle import DbHandle
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
    from modules.s3dgraphy.sync.rapporti import parse_rapporti
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


def test_parse_rapporti_knows_english_is_abutted_by():
    from modules.s3dgraphy.sync.rapporti import parse_rapporti
    for label in ("supports", "Supports", "abutted by", "is abutted by"):
        parsed = parse_rapporti("[['%s','1','1','S']]" % label)
        assert parsed and parsed[0][0] == "is_abutted_by", label
