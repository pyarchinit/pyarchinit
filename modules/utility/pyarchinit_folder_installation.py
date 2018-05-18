#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
/***************************************************************************
        pyArchInit Plugin  - A QGIS plugin to manage archaeological dataset
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
from os.path import expanduser

from builtins import object
from builtins import str

from .pyarchinit_OS_utility import Pyarchinit_OS_Utility


class pyarchinit_Folder_installation(object):
    HOME = expanduser("~")
    HOME += os.sep + 'pyarchinit'
    os.environ['PYARCHINIT_HOME'] = HOME
    MODULE_PATH = os.path.dirname(__file__)

    OS_UTILITY = Pyarchinit_OS_Utility()

    def install_dir(self):
        home_DB_path = '{}{}{}'.format(self.HOME, os.sep, 'pyarchinit_DB_folder')

        self.installConfigFile(home_DB_path)

        db_copy_from_path_rel = os.path.join(os.sep, 'DBfiles', 'pyarchinit_db.sqlite')
        db_copy_from_path = '{}{}'.format(self.MODULE_PATH, db_copy_from_path_rel)
        db_copy_to_path = '{}{}{}'.format(home_DB_path, os.sep, 'pyarchinit_db.sqlite')

        logo_copy_from_path_rel = os.path.join(os.sep, 'DBfiles', 'logo.jpg')
        logo_copy_from_path = '{}{}'.format(self.MODULE_PATH, logo_copy_from_path_rel)
        logo_copy_to_path = '{}{}{}'.format(home_DB_path, os.sep, 'logo.jpg')

        self.OS_UTILITY.create_dir(str(home_DB_path))

        self.OS_UTILITY.copy_file(db_copy_from_path, db_copy_to_path)
        self.OS_UTILITY.copy_file(logo_copy_from_path, logo_copy_to_path)

        home_PDF_path = '{}{}{}'.format(self.HOME, os.sep, 'pyarchinit_PDF_folder')
        self.OS_UTILITY.create_dir(home_PDF_path)

        home_MATRIX_path = '{}{}{}'.format(self.HOME, os.sep, 'pyarchinit_Matrix_folder')
        self.OS_UTILITY.create_dir(home_MATRIX_path)

        home_THUMBNAILS_path = '{}{}{}'.format(self.HOME, os.sep, 'pyarchinit_Thumbnails_folder')
        self.OS_UTILITY.create_dir(home_THUMBNAILS_path)

        home_MAPS_path = '{}{}{}'.format(self.HOME, os.sep, 'pyarchinit_MAPS_folder')
        self.OS_UTILITY.create_dir(home_MAPS_path)

        home_REPORT_path = '{}{}{}'.format(self.HOME, os.sep, 'pyarchinit_Report_folder')
        self.OS_UTILITY.create_dir(home_REPORT_path)

        home_QUANT_path = '{}{}{}'.format(self.HOME, os.sep, 'pyarchinit_Quantificazioni_folder')
        self.OS_UTILITY.create_dir(home_QUANT_path)

        home_TEST_path = '{}{}{}'.format(self.HOME, os.sep, 'pyarchinit_Test_folder')
        self.OS_UTILITY.create_dir(home_TEST_path)

        home_BACKUP_linux_path = '{}{}{}'.format(self.HOME, os.sep, 'pyarchinit_db_backup')
        self.OS_UTILITY.create_dir(home_BACKUP_linux_path)

    def installConfigFile(self, path):
        config_copy_from_path_rel = os.path.join(os.sep, 'DBfiles', 'config.cfg')
        config_copy_from_path = '{}{}'.format(self.MODULE_PATH, config_copy_from_path_rel)
        config_copy_to_path = '{}{}{}'.format(path, os.sep, 'config.cfg')
        self.OS_UTILITY.copy_file(config_copy_from_path, config_copy_to_path)
