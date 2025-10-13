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
from qgis.PyQt.QtWidgets import QFileDialog, QGraphicsScene,  QGraphicsView, QListWidgetItem, QDialog, QMessageBox, QProgressDialog
from qgis.PyQt.QtCore import Qt, pyqtSlot, QCoreApplication, QThread
from qgis.core import Qgis,QgsLayoutFrame, QgsMessageLog, QgsProject, QgsLayoutExporter, QgsApplication, QgsLayoutItemMap, QgsReadWriteContext, QgsPrintLayout,QgsLayoutMultiFrame, QgsLayoutItemHtml, QgsLayoutItemPicture
from qgis.PyQt.QtXml import QDomDocument

from ..modules.db.pyarchinit_utility import Utility
from .Interactive_matrix import *
MAIN_DIALOG_CLASS, _ = loadUiType(
    os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'Gis_Time_controller.ui'))

class ZoomableGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.ScrollHandDrag)

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
    L=QgsSettings().value("locale/userLocale")[0:2]
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
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.listWidget.addItem(item)
        self.abort = False

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
            self.DB_MANAGER = Pyarchinit_db_management(conn_str)
            self.DB_MANAGER.connection()
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
                                self.listWidget.item(i).checkState() == Qt.Checked]
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
                    self.graphicsView.fitInView(scene.itemsBoundingRect(), Qt.KeepAspectRatio)



            except AssertionError as e:

                QMessageBox.warning(self, "Alert", str(e))

    def define_order_layer_value(self, v):
        if self.selected_layers is None or not self.selected_layers:
            QgsMessageLog.logMessage('I layer Quote View e US View devono essere caricati.', 'Avviso')
            return

        sito = "','".join(self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('us_table', 'sito', 'US')))
        area = "','".join(self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('us_table', 'area', 'US')))

        self.ORDER_LAYER_VALUE = v

        for layer in self.selected_layers:
            data_provider = layer.dataProvider()
            self.liststring(sito, area, layer, data_provider)




    def update_datazione(self, value):
        # Cerca il valore dello spinBox nel dizionario e imposta il valore del textEdit_datazione corrispondente
        datazioni = self.datazione_dict.get(value, [])
        # Rimuove i duplicati convertendo la lista in un set
        unique_datazioni = set(datazioni)
        self.textEdit_datazione.setPlainText('\n'.join(map(str, unique_datazioni)))

    def liststring(self, sito, area, i, e):
        new_sub_set_string = f"order_layer <= {self.ORDER_LAYER_VALUE} AND sito IN ('{sito}') AND area IN ('{area}')"
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
                                    QMessageBox.Ok)
        
            elif self.L=='de': 
                QMessageBox.warning(self, "Alert", "Es gibt keine Perioden in diesem Zeitintervall.",
                                    QMessageBox.Ok)
            else: 
                QMessageBox.warning(self, "Alert", "There are no Periods in this time interval",
                                    QMessageBox.Ok)
            
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
                    QMessageBox.warning(self, "Alert", "Non ci sono geometrie da visualizzare", QMessageBox.Ok)

                elif self.L=='de':
                    QMessageBox.warning(self, "Alert", "es gibt keine Geometrien, die angezeigt werden können", QMessageBox.Ok) 
                else:
                    QMessageBox.warning(self, "Alert", "There are no geometries to display", QMessageBox.Ok)    
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



    def generate_images(self):
        # Aprire un dialogo per la selezione del percorso del file
        self.path = QFileDialog.getExistingDirectory(self, 'Selezionare una cartella', '/')
        if not self.path:
            return
        # Get reference to active QgsMapCanvas:
        #logging.info('Start generating images.')
        canvas = self.iface.mapCanvas()
        # Carica il template
        HOME = os.environ['PYARCHINIT_HOME']
        path = '{}{}{}{}'.format(HOME, os.sep, "bin/profile/template/", 'layout_TimeManager.qpt')

        self.load_template(path)
        if not self.current_layout:
            return

        max_num_order_layer = self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, "order_layer")
        
        # Calcola quanti order_layer hanno datazione valida per la progress bar
        valid_order_layers = []
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
                valid_order_layers.append(value)
        
        if not valid_order_layers:
            QMessageBox.information(self, "Info", "Nessun order_layer con datazione valida trovato.")
            return
        
        # Crea progress dialog non modale
        progress = QProgressDialog("Generazione tavole in corso...", "Annulla", 0, len(valid_order_layers), self)
        progress.setWindowTitle("Generazione Atlas")
        progress.setWindowModality(Qt.NonModal)  # Non bloccare l'interfaccia
        progress.setAutoClose(False)  # Non chiudere automaticamente
        progress.setAutoReset(False)  # Non reset automaticamente
        progress.show()
        progress_count = 0
        
        print(f"=== DEBUG: Inizio atlas generation ===")
        print(f"Valid order layers: {valid_order_layers}")
        print(f"Max order layer: {max_num_order_layer}")
        
        print(f"Inizio generazione atlas per {len(valid_order_layers)} order_layer validi...")
        
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
            
            # Salta questo order_layer se non ha datazione valida
            if not has_valid_datazione:
                print(f"Skipping order_layer {value} - no valid datazione")
                continue
            
            # Aggiorna progress dialog
            progress_count += 1
            progress.setValue(progress_count)
            progress.setLabelText(f"Generando Tavola {value} ({progress_count}/{len(valid_order_layers)})...")
            
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
            self.graphicsView.fitInView(scene.itemsBoundingRect(), Qt.KeepAspectRatio)
        
        # Chiudi progress bar e mostra messaggio di completamento
        progress.close()
        
        if not self.abort and not progress.wasCanceled():
            QMessageBox.information(self, "Atlas Completato", 
                                  f"Generazione atlas completata con successo!\n"
                                  f"Tavole generate: {progress_count}\n"
                                  f"Salvate in: {self.path}")
            print(f"Atlas generato con successo: {progress_count} tavole create")
        else:
            QMessageBox.information(self, "Atlas Interrotto", 
                                  f"Generazione atlas interrotta dall'utente.\n"
                                  f"Tavole generate prima dell'interruzione: {progress_count}")
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
