"""Il Time Manager disegna la matrice senza Graphviz (2026-10-09).

Richiesta di Enzo: «uso graphviz e questo spesso blocca o impiega tempo,
dato che ogni generazione deve fare una serie di processi». Qui si
provano le promesse nel sorgente — il collegamento vero vive dentro
QGIS — più la parte pura, che è provata per intero in
``test_em_matrix_records.py``.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

TM = _ROOT / "tabs" / "Gis_Time_controller.py"


def _source() -> str:
    return TM.read_text(encoding="utf-8")


def test_the_matrix_no_longer_goes_through_graphviz():
    """Né il JPEG di `dot` né la chiamata a `generate_matrix_3` restano
    sulla strada della matrice del Time Manager."""
    src = _source()
    assert "Harris_matrix_viewtred.dot.jpg" not in src
    assert "generate_matrix_3" not in src


def test_it_draws_with_the_same_engine_as_the_panel():
    """Una matrice sola, disegnata in un modo solo: se il Time Manager
    avesse un suo disegno, i due divergerebbero."""
    src = _source()
    assert "em_matrix_records" in src
    assert "em_matrix_layout" in src
    assert "MatrixView" in src


def test_the_atlas_gets_a_vector_picture():
    """Nella tavola la matrice è vettoriale: si legge a ogni scala e pesa
    decine di KB invece dei megabyte del JPEG."""
    src = _source()
    assert "FormatSVG" in src
    assert "Harris_matrix_timemanager.svg" in src


def test_the_periods_are_read_once_not_once_per_area_and_period():
    """La via vecchia faceva una query dentro due cicli annidati, a ogni
    rigenerazione. È lì che se ne andava il tempo, più che in `dot`."""
    src = _source()
    assert "_PERIODI_CACHE" in src
    assert "def _periodi_del_sito" in src


def test_the_drawing_helper_filters_to_the_visible_units():
    """Il Time Manager mostra le US fino alla posizione del cursore: la
    matrice deve essere quella, non quella di tutto il sito."""
    src = _source()
    assert "def _disegna_matrice" in src
    assert "visible=visibili" in src


# ---------------- i tre guasti segnalati il 2026-10-09 ---------------------

def test_the_matrix_follows_the_dial():
    """Enzo: «il matrix non si aggiorna quando giro la manopola, devo
    spegnere e riaccendere il checkbox». Era agganciato a `stateChanged`
    della spunta e a nient'altro. Ora si rifà quando la manopola si ferma,
    DOPO che il filtro è stato applicato."""
    src = _source()
    inizio = src.index("def _on_debounce_timeout")
    corpo = src[inizio:inizio + 900]
    assert "update_graphics_view" in corpo
    assert "checkBox_matrix.isChecked" in corpo


def test_the_datings_come_from_the_database_not_from_the_filtered_layer():
    """Enzo: «non vedo più la periodizzazione se giro in senso orario,
    mentre in senso antiorario compare». Le datazioni si leggevano dalle
    feature del layer, cioè attraverso il filtro corrente — che però si
    applica dopo, con un timer. Girando in avanti il livello nuovo non era
    ancora nel layer."""
    src = _source()
    assert "def _datazioni_del_sito" in src
    inizio = src.index("def set_max_num")
    corpo = src[inizio:src.index("def ", inizio + 10)]
    assert "self._datazioni_del_sito()" in corpo
    assert "getFeatures()" not in corpo


def test_update_datazione_is_connected_once_not_on_every_turn():
    """`set_max_num` è agganciato a `valueChanged` e dentro ri-collegava
    `update_datazione` a `valueChanged`: le connessioni si accumulavano a
    ogni scatto della manopola."""
    src = _source()
    inizio = src.index("def set_max_num")
    corpo = src[inizio:src.index("def ", inizio + 10)]
    assert "valueChanged.connect" not in corpo
    assert src.count(
        "self.spinBox_relative_cronology.valueChanged.connect("
        "self.update_datazione)") == 1


def test_the_cached_tables_do_not_survive_a_change_of_site():
    """Sono attributi di classe: senza azzerarle, riaprendo la finestra su
    un altro sito si vedrebbero i periodi di prima."""
    src = _source()
    assert "type(self)._PERIODI_CACHE = {}" in src
    assert "type(self)._DATAZIONI_CACHE = {}" in src


def test_the_units_outside_the_view_are_drawn_faded_not_dropped():
    """Enzo: «le US che non sono presenti ma servono per agganciare i nodi
    devono essere opacizzate, per far intendere che non sono visibili
    nella mappa»."""
    from modules.utility.em_matrix_records import model_from_records

    righe = [dict(sito="Alfa", area="1", us="1", unita_tipo="US",
                  periodo_iniziale="1", fase_iniziale="1",
                  rapporti="[['Copre', '2', '1', 'Alfa']]"),
             dict(sito="Alfa", area="1", us="2", unita_tipo="US",
                  periodo_iniziale="1", fase_iniziale="1", rapporti="[]")]
    model = model_from_records(righe, [("1", "1", "Epoca", 1, 2)],
                               visible={("1", "1")})
    sbiadite = [u.label for u in model.units if u.dimmed]
    assert sbiadite == ["1.US2"]
    assert len(model.relations) == 1


def test_the_matrix_is_built_from_all_the_rows_not_only_the_visible_ones():
    """Le US fuori vista che un rapporto cita entrano nel disegno
    sbiadite: ma per saperlo servono le loro righe, e `data_list` contiene
    solo quelle visibili. Si leggono dal database, una volta sola."""
    src = _source()
    assert "def _record_del_sito" in src
    assert "def _modello_matrice" in src
    inizio = src.index("def _modello_matrice")
    corpo = src[inizio:src.index("def ", inizio + 10)]
    assert "self._record_del_sito(sito)" in corpo
    assert "visible=visibili" in corpo


def test_the_view_and_the_atlas_build_the_model_the_same_way():
    """Due costruttori diversi divergerebbero: la tavola stampata e quello
    che si vede a schermo devono essere la stessa matrice."""
    src = _source()
    assert src.count("self._modello_matrice(") == 2
