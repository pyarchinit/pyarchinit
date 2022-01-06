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
import os
import platform
from pdf2docx import parse
from datetime import date
import cv2
from builtins import range
from builtins import str
from qgis.PyQt.QtWidgets import QDialog, QMessageBox, QTableWidgetItem
from qgis.PyQt.uic import loadUiType
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import QColor, QIcon
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.uic import loadUiType
from qgis.core import QgsSettings
from ..modules.db.pyarchinit_conn_strings import Connection
from ..modules.db.pyarchinit_db_manager import Pyarchinit_db_management
from ..modules.db.pyarchinit_utility import Utility
from ..modules.gis.pyarchinit_pyqgis import Pyarchinit_pyqgis
#from ..modules.utility.pdf_models.pyarchinit_exp_Findssheet_pdf import generate_pdf
from ..modules.utility.pyarchinit_error_check import Error_check
from ..modules.utility.pyarchinit_exp_Individui_pdf import generate_pdf
from ..gui.sortpanelmain import SortPanelMain
from ..gui.pyarchinitConfigDialog import pyArchInitDialog_Config
MAIN_DIALOG_CLASS, _ = loadUiType(os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'Schedaind.ui'))


class pyarchinit_Schedaind(QDialog, MAIN_DIALOG_CLASS):
    L=QgsSettings().value("locale/userLocale")[0:2]
    if L=='it':
        MSG_BOX_TITLE = "PyArchInit - Scheda Individui"
    elif L=='en':
        MSG_BOX_TITLE = "PyArchInit - Individual Form"
    elif L=='de':
        MSG_BOX_TITLE = "PyArchInit - Formular Individuel"
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
    SORT_ITEMS_CONVERTED = ''
    UTILITY = Utility()
    DB_MANAGER = ""
    TABLE_NAME = 'individui_table'
    MAPPER_TABLE_CLASS = "SCHEDAIND"
    NOME_SCHEDA = "Scheda Individuo"
    ID_TABLE = "id_scheda_ind"
    if L=='it':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Sito": "sito",
            "Area": "area",
            "US": "us",
            "Nr. Individuo": "nr_individuo",
            "Data Schedatura": "data_schedatura",
            "Schedatore": "schedatore",
            "Stima del sesso": "sesso",
            "Stima dell'eta' di morte min": "eta_min",
            "Stima dell'eta' di morte max": "eta_max",
            "Classi di eta'": "classi_eta",
            "Osservazioni": "osservazioni",
            "Sigla struttura":"sigla_struttura",
            "Nr struttura":"nr_struttura",
            "Completo si no":"completo_si_no",
            "Disturbato si no":"disturbato_si_no",
            "In connessione si no":"in_connessione_si_no",
            "Lunghezza scheletro":"lunghezza_scheletro",
            "Posizione scheletro":"posizione_scheletro",
            "Posizione cranio":"posizione_cranio",
            "Posizione arti superiori":"posizione_arti_superiori",
            "Posizione arti inferiori":"posizione_arti_inferiori",
            "Orientamento asse":"orientamento_asse",
            "Orientamento azimut":"orientamento_azimut"          
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Sito",
            "Area",
            "US",
            "Nr. Individuo",
            "Data schedatura",
            "Schedatore",
            "Stima del sesso",
            #"Stima dell'eta' di morte min",
            #"Stima dell'eta' di morte max",
            "Classi di eta'",
            "Osservazioni"
        ]
    elif L=='de':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Ausgrabungsstätte": "sito",
            "SE": "us",
            "Areal": "area",
            "Nr. Individuel": "nr_individuo",
            "Katalogisierungsdaten": "data_schedatura",
            "Physikalische Daten": "schedatore",
            "Geschätztes Geschlecht": "sesso",
            "Schätzung des Todesalters  min": "eta_min",
            "Schätzung des Todesalters  max": "eta_max",
            "Altersklassen": "classi_eta",
            "Beobachtungen": "osservazioni"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Ausgrabungsstätte",
            "SE",
            "Areal",
            "Nr. Individuel",
            "Katalogisierungsdaten",
            "Physikalische Daten",
            "Geschätztes Geschlecht",
            "Schätzung des Todesalters  min",
            "Schätzung des Todesalters  max",
            "Altersklassen",
            "Beobachtungen"
        ]
    else:
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Site": "sito",
            "SU": "us",
            "Area": "area",
            "Individual Nr.": "nr_individuo",
            "Date Form": "data_schedatura",
            "Filler": "schedatore",
            "Extimation sex": "sesso",
            "Extimation age of death min": "eta_min",
            "Extimation age of death max": "eta_max",
            "Age class": "classi_eta",
            "Note": "osservazioni"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Site",
            "SU",
            "Area",
            "Individual Nr.",
            "Date Form",
            "Filler",
            "Extimation sex",
            "Extimation age of death min",
            "Extimation age of death max",
            "Age class",
            "Note"
        ]   
    TABLE_FIELDS = [
        'sito',
        'area',
        'us',
        'nr_individuo',
        'data_schedatura',
        'schedatore',
        'sesso',
        'eta_min',
        'eta_max',
        'classi_eta',
        'osservazioni',
        'sigla_struttura',
        'nr_struttura',
        'completo_si_no',
        'disturbato_si_no',
        'in_connessione_si_no',
        'lunghezza_scheletro',
        'posizione_scheletro',
        'posizione_cranio',
        'posizione_arti_superiori',
        'posizione_arti_inferiori',
        'orientamento_asse',
        'orientamento_azimut'   
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
    
    HOME = os.environ['PYARCHINIT_HOME']
    PDFFOLDER = '{}{}{}'.format(HOME, os.sep, "pyarchinit_PDF_folder")
    DB_SERVER = "not defined"  ####nuovo sistema sort
    
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
            QMessageBox.warning(self, "Connection System", str(e), QMessageBox.Ok)
        # SIGNALS & SLOTS Functions
        
        self.lineEdit_individuo.setText('')
        
        self.lineEdit_individuo.textChanged.connect(self.update)
        self.lineEdit_individuo.textChanged.connect(self.charge_struttura_list)
       
        self.lineEdit_individuo.textChanged.connect(self.charge_struttura_nr)
        ###########################da attivare ma vi è un baco che bisogna capire dove#############################
        # self.lineEdit_individuo.textChanged.connect(self.charge_area)
        # self.lineEdit_individuo.textChanged.connect(self.charge_us)
        ############################fine#####################################################################
        self.toolButton_pdfpath.clicked.connect(self.setPathpdf)
        self.pbnOpenpdfDirectory.clicked.connect(self.openpdfDir)
        sito = self.comboBox_sito.currentText()
        self.comboBox_sito.setEditText(sito)
        
        self.fill_fields()
        self.set_sito()
        self.msg_sito()
        self.numero_invetario()
    def numero_invetario(self):
        
        contatore = 0
        list=[]
        if self.lineEdit_individuo.text()=='':
            self.lineEdit_individuo.clear()
            self.lineEdit_individuo.setText('1')
            self.lineEdit_individuo.update()
            for i in range(len(self.DATA_LIST)):
                self.lineEdit_individuo.clear()
                contatore = int(self.DATA_LIST[i].nr_individuo)
                #contatore.sort(reverse=False)
                list.append(contatore)
                
               
                list[-1]+=1
                
                list.sort()
            for e in list:    
                
                self.lineEdit_individuo.setText(str(e))
    
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
                    
                    QMessageBox.warning(self,"WILLKOMMEN","WILLKOMMEN in pyArchInit" + "individuel formular"+ ". Die Datenbank ist leer. Tippe 'Ok' und aufgehts!",
                                        QMessageBox.Ok) 
                else:
                    QMessageBox.warning(self,"WELCOME", "Welcome in pyArchInit" + "individual form" + ". The DB is empty. Push 'Ok' and Good Work!",
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
        self.setComboBoxEditable(["self.comboBox_sigla_struttura"], 1)
        self.setComboBoxEditable(["self.comboBox_nr_struttura"], 1)
        self.setComboBoxEditable(["self.comboBox_area"], 1)
        self.setComboBoxEditable(["self.comboBox_us"], 1)

    def loadMapPreview(self, mode=0):
        pass

    def charge_list(self):

        l = QgsSettings().value("locale/userLocale", QVariant)
        lang = ""
        for key, values in self.LANG.items():
            if values.__contains__(l):
                lang = str(key)
        lang = "'" + lang + "'"

        # lista sito

        sito_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('site_table', 'sito', 'SITE'))
        try:
            sito_vl.remove('')
        except:
            pass

        self.comboBox_sito.clear()

        sito_vl.sort()
        self.comboBox_sito.addItems(sito_vl)

        # lista rito

        self.comboBox_disturbato.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'individui_table' + "'",
            'tipologia_sigla': "'" + '801.801' + "'"
        }

        disturbato = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        disturbato_vl = []

        for i in range(len(disturbato)):
            disturbato_vl.append(disturbato[i].sigla)

        disturbato_vl.sort()
        self.comboBox_disturbato.addItems(disturbato_vl)

        self.comboBox_completo.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'individui_table' + "'",
            'tipologia_sigla': "'" + '801.801' + "'"
        }

        completo = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        completo_vl = []

        for i in range(len(completo)):
            completo_vl.append(completo[i].sigla)

        completo_vl.sort()
        self.comboBox_completo.addItems(completo_vl)

        
        self.comboBox_in_connessione.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'individui_table' + "'",
            'tipologia_sigla': "'" + '801.801' + "'"
        }

        in_connessione = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        in_connessione_vl = []

        for i in range(len(in_connessione)):
            in_connessione_vl.append(in_connessione[i].sigla)

        in_connessione_vl.sort()
        self.comboBox_in_connessione.addItems(in_connessione_vl)

        
        # lista segnacoli

        self.comboBox_posizione_cranio.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'individui_table' + "'",
            'tipologia_sigla': "'" + '8.1' + "'"
        }

        posizione_cranio = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        posizione_cranio_vl = []

        for i in range(len(posizione_cranio)):
            posizione_cranio_vl.append(posizione_cranio[i].sigla_estesa)

        posizione_cranio_vl.sort()
        self.comboBox_posizione_cranio.addItems(posizione_cranio_vl)

        
        self.comboBox_posizione_scheletro.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'individui_table' + "'",
            'tipologia_sigla': "'" + '8.2' + "'"
        }

        posizione_scheletro = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        posizione_scheletro_vl = []

        for i in range(len(posizione_scheletro)):
            posizione_scheletro_vl.append(posizione_scheletro[i].sigla_estesa)

        posizione_scheletro_vl.sort()
        self.comboBox_posizione_scheletro.addItems(posizione_scheletro_vl)
        
        self.comboBox_orientamento_asse.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'individui_table' + "'",
            'tipologia_sigla': "'" + '8.3' + "'"
        }

        orientamento_asse = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        orientamento_asse_vl = []

        for i in range(len(orientamento_asse)):
            orientamento_asse_vl.append(orientamento_asse[i].sigla_estesa)

        orientamento_asse_vl.sort()
        self.comboBox_orientamento_asse.addItems(orientamento_asse_vl)
       
        self.comboBox_arti_superiori.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'individui_table' + "'",
            'tipologia_sigla': "'" + '8.4' + "'"
        }

        arti_superiori = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        arti_superiori_vl = []

        for i in range(len(arti_superiori)):
            arti_superiori_vl.append(arti_superiori[i].sigla_estesa)

        arti_superiori_vl.sort()
        self.comboBox_arti_superiori.addItems(arti_superiori_vl)
       
        self.comboBox_arti_inferiori.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'individui_table' + "'",
            'tipologia_sigla': "'" + '8.5' + "'"
        }

        arti_inferiori = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        arti_inferiori_vl = []

        for i in range(len(arti_inferiori)):
            arti_inferiori_vl.append(arti_inferiori[i].sigla_estesa)

        arti_inferiori_vl.sort()
        self.comboBox_arti_inferiori.addItems(arti_inferiori_vl)
        
        
        
    
    
    
    def msg_sito(self):
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
            
                QMessageBox.information(self, "Warnung" , "Es gibt keine solche archäologische Stätte: "'""'+ str(site_set_str) +'"'" in dieser Registerkarte, Bitte deaktivieren Sie die 'Site-Wahl' in der Plugin-Konfigurationsregisterkarte, um alle Datensätze zu sehen oder die Registerkarte zu erstellen",QMessageBox.Ok) 
            else:
            
                QMessageBox.information(self, "Warning" , "There is no such site: "'"'+ str(site_set_str) +'"'" in this tab, Please disable the 'site choice' from the plugin configuration tab to see all records or create the tab",QMessageBox.Ok) 
    
    
    
    def charge_struttura_nr(self): 
        
        search_dict = {
            'sito': "'" + str(self.comboBox_sito.currentText()) + "'"
        }

        struttura_vl = self.DB_MANAGER.query_bool(search_dict, 'TOMBA')
        
        nr_struttura_list=[]
        for i in range(len(struttura_vl)):
            #if not nr_struttura_list.__contains__(str(struttura_vl[i].numero_struttura)):
            nr_struttura_list.append(str(struttura_vl[i].nr_struttura))
        try:
            nr_struttura_list.remove('')
        except:
            pass
        self.comboBox_nr_struttura.clear()
        nr_struttura_list.sort()
        self.comboBox_nr_struttura.addItems(self.UTILITY.remove_dup_from_list(nr_struttura_list))
        if self.STATUS_ITEMS[self.BROWSE_STATUS] == "Trova" or "Finden" or "Find":
                
                self.comboBox_nr_struttura.setEditText("")
        elif self.STATUS_ITEMS[self.BROWSE_STATUS] == "Usa" or "Aktuell " or "Current":
            try:    
                if len(self.DATA_LIST) > 0:
        
                    
                    self.comboBox_nr_struttura.setEditText(self.DATA_LIST[self.rec_num].nr_struttura)
            except:
                pass
    def charge_struttura_list(self):
        
        search_dict = {
            'sito': "'" + str(self.comboBox_sito.currentText()) + "'"
        }

        struttura_vl = self.DB_MANAGER.query_bool(search_dict, 'TOMBA')
        sigla_struttura_list = []
        for i in range(len(struttura_vl)):
            sigla_struttura_list.append(str(struttura_vl[i].sigla_struttura))
        try:
            sigla_struttura_list.remove('')
        except:
            pass
        self.comboBox_sigla_struttura.clear()
        sigla_struttura_list.sort()

        self.comboBox_sigla_struttura.addItems(self.UTILITY.remove_dup_from_list(sigla_struttura_list))

        if self.STATUS_ITEMS[self.BROWSE_STATUS] == "Trova" or "Finden" or "Find":
                self.comboBox_sigla_struttura.setEditText("")
                
        elif self.STATUS_ITEMS[self.BROWSE_STATUS] == "Usa" or "Aktuell " or "Current":
            try:    
                if len(self.DATA_LIST) > 0:
        
                    self.comboBox_sigla_struttura.setEditText(self.DATA_LIST[self.rec_num].sigla_struttura)
                    
            except:
                pass
    ##################################da attivare###########################################
    # def charge_area(self): 
        
        # search_dict = {
            # 'sito': "'" + str(self.comboBox_sito.currentText()) + "'"
        # }

        # area_vl = self.DB_MANAGER.query_bool(search_dict, 'TOMBA')
        
        # nr_area_list=[]
        # for i in range(len(area_vl)):
            # #if not nr_area_list.__contains__(str(area_vl[i].numero_area)):
            # nr_area_list.append(str(area_vl[i].area))
        # try:
            # nr_area_list.remove('')
        # except:
            # pass
        # self.comboBox_area.clear()
        # nr_area_list.sort()
        # self.comboBox_area.addItems(self.UTILITY.remove_dup_from_list(nr_area_list))
        # if self.STATUS_ITEMS[self.BROWSE_STATUS] == "Trova" or "Finden" or "Find":
                
            # self.comboBox_area.setEditText("")
        
        # elif self.STATUS_ITEMS[self.BROWSE_STATUS] == "Usa" or "Aktuell " or "Current":
                
            # if len(self.DATA_LIST) > 0:
                # try:
                    
                    # self.comboBox_area.setEditText(self.DATA_LIST[self.rec_num].area)
                # except:
                    # pass
    
    # def charge_us(self): 
        
        # search_dict = {
            # 'sito': "'" + str(self.comboBox_sito.currentText()) + "'",
            # 'area': "'" +  str(eval('self.DATA_LIST[int(self.REC_CORR)].area'))+ "'",
            # #'unita_tipo': "US",
            # 'struttura': "'" + str(eval('self.DATA_LIST[int(self.REC_CORR)].sigla_struttura'))+'-'+ str(eval('self.DATA_LIST[int(self.REC_CORR)].nr_struttura'))+"'"
        # }
        # #QMessageBox.warning(self, "ATTENZIONE", str(search_dict), QMessageBox.Ok)
        # us_vl = self.DB_MANAGER.query_bool(search_dict, 'US')
        
        # nr_us_list=[]
        # for i in range(len(us_vl)):
            # #if not nr_us_list.__contains__(str(us_vl[i].numero_us)):
            # nr_us_list.append(str(us_vl[i].us))
        # try:
            # nr_us_list.remove('')
        # except:
            # pass
        # self.comboBox_us.clear()
        # nr_us_list.sort()
        # self.comboBox_us.addItems(self.UTILITY.remove_dup_from_list(nr_us_list))
        # if self.STATUS_ITEMS[self.BROWSE_STATUS] == "Trova" or "Finden" or "Find":
                
            # self.comboBox_us.setEditText("")
        # elif self.STATUS_ITEMS[self.BROWSE_STATUS] == "Usa" or "Aktuell " or "Current":
            # try:    
                # if len(self.DATA_LIST) > 0:
        
                    
                    # self.comboBox_us.setEditText(self.DATA_LIST[self.rec_num].us)
            # except:
                # pass
    
    
    ######################################fine###################################################
    
    
    def charge_periodo_list(self):
        pass

    def charge_fase_iniz_list(self):
        pass

    def charge_fase_fin_list(self):
        pass

        # buttons functions

    def generate_list_pdf(self):
        data_list = []
        for i in range(len(self.DATA_LIST)):
            data_list.append([
                str(self.DATA_LIST[i].sito.replace('_',' ')),  # 1 - Sito
                str(self.DATA_LIST[i].area),  # 2 - Area
                str(self.DATA_LIST[i].us),  # 3 - us
                str(self.DATA_LIST[i].nr_individuo),  # 4 -  nr individuo
                str(self.DATA_LIST[i].data_schedatura),  # 5 - data schedatura
                str(self.DATA_LIST[i].schedatore),  # 6 - schedatore
                str(self.DATA_LIST[i].sesso),  # 7 - sesso
                str(self.DATA_LIST[i].eta_min),  # 8 - eta' minima
                str(self.DATA_LIST[i].eta_max),  # 9- eta massima
                str(self.DATA_LIST[i].classi_eta),  # 10 - classi di eta'
                str(self.DATA_LIST[i].osservazioni),
                str(self.DATA_LIST[i].sigla_struttura),
                str(self.DATA_LIST[i].nr_struttura),
                str(self.DATA_LIST[i].completo_si_no),
                str(self.DATA_LIST[i].disturbato_si_no),
                str(self.DATA_LIST[i].in_connessione_si_no),
                str(self.DATA_LIST[i].lunghezza_scheletro),
                str(self.DATA_LIST[i].posizione_scheletro),
                str(self.DATA_LIST[i].posizione_cranio),
                str(self.DATA_LIST[i].posizione_arti_superiori),
                str(self.DATA_LIST[i].posizione_arti_inferiori),
                str(self.DATA_LIST[i].orientamento_asse),
                str(self.DATA_LIST[i].orientamento_azimut)   
            ])
        return data_list

    
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

    def on_toolButtonGis_toggled(self):
        if self.L=='it':
            if self.toolButtonGis.isChecked():
                QMessageBox.warning(self, "Messaggio",
                                    "Modalita' GIS attiva. Da ora le tue ricerche verranno visualizzate sul GIS",
                                    QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "Messaggio",
                                    "Modalita' GIS disattivata. Da ora le tue ricerche non verranno piu' visualizzate sul GIS",
                                    QMessageBox.Ok)
        elif self.L=='de':
            if self.toolButtonGis.isChecked():
                QMessageBox.warning(self, "Message",
                                    "Modalität' GIS aktiv. Von jetzt wird Deine Untersuchung mit Gis visualisiert",
                                    QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "Message",
                                    "Modalität' GIS deaktiviert. Von jetzt an wird deine Untersuchung nicht mehr mit Gis visualisiert",
                                    QMessageBox.Ok)
        else:
            if self.toolButtonGis.isChecked():
                QMessageBox.warning(self, "Message",
                                    "GIS mode active. From now on your searches will be displayed on the GIS",
                                    QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "Message",
                                    "GIS mode disabled. From now on, your searches will no longer be displayed on the GIS.",
                                    QMessageBox.Ok)
                                    
    # def on_toolButtonPreview_toggled(self):
        # if self.L=='it':
            # if self.toolButtonPreview.isChecked():
                # QMessageBox.warning(self, "Messaggio",
                                    # "Modalita' Preview US attivata. Le piante delle US saranno visualizzate nella sezione Piante",
                                    # QMessageBox.Ok)
                # self.loadMapPreview()
            # else:
                # self.loadMapPreview(1)
        # elif self.L=='de':
            # if self.toolButtonPreview.isChecked():
                # QMessageBox.warning(self, "Message",
                                    # "Modalität' Preview der aktivierten SE. Die Plana der SE werden in der Auswahl der Plana visualisiert",
                                    # QMessageBox.Ok)
                # self.loadMapPreview()
            # else:
                # self.loadMapPreview(1)
                
        # else:
            # if self.toolButtonPreview.isChecked():
                # QMessageBox.warning(self, "Message",
                                    # "Preview SU mode enabled. US plants will be displayed in the Plants section",
                                    # QMessageBox.Ok)
                # self.loadMapPreview()
            # else:
                # self.loadMapPreview(1)

    """
    def on_pushButton_addRaster_pressed(self):
        if self.toolButtonGis.isChecked() == True:
            self.pyQGIS.addRasterLayer()
    """

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
                            pass
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

        if self.BROWSE_STATUS != "n":
            if bool(self.comboBox_sito.currentText()) and self.comboBox_sito.currentText()==sito_set_str:
                self.BROWSE_STATUS = "n"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.empty_fields_nosite()
                self.label_sort.setText(self.SORTED_ITEMS["n"])

                #self.setComboBoxEditable(["self.comboBox_sito"], 0)
                self.setComboBoxEnable(["self.comboBox_sito"], "False")
                # self.setComboBoxEnable(["self.comboBox_area"], "True")
                # self.setComboBoxEnable(["self.comboBox_us"], "True")
                self.setComboBoxEnable(["self.lineEdit_individuo"], "True")
                self.SORT_STATUS = "n"
                self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.set_rec_counter('', '')
                self.label_sort.setText(self.SORTED_ITEMS["n"])
                self.numero_invetario()
            else:
                self.BROWSE_STATUS = "n"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.empty_fields()
                self.label_sort.setText(self.SORTED_ITEMS["n"])

                self.setComboBoxEditable(["self.comboBox_sito"], 1)
                self.setComboBoxEnable(["self.comboBox_sito"], "True")
                # self.setComboBoxEnable(["self.comboBox_area"], "True")
                # self.setComboBoxEnable(["self.comboBox_us"], "True")
                self.setComboBoxEnable(["self.lineEdit_individuo"], "True")

                self.SORT_STATUS = "n"
                self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.set_rec_counter('', '')
                self.numero_invetario()                
            self.enable_button(0)

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
                    self.setComboBoxEnable(["self.comboBox_sito"], "False")
                    # self.setComboBoxEnable(["self.comboBox_area"], "False")
                    # self.setComboBoxEnable(["self.comboBox_us"], "False")
                    self.setComboBoxEnable(["self.lineEdit_individuo"], "False")
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
        if self.L=='it':
            if EC.data_is_empty(str(self.comboBox_sito.currentText())) == 0:
                QMessageBox.warning(self, "ATTENZIONE", "Campo Sito. \n Il campo non deve essere vuoto", QMessageBox.Ok)
                test = 1

            
            if EC.data_is_empty(str(self.lineEdit_individuo.text())) == 0:
                QMessageBox.warning(self, "ATTENZIONE", "Campo nr individuo. \n Il campo non deve essere vuoto",
                                    QMessageBox.Ok)
                test = 1

            area = self.comboBox_area.currentText()
            # us = self.comboBox_us.currentText()
            #nr_individuo = self.lineEdit_individuo.text()
            # eta_min = self.comboBox_eta_min.currentText()
            # eta_max = self.comboBox_eta_max.currentText()
            lunghezza_scheletro = self.lineEdit_lunghezza_scheletro.text()
            #azimut = self.lineEdit_orientamento_azimut.text()
            if area != "":
                if EC.data_lenght(area, 3) == '':
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Campo Area. \n Il valore deve essere lungo massimo 4 caratteri alfanumerici",
                                        QMessageBox.Ok)
                    test = 1

            # if us != "":
                # if EC.data_is_int(us) == 0:
                    # QMessageBox.warning(self, "ATTENZIONE", "Campo US. \n Il valore deve essere di tipo numerico",
                                        # QMessageBox.Ok)
                    # test = 1

            # if nr_individuo != "":
                # if EC.data_is_int(nr_individuo) == 0:
                    # QMessageBox.warning(self, "ATTENZIONE", "Campo Nr individuo. \n Il valore deve essere di tipo numerico",
                                        # QMessageBox.Ok)
                    # test = 1

            # if eta_min != "":
                # if EC.data_is_int(eta_min) == 0:
                    # QMessageBox.warning(self, "ATTENZIONE", "Campo Età minima \n Il valore deve essere di tipo numerico",
                                        # QMessageBox.Ok)
                    # test = 1

            # if eta_max != "":
                # if EC.data_is_int(eta_max) == 0:
                    # QMessageBox.warning(self, "ATTENZIONE", "Campo Età massima \n Il valore deve essere di tipo numerico",
                                        # QMessageBox.Ok)
                    # test = 1
            if lunghezza_scheletro != "":
                if EC.data_is_float(lunghezza_scheletro) == 0:
                    QMessageBox.warning(self, "ATTENZIONE", "Campo Lunghezza Scheletro. \n Il valore deve essere di tipo numerico. \n (Sono stati inserite lettere, virgole, accenti o caratteri non numerici.",
                                        QMessageBox.Ok)
                    test = 1
            
        
        elif self.L=='de':  
            if EC.data_is_empty(str(self.comboBox_sito.currentText())) == 0:
                QMessageBox.warning(self, "ACHTUNG", " Feld Ausgrabungstätte. \n Das Feld darf nicht leer sein", QMessageBox.Ok)
                test = 1

            # if EC.data_is_empty(str(self.lineEdit_area.text())) == 0:
                # QMessageBox.warning(self, "ACHTUNG", "Feld Areal. \n Das Feld darf nicht leer sein", QMessageBox.Ok)
                # test = 1

            # if EC.data_is_empty(str(self.lineEdit_us.text())) == 0:
                # QMessageBox.warning(self, "ACHTUNG", "Feld SE. \n Das Feld darf nicht leer sein", QMessageBox.Ok)
                # test = 1
                
            if EC.data_is_empty(str(self.lineEdit_individuo.text())) == 0:
                QMessageBox.warning(self, "ACHTUNG", "Feld nr individuel. \n Das Feld darf nicht leer sein",
                                    QMessageBox.Ok)
                test = 1    
                
            # area = self.lineEdit_area.text()
            # us = self.lineEdit_us.text()
            nr_individuo = self.lineEdit_individuo.text()
            
            # if area != "":
                # if EC.data_is_int(area) == 0:
                    # QMessageBox.warning(self, "ACHTUNG", "Feld Areal. \n Der Wert muss numerisch eingegeben werden",
                                        # QMessageBox.Ok)
                    # test = 1

            # if us != "":
                # if EC.data_is_int(us) == 0:
                    # QMessageBox.warning(self, "ACHTUNG", "Feld SE. \n Der Wert muss numerisch eingegeben werden",
                                        # QMessageBox.Ok)
                    # test = 1
            if nr_individuo != "":
                if EC.data_is_int(nr_individuo) == 0:
                    QMessageBox.warning(self, "ACHTUNG", "Feld Individuel nr. \n Der Wert muss numerisch eingegeben werden",
                                        QMessageBox.Ok)
                    test = 1

           
        
        else:  
            if EC.data_is_empty(str(self.comboBox_sito.currentText())) == 0:
                QMessageBox.warning(self, "WARNING", "Site Field. \n The field must not be empty", QMessageBox.Ok)
                test = 1

            # if EC.data_is_empty(str(self.lineEdit_area.text())) == 0:
                # QMessageBox.warning(self, "WARNING", "Area Field. \n The field must not be empty", QMessageBox.Ok)
                # test = 1

            # if EC.data_is_empty(str(self.lineEdit_us.text())) == 0:
                # QMessageBox.warning(self, "WARNING", "SU Field. \n The field must not be empty", QMessageBox.Ok)
                # test = 1
                
            if EC.data_is_empty(str(self.lineEdit_individuo.text())) == 0:
                QMessageBox.warning(self, "WARNING", "Individual nr. Field. \n The field must not be empty",
                                    QMessageBox.Ok)
                test = 1    
                
            # area = self.lineEdit_area.text()
            # us = self.lineEdit_us.text()
            nr_individuo = self.lineEdit_individuo.text()
            eta_min = self.comboBox_eta_min.currentText()
            eta_max = self.comboBox_eta_max.currentText()   
            
            # if area != "":
                # if EC.data_is_int(area) == 0:
                    # QMessageBox.warning(self, "WARNING", "Area Field. \n The value must be numerical",
                                        # QMessageBox.Ok)
                    # test = 1

            # if us != "":
                # if EC.data_is_int(us) == 0:
                    # QMessageBox.warning(self, "WARNING", "SU Field. \n The value must be numerical",
                                        # QMessageBox.Ok)
                    # test = 1
            if nr_individuo != "":
                if EC.data_is_int(nr_individuo) == 0:
                    QMessageBox.warning(self, "WARNING", "Individual nr. Field. \n The value must be numerical",
                                        QMessageBox.Ok)
                    test = 1

            
        return test

    def insert_new_rec(self):
       
        
        
        if self.lineEdit_lunghezza_scheletro.text() == "":
            lunghezza_scheletro = None
        else:
            lunghezza_scheletro = float(self.lineEdit_lunghezza_scheletro.text())
        
        # if self.lineEdit_orientamento_azimut.text() == "":
            # orientamento_azimut = None
        # else:
            # orientamento_azimut = float(self.lineEdit_orientamento_azimut.text())
        
        try:
            data = self.DB_MANAGER.insert_values_ind(
                self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, self.ID_TABLE) + 1,
                str(self.comboBox_sito.currentText()),  # 1 - Sito
                str(self.comboBox_area.currentText()),  # 2 - area
                str(self.comboBox_us.currentText()),
                int(self.lineEdit_individuo.text()),
                str(self.lineEdit_data_schedatura.text()),  # 5 - data schedatura
                str(self.lineEdit_schedatore.text()),  # 6 - schedatore
                str(self.comboBox_sesso.currentText()),  # 7 - sesso
                str(self.comboBox_eta_min.currentText()),  # 8 - eta' min
                str(self.comboBox_eta_max.currentText()),
                str(self.comboBox_classi_eta.currentText()), # 10 - classi eta
                str(self.textEdit_osservazioni.toPlainText()),  # 11 - osservazioni
                str(self.comboBox_sigla_struttura.currentText()),
                str(self.comboBox_nr_struttura.currentText()),
                str(self.comboBox_completo.currentText()),
                str(self.comboBox_disturbato.currentText()),
                str(self.comboBox_in_connessione.currentText()),
                lunghezza_scheletro,
                str(self.comboBox_posizione_scheletro.currentText()),
                str(self.comboBox_posizione_cranio.currentText()),
                str(self.comboBox_arti_superiori.currentText()),
                str(self.comboBox_arti_inferiori.currentText()),
                str(self.comboBox_orientamento_asse.currentText()),
                str(self.lineEdit_orientamento_azimut.text())
            )
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

    # def on_pushButton_insert_row_rapporti_pressed(self):
        # self.insert_new_row('self.tableWidget_rapporti')

    # def on_pushButton_insert_row_inclusi_pressed(self):
        # self.insert_new_row('self.tableWidget_inclusi')

    # def on_pushButton_insert_row_campioni_pressed(self):
        # self.insert_new_row('self.tableWidget_campioni')

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
            except :
                pass

    def on_pushButton_last_rec_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            try:
                self.empty_fields()
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), len(self.DATA_LIST) - 1
                self.fill_fields(self.REC_CORR)
                self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
            except :
                pass

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
                except:
                    pass

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
                except:
                    pass

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
                    QMessageBox.warning(self, "Message!!!", "Errortyp: " + str(e))
                if not bool(self.DATA_LIST):
                    QMessageBox.warning(self, "Warning", "Die Datenbank ist leer!", QMessageBox.Ok)
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
                QMessageBox.warning(self, "Messagio!!!", "Action deleted!")
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
        
        if self.BROWSE_STATUS != "f" and self.check_record_state() == 1:
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
                    self.setComboBoxEnable(["self.comboBox_sito"], "False")
                    
                    # self.setComboBoxEnable(["self.comboBox_us"], "True")
                    self.setComboBoxEnable(["self.lineEdit_individuo"], "True")
                    #self.setComboBoxEnable(["self.textEdit_osservazioni"], "False")

                    ###
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.set_rec_counter('', '')
                    self.label_sort.setText(self.SORTED_ITEMS["n"])
                    #self.charge_list()
                    self.empty_fields_nosite()
                else:
                    self.BROWSE_STATUS = "f"
                    self.setComboBoxEditable(["self.comboBox_sito"], 0)
                    
                    self.setComboBoxEnable(["self.lineEdit_individuo"], "True")
                   
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
            

            if self.lineEdit_individuo.text() != "":
                individuo = int(self.lineEdit_individuo.text())
            else:
                individuo = ""

                        
            if self.lineEdit_lunghezza_scheletro.text() != "":
                lunghezza_scheletro = float(self.lineEdit_lunghezza_scheletro.text())
                
            else:
                lunghezza_scheletro = None
           
            search_dict = {
                self.TABLE_FIELDS[0]: "'" + str(self.comboBox_sito.currentText()) + "'",  # 1 - Sito
                self.TABLE_FIELDS[1]: "'" + str(self.comboBox_area.currentText()) + "'",  # 2 - Area
                self.TABLE_FIELDS[2]: "'" + str(self.comboBox_us.currentText()) + "'",  # 3 - US
                self.TABLE_FIELDS[3]: individuo,  # 4 - individuo
                self.TABLE_FIELDS[4]: "'" + str(self.lineEdit_data_schedatura.text()) + "'",  # 5 - data schedatura
                self.TABLE_FIELDS[5]: "'" + str(self.lineEdit_schedatore.text()) + "'",  # 6 - schedatore
                self.TABLE_FIELDS[6]: "'" + str(self.comboBox_sesso.currentText()) + "'",  # 7 - sesso
                self.TABLE_FIELDS[7]: "'" + str(self.comboBox_eta_min.currentText()) + "'",  # 8 - eta min
                self.TABLE_FIELDS[8]: "'" + str(self.comboBox_eta_max.currentText()) + "'",
                self.TABLE_FIELDS[9]: "'" + str(self.comboBox_classi_eta.currentText()) + "'",  # 10 - classi eta
                self.TABLE_FIELDS[10]: "'" +str(self.textEdit_osservazioni.toPlainText())+ "'",  # 11 - osservazioni
                self.TABLE_FIELDS[11]: "'" + str(self.comboBox_sigla_struttura.currentText()) + "'",  # 1 - Sito
                self.TABLE_FIELDS[12]: "'" + str(self.comboBox_nr_struttura.currentText()) + "'",  # 1 - Sito
                self.TABLE_FIELDS[13]: "'" + str(self.comboBox_completo.currentText()) + "'",  # 1 - Sito
                self.TABLE_FIELDS[14]: "'" + str(self.comboBox_disturbato.currentText()) + "'",  # 1 - Sito
                self.TABLE_FIELDS[15]: "'" + str(self.comboBox_in_connessione.currentText()) + "'",  # 1 - Sito
                self.TABLE_FIELDS[16]: lunghezza_scheletro,  # 1 - Sito
                self.TABLE_FIELDS[17]: "'" + str(self.comboBox_posizione_scheletro.currentText()) + "'",  # 1 - Sito
                self.TABLE_FIELDS[18]: "'" + str(self.comboBox_posizione_cranio.currentText()) + "'",  # 1 - Sito
                self.TABLE_FIELDS[19]: "'" + str(self.comboBox_arti_superiori.currentText()) + "'",  # 1 - Sito
                self.TABLE_FIELDS[20]: "'" + str(self.comboBox_arti_inferiori.currentText()) + "'",  # 1 - Sito
                self.TABLE_FIELDS[21]: "'" + str(self.comboBox_orientamento_asse.currentText()) + "'",  # 1 - Sito
                self.TABLE_FIELDS[22]: "'" + str(self.lineEdit_orientamento_azimut.text()) + "'"}

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
                        QMessageBox.warning(self, "ATTENZIONE", "Non e' stato trovato alcun record!", QMessageBox.Ok)
                    elif self.L=='de':
                        QMessageBox.warning(self, "ACHTUNG", "kein Eintrag gefunden!", QMessageBox.Ok)
                    else:
                        QMessageBox.warning(self, "Warning", "The record has not been found ", QMessageBox.Ok)

                        self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                        self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                        
                        self.BROWSE_STATUS = "b"
                        self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])

                        self.setComboBoxEnable(["self.comboBox_sito"], "False")
                        self.setComboBoxEditable(["self.comboBox_sigla_struttura"], 0)
                        self.setComboBoxEditable(["self.comboBox_nr_struttura"], 0)
                        self.setComboBoxEditable(["self.comboBox_area"], 0)
                        self.setComboBoxEditable(["self.comboBox_us"], 0)
                        self.setComboBoxEnable(["self.lineEdit_individuo"], "True")
                        self.setComboBoxEnable(["self.textEdit_osservazioni"], "True")
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
                            if self.toolButtonGis.isChecked():
                                id_us_list = self.charge_id_us_for_individuo()
                                self.pyQGIS.charge_individui_us(id_us_list)
                                self.pyQGIS.charge_individui_from_research(self.DATA_LIST)

                        else:
                            strings = ("Sono stati trovati", self.REC_TOT, "records")
                            if self.toolButtonGis.isChecked():
                                id_us_list = self.charge_id_us_for_individuo()
                                self.pyQGIS.charge_individui_us(id_us_list)
                                self.pyQGIS.charge_individui_from_research(self.DATA_LIST)
                    
                    elif self.L=='de':
                        if self.REC_TOT == 1:
                            strings = ("Es wurde gefunden", self.REC_TOT, "record")
                            if self.toolButtonGis.isChecked():
                                id_us_list = self.charge_id_us_for_individuo()
                                self.pyQGIS.charge_individui_us(id_us_list)
                                self.pyQGIS.charge_individui_from_research(self.DATA_LIST)

                        else:
                            strings = ("Sie wurden gefunden", self.REC_TOT, "records")
                            if self.toolButtonGis.isChecked():
                                id_us_list = self.charge_id_us_for_individuo()
                                self.pyQGIS.charge_individui_us(id_us_list)
                                self.pyQGIS.charge_individui_from_research(self.DATA_LIST)
                                
                    else:
                        if self.REC_TOT == 1:
                            strings = ("It has been found", self.REC_TOT, "record")
                            if self.toolButtonGis.isChecked():
                                id_us_list = self.charge_id_us_for_individuo()
                                self.pyQGIS.charge_individui_us(id_us_list)
                                self.pyQGIS.charge_individui_from_research(self.DATA_LIST)

                        else:
                            strings = ("They have been found", self.REC_TOT, "records")
                            if self.toolButtonGis.isChecked():
                                id_us_list = self.charge_id_us_for_individuo()
                                self.pyQGIS.charge_individui_us(id_us_list)
                                self.pyQGIS.charge_individui_from_research(self.DATA_LIST)          
                    self.setComboBoxEnable(["self.comboBox_sito"], "False")
                    
                    self.setComboBoxEnable(["self.lineEdit_individuo"], "False")
                    self.setComboBoxEnable(["self.textEdit_osservazioni"], "True")
                    QMessageBox.warning(self, "Message", "%s %d %s" % strings, QMessageBox.Ok)

        self.enable_button_search(1)

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
                if value != None:
                    sub_list.append(str(value.text()))

            if bool(sub_list):
                lista.append(sub_list)

        return lista

    def tableInsertData(self, t, d):
        pass
        """
        self.table_name = t
        self.data_list = eval(d)
        self.data_list.sort()

        #column table count
        table_col_count_cmd = ("%s.columnCount()") % (self.table_name)
        table_col_count = eval(table_col_count_cmd)

        #clear table
        table_clear_cmd = ("%s.clearContents()") % (self.table_name)
        eval(table_clear_cmd)

        for i in range(table_col_count):
            table_rem_row_cmd = ("%s.removeRow(%d)") % (self.table_name, i)
            eval(table_rem_row_cmd)

        #for i in range(len(self.data_list)):
            #self.insert_new_row(self.table_name)

        for row in range(len(self.data_list)):
            cmd = ('%s.insertRow(%s)') % (self.table_name, row)
            eval(cmd)
            for col in range(len(self.data_list[row])):
                #item = self.comboBox_sito.setEditText(self.data_list[0][col]
                item = QTableWidgetItem(self.data_list[row][col])
                exec_str = ('%s.setItem(%d,%d,item)') % (self.table_name,row,col)
                eval(exec_str)
        """

    def insert_new_row(self, table_name):
        """insert new row into a table based on table_name"""
        cmd = table_name + ".insertRow(0)"
        eval(cmd)

    def empty_fields_nosite(self):
        
        self.comboBox_area.setEditText("")  # 2 - area
        self.comboBox_us.setEditText("")  # 3 - US
        self.lineEdit_data_schedatura.clear()  # 4 - data schedatura
        self.lineEdit_schedatore.clear()  # 5 - schedatore
        self.lineEdit_individuo.clear()  # 6 - individuo
        self.comboBox_sesso.setEditText("")  # 7 - sesso
        self.comboBox_eta_min.setEditText("")  # 8 - eta' minima
        self.comboBox_eta_max.setEditText("")  # 9 - eta' massima
        self.comboBox_classi_eta.setEditText("")  # 10 - classi di eta'
        self.textEdit_osservazioni.clear()  # 11 - osservazioni
        self.comboBox_sigla_struttura.setEditText("")  # 2 - area
        self.comboBox_nr_struttura.setEditText("")  # 2 - area
        self.comboBox_completo.setEditText("")  # 2 - area
        self.comboBox_disturbato.setEditText("")  # 2 - area
        self.comboBox_in_connessione.setEditText("")  # 2 - area
        self.lineEdit_lunghezza_scheletro.clear()  # 2 - area
        self.comboBox_posizione_scheletro.setEditText("")  # 2 - area
        self.comboBox_posizione_cranio.setEditText("")  # 2 - area
        self.comboBox_arti_superiori.setEditText("")  # 2 - area
        self.comboBox_arti_inferiori.setEditText("")  # 2 - area
        self.comboBox_orientamento_asse.setEditText("")  # 2 - area
        self.lineEdit_orientamento_azimut.clear()  # 2 - area
        
        
    
    def empty_fields(self):
       
        self.comboBox_sito.setEditText("")  # 1 - Sito
        self.comboBox_area.setEditText("")  # 2 - area
        self.comboBox_us.setEditText("")  # 3 - US
        self.lineEdit_data_schedatura.clear()  # 4 - data schedatura
        self.lineEdit_schedatore.clear()  # 5 - schedatore
        self.lineEdit_individuo.clear()  # 6 - individuo
        self.comboBox_sesso.setEditText("")  # 7 - sesso
        self.comboBox_eta_min.setEditText("")  # 8 - eta' minima
        self.comboBox_eta_max.setEditText("")  # 9 - eta' massima
        self.comboBox_classi_eta.setEditText("")  # 10 - classi di eta'
        self.textEdit_osservazioni.clear()  # 11 - osservazioni
        self.comboBox_sigla_struttura.setEditText("")  # 2 - area
        self.comboBox_nr_struttura.setEditText("")  # 2 - area
        self.comboBox_completo.setEditText("")  # 2 - area
        self.comboBox_disturbato.setEditText("")  # 2 - area
        self.comboBox_in_connessione.setEditText("")  # 2 - area
        self.lineEdit_lunghezza_scheletro.clear()  # 2 - area
        self.comboBox_posizione_scheletro.setEditText("")  # 2 - area
        self.comboBox_posizione_cranio.setEditText("")  # 2 - area
        self.comboBox_arti_superiori.setEditText("")  # 2 - area
        self.comboBox_arti_inferiori.setEditText("")  # 2 - area
        self.comboBox_orientamento_asse.setEditText("")  # 2 - area
        self.lineEdit_orientamento_azimut.clear()  # 2 - area
        

    def fill_fields(self, n=0):
        self.rec_num = n
        try:
            self.comboBox_sito.setEditText(str(self.DATA_LIST[self.rec_num].sito))  # 1 - Sito
            self.comboBox_area.setEditText(str(self.DATA_LIST[self.rec_num].area))  # 2 - area
            
            self.comboBox_us.setEditText(str(self.DATA_LIST[self.rec_num].us))
            
            self.lineEdit_individuo.setText(str(self.DATA_LIST[self.rec_num].nr_individuo))  # 4 - nr individuo
            self.lineEdit_data_schedatura.setText(str(self.DATA_LIST[self.rec_num].data_schedatura))  # 5 - data schedatura
            self.lineEdit_schedatore.setText(str(self.DATA_LIST[self.rec_num].schedatore))  # 6 - schedatore
            self.comboBox_sesso.setEditText(str(self.DATA_LIST[self.rec_num].sesso))  # 7 - sesso

            
            self.comboBox_eta_min.setEditText(str(self.DATA_LIST[self.rec_num].eta_min))

            
            
            self.comboBox_eta_max.setEditText(str(self.DATA_LIST[self.rec_num].eta_max))

            self.comboBox_classi_eta.setEditText(str(self.DATA_LIST[self.rec_num].classi_eta))  # 10 - classi di eta

            str(self.textEdit_osservazioni.setText(self.DATA_LIST[self.rec_num].osservazioni))
            
            self.comboBox_sigla_struttura.setEditText(str(self.DATA_LIST[self.rec_num].sigla_struttura))  # 1 - Sito
            
            
            
            self.comboBox_nr_struttura.setEditText(str(self.DATA_LIST[self.rec_num].nr_struttura))
            
            self.comboBox_completo.setEditText(str(self.DATA_LIST[self.rec_num].completo_si_no))  # 1 - Sito
            self.comboBox_disturbato.setEditText(str(self.DATA_LIST[self.rec_num].disturbato_si_no))  # 1 - Sito
            self.comboBox_in_connessione.setEditText(str(self.DATA_LIST[self.rec_num].in_connessione_si_no))  # 1 - Sito
            
            if not self.DATA_LIST[self.rec_num].lunghezza_scheletro:
                str(self.lineEdit_lunghezza_scheletro.setText(""))
            else:
                self.lineEdit_lunghezza_scheletro.setText(str(self.DATA_LIST[self.rec_num].lunghezza_scheletro))  # 1 - Sito
            self.comboBox_posizione_scheletro.setEditText(str(self.DATA_LIST[self.rec_num].posizione_scheletro))  # 1 - Sito
            self.comboBox_posizione_cranio.setEditText(str(self.DATA_LIST[self.rec_num].posizione_cranio))  # 1 - Sito
            self.comboBox_arti_superiori.setEditText(str(self.DATA_LIST[self.rec_num].posizione_arti_superiori))  # 1 - Sito
            self.comboBox_arti_inferiori.setEditText(str(self.DATA_LIST[self.rec_num].posizione_arti_inferiori))  # 1 - Sito
            self.comboBox_orientamento_asse.setEditText(str(self.DATA_LIST[self.rec_num].orientamento_asse))  # 1 - Sito
            
            
            self.lineEdit_orientamento_azimut.setText(str(self.DATA_LIST[self.rec_num].orientamento_azimut))  # 1 - Sito
            
            
        except Exception as e :
            QMessageBox.warning(self, "Error", str(e), QMessageBox.Ok)

    def set_rec_counter(self, t, c):
        self.rec_tot = t
        self.rec_corr = c
        self.label_rec_tot.setText(str(self.rec_tot))
        self.label_rec_corrente.setText(str(self.rec_corr))

    def set_LIST_REC_TEMP(self):
        
        if self.lineEdit_lunghezza_scheletro.text() == "":
            lunghezza_scheletro = None
        else:
            lunghezza_scheletro = self.lineEdit_lunghezza_scheletro.text()
        
        # if self.lineEdit_orientamento_azimut.text() == "":
            # orientamento_azimut = None
        # else:
            # orientamento_azimut = self.lineEdit_orientamento_azimut.text()
            # data
        self.DATA_LIST_REC_TEMP = [
            str(self.comboBox_sito.currentText()),  # 1 - Sito
            str(self.comboBox_area.currentText()),  # 2 - Area
            str(self.comboBox_us.currentText()),  # 3 - US
            str(self.lineEdit_individuo.text()),  # 4 - individuo
            str(self.lineEdit_data_schedatura.text()),  # 5 - data schedatura
            str(self.lineEdit_schedatore.text()),  # 6 - schedatore
            str(self.comboBox_sesso.currentText()),  # 7 - sesso
            str(self.comboBox_eta_min.currentText()),  # 8- eta minima
            str(self.comboBox_eta_max.currentText()),  # 8- eta minima  # 9 - eta massima
            str(self.comboBox_classi_eta.currentText()),  # 10 - classi eta
            str(self.textEdit_osservazioni.toPlainText()),
            str(self.comboBox_sigla_struttura.currentText()),
            str(self.comboBox_nr_struttura.currentText()),  # 8- eta minima
            str(self.comboBox_completo.currentText()),
            str(self.comboBox_disturbato.currentText()),
            str(self.comboBox_in_connessione.currentText()),
            str(lunghezza_scheletro),
            str(self.comboBox_posizione_scheletro.currentText()),
            str(self.comboBox_posizione_cranio.currentText()),
            str(self.comboBox_arti_superiori.currentText()),
            str(self.comboBox_arti_inferiori.currentText()),
            str(self.comboBox_orientamento_asse.currentText()),
            str(self.lineEdit_orientamento_azimut.text())]  # 11 - osservazioni

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

    def rec_toupdate(self):
        rec_to_update = self.UTILITY.pos_none_in_list(self.DATA_LIST_REC_TEMP)

        # f = open('/test_rec_to_update_ind.txt', 'w')
        # f.write(str(rec_to_update))
        # f.close()

        return rec_to_update

    def charge_id_us_for_individuo(self):
        data_list_us = []
        for rec in range(len(self.DATA_LIST)):
            sito = "'" + str(self.DATA_LIST[rec].sito) + "'"
            area = "'" + str(self.DATA_LIST[rec].area) + "'"
            us = int(self.DATA_LIST[rec].us)

            serch_dict_us = {'sito': sito, 'area': area, 'us': us}
            us_ind = self.DB_MANAGER.query_bool(serch_dict_us, "SCHEDAIND")
            data_list_us.append(us_ind)

        data_list_id_us = []
        for us in range(len(data_list_us)):
            data_list_id_us.append(data_list_us[us][0].id_scheda_ind)

        return data_list_id_us

    def testing(self, name_file, message):
        f = open(str(name_file), 'w')
        f.write(str(message))
        f.close()
    def on_pushButton_print_pressed(self):
        if self.L=='it':
            if self.checkBox_s_us.isChecked():
                US_pdf_sheet = generate_pdf()
                data_list = self.generate_list_pdf()
                US_pdf_sheet.build_Individui_sheets(data_list)
                QMessageBox.warning(self, 'Ok',"Esportazione terminata Schede Individui",QMessageBox.Ok)
            else:   
                pass
            if self.checkBox_e_us.isChecked() :
                US_index_pdf = generate_pdf()
                data_list = self.generate_list_pdf()
                try:               
                    if bool(data_list):
                        US_index_pdf.build_index_individui(data_list, data_list[0][0])
                        QMessageBox.warning(self, 'Ok',"Esportazione terminata Elenco Individui",QMessageBox.Ok)
                    else:
                        QMessageBox.warning(self, 'ATTENZIONE',"L'elenco Individui non può essere esportato devi riempire prima le schede Individui",QMessageBox.Ok)
                except Exception as e :
                    QMessageBox.warning(self, 'ATTENZIONE',str(e),QMessageBox.Ok)
            else:
                pass
            if self.checkBox_e_foto_t.isChecked():
                US_index_pdf = generate_US_pdf()
                data_list_foto = self.generate_list_foto()
                try:
                        if bool(data_list_foto):
                            US_index_pdf.build_index_Foto(data_list_foto, data_list_foto[0][0])
                            QMessageBox.warning(self, 'Ok',"Esportazione terminata Elenco Foto",QMessageBox.Ok)
                        else:
                            QMessageBox.warning(self, 'ATTENZIONE',"L'elenco foto non può essere esportato perchè non hai immagini taggate.",QMessageBox.Ok)
                except Exception as e :
                    QMessageBox.warning(self, 'ATTENZIONE',str(e),QMessageBox.Ok)
            if self.checkBox_e_foto.isChecked():
                US_index_pdf = generate_US_pdf()
                data_list_foto = self.generate_list_foto()
                try:
                        if bool(data_list_foto):
                            US_index_pdf.build_index_Foto_2(data_list_foto, data_list_foto[0][0])
                            QMessageBox.warning(self, 'Ok',"Esportazione terminata Elenco Foto senza thumbanil",QMessageBox.Ok)
                        else:
                            QMessageBox.warning(self, 'ATTENZIONE',"L'elenco foto non può essere esportato perchè non hai immagini taggate.",QMessageBox.Ok)
                except Exception as e :
                    QMessageBox.warning(self, 'ATTENZIONE',str(e),QMessageBox.Ok)
        elif self.L=='en':  
            if self.checkBox_s_us.isChecked():
                US_pdf_sheet = generate_US_pdf()
                data_list = self.generate_list_pdf()
                US_pdf_sheet.build_US_sheets(data_list)
                QMessageBox.warning(self, 'Ok',"Export finished SU Forms",QMessageBox.Ok)
            else:   
                pass
            if self.checkBox_e_us.isChecked() :
                US_index_pdf = generate_US_pdf()
                data_list = self.generate_list_pdf()
                try:               
                    if bool(data_list):
                        US_index_pdf.build_index_US(data_list, data_list[0][0])
                        QMessageBox.warning(self, 'Ok',"Export finished SU List",QMessageBox.Ok)
                    else:
                        QMessageBox.warning(self, 'WARNING',"The SU list cannot be exported you have to fill in the SU tabs first",QMessageBox.Ok)
                except Exception as e :
                    QMessageBox.warning(self, 'WARNING',str(e),QMessageBox.Ok)
            else:
                pass
            if self.checkBox_e_foto_t.isChecked():
                US_index_pdf = generate_US_pdf()
                data_list_foto = self.generate_list_foto()
                try:
                        if bool(data_list_foto):
                            US_index_pdf.build_index_Foto(data_list_foto, data_list_foto[0][0])
                            QMessageBox.warning(self, 'Ok',"Export finished SU List",QMessageBox.Ok)
                        else:
                            QMessageBox.warning(self, 'WARNING', 'The photo list cannot be exported because you do not have tagged images.',QMessageBox.Ok)
                except Exception as e :
                    QMessageBox.warning(self, 'WARNING',str(e),QMessageBox.Ok)
            if self.checkBox_e_foto.isChecked():
                US_index_pdf = generate_US_pdf()
                data_list_foto = self.generate_list_foto()
                try:
                        if bool(data_list_foto):
                            US_index_pdf.build_index_Foto_2(data_list_foto, data_list_foto[0][0])
                            QMessageBox.warning(self, 'Ok', "Export finished Photo List without thumbanil",QMessageBox.Ok)
                        else:
                            QMessageBox.warning(self, 'WARNING', "The photo list cannot be exported because you do not have tagged images.",QMessageBox.Ok)
                except Exception as e :
                    QMessageBox.warning(self, 'WARNING',str(e),QMessageBox.Ok)
        elif self.L=='de':
            if self.checkBox_s_us.isChecked():
                US_pdf_sheet = generate_US_pdf()
                data_list = self.generate_list_pdf()
                US_pdf_sheet.build_US_sheets(data_list)
                QMessageBox.warning(self, "Okay", "Export beendet",QMessageBox.Ok)
            else:   
                pass
            if self.checkBox_e_us.isChecked() :
                US_index_pdf = generate_US_pdf()
                data_list = self.generate_list_pdf()
                try:               
                    if bool(data_list):
                        US_index_pdf.build_index_US(data_list, data_list[0][0])
                        QMessageBox.warning(self, "Okay", "Export beendet",QMessageBox.Ok)
                    else:
                        QMessageBox.warning(self, 'WARNUNG', 'Die Liste kann nicht exportiert werden, Sie müssen zuerst die Formulare ausfüllen',QMessageBox.Ok)
                except Exception as e :
                    QMessageBox.warning(self, 'WARNUNG',str(e),QMessageBox.Ok)
            else:
                pass
            if self.checkBox_e_foto_t.isChecked():
                US_index_pdf = generate_US_pdf()
                data_list_foto = self.generate_list_foto()
                try:
                        if bool(data_list_foto):
                            US_index_pdf.build_index_Foto(data_list_foto, data_list_foto[0][0])
                            QMessageBox.warning(self, "Okay", "Fertige Fotoliste exportieren",QMessageBox.Ok)
                        else:
                            QMessageBox.warning(self, 'WARNUNG', 'Die Fotoliste kann nicht exportiert werden, da Sie keine markierten Bilder haben.',QMessageBox.Ok)
                except Exception as e :
                    QMessageBox.warning(self, 'WARNUNG',str(e),QMessageBox.Ok)
            if self.checkBox_e_foto.isChecked():
                US_index_pdf = generate_US_pdf()
                data_list_foto = self.generate_list_foto()
                try:
                        if bool(data_list_foto):
                            US_index_pdf.build_index_Foto_2(data_list_foto, data_list_foto[0][0])
                            QMessageBox.warning(self, 'Ok', 'Fertige Fotoliste ohne Daumenballen exportieren',QMessageBox.Ok)
                        else:
                            QMessageBox.warning(self, 'WARNUNG', 'Die Fotoliste kann nicht exportiert werden, da Sie keine markierten Bilder haben.',QMessageBox.Ok)
                except Exception as e :
                    QMessageBox.warning(self, 'WARNUNG',str(e),QMessageBox.Ok)
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
            QMessageBox.information(self, "INFO", "Conversione terminata",
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

## Class end
