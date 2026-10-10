"""Il giudizio sulla cronologia di un sito, senza database e senza QGIS.

Le righe sono costruite a mano: `check_chronology` non deve sapere da dove
vengono, ed è questo che lo rende provabile.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
_EXT_LIBS = str(_ROOT / "ext_libs")
if _EXT_LIBS in sys.path:
    sys.path.remove(_EXT_LIBS)
sys.path.insert(0, _EXT_LIBS)

from modules.utility import chronology_check as CC


def _p(periodo, fase, ini, fin, estesa="XV secolo"):
    return {"periodo": periodo, "fase": fase, "cron_iniziale": ini,
            "cron_finale": fin, "datazione_estesa": estesa}


def test_two_phases_with_the_same_span_are_one_overlap():
    """Due fasi con lo stesso intervallo sono UNA sovrapposizione, non due.

    È il caso del database di Enzo: 2/2.2 e 3/1 portano entrambe 1500–1549.
    """
    periods = [_p("2", "2.2", 1500, 1549), _p("3", "1", 1500, 1549)]
    issues = CC.check_chronology(periods, [], sito="S")
    assert [i.kind for i in issues] == ["epoch_overlap"]
    assert issues[0].auto is False
    assert issues[0].summary == (
        "Le fasi 2/2.2 e 3/1 si sovrappongono per 50 anni (1500–1549)")


def test_identical_spans_carry_no_proposal():
    """Con due intervalli identici non esiste un restringimento possibile.

    Alzare l'inizio della più recente a 1550 la farebbe finire prima di
    cominciare. Si segnala e basta: chi si sposta lo sa solo chi ha scavato.
    """
    periods = [_p("2", "2.2", 1500, 1549), _p("3", "1", 1500, 1549)]
    issues = CC.check_chronology(periods, [], sito="S")
    assert issues[0].edits == []


def test_partial_overlap_proposes_moving_the_more_recent_start():
    periods = [_p("2", "2.2", 1500, 1600), _p("3", "1", 1550, 1650)]
    issues = CC.check_chronology(periods, [], sito="S")
    assert len(issues) == 1
    edit, = issues[0].edits
    assert edit.set_fields == (("cron_iniziale", 1601),)
    assert edit.target == ("periodizzazione_table",
                           {"periodo": "3", "fase": "1"})


def test_spans_that_touch_without_overlapping_are_not_an_issue():
    periods = [_p("2", "2.2", 1450, 1499), _p("3", "1", 1500, 1549)]
    assert CC.check_chronology(periods, [], sito="S") == []


def test_a_reversed_span_is_never_pre_checked():
    """`1650 → 1450` è «quasi sempre un periodo a.C. battuto senza il segno
    meno» (modules/utility/periodization_checks.py, database Ventena,
    2026-08-27): una correzione spuntata di suo trasformerebbe l'Età del
    Bronzo Medio nel 1450–1650 d.C., e senza che nessuno l'abbia chiesto.
    """
    periods = [_p("6", "1", 1650, 1450, "Età del Bronzo Medio")]
    issues = CC.check_chronology(periods, [], sito="S")
    assert [i.kind for i in issues] == ["epoch_reversed"]
    assert issues[0].auto is False


def test_a_reversed_span_proposes_the_two_years_as_negatives():
    """La correzione è quella di `periodization_checks`: gli anni si scrivono
    negativi, non si scambiano. Scambiarli renderebbe `inizio > fine` falso e
    **zittirebbe** l'avviso del projector, che gira nello stesso clic.
    """
    periods = [_p("6", "1", 1650, 1450, "Età del Bronzo Medio")]
    issues = CC.check_chronology(periods, [], sito="S")
    edit, = issues[0].edits
    assert edit.set_fields == (("cron_iniziale", -1650),
                               ("cron_finale", -1450))
    assert edit.target == ("periodizzazione_table",
                           {"periodo": "6", "fase": "1"})


def test_a_reversed_span_carries_one_single_proposal():
    """Il dialogo applica una issue quando è spuntata **e** ha delle `edits`:
    due proposte nella stessa issue si applicherebbero insieme, e la
    combinazione di una negazione e di uno scambio non è nessuna delle due.
    """
    periods = [_p("6", "1", 1650, 1450, "Età del Bronzo Medio")]
    assert len(CC.check_chronology(periods, [], sito="S")[0].edits) == 1


def test_the_reversed_summary_says_what_periodization_checks_says():
    """Le due verifiche compaiono nella stessa finestra: devono dire una cosa
    sola. Lo scambio resta nominato come alternativa da fare a mano."""
    periods = [_p("6", "1", 1650, 1450, "Età del Bronzo Medio")]
    riassunto = CC.check_chronology(periods, [], sito="S")[0].summary
    assert "a.C." in riassunto
    assert "-1650" in riassunto
    assert "Periodizzazione" in riassunto      # dove si fa a mano
    assert "scambia" in riassunto.lower()      # l'altra lettura, nominata
    inglese = CC.check_chronology(periods, [], sito="S", lang="en")[0].summary
    assert "BC" in inglese and "minus" in inglese.lower()


def test_a_span_already_bc_proposes_the_swap_not_another_negation():
    """`-1450 → -1650`: il segno c'è già, e negare porterebbe l'Età del Bronzo
    nel 1450–1650 d.C. — l'errore che questa correzione deve evitare. Qui la
    lettura buona è lo scambio, e resta una proposta da spuntare.
    """
    periods = [_p("6", "1", -1450, -1650, "Età del Bronzo Medio")]
    issues = CC.check_chronology(periods, [], sito="S")
    assert issues[0].auto is False
    edit, = issues[0].edits
    assert edit.set_fields == (("cron_iniziale", -1650),
                               ("cron_finale", -1450))
    assert "a.C." not in issues[0].summary


def test_the_two_checks_fire_on_the_same_row_and_agree():
    """`suspicious_chronologies` e `epoch_reversed` hanno lo stesso predicato:
    il rimedio che raccontano deve essere lo stesso, non l'opposto."""
    from modules.utility.periodization_checks import (
        format_chronology_warning, suspicious_chronologies)
    riga = (6, "1", 1650, 1450, "Età del Bronzo Medio")
    sospette = suspicious_chronologies([riga])
    assert len(sospette) == 1
    avviso = format_chronology_warning(sospette, "it")
    nostro = CC.check_chronology(
        [_p("6", "1", 1650, 1450, "Età del Bronzo Medio")], [],
        sito="S")[0].summary
    for pezzo in ("a.C.", "negativ"):
        assert pezzo in avviso.lower() or pezzo in avviso
        assert pezzo in nostro.lower() or pezzo in nostro


