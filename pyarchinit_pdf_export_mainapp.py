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
from builtins import str
from builtins import range

from qgis.PyQt.QtWidgets import QDialog, QMessageBox
from qgis.PyQt.uic import loadUiType
from qgis.core import Qgis

import platform
import subprocess


from .modules.utility.pyarchinit_exp_USsheet_pdf import *

from .modules.db.pyarchinit_conn_strings import Connection
from .modules.db.pyarchinit_db_manager import Pyarchinit_db_management
from .modules.db.pyarchinit_utility import *
from .modules.utility.pyarchinit_exp_Findssheet_pdf import generate_reperti_pdf
from .modules.utility.pyarchinit_exp_Periodizzazionesheet_pdf import generate_Periodizzazione_pdf
from .modules.utility.pyarchinit_exp_Periodosheet_pdf import generate_US_pdf
from .modules.utility.pyarchinit_exp_Strutturasheet_pdf import generate_struttura_pdf
from .modules.utility.pyarchinit_exp_Tafonomiasheet_pdf import generate_tafonomia_pdf

MAIN_DIALOG_CLASS, _ = loadUiType(os.path.join(os.path.dirname(__file__), 'modules', 'gui', 'pyarchinit_pdf_exp_ui.ui'))


class pyarchinit_pdf_export(QDialog, MAIN_DIALOG_CLASS):
    UTILITY = Utility()
    OS_UTILITY = Pyarchinit_OS_Utility()
    DB_MANAGER = ""
    HOME = ""
    DATA_LIST = []

    ##	if os.name == 'posix':
    ##		HOME = os.environ['HOME']
    ##	elif os.name == 'nt':
    ##		HOME = os.environ['HOMEPATH']
    ##
    ##	PARAMS_DICT={'SERVER':'',
    ##				'HOST': '',
    ##				'DATABASE':'',
    ##				'PASSWORD':'',
    ##				'PORT':'',
    ##				'USER':'',
    ##				'THUMB_PATH':''}

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
        QMessageBox.warning(self, "Alert",
                            "Sistema sperimentale. Esporta le schede PDF in /vostro_utente/pyarchinit_DB_folder. Sostituisce i documenti gia' presenti. Se volete conservarli fatene una copia o rinominateli.",
                            QMessageBox.Ok)

        conn = Connection()
        conn_str = conn.conn_str()
        try:
            self.DB_MANAGER = Pyarchinit_db_management(conn_str)
            self.DB_MANAGER.connection()
        except Exception as e:
            e = str(e)
            if e.find("no such table"):
                QMessageBox.warning(self, "Alert",
                                    "La connessione e' fallita <br><br> %s. E' NECESSARIO RIAVVIARE QGIS" % (str(e)),
                                    QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "Alert",
                                    "Attenzione rilevato bug! Segnalarlo allo sviluppatore<br> Errore: <br>" + str(e),
                                    QMessageBox.Ok)

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
        if os.name == 'posix':
            self.HOME = os.environ['HOME']
        elif os.name == 'nt':
            self.HOME = os.environ['HOMEPATH']

    def on_pushButton_open_dir_pressed(self):
        path = ('%s%s%s') % (self.HOME, os.sep, "pyarchinit_PDF_folder")

        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

    def messageOnSuccess(self, printed):
        if printed:
            self.iface.messageBar().pushMessage("Esportazione avvenuta con successo", Qgis.Success)
        else:
            self.iface.messageBar().pushMessage("Non ci sono dati da esportare", Qgis.Info)

    def on_pushButton_exp_pdf_pressed(self):
        sito = str(self.comboBox_sito.currentText())
        printed = False
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
                    QMessageBox.warning(self, "Alert", "Attenzione non vi sono schede da stampare", QMessageBox.Ok)
                else:
                    US_pdf_sheet = generate_US_pdf()
                    data_list = self.generate_list_US_pdf()
                    US_pdf_sheet.build_US_sheets(data_list)  # export sheet
                    US_pdf_sheet.build_index_US(data_list, data_list[0][0])  # export list

            if self.DATA_LIST:
                printed = True
                self.DATA_LIST = []

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
                Periodizzazione_pdf_sheet.build_Periodizzazione_sheets(data_list)  # deve essere aggiunto il file per generare i pdf
                Periodizzazione_pdf_sheet.build_index_Periodizzazione(data_list, data_list[0][0])  # deve essere aggiunto il file per generare i pdf

            if self.DATA_LIST:
                printed = True
                self.DATA_LIST = []

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
                Struttura_pdf_sheet.build_Struttura_sheets(
                    data_list)  # deve essere aggiunto il file per generare i pdf
                Struttura_pdf_sheet.build_index_Struttura(data_list, data_list[0][0])

            if self.DATA_LIST:
                printed = True
                self.DATA_LIST = []

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
                Finds_pdf_sheet.build_Finds_sheets(data_list)
                Finds_pdf_sheet.build_index_Finds(data_list, data_list[0][0])

            if self.DATA_LIST:
                printed = True
                self.DATA_LIST = []

        if self.checkBox_tafonomia.isChecked():
            tafonomia_res = self.db_search_DB('TAFONOMIA', 'sito', sito)

            if bool(tafonomia_res):
                id_list = []
                for i in range(len(tafonomia_res)):
                    id_list.append(tafonomia_res[i].id_tafonomia)

                temp_data_list = self.DB_MANAGER.query_sort(id_list, ['nr_scheda_taf'], 'asc', 'TAFONOMIA',
                                                            'id_tafonomia')

                for i in temp_data_list:
                    self.DATA_LIST.append(i)

                Tafonomia_pdf_sheet = generate_tafonomia_pdf()
                data_list = self.generate_list_tafonomia_pdf()
                Tafonomia_pdf_sheet.build_Tafonomia_sheets(data_list)
                Tafonomia_pdf_sheet.build_index_Tafonomia(data_list, data_list[0][0])

            if self.DATA_LIST:
                printed = True
                self.DATA_LIST = []

        ##		if self.checkBox_individui.isChecked() == True:
        ##			individui_res = self.db_search_DB('SCHEDAIND','sito', sito)
        ##
        ##			if bool(individui_res) == True:
        ##				id_list = []
        ##				for i in range(len(individui_res)):
        ##					id_list.append(individui_res[i].id_scheda_ind)
        ##
        ##				temp_data_list = self.DB_MANAGER.query_sort(id_list, ['nr_individuo'], 'asc', 'SCHEDAIND', 'id_scheda_ind')
        ##
        ##				for i in temp_data_list:
        ##					self.DATA_LIST.append(i)
        ##
        ##				Individui_pdf_sheet = generate_pdf()
        ##				data_list = self.generate_list_individui_pdf()
        ##				Individui_pdf_sheet.build_Individui_sheets(self.DATA_LIST)
        ##				Individui_pdf_sheet.build_index_individui(self.DATA_LIST, self.DATA_LIST[0][0])
        ##
        ##			self.DATA_LIST = []
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
        for i in range(len(self.DATA_LIST)):
            # assegnazione valori di quota mn e max
            sito = str(self.DATA_LIST[i].sito)
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
                quota_min = "Non inserita su GIS"
                quota_max = "Non inserita su GIS"

                # assegnazione numero di pianta
            resus = self.DB_MANAGER.select_us_from_db_sql(sito, area, us, "2")
            elenco_record = []
            for us in resus:
                elenco_record.append(us)

            if bool(elenco_record):
                sing_rec = elenco_record[0]
                elenco_piante = sing_rec[7]
                if elenco_piante != None:
                    piante = elenco_piante
                else:
                    piante = "US disegnata su base GIS"
            else:
                piante = "US disegnata su base GIS"

            # d_str = str(self.DATA_LIST[i].d_stratigrafica)
            # QMessageBox.warning(self, "Alert", str(self.DATA_LIST[i]), QMessageBox.Ok)
            # sito = str(self.DATA_LIST[i].sito)

            data_list.append([
                str(self.DATA_LIST[i].sito),  # 1 - Sito
                str(self.DATA_LIST[i].area),  # 2 - Area
                int(self.DATA_LIST[i].us),  # 3 - US
                str(self.DATA_LIST[i].d_stratigrafica),  # 4 - definizione stratigrafica
                str(self.DATA_LIST[i].d_interpretativa),  # 5 - definizione intepretata
                str(self.DATA_LIST[i].descrizione),  # 6 - descrizione
                str(self.DATA_LIST[i].interpretazione),  # 7 - interpretazione
                str(self.DATA_LIST[i].periodo_iniziale),  # 8 - periodo iniziale
                str(self.DATA_LIST[i].fase_iniziale),  # 9 - fase iniziale
                str(self.DATA_LIST[i].periodo_finale),  # 10 - periodo finale iniziale
                str(self.DATA_LIST[i].fase_finale),  # 11 - fase finale
                str(self.DATA_LIST[i].scavato),  # 12 - scavato
                str(self.DATA_LIST[i].attivita),  # 13 - attivita
                str(self.DATA_LIST[i].anno_scavo),  # 14 - anno scavo
                str(self.DATA_LIST[i].metodo_di_scavo),  # 15 - metodo
                str(self.DATA_LIST[i].inclusi),  # 16 - inclusi
                str(self.DATA_LIST[i].campioni),  # 17 - campioni
                str(self.DATA_LIST[i].rapporti),  # 18 - rapporti
                str(self.DATA_LIST[i].data_schedatura),  # 19 - data schedatura
                str(self.DATA_LIST[i].schedatore),  # 20 - schedatore
                str(self.DATA_LIST[i].formazione),  # 21 - formazione
                str(self.DATA_LIST[i].stato_di_conservazione),  # 22 - conservazione
                str(self.DATA_LIST[i].colore),  # 23 - colore
                str(self.DATA_LIST[i].consistenza),  # 24 - consistenza
                str(self.DATA_LIST[i].struttura),  # 25 - struttura
                str(quota_min),  # 26 - quota_min
                str(quota_max),  # 27 - quota_max
                str(piante),  # 28 - piante
                str(self.DATA_LIST[i].documentazione)  # 29 - documentazione
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
                str(self.DATA_LIST[i].sito),  # 1 - Sito
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
            sito = str(self.DATA_LIST[i].sito)
            sigla_struttura = ('%s%s') % (
            str(self.DATA_LIST[i].sigla_struttura), str(self.DATA_LIST[i].numero_struttura))

            res_strutt = self.DB_MANAGER.query_bool(
                {"sito": "'" + str(sito) + "'", "struttura": "'" + str(sigla_struttura) + "'"}, "US")
            us_strutt_list = []
            if bool(res_strutt):
                for rs in res_strutt:
                    us_strutt_list.append([str(rs.sito), str(rs.area), str(rs.area)])

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
                quota_min_strutt = "Non inserita su GIS"
                quota_max_strutt = "Non inserita su GIS"

            data_list.append([
                str(self.DATA_LIST[i].sito),  # 1 - Sito
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
                str(self.DATA_LIST[i].sito),  # 2 - sito
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
                str(self.DATA_LIST[i].rivestimento)  # 21- rivestimento
            ])
        return data_list

    def generate_list_individui_pdf(self):
        data_list = []
        for i in range(len(self.DATA_LIST)):
            data_list.append([
                str(self.DATA_LIST[i].sito),  # 1 - Sito
                int(self.DATA_LIST[i].area),  # 2 - Area
                int(self.DATA_LIST[i].us),  # 3 - us
                int(self.DATA_LIST[i].nr_individuo),  # 4 -  nr individuo
                str(self.DATA_LIST[i].data_schedatura),  # 5 - data schedatura
                str(self.DATA_LIST[i].schedatore),  # 6 - schedatore
                str(self.DATA_LIST[i].sesso),  # 7 - sesso
                str(self.DATA_LIST[i].eta_min),  # 8 - eta' minima
                str(self.DATA_LIST[i].eta_max),  # 9- eta massima
                str(self.DATA_LIST[i].classi_eta),  # 10 - classi di eta'
                str(self.DATA_LIST[i].osservazioni)  # 11 - osservazioni
            ])
        return data_list

    def generate_list_tafonomia_pdf(self):
        data_list = []
        for i in range(len(self.DATA_LIST)):
            sito = str(self.DATA_LIST[i].sito)
            nr_individuo = str(self.DATA_LIST[i].nr_individuo)
            sigla_struttura = ('%s%s') % (str(self.DATA_LIST[i].sigla_struttura), str(self.DATA_LIST[i].nr_struttura))

            res_ind = self.DB_MANAGER.query_bool(
                {"sito": "'" + str(sito) + "'", "nr_individuo": "'" + str(nr_individuo) + "'"}, "SCHEDAIND")
            # res = db.query_distinct('INVENTARIO_MATERIALI',[['sito','"Sito archeologico"']], ['area', 'us'])
            us_ind_list = []
            if bool(res_ind):
                for ri in res_ind:
                    us_ind_list.append([str(ri.sito), str(ri.area), str(ri.us)])

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
                quota_min_ind = "Non inserita su GIS"
                quota_max_ind = "Non inserita su GIS"

            ##########################################################################

            res_strutt = self.DB_MANAGER.query_bool(
                {"sito": "'" + str(sito) + "'", "struttura": "'" + str(sigla_struttura) + "'"}, "US")
            # res = db.query_distinct('INVENTARIO_MATERIALI',[['sito','"Sito archeologico"']], ['area', 'us'])
            us_strutt_list = []
            if bool(res_strutt):
                for rs in res_strutt:
                    us_strutt_list.append([str(rs.sito), str(rs.area), str(rs.area)])

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
                quota_min_strutt = "Non inserita su GIS"
                quota_max_strutt = "Non inserita su GIS"

            data_list.append([
                str(self.DATA_LIST[i].sito),  # 0 - Sito
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
                str(self.DATA_LIST[i].orientamento_asse),  # 14 - orientamento asse
                self.DATA_LIST[i].orientamento_azimut,  # 15 orientamento azimut
                str(self.DATA_LIST[i].corredo_presenza),  # 16-  corredo presenza
                str(self.DATA_LIST[i].corredo_tipo),  # 17 - corredo tipo
                str(self.DATA_LIST[i].corredo_descrizione),  # 18 - corredo descrizione
                self.DATA_LIST[i].lunghezza_scheletro,  # 19 - lunghezza scheletro
                str(self.DATA_LIST[i].posizione_cranio),  # 20 - posizione cranio
                str(self.DATA_LIST[i].posizione_scheletro),  # 21 - posizione cranio
                str(self.DATA_LIST[i].posizione_arti_superiori),  # 22 - posizione arti superiori
                str(self.DATA_LIST[i].posizione_arti_inferiori),  # 23 - posizione arti inferiori
                str(self.DATA_LIST[i].completo_si_no),  # 24 - completo
                str(self.DATA_LIST[i].disturbato_si_no),  # 25- disturbato
                str(self.DATA_LIST[i].in_connessione_si_no),  # 26 - in connessione
                str(self.DATA_LIST[i].caratteristiche),  # 27 - caratteristiche
                str(self.DATA_LIST[i].periodo_iniziale),  # 28 - periodo iniziale
                str(self.DATA_LIST[i].fase_iniziale),  # 29 - fase iniziale
                str(self.DATA_LIST[i].periodo_finale),  # 30 - periodo finale
                str(self.DATA_LIST[i].fase_finale),  # 31 - fase finale
                str(self.DATA_LIST[i].datazione_estesa),  # 32 - datazione estesa
                str(self.DATA_LIST[i].misure_tafonomia),  # 33 - misure tafonomia
                quota_min_ind,  # 34 - quota min individuo
                quota_max_ind,  # 35 - quota max individuo
                quota_min_strutt,  # 36 - quota min struttura
                quota_max_strutt  # 37 - quota max struttura
            ])

        return data_list


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    ui = pyarchinit_pdf_export()
    ui.show()
    sys.exit(app.exec_())
