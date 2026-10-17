"""L'HTML della narrativa come lo vuole chi lo legge (Enzo, 17 ottobre 2026:
«nella narrativa andrebbe messo anche un indice»).

TempluMare porta 13 capitoli in due parti («Rilievo e analisi — …»,
«Ricostruzione — …») e dentro la prosa i sottotitoli in Markdown
(«### Past researches»), che la libreria lasciava come testo. Qui: i
sottotitoli diventano titoli, e in testa alla pagina c'è l'indice, con i
capitoli raggruppati per parte e i sottotitoli sotto il loro capitolo.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
for p in (str(_ROOT / "ext_libs"), str(_ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

from modules.s3dgraphy import em_narrative as en  # noqa: E402
from modules.s3dgraphy import em_narrative_html as nh  # noqa: E402


def _grafo():
    from s3dgraphy.graph import Graph
    from s3dgraphy.nodes.narrative_node import NarrativeNode
    from s3dgraphy.nodes.stratigraphic_node import StratigraphicUnit
    g = Graph(graph_id="Temple")
    g.name = "Temple"
    u = StratigraphicUnit("u1", "SU001")
    u.data = {"us": "1"}
    g.add_node(u)
    n = NarrativeNode(node_id="narr", name="Il Grande Tempio", lang="en")
    intro = n.add_chapter("Rilievo e analisi — Introduction", canonical=True)
    intro.add_prose("The Great Temple is known as *Malacbel*.\n\n### Past researches\n\n"
                    "The first excavations.\n\n### Current researches\n\nNew surveys.")
    n.add_chapter("Rilievo e analisi — 4D survey", canonical=True).add_prose("Survey of [[u1]].")
    n.add_chapter("Ricostruzione — Virtual Activity 1", canonical=True).add_prose("Foundations.")
    n.add_chapter("Conclusioni", canonical=True).add_prose("The end.")
    g.add_node(n)
    return g, n


def _html(tmp_path, **kw):
    g, n = _grafo()
    percorso = tmp_path / "n.html"
    en.export_file(g, n, "html", percorso, **kw)
    return percorso.read_text(encoding="utf-8")


def _indice(pagina):
    m = re.search(r'<nav class="pya-indice"[^>]*>(.*?)</nav>', pagina, re.S)
    assert m, "manca l'indice"
    return m.group(1)


def test_i_sottotitoli_markdown_diventano_titoli(tmp_path):
    pagina = _html(tmp_path)
    assert "### " not in pagina
    assert re.search(r'<h3 id="pya-sez-0-0">Past researches</h3>', pagina)
    assert re.search(r'<h3 id="pya-sez-0-1">Current researches</h3>', pagina)
    assert "<em>Malacbel</em>" in pagina                     # il corsivo lo fa già la libreria


def test_l_indice_porta_a_ogni_capitolo_e_sottotitolo(tmp_path):
    pagina = _html(tmp_path)
    indice = _indice(pagina)
    for k in range(4):
        assert 'href="#pya-cap-%d"' % k in indice
        assert re.search(r'<h2 id="pya-cap-%d"' % k, pagina)
    assert 'href="#pya-sez-0-0"' in indice and 'href="#pya-sez-0-1"' in indice
    # l'indice sta in testa: prima del primo capitolo
    assert pagina.index('class="pya-indice"') < pagina.index('id="pya-cap-0"')


def _lista_della_parte(indice, parte):
    """L'<ol> della parte, con le liste annidate dentro (bilanciato)."""
    inizio = indice.index('<span class="pya-parte">%s</span><ol>' % parte)
    i = indice.index("<ol>", inizio)
    profondita = 0
    for m in re.finditer(r"</?ol>", indice[i:]):
        profondita += 1 if m.group(0) == "<ol>" else -1
        if profondita == 0:
            return indice[i:i + m.end()]
    raise AssertionError("lista non chiusa")


def test_i_capitoli_di_una_stessa_parte_stanno_insieme(tmp_path):
    indice = _indice(_html(tmp_path))
    rilievo = _lista_della_parte(indice, "Rilievo e analisi")
    assert ">Introduction<" in rilievo and ">4D survey<" in rilievo
    assert "Virtual Activity 1" not in rilievo
    assert ">Conclusioni<" in indice                          # senza parte: da solo
    assert ">Ricostruzione — Virtual Activity 1<" in indice   # parte con un capitolo solo: titolo intero


