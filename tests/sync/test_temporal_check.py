"""Tests for modules.utility.temporal_check (temporal paradox detection)."""
import sqlite3
from pathlib import Path

from modules.utility import temporal_check as TC


def test_classify_relation():
    for et in ("overlies", "cuts", "fills", "abuts", "is_after"):
        assert TC._classify_relation(et) == "later"
    for et in ("is_overlain_by", "is_cut_by", "is_filled_by",
               "is_abutted_by", "is_before"):
        assert TC._classify_relation(et) == "earlier"
    for et in ("is_physically_equal_to", "is_bonded_to"):
        assert TC._classify_relation(et) == "contemp"
    assert TC._classify_relation("generic_connection") is None
    assert TC._classify_relation(None) is None


# ---------------------------------------------------------------------------
# Task 2: chronology readers + unit_span
# ---------------------------------------------------------------------------

def _db(tmp_path):
    p = tmp_path / "t.sqlite"
    c = sqlite3.connect(p)
    c.executescript(
        "CREATE TABLE periodizzazione_table (sito TEXT, periodo INTEGER,"
        " fase TEXT, cron_iniziale INTEGER, cron_finale INTEGER);"
        "CREATE TABLE us_table (sito TEXT, us TEXT, periodo_iniziale TEXT,"
        " fase_iniziale TEXT, periodo_finale TEXT, fase_finale TEXT);")
    c.execute("INSERT INTO periodizzazione_table VALUES ('S',1,'1',-100,0)")
    c.execute("INSERT INTO periodizzazione_table VALUES ('S',2,'1',0,100)")
    c.execute("INSERT INTO periodizzazione_table VALUES ('S',3,'1',100,200)")
    c.execute("INSERT INTO us_table VALUES ('S','US5','1','1','1','1')")
    c.execute("INSERT INTO us_table VALUES ('S','US7','3','1','3','1')")
    c.execute("INSERT INTO us_table VALUES ('S','US9',NULL,NULL,NULL,NULL)")
    c.commit(); c.close()
    from modules.s3dgraphy.sync._db_handle import DbHandle
    return DbHandle.from_path(p)


def test_build_chronology(tmp_path):
    chrono = TC.build_chronology(_db(tmp_path), "S")
    assert chrono[("1", "1")] == (-100, 0)
    assert chrono[("3", "1")] == (100, 200)


def test_load_unit_periods(tmp_path):
    up = TC.load_unit_periods(_db(tmp_path), "S")
    assert up["US5"] == ("1", "1", "1", "1")
    assert up["US9"] == ("", "", "", "")


def test_unit_span(tmp_path):
    chrono = TC.build_chronology(_db(tmp_path), "S")
    assert TC.unit_span(("1", "1", "1", "1"), chrono) == (-100, 0)
    assert TC.unit_span(("1", "1", "3", "1"), chrono) == (-100, 200)  # span both
    assert TC.unit_span(("", "", "", ""), chrono) is None
    assert TC.unit_span(("9", "1", "9", "1"), chrono) is None  # no such period


def test_unit_span_fase_fallback(tmp_path):
    chrono = TC.build_chronology(_db(tmp_path), "S")
    # blank fase -> aggregate over the periodo
    assert TC.unit_span(("2", "", "2", ""), chrono) == (0, 100)


# ---------------------------------------------------------------------------
# Task 3: detect_temporal + localized summaries
# ---------------------------------------------------------------------------

class _N:
    def __init__(self, nid, us=None, node_type="US"):
        self.node_id = nid; self.name = nid; self.node_type = node_type
        self.attributes = {"unita_tipo": "US"}
        if us is not None:
            self.attributes["us"] = us
class _E:
    def __init__(self, s, t, et):
        self.edge_source = s; self.edge_target = t; self.edge_type = et
class _G:
    def __init__(self, nodes, edges): self.nodes = nodes; self.edges = edges
    def find_node_by_id(self, nid):
        return next((n for n in self.nodes if n.node_id == nid), None)

_CHRONO = {("1", "1"): (-100, 0), ("2", "1"): (0, 100), ("3", "1"): (100, 200)}

def test_detect_inversion():
    # US5 (period 1, old) OVERLIES US7 (period 3, new) -> inversion
    g = _G([_N("a", us="US5"), _N("b", us="US7")], [_E("a", "b", "overlies")])
    up = {"US5": ("1", "1", "1", "1"), "US7": ("3", "1", "3", "1")}
    iss = TC.detect_temporal(g, _CHRONO, up, sito="S", lang="it")
    assert [i.kind for i in iss] == [TC.TEMPORAL_INVERSION]
    assert iss[0].us_path == ["US5", "US7"]   # [later, earlier]

