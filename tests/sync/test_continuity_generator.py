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
