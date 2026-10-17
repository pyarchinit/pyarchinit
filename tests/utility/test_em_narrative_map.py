"""La mappa interattiva nell'HTML della narrativa (Enzo, 13 ottobre 2026):
SVG dei disegni delle unità, periodi dagli archi del grafo, innesto
nell'HTML della libreria (menzioni → link, capitoli con l'epoca, CSS e
JavaScript inline). Parte pura: niente QGIS."""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
for _p in (_ROOT / "ext_libs",):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

pytest.importorskip("s3dgraphy")
from modules.s3dgraphy import em_narrative_map as nm  # noqa: E402


def _grafo():
    from s3dgraphy.graph import Graph
    from s3dgraphy.nodes.epoch_node import EpochNode
    from s3dgraphy.nodes.stratigraphic_node import StratigraphicUnit
    g = Graph(graph_id="Villa")
    g.add_node(EpochNode("epoch_1_1", "Età romana", -100, 300))
    g.add_node(EpochNode("epoch_2_1", "Medioevo", 500, 1400))
    for uid, nome, us, epoca in (("u1", "1.US1", "1", "epoch_2_1"), ("u2", "1.US2", "2", "epoch_1_1"),
                                 ("u3", "1.US3", "3", "epoch_1_1")):
        n = StratigraphicUnit(uid, nome)
        n.data = {"sito": "Villa", "area": "1", "us": us}
        g.add_node(n)
        g.add_edge(uid + "_fe", uid, epoca, "has_first_epoch")
    g.add_edge("u2_se", "u2", "epoch_2_1", "survive_in_epoch")      # la 2 sopravvive nel Medioevo
    return g


def test_i_periodi_delle_unita_vengono_dagli_archi():
    g = _grafo()
    assert nm.epochs_of(g) == {"u1": ["epoch_2_1"], "u2": ["epoch_1_1", "epoch_2_1"], "u3": ["epoch_1_1"]}
    assert nm.epoch_names(g) == {"epoch_1_1": "Età romana", "epoch_2_1": "Medioevo"}
    meta = nm.units_meta(g)
    assert meta["u2"] == {"name": "1.US2", "number": "2", "area": "1", "sito": "Villa", "unita_tipo": "",
                          "epochs": ["epoch_1_1", "epoch_2_1"]}


def test_l_svg_porta_un_path_per_disegno_e_un_etichetta_per_unita():
    disegni = [nm.Drawing("u1", [[(10.0, 20.0), (14.0, 20.0), (14.0, 23.0), (10.0, 23.0)]], (12.0, 21.5)),
               nm.Drawing("u2", [[(0.0, 0.0), (4.0, 0.0), (4.0, 4.0), (0.0, 4.0)],
                                 [(1.0, 1.0), (2.0, 1.0), (2.0, 2.0), (1.0, 2.0)]], (3.0, 3.0))]
    meta = {"u1": {"number": "1", "name": "1.US1", "epochs": ["epoch_2_1"]},
            "u2": {"number": "2", "name": "1.US2", "epochs": ["epoch_1_1", "epoch_2_1"]}}
    svg, box = nm.svg_map(disegni, meta)
    assert svg.startswith("<svg") and 'viewBox="0 0 14 23"' in svg
    # y capovolta: il punto (10,20) → (10, 3); l'anello interno è un secondo sotto-percorso
    assert 'data-u="u1" data-e="epoch_2_1" d="M10 3L14 3L14 0L10 0Z"' in svg
    assert 'data-u="u2" data-e="epoch_1_1 epoch_2_1" d="M0 23L4 23L4 19L0 19ZM1 22L2 22L2 21L1 21Z"' in svg
    assert '<text class="l" data-u="u1" data-e="epoch_2_1" x="12" y="1.5">1</text>' in svg
    assert box["all"] == [0, 0, 14, 23]
    assert box["epoch_2_1"] == [0, 0, 14, 23] and box["epoch_1_1"] == [0, 19, 4, 4]


