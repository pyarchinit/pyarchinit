#!/usr/bin/env python3
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

import math
from datetime import date
import platform
import cv2
import time
import numpy as np
import urllib.parse
import pyvista as pv
import vtk

from pyvistaqt import QtInteractor
import functools
from builtins import range

from qgis.PyQt.QtCore import Qt, QSize, QVariant, QDateTime
from qgis.PyQt.QtGui import QIcon, QColor
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.uic import loadUiType
from qgis.core import QgsSettings, Qgis
from qgis.gui import QgsMapCanvas
from collections import OrderedDict
import subprocess

from ..modules.utility.skatch_gpt_INVMAT import GPTWindow
from ..modules.utility.VideoPlayerArtefact import VideoPlayerWindow
from ..modules.utility.pyarchinit_media_utility import *
from ..modules.db.pyarchinit_conn_strings import Connection
from ..modules.db.pyarchinit_db_manager import Pyarchinit_db_management
from ..modules.db.pyarchinit_utility import Utility
from ..modules.utility.csv_writer import UnicodeWriter

from ..modules.utility.delegateComboBox import ComboBoxDelegate
from ..modules.utility.pyarchinit_error_check import Error_check
from ..modules.utility.pyarchinit_exp_Findssheet_pdf import generate_reperti_pdf
from ..modules.gis.pyarchinit_pyqgis import Pyarchinit_pyqgis
from ..modules.utility.archaeological_data_mapping import ArchaeologicalDataMapper
from ..gui.imageViewer import ImageViewer
from ..gui.quantpanelmain import QuantPanelMain
from ..gui.sortpanelmain import SortPanelMain
from ..gui.pyarchinitConfigDialog import pyArchInitDialog_Config

MAIN_DIALOG_CLASS, _ = loadUiType(os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'Tma.ui'))

