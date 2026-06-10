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

def test_no_inversion_touching_boundary():
    # Strict rule (spec §5): an inversion needs cron_finale(later) STRICTLY <
    # cron_iniziale(earlier). Adjacent periods that merely touch at one cron
    # point overlap and are NOT flagged. p1=(-100,0) touches p2=(0,100) at 0.
    # later=US5 in p1 (ends at 0), earlier=US7 in p2 (starts at 0): 0 < 0 False.
    g = _G([_N("a", us="US5"), _N("b", us="US7")], [_E("a", "b", "overlies")])
    up = {"US5": ("1", "1", "1", "1"), "US7": ("2", "1", "2", "1")}
    assert TC.detect_temporal(g, _CHRONO, up, sito="S", lang="it") == []
    # Same touching pair via an 'earlier' edge (is_overlain_by) — symmetric:
    # US7 is_overlain_by US5 → later=US5(p1), earlier=US7(p2) → still touching.
    g2 = _G([_N("a", us="US7"), _N("b", us="US5")],
            [_E("a", "b", "is_overlain_by")])
    assert TC.detect_temporal(g2, _CHRONO, up, sito="S", lang="it") == []
    # Contrast: a one-period GAP (p1 vs p3, 0 < 100) is strictly disjoint → flagged.
    up_gap = {"US5": ("1", "1", "1", "1"), "US7": ("3", "1", "3", "1")}
    iss = TC.detect_temporal(g, _CHRONO, up_gap, sito="S", lang="it")
    assert [i.kind for i in iss] == [TC.TEMPORAL_INVERSION]

def test_no_contemp_violation_touching_boundary():
    # Contemporaneity uses the same strict boundary: touching periods overlap,
    # so a contemp edge across a touching boundary is NOT a violation.
    g = _G([_N("a", us="US5"), _N("b", us="US7")],
           [_E("a", "b", "is_physically_equal_to")])
    up = {"US5": ("1", "1", "1", "1"), "US7": ("2", "1", "2", "1")}  # touch at 0
    assert TC.detect_temporal(g, _CHRONO, up, sito="S", lang="it") == []

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


# ---------------------------------------------------------------------------
# Task 4: solve_fixes (majority heuristic + target period)
# ---------------------------------------------------------------------------

def _mk(rels):
    """rels = list of (src_us, edge_type, tgt_us). Returns graph with one
    node per us."""
    us_set = {u for (s, _e, t) in rels for u in (s, t)}
    nodes = [_N(u, us=u) for u in us_set]
    edges = [_E(s, t, e) for (s, e, t) in rels]
    return _G(nodes, edges)

def test_solve_tie_leaves_suggestion():
    g = _mk([("US5", "overlies", "US7")])
    up = {"US5": ("1", "1", "1", "1"), "US7": ("3", "1", "3", "1")}
    iss = TC.detect_temporal(g, _CHRONO, up, sito="S", lang="it")
    TC.solve_fixes(iss, g, _CHRONO, up, sito="S")
    assert iss[0].auto is False and iss[0].edits == []  # 1 vs 1 conflict = tie

def test_solve_moves_majority_outlier():
    # US5 covers US7 and US8; US5 wrongly in period 1 (older) -> US5 is outlier
    g = _mk([("US5", "overlies", "US7"), ("US5", "overlies", "US8")])
    up = {"US5": ("1", "1", "1", "1"),
          "US7": ("3", "1", "3", "1"), "US8": ("3", "1", "3", "1")}
    iss = TC.detect_temporal(g, _CHRONO, up, sito="S", lang="it")
    TC.solve_fixes(iss, g, _CHRONO, up, sito="S")
    inv = [i for i in iss if i.kind == TC.TEMPORAL_INVERSION]
    assert inv and all(i.auto for i in inv)
    moved = inv[0].edits[0]
    assert moved.us == "US5"
    assert dict(moved.set_fields)["periodo_iniziale"] == "3"  # minimal move to >=3

def test_solve_skips_multiperiod_unit():
    # Local chrono with a real GAP (p2 ends at 50, p3 starts at 100) so the
    # multi-period span (-100,50) is STRICTLY before p3 (100,200) → a genuine
    # inversion under the strict-< rule, not a touching boundary.
    chrono = {("1", "1"): (-100, 0), ("2", "1"): (0, 50), ("3", "1"): (100, 200)}
    g = _mk([("CON_US5", "overlies", "US7"), ("CON_US5", "overlies", "US8")])
    up = {"CON_US5": ("1", "1", "2", "1"),    # spans periods -> not auto-movable
          "US7": ("3", "1", "3", "1"), "US8": ("3", "1", "3", "1")}
    iss = TC.detect_temporal(g, chrono, up, sito="S", lang="it")
    TC.solve_fixes(iss, g, chrono, up, sito="S")
    inv = [i for i in iss if i.kind == TC.TEMPORAL_INVERSION]
    assert inv and all(i.edits == [] for i in inv)  # suggestion only

def test_solve_gap_fill_contemporaneity():
    g = _mk([("US5", "is_bonded_to", "US9")])
    up = {"US5": ("2", "1", "2", "1"), "US9": ("", "", "", "")}
    iss = TC.detect_temporal(g, _CHRONO, up, sito="S", lang="it")
    TC.solve_fixes(iss, g, _CHRONO, up, sito="S")
    c = [i for i in iss if i.kind == TC.TEMPORAL_CONTEMPORANEITY][0]
    assert c.auto is True
    assert c.edits[0].us == "US9"
    assert dict(c.edits[0].set_fields)["periodo_iniziale"] == "2"


