"""L'inserto panoramico della tavola (2026-10-09).

Enzo: «dovresti aggiustare anche l'overview, che nel caso di uno scavo
come base map deve avere un OpenStreetMap o satellite con il solo
puntino della localizzazione».

L'inserto serve a dire **dove si è nel mondo**: ripetere lo scavo non lo
dice, e inquadrato sullo scavo non dice niente del tutto. Qui si prova la
parte che decide — quale mappa è l'inserto, quale sfondo, quanto largo —
senza rete e senza QGIS.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from modules.utility.atlas_overview import (  # noqa: E402
    BASE_MAPS,
    DEFAULT_BASE_MAP,
    base_map_uri,
    overview_indexes,
    overview_window,
)


# ------------------------------------------------- quale mappa è l'inserto

def test_the_inset_is_every_map_but_the_main_one():
    assert overview_indexes([(409.0, 348.0), (75.0, 61.0)], 0) == [1]
    assert overview_indexes([(75.0, 61.0), (409.0, 348.0)], 1) == [0]


def test_a_layout_with_one_map_has_no_inset():
    assert overview_indexes([(409.0, 348.0)], 0) == []


def test_two_insets_are_both_insets():
    assert overview_indexes([(400.0, 300.0), (70.0, 60.0), (50.0, 40.0)],
                            0) == [1, 2]


def test_no_map_no_inset():
    assert overview_indexes([], None) == []


# ------------------------------------------------------------ lo sfondo

def test_openstreetmap_is_the_default():
    assert DEFAULT_BASE_MAP == "osm"
    assert "osm" in BASE_MAPS and "satellite" in BASE_MAPS


def test_the_uri_is_the_one_qgis_wants_for_xyz_tiles():
    uri = base_map_uri("osm")
    assert uri.startswith("type=xyz&") and "url=" in uri
    assert "zmax=" in uri and "zmin=" in uri
    # l'URL va codificato: le graffe di {z}/{x}/{y} non devono spezzare l'uri
    assert "%7Bz%7D" in uri or "{z}" in uri


def test_the_satellite_is_a_different_source():
    assert base_map_uri("satellite") != base_map_uri("osm")


def test_an_unknown_base_map_falls_back_instead_of_raising():
    assert base_map_uri("non esiste") == base_map_uri(DEFAULT_BASE_MAP)


# --------------------------------------------------- quanto largo inquadrare

def test_the_window_is_a_square_around_the_point():
    x1, y1, x2, y2 = overview_window((1000.0, 2000.0), half_width=500.0)
    assert (x1, y1, x2, y2) == (500.0, 1500.0, 1500.0, 2500.0)


def test_the_window_is_wide_enough_to_say_which_region():
    """Un inserto da cento metri non dice dove sei: dice solo che sei lì."""
    x1, _y1, x2, _y2 = overview_window((0.0, 0.0))
    assert (x2 - x1) >= 50_000.0


def test_a_point_that_is_not_a_point():
    assert overview_window(None) is None
    assert overview_window(("a", "b")) is None


# ------------------------------------------- le promesse nel generatore

TM = _ROOT / "tabs" / "Gis_Time_controller.py"


def _corpo(nome: str) -> str:
    src = TM.read_text(encoding="utf-8")
    inizio = src.index("def %s" % nome)
    return src[inizio:src.index("\n    def ", inizio + 10)]


def test_the_inset_gets_a_base_map_and_a_dot():
    corpo = _corpo("_prepara_panoramica")
    assert "_sfondo_e_puntino" in corpo
    assert "setLayers(strati)" in corpo


def test_the_inset_does_not_follow_the_project_layers():
    """Prima seguiva il progetto e mostrava le stesse US della mappa
    grande, in piccolo: non diceva niente che non ci fosse già."""
    corpo = _corpo("_prepara_panoramica")
    assert "setKeepLayerSet(True)" in corpo


def test_the_inset_is_in_web_mercator_because_the_tiles_are():
    corpo = _corpo("_prepara_panoramica")
    assert "EPSG:3857" in corpo


def test_without_the_network_the_dot_is_still_drawn():
    """In scavo la rete spesso non c'è: l'inserto deve degradare, non
    rompersi."""
    corpo = _corpo("_sfondo_e_puntino")
    assert "isValid()" in corpo
    assert "sfondo = None" in corpo
    corpo2 = _corpo("_prepara_panoramica")
    assert "if sfondo is not None" in corpo2


def test_the_base_map_can_be_switched_without_touching_the_code():
    corpo = _corpo("_sfondo_e_puntino")
    assert "pyarchinit/atlas_basemap" in corpo


def test_the_extra_layers_do_not_stay_in_the_project():
    """Sono roba della tavola, non del progetto di chi sta scavando."""
    src = TM.read_text(encoding="utf-8")
    assert "def _butta_via_la_panoramica" in src
    assert "addMapLayer(strato, False)" in _corpo("_prepara_panoramica")
    corpo = _corpo("generate_images")
    assert "self._butta_via_la_panoramica()" in corpo
