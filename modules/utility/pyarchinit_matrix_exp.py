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

from graphviz import Digraph


class HARRIS_MATRIX_EXP:
    HOME = os.environ['PYARCHINIT_HOME']

    def __init__(self, sequence, periodi):
        self.sequence = sequence
        self.periodi = periodi

    def export_matrix(self):
        G = Digraph(engine='dot')
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

        Matrix_path = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_Matrix_folder")
        filename = '{}{}{}'.format(Matrix_path, os.sep, 'Harris_matrix')

        G.format = 'svg'
        G.render(filename)
        G.format = 'png'
        G.render(filename)
        G.format = 'dot'
        G.render(filename)

        return G


if __name__ == "__main__":
    data = [(1, 2), (2, 4), ]
    Harris_matrix_exp = HARRIS_MATRIX_EXP(data)
    Harris_matrix_exp.export_matrix()