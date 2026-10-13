"""La finestra «Stili delle viste» (spec 2026-10-13): per ogni vista di
pyArchInit si compone lo stile — simbologia con l'editor di QGIS,
etichette con un pannello nostro — con un'anteprima sui dati del sito
corrente; lo si salva nel database del progetto, lo si rende predefinito
per il sito o per tutti, lo si esporta e importa come QML, lo si applica
ai layer caricati. Il progetto non si tocca finché non lo si chiede.

I testi sono in ``_L`` (it/en). Le funzioni a livello di modulo (caricare
la vista, i preset di simbologia, trovare i layer del progetto) si provano
senza aprire la finestra.
"""
from __future__ import annotations

import colorsys
import os
import sys
from typing import List, Optional

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtWidgets import (QCheckBox, QColorDialog, QComboBox, QDialog, QDoubleSpinBox,
                                 QFileDialog, QFontComboBox, QHBoxLayout, QInputDialog, QLabel,
                                 QLineEdit, QListWidget, QListWidgetItem, QMessageBox, QPushButton,
                                 QSplitter, QTabWidget, QTreeWidget, QTreeWidgetItem, QVBoxLayout,
                                 QWidget)

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from modules.utility.view_styles import (GROUPS, PLACEMENTS, PRESETS, VIEWS, LabelRecipe,  # noqa: E402
                                         SavedStyle, ViewSpec, choose_style, default_recipe,
                                         group_label, view_by_name, view_label)
from modules.utility.view_styles_apply import (apply_recipe, export_qml_text,  # noqa: E402
                                               import_qml_text, recipe_from_layer, shipped_qml)
from modules.utility import view_styles_store as store  # noqa: E402


def _lang() -> str:
    try:
        from qgis.core import QgsSettings
        return (QgsSettings().value("locale/userLocale", "it", type=str) or "it")[:2]
    except Exception:                               # noqa: BLE001
        return "it"


_L = {
    "title": {"it": "Stili delle viste", "en": "View styles"},
    "views": {"it": "Viste", "en": "Views"},
    "styles": {"it": "Stili salvati", "en": "Saved styles"},
    "new": {"it": "Nuovo", "en": "New"},
    "duplicate": {"it": "Duplica", "en": "Duplicate"},
    "rename": {"it": "Rinomina…", "en": "Rename…"},
    "delete": {"it": "Elimina", "en": "Delete"},
    "default_site": {"it": "Predefinito per questo sito", "en": "Default for this site"},
    "default_all": {"it": "Predefinito per tutti i siti", "en": "Default for all sites"},
    "export": {"it": "Esporta QML…", "en": "Export QML…"},
    "import": {"it": "Importa QML…", "en": "Import QML…"},
    "apply": {"it": "Applica ai layer caricati", "en": "Apply to loaded layers"},
    "save": {"it": "Salva", "en": "Save"},
    "save_as": {"it": "Salva come…", "en": "Save as…"},
    "close": {"it": "Chiudi", "en": "Close"},
    "fit": {"it": "Inquadra", "en": "Zoom to data"},
    "symbology": {"it": "Simbologia", "en": "Symbology"},
    "labels": {"it": "Etichette", "en": "Labels"},
    "preset": {"it": "Preset:", "en": "Preset:"},
    "preset_keep": {"it": "— lascia com'è —", "en": "— keep as is —"},
    "preset_outline": {"it": "Solo contorno", "en": "Outline only"},
    "preset_shipped": {"it": "Stile fornito con pyArchInit", "en": "Style shipped with pyArchInit"},
    "preset_cat": {"it": "Categorie per «{field}»", "en": "Categories by “{field}”"},
    "labels_on": {"it": "Etichette attive", "en": "Labels on"},
    "label_preset": {"it": "Che cosa scrivere:", "en": "What to write:"},
    "lp_none": {"it": "Nessuna etichetta", "en": "No label"},
    "lp_us_circle": {"it": "Numero dell'unità in un cerchio", "en": "Unit number in a circle"},
    "lp_quota": {"it": "Quota sopra il simbolo", "en": "Elevation above the symbol"},
    "lp_field": {"it": "Un campo o un'espressione", "en": "A field or an expression"},
    "field": {"it": "Campo:", "en": "Field:"},
    "expression": {"it": "Espressione:", "en": "Expression:"},
    "placement": {"it": "Posizione:", "en": "Placement:"},
    "pl_centroid": {"it": "Al centro", "en": "Centred"},
    "pl_around_point": {"it": "Intorno al punto", "en": "Around the point"},
    "pl_above_symbol": {"it": "Sopra il simbolo", "en": "Above the symbol"},
    "offset": {"it": "Scostamento (mm):", "en": "Offset (mm):"},
    "one_per_unit": {"it": "Una etichetta per unità (sul disegno più grande che si vede)",
                     "en": "One label per unit (on the largest visible drawing)"},
    "text_format": {"it": "Carattere e sfondo", "en": "Font and background"},
    "font": {"it": "Carattere:", "en": "Font:"},
    "size": {"it": "Corpo (mm):", "en": "Size (mm):"},
    "bold": {"it": "Grassetto", "en": "Bold"},
    "color": {"it": "Colore…", "en": "Colour…"},
    "buffer": {"it": "Alone bianco", "en": "White buffer"},
    "circle": {"it": "Sfondo a cerchio", "en": "Circle background"},
    "circle_fill": {"it": "Riempimento…", "en": "Fill…"},
    "circle_stroke": {"it": "Bordo…", "en": "Stroke…"},
    "site_all": {"it": "tutti i siti", "en": "all sites"},
    "default_mark": {"it": "✓ predefinito", "en": "✓ default"},
    "not_in_db": {"it": "Vista non presente in questo database.", "en": "View not present in this database."},
    "no_geom": {"it": "Nessuna geometria per il sito corrente.", "en": "No geometry for the current site."},
    "no_db": {"it": "Database non collegato: gli stili si possono solo esportare.",
              "en": "Database not connected: styles can only be exported."},
    "no_table": {"it": "La tabella degli stili non si può creare in questo database: gli stili si possono solo esportare.",
                 "en": "The styles table cannot be created in this database: styles can only be exported."},
    "loaded": {"it": "{n} geometrie del sito «{site}».", "en": "{n} geometries of site “{site}”."},
    "loaded_all": {"it": "{n} geometrie (tutti i siti).", "en": "{n} geometries (all sites)."},
    "saved": {"it": "Stile «{name}» salvato.", "en": "Style “{name}” saved."},
    "applied": {"it": "Stile applicato a {n} layer del progetto.", "en": "Style applied to {n} project layers."},
    "applied_none": {"it": "Nessun layer di questa vista nel progetto.", "en": "No layer of this view in the project."},
    "exported": {"it": "QML scritto in {path}.", "en": "QML written to {path}."},
    "import_failed": {"it": "Il file «{name}» non si legge come QML.", "en": "“{name}” does not read as QML."},
    "name_prompt": {"it": "Nome dello stile:", "en": "Style name:"},
    "delete_confirm": {"it": "Eliminare lo stile «{name}»?", "en": "Delete the style “{name}”?"},
    "qml_filter": {"it": "Stile QGIS (*.qml)", "en": "QGIS style (*.qml)"},
    "legacy": {"it": "Salvato con QGIS", "en": "Saved with QGIS"},
    "no_style_selected": {"it": "Scegli prima uno stile salvato.", "en": "Choose a saved style first."},
}


