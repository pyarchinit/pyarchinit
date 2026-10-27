"""Su macOS l'installatore cercava QGIS 4 solo in una versione scritta fissa:
qualunque versione (4_2_2, 4.4, «QGIS 4») va trovata, in /Applications e in
~/Applications; e il Python di ripiego di QGIS 4 dev'essere uno che parte
(il lanciatore Contents/MacOS/python, che imposta PYTHONHOME)."""
from __future__ import annotations

import glob
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
for p in (str(_ROOT / "ext_libs"), str(_ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

from modules.utility import python_env as pe  # noqa: E402


def _app(radice, nome):
    macos = radice / nome / "Contents" / "MacOS"
    macos.mkdir(parents=True)
    return macos


def test_ogni_qgis_installato(tmp_path):
    app, utente = tmp_path / "Applications", tmp_path / "home" / "Applications"
    for nome in ("QGIS.app", "QGIS-LTR.app", "QGIS-final-4_2_2.app", "QGIS 4.app"):
        _app(app, nome)
    _app(utente, "QGIS-final-4_4_0.app")
    _app(app, "Qualcosa.app")
    (app / "QGIS-rotto.app").mkdir()                              # senza Contents/MacOS
    trovati = pe.mac_qgis_apps(roots=(str(app), str(utente)))
    nomi = sorted(Path(t).parents[1].name for t in trovati)
    assert nomi == ["QGIS 4.app", "QGIS-LTR.app", "QGIS-final-4_2_2.app", "QGIS-final-4_4_0.app", "QGIS.app"]


def test_due_qgis_con_lo_stesso_nome_restano_tutti_e_due(tmp_path):
    a = _app(tmp_path / "Applications", "QGIS-final-4_2_2.app")
    b = _app(tmp_path / "home" / "Applications", "QGIS-final-4_2_2.app")
    percorsi = pe.with_qgis_apps({"standard": "/x/QGIS.app/Contents/MacOS"}, [str(a), str(b)])
    assert str(a) in percorsi.values() and str(b) in percorsi.values()
    assert percorsi["standard"] == "/x/QGIS.app/Contents/MacOS"


def test_il_python_di_ripiego_di_qgis4_e_il_lanciatore(tmp_path):
    macos = _app(tmp_path, "QGIS-final-4_2_2.app")
    candidati = pe.mac_fallback_pythons([str(macos)], (3, 12))
    assert candidati[0] == str(macos / "python")                  # il lanciatore, prima di tutto
    assert str(macos / "bin" / "python3") in candidati            # il QGIS 3 com'era


@pytest.mark.skipif(not glob.glob("/Applications/QGIS*4*.app/Contents/MacOS/python"),
                    reason="nessun QGIS 4 installato qui")
def test_il_lanciatore_di_qgis4_parte_davvero():
    lanciatore = sorted(glob.glob("/Applications/QGIS*4*.app/Contents/MacOS/python"))[-1]
    risposta = pe.probe(lanciatore)
    assert risposta and risposta[0] == 3 and risposta[3]          # Python 3 con pip
