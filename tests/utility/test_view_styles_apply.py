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


def _etichette_grandi(layer, size_mm=3.5, bold=True):
    """Un layer con il numero cerchiato e un carattere personalizzato."""
    from qgis.core import QgsVectorLayerSimpleLabeling
    assert label_us_view(layer)
    etichettatura = layer.labeling()
    impostazioni = etichettatura.settings()
    formato = impostazioni.format()
    formato.setSize(size_mm)
    carattere = formato.font()
    carattere.setBold(bold)
    formato.setFont(carattere)
    impostazioni.setFormat(formato)
    layer.setLabeling(QgsVectorLayerSimpleLabeling(impostazioni))


def test_il_carattere_salvato_sopravvive_all_applicazione(qgs, tmp_path):
    """Revisione (I1): `apply_recipe` rifaceva le etichette da zero e il
    carattere salvato — corpo, grassetto — spariva al caricamento e in
    «Applica ai layer caricati»."""
    origine = _poligoni([("1", "POLYGON((0 0, 10 0, 10 10, 0 10, 0 0))"), ("2", "POLYGON((20 20, 30 20, 30 30, 20 30, 20 20))")])
    _etichette_grandi(origine)
    engine = create_engine("sqlite:///%s" % (tmp_path / "stili.sqlite"))
    store.ensure_table(engine)
    stile = SavedStyle(None, "pyarchinit_us_view", None, "Grande", va.export_qml_text(origine),
                       LabelRecipe(enabled=True, preset="us_circle", one_per_unit=True), is_default=True)
    store.save_style(engine, stile)
    fresco = _poligoni([("1", "POLYGON((0 0, 10 0, 10 10, 0 10, 0 0))"),
                        ("1", "POLYGON((2 2, 4 2, 4 4, 2 4, 2 2))"),
                        ("2", "POLYGON((20 20, 30 20, 30 30, 20 30, 20 20))")])
    assert va.apply_view_style(fresco, "pyarchinit_us_view", engine=engine).startswith("saved:")
    etichettatura = fresco.labeling()
    impostazioni = etichettatura.settings()
    formato = impostazioni.format()
    assert abs(formato.size() - 3.5) < 0.01 and formato.font().bold()        # il carattere salvato
    assert formato.background().enabled()                                    # il cerchio
    assert len(_mostra(fresco).split("(")[1].rstrip(")").split(",")) == 2     # una per unità, ricalcolata


def test_uno_stile_con_etichette_e_ricetta_spenta_le_tiene(qgs, tmp_path):
    """Revisione (I2): un QML importato con le etichette accese e la
    ricetta `none` si caricava con le etichette spente."""
    origine = _poligoni([("1", "POLYGON((0 0, 10 0, 10 10, 0 10, 0 0))")], "Strutture")
    assert label_us_view(origine)
    engine = create_engine("sqlite:///%s" % (tmp_path / "stili.sqlite"))
    store.ensure_table(engine)
    store.save_style(engine, SavedStyle(None, "pyarchinit_strutture_view", None, "Con etichette",
                                        va.export_qml_text(origine), LabelRecipe(), is_default=True))
    fresco = _poligoni([("1", "POLYGON((0 0, 10 0, 10 10, 0 10, 0 0))")], "Strutture")
    assert va.apply_view_style(fresco, "pyarchinit_strutture_view", engine=engine).startswith("saved:")
    assert fresco.labelsEnabled()
    ricetta = va.recipe_from_layer(fresco)
    assert ricetta.enabled and ricetta.preset == "us_circle" and ricetta.one_per_unit
    spento = _poligoni([("1", "POLYGON((0 0, 10 0, 10 10, 0 10, 0 0))")])
    assert va.recipe_from_layer(spento) == LabelRecipe()


def test_il_qml_porta_solo_stile_etichette_e_resa(qgs):
    """Revisione (M5): esportare tutte le categorie spazzava le proprietà
    personalizzate e la configurazione dei campi del layer di arrivo."""
    a = _poligoni([("1", "POLYGON((0 0, 10 0, 10 10, 0 10, 0 0))")])
    testo = va.export_qml_text(a)
    b = _poligoni([("2", "POLYGON((0 0, 10 0, 10 10, 0 10, 0 0))")])
    b.setCustomProperty("pyarchinit/qualcosa", "resta")
    assert va.import_qml_text(b, testo)
    assert b.customProperty("pyarchinit/qualcosa") == "resta"


