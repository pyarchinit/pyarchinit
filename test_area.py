#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
/***************************************************************************
        pyArchInit Plugin  - A QGIS plugin to manage archaeological dataset
        					 stored in Postgres
                             -------------------
    begin                : 2007-12-01
    copyright            : (C) 2010 by Luca Mandolesi
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
import os

#mettete qua i vostri import
#import qrcode

##from PyQt4.QtCore import *
##from PyQt4.QtGui import *
import PyQt4.QtGui
##from PyQt4 import QtGui, QtCore

from qgis.core import *
from qgis.gui import *

from settings import *

class Test_area:
	if os.name == 'posix':
		HOME = os.environ['HOME']
	elif os.name == 'nt':
		HOME = os.environ['HOMEPATH']

	REPORT_PATH = ('%s%s%s') % (HOME, os.sep, "pyarchinit_Test_folder")

	def __init__(self, data):
		self.data = data

##	def run_test(self):
##		#Inserire qui la propria funzione
##		cfg_rel_path = os.path.join(os.sep,'pyarchinit_DB_folder', 'config.cfg')
##		file_path = ('%s%s') % (self.HOME, cfg_rel_path)
##		conf = open(file_path, "r")
##		con_sett = conf.read()
##		conf.close()
##
##		settings = Settings(con_sett)
##		settings.set_configuration()
##		
##		if settings.SERVER == 'sqlite':
##			sqliteDB_path = os.path.join(os.sep,'pyarchinit_DB_folder', 'pyarchinit_db.sqlite')
##			db_file_path = ('%s%s') % (self.HOME, sqliteDB_path)
##
##			gidstr =  "sito = '" + str(self.data[0]) +"'"
##			if len(self.data) > 1:
##				for i in range(len(self.data)):
##					gidstr += " OR sito = '" + str(self.data[0]) +"'"
##
##			uri = QgsDataSourceURI()
##			uri.setDatabase(db_file_path)
##
##			uri.setDataSource('','pyarchinit_sito_view', 'the_geom', gidstr, "ROWID")
##			layerSito=QgsVectorLayer(uri.uri(), 'pyarchinit_sito_view', 'spatialite')
##			if  layerSito.isValid() == True:
##				#style_path = ('%s%s') % (self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
##				#layerUS.loadNamedStyle(style_path)
##				QgsMapLayerRegistry.instance().addMapLayers([layerSito], True)

	def run_test(self):
		pass
		#Inserire qui la propria funzione
##		qr = qrcode.QRCode(
##			version=1,
##			error_correction=qrcode.constants.ERROR_CORRECT_L,
##			box_size=10,
##			border=4,
##		)
##		qr.add_data(str(self.data))
##		qr.make(fit=True)
##
##		img = qr.make_image()
##		file_path = self.REPORT_PATH + '/pyarchinit_qrcode.png'
##		img.save(file_path)
