"""La matrice costruita dai record, senza passare da un file (2026-10-09).

Il Time Manager ha in mano le US visibili a una certa posizione del
cursore e i periodi del sito: non un em.json. Serve la stessa matrice
che il pannello disegna, ma a partire da quelle righe — e senza
Graphviz, che costa un sottoprocesso e un JPEG da megabyte a ogni
rigenerazione.

Tutto puro: nessun database, nessun Qt.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from modules.utility.em_matrix_records import model_from_records  # noqa: E402

PERIODI = [
    # periodo, fase, datazione_estesa, cron_iniziale, cron_finale
    ("1", "1", "Età moderna", 1600, 1799),
    ("2", "1", "XV secolo", 1451, 1499),
]


def _rec(us, **extra):
    base = dict(sito="Alfa", area="1", us=us, unita_tipo="US",
                periodo_iniziale="2", fase_iniziale="1", rapporti="[]",
                d_stratigrafica="", d_interpretativa="")
    base.update(extra)
    return base


def test_each_record_becomes_a_unit_in_its_period():
    model = model_from_records([_rec("1"), _rec("2")], PERIODI)
    assert [u.label for u in model.units] == ["1.US1", "1.US2"]
    assert {u.epoch_id for u in model.units} == {"2_1"}
    assert [e.name for e in model.epochs] == ["Età moderna", "XV secolo"]


def test_the_periods_carry_their_years():
    model = model_from_records([_rec("1")], PERIODI)
    moderna = next(e for e in model.epochs if e.name == "Età moderna")
    assert (moderna.start, moderna.end) == (1600.0, 1799.0)


def test_covers_becomes_a_relation_that_goes_down():
    model = model_from_records(
        [_rec("1", rapporti="[['Copre', '2', '1', 'Alfa']]"), _rec("2")],
        PERIODI)
    assert len(model.relations) == 1
    r = model.relations[0]
    assert (r.source, r.target, r.kind) == ("1.US1", "1.US2", "overlies")


def test_covered_by_is_turned_around():
    """«Coperto da» dice la stessa cosa dall'altro capo: nella matrice la
    freccia parte da chi copre, se no il verso si capovolge."""
    model = model_from_records(
        [_rec("1", rapporti="[['Coperto da', '2', '1', 'Alfa']]"), _rec("2")],
        PERIODI)
    r = model.relations[0]
    assert (r.source, r.target, r.kind) == ("1.US2", "1.US1", "overlies")


def test_cuts_fills_abuts_and_equals_keep_their_own_kind():
    casi = {
        "Taglia": "cuts", "Riempie": "fills", "Si appoggia a": "abuts",
        "Uguale a": "equals", "Si lega a": "bonded_to",
    }
    for voce, atteso in casi.items():
        model = model_from_records(
            [_rec("1", rapporti="[['%s', '2', '1', 'Alfa']]" % voce),
             _rec("2")], PERIODI)
        assert model.relations, voce
        assert model.relations[0].kind == atteso, (voce, model.relations[0].kind)


def test_a_relation_to_a_unit_that_is_not_there_is_dropped():
    """Il Time Manager mostra solo le US fino a una certa posizione: un
    rapporto verso una US che non è nel disegno non si può disegnare."""
    model = model_from_records(
        [_rec("1", rapporti="[['Copre', '99', '1', 'Alfa']]")], PERIODI)
    assert model.relations == []
    assert model.warnings


def test_only_the_visible_units_are_drawn():
    model = model_from_records(
        [_rec("1"), _rec("2"), _rec("3")], PERIODI,
        visible={("1", "2"), ("1", "3")})
    assert [u.label for u in model.units] == ["1.US2", "1.US3"]


def test_the_short_form_of_rapporti_still_works():
    """Nel database convivono le voci a due elementi e quelle a quattro:
    la forma corta prende l'area del record (lezione della 5.13.35)."""
    model = model_from_records(
        [_rec("1", rapporti="[['Copre', '2']]"), _rec("2")], PERIODI)
    assert model.relations[0].target == "1.US2"


def test_a_broken_rapporti_cell_does_not_stop_the_drawing():
    model = model_from_records(
        [_rec("1", rapporti="non è una lista"), _rec("2")], PERIODI)
    assert len(model.units) == 2
    assert model.warnings