def test_no_inversion_same_or_overlapping_period():
    g = _G([_N("a", us="US5"), _N("b", us="US7")], [_E("a", "b", "overlies")])
    up = {"US5": ("3", "1", "3", "1"), "US7": ("1", "1", "1", "1")}  # correct order
    assert TC.detect_temporal(g, _CHRONO, up, sito="S", lang="it") == []
    up2 = {"US5": ("2", "1", "2", "1"), "US7": ("2", "1", "2", "1")}  # same period
    assert TC.detect_temporal(g, _CHRONO, up2, sito="S", lang="it") == []

def test_detect_contemporaneity_disjoint():
    g = _G([_N("a", us="US5"), _N("b", us="US7")],
           [_E("a", "b", "is_physically_equal_to")])
    up = {"US5": ("1", "1", "1", "1"), "US7": ("3", "1", "3", "1")}
    iss = TC.detect_temporal(g, _CHRONO, up, sito="S", lang="it")
    assert [i.kind for i in iss] == [TC.TEMPORAL_CONTEMPORANEITY]

def test_unevaluable_when_one_dated_one_not():
    g = _G([_N("a", us="US5"), _N("b", us="US9")], [_E("a", "b", "overlies")])
    up = {"US5": ("1", "1", "1", "1"), "US9": ("", "", "", "")}
    iss = TC.detect_temporal(g, _CHRONO, up, sito="S", lang="it")
    assert [i.kind for i in iss] == [TC.TEMPORAL_UNEVALUABLE]

def test_unevaluable_contemp_one_dated_one_not():
    # contemporaneous pair where one unit has no period → unevaluable, not contemp
    g = _G([_N("a", us="US5"), _N("b", us="US9")],
           [_E("a", "b", "is_physically_equal_to")])
    up = {"US5": ("1", "1", "1", "1"), "US9": ("", "", "", "")}
    iss = TC.detect_temporal(g, _CHRONO, up, sito="S", lang="it")
    assert [i.kind for i in iss] == [TC.TEMPORAL_UNEVALUABLE]

def test_placeholder_excluded():
    g = _G([_N("a", us="US5"), _N("b")], [_E("a", "b", "overlies")])  # b us=None
    up = {"US5": ("1", "1", "1", "1")}
    assert TC.detect_temporal(g, _CHRONO, up, sito="S", lang="it") == []


def test_unevaluable_summary_is_generic_for_all_langs():
    """s_temporal_uneval summary must be factually correct for BOTH
    contemporaneous (is_physically_equal_to / is_bonded_to) and order
    (overlies / cuts / …) edge types — i.e. must NOT say 'order relationship'
    when the edge is a contemporaneity declaration."""
    up = {"US5": ("1", "1", "1", "1"), "US9": ("", "", "", "")}
    for lang in ("it", "en", "de", "es", "fr", "pt"):
        # contemp edge (is_physically_equal_to) with one undated unit
        g_c = _G([_N("a", us="US5"), _N("b", us="US9")],
                 [_E("a", "b", "is_physically_equal_to")])
        iss_c = TC.detect_temporal(g_c, _CHRONO, up, sito="S", lang=lang)
        assert len(iss_c) == 1, f"[{lang}] contemp: expected 1 issue"
        assert iss_c[0].kind == TC.TEMPORAL_UNEVALUABLE
        # The summary must NOT imply an ordering relation
        summ_c = iss_c[0].summary.lower()
        assert "order" not in summ_c, (
            f"[{lang}] contemp summary implies ordering: {iss_c[0].summary!r}")
        assert "ordine" not in summ_c, (
            f"[{lang}] contemp summary implies ordering: {iss_c[0].summary!r}")
        assert "ordnung" not in summ_c, (
            f"[{lang}] contemp summary implies ordering: {iss_c[0].summary!r}")
        assert "orden" not in summ_c, (
            f"[{lang}] contemp summary implies ordering: {iss_c[0].summary!r}")
        assert "ordre" not in summ_c, (
            f"[{lang}] contemp summary implies ordering: {iss_c[0].summary!r}")
        # order edge (overlies) with one undated unit → same kind, also generic
        g_o = _G([_N("a", us="US5"), _N("b", us="US9")],
                 [_E("a", "b", "overlies")])
        iss_o = TC.detect_temporal(g_o, _CHRONO, up, sito="S", lang=lang)
        assert len(iss_o) == 1, f"[{lang}] order: expected 1 issue"
        assert iss_o[0].kind == TC.TEMPORAL_UNEVALUABLE
