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
        "Località": "localita",
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
        "Località",
        "Cassetta",
        "Fascia cronologica",
        "Categoria"
    ]

    TABLE_FIELDS = [
        'sito',
        'area',
        'dscu',
        'ogtm',
        'ldct',
        'ldcn',
        'vecchia_collocazione',
        'cassetta',
        'localita',
        'scan',
        'saggio',
        'vano_locus',
        'dscd',
        'rcgd',
        'rcgz',
        'aint',
        'aind',
        'dtzg',
        'dtzs',
        'cronologie',
        'n_reperti',
        'peso',
        'deso',
        'madi',
        'macc',
        'macl',
        'macp',
        'macd',
        'cronologia_mac',
        'macq',
        'ftap',
        'ftan',
        'drat',
        'dran',
        'draa'
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

        # lista area
        area_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('us_table', 'area', 'US'))
        try:
            area_vl.remove('')
        except:
            pass
        self.comboBox_area.clear()
        area_vl.sort()
        self.comboBox_area.addItems(area_vl)

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
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                self.fill_fields()
                self.BROWSE_STATUS = "b"
                self.SORT_STATUS = "n"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                self.setComboBoxEnable(["self.comboBox_sito"], "False")
            else:
                pass
        except:
            if self.L == 'it':
                QMessageBox.information(self, "Attenzione", "Non esiste questo sito: "'"' + str(
                    sito_set_str) + '"'" in questa scheda, Per favore distattiva la 'scelta sito' dalla scheda di configurazione plugin per vedere tutti i record oppure crea la scheda",
                                        QMessageBox.Ok)
            else:
                QMessageBox.information(self, "Warning", "There is no such site: "'"' + str(
                    sito_set_str) + '"'" in this tab, Please disable the 'site choice' from the plugin configuration tab to see all records or create the tab",
                                        QMessageBox.Ok)

    def fill_fields(self, n=0):
        """Fill form fields with data from current record."""
        self.rec_num = n

        if self.DATA_LIST:
            try:
                # Basic fields from UI
                self.comboBox_sito.setEditText(str(self.DATA_LIST[self.rec_num].sito))
                self.comboBox_area.setEditText(str(self.DATA_LIST[self.rec_num].area))
                self.lineEdit_us.setText(str(self.DATA_LIST[self.rec_num].dscu))

                # Object data
                if self.DATA_LIST[self.rec_num].ogtm:
                    self.comboBox_ogtm.setEditText(str(self.DATA_LIST[self.rec_num].ogtm))

                # Location data
                if self.DATA_LIST[self.rec_num].ldct:
                    self.comboBox_ldct.setEditText(str(self.DATA_LIST[self.rec_num].ldct))
                if self.DATA_LIST[self.rec_num].ldcn:
                    self.lineEdit_ldcn.setText(str(self.DATA_LIST[self.rec_num].ldcn))
                if self.DATA_LIST[self.rec_num].vecchia_collocazione:
                    self.lineEdit_vecchia_collocazione.setText(str(self.DATA_LIST[self.rec_num].vecchia_collocazione))
                if self.DATA_LIST[self.rec_num].cassetta:
                    self.lineEdit_cassetta.setText(str(self.DATA_LIST[self.rec_num].cassetta))

                # Excavation data
                if self.DATA_LIST[self.rec_num].localita:
                    self.lineEdit_localita.setText(str(self.DATA_LIST[self.rec_num].localita))
                if self.DATA_LIST[self.rec_num].scan:
                    self.lineEdit_scan.setText(str(self.DATA_LIST[self.rec_num].scan))
                if self.DATA_LIST[self.rec_num].saggio:
                    self.lineEdit_saggio.setText(str(self.DATA_LIST[self.rec_num].saggio))
                if self.DATA_LIST[self.rec_num].vano_locus:
                    self.lineEdit_vano_locus.setText(str(self.DATA_LIST[self.rec_num].vano_locus))
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

                # Dating data
                if self.DATA_LIST[self.rec_num].dtzg:
                    self.lineEdit_dtzg.setText(str(self.DATA_LIST[self.rec_num].dtzg))
                if self.DATA_LIST[self.rec_num].dtzs:
                    self.lineEdit_dtzs.setText(str(self.DATA_LIST[self.rec_num].dtzs))
                if self.DATA_LIST[self.rec_num].cronologie:
                    self.lineEdit_cronologie.setText(str(self.DATA_LIST[self.rec_num].cronologie))
                if self.DATA_LIST[self.rec_num].n_reperti:
                    self.lineEdit_n_reperti.setText(str(self.DATA_LIST[self.rec_num].n_reperti))
                if self.DATA_LIST[self.rec_num].peso:
                    self.lineEdit_peso.setText(str(self.DATA_LIST[self.rec_num].peso))

                # Technical data
                if self.DATA_LIST[self.rec_num].deso:
                    self.textEdit_deso.setText(str(self.DATA_LIST[self.rec_num].deso))
                if self.DATA_LIST[self.rec_num].madi:
                    self.lineEdit_madi.setText(str(self.DATA_LIST[self.rec_num].madi))
                if self.DATA_LIST[self.rec_num].macc:
                    self.lineEdit_macc.setText(str(self.DATA_LIST[self.rec_num].macc))
                if self.DATA_LIST[self.rec_num].macl:
                    self.lineEdit_macl.setText(str(self.DATA_LIST[self.rec_num].macl))
                if self.DATA_LIST[self.rec_num].macp:
                    self.lineEdit_macp.setText(str(self.DATA_LIST[self.rec_num].macp))
                if self.DATA_LIST[self.rec_num].macd:
                    self.lineEdit_macd.setText(str(self.DATA_LIST[self.rec_num].macd))
                if self.DATA_LIST[self.rec_num].cronologia_mac:
                    self.lineEdit_cronologia_mac.setText(str(self.DATA_LIST[self.rec_num].cronologia_mac))
                if self.DATA_LIST[self.rec_num].macq:
                    self.lineEdit_macq.setText(str(self.DATA_LIST[self.rec_num].macq))

                # Documentation tables - Fill from database
                self.fill_documentation_tables()

            except Exception as e:
                QMessageBox.warning(self, "Error", str(e), QMessageBox.Ok)

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

        if self.comboBox_ogtm.currentText():
            ogtm = self.comboBox_ogtm.currentText()
        else:
            ogtm = ""

        # Location
        if self.comboBox_ldct.currentText():
            ldct = self.comboBox_ldct.currentText()
        else:
            ldct = ""

        if self.lineEdit_ldcn.text():
            ldcn = self.lineEdit_ldcn.text()
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
        if self.lineEdit_localita.text():
            localita = self.lineEdit_localita.text()
        else:
            localita = ""

        if self.lineEdit_scan.text():
            scan = self.lineEdit_scan.text()
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

        if self.lineEdit_dtzs.text():
            dtzs = self.lineEdit_dtzs.text()
        else:
            dtzs = ""

        if self.lineEdit_cronologie.text():
            cronologie = self.lineEdit_cronologie.text()
        else:
            cronologie = ""

        if self.lineEdit_n_reperti.text():
            n_reperti = self.lineEdit_n_reperti.text()
        else:
            n_reperti = ""

        if self.lineEdit_peso.text():
            peso = self.lineEdit_peso.text()
        else:
            peso = ""

        # Technical data
        if self.textEdit_deso.toPlainText():
            deso = self.textEdit_deso.toPlainText()
        else:
            deso = ""

        if self.lineEdit_madi.text():
            madi = self.lineEdit_madi.text()
        else:
            madi = ""

        if self.lineEdit_macc.text():
            macc = self.lineEdit_macc.text()
        else:
            macc = ""

        if self.lineEdit_macl.text():
            macl = self.lineEdit_macl.text()
        else:
            macl = ""

        if self.lineEdit_macp.text():
            macp = self.lineEdit_macp.text()
        else:
            macp = ""

        if self.lineEdit_macd.text():
            macd = self.lineEdit_macd.text()
        else:
            macd = ""

        if self.lineEdit_cronologia_mac.text():
            cronologia_mac = self.lineEdit_cronologia_mac.text()
        else:
            cronologia_mac = ""

        if self.lineEdit_macq.text():
            macq = self.lineEdit_macq.text()
        else:
            macq = ""

        # Get documentation data from tables
        ftap, ftan = self.get_foto_data()
        drat, dran, draa = self.get_disegni_data()

        # Build the temp list
        self.DATA_LIST_REC_TEMP = [
            str(self.comboBox_sito.currentText()),  # sito
            str(self.comboBox_area.currentText()),  # area
            str(dscu),  # US
            str(ogtm),  # materiale
            str(ldct),  # tipo collocazione
            str(ldcn),  # denominazione
            str(vecchia_collocazione),
            str(cassetta),
            str(localita),
            str(scan),
            str(saggio),
            str(vano_locus),
            str(dscd),
            str(rcgd),
            str(rcgz),
            str(aint),
            str(aind),
            str(dtzg),
            str(dtzs),
            str(cronologie),
            str(n_reperti),
            str(peso),
            str(deso),
            str(madi),
            str(macc),
            str(macl),
            str(macp),
            str(macd),
            str(cronologia_mac),
            str(macq),
            str(ftap),
            str(ftan),
            str(drat),
            str(dran),
            str(draa)
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
        self.comboBox_ogtm.setEditText("")
        self.comboBox_ldct.setEditText("")
        self.lineEdit_ldcn.clear()
        self.lineEdit_vecchia_collocazione.clear()
        self.lineEdit_cassetta.clear()
        self.lineEdit_localita.clear()
        self.lineEdit_scan.clear()
        self.lineEdit_saggio.clear()
        self.lineEdit_vano_locus.clear()
        self.lineEdit_dscd.clear()
        self.lineEdit_rcgd.clear()
        self.textEdit_rcgz.clear()
        self.lineEdit_aint.clear()
        self.lineEdit_aind.clear()
        self.lineEdit_dtzg.clear()
        self.lineEdit_dtzs.clear()
        self.lineEdit_cronologie.clear()
        self.lineEdit_n_reperti.clear()
        self.lineEdit_peso.clear()
        self.textEdit_deso.clear()
        self.lineEdit_madi.clear()
        self.lineEdit_macc.clear()
        self.lineEdit_macl.clear()
        self.lineEdit_macp.clear()
        self.lineEdit_macd.clear()
        self.lineEdit_cronologia_mac.clear()
        self.lineEdit_macq.clear()

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

            if self.DATA_LIST_REC_CORR == self.DATA_LIST_REC_TEMP:
                return 0
            else:
                return 1
        else:
            return 0

    def data_error_check(self):
        """Check for data errors in form fields."""
        test = 0
        EC = Error_check()

        # Check required fields
        if self.comboBox_ogtm.currentText() == "":
            QMessageBox.warning(self, "ATTENZIONE", "Campo Materiale obbligatorio!", QMessageBox.Ok)
            test = 1
            return test

        if self.lineEdit_ldcn.text() == "":
            QMessageBox.warning(self, "ATTENZIONE", "Campo Denominazione collocazione obbligatorio!", QMessageBox.Ok)
            test = 1
            return test

        if self.lineEdit_cassetta.text() == "":
            QMessageBox.warning(self, "ATTENZIONE", "Campo Cassetta obbligatorio!", QMessageBox.Ok)
            test = 1
            return test

        if self.lineEdit_localita.text() == "":
            QMessageBox.warning(self, "ATTENZIONE", "Campo Località obbligatorio!", QMessageBox.Ok)
            test = 1
            return test

        if self.lineEdit_us.text() == "":
            QMessageBox.warning(self, "ATTENZIONE", "Campo US obbligatorio!", QMessageBox.Ok)
            test = 1
            return test

        if self.lineEdit_dtzg.text() == "":
            QMessageBox.warning(self, "ATTENZIONE", "Campo Fascia cronologica obbligatorio!", QMessageBox.Ok)
            test = 1
            return test

        if self.lineEdit_macc.text() == "":
            QMessageBox.warning(self, "ATTENZIONE", "Campo Categoria obbligatorio!", QMessageBox.Ok)
            test = 1
            return test

        # Check OGTM values
        valori_ogtm = ['CERAMICA', 'INDUSTRIA LITICA', 'LITICA', 'METALLO']
        if self.comboBox_ogtm.currentText() and self.comboBox_ogtm.currentText() not in valori_ogtm:
            QMessageBox.warning(self, "ATTENZIONE",
                                f"Valore Materiale non valido! Valori accettati: {', '.join(valori_ogtm)}",
                                QMessageBox.Ok)
            test = 1
            return test

        return test

    def update_if(self, msg):
        """Update interface message."""
        if msg == 1:
            self.update_record()
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

        self.REC_CORR = self.REC_CORR - 1
        if self.REC_CORR < 0:
            self.REC_CORR = 0
            QMessageBox.warning(self, "Attenzione", "Sei al primo record!", QMessageBox.Ok)
        else:
            try:
                self.empty_fields()
                self.fill_fields(self.REC_CORR)
                self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e), QMessageBox.Ok)

    def on_pushButton_next_rec_pressed(self):
        """Navigate to next record."""
        if self.check_record_state() == 1:
            self.update_if(QgsSettings().value("pyArchInit/ifupdaterecord"))

        self.REC_CORR = self.REC_CORR + 1
        if self.REC_CORR >= self.REC_TOT:
            self.REC_CORR = self.REC_TOT - 1
            QMessageBox.warning(self, "Attenzione", "Sei all'ultimo record!", QMessageBox.Ok)
        else:
            try:
                self.empty_fields()
                self.fill_fields(self.REC_CORR)
                self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e), QMessageBox.Ok)

    def on_pushButton_new_rec_pressed(self):
        """Create a new record."""
        if self.check_record_state() == 1:
            self.update_if(QgsSettings().value("pyArchInit/ifupdaterecord"))

        if self.BROWSE_STATUS != "n":
            self.BROWSE_STATUS = "n"
            self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
            self.empty_fields()
            self.label_sort.setText(self.SORTED_ITEMS["n"])

            self.setComboBoxEnable(["self.comboBox_sito"], "True")
            self.setComboBoxEditable(["self.comboBox_sito"], 1)

            self.set_rec_counter('', '')
            self.label_sort.setText(self.SORTED_ITEMS["n"])

    def on_pushButton_save_pressed(self):
        """Save the current record."""
        if self.BROWSE_STATUS == "b":
            if self.data_error_check() == 0:
                if self.check_record_state() == 1:
                    self.update_record()
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

        if self.comboBox_ogtm.currentText() != "":
            search_dict['ogtm'] = "'" + str(self.comboBox_ogtm.currentText()) + "'"

        if self.lineEdit_ldcn.text() != "":
            search_dict['ldcn'] = "'" + str(self.lineEdit_ldcn.text()) + "'"

        if self.lineEdit_cassetta.text() != "":
            search_dict['cassetta'] = "'" + str(self.lineEdit_cassetta.text()) + "'"

        if self.lineEdit_localita.text() != "":
            search_dict['localita'] = "'" + str(self.lineEdit_localita.text()) + "'"

        if self.lineEdit_dtzg.text() != "":
            search_dict['dtzg'] = "'" + str(self.lineEdit_dtzg.text()) + "'"

        if self.lineEdit_macc.text() != "":
            search_dict['macc'] = "'" + str(self.lineEdit_macc.text()) + "'"

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
                str(self.comboBox_ogtm.currentText()),
                str(self.comboBox_ldct.currentText()),
                str(self.lineEdit_ldcn.text()),
                str(self.lineEdit_vecchia_collocazione.text()),
                str(self.lineEdit_cassetta.text()),
                str(self.lineEdit_localita.text()),
                str(self.lineEdit_scan.text()),
                str(self.lineEdit_saggio.text()),
                str(self.lineEdit_vano_locus.text()),
                str(self.lineEdit_dscd.text()),
                str(self.lineEdit_us.text()),  # dscu
                str(self.lineEdit_rcgd.text()),
                str(self.textEdit_rcgz.toPlainText()),
                str(self.lineEdit_aint.text()),
                str(self.lineEdit_aind.text()),
                str(self.lineEdit_dtzg.text()),
                str(self.lineEdit_dtzs.text()),
                str(self.lineEdit_cronologie.text()),
                str(self.lineEdit_n_reperti.text()),
                str(self.lineEdit_peso.text()),
                str(self.textEdit_deso.toPlainText()),
                str(self.lineEdit_madi.text()),
                str(self.lineEdit_macc.text()),
                str(self.lineEdit_macl.text()),
                str(self.lineEdit_macp.text()),
                str(self.lineEdit_macd.text()),
                str(self.lineEdit_cronologia_mac.text()),
                str(self.lineEdit_macq.text()),
                str(ftap),
                str(ftan),
                str(drat),
                str(dran),
                str(draa)
            )

            self.DB_MANAGER.insert_data_session(data)
            return 1

        except Exception as e:
            QMessageBox.warning(self, "Error", "Problema nell'inserimento: " + str(e), QMessageBox.Ok)
            return 0

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
        """Update current record in database."""
        try:
            # Get documentation data from tables
            ftap, ftan = self.get_foto_data()
            drat, dran, draa = self.get_disegni_data()

            self.DB_MANAGER.update(self.MAPPER_TABLE_CLASS,
                                   self.ID_TABLE,
                                   [eval("int(self.DATA_LIST[self.REC_CORR]." + self.ID_TABLE + ")")],
                                   self.TABLE_FIELDS,
                                   self.set_LIST_REC_TEMP())
            return 1
        except Exception as e:
            QMessageBox.warning(self, "Error", "Problema nell'aggiornamento: " + str(e), QMessageBox.Ok)
            return 0
