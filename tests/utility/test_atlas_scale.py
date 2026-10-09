"""La tavola si riempie, e la scala è una scala vera (2026-10-09).

Enzo, guardando le prime stampe buone: «non credo la scala sia giusta,
dovresti far in modo che il disegno, a seconda del layout usato, riempia
la pagina e si scali in automatico, e la scala deve essere corretta».

Aveva ragione tre volte:
- si inquadrava sull'estensione del **canvas**, non su quella dei dati,
  quindi il disegno restava piccolo in mezzo al foglio;
- si inquadravano **tutte** le mappe, compreso l'inserto panoramico, che
  serve proprio a mostrare dove si è nel mondo;
- le due barre di scala del modello **non sono collegate a nessuna
  mappa**, e la numerica stampava «1:1» perché non aveva nulla da
  leggere.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from modules.utility.atlas_scale import (  # noqa: E402
    NICE_SCALES,
    fitting_extent,
    main_map_index,
    nice_scale,
)


# ------------------------------------------------- la scala arrotondata

def test_a_scale_becomes_the_next_real_one():
    """1:18,6 non è una scala da disegno: si sale alla prima vera che
    contiene ancora tutto."""
    assert nice_scale(18.6) == 20
    assert nice_scale(21) == 25
    assert nice_scale(1) == 1
    assert nice_scale(4.2) == 5


def test_a_scale_that_is_already_right_does_not_change():
    for s in (10, 20, 50, 100, 200, 500):
        assert nice_scale(s) == s


def test_it_never_shrinks_the_drawing():
    """Arrotondare in giù taglierebbe fuori una parte dello scavo."""
    for v in (3.1, 7.7, 19.9, 101.0, 999.0):
        assert nice_scale(v) >= v


def test_a_very_large_scale_is_rounded_to_a_round_thousand():
    assert nice_scale(123456) % 1000 == 0
    assert nice_scale(123456) >= 123456


def test_nonsense_does_not_raise():
    assert nice_scale(0) == NICE_SCALES[0]
    assert nice_scale(-5) == NICE_SCALES[0]
    assert nice_scale(float("nan")) == NICE_SCALES[0]


# ------------------------------------------- quale mappa è quella grande

def test_the_biggest_map_is_the_one_to_frame():
    """Il modello del Time Manager ha due mappe: quella grande e
    l'inserto panoramico, che non va toccato."""
    assert main_map_index([(409.0, 348.0), (75.0, 61.0)]) == 0
    assert main_map_index([(75.0, 61.0), (409.0, 348.0)]) == 1


def test_a_single_map_is_the_main_one():
    assert main_map_index([(100.0, 100.0)]) == 0


def test_no_map_at_all():
    assert main_map_index([]) is None


# ------------------------------------------------- l'inquadratura giusta

def test_the_extent_gets_a_margin_so_nothing_touches_the_frame():
    x1, y1, x2, y2 = fitting_extent((0.0, 0.0, 10.0, 10.0), margin=0.1)
    assert (x1, y1, x2, y2) == (-1.0, -1.0, 11.0, 11.0)


def test_a_point_extent_becomes_something_you_can_frame():
    """Un solo punto ha estensione nulla: inquadrarlo è uno zoom infinito."""
    x1, y1, x2, y2 = fitting_extent((5.0, 5.0, 5.0, 5.0), minimum=2.0)
    assert x2 - x1 >= 2.0 and y2 - y1 >= 2.0
    assert abs((x1 + x2) / 2 - 5.0) < 1e-9


def test_an_empty_extent_is_refused():
    assert fitting_extent(None) is None


def test_no_extra_margin_is_added_when_framing_the_sheet():
    """Misurato il 2026-10-09: un margine del 6% spingeva 1:18,6 oltre il
    20 e faceva saltare la serie a 1:25, cioè un disegno più piccolo del
    necessario. Inchiostro sul foglio: 22,85% esatta, 13,26% col margine
    e arrotondata, 19,88% senza margine e arrotondata."""
    sorgente = (_ROOT / "tabs" / "Gis_Time_controller.py").read_text(
        encoding="utf-8")
    inizio = sorgente.index("def _inquadra_tavola")
    corpo = sorgente[inizio:sorgente.index("\n    def ", inizio + 10)]
    assert "margin=0.0" in corpo


def test_a_margin_of_zero_still_protects_a_flat_extent():
    """Una sola US non deve dare uno zoom infinito nemmeno senza margine."""
    x1, y1, x2, y2 = fitting_extent((5.0, 5.0, 5.0, 5.0), margin=0.0,
                                    minimum=2.0)
    assert x2 - x1 >= 2.0 and y2 - y1 >= 2.0


def test_the_whole_atlas_shares_one_frame_and_one_scale():
    """Un atlante deve avere la stessa scala su tutte le tavole: se ogni
    tavola si adattasse al suo livello, la stessa US cambierebbe
    dimensione da una pagina all'altra e le tavole non si
    confronterebbero più."""
    sorgente = (_ROOT / "tabs" / "Gis_Time_controller.py").read_text(
        encoding="utf-8")
    assert "def _riquadro_del_sito" in sorgente
    inizio = sorgente.index("def generate_images")
    corpo = sorgente[inizio:sorgente.index("\n    def ", inizio + 10)]
    assert "self._riquadro_atlante = self._riquadro_del_sito()" in corpo
    # e si azzera alla fine, se no la prossima generazione userebbe
    # l'inquadratura di quella di prima
    assert "self._riquadro_atlante = None" in corpo
