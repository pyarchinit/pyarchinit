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


def test_the_paradata_types_are_drawn_as_em_draws_them():
    """Documento e proprietà non sono una ellisse e un cerchio.

    Fino al 5.13.72-alpha si disegnavano con la forma di ripiego di
    ``node_styles`` — il file la chiama «the ripiego for consumers that
    cannot draw paths» — mentre l'Extended Matrix li disegna: il
    documento è un foglio con l'angolo piegato (``2d_glyphs.document``),
    la proprietà è una annotazione fra parentesi. Noi i tracciati li
    sappiamo disegnare.
    """
    lay = layout(_model(labels=("D1", "P1"), tipi={"D1": "document",
                                                   "P1": "property"}))
    svg = to_svg(lay)
    assert "<ellipse" not in svg and "<circle" not in svg
    assert 'class="glifo"' in svg            # il foglio
    assert 'class="parentesi"' in svg        # la proprietà
    assert "#DEDDDE" in svg                  # il campo della proprietà


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


def _testo_y(svg: str, nome: str) -> float:
    """L'ordinata della riga di testo che porta quel nome."""
    import re

    trovato = re.search(r'<text x="[-\d.]+" y="([-\d.]+)"[^>]*>%s</text>' % nome,
                        svg)
    assert trovato, (nome, svg[:200])
    return float(trovato.group(1))


def test_the_extractor_and_the_combiner_are_their_pictogram():
    """Non un pentagono e un esagono — che sono il ripiego di
    ``node_styles`` — ma il disegno del manuale dell'Extended Matrix,
    livello per livello, con i colori che il file si porta."""
    lay = layout(_model(labels=("E1", "C1"), tipi={"E1": "extractor",
                                                   "C1": "combiner"}))
    svg = to_svg(lay)
    assert svg.count('class="glifo"') == 2
    assert "#888687" in svg                 # il grigio dell'estrattore
    assert "#868384" in svg                 # il grigio del combinatore
    assert 'opacity="0.071"' in svg         # il velo del combinatore
    # sette livelli più otto: il disegno è tutto lì, niente immagini
    assert svg.count("<path d=") >= 15


def test_a_centred_icon_writes_its_name_under_the_drawing():
    """È quello che fa l'esportatore SVG di EMStudio per i ``types``: il
    nome sotto l'icona, perché l'icona è il nodo."""
    lay = layout(_model(labels=("E1",), tipi={"E1": "extractor"}))
    casella = [b for b in lay.boxes if b.unit.node_id == "E1"][0]
    assert _testo_y(to_svg(lay), "E1") > casella.y + casella.h


def test_the_document_writes_its_name_on_the_sheet():
    """Il nome del documento sta SUL foglio, al 62% della sua altezza:
    è la ragione per cui il file lo tiene fuori dai ``types``."""
    lay = layout(_model(labels=("Fotografie",), tipi={"Fotografie": "document"}))
    casella = lay.boxes[0]
    y = _testo_y(to_svg(lay), "Fotografie")
    assert casella.y < y < casella.y + casella.h


def test_the_stratigraphic_units_are_drawn_exactly_as_before():
    """Il patto della modifica: i paradati prendono il loro disegno, la
    matrice delle unità stratigrafiche non si muove di un pixel."""
    lay = layout(_model(labels=("US1", "US2"),
                        relazioni=[("US1", "US2", "overlies")]))
    svg = to_svg(lay)
    assert 'class="glifo"' not in svg and 'class="parentesi"' not in svg
    for casella in lay.boxes:
        assert (casella.w, casella.h) == (132.0, 36.0)
        assert _testo_y(svg, casella.unit.label) == casella.y + casella.h / 2 + 4


def test_the_background_is_a_valid_length_not_a_double_percent():
    """Lo sfondo della matrice esce **trasparente**.

    La riga era `'<rect width="100%%" ...>'`: un `%%` si scrive così
    dentro una stringa di formato, ma questa non lo è — nessun `%` la
    interpola — e il doppio per cento finisce **letterale** nel file.
    `width="100%%"` non è una lunghezza SVG valida, quindi il rettangolo
    di fondo non si dipinge.

    Misurato con `rsvg-convert` sulla matrice del sito di esempio: il
    pixel in alto a sinistra era `(0, 0, 0, 0)` — trasparente — invece
    del `#FBFCFE` dichiarato. Su un visualizzatore bianco non si nota;
    in modalità scura, o dentro un PDF, il disegno galleggia su quello
    che c'è dietro.
    """
    svg = to_svg(layout(_model()), title="Scavo archeologico")
    assert "100%%" not in svg
    assert '<rect width="100%" height="100%" fill="#FBFCFE"/>' in svg


# ---------------------------------------------------------------------------
# Le linee dicono che rapporto sono (Enzo, 12 ottobre 2026)
# ---------------------------------------------------------------------------
# «I nodi em come property, combinar, extractor e doc dovrebbero avere
# archi dot line non continue; le USM un bordo di colore diverso dal rosso;
# i tagli un arco dot line, magari verde». La sequenza — copre, riempie, si
# appoggia — resta grigia e piena: è la matrice. Tutto il resto si
# distingue dalla linea, non dalla posizione.