def _t(key: str, lang: Optional[str] = None, **kw) -> str:
    voce = _L.get(key) or {}
    lingua = "it" if str(lang or _lang()).startswith("it") else "en"
    testo = voce.get(lingua) or voce.get("en") or key
    return testo.format(**kw) if kw else testo


# ---------------------------------------------------------------------------
# Senza finestra: caricare la vista, i preset, i layer del progetto
# ---------------------------------------------------------------------------

def load_view_layer(conn_str: str, spec: ViewSpec, site: Optional[str] = None, lang: Optional[str] = None):
    """La vista dal database, come layer **non** aggiunto al progetto,
    filtrata sul sito se la vista ha il campo. ``None`` se non c'è."""
    from qgis.core import QgsDataSourceUri, QgsVectorLayer
    from sqlalchemy.engine import make_url
    try:
        url = make_url(str(conn_str))
    except Exception:                               # noqa: BLE001
        return None
    nome = view_label(spec, lang)
    filtro = ""
    if site and spec.site_field:
        filtro = "%s = '%s'" % (spec.site_field, str(site).replace("'", "''"))
    if url.drivername.startswith("sqlite"):
        percorso = url.database or ""
        if not os.path.isfile(percorso):
            return None
        layer = QgsVectorLayer("%s|layername=%s" % (percorso, spec.name), nome, "ogr")
        if not layer.isValid():
            return None
        if filtro and spec.site_field in [f.name() for f in layer.fields()]:
            layer.setSubsetString(filtro)
    else:
        uri = QgsDataSourceUri()
        uri.setConnection(url.host or "", str(url.port or 5432), url.database or "",
                          url.username or "", url.password or "")
        uri.setDataSource("public", spec.name, "the_geom", filtro, "gid")
        layer = QgsVectorLayer(uri.uri(), nome, "postgres")
        if not layer.isValid():
            return None
    return layer


def outline_only_renderer(layer):
    """Solo il contorno (poligoni), una linea sottile (linee), un cerchietto
    vuoto (punti)."""
    from qgis.core import (QgsFillSymbol, QgsLineSymbol, QgsMarkerSymbol, QgsSingleSymbolRenderer,
                           QgsWkbTypes)
    tipo = layer.geometryType()
    if tipo == QgsWkbTypes.PolygonGeometry:
        simbolo = QgsFillSymbol.createSimple({"color": "0,0,0,0", "outline_color": "50,50,50,255",
                                              "outline_width": "0.3", "outline_style": "solid"})
    elif tipo == QgsWkbTypes.LineGeometry:
        simbolo = QgsLineSymbol.createSimple({"color": "50,50,50,255", "width": "0.4"})
    else:
        simbolo = QgsMarkerSymbol.createSimple({"color": "255,255,255,0", "outline_color": "50,50,50,255",
                                                "size": "2.5"})
    return QgsSingleSymbolRenderer(simbolo)


def categorized_renderer(layer, field: str):
    """Una categoria per ogni valore del campo, con colori pastello
    distanziati; ``None`` se il campo non c'è."""
    from qgis.core import QgsCategorizedSymbolRenderer, QgsRendererCategory, QgsSymbol
    from qgis.PyQt.QtGui import QColor
    indice = layer.fields().indexOf(field)
    if indice < 0:
        return None
    valori = sorted((str(v) for v in layer.uniqueValues(indice) if v not in (None, "")), key=str.lower)
    categorie = []
    for k, valore in enumerate(valori):
        simbolo = QgsSymbol.defaultSymbol(layer.geometryType())
        r, g, b = colorsys.hsv_to_rgb((k * 0.618033988749895) % 1.0, 0.45, 0.95)
        simbolo.setColor(QColor(int(r * 255), int(g * 255), int(b * 255)))
        categorie.append(QgsRendererCategory(valore, simbolo, valore))
    return QgsCategorizedSymbolRenderer(field, categorie)


def layer_is_view(layer, view_name: str) -> bool:
    """Vero se la sorgente del layer è questa vista (OGR o PostgreSQL):
    il nome intero, non un prefisso (revisione, I5: «doc_view» stava
    dentro «doc_view_b»)."""
    import re
    try:
        sorgente = str(layer.source() or "")
    except Exception:                               # noqa: BLE001
        return False
    nome = re.escape(view_name)
    return bool(re.search(r"layername=%s(?=$|\|)" % nome, sorgente)
                or re.search(r'"%s"' % nome, sorgente)
                or re.search(r"table=(?:\"public\"\.)?\"%s\"" % nome, sorgente))


def project_layers_of_view(view_name: str) -> List:
    from qgis.core import QgsProject, QgsVectorLayer
    return [l for l in QgsProject.instance().mapLayers().values()
            if isinstance(l, QgsVectorLayer) and layer_is_view(l, view_name)]


# ---------------------------------------------------------------------------
# La finestra
# ---------------------------------------------------------------------------

