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


# ---- niente sovrapposizioni, e solo le US che si vedono (2026-10-09) ------

def test_one_label_per_unit_the_biggest_drawing():
    """La vista US ha una riga per ogni disegno: 482 poligoni per 37
    unità sul sito di esempio."""
    from modules.utility.atlas_labels import largest_per_group

    righe = [(1, ("1", "36"), 2.0, 5), (2, ("1", "36"), 9.0, 5),
             (3, ("1", "37"), 1.0, 6)]
    assert largest_per_group(righe) == {("1", "36"): 2, ("1", "37"): 3}


def test_at_equal_size_the_one_on_top_wins():
    """Se due disegni hanno la stessa area, si etichetta quello che si
    vede: il più recente."""
    from modules.utility.atlas_labels import largest_per_group

    righe = [(1, ("1", "36"), 4.0, 2), (2, ("1", "36"), 4.0, 9)]
    assert largest_per_group(righe)[("1", "36")] == 2


def test_rubbish_rows_do_not_break_the_count():
    from modules.utility.atlas_labels import largest_per_group

    assert largest_per_group([(1, ("a",), None, None), "non una riga"]) \
        .get(("a",)) == 1


def test_the_ids_become_an_expression_qgis_can_read():
    from modules.utility.atlas_labels import ids_expression

    assert ids_expression([3, 1, 1, 2]) == "$id IN (1, 2, 3)"


def test_nothing_to_label_is_not_an_expression():
    """Un filtro vuoto nasconderebbe tutto; `None` lascia il default."""
    from modules.utility.atlas_labels import ids_expression

    assert ids_expression([]) is None
    assert ids_expression(None) is None


def test_the_covered_units_are_worked_out_in_python_not_in_an_expression():
    """`overlay_within` su sé stesso è O(n²) e si rivaluta a ogni
    disegno: misurato, su 482 poligoni non finiva in due minuti."""
    import inspect

    from modules.utility import atlas_labels

    sorgente = inspect.getsource(atlas_labels)
    assert "overlay_within(" not in sorgente
    assert "QgsSpatialIndex" in sorgente
    assert "sopra.contains(mia)" in sorgente


def test_labels_move_instead_of_disappearing_when_they_collide():
    """Enzo: «le etichette non si devono mai sovrapporre; nel caso siano
    vicine usi una linea e la sposti». Con `OverPoint` QGIS scarta quelle
    in conflitto; servono posizioni alternative più il richiamo."""
    import inspect

    from modules.utility import atlas_labels

    sorgente = inspect.getsource(atlas_labels)
    assert "OrderedPositionsAroundPoint" in sorgente
    assert "QgsSimpleLineCallout" in sorgente
    assert "setEnabled(True)" in sorgente


def test_the_callout_line_only_shows_when_the_label_really_moved():
    """Una linea di richiamo lunga zero è solo sporcizia sul disegno."""
    from modules.utility.atlas_labels import CALLOUT_MIN_MM

    assert CALLOUT_MIN_MM > 0


def test_the_visible_set_is_recomputed_for_every_sheet():
    """Due ragioni, misurate tutte e due: quali US siano coperte dipende
    dal livello (1 etichetta su tutto il sito, 19 al livello 12), e gli
    **id delle feature cambiano quando cambia il filtro** — fra i due
    calcoli non ce n'era nemmeno uno in comune, ed è per questo che i
    numeri non comparivano affatto."""
    src = TM.read_text(encoding="utf-8")
    assert "def _aggiorna_etichette_us" in src
    assert "labelled_ids(layer)" in _corpo("_aggiorna_etichette_us")
    # e si chiama DOPO che il filtro del livello è stato applicato
    generazione = _corpo("generate_images")
    assert "self._aggiorna_etichette_us()" in generazione
    assert generazione.index("self.define_order_layer_value(value)") < \
        generazione.index("self._aggiorna_etichette_us()")
