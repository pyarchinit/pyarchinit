"""Che cosa pyArchInit accetta come media, e come lo chiama (Enzo, 16
ottobre 2026: «fai gestire a pyarchinit anche i glb»; «gestisce come media,
oltre alle immagini, anche 3D, pdf, excel, word, txt, csv»).

Un elenco solo per tutte le schede, invece di una copia per scheda: le
schede accettavano obj, stl, ply, fbx e 3ds ma non i glb dei proxy di
EMStudio, e nessun documento. E il nome si taglia all'ULTIMO punto: le
schede tagliavano al primo, e «D.07.05.jpg» diventava il file «D» di
tipo «07», rifiutato."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from modules.utility.media_kinds import (  # noqa: E402
    ACCEPTED_EXTENSIONS, DOCUMENT_EXTENSIONS, MODEL_3D_EXTENSIONS,
    media_type_of, split_media_name, suffixes)


@pytest.mark.parametrize("nome, tipo", [
    ("SU002.glb", "3d_model"), ("scena.GLTF", "3d_model"), ("rilievo.obj", "3d_model"),
    ("pezzo.stl", "3d_model"), ("nuvola.ply", "3d_model"),
    ("D.05 Diaconescu 2013.pdf", "document"), ("relazione.docx", "document"),
    ("vecchia.doc", "document"), ("misure.xlsx", "document"), ("misure.xls", "document"),
    ("tabella.csv", "document"), ("note.txt", "document"), ("testo.odt", "document"),
    ("foglio.ods", "document"), ("lettera.rtf", "document"),
    ("D.07.05.jpg", "image"), ("pianta.TIF", "image"), ("scavo.mp4", "video"),
])
def test_il_tipo_viene_dall_estensione(nome, tipo):
    assert media_type_of(nome) == tipo


@pytest.mark.parametrize("nome", ["GreatTemple.blend", "colonna.mtl", "rilievo.psx", "senza_estensione", ""])
def test_quello_che_non_e_un_media_resta_fuori(nome):
    assert media_type_of(nome) is None


def test_glb_e_documenti_sono_accettati_dappertutto():
    assert {"glb", "gltf", "obj", "stl", "ply", "fbx", "3ds"} <= set(MODEL_3D_EXTENSIONS)
    assert {"pdf", "doc", "docx", "xls", "xlsx", "csv", "txt", "odt", "ods", "rtf"} <= set(DOCUMENT_EXTENSIONS)
    assert set(MODEL_3D_EXTENSIONS) | set(DOCUMENT_EXTENSIONS) | {"jpg", "png", "mp4"} <= set(ACCEPTED_EXTENSIONS)


@pytest.mark.parametrize("percorso, atteso", [
    ("D.07.05.jpg", ("D.07.05", "jpg")),
    ("/progetto/EM/DosCo/D.07 Maison Carree Nimes.png", ("D.07 Maison Carree Nimes", "png")),
    (r"C:\scavo\foto\US 12.JPG", ("US 12", "JPG")),
    ("SM_OB_EST_L_LOD1@lod3-aton-heriverse.glb", ("SM_OB_EST_L_LOD1@lod3-aton-heriverse", "glb")),
    ("senza_estensione", ("senza_estensione", "")),
])
def test_il_nome_si_taglia_all_ultimo_punto(percorso, atteso):
    assert split_media_name(percorso) == atteso


def test_i_suffissi_seguono_quelli_delle_schede():
    assert suffixes("image", "jpg") == ("_thumb.png", ".png")
    assert suffixes("video", "MOV") == ("_video.png", ".mov")
    assert suffixes("3d_model", "glb") == ("_3d_thumb.png", ".glb")
    assert suffixes("document", "PDF") == ("_doc_thumb.png", ".pdf")
