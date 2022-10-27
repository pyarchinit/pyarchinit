
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
from datetime import date
import platform
from pdf2docx import parse
import sys
from builtins import range
from builtins import str
from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtWidgets import QDialog, QMessageBox,QTableWidgetItem
from qgis.PyQt.uic import loadUiType
from qgis.core import QgsSettings

from ..modules.db.pyarchinit_conn_strings import Connection
from ..modules.db.pyarchinit_db_manager import Pyarchinit_db_management
from ..modules.db.pyarchinit_utility import Utility
from ..modules.gis.pyarchinit_pyqgis import Pyarchinit_pyqgis
from ..modules.utility.delegateComboBox import ComboBoxDelegate
from ..modules.utility.pyarchinit_error_check import Error_check
from ..modules.utility.pyarchinit_exp_Strutturasheet_pdf import generate_struttura_pdf
from ..gui.sortpanelmain import SortPanelMain
from ..gui.pyarchinitConfigDialog import pyArchInitDialog_Config
MAIN_DIALOG_CLASS, _ = loadUiType(os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'Struttura.ui'))


class pyarchinit_Struttura(QDialog, MAIN_DIALOG_CLASS):
    L=QgsSettings().value("locale/userLocale")[0:2]
    if L=='it':
        MSG_BOX_TITLE = "PyArchInit - Scheda Struttura"
    elif L=='en':
        MSG_BOX_TITLE = "PyArchInit - Structure form"
    elif L=='de':
        MSG_BOX_TITLE = "PyArchInit - Struktur formular"
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
    TABLE_NAME = 'struttura_table'
    MAPPER_TABLE_CLASS = 'STRUTTURA'
    NOME_SCHEDA = "Scheda Struttura"
    ID_TABLE = "id_struttura"
    if L=='it':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Sito": "sito",
            "Sigla struttura": "sigla_struttura",
            "Numero struttura": "numero_struttura",
            "Categoria struttura": "categoria_struttura",
            "Tipologia struttura": "tipologia_struttura",
            "Definizione struttura": "definizione_struttura",
            "Descrizione": "descrizione",
            "Interpretazione": "interpretazione",
            "Periodo iniziale": "periodo_iniziale",
            "Fase iniziale": "fase_iniziale",
            "Periodo finale": "periodo_finale",
            "Fase_finale": "fase_finale",
            "Datazione estesa": "datazione_estesa"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Sito",
            "Sigla struttura",
            "Numero struttura",
            "Categoria struttura",
            "Tipologia struttura",
            "Definizione struttura",
            "Descrizione",
            "Interpretazione",
            "Periodo iniziale",
            "Fase iniziale",
            "Periodo finale",
            "Fase_finale",
            "Datazione estesa"
        ]
    elif L=='de':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Ausgrabungsstätte": "sito",
            "Strukturcode": "sigla_struttura",
            "Nr. Struktur": "numero_struttura",
            "Kategorie Struktur": "categoria_struttura",
            "Typologie Struktur": "tipologia_struttura",
            "Definition": "definizione_struttura",
            "Beschreibung": "descrizione",
            "Deutung": "interpretazione",
            "Anfangszeitraum": "periodo_iniziale",
            "Anfangsphase": "fase_iniziale",
            "Letzte zeitraum": "periodo_finale",
            "Letzte phase": "fase_finale",
            "Erweiterte Datierung": "datazione_estesa"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Ausgrabungsstätte",
            "Strukturcode",
            "Nr. Struktur",
            "Kategorie Struktur",
            "Typologie Struktur",
            "Definition",
            "Beschreibung",
            "Deutung",
            "Anfangszeitraum",
            "Anfangsphase",
            "Letzte zeitraum",
            "Letzte phase",
            "Erweiterte Datierung"
        ]
    else:
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Site": "sito",
            "Structure code": "sigla_struttura",
            "Structure number": "numero_struttura",
            "Structure categories": "categoria_struttura",
            "Structure typology": "tipologia_struttura",
            "Definition": "definizione_struttura",
            "Description": "descrizione",
            "Interpretation": "interpretazione",
            "Starting period": "periodo_iniziale",
            "Starting phase": "fase_iniziale",
            "Final period": "periodo_finale",
            "Final phase": "fase_finale",
            "Letteral datetion": "datazione_estesa"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Site",
            "Structure code",
            "Structure number",
            "Structure categories",
            "Structure typology",
            "Definition",
            "Description",
            "Interpretation",
            "Starting period",
            "Starting phase",
            "Final period",
            "Final phase",
            "Letteral datetion"]
    TABLE_FIELDS = [
        "sito",
        "sigla_struttura",
        "numero_struttura",
        "categoria_struttura",
        "tipologia_struttura",
        "definizione_struttura",
        "descrizione",
        "interpretazione",
        "periodo_iniziale",
        "fase_iniziale",
        "periodo_finale",
        "fase_finale",
        "datazione_estesa",
        "materiali_impiegati",
        "elementi_strutturali",
        "rapporti_struttura",
        "misure_struttura"
    ]

    LANG = {
       "IT": ['it_IT', 'IT', 'it', 'IT_IT'],
        "EN_US": ['en_US','EN_US'],
        "DE": ['de_DE','de','DE', 'DE_DE'],
        "FR": ['fr_FR','fr','FR', 'FR_FR'],
        "ES": ['es_ES','es','ES', 'ES_ES'],
        "PT": ['pt_PT','pt','PT', 'PT_PT'],
        "SV": ['sv_SV','sv','SV', 'SV_SV'],
        "RU": ['ru_RU','ru','RU', 'RU_RU'],
        "RO": ['ro_RO','ro','RO', 'RO_RO'],
        "AR": ['ar_AR','ar','AR', 'AR_AR'],
        "PT_BR": ['pt_BR','PT_BR'],
        "SL": ['sl_SL','sl','SL', 'SL_SL'],
    }

    DB_SERVER = "not defined"  ####nuovo sistema sort
    HOME = os.environ['PYARCHINIT_HOME']


    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.pyQGIS = Pyarchinit_pyqgis(iface)
        self.setupUi(self)
        self.currentLayerId = None
        self.mDockWidget_export.setHidden(True)
        self.mDockWidget_3.setHidden(True)
        
        try:
            self.on_pushButton_connect_pressed()
        except Exception as e:
            QMessageBox.warning(self, "Connection system", str(e), QMessageBox.Ok)

            # SIGNALS & SLOTS Functions
        self.comboBox_sigla_struttura.editTextChanged.connect(self.add_value_to_categoria)
        if len(self.DATA_LIST)==0:
            self.comboBox_sito.setCurrentIndex(0)
        else:
            self.comboBox_sito.setCurrentIndex(1)

        self.comboBox_sito.currentIndexChanged.connect(self.charge_periodo_iniz_list)
        self.comboBox_sito.currentIndexChanged.connect(self.charge_periodo_fin_list)
        self.comboBox_per_iniz.currentIndexChanged.connect(self.charge_fase_iniz_list)
        self.comboBox_per_fin.currentIndexChanged.connect(self.charge_fase_fin_list)
        self.comboBox_per_iniz.currentIndexChanged.connect(self.charge_datazione_list)
        self.comboBox_fas_iniz.currentIndexChanged.connect(self.charge_datazione_list)
        self.toolButton_pdfpath.clicked.connect(self.setPathpdf)
        self.pbnOpenpdfDirectory.clicked.connect(self.openpdfDir)
        sito = self.comboBox_sito.currentText()
        self.comboBox_sito.setEditText(sito)
        self.fill_fields()
        self.customize_GUI()
        self.set_sito()
        self.msg_sito()
    def on_pushButton_print_pressed(self):
        if self.L=='it':
            if self.checkBox_s_us.isChecked():
                Struttura_pdf_sheet = generate_struttura_pdf()  # deve essere importata la classe
                data_list = self.generate_list_pdf()  # deve essere aggiunta la funzione
                Struttura_pdf_sheet.build_Struttura_sheets(data_list)  # deve essere aggiunto il file per generare i pdf
                QMessageBox.warning(self, 'Ok',"Esportazione terminata Schede Struttura",QMessageBox.Ok)
            else:   
                pass
            if self.checkBox_e_us.isChecked() :
                Struttura_index_pdf = generate_struttura_pdf()
                data_list = self.generate_list_pdf()
            
                try:               
                    if bool(data_list):
                        Struttura_index_pdf.build_index_Struttura(data_list, data_list[0][0])
                        QMessageBox.warning(self, 'Ok',"Esportazione terminata Elenco Struttura",QMessageBox.Ok)
                    else:
                        QMessageBox.warning(self, 'ATTENZIONE',"L'elenco Struttura non può essere esportato devi riempire prima la scheda Struttura",QMessageBox.Ok)
                except Exception as e :
                    QMessageBox.warning(self, 'ATTENZIONE',str(e),QMessageBox.Ok)
            else:
                pass
            
        
        else:
            if self.checkBox_s_us.isChecked():
                Struttura_pdf_sheet = generate_struttura_pdf()  # deve essere importata la classe
                data_list = self.generate_list_pdf()  # deve essere aggiunta la funzione
                Struttura_pdf_sheet.build_Struttura_sheets(data_list)  # deve essere aggiunto il file per generare i pdf
                QMessageBox.warning(self, 'Ok',"Exportation Done",QMessageBox.Ok)
            else:   
                pass
            if self.checkBox_e_us.isChecked() :
                Struttura_index_pdf = generate_struttura_pdf()
                data_list = self.generate_list_pdf()
            
                try:               
                    if bool(data_list):
                        Struttura_index_pdf.build_index_Struttura(data_list, data_list[0][0])
                        QMessageBox.warning(self, 'Ok',"Exportation list done",QMessageBox.Ok)
                    else:
                        QMessageBox.warning(self, 'Warning',"The Structure list cannot be exported you have to fill in the Structure tabs before",QMessageBox.Ok)
                except Exception as e :
                    QMessageBox.warning(self, 'Warning',str(e),QMessageBox.Ok)
            else:
                pass
            # if self.checkBox_e_foto_t.isChecked():
                # US_index_pdf = generate_US_pdf()
                # data_list_foto = self.generate_list_foto()
                # try:
                        # if bool(data_list_foto):
                            # US_index_pdf.build_index_Foto(data_list_foto, data_list_foto[0][0])
                            # QMessageBox.warning(self, 'Ok',"Esportazione terminata Elenco Foto",QMessageBox.Ok)
                        # else:
                            # QMessageBox.warning(self, 'ATTENZIONE',"L'elenco foto non può essere esportato perchè non hai immagini taggate.",QMessageBox.Ok)
                # except Exception as e :
                    # QMessageBox.warning(self, 'ATTENZIONE',str(e),QMessageBox.Ok)
            # if self.checkBox_e_foto.isChecked():
                # US_index_pdf = generate_US_pdf()
                # data_list_foto = self.generate_list_foto()
                # try:
                        # if bool(data_list_foto):
                            # US_index_pdf.build_index_Foto_2(data_list_foto, data_list_foto[0][0])
                            # QMessageBox.warning(self, 'Ok',"Esportazione terminata Elenco Foto senza thumbanil",QMessageBox.Ok)
                        # else:
                            # QMessageBox.warning(self, 'ATTENZIONE',"L'elenco foto non può essere esportato perchè non hai immagini taggate.",QMessageBox.Ok)
                # except Exception as e :
                    # QMessageBox.warning(self, 'ATTENZIONE',str(e),QMessageBox.Ok)
        # elif self.L=='en':  
            # if self.checkBox_s_us.isChecked():
                # US_pdf_sheet = generate_US_pdf()
                # data_list = self.generate_list_pdf()
                # US_pdf_sheet.build_US_sheets_en(data_list)
                # QMessageBox.warning(self, 'Ok',"Export finished Forms",QMessageBox.Ok)
            # else:   
                # pass
            # if self.checkBox_e_us.isChecked() :
                # US_index_pdf = generate_US_pdf()
                # data_list = self.generate_list_pdf()
                # try:               
                    # if bool(data_list):
                        # US_index_pdf.build_index_US_en(data_list, data_list[0][0])
                        # QMessageBox.warning(self, 'Ok',"Export finished Grave List",QMessageBox.Ok)
                    # else:
                        # QMessageBox.warning(self, 'WARNING',"The Grave list cannot be exported you have to fill in the Grave tabs first",QMessageBox.Ok)
                # except Exception as e :
                    # QMessageBox.warning(self, 'WARNING',str(e),QMessageBox.Ok)
            # else:
                # pass
            # if self.checkBox_e_foto_t.isChecked():
                # US_index_pdf = generate_US_pdf()
                # data_list_foto = self.generate_list_foto()
                # try:
                        # if bool(data_list_foto):
                            # US_index_pdf.build_index_Foto_en(data_list_foto, data_list_foto[0][0])
                            # QMessageBox.warning(self, 'Ok',"Export finished Grave List",QMessageBox.Ok)
                        # else:
                            # QMessageBox.warning(self, 'WARNING', 'The photo list cannot be exported because you do not have tagged images.',QMessageBox.Ok)
                # except Exception as e :
                    # QMessageBox.warning(self, 'WARNING',str(e),QMessageBox.Ok)
            # if self.checkBox_e_foto.isChecked():
                # US_index_pdf = generate_US_pdf()
                # data_list_foto = self.generate_list_foto()
                # try:
                        # if bool(data_list_foto):
                            # US_index_pdf.build_index_Foto_2_en(data_list_foto, data_list_foto[0][0])
                            # QMessageBox.warning(self, 'Ok', "Export finished Photo List without thumbanil",QMessageBox.Ok)
                        # else:
                            # QMessageBox.warning(self, 'WARNING', "The photo list cannot be exported because you do not have tagged images.",QMessageBox.Ok)
                # except Exception as e :
                    # QMessageBox.warning(self, 'WARNING',str(e),QMessageBox.Ok)
        # elif self.L=='de':
            # if self.checkBox_s_us.isChecked():
                # US_pdf_sheet = generate_US_pdf()
                # data_list = self.generate_list_pdf()
                # US_pdf_sheet.build_US_sheets_de(data_list)
                # QMessageBox.warning(self, 'Ok',"Esportazione terminata Schede US",QMessageBox.Ok)
            # else:   
                # pass
            # if self.checkBox_e_us.isChecked() :
                # US_index_pdf = generate_US_pdf()
                # data_list = self.generate_list_pdf()
                # try:               
                    # if bool(data_list):
                        # US_index_pdf.build_index_US_de(data_list, data_list[0][0])
                        # QMessageBox.warning(self, "Okay", "Export beendet",QMessageBox.Ok)
                    # else:
                        # QMessageBox.warning(self, 'WARNUNG', 'Die Liste kann nicht exportiert werden, Sie müssen zuerst die Formulare ausfüllen',QMessageBox.Ok)
                # except Exception as e :
                    # QMessageBox.warning(self, 'WARNUNG',str(e),QMessageBox.Ok)
            # else:
                # pass
            # if self.checkBox_e_foto_t.isChecked():
                # US_index_pdf = generate_US_pdf()
                # data_list_foto = self.generate_list_foto()
                # try:
                        # if bool(data_list_foto):
                            # US_index_pdf.build_index_Foto_de(data_list_foto, data_list_foto[0][0])
                            # QMessageBox.warning(self, "Okay", "Fertige Fotoliste exportieren",QMessageBox.Ok)
                        # else:
                            # QMessageBox.warning(self, 'WARNUNG', 'Die Fotoliste kann nicht exportiert werden, da Sie keine markierten Bilder haben.',QMessageBox.Ok)
                # except Exception as e :
                    # QMessageBox.warning(self, 'WARNUNG',str(e),QMessageBox.Ok)
            # if self.checkBox_e_foto.isChecked():
                # US_index_pdf = generate_US_pdf()
                # data_list_foto = self.generate_list_foto()
                # try:
                        # if bool(data_list_foto):
                            # US_index_pdf.build_index_Foto_2_de(data_list_foto, data_list_foto[0][0])
                            # QMessageBox.warning(self, 'Ok', 'Fertige Fotoliste ohne Daumenballen exportieren',QMessageBox.Ok)
                        # else:
                            # QMessageBox.warning(self, 'WARNUNG', 'Die Fotoliste kann nicht exportiert werden, da Sie keine markierten Bilder haben.',QMessageBox.Ok)
                # except Exception as e :
                    # QMessageBox.warning(self, 'WARNUNG',str(e),QMessageBox.Ok)
    def on_pushButton_convert_pressed(self):
        # if not bool(self.setPathpdf()):    
            # QMessageBox.warning(self, "INFO", "devi scegliere un file pdf",
                                # QMessageBox.Ok)
        try:
            pdf_file = self.lineEdit_pdf_path.text()
            filename=pdf_file.split("/")[-1]
            docx_file = self.PDFFOLDER+'/'+filename+'.docx'
            # convert pdf to docx
            parse(pdf_file, docx_file, start=self.lineEdit_pag1.text(), end=self.lineEdit_pag2.text())
            QMessageBox.information(self, "INFO", "Conversion completed",
                                QMessageBox.Ok)
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e),
                                QMessageBox.Ok)
    
    def openpdfDir(self):
        HOME = os.environ['PYARCHINIT_HOME']
        path = '{}{}{}'.format(HOME, os.sep, "pyarchinit_PDF_folder")
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
    
    def on_pushButton_open_dir_pressed(self):
        HOME = os.environ['PYARCHINIT_HOME']
        path = '{}{}{}'.format(HOME, os.sep, "pyarchinit_PDF_folder")
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

    
    def setPathpdf(self):
        s = QgsSettings()
        dbpath = QFileDialog.getOpenFileName(
            self,
            "Set file name",
            self.PDFFOLDER,
            " PDF (*.pdf)"
        )[0]
        #filename=dbpath.split("/")[-1]
        if dbpath:
            self.lineEdit_pdf_path.setText(dbpath)
            s.setValue('',dbpath)
    
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
                self.BROWSE_STATUS = "b"
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
                    
                    QMessageBox.warning(self,"WILLKOMMEN","WILLKOMMEN in pyArchInit" + "Munsterformular"+ ". Die Datenbank ist leer. Tippe 'Ok' und aufgehts!",
                                        QMessageBox.Ok) 
                else:
                    QMessageBox.warning(self,"WELCOME", "Welcome in pyArchInit" + "Samples form" + ". The DB is empty. Push 'Ok' and Good Work!",
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

    def customize_GUI(self):

        l = QgsSettings().value("locale/userLocale", QVariant)
        lang = ""
        for key, values in self.LANG.items():
            if values.__contains__(l):
                lang = str(key)
        lang = "'" + lang + "'"

        self.tableWidget_rapporti.setColumnWidth(0, 220)
        self.tableWidget_rapporti.setColumnWidth(1, 220)
        self.tableWidget_rapporti.setColumnWidth(2, 150)
        self.tableWidget_rapporti.setColumnWidth(3, 100)

        self.tableWidget_materiali_impiegati.setColumnWidth(0, 200)

        self.tableWidget_elementi_strutturali.setColumnWidth(0, 150)
        self.tableWidget_elementi_strutturali.setColumnWidth(1, 100)

        self.tableWidget_misurazioni.setColumnWidth(0, 280)
        self.tableWidget_misurazioni.setColumnWidth(1, 200)
        self.tableWidget_misurazioni.setColumnWidth(2, 130)

        self.setComboBoxEditable(["self.comboBox_per_iniz"], 1)
        self.setComboBoxEditable(["self.comboBox_fas_iniz"], 1)
        self.setComboBoxEditable(["self.comboBox_per_fin"], 1)
        self.setComboBoxEditable(["self.comboBox_fas_fin"], 1)

        if self.L=='it':
            valuesRapporti = ["Si appoggia a", "Gli si appoggia", "Connesso con", "Si sovrappone a", "Gli si sovrappone",
                              "Ampliato da", "Amplia", "Uguale a",""]
            self.delegateRapporti = ComboBoxDelegate()
            self.delegateRapporti.def_values(valuesRapporti)
            self.delegateRapporti.def_editable('True')
            self.tableWidget_rapporti.setItemDelegateForColumn(0, self.delegateRapporti)
        elif self.L=='de':
            valuesRapporti = ["Stützt sich auf", "Wird gestüzt von", "Bindet an", "Überschneidungen sich auf", "Wird Überschneidungen von",
                              "Erweitert um", "Erweitert", "Entspricht", ""]
            self.delegateRapporti = ComboBoxDelegate()
            self.delegateRapporti.def_values(valuesRapporti)
            self.delegateRapporti.def_editable('True')
            self.tableWidget_rapporti.setItemDelegateForColumn(0, self.delegateRapporti)
            
        else:
            valuesRapporti = ["Abuts", "Supports", "Connected to", "Overlaps", "Overlaid by",
                              "Extend by", "Extend", "Same as", ""]
            self.delegateRapporti = ComboBoxDelegate()
            self.delegateRapporti.def_values(valuesRapporti)
            self.delegateRapporti.def_editable('True')
            self.tableWidget_rapporti.setItemDelegateForColumn(0, self.delegateRapporti)    
        # lista materiali

        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'struttura_table' + "'",
            'tipologia_sigla': "'" + '6.5' + "'"
        }

        materiali = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        valuesMateriali = []

        for i in range(len(materiali)):
            valuesMateriali.append(materiali[i].sigla_estesa)

        valuesMateriali.sort()

        #valuesMateriali = ["Terra", "Pietre", "Laterizio", "Ciottoli", "Calcare", "Calce", "Legno", "Concotto",
        #                   "Ghiaia", "Sabbia", "Malta", "Metallo", "Gesso"]
        self.delegateMateriali = ComboBoxDelegate()
        self.delegateMateriali.def_values(valuesMateriali)
        self.delegateMateriali.def_editable('False')
        self.tableWidget_materiali_impiegati.setItemDelegateForColumn(0, self.delegateMateriali)

        # lista elementi strutturali - tipologia elemento

        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'struttura_table' + "'",
            'tipologia_sigla': "'" + '6.6' + "'"
        }

        tipEl = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        valuesTipEl = []

        for i in range(len(tipEl)):
            valuesTipEl.append(tipEl[i].sigla_estesa)

        valuesTipEl.sort()

        # valuesMateriali = ["Terra", "Pietre", "Laterizio", "Ciottoli", "Calcare", "Calce", "Legno", "Concotto",
        #                   "Ghiaia", "Sabbia", "Malta", "Metallo", "Gesso"]
        self.delegateTipEl = ComboBoxDelegate()
        self.delegateTipEl.def_values(valuesTipEl)
        self.delegateTipEl.def_editable('False')
        self.tableWidget_elementi_strutturali.setItemDelegateForColumn(0, self.delegateTipEl)

        # lista misurazione - tipo misura

        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'struttura_table' + "'",
            'tipologia_sigla': "'" + '6.7' + "'"
        }

        elTipoMis = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        valuesTipoMis = []

        for i in range(len(elTipoMis)):
            valuesTipoMis.append(elTipoMis[i].sigla_estesa)

        valuesTipoMis.sort()

        self.delegateTipoMis = ComboBoxDelegate()
        self.delegateTipoMis.def_values(valuesTipoMis)
        self.delegateTipoMis.def_editable('False')
        self.tableWidget_misurazioni.setItemDelegateForColumn(0, self.delegateTipoMis)

        # lista misurazione - unita' di misura

        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'struttura_table' + "'",
            'tipologia_sigla': "'" + '6.8' + "'"
        }

        elUnitaMis = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        valuesUnitaMis = []

        for i in range(len(elUnitaMis)):
            valuesUnitaMis.append(elUnitaMis[i].sigla)

        valuesUnitaMis.sort()

        self.delegateUnitaMis = ComboBoxDelegate()
        self.delegateUnitaMis.def_values(valuesUnitaMis)
        self.delegateUnitaMis.def_editable('False')
        self.tableWidget_misurazioni.setItemDelegateForColumn(1, self.delegateUnitaMis)

        # lista rapporti struttura - sigla

        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'struttura_table' + "'",
            'tipologia_sigla': "'" + '6.1' + "'"
        }

        elSig = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        valuesSig = []

        for i in range(len(elSig)):
            valuesSig.append(elSig[i].sigla)

        valuesSig.sort()

        self.delegateSig = ComboBoxDelegate()
        self.delegateSig.def_values(valuesSig)
        self.delegateSig.def_editable('False')
        self.tableWidget_rapporti.setItemDelegateForColumn(2, self.delegateSig)

    def charge_list(self):

        #lista sito

        sito_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('site_table', 'sito', 'SITE'))

        try:
            sito_vl.remove('')
        except:
            pass
        self.comboBox_sito.clear()
        sito_vl.sort()
        self.comboBox_sito.addItems(sito_vl)

        #lista rapporti struttura - sito

        self.delegateSito = ComboBoxDelegate()
        self.delegateSito.def_values(sito_vl)
        self.delegateSito.def_editable('False')
        self.tableWidget_rapporti.setItemDelegateForColumn(1, self.delegateSito)

        #lista sigla struttura

        l = QgsSettings().value("locale/userLocale", QVariant)
        lang = ""
        for key, values in self.LANG.items():
            if values.__contains__(l):
                lang = str(key)
        lang = "'" + lang + "'"

        self.comboBox_sigla_struttura.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'struttura_table' + "'",
            'tipologia_sigla': "'" + '6.1' + "'"
        }

        sigla_struttura = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        sigla_struttura_vl = []

        for i in range(len(sigla_struttura)):
            sigla_struttura_vl.append(sigla_struttura[i].sigla)

        sigla_struttura_vl.sort()
        self.comboBox_sigla_struttura.addItems(sigla_struttura_vl)

        # lista categoria struttura

        self.comboBox_categoria_struttura.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'struttura_table' + "'",
            'tipologia_sigla': "'" + '6.2' + "'"
        }

        categoria_struttura = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        categoria_struttura_vl = []

        for i in range(len(categoria_struttura)):
            categoria_struttura_vl.append(categoria_struttura[i].sigla_estesa)

        categoria_struttura_vl.sort()
        self.comboBox_categoria_struttura.addItems(categoria_struttura_vl)

        # lista tipologia struttura

        self.comboBox_tipologia_struttura.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'struttura_table' + "'",
            'tipologia_sigla': "'" + '6.3' + "'"
        }

        tipologia_struttura = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        tipologia_struttura_vl = []

        for i in range(len(tipologia_struttura)):
            tipologia_struttura_vl.append(tipologia_struttura[i].sigla_estesa)

        tipologia_struttura_vl.sort()
        self.comboBox_tipologia_struttura.addItems(tipologia_struttura_vl)

        # lista definizione struttura

        self.comboBox_definizione_struttura.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'struttura_table' + "'",
            'tipologia_sigla': "'" + '6.4' + "'"
        }

        definizione_struttura = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        definizione_struttura_vl = []

        for i in range(len(definizione_struttura)):
            definizione_struttura_vl.append(definizione_struttura[i].sigla_estesa)

        definizione_struttura_vl.sort()
        self.comboBox_definizione_struttura.addItems(definizione_struttura_vl)

    def msg_sito(self):
        #self.model_a.database().close()
        conn = Connection()
        sito_set= conn.sito_set()
        sito_set_str = sito_set['sito_set']
        if bool(self.comboBox_sito.currentText()) and self.comboBox_sito.currentText()==sito_set_str:
            
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
                self.setComboBoxEnable(["self.comboBox_sito"], "False")
            else:
                pass#
        except:
            if self.L=='it':
            
                QMessageBox.information(self, "Attenzione" ,"Non esiste questo sito: "'"'+ str(sito_set_str) +'"'" in questa scheda, Per favore distattiva la 'scelta sito' dalla scheda di configurazione plugin per vedere tutti i record oppure crea la scheda",QMessageBox.Ok) 
            elif self.L=='de':
            
                QMessageBox.information(self, "Warnung" , "Es gibt keine solche archäologische Stätte: "'""'+ str(sito_set_str) +'"'" in dieser Registerkarte, Bitte deaktivieren Sie die 'Site-Wahl' in der Plugin-Konfigurationsregisterkarte, um alle Datensätze zu sehen oder die Registerkarte zu erstellen",QMessageBox.Ok) 
            else:
            
                QMessageBox.information(self, "Warning" , "There is no such site: "'"'+ str(sito_set_str) +'"'" in this tab, Please disable the 'site choice' from the plugin configuration tab to see all records or create the tab",QMessageBox.Ok)  
    def charge_periodo_iniz_list(self):
        sito = str(self.comboBox_sito.currentText())
        # sitob = sito.decode('utf-8')

        search_dict = {
            'sito': "'" + sito + "'"
        }

        periodo_vl = self.DB_MANAGER.query_bool(search_dict, 'PERIODIZZAZIONE')

        periodo_list = []

        for i in range(len(periodo_vl)):
            periodo_list.append(str(periodo_vl[i].periodo))
        try:
            periodo_vl.remove('')
        except:
            pass

        self.comboBox_per_iniz.clear()
        self.comboBox_per_iniz.addItems(self.UTILITY.remove_dup_from_list(periodo_list))

        if self.STATUS_ITEMS[self.BROWSE_STATUS] == "Trova" or "Find":
            self.comboBox_per_iniz.setEditText("")
        elif self.STATUS_ITEMS[self.BROWSE_STATUS] == "Usa" or "Current":
            if len(self.DATA_LIST) > 0:
                try:
                    self.comboBox_per_iniz.setEditText(self.DATA_LIST[self.rec_num].periodo_iniziale)
                except:
                    pass  # non vi sono periodi per questo scavo

    def charge_periodo_fin_list(self):
        search_dict = {
            'sito': "'" + str(self.comboBox_sito.currentText()) + "'"
        }

        periodo_vl = self.DB_MANAGER.query_bool(search_dict, 'PERIODIZZAZIONE')
        periodo_list = []

        for i in range(len(periodo_vl)):
            periodo_list.append(str(periodo_vl[i].periodo))
        try:
            periodo_vl.remove('')
        except:
            pass

        self.comboBox_per_fin.clear()
        self.comboBox_per_fin.addItems(self.UTILITY.remove_dup_from_list(periodo_list))

        if self.STATUS_ITEMS[self.BROWSE_STATUS] == "Trova" or "Find":
            self.comboBox_per_fin.setEditText("")
        elif self.STATUS_ITEMS[self.BROWSE_STATUS] == "Usa" or "Current":
            if len(self.DATA_LIST) > 0:
                try:
                    self.comboBox_per_fin.setEditText(self.DATA_LIST[self.rec_num].periodo_iniziale)
                except:
                    pass

    def charge_fase_iniz_list(self):
        try:
            search_dict = {
                'sito': "'" + str(self.comboBox_sito.currentText()) + "'",
                'periodo': "'" + str(self.comboBox_per_iniz.currentText()) + "'",
            }

            fase_list_vl = self.DB_MANAGER.query_bool(search_dict, 'PERIODIZZAZIONE')

            fase_list = []

            for i in range(len(fase_list_vl)):
                fase_list.append(str(fase_list_vl[i].fase))

            try:
                fase_list.remove('')
            except:
                pass

            self.comboBox_fas_iniz.clear()

            fase_list.sort()
            self.comboBox_fas_iniz.addItems(self.UTILITY.remove_dup_from_list(fase_list))

            if self.STATUS_ITEMS[self.BROWSE_STATUS] == "Trova" or "Find":
                self.comboBox_fas_iniz.setEditText("")
            else:
                self.comboBox_fas_iniz.setEditText(self.DATA_LIST[self.rec_num].fase_iniziale)
        except:
            pass


    def charge_fase_fin_list(self):
        try:
            search_dict = {
                'sito': "'" + str(self.comboBox_sito.currentText()) + "'",
                'periodo': "'" + str(self.comboBox_per_fin.currentText()) + "'",
            }

            fase_list_vl = self.DB_MANAGER.query_bool(search_dict, 'PERIODIZZAZIONE')

            fase_list = []

            for i in range(len(fase_list_vl)):
                fase_list.append(str(fase_list_vl[i].fase))

            try:
                fase_list.remove('')
            except:
                pass

            self.comboBox_fas_fin.clear()
            fase_list.sort()
            self.comboBox_fas_fin.addItems(self.UTILITY.remove_dup_from_list(fase_list))

            if self.STATUS_ITEMS[self.BROWSE_STATUS] == "Trova" or "Find":
                self.comboBox_fas_fin.setEditText("")
            else:
                self.comboBox_fas_fin.setEditText(self.DATA_LIST[self.rec_num].fase_finale)
        except:
            pass

            # buttons functions

    def charge_datazione_list(self):
        if self.comboBox_sito.editTextChanged: 
            try:
                search_dict = {
                    'sito': "'" + str(self.comboBox_sito.currentText()) + "'",
                    'periodo': "'" + str(self.comboBox_per_iniz.currentText()) + "'",
                    'fase': "'" + str(self.comboBox_fas_iniz.currentText()) + "'"
                }
                datazione_list_vl = self.DB_MANAGER.query_bool(search_dict, 'PERIODIZZAZIONE')
                datazione_list = []
                for i in range(len(datazione_list_vl)):
                    datazione_list.append(str(datazione_list_vl[i].datazione_estesa))
                try:
                    datazione_list.remove('')
                except:
                    pass
                self.comboBox_datazione_estesa.clear()
                datazione_list.sort()
                self.comboBox_datazione_estesa.addItems(self.UTILITY.remove_dup_from_list(datazione_list))
                if self.STATUS_ITEMS[self.BROWSE_STATUS] == "Trova" or "Find":
                    self.comboBox_datazione_estesa.setEditText("")
                else:
                    self.comboBox_datazione_estesa.setEditText(self.DATA_LIST[self.rec_num].datazione_estesa)
            except:
                pass
    
    def on_pushButton_sort_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            dlg = SortPanelMain(self)
            dlg.insertItems(self.SORT_ITEMS)
            dlg.exec_()

            items, order_type = dlg.ITEMS, dlg.TYPE_ORDER

            items_converted = []
            for i in items:
                items_converted.append(self.CONVERSION_DICT[i])

            self.SORT_MODE = order_type
            self.empty_fields()

            id_list = []
            for i in self.DATA_LIST:
                id_list.append(eval("i." + self.ID_TABLE))
            self.DATA_LIST = []

            temp_data_list = self.DB_MANAGER.query_sort(id_list, items_converted, order_type, self.MAPPER_TABLE_CLASS,
                                                        self.ID_TABLE)

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
            self.label_sort.setText(self.SORTED_ITEMS["o"])
            self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
            self.fill_fields()

    def add_value_to_categoria(self):
        if str(self.comboBox_sigla_struttura.currentText()) == '':
            self.setComboBoxEditable(["self.comboBox_sigla_struttura"], 1)

    def on_pushButton_new_rec_pressed(self):
        conn = Connection()
        
        sito_set= conn.sito_set()
        sito_set_str = sito_set['sito_set']
        
        if bool(self.DATA_LIST):
            if self.data_error_check() == 1:
                pass
            # else:
                # if self.BROWSE_STATUS == "b":
                    # if bool(self.DATA_LIST):
                        # if self.records_equal_check() == 1:
                            # if self.L=='it':
                                # self.update_if(QMessageBox.warning(self, 'Errore',
                                                                   # "Il record e' stato modificato. Vuoi salvare le modifiche?",QMessageBox.Ok | QMessageBox.Cancel))
                            # elif self.L=='de':
                                # self.update_if(QMessageBox.warning(self, 'Error',
                                                                   # "Der Record wurde geändert. Möchtest du die Änderungen speichern?",
                                                                   # QMessageBox.Ok | QMessageBox.Cancel))
                                                                   
                            # else:
                                # self.update_if(QMessageBox.warning(self, 'Error',
                                                                   # "The record has been changed. Do you want to save the changes?",
                                                                   # QMessageBox.Ok | QMessageBox.Cancel))
                            # set the GUI for a new record
        if self.BROWSE_STATUS != "n":
            if bool(self.comboBox_sito.currentText()) and self.comboBox_sito.currentText()==sito_set_str:
                self.BROWSE_STATUS = "n"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.empty_fields_nosite()
                self.label_sort.setText(self.SORTED_ITEMS["n"])
                self.SORT_STATUS = "n"
                #self.setComboBoxEditable(["self.comboBox_sito"], 1)
                self.setComboBoxEditable(["self.comboBox_sigla_struttura"], 0)
                self.setComboBoxEnable(["self.comboBox_sito"], False)
                self.setComboBoxEnable(["self.comboBox_sigla_struttura"], True)
                self.setComboBoxEnable(["self.numero_struttura"], True)

                self.set_rec_counter('', '')
            else:
                self.BROWSE_STATUS = "n"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
                self.empty_fields()
                self.label_sort.setText(self.SORTED_ITEMS["n"])

                self.setComboBoxEditable(["self.comboBox_sito"], 1)
                self.setComboBoxEditable(["self.comboBox_sigla_struttura"], 1)
                self.setComboBoxEnable(["self.comboBox_sito"], True)
                self.setComboBoxEnable(["self.comboBox_sigla_struttura"], True)
                self.setComboBoxEnable(["self.numero_struttura"], True)

                self.set_rec_counter('', '')
            self.enable_button(0)

    def on_pushButton_save_pressed(self):
        # save record
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
                    self.empty_fields()
                    self.SORT_STATUS = "n"
                    self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
                    self.enable_button(1)
                    self.fill_fields(self.REC_CORR)
                else:
                    if self.L=='it':
                        QMessageBox.warning(self, "ATTENZIONE", "Non è stata realizzata alcuna modifica.", QMessageBox.Ok)
                    elif self.L=='de':
                        QMessageBox.warning(self, "ACHTUNG", "Keine Änderung vorgenommen", QMessageBox.Ok)
                    else:
                        QMessageBox.warning(self, "Warning", "No changes have been made", QMessageBox.Ok)   
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

                    self.setComboBoxEditable(["self.comboBox_sito"], 1)
                    self.setComboBoxEditable(["self.comboBox_sigla_struttura"], 1)
                    self.setComboBoxEnable(["self.comboBox_sito"], "False")
                    self.setComboBoxEnable(["self.comboBox_sigla_struttura"], "False")
                    self.setComboBoxEnable(["self.numero_struttura"], "False")

                    self.fill_fields(self.REC_CORR)
                    self.enable_button(1)
            else:
                    if self.L=='it':
                        QMessageBox.warning(self, "ATTENZIONE", "Problema nell'inserimento dati", QMessageBox.Ok)
                    elif self.L=='de':
                        QMessageBox.warning(self, "ACHTUNG", "Problem der Dateneingabe", QMessageBox.Ok)
                    else:
                        QMessageBox.warning(self, "Warning", "Problem with data entry", QMessageBox.Ok)    

    def data_error_check(self):
        test = 0
        EC = Error_check()

        nr_struttura = self.numero_struttura.text()
        if self.L=='it':
            if EC.data_is_empty(str(self.comboBox_sito.currentText())) == 0:
                QMessageBox.warning(self, "ATTENZIONE", "Campo Sito \n Il campo non deve essere vuoto", QMessageBox.Ok)
                test = 1

            if EC.data_is_empty(str(self.comboBox_sigla_struttura.currentText())) == 0:
                QMessageBox.warning(self, "ATTENZIONE", "Campo Sigla Struttura \n Il campo non deve essere vuoto",
                                    QMessageBox.Ok)
                test = 1

            if EC.data_is_empty(str(self.numero_struttura.text())) == 0:
                QMessageBox.warning(self, "ATTENZIONE", "Campo Nr Struttura \n Il campo non deve essere vuoto",
                                    QMessageBox.Ok)
                test = 1

            if nr_struttura != "":
                if EC.data_is_int(nr_struttura) == 0:
                    QMessageBox.warning(self, "ATTENZIONE", "Campo Nr Struttura. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

        elif self.L=='de':
            if EC.data_is_empty(str(self.comboBox_sito.currentText())) == 0:
                QMessageBox.warning(self, "ACHTUNG", " Feld Ausgrabungstätte \n Das Feld darf nicht leer sein", QMessageBox.Ok)
                test = 1

            if EC.data_is_empty(str(self.comboBox_sigla_struttura.currentText())) == 0:
                QMessageBox.warning(self, "ACHTUNG", " Feld Strukturcode \n Das Feld darf nicht leer sein",QMessageBox.Ok)
                test = 1

            if EC.data_is_empty(str(self.numero_struttura.text())) == 0:
                QMessageBox.warning(self, "ACHTUNG", " Feld Strukturcode \n Das Feld darf nicht leer sein",QMessageBox.Ok)
                test = 1

            if nr_struttura != "":
                if EC.data_is_int(nr_struttura) == 0:
                    QMessageBox.warning(self,"ACHTUNG", " Feld Strukturcode \n Der Wert muss numerisch eingegeben werden", QMessageBox.Ok)
                    test = 1
        
        else:
            if EC.data_is_empty(str(self.comboBox_sito.currentText())) == 0:
                QMessageBox.warning(self, "WARNING", "Site Field \n The field must not be empty", QMessageBox.Ok)
                test = 1  

            if EC.data_is_empty(str(self.comboBox_sigla_struttura.currentText())) == 0:
                QMessageBox.warning(self, "WARNING", "Structure code Field \n The field must not be empty",QMessageBox.Ok)
                test = 1

            if EC.data_is_empty(str(self.numero_struttura.text())) == 0:
                QMessageBox.warning(self, "WARNING", "Structure Nr. Field \n The field must not be empty", QMessageBox.Ok)
                test = 1

            if nr_struttura != "":
                if EC.data_is_int(nr_struttura) == 0:
                    QMessageBox.warning(self, "WARNING", "Structure Nr. Field \n The value must be numerical",QMessageBox.Ok)
                    test = 1
        
        return test

    def insert_new_rec(self):

        # TableWidget
        ##Materiali_impiegati
        materiali_impiegati = self.table2dict("self.tableWidget_materiali_impiegati")
        ##Elementi_strutturali
        elementi_strutturali = self.table2dict("self.tableWidget_elementi_strutturali")
        ##Rapporti_struttura
        rapporti_struttura = self.table2dict("self.tableWidget_rapporti")
        ##Misurazioni
        misurazioni = self.table2dict("self.tableWidget_misurazioni")

        if self.comboBox_per_iniz.currentText() == "":
            per_iniz = None
        else:
            per_iniz = int(self.comboBox_per_iniz.currentText())

        if self.comboBox_fas_iniz.currentText() == "":
            fas_iniz = None
        else:
            fas_iniz = int(self.comboBox_fas_iniz.currentText())

        if self.comboBox_per_fin.currentText() == "":
            per_fin = None
        else:
            per_fin = int(self.comboBox_per_fin.currentText())

        if self.comboBox_fas_fin.currentText() == "":
            fas_fin = None
        else:
            fas_fin = int(self.comboBox_fas_fin.currentText())

        try:
            data = self.DB_MANAGER.insert_struttura_values(
                self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, self.ID_TABLE) + 1,  # 0
                str(self.comboBox_sito.currentText()),  # 1 - Sito
                str(self.comboBox_sigla_struttura.currentText()),  # 2 - sigla_struttura
                int(self.numero_struttura.text()),  # 3 - numero_struttura
                str(self.comboBox_categoria_struttura.currentText()),  # 4 - categoria_struttura
                str(self.comboBox_tipologia_struttura.currentText()),  # 5 - tipologia_struttura
                str(self.comboBox_definizione_struttura.currentText()),  # 6 - definizione_struttura
                str(self.textEdit_descrizione_struttura.toPlainText()),  # 7 - descrizione
                str(self.textEdit_interpretazione_struttura.toPlainText()),  # 8 - interpretazione
                per_iniz,  # 9 - periodo iniziale
                fas_iniz,  # 10 - fase iniziale
                per_fin,  # 11 - periodo finale iniziale
                fas_fin,  # 12 - fase finale
                str(self.comboBox_datazione_estesa.currentText()),  # 13 - datazione estesa
                str(materiali_impiegati),  # 14 - materiali impiegati
                str(elementi_strutturali),  # 15 - elementi_strutturali
                str(rapporti_struttura),  # 16 - rapporti struttura
                str(misurazioni))  # 17 - misurazioni

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
            if self.BROWSE_STATUS != "f":
                if bool(self.comboBox_sito.currentText()) and self.comboBox_sito.currentText()==sito_set_str:
                    self.BROWSE_STATUS = "f"
                    ###
                    #self.setComboBoxEditable(["self.comboBox_sito"], 1)
                    self.setComboBoxEditable(["self.comboBox_sigla_struttura"], 1)
                    self.setComboBoxEnable(["self.comboBox_sito"], False)
                    self.setComboBoxEnable(["self.comboBox_sigla_struttura"], True)
                    self.setComboBoxEnable(["self.numero_struttura"], True)

                    self.setComboBoxEnable(["self.textEdit_descrizione_struttura"], "False")
                    self.setComboBoxEnable(["self.textEdit_interpretazione_struttura"], "False")
                    self.setTableEnable(["self.tableWidget_materiali_impiegati", "self.tableWidget_elementi_strutturali",
                                         "self.tableWidget_rapporti",
                                         "self.tableWidget_misurazioni"], "False")

                    ###
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.set_rec_counter('', '')
                    self.label_sort.setText(self.SORTED_ITEMS["n"])
                    #self.charge_list()
                    self.empty_fields_nosite()
                else:
                    self.BROWSE_STATUS = "f"
                    ###
                    self.setComboBoxEditable(["self.comboBox_sito"], 0)
                    self.setComboBoxEditable(["self.comboBox_sigla_struttura"], 1)
                    self.setComboBoxEnable(["self.comboBox_sito"], True)
                    self.setComboBoxEnable(["self.comboBox_sigla_struttura"], True)
                    self.setComboBoxEnable(["self.numero_struttura"], True)

                    self.setComboBoxEnable(["self.textEdit_descrizione_struttura"], "False")
                    self.setComboBoxEnable(["self.textEdit_interpretazione_struttura"], "False")
                    self.setTableEnable(["self.tableWidget_materiali_impiegati", "self.tableWidget_elementi_strutturali",
                                         "self.tableWidget_rapporti",
                                         "self.tableWidget_misurazioni"], "False")

                    ###
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.set_rec_counter('', '')
                    self.label_sort.setText(self.SORTED_ITEMS["n"])
                    self.charge_list()
                    self.empty_fields()
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
            if self.numero_struttura.text() != "":
                numero_struttura = int(self.numero_struttura.text())
            else:
                numero_struttura = ""

            if self.comboBox_per_iniz.currentText() != "":
                periodo_iniziale = int(self.comboBox_per_iniz.currentText())
            else:
                periodo_iniziale = ""

            if self.comboBox_fas_iniz.currentText() != "":
                fase_iniziale = int(self.comboBox_fas_iniz.currentText())
            else:
                fase_iniziale = ""

            if self.comboBox_per_fin.currentText() != "":
                periodo_finale = int(self.comboBox_per_fin.currentText())
            else:
                periodo_finale = ""

            if self.comboBox_fas_fin.currentText() != "":
                fase_finale = int(self.comboBox_fas_fin.currentText())
            else:
                fase_finale = ""

            search_dict = {
                self.TABLE_FIELDS[0]: "'" + str(self.comboBox_sito.currentText()) + "'",  # 1 - Sito
                self.TABLE_FIELDS[1]: "'" + str(self.comboBox_sigla_struttura.currentText()) + "'",
                # 2 - Sigla struttura
                self.TABLE_FIELDS[2]: numero_struttura,  # 3 - numero struttura
                self.TABLE_FIELDS[3]: "'" + str(self.comboBox_categoria_struttura.currentText()) + "'",
                # 4 - categoria struttura
                self.TABLE_FIELDS[4]: "'" + str(self.comboBox_tipologia_struttura.currentText()) + "'",
                # 5 - tipologia struttura
                self.TABLE_FIELDS[5]: "'" + str(self.comboBox_definizione_struttura.currentText()) + "'",
                # 6 - definizione struttura
                # self.TABLE_FIELDS[6] : str(self.textEdit_descrizione_struttura.toPlainText()),                                #7 - descrizione struttura
                # self.TABLE_FIELDS[7] : str(self.textEdit_interpretazione_struttura.toPlainText()),                            #8 - intepretazione struttura
                self.TABLE_FIELDS[8]: periodo_iniziale,  # 9 - periodo iniziale
                self.TABLE_FIELDS[9]: fase_iniziale,  # 10 - fase iniziale
                self.TABLE_FIELDS[10]: periodo_finale,  # 11 - periodo finale
                self.TABLE_FIELDS[11]: fase_finale,  # 12 - fase finale
                self.TABLE_FIELDS[12]: "'" + str(self.comboBox_datazione_estesa.currentText()) + "'"  # 10 - datazione_estesa
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

                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])

                    self.setComboBoxEnable(["self.comboBox_sito"], "False")
                    self.setComboBoxEnable(["self.comboBox_sigla_struttura"], "False")
                    self.setComboBoxEnable(["self.numero_struttura"], "False")
                    self.setComboBoxEditable(["self.comboBox_sito"], 1)
                    self.setComboBoxEditable(["self.comboBox_sigla_struttura"], 1)

                    self.setComboBoxEnable(["self.textEdit_descrizione_struttura"], "True")
                    self.setComboBoxEnable(["self.textEdit_interpretazione_struttura"], "True")
                    self.setTableEnable(
                        ["self.tableWidget_materiali_impiegati", "self.tableWidget_elementi_strutturali",
                         "self.tableWidget_rapporti",
                         "self.tableWidget_misurazioni"], "True")

                    self.fill_fields(self.REC_CORR)
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
                            if self.toolButton_draw_strutture.isChecked():
                                # sing_layer = [self.DATA_LIST[self.REC_CORR]]
                                self.pyQGIS.charge_structure_from_research(self.DATA_LIST)
                        else:
                            strings = ("Sono stati trovati", self.REC_TOT, "records")
                            if self.toolButton_draw_strutture.isChecked():
                                # sing_layer = [self.DATA_LIST[self.REC_CORR]]
                                self.pyQGIS.charge_structure_from_research(self.DATA_LIST)
                    elif self.L=='de':
                        if self.REC_TOT == 1:
                            strings = ("Es wurde gefunden", self.REC_TOT, "record")
                            if self.toolButton_draw_strutture.isChecked():
                                # sing_layer = [self.DATA_LIST[self.REC_CORR]]
                                self.pyQGIS.charge_structure_from_research(self.DATA_LIST)
                        else:
                            strings = ("Sie wurden gefunden", self.REC_TOT, "records")
                            if self.toolButton_draw_strutture.isChecked():
                                # sing_layer = [self.DATA_LIST[self.REC_CORR]]
                                self.pyQGIS.charge_structure_from_research(self.DATA_LIST)
                                
                    else:
                        if self.REC_TOT == 1:
                            strings = ("It has been found", self.REC_TOT, "record")
                            if self.toolButton_draw_strutture.isChecked():
                                # sing_layer = [self.DATA_LIST[self.REC_CORR]]
                                self.pyQGIS.charge_structure_from_research(self.DATA_LIST)
                        else:
                            strings = ("They have been found", self.REC_TOT, "records")
                            if self.toolButton_draw_strutture.isChecked():
                                # sing_layer = [self.DATA_LIST[self.REC_CORR]]
                                self.pyQGIS.charge_structure_from_research(self.DATA_LIST)          
                    self.setComboBoxEditable(["self.comboBox_sito"], 1)
                    self.setComboBoxEditable(["self.comboBox_sigla_struttura"], 1)
                    self.setComboBoxEnable(["self.comboBox_sito"], "False")
                    self.setComboBoxEnable(["self.comboBox_sigla_struttura"], "False")
                    self.setComboBoxEnable(["self.numero_struttura"], "False")

                    self.setComboBoxEnable(["self.textEdit_descrizione_struttura"], "True")
                    self.setComboBoxEnable(["self.textEdit_interpretazione_struttura"], "True")
                    self.setTableEnable(
                        ["self.tableWidget_materiali_impiegati", "self.tableWidget_elementi_strutturali",
                         "self.tableWidget_rapporti",
                         "self.tableWidget_misurazioni"], "True")

                    QMessageBox.warning(self, "Message", "%s %d %s" % strings, QMessageBox.Ok)
        self.enable_button_search(1)

    # def on_pushButton_pdf_index_exp_pressed(self):
        # if self.L=='it':
            # Struttura_index_pdf = generate_struttura_pdf()
            # data_list = self.generate_list_pdf()
            # Struttura_index_pdf.build_index_Struttura(data_list, data_list[0][0])
        # elif self.L=='de':
            # Struttura_index_pdf = generate_struttura_pdf()
            # data_list = self.generate_list_pdf()
            # Struttura_index_pdf.build_index_Struttura_de(data_list, data_list[0][0])    
        # else:
            # Struttura_index_pdf = generate_struttura_pdf()
            # data_list = self.generate_list_pdf()
            # Struttura_index_pdf.build_index_Struttura_en(data_list, data_list[0][0])
    # def on_pushButton_pdf_exp_pressed(self):
        # if self.L=='it':
            # if self.checkBox_s_us.isChecked():
                # Struttura_pdf_sheet = generate_struttura_pdf()  # deve essere importata la classe
                # data_list = self.generate_list_pdf()  # deve essere aggiunta la funzione
                # Struttura_pdf_sheet.build_Struttura_sheets(data_list)  # deve essere aggiunto il file per generare i pdf
                # QMessageBox.warning(self, 'Ok',"Esportazione terminata Schede Struttura",QMessageBox.Ok)
            # else:   
                # pass
            # if self.checkBox_e_us.isChecked() :
                # Struttura_index_pdf = generate_struttura_pdf()
                # data_list = self.generate_list_pdf()
            
                # try:               
                    # if bool(data_list):
                        # Struttura_index_pdf.build_index_Struttura(data_list, data_list[0][0])
                        # QMessageBox.warning(self, 'Ok',"Esportazione terminata Elenco Struttura",QMessageBox.Ok)
                    # else:
                        # QMessageBox.warning(self, 'ATTENZIONE',"L'elenco Struttura non può essere esportato devi riempire prima la scheda Struttura",QMessageBox.Ok)
                # except Exception as e :
                    # QMessageBox.warning(self, 'ATTENZIONE',str(e),QMessageBox.Ok)
            # else:
                # pass
            
        
        # else:
            # if self.checkBox_s_us.isChecked():
                # Struttura_pdf_sheet = generate_struttura_pdf()  # deve essere importata la classe
                # data_list = self.generate_list_pdf()  # deve essere aggiunta la funzione
                # Struttura_pdf_sheet.build_Struttura_sheets(data_list)  # deve essere aggiunto il file per generare i pdf
                # QMessageBox.warning(self, 'Ok',"Exportation Done",QMessageBox.Ok)
            # else:   
                # pass
            # if self.checkBox_e_us.isChecked() :
                # Struttura_index_pdf = generate_struttura_pdf()
                # data_list = self.generate_list_pdf()
            
                # try:               
                    # if bool(data_list):
                        # Struttura_index_pdf.build_index_Struttura(data_list, data_list[0][0])
                        # QMessageBox.warning(self, 'Ok',"Exportation list done",QMessageBox.Ok)
                    # else:
                        # QMessageBox.warning(self, 'Warning',"The Structure list cannot be exported you have to fill in the Structure tabs before",QMessageBox.Ok)
                # except Exception as e :
                    # QMessageBox.warning(self, 'Warning',str(e),QMessageBox.Ok)
            # else:
                # pass
            
    def generate_list_pdf(self):
        data_list = []

        for i in range(len(self.DATA_LIST)):
            sito = str(self.DATA_LIST[i].sito)
            sigla_st = '{}{}{}'.format(str(self.DATA_LIST[i].sigla_struttura),'-', str(self.DATA_LIST[i].numero_struttura))            
            res_strutt = self.DB_MANAGER.query_bool({"sito": "'" + str(sito) + "'", "struttura": "'" + str(sigla_st) + "'"}, "US")
            us_strutt_list = []
            #if bool(res_strutt):
            for rs in res_strutt:
                us_strutt_list.append([str(rs.sito), str(rs.area), int(rs.us)])
                
            res_quote_strutt=''
            quote_strutt = []
            #if bool(us_strutt_list):
            for sing_us in us_strutt_list:
                res_quote_strutt = self.DB_MANAGER.select_quote_from_db_sql(sing_us[0], sing_us[1], sing_us[2])
                
            #if bool(res_quote_strutt):
            for sing_us2 in res_quote_strutt:
                sing_quota_value = str(sing_us2[5])
               
                if sing_quota_value[0] == '-':
                    sing_quota_value = sing_quota_value[:7]
                else:
                    sing_quota_value = sing_quota_value[:6]

                sing_quota = [sing_quota_value, sing_us2[4]]
                quote_strutt.append(sing_quota)
            quote_strutt.sort()

            if bool(quote_strutt):
                quota_min_strutt = '%s %s' % (quote_strutt[0][0], quote_strutt[0][1])
                quota_max_strutt = '%s %s' % (quote_strutt[-1][0], quote_strutt[-1][1])
            else:
                if self.L=='it':
                
                    quota_min_strutt = "Non inserita su GIS"
                    quota_max_strutt = "Non inserita su GIS"
                elif self.L == 'de':
                    quota_min_strutt = "Nicht im GIS einbinden "
                    quota_max_strutt = "Nicht im GIS einbinden "
                else :
                    quota_min_strutt = "Not inserted in GIS "
                    quota_max_strutt = "Not inserted in GIS  "

            data_list.append([
                str(self.DATA_LIST[i].sito.replace('_',' ')),  # 1 - Sito
                str(self.DATA_LIST[i].sigla_struttura),  # 2 -  sigla struttura
                int(self.DATA_LIST[i].numero_struttura),  # 3 - numero struttura
                str(self.DATA_LIST[i].categoria_struttura),  # 4 - categoria
                str(self.DATA_LIST[i].tipologia_struttura),  # 5 - tipologia
                str(self.DATA_LIST[i].definizione_struttura),  # 6 - definizione
                str(self.DATA_LIST[i].descrizione),  # 7 - descrizione
                str(self.DATA_LIST[i].interpretazione),  # 7 - iintepretazione
                str(self.DATA_LIST[i].periodo_iniziale),  # 8 - periodo iniziale
                str(self.DATA_LIST[i].fase_iniziale),  # 9 - fase iniziale
                str(self.DATA_LIST[i].periodo_finale),  # 10 - periodo finale
                str(self.DATA_LIST[i].fase_finale),  # 11 - fase finale
                str(self.DATA_LIST[i].datazione_estesa),  # 12 - datazione estesa
                str(self.DATA_LIST[i].materiali_impiegati),  # 13 - materiali impiegati
                str(self.DATA_LIST[i].elementi_strutturali),  # 14 - elementi strutturali
                str(self.DATA_LIST[i].rapporti_struttura),  # 15 - rapporti struttura
                str(self.DATA_LIST[i].misure_struttura),  # 16 - misure
                quota_min_strutt,  # 17 - quota min
                quota_max_strutt  # 18 - quota max
            ])
        return data_list

    def on_toolButton_draw_strutture_toggled(self):
        if self.L=='it':    
            if self.toolButton_draw_strutture.isChecked():
                QMessageBox.warning(self, "Messaggio",
                                    "Modalita' GIS attiva. Da ora le tue ricerche verranno visualizzate sul GIS",
                                    QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "Messaggio",
                                    "Modalita' GIS disattivata. Da ora le tue ricerche non verranno piu' visualizzate sul GIS",
                                    QMessageBox.Ok)
        elif self.L=='de':  
            if self.toolButton_draw_strutture.isChecked():
                QMessageBox.warning(self, "Message",
                                    "Modalität' GIS aktiv. Von jetzt wird Deine Untersuchung mit Gis visualisiert",
                                    QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "Message",
                                    "Modalität' GIS deaktiviert. Von jetzt an wird deine Untersuchung nicht mehr mit Gis visualisiert",
                                    QMessageBox.Ok)
                                    
                                    
        else:   
            if self.toolButton_draw_strutture.isChecked():
                QMessageBox.warning(self, "Message",
                                    "GIS mode active. From now on your searches will be displayed on the GIS",
                                    QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "Message",
                                    "GIS mode disabled. From now on, your searches will no longer be displayed on the GIS.",
                                    QMessageBox.Ok)                     
    def on_pushButton_draw_struttura_pressed(self):
        
        sing_layer = [self.DATA_LIST[self.REC_CORR]]
        self.pyQGIS.charge_structure_from_research(sing_layer)

    
    def on_pushButton_view_all_st_pressed(self):
        
        lista=[]
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
        
        
            for e in self.DATA_LIST:
            
                sito_p = e.sito
                sigla_st = e.sigla_struttura
                n_st = e.numero_struttura
            
            
                self.pyQGIS.charge_vector_layers_all_st(sito_p, sigla_st,n_st)
    
        except Exception as e:
            print(str(e))  
    
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

    def setComboBoxEditable(self, f, n):
        field_names = f
        value = n

        for fn in field_names:
            cmd = '{}{}{}{}'.format(fn, '.setEditable(', n, ')')
            eval(cmd)

    def setComboBoxEnable(self, f, v):
        field_names = f
        value = v

        for fn in field_names:
            cmd = '{}{}{}{}'.format(fn, '.setEnabled(', v, ')')
            eval(cmd)

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
                if value != None:
                    sub_list.append(str(value.text()))
            if bool(sub_list):
                lista.append(sub_list)
        return lista

    def setTableEnable(self, t, v):
        tab_names = t
        value = v

        for tn in tab_names:
            cmd = '{}{}{}{}'.format(tn, '.setEnabled(', v, ')')
            eval(cmd)

    def empty_fields_nosite(self):

        materiali_impiegati_row_count = self.tableWidget_materiali_impiegati.rowCount()
        elementi_strutturali_row_count = self.tableWidget_elementi_strutturali.rowCount()
        rapporti_struttura_row_count = self.tableWidget_rapporti.rowCount()
        misurazioni_row_count = self.tableWidget_misurazioni.rowCount()

        
        self.comboBox_sigla_struttura.setEditText("")  # 2 - sigla_struttura
        self.numero_struttura.clear()  # 3 - numero_struttura
        self.comboBox_categoria_struttura.setEditText("")  # 4 - categoria_struttura
        self.comboBox_tipologia_struttura.setEditText("")  # 5 - tipologia_struttura
        self.comboBox_definizione_struttura.setEditText("")  # 6 - definizione_struttura
        self.textEdit_descrizione_struttura.clear()  # 7 - descrizione
        self.textEdit_interpretazione_struttura.clear()  # 8 - interpretazione
        self.comboBox_per_iniz.setEditText("")  # 9 - periodo iniziale
        self.comboBox_fas_iniz.setEditText("")  # 10 - fase iniziale
        self.comboBox_per_fin.setEditText("")  # 11 - periodo finale iniziale
        self.comboBox_fas_fin.setEditText("")  # 12 - fase finale
        self.comboBox_datazione_estesa.setEditText("")  # 13 - datazione estesa

        for i in range(materiali_impiegati_row_count):
            self.tableWidget_materiali_impiegati.removeRow(0)
        self.insert_new_row("self.tableWidget_materiali_impiegati")  # 14 - materiali impiegati

        for i in range(elementi_strutturali_row_count):
            self.tableWidget_elementi_strutturali.removeRow(0)
        self.insert_new_row("self.tableWidget_elementi_strutturali")  # 15 - elementi_strutturali

        for i in range(rapporti_struttura_row_count):
            self.tableWidget_rapporti.removeRow(0)
        self.insert_new_row("self.tableWidget_rapporti")  # 16 - rapporti struttura

        for i in range(misurazioni_row_count):
            self.tableWidget_misurazioni.removeRow(0)
        self.insert_new_row("self.tableWidget_misurazioni")  # 17 - rapporti struttura
    def empty_fields(self):

        materiali_impiegati_row_count = self.tableWidget_materiali_impiegati.rowCount()
        elementi_strutturali_row_count = self.tableWidget_elementi_strutturali.rowCount()
        rapporti_struttura_row_count = self.tableWidget_rapporti.rowCount()
        misurazioni_row_count = self.tableWidget_misurazioni.rowCount()

        self.comboBox_sito.setEditText("")  # 1 - Sito
        self.comboBox_sigla_struttura.setEditText("")  # 2 - sigla_struttura
        self.numero_struttura.clear()  # 3 - numero_struttura
        self.comboBox_categoria_struttura.setEditText("")  # 4 - categoria_struttura
        self.comboBox_tipologia_struttura.setEditText("")  # 5 - tipologia_struttura
        self.comboBox_definizione_struttura.setEditText("")  # 6 - definizione_struttura
        self.textEdit_descrizione_struttura.clear()  # 7 - descrizione
        self.textEdit_interpretazione_struttura.clear()  # 8 - interpretazione
        self.comboBox_per_iniz.setEditText("")  # 9 - periodo iniziale
        self.comboBox_fas_iniz.setEditText("")  # 10 - fase iniziale
        self.comboBox_per_fin.setEditText("")  # 11 - periodo finale iniziale
        self.comboBox_fas_fin.setEditText("")  # 12 - fase finale
        self.comboBox_datazione_estesa.setEditText("")  # 13 - datazione estesa

        for i in range(materiali_impiegati_row_count):
            self.tableWidget_materiali_impiegati.removeRow(0)
        self.insert_new_row("self.tableWidget_materiali_impiegati")  # 14 - materiali impiegati

        for i in range(elementi_strutturali_row_count):
            self.tableWidget_elementi_strutturali.removeRow(0)
        self.insert_new_row("self.tableWidget_elementi_strutturali")  # 15 - elementi_strutturali

        for i in range(rapporti_struttura_row_count):
            self.tableWidget_rapporti.removeRow(0)
        self.insert_new_row("self.tableWidget_rapporti")  # 16 - rapporti struttura

        for i in range(misurazioni_row_count):
            self.tableWidget_misurazioni.removeRow(0)
        self.insert_new_row("self.tableWidget_misurazioni")  # 17 - rapporti struttura

    def fill_fields(self, n=0):
        self.rec_num = n

        try:

            self.comboBox_sito.setEditText(self.DATA_LIST[self.rec_num].sito)  # 1 - Sito
            self.comboBox_sigla_struttura.setEditText(str(self.DATA_LIST[self.rec_num].sigla_struttura))  # 2 - Periodo
            self.numero_struttura.setText(str(self.DATA_LIST[self.rec_num].numero_struttura))  # 3 - Fase
            self.comboBox_categoria_struttura.setEditText(
                str(self.DATA_LIST[self.rec_num].categoria_struttura))  # 4 - Fase
            self.comboBox_tipologia_struttura.setEditText(
                str(self.DATA_LIST[self.rec_num].tipologia_struttura))  # 5 - tipologia_struttura
            self.comboBox_definizione_struttura.setEditText(
                str(self.DATA_LIST[self.rec_num].definizione_struttura))  # 6 - definizione_struttura
            str(self.textEdit_descrizione_struttura.setText(
                self.DATA_LIST[self.rec_num].descrizione))  # 6 - descrizione
            str(self.textEdit_interpretazione_struttura.setText(
                self.DATA_LIST[self.rec_num].interpretazione))  # 7 - interpretazione
            self.comboBox_datazione_estesa.setEditText(
                str(self.DATA_LIST[self.rec_num].datazione_estesa))  # 12 - datazione estesa
            self.tableInsertData("self.tableWidget_materiali_impiegati",
                                 self.DATA_LIST[self.rec_num].materiali_impiegati)  # 13 - materiali impiegati
            self.tableInsertData("self.tableWidget_elementi_strutturali",
                                 self.DATA_LIST[self.rec_num].elementi_strutturali)  # 14 - elementi struttura
            self.tableInsertData("self.tableWidget_rapporti",
                                 self.DATA_LIST[self.rec_num].rapporti_struttura)  # 15 - rapporti struttura
            self.tableInsertData("self.tableWidget_misurazioni",
                                 self.DATA_LIST[self.rec_num].misure_struttura)  # 16 - misure struttura

            if self.DATA_LIST[self.rec_num].periodo_iniziale == None:
                self.comboBox_per_iniz.setEditText("")
            else:
                self.comboBox_per_iniz.setEditText(str(self.DATA_LIST[self.rec_num].periodo_iniziale))

            if self.DATA_LIST[self.rec_num].fase_iniziale == None:
                self.comboBox_fas_iniz.setEditText("")
            else:
                self.comboBox_fas_iniz.setEditText(str(self.DATA_LIST[self.rec_num].fase_iniziale))

            if self.DATA_LIST[self.rec_num].periodo_finale == None:
                self.comboBox_per_fin.setEditText("")
            else:
                self.comboBox_per_fin.setEditText(str(self.DATA_LIST[self.rec_num].periodo_finale))

            if self.DATA_LIST[self.rec_num].fase_finale == None:
                self.comboBox_fas_fin.setEditText("")
            else:
                self.comboBox_fas_fin.setEditText(str(self.DATA_LIST[self.rec_num].fase_finale))

        except :#Exception as e:
            pass#QMessageBox.warning(self, "Errore fill", str(e), QMessageBox.Ok)

    def set_rec_counter(self, t, c):
        self.rec_tot = t
        self.rec_corr = c
        self.label_rec_tot.setText(str(self.rec_tot))
        self.label_rec_corrente.setText(str(self.rec_corr))

    def set_LIST_REC_TEMP(self):
        # data
        if self.numero_struttura.text() == "":
            numero_struttura = None
        else:
            numero_struttura = self.numero_struttura.text()

        if self.comboBox_per_iniz.currentText() == "":
            periodo_iniziale = None
        else:
            periodo_iniziale = self.comboBox_per_iniz.currentText()

        if self.comboBox_fas_iniz.currentText() == "":
            fase_iniziale = None
        else:
            fase_iniziale = self.comboBox_fas_iniz.currentText()

        if self.comboBox_per_fin.currentText() == "":
            periodo_finale = None
        else:
            periodo_finale = self.comboBox_per_fin.currentText()

        if self.comboBox_fas_fin.currentText() == "":
            fase_finale = None
        else:
            fase_finale = self.comboBox_fas_fin.currentText()

        ##Campioni
        materiali_impiegati = self.table2dict("self.tableWidget_materiali_impiegati")
        ##Elementi_strutturali
        elementi_strutturali = self.table2dict("self.tableWidget_elementi_strutturali")
        ##Rapporti_struttura
        rapporti_struttura = self.table2dict("self.tableWidget_rapporti")
        ##Misurazioni
        misurazioni = self.table2dict("self.tableWidget_misurazioni")

        self.DATA_LIST_REC_TEMP = [
            str(self.comboBox_sito.currentText()),  # 1 - Sito
            str(self.comboBox_sigla_struttura.currentText()),  # 2 - sigla
            str(numero_struttura),  # 3 - numero_struttura
            str(self.comboBox_categoria_struttura.currentText()),  # 3 - categoria
            str(self.comboBox_tipologia_struttura.currentText()),  # 3 - tipologia
            str(self.comboBox_definizione_struttura.currentText()),  # 4 - definizione
            str(self.textEdit_descrizione_struttura.toPlainText()),  # 6 - descrizione
            str(self.textEdit_interpretazione_struttura.toPlainText()),  # 6 - intepretazione
            str(periodo_iniziale),  # 6 - periodo iniziale
            str(fase_iniziale),  # 6 - fase iniziale
            str(periodo_finale),  # 6 - periodo finale
            str(fase_finale),  # 6 - fase finale
            str(self.comboBox_datazione_estesa.currentText()),  # 7- cron estesa
            str(materiali_impiegati),  # 8-  materiali impiegati
            str(elementi_strutturali),  # 8- elementi strutturali
            str(rapporti_struttura),  # 8- rapporti struttura
            str(misurazioni)  # 8- misurazioni
        ]

    def rec_toupdate(self):
        rec_to_update = self.UTILITY.pos_none_in_list(self.DATA_LIST_REC_TEMP)
        return rec_to_update

    def set_LIST_REC_CORR(self):
        self.DATA_LIST_REC_CORR = []
        for i in self.TABLE_FIELDS:
            self.DATA_LIST_REC_CORR.append(eval("unicode(self.DATA_LIST[self.REC_CORR]." + i + ")"))

    def records_equal_check(self):
        self.set_LIST_REC_TEMP()
        self.set_LIST_REC_CORR()
        if self.DATA_LIST_REC_CORR == self.DATA_LIST_REC_TEMP:
            return 0
        else:
            return 1

    def tableInsertData(self, t, d):
        """Set the value into alls Grid"""
        self.table_name = t
        self.data_list = eval(d)
        self.data_list.sort()

        # column table count
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

        for row in range(len(self.data_list)):
            cmd = ('%s.insertRow(%s)') % (self.table_name, row)
            eval(cmd)
            for col in range(len(self.data_list[row])):
                # item = self.comboBox_sito.setEditText(self.data_list[0][col]
                item = QTableWidgetItem(self.data_list[row][col])
                exec_str = ('%s.setItem(%d,%d,item)') % (self.table_name, row, col)
                eval(exec_str)

                # insert new row into tableWidget

    def on_pushButton_insert_row_rapporti_pressed(self):
        self.insert_new_row('self.tableWidget_rapporti')

    def on_pushButton_remove_row_rapporti_pressed(self):
        self.remove_row('self.tableWidget_rapporti')

    ##

    def on_pushButton_insert_row_materiali_pressed(self):
        self.insert_new_row('self.tableWidget_materiali_impiegati')

    def on_pushButton_remove_row_materiali_pressed(self):
        self.remove_row('self.tableWidget_materiali_impiegati')

    ##
    def on_pushButton_insert_row_elementi_pressed(self):
        self.insert_new_row('self.tableWidget_elementi_strutturali')

    def on_pushButton_remove_row_elementi_pressed(self):
        self.remove_row('self.tableWidget_elementi_strutturali')

    def on_pushButton_insert_row_misurazioni_pressed(self):
        self.insert_new_row('self.tableWidget_misurazioni')

    def on_pushButton_remove_row_misurazioni_pressed(self):
        self.remove_row('self.tableWidget_misurazioni')

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
        if not rowSelected:
            QMessageBox.warning(self, "Error", "not record selected", QMessageBox.Ok)
            return
        rowIndex = (rowSelected[0].row())
        cmd = ("%s.removeRow(%d)") % (table_name, rowIndex)
        eval(cmd)

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

