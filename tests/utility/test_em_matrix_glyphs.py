"""I pittogrammi dell'Extended Matrix: quello che si può provare senza Qt.

Un disegno si prova guardandolo, ma la parte che decide **che cosa** si
disegna è dato puro: quali tipi hanno un pittogramma, quanti livelli ha,
con che colori, quanto viene grande la sua casella. Tutto questo esce
dalle regole visive della libreria e si legge qui, senza aprire una
finestra e senza costruire un widget.
"""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from modules.utility import em_matrix_glyphs as G  # noqa: E402


def _regole() -> dict:
    return json.loads(G.rules_path().read_text(encoding="utf-8"))


def test_the_module_needs_no_qt():
    """La ricerca del pittogramma è lettura di dati: deve potersi provare
    headless, e tutt'e due i disegnatori — l'SVG e la scena Qt — devono
    poterla chiedere allo stesso posto."""
    sorgente = (_ROOT / "modules" / "utility" / "em_matrix_glyphs.py").read_text(
        encoding="utf-8")
    moduli = set()
    for nodo in ast.walk(ast.parse(sorgente)):
        if isinstance(nodo, ast.Import):
            moduli |= {a.name for a in nodo.names}
        elif isinstance(nodo, ast.ImportFrom) and nodo.module:
            moduli.add(nodo.module)
    assert not [m for m in moduli if "qgis" in m or "Qt" in m], moduli


def test_the_glyphs_come_from_the_rules_and_not_from_a_table_of_ours():
    """Una tabella nostra prima o poi divergerebbe da quella di EMStudio:
    quanti livelli ha ciascun pittogramma lo dice il file."""
    regole = _regole()
    disegni = regole["2d_glyphs"]
    for tipo in ("extractor", "combiner", "document"):
        glifo = G.glyph_for(tipo)
        assert glifo is not None, tipo
        assert len(glifo.layers) == len(disegni[tipo]["layers"]), tipo
        assert list(glifo.view_box) == list(disegni[tipo]["viewBox"]), tipo
    assert len(G.glyph_for("extractor").layers) == 7
    assert len(G.glyph_for("combiner").layers) == 8
    assert len(G.glyph_for("document").layers) == 3


def test_the_aspect_is_the_one_the_layout_engine_reads():
    """``2d_render_glyph_types.aspect`` è quello su cui il motore di
    EMStudio misura la casella: il nostro impaginatore deve leggere lo
    stesso numero, se no la stessa matrice viene larga in due modi."""
    dichiarati = _regole()["2d_render_glyph_types"]["aspect"]
    for tipo in ("extractor", "combiner", "document"):
        assert G.glyph_for(tipo).aspect == pytest.approx(dichiarati[tipo])


def test_every_path_respects_the_contract_of_the_file():
    """«ABSOLUTE M / L / C / Z only»: se un tracciato non lo rispettasse,
    il writer SVG e la scena Qt lo interpreterebbero in due modi
    diversi."""
    for tipo in ("extractor", "combiner", "document"):
        for livello in G.glyph_for(tipo).layers:
            assert livello.commands
            for comando in livello.commands:
                assert comando[0] in ("M", "L", "C", "Z"), (tipo, comando)


def test_a_path_outside_the_contract_is_refused():
    """Un arco o un comando relativo non si indovinano: chi legge ripiega
    sulla forma geometrica, che è il ripiego che il file stesso
    dichiara."""
    with pytest.raises(ValueError):
        G.parse_path("M0 0 a 5 5 0 0 1 10 10")
    with pytest.raises(ValueError):
        G.parse_path("m0 0 l10 10")
    with pytest.raises(ValueError):
        G.parse_path("")


def test_the_colours_are_the_canonical_ones_of_the_language():
    """Non si ricolora niente: il grigio dell'Extended Matrix fa parte
    dell'identità del pittogramma (``_roles.ground`` → recolor false)."""
    estrattore = G.glyph_for("extractor")
    assert estrattore.layers[0].role == "ground"
    assert estrattore.layers[0].fill == "#888687"
    combinatore = G.glyph_for("combiner")
    assert combinatore.layers[0].role == "halo"
    assert combinatore.layers[0].opacity == pytest.approx(0.071)
    documento = G.glyph_for("document")
    assert [l.role for l in documento.layers] == ["paper", "border", "ink"]
    assert documento.layers[1].stroke == "#000000"
    assert documento.layers[1].stroke_width == pytest.approx(0.5)


