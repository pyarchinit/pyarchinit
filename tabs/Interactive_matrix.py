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
import random
#import networkx as nx
import graphviz
# import pygraphviz as pgv
from graphviz import Digraph, Source
#from networkx.drawing.nx_pydot import graphviz_layout

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
#from networkx.drawing.nx_agraph import *
from qgis.PyQt.QtWidgets import QDialog, QMessageBox
from qgis.PyQt.uic import loadUiType
from qgis.core import QgsSettings
from ..modules.db.pyarchinit_conn_strings import Connection
from ..modules.db.pyarchinit_db_manager import get_db_manager
from ..modules.gis.pyarchinit_pyqgis import Pyarchinit_pyqgis
from ..modules.utility.pyarchinit_matrix_exp import *
import re
MAIN_DIALOG_CLASS, _ = loadUiType(
    os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'Interactive_matrix.ui'))


class pyarchinit_Interactive_Matrix(QDialog, MAIN_DIALOG_CLASS):
    L=QgsSettings().value("locale/userLocale", "it", type=str)[:2]
    MSG_BOX_TITLE = "PyArchInit - Harrys Matrix"
    DB_MANAGER = ""
    DATA_LIST = ""
    ID_US_DICT = {}

    HOME = os.environ['PYARCHINIT_HOME']

    QUANT_PATH = '{}{}{}'.format(HOME, os.sep, "pyarchinit_Quantificazioni_folder")

    def __init__(self, iface, data_list, id_us_dict):
        super().__init__()
        self.iface = iface
        self.pyQGIS = Pyarchinit_pyqgis(iface)
        self.DATA_LIST = data_list
        self.ID_US_DICT = id_us_dict
        self.setupUi(self)

        ##      self.textbox.setText('1 2 3 4')
        # self.on_draw()
        try:
            self.DB_connect()
        except:
            pass

    def DB_connect(self):
        conn = Connection()
        conn_str = conn.conn_str()
        try:
            self.DB_MANAGER = get_db_manager(conn_str, use_singleton=True)
        except Exception as e:
            e = str(e)
            
            if self.L=='it':
                QMessageBox.warning(self, "Attenzione",
                                "bug! Scrivere allo sviluppatore <br> Error: <br>" + str(e),
                                QMessageBox.StandardButton.Ok)
            if self.L=='it':
                QMessageBox.warning(self, "Warnung",
                                "bug! Schreiben Sie an den Entwickler <br> Error: <br>" + str(e),
                                QMessageBox.StandardButton.Ok)
                                
            else:
                QMessageBox.warning(self, "Alert",
                                "bug! write to the developer <br> Error: <br>" + str(e),
                                QMessageBox.StandardButton.Ok)                    
    def urlify(self,s):

        # Rimuove tutti i caratteri che non sono parole (tutto tranne i numeri e le lettere)
        s = re.sub(r"[^\w\s]", ' ', s)

        # Sostituire tutti gli spazi bianchi con un underscore
        s = re.sub(r"\s+", '_', s)

        return s
    def generate_matrix_2(self):
        data = []
        negative =[]
        conteporane=[]
        connection=[]
        connection_to=[]

        for sing_rec in self.DATA_LIST:
            try:
                us = str(sing_rec.us)
                un_t = str(sing_rec.unita_tipo)##per inserire il termine US o USM
                datazione = str(sing_rec.periodo_iniziale)+'-'+str(sing_rec.fase_iniziale)##per inserire la datazione estesa
                defin = str(sing_rec.d_interpretativa.replace(' ','_'))##per inserire la definizione startigrafica
                doc = str(sing_rec.doc_usv.replace(' ','_'))##per inserire la definizione startigrafica
            
                rapporti_stratigrafici = eval(sing_rec.rapporti2)
            except (NameError, SyntaxError) as e: 
                if self.L=='it':
                    QMessageBox.warning(self, 'ATTENZIONE','Mancano i valori unita tipo e interpretazione startigrafica nella tablewidget dei rapporti startigrafici. affinchè il matrix sia esportato correttamente devi inserirli',
                            QMessageBox.StandardButton.Ok)
                    break        
                elif self.L=='de':
                    QMessageBox.warning(self, "Warnung", "Sie müssen den Einheitentyp und die startigraphische Interpretation im Tabellenwidget startigraphic reports eingeben",
                                    QMessageBox.StandardButton.Ok)
                    break                
                else:
                    QMessageBox.warning(self, "Warning", "You have to enter the unit type and startigraphic interpretation in the startigraphic reports tablewidget",
                                    QMessageBox.StandardButton.Ok)           
                    break
            try:
                
                    
                for  sing_rapp in rapporti_stratigrafici:
                
                    if   sing_rapp[0] == 'Covers' or  sing_rapp[0] == 'Abuts' or  sing_rapp[0] == 'Fills' or  sing_rapp[0] == 'Copre' or  sing_rapp[0] == 'Si appoggia a' or  sing_rapp[0] == 'Riempie'   or  sing_rapp[0] == 'Verfüllt' or sing_rapp[0] == 'Bindet an' or  sing_rapp[0] == 'Entspricht' :
                        if sing_rapp[1] != '':
                            harris_rapp = (un_t+us+'_'+defin+'_'+datazione,str(sing_rapp[2])+str(sing_rapp[1])+'_'+str(sing_rapp[3].replace(' ','_')+'_'+str(sing_rapp[4])))
                            data.append(harris_rapp)
                        
                        
                    
                    if sing_rapp[0] == 'Taglia' or sing_rapp[0] == 'Cuts' or sing_rapp[0] == 'Schneidet':
                        if sing_rapp[1] != '':
                            harris_rapp1 = (un_t+us+'_'+defin+'_'+datazione,str(sing_rapp[2])+str(sing_rapp[1])+'_'+str(sing_rapp[3].replace(' ','_')+'_'+str(sing_rapp[4])))
                            negative.append(harris_rapp1)
                            
                    
                    if sing_rapp[0] == 'Si lega a' or  sing_rapp[0] == 'Uguale a' or sing_rapp[0] == 'Connected to' or  sing_rapp[0] == 'Same as'or sing_rapp[0] == 'Liegt über' or  sing_rapp[0] == 'Stützt sich auf':
                        if sing_rapp[1] != '':
                            harris_rapp2 = (un_t+us+'_'+defin+'_'+datazione,str(sing_rapp[2])+str(sing_rapp[1])+'_'+str(sing_rapp[3].replace(' ','_')+'_'+str(sing_rapp[4])))
                            conteporane.append(harris_rapp2)
                    
                    if sing_rapp[0] == '>' :
                        if sing_rapp[1] != '':
                            harris_rapp3 = (un_t+us+'_'+defin+'_'+datazione,str(sing_rapp[2])+str(sing_rapp[1])+'_'+str(sing_rapp[3].replace(' ','_')+'_'+str(sing_rapp[4])))
                            connection.append(harris_rapp3)
                    
                    
                    if sing_rapp[0] == '>>' :
                        if sing_rapp[1] != '':
                            harris_rapp4 = (un_t+us+'_'+defin+'_'+datazione,str(sing_rapp[2])+str(sing_rapp[1])+'_'+str(sing_rapp[3].replace(' ','_')+'_'+str(sing_rapp[4])))
                            connection_to.append(harris_rapp4)        
            
                    # if sing_rapp[0] == '<->' :
                        # if sing_rapp[1] != '':
                            # harris_rapp4 = (un_t+us+'_'+doc+'_'+datazione,str(sing_rapp[2])+str(sing_rapp[1])+'_'+str(sing_rapp[3].replace(' ','_')+'_'+str(sing_rapp[4])))
                            # connection_to.append(harris_rapp4)      
            except Exception as e:
                    
                    if self.L=='it':
                        QMessageBox.warning(self, 'ATTENZIONE','Mancano i valori unita tipo e interpretazione startigrafica nella tablewidget dei rapporti startigrafici. affinchè il matrix sia esportato correttamente devi inserirli',
                                QMessageBox.StandardButton.Ok)
                    elif self.L=='de':
                        QMessageBox.warning(self, "Warnung", "Sie müssen den Einheitentyp und die startigraphische Interpretation im Tabellenwidget startigraphic reports eingeben",
                                        QMessageBox.StandardButton.Ok)
                                        
                    else:
                        QMessageBox.warning(self, "Warning", "You have to enter the unit type and startigraphic interpretation in the startigraphic reports tablewidget",
                                        QMessageBox.StandardButton.Ok)                    
        sito = self.DATA_LIST[0].sito
        #area = self.DATA_LIST[1].area
        search_dict = {
            'sito': "'" + str(sito) + "'",
            #'area': "'" + str(area) + "'"
        }

        periodizz_data_list = self.DB_MANAGER.query_bool(search_dict, 'PERIODIZZAZIONE')

        periodi_data_values = []
        for a in periodizz_data_list:
            periodi_data_values.append([a.periodo, a.fase,a.datazione_estesa])

        periodi_us_list = []

        clust_number = 0
        for i in periodi_data_values:
            search_dict = {
                'sito': "'" + str(sito) + "'",
                'periodo_iniziale': "'" + str(i[0]) + "'",
                'fase_iniziale': "'" + str(i[1]) + "'",
                'datazione':"'" + str(i[2]) + "'"
            }
            search_dict2 = {
                'sito': "'" + str(sito) + "'",
                'periodo_iniziale': "'" + str(i[0]) + "'",
                'fase_iniziale': "'" + str(i[1]) + "'"
            }
            us_group = self.DB_MANAGER.query_bool(search_dict2, 'US')

            cluster_label = "cluster%s" % (clust_number)

            if self.L=='it':
                periodo_label = "Periodo %s : Fase %s : %s" % (str(i[0]), str(i[1]),str(i[2]))
                
                sing_per = [cluster_label, periodo_label]
                
                sing_us = []

            elif self.L=='de':
                periodo_label = "Period %s : Phase %s : %s" % (str(i[0]), str(i[1]),str(i[2]))

                sing_per = [cluster_label, periodo_label]
                
                sing_us = []

            else:
                periodo_label = "Period %s : Phase %s : %s" % (str(i[0]), str(i[1]), str(i[2]))

                sing_per = [cluster_label, periodo_label]

                sing_us = []  

            for rec in us_group:

                sing_us.append(rec.unita_tipo+str(rec.us)+'_'+rec.d_interpretativa.replace(' ','_')+'_'+rec.periodo_iniziale+'-'+rec.fase_iniziale)

            sing_per.insert(0, sing_us )
            #sing_per.insert(0, sing_ut )
            periodi_us_list.append(sing_per)

            clust_number += 1
        
        matrix_exp = HarrisMatrix(data,negative,conteporane,connection,connection_to, periodi_us_list)
        try: 
            data_plotting_2 = matrix_exp.export_matrix_2
        except Exception as e :
            QMessageBox.information(self, "Info", str(e), QMessageBox.StandardButton.Ok)
        finally:
            data_plotting_2 = matrix_exp.export_matrix_2
        if self.L=='it':
            QMessageBox.information(self, "Info", "Esportazione completata", QMessageBox.StandardButton.Ok)
        elif self.L=='de':
            QMessageBox.information(self, "Info", "Exportieren kompliziert", QMessageBox.StandardButton.Ok)
        else:
            QMessageBox.information(self, "Info", "Exportation complited", QMessageBox.StandardButton.Ok)    
             
        return data_plotting_2

    def generate_matrix(self):
        data = []
        negative = []
        conteporane = []
        # QMessageBox.information(None, "Info", str(self.DATA_LIST[0].us), QMessageBox.Ok)
        for sing_rec in self.DATA_LIST:
            us = str(sing_rec.us)
            un_t = str(sing_rec.unita_tipo)
            sito = str(sing_rec.sito)
            area = str(sing_rec.area)

            rapporti_stratigrafici = eval(sing_rec.rapporti)

            try:
                for sing_rapp in rapporti_stratigrafici:
                    if sing_rapp[0] in ['Covers', 'Abuts', 'Fills', 'Copre', 'Si appoggia a', 'Riempie', 'Verfüllt',
                                        'Bindet an', 'Entspricht']:
                        if sing_rapp[1] != '':
                            harris_rapp = (area + '_' + 'US' + us, str(sing_rapp[2]) + '_' + 'US' + str(sing_rapp[1]))
                            data.append(harris_rapp)

                    if sing_rapp[0] in ['Taglia', 'Cuts', 'Schneidet']:
                        if sing_rapp[1] != '':
                            harris_rapp1 = (area + '_' + 'US' + us, str(sing_rapp[2]) + '_' + 'US' + str(sing_rapp[1]))
                            negative.append(harris_rapp1)

                    if sing_rapp[0] in ['Si lega a', 'Uguale a', 'Connected to', 'Same as', 'Liegt über',
                                        'Stützt sich auf']:
                        if sing_rapp[1] != '':
                            harris_rapp2 = (area + '_' + 'US' + us, str(sing_rapp[2]) + '_' + 'US' + str(sing_rapp[1]))
                            conteporane.append(harris_rapp2)
            except Exception as e:
                print(f"Errore durante la generazione della matrice: {e}")

                if self.L == 'it':
                    QMessageBox.warning(self, "Warning", "Problema nel sistema di esportazione del Matrix:" + str(e),
                                        QMessageBox.StandardButton.Ok)
                elif self.L == 'de':
                    QMessageBox.warning(self, "Warnung", "Problem im Matrix-Exportsystem:" + str(e),
                                        QMessageBox.StandardButton.Ok)
                else:
                    QMessageBox.warning(self, "Warning", "Problem in the Matrix export system:" + str(e),
                                        QMessageBox.StandardButton.Ok)

        sito = self.DATA_LIST[0].sito
        # area = self.DATA_LIST[0].area

        search_dict = {
            'sito': "'" + str(sito) + "'",
        }

        periodizz_data_list = self.DB_MANAGER.query_bool(search_dict, 'PERIODIZZAZIONE')

        periodi_data_values = []

        for a in periodizz_data_list:
            periodi_data_values.append([a.cont_per, a.datazione_estesa, a.periodo, a.fase, a.descrizione])

        # Clear the previous contents of the list
        periodi_us_list = []

        clust_number = 0

        # Get all the areas
        areas = set([rec.area for rec in self.DATA_LIST if rec.sito == sito])
        cluster_label = "cluster%s" % clust_number

        # Iterate over the unique areas
        for area in areas:
            for i in periodi_data_values:
                search_dict2 = {
                    'sito': "'" + str(sito) + "'",
                    #'area': "'" + str(area) + "'",
                    'periodo_iniziale': "'" + str(i[2]) + "'",
                    'fase_iniziale': "'" + str(i[3]) + "'"
                }
                us_group = self.DB_MANAGER.query_bool(search_dict2, 'US')

                periodo_label = "%s" % (str(i[1]))

                sing_us = [rec.area + '_' + 'US' + str(rec.us) for rec in us_group]

                # Modifica: Usiamo le cronologie iniziali e finali
                fase_id = i[3]  # Il numero/id della fase
                periodo_id = i[2]  # Il numero/id del periodo

                # Cerchiamo le cronologie dalla tabella PERIODIZZAZIONE
                try:
                    # Query per trovare le date di inizio e fine
                    search_dates = {
                        'sito': "'" + str(sito) + "'",
                        #'area': "'" + str(area) + "'",
                        'periodo': "'" + str(periodo_id) + "'",
                        'fase': "'" + str(fase_id) + "'"
                    }

                    # Query per ottenere i campi cron_iniziale e cron_finale
                    date_records = self.DB_MANAGER.query_bool(search_dates, 'PERIODIZZAZIONE')

                    if date_records and len(date_records) > 0:
                        if hasattr(date_records[0], 'cron_iniziale') and hasattr(date_records[0], 'cron_finale'):
                            # Gestione dei valori negativi (per date a.C.)
                            cron_iniziale = date_records[0].cron_iniziale
                            cron_finale = date_records[0].cron_finale

                            # Formattazione con gestione di valori negativi (a.C.)
                            iniziale_str = str(abs(cron_iniziale)) + " a.C." if cron_iniziale < 0 else str(
                                cron_iniziale) + " d.C."
                            finale_str = str(abs(cron_finale)) + " a.C." if cron_finale < 0 else str(
                                cron_finale) + " d.C."

                            fase = "Fase%s: da %s a %s" % (str(fase_id), iniziale_str, finale_str)
                        else:
                            # Fallback al datazione_estesa se i campi non sono disponibili
                            fase = "Fase%s: %s" % (str(fase_id), str(i[1]))
                    else:
                        # Se non troviamo i dati specifici, usiamo solo il numero della fase
                        fase = "Fase%s" % str(fase_id)
                except Exception as e:
                    # Messaggio dettagliato con informazioni sulla US incriminata
                    us_info = f"Sito: {sito}, Area: {area}, Periodo: {periodo_id}, Fase: {fase_id}"
                    affected_us = ", ".join([str(rec.us) for rec in us_group[:10]]) + (
                        "..." if len(us_group) > 10 else "")
                    error_message = (f"Errore nel recupero delle cronologie per:\n{us_info}\n Non hai inserito nella "
                                     f"scheda periodizzazione la datazione estesa per questa US.\n\nUS interessate: "
                                     f"{affected_us}\n\nErrore: {e}\n Verrà usato il numero della fase come nome della fase."
                                     f"Per favore, inserisci la datazione estesa per questa US nella scheda periodizzazione." )

                    QMessageBox.warning(self, "Errore", error_message, QMessageBox.StandardButton.Ok)

                    # Fallback in caso di errore
                    fase = "Fase%s" % str(fase_id)

                sing_fase = [fase, sing_us]

                periodo = "%s" % (str(i[2]))
                sing_per = [periodo, sing_fase]

                sing_per = [periodo_label, sing_per]

                area_label = "%s" % str(area)
                sing_area = [cluster_label, area_label, sing_per]

                sito_label = "%s" % str(sito)
                sing_sito = [cluster_label, sito_label, sing_area]

                periodi_us_list.append(sing_sito)

                clust_number += 1

        matrix_exp = HarrisMatrix(data, negative, conteporane, '', '', periodi_us_list)

        data_plotting = matrix_exp.export_matrix

        if self.L == 'it':
            QMessageBox.information(self, "Info", "Esportazione completata", QMessageBox.StandardButton.Ok)
        elif self.L == 'de':
            QMessageBox.information(self, "Info", "Exportieren kompliziert", QMessageBox.StandardButton.Ok)
        else:
            QMessageBox.information(self, "Info", "Exportation complited", QMessageBox.StandardButton.Ok)

        return data_plotting


