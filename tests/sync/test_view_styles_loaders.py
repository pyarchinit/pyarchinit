"""I caricatori di `pyarchinit_pyqgis.py` passano tutti da `_stile_vista`
(Task 4 degli Stili delle viste): per ogni vista del registro, su SQLite e
su PostgreSQL, subito dopo la creazione del layer; i QML forniti e le
etichette non si applicano più a mano."""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from modules.utility.view_styles import VIEWS  # noqa: E402

SRC = _ROOT / "modules" / "gis" / "pyarchinit_pyqgis.py"
NOMI = {v.name for v in VIEWS}


def _righe():
    return SRC.read_text(encoding="utf-8").split("\n")


def test_ogni_vista_caricata_da_sqlite_passa_da_stile_vista():
    righe = _righe()
    carichi = [(i, m.group(1), m.group(2)) for i, r in enumerate(righe)
               for m in [re.match(r"^\s*(\w+) = self\._load_spatialite_view\(\w+, '([a-z_]+)'", r)] if m]
    assert carichi
    for i, var, vista in carichi:
        if vista not in NOMI:
            continue
        finestra = "\n".join(righe[i + 1:i + 4])
        assert "self._stile_vista(%s, '%s'" % (var, vista) in finestra, (i + 1, righe[i].strip())


def test_ogni_vista_caricata_da_postgres_passa_da_stile_vista():
    righe = _righe()
    trovate = 0
    for i, r in enumerate(righe):
        m = re.match(r'^\s*uri\w*\.setDataSource\("public", "([a-z_]+)"', r)
        if not m or m.group(1) not in NOMI:
            continue
        trovate += 1
        finestra = "\n".join(righe[i + 1:i + 8])
        assert "self._stile_vista(" in finestra and "'%s'" % m.group(1) in finestra, (i + 1, r.strip())
    assert trovate >= 20


def test_i_qml_forniti_e_le_etichette_non_si_applicano_piu_a_mano():
    testo = SRC.read_text(encoding="utf-8")
    assert "quote_us_view.qml" not in testo
    assert "label_us_view(" not in testo and "label_quote_view(" not in testo
    for m in re.finditer(r"^(\s*)(\w+)\.apply_style_to_layer\((\w+)", testo, re.M):
        prima = testo[:m.start()].split("\n")[-2:]
        assert any("self._stile_salvato(%s)" % m.group(3) in r for r in prima), m.group(0)


def test_i_metodi_dello_stile_esistono():
    albero = ast.parse(SRC.read_text(encoding="utf-8"))
    nomi = {n.name for n in ast.walk(albero) if isinstance(n, ast.FunctionDef)}
    assert {"_stile_vista", "_stile_salvato", "_engine_stili", "_sito_corrente"} <= nomi
