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
