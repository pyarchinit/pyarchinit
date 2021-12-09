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
import os

from qgis.PyQt.QtWidgets import QDialog, QMessageBox
from qgis.PyQt.uic import loadUiType

from ..modules.db.pyarchinit_conn_strings import Connection
from ..modules.db.pyarchinit_db_manager import Pyarchinit_db_management
from ..modules.db.pyarchinit_utility import Utility
from ..modules.gis.pyarchinit_pyqgis import Pyarchinit_pyqgis

MAIN_DIALOG_CLASS, _ = loadUiType(os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'Upd.ui'))


class pyarchinit_Upd_Values(QDialog, MAIN_DIALOG_CLASS):
    MSG_BOX_TITLE = "PyArchInit - Aggiornamento Valori"
    DATA_LIST = []
    DATA_LIST_REC_CORR = []
    DATA_LIST_REC_TEMP = []
    REC_CORR = 0
    REC_TOT = 0
    STATUS = {"usa": "Usa", "trova": "Trova", "nuovo_record": "Nuovo Record"}
    SORT_MODE = 'asc'
    SORTED = {"n": "Non ordinati", "o": "Ordinati"}
    UTILITY = Utility()
    DB_MANAGER = ""
    TABLE_NAME = 'us_table'
    MAPPER_TABLE_CLASS = "US"
    NOME_SCHEDA = "Scheda US"
    ID_TABLE = "id_us"
    CONVERSION_DICT = {}
    SORT_ITEMS = []

    TABLE_FIELDS = []

    def __init__(self, iface):
        self.iface = iface
        self.pyQGIS = Pyarchinit_pyqgis(self.iface)

        QDialog.__init__(self)
        self.setupUi(self)
        self.currentLayerId = None
        self.load_connection()

    def load_connection(self):
        QMessageBox.warning(self, "Alert", "Sistema in corso di abbandono. A breve verra' eliminato.", QMessageBox.Ok)

        conn = Connection()
        conn_str = conn.conn_str()
        try:
            self.DB_MANAGER = Pyarchinit_db_management(conn_str)
            self.DB_MANAGER.connection()
        except:
            pass

    def on_pushButton_pressed(self):

        field_position = self.pyQGIS.findFieldFrDict('gid')

        field_list = self.pyQGIS.selectedFeatures()

        id_list_sf = self.pyQGIS.findItemInAttributeMap(field_position, field_list)

        id_list = []
        for idl in id_list_sf:
            sid = idl.toInt()
            id_list.append(sid[0])

        table_name = str(self.nome_tabellaLineEdit.text())

        id_field = str(self.campoIDLineEdit.text())

        field_2_upd = str(self.nome_campoLineEdit.text())

        value_2_upd = str(self.sostituisci_conLineEdit.text())

        for i in id_list:
            self.update_record(table_name, id_field, [i], [field_2_upd], [value_2_upd])

    def update_record(self, table_value, id_field_value, id_value_list, table_fields_list, data_list):
        self.DB_MANAGER.update(table_value,
                               id_field_value,
                               id_value_list,
                               table_fields_list,
                               data_list)