def test_a_reversed_span_is_not_also_an_overlap():
    """Un intervallo rovesciato esce dal confronto: un problema per volta.

    La riverifica che segue l'applicazione lo guarda da capo, raddrizzato.
    """
    periods = [_p("2", "2.2", 1549, 1500), _p("3", "1", 1480, 1560)]
    kinds = [i.kind for i in CC.check_chronology(periods, [], sito="S")]
    assert kinds == ["epoch_reversed"]


def test_phase_without_years_is_reported_and_not_automatic():
    periods = [_p("2", "2.2", None, None)]
    issues = CC.check_chronology(periods, [], sito="S")
    assert [i.kind for i in issues] == ["epoch_no_dates"]
    assert issues[0].auto is False
    assert issues[0].edits == []
    assert "2/2.2" in issues[0].summary


def test_a_year_written_as_text_is_a_phase_without_years_not_a_crash():
    periods = [_p("2", "2.2", "XV sec", 1499)]
    assert [i.kind for i in CC.check_chronology(periods, [], sito="S")] \
        == ["epoch_no_dates"]


def test_bc_years_are_negative_and_year_zero_is_a_year():
    """Le date a.C. si scrivono negative, e lo zero è un anno come gli altri.

    Senza questo, uno `if not ini` leggerebbe l'anno 0 come «nessun anno» e
    una periodizzazione a cavallo dell'era non si verificherebbe mai.
    """
    periods = [_p("1", "1", -100, 0), _p("1", "2", -50, 50)]
    issues = CC.check_chronology(periods, [], sito="S")
    assert [i.kind for i in issues] == ["epoch_overlap"]
    edit, = issues[0].edits
    assert edit.set_fields == (("cron_iniziale", 1),)
    assert edit.target == ("periodizzazione_table",
                           {"periodo": "1", "fase": "2"})


