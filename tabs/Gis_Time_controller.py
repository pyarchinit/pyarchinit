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

import sys


from qgis.PyQt.QtGui import QPixmap, QPainter, QImage


from qgis.PyQt.QtWidgets import QVBoxLayout, QGraphicsScene,  QGraphicsView, QListWidgetItem,QApplication, QDialog, QMessageBox
from qgis.PyQt.QtCore import Qt

from qgis.core import Qgis, QgsMessageLog, QgsProject
from ..modules.db.pyarchinit_utility import Utility

from .US_USM import pyarchinit_US
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

        self.listWidget.itemChanged.connect(self.update_selected_layers)


        self.dial_relative_cronology.valueChanged.connect(self.set_max_num)
        self.spinBox_relative_cronology.valueChanged.connect(self.set_max_num)

        self.dial_relative_cronology.valueChanged.connect(self.define_order_layer_value)
        self.dial_relative_cronology.valueChanged.connect(self.spinBox_relative_cronology.setValue)

        self.spinBox_relative_cronology.valueChanged.connect(self.define_order_layer_value)
        self.spinBox_relative_cronology.valueChanged.connect(self.dial_relative_cronology.setValue)
        self.listWidget.itemSelectionChanged.connect(self.update_selected_layers)

        #self.update_graphics_view_test()
        self.spinBox_relative_cronology.valueChanged.connect(self.update_graphics_view)
        if self.checkBox_matrix.isChecked():
            self.update_graphics_view()
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


        max_num_order_layer = self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, "order_layer") + 1,
        self.dial_relative_cronology.setMaximum(max_num_order_layer[0])
        self.spinBox_relative_cronology.setMaximum(max_num_order_layer[0])

        self.spinBox_relative_cronology.valueChanged.connect(self.update_datazione)
        self.update_datazione(self.spinBox_relative_cronology.value())
        self.update_datazione(self.dial_relative_cronology.value())





    def update_graphics_view(self):
        if self.checkBox_matrix.isChecked():
            try:
                self.id_us_dict = {}

                data_list = []
                for layer in self.selected_layers:

                    fields = layer.fields()
                    self.fieldname = next((field.name() for field in fields if 'datazione' in field.name().lower()), '')
                    if not self.fieldname:
                        print(f"No 'datazione' field found in layer {layer.name()}")
                        continue
                    #self.us = next((field.name() for field in fields if 'us' in field.name().lower()), '')
                    #self.rapporti = next((field.name() for field in fields if 'rapporti' in field.name().lower()), '')
                    # Crea un dizionario che mappa ogni attributo "us" a una lista di attributi "datazione" corrispondenti

                    for feature in layer.getFeatures():
                        data_dict = {field.name(): feature[field.name()] for field in feature.fields()}
                        data_list.append(data_dict)
                        order_layer = feature.attribute("order_layer")
                        datazione = feature.attribute(self.fieldname)
                        if order_layer in self.id_us_dict:
                            self.id_us_dict[order_layer].append(datazione)
                        else:
                            self.id_us_dict[order_layer] = [datazione]

                dlg = pyarchinit_view_Matrix_pre(self.iface, data_list, self.id_us_dict)
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



