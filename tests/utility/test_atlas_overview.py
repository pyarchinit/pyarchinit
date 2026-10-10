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
    assert "type=xyz&" in uri and "url=" in uri
    assert "zmax=" in uri and "zmin=" in uri
    # le graffe di {z}/{x}/{y} codificate, e SOLO quelle — vedi
    # test_only_the_braces_are_encoded_in_the_tile_url
    assert "%7Bz%7D" in uri


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
    assert "_strati_nella_toc" in corpo
    assert "_tema_dell_inserto" in corpo


def test_the_inset_follows_its_own_theme_not_the_project():
    """Prima seguiva il progetto e mostrava le stesse US della mappa
    grande, in piccolo: non diceva niente che non ci fosse già. Ora segue
    un tema che contiene solo lo sfondo e il puntino."""
    corpo = _corpo("_prepara_panoramica")
    assert "setFollowVisibilityPresetName(tema)" in corpo
    assert "setKeepLayerSet(False)" in corpo


def test_the_inset_is_in_web_mercator_because_the_tiles_are():
    corpo = _corpo("_prepara_panoramica")
    assert "EPSG:3857" in corpo


def test_without_the_network_the_dot_is_still_drawn():
    """In scavo la rete spesso non c'è: l'inserto deve degradare, non
    rompersi. Il tema si fa col solo puntino — lo prova
    ``test_the_theme_holds_the_basemap_and_the_dot_and_nothing_else``."""
    corpo = _corpo("_strati_nella_toc")
    assert "isValid()" in corpo
    assert "sfondo = None" in corpo


def test_the_base_map_can_be_switched_without_touching_the_code():
    corpo = _corpo("_strati_nella_toc")
    assert "pyarchinit/atlas_basemap" in corpo


def test_the_extra_layers_live_in_a_group_of_their_own():
    """Non si buttano più via: Enzo ha chiesto che OSM finisca nella TOC, e
    un tema che punta a un layer cancellato non mostra niente se il layout
    si riapre domani. Stanno in un gruppo spento, in fondo all'albero, e si
    riusano invece di moltiplicarsi."""
    corpo = _corpo("_gruppo_dell_inserto")
    assert "findGroup(GROUP_NAME)" in corpo
    assert "addGroup(GROUP_NAME)" in corpo
    assert "setItemVisibilityChecked(False)" in corpo
    toc = _corpo("_strati_nella_toc")
    assert "gruppo.addLayer" in toc
    assert "is_base_map(" in toc, "lo sfondo si riusa, non si riaggiunge"


# ---------------------------------------------------------------------------
# L'inserto passa dall'albero dei layer e da un tema (2026-10-10)
# ---------------------------------------------------------------------------
# Enzo, 2026-10-10: «nel momento in cui avvio l'atlas aggiungi nella TOC di
# QGIS osm se non c'è, e crei una vista solo per osm senza layer dentro e la
# associ all'overview». Il perché è buono: un `setLayers()` su layer che
# stanno nel progetto ma FUORI dall'albero è la strada che non ha mai
# disegnato una tessera; un tema mappa è la via che QGIS usa di suo per dire
# a una mappa del layout quali layer mostrare.

def test_the_group_and_the_theme_have_stable_names():
    """Si riusano fra una generazione e l'altra: se i nomi cambiassero, ogni
    export lascerebbe un gruppo in più nell'albero."""
    from modules.utility.atlas_overview import GROUP_NAME, THEME_NAME

    assert GROUP_NAME and THEME_NAME
    assert GROUP_NAME != THEME_NAME


def test_the_theme_holds_the_basemap_and_the_dot_and_nothing_else():
    """«Una vista solo per osm senza layer dentro»: nel tema non entra
    nessun layer del progetto — né le US né le quote. Il puntino sì, che è
    il motivo per cui l'inserto esiste."""
    from modules.utility.atlas_overview import theme_layers

    assert theme_layers("sfondo", "punto") == ["sfondo", "punto"]
    # senza sfondo (rete assente) resta il puntino: dice meno, non è un errore
    assert theme_layers(None, "punto") == ["punto"]
    # senza puntino non c'è inserto da fare
    assert theme_layers("sfondo", None) == []
    assert theme_layers(None, None) == []


def test_a_basemap_is_recognised_by_its_source_not_by_its_name():
    """Chi usa il plugin può rinominare il layer nella TOC: se lo cercassimo
    per nome ne aggiungeremmo uno nuovo a ogni export."""
    from modules.utility.atlas_overview import base_map_uri, is_base_map

    assert is_base_map(base_map_uri("osm"), "osm")
    assert not is_base_map(base_map_uri("satellite"), "osm")
    assert not is_base_map("", "osm")
    assert not is_base_map(None, "osm")


# ---------------------------------------------------------------------------
# L'URL era codificato due volte (2026-10-10)
# ---------------------------------------------------------------------------
# Enzo ha incollato le proprietà dei due layer, il mio e quello che QGIS
# aggiunge da «XYZ Tiles», e la differenza era tutta lì:
#
#   mio:   url=https%3A%2F%2Ftile.openstreetmap.org%2F%7Bz%7D%2F...
#   QGIS:  url=https://tile.openstreetmap.org/%7Bz%7D/%7Bx%7D/%7By%7D.png
#
# `quote(url, safe="")` codifica anche `:` e `/`, e QGIS decodificando una
# volta si ritrova una stringa ancora codificata: non un indirizzo. Il suo
# pannello contava **29 700 errori** di cache e zero tessere trovate.

def test_only_the_braces_are_encoded_in_the_tile_url():
    """QGIS codifica le graffe e lascia stare schema e barre. Se si codifica
    tutto, l'indirizzo non è più un indirizzo."""
    from modules.utility.atlas_overview import base_map_uri

    uri = base_map_uri("osm")
    assert "url=https://tile.openstreetmap.org/" in uri, \
        "schema e barre non si codificano: %s" % uri
    assert "%7Bz%7D/%7Bx%7D/%7By%7D" in uri, "le graffe sì"
    assert "%3A%2F%2F" not in uri, "doppia codifica: era questo il baco"


def test_the_uri_is_the_one_qgis_writes_itself():
    """Parola per parola quella che Enzo ha letto nelle proprietà del layer
    aggiunto da «XYZ Tiles», che le tessere le scarica."""
    from modules.utility.atlas_overview import base_map_uri

    assert base_map_uri("osm") == (
        "tilePixelRatio=1&type=xyz&"
        "url=https://tile.openstreetmap.org/%7Bz%7D/%7Bx%7D/%7By%7D.png&"
        "zmax=19&zmin=0")


def test_an_ampersand_in_the_url_is_still_encoded():
    """Una sorgente con una chiave in coda spezzerebbe l'uri in due
    parametri se l'`&` restasse nudo."""
    from modules.utility.atlas_overview import quote_tile_url

    assert quote_tile_url("https://x.y/{z}/{x}/{y}.png?key=a&b=c") == (
        "https://x.y/%7Bz%7D/%7Bx%7D/%7By%7D.png?key%3Da%26b%3Dc")
