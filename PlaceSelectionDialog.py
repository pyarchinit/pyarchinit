#! /usr/bin/env python
# -*- coding: utf 8 -*-
"""
/***************************************************************************
        pyArchInit Plugin  - A QGIS plugin to manage archaeological dataset
                             stored in Postgres
                             -------------------
    begin                : 2021-12-01
    copyright            : (C) 2021 by Enzo Cocca <enzo.ccc@gmail.com>
    email                : mandoluca at gmail.com
 ***************************************************************************/
/***************************************************************************
 *                                                                          *
 *   This program is free software; you can redistribute it and/or modify   *
 *   it under the terms of the GNU General Public License as published by   *
 *   the Free Software Foundation; either version 2 of the License, or      *
 *   (at your option) any later version.                                    *                                                                       *
 ***************************************************************************/
"""


import os
from qgis.PyQt.QtWidgets import QDialog
from qgis.PyQt import uic

# create the dialog for GeoCoding
class PlaceSelectionDialog(QDialog):

  def __init__(self):
    super(PlaceSelectionDialog, self).__init__()
    uic.loadUi(os.path.join(os.path.dirname(__file__), 'gui', 'ui', 'Ui_PlaceSelection.ui'), self)
