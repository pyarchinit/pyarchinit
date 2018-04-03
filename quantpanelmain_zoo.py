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
from PyQt4 import QtCore
from PyQt4 import QtGui
from modules.gui.quant_panel_ui_zoo import Ui_quantPanel_zoo
from sortpanelmain import SortPanelMain


class QuantPanelMain(QDialog, Ui_quantPanel_zoo):
	ITEMS = []
	TYPE_QUANT = ""
	def __init__(self, parent=None, db=None):
		QDialog.__init__(self, parent)
		self.setupUi(self)
		
	def on_calcola1_pressed(self):
		
		self.ITEMS = []
			
		if self.radioButtonUsMin.isChecked() == True:
			self.TYPE_QUANT = "US"
		
		else:
			self.close()
			
		if self.psill.text() == "":
			psill = ''
		else:
			psill = int(self.psill.text())

		if self.model.currentText() == "":
			model = ''
		else:
			model = str(self.model.currentText())

		if self.rang.text() == "":
			rang = ''
		else:
			rang = int(self.rang.text())
				
				
if __name__ == '__main__':
	import sys
	a = QApplication(sys.argv)
	dlg = SortPanelMain()
	dlg.show()
	sys.exit(a.exec_())
