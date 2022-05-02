#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
/***************************************************************************
    pyArchInit Plugin  - A QGIS plugin to manage archaeological dataset stored in Postgres

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
from datetime import date

import sys
from builtins import range
from builtins import str

from gui.sortpanelmain import SortPanelMain
from .US_USM import pyarchinit_US
from ..modules.db.pyarchinit_conn_strings import Connection
from ..modules.db.pyarchinit_db_manager import Pyarchinit_db_management
from ..modules.db.pyarchinit_utility import Utility

MAIN_DIALOG_CLASS, _ = loadUiType(
    os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'Pdf_administrator.ui'))


class pyarchinit_PDFAdministrator(QDialog, MAIN_DIALOG_CLASS):
    MSG_BOX_TITLE = "PyArchInit - pyarchinit_version 0.4 - Gestione PDF"
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
    TABLE_NAME = 'pdf_administrator_table'
    MAPPER_TABLE_CLASS = "PDF_ADMINISTRATOR"
    NOME_SCHEDA = "Gestione PDF"
    ID_TABLE = "id_pdf_administrator"
    CONVERSION_DICT = {
        ID_TABLE: ID_TABLE,
        "Nome tabella": "table_name",  # 1
        "Schema griglia": "schema_griglia",  # 2
        "Schema fusione celle": "schema_fusione_celle",  # 3
        "Modello": "modello"  # 4
    }
    SORT_ITEMS = [
        "Nome tabella",  # 1
        "Schema griglia",  # 2
        "Schema fusione celle",  # 3
        "Modello"  # 4
    ]

    TABLE_FIELDS = [
        "table_name",  # 1
        "schema_griglia",  # 2
        "schema_fusione_celle",  # 3
        "modello"  # 4
    ]
    ROW = 0
    COL = 0
    TABLE_NAME = ''
    TABLE_NAME_DICT = {'site_table': 'Sito',
                       'us_table': 'US',
                       'periodizzazione_table': 'Periodizzazione'}
    ID_LIST = ''

    def __init__(self, parent=None, db=None):
        super().__init__()
        self.setupUi(self)
        ##  def __init__(self, iface):
        ##      self.iface = iface
        ##      #self.pyQGIS = Pyarchinit_pyqgis(self.iface)
        ##      QDialog.__init__(self)
        ##      self.setupUi(self)
        self.currentLayerId = None
        # self.on_pushButton_connect_pressed()
        self.tableWidget_schema_griglia.itemSelectionChanged.connect(self.cellchanged)

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

    def connect(self):
        from pyarchinit_conn_strings import *
        conn = Connection()
        conn_str = conn.conn_str()
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
                self.fill_fields()
            else:
                QMessageBox.warning(self, "BENVENUTO",
                                    "Benvenuto in pyArchInit" + self.NOME_SCHEDA + ". Il database e' vuoto. Premi 'Ok' e buon lavoro!",
                                    QMessageBox.Ok)
                # QMessageBox.warning(self, "BENVENUTO", "lanciato da connect prima di charge list",  QMessageBox.Ok)
                self.BROWSE_STATUS = 'x'
                self.charge_list()
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

    def cellchanged(self):
        self.ROW = self.tableWidget_schema_griglia.currentRow()
        self.COL = self.tableWidget_schema_griglia.currentColumn()

    def on_pushButton_inserisci_nome_campo_pressed(self):
        # a = self.tableWidget_schema_griglia.item()
        # QMessageBox.warning(self, "Alert", str(self.ROW),  QMessageBox.Ok)
        item = QTableWidgetItem(str(self.comboBox_elenco_campi.currentText()))
        exec_str = ('self.tableWidget_schema_griglia.setItem(%d,%d,item)') % (self.ROW, self.COL)
        eval(exec_str)

    def cell_click_ed(self):
        pass

        # QMessageBox.warning(self, "Test table click" , QMessageBox.Ok)

    def set_table_name(self, tname):
        self.TABLE_NAME = tname
        self.label_tabella_corrente.setText(str(self.TABLE_NAME_DICT[self.TABLE_NAME]))  # 1 - nome_tabella

    def charge_list(self):
        fields_list = self.DB_MANAGER.fields_list(str(self.TABLE_NAME))
        try:
            fields_list.remove('')
        except:
            pass
        self.comboBox_elenco_campi.clear()
        fields_list.sort()
        self.comboBox_elenco_campi.addItems(fields_list)

    def add_id_list(self, id_list):
        self.ID_LIST = id_list

    def on_pushButton_charge_default_schema_pressed(self):
        default_schema = """[["C0R0", "C1R0", "C2R0", "C3R0", "C4R0", "C5R0", "C6R0", "C7R0", "C8R0"],
                                    ["C0R1", "C1R1", "C2R1", "C3R1", "C4R1", "C5R1", "C6R1", "C7R1", "C8R1"],
                                    ["C0R2", "C1R2", "C2R2", "C3R2", "C4R2", "C5R2", "C6R2", "C7R2", "C8R2"],
                                    ["C0R3", "C1R3", "C2R3", "C3R3", "C4R3", "C5R3", "C6R3", "C7R3", "C8R3"],
                                    ["C0R4", "C1R4", "C2R4", "C3R4", "C4R4", "C5R4", "C6R4", "C7R4", "C8R4"],
                                    ["C0R5", "C1R5", "C2R5", "C3R5", "C4R4", "C5R5", "C6R5", "C7R5", "C8R5"],
                                    ["C0R6", "C1R6", "C2R6", "C3R6", "C4R4", "C5R6", "C6R6", "C7R6", "C8R6"]]"""

        self.tableInsertData('self.tableWidget_schema_griglia', default_schema)
        QMessageBox.warning(self, "Alert", str(self.ID_LIST), QMessageBox.Ok)

        # buttons functions

    def on_pushButton_sort_pressed(self):
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
        if self.BROWSE_STATUS == "b":
            if bool(self.DATA_LIST):
                if self.records_equal_check() == 1:
                    self.update_if(QMessageBox.warning(self,
                                                       'Errore',
                                                       "Il record e' stato modificato. Vuoi salvare le modifiche?",
                                                       QMessageBox.Ok | QMessageBox.Cancel))

                    # set the GUI for a new record
        if self.BROWSE_STATUS != "n":
            self.BROWSE_STATUS = "n"
            self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
            self.empty_fields()
            self.label_sort.setText(self.SORTED_ITEMS["n"])
            self.set_rec_counter('', '')
            self.enable_button(0)

    def on_pushButton_save_pressed(self):
        # save record
        if self.BROWSE_STATUS == "b":
            if self.records_equal_check() == 1:
                self.update_if(
                    QMessageBox.warning(self, 'ATTENZIONE', "Il record e' stato modificato. Vuoi salvare le modifiche?",
                                        QMessageBox.Ok | QMessageBox.Cancel))
                self.label_sort.setText(self.SORTED_ITEMS["n"])
                self.enable_button(1)
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

                    self.fill_fields(self.REC_CORR)
                    self.enable_button(1)
                else:
                    pass

    def data_error_check(self):
        test = 0
        ##      EC = Error_check()
        ##
        ##      if EC.data_is_empty(unicode(self.comboBox_sito.currentText())) == 0:
        ##          QMessageBox.warning(self, "ATTENZIONE", "Campo Sito. \n Il campo non deve essere vuoto",  QMessageBox.Ok)
        ##          test = 1
        ##
        return test

    def insert_new_rec(self):
        # TableWidget
        ##Rapporti
        schema_griglia = self.table2dict("self.tableWidget_schema_griglia")
        schema_fusione_celle = self.table2dict("self.tableWidget_gestione_celle")
        try:
            data = self.DB_MANAGER.insert_pdf_administrator_values(
                self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, self.ID_TABLE) + 1,
                str(self.label_tabella_corrente.text()),  # 1 - nome_tabella
                str(schema_griglia),  # 2 - schema_griglia
                str(schema_fusione_celle),  # 3 - schema_fusione_celle
                str(self.comboBox_modello.currentText()))  # 4 - modello
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

    def on_pushButton_view_all_pressed(self):
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
        if self.records_equal_check() == 1:
            self.update_if(
                QMessageBox.warning(self, 'Errore', "Il record e' stato modificato. Vuoi salvare le modifiche?",
                                    QMessageBox.Ok | QMessageBox.Cancel))
        try:
            self.empty_fields()
            self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0

            self.fill_fields(0)
            self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
        except Exception as e:
            QMessageBox.warning(self, "Errore", str(e), QMessageBox.Ok)

    def on_pushButton_last_rec_pressed(self):
        if self.records_equal_check() == 1:
            self.update_if(
                QMessageBox.warning(self, 'Errore', "Il record e' stato modificato. Vuoi salvare le modifiche?",
                                    QMessageBox.Ok | QMessageBox.Cancel))
        try:
            self.empty_fields()
            self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), len(self.DATA_LIST) - 1

            self.fill_fields(self.REC_CORR)
            self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
        except Exception as e:
            QMessageBox.warning(self, "Errore", str(e), QMessageBox.Ok)

    def on_pushButton_prev_rec_pressed(self):
        if self.records_equal_check() == 1:
            self.update_if(
                QMessageBox.warning(self, 'Errore', "Il record e' stato modificato. Vuoi salvare le modifiche?",
                                    QMessageBox.Ok | QMessageBox.Cancel))

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

        if self.records_equal_check() == 1:
            self.update_if(
                QMessageBox.warning(self, 'Errore', "Il record e' stato modificato. Vuoi salvare le modifiche?",
                                    QMessageBox.Ok | QMessageBox.Cancel))

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
                                  "Vuoi veramente eliminare il record? \n L'azione e' irreversibile",
                                  QMessageBox.Ok | QMessageBox.Cancel)
        if msg == QMessageBox.Cancel:
            QMessageBox.warning(self, "Messagio!!!", "Azione Annullata!")
        else:
            try:
                id_to_delete = eval("self.DATA_LIST[self.REC_CORR]." + self.ID_TABLE)
                self.DB_MANAGER.delete_one_record(self.TABLE_NAME, self.ID_TABLE, id_to_delete)
                self.charge_records()  # charge records from DB
                QMessageBox.warning(self, "Messaggio!!!", "Record eliminato!")
                self.charge_list()
            except:
                QMessageBox.warning(self, "Attenzione", "Il database e' vuoto!", QMessageBox.Ok)

            if not bool(self.DATA_LIST):
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

                self.fill_fields()
                self.BROWSE_STATUS = "b"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
        self.label_sort.setText(self.SORTED_ITEMS["n"])

    def on_pushButton_new_search_pressed(self):
        # self.setComboBoxEditable()
        if self.records_equal_check() == 1 and self.BROWSE_STATUS == "b":
            self.update_if(QMessageBox.warning(self, 'Errore',
                                               "Il record e' stato modificato. Vuoi salvare le modifiche?",
                                               QMessageBox.Ok | QMessageBox.Cancel))
            # else:
        self.enable_button_search(0)

        # set the GUI for a new search
        if self.BROWSE_STATUS != "f":
            self.BROWSE_STATUS = "f"
            self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
            self.empty_fields()
            self.set_rec_counter('', '')
            self.label_sort.setText(self.SORTED_ITEMS["n"])

    def on_pushButton_search_go_pressed(self):
        pass

    def update_if(self, msg):
        rec_corr = self.REC_CORR
        if msg == QMessageBox.Ok:
            self.update_record()
            id_list = []
            for i in self.DATA_LIST:
                id_list.append(eval("i." + self.ID_TABLE))
            self.DATA_LIST = []
            if self.SORT_STATUS == "n":
                temp_data_list = self.DB_MANAGER.query_sort(id_list, [self.ID_TABLE], 'asc', self.MAPPER_TABLE_CLASS,
                                                            self.ID_TABLE)
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

                # custom functions

    def charge_records(self):
        self.DATA_LIST = []
        id_list = []
        for i in self.DB_MANAGER.query(eval(self.MAPPER_TABLE_CLASS)):
            id_list.append(eval("i." + self.ID_TABLE))
        temp_data_list = self.DB_MANAGER.query_sort(id_list, [self.ID_TABLE], 'asc', self.MAPPER_TABLE_CLASS,
                                                    self.ID_TABLE)
        for i in temp_data_list:
            self.DATA_LIST.append(i)

    def datestrfdate(self):
        now = date.today()
        today = now.strftime("%d-%m-%Y")
        return today

    def empty_fields(self):
        schema_griglia = self.tableWidget_schema_griglia.rowCount()
        schema_fusione_celle = self.tableWidget_gestione_celle.rowCount()

        for i in range(schema_griglia):
            self.tableWidget_schema_griglia.removeRow(0)
            # self.insert_new_row("self.tableWidget_schema_griglia")

        for i in range(schema_fusione_celle):
            self.tableWidget_schema_griglia.removeRow(0)
            # self.insert_new_row("self.tableWidget_gestione_celle")

        self.comboBox_modello.setEditText("")

    def fill_fields(self, n=0):
        self.rec_num = n
        str(self.label_tabella_corrente.setText(self.DATA_LIST[self.rec_num].table_name))  # 1 - Nome tabella
        self.tableInsertData("self.tableWidget_schema_griglia",
                             self.DATA_LIST[self.rec_num].schema_griglia)  # 2 - Schema Griglia
        self.tableInsertData("self.tableWidget_gestione_celle",
                             self.DATA_LIST[self.rec_num].schema_fusione_celle)  # 3 - Schema Fusione
        self.comboBox_modello.setEditText(self.DATA_LIST[self.rec_num].modello)  # 4 - modello
        self.charge_list()

    def set_rec_counter(self, t, c):
        self.rec_tot = t
        self.rec_corr = c
        self.label_rec_tot.setText(str(self.rec_tot))
        self.label_rec_corrente.setText(str(self.rec_corr))

    def set_LIST_REC_TEMP(self):

        # TableWidget
        ##Rapporti
        schema_griglia = self.table2dict("self.tableWidget_schema_griglia")
        schema_fusione_celle = self.table2dict("self.tableWidget_gestione_celle")
        self.DATA_LIST_REC_TEMP = [
            str(self.label_tabella_corrente.text()),  # 1 - nome_tabella
            str(schema_griglia),  # 2 - schema_griglia
            str(schema_fusione_celle),  # 3 - schema fusione celle
            str(self.comboBox_modello.currentText())]  # 4 - modello

    def set_LIST_REC_CORR(self):
        self.DATA_LIST_REC_CORR = []
        for i in self.TABLE_FIELDS:
            self.DATA_LIST_REC_CORR.append(
                eval("unicode(self.DATA_LIST[self.REC_CORR]." + i + ")"))

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
            cmd = '{}{}{}{}'.format(fn, '.setEditable(', n, ')')
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
        self.DB_MANAGER.update(self.MAPPER_TABLE_CLASS,
                               self.ID_TABLE,
                               [eval(
                                   "int(self.DATA_LIST[self.REC_CORR]." + self.ID_TABLE + ")")],
                               self.TABLE_FIELDS,
                               self.rec_toupdate())

    def testing(self, name_file, message):
        f = open(str(name_file), 'w')
        f.write(str(message))
        f.close()

    def table2dict(self, n):
        self.tablename = n
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

    def tableInsertData(self, t, d):
        """Set the value into alls Grid"""
        self.table_name = t
        self.data_list = eval(d)
        self.data_list.sort()

        table_col_count_cmd = ("%s.columnCount()") % (self.table_name)
        table_col_count = eval(table_col_count_cmd)

        # clear table
        table_clear_cmd = ("%s.clearContents()") % (self.table_name)
        eval(table_clear_cmd)

        for i in range(table_col_count):
            table_rem_row_cmd = ("%s.removeRow(%d)") % (self.table_name, i)
            eval(table_rem_row_cmd)

            # for i in range(len(self.data_list)):
            # self.insert_new_row(self.table_name)
            # QMessageBox.warning(self,"Messagio!!!","numero_righe" + str(len(self.data_list)))
        for row in range(len(self.data_list)):
            cmd = ('%s.insertRow(%s)') % (self.table_name, row)
            eval(cmd)
            # QMessageBox.warning(self,"Messagio!!!","numero colonne" + str(len(self.data_list[row])))
            for col in range(len(self.data_list[row])):
                # item = self.comboBox_sito.setEditText(self.data_list[0][col]
                item = QTableWidgetItem(str(self.data_list[row][col]))
                exec_str = ('%s.setItem(%d,%d,item)') % (self.table_name, row, col)
                eval(exec_str)

    def on_pushButton_add_row_griglia_pressed(self):
        self.insert_new_row('self.tableWidget_schema_griglia')

    def on_pushButton_remove_row_griglia_pressed(self):
        self.remove_row('self.tableWidget_schema_griglia')

    def on_pushButton_add_row_cell_pressed(self):
        self.insert_new_row('self.tableWidget_gestione_celle')

    def on_pushButton_remove_row_cell_pressed(self):
        self.remove_row('self.tableWidget_gestione_celle')

    def insert_new_row(self, table_name):
        """insert new row into a table based on table_name"""
        cmd = table_name + ".insertRow(0)"
        eval(cmd)

    def remove_row(self, table_name):
        """insert new row into a table based on table_name"""
        table_row_count_cmd = ("%s.rowCount()") % (table_name)
        table_row_count = eval(table_row_count_cmd)
        rowSelected_cmd = ("%s.selectedIndexes()") % (table_name)
        rowSelected = eval(rowSelected_cmd)
        rowIndex = (rowSelected[0].row())
        cmd = ("%s.removeRow(%d)") % (table_name, rowIndex)
        eval(cmd)


## Class end

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = pyarchinit_US()
    ui.show()
    sys.exit(app.exec_())
