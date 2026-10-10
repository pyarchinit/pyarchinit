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


def test_reversed_span_swaps_the_two_years_automatically():
    periods = [_p("2", "2.2", 1549, 1500)]
    issues = CC.check_chronology(periods, [], sito="S")
    assert [i.kind for i in issues] == ["epoch_reversed"]
    assert issues[0].auto is True
    edit, = issues[0].edits
    assert edit.set_fields == (("cron_iniziale", 1500), ("cron_finale", 1549))
    assert edit.target == ("periodizzazione_table",
                           {"periodo": "2", "fase": "2.2"})


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


def test_the_eight_entries_are_in_all_six_blocks_without_falling_back():
    """`_t` ripiega sull'inglese, quindi una chiave mancante non si vedrebbe
    dal titolo: si guarda il dizionario."""
    from modules.utility.rapporti_check import _L
    chiavi = ("t_epoch_overlap", "t_epoch_reversed", "t_epoch_no_dates",
              "t_datazione_mismatch", "s_epoch_overlap", "s_epoch_reversed",
              "s_epoch_no_dates", "s_datazione_mismatch")
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
