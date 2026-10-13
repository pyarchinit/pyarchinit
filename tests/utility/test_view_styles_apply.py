"""Applicare uno stile a un layer: QML dentro e fuori, la ricetta delle
etichette ricalcolata, la scelta del predefinito (Task 3 degli Stili delle
viste). Serve il Python di QGIS."""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("qgis.core")

from qgis.core import (QgsApplication, QgsCategorizedSymbolRenderer, QgsFeature, QgsFillSymbol,  # noqa: E402
                       QgsGeometry, QgsPalLayerSettings, QgsRendererCategory, QgsSingleSymbolRenderer,
                       QgsVectorLayer)
from sqlalchemy import create_engine  # noqa: E402

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from modules.utility import view_styles_apply as va  # noqa: E402
from modules.utility import view_styles_store as store  # noqa: E402
from modules.utility.atlas_labels import label_us_view  # noqa: E402
from modules.utility.view_styles import LabelRecipe, SavedStyle  # noqa: E402


@pytest.fixture(scope="module")
def qgs():
    app = QgsApplication.instance()
    if app is None:
        QgsApplication.setPrefixPath(
            os.environ.get("QGIS_PREFIX_PATH", "/Applications/QGIS.app/Contents/MacOS"), True)
        app = QgsApplication([], False)
        app.initQgis()
    return app


US_FIELDS = "field=scavo_s:string&field=area_s:string&field=us_s:string&field=stratigraph_index_us:integer&field=sito:string&field=tipo_us_s:string"


def _poligoni(righe, nome="US"):
    layer = QgsVectorLayer("Polygon?crs=EPSG:32633&" + US_FIELDS, nome, "memory")
    feats = []
    for us, wkt in righe:
        f = QgsFeature(layer.fields())
        f.setAttributes(["Scavo", "1", us, 2, "Scavo", "positiva"])
        f.setGeometry(QgsGeometry.fromWkt(wkt))
        feats.append(f)
    layer.dataProvider().addFeatures(feats)
    layer.updateExtents()
    return layer


def _mostra(layer):
    etichettatura = layer.labeling()
    impostazioni = etichettatura.settings()
    proprieta = impostazioni.dataDefinedProperties()
    return proprieta.property(QgsPalLayerSettings.Property.Show).expressionString()


def test_il_qml_fa_il_giro_con_categorie_ed_etichette(qgs):
    a = _poligoni([("1", "POLYGON((0 0, 10 0, 10 10, 0 10, 0 0))"), ("2", "POLYGON((20 20, 30 20, 30 30, 20 30, 20 20))")])
    cats = [QgsRendererCategory(v, QgsFillSymbol.createSimple({"color": c}), v)
            for v, c in (("1", "255,0,0,255"), ("2", "0,0,255,255"))]
    a.setRenderer(QgsCategorizedSymbolRenderer("us_s", cats))
    assert label_us_view(a)
    testo = va.export_qml_text(a)
    assert "<labeling" in testo and "categorizedSymbol" in testo
    b = _poligoni([("1", "POLYGON((0 0, 10 0, 10 10, 0 10, 0 0))")])
    assert va.import_qml_text(b, testo) is True
    assert b.renderer().type() == "categorizedSymbol" and b.labelsEnabled()
    assert va.import_qml_text(b, "questo non è xml") is False


def test_una_per_unita_si_ricalcola_e_non_si_fida_del_qml(qgs):
    uno = _poligoni([("1", "POLYGON((0 0, 10 0, 10 10, 0 10, 0 0))")])
    assert label_us_view(uno)
    testo = va.export_qml_text(uno)                                        # porta «$id IN (1)»
    tre = _poligoni([("1", "POLYGON((0 0, 10 0, 10 10, 0 10, 0 0))"),
                     ("1", "POLYGON((2 2, 4 2, 4 4, 2 4, 2 2))"),
                     ("2", "POLYGON((20 20, 30 20, 30 30, 20 30, 20 20))")])
    assert va.import_qml_text(tre, testo)
    assert _mostra(tre).count(",") == 0                                    # stantio: un id solo
    assert va.apply_recipe(tre, LabelRecipe(enabled=True, preset="us_circle", one_per_unit=True))
    ids = _mostra(tre).split("(")[1].rstrip(")").split(",")
    assert len(ids) == 2                                                   # una per unità, ricalcolata
    assert va.apply_recipe(tre, LabelRecipe(enabled=True, preset="us_circle", one_per_unit=False))
    assert "$id IN" not in _mostra(tre)                                    # tutti i disegni
    assert va.apply_recipe(tre, LabelRecipe())                             # spenta
    assert not tre.labelsEnabled()