def _polilinee(svg, classe):
    import re
    return re.findall(r'<g class="%s"><polyline[^>]*>' % re.escape(classe), svg)


def test_a_cut_is_a_dotted_green_line():
    svg = to_svg(layout(_model(labels=("T1", "US2"),
                               relazioni=(("T1", "US2", "cuts"),))))
    linee = _polilinee(svg, "edge cut")
    assert len(linee) == 1, svg
    assert 'stroke="#2F8F4E"' in linee[0]
    assert 'stroke-dasharray="2 4"' in linee[0]


def test_the_sequence_stays_grey_and_solid():
    svg = to_svg(layout(_model(relazioni=(("US1", "US2", "overlies"),))))
    linee = _polilinee(svg, "edge")
    assert len(linee) == 1, svg
    assert 'stroke="#6B7684"' in linee[0]
    assert "stroke-dasharray" not in linee[0]


def test_paradata_edges_take_the_library_style_and_are_never_solid():
    """Lo stile per arco sta in `em_visual_rules.json` e si adotta:
    `extracted_from` punteggiato bruno, `has_data_provenance` tratteggiato
    arancio, `has_property` tratteggiato oro, `generic_connection`
    tratteggiato grigio. `combines` nel file è **continuo**: qui è
    tratteggiato lo stesso, perché un arco verso un paradato non deve mai
    sembrare una sovrapposizione — è l'unica deroga, e si dichiara."""
    tipi = {"E1": "extractor", "D1": "document", "P1": "property",
            "C1": "combiner", "N1": "USVn"}
    svg = to_svg(layout(_model(
        labels=("US1", "E1", "D1", "P1", "C1", "N1"), tipi=tipi,
        relazioni=(("E1", "D1", "extracted_from"),
                   ("P1", "E1", "has_data_provenance"),
                   ("US1", "P1", "has_property"),
                   ("N1", "C1", "generic_connection"),
                   ("C1", "E1", "combines")))))
    linee = _polilinee(svg, "edge paradata")
    assert len(linee) == 5, svg
    colori = {l.split('stroke="')[1].split('"')[0] for l in linee}
    assert colori == {"#A52A2A", "#FFA500", "#FFD700", "#808080", "#FF6347"}, colori
    for l in linee:
        assert "stroke-dasharray" in l, l


def test_an_upward_cut_is_red_but_still_dotted():
    """Il rosso della salita vince sul colore, non sulla linea: un taglio
    che risale è una contraddizione **e** un taglio."""
    m = MatrixModel(
        units=[Unit("T1", "T1", "US", "vecchia"), Unit("US2", "US2", "US", "nuova")],
        epochs=[Epoch("nuova", "XV", 1451, 1499, "#FFF"),
                Epoch("vecchia", "XIV", 1351, 1399, "#FFF")],
        relations=[Relation("T1", "US2", "cuts")], title="t")
    svg = to_svg(layout(m))
    linee = _polilinee(svg, "edge salita cut")
    assert len(linee) == 1, svg
    assert 'stroke-dasharray="2 4"' in linee[0]


# ---------------------------------------------------------------------------
# Il bordo delle USM
# ---------------------------------------------------------------------------

def test_a_wall_unit_has_a_brown_border_in_every_language():
    """Il tipo del nodo è «US» per tutte; `data.unita_tipo` dice se è una
    muratura — USM, WSU, MSE, UEM, USZ, ΤΣΜ, la tabella delle lingue."""
    for sigla in ("USM", "WSU", "MSE", "UEM", "USZ", "ΤΣΜ"):
        u = Unit("M1", "M1", "US", "e", data={"unita_tipo": sigla})
        m = MatrixModel(units=[u], epochs=[Epoch("e", "XV", 1451, 1499, "#FFF")],
                        relations=[], title="t")
        svg = to_svg(layout(m))
        assert 'stroke="#7A4B1D"' in svg, sigla
        assert 'stroke="#9B3333"' not in svg, sigla


def test_a_plain_unit_keeps_the_red_border():
    u = Unit("US1", "US1", "US", "e", data={"unita_tipo": "US"})
    m = MatrixModel(units=[u], epochs=[Epoch("e", "XV", 1451, 1499, "#FFF")],
                    relations=[], title="t")
    assert 'stroke="#9B3333"' in to_svg(layout(m))


def test_the_continuity_diamond_carries_no_printed_label():
    """Un rombo nero piccolo, senza nome sopra: il nome resta nel
    `<title>` per chi ci passa col mouse. La riga della USM 12 sotto di
    lui dice già di chi è."""
    import re
    svg = to_svg(layout(_model(labels=("B1", "US1"), tipi={"B1": "BR"},
                               relazioni=(("B1", "US1", "is_after"),))))
    gruppo = re.search(r'<g class="unit" data-id="B1">.*?</g>', svg, re.S)
    assert gruppo, svg
    assert "<text" not in gruppo.group(0), gruppo.group(0)
    assert "<title>B1</title>" in gruppo.group(0)
    altro = re.search(r'<g class="unit" data-id="US1">.*?</g>', svg, re.S)
    assert "<text" in altro.group(0)
