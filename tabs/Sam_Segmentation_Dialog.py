# -*- coding: utf-8 -*-
"""SAM — segmentazione di ortofoto e tile in poligoni, per pyArchInit.

Pietre e unità stratigrafiche, ma anche edifici, strade, campi, fiumi: il
dialogo prende un layer raster (un file o un servizio di tile come ESRI,
Google, WMS), un'area e un modo di indicare che cosa segmentare, e scrive
poligoni in un layer di destinazione — i layer US di pyArchInit, un layer
poligonale qualunque, o un layer temporaneo nuovo.

Quattro pezzi, ognuno col suo modulo:

- `modules/utility/sam_environment.py`: l'ambiente Python separato
  (`<home>/bin/sam_venv`), i pesi (`<home>/bin/models/sam`), i comandi;
- `modules/gis/sam_raster_source.py`: l'immagine da segmentare — ritaglio
  del file con GDAL, oppure **rendering della vista** per i tile — e la
  georeferenza per tornare dai pixel alla mappa;
- `scripts/sam_worker.py`: il lavoro vero, nel venv (SAM 2.1 e YOLOE con
  ultralytics; Replicate e Roboflow in cloud), che restituisce poligoni in
  pixel;
- `modules/gis/sam_map_tools.py`: gli strumenti di mappa per punti,
  riquadri e poligoni (coordinate di mappa).

Modi: **tutto automatico** (SAM 2.1 segmenta ogni cosa), **punti**,
**riquadro**, **poligono** disegnato o da layer (si segmenta solo dentro),
**classi a testo** («building, road, river, field»: YOLOE-26 in locale o
SAM 3 in cloud, e ogni poligono porta la sua etichetta).

Author: Enzo Cocca <enzo.ccc@gmail.com>
"""
from __future__ import annotations

import json
import os
import tempfile
from datetime import date, datetime

from qgis.PyQt.QtCore import Qt, QSettings, QThread, pyqtSignal
from qgis.PyQt.QtWidgets import (
    QApplication, QButtonGroup, QCheckBox, QComboBox, QDialog, QDoubleSpinBox,
    QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QMessageBox,
    QPlainTextEdit, QProgressBar, QPushButton, QRadioButton, QSpinBox, QVBoxLayout,
    QWidget,
)
from qgis.core import (
    Qgis, QgsCoordinateTransform, QgsFeature, QgsField, QgsFields, QgsGeometry,
    QgsFieldProxyModel, QgsMapLayerProxyModel, QgsMessageLog, QgsPointXY, QgsProject,
    QgsRasterLayer, QgsRectangle, QgsSettings, QgsVectorLayer, QgsWkbTypes,
)
from qgis.PyQt.QtCore import QVariant
from qgis.gui import QgsFieldComboBox, QgsMapLayerComboBox
from qgis.utils import iface

from modules.gis import sam_raster_source as rs
from modules.utility import sam_environment as se
from modules.utility.pyarchinit_home import pyarchinit_home

try:
    from modules.gis.sam_map_tools import SamBoxMapTool, SamPointMapTool, SamPolygonMapTool
    HAS_MAP_TOOLS = True
except ImportError as e:                       # pragma: no cover
    HAS_MAP_TOOLS = False
    QgsMessageLog.logMessage(f"SAM map tools not available: {e}", "PyArchInit", Qgis.Warning)

LOG = "PyArchInit SAM"
US_LAYER_NAMES = ("pyunitastratigrafiche", "pyunitastratigrafiche_usm")
DEFAULT_CLASSES = "building, road, river, field"
MEMORY_FIELDS = (("label", QVariant.String), ("score", QVariant.Double), ("area", QVariant.Double),
                 ("source", QVariant.String), ("created", QVariant.String))
MODE_AUTO, MODE_POINTS, MODE_BOX, MODE_POLYGON, MODE_LAYER, MODE_TEXT = 1, 2, 3, 4, 5, 6
TEXT_MODES = (MODE_TEXT,)


def _lang():
    try:
        return (QgsSettings().value("locale/userLocale", "it", type=str) or "it")[:2]
    except Exception:          # noqa: BLE001
        return "it"


