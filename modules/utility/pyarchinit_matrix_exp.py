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
    
    def __init__(self, sequence,negative, periodi):
        self.sequence = sequence
        self.negative = negative
        self.periodi=periodi
        
    
    @property
    def export_matrix(self):
        
        self.MATRIX = Setting_Matrix()
        
        self.color_str = self.MATRIX.on_Ucolor(0)
        
        G = Digraph(engine='neato',strict=False)
        
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
        for i in self.sequence:
            a = (i[0], i[1])
            elist1.append(a)
        
        with G.subgraph(name='main') as e:
           
            e.edges(elist1)
            
            e.node_attr['shape'] = 'square'
            e.node_attr['style'] = 'strocked'
            e.node_attr.update(style='filled', fillcolor='white')
            e.node_attr['color'] = 'black'    
            e.node_attr['penwidth'] = '.5'
            e.edge_attr['penwidth'] = '.5'
            e.edge_attr['style'] = 'solid'
            e.edge_attr.update(arrowhead='diamond', arrowsize='.7')
            for i in self.negative:
                a = (i[0], i[1])
                elist2.append(a)
            
        with G.subgraph(name='main2') as a:
           
            a.edges(elist2)
            
            a.node_attr['shape'] = 'square'
            a.node_attr['style'] = 'strocked'
            a.node_attr.update(style='filled', fillcolor='gray')
            a.node_attr['color'] = 'red'    
            a.node_attr['penwidth'] = '.5'
            a.edge_attr['penwidth'] = '.5'
            a.edge_attr['style'] = 'dashed'
            a.edge_attr.update(arrowhead='inv', arrowsize='.8')    
        
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