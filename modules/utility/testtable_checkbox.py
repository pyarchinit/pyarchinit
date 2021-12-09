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

from __future__ import print_function

from builtins import range
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QApplication


class Window(QWidget):
    def __init__(self, rows, columns):
        QWidget.__init__(self)
        self.table = QTableWidget(rows, columns, self)
        for column in range(columns):
            for row in range(rows):
                item = QTableWidgetItem('Text%d' % row)
                if row % 2:
                    item.setFlags(Qt.ItemIsUserCheckable |
                                  Qt.ItemIsEnabled)
                    item.setCheckState(Qt.Unchecked)
                self.table.setItem(row, column, item)
        self.table.itemClicked.connect(self.handleItemClicked)
        layout = QVBoxLayout(self)
        layout.addWidget(self.table)
        self._list = []

    def handleItemClicked(self, item):
        if item.checkState() == Qt.Checked:
            print(('"%s" Checked' % item.text()))
            self._list.append(item.row())
            print(self._list)
        else:
            print('"%s" Clicked' % item.text())


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    window = Window(6, 3)
    window.resize(350, 300)
    window.show()
    sys.exit(app.exec_())
