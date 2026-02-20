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

import os
import sys
from datetime import date
from qgis.PyQt.QtWidgets import QDialog, QMessageBox
from qgis.PyQt.uic import loadUiType
from qgis.core import QgsSettings

from ..gui.pyarchinitConfigDialog import pyArchInitDialog_Config
from ..gui.sortpanelmain import SortPanelMain
from ..modules.db.pyarchinit_conn_strings import Connection
from ..modules.db.pyarchinit_db_manager import get_db_manager
from ..modules.db.pyarchinit_utility import Utility
from ..modules.utility.pyarchinit_error_check import Error_check
from ..modules.utility.pyarchinit_theme_manager import ThemeManager

MAIN_DIALOG_CLASS, _ = loadUiType(
    os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'Budget.ui'))


class pyarchinit_Budget(QDialog, MAIN_DIALOG_CLASS):
    L = QgsSettings().value("locale/userLocale", "it", type=str)[:2]
    if L == 'it':
        MSG_BOX_TITLE = "PyArchInit - Scheda Budget"
    elif L == 'en':
        MSG_BOX_TITLE = "PyArchInit - Budget Form"
    elif L == 'de':
        MSG_BOX_TITLE = "PyArchInit - Budgetformular"
    else:
        MSG_BOX_TITLE = "PyArchInit - Budget Form"

    DATA_LIST = []
    DATA_LIST_REC_CORR = []
    DATA_LIST_REC_TEMP = []
    REC_CORR = 0
    REC_TOT = 0
    SITO = pyArchInitDialog_Config

    if L == 'it':
        STATUS_ITEMS = {"b": "Usa", "f": "Trova", "n": "Nuovo Record"}
    elif L == 'de':
        STATUS_ITEMS = {"b": "Aktuell", "f": "Finden", "n": "Neuer Rekord"}
    else:
        STATUS_ITEMS = {"b": "Current", "f": "Find", "n": "New Record"}

    BROWSE_STATUS = "b"
    SORT_MODE = 'asc'

    if L == 'it':
        SORTED_ITEMS = {"n": "Non ordinati", "o": "Ordinati"}
    elif L == 'de':
        SORTED_ITEMS = {"n": "Nicht sortiert", "o": "Sortiert"}
    else:
        SORTED_ITEMS = {"n": "Not sorted", "o": "Sorted"}

    SORT_STATUS = "n"
    UTILITY = Utility()
    DB_MANAGER = ""
    TABLE_NAME = 'budget_table'
    MAPPER_TABLE_CLASS = "BUDGET"
    NOME_SCHEDA = "Scheda Budget"
    ID_TABLE = "id_budget"

    if L == 'it':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Sito": "sito",
            "Anno": "anno",
            "Categoria": "categoria",
            "Descrizione": "descrizione",
            "Importo previsto": "importo_previsto",
            "Importo effettivo": "importo_effettivo",
            "Data registrazione": "data_registrazione",
            "Data spesa": "data_spesa",
            "Fornitore": "fornitore",
            "Numero fattura": "numero_fattura",
            "Note": "note"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Sito",
            "Anno",
            "Categoria",
            "Fornitore",
            "Data spesa"
        ]
    elif L == 'en':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Site": "sito",
            "Year": "anno",
            "Category": "categoria",
            "Description": "descrizione",
            "Estimated Amount": "importo_previsto",
            "Actual Amount": "importo_effettivo",
            "Registration Date": "data_registrazione",
            "Expense Date": "data_spesa",
            "Supplier": "fornitore",
            "Invoice Number": "numero_fattura",
            "Notes": "note"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Site",
            "Year",
            "Category",
            "Supplier",
            "Expense Date"
        ]
    elif L == 'de':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Fundort": "sito",
            "Jahr": "anno",
            "Kategorie": "categoria",
            "Beschreibung": "descrizione",
            "Geplanter Betrag": "importo_previsto",
            "Tatsaechlicher Betrag": "importo_effettivo",
            "Registrierungsdatum": "data_registrazione",
            "Ausgabendatum": "data_spesa",
            "Lieferant": "fornitore",
            "Rechnungsnummer": "numero_fattura",
            "Anmerkungen": "note"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Fundort",
            "Jahr",
            "Kategorie",
            "Lieferant",
            "Ausgabendatum"
        ]
    elif L == 'es':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Sitio": "sito",
            "Ano": "anno",
            "Categoria": "categoria",
            "Descripcion": "descrizione",
            "Importe previsto": "importo_previsto",
            "Importe efectivo": "importo_effettivo",
            "Fecha registro": "data_registrazione",
            "Fecha gasto": "data_spesa",
            "Proveedor": "fornitore",
            "Numero factura": "numero_fattura",
            "Notas": "note"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Sitio",
            "Ano",
            "Categoria",
            "Proveedor",
            "Fecha gasto"
        ]
    elif L == 'fr':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Site": "sito",
            "Annee": "anno",
            "Categorie": "categoria",
            "Description": "descrizione",
            "Montant prevu": "importo_previsto",
            "Montant effectif": "importo_effettivo",
            "Date enregistrement": "data_registrazione",
            "Date depense": "data_spesa",
            "Fournisseur": "fornitore",
            "Numero facture": "numero_fattura",
            "Notes": "note"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Site",
            "Annee",
            "Categorie",
            "Fournisseur",
            "Date depense"
        ]
    elif L == 'ar':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "موقع": "sito",
            "السنة": "anno",
            "الفئة": "categoria",
            "الوصف": "descrizione",
            "المبلغ المتوقع": "importo_previsto",
            "المبلغ الفعلي": "importo_effettivo",
            "تاريخ التسجيل": "data_registrazione",
            "تاريخ الإنفاق": "data_spesa",
            "المورد": "fornitore",
            "رقم الفاتورة": "numero_fattura",
            "ملاحظات": "note"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "موقع",
            "السنة",
            "الفئة",
            "المورد",
            "تاريخ الإنفاق"
        ]
    elif L == 'ca':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Jaciment": "sito",
            "Any": "anno",
            "Categoria": "categoria",
            "Descripcio": "descrizione",
            "Import previst": "importo_previsto",
            "Import efectiu": "importo_effettivo",
            "Data registre": "data_registrazione",
            "Data despesa": "data_spesa",
            "Proveidor": "fornitore",
            "Numero factura": "numero_fattura",
            "Notes": "note"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Jaciment",
            "Any",
            "Categoria",
            "Proveidor",
            "Data despesa"
        ]
    elif L == 'ro':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Sit": "sito",
            "An": "anno",
            "Categorie": "categoria",
            "Descriere": "descrizione",
            "Suma prevazuta": "importo_previsto",
            "Suma efectiva": "importo_effettivo",
            "Data inregistrare": "data_registrazione",
            "Data cheltuiala": "data_spesa",
            "Furnizor": "fornitore",
            "Numar factura": "numero_fattura",
            "Note": "note"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Sit",
            "An",
            "Categorie",
            "Furnizor",
            "Data cheltuiala"
        ]
    elif L == 'pt':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Sitio": "sito",
            "Ano": "anno",
            "Categoria": "categoria",
            "Descricao": "descrizione",
            "Valor previsto": "importo_previsto",
            "Valor efetivo": "importo_effettivo",
            "Data registo": "data_registrazione",
            "Data despesa": "data_spesa",
            "Fornecedor": "fornitore",
            "Numero fatura": "numero_fattura",
            "Notas": "note"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Sitio",
            "Ano",
            "Categoria",
            "Fornecedor",
            "Data despesa"
        ]
    elif L == 'el':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Θέση": "sito",
            "Έτος": "anno",
            "Κατηγορία": "categoria",
            "Περιγραφή": "descrizione",
            "Εκτιμώμενο ποσό": "importo_previsto",
            "Πραγματικό ποσό": "importo_effettivo",
            "Ημερομηνία καταχώρησης": "data_registrazione",
            "Ημερομηνία δαπάνης": "data_spesa",
            "Προμηθευτής": "fornitore",
            "Αριθμός τιμολογίου": "numero_fattura",
            "Σημειώσεις": "note"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Θέση",
            "Έτος",
            "Κατηγορία",
            "Προμηθευτής",
            "Ημερομηνία δαπάνης"
        ]
    else:
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Site": "sito",
            "Year": "anno",
            "Category": "categoria",
            "Description": "descrizione",
            "Estimated Amount": "importo_previsto",
            "Actual Amount": "importo_effettivo",
            "Registration Date": "data_registrazione",
            "Expense Date": "data_spesa",
            "Supplier": "fornitore",
            "Invoice Number": "numero_fattura",
            "Notes": "note"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Site",
            "Year",
            "Category",
            "Supplier",
            "Expense Date"
        ]

    TABLE_FIELDS = [
        'sito',
        'anno',
        'categoria',
        'descrizione',
        'importo_previsto',
        'importo_effettivo',
        'data_registrazione',
        'data_spesa',
        'fornitore',
        'numero_fattura',
        'note'
    ]

    DB_SERVER = "not defined"
    HOME = os.environ['PYARCHINIT_HOME']

    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.setupUi(self)

        ThemeManager.apply_theme(self)
        self.theme_toggle_btn = ThemeManager.add_theme_toggle_to_form(self)

        self.currentLayerId = None
        try:
            self.on_pushButton_connect_pressed()
        except:
            pass
        self.fill_fields()
        self.set_sito()
        self.msg_sito()

    def enable_button(self, n):
        self.pushButton_connect.setEnabled(n)
        self.pushButton_new_rec.setEnabled(n)
        self.pushButton_show_all.setEnabled(n)
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
        self.pushButton_show_all.setEnabled(n)
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
            self.DB_MANAGER = get_db_manager(conn_str, use_singleton=True)
            self.charge_records()
            if bool(self.DATA_LIST):
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                self.BROWSE_STATUS = "b"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.label_sort.setText(self.SORTED_ITEMS["n"])
                self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                self.charge_list()
                self.fill_fields()
            else:
                if self.L == 'it':
                    QMessageBox.warning(self, "BENVENUTO",
                        "Benvenuto in pyArchInit " + self.NOME_SCHEDA + ". Il database e' vuoto.",
                        QMessageBox.StandardButton.Ok)
                elif self.L == 'de':
                    QMessageBox.warning(self, "WILLKOMMEN",
                        "WILLKOMMEN in pyArchInit " + self.NOME_SCHEDA + ". Die Datenbank ist leer.",
                        QMessageBox.StandardButton.Ok)
                else:
                    QMessageBox.warning(self, "WELCOME",
                        "Welcome in pyArchInit " + self.NOME_SCHEDA + ". The DB is empty.",
                        QMessageBox.StandardButton.Ok)
                self.charge_list()
                self.BROWSE_STATUS = 'x'
                self.on_pushButton_new_rec_pressed()
        except Exception as e:
            e = str(e)
            if e.find("no such table"):
                if self.L == 'it':
                    msg = "La connessione e' fallita {}. E' NECESSARIO RIAVVIARE QGIS".format(str(e))
                elif self.L == 'de':
                    msg = "Verbindungsfehler {}. QGIS neustarten".format(str(e))
                else:
                    msg = "The connection failed {}. You MUST RESTART QGIS".format(str(e))

    def charge_list(self):
        sito_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('site_table', 'sito', 'SITE'))
        try:
            sito_vl.remove('')
        except:
            pass
        self.comboBox_sito.clear()
        sito_vl.sort()
        self.comboBox_sito.addItems(sito_vl)

    def msg_sito(self):
        conn = Connection()
        sito_set = conn.sito_set()
        sito_set_str = sito_set['sito_set']
        if bool(self.comboBox_sito.currentText()) and self.comboBox_sito.currentText() == sito_set_str:
            if self.L == 'it':
                QMessageBox.information(self, "OK", "Sei connesso al sito: %s" % str(sito_set_str), QMessageBox.StandardButton.Ok)
            elif self.L == 'de':
                QMessageBox.information(self, "OK", "Sie sind mit der Stätte verbunden: %s" % str(sito_set_str), QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.information(self, "OK", "You are connected to the site: %s" % str(sito_set_str), QMessageBox.StandardButton.Ok)
        elif sito_set_str == '':
            if self.L == 'it':
                msg = QMessageBox.information(self, "Attenzione", "Non hai settato alcun sito.",
                    QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            elif self.L == 'de':
                msg = QMessageBox.information(self, "Achtung", "Sie haben keine Stätten eingerichtet.",
                    QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            else:
                msg = QMessageBox.information(self, "Warning", "You have not set up any site.",
                    QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            if msg == QMessageBox.StandardButton.Cancel:
                pass
            else:
                dlg = pyArchInitDialog_Config(self)
                dlg.charge_list()
                dlg.exec()

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
                self.DATA_LIST = []
                for i in res:
                    self.DATA_LIST.append(i)
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                if len(self.DATA_LIST) == 0:
                    return
                self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                self.fill_fields()
                self.BROWSE_STATUS = "b"
                self.SORT_STATUS = "n"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                self.setComboBoxEnable(["self.comboBox_sito"], "False")
        except Exception as e:
            QMessageBox.warning(self, "Error", "Error: %s" % str(e), QMessageBox.StandardButton.Ok)

    def on_pushButton_sort_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
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
            self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
            self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
            self.SORT_STATUS = "o"
            self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
            self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
            self.fill_fields()

    def on_pushButton_new_rec_pressed(self):
        conn = Connection()
        sito_set = conn.sito_set()
        sito_set_str = sito_set['sito_set']
        if bool(self.DATA_LIST):
            if self.data_error_check() == 1:
                pass
            else:
                if self.BROWSE_STATUS == "b":
                    if bool(self.DATA_LIST):
                        if self.records_equal_check() == 1:
                            if self.L == 'it':
                                self.update_if(QMessageBox.warning(self, 'Errore',
                                    "Il record e' stato modificato. Vuoi salvare le modifiche?",
                                    QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))
                            elif self.L == 'de':
                                self.update_if(QMessageBox.warning(self, 'Error',
                                    "Der Record wurde geändert. Möchtest du die Änderungen speichern?",
                                    QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))
                            else:
                                self.update_if(QMessageBox.warning(self, 'Error',
                                    "The record has been changed. Do you want to save the changes?",
                                    QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))
        if self.BROWSE_STATUS != "n":
            if bool(self.comboBox_sito.currentText()) and self.comboBox_sito.currentText() == sito_set_str:
                self.BROWSE_STATUS = "n"
                self.setComboBoxEnable(["self.comboBox_sito"], "False")
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.set_rec_counter('', '')
                self.label_sort.setText(self.SORTED_ITEMS["n"])
                self.empty_fields_nosite()
            else:
                self.BROWSE_STATUS = "n"
                self.setComboBoxEnable(["self.comboBox_sito"], "True")
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.set_rec_counter('', '')
                self.label_sort.setText(self.SORTED_ITEMS["n"])
                self.empty_fields()
            self.enable_button(0)

    def on_pushButton_save_pressed(self):
        if self.BROWSE_STATUS == "b":
            if self.data_error_check() == 0:
                if self.records_equal_check() == 1:
                    if self.L == 'it':
                        self.update_if(QMessageBox.warning(self, 'Errore',
                            "Il record e' stato modificato. Vuoi salvare le modifiche?",
                            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))
                    elif self.L == 'de':
                        self.update_if(QMessageBox.warning(self, 'Error',
                            "Der Record wurde geändert. Möchtest du die Änderungen speichern?",
                            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))
                    else:
                        self.update_if(QMessageBox.warning(self, 'Error',
                            "The record has been changed. Do you want to save the changes?",
                            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))
                    self.SORT_STATUS = "n"
                    self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
                    self.enable_button(1)
                    self.fill_fields(self.REC_CORR)
                else:
                    if self.L == 'it':
                        QMessageBox.warning(self, "ATTENZIONE", "Non è stata realizzata alcuna modifica.", QMessageBox.StandardButton.Ok)
                    elif self.L == 'de':
                        QMessageBox.warning(self, "ACHTUNG", "Keine Änderung vorgenommen", QMessageBox.StandardButton.Ok)
                    else:
                        QMessageBox.warning(self, "Warning", "No changes have been made", QMessageBox.StandardButton.Ok)
        else:
            if self.data_error_check() == 0:
                test_insert = self.insert_new_rec()
                if test_insert == 1:
                    self.empty_fields()
                    self.SORT_STATUS = "n"
                    self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
                    self.charge_records()
                    self.charge_list()
                    self.set_sito()
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), len(self.DATA_LIST) - 1
                    self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
                    self.setComboBoxEnable(["self.comboBox_sito"], "False")
                    self.fill_fields(self.REC_CORR)
                    self.enable_button(1)

    def data_error_check(self):
        test = 0
        EC = Error_check()

        if self.L == 'it':
            if self.comboBox_sito.currentText() == "":
                QMessageBox.warning(self, "ATTENZIONE", "Campo Sito obbligatorio!", QMessageBox.StandardButton.Ok)
                test = 1
            if self.lineEdit_anno.text() == "":
                QMessageBox.warning(self, "ATTENZIONE", "Campo Anno obbligatorio!", QMessageBox.StandardButton.Ok)
                test = 1
            elif EC.data_is_int(self.lineEdit_anno.text()) == 0:
                QMessageBox.warning(self, "ATTENZIONE", "Campo Anno: il valore deve essere numerico", QMessageBox.StandardButton.Ok)
                test = 1
        elif self.L == 'de':
            if self.comboBox_sito.currentText() == "":
                QMessageBox.warning(self, "ACHTUNG", "Feld Fundort erforderlich!", QMessageBox.StandardButton.Ok)
                test = 1
            if self.lineEdit_anno.text() == "":
                QMessageBox.warning(self, "ACHTUNG", "Feld Jahr erforderlich!", QMessageBox.StandardButton.Ok)
                test = 1
            elif EC.data_is_int(self.lineEdit_anno.text()) == 0:
                QMessageBox.warning(self, "ACHTUNG", "Feld Jahr: Der Wert muss numerisch sein", QMessageBox.StandardButton.Ok)
                test = 1
        else:
            if self.comboBox_sito.currentText() == "":
                QMessageBox.warning(self, "WARNING", "Site field required!", QMessageBox.StandardButton.Ok)
                test = 1
            if self.lineEdit_anno.text() == "":
                QMessageBox.warning(self, "WARNING", "Year field required!", QMessageBox.StandardButton.Ok)
                test = 1
            elif EC.data_is_int(self.lineEdit_anno.text()) == 0:
                QMessageBox.warning(self, "WARNING", "Year field: the value must be numeric", QMessageBox.StandardButton.Ok)
                test = 1

        return test

    def insert_new_rec(self):
        try:
            importo_previsto = None
            if self.lineEdit_importo_previsto.text():
                try:
                    importo_previsto = float(self.lineEdit_importo_previsto.text())
                except ValueError:
                    importo_previsto = None

            importo_effettivo = None
            if self.lineEdit_importo_effettivo.text():
                try:
                    importo_effettivo = float(self.lineEdit_importo_effettivo.text())
                except ValueError:
                    importo_effettivo = None

            data = self.DB_MANAGER.insert_budget_values(
                self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, self.ID_TABLE) + 1,
                str(self.comboBox_sito.currentText()),
                int(self.lineEdit_anno.text()),
                str(self.comboBox_categoria.currentText()),
                str(self.textEdit_descrizione.toPlainText()),
                importo_previsto,
                importo_effettivo,
                str(self.lineEdit_data_registrazione.text()),
                str(self.lineEdit_data_spesa.text()),
                str(self.lineEdit_fornitore.text()),
                str(self.lineEdit_numero_fattura.text()),
                str(self.textEdit_note.toPlainText()))

            try:
                self.DB_MANAGER.insert_data_session(data)
                return 1
            except Exception as e:
                e_str = str(e)
                if e_str.__contains__("IntegrityError"):
                    if self.L == 'it':
                        msg = self.ID_TABLE + " gia' presente nel database"
                    elif self.L == 'de':
                        msg = self.ID_TABLE + " bereits in der Datenbank"
                    else:
                        msg = self.ID_TABLE + " exist in db"
                    QMessageBox.warning(self, "Error", "Error" + str(msg), QMessageBox.StandardButton.Ok)
                else:
                    QMessageBox.warning(self, "Error", "Error 1 \n" + str(e), QMessageBox.StandardButton.Ok)
                return 0
        except Exception as e:
            QMessageBox.warning(self, "Error", "Error 2 \n" + str(e), QMessageBox.StandardButton.Ok)
            return 0

    def check_record_state(self):
        ec = self.data_error_check()
        if ec == 1:
            return 1
        elif self.records_equal_check() == 1 and ec == 0:
            if self.L == 'it':
                self.update_if(QMessageBox.warning(self, 'Errore',
                    "Il record e' stato modificato. Vuoi salvare le modifiche?",
                    QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))
            elif self.L == 'de':
                self.update_if(QMessageBox.warning(self, 'Errore',
                    "Der Record wurde geändert. Möchtest du die Änderungen speichern?",
                    QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))
            else:
                self.update_if(QMessageBox.warning(self, "Error",
                    "The record has been changed. You want to save the changes?",
                    QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))
            return 0

    def on_pushButton_view_all_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            self.empty_fields()
            self.charge_records()
            self.fill_fields()
            self.BROWSE_STATUS = "b"
            self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
            self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
            self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
            self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
            self.label_sort.setText(self.SORTED_ITEMS["n"])

    on_pushButton_show_all_pressed = on_pushButton_view_all_pressed

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
                QMessageBox.warning(self, "Error", str(e), QMessageBox.StandardButton.Ok)

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
                QMessageBox.warning(self, "Error", str(e), QMessageBox.StandardButton.Ok)

    def on_pushButton_prev_rec_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            self.REC_CORR = self.REC_CORR - 1
            if self.REC_CORR == -1:
                self.REC_CORR = 0
                if self.L == 'it':
                    QMessageBox.warning(self, "Attenzione", "Sei al primo record!", QMessageBox.StandardButton.Ok)
                elif self.L == 'de':
                    QMessageBox.warning(self, "Achtung", "du befindest dich im ersten Datensatz!", QMessageBox.StandardButton.Ok)
                else:
                    QMessageBox.warning(self, "Warning", "You are at the first record!", QMessageBox.StandardButton.Ok)
            else:
                try:
                    self.empty_fields()
                    self.fill_fields(self.REC_CORR)
                    self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
                except Exception as e:
                    QMessageBox.warning(self, "Error", str(e), QMessageBox.StandardButton.Ok)

    def on_pushButton_next_rec_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            self.REC_CORR = self.REC_CORR + 1
            if self.REC_CORR >= self.REC_TOT:
                self.REC_CORR = self.REC_CORR - 1
                if self.L == 'it':
                    QMessageBox.warning(self, "Attenzione", "Sei all'ultimo record!", QMessageBox.StandardButton.Ok)
                elif self.L == 'de':
                    QMessageBox.warning(self, "Achtung", "du befindest dich im letzten Datensatz!", QMessageBox.StandardButton.Ok)
                else:
                    QMessageBox.warning(self, "Warning", "You are at the last record!", QMessageBox.StandardButton.Ok)
            else:
                try:
                    self.empty_fields()
                    self.fill_fields(self.REC_CORR)
                    self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
                except Exception as e:
                    QMessageBox.warning(self, "Error", str(e), QMessageBox.StandardButton.Ok)

    def on_pushButton_delete_pressed(self):
        if self.L == 'it':
            msg = QMessageBox.warning(self, "Attenzione!!!", "Vuoi veramente eliminare il record?",
                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        elif self.L == 'de':
            msg = QMessageBox.warning(self, "Achtung!!!", "Willst du wirklich diesen Eintrag löschen?",
                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        else:
            msg = QMessageBox.warning(self, "Warning!!!", "Do you really want to delete the record?",
                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)

        if msg == QMessageBox.StandardButton.Cancel:
            return
        try:
            id_to_delete = getattr(self.DATA_LIST[self.REC_CORR], self.ID_TABLE)
            self.DB_MANAGER.delete_one_record(self.TABLE_NAME, self.ID_TABLE, id_to_delete)
            self.charge_records()
        except Exception as e:
            QMessageBox.warning(self, "Error", "error type: " + str(e))
        if not bool(self.DATA_LIST):
            self.DATA_LIST = []
            self.DATA_LIST_REC_CORR = []
            self.DATA_LIST_REC_TEMP = []
            self.REC_CORR = 0
            self.REC_TOT = 0
            self.empty_fields()
            self.set_rec_counter(0, 0)
        if bool(self.DATA_LIST):
            self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
            self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
            self.BROWSE_STATUS = "b"
            self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
            self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
            self.charge_list()
            self.fill_fields()
            self.set_sito()
        self.SORT_STATUS = "n"
        self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])

    def on_pushButton_new_search_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            self.enable_button_search(0)
            conn = Connection()
            sito_set = conn.sito_set()
            sito_set_str = sito_set['sito_set']
            if self.BROWSE_STATUS != "f":
                if bool(self.comboBox_sito.currentText()) and self.comboBox_sito.currentText() == sito_set_str:
                    self.BROWSE_STATUS = "f"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.empty_fields_nosite()
                    self.set_rec_counter('', '')
                    self.label_sort.setText(self.SORTED_ITEMS["n"])
                    self.setComboBoxEnable(["self.comboBox_sito"], "False")
                else:
                    self.BROWSE_STATUS = "f"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.empty_fields()
                    self.set_rec_counter('', '')
                    self.label_sort.setText(self.SORTED_ITEMS["n"])
                    self.setComboBoxEnable(["self.comboBox_sito"], "True")
                    self.charge_list()

    def on_pushButton_search_go_pressed(self):
        if self.BROWSE_STATUS != "f":
            if self.L == 'it':
                QMessageBox.warning(self, "ATTENZIONE", "Per eseguire una nuova ricerca clicca sul pulsante 'new search'", QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.warning(self, "WARNING", "To perform a new search click on the 'new search' button", QMessageBox.StandardButton.Ok)
        else:
            if self.lineEdit_anno.text() != "":
                anno = "'" + str(self.lineEdit_anno.text()) + "'"
            else:
                anno = ""

            search_dict = {
                'sito': "'" + str(self.comboBox_sito.currentText()) + "'",
                'anno': anno,
                'categoria': "'" + str(self.comboBox_categoria.currentText()) + "'",
                'descrizione': str(self.textEdit_descrizione.toPlainText()),
                'fornitore': "'" + str(self.lineEdit_fornitore.text()) + "'",
                'numero_fattura': "'" + str(self.lineEdit_numero_fattura.text()) + "'",
                'note': str(self.textEdit_note.toPlainText()),
            }
            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)
            if not bool(search_dict):
                if self.L == 'it':
                    QMessageBox.warning(self, "ATTENZIONE", "Non è stata impostata nessuna ricerca!!!", QMessageBox.StandardButton.Ok)
                else:
                    QMessageBox.warning(self, "WARNING", "No search has been set!!!", QMessageBox.StandardButton.Ok)
            else:
                res = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
                if not bool(res):
                    if self.L == 'it':
                        QMessageBox.warning(self, "ATTENZIONE", "Non e' stato trovato alcun record!", QMessageBox.StandardButton.Ok)
                    else:
                        QMessageBox.warning(self, "Warning", "The record has not been found", QMessageBox.StandardButton.Ok)
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
                    self.setComboBoxEnable(["self.comboBox_sito"], "False")
                    if self.REC_TOT == 1:
                        strings = ("Found", self.REC_TOT, "record")
                    else:
                        strings = ("Found", self.REC_TOT, "records")
                    QMessageBox.warning(self, "Message", "%s %d %s" % strings, QMessageBox.StandardButton.Ok)
        self.enable_button_search(1)

    def update_if(self, msg):
        rec_corr = self.REC_CORR
        if msg == QMessageBox.StandardButton.Ok:
            test = self.update_record()
            if test == 1:
                id_list = []
                for i in self.DATA_LIST:
                    id_list.append(getattr(i, self.ID_TABLE))
                self.DATA_LIST = []
                if self.SORT_STATUS == "n":
                    temp_data_list = self.DB_MANAGER.query_sort(id_list, [self.ID_TABLE], 'asc',
                                                                self.MAPPER_TABLE_CLASS, self.ID_TABLE)
                else:
                    temp_data_list = self.DB_MANAGER.query_sort(id_list, self.SORT_ITEMS_CONVERTED, self.SORT_MODE,
                                                                self.MAPPER_TABLE_CLASS, self.ID_TABLE)
                for i in temp_data_list:
                    self.DATA_LIST.append(i)
                self.BROWSE_STATUS = "b"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                return 1
            elif test == 0:
                return 0

    def charge_records(self):
        self.DATA_LIST = self.DB_MANAGER.query_ordered(self.MAPPER_TABLE_CLASS, self.ID_TABLE, 'asc')

    def setComboBoxEditable(self, f, n):
        for fn in f:
            widget_name = fn.replace('self.', '') if fn.startswith('self.') else fn
            widget = getattr(self, widget_name, None)
            if widget is not None:
                widget.setEditable(bool(n))

    def setComboBoxEnable(self, f, v):
        for fn in f:
            widget_name = fn.replace('self.', '') if fn.startswith('self.') else fn
            widget = getattr(self, widget_name, None)
            if widget is not None:
                widget.setEnabled(v == "True")

    def set_rec_counter(self, t, c):
        self.rec_tot = t
        self.rec_corr = c
        self.label_rec_tot.setText(str(self.rec_tot))
        self.label_rec_corrente.setText(str(self.rec_corr))

    def empty_fields_nosite(self):
        self.lineEdit_anno.clear()
        self.comboBox_categoria.setEditText("")
        self.textEdit_descrizione.clear()
        self.lineEdit_importo_previsto.clear()
        self.lineEdit_importo_effettivo.clear()
        self.lineEdit_data_registrazione.clear()
        self.lineEdit_data_spesa.clear()
        self.lineEdit_fornitore.clear()
        self.lineEdit_numero_fattura.clear()
        self.textEdit_note.clear()

    def empty_fields(self):
        self.comboBox_sito.setEditText("")
        self.lineEdit_anno.clear()
        self.comboBox_categoria.setEditText("")
        self.textEdit_descrizione.clear()
        self.lineEdit_importo_previsto.clear()
        self.lineEdit_importo_effettivo.clear()
        self.lineEdit_data_registrazione.clear()
        self.lineEdit_data_spesa.clear()
        self.lineEdit_fornitore.clear()
        self.lineEdit_numero_fattura.clear()
        self.textEdit_note.clear()

    def fill_fields(self, n=0):
        self.rec_num = n
        try:
            self.comboBox_sito.setEditText(str(self.DATA_LIST[self.rec_num].sito))

            if self.DATA_LIST[self.rec_num].anno is not None:
                self.lineEdit_anno.setText(str(self.DATA_LIST[self.rec_num].anno))
            else:
                self.lineEdit_anno.setText("")

            self.comboBox_categoria.setEditText(str(self.DATA_LIST[self.rec_num].categoria) if self.DATA_LIST[self.rec_num].categoria else "")
            self.textEdit_descrizione.setText(str(self.DATA_LIST[self.rec_num].descrizione) if self.DATA_LIST[self.rec_num].descrizione else "")

            if self.DATA_LIST[self.rec_num].importo_previsto is not None:
                self.lineEdit_importo_previsto.setText(str(self.DATA_LIST[self.rec_num].importo_previsto))
            else:
                self.lineEdit_importo_previsto.setText("")

            if self.DATA_LIST[self.rec_num].importo_effettivo is not None:
                self.lineEdit_importo_effettivo.setText(str(self.DATA_LIST[self.rec_num].importo_effettivo))
            else:
                self.lineEdit_importo_effettivo.setText("")

            self.lineEdit_data_registrazione.setText(str(self.DATA_LIST[self.rec_num].data_registrazione) if self.DATA_LIST[self.rec_num].data_registrazione else "")
            self.lineEdit_data_spesa.setText(str(self.DATA_LIST[self.rec_num].data_spesa) if self.DATA_LIST[self.rec_num].data_spesa else "")
            self.lineEdit_fornitore.setText(str(self.DATA_LIST[self.rec_num].fornitore) if self.DATA_LIST[self.rec_num].fornitore else "")
            self.lineEdit_numero_fattura.setText(str(self.DATA_LIST[self.rec_num].numero_fattura) if self.DATA_LIST[self.rec_num].numero_fattura else "")
            self.textEdit_note.setText(str(self.DATA_LIST[self.rec_num].note) if self.DATA_LIST[self.rec_num].note else "")
        except:
            pass

    def set_LIST_REC_TEMP(self):
        anno = str(self.lineEdit_anno.text()) if self.lineEdit_anno.text() else ''
        imp_prev = str(self.lineEdit_importo_previsto.text()) if self.lineEdit_importo_previsto.text() else ''
        imp_eff = str(self.lineEdit_importo_effettivo.text()) if self.lineEdit_importo_effettivo.text() else ''

        self.DATA_LIST_REC_TEMP = [
            str(self.comboBox_sito.currentText()),
            anno,
            str(self.comboBox_categoria.currentText()),
            str(self.textEdit_descrizione.toPlainText()),
            imp_prev,
            imp_eff,
            str(self.lineEdit_data_registrazione.text()),
            str(self.lineEdit_data_spesa.text()),
            str(self.lineEdit_fornitore.text()),
            str(self.lineEdit_numero_fattura.text()),
            str(self.textEdit_note.toPlainText())
        ]

    def set_LIST_REC_CORR(self):
        self.DATA_LIST_REC_CORR = []
        for i in self.TABLE_FIELDS:
            self.DATA_LIST_REC_CORR.append(str(getattr(self.DATA_LIST[self.REC_CORR], i)))

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
                                   [int(getattr(self.DATA_LIST[self.REC_CORR], self.ID_TABLE))],
                                   self.TABLE_FIELDS,
                                   self.rec_toupdate())
            return 1
        except Exception as e:
            save_file = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_Report_folder")
            file_ = os.path.join(save_file, 'error_encodig_data_recover.txt')
            with open(file_, "a") as fh:
                try:
                    raise ValueError(str(e))
                except ValueError as s:
                    print(s, file=fh)
            QMessageBox.warning(self, "Message",
                "Encoding problem: accents or characters not accepted by the database.",
                QMessageBox.StandardButton.Ok)
            return 0

    def rec_toupdate(self):
        rec_to_update = self.UTILITY.pos_none_in_list(self.DATA_LIST_REC_TEMP)
        return rec_to_update

    def datestrfdate(self):
        now = date.today()
        today = now.strftime("%d-%m-%Y")
        return today


## Class end

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = pyarchinit_Budget()
    ui.show()
    sys.exit(app.exec())
