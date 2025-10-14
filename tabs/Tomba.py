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
import functools
import platform
import math
import subprocess
from datetime import date
import cv2
from builtins import range
from collections import OrderedDict
from builtins import str
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.uic import loadUiType
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtCore import QTimer
from qgis.PyQt.QtGui import QColor, QIcon
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.uic import loadUiType
from qgis.core import Qgis, QgsSettings,QgsGeometry
from qgis.gui import QgsMapCanvas, QgsMapToolPan
from ..modules.utility.delegateComboBox import ComboBoxDelegate
from ..modules.utility.pyarchinit_media_utility import *
from ..modules.db.pyarchinit_conn_strings import Connection
from ..modules.db.concurrency_manager import ConcurrencyManager, RecordLockIndicator
from ..modules.db.pyarchinit_db_manager import get_db_manager
from ..modules.db.pyarchinit_utility import Utility
from ..modules.gis.pyarchinit_pyqgis import Pyarchinit_pyqgis
from ..modules.utility.pyarchinit_error_check import Error_check
from ..modules.utility.pyarchinit_exp_Tombasheet_pdf import generate_tomba_pdf
from ..gui.imageViewer import ImageViewer
from ..gui.sortpanelmain import SortPanelMain
from ..gui.pyarchinitConfigDialog import pyArchInitDialog_Config
MAIN_DIALOG_CLASS, _ = loadUiType(os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'Tomba.ui'))