def test_l_innesto_lega_menzioni_e_capitoli_alla_mappa():
    html = ('<html lang="it"><head><meta charset="utf-8"><style>body{}</style></head><body>\n'
            '<h1>Villa</h1>\n<h2>Presentazione</h2><p>Testo.</p>'
            '<h2>Età romana</h2><p>Sotto <em class="em-mention">1.US2</em> e <em class="em-mention">1.US3</em>.</p>'
            '<h2>Medioevo</h2><p>Poi <em class="em-mention">1.US1</em> taglia <em class="em-mention">1.US2</em>; '
            '<em class="em-mention">Ignota</em>.</p>'
            '<section class="em-sources"><h2>Fonti</h2><ul></ul></section></body></html>')
    capitoli = [{"title": "Presentazione", "epoch": None, "units": []},
                {"title": "Età romana", "epoch": "epoch_1_1", "units": ["u2", "u3"]},
                {"title": "Medioevo", "epoch": "epoch_2_1", "units": ["u1", "u2"]}]
    meta = {"u1": {"name": "1.US1", "number": "1", "epochs": ["epoch_2_1"]},
            "u2": {"name": "1.US2", "number": "2", "epochs": ["epoch_1_1", "epoch_2_1"]},
            "u3": {"name": "1.US3", "number": "3", "epochs": ["epoch_1_1"]}}
    fuori = nm.inject_map(html, "<svg id=\"pya-svg\"></svg>", {"all": [0, 0, 1, 1]}, capitoli, meta,
                          {"epoch_1_1": "Età romana", "epoch_2_1": "Medioevo"}, lang="it")
    assert '<a class="em-mention pya-u" href="#pya-map" data-u="u2" data-e="epoch_1_1">1.US2</a>' in fuori
    assert '<a class="em-mention pya-u" href="#pya-map" data-u="u2" data-e="epoch_2_1">1.US2</a>' in fuori
    assert '<em class="em-mention">Ignota</em>' in fuori                   # non risolta: resta com'è
    assert '<h2 id="pya-cap-1" class="pya-cap" data-e="epoch_1_1" data-units="u2 u3">Età romana</h2>' in fuori
    assert '<h2 id="pya-cap-0" class="pya-cap" data-e="" data-units="">Presentazione</h2>' in fuori
    assert "<h2>Fonti</h2>" in fuori                                        # le fonti non sono un capitolo
    assert fuori.count("<svg") == 1 and 'id="pya-map"' in fuori and "<script>" in fuori
    assert "pya-layout" in fuori and fuori.index("</style>") > fuori.index(".pya-map")
    assert re.search(r'"epochNames":\s*\{"epoch_1_1": "Età romana"', fuori)
    assert "tutto il sito" in fuori


def test_senza_disegni_l_html_resta_quello_della_libreria():
    html = "<html><head><style>b{}</style></head><body><h1>X</h1><h2>A</h2></body></html>"
    assert nm.inject_map(html, "", {}, [], {}, {}, lang="it") == html


def test_con_la_mappa_la_pagina_si_allarga():
    """Enzo, 13 ottobre 2026: «la pagina dell'HTML devi allargarla, così è
    una colonna stretta»: la libreria chiude il body a 42rem; con la mappa
    il body si allarga e il testo tiene una colonna leggibile."""
    html = ('<html><head><style>body { max-width: 42rem; }</style></head><body>'
            '<h1>X</h1><h2>A</h2><p><em class="em-mention">1.US1</em></p></body></html>')
    meta = {"u1": {"name": "1.US1", "number": "1", "epochs": ["e"]}}
    fuori = nm.inject_map(html, '<svg id="pya-svg"></svg>', {"all": [0, 0, 1, 1]},
                          [{"title": "A", "epoch": "e", "units": ["u1"]}], meta, {"e": "E"}, lang="it")
    assert re.search(r"body\s*\{[^}]*max-width:\s*min\(96vw,\s*1500px\)\s*!important", fuori)
    assert ".pya-text" in fuori and "max-width: 46rem" in fuori


def test_la_mappa_si_registra_nella_selezione_comune():
    assert "PYA_SEL.add(" in nm._JS
    assert "addEventListener('click'" not in nm._JS        # i clic li ascolta lo script comune
    vista = nm.map_view('<svg id="pya-svg"></svg>', {"all": [0, 0, 1, 1]},
                        {"u1": {"name": "1.US1", "epochs": []}}, {}, lang="en")
    assert vista.key == "map" and vista.label == "Map" and vista.panel.startswith('<svg id="pya-svg">')
    assert 'id="pya-reset" class="pya-reset"' in vista.panel and "var PYA = " in vista.script


def test_i_dati_della_mappa_non_portano_la_prima_epoca():
    """La prima epoca delle unità la usa lo script comune (PYA_SEL), non la mappa."""
    vista = nm.map_view('<svg id="pya-svg"></svg>', {"all": [0, 0, 1, 1]},
                        {"u1": {"name": "1.US1", "epochs": ["e1"]}}, {}, lang="it")
    assert "firstEpoch" not in vista.script and '"units": {"u1": "1.US1"}' in vista.script