def test_il_qml_fornito_che_non_si_carica_non_finge(qgs, monkeypatch):
    """Revisione (M1): `loadNamedStyle` che fallisce tornava comunque «shipped»."""
    from modules.utility import view_styles as vs
    quote = QgsVectorLayer("Point?crs=EPSG:32633&field=sito_q:string&field=us_q:string&field=quota_q:double",
                           "Quote", "memory")
    monkeypatch.setattr(va, "shipped_qml", lambda spec: "/percorso/che/non/esiste.qml")
    assert va.apply_view_style(quote, "pyarchinit_quote_view") == "none"


ORDER_FIELDS = (US_FIELDS + "&field=order_layer:integer&field=periodo_iniziale:string"
                "&field=fase_iniziale:string&field=cont_per:string")


def _poligoni_ordinati(nome="US"):
    layer = QgsVectorLayer("Polygon?crs=EPSG:32633&" + ORDER_FIELDS, nome, "memory")
    layer.dataProvider().addAttributes([])
    prov = layer.dataProvider()
    for k, (us, ordine) in enumerate((("1", 2), ("2", 1), ("3", 0))):
        f = QgsFeature(layer.fields())
        f.setGeometry(QgsGeometry.fromWkt("POLYGON((%d 0, %d 0, %d 1, %d 1, %d 0))" % (k, k + 1, k + 1, k, k)))
        f.setAttributes(["Scavo", "1", us, 1, "Scavo", "Strato", ordine, "", "", ""])
        prov.addFeature(f)
    layer.updateExtents()
    return layer


def test_le_viste_di_unita_si_disegnano_dal_piu_antico_al_piu_recente(qgs, tmp_path):
    """Enzo, 13 ottobre 2026: «l'ordine di visualizzazione dei poligoni deve
    seguire sempre dal più recente al più antico, in modo che quando spengo i
    checkbox visualizzo quello sottostante». Il ripiego, uno stile salvato
    e un QML importato lasciano tutti l'ordine come il Time Manager:
    order_layer crescente (0 = più antica, disegnata per prima, sotto)."""
    from sqlalchemy import create_engine
    from modules.utility import view_styles_store as store
    from modules.utility.view_styles import SavedStyle, LabelRecipe
    layer = _poligoni_ordinati()
    assert va.apply_view_style(layer, "pyarchinit_us_view", None, engine=None, fallback=True) == "shipped"
    r = layer.renderer()
    assert r.orderByEnabled() and "order_layer" in r.orderBy().dump()
    # uno stile salvato senza ordine nel QML: l'ordine c'è lo stesso
    engine = create_engine("sqlite:///%s" % (tmp_path / "stili.sqlite"))
    store.ensure_table(engine)
    senza = _poligoni_ordinati("senza")
    stile = SavedStyle(None, "pyarchinit_us_view", None, "piatto", va.export_qml_text(senza), LabelRecipe(), True)
    store.save_style(engine, stile)
    store.set_default(engine, stile.id)
    altro = _poligoni_ordinati("altro")
    assert va.apply_view_style(altro, "pyarchinit_us_view", None, engine=engine).startswith("saved:")
    assert altro.renderer().orderByEnabled() and "order_layer" in altro.renderer().orderBy().dump()
    # le quote hanno order_layer anche loro (viste vere) ma sono punti, non unità: nessun ordine
    quote = QgsVectorLayer("Point?crs=EPSG:32633&field=sito_q:string&field=us_q:string&field=quota_q:double"
                           "&field=order_layer:integer", "Quote", "memory")
    va.apply_view_style(quote, "pyarchinit_quote_view", None, engine=None, fallback=True)
    assert not quote.renderer().orderByEnabled()


def test_la_simbologia_nidificata_e_lo_styler_del_thesaurus_tengono_l_ordine(qgs):
    """Dove il renderer si rifà da capo dopo il ripiego — la simbologia
    nidificata (Map preview su SQLite, schede Deteta/Detsesso, caricatori
    dalla matrice) e lo styler del thesaurus (Map preview su PostgreSQL) —
    l'ordine stratigrafico va rimesso (dubbio 4 dell'agente dei tutorial)."""
    import types
    from modules.gis.pyarchinit_pyqgis import Pyarchinit_pyqgis
    from modules.utility.create_style import ThesaurusStyler
    layer = _poligoni_ordinati("nidificata")
    stub = types.SimpleNamespace(_engine_stili=lambda: None)
    assert Pyarchinit_pyqgis.create_us_nested_symbology(stub, layer, None) is True
    assert layer.renderer().orderByEnabled() and "order_layer" in layer.renderer().orderBy().dump()
    altro = _poligoni_ordinati("thesaurus")
    ThesaurusStyler("/nessun/posto.qml").apply_style_to_layer(altro, "tipo_us_s", {"Strato": "S"})
    assert altro.renderer().type() == "categorizedSymbol"
    assert altro.renderer().orderByEnabled() and "order_layer" in altro.renderer().orderBy().dump()
