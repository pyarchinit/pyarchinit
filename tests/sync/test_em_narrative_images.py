"""Le immagini delle unità nella narrativa (2026-10-12, «inserire le immagini
delle US associate quando parlo di quella US»): nel testo della scheda, nelle
figure di HTML e DOCX, e nel PDF stampabile."""
from __future__ import annotations

import io
import shutil
import sqlite3
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
for p in (str(_ROOT / "ext_libs"), str(_ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

from modules.s3dgraphy import em_export  # noqa: E402
from modules.s3dgraphy import em_narrative as en  # noqa: E402

SITO = "Scavo archeologico"


def _png(path, w=60, h=40, colore=(200, 30, 30)):
    from PIL import Image
    Image.new("RGB", (w, h), colore).save(path)
    return str(path)


@pytest.fixture()
def scavo(tmp_path, monkeypatch):
    """Il DB di prova, con le cartelle delle anteprime e delle immagini
    ridotte riempite per le unità 1 e 2 dell'area 1 (tre media a testa nel
    DB: file solo per i primi due della US 1, uno per la US 2)."""
    folder = tmp_path / "pyarchinit_DB_folder"
    folder.mkdir()
    resources = _ROOT / "resources" / "dbfiles"
    shutil.copy(resources / "config.cfg", folder / "config.cfg")
    shutil.copy(resources / "pyarchinit_db.sqlite", folder / "db.sqlite")
    monkeypatch.setenv("PYARCHINIT_HOME", str(tmp_path))
    conn = "sqlite:///%s" % (folder / "db.sqlite")
    thumb, resize = tmp_path / "thumb", tmp_path / "resize"
    thumb.mkdir(), resize.mkdir()
    db = sqlite3.connect(folder / "db.sqlite")
    righe = db.execute(
        "SELECT u.us, m.id_media, m.media_name, t.filepath FROM media_to_entity_table m "
        "JOIN us_table u ON u.id_us = m.id_entity LEFT JOIN media_thumb_table t "
        "ON t.id_media = m.id_media WHERE m.entity_type = 'US' AND u.sito = ? "
        "AND u.area = '1' AND u.us IN ('1', '2') ORDER BY u.us, m.media_name", (SITO,)).fetchall()
    db.close()
    per_us = {}
    for us, id_media, nome, anteprima in righe:
        per_us.setdefault(us, []).append((id_media, nome, anteprima))
    for id_media, nome, anteprima in per_us["1"][:2]:
        _png(resize / ("%s_%s.png" % (id_media, nome)), 120, 80)
        if anteprima:
            _png(thumb / anteprima, 30, 20)
    id_media, nome, anteprima = per_us["2"][0]
    _png(thumb / anteprima, 30, 20, (30, 200, 30))              # solo l'anteprima, niente ridotta
    out = tmp_path / "em"
    path, *_ = em_export.export_site(conn, SITO, str(out), per_saggio=False)
    cont, _ = en.load_project(path)
    return {"conn": conn, "thumb": str(thumb), "resize": str(resize), "path": path,
            "cont": cont, "graph": cont.active(), "per_us": per_us}


def _nodo_us(graph, us):
    return next(n for n in graph.nodes if (getattr(n, "data", None) or {}).get("us") == us
                and (n.data or {}).get("area") == "1")


def test_i_file_delle_immagini_di_una_unita_preferiscono_la_ridotta_poi_l_anteprima(scavo):
    g = scavo["graph"]
    file1 = en.unit_media_files(scavo["conn"], _nodo_us(g, "1"), scavo["thumb"], scavo["resize"])
    assert len(file1) == 2 and all(f.startswith(scavo["resize"]) for f in file1)
    file2 = en.unit_media_files(scavo["conn"], _nodo_us(g, "2"), scavo["thumb"], scavo["resize"])
    assert len(file2) == 1 and file2[0].startswith(scavo["thumb"])
    assert en.unit_media_files(scavo["conn"], _nodo_us(g, "3"), scavo["thumb"], scavo["resize"]) == []
    solo_anteprime = en.unit_media_files(scavo["conn"], _nodo_us(g, "1"), scavo["thumb"], scavo["resize"],
                                         prefer="thumb")
    assert len(solo_anteprime) == 2 and all(f.startswith(scavo["thumb"]) for f in solo_anteprime)
    assert len(en.unit_media_files(scavo["conn"], _nodo_us(g, "1"), scavo["thumb"], scavo["resize"], limit=1)) == 1


def test_compose_images_mette_le_immagini_una_accanto_all_altra(tmp_path):
    from PIL import Image
    a = _png(tmp_path / "a.png", 120, 80)
    b = _png(tmp_path / "b.png", 60, 90, (30, 30, 200))
    dati = en.compose_images([a, b], height=100)
    img = Image.open(io.BytesIO(dati))
    assert img.format == "PNG" and img.height == 100 and 150 + 66 <= img.width <= 150 + 67 + en.IMAGE_GAP
    solo = Image.open(io.BytesIO(en.compose_images([a], height=100)))
    assert solo.height == 100 and solo.width == 150
    assert en.compose_images([]) is None
    assert en.compose_images([str(tmp_path / "manca.png"), a]) is not None   # un file rotto non ferma l'altro


def test_figures_for_da_una_figura_alle_unita_citate_che_hanno_immagini(scavo):
    g, cont = scavo["graph"], scavo["cont"]
    n = en.scaffold(g, "it")
    cap = next(c for c in n.chapters if c.anchor and any(
        b.block_type == "embed" and b.ref == _nodo_us(g, "1").node_id for b in c.blocks))
    u1, u2, u3 = (_nodo_us(g, x).node_id for x in ("1", "2", "3"))
    en.generate_chapter(g, n, cap, chat=lambda m: "Prima [[%s]], poi [[%s]] e [[%s]]." % (u1, u2, u3), model="m")
    figure = en.figures_for(g, n, scavo["conn"], scavo["thumb"], scavo["resize"])
    assert set(figure) == {"us:" + u1, "us:" + u2}                  # la 3 non ha file, le non citate no
    assert all(v.startswith(b"\x89PNG") for v in figure.values())
    assert en.figures_for(g, n, None, scavo["thumb"], scavo["resize"]) == {}   # senza DB niente immagini


def test_gli_export_portano_le_figure_e_il_pdf_e_stampabile(scavo, tmp_path):
    g = scavo["graph"]
    n = en.scaffold(g, "it")
    cap = next(c for c in n.chapters if c.anchor and any(
        b.block_type == "embed" and b.ref == _nodo_us(g, "1").node_id for b in c.blocks))
    u1 = _nodo_us(g, "1").node_id
    en.generate_chapter(g, n, cap, chat=lambda m: "Sopra tutto sta [[%s]], una struttura." % u1, model="m")
    figure = en.figures_for(g, n, scavo["conn"], scavo["thumb"], scavo["resize"])
    nome_u1 = _nodo_us(g, "1").name
    html = Path(en.export_file(g, n, "html", tmp_path / "n.html", figures=figure)).read_text(encoding="utf-8")
    assert "data:image/png;base64," in html and nome_u1 in html
    senza = Path(en.export_file(g, n, "html", tmp_path / "s.html")).read_text(encoding="utf-8")
    assert "data:image/png" not in senza
    docx = Path(en.export_file(g, n, "docx", tmp_path / "n.docx", figures=figure))
    assert docx.stat().st_size > Path(en.export_file(g, n, "docx", tmp_path / "s.docx")).stat().st_size
    pdf = Path(en.export_pdf(g, n, tmp_path / "n.pdf", figures=figure, lang="it"))
    assert pdf.read_bytes()[:5] == b"%PDF-"
    import fitz
    doc = fitz.open(str(pdf))
    testo = "".join(page.get_text() for page in doc)
    assert cap.title in testo and "una struttura" in testo and nome_u1 in testo
    assert sum(len(page.get_images()) for page in doc) >= 1
    assert "nosurname" not in testo
    assert "non validato da una persona" in testo.lower() and "\u26a0" not in testo
    assert "Attenzione: 1 paragrafo è una bozza" in testo              # l'avviso in testa, al singolare   # l'avviso su una riga sua, senza il simbolo che Cambria non ha


def test_il_testo_della_scheda_mostra_le_anteprime_dopo_la_prima_menzione():
    sys.path.insert(0, str(_ROOT / "tests" / "utility"))
    from test_em_narrative import grafo_di_prova
    g = grafo_di_prova()
    n = en.scaffold(g, "it")
    cap = n.chapter_by_anchor("epoch_1_1")
    en.generate_chapter(g, n, cap, chat=lambda m: "Prima [[u3]].\n\nPoi [[u2]] e ancora [[u3]].", model="m")
    media = {"u3": [("/tmp/u3_a.png", "foto A"), ("/tmp/u3_b.png", "foto B")], "u2": []}
    html = en.chapter_html(cap, en.name_of(g), media_of=lambda ref: media.get(ref, []))
    primo, secondo = html.split("</p>", 1)[0], html.split("</p>", 1)[1]
    assert 'src="/tmp/u3_a.png"' in secondo.split("<p>", 1)[0]     # subito dopo il primo paragrafo
    assert html.count('src="/tmp/u3_a.png"') == 1 and "foto A" in html and "1.US3" in html
    assert 'src="/tmp/u3_b.png"' in html and "u2_" not in html
