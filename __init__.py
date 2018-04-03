#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
/***************************************************************************
		pyArchInit Plugin  - A QGIS plugin to manage archaeological dataset
							 stored in Postgres
							 -------------------
	begin				: 2007-12-01
	copyright			: (C) 2010 by Luca Mandolesi
	email				: mandoluca at gmail.com
 ***************************************************************************/

/***************************************************************************
 *																		 *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or	 *
 *   (at your option) any later version.								   *
 *																		 *
 ***************************************************************************/
"""
# Use pdb for debugging


##def name():
##  return "pyArchinit Dev - Archeological GIS Tools"
##
##def description():
##  return "Under Testing - Use for testing only - PyArchInit it's tool to manage archaeological dataset - Only Windows 7 Tested"
##
##def version():
##  return "0.1.6"
##
##def plugin_type():
##  return QgisPlugin.UI # UI plugin
##
##def author_name():
##  return "Luca Mandolesi - pyarchinit@gmail.com"
##"""
##def qgisMinimumVersion():
## return "1.0"
##
##def qgisMaximumVersion():
##	return "2.99"
##"""
def classFactory(iface):
    from pyarchinit_plugin import PyArchInitPlugin
    return PyArchInitPlugin(iface)
