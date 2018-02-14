#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
/***************************************************************************
	pyArchInit Plugin  - A QGIS plugin to manage archaeological dataset
							 stored in Postgres
							 -------------------
	begin				 : 2007-12-01
	copyright			 : (C) 2008 by Luca Mandolesi
	email				 : mandoluca at gmail.com
 ***************************************************************************/

/***************************************************************************
 *																		   *
 *	 This program is free software; you can redistribute it and/or modify  *
 *	 it under the terms of the GNU General Public License as published by  *
 *	 the Free Software Foundation; either version 2 of the License, or	   *
 *	 (at your option) any later version.								   *
 *																		   *
 ***************************************************************************/
"""

import os
import shutil

class pyarchinit_OS_Utility:

	def create_dir(self, d):
		dirname = d

		try:
			os.makedirs(dirname)
			return 1
		except OSError:
			if os.path.exists(dirname):
				# We are nearly safe
				return 0 #la cartella esiste
			else:
				# There was an error on creation, so make sure we know about it
				raise

	def copy_file_img(self, f, d):
		file_path = f
		destination = d
		shutil.copy(file_path, destination)

	def copy_file(self, f, d):
		file_path = f
		destination = d
		if os.access(destination, 0) == True:
			return 0 #la cartella esiste
		else:
			try:
				shutil.copy(file_path, destination)
				return 1
			except OSError:
				if os.path.exists(destination):
					return 0
				else:
					raise