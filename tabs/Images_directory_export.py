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
import platform
import sys
from builtins import str
from qgis.PyQt.QtWidgets import QDialog, QMessageBox
from qgis.PyQt.uic import loadUiType
from qgis.core import QgsSettings
from ..gui.pyarchinitConfigDialog import pyArchInitDialog_Config
from ..modules.db.pyarchinit_conn_strings import Connection
from ..modules.db.pyarchinit_db_manager import Pyarchinit_db_management
from ..modules.db.pyarchinit_utility import Utility
from ..modules.utility.pyarchinit_OS_utility import Pyarchinit_OS_Utility

MAIN_DIALOG_CLASS, _ = loadUiType(
    os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'Images_directory_export.ui'))


class pyarchinit_Images_directory_export(QDialog, MAIN_DIALOG_CLASS):
    L=QgsSettings().value("locale/userLocale")[0:2]
    UTILITY = Utility()
    OS_UTILITY = Pyarchinit_OS_Utility()
    DB_MANAGER = ""
    HOME = os.environ['PYARCHINIT_HOME']

    def __init__(self, parent=None, db=None):
        QDialog.__init__(self, parent)
        # Set up the user interface from Designer.
        self.setupUi(self)

        try:
            self.connect()
        except:
            pass
        self.charge_list()
        
    def connect(self):
        #QMessageBox.warning(self, "Alert", "Sistema sperimentale solo per lo sviluppo", QMessageBox.Ok)

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
    def on_pushButton_open_dir_pressed(self):
        #HOME = os.environ['PYARCHINIT_HOME']
        path = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_image_export")
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
    
   
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
        try:
            if self.comboBox_export.currentIndex()==0:
                
                us_res = self.db_search_DB('US', 'sito', sito)
                sito_path = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_image_export")
                self.OS_UTILITY.create_dir(sito_path)
                if bool(us_res):
                    if self.L=='it':
                        sito_folder =  '{}{}{}'.format(sito_path, os.sep, self.comboBox_sito.currentText() +' - '+ str('Tutte le immagini'))
                    elif self.L=='de':
                        sito_folder =  '{}{}{}'.format(sito_path, os.sep, self.comboBox_sito.currentText() +' - '+ str('Alle Bilder'))
                    else:
                        sito_folder =  '{}{}{}'.format(sito_path, os.sep, self.comboBox_sito.currentText() +' - '+ str('All Images'))
                    # Periodo_path = '{}{}{}'.format(sito_folder, os.sep, "Periodo")
                    # self.OS_UTILITY.create_dir(Periodo_path)
                    for sing_us in us_res:
                        sing_per_num = str(sing_us.periodo_iniziale)
                        prefix = ''
                        sing_per_num_len = len(sing_per_num)
                        if sing_per_num_len == 1:
                            prefix = prefix * 1
                        
                        else:
                            pass
                        sing_per_dir = prefix + str(sing_per_num)
                        if self.L=='it':
                            sing_Periodo_path = ('%s%sPeriodo - %s') % (sito_folder, os.sep, sing_per_dir)
                        elif self.L=='de':
                            sing_Periodo_path = ('%s%sPeriod - %s') % (sito_folder, os.sep, sing_per_dir)
                        else:
                            sing_Periodo_path = ('%s%sPeriod - %s') % (sito_folder, os.sep, sing_per_dir)
                        self.OS_UTILITY.create_dir(sing_Periodo_path)
                        
                        
                        
                        sing_fase_num = str(sing_us.fase_iniziale)
                        prefix = ''
                        sing_fase_num_len = len(sing_fase_num)
                        if sing_fase_num_len == 1:
                            prefix = prefix * 1
                        
                        else:
                            pass
                        sing_fase_dir = prefix + str(sing_fase_num)
                        if self.L=='it':
                            sing_Fase_path = ('%s%sFase - %s') % (sing_Periodo_path, os.sep, sing_fase_dir)
                        elif self.L=='de':
                            sing_Fase_path = ('%s%sPhase - %s') % (sing_Periodo_path, os.sep, sing_fase_dir)
                        else:
                            sing_Fase_path = ('%s%sPhase - %s') % (sing_Periodo_path, os.sep, sing_fase_dir)
                        self.OS_UTILITY.create_dir(sing_Fase_path)
                            
                            
                            
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
                        if self.L=='it':
                            sing_US_path = ('%s%sUS - %s') % (sing_Fase_path , os.sep, sing_us_dir)
                        elif self.L=='de':
                            sing_US_path = ('%s%sSE - %s') % (sing_Fase_path , os.sep, sing_us_dir)
                        else:
                            sing_US_path = ('%s%sSU - %s') % (sing_Fase_path , os.sep, sing_us_dir)
                        self.OS_UTILITY.create_dir(sing_US_path)

                        search_dict = {'id_entity': sing_us.id_us, 'entity_type': "'" + "US" + "'"}

                        u = Utility()
                        search_dict = u.remove_empty_items_fr_dict(search_dict)
                        search_images_res = self.DB_MANAGER.query_bool(search_dict, 'MEDIAVIEW')

                        for sing_media in search_images_res:
                            self.OS_UTILITY.copy_file_img(thumb_resize_str+str(sing_media.path_resize), sing_US_path)
                    
                        search_images_res = ""
                    ###################Reperti################################################
                    reperti_res = self.db_search_DB('INVENTARIO_MATERIALI', 'sito', sito)
                    
                    if bool(reperti_res):
                        
                        for sing_us,a in zip(us_res, reperti_res):
                            sing_per_num = str(sing_us.area)
                            prefix = ''
                            sing_per_num_len = len(sing_per_num)
                            if sing_per_num_len == 1:
                                prefix = prefix * 1
                            
                            else:
                                pass
                            sing_per_dir = prefix + str(sing_per_num)
                            if self.L=='it':
                                sing_Periodo_path = ('%s%sPeriodo - %s') % (sito_folder, os.sep, sing_per_dir)
                            elif self.L=='de':
                                sing_Periodo_path = ('%s%sPeriod - %s') % (sito_folder, os.sep, sing_per_dir)
                            else:
                                sing_Periodo_path = ('%s%sPeriod - %s') % (sito_folder, os.sep, sing_per_dir)
                            self.OS_UTILITY.create_dir(sing_Periodo_path)
                            
                            
                            
                            sing_fase_num = str(sing_us.us)
                            prefix = ''
                            sing_fase_num_len = len(sing_fase_num)
                            if sing_fase_num_len == 1:
                                prefix = prefix * 1
                            
                            else:
                                pass
                            sing_fase_dir = prefix + str(sing_fase_num)
                            if self.L=='it':
                                sing_Fase_path = ('%s%sFase - %s') % (sing_Periodo_path, os.sep, sing_fase_dir)
                            elif self.L=='de':
                                sing_Fase_path = ('%s%sPhase - %s') % (sing_Periodo_path, os.sep, sing_fase_dir)
                            else:
                                sing_Fase_path = ('%s%sPhase - %s') % (sing_Periodo_path, os.sep, sing_fase_dir)
                            self.OS_UTILITY.create_dir(sing_Fase_path)
                                
                                
                            sing_reperti_num = str(a.numero_inventario)
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
                            if self.L=='it':
                                sing_REPERTI_path = ('%s%sRA - %s') % (sing_Fase_path, os.sep, sing_reperti_dir)
                            else:
                                sing_REPERTI_path = ('%s%sAA - %s') % (sing_Fase_path, os.sep, sing_reperti_dir)
                            self.OS_UTILITY.create_dir(sing_REPERTI_path)

                            search_dict = {'id_entity': a.id_invmat, 'entity_type': "'" + "REPERTO" + "'"}

                            u = Utility()
                            search_dict = u.remove_empty_items_fr_dict(search_dict)
                            search_images_res = self.DB_MANAGER.query_bool(search_dict, 'MEDIAVIEW')

                            for sing_media in search_images_res:
                                self.OS_UTILITY.copy_file_img(thumb_resize_str+str(sing_media.path_resize), sing_REPERTI_path)
                    #################################Tombe####################################################
                    tomba_res = self.db_search_DB('TOMBA', 'sito', sito)
                    
                    if bool(tomba_res):
                        for sing_t in  tomba_res:
                            sing_per_num = str(sing_t.periodo_iniziale)
                            prefix = ''
                            sing_per_num_len = len(sing_per_num)
                            if sing_per_num_len == 1:
                                prefix = prefix * 1
                            
                            else:
                                pass
                            sing_per_dir = prefix + str(sing_per_num)
                            if self.L=='it':
                                sing_Periodo_path = ('%s%sPeriodo - %s') % (sito_folder, os.sep, sing_per_dir)
                            elif self.L=='de':
                                sing_Periodo_path = ('%s%sPeriod - %s') % (sito_folder, os.sep, sing_per_dir)
                            else:
                                sing_Periodo_path = ('%s%sPeriod - %s') % (sito_folder, os.sep, sing_per_dir)
                            self.OS_UTILITY.create_dir(sing_Periodo_path)
                            
                            
                            
                            sing_fase_num = str(sing_t.fase_iniziale)
                            prefix = ''
                            sing_fase_num_len = len(sing_fase_num)
                            if sing_fase_num_len == 1:
                                prefix = prefix * 1
                            
                            else:
                                pass
                            sing_fase_dir = prefix + str(sing_fase_num)
                            if self.L=='it':
                                sing_Fase_path = ('%s%sFase - %s') % (sing_Periodo_path, os.sep, sing_fase_dir)
                            elif self.L=='de':
                                sing_Fase_path = ('%s%sPhase - %s') % (sing_Periodo_path, os.sep, sing_fase_dir)
                            else:
                                sing_Fase_path = ('%s%sPhase - %s') % (sing_Periodo_path, os.sep, sing_fase_dir)
                            self.OS_UTILITY.create_dir(sing_Fase_path)
                            
                            sing_tomba_num = str(sing_t.nr_scheda_taf)
                            prefix = '0'
                            sing_tomba_num_len = len(sing_tomba_num)
                            if sing_tomba_num_len == 1:
                                prefix = prefix * 1
                            else:
                                pass

                            sing_tomba_dir = prefix + str(sing_tomba_num)
                            if self.L=='it':
                                sing_TOMBA_path = ('%s%sTB - %s') % (sing_Fase_path, os.sep, sing_tomba_dir)
                            elif self.L=='de':
                                sing_TOMBA_path = ('%s%sGrab - %s') % (sing_Fase_path, os.sep, sing_tomba_dir)
                            else:
                                sing_TOMBA_path = ('%s%sGrave - %s') % (sing_Fase_path, os.sep, sing_tomba_dir)    
                            
                            self.OS_UTILITY.create_dir(sing_TOMBA_path)

                            search_dict = {'id_entity': sing_t.id_tomba, 'entity_type': "'" + "TOMBA" + "'"}

                            u = Utility()
                            search_dict = u.remove_empty_items_fr_dict(search_dict)
                            search_images_res = self.DB_MANAGER.query_bool(search_dict, 'MEDIAVIEW')

                            for sing_media in search_images_res:
                                self.OS_UTILITY.copy_file_img(thumb_resize_str+str(sing_media.path_resize), sing_TOMBA_path)
                            
                            search_images_res = ""
                
                ##############################Strutture#####################################################################
                
                struttura_res = self.db_search_DB('STRUTTURA', 'sito', sito)
                if bool(struttura_res):
                
                    for sing_s in struttura_res:
                        sing_per_num = str(sing_s.periodo_iniziale)
                        prefix = ''
                        sing_per_num_len = len(sing_per_num)
                        if sing_per_num_len == 1:
                            prefix = prefix * 1
                        
                        else:
                            pass
                        sing_per_dir = prefix + str(sing_per_num)
                        if self.L=='it':
                            sing_Periodo_path = ('%s%sPeriodo - %s') % (sito_folder, os.sep, sing_per_dir)
                        elif self.L=='de':
                            sing_Periodo_path = ('%s%sPeriod - %s') % (sito_folder, os.sep, sing_per_dir)
                        else:
                            sing_Periodo_path = ('%s%sPeriod - %s') % (sito_folder, os.sep, sing_per_dir)
                        self.OS_UTILITY.create_dir(sing_Periodo_path)
                        
                        
                        
                        sing_fase_num = str(sing_s.fase_iniziale)
                        prefix = ''
                        sing_fase_num_len = len(sing_fase_num)
                        if sing_fase_num_len == 1:
                            prefix = prefix * 1
                        
                        else:
                            pass
                        sing_fase_dir = prefix + str(sing_fase_num)
                        if self.L=='it':
                            sing_Fase_path = ('%s%sFase - %s') % (sing_Periodo_path, os.sep, sing_fase_dir)
                        elif self.L=='de':
                            sing_Fase_path = ('%s%sPhase - %s') % (sing_Periodo_path, os.sep, sing_fase_dir)
                        else:
                            sing_Fase_path = ('%s%sPhase - %s') % (sing_Periodo_path, os.sep, sing_fase_dir)
                        self.OS_UTILITY.create_dir(sing_Fase_path)
                            
                            
                            
                        sing_us_num = str(sing_s.sigla_struttura+str(sing_s.numero_struttura))
                        
                        
                        
                        sing_us_dir = prefix + str(sing_us_num)
                        if self.L=='it':
                            sing_US_path = ('%s%sStruttura - %s') % (sing_Fase_path , os.sep, sing_us_num)
                        elif self.L=='de':
                            sing_US_path = ('%s%sStruktur - %s') % (sing_Fase_path , os.sep, sing_us_num)
                        else:
                            sing_US_path = ('%s%sStructure - %s') % (sing_Fase_path , os.sep, sing_us_num)
                        
                        self.OS_UTILITY.create_dir(sing_US_path)

                        search_dict = {'id_entity': sing_s.id_struttura, 'entity_type': "'" + "STRUTTURA" + "'"}

                        u = Utility()
                        search_dict = u.remove_empty_items_fr_dict(search_dict)
                        search_images_res = self.DB_MANAGER.query_bool(search_dict, 'MEDIAVIEW')

                        for sing_media in search_images_res:
                            try:
                                self.OS_UTILITY.copy_file_img(thumb_resize_str+str(sing_media.path_resize), sing_US_path)
                            except:
                                pass
                        search_images_res = ""
                    if self.L=='it':
                        QMessageBox.warning(self, "Alert", "Creazione directories terminata", QMessageBox.Ok)
                    elif self.L=='de':
                        QMessageBox.warning(self, "Alert", "Verzeichniserstellung abgeschlossen", QMessageBox.Ok)
                    else:
                        QMessageBox.warning(self, "Alert", "Directory creation complete", QMessageBox.Ok)    
            
            ############################immagini us##########################################################
            elif self.comboBox_export.currentIndex()==1:
                
                us_res1 = self.db_search_DB('US', 'sito', sito)
                sito_path1 = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_image_export")
                self.OS_UTILITY.create_dir(sito_path1)
                if bool(us_res1):
                    if self.L=='it':
                        us_folder_1 =  '{}{}{}'.format(sito_path1, os.sep, self.comboBox_sito.currentText() +' - '+ str('US in periodi e fasi'))
                    elif self.L=='de':
                        us_folder_1 =  '{}{}{}'.format(sito_path1, os.sep, self.comboBox_sito.currentText() +' - '+ str('SE in Perioden und Phasen'))
                    else:
                        us_folder_1 =  '{}{}{}'.format(sito_path1, os.sep, self.comboBox_sito.currentText() +' - '+ str('SU in period e phase'))
                    for sing_us in us_res1:
                        sing_per_num = str(sing_us.periodo_iniziale)
                        prefix = ''
                        sing_per_num_len = len(sing_per_num)
                        if sing_per_num_len == 1:
                            prefix = prefix * 1
                        
                        else:
                            pass
                        sing_per_dir = prefix + str(sing_per_num)
                        if self.L=='it':
                            sing_Periodo_path = ('%s%sPeriodo - %s') % (us_folder_1, os.sep, sing_per_dir)
                        elif self.L=='de':
                            sing_Periodo_path = ('%s%sPeriod - %s') % (us_folder_1, os.sep, sing_per_dir)
                        else:
                            sing_Periodo_path = ('%s%sPeriod - %s') % (us_folder_1, os.sep, sing_per_dir)
                        self.OS_UTILITY.create_dir(sing_Periodo_path)
                        
                        
                        
                        sing_fase_num = str(sing_us.fase_iniziale)
                        prefix = ''
                        sing_fase_num_len = len(sing_fase_num)
                        if sing_fase_num_len == 1:
                            prefix = prefix * 1
                        
                        else:
                            pass
                        sing_fase_dir = prefix + str(sing_fase_num)
                        if self.L=='it':
                            sing_Fase_path = ('%s%sFase - %s') % (sing_Periodo_path, os.sep, sing_fase_dir)
                        elif self.L=='de':
                            sing_Fase_path = ('%s%sPhase - %s') % (sing_Periodo_path, os.sep, sing_fase_dir)
                        else:
                            sing_Fase_path = ('%s%sPhase - %s') % (sing_Periodo_path, os.sep, sing_fase_dir)
                        self.OS_UTILITY.create_dir(sing_Fase_path)
                            
                            
                            
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
                        if self.L=='it':
                            sing_US_path = ('%s%sUS - %s') % (sing_Fase_path , os.sep, sing_us_dir)
                        elif self.L=='de':
                            sing_US_path = ('%s%sSE - %s') % (sing_Fase_path , os.sep, sing_us_dir)
                        else:
                            sing_US_path = ('%s%sSU - %s') % (sing_Fase_path , os.sep, sing_us_dir)    
                        
                        self.OS_UTILITY.create_dir(sing_US_path)

                        search_dict = {'id_entity': sing_us.id_us, 'entity_type': "'" + "US" + "'"}

                        u = Utility()
                        search_dict = u.remove_empty_items_fr_dict(search_dict)
                        search_images_res = self.DB_MANAGER.query_bool(search_dict, 'MEDIAVIEW')

                        for sing_media in search_images_res:
                            self.OS_UTILITY.copy_file_img(thumb_resize_str+str(sing_media.path_resize), sing_US_path)
                    
                        search_images_res = ""
                        
                
                
                    if self.L=='it':
                        QMessageBox.warning(self, "Alert", "Creazione directories terminata", QMessageBox.Ok)
                    elif self.L=='de':
                        QMessageBox.warning(self, "Alert", "Verzeichniserstellung abgeschlossen", QMessageBox.Ok)
                    else:
                        QMessageBox.warning(self, "Alert", "Directory creation complete", QMessageBox.Ok)
            
            
            
            
            elif self.comboBox_export.currentIndex()==2:
                
                us_res2 = self.db_search_DB('US', 'sito', sito)
                sito_path2 = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_image_export")
                self.OS_UTILITY.create_dir(sito_path2)
                if bool(us_res2):
                    if self.L=='it':
                        sito_folder2 =  '{}{}{}'.format(sito_path2, os.sep, self.comboBox_sito.currentText() +' - '+ str('US'))
                    elif self.L=='de':
                        sito_folder2 =  '{}{}{}'.format(sito_path2, os.sep, self.comboBox_sito.currentText() +' - '+ str('SE'))
                    else:
                        sito_folder2 =  '{}{}{}'.format(sito_path2, os.sep, self.comboBox_sito.currentText() +' - '+ str('SU'))    
                    
                    # Periodo_path = '{}{}{}'.format(sito_folder, os.sep, "Periodo")
                    # self.OS_UTILITY.create_dir(Periodo_path)
                    for sing_us in us_res2:
                        
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
                        if self.L=='it':
                            sing_US_path = ('%s%sUS - %s') % (sito_folder2 , os.sep, sing_us_dir)
                        elif self.L=='de':
                            sing_US_path = ('%s%sSE - %s') % (sito_folder2 , os.sep, sing_us_dir)
                        else:
                            sing_US_path = ('%s%sSU - %s') % (sito_folder2 , os.sep, sing_us_dir)    
                        
                        self.OS_UTILITY.create_dir(sing_US_path)

                        search_dict = {'id_entity': sing_us.id_us, 'entity_type': "'" + "US" + "'"}

                        u = Utility()
                        search_dict = u.remove_empty_items_fr_dict(search_dict)
                        search_images_res = self.DB_MANAGER.query_bool(search_dict, 'MEDIAVIEW')

                        for sing_media in search_images_res:
                            self.OS_UTILITY.copy_file_img(thumb_resize_str+str(sing_media.path_resize), sing_US_path)
                    
                        search_images_res = ""
                    if self.L=='it':
                        QMessageBox.warning(self, "Alert", "Creazione directories terminata", QMessageBox.Ok)
                    elif self.L=='de':
                        QMessageBox.warning(self, "Alert", "Verzeichniserstellung abgeschlossen", QMessageBox.Ok)
                    else:
                        QMessageBox.warning(self, "Alert", "Directory creation complete", QMessageBox.Ok)
            
            ############################Immagini reperti#################################################
            
            
            elif self.comboBox_export.currentIndex()==3:
                
                us_res3 = self.db_search_DB('INVENTARIO_MATERIALI', 'sito', sito)
                sito_path3 = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_image_export")
                self.OS_UTILITY.create_dir(sito_path3)
                if bool(us_res3):
                    if self.L=='it':
                        sito_folder3 =  '{}{}{}'.format(sito_path3, os.sep, self.comboBox_sito.currentText() +' - '+ str('RA'))
                    elif self.L=='de':
                        sito_folder3 =  '{}{}{}'.format(sito_path3, os.sep, self.comboBox_sito.currentText() +' - '+ str('EA'))
                    else:
                        sito_folder3 =  '{}{}{}'.format(sito_path3, os.sep, self.comboBox_sito.currentText() +' - '+ str('AA'))
                    for sing_us in us_res3:
                        
                        sing_us_num = str(sing_us.numero_inventario)
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
                        sing_US_path = ('%s%sRA - %s') % (sito_folder3 , os.sep, sing_us_dir)
                        self.OS_UTILITY.create_dir(sing_US_path)

                        search_dict = {'id_entity': sing_us.id_invmat, 'entity_type': "'" + "REPERTO" + "'"}

                        u = Utility()
                        search_dict = u.remove_empty_items_fr_dict(search_dict)
                        search_images_res = self.DB_MANAGER.query_bool(search_dict, 'MEDIAVIEW')

                        for sing_media in search_images_res:
                            self.OS_UTILITY.copy_file_img(thumb_resize_str+str(sing_media.path_resize), sing_US_path)
                    
                        search_images_res = ""
                    if self.L=='it':
                        QMessageBox.warning(self, "Alert", "Creazione directories terminata", QMessageBox.Ok)
                    elif self.L=='de':
                        QMessageBox.warning(self, "Alert", "Verzeichniserstellung abgeschlossen", QMessageBox.Ok)
                    else:
                        QMessageBox.warning(self, "Alert", "Directory creation complete", QMessageBox.Ok)
            
            elif self.comboBox_export.currentIndex()==4:
                
                us_res4 = self.db_search_DB('INVENTARIO_MATERIALI', 'sito', sito)
                sito_path4 = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_image_export")
                self.OS_UTILITY.create_dir(sito_path4)
                if bool(us_res4):
                    if self.L=='it':
                        sito_folder4 =  '{}{}{}'.format(sito_path4, os.sep, self.comboBox_sito.currentText() +' - '+ str('RA Definizione Materiali'))
                    elif self.L=='de':
                        sito_folder4 =  '{}{}{}'.format(sito_path4, os.sep, self.comboBox_sito.currentText() +' - '+ str('EA Materialdefinition'))
                    else:
                        sito_folder4 =  '{}{}{}'.format(sito_path4, os.sep, self.comboBox_sito.currentText() +' - '+ str('AA Material Definition'))
                    for sing_us in us_res4:
                        sing_per_num = str(sing_us.definizione)
                        
                        #sing_per_dir = prefix + str(sing_per_num)
                        sing_def_path = ('%s%sDefinizione - %s') % (sito_folder4, os.sep, sing_per_num)
                        self.OS_UTILITY.create_dir(sing_def_path)
                        
                        sing_us_num = str(sing_us.numero_inventario)
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
                        sing_US_path = ('%s%sRA - %s') % (sing_def_path , os.sep, sing_us_dir)
                        self.OS_UTILITY.create_dir(sing_US_path)

                        search_dict = {'id_entity': sing_us.id_invmat, 'entity_type': "'" + "REPERTO" + "'"}

                        u = Utility()
                        search_dict = u.remove_empty_items_fr_dict(search_dict)
                        search_images_res = self.DB_MANAGER.query_bool(search_dict, 'MEDIAVIEW')

                        for sing_media in search_images_res:
                            self.OS_UTILITY.copy_file_img(thumb_resize_str+str(sing_media.path_resize), sing_US_path)
                    
                        search_images_res = ""
                    if self.L=='it':
                        QMessageBox.warning(self, "Alert", "Creazione directories terminata", QMessageBox.Ok)
                    elif self.L=='de':
                        QMessageBox.warning(self, "Alert", "Verzeichniserstellung abgeschlossen", QMessageBox.Ok)
                    else:
                        QMessageBox.warning(self, "Alert", "Directory creation complete", QMessageBox.Ok)
           
            elif self.comboBox_export.currentIndex()==5:
                
                us_res5 = self.db_search_DB('INVENTARIO_MATERIALI', 'sito', sito)
                sito_path5 = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_image_export")
                self.OS_UTILITY.create_dir(sito_path5)
                if bool(us_res5):
                    if self.L=='it':
                        sito_folder5 =  '{}{}{}'.format(sito_path5, os.sep, self.comboBox_sito.currentText() +' - '+ str('RA Tipo Reperto'))
                    elif self.L=='de':
                        sito_folder5 =  '{}{}{}'.format(sito_path5, os.sep, self.comboBox_sito.currentText() +' - '+ str('EA Suchen Typ'))
                    else:
                        sito_folder5 =  '{}{}{}'.format(sito_path5, os.sep, self.comboBox_sito.currentText() +' - '+ str('AA Type Artefact'))
                    
                    for sing_us in us_res5:
                        sing_per_num = str(sing_us.definizione)
                        
                        if self.L=='it':
                            sing_def_path = ('%s%sDefinizione - %s') % (sito_folder5, os.sep, sing_per_num)
                        elif self.L=='de':
                            sing_def_path = ('%s%sDefinition - %s') % (sito_folder5, os.sep, sing_per_num)
                        else:
                            sing_def_path = ('%s%sDefinition - %s') % (sito_folder5, os.sep, sing_per_num)
                        
                        self.OS_UTILITY.create_dir(sing_def_path)
                        
                        
                        sing_tipo_num = str(sing_us.tipo_reperto)
                        
                        if self.L=='it':
                            sing_tipo_path = ('%s%sDefinizione - %s') % (sing_def_path , os.sep, sing_tipo_num)
                        elif self.L=='de':
                            sing_tipo_path = ('%s%sDefinition - %s') % (sing_def_path , os.sep, sing_tipo_num)
                        else:
                            sing_tipo_path = ('%s%sDefinition - %s') % (sing_def_path , os.sep, sing_tipo_num)    
                        self.OS_UTILITY.create_dir(sing_tipo_path)
                        
                        sing_us_num = str(sing_us.numero_inventario)
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
                        
                        if self.L=='it':
                            sing_US_path = ('%s%sRA - %s') % (sing_tipo_path , os.sep, sing_us_dir)
                        elif self.L=='de':
                            sing_US_path = ('%s%sEA - %s') % (sing_tipo_path , os.sep, sing_us_dir)
                        else:
                            sing_US_path = ('%s%sAA - %s') % (sing_tipo_path , os.sep, sing_us_dir)
                        self.OS_UTILITY.create_dir(sing_US_path)

                        search_dict = {'id_entity': sing_us.id_invmat, 'entity_type': "'" + "REPERTO" + "'"}

                        u = Utility()
                        search_dict = u.remove_empty_items_fr_dict(search_dict)
                        search_images_res = self.DB_MANAGER.query_bool(search_dict, 'MEDIAVIEW')

                        for sing_media in search_images_res:
                            self.OS_UTILITY.copy_file_img(thumb_resize_str+str(sing_media.path_resize), sing_US_path)
                    
                        search_images_res = ""
                    if self.L=='it':
                        QMessageBox.warning(self, "Alert", "Creazione directories terminata", QMessageBox.Ok)
                    elif self.L=='de':
                        QMessageBox.warning(self, "Alert", "Verzeichniserstellung abgeschlossen", QMessageBox.Ok)
                    else:
                        QMessageBox.warning(self, "Alert", "Directory creation complete", QMessageBox.Ok)
                
            
            #############################################immagini Tomba############################################
            elif self.comboBox_export.currentIndex()==6:
                
                us_res6 = self.db_search_DB('TOMBA', 'sito', sito)
                sito_path6 = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_image_export")
                self.OS_UTILITY.create_dir(sito_path6)
                if bool(us_res6):
                    if self.L=='it':
                        sito_folder6 =  '{}{}{}'.format(sito_path6, os.sep, self.comboBox_sito.currentText() +' - '+ str('TB'))
                    elif self.L=='de':
                        sito_folder6 =  '{}{}{}'.format(sito_path6, os.sep, self.comboBox_sito.currentText() +' - '+ str('Grab'))
                    else:
                        sito_folder6 =  '{}{}{}'.format(sito_path6, os.sep, self.comboBox_sito.currentText() +' - '+ str('Grave'))
                    for sing_us in us_res6:
                        
                        sing_us_num = str(sing_us.nr_scheda_taf)
                        prefix = '0'
                        sing_us_num_len = len(sing_us_num)
                        if sing_us_num_len == 1:
                            prefix = prefix * 1
                        else:
                            pass
                                           
                        sing_us_dir = prefix + str(sing_us_num)
                        if self.L=='it':
                            sing_US_path = ('%s%sTB - %s') % (sito_folder6 , os.sep, sing_us_dir)
                        elif self.L=='de':
                            sing_US_path = ('%s%sGrab - %s') % (sito_folder6 , os.sep, sing_us_dir)
                        else:
                            sing_US_path = ('%s%sGrave - %s') % (sito_folder6 , os.sep, sing_us_dir)
                        
                        self.OS_UTILITY.create_dir(sing_US_path)

                        search_dict = {'id_entity': sing_us.id_tomba, 'entity_type': "'" + "TOMBA" + "'"}

                        u = Utility()
                        search_dict = u.remove_empty_items_fr_dict(search_dict)
                        search_images_res = self.DB_MANAGER.query_bool(search_dict, 'MEDIAVIEW')

                        for sing_media in search_images_res:
                            self.OS_UTILITY.copy_file_img(thumb_resize_str+str(sing_media.path_resize), sing_US_path)
                    
                        search_images_res = ""
                if self.L=='it':
                    QMessageBox.warning(self, "Alert", "Creazione directories terminata", QMessageBox.Ok)
                elif self.L=='de':
                    QMessageBox.warning(self, "Alert", "Verzeichniserstellung abgeschlossen", QMessageBox.Ok)
                else:
                    QMessageBox.warning(self, "Alert", "Directory creation complete", QMessageBox.Ok)
            
            elif self.comboBox_export.currentIndex()==7:
                
                us_res7 = self.db_search_DB('TOMBA', 'sito', sito)
                sito_path7 = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_image_export")
                self.OS_UTILITY.create_dir(sito_path7)
                if bool(us_res7):
                    if self.L=='it':
                        sito_folder7 =  '{}{}{}'.format(sito_path7, os.sep, self.comboBox_sito.currentText() +' - '+ str('TB in periodi e fasi'))
                    elif self.L=='de':
                        sito_folder7 =  '{}{}{}'.format(sito_path7, os.sep, self.comboBox_sito.currentText() +' - '+ str('Grab in Perioden und Phasen'))
                    else:
                        sito_folder7 =  '{}{}{}'.format(sito_path7, os.sep, self.comboBox_sito.currentText() +' - '+ str('Grave in periods and phases'))
                    for sing_us in us_res7:
                        sing_per_num = str(sing_us.periodo_iniziale)
                        prefix = ''
                        sing_per_num_len = len(sing_per_num)
                        if sing_per_num_len == 1:
                            prefix = prefix * 1
                        
                        else:
                            pass
                        sing_per_dir = prefix + str(sing_per_num)
                        if self.L=='it':
                            sing_Periodo_path = ('%s%sPeriodo - %s') % (sito_folder7, os.sep, sing_per_dir)
                        elif self.L=='de':
                            sing_Periodo_path = ('%s%sPeriod - %s') % (sito_folder7, os.sep, sing_per_dir)
                        else:
                            sing_Periodo_path = ('%s%sPeriod - %s') % (sito_folder7, os.sep, sing_per_dir)
                        self.OS_UTILITY.create_dir(sing_Periodo_path)
                        
                        
                        
                        sing_fase_num = str(sing_us.fase_iniziale)
                        prefix = ''
                        sing_fase_num_len = len(sing_fase_num)
                        if sing_fase_num_len == 1:
                            prefix = prefix * 1
                        
                        else:
                            pass
                        sing_fase_dir = prefix + str(sing_fase_num)
                        if self.L=='it':
                            sing_Fase_path = ('%s%sFase - %s') % (sing_Periodo_path, os.sep, sing_fase_dir)
                        elif self.L=='de':
                            sing_Fase_path = ('%s%sPhase - %s') % (sing_Periodo_path, os.sep, sing_fase_dir)
                        else:
                            sing_Fase_path = ('%s%sPhase - %s') % (sing_Periodo_path, os.sep, sing_fase_dir)
                        self.OS_UTILITY.create_dir(sing_Fase_path)
                         
                        sing_us_num = str(sing_us.nr_scheda_taf)
                        prefix = '0'
                        sing_us_num_len = len(sing_us_num)
                        if sing_us_num_len == 1:
                            prefix = prefix * 1
                        else:
                            pass
                       
                        sing_us_dir = prefix + str(sing_us_num)
                        if self.L=='it':
                            sing_US_path = ('%s%sTB - %s') % (sing_Fase_path , os.sep, sing_us_dir)
                        elif self.L=='de':
                            sing_US_path = ('%s%sGrab - %s') % (sing_Fase_path , os.sep, sing_us_dir)
                        else:
                            sing_US_path = ('%s%sGrave - %s') % (sing_Fase_path , os.sep, sing_us_dir)
                        
                        self.OS_UTILITY.create_dir(sing_US_path)

                        search_dict = {'id_entity': sing_us.id_tomba, 'entity_type': "'" + "TOMBA" + "'"}

                        u = Utility()
                        search_dict = u.remove_empty_items_fr_dict(search_dict)
                        search_images_res = self.DB_MANAGER.query_bool(search_dict, 'MEDIAVIEW')

                        for sing_media in search_images_res:
                            self.OS_UTILITY.copy_file_img(thumb_resize_str+str(sing_media.path_resize), sing_US_path)
                    
                        search_images_res = ""
                    if self.L=='it':
                        QMessageBox.warning(self, "Alert", "Creazione directories terminata", QMessageBox.Ok)
                    elif self.L=='de':
                        QMessageBox.warning(self, "Alert", "Verzeichniserstellung abgeschlossen", QMessageBox.Ok)
                    else:
                        QMessageBox.warning(self, "Alert", "Directory creation complete", QMessageBox.Ok)
                
            
            ########################################Immagini strutture##################################################
           
            elif self.comboBox_export.currentIndex()==8:
                
                us_res8 = self.db_search_DB('STRUTTURA', 'sito', sito)
                sito_path8 = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_image_export")
                self.OS_UTILITY.create_dir(sito_path8)
                if bool(us_res8):
                    sito_folder8 =  '{}{}{}'.format(sito_path8, os.sep, self.comboBox_sito.currentText() +' - '+ str('ST'))
                    # Periodo_path = '{}{}{}'.format(sito_folder, os.sep, "Periodo")
                    # self.OS_UTILITY.create_dir(Periodo_path)
                    for sing_us in us_res8:
                        
                        sing_us_num = str(sing_us.sigla_struttura+str(sing_us.numero_struttura))
                        if self.L=='it':
                            sing_US_path = ('%s%sStruttura - %s') % (sito_folder8 , os.sep, sing_us_num)
                        elif self.L=='it':
                            sing_US_path = ('%s%sStrukturen - %s') % (sito_folder8 , os.sep, sing_us_num)
                        else:
                            sing_US_path = ('%s%sStructure - %s') % (sito_folder8 , os.sep, sing_us_num)
                        
                        self.OS_UTILITY.create_dir(sing_US_path)

                        search_dict = {'id_entity': sing_us.id_struttura, 'entity_type': "'" + "STRUTTURA" + "'"}

                        u = Utility()
                        search_dict = u.remove_empty_items_fr_dict(search_dict)
                        search_images_res = self.DB_MANAGER.query_bool(search_dict, 'MEDIAVIEW')

                        for sing_media in search_images_res:
                            try:
                                self.OS_UTILITY.copy_file_img(thumb_resize_str+str(sing_media.path_resize), sing_US_path)
                            except:
                                pass
                        search_images_res = ""
                    if self.L=='it':
                        QMessageBox.warning(self, "Alert", "Creazione directories terminata", QMessageBox.Ok)
                    elif self.L=='de':
                        QMessageBox.warning(self, "Alert", "Verzeichniserstellung abgeschlossen", QMessageBox.Ok)
                    else:
                        QMessageBox.warning(self, "Alert", "Directory creation complete", QMessageBox.Ok)
           
            elif self.comboBox_export.currentIndex()==9:
                
                us_res9 = self.db_search_DB('STRUTTURA', 'sito', sito)
                sito_path9 = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_image_export")
                self.OS_UTILITY.create_dir(sito_path9)
                if bool(us_res9):
                    if self.L=='it':
                    
                        sito_folder9 =  '{}{}{}'.format(sito_path9, os.sep, self.comboBox_sito.currentText() +' - '+ str('ST in periodi e fasi'))
                    elif self.L=='de':
                    
                        sito_folder9 =  '{}{}{}'.format(sito_path9, os.sep, self.comboBox_sito.currentText() +' - '+ str('ST in Perioden un Phasen'))
                        
                    else:
                    
                        sito_folder9 =  '{}{}{}'.format(sito_path9, os.sep, self.comboBox_sito.currentText() +' - '+ str('ST in periods and phases'))    
                    for sing_us in us_res9:
                        sing_per_num = str(sing_us.periodo_iniziale)
                        prefix = ''
                        sing_per_num_len = len(sing_per_num)
                        if sing_per_num_len == 1:
                            prefix = prefix * 1
                        
                        else:
                            pass
                        sing_per_dir = prefix + str(sing_per_num)
                        if self.L=='it':
                            sing_Periodo_path = ('%s%sPeriodo - %s') % (sito_folder9, os.sep, sing_per_dir)
                        elif self.L=='de':
                            sing_Periodo_path = ('%s%sPeriod - %s') % (sito_folder9, os.sep, sing_per_dir)
                        else:
                            sing_Periodo_path = ('%s%sPeriod - %s') % (sito_folder9, os.sep, sing_per_dir)
                        self.OS_UTILITY.create_dir(sing_Periodo_path)
                        
                        
                        
                        sing_fase_num = str(sing_us.fase_iniziale)
                        prefix = ''
                        sing_fase_num_len = len(sing_fase_num)
                        if sing_fase_num_len == 1:
                            prefix = prefix * 1
                        
                        else:
                            pass
                        sing_fase_dir = prefix + str(sing_fase_num)
                        if self.L=='it':
                            sing_Fase_path = ('%s%sFase - %s') % (sing_Periodo_path, os.sep, sing_fase_dir)
                        elif self.L=='de':
                            sing_Fase_path = ('%s%sPhase - %s') % (sing_Periodo_path, os.sep, sing_fase_dir)
                        else:
                            sing_Fase_path = ('%s%sPhase - %s') % (sing_Periodo_path, os.sep, sing_fase_dir)
                        self.OS_UTILITY.create_dir(sing_Fase_path)
                           
                        sing_us_num = str(sing_us.sigla_struttura+str(sing_us.numero_struttura))
                            
                        sing_us_dir = prefix + str(sing_us_num)
                        sing_US_path = ('%s%sStruttura - %s') % (sing_Fase_path , os.sep, sing_us_num)
                        self.OS_UTILITY.create_dir(sing_US_path)

                        search_dict = {'id_entity': sing_us.id_struttura, 'entity_type': "'" + "STRUTTURA" + "'"}

                        u = Utility()
                        search_dict = u.remove_empty_items_fr_dict(search_dict)
                        search_images_res = self.DB_MANAGER.query_bool(search_dict, 'MEDIAVIEW')

                        for sing_media in search_images_res:
                            try:
                                self.OS_UTILITY.copy_file_img(thumb_resize_str+str(sing_media.path_resize), sing_US_path)
                            except:
                                pass
                        search_images_res = ""
                    if self.L=='it':
                        QMessageBox.warning(self, "Alert", "Creazione directories terminata", QMessageBox.Ok)
                    elif self.L=='de':
                        QMessageBox.warning(self, "Alert", "Verzeichniserstellung abgeschlossen", QMessageBox.Ok)
                    else:
                        QMessageBox.warning(self, "Alert", "Directory creation complete", QMessageBox.Ok)
        
        except Exception as e:
            if self.L=='it':
                QMessageBox.warning(self, "Attenzione", " Priodo iniziale o fase iniziale mancante. Ricontrolla", QMessageBox.Ok)
            elif self.L=='de':
                QMessageBox.warning(self, "Achtung", str(e), QMessageBox.Ok)
            elif self.L=='en':   
                QMessageBox.warning(self, "Attention", str(e), QMessageBox.Ok)
    def db_search_DB(self, table_class, field, value):
        self.table_class = table_class
        self.field = field
        self.value = value

        search_dict = {self.field: "'" + str(self.value) + "'"}

        u = Utility()
        search_dict = u.remove_empty_items_fr_dict(search_dict)

        res = self.DB_MANAGER.query_bool(search_dict, self.table_class)

        return res


# if __name__ == '__main__':
    # app = QApplication(sys.argv)
    # ui = pyArchInitDialog_Config()
    # ui.show()
    # sys.exit(app.exec_())
