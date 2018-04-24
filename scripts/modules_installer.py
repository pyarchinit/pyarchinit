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
 *   (at your option) any later version.                                   *																		*
 ***************************************************************************/
"""

import subprocess

import sys

# Adding the dependencies python modules in
# package list in order to install via pip module
packages = ['pyper',
            'sqlalchemy',
            'graphviz',
            'reportlab']

for p in packages:
    if p.startswith('graphviz'):
        try:
            subprocess.call(['dot', '-V'])
        except Exception as e:
            print('INFO: It seems that Graphviz is not installed on your system, ')
            print('INFO: anyway the graphviz python module will be installed on your system, ')
            print('INFO: but the export matrix functionality from pyarchinit plugin will be disabled.')
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', p], shell=False)