class ViewStylesDialog(QDialog):
    """Vedi il docstring del modulo. ``engine`` può essere ``None`` (niente
    stili salvati, solo esporta); ``view_name`` apre già su quella vista."""

    def __init__(self, iface=None, conn_str: str = "", site: Optional[str] = None, parent=None,
                 view_name: Optional[str] = None, engine=None, lang: Optional[str] = None):
        super().__init__(parent)
        self.iface = iface
        self.conn_str = str(conn_str or "")
        self.site = str(site).strip() if site else None
        self.lang = lang or _lang()
        self._engine = engine if engine is not None else self._apri_motore()
        self._spec: Optional[ViewSpec] = None
        self._layer = None
        self._stile: Optional[SavedStyle] = None
        self._editor = None
        self._formato_personalizzato = False
        self._zitto = False
        self.setObjectName("stili_delle_viste")
        self.setWindowTitle(_t("title", self.lang))
        self.resize(1180, 760)
        self._costruisci()
        self._riempi_viste()
        if view_name:
            self.select_view(view_name)

    # ---- costruzione -------------------------------------------------
    def _apri_motore(self):
        if not self.conn_str:
            return None
        self._motivo_senza_motore = "no_db"
        try:
            from sqlalchemy import create_engine
            motore = create_engine(self.conn_str)
        except Exception:                           # noqa: BLE001
            return None
        try:
            store.ensure_table(motore)
        except Exception:                           # noqa: BLE001
            self._motivo_senza_motore = "no_table"      # collegato, ma senza permesso di creare
            return None
        return motore

    def _costruisci(self):
        from qgis.gui import QgsMapCanvas
        radice = QVBoxLayout(self)
        divisore = QSplitter(Qt.Orientation.Horizontal, self)
        radice.addWidget(divisore, 1)

        # colonna sinistra: viste e stili salvati
        sinistra = QWidget(divisore)
        ls = QVBoxLayout(sinistra)
        ls.addWidget(QLabel(_t("views", self.lang)))
        self.viste = QTreeWidget(sinistra)
        self.viste.setObjectName("viste")
        self.viste.setHeaderHidden(True)
        self.viste.currentItemChanged.connect(lambda cur, _prev: self._vista_scelta(cur))
        ls.addWidget(self.viste, 2)
        ls.addWidget(QLabel(_t("styles", self.lang)))
        self.stili = QListWidget(sinistra)
        self.stili.setObjectName("stili")
        self.stili.currentItemChanged.connect(lambda cur, _prev: self._stile_scelto(cur))
        ls.addWidget(self.stili, 2)
        self.bottoni = {}
        for riga in (("new", "duplicate", "rename", "delete"),
                     ("default_site", "default_all"),
                     ("export", "import")):
            h = QHBoxLayout()
            for chiave in riga:
                b = QPushButton(_t(chiave, self.lang), sinistra)
                b.setObjectName({"new": "nuovo", "duplicate": "duplica", "rename": "rinomina",
                                 "delete": "elimina", "default_site": "predefinito_sito",
                                 "default_all": "predefinito_tutti", "export": "esporta",
                                 "import": "importa"}[chiave])
                self.bottoni[chiave] = b
                h.addWidget(b)
            ls.addLayout(h)
        self.bottoni["new"].clicked.connect(self._nuovo)
        self.bottoni["duplicate"].clicked.connect(self._duplica)
        self.bottoni["rename"].clicked.connect(self._rinomina)
        self.bottoni["delete"].clicked.connect(self._elimina)
        self.bottoni["default_site"].clicked.connect(lambda: self.set_default("site"))
        self.bottoni["default_all"].clicked.connect(lambda: self.set_default("all"))
        self.bottoni["export"].clicked.connect(self._esporta)
        self.bottoni["import"].clicked.connect(self._importa)

        # colonna destra: anteprima e schede
        destra = QWidget(divisore)
        ld = QVBoxLayout(destra)
        self.anteprima = QgsMapCanvas(destra)
        self.anteprima.setObjectName("anteprima")
        self.anteprima.setMinimumHeight(260)
        ld.addWidget(self.anteprima, 2)
        riga_stato = QHBoxLayout()
        self.stato = QLabel("", destra)
        self.stato.setObjectName("stato")
        riga_stato.addWidget(self.stato, 1)
        self.bottone_inquadra = QPushButton(_t("fit", self.lang), destra)
        self.bottone_inquadra.setObjectName("inquadra")
        self.bottone_inquadra.clicked.connect(self._inquadra)
        riga_stato.addWidget(self.bottone_inquadra)
        ld.addLayout(riga_stato)
        self.schede = QTabWidget(destra)
        self.schede.setObjectName("schede")
        ld.addWidget(self.schede, 3)
        self._costruisci_simbologia()
        self._costruisci_etichette()

        divisore.setStretchFactor(0, 1)
        divisore.setStretchFactor(1, 3)

        # in basso
        fondo = QHBoxLayout()
        self.bottone_applica = QPushButton(_t("apply", self.lang), self)
        self.bottone_applica.setObjectName("applica")
        self.bottone_applica.clicked.connect(self._applica_al_progetto)
        fondo.addWidget(self.bottone_applica)
        fondo.addStretch(1)
        self.bottone_salva = QPushButton(_t("save", self.lang), self)
        self.bottone_salva.setObjectName("salva")
        self.bottone_salva.clicked.connect(lambda: self.save())
        fondo.addWidget(self.bottone_salva)
        self.bottone_salva_come = QPushButton(_t("save_as", self.lang), self)
        self.bottone_salva_come.setObjectName("salva_come")
        self.bottone_salva_come.clicked.connect(self._salva_come)
        fondo.addWidget(self.bottone_salva_come)
        self.bottone_chiudi = QPushButton(_t("close", self.lang), self)
        self.bottone_chiudi.setObjectName("chiudi")
        self.bottone_chiudi.clicked.connect(self.close)
        fondo.addWidget(self.bottone_chiudi)
        radice.addLayout(fondo)
        if self._engine is None:
            self.stato.setText(_t(getattr(self, "_motivo_senza_motore", "no_db"), self.lang))

    def _costruisci_simbologia(self):
        pagina = QWidget(self.schede)
        lp = QVBoxLayout(pagina)
        riga = QHBoxLayout()
        riga.addWidget(QLabel(_t("preset", self.lang)))
        self.preset_simbologia = QComboBox(pagina)
        self.preset_simbologia.setObjectName("preset_simbologia")
        self.preset_simbologia.currentIndexChanged.connect(self._preset_simbologia_scelto)
        riga.addWidget(self.preset_simbologia, 1)
        lp.addLayout(riga)
        self.contenitore_editor = QVBoxLayout()
        lp.addLayout(self.contenitore_editor, 1)
        self.schede.addTab(pagina, _t("symbology", self.lang))

    def _costruisci_etichette(self):
        pagina = QWidget(self.schede)
        le = QVBoxLayout(pagina)
        self.etichette_attive = QCheckBox(_t("labels_on", self.lang), pagina)
        self.etichette_attive.setObjectName("etichette_attive")
        le.addWidget(self.etichette_attive)
        griglia = QHBoxLayout()
        griglia.addWidget(QLabel(_t("label_preset", self.lang)))
        self.preset_etichette = QComboBox(pagina)
        self.preset_etichette.setObjectName("preset_etichette")
        for chiave in PRESETS:
            self.preset_etichette.addItem(_t("lp_" + chiave, self.lang), chiave)
        griglia.addWidget(self.preset_etichette, 1)
        le.addLayout(griglia)
        riga_campo = QHBoxLayout()
        riga_campo.addWidget(QLabel(_t("field", self.lang)))
        self.campo_etichetta = QComboBox(pagina)
        self.campo_etichetta.setObjectName("campo_etichetta")
        riga_campo.addWidget(self.campo_etichetta, 1)
        riga_campo.addWidget(QLabel(_t("expression", self.lang)))
        self.espressione = QLineEdit(pagina)
        self.espressione.setObjectName("espressione")
        riga_campo.addWidget(self.espressione, 2)
        le.addLayout(riga_campo)
        riga_pos = QHBoxLayout()
        riga_pos.addWidget(QLabel(_t("placement", self.lang)))
        self.posizione = QComboBox(pagina)
        self.posizione.setObjectName("posizione")
        for chiave in PLACEMENTS:
            self.posizione.addItem(_t("pl_" + chiave, self.lang), chiave)
        riga_pos.addWidget(self.posizione, 1)
        riga_pos.addWidget(QLabel(_t("offset", self.lang)))
        self.scostamento = QDoubleSpinBox(pagina)
        self.scostamento.setObjectName("scostamento")
        self.scostamento.setRange(0.0, 50.0)
        self.scostamento.setSingleStep(0.5)
        riga_pos.addWidget(self.scostamento)
        le.addLayout(riga_pos)
        self.una_per_unita = QCheckBox(_t("one_per_unit", self.lang), pagina)
        self.una_per_unita.setObjectName("una_per_unita")
        le.addWidget(self.una_per_unita)
        le.addWidget(QLabel(_t("text_format", self.lang)))
        self._costruisci_formato(pagina, le)
        le.addStretch(1)
        self.schede.addTab(pagina, _t("labels", self.lang))
        for segnale in (self.etichette_attive.toggled, self.preset_etichette.currentIndexChanged,
                        self.campo_etichetta.currentIndexChanged, self.espressione.editingFinished,
                        self.posizione.currentIndexChanged, self.scostamento.valueChanged,
                        self.una_per_unita.toggled):
            segnale.connect(self._etichette_cambiate)

    def _costruisci_formato(self, pagina, layout):
        """Il carattere delle etichette, con controlli nostri: il
        `QgsTextFormatWidget` di QGIS va in segfault fuori dall'applicazione."""
        riga = QHBoxLayout()
        riga.addWidget(QLabel(_t("font", self.lang)))
        self.carattere = QFontComboBox(pagina)
        self.carattere.setObjectName("carattere")
        riga.addWidget(self.carattere, 2)
        riga.addWidget(QLabel(_t("size", self.lang)))
        self.corpo_mm = QDoubleSpinBox(pagina)
        self.corpo_mm.setObjectName("corpo_mm")
        self.corpo_mm.setRange(0.5, 30.0)
        self.corpo_mm.setSingleStep(0.5)
        self.corpo_mm.setValue(2.2)
        riga.addWidget(self.corpo_mm)
        self.grassetto = QCheckBox(_t("bold", self.lang), pagina)
        self.grassetto.setObjectName("grassetto")
        riga.addWidget(self.grassetto)
        layout.addLayout(riga)
        riga2 = QHBoxLayout()
        self._colori = {"testo": QColor("#1A1A1A"), "sfondo": QColor("#FFFFFF"), "bordo": QColor("#7A2020")}
        self.colore_testo = QPushButton(_t("color", self.lang), pagina)
        self.colore_testo.setObjectName("colore_testo")
        self.colore_testo.clicked.connect(lambda: self._scegli_colore("testo"))
        riga2.addWidget(self.colore_testo)
        self.alone = QCheckBox(_t("buffer", self.lang), pagina)
        self.alone.setObjectName("alone")
        riga2.addWidget(self.alone)
        self.sfondo_cerchio = QCheckBox(_t("circle", self.lang), pagina)
        self.sfondo_cerchio.setObjectName("sfondo_cerchio")
        riga2.addWidget(self.sfondo_cerchio)
        self.colore_sfondo = QPushButton(_t("circle_fill", self.lang), pagina)
        self.colore_sfondo.setObjectName("colore_sfondo")
        self.colore_sfondo.clicked.connect(lambda: self._scegli_colore("sfondo"))
        riga2.addWidget(self.colore_sfondo)
        self.colore_bordo = QPushButton(_t("circle_stroke", self.lang), pagina)
        self.colore_bordo.setObjectName("colore_bordo")
        self.colore_bordo.clicked.connect(lambda: self._scegli_colore("bordo"))
        riga2.addWidget(self.colore_bordo)
        riga2.addStretch(1)
        layout.addLayout(riga2)
        for segnale in (self.carattere.currentFontChanged, self.corpo_mm.valueChanged,
                        self.grassetto.toggled, self.alone.toggled, self.sfondo_cerchio.toggled):
            segnale.connect(self._formato_cambiato)

    def _scegli_colore(self, chiave: str):
        colore = QColorDialog.getColor(self._colori[chiave], self, _t("color", self.lang))
        if colore.isValid():
            self._colori[chiave] = colore
            self._formato_cambiato()

    def text_format(self):
        """Il `QgsTextFormat` composto dai controlli."""
        from qgis.core import QgsTextBackgroundSettings, QgsTextBufferSettings, QgsTextFormat, QgsUnitTypes
        from qgis.PyQt.QtCore import QSizeF
        formato = QgsTextFormat()
        carattere = self.carattere.currentFont()
        carattere.setBold(self.grassetto.isChecked())
        formato.setFont(carattere)
        formato.setSize(float(self.corpo_mm.value()))
        formato.setSizeUnit(QgsUnitTypes.RenderUnit.RenderMillimeters)
        formato.setColor(self._colori["testo"])
        alone = QgsTextBufferSettings()
        alone.setEnabled(self.alone.isChecked())
        alone.setSize(0.6)
        alone.setSizeUnit(QgsUnitTypes.RenderUnit.RenderMillimeters)
        alone.setColor(QColor("#FFFFFF"))
        formato.setBuffer(alone)
        sfondo = QgsTextBackgroundSettings()
        sfondo.setEnabled(self.sfondo_cerchio.isChecked())
        sfondo.setType(QgsTextBackgroundSettings.ShapeType.ShapeCircle)
        sfondo.setSizeType(QgsTextBackgroundSettings.SizeType.SizeBuffer)
        sfondo.setSize(QSizeF(0.9, 0.9))
        sfondo.setSizeUnit(QgsUnitTypes.RenderUnit.RenderMillimeters)
        sfondo.setFillColor(self._colori["sfondo"])
        sfondo.setStrokeColor(self._colori["bordo"])
        sfondo.setStrokeWidth(0.25)
        sfondo.setStrokeWidthUnit(QgsUnitTypes.RenderUnit.RenderMillimeters)
        formato.setBackground(sfondo)
        return formato

    def set_text_format(self, size_mm=None, bold=None, color=None, circle=None, buffer=None):
        """Per i test e per chi vuole comporre da codice."""
        self._zitto = True
        if size_mm is not None:
            self.corpo_mm.setValue(float(size_mm))
        if bold is not None:
            self.grassetto.setChecked(bool(bold))
        if color is not None:
            self._colori["testo"] = QColor(color)
        if circle is not None:
            self.sfondo_cerchio.setChecked(bool(circle))
        if buffer is not None:
            self.alone.setChecked(bool(buffer))
        self._zitto = False
        self._formato_cambiato()

    # ---- l'elenco delle viste ----------------------------------------
    def _riempi_viste(self):
        self.viste.clear()
        gruppi = {}
        for chiave in GROUPS:
            voce = QTreeWidgetItem(self.viste, [group_label(chiave, self.lang)])
            voce.setFlags(voce.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            voce.setExpanded(True)
            gruppi[chiave] = voce
        for spec in VIEWS:
            voce = QTreeWidgetItem(gruppi[spec.group], [view_label(spec, self.lang)])
            voce.setData(0, Qt.ItemDataRole.UserRole, spec.name)

    def _voce_vista(self, name: str):
        for i in range(self.viste.topLevelItemCount()):
            gruppo = self.viste.topLevelItem(i)
            for k in range(gruppo.childCount()):
                voce = gruppo.child(k)
                if voce.data(0, Qt.ItemDataRole.UserRole) == name:
                    return voce
        return None

    def select_view(self, name: str) -> bool:
        voce = self._voce_vista(name)
        if voce is None:
            return False
        self.viste.setCurrentItem(voce)
        if self._spec is None or self._spec.name != name:
            self._vista_scelta(voce)
        return True

    def _mostra_stato(self, testo: str):
        """La riga di stato; senza il motore degli stili porta anche il perché
        (prima i due messaggi del database venivano coperti dal conteggio
        alla prima vista scelta, cioè sempre)."""
        if self._engine is None:
            testo = "%s %s" % (testo, _t(getattr(self, "_motivo_senza_motore", "no_db"), self.lang))
        self.stato.setText(testo)

    def _vista_scelta(self, voce):
        if voce is None or not voce.data(0, Qt.ItemDataRole.UserRole):
            return
        spec = view_by_name(voce.data(0, Qt.ItemDataRole.UserRole))
        if spec is None:
            return
        self._spec = spec
        self._stile = None
        self._formato_personalizzato = False
        self._layer = load_view_layer(self.conn_str, spec, self.site, self.lang)
        if self._layer is None:
            voce.setForeground(0, Qt.GlobalColor.gray)
            self._mostra_stato(_t("not_in_db", self.lang))
            self.anteprima.setLayers([])
            self.anteprima.refresh()
        else:
            n = self._layer.featureCount()
            if n <= 0:
                self._mostra_stato(_t("no_geom", self.lang))
            elif self.site and spec.site_field:
                self._mostra_stato(_t("loaded", self.lang, n=n, site=self.site))
            else:
                self._mostra_stato(_t("loaded_all", self.lang, n=n))
            from modules.utility.view_styles_apply import apply_view_style
            apply_view_style(self._layer, spec.name, self.site, engine=self._engine)
            self.anteprima.setDestinationCrs(self._layer.crs())
            self.anteprima.setLayers([self._layer])
            self._inquadra()
        self._riempi_preset_simbologia()
        self._ricostruisci_editor()
        self._riempi_campi()
        self._mostra_ricetta(default_recipe(spec) if self._layer is None else self._ricetta_del_layer())
        self.refresh_styles()

    def _ricetta_del_layer(self) -> LabelRecipe:
        """La ricetta che `apply_view_style` ha appena applicato: quella dello
        stile salvato predefinito, o quella di partenza."""
        if self._engine is not None and self._spec is not None:
            try:
                scelto = choose_style(store.list_styles(self._engine, self._spec.name), self.site)
            except Exception:                       # noqa: BLE001
                scelto = None
            if scelto is not None:
                self._stile = scelto
                return scelto.recipe
        return default_recipe(self._spec)

    # ---- simbologia --------------------------------------------------
    def _riempi_preset_simbologia(self):
        self._zitto = True
        self.preset_simbologia.clear()
        self.preset_simbologia.addItem(_t("preset_keep", self.lang), "")
        self.preset_simbologia.addItem(_t("preset_outline", self.lang), "outline")
        if self._spec is not None and shipped_qml(self._spec):
            self.preset_simbologia.addItem(_t("preset_shipped", self.lang), "shipped")
        campi = [f.name() for f in self._layer.fields()] if self._layer is not None else []
        for campo in (self._spec.category_fields if self._spec else ()):
            if campo in campi:
                self.preset_simbologia.addItem(_t("preset_cat", self.lang, field=campo), "cat:" + campo)
        self._zitto = False

    def _preset_simbologia_scelto(self, _indice):
        if self._zitto:
            return
        chiave = self.preset_simbologia.currentData()
        if chiave:
            self.apply_symbology_preset(chiave)

    def apply_symbology_preset(self, chiave: str) -> bool:
        if self._layer is None:
            return False
        if chiave == "outline":
            self._layer.setRenderer(outline_only_renderer(self._layer))
        elif chiave == "shipped":
            qml = shipped_qml(self._spec)
            if not qml:
                return False
            ricetta = self.current_recipe()
            self._layer.loadNamedStyle(qml)
            apply_recipe(self._layer, ricetta, touch_when_off=True)
        elif chiave.startswith("cat:"):
            renderer = categorized_renderer(self._layer, chiave[4:])
            if renderer is None:
                return False
            self._layer.setRenderer(renderer)
        else:
            return False
        self._ricostruisci_editor()
        self._aggiorna_anteprima()
        return True

    def _ricostruisci_editor(self):
        from qgis.core import QgsStyle
        from qgis.gui import QgsRendererPropertiesDialog
        if self._editor is not None:
            self.contenitore_editor.removeWidget(self._editor)
            self._editor.setParent(None)
            self._editor.deleteLater()
            self._editor = None
        if self._layer is None:
            return
        self._editor = QgsRendererPropertiesDialog(self._layer, QgsStyle.defaultStyle(), True, self)
        self._editor.setObjectName("editor_simbologia")
        try:
            self._editor.setMapCanvas(self.anteprima)
        except Exception:                           # noqa: BLE001
            pass
        self._editor.widgetChanged.connect(self._editor_cambiato)
        self.contenitore_editor.addWidget(self._editor)

    def _editor_cambiato(self):
        if self._editor is None:
            return
        try:
            self._editor.apply()
        except Exception:                           # noqa: BLE001
            return
        self._aggiorna_anteprima()

    # ---- etichette ---------------------------------------------------
    def _riempi_campi(self):
        from modules.utility.atlas_labels import US_GROUP_FIELDS, US_GROUP_FIELDS_ALT
        self._zitto = True
        self.campo_etichetta.clear()
        self.campo_etichetta.addItem("", "")
        campi = []
        if self._layer is not None:
            for f in self._layer.fields():
                self.campo_etichetta.addItem(f.name(), f.name())
                campi.append(f.name())
        raggruppabile = any(set(coppia) <= set(campi) for coppia in (US_GROUP_FIELDS, US_GROUP_FIELDS_ALT))
        self.una_per_unita.setEnabled(raggruppabile)
        if not raggruppabile:
            self.una_per_unita.setChecked(False)
        self._zitto = False

    def _mostra_ricetta(self, ricetta: LabelRecipe):
        self._zitto = True
        self.etichette_attive.setChecked(bool(ricetta.enabled))
        self.preset_etichette.setCurrentIndex(max(0, self.preset_etichette.findData(ricetta.preset)))
        campo = ricetta.expression or ""
        i = self.campo_etichetta.findData(campo)
        self.campo_etichetta.setCurrentIndex(i if i >= 0 else 0)
        self.espressione.setText("" if i >= 0 else campo)
        self.posizione.setCurrentIndex(max(0, self.posizione.findData(ricetta.placement)))
        self.scostamento.setValue(float(ricetta.offset_mm or 0.0))
        self.una_per_unita.setChecked(bool(ricetta.one_per_unit))
        self._zitto = False
        self._aggiorna_formato_dal_layer()

    def current_recipe(self) -> LabelRecipe:
        espressione = self.espressione.text().strip() or (self.campo_etichetta.currentData() or "")
        return LabelRecipe(enabled=self.etichette_attive.isChecked(),
                           preset=self.preset_etichette.currentData() or "none",
                           expression=espressione or None,
                           placement=self.posizione.currentData() or "centroid",
                           offset_mm=float(self.scostamento.value()),
                           one_per_unit=self.una_per_unita.isChecked())

    def apply_label_preset(self, preset: str):
        self._zitto = True
        self.preset_etichette.setCurrentIndex(max(0, self.preset_etichette.findData(preset)))
        self.etichette_attive.setChecked(preset != "none")
        if preset == "us_circle":
            self.una_per_unita.setChecked(True)
        if preset == "quota":
            self.posizione.setCurrentIndex(max(0, self.posizione.findData("above_symbol")))
        self._zitto = False
        self._etichette_cambiate()

    def _etichette_cambiate(self, *_args):
        if self._zitto or self._layer is None:
            return
        ricetta = self.current_recipe()
        apply_recipe(self._layer, ricetta, touch_when_off=True)
        if self._formato_personalizzato:
            self._applica_formato()
        else:
            self._aggiorna_formato_dal_layer()
        self._aggiorna_anteprima()

    def _aggiorna_formato_dal_layer(self):
        """I controlli del carattere leggono il formato che il layer ha
        adesso (quello della ricetta appena applicata)."""
        if self._layer is None:
            return
        etichettatura = self._layer.labeling()
        if etichettatura is None:
            return
        try:
            self._zitto = True
            impostazioni = etichettatura.settings()
            formato = impostazioni.format()
            self.carattere.setCurrentFont(formato.font())
            if formato.size() > 0:
                self.corpo_mm.setValue(float(formato.size()))
            self.grassetto.setChecked(bool(formato.font().bold()))
            self._colori["testo"] = QColor(formato.color())
            self.alone.setChecked(bool(formato.buffer().enabled()))
            sfondo = formato.background()
            self.sfondo_cerchio.setChecked(bool(sfondo.enabled()))
            if sfondo.enabled():
                self._colori["sfondo"] = QColor(sfondo.fillColor())
                self._colori["bordo"] = QColor(sfondo.strokeColor())
        except Exception:                           # noqa: BLE001
            pass
        finally:
            self._zitto = False

    def _formato_cambiato(self, *_args):
        if self._zitto or self._layer is None:
            return
        self._formato_personalizzato = True
        self._applica_formato()
        self._aggiorna_anteprima()

    def _applica_formato(self):
        from qgis.core import QgsVectorLayerSimpleLabeling
        etichettatura = self._layer.labeling()
        if etichettatura is None:
            return
        impostazioni = etichettatura.settings()
        impostazioni.setFormat(self.text_format())
        self._layer.setLabeling(QgsVectorLayerSimpleLabeling(impostazioni))

    # ---- anteprima ---------------------------------------------------
    def _aggiorna_anteprima(self):
        if self._layer is not None:
            self._layer.triggerRepaint()
        self.anteprima.refresh()

    def _inquadra(self):
        if self._layer is None:
            return
        self.anteprima.setExtent(self._layer.extent())
        self.anteprima.refresh()

    def current_layer(self):
        return self._layer

    # ---- stili salvati -----------------------------------------------
    def refresh_styles(self):
        self.stili.clear()
        if self._engine is None or self._spec is None:
            return
        try:
            elenco = store.list_styles(self._engine, self._spec.name)
        except Exception:                           # noqa: BLE001
            elenco = []
        for stile in elenco:
            sito = _t("site_all", self.lang) if stile.for_all_sites else str(stile.site)
            testo = "%s · %s" % (stile.name, sito)
            if stile.is_default:
                testo += " · " + _t("default_mark", self.lang)
            voce = QListWidgetItem(testo, self.stili)
            voce.setData(Qt.ItemDataRole.UserRole, stile.id)
            if self._stile is not None and stile.id == self._stile.id:
                self.stili.blockSignals(True)           # evidenzia senza ricaricare (revisione, M9)
                self.stili.setCurrentItem(voce)
                self.stili.blockSignals(False)
        if self._layer is not None:
            for sid, nome in store.legacy_qgis_styles(self._layer):
                voce = QListWidgetItem("%s · %s" % (nome, _t("legacy", self.lang)), self.stili)
                voce.setData(Qt.ItemDataRole.UserRole, "qgis:%s" % sid)

    def _stile_scelto(self, voce):
        if voce is None or self._layer is None:
            return
        dato = voce.data(Qt.ItemDataRole.UserRole)
        if isinstance(dato, str) and dato.startswith("qgis:"):
            try:
                xml = self._layer.getStyleFromDatabase(dato[5:])[0]
            except Exception:                       # noqa: BLE001
                return
            if xml and import_qml_text(self._layer, xml):
                self._stile = None
                self._formato_personalizzato = False
                self._ricostruisci_editor()
                self._mostra_ricetta(recipe_from_layer(self._layer))
                self._aggiorna_anteprima()
            return
        stile = self._stile_per_id(dato)
        if stile is not None:
            self.load_style(stile)

    def _stile_per_id(self, sid) -> Optional[SavedStyle]:
        if self._engine is None or self._spec is None:
            return None
        try:
            return next((s for s in store.list_styles(self._engine, self._spec.name) if s.id == sid), None)
        except Exception:                           # noqa: BLE001
            return None

    def load_style(self, stile: SavedStyle):
        if self._layer is None:
            return
        self._stile = stile
        self._formato_personalizzato = False
        import_qml_text(self._layer, stile.qml)
        apply_recipe(self._layer, stile.recipe, touch_when_off=False, keep_format=True)
        self._ricostruisci_editor()
        self._mostra_ricetta(stile.recipe)
        self._aggiorna_anteprima()

    def _avvisa(self, testo: str, warning: bool = False):
        """Nella riga di stato sempre; in una finestra solo se la finestra
        si vede (una modale senza nessuno davanti blocca tutto)."""
        self.stato.setText(testo)
        if self.isVisible():
            (QMessageBox.warning if warning else QMessageBox.information)(self, _t("title", self.lang), testo)

    def _stile_corrente_o_avviso(self) -> Optional[SavedStyle]:
        voce = self.stili.currentItem()
        stile = self._stile_per_id(voce.data(Qt.ItemDataRole.UserRole)) if voce is not None else self._stile
        if stile is None:
            self._avvisa(_t("no_style_selected", self.lang))
        return stile

    def save(self, name: Optional[str] = None, site: Optional[str] = "__corrente__") -> Optional[int]:
        """Salva lo stile composto: sullo stile corrente, o come nuovo con
        ``name``. ``site`` ``"__corrente__"`` = come lo stile corrente (o
        «tutti» per uno nuovo); ``None`` = tutti i siti; un nome = quel sito."""
        if self._engine is None or self._layer is None or self._spec is None:
            return None
        if self._stile is None and name is None:
            name, ok = QInputDialog.getText(self, _t("title", self.lang), _t("name_prompt", self.lang))
            if not ok or not str(name).strip():
                return None
        if self._stile is not None and name is None:
            stile = self._stile
        else:
            sito = (self._stile.site if (self._stile is not None and site == "__corrente__") else
                    (None if site in (None, "__corrente__") else site))
            stile = SavedStyle(None, self._spec.name, sito, str(name).strip(), "", LabelRecipe())
        stile.qml = export_qml_text(self._layer)
        stile.recipe = self.current_recipe()
        if not stile.author:
            try:
                import getpass
                stile.author = getpass.getuser()
            except Exception:                       # noqa: BLE001
                stile.author = ""
        store.save_style(self._engine, stile)
        self._stile = stile
        self.refresh_styles()
        self.stato.setText(_t("saved", self.lang, name=stile.name))
        return stile.id

    def _salva_come(self):
        name, ok = QInputDialog.getText(self, _t("title", self.lang), _t("name_prompt", self.lang))
        if ok and str(name).strip():
            self.save(str(name).strip(), None)

    def _nuovo(self):
        if self._spec is None or self._layer is None:
            return
        self._stile = None
        self.stili.setCurrentItem(None)
        self.apply_symbology_preset("outline")
        self._mostra_ricetta(default_recipe(self._spec))
        self._etichette_cambiate()

    def _duplica(self):
        stile = self._stile_corrente_o_avviso()
        if stile is None:
            return
        copia = SavedStyle(None, stile.view_name, stile.site, stile.name + " (2)", stile.qml, stile.recipe,
                           False, stile.author)
        store.save_style(self._engine, copia)
        self._stile = copia
        self.refresh_styles()

    def _rinomina(self):
        stile = self._stile_corrente_o_avviso()
        if stile is None:
            return
        name, ok = QInputDialog.getText(self, _t("title", self.lang), _t("name_prompt", self.lang), text=stile.name)
        if ok and str(name).strip():
            store.rename_style(self._engine, stile.id, str(name).strip())
            self.refresh_styles()

    def _elimina(self):
        stile = self._stile_corrente_o_avviso()
        if stile is None:
            return
        if QMessageBox.question(self, _t("title", self.lang), _t("delete_confirm", self.lang, name=stile.name),
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) \
                != QMessageBox.StandardButton.Yes:
            return
        store.delete_style(self._engine, stile.id)
        if self._stile is not None and self._stile.id == stile.id:
            self._stile = None
        self.refresh_styles()

    def set_default(self, scope: str = "site") -> bool:
        """Lo stile corrente diventa il predefinito del sito corrente
        (``scope="site"``) o di tutti i siti (``"all"``): se il suo ambito
        è diverso, il predefinito nuovo è una copia nell'ambito nuovo e
        l'originale resta dov'è."""
        if self._engine is None:
            return False
        stile = self._stile_corrente_o_avviso()
        if stile is None:
            return False
        nuovo_sito = self.site if scope == "site" else None
        if scope == "site" and not self.site:
            return False
        if (stile.site or None) != nuovo_sito:
            # l'ambito cambia: lo stile di prima resta dov'è, il predefinito
            # nuovo è una copia nell'ambito nuovo (revisione, M2)
            stile = SavedStyle(None, stile.view_name, nuovo_sito, stile.name, stile.qml, stile.recipe,
                               False, stile.author)
            store.save_style(self._engine, stile)
        store.set_default(self._engine, stile.id)
        self._stile = stile
        self.refresh_styles()
        return True

    def export_qml(self, path: str) -> bool:
        if self._layer is None:
            return False
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(export_qml_text(self._layer))
        self.stato.setText(_t("exported", self.lang, path=path))
        return True

    def import_qml(self, path: str) -> Optional[int]:
        """Un QML come stile nuovo (nome del file), applicato all'anteprima."""
        if self._layer is None or self._spec is None:
            return None
        try:
            with open(path, "r", encoding="utf-8") as fh:
                testo = fh.read()
        except OSError:
            testo = ""
        if not testo or not import_qml_text(self._layer, testo):
            self._avvisa(_t("import_failed", self.lang, name=os.path.basename(path)), warning=True)
            return None
        self._formato_personalizzato = False
        self._ricostruisci_editor()
        self._mostra_ricetta(recipe_from_layer(self._layer))
        self._aggiorna_anteprima()
        nome = os.path.splitext(os.path.basename(path))[0]
        if self._engine is None:
            return None
        stile = SavedStyle(None, self._spec.name, None, nome, export_qml_text(self._layer), self.current_recipe())
        store.save_style(self._engine, stile)
        self._stile = stile
        self.refresh_styles()
        return stile.id

    def _esporta(self):
        if self._spec is None:
            return
        percorso, _f = QFileDialog.getSaveFileName(self, _t("export", self.lang), self._spec.name + ".qml",
                                                   _t("qml_filter", self.lang))
        if percorso:
            if not percorso.lower().endswith(".qml"):
                percorso += ".qml"
            self.export_qml(percorso)

    def _importa(self):
        percorso, _f = QFileDialog.getOpenFileName(self, _t("import", self.lang), "", _t("qml_filter", self.lang))
        if percorso:
            self.import_qml(percorso)

    # ---- il progetto -------------------------------------------------
    def apply_to_project(self) -> int:
        """Lo stile composto sui layer del progetto che vengono da questa
        vista: QML più ricetta (ricalcolata su ciascuno)."""
        if self._layer is None or self._spec is None:
            return 0
        qml = export_qml_text(self._layer)
        ricetta = self.current_recipe()
        quanti = 0
        for layer in project_layers_of_view(self._spec.name):
            if import_qml_text(layer, qml):
                apply_recipe(layer, ricetta, touch_when_off=False, keep_format=True)
                layer.triggerRepaint()
                quanti += 1
        return quanti

    def _applica_al_progetto(self):
        n = self.apply_to_project()
        self.stato.setText(_t("applied", self.lang, n=n) if n else _t("applied_none", self.lang))
        try:
            if self.iface is not None:
                self.iface.mapCanvas().refresh()
        except Exception:                           # noqa: BLE001
            pass

    def dispose(self):
        """Lascia andare il layer, l'editor e il canvas prima che se ne vada
        l'applicazione: distrutti dopo, QGIS crolla all'uscita."""
        try:
            self.anteprima.setLayers([])
        except Exception:                           # noqa: BLE001
            pass
        self._layer = None
        try:
            self._ricostruisci_editor()
        except Exception:                           # noqa: BLE001
            pass
        self._stile = None

    def closeEvent(self, event):
        self.dispose()
        super().closeEvent(event)


def view_name_of_layer(layer) -> Optional[str]:
    """La vista del registro da cui viene il layer, o None."""
    if layer is None:
        return None
    for spec in VIEWS:
        if layer_is_view(layer, spec.name):
            return spec.name
    return None


def _config_site() -> Optional[str]:
    """Il sito impostato in config.cfg (SITE_SET), o None."""
    try:
        from modules.utility.pyarchinit_home import pyarchinit_home
        from modules.utility.settings import Settings
        percorso = os.path.join(pyarchinit_home(), "pyarchinit_DB_folder", "config.cfg")
        with open(percorso, "r") as conf:
            settings = Settings(conf.read())
        settings.set_configuration()
        sito = str(getattr(settings, "SITE_SET", "") or "").strip()
        return sito or None
    except Exception:                               # noqa: BLE001
        return None


def open_view_styles(iface, parent=None, site: Optional[str] = None, view_name: Optional[str] = None,
                     conn_str: Optional[str] = None, active_layer=None, show: bool = True,
                     lang: Optional[str] = None):
    """La porta unica: dal menu del plugin, dal menu del layer e dalla
    scheda US. Non modale; la finestra resta appesa a chi l'ha aperta."""
    if conn_str is None:
        try:
            from modules.db.pyarchinit_conn_strings import Connection
            conn_str = Connection().conn_str()
        except Exception:                           # noqa: BLE001
            conn_str = ""
    if site is None:
        site = _config_site()
    if view_name is None and active_layer is not None:
        view_name = view_name_of_layer(active_layer)
    if view_name is None:
        view_name = "pyarchinit_us_view"
    padrone = parent if parent is not None else (iface.mainWindow() if iface is not None else None)
    dlg = ViewStylesDialog(iface, conn_str, site, padrone, view_name=view_name, lang=lang)
    if padrone is not None:
        try:
            setattr(padrone, "_pyarchinit_view_styles", dlg)
        except Exception:                           # noqa: BLE001
            pass
    if show:
        dlg.show()
        dlg.raise_()
    return dlg
