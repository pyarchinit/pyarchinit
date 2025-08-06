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

from qgis.PyQt.QtCore import Qt, QEvent, QTimer
from qgis.PyQt.QtWidgets import QApplication, QDialog, QMessageBox, QItemDelegate, QComboBox, QListView, QToolTip, QAbstractItemView, QStyleOptionViewItem
from qgis.PyQt.QtGui import QCursor, QHelpEvent


class TooltipListView(QListView):
    """Custom ListView that properly shows tooltips"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        # Force the view to generate tooltip events
        self.viewport().setAttribute(Qt.WA_AlwaysShowToolTips, True)
        
    def viewportEvent(self, event):
        """Handle viewport events including tooltips"""
        if event.type() == QEvent.ToolTip:
            # Cast to QHelpEvent to get position
            help_event = event
            index = self.indexAt(help_event.pos())
            
            if index.isValid():
                # Get the item data
                item_text = self.model().data(index, Qt.DisplayRole)
                if item_text:
                    # Show tooltip
                    QToolTip.showText(help_event.globalPos(), str(item_text))
                    return True
            
            QToolTip.hideText()
            return True
            
        return super().viewportEvent(event)


class TooltipComboBox(QComboBox):
    """Custom ComboBox that shows tooltips for items in the dropdown"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # Use our custom list view
        self._tooltipView = TooltipListView(self)
        self.setView(self._tooltipView)
        # Enable tooltips on the combo box itself
        self.setToolTip("Click per aprire la lista")
        
    def addItem(self, text, userData=None):
        """Override to ensure we can add tooltips"""
        super().addItem(text, userData)
        # Set the tooltip role data to be the same as display text
        index = self.count() - 1
        self.setItemData(index, text, Qt.ToolTipRole)
        
    def showPopup(self):
        """Override to ensure view is properly configured when shown"""
        super().showPopup()
        # Force tooltip generation
        self.view().viewport().setAttribute(Qt.WA_AlwaysShowToolTips, True)


class ComboBoxDelegate(QItemDelegate):
    values = []
    editable = "False"

    def __init__(self, values=None, parent=None):
        QItemDelegate.__init__(self, parent)
        if values:
            self.values = values

    def def_values(self, values):
        self.values = values

    def def_editable(self, editable):
        self.editable = editable

    def createEditor(self, parent, option, index):
        # Use custom TooltipComboBox instead of regular QComboBox
        editor = TooltipComboBox(parent)
        
        # Add items - the TooltipComboBox.addItem method will handle tooltips
        for value in self.values:
            editor.addItem(value)
        
        # Set size adjust policy to show full content where possible
        editor.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        
        # Handle editable property
        if hasattr(self, 'editable') and self.editable != "":
            editor.setEditable(eval(self.editable))
        else:
            editor.setEditable(False)
            
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