_L = {
    "title": {"it": "SAM — Segmentazione (pietre, edifici, strade, campi, fiumi…)",
              "en": "SAM — Segmentation (stones, buildings, roads, fields, rivers…)"},
    "header": {"it": "<b>Segmentazione automatica</b> — da un'ortofoto o da un layer di tile (ESRI, Google, WMS) "
                     "a poligoni, con SAM 2.1 (Meta) o con classi a testo.",
               "en": "<b>Automatic segmentation</b> — from an orthophoto or a tile layer (ESRI, Google, WMS) "
                     "to polygons, with SAM 2.1 (Meta) or with text classes."},
    "env": {"it": "Ambiente locale", "en": "Local environment"},
    "env_checking": {"it": "controllo…", "en": "checking…"},
    "env_ready": {"it": "pronto — {0}", "en": "ready — {0}"},
    "env_missing": {"it": "non installato: serve per i modelli locali (SAM 2.1, YOLOE). "
                          "Un Python 3.10–3.13 di sistema, ~1.5 GB di pacchetti.",
                    "en": "not installed: needed for the local models (SAM 2.1, YOLOE). "
                          "A system Python 3.10–3.13, ~1.5 GB of packages."},
    "env_install": {"it": "Installa / aggiorna", "en": "Install / update"},
    "env_installing": {"it": "installazione in corso…", "en": "installing…"},
    "env_log": {"it": "Mostra registro", "en": "Show log"},
    "image": {"it": "Immagine", "en": "Image"},
    "raster_layer": {"it": "Layer raster:", "en": "Raster layer:"},
    "raster_tip": {"it": "Ortofoto (file) oppure tile/WMS: i servizi si rendono dalla vista.",
                   "en": "Orthophoto (file) or tiles/WMS: services are rendered from the view."},
    "area": {"it": "Area:", "en": "Area:"},
    "area_view": {"it": "vista corrente", "en": "current view"},
    "area_all": {"it": "tutto il raster", "en": "whole raster"},
    "mupp": {"it": "Risoluzione (unità mappa/px):", "en": "Resolution (map units/px):"},
    "mupp_tip": {"it": "Per i tile: quanti metri (o gradi) per pixel nel reso. Il valore proposto è quello della vista.",
                 "en": "For tiles: map units per pixel in the render. The proposed value is the view's."},
    "max_side": {"it": "Lato massimo (px):", "en": "Max side (px):"},
    "max_side_tip": {"it": "Oltre questo lato l'immagine viene ridotta. SAM lavora a 1024 interni.",
                     "en": "Above this side the image is downscaled. SAM works at 1024 internally."},
    "what": {"it": "Che cosa segmentare", "en": "What to segment"},
    "mode_auto": {"it": "Tutto automatico (ogni oggetto)", "en": "Everything (automatic)"},
    "mode_points": {"it": "Punti: clicca gli oggetti sulla mappa", "en": "Points: click the objects on the map"},
    "mode_box": {"it": "Riquadro: disegna un rettangolo", "en": "Box: draw a rectangle"},
    "mode_polygon": {"it": "Poligono: disegna l'area", "en": "Polygon: draw the area"},
    "mode_layer": {"it": "Poligono da layer:", "en": "Polygon from layer:"},
    "mode_text": {"it": "Classi a testo:", "en": "Text classes:"},
    "classes_tip": {"it": "Parole in inglese separate da virgola: building, road, river, field, stone, wall…",
                    "en": "English words separated by commas: building, road, river, field, stone, wall…"},
    "conf": {"it": "Soglia:", "en": "Threshold:"},
    "instr_points": {"it": "Premi «Avvia», poi clicca gli oggetti sulla mappa. Tasto destro o Invio per finire, Esc per annullare.",
                     "en": "Press “Start”, then click the objects on the map. Right-click or Enter to finish, Esc to cancel."},
    "instr_box": {"it": "Premi «Avvia», poi trascina un rettangolo sulla mappa. Esc per annullare.",
                  "en": "Press “Start”, then drag a rectangle on the map. Esc to cancel."},
    "instr_polygon": {"it": "Premi «Avvia», poi clicca i vertici; tasto destro o Invio per chiudere, Backspace toglie l'ultimo, Esc annulla.",
                      "en": "Press “Start”, then click the vertices; right-click or Enter to close, Backspace removes the last, Esc cancels."},
    "instr_layer": {"it": "Si usa la geometria selezionata nel layer (o tutte, se nessuna è selezionata).",
                    "en": "The selected feature of the layer is used (or all of them if none is selected)."},
    "instr_text": {"it": "Ogni classe diventa un'etichetta sui poligoni. In locale serve YOLOE (con il codificatore di testo); in cloud SAM 3 di Roboflow.",
                   "en": "Each class becomes a label on the polygons. Locally this needs YOLOE (with the text encoder); in the cloud Roboflow's SAM 3."},
    "model": {"it": "Modello", "en": "Model"},
    "model_label": {"it": "Modello:", "en": "Model:"},
    "weights_ok": {"it": "pesi presenti ✓", "en": "weights present ✓"},
    "weights_missing": {"it": "pesi mancanti (~{0} MB)", "en": "weights missing (~{0} MB)"},
    "download": {"it": "Scarica pesi", "en": "Download weights"},
    "api_key": {"it": "Chiave API:", "en": "API key:"},
    "api_replicate": {"it": '<a href="https://replicate.com/account/api-tokens">Chiave Replicate</a>',
                      "en": '<a href="https://replicate.com/account/api-tokens">Replicate key</a>'},
    "api_roboflow": {"it": '<a href="https://app.roboflow.com/settings/api">Chiave Roboflow</a>',
                     "en": '<a href="https://app.roboflow.com/settings/api">Roboflow key</a>'},
    "target": {"it": "Destinazione", "en": "Target"},
    "target_layer": {"it": "Layer:", "en": "Layer:"},
    "target_new": {"it": "— nuovo layer temporaneo —", "en": "— new temporary layer —"},
    "target_tip": {"it": "Un layer poligonale del progetto (pyunitastratigrafiche, un tuo layer) oppure un layer temporaneo nuovo.",
                   "en": "A polygon layer of the project (pyunitastratigrafiche, your own) or a new temporary layer."},
    "site": {"it": "Sito:", "en": "Site:"},
    "area_us": {"it": "Area:", "en": "Area:"},
    "strat": {"it": "Indice stratigrafico:", "en": "Stratigraphic index:"},
    "strat_tip": {"it": "1 = pietre/oggetti, 2 = strato/area", "en": "1 = stones/objects, 2 = layer/area"},
    "tipo_us": {"it": "Tipo US:", "en": "US type:"},
    "label_field": {"it": "Campo per l'etichetta:", "en": "Field for the label:"},
    "label_field_tip": {"it": "Dove scrivere la classe (o «segmento»); vuoto = non scrivere.",
                        "en": "Where to write the class (or “segment”); empty = do not write."},
    "ready": {"it": "Pronto", "en": "Ready"},
    "start": {"it": "Avvia", "en": "Start"},
    "start_select": {"it": "Avvia la selezione", "en": "Start selection"},
    "cancel": {"it": "Annulla", "en": "Cancel"},
    "close": {"it": "Chiudi", "en": "Close"},
    "err_no_raster": {"it": "Scegli un layer raster.", "en": "Choose a raster layer."},
    "err_no_canvas": {"it": "La mappa di QGIS non è disponibile.", "en": "The QGIS map is not available."},
    "err_no_env": {"it": "L'ambiente locale non è installato: premi «Installa / aggiorna» (o scegli un modello cloud).",
                   "en": "The local environment is not installed: press “Install / update” (or choose a cloud model)."},
    "err_no_weights": {"it": "I pesi del modello mancano: premi «Scarica pesi».",
                       "en": "The model weights are missing: press “Download weights”."},
    "err_no_key": {"it": "Serve la chiave API del servizio.", "en": "The service API key is needed."},
    "err_no_classes": {"it": "Scrivi almeno una classe (es. building, road).",
                       "en": "Write at least one class (e.g. building, road)."},
    "err_no_area": {"it": "Compila l'area per il layer US.", "en": "Fill in the area for the US layer."},
    "err_no_polygon_layer": {"it": "Scegli un layer poligonale.", "en": "Choose a polygon layer."},
    "err_no_features": {"it": "Il layer non ha geometrie.", "en": "The layer has no features."},
    "err_outside": {"it": "L'area scelta non copre il raster.", "en": "The chosen area does not cover the raster."},
    "preparing": {"it": "Preparo l'immagine…", "en": "Preparing the image…"},
    "rendering": {"it": "Rendo la vista del layer di tile…", "en": "Rendering the tile layer view…"},
    "running": {"it": "Segmentazione in corso…", "en": "Segmenting…"},
    "no_points": {"it": "Nessun punto dentro l'immagine.", "en": "No point inside the image."},
    "no_box": {"it": "Nessun riquadro disegnato.", "en": "No box drawn."},
    "cancelled": {"it": "Selezione annullata.", "en": "Selection cancelled."},
    "done": {"it": "Fatto: {0} poligoni aggiunti a «{1}» ({2}).", "en": "Done: {0} polygons added to “{1}” ({2})."},
    "done_none": {"it": "Nessun poligono trovato: prova un'area più piccola, una soglia più bassa o un altro modello.",
                  "en": "No polygon found: try a smaller area, a lower threshold or another model."},
    "failed": {"it": "Segmentazione fallita", "en": "Segmentation failed"},
    "warn": {"it": "Attenzione", "en": "Warning"},
    "error": {"it": "Errore", "en": "Error"},
    "installed": {"it": "Ambiente pronto: {0}", "en": "Environment ready: {0}"},
    "install_failed": {"it": "Installazione non riuscita: {0}", "en": "Installation failed: {0}"},
    "downloading": {"it": "Scarico {0}", "en": "Downloading {0}"},
    "segment": {"it": "segmento", "en": "segment"},
    "us_edit_hint": {"it": "Poi assegna i numeri US nella tabella degli attributi.",
                     "en": "Then assign the US numbers in the attribute table."},
}