def test_the_document_is_a_sheet_and_the_others_are_centred_icons():
    """Il documento ha i tracciati ma non è un'icona centrata: il suo nome
    si scrive SOPRA il foglio. Metterlo fra i ``types`` lo ridurrebbe a
    «…», che è esattamente la ragione per cui il file gli dà un elenco
    suo."""
    assert G.is_sheet("document")
    assert not G.is_sheet("extractor")
    assert not G.is_sheet("combiner")
    assert G.is_glyph("extractor") and G.is_glyph("combiner")


def test_the_property_has_no_glyph_and_never_will():
    """«`property` is NOT here and will not be: a text annotation in a
    bracket, whose width its text decides»."""
    assert G.glyph_for("property") is None
    assert "property" not in _regole()["2d_glyphs"]
    assert G.is_property("property")


def test_contain_fits_the_viewbox_and_centres_it():
    glifo = G.glyph_for("document")
    vx, vy, vw, vh = glifo.view_box
    scala, dx, dy = G.contain(glifo, 10.0, 20.0, 100.0, 50.0)
    assert scala == pytest.approx(min(100.0 / vw, 50.0 / vh))
    # il disegno sta dentro la casella e ci sta in mezzo
    assert dx + vx * scala == pytest.approx(10.0 + (100.0 - vw * scala) / 2)
    assert dy + vy * scala == pytest.approx(20.0 + (50.0 - vh * scala) / 2)


def test_a_glyph_box_is_driven_by_its_height():
    """«a glyph drawn 32 wide inside a 90x32 box leaves empty margins, and
    the connect handle ends up floating away from the glyph»."""
    for tipo in ("extractor", "combiner", "document"):
        larghezza, altezza = G.box_size(tipo, "qualunque", 132.0, 36.0)
        assert altezza == 36.0
        assert larghezza == pytest.approx(36.0 * G.glyph_for(tipo).aspect)
    assert G.box_size("document", "x", 132.0, 36.0)[0] < 36.0  # 0,636


def test_a_stratigraphic_unit_keeps_the_box_it_always_had():
    """Il punto della modifica: i pittogrammi cambiano, la matrice no."""
    for tipo in ("US", "USM", "USVs", "SF", "BR", ""):
        assert G.box_size(tipo, "US 1234", 132.0, 36.0) == (132.0, 36.0)


def test_the_property_is_as_wide_as_its_text():
    corta = G.box_size("property", "a", 132.0, 36.0)[0]
    lunga = G.box_size("property", "1.property800", 132.0, 36.0)[0]
    assert corta < lunga <= 132.0
    # il braccio della parentesi c'è sempre, anche per un nome di una lettera
    assert corta >= 36.0 * G.PROP_ARM


def test_the_property_bracket_is_open_on_the_right_like_the_drawing():
    """``src/2D/property.svg``: il campo grigio è chiuso, la parentesi no —
    borda solo il lato sinistro, ed è quello che la fa leggere come una
    parentesi invece che come una casella."""
    disegno = G.property_drawing(0.0, 0.0, 120.0, 36.0)
    assert disegno.field_d.endswith("Z")
    assert "Z" not in disegno.bracket_d
    assert disegno.fill == "#DEDDDE" and disegno.stroke == "#000000"
    # i due tracciati rispettano lo stesso contratto dei pittogrammi
    for d in (disegno.field_d, disegno.bracket_d):
        for comando in G.parse_path(d):
            assert comando[0] in ("M", "L", "C", "Z")
    # il testo comincia dopo il braccio e finisce dentro il campo
    assert disegno.text_x > 36.0 * G.PROP_ARM
    assert disegno.text_right < 120.0


def test_the_name_of_a_glyph_is_counted_in_the_canvas():
    """Il nome di un foglio è più largo del foglio e non si taglia: se la
    tela non lo contasse, l'ultimo documento a destra perderebbe metà del
    nome fuori dall'immagine (visto sull'anteprima del sito di esempio)."""
    larghezza, _h = G.box_size("document", "1.DOC4001", 132.0, 36.0)
    assert G.label_overhang("document", "1.DOC4001", larghezza) > 0
    assert G.label_overhang("US", "1.USM12", 132.0) == 0.0
