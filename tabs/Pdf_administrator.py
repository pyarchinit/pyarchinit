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

from gui.sortpanelmain import SortPanelMain
from .US_USM import pyarchinit_US
from ..modules.db.pyarchinit_conn_strings import Connection
from ..modules.db.pyarchinit_db_manager import get_db_manager
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
            self.DB_MANAGER = get_db_manager(conn_str, use_singleton=True)
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
                                    QMessageBox.StandardButton.Ok)
                # QMessageBox.warning(self, "BENVENUTO", "lanciato da connect prima di charge list",  QMessageBox.Ok)
                self.BROWSE_STATUS = 'x'
                self.charge_list()
                self.on_pushButton_new_rec_pressed()
        except Exception as e:
            e = str(e)
            if e.find("no such table"):
                QMessageBox.warning(self, "Alert",
                                    "La connessione e' fallita <br><br> Tabella non presente. E' NECESSARIO RIAVVIARE QGIS" + str(
                                        e), QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.warning(self, "Alert",
                                    "Attenzione rilevato bug! Segnalarlo allo sviluppatore<br> Errore: <br>" + str(e),
                                    QMessageBox.StandardButton.Ok)

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
        QMessageBox.warning(self, "Alert", str(self.ID_LIST), QMessageBox.StandardButton.Ok)

        # buttons functions

    def on_pushButton_sort_pressed(self):
        dlg = SortPanelMain(self)
        dlg.insertItems(self.SORT_ITEMS)
        dlg.exec()

        items, order_type = dlg.ITEMS, dlg.TYPE_ORDER

        self.SORT_ITEMS_CONVERTED = []
        for i in items:
            self.SORT_ITEMS_CONVERTED.append(self.CONVERSION_DICT[str(i)])

        self.SORT_MODE = order_type
        self.empty_fields()

        id_list = []
        for i in self.DATA_LIST:
            id_list.append(getattr(i, self.ID_TABLE))
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
                                                       QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))

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
                                        QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))
                self.label_sort.setText(self.SORTED_ITEMS["n"])
                self.enable_button(1)
            else:
                QMessageBox.warning(self, "ATTENZIONE", "Non è stata realizzata alcuna modifica.", QMessageBox.StandardButton.Ok)
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
                QMessageBox.warning(self, "Errore", "Attenzione 1 ! \n" + str(msg), QMessageBox.StandardButton.Ok)
                return 0
        except Exception as e:
            QMessageBox.warning(self, "Errore", "Attenzione 2 ! \n" + str(e), QMessageBox.StandardButton.Ok)
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
                                    QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))
        try:
            self.empty_fields()
            self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0

            self.fill_fields(0)
            self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
        except Exception as e:
            QMessageBox.warning(self, "Errore", str(e), QMessageBox.StandardButton.Ok)

    def on_pushButton_last_rec_pressed(self):
        if self.records_equal_check() == 1:
            self.update_if(
                QMessageBox.warning(self, 'Errore', "Il record e' stato modificato. Vuoi salvare le modifiche?",
                                    QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))
        try:
            self.empty_fields()
            self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), len(self.DATA_LIST) - 1

            self.fill_fields(self.REC_CORR)
            self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
        except Exception as e:
            QMessageBox.warning(self, "Errore", str(e), QMessageBox.StandardButton.Ok)

    def on_pushButton_prev_rec_pressed(self):
        if self.records_equal_check() == 1:
            self.update_if(
                QMessageBox.warning(self, 'Errore', "Il record e' stato modificato. Vuoi salvare le modifiche?",
                                    QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))

        self.REC_CORR = self.REC_CORR - 1
        if self.REC_CORR == -1:
            self.REC_CORR = 0
            QMessageBox.warning(self, "Errore", "Sei al primo record!", QMessageBox.StandardButton.Ok)
        else:
            try:
                self.empty_fields()

                self.fill_fields(self.REC_CORR)
                self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
            except Exception as e:
                QMessageBox.warning(self, "Errore", str(e), QMessageBox.StandardButton.Ok)

    def on_pushButton_next_rec_pressed(self):

        if self.records_equal_check() == 1:
            self.update_if(
                QMessageBox.warning(self, 'Errore', "Il record e' stato modificato. Vuoi salvare le modifiche?",
                                    QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))

        self.REC_CORR = self.REC_CORR + 1
        if self.REC_CORR >= self.REC_TOT:
            self.REC_CORR = self.REC_CORR - 1
            QMessageBox.warning(self, "Errore", "Sei all'ultimo record!", QMessageBox.StandardButton.Ok)
        else:
            try:
                self.empty_fields()

                self.fill_fields(self.REC_CORR)
                self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
            except Exception as e:
                QMessageBox.warning(self, "Errore", str(e), QMessageBox.StandardButton.Ok)

    def on_pushButton_delete_pressed(self):
        msg = QMessageBox.warning(self, "Attenzione!!!",
                                  "Vuoi veramente eliminare il record? \n L'azione e' irreversibile",
                                  QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        if msg == QMessageBox.StandardButton.Cancel:
            QMessageBox.warning(self, "Messagio!!!", "Azione Annullata!")
        else:
            try:
                id_to_delete = getattr(self.DATA_LIST[self.REC_CORR], self.ID_TABLE)
                self.DB_MANAGER.delete_one_record(self.TABLE_NAME, self.ID_TABLE, id_to_delete)
                self.charge_records()  # charge records from DB
                QMessageBox.warning(self, "Messaggio!!!", "Record eliminato!")
                self.charge_list()
            except:
                QMessageBox.warning(self, "Attenzione", "Il database e' vuoto!", QMessageBox.StandardButton.Ok)

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
                                               QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))
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
        if msg == QMessageBox.StandardButton.Ok:
            self.update_record()
            id_list = []
            for i in self.DATA_LIST:
                id_list.append(getattr(i, self.ID_TABLE))
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
            id_list.append(getattr(i, self.ID_TABLE))
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
                str(getattr(self.DATA_LIST[self.REC_CORR], i)))

    def setComboBoxEnable(self, f, v):
        """Set enabled state for widgets - uses getattr instead of eval for security"""
        for fn in field_names:
            cmd = '{}{}{}{}'.format(fn, '.setEnabled(', v, ')')
            eval(cmd)

    def setComboBoxEditable(self, f, n):
        """Set editable state for widgets - uses getattr instead of eval for security"""
        for fn in f:
            widget_name = fn.replace('self.' , '') if fn.startswith('self.' ) else fn
            widget = getattr(self, widget_name, None)
            if widget is not None:
                widget.setEditable(bool(n))


## Class end

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = pyarchinit_US()
    ui.show()
    sys.exit(app.exec())