def test_phase_2_1_and_2_10_are_two_phases_not_one():
    """Come float sarebbero la stessa fase, e una delle due si perderebbe.

    Gli intervalli si sovrappongono di proposito: se le chiavi collassassero,
    `spans` terrebbe una riga sola e la sovrapposizione non si vedrebbe.
    """
    periods = [_p("2", "2.1", 1400, 1500), _p("2", "2.10", 1450, 1550)]
    issues = CC.check_chronology(periods, [], sito="S")
    assert [i.kind for i in issues] == ["epoch_overlap"]
    assert issues[0].us_path == ["2/2.1", "2/2.10"]


def test_empty_periodization_is_not_an_error():
    assert CC.check_chronology([], [], sito="S") == []


def test_the_four_titles_exist_in_all_six_languages():
    from modules.utility import rapporti_check as RC
    for kind in ("epoch_overlap", "epoch_reversed", "epoch_no_dates",
                 "datazione_mismatch"):
        for lang in ("it", "en", "de", "es", "fr", "pt"):
            titolo = RC.kind_title(kind, lang)
            assert titolo and not titolo.startswith("t_"), (kind, lang)


def test_a_whole_year_written_as_a_float_is_a_year():
    periods = [_p("2", "2.2", 1500.0, "1549.0")]
    issues = CC.check_chronology(periods, [], sito="S")
    assert issues == []          # intervallo valido, nessuna sovrapposizione


def test_a_fractional_year_is_still_a_phase_without_years():
    periods = [_p("2", "2.2", 1500.5, 1549)]
    assert [i.kind for i in CC.check_chronology(periods, [], sito="S")] \
        == ["epoch_no_dates"]


def test_the_nine_entries_are_in_all_six_blocks_without_falling_back():
    """`_t` ripiega sull'inglese, quindi una chiave mancante non si vedrebbe
    dal titolo: si guarda il dizionario."""
    from modules.utility.rapporti_check import _L
    chiavi = ("t_epoch_overlap", "t_epoch_reversed", "t_epoch_no_dates",
              "t_datazione_mismatch", "s_epoch_overlap", "s_epoch_reversed",
              "s_epoch_reversed_swap", "s_epoch_no_dates",
              "s_datazione_mismatch")
    for lang in ("it", "en", "de", "es", "fr", "pt"):
        mancanti = [k for k in chiavi if k not in _L[lang]]
        assert not mancanti, (lang, mancanti)


def test_the_break_does_not_skip_an_overlap_with_an_earlier_phase():
    """La terza fase si sovrappone solo alla prima: il `break` interno deve
    fermare il confronto della seconda, non quello della prima."""
    periods = [_p("1", "1", 1400, 1600), _p("1", "2", 1450, 1500),
               _p("1", "3", 1550, 1700)]
    issues = CC.check_chronology(periods, [], sito="S")
    assert [i.us_path for i in issues] == [["1/1", "1/2"], ["1/1", "1/3"]]


def test_not_a_number_is_a_phase_without_years_and_does_not_raise():
    """`NaN` e `inf` arrivano da una colonna REAL o da un import mal fatto, e
    un'eccezione qui farebbe fallire la verifica intera, non una fase."""
    for valore in (float("nan"), float("inf"), "nan", "inf", "-inf"):
        periods = [_p("2", "2.2", valore, 1549)]
        assert [i.kind for i in CC.check_chronology(periods, [], sito="S")] \
            == ["epoch_no_dates"], valore


def _u(us, periodo, fase, datazione):
    return {"us": us, "periodo_iniziale": periodo, "fase_iniziale": fase,
            "datazione": datazione}


def test_sheet_dating_out_of_step_is_rewritten_from_the_periodization():
    """La periodizzazione è la fonte e la scheda la copia (Enzo, 2026-10-10).

    Riscrivere la copia dalla fonte non ha alternative: automatica.
    """
    periods = [_p("2", "3", 1451, 1499, "XV secolo")]
    units = [_u("12", "2", "3", "Prima metà del XV secolo")]
    issues = CC.check_chronology(periods, units, sito="S")
    assert [i.kind for i in issues] == ["datazione_mismatch"]
    assert issues[0].auto is True
    edit, = issues[0].edits
    assert edit.us == "12"
    assert edit.set_fields == (("datazione", "XV secolo"),)
    # us_table, nominata per intero: l'identità di una scheda è di quattro
    # colonne, e `us` da sola riscriverebbe anche la US 12 di un'altra area.
    assert edit.target == ("us_table", {"us": "12", "area": "",
                                        "unita_tipo": ""})