class pyarchinit_Tomba(QDialog, MAIN_DIALOG_CLASS):
    L=QgsSettings().value("locale/userLocale")[0:2]
    if L=='it':
        MSG_BOX_TITLE = "PyArchInit - Scheda Tomba"
    
    elif L=='de':
        MSG_BOX_TITLE = "PyArchInit - Formular Gravel"
    else:
        MSG_BOX_TITLE = "PyArchInit - Gravel form" 
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
    TABLE_NAME = 'tomba_table'
    MAPPER_TABLE_CLASS = "TOMBA"
    NOME_SCHEDA = "Scheda Tomba"
    ID_TABLE = "id_tomba"
    
    
    if L=='it':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Sito": "sito",
            "Area": "area",
            "Numero scheda": "nr_scheda_taf",
            "Sigla struttura": "sigla_struttura",
            "Nr struttura": "nr_struttura",
            "Nr Individuo": "nr_individuo",
            "Rito": "rito",
            "Descrizione": "descrizione_taf",
            "Interpretazione": "interpretazione_taf",
            "Segnacoli": "segnacoli",
            "Canale libatorio": "canale_libatorio_si_no",
            "Oggetti esterni rinvenuti": "oggetti_rinvenuti_esterno",
            "Stato di conservazione": "stato_di_conservazione",
            "Tipo di copertura": "copertura_tipo",
            "Tipo contenitore resti": "tipo_contenitore_resti",
            "Tipo deposizione": "tipo_deposizione",
            "Tipo sepoltura": "tipo_sepoltura",
            "Presenza del corredo": "corredo_presenza",
            "Tipo di corredo": "corredo_tipo",
            "Descrizione corredo": "corredo_descrizione",
            "Periodo iniziale": "periodo_iniziale",
            "Fase iniziale": "fase_iniziale",
            "Periodo finale": "periodo_finale",
            "Fase finale": "fase_finale",
            "Datazione estesa": "datazione_estesa"
        }

        SORT_ITEMS = [
            ID_TABLE,
            "Sito",
            "Area",
            "Numero scheda",
            "Sigla struttura",
            "Nr struttura",
            "Nr Individuo",
            "Rito",
            "Descrizione",
            "Interpretazione",
            "Segnacoli",
            "Canale libatorio",
            "Oggetti esterni rinvenuti",
            "Stato di conservazione",
            "Tipo di copertura",
            "Tipo contenitore resti",
            "Tipo deposizione",
            "Tipo sepoltura",
            "Presenza del corredo",
            "Tipo di corredo",
            "Descrizione corredo",
            "Periodo iniziale",
            "Fase iniziale",
            "Periodo finale",
            "Fase finale",
            "Datazione estesa"
        ]
    elif L=='de':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Ausgrabungsstätte": "sito",
            "Nr. Feld": "nr_scheda_taf",
            "Strukturcode": "sigla_struttura",
            "Nr struktur": "nr_struttura",
            "Nr Individuel": "nr_individuo",
            "Ritus": "rito",
            "Beschreibung": "descrizione_taf",
            "Deutung": "interpretazione_taf",
            "Markierung": "segnacoli",
            "Kanaal Libatorio": "canale_libatorio_si_no",
            "External Object found": "oggetti_rinvenuti_esterno",
            "Erhaltungszustand": "stato_di_conservazione",
            "Abdeckung": "copertura_tipo",
            "Funeralbehältnisses": "tipo_contenitore_resti",
            "Orientierung Achse": "orientamento_asse",
            "Orientierung Azimut": "orientamento_azimut",
            "Grabbeigabe": "corredo_presenza",
            "Grabbeigabetyp": "corredo_tipo",
            "Beschreibung Grabbeigabe": "corredo_descrizione",
            "Skelettlänge": "lunghezza_scheletro",
            "Skelettposition": "posizione_scheletro",
            "Schädelposition": "posizione_cranio",
            "Position der oberen Gliedmaße": "posizione_arti_superiori",
            "Position der unteren Gliedmaße": "posizione_arti_inferiori",
            "Voll": "completo_si_no",
            "Gestört": "disturbato_si_no",
            "In Verbindung": "in_connessione_si_no",
            "Features": "caratteristiche",
            "Anfangszeitraum": "periodo_iniziale",
            "Anfangsphase": "fase_iniziale",
            "Letzte zeitraum": "periodo_finale",
            "Letzte phase": "fase_finale",
            "Erweiterte Datierung": "datazione_estesa"
        }

        SORT_ITEMS = [
            ID_TABLE,
            "Ausgrabungsstätte",
            "Nr. Feld",
            "Strukturcode",
            "Nr struktur",
            "Nr Individuel",
            "Ritus",
            "Beschreibung",
            "Deutung",
            "Markierung",
            "Kanaal Libatorio",
            "External Object found",
            "Erhaltungszustand",
            "Abdeckung",
            "Funeralbehältnisses",
            "Orientierung Achse",
            "Orientierung Azimut",
            "Grabbeigabe",
            "Grabbeigabetyp",
            "Beschreibung Grabbeigabe",
            "Skelettlänge",
            "Skelettposition",
            "Schädelposition",
            "Position der oberen Gliedmaße",
            "Position der unteren Gliedmaße",
            "Voll",
            "Gestört",
            "In Verbindung",
            "Features",
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
            "Field Nr.": "nr_scheda_taf",
            "Structure code": "sigla_struttura",
            "Structure Nr.": "nr_struttura",
            "Individual Nr.": "nr_individuo",
            "Rite": "rito",
            "Description": "descrizione_taf",
            "Interpretation": "interpretazione_taf",
            "Marker": "segnacoli",
            "Canal libatorio": "canale_libatorio_si_no",
            "External object found": "oggetti_rinvenuti_esterno",
            "Status of preservation": "stato_di_conservazione",
            "Covering type": "copertura_tipo",
            "Container type": "tipo_contenitore_resti",
            "Axes orientation": "orientamento_asse",
            "Azimut orietation": "orientamento_azimut",
            "Trousseau": "corredo_presenza",
            "Trousseau type": "corredo_tipo",
            "Trousseau description ": "corredo_descrizione",
            "Skeleton length": "lunghezza_scheletro",
            "Skeleton position": "posizione_scheletro",
            "Skull position": "posizione_cranio",
            "Upper limb position": "posizione_arti_superiori",
            "Lower limb position": "posizione_arti_inferiori",
            "Complete": "completo_si_no",
            "Hampered": "disturbato_si_no",
            "In connection": "in_connessione_si_no",
            "Charaterisitcs": "caratteristiche",
            "Start period": "periodo_iniziale",
            "Start phase": "fase_iniziale",
            "Final period": "periodo_finale",
            "Final phase": "fase_finale",
            "Litteral datation ": "datazione_estesa"
        }

        SORT_ITEMS = [
            ID_TABLE,
            "Site",
            "Field Nr.",
            "Structure code",
            "Structure Nr.",
            "Individual Nr.",
            "Rite",
            "Description",
            "Interpretation",
            "Marker",
            "Canal libatorio",
            "External object found",
            "Status of preservation",
            "Covering type",
            "Container type",
            "Axes orientation",
            "Azimut orietation",
            "Trousseau",
            "Trousseau type",
            "Trousseau description ",
            "Skeleton length",
            "Skeleton position",
            "Skull position",
            "Upper limb position",
            "Lower limb position",
            "Complete",
            "Hampered",
            "In connection",
            "Charaterisitcs",
            "Start period",
            "Start phase",
            "Final period",
            "Final phase",
            "Litteral datation "
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

    TABLE_FIELDS = [
        'sito',
        'area',
        'nr_scheda_taf',
        'sigla_struttura',
        'nr_struttura',
        'nr_individuo',
        'rito',
        'descrizione_taf',
        'interpretazione_taf',
        'segnacoli',
        'canale_libatorio_si_no',
        'oggetti_rinvenuti_esterno',
        'stato_di_conservazione',
        'copertura_tipo',
        'tipo_contenitore_resti',
        'tipo_deposizione',
        'tipo_sepoltura',
        'corredo_presenza',
        'corredo_tipo',
        'corredo_descrizione',
        'periodo_iniziale',
        'fase_iniziale',
        'periodo_finale',
        'fase_finale',
        'datazione_estesa'
    ]

    HOME = os.environ['PYARCHINIT_HOME']
    REPORT_PATH = '{}{}{}'.format(HOME, os.sep, "pyarchinit_Report_folder")
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
        self.setAcceptDrops(True)
        self.iconListWidget.setDragDropMode(QAbstractItemView.DragDrop)
        # Dizionario per memorizzare le immagini in cache
        self.image_cache = OrderedDict()

        # Numero massimo di elementi nella cache
        self.cache_limit = 100
        try:
            self.on_pushButton_connect_pressed()
        except Exception as e:
            QMessageBox.warning(self, "Connection system", str(e), QMessageBox.Ok)
        sito = self.comboBox_sito.currentText()
        self.comboBox_sito.setEditText(sito)

        self.lineEdit_nr_scheda.setText('')
        self.lineEdit_nr_scheda.textChanged.connect(self.update)
        self.lineEdit_nr_scheda.textChanged.connect(self.charge_struttura_list)
        #self.comboBox_sito.currentTextChanged.connect(self.charge_struttura_list)
        #self.charge_struttura_list
        self.comboBox_sigla_struttura.currentIndexChanged.connect(self.charge_struttura_nr)
        self.comboBox_nr_struttura.currentTextChanged.connect(self.charge_individuo_list)
        #self.charge_individuo_list()
        self.lineEdit_nr_scheda.textChanged.connect(self.charge_oggetti_esterno_list)
        
        # SIGNALS & SLOTS Functions
        
        self.lineEdit_nr_scheda.textChanged.connect(self.charge_periodo_iniz_list)
        self.lineEdit_nr_scheda.textChanged.connect(self.charge_periodo_fin_list)

        self.comboBox_per_iniz.currentIndexChanged.connect(self.charge_periodo_fin_list)
        self.comboBox_per_iniz.currentIndexChanged.connect(self.charge_fase_iniz_list)
        
        self.comboBox_per_fin.currentIndexChanged.connect(self.charge_fase_fin_list)
        #self.comboBox_per_iniz.currentIndexChanged.connect(self.charge_datazione_list)
        self.comboBox_fas_iniz.currentIndexChanged.connect(self.charge_datazione_list)

        self.toolButton_pdfpath.clicked.connect(self.setPathpdf)
        self.pbnOpenpdfDirectory.clicked.connect(self.openpdfDir)
        self.fill_fields()
        self.customize_GUI()
        self.lineEdit_nr_scheda.textChanged.connect(self.loadCorredolist)
        self.set_sito()
        self.msg_sito()
        self.numero_invetario()
        self.update_dating()
    def numero_invetario(self):
        # self.set_sito()
        contatore = 0
        list=[]
        if self.lineEdit_nr_scheda.text()=='':
            self.lineEdit_nr_scheda.clear()
            self.lineEdit_nr_scheda.setText('1')
            self.lineEdit_nr_scheda.update()
            for i in range(len(self.DATA_LIST)):
                self.lineEdit_nr_scheda.clear()
                contatore = int(self.DATA_LIST[i].nr_scheda_taf)
                #contatore.sort(reverse=False)
                list.append(contatore)
                
               
                list[-1]+=1
                
                list.sort()
            for e in list:    
                
                self.lineEdit_nr_scheda.setText(str(e))
    def loadCorredolist(self):
        self.tableWidget_corredo_tipo.clear()
        if self.L=='it':
            col =['ID Reperto','ID Indv.','Materiale','Posizione del corredo','Posizione nel corredo']
        elif self.L=='de':
            col =['Artefakt ID','Indv. ID','Material','Ort in Aussteuer','Ort in Aussteuer']
        else:
             col =['Item ID','Indv. ID','Material','Position in trousseau','Position in trousseau']
        self.tableWidget_corredo_tipo.setHorizontalHeaderLabels(col)
        numRows = self.tableWidget_corredo_tipo.setRowCount(0)
        conn = Connection()
        area= str(self.comboBox_area.currentText())    
        sito_set= conn.sito_set()
        sito_set_str = sito_set['sito_set']
        
        try:
            if bool (sito_set_str):
                search_dict = {
                        'sito': "'"+str(sito_set_str)+"'",
                        'struttura': "'" + str(eval('self.DATA_LIST[int(self.REC_CORR)].sigla_struttura'))+'-'+ str(eval('self.DATA_LIST[int(self.REC_CORR)].nr_struttura'))+"'"
                    }
                u = Utility()
                search_dict = u.remove_empty_items_fr_dict(search_dict)
                search_dict2 = {
                        'sito': "'"+str(sito_set_str)+"'",
                        'sigla_struttura': "'" + str(eval('self.DATA_LIST[int(self.REC_CORR)].sigla_struttura'))+"'",
                        'nr_struttura': "'"+str(eval('self.DATA_LIST[int(self.REC_CORR)].nr_struttura'))+"'"
                    }
                u = Utility()
                search_dict = u.remove_empty_items_fr_dict(search_dict)
                record_inventario_list = self.DB_MANAGER.query_bool(search_dict, 'INVENTARIO_MATERIALI')
                
                nus=0
                reperto=[]
                materiale = []
                individuo=[]
                for i in record_inventario_list:
                    reperto.append(str(i.n_reperto))
                    materiale.append(i.definizione)
                
                
                for b in record_inventario_list:
                     
                    self.delegateRS = ComboBoxDelegate()
                    self.delegateRS.def_values(reperto)
                    self.delegateRS.def_editable('False')
                    self.tableWidget_corredo_tipo.setItemDelegateForColumn(0,self.delegateRS)
                    
                    self.delegateMS = ComboBoxDelegate()
                    self.delegateMS.def_values(materiale)
                    self.delegateMS.def_editable('False')
                    self.tableWidget_corredo_tipo.setItemDelegateForColumn(2,self.delegateMS)
                
                record_individui_list = self.DB_MANAGER.query_bool(search_dict2, 'SCHEDAIND')
                for e in record_individui_list:
                    individuo.append(str(e.nr_individuo))
                for a in record_individui_list:
                    
                    self.delegateIS = ComboBoxDelegate()
                    self.delegateIS.def_values(individuo)
                    self.delegateIS.def_editable('False')
                    self.tableWidget_corredo_tipo.setItemDelegateForColumn(1,self.delegateIS)
        
        
        except:
            pass
        
    
    
    def enable_button(self, n):
        #self.pushButton_connect.setEnabled(n)

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
        #self.pushButton_connect.setEnabled(n)

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
            self.DB_MANAGER = get_db_manager(conn_str, use_singleton=True)

            # Get database username and set it in the concurrency manager
            user_info = conn.datauser()
            db_username = user_info.get('user', 'unknown')
            if hasattr(self, 'concurrency_manager'):
                self.concurrency_manager.set_username(db_username)

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
                    msg = "Warnung. Es wurde ein bug gefunden! Fehler einsenden: ".format(str(e))
                    self.iface.messageBar().pushMessage(self.tr(msg), Qgis.Warning, 0)  
                else:
                    msg = "Warning bug detected! Report it to the developer. Error: ".format(str(e))
                    self.iface.messageBar().pushMessage(self.tr(msg), Qgis.Warning, 0)

    def customize_GUI(self):
        self.tableWidget_corredo_tipo.setColumnWidth(0, 100)
        self.tableWidget_corredo_tipo.setColumnWidth(1, 100)
        self.tableWidget_corredo_tipo.setColumnWidth(2, 100)
        self.tableWidget_corredo_tipo.setColumnWidth(3, 200)
        self.tableWidget_corredo_tipo.setColumnWidth(4, 200)
        
        self.setComboBoxEnable(["self.lineEdit_nr_scheda"], "True")
        self.mapPreview = QgsMapCanvas(self)
        self.mapPreview.setCanvasColor(QColor(225, 225, 225))
        self.tabWidget.addTab(self.mapPreview, "Piante")

        self.iconListWidget.setLineWidth(2)
        self.iconListWidget.setMidLineWidth(2)
        self.iconListWidget.setProperty("showDropIndicator", False)
        self.iconListWidget.setIconSize(QSize(430, 570))

        self.iconListWidget.setUniformItemSizes(True)
        self.iconListWidget.setObjectName("iconListWidget")
        self.iconListWidget.SelectionMode()
        self.iconListWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.iconListWidget.itemDoubleClicked.connect(self.openWide_image)
        # comboBox customizations
        self.setComboBoxEditable(["self.comboBox_sigla_struttura"], 1)
        self.setComboBoxEditable(["self.comboBox_nr_struttura"], 1)
        self.setComboBoxEditable(["self.comboBox_nr_individuo"], 1)
        self.setComboBoxEditable(["self.comboBox_oggetti_esterno"], 1)
        self.setComboBoxEditable(["self.comboBox_per_fin"], 1)
        self.setComboBoxEditable(["self.comboBox_fas_fin"], 1)
        self.setComboBoxEditable(["self.comboBox_per_iniz"], 1)
        self.setComboBoxEditable(["self.comboBox_fas_iniz"], 1)

    def loadMapPreview(self, mode=0):
        if mode == 0:
            """ if has geometry column load to map canvas """
            gidstr = self.ID_TABLE + " = " + str(
                eval("self.DATA_LIST[int(self.REC_CORR)]." + self.ID_TABLE))
            layerToSet = self.pyQGIS.loadMapPreview(gidstr)
            QMessageBox.warning(self, "layer to set", '\n'.join([l.name() for l in layerToSet]), QMessageBox.Ok)
            self.mapPreview.setLayers(layerToSet)
            self.mapPreview.zoomToFullExtent()
        elif mode == 1:
            self.mapPreview.setLayers([])
            self.mapPreview.zoomToFullExtent()
    def dropEvent(self, event):
        mimeData = event.mimeData()
        accepted_formats = ["jpg", "jpeg", "png", "tiff", "tif", "bmp", "mp4", "avi", "mov", "mkv", "flv"]
        if mimeData.hasUrls():
            for url in mimeData.urls():
                try:
                    path = url.toLocalFile()
                    if os.path.isfile(path):
                        filename = os.path.basename(path)
                        filetype = filename.split(".")[-1]
                        if filetype.lower() in accepted_formats:
                            self.load_and_process_image(path)
                        else:
                            QMessageBox.warning(self, "Error", f"Unsupported file type: {filetype}", QMessageBox.Ok)
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Failed to process the file: {str(e)}", QMessageBox.Ok)
        super().dropEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def insert_record_media(self, mediatype, filename, filetype, filepath):
        self.mediatype = mediatype
        self.filename = filename
        self.filetype = filetype
        self.filepath = filepath
        try:
            data = self.DB_MANAGER.insert_media_values(
                self.DB_MANAGER.max_num_id('MEDIA', 'id_media') + 1,
                str(self.mediatype),  # 1 - mediatyype
                str(self.filename),  # 2 - filename
                str(self.filetype),  # 3 - filetype
                str(self.filepath),  # 4 - filepath
                str('Insert description'),  # 5 - descrizione
                str("['imagine']"))  # 6 - tags
            try:
                self.DB_MANAGER.insert_data_session(data)
                return 1
            except Exception as e:
                e_str = str(e)
                if e_str.__contains__("Integrity"):
                    msg = self.filename + ": Image already in the database"
                else:
                    msg = e
                # QMessageBox.warning(self, "Errore", "Warning 1 ! \n"+ str(msg),  QMessageBox.Ok)
                return 0
        except Exception as e:
            QMessageBox.warning(self, "Error", "Warning 2 ! \n" + str(e), QMessageBox.Ok)
            return 0

    def insert_record_mediathumb(self, media_max_num_id, mediatype, filename, filename_thumb, filetype, filepath_thumb,
                                 filepath_resize):
        self.media_max_num_id = media_max_num_id
        self.mediatype = mediatype
        self.filename = filename
        self.filename_thumb = filename_thumb
        self.filetype = filetype
        self.filepath_thumb = filepath_thumb
        self.filepath_resize = filepath_resize
        try:
            data = self.DB_MANAGER.insert_mediathumb_values(
                self.DB_MANAGER.max_num_id('MEDIA_THUMB', 'id_media_thumb') + 1,
                str(self.media_max_num_id),  # 1 - media_max_num_id
                str(self.mediatype),  # 2 - mediatype
                str(self.filename),  # 3 - filename
                str(self.filename_thumb),  # 4 - filename_thumb
                str(self.filetype),  # 5 - filetype
                str(self.filepath_thumb),  # 6 - filepath_thumb
                str(self.filepath_resize))  # 6 - filepath_thumb
            try:
                self.DB_MANAGER.insert_data_session(data)
                return 1
            except Exception as e:
                e_str = str(e)
                if e_str.__contains__("Integrity"):
                    msg = self.filename + ": thumb already present into the database"
                else:
                    msg = e
                # QMessageBox.warning(self, "Error", "warming 1 ! \n"+ str(msg),  QMessageBox.Ok)
                return 0
        except Exception as e:
            QMessageBox.warning(self, "Error", "Warning 2 ! \n" + str(e), QMessageBox.Ok)
            return 0

    def insert_mediaToEntity_rec(self, id_entity, entity_type, table_name, id_media, filepath, media_name):
        """
        id_mediaToEntity,
        id_entity,
        entity_type,
        table_name,
        id_media,
        filepath,
        media_name"""
        self.id_entity = id_entity
        self.entity_type = entity_type
        self.table_name = table_name
        self.id_media = id_media
        self.filepath = filepath
        self.media_name = media_name
        try:
            data = self.DB_MANAGER.insert_media2entity_values(
                self.DB_MANAGER.max_num_id('MEDIATOENTITY', 'id_mediaToEntity') + 1,
                int(self.id_entity),  # 1 - id_entity
                str(self.entity_type),  # 2 - entity_type
                str(self.table_name),  # 3 - table_name
                int(self.id_media),  # 4 - us
                str(self.filepath),  # 5 - filepath
                str(self.media_name))  # 6 - media_name
            try:
                self.DB_MANAGER.insert_data_session(data)
                return 1
            except Exception as e:
                e_str = str(e)
                if e_str.__contains__("Integrity"):
                    msg = self.ID_TABLE + " already present into the database"
                else:
                    msg = e
                QMessageBox.warning(self, "Error", "Warning 1 ! \n" + str(msg), QMessageBox.Ok)
                return 0
        except Exception as e:
            QMessageBox.warning(self, "Error", "Warning 2 ! \n" + str(e), QMessageBox.Ok)
            return 0

    def delete_mediaToEntity_rec(self, id_entity, entity_type, table_name, id_media, filepath, media_name):
        """
        id_mediaToEntity,
        id_entity,
        entity_type,
        table_name,
        id_media,
        filepath,
        media_name"""
        self.id_entity = id_entity
        self.entity_type = entity_type
        self.table_name = table_name
        self.id_media = id_media
        self.filepath = filepath
        self.media_name = media_name
        try:
            data = self.DB_MANAGER.insert_media2entity_values(
                self.DB_MANAGER.max_num_id('MEDIATOENTITY', 'id_mediaToEntity') + 1,
                int(self.id_entity),  # 1 - id_entity
                str(self.entity_type),  # 2 - entity_type
                str(self.table_name),  # 3 - table_name
                int(self.id_media),  # 4 - us
                str(self.filepath),  # 5 - filepath
                str(self.media_name))
        except Exception as e:
            QMessageBox.warning(self, "Error", "Warning 2 ! \n" + str(e), QMessageBox.Ok)
            return 0

    def generate_reperti(self):
        # tags_list = self.table2dict('self.tableWidgetTags_US')
        record_rep_list = []
        sito = self.comboBox_sito.currentText()

        nv = self.lineEdit_nr_scheda.text()
        # for sing_tags in tags_list:
        search_dict = {'sito': "'" + str(sito) + "'",
                       'nr_scheda_taf': "'" + str(nv) + "'"
                       }
        j = self.DB_MANAGER.query_bool(search_dict, 'TOMBA')
        record_rep_list.append(j)
        # QMessageBox.information(self, 'search db', str(record_us_list))
        rep_list = []
        for r in record_rep_list:
            rep_list.append([r[0].id_tomba, 'TOMBA', 'tomba_table'])
        return rep_list

    def assignTags_reperti(self, item):
        """
        id_mediaToEntity,
        id_entity,
        entity_type,
        table_name,
        id_media,
        filepath,
        media_name
        """
        rep_list = self.generate_reperti()
        # QMessageBox.information(self,'search db',str(us_list))
        if not rep_list:
            return

        for rep_data in rep_list:
            id_orig_item = item.text()  # return the name of original file
            search_dict = {'filename': "'" + str(id_orig_item) + "'"}
            media_data = self.DB_MANAGER.query_bool(search_dict, 'MEDIA')
            self.insert_mediaToEntity_rec(rep_data[0], rep_data[1], rep_data[2], media_data[0].id_media,
                                          media_data[0].filepath, media_data[0].filename)

    def load_and_process_image(self, filepath):
        media_resize_suffix = ''
        media_thumb_suffix = ''
        conn = Connection()
        thumb_path = conn.thumb_path()
        thumb_path_str = thumb_path['thumb_path']
        if thumb_path_str=='':
            if self.L=='it':
                QMessageBox.information(self, "Info", "devi settare prima la path per salvare le thumbnail e i video. Vai in impostazioni di sistema/ path setting ")
            elif self.L=='de':
                QMessageBox.information(self, "Info", "müssen Sie zuerst den Pfad zum Speichern der Miniaturansichten und Videos festlegen. Gehen Sie zu System-/Pfad-Einstellung")
            else:
                QMessageBox.information(self, "Message", "you must first set the path to save the thumbnails and videos. Go to system/path setting")
        else:
            filename = os.path.basename(filepath)
            filename, filetype = filename.split(".")[0], filename.split(".")[1]
            # Check the media type based on the file extension
            accepted_image_formats = ["jpg", "jpeg", "png", "tiff", "tif", "btm"]
            accepted_video_formats = ["mp4", "avi", "mov", "mkv", "flv"]
            if filetype.lower() in accepted_image_formats:
                mediatype = 'image'
                media_thumb_suffix = '_thumb.png'
                media_resize_suffix = '.png'

            elif filetype.lower() in accepted_video_formats:
                mediatype = 'video'
                media_thumb_suffix = '_video.png'


            else:
                # Handle unrecognized media type
                raise ValueError(f"Unrecognized media type for file {filename}.{filetype}")

            if mediatype == 'video':
                if filetype.lower() == 'mp4':
                    media_resize_suffix = '.mp4'
                elif filetype.lower() == 'avi':
                    media_resize_suffix = '.avi'
                elif filetype.lower() == 'mov':
                    media_resize_suffix = '.mov'
                elif filetype.lower() == 'mkv':
                    media_resize_suffix = '.mkv'
                elif filetype.lower() == 'flv':
                    media_resize_suffix = '.flv'

            # Check and insert record in the database
            idunique_image_check = self.db_search_check('MEDIA', 'filepath', filepath)

            try:
                if bool(idunique_image_check):

                    return
                else:
                    # mediatype = 'image'
                    self.insert_record_media(mediatype, filename, filetype, filepath)
                    MU = Media_utility()
                    MUR = Media_utility_resize()
                    MU_video = Video_utility()
                    MUR_video = Video_utility_resize()
                    media_max_num_id = self.DB_MANAGER.max_num_id('MEDIA', 'id_media')
                    thumb_path = conn.thumb_path()
                    thumb_path_str = thumb_path['thumb_path']
                    thumb_resize = conn.thumb_resize()
                    thumb_resize_str = thumb_resize['thumb_resize']
                    filenameorig = filename
                    filename_thumb = str(media_max_num_id) + "_" + filename + media_thumb_suffix
                    filename_resize = str(media_max_num_id) + "_" + filename + media_resize_suffix
                    filepath_thumb = filename_thumb
                    filepath_resize = filename_resize
                    self.SORT_ITEMS_CONVERTED = []

                    try:
                        if mediatype == 'video':
                            vcap = cv2.VideoCapture(filepath)
                            res, im_ar = vcap.read()
                            while im_ar.mean() < 1 and res:
                                res, im_ar = vcap.read()
                            im_ar = cv2.resize(im_ar, (100, 100), 0, 0, cv2.INTER_LINEAR)
                            # to save we have two options
                            outputfile = '{}.png'.format(os.path.dirname(filepath) + '/' + filename)
                            cv2.imwrite(outputfile, im_ar)
                            MU_video.resample_images(media_max_num_id, outputfile, filenameorig, thumb_path_str,
                                                     media_thumb_suffix)
                            MUR_video.resample_images(media_max_num_id, filepath, filenameorig, thumb_resize_str,
                                                      media_resize_suffix)
                        else:
                            MU.resample_images(media_max_num_id, filepath, filenameorig, thumb_path_str, media_thumb_suffix)
                            MUR.resample_images(media_max_num_id, filepath, filenameorig, thumb_resize_str,
                                                media_resize_suffix)
                    except Exception as e:
                        QMessageBox.warning(self, "Cucu", str(e), QMessageBox.Ok)
                    self.insert_record_mediathumb(media_max_num_id, mediatype, filename, filename_thumb, filetype,
                                                  filepath_thumb, filepath_resize)

                    item = QListWidgetItem(str(filenameorig))
                    item.setData(Qt.UserRole, str(media_max_num_id))
                    icon = QIcon(str(thumb_path_str) + filepath_thumb)
                    item.setIcon(icon)
                    self.iconListWidget.addItem(item)

                self.assignTags_reperti(item)



            except:
                if self.L == 'it':
                    QMessageBox.warning(self, "Warning", "controlla che il nome del file non abbia caratteri speciali",
                                        QMessageBox.Ok)
                if self.L == 'de':
                    QMessageBox.warning(self, "Warning", "prüfen, ob der Dateiname keine Sonderzeichen enthält",
                                        QMessageBox.Ok)
                else:
                    QMessageBox.warning(self, "Warning", "check that the file name has no special characters",
                                        QMessageBox.Ok)

    def db_search_check(self, table_class, field, value):
        self.table_class = table_class
        self.field = field
        self.value = value
        search_dict = {self.field: "'" + str(self.value) + "'"}
        u = Utility()
        search_dict = u.remove_empty_items_fr_dict(search_dict)
        res = self.DB_MANAGER.query_bool(search_dict, self.table_class)
        return res
    def on_pushButton_removetags_pressed(self):
        def r_id():
            sito = self.comboBox_sito.currentText()
            #area = self.comboBox_area.currentText()
            nv = self.lineEdit_nr_scheda.text()
            record_us_list=[]
            search_dict = {'sito': "'" + str(sito) + "'",

                           'nr_scheda_taf': "'" + str(nv) + "'"
                           }
            j = self.DB_MANAGER.query_bool(search_dict, 'TOMBA')
            record_us_list.append(j)
            # QMessageBox.information(self, 'search db', str(record_us_list))
            us_list = []
            for r in record_us_list:
                a=r[0].id_tomba
            #QMessageBox.information(self,'ok',str(a))# QMessageBox.information(self, "Scheda US", str(us_list), QMessageBox.Ok)
            return a

        items_selected = self.iconListWidget.selectedItems()
        if not bool(items_selected):
            if self.L == 'it':

                msg = QMessageBox.warning(self, "Attenzione!!!",
                                          "devi selezionare prima l'immagine",
                                          QMessageBox.Ok)

            elif self.L == 'de':

                msg = QMessageBox.warning(self, "Warnung",
                                          "moet je eerst de afbeelding selecteren",
                                          QMessageBox.Ok)
            else:

                msg = QMessageBox.warning(self, "Warning",
                                          "you must first select an image",
                                          QMessageBox.Ok)
        else:
            if self.L == 'it':
                msg = QMessageBox.warning(self, "Warning",
                                          "Vuoi veramente cancellare i tags dalle thumbnail selezionate? \n L'azione è irreversibile",
                                          QMessageBox.Ok | QMessageBox.Cancel)
                if msg == QMessageBox.Cancel:
                    QMessageBox.warning(self, "Messaggio!!!", "Azione Annullata!")
                else:
                    # items_selected = self.iconListWidget.selectedItems()
                    for item in items_selected:
                        id_orig_item = item.text()  # return the name of original file

                        # s = self.iconListWidget.item(0, 0).text()
                        self.DB_MANAGER.remove_tags_from_db_sql_scheda(r_id(), id_orig_item)
                        row = self.iconListWidget.row(item)
                        self.iconListWidget.takeItem(row)
                    QMessageBox.warning(self, "Info", "Tags rimossi!")
            elif self.L == 'de':
                msg = QMessageBox.warning(self, "Warning",
                                          "Wollen Sie wirklich die Tags aus den ausgewählten Miniaturbildern löschen? \n Die Aktion ist unumkehrbar",
                                          QMessageBox.Ok | QMessageBox.Cancel)
                if msg == QMessageBox.Cancel:
                    QMessageBox.warning(self, "Warnung", "Azione Annullata!")
                else:
                    # items_selected = self.iconListWidget.selectedItems()
                    for item in items_selected:
                        id_orig_item = item.text()  # return the name of original file

                        # s = self.iconListWidget.item(0, 0).text()
                        self.DB_MANAGER.remove_tags_from_db_sql_scheda(r_id(), id_orig_item)
                        row = self.iconListWidget.row(item)
                        self.iconListWidget.takeItem(row)
                    QMessageBox.warning(self, "Info", "Tags entfernt")

            else:
                msg = QMessageBox.warning(self, "Warning",
                                          "Do you really want to delete the tags from the selected thumbnails? \n The action is irreversible",
                                          QMessageBox.Ok | QMessageBox.Cancel)
                if msg == QMessageBox.Cancel:
                    QMessageBox.warning(self, "Warning", "Action cancelled")
                else:
                    # items_selected = self.iconListWidget.selectedItems()
                    for item in items_selected:
                        id_orig_item = item.text()  # return the name of original file

                        # s = self.iconListWidget.item(0, 0).text()
                        self.DB_MANAGER.remove_tags_from_db_sql_scheda(r_id(), id_orig_item)
                        row = self.iconListWidget.row(item)
                        self.iconListWidget.takeItem(row)  # remove the item from the list

                    QMessageBox.warning(self, "Info", "Tags removed")

    def on_pushButton_all_images_pressed(self):
        record_us_list = self.DB_MANAGER.query('MEDIA_THUMB')

        et = {'entity_type': "'TOMBA'"}
        ser = self.DB_MANAGER.query_bool(et, 'MEDIATOENTITY')
        # Verifica se record_us_list è vuota
        if not record_us_list and not ser:
            QMessageBox.information(self, "Informazione", "Non ci sono immagini da mostrare.")
            return  # Termina la funzione

        # Inizializza la QListWidget fuori dal ciclo
        self.new_list_widget = QListWidget()
        # ##self.new_list_widget.setFixedSize(200, 300)
        self.new_list_widget.setSelectionMode(QAbstractItemView.SingleSelection)  # Permette selezioni multiple

        done_button = QPushButton("TAG")

        def update_done_button():
            if not self.new_list_widget.selectedItems():
                done_button.setHidden(True)
            else:
                done_button.setHidden(False)
                done_button.clicked.connect(self.on_done_selecting_all)

        self.new_list_widget.itemSelectionChanged.connect(
            update_done_button)  # Aggiungi un layout per le etichette dei numeri delle pagine
        self.pageLayout = QHBoxLayout()
        self.current_page_label = QLabel()  # Creiamo l'etichetta per la pagina corrente
        self.total_pages_label = QLabel()  # Creiamo l'etichetta per il totale delle pagine

        self.pageLayout.addWidget(self.current_page_label)  # Aggiungiamo l'etichetta della pagina corrente al layout
        self.pageLayout.addWidget(self.total_pages_label)  # Aggiungiamo l'etichetta del totale delle pagine al layout

        # Aggiungi un pulsante "Indietro"
        self.prevButton = QPushButton("<<")
        self.prevButton.clicked.connect(self.go_to_previous_page)
        self.pageLayout.addWidget(self.prevButton)

        # Aggiungi le etichette dei numeri delle pagine
        self.pageLabels = []
        for i in range(1, 6):
            label = QLabel(str(i))
            label.setAlignment(Qt.AlignCenter)
            label.setMinimumWidth(30)
            label.setFrameStyle(QFrame.Panel | QFrame.Sunken)
            label.setMargin(2)
            label.mousePressEvent = functools.partial(self.on_page_label_clicked, i)
            self.pageLabels.append(label)
            self.pageLayout.addWidget(label)

        # Aggiungi un pulsante "Avanti"
        self.nextButton = QPushButton(">>")
        self.nextButton.clicked.connect(self.go_to_next_page)
        self.pageLayout.addWidget(self.nextButton)

        layout = QVBoxLayout()
        # Crea un campo di input per la ricerca
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Cerca...poi schiaccia invio")
        self.current_filter_text = ""

        self.page_size = 10  # Numero di immagini per pagina
        self.current_page = 1  # Pagina corrente
        self.total_pages = 0  # Numero totale di pagine

        # Aggiungi il campo di ricerca al layout sopra la QListWidget
        layout.insertWidget(0, self.search_field)

        layout.addLayout(self.pageLayout)
        layout.addWidget(self.new_list_widget)
        layout.addWidget(done_button)

        # Imposta il fattore di estensione per i widget nel layout
        # Il primo parametro è l'indice del widget e il secondo parametro è il fattore di estensione
        # In questo caso, new_list_widget ha un indice di 0 e done_button ha un indice di 1
        layout.setStretchFactor(self.new_list_widget, 5)  # new_list_widget avrà 3 volte più spazio di done_button
        layout.setStretchFactor(done_button, 1)  # done_button avrà 1/3 dello spazio di new_list_widget

        # Imposta il layout sulla tua finestra o su un altro widget
        self.setLayout(layout)

        # Crea un nuovo widget per contenere la QListWidget e il pulsante, e applica il layout
        self.widget = QWidget()
        self.widget.setLayout(layout)
        self.widget.adjustSize()
        self.widget.show()

        self.load_images()

        # Connette il campo di ricerca a una funzione di filtraggio
        self.search_field.returnPressed.connect(self.filter_items)

    def load_images(self, filter_text=None):
        conn = Connection()
        thumb_path = conn.thumb_path()
        thumb_path_str = thumb_path['thumb_path']
        u = Utility()

        # Calcola l'offset per la pagina corrente
        # offset = (self.current_page - 1) * self.page_size

        # Ottieni tutti i record delle immagini
        all_images = self.DB_MANAGER.query('MEDIA_THUMB')

        # Ottieni tutte le immagini taggate
        tagged_images = self.DB_MANAGER.query('MEDIATOENTITY')

        # Ottieni gli id_media di tutte le immagini taggate
        tagged_ids = [i.id_media for i in tagged_images]

        # Filtra tutte le immagini per ottenere solo quelle non taggate
        untagged_images = [i for i in all_images if i.id_media not in tagged_ids]

        # Inizializza l'elenco delle immagini 'US' come un duplicato delle immagini non taggate
        us_images = untagged_images[:]

        if len(all_images) > 100:

            if filter_text:  # se il filtro è attivo
                filtered_images = [i for i in untagged_images if filter_text.lower() in i.media_filename.lower()]
            else:
                filtered_images = us_images
            # Calcola gli indici di inizio e fine per la pagina corrente
            start_index = (self.current_page - 1) * self.page_size
            end_index = start_index + self.page_size

            # Ottieni i record delle immagini per la pagina corrente
            self.record_us_list = filtered_images[start_index:end_index]
            # Pulisci la QListWidget prima di aggiungere le nuove immagini
            self.new_list_widget.clear()
            # Aggiungi l'intestazione alla QListWidget
            header_item = QListWidgetItem(
                "Le righe selezionate in giallo indicano immagini non taggate\n Da questo strumento solo le righe selezionate gialle posso essere taggate ")
            header_item.setBackground(QColor('lightgrey'))
            header_item.setFlags(header_item.flags() & ~Qt.ItemIsSelectable)  # rendi l'item non selezionabile
            self.new_list_widget.addItem(header_item)
            # Aggiungi le immagini alla QListWidget

            for i in self.record_us_list:
                search_dict = {'id_media': "'" + str(i.id_media) + "'"}
                u = Utility()
                search_dict = u.remove_empty_items_fr_dict(search_dict)
                mediathumb_data = self.DB_MANAGER.query_bool(search_dict, "MEDIA_THUMB")
                thumb_path = str(mediathumb_data[0].filepath)
                # Verifica se l'immagine è già in cache
                if thumb_path not in self.image_cache:
                    # Se non è in cache, carica l'immagine
                    icon = QIcon(thumb_path_str + thumb_path)

                    # Se la cache ha raggiunto il limite, rimuove l'elemento più vecchio
                    if len(self.image_cache) >= self.cache_limit:
                        self.image_cache.popitem(last=False)

                    # Aggiunge l'immagine alla cache
                    self.image_cache[thumb_path] = icon
                else:

                    icon = self.image_cache[thumb_path]

                self.image_cache.move_to_end(thumb_path)

                item = QListWidgetItem(str(i.media_filename))
                item.setData(Qt.UserRole, str(i.media_filename))
                icon = QIcon(thumb_path_str + thumb_path)
                item.setIcon(icon)

                item.setBackground(QColor("yellow"))

                self.new_list_widget.addItem(item)


        else:
            for image in all_images:
                # Crea un nuovo dizionario di ricerca per MEDIATOENTITY
                search_dict = {'id_media': "'" + str(image.id_media) + "'",
                               'entity_type': "'TOMBA'"}
                search_dict = u.remove_empty_items_fr_dict(search_dict)

                # Recupera l'elenco di 'US' associati all'immagine
                mediatoentity_data = self.DB_MANAGER.query_bool(search_dict, "MEDIATOENTITY")

                # Se l'immagine ha una o più 'US' associate, aggiungila all'elenco
                if mediatoentity_data:
                    us_images.append(image)

            if filter_text:  # se il filtro è attivo
                filtered_images = [i for i in untagged_images if filter_text.lower() in i.media_filename.lower()]
            else:
                filtered_images = us_images
            # Calcola gli indici di inizio e fine per la pagina corrente
            start_index = (self.current_page - 1) * self.page_size
            end_index = start_index + self.page_size

            # Ottieni i record delle immagini per la pagina corrente
            self.record_us_list = filtered_images[start_index:end_index]
            # Pulisci la QListWidget prima di aggiungere le nuove immagini
            self.new_list_widget.clear()
            # Aggiungi l'intestazione alla QListWidget
            header_item = QListWidgetItem(
                "Le righe selezionate in giallo indicano immagini non taggate\n Da questo strumento solo le righe selezionate gialle posso essere taggate ")
            header_item.setBackground(QColor('lightgrey'))
            header_item.setFlags(header_item.flags() & ~Qt.ItemIsSelectable)  # rendi l'item non selezionabile
            self.new_list_widget.addItem(header_item)
            # Aggiungi le immagini alla QListWidget

            for i in self.record_us_list:
                search_dict = {'id_media': "'" + str(i.id_media) + "'"}
                u = Utility()
                search_dict = u.remove_empty_items_fr_dict(search_dict)
                mediathumb_data = self.DB_MANAGER.query_bool(search_dict, "MEDIA_THUMB")
                thumb_path = str(mediathumb_data[0].filepath)
                # Verifica se l'immagine è già in cache
                if thumb_path not in self.image_cache:
                    # Se non è in cache, carica l'immagine
                    icon = QIcon(thumb_path_str + thumb_path)

                    # Se la cache ha raggiunto il limite, rimuove l'elemento più vecchio
                    if len(self.image_cache) >= self.cache_limit:
                        self.image_cache.popitem(last=False)

                    # Aggiunge l'immagine alla cache
                    self.image_cache[thumb_path] = icon
                else:
                    # Se è in cache, utilizza l'icona dalla cache
                    icon = self.image_cache[thumb_path]

                    # Aggiorna l'ordine della cache spostando l'elemento utilizzato alla fine
                self.image_cache.move_to_end(thumb_path)
                # Crea un nuovo dizionario di ricerca per MEDIATOENTITY
                search_dict = {'id_media': "'" + str(i.id_media) + "'",
                               'entity_type': "'TOMBA'"}
                search_dict = u.remove_empty_items_fr_dict(search_dict)
                # Recupera l'elenco di US associati all'immagine
                mediatoentity_data = self.DB_MANAGER.query_bool(search_dict, "MEDIATOENTITY")
                us_list = [str(g.id_entity) for g in
                           mediatoentity_data]  # Se 'entity_type' è 'US', aggiungi l'id_media a us_images
                # Rimuovi i duplicati dalla lista convertendola in un set e poi di nuovo in una lista
                us_list = list(set(us_list))
                us_list = [g.id_entity for g in mediatoentity_data if 'TOMBA' in g.entity_type]
                item = QListWidgetItem(str(i.media_filename))
                item.setData(Qt.UserRole, str(i.media_filename))
                icon = QIcon(thumb_path_str + thumb_path)
                item.setIcon(icon)
                if us_list:

                    item.setBackground(QColor("white"))

                    # Inizializza una lista vuota per i nomi delle US
                    us_names = []

                    for us_id in us_list:
                        # Crea un nuovo dizionario di ricerca per l'US
                        search_dict_us = {'id_tomba': us_id}
                        search_dict_us = u.remove_empty_items_fr_dict(search_dict_us)

                        # Query the US table
                        us_data = self.DB_MANAGER.query_bool(search_dict_us, "TOMBA")

                        # Se l'US esiste, aggiungi il suo nome alla lista
                        if us_data:
                            us_names.extend([str(us.nr_scheda_taf) for us in us_data])

                    # Se ci sono dei nomi US, aggiungi questi all'elemento
                    if us_names:
                        item.setText(item.text() + " - TOMBA: " + ', '.join(us_names))
                    else:
                        pass  # oppure: item.setText(item.text() + " - US: Non trovato")
                else:

                    item.setBackground(QColor("yellow"))

                # Aggiungi l'elemento alla QListWidget
                # self.new_list_widget.clear()
                self.new_list_widget.addItem(item)

            # Calcola il numero totale di pagine
            self.total_pages = math.ceil(len(filtered_images) / self.page_size)

            # Aggiorna l'aspetto delle etichette dei numeri delle pagine
            self.update_page_labels()

    def update_page_labels(self):
        # Disabilita il pulsante "Indietro" se siamo alla prima pagina
        self.prevButton.setEnabled(self.current_page > 1)

        # Disabilita il pulsante "Avanti" se siamo all'ultima pagina
        self.nextButton.setEnabled(self.current_page < self.total_pages)

        # Aggiorna l'aspetto delle etichette dei numeri delle pagine
        for label in self.pageLabels:
            page_number = int(label.text())
            label.setEnabled(page_number != self.current_page)

        # Aggiorna l'etichetta della pagina corrente e del totale delle pagine
        self.current_page_label.setText(f"Pagina corrente: {self.current_page}")
        self.total_pages_label.setText(f"Totale pagine: {self.total_pages}")

    def go_to_previous_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_images(self.current_filter_text)

    def go_to_next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_images(self.current_filter_text)

    def on_page_label_clicked(self, page, _=None):
        if page != self.current_page:
            self.current_page = page
            self.load_images(self.current_filter_text)

    def filter_items(self):
        # Ottieni il testo corrente nel campo di ricerca
        self.current_filter_text = self.search_field.text().lower()
        self.load_images(self.current_filter_text)
    def on_done_selecting_all(self):

        def r_list():
            sito = self.comboBox_sito.currentText()
            #area = self.comboBox_area.currentText()
            us = self.lineEdit_nr_scheda.text()
            record_us_list=[]
            #for sing_tags in selected_us:
            search_dict = {'sito': "'" + str(sito)+ "'",
                           #'area': "'" + str(area) + "'",
                           'nr_scheda_taf': "'" + str(us) + "'"
                           }
            j = self.DB_MANAGER.query_bool(search_dict, 'TOMBA')
            record_us_list.append(j)
            us_list = []
            for r in record_us_list:
                us_list.append([r[0].id_tomba, 'TOMBA', 'tomba_table'])
            # QMessageBox.information(self, "Scheda US", str(us_list), QMessageBox.Ok)
            return us_list

        items_selected = self.new_list_widget.selectedItems()
        for item in items_selected:
            for us_data in r_list():
                id_orig_item = item.text()  # return the name of original file
                search_dict = {'filename': "'" + str(id_orig_item) + "'"}
                media_data = self.DB_MANAGER.query_bool(search_dict, 'MEDIA')

                # Check if media_data is not empty
                if media_data:
                    # Check if this image is already in the database
                    search_dict = {'id_media': "'" + str(media_data[0].id_media) + "'"}
                    existing_entry = self.DB_MANAGER.query_bool(search_dict, 'MEDIATOENTITY')

                    # If this image is already in the database, continue with the next item
                    if existing_entry:
                        continue

                    self.insert_mediaToEntity_rec(us_data[0], us_data[1], us_data[2], media_data[0].id_media,
                                                  media_data[0].filepath, media_data[0].filename)
                else:
                    pass
                    #QMessageBox.warning(self, "Attenzione",
                                        #"Immagine già taggata: " + str(id_orig_item))
                    # After tagging the image, update the corresponding QListWidgetItem

        # After tagging, update the iconListWidget
        self.fill_iconListWidget()
        self.update_list_widget_item(item)
    def update_list_widget_item(self,item):
        #items_selected = self.new_list_widg)et.selectedItems(
        search_dict = {'media_name': "'" + str(item.text()) + "'"}
        u = Utility()
        search_dict = u.remove_empty_items_fr_dict(search_dict)
        mediatoentity_data = self.DB_MANAGER.query_bool(search_dict, "MEDIATOENTITY")

        # Update the QListWidgetItem based on whether it matches
        if mediatoentity_data:
            item.setBackground(QColor("white"))

            # Create a new search dictionary for the US
            search_dict_us = {'id_us': "'" + str(mediatoentity_data[0].id_entity) + "'"}
            search_dict_us = u.remove_empty_items_fr_dict(search_dict_us)

            # Query the US table
            us_data = self.DB_MANAGER.query_bool(search_dict_us, "TOMBA")

            # If the US exists, add its name to the item
            if us_data:
                item.setText(item.text() + " - US: " + str(us_data[0].nr_scheda_taf))
            else:
                item.setText(item.text() + " - US: Not found")

        else:
            item.setBackground(QColor("yellow"))

    def fill_iconListWidget(self):
        #self.iconListWidget.clear()  # pulisci prima il widget
        items_selected = self.new_list_widget.selectedItems()
        for item in items_selected:
            item.text()
        # Prendi i dati dal tuo database o dalla tua fonte dati
        #data = self.DB_MANAGER.query('MEDIA_THUMB')
        search_dict = {'media_filename': "'" + str(item.text()) + "'"}
        u = Utility()
        search_dict = u.remove_empty_items_fr_dict(search_dict)
        data = self.DB_MANAGER.query_bool(search_dict, "MEDIA_THUMB")
        #QMessageBox.information(self, 'ok',str(item.text()))
        conn = Connection()

        thumb_path = conn.thumb_path()
        thumb_path_str = thumb_path['thumb_path']
        # crea un nuovo QListWidgetItem
        if data:
            list_item = QListWidgetItem(data[0].media_filename)  # utilizza il nome del file come testo dell'elemento
            list_item.setData(Qt.UserRole,data[0].media_filename)  # utilizza il nome del file come dati personalizzati dell'elemento

            # crea una QIcon con l'immagine
            #icon = QIcon(thumb_path_str + thumb_path)
            icon = QIcon(thumb_path_str + data[0].filepath)  # utilizza il percorso del file per creare l'icona
            #QMessageBox.information(self,'ok',str(thumb_path_str + data[0].filepath))
            # imposta l'icona dell'elemento
            list_item.setIcon(icon)

            # aggiungi l'elemento al QListWidget
            self.iconListWidget.addItem(list_item)
    def loadMediaPreview(self):
        self.iconListWidget.clear()
        conn = Connection()
        thumb_path = conn.thumb_path()
        thumb_path_str = thumb_path['thumb_path']
        # if mode == 0:
        # """ if has geometry column load to map canvas """
        rec_list = self.ID_TABLE + " = " + str(
            eval("self.DATA_LIST[int(self.REC_CORR)]." + self.ID_TABLE))
        search_dict = {
            'id_entity': "'" + str(eval("self.DATA_LIST[int(self.REC_CORR)]." + self.ID_TABLE)) + "'",
            'entity_type': "'TOMBA'"}
        record_us_list = self.DB_MANAGER.query_bool(search_dict, 'MEDIATOENTITY')
        for i in record_us_list:
            search_dict = {'id_media': "'" + str(i.id_media) + "'"}
            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)
            mediathumb_data = self.DB_MANAGER.query_bool(search_dict, "MEDIA_THUMB")
            thumb_path = str(mediathumb_data[0].filepath)
            item = QListWidgetItem(str(i.media_name))
            item.setData(Qt.UserRole, str(i.media_name))
            icon = QIcon(thumb_path_str+thumb_path)
            item.setIcon(icon)
            self.iconListWidget.addItem(item)
        # elif mode == 1:
            # self.iconListWidget.clear()
    def openWide_image(self):
        items = self.iconListWidget.selectedItems()
        conn = Connection()
        conn_str = conn.conn_str()
        thumb_resize = conn.thumb_resize()
        thumb_resize_str = thumb_resize['thumb_resize']
        for item in items:
            dlg = ImageViewer()
            id_orig_item = item.text()  # return the name of original file
            search_dict = {'media_filename': "'" + str(id_orig_item) + "'" , 'mediatype': "'" + 'video' + "'"} 
            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)
            #try:
            res = self.DB_MANAGER.query_bool(search_dict, "MEDIA_THUMB")
            search_dict_2 = {'media_filename': "'" + str(id_orig_item) + "'" , 'mediatype': "'" + 'image' + "'"}  
            search_dict_2 = u.remove_empty_items_fr_dict(search_dict_2)
            #try:
            res_2 = self.DB_MANAGER.query_bool(search_dict_2, "MEDIA_THUMB")
            search_dict_3 = {'media_filename': "'" + str(id_orig_item) + "'"}  
            search_dict_3 = u.remove_empty_items_fr_dict(search_dict_3)
            #try:
            res_3 = self.DB_MANAGER.query_bool(search_dict_3, "MEDIA_THUMB")
            # file_path = str(res[0].path_resize)
            # file_path_2 = str(res_2[0].path_resize)
            file_path_3 = str(res_3[0].path_resize)
            if bool(res):
                os.startfile(str(thumb_resize_str+file_path_3))
            elif bool(res_2):
                dlg.show_image(str(thumb_resize_str+file_path_3))  
                dlg.exec_()

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
        except Exception as e:
            if str(e) == "list.remove(x): x not in list":
                pass
            else:
                if self.L=='it':
                    QMessageBox.warning(self, "Messaggio", "Sistema di aggiornamento lista Sito: " + str(e), QMessageBox.Ok)
                elif self.L=='en':
                    QMessageBox.warning(self, "Message", "Site list update system: " + str(e), QMessageBox.Ok)
                elif self.L=='de':
                    QMessageBox.warning(self, "Nachricht", "Aktualisierungssystem für die Ausgrabungstätte: " + str(e), QMessageBox.Ok)
                else:
                    pass

        self.comboBox_sito.clear()

        sito_vl.sort()
        self.comboBox_sito.addItems(sito_vl)

        
        # Load area values from thesaurus
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'tomba_table' + "'",
            'tipologia_sigla': "'" + '7.8' + "'"
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
                    QMessageBox.warning(self, "Message", "Site list update system: " + str(e), QMessageBox.Ok)
                elif self.L=='de':
                    QMessageBox.warning(self, "Nachricht", "Aktualisierungssystem für die Ausgrabungstätte: " + str(e), QMessageBox.Ok)
                else:
                    pass

        self.comboBox_area.clear()

        area_vl.sort()
        self.comboBox_area.addItems(area_vl)
        
        
        # lista rito

        self.comboBox_rito.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'tomba_table' + "'",
            'tipologia_sigla': "'" + '7.1' + "'"
        }

        rito = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        rito_vl = []

        for i in range(len(rito)):
            rito_vl.append(rito[i].sigla_estesa)

        rito_vl.sort()
        self.comboBox_rito.addItems(rito_vl)

        # lista segnacoli

        self.comboBox_segnacoli.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'tomba_table' + "'",
            'tipologia_sigla': "'" + '701.701' + "'"
        }

        segnacoli = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        segnacoli_vl = []

        for i in range(len(segnacoli)):
            segnacoli_vl.append(segnacoli[i].sigla_estesa)

        segnacoli_vl.sort()
        self.comboBox_segnacoli.addItems(segnacoli_vl)

        # lista canale libatorio

        self.comboBox_canale_libatorio.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'tomba_table' + "'",
            'tipologia_sigla': "'" + '701.701' + "'"
        }

        canale_libatorio = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        canale_libatorio_vl = []

        for i in range(len(canale_libatorio)):
            canale_libatorio_vl.append(canale_libatorio[i].sigla_estesa)

        canale_libatorio_vl.sort()
        self.comboBox_canale_libatorio.addItems(canale_libatorio_vl)


        self.comboBox_conservazione_taf.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'tomba_table' + "'",
            'tipologia_sigla': "'" + '7.2' + "'"
        }

        conservazione_taf = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        conservazione_taf_vl = []

        for i in range(len(conservazione_taf)):
            conservazione_taf_vl.append(conservazione_taf[i].sigla_estesa)

        conservazione_taf_vl.sort()
        self.comboBox_conservazione_taf.addItems(conservazione_taf_vl)

        # lista tipo copertura

        self.comboBox_copertura_tipo.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'tomba_table' + "'",
            'tipologia_sigla': "'" + '7.3' + "'"
        }

        copertura_tipo = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        copertura_tipo_vl = []

        for i in range(len(copertura_tipo)):
            copertura_tipo_vl.append(copertura_tipo[i].sigla_estesa)

        copertura_tipo_vl.sort()
        self.comboBox_copertura_tipo.addItems(copertura_tipo_vl)

        self.comboBox_tipo_contenitore_resti.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'tomba_table' + "'",
            'tipologia_sigla': "'" + '7.4' + "'"
        }

        tipo_contenitore_resti = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        tipo_contenitore_resti_vl = []

        for i in range(len(tipo_contenitore_resti)):
            tipo_contenitore_resti_vl.append(tipo_contenitore_resti[i].sigla_estesa)

        tipo_contenitore_resti_vl.sort()
        self.comboBox_tipo_contenitore_resti.addItems(tipo_contenitore_resti_vl)

        self.comboBox_corredo_presenza.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'tomba_table' + "'",
            'tipologia_sigla': "'" + '702.702' + "'"
        }

        corredo_presenza = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        corredo_presenza_vl = []

        for i in range(len(corredo_presenza)):
            corredo_presenza_vl.append(corredo_presenza[i].sigla_estesa)

        corredo_presenza_vl.sort()
        self.comboBox_corredo_presenza.addItems(corredo_presenza_vl)

        
        self.comboBox_deposizione.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'tomba_table' + "'",
            'tipologia_sigla': "'" + '7.6' + "'"
        }

        deposizione = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        deposizione_vl = []

        for i in range(len(deposizione)):
            deposizione_vl.append(deposizione[i].sigla_estesa)

        deposizione_vl.sort()
        self.comboBox_deposizione.addItems(deposizione_vl)

        self.comboBox_sepoltura.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'tomba_table' + "'",
            'tipologia_sigla': "'" + '7.7' + "'"
        }

        sepoltura = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        sepoltura_vl = []

        for i in range(len(sepoltura)):
            sepoltura_vl.append(sepoltura[i].sigla_estesa)

        sepoltura_vl.sort()
        self.comboBox_sepoltura.addItems(sepoltura_vl)

       
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
                msg = QMessageBox.information(self, "Warnung", "Sie haben keine archäologischen Stätten eingerichtet. Klicken Sie auf OK oder Abbrechen, um alle Datensätze zu sehen",QMessageBox.Ok | QMessageBox.Cancel) 
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
        '''
            This function charges the 'Periodo' combobox with the values from the 'Periodizzazione' table.
        '''
        try:

            sito = str(self.comboBox_sito.currentText())
            area = str(self.comboBox_area.currentText())
            search_dict = {
                'sito': "'" + sito + "'",
                # 'area': "'" + str(eval("self.DATA_LIST[int(self.REC_CORR)].area")) + "'",
            }
            periodo_vl = self.DB_MANAGER.query_bool(search_dict, 'PERIODIZZAZIONE')
            periodo_list = []
            for i in range(len(periodo_vl)):
                periodo_list.append(str(periodo_vl[i].periodo))
            try:
                periodo_vl.remove('')
            except:
                pass
            #
            self.comboBox_per_iniz.clear()
            self.comboBox_per_iniz.addItems(self.UTILITY.remove_dup_from_list(periodo_list))
            if self.STATUS_ITEMS[self.BROWSE_STATUS] == "Trova" or "Finden" or "Find":
                self.comboBox_per_iniz.setEditText("")
            elif self.STATUS_ITEMS[self.BROWSE_STATUS] == "Usa" or "Aktuell " or "Current":
                if len(self.DATA_LIST) > 0:
                    try:
                        self.comboBox_per_iniz.setEditText(self.DATA_LIST[self.rec_num].periodo_iniziale)
                        self.comboBox_per_iniz.show()
                    except:
                        pass  # non vi sono periodi per questo scavo
        except:
            pass

    def charge_periodo_fin_list(self):
        '''
            This function charges the 'Periodo' combobox with the values from the 'Periodizzazione' table.
        '''
        try:

            sito = str(self.comboBox_sito.currentText())
            area = str(self.comboBox_area.currentText())
            search_dict = {
                'sito': "'" + sito + "'",
                # 'area': "'" + str(eval("self.DATA_LIST[int(self.REC_CORR)].area")) + "'",
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
            if self.STATUS_ITEMS[self.BROWSE_STATUS] == "Trova" or "Finden" or "Find":
                self.comboBox_per_fin.setEditText("")
            elif self.STATUS_ITEMS[self.BROWSE_STATUS] == "Usa" or "Aktuell " or "Current":
                if len(self.DATA_LIST) > 0:
                    try:
                        self.comboBox_per_fin.setEditText(self.DATA_LIST[self.rec_num].periodo_iniziale)
                    except:
                        pass
        except:
            pass  # non vi sono periodi per questo scavo

    def charge_fase_iniz_list(self):

        '''
            This function charges the 'Fase' combobox with the values from the 'Periodizzazione' table.
        '''
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
            if self.STATUS_ITEMS[self.BROWSE_STATUS] == "Trova" or "Finden" or "Find":
                self.comboBox_fas_iniz.setEditText("")
            else:
                self.comboBox_fas_iniz.setEditText(self.DATA_LIST[self.rec_num].fase_iniziale)
        except:
            pass

    def charge_fase_fin_list(self):
        '''
            This function charges the 'Fase' combobox with the values from the 'Periodizzazione' table.
        '''
        # if self.comboBox_fas_fin.activated:
        try:
            search_dict = {
                'sito': "'" + str(self.comboBox_sito.currentText()) + "'",
                'periodo': "'" + str(self.comboBox_per_fin.currentText()) + "'"
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
            if self.STATUS_ITEMS[self.BROWSE_STATUS] == "Trova" or "Finden" or "Find":
                self.comboBox_fas_fin.setEditText("")
            else:
                self.comboBox_fas_fin.setEditText(self.DATA_LIST[self.rec_num].fase_finale)
        except:
            pass

    def charge_datazione_list(self):
        '''
            This function charges the 'Datazione' combobox with the values from the 'Periodizzazione' table.
        '''
        try:
            search_dict_iniz = {
                'sito': "'" + str(self.comboBox_sito.currentText()) + "'",
                'periodo': "'" + str(self.comboBox_per_iniz.currentText()) + "'",
                'fase': "'" + str(self.comboBox_fas_iniz.currentText()) + "'"
            }
            search_dict_fin = {
                'sito': "'" + str(self.comboBox_sito.currentText()) + "'",
                'periodo': "'" + str(self.comboBox_per_fin.currentText()) + "'",
                'fase': "'" + str(self.comboBox_fas_fin.currentText()) + "'"
            }
            datazione_list_vl_iniz = self.DB_MANAGER.query_bool(search_dict_iniz, 'PERIODIZZAZIONE')
            datazione_list_vl_fin = self.DB_MANAGER.query_bool(search_dict_fin, 'PERIODIZZAZIONE')

            datazione_list_iniz = [str(item.datazione_estesa) for item in datazione_list_vl_iniz if
                                   str(item.datazione_estesa) != '']
            datazione_list_fin = [str(item.datazione_estesa) for item in datazione_list_vl_fin if
                                  str(item.datazione_estesa) != '']

            self.lineEdit_datazione.clear()
            if datazione_list_iniz:
                datazione_list_iniz.sort()
                periodo_iniziale = datazione_list_iniz[-1]
                if datazione_list_fin:
                    datazione_list_fin.sort()
                    periodo_finale = datazione_list_fin[-1]
                    if periodo_finale and str(self.comboBox_per_fin.currentText()) != '':
                        self.lineEdit_datazione.setText(f"{periodo_iniziale} / {periodo_finale}")
                    else:
                        self.lineEdit_datazione.setText(periodo_iniziale)
                else:
                    self.lineEdit_datazione.setText(periodo_iniziale)
            else:
                self.lineEdit_datazione.setText("")
        except:
            pass

    # This function should be connected to the button click event
    def update_dating(self):
        '''
            This function updates the 'Dating' field for all US records in the database.
        '''

        try:
            updates_made = self.DB_MANAGER.update_tomba_dating_from_periodizzazione(self.comboBox_sito.currentText())
            if updates_made > 0:
                # Inform the user that updates have been made
                QMessageBox.information(self, "Success",
                                        f"All 'Dating' fields have been updated successfully. Total updates made: {updates_made}",
                                        QMessageBox.Ok)
            else:
                # Inform the user that no updates were necessary
                QMessageBox.information(self, "No Updates", "No 'Dating' fields needed to be updated.",
                                        QMessageBox.Ok)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while updating 'Dating': {e}", QMessageBox.Ok)

    def charge_struttura_nr(self):
        
        search_dict = {
            'sito': "'" + str(self.comboBox_sito.currentText()) + "'",
            'sigla_struttura': "'" + str(self.comboBox_sigla_struttura.currentText()) + "'",

        }

        struttura_vl = self.DB_MANAGER.query_bool(search_dict, 'STRUTTURA')
        
        nr_struttura_list=[]
        for i in range(len(struttura_vl)):
            #if not nr_struttura_list.__contains__(str(struttura_vl[i].numero_struttura)):
            nr_struttura_list.append(str(struttura_vl[i].numero_struttura))
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

        struttura_vl = self.DB_MANAGER.query_bool(search_dict, 'SCHEDAIND')
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

    def charge_individuo_list(self):
        try:
            sito = str(self.comboBox_sito.currentText())
            search_dict = {
                'sito': "'" + sito + "'",
                'sigla_struttura': "'" + str(self.comboBox_sigla_struttura.currentText()) + "'",
                'nr_struttura': "'" + str(self.comboBox_nr_struttura.currentText()) + "'"
            }
            inv_vl = self.DB_MANAGER.query_bool(search_dict, 'SCHEDAIND')
            inv_list = [str(item.nr_individuo) for item in inv_vl if item.nr_individuo != '']


            try:
                inv_list.remove('')
            except:
                pass

            self.comboBox_nr_individuo.clear()
            self.comboBox_nr_individuo.addItems(self.UTILITY.remove_dup_from_list(inv_list))

            if self.STATUS_ITEMS[self.BROWSE_STATUS] == "Trova" or "Finden" or "Find":
                self.comboBox_nr_individuo.setEditText("")
            elif self.STATUS_ITEMS[self.BROWSE_STATUS] == "Usa" or "Aktuell " or "Current":
                if len(self.DATA_LIST) > 0:
                    self.comboBox_nr_individuo.setEditText(self.DATA_LIST[self.rec_num].nr_individuo)

        except Exception as e:
            QMessageBox.critical(self, 'Error', f'An error occurred: {e}', QMessageBox.Ok)

    def charge_oggetti_esterno_list(self):
        try:
            sito = str(self.comboBox_sito.currentText())
            area = str(self.comboBox_area.currentText())
            
            search_dict = {
                
                'sito': "'" + sito + "'",
                'struttura': "'" + str(eval('self.DATA_LIST[int(self.REC_CORR)].sigla_struttura'))+'-'+ str(eval('self.DATA_LIST[int(self.REC_CORR)].nr_struttura'))+"'"#str(eval("self.DATA_LIST[int(self.REC_CORR)].area"))+ "'",
            }
            inv_vl = self.DB_MANAGER.query_bool(search_dict,'INVENTARIO_MATERIALI')
            inv_list = []
            for i in range(len(inv_vl)):
                inv_list.append(str(inv_vl[i].n_reperto))
            try:
                inv_vl.remove('')
            except :
                pass
            self.comboBox_oggetti_esterno.clear()
            self.comboBox_oggetti_esterno.addItems(self.UTILITY.remove_dup_from_list(inv_list))
            if self.STATUS_ITEMS[self.BROWSE_STATUS] == "Trova" or "Finden" or "Find":
                self.comboBox_oggetti_esterno.setEditText("")
            elif self.STATUS_ITEMS[self.BROWSE_STATUS] == "Usa" or "Aktuell " or "Current":
                if len(self.DATA_LIST) > 0:
                    try:
                        self.comboBox_oggetti_esterno.setEditText(self.DATA_LIST[self.rec_num].oggetti_esterno)
                        
                    except :
                        pass
        except:
            pass
    def on_toolButtonPan_toggled(self):
        self.toolPan = QgsMapToolPan(self.mapPreview)
        self.mapPreview.setMapTool(self.toolPan)

    def on_pushButton_showSelectedFeatures_pressed(self):
        field_position = self.pyQGIS.findFieldFrDict(self.ID_TABLE)

        field_list = self.pyQGIS.selectedFeatures()

        id_list_sf = self.pyQGIS.findItemInAttributeMap(field_position, field_list)
        id_list = []
        for idl in id_list_sf:
            sid = idl.toInt()
            id_list.append(sid[0])

        items, order_type = [self.ID_TABLE], "asc"
        self.empty_fields()

        self.DATA_LIST = []

        temp_data_list = self.DB_MANAGER.query_sort(id_list, items, order_type, self.MAPPER_TABLE_CLASS, self.ID_TABLE)

        for us in temp_data_list:
            self.DATA_LIST.append(us)

        self.fill_fields()
        self.BROWSE_STATUS = 'b'
        self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
        if type(self.REC_CORR) == "<type 'str'>":
            corr = 0
        else:
            corr = self.REC_CORR

        self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
        self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
        self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]

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
            self.BROWSE_STATUS = 'b'
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
        if self.BROWSE_STATUS != "n":
            if bool(self.comboBox_sito.currentText()) and self.comboBox_sito.currentText()==sito_set_str:
                # Call the functions directly without connecting them to signals
                self.charge_periodo_iniz_list()
                self.charge_periodo_fin_list()

                try:
                    self.comboBox_fas_iniz.currentIndexChanged.disconnect()
                    self.comboBox_per_iniz.currentIndexChanged.disconnect()
                except TypeError:
                    pass  # Ignore the error if no connections exist
                self.comboBox_fas_iniz.currentIndexChanged.connect(self.charge_datazione_list)

                try:
                    self.comboBox_fas_fin.currentIndexChanged.disconnect()
                    self.comboBox_per_fin.currentIndexChanged.disconnect()
                except TypeError:
                    pass  # Ignore the error if no connections exist
                self.comboBox_fas_fin.currentIndexChanged.connect(self.charge_datazione_list)

                self.BROWSE_STATUS = "n"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.empty_fields_nosite()
                self.setComboBoxEnable(["self.comboBox_sito"], "False")
                self.setComboBoxEnable(["self.lineEdit_nr_scheda"], "True")

                

                self.SORT_STATUS = "n"
                self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.set_rec_counter('', '')
                self.label_sort.setText(self.SORTED_ITEMS["n"])
                self.numero_invetario()
                self.lineEdit_datazione.clear()
            else:
                self.BROWSE_STATUS = "n"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.empty_fields()
                self.setComboBoxEditable(["self.comboBox_sito"], 1)
                
                self.setComboBoxEnable(["self.comboBox_sito"], "True")
                self.setComboBoxEnable(["self.lineEdit_nr_scheda"], "True")

                
                self.SORT_STATUS = "n"
                self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.set_rec_counter('', '')
                self.label_sort.setText(self.SORTED_ITEMS["n"])
                self.numero_invetario()
                self.lineEdit_datazione.clear()
            self.enable_button(0)

    def on_pushButton_save_pressed(self):
        #self.model_a.database().close()
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
                        QMessageBox.warning(self, "Warnung", "Keine Änderung vorgenommen", QMessageBox.Ok)
                    else:
                        QMessageBox.warning(self, "Warning", "No changes have been made", QMessageBox.Ok)           
                                                           
        else:
            if self.data_error_check() == 0:
                test_insert = self.insert_new_rec()
                if test_insert == 1:
                    self.empty_fields()
                    self.SORT_STATUS = "n"
                    self.label_sort.setText(self.SORTED_ITEMS["n"])
                    self.charge_list()
                    self.set_sito()
                    self.charge_records()
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), len(self.DATA_LIST) - 1
                    self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)

                    self.setComboBoxEditable(["self.comboBox_sito"], 1)
                    # self.setComboBoxEditable(["self.comboBox_sigla_struttura"], 1)
                    # self.setComboBoxEditable(["self.comboBox_nr_struttura"], 1)
                    self.setComboBoxEditable(["self.comboBox_nr_individuo"], 1)
                    # self.setComboBoxEnable(["self.lineEdit_nr_scheda"], "False")
                    self.setComboBoxEnable(["self.comboBox_sito"], "False")
                    # self.setComboBoxEnable(["self.comboBox_sigla_struttura"], "False")
                    # self.setComboBoxEnable(["self.comboBox_nr_struttura"], "False")
                    self.setComboBoxEnable(["self.comboBox_nr_individuo"], "True")
                    self.fill_fields(self.REC_CORR)
                    self.enable_button(1)
                else:
                    if self.L=='it':
                        QMessageBox.warning(self, "ATTENZIONE", "Problema nell'inserimento dati", QMessageBox.Ok)
                    elif self.L=='de':
                        QMessageBox.warning(self, "Warnung", "Problem der Dateneingabe", QMessageBox.Ok)
                    else:
                        QMessageBox.warning(self, "Warning", "Problem with data entry", QMessageBox.Ok)    

    def data_error_check(self):
        test = 0
        EC = Error_check()
        if self.L=='it':
            if EC.data_is_empty(str(self.comboBox_sito.currentText())) == 0:
                QMessageBox.warning(self, "ATTENZIONE", "Campo Sito. \n Il campo non deve essere vuoto", QMessageBox.Ok)
                test = 1
                
        elif self.L=='de':  
            if EC.data_is_empty(str(self.comboBox_sito.currentText())) == 0:
                QMessageBox.warning(self, "Warnung", " Feld Ausgrabungstätte. \n Das Feld darf nicht leer sein", QMessageBox.Ok)
                test = 1

        else:   
            if EC.data_is_empty(str(self.comboBox_sito.currentText())) == 0:
                QMessageBox.warning(self, "WARNING", "Site Field. \n The field must not be empty", QMessageBox.Ok)
                test = 1        

        return test

    def insert_new_rec(self):
       
        corredo_tipo = self.table2dict("self.tableWidget_corredo_tipo")
        
        


        try:
            # data
            data = self.DB_MANAGER.insert_values_tomba(
                self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, self.ID_TABLE) + 1,
                str(self.comboBox_sito.currentText()),  # 1 - Sito
                str(self.comboBox_area.currentText()),
                int(self.lineEdit_nr_scheda.text()),  # 2 - nr scheda tafonomica
                str(self.comboBox_sigla_struttura.currentText()),  # 3 - tipo struttura
                str(self.comboBox_nr_struttura.currentText()),  # 4 - nr struttura
                str(self.comboBox_nr_individuo.currentText()),  # 5 - nr  individuo
                str(self.comboBox_rito.currentText()),  # 6 - rito
                str(self.textEdit_descrizione_taf.toPlainText()),  # 7 - descrizione
                str(self.textEdit_interpretazione_taf.toPlainText()),  # 8 - interpretazione
                str(self.comboBox_segnacoli.currentText()),  # 9 - segnacoli
                str(self.comboBox_canale_libatorio.currentText()),  # 10 - canale libatorio
                str(self.comboBox_oggetti_esterno.currentText()),  # 11 - oggetti esterno
                str(self.comboBox_conservazione_taf.currentText()),  # 12 - conservazione
                str(self.comboBox_copertura_tipo.currentText()),  # 13 - copertura
                str(self.comboBox_tipo_contenitore_resti.currentText()),  # 14 - tipo contenitore resti
                str(self.comboBox_deposizione.currentText()),  # 13 - copertura
                str(self.comboBox_sepoltura.currentText()),  # 14 - tipo contenitore resti
                str(self.comboBox_corredo_presenza.currentText()),  # 17 - corredo presenza
                str(corredo_tipo),  # 18 - corredo tipo
                str(self.textEdit_descrizione_corredo.toPlainText()),  # 19 - descrizione corredo
                str(self.comboBox_per_iniz.currentText()),  # 8 - periodo iniziale
                str(self.comboBox_fas_iniz.currentText()),  # 9 - fase iniziale
                str(self.comboBox_per_fin.currentText()),  # 10 - periodo finale iniziale
                str(self.comboBox_fas_fin.currentText()),  # 11 - fase finale
                str(self.lineEdit_datazione.text()))
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

            # insert new row into tableWidget

    def on_pushButton_insert_row_corredo_pressed(self):
        self.insert_new_row('self.tableWidget_corredo_tipo')

    def on_pushButton_remove_row_corredo_pressed(self):
        self.remove_row('self.tableWidget_corredo_tipo')

    

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
                    QMessageBox.warning(self, "Warnung", "du befindest dich im ersten Datensatz!", QMessageBox.Ok)
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
                    QMessageBox.warning(self, "Warnung", "du befindest dich im letzten Datensatz!", QMessageBox.Ok)
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
            msg = QMessageBox.warning(self, "Warnung!!!",
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
                    QMessageBox.warning(self, "Warnung", "Die Datenbank ist leer!", QMessageBox.Ok)
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
                    # self.setComboBoxEditable(["self.comboBox_sito"], 1)
                    # self.setComboBoxEditable(["self.comboBox_sigla_struttura"], 0)
                    # self.setComboBoxEditable(["self.comboBox_nr_struttura"], 0)
                    self.setComboBoxEditable(["self.comboBox_nr_individuo"], 1)
                    # self.setComboBoxEnable(["self.lineEdit_nr_scheda"], "True")
                    # self.setComboBoxEnable(["self.comboBox_sito"], "False")
                    # self.setComboBoxEnable(["self.comboBox_sigla_struttura"], "True")
                    # self.setComboBoxEnable(["self.comboBox_nr_struttura"], "True")
                    self.setComboBoxEnable(["self.comboBox_nr_individuo"], "True")

                    # self.setComboBoxEnable(["self.textEdit_descrizione_taf"], "False")
                    # self.setComboBoxEnable(["self.textEdit_interpretazione_taf"], "False")
                    # self.setComboBoxEnable(["self.textEdit_descrizione_corredo"], "False")
                    # self.setTableEnable(["self.tableWidget_corredo_tipo"], "False")

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
                    # self.setComboBoxEditable(["self.comboBox_sigla_struttura"], 0)
                    # self.setComboBoxEditable(["self.comboBox_nr_struttura"], 0)
                    self.setComboBoxEditable(["self.comboBox_nr_individuo"], 1)
                    # self.setComboBoxEnable(["self.lineEdit_nr_scheda"], "True")
                    # self.setComboBoxEnable(["self.comboBox_sito"], "True")
                    # self.setComboBoxEnable(["self.comboBox_sigla_struttura"], "True")
                    # self.setComboBoxEnable(["self.comboBox_nr_struttura"], "True")
                    self.setComboBoxEnable(["self.comboBox_nr_individuo"], "True")

                    # self.setComboBoxEnable(["self.textEdit_descrizione_taf"], "False")
                    # self.setComboBoxEnable(["self.textEdit_interpretazione_taf"], "False")
                    # self.setComboBoxEnable(["self.textEdit_descrizione_corredo"], "False")
                    # self.setTableEnable(["self.tableWidget_corredo_tipo"], "False")

                    ###
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.set_rec_counter('', '')
                    self.label_sort.setText(self.SORTED_ITEMS["n"])
                    self.charge_list()
                    self.empty_fields()
    def on_pushButton_showLayer_pressed(self):
        sing_layer = [self.DATA_LIST[self.REC_CORR]]
        self.pyQGIS.charge_tomba_layers(sing_layer)

    

    def on_pushButton_search_go_pressed(self):
        

        if self.BROWSE_STATUS != "f":
            if self.L=='it':
                QMessageBox.warning(self, "ATTENZIONE", "Per eseguire una nuova ricerca clicca sul pulsante 'new search' ",
                                    QMessageBox.Ok)
            elif self.L=='de':
                QMessageBox.warning(self, "Warnung", "Um eine neue Abfrage zu starten drücke  'new search' ",
                                    QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "WARNING", "To perform a new search click on the 'new search' button ",
                                    QMessageBox.Ok)  
        else:
            try:
                ## nr struttura
                if self.comboBox_area.currentText() != "":
                    area = int(self.comboBox_area.currentText())
                else:
                    area = ""

                ## nr scheda
                if self.lineEdit_nr_scheda.text() != "":
                    nr_scheda = int(self.lineEdit_nr_scheda.text())
                else:
                    nr_scheda = ""

                ## nr struttura
                if self.comboBox_nr_struttura.currentText() != "":
                    nr_struttura = int(self.comboBox_nr_struttura.currentText())
                else:
                    nr_struttura = ""

                ## nr individuo - handling QgsCheckableComboBox selection
                selected_nr_individuo = []
                for index in range(self.comboBox_nr_individuo.count()):
                    if self.comboBox_nr_individuo.model().item(index).checkState() == Qt.Checked:
                        selected_nr_individuo.append(str(self.comboBox_nr_individuo.model().item(index).text()))

                # Convert the list of selected items to a string format suitable for the search dictionary
                selected_nr_individuo_str = ', '.join(selected_nr_individuo)

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
                    self.TABLE_FIELDS[0]: "'" + str(self.comboBox_sito.currentText()) + "'",
                    self.TABLE_FIELDS[1]: area,#"'" + int(self.comboBox_area.currentText()) + "'",
                    self.TABLE_FIELDS[2]: nr_scheda,
                    self.TABLE_FIELDS[3]: "'" + str(self.comboBox_sigla_struttura.currentText()) + "'",
                    self.TABLE_FIELDS[4]: nr_struttura,
                    self.TABLE_FIELDS[5]: "'" + selected_nr_individuo_str + "'",
                    # ... (other fields)
                    self.TABLE_FIELDS[6]: "'" + str(self.comboBox_rito.currentText()) + "'",
                    self.TABLE_FIELDS[7]: "'" + str(self.textEdit_descrizione_taf.toPlainText()) + "'",
                    self.TABLE_FIELDS[8]: "'" + str(self.textEdit_interpretazione_taf.toPlainText()) + "'",
                    self.TABLE_FIELDS[9]: "'" + str(self.comboBox_segnacoli.currentText()) + "'",
                    self.TABLE_FIELDS[10]: "'" + str(self.comboBox_canale_libatorio.currentText()) + "'",
                    self.TABLE_FIELDS[11]: "'" + str(self.comboBox_oggetti_esterno.currentText()) + "'",
                    self.TABLE_FIELDS[12]: "'" + str(self.comboBox_conservazione_taf.currentText()) + "'",
                    self.TABLE_FIELDS[13]: "'" + str(self.comboBox_copertura_tipo.currentText()) + "'",
                    self.TABLE_FIELDS[14]: "'" + str(self.comboBox_tipo_contenitore_resti.currentText()) + "'",
                    self.TABLE_FIELDS[15]: "'" + str(self.comboBox_deposizione.currentText()) + "'",
                    self.TABLE_FIELDS[16]: "'" + str(self.comboBox_sepoltura.currentText()) + "'",
                    self.TABLE_FIELDS[17]: "'" + str(self.comboBox_corredo_presenza.currentText()) + "'",
                    self.TABLE_FIELDS[19]: "'" + str(self.textEdit_descrizione_corredo.toPlainText()) + "'",
                    self.TABLE_FIELDS[20]: periodo_iniziale,
                    self.TABLE_FIELDS[21]: fase_iniziale,
                    self.TABLE_FIELDS[22]: periodo_finale,
                    self.TABLE_FIELDS[23]: fase_finale,
                    self.TABLE_FIELDS[24]: "'" + str(self.lineEdit_datazione.text()) + "'"
                    }

                u = Utility()
                search_dict = u.remove_empty_items_fr_dict(search_dict)

                if not bool(search_dict):
                    if self.L=='it':
                        QMessageBox.warning(self, "ATTENZIONE", "Non è stata impostata nessuna ricerca!!!", QMessageBox.Ok)
                    elif self.L=='de':
                        QMessageBox.warning(self, "Warnung", "Keine Abfrage definiert!!!", QMessageBox.Ok)
                    else:
                        QMessageBox.warning(self, " WARNING", "No search has been set!!!", QMessageBox.Ok)
                else:
                    try:
                        res = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)

                        if not bool(res):
                            if self.L=='it':
                                QMessageBox.warning(self, "ATTENZIONE", "Non è stato trovato nessun record!", QMessageBox.Ok)
                            elif self.L=='de':
                                QMessageBox.warning(self, "Warnung", "Keinen Record gefunden!", QMessageBox.Ok)
                            else:
                                QMessageBox.warning(self, "WARNING", "No record found!", QMessageBox.Ok)

                            self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                            self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]

                            self.BROWSE_STATUS = "b"
                            self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])

                            self.setComboBoxEnable(["self.comboBox_sito"], "False")

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
                                        self.pyQGIS.charge_tomba_layers(self.DATA_LIST)
                                else:
                                    strings = ("Sono stati trovati", self.REC_TOT, "records")
                                    if self.toolButtonGis.isChecked():
                                        self.pyQGIS.charge_tomba_layers(self.DATA_LIST)
                            elif self.L=='de':
                                if self.REC_TOT == 1:
                                    strings = ("Es wurde gefunden", self.REC_TOT, "record")
                                    if self.toolButtonGis.isChecked():
                                        self.pyQGIS.charge_tomba_layers(self.DATA_LIST)
                                else:
                                    strings = ("Sie wurden gefunden", self.REC_TOT, "records")
                                    if self.toolButtonGis.isChecked():
                                        self.pyQGIS.charge_tomba_layers(self.DATA_LIST)
                            else:
                                if self.REC_TOT == 1:
                                    strings = ("It has been found", self.REC_TOT, "record")
                                    if self.toolButtonGis.isChecked():
                                        self.pyQGIS.charge_tomba_layers(self.DATA_LIST)
                                else:
                                    strings = ("They have been found", self.REC_TOT, "records")
                                    if self.toolButtonGis.isChecked():
                                        self.pyQGIS.charge_tomba_layers(self.DATA_LIST)

                            self.setComboBoxEnable(["self.comboBox_sito"], "False")

                            QMessageBox.warning(self, "Message", "%s %d %s" % strings, QMessageBox.Ok)
                    except Exception as e:
                        QMessageBox.critical(self, "Error", f"Search error: {e}", QMessageBox.Ok)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}", QMessageBox.Ok)

        self.enable_button_search(1)

        

    def generate_list_pdf(self):
        data_list = []
        for i in range(len(self.DATA_LIST)):
            sito = str(self.DATA_LIST[i].sito)#str(self.DATA_LIST[i].sito.replace('_',' '))
            nr_individuo = str(self.DATA_LIST[i].nr_individuo)
            nr_individuo_find = str(self.DATA_LIST[i].nr_individuo)
            sigla_struttura = '{}{}{}'.format(str(self.DATA_LIST[i].sigla_struttura), '-',
                                              str(self.DATA_LIST[i].nr_struttura))
            res_strutt = self.DB_MANAGER.query_bool(
                {"sito": "'" + str(sito) + "'", "struttura": "'" + str(sigla_struttura) + "'"}, "US")

            res_ind = self.DB_MANAGER.query_bool({"sito": "'" + sito + "'"},
                                                 "SCHEDAIND")

            us_ind_list = []

            for ri in res_ind:
                us_ind_list.append([str(ri.sito), str(ri.area), str(ri.us)])
            #QMessageBox.warning(self, "Messaggio",str(us_ind_list))
            res_quote_ind = ''
            quote_ind = []
            if bool(us_ind_list):
                res_quote_ind = self.DB_MANAGER.select_quote_from_db_sql(us_ind_list[0][0], us_ind_list[0][1],
                                                                         us_ind_list[0][2])

            for sing_us in res_quote_ind:
                sing_quota_value = str(sing_us[5])
                if sing_quota_value[0] == '-':
                    sing_quota_value = sing_quota_value[:7]
                else:
                    sing_quota_value = sing_quota_value[:6]

                sing_quota = [sing_quota_value, sing_us[4]]
                quote_ind.append(sing_quota)
            quote_ind.sort()

            if bool(quote_ind):
                quota_min_ind = '%s %s' % (quote_ind[0][0], quote_ind[0][1])
                quota_max_ind = '%s %s' % (quote_ind[-1][0], quote_ind[-1][1])
            else:
                if self.L=='it':
                
                    quota_min_ind = ""
                    quota_max_ind = ""
                elif self.L == 'de':
                    quota_min_ind = "Nicht im GIS einbinden "
                    quota_max_ind = "Nicht im GIS einbinden "
                else :
                    quota_min_ind= "Not inserted in GIS "
                    quota_max_ind = "Not inserted in GIS  "

            ##########################################################################

            res_quote_strutt=''
            us_strutt_list = []
            #if bool(res_strutt):
            for rs in res_strutt:
                us_strutt_list.append([str(rs.sito), str(rs.area), str(rs.us)])
                #us_strutt_list.sort()
            res_quote_strutt=''
            quote_strutt = []
            #if bool(us_strutt_list):
            for sing_us in us_strutt_list:
                res_quote_strutt = self.DB_MANAGER.select_quote_from_db_sql(sing_us[0], sing_us[1], sing_us[2])
            #if bool(res_quote_strutt):
            for sing_us in res_quote_strutt:
                sing_quota_value = str(sing_us[5])
                if sing_quota_value[0] == '-':
                    sing_quota_value = sing_quota_value[:7]
                else:
                    sing_quota_value = sing_quota_value[:6]

                sing_quota = [sing_quota_value, sing_us[4]]
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
                str(self.DATA_LIST[i].sito.replace('_',' ')),  # 0 - Sito
                str(self.DATA_LIST[i].nr_scheda_taf),  # 1 - numero scheda taf
                str(self.DATA_LIST[i].sigla_struttura),  # 2 - sigla struttura
                str(self.DATA_LIST[i].nr_struttura),  # 3 - nr struttura
                str(self.DATA_LIST[i].nr_individuo),  # 4 - nr individuo
                str(self.DATA_LIST[i].rito),  # 5 - rito
                str(self.DATA_LIST[i].descrizione_taf),  # 6 - descrizione
                str(self.DATA_LIST[i].interpretazione_taf),  # 7 - interpretazione
                str(self.DATA_LIST[i].segnacoli),  # 8 - segnacoli
                str(self.DATA_LIST[i].canale_libatorio_si_no),  # 9- canale libatorio l
                str(self.DATA_LIST[i].oggetti_rinvenuti_esterno),  # 10- oggetti rinvenuti esterno
                str(self.DATA_LIST[i].stato_di_conservazione),  # 11 - stato_di_conservazione
                str(self.DATA_LIST[i].copertura_tipo),  # 12 - copertura tipo
                str(self.DATA_LIST[i].tipo_contenitore_resti),  # 13 - tipo contenitore resti
                str(self.DATA_LIST[i].tipo_deposizione),  # 14 - orientamento asse
                str(self.DATA_LIST[i].tipo_sepoltura),  # 15 orientamento azimut
                str(self.DATA_LIST[i].corredo_presenza),  # 16-  corredo presenza
                str(self.DATA_LIST[i].corredo_tipo),  # 17 - corredo tipo
                str(self.DATA_LIST[i].corredo_descrizione),  # 18 - corredo descrizione
                str(self.DATA_LIST[i].periodo_iniziale),  # 19 - periodo iniziale
                str(self.DATA_LIST[i].fase_iniziale),  # 20 - fase iniziale
                str(self.DATA_LIST[i].periodo_finale),  # 21 - periodo finale
                str(self.DATA_LIST[i].fase_finale),  # 22 - fase finale
                str(self.DATA_LIST[i].datazione_estesa),#23
                quota_min_ind,  # 24 - quota min individuo
                quota_max_ind,  # 25 - quota max individuo
                quota_min_strutt,  # 26 - quota min struttura
                quota_max_strutt,  # 27 - quota max struttura
                us_ind_list,  # 28 - us individuo
                us_strutt_list  # 29 - us struttura
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
        return rec_to_update

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

        for row in range(len(self.data_list)):
            cmd = ('%s.insertRow(%s)') % (self.table_name, row)
            eval(cmd)
            for col in range(len(self.data_list[row])):
                item = QTableWidgetItem(self.data_list[row][col])
                exec_str = ('%s.setItem(%d,%d,item)') % (self.table_name, row, col)
                eval(exec_str)

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
    def empty_fields_nosite(self):
        
        corredo_tipo_row_count = self.tableWidget_corredo_tipo.rowCount()
        

        

        for i in range(corredo_tipo_row_count):
            self.tableWidget_corredo_tipo.removeRow(0)
        self.insert_new_row("self.tableWidget_corredo_tipo")  # 18 - corredo tipo

        

        self.comboBox_area.setEditText("")  # 1 - Sito
        self.lineEdit_nr_scheda.clear()  # 2 - nr scheda tafonomica
        self.comboBox_sigla_struttura.setEditText("")  # 3 - tipo struttura
        self.comboBox_nr_struttura.setEditText("")  # 4 - nr struttura
        # Clear QgsCheckableComboBox for nr_individuo
        for index in range(self.comboBox_nr_individuo.count()):
            self.comboBox_nr_individuo.model().item(index).setCheckState(Qt.Unchecked)

        self.comboBox_rito.setEditText("")  # 5 - rito
        self.textEdit_descrizione_taf.clear()  # 6 - descrizione
        self.textEdit_interpretazione_taf.clear()  # 7 - interpretazione
        self.comboBox_segnacoli.setEditText("")  # 8 - segnacoli
        self.comboBox_canale_libatorio.setEditText("")  # 9 - canale libatorio
        self.comboBox_oggetti_esterno.setEditText("")  # 10 - oggetti esterno
        self.comboBox_conservazione_taf.setEditText("")  # 11 - conservazione
        self.comboBox_copertura_tipo.setEditText("")  # 12 - copertura
        self.comboBox_tipo_contenitore_resti.setEditText("")  # 13 - tipo contenitore resti
        self.comboBox_deposizione.setEditText("")  # 14 - orientamento asse
        self.comboBox_sepoltura.setEditText("")
        self.comboBox_corredo_presenza.setEditText("")  # 19 - corredo presenza
        self.textEdit_descrizione_corredo.clear()  # 20 - descrizione corredo
        self.comboBox_per_iniz.setEditText("")  # 9 - periodo iniziale
        self.comboBox_fas_iniz.setEditText("")  # 10 - fase iniziale
        self.comboBox_per_fin.setEditText("")  # 11 - periodo finale iniziale
        self.comboBox_fas_fin.setEditText("")  # 12 - fase finale
        self.lineEdit_datazione.clear()  # 13 - datazione estesa
        self.iconListWidget.clear()
    def empty_fields(self):
        corredo_tipo_row_count = self.tableWidget_corredo_tipo.rowCount()
        

        

        for i in range(corredo_tipo_row_count):
            self.tableWidget_corredo_tipo.removeRow(0)
        self.insert_new_row("self.tableWidget_corredo_tipo")  # 18 - corredo tipo

        
        self.comboBox_sito.setEditText("")  # 1 - Sito
        self.comboBox_area.setEditText("")  # 1 - Sito
        self.lineEdit_nr_scheda.clear()  # 2 - nr scheda tafonomica
        self.comboBox_sigla_struttura.setEditText("")  # 3 - tipo struttura
        self.comboBox_nr_struttura.setEditText("")  # 4 - nr struttura
        # Clear QgsCheckableComboBox for nr_individuo
        for index in range(self.comboBox_nr_individuo.count()):
            self.comboBox_nr_individuo.model().item(index).setCheckState(Qt.Unchecked)

        self.comboBox_rito.setEditText("")  # 5 - rito
        self.textEdit_descrizione_taf.clear()  # 6 - descrizione
        self.textEdit_interpretazione_taf.clear()  # 7 - interpretazione
        self.comboBox_segnacoli.setEditText("")  # 8 - segnacoli
        self.comboBox_canale_libatorio.setEditText("")  # 9 - canale libatorio
        self.comboBox_oggetti_esterno.setEditText("")  # 10 - oggetti esterno
        self.comboBox_conservazione_taf.setEditText("")  # 11 - conservazione
        self.comboBox_copertura_tipo.setEditText("")  # 12 - copertura
        self.comboBox_tipo_contenitore_resti.setEditText("")  # 13 - tipo contenitore resti
        self.comboBox_deposizione.setEditText("")  # 14 - orientamento asse
        self.comboBox_sepoltura.setEditText("")
        self.comboBox_corredo_presenza.setEditText("")  # 19 - corredo presenza
        self.textEdit_descrizione_corredo.clear()  # 20 - descrizione corredo
        self.comboBox_per_iniz.setEditText("")  # 9 - periodo iniziale
        self.comboBox_fas_iniz.setEditText("")  # 10 - fase iniziale
        self.comboBox_per_fin.setEditText("")  # 11 - periodo finale iniziale
        self.comboBox_fas_fin.setEditText("")  # 12 - fase finale
        self.lineEdit_datazione.clear()  # 13 - datazione estesa
        self.iconListWidget.clear()
    def fill_fields(self, n=0):
        self.rec_num = n
        #if bool(self.DATA_LIST):
        try:

            self.comboBox_sito.setEditText(str(self.DATA_LIST[self.rec_num].sito))  # 1 - Sito
            self.comboBox_area.setEditText(str(self.DATA_LIST[self.rec_num].area))  # 1 - Sito
            self.lineEdit_nr_scheda.setText(str(self.DATA_LIST[self.rec_num].nr_scheda_taf))  # 2 - nr_scheda_taf
            self.comboBox_sigla_struttura.setEditText(self.DATA_LIST[self.rec_num].sigla_struttura)  # 3 - sigla_struttura
            self.comboBox_nr_struttura.setEditText(str(self.DATA_LIST[self.rec_num].nr_struttura))  # 4 - nr_struttura
            # Handle QgsCheckableComboBox for nr_individuo
            nr_individuo_values = str(self.DATA_LIST[self.rec_num].nr_individuo).split(
                ', ')  # Assuming it's a comma-separated string
            for index in range(self.comboBox_nr_individuo.count()):
                item_text = str(self.comboBox_nr_individuo.model().item(index).text())
                # Check each item if it's in the nr_individuo_values list
                if item_text in nr_individuo_values:
                    self.comboBox_nr_individuo.model().item(index).setCheckState(Qt.Checked)
                else:
                    self.comboBox_nr_individuo.model().item(index).setCheckState(Qt.Unchecked)
            # 5 - nr_individuo
            self.comboBox_rito.setEditText(str(self.DATA_LIST[self.rec_num].rito))  # 6 - rito
            self.textEdit_descrizione_taf.setText(str(self.DATA_LIST[self.rec_num].descrizione_taf))  # 7 - descrizione_taf
            self.textEdit_interpretazione_taf.setText(str(self.DATA_LIST[self.rec_num].interpretazione_taf))  # 8 - interpretazione_taf
            self.comboBox_segnacoli.setEditText(str(self.DATA_LIST[self.rec_num].segnacoli))  # 9 - segnacoli
            self.comboBox_canale_libatorio.setEditText(str(self.DATA_LIST[self.rec_num].canale_libatorio_si_no)) 
            self.comboBox_oggetti_esterno.setDefaultText(str(self.DATA_LIST[self.rec_num].oggetti_rinvenuti_esterno))  # 11 -  oggetti_rinvenuti_esterno
            self.comboBox_conservazione_taf.setEditText(str(self.DATA_LIST[self.rec_num].stato_di_conservazione))  # 12 - stato_di_conservazione
            self.comboBox_copertura_tipo.setEditText(str(self.DATA_LIST[self.rec_num].copertura_tipo))  # 13 - copertura_tipo
            self.comboBox_tipo_contenitore_resti.setEditText(str(self.DATA_LIST[
                                                                     self.rec_num].tipo_contenitore_resti))  
            self.comboBox_deposizione.setEditText(str(self.DATA_LIST[self.rec_num].tipo_deposizione))  # 15 - orientamento asse
            self.comboBox_sepoltura.setEditText(str(self.DATA_LIST[self.rec_num].tipo_sepoltura))  # 15 - orientamento asse        
            self.comboBox_corredo_presenza.setEditText(str(self.DATA_LIST[self.rec_num].corredo_presenza))  # 16 - corredo presenza
            self.textEdit_descrizione_corredo.setText(str(self.DATA_LIST[self.rec_num].corredo_descrizione))
            self.tableInsertData("self.tableWidget_corredo_tipo", self.DATA_LIST[self.rec_num].corredo_tipo)  # 27 - corredo tipo
            

            
            self.comboBox_per_iniz.setEditText(str(self.DATA_LIST[self.rec_num].periodo_iniziale))

        
            self.comboBox_fas_iniz.setEditText(str(self.DATA_LIST[self.rec_num].fase_iniziale))

        
            self.comboBox_per_fin.setEditText(str(self.DATA_LIST[self.rec_num].periodo_finale))

       
            self.comboBox_fas_fin.setEditText(str(self.DATA_LIST[self.rec_num].fase_finale))

            self.lineEdit_datazione.setText(str(self.DATA_LIST[self.rec_num].datazione_estesa))
            if self.toolButtonPreview.isChecked():
                self.loadMapPreview()
            if self.toolButtonPreviewMedia.isChecked():
                self.loadMediaPreview()
        except :#Exception as e:
            pass#QMessageBox.warning(self, "Errore fill", str(e), QMessageBox.Ok)

    def set_rec_counter(self, t, c):
        self.rec_tot = t
        self.rec_corr = c
        self.label_rec_tot.setText(str(self.rec_tot))
        self.label_rec_corrente.setText(str(self.rec_corr))

    def set_LIST_REC_TEMP(self):
        ## nr scheda
        if self.comboBox_area.currentText() == "":
            area = ''
        else:
            area = self.comboBox_area.currentText()
        
        
        if self.lineEdit_nr_scheda.text() == "":
            nr_scheda = ''
        else:
            nr_scheda = self.lineEdit_nr_scheda.text()

        ## nr struttura
        if self.comboBox_nr_struttura.currentText() == "":
            nr_struttura = ''
        else:
            nr_struttura = self.comboBox_nr_struttura.currentText()

        # Handle QgsCheckableComboBox selection for nr_individuo
        selected_nr_individuo = []
        for index in range(self.comboBox_nr_individuo.count()):
            if self.comboBox_nr_individuo.model().item(index).checkState() == Qt.Checked:
                selected_nr_individuo.append(str(self.comboBox_nr_individuo.model().item(index).text()))

        # Convert the list of selected items to a string format suitable for the DATA_LIST_REC_TEMP
        selected_nr_individuo_str = ', '.join(selected_nr_individuo)


            # TableWidget

       
        ##Corredo tipo
        corredo_tipo = self.table2dict("self.tableWidget_corredo_tipo")
        
        self.DATA_LIST_REC_TEMP = [
            str(self.comboBox_sito.currentText()),  # 1 - Sito
            int(area),
            int(nr_scheda),  # 2 - Nr schede
            str(self.comboBox_sigla_struttura.currentText()),  # 3 - Tipo struttura
            int(nr_struttura),  # 4 - Nr struttura
            selected_nr_individuo_str, #str(self.comboBox_nr_individuo.currentText()),  # 5 - Nr individuo
            str(self.comboBox_rito.currentText()),  # 6 - Rito
            str(self.textEdit_descrizione_taf.toPlainText()),  # 7 - Descrizione tafonimia
            str(self.textEdit_interpretazione_taf.toPlainText()),  # 8 - Interpretazione tafonimia
            str(self.comboBox_segnacoli.currentText()),  # 9 - Segnacoli
            str(self.comboBox_canale_libatorio.currentText()),  # 10 - Canale libatorio
            str(self.comboBox_oggetti_esterno.currentText()),  # 11 - Oggetti esterno
            str(self.comboBox_conservazione_taf.currentText()),  # 12 - Conservazione tomba
            str(self.comboBox_copertura_tipo.currentText()),  # 13 - Copertura tipo
            str(self.comboBox_tipo_contenitore_resti.currentText()),  # 14 - Tipo contenitore resti
            str(self.comboBox_deposizione.currentText()),  # 14 - Tipo contenitore resti
            str(self.comboBox_sepoltura.currentText()),  # 14 - Tipo contenitore resti
            str(self.comboBox_corredo_presenza.currentText()),  # 17 - corredo
            str(corredo_tipo),  # 18 - corredo tipo
            str(self.textEdit_descrizione_corredo.toPlainText()),  # 19 - descrizione corredo
            str(self.comboBox_per_iniz.currentText()),  # 8 - periodo iniziale
            str(self.comboBox_fas_iniz.currentText()),  # 9 - fase iniziale
            str(self.comboBox_per_fin.currentText()),  # 10 - periodo finale iniziale
            str(self.comboBox_fas_fin.currentText()),  # 11 - fase finale
            str(self.lineEdit_datazione.text())
        ]

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

    def setTableEnable(self, t, v):
        tab_names = t
        value = v

        for tn in tab_names:
            cmd = '{}{}{}{}'.format(tn, '.setEnabled(', v, ')')
            eval(cmd)

    def testing(self, name_file, message):
        f = open(str(name_file), 'w')
        f.write(str(message))
        f.close()
    def on_pushButton_print_pressed(self):
        if self.L=='it':
            if self.checkBox_s_us.isChecked():
                US_pdf_sheet = generate_tomba_pdf()
                data_list = self.generate_list_pdf()
                US_pdf_sheet.build_Tomba_sheets(data_list)
                QMessageBox.warning(self, 'Ok',"Esportazione terminata Schede Tomba",QMessageBox.Ok)
            else:   
                pass
            if self.checkBox_e_us.isChecked() :
                US_index_pdf = generate_tomba_pdf()
                data_list = self.generate_list_pdf()
                try:               
                    if bool(data_list):
                        US_index_pdf.build_index_Tomba(data_list, data_list[0][0])
                        QMessageBox.warning(self, 'Ok',"Esportazione terminata Elenco Tombe",QMessageBox.Ok)
                    else:
                        QMessageBox.warning(self, 'ATTENZIONE',"L'elenco Tombe non può essere esportato devi riempire prima le schede Tombe",QMessageBox.Ok)
                except Exception as e :
                    QMessageBox.warning(self, 'ATTENZIONE',str(e),QMessageBox.Ok)
            else:
                pass
        #     if self.checkBox_e_foto_t.isChecked():
        #         US_index_pdf = generate_US_pdf()
        #         data_list_foto = self.generate_list_foto()
        #         try:
        #                 if bool(data_list_foto):
        #                     US_index_pdf.build_index_Foto(data_list_foto, data_list_foto[0][0])
        #                     QMessageBox.warning(self, 'Ok',"Esportazione terminata Elenco Foto",QMessageBox.Ok)
        #                 else:
        #                     QMessageBox.warning(self, 'ATTENZIONE',"L'elenco foto non può essere esportato perchè non hai immagini taggate.",QMessageBox.Ok)
        #         except Exception as e :
        #             QMessageBox.warning(self, 'ATTENZIONE',str(e),QMessageBox.Ok)
        #     if self.checkBox_e_foto.isChecked():
        #         US_index_pdf = generate_US_pdf()
        #         data_list_foto = self.generate_list_foto()
        #         try:
        #                 if bool(data_list_foto):
        #                     US_index_pdf.build_index_Foto_2(data_list_foto, data_list_foto[0][0])
        #                     QMessageBox.warning(self, 'Ok',"Esportazione terminata Elenco Foto senza thumbanil",QMessageBox.Ok)
        #                 else:
        #                     QMessageBox.warning(self, 'ATTENZIONE',"L'elenco foto non può essere esportato perchè non hai immagini taggate.",QMessageBox.Ok)
        #         except Exception as e :
        #             QMessageBox.warning(self, 'ATTENZIONE',str(e),QMessageBox.Ok)
        # elif self.L=='en':
        #     if self.checkBox_s_us.isChecked():
        #         US_pdf_sheet = generate_US_pdf()
        #         data_list = self.generate_list_pdf()
        #         US_pdf_sheet.build_US_sheets_en(data_list)
        #         QMessageBox.warning(self, 'Ok',"Export finished Forms",QMessageBox.Ok)
        #     else:
        #         pass
        #     if self.checkBox_e_us.isChecked() :
        #         US_index_pdf = generate_US_pdf()
        #         data_list = self.generate_list_pdf()
        #         try:
        #             if bool(data_list):
        #                 US_index_pdf.build_index_US_en(data_list, data_list[0][0])
        #                 QMessageBox.warning(self, 'Ok',"Export finished Grave List",QMessageBox.Ok)
        #             else:
        #                 QMessageBox.warning(self, 'WARNING',"The Grave list cannot be exported you have to fill in the Grave tabs first",QMessageBox.Ok)
        #         except Exception as e :
        #             QMessageBox.warning(self, 'WARNING',str(e),QMessageBox.Ok)
        #     else:
        #         pass
        #     if self.checkBox_e_foto_t.isChecked():
        #         US_index_pdf = generate_US_pdf()
        #         data_list_foto = self.generate_list_foto()
        #         try:
        #                 if bool(data_list_foto):
        #                     US_index_pdf.build_index_Foto_en(data_list_foto, data_list_foto[0][0])
        #                     QMessageBox.warning(self, 'Ok',"Export finished Grave List",QMessageBox.Ok)
        #                 else:
        #                     QMessageBox.warning(self, 'WARNING', 'The photo list cannot be exported because you do not have tagged images.',QMessageBox.Ok)
        #         except Exception as e :
        #             QMessageBox.warning(self, 'WARNING',str(e),QMessageBox.Ok)
        #     if self.checkBox_e_foto.isChecked():
        #         US_index_pdf = generate_US_pdf()
        #         data_list_foto = self.generate_list_foto()
        #         try:
        #                 if bool(data_list_foto):
        #                     US_index_pdf.build_index_Foto_2_en(data_list_foto, data_list_foto[0][0])
        #                     QMessageBox.warning(self, 'Ok', "Export finished Photo List without thumbanil",QMessageBox.Ok)
        #                 else:
        #                     QMessageBox.warning(self, 'WARNING', "The photo list cannot be exported because you do not have tagged images.",QMessageBox.Ok)
        #         except Exception as e :
        #             QMessageBox.warning(self, 'WARNING',str(e),QMessageBox.Ok)
        # elif self.L=='de':
        #     if self.checkBox_s_us.isChecked():
        #         US_pdf_sheet = generate_US_pdf()
        #         data_list = self.generate_list_pdf()
        #         US_pdf_sheet.build_US_sheets_de(data_list)
        #         QMessageBox.warning(self, 'Ok',"Esportazione terminata Schede US",QMessageBox.Ok)
        #     else:
        #         pass
        #     if self.checkBox_e_us.isChecked() :
        #         US_index_pdf = generate_US_pdf()
        #         data_list = self.generate_list_pdf()
        #         try:
        #             if bool(data_list):
        #                 US_index_pdf.build_index_US_de(data_list, data_list[0][0])
        #                 QMessageBox.warning(self, "Okay", "Export beendet",QMessageBox.Ok)
        #             else:
        #                 QMessageBox.warning(self, 'WARNUNG', 'Die Liste kann nicht exportiert werden, Sie müssen zuerst die Formulare ausfüllen',QMessageBox.Ok)
        #         except Exception as e :
        #             QMessageBox.warning(self, 'WARNUNG',str(e),QMessageBox.Ok)
        #     else:
        #         pass
        #     if self.checkBox_e_foto_t.isChecked():
        #         US_index_pdf = generate_US_pdf()
        #         data_list_foto = self.generate_list_foto()
        #         try:
        #                 if bool(data_list_foto):
        #                     US_index_pdf.build_index_Foto_de(data_list_foto, data_list_foto[0][0])
        #                     QMessageBox.warning(self, "Okay", "Fertige Fotoliste exportieren",QMessageBox.Ok)
        #                 else:
        #                     QMessageBox.warning(self, 'WARNUNG', 'Die Fotoliste kann nicht exportiert werden, da Sie keine markierten Bilder haben.',QMessageBox.Ok)
        #         except Exception as e :
        #             QMessageBox.warning(self, 'WARNUNG',str(e),QMessageBox.Ok)
        #     if self.checkBox_e_foto.isChecked():
        #         US_index_pdf = generate_US_pdf()
        #         data_list_foto = self.generate_list_foto()
        #         try:
        #                 if bool(data_list_foto):
        #                     US_index_pdf.build_index_Foto_2_de(data_list_foto, data_list_foto[0][0])
        #                     QMessageBox.warning(self, 'Ok', 'Fertige Fotoliste ohne Daumenballen exportieren',QMessageBox.Ok)
        #                 else:
        #                     QMessageBox.warning(self, 'WARNUNG', 'Die Fotoliste kann nicht exportiert werden, da Sie keine markierten Bilder haben.',QMessageBox.Ok)
        #         except Exception as e :
        #             QMessageBox.warning(self, 'WARNUNG',str(e),QMessageBox.Ok)
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
    # def on_pushButton_convert_pressed(self):
    #     # if not bool(self.setPathpdf()):
    #         # QMessageBox.warning(self, "INFO", "devi scegliere un file pdf",
    #                             # QMessageBox.Ok)
    #     try:
    #         pdf_file = self.lineEdit_pdf_path.text()
    #         filename=pdf_file.split("/")[-1]
    #         docx_file = self.PDFFOLDER+'/'+filename+'.docx'
    #         # convert pdf to docx
    #         parse(pdf_file, docx_file, start=self.lineEdit_pag1.text(), end=self.lineEdit_pag2.text())
    #         QMessageBox.information(self, "INFO", "Conversion completed",
    #                             QMessageBox.Ok)
    #     except Exception as e:
    #         QMessageBox.warning(self, "Error", str(e),
    #                             QMessageBox.Ok)
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

    
        


    def check_for_updates(self):
        """Check if current record has been modified by others"""
        try:
            if self.BROWSE_STATUS == "b" and self.editing_record_id and self.DB_MANAGER:
                # Skip check if we're currently saving to avoid false positives
                if hasattr(self, 'is_saving') and self.is_saving:
                    return

                # Determine table name
                table_name = 'tomba_table'

                # Get current username to skip self-modifications
                current_user = self.concurrency_manager.get_username() if hasattr(self, 'concurrency_manager') else 'unknown'

                has_conflict, db_version, last_modified_by, last_modified_timestamp = \
                    self.concurrency_manager.check_version_conflict(
                        table_name,
                        self.editing_record_id,
                        self.current_record_version,
                        self.DB_MANAGER
                    )

                # Only show conflict if it's a real conflict:
                # - Not a self-modification (different user)
                # - Not a system update
                # - Has actual version change
                if has_conflict and last_modified_by and \
                   last_modified_by != current_user and \
                   last_modified_by.lower() not in ['system', 'postgres'] and \
                   db_version != self.current_record_version:
                    # Show notification
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Warning)
                    msg.setWindowTitle("Record Modificato / Record Modified")
                    msg.setText(
                        f"Questo record è stato modificato da {last_modified_by} "
                        f"alle {last_modified_timestamp}.\n\n"
                        f"This record was modified by {last_modified_by} "
                        f"at {last_modified_timestamp}.\n\n"
                        f"Vuoi ricaricare il record? / Do you want to reload?"
                    )
                    msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

                    if msg.exec_() == QMessageBox.Yes:
                        # Save current record position
                        current_pos = self.REC_CORR
                        # Reload records
                        self.charge_records()
                        # Restore position and fill fields
                        self.fill_fields(current_pos)
                        # Update version after reload
                        self.current_record_version = db_version
        except Exception as e:
            # Log silently to avoid annoying messages
            pass  # QgsMessageLog.logMessage(f"Update check error: {str(e)}", "PyArchInit", Qgis.Info)

## Class end
