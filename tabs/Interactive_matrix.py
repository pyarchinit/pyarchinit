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

from builtins import range
from builtins import str
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
#from networkx.drawing.nx_agraph import *
from qgis.PyQt.QtWidgets import QDialog, QMessageBox
from qgis.PyQt.uic import loadUiType
from qgis.core import QgsSettings
from ..modules.db.pyarchinit_conn_strings import Connection
from ..modules.db.pyarchinit_db_manager import Pyarchinit_db_management
from ..modules.gis.pyarchinit_pyqgis import Pyarchinit_pyqgis
from ..modules.utility.pyarchinit_matrix_exp import *
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
                area=str(sing_rec.area)
                
                
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
                            harris_rapp = (un_t+us+'_'+defin+'_'+datazione+'_'+area,str(sing_rapp[2])+str(sing_rapp[1])+'_'+str(sing_rapp[3].replace(' ','_')+'_'+str(sing_rapp[4]))+'_'+str(sing_rapp[5]))
                            data.append(harris_rapp)
                        
                        
                    
                    if sing_rapp[0] == 'Taglia' or sing_rapp[0] == 'Cuts' or sing_rapp[0] == 'Schneidet':
                        if sing_rapp[1] != '':
                            harris_rapp1 = (un_t+us+'_'+defin+'_'+datazione+'_'+area,str(sing_rapp[2])+str(sing_rapp[1])+'_'+str(sing_rapp[3].replace(' ','_')+'_'+str(sing_rapp[4]))+'_'+str(sing_rapp[5]))
                            
                    
                    if sing_rapp[0] == 'Si lega a' or  sing_rapp[0] == 'Uguale a' or sing_rapp[0] == 'Connected to' or  sing_rapp[0] == 'Same as'or sing_rapp[0] == 'Liegt über' or  sing_rapp[0] == 'Stützt sich auf':
                        if sing_rapp[1] != '':
                            harris_rapp2 = (un_t+us+'_'+defin+'_'+datazione+'_'+area,str(sing_rapp[2])+str(sing_rapp[1])+'_'+str(sing_rapp[3].replace(' ','_')+'_'+str(sing_rapp[4]))+'_'+str(sing_rapp[5]))
                            conteporane.append(harris_rapp2)
                    
                    if sing_rapp[0] == '>' :
                        if sing_rapp[1] != '':
                            harris_rapp3 = (un_t+us+'_'+defin+'_'+datazione+'_'+area,str(sing_rapp[2])+str(sing_rapp[1])+'_'+str(sing_rapp[3].replace(' ','_')+'_'+str(sing_rapp[4]))+'_'+str(sing_rapp[5]))
                            connection.append(harris_rapp3)
                    
                    
                    if sing_rapp[0] == '>>' :
                        if sing_rapp[1] != '':
                            harris_rapp4 = (un_t+us+'_'+defin+'_'+datazione+'_'+area,str(sing_rapp[2])+str(sing_rapp[1])+'_'+str(sing_rapp[3].replace(' ','_')+'_'+str(sing_rapp[4]))+'_'+str(sing_rapp[5]))
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
        area = self.DATA_LIST[1].area
        search_dict_period = {
            'sito': "'" + str(sito) + "'",
            #'area': "'" + str(area) + "'"
        }
        search_dict_area = {
            'sito': "'" + str(sito) + "'",
            'area': "'" + str(area) + "'"
        }
        periodizz_data_list = self.DB_MANAGER.query_bool(search_dict_period, 'US')

        periodi_data_values = []
        
        area_data_list = self.DB_MANAGER.query_bool(search_dict_area, 'US')

        area_data_values = []
        
        
        periodi_us_list = []
        area_us_list =[]
        clust_number = 0
        clust_number_area = 0
        
        for b in area_data_list:
            
            area_data_values.append([b.area])
        for a in periodizz_data_list:
                
            periodi_data_values.append([a.periodo_iniziale, a.fase_iniziale,a.datazione, a.area])  
            
        
        
        for s in area_data_values:
            
            search_dict2 = {
                'sito': "'" + str(sito) + "'",
                'area': "'" + str(s[0]) + "'",
                
            }
            area_group = self.DB_MANAGER.query_bool(search_dict2, 'US')

            cluster_label_a = "cluster%s" % (clust_number_area)

            
            area_label = "Area %s " % (str(s[0]))
            sing_per_area = [cluster_label_a,  area_label]
            sing_us_area = []
              
            for rec in area_group:
                        
                sing_us_area.append(rec.area) 
        
            sing_per_area.insert(0,'')
            

                
                    
            
                         
            
        for i in periodi_data_values:
            # search_dict = {
                # 'sito': "'" + str(sito) + "'",
                # 'periodo_iniziale': "'" + str(i[0]) + "'",
                # 'fase_iniziale': "'" + str(i[1]) + "'",
                # 'datazione':"'" + str(i[2]) + "'"
            # }
            search_dict2 = {
                'sito': "'" + str(sito) + "'",
                'area': "'" + str(i[3]) + "'",
                'periodo_iniziale': "'" + str(i[0]) + "'",
                'fase_iniziale': "'" + str(i[1]) + "'"
            }
            us_group = self.DB_MANAGER.query_bool(search_dict2, 'US')

            cluster_label = "cluster%s" % (clust_number)

            # if self.L=='it':
                
                # periodo_label = "Periodo %s : Fase %s : %s" % (str(i[0]), str(i[1]),str(i[2]))
                
                # sing_per = [cluster_label,  periodo_label]
                
                # sing_us = []
                # sing_ut=[]
                
            
            # else:
                # periodo_label = "Period %s : Phase %s : %s" % (str(i[0]), str(i[1]), str(i[2]))

                # sing_per = [cluster_label, periodo_label]
            periodo_label = "Periodo %s : Fase %s : %s" % (str(i[0]), str(i[1]),str(i[2]))
                    
            sing_per = [cluster_label,  periodo_label]
            sing_us = []  
                
                
                       
            for rec in us_group:
                
                sing_us.append(rec.unita_tipo+str(rec.us)+'_'+rec.d_interpretativa.replace(' ','_')+'_'+rec.periodo_iniziale+'-'+rec.fase_iniziale+'_'+rec.area)
                    
            
                
            sing_per.insert(0, sing_us )
                  
        
            periodi_us_list.append(sing_per)
            # area_us_list.append(periodi_us_list)
            clust_number+= 1
                
            area_us_list.append(sing_per_area)
            clust_number_area += 1    
        
        
            
                    
                
       
                
        matrix_exp = HarrisMatrix(data,negative,conteporane,connection,connection_to, periodi_us_list,area_us_list)
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

    # def hierarchy_pos(G, root=None, width=1., vert_gap = 0.2, vert_loc = 0, xcenter = 0.5):

        # '''
        # From Joel's answer at https://stackoverflow.com/a/29597209/2966723.  
        # Licensed under Creative Commons Attribution-Share Alike 
        
        # If the graph is a tree this will return the positions to plot this in a 
        # hierarchical layout.
        
        # G: the graph (must be a tree)
        
        # root: the root node of current branch 
        # - if the tree is directed and this is not given, 
          # the root will be found and used
        # - if the tree is directed and this is given, then 
          # the positions will be just for the descendants of this node.
        # - if the tree is undirected and not given, 
          # then a random choice will be used.
        
        # width: horizontal space allocated for this branch - avoids overlap with other branches
        
        # vert_gap: gap between levels of hierarchy
        
        # vert_loc: vertical location of root
        
        # xcenter: horizontal location of root
        # '''
        # if not nx.is_tree(G):
            # raise TypeError('cannot use hierarchy_pos on a graph that is not a tree')

        # if root is None:
            # if isinstance(G, nx.DiGraph):
                # root = next(iter(nx.topological_sort(G)))  #allows back compatibility with nx version 1.11
            # else:
                # root = random.choice(list(G.nodes))

        # def _hierarchy_pos(G, root, width=1., vert_gap = 0.2, vert_loc = 0, xcenter = 0.5, pos = None, parent = None):
            # '''
            # see hierarchy_pos docstring for most arguments

            # pos: a dict saying where all nodes go if they have been assigned
            # parent: parent of this branch. - only affects it if non-directed

            # '''
        
            # if pos is None:
                # pos = {root:(xcenter,vert_loc)}
            # else:
                # pos[root] = (xcenter, vert_loc)
            # children = list(G.neighbors(root))
            # if not isinstance(G, nx.DiGraph) and parent is not None:
                # children.remove(parent)  
            # if len(children)!=0:
                # dx = width/len(children) 
                # nextx = xcenter - width/2 - dx/2
                # for child in children:
                    # nextx += dx
                    # pos = _hierarchy_pos(G,child, width = dx, vert_gap = vert_gap, 
                                        # vert_loc = vert_loc-vert_gap, xcenter=nextx,
                                        # pos=pos, parent = root)
            # return pos

                
        # return _hierarchy_pos(G, root, width, vert_gap, vert_loc, xcenter)
    
    
    # def plot_matrix(self,dp):
        
        # G1 = nx.DiGraph(dp)  # now make it a Graph
        # #nx.communicability(G1)
        # pos = graphviz_layout(G1,prog='dot')
        # #assert_equal(nx.flow_hierarchy(G1))
        # nx.draw(G1,pos,with_labels=True, arrows=True)
        
        # limits=plt.axis('on')
        # #plt.show()
        # self.widgetMatrix.canvas.ax.set_title('click su una US per disegnarla a video', picker=True)
        
        # points = []
        # key = []
        # for k, v in list(pos.items()):
            # key.append(k)
            # points.append(v)

        # for i in range(len(key)):
            # self.widgetMatrix.canvas.ax.text(points[i][0], points[i][1], key[i], picker=True, ha='center', alpha=0)
        
        
        # self.widgetMatrix.canvas.mpl_connect('pick_event', self.on_pick)
        # self.widgetMatrix.canvas.draw()
        
    # def on_pick(self, event):
        
        # text = event.artist
        # value = text.get_prop_tup()
        # text_to_pass = value[2]
        # idus = self.ID_US_DICT[int(text_to_pass)]
        # self.pyQGIS.charge_vector_layers_from_matrix(idus)
        