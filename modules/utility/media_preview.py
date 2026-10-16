"""La miniatura e la copia di ogni media, come la scheda le scrive.

La scheda elenca solo i media che hanno una riga in ``media_thumb_table``,
cioè una miniatura (Enzo, 16 ottobre 2026: i ``.glb`` importati da un
em.json non ne avevano e restavano invisibili). Qui le si fa per ogni tipo:

* **immagini**: la miniatura da 150 px e la copia ridimensionata, con le
  routine di sempre (``Media_utility``), che sanno anche dell'archivio remoto;
* **video**: un fotogramma come miniatura, il video copiato;
* **modelli 3D** (anche ``.glb`` e ``.gltf``): la vista del modello resa da
  pyvista — i glTF con ``import_gltf``, che porta i loro colori — e il file
  copiato, come faceva la scheda per obj, stl e gli altri;
* **documenti** (pdf, Word, Excel, csv, txt…): la prima pagina per i PDF,
  un'icona col tipo per gli altri (le prime righe per csv e txt), e il file
  copiato, che poi si apre con il programma del sistema.

I nomi sono quelli della scheda, ``<id>_<nome><suffisso>``, e il nome si
passa alle routine CON l'estensione: tagliano al punto, e senza estensione
«D.07.05» diventava «D.07» (la riga cercava un file che non c'era).
"""
from __future__ import annotations

import os
import tempfile
from typing import Callable, Optional, Tuple

from .media_kinds import split_media_name, suffixes

#: oltre questa misura un modello 3D non si apre per la miniatura: un'icona
_MAX_BYTES_3D = 300 * 1024 * 1024

#: colore della fascia dell'icona, per estensione
_COLORI = {
    "pdf": (179, 11, 0), "doc": (43, 87, 154), "docx": (43, 87, 154), "odt": (43, 87, 154),
    "rtf": (43, 87, 154), "xls": (33, 115, 70), "xlsx": (33, 115, 70), "ods": (33, 115, 70),
    "csv": (33, 115, 70), "txt": (90, 90, 90),
}
_COLORE_3D = (106, 63, 160)
_COLORE_VIDEO = (51, 51, 51)


def _remote(path: str) -> bool:
    try:
        from .pyarchinit_media_utility import is_remote_path
    except ImportError:                                      # pragma: no cover
        return False
    return bool(is_remote_path(path))


def _cartella(path: str) -> str:
    """La cartella con il separatore in fondo: le routine attaccano il nome
    del file alla cartella senza metterlo."""
    p = str(path or "")
    if not p:
        return p
    if _remote(p):
        return p if p.endswith("/") else p + "/"
    return p if p.endswith(("/", os.sep)) else p + os.sep


def make_previews(id_media, src: str, filename: str, filetype: str, mediatype: str,
                  thumb_dir: str, resize_dir: str, *,
                  log: Optional[Callable[[str], None]] = None) -> Tuple[str, str]:
    """Scrive la miniatura in ``thumb_dir`` e la copia in ``resize_dir``;
    restituisce i due nomi come la scheda li registra in
    ``media_thumb_table`` (``filepath`` e ``path_resize``). Un modello o un
    documento che non si riesce a disegnare ha un'icona, e lo si dice a
    ``log``: il media resta, con la sua copia."""
    from .pyarchinit_media_utility import (Media_utility, Media_utility_resize,
                                           Video_utility_resize)
    scrivi = log or (lambda _m: None)
    thumb_suffix, resize_suffix = suffixes(mediatype, filetype)
    thumb_dir, resize_dir = _cartella(thumb_dir), _cartella(resize_dir)
    con_estensione = "%s.%s" % (filename, filetype or "x")
    if mediatype == "image":
        Media_utility().resample_images(id_media, src, con_estensione, thumb_dir, thumb_suffix)
        Media_utility_resize().resample_images(id_media, src, con_estensione, resize_dir, resize_suffix)
    else:
        anteprima = _anteprima(src, filename, filetype, mediatype, scrivi)
        try:
            Media_utility().resample_images(id_media, anteprima, filename + ".png",
                                            thumb_dir, thumb_suffix)
        finally:
            try:
                os.remove(anteprima)
            except OSError:
                pass
        Video_utility_resize().resample_images(id_media, src, con_estensione, resize_dir, resize_suffix)
        if mediatype == "3d_model" and str(filetype).lower() not in ("glb", "gltf"):
            _copia_texture(id_media, src, resize_dir)
    return ("%s_%s%s" % (id_media, filename, thumb_suffix),
            "%s_%s%s" % (id_media, filename, resize_suffix))


