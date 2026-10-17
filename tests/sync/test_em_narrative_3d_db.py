"""L'HTML della narrativa con la scena 3D dei proxy (17 ottobre 2026): la
scena c'è quando il database ha i file dei proxy, e i nomi delle unità sono
link anche senza la mappa."""
from __future__ import annotations

import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
for _p in (str(_ROOT), str(_ROOT / "ext_libs")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from tests.utility.test_em_narrative_3d import _db, _file, _grafo  # noqa: E402


def test_l_html_della_narrativa_porta_la_scena_3d(tmp_path):
    from s3dgraphy.nodes.narrative_node import NarrativeNode
    from modules.s3dgraphy import em_narrative as en
    g = _grafo()
    n = NarrativeNode(node_id="narr", name="Tempio")
    n.add_chapter("Virtual Activity 1", canonical=True).add_prose("La fondazione [[u1]] e la [[u3]].")
    n.add_chapter("Fine", canonical=True).add_prose("Niente proxy per [[u2]].")
    g.add_node(n)
    glb = _file(tmp_path / "Tempio" / "EM" / "proxies", "SU002.glb", 64)
    conn = _db(tmp_path, [(1, "3d_model", "SU002", "glb", str(glb))])
    percorso = tmp_path / "n.html"
    en.export_file(g, n, "html", percorso, map_conn=conn, lang="it", media_base=("", ""))
    pagina = percorso.read_text(encoding="utf-8")
    assert 'id="pya-3d-data"' in pagina and pagina.count("var PYA_SEL = ") == 1
    assert '<a class="em-mention pya-u" href="#pya-map" data-u="u1" data-e="ep1">SU002</a>' in pagina
    assert re.search(r'<a class="em-mention pya-u"[^>]*data-u="u2"', pagina)      # senza proxy: è un'unità
    assert "pya-svg" not in pagina and '<nav class="pya-tabs">' not in pagina   # niente disegni, niente schede
    senza = tmp_path / "senza.html"
    en.export_file(g, n, "html", senza, lang="it")
    assert "pya-3d" not in senza.read_text(encoding="utf-8")                     # niente database, niente scena
