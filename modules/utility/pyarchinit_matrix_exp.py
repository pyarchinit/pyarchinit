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
    def __init__(self, sequence,negative,conteporene,periodi):
        self.sequence = sequence
        self.negative = negative
        self.periodi=periodi
        self.conteporene=conteporene
       
    @property
    def export_matrix(self):
        
        dialog = Setting_Matrix()
        
        dialog.exec_()
        
        
        G = Digraph(engine='dot',strict=False)
        G.attr(rankdir='TB')
        G.attr(compound='true')
        G.graph_attr['pad']="0.5"
        G.graph_attr['nodesep']="1"
        G.graph_attr['ranksep']="1.5"
        G.graph_attr['splines'] = 'ortho'
        #G.graph_attr['dpi'] = 
        
        
        elist1 = []
        elist2 = []
        elist3 = []
        
        
        
        # try:
            # for s in self.periodi:
                
                # #a.add_node(s[0])
                # a=m.add_group(s[2])    
                
            
            # for e in self.sequence: a.add_node(e[0],description=e[0])      
            # for e in  self.sequence:
                
                # b=a.add_edge(e[0],e[1])
              
            # for h in self.negative: a.add_node(h[0],description=h[0])
            # for h in  self.negative:
                # fc=a.add_node(b[0])
            
                
            # for j in self.conteporene: a.add_node(j[0],description=j[0])
            # for j  in  self.conteporene:
                
                # d=a.add_edge(j[0],j[1],arrowfoot= "none")
            
        # except:
            # pass
        # m.write_graph(r'C:\Users\utente\pyarchinit\pyarchinit_Matrix_folder\example.graphml', pretty_print=True)    
        if bool(dialog.checkBox_period.isChecked()):         
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
            
            e.node_attr['shape'] = str(dialog.combo_box_3.currentText())
            e.node_attr['style'] = str(dialog.combo_box_4.currentText())
            e.node_attr.update(style='filled', fillcolor=str(dialog.combo_box.currentText()))
            e.node_attr['color'] = 'black'    
            e.node_attr['penwidth'] = str(dialog.combo_box_5.currentText())
            e.edge_attr['penwidth'] = str(dialog.combo_box_5.currentText())
            e.edge_attr['style'] = str(dialog.combo_box_10.currentText())
            e.edge_attr.update(arrowhead=str(dialog.combo_box_11.currentText()), arrowsize=str(dialog.combo_box_12.currentText()))
            
            for cc in self.conteporene:
                a = (cc[0],cc[1])
                elist3.append(a)
        
            with G.subgraph(name='main1') as b:
                
                
                b.edges(elist3)
                
                b.node_attr['shape'] = str(dialog.combo_box_18.currentText())
                b.node_attr['style'] = str(dialog.combo_box_22.currentText())
                b.node_attr.update(style='filled', fillcolor=str(dialog.combo_box_17.currentText()))
                b.node_attr['color'] = 'black'    
                b.node_attr['penwidth'] = str(dialog.combo_box_19.currentText())
                b.edge_attr['penwidth'] = str(dialog.combo_box_19.currentText())
                b.edge_attr['style'] = str(dialog.combo_box_23.currentText())
                b.edge_attr.update(arrowhead=str(dialog.combo_box_21.currentText()), arrowsize=str(dialog.combo_box_24.currentText()))
                
            for dd in self.negative:
                a = (dd[0],dd[1])
                elist2.append(a)
        
            with G.subgraph(name='main2') as a:
                #a.attr(rank='same')
                a.edges(elist2)
                
                a.node_attr['shape'] = str(dialog.combo_box_6.currentText())
                a.node_attr['style'] = str(dialog.combo_box_8.currentText())
                a.node_attr.update(style='filled', fillcolor=str(dialog.combo_box_2.currentText()))
                a.node_attr['color'] = 'black'    
                a.node_attr['penwidth'] = str(dialog.combo_box_7.currentText())
                a.edge_attr['penwidth'] = str(dialog.combo_box_7.currentText())
                a.edge_attr['style'] = str(dialog.combo_box_15.currentText())
                a.edge_attr.update(arrowhead=str(dialog.combo_box_14.currentText()), arrowsize=str(dialog.combo_box_16.currentText()))    
                
            
        
        
        if bool(dialog.checkBox_legend.isChecked()):
            with G.subgraph(name='cluster3') as j:
                j.attr(rank='max')
                j.attr(fillcolor='white', label='Legend', fontcolor='black',fontsize='16',
                style='filled')
                with G.subgraph(name='cluster3') as i:
                    i.attr(rank='max')
                    if self.L=='it':
                        i.node('a0', shape=str(dialog.combo_box_3.currentText()), fillcolor=str(dialog.combo_box.currentText()), style='filled', gradientangle='90',label='Ante/Post') 
                        i.edge('a0', 'a1',shape=str(dialog.combo_box_3.currentText()), fillcolor=str(dialog.combo_box.currentText()), style=str(dialog.combo_box_10.currentText()),arrowhead=str(dialog.combo_box_11.currentText()), arrowsize=str(dialog.combo_box_12.currentText()))
                        
                        i.node('a1', shape=str(dialog.combo_box_6.currentText()), fillcolor=str(dialog.combo_box_2.currentText()), style='filled', gradientangle='90',label='Negative')
                        i.edge('a1', 'a2',shape=str(dialog.combo_box_8.currentText()), fillcolor=str(dialog.combo_box_2.currentText()), style=str(dialog.combo_box_15.currentText()),arrowhead=str(dialog.combo_box_14.currentText()), arrowsize=str(dialog.combo_box_16.currentText()))
                        
                        i.node('a2', shape=str(dialog.combo_box_18.currentText()), fillcolor=str(dialog.combo_box_17.currentText()), style='filled', gradientangle='1',label='Cont.')
                        # i.node('node3', shape=str(dialog.combo_box_18.currentText()), fillcolor=str(dialog.combo_box_17.currentText()), style='filled', gradientangle='1')
                        i.edge('a2', 'a1',shape=str(dialog.combo_box_22.currentText()), fillcolor=str(dialog.combo_box_17.currentText()), style=str(dialog.combo_box_23.currentText()),arrowhead=str(dialog.combo_box_21.currentText()), arrowsize=str(dialog.combo_box_24.currentText()))
                    elif self.L=='de':
                        i.node('a0', shape=str(dialog.combo_box_3.currentText()), fillcolor=str(dialog.combo_box.currentText()), style='filled', gradientangle='90',label='Ante/Post') 
                        i.edge('a0', 'a1',shape=str(dialog.combo_box_3.currentText()), fillcolor=str(dialog.combo_box.currentText()), style=str(dialog.combo_box_10.currentText()),arrowhead=str(dialog.combo_box_11.currentText()), arrowsize=str(dialog.combo_box_12.currentText()))
                        
                        i.node('a1', shape=str(dialog.combo_box_6.currentText()), fillcolor=str(dialog.combo_box_2.currentText()), style='filled', gradientangle='90',label='Negativ')
                        i.edge('a1', 'a2',shape=str(dialog.combo_box_8.currentText()), fillcolor=str(dialog.combo_box_2.currentText()), style=str(dialog.combo_box_15.currentText()),arrowhead=str(dialog.combo_box_14.currentText()), arrowsize=str(dialog.combo_box_16.currentText()))
                        
                        i.node('a2', shape=str(dialog.combo_box_18.currentText()), fillcolor=str(dialog.combo_box_17.currentText()), style='filled', gradientangle='1',label='Wie')
                        #i.node('node3', shape=str(dialog.combo_box_18.currentText()), fillcolor=str(dialog.combo_box_17.currentText()), style='filled', gradientangle='1')
                        i.edge('a2', 'a1',shape=str(dialog.combo_box_22.currentText()), fillcolor=str(dialog.combo_box_17.currentText()), style=str(dialog.combo_box_23.currentText()),arrowhead=str(dialog.combo_box_21.currentText()), arrowsize=str(dialog.combo_box_24.currentText()))
                    else:
                        i.node('a0', shape=str(dialog.combo_box_3.currentText()), fillcolor=str(dialog.combo_box.currentText()), style='filled', gradientangle='90',label='Ante/Post') 
                        i.edge('a0', 'a1',shape=str(dialog.combo_box_3.currentText()), fillcolor=str(dialog.combo_box.currentText()), style=str(dialog.combo_box_10.currentText()),arrowhead=str(dialog.combo_box_11.currentText()), arrowsize=str(dialog.combo_box_12.currentText()))
                        
                        i.node('a1', shape=str(dialog.combo_box_6.currentText()), fillcolor=str(dialog.combo_box_2.currentText()), style='filled', gradientangle='90',label='Negative')
                        i.edge('a1', 'a2',shape=str(dialog.combo_box_8.currentText()), fillcolor=str(dialog.combo_box_2.currentText()), style=str(dialog.combo_box_15.currentText()),arrowhead=str(dialog.combo_box_14.currentText()), arrowsize=str(dialog.combo_box_16.currentText()))
                        
                        i.node('a2', shape=str(dialog.combo_box_18.currentText()), fillcolor=str(dialog.combo_box_17.currentText()), style='filled', gradientangle='1',label='Same')
                        #i.node('node3', shape=str(dialog.combo_box_18.currentText()), fillcolor=str(dialog.combo_box_17.currentText()), style='filled', gradientangle='1')
                        i.edge('a2', 'a1',shape=str(dialog.combo_box_22.currentText()), fillcolor=str(dialog.combo_box_17.currentText()), style=str(dialog.combo_box_23.currentText()),arrowhead=str(dialog.combo_box_21.currentText()), arrowsize=str(dialog.combo_box_24.currentText()))
                    
        
        dt = datetime.datetime.now()
        matrix_path = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_Matrix_folder")
        filename = ('%s_%s_%s_%s_%s_%s_%s') % (
        'Harris_matrix', dt.day, dt.month, dt.year, dt.hour, dt.minute, dt.second)
        f = open(filename, "w")
        
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
        
        dialog = Setting_Matrix()
        
        dialog.exec_()
        
        
        G = Digraph(engine='dot',strict=False)
        G.attr(rankdir='TB')
        G.attr(compound='true')
        G.graph_attr['pad']="0.5"
        G.graph_attr['nodesep']="1"
        G.graph_attr['ranksep']="1.5"
        G.graph_attr['splines'] = 'ortho'
        # G.graph_attr['dpi'] = '50'
        
        elist1 = []
        elist2 = []
        elist3 = []
       
        if bool(dialog.checkBox_period.isChecked()):         
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
            
            e.node_attr['shape'] = str(dialog.combo_box_3.currentText())
            e.node_attr['style'] = str(dialog.combo_box_4.currentText())
            e.node_attr.update(style='filled', fillcolor=str(dialog.combo_box.currentText()))
            e.node_attr['color'] = 'black'    
            e.node_attr['penwidth'] = str(dialog.combo_box_5.currentText())
            e.edge_attr['penwidth'] = str(dialog.combo_box_5.currentText())
            e.edge_attr['style'] = str(dialog.combo_box_10.currentText())
            e.edge_attr.update(arrowhead=str(dialog.combo_box_11.currentText()), arrowsize=str(dialog.combo_box_12.currentText()))
            
            for cc in self.conteporene:
                a = (cc[0],cc[1])
                elist3.append(a)
        
            with G.subgraph(name='main1') as b:
                
                
                b.edges(elist3)
                
                b.node_attr['shape'] = str(dialog.combo_box_18.currentText())
                b.node_attr['style'] = str(dialog.combo_box_22.currentText())
                b.node_attr.update(style='filled', fillcolor=str(dialog.combo_box_17.currentText()))
                b.node_attr['color'] = 'black'    
                b.node_attr['penwidth'] = str(dialog.combo_box_19.currentText())
                b.edge_attr['penwidth'] = str(dialog.combo_box_19.currentText())
                b.edge_attr['style'] = str(dialog.combo_box_23.currentText())
                b.edge_attr.update(arrowhead=str(dialog.combo_box_21.currentText()), arrowsize=str(dialog.combo_box_24.currentText()))
                
            for dd in self.negative:
                a = (dd[0],dd[1])
                elist2.append(a)
        
            with G.subgraph(name='main2') as a:
                #a.attr(rank='same')
                a.edges(elist2)
                
                a.node_attr['shape'] = str(dialog.combo_box_6.currentText())
                a.node_attr['style'] = str(dialog.combo_box_8.currentText())
                a.node_attr.update(style='filled', fillcolor=str(dialog.combo_box_2.currentText()))
                a.node_attr['color'] = 'black'    
                a.node_attr['penwidth'] = str(dialog.combo_box_7.currentText())
                a.edge_attr['penwidth'] = str(dialog.combo_box_7.currentText())
                a.edge_attr['style'] = str(dialog.combo_box_15.currentText())
                a.edge_attr.update(arrowhead=str(dialog.combo_box_14.currentText()), arrowsize=str(dialog.combo_box_16.currentText()))    
                
            
        
        
        if bool(dialog.checkBox_legend.isChecked()):
            with G.subgraph(name='cluster3') as j:
                j.attr(rank='max')
                j.attr(fillcolor='white', label='Legend', fontcolor='black',fontsize='16',
                style='filled')
                with G.subgraph(name='cluster3') as i:
                    i.attr(rank='max')
                    if self.L=='it':
                        i.node('a0', shape=str(dialog.combo_box_3.currentText()), fillcolor=str(dialog.combo_box.currentText()), style='filled', gradientangle='90',label='Ante/Post') 
                        i.edge('a0', 'a1',shape=str(dialog.combo_box_3.currentText()), fillcolor=str(dialog.combo_box.currentText()), style=str(dialog.combo_box_10.currentText()),arrowhead=str(dialog.combo_box_11.currentText()), arrowsize=str(dialog.combo_box_12.currentText()))
                        
                        i.node('a1', shape=str(dialog.combo_box_6.currentText()), fillcolor=str(dialog.combo_box_2.currentText()), style='filled', gradientangle='90',label='Negative')
                        i.edge('a1', 'a2',shape=str(dialog.combo_box_8.currentText()), fillcolor=str(dialog.combo_box_2.currentText()), style=str(dialog.combo_box_15.currentText()),arrowhead=str(dialog.combo_box_14.currentText()), arrowsize=str(dialog.combo_box_16.currentText()))
                        
                        i.node('a2', shape=str(dialog.combo_box_18.currentText()), fillcolor=str(dialog.combo_box_17.currentText()), style='filled', gradientangle='1',label='Cont.')
                        # i.node('node3', shape=str(dialog.combo_box_18.currentText()), fillcolor=str(dialog.combo_box_17.currentText()), style='filled', gradientangle='1')
                        i.edge('a2', 'a1',shape=str(dialog.combo_box_22.currentText()), fillcolor=str(dialog.combo_box_17.currentText()), style=str(dialog.combo_box_23.currentText()),arrowhead=str(dialog.combo_box_21.currentText()), arrowsize=str(dialog.combo_box_24.currentText()))
                    elif self.L=='de':
                        i.node('a0', shape=str(dialog.combo_box_3.currentText()), fillcolor=str(dialog.combo_box.currentText()), style='filled', gradientangle='90',label='Ante/Post') 
                        i.edge('a0', 'a1',shape=str(dialog.combo_box_3.currentText()), fillcolor=str(dialog.combo_box.currentText()), style=str(dialog.combo_box_10.currentText()),arrowhead=str(dialog.combo_box_11.currentText()), arrowsize=str(dialog.combo_box_12.currentText()))
                        
                        i.node('a1', shape=str(dialog.combo_box_6.currentText()), fillcolor=str(dialog.combo_box_2.currentText()), style='filled', gradientangle='90',label='Negativ')
                        i.edge('a1', 'a2',shape=str(dialog.combo_box_8.currentText()), fillcolor=str(dialog.combo_box_2.currentText()), style=str(dialog.combo_box_15.currentText()),arrowhead=str(dialog.combo_box_14.currentText()), arrowsize=str(dialog.combo_box_16.currentText()))
                        
                        i.node('a2', shape=str(dialog.combo_box_18.currentText()), fillcolor=str(dialog.combo_box_17.currentText()), style='filled', gradientangle='1',label='Wie')
                        #i.node('node3', shape=str(dialog.combo_box_18.currentText()), fillcolor=str(dialog.combo_box_17.currentText()), style='filled', gradientangle='1')
                        i.edge('a2', 'a1',shape=str(dialog.combo_box_22.currentText()), fillcolor=str(dialog.combo_box_17.currentText()), style=str(dialog.combo_box_23.currentText()),arrowhead=str(dialog.combo_box_21.currentText()), arrowsize=str(dialog.combo_box_24.currentText()))
                    else:
                        i.node('a0', shape=str(dialog.combo_box_3.currentText()), fillcolor=str(dialog.combo_box.currentText()), style='filled', gradientangle='90',label='Ante/Post') 
                        i.edge('a0', 'a1',shape=str(dialog.combo_box_3.currentText()), fillcolor=str(dialog.combo_box.currentText()), style=str(dialog.combo_box_10.currentText()),arrowhead=str(dialog.combo_box_11.currentText()), arrowsize=str(dialog.combo_box_12.currentText()))
                        
                        i.node('a1', shape=str(dialog.combo_box_6.currentText()), fillcolor=str(dialog.combo_box_2.currentText()), style='filled', gradientangle='90',label='Negative')
                        i.edge('a1', 'a2',shape=str(dialog.combo_box_8.currentText()), fillcolor=str(dialog.combo_box_2.currentText()), style=str(dialog.combo_box_15.currentText()),arrowhead=str(dialog.combo_box_14.currentText()), arrowsize=str(dialog.combo_box_16.currentText()))
                        
                        i.node('a2', shape=str(dialog.combo_box_18.currentText()), fillcolor=str(dialog.combo_box_17.currentText()), style='filled', gradientangle='1',label='Same')
                        #i.node('node3', shape=str(dialog.combo_box_18.currentText()), fillcolor=str(dialog.combo_box_17.currentText()), style='filled', gradientangle='1')
                        i.edge('a2', 'a1',shape=str(dialog.combo_box_22.currentText()), fillcolor=str(dialog.combo_box_17.currentText()), style=str(dialog.combo_box_23.currentText()),arrowhead=str(dialog.combo_box_21.currentText()), arrowsize=str(dialog.combo_box_24.currentText()))
                    
        
        dt = datetime.datetime.now()
        matrix_path = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_Matrix_folder")
        filename = ('%s') % (
        'Harris_matrix2ED')
        f = open(filename, "w")
        
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
                             #startupinfo=si if Pyarchinit_OS_Utility.isWindows()else None)

        #tred_file = os.path.join(matrix_path, filename + '_graphml.dot')
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
        # f = Source.from_file(tred_file, format='png')
        # f.render()
        # g = Source.from_file(tred_file, format='jpg')
        # g.render()
        # return g,f
        # # return f
    
    def on_pushButton_graphml_pressed(self):
        provo= dottoxml, tred, graphml_file
        return provo