def _copia_texture(id_media, src: str, resize_dir: str) -> None:
    """La texture JPG con lo stesso nome del modello va accanto alla copia,
    dove il visore la cerca (come faceva la scheda)."""
    texture = os.path.splitext(src)[0] + ".jpg"
    if not os.path.isfile(texture) or _remote(resize_dir):
        return
    import shutil
    try:
        shutil.copy2(texture, os.path.join(resize_dir, "%s_%s" % (id_media, os.path.basename(texture))))
    except OSError:
        pass


# ------------------------------------------------------------- anteprime

def _png_temporaneo() -> str:
    fd, path = tempfile.mkstemp(prefix="pyarchinit_anteprima_", suffix=".png")
    os.close(fd)
    return path


def _anteprima(src: str, filename: str, filetype: str, mediatype: str, scrivi) -> str:
    """Un PNG da cui ricavare la miniatura: il modello, la pagina, il
    fotogramma, o un'icona quando non si può."""
    out = _png_temporaneo()
    estensione = str(filetype or "").lower()
    try:
        if mediatype == "3d_model":
            if os.path.getsize(src) > _MAX_BYTES_3D:
                raise ValueError("modello troppo grande per la miniatura")
            render_model_png(src, out)
            return out
        if mediatype == "video":
            _fotogramma(src, out)
            return out
        if mediatype == "document" and estensione == "pdf":
            _prima_pagina(src, out)
            return out
        if mediatype == "document":
            _icona(out, estensione, righe=_prime_righe(src) if estensione in ("txt", "csv") else None)
            return out
    except Exception as e:                                   # noqa: BLE001
        scrivi("%s.%s: anteprima non riuscita (%s), al suo posto un'icona" % (filename, filetype, e))
    colore = _COLORE_3D if mediatype == "3d_model" else (
        _COLORE_VIDEO if mediatype == "video" else None)
    _icona(out, "3D" if mediatype == "3d_model" else estensione, colore=colore)
    return out


def render_model_png(src: str, out: str, size: Tuple[int, int] = (400, 400)) -> None:
    """La vista di un modello 3D, scritta in ``out``. I glTF si importano
    come scena (con i loro materiali); gli altri si leggono come superficie,
    con la texture JPG accanto se c'è."""
    import pyvista as pv
    plotter = pv.Plotter(off_screen=True, window_size=list(size))
    try:
        plotter.set_background("white")
        if split_media_name(src)[1].lower() in ("glb", "gltf"):
            plotter.import_gltf(src)
            if not plotter.renderer.GetActors().GetNumberOfItems():
                raise ValueError("il glTF non contiene geometrie")
        else:
            add_model(plotter, src)
        plotter.view_isometric()
        plotter.reset_camera()
        plotter.screenshot(out)
    finally:
        plotter.close()


def _fotogramma(src: str, out: str) -> None:
    import cv2
    vcap = cv2.VideoCapture(src)
    try:
        ok, frame = vcap.read()
        while ok and frame is not None and frame.mean() < 1:
            ok, frame = vcap.read()
        if not ok or frame is None:
            raise ValueError("nessun fotogramma leggibile")
        cv2.imwrite(out, frame)
    finally:
        vcap.release()


def _prima_pagina(src: str, out: str) -> None:
    import fitz
    doc = fitz.open(src)
    try:
        pagina = doc.load_page(0)
        scala = 400.0 / max(pagina.rect.width, pagina.rect.height, 1)
        pagina.get_pixmap(matrix=fitz.Matrix(scala, scala), alpha=False).save(out)
    finally:
        doc.close()


def _prime_righe(src: str, quante: int = 14) -> list:
    try:
        with open(src, "rb") as fh:
            grezzo = fh.read(4096)
    except OSError:
        return []
    for codifica in ("utf-8", "latin-1"):
        try:
            testo = grezzo.decode(codifica)
            break
        except UnicodeDecodeError:
            continue
    return [r[:38] for r in testo.splitlines()[:quante]]


