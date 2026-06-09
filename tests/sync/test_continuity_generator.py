# tests/sync/test_continuity_generator.py
from modules.s3dgraphy.sync.continuity_generator import (
    Candidate, scan_candidates,
)

def _rec(**kw):
    base = dict(sito="S", us="US5", unita_tipo="US", area="1",
                struttura="M1", periodo_iniziale="1", fase_iniziale="1",
                periodo_finale="3", fase_finale="2", other_locations=None)
    base.update(kw)
    return base

def test_scan_includes_period_jump():
    cands = scan_candidates([_rec()])
    assert len(cands) == 1
    c = cands[0]
    assert isinstance(c, Candidate)
    assert c.us == "US5" and c.periodo_iniziale == "1" and c.periodo_finale == "3"

def test_scan_excludes_same_period():
    assert scan_candidates([_rec(periodo_finale="1")]) == []

def test_scan_excludes_null_periods():
    assert scan_candidates([_rec(periodo_iniziale=None)]) == []
    assert scan_candidates([_rec(periodo_finale="")]) == []

def test_scan_excludes_non_us_usm_types():
    assert scan_candidates([_rec(unita_tipo="USV")]) == []
    assert scan_candidates([_rec(unita_tipo="CON", us="CON_US5")]) == []

def test_scan_inherits_all_areas_via_other_locations():
    c = scan_candidates([_rec(other_locations='["2","3"]')])[0]
    assert c.other_locations == '["2","3"]'


# ---------------------------------------------------------------------------
# Task 3: build_con_record + desired_rapporti (pure)
# ---------------------------------------------------------------------------
from modules.s3dgraphy.sync.continuity_generator import (
    build_con_record, desired_rapporti, con_us_code,
)
from modules.s3dgraphy.sync.rapporti import continuity_label, parse_rapporti

def test_con_us_code():
    assert con_us_code("US5") == "CON_US5"
    assert con_us_code("USM6") == "CON_USM6"

def test_build_con_record_fields():
    c = scan_candidates([_rec(other_locations='["2"]')])[0]
    rec = build_con_record(c, schedatore="enzo", lang="it")
    assert rec["us"] == "CON_US5"
    assert rec["unita_tipo"] == "CON"
    assert rec["sito"] == "S"
    assert rec["area"] == "1"
    assert rec["struttura"] == "M1"
    assert rec["other_locations"] == '["2"]'
    assert rec["periodo_iniziale"] == "1" and rec["periodo_finale"] == "3"
    assert rec["fase_iniziale"] == "1" and rec["fase_finale"] == "2"
    assert rec["d_stratigrafica"] == "Continuità"
    assert "US5" in rec["descrizione"] and "1" in rec["descrizione"]
    assert rec["schedatore"] == "enzo"
    # CON-side rapporti: forward continuity to the madre
    fwd = continuity_label("it", "forward")
    assert rec["rapporti"] == [[fwd, "US5", "1", "S"]]

def test_desired_rapporti_pair_directions():
    c = scan_candidates([_rec()])[0]
    con_entry, madre_entry = desired_rapporti(c, lang="it")
    # CON row -> forward -> CON is_after US (no swap)
    p_con = parse_rapporti([con_entry])
    assert p_con == [("is_after", "US5", "1", "S", False)]
    # madre row -> reverse -> swap -> still CON is_after US
    p_madre = parse_rapporti([madre_entry])
    assert p_madre == [("is_after", "CON_US5", "1", "S", True)]

def test_build_con_record_area_default():
    """area=None/empty must default to "1" consistently in both the
    record dict and the embedded rapporti entry — guards against the
    spatial mismatch where record["area"]=None but rapporti[0][2]="1"."""
    c = scan_candidates([_rec(area="")])[0]
    rec = build_con_record(c, schedatore="x", lang="it")
    # The record field must use the resolved default, not the raw empty value
    assert rec["area"] == "1", (
        "record['area'] should default to '1' when madre.area is empty"
    )
    # The rapporti entry must use the same resolved default
    assert rec["rapporti"][0][2] == "1", (
        "rapporti[0][2] (area) should match record['area'] == '1'"
    )


# ---------------------------------------------------------------------------
# Task 4: diff_continuity (pure, idempotent)
# ---------------------------------------------------------------------------
from modules.s3dgraphy.sync.continuity_generator import diff_continuity, Plan

def _desired_for(*recs):
    return [build_con_record(c, schedatore="x", lang="it")
            for c in scan_candidates(list(recs))]

def test_diff_creates_when_absent():
    desired = _desired_for(_rec())
    plan = diff_continuity({}, desired)
    assert isinstance(plan, Plan)
    assert [d["us"] for d in plan.to_create] == ["CON_US5"]
    assert plan.to_update == [] and plan.unchanged == [] and plan.orphan == []

