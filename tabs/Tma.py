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

import os
import platform
import subprocess
import shutil
import datetime
from builtins import range
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtCore import Qt, QTimer
from qgis.PyQt.QtGui import QBrush, QColor
from qgis.PyQt.uic import loadUiType
from qgis.core import QgsSettings, Qgis, QgsMessageLog

from ..gui.pyarchinitConfigDialog import pyArchInitDialog_Config
from ..gui.sortpanelmain import SortPanelMain
from ..modules.db.pyarchinit_conn_strings import Connection
from ..modules.db.pyarchinit_db_manager import Pyarchinit_db_management
from ..modules.db.pyarchinit_utility import Utility
from ..modules.gis.pyarchinit_pyqgis import Pyarchinit_pyqgis
from ..modules.utility.pyarchinit_error_check import Error_check
from ..modules.utility.pyarchinit_media_utility import *
from ..modules.db.entities.TMA import TMA
from ..modules.db.entities.TMA_MATERIALI import TMA_MATERIALI
from ..modules.utility.pyarchinit_exp_Tmasheet_pdf import single_TMA_pdf

# Additional imports for media support
from qgis.PyQt.QtGui import QIcon, QPixmap
from qgis.PyQt.QtWidgets import QListWidget, QListWidgetItem, QAbstractItemView
from qgis.PyQt.QtCore import QSize, QVariant
from qgis.gui import QgsMapCanvas
from ..gui.imageViewer import ImageViewer
from ..modules.utility.delegateComboBox import ComboBoxDelegate
import urllib.parse

MAIN_DIALOG_CLASS, _ = loadUiType(os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'Tma.ui'))


