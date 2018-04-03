#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
/***************************************************************************
        pyArchInit Plugin  - A QGIS plugin to manage archaeological datatet
        					 stored in Postgres
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
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from modules.gui.sort_panel_ui import Ui_sortPanel


class SortPanelMain(QDialog, Ui_sortPanel):
	ITEMS = []
	TYPE_ORDER = ""
	def __init__(self, parent=None, db=None):
		QDialog.__init__(self, parent)
		self.setupUi(self)
		
	def on_pushButtonSort_pressed(self):
		self.ITEMS = []
		for index in range(self.FieldListsort.count()):
			self.ITEMS.append(self.FieldListsort.item(index).text())

    if self.radioButtonAsc.isChecked():
			self.TYPE_ORDER = "asc"
		else:
			self.TYPE_ORDER = "desc"

    if not bool(self.ITEMS):
			ttl = QString("Non è stato impostata alcun criterio. Vuoi uscire?")
			msg = QMessageBox.warning(self,'ATTENZIONE',ttl, QMessageBox.Cancel,1)
			if msg == 1:
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
		
		if len(all_items) >0:
			for item in all_items:
				self.FieldListsort.addItem(item)

	def insertItems(self, lv):
		self.FieldsList.insertItems(0,lv)
		

if __name__ == '__main__':
	import sys
	a = QApplication(sys.argv)
	dlg = SortPanelMain()
	dlg.show()
	sys.exit(a.exec_())
