"""US/USM styles: existing QML as template, cont_per, drawing order (2026-09-11).

- "Carica stile esistente" only looked for styles saved in the database and,
  finding none, fell back to the categorisation window: now an existing
  style (database, pyArchInit QML or any .qml file) is the template of the
  categories built on the chosen field, keeping its colours for the values
  it already has.
- cont_per (period/phase) is a fourth categorisation field.
- The drawing order was never applied (setOrderBy was called on the layer,
  where it does not exist, and the error was swallowed): now it is set on
  the renderer, like the Time Manager — undated first, then periods by
  chronology, then order_layer, then stratigraph_index_us.

Needs the QGIS python (qgis.core); skipped elsewhere.
"""
from __future__ import annotations

import os
import sqlite3
import sys
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("qgis.core")

from qgis.core import (QgsApplication, QgsCategorizedSymbolRenderer, QgsFeature,  # noqa: E402
                       QgsFeatureRequest, QgsFillSymbol, QgsGeometry, QgsRendererCategory,
                       QgsSingleSymbolRenderer, QgsVectorLayer)

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
if (_ROOT / "ext_libs").is_dir() and str(_ROOT / "ext_libs") not in sys.path:
    sys.path.append(str(_ROOT / "ext_libs"))          # sqlalchemy, if QGIS has none

from modules.utility import create_style as cs  # noqa: E402

FIELDS = ("field=sito:string&field=us_s:string&field=d_stratigrafica:string&field=tipo_us_s:string"
          "&field=d_interpretativa:string&field=stratigraph_index_us:integer&field=order_layer:integer"
          "&field=periodo_iniziale:string&field=fase_iniziale:string&field=cont_per:string")
# us_s, d_stratigrafica, tipo_us_s, stratigraph_index_us, order_layer, periodo, fase, cont_per
FEATURES = [
    ("A", "Strato", "positiva", 1, 5, "1", "2", "2"),     # 1600: most recent
    ("B", "Taglio", "negativa", 1, 1, "2", "1", "3"),     # 1550, order 1
    ("C", "Strato", "positiva", 1, 3, "2", "1", "3"),     # 1550, order 3
    ("D", "Crollo", "positiva", 1, 0, None, None, None),  # undated
]


@pytest.fixture(scope="module")
def qgs():
    app = QgsApplication.instance()
    if app is None:
        QgsApplication.setPrefixPath(os.environ.get("QGIS_PREFIX_PATH", "/Applications/QGIS.app/Contents/MacOS"), True)
        app = QgsApplication([], False)
        app.initQgis()
    return app


class _Conn:
    def __init__(self, path):
        self.path = path

    def conn_str(self):
        return "sqlite:///" + self.path


def _db(tmp_path):
    path = str(tmp_path / "scavo.sqlite")
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE us_table (sito TEXT, d_stratigrafica TEXT, unita_tipo TEXT, "
                "order_layer INTEGER, d_interpretativa TEXT)")
    con.execute("CREATE TABLE periodizzazione_table (sito TEXT, periodo INTEGER, fase REAL, cron_iniziale INTEGER, "
                "cron_finale INTEGER, cont_per INTEGER, datazione_estesa TEXT)")
    con.executemany("INSERT INTO periodizzazione_table VALUES (?, ?, ?, ?, ?, ?, ?)",
                    [("S", 1, 1, 1800, 2022, 1, "Eta contemporanea"), ("S", 1, 2, 1600, 1799, 2, "Eta moderna"),
                     ("S", 2, 1, 1550, 1599, 3, "Tardo XVI secolo")])
    con.commit()
    con.close()
    return path


def _layer():
    layer = QgsVectorLayer("Polygon?crs=EPSG:32633&" + FIELDS, "us", "memory")
    features = []
    for i, (us, ds, tipo, idx, order, per, fase, cp) in enumerate(FEATURES):
        f = QgsFeature(layer.fields())
        f.setAttributes(["S", us, ds, tipo, "", idx, order, per, fase, cp])
        x = 10 * i
        f.setGeometry(QgsGeometry.fromWkt(f"POLYGON(({x} 0, {x + 5} 0, {x + 5} 5, {x} 5, {x} 0))"))
        features.append(f)
    layer.dataProvider().addFeatures(features)
    layer.updateExtents()
    return layer