class pyarchinit_Tma(QDialog, MAIN_DIALOG_CLASS):
    """This class provides the implementation of the TMA (Tabella Materiali Archeologici) tab."""

    L = QgsSettings().value("locale/userLocale")[0:2]
    if L == 'it':
        MSG_BOX_TITLE = "PyArchInit - Scheda TMA"
    else:
        MSG_BOX_TITLE = "PyArchInit - TMA form"

    DATA_LIST = []
    DATA_LIST_REC_CORR = []
    DATA_LIST_REC_TEMP = []
    REC_CORR = 0
    REC_TOT = 0
    SITO = pyArchInitDialog_Config
    if L == 'it':
        STATUS_ITEMS = {"b": "Usa", "f": "Trova", "n": "Nuovo Record"}
    else:
        STATUS_ITEMS = {"b": "Current", "f": "Find", "n": "New Record"}
    BROWSE_STATUS = "b"
    SORT_MODE = 'asc'
    if L == 'it':
        SORTED_ITEMS = {"n": "Non ordinati", "o": "Ordinati"}
    else:
        SORTED_ITEMS = {"n": "Not sorted", "o": "Sorted"}
    SORT_STATUS = "n"
    SORT_ITEMS_CONVERTED = ''
    UTILITY = Utility()
    DB_MANAGER = ""
    TABLE_NAME = 'tma_materiali_archeologici'
    MAPPER_TABLE_CLASS = "TMA"
    NOME_SCHEDA = "Scheda TMA - Tabella Materiali Archeologici"
    ID_TABLE = "id"

    CONVERSION_DICT = {
        ID_TABLE: ID_TABLE,

        "Sito": "sito",
        "Area": "area",
        "US": "dscu",
        "Materiale": "ogtm",
        "Tipologia collocazione": "ldct",
        "Denominazione collocazione": "ldcn",
        "Vecchia collocazione": "vecchia_collocazione",
        "Cassetta": "cassetta",
        "Denominazione scavo": "scan",
        "Saggio": "saggio",
        "Vano/Locus": "vano_locus",
        "Data scavo": "dscd",
        "Data ricognizione": "rcgd",
        "Specifiche ricognizione": "rcgz",
        "Tipo acquisizione": "aint",
        "Data acquisizione": "aind",
        "Fascia cronologica": "dtzg",
        "Frazione cronologica": "dtzs",
        "Cronologie": "cronologie",
        "N. reperti": "n_reperti",
        "Peso": "peso",
        "Indicazione oggetti": "deso",
        "Inventario": "madi",
        "Categoria": "macc",
        "Classe": "macl",
        "Precisazione tipologica": "macp",
        "Definizione": "macd",
        "Cronologia": "cronologia_mac",
        "Quantità": "macq",
        "Tipo fotografia": "ftap",
        "Codice foto": "ftan",
        "Tipo disegno": "drat",
        "Codice disegno": "dran",
        "Autore disegno": "draa"
    }

    SORT_ITEMS = [
        ID_TABLE,
        "Sito",
        "Area",
        "US",
        "Materiale",
        "Cassetta",
        "Fascia cronologica",
        "Categoria"
    ]

    TABLE_FIELDS = [
        'sito',
        'area',
        'ogtm',
        'ldct',
        'ldcn',
        'vecchia_collocazione',
        'cassetta',
        'scan',
        'saggio',
        'vano_locus',
        'dscd',
        'dscu',
        'rcgd',
        'rcgz',
        'aint',
        'aind',
        'dtzg',
        'deso',
        'nsc',
        'ftap',
        'ftan',
        'drat',
        'dran',
        'draa',
        'created_at',
        'updated_at',
        'created_by',
        'updated_by'
    ]

    LANG = {
        "IT": ['it_IT', 'IT', 'it', 'IT_IT'],
        "EN": ['en_US', 'EN', "en", "EN_US"],
        "DE": ['de_DE', 'de', 'DE', 'DE_DE']
    }

    HOME = os.environ['PYARCHINIT_HOME']
    REPORT_PATH = '{}{}{}'.format(HOME, os.sep, "pyarchinit_Report_folder")
    PDFFOLDER = '{}{}{}'.format(HOME, os.sep, "pyarchinit_PDF_folder")
    DB_SERVER = "not defined"

    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.pyQGIS = Pyarchinit_pyqgis(iface)
        self.setupUi(self)
        self.currentLayerId = None
        
        # Initialize media widget
        self.iconListWidget = QListWidget(self)
        self.iconListWidget.setViewMode(QListWidget.IconMode)
        self.iconListWidget.setIconSize(QSize(150, 150))
        self.iconListWidget.setMovement(QListWidget.Static)
        self.iconListWidget.setSpacing(12)
        self.iconListWidget.setResizeMode(QListWidget.Adjust)
        self.iconListWidget.setLayoutMode(QListWidget.Batched)
        self.iconListWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.iconListWidget.setLineWidth(2)
        self.iconListWidget.setMidLineWidth(2)
        self.iconListWidget.itemDoubleClicked.connect(self.openWide_image)
        
        # Enable drag and drop
        self.setAcceptDrops(True)
        self.iconListWidget.setAcceptDrops(True)
        
        # Add map preview
        self.mapPreview = QgsMapCanvas(self)
        self.mapPreview.setCanvasColor(QColor(225, 225, 225))
        
        # Add tabs for media and map
        self.addMediaTab()
        
        # Initialize navigation timer to prevent multiple clicks
        self._nav_timer = QTimer()
        self._nav_timer.setSingleShot(True)
        self._nav_timer.timeout.connect(self._process_navigation)
        self._nav_direction = None
        self._nav_in_progress = False

        try:
            self.on_pushButton_connect_pressed()
        except Exception as e:
            QMessageBox.warning(self, "Connection system", str(e), QMessageBox.Ok)

        # Initialize GUI after connecting to database
        self.customize_GUI()
        
        self.msg_sito()
        self.set_sito()

    def customize_GUI(self):
        """Customize the GUI elements - connect signals to slots."""
        # Get language settings like Inv_Materiali does
        l = QgsSettings().value("locale/userLocale", QVariant)
        lang = ""
        for key, values in self.LANG.items():
            if values.__contains__(l):
                lang = str(key)
        lang = "'" + lang + "'"
        
        # Connect table buttons (ora definiti nel file UI)
        self.pushButton_add_foto.clicked.connect(self.on_pushButton_add_foto_pressed)
        self.pushButton_remove_foto.clicked.connect(self.on_pushButton_remove_foto_pressed)
        self.pushButton_add_disegno.clicked.connect(self.on_pushButton_add_disegno_pressed)
        self.pushButton_remove_disegno.clicked.connect(self.on_pushButton_remove_disegno_pressed)
        
        # Connect materials table buttons
        self.pushButton_add_materiale.clicked.connect(self.on_pushButton_add_materiale_pressed)
        self.pushButton_remove_materiale.clicked.connect(self.on_pushButton_remove_materiale_pressed)
        
        # Initialize materials table with thesaurus support
        self.setup_materials_table_with_thesaurus()
        self.current_material_index = -1
        self.materials_data = []
        
        # Setup thesaurus for main TMA fields following Inv_Materiali pattern
        # Only proceed if DB_MANAGER is properly initialized
        if self.DB_MANAGER and self.DB_MANAGER != "":
            # Location type (ldct) - ComboBox
            if hasattr(self, 'comboBox_ldct'):
                search_dict = {
                    'lingua': lang,
                    'nome_tabella': "'" + 'tma_table' + "'",  # Using alias table name
                    'tipologia_sigla': "'" + '10.10' + "'"
                }
                ldct_vl = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
                values_ldct = []
                for i in range(len(ldct_vl)):
                    values_ldct.append(ldct_vl[i].sigla_estesa)
                values_ldct.sort()
                self.comboBox_ldct.clear()
                self.comboBox_ldct.addItems(values_ldct)
        
            # Acquisition type (aint) - Already a ComboBox in UI
            if hasattr(self, 'comboBox_aint'):
                search_dict = {
                    'lingua': lang,
                    'nome_tabella': "'" + 'tma_table' + "'",
                    'tipologia_sigla': "'" + '10.11' + "'"
                }
                aint_vl = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
                values_aint = []
                for i in range(len(aint_vl)):
                    values_aint.append(aint_vl[i].sigla_estesa)
                values_aint.sort()
                self.comboBox_aint.clear()
                self.comboBox_aint.addItems(values_aint)
            
            # Photo type (ftap) - ComboBox if exists
            if hasattr(self, 'comboBox_ftap'):
                search_dict = {
                    'lingua': lang,
                    'nome_tabella': "'" + 'tma_table' + "'",
                    'tipologia_sigla': "'" + '10.12' + "'"
                }
                ftap_vl = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
                values_ftap = []
                for i in range(len(ftap_vl)):
                    values_ftap.append(ftap_vl[i].sigla_estesa)
                values_ftap.sort()
                self.comboBox_ftap.clear()
                self.comboBox_ftap.addItems(values_ftap)
            
            # Drawing type (drat) - ComboBox if exists
            if hasattr(self, 'comboBox_drat'):
                search_dict = {
                    'lingua': lang,
                    'nome_tabella': "'" + 'tma_table' + "'",
                    'tipologia_sigla': "'" + '10.13' + "'"
                }
                drat_vl = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
                values_drat = []
                for i in range(len(drat_vl)):
                    values_drat.append(drat_vl[i].sigla_estesa)
                values_drat.sort()
                self.comboBox_drat.clear()
                self.comboBox_drat.addItems(values_drat)
        # else: DB_MANAGER not ready yet
        
        # Connect fields to auto-update chronology and inventory
        # Moved to fill_fields to avoid multiple connections
        # self.lineEdit_us.textChanged.connect(self.on_us_changed)
        self.comboBox_area.currentIndexChanged.connect(self.on_area_changed)
        self.comboBox_sito.currentIndexChanged.connect(self.on_sito_changed)
        
        # Ensure add material button is properly connected (prevent double connections)
        try:
            self.pushButton_add_materiale.clicked.disconnect()
        except:
            pass
        self.pushButton_add_materiale.clicked.connect(self.on_pushButton_add_materiale_pressed)
        
        # Setup inventory field as read-only
        self.lineEdit_inventario.setReadOnly(True)

        # Connect other signals
        self.pushButton_first_rec.clicked.connect(self.on_pushButton_first_rec_pressed)
        self.pushButton_prev_rec.clicked.connect(self.on_pushButton_prev_rec_pressed)
        self.pushButton_next_rec.clicked.connect(self.on_pushButton_next_rec_pressed)
        self.pushButton_last_rec.clicked.connect(self.on_pushButton_last_rec_pressed)
        self.pushButton_new_rec.clicked.connect(self.on_pushButton_new_rec_pressed)
        self.pushButton_save.clicked.connect(self.on_pushButton_save_pressed)
        self.pushButton_delete.clicked.connect(self.on_pushButton_delete_pressed)
        self.pushButton_new_search.clicked.connect(self.on_pushButton_new_search_pressed)
        self.pushButton_search_go.clicked.connect(self.on_pushButton_search_go_pressed)
        self.pushButton_sort.clicked.connect(self.on_pushButton_sort_pressed)
        self.pushButton_view_all_2.clicked.connect(self.on_pushButton_view_all_pressed)
        self.pushButton_open_dir.clicked.connect(self.on_pushButton_open_dir_pressed)
        self.toolButtonGis.clicked.connect(self.on_toolButtonGis_toggled)
        self.pushButton_import.clicked.connect(self.on_pushButton_import_pressed)
        self.pushButton_export_ica.clicked.connect(self.on_pushButton_export_pdf_pressed)
        self.pushButton_export_pdf.clicked.connect(self.on_pushButton_export_tma_pdf_pressed)

    def enable_button(self, n):
        self.pushButton_new_rec.setEnabled(n)
        self.pushButton_view_all_2.setEnabled(n)
        self.pushButton_first_rec.setEnabled(n)
        self.pushButton_last_rec.setEnabled(n)
        self.pushButton_prev_rec.setEnabled(n)
        self.pushButton_next_rec.setEnabled(n)
        self.pushButton_delete.setEnabled(n)
        self.pushButton_new_search.setEnabled(n)
        self.pushButton_search_go.setEnabled(n)
        self.pushButton_sort.setEnabled(n)

    def enable_button_search(self, n):
        self.pushButton_new_rec.setEnabled(n)
        self.pushButton_view_all_2.setEnabled(n)
        self.pushButton_first_rec.setEnabled(n)
        self.pushButton_last_rec.setEnabled(n)
        self.pushButton_prev_rec.setEnabled(n)
        self.pushButton_next_rec.setEnabled(n)
        self.pushButton_delete.setEnabled(n)
        self.pushButton_save.setEnabled(n)
        self.pushButton_sort.setEnabled(n)

    def on_pushButton_connect_pressed(self):
        conn = Connection()
        conn_str = conn.conn_str()
        test_conn = conn_str.find('sqlite')

        if test_conn == 0:
            self.DB_SERVER = "sqlite"

        try:
            self.DB_MANAGER = Pyarchinit_db_management(conn_str)
            self.DB_MANAGER.connection()
            self.charge_records()  # charge records from DB
            # check if DB is empty
            if bool(self.DATA_LIST):
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                self.BROWSE_STATUS = 'b'
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.label_sort.setText(self.SORTED_ITEMS["n"])
                self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                self.charge_list()
                self.fill_fields()
            else:
                if self.L == 'it':
                    QMessageBox.warning(self, "BENVENUTO",
                                        "Benvenuto in pyArchInit " + self.NOME_SCHEDA + ". Il database e' vuoto. Premi 'Ok' e buon lavoro!",
                                        QMessageBox.Ok)
                else:
                    QMessageBox.warning(self, "WELCOME",
                                        "Welcome in pyArchInit" + "TMA form" + ". The DB is empty. Push 'Ok' and Good Work!",
                                        QMessageBox.Ok)
                self.charge_list()
                self.BROWSE_STATUS = 'x'
                self.on_pushButton_new_rec_pressed()

        except Exception as e:
            e = str(e)
            if e.find("no such table"):
                if self.L == 'it':
                    msg = "La connessione e' fallita {}. " \
                          "E' NECESSARIO RIAVVIARE QGIS oppure rilevato bug! Segnalarlo allo sviluppatore".format(
                        str(e))
                    self.iface.messageBar().pushMessage(self.tr(msg), Qgis.Warning, 0)
                else:
                    msg = "The connection failed {}. " \
                          "You MUST RESTART QGIS or bug detected! Report it to the developer".format(str(e))
            else:
                if self.L == 'it':
                    msg = "Attenzione rilevato bug! Segnalarlo allo sviluppatore. Errore: ".format(str(e))
                    self.iface.messageBar().pushMessage(self.tr(msg), Qgis.Warning, 0)
                else:
                    msg = "Warning bug detected! Report it to the developer. Error: ".format(str(e))
                    self.iface.messageBar().pushMessage(self.tr(msg), Qgis.Warning, 0)

    def charge_list(self):
        """Load combobox lists."""
        # Get language setting
        l = QgsSettings().value("locale/userLocale", "en")
        lang = ""
        for key, values in self.LANG.items():
            if values.__contains__(l):
                lang = str(key)
        lang = "'" + lang + "'"
        
        # lista sito
        sito_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('site_table', 'sito', 'SITE'))
        try:
            sito_vl.remove('')
        except Exception as e:
            if str(e) == "list.remove(x): x not in list":
                pass
            else:
                if self.L == 'it':
                    QMessageBox.warning(self, "Messaggio", "Sistema di aggiornamento lista Sito: " + str(e),
                                        QMessageBox.Ok)
                else:
                    QMessageBox.warning(self, "Message", "Site list update system: " + str(e), QMessageBox.Ok)

        self.comboBox_sito.clear()
        sito_vl.sort()
        self.comboBox_sito.addItems(sito_vl)

        # lista area from thesaurus
        self.comboBox_area.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'tma_materiali_archeologici' + "'",
            'tipologia_sigla': "'" + '10.7' + "'"
        }
        area_vl_thesaurus = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        area_vl = []
        for s in area_vl_thesaurus:
            area_vl.append(str(s.sigla_estesa))
        area_vl.sort()
        self.comboBox_area.addItems(area_vl)
        
        # Load thesaurus values for TMA fields
        # 10.1 - Denominazione collocazione
        search_dict_ldcn = {
            'nome_tabella': "'tma_materiali_archeologici'",
            'tipologia_sigla': "'10.1'"
        }
        ldcn_res = self.DB_MANAGER.query_bool(search_dict_ldcn, 'PYARCHINIT_THESAURUS_SIGLE')
        self.comboBox_ldcn.clear()
        ldcn_dict = {}
        for i in range(len(ldcn_res)):
            sigla_estesa = str(ldcn_res[i].sigla_estesa)
            sigla = str(ldcn_res[i].sigla)
            ldcn_dict[sigla_estesa] = sigla
        
        # Sort and add items with tooltips
        for sigla_estesa in sorted(ldcn_dict.keys()):
            self.comboBox_ldcn.addItem(sigla_estesa)
            index = self.comboBox_ldcn.count() - 1
            self.comboBox_ldcn.setItemData(index, f"Codice: {ldcn_dict[sigla_estesa]}", Qt.ToolTipRole)
        
        # 10.2 - Saggio
        search_dict_saggio = {
            'nome_tabella': "'tma_materiali_archeologici'",
            'tipologia_sigla': "'10.2'"
        }
        saggio_res = self.DB_MANAGER.query_bool(search_dict_saggio, 'PYARCHINIT_THESAURUS_SIGLE')
        self.comboBox_saggio.clear()
        saggio_dict = {}
        for i in range(len(saggio_res)):
            sigla_estesa = str(saggio_res[i].sigla_estesa)
            sigla = str(saggio_res[i].sigla)
            saggio_dict[sigla_estesa] = sigla
        
        # Sort and add items with tooltips
        for sigla_estesa in sorted(saggio_dict.keys()):
            self.comboBox_saggio.addItem(sigla_estesa)
            index = self.comboBox_saggio.count() - 1
            self.comboBox_saggio.setItemData(index, f"Codice: {saggio_dict[sigla_estesa]}", Qt.ToolTipRole)
        
        # 10.3 - Vano/Locus
        search_dict_vano = {
            'nome_tabella': "'tma_materiali_archeologici'",
            'tipologia_sigla': "'10.3'"
        }
        vano_res = self.DB_MANAGER.query_bool(search_dict_vano, 'PYARCHINIT_THESAURUS_SIGLE')
        self.comboBox_vano_locus.clear()
        vano_dict = {}
        for i in range(len(vano_res)):
            sigla_estesa = str(vano_res[i].sigla_estesa)
            sigla = str(vano_res[i].sigla)
            vano_dict[sigla_estesa] = sigla
        
        # Sort and add items with tooltips
        for sigla_estesa in sorted(vano_dict.keys()):
            self.comboBox_vano_locus.addItem(sigla_estesa)
            index = self.comboBox_vano_locus.count() - 1
            self.comboBox_vano_locus.setItemData(index, f"Codice: {vano_dict[sigla_estesa]}", Qt.ToolTipRole)
        
        # Note: Materials are handled through separate TMA_MATERIALI table in database

    def charge_records(self):
        self.DATA_LIST = []
        if self.DB_SERVER == 'sqlite':
            for i in self.DB_MANAGER.query(self.MAPPER_TABLE_CLASS):
                self.DATA_LIST.append(i)
        else:
            id_list = []
            for i in self.DB_MANAGER.query(self.MAPPER_TABLE_CLASS):
                id_list.append(eval("i." + self.ID_TABLE))
            temp_data_list = self.DB_MANAGER.query_sort(id_list, [self.ID_TABLE], 'asc', self.MAPPER_TABLE_CLASS,
                                                        self.ID_TABLE)
            for i in temp_data_list:
                self.DATA_LIST.append(i)

    def datestrfdate(self):
        """Convert date fields to string format."""
        # Handle date conversions if needed
        pass

    def table_set_todelete(self):
        """Mark tables for deletion mode."""
        # This would be used for batch operations
        pass

    def msg_sito(self):
        conn = Connection()
        sito_set = conn.sito_set()
        sito_set_str = sito_set['sito_set']
        if bool(self.comboBox_sito.currentText()) and self.comboBox_sito.currentText() == sito_set_str:
            if self.L == 'it':
                QMessageBox.information(self, "OK", "Sei connesso al sito: %s" % str(sito_set_str), QMessageBox.Ok)
            else:
                QMessageBox.information(self, "OK", "You are connected to the site: %s" % str(sito_set_str),
                                        QMessageBox.Ok)

        elif sito_set_str == '':
            if self.L == 'it':
                msg = QMessageBox.information(self, "Attenzione",
                                              "Non hai settato alcun sito. Vuoi settarne uno? click Ok altrimenti Annulla per  vedere tutti i record",
                                              QMessageBox.Ok | QMessageBox.Cancel)
            else:
                msg = QMessageBox.information(self, "Warning",
                                              "You have not set up any archaeological site. Do you want to set one? click Ok otherwise Cancel to see all records",
                                              QMessageBox.Ok | QMessageBox.Cancel)
            if msg == QMessageBox.Cancel:
                pass
            else:
                dlg = pyArchInitDialog_Config(self)
                dlg.charge_list()
                dlg.exec_()

    def set_sito(self):
        conn = Connection()
        sito_set = conn.sito_set()
        sito_set_str = sito_set['sito_set']
        try:
            if bool(sito_set_str):
                search_dict = {'sito': "'" + str(sito_set_str) + "'"}
                u = Utility()
                search_dict = u.remove_empty_items_fr_dict(search_dict)
                res = self.DB_MANAGER.query_bool(search_dict, 'TMA')
                self.DATA_LIST = []
                for i in res:
                    self.DATA_LIST.append(i)
                if self.DATA_LIST:
                    self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                    self.fill_fields()
                    self.BROWSE_STATUS = "b"
                    self.SORT_STATUS = "n"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                    self.charge_list()
                    self.label_sort.setText(self.SORTED_ITEMS["n"])
                else:
                    # No records for this site yet
                    self.BROWSE_STATUS = "x"
                    self.DATA_LIST = []
                    self.DATA_LIST_REC_CORR = []
                    self.DATA_LIST_REC_TEMP = []
                    self.REC_CORR = 0
                    self.REC_TOT = 0
                    self.empty_fields()
                    self.set_rec_counter(0, 0)
                    # Set the site field to the sito_set value
                    self.comboBox_sito.setEditText(sito_set_str)
                self.setComboBoxEnable(["self.comboBox_sito"], "False")
                self.setComboBoxEditable(["self.comboBox_sito"], 0)
            else:
                self.setComboBoxEnable(["self.comboBox_sito"], "True")
                self.setComboBoxEditable(["self.comboBox_sito"], 1)
        except Exception as e:
            if self.L == 'it':
                QMessageBox.information(self, "Attenzione", 
                                        f"Non esiste questo sito: '{sito_set_str}' in questa scheda. "
                                        "Per favore disattiva la 'scelta sito' dalla scheda di configurazione plugin per vedere tutti i record oppure crea la scheda",
                                        QMessageBox.Ok)
            else:
                QMessageBox.information(self, "Warning", 
                                        f"There is no such site: '{sito_set_str}' in this tab. "
                                        "Please disable the 'site choice' from the plugin configuration tab to see all records or create the tab",
                                        QMessageBox.Ok)

    def fill_fields(self, n=0):
        """Fill form fields with data from current record."""
        QgsMessageLog.logMessage(f"DEBUG fill_fields - chiamato con n={n}, REC_CORR={self.REC_CORR}", "PyArchInit", Qgis.Info)
        self.rec_num = n
        
        if not self.DATA_LIST:
            QgsMessageLog.logMessage(f"DEBUG fill_fields - DATA_LIST è vuota, esco", "PyArchInit", Qgis.Info)
            return
            
        try:
            # Temporarily disconnect the US change signal to prevent cascading updates
            try:
                self.lineEdit_us.textChanged.disconnect()
            except:
                pass  # Signal might not be connected

            # Basic fields from UI
            self.comboBox_sito.setEditText(str(self.DATA_LIST[self.rec_num].sito))
            self.comboBox_area.setEditText(str(self.DATA_LIST[self.rec_num].area))
            self.lineEdit_us.setText(str(self.DATA_LIST[self.rec_num].dscu))

            # Note: ogtm (materiale) field has been moved to materials table

            # Location data
            if self.DATA_LIST[self.rec_num].ldct:
                self.comboBox_ldct.setEditText(str(self.DATA_LIST[self.rec_num].ldct))
            if self.DATA_LIST[self.rec_num].ldcn:
                self.comboBox_ldcn.setEditText(str(self.DATA_LIST[self.rec_num].ldcn))
            if self.DATA_LIST[self.rec_num].vecchia_collocazione:
                self.lineEdit_vecchia_collocazione.setText(str(self.DATA_LIST[self.rec_num].vecchia_collocazione))
            if self.DATA_LIST[self.rec_num].cassetta:
                self.lineEdit_cassetta.setText(str(self.DATA_LIST[self.rec_num].cassetta))

            # Excavation data
            if self.DATA_LIST[self.rec_num].scan:
                self.lineEdit_scan.setText(str(self.DATA_LIST[self.rec_num].scan))
            if self.DATA_LIST[self.rec_num].saggio:
                self.comboBox_saggio.setEditText(str(self.DATA_LIST[self.rec_num].saggio))
            if self.DATA_LIST[self.rec_num].vano_locus:
                self.comboBox_vano_locus.setEditText(str(self.DATA_LIST[self.rec_num].vano_locus))
            if self.DATA_LIST[self.rec_num].dscd:
                self.lineEdit_dscd.setText(str(self.DATA_LIST[self.rec_num].dscd))

            # Survey data
            if self.DATA_LIST[self.rec_num].rcgd:
                self.lineEdit_rcgd.setText(str(self.DATA_LIST[self.rec_num].rcgd))
            if self.DATA_LIST[self.rec_num].rcgz:
                self.textEdit_rcgz.setText(str(self.DATA_LIST[self.rec_num].rcgz))
            if self.DATA_LIST[self.rec_num].aint:
                self.comboBox_aint.setCurrentText(str(self.DATA_LIST[self.rec_num].aint))
            if self.DATA_LIST[self.rec_num].aind:
                self.lineEdit_aind.setText(str(self.DATA_LIST[self.rec_num].aind))

            # Dating data - only fascia cronologica is left
            if self.DATA_LIST[self.rec_num].dtzg:
                self.lineEdit_dtzg.setText(str(self.DATA_LIST[self.rec_num].dtzg))

            # Technical data - only deso remains in main form
            if self.DATA_LIST[self.rec_num].deso:
                self.textEdit_deso.setText(str(self.DATA_LIST[self.rec_num].deso))

            # Load materials table from separate table
            self.load_materials_table()

            # Documentation tables - Fill from database
            self.fill_documentation_tables()

            # Update inventory field with RA numbers
            self.update_inventory_field()

            # Reconnect the US change signal after filling fields
            self.lineEdit_us.textChanged.connect(self.on_us_changed)

        except Exception as e:
            QMessageBox.warning(self, "Error", str(e), QMessageBox.Ok)
        finally:
            # Ensure signal is reconnected even if there's an error (removed duplicate connection)
            pass

    def fill_documentation_tables(self):
        """Fill documentation tables with data."""
        # Clear tables
        self.tableWidget_foto.setRowCount(0)
        self.tableWidget_disegni.setRowCount(0)

        # Fill photo table - Here we need to parse the data from fields
        if hasattr(self.DATA_LIST[self.rec_num], 'ftap') and self.DATA_LIST[self.rec_num].ftap:
            # If there are multiple photos separated by some delimiter
            tipi_foto = str(self.DATA_LIST[self.rec_num].ftap).split(';')
            codici_foto = str(self.DATA_LIST[self.rec_num].ftan).split(';') if self.DATA_LIST[self.rec_num].ftan else []

            for i, tipo in enumerate(tipi_foto):
                if tipo.strip():
                    row_position = self.tableWidget_foto.rowCount()
                    self.tableWidget_foto.insertRow(row_position)
                    self.tableWidget_foto.setItem(row_position, 0, QTableWidgetItem(tipo.strip()))
                    if i < len(codici_foto):
                        self.tableWidget_foto.setItem(row_position, 1, QTableWidgetItem(codici_foto[i].strip()))

        # Fill drawings table
        if hasattr(self.DATA_LIST[self.rec_num], 'drat') and self.DATA_LIST[self.rec_num].drat:
            # If there are multiple drawings separated by some delimiter
            tipi_disegno = str(self.DATA_LIST[self.rec_num].drat).split(';')
            codici_disegno = str(self.DATA_LIST[self.rec_num].dran).split(';') if self.DATA_LIST[
                self.rec_num].dran else []
            autori_disegno = str(self.DATA_LIST[self.rec_num].draa).split(';') if self.DATA_LIST[
                self.rec_num].draa else []

            for i, tipo in enumerate(tipi_disegno):
                if tipo.strip():
                    row_position = self.tableWidget_disegni.rowCount()
                    self.tableWidget_disegni.insertRow(row_position)
                    self.tableWidget_disegni.setItem(row_position, 0, QTableWidgetItem(tipo.strip()))
                    if i < len(codici_disegno):
                        self.tableWidget_disegni.setItem(row_position, 1, QTableWidgetItem(codici_disegno[i].strip()))
                    if i < len(autori_disegno):
                        self.tableWidget_disegni.setItem(row_position, 2, QTableWidgetItem(autori_disegno[i].strip()))
        
        # Load media for this TMA record
        self.load_tma_media()

    def load_tma_media(self):
        """Load media associated with current TMA record."""
        # Clear existing items
        self.iconListWidget.clear()
        
        if self.DATA_LIST and self.REC_CORR < len(self.DATA_LIST):
            current_tma = self.DATA_LIST[self.REC_CORR]
            
            # Search for media associated with this TMA
            search_dict = {
                'id_entity': int(current_tma.id),
                'entity_type': 'TMA'
            }
            
            media_to_entity_list = self.DB_MANAGER.query_bool(search_dict, 'MEDIATOENTITY')
            
            if media_to_entity_list:
                # Get connection for paths
                conn = Connection()
                thumb_path = conn.thumb_path()
                thumb_path_str = thumb_path['thumb_path']
                
                for media_to_entity in media_to_entity_list:
                    # Get media details
                    media_search = {'id_media': int(media_to_entity.id_media)}
                    media_data = self.DB_MANAGER.query_bool(media_search, 'MEDIA')
                    
                    if media_data:
                        media = media_data[0]
                        
                        # Get thumbnail data
                        thumb_search = {'id_media': str(media.id_media)}
                        thumb_data = self.DB_MANAGER.query_bool(thumb_search, 'MEDIA_THUMB')
                        
                        if thumb_data:
                            # Create list item
                            item = QListWidgetItem(str(media.filename))
                            item.setData(Qt.UserRole, str(media.id_media))
                            
                            # Set icon
                            icon_path = os.path.join(thumb_path_str, thumb_data[0].filepath)
                            if os.path.exists(icon_path):
                                icon = QIcon(icon_path)
                                item.setIcon(icon)
                            
                            self.iconListWidget.addItem(item)

    def set_rec_counter(self, t, c):
        QgsMessageLog.logMessage(f"DEBUG set_rec_counter - prima: rec_tot={self.rec_tot if hasattr(self, 'rec_tot') else 'None'}, rec_corr={self.rec_corr if hasattr(self, 'rec_corr') else 'None'}", "PyArchInit", Qgis.Info)
        QgsMessageLog.logMessage(f"DEBUG set_rec_counter - impostando: t={t}, c={c}", "PyArchInit", Qgis.Info)
        self.rec_tot = t
        self.rec_corr = c
        self.label_rec_tot.setText(str(self.rec_tot))
        self.label_rec_corrente.setText(str(self.rec_corr))
        QgsMessageLog.logMessage(f"DEBUG set_rec_counter - dopo: rec_tot={self.rec_tot}, rec_corr={self.rec_corr}", "PyArchInit", Qgis.Info)


    def records_equal_check(self):
        try:
            #self.set_sito()
            self.set_LIST_REC_TEMP()
            self.set_LIST_REC_CORR()

            if self.DATA_LIST_REC_CORR == self.DATA_LIST_REC_TEMP:
                return 0
            else:
                return 1
        except IndexError as e:
            print(f"IndexError: {e}")
            return 0
        except Exception as e:
            print(f"Unexpected error: {e}")
        return 0

    def set_LIST_REC_CORR(self):
        print(f"self.REC_CORR: {self.REC_CORR}, len(self.DATA_LIST): {len(self.DATA_LIST)}")

        if self.REC_CORR < 0 or self.REC_CORR >= len(self.DATA_LIST):
            raise IndexError("self.REC_CORR is out of range")

        self.DATA_LIST_REC_CORR = []
        for i in self.TABLE_FIELDS:
            try:
                self.DATA_LIST_REC_CORR.append(eval("unicode(self.DATA_LIST[self.REC_CORR]." + i + ")"))
            except IndexError as e:
                print(f"IndexError: {e} - self.REC_CORR: {self.REC_CORR}, len(self.DATA_LIST): {len(self.DATA_LIST)}")
                raise
            except Exception as e:
                print(f"Unexpected error: {e}")
                raise

    def set_LIST_REC_TEMP(self):
        """Build the temporary record list from form data."""
        # Get values from form fields
        if self.lineEdit_us.text():
            dscu = self.lineEdit_us.text()
        else:
            dscu = ""

        # Note: materiale field has been moved to materials table
        ogtm = ""

        # Location
        if self.comboBox_ldct.currentText():
            ldct = self.comboBox_ldct.currentText()
        else:
            ldct = ""

        if self.comboBox_ldcn.currentText():
            ldcn = self.comboBox_ldcn.currentText()
        else:
            ldcn = ""

        if self.lineEdit_vecchia_collocazione.text():
            vecchia_collocazione = self.lineEdit_vecchia_collocazione.text()
        else:
            vecchia_collocazione = ""

        if self.lineEdit_cassetta.text():
            cassetta = self.lineEdit_cassetta.text()
        else:
            cassetta = ""

        # Excavation data

        if self.lineEdit_scan.text():
            scan = self.lineEdit_scan.text()
        else:
            scan = ""

        if self.comboBox_saggio.currentText():
            saggio = self.comboBox_saggio.currentText()
        else:
            saggio = ""

        if self.comboBox_vano_locus.currentText():
            vano_locus = self.comboBox_vano_locus.currentText()
        else:
            vano_locus = ""

        if self.lineEdit_dscd.text():
            dscd = self.lineEdit_dscd.text()
        else:
            dscd = ""

        # Survey data
        if self.lineEdit_rcgd.text():
            rcgd = self.lineEdit_rcgd.text()
        else:
            rcgd = ""

        if self.textEdit_rcgz.toPlainText():
            rcgz = self.textEdit_rcgz.toPlainText()
        else:
            rcgz = ""

        if self.comboBox_aint.currentText():
            aint = self.comboBox_aint.currentText()
        else:
            aint = ""

        if self.lineEdit_aind.text():
            aind = self.lineEdit_aind.text()
        else:
            aind = ""

        # Dating
        if self.lineEdit_dtzg.text():
            dtzg = self.lineEdit_dtzg.text()
        else:
            dtzg = ""

        # Technical data
        if self.textEdit_deso.toPlainText():
            deso = self.textEdit_deso.toPlainText()
        else:
            deso = ""
        
        # Note storico-critiche field doesn't exist in the UI
        nsc = ""

        # Get documentation data from tables
        ftap, ftan = self.get_foto_data()
        drat, dran, draa = self.get_disegni_data()

        # Build the temp list (28 fields with system fields)
        self.DATA_LIST_REC_TEMP = [
            str(self.comboBox_sito.currentText()),  # sito
            str(self.comboBox_area.currentText()),  # area
            str(ogtm),  # materiale
            str(ldct),  # tipo collocazione
            str(ldcn),  # denominazione
            str(vecchia_collocazione),
            str(cassetta),
            str(scan),
            str(saggio),
            str(vano_locus),
            str(dscd),
            str(dscu),  # US
            str(rcgd),
            str(rcgz),
            str(aint),
            str(aind),
            str(dtzg),  # Single chronology
            str(deso),
            str(nsc),
            str(ftap),
            str(ftan),
            str(drat),
            str(dran),
            str(draa),
            '',  # created_at
            '',  # updated_at
            '',  # created_by
            ''   # updated_by
        ]

    def get_foto_data(self):
        """Get photo data from table widget."""
        tipi = []
        codici = []

        for row in range(self.tableWidget_foto.rowCount()):
            tipo_item = self.tableWidget_foto.item(row, 0)
            codice_item = self.tableWidget_foto.item(row, 1)

            if tipo_item:
                tipi.append(tipo_item.text())
            if codice_item:
                codici.append(codice_item.text())

        return ';'.join(tipi), ';'.join(codici)

    def get_disegni_data(self):
        """Get drawings data from table widget."""
        tipi = []
        codici = []
        autori = []

        for row in range(self.tableWidget_disegni.rowCount()):
            tipo_item = self.tableWidget_disegni.item(row, 0)
            codice_item = self.tableWidget_disegni.item(row, 1)
            autore_item = self.tableWidget_disegni.item(row, 2)

            if tipo_item:
                tipi.append(tipo_item.text())
            if codice_item:
                codici.append(codice_item.text())
            if autore_item:
                autori.append(autore_item.text())

        return ';'.join(tipi), ';'.join(codici), ';'.join(autori)

    def setup_materials_table(self):
        """Setup the materials table widget with proper headers and structure."""
        # Enable horizontal header visibility (UI file has it disabled)
        self.tableWidget_materiali.horizontalHeader().setVisible(True)
        
        # Set column headers - Materiale moved from main form, Inventario removed
        headers = ["Materiale *", "Categoria *", "Classe", "Prec. tipologica", "Definizione", "Cronologia", "Quantità", "Peso"]
        self.tableWidget_materiali.setColumnCount(len(headers))
        self.tableWidget_materiali.setHorizontalHeaderLabels(headers)
        
        # Set column widths
        header = self.tableWidget_materiali.horizontalHeader()
        try:
            # Try newer PyQt5 method first
            from qgis.PyQt.QtWidgets import QHeaderView
            for i in range(len(headers)):
                header.setSectionResizeMode(i, QHeaderView.Stretch)
        except (ImportError, AttributeError):
            # Fallback for older versions
            try:
                for i in range(len(headers)):
                    header.setResizeMode(i, 1)  # 1 = Stretch
            except:
                pass  # If all else fails, just use default sizing

    def load_materials_table(self):
        """Load materials data for current TMA record from database."""
        if not self.DATA_LIST or self.rec_num >= len(self.DATA_LIST):
            return
            
        # Clear table
        self.tableWidget_materiali.setRowCount(0)
        
        # Ensure headers are visible
        self.setup_materials_table()
        
        try:
            # Get current TMA id
            current_tma_id = self.DATA_LIST[self.rec_num].id
            QgsMessageLog.logMessage(f"DEBUG TMA load_materials_table: current_tma_id = {current_tma_id}, type = {type(current_tma_id)}", "PyArchInit", Qgis.Info)
            
            # Convert to int to ensure consistent type
            current_tma_id = int(current_tma_id)
            
            # Use direct SQL query to avoid type comparison issues in query_bool
            from sqlalchemy import text
            from sqlalchemy.orm import sessionmaker
            
            # Create a session
            Session = sessionmaker(bind=self.DB_MANAGER.engine)
            session = Session()
            
            try:
                # Get materials using direct SQL
                sql = text("SELECT * FROM tma_materiali_ripetibili WHERE id_tma = :id_tma")
                result = session.execute(sql, {'id_tma': current_tma_id})
                
                # Process results
                for row in result:
                    table_row = self.tableWidget_materiali.rowCount()
                    self.tableWidget_materiali.insertRow(table_row)
                    
                    # Fill row data - map column indices from query result
                    # Assuming column order: id, id_tma, madi, macc, macl, macp, macd, cronologia_mac, macq, peso
                    item0 = QTableWidgetItem(str(row[2]) if row[2] else "")  # madi
                    # Store the material ID in the first item's user data
                    item0.setData(Qt.UserRole, int(row[0]))  # id
                    self.tableWidget_materiali.setItem(table_row, 0, item0)
                    
                    self.tableWidget_materiali.setItem(table_row, 1, QTableWidgetItem(str(row[3]) if row[3] else ""))  # macc
                    self.tableWidget_materiali.setItem(table_row, 2, QTableWidgetItem(str(row[4]) if row[4] else ""))  # macl
                    self.tableWidget_materiali.setItem(table_row, 3, QTableWidgetItem(str(row[5]) if row[5] else ""))  # macp
                    self.tableWidget_materiali.setItem(table_row, 4, QTableWidgetItem(str(row[6]) if row[6] else ""))  # macd
                    self.tableWidget_materiali.setItem(table_row, 5, QTableWidgetItem(str(row[7]) if row[7] else ""))  # cronologia_mac
                    self.tableWidget_materiali.setItem(table_row, 6, QTableWidgetItem(str(row[8]) if row[8] else ""))  # macq
                    self.tableWidget_materiali.setItem(table_row, 7, QTableWidgetItem(str(row[9]) if row[9] else ""))  # peso
                    
                QgsMessageLog.logMessage(f"DEBUG TMA load_materials_table: Loaded {self.tableWidget_materiali.rowCount()} materials", "PyArchInit", Qgis.Info)
                    
            finally:
                session.close()
                
        except Exception as e:
            QgsMessageLog.logMessage(f"DEBUG TMA load_materials_table: Error occurred: {str(e)}", "PyArchInit", Qgis.Warning)
            import traceback
            traceback.print_exc()
            QMessageBox.warning(self, "Error", f"Errore nel caricamento materiali: {str(e)}", QMessageBox.Ok)

    def save_materials_data(self, tma_id):
        """Save materials table data to database."""
        QgsMessageLog.logMessage(f"DEBUG TMA save_materials_data: CALLED with tma_id={tma_id}, type={type(tma_id)}", "PyArchInit", Qgis.Info)
        try:
            QgsMessageLog.logMessage(f"DEBUG TMA save_materials_data: Starting with tma_id={tma_id}, type={type(tma_id)}", "PyArchInit", Qgis.Info)
            
            # Use direct SQL to avoid type comparison issues in query_bool
            from sqlalchemy import text
            from sqlalchemy.orm import sessionmaker
            
            # Convert tma_id to int for consistency
            tma_id_int = int(tma_id)
            
            # Create a session
            Session = sessionmaker(bind=self.DB_MANAGER.engine)
            session = Session()
            
            try:
                # Get existing materials using direct SQL
                sql = text("SELECT * FROM tma_materiali_ripetibili WHERE id_tma = :id_tma")
                result = session.execute(sql, {'id_tma': tma_id_int})
                
                existing_materials = []
                for row in result:
                    # Create a simple object to hold the data
                    class MaterialData:
                        def __init__(self, row_data):
                            self.id = row_data[0]
                            self.id_tma = row_data[1]
                            self.madi = row_data[2]
                            self.macc = row_data[3]
                            self.macl = row_data[4]
                            self.macp = row_data[5]
                            self.macd = row_data[6]
                            self.cronologia_mac = row_data[7]
                            self.macq = row_data[8]
                            self.peso = row_data[9]
                    existing_materials.append(MaterialData(row))
                    
                QgsMessageLog.logMessage(f"DEBUG TMA: Found {len(existing_materials)} existing materials", "PyArchInit", Qgis.Info)
                
            except Exception as query_error:
                QgsMessageLog.logMessage(f"DEBUG TMA: Error getting existing materials: {query_error}", "PyArchInit", Qgis.Warning)
                import traceback
                traceback.print_exc()
                existing_materials = []
            finally:
                session.close()
            
            # Ensure IDs are integers for consistent comparison
            existing_ids = {}
            for mat in existing_materials:
                QgsMessageLog.logMessage(f"DEBUG TMA: Material ID={mat.id}, type={type(mat.id)}", "PyArchInit", Qgis.Info)
                existing_ids[int(mat.id)] = mat
            
            # Track which IDs we've seen in the table widget
            seen_ids = set()
            
            # Process each row in the table widget
            for row in range(self.tableWidget_materiali.rowCount()):
                QgsMessageLog.logMessage(f"DEBUG TMA: Processing row {row}", "PyArchInit", Qgis.Info)
                
                # Column 0 is Materiale (stored in madi field in database)
                materiale = self.tableWidget_materiali.item(row, 0).text() if self.tableWidget_materiali.item(row, 0) else ""
                macc = self.tableWidget_materiali.item(row, 1).text() if self.tableWidget_materiali.item(row, 1) else ""
                macl = self.tableWidget_materiali.item(row, 2).text() if self.tableWidget_materiali.item(row, 2) else ""
                macp = self.tableWidget_materiali.item(row, 3).text() if self.tableWidget_materiali.item(row, 3) else ""
                macd = self.tableWidget_materiali.item(row, 4).text() if self.tableWidget_materiali.item(row, 4) else ""
                cronologia_mac = self.tableWidget_materiali.item(row, 5).text() if self.tableWidget_materiali.item(row, 5) else ""
                macq = self.tableWidget_materiali.item(row, 6).text() if self.tableWidget_materiali.item(row, 6) else ""
                peso_text = self.tableWidget_materiali.item(row, 7).text() if self.tableWidget_materiali.item(row, 7) else ""
                
                QgsMessageLog.logMessage(f"DEBUG TMA: Row {row} data - materiale: '{materiale}', macc: '{macc}'", "PyArchInit", Qgis.Info)
                
                # Convert peso to float
                try:
                    peso = float(peso_text) if peso_text else 0.0
                except ValueError:
                    peso = 0.0
                
                # Skip completely empty rows
                if not materiale.strip() and not macc.strip():
                    QgsMessageLog.logMessage(f"DEBUG TMA: Skipping row {row} - both materiale and category are empty", "PyArchInit", Qgis.Info)
                    continue
                
                # Category is required if material is specified
                if materiale.strip() and not macc.strip():
                    QgsMessageLog.logMessage(f"DEBUG TMA: ERROR - row {row} has materiale but no category (required)", "PyArchInit", Qgis.Warning)
                    raise ValueError(f"Riga {row + 1}: Il campo Categoria è obbligatorio quando si inserisce un materiale")
                
                # Check if this row has an existing ID (stored as row data)
                material_id = self.tableWidget_materiali.item(row, 0).data(Qt.UserRole) if self.tableWidget_materiali.item(row, 0) else None
                QgsMessageLog.logMessage(f"DEBUG TMA: Row {row} material_id={material_id}, type={type(material_id)}", "PyArchInit", Qgis.Info)
                
                # Convert to int if not None
                if material_id is not None:
                    try:
                        material_id = int(material_id)
                        QgsMessageLog.logMessage(f"DEBUG TMA: Converted material_id to int: {material_id}", "PyArchInit", Qgis.Info)
                    except Exception as e:
                        QgsMessageLog.logMessage(f"DEBUG TMA: Error converting material_id to int: {e}", "PyArchInit", Qgis.Warning)
                        material_id = None
                
                if material_id is not None and material_id in existing_ids:
                    # Update existing material
                    seen_ids.add(material_id)
                    
                    # Check if data has changed
                    existing = existing_ids[material_id]
                    if (str(existing.madi or '') != materiale or 
                        str(existing.macc or '') != macc or 
                        str(existing.macl or '') != macl or 
                        str(existing.macp or '') != macp or 
                        str(existing.macd or '') != macd or 
                        str(existing.cronologia_mac or '') != cronologia_mac or 
                        str(existing.macq or '') != macq or 
                        float(existing.peso or 0) != peso):
                        
                        # Data has changed, update record
                        update_values_dict = {
                            'madi': materiale,  # Column 0 is materiale, stored in madi field
                            'macc': macc,
                            'macl': macl,
                            'macp': macp,
                            'macd': macd,
                            'cronologia_mac': cronologia_mac,
                            'macq': macq,
                            'peso': peso
                        }
                        
                        # Update using the DB manager's update method
                        self.DB_MANAGER.update('TMA_MATERIALI', 'id', [material_id], 
                                               list(update_values_dict.keys()), 
                                               list(update_values_dict.values()))
                else:
                    # Insert new material
                    try:
                        max_id = self.DB_MANAGER.max_num_id('TMA_MATERIALI', 'id')
                        new_material_id = (max_id + 1) if max_id is not None else 1
                    except:
                        new_material_id = 1
                    
                    # Use direct SQL insert to avoid foreign key issues with SQLAlchemy ORM
                    try:
                        # Create a new session for the insert operation
                        from sqlalchemy import text
                        from sqlalchemy.orm import sessionmaker
                        
                        InsertSession = sessionmaker(bind=self.DB_MANAGER.engine)
                        insert_session = InsertSession()
                        
                        try:
                            # Use direct SQL - this works better with SQLite foreign keys
                            sql = """INSERT INTO tma_materiali_ripetibili 
                                    (id, id_tma, madi, macc, macl, macp, macd, cronologia_mac, macq, peso, 
                                     created_at, updated_at, created_by, updated_by)
                                    VALUES (:id, :id_tma, :madi, :macc, :macl, :macp, :macd, :cronologia_mac, :macq, :peso, 
                                            :created_at, :updated_at, :created_by, :updated_by)"""
                            
                            params = {
                                'id': new_material_id,
                                'id_tma': tma_id_int,  # Use the integer version
                                'madi': materiale,
                                'macc': macc,
                                'macl': macl,
                                'macp': macp,
                                'macd': macd,
                                'cronologia_mac': cronologia_mac,
                                'macq': macq,
                                'peso': peso,
                                'created_at': '',
                                'updated_at': '',
                                'created_by': '',
                                'updated_by': ''
                            }
                            
                            insert_session.execute(text(sql), params)
                            insert_session.commit()
                            
                        finally:
                            insert_session.close()
                            
                    except Exception as insert_error:
                        QgsMessageLog.logMessage(f"SQL insert failed: {insert_error}", "PyArchInit", Qgis.Warning)
                        raise
                    seen_ids.add(new_material_id)
            
            # Delete materials that were removed from the table
            for existing_id in existing_ids:
                if existing_id not in seen_ids:
                    self.DB_MANAGER.delete_record_by_field('TMA_MATERIALI', 'id', existing_id)
                    
        except Exception as e:
            import traceback
            traceback.print_exc()
            error_msg = f"Errore nel salvataggio materiali: {str(e)}\n\n"
            error_msg += f"TMA ID: {tma_id}\n"
            error_msg += f"Tabelle verificate nel database."
            QMessageBox.warning(self, "Error", error_msg, QMessageBox.Ok)

    def on_pushButton_add_materiale_pressed(self):
        """Add a new row to materials table."""
        # Disconnect signal temporarily to prevent double add
        try:
            self.pushButton_add_materiale.clicked.disconnect()
        except:
            pass
            
        row = self.tableWidget_materiali.rowCount()
        self.tableWidget_materiali.insertRow(row)
        
        # Debug: check if delegates are working
        QgsMessageLog.logMessage(f"DEBUG TMA: Adding new row {row}", "PyArchInit", Qgis.Info)
        for col in range(5):  # Check first 5 columns which should have thesaurus
            delegate = self.tableWidget_materiali.itemDelegateForColumn(col)
            if delegate:
                QgsMessageLog.logMessage(f"  Column {col} has delegate: {type(delegate).__name__}", "PyArchInit", Qgis.Info)
        
        # Don't set items - let the delegate handle it
        # Just ensure the table has the right number of columns
        for col in range(self.tableWidget_materiali.columnCount()):
            if not self.tableWidget_materiali.item(row, col):
                self.tableWidget_materiali.setItem(row, col, QTableWidgetItem(""))
        
        # Reconnect signal
        self.pushButton_add_materiale.clicked.connect(self.on_pushButton_add_materiale_pressed)

    def on_pushButton_remove_materiale_pressed(self):
        """Remove selected row from materials table."""
        current_row = self.tableWidget_materiali.currentRow()
        if current_row >= 0:
            self.tableWidget_materiali.removeRow(current_row)
    
    def update_material_navigation(self):
        """Update navigation buttons for materials table."""
        # This method updates the navigation UI based on current position
        # For now, we'll keep navigation buttons always enabled
        pass
    

    def set_LIST_REC_CORR(self):
        """Set the current record list."""
        self.DATA_LIST_REC_CORR = []
        for i in self.TABLE_FIELDS:
            self.DATA_LIST_REC_CORR.append(eval("str(self.DATA_LIST[self.REC_CORR]." + i + ")"))

    def empty_fields(self):
        """Clear all form fields."""
        # Basic fields
        self.comboBox_sito.setEditText("")
        self.comboBox_area.setEditText("")
        self.lineEdit_us.clear()

        # All other fields
        self.comboBox_ldct.setEditText("")
        self.comboBox_ldcn.setEditText("")
        self.lineEdit_vecchia_collocazione.clear()
        self.lineEdit_cassetta.clear()
        self.lineEdit_scan.clear()
        self.comboBox_saggio.setEditText("")
        self.comboBox_vano_locus.setEditText("")
        self.lineEdit_dscd.clear()
        self.lineEdit_rcgd.clear()
        self.textEdit_rcgz.clear()
        self.comboBox_aint.setCurrentIndex(0)
        self.lineEdit_aind.clear()
        self.lineEdit_dtzg.clear()
        self.textEdit_deso.clear()
        
        # Clear materials table
        self.tableWidget_materiali.setRowCount(0)
        # Ensure headers are visible
        self.setup_materials_table()
        
        # Clear inventory field
        self.lineEdit_inventario.clear()
        
        # Reset materials navigation
        self.current_material_index = -1
        self.materials_data = []
        self.update_material_navigation()

        # Clear tables
        self.tableWidget_foto.setRowCount(0)
        self.tableWidget_disegni.setRowCount(0)

    def empty_fields_nosite(self):
        """Clear all form fields."""
        # Basic fields
        self.comboBox_sito.setEditText("")
        self.comboBox_area.setEditText("")
        self.lineEdit_us.clear()

        # All other fields
        self.comboBox_ldct.setEditText("")
        self.comboBox_ldcn.setEditText("")
        self.lineEdit_vecchia_collocazione.clear()
        self.lineEdit_cassetta.clear()
        self.lineEdit_scan.clear()
        self.comboBox_saggio.setEditText("")
        self.comboBox_vano_locus.setEditText("")
        self.lineEdit_dscd.clear()
        self.lineEdit_rcgd.clear()
        self.textEdit_rcgz.clear()
        self.comboBox_aint.setCurrentIndex(0)
        self.lineEdit_aind.clear()
        self.lineEdit_dtzg.clear()
        self.textEdit_deso.clear()

        # Clear materials table
        self.tableWidget_materiali.setRowCount(0)
        # Ensure headers are visible
        self.setup_materials_table()

        # Clear inventory field
        self.lineEdit_inventario.clear()

        # Reset materials navigation
        self.current_material_index = -1
        self.materials_data = []
        self.update_material_navigation()

        # Clear tables
        self.tableWidget_foto.setRowCount(0)
        self.tableWidget_disegni.setRowCount(0)
    # def check_record_state(self):
    #     """Check if the current record has been modified."""
    #     ec = self.data_error_check()
    #     if ec == 1:
    #         return 1
    #
    #     if self.DATA_LIST:
    #         self.set_LIST_REC_TEMP()
    #         self.set_LIST_REC_CORR()
    #
    #         # Check main record changes
    #         main_record_changed = self.DATA_LIST_REC_CORR != self.DATA_LIST_REC_TEMP
    #
    #         # Check if materials have changed
    #         materials_changed = self.check_materials_state()
    #
    #         if main_record_changed or materials_changed:
    #             return 1
    #         else:
    #             return 0
    #     else:
    #         return 0
    def check_record_state(self):
        QgsMessageLog.logMessage(f"DEBUG check_record_state - iniziato", "PyArchInit", Qgis.Info)
        ec = self.data_error_check()
        QgsMessageLog.logMessage(f"DEBUG check_record_state - data_error_check returned: {ec}", "PyArchInit", Qgis.Info)
        if ec == 1:
            return 1  # ci sono errori di immissione
        
        rec_equal_result = self.records_equal_check()
        QgsMessageLog.logMessage(f"DEBUG check_record_state - records_equal_check returned: {rec_equal_result}", "PyArchInit", Qgis.Info)
        
        if rec_equal_result == 1 and ec == 0:
            if self.L=='it':
                self.update_if(
                    QMessageBox.warning(self, 'Errore', "Il record e' stato modificato. Vuoi salvare le modifiche?",
                                        QMessageBox.Ok | QMessageBox.Cancel))
            elif self.L=='de':
                self.update_if(
                    QMessageBox.warning(self, 'Errore', "Der Record wurde geändert. Möchtest du die Änderungen speichern?",
                                        QMessageBox.Ok | QMessageBox.Cancel))
            else:
                self.update_if(
                    QMessageBox.warning(self, "Error", "The record has been changed. You want to save the changes?",
                                        QMessageBox.Ok | QMessageBox.Cancel))
        return 0  # Importante: deve sempre ritornare 0 se non ci sono errori
    def check_materials_state(self):
        """Check if materials in the table have changed compared to database."""
        QgsMessageLog.logMessage("DEBUG TMA: check_materials_state called", "PyArchInit", Qgis.Info)
        try:
            if not self.DATA_LIST or self.REC_CORR >= len(self.DATA_LIST):
                QgsMessageLog.logMessage("DEBUG TMA: New record or no data list", "PyArchInit", Qgis.Info)
                # New record, check if table has content with valid data
                for row in range(self.tableWidget_materiali.rowCount()):
                    macc = self.tableWidget_materiali.item(row, 1).text() if self.tableWidget_materiali.item(row, 1) else ""
                    if macc.strip():  # At least one row has category filled
                        return True
                return False
            
            # Get current materials from database using direct SQL to avoid type issues
            current_tma_id = self.DATA_LIST[self.REC_CORR].id
            QgsMessageLog.logMessage(f"DEBUG TMA: Getting materials for TMA ID {current_tma_id}, type={type(current_tma_id)}", "PyArchInit", Qgis.Info)
            
            # Use direct SQL query to avoid type comparison issues in query_bool
            from sqlalchemy import text
            from sqlalchemy.orm import sessionmaker
            
            # Convert tma_id to int for consistency
            tma_id_int = int(current_tma_id)
            
            # Create a session
            Session = sessionmaker(bind=self.DB_MANAGER.engine)
            session = Session()
            
            try:
                # Get existing materials using direct SQL
                sql = text("SELECT * FROM tma_materiali_ripetibili WHERE id_tma = :id_tma")
                result = session.execute(sql, {'id_tma': tma_id_int})
                
                # Convert results to list of dictionaries
                db_materials = []
                for row in result:
                    # Create a dictionary with material data
                    # Access by index since we're using direct SQL
                    mat_dict = {
                        'id': row[0],
                        'id_tma': row[1],
                        'madi': row[2],
                        'macc': row[3],
                        'macl': row[4],
                        'macp': row[5],
                        'macd': row[6],
                        'cronologia_mac': row[7],
                        'macq': row[8],
                        'peso': row[9]
                    }
                    db_materials.append(mat_dict)
                
                # Create a map of existing materials by ID
                db_materials_by_id = {mat['id']: mat for mat in db_materials}
                
                # Track which IDs we've seen and count valid rows
                seen_ids = set()
                valid_rows = 0
                
                # Check all rows in the table
                for row in range(self.tableWidget_materiali.rowCount()):
                    # Get category to check if row is valid
                    macc = self.tableWidget_materiali.item(row, 1).text() if self.tableWidget_materiali.item(row, 1) else ""
                    if not macc.strip():
                        continue  # Skip empty rows
                        
                    valid_rows += 1
                    
                    # Get the material ID stored in the first column's user data
                    material_id = self.tableWidget_materiali.item(row, 0).data(Qt.UserRole) if self.tableWidget_materiali.item(row, 0) else None
                    
                    if material_id is None:
                        # This is a new material
                        return True
                    
                    if material_id not in db_materials_by_id:
                        # Material ID exists in table but not in database (shouldn't happen)
                        return True
                    
                    seen_ids.add(material_id)
                    
                    # Compare values with database
                    db_material = db_materials_by_id[material_id]
                    
                    # Get values from table
                    table_madi = self.tableWidget_materiali.item(row, 0).text() if self.tableWidget_materiali.item(row, 0) else ""
                    table_macc = self.tableWidget_materiali.item(row, 1).text() if self.tableWidget_materiali.item(row, 1) else ""
                    table_macl = self.tableWidget_materiali.item(row, 2).text() if self.tableWidget_materiali.item(row, 2) else ""
                    table_macp = self.tableWidget_materiali.item(row, 3).text() if self.tableWidget_materiali.item(row, 3) else ""
                    table_macd = self.tableWidget_materiali.item(row, 4).text() if self.tableWidget_materiali.item(row, 4) else ""
                    table_cronologia = self.tableWidget_materiali.item(row, 5).text() if self.tableWidget_materiali.item(row, 5) else ""
                    table_macq = self.tableWidget_materiali.item(row, 6).text() if self.tableWidget_materiali.item(row, 6) else ""
                    table_peso = self.tableWidget_materiali.item(row, 7).text() if self.tableWidget_materiali.item(row, 7) else ""
                    
                    # Get values from database
                    db_madi = str(db_material['madi']) if db_material['madi'] else ""
                    db_macc = str(db_material['macc']) if db_material['macc'] else ""
                    db_macl = str(db_material['macl']) if db_material['macl'] else ""
                    db_macp = str(db_material['macp']) if db_material['macp'] else ""
                    db_macd = str(db_material['macd']) if db_material['macd'] else ""
                    db_cronologia = str(db_material['cronologia_mac']) if db_material['cronologia_mac'] else ""
                    db_macq = str(db_material['macq']) if db_material['macq'] else ""
                    db_peso = str(db_material['peso']) if db_material['peso'] else ""
                    
                    # Compare values
                    if (table_madi != db_madi or table_macc != db_macc or table_macl != db_macl or 
                        table_macp != db_macp or table_macd != db_macd or table_cronologia != db_cronologia or
                        table_macq != db_macq or table_peso != db_peso):
                        return True
                
                # Check if any materials were deleted (exist in DB but not seen in table)
                if len(seen_ids) != len(db_materials):
                    return True
                
                return False
                
            finally:
                session.close()
            
        except Exception as e:
            QgsMessageLog.logMessage(f"DEBUG TMA: Error in check_materials_state: {e}", "PyArchInit", Qgis.Warning)
            # If error occurs, assume changed to be safe
            return True

    def data_error_check(self):
        """Check for data errors in form fields."""
        test = 0
        EC = Error_check()

        # Check required fields
        # Note: materiale field has been moved to materials table

        if self.comboBox_ldcn.currentText() == "":
            QMessageBox.warning(self, "ATTENZIONE", "Campo Denominazione collocazione obbligatorio!", QMessageBox.Ok)
            test = 1
            return test

        if self.lineEdit_cassetta.text() == "":
            QMessageBox.warning(self, "ATTENZIONE", "Campo Cassetta obbligatorio!", QMessageBox.Ok)
            test = 1
            return test


        if self.lineEdit_us.text() == "":
            QMessageBox.warning(self, "ATTENZIONE", "Campo US obbligatorio!", QMessageBox.Ok)
            test = 1
            return test


        # Materials are now in the materials table and are optional

        return test

    def update_if(self, msg):
        """Update interface message."""
        print(f"DEBUG update_if - chiamato con msg={msg}")
        if msg == QMessageBox.Ok:
            print(f"DEBUG update_if - utente ha scelto OK, aggiornando il record")
            self.update_record_to_db()
        else:
            print(f"DEBUG update_if - utente ha scelto Cancel o altro")

    def on_pushButton_import_pressed(self):
        """Open import dialog."""
        from ..gui.tma_import_dialog import TMAImportDialog
        
        dlg = TMAImportDialog(self.DB_MANAGER, self)
        dlg.exec_()
        
        # Refresh data after import
        self.charge_records()
        self.charge_list()
        
        if self.DATA_LIST:
            self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), len(self.DATA_LIST) - 1
            self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[self.REC_CORR]
            self.fill_fields(self.REC_CORR)
            self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
            self.BROWSE_STATUS = 'b'
            self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
            self.label_sort.setText(self.SORTED_ITEMS["n"])
        
    def update_record(self):
        """Update the current record if modified."""
        if self.check_record_state() == 1:
            msg = QMessageBox.warning(self, "Attenzione",
                                      "Il record è stato modificato. Vuoi salvare le modifiche?",
                                      QMessageBox.Save | QMessageBox.Cancel)
            if msg == QMessageBox.Save:
                self.on_pushButton_save_pressed()

    def setComboBoxEnable(self, f, v):
        """Enable/disable comboboxes."""
        field_names = f
        value = v

        for field in field_names:
            field_name = eval(field)
            field_name.setEnabled(eval(value))

    def setComboBoxEditable(self, f, n):
        """Set combobox editable state."""
        field_names = f
        value = n

        for field in field_names:
            field_name = eval(field)
            field_name.setEditable(value)

    # Button event handlers
    def on_pushButton_first_rec_pressed(self):
        """Navigate to first record."""
        if self.check_record_state() == 1:
            self.update_if(QgsSettings().value("pyArchInit/ifupdaterecord"))
            return
            
        try:
            self.empty_fields()
            self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
            self.fill_fields(0)
            self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e), QMessageBox.Ok)

    def on_pushButton_last_rec_pressed(self):
        """Navigate to last record."""
        if self.check_record_state() == 1:
            self.update_if(QgsSettings().value("pyArchInit/ifupdaterecord"))
            return
            
        try:
            self.empty_fields()
            self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), len(self.DATA_LIST) - 1
            self.fill_fields(self.REC_CORR)
            self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e), QMessageBox.Ok)

    def on_pushButton_prev_rec_pressed(self):
        if self._nav_in_progress:
            QgsMessageLog.logMessage(f"PREV - Navigation already in progress, ignoring", "PyArchInit", Qgis.Warning)
            return
            
        QgsMessageLog.logMessage(f"PREV - Button clicked, queueing navigation", "PyArchInit", Qgis.Info)
        self._nav_direction = 'prev'
        self._nav_timer.stop()  # Stop any pending timer
        self._nav_timer.start(100)  # Start with 100ms delay

    def on_pushButton_next_rec_pressed(self):
        if self._nav_in_progress:
            QgsMessageLog.logMessage(f"NEXT - Navigation already in progress, ignoring", "PyArchInit", Qgis.Warning)
            return
            
        QgsMessageLog.logMessage(f"NEXT - Button clicked, queueing navigation", "PyArchInit", Qgis.Info)
        self._nav_direction = 'next'
        self._nav_timer.stop()  # Stop any pending timer
        self._nav_timer.start(100)  # Start with 100ms delay
    
    def _process_navigation(self):
        """Process the queued navigation after timer delay."""
        if self._nav_in_progress:
            return
            
        self._nav_in_progress = True
        QgsMessageLog.logMessage(f"Processing navigation: {self._nav_direction}", "PyArchInit", Qgis.Info)
        
        try:
            if self._nav_direction == 'prev':
                self._do_prev_navigation()
            elif self._nav_direction == 'next':
                self._do_next_navigation()
        finally:
            self._nav_in_progress = False
            self._nav_direction = None
    
    def _do_prev_navigation(self):
        """Execute previous record navigation."""
        QgsMessageLog.logMessage(f"PREV - REC_CORR prima: {self.REC_CORR}", "PyArchInit", Qgis.Info)
        
        if self.check_record_state() == 1:
            return
            
        self.REC_CORR = self.REC_CORR - 1
        if self.REC_CORR <= -1:
            self.REC_CORR = 0
            if self.L=='it':
                QMessageBox.warning(self, "Attenzione", "Sei al primo record!", QMessageBox.Ok)
            elif self.L=='de':
                QMessageBox.warning(self, "Achtung", "du befindest dich im ersten Datensatz!", QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "Warning", "You are to the first record!", QMessageBox.Ok)        
        else:
            try:
                self.empty_fields()
                self.fill_fields(self.REC_CORR)
                self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
            except Exception as e:
                QgsMessageLog.logMessage(f"PREV - Exception: {e}", "PyArchInit", Qgis.Critical)
                import traceback
                traceback.print_exc()
        
        QgsMessageLog.logMessage(f"PREV - REC_CORR dopo: {self.REC_CORR}", "PyArchInit", Qgis.Info)
    
    def _do_next_navigation(self):
        """Execute next record navigation."""
        QgsMessageLog.logMessage(f"NEXT - REC_CORR prima: {self.REC_CORR}", "PyArchInit", Qgis.Info)
        
        if self.check_record_state() == 1:
            return
            
        self.REC_CORR = self.REC_CORR + 1
        if self.REC_CORR >= self.REC_TOT:
            self.REC_CORR = self.REC_CORR - 1
            if self.L=='it':
                QMessageBox.warning(self, "Attenzione", "Sei all'ultimo record!", QMessageBox.Ok)
            elif self.L=='de':
                QMessageBox.warning(self, "Achtung", "du befindest dich im letzten Datensatz!", QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "Error", "You are to the last record!", QMessageBox.Ok)  
        else:
            try:
                self.empty_fields()
                self.fill_fields(self.REC_CORR)
                self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
            except Exception as e:
                QgsMessageLog.logMessage(f"NEXT - Exception: {e}", "PyArchInit", Qgis.Critical)
                import traceback
                traceback.print_exc()
        
        QgsMessageLog.logMessage(f"NEXT - REC_CORR dopo: {self.REC_CORR}", "PyArchInit", Qgis.Info)

    def on_pushButton_new_rec_pressed(self):
        """Create a new record."""
        if self.check_record_state() == 1:
            self.update_if(QgsSettings().value("pyArchInit/ifupdaterecord"))
            return
            
        if self.BROWSE_STATUS != "n":
            conn = Connection()
            sito_set = conn.sito_set()
            sito_set_str = sito_set['sito_set']
            
            self.BROWSE_STATUS = "n"
            self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
            self.empty_fields()
            self.label_sort.setText(self.SORTED_ITEMS["n"])

            if bool(sito_set_str):
                # When sito_set is active, set the site field and make it read-only
                self.comboBox_sito.setEditText(sito_set_str)
                self.setComboBoxEnable(["self.comboBox_sito"], "False")
                self.setComboBoxEditable(["self.comboBox_sito"], 0)
            else:
                # When sito_set is not active, allow site selection
                self.setComboBoxEnable(["self.comboBox_sito"], "True")
                self.setComboBoxEditable(["self.comboBox_sito"], 1)

            self.set_rec_counter('', '')
            self.label_sort.setText(self.SORTED_ITEMS["n"])

    def on_pushButton_save_pressed(self):
        """Save the current record."""
        
        try:
            if self.BROWSE_STATUS == "b":
                if self.data_error_check() == 0:
                    try:
                        record_state = self.check_record_state()
                        if record_state == 1:
                            self.update_record_to_db()
                            self.SORT_STATUS = "n"
                            self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
                    except Exception as e:
                        import traceback
                        traceback.print_exc()
                        QMessageBox.warning(self, "Error", f"Errore nel salvataggio materiali: {str(e)}", QMessageBox.Ok)
                    self.enable_button(1)
                    self.fill_fields(self.REC_CORR)
                else:
                    QMessageBox.warning(self, "ATTENZIONE", "Non è stata realizzata alcuna modifica!", QMessageBox.Ok)
            else:
                if self.data_error_check() == 0:
                    test_insert = self.insert_new_rec()
                    if test_insert == 1:
                        self.empty_fields()
                        self.label_sort.setText(self.SORTED_ITEMS["n"])
                        self.charge_list()
                        self.charge_records()
                        self.BROWSE_STATUS = "b"
                        self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                        self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), len(self.DATA_LIST) - 1
                        self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)

                        self.setComboBoxEnable(["self.comboBox_sito"], "False")
                        self.fill_fields(self.REC_CORR)
                        self.enable_button(1)
                    else:
                        pass
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.warning(self, "Error", f"Errore nel salvataggio: {str(e)}", QMessageBox.Ok)

    def on_pushButton_delete_pressed(self):
        """Delete the current record."""
        msg = QMessageBox.warning(self, "Attenzione!!!",
                                  "Vuoi veramente eliminare il record? \n L'azione è irreversibile",
                                  QMessageBox.Ok | QMessageBox.Cancel)
        if msg == QMessageBox.Ok:
            try:
                id_to_delete = eval("self.DATA_LIST[self.REC_CORR]." + self.ID_TABLE)
                self.DB_MANAGER.delete_one_record(self.TABLE_NAME, self.ID_TABLE, id_to_delete)
                self.charge_list()
                self.charge_records()
                QMessageBox.warning(self, "Messaggio", "Record eliminato!", QMessageBox.Ok)
            except Exception as e:
                QMessageBox.warning(self, "Messaggio", "Problema di connessione", QMessageBox.Ok)

            if not bool(self.DATA_LIST):
                self.DATA_LIST = []
                self.DATA_LIST_REC_CORR = []
                self.DATA_LIST_REC_TEMP = []
                self.REC_CORR = 0
                self.REC_TOT = 0
                self.empty_fields()
                self.set_rec_counter(0, 0)
            elif self.REC_CORR == 0:
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                self.fill_fields()
                self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
            elif self.REC_CORR == self.REC_TOT:
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), len(self.DATA_LIST) - 1
                self.fill_fields(self.REC_CORR)
                self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)

    def on_pushButton_new_search_pressed(self):
        """Enable search mode."""
        if self.check_record_state() == 1:
            self.update_if(QgsSettings().value("pyArchInit/ifupdaterecord"))
            return
            
        self.enable_button_search(0)
        self.BROWSE_STATUS = "f"
        self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])

        self.setComboBoxEnable(["self.comboBox_sito"], "True")
        self.setComboBoxEditable(["self.comboBox_sito"], 1)

        self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
        self.set_rec_counter('', '')
        self.label_sort.setText(self.SORTED_ITEMS["n"])
        self.empty_fields()

    def on_pushButton_search_go_pressed(self):
        """Execute search."""
        if self.BROWSE_STATUS != "f":
            QMessageBox.warning(self, "ATTENZIONE", "Per eseguire una nuova ricerca clicca sul pulsante 'new search'",
                                QMessageBox.Ok)
        else:
            search_dict = self.build_search_dict()

            if not bool(search_dict):
                QMessageBox.warning(self, "ATTENZIONE", "Non è stata impostata alcuna ricerca!", QMessageBox.Ok)
            else:
                res = self.DB_MANAGER.query_bool(search_dict, 'TMA')

                if not bool(res):
                    QMessageBox.warning(self, "ATTENZIONE", "Non è stato trovato alcun record!", QMessageBox.Ok)

                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                    self.fill_fields(self.REC_CORR)
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])

                    self.setComboBoxEnable(["self.comboBox_sito"], "False")

                else:
                    self.DATA_LIST = []
                    for i in res:
                        self.DATA_LIST.append(i)
                    self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                    self.fill_fields()
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)

                    if self.REC_TOT == 1:
                        strings = ("È stato trovato", self.REC_TOT, "record")
                    else:
                        strings = ("Sono stati trovati", self.REC_TOT, "record")

                    self.setComboBoxEnable(["self.comboBox_sito"], "False")

                    QMessageBox.warning(self, "Messaggio", "%s %d %s" % strings, QMessageBox.Ok)

        self.enable_button_search(1)

    def on_pushButton_sort_pressed(self):
        """Open sort dialog."""
        dlg = SortPanelMain(self)
        dlg.insertItems(self.SORT_ITEMS)
        dlg.exec_()

        items, order_type = dlg.ITEMS, dlg.TYPE_ORDER

        if not items:
            QMessageBox.warning(self, "Messaggio", "Non hai ordinato alcun campo", QMessageBox.Ok)
        else:
            self.SORT_ITEMS_CONVERTED = []
            for i in items:
                self.SORT_ITEMS_CONVERTED.append(self.CONVERSION_DICT[str(i)])

            self.SORT_MODE = order_type
            self.empty_fields()

            id_list = self.DATA_LIST[self.REC_CORR].id

            self.DATA_LIST = self.DB_MANAGER.query_sort(id_list, self.SORT_ITEMS_CONVERTED, self.SORT_MODE,
                                                        self.MAPPER_TABLE_CLASS, self.ID_TABLE)
            self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
            self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
            self.SORT_STATUS = "o"
            self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
            self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
            self.fill_fields()

    def on_pushButton_view_all_pressed(self):
        """View all records."""
        if self.check_record_state() == 1:
            self.update_if(QgsSettings().value("pyArchInit/ifupdaterecord"))
            return
            
        self.empty_fields()
        self.charge_records()
        self.fill_fields()
        self.BROWSE_STATUS = "b"
        self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
        if type(self.REC_CORR) == "<type 'str'>":
            corr = 0
        else:
            corr = self.REC_CORR

        self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
        self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
        self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
        self.label_sort.setText(self.SORTED_ITEMS["n"])

    # Table widget handlers
    def on_pushButton_add_foto_pressed(self):
        """Add a photo row to the documentation table."""
        row_position = self.tableWidget_foto.rowCount()
        self.tableWidget_foto.insertRow(row_position)

    def on_pushButton_remove_foto_pressed(self):
        """Remove selected photo row from documentation table."""
        row = self.tableWidget_foto.currentRow()
        if row >= 0:
            self.tableWidget_foto.removeRow(row)

    def on_pushButton_add_disegno_pressed(self):
        """Add a drawing row to the documentation table."""
        row_position = self.tableWidget_disegni.rowCount()
        self.tableWidget_disegni.insertRow(row_position)

    def on_pushButton_remove_disegno_pressed(self):
        """Remove selected drawing row from documentation table."""
        row = self.tableWidget_disegni.currentRow()
        if row >= 0:
            self.tableWidget_disegni.removeRow(row)

    # GIS handlers
    def on_toolButtonGis_toggled(self):
        """Handle GIS button toggle."""
        if self.toolButtonGis.isChecked():
            QMessageBox.warning(self, "Messaggio",
                                "Sistema attivato. Da ora le tue ricerche verranno visualizzate sul GIS",
                                QMessageBox.Ok)
        else:
            QMessageBox.warning(self, "Messaggio",
                                "Sistema disattivato. Da ora le tue ricerche non verranno visualizzate sul GIS",
                                QMessageBox.Ok)

    # Export handlers
    def on_pushButton_open_dir_pressed(self):
        """Open media directory."""
        HOME = os.environ['PYARCHINIT_HOME']
        path = '{}{}{}'.format(HOME, os.sep, "pyarchinit_Media_folder")
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

    def build_search_dict(self):
        """Build search dictionary from form fields."""
        search_dict = {}

        if self.comboBox_sito.currentText() != "":
            search_dict['sito'] = "'" + str(self.comboBox_sito.currentText()) + "'"

        if self.comboBox_area.currentText() != "":
            search_dict['area'] = "'" + str(self.comboBox_area.currentText()) + "'"

        if self.lineEdit_us.text() != "":
            search_dict['dscu'] = "'" + str(self.lineEdit_us.text()) + "'"

        # Note: materiale field has been moved to materials table

        if self.comboBox_ldcn.currentText() != "":
            search_dict['ldcn'] = "'" + str(self.comboBox_ldcn.currentText()) + "'"

        if self.lineEdit_cassetta.text() != "":
            search_dict['cassetta'] = "'" + str(self.lineEdit_cassetta.text()) + "'"


        if self.lineEdit_dtzg.text() != "":
            search_dict['dtzg'] = "'" + str(self.lineEdit_dtzg.text()) + "'"

        return search_dict

    def insert_new_rec(self):
        """Insert a new record into the database."""
        try:
            # Get documentation data from tables
            ftap, ftan = self.get_foto_data()
            drat, dran, draa = self.get_disegni_data()

            # Build the data tuple from form fields
            data = self.DB_MANAGER.insert_tma_values(
                self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, self.ID_TABLE) + 1,
                str(self.comboBox_sito.currentText()),
                str(self.comboBox_area.currentText()),
                '',  # ogtm - materiale field has been moved to materials table
                str(self.comboBox_ldct.currentText()),
                str(self.comboBox_ldcn.currentText()),
                str(self.lineEdit_vecchia_collocazione.text()),
                str(self.lineEdit_cassetta.text()),
                str(self.lineEdit_scan.text()),
                str(self.comboBox_saggio.currentText()),
                str(self.comboBox_vano_locus.currentText()),
                str(self.lineEdit_dscd.text()),
                str(self.lineEdit_us.text()),  # dscu
                str(self.lineEdit_rcgd.text()),
                str(self.textEdit_rcgz.toPlainText()),
                str(self.comboBox_aint.currentText()),
                str(self.lineEdit_aind.text()),
                str(self.lineEdit_dtzg.text()),  # Single chronology field
                str(self.textEdit_deso.toPlainText()),
                '',  # nsc field doesn't exist in UI
                ftap,
                ftan,
                drat,
                dran,
                draa,
                '',  # created_at
                '',  # updated_at
                '',  # created_by
                ''   # updated_by
            )

            self.DB_MANAGER.insert_data_session(data)
            
            # Get the ID of the inserted record and save materials
            inserted_id = self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, self.ID_TABLE)
            self.save_materials_data(inserted_id)
            
            return 1

        except Exception as e:
            QMessageBox.warning(self, "Error", "Problema nell'inserimento: " + str(e), QMessageBox.Ok)
            return 0

    def update_record_to_db(self):
        """Update current record in database."""
        try:
            # Get documentation data from tables
            ftap, ftan = self.get_foto_data()
            drat, dran, draa = self.get_disegni_data()

            # Update main TMA record
            self.set_LIST_REC_TEMP()  # This sets self.DATA_LIST_REC_TEMP
            self.DB_MANAGER.update(self.MAPPER_TABLE_CLASS,
                                   self.ID_TABLE,
                                   [eval("int(self.DATA_LIST[self.REC_CORR]." + self.ID_TABLE + ")")],
                                   self.TABLE_FIELDS,
                                   self.DATA_LIST_REC_TEMP)
            
            # Save materials data for updated record
            current_id = eval("int(self.DATA_LIST[self.REC_CORR]." + self.ID_TABLE + ")")
            self.save_materials_data(current_id)
            
            return 1
        except Exception as e:
            QMessageBox.warning(self, "Error", "Problema nell'aggiornamento: " + str(e), QMessageBox.Ok)
            return 0
    
    def on_pushButton_export_pdf_pressed(self):
        """Export current TMA record to PDF."""
        if not self.DATA_LIST:
            QMessageBox.warning(self, "Attenzione", "Nessun record da esportare!", QMessageBox.Ok)
            return
            
        try:
            # Get current TMA record
            current_tma = self.DATA_LIST[self.REC_CORR]
            
            # Get materials for this TMA
            search_dict = {'id_tma': int(current_tma.id)}
            materials = self.DB_MANAGER.query_bool(search_dict, 'TMA_MATERIALI')
            
            # Get thumbnail path following Inv_Materiali logic
            conn = Connection()
            thumb_resize = conn.thumb_resize()
            thumb_path_str = thumb_resize['thumb_resize']
            
            # Search for media using MEDIAVIEW
            id_entity = str(current_tma.id)
            search_media = {'id_entity': "'" + id_entity + "'",
                           'entity_type': "'TMA'"}
            
            record_media_list = self.DB_MANAGER.query_bool(search_media, 'MEDIAVIEW')
            
            thumbnail_path = ''
            if record_media_list:
                # Get first image path
                try:
                    thumbnail_path = thumb_path_str + str(record_media_list[0].path_resize)
                except:
                    thumbnail_path = ''
            
            # Prepare data for PDF - pass as list [record, materials, thumbnail]
            data = [current_tma, materials, thumbnail_path]
            
            # Generate PDF
            tma_pdf = single_TMA_pdf(data)
            pdf_path = tma_pdf.file_path if hasattr(tma_pdf, 'file_path') else self.PDFFOLDER
            
            if self.L == 'it':
                QMessageBox.information(self, "Esportazione completata", 
                                        f"Scheda TMA esportata con successo!\nFile: {pdf_path}", 
                                        QMessageBox.Ok)
            else:
                QMessageBox.information(self, "Export completed", 
                                        f"TMA form exported successfully!\nFile: {pdf_path}", 
                                        QMessageBox.Ok)
            
            # Open the PDF file
            if platform.system() == "Windows":
                os.startfile(pdf_path)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", pdf_path])
            else:
                subprocess.Popen(["xdg-open", pdf_path])
                
        except Exception as e:
            QMessageBox.warning(self, "Errore", f"Errore nell'esportazione PDF: {str(e)}", QMessageBox.Ok)
    
    def on_pushButton_export_tma_pdf_pressed(self):
        """Export current TMA record to PDF using the specific TMA template."""
        self.on_pushButton_print_pressed()  # Use the new print dialog
    
    def on_pushButton_auto_fill_materials_pressed(self):
        """Auto-fill materials from inventory based on site/area/us."""
        try:
            # Get current site, area, us
            sito = self.comboBox_sito.currentText()
            area = self.comboBox_area.currentText()
            us = self.lineEdit_us.text()
            
            if not sito or not area or not us:
                QMessageBox.warning(self, "Attenzione", 
                                    "Compilare Sito, Area e US per recuperare i materiali dall'inventario!", 
                                    QMessageBox.Ok)
                return
            
            # Query inventory materials with repertato = 'Si'
            search_dict = {
                'sito': f"'{sito}'",
                'area': f"'{area}'",
                'us': f"'{us}'",
                'repertato': "'Si'"
            }
            
            inventory_materials = self.DB_MANAGER.query_bool(search_dict, 'INVENTARIO_MATERIALI')
            
            if not inventory_materials:
                QMessageBox.information(self, "Info", 
                                        f"Nessun materiale repertato trovato per Sito: {sito}, Area: {area}, US: {us}", 
                                        QMessageBox.Ok)
                return
            
            # Ask user for confirmation
            msg = QMessageBox.question(self, "Conferma", 
                                       f"Trovati {len(inventory_materials)} materiali repertati.\n"
                                       f"Vuoi aggiungerli alla tabella materiali?", 
                                       QMessageBox.Yes | QMessageBox.No)
            
            if msg == QMessageBox.No:
                return
            
            # Add materials to table
            for inv_mat in inventory_materials:
                row = self.tableWidget_materiali.rowCount()
                self.tableWidget_materiali.insertRow(row)
                
                # Map inventory fields to TMA materials fields
                # Inventario (n_reperto)
                self.tableWidget_materiali.setItem(row, 0, 
                    QTableWidgetItem(str(inv_mat.n_reperto) if inv_mat.n_reperto else ""))
                
                # Categoria (tipo_reperto)
                self.tableWidget_materiali.setItem(row, 1, 
                    QTableWidgetItem(str(inv_mat.tipo_reperto) if inv_mat.tipo_reperto else ""))
                
                # Classe (tipo)
                self.tableWidget_materiali.setItem(row, 2, 
                    QTableWidgetItem(str(inv_mat.tipo) if inv_mat.tipo else ""))
                
                # Prec. tipologica (criterio_schedatura)
                self.tableWidget_materiali.setItem(row, 3, 
                    QTableWidgetItem(str(inv_mat.criterio_schedatura) if inv_mat.criterio_schedatura else ""))
                
                # Definizione
                self.tableWidget_materiali.setItem(row, 4, 
                    QTableWidgetItem(str(inv_mat.definizione) if inv_mat.definizione else ""))
                
                # Cronologia MAC (datazione_reperto)
                self.tableWidget_materiali.setItem(row, 5, 
                    QTableWidgetItem(str(inv_mat.datazione_reperto) if inv_mat.datazione_reperto else ""))
                
                # Quantità (totale_frammenti)
                self.tableWidget_materiali.setItem(row, 6, 
                    QTableWidgetItem(str(inv_mat.totale_frammenti) if inv_mat.totale_frammenti else "1"))
                
                # Peso
                self.tableWidget_materiali.setItem(row, 7, 
                    QTableWidgetItem(str(inv_mat.peso) if inv_mat.peso else ""))
            
            QMessageBox.information(self, "Completato", 
                                    f"Aggiunti {len(inventory_materials)} materiali dall'inventario!", 
                                    QMessageBox.Ok)
            
        except Exception as e:
            QMessageBox.warning(self, "Errore", f"Errore nel recupero materiali: {str(e)}", QMessageBox.Ok)
    
    def on_us_changed(self):
        """Handle US field change to sync chronology."""
        try:
            # Only proceed if we have site, area, and us
            sito = self.comboBox_sito.currentText()
            area = self.comboBox_area.currentText()
            us = self.lineEdit_us.text()
            
            QgsMessageLog.logMessage(f"DEBUG TMA: on_us_changed called - sito: {sito}, area: {area}, us: {us}", "PyArchInit", Qgis.Info)
            
            if not sito or not area or not us:
                QgsMessageLog.logMessage("DEBUG TMA: Missing sito, area, or us - returning", "PyArchInit", Qgis.Info)
                return
            
            # Query US record
            search_dict = {
                'sito': f"'{sito}'",
                'area': f"'{area}'",
                'us': int(us) if us.isdigit() else 0
            }
            
            QgsMessageLog.logMessage(f"DEBUG TMA: Querying US with search_dict: {search_dict}", "PyArchInit", Qgis.Info)
            us_records = self.DB_MANAGER.query_bool(search_dict, 'US')
            QgsMessageLog.logMessage(f"DEBUG TMA: Found {len(us_records) if us_records else 0} US records", "PyArchInit", Qgis.Info)
            
            if us_records and len(us_records) > 0:
                us_record = us_records[0]
                
                # Try different field names for datazione
                datazione_value = None
                if hasattr(us_record, 'datazione_estesa') and us_record.datazione_estesa:
                    datazione_value = str(us_record.datazione_estesa)
                elif hasattr(us_record, 'datazione') and us_record.datazione:
                    datazione_value = str(us_record.datazione)
                
                if datazione_value:
                    self.lineEdit_dtzg.setText(datazione_value)
                    QgsMessageLog.logMessage(f"DEBUG TMA: Set fascia cronologica to: {datazione_value}", "PyArchInit", Qgis.Info)
                else:
                    # If no datazione field, try to build from period/phase
                    datazione = ""
                    periodo_iniziale = getattr(us_record, 'periodo_iniziale', None)
                    fase_iniziale = getattr(us_record, 'fase_iniziale', None)
                    periodo_finale = getattr(us_record, 'periodo_finale', None)
                    fase_finale = getattr(us_record, 'fase_finale', None)
                    
                    QgsMessageLog.logMessage(f"DEBUG TMA: Building from periodo/fase: {periodo_iniziale}/{fase_iniziale} - {periodo_finale}/{fase_finale}", "PyArchInit", Qgis.Info)
                    
                    # Check if initial and final are the same
                    if periodo_iniziale and periodo_finale and str(periodo_iniziale) == str(periodo_finale):
                        # Same period
                        datazione = f"Periodo {periodo_iniziale}"
                        if fase_iniziale and fase_finale and str(fase_iniziale) == str(fase_finale):
                            # Same phase
                            datazione += f", Fase {fase_iniziale}"
                        elif fase_iniziale and fase_finale and str(fase_iniziale) != str(fase_finale):
                            # Different phases in same period
                            datazione += f", Fase {fase_iniziale} - {fase_finale}"
                        elif fase_iniziale:
                            datazione += f", Fase {fase_iniziale}"
                        elif fase_finale:
                            datazione += f", Fase {fase_finale}"
                    else:
                        # Different periods or only one period
                        if periodo_iniziale:
                            datazione = f"Periodo {periodo_iniziale}"
                            if fase_iniziale:
                                datazione += f", Fase {fase_iniziale}"
                        if periodo_finale and str(periodo_finale) != str(periodo_iniziale):
                            if datazione:
                                datazione += " - "
                            datazione += f"Periodo {periodo_finale}"
                            if fase_finale:
                                datazione += f", Fase {fase_finale}"
                    
                    if datazione:
                        self.lineEdit_dtzg.setText(datazione)
                        QgsMessageLog.logMessage(f"DEBUG TMA: Set fascia cronologica from periodo/fase to: {datazione}", "PyArchInit", Qgis.Info)
                    else:
                        self.lineEdit_dtzg.clear()
                        QgsMessageLog.logMessage("DEBUG TMA: No datazione data available", "PyArchInit", Qgis.Info)
            else:
                QgsMessageLog.logMessage(f"DEBUG TMA: No US records found for: sito={sito}, area={area}, us={us}", "PyArchInit", Qgis.Info)
                self.lineEdit_dtzg.clear()
                        
        except Exception as e:
            # Print the error for debugging
            QgsMessageLog.logMessage(f"DEBUG TMA ERROR in on_us_changed: {str(e)}", "PyArchInit", Qgis.Warning)
            import traceback
            traceback.print_exc()
    
    def on_area_changed(self):
        """Handle area field change to update inventory."""
        self.update_inventory_field()
    
    def on_sito_changed(self):
        """Handle site field change to update inventory."""
        self.update_inventory_field()
    
    def update_inventory_field(self):
        """Update the inventory field with RA numbers from inventory materials."""
        try:
            # Clear the field first
            self.lineEdit_inventario.clear()
            
            # Get current site, area, us
            sito = self.comboBox_sito.currentText()
            area = self.comboBox_area.currentText()
            us = self.lineEdit_us.text()
            
            if not sito or not area or not us:
                return
            
            # Query inventory materials with repertato = 'Si' (RA numbers)
            search_dict = {
                'sito': f"'{sito}'",
                'area': f"'{area}'",
                'us': f"'{us}'",
                'repertato': "'Si'"
            }
            
            inventory_materials = self.DB_MANAGER.query_bool(search_dict, 'INVENTARIO_MATERIALI')
            
            if inventory_materials:
                # Extract RA numbers (n_reperto) and join with semicolon
                ra_numbers = []
                for mat in inventory_materials:
                    if hasattr(mat, 'n_reperto') and mat.n_reperto:
                        ra_numbers.append(str(mat.n_reperto))
                
                # Sort the RA numbers for better display
                ra_numbers.sort()
                
                # Update the inventory field
                if ra_numbers:
                    self.lineEdit_inventario.setText('; '.join(ra_numbers))
                    
        except Exception as e:
            # Silently fail - this is just a helper function
            pass
    
    def load_thesaurus_values(self, field_type):
        """Load thesaurus values for material fields."""
        try:
            lang = QgsSettings().value("locale/userLocale", "it")[:2]
            
            # Map field types to thesaurus categories
            # Using correct tipologia_sigla codes for tma_materiali_archeologici
            thesaurus_map = {
                'materiale': '10.4',   # Materiale
                'categoria': '10.5',   # Categoria
                'classe': '10.6',      # Classe
                'tipologia': '10.8',   # Prec. tipologica
                'definizione': '10.9', # Definizione
                'cronologia': '10.16'  # Cronologia
            }
            
            if field_type not in thesaurus_map:
                return []
            
            # Use alias table name for materials data
            search_dict = {
                'lingua': "'" + lang.upper() + "'",  # Use uppercase for language with quotes
                'nome_tabella': "'tma_materiali_table'",  # Using alias
                'tipologia_sigla': "'" + thesaurus_map[field_type] + "'"
            }
            
            thesaurus_records = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
            values = []
            
            for record in thesaurus_records:
                if hasattr(record, 'sigla_estesa') and record.sigla_estesa:
                    values.append(record.sigla_estesa)
            
            values.sort()
            return values
            
        except Exception as e:
            # Return empty list if thesaurus not available
            return []
    
    def convert_aint_to_combobox_with_thesaurus(self, lang):
        """Convert aint field from LineEdit to ComboBox with thesaurus values."""
        try:
            # Get the parent layout of the lineEdit_aint
            parent = self.lineEdit_aint.parent()
            layout = parent.layout()
            
            # Find the position of lineEdit_aint in the layout
            for i in range(layout.count()):
                item = layout.itemAt(i)
                if item and item.widget() == self.lineEdit_aint:
                    row, col, rowspan, colspan = layout.getItemPosition(i)
                    
                    # Create ComboBox
                    self.comboBox_aint = QComboBox()
                    self.comboBox_aint.setEditable(True)
                    
                    # Load thesaurus values for aint using alias table name
                    if self.DB_MANAGER and self.DB_MANAGER != "":
                        search_dict = {
                            'lingua': lang,
                            'nome_tabella': "'" + 'tma_table' + "'",  # Using alias
                            'tipologia_sigla': "'" + '10.11' + "'"
                        }
                        
                        thesaurus_records = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
                    else:
                        thesaurus_records = []
                    
                    # Add empty option
                    self.comboBox_aint.addItem("")
                    
                    # Add thesaurus values
                    for record in thesaurus_records:
                        if hasattr(record, 'sigla_estesa') and record.sigla_estesa:
                            self.comboBox_aint.addItem(record.sigla_estesa)
                    
                    # Hide the LineEdit and add ComboBox
                    self.lineEdit_aint.hide()
                    layout.addWidget(self.comboBox_aint, row, col, rowspan, colspan)
                    
                    QgsMessageLog.logMessage(f"DEBUG TMA: Converted aint to ComboBox with {self.comboBox_aint.count()} items", "PyArchInit", Qgis.Info)
                    break
                    
        except Exception as e:
            QgsMessageLog.logMessage(f"DEBUG TMA: Error converting aint field: {str(e)}", "PyArchInit", Qgis.Warning)
            # If conversion fails, keep the LineEdit
            self.comboBox_aint = None
    
    def setup_materials_table_with_thesaurus(self):
        """Setup materials table with thesaurus support using delegates."""
        from qgis.PyQt.QtWidgets import QStyledItemDelegate, QComboBox
        
        class ComboBoxDelegate(QStyledItemDelegate):
            def __init__(self, items, parent=None):
                super().__init__(parent)
                self.items = items
            
            def createEditor(self, parent, option, index):
                editor = QComboBox(parent)
                editor.addItems(self.items)
                editor.setEditable(True)  # Allow custom values
                return editor
            
            def setEditorData(self, editor, index):
                value = index.model().data(index, Qt.EditRole)
                if value in self.items:
                    editor.setCurrentText(value)
                else:
                    editor.setEditText(str(value) if value else "")
            
            def setModelData(self, editor, model, index):
                model.setData(index, editor.currentText(), Qt.EditRole)
        
        # Setup base table
        self.setup_materials_table()
        
        # Load thesaurus values for each column that needs it
        materiale_values = self.load_thesaurus_values('materiale')
        categoria_values = self.load_thesaurus_values('categoria')
        classe_values = self.load_thesaurus_values('classe')
        tipologia_values = self.load_thesaurus_values('tipologia')
        definizione_values = self.load_thesaurus_values('definizione')
        cronologia_values = self.load_thesaurus_values('cronologia')
        
        # Don't use default values - only use thesaurus values
        
        # Debug print
        QgsMessageLog.logMessage(f"DEBUG TMA THESAURUS: Materiale values: {len(materiale_values)} items", "PyArchInit", Qgis.Info)
        QgsMessageLog.logMessage(f"DEBUG TMA THESAURUS: Categoria values: {len(categoria_values)} items", "PyArchInit", Qgis.Info)
        QgsMessageLog.logMessage(f"DEBUG TMA THESAURUS: Classe values: {len(classe_values)} items", "PyArchInit", Qgis.Info)
        QgsMessageLog.logMessage(f"DEBUG TMA THESAURUS: Tipologia values: {len(tipologia_values)} items", "PyArchInit", Qgis.Info)
        QgsMessageLog.logMessage(f"DEBUG TMA THESAURUS: Definizione values: {len(definizione_values)} items", "PyArchInit", Qgis.Info)
        
        # Set delegates for columns with thesaurus support
        if materiale_values:
            self.tableWidget_materiali.setItemDelegateForColumn(0, ComboBoxDelegate(materiale_values, self.tableWidget_materiali))
            QgsMessageLog.logMessage(f"DEBUG TMA: Set delegate for Materiale column with {len(materiale_values)} values", "PyArchInit", Qgis.Info)
        if categoria_values:
            self.tableWidget_materiali.setItemDelegateForColumn(1, ComboBoxDelegate(categoria_values, self.tableWidget_materiali))
            QgsMessageLog.logMessage(f"DEBUG TMA: Set delegate for Categoria column with {len(categoria_values)} values", "PyArchInit", Qgis.Info)
        if classe_values:
            self.tableWidget_materiali.setItemDelegateForColumn(2, ComboBoxDelegate(classe_values, self.tableWidget_materiali))
            QgsMessageLog.logMessage(f"DEBUG TMA: Set delegate for Classe column with {len(classe_values)} values", "PyArchInit", Qgis.Info)
        if tipologia_values:
            self.tableWidget_materiali.setItemDelegateForColumn(3, ComboBoxDelegate(tipologia_values, self.tableWidget_materiali))
            QgsMessageLog.logMessage(f"DEBUG TMA: Set delegate for Tipologia column with {len(tipologia_values)} values", "PyArchInit", Qgis.Info)
        if definizione_values:
            self.tableWidget_materiali.setItemDelegateForColumn(4, ComboBoxDelegate(definizione_values, self.tableWidget_materiali))
            QgsMessageLog.logMessage(f"DEBUG TMA: Set delegate for Definizione column with {len(definizione_values)} values", "PyArchInit", Qgis.Info)
        if cronologia_values:
            self.tableWidget_materiali.setItemDelegateForColumn(5, ComboBoxDelegate(cronologia_values, self.tableWidget_materiali))
            QgsMessageLog.logMessage(f"DEBUG TMA: Set delegate for Cronologia column with {len(cronologia_values)} values", "PyArchInit", Qgis.Info)
    
    def addMediaTab(self):
        """Add media and map tabs to the existing tab widget."""
        # Add Media tab
        media_tab = QWidget()
        media_layout = QVBoxLayout(media_tab)
        
        # Add button layout for media management
        button_layout = QHBoxLayout()
        
        # Add tag buttons
        self.pushButton_tags_TMA = QPushButton("Aggiungi tags")
        self.pushButton_tags_TMA.clicked.connect(self.assignTags_TMA)
        button_layout.addWidget(self.pushButton_tags_TMA)
        
        self.pushButton_remove_tags = QPushButton("Rimuovi tags")
        self.pushButton_remove_tags.clicked.connect(self.removeTags_TMA)
        button_layout.addWidget(self.pushButton_remove_tags)
        
        self.pushButton_all_images = QPushButton("Vedi tutte immagini")
        self.pushButton_all_images.clicked.connect(self.viewAllImages)
        button_layout.addWidget(self.pushButton_all_images)
        
        button_layout.addStretch()
        
        media_layout.addLayout(button_layout)
        media_layout.addWidget(self.iconListWidget)
        self.tabWidget.addTab(media_tab, "Media")
        
        # Add Map tab  
        self.tabWidget.addTab(self.mapPreview, "Map preview")
    
    def loadMediaPreview(self, mode=0):
        """Load media preview for the current TMA record."""
        self.iconListWidget.clear()
        conn = Connection()
        
        thumb_path = conn.thumb_path()
        thumb_path_str = thumb_path['thumb_path']
        
        if mode == 0:
            try:
                if not self.DATA_LIST or self.REC_CORR >= len(self.DATA_LIST):
                    return
                    
                # Get current record ID
                current_id = self.DATA_LIST[self.REC_CORR].id
                
                # Query media for this TMA record
                search_dict = {
                    'id_entity': current_id,
                    'entity_type': "'TMA'"
                }
                
                media_data = self.DB_MANAGER.query_bool(search_dict, 'MEDIATOENTITY')
                
                for media in media_data:
                    # Get thumbnail data
                    thumb_search = {'media_filename': f"'{media.media_name}'"}
                    thumb_data = self.DB_MANAGER.query_bool(thumb_search, 'MEDIA_THUMB')
                    
                    if thumb_data:
                        thumb_path = thumb_data[0].filepath
                        item = QListWidgetItem(str(media.media_name))
                        item.setData(Qt.UserRole, str(media.media_name))
                        icon = QIcon(thumb_path_str + thumb_path)
                        item.setIcon(icon)
                        self.iconListWidget.addItem(item)
                        
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e), QMessageBox.Ok)
                
        elif mode == 1:
            self.iconListWidget.clear()
    
    def openWide_image(self):
        """Open selected image in full view."""
        items = self.iconListWidget.selectedItems()
        conn = Connection()
        
        thumb_resize = conn.thumb_resize()
        thumb_resize_str = thumb_resize['thumb_resize']
        
        for item in items:
            # Get the media id or filename from item data
            item_data = item.data(Qt.UserRole)
            
            # Try to get media by id first, then by filename
            if str(item_data).isdigit():
                search_dict = {'id_media': int(item_data)}
            else:
                search_dict = {'filename': f"'{item_data}'"}
                
            media_data = self.DB_MANAGER.query_bool(search_dict, 'MEDIA')
            
            if media_data:
                # Get media thumb data to find the resized image path
                media_thumb_search = {'id_media': str(media_data[0].id_media)}
                media_thumb_data = self.DB_MANAGER.query_bool(media_thumb_search, 'MEDIA_THUMB')
                
                if media_thumb_data:
                    # Use the resized image path
                    file_path = media_thumb_data[0].path_resize
                    full_path = thumb_resize_str + file_path
                    
                    # Check if it's an image
                    if file_path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff')):
                        dlg = ImageViewer(self)
                        dlg.show_image(full_path)
                        dlg.exec_()
    
    def loadMapPreview(self, mode=0):
        """Load map preview for current TMA record."""
        if not hasattr(self, 'mapPreview'):
            return
            
        if mode == 0:
            try:
                if not self.DATA_LIST or self.REC_CORR >= len(self.DATA_LIST):
                    return
                    
                # Get current record data
                current_tma = self.DATA_LIST[self.REC_CORR]
                
                # Build query for map layers based on site/area
                gidstr = f"sito = '{current_tma.sito}' AND area = '{current_tma.area}'"
                
                # Load relevant layers
                layerToSet = self.pyQGIS.loadMapPreview_new(gidstr)
                self.mapPreview.setLayers(layerToSet)
                self.mapPreview.zoomToFullExtent()
                
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e), QMessageBox.Ok)
                
        elif mode == 1:
            self.mapPreview.setLayers([])
            self.mapPreview.zoomToFullExtent()
    
    def assignTags_TMA_from_item(self, item):
        """Assign tags from a single media item to current TMA record."""
        if self.DATA_LIST and self.REC_CORR < len(self.DATA_LIST):
            current_tma = self.DATA_LIST[self.REC_CORR]
            
            # Get media ID from item data
            media_id = item.data(Qt.UserRole)
            
            if str(media_id).isdigit():
                # Search by media ID
                search_dict = {'id_media': int(media_id)}
                media_data = self.DB_MANAGER.query_bool(search_dict, 'MEDIA')
                
                if media_data:
                    self.insert_mediaToEntity_rec(
                        current_tma.id,
                        'TMA',
                        'tma_materiali_archeologici',
                        media_data[0].id_media,
                        media_data[0].filepath,
                        media_data[0].filename
                    )

    def assignTags_TMA(self):
        """Assign current TMA record as tag to selected media."""
        if not self.DATA_LIST:
            QMessageBox.warning(self, "Warning", "No TMA record loaded", QMessageBox.Ok)
            return
            
        items_selected = self.iconListWidget.selectedItems()
        if not items_selected:
            QMessageBox.warning(self, "Warning", "Select media items first", QMessageBox.Ok)
            return
            
        # Get current record data
        current_tma = self.DATA_LIST[self.REC_CORR]
        
        for item in items_selected:
            # Get media ID from item data (we store media_id in UserRole)
            media_id = item.data(Qt.UserRole)
            media_name = item.text()
            
            # Check if already tagged
            search_dict = {
                'id_entity': int(current_tma.id),
                'entity_type': 'TMA',
                'id_media': int(media_id)
            }
            
            existing = self.DB_MANAGER.query_bool(search_dict, 'MEDIATOENTITY')
            
            if not existing:
                # Create new media-entity relation
                try:
                    mediatoentity_data = self.DB_MANAGER.insert_media_to_entity_values(
                        None,  # id will be auto-generated
                        int(current_tma.id),  # id_entity
                        'TMA',  # entity_type  
                        'TMA',  # table_name
                        int(media_id),  # id_media
                        '',  # filepath (not used)
                        media_name  # media_name
                    )
                    
                    self.DB_MANAGER.insert_data_session(mediatoentity_data)
                    
                    # Update item appearance
                    item.setBackground(QColor("green"))
                    
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Error tagging media: {str(e)}", QMessageBox.Ok)
            else:
                QMessageBox.information(self, "Info", f"Media {media_name} already tagged", QMessageBox.Ok)
    
    def dropEvent(self, event):
        """Handle file drop events for media upload."""
        mimeData = event.mimeData()
        accepted_formats = ["jpg", "jpeg", "png", "tiff", "tif", "bmp", "mp4", "avi", "mov", "mkv", "flv", "obj", "stl",
                            "ply", "fbx", "3ds"]

        if mimeData.hasUrls():
            for url in mimeData.urls():
                try:
                    path = url.toLocalFile()
                    filetype = path.split(".")[-1].lower()
                    
                    if filetype in accepted_formats:
                        # Check if this is an image
                        if filetype in ["jpg", "jpeg", "png", "tiff", "tif", "bmp"]:
                            self.load_and_process_image(path)
                        else:
                            QMessageBox.warning(self, "Error", f"Unsupported file type: {filetype}", QMessageBox.Ok)
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Failed to process the file: {str(e)}", QMessageBox.Ok)
        super().dropEvent(event)

    def dragEnterEvent(self, event):
        """Accept drag events for supported file types."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def load_and_process_image(self, filepath):
        """Process dropped image file and add to media."""
        try:
            # Get connection settings
            conn = Connection()
            thumb_path = conn.thumb_path()
            thumb_resize = conn.thumb_resize()
            
            # Get filename without extension
            filename_orig = os.path.basename(filepath)
            filename, filetype = os.path.splitext(filename_orig)
            filename = filename  # filename without extension
            filetype = filetype[1:]  # remove the dot
            
            # Generate unique media ID
            media_max_num_id = self.DB_MANAGER.max_num_id('MEDIA', 'id_media')
            
            # Create unique filenames with media ID prefix
            media_filename = str(media_max_num_id) + "_" + filename + "." + filetype
            filename_thumb = str(media_max_num_id) + "_" + filename + "_thumb.png"
            filename_resize = str(media_max_num_id) + "_" + filename + ".png"
            
            # Copy original file to media directory with unique name
            dest_path = os.path.join(thumb_resize['thumb_resize'], media_filename)
            shutil.copy(filepath, dest_path)
            
            # Get media utility instances
            MU = Media_utility()
            MUR = Media_utility_resize()
            
            # Create thumbnail
            MU.resample_images(media_max_num_id, filepath, filename, 
                               thumb_path['thumb_path'], '_thumb.png')
            
            # Create resized image
            MUR.resample_images(media_max_num_id, filepath, filename,
                               thumb_resize['thumb_resize'], '.png')
            
            # Save to database
            try:
                # Build tags from current TMA record
                tags = 'TMA'
                if self.DATA_LIST and self.REC_CORR < len(self.DATA_LIST):
                    current_tma = self.DATA_LIST[self.REC_CORR]
                    tags = f"TMA - Sito: {current_tma.sito} - Area: {current_tma.area} - US: {current_tma.dscu} - Cassetta: {current_tma.cassetta}"
                
                # Insert media record
                media_data = self.DB_MANAGER.insert_media_values(
                    self.DB_MANAGER.max_num_id('MEDIA', 'id_media') + 1,
                    'image',  # mediatype
                    str(media_filename),  # filename (unique with media ID)
                    str(filetype),  # filetype
                    str(media_filename),  # filepath (same as filename for uniqueness)
                    '',  # descrizione
                    tags  # tags with TMA info
                )
                self.DB_MANAGER.insert_data_session(media_data)
                
                # Insert media thumb record
                thumb_data = self.DB_MANAGER.insert_mediathumb_values(
                    self.DB_MANAGER.max_num_id('MEDIA_THUMB', 'id_media_thumb') + 1,
                    str(media_max_num_id),
                    'image',
                    str(filename),
                    str(filename_thumb),
                    str(filetype),
                    str(filename_thumb),
                    str(filename_resize)
                )
                self.DB_MANAGER.insert_data_session(thumb_data)
                
                # Add to iconListWidget  
                item = QListWidgetItem(str(filename_orig))
                item.setData(Qt.UserRole, str(media_max_num_id))
                # Set icon using the thumbnail
                icon_path = os.path.join(str(thumb_path['thumb_path']), filename_thumb)
                icon = QIcon(icon_path)
                item.setIcon(icon)
                self.iconListWidget.addItem(item)
                
                # If we have a current TMA record, automatically tag it
                if self.DATA_LIST and self.REC_CORR < len(self.DATA_LIST):
                    self.assignTags_TMA_from_item(item)
                
                QMessageBox.information(self, "Success", f"Image {filename} added successfully!", QMessageBox.Ok)
                
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error saving to database: {str(e)}", QMessageBox.Ok)
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error processing image: {str(e)}", QMessageBox.Ok)
    
    def removeTags_TMA(self):
        """Remove tags from selected media."""
        if not self.DATA_LIST:
            QMessageBox.warning(self, "Warning", "No TMA record loaded", QMessageBox.Ok)
            return
            
        items_selected = self.iconListWidget.selectedItems()
        if not items_selected:
            QMessageBox.warning(self, "Warning", "Select media items first", QMessageBox.Ok)
            return
            
        # Get current record data
        current_tma = self.DATA_LIST[self.REC_CORR]
        
        msg = QMessageBox.question(self, "Confirm", 
                                   f"Remove tags from {len(items_selected)} selected media?", 
                                   QMessageBox.Yes | QMessageBox.No)
        
        if msg == QMessageBox.No:
            return
            
        for item in items_selected:
            # Get media ID from item data
            media_id = item.data(Qt.UserRole)
            
            # Find and delete the relation
            search_dict = {
                'id_entity': int(current_tma.id),
                'entity_type': 'TMA',
                'id_media': int(media_id)
            }
            
            existing = self.DB_MANAGER.query_bool(search_dict, 'MEDIATOENTITY')
            
            if existing:
                try:
                    for record in existing:
                        self.DB_MANAGER.delete_record_by_field('MEDIATOENTITY', 'id_mediaToEntity', record.id_mediaToEntity)
                    
                    # Update item appearance
                    item.setBackground(QColor())  # Reset background
                    
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Error removing tag: {str(e)}", QMessageBox.Ok)
                    
    def viewAllImages(self):
        """View all images in the database."""
        try:
            # Save current state
            current_state = None
            if self.DATA_LIST and self.REC_CORR < len(self.DATA_LIST):
                current_state = (self.DATA_LIST, self.REC_CORR)
            
            # Query all media
            media_list = self.DB_MANAGER.query('MEDIA')
            
            # Clear current list
            self.iconListWidget.clear()
            
            # Connection settings
            conn = Connection()
            thumb_path = conn.thumb_path()
            thumb_path_str = thumb_path['thumb_path']
            
            # Load all media
            for media in media_list:
                if media.mediatype == 'image':
                    # Build thumbnail path directly
                    thumb_filename = f"{media.id_media}_{os.path.splitext(media.filename)[0]}_thumb.png"
                    thumb_filepath = os.path.join(thumb_path_str, thumb_filename)
                    
                    if os.path.exists(thumb_filepath):
                        item = QListWidgetItem(str(media.filename))
                        item.setData(Qt.UserRole, str(media.id_media))
                        icon = QIcon(thumb_filepath)
                        item.setIcon(icon)
                        
                        # Check if tagged to current TMA
                        if self.DATA_LIST and self.REC_CORR < len(self.DATA_LIST):
                            current_tma = self.DATA_LIST[self.REC_CORR]
                            search_dict = {
                                'id_entity': int(current_tma.id),
                                'entity_type': 'TMA',
                                'id_media': int(media.id_media)
                            }
                            if self.DB_MANAGER.query_bool(search_dict, 'MEDIATOENTITY'):
                                item.setBackground(QColor("green"))
                                
                        self.iconListWidget.addItem(item)
                        
            QMessageBox.information(self, "Info", f"Loaded {self.iconListWidget.count()} images", QMessageBox.Ok)
            
            # Restore current state if saved
            if current_state:
                self.DATA_LIST, self.REC_CORR = current_state
                # Reload only TMA-specific media
                self.load_tma_media()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error loading images: {str(e)}", QMessageBox.Ok)
    
    def insert_mediaToEntity_rec(self, id_entity, entity_type, table_name, id_media, filepath, media_name):
        """Insert record into MEDIATOENTITY table."""
        try:
            data = self.DB_MANAGER.insert_media2entity_values(
                self.DB_MANAGER.max_num_id('MEDIATOENTITY', 'id_mediaToEntity') + 1,
                int(id_entity),        # 1 - id_entity
                str(entity_type),      # 2 - entity_type
                str(table_name),       # 3 - table_name
                int(id_media),         # 4 - id_media
                str(filepath),         # 5 - filepath
                str(media_name))       # 6 - media_name
            try:
                self.DB_MANAGER.insert_data_session(data)
                return 1
            except Exception as e:
                e_str = str(e)
                if e_str.__contains__("Integrity"):
                    msg = "Media to entity association already present in database"
                    QMessageBox.warning(self, "Warning", msg, QMessageBox.Ok)
                else:
                    QMessageBox.critical(self, "Error", str(e), QMessageBox.Ok)
                return 0
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Database error: {str(e)}", QMessageBox.Ok)
    
    def on_pushButton_print_pressed(self):
        """Handle print button click - show dialog to choose print type."""
        # Reset filter values
        if hasattr(self, 'filter_materiale_value'):
            delattr(self, 'filter_materiale_value')
        if hasattr(self, 'filter_categoria_value'):
            delattr(self, 'filter_categoria_value')
            
        # Create dialog for print options
        dialog = QDialog(self)
        dialog.setWindowTitle("Opzioni di stampa TMA")
        dialog.resize(400, 300)
        
        layout = QVBoxLayout(dialog)
        
        # Title
        title = QLabel("<h3>Seleziona il tipo di stampa</h3>")
        layout.addWidget(title)
        
        # Radio buttons for print type
        self.radio_single = QRadioButton("Stampa scheda singola (record corrente)")
        self.radio_single.setChecked(True)
        layout.addWidget(self.radio_single)
        
        self.radio_list = QRadioButton("Stampa lista filtrata")
        layout.addWidget(self.radio_list)
        
        # Filters group (enabled only when list is selected)
        filters_group = QGroupBox("Filtri per lista")
        filters_layout = QVBoxLayout()
        
        self.check_filter_cassetta = QCheckBox("Filtra per cassetta corrente")
        self.check_filter_us = QCheckBox("Filtra per US corrente")
        self.check_filter_area = QCheckBox("Filtra per area corrente")
        self.check_filter_sito = QCheckBox("Filtra per sito corrente")
        self.check_filter_materiale = QCheckBox("Filtra per materiale")
        self.check_filter_categoria = QCheckBox("Filtra per categoria")
        
        filters_layout.addWidget(self.check_filter_cassetta)
        filters_layout.addWidget(self.check_filter_us)
        filters_layout.addWidget(self.check_filter_area)
        filters_layout.addWidget(self.check_filter_sito)
        filters_layout.addWidget(self.check_filter_materiale)
        filters_layout.addWidget(self.check_filter_categoria)
        
        filters_group.setLayout(filters_layout)
        layout.addWidget(filters_group)
        
        # Enable/disable filters based on radio selection
        def toggle_filters():
            enabled = self.radio_list.isChecked()
            filters_group.setEnabled(enabled)
            
        self.radio_single.toggled.connect(toggle_filters)
        toggle_filters()
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        # Execute dialog
        if dialog.exec_() == QDialog.Accepted:
            if self.radio_single.isChecked():
                self.print_single_tma()
            else:
                self.print_tma_list()
    
    def print_single_tma(self):
        """Print single TMA record."""
        # Simply call the existing export method
        self.on_pushButton_export_pdf_pressed()
    
    def print_tma_list(self):
        """Print filtered TMA list."""
        # Import PDF generator
        from ..modules.utility.pyarchinit_exp_Tmasheet_pdf import generate_tma_pdf
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, PageBreak
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet
        
        try:
            # Build search filters
            search_dict = {}
            
            if self.check_filter_sito.isChecked() and self.comboBox_sito.currentText():
                search_dict['sito'] = self.comboBox_sito.currentText()
                
            if self.check_filter_area.isChecked() and self.comboBox_area.currentText():
                search_dict['area'] = self.comboBox_area.currentText()
                
            if self.check_filter_us.isChecked() and self.lineEdit_us.text():
                search_dict['dscu'] = self.lineEdit_us.text()
                
            if self.check_filter_cassetta.isChecked() and self.lineEdit_cassetta.text():
                search_dict['cassetta'] = self.lineEdit_cassetta.text()
            
            # Query TMA records
            if search_dict:
                tma_list = self.DB_MANAGER.query_bool(search_dict, 'TMA')
            else:
                tma_list = self.DB_MANAGER.query('TMA')
            
            if not tma_list:
                QMessageBox.warning(self, "Attenzione", "Nessun record trovato con i filtri specificati", QMessageBox.Ok)
                return
            
            # Prepare data for list
            data_list = []
            
            for tma in tma_list:
                # Get materials for this TMA
                materials = self.DB_MANAGER.query_bool({'id_tma': int(tma.id)}, 'TMA_MATERIALI')
                
                # Process each material or create single row if no materials
                if materials:
                    for mat in materials:
                        row_data = [
                            str(tma.sito),
                            str(tma.area),
                            str(tma.dscu) if tma.dscu else '',
                            str(tma.cassetta),
                            str(mat.macc) if mat.macc else '',  # Categoria
                            str(mat.macl) if mat.macl else '',  # Classe
                            str(mat.macd) if mat.macd else '',  # Definizione
                            str(mat.macq) if mat.macq else '',  # Quantità
                            str(mat.peso) if mat.peso else ''   # Peso
                        ]
                        
                        # Apply material/category filters if selected
                        include_row = True
                        
                        if self.check_filter_materiale.isChecked():
                            # Ask for material filter value if not set
                            if not hasattr(self, 'filter_materiale_value'):
                                text, ok = QInputDialog.getText(self, "Filtro Materiale", "Inserisci il materiale da filtrare:")
                                if ok and text:
                                    self.filter_materiale_value = text.lower()
                                else:
                                    self.filter_materiale_value = None
                            
                            if self.filter_materiale_value:
                                # Check if material matches (partial match)
                                mat_val = str(mat.macc).lower() if mat.macc else ''
                                if self.filter_materiale_value not in mat_val:
                                    include_row = False
                        
                        if self.check_filter_categoria.isChecked() and include_row:
                            # Ask for category filter value if not set
                            if not hasattr(self, 'filter_categoria_value'):
                                text, ok = QInputDialog.getText(self, "Filtro Categoria", "Inserisci la categoria da filtrare:")
                                if ok and text:
                                    self.filter_categoria_value = text.lower()
                                else:
                                    self.filter_categoria_value = None
                            
                            if self.filter_categoria_value:
                                # Check if category matches (partial match)
                                cat_val = str(mat.macc).lower() if mat.macc else ''
                                if self.filter_categoria_value not in cat_val:
                                    include_row = False
                        
                        if include_row:
                            data_list.append(row_data)
                else:
                    # Add TMA without materials
                    row_data = [
                        str(tma.sito),
                        str(tma.area),
                        str(tma.dscu) if tma.dscu else '',
                        str(tma.cassetta),
                        '', '', '', '', ''  # Empty material fields
                    ]
                    data_list.append(row_data)
            
            # Sort by cassetta, area, US
            data_list.sort(key=lambda x: (x[0], x[1], x[2], x[3]))
            
            # Create PDF
            HOME = os.environ['PYARCHINIT_HOME']
            PDF_path = os.path.join(HOME, "pyarchinit_PDF_folder")
            filename = f"Lista_TMA_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = os.path.join(PDF_path, filename)
            
            doc = SimpleDocTemplate(filepath, pagesize=landscape(A4))
            elements = []
            styles = getSampleStyleSheet()
            
            # Title
            title = Paragraph("<b>LISTA TABELLA MATERIALI ARCHEOLOGICI (TMA)</b>", styles['Title'])
            elements.append(title)
            elements.append(Paragraph(f"Data: {datetime.datetime.now().strftime('%d/%m/%Y')}", styles['Normal']))
            elements.append(Paragraph("<br/><br/>", styles['Normal']))
            
            # Create table with headers
            headers = ['Sito', 'Area', 'US', 'Cassetta', 'Categoria', 'Classe', 'Definizione', 'Quantità', 'Peso']
            table_data = [headers] + data_list
            
            # Create table
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                # Alternate row colors
                *[('BACKGROUND', (0, i), (-1, i), colors.white if i % 2 == 0 else colors.lightgrey) 
                  for i in range(1, len(table_data))],
            ]))
            
            elements.append(table)
            
            # Build PDF
            doc.build(elements)
            
            QMessageBox.information(self, "Esportazione completata", 
                                    f"Lista TMA esportata in:\n{filepath}\n\nTotale record: {len(data_list)}", 
                                    QMessageBox.Ok)
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore nella generazione del PDF: {str(e)}", QMessageBox.Ok)
