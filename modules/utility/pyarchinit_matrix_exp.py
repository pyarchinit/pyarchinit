# -*- coding: utf-8 -*-
"""
/***************************************************************************
    pyArchInit Plugin  - A QGIS plugin to manage archaeological dataset
    stored in Postgres
    -------------------
    begin                : 2018-04-24
    copyright            : (C) 2018 by Salvatore Larosa
    email                : lrssvtml (at) gmail (dot) com
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
import os
import subprocess
from qgis.PyQt import QtCore
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtCore import *
from qgis.core import QgsSettings
import datetime
from datetime import date
from graphviz import Digraph, Source
from .pyarchinit_OS_utility import Pyarchinit_OS_Utility
from ..db.pyarchinit_db_manager import Pyarchinit_db_management
from ...tabs.pyarchinit_setting_matrix import *
class HarrisMatrix:
    L=QgsSettings().value("locale/userLocale")[0:2]
    HOME = os.environ['PYARCHINIT_HOME']
    DB_MANAGER = ""
    TABLE_NAME = 'us_table'
    MAPPER_TABLE_CLASS = "US"
    ID_TABLE = "id_us"
    MATRIX = Setting_Matrix()
    #s=pyqtSignal(str)
    def __init__(self, sequence,negative,conteporene,connection,connection_to,periodi,area):
        self.sequence = sequence
        self.negative = negative
        self.periodi=periodi
        self.area=area
        self.conteporene=conteporene
        self.connection=connection
        self.connection_to=connection_to
        self.dialog = Setting_Matrix()        
        self.dialog.exec_()
    @property
    def export_matrix(self):
        G = Digraph(engine='dot',strict=False)
        G.attr(rankdir='TB')
        G.attr(compound='true')
        G.graph_attr['pad']="0.5"
        G.graph_attr['nodesep']="1"
        G.graph_attr['ranksep']="1.5"
        G.graph_attr['splines'] = 'ortho'
        G.graph_attr['dpi'] = str(self.dialog.lineEdit_dpi.text())
        elist1 = []
        elist2 = []
        elist3 = []
        elist4 = []
        elist5 = []
        
        if bool(self.dialog.checkBox_period.isChecked()):         
            for aa in self.periodi:
                with G.subgraph(name=aa[1]) as c:
                    for n in aa[0]:
                        c.attr('node',shape='record', label =str(n))
                        c.node(str(n))
                    c.attr(color='blue')
                    c.attr('node', shape='record', fillcolor='white', style='filled', gradientangle='90',label=aa[2])
                    c.node(aa[2])           
        for bb in self.sequence:
            a = (bb[0],bb[1])
            elist1.append(a)
        with G.subgraph(name='main') as e:
            e.attr(rankdir='TB')
            e.edges(elist1)
            e.node_attr['shape'] = str(self.dialog.combo_box_3.currentText())
            e.node_attr['style'] = str(self.dialog.combo_box_4.currentText())
            e.node_attr.update(style='filled', fillcolor=str(self.dialog.combo_box.currentText()))
            e.node_attr['color'] = 'black'    
            e.node_attr['penwidth'] = str(self.dialog.combo_box_5.currentText())
            e.edge_attr['penwidth'] = str(self.dialog.combo_box_5.currentText())
            e.edge_attr['style'] = str(self.dialog.combo_box_10.currentText())
            e.edge_attr.update(arrowhead=str(self.dialog.combo_box_11.currentText()), arrowsize=str(self.dialog.combo_box_12.currentText()))
            for cc in self.conteporene:
                a = (cc[0],cc[1])
                elist3.append(a)
            with G.subgraph(name='main1') as b:
                b.edges(elist3)
                b.node_attr['shape'] = str(self.dialog.combo_box_18.currentText())
                b.node_attr['style'] = str(self.dialog.combo_box_22.currentText())
                b.node_attr.update(style='filled', fillcolor=str(self.dialog.combo_box_17.currentText()))
                b.node_attr['color'] = 'black'    
                b.node_attr['penwidth'] = str(self.dialog.combo_box_19.currentText())
                b.edge_attr['penwidth'] = str(self.dialog.combo_box_19.currentText())
                b.edge_attr['style'] = str(self.dialog.combo_box_23.currentText())
                b.edge_attr.update(arrowhead=str(self.dialog.combo_box_21.currentText()), arrowsize=str(self.dialog.combo_box_24.currentText()))
            for dd in self.negative:
                a = (dd[0],dd[1])
                elist2.append(a)
            with G.subgraph(name='main2') as a:
                #a.attr(rank='same')
                a.edges(elist2)
                a.node_attr['shape'] = str(self.dialog.combo_box_6.currentText())
                a.node_attr['style'] = str(self.dialog.combo_box_8.currentText())
                a.node_attr.update(style='filled', fillcolor=str(self.dialog.combo_box_2.currentText()))
                a.node_attr['color'] = 'black'    
                a.node_attr['penwidth'] = str(self.dialog.combo_box_7.currentText())
                a.edge_attr['penwidth'] = str(self.dialog.combo_box_7.currentText())
                a.edge_attr['style'] = str(self.dialog.combo_box_15.currentText())
                a.edge_attr.update(arrowhead=str(self.dialog.combo_box_14.currentText()), arrowsize=str(self.dialog.combo_box_16.currentText()))    
            for ee in self.connection:
                a = (ee[0],ee[1])
                elist4.append(a)
            with G.subgraph(name='main3') as tr:
                #a.attr(rank='same')
                a.edges(elist4)
                a.node_attr['shape'] = str(self.dialog.combo_box_3.currentText())
                a.node_attr['style'] = str(self.dialog.combo_box_4.currentText())
                a.node_attr.update(style='filled', fillcolor=str(self.dialog.combo_box_2.currentText()))
                a.node_attr['color'] = 'black'    
                a.node_attr['penwidth'] = str(self.dialog.combo_box_5.currentText())
                a.edge_attr['penwidth'] = str(self.dialog.combo_box_5.currentText())
                a.edge_attr['style'] = str(self.dialog.combo_box_10.currentText())
                a.edge_attr.update(arrowhead=str(self.dialog.combo_box_11.currentText()), arrowsize=str(self.dialog.combo_box_16.currentText()))    
            for ff in self.connection_to:
                a = (ff[0],ff[1])
                elist5.append(a)
            with G.subgraph(name='main4') as tb:
                #a.attr(rank='same')
                a.edges(elist5)
                a.node_attr['shape'] = str(self.dialog.combo_box_6.currentText())
                a.node_attr['style'] = str(self.dialog.combo_box_8.currentText())
                a.node_attr.update(style='filled', fillcolor=str(self.dialog.combo_box_2.currentText()))
                a.node_attr['color'] = 'black'    
                a.node_attr['penwidth'] = str(self.dialog.combo_box_7.currentText())
                a.edge_attr['penwidth'] = str(self.dialog.combo_box_7.currentText())
                a.edge_attr['style'] = 'dashed'
                a.edge_attr.update(arrowhead=str(self.dialog.combo_box_14.currentText()), arrowsize=str(self.dialog.combo_box_16.currentText()))    
        if bool(self.dialog.checkBox_legend.isChecked()):
            with G.subgraph(name='cluster3') as j:
                j.attr(rank='max')
                j.attr(fillcolor='white', label='Legend', fontcolor='black',fontsize='16',
                style='filled')
                with G.subgraph(name='cluster3') as i:
                    i.attr(rank='max')
                    if self.L=='it':
                        i.node('a0', shape=str(self.dialog.combo_box_3.currentText()), fillcolor=str(self.dialog.combo_box.currentText()), style='filled', gradientangle='90',label='Ante/Post') 
                        i.edge('a0', 'a1',shape=str(self.dialog.combo_box_3.currentText()), fillcolor=str(self.dialog.combo_box.currentText()), style=str(self.dialog.combo_box_10.currentText()),arrowhead=str(self.dialog.combo_box_11.currentText()), arrowsize=str(self.dialog.combo_box_12.currentText()))
                        i.node('a1', shape=str(self.dialog.combo_box_6.currentText()), fillcolor=str(self.dialog.combo_box_2.currentText()), style='filled', gradientangle='90',label='Negative')
                        i.edge('a1', 'a2',shape=str(self.dialog.combo_box_8.currentText()), fillcolor=str(self.dialog.combo_box_2.currentText()), style=str(self.dialog.combo_box_15.currentText()),arrowhead=str(self.dialog.combo_box_14.currentText()), arrowsize=str(self.dialog.combo_box_16.currentText()))
                        i.node('a2', shape=str(self.dialog.combo_box_18.currentText()), fillcolor=str(self.dialog.combo_box_17.currentText()), style='filled', gradientangle='1',label='Cont.')
                        # i.node('node3', shape=str(self.dialog.combo_box_18.currentText()), fillcolor=str(self.dialog.combo_box_17.currentText()), style='filled', gradientangle='1')
                        i.edge('a2', 'a1',shape=str(self.dialog.combo_box_22.currentText()), fillcolor=str(self.dialog.combo_box_17.currentText()), style=str(self.dialog.combo_box_23.currentText()),arrowhead=str(self.dialog.combo_box_21.currentText()), arrowsize=str(self.dialog.combo_box_24.currentText()))
                    elif self.L=='de':
                        i.node('a0', shape=str(self.dialog.combo_box_3.currentText()), fillcolor=str(self.dialog.combo_box.currentText()), style='filled', gradientangle='90',label='Ante/Post') 
                        i.edge('a0', 'a1',shape=str(self.dialog.combo_box_3.currentText()), fillcolor=str(self.dialog.combo_box.currentText()), style=str(self.dialog.combo_box_10.currentText()),arrowhead=str(self.dialog.combo_box_11.currentText()), arrowsize=str(self.dialog.combo_box_12.currentText()))
                        i.node('a1', shape=str(self.dialog.combo_box_6.currentText()), fillcolor=str(self.dialog.combo_box_2.currentText()), style='filled', gradientangle='90',label='Negativ')
                        i.edge('a1', 'a2',shape=str(self.dialog.combo_box_8.currentText()), fillcolor=str(self.dialog.combo_box_2.currentText()), style=str(self.dialog.combo_box_15.currentText()),arrowhead=str(self.dialog.combo_box_14.currentText()), arrowsize=str(self.dialog.combo_box_16.currentText()))
                        i.node('a2', shape=str(self.dialog.combo_box_18.currentText()), fillcolor=str(self.dialog.combo_box_17.currentText()), style='filled', gradientangle='1',label='Wie')
                        #i.node('node3', shape=str(self.dialog.combo_box_18.currentText()), fillcolor=str(self.dialog.combo_box_17.currentText()), style='filled', gradientangle='1')
                        i.edge('a2', 'a1',shape=str(self.dialog.combo_box_22.currentText()), fillcolor=str(self.dialog.combo_box_17.currentText()), style=str(self.dialog.combo_box_23.currentText()),arrowhead=str(self.dialog.combo_box_21.currentText()), arrowsize=str(self.dialog.combo_box_24.currentText()))
                    else:
                        i.node('a0', shape=str(self.dialog.combo_box_3.currentText()), fillcolor=str(self.dialog.combo_box.currentText()), style='filled', gradientangle='90',label='Ante/Post') 
                        i.edge('a0', 'a1',shape=str(self.dialog.combo_box_3.currentText()), fillcolor=str(self.dialog.combo_box.currentText()), style=str(self.dialog.combo_box_10.currentText()),arrowhead=str(self.dialog.combo_box_11.currentText()), arrowsize=str(self.dialog.combo_box_12.currentText()))
                        i.node('a1', shape=str(self.dialog.combo_box_6.currentText()), fillcolor=str(self.dialog.combo_box_2.currentText()), style='filled', gradientangle='90',label='Negative')
                        i.edge('a1', 'a2',shape=str(self.dialog.combo_box_8.currentText()), fillcolor=str(self.dialog.combo_box_2.currentText()), style=str(self.dialog.combo_box_15.currentText()),arrowhead=str(self.dialog.combo_box_14.currentText()), arrowsize=str(self.dialog.combo_box_16.currentText()))
                        i.node('a2', shape=str(self.dialog.combo_box_18.currentText()), fillcolor=str(self.dialog.combo_box_17.currentText()), style='filled', gradientangle='1',label='Same')
                        #i.node('node3', shape=str(self.dialog.combo_box_18.currentText()), fillcolor=str(self.dialog.combo_box_17.currentText()), style='filled', gradientangle='1')
                        i.edge('a2', 'a1',shape=str(self.dialog.combo_box_22.currentText()), fillcolor=str(self.dialog.combo_box_17.currentText()), style=str(self.dialog.combo_box_23.currentText()),arrowhead=str(self.dialog.combo_box_21.currentText()), arrowsize=str(self.dialog.combo_box_24.currentText()))
        dt = datetime.datetime.now()
        matrix_path = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_Matrix_folder")
        filename ='Harris_matrix'
        #f = open(filename, "w")
        G.format = 'dot'
        dot_file = G.render(directory=matrix_path, filename=filename)
        # For MS-Windows, we need to hide the console window.
        if Pyarchinit_OS_Utility.isWindows():
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = subprocess.SW_HIDE
        #cmd = ' '.join(['tred', dot_file])
        #dotargs = shlex.split(cmd)
        with open(os.path.join(matrix_path, filename + '_tred.dot'), "w") as out, \
                open(os.path.join(matrix_path, 'matrix_error.txt'), "w") as err:
            subprocess.Popen(['tred',dot_file],
                             #shell=True,
                             stdout=out,
                             stderr=err)
                             #startupinfo=si if Pyarchinit_OS_Utility.isWindows()else None)
        tred_file = os.path.join(matrix_path, filename + '_tred.dot')
        ######################trasformazione in jsone xdot_jason###########################################
        # with open(os.path.join(matrix_path, filename + '_tred.gml'), "w") as out:
            # subprocess.Popen(['gv2gml',tred_file],
                             # #shell=True,
                             # stdout=out)
                             #startupinfo=si if Pyarchinit_OS_Utility.isWindows()else None)
        # with open(os.path.join(matrix_path, filename + '_tred.xdot_json'), "w") as out:
            # subprocess.Popen(['tred',tred_file],
                             # #shell=True,
                             # stdout=out)
                             # #startupinfo=si if Pyarchinit_OS_Utility.isWindows()else None)
        ##############################################################################################
        f = Source.from_file(tred_file, format='png')
        f.render()
        g = Source.from_file(tred_file, format='jpg')
        g.render()
        return g,f
        # return f
    @property
    def export_matrix_2(self):
        G = Digraph(engine='dot',strict=False)
        G.attr(rankdir='TB')
        G.attr(compound='true')
        G.graph_attr['pad']="0.5"
        G.graph_attr['nodesep']="1"
        G.graph_attr['ranksep']="1.5"
        G.graph_attr['splines'] = 'ortho'
        G.graph_attr['dpi'] = str(self.dialog.lineEdit_dpi.text())
        elist1 = []
        elist2 = []
        elist3 = []
        elist4 = []
        elist5 = []
        if bool(self.dialog.checkBox_period.isChecked()):         
            
            
                      
            for aa in self.periodi:
                with G.subgraph(name=aa[1]) as c:
                    for n in aa[0]:
                        c.attr('node',shape='record', label =str(n))
                        c.node(str(n))
                    c.attr(color='blue')
                    c.attr('node', shape='record', fillcolor='white', style='filled', gradientangle='90',label=aa[2])
                    c.node(aa[2])           
                   
        for ab in self.area:
            with G.subgraph(name=ab[1]) as s:
                for n in ab[0]:
                    s.attr('node',shape='record', label =str(n))
                    s.node(str(n))
                s.attr(color='green')
                s.attr('node', shape='record', fillcolor='white', style='filled', gradientangle='90',label=ab[2])
                s.node(ab[2])    
        for bb in self.sequence:
            a = (bb[0],bb[1])            
            elist1.append(a)
        with G.subgraph(name='main') as e:
            e.attr(rankdir='TB')
            e.edges(elist1)            
            e.node_attr['shape'] = str(self.dialog.combo_box_3.currentText())
            e.node_attr['style'] = str(self.dialog.combo_box_4.currentText())
            e.node_attr.update(style='filled', fillcolor=str(self.dialog.combo_box.currentText()))
            e.node_attr['color'] = 'black'
            e.node_attr['penwidth'] = str(self.dialog.combo_box_5.currentText())
            e.edge_attr['penwidth'] = str(self.dialog.combo_box_5.currentText())
            e.edge_attr['style'] = str(self.dialog.combo_box_10.currentText())
            e.edge_attr.update(arrowhead=str(self.dialog.combo_box_11.currentText()), arrowsize=str(self.dialog.combo_box_12.currentText()))
            for cc in self.conteporene:
                a = (cc[0],cc[1])
                elist3.append(a)
            with G.subgraph(name='main1') as b:
                b.edges(elist3)
                b.node_attr['shape'] = str(self.dialog.combo_box_18.currentText())
                b.node_attr['style'] = str(self.dialog.combo_box_22.currentText())
                b.node_attr.update(style='filled', fillcolor=str(self.dialog.combo_box_17.currentText()))
                b.node_attr['color'] = 'black'  
                b.node_attr['penwidth'] = str(self.dialog.combo_box_19.currentText())
                b.edge_attr['penwidth'] = str(self.dialog.combo_box_19.currentText())
                b.edge_attr['style'] = str(self.dialog.combo_box_23.currentText())
                b.edge_attr.update(arrowhead=str(self.dialog.combo_box_21.currentText()), arrowsize=str(self.dialog.combo_box_24.currentText()))
            for dd in self.negative:
                a = (dd[0],dd[1])
                elist2.append(a)
            with G.subgraph(name='main2') as a:
                #a.attr(rank='same')
                a.edges(elist2)
                a.node_attr['shape'] = str(self.dialog.combo_box_6.currentText())
                a.node_attr['style'] = str(self.dialog.combo_box_8.currentText())
                a.node_attr.update(style='filled', fillcolor=str(self.dialog.combo_box_2.currentText()))
                a.node_attr['color'] = 'black'    
                a.node_attr['penwidth'] = str(self.dialog.combo_box_7.currentText())
                a.edge_attr['penwidth'] = str(self.dialog.combo_box_7.currentText())
                a.edge_attr['style'] = str(self.dialog.combo_box_15.currentText())
                a.edge_attr.update(arrowhead=str(self.dialog.combo_box_14.currentText()), arrowsize=str(self.dialog.combo_box_16.currentText()))    
            for ee in self.connection:
                a = (ee[0],ee[1])
                elist4.append(a)
            with G.subgraph(name='main3') as r:
                #a.attr(rank='same')
                r.edges(elist4)
                r.node_attr['shape'] = str(self.dialog.combo_box_26.currentText())
                r.node_attr['style'] = str(self.dialog.combo_box_30.currentText())
                r.node_attr.update(style='filled', fillcolor=str(self.dialog.combo_box_28.currentText()))
                r.node_attr['color'] = 'black'    
                r.node_attr['penwidth'] = str(self.dialog.combo_box_27.currentText())
                r.edge_attr['penwidth'] = str(self.dialog.combo_box_27.currentText())
                r.edge_attr['style'] = str(self.dialog.combo_box_31.currentText())
                r.edge_attr.update(arrowhead=str(self.dialog.combo_box_29.currentText()), arrowsize=str(self.dialog.combo_box_32.currentText()))    
            for ff in self.connection_to:
                a = (ff[0],ff[1])
                elist5.append(a)
            with G.subgraph(name='main4') as t:
                #a.attr(rank='same')
                t.edges(elist5)
                t.node_attr['shape'] = str(self.dialog.combo_box_34.currentText())
                t.node_attr['style'] = str(self.dialog.combo_box_38.currentText())
                t.node_attr.update(style='filled', fillcolor=str(self.dialog.combo_box_36.currentText()))
                t.node_attr['color'] = 'black'    
                t.node_attr['penwidth'] = str(self.dialog.combo_box_35.currentText())
                t.edge_attr['penwidth'] = str(self.dialog.combo_box_35.currentText())
                t.edge_attr['style'] = str(self.dialog.combo_box_39.currentText())
                t.edge_attr.update(arrowhead=str(self.dialog.combo_box_37.currentText()), arrowsize=str(self.dialog.combo_box_40.currentText()))    
        if bool(self.dialog.checkBox_legend.isChecked()):
            with G.subgraph(name='cluster3') as j:
                j.attr(rank='max')
                j.attr(fillcolor='white', label='Legend', fontcolor='black',fontsize='16',
                style='filled')
                with G.subgraph(name='cluster3') as i:
                    i.attr(rank='max')
                    if self.L=='it':
                        i.node('a0', shape=str(self.dialog.combo_box_3.currentText()), fillcolor=str(self.dialog.combo_box.currentText()), style='filled', gradientangle='90',label='Ante/Post') 
                        i.edge('a0', 'a1',shape=str(self.dialog.combo_box_3.currentText()), fillcolor=str(self.dialog.combo_box.currentText()), style=str(self.dialog.combo_box_10.currentText()),arrowhead=str(self.dialog.combo_box_11.currentText()), arrowsize=str(self.dialog.combo_box_12.currentText()))
                        i.node('a1', shape=str(self.dialog.combo_box_6.currentText()), fillcolor=str(self.dialog.combo_box_2.currentText()), style='filled', gradientangle='90',label='Negative')
                        i.edge('a1', 'a2',shape=str(self.dialog.combo_box_8.currentText()), fillcolor=str(self.dialog.combo_box_2.currentText()), style=str(self.dialog.combo_box_15.currentText()),arrowhead=str(self.dialog.combo_box_14.currentText()), arrowsize=str(self.dialog.combo_box_16.currentText()))
                        i.node('a2', shape=str(self.dialog.combo_box_18.currentText()), fillcolor=str(self.dialog.combo_box_17.currentText()), style='filled', gradientangle='1',label='Cont.')
                        # i.node('node3', shape=str(self.dialog.combo_box_18.currentText()), fillcolor=str(self.dialog.combo_box_17.currentText()), style='filled', gradientangle='1')
                        i.edge('a2', 'a1',shape=str(self.dialog.combo_box_22.currentText()), fillcolor=str(self.dialog.combo_box_17.currentText()), style=str(self.dialog.combo_box_23.currentText()),arrowhead=str(self.dialog.combo_box_21.currentText()), arrowsize=str(self.dialog.combo_box_24.currentText()))
                    elif self.L=='de':
                        i.node('a0', shape=str(self.dialog.combo_box_3.currentText()), fillcolor=str(self.dialog.combo_box.currentText()), style='filled', gradientangle='90',label='Ante/Post') 
                        i.edge('a0', 'a1',shape=str(self.dialog.combo_box_3.currentText()), fillcolor=str(self.dialog.combo_box.currentText()), style=str(self.dialog.combo_box_10.currentText()),arrowhead=str(self.dialog.combo_box_11.currentText()), arrowsize=str(self.dialog.combo_box_12.currentText()))
                        i.node('a1', shape=str(self.dialog.combo_box_6.currentText()), fillcolor=str(self.dialog.combo_box_2.currentText()), style='filled', gradientangle='90',label='Negativ')
                        i.edge('a1', 'a2',shape=str(self.dialog.combo_box_8.currentText()), fillcolor=str(self.dialog.combo_box_2.currentText()), style=str(self.dialog.combo_box_15.currentText()),arrowhead=str(self.dialog.combo_box_14.currentText()), arrowsize=str(self.dialog.combo_box_16.currentText()))
                        i.node('a2', shape=str(self.dialog.combo_box_18.currentText()), fillcolor=str(self.dialog.combo_box_17.currentText()), style='filled', gradientangle='1',label='Wie')
                        #i.node('node3', shape=str(self.dialog.combo_box_18.currentText()), fillcolor=str(self.dialog.combo_box_17.currentText()), style='filled', gradientangle='1')
                        i.edge('a2', 'a1',shape=str(self.dialog.combo_box_22.currentText()), fillcolor=str(self.dialog.combo_box_17.currentText()), style=str(self.dialog.combo_box_23.currentText()),arrowhead=str(self.dialog.combo_box_21.currentText()), arrowsize=str(self.dialog.combo_box_24.currentText()))
                    else:
                        i.node('a0', shape=str(self.dialog.combo_box_3.currentText()), fillcolor=str(self.dialog.combo_box.currentText()), style='filled', gradientangle='90',label='Ante/Post') 
                        i.edge('a0', 'a1',shape=str(self.dialog.combo_box_3.currentText()), fillcolor=str(self.dialog.combo_box.currentText()), style=str(self.dialog.combo_box_10.currentText()),arrowhead=str(self.dialog.combo_box_11.currentText()), arrowsize=str(self.dialog.combo_box_12.currentText()))
                        i.node('a1', shape=str(self.dialog.combo_box_6.currentText()), fillcolor=str(self.dialog.combo_box_2.currentText()), style='filled', gradientangle='90',label='Negative')
                        i.edge('a1', 'a2',shape=str(self.dialog.combo_box_8.currentText()), fillcolor=str(self.dialog.combo_box_2.currentText()), style=str(self.dialog.combo_box_15.currentText()),arrowhead=str(self.dialog.combo_box_14.currentText()), arrowsize=str(self.dialog.combo_box_16.currentText()))
                        i.node('a2', shape=str(self.dialog.combo_box_18.currentText()), fillcolor=str(self.dialog.combo_box_17.currentText()), style='filled', gradientangle='1',label='Same')
                        #i.node('node3', shape=str(self.dialog.combo_box_18.currentText()), fillcolor=str(self.dialog.combo_box_17.currentText()), style='filled', gradientangle='1')
                        i.edge('a2', 'a1',shape=str(self.dialog.combo_box_22.currentText()), fillcolor=str(self.dialog.combo_box_17.currentText()), style=str(self.dialog.combo_box_23.currentText()),arrowhead=str(self.dialog.combo_box_21.currentText()), arrowsize=str(self.dialog.combo_box_24.currentText()))
        dt = datetime.datetime.now()
        matrix_path = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_Matrix_folder")
        filename = ('%s') % (
        'Harris_matrix2ED')
        #f = open(filename, "w")
        G.format = 'dot'
        dot_file = G.render(directory=matrix_path, filename=filename)
        # For MS-Windows, we need to hide the console window.
        if Pyarchinit_OS_Utility.isWindows():
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = subprocess.SW_HIDE
        #cmd = ' '.join(['tred', dot_file])
        #dotargs = shlex.split(cmd)
        with open(os.path.join(matrix_path, filename + '_graphml.dot'), "w") as out:
            subprocess.Popen(['tred',dot_file],
                             #shell=True,
                             stdout=out)
        tred_file = os.path.join(matrix_path, filename + '_graphml.dot')                     
        g = Source.from_file(tred_file, format='jpg')
        g.render()
        return g

        
# class IntHarrisMatrix:
    # HOME = os.environ['PYARCHINIT_HOME']

    # def __init__(self, sequence, periodi):
        # self.sequence = sequence
        # self.periodi = periodi

    # def export_matrix(self):
        # G = Digraph(engine='dot', strict=False)
        # G.graph_attr['splines'] = 'ortho'
        # G.graph_attr['dpi'] = '300'
        # elist = []

        # for i in self.sequence:
            # a = (i[0], i[1])
            # elist.append(a)

        # with G.subgraph(name='main') as d:
            # d.edges(elist)
            # d.node_attr['shape'] = 'box'
            # d.node_attr['style'] = 'strocked'
            # d.node_attr['color'] = 'red'
            # d.attr(label='pyArchInit - Harris Matrix Export System')

        # for i in self.periodi:
            # with G.subgraph(name=i[1]) as c:
                # # c.attr(bgcolor='lightgrey')
                # for n in i[0]:
                    # c.attr('node', shape='square', label=str(n), color='blue')
                    # c.node(str(n))
                # c.attr(color='blue')
                # c.attr(label=i[2])

        # matrix_path = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_Matrix_folder")
        # filename = 'Harris_matrix'

        # G.format = 'dot'
        # dot_file = G.render(filename=filename, directory=matrix_path)

        # # For MS-Windows, we need to hide the console window.
        # if Pyarchinit_OS_Utility.isWindows():
            # si = subprocess.STARTUPINFO()
            # si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            # si.wShowWindow = subprocess.SW_HIDE

        # # cmd = ' '.join(['tred', dot_file])
        # # dotargs = shlex.split(cmd)

        # with open(os.path.join(matrix_path, filename + '_tred.dot'), "wb") as out, \
                # open(os.path.join(matrix_path, 'matrix_error.txt'), "wb") as err:
            # subprocess.Popen(['tred', dot_file],
                             # #shell=False,
                             # stdout=out,
                             # stderr=err)
                             # #startupinfo=si if Pyarchinit_OS_Utility.isWindows() else None)

        # tred_file = os.path.join(matrix_path, filename + '_tred.dot')
        # g = Source.from_file(tred_file, format='svg')
        # g.render()
        # f = Source.from_file(tred_file, format='png')
        # f.render()

        # return g                             