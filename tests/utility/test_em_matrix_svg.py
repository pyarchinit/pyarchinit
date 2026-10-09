"""Il disegno della matrice in SVG: puro, senza dipendenze, leggibile.

È lo stesso disegno che la vista Qt mette a schermo, e serve anche
all'utente per salvare e stampare. Essendo testo, i test lo possono
leggere: è l'unico modo onesto di provare un disegno senza aprire una
finestra.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from modules.utility.em_matrix_layout import layout  # noqa: E402
from modules.utility.em_matrix_model import (  # noqa: E402
    Epoch,
    MatrixModel,
    Relation,
    Unit,
)
from modules.utility.em_matrix_svg import to_svg, write_svg  # noqa: E402


def _model(labels=("US1", "US2"), tipi=None, relazioni=(), epoca=True):
    tipi = tipi or {}
    unita = [Unit(node_id=l, label=l, node_type=tipi.get(l, "US"),
                  epoch_id="e" if epoca else None) for l in labels]
    return MatrixModel(
        units=unita,
        epochs=[Epoch("e", "XV secolo", 1451, 1499, "#FFF0F5")] if epoca else [],
        relations=[Relation(a, b, k) for a, b, k in relazioni],
        title="Scavo di prova")


def test_the_svg_is_well_formed_and_has_a_band_and_a_box_for_everything():
    lay = layout(_model())
    svg = to_svg(lay)
    assert svg.startswith("<svg") and svg.rstrip().endswith("</svg>")
    assert svg.count('class="unit"') == len(lay.boxes)
    assert svg.count('class="band"') == len(lay.bands)
    assert "XV secolo" in svg


def test_the_title_travels_when_asked():
    svg = to_svg(layout(_model()), title="Scavo archeologico")
    assert "Scavo archeologico" in svg


def test_each_type_is_drawn_with_the_shape_the_rules_say():
    lay = layout(_model(
        labels=("US1", "V1", "N1", "S1", "B1"),
        tipi={"V1": "USVs", "N1": "USVn", "S1": "SF", "B1": "BR"}))
    svg = to_svg(lay)
    assert "<rect" in svg                   # la US
    assert svg.count("<polygon") >= 4       # parallelogramma, esagono, ottagono, rombo
    assert "#9B3333" in svg                 # il bordo della US
    assert "#248FE7" in svg                 # il bordo della USVs


def test_the_round_types_are_drawn_round():
    lay = layout(_model(labels=("D1", "P1"), tipi={"D1": "document",
                                                   "P1": "property"}))
    svg = to_svg(lay)
    assert "<ellipse" in svg or "<circle" in svg


def test_every_relation_becomes_a_line():
    lay = layout(_model(relazioni=[("US1", "US2", "overlies")]))
    svg = to_svg(lay)
    assert svg.count("<polyline") == 1


def test_a_name_too_long_is_shortened_not_spilled():
    """Accorciato nel disegno, intero nel suggerimento: la casella è
    larga quanto è larga, ma il nome completo non si perde."""
    import re

    lay = layout(_model(labels=("1.Combinar9000000000000000",)))
    svg = to_svg(lay)
    disegnati = re.findall(r"<text[^>]*>([^<]*)</text>", svg)
    assert "1.Combinar9000000000000000" not in disegnati
    assert any("…" in t for t in disegnati), disegnati
    assert "<title>1.Combinar9000000000000000</title>" in svg


def test_what_must_be_escaped_is_escaped():
    lay = layout(_model(labels=('US <1> & "2"',)))
    svg = to_svg(lay)
    assert "&lt;1&gt;" in svg and "&amp;" in svg
    assert "<1>" not in svg


def test_an_empty_site_still_draws_a_page():
    lay = layout(MatrixModel(units=[], epochs=[], relations=[]))
    svg = to_svg(lay, title="vuoto")
    assert svg.startswith("<svg") and "vuoto" in svg


def test_writing_to_a_file_gives_back_the_path(tmp_path):
    lay = layout(_model())
    percorso = write_svg(lay, tmp_path / "matrice.svg", title="Prova")
    assert Path(percorso).exists()
    assert Path(percorso).read_text(encoding="utf-8").startswith("<svg")


def test_the_continuity_link_is_drawn_apart():
    """Il legame del nodo di continuità racconta una durata — quella US
    sopravvive dal suo periodo fino a qui — e non una sovrapposizione:
    si deve riconoscere a colpo d'occhio."""
    from modules.utility.em_matrix_model import Epoch

    model = MatrixModel(
        units=[Unit("c", "1.CON500", "BR", "recente"),
               Unit("u", "1.USM12", "US", "antica")],
        epochs=[Epoch("recente", "Fine XVI", 1550, 1599),
                Epoch("antica", "XV secolo", 1451, 1499)],
        relations=[Relation("c", "u", "is_after")])
    svg = to_svg(layout(model))
    assert 'class="edge continuity"' in svg