def test_diff_unchanged_when_identical():
    desired = _desired_for(_rec())
    # existing CON identical to desired (same comparable fields)
    existing = {"CON_US5": dict(desired[0])}
    plan = diff_continuity(existing, desired)
    assert plan.unchanged == ["CON_US5"]
    assert plan.to_create == [] and plan.to_update == []

def test_diff_updates_when_span_changed():
    desired = _desired_for(_rec(periodo_finale="4"))   # span now 1..4
    existing = {"CON_US5": dict(_desired_for(_rec(periodo_finale="3"))[0])}
    plan = diff_continuity(existing, desired)
    assert [d["us"] for d in plan.to_update] == ["CON_US5"]

def test_diff_marks_orphan():
    # existing CON whose madre no longer jumps periods (no desired entry)
    existing = {"CON_US9": {"us": "CON_US9", "sito": "S"}}
    plan = diff_continuity(existing, [])
    assert plan.orphan == ["CON_US9"]

def test_diff_is_idempotent_second_pass():
    desired = _desired_for(_rec())
    # simulate state after first apply: existing == desired
    existing = {d["us"]: dict(d) for d in desired}
    plan = diff_continuity(existing, desired)
    assert plan.to_create == [] and plan.to_update == []
    assert plan.unchanged == ["CON_US5"]


def test_diff_dedup_duplicate_candidates():
    """If desired contains two entries with identical us key (e.g. from
    duplicate DB rows), diff_continuity must not emit both as to_create —
    the second should be silently dropped (first-seen wins)."""
    desired = _desired_for(_rec(), _rec())   # two identical records → same key
    # sanity: both have the same 'us' key
    assert desired[0]["us"] == desired[1]["us"] == "CON_US5"
    plan = diff_continuity({}, desired)
    assert len(plan.to_create) == 1, (
        "duplicate desired entries for the same us key must be deduped"
    )
    assert plan.to_create[0]["us"] == "CON_US5"


def test_norm_rapporti_includes_area_and_sito():
    """_norm_rapporti must include area and sito in the comparison tuple so
    that rapporti drift (different area/sito baked in) is detected as a
    change, not silently treated as unchanged."""
    from modules.s3dgraphy.sync.continuity_generator import _norm_rapporti

    entry_a = ["è continuità di", "US5", "1", "S"]
    entry_b = ["è continuità di", "US5", "2", "S"]   # area differs
    assert _norm_rapporti([entry_a]) != _norm_rapporti([entry_b]), (
        "_norm_rapporti must distinguish entries with different area"
    )

    entry_c = ["è continuità di", "US5", "1", "S"]
    entry_d = ["è continuità di", "US5", "1", "OTHER"]   # sito differs
    assert _norm_rapporti([entry_c]) != _norm_rapporti([entry_d]), (
        "_norm_rapporti must distinguish entries with different sito"
    )


def test_record_matches_detects_rapporti_area_drift():
    """_record_matches must return False when rapporti area inside the
    existing record differs from the desired (e.g. after a manual DB edit)."""
    from modules.s3dgraphy.sync.continuity_generator import _record_matches
    fwd = continuity_label("it", "forward")
    existing = {
        "sito": "S", "us": "CON_US5", "area": "1",
        "struttura": "M1", "periodo_iniziale": "1", "fase_iniziale": "1",
        "periodo_finale": "3", "fase_finale": "2", "other_locations": None,
        "d_stratigrafica": "Continuità",
        "descrizione": "Continuità di US5 dal periodo 1 al periodo 3",
        "rapporti": [[fwd, "US5", "999", "S"]],   # area baked in is "999"
    }
    desired = {
        "sito": "S", "us": "CON_US5", "area": "1",
        "struttura": "M1", "periodo_iniziale": "1", "fase_iniziale": "1",
        "periodo_finale": "3", "fase_finale": "2", "other_locations": None,
        "d_stratigrafica": "Continuità",
        "descrizione": "Continuità di US5 dal periodo 1 al periodo 3",
        "rapporti": [[fwd, "US5", "1", "S"]],     # correct area "1"
    }
    assert not _record_matches(existing, desired), (
        "_record_matches must detect drift when rapporti area differs"
    )


# ---------------------------------------------------------------------------
# Task 5: I/O — readers + apply_plan (DbHandle, SQLite integration)
# ---------------------------------------------------------------------------
import sqlite3
import pytest
from pathlib import Path
from modules.s3dgraphy.sync._db_handle import DbHandle
from modules.s3dgraphy.sync.continuity_generator import (
    load_site_records, load_existing_con, apply_plan,
)
from modules.s3dgraphy.sync.rapporti import continuity_label, _coerce_to_list


