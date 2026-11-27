#! /usr/bin/env python
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
import traceback
import sys
from qgis.PyQt.QtWidgets import *
from qgis.core import QgsMessageLog, Qgis, QgsSettings
from .pyarchinit_OS_utility import Pyarchinit_OS_Utility


#: keys every config.cfg must carry, with the value a new one gets
_CONFIG_DEFAULTS = (("THUMB_RESIZE", "insert path for the image resized"),
                    ("SITE_SET", ""),
                    ("LOGO", "insert path for the image logo"),
                    ("SSLMODE", "allow"))


def _ensure_config_keys(path_rel):
    """Add the keys a config.cfg lacks, reading it as the dictionary it is.

    The old repair patched the file by byte offsets (``seek(-3, 2)``): on a
    file without a trailing newline, or lacking two keys at once, it wrote
    ``'SITE_SET' :','LOGO'`` and the configuration no longer parsed — every
    export failed with SyntaxError (27 Nov 2026). A file that does not parse
    is left exactly as it is."""
    import ast
    try:
        with open(path_rel, "r", encoding="utf-8") as fh:
            testo = fh.read()
        conf = ast.literal_eval(testo.strip())
    except Exception:                               # noqa: BLE001
        return
    if not isinstance(conf, dict):
        return
    mancanti = [(k, v) for k, v in _CONFIG_DEFAULTS if k not in conf]
    if not mancanti:
        return
    for k, v in mancanti:
        conf[k] = v
    try:
        with open(path_rel, "w", encoding="utf-8") as fh:
            fh.write(repr(conf))
    except Exception:                               # noqa: BLE001
        pass


class Settings(object):

    SERVER = ""
    HOST = ""
    DATABASE = ""
    PASSWORD = ""
    PORT = ""
    USER = ""
    SSLMODE = "allow"
    THUMB_PATH = ""
    THUMB_RESIZE = ""
    SITE_SET = ""
    LOGO = ""
    RESOURCES_PATH = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'resources')
    OS_UTILITY = Pyarchinit_OS_Utility()
    HOME = os.environ['PYARCHINIT_HOME']
    path_rel = os.path.join(os.sep, HOME, 'pyarchinit_DB_folder', 'config.cfg')
    
    _ensure_config_keys(path_rel)

    def __init__(self, s):

        self.configuration = eval(s)

    def set_configuration(self):

        self.SERVER = self.configuration['SERVER']
        self.HOST = self.configuration['HOST']
        self.DATABASE = self.configuration['DATABASE']
        self.PASSWORD = self.configuration['PASSWORD']
        self.PORT = self.configuration['PORT']
        self.USER = self.configuration['USER']
        self.SSLMODE = self.configuration.get('SSLMODE', 'allow')
        self.THUMB_PATH = self.configuration['THUMB_PATH']
        self.THUMB_RESIZE = self.configuration['THUMB_RESIZE']
        self.SITE_SET = self.configuration['SITE_SET']
        self.LOGO = self.configuration['LOGO']
        PLUGIN_PATH = path = os.path.dirname(__file__)
