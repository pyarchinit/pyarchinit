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
from builtins import str
from builtins import range

from qgis.PyQt.QtWidgets import QDialog, QMessageBox
from qgis.PyQt.uic import loadUiType
from qgis.core import Qgis, QgsSettings

import platform
import subprocess
import os


from ..modules.db.pyarchinit_conn_strings import Connection
from ..modules.db.pyarchinit_db_manager import Pyarchinit_db_management
from ..modules.db.pyarchinit_utility import *
from ..modules.utility.pyarchinit_exp_USsheet_pdf import generate_US_pdf
from ..modules.utility.pyarchinit_exp_Findssheet_pdf import generate_reperti_pdf
from ..modules.utility.pyarchinit_exp_Periodizzazionesheet_pdf import generate_Periodizzazione_pdf
from ..modules.utility.pyarchinit_exp_Individui_pdf import generate_pdf
from ..modules.utility.pyarchinit_exp_Strutturasheet_pdf import generate_struttura_pdf
from ..modules.utility.pyarchinit_exp_Tombasheet_pdf import generate_tomba_pdf
from ..modules.utility.pyarchinit_exp_Campsheet_pdf import generate_campioni_pdf
from ..modules.utility.pyarchinit_OS_utility import Pyarchinit_OS_Utility
MAIN_DIALOG_CLASS, _ = loadUiType(os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'Pdf_export.ui'))


