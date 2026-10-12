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

def test_scan_accepts_the_localised_unit_types():
    """La sigla dell'unità stratigrafica è **tradotta**: US/USM in
    italiano, SU/WSU in inglese, SE/MSE in tedesco, ΣΜ/ΤΣΜ in greco
    (`UNIT_TYPE_ABBREV`). Il generatore guardava solo US e USM, quindi su
    un database non italiano non trovava **nessun** candidato: misurato
    sui dieci siti del database di esempio, 4 candidati sull'italiano e 0
    su ciascuno degli altri nove.
    """
    for sigla in ("SU", "WSU", "SE", "MSE", "UE", "UEM", "USZ",
                  "\u03a3\u039c", "\u03a4\u03a3\u039c"):
        assert len(scan_candidates([_rec(unita_tipo=sigla)])) == 1, sigla


def test_scan_inherits_all_areas_via_other_locations():
    c = scan_candidates([_rec(other_locations='["2","3"]')])[0]
    assert c.other_locations == '["2","3"]'


# ---------------------------------------------------------------------------
# Task 3: build_con_record + desired_rapporti (pure)
# ---------------------------------------------------------------------------
from modules.s3dgraphy.sync.continuity_generator import (
    build_con_record, desired_rapporti, con_us_code,
)
from modules.s3dgraphy.sync import continuity_label
from s3dgraphy.rapporti import parse_rapporti

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
    # madre row -> reverse label -> dalla dev43 la libreria lo legge come
    # il suo tipo, is_before, senza girare niente (come «Coperto da» →
    # is_overlain_by); a ripiegarlo su "CON is_after US" pensano i
    # consumatori (graph_projector, room/us_ops: is_before → is_after + swap)
    p_madre = parse_rapporti([madre_entry])
    assert p_madre == [("is_before", "CON_US5", "1", "S", False)]

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
from s3dgraphy.sync._db_handle import DbHandle
from modules.s3dgraphy.sync.continuity_generator import (
    load_site_records, load_existing_con, apply_plan,
)
from modules.s3dgraphy.sync import continuity_label
from s3dgraphy.rapporti import _coerce_to_list


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


# ---------------------------------------------------------------------------
# Anche i salti di FASE, quando il pannello lo chiede
# ---------------------------------------------------------------------------
# «Per generare la continuità con le US/USM che hanno periodo iniziale e
# finale cosa c'è bisogno di altro? non mi genera la continuità oppure ho
# capito io male» (Enzo, 12 ottobre 2026). Non aveva capito male: la
# regola guarda il **periodo** e ignora la fase, e nel suo database
# l'unica unità che si muoveva era una USM da 2/3 a 2/4 — stesso periodo,
# fase diversa. Una muratura che vive dalla fase 3 alla fase 4 sopravvive
# comunque, quindi la spunta «anche i salti di fase» del pannello la
# comprende. Resta **spenta** per difetto: un bottone già spedito non
# cambia da sé quello che scrive nei database di chi aggiorna.

def test_scan_ignores_a_phase_jump_by_default():
    righe = [_rec(periodo_iniziale="2", periodo_finale="2",
                  fase_iniziale="3", fase_finale="4")]
    assert scan_candidates(righe) == []


def test_scan_takes_a_phase_jump_when_asked():
    righe = [_rec(periodo_iniziale="2", periodo_finale="2",
                  fase_iniziale="3", fase_finale="4")]
    cands = scan_candidates(righe, include_phase=True)
    assert len(cands) == 1
    c = cands[0]
    assert (c.periodo_iniziale, c.fase_iniziale) == ("2", "3")
    assert (c.periodo_finale, c.fase_finale) == ("2", "4")


def test_a_unit_that_does_not_move_at_all_is_never_a_candidate():
    """La spunta allarga la regola, non la scioglie: stesso periodo e
    stessa fase vuol dire un'unità che non attraversa niente."""
    fermo = [_rec(periodo_iniziale="2", periodo_finale="2",
                  fase_iniziale="3", fase_finale="3")]
    assert scan_candidates(fermo) == []
    assert scan_candidates(fermo, include_phase=True) == []


def test_a_phase_jump_needs_both_phases():
    """Senza una delle due fasi non si sa se si muove: niente candidato."""
    for riga in (_rec(periodo_iniziale="2", periodo_finale="2",
                      fase_iniziale="3", fase_finale=None),
                 _rec(periodo_iniziale="2", periodo_finale="2",
                      fase_iniziale="", fase_finale="4")):
        assert scan_candidates([riga], include_phase=True) == [], riga


def test_the_period_jump_still_wins_with_the_checkbox_on():
    """Acceso o spento, un salto di periodo è sempre un candidato."""
    righe = [_rec()]      # 1/1 -> 3/2
    assert len(scan_candidates(righe)) == 1
    assert len(scan_candidates(righe, include_phase=True)) == 1


# ---------------------------------------------------------------------------
# La continuità è UNA per unità: una CON che c'è già si adotta, non si raddoppia
# ---------------------------------------------------------------------------
# «Perché ci sono due rombi con la stessa USM? La continuità dovrebbe
# essere unica» (Enzo, 12 ottobre 2026). Il generatore riconosceva la sua
# scheda **per nome** — `CON_<us>` — e una continuità scritta a mano con
# un altro codice (la `CON 500` del demo, con il rapporto `> 12`) non la
# vedeva: ne creava una seconda accanto e segnava la prima come orfana.
# La madre di una CON è l'unità che i suoi rapporti nominano, comunque
# si chiami la scheda; se c'è, si aggiorna quella e il nome resta suo.