def _make_db(tmp_path: Path) -> DbHandle:
    p = tmp_path / "con_test.sqlite"
    con = sqlite3.connect(p)
    con.executescript(
        "CREATE TABLE us_table ("
        " id_us INTEGER PRIMARY KEY, sito TEXT, area TEXT, us TEXT,"
        " d_stratigrafica TEXT, descrizione TEXT, periodo_iniziale TEXT,"
        " fase_iniziale TEXT, periodo_finale TEXT, fase_finale TEXT,"
        " rapporti TEXT, schedatore TEXT, struttura TEXT, unita_tipo TEXT,"
        " other_locations TEXT, entity_uuid TEXT, node_uuid TEXT);")
    con.execute(
        "INSERT INTO us_table (id_us,sito,area,us,unita_tipo,"
        "periodo_iniziale,periodo_finale,struttura,rapporti) VALUES"
        " (1,'S','1','US5','US','1','3','M1','[]')")
    con.commit(); con.close()
    return DbHandle.from_path(p)


def test_apply_plan_creates_con_and_reciprocal(tmp_path):
    h = _make_db(tmp_path)
    recs = load_site_records(h, "S")
    from modules.s3dgraphy.sync.continuity_generator import (
        scan_candidates, build_con_record, diff_continuity)
    desired = [build_con_record(c, schedatore="enzo", lang="it")
               for c in scan_candidates(recs)]
    plan = diff_continuity(load_existing_con(h, "S"), desired)
    report = apply_plan(h, plan, "S", remove_orphans=False)
    assert report.created == 1
    # CON row exists with unita_tipo CON
    con_rows = load_existing_con(h, "S")
    assert "CON_US5" in con_rows
    # reciprocal written on madre US5
    with h.engine.connect() as c:
        from sqlalchemy import text
        rap = c.execute(text("SELECT rapporti FROM us_table WHERE us='US5'"
                             " AND sito='S'")).fetchone()[0]
    rev = continuity_label("it", "reverse")
    assert any(e[0] == rev and e[1] == "CON_US5"
               for e in _coerce_to_list(rap))


def test_apply_plan_idempotent_second_run(tmp_path):
    h = _make_db(tmp_path)
    from modules.s3dgraphy.sync.continuity_generator import generate_continuity
    r1 = generate_continuity(h, "S", schedatore="enzo", lang="it")
    assert r1.created == 1
    r2 = generate_continuity(h, "S", schedatore="enzo", lang="it")
    assert r2.created == 0 and r2.updated == 0


def test_apply_plan_removes_orphan_only_when_opted_in(tmp_path):
    h = _make_db(tmp_path)
    from sqlalchemy import text
    with h.engine.begin() as c:
        c.execute(text("INSERT INTO us_table (id_us,sito,area,us,unita_tipo,"
                       "periodo_iniziale,periodo_finale) VALUES"
                       " (2,'S','1','CON_US9','CON','1','3')"))
    from modules.s3dgraphy.sync.continuity_generator import generate_continuity
    r = generate_continuity(h, "S", schedatore="x", lang="it",
                            remove_orphans=False)
    assert "CON_US9" in load_existing_con(h, "S")     # kept
    r2 = generate_continuity(h, "S", schedatore="x", lang="it",
                             remove_orphans=True)
    assert "CON_US9" not in load_existing_con(h, "S")  # removed
    assert r2.orphans_removed == 1


def test_build_plan_smoke(tmp_path):
    h = _make_db(tmp_path)
    from modules.s3dgraphy.sync.continuity_generator import build_plan
    plan = build_plan(h, "S", schedatore="enzo", lang="it")
    assert [d["us"] for d in plan.to_create] == ["CON_US5"]


def test_orphan_delete_is_site_scoped(tmp_path):
    """Orphan DELETE must not touch identically-named CON rows in other sites.

    Regression guard for the critical multi-site bug: without AND sito=:sito
    in the DELETE, a CON_US9 orphan in site 'S' would silently delete
    CON_US9 in site 'S2' as well.
    """
    h = _make_db(tmp_path)
    from sqlalchemy import text
    from modules.s3dgraphy.sync.continuity_generator import generate_continuity
    with h.engine.begin() as c:
        # Orphan CON_US9 in site S (US9 has no period span → no candidate)
        c.execute(text("INSERT INTO us_table (id_us,sito,area,us,unita_tipo,"
                       "periodo_iniziale,periodo_finale) VALUES"
                       " (2,'S','1','CON_US9','CON','1','3')"))
        # Identically-named CON_US9 in a second site S2
        c.execute(text("INSERT INTO us_table (id_us,sito,area,us,unita_tipo,"
                       "periodo_iniziale,periodo_finale) VALUES"
                       " (3,'S2','1','CON_US9','CON','1','3')"))
    # Running generate_continuity for site S with remove_orphans=True
    # should remove S's CON_US9 but leave S2's intact
    generate_continuity(h, "S", schedatore="x", lang="it",
                        remove_orphans=True)
    # S's orphan must be gone
    assert "CON_US9" not in load_existing_con(h, "S"), (
        "CON_US9 in site S should have been removed as an orphan"
    )
    # S2's identically-named row must survive
    assert "CON_US9" in load_existing_con(h, "S2"), (
        "CON_US9 in site S2 must not be touched by site S orphan cleanup"
    )
