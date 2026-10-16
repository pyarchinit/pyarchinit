"""Ogni media ha la sua miniatura e la sua copia, come quelli caricati dalla
scheda (Enzo, 16 ottobre 2026: «non trova i media»; «fai gestire anche i
glb»; media anche pdf, excel, word, txt, csv).

La scheda elenca solo i media che hanno una miniatura: i ``.glb`` importati
dall'em.json non ne avevano, e restavano invisibili. E la miniatura deve
chiamarsi come la riga del database dice: con «D.07.05» la routine delle
immagini tagliava al punto e scriveva «2_D.07_thumb.png» mentre la riga
cercava «2_D.07.05_thumb.png»."""
from __future__ import annotations

import filecmp
import shutil
import sys
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from modules.utility.media_preview import make_previews  # noqa: E402

GLB = PLUGIN_ROOT / "ext_libs" / "s3dgraphy" / "JSON_config" / "src" / "3D" / "SF.glb"


@pytest.fixture
def cartelle(tmp_path):
    thumb, resize = tmp_path / "thumb", tmp_path / "resize"
    thumb.mkdir()
    resize.mkdir()
    return tmp_path, str(thumb) + "/", str(resize) + "/"


def _colori(png):
    from PIL import Image
    im = Image.open(png).convert("RGB")
    return len(im.getcolors(1 << 20) or []), im.size


def test_immagine_col_punto_nel_nome(cartelle):
    base, thumb, resize = cartelle
    from PIL import Image
    src = base / "D.07.05.jpg"
    Image.new("RGB", (800, 400), (180, 120, 60)).save(src)
    nomi = make_previews(2, str(src), "D.07.05", "jpg", "image", thumb, resize)
    assert nomi == ("2_D.07.05_thumb.png", "2_D.07.05.png")
    assert Path(thumb, nomi[0]).is_file() and Path(resize, nomi[1]).is_file()
    assert max(_colori(Path(thumb, nomi[0]))[1]) <= 150


def test_glb_ha_la_sua_miniatura_e_la_sua_copia(cartelle):
    pytest.importorskip("pyvista")
    base, thumb, resize = cartelle
    src = base / "SU002.glb"
    shutil.copy2(GLB, src)
    nomi = make_previews(5, str(src), "SU002", "glb", "3d_model", thumb, resize)
    assert nomi == ("5_SU002_3d_thumb.png", "5_SU002.glb")
    assert _colori(Path(thumb, nomi[0]))[0] > 3                 # c'è un modello, non un foglio bianco
    assert filecmp.cmp(src, Path(resize, nomi[1]), shallow=False)


def test_pdf_mostra_la_prima_pagina(cartelle):
    fitz = pytest.importorskip("fitz")
    base, thumb, resize = cartelle
    src = base / "D.05 Relazione.pdf"
    doc = fitz.open()
    pagina = doc.new_page()
    pagina.draw_rect(fitz.Rect(40, 40, 400, 300), color=(0.8, 0.1, 0.1), fill=(0.8, 0.1, 0.1))
    pagina.insert_text((50, 360), "Templu Mare", fontsize=30)
    doc.save(str(src))
    doc.close()
    nomi = make_previews(9, str(src), "D.05 Relazione", "pdf", "document", thumb, resize)
    assert nomi == ("9_D.05 Relazione_doc_thumb.png", "9_D.05 Relazione.pdf")
    from PIL import Image
    im = Image.open(Path(thumb, nomi[0])).convert("RGB")
    rossi = sum(1 for p in im.getdata() if p[0] > 150 and p[1] < 80 and p[2] < 80)
    assert rossi > 50                                            # il riquadro rosso della pagina
    assert filecmp.cmp(src, Path(resize, nomi[1]), shallow=False)


@pytest.mark.parametrize("nome, estensione, contenuto", [
    ("relazione", "docx", b"PK\x03\x04finto"), ("misure", "xlsx", b"PK\x03\x04finto"),
    ("tabella", "csv", b"us;quota\n1;12.3\n2;11.8\n"), ("note", "txt", "Scavo 2016\nsaggio S2".encode()),
])
def test_word_excel_csv_txt_hanno_un_icona(cartelle, nome, estensione, contenuto):
    base, thumb, resize = cartelle
    src = base / ("%s.%s" % (nome, estensione))
    src.write_bytes(contenuto)
    nomi = make_previews(3, str(src), nome, estensione, "document", thumb, resize)
    assert nomi == ("3_%s_doc_thumb.png" % nome, "3_%s.%s" % (nome, estensione))
    assert _colori(Path(thumb, nomi[0]))[0] > 2
    assert filecmp.cmp(src, Path(resize, nomi[1]), shallow=False)


def test_un_modello_rotto_ha_comunque_una_miniatura(cartelle):
    base, thumb, resize = cartelle
    src = base / "rotto.glb"
    src.write_bytes(b"non e un glb")
    avvisi = []
    nomi = make_previews(4, str(src), "rotto", "glb", "3d_model", thumb, resize, log=avvisi.append)
    assert Path(thumb, nomi[0]).is_file() and Path(resize, nomi[1]).is_file()
    assert avvisi and "rotto" in avvisi[0]


def test_cartelle_senza_barra_finale(cartelle):
    base, thumb, resize = cartelle
    src = base / "note.txt"
    src.write_text("x", encoding="utf-8")
    nomi = make_previews(1, str(src), "note", "txt", "document", thumb.rstrip("/"), resize.rstrip("/"))
    assert Path(thumb, nomi[0]).is_file() and Path(resize, nomi[1]).is_file()


def test_il_visore_legge_il_glb_come_una_superficie():
    pytest.importorskip("pyvista")
    from modules.utility.media_preview import read_mesh
    mesh = read_mesh(str(GLB))
    assert mesh.n_points > 0
    assert mesh.find_closest_point(mesh.center) >= 0           # serve alle misure del visore


def test_un_documento_remoto_si_apre_come_indirizzo():
    """Con l'archivio remoto (webdav, http) il percorso del documento è un
    indirizzo: «fromLocalFile» ne faceva un file che non esiste."""
    pytest.importorskip("qgis.PyQt")
    from modules.utility.media_preview import _qurl_for
    assert _qurl_for("https://archivio.example.org/media/D.05.pdf").scheme() == "https"
    assert _qurl_for("/Users/enzo/pyarchinit_5/resize/9_D.05.pdf").isLocalFile()
