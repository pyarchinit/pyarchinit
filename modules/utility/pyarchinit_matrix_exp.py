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

from graphviz import Digraph, Source
from .pyarchinit_OS_utility import Pyarchinit_OS_Utility


class HARRIS_MATRIX_EXP:
    HOME = os.environ['PYARCHINIT_HOME']

    def __init__(self, sequence, periodi):
        self.sequence = sequence
        self.periodi = periodi

    def export_matrix(self):
        G = Digraph(engine='dot', strict=True)
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

        matrix_path = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_Matrix_folder")
        filename = '{}{}{}'.format(matrix_path, os.sep, 'Harris_matrix')

        G.format = 'dot'
        dot_file = G.render(filename, cleanup=True)

        # For MS-Windows, we need to hide the console window.
        if Pyarchinit_OS_Utility.isWindows():
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = subprocess.SW_HIDE

        with open(filename + '_tred.dot', "wb") as out, \
                open(matrix_path + '/matrix_error.txt', "wb") as err:
            subprocess.Popen(['tred', dot_file],
                             stdout=out,
                             stderr=err)
                             # startupinfo=si if Pyarchinit_OS_Utility.isWindows() else None)

        g = Source.from_file(filename + '_tred.dot')
        g.format = 'svg'
        g.render(filename, cleanup=True)
        g.format = 'png'
        g.render(filename, cleanup=True)

        return g


if __name__ == "__main__":
    data = [(1, 2), (2, 4), ]
    Harris_matrix_exp = HARRIS_MATRIX_EXP(data)
    Harris_matrix_exp.export_matrix()