def _font(px: int):
    from PIL import ImageFont
    for nome in ("Arial.ttf", "/System/Library/Fonts/Supplemental/Arial.ttf",
                 "/Library/Fonts/Arial.ttf", "C:/Windows/Fonts/arial.ttf",
                 "DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(nome, px)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def _icona(out: str, etichetta: str, *, righe=None, colore=None) -> None:
    """Un foglio con l'angolo piegato e una fascia col tipo (PDF, DOCX,
    XLSX, 3D…); per csv e txt anche le prime righe del testo."""
    from PIL import Image, ImageDraw
    lato = 400
    im = Image.new("RGB", (lato, lato), (255, 255, 255))
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1, piega = 70, 30, 330, 370, 60
    d.polygon([(x0, y0), (x1 - piega, y0), (x1, y0 + piega), (x1, y1), (x0, y1)],
              fill=(248, 248, 248), outline=(150, 150, 150))
    d.polygon([(x1 - piega, y0), (x1 - piega, y0 + piega), (x1, y0 + piega)],
              fill=(220, 220, 220), outline=(150, 150, 150))
    if righe:
        f = _font(16)
        for i, riga in enumerate(righe):
            d.text((x0 + 14, y0 + 70 + i * 19), riga, fill=(60, 60, 60), font=f)
    fascia = colore or _COLORI.get(str(etichetta).lower(), (90, 90, 90))
    d.rectangle([x0 - 20, 250, x1 - 40, 320], fill=fascia)
    testo = str(etichetta or "?").upper()[:5]
    f = _font(44)
    try:
        l, t, r, b = d.textbbox((0, 0), testo, font=f)
        larghezza, altezza = r - l, b - t
    except AttributeError:                                   # PIL molto vecchio
        larghezza, altezza = d.textsize(testo, font=f)
    d.text(((x0 - 20 + x1 - 40 - larghezza) / 2, 285 - altezza / 2 - 4), testo,
           fill=(255, 255, 255), font=f)
    im.save(out)


# ------------------------------------------------------------- il visore

def read_mesh(path: str):
    """Il modello come superficie unica (``PolyData``): il visore delle
    schede ci misura sopra (``find_closest_point``, ``points``), e un glTF
    si legge come un insieme di blocchi, che si uniscono."""
    import pyvista as pv
    dati = pv.read(path)
    if isinstance(dati, pv.MultiBlock):
        dati = dati.combine().extract_surface()
    elif not isinstance(dati, pv.PolyData) and hasattr(dati, "extract_surface"):
        dati = dati.extract_surface()
    return dati


def add_model(plotter, path: str, mesh=None):
    """Mette il modello nel ``plotter``: i glTF come scena, con i loro
    materiali; gli altri come superficie, con la texture JPG che ha lo
    stesso nome, se c'è. Restituisce la superficie (per le misure)."""
    import pyvista as pv
    if mesh is None:
        mesh = read_mesh(path)
    if split_media_name(path)[1].lower() in ("glb", "gltf"):
        try:
            plotter.import_gltf(path)
            return mesh
        except Exception:                                    # noqa: BLE001
            pass                                             # come superficie
    texture = os.path.splitext(path)[0] + ".jpg"
    if os.path.exists(texture):
        plotter.add_mesh(mesh, texture=pv.read_texture(texture), show_edges=False)
    else:
        plotter.add_mesh(mesh, show_edges=False)
    return mesh


def _qurl_for(path: str):
    """Un indirizzo (http, webdav… dell'archivio remoto) resta un
    indirizzo; un percorso diventa un file locale."""
    from qgis.PyQt.QtCore import QUrl
    testo = str(path or "")
    if "://" in testo:
        return QUrl(testo)
    return QUrl.fromLocalFile(testo)


def open_with_system(path: str) -> bool:
    """Apre il documento con il programma che il sistema usa per quel
    tipo (Word, Excel, il lettore PDF…), o l'indirizzo nel browser."""
    from qgis.PyQt.QtGui import QDesktopServices
    return bool(QDesktopServices.openUrl(_qurl_for(path)))
