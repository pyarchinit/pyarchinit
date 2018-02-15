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
class Error_check:

	def data_is_empty(self, d):
		if bool(d) == False:
			return 0
		else:
			return 1

	def data_is_int(self, d):
		try:
			int(d)
		except:
			return 0
		else:
			return 1

	def data_lenght(self, d, l):
		if len(d) > l:
			return 0
		else:
			return 1