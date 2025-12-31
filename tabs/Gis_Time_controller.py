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
from qgis.PyQt.QtCore import Qt, pyqtSlot, QCoreApplication, QThread, QRectF
from qgis.core import Qgis,QgsLayoutFrame, QgsMessageLog, QgsProject, QgsLayoutExporter, QgsApplication, QgsLayoutItemMap, QgsReadWriteContext, QgsPrintLayout,QgsLayoutMultiFrame, QgsLayoutItemHtml, QgsLayoutItemPicture, QgsLayoutItemLabel
from qgis.PyQt.QtXml import QDomDocument

from ..modules.db.pyarchinit_utility import Utility
from .Interactive_matrix import *
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
        self.dial_relative_cronology.valueChanged.connect(self.define_order_layer_value)
        self.dial_relative_cronology.valueChanged.connect(self.spinBox_relative_cronology.setValue)
        self.spinBox_relative_cronology.valueChanged.connect(self.define_order_layer_value)
        self.spinBox_relative_cronology.valueChanged.connect(self.dial_relative_cronology.setValue)
        self.listWidget.itemSelectionChanged.connect(self.update_selected_layers)
        self.spinBox_relative_cronology.valueChanged.connect(self.update_graphics_view)
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


    def update_layers(self, layers):
        # 'layers' è una lista di oggetti QgsMapLayer.
        # Qui implementi la logica per gestire i layer selezionati.
        self.selected_layers = layers  # memorizza i layer selezionati in un attributo dell'istanza

    def set_max_num(self):


        if self.selected_layers is None or not self.selected_layers:
            self.listWidget.addItem('I layer Quote View e US View devono essere caricati.')
            return

        self.datazione_dict = {}

        for us_layer in self.selected_layers:
            fields = us_layer.fields()
            self.fieldname = next((field.name() for field in fields if 'datazione' in field.name().lower()), '')

            if not self.fieldname:
                print(f"No 'datazione' field found in layer {us_layer.name()}")
                continue

            # Crea un dizionario che mappa ogni attributo "order_layer" a una lista di attributi "datazione" corrispondenti
            for feature in us_layer.getFeatures():
                order_layer = feature.attribute("order_layer")
                datazione = feature.attribute(self.fieldname)

                if order_layer in self.datazione_dict:
                    self.datazione_dict[order_layer].append(datazione)

                else:
                    self.datazione_dict[order_layer] = [datazione]

        max_num_order_layer = self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, "order_layer")
        if max_num_order_layer is not None:
            max_num_order_layer += 1
            self.dial_relative_cronology.setMaximum(max_num_order_layer)
            self.spinBox_relative_cronology.setMaximum(max_num_order_layer)
        else:
            # handle the error
            print("Errore: max_num_order_layer è None")

        self.spinBox_relative_cronology.valueChanged.connect(self.update_datazione)
        self.update_datazione(self.spinBox_relative_cronology.value())
        self.update_datazione(self.dial_relative_cronology.value())





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

                if data_list:  # Genera matrice solo se ci sono dati
                    dlg = pyarchinit_view_Matrix_pre(self.iface, data_list, self.id_us_dict)
                    dlg.visible_us_list = visible_us_list  # Passa la lista delle US visibili
                    dlg.generate_matrix_3()
                HOME = os.environ['PYARCHINIT_HOME']
                path = '{}{}{}{}'.format(HOME, os.sep, "pyarchinit_Matrix_folder/", 'Harris_matrix_viewtred.dot.jpg')
                if path:
                    # Rimuovi la graphicsView esistente dal layout
                    self.horizontalLayout_2.removeWidget(self.graphicsView)

                    # Crea una nuova ZoomableGraphicsView
                    self.graphicsView = ZoomableGraphicsView()

                    # Aggiungi la ZoomableGraphicsView al layout
                    self.horizontalLayout_2.addWidget(self.graphicsView)

                    # Procedi come prima
                    pixmap = QPixmap(path)
                    scene = QGraphicsScene()
                    scene.addPixmap(pixmap)
                    self.graphicsView.setScene(scene)
                    self.graphicsView.setFocus()
                    self.graphicsView.fitInView(scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)



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

        sito = "','".join(self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('us_table', 'sito', 'US')))
        area = "','".join(self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('us_table', 'area', 'US')))

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
        new_sub_set_string = f"order_layer {operator} {self.ORDER_LAYER_VALUE} AND sito IN ('{sito}') AND area IN ('{area}')"

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
        info_label = QLabel("Seleziona il template da utilizzare per la generazione dell'atlas:")
        layout.addWidget(info_label)
        
        # Lista template
        template_list = QListWidget()
        for name, path in templates:
            item = QListWidgetItem(f"{name}")
            item.setToolTip(f"Path: {path}")
            item.setData(Qt.ItemDataRole.UserRole, path)  # Salva il path nell'item
            template_list.addItem(item)
        
        # Seleziona il primo per default
        if template_list.count() > 0:
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
            
            QMessageBox.information(
                self,
                "Layout Designer",
                f"Il Layout Designer è stato aperto per il template: {self.current_layout.name()}\n\n"
                f"Puoi modificare:\n"
                f"• Posizione e dimensioni degli elementi\n"
                f"• Stili, colori e font\n"
                f"• Aggiungere nuovi elementi (testo, immagini, ecc.)\n"
                f"• Configurare la mappa e la scala\n\n"
                f"Chiudi il designer e clicca OK quando hai terminato le modifiche."
            )
            
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
            
        # Chiedi se vuole modificare il template prima di procedere
        reply = QMessageBox.question(
            self, 
            "Modifica Template", 
            "Vuoi aprire il Layout Designer per modificare il template prima di generare l'atlas?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
        )
        
        if reply == QMessageBox.StandardButton.Cancel:
            return
        elif reply == QMessageBox.StandardButton.Yes:
            # Apri il layout designer
            self.open_layout_designer()
            
            # Chiedi conferma per procedere
            proceed = QMessageBox.question(
                self,
                "Continua Atlas",
                "Hai terminato le modifiche al layout?\nProcedere con la generazione dell'atlas?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if proceed != QMessageBox.StandardButton.Yes:
                return

        max_num_order_layer = self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, "order_layer")
        total_order_layers = max_num_order_layer + 1  # da 0 a max incluso
        
        # Conta quanti order_layer hanno datazione valida (solo per info)
        valid_count = 0
        for value in range(0, max_num_order_layer + 1):
            has_valid_datazione = False
            for layer in self.selected_layers:
                fields = layer.fields()
                fieldname = next((field.name() for field in fields if 'datazione' in field.name().lower()), '')
                if fieldname:
                    for feature in layer.getFeatures():
                        if (feature.attribute("order_layer") == value and 
                            feature.attribute(fieldname) and 
                            str(feature.attribute(fieldname)).strip() != ''):
                            has_valid_datazione = True
                            break
                if has_valid_datazione:
                    break
            if has_valid_datazione:
                valid_count += 1
        
        if valid_count == 0:
            QMessageBox.information(self, "Info", "Nessun order_layer con datazione valida trovato.")
            return
        
        # Crea progress dialog per tutti gli order_layer (inclusi quelli skippati)
        progress = QProgressDialog("Generazione tavole in corso...", "Annulla", 0, total_order_layers, self)
        progress.setWindowTitle("Generazione Atlas")
        progress.setWindowModality(Qt.WindowModality.NonModal)  # Non bloccare l'interfaccia
        progress.setAutoClose(False)  # Non chiudere automaticamente
        progress.setAutoReset(False)  # Non reset automaticamente
        progress.show()
        progress_count = 0
        
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
            QCoreApplication.processEvents()  # Process system events to allow the refresh to start
            QThread.sleep(2)  # Wait for a second
            while canvas.isDrawing():
                QCoreApplication.processEvents()
            #QThread.sleep(2)

            #QMessageBox.information(None, 'ok', f"{self.current_layout}")# Define the area of the layout to be exported

            layoutItemMap = [i for i in self.current_layout.items() if isinstance(i, QgsLayoutItemMap)][0]

            # Ottieni l'elemento HTML dalla layout
            html_item = None
            for i in self.current_layout.items():
                if hasattr(i, 'id') and i.id() == '123':#123 è l'id dell'elemento HTML
                    html_item = i
                    break
            if html_item is None:
                print("Couldn't find HTML item")
                return
            #QMessageBox.information(None, 'ok', str(type(html_item)))
            if isinstance(html_item, QgsLayoutFrame):
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
                print("Couldn't find Image item")
                return

            # controllo se il checkbox 'matrix' è attivo
            if bool(self.checkBox_matrix.isChecked()) and data_list:
                # Passa solo i dati delle US visibili alla generazione della matrice
                dlg = pyarchinit_view_Matrix_pre(self.iface, data_list, self.id_us_dict)
                dlg.visible_us_list = visible_us_list  # Passa la lista delle US visibili
                dlg.generate_matrix_3()
                HOME = os.environ.get('PYARCHINIT_HOME', os.path.expanduser('~'))
                matrix_image = '{}{}{}{}'.format(HOME, os.sep, "pyarchinit_Matrix_folder/",
                                                 "Harris_matrix_viewtred.dot.jpg")  # path dell'immagine della matrice

                if matrix_image:
                    # Impostare l'immagine della matrice sull'elemento immagine
                    if isinstance(image_item, QgsLayoutItemPicture):

                        image_item.setPicturePath(matrix_image)
                        image_item.setMode(QgsLayoutItemPicture.FormatRaster)




                else:
                    QMessageBox.warning(self, "Attenzione",
                                        "L'immagine della matrice non è stata generata correttamente")
                image_item.setVisibility(True)

            else:
                # Se il checkbox 'matrix' non è spuntato, rendi l'elemento immagine invisibile
                image_item.setVisibility(False)

            self.current_layout.refresh()
            exporter = QgsLayoutExporter(self.current_layout)
            image_path = f"{self.path}/Tavola_{value}.jpg"
            print(f"DEBUG: Exporting Tavola_{value}.jpg to {image_path}")
            exporter.exportToImage(image_path, QgsLayoutExporter.ImageExportSettings())
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
        progress.close()
        
        if not self.abort and not progress.wasCanceled():
            QMessageBox.information(self, "Atlas Completato", 
                                  f"Generazione atlas completata con successo!\n"
                                  f"Order layers processati: {progress_count}/{total_order_layers}\n"
                                  f"Tavole con datazione valida generate: {valid_count}\n"
                                  f"Salvate in: {self.path}")
            print(f"Atlas generato con successo: {valid_count} tavole create su {progress_count} order_layer processati")
        else:
            QMessageBox.information(self, "Atlas Interrotto", 
                                  f"Generazione atlas interrotta dall'utente.\n"
                                  f"Order layers processati prima dell'interruzione: {progress_count}/{total_order_layers}")
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
