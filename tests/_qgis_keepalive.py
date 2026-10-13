"""Una sola applicazione QGIS per tutta la sessione di test, tenuta viva.

Le fixture `qgs` dei singoli moduli creano `QgsApplication` e la lasciano
al garbage collector a fine modulo: l'applicazione muore, il modulo
successivo ne crea un'altra, e gli oggetti statici di QGIS rimasti della
prima — `QgsStyle.defaultStyle()` per primo — puntano nel vuoto (segfault
nella finestra «Stili delle viste», 13 ottobre 2026). Qui l'applicazione
nasce una volta sola, prima di tutto, e resta per tutto il processo.

I `conftest.py` di `tests/`, `tests/sync/` e `tests/utility/` importano la
fixture: pytest carica solo i conftest dalla radice degli argomenti in
giù, e un lancio di soli file in `tests/sync` non vedrebbe `tests/conftest.py`.
"""
from __future__ import annotations

import os

# Le librerie numeriche a un thread, PRIMA che numpy carichi il BLAS (questo
# modulo è importato dai conftest, quindi prima della raccolta dei test): il
# kriging di GeoArchaeo risolve sistemi con `np.linalg.solve` dentro un
# QThread, e con Accelerate a più thread il processo crollava a tratti
# (segfault in `_krige_targets`, 13 ottobre 2026; 3 giri su 3 puliti a un
# thread). Per i test la velocità non conta, la stabilità sì.
for _var in ("VECLIB_MAXIMUM_THREADS", "OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_var, "1")

import pytest

_APP = None


@pytest.fixture(scope="session", autouse=True)
def qgis_application_keepalive():
    global _APP
    if os.environ.get("PYARCHINIT_NO_KEEPALIVE"):      # per isolare un guasto
        yield None
        return
    try:
        from qgis.core import QgsApplication
    except Exception:                               # noqa: BLE001
        yield None
        return
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QgsApplication.instance()
    if app is None:
        QgsApplication.setPrefixPath(
            os.environ.get("QGIS_PREFIX_PATH", "/Applications/QGIS.app/Contents/MacOS"), True)
        app = QgsApplication([], False)
        app.initQgis()
    _APP = app
    yield app