def _t(key, *args):
    text = _L[key].get(_lang(), _L[key]["en"])
    return text.format(*args) if args else text


# ----------------------------------------------------------------------
# Funzioni pure (provate dai test)
# ----------------------------------------------------------------------
def models_for(text_mode):
    """Le voci della tendina «Modello» per il tipo di prompt: (etichetta, backend, chiave pesi)."""
    if text_mode:
        rows = [(f"Locale: {se.WEIGHTS[k].label} — ~{se.WEIGHTS[k].size_mb} MB + MobileCLIP2 254 MB",
                 "yoloe", k) for k in se.TEXT_KEYS]
        rows.append(("Cloud: Roboflow SAM 3 (classi a testo, chiave API)", "roboflow", None))
        return rows
    rows = [(f"Locale: {se.WEIGHTS[k].label} — ~{se.WEIGHTS[k].size_mb} MB", "sam2", k) for k in se.SAM_KEYS]
    rows.append(("Cloud: Replicate SAM-2 (solo automatico, chiave API)", "replicate", None))
    return rows


def is_us_layer(layer):
    """Un layer US/USM di pyArchInit (per nome o per sorgente)."""
    if layer is None:
        return False
    name = (layer.name() or "").lower()
    source = (layer.source() or "").lower()
    return any(name == n or name.startswith(n + " ") or f"table=\"{n}\"" in source or f"layername={n}" in source
               for n in US_LAYER_NAMES)


def new_memory_layer(name, crs):
    """Un layer temporaneo di multipoligoni con i campi dei segmenti."""
    layer = QgsVectorLayer(f"MultiPolygon?crs={crs.authid() or 'EPSG:4326'}", name, "memory")
    fields = QgsFields()
    for fname, ftype in MEMORY_FIELDS:
        fields.append(QgsField(fname, ftype))
    layer.dataProvider().addAttributes(list(fields))
    layer.updateFields()
    return layer


def feature_attributes(fields, polygon, geom, context):
    """Gli attributi di un segmento per il layer di destinazione.

    `context`: dict con site, area, strat_index, tipo_us (layer US), label_field
    (altri layer), source (nome del modello). Scrive solo i campi che esistono.
    """
    names = [f.name() for f in fields]
    values = {}
    label = polygon.get("label") or context.get("default_label") or _t("segment")
    if context.get("us_layer"):
        mapping = {"scavo_s": context.get("site"), "area_s": context.get("area"),
                   "us_s": None, "stratigraph_index_us": context.get("strat_index"),
                   "tipo_us_s": context.get("tipo_us"), "disegnatore": "SAM " + str(context.get("source") or ""),
                   "data": date.today().isoformat()}
        for k, v in mapping.items():
            if k in names and v is not None:
                values[k] = v
        return values
    label_field = context.get("label_field")
    if label_field and label_field in names:
        values[label_field] = label
    if "score" in names and polygon.get("score") is not None:
        values["score"] = float(polygon["score"])
    if "area" in names:
        values["area"] = float(geom.area())
    if "source" in names:
        values["source"] = str(context.get("source") or "")
    if "created" in names:
        values["created"] = datetime.now().isoformat(timespec="seconds")
    return values


def prompts_to_pixels(mode, prompts, image):
    """Punti/riquadri in coordinate mappa (CRS dell'immagine) -> pixel dell'immagine."""
    gt = image.geotransform
    w, h = image.width, image.height
    out = {}
    if mode == MODE_POINTS:
        pts = []
        for x, y in prompts:
            c, r = rs.map_to_pixel(gt, x, y)
            if 0 <= c < w and 0 <= r < h:
                pts.append([c, r])
        out["points"] = pts
        out["labels"] = [1] * len(pts)
    elif mode == MODE_BOX:
        boxes = []
        for x1, y1, x2, y2 in prompts:
            c1, r1 = rs.map_to_pixel(gt, min(x1, x2), max(y1, y2))
            c2, r2 = rs.map_to_pixel(gt, max(x1, x2), min(y1, y2))
            c1, c2 = max(0.0, c1), min(float(w), c2)
            r1, r2 = max(0.0, r1), min(float(h), r2)
            if c2 - c1 >= 2 and r2 - r1 >= 2:
                boxes.append([c1, r1, c2, r2])
        out["boxes"] = boxes
    return out


# ----------------------------------------------------------------------
class _CheckThread(QThread):
    done = pyqtSignal(bool, str)

    def run(self):
        ok, info = se.is_ready()
        self.done.emit(ok, info)


