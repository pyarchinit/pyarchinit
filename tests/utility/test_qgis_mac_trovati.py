"""Su macOS l'installatore cercava QGIS 4 solo in
/Applications/QGIS-final-4_0_0.app: qualunque versione (4_2_2, 4.4, «QGIS 4»)
va trovata, in /Applications e in ~/Applications."""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
for p in (str(_ROOT / "ext_libs"), str(_ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

from modules.utility import python_env as pe  # noqa: E402

INIT = (_ROOT / "__init__.py").read_text(encoding="utf-8")


def test_ogni_qgis_installato(tmp_path):
    app, utente = tmp_path / "Applications", tmp_path / "home" / "Applications"
    for nome in ("QGIS.app", "QGIS-LTR.app", "QGIS-final-4_2_2.app", "QGIS 4.app"):
        (app / nome / "Contents" / "MacOS").mkdir(parents=True)
    (utente / "QGIS-final-4_4_0.app" / "Contents" / "MacOS").mkdir(parents=True)
    (app / "Qualcosa.app" / "Contents" / "MacOS").mkdir(parents=True)
    (app / "QGIS-rotto.app").mkdir()                              # senza Contents/MacOS
    trovati = pe.mac_qgis_apps(roots=(str(app), str(utente)))
    nomi = sorted(Path(t).parents[1].name for t in trovati)
    assert nomi == ["QGIS 4.app", "QGIS-LTR.app", "QGIS-final-4_2_2.app", "QGIS-final-4_4_0.app", "QGIS.app"]
    assert all(t.endswith("/Contents/MacOS") for t in trovati)


def test_l_installatore_non_ha_piu_un_qgis4_scritto_fisso():
    assert "4_0_0" not in INIT
    assert "mac_qgis_apps(" in INIT
    fallback = INIT[INIT.index("    def _python_fallbacks() -> List[str]:"):]
    fallback = fallback[:fallback.index("\n    @staticmethod", 10)]
    # QGIS 4 tiene il Python in Contents/MacOS/python3.12
    assert "subdir in (qgis_base," in fallback
