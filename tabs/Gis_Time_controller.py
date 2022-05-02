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
from builtins import str
from builtins import range
import sys
import os
# TODO: must be fixed
# from olefile.olefile import v

from qgis.PyQt.QtWidgets import QApplication, QDialog, QMessageBox
from qgis.PyQt.uic import loadUiType
from qgis.core import Qgis, QgsMessageLog, QgsSettings

from ..modules.db.pyarchinit_conn_strings import Connection
from ..modules.db.pyarchinit_db_manager import Pyarchinit_db_management
from ..modules.gis.pyarchinit_pyqgis import Pyarchinit_pyqgis
from .US_USM import pyarchinit_US

MAIN_DIALOG_CLASS, _ = loadUiType(
    os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'Gis_Time_controller.ui'))


class pyarchinit_Gis_Time_Controller(QDialog, MAIN_DIALOG_CLASS):
    L=QgsSettings().value("locale/userLocale")[0:2]
    MSG_BOX_TITLE = "PyArchInit - Gis Time Management"
    DB_MANAGER = ""
    ORDER_LAYER_VALUE = ""
    MAPPER_TABLE_CLASS = "US"

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

        self.dial_relative_cronology.valueChanged.connect(self.set_max_num)
        self.spinBox_relative_cronology.valueChanged.connect(self.set_max_num)

        self.dial_relative_cronology.valueChanged.connect(self.define_order_layer_value)
        self.dial_relative_cronology.valueChanged.connect(self.spinBox_relative_cronology.setValue)

        self.spinBox_relative_cronology.valueChanged.connect(self.define_order_layer_value)
        self.spinBox_relative_cronology.valueChanged.connect(self.dial_relative_cronology.setValue)

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

    def set_max_num(self):
        max_num_order_layer = self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, "order_layer") + 1,
        self.dial_relative_cronology.setMaximum(max_num_order_layer[0])
        self.spinBox_relative_cronology.setMaximum(max_num_order_layer[0])

    def define_order_layer_value(self,v):
        try:
            self.ORDER_LAYER_VALUE = v
            # self.ORDER_SITO = sito
            # self.ORDER_AREA= area
            layer = self.iface.mapCanvas().currentLayer().dataProvider()
            originalSubsetString = layer.subsetString()
            newSubSetString = "order_layer <= %s" % (self.ORDER_LAYER_VALUE)  # 4D dimension
            layer.setSubsetString(newSubSetString)
            layer = self.iface.mapCanvas().currentLayer()
            layer.triggerRepaint()

        except Exception as e:
            QgsMessageLog.logMessage(
                "You must to load pyarchinit_us_view and/or select it from pyarchinit GeoDatabase" + str(e))
            self.iface.messageBar().pushMessage("Help",
                                                "You must to load pyarchinit_us_view and/or select it from pyarchinit GeoDatabase",
                                                level=Qgis.Warning)

    def reset_query(self):
        self.ORDER_LAYER_VALUE = v
        

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


## Class end

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = pyarchinit_US()
    ui.show()
    sys.exit(app.exec_())
