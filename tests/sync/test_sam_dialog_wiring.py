"""SAM: la finestra riscritta — cablaggio e funzioni pure (2026-10-12).

Prima: bersaglio solo `pyunitastratigrafiche`/`_usm`, raster solo da file,
tre script worker e un venv che nessuno creava. Ora: layer temporaneo o
qualunque layer poligonale, tile resi dalla vista, ambiente installabile e
pesi scaricabili dalla finestra, classi a testo (edifici, strade, fiumi…).
"""
from __future__ import annotations

import ast
import importlib.util
import os
import sys
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("qgis.core")

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from qgis.core import (QgsApplication, QgsCoordinateReferenceSystem, QgsFeature, QgsField,  # noqa: E402
                       QgsGeometry, QgsProject, QgsVectorLayer)
from qgis.PyQt.QtCore import QVariant  # noqa: E402

SOURCE = (_ROOT / "tabs" / "Sam_Segmentation_Dialog.py").read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def qgs():
    app = QgsApplication.instance()
    if app is None:
        QgsApplication.setPrefixPath(os.environ.get("QGIS_PREFIX_PATH", "/Applications/QGIS.app/Contents/MacOS"), True)
        app = QgsApplication([], False)
        app.initQgis()
    return app


@pytest.fixture(scope="module")
def dlg_module(qgs):
    spec = importlib.util.spec_from_file_location("sam_dialog_under_test", _ROOT / "tabs" / "Sam_Segmentation_Dialog.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# --- cablaggio (albero sintattico) ---------------------------------------------
def _class(tree, name):
    return next(n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name == name)


def test_ogni_metodo_privato_chiamato_su_self_esiste():
    tree = ast.parse(SOURCE)
    cls = _class(tree, "SamSegmentationDialog")
    defined = {n.name for n in cls.body if isinstance(n, ast.FunctionDef)}
    used = set()
    for n in ast.walk(cls):
        if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id == "self" \
                and n.attr.startswith("_") and not n.attr.startswith("__"):
            used.add(n.attr)
    attrs_not_methods = {"_job"}
    missing = {u for u in used - defined - attrs_not_methods}
    assert not missing, f"metodi privati usati ma non definiti: {sorted(missing)}"


def test_niente_script_worker_in_bin_ne_percorsi_di_venv_scritti_a_mano():
    assert "sam_local_worker" not in SOURCE and "sam_api_worker" not in SOURCE
    assert "'sam_venv'" not in SOURCE and '"sam_venv"' not in SOURCE, "il percorso del venv lo sa sam_environment"
    assert "se.worker_command(" in SOURCE and "se.SamWorkerThread(" in SOURCE
    assert "se.SamSetupThread(" in SOURCE and "se.SamDownloadThread(" in SOURCE


def test_gli_strumenti_di_mappa_ricevono_coordinate_di_mappa_non_pixel():
    """`raster_layer=None`: i tool restituiscono coordinate di mappa, i pixel li fa il dialogo."""
    assert "SamPointMapTool(canvas, None," in SOURCE
    assert "SamBoxMapTool(canvas, None," in SOURCE
    assert "SamPolygonMapTool(canvas, None," in SOURCE


def test_il_plugin_non_chiama_piu_il_modulo_solo_pietre():
    plugin = (_ROOT / "pyarchinitPlugin.py").read_text(encoding="utf-8")
    assert "SAM Stone Segmentation" not in plugin
    assert plugin.count("SamSegmentationDialog(db_manager, parent=self.iface.mainWindow())") == 1


# --- funzioni pure ----------------------------------------------------------------
def test_modelli_per_tipo_di_prompt(dlg_module):
    normal = dlg_module.models_for(False)
    text = dlg_module.models_for(True)
    assert [b for _, b, _ in normal] == ["sam2"] * 4 + ["replicate"]
    assert [b for _, b, _ in text] == ["yoloe"] * 3 + ["roboflow"]
    assert text[0][2] == "yoloe-26s" and "MobileCLIP2" in text[0][0]
    assert normal[-1][2] is None and text[-1][2] is None


def test_is_us_layer_per_nome_e_sorgente(qgs, dlg_module):
    us = QgsVectorLayer("MultiPolygon?crs=EPSG:32633", "pyunitastratigrafiche", "memory")
    usm = QgsVectorLayer("MultiPolygon?crs=EPSG:32633", "pyunitastratigrafiche_usm", "memory")
    other = QgsVectorLayer("MultiPolygon?crs=EPSG:32633", "edifici", "memory")
    assert dlg_module.is_us_layer(us) and dlg_module.is_us_layer(usm)
    assert not dlg_module.is_us_layer(other) and not dlg_module.is_us_layer(None)


def test_il_layer_temporaneo_ha_i_campi_dei_segmenti(qgs, dlg_module):
    layer = dlg_module.new_memory_layer("SAM_prova", QgsCoordinateReferenceSystem("EPSG:3857"))
    assert layer.isValid() and layer.crs().authid() == "EPSG:3857"
    assert [f.name() for f in layer.fields()] == ["label", "score", "area", "source", "created"]
    assert layer.geometryType() == 2       # poligoni


def test_attributi_per_il_layer_us_e_per_gli_altri(qgs, dlg_module):
    us = QgsVectorLayer("MultiPolygon?crs=EPSG:32633&field=scavo_s:string&field=area_s:integer&field=us_s:integer"
                        "&field=stratigraph_index_us:integer&field=tipo_us_s:string&field=disegnatore:string"
                        "&field=data:string", "pyunitastratigrafiche", "memory")
    geom = QgsGeometry.fromWkt("MULTIPOLYGON(((0 0, 10 0, 10 10, 0 10, 0 0)))")
    ctx = {"us_layer": True, "site": "Scavo", "area": "1", "strat_index": 1, "tipo_us": "pietra", "source": "sam2.1_t.pt"}
    vals = dlg_module.feature_attributes(us.fields(), {"label": "building", "score": 0.9}, geom, ctx)
    assert vals["scavo_s"] == "Scavo" and vals["area_s"] == "1" and vals["tipo_us_s"] == "pietra"
    assert vals["disegnatore"].startswith("SAM ") and "us_s" not in vals
    mem = dlg_module.new_memory_layer("m", QgsCoordinateReferenceSystem("EPSG:32633"))
    ctx = {"us_layer": False, "label_field": "label", "source": "yoloe-26s-seg.pt"}
    vals = dlg_module.feature_attributes(mem.fields(), {"label": "building", "score": 0.9}, geom, ctx)
    assert vals["label"] == "building" and vals["score"] == 0.9 and vals["area"] == 100.0
    assert vals["source"] == "yoloe-26s-seg.pt" and "created" in vals
    vals = dlg_module.feature_attributes(mem.fields(), {"label": None}, geom, ctx)
    assert vals["label"] == "segmento"


def test_prompt_in_pixel_dentro_l_immagine(qgs, dlg_module):
    from modules.gis.sam_raster_source import SamImage
    img = SamImage("x.png", 100, 50, (1000.0, 0.5, 0.0, 2000.0, 0.0, -0.5), QgsCoordinateReferenceSystem("EPSG:32633"))
    pix = dlg_module.prompts_to_pixels(dlg_module.MODE_POINTS, [[1010.0, 1995.0], [5000.0, 5000.0]], img)
    assert pix == {"points": [[20.0, 10.0]], "labels": [1]}
    pix = dlg_module.prompts_to_pixels(dlg_module.MODE_BOX, [[1005.0, 1990.0, 1015.0, 1998.0]], img)
    assert pix["boxes"] == [[10.0, 4.0, 30.0, 20.0]]
    pix = dlg_module.prompts_to_pixels(dlg_module.MODE_BOX, [[900.0, 2100.0, 901.0, 2101.0]], img)
    assert pix["boxes"] == []


def test_sam2_lavora_solo_a_1024_e_yoloe_a_multipli_di_32(dlg_module):
    """Bug visto da Enzo: immagine 960 px -> imgsz 960 -> «size of tensor a (60) must match (56)»."""
    assert dlg_module.worker_imgsz("sam2", 960, 700) == 1024
    assert dlg_module.worker_imgsz("sam2", 4000, 3000) == 1024
    assert dlg_module.worker_imgsz("replicate", 500, 500) == 1024
    assert dlg_module.worker_imgsz("yoloe", 1000, 800) == 1024
    assert dlg_module.worker_imgsz("yoloe", 4000, 3000) == 1280
    assert dlg_module.worker_imgsz("yoloe", 30, 20) == 64


# --- la finestra, senza QGIS vivo ----------------------------------------------------
def test_la_finestra_si_apre_e_cambia_modelli_col_modo(qgs, dlg_module, monkeypatch):
    monkeypatch.setattr(dlg_module.se, "is_ready", lambda *a, **k: (False, "ambiente non installato"))
    dlg = dlg_module.SamSegmentationDialog(None)
    qgs.processEvents()
    assert dlg.comboBox_target.allowEmptyLayer()
    assert dlg.current_mode() == dlg_module.MODE_AUTO
    assert dlg.comboBox_model.count() == 5 and dlg.current_backend()[0] == "sam2"
    dlg.radio_text.setChecked(True)
    dlg._on_mode_changed(dlg.radio_text)
    assert dlg.comboBox_model.count() == 4 and dlg.current_backend()[0] == "yoloe"
    assert dlg.lineEdit_classes.isEnabled() and "building" in dlg.lineEdit_classes.text()
    dlg.comboBox_model.setCurrentIndex(3)       # Roboflow
    assert dlg.current_backend() == ("roboflow", None)
    assert dlg.lineEdit_api_key.isVisibleTo(dlg) and not dlg.btn_download.isVisibleTo(dlg)
    assert dlg._validate() in (dlg_module._t("err_no_raster"), dlg_module._t("err_no_canvas"))
    # un layer poligonale qualunque come destinazione: il campo etichetta si propone da solo
    other = QgsVectorLayer("MultiPolygon?crs=EPSG:32633&field=id:integer&field=classe:string", "edifici", "memory")
    QgsProject.instance().addMapLayer(other)
    dlg.comboBox_target.setLayer(other)
    dlg._on_target_changed(other)
    assert not dlg.us_widget.isVisibleTo(dlg) and dlg.comboBox_label_field.currentField() == "classe"
    dlg.check_thread.wait(5000)
    QgsProject.instance().removeMapLayer(other.id())


# --- rifiniture dopo la lettura dell'agente dei tutorial -----------------------------
def test_le_voci_dei_modelli_e_le_istruzioni_sono_nella_lingua_giusta(dlg_module):
    assert dlg_module.models_for(True, "en")[0][0].startswith("Local:")
    assert "text classes" in dlg_module.models_for(True, "en")[-1][0]
    assert "solo automatico" in dlg_module.models_for(False, "it")[-1][0]
    assert "Locale:" in dlg_module.models_for(False, "it")[0][0]
    for key in ("instr_points", "instr_box", "instr_polygon"):
        assert "Avvia la selezione" in dlg_module._L[key]["it"] and "Start selection" in dlg_module._L[key]["en"]
    assert "err_outside" not in dlg_module._L, "il messaggio lo da' sam_raster_source, nella lingua di QGIS"


def test_polygon_parts_only_butta_linee_e_punti(qgs, dlg_module):
    coll = QgsGeometry.fromWkt("GEOMETRYCOLLECTION(POLYGON((0 0, 4 0, 4 4, 0 4, 0 0)), LINESTRING(0 0, 9 9), POINT(1 1))")
    out = dlg_module.polygon_parts_only(coll)
    assert out.isMultipart() and out.type() == 2 and out.area() == pytest.approx(16.0)
    assert dlg_module.polygon_parts_only(QgsGeometry.fromWkt("GEOMETRYCOLLECTION(LINESTRING(0 0, 9 9))")).isEmpty()
    plain = dlg_module.polygon_parts_only(QgsGeometry.fromWkt("POLYGON((0 0, 2 0, 2 2, 0 2, 0 0))"))
    assert plain.isMultipart() and plain.area() == pytest.approx(4.0)


def test_il_layer_dei_segmenti_ha_riempimento_semitrasparente_per_etichetta(qgs, dlg_module):
    layer = dlg_module.new_memory_layer("s", QgsCoordinateReferenceSystem("EPSG:32633"))
    feats = []
    for i, lab in enumerate(("building", "road", "road")):
        f = QgsFeature(layer.fields())
        f.setGeometry(QgsGeometry.fromWkt(f"MULTIPOLYGON((({i*10} 0, {i*10+5} 0, {i*10+5} 5, {i*10} 5, {i*10} 0)))"))
        f.setAttribute("label", lab)
        feats.append(f)
    layer.dataProvider().addFeatures(feats)
    dlg_module.style_segments_layer(layer)
    renderer = layer.renderer()
    cats = renderer.categories()            # copie: vanno tenute in vita finche' si guarda il simbolo
    assert renderer.type() == "categorizedSymbol" and len(cats) == 2
    sym = cats[0].symbol()
    assert 0.3 < sym.opacity() < 0.6 and sym.symbolLayer(0).brushStyle() != 0      # riempito, non solo contorno
    single = dlg_module.new_memory_layer("u", QgsCoordinateReferenceSystem("EPSG:32633"))
    dlg_module.style_segments_layer(single)
    assert single.renderer().type() == "singleSymbol" and single.renderer().symbol().opacity() < 1.0


def _fake_job(dlg_module):
    from modules.gis.sam_raster_source import SamImage
    crs = QgsCoordinateReferenceSystem("EPSG:32633")
    return {"image": SamImage("x.png", 100, 100, (1000.0, 1.0, 0.0, 2000.0, 0.0, -1.0), crs), "area": None,
            "mode": 1, "backend": "sam2", "key": "sam2.1_t", "canvas_crs": crs}


RESULT = {"model": "sam2.1_t.pt", "polygons": [{"ring": [[0, 0], [10, 0], [10, 10], [0, 10]], "holes": [],
                                                 "score": 0.5, "label": "stone", "area_px": 100}], "warnings": []}


def test_add_results_rispetta_la_sessione_di_modifica_aperta(qgs, dlg_module, monkeypatch):
    """Prima: commitChanges() salvava anche le modifiche in sospeso dell'utente, e rollBack() le buttava."""
    monkeypatch.setattr(dlg_module.se, "is_ready", lambda *a, **k: (False, "no"))
    dlg = dlg_module.SamSegmentationDialog(None)
    qgs.processEvents()
    layer = QgsVectorLayer("MultiPolygon?crs=EPSG:32633&field=label:string", "edifici", "memory")
    QgsProject.instance().addMapLayer(layer)
    dlg.comboBox_target.setLayer(layer)
    dlg._on_target_changed(layer)
    layer.startEditing()
    pending = QgsFeature(layer.fields())
    pending.setGeometry(QgsGeometry.fromWkt("MULTIPOLYGON(((0 0, 1 0, 1 1, 0 1, 0 0)))"))
    layer.addFeature(pending)
    dlg._job = _fake_job(dlg_module)
    added, target, left_open = dlg._add_results(RESULT)
    assert added == 1 and target is layer and left_open is True
    assert layer.isEditable() and layer.featureCount() == 2      # la sessione resta aperta, niente salvato
    layer.rollBack()
    assert layer.featureCount() == 0
    # senza sessione aperta: si salva, e il layer torna in sola lettura
    added, target, left_open = dlg._add_results(RESULT)
    assert added == 1 and left_open is False and not layer.isEditable() and layer.featureCount() == 1
    assert next(layer.getFeatures())["label"] == "stone"
    dlg.check_thread.wait(5000)
    QgsProject.instance().removeMapLayer(layer.id())


def test_add_results_sul_layer_temporaneo_lo_crea_riempito(qgs, dlg_module, monkeypatch):
    monkeypatch.setattr(dlg_module.se, "is_ready", lambda *a, **k: (False, "no"))
    dlg = dlg_module.SamSegmentationDialog(None)
    qgs.processEvents()
    dlg.comboBox_target.setLayer(None)
    dlg._job = _fake_job(dlg_module)
    before = set(QgsProject.instance().mapLayers())
    added, target, left_open = dlg._add_results(RESULT)
    assert added == 1 and left_open is False and target.id() in QgsProject.instance().mapLayers()
    assert target.name().startswith("SAM_") and target.featureCount() == 1
    assert target.renderer().symbol().opacity() < 1.0
    feat = next(target.getFeatures())
    assert feat["label"] == "stone" and feat["area"] == pytest.approx(100.0) and feat["source"] == "sam2.1_t.pt"
    assert feat.geometry().boundingBox().xMinimum() == 1000.0 and feat.geometry().boundingBox().yMaximum() == 2000.0
    dlg.check_thread.wait(5000)
    for lid in set(QgsProject.instance().mapLayers()) - before:
        QgsProject.instance().removeMapLayer(lid)
