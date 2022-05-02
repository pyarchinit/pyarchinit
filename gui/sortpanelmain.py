#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
/***************************************************************************
        pyArchInit Plugin  - A QGIS plugin to manage archaeological datatet
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
from __future__ import absolute_import


from builtins import range
from qgis.PyQt.QtWidgets import QApplication, QDialog, QMessageBox
from qgis.PyQt.uic import loadUiType

import os

MAIN_DIALOG_CLASS, _ = loadUiType(os.path.join(os.path.dirname(__file__), 'ui', 'sortpanelmain.ui'))


class SortPanelMain(QDialog, MAIN_DIALOG_CLASS):
    TYPE_ORDER = ""

    def __init__(self, parent=None, db=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.ITEMS = []

    def closeEvent(self, event):
        if not self.ITEMS:
            self.ITEMS.append(self.FieldsList.item(0).text())

        self.deleteLater()
        QDialog.closeEvent(self, event)

    def on_pushButtonSort_pressed(self):
        for index in range(self.FieldListsort.count()):
            self.ITEMS.append(self.FieldListsort.item(index).text())

        if self.radioButtonAsc.isChecked():
            self.TYPE_ORDER = "asc"
        else:
            self.TYPE_ORDER = "desc"

        if not self.ITEMS:
            ttl = "Non è stato impostata alcun criterio. Vuoi uscire?"
            msg = QMessageBox.warning(self, 'ATTENZIONE', ttl, QMessageBox.Ok | QMessageBox.Cancel)
            if msg == QMessageBox.Ok:
                self.close()
            else:
                pass
        else:
            self.close()

    def on_pushButtonRight_pressed(self):
        all_items = []

        for index in range(self.FieldsList.count()):
            all_items.append(self.FieldsList.item(index).text())

        item_selected = self.FieldsList.selectedItems()

        all_items.remove(item_selected[0].text())
        try:
            all_items.remove('')
        except:
            pass
        self.FieldListsort.addItem(item_selected[0].text())

        self.FieldsList.clear()

        for item in all_items:
            self.FieldsList.addItem(item)

    def on_pushButtonLeft_pressed(self):
        all_items = []

        for index in range(self.FieldListsort.count()):
            all_items.append(self.FieldListsort.item(index).text())

        item_selected = self.FieldListsort.selectedItems()
        try:
            all_items.remove(item_selected[0].text())
        except:
            pass
        self.FieldsList.addItem(item_selected[0].text())

        self.FieldListsort.clear()

        if len(all_items) > 0:
            for item in all_items:
                self.FieldListsort.addItem(item)

    def insertItems(self, lv):
        self.FieldsList.insertItems(0, lv)


if __name__ == '__main__':
    import sys

    a = QApplication(sys.argv)
    dlg = SortPanelMain()
    dlg.show()
    sys.exit(a.exec_())
