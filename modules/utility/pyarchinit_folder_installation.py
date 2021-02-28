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
import shutil
from builtins import object
from builtins import str

from .pyarchinit_OS_utility import Pyarchinit_OS_Utility


class pyarchinit_Folder_installation(object):
    HOME = expanduser("~")
    HOME += os.sep + 'pyarchinit'
    os.environ['PYARCHINIT_HOME'] = HOME
    RESOURCES_PATH = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'resources')

    OS_UTILITY = Pyarchinit_OS_Utility()

    def install_dir(self):
        home_DB_path = '{}{}{}'.format(self.HOME, os.sep, 'pyarchinit_DB_folder')
        self.OS_UTILITY.create_dir(home_DB_path)

        self.installConfigFile(home_DB_path)

        home_bin_export_path = '{}{}{}'.format(self.HOME, os.sep, 'bin')
        self.OS_UTILITY.create_dir(home_bin_export_path)

        db_copy_from_bin_rel = os.path.join(os.sep, 'dbfiles', 'pyarchinit.sqlite')
        db_copy_from_bin = '{}{}'.format(self.RESOURCES_PATH, db_copy_from_bin_rel)
        db_copy_to_bin = '{}{}{}'.format(home_bin_export_path, os.sep, 'pyarchinit.sqlite')

        w_copy_from_path_rel = os.path.join(os.sep, 'dbfiles', 'sqldiff.exe')
        w_copy_from_path = '{}{}'.format(self.RESOURCES_PATH, w_copy_from_path_rel)
        w_copy_to_path = '{}{}{}'.format(home_bin_export_path, os.sep, 'sqldiff.exe')

        linux_copy_from_path_rel = os.path.join(os.sep, 'dbfiles', 'sqldiff_linux')
        linux_copy_from_path = '{}{}'.format(self.RESOURCES_PATH, linux_copy_from_path_rel)
        linux_copy_to_path = '{}{}{}'.format(home_bin_export_path, os.sep, 'sqldiff_linux')

        osx_copy_from_path_rel = os.path.join(os.sep, 'dbfiles', 'sqldiff_osx')
        osx_copy_from_path = '{}{}'.format(self.RESOURCES_PATH, osx_copy_from_path_rel)
        osx_copy_to_path = '{}{}{}'.format(home_bin_export_path, os.sep, 'sqldiff_osx')
        
        dottoxml_copy_from_path_rel = os.path.join(os.sep, 'dbfiles', 'dottoxml.py')
        dottoxml_copy_from_path = '{}{}'.format(self.RESOURCES_PATH, dottoxml_copy_from_path_rel)
        dottoxml_copy_to_path = '{}{}{}'.format(home_bin_export_path, os.sep, 'dottoxml.py')
        
        dot_copy_from_path_rel = os.path.join(os.sep, 'dbfiles', 'dot.py')
        dot_copy_from_path = '{}{}'.format(self.RESOURCES_PATH, dot_copy_from_path_rel)
        dot_copy_to_path = '{}{}{}'.format(home_bin_export_path, os.sep, 'dot.py')
        
        X11Colors_copy_from_path_rel = os.path.join(os.sep, 'dbfiles', 'X11Colors.py')
        X11Colors_copy_from_path = '{}{}'.format(self.RESOURCES_PATH, X11Colors_copy_from_path_rel)
        X11Colors_copy_to_path = '{}{}{}'.format(home_bin_export_path, os.sep, 'X11Colors.py')
        
        self.OS_UTILITY.copy_file(db_copy_from_bin, db_copy_to_bin)
        self.OS_UTILITY.copy_file(w_copy_from_path, w_copy_to_path)
        self.OS_UTILITY.copy_file(linux_copy_from_path, linux_copy_to_path)
        self.OS_UTILITY.copy_file(osx_copy_from_path, osx_copy_to_path)
        self.OS_UTILITY.copy_file(dottoxml_copy_from_path, dottoxml_copy_to_path)
        self.OS_UTILITY.copy_file(dot_copy_from_path, dot_copy_to_path)
        self.OS_UTILITY.copy_file(X11Colors_copy_from_path, X11Colors_copy_to_path)

        db_copy_from_path_rel = os.path.join(os.sep, 'dbfiles', 'pyarchinit_db.sqlite')
        db_copy_from_path = '{}{}'.format(self.RESOURCES_PATH, db_copy_from_path_rel)
        db_copy_to_path = '{}{}{}'.format(home_DB_path, os.sep, 'pyarchinit_db.sqlite')
        
        logo_copy_from_path_rel = os.path.join(os.sep, 'dbfiles', 'logo.jpg')
        logo_copy_from_path = '{}{}'.format(self.RESOURCES_PATH, logo_copy_from_path_rel)
        logo_copy_to_path = '{}{}{}'.format(home_DB_path, os.sep, 'logo.jpg')
        
        
        logo_copy_from_path_rel_adarte = os.path.join(os.sep, 'dbfiles', 'logo_2.png')
        logo_copy_from_path_adarte = '{}{}'.format(self.RESOURCES_PATH, logo_copy_from_path_rel_adarte)
        logo_copy_to_path_adarte = '{}{}{}'.format(home_DB_path, os.sep, 'logo_2.png')
        
        ### logo per la versione tedesca
        logo_copy_from_path_rel_de = os.path.join(os.sep, 'dbfiles', 'logo_de.jpg')
        logo_copy_from_path_de = '{}{}'.format(self.RESOURCES_PATH, logo_copy_from_path_rel_de)
        logo_copy_to_path_de = '{}{}{}'.format(home_DB_path, os.sep, 'logo_de.jpg')
        
        
        self.OS_UTILITY.copy_file(db_copy_from_path, db_copy_to_path)
        self.OS_UTILITY.copy_file(logo_copy_from_path, logo_copy_to_path)
        self.OS_UTILITY.copy_file(logo_copy_from_path_adarte, logo_copy_to_path_adarte)   
        self.OS_UTILITY.copy_file(logo_copy_from_path_de, logo_copy_to_path_de)   

        home_excel_path = '{}{}{}'.format(self.HOME, os.sep, 'pyarchinit_EXCEL_folder')
        self.OS_UTILITY.create_dir(home_excel_path)
		
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

        home_image_export_path = '{}{}{}'.format(self.HOME, os.sep, 'pyarchinit_image_export')
        self.OS_UTILITY.create_dir(home_image_export_path)
        
        home_R_export_path = '{}{}{}'.format(self.HOME, os.sep, 'pyarchinit_R_export')
        self.OS_UTILITY.create_dir(home_R_export_path)



    def installConfigFile(self, path):
        
        config_copy_from_path_rel = os.path.join(os.sep, 'dbfiles', 'config.cfg')
        config_copy_from_path = '{}{}'.format(self.RESOURCES_PATH, config_copy_from_path_rel)
        config_copy_to_path = '{}{}{}'.format(path, os.sep, 'config.cfg')
        self.OS_UTILITY.copy_file(config_copy_from_path, config_copy_to_path)

        logo_copy_from_path_rel = os.path.join(os.sep, 'dbfiles', 'logo.jpg')
        logo_copy_from_path = '{}{}'.format(self.RESOURCES_PATH, logo_copy_from_path_rel)
        logo_copy_to_path = '{}{}{}'.format(path, os.sep, 'logo.jpg')
        
        self.OS_UTILITY.copy_file(logo_copy_from_path, logo_copy_to_path)
        
        logo_copy_from_path_rel_adarte = os.path.join(os.sep, 'dbfiles', 'logo_2.png')
        logo_copy_from_path_adarte = '{}{}'.format(self.RESOURCES_PATH, logo_copy_from_path_rel_adarte)
        logo_copy_to_path_adarte = '{}{}{}'.format(path, os.sep, 'logo_2.png')
        
        self.OS_UTILITY.copy_file(logo_copy_from_path_adarte, logo_copy_to_path_adarte)
        
        
        logo_copy_from_path_rel_de = os.path.join(os.sep, 'dbfiles', 'logo_de.jpg')
        logo_copy_from_path_de = '{}{}'.format(self.RESOURCES_PATH, logo_copy_from_path_rel_de)
        logo_copy_to_path_de = '{}{}{}'.format(path, os.sep, 'logo_de.jpg')
        
        self.OS_UTILITY.copy_file(logo_copy_from_path_de, logo_copy_to_path_de)

        home_bin_export_path = '{}{}{}'.format(self.HOME, os.sep, 'bin')
        self.OS_UTILITY.create_dir(home_bin_export_path)

        db_copy_from_bin_rel = os.path.join(os.sep, 'dbfiles', 'pyarchinit.sqlite')
        db_copy_from_bin = '{}{}'.format(self.RESOURCES_PATH, db_copy_from_bin_rel)
        db_copy_to_bin = '{}{}{}'.format(home_bin_export_path, os.sep, 'pyarchinit.sqlite')

        w_copy_from_path_rel = os.path.join(os.sep, 'dbfiles', 'sqldiff.exe')
        w_copy_from_path = '{}{}'.format(self.RESOURCES_PATH, w_copy_from_path_rel)
        w_copy_to_path = '{}{}{}'.format(home_bin_export_path, os.sep, 'sqldiff.exe')

        linux_copy_from_path_rel = os.path.join(os.sep, 'dbfiles', 'sqldiff_linux')
        linux_copy_from_path = '{}{}'.format(self.RESOURCES_PATH, linux_copy_from_path_rel)
        linux_copy_to_path = '{}{}{}'.format(home_bin_export_path, os.sep, 'sqldiff_linux')

        osx_copy_from_path_rel = os.path.join(os.sep, 'dbfiles', 'sqldiff_osx')
        osx_copy_from_path = '{}{}'.format(self.RESOURCES_PATH, osx_copy_from_path_rel)
        osx_copy_to_path = '{}{}{}'.format(home_bin_export_path, os.sep, 'sqldiff_osx')
        
        dottoxml_copy_from_path_rel = os.path.join(os.sep, 'dbfiles', 'dottoxml.py')
        dottoxml_copy_from_path = '{}{}'.format(self.RESOURCES_PATH, dottoxml_copy_from_path_rel)
        dottoxml_copy_to_path = '{}{}{}'.format(home_bin_export_path, os.sep, 'dottoxml.py')
        
        dot_copy_from_path_rel = os.path.join(os.sep, 'dbfiles', 'dot.py')
        dot_copy_from_path = '{}{}'.format(self.RESOURCES_PATH, dot_copy_from_path_rel)
        dot_copy_to_path = '{}{}{}'.format(home_bin_export_path, os.sep, 'dot.py')
        
        X11Colors_copy_from_path_rel = os.path.join(os.sep, 'dbfiles', 'X11Colors.py')
        X11Colors_copy_from_path = '{}{}'.format(self.RESOURCES_PATH, X11Colors_copy_from_path_rel)
        X11Colors_copy_to_path = '{}{}{}'.format(home_bin_export_path, os.sep, 'X11Colors.py')
        
        self.OS_UTILITY.copy_file(db_copy_from_bin, db_copy_to_bin)
        self.OS_UTILITY.copy_file(w_copy_from_path, w_copy_to_path)
        self.OS_UTILITY.copy_file(linux_copy_from_path, linux_copy_to_path)
        self.OS_UTILITY.copy_file(osx_copy_from_path, osx_copy_to_path)
        self.OS_UTILITY.copy_file_img(dottoxml_copy_from_path, dottoxml_copy_to_path)
        self.OS_UTILITY.copy_file_img(dot_copy_from_path, dot_copy_to_path)
        self.OS_UTILITY.copy_file_img(X11Colors_copy_from_path, X11Colors_copy_to_path)