def test_le_fonti_sono_l_ultima_voce(tmp_path):
    g, n = _grafo()
    from s3dgraphy.nodes.document_node import DocumentNode
    g.add_node(DocumentNode("d1", "D.05"))
    n.chapters[1].add_embed("d1", "source")
    percorso = tmp_path / "n.html"
    en.export_file(g, n, "html", percorso)
    pagina = percorso.read_text(encoding="utf-8")
    indice = _indice(pagina)
    assert 'href="#pya-fonti"' in indice and '<h2 id="pya-fonti">' in pagina
    assert indice.rindex("pya-fonti") > indice.rindex("pya-cap-3")


def test_la_parola_indice_nella_lingua_dell_esportazione(tmp_path):
    assert ">Indice<" in _indice(_html(tmp_path, lang="it"))
    assert ">Contents<" in _indice(_html(tmp_path, lang="en"))
    assert ">Inhalt<" in _indice(_html(tmp_path, lang="de"))


def test_con_la_mappa_l_indice_usa_gli_id_dei_capitoli_della_mappa():
    pagina = ("<html><head><style></style></head><body><h1>T</h1><p class=\"em-byline\">x</p>"
              '<h2 id="pya-cap-0" class="pya-cap" data-e="e1" data-units="u1">A</h2><p>a</p>'
              '<h2 id="pya-cap-1" class="pya-cap" data-e="" data-units="">B</h2><p>b</p>'
              "</body></html>")
    fuori = nh.add_index(pagina, "it")
    assert fuori.count('id="pya-cap-0"') == 1 and fuori.count('id="pya-cap-1"') == 1
    assert 'href="#pya-cap-1"' in _indice(fuori)
    assert 'data-units="u1"' in fuori                         # gli attributi della mappa restano


def test_l_indice_si_mette_una_volta_sola():
    pagina = "<html><head><style></style></head><body><h1>T</h1><h2>A</h2><p>a</p></body></html>"
    due = nh.add_index(nh.add_index(pagina, "it"), "it")
    assert due.count('class="pya-indice"') == 1


# ------------------------------------------------ le fonti di ogni capitolo

def _grafo_fonti():
    """Due unità con le loro catene: u1 → altezza → estrattore → D.05;
    u2 → materiale → combinatore → due estrattori → D.07 e D.05; u3 senza."""
    from s3dgraphy.graph import Graph
    from s3dgraphy.nodes.combiner_node import CombinerNode
    from s3dgraphy.nodes.document_node import DocumentNode
    from s3dgraphy.nodes.extractor_node import ExtractorNode
    from s3dgraphy.nodes.group_node import ActivityNodeGroup
    from s3dgraphy.nodes.property_node import PropertyNode
    from s3dgraphy.nodes.stratigraphic_node import StratigraphicUnit
    g = Graph(graph_id="Temple")
    for uid, nome in (("u1", "SU001"), ("u2", "USV101"), ("u3", "SU003")):
        g.add_node(StratigraphicUnit(uid, nome))
    g.add_node(PropertyNode("p1", "height"))
    g.add_node(PropertyNode("p2", "material"))
    g.add_node(ExtractorNode("x1", "D.05.01"))
    g.add_node(ExtractorNode("x2", "D.07.01"))
    g.add_node(ExtractorNode("x3", "D.05.02"))
    g.add_node(CombinerNode("c1", "C.01"))
    g.add_node(DocumentNode("d5", "D.05", description="Diaconescu 2013"))
    g.add_node(DocumentNode("d7", "D.07", description="Maison Carrée"))
    g.add_node(ActivityNodeGroup("a1", "VAct.01"))
    for i, (s, t, tipo) in enumerate((
            ("u1", "p1", "has_property"), ("p1", "x1", "has_data_provenance"),
            ("x1", "d5", "extracted_from"),
            ("u2", "p2", "has_property"), ("p2", "c1", "has_data_provenance"),
            ("c1", "x2", "combines"), ("c1", "x3", "combines"),
            ("x2", "d7", "extracted_from"), ("x3", "d5", "extracted_from"),
            ("u2", "a1", "is_in_activity"), ("u3", "a1", "is_in_activity"))):
        g.add_edge("e%d" % i, s, t, tipo)
    return g