class pyarchinit_view_Matrix(QDialog, MAIN_DIALOG_CLASS):
    L = QgsSettings().value("locale/userLocale", "it", type=str)[:2]
    MSG_BOX_TITLE = "PyArchInit - Harrys Matrix"
    DB_MANAGER = ""
    DATA_LIST = ""
    ID_US_DICT = {}

    HOME = os.environ['PYARCHINIT_HOME']

    def __init__(self, iface, data_list, id_us_dict):
        super().__init__()
        self.iface = iface
        self.pyQGIS = Pyarchinit_pyqgis(iface)
        self.DATA_LIST = data_list
        self.ID_US_DICT = id_us_dict
        self.setupUi(self)

        ##      self.textbox.setText('1 2 3 4')
        # self.on_draw()
        try:
            self.DB_connect()
        except:
            pass

    def DB_connect(self):
        conn = Connection()
        conn_str = conn.conn_str()
        try:
            self.DB_MANAGER = get_db_manager(conn_str, use_singleton=True)
        except Exception as e:
            e = str(e)

            if self.L == 'it':
                QMessageBox.warning(self, "Attenzione",
                                    "bug! Scrivere allo sviluppatore <br> Error: <br>" + str(e),
                                    QMessageBox.StandardButton.Ok)
            if self.L == 'it':
                QMessageBox.warning(self, "Warnung",
                                    "bug! Schreiben Sie an den Entwickler <br> Error: <br>" + str(e),
                                    QMessageBox.StandardButton.Ok)

            else:
                QMessageBox.warning(self, "Alert",
                                    "bug! write to the developer <br> Error: <br>" + str(e),
                                    QMessageBox.StandardButton.Ok)

    def urlify(self, s):

        # Rimuove tutti i caratteri che non sono parole (tutto tranne i numeri e le lettere)
        s = re.sub(r"[^\w\s]", ' ', s)

        # Sostituire tutti gli spazi bianchi con un underscore
        s = re.sub(r"\s+", '_', s)

        return s



    def generate_matrix(self):
        data = []
        negative = []
        conteporane = []

        for sing_rec in self.DATA_LIST:
            us = str(sing_rec.us)
            un_t = str(sing_rec.unita_tipo)  ##per inserire il termine US o USM
            # datazione = str(sing_rec.datazione)##per inserire la datazione estesa
            # defin = str(sing_rec.d_stratigrafica.replace(' ','_'))##per inserire la definizione startigrafica
            sito = str(sing_rec.sito)
            area = str(sing_rec.area)
            rapporti_stratigrafici = eval(sing_rec.rapporti)

            try:
                for sing_rapp in rapporti_stratigrafici:

                    if sing_rapp[0] == 'Covers' or sing_rapp[0] == 'Abuts' or sing_rapp[0] == 'Fills' or sing_rapp[
                        0] == 'Copre' or sing_rapp[0] == 'Si appoggia a' or sing_rapp[0] == 'Riempie' or sing_rapp[
                        0] == 'Verfüllt' or sing_rapp[0] == 'Bindet an' or sing_rapp[0] == 'Entspricht':
                        if sing_rapp[1] != '':
                            harris_rapp = (us, str(sing_rapp[1]))
                            data.append(harris_rapp)

                    if sing_rapp[0] == 'Taglia' or sing_rapp[0] == 'Cuts' or sing_rapp[0] == 'Schneidet':
                        if sing_rapp[1] != '':
                            harris_rapp1 = (us, str(sing_rapp[1]))
                            negative.append(harris_rapp1)

                    if sing_rapp[0] == 'Si lega a' or sing_rapp[0] == 'Uguale a' or sing_rapp[
                        0] == 'Connected to' or sing_rapp[0] == 'Same as' or sing_rapp[0] == 'Liegt über' or \
                            sing_rapp[0] == 'Stützt sich auf':
                        if sing_rapp[1] != '':
                            harris_rapp2 = (us, str(sing_rapp[1]))
                            conteporane.append(harris_rapp2)


            except Exception as e:

                if self.L == 'it':
                    QMessageBox.warning(self, "Warning",
                                        "Problema nel sistema di esportazione del Matrix:" + str(e),
                                        QMessageBox.StandardButton.Ok)
                elif self.L == 'de':
                    QMessageBox.warning(self, "Warnung", "Problem im Matrix-Exportsystem:" + str(e),
                                        QMessageBox.StandardButton.Ok)

                else:
                    QMessageBox.warning(self, "Warning", "Problem in the Matrix export system:" + str(e),
                                        QMessageBox.StandardButton.Ok)
        sito = self.DATA_LIST[0].sito
        # area = self.DATA_LIST[1].area
        search_dict = {
            'sito': "'" + str(sito) + "'",
            # 'area': "'" + str(area) + "'"
        }

        periodizz_data_list = self.DB_MANAGER.query_bool(search_dict, 'PERIODIZZAZIONE')

        periodi_data_values = []

        for a in periodizz_data_list:
            periodi_data_values.append([a.periodo, a.fase, a.datazione_estesa])

        periodi_us_list = []

        clust_number = 0
        for i in periodi_data_values:
            search_dict = {
                'sito': "'" + str(sito) + "'",
                'periodo_iniziale': "'" + str(i[0]) + "'",
                'fase_iniziale': "'" + str(i[1]) + "'",
                'datazione': "'" + str(i[2]) + "'"
            }
            search_dict2 = {
                'sito': "'" + str(sito) + "'",
                'periodo_iniziale': "'" + str(i[0]) + "'",
                'fase_iniziale': "'" + str(i[1]) + "'"
            }
            us_group = self.DB_MANAGER.query_bool(search_dict2, 'US')

            cluster_label = "cluster%s" % (clust_number)

            if self.L == 'it':
                periodo_label = "Periodo %s : Fase %s : %s" % (str(i[0]), str(i[1]), str(i[2]))

                sing_per = [cluster_label, periodo_label]

                sing_us = []
                sing_ut = []

            elif self.L == 'de':
                periodo_label = "Period %s : Phase %s : %s" % (str(i[0]), str(i[1]), str(i[2]))

                sing_per = [cluster_label, periodo_label]

                sing_us = []
                sing_ut = []


            else:
                periodo_label = "Period %s : Phase %s : %s" % (str(i[0]), str(i[1]), str(i[2]))

                sing_per = [cluster_label, periodo_label]

                sing_us = []
                sing_ut = []
            for rec in us_group:
                # sing_ut.append(rec.unita_tipo)
                # sing_ut.append(rec.unita_tipo)

                sing_us.append(rec.us)
                # sing_def.append(rec.d_stratigrafica)

            sing_per.insert(0, sing_us)
            # sing_per.insert(0, sing_ut )
            periodi_us_list.append(sing_per)

            clust_number += 1

        matrix_exp = ViewHarrisMatrix(data, negative, conteporane, '', '', periodi_us_list)

        data_plotting = matrix_exp.export_matrix



        return data_plotting