from modules.s3dgraphy.sync.continuity_generator import (  # noqa: E402
    build_con_record, diff_continuity, madre_of_con,
)


def test_the_madre_of_a_con_is_the_unit_its_rapporti_name():
    assert madre_of_con({"rapporti": "[['>', '12']]"}) == "12"
    assert madre_of_con({"rapporti": [["Continuità successiva a", "12",
                                       "1", "S"]]}) == "12"
    assert madre_of_con({"rapporti": [["Continuity after", "7"],
                                      ["Continuity after", "7"]]}) == "7"


def test_a_con_that_names_two_units_has_no_madre():
    assert madre_of_con({"rapporti": [["Continuità successiva a", "12"],
                                      ["Continuità successiva a", "13"]]}) is None
    assert madre_of_con({"rapporti": ""}) is None
    assert madre_of_con({"rapporti": None}) is None


def _cand_12():
    return scan_candidates([_rec(us="12", unita_tipo="USM", periodo_iniziale="2",
                                 fase_iniziale="3", periodo_finale="2",
                                 fase_finale="4")], include_phase=True)[0]


def test_a_hand_made_continuity_is_adopted_not_duplicated():
    esistente = {"500": {"us": "500", "area": "1", "struttura": None,
                         "periodo_iniziale": "2", "fase_iniziale": "1",
                         "periodo_finale": "2", "fase_finale": "1",
                         "other_locations": None, "d_stratigrafica": "Continuity",
                         "descrizione": "", "rapporti": "[['>', '12']]"}}
    piano = diff_continuity(esistente, [build_con_record(_cand_12())])
    assert piano.to_create == []
    assert piano.orphan == []
    assert len(piano.to_update) == 1
    adottata = piano.to_update[0]
    assert adottata["us"] == "500"              # il nome resta il suo
    assert adottata["madre"] == "12"
    assert (adottata["periodo_iniziale"], adottata["fase_iniziale"],
            adottata["periodo_finale"], adottata["fase_finale"]) == ("2", "3", "2", "4")
    assert adottata["rapporti"][0][1] == "12"


def test_an_adopted_continuity_already_aligned_is_unchanged():
    d = build_con_record(_cand_12())
    gia = dict(d, us="500")
    piano = diff_continuity({"500": gia}, [d])
    assert piano.unchanged == ["500"] and not piano.to_update and not piano.to_create


def test_a_con_pointing_elsewhere_is_still_an_orphan():
    esistente = {"600": {"us": "600", "rapporti": "[['>', '99']]",
                         "area": "1", "periodo_iniziale": "1", "periodo_finale": "2"}}
    piano = diff_continuity(esistente, [build_con_record(_cand_12())])
    assert [d["us"] for d in piano.to_create] == ["CON_12"]
    assert piano.orphan == ["600"]


def test_the_name_still_wins_when_both_exist():
    """`CON_12` c'è già **e** c'è una CON a mano verso la 12: si aggiorna
    quella col nome, e l'altra resta un'orfana da decidere a mano —
    due continuità sono un errore da vedere, non da sciogliere da soli."""
    d = build_con_record(_cand_12())
    esistente = {"CON_12": dict(d),
                 "500": {"us": "500", "rapporti": "[['>', '12']]", "area": "1"}}
    piano = diff_continuity(esistente, [d])
    assert piano.unchanged == ["CON_12"]
    assert piano.orphan == ["500"]


def test_on_the_example_database_the_hand_made_con500_is_updated_not_doubled(tmp_path):
    """Sul demo, col salto di fase acceso: la USM 12 (2/3 → 2/2: nasce nel
    XV secolo e arriva alla prima metà del XVI) ha già la CON 500 scritta
    a mano con `> 12`. Dopo «Genera continuità» le CON del
    sito sono **una**, è la 500, con l'arco della madre e l'etichetta
    canonica; e la 12 la nomina **una volta sola**."""
    import ast
    import shutil
    import sqlite3
    from pathlib import Path
    from modules.s3dgraphy.sync.continuity_generator import generate_continuity
    from s3dgraphy.sync._db_handle import _resolve_db_handle
    origine = Path(__file__).resolve().parents[2] / "resources" / "dbfiles" / "pyarchinit_db.sqlite"
    copia = tmp_path / "demo.sqlite"
    shutil.copy2(origine, copia)
    sito = "Scavo archeologico"
    rep = generate_continuity(_resolve_db_handle("sqlite:///%s" % copia), sito,
                              include_phase=True)
    assert (rep.created, rep.updated) == (0, 1), rep
    con = sqlite3.connect(str(copia))
    righe = con.execute(
        "select us, periodo_iniziale, fase_iniziale, periodo_finale, fase_finale, "
        "rapporti from us_table where sito=? and unita_tipo='CON'", (sito,)).fetchall()
    assert len(righe) == 1, righe
    us, pi, fi, pf, ff, rapporti = righe[0]
    assert us == "500"
    assert (pi, fi, pf, ff) == ("2", "3", "2", "2")
    assert [r[1] for r in ast.literal_eval(rapporti)] == ["12"]
    madre = con.execute("select rapporti from us_table where sito=? and us='12' "
                        "and unita_tipo='USM'", (sito,)).fetchone()[0]
    verso_500 = [r for r in ast.literal_eval(madre) if r[1] == "500"]
    assert len(verso_500) == 1, madre
    assert verso_500[0][0] != "<", madre