def test_senza_motore_la_vista_delle_quote_prende_il_qml_fornito_e_la_quota(qgs):
    quote = QgsVectorLayer("Point?crs=EPSG:32633&field=sito_q:string&field=us_q:string&field=quota_q:double",
                           "Quote", "memory")
    assert va.apply_view_style(quote, "pyarchinit_quote_view") == "shipped"
    assert quote.labelsEnabled()
    etichettatura = quote.labeling()
    assert "quota_q" in etichettatura.settings().fieldName
    assert quote.renderer() is not None


def test_una_vista_senza_qml_e_senza_stile_non_tocca_niente(qgs):
    tomba = _poligoni([("1", "POLYGON((0 0, 10 0, 10 10, 0 10, 0 0))")], "Tomba")
    assert label_us_view(tomba)                                            # etichette già sue
    assert va.apply_view_style(tomba, "pyarchinit_tomba_view", "Scavo") == "none"
    assert tomba.labelsEnabled()
    assert va.apply_view_style(tomba, "vista_che_non_esiste") == "none"


def test_lo_stile_salvato_predefinito_vince_e_il_sito_batte_tutti(qgs, tmp_path):
    engine = create_engine("sqlite:///%s" % (tmp_path / "stili.sqlite"))
    store.ensure_table(engine)
    rosso = _poligoni([("1", "POLYGON((0 0, 10 0, 10 10, 0 10, 0 0))")], "Strutture")
    rosso.setRenderer(QgsSingleSymbolRenderer(QgsFillSymbol.createSimple({"color": "255,0,0,255"})))
    blu = _poligoni([("1", "POLYGON((0 0, 10 0, 10 10, 0 10, 0 0))")], "Strutture")
    blu.setRenderer(QgsSingleSymbolRenderer(QgsFillSymbol.createSimple({"color": "0,0,255,255"})))
    tutti = SavedStyle(None, "pyarchinit_strutture_view", None, "Rosso per tutti", va.export_qml_text(rosso),
                       LabelRecipe(enabled=True, preset="field", expression='"sito"'), is_default=True)
    scavo = SavedStyle(None, "pyarchinit_strutture_view", "Scavo", "Blu dello scavo", va.export_qml_text(blu),
                       LabelRecipe(), is_default=True)
    store.save_style(engine, tutti)
    store.save_style(engine, scavo)
    bersaglio = _poligoni([("1", "POLYGON((0 0, 10 0, 10 10, 0 10, 0 0))")], "Strutture")
    assert va.apply_view_style(bersaglio, "pyarchinit_strutture_view", "Altro", engine=engine) == "saved:%d" % tutti.id
    assert bersaglio.renderer().symbol().color().red() == 255 and bersaglio.labelsEnabled()
    etichettatura = bersaglio.labeling()
    assert "sito" in etichettatura.settings().fieldName
    assert va.apply_view_style(bersaglio, "pyarchinit_strutture_view", "Scavo", engine=engine) == "saved:%d" % scavo.id
    assert bersaglio.renderer().symbol().color().blue() == 255 and not bersaglio.labelsEnabled()
    rotto = create_engine("sqlite:////percorso/che/non/esiste/x.sqlite")
    assert va.apply_view_style(bersaglio, "pyarchinit_strutture_view", "Scavo", engine=rotto) == "none"


def test_il_qml_fornito_si_trova_per_nome(qgs):
    from modules.utility.view_styles import view_by_name
    assert va.shipped_qml(view_by_name("pyarchinit_us_view")).endswith("us_view.qml")
    assert va.shipped_qml(view_by_name("pyarchinit_tomba_view")) is None


def test_senza_ripiego_si_applica_solo_uno_stile_salvato(qgs):
    """I caricatori secondari (matrice, documentazione) caricano la vista
    nuda: con ``fallback=False`` si applica solo un predefinito salvato."""
    quote = QgsVectorLayer("Point?crs=EPSG:32633&field=sito_q:string&field=us_q:string&field=quota_q:double",
                           "Quote", "memory")
    assert va.apply_view_style(quote, "pyarchinit_quote_view", fallback=False) == "none"
    assert not quote.labelsEnabled()
