"""Cambria (le schede in PDF) si installa da sé, nei font dell'utente: prima
macOS apriva una cartella e chiedeva un doppio clic su ogni file."""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from modules.utility import font_install as fi  # noqa: E402

FILE = ("Cambria.ttf", "cambria.ttc", "cambriab.ttf", "cambriai.ttf", "cambriaz.ttf")
INIT = (_ROOT / "__init__.py").read_text(encoding="utf-8")


def test_dalla_cartella_bin(tmp_path):
    bin_, font = tmp_path / "bin", tmp_path / "Fonts"
    bin_.mkdir()
    for f in FILE:
        (bin_ / f).write_bytes(b"font " + f.encode())
    assert sorted(fi.install_cambria(str(bin_), str(font))) == sorted(FILE)
    assert (font / "cambria.ttc").read_bytes() == b"font cambria.ttc"
    assert fi.install_cambria(str(bin_), str(font)) == []          # già installato: niente
    assert fi.cambria_installed(str(font))


def test_dallo_zip_del_plugin_se_bin_non_li_ha(tmp_path):
    archivio = tmp_path / "cambria.zip"
    with zipfile.ZipFile(archivio, "w") as z:
        for f in FILE:
            z.writestr(f, b"zip " + f.encode())
    font = tmp_path / "Fonts"
    copiati = fi.install_cambria(str(tmp_path / "bin_vuota"), str(font), zip_path=str(archivio))
    assert sorted(copiati) == sorted(FILE) and (font / "cambriab.ttf").read_bytes() == b"zip cambriab.ttf"


def test_lo_zip_vero_del_plugin(tmp_path):
    copiati = fi.install_cambria(str(tmp_path / "niente"), str(tmp_path / "Fonts"),
                                 zip_path=str(_ROOT / "resources" / "dbfiles" / "cambria.zip"))
    assert "cambria.ttc" in copiati


def test_niente_da_copiare_si_dice(tmp_path):
    assert fi.install_cambria(str(tmp_path / "a"), str(tmp_path / "Fonts"), zip_path=str(tmp_path / "no.zip")) == []
    assert not fi.cambria_installed(str(tmp_path / "Fonts"))


def test_l_avvio_installa_da_solo():
    corpo = INIT[INIT.index("    def install_fonts(splash=None) -> None:"):]
    corpo = corpo[:corpo.index("\ndef ", 10)]
    assert "install_cambria(" in corpo and "user_fonts_dir(" in corpo
