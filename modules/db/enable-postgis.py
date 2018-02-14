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
#from settings import *
import os
from sqlalchemy import *
import psycopg2
from psycopg2 import *
from psycopg2.extensions import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *
#settings = Settings()
db_engine = "postgres"

if db_engine == "sqlite":
	current_path = os.path.dirname(os.path.abspath(__file__))
	db_file = os.path.join(current_path, 'pyarchinit.db')
	dsn = 'sqlite:///'+db_file
	db = create_engine(dsn)
	import pyarchinit_db_structure

elif db_engine == "postgres":
	engine = create_engine("postgres://postgres:@127.0.0.1:5432/postgres")
	engine.raw_connection().set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
	engine.text("CREATE DATABASE %s ENCODING = 'utf8'" % 'pippo').execute()
	os.system('/usr/local/pgsql/bin/createlang plpgsql pippo')
	os.system('/usr/local/bin/psql -d pippo -f  "/usr/local/pgsql/share/contrib/lwpostgis.sql"')
	os.system('/usr/local/bin/psql -d pippo -f  "/usr/local/pgsql/share/contrib/spatial_ref_sys.sql"')
	import pyarchinit_db_structure