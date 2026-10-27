"""Cambria (le schede in PDF) si installa da sé, nei font dell'utente: prima
macOS apriva una cartella e chiedeva un doppio clic su ogni file. ReportLab
cerca i nomi esatti (``Cambria.ttc``, ``cambriab.ttf``, ``cambriai.ttf``,
``cambriaz.ttf``): conta solo quello, con le maiuscole giuste (Linux), file
interi e veri font."""
from __future__ import annotations

import errno
import sys
import zipfile
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from modules.utility import font_install as fi  # noqa: E402

# come nello zip del plugin e in ~/pyarchinit_5/bin: «cambria.ttc» minuscolo
SORGENTI = ("Cambria.ttf", "cambria.ttc", "cambriab.ttf", "cambriai.ttf", "cambriaz.ttf")
INIT = (_ROOT / "__init__.py").read_text(encoding="utf-8")


def _font(nome):
    testa = b"ttcf" if nome.lower().endswith(".ttc") else b"\x00\x01\x00\x00"
    return testa + b" finto " + nome.encode() + b" " * 64


def _bin(cartella):
    cartella.mkdir(parents=True)
    for f in SORGENTI:
        (cartella / f).write_bytes(_font(f))
    return cartella


def test_dalla_cartella_bin_coi_nomi_che_cerca_reportlab(tmp_path):
    font = tmp_path / "Fonts"
    copiati = fi.install_cambria(str(_bin(tmp_path / "bin")), str(font))
    assert set(fi.REQUIRED) <= set(copiati)
    # i nomi esatti, anche dove le maiuscole contano (Linux)
    assert {"Cambria.ttc", "cambriab.ttf", "cambriai.ttf", "cambriaz.ttf"} <= set(p.name for p in font.iterdir())
    assert fi.cambria_installed(str(font))
    assert fi.install_cambria(str(tmp_path / "bin"), str(font)) == []          # già tutto: niente


def test_una_cartella_col_solo_cambria_ttf_non_e_installata(tmp_path):
    font = tmp_path / "Fonts"
    font.mkdir()
    (font / "Cambria.ttf").write_bytes(_font("Cambria.ttf"))
    assert not fi.cambria_installed(str(font))
    fi.install_cambria(str(_bin(tmp_path / "bin")), str(font))
    assert fi.cambria_installed(str(font))


def test_un_file_vuoto_o_rovinato_si_rifa(tmp_path):
    font = tmp_path / "Fonts"
    font.mkdir()
    (font / "Cambria.ttc").write_bytes(b"")
    (font / "cambriab.ttf").write_bytes(b"spazzatura" * 10)
    assert not fi.cambria_installed(str(font))
    copiati = fi.install_cambria(str(_bin(tmp_path / "bin")), str(font))
    assert "Cambria.ttc" in copiati and "cambriab.ttf" in copiati
    assert (font / "Cambria.ttc").read_bytes() == _font("cambria.ttc")
    assert fi.cambria_installed(str(font))


def test_una_copia_interrotta_non_lascia_mezzi_file(tmp_path, monkeypatch):
    """Disco pieno a metà: niente file troncato col nome giusto (che poi
    conterebbe come installato e romperebbe la scheda US per sempre)."""
    import shutil
    vero = shutil.copyfileobj

    def pieno(src, dst, *a, **k):
        dst.write(src.read(10))
        raise OSError(errno.ENOSPC, "No space left on device")
    monkeypatch.setattr(shutil, "copyfileobj", pieno)
    font = tmp_path / "Fonts"
    assert fi.install_cambria(str(_bin(tmp_path / "bin")), str(font)) == []
    monkeypatch.setattr(shutil, "copyfileobj", vero)
    assert not [p.name for p in font.iterdir()] if font.exists() else True
    assert not fi.cambria_installed(str(font))


def test_dallo_zip_del_plugin_se_bin_non_li_ha(tmp_path):
    archivio = tmp_path / "cambria.zip"
    with zipfile.ZipFile(archivio, "w") as z:
        for f in SORGENTI:
            z.writestr(f, _font(f))
    font = tmp_path / "Fonts"
    fi.install_cambria(str(tmp_path / "bin_vuota"), str(font), zip_path=str(archivio))
    assert fi.cambria_installed(str(font)) and (font / "Cambria.ttc").exists()


def test_uno_zip_rotto_non_ferma_niente(tmp_path):
    archivio = tmp_path / "cambria.zip"
    with zipfile.ZipFile(archivio, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("cambria.ttc", _font("cambria.ttc") * 200)
    dati = bytearray(archivio.read_bytes())
    for i in range(60, 120):
        dati[i] ^= 0x5A                                    # flusso compresso guasto
    archivio.write_bytes(bytes(dati))
    font = tmp_path / "Fonts"
    assert fi.install_cambria(None, str(font), zip_path=str(archivio)) == []
    assert not fi.cambria_installed(str(font))


def test_lo_zip_vero_del_plugin(tmp_path):
    font = tmp_path / "Fonts"
    fi.install_cambria(str(tmp_path / "niente"), str(font),
                       zip_path=str(_ROOT / "resources" / "dbfiles" / "cambria.zip"))
    assert fi.cambria_installed(str(font))
    from reportlab.pdfbase.ttfonts import TTFont
    TTFont("CambriaProva", str(font / "Cambria.ttc"))            # ReportLab lo apre


def test_senza_cartella_di_origine_non_si_usa_un_percorso_relativo(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _bin(tmp_path / "bin")                                 # «bin» relativo: non va preso
    assert fi.install_cambria("bin", str(tmp_path / "Fonts")) == []


def test_l_avvio_lo_chiama_sempre_e_non_si_blocca():
    corpo = INIT[INIT.index("    def install_fonts(splash=None) -> None:"):]
    corpo = corpo[:corpo.index("\ndef ", 10)]
    assert "install_cambria(" in corpo and "except Exception" in corpo
    assert "PYARCHINIT_HOME" in corpo and "os.environ.get('PYARCHINIT_HOME'" not in corpo
    assert "subprocess.run([\"fc-cache\"" not in corpo                 # non aspetta fc-cache


def test_gli_zip_non_si_riestraggono_a_ogni_avvio():
    """pyarchinit_folder_installation dice «già estratto» se c'è un percorso
    dopo l'estrazione: per cambria.zip cercava «bin/cambria», che non esiste
    mai (lo zip ha i file sciolti), e riestraeva 4,4 MB a ogni avvio."""
    import ast as _ast
    sorgente = (_ROOT / "modules" / "utility" / "pyarchinit_folder_installation.py").read_text(encoding="utf-8")
    coppie = None
    for nodo in _ast.walk(_ast.parse(sorgente)):
        if isinstance(nodo, _ast.Assign) and getattr(nodo.targets[0], "id", "") == "zip_extracts":
            coppie = _ast.literal_eval(nodo.value)
    assert coppie
    for zip_name, prova in coppie:
        nomi = zipfile.ZipFile(_ROOT / "resources" / "dbfiles" / zip_name).namelist()
        assert any(n.rstrip("/") == prova or n.startswith(prova + "/") for n in nomi), (zip_name, prova)
