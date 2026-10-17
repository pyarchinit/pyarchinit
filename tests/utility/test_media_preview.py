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


# -------------------------------------------- i modelli 3D, fuori da QGIS

def test_il_modello_si_disegna_fuori_dal_processo(cartelle, monkeypatch):
    """Su macOS ogni disegno di VTK dentro QGIS lasciava viva una vista
    Cocoa (``vtkCocoaGLView``) dopo il plotter chiuso: alla prima notifica
    della finestra — chiudere il riepilogo dell'importazione dell'em.json —
    VTK chiamava un oggetto già distrutto e QGIS si chiudeva (Enzo, 17
    ottobre 2026). Il disegno si fa in un altro processo: qui, sul posto,
    è vietato."""
    pytest.importorskip("pyvista")
    import modules.utility.media_preview as mp

    def vietato(*_a, **_k):
        raise AssertionError("modello disegnato dentro il processo di QGIS")

    monkeypatch.setattr(mp, "_disegna", vietato)
    base, _thumb, _resize = cartelle
    out = base / "vista.png"
    mp.render_model_png(str(GLB), str(out), (160, 160))
    assert _colori(out)[0] > 3


def test_tanti_modelli_un_processo_solo(cartelle, monkeypatch):
    """Un'importazione con 65 proxy non apre 65 processi: uno per tutti,
    e un modello che non si disegna non ferma gli altri."""
    pytest.importorskip("pyvista")
    import modules.utility.media_preview as mp
    avvii = []
    vero = mp._avvia
    monkeypatch.setattr(mp, "_avvia", lambda *a, **k: avvii.append(1) or vero(*a, **k))
    base, _thumb, _resize = cartelle
    rotto = base / "rotto.glb"
    rotto.write_bytes(b"non e un glb")
    lavori = [(str(GLB), str(base / "a.png")), (str(rotto), str(base / "b.png")),
              (str(GLB), str(base / "c.png"))]
    passi = []
    esiti = mp.render_models_png(lavori, (120, 120), progress=lambda f, t, n: passi.append((f, t)))
    assert len(avvii) == 1
    assert esiti[str(base / "a.png")] is None and esiti[str(base / "c.png")] is None
    assert esiti[str(base / "b.png")]                            # il perché
    assert _colori(base / "a.png")[0] > 3 and _colori(base / "c.png")[0] > 3
    assert passi[-1] == (3, 3)


def test_un_modello_che_uccide_il_processo_non_ferma_gli_altri(cartelle, monkeypatch):
    """Se VTK cade su un modello, quel modello ha l'icona e gli altri si
    disegnano in un processo nuovo."""
    pytest.importorskip("pyvista")
    import modules.utility.media_preview as mp
    monkeypatch.setattr(mp, "_AVVIO", mp._AVVIO.replace(
        "from modules.utility.media_preview import _servi\n",
        "import os, modules.utility.media_preview as m\n"
        "vero = m._disegna\n"
        "m._disegna = lambda s, o, z: os._exit(3) if s.endswith('muore.glb') else vero(s, o, z)\n"
        "from modules.utility.media_preview import _servi\n"))
    base, _thumb, _resize = cartelle
    muore = base / "muore.glb"
    shutil.copy2(GLB, muore)
    lavori = [(str(muore), str(base / "a.png")), (str(GLB), str(base / "b.png"))]
    esiti = mp.render_models_png(lavori, (100, 100))
    assert esiti[str(base / "a.png")] and "3" in esiti[str(base / "a.png")]
    assert esiti[str(base / "b.png")] is None and _colori(base / "b.png")[0] > 3


def test_un_modello_che_non_finisce_si_lascia_indietro(cartelle):
    """Un disegno che non finisce non blocca la finestra: passato il tempo,
    il processo si ferma e il modello avrà l'icona."""
    import modules.utility.media_preview as mp
    base, _thumb, _resize = cartelle
    lavori = [(str(GLB), str(base / ("%d.png" % i))) for i in range(2)]
    esiti = mp.render_models_png(lavori, (64, 64), timeout=0.01)
    assert all(esiti[o] and "tempo" in esiti[o] for _s, o in lavori), esiti


def test_un_modello_troppo_grande_non_si_apre(cartelle, monkeypatch):
    import modules.utility.media_preview as mp
    monkeypatch.setattr(mp, "_MAX_BYTES_3D", 10)
    monkeypatch.setattr(mp, "_avvia", lambda *a, **k: pytest.fail("processo avviato per niente"))
    base, _thumb, _resize = cartelle
    esiti = mp.render_models_png([(str(GLB), str(base / "a.png"))])
    assert "troppo grande" in esiti[str(base / "a.png")]


def test_la_miniatura_usa_il_disegno_gia_pronto(cartelle, monkeypatch):
    """L'importazione disegna tutti i modelli insieme e passa il disegno a
    ``make_previews``, che non ridisegna e non cancella il file di altri."""
    import modules.utility.media_preview as mp
    monkeypatch.setattr(mp, "render_models_png", lambda *a, **k: pytest.fail("ridisegnato"))
    base, thumb, resize = cartelle
    from PIL import Image
    pronto = base / "pronto.png"
    Image.new("RGB", (300, 300), (10, 120, 200)).save(pronto)
    src = base / "SU002.glb"
    shutil.copy2(GLB, src)
    nomi = mp.make_previews(5, str(src), "SU002", "glb", "3d_model", thumb, resize,
                            model_png=str(pronto))
    assert nomi == ("5_SU002_3d_thumb.png", "5_SU002.glb")
    im = Image.open(Path(thumb, nomi[0])).convert("RGB")
    assert im.getpixel((im.size[0] // 2, im.size[1] // 2)) == (10, 120, 200)
    assert pronto.is_file()


def test_un_disegno_gia_fallito_da_l_icona_senza_riprovare(cartelle, monkeypatch):
    import modules.utility.media_preview as mp
    monkeypatch.setattr(mp, "render_models_png", lambda *a, **k: pytest.fail("ridisegnato"))
    base, thumb, resize = cartelle
    src = base / "SU002.glb"
    shutil.copy2(GLB, src)
    avvisi = []
    nomi = mp.make_previews(5, str(src), "SU002", "glb", "3d_model", thumb, resize,
                            model_error="il glTF non contiene geometrie", log=avvisi.append)
    assert Path(thumb, nomi[0]).is_file()
    assert avvisi and "il glTF non contiene geometrie" in avvisi[0]
