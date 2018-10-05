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
import os

from builtins import object

from ..utility.settings import Settings


class Connection(object):
    HOME = os.environ['PYARCHINIT_HOME']

    def conn_str(self):
        cfg_rel_path = os.path.join(os.sep, 'pyarchinit_DB_folder', 'config.cfg')
        file_path = '{}{}'.format(self.HOME, cfg_rel_path)
        conf = open(file_path, "r")

        data = conf.read()
        settings = Settings(data)
        settings.set_configuration()
        conf.close()

        conn_str_dict = {"server": settings.SERVER,
                         "user": settings.USER,
                         "host": settings.HOST,
                         "port": settings.PORT,
                         "db_name": settings.DATABASE,
                         "password": settings.PASSWORD}

        if conn_str_dict["server"] == 'postgres':
            try:
                conn_str = "%s://%s:%s@%s:%s/%s%s?charset=utf8" % (
                "postgresql", conn_str_dict["user"], conn_str_dict["password"], conn_str_dict["host"],
                conn_str_dict["port"], conn_str_dict["db_name"], "?sslmode=allow")
            except:
                conn_str = "%s://%s:%s@%s:%d/%s" % (
                "postgresql", conn_str_dict["user"], conn_str_dict["password"], conn_str_dict["host"],
                conn_str_dict["port"], conn_str_dict["db_name"])
        elif conn_str_dict["server"] == 'sqlite':
            sqlite_DB_path = '{}{}{}'.format(self.HOME, os.sep,
                                           "pyarchinit_DB_folder")

            dbname_abs = sqlite_DB_path + os.sep + conn_str_dict["db_name"]

            conn_str = "%s:///%s" % (conn_str_dict["server"], dbname_abs)

        return conn_str

    def thumb_path(self):
        cfg_rel_path = os.path.join(os.sep, 'pyarchinit_DB_folder', 'config.cfg')
        file_path = '{}{}'.format(self.HOME, cfg_rel_path)
        conf = open(file_path, "r")

        data = conf.read()
        settings = Settings(data)
        settings.set_configuration()
        conf.close()
        thumb_path = {"thumb_path": settings.THUMB_PATH}

        return thumb_path