def test_the_summary_shows_both_texts():
    """L'anteprima è l'unico punto in cui si vede cosa si sta per riscrivere,
    e su un sito tradotto sono cinquantuno righe in un colpo."""
    periods = [_p("2", "2", 1500, 1549, "First half of the 16th century")]
    units = [_u("4", "2", "2", "Prima metà del XVI secolo")]
    issues = CC.check_chronology(periods, units, sito="S")
    assert "Prima metà del XVI secolo" in issues[0].summary
    assert "First half of the 16th century" in issues[0].summary


def test_matching_dating_is_not_an_issue():
    periods = [_p("2", "3", 1451, 1499, "XV secolo")]
    units = [_u("12", "2", "3", "XV secolo")]
    assert CC.check_chronology(periods, units, sito="S") == []


def test_an_empty_sheet_dating_is_filled_from_its_phase():
    """Sul database di esempio sono quattro per sito: la fonte c'è e la copia
    manca, che è la stessa regola."""
    periods = [_p("2", "3", 1451, 1499, "XV secolo")]
    units = [_u("12", "2", "3", None)]
    issues = CC.check_chronology(periods, units, sito="S")
    assert [i.kind for i in issues] == ["datazione_mismatch"]
    assert issues[0].edits[0].set_fields == (("datazione", "XV secolo"),)


def test_none_and_empty_string_say_the_same_thing():
    """`datazione = None` nella scheda e `datazione_estesa = ''` nella
    periodizzazione non sono un disallineamento: sono due vuoti."""
    periods = [_p("2", "3", 1451, 1499, "")]
    units = [_u("12", "2", "3", None)]
    assert CC.check_chronology(periods, units, sito="S") == []


def test_an_empty_source_never_blanks_a_filled_sheet():
    """Senza questa regola la verifica svuoterebbe le schede dei siti con la
    periodizzazione incompleta: non c'è niente da copiare."""
    periods = [_p("2", "3", 1451, 1499, None)]
    units = [_u("12", "2", "3", "XV secolo")]
    assert CC.check_chronology(periods, units, sito="S") == []


def test_a_unit_without_a_period_has_no_source_to_copy_from():
    """Senza periodo non c'è fonte, e non si copia dalla fase fantasma.

    La periodizzazione porta di proposito una riga con il periodo vuoto e la
    datazione piena: è l'unico caso in cui la guardia `not key[0]` è quello
    che ferma la copia, invece della fonte vuota.
    """
    periods = [_p("2", "3", 1451, 1499, "XV secolo"),
               _p("", "", 1000, 1100, "fase fantasma")]
    units = [_u("12", "", "", "qualcosa")]
    assert CC.check_chronology(periods, units, sito="S") == []


def test_a_unit_pointing_at_a_phase_that_does_not_exist_is_skipped():
    periods = [_p("2", "3", 1451, 1499, "XV secolo")]
    units = [_u("12", "9", "9", "qualcosa")]
    assert CC.check_chronology(periods, units, sito="S") == []


def test_whitespace_around_the_dating_is_not_a_mismatch():
    periods = [_p("2", "3", 1451, 1499, "XV secolo")]
    units = [_u("12", "2", "3", "  XV secolo  ")]
    assert CC.check_chronology(periods, units, sito="S") == []


def test_edit_prefix_names_the_us_when_there_is_no_target():
    from modules.utility.rapporti_check import Edit
    assert CC.edit_prefix(Edit(us="12")) == "US 12"


def test_edit_prefix_names_area_and_unit_type_when_they_are_there():
    """Su uno scavo a più aree «US 1» da solo non dice quale riga si riscrive,
    e l'anteprima è il punto in cui si guarda."""
    from modules.utility.rapporti_check import Edit
    e = Edit(us="1", target=("us_table", {"us": "1", "area": "2",
                                          "unita_tipo": "USM"}))
    assert CC.edit_prefix(e) == "US 1 (2, USM)"


