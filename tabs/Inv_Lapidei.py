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
import numpy as np
import sys
from builtins import range
from builtins import str
from qgis.PyQt.QtCore import Qt, QSize, QVariant
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QDialog, QMessageBox, QListWidget, QListView, QFrame, QAbstractItemView, \
    QTableWidgetItem, QListWidgetItem
from qgis.PyQt.uic import loadUiType
from qgis.core import QgsSettings

from ..gui.imageViewer import ImageViewer
from ..modules.db.pyarchinit_conn_strings import Connection
from ..modules.db.pyarchinit_db_manager import Pyarchinit_db_management
from ..modules.db.pyarchinit_utility import Utility
from ..modules.utility.pyarchinit_error_check import Error_check
from ..modules.utility.pyarchinit_exp_Findssheet_pdf import generate_reperti_pdf
from ..modules.utility.pyarchinit_exp_Invlapsheet_pdf import generate_reperti_pdf
from ..gui.sortpanelmain import SortPanelMain
from ..gui.pyarchinitConfigDialog import pyArchInitDialog_Config
MAIN_DIALOG_CLASS, _ = loadUiType(os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'Inv_Lapidei.ui'))


class pyarchinit_Inventario_Lapidei(QDialog, MAIN_DIALOG_CLASS):
    L=QgsSettings().value("locale/userLocale")[0:2]
    if L=='it':
        MSG_BOX_TITLE = "PyArchInit - Scheda Lapidei"
    elif L=='en':
        MSG_BOX_TITLE = "PyArchInit - Stone form"
    elif L=='de':
        MSG_BOX_TITLE = "PyArchInit - Stone formular"
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
    TABLE_NAME = 'inventario_lapidei_table'
    MAPPER_TABLE_CLASS = "INVENTARIO_LAPIDEI"
    NOME_SCHEDA = "Scheda    Scheda reperti lapidei"
    ID_TABLE = "id_invlap"
    if L=='it':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Sito": "sito",
            "Scheda Numero": "scheda_numero",
            "Collocazione": "collocazione",
            "Oggetto": "oggetto",
            "Tipologia": "tipologia",
            "Materiale": "materiale",
            "D (letto posa)": "d_letto_posa",
            "d (letto attesa)": "d_letto_attesa",
            "Toro": "toro",
            "Spessore": "spessore",
            "Larghezza": "larghezza",
            "Lunghezza": "lunghezza",
            "h": 'h',
            "Descrizione": 'descrizione',
            "Lavorazione e stato di conservazione": 'lavorazione_e_stato_di_conservazione',
            "Confronti": 'confronti',
            "Cronologia": 'cronologia',
            "Bibliografia": 'bibliografia',
            "Autore scheda": 'compilatore'
        }

        SORT_ITEMS = [
            ID_TABLE,
            "Sito",
            "Scheda Numero",
            "Collocazione",
            "Oggetto",
            "Tipologia",
            "Materiale",
            "D (letto posa)",
            "d (letto attesa)",
            "Toro",
            "Spessore"
            "Larghezza",
            "Lunghezza",
            "h",
            "Descrizione",
            "Lavorazione e stato di conservazione",
            "Confronti",
            "Cronologia",
            "Bibliografia",
            "Autore scheda"
        ]
            
    elif L=='de':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Ausgrabungsstätte": "sito",
            "Feld Nr.": "scheda_numero",
            "Lage": "collocazione",
            "Thema": "oggetto",
            "Typologie": "tipologia",
            "Material": "materiale",
            "D (bett)": "d_letto_posa",
            "D (Wartebett)": "d_letto_attesa",
            "Wulst": "toro",
            "Dicke": "spessore",
            "Breite": "larghezza",
            "Länge": "lunghezza",
            "h": 'h',
            "Beschreibung": 'descrizione',
            "Verarbeitung und Erhaltungszustand": 'lavorazione_e_stato_di_conservazione',
            "Vergleiche": 'confronti',
            "Chronologie": 'cronologia',
            "Bibliographie": 'bibliografia',
            "Verfasser": 'compilatore'
        }

        SORT_ITEMS = [
            ID_TABLE,
            "Ausgrabungsstätte",
            "Feld Nr.",
            "Lage",
            "Thema",
            "Typologie",
            "Material",
            "D (bett)",
            "D (Wartebett)",
            "Wulst",
            "Dicke",
            "Breite",
            "Länge",
            "h",
            "Beschreibung",
            "Verarbeitung und Erhaltungszustand",
            "Vergleiche",
            "Chronologie",
            "Bibliographie",
            "Verfasser"
        ]
    else:
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Site": "sito",
            "Nr. Form": "scheda_numero",
            "Place": "collocazione",
            "Object": "oggetto",
            "Typology": "tipologia",
            "Material": "materiale",
            "D (bed pose)": "d_letto_posa",
            "D (waiting bed)": "d_letto_attesa",
            "Toro": "toro",
            "Thikness": "spessore",
            "Weight": "larghezza",
            "Lenght": "lunghezza",
            "h": 'h',
            "Description": 'descrizione',
            "Processing and state of presevation": 'lavorazione_e_stato_di_conservazione',
            "Comparision": 'confronti',
            "Chronology": 'cronologia',
            "Bibliography": 'bibliografia',
            "Filler": 'compilatore'
        }

        SORT_ITEMS = [
            ID_TABLE,
            "Site",
            "Nr. Form",
            "Place",
            "Object",
            "Typology",
            "Material",
            "D (bed pose)",
            "D (waiting bed)",
            "Toro",
            "Thikness",
            "Weight",
            "Lenght",
            "h",
            "Description",
            "Processing and state of presevation",
            "Comparision",
            "Chronology",
            "Bibliography",
            "Filler"
        ]
    TABLE_FIELDS = [
        "sito",
        "scheda_numero",
        "collocazione",
        "oggetto",
        "tipologia",
        "materiale",
        "d_letto_posa",
        "d_letto_attesa",
        "toro",
        "spessore",
        "larghezza",
        "lunghezza",
        "h",
        "descrizione",
        "lavorazione_e_stato_di_conservazione",
        "confronti",
        "cronologia",
        "bibliografia",
        "compilatore"
    ]

    TABLE_FIELDS_UPDATE = [
        "collocazione",
        "oggetto",
        "tipologia",
        "materiale",
        "d_letto_posa",
        "d_letto_attesa",
        "toro",
        "spessore",
        "larghezza",
        "lunghezza",
        "h",
        "descrizione",
        "lavorazione_e_stato_di_conservazione",
        "confronti",
        "cronologia",
        "bibliografia",
        "compilatore"
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

    SEARCH_DICT_TEMP = ""

    HOME = os.environ['PYARCHINIT_HOME']

    #   QUANT_PATH = '{}{}{}'.format(HOME, os.sep, "pyarchinit_Quantificazioni_folder")

    DB_SERVER = 'not defined'

    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.setupUi(self)
        self.currentLayerId = None
        try:
            self.on_pushButton_connect_pressed()
        except Exception as e:
            QMessageBox.warning(self, "Connection system", str(e), QMessageBox.Ok)
        self.fill_fields()
        self.set_sito()
        self.msg_sito()
    def plot_chart(self, d, t, yl):
        self.data_list = d
        self.title = t
        self.ylabel = yl

        if type(self.data_list) == list:
            data_diz = {}
            for item in self.data_list:
                data_diz[item[0]] = item[1]
        x = list(range(len(data_diz)))
        n_bars = len(data_diz)
        values = list(data_diz.values())
        teams = list(data_diz.keys())
        ind = np.arange(n_bars)
        # randomNumbers = random.sample(range(0, 10), 10)
        self.widget.canvas.ax.clear()
        # QMessageBox.warning(self, "Alert", str(teams) ,  QMessageBox.Ok)

        bars = self.widget.canvas.ax.bar(left=x, height=values, width=0.5, align='center', alpha=0.4, picker=5)
        # guardare il metodo barh per barre orizzontali
        self.widget.canvas.ax.set_title(self.title)
        self.widget.canvas.ax.set_ylabel(self.ylabel)
        l = []
        for team in teams:
            l.append('""')

            # self.widget.canvas.ax.set_xticklabels(x , ""   ,size = 'x-small', rotation = 0)
        n = 0

        for bar in bars:
            val = int(bar.get_height())
            x_pos = bar.get_x() + 0.25
            label = teams[n] + ' - ' + str(val)
            y_pos = 0.1  # bar.get_height() - bar.get_height() + 1
            self.widget.canvas.ax.tick_params(axis='x', labelsize=8)
            # self.widget.canvas.ax.set_xticklabels(ind + x, ['fg'], position = (x_pos,y_pos), xsize = 'small', rotation = 90)

            self.widget.canvas.ax.text(x_pos, y_pos, label, zorder=0, ha='center', va='bottom', size='x-small',
                                       rotation=90)
            n += 1
            # self.widget.canvas.ax.plot(randomNumbers)
        self.widget.canvas.draw()

    def on_pushButton_connect_pressed(self):
        # self.setComboBoxEditable(["self.comboBox_sito"],1)
        conn = Connection()
        conn_str = conn.conn_str()

        test_conn = conn_str.find('sqlite')

        if test_conn == 0:
            self.DB_SERVER = "sqlite"

        try:
            self.DB_MANAGER = Pyarchinit_db_management(conn_str)
            self.DB_MANAGER.connection()
            self.charge_records()
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
                    
                    QMessageBox.warning(self,"WILLKOMMEN","WILLKOMMEN in pyArchInit" + "Stoneformular"+ ". Die Datenbank ist leer. Tippe 'Ok' und aufgehts!",
                                        QMessageBox.Ok) 
                else:
                    QMessageBox.warning(self,"WELCOME", "Welcome in pyArchInit" + "Stone form" + ". The DB is empty. Push 'Ok' and Good Work!",
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

    def customize_gui(self):
        # media prevew system
        self.iconListWidget = QListWidget(self)
        self.iconListWidget.setFrameShape(QFrame.StyledPanel)
        self.iconListWidget.setFrameShadow(QFrame.Sunken)
        self.iconListWidget.setLineWidth(2)
        self.iconListWidget.setMidLineWidth(2)
        self.iconListWidget.setProperty("showDropIndicator", False)
        self.iconListWidget.setIconSize(QSize(150, 150))
        self.iconListWidget.setMovement(QListView.Snap)
        self.iconListWidget.setResizeMode(QListView.Adjust)
        self.iconListWidget.setLayoutMode(QListView.Batched)
        self.iconListWidget.setGridSize(QSize(160, 160))
        self.iconListWidget.setViewMode(QListView.IconMode)
        self.iconListWidget.setUniformItemSizes(True)
        self.iconListWidget.setBatchSize(1000)
        self.iconListWidget.setObjectName("iconListWidget")
        self.iconListWidget.SelectionMode()
        self.iconListWidget.setSelectionMode(QAbstractItemView.MultiSelection)
        self.iconListWidget.itemDoubleClicked.connect(self.openWide_image)
        self.tabWidget.addTab(self.iconListWidget, "Media")

        # delegate combobox

        #       valuesTE = ["frammento", "frammenti", "intero", "integro"]
        #       self.delegateTE = ComboBoxDelegate()
        #       self.delegateTE.def_values(valuesTE)
        #       self.delegateTE.def_editable('False')
        #       self.tableWidget_elementi_reperto.setItemDelegateForColumn(1,self.delegateTE)


        #   def loadMediaPreview(self, mode = 0):
        self.iconListWidget.clear()
        if mode == 0:
            """ if has geometry column load to map canvas """

            rec_list = self.ID_TABLE + " = " + str(
                eval("self.DATA_LIST[int(self.REC_CORR)]." + self.ID_TABLE))
            search_dict = {
                'id_entity': "'" + str(eval("self.DATA_LIST[int(self.REC_CORR)]." + self.ID_TABLE)) + "'",
                'entity_type': "'REPERTO'"}
            record_us_list = self.DB_MANAGER.query_bool(search_dict, 'MEDIATOENTITY')
            for i in record_us_list:
                search_dict = {'id_media': "'" + str(i.id_media) + "'"}

                u = Utility()
                search_dict = u.remove_empty_items_fr_dict(search_dict)
                mediathumb_data = self.DB_MANAGER.query_bool(search_dict, "MEDIA_THUMB")
                thumb_path = str(mediathumb_data[0].filepath)

                item = QListWidgetItem(str(i.id_media))

                item.setData(QtCore.Qt.UserRole, str(i.id_media))
                icon = QIcon(thumb_path)
                item.setIcon(icon)
                self.iconListWidget.addItem(item)
        elif mode == 1:
            self.iconListWidget.clear()

    def openWide_image(self):
        items = self.iconListWidget.selectedItems()
        for item in items:
            dlg = ImageViewer(self)
            id_orig_item = item.text()  # return the name of original file

            search_dict = {'id_media': "'" + str(id_orig_item) + "'"}

            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)

            try:
                res = self.DB_MANAGER.query_bool(search_dict, "MEDIA")
                file_path = str(res[0].filepath)
            except Exception as e:
                QMessageBox.warning(self, "Error", "Warning 1 file: " + str(e), QMessageBox.Ok)

            dlg.show_image(str(file_path))  # item.data(QtCore.Qt.UserRole).toString()))
            dlg.exec_()

    def charge_list(self):

        #lista sito

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

        #lista tipologia

        l = QgsSettings().value("locale/userLocale", QVariant)
        lang = ""
        for key, values in self.LANG.items():
            if values.__contains__(l):
                lang = str(key)
        lang = "'" + lang + "'"

        self.comboBox_tipologia.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'inventario_lapidei_table' + "'",
            'tipologia_sigla': "'" + '5.1' + "'"
        }

        tipologia = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        tipologia_vl = []

        for i in range(len(tipologia)):
            tipologia_vl.append(tipologia[i].sigla_estesa)

        tipologia_vl.sort()
        self.comboBox_tipologia.addItems(tipologia_vl)

        # lista materiale

        self.comboBox_materiale.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'inventario_lapidei_table' + "'",
            'tipologia_sigla': "'" + '5.2' + "'"
        }

        materiale = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        materiale_vl = []

        for i in range(len(materiale)):
            materiale_vl.append(materiale[i].sigla_estesa)

        materiale_vl.sort()
        self.comboBox_materiale.addItems(materiale_vl)

        # lista oggetto

        self.comboBox_oggetto.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'inventario_lapidei_table' + "'",
            'tipologia_sigla': "'" + '5.3' + "'"
        }

        oggetto = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        oggetto_vl = []

        for i in range(len(oggetto)):
            oggetto_vl.append(oggetto[i].sigla_estesa)

        oggetto_vl.sort()
        self.comboBox_oggetto.addItems(oggetto_vl)


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

            ##  def on_toolButtonPreviewMedia_toggled(self):
            ##      if self.toolButtonPreviewMedia.isChecked() == True:
            ##          QMessageBox.warning(self, "Messaggio", "Modalita' Preview Media Reperti attivata. Le immagini dei Reperti saranno visualizzate nella sezione Media", QMessageBox.Ok)
            ##          self.loadMediaPreview()
            ##      else:
            ##          self.loadMediaPreview(1)

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

        if self.BROWSE_STATUS != "n":
            if bool(self.comboBox_sito.currentText()) and self.comboBox_sito.currentText()==sito_set_str:
                self.BROWSE_STATUS = "n"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.empty_fields()

                #self.setComboBoxEditable(['self.comboBox_sito'], 0)
                # self.setComboBoxEditable(['self.comboBox_sito'], 1)
                self.setComboBoxEnable(['self.comboBox_sito'], 'False')
                self.setComboBoxEnable(['self.lineEdit_num_inv'], 'True')

                self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])

                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.set_rec_counter('', '')
                self.label_sort.setText(self.SORTED_ITEMS["n"])
                self.empty_fields_nosite()
            else:
                self.BROWSE_STATUS = "n"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.empty_fields()

                self.setComboBoxEditable(['self.comboBox_sito'], 0)
                # self.setComboBoxEditable(['self.comboBox_sito'], 1)
                self.setComboBoxEnable(['self.comboBox_sito'], 'True')
                self.setComboBoxEnable(['self.lineEdit_num_inv'], 'True')

                self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])

                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.set_rec_counter('', '')
                self.label_sort.setText(self.SORTED_ITEMS["n"])
                self.empty_fields()
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

                    self.setComboBoxEditable(['self.comboBox_sito'], 1)
                    self.setComboBoxEnable(['self.comboBox_sito'], 'False')
                    self.setComboBoxEnable(['self.lineEdit_num_inv'], 'False')

                    self.fill_fields(self.REC_CORR)
                    self.enable_button(1)

    def generate_list_pdf(self):
        data_list = []
        for i in range(len(self.DATA_LIST)):
            data_list.append([
                str(self.DATA_LIST[i].id_invlap),  # 0 - id_invlap
                str(self.DATA_LIST[i].sito),  # 1- contesto_provenienza
                int(self.DATA_LIST[i].scheda_numero),  # 2- scheda_numero
                str(self.DATA_LIST[i].collocazione),  # 3 - collocazione
                str(self.DATA_LIST[i].oggetto),  # 4 - oggetto
                str(self.DATA_LIST[i].tipologia),  # 5 - tipologia
                str(self.DATA_LIST[i].materiale),  # 6 - materiale
                str(self.DATA_LIST[i].d_letto_posa),  # 7 - D_letto_posa
                str(self.DATA_LIST[i].d_letto_attesa),  # 8 - d_letto_attesa
                str(self.DATA_LIST[i].toro),  # 9 - toro
                str(self.DATA_LIST[i].spessore),  # 10 - spessore
                str(self.DATA_LIST[i].larghezza),  # 11 - larghezza
                str(self.DATA_LIST[i].lunghezza),  # 12 - lunghezza
                str(self.DATA_LIST[i].h),  # 13 - h
                str(self.DATA_LIST[i].descrizione),  # 14 - descrizione
                str(self.DATA_LIST[i].lavorazione_e_stato_di_conservazione),
                # 15 - lavorazione_e_stato_di_conservazione
                str(self.DATA_LIST[i].confronti),  # 16 - confronti
                str(self.DATA_LIST[i].cronologia),  # 17 - .cronologia
                str(self.DATA_LIST[i].bibliografia),  # 18 - .bibliografia
                str(self.DATA_LIST[i].compilatore)  # 19 - autore scheda
            ])
        return data_list

    def on_pushButton_exp_pdf_sheet_pressed(self):
        if self.L=='it':
            Invlap_pdf_sheet = generate_reperti_pdf()
            data_list = self.generate_list_pdf()
            Invlap_pdf_sheet.build_Invlap_sheets(data_list)
        elif self.L=='de':
            Invlap_pdf_sheet = generate_reperti_pdf()
            data_list = self.generate_list_pdf()
            Invlap_pdf_sheet.build_Invlap_sheets_de(data_list)
        else:
            Invlap_pdf_sheet = generate_reperti_pdf()
            data_list = self.generate_list_pdf()
            Invlap_pdf_sheet.build_Invlap_sheets_en(data_list)
    def data_error_check(self):
        test = 0
        EC = Error_check()

        nr_inv = self.lineEdit_num_inv.text()
        if self.L=='it':
            if EC.data_is_empty(str(self.comboBox_sito.currentText())) == 0:
                QMessageBox.warning(self, "ATTENZIONE", "Campo Contesto-Provenienza. \n Il campo non deve essere vuoto",
                                    QMessageBox.Ok)
                test = 1

            if EC.data_is_empty(str(self.lineEdit_num_inv.text())) == 0:
                QMessageBox.warning(self, "ATTENZIONE", "Campo Scheda numero. \n Il campo non deve essere vuoto",
                                    QMessageBox.Ok)
                test = 1

            if nr_inv != "":
                if EC.data_is_int(nr_inv) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Campo Numero inventario\nIl valore deve essere di tipo numerico", QMessageBox.Ok)
                    test = 1
        elif self.L=='de':
            if EC.data_is_empty(str(self.comboBox_sito.currentText())) == 0:
                QMessageBox.warning(self, "ACHTUNG", " Feld Kontext / Herkunft \n Das Feld darf nicht leer sein", QMessageBox.Ok)
                test = 1

            if EC.data_is_empty(str(self.lineEdit_num_inv.text())) == 0:
                QMessageBox.warning(self, "ACHTUNG", " Feld Formular Nr. \n Das Feld darf nicht leer sein", QMessageBox.Ok)
                test = 1

            if nr_inv != "":
                if EC.data_is_int(nr_inv) == 0:
                    QMessageBox.warning(self, "ACHTUNG", "Feld Inv. Nr. \n Der Wert muss numerisch eingegeben werden", QMessageBox.Ok)
                    test = 1
                    
                    
        else:
            if EC.data_is_empty(str(self.comboBox_sito.currentText())) == 0:
                QMessageBox.warning(self, "WARNING", "Context Field \n The field must not be empty ",
                                    QMessageBox.Ok)
                test = 1

            if EC.data_is_empty(str(self.lineEdit_num_inv.text())) == 0:
                QMessageBox.warning(self, "WARNING", "Inv. Nr. Field \n The field must not be empty ",
                                    QMessageBox.Ok)
                test = 1

            if nr_inv != "":
                if EC.data_is_int(nr_inv) == 0:
                    QMessageBox.warning(self, "WARNING", "Inv. Nr. Field \n The value must be numerical", QMessageBox.Ok)
                    test = 1            
        return test

    def insert_new_rec(self):
        ##bibliografia
        bibliografia = self.table2dict("self.tableWidget_bibliografia")

        try:
            if self.lineEdit_d_letto_posa.text() == "":
                d_letto_posa = None
            else:
                d_letto_posa = float(self.lineEdit_d_letto_posa.text())

            if self.lineEdit_d_letto_attesa.text() == "":
                d_letto_attesa = None
            else:
                d_letto_attesa = float(self.lineEdit_d_letto_attesa.text())

            if self.lineEdit_toro.text() == "":
                toro = None
            else:
                toro = float(self.lineEdit_toro.text())

            if self.lineEdit_spessore.text() == "":
                spessore = None
            else:
                spessore = float(self.lineEdit_spessore.text())

            if self.lineEdit_larghezza.text() == "":
                larghezza = None
            else:
                larghezza = float(self.lineEdit_larghezza.text())

            if self.lineEdit_lunghezza.text() == "":
                lunghezza = None
            else:
                lunghezza = float(self.lineEdit_lunghezza.text())

            if self.lineEdit_h.text() == "":
                h = None
            else:
                h = float(self.lineEdit_h.text())

            data = self.DB_MANAGER.insert_values_Lapidei(
                self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, self.ID_TABLE) + 1,  # 0 - IDsito
                str(self.comboBox_sito.currentText()),  # 1 - Sito
                int(self.lineEdit_num_inv.text()),  # 2 - num_inv
                str(self.lineEdit_collocazione.text()),  # 3 - tipo_reperto
                str(self.comboBox_oggetto.currentText()),  # 4 - criterio
                str(self.comboBox_tipologia.currentText()),  # 5 - definizione
                str(self.comboBox_materiale.currentText()),  # 6 - descrizione
                d_letto_posa,  # 12 - stato di conservazione
                d_letto_attesa,  # 13 - datazione reperto
                toro,
                spessore,
                larghezza,
                lunghezza,
                h,
                str(self.textEdit_descrizione.toPlainText()),
                str(self.textEdit_lavorazione_e_stato_di_conservazione.toPlainText()),
                # 11 - luogo conservazione
                str(self.textEdit_confronti.toPlainText()),
                str(self.lineEdit_cronologia.text()),  # 5 - definizione
                str(bibliografia),
                str(self.lineEdit_compilatore.text()),  # 16 - rif biblio
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

           

    def on_pushButton_insert_row_bibliografia_pressed(self):
        self.insert_new_row('self.tableWidget_bibliografia')

    def on_pushButton_remove_row_bibliografia_pressed(self):
        self.remove_row('self.tableWidget_bibliografia')

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

    def on_pushButton_view_all_2_pressed(self):
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
            ##          if self.toolButtonPreviewMedia.isChecked() == True:
            ##              self.loadMediaPreview(1)

            # records surf functions

    def on_pushButton_first_rec_pressed(self):
        if self.check_record_state() == 1:
            ##          if self.toolButtonPreviewMedia.isChecked() == True:
            self.loadMediaPreview(1)
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
            ##          if self.toolButtonPreviewMedia.isChecked() == True:
            self.loadMediaPreview(0)
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
                    #self.setComboBoxEditable(['self.comboBox_sito'], 1)
                    self.setComboBoxEnable(['self.comboBox_sito'], 'False')
                    
                    ###
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.set_rec_counter('', '')
                    self.label_sort.setText(self.SORTED_ITEMS["n"])
                    #self.charge_list()
                    self.empty_fields_nosite()
                else:
                    self.BROWSE_STATUS = "f"
                    ###
                    self.setComboBoxEditable(['self.comboBox_sito'], 1)
                    self.setComboBoxEnable(['self.comboBox_sito'], 'True')
                   
                    
                    ###
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.set_rec_counter('', '')
                    self.label_sort.setText(self.SORTED_ITEMS["n"])
                    self.charge_list()
                    self.empty_fields()
    def on_pushButton_search_go_pressed(self):
        check_for_buttons = 0
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
            ##scavato
            if self.lineEdit_num_inv.text() != "":
                scheda_numero = int(self.lineEdit_num_inv.text())
            else:
                scheda_numero = ""

            if self.lineEdit_d_letto_posa.text() != "":
                d_letto_posa = int(self.lineEdit_d_letto_posa.text())
            else:
                d_letto_posa = ""

            if self.lineEdit_d_letto_attesa.text() != "":
                d_letto_attesa = int(self.lineEdit_d_letto_attesa.text())
            else:
                d_letto_attesa = ""

            if self.lineEdit_toro.text() != "":
                toro = int(self.lineEdit_toro.text())
            else:
                toro = ""

            if self.lineEdit_spessore.text() != "":
                spessore = int(self.lineEdit_spessore.text())
            else:
                spessore = ""

            if self.lineEdit_larghezza.text() != "":
                larghezza = int(self.lineEdit_larghezza.text())
            else:
                larghezza = ""

            if self.lineEdit_lunghezza.text() != "":
                lunghezza = int(self.lineEdit_lunghezza.text())
            else:
                lunghezza = ""

            if self.lineEdit_h.text() != "":
                h = int(self.lineEdit_h.text())
            else:
                h = ""

            search_dict = {
                self.TABLE_FIELDS[0]: "'" + str(self.comboBox_sito.currentText()) + "'",
                self.TABLE_FIELDS[1]: scheda_numero,
                self.TABLE_FIELDS[2]: "'" + str(self.lineEdit_collocazione.text()) + "'",
                self.TABLE_FIELDS[3]: "'" + str(self.comboBox_oggetto.currentText()) + "'",
                self.TABLE_FIELDS[4]: "'" + str(self.comboBox_tipologia.currentText()) + "'",
                self.TABLE_FIELDS[5]: "'" + str(self.comboBox_materiale.currentText()) + "'",
                self.TABLE_FIELDS[6]: d_letto_posa,
                self.TABLE_FIELDS[7]: d_letto_attesa,
                self.TABLE_FIELDS[8]: toro,
                self.TABLE_FIELDS[9]: spessore,
                self.TABLE_FIELDS[10]: larghezza,
                self.TABLE_FIELDS[11]: lunghezza,
                self.TABLE_FIELDS[12]: h,
                self.TABLE_FIELDS[13]: "'" + str(self.textEdit_descrizione.text()) + "'",
                self.TABLE_FIELDS[14]: "'" + str(self.lineEdit_lavorazione_e_stato_di_conservazione.text()) + "'",
                self.TABLE_FIELDS[15]: "'" + str(self.lineEdit_confronti.text()) + "'",
                self.TABLE_FIELDS[16]: "'" + str(self.lineEdit_cronologia.text()) + "'",
                self.TABLE_FIELDS[17]: "'" + str(self.lineEdit_bibliografia.text()) + "'",
                self.TABLE_FIELDS[18]: "'" + str(self.lineEdit_compilatore.text()) + "'",
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

                    self.setComboBoxEditable(["self.comboBox_sito"], 1)
                    self.setComboBoxEnable(["self.comboBox_sito"], "False")
                    #self.setlineEditEnable(["self.lineEdit_num_inv"], "False")
                    self.settextEditEnable(["self.textEdit_descrizione"], "True")
                    self.setTableEnable(["self.tableWidget_bibliografia"], "True")
                    check_for_buttons = 1

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

                    self.setComboBoxEditable(["self.comboBox_sito"], 1)
                    #self.setlineEditEnable(['self.lineEdit_num_inv'], "False")
                    self.setComboBoxEnable(['self.comboBox_sito'], "False")
                    self.setTableEnable(["self.tableWidget_bibliografia"], "True")
                    check_for_buttons = 1

                    QMessageBox.warning(self, "Message", "%s %d %s" % strings, QMessageBox.Ok)

        if check_for_buttons == 1:
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
        # rec_to_update = rec_to_update[:2]
        return rec_to_update

    # custom functions
    ######old system
    ##  def charge_records(self):
    ##      self.DATA_LIST = []
    ##      id_list = []
    ##      for i in self.DB_MANAGER.query(eval(self.MAPPER_TABLE_CLASS)):
    ##          id_list.append(eval("i."+ self.ID_TABLE))
    ##
    ##      temp_data_list = self.DB_MANAGER.query_sort(id_list, [self.ID_TABLE], 'asc', self.MAPPER_TABLE_CLASS, self.ID_TABLE)
    ##      for i in temp_data_list:
    ##          self.DATA_LIST.append(i)


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
                item = QTableWidgetItem(str(self.data_list[row][col]))
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
        try:
            rowIndex = (rowSelected[1].row())
            cmd = ("%s.removeRow(%d)") % (table_name, rowIndex)
            eval(cmd)
        except:
            QMessageBox.warning(self, "Messaggio", "Devi selezionare una riga", QMessageBox.Ok)
    
    
    def empty_fields_nosite(self):
        bibliografia_row_count = self.tableWidget_bibliografia.rowCount()

        #self.comboBox_sito.setEditText("")  # 1 - Sito
        self.lineEdit_num_inv.clear()  # 2 - num_inv
        self.lineEdit_collocazione.clear()  # 3 - collocazione
        self.comboBox_oggetto.setEditText("")  # 4 - oggetto
        self.comboBox_tipologia.setEditText("")  # 5 - tipologia
        self.comboBox_materiale.setEditText("")  # 9 - materiale
        self.lineEdit_d_letto_posa.clear()  # 6 - d_letto_posa
        self.lineEdit_d_letto_attesa.clear()  # 7 - d_letto_attesa
        self.lineEdit_toro.clear()  # 8 - toro
        self.lineEdit_spessore.clear()  # 10 - spessore
        self.lineEdit_larghezza.clear()  # 11 - larghezza
        self.lineEdit_lunghezza.clear()  # 13 - lunghezza
        self.lineEdit_h.clear()  # 14 - h
        self.textEdit_descrizione.clear()  # 12 - descrizione
        self.textEdit_lavorazione_e_stato_di_conservazione.clear()  # 15 - lavorazione e stato...
        self.textEdit_confronti.clear()  # 16 - confronti
        self.lineEdit_cronologia.clear()  # 17 - cronologia
        self.lineEdit_compilatore.clear()  # 18 - compilatore

        for i in range(bibliografia_row_count):
            self.tableWidget_bibliografia.removeRow(0)
        self.insert_new_row("self.tableWidget_bibliografia")  # 19- bibliografia
    def empty_fields(self):
        bibliografia_row_count = self.tableWidget_bibliografia.rowCount()

        self.comboBox_sito.setEditText("")  # 1 - Sito
        self.lineEdit_num_inv.clear()  # 2 - num_inv
        self.lineEdit_collocazione.clear()  # 3 - collocazione
        self.comboBox_oggetto.setEditText("")  # 4 - oggetto
        self.comboBox_tipologia.setEditText("")  # 5 - tipologia
        self.comboBox_materiale.setEditText("")  # 9 - materiale
        self.lineEdit_d_letto_posa.clear()  # 6 - d_letto_posa
        self.lineEdit_d_letto_attesa.clear()  # 7 - d_letto_attesa
        self.lineEdit_toro.clear()  # 8 - toro
        self.lineEdit_spessore.clear()  # 10 - spessore
        self.lineEdit_larghezza.clear()  # 11 - larghezza
        self.lineEdit_lunghezza.clear()  # 13 - lunghezza
        self.lineEdit_h.clear()  # 14 - h
        self.textEdit_descrizione.clear()  # 12 - descrizione
        self.textEdit_lavorazione_e_stato_di_conservazione.clear()  # 15 - lavorazione e stato...
        self.textEdit_confronti.clear()  # 16 - confronti
        self.lineEdit_cronologia.clear()  # 17 - cronologia
        self.lineEdit_compilatore.clear()  # 18 - compilatore

        for i in range(bibliografia_row_count):
            self.tableWidget_bibliografia.removeRow(0)
        self.insert_new_row("self.tableWidget_bibliografia")  # 19- bibliografia

    def fill_fields(self, n=0):
        self.rec_num = n
        # QMessageBox.warning(self, "check fill fields", str(self.rec_num),  QMessageBox.Ok)
        try:
            str(self.comboBox_sito.setEditText(self.DATA_LIST[self.rec_num].sito))  # 1 - Sito
            self.lineEdit_num_inv.setText(str(self.DATA_LIST[self.rec_num].scheda_numero))  # 2 - scheda numero
            str(self.comboBox_tipologia.setEditText(self.DATA_LIST[self.rec_num].tipologia))  # 3 - tipologia
            str(self.comboBox_materiale.setEditText(self.DATA_LIST[self.rec_num].materiale))  # 4 - materiale
            str(self.comboBox_oggetto.setEditText(self.DATA_LIST[self.rec_num].oggetto))  # 5 - oggetto
            str(self.textEdit_descrizione.setText(self.DATA_LIST[self.rec_num].descrizione))  # 6 - descrizione
            str(self.textEdit_lavorazione_e_stato_di_conservazione.setText(
                self.DATA_LIST[self.rec_num].lavorazione_e_stato_di_conservazione))  # 6 - descrizione
            self.lineEdit_collocazione.setText(str(self.DATA_LIST[self.rec_num].collocazione))  # 2 - scheda numero
            self.lineEdit_compilatore.setText(str(self.DATA_LIST[self.rec_num].compilatore))  # 2 - scheda numero
            str(self.textEdit_confronti.setText(self.DATA_LIST[self.rec_num].confronti))  # 6 - descrizione
            self.lineEdit_cronologia.setText(str(self.DATA_LIST[self.rec_num].cronologia))  # 2 - scheda numero

            self.tableInsertData("self.tableWidget_bibliografia",
                                 self.DATA_LIST[self.rec_num].bibliografia)  # 8 - bibliografia

            if self.DATA_LIST[self.rec_num].d_letto_posa == None:  # 9 - d_letto_posa
                self.lineEdit_d_letto_posa.setText("")
            else:
                self.lineEdit_d_letto_posa.setText(str(self.DATA_LIST[self.rec_num].d_letto_posa))

            if self.DATA_LIST[self.rec_num].d_letto_attesa == None:  # 10 - d_letto_attesa
                self.lineEdit_d_letto_attesa.setText("")
            else:
                self.lineEdit_d_letto_attesa.setText(str(self.DATA_LIST[self.rec_num].d_letto_attesa))

            if self.DATA_LIST[self.rec_num].toro == None:  # 11 - toro
                self.lineEdit_toro.setText("")
            else:
                self.lineEdit_toro.setText(str(self.DATA_LIST[self.rec_num].toro))

            if self.DATA_LIST[self.rec_num].spessore == None:  # 12 - spessore
                self.lineEdit_spessore.setText("")
            else:
                self.lineEdit_spessore.setText(str(self.DATA_LIST[self.rec_num].spessore))

            if self.DATA_LIST[self.rec_num].larghezza == None:  # 13 - larghezza
                self.lineEdit_larghezza.setText("")
            else:
                self.lineEdit_larghezza.setText(str(self.DATA_LIST[self.rec_num].larghezza))

            if self.DATA_LIST[self.rec_num].lunghezza == None:  # 14 - lunghezza
                self.lineEdit_lunghezza.setText("")
            else:
                self.lineEdit_lunghezza.setText(str(self.DATA_LIST[self.rec_num].lunghezza))

            if self.DATA_LIST[self.rec_num].h == None:  # 15 - h
                self.lineEdit_h.setText("")
            else:
                self.lineEdit_h.setText(str(self.DATA_LIST[self.rec_num].h))

                ##########
        except :
            pass#QMessageBox.warning(self, "Errore Fill Fields", str(e), QMessageBox.Ok)

    def set_rec_counter(self, t, c):
        self.rec_tot = t
        self.rec_corr = c
        self.label_rec_tot.setText(str(self.rec_tot))
        self.label_rec_corrente.setText(str(self.rec_corr))

    def set_LIST_REC_TEMP(self):
        # TableWidget

        # bibliografia
        bibliografia = self.table2dict("self.tableWidget_bibliografia")

        ##Dimensioni
        if self.lineEdit_d_letto_posa.text() == "":
            d_letto_posa = None
        else:
            d_letto_posa = self.lineEdit_d_letto_posa.text()

        if self.lineEdit_d_letto_attesa.text() == "":
            d_letto_attesa = None
        else:
            d_letto_attesa = self.lineEdit_d_letto_attesa.text()

        if self.lineEdit_toro.text() == "":
            toro = None
        else:
            toro = self.lineEdit_toro.text()

        if self.lineEdit_spessore.text() == "":
            spessore = None
        else:
            spessore = self.lineEdit_spessore.text()

        if self.lineEdit_larghezza.text() == "":
            larghezza = None
        else:
            larghezza = self.lineEdit_larghezza.text()

        if self.lineEdit_lunghezza.text() == "":
            lunghezza = None
        else:
            lunghezza = self.lineEdit_lunghezza.text()

        if self.lineEdit_h.text() == "":
            h = None
        else:
            h = self.lineEdit_h.text()

            # data
        self.DATA_LIST_REC_TEMP = [
            str(self.comboBox_sito.currentText()),  # 1 - Sito
            str(self.lineEdit_num_inv.text()),  # 2 - num_inv
            str(self.lineEdit_collocazione.text()),  # 3 - collocazione
            str(self.comboBox_oggetto.currentText()),  # 4 - oggetto
            str(self.comboBox_tipologia.currentText()),  # 5 - tipologia
            str(self.comboBox_materiale.currentText()),  # 6 - materiale
            str(d_letto_posa),  # 8 - d_letto_posa
            str(d_letto_attesa),  # 9 - d_letto_attesa
            str(toro),  # 10 - toro
            str(spessore),  # 11 - spessore
            str(larghezza),  # 12 - larghezza
            str(lunghezza),  # 13 - lunghezza
            str(h),  # 14 - h
            str(self.textEdit_descrizione.toPlainText()),  # 15 - descrizione
            str(self.textEdit_lavorazione_e_stato_di_conservazione.toPlainText()),  # 16 - lavorazione
            str(self.textEdit_confronti.toPlainText()),  # 17 - confronti
            str(self.lineEdit_cronologia.text()),  # 18 - cronologia
            str(bibliografia),  # 19 - bibliografia
            str(self.lineEdit_compilatore.text()),  # 20 - compilatore
        ]

    def enable_button(self, n):
        self.pushButton_connect.setEnabled(n)

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
        self.pushButton_connect.setEnabled(n)

        self.pushButton_new_rec.setEnabled(n)

        self.pushButton_view_all_2.setEnabled(n)

        self.pushButton_first_rec.setEnabled(n)

        self.pushButton_last_rec.setEnabled(n)

        self.pushButton_prev_rec.setEnabled(n)

        self.pushButton_next_rec.setEnabled(n)

        self.pushButton_delete.setEnabled(n)

        self.pushButton_save.setEnabled(n)

        self.pushButton_sort.setEnabled(n)

    def setTableEnable(self, t, v):
        tab_names = t
        value = v

        for tn in tab_names:
            cmd = '{}{}{}{}'.format(tn, '.setEnabled(', v, ')')
            eval(cmd)

    def set_LIST_REC_CORR(self):
        self.DATA_LIST_REC_CORR = []
        for i in self.TABLE_FIELDS:
            self.DATA_LIST_REC_CORR.append(eval("unicode(self.DATA_LIST[self.REC_CORR]." + i + ")"))

    def records_equal_check(self):
        self.set_LIST_REC_TEMP()
        self.set_LIST_REC_CORR()

        # test

        # QMessageBox.warning(self, "ATTENZIONE", str(self.DATA_LIST_REC_CORR) + " temp " + str(self.DATA_LIST_REC_TEMP), QMessageBox.Ok)

        check_str = str(self.DATA_LIST_REC_CORR) + " " + str(self.DATA_LIST_REC_TEMP)

        if self.DATA_LIST_REC_CORR == self.DATA_LIST_REC_TEMP:
            return 0
        else:
            return 1

    def testing(self, name_file, message):
        f = open(str(name_file), 'w')
        f.write(str(message))
        f.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = pyarchinit_scheda_Lapidei()
    ui.show()
    sys.exit(app.exec_())