def test_le_fonti_di_un_unita_seguono_proprieta_estrattori_e_combinatori():
    g = _grafo_fonti()
    fonti = nh.unit_sources(g, ["u1", "u2", "u3"])
    assert [f.doc_id for f in fonti] == ["d5", "d7"]              # in ordine di prima apparizione
    d5 = fonti[0]
    assert d5.name == "D.05" and d5.description == "Diaconescu 2013"
    assert ("SU001", "height", "D.05.01") in d5.uses and ("USV101", "material", "D.05.02") in d5.uses
    assert fonti[1].uses == [("USV101", "material", "D.07.01")]


def test_le_unita_del_capitolo_le_menzioni_poi_gli_embed_poi_l_ancora():
    from s3dgraphy.nodes.narrative_node import NarrativeNode
    g = _grafo_fonti()
    n = NarrativeNode(node_id="narr", name="T")
    citato = n.add_chapter("Uno", canonical=True)
    citato.add_prose("Si vede [[u1]].")
    ancorato = n.add_chapter("VAct.01", anchor="a1", canonical=True)
    ancorato.add_prose("Nessuna menzione.")
    vuoto = n.add_chapter("Introduzione", canonical=True)
    vuoto.add_prose("Niente.")
    assert nh.chapter_units(g, citato) == ["u1"]
    assert nh.chapter_units(g, ancorato) == ["u2", "u3"]
    assert nh.chapter_units(g, vuoto) == []


# ------------------------------------------------ le fonti come hotspot

_REGISTRO = {
    "d5": {"title": "D.05", "description": "Diaconescu 2013", "kind": "PDF",
           "uses": [["SU001", "height", "D.05.01"]], "preview": "data:image/png;base64,AAA",
           "file": "JVBERi0=", "mime": "application/pdf", "link": "file:///tmp/D.05.pdf",
           "path": "/tmp/D.05.pdf"},
    "d7": {"title": "D.07", "description": "Maison Carrée", "kind": "PNG", "uses": [],
           "preview": "", "file": "", "mime": "image/png", "link": "", "path": ""},
}

_PAGINA = ("<!doctype html><html><head><style>body{}</style></head><body>\n"
           "<h1>T</h1>\n<p class=\"em-byline\">x</p>\n"
           "<h2>Uno</h2>\n<p>Testo <em class=\"em-mention\">D.07</em>.</p>\n"
           "<div class=\"em-embed\"><div class=\"em-kind\">fonte</div><div class=\"em-title\">D.05</div></div>\n"
           "<h2>Due</h2>\n<p>Altro.</p>\n"
           "<section class=\"em-sources\"><h2>Fonti</h2><ul><li>Prompt</li><li>D.05</li></ul></section>"
           "<footer class=\"em-footer\">snapshot</footer>\n</body></html>\n")


def test_ogni_capitolo_chiude_con_le_sue_fonti():
    fuori = nh.add_sources(_PAGINA, [["d5", "d7"], []], _REGISTRO, "it")
    uno = fuori[fuori.index("<h2>Uno</h2>"):fuori.index("<h2>Due</h2>")]
    assert 'class="pya-fonti-cap"' in uno and "Fonti del capitolo" in uno
    riga = uno[uno.index('class="pya-fonti-cap"'):]
    assert riga.index('data-src="d5"') < riga.index('data-src="d7"')
    due = fuori[fuori.index("<h2>Due</h2>"):fuori.index('<section class="em-sources">')]
    assert "pya-fonti-cap" not in due                         # senza fonti, niente riga


