#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
/***************************************************************************
        pyArchInit Plugin  - A QGIS plugin to manage archaeological dataset
        					 stored in Postgres
                             -------------------
    begin                : 2007-12-01
    copyright            : (C) 2008 by Luca Mandolesi; Enzo Cocca <enzo.ccc@gmail.com>
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

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QApplication, QDialog, QMessageBox, QItemDelegate, QComboBox


class ComboBoxDelegate(QItemDelegate):
    values = ""
    editable = ""

    def __init__(self, parent=None):
        QItemDelegate.__init__(self, parent)

    def def_values(self, values):
        self.values = values

    def def_editable(self, editable):
        self.editable = editable

    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        editor.addItems(self.values)
        editor.setEditable(eval(self.editable))
        return editor

    def setEditorData(self, editor, index):
        text = index.model().data(index, Qt.DisplayRole)  # .String()
        i = editor.findText(text)
        if i == -1:
            i = 0
        editor.setCurrentIndex(i)

    def setModelData(self, editor, model, index):
        # model.setData(index, QtCore.QVariant(editor.currentText() ))
        model.setData(index, editor.currentText())