def test_edit_prefix_stays_short_when_there_is_nothing_to_tell_apart():
    from modules.utility.rapporti_check import Edit
    e = Edit(us="12", target=("us_table", {"us": "12", "area": "",
                                           "unita_tipo": ""}))
    assert CC.edit_prefix(e) == "US 12"


def test_edit_prefix_names_the_row_when_the_target_is_another_table():
    """«US 2/2.2» mentirebbe sulla riga che si sta per cambiare."""
    from modules.utility.rapporti_check import Edit
    e = Edit(us="2/2.2", target=("periodizzazione_table",
                                 {"periodo": "2", "fase": "2.2"}))
    assert CC.edit_prefix(e) == "periodizzazione_table fase=2.2 periodo=2"


def test_explain_bounds_reads_span_rule_and_provenance():
    """Due estremi dalla stessa relazione: una provenienza sola, come prima."""
    entry = {"start": 1500.0, "end": 1549.0, "start_rule": "epoch",
             "start_source": "epoch_2_2", "start_relation": "has_first_epoch",
             "end_rule": "epoch", "end_source": "epoch_2_2",
             "end_relation": "has_first_epoch", "rule": "epoch"}
    riga = CC.explain_bounds(entry)
    assert riga == "1500–1549 · epoca · has_first_epoch → epoch_2_2"


def test_explain_bounds_labels_the_two_bounds_when_they_differ():
    """Il caso vero: sul sito di Enzo due voci su 45 hanno gli estremi da
    relazioni diverse, e senza l'etichetta la fine verrebbe attribuita alla
    relazione dell'inizio."""
    entry = {"start": 1451.0, "end": 1499.0, "start_rule": "epoch",
             "start_source": "epoch_2_4", "start_relation": "survive_in_epoch",
             "end_rule": "epoch", "end_source": "epoch_2_3",
             "end_relation": "has_first_epoch", "rule": "epoch"}
    assert CC.explain_bounds(entry) == (
        "1451–1499 · epoca"
        " · inizio survive_in_epoch → epoch_2_4"
        " · fine has_first_epoch → epoch_2_3")


def test_explain_bounds_names_the_rule_in_the_chosen_language():
    """Qui la fine non porta provenienza: l'inizio si etichetta, altrimenti
    la sua relazione sembrerebbe coprire anche la fine."""
    entry = {"start": -100.0, "end": 0.0, "start_rule": "tpq",
             "start_source": "USM101", "start_relation": "is_after",
             "rule": "tpq"}
    assert CC.explain_bounds(entry, lang="en") == \
        "-100–0 · terminus post quem · start is_after → USM101"


def test_explain_bounds_on_an_entry_without_bounds_does_not_raise():
    assert CC.explain_bounds({}) == ""
    assert CC.explain_bounds(None) == ""


def test_explain_bounds_with_only_an_end_says_so():
    entry = {"end": 1549.0, "end_rule": "taq", "end_source": "US7",
             "end_relation": "is_before", "rule": "taq"}
    assert CC.explain_bounds(entry) == \
        "…–1549 · terminus ante quem · is_before → US7"


def test_explain_bounds_without_provenance_gives_just_span_and_rule():
    entry = {"start": 1500.0, "end": 1549.0, "rule": "written"}
    assert CC.explain_bounds(entry) == "1500–1549 · data scritta"


def test_explain_bounds_prints_an_unknown_rule_as_it_is():
    """Se la libreria aggiungesse una regola, la riga la nomina invece di
    saltare: meglio un nome tecnico che un'eccezione nel pannello."""
    entry = {"start": 1500.0, "end": 1549.0, "rule": "regola_nuova"}
    assert CC.explain_bounds(entry) == "1500–1549 · regola_nuova"


def test_every_language_covers_the_five_rules_and_the_two_sides():
    """`_RULES` ripiega sull'inglese, quindi una lingua cancellata non si
    vedrebbe da `explain_bounds`: si guarda il dizionario."""
    for lang in ("it", "en", "de", "es", "fr", "pt"):
        assert set(CC._RULES[lang]) == {"written", "epoch", "contained",
                                        "tpq", "taq"}, lang
        assert len(CC._LATI[lang]) == 2, lang
        assert all(CC._LATI[lang]), lang