class pyarchinit_pdf_export(QDialog, MAIN_DIALOG_CLASS):
    UTILITY = Utility()
    OS_UTILITY = Pyarchinit_OS_Utility()
    DB_MANAGER = ""
    HOME = ""
    DATA_LIST = []
    L=QgsSettings().value("locale/userLocale")[0:2]
    ##  if os.name == 'posix':
    ##      HOME = os.environ['HOME']
    ##  elif os.name == 'nt':
    ##      HOME = os.environ['HOMEPATH']
    ##
    ##  PARAMS_DICT={'SERVER':'',
    ##              'HOST': '',
    ##              'DATABASE':'',
    ##              'PASSWORD':'',
    ##              'PORT':'',
    ##              'USER':'',
    ##              'THUMB_PATH':''}

    def __init__(self, iface):
        super().__init__()
        # Set up the user interface from Designer.
        self.setupUi(self)

        self.iface = iface

        try:
            self.connect()
        except:
            pass
        self.charge_list()
        self.set_home_path()

        # self.load_dict()
        # self.charge_data()

    def connect(self):
        #QMessageBox.warning(self, "Alert",
                            #"Sistema sperimentale. Esporta le schede PDF in /vostro_utente/pyarchinit_DB_folder. Sostituisce i documenti gia' presenti. Se volete conservarli fatene una copia o rinominateli.",
                            #QMessageBox.Ok)

        conn = Connection()
        conn_str = conn.conn_str()
        try:
            self.DB_MANAGER = Pyarchinit_db_management(conn_str)
            self.DB_MANAGER.connection()
        except Exception as e:
            e = str(e)
                        
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
            
    def charge_list(self):
        # lista sito
        sito_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('site_table', 'sito', 'SITE'))
        try:
            sito_vl.remove('')
        except:
            pass

        self.comboBox_sito.clear()

        sito_vl.sort()
        self.comboBox_sito.addItems(sito_vl)

    def set_home_path(self):
        self.HOME = os.environ['PYARCHINIT_HOME']

    def on_pushButton_open_dir_pressed(self):
        path = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_PDF_folder")

        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

    def messageOnSuccess(self, printed):
        if printed:
            self.iface.messageBar().pushMessage("Exportation ok", Qgis.Success)
        else:
            self.iface.messageBar().pushMessage("Exportation falied", Qgis.Info)

    def on_pushButton_exp_pdf_pressed(self):
        sito = str(self.comboBox_sito.currentText())
        
        ####Esportazione della Scheda e indice US
        
        if self.checkBox_US.isChecked():

            us_res = self.db_search_DB('US', 'sito', sito)

            if bool(us_res):
                
                id_list = []
                for i in range(len(us_res)):
                    id_list.append(us_res[i].id_us)

                temp_data_list = self.DB_MANAGER.query_sort(id_list, ['area', 'us'], 'asc', 'US', 'id_us')
                for i in temp_data_list:
                    self.DATA_LIST.append(i)

                if len(self.DATA_LIST) < 1:
                    QMessageBox.warning(self, "Alert", "No form to print, before you need fill it", QMessageBox.Ok)
                else:
                    
                    US_pdf_sheet = generate_US_pdf()
                    data_list = self.generate_list_US_pdf()
                    if self.L=='it':
                        US_pdf_sheet.build_US_sheets(data_list)  # export sheet
                        US_pdf_sheet.build_index_US(data_list, data_list[0][0])  # export list
                    elif self.L=='de':
                        US_pdf_sheet.build_US_sheets_de(data_list)  # export sheet
                        US_pdf_sheet.build_index_US_de(data_list, data_list[0][0])  # export list
                    else:
                        US_pdf_sheet.build_US_sheets_en(data_list)  # export sheet
                        US_pdf_sheet.build_index_US_en(data_list, data_list[0][0])  # export list   
                    
            if self.DATA_LIST:
                printed = True
                self.DATA_LIST = []
            self.messageOnSuccess(printed)
        ####Esportazione della Scheda e indice Periodizzazione
        if self.checkBox_periodo.isChecked():

            periodizzazione_res = self.db_search_DB('PERIODIZZAZIONE', 'sito', sito)

            if bool(periodizzazione_res):
                id_list = []
                for i in range(len(periodizzazione_res)):
                    id_list.append(periodizzazione_res[i].id_perfas)

                temp_data_list = self.DB_MANAGER.query_sort(id_list, ['cont_per'], 'asc', 'PERIODIZZAZIONE',
                                                            'id_perfas')

                for i in temp_data_list:
                    self.DATA_LIST.append(i)

                Periodizzazione_pdf_sheet = generate_Periodizzazione_pdf()  # deve essere importata la classe
                data_list = self.generate_list_periodizzazione_pdf()  # deve essere aggiunta la funzione
                if self.L=='it':
                    Periodizzazione_pdf_sheet.build_Periodizzazione_sheets(
                        data_list)  # deve essere aggiunto il file per generare i pdf
                    Periodizzazione_pdf_sheet.build_index_Periodizzazione(data_list, data_list[0][
                        0])  # deve essere aggiunto il file per generare i pdf
                elif self.L=='de':
                    Periodizzazione_pdf_sheet.build_Periodizzazione_sheets_de(
                        data_list)  # deve essere aggiunto il file per generare i pdf
                    Periodizzazione_pdf_sheet.build_index_Periodizzazione_de(data_list, data_list[0][
                        0])  # deve essere aggiunto il file per generare i pdf
                else:
                    Periodizzazione_pdf_sheet.build_Periodizzazione_sheets_en(
                        data_list)  # deve essere aggiunto il file per generare i pdf
                    Periodizzazione_pdf_sheet.build_index_Periodizzazione_en(data_list, data_list[0][
                        0])  # deve essere aggiunto il file per generare i pdf      
                        
                        
            if self.DATA_LIST:
                printed = True
                self.DATA_LIST = []
            self.messageOnSuccess(printed)
        ####Esportazione della Scheda e indice Struttura
        if self.checkBox_struttura.isChecked():
            struttura_res = self.db_search_DB('STRUTTURA', 'sito', sito)

            if bool(struttura_res):
                id_list = []
                for i in range(len(struttura_res)):
                    id_list.append(struttura_res[i].id_struttura)

                temp_data_list = self.DB_MANAGER.query_sort(id_list, ['sigla_struttura', 'numero_struttura'], 'asc',
                                                            'STRUTTURA', 'id_struttura')

                for i in temp_data_list:
                    self.DATA_LIST.append(i)

                Struttura_pdf_sheet = generate_struttura_pdf()  # deve essere importata la classe
                data_list = self.generate_list_struttura_pdf()  # deve essere aggiunta la funzione
                
                if self.L=='it':
                    Struttura_pdf_sheet.build_Struttura_sheets(
                        data_list)  # deve essere aggiunto il file per generare i pdf
                    Struttura_pdf_sheet.build_index_Struttura(data_list, data_list[0][0])
                elif self.L=='de':
                    Struttura_pdf_sheet.build_Struttura_sheets_de(data_list)  # deve essere aggiunto il file per generare i pdf
                    Struttura_pdf_sheet.build_index_Struttura_de(data_list, data_list[0][0])
                else:
                    Struttura_pdf_sheet.build_Struttura_sheets_en(data_list)  # deve essere aggiunto il file per generare i pdf
                    Struttura_pdf_sheet.build_index_Struttura_en(data_list, data_list[0][0])    

            if self.DATA_LIST:
                printed = True
                self.DATA_LIST = []
                
            self.messageOnSuccess(printed)        
        ####Esportazione della Scheda materiali
        if self.checkBox_reperti.isChecked():
            reperti_res = self.db_search_DB('INVENTARIO_MATERIALI', 'sito', sito)

            if bool(reperti_res):
                id_list = []
                for i in range(len(reperti_res)):
                    id_list.append(reperti_res[i].id_invmat)

                temp_data_list = self.DB_MANAGER.query_sort(id_list, ['numero_inventario'], 'asc',
                                                            'INVENTARIO_MATERIALI', 'id_invmat')

                for i in temp_data_list:
                    self.DATA_LIST.append(i)

                Finds_pdf_sheet = generate_reperti_pdf()
                data_list = self.generate_list_reperti_pdf()
                if self.L=='it':
                    Finds_pdf_sheet.build_Finds_sheets(data_list)
                    Finds_pdf_sheet.build_index_Finds(data_list, data_list[0][0])
                elif self.L=='de':
                    Finds_pdf_sheet.build_Finds_sheets_de(data_list)
                    Finds_pdf_sheet.build_index_Finds_de(data_list, data_list[0][0])
                else:
                    Finds_pdf_sheet.build_Finds_sheets_en(data_list)
                    Finds_pdf_sheet.build_index_Finds_en(data_list, data_list[0][0])    
                    
            if self.DATA_LIST:
                printed = True
                self.DATA_LIST = []
            self.messageOnSuccess(printed)
        ####Esportazione della Scheda tomba
        if self.checkBox_tomba.isChecked():
            tomba_res = self.db_search_DB('TOMBA', 'sito', sito)

            if bool(tomba_res):
                id_list = []
                for i in range(len(tomba_res)):
                    id_list.append(tomba_res[i].id_tomba)

                temp_data_list = self.DB_MANAGER.query_sort(id_list, ['nr_scheda_taf'], 'asc', 'TOMBA',
                                                            'id_tomba')

                for i in temp_data_list:
                    self.DATA_LIST.append(i)

                Tomba_pdf_sheet = generate_tomba_pdf()
                data_list = self.generate_list_tomba_pdf()
                
                if self.L=='it':
                    Tomba_pdf_sheet.build_Tomba_sheets(data_list)
                    Tomba_pdf_sheet.build_index_Tomba(data_list, data_list[0][0])
                elif self.L=='de':
                    Tomba_pdf_sheet.build_Tomba_sheets_de(data_list)
                    Tomba_pdf_sheet.build_index_Tomba(data_list, data_list[0][0])
                else:
                    Tomba_pdf_sheet.build_Tomba_sheets_en(data_list)
                    Tomba_pdf_sheet.build_index_Tomba(data_list, data_list[0][0])    
                    
            if self.DATA_LIST:
                printed = True
                self.DATA_LIST = []

        
            self.messageOnSuccess(printed)
        ####Esportazione della Scheda campioni
        if self.checkBox_campioni.isChecked():
            campioni_res = self.db_search_DB('CAMPIONI', 'sito', sito)

            if bool(campioni_res):
                id_list = []
                for i in range(len(campioni_res)):
                    id_list.append(campioni_res[i].id_campione)

                temp_data_list = self.DB_MANAGER.query_sort(id_list, ['nr_campione'], 'asc', 'CAMPIONI',
                                                            'id_campione')

                for i in temp_data_list:
                    self.DATA_LIST.append(i)

                Campioni_pdf_sheet = generate_campioni_pdf()
                data_list = self.generate_list_campioni_pdf()
                
                if self.L=='it':
                    Campioni_pdf_sheet.build_Champ_sheets(data_list)
                    Campioni_pdf_sheet.build_index_Campioni(data_list, data_list[0][0])
                elif self.L=='de':
                    Campioni_pdf_sheet.build_Champ_sheets_de(data_list)
                    Campioni_pdf_sheet.build_index_Campioni_de(data_list, data_list[0][0])
                else:
                    Campioni_pdf_sheet.build_Champ_sheets_en(data_list)
                    Campioni_pdf_sheet.build_index_Campioni_en(data_list, data_list[0][0])  
                    
            if self.DATA_LIST:
                printed = True
                self.DATA_LIST = []
            self.messageOnSuccess(printed)
        ####Esportazione della Scheda individui
        if self.checkBox_individui.isChecked():
            ind_res = self.db_search_DB('SCHEDAIND', 'sito', sito)

            if bool(ind_res):
                id_list = []
                for i in range(len(ind_res)):
                    id_list.append(ind_res[i].id_scheda_ind)

                temp_data_list = self.DB_MANAGER.query_sort(id_list, ['nr_individuo'], 'asc', 'SCHEDAIND',
                                                            'id_scheda_ind')

                for i in temp_data_list:
                    self.DATA_LIST.append(i)

                Ind_pdf_sheet = generate_pdf()
                data_list = self.generate_list_individui_pdf()
                
                if self.L=='it':
                    Ind_pdf_sheet.build_Individui_sheets(data_list)
                    Ind_pdf_sheet.build_index_individui(data_list, data_list[0][0])
                elif self.L=='de':
                    Ind_pdf_sheet.build_Individui_sheets_de(data_list)
                    Ind_pdf_sheet.build_index_individui_de(data_list, data_list[0][0])
                else:
                    Ind_pdf_sheet.build_Individui_sheets_en(data_list)
                    Ind_pdf_sheet.build_index_individui_en(data_list, data_list[0][0]) 
                    
            if self.DATA_LIST:
                printed = True
                self.DATA_LIST = []
            #self.messageOnSuccess(printed)
            self.messageOnSuccess(printed)
    def db_search_DB(self, table_class, field, value):
        self.table_class = table_class
        self.field = field
        self.value = value

        search_dict = {self.field: "'" + str(self.value) + "'"}

        u = Utility()
        search_dict = u.remove_empty_items_fr_dict(search_dict)

        res = self.DB_MANAGER.query_bool(search_dict, self.table_class)

        return res

    def generate_list_US_pdf(self):
        data_list = []
        #############inserimento nome fiel media############
        for i in range(len(self.DATA_LIST)):
            # assegnazione valori di quota mn e max
            id_us = str(self.DATA_LIST[i].id_us)
            sito = str(self.DATA_LIST[i].sito)#.replace('_',' '))
            area = str(self.DATA_LIST[i].area)
            us = str(self.DATA_LIST[i].us)
            res = self.DB_MANAGER.select_quote_from_db_sql(sito, area, us)
            quote = []
            for sing_us in res:
                sing_quota_value = str(sing_us[5])
                if sing_quota_value[0] == '-':
                    sing_quota_value = sing_quota_value[:7]
                else:
                    sing_quota_value = sing_quota_value[:6]
                sing_quota = [sing_quota_value, sing_us[4]]
                quote.append(sing_quota)
            quote.sort()
            if bool(quote):
                quota_min = '%s %s' % (quote[0][0], quote[0][1])
                quota_max = '%s %s' % (quote[-1][0], quote[-1][1])
            else:
                if self.L=='it':
                    quota_min = ""
                    quota_max = ""
                elif self.L == 'de':
                    quota_min = ""
                    quota_max = ""
                else :
                    quota_min = ""
                    quota_max = ""
                # assegnazione numero di pianta
            resus = self.DB_MANAGER.select_us_from_db_sql(sito, area, us, "2")
            elenco_record = []
            for us in resus:
                elenco_record.append(us)
            if bool(elenco_record):
                sing_rec = elenco_record[0]
                elenco_piante = sing_rec[6]
                if elenco_piante != None:
                    piante = elenco_piante
                else:
                    if self.L=='it':
                        piante = "US disegnata su base GIS" 
                    elif self.L=='de':
                        piante = "SE im GIS gezeichnet" 
                    else:
                        piante= "SU draft on GIS"
            else:
                if self.L=='it':
                    piante = "US disegnata su base GIS" 
                elif self.L=='de':
                    piante = "SE im GIS gezeichnet" 
                else:
                    piante= "SU draft on GIS"
            if self.DATA_LIST[i].quota_min_usm == None:
                quota_min_usm = ""
            else:
                quota_min_usm = str(self.DATA_LIST[i].quota_min_usm)
            if self.DATA_LIST[i].quota_max_usm == None:
                quota_max_usm = ""
            else:
                quota_max_usm = str(self.DATA_LIST[i].quota_max_usm)
            #nuovi campi per Archeo3
            if not self.DATA_LIST[i].quota_relativa:
                quota_relativa = ""  # 55
            else:
                quota_relativa = str(self.DATA_LIST[i].quota_relativa)
            if not self.DATA_LIST[i].quota_abs:
                quota_abs = ""  # 56
            else:
                quota_abs = str(self.DATA_LIST[i].quota_abs)
            if not self.DATA_LIST[i].lunghezza_max:
                lunghezza_max = ""
            else:
                lunghezza_max = str(self.DATA_LIST[i].lunghezza_max)  # 65 lunghezza max
            if not self.DATA_LIST[i].altezza_max:
                altezza_max = ""
            else:
                altezza_max = str(self.DATA_LIST[i].altezza_max)  # 66 altezza max
            if not self.DATA_LIST[i].altezza_min:
                altezza_min = ""
            else:
                altezza_min = str(self.DATA_LIST[i].altezza_min)  # 67 altezza min
            if not self.DATA_LIST[i].profondita_max:
                profondita_max = ""
            else:
                profondita_max = str(self.DATA_LIST[i].profondita_max)  # 68 profondita_max
            if not self.DATA_LIST[i].profondita_min:
                profondita_min = ""
            else:
                profondita_min = str(self.DATA_LIST[i].profondita_min)  # 69 profondita min
            if not self.DATA_LIST[i].larghezza_media:
                larghezza_media = ""
            else:
                larghezza_media = str(self.DATA_LIST[i].larghezza_media)  # 70 larghezza media
            if not self.DATA_LIST[i].quota_max_abs:
                quota_max_abs = ""
            else:
                quota_max_abs = str(self.DATA_LIST[i].quota_max_abs)  # 71 quota_max_abs
            if not self.DATA_LIST[i].quota_max_rel:
                quota_max_rel = ""
            else:
                quota_max_rel = str(self.DATA_LIST[i].quota_max_rel)  # 72 quota_max_rel
            if not self.DATA_LIST[i].quota_min_abs:
                quota_min_abs = ""
            else:
                quota_min_abs = str(self.DATA_LIST[i].quota_min_abs)  # 73 quota_min_abs
            if not self.DATA_LIST[i].quota_min_rel:
                quota_min_rel = ""
            else:
                quota_min_rel = str(self.DATA_LIST[i].quota_min_rel)  # 74 quota_min_rel
            if not self.DATA_LIST[i].lunghezza_usm:
                lunghezza_usm = ""
            else:
                lunghezza_usm = str(self.DATA_LIST[i].lunghezza_usm)  # 85 lunghezza usm
            if not self.DATA_LIST[i].altezza_usm:
                altezza_usm = ""
            else:
                altezza_usm = str(self.DATA_LIST[i].altezza_usm)  # 86 altezza usm
            if not self.DATA_LIST[i].spessore_usm:
                spessore_usm = ""
            else:
                spessore_usm = str(self.DATA_LIST[i].spessore_usm)  # 87 spessore usm
            data_list.append([
                str(self.DATA_LIST[i].sito.replace('_',' ')),  # 0 - Sito
                str(self.DATA_LIST[i].area),  # 1 - Area
                int(self.DATA_LIST[i].us),  # 2 - US
                str(self.DATA_LIST[i].d_stratigrafica),  # 3 - definizione stratigrafica
                str(self.DATA_LIST[i].d_interpretativa),  # 4 - definizione intepretata
                str(self.DATA_LIST[i].descrizione),  # 5 - descrizione
                str(self.DATA_LIST[i].interpretazione),  # 6 - interpretazione
                str(self.DATA_LIST[i].periodo_iniziale),  # 7 - periodo iniziale
                str(self.DATA_LIST[i].fase_iniziale),  # 8 - fase iniziale
                str(self.DATA_LIST[i].periodo_finale),  # 9 - periodo finale iniziale
                str(self.DATA_LIST[i].fase_finale),  # 10 - fase finale
                str(self.DATA_LIST[i].scavato),  # 11 - scavato
                str(self.DATA_LIST[i].attivita),  # 12 - attivita
                str(self.DATA_LIST[i].anno_scavo),  # 13 - anno scavo
                str(self.DATA_LIST[i].metodo_di_scavo),  # 14 - metodo
                str(self.DATA_LIST[i].inclusi),  # 15 - inclusi
                str(self.DATA_LIST[i].campioni),  # 16 - campioni
                str(self.DATA_LIST[i].rapporti),            # 17 - rapporti
                #str(self.DATA_LIST[i].organici),  # organici
                #str(self.DATA_LIST[i].inorganici),  # inorganici
                str(self.DATA_LIST[i].data_schedatura),  # 18 - data schedatura
                str(self.DATA_LIST[i].schedatore),  # 19 - schedatore
                str(self.DATA_LIST[i].formazione),  # 20 - formazione
                str(self.DATA_LIST[i].stato_di_conservazione),  # 21 - conservazione
                str(self.DATA_LIST[i].colore),  # 22 - colore
                str(self.DATA_LIST[i].consistenza),  # 23 - consistenza
                str(self.DATA_LIST[i].struttura),  # 24 - struttura
                str(quota_min),  # 25 - quota_min
                str(quota_max),  # 26 - quota_max
                str(piante),  # 27 - piante CAMPO RICAVATO DA GIS CON VALORI SI/NO
                str(self.DATA_LIST[i].documentazione),  # 28 - documentazione
                #campi USM
                str(self.DATA_LIST[i].unita_tipo),  # 29 - unita tipo
                str(self.DATA_LIST[i].settore),  # 30 - settore
                str(self.DATA_LIST[i].quad_par),  # 31 quadrato
                str(self.DATA_LIST[i].ambient),  # 32 ambiente
                str(self.DATA_LIST[i].saggio),  # 33 saggio
                str(self.DATA_LIST[i].elem_datanti),  # 34 - elem_datanti
                str(self.DATA_LIST[i].funz_statica),  # 35 - funz_statica
                str(self.DATA_LIST[i].lavorazione),  # 36 lavorazione
                str(self.DATA_LIST[i].spess_giunti),  # 37 spess_giunti
                str(self.DATA_LIST[i].letti_posa),            #38 letti posa
                str(self.DATA_LIST[i].alt_mod),               #39  al modulo
                str(self.DATA_LIST[i].un_ed_riass),           #40 unita edilizia riassuntiva
                str(self.DATA_LIST[i].reimp),                 #41 reimpiego
                str(self.DATA_LIST[i].posa_opera),            #42 posa opera
                str(quota_min_usm),                           #43 quota min usm
                str(quota_max_usm),                           #44 quota max usm
                str(self.DATA_LIST[i].cons_legante),          #45 cons legante
                str(self.DATA_LIST[i].col_legante),           #46 col legante
                str(self.DATA_LIST[i].aggreg_legante),        #47 aggreg legante
                str(self.DATA_LIST[i].con_text_mat),          #48  con text mat
                str(self.DATA_LIST[i].col_materiale),         #49  col materiale
                str(self.DATA_LIST[i].inclusi_materiali_usm),  #50 inclusi materili usm
                #NUOVI CAMPI PER ARCHEO3
                str(self.DATA_LIST[i].n_catalogo_generale),  # 51 nr catalogo generale campi aggiunti per archeo 3.0 e allineamento ICCD
                str(self.DATA_LIST[i].n_catalogo_interno),  # 52 nr catalogo interno
                str(self.DATA_LIST[i].n_catalogo_internazionale),  # 53 nr catalogo internazionale
                str(self.DATA_LIST[i].soprintendenza),  # 54 nr soprintendenza
                str(quota_relativa), #55 quota relativa
                str(quota_abs),   #56 quota assoluta
                str(self.DATA_LIST[i].ref_tm),  # 57 ref tm
                str(self.DATA_LIST[i].ref_ra),  # 58 ref ra
                str(self.DATA_LIST[i].ref_n),  # 59 ref n
                str(self.DATA_LIST[i].posizione),  # 60 posizione
                str(self.DATA_LIST[i].criteri_distinzione),  #61 criteri distinzione
                str(self.DATA_LIST[i].modo_formazione),  # 62 modo formazione
                str(self.DATA_LIST[i].componenti_organici),  # 63 componenti organici
                str(self.DATA_LIST[i].componenti_inorganici),  # 64 #  componenti inorganici
                str(lunghezza_max), #65 lunghezza max
                str(altezza_max), #66 altezza max
                str(altezza_min),  #67 altezza min
                str(profondita_max),  #68 profondita max
                str(profondita_min),  #69 profondita min
                str(larghezza_media),  #70 larghezza media
                str(quota_max_abs),   #71 quota max assoluta
                str(quota_max_rel),   #72 quota max rel
                str(quota_min_abs),   #73 quota min assoluta
                str(quota_min_rel),   #74 quota min relativa
                str(self.DATA_LIST[i].osservazioni),  # 75 osservazioni
                str(self.DATA_LIST[i].datazione), # 76 datazione
                str(self.DATA_LIST[i].flottazione),  # 77 flottazione
                str(self.DATA_LIST[i].setacciatura),  # 78 setacciatura
                str(self.DATA_LIST[i].affidabilita),  # 79 affidabilita
                str(self.DATA_LIST[i].direttore_us),  # 80 direttore us
                str(self.DATA_LIST[i].responsabile_us),  # 81 responsabile us
                str(self.DATA_LIST[i].cod_ente_schedatore),  # 82 cod ente schedatore
                str(self.DATA_LIST[i].data_rilevazione),  # 83 data rilevazione
                str(self.DATA_LIST[i].data_rielaborazione),  # 84 data rielaborazione
                str(lunghezza_usm), #85 lunghezza usm
                str(altezza_usm),  #86 altezza usm
                str(spessore_usm),  #87 spessore usm
                str(self.DATA_LIST[i].tecnica_muraria_usm),  # 88 tecnica muraria usm
                str(self.DATA_LIST[i].modulo_usm),  # 89 modulo usm
                str(self.DATA_LIST[i].campioni_malta_usm),  # 90 campioni malta usm
                str(self.DATA_LIST[i].campioni_mattone_usm),  # 91 campioni mattone usm
                str(self.DATA_LIST[i].campioni_pietra_usm),  # 92 campioni pietra usm
                str(self.DATA_LIST[i].provenienza_materiali_usm),  # 93 provenienza_materiali_usm
                str(self.DATA_LIST[i].criteri_distinzione_usm),  # 94 criteri distinzione usm
                str(self.DATA_LIST[i].uso_primario_usm),  #95 uso primario
                str(self.DATA_LIST[i].tipologia_opera),
                str(self.DATA_LIST[i].sezione_muraria),
                str(self.DATA_LIST[i].orientamento),
                str(self.DATA_LIST[i].materiali_lat),
                str(self.DATA_LIST[i].lavorazione_lat),
                str(self.DATA_LIST[i].consistenza_lat),
                str(self.DATA_LIST[i].forma_lat),
                str(self.DATA_LIST[i].colore_lat),
                str(self.DATA_LIST[i].impasto_lat),
                str(self.DATA_LIST[i].forma_p),
                str(self.DATA_LIST[i].colore_p),
                str(self.DATA_LIST[i].taglio_p),
                str(self.DATA_LIST[i].posa_opera_p),
                str(self.DATA_LIST[i].inerti_usm),
                str(self.DATA_LIST[i].tipo_legante_usm),
                str(self.DATA_LIST[i].rifinitura_usm),
                str(self.DATA_LIST[i].materiale_p),
                str(self.DATA_LIST[i].consistenza_p),
            ])
        return data_list

    def generate_list_periodizzazione_pdf(self):
        periodo = ""
        fase = ""
        cron_iniz = ""
        cron_fin = ""

        data_list = []
        for i in range(len(self.DATA_LIST)):

            if self.DATA_LIST[i].periodo == None:
                periodo = ""
            else:
                periodo = str(self.DATA_LIST[i].periodo)

            if self.DATA_LIST[i].fase == None:
                fase = ""
            else:
                fase = str(self.DATA_LIST[i].fase)

            if self.DATA_LIST[i].cron_iniziale == None:
                cron_iniz = ""
            else:
                cron_iniz = str(self.DATA_LIST[i].cron_iniziale)

            if self.DATA_LIST[i].cron_finale == None:
                cron_fin = ""
            else:
                cron_fin = str(self.DATA_LIST[i].cron_finale)

            data_list.append([
                str(self.DATA_LIST[i].sito.replace('_',' ')),  # 1 - Sito
                str(periodo),  # 2 - Area
                str(fase),  # 3 - US
                str(cron_iniz),  # 4 - definizione stratigrafica
                str(cron_fin),  # 5 - definizione intepretata
                str(self.DATA_LIST[i].datazione_estesa),  # 6 - descrizione
                str(self.DATA_LIST[i].descrizione)  # 7 - interpretazione
            ])
        return data_list

    def generate_list_struttura_pdf(self):
        data_list = []

        for i in range(len(self.DATA_LIST)):
            sito = str(self.DATA_LIST[i].sito.replace('_',' '))
            sigla_struttura = '{}{}'.format(
                str(self.DATA_LIST[i].sigla_struttura), str(self.DATA_LIST[i].numero_struttura))

            res_strutt = self.DB_MANAGER.query_bool(
                {"sito": "'" + str(sito) + "'", "struttura": "'" + str(sigla_struttura) + "'"}, "US")
            us_strutt_list = []
            if bool(res_strutt):
                for rs in res_strutt:
                    us_strutt_list.append([str(rs.sito), str(rs.area), str(rs.us)])

            quote_strutt = []
            if bool(us_strutt_list):
                for sing_us in us_strutt_list:
                    res_quote_strutt = self.DB_MANAGER.select_quote_from_db_sql(sing_us[0], sing_us[1], sing_us[2])
                    if bool(res_quote_strutt):
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

    def generate_list_reperti_pdf(self):
        data_list = []
        for i in range(len(self.DATA_LIST)):
            data_list.append([
                str(self.DATA_LIST[i].id_invmat),  # 1 - id_invmat
                str(self.DATA_LIST[i].sito.replace('_',' ')),  # 2 - sito
                int(self.DATA_LIST[i].numero_inventario),  # 3 - numero_inventario
                str(self.DATA_LIST[i].tipo_reperto),  # 4 - tipo_reperto
                str(self.DATA_LIST[i].criterio_schedatura),  # 5 - criterio_schedatura
                str(self.DATA_LIST[i].definizione),  # 6 - definizione
                str(self.DATA_LIST[i].descrizione),  # 7 - descrizione
                str(self.DATA_LIST[i].area),  # 8 - area
                str(self.DATA_LIST[i].us),  # 9 - us
                str(self.DATA_LIST[i].lavato),  # 10 - lavato
                str(self.DATA_LIST[i].nr_cassa),  # 11 - nr_cassa
                str(self.DATA_LIST[i].luogo_conservazione),  # 12 - luogo_conservazione
                str(self.DATA_LIST[i].stato_conservazione),  # 13 - stato_conservazione
                str(self.DATA_LIST[i].datazione_reperto),  # 14 - datazione_reperto
                str(self.DATA_LIST[i].elementi_reperto),  # 15 - elementi_reperto
                str(self.DATA_LIST[i].misurazioni),  # 16 - misurazioni
                str(self.DATA_LIST[i].rif_biblio),  # 17 - rif_biblio
                str(self.DATA_LIST[i].tecnologie),  # 18 - misurazioni
                str(self.DATA_LIST[i].tipo),  # 19 - tipo
                str(self.DATA_LIST[i].corpo_ceramico),  # 20 - corpo_ceramico
                str(self.DATA_LIST[i].rivestimento),  # 21 - rivestimento
                str(self.DATA_LIST[i].repertato),  # 22 - repertato
                str(self.DATA_LIST[i].diagnostico),
                str(self.DATA_LIST[i].n_reperto),
                str(self.DATA_LIST[i].tipo_contenitore)# 23 - diagnostico
            ])
        return data_list
    def generate_list_individui_pdf(self):
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


    def generate_list_tomba_pdf(self):
        data_list = []
        for i in range(len(self.DATA_LIST)):
            sito = str(self.DATA_LIST[i].sito.replace('_',' '))
            nr_individuo = str(self.DATA_LIST[i].nr_individuo)
            nr_individuo_find = str(self.DATA_LIST[i].nr_individuo)
            sigla_struttura = '{}{}{}'.format(str(self.DATA_LIST[i].sigla_struttura),'-', str(self.DATA_LIST[i].nr_struttura))

            res_ind = self.DB_MANAGER.query_bool({"sito": "'" + sito + "'"},
                                                 "SCHEDAIND")

            us_ind_list = []
            if bool(res_ind):
                for ri in res_ind:
                    us_ind_list.append([str(ri.sito), str(ri.area), str(ri.us)])
                us_ind_list.sort()

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

            res_strutt = self.DB_MANAGER.query_bool(
                {"sito": "'" + str(sito) + "'", "struttura": "'" + str(sigla_struttura) + "'"}, "US")
            
            us_strutt_list = []
            if bool(res_strutt):
                for rs in res_strutt:
                    us_strutt_list.append([str(rs.sito), str(rs.area), str(rs.us)])
                us_strutt_list.sort()

            quote_strutt = []
            if bool(us_strutt_list):
                for sing_us in us_strutt_list:
                    res_quote_strutt = self.DB_MANAGER.select_quote_from_db_sql(sing_us[0], sing_us[1], sing_us[2])
                    if bool(res_quote_strutt):
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
    def generate_list_campioni_pdf(self):
        data_list = []
        for i in range(len(self.DATA_LIST)):
            if str(self.DATA_LIST[i].nr_campione) == 'None':
                numero_campione = ''
            else:
                numero_campione = str(self.DATA_LIST[i].nr_campione)

            if str(self.DATA_LIST[i].us) == 'None':
                us = ''
            else:
                us = str(self.DATA_LIST[i].us)

            if str(self.DATA_LIST[i].numero_inventario_materiale) == 'None':
                numero_inventario_materiale = ''
            else:
                numero_inventario_materiale = str(self.DATA_LIST[i].numero_inventario_materiale)

            if str(self.DATA_LIST[i].nr_cassa) == 'None':
                nr_cassa = ''
            else:
                nr_cassa = str(self.DATA_LIST[i].nr_cassa)

            data_list.append([
                str(self.DATA_LIST[i].sito.replace('_',' ')),  # 1 - Sito
                str(numero_campione),  # 2 - Numero campione
                str(self.DATA_LIST[i].tipo_campione),  # 3 - Tipo campione
                str(self.DATA_LIST[i].descrizione),  # 4 - Descrizione
                str(self.DATA_LIST[i].area),  # 5 - Area
                str(us),  # 6 - us
                str(numero_inventario_materiale),  # 7 - numero inventario materiale
                str(self.DATA_LIST[i].luogo_conservazione),  # 8 - luogo_conservazione
                str(nr_cassa)  # 9 - nr cassa
            ])

        return data_list

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    ui = pyarchinit_pdf_export()
    ui.show()
    sys.exit(app.exec_())
