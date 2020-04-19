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

import datetime
from datetime import date
from graphviz import Digraph, Source
from .pyarchinit_OS_utility import Pyarchinit_OS_Utility


class HarrisMatrix:
    HOME = os.environ['PYARCHINIT_HOME']

    def __init__(self, sequence, periodi):
        self.sequence = sequence
        self.periodi = periodi

    @property
    def export_matrix(self):
        G = Digraph(engine='neato', strict=False)
        G.graph_attr['splines'] = 'ortho'
        G.graph_attr['dpi'] = '300'
        elist = []

        for i in self.sequence:
            a = (i[0], i[1])
            elist.append(a)

        with G.subgraph(name='main') as d:
            d.edges(elist)
            d.node_attr['shape'] = 'box'
            d.node_attr['style'] = 'strocked'
            d.node_attr['color'] = 'red'
            d.attr(label='pyArchInit - Harris Matrix Export System')

        for i in self.periodi:
            with G.subgraph(name=i[1]) as c:
                # c.attr(bgcolor='lightgrey')
                for n in i[0]:
                    c.attr('node', shape='square', label=str(n), color='blue')
                    c.node(str(n))
                c.attr(color='blue')
                c.attr(label=i[2])
        dt = datetime.datetime.now()
        matrix_path = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_Matrix_folder")
        filename = ('%s_%s_%s_%s_%s_%s_%s') % (
        'Harris_matrix', dt.day, dt.month, dt.year, dt.hour, dt.minute, dt.second)
        f = open(filename, "w")

        G.format = 'xdot'
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
        g = Source.from_file(tred_file, format='svg')
        g.render()
        f = Source.from_file(tred_file, format='png')
        f.render()

        return g
