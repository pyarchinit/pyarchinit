"""La vista US appena caricata porta il numero dell'unità in un cerchio
(13 ottobre 2026: «dovrebbe mettere le etichette delle US cerchiate»),
con la stessa ricetta delle tavole dell'atlante: una etichetta per unità,
sul disegno più grande che si vede. Serve il Python di QGIS."""
from __future__ import annotations

import ast
import os
import sys
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("qgis.core")

from qgis.core import (QgsApplication, QgsFeature, QgsGeometry,  # noqa: E402
                       QgsPalLayerSettings, QgsTextBackgroundSettings, QgsVectorLayer)

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from modules.utility.atlas_labels import label_us_view  # noqa: E402


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

FIELDS = "field=scavo_s:string&field=area_s:string&field=us_s:string&field=stratigraph_index_us:integer"


def _vista_us():
    layer = QgsVectorLayer("Polygon?crs=EPSG:32633&" + FIELDS, "US view", "memory")
    righe = [("Scavo", "1", "1", 2, "POLYGON((0 0, 10 0, 10 10, 0 10, 0 0))"),      # US 1, disegno grande
             ("Scavo", "1", "1", 1, "POLYGON((2 2, 4 2, 4 4, 2 4, 2 2))"),          # US 1, disegno piccolo
             ("Scavo", "1", "2", 2, "POLYGON((20 20, 30 20, 30 30, 20 30, 20 20))")]  # US 2
    feats = []
    for scavo, area, us, indice, wkt in righe:
        f = QgsFeature(layer.fields())
        f.setAttributes([scavo, area, us, indice])
        f.setGeometry(QgsGeometry.fromWkt(wkt))
        feats.append(f)
    layer.dataProvider().addFeatures(feats)
    layer.updateExtents()
    return layer


def test_la_vista_us_prende_il_numero_in_un_cerchio_una_volta_per_unita(qgs):
    layer = _vista_us()
    assert label_us_view(layer) is True
    assert layer.labelsEnabled()
    etichettatura = layer.labeling()                        # tenuto vivo: settings() punta dentro di lui
    impostazioni = etichettatura.settings()
    assert impostazioni.fieldName == "us_s"
    formato = impostazioni.format()
    sfondo = formato.background()
    assert sfondo.enabled() and sfondo.type() == QgsTextBackgroundSettings.ShapeType.ShapeCircle
    proprieta = impostazioni.dataDefinedProperties()
    mostra = proprieta.property(QgsPalLayerSettings.Property.Show)
    assert mostra.isActive() and mostra.expressionString().count("$id IN") == 1
    ids = [int(x) for x in mostra.expressionString().split("(")[1].rstrip(")").split(",")]
    assert len(ids) == 2                                    # una per unità, non una per disegno


def test_un_layer_che_non_e_la_vista_us_resta_senza_etichette(qgs):
    punti = QgsVectorLayer("Point?crs=EPSG:32633&" + FIELDS, "Quote", "memory")
    assert label_us_view(punti) is False and not punti.labelsEnabled()
    senza = QgsVectorLayer("Polygon?crs=EPSG:32633&field=gid:integer", "x", "memory")
    assert label_us_view(senza) is False and not senza.labelsEnabled()


def test_lo_stile_scelto_della_vista_us_porta_anche_le_etichette():
    """`USViewStyler.apply_style_to_layer` è il punto unico da cui passano
    le viste US e USM, su SQLite e su PostgreSQL: le etichette stanno lì."""
    albero = ast.parse((_ROOT / "modules" / "utility" / "create_style.py").read_text(encoding="utf-8"))
    for n in ast.walk(albero):
        if isinstance(n, ast.FunctionDef) and n.name == "apply_style_to_layer" and \
                any(a.arg == "choice" for a in n.args.args):
            chiamate = {c.func.attr if isinstance(c.func, ast.Attribute) else getattr(c.func, "id", "")
                        for c in ast.walk(n) if isinstance(c, ast.Call)}
            assert "label_us_view" in chiamate
            return
    raise AssertionError("USViewStyler.apply_style_to_layer")


def _mostra(layer) -> str:
    """L'espressione «quali disegni etichettare». Ogni oggetto di PyQGIS
    tenuto in una variabile: la catena di temporanei va in segfault."""
    etichettatura = layer.labeling()
    impostazioni = etichettatura.settings()
    proprieta = impostazioni.dataDefinedProperties()
    mostra = proprieta.property(QgsPalLayerSettings.Property.Show)
    return mostra.expressionString()


def test_le_etichette_di_prima_sopravvivono_alla_tavola_dell_atlante(qgs):
    """`setLabeling` distrugge l'etichettatura vecchia: chi se la tiene
    com'era (il Time Manager, per rimetterla a fine tavola) deve tenerne
    una copia, o rimette un puntatore morto — RuntimeError ingoiato, o
    segfault salvando il progetto (misurato il 13 ottobre 2026)."""
    from modules.utility.atlas_labels import remember_labeling, restore_labeling, us_labeling
    layer = _vista_us()
    assert label_us_view(layer)
    di_prima = _mostra(layer)
    ricordo = remember_labeling(layer)
    layer.setLabeling(us_labeling([f.name() for f in layer.fields()], None))   # la tavola: tutte etichettate
    layer.setLabelsEnabled(True)
    restore_labeling(layer, ricordo)
    assert layer.labelsEnabled()
    assert _mostra(layer) == di_prima
    nudo = QgsVectorLayer("Polygon?crs=EPSG:32633&" + FIELDS, "senza", "memory")
    ricordo = remember_labeling(nudo)
    nudo.setLabeling(us_labeling([f.name() for f in nudo.fields()], None))
    nudo.setLabelsEnabled(True)
    restore_labeling(nudo, ricordo)
    assert nudo.labeling() is None and not nudo.labelsEnabled()


def test_la_vista_delle_quote_prende_la_quota_sopra_il_simbolo(qgs):
    """«le etichette delle quote non compaiono» (13 ottobre 2026): la vista
    delle quote, appena caricata, porta il valore della quota con la
    ricetta delle tavole dell'atlante."""
    from modules.utility.atlas_labels import label_quote_view
    quote = QgsVectorLayer("Point?crs=EPSG:32633&field=sito_q:string&field=us_q:string&field=quota_q:double",
                           "Quote view", "memory")
    assert label_quote_view(quote) is True
    assert quote.labelsEnabled()
    etichettatura = quote.labeling()
    impostazioni = etichettatura.settings()
    assert "quota_q" in impostazioni.fieldName and impostazioni.isExpression
    poligoni = QgsVectorLayer("Polygon?crs=EPSG:32633&" + FIELDS, "US", "memory")
    assert label_quote_view(poligoni) is False and not poligoni.labelsEnabled()
    senza = QgsVectorLayer("Point?crs=EPSG:32633&field=gid:integer", "x", "memory")
    assert label_quote_view(senza) is False


def test_la_rinuncia_delle_etichette_dice_il_perche(qgs):
    from modules.utility.atlas_labels import label_us_view, why_not_us_view
    punti = QgsVectorLayer("Point?crs=EPSG:32633&" + FIELDS, "Quote", "memory")
    assert label_us_view(punti) is False
    assert "poligon" in why_not_us_view(punti).lower()
    senza = QgsVectorLayer("Polygon?crs=EPSG:32633&field=gid:integer", "x", "memory")
    assert "us" in why_not_us_view(senza).lower()
    assert why_not_us_view(_vista_us()) == ""
