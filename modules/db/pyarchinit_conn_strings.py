# -*- coding: utf-8 -*-
"""
/***************************************************************************
        pyArchInit Plugin  - A QGIS plugin to manage archaeological dataset
                             stored in Postgres
                             -------------------
    begin                : 2007-12-01
    copyright            : (C) 2008 by Luca Mandolesi; Enzo Cocca <enzo.ccc@gmail.com>
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
import datetime
import traceback as tb

from ..utility.settings import Settings
from ..utility.pyarchinit_OS_utility import Pyarchinit_OS_Utility
from qgis.PyQt.QtWidgets import QDialog, QMessageBox


class PyArchInitConnLogger:
    """Simple file logger for connection operations"""
    def __init__(self):
        self.log_file = '/Users/enzo/pyarchinit_conn_debug.log'

    def log(self, message):
        """Write a log message with timestamp"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] {message}\n")
                f.flush()
        except Exception:
            pass  # Silently fail if logging doesn't work

    def log_exception(self, exc, context=""):
        """Log an exception with traceback"""
        self.log(f"EXCEPTION in {context}: {type(exc).__name__}: {str(exc)}")
        traceback = tb.format_exc()
        for line in traceback.split('\n'):
            if line:
                self.log(f"  {line}")

class Connection(object):
    HOME = os.environ['PYARCHINIT_HOME']
    RESOURCES_PATH = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'resources')

    OS_UTILITY = Pyarchinit_OS_Utility()

    def __init__(self):
        self.logger = PyArchInitConnLogger()
    
    def conn_str(self):
        self.logger.log("\n=== Connection.conn_str called ===")

        # Log stack trace to see where this is being called from
        stack = tb.format_stack()
        self.logger.log("Call stack:")
        for i, frame in enumerate(stack[-5:-1]):
            self.logger.log(f"  Frame {i}: {frame.strip()}")

        cfg_rel_path = os.path.join(os.sep, 'pyarchinit_DB_folder', 'config.cfg')
        file_path = '{}{}'.format(self.HOME, cfg_rel_path)
        self.logger.log(f"Config file path: {file_path}")

        try:
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
                         "password": settings.PASSWORD,
                         "sslmode": getattr(settings, 'SSLMODE', 'allow')}

            # Log connection parameters (mask password)
            self.logger.log(f"Server type: {conn_str_dict['server']}")
            self.logger.log(f"User: {conn_str_dict['user']}")
            self.logger.log(f"Host: {conn_str_dict['host']}")
            self.logger.log(f"Port: {conn_str_dict['port']}")
            self.logger.log(f"Database: {conn_str_dict['db_name']}")
            self.logger.log(f"SSL Mode: {conn_str_dict['sslmode']}")

            if conn_str_dict["server"] == 'postgres':
                sslmode = conn_str_dict.get("sslmode", "allow")
                try:
                    conn_str = "%s://%s:%s@%s:%s/%s?sslmode=%s" % (
                    "postgresql", conn_str_dict["user"], conn_str_dict["password"], conn_str_dict["host"],
                    conn_str_dict["port"], conn_str_dict["db_name"], sslmode)
                    # Log masked connection string
                    masked_str = "%s://%s:***@%s:%s/%s?sslmode=%s" % (
                    "postgresql", conn_str_dict["user"], conn_str_dict["host"],
                    conn_str_dict["port"], conn_str_dict["db_name"], sslmode)
                    self.logger.log(f"PostgreSQL connection string (masked): {masked_str}")
                    test=True
                except Exception as e:
                    self.logger.log_exception(e, "creating PostgreSQL connection string (with SSL)")
                    QMessageBox.warning(self, "Attenzione", 'Problema', QMessageBox.Ok)
                    conn_str = "%s://%s:%s@%s:%s/%s?sslmode=%s" % (
                    "postgresql", conn_str_dict["user"], conn_str_dict["password"], conn_str_dict["host"],
                    conn_str_dict["port"], conn_str_dict["db_name"], sslmode)
                    masked_str = "%s://%s:***@%s:%s/%s?sslmode=%s" % (
                    "postgresql", conn_str_dict["user"], conn_str_dict["host"],
                    conn_str_dict["port"], conn_str_dict["db_name"], sslmode)
                    self.logger.log(f"PostgreSQL connection string fallback (masked): {masked_str}")

            elif conn_str_dict["server"] == 'sqlite':
                sqlite_DB_path = '{}{}{}'.format(self.HOME, os.sep,
                                               "pyarchinit_DB_folder")
                dbname_abs = sqlite_DB_path + os.sep + conn_str_dict["db_name"]
                conn_str = "%s:///%s" % (conn_str_dict["server"], dbname_abs)
                self.logger.log(f"SQLite connection string: {conn_str}")
            else:
                self.logger.log(f"Unknown server type: {conn_str_dict['server']}")
                conn_str = None

        except Exception as e:
            self.logger.log_exception(e, "conn_str")
            raise

        self.logger.log(f"Returning connection string: {conn_str is not None}")
        return conn_str
        
    def databasename(self):
        cfg_rel_path = os.path.join(os.sep, 'pyarchinit_DB_folder', 'config.cfg')
        file_path = '{}{}'.format(self.HOME, cfg_rel_path)
        conf = open(file_path, "r")

        data = conf.read()
        settings = Settings(data)
        settings.set_configuration()
        conf.close()
        dbname = {"db_name": settings.DATABASE}

        return dbname
    def datauser(self):
        cfg_rel_path = os.path.join(os.sep, 'pyarchinit_DB_folder', 'config.cfg')
        file_path = '{}{}'.format(self.HOME, cfg_rel_path)
        conf = open(file_path, "r")

        data = conf.read()
        settings = Settings(data)
        settings.set_configuration()
        conf.close()
        user = {"user": settings.USER}

        return user
    def datahost(self):
        cfg_rel_path = os.path.join(os.sep, 'pyarchinit_DB_folder', 'config.cfg')
        file_path = '{}{}'.format(self.HOME, cfg_rel_path)
        conf = open(file_path, "r")

        data = conf.read()
        settings = Settings(data)
        settings.set_configuration()
        conf.close()
        host = {"host": settings.HOST}
        return host
    def dataport(self):
        cfg_rel_path = os.path.join(os.sep, 'pyarchinit_DB_folder', 'config.cfg')
        file_path = '{}{}'.format(self.HOME, cfg_rel_path)
        conf = open(file_path, "r")

        data = conf.read()
        settings = Settings(data)
        settings.set_configuration()
        conf.close()
        port = {"port": settings.PORT}
        return port
    
    def datapassword(self):
        
        cfg_rel_path = os.path.join(os.sep, 'pyarchinit_DB_folder', 'config.cfg')
        file_path = '{}{}'.format(self.HOME, cfg_rel_path)
        conf = open(file_path, "r")

        data = conf.read()
        settings = Settings(data)
        settings.set_configuration()
        conf.close()
        password = {"password": settings.PASSWORD}
        return password
        
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
    
    def thumb_resize(self):
        cfg_rel_path = os.path.join(os.sep, 'pyarchinit_DB_folder', 'config.cfg')
        file_path = '{}{}'.format(self.HOME, cfg_rel_path)
        conf = open(file_path, "r")

        data = conf.read()
        settings = Settings(data)
        settings.set_configuration()
        conf.close()
        thumb_resize = {"thumb_resize": settings.THUMB_RESIZE}

        return thumb_resize
    def sito_set(self):
        cfg_rel_path = os.path.join(os.sep, 'pyarchinit_DB_folder', 'config.cfg')
        file_path = '{}{}'.format(self.HOME, cfg_rel_path)
        conf = open(file_path, "r")

        data = conf.read()
        settings = Settings(data)
        settings.set_configuration()
        conf.close()
        sito_set = {"sito_set": settings.SITE_SET}

        return sito_set
    def logo_path(self):
        cfg_rel_path = os.path.join(os.sep, 'pyarchinit_DB_folder', 'config.cfg')
        file_path = '{}{}'.format(self.HOME, cfg_rel_path)
        conf = open(file_path, "r")

        data = conf.read()
        settings = Settings(data)
        settings.set_configuration()
        conf.close()
        logo = {"logo": settings.LOGO}

        return logo