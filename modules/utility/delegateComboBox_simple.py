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
from qgis.PyQt.QtWidgets import QItemDelegate, QComboBox


class ComboBoxDelegate(QItemDelegate):
    """Simple ComboBox delegate with built-in tooltip support"""
    
    def __init__(self, values=None, parent=None):
        QItemDelegate.__init__(self, parent)
        self.values = values if values else []
        self.editable = "False"

    def def_values(self, values):
        self.values = values

    def def_editable(self, editable):
        self.editable = editable

    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        
        # Add all items
        for value in self.values:
            editor.addItem(value)
        
        # Set combo box properties for better display
        editor.setMaxVisibleItems(10)  # Show more items at once
        editor.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        
        # Set a tooltip on the combo box itself that shows current value
        editor.setToolTip("Valore corrente: " + editor.currentText())
        
        # Update tooltip when selection changes
        editor.currentTextChanged.connect(lambda text: editor.setToolTip("Valore corrente: " + text))
        
        # Handle editable property
        if hasattr(self, 'editable') and self.editable != "":
            editor.setEditable(eval(self.editable))
        else:
            editor.setEditable(False)
            
        return editor

    def setEditorData(self, editor, index):
        text = index.model().data(index, Qt.DisplayRole)
        i = editor.findText(text)
        if i == -1:
            i = 0
        editor.setCurrentIndex(i)
        editor.setToolTip("Valore corrente: " + editor.currentText())

    def setModelData(self, editor, model, index):
        model.setData(index, editor.currentText())