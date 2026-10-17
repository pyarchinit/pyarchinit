"""Il DOCX della narrativa con l'indice, i sottotitoli, il corsivo e le
fonti di ogni capitolo (17 ottobre 2026): la libreria lasciava «### Past
researches» e «*Malacbel*» come testo, e non c'era un indice."""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
for p in (str(_ROOT / "ext_libs"), str(_ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

docx = pytest.importorskip("docx")

from modules.s3dgraphy import em_narrative as en  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_em_narrative_html import _grafo, _grafo_fonti  # noqa: E402


def _docx(tmp_path, g, n):
    percorso = tmp_path / "n.docx"
    en.export_file(g, n, "docx", percorso, lang="it")
    return percorso


def test_i_sottotitoli_diventano_titoli_di_secondo_livello(tmp_path):
    g, n = _grafo()
    d = docx.Document(str(_docx(tmp_path, g, n)))
    secondi = [p.text for p in d.paragraphs if p.style.name == "Heading 2"]
    assert secondi == ["Past researches", "Current researches"]
    assert not any(p.text.startswith("#") for p in d.paragraphs)


def test_il_corsivo_del_markdown_e_corsivo(tmp_path):
    g, n = _grafo()
    d = docx.Document(str(_docx(tmp_path, g, n)))
    assert not any("*" in p.text for p in d.paragraphs)
    corsivi = [r for p in d.paragraphs for r in p.runs if r.text == "Malacbel"]
    assert corsivi and all(r.italic for r in corsivi)


def test_c_e_l_indice_di_word_con_i_titoli_gia_scritti(tmp_path):
    g, n = _grafo()
    percorso = _docx(tmp_path, g, n)
    with zipfile.ZipFile(str(percorso)) as z:
        corpo = z.read("word/document.xml").decode("utf-8")
        impostazioni = z.read("word/settings.xml").decode("utf-8")
    assert 'TOC \\o "1-2" \\h \\z \\u' in corpo
    assert "w:updateFields" in impostazioni
    d = docx.Document(str(percorso))
    testi = [p.text for p in d.paragraphs]
    i = testi.index("Indice")
    assert "Rilievo e analisi — Introduction" in testi[i + 1:i + 8]
    primo_capitolo = next(k for k, p in enumerate(d.paragraphs) if p.style.name == "Heading 1")
    assert i < primo_capitolo                                 # l'indice sta prima dei capitoli


def test_ogni_capitolo_chiude_con_le_sue_fonti(tmp_path):
    from s3dgraphy.nodes.narrative_node import NarrativeNode
    g = _grafo_fonti()
    n = NarrativeNode(node_id="narr", name="T")
    n.add_chapter("Uno", canonical=True).add_prose("Si vede [[u1]].")
    n.add_chapter("VAct.01", anchor="a1", canonical=True).add_prose("Lavori.")
    g.add_node(n)
    d = docx.Document(str(_docx(tmp_path, g, n)))
    testi = [p.text for p in d.paragraphs]
    titoli = {p.text: k for k, p in enumerate(d.paragraphs) if p.style.name == "Heading 1"}
    uno = testi[titoli["Uno"]:titoli["VAct.01"]]                  # il capitolo, non la voce dell'indice
    riga = [t for t in uno if t.startswith("Fonti del capitolo")]
    assert riga and "D.05" in riga[0] and "D.07" not in riga[0]
    dopo = " ".join(testi[titoli["VAct.01"]:])
    assert "D.07" in dopo and "Maison Carrée" in dopo
