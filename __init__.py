#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
/***************************************************************************
        pyArchInit Plugin  - A QGIS plugin to manage archaeological dataset
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
import re

import sys

from .modules.utility.pyarchinit_folder_installation import pyarchinit_Folder_installation

sys.path.append(os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'resources')))
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'gui', 'ui')))

fi = pyarchinit_Folder_installation()
fi.install_dir()

missing_libraries = []
try:
    import pyper
except Exception as e:
    missing_libraries.append(str(e))

try:
    import graphviz
except Exception as e:
    missing_libraries.append(str(e))

try:
    import sqlalchemy
except Exception as e:
    missing_libraries.append(str(e))

try:
    import reportlab
except Exception as e:
    missing_libraries.append(str(e))

try:
    import matplotlib
except Exception as e:
    missing_libraries.append(str(e))

try:
    import networkx
except Exception as e:
    missing_libraries.append(str(e))

install_libraries = []
for l in missing_libraries:
    p = re.findall(r"'(.*?)'", l)
    install_libraries.append(p[0])

if install_libraries:
    from qgis.PyQt.QtWidgets import QMessageBox

    res = QMessageBox.warning(None, 'PyArchInit', "Some of the required packages are missing from your machine:\n{}\n\n"
                                                  "Do you want install the missing packages?".format(
        ',\n'.join(missing_libraries)), QMessageBox.Ok | QMessageBox.Cancel)
    if res == QMessageBox.Ok:
        import subprocess

        cmd = 'python3'
        subprocess.call(['{}'.format(os.path.join(os.path.dirname(__file__), 'scripts', 'modules_installer.py')),
                         ','.join(install_libraries)])
    else:
        pass


def classFactory(iface):
    from .pyarchinitPlugin import PyArchInitPlugin
    return PyArchInitPlugin(iface)
