"""I caricatori di `pyarchinit_pyqgis.py` passano tutti da `_stile_vista`
(Task 4 degli Stili delle viste): per ogni vista del registro, su SQLite e
su PostgreSQL, subito dopo la creazione del layer; i QML forniti e le
etichette non si applicano più a mano."""
from __future__ import annotations

import ast
import re
import sys

import pytest
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


LEGACY = ("stile_quote.qml", "quote_view.qml", "us_caratterizzazioni.qml")


def test_nessun_qml_legacy_sovrascrive_lo_stile_risolto():
    """Dopo `_stile_vista` un `loadNamedStyle` dello stesso layer può esserci
    solo sotto `if not self._stile_salvato(var)`, e mai con un QML legacy
    dopo un ripiego (`fallback=True`): un QML senza `<labeling>` caricato
    dopo cancella il predefinito salvato e le etichette (trovato leggendo i
    caricatori PostgreSQL, 13 ottobre 2026)."""
    righe = _righe()
    for i, r in enumerate(righe):
        if "self._stile_vista(" not in r or r.strip().startswith("#"):
            continue
        var = re.search(r"_stile_vista\((\w+),", r).group(1)
        ripiego = "fallback=True" in r
        for j in range(i + 1, min(i + 16, len(righe))):
            x = righe[j]
            if "self._stile_vista(" in x or re.match(r"^\s*def ", x):
                break
            if x.strip().startswith("#"):
                continue
            if "%s.loadNamedStyle(" % var in x or "create_us_nested_symbology(%s" % var in x:
                blocco = "\n".join(righe[i + 1:j + 1])
                assert not (ripiego and any(q in blocco for q in LEGACY)), (j + 1, x.strip())
                prima = [y for y in righe[i + 1:j] if y.strip() and not y.strip().startswith("#")]
                assert any("self._stile_salvato(%s)" % var in y for y in prima), (j + 1, x.strip())


def _percorso(istruzioni, chiamata):
    """[(blocco, indice, istruzione)] dal corpo della funzione fino
    all'istruzione che contiene la chiamata, seguendo solo il ramo preso."""
    for i, st in enumerate(istruzioni):
        if not any(n is chiamata for n in ast.walk(st)):
            continue
        sotto = []
        blocchi = [getattr(st, c) for c in ("body", "orelse", "finalbody")
                   if isinstance(getattr(st, c, None), list)]
        if isinstance(st, ast.Try):
            blocchi += [h.body for h in st.handlers]
        for blocco in blocchi:
            if blocco and isinstance(blocco[0], ast.stmt):
                sotto = _percorso(blocco, chiamata)
                if sotto:
                    break
        return [(istruzioni, i, st)] + sotto
    return []


def _bersagli(nodo):
    """I nomi che un'istruzione lega, senza entrare nei rami che
    potrebbero non essere eseguiti (if, for, while)."""
    nomi = set()
    for n in ast.walk(nodo):
        if isinstance(n, (ast.If, ast.For, ast.While)) and n is not nodo:
            continue
        if isinstance(n, ast.Assign):
            for t in n.targets:
                nomi |= {x.id for x in ast.walk(t) if isinstance(x, ast.Name)}
        elif isinstance(n, (ast.AugAssign, ast.AnnAssign, ast.NamedExpr)):
            nomi |= {x.id for x in ast.walk(n.target) if isinstance(x, ast.Name)}
        elif isinstance(n, ast.withitem) and n.optional_vars is not None:
            nomi |= {x.id for x in ast.walk(n.optional_vars) if isinstance(x, ast.Name)}
        elif isinstance(n, ast.ExceptHandler) and n.name:
            nomi.add(n.name)
    return nomi


def _legati_prima(fn, chiamata):
    """Parametri più i nomi legati dalle istruzioni che precedono la
    chiamata lungo il suo percorso (un `if` fratello non conta: il ramo
    preso potrebbe essere l'altro, come in loadMapPreview_new)."""
    nomi = {a.arg for a in fn.args.args + fn.args.kwonlyargs}
    for blocco, i, st in _percorso(fn.body, chiamata):
        for prima in blocco[:i]:
            if isinstance(prima, (ast.If, ast.For, ast.While)):
                continue                                  # ramo non garantito
            nomi |= _bersagli(prima)
        if isinstance(st, ast.For):
            nomi |= {x.id for x in ast.walk(st.target) if isinstance(x, ast.Name)}
        elif isinstance(st, ast.With):
            for it in st.items:
                if it.optional_vars is not None:
                    nomi |= {x.id for x in ast.walk(it.optional_vars) if isinstance(x, ast.Name)}
        elif isinstance(st, ast.Try):
            nomi |= {h.name for h in st.handlers if h.name}
    return nomi


