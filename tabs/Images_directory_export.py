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
from __future__ import absolute_import

import os

import sys
from builtins import str
from qgis.PyQt.QtWidgets import QDialog, QMessageBox
from qgis.PyQt.uic import loadUiType

from ..gui.pyarchinitConfigDialog import pyArchInitDialog_Config
from ..modules.db.pyarchinit_conn_strings import Connection
from ..modules.db.pyarchinit_db_manager import Pyarchinit_db_management
from ..modules.db.pyarchinit_utility import Utility
from ..modules.utility.pyarchinit_OS_utility import Pyarchinit_OS_Utility

MAIN_DIALOG_CLASS, _ = loadUiType(
    os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'Images_directory_export.ui'))


class pyarchinit_Images_directory_export(QDialog, MAIN_DIALOG_CLASS):
    UTILITY = Utility()
    OS_UTILITY = Pyarchinit_OS_Utility()
    DB_MANAGER = ""
    HOME = os.environ['PYARCHINIT_HOME']

    ##  if os.name == 'posix':
    ##      HOME = os.environ['HOME']
    ##  elif os.name == 'nt':
    ##      HOME = os.environ['HOMEPATH']
    ##
    ##  PARAMS_DICT={'SERVER':'',
    ##              'HOST': '',
    ##              'DATABASE':'',
    ##              'PASSWORD':'',
    ##              'PORT':'',
    ##              'USER':'',
    ##              'THUMB_PATH':''}


    def __init__(self, parent=None, db=None):
        QDialog.__init__(self, parent)
        # Set up the user interface from Designer.
        self.setupUi(self)

        try:
            self.connect()
        except:
            pass
        self.charge_list()
        #self.set_home_path()

        # self.load_dict()
        # self.charge_data()

    def connect(self):
        QMessageBox.warning(self, "Alert", "Sistema sperimentale solo per lo sviluppo", QMessageBox.Ok)

        conn = Connection()
        conn_str = conn.conn_str()
        try:
            self.DB_MANAGER = Pyarchinit_db_management(conn_str)
            self.DB_MANAGER.connection()
        except Exception as e:
            e = str(e)
            if e.find("no such table"):
                QMessageBox.warning(self, "Alert",
                                    "La connessione e' fallita <br><br> %s. E' NECESSARIO RIAVVIARE QGIS" % (str(e)),
                                    QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "Alert",
                                    "Attenzione rilevato bug! Segnalarlo allo sviluppatore<br> Errore: <br>" + str(e),
                                    QMessageBox.Ok)

    def charge_list(self):
        # lista sito
        sito_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('site_table', 'sito', 'SITE'))
        try:
            sito_vl.remove('')
        except:
            pass

        self.comboBox_sito.clear()

        sito_vl.sort()
        self.comboBox_sito.addItems(sito_vl)

    #def set_home_path(self):
        #self.HOME = os.environ['PYARCHINIT_HOME']

    def on_pushButton_exp_icons_pressed(self):
        sito = str(self.comboBox_sito.currentText())
        conn = Connection()
        conn_str = conn.conn_str()
        thumb_resize = conn.thumb_resize()
        thumb_resize_str = thumb_resize['thumb_resize']
        if self.checkBox_US.isChecked()== True:
            us_res = self.db_search_DB('US', 'sito', sito)
            sito_path = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_image_export")
            self.OS_UTILITY.create_dir(sito_path)
            if bool(us_res)== True:
                US_path = '{}{}{}'.format(sito_path, os.sep, "Unita_Stratigrafiche")
                self.OS_UTILITY.create_dir(US_path)
                for sing_us in us_res:
                    sing_us_num = str(sing_us.us)
                    prefix = '0'
                    sing_us_num_len = len(sing_us_num)
                    if sing_us_num_len == 1:
                        prefix = prefix * 4
                    elif sing_us_num_len == 2:
                        prefix = prefix * 3
                    elif sing_us_num_len == 3:
                        prefix = prefix * 2
                    else:
                        pass

                    sing_us_dir = prefix + str(sing_us_num)
                    sing_US_path = ('%s%sUS%s') % (US_path, os.sep, sing_us_dir)
                    self.OS_UTILITY.create_dir(sing_US_path)

                    search_dict = {'id_entity': sing_us.id_us, 'entity_type': "'" + "US" + "'"}

                    u = Utility()
                    search_dict = u.remove_empty_items_fr_dict(search_dict)
                    search_images_res = self.DB_MANAGER.query_bool(search_dict, 'MEDIAVIEW')

                    for sing_media in search_images_res:
                        self.OS_UTILITY.copy_file_img(thumb_resize_str+str(sing_media.path_resize), sing_US_path)
                    ##                      QMessageBox.warning(self, "Alert", str(sing_media.filepath),  QMessageBox.Ok)
                    ##                      QMessageBox.warning(self, "Alert", str(sing_US_path),  QMessageBox.Ok)

                    search_images_res = ""
                QMessageBox.warning(self, "Alert", "Creazione directories terminata", QMessageBox.Ok)
        
        
        if self.checkBox_reperti.isChecked()== True:
            reperti_res = self.db_search_DB('INVENTARIO_MATERIALI', 'sito', sito)
            sito_path = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_image_export")
            self.OS_UTILITY.create_dir(sito_path)
            if bool(reperti_res)== True:
                REPERTI_path = '{}{}{}'.format(sito_path, os.sep, "REPERTI")
                self.OS_UTILITY.create_dir(REPERTI_path)
                for sing_reperti in reperti_res:
                    sing_reperti_num = str(sing_reperti.numero_inventario)
                    prefix = '0'
                    sing_reperti_num_len = len(sing_reperti_num)
                    if sing_reperti_num_len == 1:
                        prefix = prefix * 4
                    elif sing_reperti_num_len == 2:
                        prefix = prefix * 3
                    elif sing_reperti_num_len == 3:
                        prefix = prefix * 2
                    else:
                        pass

                    sing_reperti_dir = prefix + str(sing_reperti_num)
                    sing_REPERTI_path = ('%s%sREPERTI%s') % (REPERTI_path, os.sep, sing_reperti_dir)
                    self.OS_UTILITY.create_dir(sing_REPERTI_path)

                    search_dict = {'id_entity': sing_reperti.id_invmat, 'entity_type': "'" + "REPERTO" + "'"}

                    u = Utility()
                    search_dict = u.remove_empty_items_fr_dict(search_dict)
                    search_images_res = self.DB_MANAGER.query_bool(search_dict, 'MEDIAVIEW')

                    for sing_media in search_images_res:
                        self.OS_UTILITY.copy_file_img(thumb_resize_str+str(sing_media.path_resize), sing_REPERTI_path)
                    ##                      QMessageBox.warning(self, "Alert", str(sing_media.filepath),  QMessageBox.Ok)
                    ##                      QMessageBox.warning(self, "Alert", str(sing_US_path),  QMessageBox.Ok)

                    search_images_res = ""
                QMessageBox.warning(self, "Alert", "Creazione directories terminata", QMessageBox.Ok)
    def db_search_DB(self, table_class, field, value):
        self.table_class = table_class
        self.field = field
        self.value = value

        search_dict = {self.field: "'" + str(self.value) + "'"}

        u = Utility()
        search_dict = u.remove_empty_items_fr_dict(search_dict)

        res = self.DB_MANAGER.query_bool(search_dict, self.table_class)

        return res


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = pyArchInitDialog_Config()
    ui.show()
    sys.exit(app.exec_())
