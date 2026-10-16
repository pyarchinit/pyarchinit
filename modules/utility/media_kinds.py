"""Che cosa pyArchInit accetta come media, e come lo chiama.

Un elenco solo per tutte le schede (Enzo, 16 ottobre 2026: «fai gestire a
pyarchinit anche i glb»; i media sono anche 3D, pdf, excel, word, txt e csv).
Prima ogni scheda aveva la sua copia: obj, stl, ply, fbx e 3ds sì, i ``.glb``
dei proxy di EMStudio no, e nessun documento.

Il nome si taglia all'ULTIMO punto: le schede tagliavano al primo, e
«D.07.05.jpg» — il nome di un estrattore dell'Extended Matrix — diventava il
file «D» di tipo «07», rifiutato. Modulo puro: niente Qt, niente database.
"""
from __future__ import annotations

import re
from typing import Optional, Tuple

#: le estensioni, in minuscolo, per tipo di media
IMAGE_EXTENSIONS: Tuple[str, ...] = ("jpg", "jpeg", "png", "tiff", "tif", "bmp")
VIDEO_EXTENSIONS: Tuple[str, ...] = ("mp4", "avi", "mov", "mkv", "flv")
MODEL_3D_EXTENSIONS: Tuple[str, ...] = ("obj", "stl", "ply", "fbx", "3ds", "glb", "gltf")
DOCUMENT_EXTENSIONS: Tuple[str, ...] = (
    "pdf", "doc", "docx", "odt", "rtf",          # testi
    "xls", "xlsx", "ods", "csv",                 # fogli di calcolo e tabelle
    "txt",                                       # testo semplice
)

ACCEPTED_EXTENSIONS: Tuple[str, ...] = (
    IMAGE_EXTENSIONS + VIDEO_EXTENSIONS + MODEL_3D_EXTENSIONS + DOCUMENT_EXTENSIONS)

_TIPO = {}
for _tipo, _estensioni in (("image", IMAGE_EXTENSIONS), ("video", VIDEO_EXTENSIONS),
                           ("3d_model", MODEL_3D_EXTENSIONS),
                           ("document", DOCUMENT_EXTENSIONS)):
    for _e in _estensioni:
        _TIPO[_e] = _tipo

#: il suffisso della miniatura per tipo: quelli che le schede scrivevano già
#: per immagini, video e 3D; «_doc_thumb.png» per i documenti
_SUFFISSO_MINIATURA = {"image": "_thumb.png", "video": "_video.png",
                       "3d_model": "_3d_thumb.png", "document": "_doc_thumb.png"}


def split_media_name(path: str) -> Tuple[str, str]:
    """``(nome, estensione)`` del file, tagliato all'ultimo punto; il
    percorso si toglie con ``/`` e con ``\\`` (un percorso di Windows letto
    su un Mac resta un percorso). L'estensione mantiene le maiuscole."""
    base = re.split(r"[\\/]", str(path or ""))[-1]
    if "." not in base.strip("."):
        return base, ""
    nome, _, estensione = base.rpartition(".")
    return nome, estensione


def media_type_of(path: str) -> Optional[str]:
    """``image``, ``video``, ``3d_model``, ``document``; None per quello che
    non è un media (un ``.blend``, un ``.mtl``, un file senza estensione)."""
    return _TIPO.get(split_media_name(path)[1].lower())


def suffixes(mediatype: str, filetype: str) -> Tuple[str, str]:
    """``(suffisso della miniatura, suffisso della copia ridimensionata)``,
    come le schede li compongono: ``<id>_<nome><suffisso>``. Le immagini si
    ridimensionano in PNG; video, modelli 3D e documenti si copiano tali e
    quali, con la loro estensione."""
    if mediatype == "image":
        return _SUFFISSO_MINIATURA["image"], ".png"
    return _SUFFISSO_MINIATURA.get(mediatype, "_thumb.png"), "." + str(filetype or "").lower()