class pyarchinit_view_Matrix_pre(QDialog, MAIN_DIALOG_CLASS):
    L = QgsSettings().value("locale/userLocale", "it", type=str)[:2]
    MSG_BOX_TITLE = "PyArchInit - Harrys Matrix"
    DB_MANAGER = ""
    DATA_LIST = ""
    ID_US_DICT = {}

    HOME = os.environ['PYARCHINIT_HOME']

    def __init__(self, iface, data_list, id_us_dict):
        super().__init__()
        self.iface = iface
        self.pyQGIS = Pyarchinit_pyqgis(iface)
        self.DATA_LIST = data_list
        self.ID_US_DICT = id_us_dict
        self.setupUi(self)

        ##      self.textbox.setText('1 2 3 4')
        # self.on_draw()
        try:
            self.DB_connect()
        except:
            pass

    def DB_connect(self):
        conn = Connection()
        conn_str = conn.conn_str()
        try:
            self.DB_MANAGER = get_db_manager(conn_str, use_singleton=True)
        except Exception as e:
            e = str(e)

            if self.L == 'it':
                QMessageBox.warning(self, "Attenzione",
                                    "bug! Scrivere allo sviluppatore <br> Error: <br>" + str(e),
                                    QMessageBox.StandardButton.Ok)
            if self.L == 'it':
                QMessageBox.warning(self, "Warnung",
                                    "bug! Schreiben Sie an den Entwickler <br> Error: <br>" + str(e),
                                    QMessageBox.StandardButton.Ok)

            else:
                QMessageBox.warning(self, "Alert",
                                    "bug! write to the developer <br> Error: <br>" + str(e),
                                    QMessageBox.StandardButton.Ok)

    def urlify(self, s):

        # Rimuove tutti i caratteri che non sono parole (tutto tranne i numeri e le lettere)
        s = re.sub(r"[^\w\s]", ' ', s)

        # Sostituire tutti gli spazi bianchi con un underscore
        s = re.sub(r"\s+", '_', s)

        return s

    def generate_matrix_3(self):
        data = []
        negative = []
        conteporane = []
        
        # Prepara lista delle US visibili per filtraggio
        visible_us_set = set()
        bridge_us_set = set()  # US ponte per mantenere continuità
        
        if hasattr(self, 'visible_us_list') and self.visible_us_list:
            for area_val, us_val in self.visible_us_list:
                visible_us_set.add(f"{area_val}_US{us_val}")
        
        print(f"DEBUG - Total records in DATA_LIST: {len(self.DATA_LIST)}")
        print(f"DEBUG - Visible US list length: {len(self.visible_us_list) if hasattr(self, 'visible_us_list') and self.visible_us_list else 0}")
        
        # Primo pass: identifica US ponte necessarie per mantenere continuità
        if visible_us_set:
            print(f"DEBUG - Looking for bridge US to maintain continuity...")
            for sing_rec in self.DATA_LIST:
                us = str(sing_rec['us'])
                area = str(sing_rec['area'])
                current_us_key = f"{area}_US{us}"
                
                if current_us_key in visible_us_set:
                    try:
                        rapporti_stratigrafici = eval(sing_rec['rapporti'])
                        for sing_rapp in rapporti_stratigrafici:
                            if len(sing_rapp) >= 2 and sing_rapp[1] != '':
                                target_area = str(sing_rapp[2]) if len(sing_rapp) > 2 else area
                                target_us_key = f"{target_area}_US{sing_rapp[1]}"
                                
                                # Se target non è visibile ma necessario per continuità, aggiungilo come ponte
                                if target_us_key not in visible_us_set:
                                    bridge_us_set.add(target_us_key)
                                    print(f"DEBUG - Added bridge US: {target_us_key}")
                    except:
                        pass
            
            print(f"DEBUG - Bridge US found: {len(bridge_us_set)}")
        
        # Combina visible e bridge US
        all_us_set = visible_us_set | bridge_us_set if visible_us_set else set()
        print(f"DEBUG - Total US to process: {len(all_us_set)}")
        
        # Set per tracciare relazioni già aggiunte e prevenire cicli semplici
        added_relations = set()
        
        for sing_rec in self.DATA_LIST:
            us = str(sing_rec['us'])
            area = str(sing_rec['area'])
            current_us_key = f"{area}_US{us}"
            
            # Se abbiamo una lista di US visibili, filtra usando all_us_set (include bridge US)
            if all_us_set and current_us_key not in all_us_set:
                print(f"DEBUG - Skipping US {current_us_key} - not in visible/bridge set")
                continue
            else:
                print(f"DEBUG - Processing US {current_us_key}")

            try:
                rapporti_stratigrafici = eval(sing_rec['rapporti'])
            except:
                print(f"DEBUG - Error parsing rapporti for US {current_us_key}: {sing_rec.get('rapporti', 'N/A')}")
                rapporti_stratigrafici = []


            try:
                for sing_rapp in rapporti_stratigrafici:
                    if len(sing_rapp) >= 2 and sing_rapp[1] != '':
                        # Gestisce sia formato a 2 elementi che formato a 3+ elementi
                        target_area = str(sing_rapp[2]) if len(sing_rapp) > 2 else area
                        target_us_key = f"{target_area}_US{sing_rapp[1]}"
                        
                        # Se abbiamo filtro e l'US target non è nella lista (visible + bridge), salta
                        if all_us_set and target_us_key not in all_us_set:
                            print(f"DEBUG - Skipping relation to {target_us_key} - not in processed set")
                            continue
                            
                        if sing_rapp[0] in ['Covers', 'Abuts', 'Fills', 'Copre', 'Si appoggia a', 'Riempie', 'Verfüllt',
                                            'Bindet an', 'Entspricht']:
                            harris_rapp = (current_us_key, target_us_key)
                            reverse_relation = (target_us_key, current_us_key)
                            
                            # Evita cicli diretti
                            if harris_rapp not in added_relations and reverse_relation not in added_relations:
                                data.append(harris_rapp)
                                added_relations.add(harris_rapp)
                        elif sing_rapp[0] in ['Coperto da', 'Covered by', 'Riempito da']:
                            # Inverti la relazione per "coperto da"
                            harris_rapp = (target_us_key, current_us_key)
                            reverse_relation = (current_us_key, target_us_key)
                            
                            # Evita cicli diretti
                            if harris_rapp not in added_relations and reverse_relation not in added_relations:
                                data.append(harris_rapp)
                                added_relations.add(harris_rapp)

                        elif sing_rapp[0] in ['Taglia', 'Cuts', 'Schneidet']:
                            harris_rapp1 = (current_us_key, target_us_key)
                            if harris_rapp1 not in added_relations:
                                negative.append(harris_rapp1)
                                added_relations.add(harris_rapp1)
                        elif sing_rapp[0] in ['Tagliato da', 'Cut by']:
                            # Inverti la relazione per "tagliato da"
                            harris_rapp1 = (target_us_key, current_us_key)
                            if harris_rapp1 not in added_relations:
                                negative.append(harris_rapp1)
                                added_relations.add(harris_rapp1)

                        elif sing_rapp[0] in ['Si lega a', 'Uguale a', 'Connected to', 'Same as', 'Liegt über',
                                            'Stützt sich auf', 'Gli si appoggia', '<']:
                            harris_rapp2 = (current_us_key, target_us_key)
                            if harris_rapp2 not in added_relations:
                                conteporane.append(harris_rapp2)
                                added_relations.add(harris_rapp2)
                        elif sing_rapp[0] in ['Riempie', 'Fills']:
                            harris_rapp = (current_us_key, target_us_key)
                            reverse_relation = (target_us_key, current_us_key)
                            
                            # Evita cicli diretti
                            if harris_rapp not in added_relations and reverse_relation not in added_relations:
                                data.append(harris_rapp)
                                added_relations.add(harris_rapp)
                        elif sing_rapp[0] in ['Riempito da', 'Filled by']:
                            harris_rapp = (target_us_key, current_us_key)
                            reverse_relation = (current_us_key, target_us_key)
                            
                            # Evita cicli diretti
                            if harris_rapp not in added_relations and reverse_relation not in added_relations:
                                data.append(harris_rapp)
                                added_relations.add(harris_rapp)
            except Exception as e:
                print(f"Errore durante la generazione della matrice per US {current_us_key}: {e}")
                if self.L == 'it':
                    QMessageBox.warning(self, "Warning", "Problema nel sistema di esportazione del Matrix:" + str(e),
                                        QMessageBox.StandardButton.Ok)
                elif self.L == 'de':
                    QMessageBox.warning(self, "Warnung", "Problem im Matrix-Exportsystem:" + str(e),
                                        QMessageBox.StandardButton.Ok)
                else:
                    QMessageBox.warning(self, "Warning", "Problem in the Matrix export system:" + str(e),
                                        QMessageBox.StandardButton.Ok)
        sito = self.DATA_LIST[0]['sito']
        # area = self.DATA_LIST[0].area

        search_dict = {
            'sito': "'" + str(sito) + "'",

        }

        periodizz_data_list = self.DB_MANAGER.query_bool(search_dict, 'PERIODIZZAZIONE')

        periodi_data_values = []

        for a in periodizz_data_list:
            periodi_data_values.append([a.cont_per, a.datazione_estesa, a.periodo, a.fase, a.descrizione])

        # Clear the previous contents of the list
        periodi_us_list = []

        clust_number = 0

        # Get all the areas
        areas = set([rec['area'] for rec in self.DATA_LIST if rec['sito'] == sito])

        # per = set([rec.fase_iniziale for rec in self.DATA_LIST if rec.sito == sito])  # update here
        cluster_label = "cluster%s" % clust_number

        # Iterate over the unique areas
        for area in areas:

            for i in periodi_data_values:
                search_dict2 = {
                    'sito': "'" + str(sito) + "'",
                    'area': "'" + str(area) + "'",  # add 'area' to the search_dict2
                    'periodo_iniziale': "'" + str(i[2]) + "'",
                    'fase_iniziale': "'" + str(i[3]) + "'"

                }
                us_group = self.DB_MANAGER.query_bool(search_dict2, 'US')

                periodo_label = "%s" % (str(i[1]))

                # Filtra solo le US visibili se abbiamo un filtro
                if visible_us_set:
                    sing_us = []
                    for rec in us_group:
                        us_key = f"{rec.area}_US{rec.us}"
                        if us_key in visible_us_set:
                            sing_us.append(us_key)
                else:
                    sing_us = [rec.area + '_' + 'US' + str(rec.us) for rec in us_group]

                # Solo aggiungi se ci sono US visibili
                if sing_us:
                    fase = "Fase%s: %s" % (str(i[3]), str(i[4]))
                    sing_fase = [fase,
                                 sing_us]  # create a nested list for each 'periodo_fase' with its corresponding list of 'us'

                    periodo = "%s" % (str(i[2]))
                    sing_per = [periodo,
                                sing_fase]  # create a nested list for each 'periodo_fase' with its corresponding list of 'us'

                    sing_per = [periodo_label,
                                sing_per]  # create a nested list for each 'periodo_fase' with its corresponding list of 'us'

                    area_label = "%s" % str(area)  # create area label
                    sing_area = [cluster_label, area_label,
                                 sing_per]  # create list that includes area label and the nested 'sing_per' list

                    sito_label = "%s" % str(sito)  # create sito label
                    sing_sito = [cluster_label, sito_label,
                                 sing_area]  # create list that includes sito label and the nested 'sing_area' list

                    periodi_us_list.append(sing_sito)  # append the nested 'sing_sito' list to the 'periodi_us_list'

                clust_number += 1

        print(f"DEBUG - Data nodes: {len(data)}")
        print(f"DEBUG - Negative nodes: {len(negative)}")
        print(f"DEBUG - Conteporane nodes: {len(conteporane)}")
        print(f"DEBUG - Visible US set size: {len(visible_us_set)}")
        print(f"DEBUG - Visible US set: {list(visible_us_set)[:10]}")
        if data:
            print(f"DEBUG - Sample data: {data[:5]}")
        else:
            print("DEBUG - No data nodes generated!")
        
        matrix_exp = ViewHarrisMatrix(data, negative, conteporane, '', '', periodi_us_list)

        data_plotting = matrix_exp.export_matrix_3


        return data_plotting

        
