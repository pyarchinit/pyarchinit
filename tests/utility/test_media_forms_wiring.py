"""Le quattro schede con i media completi (US, Struttura, Materiali,
Ceramica) accettano i .glb e i documenti, e tagliano il nome all'ultimo
punto (Enzo, 16 ottobre 2026: «fai gestire a pyarchinit anche i glb»; i
media sono anche pdf, excel, word, txt e csv).

Ogni scheda aveva la sua copia del codice: si controlla che tutte e quattro
passino per gli stessi moduli (``media_kinds``, ``media_preview``)."""
from __future__ import annotations

import re
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
SCHEDE = ["tabs/US_USM.py", "tabs/Struttura.py", "tabs/Inv_Materiali.py",
          "tabs/pyarchinit_Pottery_mainapp.py"]


def _testo(rel):
    return (PLUGIN_ROOT / rel).read_text(encoding="utf-8")


def _funzione(testo, firma):
    i = testo.index(firma)
    fine = testo.find("\n    def ", i + 10)
    return testo[i:fine if fine > 0 else None]


@pytest.mark.parametrize("scheda", SCHEDE)
def test_accetta_glb_e_documenti(scheda):
    s = _testo(scheda)
    assert "accepted_formats = list(ACCEPTED_EXTENSIONS)" in _funzione(s, "    def dropEvent(self, event):")
    corpo = _funzione(s, "    def load_and_process_image(self, filepath):")
    assert "accepted_3d_formats = list(MODEL_3D_EXTENSIONS)" in corpo
    assert "accepted_document_formats = list(DOCUMENT_EXTENSIONS)" in corpo
    assert "mediatype = 'document'" in corpo and "media_thumb_suffix = '_doc_thumb.png'" in corpo
    assert re.search(r"if mediatype == 'document':\s+make_previews\(", corpo)


@pytest.mark.parametrize("scheda", SCHEDE)
def test_il_nome_si_taglia_all_ultimo_punto(scheda):
    s = _testo(scheda)
    assert 'filename.split(".")[0], filename.split(".")[1]' not in s
    corpo = _funzione(s, "    def load_and_process_image(self, filepath):")
    assert "split_media_name(filename)" in corpo
    # le routine delle miniature tagliano al punto: ricevono il nome CON
    # l'estensione, altrimenti «D.07.05» diventa «D.07»
    chiamate = re.findall(r"M(?:U|UR|U_video|UR_video)\.resample_images\(media_max_num_id, \w+, ([^,]+),", corpo)
    assert chiamate and all(c.strip() == 'filenameorig + "." + filetype' for c in chiamate), chiamate


@pytest.mark.parametrize("scheda", SCHEDE)
def test_il_3d_passa_per_il_modulo_comune(scheda):
    s = _testo(scheda)
    for firma in ("    def process_3d_model(", "    def generate_3d_thumbnail("):
        corpo = _funzione(s, firma)
        assert "render_model_png(" in corpo and "pv.read(" not in corpo, firma
    visore = _funzione(s, "    def show_3d_model(self, file_path):")
    assert "mesh = read_mesh(file_path)" in visore and "add_model(plotter, file_path, mesh)" in visore
    assert "pv.read(" not in visore


@pytest.mark.parametrize("scheda", SCHEDE)
def test_i_documenti_si_aprono_col_programma_del_sistema(scheda):
    s = _testo(scheda)
    aperture = [m.start() for m in re.finditer(r"        def show_media\(file_path, media_type\):", s)]
    assert aperture
    for i in aperture:
        corpo = s[i:s.index("        def query_media(", i)]
        assert "elif media_type == 'document':" in corpo and "open_with_system(full_path)" in corpo
