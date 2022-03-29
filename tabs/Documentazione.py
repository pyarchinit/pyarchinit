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

import os
import sys
from builtins import range
from builtins import str
from qgis.PyQt.QtWidgets import QDialog, QMessageBox
from qgis.PyQt.uic import loadUiType
from qgis.core import QgsSettings
from ..modules.db.pyarchinit_conn_strings import Connection
from ..modules.db.pyarchinit_db_manager import Pyarchinit_db_management
from ..modules.db.pyarchinit_utility import Utility
from ..modules.gis.pyarchinit_pyqgis import Pyarchinit_pyqgis
from ..modules.utility.pyarchinit_error_check import Error_check
from ..modules.utility.pyarchinit_exp_Documentazionesheet_pdf import generate_documentazione_pdf
from ..gui.sortpanelmain import SortPanelMain
from ..tabs.Documentazione_preview import pyarchinit_doc_preview
from ..gui.pyarchinitConfigDialog import pyArchInitDialog_Config
MAIN_DIALOG_CLASS, _ = loadUiType(os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'Documentazione.ui'))


class pyarchinit_Documentazione(QDialog, MAIN_DIALOG_CLASS):
    L=QgsSettings().value("locale/userLocale")[0:2]
    if L=='it':
        MSG_BOX_TITLE = "PyArchInit - Documentazione"
    elif L=='en':
        MSG_BOX_TITLE = "PyArchInit - Documentation"
    elif L=='de':
        MSG_BOX_TITLE = "PyArchInit - Documentation"  
    DATA_LIST = []
    DATA_LIST_REC_CORR = []
    DATA_LIST_REC_TEMP = []
    REC_CORR = 0
    REC_TOT = 0
    SITO = pyArchInitDialog_Config
    if L=='it':
        STATUS_ITEMS = {"b": "Usa", "f": "Trova", "n": "Nuovo Record"}
    
    if L=='de':
        STATUS_ITEMS = {"b": "Aktuell ", "f": "Finden", "n": "Neuer Rekord"}
    
    else :
        STATUS_ITEMS = {"b": "Current", "f": "Find", "n": "New Record"}
    BROWSE_STATUS = "b"
    SORT_MODE = 'asc'
    if L=='it':
        SORTED_ITEMS = {"n": "Non ordinati", "o": "Ordinati"}
    if L=='de':
        SORTED_ITEMS = {"n": "Nicht sortiert", "o": "Sortiert"}
    else:
        SORTED_ITEMS = {"n": "Not sorted", "o": "Sorted"}
    SORT_STATUS = "n"
    UTILITY = Utility()
    DB_MANAGER = ""
    TABLE_NAME = 'documentazione_table'
    MAPPER_TABLE_CLASS = "DOCUMENTAZIONE"
    NOME_SCHEDA = "Scheda Documentazione"
    ID_TABLE = "id_documentazione"
    
    if L=='it':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Sito": "sito",
            "Nome documentazione": "nome_doc",
            "Data": "data",
            "Tipo documentazione": "tipo_documentazione",
            "Sorgente": "sorgente",
            "Scala": "scala",
            "Disegnatore": "disegnatore",
            "Note": "note",
        }

        SORT_ITEMS = [
            ID_TABLE,
            "Sito",
            "Nome documentazione",
            "Data",
            "Tipo documentazione",
            "Sorgente",
            "Scala",
            "Disegnatore",
            "Note",
        ]
    elif L=='de':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Ausgrabungsstätte": "sito",
            "Dokumentationsname": "nome_doc",
            "Datum": "data",
            "Dokumentationstyp": "tipo_documentazione",
            "Quelle": "sorgente",
            "Maßstab": "scala",
            "Zeichner": "disegnatore",
            "Notes": "note",
        }

        SORT_ITEMS = [
            ID_TABLE,
            "Ausgrabungsstätte",
            "Dokumentationsname",
            "Datum",
            "Dokumentationstyp",
            "Quelle",
            "Maßstab",
            "Zeichner",
            "Notes"
        ]
    else:
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Site": "sito",
            "Documentation name": "nome_doc",
            "Date": "data",
            "Documentation Type": "tipo_documentazione",
            "Source": "sorgente",
            "Scale": "scala",
            "Draftman": "disegnatore",
            "Note": "note"
        }

        SORT_ITEMS = [
            ID_TABLE,
            "Site",
            "Documentation name",
            "Date",
            "Documentation Type",
            "Source",
            "Scale",
            "Draftman",
            "Note"
        ]   
        
    TABLE_FIELDS = [
        "sito",
        "nome_doc",
        "data",
        "tipo_documentazione",
        "sorgente",
        "scala",
        "disegnatore",
        "note",
    ]

    LANG = {
        "IT": ['it_IT', 'IT', 'it', 'IT_IT'],
        "EN_US": ['en_US','EN_US','en','EN'],
        "DE": ['de_DE','de','DE', 'DE_DE'],
        #"FR": ['fr_FR','fr','FR', 'FR_FR'],
        #"ES": ['es_ES','es','ES', 'ES_ES'],
        #"PT": ['pt_PT','pt','PT', 'PT_PT'],
        #"SV": ['sv_SV','sv','SV', 'SV_SV'],
        #"RU": ['ru_RU','ru','RU', 'RU_RU'],
        #"RO": ['ro_RO','ro','RO', 'RO_RO'],
        #"AR": ['ar_AR','ar','AR', 'AR_AR'],
        #"PT_BR": ['pt_BR','PT_BR'],
        #"SL": ['sl_SL','sl','SL', 'SL_SL'],
    }

    HOME = os.environ['PYARCHINIT_HOME']

    REPORT_PATH = '{}{}{}'.format(HOME, os.sep, "pyarchinit_Report_folder")

    DB_SERVER = "not defined"  ####nuovo sistema sort

    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.pyQGIS = Pyarchinit_pyqgis(iface)
        self.setupUi(self)
        self.currentLayerId = None
        try:
            self.on_pushButton_connect_pressed()
        except Exception as e:
            QMessageBox.warning(self, "Connection System", str(e), QMessageBox.Ok)
        self.fill_fields()
        
        self.set_sito()
        self.msg_sito()
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
                if self.L=='it':
                    QMessageBox.warning(self,"BENVENUTO", "Benvenuto in pyArchInit " + self.NOME_SCHEDA + ". Il database e' vuoto. Premi 'Ok' e buon lavoro!",
                                        QMessageBox.Ok)
                
                elif self.L=='de':
                    
                    QMessageBox.warning(self,"WILLKOMMEN","WILLKOMMEN in pyArchInit" + "Documentationformular"+ ". Die Datenbank ist leer. Tippe 'Ok' und aufgehts!",
                                        QMessageBox.Ok) 
                else:
                    QMessageBox.warning(self,"WELCOME", "Welcome in pyArchInit" + "Documentation form" + ". The DB is empty. Push 'Ok' and Good Work!",
                                        QMessageBox.Ok)    
                self.charge_list()
                self.BROWSE_STATUS = 'x'
                self.on_pushButton_new_rec_pressed()
        except Exception as e:
            e = str(e)
            if e.find("no such table"):
            
                if self.L=='it':
                    msg = "La connessione e' fallita {}. " \
                          "E' NECESSARIO RIAVVIARE QGIS oppure rilevato bug! Segnalarlo allo sviluppatore".format(str(e))
                    self.iface.messageBar().pushMessage(self.tr(msg), Qgis.Warning, 0)
                
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

                ####################################

    def charge_list(self):

        # lista sito

        sito_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('site_table', 'sito', 'SITE'))

        try:
            sito_vl.remove('')
        except:
            pass
        self.comboBox_sito_doc.clear()
        sito_vl.sort()
        self.comboBox_sito_doc.addItems(sito_vl)
        
        
        
        
       
    
    ###################################


    def msg_sito(self):
        #self.model_a.database().close()
        conn = Connection()
        sito_set= conn.sito_set()
        sito_set_str = sito_set['sito_set']
        if bool(self.comboBox_sito_doc.currentText()) and self.comboBox_sito_doc.currentText()==sito_set_str:
            
            if self.L=='it':
                QMessageBox.information(self, "OK" ,"Sei connesso al sito: %s" % str(sito_set_str),QMessageBox.Ok) 
        
            elif self.L=='de':
                QMessageBox.information(self, "OK", "Sie sind mit der archäologischen Stätte verbunden: %s" % str(sito_set_str),QMessageBox.Ok) 
                
            else:
                QMessageBox.information(self, "OK", "You are connected to the site: %s" % str(sito_set_str),QMessageBox.Ok)     
        
        elif sito_set_str=='':    
            if self.L=='it':
                msg = QMessageBox.information(self, "Attenzione" ,"Non hai settato alcun sito. Vuoi settarne uno? click Ok altrimenti Annulla per  vedere tutti i record",QMessageBox.Ok | QMessageBox.Cancel) 
            elif self.L=='de':
                msg = QMessageBox.information(self, "Achtung", "Sie haben keine archäologischen Stätten eingerichtet. Klicken Sie auf OK oder Abbrechen, um alle Datensätze zu sehen",QMessageBox.Ok | QMessageBox.Cancel) 
            else:
                msg = QMessageBox.information(self, "Warning" , "You have not set up any archaeological site. Do you want to set one? click Ok otherwise Cancel to see all records",QMessageBox.Ok | QMessageBox.Cancel) 
            if msg == QMessageBox.Cancel:
                pass
            else: 
                dlg = pyArchInitDialog_Config(self)
                dlg.charge_list()
                dlg.exec_()
    def set_sito(self):
        #self.model_a.database().close()
        conn = Connection()
        sito_set= conn.sito_set()
        sito_set_str = sito_set['sito_set']
        try:
            if bool (sito_set_str):
                search_dict = {
                    'sito': "'" + str(sito_set_str) + "'"}  # 1 - Sito
                u = Utility()
                search_dict = u.remove_empty_items_fr_dict(search_dict)
                res = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
                self.DATA_LIST = []
                for i in res:
                    self.DATA_LIST.append(i)
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]  ####darivedere
                self.fill_fields()
                self.BROWSE_STATUS = "b"
                self.SORT_STATUS = "n"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                self.setComboBoxEnable(["self.comboBox_sito_doc"], "False")
            else:
                pass#
        except:
            if self.L=='it':
            
                QMessageBox.information(self, "Attenzione" ,"Non esiste questo sito: "'"'+ str(sito_set_str) +'"'" in questa scheda, Per favore distattiva la 'scelta sito' dalla scheda di configurazione plugin per vedere tutti i record oppure crea la scheda",QMessageBox.Ok) 
            elif self.L=='de':
            
                QMessageBox.information(self, "Warnung" , "Es gibt keine solche archäologische Stätte: "'""'+ str(sito_set_str) +'"'" in dieser Registerkarte, Bitte deaktivieren Sie die 'Site-Wahl' in der Plugin-Konfigurationsregisterkarte, um alle Datensätze zu sehen oder die Registerkarte zu erstellen",QMessageBox.Ok) 
            else:
            
                QMessageBox.information(self, "Warning" , "There is no such site: "'"'+ str(sito_set_str) +'"'" in this tab, Please disable the 'site choice' from the plugin configuration tab to see all records or create the tab",QMessageBox.Ok) 
    def generate_list_pdf(self):
        data_list = []
        for i in range(len(self.DATA_LIST)):

            sito = str(self.DATA_LIST[i].sito.replace('_',' '))
            tipo_doc = str(self.DATA_LIST[i].tipo_documentazione)
            nome_doc = str(self.DATA_LIST[i].nome_doc)
            note = str(self.DATA_LIST[i].note)

            res_us_doc = self.DB_MANAGER.select_us_doc_from_db_sql(sito, tipo_doc, nome_doc)

            res_usneg_doc = self.DB_MANAGER.select_usneg_doc_from_db_sql(sito, tipo_doc, nome_doc)

            elenco_us_doc = []
            elenco_usneg_doc = []

            if bool(res_us_doc):
                for sing_rec in res_us_doc:
                    tup_area_us = (str(sing_rec[1]), str(sing_rec[3]))
                    elenco_us_doc.append(tup_area_us)

            if bool(res_usneg_doc):
                for sing_rec in res_usneg_doc:
                    tup_area_usneg = (str(sing_rec[2]), str(sing_rec[3]))
                    elenco_usneg_doc.append(tup_area_usneg)

            elenco_us_pdf = elenco_us_doc + elenco_usneg_doc

            string_to_pdf = ""

            if bool(elenco_us_pdf):

                elenco_us_pdf.sort()

                area_corr = str(elenco_us_pdf[0][0])
                us_elenco = ""

                string_to_pdf = ""

                for rec_us in range(len(elenco_us_pdf)):
                    if area_corr == str(elenco_us_pdf[rec_us][0]):
                        us_elenco += str(elenco_us_pdf[rec_us][1]) + ", "
                    else:
                        if self.L=='it':
                            if string_to_pdf == "":
                                string_to_pdf = "Area " + area_corr + ": " + us_elenco[:-2]
                                area_corr = str(elenco_us_pdf[rec_us][0])
                                us_elenco = str(elenco_us_pdf[rec_us][1]) + ", "
                            else:
                                string_to_pdf += "<br/>Area " + area_corr + ": " + us_elenco[:-2]
                                area_corr = str(elenco_us_pdf[rec_us][0])
                                us_elenco = str(elenco_us_pdf[rec_us][1]) + ", "
                            
                        elif self.L=='de':
                            if string_to_pdf == "":
                                string_to_pdf = "Areal " + area_corr + ": " + us_elenco[:-2]
                                area_corr = str(elenco_us_pdf[rec_us][0])
                                us_elenco = str(elenco_us_pdf[rec_us][1]) + ", "
                            else:
                                string_to_pdf += "<br/>Areal " + area_corr + ": " + us_elenco[:-2]
                                area_corr = str(elenco_us_pdf[rec_us][0])
                                us_elenco = str(elenco_us_pdf[rec_us][1]) + ", "
                        else:
                            if string_to_pdf == "":
                                string_to_pdf = "Area " + area_corr + ": " + us_elenco[:-2]
                                area_corr = str(elenco_us_pdf[rec_us][0])
                                us_elenco = str(elenco_us_pdf[rec_us][1]) + ", "
                            else:
                                string_to_pdf += "<br/>Area " + area_corr + ": " + us_elenco[:-2]
                                area_corr = str(elenco_us_pdf[rec_us][0])
                                us_elenco = str(elenco_us_pdf[rec_us][1]) + ", "        
                if self.L=='it':                
                    string_to_pdf += "<br/>Area " + area_corr + ": " + us_elenco[:-2]
                elif self.L=='de':               
                    string_to_pdf += "<br/>Areal " + area_corr + ": " + us_elenco[:-2]
                else:               
                    string_to_pdf += "<br/>Area " + area_corr + ": " + us_elenco[:-2]   
            else:
                pass

            data_list.append([
                str(self.DATA_LIST[i].sito.replace('_',' ')),  # 1 - Sito
                str(self.DATA_LIST[i].nome_doc),  # 2 - Area
                str(self.DATA_LIST[i].data),  # 4 - definizione stratigrafica
                str(self.DATA_LIST[i].tipo_documentazione),  # 5 - definizione intepretata
                str(self.DATA_LIST[i].sorgente),  # 6 - descrizione
                str(self.DATA_LIST[i].scala),  # 7 - interpretazione
                str(self.DATA_LIST[i].disegnatore),  # 8 - periodo iniziale
                str(self.DATA_LIST[i].note),  # 9 - fase iniziale
                note])

        return data_list

    def on_pushButton_disegno_doc_pressed(self):
        sing_layer = [self.DATA_LIST[self.REC_CORR]]
        self.pyQGIS.charge_vector_layers_doc(sing_layer)

    def on_pushButton_exp_scheda_doc_pressed(self):
        if self.L=='it':
            single_Documentazione_pdf_sheet = generate_documentazione_pdf()
            data_list = self.generate_list_pdf()
            single_Documentazione_pdf_sheet.build_Documentazione_sheets(data_list)
        elif self.L=='de':
            single_Documentazione_pdf_sheet = generate_documentazione_pdf()
            data_list = self.generate_list_pdf()
            single_Documentazione_pdf_sheet.build_Documentazione_sheets_de(data_list)
        else:
            single_Documentazione_pdf_sheet = generate_documentazione_pdf()
            data_list = self.generate_list_pdf()
            single_Documentazione_pdf_sheet.build_Documentazione_sheets_en(data_list)   
            
    def on_pushButton_exp_elenco_doc_pressed(self):
        if self.L=='it':
            Documentazione_index_pdf = generate_documentazione_pdf()
            data_list = self.generate_list_pdf()
            Documentazione_index_pdf.build_index_Documentazione(data_list, data_list[0][0])
        elif self.L=='de':
            Documentazione_index_pdf = generate_documentazione_pdf()
            data_list = self.generate_list_pdf()
            Documentazione_index_pdf.build_index_Documentazione_de(data_list, data_list[0][0])
        else:
            Documentazione_index_pdf = generate_documentazione_pdf()
            data_list = self.generate_list_pdf()
            Documentazione_index_pdf.build_index_Documentazione_en(data_list, data_list[0][0])  
            
    def on_pushButtonPreview_pressed(self):

        docstr = (' \"%s\"=\'%s\' AND \"%s\"=\'%s\' AND \"%s\"=\'%s\' ') % ('sito',
                                                                            str(self.DATA_LIST[self.REC_CORR].sito),
                                                                            'nome_doc',
                                                                            str(self.DATA_LIST[self.REC_CORR].nome_doc),
                                                                            'tipo_doc',
                                                                            str(self.DATA_LIST[
                                                                                    self.REC_CORR].tipo_documentazione))

        QMessageBox.warning(self, "query", str(docstr), QMessageBox.Ok)

        dlg = pyarchinit_doc_preview(self, docstr)

        dlg.exec_()

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
        conn = Connection()
        
        sito_set= conn.sito_set()
        sito_set_str = sito_set['sito_set']
        if bool(self.DATA_LIST):
            if self.data_error_check() == 1:
                pass
            else:
                if self.BROWSE_STATUS == "b":
                    if bool(self.DATA_LIST):
                        if self.records_equal_check() == 1:
                            if self.L=='it':
                                self.update_if(QMessageBox.warning(self, 'Errore',
                                                                   "Il record e' stato modificato. Vuoi salvare le modifiche?",QMessageBox.Ok | QMessageBox.Cancel))
                            elif self.L=='de':
                                self.update_if(QMessageBox.warning(self, 'Error',
                                                                   "Der Record wurde geändert. Möchtest du die Änderungen speichern?",
                                                                   QMessageBox.Ok | QMessageBox.Cancel))
                                                                   
                            else:
                                self.update_if(QMessageBox.warning(self, 'Error',
                                                                   "The record has been changed. Do you want to save the changes?",
                                                                   QMessageBox.Ok | QMessageBox.Cancel))
                            # set the GUI for a new record
        if self.BROWSE_STATUS != "n":
            if bool(self.comboBox_sito_doc.currentText()) and self.comboBox_sito_doc.currentText()==sito_set_str:
                self.BROWSE_STATUS = "n"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.empty_fields_nosite()
                self.label_sort.setText(self.SORTED_ITEMS["n"])

                #self.setComboBoxEditable(["self.comboBox_sito_doc"], 1)
                self.setComboBoxEnable(["self.comboBox_sito_doc"], "False")
                self.setComboBoxEnable(["self.comboBox_tipo_doc"], "True")
                self.setComboBoxEnable(["self.lineEdit_nome_doc"], "True")

                self.set_rec_counter('', '')
            else:
                self.BROWSE_STATUS = "n"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.empty_fields()
                self.label_sort.setText(self.SORTED_ITEMS["n"])

                self.setComboBoxEditable(["self.comboBox_sito_doc"], 1)
                self.setComboBoxEnable(["self.comboBox_sito_doc"], "True")
                self.setComboBoxEnable(["self.comboBox_tipo_doc"], "True")
                self.setComboBoxEnable(["self.lineEdit_nome_doc"], "True")

                self.set_rec_counter('', '')
            
            self.enable_button(0)


            ###########################################

    def on_pushButton_save_pressed(self):
        # save record
        if self.BROWSE_STATUS == "b":
            if self.data_error_check() == 0:
                if self.records_equal_check() == 1:
                    if self.L=='it':
                        self.update_if(QMessageBox.warning(self, 'Errore',
                                                           "Il record e' stato modificato. Vuoi salvare le modifiche?",QMessageBox.Ok | QMessageBox.Cancel))
                    elif self.L=='de':
                        self.update_if(QMessageBox.warning(self, 'Error',
                                                           "Der Record wurde geändert. Möchtest du die Änderungen speichern?",
                                                           QMessageBox.Ok | QMessageBox.Cancel))
                                                    
                    else:
                        self.update_if(QMessageBox.warning(self, 'Error',
                                                           "The record has been changed. Do you want to save the changes?",
                                                           QMessageBox.Ok | QMessageBox.Cancel))
        else:
            if self.data_error_check() == 0:
                test_insert = self.insert_new_rec()
                if test_insert == 1:
                    self.empty_fields()
                    self.label_sort.setText(self.SORTED_ITEMS["n"])
                    self.charge_list()
                    self.set_sito()
                    self.charge_records()
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), len(self.DATA_LIST) - 1
                    self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)

                    ##################################################

                    self.setComboBoxEditable(["self.comboBox_sito_doc"], 1)
                    self.setComboBoxEnable(["self.comboBox_sito_doc"], "False")
                    self.setComboBoxEnable(["self.comboBox_tipo_doc"], "False")
                    self.setComboBoxEnable(["self.lineEdit_nome_doc"], "False")

                    self.fill_fields(self.REC_CORR)
                    self.enable_button(1)
                else:
                    pass

                    ##################################################

    def data_error_check(self):
        test = 0
        EC = Error_check()
        if self.L=='it':
            if EC.data_is_empty(str(self.comboBox_sito_doc.currentText())) == 0:
                QMessageBox.warning(self, "ATTENZIONE", "Campo Sito. \n Il campo non deve essere vuoto", QMessageBox.Ok)
                test = 1

            if EC.data_is_empty(str(self.comboBox_tipo_doc.currentText())) == 0:
                QMessageBox.warning(self, "ATTENZIONE", "Campo Tipo documentazione \n Il campo non deve essere vuoto",
                                    QMessageBox.Ok)
                test = 1

            if EC.data_is_empty(str(self.lineEdit_nome_doc.text())) == 0:
                QMessageBox.warning(self, "ATTENZIONE", "Campo Nome documentazione \n Il campo non deve essere vuoto",
                                    QMessageBox.Ok)
                test = 1
        elif self.L=='de':
            if EC.data_is_empty(str(self.comboBox_sito_doc.currentText())) == 0:
                QMessageBox.warning(self, "ACHTUNG", " Feld Ausgrabungstätte. \n Das Feld darf nicht leer sein", QMessageBox.Ok)
                test = 1

            if EC.data_is_empty(str(self.comboBox_tipo_doc.currentText())) == 0:
                QMessageBox.warning(self, "ACHTUNG", " Feld Documentation \n Das Feld darf nicht leer sein", QMessageBox.Ok)
                test = 1

            if EC.data_is_empty(str(self.lineEdit_nome_doc.text())) == 0:
                QMessageBox.warning(self, "ACHTUNG", " Feld Ausgrabungstätte. \n Das Feld darf nicht leer sein", QMessageBox.Ok)
                test = 1
        else:
            if EC.data_is_empty(str(self.comboBox_sito_doc.currentText())) == 0:
                QMessageBox.warning(self,"WARNING", "Site Field. \n The field must not be empty", QMessageBox.Ok)
                test = 1

            if EC.data_is_empty(str(self.comboBox_tipo_doc.currentText())) == 0:
                QMessageBox.warning(self,"WARNING", "Documetation Field. \n The field must not be empty", QMessageBox.Ok)
                test = 1

            if EC.data_is_empty(str(self.lineEdit_nome_doc.text())) == 0:
                QMessageBox.warning(self,"WARNING", "Name Documentation Field. \n The field must not be empty", QMessageBox.Ok)
                test = 1        
        return test

    def insert_new_rec(self):
        try:

            data = self.DB_MANAGER.insert_values_documentazione(
                self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, self.ID_TABLE) + 1,
                str(self.comboBox_sito_doc.currentText()),  # 1 - Sito
                str(self.lineEdit_nome_doc.text()),  # 2 - Nome Documentazione
                str(self.lineEdit_data_doc.text()),  # 3 - Data
                str(self.comboBox_tipo_doc.currentText()),  # 4 - Tipo Documentazione
                str(self.comboBox_sorgente_doc.currentText()),  # 5 - Sorgente
                str(self.comboBox_scala_doc.currentText()),  # 6 - Scala
                str(self.lineEdit_disegnatore_doc.text()),  # 7 - Disegnatore
                str(self.textEdit_note_doc.toPlainText()))  # 8 - Note

            try:
                self.DB_MANAGER.insert_data_session(data)
                return 1
            except Exception as e:
                e_str = str(e)
                if e_str.__contains__("IntegrityError"):
                    
                    if self.L=='it':
                        msg = self.ID_TABLE + " gia' presente nel database"
                        QMessageBox.warning(self, "Error", "Error" + str(msg), QMessageBox.Ok)
                    elif self.L=='de':
                        msg = self.ID_TABLE + " bereits in der Datenbank"
                        QMessageBox.warning(self, "Error", "Error" + str(msg), QMessageBox.Ok)  
                    else:
                        msg = self.ID_TABLE + " exist in db"
                        QMessageBox.warning(self, "Error", "Error" + str(msg), QMessageBox.Ok)  
                else:
                    msg = e
                    QMessageBox.warning(self, "Error", "Error 1 \n" + str(msg), QMessageBox.Ok)
                return 0

        except Exception as e:
            QMessageBox.warning(self, "Error", "Error 2 \n" + str(e), QMessageBox.Ok)
            return 0

    def check_record_state(self):
        ec = self.data_error_check()
        if ec == 1:
            return 1  # ci sono errori di immissione
        elif self.records_equal_check() == 1 and ec == 0:
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
            # self.charge_records()
            return 0  # non ci sono errori di immissione

            # records surf functions

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
                QMessageBox.warning(self, "Error", str(e), QMessageBox.Ok)

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
                QMessageBox.warning(self, "Error", str(e), QMessageBox.Ok)

    def on_pushButton_prev_rec_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            self.REC_CORR = self.REC_CORR - 1
            if self.REC_CORR == -1:
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
                    QMessageBox.warning(self, "Error", str(e), QMessageBox.Ok)

    def on_pushButton_next_rec_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            self.REC_CORR = self.REC_CORR + 1
            if self.REC_CORR >= self.REC_TOT:
                self.REC_CORR = self.REC_CORR - 1
                if self.L=='it':
                    QMessageBox.warning(self, "Attenzione", "Sei all'ultimo record!", QMessageBox.Ok)
                elif self.L=='de':
                    QMessageBox.warning(self, "Achtung", "du befindest dich im letzten Datensatz!", QMessageBox.Ok)
                else:
                    QMessageBox.warning(self, "Error", "You are to the first record!", QMessageBox.Ok)  
            else:
                try:
                    self.empty_fields()
                    self.fill_fields(self.REC_CORR)
                    self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
                except Exception as e:
                    QMessageBox.warning(self, "Error", str(e), QMessageBox.Ok)

    def on_pushButton_delete_pressed(self):
        
        if self.L=='it':
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
                    self.set_sito()
        elif self.L=='de':
            msg = QMessageBox.warning(self, "Achtung!!!",
                                      "Willst du wirklich diesen Eintrag löschen? \n Der Vorgang ist unumkehrbar",
                                      QMessageBox.Ok | QMessageBox.Cancel)
            if msg == QMessageBox.Cancel:
                QMessageBox.warning(self, "Message!!!", "Aktion annulliert!")
            else:
                try:
                    id_to_delete = eval("self.DATA_LIST[self.REC_CORR]." + self.ID_TABLE)
                    self.DB_MANAGER.delete_one_record(self.TABLE_NAME, self.ID_TABLE, id_to_delete)
                    self.charge_records()  # charge records from DB
                    QMessageBox.warning(self, "Message!!!", "Record gelöscht!")
                except Exception as e:
                    QMessageBox.warning(self, "Messagge!!!", "Errortyp: " + str(e))
                if not bool(self.DATA_LIST):
                    QMessageBox.warning(self, "Achtung", "Die Datenbank ist leer!", QMessageBox.Ok)
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
                    self.set_sito()
        else:
            msg = QMessageBox.warning(self, "Warning!!!",
                                      "Do you really want to break the record? \n Action is irreversible.",
                                      QMessageBox.Ok | QMessageBox.Cancel)
            if msg == QMessageBox.Cancel:
                QMessageBox.warning(self, "Message!!!", "Action deleted!")
            else:
                try:
                    id_to_delete = eval("self.DATA_LIST[self.REC_CORR]." + self.ID_TABLE)
                    self.DB_MANAGER.delete_one_record(self.TABLE_NAME, self.ID_TABLE, id_to_delete)
                    self.charge_records()  # charge records from DB
                    QMessageBox.warning(self, "Message!!!", "Record deleted!")
                except Exception as e:
                    QMessageBox.warning(self, "Message!!!", "error type: " + str(e))
                if not bool(self.DATA_LIST):
                    QMessageBox.warning(self, "Warning", "the db is empty!", QMessageBox.Ok)
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
                    self.set_sito()
            
            
            self.SORT_STATUS = "n"
            self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])

    def on_pushButton_new_search_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            self.enable_button_search(0)

            conn = Connection()
        
            sito_set= conn.sito_set()
            sito_set_str = sito_set['sito_set']

            # set the GUI for a new search
            if self.BROWSE_STATUS != "f":
                if bool(self.comboBox_sito_doc.currentText()) and self.comboBox_sito_doc.currentText()==sito_set_str:
                    self.BROWSE_STATUS = "f"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.setComboBoxEnable(["self.comboBox_sito_doc"], "False")
                    self.setComboBoxEnable(["self.lineEdit_nome_doc"], "True")
                    self.setComboBoxEnable(["self.comboBox_tipo_doc"], "True")
                    self.setComboBoxEnable(["self.textEdit_note_doc"], "False")
                    #self.setComboBoxEditable(["self.comboBox_sito_doc"], 1)
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.set_rec_counter('', '')
                    self.label_sort.setText(self.SORTED_ITEMS["n"])
                    #self.charge_list()
                    self.empty_fields_nosite()
                else:
                    self.BROWSE_STATUS = "f"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.setComboBoxEnable(["self.comboBox_sito_doc"], "True")
                    self.setComboBoxEnable(["self.lineEdit_nome_doc"], "True")
                    self.setComboBoxEnable(["self.comboBox_tipo_doc"], "True")
                    self.setComboBoxEnable(["self.textEdit_note_doc"], "False")
                    self.setComboBoxEditable(["self.comboBox_sito_doc"], 1)
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.set_rec_counter('', '')
                    self.label_sort.setText(self.SORTED_ITEMS["n"])
                    self.charge_list()
                    self.empty_fields()
                ################################################

    def on_pushButton_search_go_pressed(self):
        if self.BROWSE_STATUS != "f":
            if self.L=='it':
                QMessageBox.warning(self, "ATTENZIONE", "Per eseguire una nuova ricerca clicca sul pulsante 'new search' ",
                                    QMessageBox.Ok)
            elif self.L=='de':
                QMessageBox.warning(self, "ACHTUNG", "Um eine neue Abfrage zu starten drücke  'new search' ",
                                    QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "WARNING", "To perform a new search click on the 'new search' button ",
                                    QMessageBox.Ok)  
        else:
            search_dict = {
                self.TABLE_FIELDS[0]: "'" + str(self.comboBox_sito_doc.currentText()) + "'",  # 1 - Sito
                self.TABLE_FIELDS[1]: "'" + str(self.lineEdit_nome_doc.text()) + "'",  # 2 - Nome Documentazione
                self.TABLE_FIELDS[2]: "'" + str(self.lineEdit_data_doc.text()) + "'",  # 3 - Data
                self.TABLE_FIELDS[3]: "'" + str(self.comboBox_tipo_doc.currentText()) + "'",  # 4 - Tipo Documentazione
                self.TABLE_FIELDS[4]: "'" + str(self.comboBox_sorgente_doc.currentText()) + "'",  # 5 - Sorgente
                self.TABLE_FIELDS[5]: "'" + str(self.comboBox_scala_doc.currentText()) + "'",  # 6 - Scala
                self.TABLE_FIELDS[6]: "'" + str(self.lineEdit_disegnatore_doc.text()) + "'"  # 7 - Disegnatore
            }

            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)

            if not bool(search_dict):
                if self.L=='it':
                    QMessageBox.warning(self, "ATTENZIONE", "Non è stata impostata nessuna ricerca!!!", QMessageBox.Ok)
                elif self.L=='de':
                    QMessageBox.warning(self, "ACHTUNG", "Keine Abfrage definiert!!!", QMessageBox.Ok)
                else:
                    QMessageBox.warning(self, " WARNING", "No search has been set!!!", QMessageBox.Ok)      
            else:
                res = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
                if not bool(res):
                    if self.L=='it':
                        QMessageBox.warning(self, "ATTENZIONE", "Non è stato trovato nessun record!", QMessageBox.Ok)
                    elif self.L=='de':
                        QMessageBox.warning(self, "ACHTUNG", "Keinen Record gefunden!", QMessageBox.Ok)
                    else:
                        QMessageBox.warning(self, "WARNING," "No record found!", QMessageBox.Ok)

                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]

                    self.fill_fields(self.REC_CORR)
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])

                    self.setComboBoxEnable(["self.comboBox_sito_doc"], "False")
                    self.setComboBoxEnable(["self.lineEdit_nome_doc"], "False")
                    self.setComboBoxEnable(["self.comboBox_tipo_doc"], "False")
                    self.setComboBoxEnable(["self.textEdit_note_doc"], "True")
                    self.setComboBoxEditable(["self.comboBox_sito_doc"], 1)

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

                    if self.L=='it':
                        if self.REC_TOT == 1:
                            strings = ("E' stato trovato", self.REC_TOT, "record")
                        else:
                            strings = ("Sono stati trovati", self.REC_TOT, "records")
                    elif self.L=='de':
                        if self.REC_TOT == 1:
                            strings = ("Es wurde gefunden", self.REC_TOT, "record")
                        else:
                            strings = ("Sie wurden gefunden", self.REC_TOT, "records")
                    else:
                        if self.REC_TOT == 1:
                            strings = ("It has been found", self.REC_TOT, "record")
                        else:
                            strings = ("They have been found", self.REC_TOT, "records")

                    self.setComboBoxEnable(["self.comboBox_sito_doc"], "False")
                    self.setComboBoxEnable(["self.lineEdit_nome_doc"], "False")
                    self.setComboBoxEnable(["self.comboBox_tipo_doc"], "False")
                    self.setComboBoxEnable(["self.textEdit_note_doc"], "True")
                    self.setComboBoxEditable(["self.comboBox_sito_doc"], 1)

                    QMessageBox.warning(self, "Message", "%s %d %s" % strings, QMessageBox.Ok)

        self.enable_button_search(1)

    def on_pushButton_test_pressed(self):
        pass

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

    def empty_fields_nosite(self):
        
        self.lineEdit_nome_doc.clear()  # 2 - Nome Dcumentazione
        self.lineEdit_data_doc.clear()  # 3 - Data
        self.comboBox_tipo_doc.setEditText("")  # 4 - Tipo Documentazione
        self.comboBox_sorgente_doc.setEditText("")  # 5 - Sorgente
        self.comboBox_scala_doc.setEditText("")  # 6 - Scala
        self.lineEdit_disegnatore_doc.clear()  # 7 - Dsegnatore
        self.textEdit_note_doc.clear()  # 8 - Note
    def empty_fields(self):
        self.comboBox_sito_doc.setEditText("")  # 1 - Sito
        self.lineEdit_nome_doc.clear()  # 2 - Nome Dcumentazione
        self.lineEdit_data_doc.clear()  # 3 - Data
        self.comboBox_tipo_doc.setEditText("")  # 4 - Tipo Documentazione
        self.comboBox_sorgente_doc.setEditText("")  # 5 - Sorgente
        self.comboBox_scala_doc.setEditText("")  # 6 - Scala
        self.lineEdit_disegnatore_doc.clear()  # 7 - Dsegnatore
        self.textEdit_note_doc.clear()  # 8 - Note

    def fill_fields(self, n=0):
        self.rec_num = n
        try:
            str(self.comboBox_sito_doc.setEditText(self.DATA_LIST[self.rec_num].sito))  # 1 - Sito
            str(self.lineEdit_nome_doc.setText(self.DATA_LIST[self.rec_num].nome_doc))  # 2 - Nome Dcumentazione
            str(self.lineEdit_data_doc.setText(self.DATA_LIST[self.rec_num].data))  # 3 - Data
            str(self.comboBox_tipo_doc.setEditText(
                self.DATA_LIST[self.rec_num].tipo_documentazione))  # 4 - Tipo Documentazione
            str(self.comboBox_sorgente_doc.setEditText(self.DATA_LIST[self.rec_num].sorgente))  # 5 - Sorgente
            str(self.comboBox_scala_doc.setEditText(self.DATA_LIST[self.rec_num].scala))  # 6 - Scala
            str(self.lineEdit_disegnatore_doc.setText(self.DATA_LIST[self.rec_num].disegnatore))  # 7 - Dsegnatore
            str(self.textEdit_note_doc.setText(self.DATA_LIST[self.rec_num].note))  # 8 - Note
        except :#Exception as e:
            pass#QMessageBox.warning(self, "Errore fill", str(e), QMessageBox.Ok)
    def set_rec_counter(self, t, c):
        self.rec_tot = t
        self.rec_corr = c
        self.label_rec_tot.setText(str(self.rec_tot))
        self.label_rec_corrente.setText(str(self.rec_corr))

    def set_LIST_REC_TEMP(self):

        # data
        self.DATA_LIST_REC_TEMP = [
            str(self.comboBox_sito_doc.currentText()),  # 1 - Sito
            str(self.lineEdit_nome_doc.text()),  # 2 - Nome Documentazione
            str(self.lineEdit_data_doc.text()),  # 3 - Data
            str(self.comboBox_tipo_doc.currentText()),  # 4 - Tipo Documentazione
            str(self.comboBox_sorgente_doc.currentText()),  # 5 - Sorgente
            str(self.comboBox_scala_doc.currentText()),  # 6 - Scala
            str(self.lineEdit_disegnatore_doc.text()),  # 7 - Disegnatore
            str(self.textEdit_note_doc.toPlainText())  # 8 - Note
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
        try:
            self.DB_MANAGER.update(self.MAPPER_TABLE_CLASS,
                                   self.ID_TABLE,
                                   [eval("int(self.DATA_LIST[self.REC_CORR]." + self.ID_TABLE + ")")],
                                   self.TABLE_FIELDS,
                                   self.rec_toupdate())
            return 1
        except Exception as e:
            str(e)
            save_file='{}{}{}'.format(self.HOME, os.sep,"pyarchinit_Report_folder") 
            file_=os.path.join(save_file,'error_encodig_data_recover.txt')
            with open(file_, "a") as fh:
                try:
                    raise ValueError(str(e))
                except ValueError as s:
                    print(s, file=fh)
            if self.L=='it':
                QMessageBox.warning(self, "Messaggio",
                                    "Problema di encoding: sono stati inseriti accenti o caratteri non accettati dal database. Verrà fatta una copia dell'errore con i dati che puoi recuperare nella cartella pyarchinit_Report _Folder", QMessageBox.Ok)
            
            
            elif self.L=='de':
                QMessageBox.warning(self, "Message",
                                    "Encoding problem: accents or characters not accepted by the database were entered. A copy of the error will be made with the data you can retrieve in the pyarchinit_Report _Folder", QMessageBox.Ok) 
            else:
                QMessageBox.warning(self, "Message",
                                    "Kodierungsproblem: Es wurden Akzente oder Zeichen eingegeben, die von der Datenbank nicht akzeptiert werden. Es wird eine Kopie des Fehlers mit den Daten erstellt, die Sie im pyarchinit_Report _Ordner abrufen können", QMessageBox.Ok)
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
