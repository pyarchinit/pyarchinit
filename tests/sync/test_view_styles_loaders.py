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


SPECIALI = ("us_view_dot.qml", "us_view_preview.qml", "us_vuote.qml")


def _righe():
    return SRC.read_text(encoding="utf-8").split("\n")


def _esente(righe, i) -> bool:
    """Un layer con uno stile fisso suo (anteprima della matrice, «US
    Disegno») o di servizio (`layerUS_us`) non prende lo stile della vista."""
    if "layerUS_us" in righe[i]:
        return True
    finestra = "\n".join(righe[i + 1:i + 16])
    return any(q in finestra for q in SPECIALI)


def _carichi(righe):
    """`(riga, variabile, vista)` per ogni creazione di un layer da una
    vista del registro: `_load_spatialite_view(...)`, oppure
    `setDataSource(<schema>, '<vista>'…)` seguito da `QgsVectorLayer(uri.uri(), …)`."""
    fuori = []
    for i, r in enumerate(righe):
        if r.strip().startswith("#"):
            continue
        m = re.match(r"^\s*(\w+) = self\._load_spatialite_view\(\w+, '([a-z_]+)'", r)
        if m and m.group(2) in NOMI:
            fuori.append((i, m.group(1), m.group(2)))
            continue
        m = re.match(r"""^\s*(uri\w*)\.setDataSource\(\s*['"][^'"]*['"]\s*,\s*['"]([a-z_]+)['"]""", r)
        if m and m.group(2) in NOMI:
            for j in range(i + 1, i + 8):
                mm = re.match(r"^\s*(\w+) = QgsVectorLayer\(%s\.uri\(\)" % re.escape(m.group(1)), righe[j])
                if mm:
                    fuori.append((j, mm.group(1), m.group(2)))
                    break
    return fuori


def test_ogni_vista_caricata_passa_da_stile_vista_su_sqlite_e_postgres():
    righe = _righe()
    carichi = _carichi(righe)
    assert len(carichi) >= 60, len(carichi)
    for i, var, vista in carichi:
        finestra = "\n".join(righe[i + 1:i + 4])
        if _esente(righe, i):
            assert "_stile_vista(" not in finestra, (i + 1, righe[i].strip())
            continue
        assert "self._stile_vista(%s, '%s'" % (var, vista) in finestra, (i + 1, righe[i].strip())


def test_le_quote_e_le_unita_delle_schede_prendono_il_ripiego():
    """Dove la vista nasceva già con un QML o con lo stile scelto, il
    ripiego è acceso; le quote sempre."""
    righe = _righe()
    for i, var, vista in _carichi(righe):
        if _esente(righe, i):
            continue
        finestra = "\n".join(righe[i + 1:i + 4])
        if vista in ("pyarchinit_quote_view", "pyarchinit_quote_usm_view"):
            assert "fallback=True" in finestra, (i + 1, righe[i].strip())


def test_i_qml_forniti_e_le_etichette_non_si_applicano_piu_a_mano():
    testo = SRC.read_text(encoding="utf-8")
    assert "quote_us_view.qml" not in testo
    assert "label_us_view(" not in testo and "label_quote_view(" not in testo
    for m in re.finditer(r"^(\s*)(\w+)\.apply_style_to_layer\((\w+)", testo, re.M):
        prima = testo[:m.start()].split("\n")[-2:]
        assert any("self._stile_salvato(%s)" % m.group(3) in r for r in prima), m.group(0)
    righe = testo.split("\n")
    for i, r in enumerate(righe):
        if "self._stile_vista(" in r and "fallback=True" in r:
            var = re.search(r"_stile_vista\((\w+),", r).group(1)
            dopo = "\n".join(x for x in righe[i + 1:i + 16] if not x.strip().startswith("#"))
            assert "%s.loadNamedStyle(style_path)" % var not in dopo or "us_view.qml" not in dopo, (i + 1, r.strip())


def test_i_metodi_dello_stile_esistono():
    albero = ast.parse(SRC.read_text(encoding="utf-8"))
    nomi = {n.name for n in ast.walk(albero) if isinstance(n, ast.FunctionDef)}
    assert {"_stile_vista", "_stile_salvato", "_engine_stili", "_sito_corrente"} <= nomi
