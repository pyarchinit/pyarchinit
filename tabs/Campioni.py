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

import sys
from builtins import range
from builtins import str
from qgis.PyQt.QtWidgets import QApplication, QDialog, QMessageBox
from qgis.PyQt.uic import loadUiType

from ..modules.db.pyarchinit_conn_strings import Connection
from ..modules.db.pyarchinit_db_manager import Pyarchinit_db_management
from ..modules.db.pyarchinit_utility import Utility
from ..modules.gis.pyarchinit_pyqgis import Pyarchinit_pyqgis
from ..modules.utility.pyarchinit_error_check import Error_check
from ..modules.utility.pyarchinit_exp_Campsheet_pdf import *
from ..modules.utility.pyarchinit_exp_Campsheet_pdf import generate_campioni_pdf
from .US_USM import pyarchinit_US
from ..sortpanelmain import SortPanelMain

MAIN_DIALOG_CLASS, _ = loadUiType(os.path.join(os.path.dirname(__file__),'..', 'ui', 'Campioni.ui'))


class pyarchinit_Campioni(QDialog, MAIN_DIALOG_CLASS):
    MSG_BOX_TITLE = "PyArchInit - pyarchinit_version 0.4 - Scheda Campioni"
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
    TABLE_NAME = 'campioni_table'
    MAPPER_TABLE_CLASS = "CAMPIONI"
    NOME_SHEDA = "Scheda Campioni"
    ID_TABLE = "id_campione"
    CONVERSION_DICT = {
        ID_TABLE: ID_TABLE,
        "Sito": "sito",
        "Nr Campione": "nr_campione",
        "Tipo campione": "tipo_campione",
        "Descrizione": "descrizione",
        "Area": "area",
        "US": "us",
        "Nr. Inventario Materiale": "numero_inventario_materiale",
        "Nr Cassa": "nr_cassa",
        "Luogo di conservazione": "luogo_conservazione"
    }

    SORT_ITEMS = [
        ID_TABLE,
        "Sito",
        "Nr Campione",
        "Tipo campione",
        "Descrizione",
        "Area",
        "US",
        "Nr. Inventario Materiale",
        "Nr Cassa",
        "Luogo di conservazione"
    ]

    TABLE_FIELDS = [
        "sito",
        "nr_campione",
        "tipo_campione",
        "descrizione",
        "area",
        "us",
        "numero_inventario_materiale",
        "nr_cassa",
        "luogo_conservazione"
    ]

    DB_SERVER = 'not defined'

    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.pyQGIS = Pyarchinit_pyqgis(iface)
        self.setupUi(self)
        self.currentLayerId = None
        try:
            self.on_pushButton_connect_pressed()
        except Exception as e:
            QMessageBox.warning(self, "Sistema di connessione", str(e), QMessageBox.Ok)

    def enable_button(self, n):
        self.pushButton_connect.setEnabled(n)

        self.pushButton_new_rec.setEnabled(n)

        self.pushButton_view_all.setEnabled(n)

        self.pushButton_first_rec.setEnabled(n)

        self.pushButton_last_rec.setEnabled(n)

        self.pushButton_prev_rec.setEnabled(n)

        self.pushButton_next_rec.setEnabled(n)

        self.pushButton_delete.setEnabled(n)

        self.pushButton_new_search.setEnabled(n)

        self.pushButton_search_go.setEnabled(n)

        self.pushButton_sort.setEnabled(n)

    def enable_button_search(self, n):
        self.pushButton_connect.setEnabled(n)

        self.pushButton_new_rec.setEnabled(n)

        self.pushButton_view_all.setEnabled(n)

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
                QMessageBox.warning(self, "BENVENUTO",
                                    "Benvenuto in pyArchInit" + self.NOME_SCHEDA + ". Il database e' vuoto. Premi 'Ok' e buon lavoro!",
                                    QMessageBox.Ok)
                self.charge_list()
                self.BROWSE_STATUS = 'x'
                self.on_pushButton_new_rec_pressed()
        except Exception as e:
            e = str(e)
            if e.find("no such table"):
                QMessageBox.warning(self, "Alert",
                                    "La connessione e' fallita <br><br> Tabella non presente. E' NECESSARIO RIAVVIARE QGIS" + str(
                                        e), QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "Alert",
                                    "Attenzione rilevato bug! Segnalarlo allo sviluppatore<br> Errore: <br>" + str(e),
                                    QMessageBox.Ok)

    def charge_list(self):
        sito_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('site_table', 'sito', 'SITE'))

        try:
            sito_vl.remove('')
        except:
            pass
        self.comboBox_sito.clear()
        sito_vl.sort()
        self.comboBox_sito.addItems(sito_vl)

        # buttons functions

    def on_pushButton_pdf_pressed(self):
        pass

    def on_pushButton_sort_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            dlg = SortPanelMain(self)
            dlg.insertItems(self.SORT_ITEMS)
            dlg.exec_()

            items, order_type = dlg.ITEMS, dlg.TYPE_ORDER

            self.SORT_ITEMS_CONVERTED = []
            for i in items:
                self.SORT_ITEMS_CONVERTED.append(self.CONVERSION_DICT[str(i)])

            self.SORT_MODE = order_type
            self.empty_fields()

            id_list = []
            for i in self.DATA_LIST:
                id_list.append(eval("i." + self.ID_TABLE))
            self.DATA_LIST = []

            temp_data_list = self.DB_MANAGER.query_sort(id_list, self.SORT_ITEMS_CONVERTED, self.SORT_MODE,
                                                        self.MAPPER_TABLE_CLASS, self.ID_TABLE)

            for i in temp_data_list:
                self.DATA_LIST.append(i)
            self.BROWSE_STATUS = "b"
            self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
            if type(self.REC_CORR) == "<type 'str'>":
                corr = 0
            else:
                corr = self.REC_CORR

            self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
            self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
            self.SORT_STATUS = "o"
            self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
            self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
            self.fill_fields()

    def on_pushButton_new_rec_pressed(self):
        if bool(self.DATA_LIST):
            if self.data_error_check() == 1:
                pass
            else:
                if self.BROWSE_STATUS == "b":
                    if bool(self.DATA_LIST):
                        if self.records_equal_check() == 1:
                            self.update_if(QMessageBox.warning(self, 'Errore',
                                                               "Il record e' stato modificato. Vuoi salvare le modifiche?",
                                                                QMessageBox.Ok | QMessageBox.Cancel))

                            # set the GUI for a new record
        if self.BROWSE_STATUS != "n":
            self.BROWSE_STATUS = "n"
            self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
            self.empty_fields()
            self.label_sort.setText(self.SORTED_ITEMS["n"])

            self.setComboBoxEditable(["self.comboBox_sito"], 1)

            self.setComboBoxEnable(["self.comboBox_sito"], "True")
            self.setComboBoxEnable(["self.lineEdit_nr_campione"], "True")

            self.set_rec_counter('', '')
            self.enable_button(0)

    def on_pushButton_save_pressed(self):
        # save record
        if self.BROWSE_STATUS == "b":
            if self.data_error_check() == 0:
                if self.records_equal_check() == 1:
                    self.update_if(QMessageBox.warning(self, 'ATTENZIONE',
                                                       "Il record e' stato modificato. Vuoi salvare le modifiche?",
                                                       QMessageBox.Ok | QMessageBox.Cancel))
                    self.label_sort.setText(self.SORTED_ITEMS["n"])
                    self.enable_button(1)
                    self.fill_fields(self.REC_CORR)
                else:
                    QMessageBox.warning(self, "ATTENZIONE", "Non è stata realizzata alcuna modifica.", QMessageBox.Ok)
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

                    self.setComboBoxEditable(["self.comboBox_sito"], 1)
                    self.setComboBoxEnable(["self.comboBox_sito"], "False")
                    self.setComboBoxEnable(["self.lineEdit_nr_campione"], "False")
                    self.fill_fields(self.REC_CORR)
                    self.enable_button(1)
                else:
                    pass

    def data_error_check(self):
        test = 0
        EC = Error_check()

        if EC.data_is_empty(str(self.comboBox_sito.currentText())) == 0:
            QMessageBox.warning(self, "ATTENZIONE", "Campo Sito. \n Il campo non deve essere vuoto", QMessageBox.Ok)
            test = 1

        if EC.data_is_empty(str(self.lineEdit_nr_campione.text())) == 0:
            QMessageBox.warning(self, "ATTENZIONE", "Campo nr_campione \n Il campo non deve essere vuoto",
                                QMessageBox.Ok)
            test = 1

        nr_campione = self.lineEdit_nr_campione.text()

        if nr_campione != "":
            if EC.data_is_int(nr_campione) == 0:
                QMessageBox.warning(self, "ATTENZIONE", "Campo Nr Campione \n Il valore deve essere di tipo numerico",
                                    QMessageBox.Ok)
                test = 1

        return test

    def insert_new_rec(self):
        try:
            if self.lineEdit_nr_campione.text() == "":
                nr_campione = None
            else:
                nr_campione = int(self.lineEdit_nr_campione.text())

            if self.lineEdit_us.text() == "":
                us = None
            else:
                us = int(self.lineEdit_us.text())

            if self.lineEdit_cassa.text() == "":
                nr_cassa = None
            else:
                nr_cassa = int(self.lineEdit_cassa.text())

            if self.lineEdit_n_inv_mat.text() == "":
                numero_inventario_materiale = None
            else:
                numero_inventario_materiale = int(self.lineEdit_n_inv_mat.text())

            data = self.DB_MANAGER.insert_campioni_values(
                self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, self.ID_TABLE) + 1,
                str(self.comboBox_sito.currentText()),  # 1 - Sito
                nr_campione,  # 2 - nr campione
                str(self.comboBox_tipo_campione.currentText()),  # 3 - tipo_campione
                str(self.textEdit_descrizione_camp.toPlainText()),  # 4 - descrizione
                str(self.lineEdit_area.text()),  # 5 - area
                us,  # 6 - us
                numero_inventario_materiale,  # 7 - inv materiale
                nr_cassa,  # 8 - nr_cassa
                str(self.lineEdit_luogo_conservazione.text()))  # 9 - luogo conservazione

            try:
                self.DB_MANAGER.insert_data_session(data)
                return 1
            except Exception as e:
                e_str = str(e)
                if e_str.__contains__("Integrity"):
                    msg = self.ID_TABLE + " gia' presente nel database"
                else:
                    msg = e
                QMessageBox.warning(self, "Errore", "Attenzione 1 ! \n" + str(msg), QMessageBox.Ok)
                return 0
        except Exception as e:
            QMessageBox.warning(self, "Errore", "Attenzione 2 ! \n" + str(e), QMessageBox.Ok)
            return 0

    def check_record_state(self):
        ec = self.data_error_check()
        if ec == 1:
            return 1  # ci sono errori di immissione
        elif self.records_equal_check() == 1 and ec == 0:
            self.update_if(
                QMessageBox.warning(self, 'Errore', "Il record e' stato modificato. Vuoi salvare le modifiche?",
                                    QMessageBox.Ok | QMessageBox.Cancel))
            # self.charge_records() incasina lo stato trova
            return 0  # non ci sono errori di immissione

    def on_pushButton_view_all_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
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

            # records surf functions

    def on_pushButton_first_rec_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            try:
                self.empty_fields()
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                self.fill_fields(0)
                self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
            except Exception as e:
                QMessageBox.warning(self, "Errore", str(e), QMessageBox.Ok)

    def on_pushButton_last_rec_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            try:
                self.empty_fields()
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), len(self.DATA_LIST) - 1
                self.fill_fields(self.REC_CORR)
                self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
            except Exception as e:
                QMessageBox.warning(self, "Errore", str(e), QMessageBox.Ok)

    def on_pushButton_prev_rec_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            self.REC_CORR = self.REC_CORR - 1
            if self.REC_CORR == -1:
                self.REC_CORR = 0
                QMessageBox.warning(self, "Errore", "Sei al primo record!", QMessageBox.Ok)
            else:
                try:
                    self.empty_fields()
                    self.fill_fields(self.REC_CORR)
                    self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
                except Exception as e:
                    QMessageBox.warning(self, "Errore", str(e), QMessageBox.Ok)

    def on_pushButton_next_rec_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            self.REC_CORR = self.REC_CORR + 1
            if self.REC_CORR >= self.REC_TOT:
                self.REC_CORR = self.REC_CORR - 1
                QMessageBox.warning(self, "Errore", "Sei all'ultimo record!", QMessageBox.Ok)
            else:
                try:
                    self.empty_fields()
                    self.fill_fields(self.REC_CORR)
                    self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
                except Exception as e:
                    QMessageBox.warning(self, "Errore", str(e), QMessageBox.Ok)

    def on_pushButton_delete_pressed(self):
        msg = QMessageBox.warning(self, "Attenzione!!!",
                                  "Vuoi veramente eliminare il record? \n L'azione è irreversibile",
                                  QMessageBox.Ok | QMessageBox.Cancel)
        if msg == QMessageBox.Cancel:
            QMessageBox.warning(self, "Messagio!!!", "Azione Annullata!")
        else:
            try:
                id_to_delete = eval("self.DATA_LIST[self.REC_CORR]." + self.ID_TABLE)
                self.DB_MANAGER.delete_one_record(self.TABLE_NAME, self.ID_TABLE, id_to_delete)
                self.charge_records()  # charge records from DB
                QMessageBox.warning(self, "Messaggio!!!", "Record eliminato!")
            except Exception as e:
                QMessageBox.warning(self, "Messaggio!!!", "Tipo di errore: " + str(e))
            if not bool(self.DATA_LIST):
                QMessageBox.warning(self, "Attenzione", "Il database è vuoto!", QMessageBox.Ok)
                self.DATA_LIST = []
                self.DATA_LIST_REC_CORR = []
                self.DATA_LIST_REC_TEMP = []
                self.REC_CORR = 0
                self.REC_TOT = 0
                self.empty_fields()
                self.set_rec_counter(0, 0)
                # check if DB is empty
            if bool(self.DATA_LIST):
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]

                self.BROWSE_STATUS = "b"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                self.charge_list()
                self.fill_fields()
        self.SORT_STATUS = "n"
        self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])

    def on_pushButton_new_search_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            self.enable_button_search(0)

            # set the GUI for a new search
            if self.BROWSE_STATUS != "f":
                self.BROWSE_STATUS = "f"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                ###
                self.setComboBoxEnable(["self.comboBox_sito"], "True")
                self.setComboBoxEnable(["self.lineEdit_nr_campione"], "True")
                self.setComboBoxEnable(["self.textEdit_descrizione_camp"], "False")
                ###
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.set_rec_counter('', '')
                self.label_sort.setText(self.SORTED_ITEMS["n"])
                self.charge_list()
                self.empty_fields()

    def on_pushButton_search_go_pressed(self):
        if self.BROWSE_STATUS != "f":
            QMessageBox.warning(self, "ATTENZIONE", "Per eseguire una nuova ricerca clicca sul pulsante 'new search' ",
                                QMessageBox.Ok)
        else:

            if self.lineEdit_nr_campione.text() == "":
                nr_campione = None
            else:
                nr_campione = int(self.lineEdit_nr_campione.text())

            if self.lineEdit_us.text() == "":
                us = None
            else:
                us = int(self.lineEdit_us.text())

            if self.lineEdit_cassa.text() == "":
                nr_cassa = None
            else:
                nr_cassa = int(self.lineEdit_cassa.text())

            if self.lineEdit_n_inv_mat.text() == "":
                numero_inventario_materiale = None
            else:
                numero_inventario_materiale = int(self.lineEdit_n_inv_mat.text())

            search_dict = {
                self.TABLE_FIELDS[0]: "'" + str(self.comboBox_sito.currentText()) + "'",  # 1 - Sito
                self.TABLE_FIELDS[1]: nr_campione,  # 2 - numero_campione
                self.TABLE_FIELDS[2]: "'" + str(self.comboBox_tipo_campione.currentText()) + "'",  # 3 - tipo campione
                self.TABLE_FIELDS[4]: "'" + str(self.lineEdit_area.text()) + "'",  # 4- area
                self.TABLE_FIELDS[5]: us,  # 5 - us
                self.TABLE_FIELDS[6]: numero_inventario_materiale,  # 6 - numero inventario materiale
                self.TABLE_FIELDS[7]: nr_cassa,  # 7- nr cassa
                self.TABLE_FIELDS[8]: "'" + str(self.lineEdit_luogo_conservazione.text()) + "'"  # 8 - periodo finale
            }

            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)

            if not bool(search_dict):
                QMessageBox.warning(self, "ATTENZIONE", "Non e' stata impostata alcuna ricerca!!!", QMessageBox.Ok)
            else:
                res = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
                if not bool(res):
                    QMessageBox.warning(self, "ATTENZIONE", "Non e' stato trovato alcun record!", QMessageBox.Ok)

                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]

                    self.fill_fields(self.REC_CORR)
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])

                    self.setComboBoxEnable(["self.comboBox_sito"], "False")
                    self.setComboBoxEnable(["self.lineEdit_nr_campione"], "True")
                    self.setComboBoxEnable(["self.textEdit_descrizione_camp"], "True")

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
                        strings = ("E' stato trovato", self.REC_TOT, "record")
                    else:
                        strings = ("Sono stati trovati", self.REC_TOT, "records")

                    self.setComboBoxEnable(["self.comboBox_sito"], "False")
                    self.setComboBoxEnable(["self.lineEdit_nr_campione"], "True")
                    self.setComboBoxEnable(["self.textEdit_descrizione_camp"], "True")

                    QMessageBox.warning(self, "Messaggio", "%s %d %s" % strings, QMessageBox.Ok)

        self.enable_button_search(1)

    def on_pushButton_test_pressed(self):
        pass

    def on_pushButton_index_pdf_pressed(self):
        Camp_index_pdf = generate_campioni_pdf()
        data_list = self.generate_list_pdf()
        Camp_index_pdf.build_index_Campioni(data_list, data_list[0][0])

        sito_ec = str(self.comboBox_sito.currentText())
        Mat_casse_pdf = generate_campioni_pdf()
        data_list = self.generate_el_casse_pdf(sito_ec)
        Mat_casse_pdf.build_index_Casse(data_list, sito_ec)
        Mat_casse_pdf.build_box_labels_Campioni(data_list, sito_ec)

    def on_pushButton_exp_champ_sheet_pdf_pressed(self):
        if self.records_equal_check() == 1:
            self.update_if(
                QMessageBox.warning(self, 'Errore', "Il record è stato modificato. Vuoi salvare le modifiche?",
                                    QMessageBox.Ok | QMessageBox.Cancel))

        Champ_pdf_sheet = generate_campioni_pdf()
        data_list = self.generate_list_pdf()
        Champ_pdf_sheet.build_Champ_sheets(data_list)

        # ********************************************************************************

    def generate_el_casse_pdf(self, sito):
        self.sito_ec = sito
        elenco_casse_res = self.DB_MANAGER.query_distinct('CAMPIONI', [['sito', '"' + str(self.sito_ec) + '"']],
                                                          ['nr_cassa'])

        elenco_casse_list = []  # accoglie la sigla numerica delle casse presenti per un determinato sito.
        for i in elenco_casse_res:
            elenco_casse_list.append(i.nr_cassa)

        data_for_pdf = []  # contiene i singoli dati per l'esportazione dell'elenco casse

        elenco_casse_list.sort()
        for cassa in elenco_casse_list:
            single_cassa = []  # contiene i dati della singola cassa

            str_cassa = "<b>" + str(cassa) + "</b>"
            single_cassa.append(str_cassa)  # inserisce la sigla di cassa

            ###cerca le singole area/us presenti in quella cassa
            res_inv = self.DB_MANAGER.query_distinct('CAMPIONI',
                                                     [['sito', '"' + str(self.sito_ec) + '"'], ['nr_cassa', cassa]],
                                                     ['nr_campione', 'tipo_campione'])

            res_inv_list = []
            for i in res_inv:
                res_inv_list.append(i)

            n_inv_res_list = ""
            for i in range(len(res_inv_list)):
                if i != len(res_inv_list) - 1:
                    n_inv_res_list += " N.inv:" + str(res_inv_list[i].nr_campione) + "/" + str(
                        res_inv_list[i].tipo_campione) + ","
                else:
                    n_inv_res_list += " N.inv:" + str(res_inv_list[i].nr_campione) + "/" + str(
                        res_inv_list[i].tipo_campione)

                    # inserisce l'elenco degli inventari
            single_cassa.append(n_inv_res_list)

            ###cerca le singole area/us presenti in quella cassa
            res_us = self.DB_MANAGER.query_distinct('CAMPIONI',
                                                    [['sito', '"' + str(self.sito_ec) + '"'], ['nr_cassa', cassa]],
                                                    ['area', 'us'])

            res_us_list = []
            for i in res_us:
                res_us_list.append(i)

            us_res_list = ""  # [] #accoglie l'elenco delle US presenti in quella cassa
            for i in range(len(res_us_list)):
                params_dict = {'sito': '"' + str(self.sito_ec) + '"', 'area': '"' + str(res_us_list[i].area) + '"',
                               'us': '"' + str(res_us_list[i].us) + '"'}
                res_struct = self.DB_MANAGER.query_bool(params_dict, 'US')

                res_struct_list = []
                for s_strutt in res_struct:
                    res_struct_list.append(s_strutt)

                structure_string = ""
                if len(res_struct_list) > 0:
                    for sing_us in res_struct_list:
                        if sing_us.struttura != '':
                            structure_string += "(" + str(sing_us.struttura) + '/'

                    if structure_string != "":
                        structure_string += ")"

                if i != len(res_us_list) - 1:
                    us_res_list += "Area:" + str(res_us_list[i].area) + ",US:" + str(
                        res_us_list[i].us) + structure_string + ", "  # .append("Area:"+str(i.area) + ",US:"+str(i.us))
                else:
                    us_res_list += "Area:" + str(res_us_list[i].area) + ",US:" + str(
                        res_us_list[i].us) + structure_string  # .append("Area:"+str(i.area) + ",US:"+str(i.us))

                    # us_res_list.sort()
                    # inserisce l'elenco delle us
            single_cassa.append(us_res_list)

            ###cerca il luogo di conservazione della cassa
            params_dict = {'sito': '"' + str(self.sito_ec) + '"', 'nr_cassa': '"' + str(cassa) + '"'}
            res_luogo_conservazione = self.DB_MANAGER.query_bool(params_dict, 'CAMPIONI')
            luogo_conservazione = res_luogo_conservazione[0].luogo_conservazione
            single_cassa.append(luogo_conservazione)  # inserisce la sigla di cassa

            data_for_pdf.append(single_cassa)

            # QMessageBox.warning(self,'tk',str(data_for_pdf), QMessageBox.Ok)
        return data_for_pdf

    def generate_list_pdf(self):
        data_list = []
        for i in range(len(self.DATA_LIST)):
            if str(self.DATA_LIST[i].nr_campione) == 'None':
                numero_campione = ''
            else:
                numero_campione = str(self.DATA_LIST[i].nr_campione)

            if str(self.DATA_LIST[i].us) == 'None':
                us = ''
            else:
                us = str(self.DATA_LIST[i].us)

            if str(self.DATA_LIST[i].numero_inventario_materiale) == 'None':
                numero_inventario_materiale = ''
            else:
                numero_inventario_materiale = str(self.DATA_LIST[i].numero_inventario_materiale)

            if str(self.DATA_LIST[i].nr_cassa) == 'None':
                nr_cassa = ''
            else:
                nr_cassa = str(self.DATA_LIST[i].nr_cassa)

            data_list.append([
                str(self.DATA_LIST[i].sito),  # 1 - Sito
                str(numero_campione),  # 2 - Numero campione
                str(self.DATA_LIST[i].tipo_campione),  # 3 - Tipo campione
                str(self.DATA_LIST[i].descrizione),  # 4 - Descrizione
                str(self.DATA_LIST[i].area),  # 5 - Area
                str(us),  # 6 - us
                str(numero_inventario_materiale),  # 7 - numero inventario materiale
                str(self.DATA_LIST[i].luogo_conservazione),  # 8 - luogo_conservazione
                str(nr_cassa)  # 9 - nr cassa
            ])

        return data_list

    def update_if(self, msg):
        rec_corr = self.REC_CORR
        if msg == QMessageBox.Ok:
            test = self.update_record()
            if test == 1:
                id_list = []
                for i in self.DATA_LIST:
                    id_list.append(eval("i." + self.ID_TABLE))
                self.DATA_LIST = []
                if self.SORT_STATUS == "n":
                    temp_data_list = self.DB_MANAGER.query_sort(id_list, [self.ID_TABLE], 'asc',
                                                                self.MAPPER_TABLE_CLASS,
                                                                self.ID_TABLE)  # self.DB_MANAGER.query_bool(self.SEARCH_DICT_TEMP, self.MAPPER_TABLE_CLASS) #
                else:
                    temp_data_list = self.DB_MANAGER.query_sort(id_list, self.SORT_ITEMS_CONVERTED, self.SORT_MODE,
                                                                self.MAPPER_TABLE_CLASS, self.ID_TABLE)
                for i in temp_data_list:
                    self.DATA_LIST.append(i)
                self.BROWSE_STATUS = "b"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                if type(self.REC_CORR) == "<type 'str'>":
                    corr = 0
                else:
                    corr = self.REC_CORR
                return 1
            elif test == 0:
                return 0

                # custom functions

    def charge_records(self):
        self.DATA_LIST = []
        id_list = []
        for i in self.DB_MANAGER.query(self.MAPPER_TABLE_CLASS):
            id_list.append(eval("i." + self.ID_TABLE))

        temp_data_list = self.DB_MANAGER.query_sort(id_list, [self.ID_TABLE], 'asc', self.MAPPER_TABLE_CLASS,
                                                    self.ID_TABLE)
        for i in temp_data_list:
            self.DATA_LIST.append(i)

    def datestrfdate(self):
        now = date.today()
        today = now.strftime("%d-%m-%Y")
        return today

    def table2dict(self, n):
        self.tablename = n
        row = eval(self.tablename + ".rowCount()")
        col = eval(self.tablename + ".columnCount()")
        lista = []
        for r in range(row):
            sub_list = []
            for c in range(col):
                value = eval(self.tablename + ".item(r,c)")
                if bool(value):
                    sub_list.append(str(value.text()))
            lista.append(sub_list)
        return lista

    def empty_fields(self):
        self.comboBox_sito.setEditText("")  # 1 - Sito
        self.lineEdit_nr_campione.clear()  # 2 - Nr campione
        self.comboBox_tipo_campione.setEditText("")  # 3 - Sito
        self.textEdit_descrizione_camp.clear()  # 4 - descrizione
        self.lineEdit_nr_campione.clear()  # 5 - Nr campione
        self.lineEdit_area.clear()  # 6 - area
        self.lineEdit_us.clear()  # 7 - us
        self.lineEdit_n_inv_mat.clear()  # 8 - numero inventario_materiale
        self.lineEdit_luogo_conservazione.clear()  # 9 - luogo di conservazione
        self.lineEdit_cassa.clear()  # 10 - cassa

    def fill_fields(self, n=0):
        self.rec_num = n
        if str(self.DATA_LIST[self.rec_num].nr_campione) == 'None':
            numero_campione = ''
        else:
            numero_campione = str(self.DATA_LIST[self.rec_num].nr_campione)

        if str(self.DATA_LIST[self.rec_num].us) == 'None':
            us = ''
        else:
            us = str(self.DATA_LIST[self.rec_num].us)

        if str(self.DATA_LIST[self.rec_num].numero_inventario_materiale) == 'None':
            numero_inventario_materiale = ''
        else:
            numero_inventario_materiale = str(self.DATA_LIST[self.rec_num].numero_inventario_materiale)

        if str(self.DATA_LIST[self.rec_num].nr_cassa) == 'None':
            nr_cassa = ''
        else:
            nr_cassa = str(self.DATA_LIST[self.rec_num].nr_cassa)

        str(self.comboBox_sito.setEditText(self.DATA_LIST[self.rec_num].sito))  # 1 - Sito
        str(self.lineEdit_nr_campione.setText(numero_campione))  # 2 - Numero campione
        str(self.comboBox_tipo_campione.setEditText(self.DATA_LIST[self.rec_num].tipo_campione))  # 3 - Tipo campione
        str(self.textEdit_descrizione_camp.setText(self.DATA_LIST[self.rec_num].descrizione))  # 4 - Descrizione
        str(self.lineEdit_area.setText(self.DATA_LIST[self.rec_num].area))  # 5 - Area
        str(self.lineEdit_us.setText(us))  # 6 - us
        str(self.lineEdit_n_inv_mat.setText(numero_inventario_materiale))  # 7 - numero inventario materiale
        str(self.lineEdit_luogo_conservazione.setText(
            self.DATA_LIST[self.rec_num].luogo_conservazione))  # 8 - luogo_conservazione
        str(self.lineEdit_cassa.setText(nr_cassa))  # 9 - nr cassa

    def set_rec_counter(self, t, c):
        self.rec_tot = t
        self.rec_corr = c
        self.label_rec_tot.setText(str(self.rec_tot))
        self.label_rec_corrente.setText(str(self.rec_corr))

    def set_LIST_REC_TEMP(self):

        if self.lineEdit_nr_campione.text() == "":
            nr_campione = None
        else:
            nr_campione = int(self.lineEdit_nr_campione.text())

        if self.lineEdit_us.text() == "":
            us = None
        else:
            us = int(self.lineEdit_us.text())

        if self.lineEdit_cassa.text() == "":
            nr_cassa = None
        else:
            nr_cassa = int(self.lineEdit_cassa.text())

        if self.lineEdit_n_inv_mat.text() == "":
            numero_inventario_materiale = None
        else:
            numero_inventario_materiale = int(self.lineEdit_n_inv_mat.text())

            # data
        self.DATA_LIST_REC_TEMP = [
            str(self.comboBox_sito.currentText()),  # 1 - Sito
            str(nr_campione),  # 2 - nr campione
            str(self.comboBox_tipo_campione.currentText()),  # 3 - tipo campione
            str(self.textEdit_descrizione_camp.toPlainText()),  # 4 - descrizione
            str(self.lineEdit_area.text()),  # 5 - area
            str(us),  # 6 - us
            str(numero_inventario_materiale),  # 7 - numero_inventario_materiale
            str(nr_cassa),  # 8 - numero cassa
            str(self.lineEdit_luogo_conservazione.text())  # 9 - luogo conservazione
        ]

    def set_LIST_REC_CORR(self):
        self.DATA_LIST_REC_CORR = []
        for i in self.TABLE_FIELDS:
            self.DATA_LIST_REC_CORR.append(eval("unicode(self.DATA_LIST[self.REC_CORR]." + i + ")"))

    def setComboBoxEnable(self, f, v):
        field_names = f
        value = v

        for fn in field_names:
            cmd = '{}{}{}{}'.format(fn, '.setEnabled(', v, ')')
            eval(cmd)

    def setComboBoxEditable(self, f, n):
        field_names = f
        value = n

        for fn in field_names:
            cmd = ('%s%s%d%s') % (fn, '.setEditable(', n, ')')
            eval(cmd)

    def rec_toupdate(self):
        rec_to_update = self.UTILITY.pos_none_in_list(self.DATA_LIST_REC_TEMP)
        return rec_to_update

    def records_equal_check(self):
        self.set_LIST_REC_TEMP()
        self.set_LIST_REC_CORR()

        if self.DATA_LIST_REC_CORR == self.DATA_LIST_REC_TEMP:
            return 0
        else:
            return 1

    def update_record(self):
        try:
            self.DB_MANAGER.update(self.MAPPER_TABLE_CLASS,
                                   self.ID_TABLE,
                                   [eval("int(self.DATA_LIST[self.REC_CORR]." + self.ID_TABLE + ")")],
                                   self.TABLE_FIELDS,
                                   self.rec_toupdate())
            return 1
        except Exception as e:
            QMessageBox.warning(self, "Messaggio",
                                "Problema di encoding: sono stati inseriti accenti o caratteri non accettati dal database. Se chiudete ora la scheda senza correggere gli errori perderete i dati. Fare una copia di tutto su un foglio word a parte. Errore :" + str(
                                    e), QMessageBox.Ok)
            return 0

    def testing(self, name_file, message):
        f = open(str(name_file), 'w')
        f.write(str(message))
        f.close()


## Class end

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = pyarchinit_US()
    ui.show()
    sys.exit(app.exec_())
