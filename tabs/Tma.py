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
from sqlalchemy import text

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
from ..modules.utility.pyarchinit_tma_label_pdf import TMALabelPDF

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
        "Settore": 'settore',
        "Localita": 'localita',
        "Inventario": 'inventario',
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
        'localita',
        'settore',
        'inventario',
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

        self.setupUi(self)
        self.currentLayerId = None

        # Flag to track if materials have been loaded for current record
        self.materials_loaded = False

        # Track deleted material IDs
        self.deleted_material_ids = set()

        # Flag to prevent event handlers from clearing comboboxes during data loading
        self.loading_data = False

        # Flag to track if combobox lists have been loaded
        self.lists_loaded = False

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
        #self.mapPreview = QgsMapCanvas(self)
        #self.mapPreview.setCanvasColor(QColor(225, 225, 225))
        
        # Add tabs for media and map
        self.addMediaTab()
        


        self.customize_GUI()

        self.set_sito()
        self.msg_sito()
        try:
            self.on_pushButton_connect_pressed()
        except Exception as e:
            QMessageBox.warning(self, "Connection System", str(e), QMessageBox.Ok)
            # SIGNALS & SLOTS Functions


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
        
        # Connect materials table buttons - disconnect first to avoid duplicates
        try:
            self.pushButton_add_materiale.clicked.disconnect()
        except:
            pass  # No connections to disconnect
        try:
            self.pushButton_remove_materiale.clicked.disconnect()
        except:
            pass  # No connections to disconnect
            
        self.pushButton_add_materiale.clicked.connect(self.on_pushButton_add_materiale_pressed)
        self.pushButton_remove_materiale.clicked.connect(self.on_pushButton_remove_materiale_pressed)
        
        # Initialize materials table basic structure
        self.setup_materials_table()
        self.current_material_index = -1
        self.materials_data = []
        
        # Thesaurus loading will be done in charge_list method when DB is ready
        
        # Connect fields to auto-update chronology and inventory
        # Moved to fill_fields to avoid multiple connections
        # self.lineEdit_us.textChanged.connect(self.on_us_changed)
        self.comboBox_area.currentIndexChanged.connect(self.on_area_changed)
        self.comboBox_sito.currentIndexChanged.connect(self.on_sito_changed)
        
        # Connect hierarchical filters for localita->area->settore
        self.comboBox_localita.currentIndexChanged.connect(self.on_localita_changed)
        
        
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
        # self.pushButton_open_dir.clicked.connect(self.on_pushButton_open_dir_pressed)
        #self.toolButtonGis.clicked.connect(self.on_toolButtonGis_toggled)
        # self.pushButton_import.clicked.connect(self.on_pushButton_import_pressed)
        # #self.pushButton_export_ica.clicked.connect(self.on_pushButton_export_pdf_pressed)
        # self.pushButton_export_pdf.clicked.connect(self.on_pushButton_export_tma_pdf_pressed)
        # self.pushButton_export_labels.clicked.connect(self.on_pushButton_export_labels_pressed)

        # Automatically connect to DB when the tab is opened
        # This ensures all fields are properly loaded including area and settore
        try:
            self.on_pushButton_connect_pressed()
        except Exception as e:
            QgsMessageLog.logMessage(f"TMA: Auto-connect on init: {str(e)}", "PyArchInit", Qgis.Warning)

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
            if self.DATA_LIST:
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                self.BROWSE_STATUS = 'b'
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.label_sort.setText(self.SORTED_ITEMS["n"])
                self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                # First call fill_fields to set rec_num, then charge_list
                # This ensures charge_list can properly save and restore values
                self.fill_fields(0)  # Pass index 0 explicitly for first record
                self.iconListWidget.update()
            else:
                if self.L=='it':
                    QMessageBox.warning(self,"BENVENUTO", "Benvenuto in pyArchInit " + self.NOME_SCHEDA + ". Il database e' vuoto. Premi 'Ok' e buon lavoro!",
                                        QMessageBox.Ok)
                elif self.L=='de':
                    QMessageBox.warning(self,"WILLKOMMEN","WILLKOMMEN in pyArchInit" + "SE-MSE formular"+ ". Die Datenbank ist leer. Tippe 'Ok' und aufgehts!",
                                        QMessageBox.Ok)
                else:
                    QMessageBox.warning(self,"WELCOME", "Welcome in pyArchInit" + "Samples SU-WSU" + ". The DB is empty. Push 'Ok' and Good Work!",
                                        QMessageBox.Ok)
                self.charge_list()
                self.lists_loaded = True  # Mark lists as loaded
                self.BROWSE_STATUS = 'x'
                self.setComboBoxEnable(["self.comboBox_area"], "True")
                self.setComboBoxEnable(["self.lineEdit_us"], "True")
                self.on_pushButton_new_rec_pressed()
                self.iconListWidget.update()
        except Exception as e:
            e = str(e)
            if e.find("no such table"):
                if self.L=='it':
                    msg = "La connessione e' fallita {}. " \
                          "E' NECESSARIO RIAVVIARE QGIS oppure rilevato bug! Segnalarlo allo sviluppatore".format(str(e))
                    self.iface.messageBar().pushMessage(self.tr(msg), Qgis.Warning, 0)

                elif self.L=='de':
                    msg = "Verbindungsfehler {}. " \
                          " QGIS neustarten oder es wurde ein bug gefunden! Fehler einsenden".format(str(e))
                    self.iface.messageBar().pushMessage(self.tr(msg), Qgis.Warning, 0)
                else:
                    msg = "The connection failed {}. " \
                          "You MUST RESTART QGIS or bug detected! Report it to the developer".format(str(e))
            else:
                if self.L=='it':
                    msg = "Attenzione rilevato bug! Segnalarlo allo sviluppatore. Errore: ".format(str(e))
                    self.iface.messageBar().pushMessage(self.tr(msg), Qgis.Warning, 0)
                elif self.L=='de':
                    msg = "ACHTUNG. Es wurde ein bug gefunden! Fehler einsenden: ".format(str(e))
                    self.iface.messageBar().pushMessage(self.tr(msg), Qgis.Warning, 0)
                else:
                    msg = "Warning bug detected! Report it to the developer. Error: ".format(str(e))
                    self.iface.messageBar().pushMessage(self.tr(msg), Qgis.Warning, 0)

    def check_and_update_schema(self):
        """Check and update database schema if needed for both SQLite and PostgreSQL."""
        try:
            conn = self.DB_MANAGER.engine.raw_connection()
            cursor = conn.cursor()
            
            needs_update = False
            
            if self.DB_SERVER == "sqlite":
                # SQLite: Check columns using PRAGMA
                cursor.execute("PRAGMA table_info(tma_materiali_archeologici)")
                columns = cursor.fetchall()
                column_names = [col[1] for col in columns]
                
                
                if 'settore' not in column_names:
                    cursor.execute("ALTER TABLE tma_materiali_archeologici ADD COLUMN settore TEXT")
                    needs_update = True
                    QgsMessageLog.logMessage("Added 'settore' column to TMA table", "PyArchInit", Qgis.Info)
                    
            else:  # PostgreSQL
                # PostgreSQL: Check columns using information_schema
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'tma_materiali_archeologici'
                    AND column_name = 'settore'
                """)
                existing_columns = [row[0] for row in cursor.fetchall()]
                
                
                if 'settore' not in existing_columns:
                    cursor.execute("ALTER TABLE tma_materiali_archeologici ADD COLUMN settore TEXT")
                    needs_update = True
                    QgsMessageLog.logMessage("Added 'settore' column to TMA table", "PyArchInit", Qgis.Info)
            
            if needs_update:
                conn.commit()
                if self.L == 'it':
                    QMessageBox.information(self, "Database aggiornato", 
                                          "La tabella TMA è stata aggiornata con i nuovi campi località e settore.",
                                          QMessageBox.Ok)
                else:
                    QMessageBox.information(self, "Database updated", 
                                          "The TMA table has been updated with new locality and sector fields.",
                                          QMessageBox.Ok)
            
            cursor.close()
            
        except Exception as e:
            QgsMessageLog.logMessage(f"Error checking/updating schema: {str(e)}", "PyArchInit", Qgis.Warning)

    def charge_list(self):
        """Load combobox lists."""
        # Store current values before clearing comboboxes
        # This fixes the bug where first record shows wrong values
        current_values = {}
        # Use REC_CORR as the index, or rec_num if it's defined
        rec_index = self.REC_CORR if hasattr(self, 'REC_CORR') else 0
        if hasattr(self, 'rec_num'):
            rec_index = self.rec_num

        if self.DATA_LIST and rec_index < len(self.DATA_LIST):
            current_record = self.DATA_LIST[rec_index]
            current_values = {
                'sito': str(current_record.sito) if hasattr(current_record, 'sito') else "",
                'area': str(current_record.area) if hasattr(current_record, 'area') else "",
                'localita': str(current_record.localita) if hasattr(current_record, 'localita') else "",
                'settore': str(current_record.settore) if hasattr(current_record, 'settore') else "",
                'ldct': str(current_record.ldct) if hasattr(current_record, 'ldct') else "",
                'ldcn': str(current_record.ldcn) if hasattr(current_record, 'ldcn') else "",
                'scan': str(current_record.scan) if hasattr(current_record, 'scan') else "",
                'aint': str(current_record.aint) if hasattr(current_record, 'aint') else "",
                'dtzg': str(current_record.dtzg) if hasattr(current_record, 'dtzg') else "",
            }

        # Get language setting following Tomba.py pattern
        l = QgsSettings().value("locale/userLocale", QVariant)
        lang = ""
        for key, values in self.LANG.items():
            if values.__contains__(l):
                lang = str(key)
        lang = "'" + lang + "'"

        # Setup materials table with thesaurus support now that DB is ready
        if hasattr(self, 'DB_MANAGER') and self.DB_MANAGER and self.DB_MANAGER != "":
            self.setup_materials_table_with_thesaurus()
            self.setup_documentation_delegates()

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
        # Restore saved value
        if 'sito' in current_values and current_values['sito']:
            self.comboBox_sito.setEditText(current_values['sito'])

        # lista area from thesaurus
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'TMA materiali archeologici' + "'",
            'tipologia_sigla': "'" + '10.7' + "'"
        }
        area_vl_thesaurus = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        area_vl = []
        for s in area_vl_thesaurus:
            area_vl.append(str(s.sigla_estesa))
        try:
            area_vl.remove('')
        except Exception as e:
            if str(e) == "list.remove(x): x not in list":
                pass
            else:
                if self.L=='it':
                    QMessageBox.warning(self, "Messaggio", "Sistema di aggiornamento lista area: " + str(e), QMessageBox.Ok)
                elif self.L=='en':
                    QMessageBox.warning(self, "Message", "Area list update system: " + str(e), QMessageBox.Ok)
                elif self.L=='de':
                    QMessageBox.warning(self, "Nachricht", "Aktualisierungssystem für die Area: " + str(e), QMessageBox.Ok)
                else:
                    pass

        self.comboBox_area.clear()
        area_vl.sort()
        self.comboBox_area.addItems(area_vl)
        # Don't restore area here - it will be set at the end of fill_fields
        
        # Load thesaurus values for TMA fields
        # 10.1 - Denominazione collocazione
        search_dict_ldcn = {
            'nome_tabella': "'" + 'TMA materiali archeologici' + "'",
            'tipologia_sigla': "'" + '10.1' + "'"  # Correct code for denominazione collocazione
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
        # Restore saved value
        if 'ldcn' in current_values and current_values['ldcn']:
            self.comboBox_ldcn.setEditText(current_values['ldcn'])
        
        # 10.2 - Tipologia Collocazione (ldct)
        search_dict_ldct = {

            'nome_tabella': "'" + 'TMA materiali archeologici' + "'",
            'tipologia_sigla': "'" + '10.2' + "'"
        }
        ldct_res = self.DB_MANAGER.query_bool(search_dict_ldct, 'PYARCHINIT_THESAURUS_SIGLE')
        self.comboBox_ldct.clear()
        ldct_dict = {}
        for i in range(len(ldct_res)):
            sigla_estesa = str(ldct_res[i].sigla_estesa)
            sigla = str(ldct_res[i].sigla)
            ldct_dict[sigla_estesa] = sigla
        
        # Sort and add items with tooltips
        for sigla_estesa in sorted(ldct_dict.keys()):
            self.comboBox_ldct.addItem(sigla_estesa)
            index = self.comboBox_ldct.count() - 1
            self.comboBox_ldct.setItemData(index, f"Codice: {ldct_dict[sigla_estesa]}", Qt.ToolTipRole)
        # Restore saved value
        if 'ldct' in current_values and current_values['ldct']:
            self.comboBox_ldct.setEditText(current_values['ldct'])
        
        # Saggio and Vano/Locus are now LineEdit fields - no thesaurus loading needed
        
        # 10.3 - Località
        search_dict_localita = {
            'nome_tabella': "'" + 'TMA materiali archeologici' + "'",
            'tipologia_sigla': "'" + '10.3' + "'"
        }
        localita_res = self.DB_MANAGER.query_bool(search_dict_localita, 'PYARCHINIT_THESAURUS_SIGLE')
        self.comboBox_localita.clear()
        localita_dict = {}
        for i in range(len(localita_res)):
            sigla_estesa = str(localita_res[i].sigla_estesa)
            sigla = str(localita_res[i].sigla)
            localita_dict[sigla_estesa] = sigla
        
        # Sort and add items with tooltips
        for sigla_estesa in sorted(localita_dict.keys()):
            self.comboBox_localita.addItem(sigla_estesa)
            index = self.comboBox_localita.count() - 1
            self.comboBox_localita.setItemData(index, f"Codice: {localita_dict[sigla_estesa]}", Qt.ToolTipRole)
        # Restore saved value
        if 'localita' in current_values and current_values['localita']:
            self.comboBox_localita.setEditText(current_values['localita'])
            
        # 10.15 - Settore
        search_dict_settore = {
            'nome_tabella': "'" + 'TMA materiali archeologici' + "'",
            'tipologia_sigla': "'" + '10.15' + "'"
        }
        settore_res = self.DB_MANAGER.query_bool(search_dict_settore, 'PYARCHINIT_THESAURUS_SIGLE')
        self.comboBox_settore.clear()
        settore_dict = {}
        for i in range(len(settore_res)):
            sigla_estesa = str(settore_res[i].sigla_estesa)
            sigla = str(settore_res[i].sigla)
            settore_dict[sigla_estesa] = sigla
        
        # Sort and add items with tooltips
        for sigla_estesa in sorted(settore_dict.keys()):
            self.comboBox_settore.addItem(sigla_estesa)
            index = self.comboBox_settore.count() - 1
            self.comboBox_settore.setItemData(index, f"Codice: {settore_dict[sigla_estesa]}", Qt.ToolTipRole)
        # Don't restore settore here - it will be set at the end of fill_fields
        
        # 10.5 - Denominazione Scavo
        search_dict_scan = {
            'nome_tabella': "'" + 'TMA materiali archeologici' + "'",
            'tipologia_sigla': "'" + '10.5' + "'"
        }
        scan_res = self.DB_MANAGER.query_bool(search_dict_scan, 'PYARCHINIT_THESAURUS_SIGLE')
        self.comboBox_scan.clear()
        scan_dict = {}
        for i in range(len(scan_res)):
            sigla_estesa = str(scan_res[i].sigla_estesa)
            sigla = str(scan_res[i].sigla)
            scan_dict[sigla_estesa] = sigla
        
        # Sort and add items with tooltips
        for sigla_estesa in sorted(scan_dict.keys()):
            self.comboBox_scan.addItem(sigla_estesa)
            index = self.comboBox_scan.count() - 1
            self.comboBox_scan.setItemData(index, f"Codice: {scan_dict[sigla_estesa]}", Qt.ToolTipRole)
        # Restore saved value
        if 'scan' in current_values and current_values['scan']:
            self.comboBox_scan.setEditText(current_values['scan'])
        
        # 10.4 - Fascia cronologica (dtzg)
        search_dict_dtzg = {

            'nome_tabella': "'" + 'TMA materiali archeologici' + "'",
            'tipologia_sigla': "'" + '10.4' + "'"
        }
        dtzg_res = self.DB_MANAGER.query_bool(search_dict_dtzg, 'PYARCHINIT_THESAURUS_SIGLE')
        self.comboBox_dtzg.clear()
        dtzg_dict = {}
        for i in range(len(dtzg_res)):
            sigla_estesa = str(dtzg_res[i].sigla_estesa)
            sigla = str(dtzg_res[i].sigla)
            dtzg_dict[sigla_estesa] = sigla
        
        # Sort and add items with tooltips
        for sigla_estesa in sorted(dtzg_dict.keys()):
            self.comboBox_dtzg.addItem(sigla_estesa)
            index = self.comboBox_dtzg.count() - 1
            self.comboBox_dtzg.setItemData(index, f"Codice: {dtzg_dict[sigla_estesa]}", Qt.ToolTipRole)
        
        # Restore saved value
        if 'dtzg' in current_values and current_values['dtzg']:
            self.comboBox_dtzg.setEditText(current_values['dtzg'])
        
        # 10.6 - Tipologia Acquisizione (aint)
        search_dict_aint = {

            'nome_tabella': "'" + 'TMA materiali archeologici' + "'",
            'tipologia_sigla': "'" + '10.6' + "'"
        }
        aint_res = self.DB_MANAGER.query_bool(search_dict_aint, 'PYARCHINIT_THESAURUS_SIGLE')
        self.comboBox_aint.clear()
        aint_dict = {}
        for i in range(len(aint_res)):
            sigla_estesa = str(aint_res[i].sigla_estesa)
            sigla = str(aint_res[i].sigla)
            aint_dict[sigla_estesa] = sigla
        
        # Sort and add items with tooltips
        for sigla_estesa in sorted(aint_dict.keys()):
            self.comboBox_aint.addItem(sigla_estesa)
            index = self.comboBox_aint.count() - 1
            self.comboBox_aint.setItemData(index, f"Codice: {aint_dict[sigla_estesa]}", Qt.ToolTipRole)
        # Restore saved value
        if 'aint' in current_values and current_values['aint']:
            self.comboBox_aint.setEditText(current_values['aint'])
        
        # Setup documentation delegates with thesaurus values
        self.setup_documentation_delegates()
        
        # Note: Materials are handled through separate TMA_MATERIALI table in database

    def charge_records(self):
        QgsMessageLog.logMessage("DEBUG TMA charge_records: Called", "PyArchInit", Qgis.Info)
        
        # First check how many records are in DB before loading
        try:
            from sqlalchemy import text
            from sqlalchemy.orm import sessionmaker
            Session = sessionmaker(bind=self.DB_MANAGER.engine)
            session = Session()
            
            # Count records before loading
            count_result = session.execute(text("SELECT COUNT(*) FROM tma_materiali_archeologici"))
            count_before = count_result.scalar()
            QgsMessageLog.logMessage(f"DEBUG TMA charge_records: Records in DB before loading: {count_before}", "PyArchInit", Qgis.Info)
            
            session.close()
        except Exception as e:
            QgsMessageLog.logMessage(f"DEBUG TMA charge_records: Error counting records: {e}", "PyArchInit", Qgis.Warning)
        
        QgsMessageLog.logMessage("DEBUG TMA: Clearing DATA_LIST in charge_records", "PyArchInit", Qgis.Info)
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
        
        QgsMessageLog.logMessage(f"DEBUG TMA charge_records: Loaded {len(self.DATA_LIST)} records into DATA_LIST", "PyArchInit", Qgis.Info)
        
        # Check records after loading
        try:
            Session = sessionmaker(bind=self.DB_MANAGER.engine)
            session = Session()
            
            count_result = session.execute(text("SELECT COUNT(*) FROM tma_materiali_archeologici"))
            count_after = count_result.scalar()
            QgsMessageLog.logMessage(f"DEBUG TMA charge_records: Records in DB after loading: {count_after}", "PyArchInit", Qgis.Info)
            
            if count_after < count_before:
                QgsMessageLog.logMessage(f"WARNING: Records were deleted during charge_records! Before: {count_before}, After: {count_after}", "PyArchInit", Qgis.Critical)
            
            session.close()
        except Exception as e:
            QgsMessageLog.logMessage(f"DEBUG TMA charge_records: Error counting records after: {e}", "PyArchInit", Qgis.Warning)
        
        # Refresh materials table delegates with thesaurus values when DB is connected
        self.setup_materials_table_with_thesaurus()

    def datestrfdate(self):
        """Convert date fields to string format."""
        from datetime import date
        now = date.today()
        today = now.strftime("%d-%m-%Y")
        return today

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
                res = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
                self.DATA_LIST = list(res)  # Convert the result to a list directly
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
                    self.setComboBoxEnable(["self.comboBox_sito"], "False")
                    self.setComboBoxEditable(["self.comboBox_sito"], 0)
                else:
                    # No records for this site yet
                    if self.L == 'it':
                        QMessageBox.information(self, "Attenzione", 
                                                f"Non ci sono record TMA per il sito: '{sito_set_str}'. "
                                                "Puoi crearne di nuovi o cambiare sito.",
                                                QMessageBox.Ok)
                    else:
                        QMessageBox.information(self, "Warning", 
                                                f"There are no TMA records for site: '{sito_set_str}'. "
                                                "You can create new ones or change site.",
                                                QMessageBox.Ok)
            else:
                self.setComboBoxEnable(["self.comboBox_sito"], "True")
                self.setComboBoxEditable(["self.comboBox_sito"], 1)
        except Exception as e:
            QgsMessageLog.logMessage(f"Error in set_sito: {str(e)}", "PyArchInit", Qgis.Warning)

    def fill_fields(self, n=0):
        self.rec_num = n
        try:
            # Set flag to prevent event handlers from clearing comboboxes
            self.loading_data = True

            # Ensure combobox lists are loaded with current record values
            # This is especially important for the first record
            if not hasattr(self, 'lists_loaded') or not self.lists_loaded:
                self.charge_list()
                self.lists_loaded = True

            # Get area and settore values
            area_value = str(self.DATA_LIST[self.rec_num].area)
            settore_value = str(self.DATA_LIST[self.rec_num].settore)

            # Block all signals to prevent event handlers from firing
            self.comboBox_sito.blockSignals(True)
            self.comboBox_localita.blockSignals(True)
            self.comboBox_area.blockSignals(True)
            self.comboBox_settore.blockSignals(True)

            # Set all combobox values while signals are blocked
            self.comboBox_sito.setEditText(str(self.DATA_LIST[self.rec_num].sito))
            self.comboBox_localita.setEditText(str(self.DATA_LIST[self.rec_num].localita))

            # Set area value
            if area_value and area_value != 'None':
                self.comboBox_area.setEditText(area_value)
            else:
                self.comboBox_area.setEditText("")

            # Set settore value - explicitly handle empty/None values
            if settore_value and settore_value != 'None' and settore_value.strip():
                self.comboBox_settore.setEditText(settore_value)
            else:
                # Force the combobox to show empty text even if it has items
                self.comboBox_settore.setEditText("")
                self.comboBox_settore.setCurrentIndex(-1)  # Deselect any item

            # Re-enable signals
            self.comboBox_sito.blockSignals(False)
            self.comboBox_localita.blockSignals(False)
            self.comboBox_area.blockSignals(False)
            self.comboBox_settore.blockSignals(False)

            # Set other fields
            self.lineEdit_inventario.setText(str(self.DATA_LIST[self.rec_num].inventario))
            self.lineEdit_materiale.setText(str(self.DATA_LIST[self.rec_num].ogtm))
            self.comboBox_ldct.setEditText(str(self.DATA_LIST[self.rec_num].ldct))
            self.comboBox_ldcn.setEditText(str(self.DATA_LIST[self.rec_num].ldcn))
            self.lineEdit_vecchia_collocazione.setText(str(self.DATA_LIST[self.rec_num].vecchia_collocazione))
            self.lineEdit_cassetta.setText(str(self.DATA_LIST[self.rec_num].cassetta))
            self.comboBox_scan.setEditText(str(self.DATA_LIST[self.rec_num].scan))
            self.lineEdit_saggio.setText(str(self.DATA_LIST[self.rec_num].saggio))
            self.lineEdit_vano_locus.setText(str(self.DATA_LIST[self.rec_num].vano_locus))
            self.lineEdit_dscd.setText(str(self.DATA_LIST[self.rec_num].dscd))
            self.lineEdit_us.setText(str(self.DATA_LIST[self.rec_num].dscu))
            self.lineEdit_rcgd.setText(str(self.DATA_LIST[self.rec_num].rcgd))
            self.textEdit_rcgz.setText(str(self.DATA_LIST[self.rec_num].rcgz))
            self.comboBox_aint.setEditText(str(self.DATA_LIST[self.rec_num].aint))
            self.lineEdit_aind.setText(str(self.DATA_LIST[self.rec_num].aind))
            self.comboBox_dtzg.setEditText(str(self.DATA_LIST[self.rec_num].dtzg))
            self.textEdit_deso.setText(str(self.DATA_LIST[self.rec_num].deso))
            
            # Load materials data for this record
            self.load_materials_table()
            
            # Documentation tables
            if self.DATA_LIST[self.rec_num].ftap:
                self.tableInsertData("self.tableWidget_foto", self.DATA_LIST[self.rec_num].ftap)
            if self.DATA_LIST[self.rec_num].drat:
                self.tableInsertData("self.tableWidget_disegno", self.DATA_LIST[self.rec_num].drat)

            # Clear loading flag after all fields are filled
            self.loading_data = False

        except Exception as e:
            # Make sure to clear the flag even if there's an error
            self.loading_data = False
            QMessageBox.warning(self, "Error", str(e), QMessageBox.Ok)

    def tableInsertData(self, table_name, data):
        """
        Insert data into a table widget
        :param table_name: name of the table widget
        :param data: data to insert (list of lists or list of dictionaries)
        """
        table_widget = eval(table_name)
        table_widget.setRowCount(0)

        # Check if data is a dictionary
        if isinstance(data, dict):
            # Convert dictionary to list of lists for insertion
            data_list = []
            for key, value in data.items():
                data_list.append([key, value])
            data = data_list

        # Check if data is a list
        if isinstance(data, list):
            # For lists of dictionaries, convert to list of lists
            if data and isinstance(data[0], dict):
                new_data = []
                for item in data:
                    row_data = []
                    for key, value in item.items():
                        row_data.append(value)
                    new_data.append(row_data)
                data = new_data

            # Insert data into table
            for row_data in data:
                row_position = table_widget.rowCount()
                table_widget.insertRow(row_position)

                for col, cell_data in enumerate(row_data):
                    if cell_data is not None:
                        cell_item = QTableWidgetItem(str(cell_data))
                        table_widget.setItem(row_position, col, cell_item)

        # Add an empty row at the end for new entries
        self.insert_new_row(table_name)

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
        
        # Update inventory field with current data from inventory materials
        self.update_inventory_field()

    def load_tma_media(self):
        """Load media associated with current TMA record."""
        # Clear existing items
        self.iconListWidget.clear()
        
        if self.DATA_LIST and self.REC_CORR < len(self.DATA_LIST):
            current_tma = self.DATA_LIST[self.REC_CORR]
            
            # Search for media associated with this TMA
            search_dict = {
                'id_entity': int(current_tma.id),
                'entity_type': "'" + 'TMA' + "'"
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
        # Solo aggiornare le label, non le variabili interne
        self.label_rec_tot.setText(str(t))
        self.label_rec_corrente.setText(str(c))


    def records_equal_check(self):
        try:
            #self.set_sito()
            self.set_LIST_REC_TEMP()
            self.set_LIST_REC_CORR()

            # Debug: Compare field by field to find differences
            from qgis.core import QgsMessageLog, Qgis
            differences = []
            for i, field_name in enumerate(self.TABLE_FIELDS):
                if i < len(self.DATA_LIST_REC_CORR) and i < len(self.DATA_LIST_REC_TEMP):
                    if self.DATA_LIST_REC_CORR[i] != self.DATA_LIST_REC_TEMP[i]:
                        # Skip system fields for comparison
                        if field_name not in ['created_at', 'updated_at', 'created_by', 'updated_by']:
                            differences.append(f"{field_name}: DB='{self.DATA_LIST_REC_CORR[i]}' != Form='{self.DATA_LIST_REC_TEMP[i]}'")
            
            if differences:
                QgsMessageLog.logMessage(f"DEBUG records_equal_check - Differences found in fields: {differences[:3]}", "PyArchInit", Qgis.Info)
            else:
                QgsMessageLog.logMessage(f"DEBUG records_equal_check - No differences in main fields", "PyArchInit", Qgis.Info)
            
            # Use the same logic for main record comparison as debug
            main_record_equal = len(differences) == 0
            
            # Check materials state
            materials_changed = self.check_materials_state()
            
            if main_record_equal and not materials_changed:
                return 0  # No changes
            else:
                return 1  # Changes detected
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
                # Get the value from the database record
                value = getattr(self.DATA_LIST[self.REC_CORR], i, None)
                # Convert None to empty string for consistent comparison
                if value is None:
                    value = ''
                else:
                    value = str(value)
                self.DATA_LIST_REC_CORR.append(value)
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

        if self.lineEdit_inventario.text():
            inv = self.lineEdit_inventario.text()
        else:
            inv = ""

        # Get ogtm from lineEdit_materiale (this is synced with the materials table)
        # This ensures consistency with what's displayed in the UI
        if self.lineEdit_materiale.text():
            ogtm = self.lineEdit_materiale.text()
        else:
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

        if self.comboBox_scan.currentText():
            scan = self.comboBox_scan.currentText()
        else:
            scan = ""

        if self.lineEdit_saggio.text():
            saggio = self.lineEdit_saggio.text()
        else:
            saggio = ""

        if self.lineEdit_vano_locus.text():
            vano_locus = self.lineEdit_vano_locus.text()
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
        if self.comboBox_dtzg.currentText():
            dtzg = self.comboBox_dtzg.currentText()
        else:
            dtzg = ""

        # Technical data
        if self.textEdit_deso.toPlainText():
            deso = self.textEdit_deso.toPlainText()
        else:
            deso = ""
        
        # Note storico-critiche field doesn't exist in the UI
        nsc = ""

            
        if self.comboBox_settore.currentText():
            settore = self.comboBox_settore.currentText()
        else:
            settore = ""

        # Get documentation data from tables
        ftap, ftan = self.get_foto_data()
        drat, dran, draa = self.get_disegni_data()
        
        # Get system fields from current record if it exists
        created_at = ''
        updated_at = ''
        created_by = ''
        updated_by = ''
        
        if hasattr(self, 'DATA_LIST') and self.DATA_LIST and 0 <= self.REC_CORR < len(self.DATA_LIST):
            current_record = self.DATA_LIST[self.REC_CORR]
            # Get system fields from the current record
            created_at = str(current_record.created_at) if hasattr(current_record, 'created_at') and current_record.created_at else ''
            updated_at = str(current_record.updated_at) if hasattr(current_record, 'updated_at') and current_record.updated_at else ''
            created_by = str(current_record.created_by) if hasattr(current_record, 'created_by') and current_record.created_by else ''
            updated_by = str(current_record.updated_by) if hasattr(current_record, 'updated_by') and current_record.updated_by else ''

        # Build the temp list (29 fields with system fields - localita removed)
        self.DATA_LIST_REC_TEMP = [
            str(self.comboBox_sito.currentText()),  # sito
            str(self.comboBox_area.currentText()),  # area
            str(self.comboBox_localita.currentText()),  # area
            str(settore),  # settore
            str(inv),  # settore
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
            created_at,  # created_at
            updated_at,  # updated_at
            created_by,  # created_by
            updated_by   # updated_by
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
        
        # Set column headers - Categoria will sync to ogtm field
        headers = ["Categoria *", "Classe", "Prec. tipologica", "Definizione", "Cronologia", "Quantità", "Peso"]
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
        # Set flag to indicate we're loading materials
        self._loading_materials = True
        
        # Remove debug logging to reduce noise
        if not self.DATA_LIST or self.rec_num >= len(self.DATA_LIST):
            self._loading_materials = False
            return
        
        # Disconnect signals during loading to prevent false change notifications
        try:
            self.tableWidget_materiali.itemChanged.disconnect(self.on_materials_table_changed)
        except:
            pass  # Signal might not be connected
            
        # Clear table
        self.tableWidget_materiali.setRowCount(0)
        
        # Ensure headers are visible
        self.setup_materials_table()
        
        try:
            # Get current TMA id
            current_tma_id = self.DATA_LIST[self.rec_num].id
            
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
                    # DB columns: id(0), id_tma(1), madi(2), macc(3), macl(4), macp(5), macd(6), cronologia_mac(7), macq(8), peso(9)
                    # Table headers: "Categoria *", "Classe", "Prec. tipologica", "Definizione", "Cronologia", "Quantità", "Peso"
                    # Correct mapping:
                    # Table col 0 (Categoria) <- madi (row[2])
                    # Table col 1 (Classe) <- macc (row[3])
                    # Table col 2 (Prec. tipologica) <- macl (row[4])
                    # Table col 3 (Definizione) <- macp (row[5])
                    # Table col 4 (Cronologia) <- cronologia_mac (row[7]) - skip macd
                    # Table col 5 (Quantità) <- macq (row[8])
                    # Table col 6 (Peso) <- peso (row[9])
                    
                    # Column 0: Categoria <- madi
                    item0 = QTableWidgetItem(str(row[2]).strip() if row[2] else "")  # madi
                    item0.setData(Qt.UserRole, int(row[0]))  # Store material ID
                    self.tableWidget_materiali.setItem(table_row, 0, item0)
                    
                    # Column 1: Classe <- macc
                    item1 = QTableWidgetItem(str(row[3]).strip() if row[3] else "")  # macc
                    self.tableWidget_materiali.setItem(table_row, 1, item1)
                    
                    # Column 2: Prec. tipologica <- macl
                    item2 = QTableWidgetItem(str(row[4]).strip() if row[4] else "")  # macl
                    self.tableWidget_materiali.setItem(table_row, 2, item2)
                    
                    # Column 3: Definizione <- macp
                    item3 = QTableWidgetItem(str(row[5]).strip() if row[5] else "")  # macp
                    self.tableWidget_materiali.setItem(table_row, 3, item3)
                    
                    # Column 4: Cronologia <- cronologia_mac (skip macd)
                    item4 = QTableWidgetItem(str(row[7]).strip() if row[7] else "")  # cronologia_mac
                    self.tableWidget_materiali.setItem(table_row, 4, item4)
                    
                    # Column 5: Quantità <- macq
                    item5 = QTableWidgetItem(str(row[8]).strip() if row[8] else "")  # macq
                    self.tableWidget_materiali.setItem(table_row, 5, item5)
                    
                    # Column 6: Peso <- peso
                    item6 = QTableWidgetItem(str(row[9]).strip() if row[9] else "")  # peso
                    self.tableWidget_materiali.setItem(table_row, 6, item6)
                    
                # Log each material loaded
                for i in range(self.tableWidget_materiali.rowCount()):
                    item0 = self.tableWidget_materiali.item(i, 0)
                    if item0:
                        QgsMessageLog.logMessage(f"  Row {i}: Category='{item0.text()}', ID={item0.data(Qt.UserRole)}", "PyArchInit", Qgis.Info)
                
                # Mark materials as loaded
                self.materials_loaded = True
                
                # Update the materiale field with loaded materials
                self.update_materiale_field()
                    
            finally:
                session.close()
                
        except Exception as e:
            QgsMessageLog.logMessage(f"DEBUG TMA load_materials_table: Error occurred: {str(e)}", "PyArchInit", Qgis.Warning)
            import traceback
            traceback.print_exc()
        
        # Reconnect signal after loading is complete (only if not already connected)
        try:
            # Try to disconnect first to avoid duplicate connections
            self.tableWidget_materiali.itemChanged.disconnect(self.on_materials_table_changed)
        except:
            pass  # Was not connected
        
        # Now connect once
        self.tableWidget_materiali.itemChanged.connect(self.on_materials_table_changed)
        
        # Clear the materials_modified flag after loading
        self.materials_modified = False
        self._loading_materials = False
        QgsMessageLog.logMessage(f"DEBUG load_materials_table: Reset flags - materials_modified=False, _loading_materials=False", "PyArchInit", Qgis.Info)

    def save_materials_data(self, tma_id):
        """Save materials table data to database."""
        QgsMessageLog.logMessage(f"DEBUG TMA save_materials_data: CALLED with tma_id={tma_id}, type={type(tma_id)}", "PyArchInit", Qgis.Info)
        QgsMessageLog.logMessage(f"DEBUG TMA save_materials_data: Table has {self.tableWidget_materiali.rowCount()} rows", "PyArchInit", Qgis.Info)
        QgsMessageLog.logMessage(f"DEBUG TMA save_materials_data: materials_loaded flag = {self.materials_loaded}", "PyArchInit", Qgis.Info)
        
        # SAFETY CHECK: If materials were never loaded, don't process anything
        if not self.materials_loaded:
            QgsMessageLog.logMessage("WARNING TMA save_materials_data: Materials were never loaded - skipping save to prevent data loss", "PyArchInit", Qgis.Warning)
            return
            
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
            
            # Track empty rows for user notification
            empty_rows = []
            
            # Force table to commit any pending edits before reading
            QgsMessageLog.logMessage("DEBUG TMA save_materials_data: Forcing commit of pending edits", "PyArchInit", Qgis.Info)
            
            # Method 1: Close any persistent editors
            for r in range(self.tableWidget_materiali.rowCount()):
                for c in range(self.tableWidget_materiali.columnCount()):
                    item = self.tableWidget_materiali.item(r, c)
                    if item:
                        self.tableWidget_materiali.closePersistentEditor(item)
            
            # Method 2: End edit mode
            if self.tableWidget_materiali.state() == QAbstractItemView.EditingState:
                current = self.tableWidget_materiali.currentItem()
                if current:
                    # Get the delegate and force it to commit
                    delegate = self.tableWidget_materiali.itemDelegateForColumn(current.column())
                    if delegate:
                        # Try to get the editor widget
                        editor = self.tableWidget_materiali.indexWidget(self.tableWidget_materiali.currentIndex())
                        if editor:
                            # Force the delegate to save data
                            delegate.setModelData(editor, self.tableWidget_materiali.model(), self.tableWidget_materiali.currentIndex())
                    
                    self.tableWidget_materiali.closePersistentEditor(current)
                    # Force end editing mode
                    self.tableWidget_materiali.setCurrentItem(None)
            
            # Method 3: Force focus away to commit any delegate changes
            try:
                self.setFocus()
                from qgis.PyQt.QtWidgets import QApplication
                QApplication.processEvents()  # Process any pending events
            except:
                pass  # In case QApplication is not available
            
            # Method 4: Deselect to ensure all data is committed
            self.tableWidget_materiali.setCurrentCell(-1, -1)
            
            # Give a moment for everything to settle
            try:
                from qgis.PyQt.QtWidgets import QApplication
                QApplication.processEvents()
            except:
                pass
            
            # Process each row in the table widget
            for row in range(self.tableWidget_materiali.rowCount()):
                QgsMessageLog.logMessage(f"DEBUG TMA: Processing row {row} of {self.tableWidget_materiali.rowCount()} total rows", "PyArchInit", Qgis.Info)
                
                # Debug: check if items exist and create missing ones
                for col in range(7):  # Table has 7 columns, not 8
                    item = self.tableWidget_materiali.item(row, col)
                    if item:
                        QgsMessageLog.logMessage(f"DEBUG TMA save: Row {row}, Col {col} - item exists, text='{item.text()}', type={type(item)}", "PyArchInit", Qgis.Info)
                    else:
                        QgsMessageLog.logMessage(f"DEBUG TMA save: Row {row}, Col {col} - NO ITEM! Creating one now...", "PyArchInit", Qgis.Warning)
                        # Create missing item
                        empty_item = QTableWidgetItem("")
                        empty_item.setToolTip("")
                        self.tableWidget_materiali.setItem(row, col, empty_item)
                
                # Column mapping according to setup_materials_table:
                # Column 0: Categoria * (macc)
                # Column 1: Classe (macl)
                # Column 2: Prec. tipologica (macp)
                # Column 3: Definizione (macd)
                # Column 4: Cronologia (cronologia_mac)
                # Column 5: Quantità (macq)
                # Column 6: Peso
                # Note: madi (materiale) is now stored in lineEdit_materiale, not in table
                
                item0 = self.tableWidget_materiali.item(row, 0)
                item1 = self.tableWidget_materiali.item(row, 1)
                item2 = self.tableWidget_materiali.item(row, 2)
                item3 = self.tableWidget_materiali.item(row, 3)
                item4 = self.tableWidget_materiali.item(row, 4)
                item5 = self.tableWidget_materiali.item(row, 5)
                item6 = self.tableWidget_materiali.item(row, 6)
                
                # Get text values from table items - try multiple methods
                # Try text() first, then data() roles as fallback
                def get_cell_value(item, col_index):
                    if not item:
                        return ""
                    
                    # Try text() first - this should have the committed value
                    val = item.text()
                    if val:
                        QgsMessageLog.logMessage(f"DEBUG TMA get_cell_value: Row {row}, Col {col_index} - text()='{val}'", "PyArchInit", Qgis.Info)
                        return val
                    
                    # Try EditRole
                    val = item.data(Qt.EditRole)
                    if val:
                        QgsMessageLog.logMessage(f"DEBUG TMA get_cell_value: Row {row}, Col {col_index} - EditRole='{val}'", "PyArchInit", Qgis.Info)
                        return str(val)
                    
                    # Try DisplayRole
                    val = item.data(Qt.DisplayRole)
                    if val:
                        QgsMessageLog.logMessage(f"DEBUG TMA get_cell_value: Row {row}, Col {col_index} - DisplayRole='{val}'", "PyArchInit", Qgis.Info)
                        return str(val)
                    
                    # Try backup UserRole+1
                    val = item.data(Qt.UserRole + 1)
                    if val:
                        QgsMessageLog.logMessage(f"DEBUG TMA get_cell_value: Row {row}, Col {col_index} - UserRole+1='{val}'", "PyArchInit", Qgis.Info)
                        return str(val)
                    
                    QgsMessageLog.logMessage(f"DEBUG TMA get_cell_value: Row {row}, Col {col_index} - NO DATA FOUND!", "PyArchInit", Qgis.Warning)
                    return ""
                
                # Get values from table with correct mapping (7 columns total)
                # Table headers: "Categoria *", "Classe", "Prec. tipologica", "Definizione", "Cronologia", "Quantità", "Peso"
                # Mapping to database fields:
                # Column 0: Categoria -> madi
                # Column 1: Classe -> macc
                # Column 2: Prec. tipologica -> macl
                # Column 3: Definizione -> macp
                # Column 4: Cronologia -> cronologia_mac
                # Column 5: Quantità -> macq
                # Column 6: Peso -> peso
                # Note: macd is not used in the UI, set to empty string
                
                madi = get_cell_value(item0, 0)  # Categoria -> madi
                macc = get_cell_value(item1, 1)  # Classe -> macc
                macl = get_cell_value(item2, 2)  # Prec. tipologica -> macl
                macp = get_cell_value(item3, 3)  # Definizione -> macp
                cronologia_mac = get_cell_value(item4, 4)  # Cronologia -> cronologia_mac
                macq = get_cell_value(item5, 5)  # Quantità -> macq
                peso_text = get_cell_value(item6, 6)  # Peso -> peso
                
                # macd is not in the UI, set to empty string
                macd = ""
                
                # Use madi as the material identifier
                materiale = madi
                
                # Convert to string to ensure consistency and trim whitespace
                materiale = str(materiale).strip() if materiale else ""
                madi = str(madi).strip() if madi else ""
                macc = str(macc).strip() if macc else ""
                macl = str(macl).strip() if macl else ""
                macp = str(macp).strip() if macp else ""
                macd = str(macd).strip() if macd else ""
                cronologia_mac = str(cronologia_mac).strip() if cronologia_mac else ""
                macq = str(macq).strip() if macq else ""
                peso_text = str(peso_text).strip() if peso_text else ""
                
                QgsMessageLog.logMessage(f"DEBUG TMA save_materials: Row {row} - item5={item5}, cronologia_mac='{cronologia_mac}'", "PyArchInit", Qgis.Info)
                
                QgsMessageLog.logMessage(f"DEBUG TMA: Row {row} data - materiale: '{materiale}', macc: '{macc}'", "PyArchInit", Qgis.Info)
                
                # Convert peso to float
                try:
                    peso = float(peso_text) if peso_text else 0.0
                except ValueError:
                    peso = 0.0
                
                # Skip completely empty rows (Category/madi is required as it's the main identifier)
                if not madi.strip():
                    QgsMessageLog.logMessage(f"DEBUG TMA: Row {row} - categoria (madi) is empty, madi='{madi}'", "PyArchInit", Qgis.Info)
                    QgsMessageLog.logMessage(f"DEBUG TMA: Row {row} - item0={item0}, item0.text()='{item0.text() if item0 else 'None'}'", "PyArchInit", Qgis.Info)
                    
                    # Check if this is truly an empty row or if we have data loss
                    has_any_data = False
                    for c in range(7):
                        test_item = self.tableWidget_materiali.item(row, c)
                        if test_item and test_item.text().strip():
                            has_any_data = True
                            QgsMessageLog.logMessage(f"DEBUG TMA: Row {row} has data in column {c}: '{test_item.text()}'", "PyArchInit", Qgis.Warning)
                    
                    if has_any_data:
                        QgsMessageLog.logMessage(f"ERROR TMA: Row {row} has data but category reading failed!", "PyArchInit", Qgis.Critical)
                    
                    empty_rows.append(row + 1)  # Use 1-based indexing for user message
                    continue
                
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
                    
                    # Check if data has changed (trim existing values for comparison)
                    existing = existing_ids[material_id]
                    if (str(existing.madi or '').strip() != materiale or 
                        str(existing.macc or '').strip() != macc or 
                        str(existing.macl or '').strip() != macl or 
                        str(existing.macp or '').strip() != macp or 
                        str(existing.macd or '').strip() != macd or 
                        str(existing.cronologia_mac or '').strip() != cronologia_mac or 
                        str(existing.macq or '').strip() != macq or 
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
                    # Get the max ID considering both existing materials and newly inserted ones this session
                    try:
                        max_id = self.DB_MANAGER.max_num_id('TMA_MATERIALI', 'id')
                        QgsMessageLog.logMessage(f"DEBUG TMA: max_id from DB = {max_id}", "PyArchInit", Qgis.Info)
                        
                        # Also consider IDs we've already used in this save session
                        if seen_ids:
                            max_seen_id = max(seen_ids)
                            QgsMessageLog.logMessage(f"DEBUG TMA: max seen_id = {max_seen_id}, seen_ids = {seen_ids}", "PyArchInit", Qgis.Info)
                            max_id = max(max_id if max_id is not None else 0, max_seen_id)
                        
                        new_material_id = (max_id + 1) if max_id is not None else 1
                    except Exception as id_error:
                        QgsMessageLog.logMessage(f"DEBUG TMA: Error getting max ID: {id_error}", "PyArchInit", Qgis.Warning)
                        # If all else fails, use a safe starting point
                        if seen_ids:
                            new_material_id = max(seen_ids) + 1
                        else:
                            new_material_id = 1
                    
                    QgsMessageLog.logMessage(f"DEBUG TMA: Assigning new material ID {new_material_id} for row {row}", "PyArchInit", Qgis.Info)
                    
                    # Track this new ID
                    seen_ids.add(new_material_id)
                    
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
                            
                            # Store the new material ID in the table widget for future updates
                            if self.tableWidget_materiali.item(row, 0):
                                self.tableWidget_materiali.item(row, 0).setData(Qt.UserRole, new_material_id)
                                QgsMessageLog.logMessage(f"DEBUG TMA: Stored new material ID {new_material_id} in row {row}", "PyArchInit", Qgis.Info)
                            
                        finally:
                            insert_session.close()
                            
                    except Exception as insert_error:
                        QgsMessageLog.logMessage(f"SQL insert failed: {insert_error}", "PyArchInit", Qgis.Warning)
                        raise
                    seen_ids.add(new_material_id)
                    QgsMessageLog.logMessage(f"DEBUG TMA: Successfully inserted material ID {new_material_id}, seen_ids now: {seen_ids}", "PyArchInit", Qgis.Info)
            
            # Delete materials that were removed from the table
            # ONLY delete if we have explicitly loaded materials AND the user has made changes
            QgsMessageLog.logMessage(f"DEBUG TMA: Deletion check - materials_loaded={self.materials_loaded}, table_rows={self.tableWidget_materiali.rowCount()}, existing_materials={len(existing_materials)}, seen_ids={seen_ids}", "PyArchInit", Qgis.Info)
            
            # Check if we should process deletions
            should_process_deletions = False
            
            # Only process deletions if:
            # 1. Materials were loaded successfully from an existing record
            # 2. AND we have existing materials to potentially delete
            # 3. AND it's not a new record (check if we're in update mode)
            if self.materials_loaded and len(existing_materials) > 0 and self.BROWSE_STATUS == "b":
                # We're updating an existing record with existing materials
                should_process_deletions = True
                QgsMessageLog.logMessage(f"DEBUG TMA: Will process deletions - existing record with {len(existing_materials)} existing materials", "PyArchInit", Qgis.Info)
            else:
                QgsMessageLog.logMessage(f"DEBUG TMA: NOT processing deletions - materials_loaded={self.materials_loaded}, existing_materials={len(existing_materials)}, BROWSE_STATUS={self.BROWSE_STATUS}", "PyArchInit", Qgis.Info)
            
            # Also process explicitly deleted materials
            if hasattr(self, 'deleted_material_ids') and self.deleted_material_ids:
                QgsMessageLog.logMessage(f"DEBUG TMA: Processing {len(self.deleted_material_ids)} explicitly deleted materials", "PyArchInit", Qgis.Info)
                for deleted_id in self.deleted_material_ids:
                    try:
                        delete_session = Session()
                        sql = text("DELETE FROM tma_materiali_ripetibili WHERE id = :id")
                        delete_session.execute(sql, {'id': deleted_id})
                        delete_session.commit()
                        delete_session.close()
                        QgsMessageLog.logMessage(f"DEBUG TMA: Deleted material ID={deleted_id}", "PyArchInit", Qgis.Info)
                    except Exception as del_error:
                        QgsMessageLog.logMessage(f"Error deleting material {deleted_id}: {del_error}", "PyArchInit", Qgis.Warning)
                # Clear the deleted IDs after processing
                self.deleted_material_ids.clear()
            
            # Process deletions if appropriate
            if should_process_deletions:
                for existing_id in existing_ids:
                    if existing_id not in seen_ids and (not hasattr(self, 'deleted_material_ids') or existing_id not in self.deleted_material_ids):
                        QgsMessageLog.logMessage(f"DEBUG TMA: Deleting material ID={existing_id} (not in current table)", "PyArchInit", Qgis.Info)
                        try:
                            delete_session = Session()
                            sql = text("DELETE FROM tma_materiali_ripetibili WHERE id = :id")
                            delete_session.execute(sql, {'id': existing_id})
                            delete_session.commit()
                            delete_session.close()
                        except Exception as del_error:
                            QgsMessageLog.logMessage(f"Error deleting material: {del_error}", "PyArchInit", Qgis.Warning)
            
            # Clean up empty rows from the table widget (visual cleanup)
            rows_to_remove = []
            for row in range(self.tableWidget_materiali.rowCount() - 1, -1, -1):  # Iterate backwards
                is_empty = True
                for col in range(self.tableWidget_materiali.columnCount()):
                    item = self.tableWidget_materiali.item(row, col)
                    if item and item.text().strip():
                        is_empty = False
                        break
                if is_empty:
                    rows_to_remove.append(row)
            
            # Remove empty rows
            for row in rows_to_remove:
                QgsMessageLog.logMessage(f"DEBUG TMA: Removing empty row {row} from table", "PyArchInit", Qgis.Info)
                self.tableWidget_materiali.removeRow(row)
            
            # Notify user about empty rows if any
            if empty_rows:
                # Double-check if these rows were truly empty or if there was a data reading issue
                truly_empty_rows = []
                for row_num in empty_rows:
                    row_idx = row_num - 1  # Convert back to 0-based index
                    if row_idx < self.tableWidget_materiali.rowCount():
                        # Check if the row has any visible data
                        row_has_data = False
                        for c in range(self.tableWidget_materiali.columnCount()):
                            item = self.tableWidget_materiali.item(row_idx, c)
                            if item and item.text().strip():
                                row_has_data = True
                                break
                        
                        if not row_has_data:
                            truly_empty_rows.append(row_num)
                        else:
                            QgsMessageLog.logMessage(f"DEBUG TMA: Row {row_num} reported as empty but has data - skipping error message", "PyArchInit", Qgis.Info)
                
                # Only show message for truly empty rows
                if truly_empty_rows:
                    if self.L == 'it':
                        msg = f"Attenzione: Le righe {', '.join(map(str, truly_empty_rows))} non sono state salvate perché manca la categoria (campo obbligatorio)."
                    else:
                        msg = f"Warning: Rows {', '.join(map(str, truly_empty_rows))} were not saved because category is missing (required field)."
                    QMessageBox.information(self, "Materiali vuoti", msg, QMessageBox.Ok)
                    
        except Exception as e:
            import traceback
            traceback.print_exc()
            error_msg = f"Errore nel salvataggio materiali: {str(e)}\n\n"
            error_msg += f"TMA ID: {tma_id}\n"
            error_msg += f"Tabelle verificate nel database."
            QMessageBox.warning(self, "Error", error_msg, QMessageBox.Ok)

    def on_pushButton_add_materiale_pressed(self):
        """Add a new row to materials table."""
        # Prevent multiple rapid calls - check and set flag atomically
        if hasattr(self, '_button_operation_timer') and self._button_operation_timer.isActive():
            QgsMessageLog.logMessage("DEBUG TMA add_materiale: Button operation in progress, skipping", "PyArchInit", Qgis.Warning)
            return
        
        # Create timer if it doesn't exist
        if not hasattr(self, '_button_operation_timer'):
            self._button_operation_timer = QTimer()
            self._button_operation_timer.setSingleShot(True)
        
        # Start timer to prevent rapid successive calls (250ms cooldown)
        self._button_operation_timer.start(250)
        
        # Temporarily block signals on the table to prevent cascading events
        self.tableWidget_materiali.blockSignals(True)
        
        try:
            # Debug: log entry and current state
            rows_before = self.tableWidget_materiali.rowCount()
            QgsMessageLog.logMessage(f"DEBUG TMA add_materiale: CALLED - rows before = {rows_before}", "PyArchInit", Qgis.Info)
            
            # Add single row
            row = self.tableWidget_materiali.rowCount()
            self.tableWidget_materiali.insertRow(row)
            
            rows_after = self.tableWidget_materiali.rowCount()
            QgsMessageLog.logMessage(f"DEBUG TMA add_materiale: Added row {row} - rows after = {rows_after}", "PyArchInit", Qgis.Info)
            
            # Debug: check if delegates are working
            for col in range(5):  # Check first 5 columns which should have thesaurus
                delegate = self.tableWidget_materiali.itemDelegateForColumn(col)
                if delegate:
                    QgsMessageLog.logMessage(f"  Column {col} has delegate: {type(delegate).__name__}", "PyArchInit", Qgis.Info)
            
            # Create empty items for each column - REQUIRED for delegates to work properly
            for col in range(self.tableWidget_materiali.columnCount()):
                if not self.tableWidget_materiali.item(row, col):
                    empty_item = QTableWidgetItem("")
                    empty_item.setToolTip("")
                    self.tableWidget_materiali.setItem(row, col, empty_item)
                    
        finally:
            # Re-enable signals
            self.tableWidget_materiali.blockSignals(False)

    def on_pushButton_remove_materiale_pressed(self):
        """Remove selected row from materials table."""
        # Prevent multiple rapid calls - use same timer as add method
        if hasattr(self, '_button_operation_timer') and self._button_operation_timer.isActive():
            QgsMessageLog.logMessage("DEBUG TMA remove_materiale: Button operation in progress, skipping", "PyArchInit", Qgis.Warning)
            return
        
        # Create timer if it doesn't exist
        if not hasattr(self, '_button_operation_timer'):
            self._button_operation_timer = QTimer()
            self._button_operation_timer.setSingleShot(True)
        
        # Start timer to prevent rapid successive calls (250ms cooldown)
        self._button_operation_timer.start(250)
        
        # Temporarily block signals on the table to prevent cascading events
        self.tableWidget_materiali.blockSignals(True)
        
        try:
            rows_before = self.tableWidget_materiali.rowCount()
            current_row = self.tableWidget_materiali.currentRow()
            QgsMessageLog.logMessage(f"DEBUG TMA remove_materiale: CALLED - rows before = {rows_before}, current_row = {current_row}", "PyArchInit", Qgis.Info)
            
            if current_row >= 0:
                # Get the material ID if it exists (for existing records)
                item = self.tableWidget_materiali.item(current_row, 0)
                if item and item.data(Qt.UserRole) is not None:
                    material_id = item.data(Qt.UserRole)
                    QgsMessageLog.logMessage(f"DEBUG TMA: Removing material row {current_row} with ID {material_id}", "PyArchInit", Qgis.Info)
                    # Mark as deleted (will be handled during save)
                    if not hasattr(self, 'deleted_material_ids'):
                        self.deleted_material_ids = set()
                    self.deleted_material_ids.add(int(material_id))
                
                self.tableWidget_materiali.removeRow(current_row)
                
                rows_after = self.tableWidget_materiali.rowCount()
                QgsMessageLog.logMessage(f"DEBUG TMA remove_materiale: Removed row {current_row} - rows after = {rows_after}", "PyArchInit", Qgis.Info)
                
                # Update materiale field after removing row
                self.update_materiale_field()
            else:
                QgsMessageLog.logMessage(f"DEBUG TMA remove_materiale: No row selected", "PyArchInit", Qgis.Info)
                
        finally:
            # Re-enable signals
            self.tableWidget_materiali.blockSignals(False)
    
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
        self.comboBox_localita.setEditText("")
        # Don't clear area here - let it be managed by località change
        self.lineEdit_us.clear()
        self.lineEdit_inventario.clear()
        # All other fields
        self.comboBox_ldct.setEditText("")
        self.comboBox_ldcn.setEditText("")
        self.lineEdit_vecchia_collocazione.clear()
        self.lineEdit_cassetta.clear()
        self.comboBox_scan.setEditText("")
        self.lineEdit_saggio.clear()
        self.lineEdit_vano_locus.clear()
        self.lineEdit_dscd.clear()
        self.lineEdit_rcgd.clear()
        self.textEdit_rcgz.clear()
        self.comboBox_aint.setEditText("")
        self.lineEdit_aind.clear()
        self.comboBox_dtzg.setEditText("")  # Don't clear items, just reset selection
        self.textEdit_deso.clear()
        
        # Clear new fields
        # Clear area and settore when località is cleared
        self.comboBox_area.setEditText("")
        self.comboBox_settore.setEditText("")
        self.lineEdit_materiale.clear()
        
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
        
        # Clear media list
        self.iconListWidget.clear()
        
        # Reset materials loaded flag
        self.materials_loaded = False

    def empty_fields_nosite(self):
        """Clear all form fields except site."""
        # Save current site
        current_site = self.comboBox_sito.currentText()
        
        # Basic fields (except site)
        self.comboBox_area.setEditText("")
        self.lineEdit_us.clear()
        self.lineEdit_inventario.clear()
        # All other fields
        self.comboBox_ldct.setEditText("")
        self.comboBox_ldcn.setEditText("")
        self.lineEdit_vecchia_collocazione.clear()
        self.lineEdit_cassetta.clear()
        self.comboBox_scan.setEditText("")
        self.lineEdit_saggio.clear()
        self.lineEdit_vano_locus.clear()
        self.lineEdit_dscd.clear()
        self.lineEdit_rcgd.clear()
        self.textEdit_rcgz.clear()
        self.comboBox_aint.setEditText("")
        self.lineEdit_aind.clear()
        self.comboBox_dtzg.setEditText("")  # Keep the list items
        self.textEdit_deso.clear()

        # Clear new fields
        self.comboBox_settore.setEditText("")
        self.lineEdit_materiale.clear()

        # Clear materials table
        self.tableWidget_materiali.setRowCount(0)
        # Ensure headers are visible
        self.setup_materials_table()

        # Clear inventory field


        # Reset materials navigation
        self.current_material_index = -1
        self.materials_data = []
        self.update_material_navigation()

        # Clear tables
        self.tableWidget_foto.setRowCount(0)
        self.tableWidget_disegni.setRowCount(0)
        
        # Restore site value
        if current_site:
            self.comboBox_sito.setEditText(current_site)
            
        # Clear località but don't trigger event yet
        self.comboBox_localita.blockSignals(True)
        self.comboBox_localita.setEditText("")
        self.comboBox_localita.blockSignals(False)
            
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
    
    def REC_TOT_TEMP(self):
        """Return the temporary total number of records."""
        return self.REC_TOT
    
    def check_record_state(self):
        """Check if record has been modified but don't show dialog or trigger actions."""
        ec = self.data_error_check()
        QgsMessageLog.logMessage(f"DEBUG check_record_state: data_error_check returned {ec}", "PyArchInit", Qgis.Info)
        
        if ec == 1:
            return 1  # ci sono errori di immissione
        
        records_equal_result = self.records_equal_check()
        QgsMessageLog.logMessage(f"DEBUG check_record_state: records_equal_check returned {records_equal_result}", "PyArchInit", Qgis.Info)
        
        if records_equal_result == 0 and ec == 0:
            # Records are equal, check materials
            materials_changed = self.check_materials_state()
            QgsMessageLog.logMessage(f"DEBUG check_record_state: records_equal=True, materials_changed={materials_changed}", "PyArchInit", Qgis.Info)
            if materials_changed:
                return 1  # Materials have been modified
            return 0  # nessuna modifica
        else:
            # Records are NOT equal
            QgsMessageLog.logMessage(f"DEBUG check_record_state: records NOT equal (result={records_equal_result}), returning 1", "PyArchInit", Qgis.Info)
            return 1  # record modificato

            # records surf functions
    def check_materials_state(self):
        """Check if materials in the table have changed compared to database."""
        # Don't check if we're currently loading materials
        if hasattr(self, '_loading_materials') and self._loading_materials:
            QgsMessageLog.logMessage("DEBUG check_materials_state: Skipping - currently loading materials", "PyArchInit", Qgis.Info)
            return False
            
        try:
            # Don't use materials_modified flag for checking - it causes false positives
            # The flag should only be set when user actually modifies materials
            
            if not self.DATA_LIST or self.REC_CORR >= len(self.DATA_LIST):
                # New record, check if table has content with valid data
                for row in range(self.tableWidget_materiali.rowCount()):
                    # Check first column (categoria) since that's the main field
                    item = self.tableWidget_materiali.item(row, 0)
                    if item and item.text().strip():
                        return True
                return False
            
            # Get current materials from database using direct SQL to avoid type issues
            current_tma_id = self.DATA_LIST[self.REC_CORR].id
            
            # Use direct SQL query to avoid type comparison issues in query_bool
            from sqlalchemy import text
            from sqlalchemy.orm import sessionmaker
            
            # Convert tma_id to int for consistency
            tma_id_int = int(current_tma_id)
            
            # Create a session
            Session = sessionmaker(bind=self.DB_MANAGER.engine)
            session = Session()
            
            try:
                # Get existing materials using direct SQL - select specific columns to ensure correct mapping
                sql = text("SELECT id, id_tma, madi, macc, macl, macp, macd, cronologia_mac, macq, peso FROM tma_materiali_ripetibili WHERE id_tma = :id_tma ORDER BY id")
                result = session.execute(sql, {'id_tma': tma_id_int})
                
                # Convert results to list of dictionaries
                db_materials = []
                for row in result:
                    # Create a dictionary with material data
                    # Access by index since we're using direct SQL
                    mat_dict = {
                        'id': row[0],
                        'id_tma': row[1],
                        'madi': row[2],        # categoria
                        'macc': row[3],        # classe
                        'macl': row[4],        # tipologia  
                        'macp': row[5],        # definizione
                        'macd': row[6],        # ?
                        'cronologia_mac': row[7],  # cronologia
                        'macq': row[8],        # quantità
                        'peso': row[9]         # peso
                    }
                    db_materials.append(mat_dict)
                
                # Count valid rows in table (rows with at least categoria filled)
                table_valid_rows = 0
                table_materials = []
                
                for row in range(self.tableWidget_materiali.rowCount()):
                    # Check if row has categoria (column 0)
                    madi_item = self.tableWidget_materiali.item(row, 0)
                    if madi_item and madi_item.text().strip():
                        table_valid_rows += 1
                        
                        # Get all values from this row (7 columns total)
                        # Mapping: Col 0->madi, Col 1->macc, Col 2->macl, Col 3->macp, Col 4->cronologia_mac, Col 5->macq, Col 6->peso
                        mat_data = {
                            'madi': madi_item.text().strip(),
                            'macc': self.tableWidget_materiali.item(row, 1).text().strip() if self.tableWidget_materiali.item(row, 1) else "",
                            'macl': self.tableWidget_materiali.item(row, 2).text().strip() if self.tableWidget_materiali.item(row, 2) else "",
                            'macp': self.tableWidget_materiali.item(row, 3).text().strip() if self.tableWidget_materiali.item(row, 3) else "",
                            'macd': "",  # Not in UI, always empty
                            'cronologia_mac': self.tableWidget_materiali.item(row, 4).text().strip() if self.tableWidget_materiali.item(row, 4) else "",
                            'macq': self.tableWidget_materiali.item(row, 5).text().strip() if self.tableWidget_materiali.item(row, 5) else "",
                            'peso': self.tableWidget_materiali.item(row, 6).text().strip() if self.tableWidget_materiali.item(row, 6) else ""
                        }
                        table_materials.append(mat_data)
                
                # Quick check: different number of materials
                if len(db_materials) != table_valid_rows:
                    QgsMessageLog.logMessage(f"DEBUG check_materials_state: Count mismatch - DB={len(db_materials)}, Table={table_valid_rows}", "PyArchInit", Qgis.Info)
                    return True
                
                # Compare materials content if counts match
                if len(db_materials) > 0:
                    # Compare each material
                    for i, db_mat in enumerate(db_materials):
                        if i >= len(table_materials):
                            return True  # Missing material in table
                        
                        table_mat = table_materials[i]
                        
                        # Compare each field (converting None to empty string and trimming)
                        db_values = {
                            'madi': str(db_mat['madi'] or '').strip(),
                            'macc': str(db_mat['macc'] or '').strip(),
                            'macl': str(db_mat['macl'] or '').strip(),
                            'macp': str(db_mat['macp'] or '').strip(),
                            'macd': str(db_mat['macd'] or '').strip(),
                            'cronologia_mac': str(db_mat['cronologia_mac'] or '').strip(),
                            'macq': str(db_mat['macq'] or '').strip(),
                            'peso': str(db_mat['peso'] or '').strip()
                        }
                        
                        differences = []
                        for field in ['madi', 'macc', 'macl', 'macp', 'macd', 'cronologia_mac', 'macq', 'peso']:
                            if db_values[field] != table_mat[field]:
                                differences.append(f"{field}: DB='{db_values[field]}' != Table='{table_mat[field]}'")
                        
                        if differences:
                            QgsMessageLog.logMessage(f"DEBUG check_materials_state: Material {i} differs - {differences}", "PyArchInit", Qgis.Info)
                            return True
                
                return False
                
            finally:
                session.close()
            
        except Exception as e:
            QgsMessageLog.logMessage(f"DEBUG TMA: Error in check_materials_state: {e}", "PyArchInit", Qgis.Warning)
            # If error occurs, assume no change to avoid false positives
            return False

    def data_error_check(self):
        """Check for data errors in form fields."""
        test = 0
        EC = Error_check()

        # Check required fields
        # Note: materiale field has been moved to materials table

        # ldcn and cassetta are now optional fields


        # US field is optional
        # All required field checks have been removed as per new requirements


        # Materials are now in the materials table and are optional

        return test

    def update_if(self, msg):
        """Update interface message."""
        return msg

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
        # Prevent multiple rapid navigation calls
        if hasattr(self, '_navigation_in_progress') and self._navigation_in_progress:
            return
            
        # Also check with a timestamp to prevent rapid double clicks
        import time
        current_time = time.time()
        if hasattr(self, '_last_navigation_time'):
            if current_time - self._last_navigation_time < 0.5:  # 500ms debounce
                return
        self._last_navigation_time = current_time
            
        if self.check_record_state() == 1:
            msg = QMessageBox.warning(self, 'Attenzione', 
                                     "Il record è stato modificato. Vuoi salvare le modifiche?",
                                     QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if msg == QMessageBox.Cancel:
                return
            elif msg == QMessageBox.Yes:
                self.on_pushButton_save_pressed()
                if self.REC_CORR == 0:
                    return  # Already at first record
        
        self._navigation_in_progress = True
        try:
            self.empty_fields()
            self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
            self.fill_fields(0)
            self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e), QMessageBox.Ok)
        finally:
            self._navigation_in_progress = False

    def on_pushButton_last_rec_pressed(self):
        # Prevent multiple rapid navigation calls
        if hasattr(self, '_navigation_in_progress') and self._navigation_in_progress:
            return
            
        # Also check with a timestamp to prevent rapid double clicks
        import time
        current_time = time.time()
        if hasattr(self, '_last_navigation_time'):
            if current_time - self._last_navigation_time < 0.5:  # 500ms debounce
                return
        self._last_navigation_time = current_time
            
        if self.check_record_state() == 1:
            msg = QMessageBox.warning(self, 'Attenzione', 
                                     "Il record è stato modificato. Vuoi salvare le modifiche?",
                                     QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if msg == QMessageBox.Cancel:
                return
            elif msg == QMessageBox.Yes:
                self.on_pushButton_save_pressed()
                if self.REC_CORR == len(self.DATA_LIST) - 1:
                    return  # Already at last record
        
        self._navigation_in_progress = True
        try:
            self.empty_fields()
            self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), len(self.DATA_LIST) - 1
            self.fill_fields(self.REC_CORR)
            self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e), QMessageBox.Ok)
        finally:
            self._navigation_in_progress = False

    def on_pushButton_prev_rec_pressed(self):
        QgsMessageLog.logMessage(f"DEBUG TMA PREV: Called. REC_CORR={self.REC_CORR}, REC_TOT={self.REC_TOT}", "PyArchInit", Qgis.Info)
        
        # Prevent multiple rapid navigation calls
        if hasattr(self, '_navigation_in_progress') and self._navigation_in_progress:
            QgsMessageLog.logMessage("DEBUG TMA PREV: Navigation already in progress, skipping", "PyArchInit", Qgis.Warning)
            return
            
        # Also check with a timestamp to prevent rapid double clicks
        import time
        current_time = time.time()
        if hasattr(self, '_last_navigation_time'):
            if current_time - self._last_navigation_time < 0.5:  # 500ms debounce
                QgsMessageLog.logMessage(f"DEBUG TMA PREV: Too rapid (delta={current_time - self._last_navigation_time:.3f}s), skipping", "PyArchInit", Qgis.Warning)
                return
        self._last_navigation_time = current_time
            
        if self.REC_CORR <= 0:
            if self.L=='it':
                QMessageBox.warning(self, "Attenzione", "Sei al primo record!", QMessageBox.Ok)
            elif self.L=='de':
                QMessageBox.warning(self, "Warnung", "du befindest dich im ersten Datensatz!", QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "Warning", "You are at the first record!", QMessageBox.Ok)
            return
            
        if self.check_record_state() == 1:
            msg = QMessageBox.warning(self, 'Attenzione', 
                                     "Il record è stato modificato. Vuoi salvare le modifiche?",
                                     QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if msg == QMessageBox.Cancel:
                return
            elif msg == QMessageBox.Yes:
                self.on_pushButton_save_pressed()
        
        self._navigation_in_progress = True
        try:
            self.REC_CORR = self.REC_CORR - 1
            QgsMessageLog.logMessage(f"DEBUG TMA PREV: New REC_CORR={self.REC_CORR}", "PyArchInit", Qgis.Info)
            self.empty_fields()
            self.fill_fields(self.REC_CORR)
            self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
            QgsMessageLog.logMessage(f"DEBUG TMA PREV: Navigation completed to record {self.REC_CORR + 1}/{self.REC_TOT}", "PyArchInit", Qgis.Info)
        except Exception as e:
            QgsMessageLog.logMessage(f"DEBUG TMA PREV: Error during navigation: {e}", "PyArchInit", Qgis.Critical)
            QMessageBox.warning(self, "Error", str(e), QMessageBox.Ok)
        finally:
            self._navigation_in_progress = False

    def on_pushButton_next_rec_pressed(self):
        QgsMessageLog.logMessage(f"DEBUG TMA NEXT: Called. REC_CORR={self.REC_CORR}, REC_TOT={self.REC_TOT}", "PyArchInit", Qgis.Info)
        
        # Prevent multiple rapid navigation calls
        if hasattr(self, '_navigation_in_progress') and self._navigation_in_progress:
            QgsMessageLog.logMessage("DEBUG TMA NEXT: Navigation already in progress, skipping", "PyArchInit", Qgis.Warning)
            return
            
        # Also check with a timestamp to prevent rapid double clicks
        import time
        current_time = time.time()
        if hasattr(self, '_last_navigation_time'):
            if current_time - self._last_navigation_time < 0.5:  # 500ms debounce
                QgsMessageLog.logMessage(f"DEBUG TMA NEXT: Too rapid (delta={current_time - self._last_navigation_time:.3f}s), skipping", "PyArchInit", Qgis.Warning)
                return
        self._last_navigation_time = current_time
            
        if self.REC_CORR >= self.REC_TOT - 1:
            if self.L=='it':
                QMessageBox.warning(self, "Attenzione", "Sei all'ultimo record!", QMessageBox.Ok)
            elif self.L=='de':
                QMessageBox.warning(self, "Warnung", "du befindest dich im letzten Datensatz!", QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "Warning", "You are at the last record!", QMessageBox.Ok)
            return
            
        if self.check_record_state() == 1:
            msg = QMessageBox.warning(self, 'Attenzione', 
                                     "Il record è stato modificato. Vuoi salvare le modifiche?",
                                     QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if msg == QMessageBox.Cancel:
                return
            elif msg == QMessageBox.Yes:
                self.on_pushButton_save_pressed()
        
        self._navigation_in_progress = True
        try:
            self.REC_CORR = self.REC_CORR + 1
            QgsMessageLog.logMessage(f"DEBUG TMA NEXT: New REC_CORR={self.REC_CORR}", "PyArchInit", Qgis.Info)
            self.empty_fields()
            self.fill_fields(self.REC_CORR)
            self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
            QgsMessageLog.logMessage(f"DEBUG TMA NEXT: Navigation completed to record {self.REC_CORR + 1}/{self.REC_TOT}", "PyArchInit", Qgis.Info)
        except Exception as e:
            QgsMessageLog.logMessage(f"DEBUG TMA NEXT: Error during navigation: {e}", "PyArchInit", Qgis.Critical)
            QMessageBox.warning(self, "Error", str(e), QMessageBox.Ok)
        finally:
            self._navigation_in_progress = False




    def on_pushButton_new_rec_pressed(self):
        """Create a new record."""
        QgsMessageLog.logMessage("DEBUG TMA NEW_REC: Button clicked", "PyArchInit", Qgis.Info)
        
        # Check current state
        QgsMessageLog.logMessage(f"DEBUG TMA NEW_REC: BROWSE_STATUS={self.BROWSE_STATUS}, REC_CORR={self.REC_CORR}, REC_TOT={self.REC_TOT}", "PyArchInit", Qgis.Info)
        
        # Check if record has been modified
        record_state = self.check_record_state()
        QgsMessageLog.logMessage(f"DEBUG TMA NEW_REC: check_record_state() returned {record_state}", "PyArchInit", Qgis.Info)
        
        if record_state == 1:
            QgsMessageLog.logMessage("DEBUG TMA NEW_REC: Record has unsaved changes, showing update dialog", "PyArchInit", Qgis.Warning)
            self.update_if(QgsSettings().value("pyArchInit/ifupdaterecord"))
            QgsMessageLog.logMessage("DEBUG TMA NEW_REC: Returning early due to unsaved changes", "PyArchInit", Qgis.Warning)
            return
            
        if self.BROWSE_STATUS != "n":
            QgsMessageLog.logMessage(f"DEBUG TMA NEW_REC: Switching from BROWSE_STATUS={self.BROWSE_STATUS} to 'n' (new)", "PyArchInit", Qgis.Info)
            
            conn = Connection()
            sito_set = conn.sito_set()
            sito_set_str = sito_set['sito_set']
            QgsMessageLog.logMessage(f"DEBUG TMA NEW_REC: sito_set_str='{sito_set_str}'", "PyArchInit", Qgis.Info)
            
            self.BROWSE_STATUS = "n"
            self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
            
            QgsMessageLog.logMessage("DEBUG TMA NEW_REC: Calling empty_fields_nosite()", "PyArchInit", Qgis.Info)
            self.empty_fields_nosite()
            
            # Reset materials loaded flag when creating new record
            self.materials_loaded = False
            QgsMessageLog.logMessage(f"DEBUG TMA NEW_REC: materials_loaded set to False", "PyArchInit", Qgis.Info)
            
            self.label_sort.setText(self.SORTED_ITEMS["n"])
            
            # Set first available località value and trigger area loading
            localita_count = self.comboBox_localita.count()
            QgsMessageLog.logMessage(f"DEBUG TMA NEW_REC: località count = {localita_count}", "PyArchInit", Qgis.Info)
            
            if localita_count > 0:
                # Set first item in località dropdown
                self.comboBox_localita.setCurrentIndex(0)
                QgsMessageLog.logMessage(f"DEBUG TMA NEW_REC: Set località to index 0", "PyArchInit", Qgis.Info)
                # This will trigger on_localita_changed which will load filtered areas
            else:
                # If no località available, load all areas
                QgsMessageLog.logMessage("DEBUG TMA NEW_REC: No località available, loading all areas", "PyArchInit", Qgis.Info)
                self.load_area_values()
                
            # Mark materials as loaded for new records so they can be saved
            self.materials_loaded = True
            QgsMessageLog.logMessage(f"DEBUG TMA NEW_REC: materials_loaded set to True for new record", "PyArchInit", Qgis.Info)

            if bool(sito_set_str):
                # When sito_set is active, set the site field and make it read-only
                QgsMessageLog.logMessage(f"DEBUG TMA NEW_REC: Setting site to '{sito_set_str}' and making it read-only", "PyArchInit", Qgis.Info)
                self.comboBox_sito.setEditText(sito_set_str)
                self.setComboBoxEnable(["self.comboBox_sito"], "False")
                self.setComboBoxEditable(["self.comboBox_sito"], 0)
            else:
                # When sito_set is not active, allow site selection
                QgsMessageLog.logMessage("DEBUG TMA NEW_REC: No sito_set, enabling site selection", "PyArchInit", Qgis.Info)
                self.setComboBoxEnable(["self.comboBox_sito"], "True")
                self.setComboBoxEditable(["self.comboBox_sito"], 1)

            self.set_rec_counter('', '')
            self.label_sort.setText(self.SORTED_ITEMS["n"])
            QgsMessageLog.logMessage("DEBUG TMA NEW_REC: New record mode activated successfully", "PyArchInit", Qgis.Info)
        else:
            QgsMessageLog.logMessage(f"DEBUG TMA NEW_REC: Already in new record mode (BROWSE_STATUS={self.BROWSE_STATUS})", "PyArchInit", Qgis.Info)

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
                            # Update the local record to reflect changes
                            # Reload the single updated record from DB
                            search_dict = {'id': self.DATA_LIST[self.REC_CORR].id}
                            updated_record = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
                            if updated_record:
                                self.DATA_LIST[self.REC_CORR] = updated_record[0]
                                self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[self.REC_CORR]
                                # Just update the temp record without reloading UI
                                self.set_LIST_REC_TEMP()
                                self.set_LIST_REC_CORR()
                            QMessageBox.information(self, "Info", "Record aggiornato con successo", QMessageBox.Ok)
                    except Exception as e:
                        import traceback
                        traceback.print_exc()
                        QMessageBox.warning(self, "Error", f"Errore nel salvataggio materiali: {str(e)}", QMessageBox.Ok)
                    self.enable_button(1)
                else:
                    QMessageBox.warning(self, "ATTENZIONE", "Non è stata realizzata alcuna modifica!", QMessageBox.Ok)
            else:
                if self.data_error_check() == 0:
                    test_insert = self.insert_new_rec()
                    if test_insert == 1:
                        self.empty_fields()
                        self.label_sort.setText(self.SORTED_ITEMS["n"])
                        # Reload only the current record data without resetting UI
                        # Get the inserted record ID
                        inserted_id = self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, self.ID_TABLE)
                        # Query just the new record
                        search_dict = {'id': inserted_id}
                        new_record = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
                        if new_record:
                            # Add to DATA_LIST
                            self.DATA_LIST.append(new_record[0])
                            self.BROWSE_STATUS = "b"
                            self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                            self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), len(self.DATA_LIST) - 1
                            self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
                            self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[self.REC_CORR]
                            # Refill fields with the saved record to ensure form state matches DB
                            self.fill_fields(self.REC_CORR)
                            self.setComboBoxEnable(["self.comboBox_sito"], "False")
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
                
                # First delete all related materials from tma_materiali_ripetibili
                try:
                    session = self.DB_MANAGER.engine.connect()
                    sql = text("DELETE FROM tma_materiali_ripetibili WHERE id_tma = :id_tma")
                    session.execute(sql, {"id_tma": id_to_delete})
                    session.close()
                    QgsMessageLog.logMessage(f"Deleted related materials for TMA id: {id_to_delete}", "PyArchInit", Qgis.Info)
                except Exception as e:
                    QgsMessageLog.logMessage(f"Error deleting related materials: {str(e)}", "PyArchInit", Qgis.Warning)
                
                # Then delete the main TMA record
                self.DB_MANAGER.delete_one_record(self.TABLE_NAME, self.ID_TABLE, id_to_delete)
                self.charge_list()
                self.charge_records()
                QMessageBox.warning(self, "Messaggio", "Record eliminato!", QMessageBox.Ok)
            except Exception as e:
                import traceback
                traceback.print_exc()
                QgsMessageLog.logMessage(f"ERROR deleting TMA record: {str(e)}", "PyArchInit", Qgis.Critical)
                QMessageBox.warning(self, "Errore", f"Errore nella cancellazione: {str(e)}", QMessageBox.Ok)

            if not bool(self.DATA_LIST):
                QgsMessageLog.logMessage(f"DEBUG TMA: Clearing DATA_LIST in charge_records\", \"PyArchInit\", Qgis.Info")
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
            else:
                # We're in the middle of the list
                self.REC_TOT = len(self.DATA_LIST)
                if self.REC_CORR >= self.REC_TOT:
                    self.REC_CORR = self.REC_TOT - 1
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

        # Keep site disabled during search
        self.setComboBoxEnable(["self.comboBox_sito"], "False")
        self.setComboBoxEditable(["self.comboBox_sito"], 0)

        self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
        self.set_rec_counter('', '')
        self.label_sort.setText(self.SORTED_ITEMS["n"])
        self.empty_fields()
        
        # Add empty row to materials table for search
        if self.tableWidget_materiali.rowCount() == 0:
            self.tableWidget_materiali.insertRow(0)

    def on_pushButton_search_go_pressed(self):
        """Execute search."""
        if self.BROWSE_STATUS != "f":
            QMessageBox.warning(self, "ATTENZIONE", "Per eseguire una nuova ricerca clicca sul pulsante 'new search'",
                                QMessageBox.Ok)
        else:
            search_dict = self.build_search_dict()
            materials_search = self.build_materials_search_dict()

            # DEBUG: Log the search dictionary
            QgsMessageLog.logMessage(f"DEBUG TMA Search: search_dict = {search_dict}", "PyArchInit", Qgis.Info)
            QgsMessageLog.logMessage(f"DEBUG TMA Search: materials_search = {materials_search}", "PyArchInit", Qgis.Info)

            if not bool(search_dict) and not bool(materials_search):
                QMessageBox.warning(self, "ATTENZIONE", "Non è stata impostata alcuna ricerca!", QMessageBox.Ok)
            else:
                # Check if we have a cassetta search - handle it specially
                cassetta_search = None
                if self.lineEdit_cassetta.text():
                    cassetta_search = str(self.lineEdit_cassetta.text()).strip()
                    # Remove cassetta from search_dict as we'll handle it separately
                    search_dict = {k: v for k, v in search_dict.items() if k != 'cassetta'}
                    QgsMessageLog.logMessage(f"DEBUG TMA: Special cassetta search for: '{cassetta_search}'", "PyArchInit", Qgis.Info)

                # First search TMA records (without cassetta)
                if search_dict:
                    # DEBUG: Log before query
                    QgsMessageLog.logMessage(f"DEBUG TMA: Executing query_bool with dict: {search_dict}", "PyArchInit", Qgis.Info)
                    res = self.DB_MANAGER.query_bool(search_dict, 'TMA')
                    QgsMessageLog.logMessage(f"DEBUG TMA: Query returned {len(res) if res else 0} results", "PyArchInit", Qgis.Info)
                else:
                    res = self.DB_MANAGER.query('TMA')

                # Now filter by cassetta if needed (respecting comma-space delimiters)
                if cassetta_search and res:
                    filtered_res = []
                    for tma in res:
                        if self._cassetta_contains_token(tma.cassetta, cassetta_search):
                            filtered_res.append(tma)
                    QgsMessageLog.logMessage(f"DEBUG TMA: Cassetta filter reduced {len(res)} to {len(filtered_res)} results", "PyArchInit", Qgis.Info)
                    res = filtered_res

                # Filter by materials if needed
                if materials_search and res:
                    filtered_res = []
                    for tma in res:
                        # Check if this TMA has materials matching our search
                        materials = self.DB_MANAGER.query_bool({'id_tma': int(tma.id)}, 'TMA_MATERIALI')
                        for mat in materials:
                            match = True
                            for field, value in materials_search.items():
                                mat_value = getattr(mat, field, None)
                                if mat_value and value.lower() not in str(mat_value).lower():
                                    match = False
                                    break
                            if match:
                                filtered_res.append(tma)
                                break
                    res = filtered_res

                if not bool(res):
                    QMessageBox.warning(self, "ATTENZIONE", "Non è stato trovato alcun record!", QMessageBox.Ok)

                    if self.DATA_LIST:  # Check if DATA_LIST is not empty before accessing index 0
                        self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                        self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                        self.fill_fields(self.REC_CORR)
                        self.BROWSE_STATUS = "b"
                        self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])

                        self.setComboBoxEnable(["self.comboBox_sito"], "False")

                else:
                    QgsMessageLog.logMessage(f"DEBUG TMA: Clearing DATA_LIST in charge_records\", \"PyArchInit\", Qgis.Info")
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
        path = '{}{}{}'.format(HOME, os.sep, "pyarchinit_PDF_folder")
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

    def _cassetta_contains_token(self, cassetta_value, search_token):
        """
        Check if a cassetta field contains the search token as a complete item.
        Respects comma-space delimiters.

        Examples:
        - "1, 2, C1" contains "1" but not "11"
        - "C1, C2, 11" contains "11" and "C1" but not "1"
        """
        if not cassetta_value:
            return False

        # Convert both to strings and clean up
        cassetta_str = str(cassetta_value).strip()
        search_str = str(search_token).strip()

        if not cassetta_str or not search_str:
            return False

        # Split by comma-space delimiter
        tokens = [token.strip() for token in cassetta_str.split(',')]

        # Check for exact token match (case-insensitive)
        for token in tokens:
            if token.lower() == search_str.lower():
                QgsMessageLog.logMessage(f"DEBUG TMA: Found token match '{search_str}' in '{cassetta_str}'", "PyArchInit", Qgis.Info)
                return True

        return False

    def build_search_dict(self):
        """Build search dictionary from form fields."""
        search_dict = {}

        if self.comboBox_sito.currentText() != "":
            search_dict['sito'] = "'" + str(self.comboBox_sito.currentText()) + "'"

        if self.comboBox_area.currentText() != "":
            search_dict['area'] = "'" + str(self.comboBox_area.currentText()) + "'"


        if self.comboBox_settore.currentText() != "":
            search_dict['settore'] = "'" + str(self.comboBox_settore.currentText()) + "'"

        if self.lineEdit_us.text() != "":
            search_dict['dscu'] = "'" + str(self.lineEdit_us.text()) + "'"

        # Note: materiale field has been moved to materials table

        if self.comboBox_ldcn.currentText() != "":
            search_dict['ldcn'] = "'" + str(self.comboBox_ldcn.currentText()) + "'"

        if self.lineEdit_cassetta.text() != "":
            # Note: cassetta is handled specially in on_pushButton_search_go_pressed
            # to respect comma-space delimiters (e.g., "1, 2, C1")
            # We include it here so the search method knows to handle it
            search_dict['cassetta'] = "'" + str(self.lineEdit_cassetta.text()).strip() + "'"


        if self.comboBox_dtzg.currentText() != "":
            search_dict['dtzg'] = "'" + str(self.comboBox_dtzg.currentText()) + "'"

        return search_dict
    
    def build_materials_search_dict(self):
        """Build search dictionary for materials table."""
        materials_search = {}
        
        # Check each cell in materials table for non-empty values
        for row in range(self.tableWidget_materiali.rowCount()):
            # madi (materiale)
            item = self.tableWidget_materiali.item(row, 0)
            if item and item.text():
                if 'madi' not in materials_search:
                    materials_search['madi'] = item.text()
            
            # macc (categoria)
            item = self.tableWidget_materiali.item(row, 1)
            if item and item.text():
                if 'macc' not in materials_search:
                    materials_search['macc'] = item.text()
            
            # macl (classe)
            item = self.tableWidget_materiali.item(row, 2)
            if item and item.text():
                if 'macl' not in materials_search:
                    materials_search['macl'] = item.text()
            
            # macp (precisazione)
            item = self.tableWidget_materiali.item(row, 3)
            if item and item.text():
                if 'macp' not in materials_search:
                    materials_search['macp'] = item.text()
            
            # macd (definizione)
            item = self.tableWidget_materiali.item(row, 4)
            if item and item.text():
                if 'macd' not in materials_search:
                    materials_search['macd'] = item.text()
        
        return materials_search

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
                str(self.comboBox_localita.currentText()),
                str(self.comboBox_settore.currentText()),
                str(self.lineEdit_inventario.text()),  # inventario field
                '',  # ogtm - materiale field has been moved to materials table
                str(self.comboBox_ldct.currentText()),
                str(self.comboBox_ldcn.currentText()),
                str(self.lineEdit_vecchia_collocazione.text()),
                str(self.lineEdit_cassetta.text()),
                str(self.comboBox_scan.currentText()),
                str(self.lineEdit_saggio.text()),
                str(self.lineEdit_vano_locus.text()),
                str(self.lineEdit_dscd.text()),
                str(self.lineEdit_us.text()),  # dscu
                str(self.lineEdit_rcgd.text()),
                str(self.textEdit_rcgz.toPlainText()),
                str(self.comboBox_aint.currentText()),
                str(self.lineEdit_aind.text()),
                str(self.comboBox_dtzg.currentText()),  # Single chronology field
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

            QgsMessageLog.logMessage(f"DEBUG TMA: About to insert data - Type: {type(data).__name__}", "PyArchInit", Qgis.Info)
            self.DB_MANAGER.insert_data_session(data)
            QgsMessageLog.logMessage(f"DEBUG TMA: Data inserted successfully", "PyArchInit", Qgis.Info)
            
            # Get the ID of the inserted record and save materials
            inserted_id = self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, self.ID_TABLE)
            QgsMessageLog.logMessage(f"DEBUG TMA: Inserted record ID: {inserted_id}", "PyArchInit", Qgis.Info)
            self.save_materials_data(inserted_id)
            
            return 1

        except Exception as e:
            QMessageBox.warning(self, "Error", "Problema nell'inserimento: " + str(e), QMessageBox.Ok)
            return 0

    def update_record_to_db(self):
        """Update current record in database."""
        try:
            # Check records before update
            from sqlalchemy import text
            from sqlalchemy.orm import sessionmaker
            Session = sessionmaker(bind=self.DB_MANAGER.engine)
            session = Session()
            
            count_before = session.execute(text("SELECT COUNT(*) FROM tma_materiali_archeologici")).scalar()
            QgsMessageLog.logMessage(f"DEBUG update_record_to_db: Records before update: {count_before}", "PyArchInit", Qgis.Info)
            session.close()
            
            # Get documentation data from tables
            ftap, ftan = self.get_foto_data()
            drat, dran, draa = self.get_disegni_data()

            # Update main TMA record
            self.set_LIST_REC_TEMP()  # This sets self.DATA_LIST_REC_TEMP
            current_id = eval("int(self.DATA_LIST[self.REC_CORR]." + self.ID_TABLE + ")")
            QgsMessageLog.logMessage(f"DEBUG update_record_to_db: Updating TMA ID {current_id}", "PyArchInit", Qgis.Info)
            
            self.DB_MANAGER.update(self.MAPPER_TABLE_CLASS,
                                   self.ID_TABLE,
                                   [current_id],
                                   self.TABLE_FIELDS,
                                   self.DATA_LIST_REC_TEMP)
            
            # Check records after update
            session = Session()
            count_after = session.execute(text("SELECT COUNT(*) FROM tma_materiali_archeologici")).scalar()
            QgsMessageLog.logMessage(f"DEBUG update_record_to_db: Records after update: {count_after}", "PyArchInit", Qgis.Info)
            
            if count_after < count_before:
                QgsMessageLog.logMessage(f"ERROR: Records deleted during update! Before: {count_before}, After: {count_after}", "PyArchInit", Qgis.Critical)
            
            session.close()
            
            # Save materials data for updated record
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
                'sito': "'" + str(sito) + "'",
                'area': "'" + str(area) + "'",
                'us': "'" + str(us) + "'",
                'repertato': "'" + 'Si' + "'"
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
        """Handle US field change - only updates inventory."""
        # Update inventory field when US changes
        self.update_inventory_field()
    
    def on_localita_changed(self):
        """Handle località field change to filter area and reset settore."""
        # Skip if we're loading data to avoid clearing restored values
        if hasattr(self, 'loading_data') and self.loading_data:
            return
        # When località changes, reset area and settore
        self.comboBox_area.clear()
        self.comboBox_settore.clear()
        # Filter area based on selected località
        self.filter_area_by_localita()
        self.update_inventory_field()
    
    def on_area_changed(self):
        """Handle area field change to update inventory and filter settore."""
        # Skip if we're loading data to avoid clearing restored values
        if hasattr(self, 'loading_data') and self.loading_data:
            return
        self.update_inventory_field()
        # Filter settore based on selected area
        self.filter_settore_by_area()
    
    def on_sito_changed(self):
        try:
            """Handle site field change to update inventory and reset location fields."""
            # Skip if we're loading data to avoid clearing restored values
            if hasattr(self, 'loading_data') and self.loading_data:
                return
            self.update_inventory_field()
            # When site changes, reset area and settore
            self.comboBox_area.clear()
            self.comboBox_settore.clear()
            # Reload all areas for the new site context
            self.load_area_values()

        except Exception as e:
            QgsMessageLog.logMessage(f"Error filtering areas: {str(e)}", "PyArchInit", Qgis.Warning)
            self.load_area_values()
    
    def filter_area_by_localita(self):
        """Filter area options based on selected località."""
        if not self.DB_MANAGER or self.DB_MANAGER == "":
            return
            
        current_localita = self.comboBox_localita.currentText()
        if not current_localita:
            # If no località selected, load all areas
            self.load_area_values()
            return
            
        try:
            # Get località sigla from extended name
            search_dict = {
                'nome_tabella': "'" + 'TMA materiali archeologici' + "'",
                'tipologia_sigla': "'" + '10.3' + "'",
                'sigla_estesa': "'" + str(current_localita) + "'"
            }
            localita_res = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
            
            if localita_res:
                localita_sigla = localita_res[0].sigla
                
                # Get areas that belong to this località
                search_dict_area = {
                    'nome_tabella': 'TMA materiali archeologici',
                    'tipologia_sigla': "'10.7'",
                    'parent_sigla': f"'{localita_sigla}'"
                }
                area_res = self.DB_MANAGER.query_bool(search_dict_area, 'PYARCHINIT_THESAURUS_SIGLE')
                
                # Update area combobox
                self.comboBox_area.clear()
                area_values = []
                for area in area_res:
                    area_values.append(str(area.sigla_estesa))
                area_values.sort()
                self.comboBox_area.addItems(area_values)
            else:
                # If località not found in thesaurus, load all areas
                self.load_area_values()
                
        except Exception as e:
            QgsMessageLog.logMessage(f"Error filtering area: {str(e)}", "PyArchInit", Qgis.Warning)
            self.load_area_values()
    
    def filter_settore_by_area(self):
        """Filter settore options based on selected area."""
        if not self.DB_MANAGER or self.DB_MANAGER == "":
            return

        # Store current settore value before clearing
        current_settore = self.comboBox_settore.currentText()

        current_area = self.comboBox_area.currentText()
        if not current_area:
            # If no area selected, clear settore
            self.comboBox_settore.clear()
            return

        try:
            # Get area sigla from extended name
            search_dict = {
                'nome_tabella': "'" + 'TMA materiali archeologici' + "'",
                'tipologia_sigla': "'" + '10.7' + "'",
                'sigla_estesa': "'" + str(current_area) + "'"
            }
            area_res = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')

            if area_res:
                area_sigla = area_res[0].sigla

                # Get settori that belong to this area
                search_dict_settore = {
                    'nome_tabella': 'TMA materiali archeologici',
                    'tipologia_sigla': "'10.15'",
                    'parent_sigla': f"'{area_sigla}'"
                }
                settore_res = self.DB_MANAGER.query_bool(search_dict_settore, 'PYARCHINIT_THESAURUS_SIGLE')

                # Update settore combobox
                self.comboBox_settore.clear()
                settore_values = []
                for settore in settore_res:
                    settore_values.append(str(settore.sigla_estesa))
                settore_values.sort()
                self.comboBox_settore.addItems(settore_values)

                # Restore the previous settore value if it exists in the new list
                # Otherwise, keep it empty (don't auto-select first item)
                if current_settore and current_settore in settore_values:
                    self.comboBox_settore.setEditText(current_settore)
                else:
                    # Force empty selection
                    self.comboBox_settore.setEditText("")
                    self.comboBox_settore.setCurrentIndex(-1)
            else:
                # If area not found in thesaurus, load all settori
                self.load_settore_values()
                # Keep settore empty if it was empty
                if not current_settore:
                    self.comboBox_settore.setEditText("")
                    self.comboBox_settore.setCurrentIndex(-1)

        except Exception as e:
            QgsMessageLog.logMessage(f"Error filtering settore: {str(e)}", "PyArchInit", Qgis.Warning)
            self.load_settore_values()
            # Keep settore empty if it was empty
            if not current_settore:
                self.comboBox_settore.setEditText("")
                self.comboBox_settore.setCurrentIndex(-1)
    
    def load_area_values(self):
        """Load all area values from thesaurus."""

        l = QgsSettings().value("locale/userLocale", QVariant)[0:2]
        lang = ""
        for key, values in self.LANG.items():
            if values.__contains__(l):
                lang = str(key)
        lang = "'" + lang + "'"
        
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'TMA materiali archeologici' + "'",
            'tipologia_sigla': "'" + '10.7' + "'"  # Area code
        }
        area_vl_thesaurus = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        area_vl = []
        for s in area_vl_thesaurus:
            area_vl.append(str(s.sigla_estesa))
        area_vl.sort()
        self.comboBox_area.clear()
        self.comboBox_area.addItems(area_vl)
    
    def load_settore_values(self):
        """Load all settore values from thesaurus."""
        # Store current settore value before clearing
        current_settore = self.comboBox_settore.currentText()

        search_dict = {
            'nome_tabella': "'" + 'TMA materiali archeologici' + "'",
            'tipologia_sigla': "'" + '10.15' + "'"
        }
        settore_res = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        settore_values = []
        for s in settore_res:
            settore_values.append(str(s.sigla_estesa))
        settore_values.sort()
        self.comboBox_settore.clear()
        self.comboBox_settore.addItems(settore_values)

        # Restore settore value if it was empty, keep it empty
        if not current_settore:
            self.comboBox_settore.setEditText("")
            self.comboBox_settore.setCurrentIndex(-1)
    
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
                'sito': "'" + str(sito) + "'",
                'area': "'" + str(area) + "'",
                'us': "'" + str(us) + "'",
                'repertato': "'" + 'Si' + "'"
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
            lang = QgsSettings().value("locale/userLocale", "it")[:2].upper()  # Use uppercase as in database
            
            # Map field types to thesaurus categories
            # Using correct tipologia_sigla codes according to thesaurus structure
            thesaurus_map = {
                'categoria': '10.10',   # Categoria materiale (ceramica, vetro, metallo, etc.)
                'classe': '10.11',      # Classe (ceramica fine, grezza, etc.)
                'tipologia': '10.12',   # Precisazione tipologica
                'definizione': '10.13', # Definizione
                'cronologia_mac': '10.4'  # Cronologia (Neolitico, Minoico, etc.)
            }
            
            if field_type not in thesaurus_map:
                return []
            
            # Use correct table name for thesaurus lookup
            # Material fields use TMA Materiali Ripetibili table (with capitals)
            table_name = 'TMA Materiali Ripetibili'
            
            search_dict = {
                'lingua': "'" + str(lang) + "'",  # Add quotes around language code
                'nome_tabella': "'" + str(table_name) + "'",
                'tipologia_sigla': "'" + str(thesaurus_map[field_type]) + "'"
            }
            
            # DEBUG: Log the exact query
            QgsMessageLog.logMessage(f"DEBUG TMA thesaurus query: search_dict = {search_dict}", "PyArchInit", Qgis.Info)
            QgsMessageLog.logMessage(f"DEBUG TMA thesaurus: lang = '{lang}', type = {type(lang)}", "PyArchInit", Qgis.Info)
            QgsMessageLog.logMessage(f"DEBUG TMA thesaurus: table_name = '{table_name}', type = {type(table_name)}", "PyArchInit", Qgis.Info)
            QgsMessageLog.logMessage(f"DEBUG TMA thesaurus: tipologia_sigla = '{thesaurus_map[field_type]}', type = {type(thesaurus_map[field_type])}", "PyArchInit", Qgis.Info)
            
            thesaurus_records = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
            
            # DEBUG: Check what was returned
            QgsMessageLog.logMessage(f"DEBUG TMA thesaurus result: type = {type(thesaurus_records)}, len = {len(thesaurus_records) if thesaurus_records else 0}", "PyArchInit", Qgis.Info)
            values = []
            
            QgsMessageLog.logMessage(f"DEBUG load_thesaurus_values: field={field_type}, table={table_name}, code={thesaurus_map[field_type]}, records found={len(thesaurus_records)}", "PyArchInit", Qgis.Info)
            
            for record in thesaurus_records:
                if hasattr(record, 'sigla_estesa') and record.sigla_estesa:
                    values.append(record.sigla_estesa)
            
            values.sort()
            return values
            
        except Exception as e:
            # Return empty list if thesaurus not available
            return []
    

    
    def setup_materials_table_with_thesaurus(self):
        """Setup materials table with thesaurus support using delegates."""
        
        # Setup base table
        self.setup_materials_table()
        
        # Load thesaurus values for each column that needs it
        # Note: We removed 'materiale' as it's no longer a column in the table
        categoria_values = []
        classe_values = []
        tipologia_values = []
        definizione_values = []
        cronologia_values = []
        
        # Only load thesaurus if DB_MANAGER is connected
        if self.DB_MANAGER and self.DB_MANAGER != "":
            categoria_values = self.load_thesaurus_values('categoria')
            classe_values = self.load_thesaurus_values('classe')
            tipologia_values = self.load_thesaurus_values('tipologia')
            definizione_values = self.load_thesaurus_values('definizione')
            cronologia_values = self.load_thesaurus_values('cronologia_mac')
        
        # Don't use default values - only use thesaurus values
        
        # Debug print
        QgsMessageLog.logMessage(f"DEBUG TMA THESAURUS: Categoria values: {len(categoria_values)} items", "PyArchInit", Qgis.Info)
        QgsMessageLog.logMessage(f"DEBUG TMA THESAURUS: Classe values: {len(classe_values)} items", "PyArchInit", Qgis.Info)
        QgsMessageLog.logMessage(f"DEBUG TMA THESAURUS: Tipologia values: {len(tipologia_values)} items", "PyArchInit", Qgis.Info)
        QgsMessageLog.logMessage(f"DEBUG TMA THESAURUS: Definizione values: {len(definizione_values)} items", "PyArchInit", Qgis.Info)
        QgsMessageLog.logMessage(f"DEBUG TMA THESAURUS: Cronologia values: {len(cronologia_values)} items", "PyArchInit", Qgis.Info)
        
        # Set delegates for columns with thesaurus support
        if categoria_values:
            self.delegateCategoria = ComboBoxDelegate()
            self.delegateCategoria.def_values(categoria_values)
            self.delegateCategoria.def_editable('True')
            self.tableWidget_materiali.setItemDelegateForColumn(0, self.delegateCategoria)
            QgsMessageLog.logMessage(f"DEBUG TMA: Set delegate for Categoria column with {len(categoria_values)} values", "PyArchInit", Qgis.Info)
        if classe_values:
            self.delegateClasse = ComboBoxDelegate()
            self.delegateClasse.def_values(classe_values)
            self.delegateClasse.def_editable('True')
            self.tableWidget_materiali.setItemDelegateForColumn(1, self.delegateClasse)
            QgsMessageLog.logMessage(f"DEBUG TMA: Set delegate for Classe column with {len(classe_values)} values", "PyArchInit", Qgis.Info)
        if tipologia_values:
            self.delegateTipologia = ComboBoxDelegate()
            self.delegateTipologia.def_values(tipologia_values)
            self.delegateTipologia.def_editable('True')
            self.tableWidget_materiali.setItemDelegateForColumn(2, self.delegateTipologia)
            QgsMessageLog.logMessage(f"DEBUG TMA: Set delegate for Tipologia column with {len(tipologia_values)} values", "PyArchInit", Qgis.Info)
        if definizione_values:
            self.delegateDefinizione = ComboBoxDelegate()
            self.delegateDefinizione.def_values(definizione_values)
            self.delegateDefinizione.def_editable('True')
            self.tableWidget_materiali.setItemDelegateForColumn(3, self.delegateDefinizione)
            QgsMessageLog.logMessage(f"DEBUG TMA: Set delegate for Definizione column with {len(definizione_values)} values", "PyArchInit", Qgis.Info)
        if cronologia_values:
            self.delegateCronologia = ComboBoxDelegate()
            self.delegateCronologia.def_values(cronologia_values)
            self.delegateCronologia.def_editable('True')
            self.tableWidget_materiali.setItemDelegateForColumn(4, self.delegateCronologia)
            QgsMessageLog.logMessage(f"DEBUG TMA: Set delegate for Cronologia column with {len(cronologia_values)} values", "PyArchInit", Qgis.Info)
        

        
        # Setup delegates for documentation tables
        self.setup_documentation_delegates()
    
    def setup_documentation_delegates(self):
        """Setup delegates for photo and drawing documentation tables."""
        
        # Load photo types from thesaurus
        ftap_values = []
        if self.DB_MANAGER and self.DB_MANAGER != "":
            search_dict = {
                'lingua': "'" + 'it' + "'",  # Use lowercase
                'nome_tabella': "'" + 'TMA materiali archeologici' + "'",
                'tipologia_sigla': "'" + '10.9' + "'"
            }
            ftap_res = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
            for rec in ftap_res:
                if hasattr(rec, 'sigla_estesa') and rec.sigla_estesa:
                    ftap_values.append(str(rec.sigla_estesa))
            ftap_values.sort()
        
        # If we have photo types, set delegate for first column of photo table
        if ftap_values and hasattr(self, 'tableWidget_foto'):
            self.delegateFotoTipo = ComboBoxDelegate()
            self.delegateFotoTipo.def_values(ftap_values)
            self.delegateFotoTipo.def_editable('True')
            self.tableWidget_foto.setItemDelegateForColumn(0, self.delegateFotoTipo)
            QgsMessageLog.logMessage(f"DEBUG TMA: Set delegate for Photo Type column with {len(ftap_values)} values", "PyArchInit", Qgis.Info)
        
        # For drawings, we might need drawing types from thesaurus too
        # Currently using free text, but could be enhanced
        
        # Load drawing types from thesaurus if available
        drat_values = []
        if self.DB_MANAGER and self.DB_MANAGER != "":
            # Assumiamo che ci sia un tipo per i disegni (es. 10.16)
            # Per ora usiamo valori predefiniti
            drat_values = ["pianta", "sezione", "prospetto", "assonometria", "dettaglio", "schizzo"]
        
        # Set delegate for drawing type column if we have values
        if drat_values and hasattr(self, 'tableWidget_disegni'):
            self.delegateDisegniTipo = ComboBoxDelegate()
            self.delegateDisegniTipo.def_values(drat_values)
            self.delegateDisegniTipo.def_editable('True')
            self.tableWidget_disegni.setItemDelegateForColumn(0, self.delegateDisegniTipo)
            QgsMessageLog.logMessage(f"DEBUG TMA: Set delegate for Drawing Type column with {len(drat_values)} values", "PyArchInit", Qgis.Info)

            # Connect signal to track table changes
        self.tableWidget_materiali.itemChanged.connect(self.on_materials_table_changed)
        
        # Flag to track materials changes
        self.materials_modified = False
    
    def on_materials_table_changed(self, item):
        """Called when an item in the materials table is changed."""
        # Don't mark as modified if we're loading materials
        if hasattr(self, '_loading_materials') and self._loading_materials:
            QgsMessageLog.logMessage(f"DEBUG on_materials_table_changed: Ignoring change during loading - row={item.row()}, col={item.column()}", "PyArchInit", Qgis.Info)
            return
            
        # Only log meaningful changes (non-empty text)
        if item.text().strip():
            QgsMessageLog.logMessage(f"DEBUG TMA: Materials table changed - row={item.row()}, col={item.column()}, text='{item.text()}'", "PyArchInit", Qgis.Info)
        self.materials_modified = True
        QgsMessageLog.logMessage(f"DEBUG on_materials_table_changed: Set materials_modified=True", "PyArchInit", Qgis.Info)
        
        # Update tooltip to match the new content
        item.setToolTip(item.text())
        
        # Update materiale field when first column (Categoria) changes
        if item.column() == 0:  # Categoria column (now syncs to ogtm)
            self.update_materiale_field()
    
    def update_materiale_field(self):
        """Update the lineEdit_materiale field with all categories from the table."""
        materials_list = []
        for row in range(self.tableWidget_materiali.rowCount()):
            material_item = self.tableWidget_materiali.item(row, 0)  # Categoria column (now first column)
            if material_item and material_item.text().strip():
                materials_list.append(material_item.text().strip())
        
        # Update the lineEdit_materiale with comma-separated categories (syncs to ogtm)
        self.lineEdit_materiale.setText(", ".join(materials_list))
    
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
        #self.tabWidget.addTab(self.mapPreview, "Map preview")
    
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
                    'entity_type': "'" + 'TMA' + "'"
                }
                
                media_data = self.DB_MANAGER.query_bool(search_dict, 'MEDIATOENTITY')
                
                for media in media_data:
                    # Get thumbnail data
                    thumb_search = {'media_filename': "'" + str(media.media_name) + "'"}
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
                search_dict = {'filename': "'" + str(item_data) + "'"}
                
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
                'entity_type': "'" + 'TMA' + "'",
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
                'entity_type': "'" + 'TMA' + "'",
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
                QgsMessageLog.logMessage(f"DEBUG TMA: About to insert data - Type: {type(data).__name__}", "PyArchInit", Qgis.Info)
                self.DB_MANAGER.insert_data_session(data)
                QgsMessageLog.logMessage(f"DEBUG TMA: Data inserted successfully", "PyArchInit", Qgis.Info)
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
        # Initialize filter states
        self.filter_settings = {
            'sito': False,
            'area': False,
            'us': False,
            'cassetta': False,
            'materiale': False,
            'categoria': False,
            'materiale_value': '',
            'categoria_value': ''
        }
            
        # Create dialog for print options
        dialog = QDialog(self)
        dialog.setWindowTitle("Opzioni di stampa TMA")
        dialog.resize(400, 350)
        
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
        
        self.radio_all = QRadioButton("Stampa tutte le schede TMA")
        layout.addWidget(self.radio_all)
        
        # Filters group (enabled only when list is selected)
        filters_group = QGroupBox("Filtri per lista")
        filters_layout = QVBoxLayout()
        
        self.check_filter_cassetta = QCheckBox("Filtra per cassetta corrente")
        self.check_filter_us = QCheckBox("Filtra per US corrente")
        self.check_filter_area = QCheckBox("Filtra per area corrente")
        self.check_filter_sito = QCheckBox("Filtra per sito corrente")
        self.check_filter_materiale = QCheckBox("Filtra per materiale specifico")
        self.check_filter_categoria = QCheckBox("Filtra per categoria")
        
        # ComboBox for material filter
        self.combo_filter_materiale = QComboBox()
        self.combo_filter_materiale.setEnabled(False)
        self.check_filter_materiale.toggled.connect(self.combo_filter_materiale.setEnabled)
        
        # ComboBox for category filter
        self.combo_filter_categoria = QComboBox()
        self.combo_filter_categoria.setEnabled(False)
        self.check_filter_categoria.toggled.connect(self.combo_filter_categoria.setEnabled)
        
        filters_layout.addWidget(self.check_filter_cassetta)
        filters_layout.addWidget(self.check_filter_us)
        filters_layout.addWidget(self.check_filter_area)
        filters_layout.addWidget(self.check_filter_sito)
        filters_layout.addWidget(self.check_filter_materiale)
        filters_layout.addWidget(self.combo_filter_materiale)
        filters_layout.addWidget(self.check_filter_categoria)
        filters_layout.addWidget(self.combo_filter_categoria)
        
        filters_group.setLayout(filters_layout)
        layout.addWidget(filters_group)
        
        # Font size option for list printing
        font_group = QGroupBox("Opzioni di visualizzazione")
        font_layout = QHBoxLayout()
        
        font_label = QLabel("Dimensione font:")
        self.spin_font_size = QSpinBox()
        self.spin_font_size.setMinimum(6)
        self.spin_font_size.setMaximum(14)
        self.spin_font_size.setValue(8)  # Default value
        self.spin_font_size.setSuffix(" pt")
        
        font_layout.addWidget(font_label)
        font_layout.addWidget(self.spin_font_size)
        font_layout.addStretch()
        
        font_group.setLayout(font_layout)
        layout.addWidget(font_group)
        
        # Enable/disable filters based on radio selection
        def toggle_filters():
            enabled = self.radio_list.isChecked()
            filters_group.setEnabled(enabled)
            font_group.setEnabled(enabled)  # Enable font options only for list
            
            # Re-apply the individual combobox states when filters are enabled
            if enabled:
                self.combo_filter_materiale.setEnabled(self.check_filter_materiale.isChecked())
                self.combo_filter_categoria.setEnabled(self.check_filter_categoria.isChecked())
            
        self.radio_single.toggled.connect(toggle_filters)
        self.radio_list.toggled.connect(toggle_filters)
        toggle_filters()
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        # Populate filter combos before showing dialog
        self.populate_filter_combos()
        
        # Execute dialog
        if dialog.exec_() == QDialog.Accepted:
            # Save font size
            self.selected_font_size = self.spin_font_size.value()
            
            # Save filter settings
            self.filter_settings['sito'] = self.check_filter_sito.isChecked()
            self.filter_settings['area'] = self.check_filter_area.isChecked()
            self.filter_settings['us'] = self.check_filter_us.isChecked()
            self.filter_settings['cassetta'] = self.check_filter_cassetta.isChecked()
            self.filter_settings['materiale'] = self.check_filter_materiale.isChecked()
            self.filter_settings['categoria'] = self.check_filter_categoria.isChecked()
            self.filter_settings['materiale_value'] = self.combo_filter_materiale.currentText()
            self.filter_settings['categoria_value'] = self.combo_filter_categoria.currentText()
            
            if self.radio_single.isChecked():
                self.print_single_tma()
            elif self.radio_all.isChecked():
                # Print all records without filters
                self.print_all_tma()
            else:
                self.print_tma_list()
    
    def populate_filter_combos(self):
        """Populate filter combo boxes with unique values from database."""
        try:
            # Get all materials from database
            all_materials = self.DB_MANAGER.query('TMA_MATERIALI')
            
            # Extract unique values
            materiali_set = set()
            categorie_set = set()
            
            for mat in all_materials:
                if mat.madi:
                    materiali_set.add(str(mat.madi))
                if mat.macc:
                    categorie_set.add(str(mat.macc))
            
            # Populate combos
            self.combo_filter_materiale.clear()
            self.combo_filter_materiale.addItem("")  # Empty option
            self.combo_filter_materiale.addItems(sorted(materiali_set))
            
            self.combo_filter_categoria.clear()
            self.combo_filter_categoria.addItem("")  # Empty option
            self.combo_filter_categoria.addItems(sorted(categorie_set))
            
        except Exception as e:
            QgsMessageLog.logMessage(f"Error populating filter combos: {str(e)}", "PyArchInit", Qgis.Warning)
    
    def print_single_tma(self):
        """Print single TMA record."""
        # Simply call the existing export method
        self.on_pushButton_export_pdf_pressed()
    
    def print_all_tma(self):
        """Print all TMA records to PDF."""
        try:
            # Get all TMA records
            tma_list = self.DB_MANAGER.query('TMA')
            
            if not tma_list:
                QMessageBox.warning(self, "Attenzione", "Nessun record TMA trovato nel database", QMessageBox.Ok)
                return
            
            # Generate PDF for all records
            from ..modules.utility.pyarchinit_exp_Tmasheet_pdf import generate_tma_pdf
            
            # Generate PDF for each TMA record
            for tma in tma_list:
                pdf_generator = generate_tma_pdf([tma])
                pdf_generator.create_sheet()
            
            HOME = os.environ['PYARCHINIT_HOME']
            PDF_path = os.path.join(HOME, "pyarchinit_PDF_folder")
            msg = f"Tutte le schede TMA esportate in:\n{PDF_path}\n\nTotale schede: {len(tma_list)}"
            QMessageBox.information(self, "Esportazione completata", msg, QMessageBox.Ok)
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore nella generazione del PDF: {str(e)}", QMessageBox.Ok)

    def print_tma_list(self):
        """Print filtered TMA list."""
        # Import PDF generator
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet
        
        # Get font size from dialog (default to 8 if not set)
        font_size = getattr(self, 'selected_font_size', 8)
        
        try:
            # Check if we should print all records or current only
            print_all = False
            if hasattr(self, 'radio_list') and self.radio_list.isChecked():
                # Build search filters
                search_dict = {}
                
                if self.filter_settings['sito'] and self.comboBox_sito.currentText():
                    search_dict['sito'] = "'" + str(self.comboBox_sito.currentText()) + "'"
                    
                if self.filter_settings['area'] and self.comboBox_area.currentText():
                    search_dict['area'] = "'" + str(self.comboBox_area.currentText()) + "'"
                    
                if self.filter_settings['us'] and self.lineEdit_us.text():
                    search_dict['dscu'] = "'" + str(self.lineEdit_us.text()) + "'"
                    
                if self.filter_settings['cassetta'] and self.lineEdit_cassetta.text():
                    # Use LIKE for partial matching in cassetta field
                    search_text = str(self.lineEdit_cassetta.text()).strip()
                    search_dict['cassetta'] = "LIKE '%%" + search_text + "%%'"
                
                # Query TMA records
                if search_dict:
                    tma_list = self.DB_MANAGER.query_bool(search_dict, 'TMA')
                else:
                    tma_list = self.DB_MANAGER.query('TMA')
            else:
                # Use currently loaded data
                tma_list = self.DATA_LIST
            
            if not tma_list:
                QMessageBox.warning(self, "Attenzione", "Nessun record trovato con i filtri specificati", QMessageBox.Ok)
                return
            
            # Prepare data for list
            data_list = []
            
            # Check if we have material/category filters active
            has_material_filter = self.filter_settings.get('materiale', False) and self.filter_settings.get('materiale_value', '')
            has_category_filter = self.filter_settings.get('categoria', False) and self.filter_settings.get('categoria_value', '')
            
            for tma in tma_list:
                # Get materials for this TMA
                materials = self.DB_MANAGER.query_bool({'id_tma': int(tma.id)}, 'TMA_MATERIALI')
                
                # Process each material or create single row if no materials
                if materials:
                    for mat in materials:
                        # Apply material/category filters if selected
                        include_row = True
                        
                        if has_material_filter:
                            mat_val = str(mat.madi) if mat.madi else ''
                            if self.filter_settings['materiale_value'] != mat_val:
                                include_row = False
                        
                        if has_category_filter and include_row:
                            cat_val = str(mat.macc) if mat.macc else ''
                            if self.filter_settings['categoria_value'] != cat_val:
                                include_row = False
                        
                        if include_row:
                            row_data = [
                                str(tma.sito),
                                str(tma.area),
                                str(tma.dscu) if tma.dscu else '',
                                str(tma.cassetta),
                                str(tma.dtzg) if tma.dtzg else '',  # Fascia cronologica
                                str(mat.madi) if mat.madi else '',  # Materiale
                                str(mat.macc) if mat.macc else '',  # Categoria
                                str(mat.macl) if mat.macl else '',  # Classe
                                str(mat.macd) if mat.macd else '',  # Definizione
                                str(mat.macq) if mat.macq else '',  # Quantità
                                str(mat.peso) if mat.peso else ''   # Peso
                            ]
                            data_list.append(row_data)
                else:
                    # Only add TMA without materials if no material/category filters are active
                    if not has_material_filter and not has_category_filter:
                        row_data = [
                            str(tma.sito),
                            str(tma.area),
                            str(tma.dscu) if tma.dscu else '',
                            str(tma.cassetta),
                            str(tma.dtzg) if tma.dtzg else '',  # Fascia cronologica
                            '', '', '', '', '', ''  # Empty material fields
                        ]
                        data_list.append(row_data)
            
            if not data_list:
                QMessageBox.warning(self, "Attenzione", "Nessun record trovato con i filtri specificati", QMessageBox.Ok)
                return
            
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
            
            # Add filter info
            filter_info = []
            if has_material_filter:
                filter_info.append(f"Materiale: {self.filter_settings['materiale_value']}")
            if has_category_filter:
                filter_info.append(f"Categoria: {self.filter_settings['categoria_value']}")
            if filter_info:
                elements.append(Paragraph(f"Filtri applicati: {', '.join(filter_info)}", styles['Normal']))
            
            elements.append(Paragraph("<br/><br/>", styles['Normal']))
            
            # Create style for table cells
            from reportlab.lib.styles import ParagraphStyle
            cell_style = ParagraphStyle(
                'CellStyle',
                parent=styles['Normal'],
                fontSize=font_size,
                leading=font_size * 1.2,  # Line spacing
                alignment=0  # Left align
            )
            
            # Create table with headers
            headers = ['Località', 'Area', 'US', 'Cassetta', 'Fascia cronologica', 'Materiale', 'Categoria', 'Classe', 'Definizione', 'Quantità', 'Peso']
            
            # Convert data to Paragraph objects for proper text wrapping
            table_data = [headers]  # Headers remain as strings
            for row in data_list:
                para_row = []
                for cell in row:
                    # Convert each cell to Paragraph for wrapping
                    if cell and str(cell).strip():
                        para_row.append(Paragraph(str(cell), cell_style))
                    else:
                        para_row.append('')
                table_data.append(para_row)
            
            # Create table with column widths optimized for landscape A4
            # Calculate column widths based on content and font size
            # Base widths for font size 8, adjusted proportionally
            base_widths = [50, 40, 30, 50, 70, 60, 60, 50, 80, 40, 40]
            width_factor = font_size / 8.0  # Adjust widths based on font size
            col_widths = [int(w * width_factor) for w in base_widths]
            
            # Ensure total width doesn't exceed page width (landscape A4 = ~800 points)
            total_width = sum(col_widths)
            if total_width > 750:  # Leave some margin
                scale_factor = 750.0 / total_width
                col_widths = [int(w * scale_factor) for w in col_widths]
            
            table = Table(table_data, colWidths=col_widths)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),  # Center headers
                ('ALIGN', (0, 1), (-1, -1), 'LEFT'),   # Left align data
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), font_size + 1),  # Header font size
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 1), (-1, -1), 4),   # Top padding for data cells
                ('BOTTOMPADDING', (0, 1), (-1, -1), 4), # Bottom padding for data cells
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),   # Top align for wrapping text
                ('LEFTPADDING', (0, 0), (-1, -1), 3),  # Reduced padding
                ('RIGHTPADDING', (0, 0), (-1, -1), 3),  # Reduced padding
                # Alternate row colors
                *[('BACKGROUND', (0, i), (-1, i), colors.white if i % 2 == 0 else colors.lightgrey) 
                  for i in range(1, len(table_data))],
            ]))
            
            elements.append(table)
            
            # Build PDF
            doc.build(elements)
            
            msg = f"Lista TMA esportata in:\n{filepath}\n\nTotale record: {len(data_list)}"
            QMessageBox.information(self, "Esportazione completata", msg, QMessageBox.Ok)
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore nella generazione del PDF: {str(e)}", QMessageBox.Ok)
    
    def on_pushButton_export_labels_pressed(self):
        """Handle label export button click."""
        # Create dialog for label export options
        dialog = QDialog(self)
        dialog.setWindowTitle("Esportazione Etichette TMA")
        dialog.resize(450, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Title
        title = QLabel("<h3>Esportazione Etichette</h3>")
        layout.addWidget(title)
        
        # Export type
        export_group = QGroupBox("Tipo di esportazione")
        export_layout = QVBoxLayout()
        
        self.radio_label_single = QRadioButton("Etichetta singola (record corrente)")
        self.radio_label_single.setChecked(True)
        self.radio_label_list = QRadioButton("Etichette lista filtrata")
        self.radio_label_all = QRadioButton("Tutte le etichette TMA")
        
        export_layout.addWidget(self.radio_label_single)
        export_layout.addWidget(self.radio_label_list)
        export_layout.addWidget(self.radio_label_all)
        export_group.setLayout(export_layout)
        layout.addWidget(export_group)
        
        # Label format
        format_group = QGroupBox("Formato etichetta")
        format_layout = QVBoxLayout()
        
        self.combo_label_format = QComboBox()
        self.combo_label_format.addItems([
            "70x37mm (3x8 per foglio)",
            "105x57mm (2x5 per foglio)",
            "210x297mm (Foglio singolo)",
            "99.1x38.1mm - Avery L7163",
            "63.5x38.1mm - Avery L7160"
        ])
        format_layout.addWidget(QLabel("Formato:"))
        format_layout.addWidget(self.combo_label_format)
        
        # Label style
        self.combo_label_style = QComboBox()
        self.combo_label_style.addItems(["Standard", "Minimale", "Dettagliata", "QR Minimale"])
        format_layout.addWidget(QLabel("Stile:"))
        format_layout.addWidget(self.combo_label_style)
        
        format_group.setLayout(format_layout)
        layout.addWidget(format_group)
        
        # Filters (for list export)
        filters_group = QGroupBox("Filtri per lista")
        filters_layout = QVBoxLayout()
        
        self.check_label_cassetta = QCheckBox("Filtra per cassetta corrente")
        self.check_label_us = QCheckBox("Filtra per US corrente")
        self.check_label_area = QCheckBox("Filtra per area corrente")
        self.check_label_sito = QCheckBox("Filtra per sito corrente")
        
        filters_layout.addWidget(self.check_label_cassetta)
        filters_layout.addWidget(self.check_label_us)
        filters_layout.addWidget(self.check_label_area)
        filters_layout.addWidget(self.check_label_sito)
        
        filters_group.setLayout(filters_layout)
        layout.addWidget(filters_group)
        
        # Enable/disable filters based on selection
        def toggle_label_filters():
            enabled = self.radio_label_list.isChecked()
            filters_group.setEnabled(enabled)
            
        self.radio_label_single.toggled.connect(toggle_label_filters)
        toggle_label_filters()
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        # Execute dialog
        if dialog.exec_() == QDialog.Accepted:
            # Get selected format
            format_map = {
                0: 'single_70x37',
                1: 'single_105x57',
                2: 'single_210x297',
                3: 'avery_l7163',
                4: 'avery_l7160'
            }
            label_format = format_map[self.combo_label_format.currentIndex()]
            
            # Get style
            style_map = {0: 'standard', 1: 'minimal', 2: 'detailed', 3: 'qr_minimal'}
            label_style = style_map[self.combo_label_style.currentIndex()]
            
            if self.radio_label_single.isChecked():
                self.export_single_label(label_format, label_style)
            elif self.radio_label_all.isChecked():
                self.export_all_labels(label_format, label_style)
            else:
                self.export_filtered_labels(label_format, label_style)
    
    def export_single_label(self, label_format, label_style):
        """Export single label for current record."""
        try:
            if not self.DATA_LIST or self.REC_CORR < 0:
                QMessageBox.warning(self, "Attenzione", "Nessun record corrente da esportare", QMessageBox.Ok)
                return
                
            # Get current record
            current_tma = self.DATA_LIST[self.REC_CORR]
            
            # Create label
            HOME = os.environ['PYARCHINIT_HOME']
            PDF_path = os.path.join(HOME, "pyarchinit_PDF_folder")
            filename = f"Etichetta_TMA_{current_tma.id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = os.path.join(PDF_path, filename)
            
            label_gen = TMALabelPDF(label_format=label_format)
            label_gen.generate_single_label(current_tma, filepath, label_style)
            
            QMessageBox.information(self, "Esportazione completata", 
                                    f"Etichetta esportata in:\n{filepath}", QMessageBox.Ok)
                                    
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore nell'esportazione: {str(e)}", QMessageBox.Ok)
    
    def export_all_labels(self, label_format, label_style):
        """Export labels for all TMA records."""
        try:
            # Get all TMA records
            tma_list = self.DB_MANAGER.query('TMA')
            
            if not tma_list:
                QMessageBox.warning(self, "Attenzione", "Nessun record TMA nel database", QMessageBox.Ok)
                return
                
            # Create labels
            HOME = os.environ['PYARCHINIT_HOME']
            PDF_path = os.path.join(HOME, "pyarchinit_PDF_folder")
            filename = f"Etichette_TMA_tutte_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = os.path.join(PDF_path, filename)
            
            label_gen = TMALabelPDF(label_format=label_format)
            label_gen.generate_labels(tma_list, filepath, label_style)
            
            QMessageBox.information(self, "Esportazione completata", 
                                    f"Etichette esportate in:\n{filepath}\n\nTotale etichette: {len(tma_list)}", 
                                    QMessageBox.Ok)
                                    
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore nell'esportazione: {str(e)}", QMessageBox.Ok)
    
    def export_filtered_labels(self, label_format, label_style):
        """Export labels for filtered TMA records."""
        try:
            # Build search filters
            search_dict = {}
            
            if self.check_label_sito.isChecked() and self.comboBox_sito.currentText():
                search_dict['sito'] = "'" + str(self.comboBox_sito.currentText()) + "'"
                
            if self.check_label_area.isChecked() and self.comboBox_area.currentText():
                search_dict['area'] = "'" + str(self.comboBox_area.currentText()) + "'"
                
            if self.check_label_us.isChecked() and self.lineEdit_us.text():
                search_dict['dscu'] = "'" + str(self.lineEdit_us.text()) + "'"
                
            if self.check_label_cassetta.isChecked() and self.lineEdit_cassetta.text():
                # Use LIKE for partial matching in cassetta field
                search_text = str(self.lineEdit_cassetta.text()).strip()
                search_dict['cassetta'] = "LIKE '%%" + search_text + "%%'"
            
            # Query TMA records
            if search_dict:
                tma_list = self.DB_MANAGER.query_bool(search_dict, 'TMA')
            else:
                tma_list = self.DB_MANAGER.query('TMA')
                
            if not tma_list:
                QMessageBox.warning(self, "Attenzione", "Nessun record trovato con i filtri specificati", QMessageBox.Ok)
                return
                
            # Create labels
            HOME = os.environ['PYARCHINIT_HOME']
            PDF_path = os.path.join(HOME, "pyarchinit_PDF_folder")
            filename = f"Etichette_TMA_filtrate_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = os.path.join(PDF_path, filename)
            
            label_gen = TMALabelPDF(label_format=label_format)
            label_gen.generate_labels(tma_list, filepath, label_style)
            
            QMessageBox.information(self, "Esportazione completata", 
                                    f"Etichette esportate in:\n{filepath}\n\nTotale etichette: {len(tma_list)}", 
                                    QMessageBox.Ok)
                                    
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore nell'esportazione: {str(e)}", QMessageBox.Ok)
    def insert_new_row(self, table_name):
        """Insert new row into a table based on table_name."""
        cmd = table_name + ".insertRow(0)"
        eval(cmd)
    
    def remove_row(self, table_name):
        """Remove selected row from a table based on table_name."""
        table_row_count_cmd = ("%s.rowCount()") % (table_name)
        table_row_count = eval(table_row_count_cmd)
        rowSelected_cmd = ("%s.selectedIndexes()") % (table_name)
        rowSelected = eval(rowSelected_cmd)
        try:
            rowIndex = (rowSelected[0].row())
            cmd = ("%s.removeRow(%d)") % (table_name, rowIndex)
            eval(cmd)
        except:
            if self.L=='it':
                QMessageBox.warning(self, "Messaggio", "Devi selezionare una riga", QMessageBox.Ok)
            elif self.L=='de':
                QMessageBox.warning(self, "Message", "Sie müssen eine Zeile markieren.", QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "Message", "You must select a row", QMessageBox.Ok)
    
    def table2dict(self, table_name):
        """Convert table widget data to dictionary list."""
        self.tablename = table_name
        row = eval(self.tablename + ".rowCount()")
        col = eval(self.tablename + ".columnCount()")
        lista = []
        for r in range(row):
            sub_list = []
            for c in range(col):
                value = eval(self.tablename + ".item(r,c)")
                if value != None:
                    sub_list.append(str(value.text()))
            if bool(sub_list):
                lista.append(sub_list)
        return lista