def _styler(tmp_path, monkeypatch, choice, field, template=None):
    styler = cs.USViewStyler(_Conn(_db(tmp_path)), sito="S")
    asked = {"style": 0, "field": 0}

    def preference():
        asked["style"] += 1
        return choice

    def categorization(layer=None):
        asked["field"] += 1
        return field

    monkeypatch.setattr(styler, "ask_user_style_preference", preference)
    monkeypatch.setattr(styler, "ask_user_categorization_field", categorization)
    monkeypatch.setattr(styler, "choose_existing_style", lambda layer: template)
    return styler, asked


def _drawn(layer):
    renderer = layer.renderer()
    assert renderer.orderByEnabled()
    return [f["us_s"] for f in layer.getFeatures(QgsFeatureRequest().setOrderBy(renderer.orderBy()))]


def test_drawing_order_is_period_chronology_then_order_layer(qgs, tmp_path, monkeypatch):
    layer = _layer()
    styler, _ = _styler(tmp_path, monkeypatch, "temp", "d_stratigrafica")
    styler.apply_style_to_layer(layer)
    assert _drawn(layer) == ["D", "B", "C", "A"]   # undated underneath ... 1600 on top


def test_outline_only_is_ordered_too(qgs, tmp_path, monkeypatch):
    layer = _layer()
    styler, _ = _styler(tmp_path, monkeypatch, "null_fill", None)
    styler.apply_style_to_layer(layer)
    assert isinstance(layer.renderer(), QgsSingleSymbolRenderer)
    assert _drawn(layer) == ["D", "B", "C", "A"]


def test_an_existing_qml_is_the_template_of_the_chosen_field(qgs, tmp_path, monkeypatch):
    template = _layer()
    red = QgsFillSymbol.createSimple({"color": "255,0,0,255", "outline_width": "1.2"})
    renderer = QgsCategorizedSymbolRenderer("tipo_us_s", [QgsRendererCategory("positiva", red, "positiva")])
    renderer.setSourceSymbol(QgsFillSymbol.createSimple({"color": "90,90,90,255", "outline_width": "1.2"}))
    template.setRenderer(renderer)
    qml = str(tmp_path / "template.qml")
    template.saveNamedStyle(qml)

    layer = _layer()
    styler, asked = _styler(tmp_path, monkeypatch, "load", "tipo_us_s", ("file", qml))
    styler.apply_style_to_layer(layer)

    rules = layer.renderer().rootRule().children()
    assert rules and all('"tipo_us_s"' in r.filterExpression() for r in rules)
    positive = next(r for r in rules if r.label() == "positiva")
    negative = next(r for r in rules if r.label() == "negativa")
    assert positive.symbol().color().name() == "#ff0000"                            # QML colour kept
    assert negative.symbol().symbolLayer(0).strokeWidth() == pytest.approx(1.2)     # QML symbol as template
    assert asked == {"style": 1, "field": 1}
    assert _drawn(layer) == ["D", "B", "C", "A"]


def test_cont_per_is_offered_and_labelled_with_the_periodization(qgs, tmp_path, monkeypatch):
    layer = _layer()
    styler = cs.USViewStyler(_Conn(_db(tmp_path)), sito="S")
    seen = {}

    def get_item(parent, title, prompt, items, current=0, editable=False):
        seen["items"] = list(items)
        return items[-1], True

    monkeypatch.setattr(cs.QInputDialog, "getItem", staticmethod(get_item))
    assert styler.ask_user_categorization_field(layer) == "cont_per"
    assert len(seen["items"]) == 4
    styler._apply_temp_style(layer, "cont_per")
    labels = {r.label() for r in layer.renderer().rootRule().children()}
    assert any("Tardo XVI secolo" in label for label in labels)


def test_the_choice_is_asked_once_for_the_per_period_layers(qgs, tmp_path, monkeypatch):
    styler, asked = _styler(tmp_path, monkeypatch, "temp", "d_stratigrafica")
    styler.apply_style_to_layer(_layer(), choice="temp")
    styler.apply_style_to_layer(_layer(), choice="temp")
    assert asked == {"style": 0, "field": 1}