class SamSegmentationDialog(QDialog):
    """La finestra. `db_manager` resta per compatibilità con il plugin (non serve)."""

    def __init__(self, db_manager=None, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.map_tool = None
        self.previous_map_tool = None
        self.worker = None
        self.setup_thread = None
        self.download_thread = None
        self.check_thread = None
        self.env_ready = False
        self.env_info = ""
        self.work_dir = tempfile.mkdtemp(prefix="pyarchinit_sam_")
        self._job = None                      # dati del lavoro in corso
        self.initUI()
        self.load_settings()
        self._check_environment()

    # ------------------------------------------------------------------
    # Interfaccia
    # ------------------------------------------------------------------
    def initUI(self):
        self.setWindowTitle(_t("title"))
        self.setMinimumWidth(560)
        layout = QVBoxLayout(self)

        header = QLabel(_t("header"))
        header.setWordWrap(True)
        layout.addWidget(header)

        # --- ambiente -------------------------------------------------
        env_group = QGroupBox(_t("env"))
        env_layout = QGridLayout()
        self.label_env = QLabel(_t("env_checking"))
        self.label_env.setWordWrap(True)
        env_layout.addWidget(self.label_env, 0, 0)
        self.btn_install = QPushButton(_t("env_install"))
        self.btn_install.clicked.connect(self.install_environment)
        env_layout.addWidget(self.btn_install, 0, 1)
        self.btn_log = QPushButton(_t("env_log"))
        self.btn_log.setCheckable(True)
        self.btn_log.toggled.connect(lambda on: self.text_log.setVisible(on))
        env_layout.addWidget(self.btn_log, 0, 2)
        self.text_log = QPlainTextEdit()
        self.text_log.setReadOnly(True)
        self.text_log.setMaximumHeight(140)
        self.text_log.setVisible(False)
        env_layout.addWidget(self.text_log, 1, 0, 1, 3)
        env_group.setLayout(env_layout)
        layout.addWidget(env_group)

        # --- immagine -------------------------------------------------
        img_group = QGroupBox(_t("image"))
        img_layout = QGridLayout()
        img_layout.addWidget(QLabel(_t("raster_layer")), 0, 0)
        self.comboBox_raster = QgsMapLayerComboBox()
        self.comboBox_raster.setFilters(QgsMapLayerProxyModel.RasterLayer)
        self.comboBox_raster.setToolTip(_t("raster_tip"))
        self.comboBox_raster.layerChanged.connect(self._on_raster_changed)
        img_layout.addWidget(self.comboBox_raster, 0, 1, 1, 3)
        self.label_raster_info = QLabel("")
        self.label_raster_info.setStyleSheet("color: gray;")
        img_layout.addWidget(self.label_raster_info, 1, 1, 1, 3)

        img_layout.addWidget(QLabel(_t("area")), 2, 0)
        self.radio_area_view = QRadioButton(_t("area_view"))
        self.radio_area_all = QRadioButton(_t("area_all"))
        self.radio_area_view.setChecked(True)
        self.area_group = QButtonGroup(self)
        self.area_group.addButton(self.radio_area_view, 1)
        self.area_group.addButton(self.radio_area_all, 2)
        area_row = QHBoxLayout()
        area_row.addWidget(self.radio_area_view)
        area_row.addWidget(self.radio_area_all)
        area_row.addStretch()
        img_layout.addLayout(area_row, 2, 1, 1, 3)

        self.label_mupp = QLabel(_t("mupp"))
        img_layout.addWidget(self.label_mupp, 3, 0)
        self.spin_mupp = QDoubleSpinBox()
        self.spin_mupp.setDecimals(6)
        self.spin_mupp.setRange(0.000001, 100000.0)
        self.spin_mupp.setValue(0.1)
        self.spin_mupp.setToolTip(_t("mupp_tip"))
        img_layout.addWidget(self.spin_mupp, 3, 1)
        img_layout.addWidget(QLabel(_t("max_side")), 3, 2)
        self.spin_max_side = QSpinBox()
        self.spin_max_side.setRange(512, rs.MAX_SIDE_LIMIT)
        self.spin_max_side.setSingleStep(256)
        self.spin_max_side.setValue(rs.DEFAULT_MAX_SIDE)
        self.spin_max_side.setToolTip(_t("max_side_tip"))
        img_layout.addWidget(self.spin_max_side, 3, 3)
        img_group.setLayout(img_layout)
        layout.addWidget(img_group)

        # --- che cosa -------------------------------------------------
        what_group = QGroupBox(_t("what"))
        what_layout = QGridLayout()
        self.radio_auto = QRadioButton(_t("mode_auto"))
        self.radio_points = QRadioButton(_t("mode_points"))
        self.radio_box = QRadioButton(_t("mode_box"))
        self.radio_polygon = QRadioButton(_t("mode_polygon"))
        self.radio_layer = QRadioButton(_t("mode_layer"))
        self.radio_text = QRadioButton(_t("mode_text"))
        self.radio_auto.setChecked(True)
        self.mode_group = QButtonGroup(self)
        for rb, mid in ((self.radio_auto, MODE_AUTO), (self.radio_points, MODE_POINTS), (self.radio_box, MODE_BOX),
                        (self.radio_polygon, MODE_POLYGON), (self.radio_layer, MODE_LAYER),
                        (self.radio_text, MODE_TEXT)):
            self.mode_group.addButton(rb, mid)
        what_layout.addWidget(self.radio_auto, 0, 0, 1, 3)
        what_layout.addWidget(self.radio_points, 1, 0, 1, 3)
        what_layout.addWidget(self.radio_box, 2, 0, 1, 3)
        what_layout.addWidget(self.radio_polygon, 3, 0, 1, 3)
        what_layout.addWidget(self.radio_layer, 4, 0)
        self.comboBox_polygon_layer = QgsMapLayerComboBox()
        self.comboBox_polygon_layer.setFilters(QgsMapLayerProxyModel.PolygonLayer)
        what_layout.addWidget(self.comboBox_polygon_layer, 4, 1, 1, 2)
        what_layout.addWidget(self.radio_text, 5, 0)
        self.lineEdit_classes = QLineEdit(DEFAULT_CLASSES)
        self.lineEdit_classes.setToolTip(_t("classes_tip"))
        what_layout.addWidget(self.lineEdit_classes, 5, 1, 1, 2)
        conf_row = QHBoxLayout()
        conf_row.addWidget(QLabel(_t("conf")))
        self.spin_conf = QDoubleSpinBox()
        self.spin_conf.setRange(0.05, 0.95)
        self.spin_conf.setSingleStep(0.05)
        self.spin_conf.setValue(0.30)
        conf_row.addWidget(self.spin_conf)
        conf_row.addStretch()
        what_layout.addLayout(conf_row, 6, 0, 1, 3)
        self.label_instructions = QLabel("")
        self.label_instructions.setStyleSheet("color: #0066cc; font-style: italic;")
        self.label_instructions.setWordWrap(True)
        self.label_instructions.setVisible(False)
        what_layout.addWidget(self.label_instructions, 7, 0, 1, 3)
        what_group.setLayout(what_layout)
        layout.addWidget(what_group)
        self.mode_group.buttonClicked.connect(self._on_mode_changed)

        # --- modello --------------------------------------------------
        model_group = QGroupBox(_t("model"))
        model_layout = QGridLayout()
        model_layout.addWidget(QLabel(_t("model_label")), 0, 0)
        self.comboBox_model = QComboBox()
        self.comboBox_model.currentIndexChanged.connect(self._on_model_changed)
        model_layout.addWidget(self.comboBox_model, 0, 1, 1, 2)
        self.label_weights = QLabel("")
        model_layout.addWidget(self.label_weights, 1, 1)
        self.btn_download = QPushButton(_t("download"))
        self.btn_download.clicked.connect(self.download_weights)
        model_layout.addWidget(self.btn_download, 1, 2)
        self.label_api_key = QLabel(_t("api_key"))
        model_layout.addWidget(self.label_api_key, 2, 0)
        self.lineEdit_api_key = QLineEdit()
        self.lineEdit_api_key.setEchoMode(QLineEdit.EchoMode.Password)
        model_layout.addWidget(self.lineEdit_api_key, 2, 1)
        self.label_api_link = QLabel("")
        self.label_api_link.setOpenExternalLinks(True)
        model_layout.addWidget(self.label_api_link, 2, 2)
        model_group.setLayout(model_layout)
        layout.addWidget(model_group)

        # --- destinazione ---------------------------------------------
        target_group = QGroupBox(_t("target"))
        target_layout = QGridLayout()
        target_layout.addWidget(QLabel(_t("target_layer")), 0, 0)
        self.comboBox_target = QgsMapLayerComboBox()
        self.comboBox_target.setFilters(QgsMapLayerProxyModel.PolygonLayer)
        self.comboBox_target.setAllowEmptyLayer(True, _t("target_new"))
        self.comboBox_target.setToolTip(_t("target_tip"))
        self.comboBox_target.layerChanged.connect(self._on_target_changed)
        target_layout.addWidget(self.comboBox_target, 0, 1, 1, 3)
        # attributi US
        self.us_widget = QWidget()
        us_layout = QGridLayout(self.us_widget)
        us_layout.setContentsMargins(0, 0, 0, 0)
        us_layout.addWidget(QLabel(_t("site")), 0, 0)
        self.lineEdit_site = QLineEdit()
        self.lineEdit_site.setReadOnly(True)
        us_layout.addWidget(self.lineEdit_site, 0, 1)
        us_layout.addWidget(QLabel(_t("area_us")), 0, 2)
        self.lineEdit_area = QLineEdit()
        self.lineEdit_area.setPlaceholderText("1")
        us_layout.addWidget(self.lineEdit_area, 0, 3)
        us_layout.addWidget(QLabel(_t("strat")), 1, 0)
        self.spinBox_strat_index = QSpinBox()
        self.spinBox_strat_index.setRange(1, 10)
        self.spinBox_strat_index.setToolTip(_t("strat_tip"))
        us_layout.addWidget(self.spinBox_strat_index, 1, 1)
        us_layout.addWidget(QLabel(_t("tipo_us")), 1, 2)
        self.comboBox_tipo_us = QComboBox()
        self.comboBox_tipo_us.addItems(["pietra", "layer", "accumulo", "taglio", "struttura"])
        us_layout.addWidget(self.comboBox_tipo_us, 1, 3)
        target_layout.addWidget(self.us_widget, 1, 0, 1, 4)
        # campo etichetta per gli altri layer
        self.label_field_label = QLabel(_t("label_field"))
        target_layout.addWidget(self.label_field_label, 2, 0)
        self.comboBox_label_field = QgsFieldComboBox()
        self.comboBox_label_field.setFilters(QgsFieldProxyModel.String)
        self.comboBox_label_field.setAllowEmptyFieldName(True)
        self.comboBox_label_field.setToolTip(_t("label_field_tip"))
        target_layout.addWidget(self.comboBox_label_field, 2, 1, 1, 3)
        target_group.setLayout(target_layout)
        layout.addWidget(target_group)

        # --- stato e bottoni ------------------------------------------
        self.label_status = QLabel(_t("ready"))
        self.label_status.setStyleSheet("color: gray; font-style: italic;")
        self.label_status.setWordWrap(True)
        layout.addWidget(self.label_status)
        self.progressBar = QProgressBar()
        self.progressBar.setVisible(False)
        self.progressBar.setRange(0, 0)
        layout.addWidget(self.progressBar)
        btn_row = QHBoxLayout()
        self.btn_segment = QPushButton(_t("start"))
        self.btn_segment.clicked.connect(self.on_segment_clicked)
        btn_row.addWidget(self.btn_segment)
        self.btn_cancel = QPushButton(_t("cancel"))
        self.btn_cancel.setVisible(False)
        self.btn_cancel.clicked.connect(self._cancel_running)
        btn_row.addWidget(self.btn_cancel)
        self.btn_close = QPushButton(_t("close"))
        self.btn_close.clicked.connect(self.reject)
        btn_row.addWidget(self.btn_close)
        layout.addLayout(btn_row)

        self._load_site_from_config()
        self._preselect_target()
        self._on_raster_changed(self.comboBox_raster.currentLayer())
        self._on_mode_changed(None)
        self._on_target_changed(self.comboBox_target.currentLayer())

    # ------------------------------------------------------------------
    # Stato dell'interfaccia
    # ------------------------------------------------------------------
    def _canvas(self):
        try:
            return iface.mapCanvas() if iface is not None else None
        except Exception:          # noqa: BLE001
            return None

    def _preselect_target(self):
        for layer in QgsProject.instance().mapLayers().values():
            if isinstance(layer, QgsVectorLayer) and is_us_layer(layer) and layer.name().lower() == US_LAYER_NAMES[0]:
                self.comboBox_target.setLayer(layer)
                return
        self.comboBox_target.setLayer(None)

    def _on_raster_changed(self, layer):
        if layer is None:
            self.label_raster_info.setText("")
            return
        file_raster = rs.is_file_raster(layer)
        self.label_raster_info.setText(rs.describe_layer(layer))
        self.radio_area_all.setEnabled(file_raster)
        if not file_raster:
            self.radio_area_view.setChecked(True)
        self.spin_mupp.setEnabled(not file_raster)
        self.label_mupp.setEnabled(not file_raster)
        canvas = self._canvas()
        if canvas is not None and not file_raster:
            try:
                self.spin_mupp.setValue(canvas.mapUnitsPerPixel())
            except Exception:          # noqa: BLE001
                pass

    def current_mode(self):
        return self.mode_group.checkedId()

    def _on_mode_changed(self, _button):
        mode = self.current_mode()
        text_mode = mode in TEXT_MODES
        self.comboBox_polygon_layer.setEnabled(mode == MODE_LAYER)
        self.lineEdit_classes.setEnabled(text_mode)
        instructions = {MODE_POINTS: "instr_points", MODE_BOX: "instr_box", MODE_POLYGON: "instr_polygon",
                        MODE_LAYER: "instr_layer", MODE_TEXT: "instr_text"}.get(mode)
        self.label_instructions.setVisible(instructions is not None)
        self.label_instructions.setText(_t(instructions) if instructions else "")
        self.btn_segment.setText(_t("start_select") if mode in (MODE_POINTS, MODE_BOX, MODE_POLYGON) else _t("start"))
        self._refresh_models(text_mode)

    def _refresh_models(self, text_mode):
        current = self.comboBox_model.currentData()
        self.comboBox_model.blockSignals(True)
        self.comboBox_model.clear()
        for label, backend, key in models_for(text_mode):
            self.comboBox_model.addItem(label, (backend, key))
        wanted = QSettings().value("pyArchInit/sam_model_text" if text_mode else "pyArchInit/sam_model", "")
        for i in range(self.comboBox_model.count()):
            if self.comboBox_model.itemData(i)[1] == wanted or self.comboBox_model.itemData(i) == current:
                self.comboBox_model.setCurrentIndex(i)
                break
        self.comboBox_model.blockSignals(False)
        self._on_model_changed(self.comboBox_model.currentIndex())

    def current_backend(self):
        data = self.comboBox_model.currentData()
        return data if data else ("sam2", se.SAM_KEYS[0])

    def _on_model_changed(self, _index):
        backend, key = self.current_backend()
        cloud = backend in ("replicate", "roboflow")
        self.label_weights.setVisible(not cloud)
        self.btn_download.setVisible(not cloud)
        self.label_api_key.setVisible(cloud)
        self.lineEdit_api_key.setVisible(cloud)
        self.label_api_link.setVisible(cloud)
        if cloud:
            self.label_api_link.setText(_t("api_replicate") if backend == "replicate" else _t("api_roboflow"))
            self.lineEdit_api_key.setText(QSettings().value(self._api_setting(backend), ""))
        else:
            self._refresh_weights_status()

    def _api_setting(self, backend):
        return "pyArchInit/sam2_replicate_api_key" if backend == "replicate" else "pyArchInit/sam3_roboflow_api_key"

    def _refresh_weights_status(self):
        backend, key = self.current_backend()
        if key is None:
            return
        missing = se.missing_weights(key)
        if missing:
            self.label_weights.setText(_t("weights_missing", sum(w.size_mb for w in missing)))
            self.label_weights.setStyleSheet("color: #b35c00;")
            self.btn_download.setEnabled(True)
        else:
            self.label_weights.setText(_t("weights_ok"))
            self.label_weights.setStyleSheet("color: green;")
            self.btn_download.setEnabled(False)

    def _on_target_changed(self, layer):
        us = is_us_layer(layer)
        self.us_widget.setVisible(us)
        self.label_field_label.setVisible(not us and layer is not None)
        self.comboBox_label_field.setVisible(not us and layer is not None)
        if layer is not None and not us:
            self.comboBox_label_field.setLayer(layer)
            names = [f.name().lower() for f in layer.fields()]
            for candidate in ("label", "etichetta", "classe", "class", "tipo", "nome"):
                if candidate in names:
                    self.comboBox_label_field.setField(layer.fields()[names.index(candidate)].name())
                    break

    def _load_site_from_config(self):
        try:
            config_path = os.path.join(pyarchinit_home(), "pyarchinit_DB_folder", "config.cfg")
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    config = eval(f.read())        # noqa: S307 - formato storico di pyArchInit
                self.lineEdit_site.setText(str(config.get("SITE_SET", "") or ""))
        except Exception as e:          # noqa: BLE001
            QgsMessageLog.logMessage(f"config.cfg: {e}", LOG, Qgis.Warning)

    def load_settings(self):
        s = QSettings()
        self.lineEdit_area.setText(s.value("pyArchInit/sam_last_area", ""))
        self.lineEdit_classes.setText(s.value("pyArchInit/sam_classes", DEFAULT_CLASSES) or DEFAULT_CLASSES)
        try:
            self.spin_max_side.setValue(int(s.value("pyArchInit/sam_max_side", rs.DEFAULT_MAX_SIDE)))
        except (TypeError, ValueError):
            pass

    def save_settings(self):
        s = QSettings()
        s.setValue("pyArchInit/sam_last_area", self.lineEdit_area.text())
        s.setValue("pyArchInit/sam_classes", self.lineEdit_classes.text())
        s.setValue("pyArchInit/sam_max_side", self.spin_max_side.value())
        backend, key = self.current_backend()
        if key:
            s.setValue("pyArchInit/sam_model_text" if backend == "yoloe" else "pyArchInit/sam_model", key)
        api_key = self.lineEdit_api_key.text().strip()
        if backend in ("replicate", "roboflow") and api_key:
            s.setValue(self._api_setting(backend), api_key)

    def _log(self, line):
        self.text_log.appendPlainText(line)
        QgsMessageLog.logMessage(line, LOG, Qgis.Info)

    # ------------------------------------------------------------------
    # Ambiente e pesi
    # ------------------------------------------------------------------
    def _check_environment(self):
        self.label_env.setText(_t("env_checking"))
        self.check_thread = _CheckThread(self)
        self.check_thread.done.connect(self._on_environment_checked)
        self.check_thread.start()

    def _on_environment_checked(self, ok, info):
        self.env_ready, self.env_info = ok, info
        if ok:
            self.label_env.setText(_t("env_ready", info))
            self.label_env.setStyleSheet("color: green;")
        else:
            self.label_env.setText(_t("env_missing"))
            self.label_env.setStyleSheet("color: #b35c00;")

    def install_environment(self):
        if self.setup_thread is not None and self.setup_thread.isRunning():
            return
        self.btn_install.setEnabled(False)
        self.btn_log.setChecked(True)
        self.label_env.setText(_t("env_installing"))
        self.setup_thread = se.SamSetupThread(self)
        self.setup_thread.log.connect(self._log)
        self.setup_thread.finished_ok.connect(self._on_install_finished)
        self.setup_thread.start()

    def _on_install_finished(self, ok, info):
        self.btn_install.setEnabled(True)
        self._on_environment_checked(ok, info)
        self._log(_t("installed", info) if ok else _t("install_failed", info))
        if not ok:
            QMessageBox.warning(self, _t("warn"), _t("install_failed", info))

    def download_weights(self):
        backend, key = self.current_backend()
        if key is None or (self.download_thread is not None and self.download_thread.isRunning()):
            return
        self.btn_download.setEnabled(False)
        self.progressBar.setRange(0, 100)
        self.progressBar.setVisible(True)
        self.download_thread = se.SamDownloadThread(key, self)
        self.download_thread.progress.connect(self._on_download_progress)
        self.download_thread.finished_ok.connect(self._on_download_finished)
        self.download_thread.start()

    def _on_download_progress(self, percent, text):
        self.progressBar.setValue(percent)
        self.label_status.setText(_t("downloading", text))

    def _on_download_finished(self, ok, info):
        self.progressBar.setVisible(False)
        self.progressBar.setRange(0, 0)
        self.label_status.setText(info)
        self._refresh_weights_status()
        if not ok:
            QMessageBox.warning(self, _t("warn"), info)

    # ------------------------------------------------------------------
    # Avvio
    # ------------------------------------------------------------------
    def _validate(self):
        raster = self.comboBox_raster.currentLayer()
        if raster is None:
            return _t("err_no_raster")
        if self._canvas() is None:
            return _t("err_no_canvas")
        backend, key = self.current_backend()
        mode = self.current_mode()
        if backend in ("replicate", "roboflow"):
            if not self.lineEdit_api_key.text().strip():
                return _t("err_no_key")
        else:
            if not self.env_ready:
                return _t("err_no_env")
            if se.missing_weights(key):
                return _t("err_no_weights")
        if mode == MODE_TEXT and not [c for c in self.lineEdit_classes.text().replace(";", ",").split(",") if c.strip()]:
            return _t("err_no_classes")
        if mode == MODE_LAYER and self.comboBox_polygon_layer.currentLayer() is None:
            return _t("err_no_polygon_layer")
        target = self.comboBox_target.currentLayer()
        if is_us_layer(target) and not self.lineEdit_area.text().strip():
            return _t("err_no_area")
        return None

    def on_segment_clicked(self):
        problem = self._validate()
        if problem:
            QMessageBox.warning(self, _t("warn"), problem)
            return
        self.save_settings()
        mode = self.current_mode()
        if mode in (MODE_POINTS, MODE_BOX, MODE_POLYGON):
            if not HAS_MAP_TOOLS:
                QMessageBox.warning(self, _t("warn"), "Map tools not available")
                return
            self._start_interactive_selection(mode)
            return
        if mode == MODE_LAYER:
            area = self._area_from_layer()
            if area is None:
                return
            self._run(mode, area=area)
            return
        self._run(mode)

    # --- strumenti di mappa -------------------------------------------
    def _start_interactive_selection(self, mode):
        canvas = self._canvas()
        self.previous_map_tool = canvas.mapTool()
        self.hide()
        if mode == MODE_POINTS:
            self.map_tool = SamPointMapTool(canvas, None, on_points_collected=self._on_points_collected,
                                            on_point_added=None, on_cancelled=self._on_selection_cancelled)
            iface.messageBar().pushInfo("SAM", _t("instr_points"))
        elif mode == MODE_BOX:
            self.map_tool = SamBoxMapTool(canvas, None, on_box_drawn=self._on_box_drawn,
                                          on_cancelled=self._on_selection_cancelled)
            iface.messageBar().pushInfo("SAM", _t("instr_box"))
        else:
            self.map_tool = SamPolygonMapTool(canvas, None, on_polygon_drawn=self._on_polygon_drawn,
                                              on_cancelled=self._on_selection_cancelled)
            iface.messageBar().pushInfo("SAM", _t("instr_polygon"))
        canvas.setMapTool(self.map_tool)

    def _restore_map_tool(self):
        canvas = self._canvas()
        if self.map_tool is not None:
            try:
                self.map_tool.deactivate()
            except Exception:          # noqa: BLE001
                pass
            self.map_tool = None
        if canvas is not None and self.previous_map_tool is not None:
            canvas.setMapTool(self.previous_map_tool)
            self.previous_map_tool = None

    def _on_selection_cancelled(self):
        self._restore_map_tool()
        self.show()
        self.label_status.setText(_t("cancelled"))

    def _on_points_collected(self, points):
        self._restore_map_tool()
        self.show()
        if not points:
            QMessageBox.warning(self, _t("warn"), _t("no_points"))
            return
        self._run(MODE_POINTS, prompts=[[float(x), float(y)] for x, y in points])

    def _on_box_drawn(self, boxes):
        self._restore_map_tool()
        self.show()
        if not boxes:
            QMessageBox.warning(self, _t("warn"), _t("no_box"))
            return
        self._run(MODE_BOX, prompts=[[float(v) for v in boxes[0]]])

    def _on_polygon_drawn(self, polygon_wkt):
        self._restore_map_tool()
        self.show()
        if not polygon_wkt:
            QMessageBox.warning(self, _t("warn"), _t("no_box"))
            return
        self._run(MODE_POLYGON, area=QgsGeometry.fromWkt(polygon_wkt))

    def _area_from_layer(self):
        layer = self.comboBox_polygon_layer.currentLayer()
        feats = layer.selectedFeatures() or list(layer.getFeatures())
        geoms = [f.geometry() for f in feats if f.geometry() is not None and not f.geometry().isEmpty()]
        if not geoms:
            QMessageBox.warning(self, _t("warn"), _t("err_no_features"))
            return None
        geom = QgsGeometry.unaryUnion(geoms) if len(geoms) > 1 else QgsGeometry(geoms[0])
        canvas_crs = self._canvas().mapSettings().destinationCrs()
        if layer.crs().isValid() and canvas_crs.isValid() and layer.crs() != canvas_crs:
            geom.transform(QgsCoordinateTransform(layer.crs(), canvas_crs, QgsProject.instance()))
        return geom

    # --- il lavoro ---------------------------------------------------------
    def _run(self, mode, prompts=None, area=None):
        """Prepara l'immagine (file o reso) e lancia il worker."""
        canvas = self._canvas()
        raster = self.comboBox_raster.currentLayer()
        canvas_crs = canvas.mapSettings().destinationCrs()
        backend, key = self.current_backend()
        self._set_busy(True, _t("preparing"))
        QApplication.processEvents()
        try:
            # l'estensione da usare, nel CRS della mappa
            if mode == MODE_BOX and prompts:
                x1, y1, x2, y2 = prompts[0]
                extent = QgsRectangle(min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
            elif mode in (MODE_POLYGON, MODE_LAYER) and area is not None:
                extent = area.boundingBox()
            elif self.radio_area_all.isChecked() and rs.is_file_raster(raster):
                extent = None
            else:
                extent = canvas.extent()
            if not rs.is_file_raster(raster):
                self.label_status.setText(_t("rendering"))
                QApplication.processEvents()
            image_path = os.path.join(self.work_dir, f"sam_{datetime.now().strftime('%H%M%S')}.png")
            image = rs.prepare_image(raster, extent, canvas_crs, image_path,
                                     map_units_per_pixel=self.spin_mupp.value(), max_side=self.spin_max_side.value())
            # area in CRS dell'immagine, e maschera fuori
            area_img = None
            if area is not None:
                area_img = rs.geometry_in_image_crs(area, canvas_crs, image)
                rs.mask_outside_polygon(image, area_img)
            # prompt in pixel
            worker_mode = "auto"
            prompts_file = None
            if mode == MODE_POINTS:
                pts = [rs.geometry_in_image_crs(QgsGeometry.fromPointXY(QgsPointXY(x, y)), canvas_crs, image).asPoint()
                       for x, y in prompts]
                pix = prompts_to_pixels(MODE_POINTS, [[p.x(), p.y()] for p in pts], image)
                if not pix["points"]:
                    raise ValueError(_t("no_points"))
                prompts_file = os.path.join(self.work_dir, "prompts.json")
                with open(prompts_file, "w", encoding="utf-8") as f:
                    json.dump(pix, f)
                worker_mode = "points"
            output = os.path.join(self.work_dir, f"result_{datetime.now().strftime('%H%M%S')}.json")
            classes = self.lineEdit_classes.text() if mode == MODE_TEXT else None
            cmd = se.worker_command(se.venv_python(), image.path, output, backend,
                                    weights=se.weight_path(key) if key else None, mode=worker_mode,
                                    prompts=prompts_file, classes=classes, conf=self.spin_conf.value(),
                                    imgsz=min(1024 if backend == "sam2" else 1280, max(image.width, image.height)),
                                    api_key=self.lineEdit_api_key.text().strip() if backend in ("replicate", "roboflow") else None)
        except Exception as e:          # noqa: BLE001
            self._set_busy(False, str(e))
            QMessageBox.warning(self, _t("warn"), str(e))
            return
        self._job = {"image": image, "area": area_img, "mode": mode, "backend": backend, "key": key,
                     "canvas_crs": canvas_crs}
        self.label_status.setText(_t("running"))
        self.worker = se.SamWorkerThread(cmd, output, parent=self)
        self.worker.progress.connect(self.label_status.setText)
        self.worker.finished_ok.connect(self._on_worker_finished)
        self.worker.start()

    def _set_busy(self, busy, text=""):
        self.btn_segment.setEnabled(not busy)
        self.btn_cancel.setVisible(busy)
        self.progressBar.setRange(0, 0)
        self.progressBar.setVisible(busy)
        if text:
            self.label_status.setText(text)

    def _cancel_running(self):
        for th in (self.worker, self.download_thread, self.setup_thread):
            if th is not None and th.isRunning():
                try:
                    th.cancel()
                except Exception:          # noqa: BLE001
                    pass
        self._set_busy(False, _t("cancelled"))

    def _on_worker_finished(self, ok, message, output):
        self._set_busy(False)
        if not ok:
            self.label_status.setText(_t("failed"))
            QMessageBox.warning(self, _t("failed"), message)
            return
        try:
            with open(output, encoding="utf-8") as f:
                result = json.load(f)
            added, target = self._add_results(result)
        except Exception as e:          # noqa: BLE001
            QgsMessageLog.logMessage(f"SAM results: {e}", LOG, Qgis.Critical)
            self.label_status.setText(_t("error"))
            QMessageBox.warning(self, _t("error"), str(e))
            return
        for w in result.get("warnings") or []:
            iface.messageBar().pushWarning("SAM", w)
        if added == 0:
            self.label_status.setText(_t("done_none"))
            QMessageBox.information(self, "SAM", _t("done_none"))
            return
        msg = _t("done", added, target.name(), result.get("model", ""))
        if is_us_layer(target):
            msg += " " + _t("us_edit_hint")
        self.label_status.setText(msg)
        iface.messageBar().pushSuccess("SAM", msg)

    def _add_results(self, result):
        """I poligoni del worker -> geometrie -> feature nel layer di destinazione."""
        job = self._job or {}
        image = job["image"]
        pairs = rs.polygons_to_geometries(result.get("polygons") or [], image.geotransform)
        pairs = rs.clip_to_area(pairs, job.get("area"))

        target = self.comboBox_target.currentLayer()
        new_layer = target is None
        if new_layer:
            raster = self.comboBox_raster.currentLayer()
            name = f"SAM_{raster.name() if raster else 'segmenti'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            target = new_memory_layer(name, image.crs)
        transform = None
        if image.crs.isValid() and target.crs().isValid() and image.crs != target.crs():
            transform = QgsCoordinateTransform(image.crs, target.crs(), QgsProject.instance())

        context = {"us_layer": is_us_layer(target), "site": self.lineEdit_site.text(),
                   "area": self.lineEdit_area.text(), "strat_index": self.spinBox_strat_index.value(),
                   "tipo_us": self.comboBox_tipo_us.currentText(), "source": result.get("model", ""),
                   "label_field": "label" if new_layer else self.comboBox_label_field.currentField(),
                   "default_label": None}
        fields = target.fields()
        features = []
        for poly, geom in pairs:
            geom = QgsGeometry(geom)
            if transform is not None:
                geom.transform(transform)
            feat = QgsFeature(fields)
            feat.setGeometry(geom)
            for k, v in feature_attributes(fields, poly, geom, context).items():
                feat.setAttribute(k, v)
            features.append(feat)

        if new_layer:
            target.dataProvider().addFeatures(features)
            target.updateExtents()
            QgsProject.instance().addMapLayer(target)
        elif features:
            if not target.isEditable():
                target.startEditing()
            target.addFeatures(features)
            if not target.commitChanges():
                errors = "; ".join(target.commitErrors())
                target.rollBack()
                raise ValueError(errors or "commit failed")
        target.triggerRepaint()
        return len(features), target

    # ------------------------------------------------------------------
    def reject(self):
        self._cancel_running()
        self._restore_map_tool()
        for th in (self.worker, self.download_thread, self.setup_thread, self.check_thread):
            if th is not None and th.isRunning():
                th.wait(3000)
        super().reject()
