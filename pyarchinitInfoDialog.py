#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
/***************************************************************************
        pyArchInit Plugin  - A QGIS plugin to manage archaeological dataset
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

from info import Ui_DialogInfo
from info import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys, os


class pyArchInitDialog_Info(QDialog, Ui_DialogInfo):
	def __init__(self, parent=None, db=None):
		QDialog.__init__(self, parent)
		# Set up the user interface from Designer.
		self.setupUi(self)



if __name__ == '__main__':
	import sys
	app = QApplication(sys.argv)
	ui = pyArchInitDialog_Info()
	ui.show()
	sys.exit(app.exec_())