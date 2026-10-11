"""La verifica cronologica sul database di esempio: i numeri, non le opinioni.

Le quattro categorie si provano su righe costruite a mano in
`test_chronology_check.py`. Qui si prova che su un database vero trovano
quello che c'è — e che una seconda verifica non ripresenta quello che la
prima ha corretto.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
_EXT_LIBS = str(_ROOT / "ext_libs")
if _EXT_LIBS in sys.path:
    sys.path.remove(_EXT_LIBS)
sys.path.insert(0, _EXT_LIBS)

from modules.utility import chronology_check as CC
from modules.utility import rapporti_check as RC

ITALIANO = "Scavo archeologico"
TRADOTTO = "Archaeological Excavation"


@pytest.fixture()
def handle(tmp_path):
    """Una copia del database di esempio: l'originale non si apre mai in
    scrittura — il QGIS di Enzo lo tiene aperto in WAL."""
    from s3dgraphy.sync._db_handle import DbHandle
    sorgente = _ROOT / "resources" / "dbfiles" / "pyarchinit_db.sqlite"
    if not sorgente.exists():
        pytest.fail("il database di esempio manca: %s" % sorgente)
    copia = tmp_path / "db.sqlite"
    shutil.copy(sorgente, copia)
    return DbHandle.from_path(copia)


def _per_kind(handle, sito):
    periods, units = CC.load_chronology_rows(handle, sito)
    issues = CC.check_chronology(periods, units, sito=sito)
    out = {}
    for i in issues:
        out.setdefault(i.kind, []).append(i)
    return out


#: Quante righe si sporcano quando a un test serve un disallineamento.
QUANTE_SPORCHE = 6


def _sporca(handle, sito: str) -> int:
    """Scrive una datazione sbagliata su alcune US, e dice su quante.

    I test qui sotto hanno bisogno di un disallineamento da correggere. Il
    database di esempio non ce l'ha più — dall'11 ottobre 2026 esce pulito,
    e il test qui sopra è lì per non lasciarlo tornare indietro — quindi
    ognuno si fa il **proprio** materiale nella propria copia. È meglio
    così: prima la prova dipendeva da un difetto che qualcuno poteva
    correggere, e correggendolo faceva cadere test che non parlavano di lui.
    """
    from sqlalchemy import text
    with handle.engine.begin() as c:
        righe = c.execute(text(
            "SELECT us FROM us_table WHERE sito = :s"
            "   AND COALESCE(datazione, '') <> ''"
            " ORDER BY CAST(us AS INTEGER) LIMIT :n"),
            {"s": sito, "n": QUANTE_SPORCHE}).fetchall()
        for (us,) in righe:
            c.execute(text(
                "UPDATE us_table SET datazione = 'Datazione da correggere'"
                " WHERE sito = :s AND us = :u"), {"s": sito, "u": us})
    return len(righe)


def test_the_example_database_ships_without_chronology_warnings(handle):
    """Il database di esempio esce **pulito**, su tutte e dieci le lingue.

    Prima portava, per sito, due sovrapposizioni — due fasi «rec» che
    duplicavano gli anni di due fasi vere — e i disallineamenti di datazione:
    tredici sull'italiano e cinquantuno su ciascun sito tradotto, dove la
    periodizzazione era tradotta e la datazione nella scheda era rimasta in
    italiano. Un utente che apriva il demo e premeva «Verifica rapporti»
    trovava gli errori del demo, non i propri.
    """
    from sqlalchemy import text
    with handle.engine.connect() as c:
        siti = [r[0] for r in c.execute(text(
            "SELECT DISTINCT sito FROM periodizzazione_table ORDER BY sito"))]
    assert len(siti) >= 10, siti
    sporchi = {}
    for sito in siti:
        per_kind = _per_kind(handle, sito)
        if per_kind:
            sporchi[sito] = {k: len(v) for k, v in per_kind.items()}
    assert not sporchi, sporchi


def test_applying_the_automatic_fixes_empties_the_category(handle):
    """Una seconda verifica non ripresenta quello che la prima ha corretto."""
    quante = _sporca(handle, ITALIANO)
    assert quante == QUANTE_SPORCHE, "il materiale della prova"
    prima = _per_kind(handle, ITALIANO)["datazione_mismatch"]
    assert len(prima) == quante, [i.summary for i in prima[:3]]
    edits = [e for iss in prima for e in iss.edits]
    assert len(edits) == quante
    RC.apply_edits(edits, handle, sito=ITALIANO)
    dopo = _per_kind(handle, ITALIANO)
    assert dopo.get("datazione_mismatch", []) == []


def test_the_summary_shows_both_texts(handle):
    """L'anteprima è l'unico punto in cui si vede cosa si sta per
    riscrivere: ci devono essere il testo della scheda e quello della fase."""
    _sporca(handle, ITALIANO)
    issues = _per_kind(handle, ITALIANO)["datazione_mismatch"]
    assert issues
    con_entrambi = [i for i in issues
                    if "Datazione da correggere" in i.summary]
    assert con_entrambi, [i.summary for i in issues[:3]]
    # e il testo della fase, che è quello che ci finirà dentro
    assert any("secolo" in i.summary or "Età" in i.summary for i in issues), \
        [i.summary for i in issues[:3]]


def test_the_fix_touches_only_its_own_site(handle):
    """La verifica è per sito, così non si riscrivono dieci siti in un colpo.

    Si sporcano **entrambi** i siti e si corregge solo l'italiano: le righe
    del sito tradotto devono restare sporche **identiche**. Si confrontano i
    valori, non i conteggi — tutte le US esistono in ogni sito, e una fuga
    scriverebbe il testo italiano sulle righe dell'altro lasciando il
    conteggio dei disallineamenti dov'era.
    """
    from sqlalchemy import text

    def righe_tradotte():
        with handle.engine.connect() as c:
            return c.execute(text(
                "SELECT us, datazione FROM us_table WHERE sito = :s "
                "ORDER BY us"), {"s": TRADOTTO}).fetchall()

    _sporca(handle, ITALIANO)
    _sporca(handle, TRADOTTO)
    prima = righe_tradotte()
    assert prima, "il sito tradotto non ha righe: la prova non direbbe niente"
    edits = [e for iss in _per_kind(handle, ITALIANO)["datazione_mismatch"]
             for e in iss.edits]
    assert edits, "senza correzioni non si proverebbe nessuna fuga"
    RC.apply_edits(edits, handle, sito=ITALIANO)
    assert righe_tradotte() == prima


def test_the_rollback_puts_the_site_back(handle):
    """E l'annulla rimette i valori di prima, non soltanto il conteggio."""
    from sqlalchemy import text

    def righe_italiane():
        with handle.engine.connect() as c:
            return c.execute(text(
                "SELECT us, datazione FROM us_table WHERE sito = :s "
                "ORDER BY us"), {"s": ITALIANO}).fetchall()

    quante = _sporca(handle, ITALIANO)
    prima = righe_italiane()
    edits = [e for iss in _per_kind(handle, ITALIANO)["datazione_mismatch"]
             for e in iss.edits]
    token = RC.apply_edits(edits, handle, sito=ITALIANO)
    # L'apply ha davvero scritto: senza questa prova, un apply che non fa
    # niente farebbe passare l'annulla senza averlo esercitato.
    assert _per_kind(handle, ITALIANO).get("datazione_mismatch", []) == []
    assert righe_italiane() != prima
    RC.rollback(token, handle)
    assert righe_italiane() == prima
    assert len(_per_kind(handle, ITALIANO)["datazione_mismatch"]) == quante