class pyarchinit_Tma(QDialog, MAIN_DIALOG_CLASS):
    """This class provides the implementation of the Tma tab."""
    
    MSG_BOX_TITLE = "PyArchInit - Tma"
    DATA_LIST = []
    DATA_LIST_REC_CORR = []
    DATA_LIST_REC_TEMP = []
    REC_CORR = 0
    REC_TOT = 0
    STATUS_ITEMS = {"b": "Usa", "f": "Trova", "n": "Nuovo Record"}
    BROWSE_STATUS = "b"
    SORT_MODE = 'asc'
    SORTED_ITEMS = {"n": "Non ordinati", "o": "Ordinati"}
    SORT_STATUS = "n"
    UTILITY = Utility()
    DB_MANAGER = ""
    TABLE_NAME = 'inventario_materiali_table'
    MAPPER_TABLE_CLASS = "INVENTARIO_MATERIALI"
    NOME_SCHEDA = "Scheda Inventario Materiali"
    ID_TABLE = "id_invmat"
    CONVERSION_DICT = {
        ID_TABLE: ID_TABLE,
        "Sito": "sito",
        "Numero inventario": "numero_inventario",
        "Tipo reperto": "tipo_reperto",
        "Classe materiale": "classe_materiale",
        "Definizione": "definizione",
        "Descrizione": "descrizione",
        "Area": "area",
        "US": "us",
        "Lavato": "lavato",
        "Numero cassa": "nr_cassa",
        "Luogo di conservazione": "luogo_conservazione",
        "Stato conservazione": "stato_conservazione",
        "Datazione reperto": "datazione_reperto",
        "Elementi reperto": "elementi_reperto",
        "Misurazioni": "misurazioni",
        "Rif Biblio": "rif_biblio",
        "Tecnologie": "tecnologie"
    }
    
    SORT_ITEMS = [
        ID_TABLE,
        "Sito",
        "Numero inventario",
        "Tipo reperto",
        "Classe materiale",
        "Definizione",
        "Descrizione",
        "Area",
        "US",
        "Lavato",
        "Numero cassa",
        "Luogo di conservazione",
        "Stato conservazione",
        "Datazione reperto",
        "Elementi reperto",
        "Misurazioni",
        "Rif Biblio",
        "Tecnologie"
    ]
    
    TABLE_FIELDS = [
        "sito",
        "numero_inventario",
        "tipo_reperto",
        "classe_materiale",
        "definizione",
        "descrizione",
        "area",
        "us",
        "lavato",
        "nr_cassa",
        "luogo_conservazione",
        "stato_conservazione",
        "datazione_reperto",
        "elementi_reperto",
        "misurazioni",
        "rif_biblio",
        "tecnologie"
    ]
    
    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.setupUi(self)
        self.pyQGIS = Pyarchinit_pyqgis(iface)
        #self.mDockWidget_2.setHidden(True)
        self.mDockWidget_export.setHidden(True)
        #self.mDockWidget_3.setHidden(True)
        self.iconListWidget.setHidden(True)
        self.mDockWidget.setHidden(True)
        self.init_gui()
        
    def init_gui(self):
        """Initialize the GUI elements."""
        self.setWindowTitle(self.NOME_SCHEDA)
        
        # Initialize database connection
        conn = Connection()
        conn_str = conn.conn_str()
        try:
            self.DB_MANAGER = Pyarchinit_db_management(conn_str)
            self.DB_MANAGER.connection()
        except Exception as e:
            QMessageBox.warning(self, "Alert", "Database connection error: " + str(e), QMessageBox.Ok)
        
        # Set up the GUI
        self.customize_gui()
        self.charge_list()
        self.empty_fields()
        self.fill_fields()
        self.set_sito()
        
    def customize_gui(self):
        """Customize the GUI elements."""
        # Set up the comboboxes, tables, and other GUI elements
        # This is a simplified version, you would need to add more code here
        # based on the specific requirements of the Tma tab
        pass
        
    def charge_list(self):
        """Load the data from the database."""
        self.DATA_LIST = []
        try:
            if self.DB_MANAGER.db_type == 'sqlite':
                id_list = self.DB_MANAGER.query_in_list('SELECT id_invmat FROM inventario_materiali_table')
                for i in id_list:
                    self.DATA_LIST.append(self.DB_MANAGER.query_bool("SELECT * FROM inventario_materiali_table WHERE id_invmat = ?", (i[0],)))
            else:
                id_list = self.DB_MANAGER.query_in_list('SELECT id_invmat FROM inventario_materiali_table')
                for i in id_list:
                    self.DATA_LIST.append(self.DB_MANAGER.query_bool("SELECT * FROM inventario_materiali_table WHERE id_invmat = %s", (i[0],)))
            
            self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
            self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
            self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR+1)
        except Exception as e:
            QMessageBox.warning(self, "Alert", str(e), QMessageBox.Ok)
            
    def fill_fields(self, n=0):
        """Fill the form fields with data."""
        self.rec_num = n
        try:
            # Fill the form fields with data from the database
            # This is a simplified version, you would need to add more code here
            # based on the specific fields in the Tma tab
            pass
        except Exception as e:
            QMessageBox.warning(self, "Alert", str(e), QMessageBox.Ok)
            
    def set_rec_counter(self, t, c):
        """Set the record counter."""
        self.rec_tot.setText(str(t))
        self.rec_corrente.setText(str(c))
        
    def set_LIST_REC_TEMP(self):
        """Set the temporary record list."""
        # This is a simplified version, you would need to add more code here
        # based on the specific fields in the Tma tab
        pass
        
    def empty_fields(self):
        """Clear all form fields."""
        # This is a simplified version, you would need to add more code here
        # based on the specific fields in the Tma tab
        pass
        
    def set_sito(self):
        """Set the site combobox."""
        try:
            sito_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('site_table', 'sito', 'SITE'))
            sito_vl.sort()
            self.comboBox_sito.clear()
            self.comboBox_sito.addItems(sito_vl)
        except Exception as e:
            QMessageBox.warning(self, "Alert", str(e), QMessageBox.Ok)