def test_bounds_by_us_keys_on_the_us_number_not_the_node_id():
    """Gli id dei nodi sono uuid7: accostare un avviso agli estremi calcolati
    chiede lo stesso modo in cui la verifica dei rapporti riconosce una unità,
    cioè l'attributo `us` che il projector mette sulle righe vere di us_table
    — non il nome, che su un nodo di servizio è tutto quello che c'è.
    """
    ID = "019f8043-4f87-7e3b-b7e8-6736d398fc27"

    class _Nodo:
        attributes = {"us": "4"}     # il nome non c'entra: conta l'attributo
        name = "USM4"

    class _Grafo:
        def chronology(self):
            return {ID: {"start": 1500.0, "end": 1549.0, "rule": "epoch"}}

        def find_node_by_id(self, node_id):
            # Risponde solo per l'id che le è stato chiesto: un passaggio di
            # argomento sbagliato deve farsi vedere.
            return _Nodo() if node_id == ID else None

    per_us = CC.bounds_by_us(_Grafo())
    assert list(per_us) == ["4"]
    assert per_us["4"]["start"] == 1500.0


def test_bounds_by_us_skips_a_node_it_cannot_name():
    """Un nodo di servizio del grafo non è una unità scavata: salta."""
    class _Grafo:
        def chronology(self):
            return {"x": {"start": 1.0, "end": 2.0, "rule": "epoch"}}

        def find_node_by_id(self, node_id):
            return None

    assert CC.bounds_by_us(_Grafo()) == {}


def test_bounds_by_us_names_a_source_unit_instead_of_its_uuid():
    """Un vincolo arrivato da un'altra unità porta l'uuid di quel nodo, e
    «is_after → 019f8043-…» non dice niente a nessuno."""
    ID_A, ID_B = "uuid-a", "uuid-b"

    class _Nodo:
        def __init__(self, us):
            self.attributes = {"us": us}
            self.name = "US%s" % us

    class _Grafo:
        def chronology(self):
            return {ID_A: {"start": 1422.0, "end": None, "rule": "tpq",
                           "start_relation": "is_after", "start_source": ID_B}}

        def find_node_by_id(self, node_id):
            return {ID_A: _Nodo("12"), ID_B: _Nodo("7")}.get(node_id)

    voce = CC.bounds_by_us(_Grafo())["12"]
    assert voce["start_source"] == "US 7"
    assert CC.explain_bounds(voce) == \
        "1422–… · terminus post quem · is_after → US 7"


def test_bounds_by_us_leaves_an_epoch_source_as_it_is():
    """Su un nodo-epoca `_us_of` restituisce il NOME dell'epoca («Età
    contemporanea»), quindi usarlo qui darebbe «US Età contemporanea»: la
    fonte si risolve con `_real_us`, che su un'epoca dà None.
    """
    class _Epoca:
        attributes = {}
        name = "Età contemporanea"

    class _Unita:
        attributes = {"us": "1"}
        name = "US1"

    class _Grafo:
        def chronology(self):
            return {"u": {"start": 1800.0, "end": 2022.0, "rule": "epoch",
                          "start_relation": "has_first_epoch",
                          "start_source": "epoch_1_1",
                          "end_relation": "has_first_epoch",
                          "end_source": "epoch_1_1"}}

        def find_node_by_id(self, node_id):
            return _Unita() if node_id == "u" else _Epoca()

    voce = CC.bounds_by_us(_Grafo())["1"]
    assert voce["start_source"] == "epoch_1_1"
    assert CC.explain_bounds(voce) == \
        "1800–2022 · epoca · has_first_epoch → epoch_1_1"


def test_two_proposals_on_the_same_phase_keep_the_strongest():
    """X=(1000,1300), Y=(1020,1150), Z=(1050,1400): due proposte alzavano
    `Z.cron_iniziale`, a 1301 e a 1151.

    Spuntandole entrambe vinceva l'ultima, 1151, che non risolve né la
    sovrapposizione con X né quella con Y — e la finestra diceva «2 correzioni
    applicate». La più forte le chiude tutte e due.
    """
    periods = [_p("1", "X", 1000, 1300), _p("1", "Y", 1020, 1150),
               _p("1", "Z", 1050, 1400)]
    issues = CC.check_chronology(periods, [], sito="S")
    assert [i.us_path for i in issues] == [["1/X", "1/Y"], ["1/X", "1/Z"],
                                           ["1/Y", "1/Z"]]
    proposte = [(i.us_path, e.set_fields, e.target)
                for i in issues for e in i.edits]
    assert proposte == [(["1/X", "1/Z"], (("cron_iniziale", 1301),),
                         ("periodizzazione_table",
                          {"periodo": "1", "fase": "Z"}))]


