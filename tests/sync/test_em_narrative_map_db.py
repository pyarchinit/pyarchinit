"""La mappa della narrativa sul database di prova (QGIS fuori schermo): i
disegni delle unità dalle viste US/USM, l'HTML esportato con la mappa e
i link, e la scheda che passa la connessione all'export."""
from __future__ import annotations

import os
import re
import shutil
import sqlite3
import sys
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("qgis.core")
from qgis.core import QgsApplication  # noqa: E402

_ROOT = Path(__file__).resolve().parents[2]
for _p in (_ROOT, _ROOT / "ext_libs"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
pytest.importorskip("s3dgraphy")
from modules.s3dgraphy import em_narrative as en  # noqa: E402
from modules.s3dgraphy import em_narrative_map as nm  # noqa: E402


@pytest.fixture(scope="module")
def qgs():
    app = QgsApplication.instance()
    if app is None:
        QgsApplication.setPrefixPath(
            os.environ.get("QGIS_PREFIX_PATH", "/Applications/QGIS.app/Contents/MacOS"), True)
        app = QgsApplication([], False)
        app.initQgis()
    return app


@pytest.fixture
def db(tmp_path):
    dest = tmp_path / "prova.sqlite"
    shutil.copy(_ROOT / "resources" / "dbfiles" / "pyarchinit_db.sqlite", dest)
    sito, area, us = sqlite3.connect(str(dest)).execute(
        "select scavo_s, area_s, us_s from pyarchinit_us_view where the_geom is not null "
        "group by 1, 2, 3 order by count(*) desc limit 1").fetchone()
    return "sqlite:///%s" % dest, str(sito), str(area), str(us)


def _grafo(sito, area, us):
    from s3dgraphy.graph import Graph
    from s3dgraphy.nodes.epoch_node import EpochNode
    from s3dgraphy.nodes.stratigraphic_node import StratigraphicUnit
    g = Graph(graph_id=sito)
    g.add_node(EpochNode("epoch_1_1", "Prima epoca", -100, 300))
    for uid, numero in (("u5", us), ("u9", "9999")):          # la 9999 non è disegnata
        n = StratigraphicUnit(uid, "%s.US%s" % (area, numero))
        n.data = {"sito": sito, "area": area, "us": numero}
        g.add_node(n)
        g.add_edge(uid + "_fe", uid, "epoch_1_1", "has_first_epoch")
    return g


def test_i_disegni_delle_unita_vengono_dalle_viste(qgs, db):
    conn, sito, area, us = db
    meta = nm.units_meta(_grafo(sito, area, us))
    disegni = nm.drawings_from_db(conn, sito, meta, "it")
    assert disegni and {d.unit_id for d in disegni} == {"u5"}
    assert sum(1 for d in disegni if d.label is not None) == 1          # un'etichetta per unità
    assert all(len(d.rings[0]) >= 3 for d in disegni)
    svg, boxes = nm.svg_map(disegni, meta)
    assert svg.count('data-u="u5"') == len(disegni) + 1 and "epoch_1_1" in boxes and "all" in boxes


def test_l_html_esportato_porta_la_mappa_e_i_link(qgs, db, tmp_path):
    conn, sito, area, us = db
    g = _grafo(sito, area, us)
    n = en.scaffold(g, "it")
    en.generate_chapter(g, n, n.chapter_by_anchor("epoch_1_1"),
                        chat=lambda m: "Sotto [[u5]] c'è [[u9]].", model="m")
    percorso = tmp_path / "narrativa.html"
    en.export_file(g, n, "html", percorso, map_conn=conn, lang="it")
    html = percorso.read_text(encoding="utf-8")
    assert '<svg id="pya-svg"' in html and 'data-u="u5"' in html
    assert re.search(r'<a class="em-mention pya-u" href="#pya-map" data-u="u5" data-e="epoch_1_1">', html)
    assert re.search(r'<h2 id="pya-cap-\d+" class="pya-cap" data-e="epoch_1_1"', html)
    assert "tutto il sito" in html and "<script>" in html
    en.export_file(g, n, "html", tmp_path / "senza.html")                # senza connessione: come prima
    assert "pya-svg" not in (tmp_path / "senza.html").read_text(encoding="utf-8")


def test_la_scheda_passa_la_connessione_all_export():
    sorgente = (_ROOT / "modules" / "s3dgraphy" / "em_narrative_tab.py").read_text(encoding="utf-8")
    assert re.search(r"en\.export_file\(g, narrativa, fmt, destinazione,\s*figures=figure,\s*map_conn=stato\.conn", sorgente)
