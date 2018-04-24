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
import os

from graphviz import Digraph


class HARRIS_MATRIX_EXP:
    HOME = os.environ['PYARCHINIT_HOME']

    def __init__(self, sequence, periodi):
        self.sequence = sequence
        self.periodi = periodi

    def export_matrix(self):
        G = Digraph()
        # G.directed = True
        # G.attr(dpi=300)
        # G.attr(label='pyArchInit - Harris Matrix Export System')

        elist = []

        for i in self.sequence:
            a = (i[0], i[1])
            elist.append(a)

        G.edges(elist)

        G.node_attr['shape'] = 'box'
        G.node_attr['style'] = 'strocked'
        G.node_attr['color'] = 'red'

        with G.subgraph() as c:
            for i in self.periodi:
                c.attr(name=i[1])
                c.attr(style='strocked')
                c.attr(shape='square')
                c.attr(color='blue')
                c.attr(label=i[2])
                c.attr(font_color='Blue')

        try:
            data_to_plot = G.tred()
        except:
            data_to_plot = G

        Matrix_path = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_Matrix_folder")

        filename_svg = '{}{}{}'.format(Matrix_path, os.sep, 'Harris_matrix.svg')
        filename_png = '{}{}{}'.format(Matrix_path, os.sep, 'Harris_matrix.png')
        filename_dot = '{}{}{}'.format(Matrix_path, os.sep, 'Harris_matrix_win.dot')

        G.format = 'svg'
        G.render(filename_svg)
        G.format = 'png'
        G.render(filename_png)
        G.format = 'dot'
        G.render(filename_dot)

        return data_to_plot


if __name__ == "__main__":
    data = [(1, 2), (2, 4), ]
    Harris_matrix_exp = HARRIS_MATRIX_EXP(data)
    Harris_matrix_exp.export_matrix()