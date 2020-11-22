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
        if self.comboBox_export.currentText()=='Tutte le immagini \ in periodi e fasi':
            
            us_res = self.db_search_DB('US', 'sito', sito)
            sito_path = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_image_export")
            self.OS_UTILITY.create_dir(sito_path)
            if bool(us_res):
                sito_folder =  '{}{}{}'.format(sito_path, os.sep, self.comboBox_sito.currentText() +' - '+ str('Tutte le immagini'))
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
                    sing_Periodo_path = ('%s%sPeriodo - %s') % (sito_folder, os.sep, sing_per_dir)
                    self.OS_UTILITY.create_dir(sing_Periodo_path)
                    
                    
                    
                    sing_fase_num = str(sing_us.fase_iniziale)
                    prefix = ''
                    sing_fase_num_len = len(sing_fase_num)
                    if sing_fase_num_len == 1:
                        prefix = prefix * 1
                    
                    else:
                        pass
                    sing_fase_dir = prefix + str(sing_fase_num)
                    sing_Fase_path = ('%s%sFase - %s') % (sing_Periodo_path, os.sep, sing_fase_dir)
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
                    sing_US_path = ('%s%sUS - %s') % (sing_Fase_path , os.sep, sing_us_dir)
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
                        sing_Periodo_path = ('%s%sPeriodo - %s') % (sito_folder, os.sep, sing_per_dir)
                        self.OS_UTILITY.create_dir(sing_Periodo_path)
                        
                        
                        
                        sing_fase_num = str(sing_us.us)
                        prefix = ''
                        sing_fase_num_len = len(sing_fase_num)
                        if sing_fase_num_len == 1:
                            prefix = prefix * 1
                        
                        else:
                            pass
                        sing_fase_dir = prefix + str(sing_fase_num)
                        sing_Fase_path = ('%s%sFase - %s') % (sing_Periodo_path, os.sep, sing_fase_dir)
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
                        sing_REPERTI_path = ('%s%sRA - %s') % (sing_Fase_path, os.sep, sing_reperti_dir)
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
                        sing_Periodo_path = ('%s%sPeriodo - %s') % (sito_folder, os.sep, sing_per_dir)
                        self.OS_UTILITY.create_dir(sing_Periodo_path)
                        
                        
                        
                        sing_fase_num = str(sing_t.fase_iniziale)
                        prefix = ''
                        sing_fase_num_len = len(sing_fase_num)
                        if sing_fase_num_len == 1:
                            prefix = prefix * 1
                        
                        else:
                            pass
                        sing_fase_dir = prefix + str(sing_fase_num)
                        sing_Fase_path = ('%s%sFase - %s') % (sing_Periodo_path, os.sep, sing_fase_dir)
                        self.OS_UTILITY.create_dir(sing_Fase_path)
                        
                        sing_tomba_num = str(sing_t.nr_scheda_taf)
                        prefix = '0'
                        sing_tomba_num_len = len(sing_tomba_num)
                        if sing_tomba_num_len == 1:
                            prefix = prefix * 4
                        elif sing_tomba_num_len == 2:
                            prefix = prefix * 3
                        elif sing_tomba_num_len == 3:
                            prefix = prefix * 2
                        else:
                            pass

                        sing_tomba_dir = prefix + str(sing_tomba_num)
                        sing_TOMBA_path = ('%s%sTB - %s') % (sing_Fase_path, os.sep, sing_tomba_dir)
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
                        sing_Periodo_path = ('%s%sPeriodo - %s') % (sito_folder, os.sep, sing_per_dir)
                        self.OS_UTILITY.create_dir(sing_Periodo_path)
                        
                        
                        
                        sing_fase_num = str(sing_s.fase_iniziale)
                        prefix = ''
                        sing_fase_num_len = len(sing_fase_num)
                        if sing_fase_num_len == 1:
                            prefix = prefix * 1
                        
                        else:
                            pass
                        sing_fase_dir = prefix + str(sing_fase_num)
                        sing_Fase_path = ('%s%sFase - %s') % (sing_Periodo_path, os.sep, sing_fase_dir)
                        self.OS_UTILITY.create_dir(sing_Fase_path)
                            
                            
                            
                        sing_us_num = str(sing_s.sigla_struttura+str(sing_s.numero_struttura))
                        
                        
                        
                        sing_us_dir = prefix + str(sing_us_num)
                        sing_US_path = ('%s%sStruttura - %s') % (sing_Fase_path , os.sep, sing_us_num)
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
                QMessageBox.warning(self, "Alert", "Creazione directories terminata", QMessageBox.Ok)
                
        
        if self.comboBox_export.currentText()=='US / in periodi e fasi':
            
            us_res = self.db_search_DB('US', 'sito', sito)
            sito_path = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_image_export")
            self.OS_UTILITY.create_dir(sito_path)
            if bool(us_res):
                sito_folder =  '{}{}{}'.format(sito_path, os.sep, self.comboBox_sito.currentText() +' - '+ str('US in periodi e fasi'))
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
                    sing_Periodo_path = ('%s%sPeriodo - %s') % (sito_folder, os.sep, sing_per_dir)
                    self.OS_UTILITY.create_dir(sing_Periodo_path)
                    
                    
                    
                    sing_fase_num = str(sing_us.fase_iniziale)
                    prefix = ''
                    sing_fase_num_len = len(sing_fase_num)
                    if sing_fase_num_len == 1:
                        prefix = prefix * 1
                    
                    else:
                        pass
                    sing_fase_dir = prefix + str(sing_fase_num)
                    sing_Fase_path = ('%s%sFase - %s') % (sing_Periodo_path, os.sep, sing_fase_dir)
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
                    sing_US_path = ('%s%sUS - %s') % (sing_Fase_path , os.sep, sing_us_dir)
                    self.OS_UTILITY.create_dir(sing_US_path)

                    search_dict = {'id_entity': sing_us.id_us, 'entity_type': "'" + "US" + "'"}

                    u = Utility()
                    search_dict = u.remove_empty_items_fr_dict(search_dict)
                    search_images_res = self.DB_MANAGER.query_bool(search_dict, 'MEDIAVIEW')

                    for sing_media in search_images_res:
                        self.OS_UTILITY.copy_file_img(thumb_resize_str+str(sing_media.path_resize), sing_US_path)
                
                    search_images_res = ""
            QMessageBox.warning(self, "Alert", "Creazione directories terminata", QMessageBox.Ok)
        if self.comboBox_export.currentText()=='US':
            
            us_res = self.db_search_DB('US', 'sito', sito)
            sito_path = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_image_export")
            self.OS_UTILITY.create_dir(sito_path)
            if bool(us_res):
                sito_folder =  '{}{}{}'.format(sito_path, os.sep, self.comboBox_sito.currentText() +' - '+ str('US'))
                # Periodo_path = '{}{}{}'.format(sito_folder, os.sep, "Periodo")
                # self.OS_UTILITY.create_dir(Periodo_path)
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
                    sing_US_path = ('%s%sUS - %s') % (sito_folder , os.sep, sing_us_dir)
                    self.OS_UTILITY.create_dir(sing_US_path)

                    search_dict = {'id_entity': sing_us.id_us, 'entity_type': "'" + "US" + "'"}

                    u = Utility()
                    search_dict = u.remove_empty_items_fr_dict(search_dict)
                    search_images_res = self.DB_MANAGER.query_bool(search_dict, 'MEDIAVIEW')

                    for sing_media in search_images_res:
                        self.OS_UTILITY.copy_file_img(thumb_resize_str+str(sing_media.path_resize), sing_US_path)
                
                    search_images_res = ""
            QMessageBox.warning(self, "Alert", "Creazione directories terminata", QMessageBox.Ok)
        if self.comboBox_export.currentText()=='Reperti':
            
            us_res = self.db_search_DB('INVENTARIO_MATERIALI', 'sito', sito)
            sito_path = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_image_export")
            self.OS_UTILITY.create_dir(sito_path)
            if bool(us_res):
                sito_folder =  '{}{}{}'.format(sito_path, os.sep, self.comboBox_sito.currentText() +' - '+ str('RA'))
                # Periodo_path = '{}{}{}'.format(sito_folder, os.sep, "Periodo")
                # self.OS_UTILITY.create_dir(Periodo_path)
                for sing_us in us_res:
                    
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
                    sing_US_path = ('%s%sRA - %s') % (sito_folder , os.sep, sing_us_dir)
                    self.OS_UTILITY.create_dir(sing_US_path)

                    search_dict = {'id_entity': sing_us.id_invmat, 'entity_type': "'" + "REPERTO" + "'"}

                    u = Utility()
                    search_dict = u.remove_empty_items_fr_dict(search_dict)
                    search_images_res = self.DB_MANAGER.query_bool(search_dict, 'MEDIAVIEW')

                    for sing_media in search_images_res:
                        self.OS_UTILITY.copy_file_img(thumb_resize_str+str(sing_media.path_resize), sing_US_path)
                
                    search_images_res = ""
            QMessageBox.warning(self, "Alert", "Creazione directories terminata", QMessageBox.Ok)
        
        if self.comboBox_export.currentText()=='Reperti \ in Definizione materiali':
            
            us_res = self.db_search_DB('INVENTARIO_MATERIALI', 'sito', sito)
            sito_path = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_image_export")
            self.OS_UTILITY.create_dir(sito_path)
            if bool(us_res):
                sito_folder =  '{}{}{}'.format(sito_path, os.sep, self.comboBox_sito.currentText() +' - '+ str('RA Definizione Materiali'))
                # Periodo_path = '{}{}{}'.format(sito_folder, os.sep, "Periodo")
                # self.OS_UTILITY.create_dir(Periodo_path)
                for sing_us in us_res:
                    sing_per_num = str(sing_us.definizione)
                    
                    #sing_per_dir = prefix + str(sing_per_num)
                    sing_def_path = ('%s%sDefinizione - %s') % (sito_folder, os.sep, sing_per_num)
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
            QMessageBox.warning(self, "Alert", "Creazione directories terminata", QMessageBox.Ok)
        
        if self.comboBox_export.currentText()=='Reperti \ in Tipo reperto':
            
            us_res = self.db_search_DB('INVENTARIO_MATERIALI', 'sito', sito)
            sito_path = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_image_export")
            self.OS_UTILITY.create_dir(sito_path)
            if bool(us_res):
                sito_folder =  '{}{}{}'.format(sito_path, os.sep, self.comboBox_sito.currentText() +' - '+ str('RA Tipo Reperto'))
                # Periodo_path = '{}{}{}'.format(sito_folder, os.sep, "Periodo")
                # self.OS_UTILITY.create_dir(Periodo_path)
                for sing_us in us_res:
                    sing_per_num = str(sing_us.definizione)
                    
                    #sing_per_dir = prefix + str(sing_per_num)
                    sing_def_path = ('%s%sDefinizione - %s') % (sito_folder, os.sep, sing_per_num)
                    self.OS_UTILITY.create_dir(sing_def_path)
                    
                    
                    sing_tipo_num = str(sing_us.tipo_reperto)
                    
                    #sing_per_dir = prefix + str(sing_per_num)
                    sing_tipo_path = ('%s%sDefinizione - %s') % (sing_def_path , os.sep, sing_tipo_num)
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
                    sing_US_path = ('%s%sRA - %s') % (sing_tipo_path , os.sep, sing_us_dir)
                    self.OS_UTILITY.create_dir(sing_US_path)

                    search_dict = {'id_entity': sing_us.id_invmat, 'entity_type': "'" + "REPERTO" + "'"}

                    u = Utility()
                    search_dict = u.remove_empty_items_fr_dict(search_dict)
                    search_images_res = self.DB_MANAGER.query_bool(search_dict, 'MEDIAVIEW')

                    for sing_media in search_images_res:
                        self.OS_UTILITY.copy_file_img(thumb_resize_str+str(sing_media.path_resize), sing_US_path)
                
                    search_images_res = ""
            QMessageBox.warning(self, "Alert", "Creazione directories terminata", QMessageBox.Ok)
        
        if self.comboBox_export.currentText()=='Tomba':
            
            us_res = self.db_search_DB('TOMBA', 'sito', sito)
            sito_path = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_image_export")
            self.OS_UTILITY.create_dir(sito_path)
            if bool(us_res):
                sito_folder =  '{}{}{}'.format(sito_path, os.sep, self.comboBox_sito.currentText() +' - '+ str('TB'))
                # Periodo_path = '{}{}{}'.format(sito_folder, os.sep, "Periodo")
                # self.OS_UTILITY.create_dir(Periodo_path)
                for sing_us in us_res:
                    
                    sing_us_num = str(sing_us.nr_scheda_taf)
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
                    sing_US_path = ('%s%sTB - %s') % (sito_folder , os.sep, sing_us_dir)
                    self.OS_UTILITY.create_dir(sing_US_path)

                    search_dict = {'id_entity': sing_us.id_tomba, 'entity_type': "'" + "TOMBA" + "'"}

                    u = Utility()
                    search_dict = u.remove_empty_items_fr_dict(search_dict)
                    search_images_res = self.DB_MANAGER.query_bool(search_dict, 'MEDIAVIEW')

                    for sing_media in search_images_res:
                        self.OS_UTILITY.copy_file_img(thumb_resize_str+str(sing_media.path_resize), sing_US_path)
                
                    search_images_res = ""
            QMessageBox.warning(self, "Alert", "Creazione directories terminata", QMessageBox.Ok)
        
        if self.comboBox_export.currentText()=='Tomba / in periodi e fasi':
            
            us_res = self.db_search_DB('TOMBA', 'sito', sito)
            sito_path = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_image_export")
            self.OS_UTILITY.create_dir(sito_path)
            if bool(us_res):
                sito_folder =  '{}{}{}'.format(sito_path, os.sep, self.comboBox_sito.currentText() +' - '+ str('TB in periodi e fasi'))
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
                    sing_Periodo_path = ('%s%sPeriodo - %s') % (sito_folder, os.sep, sing_per_dir)
                    self.OS_UTILITY.create_dir(sing_Periodo_path)
                    
                    
                    
                    sing_fase_num = str(sing_us.fase_iniziale)
                    prefix = ''
                    sing_fase_num_len = len(sing_fase_num)
                    if sing_fase_num_len == 1:
                        prefix = prefix * 1
                    
                    else:
                        pass
                    sing_fase_dir = prefix + str(sing_fase_num)
                    sing_Fase_path = ('%s%sFase - %s') % (sing_Periodo_path, os.sep, sing_fase_dir)
                    self.OS_UTILITY.create_dir(sing_Fase_path)
                        
                        
                        
                    sing_us_num = str(sing_us.nr_scheda_taf)
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
                    sing_US_path = ('%s%sTB - %s') % (sing_Fase_path , os.sep, sing_us_dir)
                    self.OS_UTILITY.create_dir(sing_US_path)

                    search_dict = {'id_entity': sing_us.id_tomba, 'entity_type': "'" + "TOMBA" + "'"}

                    u = Utility()
                    search_dict = u.remove_empty_items_fr_dict(search_dict)
                    search_images_res = self.DB_MANAGER.query_bool(search_dict, 'MEDIAVIEW')

                    for sing_media in search_images_res:
                        self.OS_UTILITY.copy_file_img(thumb_resize_str+str(sing_media.path_resize), sing_US_path)
                
                    search_images_res = ""
            QMessageBox.warning(self, "Alert", "Creazione directories terminata", QMessageBox.Ok)
        
        
        
        
        
        if self.comboBox_export.currentText()=='Strutture':
            
            us_res = self.db_search_DB('STRUTTURA', 'sito', sito)
            sito_path = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_image_export")
            self.OS_UTILITY.create_dir(sito_path)
            if bool(us_res):
                sito_folder =  '{}{}{}'.format(sito_path, os.sep, self.comboBox_sito.currentText() +' - '+ str('ST'))
                # Periodo_path = '{}{}{}'.format(sito_folder, os.sep, "Periodo")
                # self.OS_UTILITY.create_dir(Periodo_path)
                for sing_us in us_res:
                    
                    sing_us_num = str(sing_us.sigla_struttura+str(sing_us.numero_struttura))
                        
                        
                        
                    
                    sing_US_path = ('%s%sStruttura - %s') % (sito_folder , os.sep, sing_us_num)
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
            QMessageBox.warning(self, "Alert", "Creazione directories terminata", QMessageBox.Ok)
        
        if self.comboBox_export.currentText()=='Strutture / in periodi e fasi':
            
            us_res = self.db_search_DB('STRUTTURA', 'sito', sito)
            sito_path = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_image_export")
            self.OS_UTILITY.create_dir(sito_path)
            if bool(us_res):
                sito_folder =  '{}{}{}'.format(sito_path, os.sep, self.comboBox_sito.currentText() +' - '+ str('ST in periodi e fasi'))
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
                    sing_Periodo_path = ('%s%sPeriodo - %s') % (sito_folder, os.sep, sing_per_dir)
                    self.OS_UTILITY.create_dir(sing_Periodo_path)
                    
                    
                    
                    sing_fase_num = str(sing_us.fase_iniziale)
                    prefix = ''
                    sing_fase_num_len = len(sing_fase_num)
                    if sing_fase_num_len == 1:
                        prefix = prefix * 1
                    
                    else:
                        pass
                    sing_fase_dir = prefix + str(sing_fase_num)
                    sing_Fase_path = ('%s%sFase - %s') % (sing_Periodo_path, os.sep, sing_fase_dir)
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
            QMessageBox.warning(self, "Alert", "Creazione directories terminata", QMessageBox.Ok)
        
        
        
        
        
        
        # if self.checkBox_US.isChecked()== True:
            # us_res = self.db_search_DB('US', 'sito', sito)
            # sito_path = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_image_export")
            # self.OS_UTILITY.create_dir(sito_path)
            
            # if bool(us_res)== True:
                # sito_folder =  '{}{}{}'.format(sito_path, os.sep, self.comboBox_sito.currentText())
                # US_path = '{}{}{}'.format(sito_folder, os.sep, "Unita_Stratigrafiche")
                # self.OS_UTILITY.create_dir(US_path)
                # for sing_us in us_res:
                    # sing_us_num = str(sing_us.us)
                    # prefix = '0'
                    # sing_us_num_len = len(sing_us_num)
                    # if sing_us_num_len == 1:
                        # prefix = prefix * 4
                    # elif sing_us_num_len == 2:
                        # prefix = prefix * 3
                    # elif sing_us_num_len == 3:
                        # prefix = prefix * 2
                    # else:
                        # pass

                    # sing_us_dir = prefix + str(sing_us_num)
                    # sing_US_path = ('%s%sUS%s') % (US_path, os.sep, sing_us_dir)
                    # self.OS_UTILITY.create_dir(sing_US_path)

                    # search_dict = {'id_entity': sing_us.id_us, 'entity_type': "'" + "US" + "'"}

                    # u = Utility()
                    # search_dict = u.remove_empty_items_fr_dict(search_dict)
                    # search_images_res = self.DB_MANAGER.query_bool(search_dict, 'MEDIAVIEW')

                    # for sing_media in search_images_res:
                        # self.OS_UTILITY.copy_file_img(thumb_resize_str+str(sing_media.path_resize), sing_US_path)
                    # ##                      QMessageBox.warning(self, "Alert", str(sing_media.filepath),  QMessageBox.Ok)
                    # ##                      QMessageBox.warning(self, "Alert", str(sing_US_path),  QMessageBox.Ok)

                    # search_images_res = ""
                # QMessageBox.warning(self, "Alert", "Creazione directories terminata", QMessageBox.Ok)
        # if self.checkBox_periodo.isChecked():
            # us_res = self.db_search_DB('US', 'sito', sito)
            # sito_path = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_image_export")
            # self.OS_UTILITY.create_dir(sito_path)
            
            # if bool(us_res)== True:
                # sito_folder =  '{}{}{}'.format(sito_path, os.sep, self.comboBox_sito.currentText())
                # US_path = '{}{}{}'.format(sito_folder, os.sep, "Unita_Stratigrafiche")
                # US_P_path = '{}{}{}'.format(US_path, os.sep, "Periodo")
                # self.OS_UTILITY.create_dir(US_P_path)
                # for sing_us in us_res:
                    # sing_us_num = str(sing_us.periodo_iniziale)
                    # prefix = '0'
                    # sing_us_num_len = len(sing_us_num)
                    # if sing_us_num_len == 1:
                        # prefix = prefix * 1
                    
                    # else:
                        # pass

                    # sing_us_dir = prefix + str(sing_us_num)
                    # sing_US_P_path = ('%s%sPeriodo%s') % (US_P_path, os.sep, sing_us_dir)
                    # self.OS_UTILITY.create_dir(sing_US_P_path)

                    # search_dict = {'id_entity': sing_us.id_us, 'entity_type': "'" + "US" + "'"}

                    # u = Utility()
                    # search_dict = u.remove_empty_items_fr_dict(search_dict)
                    # search_images_res = self.DB_MANAGER.query_bool(search_dict, 'MEDIAVIEW')

                    # for sing_media in search_images_res:
                        # self.OS_UTILITY.copy_file_img(thumb_resize_str+str(sing_media.path_resize), sing_US_P_path)
                    # ##                      QMessageBox.warning(self, "Alert", str(sing_media.filepath),  QMessageBox.Ok)
                    # ##                      QMessageBox.warning(self, "Alert", str(sing_US_path),  QMessageBox.Ok)

                    # search_images_res = ""
                # QMessageBox.warning(self, "Alert", "Creazione directories terminata", QMessageBox.Ok)
        
        
        # if self.checkBox_fase.isChecked():
            # us_res = self.db_search_DB('US', 'sito', sito)
            # sito_path = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_image_export")
            # self.OS_UTILITY.create_dir(sito_path)
            
            # if bool(us_res)== True:
                # sito_folder =  '{}{}{}'.format(sito_path, os.sep, self.comboBox_sito.currentText())
                # US_path = '{}{}{}'.format(sito_folder, os.sep, "Unita_Stratigrafiche")
                # US_P_path = '{}{}{}'.format(US_path, os.sep, "Periodo")
                # US_F_path = '{}{}{}'.format(US_P_path, os.sep, "Fase")
                # self.OS_UTILITY.create_dir(US_F_path)
                # for sing_us in us_res:
                    # sing_us_num = str(sing_us.fase_iniziale)
                    # prefix = '0'
                    # sing_us_num_len = len(sing_us_num)
                    # if sing_us_num_len == 1:
                        # prefix = prefix * 1
                    
                    # else:
                        # pass

                    # sing_us_dir = prefix + str(sing_us_num)
                    # sing_US_F_path = ('%s%sFase%s') % (US_F_path, os.sep, sing_us_dir)
                    # self.OS_UTILITY.create_dir(sing_US_F_path)

                    # search_dict = {'id_entity': sing_us.id_us, 'entity_type': "'" + "US" + "'"}

                    # u = Utility()
                    # search_dict = u.remove_empty_items_fr_dict(search_dict)
                    # search_images_res = self.DB_MANAGER.query_bool(search_dict, 'MEDIAVIEW')

                    # for sing_media in search_images_res:
                        # self.OS_UTILITY.copy_file_img(thumb_resize_str+str(sing_media.path_resize), sing_US_F_path)
                    # ##                      QMessageBox.warning(self, "Alert", str(sing_media.filepath),  QMessageBox.Ok)
                    # ##                      QMessageBox.warning(self, "Alert", str(sing_US_path),  QMessageBox.Ok)

                    # search_images_res = ""
                # QMessageBox.warning(self, "Alert", "Creazione directories terminata", QMessageBox.Ok)
        # if self.checkBox_reperti.isChecked()== True:
            # reperti_res = self.db_search_DB('INVENTARIO_MATERIALI', 'sito', sito)
            # sito_path = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_image_export")
            # self.OS_UTILITY.create_dir(sito_path)
            # if bool(reperti_res)== True:
                # REPERTI_path = '{}{}{}'.format(sito_path, os.sep, "REPERTI")
                # self.OS_UTILITY.create_dir(REPERTI_path)
                # for sing_reperti in reperti_res:
                    # sing_reperti_num = str(sing_reperti.numero_inventario)
                    # prefix = '0'
                    # sing_reperti_num_len = len(sing_reperti_num)
                    # if sing_reperti_num_len == 1:
                        # prefix = prefix * 4
                    # elif sing_reperti_num_len == 2:
                        # prefix = prefix * 3
                    # elif sing_reperti_num_len == 3:
                        # prefix = prefix * 2
                    # else:
                        # pass

                    # sing_reperti_dir = prefix + str(sing_reperti_num)
                    # sing_REPERTI_path = ('%s%sREPERTI%s') % (REPERTI_path, os.sep, sing_reperti_dir)
                    # self.OS_UTILITY.create_dir(sing_REPERTI_path)

                    # search_dict = {'id_entity': sing_reperti.id_invmat, 'entity_type': "'" + "REPERTO" + "'"}

                    # u = Utility()
                    # search_dict = u.remove_empty_items_fr_dict(search_dict)
                    # search_images_res = self.DB_MANAGER.query_bool(search_dict, 'MEDIAVIEW')

                    # for sing_media in search_images_res:
                        # self.OS_UTILITY.copy_file_img(thumb_resize_str+str(sing_media.path_resize), sing_REPERTI_path)
                    # ##                      QMessageBox.warning(self, "Alert", str(sing_media.filepath),  QMessageBox.Ok)
                    # ##                      QMessageBox.warning(self, "Alert", str(sing_US_path),  QMessageBox.Ok)

                    # search_images_res = ""
                # QMessageBox.warning(self, "Alert", "Creazione directories terminata", QMessageBox.Ok)
        # if self.checkBox_tomba.isChecked()== True:
            # tomba_res = self.db_search_DB('TOMBA', 'sito', sito)
            # sito_path = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_image_export")
            # self.OS_UTILITY.create_dir(sito_path)
            # if bool(tomba_res)== True:
                # TOMBA_path = '{}{}{}'.format(sito_path, os.sep, "TOMBA")
                # self.OS_UTILITY.create_dir(TOMBA_path)
                # for sing_tomba in tomba_res:
                    # sing_tomba_num = str(sing_tomba.nr_scheda_taf)
                    # prefix = '0'
                    # sing_tomba_num_len = len(sing_tomba_num)
                    # if sing_tomba_num_len == 1:
                        # prefix = prefix * 4
                    # elif sing_tomba_num_len == 2:
                        # prefix = prefix * 3
                    # elif sing_tomba_num_len == 3:
                        # prefix = prefix * 2
                    # else:
                        # pass

                    # sing_tomba_dir = prefix + str(sing_tomba_num)
                    # sing_TOMBA_path = ('%s%sTOMBA%s') % (TOMBA_path, os.sep, sing_tomba_dir)
                    # self.OS_UTILITY.create_dir(sing_TOMBA_path)

                    # search_dict = {'id_entity': sing_reperti.id_invmat, 'entity_type': "'" + "TOMBA" + "'"}

                    # u = Utility()
                    # search_dict = u.remove_empty_items_fr_dict(search_dict)
                    # search_images_res = self.DB_MANAGER.query_bool(search_dict, 'MEDIAVIEW')

                    # for sing_media in search_images_res:
                        # self.OS_UTILITY.copy_file_img(thumb_resize_str+str(sing_media.path_resize), sing_TOMBA_path)
                    # ##                      QMessageBox.warning(self, "Alert", str(sing_media.filepath),  QMessageBox.Ok)
                    # ##                      QMessageBox.warning(self, "Alert", str(sing_US_path),  QMessageBox.Ok)

                    # search_images_res = ""
                # QMessageBox.warning(self, "Alert", "Creazione directories terminata", QMessageBox.Ok)
    
    
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