def test_il_sito_passato_a_stile_vista_e_legato_prima_della_chiamata():
    """`UnboundLocalError: sito_filter` in `loadMapPreview_new` (Enzo,
    13 ottobre 2026): un nome di sito passato a `_stile_vista` deve essere
    un parametro o un nome legato prima, lungo il ramo che porta alla
    chiamata, nella stessa funzione."""
    albero = ast.parse(SRC.read_text(encoding="utf-8"))
    errori = []
    for fn in ast.walk(albero):
        if not isinstance(fn, ast.FunctionDef):
            continue
        for nodo in ast.walk(fn):
            if not (isinstance(nodo, ast.Call) and isinstance(nodo.func, ast.Attribute)
                    and nodo.func.attr == "_stile_vista" and len(nodo.args) >= 3):
                continue
            sito = nodo.args[2]
            if isinstance(sito, ast.Name) and sito.id not in _legati_prima(fn, nodo):
                errori.append((nodo.lineno, fn.name, sito.id))
    assert not errori, errori


def test_i_layer_delle_viste_non_ereditano_stili_ne_etichette():
    """Enzo, 13 ottobre 2026: etichette «0,00 ha» su tutti i poligoni della
    Map preview e della vista US, che nessun codice del plugin produce: i
    layer delle viste nascono senza lo stile predefinito di QGIS
    (`loadDefaultStyle=False`), `_stile_vista` azzera le etichette prima di
    risolvere lo stile, i layer di sfondo della preview le hanno spente e il
    canvas della preview non disegna le annotazioni del progetto."""
    testo = SRC.read_text(encoding="utf-8")
    assert re.search(r"QgsVectorLayer\(ogr_uri, '', 'ogr',\s*QgsVectorLayer\.LayerOptions\(loadDefaultStyle=False\)\)", testo)
    righe = _righe()
    for i, r in enumerate(righe):
        if re.match(r"^\s*layerUS_us = ", r):
            dopo = "\n".join(righe[i + 1:i + 45])
            assert ("self._senza_etichette(layerUS_us)" in dopo or "layerUS_us.setLabelsEnabled(False)" in dopo
                    or "layerUS_us.loadNamedStyle(style_path_us)" in dopo), (i + 1, r.strip())
    scheda = (_ROOT / "tabs" / "US_USM.py").read_text(encoding="utf-8")
    assert "self.mapPreview.setAnnotationsVisible(False)" in scheda


def test_stile_vista_azzera_le_etichette_ereditate(tmp_path):
    """Un layer che arriva già etichettato (stile predefinito di QGIS, o
    chissà cosa) perde quelle etichette: decide `apply_view_style`."""
    import os, types
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    pytest.importorskip("qgis.core")
    from qgis.core import QgsApplication, QgsVectorLayer, QgsPalLayerSettings, QgsVectorLayerSimpleLabeling
    if QgsApplication.instance() is None:
        QgsApplication.setPrefixPath(os.environ.get("QGIS_PREFIX_PATH", "/Applications/QGIS.app/Contents/MacOS"), True)
        app = QgsApplication([], False); app.initQgis()
    from modules.gis.pyarchinit_pyqgis import Pyarchinit_pyqgis
    layer = QgsVectorLayer("Polygon?crs=EPSG:32633&field=sito:string&field=tipologia_struttura:string", "strutture", "memory")
    imp = QgsPalLayerSettings(); imp.fieldName = "format_number($area / 10000, 2) || ' ha'"; imp.isExpression = True
    layer.setLabeling(QgsVectorLayerSimpleLabeling(imp)); layer.setLabelsEnabled(True)
    stub = types.SimpleNamespace(_engine_stili=lambda: None)
    assert Pyarchinit_pyqgis._stile_vista(stub, layer, "pyarchinit_strutture_view", None, fallback=False) == "none"
    assert not layer.labelsEnabled() and layer.labeling() is None


def test_l_avviso_sulle_etichette_in_ettari_sta_in_tutti_i_caricatori_delle_unita():
    """L'audit delle etichette in ettari (13 ottobre 2026) parte da ogni
    caricatore delle viste delle unità: scheda US/USM, Map preview e i
    tre per periodo."""
    albero = ast.parse(SRC.read_text(encoding="utf-8"))
    attesi = {"charge_vector_layers", "charge_usm_layers", "loadMapPreview_new",
              "charge_vector_layers_periodo", "charge_vector_layers_all_period", "charge_vector_layers_usm_all_period"}
    trovati = set()
    for fn in ast.walk(albero):
        if isinstance(fn, ast.FunctionDef) and fn.name in attesi:
            for nodo in ast.walk(fn):
                if (isinstance(nodo, ast.Call) and isinstance(nodo.func, ast.Attribute)
                        and nodo.func.attr == "_avvisa_etichette_ettari"):
                    trovati.add(fn.name)
    assert trovati == attesi, attesi - trovati