# ---------------------------------------------------------------------------
# Un database di prova costruito da codice (2026-10-11)
# ---------------------------------------------------------------------------
# Il database di esempio ha un'area sola, nessuna cronologia rovesciata e
# soltanto sovrapposizioni identiche. Il generatore in
# tests/fixtures/realistic_site_db.py costruisce i casi che mancano; accanto a
# ogni riga c'è scritto perché esiste. Casi 4, 5, 6 e 7.

sys.path.insert(0, str(_ROOT / "tests" / "fixtures"))
import realistic_site_db as RSD  # noqa: E402


@pytest.fixture()
def scavo(tmp_path):
    """Lo scavo realistico: la maniglia sul file e l'URL."""
    from s3dgraphy.sync._db_handle import DbHandle
    url = RSD.build_realistic_site_db(tmp_path)
    return DbHandle.from_path(tmp_path / "db.sqlite"), url


def _issues(handle, sito=RSD.SITO):
    periods, units = CC.load_chronology_rows(handle, sito)
    out = {}
    for i in CC.check_chronology(periods, units, sito=sito):
        out.setdefault(i.kind, []).append(i)
    return out


def test_generated_site_dating_cases_are_reported_on_the_right_rows(scavo):
    """Tre schede, due avvisi.

    - US 20: la `datazione` dice «XII secolo», la fase 4/1 «Prima fase
      dell'XI secolo» -> avviso;
    - US 21: `datazione` **vuota**, la fase ne ha una -> avviso (una scheda
      vuota con la fonte piena è un disallineamento da riempire);
    - US 22: la fase 8/1 ha la `datazione_estesa` **vuota** e la scheda è
      piena -> **nessun** avviso: una fonte vuota non svuota mai una scheda.
    """
    mismatches = _issues(scavo[0])["datazione_mismatch"]
    per_us = {i.us_path[0]: i for i in mismatches}
    assert sorted(per_us) == ["20", "21"], sorted(per_us)
    for us in ("20", "21"):
        (e,) = per_us[us].edits
        assert e.set_fields == (("datazione", "Prima fase dell'XI secolo"),)
        assert e.target == ("us_table", {"us": us, "area": "1",
                                         "unita_tipo": "US"})
        assert per_us[us].auto is True
    assert "XII secolo" in per_us["20"].summary
    assert "—" in per_us["21"].summary          # la scheda vuota si legge «—»


