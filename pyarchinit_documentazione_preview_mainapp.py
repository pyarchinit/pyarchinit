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
import sys, os
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import PyQt4.QtGui
try:
	from qgis.core import *
	from qgis.gui import *
except:
	pass

from datetime import date
from psycopg2 import *



#--import pyArchInit modules--#
#from  pyarchinit_inventario_reperti_ui import Ui_DialogInventarioMateriali
from  pyarchinit_utility import *
from  pyarchinit_error_check import *


try:
	from  pyarchinit_db_manager import *
except:
	pass

from  pyarchinit_pyqgis import Pyarchinit_pyqgis

from pyarchinit_preview_doc_gui import Ui_DialogPreviewDoc

class pyarchinit_doc_preview(QDialog, Ui_DialogPreviewDoc):
	MSG_BOX_TITLE = "pyArchInit - Scheda Sistema Preview Documentazione"
	DB_MANAGER = ""
	DATA_LIST = ""
	ID_US_DICT = {}
	mapPreview = ""
	DOC_STR  = ""
	vlayer = ""
	layerToSet = ""

	if os.name == 'posix':
		HOME = os.environ['HOME']
	elif os.name == 'nt':
		HOME = os.environ['HOMEPATH']
	
	QUANT_PATH = ('%s%s%s') % (HOME, os.sep, "pyarchinit_Quantificazioni_folder")

	def __init__(self, iface, docstr):
		self.iface = iface
		self.pyQGIS = Pyarchinit_pyqgis(self.iface)
		self.DOC_STR = docstr

##		self.ID_US_DICT = id_us_dict
		QDialog.__init__(self)
		self.setupUi(self)

		self.mapPreview = QgsMapCanvas(self)
		self.mapPreview.setCanvasColor(QColor(255,255,255))
		self.gridLayout_2.addWidget(self.mapPreview, 0, 0, 1, 1)
		self.gridLayout.addWidget(self.widgetPreviewDoc, 0, 0, 1, 1)
		self.draw_preview()

##		self.textbox.setText('1 2 3 4')
		#self.on_draw()
		try:
			self.DB_connect()
		except:
			pass

	def DB_connect(self):
		from pyarchinit_conn_strings import *
		conn = Connection()
		conn_str = conn.conn_str()

		try:
			self.DB_MANAGER = Pyarchinit_db_management(conn_str)
			self.DB_MANAGER.connection()
		except Exception as e:
			e = str(e)
			QMessageBox.warning(self, "Alert", "Attenzione rilevato bug! Segnalarlo allo sviluppatore <br> Errore: <br>" + str(e) ,  QMessageBox.Ok)

	def draw_preview(self):
		#self.pyQGIS.charge_vector_layers_doc(draw_preview)
##		if mode == 0:
		self.layerToSet = self.pyQGIS.loadMapPreviewDoc(self.DOC_STR)
		self.vlayer = self.layerToSet[0].layer()

		#self.mapPreview.setLayerSet(self.layerToSet)
		self.mapPreview.setLayerSet(self.vlayer)
		self.mapPreview.zoomToFullExtent()
		#extention = self.vlayer.extent()

		#self.mapPreview.zoomToFullExtent()

		#self.vlayer.selectAll()
		#self.mapPreview.setExtent(extention)
		#self.mapPreview.zoomToSelected()

		QMessageBox.warning(self, "layer to set", str(self.layerToSet), QMessageBox.Ok)

##
##		self.vlayer.removeSelection()
##		self.mapPreview.zoomToFullExtent()
##		elif mode == 1:
##			self.mapPreview.setLayerSet( [ ] )
##			self.mapPreview.zoomToFullExtent()

	def testing(self, name_file, message):
		f = open(str(name_file), 'w')
		f.write(str(message))
		f.close()

## Class end
