#!/usr/bin/env python3
"""
/***************************************************************************
    pyArchInit Plugin  - A QGIS plugin to manage archaeological dataset
    stored in Postgres
    -------------------
    begin                : 2018-04-22
    copyright            : (C) 2008 by Salvatore Larosa
    email                : lrssvtml (at) gmail (dot) com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *                                                                        *
 ***************************************************************************/
"""

import subprocess

import sys

packages = sys.argv[1].split(',') if len(sys.argv) >= 2 else []

# Adding the dependencies python modules in
# package list in order to install via pip module

      
if not packages:
    packages = ['PypeR',
                'SQLAlchemy',
                'SQLAlchemy-Utils',
 
                'graphviz==0.8.3',

                'reportlab',
                'networkx',
                'matplotlib',
                'graphviz-0.8.3',
                ]

for p in packages:
    if p.startswith('graphviz==0.8.3'):
        try:
            subprocess.call(['dot', '-V'])
        except Exception as e:
            print('INFO: It seems that Graphviz is not installed on your system, ')
            print('INFO: anyway the graphviz python module will be installed on your system, ')
            print('INFO: but the export matrix functionality from pyarchinit plugin will be disabled.')
    if p.startswith('PypeR'):
        try:
            subprocess.call(['Rcmd'])
        except Exception as e:
            print('INFO: It seems that R is not installed on your system, ')
            print('INFO: anyway the pyper module will be installed on your system, ')
            print('INFO: but you can not use archaezoology function.')
    subprocess.check_call([sys.executable, '-m', 'pip' ,'install','--upgrade', p], shell=False)
