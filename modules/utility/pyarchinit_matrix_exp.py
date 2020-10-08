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
import datetime
from datetime import date
from graphviz import Digraph, Source
from .pyarchinit_OS_utility import Pyarchinit_OS_Utility
from ..db.pyarchinit_db_manager import Pyarchinit_db_management
from ...tabs.pyarchinit_setting_matrix import Setting_Matrix
class HarrisMatrix:
    HOME = os.environ['PYARCHINIT_HOME']
    DB_MANAGER = ""
    TABLE_NAME = 'us_table'
    MAPPER_TABLE_CLASS = "US"
    ID_TABLE = "id_us"
    MATRIX = ''
    
    def __init__(self, copre,riempie,taglia,si_appoggia_a,si_lega_a,gli_si_appoggia,riempito_da,coperto_da,tagliato_da, periodi):
        self.copre = copre
        self.riempie=riempie
        self.taglia = taglia
        self.si_appoggia_a=si_appoggia_a
        self.si_lega_a = si_lega_a
        self.gli_si_appoggia=gli_si_appoggia
        self.riempito_da=riempito_da
        self.coperto_da=coperto_da
        self.tagliato_da=tagliato_da
        self.periodi=periodi
        
    
    @property
    def export_matrix(self):
        
        self.MATRIX = Setting_Matrix()
        
        self.color_str = self.MATRIX.on_Ucolor(0)
        
        G = Digraph(engine='neato', strict=False)
        G.graph_attr['splines'] = 'ortho'
        G.graph_attr['dpi'] = '300'
        
        
        elist1 = []
        elist2 = []
        elist3 = []
        elist4 = []
        elist5 = []
        elist6 = []
        elist7 = []
        elist8 = []
        elist9 = []
        for i in self.copre:
            a = (i[0], i[1])
            elist1.append(a)
        
        with G.subgraph(name='main') as e:
           
            e.edges(elist1)
            
            e.node_attr['shape'] = 'square'
            e.node_attr['style'] = 'strocked'
            e.node_attr.update(style='filled', fillcolor='white')
            e.node_attr['color'] = 'red'    
            e.edge_attr['penwidth'] = '.5'
            e.edge_attr['style'] = 'solid'
            e.edge_attr.update(arrowhead='diamond', arrowsize='.7')
            
            
            
            
            for i in self.riempie:
                a = (i[0], i[1])
                elist2.append(a)
            with G.subgraph(name='main') as v:
                
                v.edges(elist2)
                
                v.node_attr['shape'] = 'square'
                v.node_attr['style'] = 'strocked'
                v.node_attr.update(style='filled', fillcolor='white')
                
                
                v.node_attr['color'] = 'black'
                v.edge_attr['penwidth'] = '.5'
                v.edge_attr['style'] = 'bold'      
                v.edge_attr.update(arrowhead='diamond', arrowsize='.8')    
            
            
            for i in self.taglia:
                a = (i[0], i[1])
                elist3.append(a)
            with G.subgraph(name='main') as t:
               
                t.edges(elist3)
                
                t.node_attr['shape'] = 'square'
                t.node_attr['style'] = 'strocked'
                t.node_attr.update(style='filled', fillcolor='white')
                
                
                t.node_attr['color'] = 'black'
                t.edge_attr['penwidth'] = '.5'
                t.edge_attr['style'] = 'dashed'      
                t.edge_attr.update(arrowhead='dot', arrowsize='.5') 
            
            
            for i in self.si_appoggia_a:
                a = (i[0], i[1])
                elist4.append(a)
            with G.subgraph(name='main') as s:
                
                s.edges(elist4)
                
                s.node_attr['shape'] = 'square'
                s.node_attr['style'] = 'strocked'
                s.node_attr.update(style='filled', fillcolor='white')
                
                
                s.node_attr['color'] = 'black'
                s.edge_attr['penwidth'] = '.5'
                s.edge_attr['style'] = 'strocked'      
                s.edge_attr.update(arrowhead='diamond', arrowsize='.5') 
            
            for i in self.si_lega_a:
                a = (i[0], i[1])
                elist5.append(a)
            with G.subgraph(name='main') as n:
                
                n.edges(elist5)
                
                n.node_attr['shape'] = 'square'
                n.node_attr['style'] = 'dotted'
                n.node_attr.update(style='filled', fillcolor='white')
                
                
                n.node_attr['color'] = 'black'
                n.edge_attr['penwidth'] = '.5'
                n.edge_attr['style'] = 'strocked'      
                n.edge_attr.update(arrowhead='tee', arrowsize='.8')    
            
            
            for i in self.gli_si_appoggia:
                a = (i[0], i[1])
                elist6.append(a)
            with G.subgraph(name='main') as m:
               
                m.edges(elist6)
                
                m.node_attr['shape'] = 'square'
                m.node_attr['style'] = 'strocked'
                m.node_attr.update(style='filled', fillcolor='white')
                
                
                m.node_attr['color'] = 'black'
                m.edge_attr['penwidth'] = '.5'
                m.edge_attr['style'] = 'strocked'      
                m.edge_attr.update(arrowhead='dot', arrowsize='.5') 
            
            
            for i in self.riempito_da:
                a = (i[0], i[1])
                elist7.append(a)
            with G.subgraph(name='main') as o:
                
                o.edges(elist7)
                
                o.node_attr['shape'] = 'square'
                o.node_attr['style'] = 'strocked'
                o.node_attr.update(style='filled', fillcolor='white')
                
                
                o.node_attr['color'] = 'black'
                o.edge_attr['penwidth'] = '.5'
                o.edge_attr['style'] = 'strocked'      
                o.edge_attr.update(arrowhead='inv', arrowsize='.5') 
        
        
            for i in self.coperto_da:
                a = (i[0], i[1])
                elist8.append(a)
            with G.subgraph(name='main') as x:
               
                x.edges(elist8)
                
                x.node_attr['shape'] = 'square'
                x.node_attr['style'] = 'strocked'
                x.node_attr.update(style='filled', fillcolor='white')
                
                
                x.node_attr['color'] = 'black'
                x.edge_attr['penwidth'] = '.5'
                x.edge_attr['style'] = 'bold'      
                x.edge_attr.update(arrowhead='inv', arrowsize='.5') 
            
            
            for i in self.tagliato_da:
                a = (i[0], i[1])
                elist9.append(a)
            with G.subgraph(name='main') as d:
                
                d.edges(elist9)
                
                d.node_attr['shape'] = 'square'
                d.node_attr['style'] = 'strocked'
                d.node_attr.update(style='filled', fillcolor='white')
                
                
                d.node_attr['color'] = 'black'
                d.edge_attr['penwidth'] = '.5'
                d.edge_attr['style'] = 'strocked'      
                d.edge_attr.update(arrowhead='inv', arrowsize='.5') 
    
        for i in self.periodi:
            with G.subgraph(name=i[1]) as c:
                
                for n in i[0]:
                    c.attr('node', shape='box', label =str(n))
                    
                    c.node(str(n))
                
                c.attr(color='blue')
                c.attr('node', shape='box', fillcolor='white', style='filled', gradientangle='90',label=i[2])
                
                c.node(i[2])
               
               
        
        dt = datetime.datetime.now()
        matrix_path = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_Matrix_folder")
        filename = ('%s_%s_%s_%s_%s_%s_%s') % (
        'Harris_matrix', dt.day, dt.month, dt.year, dt.hour, dt.minute, dt.second)
        f = open(filename, "w")
        
        G.format = 'xdot1.4'
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
        g = Source.from_file(tred_file, format='svgz')
        g.render()
        f = Source.from_file(tred_file, format='jpeg')
        f.render()
        #f.view()
        return g,f
        # return f