def test_the_unit_type_decides_the_symbol_and_the_label():
    """L'etichetta porta il tipo, come nell'em.json: «1.USM12», non
    «1.US12» — se no una USM 12 e una US 12 della stessa area sarebbero
    indistinguibili nel disegno."""
    model = model_from_records(
        [_rec("1", unita_tipo="USVs"), _rec("2", unita_tipo="USM")], PERIODI)
    tipi = {u.label: u.node_type for u in model.units}
    assert tipi["1.USVs1"] == "USVs"
    assert tipi["1.USM2"] == "USM"


def test_legacy_usv_codes_are_converted():
    """USVA/USVB/USVC sono la vecchia scrittura: nella matrice devono
    avere la forma giusta, come nell'export (5.13.35)."""
    model = model_from_records(
        [_rec("1", unita_tipo="USVA"), _rec("2", unita_tipo="USVB")], PERIODI)
    tipi = {u.label: u.node_type for u in model.units}
    assert tipi["1.USVs1"] == "USVs"
    assert tipi["1.USVn2"] == "USVn"


def test_a_record_without_a_period_still_gets_drawn():
    """Una US senza periodo non deve sparire dalla matrice: finisce fuori
    dalle fasce, ma c'è."""
    model = model_from_records(
        [_rec("1", periodo_iniziale="", fase_iniziale="")], PERIODI)
    assert len(model.units) == 1
    assert model.units[0].epoch_id is None


def test_the_record_text_travels_with_the_unit():
    model = model_from_records(
        [_rec("1", d_stratigrafica="strato di crollo",
              d_interpretativa="crollo del tetto")], PERIODI)
    dati = model.units[0].data
    assert dati["d_stratigrafica"] == "strato di crollo"
    assert dati["us"] == "1" and dati["area"] == "1" and dati["sito"] == "Alfa"


def test_no_records_is_an_empty_matrix_not_a_crash():
    model = model_from_records([], PERIODI)
    assert model.units == [] and model.relations == []


def test_the_model_can_be_laid_out_and_drawn():
    """La prova che conta: lo stesso impaginatore e lo stesso writer del
    pannello, senza Graphviz e senza sottoprocessi."""
    from modules.utility.em_matrix_layout import layout
    from modules.utility.em_matrix_svg import to_svg

    model = model_from_records(
        [_rec("1", rapporti="[['Copre', '2', '1', 'Alfa']]"),
         _rec("2", periodo_iniziale="1")], PERIODI)
    svg = to_svg(layout(model), "Prova")
    assert svg.startswith("<svg") and "</svg>" in svg
    assert "1.US1" in svg and "XV secolo" in svg


# ------------- le tabelle non devono divergere da quelle di prima ----------

def test_the_relation_table_matches_the_library():
    """Noi e la libreria leggiamo lo stesso vocabolario: se un giorno uno
    dei due cambia l'ordine delle voci, questo test lo dice prima che la
    matrice disegni frecce al contrario."""
    import sys as _sys
    _ext = _ROOT / "ext_libs"
    if str(_ext) not in _sys.path:
        _sys.path.insert(0, str(_ext))
    try:
        from s3dgraphy.rapporti import _REL_INDEX_EDGE_TYPE
    except Exception:                               # noqa: BLE001
        import pytest
        pytest.skip("la libreria s3dgraphy non è importabile qui")

    from modules.utility.em_matrix_records import REL_INDEX_KIND

    # la libreria nomina a parte le forme inverse; noi le giriamo
    atteso = {
        "equals": ("equals", False), "bonded_to": ("bonded_to", False),
        "overlies": ("overlies", False), "is_overlain_by": ("overlies", True),
        "fills": ("fills", False), "is_filled_by": ("fills", True),
        "cuts": ("cuts", False), "is_cut_by": ("cuts", True),
        "abuts": ("abuts", False), "is_abutted_by": ("abuts", True),
        # is_before è la lettura inversa di is_after: si gira, come
        # is_overlain_by rispetto a overlies
        "is_after": ("is_after", False), "is_before": ("is_after", True),
    }
    assert len(REL_INDEX_KIND) == len(_REL_INDEX_EDGE_TYPE)
    for indice, nome in enumerate(_REL_INDEX_EDGE_TYPE):
        assert REL_INDEX_KIND[indice] == atteso[nome], (indice, nome)


