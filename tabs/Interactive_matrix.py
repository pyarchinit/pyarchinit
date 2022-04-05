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

# import networkx as nx
from builtins import range
from builtins import str
# from networkx.drawing.nx_agraph import graphviz_layout
from qgis.PyQt.QtWidgets import QDialog, QMessageBox
from qgis.PyQt.uic import loadUiType
from qgis.core import QgsSettings
from ..modules.db.pyarchinit_conn_strings import Connection
from ..modules.db.pyarchinit_db_manager import Pyarchinit_db_management
from ..modules.gis.pyarchinit_pyqgis import Pyarchinit_pyqgis
from ..modules.utility.pyarchinit_matrix_exp import HarrisMatrix
import re
MAIN_DIALOG_CLASS, _ = loadUiType(
    os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'Interactive_matrix.ui'))


class pyarchinit_Interactive_Matrix(QDialog, MAIN_DIALOG_CLASS):
    L=QgsSettings().value("locale/userLocale")[0:2]
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
            self.DB_MANAGER = Pyarchinit_db_management(conn_str)
            self.DB_MANAGER.connection()
        except Exception as e:
            e = str(e)
            
            if self.L=='it':
                QMessageBox.warning(self, "Attenzione",
                                "bug! Scrivere allo sviluppatore <br> Error: <br>" + str(e),
                                QMessageBox.Ok)
            if self.L=='it':
                QMessageBox.warning(self, "Warnung",
                                "bug! Schreiben Sie an den Entwickler <br> Error: <br>" + str(e),
                                QMessageBox.Ok)
                                
            else:
                QMessageBox.warning(self, "Alert",
                                "bug! write to the developer <br> Error: <br>" + str(e),
                                QMessageBox.Ok)                    
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
                            QMessageBox.Ok)
                    break        
                elif self.L=='de':
                    QMessageBox.warning(self, "Warnung", "Sie müssen den Einheitentyp und die startigraphische Interpretation im Tabellenwidget startigraphic reports eingeben",
                                    QMessageBox.Ok)
                    break                
                else:
                    QMessageBox.warning(self, "Warning", "You have to enter the unit type and startigraphic interpretation in the startigraphic reports tablewidget",
                                    QMessageBox.Ok)           
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
                                QMessageBox.Ok)
                    elif self.L=='de':
                        QMessageBox.warning(self, "Warnung", "Sie müssen den Einheitentyp und die startigraphische Interpretation im Tabellenwidget startigraphic reports eingeben",
                                        QMessageBox.Ok)
                                        
                    else:
                        QMessageBox.warning(self, "Warning", "You have to enter the unit type and startigraphic interpretation in the startigraphic reports tablewidget",
                                        QMessageBox.Ok)                    
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
                sing_ut=[]
                
            elif self.L=='de':
                periodo_label = "Period %s : Phase %s : %s" % (str(i[0]), str(i[1]),str(i[2]))

                sing_per = [cluster_label, periodo_label]
                
                sing_us = []
                sing_ut=[]
            
            
            else:
                periodo_label = "Period %s : Phase %s : %s" % (str(i[0]), str(i[1]), str(i[2]))

                sing_per = [cluster_label, periodo_label]

                sing_us = []  
                sing_ut = []
            for rec in us_group:
                #sing_ut.append(rec.unita_tipo)
                #sing_ut.append(rec.unita_tipo)
                # try: 
                    # if 'DOC' in rec.unita_tipo:
                        # sing_us.append(rec.unita_tipo+str(rec.us)+'_'+rec.doc_usv.replace(' ','_')+'_'+rec.periodo_iniziale+'-'+rec.fase_iniziale)
                    # else:
                sing_us.append(rec.unita_tipo+str(rec.us)+'_'+rec.d_interpretativa.replace(' ','_')+'_'+rec.periodo_iniziale+'-'+rec.fase_iniziale)
                # except:
                    # pass
                # else:
                    # sing_us.append(rec.unita_tipo+str(rec.us)+'_'+rec.d_interpretativa.replace(' ','_')+'_'+rec.periodo_iniziale+'-'+rec.fase_iniziale)
                #sing_def.append(rec.d_stratigrafica)
            
            sing_per.insert(0, sing_us )
            #sing_per.insert(0, sing_ut )
            periodi_us_list.append(sing_per)

            clust_number += 1
        
        matrix_exp = HarrisMatrix(data,negative,conteporane,connection,connection_to, periodi_us_list)
        try: 
            data_plotting_2 = matrix_exp.export_matrix_2
        except Exception as e :
            QMessageBox.information(self, "Info", str(e), QMessageBox.Ok)
        finally:
            data_plotting_2 = matrix_exp.export_matrix_2
        if self.L=='it':
            QMessageBox.information(self, "Info", "Esportazione completata", QMessageBox.Ok)
        elif self.L=='de':
            QMessageBox.information(self, "Info", "Exportieren kompliziert", QMessageBox.Ok)
        else:
            QMessageBox.information(self, "Info", "Exportation complited", QMessageBox.Ok)    
            
        return data_plotting_2
    def generate_matrix(self):
        data = []
        negative =[]
        conteporane=[]
        
        for sing_rec in self.DATA_LIST:
            us = str(sing_rec.us)
            un_t = str(sing_rec.unita_tipo)##per inserire il termine US o USM
            #datazione = str(sing_rec.datazione)##per inserire la datazione estesa
            #defin = str(sing_rec.d_stratigrafica.replace(' ','_'))##per inserire la definizione startigrafica
            
            rapporti_stratigrafici = eval(sing_rec.rapporti)
            
            try:
                for  sing_rapp in rapporti_stratigrafici:
                    
                    if   sing_rapp[0] == 'Covers' or  sing_rapp[0] == 'Abuts' or  sing_rapp[0] == 'Fills' or  sing_rapp[0] == 'Copre' or  sing_rapp[0] == 'Si appoggia a' or  sing_rapp[0] == 'Riempie'   or  sing_rapp[0] == 'Verfüllt' or sing_rapp[0] == 'Bindet an' or  sing_rapp[0] == 'Entspricht' :
                        if sing_rapp[1] != '':
                            harris_rapp = (us,str(sing_rapp[1]))
                            data.append(harris_rapp)
                        
                        
                    
                    if sing_rapp[0] == 'Taglia' or sing_rapp[0] == 'Cuts' or sing_rapp[0] == 'Schneidet':
                        if sing_rapp[1] != '':
                            harris_rapp1 = (us,str(sing_rapp[1]))
                            negative.append(harris_rapp1)
                            
                    
                    if sing_rapp[0] == 'Si lega a' or  sing_rapp[0] == 'Uguale a' or sing_rapp[0] == 'Connected to' or  sing_rapp[0] == 'Same as'or sing_rapp[0] == 'Liegt über' or  sing_rapp[0] == 'Stützt sich auf':
                        if sing_rapp[1] != '':
                            harris_rapp2 = (us,str(sing_rapp[1]))
                            conteporane.append(harris_rapp2)
                    
                    
            except Exception as e:
                    
                    if self.L=='it':
                        QMessageBox.warning(self, "Warning", "Problema nel sistema di esportazione del Matrix:" + str(e),
                                        QMessageBox.Ok)
                    elif self.L=='de':
                        QMessageBox.warning(self, "Warnung", "Problem im Matrix-Exportsystem:" + str(e),
                                        QMessageBox.Ok)
                                        
                    else:
                        QMessageBox.warning(self, "Warning", "Problem in the Matrix export system:" + str(e),
                                        QMessageBox.Ok)                    
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
                sing_ut=[]
                
            elif self.L=='de':
                periodo_label = "Period %s : Phase %s : %s" % (str(i[0]), str(i[1]),str(i[2]))

                sing_per = [cluster_label, periodo_label]
                
                sing_us = []
                sing_ut=[]
            
            
            else:
                periodo_label = "Period %s : Phase %s : %s" % (str(i[0]), str(i[1]), str(i[2]))

                sing_per = [cluster_label, periodo_label]

                sing_us = []  
                sing_ut = []
            for rec in us_group:
                #sing_ut.append(rec.unita_tipo)
                #sing_ut.append(rec.unita_tipo)
                
                sing_us.append(rec.us)
                #sing_def.append(rec.d_stratigrafica)
            
            sing_per.insert(0, sing_us )
            #sing_per.insert(0, sing_ut )
            periodi_us_list.append(sing_per)

            clust_number += 1
        
        matrix_exp = HarrisMatrix(data,negative,conteporane,'','',periodi_us_list)
        
        data_plotting = matrix_exp.export_matrix
        if self.L=='it':
            QMessageBox.information(self, "Info", "Esportazione completata", QMessageBox.Ok)
        elif self.L=='de':
            QMessageBox.information(self, "Info", "Exportieren kompliziert", QMessageBox.Ok)
        else:
            QMessageBox.information(self, "Info", "Exportation complited", QMessageBox.Ok)    
            
        return data_plotting

    