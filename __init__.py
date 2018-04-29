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

import sys

from .modules.utility.pyarchinit_folder_installation import pyarchinit_Folder_installation

sys.path.append(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ui'))
sys.path.insert(1, os.path.join(os.path.dirname(__file__), 'modules', 'gis'))
sys.path.insert(2, os.path.join(os.path.dirname(__file__), 'modules', 'db'))
sys.path.insert(3, os.path.join(os.path.dirname(__file__), 'modules', 'utility'))
sys.path.insert(4, os.path.join(os.path.dirname(__file__), 'tabs'))

fi = pyarchinit_Folder_installation()
fi.install_dir()


def classFactory(iface):
    from .pyarchinit_plugin import PyArchInitPlugin
    return PyArchInitPlugin(iface)
