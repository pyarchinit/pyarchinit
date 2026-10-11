"""Le etichette della pianta non si coprono più fra loro.

Chiesto da Enzo l'11 ottobre 2026: «si sovrappongono e forse sono anche
troppo grandi, devi usare delle linee per non farle sovrapporre come abbiamo
fatto in Time Manager».

Il guasto era `displayAll = True` con `OverPoint`: il primo forza il disegno
di ogni etichetta qualunque cosa succeda, il secondo le incolla al centro
del poligono — così QGIS non prova nemmeno a spostarle e la US 1, la 4 e la
2 finivano una sull'altra. La ricetta buona è quella dell'atlante del Time
Manager, e si prende da là: posizioni alternative intorno al centro, linea
di richiamo, e `PreventOverlap` con `AllowDegradedPlacement` — spostarsi è
meglio che sparire.

Needs the QGIS python (qgis.core); skipped elsewhere.
"""
from __future__ import annotations

import os

import pytest

pytest.importorskip("qgis.core")

from qgis.core import (QgsApplication, QgsPalLayerSettings,  # noqa: E402
                       QgsVectorLayer)

from modules.utility.matrix_preview import LABEL_FIELDS, LABEL_KEY  # noqa: E402
from modules.utility import matrix_preview_png as MP  # noqa: E402


@pytest.fixture(scope="module")
def qgs():
    app = QgsApplication.instance()
    if app is None:
        QgsApplication.setPrefixPath(
            os.environ.get("QGIS_PREFIX_PATH",
                           "/Applications/QGIS.app/Contents/MacOS"), True)
        app = QgsApplication([], False)
        app.initQgis()
    return app


def _layer(etichette):
    """Un layer di memoria con i campi che l'etichetta legge."""
    campi = "&".join("field=%s:%s" % (c, "integer" if c in
                                      (LABEL_KEY, "stratigraph_index_us")
                                      else "string")
                     for c in (LABEL_KEY,) + LABEL_FIELDS)
    layer = QgsVectorLayer("Polygon?crs=EPSG:32633&" + campi, "us", "memory")
    assert layer.isValid(), layer.fields().names()
    return layer


@pytest.fixture(scope="module")
def etichette(qgs):
    """Le impostazioni, **e** il layer che le possiede.

    Il layer va tenuto in vita: `QgsPalLayerSettings` restituito da
    `labeling().settings()` punta a roba che vive dentro il layer, e se il
    layer viene raccolto dal garbage collector il primo accesso al formato
    segfaulta il processo. Tenerlo in una fixture di modulo è il modo
    semplice di dirlo.
    """
    layer = _layer(qgs)
    MP._stile_etichette_us(layer)
    etichettatura = layer.labeling()
    assert etichettatura is not None, "l'etichettatura deve essere impostata"
    return layer, etichettatura.settings()


def _impostazioni(coppia):
    return coppia[1]


def test_l_etichetta_si_puo_spostare_invece_di_coprire(etichette):
    """Posizioni alternative intorno al centro, non una sola.

    Con `OverPoint` QGIS ha un posto solo: o ci sta o copre (o sparisce).
    """
    imp = _impostazioni(etichette)
    assert imp.placement == \
        QgsPalLayerSettings.Placement.OrderedPositionsAroundPoint


def test_una_linea_di_richiamo_dice_a_chi_appartiene(etichette):
    """Spostata l'etichetta, serve dire di quale unità è."""
    imp = _impostazioni(etichette)
    richiamo = imp.callout()
    assert richiamo is not None, "senza richiamo l'etichetta spostata è muta"
    assert richiamo.enabled() is True


def test_le_etichette_non_si_coprono_e_non_sparicono(etichette):
    """`PreventOverlap` perché non si coprano, `AllowDegradedPlacement`
    perché un numero in una posizione meno buona è meglio di un numero che
    non c'è."""
    from qgis.core import Qgis
    imp = _impostazioni(etichette)
    posiz = imp.placementSettings()
    assert posiz.overlapHandling() == Qgis.LabelOverlapHandling.PreventOverlap
    assert posiz.allowDegradedPlacement() is True


def test_display_all_non_e_forzato(etichette):
    """Era lui il guasto: con `displayAll` attivo QGIS disegna tutto dove
    capita e non sposta niente."""
    imp = _impostazioni(etichette)
    assert imp.displayAll is False


def test_l_etichetta_e_un_ostacolo_per_le_altre(etichette):
    imp = _impostazioni(etichette)
    assert imp.obstacleSettings().isObstacle() is True


def test_il_numero_resta_cerchiato(etichette):
    """Il cerchio bianco l'aveva chiesto lui il 10 ottobre e resta."""
    from qgis.core import QgsTextBackgroundSettings
    imp = _impostazioni(etichette)
    # Il formato in una variabile, non in catena: `imp.format()` torna un
    # temporaneo, e `.background()` su quello punta a memoria già liberata
    # — il processo segfaulta, non fallisce.
    formato = imp.format()
    sfondo = formato.background()
    assert sfondo.enabled() is True
    assert sfondo.type() == QgsTextBackgroundSettings.ShapeCircle


def test_il_corpo_del_numero_si_e_rimpicciolito(etichette):
    """«ancora troppo grandi»: 34 px, poi 22, ora 13.

    Il cerchio copriva il disegno — nell'anteprima del sito di esempio
    stava sopra la muratura della US 5 — e a 13 px con quattro di margine
    sta accanto alle pietre invece che sopra."""
    assert MP.ETICHETTA_PX == 13
    imp = _impostazioni(etichette)
    formato = imp.format()
    assert formato.size() == MP.ETICHETTA_PX