def test_the_strongest_proposal_closes_every_overlap_it_was_chosen_for():
    """La ragione per cui si tiene la più alta, scritta come asserzione: con
    `Z` spostata a 1301 nessuna delle due coppie di Z si tocca più."""
    periods = [_p("1", "X", 1000, 1300), _p("1", "Y", 1020, 1150),
               _p("1", "Z", 1301, 1400)]
    restanti = [i.us_path for i in CC.check_chronology(periods, [], sito="S")]
    assert restanti == [["1/X", "1/Y"]]     # resta solo quella senza rimedio


def test_two_proposals_on_two_different_phases_both_survive():
    """Il taglio è per riga e colonna: due fasi diverse non si fanno ombra."""
    periods = [_p("1", "A", 1000, 1100), _p("1", "B", 1050, 1200),
               _p("2", "C", 1500, 1600), _p("2", "D", 1550, 1700)]
    proposte = {e.target[1]["fase"]: e.set_fields
                for i in CC.check_chronology(periods, [], sito="S")
                for e in i.edits}
    assert proposte == {"B": (("cron_iniziale", 1101),),
                        "D": (("cron_iniziale", 1601),)}


def test_period_zero_is_a_period_not_a_missing_one():
    """La colonna `periodo` è `Integer`, e `str(0 or "")` dà `""`: il periodo
    0 si leggeva come «nessun periodo», e la sua scheda non si verificava.

    `temporal_check.build_chronology` la stessa chiave la fa con `is None`,
    quindi le due verifiche non erano nemmeno d'accordo fra loro.
    """
    periods = [_p(0, "1", 1000, 1100, "XI secolo")]
    units = [_u("5", 0, "1", "SBAGLIATA")]
    issues = CC.check_chronology(periods, units, sito="S")
    assert [i.kind for i in issues] == ["datazione_mismatch"]
    assert issues[0].edits[0].set_fields == (("datazione", "XI secolo"),)


def test_the_key_of_period_zero_is_the_same_on_both_sides():
    """`build_chronology` indicizza ("0", "0"): `_key` deve dire lo stesso, o
    una fase trovata da una verifica è invisibile all'altra."""
    assert CC._key({"periodo": 0, "fase": 0}) == ("0", "0")
    assert CC._key({"periodo": None, "fase": None}) == ("", "")


def test_a_node_that_is_not_a_real_us_does_not_enter_the_index():
    """`_us_of` ripiega sul **nome** del nodo, quindi un'epoca o un segnaposto
    `_synth_*` entravano in `per_us` sotto il loro nome: niente di
    strutturale li teneva fuori, solo la fortuna di non collidere."""
    class _Epoca:
        attributes = {}
        name = "Età contemporanea"

    class _Synth:
        attributes = {"us": "_synth_BR_654"}
        name = "_synth_BR_654"

    class _Grafo:
        def chronology(self):
            return {"e": {"start": 1800.0, "end": 2022.0, "rule": "epoch"},
                    "s": {"start": 1.0, "end": 2.0, "rule": "epoch"}}

        def find_node_by_id(self, node_id):
            return _Epoca() if node_id == "e" else _Synth()

    assert CC.bounds_by_us(_Grafo()) == {}


def test_the_phase_categories_do_not_claim_to_name_us():
    """`us_path` di una sovrapposizione porta **fasi** («2/2.2», o «4» quando
    la fase è vuota), e un `4` che coincide con la US 4 faceva comparire
    nell'anteprima la cronologia di quella US sotto un avviso che parlava di
    un'altra cosa."""
    assert CC.names_phases("epoch_overlap")
    assert CC.names_phases("epoch_reversed")
    assert CC.names_phases("epoch_no_dates")
    assert not CC.names_phases("datazione_mismatch")
    assert not CC.names_phases("missing_reciprocity")
