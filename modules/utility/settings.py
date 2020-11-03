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

import os

from builtins import object
from qgis.PyQt.QtWidgets import *
from .pyarchinit_OS_utility import Pyarchinit_OS_Utility

class Settings(object):
    SERVER = ""
    HOST = ""
    DATABASE = ""
    PASSWORD = ""
    PORT = ""
    USER = ""
    THUMB_PATH = ""
    THUMB_RESIZE = ""
    SITE_SET = ""
    RESOURCES_PATH = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'resources')
    OS_UTILITY = Pyarchinit_OS_Utility()
    HOME = os.environ['PYARCHINIT_HOME']
    path_rel = os.path.join(os.sep, HOME, 'pyarchinit_DB_folder', 'config.cfg')
    
    conf = open(path_rel,"rb+")
    
    data = conf.read()
    
    text = (b'THUMB_RESIZE')
    text_a = (b'SITE_SET')
    text_database= (b'sqlite')
    test_name_database= (b'pyarchinit_db.sqlite')
    

    
    if text in data:
        pass   
    else:       
        conf.seek(-3,2)
        conf.read(1)    
        conf.write(b"','THUMB_RESIZE' : 'insert path for the image resized'")
        
    if text_a in data:
        pass
    else:
        conf.seek(-3,2)
        conf.read(1)
        conf.write(b"','SITE_SET' : ''}")
     
    if data==True:
        conf.close()
        
        
    else:
        QMessageBox.warning(None,"BENVENUTO", "Problemi di connessione: verrà ripristinato il db sqlite di default",  QMessageBox.Ok)
        home_DB_path = '{}{}{}'.format(HOME, os.sep, 'pyarchinit_DB_folder')
        
        config_copy_from_path_rel = os.path.join(os.sep, 'dbfiles', 'config.cfg')
        config_copy_from_path = '{}{}'.format(RESOURCES_PATH, config_copy_from_path_rel)
        config_copy_to_path = '{}{}{}'.format(home_DB_path, os.sep, 'config.cfg')
        OS_UTILITY.copy_file_img(config_copy_from_path, config_copy_to_path)
        data
        conf.close()
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
        self.THUMB_RESIZE = self.configuration['THUMB_RESIZE']
        self.SITE_SET = self.configuration['SITE_SET']
        PLUGIN_PATH = path = os.path.dirname(__file__)