def test_the_legacy_unit_types_match_the_migration():
    """Terza copia della stessa mappa: va tenuta legata alle altre."""
    import sys as _sys
    if str(_ROOT) not in _sys.path:
        _sys.path.insert(0, str(_ROOT))
    try:
        from scripts.migrations._2026_05_us_vocabulary_alignment_lib import (
            REPLACEMENTS)
    except Exception:                               # noqa: BLE001
        import pytest
        pytest.skip("la libreria della migrazione non è importabile qui")

    from modules.utility.em_matrix_records import LEGACY_UNITA_TIPO

    for vecchio, nuovo in REPLACEMENTS.items():
        assert LEGACY_UNITA_TIPO.get(vecchio) == nuovo, vecchio


def test_every_relation_kind_is_one_the_matrix_knows():
    """Un tipo che l'impaginatore non conosce sarebbe un rapporto che
    sparisce dal disegno senza dirlo."""
    from modules.utility.em_matrix_model import STRATIGRAPHIC_KINDS
    from modules.utility.em_matrix_records import REL_INDEX_KIND

    for kind, _girare in REL_INDEX_KIND:
        assert kind in STRATIGRAPHIC_KINDS, kind


def test_the_matrix_is_written_as_svg_without_any_subprocess(tmp_path):
    """La via del Time Manager: dai record al file, senza Graphviz."""
    from modules.utility.em_matrix_records import write_matrix_svg

    percorso, model = write_matrix_svg(
        [_rec("1", rapporti="[['Copre', '2', '1', 'Alfa']]"),
         _rec("2", periodo_iniziale="1")],
        PERIODI, tmp_path / "matrice.svg", title="Periodo 2")
    testo = Path(percorso).read_text(encoding="utf-8")
    assert testo.startswith("<svg") and "Periodo 2" in testo
    assert len(model.units) == 2 and len(model.relations) == 1


# ------------- le US che servono solo ad agganciare (2026-10-09) ------------

def test_a_unit_outside_the_view_is_drawn_but_dimmed():
    """Enzo: «nel matrix devono comparire le US che si visualizzano; quelle
    che non sono presenti ma servono per agganciare i nodi devono essere
    opacizzate, per far intendere che non sono visibili nella mappa».

    Senza di loro il rapporto sparirebbe e la sequenza sembrerebbe rotta;
    disegnate come le altre, sembrerebbero sulla mappa."""
    model = model_from_records(
        [_rec("1", rapporti="[['Copre', '2', '1', 'Alfa']]"), _rec("2")],
        PERIODI, visible={("1", "1")})
    etichette = {u.label: u for u in model.units}
    assert set(etichette) == {"1.US1", "1.US2"}
    assert etichette["1.US1"].dimmed is False
    assert etichette["1.US2"].dimmed is True
    # e il rapporto si disegna
    assert len(model.relations) == 1


def test_a_unit_that_points_at_a_visible_one_is_a_bridge_too():
    """Il legame vale nei due versi: anche chi copre una US visibile serve
    ad agganciarla."""
    model = model_from_records(
        [_rec("1"), _rec("2", rapporti="[['Copre', '1', '1', 'Alfa']]")],
        PERIODI, visible={("1", "1")})
    etichette = {u.label: u.dimmed for u in model.units}
    assert etichette == {"1.US1": False, "1.US2": True}


def test_the_bridges_do_not_bring_their_own_bridges():
    """Un salto solo: se no una US visibile tirerebbe dentro mezzo scavo."""
    model = model_from_records(
        [_rec("1", rapporti="[['Copre', '2', '1', 'Alfa']]"),
         _rec("2", rapporti="[['Copre', '3', '1', 'Alfa']]"),
         _rec("3")],
        PERIODI, visible={("1", "1")})
    assert {u.label for u in model.units} == {"1.US1", "1.US2"}


def test_without_a_filter_nothing_is_dimmed():
    model = model_from_records([_rec("1"), _rec("2")], PERIODI)
    assert all(not u.dimmed for u in model.units)


def test_a_dimmed_unit_is_drawn_faded_in_the_svg():
    from modules.utility.em_matrix_layout import layout
    from modules.utility.em_matrix_svg import to_svg

    model = model_from_records(
        [_rec("1", rapporti="[['Copre', '2', '1', 'Alfa']]"), _rec("2")],
        PERIODI, visible={("1", "1")})
    svg = to_svg(layout(model))
    sbiadite = [r for r in svg.split("\n") if "unit fuori" in r]
    assert len(sbiadite) == 1
    assert "opacity" in sbiadite[0]
    assert "1.US2" in sbiadite[0]