def test_generated_site_an_empty_source_never_blanks_the_filled_sheet(scavo):
    """La US 22 sta nella fase 8/1, senza `datazione_estesa`: applicare tutte
    le correzioni automatiche non deve toccarle la datazione."""
    from sqlalchemy import text
    handle, _ = scavo
    edits = [e for i in _issues(handle)["datazione_mismatch"] for e in i.edits]
    RC.apply_edits(edits, handle, sito=RSD.SITO)
    with handle.engine.connect() as c:
        dat = dict(c.execute(text(
            "SELECT us, datazione FROM us_table WHERE sito = :s"),
            {"s": RSD.SITO}).fetchall())
    assert dat["22"] == "Età moderna"
    assert dat["20"] == dat["21"] == "Prima fase dell'XI secolo"
    assert "datazione_mismatch" not in _issues(handle)


def test_generated_site_a_dating_fix_touches_only_its_area(scavo):
    """Identità di riga a quattro colonne, sulla datazione.

    Si rovina la datazione della US 1 **dell'area 2** (la US 1 c'è in tutte e
    due le aree, con date diverse): l'avviso deve nominare l'area 2, la
    correzione deve scrivere quella riga sola, e l'annulla rimetterla.
    """
    from sqlalchemy import text
    handle, _ = scavo

    def date():
        with handle.engine.connect() as c:
            return dict(((a, u), d) for a, u, d in c.execute(text(
                "SELECT area, us, datazione FROM us_table WHERE sito = :s"),
                {"s": RSD.SITO}).fetchall())

    with handle.engine.begin() as c:
        c.execute(text("UPDATE us_table SET datazione = 'sbagliata' WHERE "
                       "sito = :s AND area = '2' AND us = '1'"), {"s": RSD.SITO})
    prima = date()
    nuovi = [i for i in _issues(handle)["datazione_mismatch"]
             if i.us_path == ["1"]]
    assert len(nuovi) == 1
    (e,) = nuovi[0].edits
    assert e.target == ("us_table", {"us": "1", "area": "2",
                                     "unita_tipo": "US"})
    assert e.set_fields == (("datazione", "Fine XIII - XIV secolo"),)

    token = RC.apply_edits([e], handle, sito=RSD.SITO)
    dopo = date()
    assert dopo[("2", "1")] == "Fine XIII - XIV secolo"
    assert [k for k in prima if prima[k] != dopo[k]] == [("2", "1")]
    RC.rollback(token, handle)
    assert date() == prima


