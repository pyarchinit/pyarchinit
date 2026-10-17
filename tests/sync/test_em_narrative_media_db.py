"""I media candidati di un capitolo vengono dal database, come la scheda li
mostra: qui il proxy 3D dell'unità citata, importato dall'em.json con la
sua vista (17 ottobre 2026)."""
from __future__ import annotations

import os

from tests.sync.test_em_media_import import SITO, _importa, progetto  # noqa: F401


def test_i_candidati_del_capitolo_sono_i_media_dell_unita_citata(progetto):  # noqa: F811
    from s3dgraphy.nodes.narrative_node import NarrativeNode
    from modules.s3dgraphy import em_export
    from modules.s3dgraphy import em_narrative as en
    from modules.s3dgraphy import em_narrative_media as nm
    _importa(progetto)
    conn = "sqlite:///" + str(progetto["db"])
    percorso, *_ = em_export.export_site(conn, SITO, str(progetto["tmp"] / "out"), per_saggio=False)
    grafo = en.load_project(percorso)[0].active()
    unita = grafo.find_node_by_id("u1")                     # SU002, col suo proxy glb
    n = NarrativeNode(node_id="narr", name="T")
    cap = n.add_chapter("Uno")
    cap.add_prose("Si vede [[u1]].")
    candidati = nm.chapter_media_candidates(grafo, cap, conn, progetto["thumb"], progetto["resize"])
    tre_d = [c for c in candidati if c.kind == "3d"]
    assert tre_d and tre_d[0].unit_id == "u1" and tre_d[0].filename == "SU002.glb"
    assert tre_d[0].unit_name == unita.name
    assert os.path.isfile(tre_d[0].thumb_path)              # la vista del modello
    assert not any(c.filename.endswith(".pdf") for c in candidati)   # i documenti sono fonti


def test_l_html_porta_il_modello_scelto_dopo_il_suo_paragrafo(progetto, tmp_path):  # noqa: F811
    import json
    import re
    from s3dgraphy.nodes.narrative_node import NarrativeNode
    from modules.s3dgraphy import em_export
    from modules.s3dgraphy import em_narrative as en
    from modules.s3dgraphy import em_narrative_media as nm
    _importa(progetto)
    conn = "sqlite:///" + str(progetto["db"])
    percorso, *_ = em_export.export_site(conn, SITO, str(progetto["tmp"] / "out"), per_saggio=False)
    grafo = en.load_project(percorso)[0].active()
    n = NarrativeNode(node_id="narr_media", name="T")
    cap = n.add_chapter("Uno")
    cap.add_prose("Si vede [[u1]].\n\nAltro paragrafo.")
    grafo.add_node(n)
    basi = (progetto["thumb"], progetto["resize"])
    modello = [c for c in nm.chapter_media_candidates(grafo, cap, conn, *basi) if c.kind == "3d"][0]
    nm.store_choices(n, cap, [{"key": modello.key, "after": 1, "caption": "Il proxy.", "by": "ai"}])
    uscita = tmp_path / "n.html"
    en.export_file(grafo, n, "html", uscita, map_conn=conn, lang="it", media_base=basi)
    pagina = uscita.read_text(encoding="utf-8")
    assert pagina.index("Si vede") < pagina.index('class="pya-media"') < pagina.index("Altro paragrafo")
    dati = json.loads(re.search(r"var PYA_FONTI = (\{.*?\});\n", pagina, re.S).group(1))
    voce = dati["m::" + modello.key]
    assert voce["model"] and voce["mime"] == "model/gltf-binary" and voce["file"]
    assert voce["preview"].startswith("data:image/png")
    assert 'class="pya-indice"' in pagina
