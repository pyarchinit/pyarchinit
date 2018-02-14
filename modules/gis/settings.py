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

import os, sys
class Settings:
	SERVER = ""
	HOST = ""
	DATABASE = ""
	PASSWORD = ""
	PORT = ""
	USER = ""
	THUMB_PATH = ""
	
	def __init__(self, s):
		self.configuration = eval(s)
	
	def set_configuration(self):
		self.SERVER = self.configuration['SERVER']
		self.HOST = self.configuration['HOST']
		self.DATABASE = self.configuration['DATABASE']
		self.PASSWORD = self.configuration['PASSWORD']
		self.PORT = self.configuration['PORT']
		self.USER = self.configuration['USER']
		self.THUMB_PATH = self.configuration['THUMB_PATH']

		PLUGIN_PATH = path = os.path.dirname(__file__)
