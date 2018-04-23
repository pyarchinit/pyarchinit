# -*- coding: utf 8 -*-
"""
/***************************************************************************
    pyArchInit Plugin  - A QGIS plugin to manage archaeological dataset
    stored in Postgres
                             -------------------
    begin                : 2007-12-01
    copyright            : (C) 2008 by Salvatore Larosa
    email                : lrssvtml (at) gmail (dot) com
 ***************************************************************************/

/***************************************************************************
 *                                                                         	*
 *   This program is free software; you can redistribute it and/or modify 	*
 *   it under the terms of the GNU General Public License as published by  	*
 *   the Free Software Foundation; either version 2 of the License, or    	*
 *   (at your option) any later version.                                  	*																		*
 ***************************************************************************/
"""

import subprocess
import sys

# Add the dependencies in package list in order to install via pip module
packages = ['networkx',
            'pyper',
            'pygraphviz==1.4rc1']

for p in packages:
    if p.startswith('pygraphviz'):
        try:
            subprocess.call(['dot', '-V'])
        except Exception as e:
            print('ERROR: Is Graphviz installed on your system?')
            print('ERROR: pygraphviz cannot be installed, install Graphviz and try again.')
            break
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', p], shell=False)
