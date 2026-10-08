"""La vista Qt della matrice: le promesse che si possono provare senza
aprire una finestra.

Come per il pannello della stanza, qui non si istanzia nessun widget: si
leggono le promesse nel sorgente. Quello che la vista disegna è già
provato dai test puri dell'impaginatore e del writer SVG.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

VIEW = _ROOT / "modules" / "utility" / "em_matrix_view.py"


def _source() -> str:
    return VIEW.read_text(encoding="utf-8")


def _imported_modules():
    import ast

    nomi = set()
    for nodo in ast.walk(ast.parse(_source())):
        if isinstance(nodo, ast.Import):
            nomi |= {a.name for a in nodo.names}
        elif isinstance(nodo, ast.ImportFrom) and nodo.module:
            nomi.add(nodo.module)
    return nomi


def test_the_view_needs_no_web_engine():
    """È il punto della richiesta di Enzo: vedere la matrice dentro QGIS
    senza EMStudio, senza nodo e senza motore web. Si guardano gli
    import, non le parole: la ragione per cui non c'è sta scritta nelle
    righe di commento."""
    moduli = _imported_modules()
    assert not [m for m in moduli if "WebEngine" in m or "WebKit" in m], moduli


def test_the_view_draws_the_layout_and_does_not_reread_the_file():
    """La vista prende quello che l'impaginatore ha deciso: così quello
    che si vede è esattamente quello che i test puri hanno provato."""
    src = _source()
    assert "read_em_json" not in src
    assert "em_matrix_layout" in src


def test_saving_the_svg_goes_through_the_pure_writer():
    src = _source()
    assert "em_matrix_svg" in src
    assert "write_svg" in src


def test_every_box_carries_its_node_id():
    """Cliccare una casella deve poter dire quale unità è: l'id viaggia
    sull'elemento grafico, non in una tabella parallela."""
    src = _source()
    assert "setData(" in src
    assert "node_id" in src


def test_the_view_does_not_depend_on_graphviz_or_matplotlib():
    moduli = _imported_modules()
    for estranea in ("graphviz", "matplotlib", "pydot", "networkx"):
        assert not [m for m in moduli if estranea in m], (estranea, moduli)
