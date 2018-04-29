#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
/***************************************************************************
        pyArchInit Plugin  - A QGIS plugin to manage archaeological dataset
        					 stored in Postgres
                             -------------------
    begin                : 2007-12-01
    copyright            : (C) 2008 by Luca Mandolesi
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
import os

from pyarchinit_error_check import *
from pyarchinit_utility import *

from ..modules.db.pyarchinit_conn_strings import Connection
from ..modules.db.pyarchinit_db_manager import Pyarchinit_db_management
from ..modules.gis.pyarchinit_pyqgis import Pyarchinit_pyqgis

MAIN_DIALOG_CLASS, _ = loadUiType(os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'Documentazione_preview.ui'))


class pyarchinit_doc_preview(QDialog, MAIN_DIALOG_CLASS):
    MSG_BOX_TITLE = "pyArchInit - Scheda Sistema Preview Documentazione"
    DB_MANAGER = ""
    DATA_LIST = ""
    ID_US_DICT = {}
    mapPreview = ""
    DOC_STR = ""
    vlayer = ""
    layerToSet = ""

    HOME = os.environ['PYARCHINIT_HOME']

    QUANT_PATH = '{}{}{}'.format(HOME, os.sep, "pyarchinit_Quantificazioni_folder")

    def __init__(self, iface, docstr):
        super().__init__()
        self.iface = iface
        self.pyQGIS = Pyarchinit_pyqgis(iface)
        self.setupUi(self)
        self.DOC_STR = docstr

        self.mapPreview = QgsMapCanvas(self)
        self.mapPreview.setCanvasColor(QColor(255, 255, 255))
        self.gridLayout_2.addWidget(self.mapPreview, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.widgetPreviewDoc, 0, 0, 1, 1)
        self.draw_preview()

        try:
            self.DB_connect()
        except:
            pass

    def DB_connect(self):
        conn = Connection()
        conn_str = conn.conn_str()

        try:
            self.DB_MANAGER = Pyarchinit_db_management(conn_str)
            self.DB_MANAGER.connection()
        except Exception as e:
            e = str(e)
            QMessageBox.warning(self, "Alert",
                                "Attenzione rilevato bug! Segnalarlo allo sviluppatore <br> Errore: <br>" + str(e),
                                QMessageBox.Ok)

    def draw_preview(self):
        self.layerToSet = self.pyQGIS.loadMapPreviewDoc(self.DOC_STR)
        self.vlayer = self.layerToSet[0].layer()

        self.mapPreview.setLayers(self.vlayer)
        self.mapPreview.zoomToFullExtent()

        QMessageBox.warning(self, "layer to set", str(self.layerToSet), QMessageBox.Ok)

    def testing(self, name_file, message):
        f = open(str(name_file), 'w')
        f.write(str(message))
        f.close()