def test_build_adjacency_deduplicates_parallel_edges():
    """Parallel edges between the same US pair (e.g. 'overlies' AND 'cuts')
    must not produce duplicate (neighbor, role) entries — otherwise
    conflict_score would be inflated and tie-breaks could flip incorrectly."""
    # US5 overlies US7 AND cuts US7 (two edges between the same pair)
    g = _mk([("US5", "overlies", "US7"), ("US5", "cuts", "US7")])
    id_to_us = {n.node_id: n.attributes["us"] for n in g.nodes}
    adj = TC._build_adjacency(g, id_to_us)
    # US5 should see US7 exactly once (as 'later'), not twice
    us5_neighbors = adj.get("US5", [])
    us7_entries = [(nb, role) for (nb, role) in us5_neighbors if nb == "US7"]
    assert len(us7_entries) == 1, (
        f"expected 1 entry for (US7, later), got {us7_entries}")
    # Verify conflict_score is 1, not 2
    up = {"US5": ("1", "1", "1", "1"), "US7": ("3", "1", "3", "1")}
    iss = TC.detect_temporal(g, _CHRONO, up, sito="S", lang="it")
    TC.solve_fixes(iss, g, _CHRONO, up, sito="S")
    # With two issues (both parallel edges → same inversion), each with 1 vs 1
    # conflict after dedup → tie → suggestion (auto=False). With duplicates the
    # score would be 2 vs 1 → US5 would wrongly be moved.
    # But detect_temporal also deduplicates via seen set, so only 1 issue.
    assert len(iss) == 1, f"expected 1 issue (seen-dedup), got {len(iss)}"


def test_violated_touching_boundary():
    """_violated drives conflict_score and fix-acceptance; it must use the SAME
    strict boundary as detect_temporal so a touching pair is never counted as a
    conflict that detection left unflagged (and a touching period stays a valid
    fix target)."""
    # role='later': su must end >= neighbor start to overlap. Touching = OK.
    assert TC._violated("later", (-100, 0), (0, 100)) is False   # touch at 0
    assert TC._violated("later", (-100, -1), (0, 100)) is True   # strictly before
    assert TC._violated("later", (100, 200), (100, 200)) is False  # same period
    # role='earlier': symmetric. Touching = OK.
    assert TC._violated("earlier", (0, 100), (-100, 0)) is False  # touch at 0
    assert TC._violated("earlier", (1, 100), (-100, 0)) is True   # strictly after
    # role='contemp' was already strict; touching still counts as overlap = OK.
    assert TC._violated("contemp", (-100, 0), (0, 100)) is False
    assert TC._violated("contemp", (-100, -1), (0, 100)) is True
    # None spans never violate (undatable).
    assert TC._violated("later", None, (0, 100)) is False
    assert TC._violated("earlier", (0, 100), None) is False


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


# ---------------------------------------------------------------------------
# Task 6: Wire temporal_check into check_rapporti
# ---------------------------------------------------------------------------

from modules.utility import rapporti_check as RC


def test_check_rapporti_appends_temporal_when_chrono_given():
    g = _mk([("US5", "overlies", "US7")])
    up = {"US5": ("1", "1", "1", "1"), "US7": ("3", "1", "3", "1")}
    rep = RC.check_rapporti(g, sito="S", chrono=_CHRONO, unit_periods=up)
    assert any(i.kind == TC.TEMPORAL_INVERSION for i in rep.issues)


def test_check_rapporti_skips_temporal_without_chrono():
    g = _mk([("US5", "overlies", "US7")])
    rep = RC.check_rapporti(g, sito="S")   # no chrono -> backward compatible
    assert not any(i.kind == TC.TEMPORAL_INVERSION for i in rep.issues)


def test_check_rapporti_solve_fixes_majority_outlier_wired():
    """End-to-end: solve_fixes populates edits when called through check_rapporti.

    US5 overlies both US7 and US8 (both period 3); US5 is wrongly in period 1.
    Conflict score: US5=2 vs US7=1, US8=1 -> US5 is the majority outlier.
    solve_fixes must set auto=True and populate edits on the TEMPORAL_INVERSION
    issues, proving the wired path (not the isolated solve_fixes call) works.
    """
    g_majority = _mk([("US5", "overlies", "US7"), ("US5", "overlies", "US8")])
    up_majority = {
        "US5": ("1", "1", "1", "1"),
        "US7": ("3", "1", "3", "1"),
        "US8": ("3", "1", "3", "1"),
    }
    rep = RC.check_rapporti(
        g_majority, sito="S", chrono=_CHRONO, unit_periods=up_majority)
    assert any(
        i.kind == TC.TEMPORAL_INVERSION and i.auto
        for i in rep.issues
    ), "Expected at least one auto-fixed TEMPORAL_INVERSION from majority-outlier path"


def test_kind_title_localized():
    assert RC.kind_title(TC.TEMPORAL_INVERSION, "it")
    assert RC.kind_title(TC.TEMPORAL_INVERSION, "en")
