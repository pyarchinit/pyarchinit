#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
/**************************************************************************
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
from builtins import range
from builtins import str
from qgis.PyQt.QtWidgets import QDialog, QMessageBox, QTableWidgetItem
from qgis.PyQt.uic import loadUiType
from qgis.core import QgsSettings
from ..modules.db.pyarchinit_conn_strings import Connection
from ..modules.db.pyarchinit_db_manager import Pyarchinit_db_management
from ..modules.db.pyarchinit_utility import Utility
from ..modules.gis.pyarchinit_pyqgis import Pyarchinit_pyqgis
#from ..modules.utility.pdf_models.pyarchinit_exp_Findssheet_pdf import generate_pdf
from ..modules.utility.pyarchinit_error_check import Error_check
from ..modules.utility.pyarchinit_exp_UTsheet_pdf import generate_pdf
from ..gui.sortpanelmain import SortPanelMain
from ..gui.pyarchinitConfigDialog import pyArchInitDialog_Config
MAIN_DIALOG_CLASS, _ = loadUiType(os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'UT_ui.ui'))


class pyarchinit_UT(QDialog, MAIN_DIALOG_CLASS):
    L=QgsSettings().value("locale/userLocale")[0:2]
    if L=='it':
        MSG_BOX_TITLE = "PyArchInit - Scheda UT"
    
    elif L=='de':
        MSG_BOX_TITLE = "PyArchInit - TEformular"
    else:
        MSG_BOX_TITLE = "PyArchInit - TU form" 
    DATA_LIST = []
    DATA_LIST_REC_CORR = []
    DATA_LIST_REC_TEMP = []
    REC_CORR = 0
    REC_TOT = 0
    SITO = pyArchInitDialog_Config
    if L=='it':
        STATUS_ITEMS = {"b": "Usa", "f": "Trova", "n": "Nuovo Record"}
    else :
        STATUS_ITEMS = {"b": "Current", "f": "Find", "n": "New Record"}
    BROWSE_STATUS = "b"
    SORT_MODE = 'asc'
    if L=='it':
        SORTED_ITEMS = {"n": "Non ordinati", "o": "Ordinati"}
    else:
        SORTED_ITEMS = {"n": "Not sorted", "o": "Sorted"}
    SORT_STATUS = "n"
    UTILITY = Utility()
    DB_MANAGER = ""
    TABLE_NAME = 'ut_table'
    MAPPER_TABLE_CLASS = "UT"
    NOME_SCHEDA = "Scheda UT"
    ID_TABLE = "id_ut"
    if L=='it':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            'Progetto': 'progetto',
            'numero UT': 'nr_ut',
            'UT letterale': 'ut_letterale',
            'Definizione UT': 'def_ut',
            'Descrizione UT': 'descrizione_ut',
            'Interpretazione UT': 'interpretazione_ut',
            'Nazione': 'nazione',
            'Regione': 'regione',
            'Provincia': 'provincia',
            'Comune': 'comune',
            'Frazione': 'frazione',
            'Localita': 'localita',
            'Indirizzo': 'indirizzo',
            'Nr civico': 'nr_civico',
            'Carta topografica IGM': 'carta_topo_igm',
            'CaCTR': 'carta_ctr',
            'Coord geografiche': 'coord_geografiche',
            'Coord piane': 'coord_piane',
            'Quota': 'quota',
            'Andamento terreno pendenza': 'andamento_terreno_pendenza',
            'Utilizzo suolo vegetazione': 'utilizzo_suolo_vegetazione',
            'Descrizione empirica suolo': 'descrizione_empirica_suolo',
            'Descrizione luogo': 'descrizione_luogo',
            'Metodo rilievo e ricognizione': 'metodo_rilievo_e_ricognizione',
            'Geometria': 'geometria',
            'Bibliografia': 'bibliografia',
            'Data': 'data',
            'Ora meteo': 'ora_meteo',
            'Responsabile': 'responsabile',
            'Dimensioni UT': 'dimensioni_ut',
            'Reperti per mq': 'rep_per_mq',
            'Reperti datanti': 'rep_datanti',
            'Periodo I': 'periodo_I',
            'Datazione_I': 'datazione_I',
            'Interpretazione I': 'interpretazione_I',
            'Periodo II': 'periodo_II',
            'Datazione II': 'datazione_II',
            'Interpretazione II': 'interpretazione_II',
            'Documentazione': 'documentazione',
            'Enti tutela_vincoli': 'enti_tutela_vincoli',
            'Indagini preliminari': 'indagini_preliminari'
        }
        SORT_ITEMS = [
            ID_TABLE,
            'Progetto',
            'numero UT',
            'UT letterale',
            'Definizione UT',
            'Descrizione UT',
            'Interpretazione UT',
            'Nazione',
            'Regione',
            'Provincia',
            'Comune',
            'Frazione',
            'Localita',
            'Indirizzo',
            'Nr civico',
            'Carta topografica IGM',
            'CaCTR',
            'Coord geografiche',
            'Coord piane',
            'Quota',
            'Andamento terreno pendenza',
            'Utilizzo suolo vegetazione',
            'Descrizione empirica suolo',
            'Descrizione luogo',
            'Metodo rilievo e ricognizione',
            'Geometria',
            'Bibliografia',
            'Data',
            'Ora meteo',
            'Responsabile',
            'Dimensioni UT',
            'Reperti per mq',
            'Reperti datanti',
            'Periodo I',
            'Datazione_I',
            'Interpretazione I',
            'Periodo II',
            'Datazione II',
            'Interpretazione II',
            'Documentazione',
            'Enti tutela_vincoli',
            'Indagini preliminari'
        ]
    elif L=='de':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            'Project': 'progetto',
            'TE nr.': 'nr_ut',
            'TEabc': 'ut_letterale',
            'Definition TE': 'def_ut',
            'Beschreibung TE': 'descrizione_ut',
            'Deutung TE': 'interpretazione_ut',
            'Nation': 'nazione',
            'Region': 'regione',
            'Provinz': 'provincia',
            'Stadt / Stadt': 'comune',
            'Landkreis': 'frazione',
            'Ort': 'localita',
            'Adresses': 'indirizzo',
            'Hausnummer': 'nr_civico',
            'Topographische Karte': 'carta_topo_igm',
            'CTR': 'carta_ctr',
            'Geographische Koordinaten': 'coord_geografiche',
            'Planum-Koordinaten': 'coord_piane',
            'Nivellement': 'quota',
            'Boden / Hang-Trend': 'andamento_terreno_pendenza',
            'Verwendung Boden / Vegetation': 'utilizzo_suolo_vegetazione',
            'Empirische Beschreibung des Bodens': 'descrizione_empirica_suolo',
            'Ortsbeschreibung': 'descrizione_luogo',
            'Survey u. Oberflächenbegehung': 'metodo_rilievo_e_ricognizione',
            'Geometrie': 'geometria',
            'Bibliographie': 'bibliografia',
            'Datum': 'data',
            'Zeit / Wetter': 'ora_meteo',
            'Verantwortlich': 'responsabile',
            'TE-Größe (MQ)': 'dimensioni_ut',
            'Findet für MQ': 'rep_per_mq',
            'Findet': 'rep_datanti',
            'Zeitraum I': 'periodo_I',
            'Dating_I': 'datazione_I',
            'Interpretation I': 'interpretazione_I',
            'Zeitraum II': 'periodo_II',
            'Dating II': 'datazione_II',
            'Interpretation II': 'interpretazione_II',
            'Dokumentation': 'documentazione',
            'Entitäten Schutz und Einschränkungen': 'enti_tutela_vincoli',
            'Voruntersuchungen': 'indagini_preliminari'
        }
        SORT_ITEMS = [
            ID_TABLE,
            'Project',
            'TE nr.',
            'TEabc',
            'Definition TE',
            'Beschreibung TE',
            'Deutung TE',
            'Nation',
            'Region',
            'Provinz',
            'Stadt / Stadt',
            'Landkreis',
            'Ort',
            'Adresses',
            'Hausnummer',
            'Topographische Karte',
            'CTR',
            'Geographische Koordinaten',
            'Planum-Koordinaten',
            'Nivellement',
            'Boden / Hang-Trend',
            'Verwendung Boden / Vegetation',
            'Empirische Beschreibung des Bodens',
            'Ortsbeschreibung',
            'Survey u. Oberflächenbegehung',
            'Geometrie',
            'Bibliographie',
            'Datum',
            'Zeit / Wetter',
            'Verantwortlich',
            'TE-Größe (MQ)',
            'Findet für MQ',
            'Findet',
            'Zeitraum I',
            'Dating_I',
            'Interpretation I',
            'Zeitraum II',
            'Dating II',
            'Interpretation II',
            'Dokumentation',
            'Entitäten Schutz und Einschränkungen',
            'Voruntersuchungen'
        ]
    else:
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            'Project': 'progetto',
            'TU nr.': 'nr_ut',
            'TUabc': 'ut_letterale',
            'TU definition': 'def_ut',
            'TU description': 'descrizione_ut',
            'TU interpretation': 'interpretazione_ut',
            'Nation': 'nazione',
            'Region': 'regione',
            'Province': 'provincia',
            'Town': 'comune',
            'Hamlet': 'frazione',
            'Location': 'localita',
            'Adress': 'indirizzo',
            'Nr civic': 'nr_civico',
            'Topographic map': 'carta_topo_igm',
            'CTR': 'carta_ctr',
            'Coord geogr': 'coord_geografiche',
            'Coord plane': 'coord_piane',
            'Elevation': 'quota',
            'Slop trend': 'andamento_terreno_pendenza',
            'Use vegetation soil': 'utilizzo_suolo_vegetazione',
            'Description soil': 'descrizione_empirica_suolo',
            'Description place': 'descrizione_luogo',
            'Survey': 'metodo_rilievo_e_ricognizione',
            'Geometry': 'geometria',
            'Bibliografphy': 'bibliografia',
            'Date': 'data',
            'Meteo time': 'ora_meteo',
            'Responsable': 'responsabile',
            'TU dimension': 'dimensioni_ut',
            'Finds for square meter': 'rep_per_mq',
            'Finds': 'rep_datanti',
            'Period I': 'periodo_I',
            'Datation I': 'datazione_I',
            'Interpretation I': 'interpretazione_I',
            'Period II': 'periodo_II',
            'Datation II': 'datazione_II',
            'Interpretation II': 'interpretazione_II',
            'Documentation': 'documentazione',
            'Company fconstraints': 'enti_tutela_vincoli',
            'Preliminary investigation': 'indagini_preliminari'
        }
        SORT_ITEMS = [
            ID_TABLE,
            'Project',
            'TU nr.',
            'TUabc',
            'TU definition',
            'TU description',
            'TU interpretation',
            'Nation',
            'Region',
            'Province',
            'Town',
            'Hamlet',
            'Location',
            'Adress',
            'Nr civic',
            'Topographic map',
            'CTR',
            'Coord geogr',
            'Coord plane',
            'Elevation',
            'Slop trend',
            'Use vegetation soil',
            'Description soil',
            'Description place',
            'Survey',
            'Geometry',
            'Bibliografphy',
            'Date',
            'Meteo time',
            'Responsable',
            'TU dimension',
            'Finds for square meter',
            'Finds',
            'Period I',
            'Datation I',
            'Interpretation I',
            'Period II',
            'Datation II',
            'Interpretation II',
            'Documentation',
            'Company constraints',
            'Preliminary investigation'
        ]   
    TABLE_FIELDS = [
        'progetto',
        'nr_ut',
        'ut_letterale',
        'def_ut',
        'descrizione_ut',
        'interpretazione_ut',
        'nazione',
        'regione',
        'provincia',
        'comune',
        'frazione',
        'localita',
        'indirizzo',
        'nr_civico',
        'carta_topo_igm',
        'carta_ctr',
        'coord_geografiche',
        'coord_piane',
        'quota',
        'andamento_terreno_pendenza',
        'utilizzo_suolo_vegetazione',
        'descrizione_empirica_suolo',
        'descrizione_luogo',
        'metodo_rilievo_e_ricognizione',
        'geometria',
        'bibliografia',
        'data',
        'ora_meteo',
        'responsabile',
        'dimensioni_ut',
        'rep_per_mq',
        'rep_datanti',
        'periodo_I',
        'datazione_I',
        'interpretazione_I',
        'periodo_II',
        'datazione_II',
        'interpretazione_II',
        'documentazione',
        'enti_tutela_vincoli',
        'indagini_preliminari'
    ]

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
            QMessageBox.warning(self, "Connection system", str(e), QMessageBox.Ok)
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

        self.pushButton_insert_row_documentazione.setEnabled(n)
        self.pushButton_remove_row_documentazione.setEnabled(n)

        self.pushButton_insert_row_bibliografia.setEnabled(n)
        self.pushButton_remove_row_bibliografia.setEnabled(n)

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
                    
                    QMessageBox.warning(self,"WILLKOMMEN","WILLKOMMEN in pyArchInit" + "Munsterformular"+ ". Die Datenbank ist leer. Tippe 'Ok' und aufgehts!",
                                        QMessageBox.Ok) 
                else:
                    QMessageBox.warning(self,"WELCOME", "Welcome in pyArchInit" + "Samples form" + ". The DB is empty. Push 'Ok' and Good Work!",
                                        QMessageBox.Ok)    
                self.charge_list()
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
        self.tableWidget_bibliografia.setColumnWidth(0, 380)

        self.tableWidget_documentazione.setColumnWidth(0, 150)
        self.tableWidget_documentazione.setColumnWidth(1, 300)

    def charge_list(self):
        # lista sito
        sito_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('site_table', 'progetto', 'SITE'))
        try:
            sito_vl.remove('')
        except Exception as e:
            if str(e) == "list.remove(x): x not in list":
                pass
            else:
                if self.L=='it':
                    QMessageBox.warning(self, "Messaggio", "Sistema di aggiornamento lista Sito: " + str(e), QMessageBox.Ok)
                
                elif self.L=='de':
                    QMessageBox.warning(self, "Nachricht", "Aktualisierungssystem für die Ausgrabungstätte: " + str(e), QMessageBox.Ok)
                    
                else:
                    QMessageBox.warning(self, "Message", "Site list update system: " + str(e), QMessageBox.Ok)

        self.comboBox_progetto.clear()

        sito_vl.sort()
        self.comboBox_progetto.addItems(sito_vl)

        regioni_list = ['Abruzzo', 'Basilicata', 'Calabria', 'Campania', 'Emilia-Romagna', 'Friuli Venezia Giulia',
                        'Lazio', 'Liguria', 'Lombardia', 'Marche', 'Molise', 'Piemonte', 'Puglia', 'Sardegna',
                        'Sicilia', 'Toscana', 'Trentino Alto Adige', 'Umbria', 'Valle d\'Aosta', 'Veneto']
        self.comboBox_regione.clear()
        self.comboBox_regione.addItems(regioni_list)

        province_list = ['Agrigento', 'Alessandria', 'Ancona', 'Aosta', 'Arezzo', 'Ascoli Piceno', 'Asti', 'Avellino',
                         'Bari', 'Barletta-Andria-Trani', 'Basilicata', 'Belluno', 'Benevento', 'Bergamo', 'Biella',
                         'Bologna', 'Bolzano', 'Brescia', 'Brindisi', 'Cagliari', 'Calabria', 'Caltanissetta',
                         'Campania', 'Campobasso', 'Carbonia-Iglesias', 'Caserta', 'Catania', 'Catanzaro', 'Chieti',
                         'Como', 'Cosenza', 'Cremona', 'Crotone', 'Cuneo', 'Emilia-Romagna', 'Enna', 'Fermo', 'Ferrara',
                         'Firenze', 'Foggia', "Forl'-Cesena", 'Frosinone', 'Genova', 'Gorizia', 'Grosseto', 'Imperia',
                         'Isernia', "L'Aquila", 'La Spezia', 'Latina', 'Lecce', 'Lecco', 'Livorno', 'Lodi', 'Lucca',
                         'Macerata', 'Mantova', 'Massa e Carrara', 'Matera', 'Medio Campidano', 'Messina', 'Milano',
                         'Modena', 'Monza e Brianza', 'Napoli', 'Novara', 'Nuoro', 'Ogliastra', 'Olbia-Tempio',
                         'Oristano', 'Padova', 'Palermo', 'Parma', 'Pavia', 'Perugia', 'Pesaro e Urbino', 'Pescara',
                         'Piacenza', 'Pisa', 'Pistoia', 'Pordenone', 'Potenza', 'Prato', 'Ragusa', 'Ravenna',
                         'Reggio Calabria', 'Reggio Emilia', 'Rieti', 'Rimini', 'Roma', 'Rovigo', 'Salerno', 'Sassari',
                         'Savona', 'Siena', 'Siracusa', 'Sondrio', 'Taranto', 'Teramo', 'Terni', 'Torino', 'Trapani',
                         'Trento', 'Treviso', 'Trieste', 'Udine', 'Varese', 'Venezia', 'Verbano-Cusio-Ossola',
                         'Vercelli', 'Verona', 'Vibo Valentia', 'Vicenza', 'Viterbo']
        self.comboBox_provincia.clear()
        self.comboBox_provincia.addItems(province_list)

    # buttons functions
    def msg_sito(self):
        conn = Connection()
        
        sito_set= conn.sito_set()
        sito_set_str = sito_set['sito_set']
        
        if bool(self.comboBox_progetto.currentText()) and self.comboBox_progetto.currentText()==sito_set_str:
            QMessageBox.information(self, "OK" ,"Sei connesso al sito: %s" % str(sito_set_str),QMessageBox.Ok) 
       
        elif sito_set_str=='':    
            QMessageBox.information(self, "Attenzione" ,"Non hai settato alcun sito pertanto vedrai tutti i record se il db non è vuoto",QMessageBox.Ok) 
    
    
    def set_sito(self):
        conn = Connection()
            
        sito_set= conn.sito_set()
        sito_set_str = sito_set['sito_set']
        
        try:
            if bool (sito_set_str):
                
                
            
           
            
                search_dict = {
                    'progetto': "'" + str(sito_set_str) + "'"}  # 1 - Sito
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

                self.setComboBoxEnable(["self.comboBox_progetto"], "False")
                
            else:
                
                pass#
                
        except:
            QMessageBox.information(self, "Attenzione" ,"Non esiste questo sito: "'"'+ str(sito_set_str) +'"'" in questa scheda, Per favore distattiva la 'scelta sito' dalla scheda di configurazione plugin per vedere tutti i record oppure crea la scheda",QMessageBox.Ok) 
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
            self.BROWSE_STATUS = "n"
            self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
            self.empty_fields()

            self.setComboBoxEditable(["self.comboBox_progetto"], 1)
            self.setComboBoxEditable(["self.comboBox_nr_ut"], 1)
            self.setComboBoxEnable(["self.comboBox_progetto"], "True")
            self.setComboBoxEnable(["self.comboBox_nr_ut"], "True")
            self.setComboBoxEnable(["self.lineEdit_ut_letterale"], "True")
            ###
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
                    self.label_sort.setText(self.SORTED_ITEMS["n"])
                    self.charge_list()
                    self.set_sito()
                    self.charge_records()
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), len(self.DATA_LIST) - 1
                    self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)

                    self.setComboBoxEditable(["self.comboBox_progetto"], 1)
                    self.setComboBoxEditable(["self.comboBox_nr_ut"], 1)
                    self.setComboBoxEnable(["self.comboBox_progetto"], "False")
                    self.setComboBoxEnable(["self.comboBox_nr_ut"], "False")
                    self.setComboBoxEnable(["self.lineEdit_ut_letterale"], "False")
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
            if EC.data_is_empty(str(self.comboBox_progetto.currentText())) == 0:
                QMessageBox.warning(self, "ATTENZIONE", "Campo Progetto. \n Il campo non deve essere vuoto", QMessageBox.Ok)
                test = 1

            if EC.data_is_empty(str(self.comboBox_nr_ut.currentText())) == 0:
                QMessageBox.warning(self, "ATTENZIONE", "Campo UT. \n Il campo non deve essere vuoto", QMessageBox.Ok)
                test = 1

            nr_ut = self.comboBox_nr_ut.currentText()

            if nr_ut != "":
                if EC.data_is_int(nr_ut) == 0:
                    QMessageBox.warning(self, "ATTENZIONE", "Campo Nr UT. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

            return test
            
        elif self.L=='de':
            if EC.data_is_empty(str(self.comboBox_progetto.currentText())) == 0:
                QMessageBox.warning(self,  "ACHTUNG", " Feld Project \n Das Feld darf nicht leer sein", QMessageBox.Ok)
                test = 1

            if EC.data_is_empty(str(self.comboBox_nr_ut.currentText())) == 0:
                QMessageBox.warning(self,  "ACHTUNG", " Feld TE \n Das Feld darf nicht leer sein", QMessageBox.Ok)
                test = 1

            nr_ut = self.comboBox_nr_ut.currentText()

            if nr_ut != "":
                if EC.data_is_int(nr_ut) == 0:
                    QMessageBox.warning(self, "ACHTUNG", "Feld Nr. TE \n Der Wert muss numerisch eingegeben werden",
                                        QMessageBox.Ok)
                    test = 1

            return test
        else:
            if EC.data_is_empty(str(self.comboBox_progetto.currentText())) == 0:
                QMessageBox.warning(self, "WARNING", "Project Field. \n The field must not be empty", QMessageBox.Ok)
                test = 1

            if EC.data_is_empty(str(self.comboBox_nr_ut.currentText())) == 0:
                QMessageBox.warning(self, "WARNING", "TU Field. \n The field must not be empty", QMessageBox.Ok)
                test = 1

            nr_ut = self.comboBox_nr_ut.currentText()

            if nr_ut != "":
                if EC.data_is_int(nr_ut) == 0:
                    QMessageBox.warning(self, "WARNING", "TU nr. Field. \n The value must be numerical",
                                        QMessageBox.Ok)
                    test = 1

            return test 
    def insert_new_rec(self):
        if self.lineEdit_quota.text() == "":
            quota = None
        else:
            quota = float(self.lineEdit_quota.text())

        ##Documentazione
        documentazione = self.table2dict("self.tableWidget_documentazione")
        ##Bibliografia
        bibliografia = self.table2dict("self.tableWidget_bibliografia")
        try:
            data = self.DB_MANAGER.insert_ut_values(
                self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, self.ID_TABLE) + 1,
                str(self.comboBox_progetto.currentText()),
                int(self.comboBox_nr_ut.currentText()),
                str(self.lineEdit_ut_letterale.text()),
                str(self.lineEdit_def_ut.text()),
                str(self.textEdit_descrizione_ut.toPlainText()),
                str(self.textEdit_interpretazione_ut.toPlainText()),
                str(self.comboBox_nazione.currentText()),
                str(self.comboBox_regione.currentText()),
                str(self.comboBox_provincia.currentText()),
                str(self.comboBox_comune.currentText()),
                str(self.comboBox_frazione.currentText()),
                str(self.comboBox_localita.currentText()),
                str(self.lineEdit_indirizzo.text()),
                str(self.lineEdit_nr_civico.text()),
                str(self.lineEdit_carta_topo_igm.text()),
                str(self.lineEdit_carta_ctr.text()),
                str(self.lineEdit_coord_geografiche.text()),
                str(self.lineEdit_coord_piane.text()),
                quota,
                str(self.lineEdit_andamento_terreno_pendenza.text()),
                str(self.lineEdit_utilizzo_suolo_vegetazione.text()),
                str(self.textEdit_descrizione_empirica_suolo.toPlainText()),
                str(self.textEdit_descrizione_luogo.toPlainText()),
                str(self.lineEdit_metodo_rilievo_e_ricognizione.text()),
                str(self.lineEdit_geometria.text()),
                str(bibliografia),
                str(self.lineEdit_data.text()),
                str(self.lineEdit_ora_meteo.text()),
                str(self.lineEdit_responsabile.text()),
                str(self.lineEdit_dimensioni_ut.text()),
                str(self.lineEdit_rep_per_mq.text()),
                str(self.lineEdit_rep_datanti.text()),
                str(self.lineEdit_periodo_I.text()),
                str(self.lineEdit_datazione_I.text()),
                str(self.lineEdit_interpretazione_I.text()),
                str(self.lineEdit_periodo_II.text()),
                str(self.lineEdit_datazione_II.text()),
                str(self.lineEdit_interpretazione_II.text()),
                str(documentazione),
                str(self.lineEdit_enti_tutela_vincoli.text()),
                str(self.lineEdit_indagini_preliminari.text()))
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

    def insert_new_row(self, table_name):
        """insert new row into a table based on table_name"""
        cmd = table_name + ".insertRow(0)"
        eval(cmd)

    def remove_row(self, table_name):
        """remove row into a table based on table_name"""
        cmd = table_name + ".removeRow(0)"
        eval(cmd)

    def on_pushButton_insert_row_documentazione_pressed(self):
        self.insert_new_row('self.tableWidget_documentazione')

    def on_pushButton_remove_row_documentazione_pressed(self):
        self.remove_row('self.tableWidget_documentazione')

    def on_pushButton_insert_row_bibliografia_pressed(self):
        self.insert_new_row('self.tableWidget_bibliografia')

    def on_pushButton_remove_row_bibliografia_pressed(self):
        self.remove_row('self.tableWidget_bibliografia')

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
        try:
            self.empty_fields()
            self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
            self.fill_fields(0)
            self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
        except Exception as e:
            QMessageBox.warning(self, "Error/", str(e), QMessageBox.Ok)

    def on_pushButton_last_rec_pressed(self):
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
        try:
            self.empty_fields()
            self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), len(self.DATA_LIST) - 1
            self.fill_fields(self.REC_CORR)
            self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
        except Exception as e:
            QMessageBox.warning(self, "Errore", str(e), QMessageBox.Ok)

    def on_pushButton_prev_rec_pressed(self):
        if self.check_record_state() == 1:
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

            # set the GUI for a new search
            if self.BROWSE_STATUS != "f":
                self.BROWSE_STATUS = "f"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.empty_fields()
                self.set_rec_counter('', '')
                self.label_sort.setText(self.SORTED_ITEMS["n"])
                self.setComboBoxEditable(["self.comboBox_progetto"], 1)
                self.setComboBoxEditable(["self.comboBox_nr_ut"], 1)
                self.setComboBoxEnable(["self.comboBox_progetto"], "True")
                self.setComboBoxEnable(["self.comboBox_nr_ut"], "True")
                self.setComboBoxEnable(["self.lineEdit_ut_letterale"], "True")

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
            if self.comboBox_nr_ut.currentText() != "":
                nr_ut = int(self.comboBox_nr_ut.currentText())
            else:
                nr_ut = None

            if self.comboBox_nr_ut.currentText() != "":
                nr_ut = float(self.comboBox_nr_ut.currentText())
            else:
                nr_ut = None

            if self.lineEdit_quota.text() != "":
                quota = float(self.lineEdit_quota.text())
            else:
                quota = None

            search_dict = {
                self.TABLE_FIELDS[0]: "'" + str(self.comboBox_progetto.currentText()) + "'",  # 1 - Sito
                self.TABLE_FIELDS[1]: nr_ut,  # 2 - Area
                self.TABLE_FIELDS[2]: "'" + str(self.lineEdit_ut_letterale.text()) + "'",  # 3 - US
                self.TABLE_FIELDS[3]: "'" + str(self.lineEdit_def_ut.text()) + "'",  # 6 - descrizione
                self.TABLE_FIELDS[6]: "'" + str(self.comboBox_nazione.currentText()) + "'",
                self.TABLE_FIELDS[7]: "'" + str(self.comboBox_regione.currentText()) + "'",  # 7 - interpretazione
                self.TABLE_FIELDS[8]: "'" + str(self.comboBox_provincia.currentText()) + "'",  # 8 - periodo iniziale
                self.TABLE_FIELDS[9]: "'" + str(self.comboBox_comune.currentText()) + "'",  # 9 - fase iniziale
                self.TABLE_FIELDS[10]: "'" + str(self.comboBox_frazione.currentText()) + "'",
                # 10 - periodo finale iniziale
                self.TABLE_FIELDS[11]: "'" + str(self.comboBox_localita.currentText()) + "'",  # 11 - fase finale
                self.TABLE_FIELDS[12]: "'" + str(self.lineEdit_indirizzo.text()) + "'",  # 12 - attivita
                self.TABLE_FIELDS[13]: "'" + str(self.lineEdit_nr_civico.text()) + "'",  # 13 - attivita
                self.TABLE_FIELDS[14]: "'" + str(self.lineEdit_carta_topo_igm.text()) + "'",  # 15 - metodo
                self.TABLE_FIELDS[15]: "'" + str(self.lineEdit_carta_ctr.text()) + "'",  # 16 - data schedatura
                self.TABLE_FIELDS[16]: "'" + str(self.lineEdit_coord_geografiche.text()) + "'",  # 17 - schedatore
                self.TABLE_FIELDS[17]: "'" + str(self.lineEdit_coord_piane.text()) + "'",  # 18 - formazione
                self.TABLE_FIELDS[18]: quota,  # 19 - conservazione
                self.TABLE_FIELDS[19]: "'" + str(self.lineEdit_andamento_terreno_pendenza.text()) + "'",  # 20 - colore
                self.TABLE_FIELDS[20]: "'" + str(self.lineEdit_utilizzo_suolo_vegetazione.text()) + "'",
                # 21 - consistenza
                self.TABLE_FIELDS[23]: "'" + str(self.lineEdit_metodo_rilievo_e_ricognizione.text()) + "'",
                # 23 - codice_periodo
                self.TABLE_FIELDS[24]: "'" + str(self.lineEdit_geometria.text()) + "'",
                self.TABLE_FIELDS[26]: "'" + str(self.lineEdit_data.text()) + "'",
                self.TABLE_FIELDS[27]: "'" + str(self.lineEdit_ora_meteo.text()) + "'",
                self.TABLE_FIELDS[28]: "'" + str(self.lineEdit_responsabile.text()) + "'",
                self.TABLE_FIELDS[29]: "'" + str(self.lineEdit_dimensioni_ut.text()) + "'",
                self.TABLE_FIELDS[30]: "'" + str(self.lineEdit_rep_per_mq.text()) + "'",
                self.TABLE_FIELDS[31]: "'" + str(self.lineEdit_rep_datanti.text()) + "'",
                self.TABLE_FIELDS[32]: "'" + str(self.lineEdit_periodo_I.text()) + "'",
                self.TABLE_FIELDS[33]: "'" + str(self.lineEdit_datazione_I.text()) + "'",
                self.TABLE_FIELDS[34]: "'" + str(self.lineEdit_interpretazione_I.text()) + "'",
                self.TABLE_FIELDS[35]: "'" + str(self.lineEdit_periodo_II.text()) + "'",
                self.TABLE_FIELDS[36]: "'" + str(self.lineEdit_datazione_II.text()) + "'",
                self.TABLE_FIELDS[37]: "'" + str(self.lineEdit_interpretazione_II.text()) + "'",
                self.TABLE_FIELDS[39]: "'" + str(self.lineEdit_enti_tutela_vincoli.text()) + "'",
                self.TABLE_FIELDS[40]: "'" + str(self.lineEdit_indagini_preliminari.text()) + "'"  # 24 - codice_periodo
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

                        self.setComboBoxEnable(["self.comboBox_progetto"], "False")
                        self.setComboBoxEnable(["self.comboBox_nr_ut"], "False")
                        self.setComboBoxEnable(["self.lineEdit_ut_letterale"], "False")

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

                    self.setComboBoxEnable(["self.comboBox_progetto"], "False")
                    self.setComboBoxEnable(["self.comboBox_nr_ut"], "False")
                    self.setComboBoxEnable(["self.lineEdit_ut_letterale"], "False")

                    QMessageBox.warning(self, "Message", "%s %d %s" % strings, QMessageBox.Ok)

        self.enable_button_search(1)

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

    def empty_fields(self):
        documentazione_row_count = self.tableWidget_documentazione.rowCount()
        bibliografia_row_count = self.tableWidget_bibliografia.rowCount()

        self.comboBox_progetto.setEditText("")
        self.comboBox_nr_ut.setEditText("")
        self.lineEdit_ut_letterale.clear()
        self.lineEdit_def_ut.clear()
        self.textEdit_descrizione_ut.clear()
        self.textEdit_interpretazione_ut.clear()
        self.comboBox_nazione.setEditText("")
        self.comboBox_regione.setEditText("")
        self.comboBox_provincia.setEditText("")
        self.comboBox_comune.setEditText("")
        self.comboBox_frazione.setEditText("")
        self.comboBox_localita.setEditText("")
        self.lineEdit_indirizzo.clear()
        self.lineEdit_nr_civico.clear()
        self.lineEdit_carta_topo_igm.clear()
        self.lineEdit_carta_ctr.clear()
        self.lineEdit_coord_geografiche.clear()
        self.lineEdit_coord_piane.clear()
        self.lineEdit_quota.clear()
        self.lineEdit_andamento_terreno_pendenza.clear()
        self.lineEdit_utilizzo_suolo_vegetazione.clear()
        self.textEdit_descrizione_empirica_suolo.clear()
        self.textEdit_descrizione_luogo.clear()
        self.lineEdit_metodo_rilievo_e_ricognizione.clear()
        self.lineEdit_geometria.clear()
        for i in range(documentazione_row_count):
            self.tableWidget_documentazione.removeRow(0)
        for i in range(bibliografia_row_count):
            self.tableWidget_bibliografia.removeRow(0)
        self.lineEdit_data.clear()
        self.lineEdit_ora_meteo.clear()
        self.lineEdit_responsabile.clear()
        self.lineEdit_dimensioni_ut.clear()
        self.lineEdit_rep_per_mq.clear()
        self.lineEdit_rep_datanti.clear()
        self.lineEdit_periodo_I.clear()
        self.lineEdit_datazione_I.clear()
        self.lineEdit_interpretazione_I.clear()
        self.lineEdit_periodo_II.clear()
        self.lineEdit_datazione_II.clear()
        self.lineEdit_interpretazione_II.clear()
        self.lineEdit_enti_tutela_vincoli.clear()
        self.lineEdit_indagini_preliminari.clear()

    def fill_fields(self, n=0):
        self.rec_num = n

        try:
            if self.DATA_LIST[self.rec_num].quota == None:
                self.lineEdit_quota.setText("")
            else:
                self.lineEdit_quota.setText(str(self.DATA_LIST[self.rec_num].quota))

            self.comboBox_progetto.setEditText(self.DATA_LIST[self.rec_num].progetto)
            self.comboBox_nr_ut.setEditText(str(self.DATA_LIST[self.rec_num].nr_ut))
            self.lineEdit_ut_letterale.setText(self.DATA_LIST[self.rec_num].ut_letterale)
            self.lineEdit_def_ut.setText(self.DATA_LIST[self.rec_num].def_ut)
            str(self.textEdit_descrizione_ut.setText(self.DATA_LIST[self.rec_num].descrizione_ut))
            str(self.textEdit_interpretazione_ut.setText(self.DATA_LIST[self.rec_num].interpretazione_ut))
            self.comboBox_nazione.setEditText(self.DATA_LIST[self.rec_num].nazione)
            self.comboBox_regione.setEditText(self.DATA_LIST[self.rec_num].regione)
            self.comboBox_provincia.setEditText(self.DATA_LIST[self.rec_num].provincia)
            self.comboBox_comune.setEditText(self.DATA_LIST[self.rec_num].comune)
            self.comboBox_frazione.setEditText(self.DATA_LIST[self.rec_num].frazione)
            self.comboBox_localita.setEditText(self.DATA_LIST[self.rec_num].localita)
            self.lineEdit_indirizzo.setText(self.DATA_LIST[self.rec_num].indirizzo)
            self.lineEdit_nr_civico.setText(self.DATA_LIST[self.rec_num].nr_civico)
            self.lineEdit_carta_topo_igm.setText(self.DATA_LIST[self.rec_num].carta_topo_igm)
            self.lineEdit_carta_ctr.setText(self.DATA_LIST[self.rec_num].carta_ctr)
            self.lineEdit_coord_geografiche.setText(self.DATA_LIST[self.rec_num].coord_geografiche)
            self.lineEdit_coord_piane.setText(self.DATA_LIST[self.rec_num].coord_piane)
            self.lineEdit_andamento_terreno_pendenza.setText(self.DATA_LIST[self.rec_num].andamento_terreno_pendenza)
            self.lineEdit_utilizzo_suolo_vegetazione.setText(self.DATA_LIST[self.rec_num].utilizzo_suolo_vegetazione)
            str(self.textEdit_descrizione_empirica_suolo.setText(
                self.DATA_LIST[self.rec_num].descrizione_empirica_suolo))
            str(self.textEdit_descrizione_luogo.setText(self.DATA_LIST[self.rec_num].descrizione_luogo))
            self.lineEdit_metodo_rilievo_e_ricognizione.setText(
                self.DATA_LIST[self.rec_num].metodo_rilievo_e_ricognizione)
            self.lineEdit_geometria.setText(self.DATA_LIST[self.rec_num].geometria)
            self.tableInsertData("self.tableWidget_documentazione",
                                 self.DATA_LIST[self.rec_num].documentazione)  # 19 - rapporti
            self.tableInsertData("self.tableWidget_bibliografia",
                                 self.DATA_LIST[self.rec_num].bibliografia)  # 19 - rapporti
            self.lineEdit_data.setText(self.DATA_LIST[self.rec_num].data)
            self.lineEdit_ora_meteo.setText(self.DATA_LIST[self.rec_num].ora_meteo)
            self.lineEdit_responsabile.setText(self.DATA_LIST[self.rec_num].responsabile)
            self.lineEdit_dimensioni_ut.setText(self.DATA_LIST[self.rec_num].dimensioni_ut)
            self.lineEdit_rep_per_mq.setText(self.DATA_LIST[self.rec_num].rep_per_mq)
            self.lineEdit_rep_datanti.setText(self.DATA_LIST[self.rec_num].rep_datanti)
            self.lineEdit_periodo_I.setText(self.DATA_LIST[self.rec_num].periodo_I)
            self.lineEdit_datazione_I.setText(self.DATA_LIST[self.rec_num].datazione_I)
            self.lineEdit_interpretazione_I.setText(self.DATA_LIST[self.rec_num].interpretazione_I)
            self.lineEdit_periodo_II.setText(self.DATA_LIST[self.rec_num].periodo_II)
            self.lineEdit_datazione_II.setText(self.DATA_LIST[self.rec_num].datazione_II)
            self.lineEdit_interpretazione_II.setText(self.DATA_LIST[self.rec_num].interpretazione_II)
            self.lineEdit_enti_tutela_vincoli.setText(self.DATA_LIST[self.rec_num].enti_tutela_vincoli)
            self.lineEdit_indagini_preliminari.setText(self.DATA_LIST[self.rec_num].indagini_preliminari)
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e), QMessageBox.Ok)

    def set_rec_counter(self, t, c):
        self.rec_tot = t
        self.rec_corr = c
        self.label_rec_tot.setText(str(self.rec_tot))
        self.label_rec_corrente.setText(str(self.rec_corr))

    def set_LIST_REC_TEMP(self):

        ##quota
        if self.lineEdit_quota.text() == "":
            quota = None
        else:
            quota = self.lineEdit_quota.text()

        documentazione = self.table2dict("self.tableWidget_documentazione")
        bibliografia = self.table2dict("self.tableWidget_bibliografia")

        # data
        self.DATA_LIST_REC_TEMP = [
            str(self.comboBox_progetto.currentText()),
            str(self.comboBox_nr_ut.currentText()),
            str(self.lineEdit_ut_letterale.text()),
            str(self.lineEdit_def_ut.text()),
            str(self.textEdit_descrizione_ut.toPlainText()),
            str(self.textEdit_interpretazione_ut.toPlainText()),
            str(self.comboBox_nazione.currentText()),
            str(self.comboBox_regione.currentText()),
            str(self.comboBox_provincia.currentText()),
            str(self.comboBox_comune.currentText()),
            str(self.comboBox_frazione.currentText()),
            str(self.comboBox_localita.currentText()),
            str(self.lineEdit_indirizzo.text()),
            str(self.lineEdit_nr_civico.text()),
            str(self.lineEdit_carta_topo_igm.text()),
            str(self.lineEdit_carta_ctr.text()),
            str(self.lineEdit_coord_geografiche.text()),
            str(self.lineEdit_coord_piane.text()),
            str(quota),
            str(self.lineEdit_andamento_terreno_pendenza.text()),
            str(self.lineEdit_utilizzo_suolo_vegetazione.text()),
            str(self.textEdit_descrizione_empirica_suolo.toPlainText()),
            str(self.textEdit_descrizione_luogo.toPlainText()),
            str(self.lineEdit_metodo_rilievo_e_ricognizione.text()),
            str(self.lineEdit_geometria.text()),
            str(bibliografia),
            str(self.lineEdit_data.text()),
            str(self.lineEdit_ora_meteo.text()),
            str(self.lineEdit_responsabile.text()),
            str(self.lineEdit_dimensioni_ut.text()),
            str(self.lineEdit_rep_per_mq.text()),
            str(self.lineEdit_rep_datanti.text()),
            str(self.lineEdit_periodo_I.text()),
            str(self.lineEdit_datazione_I.text()),
            str(self.lineEdit_interpretazione_I.text()),
            str(self.lineEdit_periodo_II.text()),
            str(self.lineEdit_datazione_II.text()),
            str(self.lineEdit_interpretazione_II.text()),
            str(documentazione),
            str(self.lineEdit_enti_tutela_vincoli.text()),
            str(self.lineEdit_indagini_preliminari.text())]  # 4 - provincia

    def set_LIST_REC_CORR(self):
        self.DATA_LIST_REC_CORR = []
        for i in self.TABLE_FIELDS:
            self.DATA_LIST_REC_CORR.append(eval("str(self.DATA_LIST[self.REC_CORR]." + i + ")"))
            ##self.testing('/testrecorr.txt',str(self.DATA_LIST_REC_CORR))

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
        # self.testing('/testup.txt',str(self.DATA_LIST_REC_TEMP))
        # self.testing('/testup2.txt',str(rec_to_update))
        return rec_to_update

    def records_equal_check(self):
        self.set_LIST_REC_TEMP()
        self.set_LIST_REC_CORR()

        if self.DATA_LIST_REC_CORR == self.DATA_LIST_REC_TEMP:
            return 0
        else:
            return 1

    def on_pushButton_pdf_exp_pressed(self):
        if self.L=='it':
            UT_pdf_sheet = generate_pdf()
            data_list = self.generate_list_pdf()
            UT_pdf_sheet.build_UT_sheets(data_list)
        elif self.L=='de':
            UT_pdf_sheet = generate_pdf()
            data_list = self.generate_list_pdf()
            UT_pdf_sheet.build_UT_sheets_de(data_list)
        else:
            UT_pdf_sheet = generate_pdf()
            data_list = self.generate_list_pdf()
            UT_pdf_sheet.build_UT_sheets_en(data_list)  
    def generate_list_pdf(self):
        data_list = []
        for i in range(len(self.DATA_LIST)):
            data_list.append([
                str(self.DATA_LIST[i].progetto),  # 1 - Sito
                str(self.DATA_LIST[i].nr_ut),  # 2 - Area
                str(self.DATA_LIST[i].ut_letterale),  # 3 - US
                str(self.DATA_LIST[i].def_ut),  # 4 - Definizione stratigrafica
                str(self.DATA_LIST[i].descrizione_ut),  # 5 - Definizione intepretata
                str(self.DATA_LIST[i].interpretazione_ut),  # 6 - descrizione
                str(self.DATA_LIST[i].nazione),  # 7 - interpretazione
                str(self.DATA_LIST[i].regione),  # 8 - periodo iniziale
                str(self.DATA_LIST[i].provincia),  # 9 - fase iniziale
                str(self.DATA_LIST[i].comune),  # 10 - periodo finale iniziale
                str(self.DATA_LIST[i].frazione),  # 11 - fase finale
                str(self.DATA_LIST[i].localita),  # 12 - scavato
                str(self.DATA_LIST[i].indirizzo),  # 13 - attivita
                str(self.DATA_LIST[i].nr_civico),  # 14 - anno scavo
                str(self.DATA_LIST[i].carta_topo_igm),  # 15 - metodo
                str(self.DATA_LIST[i].carta_ctr),  # 16 - inclusi
                str(self.DATA_LIST[i].coord_geografiche),  # 17 - campioni
                str(self.DATA_LIST[i].coord_piane),  # 18 - rapporti
                str(self.DATA_LIST[i].quota),  # 19 - data schedatura
                str(self.DATA_LIST[i].andamento_terreno_pendenza),  # 20 - schedatore
                str(self.DATA_LIST[i].utilizzo_suolo_vegetazione),  # 21 - formazione
                str(self.DATA_LIST[i].descrizione_empirica_suolo),  # 22 - conservazione
                str(self.DATA_LIST[i].descrizione_luogo),  # 23 - colore
                str(self.DATA_LIST[i].metodo_rilievo_e_ricognizione),  # 24 - consistenza
                str(self.DATA_LIST[i].geometria),  # 25 - struttura
                str(self.DATA_LIST[i].bibliografia),  # 25 - struttura
                str(self.DATA_LIST[i].data),  # 29 - piante
                str(self.DATA_LIST[i].ora_meteo),  # 11 - fase finale
                str(self.DATA_LIST[i].responsabile),  # 12 - scavato
                str(self.DATA_LIST[i].dimensioni_ut),  # 13 - attivita
                str(self.DATA_LIST[i].rep_per_mq),  # 14 - anno scavo
                str(self.DATA_LIST[i].rep_datanti),  # 15 - metodo
                str(self.DATA_LIST[i].periodo_I),  # 16 - inclusi
                str(self.DATA_LIST[i].datazione_I),  # 17 - campioni
                str(self.DATA_LIST[i].interpretazione_I),  # 18 - rapporti
                str(self.DATA_LIST[i].periodo_II),  # 19 - data schedatura
                str(self.DATA_LIST[i].datazione_II),  # 20 - schedatore
                str(self.DATA_LIST[i].interpretazione_II),  # 21 - formazione
                str(self.DATA_LIST[i].documentazione),  # 21 - formazione
                str(self.DATA_LIST[i].enti_tutela_vincoli),  # 22 - conservazione
                str(self.DATA_LIST[i].indagini_preliminari)  # 23 -
            ])
        return data_list

    def testing(self, name_file, message):
        f = open(str(name_file), 'w')
        f.write(str(message))
        f.close()


## Class end

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = pyarchinit_UT()
    ui.show()
    sys.exit(app.exec_())