def test_generated_site_bc_years_without_the_minus_are_proposed_as_negation(scavo):
    """1650 -> 1450, tutt'e due positivi, è un'Età del Bronzo battuta senza il
    meno. La proposta è la **negazione** (-1650, -1450), mai pre-spuntata
    (`auto` falso): scambiare i due anni la porterebbe nel 1450-1650 d.C."""
    rovesciate = {i.us_path[0]: i for i in _issues(scavo[0])["epoch_reversed"]}
    iss = rovesciate["2/1"]
    assert iss.auto is False
    (e,) = iss.edits
    assert e.set_fields == (("cron_iniziale", -1650), ("cron_finale", -1450))
    assert e.target == ("periodizzazione_table", {"periodo": "2", "fase": "1"})


def test_generated_site_a_reversed_pair_with_a_negative_year_is_swapped(scavo):
    """-100 -> -300: un anno è già negativo, il segno non manca. Negare
    porterebbe il periodo nell'era sbagliata, quindi la proposta è lo
    **scambio** (-300, -100)."""
    iss = {i.us_path[0]: i for i in _issues(scavo[0])["epoch_reversed"]}["3/1"]
    assert iss.auto is False
    (e,) = iss.edits
    assert e.set_fields == (("cron_iniziale", -300), ("cron_finale", -100))


def test_generated_site_a_correct_negative_pair_is_not_reported(scavo):
    """-1650 -> -1450 è un'Età del Bronzo scritta bene: nessun avviso di
    cronologia rovesciata, e le due rovesciate sono esattamente due."""
    rovesciate = _issues(scavo[0])["epoch_reversed"]
    assert sorted(i.us_path[0] for i in rovesciate) == ["2/1", "3/1"]
    tutti = [p for lista in _issues(scavo[0]).values() for i in lista
             for p in i.us_path]
    assert "1/1" not in tutti


def test_generated_site_the_identical_overlap_has_no_proposal_the_partial_has(scavo):
    """Due sovrapposizioni, due storie diverse.

    4/1 e 4/2 hanno lo stesso intervallo (1000-1100): niente restringimento
    possibile, quindi nessuna proposta. 5/1 (1200-1300) e 5/2 (1250-1400) si
    intersecano a metà: la proposta alza l'inizio della più recente a 1301.
    """
    per_coppia = {tuple(i.us_path): i for i in _issues(scavo[0])["epoch_overlap"]}
    assert sorted(per_coppia) == [("4/1", "4/2"), ("5/1", "5/2")]

    identica = per_coppia[("4/1", "4/2")]
    assert identica.edits == [] and identica.auto is False

    parziale = per_coppia[("5/1", "5/2")]
    assert parziale.auto is False
    (e,) = parziale.edits
    assert e.set_fields == (("cron_iniziale", 1301),)
    assert e.target == ("periodizzazione_table", {"periodo": "5", "fase": "2"})


def test_generated_site_applying_the_partial_proposal_closes_that_overlap_only(scavo):
    """La proposta, applicata, chiude la sua sovrapposizione e lascia
    l'identica: senza questa prova l'asserzione sopra potrebbe passare su una
    proposta che non chiude niente."""
    handle, _ = scavo
    (parziale,) = [i for i in _issues(handle)["epoch_overlap"] if i.edits]
    RC.apply_edits(parziale.edits, handle, sito=RSD.SITO)
    rimaste = _issues(handle)["epoch_overlap"]
    assert [tuple(i.us_path) for i in rimaste] == [("4/1", "4/2")]


def test_generated_site_without_us_rows_gives_no_chronology_issue(scavo):
    """Caso 7, lato cronologia: il sito esiste e ha una periodizzazione ma
    nessuna riga in `us_table`. Si leggono le fasi, zero unità, zero avvisi:
    nessuna eccezione e nessuna fuga dalle righe del sito accanto."""
    periods, units = CC.load_chronology_rows(scavo[0], RSD.SITO_VUOTO)
    assert len(periods) == 1
    assert units == []
    assert CC.check_chronology(periods, units, sito=RSD.SITO_VUOTO) == []


def test_generated_site_without_us_rows_projects_to_a_graph_without_us(scavo):
    """Caso 7, lato grafo: nessun nodo-unità e nessun problema di rapporti."""
    from modules.s3dgraphy.sync.graph_projector import GraphProjector
    _, url = scavo
    graph = GraphProjector().populate_graph(url, RSD.SITO_VUOTO)
    assert [n for n in graph.nodes if RC._real_us(n) is not None] == []
    assert RC.check_rapporti(graph, sito=RSD.SITO_VUOTO).issues == []
