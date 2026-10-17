"""Il PDF della narrativa con l'indice, i sottotitoli e le fonti di ogni
capitolo (Enzo, 17 ottobre 2026: «nella narrativa andrebbe messo anche un
indice»; TempluMare porta nella prosa «### Past researches» e «*Malacbel*»,
che il PDF stampava così com'erano)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
for p in (str(_ROOT / "ext_libs"), str(_ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

fitz = pytest.importorskip("fitz")
pytest.importorskip("reportlab")

from modules.s3dgraphy import em_narrative as en  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_em_narrative_html import _grafo, _grafo_fonti  # noqa: E402


def _pdf(tmp_path, g, n):
    percorso = tmp_path / "n.pdf"
    en.export_pdf(g, n, percorso, lang="it")
    return fitz.open(str(percorso))


def _testo(doc):
    return "\n".join(pagina.get_text() for pagina in doc)


def test_il_pdf_ha_l_indice_con_capitoli_e_sottotitoli(tmp_path):
    g, n = _grafo()
    doc = _pdf(tmp_path, g, n)
    indice = doc.get_toc()                                   # i segnalibri del PDF
    titoli = [(livello, titolo) for livello, titolo, _pagina in indice]
    assert (1, "Rilievo e analisi — Introduction") in titoli
    assert (2, "Past researches") in titoli and (2, "Current researches") in titoli
    assert (1, "Conclusioni") in titoli
    assert all(pagina >= 1 for _l, _t, pagina in indice)
    prima = doc[0].get_text() + (doc[1].get_text() if len(doc) > 1 else "")
    assert "Indice" in prima and "Rilievo e analisi — Introduction" in prima


def test_nel_pdf_i_sottotitoli_sono_titoli_e_il_corsivo_e_corsivo(tmp_path):
    g, n = _grafo()
    doc = _pdf(tmp_path, g, n)
    testo = _testo(doc)
    assert "###" not in testo and "*Malacbel*" not in testo
    assert "Past researches" in testo and "Malacbel" in testo
    corsivi = [s for pagina in doc for b in pagina.get_text("dict")["blocks"]
               for riga in b.get("lines", []) for s in riga["spans"] if "Malacbel" in s["text"]]
    assert corsivi and all((s["flags"] & 2) or "Oblique" in s["font"] or "I" in s["font"][-2:]
                           for s in corsivi)


def test_nel_pdf_ogni_capitolo_ha_le_sue_fonti(tmp_path):
    from s3dgraphy.nodes.narrative_node import NarrativeNode
    g = _grafo_fonti()
    n = NarrativeNode(node_id="narr", name="T")
    n.add_chapter("Uno", canonical=True).add_prose("Si vede [[u1]].")
    n.add_chapter("VAct.01", anchor="a1", canonical=True).add_prose("Lavori.")
    g.add_node(n)
    testo = _testo(_pdf(tmp_path, g, n)).replace("\n", " ")
    uno = testo[testo.index("Si vede"):testo.index("Lavori")]
    assert "Fonti del capitolo" in uno and "D.05" in uno and "D.07" not in uno
    dopo = testo[testo.index("Lavori"):]
    assert "D.07" in dopo and "Maison Carrée" in dopo
