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

import platform
import subprocess
from builtins import range
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QBrush, QColor
from qgis.PyQt.uic import loadUiType
from qgis.core import QgsSettings, Qgis

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
        "Cronologia MAC": "cronologia_mac",
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

        # Initialize GUI before connecting
        self.customize_GUI()

        try:
            self.on_pushButton_connect_pressed()
        except Exception as e:
            QMessageBox.warning(self, "Connection system", str(e), QMessageBox.Ok)

        self.msg_sito()
        self.set_sito()

    def customize_GUI(self):
        """Customize the GUI elements - connect signals to slots."""
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
        
        # Connect fields to auto-update chronology and inventory
        self.lineEdit_us.textChanged.connect(self.on_us_changed)
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
        self.rec_num = n
        if self.DATA_LIST:
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
                    self.lineEdit_aint.setText(str(self.DATA_LIST[self.rec_num].aint))
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
                # Ensure signal is reconnected even if there's an error
                try:
                    self.lineEdit_us.textChanged.connect(self.on_us_changed)
                except:
                    pass  # Already connected

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

    def set_rec_counter(self, t, c):
        """Set the record counter display."""
        self.label_rec_tot.setText(str(t))
        self.label_rec_corrente.setText(str(c))

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

        if self.lineEdit_aint.text():
            aint = self.lineEdit_aint.text()
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
        headers = ["Materiale *", "Categoria *", "Classe", "Prec. tipologica", "Definizione", "Cronologia MAC", "Quantità", "Peso"]
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
            
            # Query materials for this TMA record
            search_dict = {'id_tma': current_tma_id}
            materials = self.DB_MANAGER.query_bool(search_dict, 'TMA_MATERIALI')
            
            for material in materials:
                row = self.tableWidget_materiali.rowCount()
                self.tableWidget_materiali.insertRow(row)
                
                # Fill row data - First column is materiale (stored in madi field of TMA_MATERIALI)
                item0 = QTableWidgetItem(str(material.madi) if material.madi else "")
                # Store the material ID in the first item's user data
                item0.setData(Qt.UserRole, material.id)
                self.tableWidget_materiali.setItem(row, 0, item0)
                
                self.tableWidget_materiali.setItem(row, 1, QTableWidgetItem(str(material.macc) if material.macc else ""))
                self.tableWidget_materiali.setItem(row, 2, QTableWidgetItem(str(material.macl) if material.macl else ""))
                self.tableWidget_materiali.setItem(row, 3, QTableWidgetItem(str(material.macp) if material.macp else ""))
                self.tableWidget_materiali.setItem(row, 4, QTableWidgetItem(str(material.macd) if material.macd else ""))
                self.tableWidget_materiali.setItem(row, 5, QTableWidgetItem(str(material.cronologia_mac) if material.cronologia_mac else ""))
                self.tableWidget_materiali.setItem(row, 6, QTableWidgetItem(str(material.macq) if material.macq else ""))
                self.tableWidget_materiali.setItem(row, 7, QTableWidgetItem(str(material.peso) if material.peso else ""))
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Errore nel caricamento materiali: {str(e)}", QMessageBox.Ok)

    def save_materials_data(self, tma_id):
        """Save materials table data to database."""
        try:
            # Get existing materials for this TMA
            search_dict = {'id_tma': tma_id}
            existing_materials = self.DB_MANAGER.query_bool(search_dict, 'TMA_MATERIALI')
            existing_ids = {mat.id: mat for mat in existing_materials}
            
            # Track which IDs we've seen in the table widget
            seen_ids = set()
            
            # Process each row in the table widget
            for row in range(self.tableWidget_materiali.rowCount()):
                # Note: Column 0 is now Materiale, not Inventario (madi)
                materiale = self.tableWidget_materiali.item(row, 0).text() if self.tableWidget_materiali.item(row, 0) else ""
                macc = self.tableWidget_materiali.item(row, 1).text() if self.tableWidget_materiali.item(row, 1) else ""
                macl = self.tableWidget_materiali.item(row, 2).text() if self.tableWidget_materiali.item(row, 2) else ""
                macp = self.tableWidget_materiali.item(row, 3).text() if self.tableWidget_materiali.item(row, 3) else ""
                macd = self.tableWidget_materiali.item(row, 4).text() if self.tableWidget_materiali.item(row, 4) else ""
                cronologia_mac = self.tableWidget_materiali.item(row, 5).text() if self.tableWidget_materiali.item(row, 5) else ""
                macq = self.tableWidget_materiali.item(row, 6).text() if self.tableWidget_materiali.item(row, 6) else ""
                peso_text = self.tableWidget_materiali.item(row, 7).text() if self.tableWidget_materiali.item(row, 7) else ""
                
                # Convert peso to float
                try:
                    peso = float(peso_text) if peso_text else 0.0
                except ValueError:
                    peso = 0.0
                
                # Skip empty rows (at least category must be filled)
                if not macc.strip():
                    continue
                
                # Check if this row has an existing ID (stored as row data)
                material_id = self.tableWidget_materiali.item(row, 0).data(Qt.UserRole) if self.tableWidget_materiali.item(row, 0) else None
                
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
                    
                    material_data = self.DB_MANAGER.insert_tma_materiali_values(
                        new_material_id,
                        tma_id,
                        materiale,  # Column 0 is materiale, stored in madi field
                        macc,
                        macl,
                        macp,
                        macd,
                        cronologia_mac,
                        macq,
                        peso,
                        '',  # created_at
                        '',  # updated_at
                        '',  # created_by
                        ''   # updated_by
                    )
                    self.DB_MANAGER.insert_data_session(material_data)
                    seen_ids.add(new_material_id)
            
            # Delete materials that were removed from the table
            for existing_id in existing_ids:
                if existing_id not in seen_ids:
                    self.DB_MANAGER.delete_record_by_field('TMA_MATERIALI', 'id', existing_id)
                    
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Errore nel salvataggio materiali: {str(e)}", QMessageBox.Ok)

    def on_pushButton_add_materiale_pressed(self):
        """Add a new row to materials table."""
        # Disconnect signal temporarily to prevent double add
        try:
            self.pushButton_add_materiale.clicked.disconnect()
        except:
            pass
            
        row = self.tableWidget_materiali.rowCount()
        self.tableWidget_materiali.insertRow(row)
        
        # Set default values for new row
        self.tableWidget_materiali.setItem(row, 0, QTableWidgetItem(""))  # Materiale
        self.tableWidget_materiali.setItem(row, 1, QTableWidgetItem(""))  # Categoria (required)
        self.tableWidget_materiali.setItem(row, 2, QTableWidgetItem(""))  # Classe
        self.tableWidget_materiali.setItem(row, 3, QTableWidgetItem(""))  # Prec. tipologica
        self.tableWidget_materiali.setItem(row, 4, QTableWidgetItem(""))  # Definizione
        self.tableWidget_materiali.setItem(row, 5, QTableWidgetItem(""))  # Cronologia MAC
        self.tableWidget_materiali.setItem(row, 6, QTableWidgetItem(""))  # Quantità
        self.tableWidget_materiali.setItem(row, 7, QTableWidgetItem(""))  # Peso
        
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
        self.lineEdit_aint.clear()
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

    def check_record_state(self):
        """Check if the current record has been modified."""
        ec = self.data_error_check()
        if ec == 1:
            return 1

        if self.DATA_LIST:
            self.set_LIST_REC_TEMP()
            self.set_LIST_REC_CORR()

            # Check main record changes
            main_record_changed = self.DATA_LIST_REC_CORR != self.DATA_LIST_REC_TEMP
            
            # Check if materials have changed
            materials_changed = self.check_materials_state()
            
            if main_record_changed or materials_changed:
                return 1
            else:
                return 0
        else:
            return 0

    def check_materials_state(self):
        """Check if materials in the table have changed compared to database."""
        try:
            if not self.DATA_LIST or self.REC_CORR >= len(self.DATA_LIST):
                # New record, check if table has content with valid data
                for row in range(self.tableWidget_materiali.rowCount()):
                    macc = self.tableWidget_materiali.item(row, 1).text() if self.tableWidget_materiali.item(row, 1) else ""
                    if macc.strip():  # At least one row has category filled
                        return True
                return False
            
            # Get current materials from database
            current_tma_id = self.DATA_LIST[self.REC_CORR].id
            search_dict = {'id_tma': current_tma_id}
            db_materials = self.DB_MANAGER.query_bool(search_dict, 'TMA_MATERIALI')
            
            # Create a map of existing materials by ID
            db_materials_by_id = {mat.id: mat for mat in db_materials}
            
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
                db_madi = str(db_material.madi) if db_material.madi else ""
                db_macc = str(db_material.macc) if db_material.macc else ""
                db_macl = str(db_material.macl) if db_material.macl else ""
                db_macp = str(db_material.macp) if db_material.macp else ""
                db_macd = str(db_material.macd) if db_material.macd else ""
                db_cronologia = str(db_material.cronologia_mac) if db_material.cronologia_mac else ""
                db_macq = str(db_material.macq) if db_material.macq else ""
                db_peso = str(db_material.peso) if db_material.peso else ""
                
                # Compare values
                if (table_madi != db_madi or table_macc != db_macc or table_macl != db_macl or 
                    table_macp != db_macp or table_macd != db_macd or table_cronologia != db_cronologia or
                    table_macq != db_macq or table_peso != db_peso):
                    return True
            
            # Check if any materials were deleted (exist in DB but not seen in table)
            if len(seen_ids) != len(db_materials):
                return True
            
            return False
            
        except Exception as e:
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
        if msg == 1:
            self.update_record_to_db()
        if msg == 0:
            pass

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

        try:
            self.empty_fields()
            self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), len(self.DATA_LIST) - 1
            self.fill_fields(self.REC_CORR)
            self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e), QMessageBox.Ok)

    def on_pushButton_prev_rec_pressed(self):
        """Navigate to previous record."""
        if self.check_record_state() == 1:
            self.update_if(QgsSettings().value("pyArchInit/ifupdaterecord"))
            
        if self.REC_CORR > 0:
            self.REC_CORR = self.REC_CORR - 1
            try:
                self.empty_fields()
                self.fill_fields(self.REC_CORR)
                self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e), QMessageBox.Ok)
        else:
            QMessageBox.warning(self, "Attenzione", "Sei al primo record!", QMessageBox.Ok)

    def on_pushButton_next_rec_pressed(self):
        """Navigate to next record."""
        if self.check_record_state() == 1:
            self.update_if(QgsSettings().value("pyArchInit/ifupdaterecord"))
            
        if self.REC_CORR < self.REC_TOT - 1:
            self.REC_CORR = self.REC_CORR + 1
            try:
                self.empty_fields()
                self.fill_fields(self.REC_CORR)
                self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e), QMessageBox.Ok)
        else:
            QMessageBox.warning(self, "Attenzione", "Sei all'ultimo record!", QMessageBox.Ok)

    def on_pushButton_new_rec_pressed(self):
        """Create a new record."""
        if self.check_record_state() == 1:
            self.update_if(QgsSettings().value("pyArchInit/ifupdaterecord"))

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
        if self.BROWSE_STATUS == "b":
            if self.data_error_check() == 0:
                if self.check_record_state() == 1:
                    self.update_record_to_db()
                    self.SORT_STATUS = "n"
                    self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
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
                str(self.lineEdit_aint.text()),
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
            search_dict = {'id_tma': current_tma.id}
            materials = self.DB_MANAGER.query_bool(search_dict, 'TMA_MATERIALI')
            
            # Prepare data for PDF - pass as tuple not list
            data = (current_tma, materials)
            
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
        self.on_pushButton_export_pdf_pressed()  # Use the same functionality
    
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
            
            print(f"DEBUG TMA: on_us_changed called - sito: {sito}, area: {area}, us: {us}")
            
            if not sito or not area or not us:
                print("DEBUG TMA: Missing sito, area, or us - returning")
                return
            
            # Query US record
            search_dict = {
                'sito': f"'{sito}'",
                'area': f"'{area}'",
                'us': int(us) if us.isdigit() else 0
            }
            
            print(f"DEBUG TMA: Querying US with search_dict: {search_dict}")
            us_records = self.DB_MANAGER.query_bool(search_dict, 'US')
            print(f"DEBUG TMA: Found {len(us_records) if us_records else 0} US records")
            
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
                    print(f"DEBUG TMA: Set fascia cronologica to: {datazione_value}")
                else:
                    # If no datazione field, try to build from period/phase
                    datazione = ""
                    periodo_iniziale = getattr(us_record, 'periodo_iniziale', None)
                    fase_iniziale = getattr(us_record, 'fase_iniziale', None)
                    periodo_finale = getattr(us_record, 'periodo_finale', None)
                    fase_finale = getattr(us_record, 'fase_finale', None)
                    
                    print(f"DEBUG TMA: Building from periodo/fase: {periodo_iniziale}/{fase_iniziale} - {periodo_finale}/{fase_finale}")
                    
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
                        print(f"DEBUG TMA: Set fascia cronologica from periodo/fase to: {datazione}")
                    else:
                        self.lineEdit_dtzg.clear()
                        print("DEBUG TMA: No datazione data available")
            else:
                print(f"DEBUG TMA: No US records found for: sito={sito}, area={area}, us={us}")
                self.lineEdit_dtzg.clear()
                        
        except Exception as e:
            # Print the error for debugging
            print(f"DEBUG TMA ERROR in on_us_changed: {str(e)}")
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
                'definizione': '10.9'  # Definizione
            }
            
            if field_type not in thesaurus_map:
                return []
            
            search_dict = {
                'lingua': lang,
                'nome_tabella': "'tma_materiali_archeologici'",
                'tipologia_sigla': f"'{thesaurus_map[field_type]}'"
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
        
        # If no values from thesaurus, provide some defaults to test
        if not materiale_values:
            materiale_values = ['Ceramica', 'Metallo', 'Vetro', 'Osso', 'Pietra']
        if not categoria_values:
            categoria_values = ['Anfora', 'Sigillata', 'Comune', 'Pareti sottili']
        
        # Debug print
        print(f"DEBUG TMA THESAURUS: Materiale values: {len(materiale_values)} items")
        print(f"DEBUG TMA THESAURUS: Categoria values: {len(categoria_values)} items")
        print(f"DEBUG TMA THESAURUS: Classe values: {len(classe_values)} items")
        print(f"DEBUG TMA THESAURUS: Tipologia values: {len(tipologia_values)} items")
        print(f"DEBUG TMA THESAURUS: Definizione values: {len(definizione_values)} items")
        
        # Set delegates for columns with thesaurus support
        if materiale_values:
            self.tableWidget_materiali.setItemDelegateForColumn(0, ComboBoxDelegate(materiale_values, self.tableWidget_materiali))
            print(f"DEBUG TMA: Set delegate for Materiale column with {len(materiale_values)} values")
        if categoria_values:
            self.tableWidget_materiali.setItemDelegateForColumn(1, ComboBoxDelegate(categoria_values, self.tableWidget_materiali))
            print(f"DEBUG TMA: Set delegate for Categoria column with {len(categoria_values)} values")
        if classe_values:
            self.tableWidget_materiali.setItemDelegateForColumn(2, ComboBoxDelegate(classe_values, self.tableWidget_materiali))
            print(f"DEBUG TMA: Set delegate for Classe column with {len(classe_values)} values")
        if tipologia_values:
            self.tableWidget_materiali.setItemDelegateForColumn(3, ComboBoxDelegate(tipologia_values, self.tableWidget_materiali))
            print(f"DEBUG TMA: Set delegate for Tipologia column with {len(tipologia_values)} values")
        if definizione_values:
            self.tableWidget_materiali.setItemDelegateForColumn(4, ComboBoxDelegate(definizione_values, self.tableWidget_materiali))
            print(f"DEBUG TMA: Set delegate for Definizione column with {len(definizione_values)} values")