def test_le_fonti_in_fondo_sono_hotspot_e_ci_sono_tutte():
    fuori = nh.add_sources(_PAGINA, [["d5", "d7"], []], _REGISTRO, "it")
    sezione = fuori[fuori.index('<section class="em-sources">'):fuori.index("</section>")]
    assert "<li>Prompt</li>" in sezione                       # quello che non è un documento resta
    assert 'data-src="d5"' in sezione and "Diaconescu 2013" in sezione
    assert 'data-src="d7"' in sezione                         # aggiunta: era solo nel capitolo


def test_le_schede_fonte_e_le_menzioni_dei_documenti_diventano_hotspot():
    fuori = nh.add_sources(_PAGINA, [["d5", "d7"], []], _REGISTRO, "it")
    assert re.search(r'<div class="em-title"><a class="pya-fonte" href="#pya-f-d5"[^>]*data-src="d5"', fuori)
    assert re.search(r'<a class="pya-fonte em-mention" href="#pya-f-d7"[^>]*data-src="d7"[^>]*>D\.07</a>', fuori)


def test_tooltip_pannello_e_registro_una_volta_sola():
    import json
    fuori = nh.add_sources(nh.add_sources(_PAGINA, [["d5"], []], _REGISTRO, "it"),
                           [["d5"], []], _REGISTRO, "it")
    assert fuori.count('id="pya-tip"') == 1 and fuori.count('id="pya-pannello"') == 1
    assert fuori.count("var PYA_FONTI") == 1
    dati = json.loads(re.search(r"var PYA_FONTI = (\{.*?\});\n", fuori, re.S).group(1))
    assert dati["d5"]["title"] == "D.05" and dati["d5"]["mime"] == "application/pdf"
    assert fuori.count('class="pya-fonti-cap"') == 1


def test_senza_sezione_delle_fonti_la_si_crea_prima_del_piede():
    pagina = _PAGINA.replace('<section class="em-sources"><h2>Fonti</h2><ul><li>Prompt</li><li>D.05</li></ul></section>', "")
    fuori = nh.add_sources(pagina, [["d5"], []], _REGISTRO, "it")
    assert fuori.index('<section class="em-sources">') < fuori.index('<footer class="em-footer">')
    assert '<h2>Fonti</h2>' in fuori


def test_con_la_mappa_le_fonti_stanno_dentro_la_colonna_del_testo():
    pagina = (_PAGINA.replace("<body>", '<body>\n<div class="pya-layout"><div class="pya-text">')
              .replace("</body>", '</div><aside class="pya-map" id="pya-map">mappa</aside></div><script>var PYA = {};</script></body>'))
    fuori = nh.add_sources(pagina, [["d5"], ["d7"]], _REGISTRO, "it")
    due = fuori[fuori.index("<h2>Due</h2>"):]
    assert due.index('class="pya-fonti-cap"') < due.index('<section class="em-sources">')
    assert fuori.index('id="pya-pannello"') > fuori.index('<aside class="pya-map"')


def test_l_esportazione_html_porta_le_fonti_e_l_indice(tmp_path):
    from s3dgraphy.nodes.narrative_node import NarrativeNode
    g = _grafo_fonti()
    n = NarrativeNode(node_id="narr", name="T")
    n.add_chapter("Uno", canonical=True).add_prose("Si vede [[u1]].")
    n.add_chapter("VAct.01", anchor="a1", canonical=True).add_prose("Lavori.")
    g.add_node(n)
    percorso = tmp_path / "n.html"
    en.export_file(g, n, "html", percorso, lang="it")
    pagina = percorso.read_text(encoding="utf-8")
    assert pagina.count('class="pya-fonti-cap"') == 2
    uno = pagina[pagina.index(">Uno</h2>"):pagina.index(">VAct.01</h2>")]
    assert 'data-src="d5"' in uno and 'data-src="d7"' not in uno
    assert "var PYA_FONTI" in pagina and 'class="pya-indice"' in pagina
    assert 'href="#pya-fonti"' in _indice(pagina)


def test_la_scheda_passa_le_cartelle_dei_media_all_esportazione():
    src = (_ROOT / "modules" / "s3dgraphy" / "em_narrative_tab.py").read_text(encoding="utf-8")
    assert "media_base=(thumb, resize)" in src


# ------------------------------------------------ le unità raggruppate (Enzo, 17-10-2026)

