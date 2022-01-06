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

from builtins import range
from builtins import str
from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtWidgets import QDialog, QMessageBox,QTableWidgetItem
from qgis.PyQt.uic import loadUiType
from qgis.core import QgsSettings, Qgis
from qgis.gui import QgsMapToolPan

from ..modules.db.pyarchinit_conn_strings import Connection
from ..modules.db.pyarchinit_db_manager import Pyarchinit_db_management
from ..modules.db.pyarchinit_utility import Utility
from ..modules.gis.pyarchinit_pyqgis import Pyarchinit_pyqgis
from ..gui.imageViewer import ImageViewer
from ..gui.sortpanelmain import SortPanelMain
from ..gui.pyarchinitConfigDialog import pyArchInitDialog_Config
MAIN_DIALOG_CLASS, _ = loadUiType(os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'Detsesso.ui'))


class pyarchinit_Detsesso(QDialog, MAIN_DIALOG_CLASS):
    L=QgsSettings().value("locale/userLocale")[0:2]
    MSG_BOX_TITLE = "PyArchInit - pyarchinit_US_version 0.4 - Scheda Determinazione sesso"
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
    TABLE_NAME = 'detsesso_table'
    MAPPER_TABLE_CLASS = "DETSESSO"
    NOME_SCHEDA = "Scheda Determinazione del sesso"
    ID_TABLE = "id_det_sesso"
    CONVERSION_DICT = {
        ID_TABLE: ID_TABLE,
        "Sito": "sito",
        "Numero individuo": "num_individuo",
        "Glabella grado imp": "glab_grado_imp",
        "Processo mastoideo grado imp": "pmast_grado_imp",
        "Piano nucale grado imp": "pnuc_grado_imp",
        "Processo zigomatico grado imp": "pzig_grado_imp",
        "Arcata sopraciliare grado imp": "arcsop_grado_imp",
        "Tuberosita\' frontale e parietale grado imp": "tub_grado_imp",
        "Protuberanza occipitale esterna grado imp": "pocc_grado_imp",
        "Inclinazione frontale grado imp": "inclfr_grado_imp",
        "Osso zigomatico grado imp": "zig_grado_imp",
        "Margine sopraorbitale grado imp": "msorb_grado_imp",
        "Glabella valori": "glab_valori",
        "Processo mastoideo valori": "pmast_valori",
        "Piano nucale valori": "pnuc_valori",
        "Processo zigomatico valori": "pzig_valori",
        "Arcata sopraciliare valori": "arcsop_valori",
        "Tuberosita\' frontale e parietale valori": "tub_valori",
        "Protuberanza occipitale esterna valori": "pocc_valori",
        "Inclinazione frontale valori": "inclfr_valori",
        "Osso zigomatico valori": "zig_valori",
        "Margine sopraorbitale valori": "msorb_valori",
        "Palato	grado imp": "palato_grado_imp",
        "Morfologia mandibola grado imp": "mfmand_grado_imp",
        "Mento grado imp": "mento_grado_imp",
        "Angolo	mandibolare grado imp": "anmand_grado_imp",
        "Margine inferiore grado imp": "minf_grado_imp",
        "Branca	montante grado imp": "brmont_grado_imp",
        "Condilo mandibolare grado imp": "condm_grado_imp",
        "Palato	valori": "palato_valori",
        "Morfologia mandibola valori": "mfmand_valori",
        "Mento valori": "mento_valori",
        "Angolo	mandibolare valori": "anmand_valori",
        "Margine inferiore valori": "minf_valori",
        "Branca	montante valori": "brmont_valori",
        "Condilo mandibolare valori": "condm_valori",
        "Valore	totale sex cranio": "sex_cr_tot",
        "Indice	sessualizzazione cranio": "ind_cr_sex",
        "Superficie preauricolare I": "sup_p_I",
        "Superficie preauricolare II": "sup_p_II",
        "Superficie preauricolare III": "sup_p_III",
        "Superficie preauricolare sesso": "sup_p_sex",
        "Grande incisura ischiatica I": "in_isch_I",
        "Grande incisura ischiatica II": "in_isch_II",
        "Grande incisura ischiatica III": "in_isch_III",
        "Grande incisura ischiatica sesso": "in_isch_sex",
        "Arco composito sesso": "arco_c_sex",
        "Ramo ischio pubico I": "ramo_ip_I",
        "Ramo ischio pubico II": "ramo_ip_II",
        "Ramo ischio pubico III": "ramo_ip_III",
        "Ramo ischio pubico sesso": "ramo_ip_sex",
        "Proporzioni ischio pubiche sesso": "prop_ip_sex",
        "Indice sessualizzazione bacino": "ind_bac_sex"
    }
    SORT_ITEMS = [
        ID_TABLE,
        "Sito",
        "Numero individuo",
        "Glabella grado imp",
        "Processo mastoideo grado imp",
        "Piano nucale grado imp",
        "Processo zigomatico grado imp",
        "Arcata sopraciliare grado imp",
        "Tuberosita\' frontale e parietale grado imp",
        "Protuberanza occipitale esterna grado imp",
        "Inclinazione frontale grado imp",
        "Osso zigomatico grado imp",
        "Margine sopraorbitale grado imp",
        "Glabella valori",
        "Processo mastoideo valori",
        "Piano nucale valori",
        "Processo zigomatico valori",
        "Arcata	sopraciliare valori",
        "Tuberosita\' frontale e parietale valori",
        "Protuberanza occipitale esterna valori",
        "Inclinazione frontale valori",
        "Osso zigomatico valori",
        "Margine sopraorbitale valori",
        "Palato	grado imp",
        "Morfologia mandibola grado imp",
        "Mento grado imp",
        "Angolo	mandibolare grado imp",
        "Margine inferiore grado imp",
        "Branca	montante grado imp",
        "Condilo mandibolare grado imp",
        "Palato	valori",
        "Morfologia mandibola valori",
        "Mento valori",
        "Angolo	mandibolare valori",
        "Margine inferiore valori",
        "Branca	montante valori",
        "Condilo mandibolare valori",
        "Valore	totale sex cranio",
        "Indice	sessualizzazione cranio",
        "Superficie preauricolare I",
        "Superficie preauricolare II",
        "Superficie preauricolare III",
        "Superficie preauricolare sesso",
        "Grande incisura ischiatica I",
        "Grande incisura ischiatica II",
        "Grande incisura ischiatica III",
        "Grande incisura ischiatica sesso",
        "Arco composito sesso",
        "Ramo ischio pubico I",
        "Ramo ischio pubico II",
        "Ramo ischio pubico III",
        "Ramo ischio pubico sesso",
        "Proporzioni ischio pubiche sesso",
        "Indice sessualizzazione bacino"
    ]

    TABLE_FIELDS = [
        'sito',
        'num_individuo',
        'glab_grado_imp',
        'pmast_grado_imp',
        'pnuc_grado_imp',
        'pzig_grado_imp',
        'arcsop_grado_imp',
        'tub_grado_imp',
        'pocc_grado_imp',
        'inclfr_grado_imp',
        'zig_grado_imp',
        'msorb_grado_imp',
        'glab_valori',
        'pmast_valori',
        'pnuc_valori',
        'pzig_valori',
        'arcsop_valori',
        'tub_valori',
        'pocc_valori',
        'inclfr_valori',
        'zig_valori',
        'msorb_valori',
        'palato_grado_imp',
        'mfmand_grado_imp',
        'mento_grado_imp',
        'anmand_grado_imp',
        'minf_grado_imp',
        'brmont_grado_imp',
        'condm_grado_imp',
        'palato_valori',
        'mfmand_valori',
        'mento_valori',
        'anmand_valori',
        'minf_valori',
        'brmont_valori',
        'condm_valori',
        'sex_cr_tot',
        'ind_cr_sex',
        'sup_p_I',
        'sup_p_II',
        'sup_p_III',
        'sup_p_sex',
        'in_isch_I',
        'in_isch_II',
        'in_isch_III',
        'in_isch_sex',
        'arco_c_sex',
        'ramo_ip_I',
        'ramo_ip_II',
        'ramo_ip_III',
        'ramo_ip_sex',
        'prop_ip_sex',
        'ind_bac_sex'
    ]

    DB_SERVER = "not defined"  ####nuovo sistema sort

    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.pyQGIS = Pyarchinit_pyqgis(iface)
        self.setupUi(self)

        self.customize_GUI()  # call for GUI customizations
        self.currentLayerId = None
        try:
            self.on_pushButton_connect_pressed()
        except Exception as e:
            QMessageBox.warning(self, "Sistema di connessione", str(e), QMessageBox.Ok)
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
        pass

    def loadMapPreview(self, mode=0):
        pass

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
            
                QMessageBox.information(self, "Warnung" , "Es gibt keine solche archäologische Stätte: "'""'+ str(site_set_str) +'"'" in dieser Registerkarte, Bitte deaktivieren Sie die 'Site-Wahl' in der Plugin-Konfigurationsregisterkarte, um alle Datensätze zu sehen oder die Registerkarte zu erstellen",QMessageBox.Ok) 
            else:
            
                QMessageBox.information(self, "Warning" , "There is no such site: "'"'+ str(site_set_str) +'"'" in this tab, Please disable the 'site choice' from the plugin configuration tab to see all records or create the tab",QMessageBox.Ok)  
    
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
                int(self.DATA_LIST[i].num_individuo),  # 2 - numero individuo
                int(self.DATA_LIST[i].glab_grado_imp),  # 3 - glabella grado imp
                int(self.DATA_LIST[i].pmast_grado_imp),  # 4 - processo mastoideo	grado imp
                int(self.DATA_LIST[i].pnuc_grado_imp),  # 5 - piano nucale grado imp
                int(self.DATA_LIST[i].pzig_grado_imp),  # 6 - processo zigomatico grado imp
                int(self.DATA_LIST[i].arcsop_grado_imp),  # 7 - arcata sopraciliare grado imp
                int(self.DATA_LIST[i].tub_grado_imp),  # 8 - Tuberosita' frontale e parietale grado imp
                int(self.DATA_LIST[i].pocc_grado_imp),  # 9 - Protuberanza occipitale esterna grado imp
                int(self.DATA_LIST[i].inclfr_grado_imp),  # 10 - Inclinazione frontale grado imp
                int(self.DATA_LIST[i].zig_grado_imp),  # 11 - Osso zigomatico grado imp
                int(self.DATA_LIST[i].msorb_grado_imp),  # 12 - Margine sopraorbitale grado imp
                int(self.DATA_LIST[i].glab_valori),  # 13 - Glabella valori
                int(self.DATA_LIST[i].pmast_valori),  # 14 - Processo mastoideo valori
                int(self.DATA_LIST[i].pnuc_valori),  # 15 - Piano nucale valori
                int(self.DATA_LIST[i].pzig_valori),  # 16 - Processo zigomatico valori
                int(self.DATA_LIST[i].arcsop_valori),  # 17 - Arcata sopraciliare valori
                int(self.DATA_LIST[i].tub_valori),  # 18 - Tuberosita' frontale e parietale valori
                int(self.DATA_LIST[i].pocc_valori),  # 19 - Protuberanza occipitale esterna valori
                int(self.DATA_LIST[i].inclfr_valori),  # 20 - Inclinazione frontale valori
                int(self.DATA_LIST[i].zig_valori),  # 21 - Osso zigomatico valori
                int(self.DATA_LIST[i].msorb_valori),  # 22 - Margine sopraorbitale valori
                int(self.DATA_LIST[i].palato_grado_imp),  # 23 - Palato grado imp
                int(self.DATA_LIST[i].mfmand_grado_imp),  # 24 - Morfologia mandibola grado imp
                int(self.DATA_LIST[i].mento_grado_imp),  # 25 - Mento grado imp
                int(self.DATA_LIST[i].anmand_grado_imp),  # 26 - Angolo mandibolare grado imp
                int(self.DATA_LIST[i].minf_grado_imp),  # 27 - Margine inferiore	grado imp
                int(self.DATA_LIST[i].brmont_grado_imp),  # 28 - Branca montante grado imp
                int(self.DATA_LIST[i].condm_grado_imp),  # 29 - Condilo mandibolare grado	imp
                int(self.DATA_LIST[i].palato_valori),  # 30 - Palato valori
                int(self.DATA_LIST[i].mfmand_valori),  # 31 - Morfologia mandibola valori
                int(self.DATA_LIST[i].mento_valori),  # 32 - Mento valori
                int(self.DATA_LIST[i].anmand_valori),  # 33 - Angolo mandibolare valori
                int(self.DATA_LIST[i].minf_valori),  # 34 - Margine inferiore	valori
                int(self.DATA_LIST[i].brmont_valori),  # 35 - Branca montante valori
                int(self.DATA_LIST[i].condm_valori),  # 36 - Condilo mandibolare valori
                float(self.DATA_LIST[i].sex_cr_tot),  # 37 - Valore totale sex	cranio
                str(self.DATA_LIST[i].ind_cr_sex),  # 38 - Indice sessualizzazione cranio
                str(self.DATA_LIST[i].sup_p_I),  # 39 - Superficie preauricolare I
                str(self.DATA_LIST[i].sup_p_II),  # 40 - Superficie preauricolare II
                str(self.DATA_LIST[i].sup_p_III),  # 41 - Superficie preauricolare III
                str(self.DATA_LIST[i].sup_p_sex),  # 42 - Superficie preauricolare sesso
                str(self.DATA_LIST[i].in_isch_I),  # 43 - Grande incisura ischiatica I
                str(self.DATA_LIST[i].in_isch_II),  # 44 - Grande incisura ischiatica II
                str(self.DATA_LIST[i].in_isch_III),  # 45 - Grande incisura ischiatica III
                str(self.DATA_LIST[i].in_isch_sex),  # 46 - Grande incisura ischiatica sesso
                str(self.DATA_LIST[i].arco_c_sex),  # 47 - Arco composito sesso
                str(self.DATA_LIST[i].ramo_ip_I),  # 48 - Ramo ischio pubico I
                str(self.DATA_LIST[i].ramo_ip_II),  # 49 - Ramo ischio pubico II
                str(self.DATA_LIST[i].ramo_ip_III),  # 50 - Ramo ischio pubico III
                str(self.DATA_LIST[i].ramo_ip_sex),  # 51 - Ramo ischio pubico sesso
                str(self.DATA_LIST[i].prop_ip_sex),  # 52 - Proporzioni ischio pubiche sesso
                str(self.DATA_LIST[i].ind_bac_sex)  # 53 - Indice sessualizzazione bacino
            ])
        return data_list

    def on_toolButtonPan_toggled(self):
        self.toolPan = QgsMapToolPan(self.mapPreview)
        self.mapPreview.setMapTool(self.toolPan)

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

    def on_toolButtonGis_toggled(self):
        if self.toolButtonGis.isChecked():
            QMessageBox.warning(self, "Messaggio",
                                "Modalita' GIS attiva. Da ora le tue ricerche verranno visualizzate sul GIS",
                                QMessageBox.Ok)
        else:
            QMessageBox.warning(self, "Messaggio",
                                "Modalita' GIS disattivata. Da ora le tue ricerche non verranno piu' visualizzate sul GIS",
                                QMessageBox.Ok)

    def on_toolButtonPreview_toggled(self):
        if self.toolButtonPreview.isChecked():
            QMessageBox.warning(self, "Messaggio",
                                "Modalita' Preview US attivata. Le piante delle US saranno visualizzate nella sezione Piante",
                                QMessageBox.Ok)
            self.loadMapPreview()
        else:
            self.loadMapPreview(1)

    def on_pushButton_addRaster_pressed(self):
        if self.toolButtonGis.isChecked():
            self.pyQGIS.addRasterLayer()

    def on_pushButton_new_rec_pressed(self):
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

            # self.setComboBoxEditable(["self.comboBox_sito"],0)
            # self.setComboBoxEnable(["self.comboBox_sito"],"True")
            # self.setComboBoxEnable(["self.lineEdit_individuo"],"True")

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
                else:
                    QMessageBox.warning(self, "ATTENZIONE", "Non è stata realizzata alcuna modifica.", QMessageBox.Ok)
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

                    self.fill_fields(self.REC_CORR)
                    self.enable_button(1)
            else:
                pass

    def data_error_check(self):
        test = 0
        # EC = Error_check()
        # somes check here

        return test

    def insert_new_rec(self):

        if self.comboBox_glab_valori.currentText() == "":
            glab_valori = None
        else:
            glab_valori = int(self.comboBox_glab_valori.currentText())

        if self.comboBox_pmast_valori.currentText() == "":
            pmast_valori = None
        else:
            pmast_valori = int(self.comboBox_pmast_valori.currentText())

        if self.comboBox_pnuc_valori.currentText() == "":
            pnuc_valori = None
        else:
            pnuc_valori = int(self.comboBox_pnuc_valori.currentText())

        if self.comboBox_pzig_valori.currentText() == "":
            pzig_valori = None
        else:
            pzig_valori = int(self.comboBox_pzig_valori.currentText())

        if self.comboBox_arcsop_valori.currentText() == "":
            arcsop_valori = None
        else:
            arcsop_valori = int(self.comboBox_arcsop_valori.currentText())

        if self.comboBox_tub_valori.currentText() == "":
            tub_valori = None
        else:
            tub_valori = int(self.comboBox_tub_valori.currentText())

        if self.comboBox_pocc_valori.currentText() == "":
            pocc_valori = None
        else:
            pocc_valori = int(self.comboBox_pocc_valori.currentText())

        if self.comboBox_inclfr_valori.currentText() == "":
            inclfr_valori = None
        else:
            inclfr_valori = int(self.comboBox_inclfr_valori.currentText())

        if self.comboBox_zig_valori.currentText() == "":
            zig_valori = None
        else:
            zig_valori = int(self.comboBox_zig_valori.currentText())

        if self.comboBox_msorb_valori.currentText() == "":
            msorb_valori = None
        else:
            msorb_valori = int(self.comboBox_msorb_valori.currentText())

        if self.comboBox_palato_valori.currentText() == "":
            palato_valori = None
        else:
            palato_valori = int(self.comboBox_palato_valori.currentText())

        if self.comboBox_mfmand_valori.currentText() == "":
            mfmand_valori = None
        else:
            mfmand_valori = int(self.comboBox_mfmand_valori.currentText())

        if self.comboBox_mento_valori.currentText() == "":
            mento_valori = None
        else:
            mento_valori = int(self.comboBox_mento_valori.currentText())

        if self.comboBox_anmand_valori.currentText() == "":
            anmand_valori = None
        else:
            anmand_valori = int(self.comboBox_anmand_valori.currentText())

        if self.comboBox_minf_valori.currentText() == "":
            minf_valori = None
        else:
            minf_valori = int(self.comboBox_minf_valori.currentText())

        if self.comboBox_brmont_valori.currentText() == "":
            brmont_valori = None
        else:
            brmont_valori = int(self.comboBox_brmont_valori.currentText())

        if self.comboBox_condm_valori.currentText() == "":
            condm_valori = None
        else:
            condm_valori = int(self.comboBox_condm_valori.currentText())

        if self.lineEdit_sex_cr_tot.text() == "":
            sex_cr_tot = None
        else:
            sex_cr_tot = float(self.lineEdit_sex_cr_tot.text())

        try:
            data = self.DB_MANAGER.insert_values_detsesso(
                self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, self.ID_TABLE) + 1,
                str(self.comboBox_sito.currentText()),  # 1 - Sito
                int(self.lineEdit_nr_individuo.text()),  # 2 - Numero individuo
                int(self.lineEdit_glab_grado_imp.text()),
                int(self.lineEdit_pmast_grado_imp.text()),
                int(self.lineEdit_pnuc_grado_imp.text()),
                int(self.lineEdit_pzig_grado_imp.text()),
                int(self.lineEdit_arcsop_grado_imp.text()),
                int(self.lineEdit_tub_grado_imp.text()),
                int(self.lineEdit_pocc_grado_imp.text()),
                int(self.lineEdit_inclfr_grado_imp.text()),
                int(self.lineEdit_zig_grado_imp.text()),
                int(self.lineEdit_msorb_grado_imp.text()),
                glab_valori,  # 13 - Glabella valori
                pmast_valori,  # 14 - Processo mastoideo valori
                pnuc_valori,  # 15 - Piano nucale valori
                pzig_valori,  # 16 - Processo zigomatico valori
                arcsop_valori,  # 17 - Arcata sopraciliare valori
                tub_valori,  # 18 - Tuberosita' frontale e parietale valori
                pocc_valori,  # 19 - Protuberanza occipitale esterna valori
                inclfr_valori,  # 20 - Inclinazione frontale valori
                zig_valori,  # 21 - Osso zigomatico valori
                msorb_valori,  # 22 - Margine sopraorbitale valori
                int(self.lineEdit_palato_grado_imp.text()),
                int(self.lineEdit_mfmand_grado_imp.text()),
                int(self.lineEdit_mento_grado_imp.text()),
                int(self.lineEdit_anmand_grado_imp.text()),
                int(self.lineEdit_minf_grado_imp.text()),
                int(self.lineEdit_brmont_grado_imp.text()),
                int(self.lineEdit_condm_grado_imp.text()),
                palato_valori,  # 30 - Palato valori
                mfmand_valori,  # 31 - Morfologia mandibola valori
                mento_valori,  # 32 - Mento valori
                anmand_valori,  # 33 - Angolo mandibolare valori
                minf_valori,  # 34 - Margine inferiore valori
                brmont_valori,  # 35 - Branca montante valori
                condm_valori,  # 36 - Condilo mandibolare valori
                sex_cr_tot,  # 37 - Valore totale sex	cranio
                str(self.comboBox_ind_cr_sex.currentText()),  # 38 - Indice sessualizzazione cranio
                str(self.comboBox_sup_p_I.currentText()),  # 39 - Superficie preauricolare I
                str(self.comboBox_sup_p_II.currentText()),  # 40 - Superficie preauricolare II
                str(self.comboBox_sup_p_III.currentText()),  # 41 - Superficie preauricolare III
                str(self.comboBox_sup_p_sex.currentText()),  # 42 - Superficie preauricolare sesso
                str(self.comboBox_in_isch_I.currentText()),  # 43 - Grande incisura ischiatica I
                str(self.comboBox_in_isch_II.currentText()),  # 44 - Grande incisura ischiatica II
                str(self.comboBox_in_isch_III.currentText()),  # 45 - Grande incisura ischiatica III
                str(self.comboBox_in_isch_sex.currentText()),  # 46 - Grande incisura ischiatica sesso
                str(self.comboBox_arco_c_sex.currentText()),  # 47 - Arco composito sesso
                str(self.comboBox_ramo_ip_I.currentText()),  # 48 - Ramo ischio pubico I
                str(self.comboBox_ramo_ip_II.currentText()),  # 49 - Ramo ischio pubico II
                str(self.comboBox_ramo_ip_III.currentText()),  # 50 - Ramo ischio pubico III
                str(self.comboBox_ramo_ip_sex.currentText()),  # 51 - Ramo ischio pubico sesso
                str(self.comboBox_prop_ip_sex.currentText()),  # 52 - Proporzioni ischio pubiche sesso
                str(self.comboBox_ind_bac_sex.currentText())  # 53 - Indice sessualizzazione bacino
            )

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

            # insert new row into tableWidget

    def on_pushButton_insert_row_rapporti_pressed(self):
        self.insert_new_row('self.tableWidget_rapporti')

    def on_pushButton_insert_row_inclusi_pressed(self):
        self.insert_new_row('self.tableWidget_inclusi')

    def on_pushButton_insert_row_campioni_pressed(self):
        self.insert_new_row('self.tableWidget_campioni')

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

    def on_pushButton_search_go_pressed(self):
        if self.BROWSE_STATUS != "f":
            QMessageBox.warning(self, "ATTENZIONE", "Per eseguire una nuova ricerca clicca sul pulsante 'new search' ",
                                QMessageBox.Ok)
        else:

            # TableWidget
            search_dict = {
                self.TABLE_FIELDS[0]: "'" + str(self.comboBox_sito.currentText()) + "'",  # 0 - Sito
                self.TABLE_FIELDS[1]: int(self.lineEdit_nr_individuo.text()),  # 1 - Numero individuo
                self.TABLE_FIELDS[2]: int(self.lineEdit_glab_grado_imp.text()),  # 2 - Glabella grado imp
                self.TABLE_FIELDS[3]: int(self.lineEdit_pmast_grado_imp.text()),  # 3 - Processo mastoideo grado imp
                self.TABLE_FIELDS[4]: int(self.lineEdit_pnuc_grado_imp.text()),  # 4 - Piano nucale grado imp
                self.TABLE_FIELDS[5]: int(self.lineEdit_pzig_grado_imp.text()),  # 5 - Processo zigomatico grado imp
                self.TABLE_FIELDS[6]: int(self.lineEdit_arcsop_grado_imp.text()),  # 6 - Arcata sopraciliare grado imp
                self.TABLE_FIELDS[7]: int(self.lineEdit_tub_grado_imp.text()),
                # 7 - Tuberosita' frontale e parietale grado imp
                self.TABLE_FIELDS[8]: int(self.lineEdit_pocc_grado_imp.text()),
                # 8 - Protuberanza occipitale esterna grado imp
                self.TABLE_FIELDS[9]: int(self.lineEdit_inclfr_grado_imp.text()),
                # 9 - Inclinazione frontale grado imp
                self.TABLE_FIELDS[10]: int(self.lineEdit_zig_grado_imp.text()),  # 10 - Osso zigomatico grado imp
                self.TABLE_FIELDS[11]: int(self.lineEdit_msorb_grado_imp.text()),
                # 11 - Margine sopraorbitale grado imp
                self.TABLE_FIELDS[12]: int(self.comboBox_glab_valori.currentText()),  # 12 - Glabella valori
                self.TABLE_FIELDS[13]: int(self.comboBox_pmast_valori.currentText()),  # 13 - Processo mastoideo valori
                self.TABLE_FIELDS[14]: int(self.comboBox_pnuc_valori.currentText()),  # 14 - Piano nucale valori
                self.TABLE_FIELDS[15]: int(self.comboBox_pzig_valori.currentText()),  # 15 - Processo zigomatico valori
                self.TABLE_FIELDS[16]: int(self.comboBox_arcsop_valori.currentText()),
                # 16 - Arcata sopraciliare valori
                self.TABLE_FIELDS[17]: int(self.comboBox_tub_valori.currentText()),
                # 17 - Tuberosita' frontale e parietale valori
                self.TABLE_FIELDS[18]: int(self.comboBox_pocc_valori.currentText()),
                # 18 - Protuberanza occipitale esterna valori
                self.TABLE_FIELDS[19]: int(self.comboBox_inclfr_valori.currentText()),
                # 19 - Inclinazione frontale valori
                self.TABLE_FIELDS[20]: int(self.comboBox_zig_valori.currentText()),  # 20 - Osso zigomatico valori
                self.TABLE_FIELDS[21]: int(self.comboBox_msorb_valori.currentText()),
                # 21 - Margine sopraorbitale valori
                self.TABLE_FIELDS[22]: int(self.lineEdit_palato_grado_imp.text()),  # 22 - Palato grado imp
                self.TABLE_FIELDS[23]: int(self.lineEdit_mfmand_grado_imp.text()),
                # 23 - Morfologia mandibola grado imp
                self.TABLE_FIELDS[24]: int(self.lineEdit_mento_grado_imp.text()),  # 24 - Mento grado imp
                self.TABLE_FIELDS[25]: int(self.lineEdit_anmand_grado_imp.text()),  # 25 - Angolo mandibolare grado imp
                self.TABLE_FIELDS[26]: int(self.lineEdit_minf_grado_imp.text()),  # 26 - Margine inferiore	grado imp
                self.TABLE_FIELDS[27]: int(self.lineEdit_brmont_grado_imp.text()),  # 27 - Branca montante grado imp
                self.TABLE_FIELDS[28]: int(self.lineEdit_condm_grado_imp.text()),  # 28 - Condilo mandibolare grado	imp
                self.TABLE_FIELDS[29]: int(self.comboBox_palato_valori.currentText()),  # 29 - Palato valori
                self.TABLE_FIELDS[30]: int(self.comboBox_mfmand_valori.currentText()),
                # 30 - Morfologia mandibola valori
                self.TABLE_FIELDS[31]: int(self.comboBox_mento_valori.currentText()),  # 31 - Mento valori
                self.TABLE_FIELDS[32]: int(self.comboBox_anmand_valori.currentText()),  # 32 - Angolo mandibolare valori
                self.TABLE_FIELDS[33]: int(self.comboBox_minf_valori.currentText()),  # 33 - Margine inferiore	valori
                self.TABLE_FIELDS[34]: int(self.comboBox_brmont_valori.currentText()),  # 34 - Branca montante valori
                self.TABLE_FIELDS[35]: int(self.comboBox_condm_valori.currentText()),  # 35 - Condilo mandibolare valori
                self.TABLE_FIELDS[36]: float(self.lineEdit_sex_cr_tot.text()),  # 36 - Valore totale sex	cranio
                self.TABLE_FIELDS[37]: "'" + str(self.comboBox_ind_cr_sex.currentText()) + "'",
                # 37 - Indice sessualizzazione cranio
                self.TABLE_FIELDS[38]: "'" + str(self.comboBox_sup_p_I.currentText()) + "'",
                # 38 - Superficie preauricolare I
                self.TABLE_FIELDS[39]: "'" + str(self.comboBox_sup_p_II.currentText()) + "'",
                # 39 - Superficie preauricolare II
                self.TABLE_FIELDS[40]: "'" + str(self.comboBox_sup_p_III.currentText()) + "'",
                # 40 - Superficie preauricolare III
                self.TABLE_FIELDS[41]: "'" + str(self.comboBox_sup_p_sex.currentText()) + "'",
                # 41 - Superficie preauricolare sesso
                self.TABLE_FIELDS[42]: "'" + str(self.comboBox_in_isch_I.currentText()) + "'",
                # 42 - Grande incisura ischiatica I
                self.TABLE_FIELDS[43]: "'" + str(self.comboBox_in_isch_II.currentText()) + "'",
                # 43 - Grande incisura ischiatica II
                self.TABLE_FIELDS[44]: "'" + str(self.comboBox_in_isch_III.currentText()) + "'",
                # 44 - Grande incisura ischiatica III
                self.TABLE_FIELDS[45]: "'" + str(self.comboBox_in_isch_sex.currentText()) + "'",
                # 45 - Grande incisura ischiatica sesso
                self.TABLE_FIELDS[46]: "'" + str(self.comboBox_arco_c_sex.currentText()) + "'",
                # 46 - Arco composito sesso
                self.TABLE_FIELDS[47]: "'" + str(self.comboBox_ramo_ip_I.currentText()) + "'",
                # 47 - Ramo ischio pubico I
                self.TABLE_FIELDS[48]: "'" + str(self.comboBox_ramo_ip_II.currentText()) + "'",
                # 48 - Ramo ischio pubico II
                self.TABLE_FIELDS[49]: "'" + str(self.comboBox_ramo_ip_III.currentText()) + "'",
                # 49 - Ramo ischio pubico III
                self.TABLE_FIELDS[50]: "'" + str(self.comboBox_ramo_ip_sex.currentText()) + "'",
                # 50 - Ramo ischio pubico sesso
                self.TABLE_FIELDS[51]: "'" + str(self.comboBox_prop_ip_sex.currentText()) + "'",
                # 51 - Proporzioni ischio pubiche sesso
                self.TABLE_FIELDS[52]: "'" + str(self.comboBox_ind_bac_sex.currentText()) + "'"
                # 52 - Indice sessualizzazione bacino
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
                        if self.toolButtonGis.isChecked():
                            id_us_list = self.charge_id_us_for_individuo()
                            self.pyQGIS.charge_individui_us(id_us_list)
                    else:
                        strings = ("Sono stati trovati", self.REC_TOT, "records")
                        if self.toolButtonGis.isChecked():
                            id_us_list = self.charge_id_us_for_individuo()
                            self.pyQGIS.charge_individui_us(id_us_list)

                    QMessageBox.warning(self, "Messaggio", "%s %d %s" % strings, QMessageBox.Ok)

        self.enable_button_search(1)

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

    def insert_new_row(self, table_name):
        """insert new row into a table based on table_name"""
        cmd = table_name + ".insertRow(0)"
        eval(cmd)

    def empty_fields(self):
        # rapporti_row_count = self.tableWidget_rapporti.rowCount()
        # campioni_row_count = self.tableWidget_campioni.rowCount()
        # inclusi_row_count = self.tableWidget_inclusi.rowCount()

        self.comboBox_sito.setEditText("")  # 1 - Sito
        self.comboBox_glab_valori.setEditText("")
        self.comboBox_pmast_valori.setEditText("")  # 14 - Processo mastoideo valori
        self.comboBox_pnuc_valori.setEditText("")  # 15 - Piano nucale valori
        self.comboBox_pzig_valori.setEditText("")  # 16 - Processo zigomatico valori
        self.comboBox_arcsop_valori.setEditText("")  # 17 - Arcata sopraciliare valori
        self.comboBox_tub_valori.setEditText("")  # 18 - Tuberosita' frontale e parietale valori
        self.comboBox_pocc_valori.setEditText("")  # 19 - Protuberanza occipitale esterna valori
        self.comboBox_inclfr_valori.setEditText("")  # 20 - Inclinazione frontale valori
        self.comboBox_zig_valori.setEditText("")  # 21 - Osso zigomatico valori
        self.comboBox_msorb_valori.setEditText("")  # 22 - Margine sopraorbitale valori
        self.comboBox_palato_valori.setEditText("")  # 30 - Palato valori
        self.comboBox_mfmand_valori.setEditText("")  # 31 - Morfologia mandibola valori
        self.comboBox_mento_valori.setEditText("")  # 32 - Mento valori
        self.comboBox_anmand_valori.setEditText("")  # 33 - Angolo mandibolare valori
        self.comboBox_minf_valori.setEditText("")  # 34 - Margine inferiore valori
        self.comboBox_brmont_valori.setEditText("")  # 35 - Branca montante valori
        self.comboBox_condm_valori.setEditText("")  # 36 - Condilo mandibolare valori

        self.lineEdit_sex_cr_tot.clear()  # 37 - Valore totale sex cranio

        self.comboBox_ind_cr_sex.setEditText("")  # 38 - Indice sessualizzazione cranio
        self.comboBox_sup_p_I.setEditText("")  # 39 - Superficie preauricolare I
        self.comboBox_sup_p_II.setEditText("")  # 40 - Superficie preauricolare II
        self.comboBox_sup_p_III.setEditText("")  # 41 - Superficie preauricolare III
        self.comboBox_sup_p_sex.setEditText("")  # 42 - Superficie preauricolare sesso
        self.comboBox_in_isch_I.setEditText("")  # 43 - Grande incisura ischiatica I
        self.comboBox_in_isch_II.setEditText("")  # 44 - Grande incisura ischiatica II
        self.comboBox_in_isch_III.setEditText("")  # 45 - Grande incisura ischiatica III
        self.comboBox_in_isch_sex.setEditText("")  # 46 - Grande incisura ischiatica sesso
        self.comboBox_arco_c_sex.setEditText("")  # 47 - Arco composito sesso
        self.comboBox_ramo_ip_I.setEditText("")  # 48 - Ramo ischio pubico I
        self.comboBox_ramo_ip_II.setEditText("")  # 49 - Ramo ischio pubico II
        self.comboBox_ramo_ip_III.setEditText("")  # 50 - Ramo ischio pubico III
        self.comboBox_ramo_ip_sex.setEditText("")  # 51 - Ramo ischio pubico sesso
        self.comboBox_prop_ip_sex.setEditText("")  # 52 - Proporzioni ischio pubiche sesso
        self.comboBox_ind_bac_sex.setEditText("")

    def fill_fields(self, n=0):

        self.rec_num = n
        try:

            self.comboBox_sito.setEditText(self.DATA_LIST[self.rec_num].sito)  # 1 - Sito
            self.lineEdit_nr_individuo.setText(str(self.DATA_LIST[self.rec_num].num_individuo))

            # 2 - Numero individuo

            if self.DATA_LIST[self.rec_num].glab_valori == None:
                self.comboBox_glab_valori.setEditText("")
            else:
                self.comboBox_glab_valori.setEditText(str(self.DATA_LIST[self.rec_num].glab_valori))

            if self.DATA_LIST[self.rec_num].pmast_valori == None:
                self.comboBox_pmast_valori.setEditText("")
            else:
                self.comboBox_pmast_valori.setEditText(str(self.DATA_LIST[self.rec_num].pmast_valori))

            if self.DATA_LIST[self.rec_num].pnuc_valori == None:
                self.comboBox_pnuc_valori.setEditText("")
            else:
                self.comboBox_pnuc_valori.setEditText(str(self.DATA_LIST[self.rec_num].pnuc_valori))

            if self.DATA_LIST[self.rec_num].pzig_valori == None:
                self.comboBox_pzig_valori.setEditText("")
            else:
                self.comboBox_pzig_valori.setEditText(str(self.DATA_LIST[self.rec_num].pzig_valori))

            if self.DATA_LIST[self.rec_num].arcsop_valori == None:
                self.comboBox_arcsop_valori.setEditText("")
            else:
                self.comboBox_arcsop_valori.setEditText(str(self.DATA_LIST[self.rec_num].arcsop_valori))

            if self.DATA_LIST[self.rec_num].tub_valori == None:
                self.comboBox_tub_valori.setEditText("")
            else:
                self.comboBox_tub_valori.setEditText(str(self.DATA_LIST[self.rec_num].tub_valori))

            if self.DATA_LIST[self.rec_num].pocc_valori == None:
                self.comboBox_pocc_valori.setEditText("")
            else:
                self.comboBox_pocc_valori.setEditText(str(self.DATA_LIST[self.rec_num].pocc_valori))

            if self.DATA_LIST[self.rec_num].inclfr_valori == None:
                self.comboBox_inclfr_valori.setEditText("")
            else:
                self.comboBox_inclfr_valori.setEditText(str(self.DATA_LIST[self.rec_num].inclfr_valori))

            if self.DATA_LIST[self.rec_num].zig_valori == None:
                self.comboBox_zig_valori.setEditText("")
            else:
                self.comboBox_zig_valori.setEditText(str(self.DATA_LIST[self.rec_num].zig_valori))

            if self.DATA_LIST[self.rec_num].msorb_valori == None:
                self.comboBox_msorb_valori.setEditText("")
            else:
                self.comboBox_msorb_valori.setEditText(str(self.DATA_LIST[self.rec_num].msorb_valori))

            if self.DATA_LIST[self.rec_num].palato_valori == None:
                self.comboBox_palato_valori.setEditText("")
            else:
                self.comboBox_palato_valori.setEditText(str(self.DATA_LIST[self.rec_num].palato_valori))

            if self.DATA_LIST[self.rec_num].mfmand_valori == None:
                self.comboBox_mfmand_valori.setEditText("")
            else:
                self.comboBox_mfmand_valori.setEditText(str(self.DATA_LIST[self.rec_num].mfmand_valori))

            if self.DATA_LIST[self.rec_num].mento_valori == None:
                self.comboBox_mento_valori.setEditText("")
            else:
                self.comboBox_mento_valori.setEditText(str(self.DATA_LIST[self.rec_num].mento_valori))

            if self.DATA_LIST[self.rec_num].anmand_valori == None:
                self.comboBox_anmand_valori.setEditText("")
            else:
                self.comboBox_anmand_valori.setEditText(str(self.DATA_LIST[self.rec_num].anmand_valori))

            if self.DATA_LIST[self.rec_num].minf_valori == None:
                self.comboBox_minf_valori.setEditText("")
            else:
                self.comboBox_minf_valori.setEditText(str(self.DATA_LIST[self.rec_num].minf_valori))

            if self.DATA_LIST[self.rec_num].brmont_valori == None:
                self.comboBox_brmont_valori.setEditText("")
            else:
                self.comboBox_brmont_valori.setEditText(str(self.DATA_LIST[self.rec_num].brmont_valori))

            if self.DATA_LIST[self.rec_num].condm_valori == None:
                self.comboBox_condm_valori.setEditText("")
            else:
                self.comboBox_condm_valori.setEditText(str(self.DATA_LIST[self.rec_num].condm_valori))

            if self.DATA_LIST[self.rec_num].sex_cr_tot == None:
                self.lineEdit_sex_cr_tot.setText("")
            else:
                self.lineEdit_sex_cr_tot.setText(str(self.DATA_LIST[self.rec_num].sex_cr_tot))

            if self.DATA_LIST[self.rec_num].ind_cr_sex == None:
                self.comboBox_ind_cr_sex.setEditText("")
            else:
                self.comboBox_ind_cr_sex.setEditText(str(self.DATA_LIST[self.rec_num].ind_cr_sex))

            self.comboBox_sup_p_I.setEditText(self.DATA_LIST[self.rec_num].sup_p_I)  # 39 - Superficie preauricolare I
            self.comboBox_sup_p_II.setEditText(
                self.DATA_LIST[self.rec_num].sup_p_II)  # 40 - Superficie preauricolare II
            self.comboBox_sup_p_III.setEditText(
                self.DATA_LIST[self.rec_num].sup_p_III)  # 41 - Superficie preauricolare III
            self.comboBox_sup_p_sex.setEditText(
                self.DATA_LIST[self.rec_num].sup_p_sex)  # 42 - Superficie preauricolare sesso
            self.comboBox_in_isch_I.setEditText(
                self.DATA_LIST[self.rec_num].in_isch_I)  # 43 - Grande incisura ischiatica I
            self.comboBox_in_isch_II.setEditText(
                self.DATA_LIST[self.rec_num].in_isch_II)  # 44 - Grande incisura ischiatica II
            self.comboBox_in_isch_III.setEditText(
                self.DATA_LIST[self.rec_num].in_isch_III)  # 45 - Grande incisura ischiatica III
            self.comboBox_in_isch_sex.setEditText(
                self.DATA_LIST[self.rec_num].in_isch_sex)  # 46 - Grande incisura ischiatica sesso
            self.comboBox_arco_c_sex.setEditText(self.DATA_LIST[self.rec_num].arco_c_sex)  # 47 - Arco composito sesso
            self.comboBox_ramo_ip_I.setEditText(self.DATA_LIST[self.rec_num].ramo_ip_I)  # 48 - Ramo ischio pubico I
            self.comboBox_ramo_ip_II.setEditText(self.DATA_LIST[self.rec_num].ramo_ip_II)  # 49 - Ramo ischio pubico II
            self.comboBox_ramo_ip_III.setEditText(
                self.DATA_LIST[self.rec_num].ramo_ip_III)  # 50 - Ramo ischio pubico III
            self.comboBox_ramo_ip_sex.setEditText(
                self.DATA_LIST[self.rec_num].ramo_ip_sex)  # 51 - Ramo ischio pubico sesso
            self.comboBox_prop_ip_sex.setEditText(
                self.DATA_LIST[self.rec_num].prop_ip_sex)  # 52 - Proporzioni ischio pubiche sesso
            self.comboBox_ind_bac_sex.setEditText(
                self.DATA_LIST[self.rec_num].ind_bac_sex)  # 53 - Indice sessualizzazione bacino

        except :
            pass#QMessageBox.warning(self, "Errore", "giigi" + str(e), QMessageBox.Ok)

    def set_rec_counter(self, t, c):
        self.rec_tot = t
        self.rec_corr = c
        self.label_rec_tot.setText(str(self.rec_tot))
        self.label_rec_corrente.setText(str(self.rec_corr))

    def set_LIST_REC_TEMP(self):

        if self.comboBox_glab_valori.currentText() == "":
            glab_valori = None
        else:
            glab_valori = str(self.comboBox_glab_valori.currentText())

        if self.comboBox_pmast_valori.currentText() == "":
            pmast_valori = None
        else:
            pmast_valori = str(self.comboBox_pmast_valori.currentText())

        if self.comboBox_pnuc_valori.currentText() == "":
            pnuc_valori = None
        else:
            pnuc_valori = str(self.comboBox_pnuc_valori.currentText())

        if self.comboBox_pzig_valori.currentText() == "":
            pzig_valori = None
        else:
            pzig_valori = str(self.comboBox_pzig_valori.currentText())

        if self.comboBox_arcsop_valori.currentText() == "":
            arcsop_valori = None
        else:
            arcsop_valori = str(self.comboBox_arcsop_valori.currentText())

        if self.comboBox_tub_valori.currentText() == "":
            tub_valori = None
        else:
            tub_valori = str(self.comboBox_tub_valori.currentText())

        if self.comboBox_pocc_valori.currentText() == "":
            pocc_valori = None
        else:
            pocc_valori = str(self.comboBox_pocc_valori.currentText())

        if self.comboBox_inclfr_valori.currentText() == "":
            inclfr_valori = None
        else:
            inclfr_valori = str(self.comboBox_inclfr_valori.currentText())

        if self.comboBox_zig_valori.currentText() == "":
            zig_valori = None
        else:
            zig_valori = str(self.comboBox_zig_valori.currentText())

        if self.comboBox_msorb_valori.currentText() == "":
            msorb_valori = None
        else:
            msorb_valori = str(self.comboBox_msorb_valori.currentText())

        if self.comboBox_palato_valori.currentText() == "":
            palato_valori = None
        else:
            palato_valori = str(self.comboBox_palato_valori.currentText())

        if self.comboBox_mfmand_valori.currentText() == "":
            mfmand_valori = None
        else:
            mfmand_valori = str(self.comboBox_mfmand_valori.currentText())

        if self.comboBox_mento_valori.currentText() == "":
            mento_valori = None
        else:
            mento_valori = str(self.comboBox_mento_valori.currentText())

        if self.comboBox_anmand_valori.currentText() == "":
            anmand_valori = None
        else:
            anmand_valori = str(self.comboBox_anmand_valori.currentText())

        if self.comboBox_minf_valori.currentText() == "":
            minf_valori = None
        else:
            minf_valori = str(self.comboBox_minf_valori.currentText())

        if self.comboBox_brmont_valori.currentText() == "":
            brmont_valori = None
        else:
            brmont_valori = str(self.comboBox_brmont_valori.currentText())

        if self.comboBox_condm_valori.currentText() == "":
            condm_valori = None
        else:
            condm_valori = str(self.comboBox_condm_valori.currentText())

        if self.lineEdit_sex_cr_tot.text() == "":
            sex_cr_tot = None
        else:
            sex_cr_tot = str(self.lineEdit_sex_cr_tot.text())

            # data
        self.DATA_LIST_REC_TEMP = [
            str(self.comboBox_sito.currentText()),  # 1 - Sito
            str(self.lineEdit_nr_individuo.text()),  # 2 - Numero individuo
            str(self.lineEdit_glab_grado_imp.text()),  # 3 - Glabella grado imp
            str(self.lineEdit_pmast_grado_imp.text()),  # 4 - Processo mastoideo	grado imp
            str(self.lineEdit_pnuc_grado_imp.text()),  # 5 - Piano nucale grado	imp
            str(self.lineEdit_pzig_grado_imp.text()),  # 6 - Processo zigomatico grado imp
            str(self.lineEdit_arcsop_grado_imp.text()),  # 7 - Arcata sopraciliare grado imp
            str(self.lineEdit_tub_grado_imp.text()),  # 8 - Tuberosita' frontale e parietale grado imp
            str(self.lineEdit_pocc_grado_imp.text()),  # 9 - Protuberanza occipitale esterna grado imp
            str(self.lineEdit_inclfr_grado_imp.text()),  # 10 - Inclinazione frontale grado imp
            str(self.lineEdit_zig_grado_imp.text()),  # 11 - Osso zigomatico grado imp
            str(self.lineEdit_msorb_grado_imp.text()),  # 12 - Margine sopraorbitale grado imp
            str(glab_valori),  # 13 - Glabella valori
            str(pmast_valori),  # 14 - Processo mastoideo valori
            str(pnuc_valori),  # 15 - Piano nucale valori
            str(pzig_valori),  # 16 - Processo zigomatico valori
            str(arcsop_valori),  # 17 - Arcata sopraciliare valori
            str(tub_valori),  # 18 - Tuberosita' frontale e parietale valori
            str(pocc_valori),  # 19 - Protuberanza occipitale esterna valori
            str(inclfr_valori),  # 20 - Inclinazione frontale valori
            str(zig_valori),  # 21 - Osso zigomatico valori
            str(msorb_valori),  # 22 - Margine sopraorbitale valori
            str(self.lineEdit_palato_grado_imp.text()),  # 23 - Palato grado imp
            str(self.lineEdit_mfmand_grado_imp.text()),  # 24 - Morfologia mandibola grado imp
            str(self.lineEdit_mento_grado_imp.text()),  # 25 - Mento grado imp
            str(self.lineEdit_anmand_grado_imp.text()),  # 26 - Angolo mandibolare grado imp
            str(self.lineEdit_minf_grado_imp.text()),  # 27 - Margine inferiore	grado imp
            str(self.lineEdit_brmont_grado_imp.text()),  # 28 - Branca montante grado imp
            str(self.lineEdit_condm_grado_imp.text()),  # 29 - Condilo mandibolare grado	imp
            str(palato_valori),  # 30 - Palato valori
            str(mfmand_valori),  # 31 - Morfologia mandibola valori
            str(mento_valori),  # 32 - Mento valori
            str(anmand_valori),  # 33 - Angolo mandibolare valori
            str(minf_valori),  # 34 - Margine inferiore	valori
            str(brmont_valori),  # 35 - Branca montante valori
            str(condm_valori),  # 36 - Condilo mandibolare valori
            str(sex_cr_tot),  # 37 - Valore totale sex	cranio
            str(self.comboBox_ind_cr_sex.currentText()),  # 38 - Indice sessualizzazione cranio
            str(self.comboBox_sup_p_I.currentText()),  # 39 - Superficie preauricolare I
            str(self.comboBox_sup_p_II.currentText()),  # 40 - Superficie preauricolare II
            str(self.comboBox_sup_p_III.currentText()),  # 41 - Superficie preauricolare III
            str(self.comboBox_sup_p_sex.currentText()),  # 42 - Superficie preauricolare sesso
            str(self.comboBox_in_isch_I.currentText()),  # 43 - Grande incisura ischiatica I
            str(self.comboBox_in_isch_II.currentText()),  # 44 - Grande incisura ischiatica II
            str(self.comboBox_in_isch_III.currentText()),  # 45 - Grande incisura ischiatica III
            str(self.comboBox_in_isch_sex.currentText()),  # 46 - Grande incisura ischiatica sesso
            str(self.comboBox_arco_c_sex.currentText()),  # 47 - Arco composito sesso
            str(self.comboBox_ramo_ip_I.currentText()),  # 48 - Ramo ischio pubico I
            str(self.comboBox_ramo_ip_II.currentText()),  # 49 - Ramo ischio pubico II
            str(self.comboBox_ramo_ip_III.currentText()),  # 50 - Ramo ischio pubico III
            str(self.comboBox_ramo_ip_sex.currentText()),  # 51 - Ramo ischio pubico sesso
            str(self.comboBox_prop_ip_sex.currentText()),  # 52 - Proporzioni ischio pubiche sesso
            str(self.comboBox_ind_bac_sex.currentText())]  # 53 - Indice sessualizzazione bacino

    def set_LIST_REC_CORR(self):
        self.DATA_LIST_REC_CORR = []
        for i in self.TABLE_FIELDS:
            self.DATA_LIST_REC_CORR.append(eval("str(self.DATA_LIST[self.REC_CORR]." + i + ")"))

    def records_equal_check(self):
        self.set_LIST_REC_TEMP()
        self.set_LIST_REC_CORR()
        # f = open('/test_rec_corr_det_sesso.txt', 'w')
        # test = str(self.DATA_LIST_REC_CORR) + " " + str(self.DATA_LIST_REC_TEMP)
        # f.write(test)
        # f.close()

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

    def charge_id_us_for_individuo(self):
        data_list_us = []
        for rec in range(len(self.DATA_LIST)):
            sito = "'" + str(self.DATA_LIST[rec].sito) + "'"
            area = "'" + str(self.DATA_LIST[rec].area) + "'"
            us = int(self.DATA_LIST[rec].us)

            serch_dict_us = {'sito': sito, 'area': area, 'us': us}
            us_ind = self.DB_MANAGER.query_bool(serch_dict_us, "US")
            data_list_us.append(us_ind)

        data_list_id_us = []
        for us in range(len(data_list_us)):
            data_list_id_us.append(data_list_us[us][0].id_us)

        return data_list_id_us

    def on_pushButton_calcola_ind_sex_pressed(self):
        lista_risultati_gxv = []
        lista_gradi_utilizzati = []

        if self.comboBox_glab_valori.currentText() != "":
            lista_risultati_gxv.append(
                int(self.lineEdit_glab_grado_imp.text()) * int(self.comboBox_glab_valori.currentText()))
            lista_gradi_utilizzati.append(int(self.lineEdit_glab_grado_imp.text()))

        if self.comboBox_pmast_valori.currentText() != "":
            lista_risultati_gxv.append(
                int(self.lineEdit_pmast_grado_imp.text()) * int(self.comboBox_pmast_valori.currentText()))
            lista_gradi_utilizzati.append(int(self.lineEdit_pmast_grado_imp.text()))

        if self.comboBox_pnuc_valori.currentText() != "":
            lista_risultati_gxv.append(
                int(self.lineEdit_pnuc_grado_imp.text()) * int(self.comboBox_pnuc_valori.currentText()))
            lista_gradi_utilizzati.append(int(self.lineEdit_pnuc_grado_imp.text()))

        if self.comboBox_pzig_valori.currentText() != "":
            lista_risultati_gxv.append(
                int(self.lineEdit_pzig_grado_imp.text()) * int(self.comboBox_pzig_valori.currentText()))
            lista_gradi_utilizzati.append(int(self.lineEdit_pzig_grado_imp.text()))

        if self.comboBox_arcsop_valori.currentText() != "":
            lista_risultati_gxv.append(
                int(self.lineEdit_arcsop_grado_imp.text()) * int(self.comboBox_arcsop_valori.currentText()))
            lista_gradi_utilizzati.append(int(self.lineEdit_arcsop_grado_imp.text()))

        if self.comboBox_tub_valori.currentText() != "":
            lista_risultati_gxv.append(
                int(self.lineEdit_tub_grado_imp.text()) * int(self.comboBox_tub_valori.currentText()))
            lista_gradi_utilizzati.append(int(self.lineEdit_tub_grado_imp.text()))

        if self.comboBox_pocc_valori.currentText() != "":
            lista_risultati_gxv.append(
                int(self.lineEdit_pocc_grado_imp.text()) * int(self.comboBox_pocc_valori.currentText()))
            lista_gradi_utilizzati.append(int(self.lineEdit_pocc_grado_imp.text()))

        if self.comboBox_inclfr_valori.currentText() != "":
            lista_risultati_gxv.append(
                int(self.lineEdit_inclfr_grado_imp.text()) * int(self.comboBox_inclfr_valori.currentText()))
            lista_gradi_utilizzati.append(int(self.lineEdit_inclfr_grado_imp.text()))

        if self.comboBox_zig_valori.currentText() != "":
            lista_risultati_gxv.append(
                int(self.lineEdit_zig_grado_imp.text()) * int(self.comboBox_zig_valori.currentText()))
            lista_gradi_utilizzati.append(int(self.lineEdit_zig_grado_imp.text()))

        if self.comboBox_msorb_valori.currentText() != "":
            lista_risultati_gxv.append(
                int(self.lineEdit_msorb_grado_imp.text()) * int(self.comboBox_msorb_valori.currentText()))
            lista_gradi_utilizzati.append(int(self.lineEdit_msorb_grado_imp.text()))

        if self.comboBox_palato_valori.currentText() != "":
            lista_risultati_gxv.append(
                int(self.lineEdit_palato_grado_imp.text()) * int(self.comboBox_palato_valori.currentText()))
            lista_gradi_utilizzati.append(int(self.lineEdit_palato_grado_imp.text()))

        if self.comboBox_mfmand_valori.currentText() != "":
            lista_risultati_gxv.append(
                int(self.lineEdit_mfmand_grado_imp.text()) * int(self.comboBox_mfmand_valori.currentText()))
            lista_gradi_utilizzati.append(int(self.lineEdit_mfmand_grado_imp.text()))

        if self.comboBox_mento_valori.currentText() != "":
            lista_risultati_gxv.append(
                int(self.lineEdit_mento_grado_imp.text()) * int(self.comboBox_mento_valori.currentText()))
            lista_gradi_utilizzati.append(int(self.lineEdit_mento_grado_imp.text()))

        if self.comboBox_anmand_valori.currentText() != "":
            lista_risultati_gxv.append(
                int(self.lineEdit_anmand_grado_imp.text()) * int(self.comboBox_anmand_valori.currentText()))
            lista_gradi_utilizzati.append(int(self.lineEdit_anmand_grado_imp.text()))

        if self.comboBox_minf_valori.currentText() != "":
            lista_risultati_gxv.append(
                int(self.lineEdit_minf_grado_imp.text()) * int(self.comboBox_minf_valori.currentText()))
            lista_gradi_utilizzati.append(int(self.lineEdit_minf_grado_imp.text()))

        if self.comboBox_brmont_valori.currentText() != "":
            lista_risultati_gxv.append(
                int(self.lineEdit_brmont_grado_imp.text()) * int(self.comboBox_brmont_valori.currentText()))
            lista_gradi_utilizzati.append(int(self.lineEdit_brmont_grado_imp.text()))

        if self.comboBox_condm_valori.currentText() != "":
            lista_risultati_gxv.append(
                int(self.lineEdit_condm_grado_imp.text()) * int(self.comboBox_condm_valori.currentText()))
            lista_gradi_utilizzati.append(int(self.lineEdit_condm_grado_imp.text()))

        somma_gradi_utilizzati = 0
        for i in lista_gradi_utilizzati:
            somma_gradi_utilizzati += i

        somma_gxv_utilizzati = 0
        for i in lista_risultati_gxv:
            somma_gxv_utilizzati += i

        try:
            valore_totale = float(somma_gxv_utilizzati) / float(somma_gradi_utilizzati)

            indice_sessualizzazione = ""
            valori_indice_sessualizzazione = {"femmina_valore_min": -2, "femmina_valore_max": -0.39,
                                              "indeterminato_valore_min": -0.4, "indeterminato_valore_max": 0.4,
                                              "maschio_valore_min": 0.41, "maschio_valore_max": 2}

            if valori_indice_sessualizzazione["femmina_valore_min"] <= valore_totale <= valori_indice_sessualizzazione[
                "femmina_valore_max"]:
                indice_sessualizzazione = "Femmina"
            elif valori_indice_sessualizzazione["indeterminato_valore_min"] <= valore_totale <= \
                    valori_indice_sessualizzazione["indeterminato_valore_max"]:
                indice_sessualizzazione = "Indeterminato"
            elif valori_indice_sessualizzazione["maschio_valore_min"] <= valore_totale <= \
                    valori_indice_sessualizzazione["maschio_valore_max"]:
                indice_sessualizzazione = "Maschio"

            dati = "somma_gradi_utilizzati " + str(somma_gradi_utilizzati) + " \n somma gxv utilizzati " + str(
                somma_gxv_utilizzati) + " \n valore totale " + str(
                valore_totale) + " \n indice sessualizzazione " + str(indice_sessualizzazione)

            self.lineEdit_sex_cr_tot.setText(str(valore_totale))
            self.comboBox_ind_cr_sex.setEditText(str(indice_sessualizzazione))

            self.on_pushButton_save_pressed()
        except:
            QMessageBox.warning(self, "Messaggio", "Inserisci almeno un carattere diagnostico.", QMessageBox.Ok)

    def on_pushButton_cranio_pressed(self):
        self.open_tables_det_eta(13)

    def on_pushButton_bacino_sup_preauricolare_pressed(self):
        self.open_tables_det_eta(14)

    def on_pushButton_bacino_grande_incisura_ischiatica_pressed(self):
        self.open_tables_det_eta(15)

    def on_pushButton_bacino_arco_composito_pressed(self):
        self.open_tables_det_eta(16)

    def on_pushButton_bacino_ramo_ischio_pubico_pressed(self):
        self.open_tables_det_eta(17)

    def on_pushButton_proporzioni_ischio_pubiche_pressed(self):
        self.open_tables_det_eta(18)

        # PULSANTI IMMAGINI

    def open_tables_det_eta(self, n):
        # apre la finestra di visualizzazione delle immagini in base al valore n
        filepath = os.path.dirname(__file__)
        dlg = ImageViewer(self)

        if n == 1:  # tavola sinfisi pubica femmminile
            try:
                anthropo_image_path = '{}{}'.format(
                    filepath, os.path.join(os.sep, os.pardir, 'resources/anthropo_images/sinfisi_pubica_femmine.jpg'))
                dlg.show_image(str(anthropo_image_path))  # item.data(QtCore.Qt.UserRole).toString()))
                dlg.exec_()
            except Exception as e:
                QMessageBox.warning(self, "Errore", "Attenzione 1 file: " + str(e), QMessageBox.Ok)

        if n == 2:  # tavola sinfisi pubica maschile
            try:
                anthropo_image_path = '{}{}'.format(
                    filepath, os.path.join(os.sep, os.pardir, 'resources/anthropo_images/sinfisi_pubica_maschi.jpg'))
                dlg.show_image(str(anthropo_image_path))  # item.data(QtCore.Qt.UserRole).toString()))
                dlg.exec_()
            except Exception as e:
                QMessageBox.warning(self, "Errore", "Attenzione 1 file: " + str(e), QMessageBox.Ok)

        if n == 3:  # tavola superficie auricolare SSPIA
            try:
                anthropo_image_path = '{}{}'.format(
                    filepath, os.path.join(os.sep, os.pardir, 'resources/anthropo_images/det_eta_Kimmerle_femmine.jpg'))
                print(anthropo_image_path)
                dlg.show_image(str(anthropo_image_path))  # item.data(QtCore.Qt.UserRole).toString()))
                dlg.exec_()
            except Exception as e:
                QMessageBox.warning(self, "Errore", "Attenzione 1 file: " + str(e), QMessageBox.Ok)

        if n == 13:  # tavola cranio
            try:
                anthropo_images_path = '{}{}'.format(
                    filepath, os.path.join(os.sep, os.pardir, 'resources/anthropo_images/det_eta_Kimmerle_femmine.jpg'))
                print(anthropo_images_path)
                dlg.show_image(str(anthropo_images_path))  # item.data(QtCore.Qt.UserRole).toString()))
                dlg.exec_()
            except Exception as e:
                QMessageBox.warning(self, "Errore", "Attenzione 1 file: " + str(e), QMessageBox.Ok)

        if n == 14:  # tavola bacino sup. preauricolare
            try:
                anthropo_images_path = '{}{}'.format(
                    filepath, os.path.join(os.sep, os.pardir, 'resources/anthropo_images/detsesso_bacino_sup_preauricolare.jpg'))
                dlg.show_image(str(anthropo_images_path))  # item.data(QtCore.Qt.UserRole).toString()))
                dlg.exec_()
            except Exception as e:
                QMessageBox.warning(self, "Errore", "Attenzione 1 file: " + str(e), QMessageBox.Ok)

        if n == 15:  # tavola bacino incisura ischiatica
            try:
                anthropo_images_path = '{}{}'.format(
                    filepath, os.path.join(os.sep, os.pardir, 'resources/anthropo_images/detsesso_bacino_grande incisura ischiatica.jpg'))
                dlg.show_image(str(anthropo_images_path))  # item.data(QtCore.Qt.UserRole).toString()))
                dlg.exec_()
            except Exception as e:
                QMessageBox.warning(self, "Errore", "Attenzione 1 file: " + str(e), QMessageBox.Ok)

        if n == 16:  # tavola bacino arco composito
            try:
                anthropo_images_path = '{}{}'.format(
                    filepath, os.path.join(os.sep, os.pardir, 'resources/anthropo_images/detsesso_bacino_arco composito.jpg'))
                dlg.show_image(str(anthropo_images_path))  # item.data(QtCore.Qt.UserRole).toString()))
                dlg.exec_()
            except Exception as e:
                QMessageBox.warning(self, "Errore", "Attenzione 1 file: " + str(e), QMessageBox.Ok)

        if n == 17:  # tavola bacino ramo ischio-pubico
            try:
                anthropo_images_path = '{}{}'.format(
                    filepath, os.path.join(os.sep, os.pardir, 'resources/anthropo_images/detsesso_bacino_ramo ischio-pubico.jpg'))
                dlg.show_image(str(anthropo_images_path))  # item.data(QtCore.Qt.UserRole).toString()))
                dlg.exec_()
            except Exception as e:
                QMessageBox.warning(self, "Errore", "Attenzione 1 file: " + str(e), QMessageBox.Ok)

        if n == 18:  # tavola bacino proporzioni ischio-pubiche
            try:
                anthropo_images_path = '{}{}'.format(
                    filepath, os.path.join(os.sep, os.pardir, 'resources/anthropo_images/detsesso_bacino_proporzioni ischio-pubiche.jpg'))
                dlg.show_image(str(anthropo_images_path))  # item.data(QtCore.Qt.UserRole).toString()))
                dlg.exec_()
            except Exception as e:
                QMessageBox.warning(self, "Errore", "Attenzione 1 file: " + str(e), QMessageBox.Ok)

    def on_pushButton_calcola_ind_sex_bac_pressed(self):
        sup_p_sex = self.find_ind_sex(
            [str(self.comboBox_sup_p_I.currentText()), str(self.comboBox_sup_p_II.currentText()),
             str(self.comboBox_sup_p_III.currentText())])  # Superficie preauricolare sesso
        self.comboBox_sup_p_sex.setEditText(str(sup_p_sex))  # Superficie preauricolare sesso

        in_isch_sex = self.find_ind_sex(
            [str(self.comboBox_in_isch_I.currentText()), str(self.comboBox_in_isch_II.currentText()),
             str(self.comboBox_in_isch_III.currentText())])  # Grande incisura ischiatica sesso
        self.comboBox_in_isch_sex.setEditText(str(in_isch_sex))  # Grande incisura ischiatica sesso

        arco_c_sex = str(self.comboBox_arco_c_sex_2.currentText())  # 47 - Arco composito sesso
        self.comboBox_arco_c_sex.setEditText(str(arco_c_sex))

        ramo_ip_sex = self.find_ind_sex(
            [str(self.comboBox_ramo_ip_I.currentText()), str(self.comboBox_ramo_ip_II.currentText()),
             str(self.comboBox_ramo_ip_III.currentText())])  # Ramo ischio pubico sesso
        self.comboBox_ramo_ip_sex.setEditText(str(ramo_ip_sex))  # Ramo ischio pubico sesso

        prop_ip_sex = str(self.comboBox_prop_ip_sex_2.currentText())  # Proporzioni ischio pubiche sesso
        self.comboBox_prop_ip_sex.setEditText(str(prop_ip_sex))

        ind_bac_sex = self.find_ind_sex([sup_p_sex, in_isch_sex, arco_c_sex, ramo_ip_sex, prop_ip_sex])

        diz_ind_sex = {"": "Dati insufficienti", "M": "Maschio", "F": "Femmina", "I": "Indeterminato"}
        self.comboBox_ind_bac_sex.setEditText(diz_ind_sex[ind_bac_sex])  # Indice sessualizzazione totale

        self.on_pushButton_save_pressed()

    def find_ind_sex(self, sing_char_list):
        self.sing_char_list = sing_char_list

        ind_sex_b_parz = "Error"

        F = 0  # carattere femminile
        I = 0  # carattere non identificabile al momento per livello di conoscenze dello schedatore o della disciplina
        M = 0  # carattere maschile
        E = 0  # carattere non determinabile per carenza di dati derivanti dalla storia post-deposizionale del reperto

        for i in self.sing_char_list:
            if i == "F":
                F += 1
            if i == "M":
                M += 1
            if i == "I":
                I += 1
            if i == "":
                E += 1

        if E > 0 and F <= E and M <= E and I <= E:
            ind_sex_b_parz = ""

        elif I > 0 and F <= 1 and M <= 1 and E <= 1:
            ind_sex_b_parz = "I"

        elif I > M and I > F and I > E:
            ind_sex_b_parz = "I"

        elif F > I and F > M and F > E:
            ind_sex_b_parz = "F"

        elif M > I and M > F and M > E:
            ind_sex_b_parz = "M"

        elif E > M and E > F and E > I:
            ind_sex_b_parz = ""
        else:
            ind_sex_b_parz = "I"

        return ind_sex_b_parz

    def testing(self, name_file, message):
        f = open(str(name_file), 'w')
        f.write(str(message))
        f.close()

## Class end