def test_an_ordinary_relation_is_not_marked_as_continuity():
    svg = to_svg(layout(_model(relazioni=[("US1", "US2", "overlies")])))
    assert "continuity" not in svg


def test_a_relation_carries_an_arrow_so_its_direction_is_readable():
    """Dalla review: il verso era affidato solo alla posizione verticale,
    che però la decide la fascia dell'epoca, non la stratigrafia. Dove le
    due si contraddicono, senza freccia non si capisce chi copre chi."""
    svg = to_svg(layout(_model(relazioni=[("US1", "US2", "overlies")])))
    assert 'class="punta"' in svg


def test_a_symmetric_relation_has_no_arrow():
    """«Uguale a» non ha un verso."""
    svg = to_svg(layout(_model(relazioni=[("US1", "US2", "equals")])))
    assert 'class="punta"' not in svg


def test_a_control_character_in_a_name_does_not_break_the_file():
    """Dalla review: un nome con un carattere di controllo produceva un
    SVG che nessun browser apre. Il carattere si toglie."""
    import xml.etree.ElementTree as ET

    svg = to_svg(layout(_model(labels=("\x01brutto",))))
    ET.fromstring(svg)          # non deve sollevare


def test_an_equality_comes_out_as_two_separate_horizontal_lines():
    """Il segno di uguale: due linee staccate, non una spezzata che le
    unisce in diagonale."""
    import re

    svg = to_svg(layout(_model(relazioni=[("US1", "US2", "equals")])))
    gruppo = re.search(r'<g class="edge equality">(.*?)</g>', svg, re.S)
    assert gruppo, svg
    assert gruppo.group(1).count("<line") == 2
    assert "marker-end=" not in svg


def _in_salita():
    """Un modello in cui la stratigrafia contraddice le epoche."""
    from modules.utility.em_matrix_model import Epoch, MatrixModel, Relation, Unit
    return MatrixModel(
        units=[Unit("antica", "US9", "US", "vecchia"),
               Unit("recente", "US1", "US", "nuova")],
        epochs=[Epoch("nuova", "Età moderna", 1600, 1799),
                Epoch("vecchia", "XV secolo", 1451, 1499)],
        relations=[Relation("antica", "recente", "overlies")])


def test_an_arrow_that_climbs_the_bands_is_drawn_in_red():
    """«Se ci sono frecce che puntano verso l'alto anziché verso il basso
    sono renderizzate in rosso, così uno vede immediatamente se ci sono
    errori» — E. Demetrescu, 2026-10-09."""
    svg = to_svg(layout(_in_salita()))
    salita = [r for r in svg.split("\n") if "edge salita" in r]
    assert salita, svg
    assert "#C0392B" in salita[0]
    # anche la punta è rossa, se no il verso resta grigio
    assert 'class="punta"' in salita[0]


def test_an_ordinary_arrow_is_not_red():
    """Il marcatore rosso sta sempre nei <defs>: quello che conta è che
    nessuna linea lo usi quando non c'è niente da segnalare."""
    svg = to_svg(layout(_model(relazioni=[("US1", "US2", "overlies")])))
    assert "edge salita" not in svg
    linee = [r for r in svg.split("\n") if "<polyline" in r]
    assert linee and not [r for r in linee if "#C0392B" in r]


def test_the_arrowheads_are_real_shapes_not_svg_markers():
    """Scoperto guardando l'atlante (2026-10-09): QGIS disegna gli SVG con
    QSvgRenderer, che è SVG Tiny 1.2 e **non conosce `<marker>`**. Le
    punte sparivano dalla tavola e la matrice perdeva il verso. Un
    poligono esplicito lo capiscono tutti, browser compresi."""
    svg = to_svg(layout(_model(relazioni=[("US1", "US2", "overlies")])))
    assert "<marker" not in svg
    assert "marker-end" not in svg
    punte = [r for r in svg.split("\n") if "punta" in r]
    assert punte, svg
    assert "<polygon" in punte[0]


def test_a_climbing_arrow_has_a_red_head():
    svg = to_svg(layout(_in_salita()))
    punte = [r for r in svg.split("\n") if "punta" in r]
    assert punte and "#C0392B" in punte[0]


def test_a_continuity_link_has_a_black_head():
    """Il legame di continuità si distingue anche nella punta."""
    from modules.utility.em_matrix_model import Epoch, MatrixModel, Relation, Unit

    model = MatrixModel(
        units=[Unit("c", "CON1", "BR", "e"), Unit("u", "US1", "US", "e")],
        epochs=[Epoch("e", "XV secolo", 1451, 1499)],
        relations=[Relation("c", "u", "overlies")])
    svg = to_svg(layout(model))
    punte = [r for r in svg.split("\n") if "punta" in r]
    assert punte and "#1A1A1A" in punte[0]


def test_an_equality_has_no_arrowhead_at_all():
    svg = to_svg(layout(_model(relazioni=[("US1", "US2", "equals")])))
    assert "punta" not in svg