def test_le_schede_delle_unita_e_dei_paradati_si_raggruppano_per_unita(tmp_path):
    """«i paradati sembrano note tutte in fila una sotto l'altra»: nel capitolo
    di un'epoca la libreria metteva 367 schede in fila — i paradati senza
    dire di quale unità. Ora una riga per unità, e dentro i suoi paradati."""
    from s3dgraphy.nodes.narrative_node import NarrativeNode
    g = _grafo_fonti()
    n = NarrativeNode(node_id="narr", name="T")
    cap = n.add_chapter("II A.D.", anchor="a1")
    cap.add_prose("Il capitolo.")
    for ref, vista in (("u1", "us"), ("p1", "paradata"), ("u2", "us"), ("p2", "paradata"), ("d5", "source")):
        cap.add_embed(ref, vista)
    g.add_node(n)
    percorso = tmp_path / "n.html"
    en.export_file(g, n, "html", percorso, lang="it")
    pagina = percorso.read_text(encoding="utf-8")
    capitolo = pagina[pagina.index(">II A.D.</h2>"):]
    assert '<div class="em-kind">paradata</div>' not in capitolo
    assert '<div class="em-kind">us</div>' not in capitolo
    assert '<div class="em-kind">fonte</div>' not in capitolo       # è nella riga delle fonti
    blocco = capitolo[capitolo.index('class="pya-unita"'):]
    assert "2 unità" in blocco and "2 paradati" in blocco
    u1 = blocco[blocco.index(">SU001<"):blocco.index(">USV101<")]
    assert "height" in u1 and 'data-src="d5"' in u1 and "D.05.01" in u1
    assert capitolo.index("Il capitolo.") < capitolo.index('class="pya-unita"')


def test_un_capitolo_senza_schede_non_ha_il_blocco_delle_unita(tmp_path):
    g, n = _grafo()
    percorso = tmp_path / "n.html"
    en.export_file(g, n, "html", percorso, lang="it")
    assert 'class="pya-unita"' not in percorso.read_text(encoding="utf-8")


def test_i_paradati_di_un_unita_si_leggono_per_documento():
    """Nel TempluMare vero «Proxy Geometry» viene da un combinatore con otto
    estrattori dello stesso documento: un documento per riga, con i suoi
    estrattori, non otto volte «← D.01»; e un valore che è l'id di un nodo
    si legge col nome del nodo, non con l'uuid."""
    from s3dgraphy.graph import Graph
    from s3dgraphy.nodes.combiner_node import CombinerNode
    from s3dgraphy.nodes.document_node import DocumentNode
    from s3dgraphy.nodes.extractor_node import ExtractorNode
    from s3dgraphy.nodes.property_node import PropertyNode
    from s3dgraphy.nodes.semantic_shape_node import SemanticShapeNode
    from s3dgraphy.nodes.stratigraphic_node import StratigraphicUnit
    g = Graph(graph_id="T")
    g.add_node(StratigraphicUnit("u", "SU002"))
    g.add_node(PropertyNode("p", "Proxy Geometry"))
    forma = "20b29157-83b4-5c34-a474-6c824cf7d20b"
    g.add_node(PropertyNode("q", "geometry", value=forma))
    g.add_node(SemanticShapeNode(forma, "Shape for SU002"))
    g.add_node(CombinerNode("c", "C.1101"))
    g.add_node(DocumentNode("d", "D.01"))
    archi = [("u", "p", "has_property"), ("u", "q", "has_property"), ("p", "c", "has_data_provenance")]
    for k in ("41", "53", "54"):
        g.add_node(ExtractorNode("x" + k, "D.01." + k))
        archi += [("c", "x" + k, "combines"), ("x" + k, "d", "extracted_from")]
    for i, (s, t, tipo) in enumerate(archi):
        g.add_edge("e%d" % i, s, t, tipo)
    righe = "".join(nh._righe_paradati("u", {n.node_id: n for n in g.nodes}, nh._uscite(g), {"d": {}}))
    assert righe.count('data-src="d"') == 1
    assert "D.01.41, D.01.53, D.01.54" in righe and "C.1101" in righe
    assert "Shape for SU002" in righe and forma not in righe
