"""Le etichette della tavola: il numero di US e la quota (2026-10-09).

Enzo: «inserire il nome US in un cerchio, il nome in grassetto, e la
quota sul layer puntuale; la quota deve stare sopra la linea del
simbolo — il simbolo è un triangolino rosso e una linea sottile
orizzontale, quindi la quota deve andare sopra la linea orizzontale».

La posizione non è stata scelta a occhio: il simbolo è stato disegnato e
misurato (vedi `QUOTA_OFFSET_MM`).
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from modules.utility.atlas_labels import (  # noqa: E402
    QUOTA_FIELDS,
    QUOTA_LINE_MM,
    QUOTA_OFFSET_MM,
    US_FIELDS,
    label_field,
    quota_expression,
)


# -------------------------------------------------- quale campo etichettare

def test_the_quote_view_field_is_found():
    """`pyarchinit_quote_view` porta `quota_q`."""
    campi = ["gid", "sito_q", "area_q", "us_q", "quota_q", "id_us", "sito"]
    assert label_field(campi, QUOTA_FIELDS) == "quota_q"


def test_the_us_view_field_is_found():
    campi = ["gid", "area_s", "scavo_s", "us_s", "id_us", "sito", "area", "us"]
    assert label_field(campi, US_FIELDS) == "us"


def test_the_drawing_table_names_are_accepted_too():
    """`pyunitastratigrafiche` chiama l'unità `us_s`."""
    assert label_field(["area_s", "scavo_s", "us_s"], US_FIELDS) == "us_s"


def test_a_layer_without_the_field_gets_no_label():
    assert label_field(["gid", "the_geom"], US_FIELDS) is None
    assert label_field([], QUOTA_FIELDS) is None


def test_the_order_of_the_candidates_decides():
    """Se ci sono tutti e due si preferisce il nome della scheda."""
    assert label_field(["us_s", "us"], US_FIELDS) == US_FIELDS[0]


# ------------------------------------------------------- la quota si legge

def test_the_elevation_is_written_with_two_decimals():
    """«12.3400000001» su una tavola è illeggibile."""
    assert quota_expression("quota_q") == 'format_number("quota_q", 2)'


def test_a_field_with_a_quote_in_the_name_does_not_break_the_expression():
    assert '""' in quota_expression('qu"ota')


# ------------------------------------------- dove va la quota, e perché lì

def test_the_elevation_sits_above_the_horizontal_line():
    """Misurato disegnando il simbolo a 300 dpi: la linea orizzontale sta
    a -2,7 mm dall'ancoraggio (negativo = sopra). Il testo deve stare più
    in alto ancora, se no ci finisce sopra."""
    assert QUOTA_LINE_MM < 0, "la linea sta sopra il punto"
    assert QUOTA_OFFSET_MM < QUOTA_LINE_MM, (QUOTA_OFFSET_MM, QUOTA_LINE_MM)


def test_the_elevation_is_not_pushed_so_far_it_floats_away():
    """Una quota a mezzo centimetro dal suo simbolo non è più la sua."""
    assert abs(QUOTA_OFFSET_MM - QUOTA_LINE_MM) < 3.0


# --------------- un numero per US, non uno per disegno (2026-10-09) --------

def test_the_number_appears_once_per_unit_not_once_per_drawing():
    """La vista US ha una riga per ogni **disegno**: sul sito di esempio
    482 poligoni per 51 unità. Senza raggruppare la tavola esce coperta
    da «36 36 36 36»."""
    from modules.utility.atlas_labels import us_show_expression

    espressione = us_show_expression(["area", "us", "gid"])
    assert espressione == '$area >= maximum($area, group_by:=concat("area", \'-\', "us"))'


def test_the_drawing_table_names_group_too():
    from modules.utility.atlas_labels import us_group_expression

    assert us_group_expression(["area_s", "us_s"]) == 'concat("area_s", \'-\', "us_s")'


def test_without_a_grouping_key_everything_is_labelled():
    """Meglio un numero ripetuto che nessun numero."""
    from modules.utility.atlas_labels import us_show_expression

    assert us_show_expression(["gid", "the_geom"]) is None


def test_the_grouping_prefers_the_record_names():
    from modules.utility.atlas_labels import us_group_expression

    assert '"area"' in us_group_expression(["area", "us", "area_s", "us_s"])


# ------------------------------------------- le promesse nel generatore

TM = _ROOT / "tabs" / "Gis_Time_controller.py"


def _corpo(nome: str) -> str:
    src = TM.read_text(encoding="utf-8")
    inizio = src.index("def %s" % nome)
    return src[inizio:src.index("\n    def ", inizio + 10)]


def test_the_sheet_labels_the_units_and_the_elevations():
    corpo = _corpo("_metti_le_etichette")
    assert "us_labeling(campi)" in corpo
    assert "quota_labeling(campi)" in corpo
    assert "PolygonGeometry" in corpo and "PointGeometry" in corpo


def test_the_project_is_left_as_it_was_found():
    """Le etichette si mettono sui layer del progetto, perché è quello
    che la mappa del layout disegna: lo stato di prima va rimesso."""
    src = TM.read_text(encoding="utf-8")
    assert "def _togli_le_etichette" in src
    corpo = _corpo("_metti_le_etichette")
    assert "layer.labeling(), layer.labelsEnabled()" in corpo
    generazione = _corpo("generate_images")
    assert "self._metti_le_etichette()" in generazione
    assert "self._togli_le_etichette()" in generazione
