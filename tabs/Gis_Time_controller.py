#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
/***************************************************************************
        pyArchInit Plugin  - A QGIS plugin to manage archaeological dataset
                             stored in Postgres
                             -------------------
    begin                : 2007-12-01
    copyright            : (C) 2008 by Luca Mandolesi; Enzo Cocca <enzo.ccc@gmail.com>
    email                : mandoluca at gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from __future__ import absolute_import

import platform
import subprocess, sys
try:
    import psutil


except ImportError:
    print("openai is not installed, installing...")
    if sys.platform.startswith("win"):
        subprocess.call(["pip", "install", "psutil"],shell = False)
    elif sys.platform.startswith("darwin"):
        subprocess.call([ "/Applications/QGIS.app/Contents/MacOS/bin/python3", "-m", "pip","install", "psutil"],shell = False )
    elif sys.platform.startswith("linux"):
        subprocess.call(["pip", "install", "psutil"],shell = False)
    else:
        raise Exception(f"Unsupported platform: {sys.platform}")
    print("openai installed successfully")
from qgis.PyQt.QtGui import QPixmap, QPainter, QImage
from qgis.PyQt.QtWidgets import QFileDialog, QGraphicsScene,  QGraphicsView, QListWidgetItem, QDialog, QMessageBox, QProgressDialog, QInputDialog, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QLabel
from qgis.PyQt.QtCore import Qt, pyqtSlot, QCoreApplication, QThread, QRectF, QEventLoop, QTimer
from qgis.core import Qgis,QgsLayoutFrame, QgsMessageLog, QgsProject, QgsLayoutExporter, QgsApplication, QgsLayoutItemMap, QgsReadWriteContext, QgsPrintLayout,QgsLayoutMultiFrame, QgsLayoutItemHtml, QgsLayoutItemPicture, QgsLayoutItemLabel, QgsLayoutItemScaleBar, QgsRectangle
from qgis.PyQt.QtXml import QDomDocument

from ..modules.db.pyarchinit_utility import Utility
from .Interactive_matrix import *
from ..modules.utility.pyarchinit_theme_manager import ThemeManager
from ..modules.utility.atlas_labels import (labelled_ids,
                                            quota_labeling,
                                            us_labeling)
from ..modules.utility.atlas_overview import (DEFAULT_BASE_MAP,
                                              base_map_name,
                                              base_map_uri,
                                              overview_indexes,
                                              overview_window)
from ..modules.utility.atlas_scale import (fitting_extent,
                                           main_map_index, nice_scale)
from ..modules.utility.atlas_template import (MATRIX_ID, TITLE_ID,
                                              capabilities,
                                              describe_missing,
                                              is_usable)
MAIN_DIALOG_CLASS, _ = loadUiType(
    os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'Gis_Time_controller.ui'))

class ZoomableGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

    def wheelEvent(self, event):

        # Zoom Factor
        zoomInFactor = 1.25
        zoomOutFactor = 1 / zoomInFactor

        # Save the scene pos
        oldPos = self.mapToScene(event.pos())

        # Zoom
        if event.angleDelta().y() > 0:
            zoomFactor = zoomInFactor
        else:
            zoomFactor = zoomOutFactor
        self.scale(zoomFactor, zoomFactor)

        # Get the new position
        newPos = self.mapToScene(event.pos())

        # Move scene to old position
        delta = newPos - oldPos
        self.translate(delta.x(), delta.y())

class pyarchinit_Gis_Time_Controller(QDialog, MAIN_DIALOG_CLASS):
    L=QgsSettings().value("locale/userLocale", "it", type=str)[:2]
    MSG_BOX_TITLE = "PyArchInit - Gis Time Management"
    DB_MANAGER = ""
    DATA_LIST = ""
    ORDER_LAYER_VALUE = ""
    ORDER_SITO=''
    ORDER_AREA=''
    MAPPER_TABLE_CLASS = "US"
    UTILITY=Utility()
    def __init__(self, iface):
        super().__init__()

        #self.max_num_order_layer = None
        self.iface = iface

        self.pyQGIS = Pyarchinit_pyqgis(iface)
        self.setupUi(self)

        # Debounce timer for dial/spinbox
        self._debounce_timer = QTimer()
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.setInterval(300)
        self._debounce_timer.timeout.connect(self._on_debounce_timeout)
        self._pending_value = 0

        # Cached sito/area strings
        self._cached_sito = None
        self._cached_area = None

        # Apply theme
        ThemeManager.apply_theme(self)
        self.theme_toggle_btn = ThemeManager.add_theme_toggle_to_form(self)

        self.currentLayerId = None
        try:
            self.connect()
        except:
            pass
        self.selected_layers = None
        self.listWidget.clear()
        self.listWidget.clear()
        self.listWidget.clear()
        all_layers = QgsProject.instance().mapLayers().values()
        self.relevant_layers = [layer for layer in all_layers if
                           layer.dataProvider().fields().indexFromName('order_layer') != -1]
        #self.spinBox_relative_cronology.setHidden(True)
        for layer in self.relevant_layers:
            item = QListWidgetItem(layer.name())
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.listWidget.addItem(item)
        self.abort = False

        # Add checkbox for cumulative mode (default: checked/cumulative)
        try:
            from qgis.PyQt.QtWidgets import QCheckBox
            if not hasattr(self, 'checkBox_cumulative'):
                self.checkBox_cumulative = QCheckBox()
                if self.L == 'it':
                    self.checkBox_cumulative.setText("Modalità Cumulativa (mostra <= livello)")
                    self.checkBox_cumulative.setToolTip(self.tr("Se attivo, mostra tutte le US fino al livello selezionato.\nSe disattivo, mostra solo le US del livello esatto."))
                elif self.L == 'de':
                    self.checkBox_cumulative.setText("Kumulativer Modus (zeige <= Ebene)")
                    self.checkBox_cumulative.setToolTip(self.tr("Wenn aktiviert, zeigt alle US bis zur ausgewählten Ebene.\nWenn deaktiviert, zeigt nur US der genauen Ebene."))
                else:
                    self.checkBox_cumulative.setText("Cumulative Mode (show <= level)")
                    self.checkBox_cumulative.setToolTip(self.tr("If checked, shows all US up to selected level.\nIf unchecked, shows only US at exact level."))

                self.checkBox_cumulative.setChecked(False)  # Default: NON cumulativo (singolo livello)

                # Add to layout - try to find a good place near the dial/spinbox
                if hasattr(self, 'verticalLayout') and self.verticalLayout:
                    self.verticalLayout.addWidget(self.checkBox_cumulative)
                elif hasattr(self, 'layout') and self.layout():
                    self.layout().addWidget(self.checkBox_cumulative)

                # Connect checkbox to update filter when changed
                self.checkBox_cumulative.stateChanged.connect(lambda: self.define_order_layer_value(self.ORDER_LAYER_VALUE))

                print("Cumulative mode checkbox added successfully")
        except Exception as e:
            print(f"Error creating cumulative checkbox: {e}")
            import traceback
            traceback.print_exc()

        self.listWidget.itemChanged.connect(self.update_selected_layers)
        self.dial_relative_cronology.valueChanged.connect(self.set_max_num)
        self.spinBox_relative_cronology.valueChanged.connect(self.set_max_num)
        self.dial_relative_cronology.valueChanged.connect(self._schedule_order_layer_update)
        self.dial_relative_cronology.valueChanged.connect(self.spinBox_relative_cronology.setValue)
        self.spinBox_relative_cronology.valueChanged.connect(self._schedule_order_layer_update)
        self.spinBox_relative_cronology.valueChanged.connect(self.dial_relative_cronology.setValue)
        self.listWidget.itemSelectionChanged.connect(self.update_selected_layers)
        # Le due tabelle tenute in memoria sono di classe: aprendo la
        # finestra su un altro sito porterebbero i dati di prima.
        type(self)._PERIODI_CACHE = {}
        type(self)._DATAZIONI_CACHE = {}
        type(self)._RECORD_CACHE = {}
        # Gli avvisi su un modello incompleto si danno una volta,
        # non una per tavola.
        self._avvisato_senza_titolo = False
        self._avvisato_senza_matrice = False
        self._atlante_in_corso = False

        self.spinBox_relative_cronology.valueChanged.connect(self.update_datazione)
        self.checkBox_matrix.stateChanged.connect(self.update_graphics_view)
        if self.checkBox_matrix.isChecked():
            self.update_graphics_view()

        self.stop_button.clicked.connect(self.stop_image_generation)

    def connect(self):
        conn = Connection()
        conn_str = conn.conn_str()
        try:
            self.DB_MANAGER = get_db_manager(conn_str, use_singleton=True)
        except Exception as e:
            e = str(e)
            if e.find("no such table"):
                if self.L=='it':
                    msg = "La connessione e' fallita {}. " \
                          "E' NECESSARIO RIAVVIARE QGIS ".format(str(e))
                    self.iface.messageBar().pushMessage(self.tr(msg), Qgis.Warning, 0)
                
                    self.iface.messageBar().pushMessage(self.tr(msg), Qgis.Warning, 0)
                elif self.L=='de':
                    msg = "Verbindungsfehler {}. " \
                          " QGIS neustarten oder es wurde".format(str(e))
                    self.iface.messageBar().pushMessage(self.tr(msg), Qgis.Warning, 0)
                else:
                    msg = "The connection failed {}. " \
                          "You MUST RESTART QGIS".format(str(e))

    def update_selected_layers(self):
        selected_layer_names = [self.listWidget.item(i).text() for i in range(self.listWidget.count()) if
                                self.listWidget.item(i).checkState() == Qt.CheckState.Checked]
        self.selected_layers = [layer for layer in self.relevant_layers if layer.name() in selected_layer_names]

    def _schedule_order_layer_update(self, v):
        """Debounced order layer update."""
        self._pending_value = v
        self._debounce_timer.start()

    def _on_debounce_timeout(self):
        """Called after debounce period."""
        if getattr(self, '_atlante_in_corso', False):
            return                     # l'atlante guida lui la sequenza
        self.define_order_layer_value(self._pending_value)
        # La matrice segue la manopola. Prima si rifaceva solo spegnendo
        # e riaccendendo la spunta «Mostra Matrix» (Enzo, 2026-10-09):
        # era agganciata a stateChanged e a nient'altro. Si rifà DOPO il
        # filtro, così disegna le US che si vedono davvero.
        try:
            if self.checkBox_matrix.isChecked():
                self.update_graphics_view()
        except Exception as e:                      # noqa: BLE001
            QgsMessageLog.logMessage(
                "Matrice non aggiornata: %s" % e, "PyArchInit",
                Qgis.MessageLevel.Warning)

    def _get_cached_sito_area(self):
        """Get sito/area strings from SITE_SET config, not all sites."""
        if self._cached_sito is None:
            try:
                from ..modules.db.pyarchinit_conn_strings import Connection
                conn = Connection()
                sito_set = conn.sito_set()
                sito_set_str = sito_set.get('sito_set', '')
                if sito_set_str:
                    self._cached_sito = sito_set_str
                    # Get areas only for the selected site
                    search_dict = {'sito': "'" + sito_set_str + "'"}
                    u = Utility()
                    search_dict = u.remove_empty_items_fr_dict(search_dict)
                    area_list = self.UTILITY.tup_2_list_III(
                        self.DB_MANAGER.group_by('us_table', 'area', 'US'))
                    self._cached_area = "','".join(area_list) if area_list else ''
                else:
                    # Fallback: all sites
                    self._cached_sito = "','".join(
                        self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('us_table', 'sito', 'US')))
                    self._cached_area = "','".join(
                        self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('us_table', 'area', 'US')))
            except Exception:
                self._cached_sito = "','".join(
                    self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('us_table', 'sito', 'US')))
                self._cached_area = "','".join(
                    self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('us_table', 'area', 'US')))
        return self._cached_sito, self._cached_area

    def update_layers(self, layers):
        # 'layers' è una lista di oggetti QgsMapLayer.
        # Qui implementi la logica per gestire i layer selezionati.
        self.selected_layers = layers  # memorizza i layer selezionati in un attributo dell'istanza

    def set_max_num(self):


        if self.selected_layers is None or not self.selected_layers:
            self.listWidget.addItem('I layer Quote View e US View devono essere caricati.')
            return

        # Le datazioni vengono dal DATABASE, non dalle feature del layer.
        # Leggerle dal layer significava leggerle attraverso il filtro
        # corrente, che però si applica dopo, con un timer: girando la
        # manopola in senso orario il livello nuovo non era ancora nel
        # layer e la casella della periodizzazione restava vuota, mentre
        # in senso antiorario compariva (il filtro di prima era più
        # largo). Enzo, 2026-10-09.
        self.fieldname = 'datazione'
        self.datazione_dict = self._datazioni_del_sito()

        # Get max order_layer for the current site only (not all sites)
        try:
            sito, _ = self._get_cached_sito_area()
            search_dict = {'sito': "'" + sito + "'"}
            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)
            records = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
            max_num_order_layer = max((r.order_layer or 0) for r in records) if records else 0
        except Exception:
            max_num_order_layer = self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, "order_layer")
        if max_num_order_layer is not None:
            max_num_order_layer += 1
            self.dial_relative_cronology.setMaximum(max_num_order_layer)
            self.spinBox_relative_cronology.setMaximum(max_num_order_layer)
        else:
            # handle the error
            print("Errore: max_num_order_layer è None")

        # NB: la connessione a update_datazione sta nel costruttore. Qui
        # si rifaceva a ogni valueChanged, e siccome set_max_num è esso
        # stesso agganciato a valueChanged le connessioni si accumulavano
        # a ogni scatto della manopola.
        self.update_datazione(self.spinBox_relative_cronology.value())





    #: I periodi di un sito, letti una volta sola. La via vecchia ne
    #: faceva una query per ogni area e per ogni periodo, dentro due
    #: cicli annidati, a OGNI rigenerazione della matrice — e la matrice
    #: si rigenera a ogni scatto della manopola e a ogni pagina
    #: dell'atlante.
    _PERIODI_CACHE = {}

    def _periodi_del_sito(self, sito):
        """``(periodo, fase, datazione_estesa, cron_iniziale, cron_finale)``."""
        chiave = str(sito or "")
        if chiave in self._PERIODI_CACHE:
            return self._PERIODI_CACHE[chiave]
        righe = []
        try:
            for a in self.DB_MANAGER.query_bool(
                    {'sito': "'" + chiave + "'"}, 'PERIODIZZAZIONE'):
                righe.append((a.periodo, a.fase, a.datazione_estesa,
                              a.cron_iniziale, a.cron_finale))
        except Exception as e:                      # noqa: BLE001
            QgsMessageLog.logMessage(
                "Periodizzazione non letta per %r: %s" % (chiave, e),
                "PyArchInit", Qgis.MessageLevel.Warning)
        self._PERIODI_CACHE[chiave] = righe
        return righe

    #: Le datazioni per livello, lette una volta sola dal database.
    _DATAZIONI_CACHE = {}

    def _datazioni_del_sito(self):
        """``{order_layer: [datazione, …]}`` del sito corrente.

        Dal database e non dai layer: il layer è filtrato, e il filtro si
        applica dopo con un timer.
        """
        try:
            sito, _ = self._get_cached_sito_area()
        except Exception:                           # noqa: BLE001
            sito = ""
        chiave = str(sito or "")
        if chiave in self._DATAZIONI_CACHE:
            return self._DATAZIONI_CACHE[chiave]
        datazioni = {}
        try:
            for r in self.DB_MANAGER.query_bool(
                    {'sito': "'" + chiave + "'"}, self.MAPPER_TABLE_CLASS):
                livello = getattr(r, 'order_layer', None)
                testo = getattr(r, 'datazione', None)
                if livello is None or not testo:
                    continue
                datazioni.setdefault(livello, []).append(testo)
        except Exception as e:                      # noqa: BLE001
            QgsMessageLog.logMessage(
                "Datazioni non lette per %r: %s" % (chiave, e),
                "PyArchInit", Qgis.MessageLevel.Warning)
        self._DATAZIONI_CACHE[chiave] = datazioni
        return datazioni

    #: Tutte le righe della scheda del sito, lette una volta sola.
    _RECORD_CACHE = {}

    def _record_del_sito(self, sito):
        """Le righe di ``us_table`` del sito, come dizionari.

        Servono **tutte**, non solo quelle visibili: le US fuori vista che
        un rapporto cita entrano nel disegno sbiadite, e senza le loro
        righe non si saprebbe nemmeno che esistono.
        """
        chiave = str(sito or "")
        if chiave in self._RECORD_CACHE:
            return self._RECORD_CACHE[chiave]
        righe = []
        try:
            for r in self.DB_MANAGER.query_bool(
                    {'sito': "'" + chiave + "'"}, self.MAPPER_TABLE_CLASS):
                righe.append({c: getattr(r, c, None) for c in (
                    'sito', 'area', 'us', 'unita_tipo', 'rapporti',
                    'periodo_iniziale', 'fase_iniziale', 'periodo_finale',
                    'fase_finale', 'd_stratigrafica', 'd_interpretativa',
                    'datazione', 'order_layer')})
        except Exception as e:                      # noqa: BLE001
            QgsMessageLog.logMessage(
                "Righe US non lette per %r: %s" % (chiave, e),
                "PyArchInit", Qgis.MessageLevel.Warning)
        self._RECORD_CACHE[chiave] = righe
        return righe

    def _modello_matrice(self, data_list, visible_us_list):
        """Il modello della matrice: le US visibili alla posizione della
        manopola, più quelle che un rapporto cita — queste ultime
        sbiadite, perché non sono sulla mappa."""
        from ..modules.utility.em_matrix_records import model_from_records

        if not data_list:
            return None
        sito = str((data_list[0] or {}).get('sito') or '')
        visibili = {(str(a), str(u)) for a, u in (visible_us_list or ())}
        tutte = self._record_del_sito(sito) or data_list
        return model_from_records(
            tutte, self._periodi_del_sito(sito),
            visible=visibili or None, title=sito)

    def _disegna_matrice(self, data_list, visible_us_list, destinazione):
        """La matrice in SVG per la tavola dell'atlante. ``(percorso, modello)``.

        Al posto di Graphviz: nessun sottoprocesso ``tred``/``dot``,
        nessun JPEG di megabyte riletto da disco. Stesso impaginatore e
        stesso writer del pannello della matrice, quindi quello che si
        vede qui e quello che si vede là non divergono.
        """
        from ..modules.utility.em_matrix_layout import layout
        from ..modules.utility.em_matrix_svg import write_svg

        modello = self._modello_matrice(data_list, visible_us_list)
        if modello is None:
            return None, None
        return (write_svg(layout(modello), destinazione, modello.title),
                modello)

    def update_graphics_view(self):
        if self.checkBox_matrix.isChecked():
            try:
                self.id_us_dict = {}

                # Ottieni il valore corrente dell'order_layer
                current_order_layer = self.spinBox_relative_cronology.value()
                
                data_list = []
                visible_us_list = []
                
                for layer in self.selected_layers:
                    fields = layer.fields()
                    self.fieldname = next((field.name() for field in fields if 'datazione' in field.name().lower()), '')
                    if not self.fieldname:
                        print(f"No 'datazione' field found in layer {layer.name()}")
                        continue

                    for feature in layer.getFeatures():
                        feature_order_layer = feature.attribute("order_layer")
                        
                        # Include solo le US con order_layer <= valore corrente
                        if feature_order_layer is not None and feature_order_layer <= current_order_layer:
                            data_dict = {field.name(): feature[field.name()] for field in feature.fields()}
                            data_list.append(data_dict)
                            
                            # Aggiungi alla lista delle US visibili
                            us_val = feature.attribute("us")
                            area_val = feature.attribute("area")
                            if us_val is not None and area_val is not None:
                                visible_us_list.append((str(area_val), str(us_val)))
                            
                            datazione = feature.attribute(self.fieldname)
                            if feature_order_layer in self.id_us_dict:
                                self.id_us_dict[feature_order_layer].append(datazione)
                            else:
                                self.id_us_dict[feature_order_layer] = [datazione]

                if data_list:
                    # La matrice si disegna in casa: l'impaginatore puro
                    # ci mette millisecondi, dove tred+dot costavano due
                    # sottoprocessi e un JPEG da rileggere da disco.
                    from ..modules.utility.em_matrix_layout import layout
                    from ..modules.utility.em_matrix_view import MatrixView

                    modello = self._modello_matrice(data_list,
                                                    visible_us_list)
                    if modello is None:
                        return

                    self.horizontalLayout_2.removeWidget(self.graphicsView)
                    self.graphicsView = MatrixView()
                    self.horizontalLayout_2.addWidget(self.graphicsView)
                    self.graphicsView.show_layout(layout(modello))
                    self.graphicsView.setFocus()



            except AssertionError as e:

                QMessageBox.warning(self, "Alert", str(e))

    def define_order_layer_value(self, v, apply_period_filter=False):
        """
        Aggiorna il filtro dei layer in base al valore di order_layer e opzionalmente alla periodizzazione.

        Args:
            v: Valore di order_layer
            apply_period_filter: Se True, applica anche il filtro sulla periodizzazione basato sull'intervallo cronologico
        """
        if self.selected_layers is None or not self.selected_layers:
            QgsMessageLog.logMessage('I layer Quote View e US View devono essere caricati.', 'Avviso')
            return

        sito, area = self._get_cached_sito_area()

        self.ORDER_LAYER_VALUE = v

        # Se richiesto, ottieni i periodi/fasi nell'intervallo cronologico
        periodi_fasi = None
        if apply_period_filter:
            try:
                # Ottieni i valori dagli spinBox cronologici
                cron_iniz = int(self.spinBox_cron_iniz.text()) if hasattr(self, 'spinBox_cron_iniz') and self.spinBox_cron_iniz.text() else None
                cron_fin = int(self.spinBox_cron_fin.text()) if hasattr(self, 'spinBox_cron_fin') and self.spinBox_cron_fin.text() else None

                if cron_iniz is not None and cron_fin is not None:
                    # Query alla tabella PERIODIZZAZIONE per ottenere i periodi nell'intervallo
                    per_res = self.DB_MANAGER.query_operator(
                        [
                            ['cron_finale', '>=', cron_iniz],
                            ['cron_iniziale', '<=', cron_fin],
                        ], 'PERIODIZZAZIONE')

                    if per_res and len(per_res) > 0:
                        # Estrai le tuple (periodo, fase)
                        periodi_fasi = [(str(p.periodo), str(p.fase)) for p in per_res]
            except Exception as e:
                print(f"Errore nell'applicare il filtro periodizzazione: {e}")

        # Determina se usare modalità cumulativa o singolo livello
        cumulative = getattr(self, 'checkBox_cumulative', None)
        cumulative_value = cumulative.isChecked() if cumulative else True  # Default: cumulativo

        for layer in self.selected_layers:
            data_provider = layer.dataProvider()
            self.liststring(sito, area, layer, data_provider, periodi_fasi, cumulative_value)




    def update_datazione(self, value):
        # Cerca il valore dello spinBox nel dizionario e imposta il valore del textEdit_datazione corrispondente
        datazioni = self.datazione_dict.get(value, [])
        # Rimuove i duplicati convertendo la lista in un set
        unique_datazioni = set(datazioni)
        self.textEdit_datazione.setPlainText('\n'.join(map(str, unique_datazioni)))

    def liststring(self, sito, area, i, e, periodi_fasi=None, cumulative=True):
        """
        Imposta il filtro sui layer in base a order_layer, sito, area e opzionalmente periodizzazione.

        Args:
            sito: Lista di siti da filtrare
            area: Lista di aree da filtrare
            i: Layer
            e: Data provider
            periodi_fasi: Lista opzionale di tuple (periodo, fase) per filtrare le US
            cumulative: Se True usa "order_layer <= valore" (cumulativo), se False usa "order_layer = valore" (singolo livello)
        """
        # Usa operatore <= per cumulativo o = per singolo livello
        operator = "<=" if cumulative else "="
        order_val = self.ORDER_LAYER_VALUE if self.ORDER_LAYER_VALUE is not None else 0
        new_sub_set_string = f"order_layer {operator} {order_val} AND sito IN ('{sito}') AND area IN ('{area}')"

        # Aggiungi filtro per periodizzazione se specificato
        if periodi_fasi and len(periodi_fasi) > 0:
            # Costruisci una condizione SQL per filtrare per periodo_iniziale e fase_iniziale
            # Esempio: (periodo_iniziale = 'Periodo1' AND fase_iniziale = 'Fase1') OR (periodo_iniziale = 'Periodo2' AND fase_iniziale = 'Fase2') ...
            periodo_conditions = []
            for periodo, fase in periodi_fasi:
                if periodo and fase:
                    periodo_conditions.append(f"(periodo_iniziale = '{periodo}' AND fase_iniziale = '{fase}')")
                elif periodo:  # Solo periodo specificato
                    periodo_conditions.append(f"periodo_iniziale = '{periodo}'")

            if periodo_conditions:
                periodo_filter = " OR ".join(periodo_conditions)
                new_sub_set_string += f" AND ({periodo_filter})"

        i.setSubsetString(new_sub_set_string)
        e.setSubsetString(new_sub_set_string)


    def on_pushButton_visualize_pressed(self):
        op_cron_iniz = '<='
        op_cron_fin = '>='

        per_res = self.DB_MANAGER.query_operator(
            [
                ['cron_finale', op_cron_fin, int(self.spinBox_cron_iniz.text())],
                ['cron_iniziale', op_cron_iniz, int(self.spinBox_cron_fin.text())],
            ], 'PERIODIZZAZIONE')

        if not bool(per_res):
            
            if self.L=='it': 
                QMessageBox.warning(self, "Alert", "Non vi sono Periodizzazioni in questo intervallo di tempo",
                                    QMessageBox.StandardButton.Ok)
        
            elif self.L=='de': 
                QMessageBox.warning(self, "Alert", "Es gibt keine Perioden in diesem Zeitintervall.",
                                    QMessageBox.StandardButton.Ok)
            else: 
                QMessageBox.warning(self, "Alert", "There are no Periods in this time interval",
                                    QMessageBox.StandardButton.Ok)
            
        else:
            us_res = []
            for sing_per in range(len(per_res)):
                params = {'sito': "'" + str(per_res[sing_per].sito) + "'",
                          'periodo_iniziale': "'" + str(per_res[sing_per].periodo) + "'",
                          'fase_iniziale': "'" + str(per_res[sing_per].fase) + "'"}
                us_res.append(self.DB_MANAGER.query_bool(params, 'US'))

            us_res_dep = []

            for i in us_res:
                for n in i:
                    us_res_dep.append(n)

            if not bool(us_res_dep):
                
                if self.L=='it':
                    QMessageBox.warning(self, "Alert", "Non ci sono geometrie da visualizzare", QMessageBox.StandardButton.Ok)

                elif self.L=='de':
                    QMessageBox.warning(self, "Alert", "es gibt keine Geometrien, die angezeigt werden können", QMessageBox.StandardButton.Ok) 
                else:
                    QMessageBox.warning(self, "Alert", "There are no geometries to display", QMessageBox.StandardButton.Ok)    
            else:
                self.pyQGIS.charge_vector_layers(us_res_dep)

            try:
                self.update_graphics_view()
            except AssertionError as e:
                QMessageBox.warning(self, "Attenzione", 'Devi selezionare prima il layer us view nella toc')



    def on_pushButton_atlas_pressed(self):
        self.generate_images()

    def load_template(self, template_path):
        project = QgsProject.instance()
        manager = project.layoutManager()

        layout = QgsPrintLayout(project)
        layout.initializeDefaults()

        with open(template_path) as template_file:
            template_content = template_file.read()

        doc = QDomDocument()
        doc.setContent(template_content)

        read_context = QgsReadWriteContext()
        layout.readXml(doc.documentElement(), doc, read_context)

        layout_name = 'layout_Time_Manager'
        existing_layout = manager.layoutByName(layout_name)
        if existing_layout:
            # Elimina l'esistente layout
            manager.removeLayout(existing_layout)

        layout.setName(layout_name)
        manager.addLayout(layout)
        self.current_layout = layout



    def get_available_templates(self):
        """Ottiene la lista dei template disponibili"""
        template_paths = []
        
        # Cerca i template in diverse cartelle
        search_paths = [
            os.path.join(os.environ.get('PYARCHINIT_HOME', ''), 'bin', 'profile', 'template'),
            os.path.join(os.path.dirname(__file__), '..', 'resources', 'dbfiles'),
            os.path.dirname(__file__.replace('tabs', ''))  # directory principale plugin
        ]
        
        for search_path in search_paths:
            if os.path.exists(search_path):
                for file in os.listdir(search_path):
                    if file.endswith('.qpt'):
                        full_path = os.path.join(search_path, file)
                        template_name = os.path.splitext(file)[0]  # rimuove .qpt
                        template_paths.append((template_name, full_path))
        
        # Rimuovi duplicati basandosi sul nome
        seen_names = set()
        unique_templates = []
        for name, path in template_paths:
            if name not in seen_names:
                seen_names.add(name)
                unique_templates.append((name, path))
        
        return unique_templates

    def choose_template(self):
        """Dialog avanzato per scegliere il template da utilizzare"""
        from qgis.PyQt.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QLabel, QListWidgetItem
        
        templates = self.get_available_templates()
        if not templates:
            QMessageBox.warning(self, "Warning", "Nessun template (.qpt) trovato nelle directory standard.")
            return None
        
        # Crea dialog personalizzato
        dialog = QDialog(self)
        dialog.setWindowTitle("Scegli Layout Template per Atlas")
        dialog.setModal(True)
        dialog.resize(400, 300)
        
        layout = QVBoxLayout(dialog)
        
        # Label informativa
        info_label = QLabel(
            "Seleziona il template per l'atlas.\n"
            "✓ = titolo e matrice   • = solo mappa   ✗ = senza mappa")
        layout.addWidget(info_label)
        
        # Lista template
        template_list = QListWidget()
        # Solo il modello del Time Manager porta il titolo «Tavola N» e
        # l'immagine della matrice. Gli altri fanno tavole più spoglie, e
        # prima sceglierli faceva tornare indietro il generatore in
        # silenzio: adesso si vede subito quali sono (Enzo, 2026-10-09).
        completi = []
        for name, path in templates:
            try:
                caps = capabilities(open(path, encoding='utf-8',
                                         errors='replace').read())
            except Exception:                       # noqa: BLE001
                caps = {"map": True, "title": False, "matrix": False}
            pieno = caps.get("title") and caps.get("matrix")
            segno = "✓" if pieno else ("•" if is_usable(caps) else "✗")
            item = QListWidgetItem("%s  %s" % (segno, name))
            manca = describe_missing(caps)
            item.setToolTip("%s\n%s" % (path, manca) if manca else path)
            item.setData(Qt.ItemDataRole.UserRole, path)
            template_list.addItem(item)
            if pieno:
                completi.append(template_list.count() - 1)

        # Si parte da uno completo, se c'è: è quello che fa la tavola
        # intera, titolo e matrice compresi.
        if completi:
            template_list.setCurrentRow(completi[0])
        elif template_list.count() > 0:
            template_list.setCurrentRow(0)
            
        layout.addWidget(template_list)
        
        # Info sul template selezionato
        info_path_label = QLabel("")
        info_path_label.setWordWrap(True)
        info_path_label.setStyleSheet("QLabel { color: gray; font-size: 10px; }")
        layout.addWidget(info_path_label)
        
        # Aggiorna info quando si cambia selezione
        def update_info():
            current_item = template_list.currentItem()
            if current_item:
                path = current_item.data(Qt.ItemDataRole.UserRole)
                info_path_label.setText(f"Path: {path}")
        
        template_list.currentItemChanged.connect(update_info)
        update_info()  # Inizializza
        
        # Bottoni
        button_layout = QHBoxLayout()
        
        browse_btn = QPushButton("Sfoglia...")
        browse_btn.clicked.connect(lambda: self.browse_for_template(dialog))
        
        new_btn = QPushButton("Nuovo Template...")
        new_btn.clicked.connect(lambda: self.create_new_template(dialog))
        
        ok_btn = QPushButton("Usa Template")
        cancel_btn = QPushButton("Annulla")
        
        ok_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)
        
        button_layout.addWidget(browse_btn)
        button_layout.addWidget(new_btn)
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(ok_btn)
        
        layout.addLayout(button_layout)
        
        # Imposta bottone di default
        ok_btn.setDefault(True)
        
        # Esegui dialog
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Controlla se è stato selezionato un template personalizzato
            if hasattr(self, 'selected_custom_template'):
                path = self.selected_custom_template
                delattr(self, 'selected_custom_template')  # Pulisci
                return path
            
            # Altrimenti usa quello dalla lista
            current_item = template_list.currentItem()
            if current_item:
                return current_item.data(Qt.ItemDataRole.UserRole)
        
        return None
    
    def browse_for_template(self, parent_dialog):
        """Permette di sfogliare per un template personalizzato"""
        template_path, _ = QFileDialog.getOpenFileName(
            parent_dialog,
            "Seleziona Template Layout (.qpt)",
            os.path.expanduser("~"),
            "QGIS Layout Templates (*.qpt);;All Files (*)"
        )
        
        if template_path:
            parent_dialog.accept()
            self.selected_custom_template = template_path
            return template_path
        
        return None

    def create_new_template(self, parent_dialog):
        """Crea un nuovo template da zero"""
        template_name, ok = QInputDialog.getText(
            parent_dialog,
            "Nuovo Template",
            "Nome per il nuovo template:",
            text="Atlas_Template_Custom"
        )
        
        if not ok or not template_name.strip():
            return None
            
        # Assicurati che abbia l'estensione .qpt
        if not template_name.endswith('.qpt'):
            template_name += '.qpt'
            
        try:
            # Crea un nuovo layout vuoto
            layout_manager = QgsProject.instance().layoutManager()
            new_layout = QgsPrintLayout(QgsProject.instance())
            new_layout.initializeDefaults()
            new_layout.setName(template_name.replace('.qpt', ''))
            
            # Aggiungi elementi base per l'atlas
            # Mappa principale
            map_item = QgsLayoutItemMap(new_layout)
            map_item.attemptSetSceneRect(QRectF(20, 20, 200, 150))  # x, y, width, height in mm
            map_item.setFrameEnabled(True)
            new_layout.addLayoutItem(map_item)
            
            # Titolo
            from qgis.core import QgsLayoutItemLabel, QFont
            title_item = QgsLayoutItemLabel(new_layout)
            title_item.attemptSetSceneRect(QRectF(20, 5, 200, 10))
            title_item.setText("Atlas Tavola [% @order_layer %]")
            font = QFont()
            font.setPointSize(16)
            font.setBold(True)
            title_item.setFont(font)
            new_layout.addLayoutItem(title_item)
            
            # Area per matrice (placeholder)
            matrix_item = QgsLayoutItemPicture(new_layout)
            matrix_item.attemptSetSceneRect(QRectF(230, 20, 100, 100))
            matrix_item.setFrameEnabled(True)
            new_layout.addLayoutItem(matrix_item)
            
            # Salva il template
            template_dir = os.path.join(os.path.dirname(__file__), '..', 'resources', 'dbfiles')
            if not os.path.exists(template_dir):
                os.makedirs(template_dir)
                
            template_path = os.path.join(template_dir, template_name)
            
            # Salva come XML
            document = QDomDocument()
            context = QgsReadWriteContext()
            layout_element = document.createElement("Layout")
            
            new_layout.writeXml(layout_element, document, context)
            document.appendChild(layout_element)
            
            with open(template_path, 'w') as f:
                f.write(document.toString())
                
            # Apri il designer per personalizzazione
            layout_manager.addLayout(new_layout)
            from qgis.utils import iface
            iface.openLayoutDesigner(new_layout)
            
            QMessageBox.information(
                parent_dialog,
                "Template Creato",
                f"Nuovo template creato: {template_name}\n\n"
                f"Il Layout Designer è ora aperto per personalizzare il template.\n"
                f"Quando hai finito, chiudi il designer e il template sarà disponibile."
            )
            
            # Chiudi il dialog di selezione
            parent_dialog.accept()
            self.selected_custom_template = template_path
            return template_path
            
        except Exception as e:
            QMessageBox.critical(
                parent_dialog,
                "Errore Creazione Template",
                f"Errore nella creazione del template:\n{str(e)}"
            )
            return None

    def _estensione_dei_dati(self):
        """Il rettangolo che contiene quello che si vede adesso.

        Dalle VISTE filtrate, non dal canvas: il canvas può essere molto
        più largo dello scavo, e il disegno resterebbe un francobollo in
        mezzo al foglio (Enzo, 2026-10-09).
        """
        unione = None
        for layer in (self.selected_layers or []):
            try:
                if layer.featureCount() == 0:
                    continue
                est = layer.extent()
                if est.isEmpty():
                    continue
            except Exception:                       # noqa: BLE001
                continue
            unione = QgsRectangle(est) if unione is None else unione
            unione.combineExtentWith(est)
        if unione is None or unione.isEmpty():
            return None
        return (unione.xMinimum(), unione.yMinimum(),
                unione.xMaximum(), unione.yMaximum())

    def _riquadro_del_sito(self):
        """Il rettangolo di TUTTE le US del sito, non solo di quelle del
        livello corrente.

        Un atlante deve avere la **stessa scala su tutte le tavole**: se
        ogni tavola si adattasse al suo livello, la stessa US cambierebbe
        dimensione da una pagina all'altra e le tavole non si
        confronterebbero più. Quindi si inquadra una volta sola, sul
        massimo, e tutte le tavole usano quello.

        I filtri che si mettono qui li riscrive subito il ciclo, a ogni
        livello.
        """
        sito, _area = self._get_cached_sito_area()
        for layer in (self.selected_layers or []):
            try:
                layer.setSubsetString("sito IN ('%s')" % sito)
            except Exception:                       # noqa: BLE001
                continue
        return fitting_extent(self._estensione_dei_dati(), margin=0.0)

    def _inquadra_tavola(self, mappe):
        """Inquadra la mappa grande sui dati e sistema le scale.

        Solo la mappa **grande**: il modello del Time Manager ne ha due, e
        la piccola è l'inserto panoramico, che serve a dire dove si è nel
        mondo e che inquadrato sullo scavo non direbbe più niente.

        La scala si arrotonda alla prima scala vera che contiene ancora
        tutto (1:20, non 1:18,6), e le barre di scala del modello —
        che nel template non sono collegate a nessuna mappa, ed è per
        questo che la numerica stampava «1:1» — vengono collegate a lei.
        """
        if not mappe:
            return
        for mappa in mappe:
            try:
                # Un template salvato altrove può portarsi dietro un
                # elenco di layer che qui non esistono.
                mappa.setFollowVisibilityPreset(False)
                mappa.setKeepLayerSet(False)
            except Exception:                       # noqa: BLE001
                pass
        misure = []
        for mappa in mappe:
            try:
                m = mappa.sizeWithUnits()
                misure.append((m.width(), m.height()))
            except Exception:                       # noqa: BLE001
                misure.append((0.0, 0.0))
        indice = main_map_index(misure)
        if indice is None:
            return
        principale = mappe[indice]
        # Il riquadro è quello di tutto il sito, calcolato una volta
        # sola all'inizio della generazione: stessa inquadratura e stessa
        # scala su ogni tavola. Nessun margine in più — `zoomToExtent`
        # già lascia l'aria che serve per via delle proporzioni del
        # telaio, e un 6% in più spingeva 1:18,6 oltre il 20, facendo
        # saltare la serie a 1:25, cioè un disegno più piccolo del
        # necessario. Misurato (inchiostro sul foglio, livello 24):
        # esatta 22,85%, col margine e arrotondata 13,26%, senza margine
        # e arrotondata 19,88%.
        riquadro = getattr(self, "_riquadro_atlante", None)
        if riquadro is None:
            riquadro = fitting_extent(self._estensione_dei_dati(),
                                      margin=0.0)
        try:
            if riquadro:
                principale.zoomToExtent(QgsRectangle(*riquadro))
            else:
                principale.zoomToExtent(self.iface.mapCanvas().extent())
            scala = nice_scale(principale.scale())
            principale.setScale(scala)
        except Exception as e:                      # noqa: BLE001
            QgsMessageLog.logMessage(
                "Mappa della tavola non inquadrata: %s" % e,
                "PyArchInit", Qgis.MessageLevel.Warning)
            return
        for elemento in self.current_layout.items():
            try:
                if isinstance(elemento, QgsLayoutItemScaleBar) \
                        and elemento.linkedMap() is None:
                    elemento.setLinkedMap(principale)
            except Exception:                       # noqa: BLE001
                continue
        self._prepara_panoramica(mappe, indice, riquadro)

    def _sfondo_e_puntino(self, centro_3857):
        """Lo sfondo dell'inserto e il puntino del sito. ``(sfondo, punto)``.

        Lo sfondo è una sorgente XYZ: si scarica dalla rete, e se la rete
        non c'è resta ``None`` — l'inserto mostra il solo puntino su
        fondo bianco, che dice meno ma non è un errore. In scavo capita.
        """
        from qgis.core import (QgsCoordinateReferenceSystem, QgsFeature,
                               QgsGeometry, QgsMarkerSymbol, QgsPointXY,
                               QgsRasterLayer, QgsVectorLayer)
        from qgis.PyQt.QtCore import QSettings

        tipo = str(QSettings().value("pyarchinit/atlas_basemap",
                                     DEFAULT_BASE_MAP) or DEFAULT_BASE_MAP)
        sfondo = None
        try:
            candidato = QgsRasterLayer(base_map_uri(tipo),
                                       base_map_name(tipo), "wms")
            if candidato.isValid():
                sfondo = candidato
            else:
                QgsMessageLog.logMessage(
                    "Sfondo dell'inserto non disponibile (%s): l'inserto "
                    "mostrerà il solo puntino." % base_map_name(tipo),
                    "PyArchInit", Qgis.MessageLevel.Info)
        except Exception as e:                      # noqa: BLE001
            QgsMessageLog.logMessage(
                "Sfondo dell'inserto non caricato: %s" % e,
                "PyArchInit", Qgis.MessageLevel.Info)

        punto = QgsVectorLayer("Point?crs=EPSG:3857", "Localizzazione",
                               "memory")
        try:
            f = QgsFeature()
            f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(*centro_3857)))
            punto.dataProvider().addFeatures([f])
            punto.updateExtents()
            punto.renderer().setSymbol(QgsMarkerSymbol.createSimple({
                "name": "circle", "color": "214,45,45",
                "outline_color": "255,255,255", "outline_width": "0.4",
                "size": "3.2"}))
        except Exception:                           # noqa: BLE001
            return sfondo, None
        return sfondo, punto

    def _prepara_panoramica(self, mappe, indice_principale, riquadro):
        """L'inserto dice dove si è nel mondo, non ripete lo scavo.

        Sfondo OpenStreetMap (o satellite, da impostazione) e un solo
        puntino sul sito. Prima l'inserto seguiva i layer del progetto e
        mostrava le stesse US della mappa grande, in piccolo: non diceva
        niente che non ci fosse già (Enzo, 2026-10-09).
        """
        from qgis.core import (QgsCoordinateReferenceSystem,
                               QgsCoordinateTransform, QgsPointXY,
                               QgsRectangle)

        inserti = overview_indexes(
            [(m.sizeWithUnits().width(), m.sizeWithUnits().height())
             for m in mappe], indice_principale)
        if not inserti or not riquadro:
            return
        try:
            centro = QgsPointXY((riquadro[0] + riquadro[2]) / 2.0,
                                (riquadro[1] + riquadro[3]) / 2.0)
            sorgente = mappe[indice_principale].crs()
            if not sorgente.isValid():
                sorgente = QgsProject.instance().crs()
            verso = QgsCoordinateReferenceSystem("EPSG:3857")
            centro = QgsCoordinateTransform(
                sorgente, verso, QgsProject.instance()).transform(centro)
        except Exception as e:                      # noqa: BLE001
            QgsMessageLog.logMessage(
                "Inserto non preparato (coordinate): %s" % e,
                "PyArchInit", Qgis.MessageLevel.Warning)
            return

        sfondo, punto = self._sfondo_e_puntino((centro.x(), centro.y()))
        if punto is None:
            return
        strati = [punto] + ([sfondo] if sfondo is not None else [])
        # Fuori dalla legenda: sono roba della tavola, non del progetto di
        # chi sta scavando. Si tolgono alla fine della generazione.
        self._strati_panoramica = []
        for strato in strati:
            try:
                QgsProject.instance().addMapLayer(strato, False)
                self._strati_panoramica.append(strato)
            except Exception:                       # noqa: BLE001
                continue

        finestra = overview_window((centro.x(), centro.y()))
        for i in inserti:
            inserto = mappe[i]
            try:
                inserto.setCrs(QgsCoordinateReferenceSystem("EPSG:3857"))
                inserto.setKeepLayerSet(True)
                inserto.setLayers(strati)
                inserto.zoomToExtent(QgsRectangle(*finestra))
            except Exception as e:                  # noqa: BLE001
                QgsMessageLog.logMessage(
                    "Inserto non preparato: %s" % e, "PyArchInit",
                    Qgis.MessageLevel.Warning)

    def _metti_le_etichette(self):
        """Numero dell'unità e quota sulla tavola, e come erano prima.

        Si etichettano i layer del progetto, perché è quello che la mappa
        del layout disegna; lo stato di prima si tiene e si rimette a fine
        generazione — la tavola non deve lasciare il progetto diverso da
        come l'ha trovato.
        """
        from qgis.core import QgsWkbTypes

        self._etichette_di_prima = []
        for layer in (self.selected_layers or []):
            try:
                campi = [f.name() for f in layer.fields()]
                tipo = layer.geometryType()
                if tipo == QgsWkbTypes.GeometryType.PolygonGeometry:
                    # un'etichetta per unità, e solo per quelle che si
                    # vedono: il conto si fa qui, una volta, con
                    # l'indice spaziale.
                    nuove = us_labeling(campi, labelled_ids(layer))
                elif tipo == QgsWkbTypes.GeometryType.PointGeometry:
                    nuove = quota_labeling(campi)
                else:
                    continue
                if nuove is None:
                    continue
                self._etichette_di_prima.append(
                    (layer, layer.labeling(), layer.labelsEnabled()))
                layer.setLabeling(nuove)
                layer.setLabelsEnabled(True)
            except Exception as e:                  # noqa: BLE001
                QgsMessageLog.logMessage(
                    "Etichette non applicate a %s: %s" % (layer.name(), e),
                    "PyArchInit", Qgis.MessageLevel.Warning)

    def _togli_le_etichette(self):
        """Rimette le etichette com'erano prima della generazione."""
        for layer, prima, attive in getattr(self, "_etichette_di_prima", []) or []:
            try:
                layer.setLabeling(prima)
                layer.setLabelsEnabled(attive)
            except Exception:                       # noqa: BLE001
                continue
        self._etichette_di_prima = []

    def _butta_via_la_panoramica(self):
        """Toglie dal progetto gli strati che l'inserto ha usato."""
        for strato in getattr(self, "_strati_panoramica", []) or []:
            try:
                QgsProject.instance().removeMapLayer(strato.id())
            except Exception:                       # noqa: BLE001
                continue
        self._strati_panoramica = []

    def _chiedi(self, titolo, testo, bottoni=None):
        """Una domanda che NON blocca le altre finestre di QGIS.

        ``QMessageBox.question`` è modale all'applicazione: con il Layout
        Designer aperto gli impedisce i clic. Modale alla sola finestra
        del Time Manager, invece, il designer resta usabile.
        """
        finestra = QMessageBox(self)
        finestra.setWindowTitle(titolo)
        finestra.setText(testo)
        finestra.setIcon(QMessageBox.Icon.Question)
        if bottoni is not None:
            finestra.setStandardButtons(bottoni)
        else:
            finestra.setStandardButtons(QMessageBox.StandardButton.Yes
                                        | QMessageBox.StandardButton.No)
        finestra.setWindowModality(Qt.WindowModality.WindowModal)
        finestra.exec()
        return finestra.standardButton(finestra.clickedButton())

    def _informa(self, titolo, testo):
        """Un avviso che non blocca il Layout Designer."""
        finestra = QMessageBox(self)
        finestra.setWindowTitle(titolo)
        finestra.setText(testo)
        finestra.setIcon(QMessageBox.Icon.Information)
        finestra.setWindowModality(Qt.WindowModality.WindowModal)
        finestra.exec()

    def open_layout_designer(self):
        """Apre il Layout Designer di QGIS per modificare il template corrente"""
        if not self.current_layout:
            QMessageBox.warning(self, "Warning", "Nessun layout caricato.")
            return
            
        try:
            # Ottieni il layout manager
            layout_manager = QgsProject.instance().layoutManager()
            
            # Controlla se il layout è già nel progetto
            existing_layout = layout_manager.layoutByName(self.current_layout.name())
            if not existing_layout:
                # Aggiungi il layout al progetto se non esiste
                layout_manager.addLayout(self.current_layout)
            
            # Apri il designer
            from qgis.utils import iface
            iface.openLayoutDesigner(self.current_layout)
            
            # Modale alla sola finestra del Time Manager: il designer
            # appena aperto deve restare usabile (Enzo, 2026-10-09).
            self._informa(
                "Layout Designer",
                "Il Layout Designer è stato aperto per il template: "
                "%s\n\n"
                "Puoi modificare:\n"
                "• Posizione e dimensioni degli elementi\n"
                "• Stili, colori e font\n"
                "• Aggiungere nuovi elementi (testo, immagini, ecc.)\n"
                "• Configurare la mappa e la scala\n\n"
                "Lascia pure il designer aperto: questa finestra non lo "
                "blocca." % self.current_layout.name())
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Errore Layout Designer",
                f"Errore nell'apertura del Layout Designer:\n{str(e)}"
            )

    def save_current_as_template(self):
        """Salva il layout corrente come nuovo template"""
        if not self.current_layout:
            QMessageBox.warning(self, "Warning", "Nessun layout caricato.")
            return
            
        # Chiedi il nome del nuovo template
        template_name, ok = QInputDialog.getText(
            self, 
            "Salva Template", 
            "Inserisci il nome per il nuovo template:",
            text="Nuovo_Template_Atlas"
        )
        
        if not ok or not template_name.strip():
            return
            
        # Assicurati che abbia l'estensione .qpt
        if not template_name.endswith('.qpt'):
            template_name += '.qpt'
            
        # Cartella di destinazione
        template_dir = os.path.join(os.path.dirname(__file__), '..', 'resources', 'dbfiles')
        if not os.path.exists(template_dir):
            os.makedirs(template_dir)
            
        template_path = os.path.join(template_dir, template_name)
        
        # Controlla se esiste già
        if os.path.exists(template_path):
            reply = QMessageBox.question(
                self, 
                "File Esiste", 
                f"Il template '{template_name}' esiste già. Sovrascrivere?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        try:
            # Salva il layout come template
            document = QDomDocument()
            context = QgsReadWriteContext()
            layout_element = document.createElement("Layout")
            
            self.current_layout.writeXml(layout_element, document, context)
            document.appendChild(layout_element)
            
            with open(template_path, 'w') as f:
                f.write(document.toString())
                
            QMessageBox.information(
                self, 
                "Template Salvato", 
                f"Template salvato con successo:\n{template_path}"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Errore Salvataggio", 
                f"Errore durante il salvataggio del template:\n{str(e)}"
            )

    def generate_images(self):
        # Prima scegli il template
        template_path = self.choose_template()
        if not template_path:
            return
            
        # Poi scegli la cartella di destinazione
        self.path = QFileDialog.getExistingDirectory(self, 'Selezionare una cartella per salvare le tavole', '/')
        if not self.path:
            return
            
        # Get reference to active QgsMapCanvas:
        #logging.info('Start generating images.')
        canvas = self.iface.mapCanvas()
        
        # Carica il template scelto
        print(f"Caricando template: {template_path}")
        self.load_template(template_path)
        if not self.current_layout:
            QMessageBox.warning(self, "Errore Template", 
                              f"Impossibile caricare il template:\n{template_path}")
            return

        # Che cosa sa fare questo modello, detto PRIMA di cominciare: senza
        # mappa non si va da nessuna parte, senza titolo o senza immagine
        # della matrice si va lo stesso, con tavole più spoglie.
        try:
            caps = capabilities(open(template_path, encoding='utf-8',
                                     errors='replace').read())
        except Exception:                           # noqa: BLE001
            caps = {"map": True, "title": True, "matrix": True}
        if not is_usable(caps):
            QMessageBox.warning(self, "Atlas", describe_missing(caps))
            return
        manca = describe_missing(caps)
        if manca and self._chiedi(
                "Atlas", manca + "\n\nVuoi procedere lo stesso?"
        ) != QMessageBox.StandardButton.Yes:
            return
            
        # Chiedi se vuole modificare il template prima di procedere
        reply = self._chiedi(
            "Modifica Template",
            "Vuoi aprire il Layout Designer per modificare il template "
            "prima di generare l'atlas?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            | QMessageBox.StandardButton.Cancel)
        
        if reply == QMessageBox.StandardButton.Cancel:
            return
        elif reply == QMessageBox.StandardButton.Yes:
            # Apri il layout designer
            self.open_layout_designer()
            
            # Chiedi conferma per procedere. Modale alla NOSTRA finestra
            # soltanto: il Layout Designer è un'altra finestra di primo
            # livello, e una QMessageBox modale all'applicazione gli
            # impedisce i clic — «la finestra del Time Manager blocca la
            # finestra del layout» (Enzo, 2026-10-09).
            proceed = self._chiedi(
                "Continua Atlas",
                "Hai terminato le modifiche al layout?\n"
                "Procedere con la generazione dell'atlas?",
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No)
            if proceed != QMessageBox.StandardButton.Yes:
                return

        max_num_order_layer = self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, "order_layer")
        if max_num_order_layer is None:
            # Nessuna US numerata: senza questa guardia era un TypeError
            # su None + 1, cioè il generatore che «non parte».
            self._informa(
                "Atlas",
                "Nessuna US ha un valore di «order_layer»: non c'è una "
                "sequenza da cui ricavare le tavole.")
            return
        total_order_layers = max_num_order_layer + 1  # da 0 a max incluso
        
        # Optimized: single SQL query instead of O(levels * layers * features) scan
        try:
            valid_result = self.DB_MANAGER._execute_sql(
                "SELECT COUNT(DISTINCT order_layer) FROM us_table "
                "WHERE order_layer IS NOT NULL AND datazione IS NOT NULL AND TRIM(datazione) != ''"
            )
            valid_count = 0
            for row in valid_result:
                valid_count = row[0] if row[0] else 0
                break
        except Exception:
            valid_count = max_num_order_layer + 1

        if valid_count == 0:
            self._informa("Info", "Nessun order_layer con datazione valida trovato.")
            return
        
        # Crea progress dialog per tutti gli order_layer (inclusi quelli skippati)
        progress = QProgressDialog("Generazione tavole in corso...", "Annulla", 0, total_order_layers, self)
        progress.setWindowTitle("Generazione Atlas")
        progress.setWindowModality(Qt.WindowModality.NonModal)  # Non bloccare l'interfaccia
        progress.setAutoClose(False)  # Non chiudere automaticamente
        progress.setAutoReset(False)  # Non reset automaticamente
        progress.show()
        progress_count = 0
        non_scritte = []
        # Una volta sola, prima di cominciare: stessa scala su tutte le
        # tavole. Senza, la stessa US cambierebbe dimensione da una
        # pagina all'altra.
        self._riquadro_atlante = self._riquadro_del_sito()
        # Numero dell'unità in un cerchio e quota sopra la linea del
        # simbolo: si mettono una volta e si tolgono alla fine.
        self._metti_le_etichette()
        # Durante la generazione la manopola si muove da sola: il timer
        # di debounce rifarebbe filtro e matrice in mezzo al ciclo.
        self._atlante_in_corso = True
        
        print(f"=== DEBUG: Inizio atlas generation ===")
        print(f"Total order layers to process: {total_order_layers} (0 to {max_num_order_layer})")
        print(f"Order layers with valid datazione: {valid_count}")
        print(f"Max order layer: {max_num_order_layer}")
        
        print(f"Inizio generazione atlas per {valid_count} order_layer validi su {total_order_layers} totali...")
        
        # Usa tutti gli order_layer da 0 al massimo
        # Il controllo per la datazione verrà fatto durante l'iterazione
        for value in range(0, max_num_order_layer + 1):
            print(f"DEBUG: Processing order_layer {value}")
            if self.abort or progress.wasCanceled():
                print(f"DEBUG: Aborted at order_layer {value}")
                self.abort = False  # resetta l'attributo per il prossimo utilizzo
                break
            self.current_value = value
            self.image_saved = False

            # Imposta il valore dello spinbox sul valore corrente
            self.spinBox_relative_cronology.setValue(value)

            # Aggiorna i dati del layer in base al valore corrente dello spinbox
            #logging.info('Update layer data.')
            self.define_order_layer_value(value)

            # Aggiorna la visualizzazione della mappa per assicurarsi che mostri gli aggiornamenti ai dati del layer

            canvas.refresh()
            # Wait for canvas rendering without blocking
            loop = QEventLoop()
            canvas.renderComplete.connect(loop.quit)
            QTimer.singleShot(10000, loop.quit)  # 10s safety timeout
            if canvas.isDrawing():
                loop.exec_()
            #QThread.sleep(2)

            #QMessageBox.information(None, 'ok', f"{self.current_layout}")# Define the area of the layout to be exported

            mappe = [i for i in self.current_layout.items()
                     if isinstance(i, QgsLayoutItemMap)]
            if not mappe:
                self._atlante_in_corso = False
                progress.close()
                QMessageBox.warning(
                    self, "Atlas",
                    "Il modello scelto non contiene nessuna mappa: non ci "
                    "si può disegnare una tavola.\nScegline un altro, per "
                    "esempio «layout_TimeManager».")
                return
            layoutItemMap = mappe[0]
            # La mappa del layout va INQUADRATA: senza, conserva
            # l'inquadratura con cui il template fu salvato — su un altro
            # progetto, altrove — e disegna il niente. È il motivo per cui
            # «i layout sono vuoti» (Enzo, 2026-10-09). PRINTMAP lo fa già
            # (PRINTMAP.py:254); qui `layoutItemMap` si calcolava e non si
            # usava mai.
            self._inquadra_tavola(mappe)

            # Ottieni l'elemento HTML dalla layout
            html_item = None
            for i in self.current_layout.items():
                if hasattr(i, 'id') and i.id() == '123':#123 è l'id dell'elemento HTML
                    html_item = i
                    break
            if html_item is None:
                # Prima qui si tornava indietro in silenzio, con la barra
                # di avanzamento aperta e nessuna tavola: è il motivo per
                # cui «a volte parte e a volte no» (Enzo, 2026-10-09).
                # Un modello senza la casella del titolo fa le tavole lo
                # stesso, solo senza titolo.
                if not self._avvisato_senza_titolo:
                    self._avvisato_senza_titolo = True
                    QgsMessageLog.logMessage(
                        "Il modello non ha il titolo «Tavola N» (id %r): "
                        "le tavole escono senza titolo." % TITLE_ID,
                        "PyArchInit", Qgis.MessageLevel.Info)
            #QMessageBox.information(None, 'ok', str(type(html_item)))
            if html_item is not None and isinstance(html_item, QgsLayoutFrame):
                # Ottieni il multiframe a cui appartiene questo frame
                multi_frame = html_item.multiFrame()

                #QMessageBox.information(None, 'ok', f"Multi frame: {multi_frame}, type: {type(multi_frame)}")# Controlla se il multiframe è un QgsLayoutItemHtml
                if isinstance(multi_frame, QgsLayoutItemHtml):
                    title_html = f"<h1>Tavola {value}</h1>"
                    multi_frame.setHtml(title_html)
                    #QMessageBox.information(None, 'ok', f"HTML content: {multi_frame.html()}")
                    self.current_layout.refresh()
                    multi_frame.loadHtml()
                    #break

            # I modelli generici portano un segnaposto «{{title}}» nelle
            # etichette, che PRINTMAP sostituisce già (PRINTMAP.py:252) e
            # il Time Manager no: sulla tavola si leggeva «{{title}}»
            # stampato così com'è (visto nelle prove del 2026-10-09).
            for elemento in self.current_layout.items():
                try:
                    if elemento.type() == 65641 and '{{title}}' in elemento.text():
                        elemento.setText(elemento.text().replace(
                            '{{title}}', 'Tavola %s' % value))
                except Exception:                   # noqa: BLE001
                    continue

            self.id_us_dict = {}

            # Raccogli solo le US visibili nel layer corrente (order_layer <= value)
            data_list = []
            visible_us_list = []
            has_valid_datazione = False
            
            for layer in self.selected_layers:
                fields = layer.fields()
                self.fieldname = next((field.name() for field in fields if 'datazione' in field.name().lower()), '')
                if not self.fieldname:
                    print(f"No 'datazione' field found in layer {layer.name()}")
                    continue

                # Ottieni solo le features visibili (che rispettano il filtro corrente)
                request = layer.getFeatures()
                for feature in request:
                    feature_order_layer = feature.attribute("order_layer")
                    
                    # Include solo le US con order_layer <= valore corrente
                    if feature_order_layer is not None and feature_order_layer <= value:
                        datazione = feature.attribute(self.fieldname)
                        
                        # Controlla se almeno una US ha datazione per questo order_layer
                        if feature_order_layer == value and datazione and str(datazione).strip() != '':
                            has_valid_datazione = True
                        
                        data_dict = {field.name(): feature[field.name()] for field in feature.fields()}
                        data_list.append(data_dict)
                        
                        # Aggiungi alla lista delle US visibili
                        us_val = feature.attribute("us")
                        area_val = feature.attribute("area")
                        if us_val is not None and area_val is not None:
                            visible_us_list.append((str(area_val), str(us_val)))
            
            # Aggiorna progress dialog per tutti gli order_layer
            progress_count += 1
            progress.setValue(progress_count)
            
            # Salta questo order_layer se non ha datazione valida
            if not has_valid_datazione:
                progress.setLabelText(f"Saltando order_layer {value} (nessuna datazione) - {progress_count}/{total_order_layers}")
                print(f"Skipping order_layer {value} - no valid datazione")
                continue
            
            progress.setLabelText(f"Generando Tavola {value} - {progress_count}/{total_order_layers}")
            print(f"DEBUG: Progress updated - Generando Tavola {value} ({progress_count}/{total_order_layers})")
            
            # Controlla se l'utente ha annullato
            if progress.wasCanceled():
                self.abort = True
                break

            # Ottieni l'elemento immagine dal layout
            image_item = None
            for i in self.current_layout.items():
                if hasattr(i, 'id') and i.id() == 'matrix':  # 'matrix' è l'id dell'elemento immagine
                    image_item = i
                    break
            if image_item is None:
                # Come sopra: senza l'immagine la tavola si fa, senza la
                # matrice dentro.
                if not self._avvisato_senza_matrice:
                    self._avvisato_senza_matrice = True
                    QgsMessageLog.logMessage(
                        "Il modello non ha l'immagine della matrice "
                        "(id %r): le tavole escono senza matrice."
                        % MATRIX_ID, "PyArchInit", Qgis.MessageLevel.Info)

            # controllo se il checkbox 'matrix' è attivo
            if image_item is None:
                pass
            elif bool(self.checkBox_matrix.isChecked()) and data_list:
                # Passa solo i dati delle US visibili alla generazione della matrice
                HOME = os.environ.get('PYARCHINIT_HOME', os.path.expanduser('~'))
                cartella = '{}{}{}'.format(HOME, os.sep,
                                           "pyarchinit_Matrix_folder")
                os.makedirs(cartella, exist_ok=True)
                # Un SVG: nella tavola è vettoriale e pesa qualche decina
                # di KB invece dei megabyte del JPEG di Graphviz.
                matrix_image, _modello = self._disegna_matrice(
                    data_list, visible_us_list,
                    os.path.join(cartella, "Harris_matrix_timemanager.svg"))

                if matrix_image:
                    # Impostare l'immagine della matrice sull'elemento immagine
                    if isinstance(image_item, QgsLayoutItemPicture):

                        image_item.setPicturePath(matrix_image)
                        image_item.setMode(QgsLayoutItemPicture.FormatSVG)




                elif not self._avvisato_senza_matrice:
                    # Una volta sola: un avviso per livello avrebbe
                    # fermato la generazione con decine di finestre.
                    self._avvisato_senza_matrice = True
                    QgsMessageLog.logMessage(
                        "Matrice non disegnata per la tavola %s" % value,
                        "PyArchInit", Qgis.MessageLevel.Warning)
                image_item.setVisibility(True)

            else:
                # Se il checkbox 'matrix' non è spuntato, rendi l'elemento immagine invisibile
                image_item.setVisibility(False)

            self.current_layout.refresh()
            exporter = QgsLayoutExporter(self.current_layout)
            image_path = f"{self.path}/Tavola_{value}.jpg"
            print(f"DEBUG: Exporting Tavola_{value}.jpg to {image_path}")
            esito = exporter.exportToImage(
                image_path, QgsLayoutExporter.ImageExportSettings())
            if esito != QgsLayoutExporter.Success:
                # Prima l'esito si buttava via: una cartella non
                # scrivibile dava tavole mancanti senza una parola.
                non_scritte.append(value)
                QgsMessageLog.logMessage(
                    "Tavola %s non scritta in %s (codice %s)"
                    % (value, image_path, esito), "PyArchInit",
                    Qgis.MessageLevel.Warning)
            else:
                print(f"DEBUG: ✓ Tavola_{value}.jpg exported successfully")
            # Rimuovi la graphicsView esistente dal layout
            self.horizontalLayout_2.removeWidget(self.graphicsView)

            # Crea una nuova ZoomableGraphicsView
            self.graphicsView = ZoomableGraphicsView()

            # Aggiungi la ZoomableGraphicsView al layout
            self.horizontalLayout_2.addWidget(self.graphicsView)

            # Procedi come prima
            pixmap = QPixmap(image_path)
            scene = QGraphicsScene()
            scene.addPixmap(pixmap)
            self.graphicsView.setScene(scene)
            self.graphicsView.setFocus()
            self.graphicsView.fitInView(scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)
        
        # Chiudi progress bar e mostra messaggio di completamento
        self._atlante_in_corso = False
        self._riquadro_atlante = None
        self._togli_le_etichette()
        self._butta_via_la_panoramica()
        progress.close()
        
        if not self.abort and not progress.wasCanceled():
            coda = ("\n\nNON scritte: %s — controlla che la cartella sia "
                    "scrivibile." % ", ".join(str(v) for v in non_scritte)
                    ) if non_scritte else ""
            self._informa("Atlas Completato",
                          "Generazione atlas completata con successo!\n"
                          "Order layers processati: %s/%s\n"
                          "Tavole con datazione valida generate: %s\n"
                          "Salvate in: %s%s"
                          % (progress_count, total_order_layers, valid_count,
                             self.path, coda))
            print(f"Atlas generato con successo: {valid_count} tavole create su {progress_count} order_layer processati")
        else:
            self._informa("Atlas Interrotto",
                          "Generazione atlas interrotta dall'utente.\n"
                          "Order layers processati prima "
                          "dell'interruzione: %s/%s"
                          % (progress_count, total_order_layers))
            print("Generazione atlas interrotta dall'utente")

    def stop_processes_named(self, name):
        for proc in psutil.process_iter(['pid', 'name']):
            # Verifica se il nome del processo corrisponde a quello che stai cercando
            process_info = proc.as_dict(attrs=['pid', 'name'])
            if process_info['name'] == name:
                try:
                    proc.kill()  # Termina il processo
                except psutil.NoSuchProcess:
                    QMessageBox.information(None, 'Avviso', f"Processo {name} non trovato")

    def stop_image_generation(self):
        if platform.system() == 'Windows':
            self.stop_processes_named('dot.exe')
        elif platform.system() == 'Darwin':  # macOS
            self.stop_processes_named('dot')
        elif platform.system() == 'Linux':
            self.stop_processes_named('dot')
        self.abort = True
