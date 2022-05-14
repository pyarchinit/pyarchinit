#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
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
'''
from __future__ import absolute_import
import os
from os import *
import time
import sys
from builtins import range
from builtins import str
import PIL as Image
from PIL import *
import shutil

import platform
import cv2
import pytesseract
import numpy as np
#####################nuovi#######################
from PIL import ImageGrab
import time
from pytesseract import Output
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'# funziona meglio 
###############################
from qgis import PyQt
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.uic import loadUiType
from qgis.core import QgsSettings
from ..gui.pyarchinitConfigDialog import pyArchInitDialog_Config
from ..gui.imageViewer import ImageViewer
from ..gui.sortpanelmain import SortPanelMain
from ..modules.utility.delegateComboBox import ComboBoxDelegate
from ..modules.db.pyarchinit_conn_strings import *
from ..modules.db.pyarchinit_db_manager import *
from ..modules.db.pyarchinit_utility import *
from ..modules.utility.pyarchinit_media_utility import *
MAIN_DIALOG_CLASS, _ = loadUiType(
    os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'pyarchinit_image_viewer_dialog.ui'))
conn = Connection()
class Main(QDialog,MAIN_DIALOG_CLASS):
    L=QgsSettings().value("locale/userLocale")[0:2]
    delegateSites = ''
    DB_MANAGER = ""
    TABLE_NAME = 'media_table'
    MAPPER_TABLE_CLASS = "MEDIA"
    ID_TABLE = "id_media"
    MAPPER_TABLE_CLASS_mediatoentity = "MEDIATOENTITY"
    ID_TABLE_mediatoentity = "id_mediaToEntity"
    MAPPER_TABLE_CLASS_us = 'US'
    ID_TABLE_US = "id_us"
    MAPPER_TABLE_CLASS_mat = 'INVENTARIO_MATERIALI'
    ID_TABLE_MAT = "id_invmat"
    NOME_SCHEDA = "Scheda Media Manager"
    TABLE_THUMB_NAME = 'media_thumb_table'
    MAPPER_TABLE_CLASS_thumb = 'MEDIA_THUMB'
    ID_TABLE_THUMB = "id_media_thumb"
    LEGGO = ''
    DATA_LIST = []
    DATA_LIST_REC_CORR = []
    DATA_LIST_REC_TEMP = []
    REC_CORR = 0
    REC_TOT = 0
    if L=='it':
        STATUS_ITEMS = {"b": "Usa", "f": "Trova", "n": "Nuovo Record"}
    
    elif L=='de':
        STATUS_ITEMS = {"b": "Aktuell ", "f": "Finden", "n": "Neuer Rekord"}
    
    else :
        STATUS_ITEMS = {"b": "Current", "f": "Find", "n": "New Record"}
    BROWSE_STATUS = "b"
    SORT_MODE = 'asc'
    if L=='it':
        SORTED_ITEMS = {"n": "Non ordinati", "o": "Ordinati"}
    elif L=='de':
        SORTED_ITEMS = {"n": "Nicht sortiert", "o": "Sortiert"}
    else:
        SORTED_ITEMS = {"n": "Not sorted", "o": "Sorted"}
    SORT_STATUS = "n"
    UTILITY = Utility()
    DATA = ''
    NUM_DATA_BEGIN = 0
    NUM_DATA_END = 25
    CONVERSION_DICT = {
    ID_TABLE_THUMB:ID_TABLE_THUMB,
    "ID Media" : "id_media",
    "Media Name": "media_filename"
    }
    SORT_ITEMS = [
                "ID Media",
                "Media Name"
                ]
    TABLE_FIELDS = [
                    "id_media",
                    "media_filename"
                    ]
    SEARCH_DICT_TEMP = ""
    HOME = os.environ['PYARCHINIT_HOME']
    DB_SERVER = 'not defined'
    def __init__(self):
        # This is always the same
        QDialog.__init__(self)
        self.connection()
        self.setupUi(self)
        self.customize_gui()
        self.mDockWidget.setHidden(True)      
        self.iconListWidget.SelectionMode()
        #self.iconListWidget.itemSelectionChanged.connect(self.remove_all)
        self.iconListWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.iconListWidget.itemDoubleClicked.connect(self.openWide_image)
        self.sl.valueChanged.connect(self.valuechange)
        self.iconListWidget.itemSelectionChanged.connect(self.open_tags)
        #self.iconListWidget.itemEntered.connect(self.split_1)
        #self.iconListWidget.itemEntered.connect(self.split_2)
        self.setWindowTitle("pyArchInit - Media Manager")
        self.comboBox_sito.editTextChanged.connect(self.charge_us_list)
        self.comboBox_sito.editTextChanged.connect(self.charge_area_list)
        self.comboBox_sito.currentIndexChanged.connect(self.charge_area_list)
        self.comboBox_sito.currentIndexChanged.connect(self.charge_us_list)
        self.comboBox_area.currentIndexChanged.connect(self.charge_us_list)
        self.comboBox_area.editTextChanged.connect(self.charge_us_list)
        self.comboBox_sito.editTextChanged.connect(self.charge_sigla_list)
        self.comboBox_sito.editTextChanged.connect(self.charge_nr_st_list)
        self.fill_fields()
        sito = self.comboBox_sito.currentText()
        self.comboBox_sito.setEditText(sito)
        self.charge_list()
        self.charge_us_list()
        self.charge_area_list()
        self.charge_sigla_list()
        self.charge_nr_st_list()
        self.charge_data()
        self.view_num_rec()
    def remove_all(self):
        self.tableWidgetTags_US.setRowCount(1)
        self.tableWidgetTags_MAT.setRowCount(1)
        self.tableWidgetTags_tomba.setRowCount(1)
        self.tableWidgetTags_tomba_2.setRowCount(1)
    
    def split_2(self):
        items_selected = self.iconListWidget.selectedItems()#seleziono le icone
        res=[]
        list=[]
        self.tableWidgetTags_US.setHorizontalHeaderLabels(['Sito', 'Area', 'US'])
        row =0
        for name in items_selected: 
            names = name.text()
            if '-' not in names: 
                res.append(names) 
                continue 
            a = names.split("_") 
            for sub in a[2].split("-"): 
                for sub2 in sub:
                    res.append(f'{a[0]}_{a[1]}_{sub}') 
                for u in res:
                    res1 = str(u)
                    b = res1.split("_")
                    list.append(b)
                try:
                    self.insert_new_row('self.tableWidgetTags_US')
                    for i in list:    
                        self.tableWidgetTags_US.setItem(row,0,QTableWidgetItem(str(i[0])))
                        self.tableWidgetTags_US.setItem(row,1,QTableWidgetItem(str(i[1])))
                        self.tableWidgetTags_US.setItem(row,2,QTableWidgetItem(str(i[2])))
                except Exception as e:
                    QMessageBox.warning(self, "Messaggio", "Sistema di aggiornamento lista Sito: " + str(e), QMessageBox.Ok)
                self.remove_row('self.tableWidgetTags_US')
    def split_1(self):
        items_selected = self.iconListWidget.selectedItems()#seleziono le icone
        res=[]
        list=[]
        self.tableWidgetTags_US.setHorizontalHeaderLabels(['Sito', 'Area', 'US'])
        row =0
        #self.insert_new_row('self.tableWidgetTags_US')
        for name in items_selected: 
            names = name.text()
            if '-'  in names: 
                res.append(names) 
                continue 
            a = names.split("_") 
            list.append(a)
            try:
                for i in list:    
                    self.tableWidgetTags_US.setItem(row,0,QTableWidgetItem(str(a[0])))
                    self.tableWidgetTags_US.setItem(row,1,QTableWidgetItem(str(a[1])))
                    self.tableWidgetTags_US.setItem(row,2,QTableWidgetItem(str(a[2])))
            except Exception as e:
                QMessageBox.warning(self, "Messaggio", "Sistema di aggiornamento lista Sito: " + str(e), QMessageBox.Ok)
    def customize_gui(self):
        self.tableWidgetTags_US.setColumnWidth(0, 300)
        self.tableWidgetTags_US.setColumnWidth(1, 100)
        self.tableWidgetTags_US.setColumnWidth(2, 100)
        #self.tableWidgetTags_US.setColumnWidth(3, 100)
        self.tableWidgetTags_MAT.setColumnWidth(0, 300)
        self.tableWidgetTags_MAT.setColumnWidth(1, 150)
        self.tableWidgetTags_tomba.setColumnWidth(0, 300)
        self.tableWidgetTags_tomba.setColumnWidth(1, 150)
        self.tableWidgetTags_tomba_2.setColumnWidth(0, 300)
        self.tableWidgetTags_tomba_2.setColumnWidth(1, 100)
        self.tableWidgetTags_tomba_2.setColumnWidth(2, 100)
        self.tableWidget_tags.setColumnWidth(2, 300)
        self.iconListWidget.setIconSize(QSize(80, 180))
        self.iconListWidget.setLineWidth(2)
        self.iconListWidget.setMidLineWidth(2)
        
        valuesSites = self.charge_sito_list()
        self.delegateSites = ComboBoxDelegate()
        self.delegateSites.def_values(valuesSites)
        
        valuesArea = self.charge_area_us_list()
        self.delegateArea = ComboBoxDelegate()
        self.delegateArea.def_values(valuesArea)
        
        # valuesUS = self.charge_us_us_list()
        # self.delegateUS = ComboBoxDelegate()
        # self.delegateUS.def_values(str(valuesUS))
        
        valuesSS = self.charge_sigla_us_list()
        self.delegateSS = ComboBoxDelegate()
        self.delegateSS.def_values(valuesSS)
        
        # valuesNS = self.charge_nr_us_list()
        # self.delegateNS = ComboBoxDelegate()
        # self.delegateNS.def_values(str(valuesNS))
        
        
        self.delegateSites.def_editable('False')
        self.delegateArea.def_editable('False')
        #self.delegateUS.def_editable('False')
        #self.delegateNS.def_editable('False')
        self.delegateSS.def_editable('False')
        
        self.tableWidgetTags_US.setItemDelegateForColumn(0, self.delegateSites)
        self.tableWidgetTags_US.setItemDelegateForColumn(1, self.delegateArea)
        #self.tableWidgetTags_US.setItemDelegateForColumn(2, self.delegateUS)
        
        
        self.tableWidgetTags_MAT.setItemDelegateForColumn(0, self.delegateSites)
        self.tableWidgetTags_tomba.setItemDelegateForColumn(0, self.delegateSites)
        
        self.tableWidgetTags_tomba_2.setItemDelegateForColumn(0, self.delegateSites)        
        self.tableWidgetTags_tomba_2.setItemDelegateForColumn(1, self.delegateSS)
        #self.tableWidgetTags_tomba_2.setItemDelegateForColumn(2, self.delegateNS)
        self.charge_sito_list()
    def valuechange(self,value):
        self.sl.value() 
        self.iconListWidget.setIconSize(QSize(80 + value//40,180 + value//80))
    def charge_list(self):
        self.comboBox_sito.clear()
        sito_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('site_table', 'sito', 'SITE'))
        try:
            sito_vl.remove('')
        except Exception as e:
            if str(e) == "list.remove(x): x not in list":
                pass
            else:
                QMessageBox.warning(self, "Warning", str(e), QMessageBox.Ok)
        self.comboBox_sito.clear()
        sito_vl.sort()
        self.comboBox_sito.addItems(sito_vl)
    
    
    def charge_sigla_list(self):
        sito = str(self.comboBox_sito.currentText())
        if self.radioButton_struttura.isChecked():
            try:
                
                self.comboBox_sigla_struttura.clear()
                self.comboBox_sigla_struttura.update()
                sito = str(self.comboBox_sito.currentText())
                search_dict = {
                    'sito': "'" + sito + "'"
                }
                us_vl = self.DB_MANAGER.query_bool(search_dict, 'STRUTTURA')
                us_list = []
                if not us_vl:
                    return
                for i in range(len(us_vl)):
                    us_list.append(str(us_vl[i].sigla_struttura))
                try:
                    us_vl.remove('')
                except:
                    pass
                self.comboBox_sigla_struttura.clear()
                self.comboBox_sigla_struttura.addItems(self.UTILITY.remove_dup_from_list(us_list))
            except:
                MessageBox.warning(self, "Warning", str(e), QMessageBox.Ok)
    def charge_nr_st_list(self):
        sito = str(self.comboBox_sito.currentText())
        if self.radioButton_struttura.isChecked():
            try:
                
                self.comboBox_nr_struttura.clear()
                self.comboBox_nr_struttura.update()
                sito = str(self.comboBox_sito.currentText())
                search_dict = {
                    'sito': "'" + sito + "'"
                }
                us_vl = self.DB_MANAGER.query_bool(search_dict, 'STRUTTURA')
                us_list = []
                if not us_vl:
                    return
                for i in range(len(us_vl)):
                    us_list.append(str(us_vl[i].numero_struttura))
                try:
                    us_vl.remove('')
                except:
                    pass
                self.comboBox_nr_struttura.clear()
                self.comboBox_nr_struttura.addItems(self.UTILITY.remove_dup_from_list(us_list))
            except:
                MessageBox.warning(self, "Warning", str(e), QMessageBox.Ok)
    def charge_us_list(self):
        sito = str(self.comboBox_sito.currentText())
        if self.radioButton_us.isChecked():
            try:
                self.label_8.clear()
                self.label_8.setText('US')
                self.label_8.update()
                self.comboBox_us.clear()
                self.comboBox_us.update()
                sito = str(self.comboBox_sito.currentText())
                search_dict = {
                    'sito': "'" + sito + "'"
                }
                us_vl = self.DB_MANAGER.query_bool(search_dict, 'US')
                us_list = []
                if not us_vl:
                    return
                for i in range(len(us_vl)):
                    us_list.append(str(us_vl[i].us))
                try:
                    us_vl.remove('')
                except:
                    pass
                self.comboBox_us.clear()
                self.comboBox_us.addItems(self.UTILITY.remove_dup_from_list(us_list))
            except:
                MessageBox.warning(self, "Warning", str(e), QMessageBox.Ok)
        if self.radioButton_materiali.isChecked():
            try: 
                self.label_8.clear()
                self.label_8.setText('US')
                self.label_8.update()
                self.comboBox_us.clear()
                self.comboBox_us.update()
                sito = str(self.comboBox_sito.currentText())
                search_dict = {
                    'sito': "'" + sito + "'"
                }
                us_vl = self.DB_MANAGER.query_bool(search_dict, 'INVENTARIO_MATERIALI')
                us_list = []
                if not us_vl:
                    return 0
                for i in range(len(us_vl)):
                    us_list.append(str(us_vl[i].us))
                try:
                    us_vl.remove('')
                except:
                    pass
                self.comboBox_us.clear()
                self.comboBox_us.addItems(self.UTILITY.remove_dup_from_list(us_list))
        
            except:
                MessageBox.warning(self, "Warning", str(e), QMessageBox.Ok)
        if self.radioButton_tomba.isChecked():
            try:
                self.label_8.clear()
                self.label_8.setText('N. Tomba')
                self.label_8.update()
                self.comboBox_us.clear()
                self.comboBox_us.update()
                sito = str(self.comboBox_sito.currentText())
                search_dict = {
                    'sito': "'" + sito + "'"
                }
                us_vl = self.DB_MANAGER.query_bool(search_dict, 'TOMBA')
                us_list = []
                if not us_vl:
                    return 0
                for i in range(len(us_vl)):
                    us_list.append(str(us_vl[i].nr_scheda_taf))
                try:
                    us_vl.remove('')
                except:
                    pass
                self.comboBox_us.clear()
                self.comboBox_us.addItems(self.UTILITY.remove_dup_from_list(us_list))
            except:
                MessageBox.warning(self, "Warning", str(e), QMessageBox.Ok)    
    def charge_area_list(self):
        if self.radioButton_us.isChecked():
            sito = str(self.comboBox_sito.currentText())
            search_dict = {
                'sito': "'" + sito + "'"
            }
            area_vl = self.DB_MANAGER.query_bool(search_dict, 'US')
            area_list = []
            if not area_vl:
                return
            for i in range(len(area_vl)):
                area_list.append(str(area_vl[i].area))
            try:
                area_vl.remove('')
            except:
                pass
            self.comboBox_area.clear()
            self.comboBox_area.addItems(self.UTILITY.remove_dup_from_list(area_list))
        if self.radioButton_materiali.isChecked():
            sito = str(self.comboBox_sito.currentText())
            self.comboBox_area.clear()
            search_dict = {
                'sito': "'" + sito + "'"
            }
            area_vl = self.DB_MANAGER.query_bool(search_dict, 'INVENTARIO_MATERIALI')
            area_list = []
            if not area_vl:
                return 0
            for i in range(len(area_vl)):
                area_list.append(str(area_vl[i].area))
            try:
                area_vl.remove('')
            except:
                pass
            self.comboBox_area.clear()
            self.comboBox_area.addItems(self.UTILITY.remove_dup_from_list(area_list))
    
        if self.radioButton_tomba.isChecked():
            sito = str(self.comboBox_sito.currentText())
            self.comboBox_area.clear()
            search_dict = {
                'sito': "'" + sito + "'"
            }
            area_vl = self.DB_MANAGER.query_bool(search_dict, 'TOMBA')
            area_list = []
            if not area_vl:
                return 0
            for i in range(len(area_vl)):
                area_list.append(str(area_vl[i].area))
            try:
                area_vl.remove('')
            except:
                pass
            self.comboBox_area.clear()
            self.comboBox_area.addItems(self.UTILITY.remove_dup_from_list(area_list))
    
    def connection(self):
        conn_str = conn.conn_str()
        try:
            self.DB_MANAGER = Pyarchinit_db_management(conn_str)
            self.DB_MANAGER.connection()
            self.charge_records()
            #check if DB is empty
            if self.DATA_LIST:
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                self.BROWSE_STATUS = "b"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.label_sort.setText(self.SORTED_ITEMS["n"])
                self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR+1)
                self.charge_sito_list()
                self.fill_fields()
            else:
                if self.L=='it':
                    QMessageBox.warning(self, "BENVENUTI", "Benvenuti in pyArchInit" + self.NOME_SCHEDA + ". Il database è vuoto. premere 'Ok' e buon lavoro!",  QMessageBox.Ok)
                if self.L=='de':
                    QMessageBox.warning(self, "WILLKOMMEN", "Willkommen in pyArchInit" + self.NOME_SCHEDA + ". Die Datenbank ist leer. Drücken Sie 'Ok' und gute Arbeit!",  QMessageBox.Ok)
                else:
                    QMessageBox.warning(self, "WELCOME", "Welcome in pyArchInit" + self.NOME_SCHEDA + ". The database is empty. Push 'Ok' and good work!",  QMessageBox.Ok)
                
                self.charge_sito_list()
                self.BROWSE_STATUS = 'x'
        except Exception as  e:
            e = str(e)#QMessageBox.warning(self, "Warning", str(e), QMessageBox.Ok)
    def enable_button(self, n):
        self.pushButton_first_rec.setEnabled(n)
        self.pushButton_last_rec.setEnabled(n)
        self.pushButton_prev_rec.setEnabled(n)
        self.pushButton_next_rec.setEnabled(n)
        self.pushButton_sort.setEnabled(n)
        self.pushButton_go.setEnabled(n)
    def enable_button_search(self, n):
        self.pushButton_first_rec.setEnabled(n)
        self.pushButton_last_rec.setEnabled(n)
        self.pushButton_prev_rec.setEnabled(n)
        self.pushButton_next_rec.setEnabled(n)
        self.pushButton_sort.setEnabled(n)
        self.pushButton_go.setEnabled(n)
    def on_pushButton_go_pressed(self):
        if self.radioButton_us.isChecked():
            sito = str(self.comboBox_sito.currentText())
            area = str(self.comboBox_area.currentText())
            us = str(self.comboBox_us.currentText())
            search_dict = {
                'sito': "'" + str(sito) + "'",
                'area': "'" + str(area) + "'",
                'us': "'" + str(us) + "'"
            }
            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)
            us_vl = self.DB_MANAGER.select_medianame_2_from_db_sql(sito,area,us)
            if not bool(search_dict):
                if self.L=='it':
                    QMessageBox.warning(self, "ATTENZIONE", "Inserisci un valore", QMessageBox.Ok)
                elif self.L=='de':
                    QMessageBox.warning(self, "ACHTUNG", "Einen Wert einfügen", QMessageBox.Ok)
                else:
                    QMessageBox.warning(self, "WARNING", "Insert a value", QMessageBox.Ok)   
            else:
                res = self.DB_MANAGER.select_medianame_2_from_db_sql(sito,area,us)
                if not bool(res):
                    if self.L=='it':
                        QMessageBox.warning(self, "ATTENZIONE", "Non è stato trovato nessun record!", QMessageBox.Ok)
                    elif self.L=='de':
                        QMessageBox.warning(self, "ACHTUNG", "Keinen Record gefunden!", QMessageBox.Ok)
                    else:
                        QMessageBox.warning(self, "WARNING", "No record found!", QMessageBox.Ok)   
                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR+1)
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                    self.fill_fields(self.REC_CORR)
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.setComboBoxEnable(["self.comboBox_sito"],"True")
                    self.setComboBoxEnable(["self.comboBox_area"],"True")
                    self.setComboBoxEnable(["self.comboBox_us"],"True")
                else:
                    self.DATA_LIST = []
                    self.empty_fields()
                    for i in res:
                        self.DATA_LIST.append(i)
                    self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                    self.fill_fields()
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR+1)
                    if self.L=='it':
                        if self.REC_TOT == 1:
                            strings = ("E' stato trovato", self.REC_TOT, "record")
                            
                        else:
                            strings = ("Sono stati trovati", self.REC_TOT, "records")
                            
                    elif self.L=='de':
                        if self.REC_TOT == 1:
                            strings = ("Es wurde gefunden", self.REC_TOT, "record")
                            
                        else:
                            strings = ("Sie wurden gefunden", self.REC_TOT, "records")
                            
                    else:
                        if self.REC_TOT == 1:
                            strings = ("It has been found", self.REC_TOT, "record")
                            
                        else:
                            strings = ("They have been found", self.REC_TOT, "records")
                            
                    
                    self.setComboBoxEnable(["self.comboBox_sito"],"True")
                    self.setComboBoxEnable(["self.comboBox_area"],"True")
                    self.setComboBoxEnable(["self.comboBox_us"],"True")
                    #check_for_buttons = 1
                    QMessageBox.information(self, "Info", "%s %d %s" % strings, QMessageBox.Ok)
            self.NUM_DATA_BEGIN =  1
            self.NUM_DATA_END = len(self.DATA_LIST)
            self.view_num_rec()
            self.open_images()  
            self.iconListWidget.clear()
            thumb_path = conn.thumb_path()
            thumb_path_str = thumb_path['thumb_path']
            record_us_list = self.DB_MANAGER.select_medianame_2_from_db_sql(sito,area,us)
            for i in record_us_list:
                search_dict = {'media_filename': "'" + str(i.media_name) + "'"}
                u = Utility()
                search_dict = u.remove_empty_items_fr_dict(search_dict)
                mediathumb_data = self.DB_MANAGER.query_bool(search_dict, "MEDIA_THUMB")
                thumb_path = str(mediathumb_data[0].filepath)
                item = QListWidgetItem(str(i.media_name))
                item.setData(Qt.UserRole, str(i.media_name))
                icon = QIcon(thumb_path_str+thumb_path)
                item.setIcon(icon)
                self.iconListWidget.addItem(item)
        if self.radioButton_materiali.isChecked():
            sito = str(self.comboBox_sito.currentText())
            area = str(self.comboBox_area.currentText())
            us = str(self.comboBox_us.currentText())
            search_dict = {
                'sito': "'" + str(sito) + "'",
                'area': "'" + str(area) + "'",
                'us': "'" + str(us) + "'"
            }
            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)
            us_vl = self.DB_MANAGER.select_medianame_ra_from_db_sql(sito,area,us)
            if not bool(search_dict):
                if self.L=='it':
                    QMessageBox.warning(self, "ATTENZIONE", "Inserisci un valore", QMessageBox.Ok)
                elif self.L=='de':
                    QMessageBox.warning(self, "ACHTUNG", "Einen Wert einfügen", QMessageBox.Ok)
                else:
                    QMessageBox.warning(self, "WARNING", "Insert a value", QMessageBox.Ok)
            else:
                res = self.DB_MANAGER.select_medianame_ra_from_db_sql(sito,area,us)
                if not bool(res):
                    if self.L=='it':
                        QMessageBox.warning(self, "ATTENZIONE", "Non è stato trovato nessun record!", QMessageBox.Ok)
                    elif self.L=='de':
                        QMessageBox.warning(self, "ACHTUNG", "Keinen Record gefunden!", QMessageBox.Ok)
                    else:
                        QMessageBox.warning(self, "WARNING", "No record found!", QMessageBox.Ok)   
                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR+1)
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                    self.fill_fields(self.REC_CORR)
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.setComboBoxEnable(["self.comboBox_sito"],"True")
                    self.setComboBoxEnable(["self.comboBox_area"],"True")
                    self.setComboBoxEnable(["self.comboBox_us"],"True")
                else:
                    self.DATA_LIST = []
                    self.empty_fields()
                    for i in res:
                        self.DATA_LIST.append(i)
                    self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                    self.fill_fields()
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR+1)
                    if self.L=='it':
                        if self.REC_TOT == 1:
                            strings = ("E' stato trovato", self.REC_TOT, "record")
                            
                        else:
                            strings = ("Sono stati trovati", self.REC_TOT, "records")
                            
                    elif self.L=='de':
                        if self.REC_TOT == 1:
                            strings = ("Es wurde gefunden", self.REC_TOT, "record")
                            
                        else:
                            strings = ("Sie wurden gefunden", self.REC_TOT, "records")
                            
                    else:
                        if self.REC_TOT == 1:
                            strings = ("It has been found", self.REC_TOT, "record")
                            
                        else:
                            strings = ("They have been found", self.REC_TOT, "records")
                    self.setComboBoxEnable(["self.comboBox_sito"],"True")
                    self.setComboBoxEnable(["self.comboBox_area"],"True")
                    self.setComboBoxEnable(["self.comboBox_us"],"True")
                    QMessageBox.warning(self, "Messaggio", "%s %d %s" % strings, QMessageBox.Ok)
            self.NUM_DATA_BEGIN =  1
            self.NUM_DATA_END = len(self.DATA_LIST)
            self.view_num_rec()
            self.open_images()  
            self.iconListWidget.clear()
            thumb_path = conn.thumb_path()
            thumb_path_str = thumb_path['thumb_path']
            record_us_list = self.DB_MANAGER.select_medianame_ra_from_db_sql(sito,area,us)
            for i in record_us_list:
                search_dict = {'media_filename': "'" + str(i.media_name) + "'"}
                u = Utility()
                search_dict = u.remove_empty_items_fr_dict(search_dict)
                mediathumb_data = self.DB_MANAGER.query_bool(search_dict, "MEDIA_THUMB")
                thumb_path = str(mediathumb_data[0].filepath)
                item = QListWidgetItem(str(i.media_name))
                item.setData(Qt.UserRole, str(i.media_name))
                icon = QIcon(thumb_path_str+thumb_path)
                item.setIcon(icon)
                self.iconListWidget.addItem(item)
        
        if self.radioButton_tomba.isChecked():
            sito = str(self.comboBox_sito.currentText())
            area = str(self.comboBox_area.currentText())
            #us = str(self.comboBox_us.currentText())
            search_dict = {
                'sito': "'" + str(sito) + "'",
                'area': "'" + str(area) + "'"
            }
            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)
            us_vl = self.DB_MANAGER.select_medianame_tb_from_db_sql(sito,area)
            if not bool(search_dict):
                if self.L=='it':
                    QMessageBox.warning(self, "ATTENZIONE", "Inserisci un valore", QMessageBox.Ok)
                elif self.L=='de':
                    QMessageBox.warning(self, "ACHTUNG", "Einen Wert einfügen", QMessageBox.Ok)
                else:
                    QMessageBox.warning(self, "WARNING", "Insert a value", QMessageBox.Ok)
            else:
                res = self.DB_MANAGER.select_medianame_tb_from_db_sql(sito,area)
                if not bool(res):
                    if self.L=='it':
                        QMessageBox.warning(self, "ATTENZIONE", "Non è stato trovato nessun record!", QMessageBox.Ok)
                    elif self.L=='de':
                        QMessageBox.warning(self, "ACHTUNG", "Keinen Record gefunden!", QMessageBox.Ok)
                    else:
                        QMessageBox.warning(self, "WARNING", "No record found!", QMessageBox.Ok)   
                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR+1)
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                    self.fill_fields(self.REC_CORR)
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.setComboBoxEnable(["self.comboBox_sito"],"True")
                    self.setComboBoxEnable(["self.comboBox_area"],"True")
                    #self.setComboBoxEnable(["self.comboBox_us"],"True")
                else:
                    self.DATA_LIST = []
                    self.empty_fields()
                    for i in res:
                        self.DATA_LIST.append(i)
                    self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                    self.fill_fields()
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR+1)
                    if self.L=='it':
                        if self.REC_TOT == 1:
                            strings = ("E' stato trovato", self.REC_TOT, "record")
                            
                        else:
                            strings = ("Sono stati trovati", self.REC_TOT, "records")
                            
                    elif self.L=='de':
                        if self.REC_TOT == 1:
                            strings = ("Es wurde gefunden", self.REC_TOT, "record")
                            
                        else:
                            strings = ("Sie wurden gefunden", self.REC_TOT, "records")
                            
                    else:
                        if self.REC_TOT == 1:
                            strings = ("It has been found", self.REC_TOT, "record")
                            
                        else:
                            strings = ("They have been found", self.REC_TOT, "records")
                    self.setComboBoxEnable(["self.comboBox_sito"],"True")
                    self.setComboBoxEnable(["self.comboBox_area"],"True")
                    #self.setComboBoxEnable(["self.comboBox_us"],"True")
                    QMessageBox.warning(self, "Messaggio", "%s %d %s" % strings, QMessageBox.Ok)
            self.NUM_DATA_BEGIN =  1
            self.NUM_DATA_END = len(self.DATA_LIST)
            self.view_num_rec()
            self.open_images()  
            self.iconListWidget.clear()
            thumb_path = conn.thumb_path()
            thumb_path_str = thumb_path['thumb_path']
            record_us_list = self.DB_MANAGER.select_medianame_tb_from_db_sql(sito,area)
            for i in record_us_list:
                search_dict = {'media_filename': "'" + str(i.media_name) + "'"}
                u = Utility()
                search_dict = u.remove_empty_items_fr_dict(search_dict)
                mediathumb_data = self.DB_MANAGER.query_bool(search_dict, "MEDIA_THUMB")
                thumb_path = str(mediathumb_data[0].filepath)
                item = QListWidgetItem(str(i.media_name))
                item.setData(Qt.UserRole, str(i.media_name))
                icon = QIcon(thumb_path_str+thumb_path)
                item.setIcon(icon)
                self.iconListWidget.addItem(item)
    
    
    
    
        if self.radioButton_struttura.isChecked():
            sito = str(self.comboBox_sito.currentText())
            sigla = str(self.comboBox_sigla_struttura.currentText())
            nr_st = str(self.comboBox_nr_struttura.currentText())
            
            
            
            
            search_dict = {
                'sito': "'" + str(sito) + "'",
                'sigla_struttura': "'" + str(sigla) + "'",
                'numero_struttura': "'" + str(nr_st) + "'"
            }
            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)
            us_vl = self.DB_MANAGER.select_medianame_from_st_sql(sito,sigla,nr_st)
            if not bool(search_dict):
                if self.L=='it':
                    QMessageBox.warning(self, "ATTENZIONE", "Inserisci un valore", QMessageBox.Ok)
                elif self.L=='de':
                    QMessageBox.warning(self, "ACHTUNG", "Einen Wert einfügen", QMessageBox.Ok)
                else:
                    QMessageBox.warning(self, "WARNING", "Insert a value", QMessageBox.Ok)
            else:
                res = self.DB_MANAGER.select_medianame_from_st_sql(sito,sigla,nr_st)
                if not bool(res):
                    if self.L=='it':
                        QMessageBox.warning(self, "ATTENZIONE", "Non è stato trovato nessun record!", QMessageBox.Ok)
                    elif self.L=='de':
                        QMessageBox.warning(self, "ACHTUNG", "Keinen Record gefunden!", QMessageBox.Ok)
                    else:
                        QMessageBox.warning(self, "WARNING", "No record found!", QMessageBox.Ok)   
                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR+1)
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                    self.fill_fields(self.REC_CORR)
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.setComboBoxEnable(["self.comboBox_sito"],"True")
                    self.setComboBoxEnable(["self.comboBox_sigla_struttura"],"True")
                    self.setComboBoxEnable(["self.comboBox_nr_struttura"],"True")
                else:
                    self.DATA_LIST = []
                    self.empty_fields()
                    for i in res:
                        self.DATA_LIST.append(i)
                    self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                    self.fill_fields()
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR+1)
                    if self.L=='it':
                        if self.REC_TOT == 1:
                            strings = ("E' stato trovato", self.REC_TOT, "record")
                            
                        else:
                            strings = ("Sono stati trovati", self.REC_TOT, "records")
                            
                    elif self.L=='de':
                        if self.REC_TOT == 1:
                            strings = ("Es wurde gefunden", self.REC_TOT, "record")
                            
                        else:
                            strings = ("Sie wurden gefunden", self.REC_TOT, "records")
                            
                    else:
                        if self.REC_TOT == 1:
                            strings = ("It has been found", self.REC_TOT, "record")
                            
                        else:
                            strings = ("They have been found", self.REC_TOT, "records")
                    self.setComboBoxEnable(["self.comboBox_sito"],"True")
                    self.setComboBoxEnable(["self.comboBox_sigla_struttura"],"True")
                    self.setComboBoxEnable(["self.comboBox_nr_struttura"],"True")
                    QMessageBox.warning(self, "Messaggio", "%s %d %s" % strings, QMessageBox.Ok)
            self.NUM_DATA_BEGIN =  1
            self.NUM_DATA_END = len(self.DATA_LIST)
            self.view_num_rec()
            self.open_images()  
            self.iconListWidget.clear()
            thumb_path = conn.thumb_path()
            thumb_path_str = thumb_path['thumb_path']
            record_us_list = self.DB_MANAGER.select_medianame_from_st_sql(sito,sigla,nr_st)
            for i in record_us_list:
                search_dict = {'media_filename': "'" + str(i.media_name) + "'"}
                u = Utility()
                search_dict = u.remove_empty_items_fr_dict(search_dict)
                mediathumb_data = self.DB_MANAGER.query_bool(search_dict, "MEDIA_THUMB")
                thumb_path = str(mediathumb_data[0].filepath)
                item = QListWidgetItem(str(i.media_name))
                item.setData(Qt.UserRole, str(i.media_name))
                icon = QIcon(thumb_path_str+thumb_path)
                item.setIcon(icon)
                self.iconListWidget.addItem(item)
    
    def getDirectoryVideo(self):
        thumb_path = conn.thumb_path()
        thumb_path_str = thumb_path['thumb_path']      
        if thumb_path_str=='':
            if self.L=='it':
                QMessageBox.information(self, "Info", "devi settare prima la path per salvare le thumbnail e i video. Vai in impostazioni di sistema/ path setting ")
            elif self.L=='de':
                QMessageBox.information(self, "Info", "müssen Sie zuerst den Pfad zum Speichern der Miniaturansichten und Videos festlegen. Gehen Sie zu System-/Pfad-Einstellung")
            else:
                QMessageBox.information(self, "Message", "you must first set the path to save the thumbnails and videos. Go to system/path setting")
        else:    
            video_list=[]
            directory = QFileDialog.getExistingDirectory(self, "Directory", "Choose a directory:",
                                                         QFileDialog.ShowDirsOnly)
            if not directory:
                return 0
            try:
                for video in sorted(os.listdir(directory)):
                    if video.endswith(".mp4"): #or .avi, .mpeg, whatever.
                        filenamev, filetypev = video.split(".")[0], video.split(".")[1]  # db definisce nome immagine originale
                        filepathv = directory + '/' + filenamev + "." + filetypev  # db definisce il path immagine originale
                        idunique_video_check = self.db_search_check(self.MAPPER_TABLE_CLASS, 'filepath', filepathv)
                        
                        vcap = cv2.VideoCapture(filepathv)
                        res, im_ar = vcap.read()
                        while im_ar.mean() < 1 and res:
                              res, im_ar = vcap.read()
                        im_ar = cv2.resize(im_ar, (100, 100), 0, 0, cv2.INTER_LINEAR)
                        #to save we have two options
                        outputfile='{}.png'.format(directory + '/' + filenamev)
                        cv2.imwrite(outputfile, im_ar)
           
                        if not bool(idunique_video_check):
                            mediatype = 'video'  # db definisce il tipo di immagine originale
                            self.insert_record_media(mediatype, filenamev, filetypev,
                                                     filepathv)  # db inserisce i dati nella tabella media originali
                            MU = Video_utility()
                            MUR = Video_utility_resize()
                            media_max_num_id = self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS,
                                                                          self.ID_TABLE)  # db recupera il valore più alto ovvero l'ultimo immesso per l'immagine originale
                            thumb_path = conn.thumb_path()
                            thumb_path_str = thumb_path['thumb_path']
                            thumb_resize = conn.thumb_resize()
                            thumb_resize_str = thumb_resize['thumb_resize']
                            media_thumb_suffix = '_video.png'
                            media_resize_suffix = '.mp4'
                            filenameorig = filenamev
                            filename_thumb = str(media_max_num_id) + "_" + filenamev + media_thumb_suffix
                            filename_resize = str(media_max_num_id) + "_" +filenamev + media_resize_suffix
                            filepath_thumb =  filename_thumb
                            filepath_resize = filename_resize
                            self.SORT_ITEMS_CONVERTED = []
                            # crea la thumbnail
                            try:
                                MUR.resample_images(media_max_num_id, filepathv, filenameorig, thumb_resize_str, media_resize_suffix)
                            except Exception as e:
                                QMessageBox.warning(self, "Cucu", str(e), QMessageBox.Ok)
                                # progressBAr

                            try:
                                MU.resample_images(media_max_num_id, outputfile, filenameorig, thumb_path_str, media_thumb_suffix)
                            except Exception as e:
                                QMessageBox.warning(self, "Cucu", str(e), QMessageBox.Ok)

                            try:
                                for i in enumerate(image):
                                    image_list.append(i[0])
                                for n in range(len(image_list)):
                                    value = (float(n)/float(len(image_list)))*100
                                    self.progressBar.setValue(value)
                                    QApplication.processEvents()
                            except:
                                pass
                            self.insert_record_mediathumb(media_max_num_id, mediatype, filenamev, filename_thumb, filetypev,
                                                          filepath_thumb, filepath_resize)
                            item = QListWidgetItem(str(filenameorig))
                            item.setData(Qt.UserRole, str(media_max_num_id))
                            icon = QIcon(str(thumb_path_str)+filepath_thumb)
                            item.setIcon(icon)
                            self.iconListWidget.addItem(item)
                            
                        elif bool(idunique_video_check):
                            data = idunique_video_check
                            id_media = data[0].id_media
                            media_filename =data[0].filename
                            # visualizza le immagini nella ui
                            item = QListWidgetItem(str(media_filename))
                            data_for_thumb = self.db_search_check(self.MAPPER_TABLE_CLASS_thumb, 'media_filename',
                                                                  media_filename)  # recupera i valori della thumb in base al valore id_media del file originale
                            try:
                                thumb_path = data_for_thumb[0].filepath_thumb
                                item.setData(Qt.UserRole, thumb_path)
                                icon = QIcon(str(thumb_path_str)+filepath_thumb)  # os.path.join('%s/%s' % (directory.toUtf8(), image)))
                                item.setIcon(icon)
                                self.iconListWidget.addItem(item)
                            except:
                                pass
                
                    for i in enumerate(image):
                        image_list.append(i[0])
                    for n in range(len(image_list)):
                        value = (float(n)/float(len(image_list)))*100
                        self.progressBar.setValue(value)
                        QApplication.processEvents()
                if bool(idunique_video_check):
                    if self.L=='it':
                        QMessageBox.information(self, "Info", "I video sono già caricati nel database")
                    elif self.L=='de':
                        QMessageBox.information(self, "Info", "Videos sind bereits in die Datenbank hochgeladen")
                    else:
                        QMessageBox.information(self, "Info", "The videos are already uploaded to the database")
                elif not bool(idunique_video_check):
                    if self.L=='it':
                        QMessageBox.information(self, "Message", "Video caricati! Puoi taggarle")
                    elif self.L=='de':
                        QMessageBox.information(self, "Message", "Hochgeladene Videos! Sie können sie taggen")
                    else:
                        QMessageBox.information(self, "Message", "Uploaded videos! You can tag them")    
            
            except:
                if self.L=='it':
                    QMessageBox.warning(self, "Warning", "controlla che il nome del file non abbia caratteri speciali", QMessageBox.Ok)
                if self.L=='de':
                    QMessageBox.warning(self, "Warning", "prüfen, ob der Dateiname keine Sonderzeichen enthält", QMessageBox.Ok)
                else:
                    QMessageBox.warning(self, "Warning", "check that the file name has no special characters", QMessageBox.Ok)    
            self.progressBar.reset()
            self.charge_data ()
            self.view_num_rec()
            self.open_images()
    
    def getDirectory(self):
        thumb_path = conn.thumb_path()
        thumb_path_str = thumb_path['thumb_path']      
        if thumb_path_str=='':
            if self.L=='it':
                QMessageBox.information(self, "Info", "devi settare prima la path per salvare le thumbnail e i video. Vai in impostazioni di sistema/ path setting ")
            elif self.L=='de':
                QMessageBox.information(self, "Info", "müssen Sie zuerst den Pfad zum Speichern der Miniaturansichten und Videos festlegen. Gehen Sie zu System-/Pfad-Einstellung")
            else:
                QMessageBox.information(self, "Message", "you must first set the path to save the thumbnails and videos. Go to system/path setting")
        else:    
            image_list=[]
            directory = QFileDialog.getExistingDirectory(self, "Directory", "Choose a directory:",
                                                         QFileDialog.ShowDirsOnly)
            if not directory:
                return 0
            try:
                for image in sorted(os.listdir(directory)):    
                    if image.endswith(".png") or image.endswith(".PNG") or image.endswith(".JPG") or image.endswith(
                            ".jpg") or image.endswith(".jpeg") or image.endswith(".JPEG") or image.endswith(
                        ".tif") or image.endswith(".TIF") or image.endswith(".tiff") or image.endswith(".TIFF"):# or image.endswith(".mp4"):
                        filename, filetype = image.split(".")[0], image.split(".")[1]  # db definisce nome immagine originale
                        filepath = directory + '/' + filename + "." + filetype  # db definisce il path immagine originale
                        idunique_image_check = self.db_search_check(self.MAPPER_TABLE_CLASS, 'filepath',
                                                                    filepath)  # controlla che l'immagine non sia già presente nel db sulla base del suo path
                        if not bool(idunique_image_check):
                            mediatype = 'image'  # db definisce il tipo di immagine originale
                            self.insert_record_media(mediatype, filename, filetype,
                                                     filepath)  # db inserisce i dati nella tabella media originali
                            MU = Media_utility()
                            MUR = Media_utility_resize()
                            media_max_num_id = self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS,
                                                                          self.ID_TABLE)  # db recupera il valore più alto ovvero l'ultimo immesso per l'immagine originale
                            thumb_path = conn.thumb_path()
                            thumb_path_str = thumb_path['thumb_path']
                            thumb_resize = conn.thumb_resize()
                            thumb_resize_str = thumb_resize['thumb_resize']
                            media_thumb_suffix = '_thumb.png'
                            media_resize_suffix = '.png'
                            filenameorig = filename
                            filename_thumb = str(media_max_num_id) + "_" + filename + media_thumb_suffix
                            filename_resize = str(media_max_num_id) + "_" +filename + media_resize_suffix
                            filepath_thumb =  filename_thumb
                            filepath_resize = filename_resize
                            self.SORT_ITEMS_CONVERTED = []
                            # crea la thumbnail
                            try:
                                MU.resample_images(media_max_num_id, filepath, filenameorig, thumb_path_str, media_thumb_suffix)
                                MUR.resample_images(media_max_num_id, filepath, filenameorig, thumb_resize_str, media_resize_suffix)
                            except Exception as e:
                                QMessageBox.warning(self, "Cucu", str(e), QMessageBox.Ok)
                                # progressBAr
                            
                            
                            
                            self.insert_record_mediathumb(media_max_num_id, mediatype, filename, filename_thumb, filetype,
                                                          filepath_thumb, filepath_resize)
                            item = QListWidgetItem(str(filenameorig))
                            item.setData(Qt.UserRole, str(media_max_num_id))
                            icon = QIcon(str(thumb_path_str)+filepath_thumb)
                            item.setIcon(icon)
                            self.iconListWidget.addItem(item)
                            #self.progressBar.reset()
                        elif bool(idunique_image_check):
                            data = idunique_image_check
                            id_media = data[0].id_media
                            media_filename =data[0].filename
                            # visualizza le immagini nella ui
                            item = QListWidgetItem(str(media_filename))
                            data_for_thumb = self.db_search_check(self.MAPPER_TABLE_CLASS_thumb, 'media_filename',
                                                                  media_filename)  # recupera i valori della thumb in base al valore id_media del file originale
                            try:
                                thumb_path = data_for_thumb[0].filepath_thumb
                                item.setData(Qt.UserRole, thumb_path)
                                icon = QIcon(str(thumb_path_str)+filepath_thumb)  # os.path.join('%s/%s' % (directory.toUtf8(), image)))
                                item.setIcon(icon)
                                self.iconListWidget.addItem(item)
                            except:
                                pass
                    
                    for i in enumerate(image):
                        image_list.append(i[0])
                        
                    for n in range(len(image_list)):
                        
                        value = (float(n)/float(len(image_list)))*100
                        #QMessageBox.information(self, "Info", str(n)+''+str(len(image_list)))
                        self.progressBar.setValue(value)
                        QApplication.processEvents()
                    
                if bool(idunique_image_check):
                    if self.L=='it':
                        QMessageBox.information(self, "Info", "Le immagini sono già caricate nel database")
                    elif self.L=='de':
                        QMessageBox.information(self, "Info", "Die Bilder sind bereits in die Datenbank geladen")
                    else:
                        QMessageBox.information(self, "Info", "The images are already uploaded to the database")
                elif not bool(idunique_image_check):
                    if self.L=='it':
                        QMessageBox.information(self, "Message", "Immagini caricate! Puoi taggarle")
                    elif self.L=='de':
                        QMessageBox.information(self, "Message", "Bilder hochgeladen! Sie können sie markieren")
                    else:
                        QMessageBox.information(self, "Message", "Uploaded images! You can tag them")    
            except:
                if self.L=='it':
                    QMessageBox.warning(self, "Warning", "controlla che il nome del file non abbia caratteri speciali", QMessageBox.Ok)
                if self.L=='de':
                    QMessageBox.warning(self, "Warning", "prüfen, ob der Dateiname keine Sonderzeichen enthält", QMessageBox.Ok)
                else:
                    QMessageBox.warning(self, "Warning", "check that the file name has no special characters", QMessageBox.Ok)    
            
            self.progressBar.reset()
            #####codice da sviluppare per lautotag#########################################
            # for root, directories, files in os.walk(directory, topdown=False):
                # for name in files:
                    

                    # filename = name.split(".")[0] 
                    # img = cv2.imread(os.path.join(root, name))### importo una foto
                    # img = cv2.cvtColor(img,  cv2.COLOR_BGR2RGB)## setto il colore rgb


                    # # box = pytesseract.image_to_data(img)
                    # # print(box)
                    # boxes = pytesseract.image_to_string(img, config='--oem 1 --psm 3')#, config='-c tessedit_create_tsv=1',output_type="dict") #######do in pasto a tesseract
                    # #############################################
                    # #### Detecting Words  ######
                    # #############################################
                    # #[   0          1           2           3           4          5         6       7       8        9        10       11 ]
                    # #['level', 'page_num', 'block_num', 'par_num', 'line_num', 'word_num', 'left', 'top', 'width', 'height', 'conf', 'text']
                    # # crea una tabella di 11 colonne. questo non è necessario al fine del riconoscimento del testo 
                    # for a,b in enumerate(boxes.splitlines()):
                            # print(b)
                            # if a!=0:
                                # b = b.split()
                                # if len(b)==12:
                                    # x,y,w,h = int(b[6]),int(b[7]),int(b[8]),int(b[9])
                                    # cv2.putText(img,b[11],(x,y-180),cv2.FONT_HERSHEY_SIMPLEX,0.6,(255,27,0),2)
                                    # cv2.rectangle(img, (x,y), (x+w, y+h), (50, 50, 255), 2)

                    # # ########### cerco area e us se esistono nel box e le stampo#######

                    # # # area= str('AREA 1')
                    # # # us = str('US 4')
                    # # # if area or us in boxes:
                        # # # print(area[5])
                        # # # print (us[3])
                    # # # ##############visualizzo l'immagine con il testo evidenziato#############
                    # scale_percent = 60 # percent of original size
                    # width = int(img.shape[1] * scale_percent / 100)
                    # height = int(img.shape[0] * scale_percent / 100)
                    # dim = (width, height)
                    # # resize image
                    # resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
                    
                    # # cv2.imshow('img', resized)
                    # # cv2.waitKey(0)               
                    # row=0
                    
                    # #aa = boxes.find('-')
                    # bb = boxes.find('-')
                    # cc = boxes.find('US')
                    # # for name in items_selected: 
                        # # names = name.text()
                        # # if '-'  in names: 
                            # # res.append(names) 
                            # # continue 
                        # # a = names.split("_") 
                        # # list.append(a)
                    
                    # s1 = bb+1 
               
                    # s2 = cc+3
                    
                    
                    # try:
                        # self.insert_new_row('self.tableWidgetTags_US')
                        
                        # self.tableWidgetTags_US.setItem(row,0,QTableWidgetItem(str('Vico Rosario di Palazzo 25(NA)')))
                        # self.tableWidgetTags_US.setItem(row,1,QTableWidgetItem(str('1')))
                        # self.tableWidgetTags_US.setItem(row,3,QTableWidgetItem(str(filename)))
                        # if bb:
                            # self.tableWidgetTags_US.setItem(row,2,QTableWidgetItem(boxes[s1]))
                        # elif cc and not bb:
                            # self.tableWidgetTags_US.setItem(row,2,QTableWidgetItem(boxes[s2]))
                    # except Exception as e:
                        # QMessageBox.warning(self, "Messaggio", "Sistema di aggiornamento lista Sito: " + str(e), QMessageBox.Ok)
            
            self.charge_data ()
            self.view_num_rec()
            self.open_images()
    
    def insert_record_media(self, mediatype, filename, filetype, filepath):
        self.mediatype = mediatype
        self.filename = filename
        self.filetype = filetype
        self.filepath = filepath
        try:
            data = self.DB_MANAGER.insert_media_values(
                self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, self.ID_TABLE) + 1,
                str(self.mediatype),  # 1 - mediatyype
                str(self.filename),  # 2 - filename
                str(self.filetype),  # 3 - filetype
                str(self.filepath),  # 4 - filepath
                str('Insert description'),  # 5 - descrizione
                str("['imagine']"))  # 6 - tags
            try:
                self.DB_MANAGER.insert_data_session(data)
                return 1
            except Exception as  e:
                e_str = str(e)
                if e_str.__contains__("Integrity"):
                    msg = self.filename + ": Image already in the database"
                else:
                    msg = e
                #QMessageBox.warning(self, "Errore", "Warning 1 ! \n"+ str(msg),  QMessageBox.Ok)
                return 0
        except Exception as  e:
            QMessageBox.warning(self, "Error", "Warning 2 ! \n"+str(e),  QMessageBox.Ok)
            return 0
    def insert_record_mediathumb(self, media_max_num_id, mediatype, filename, filename_thumb, filetype, filepath_thumb, filepath_resize):
        self.media_max_num_id = media_max_num_id
        self.mediatype = mediatype
        self.filename = filename
        self.filename_thumb = filename_thumb
        self.filetype = filetype
        self.filepath_thumb = filepath_thumb
        self.filepath_resize = filepath_resize
        try:
            data = self.DB_MANAGER.insert_mediathumb_values(
                self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS_thumb, self.ID_TABLE_THUMB) + 1,
                str(self.media_max_num_id),  # 1 - media_max_num_id
                str(self.mediatype),  # 2 - mediatype
                str(self.filename),  # 3 - filename
                str(self.filename_thumb),  # 4 - filename_thumb
                str(self.filetype),  # 5 - filetype
                str(self.filepath_thumb),  # 6 - filepath_thumb
                str(self.filepath_resize))  # 6 - filepath_thumb
            try:
                self.DB_MANAGER.insert_data_session(data)
                return 1
            except Exception as e:
                e_str = str(e)
                if e_str.__contains__("Integrity"):
                    msg = self.filename + ": thumb already present into the database"
                else:
                    msg = e
                #QMessageBox.warning(self, "Error", "warming 1 ! \n"+ str(msg),  QMessageBox.Ok)
                return 0
        except Exception as  e:
            QMessageBox.warning(self, "Error", "Warning 2 ! \n"+str(e),  QMessageBox.Ok)
            return 0
    def insert_mediaToEntity_rec(self, id_entity, entity_type, table_name, id_media, filepath, media_name):
        """
        id_mediaToEntity,
        id_entity,
        entity_type,
        table_name,
        id_media,
        filepath,
        media_name"""
        self.id_entity = id_entity
        self.entity_type = entity_type
        self.table_name = table_name
        self.id_media = id_media
        self.filepath = filepath
        self.media_name = media_name
        try:
            data = self.DB_MANAGER.insert_media2entity_values(
                self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS_mediatoentity, self.ID_TABLE_mediatoentity) + 1,
                int(self.id_entity),  # 1 - id_entity
                str(self.entity_type),  # 2 - entity_type
                str(self.table_name),  # 3 - table_name
                int(self.id_media),  # 4 - us
                str(self.filepath),  # 5 - filepath
                str(self.media_name))  # 6 - media_name
            try:
                self.DB_MANAGER.insert_data_session(data)
                return 1
            except Exception as  e:
                e_str = str(e)
                if e_str.__contains__("Integrity"):
                    msg = self.ID_TABLE + " already present into the database"
                else:
                    msg = e
                QMessageBox.warning(self, "Error", "Warning 1 ! \n"+ str(msg),  QMessageBox.Ok)
                return 0
        except Exception as  e:
            QMessageBox.warning(self, "Error", "Warning 2 ! \n"+str(e),  QMessageBox.Ok)
            return 0
    def delete_mediaToEntity_rec(self, id_entity, entity_type, table_name, id_media, filepath, media_name):
        """
        id_mediaToEntity,
        id_entity,
        entity_type,
        table_name,
        id_media,
        filepath,
        media_name"""
        self.id_entity = id_entity
        self.entity_type = entity_type
        self.table_name = table_name
        self.id_media = id_media
        self.filepath = filepath
        self.media_name = media_name
        try:
            data = self.DB_MANAGER.insert_media2entity_values(
            self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS_mediatoentity, self.ID_TABLE_mediatoentity)+1,
            int(self.id_entity),                                                    #1 - id_entity
            str(self.entity_type),                                              #2 - entity_type
            str(self.table_name),                                               #3 - table_name
            int(self.id_media),                                                     #4 - us
            str(self.filepath),                                                     #5 - filepath
            str(self.media_name))
        except Exception as  e:
            QMessageBox.warning(self, "Error", "Warning 2 ! \n"+str(e),  QMessageBox.Ok)
            return 0
    def db_search_check(self, table_class, field, value):
        self.table_class = table_class
        self.field = field
        self.value = value
        search_dict = {self.field: "'" + str(self.value) + "'"}
        u = Utility()
        search_dict = u.remove_empty_items_fr_dict(search_dict)
        res = self.DB_MANAGER.query_bool(search_dict, self.table_class)
        return res
    def on_pushButton_sort_pressed(self):
        #from sortpanelmain import SortPanelMain
        #if self.check_record_state() == 1:
            #pass
        #else:
        dlg = SortPanelMain(self)
        dlg.insertItems(self.SORT_ITEMS)
        dlg.exec_()
        items,order_type = dlg.ITEMS, dlg.TYPE_ORDER
        self.SORT_ITEMS_CONVERTED = []
        for i in items:
            self.SORT_ITEMS_CONVERTED.append(self.CONVERSION_DICT[str(i)])
        self.SORT_MODE = order_type
        #self.empty_fields()
        id_list = []
        for i in self.DATA_LIST:
            id_list.append(eval("i." + self.ID_TABLE_THUMB))
        self.DATA_LIST = []
        temp_data_list = self.DB_MANAGER.query_sort(id_list, self.SORT_ITEMS_CONVERTED, self.SORT_MODE, self.MAPPER_TABLE_CLASS_thumb, self.ID_TABLE_THUMB)
        for i in temp_data_list:
            self.DATA_LIST.append(i)
        self.BROWSE_STATUS = "b"
        self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
        # if type(self.REC_CORR) == "<type 'str'>":
            # corr = 0
        # else:
            # corr = self.REC_CORR
        self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
        self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
        self.SORT_STATUS = "o"
        self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
        self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR+1)
        self.fill_fields()
    def insert_new_row(self, table_name):
        """insert new row into a table based on table_name"""
        cmd = table_name + ".insertRow(0)"
        eval(cmd)
    # def prova_remove(self):
        # model = self.model
        # indices = self.tableWidgetTags_US.selectionModel().selectedRows() 
        # for index in sorted(indices):
            # model.removeRow(index.row()) 
            # index_list = []                                                          
        # for model_index in self.tableWidgetTags_US.selectionModel().selectedRows():       
            # index = QPersistentModelIndex(model_index)         
            # index_list.append(index)                                             
        # for index in index_list:                                      
             # self.model.removeRow(index.row())
    def remove_row(self, table_name):
        """remove row into a table based on table_name"""
        table_row_count_cmd = ("%s.rowCount()") % (table_name)
        table_row_count = eval(table_row_count_cmd)
        row_index = table_row_count - 1
        cmd = ("%s.removeRow(%d)") % (table_name, row_index)
        eval(cmd)
    def remove_rowall(self, table_name):
        """remove row into a table based on table_name"""
        table_row_count_cmd = ("%s.currentRow()") % (table_name)
        table_row_count = eval(table_row_count_cmd)
        cmd = ("%s.removeRow") % (table_name)
        eval(cmd)    
    # def nothing(self,x):
        # pass
    def openWide_image(self):
        items = self.iconListWidget.selectedItems()
        conn = Connection()
        conn_str = conn.conn_str()
        thumb_resize = conn.thumb_resize()
        thumb_resize_str = thumb_resize['thumb_resize']
        for item in items:
            dlg = ImageViewer()
            id_orig_item = item.text()  # return the name of original file
            search_dict = {'media_filename': "'" + str(id_orig_item) + "'", 'mediatype': "'" + 'video' + "'"}
            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)
            
            res = self.DB_MANAGER.query_bool(search_dict, "MEDIA_THUMB")
            
            
            search_dict_2 = {'media_filename': "'" + str(id_orig_item) + "'", 'mediatype': "'" + 'image' + "'"}
            
            search_dict_2 = u.remove_empty_items_fr_dict(search_dict_2)
            
            res_2 = self.DB_MANAGER.query_bool(search_dict_2, "MEDIA_THUMB")
            
            search_dict_3 = {'media_filename': "'" + str(id_orig_item) + "'"}  
            
            search_dict_3 = u.remove_empty_items_fr_dict(search_dict_3)
            
            res_3 = self.DB_MANAGER.query_bool(search_dict_3, "MEDIA_THUMB")
            
            file_path_3 = str(res_3[0].path_resize)
            if bool(res):
                if platform.system=='Windows':
                    os.startfile(str(thumb_resize_str+file_path_3))
            
                else:
                    os.system('open ' + str(thumb_resize_str+file_path_3))
            else:
                pass
            if bool(res_2):
                dlg.show_image(str(thumb_resize_str+file_path_3))  
                dlg.exec_()
            else:
                pass
    def charge_sito_list(self):
        sito_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('site_table', 'sito', 'SITE'))
        try:
            sito_vl.remove('')
        except:
            pass
        sito_vl.sort()
        return sito_vl
    
    def charge_area_us_list(self):
        sito_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('us_table', 'area', 'US'))
        try:
            sito_vl.remove('')
        except:
            pass
        sito_vl.sort()
        return sito_vl
    def charge_us_us_list(self):
        sito_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('us_table', str('us'), 'US'))
        try:
            sito_vl.remove('')
        except:
            pass
        sito_vl.sort()
        return sito_vl
    def charge_sigla_us_list(self):
        sito_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('struttura_table', 'sigla_struttura', 'STRUTTURA'))
        try:
            sito_vl.remove('')
        except:
            pass
        sito_vl.sort()
        return sito_vl
    def charge_nr_us_list(self):
        sito_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('struttura_table', str('numero_struttura'), 'STRUTTURA'))
        try:
            sito_vl.remove('')
        except:
            pass
        sito_vl.sort()
        return sito_vl
    
    def generate_US(self):
        tags_list = self.table2dict('self.tableWidgetTags_US')
        record_us_list = []
        
        for sing_tags in tags_list:
            search_dict = {'sito': "'" + str(sing_tags[0]) + "'",
                           'area': "'" + str(sing_tags[1]) + "'",
                           'us': "'" + str(sing_tags[2]) + "'"
                           }
            record_us_list.append(self.DB_MANAGER.query_bool(search_dict, 'US'))
            
        if not record_us_list[0]:
            if self.L=='it':
                result=QMessageBox.warning(self, "Attenzione",  "Scheda US non presente. Vuoi generala? Clicca ok oppure Annulla per abortire", QMessageBox.Ok|QMessageBox.Cancel)
            elif self.L=='de':
                result=QMessageBox.warning(self, "Warnung", "SE-Karte nicht vorhanden. Sie wollen es generieren? Klicken Sie auf OK oder Abbrechen, um abzubrechen", QMessageBox.Ok|QMessageBox.Cancel)
            else:
                result=QMessageBox.warning(self, "Warning", "SU form not present. Do you want to generate it? Click OK or Cancel to abort", QMessageBox.Ok|QMessageBox.Cancel)    
                
            
            if result==QMessageBox.Ok:
                  
                rs= self.DB_MANAGER.insert_number_of_us_records(str(sing_tags[0]),str(sing_tags[1]),str(sing_tags[2]),'US')
                
                if self.L=='it':
                    QMessageBox.information(self, "Info",  "US creata", QMessageBox.Ok)
                if self.L=='de':
                    QMessageBox.information(self, "Info",  "Formular erstellt", QMessageBox.Ok)
                else:
                    QMessageBox.information(self, "Info",  "Form created", QMessageBox.Ok)
                
                return rs
            else:
                if self.L=='it':
                
                    QMessageBox.information(self, "Info", "Azione annullata", QMessageBox.Ok)
                elif self.L=='de':
                
                    QMessageBox.information(self, "Info", "Aktion abgebrochen", QMessageBox.Ok)
                else:
                
                    QMessageBox.information(self, "Info", "Action cancelled", QMessageBox.Ok)
                return
        us_list = []
        for r in record_us_list:
            
            us_list.append([r[0].id_us, 'US', 'us_table'])
        # QMessageBox.information(self, "Scheda US", str(us_list), QMessageBox.Ok)
        return us_list
    def remove_US(self):
        tags_list = self.table2dict('self.tableWidgetTags_US')
        record_us_list = []
        for sing_tags in tags_list:
                search_dict = {'sito': "'" + str(sing_tags[0]) + "'",
                           'area': "'" + str(sing_tags[1]) + "'",
                           'us': "'" + str(sing_tags[2]) + "'"
                           }
                record_us_list.remove(self.DB_MANAGER.query_bool(search_dict, 'US'))
        us_list = []
        for r in record_us_list:
            us_list.remove([r[0].id_us, 'US', 'us_table'])
        return us_list
    def generate_Reperti(self):
        tags_list = self.table2dict('self.tableWidgetTags_MAT')
        record_rep_list = []
        for sing_tags in tags_list:
            search_dict = {'sito': "'" + str(sing_tags[0]) + "'",
                           'numero_inventario': "'" + str(sing_tags[1]) + "'"
                           }
            record_rep_list.append(self.DB_MANAGER.query_bool(search_dict, 'INVENTARIO_MATERIALI'))
        if not record_rep_list[0]:
            if self.L=='it':
                result=QMessageBox.warning(self, "Attenzione",  "Scheda Reperti non presente. Vuoi generala? Clicca ok oppure Annulla per abortire", QMessageBox.Ok|QMessageBox.Cancel)
            elif self.L=='de':
                result=QMessageBox.warning(self, "Warnung", "Karte nicht vorhanden. Sie wollen es generieren? Klicken Sie auf OK oder Abbrechen, um abzubrechen", QMessageBox.Ok|QMessageBox.Cancel)
            else:
                result=QMessageBox.warning(self, "Warning", "Form not present. Do you want to generate it? Click OK or Cancel to abort", QMessageBox.Ok|QMessageBox.Cancel)    
            if result==QMessageBox.Ok:
                rs= self.DB_MANAGER.insert_number_of_reperti_records(str(sing_tags[0]),str(sing_tags[1]))
                if self.L=='it':
                    QMessageBox.information(self, "Info",  "Scheda creata", QMessageBox.Ok)
                if self.L=='de':
                    QMessageBox.information(self, "Info",  "Formular erstellt", QMessageBox.Ok)
                else:
                    QMessageBox.information(self, "Info",  "Form created", QMessageBox.Ok)
                
                return rs
            else:
                if self.L=='it':
                
                    QMessageBox.information(self, "Info", "Azione annullata", QMessageBox.Ok)
                elif self.L=='de':
                
                    QMessageBox.information(self, "Info", "Aktion abgebrochen", QMessageBox.Ok)
                else:
                
                    QMessageBox.information(self, "Info", "Action cancelled", QMessageBox.Ok)
                return    
        rep_list = []
        for r in record_rep_list:
            rep_list.append([r[0].id_invmat, 'REPERTO', 'inventario_materiali_table'])
        return rep_list
    def remove_reperti(self):
        tags_list = self.table2dict('self.tableWidgetTags_MAT')
        record_mat_list = []
        for sing_tags in tags_list:
                search_dict = {'sito': "'" + str(sing_tags[0]) + "'",
                           'numero_inventario': "'" + str(sing_tags[1]) + "'"
                           }
                record_mat_list.remove(self.DB_MANAGER.query_bool(search_dict, 'INVENTARIO_MATERIALI'))
        rep_list = []
        for r in record_rep_list:
            rep_list.append([r[0].id_invmat, 'REPERTO', 'inventario_materiali_table'])
        return rep_list
    
    def generate_Tombe(self):
        tags_list = self.table2dict('self.tableWidgetTags_tomba')
        record_tmb_list = []
        for sing_tags in tags_list:
            search_dict = {'sito': "'" + str(sing_tags[0]) + "'",
                           'nr_scheda_taf': "'" + str(sing_tags[1]) + "'"
                           }
            record_tmb_list.append(self.DB_MANAGER.query_bool(search_dict, 'TOMBA'))
        if not record_tmb_list[0]:
            if self.L=='it':
                result=QMessageBox.warning(self, "Attenzione",  "Scheda Tomba non presente. Vuoi generala? Clicca ok oppure Annulla per abortire", QMessageBox.Ok|QMessageBox.Cancel)
            elif self.L=='de':
                result=QMessageBox.warning(self, "Warnung", "Karte nicht vorhanden. Sie wollen es generieren? Klicken Sie auf OK oder Abbrechen, um abzubrechen", QMessageBox.Ok|QMessageBox.Cancel)
            else:
                result=QMessageBox.warning(self, "Warning", "Form not present. Do you want to generate it? Click OK or Cancel to abort", QMessageBox.Ok|QMessageBox.Cancel)  
            if result==QMessageBox.Ok:
                rs= self.DB_MANAGER.insert_number_of_tomba_records(str(sing_tags[0]),str(sing_tags[1]))
                if self.L=='it':
                    QMessageBox.information(self, "Info",  "Scheda creata", QMessageBox.Ok)
                if self.L=='de':
                    QMessageBox.information(self, "Info",  "Formular erstellt", QMessageBox.Ok)
                else:
                    QMessageBox.information(self, "Info",  "Form created", QMessageBox.Ok)
                
                return rs
            else:
                if self.L=='it':
                
                    QMessageBox.information(self, "Info", "Azione annullata", QMessageBox.Ok)
                elif self.L=='de':
                
                    QMessageBox.information(self, "Info", "Aktion abgebrochen", QMessageBox.Ok)
                else:
                
                    QMessageBox.information(self, "Info", "Action cancelled", QMessageBox.Ok)
                return    
        tmb_list = []
        for r in record_tmb_list:
            tmb_list.append([r[0].id_tomba, 'TOMBA', 'tomba_table'])
        return tmb_list
    def remove_Tombe(self):
        tags_list = self.table2dict('self.tableWidgetTags_tomba')
        record_tmb_list = []
        for sing_tags in tags_list:
                search_dict = {'sito': "'" + str(sing_tags[0]) + "'",
                           'nr_scheda_taf': "'" + str(sing_tags[1]) + "'"
                           }
                record_tmb_list.remove(self.DB_MANAGER.query_bool(search_dict, 'TOMBA'))
        tmb_list = []
        for r in record_tmb_list:
            tmb_list.append([r[0].id_tomba, 'TOMBA', 'tomba_table'])
        return tmb_list
    
    
    def generate_Tombe_2(self):
        tags_list = self.table2dict('self.tableWidgetTags_tomba_2')
        record_tmb_list = []
        for sing_tags in tags_list:
            search_dict = {'sito': "'" + str(sing_tags[0]) + "'",
                           'sigla_struttura': "'" + str(sing_tags[1]) + "'",
                           'numero_struttura': "'" + str(sing_tags[2]) + "'"
                           
                           }
            record_tmb_list.append(self.DB_MANAGER.query_bool(search_dict, 'STRUTTURA'))
        if not record_tmb_list[0]:
            if self.L=='it':
                result=QMessageBox.warning(self, "Attenzione",  "Scheda Struttura non presente. Vuoi generala? Clicca ok oppure Annulla per abortire", QMessageBox.Ok|QMessageBox.Cancel)
            elif self.L=='de':
                result=QMessageBox.warning(self, "Warnung", "Karte nicht vorhanden. Sie wollen es generieren? Klicken Sie auf OK oder Abbrechen, um abzubrechen", QMessageBox.Ok|QMessageBox.Cancel)
            else:
                result=QMessageBox.warning(self, "Warning", "Form not present. Do you want to generate it? Click OK or Cancel to abort", QMessageBox.Ok|QMessageBox.Cancel)  
            if result==QMessageBox.Ok:
                rs= self.DB_MANAGER.insert_struttura_records(str(sing_tags[0]),str(sing_tags[1]),str(sing_tags[2]))
                if self.L=='it':
                    QMessageBox.information(self, "Info",  "Scheda creata", QMessageBox.Ok)
                if self.L=='de':
                    QMessageBox.information(self, "Info",  "Formular erstellt", QMessageBox.Ok)
                else:
                    QMessageBox.information(self, "Info",  "Form created", QMessageBox.Ok)
                
                return rs
            else:
                if self.L=='it':
                
                    QMessageBox.information(self, "Info", "Azione annullata", QMessageBox.Ok)
                elif self.L=='de':
                
                    QMessageBox.information(self, "Info", "Aktion abgebrochen", QMessageBox.Ok)
                else:
                
                    QMessageBox.information(self, "Info", "Action cancelled", QMessageBox.Ok)
                return    
        tmb_list = []
        for r in record_tmb_list:
            tmb_list.append([r[0].id_struttura, 'STRUTTURA', 'struttura_table'])
        return tmb_list
    def remove_Tombe_2(self):
        tags_list = self.table2dict('self.tableWidgetTags_tomba_2')
        record_tmb_list = []
        for sing_tags in tags_list:
                search_dict = {'sito': "'" + str(sing_tags[0]) + "'",
                           'sigla_struttura': "'" + str(sing_tags[1]) + "'",
                           'numero_struttura': "'" + str(sing_tags[2]) + "'"
                           
                           }
                record_tmb_list.remove(self.DB_MANAGER.query_bool(search_dict, 'STRUTTURA'))
        tmb_list = []
        for r in record_tmb_list:
            tmb_list.append([r[0].id_struttura, 'STRUTTURA', 'struttura_table'])
        return tmb_list
    
    
    def table2dict(self, n):
        self.tablename = n
        row = eval(self.tablename + ".rowCount()")
        col = eval(self.tablename + ".columnCount()")
        lista = []
        for r in range(row):
            sub_list = []
            for c in range(col):
                value = eval(self.tablename + ".item(r,c)")
                if value != None:
                    sub_list.append(str(value.text()))
            if bool(sub_list):
                lista.append(sub_list)
        return lista
    def charge_data(self):
        self.DATA = self.DB_MANAGER.query(self.MAPPER_TABLE_CLASS_thumb)
        self.open_images()
    def clear_thumb_images(self):
        self.iconListWidget.clear()
    def open_images(self):
        self.clear_thumb_images()
        thumb_path = conn.thumb_path()
        thumb_path_str = thumb_path['thumb_path']
        data_len = len(self.DATA)
        if self.NUM_DATA_BEGIN >= data_len:
            # Sono già state visualizzate tutte le immagini
            self.NUM_DATA_BEGIN = 0
            self.NUM_DATA_END = 25
        elif self.NUM_DATA_BEGIN<= data_len:
            # indica che non sono state visualizzate tutte le immagini
            data = self.DATA[self.NUM_DATA_BEGIN:self.NUM_DATA_END]
            for i in range(len(data)):
                item = QListWidgetItem(str(data[i].media_filename)) ###############visualizzo nome file
                # data_for_thumb = self.db_search_check(self.MAPPER_TABLE_CLASS_thumb, 'id_media', id_media) # recupera i valori della thumb in base al valore id_media del file originale
                thumb_path = data[i].filepath
                # QMessageBox.warning(self, "Errore",str(thumb_path),  QMessageBox.Ok)
                item.setData(Qt.UserRole, str(data[i].media_filename ))
                icon = QIcon(thumb_path_str+thumb_path)  # os.path.join('%s/%s' % (directory.toUtf8(), image)))
                item.setIcon(icon)
                self.iconListWidget.addItem(item)
                # Button utility
    def on_pushButton_dir_video_pressed(self):
        self.getDirectoryVideo()
    def on_pushButton_chose_dir_pressed(self):
        self.getDirectory()
    def on_pushButton_addRow_US_pressed(self):
        self.insert_new_row('self.tableWidgetTags_US')
    def on_pushButton_removeRow_US_pressed(self):
        self.remove_row('self.tableWidgetTags_US')
    def on_pushButton_addRow_MAT_pressed(self):
        self.insert_new_row('self.tableWidgetTags_MAT')
    def on_pushButton_removeRow_MAT_pressed(self):
        self.remove_row('self.tableWidgetTags_MAT')
    def on_pushButton_addRow_tomba_pressed(self):
        self.insert_new_row('self.tableWidgetTags_tomba')
    def on_pushButton_removeRow_tomba_pressed(self):
        self.remove_row('self.tableWidgetTags_tomba')
    def on_pushButton_addRow_tomba_2_pressed(self):
        self.insert_new_row('self.tableWidgetTags_tomba_2')
    def on_pushButton_removeRow_tomba__2_pressed(self):
        self.remove_row('self.tableWidgetTags_tomba_2') 
    def on_pushButton_assignTags_US_pressed(self):
        """
        id_mediaToEntity,
        id_entity,
        entity_type,
        table_name,
        id_media,
        filepath,
        media_name
        """
        items_selected =self.iconListWidget.selectedItems()
        us_list = self.generate_US()
        if not us_list:
            return
        for item in items_selected:
            for us_data in us_list:
                id_orig_item = item.text()  # return the name of original file
                search_dict = {'filename': "'" + str(id_orig_item) + "'"}
                media_data = self.DB_MANAGER.query_bool(search_dict, 'MEDIA')
                self.insert_mediaToEntity_rec(us_data[0], us_data[1], us_data[2], media_data[0].id_media,
                                              media_data[0].filepath, media_data[0].filename)
    def on_pushButton_assignTags_MAT_pressed(self):
        """
        id_mediaToEntity,
        id_entity,
        entity_type,
        table_name,
        id_media,
        filepath,
        media_name
        """
        items_selected = self.iconListWidget.selectedItems()
        reperti_list = self.generate_Reperti()
        if not reperti_list:
            return
        for item in items_selected:
            for reperti_data in reperti_list:
                id_orig_item = item.text()  # return the name of original file
                search_dict = {'filename': "'" + str(id_orig_item) + "'"}
                media_data = self.DB_MANAGER.query_bool(search_dict, 'MEDIA')
                self.insert_mediaToEntity_rec(reperti_data[0], reperti_data[1], reperti_data[2], media_data[0].id_media,
                                              media_data[0].filepath, media_data[0].filename)
    
    
    def on_pushButton_assignTags_tomba_pressed(self):
        """
        id_mediaToEntity,
        id_entity,
        entity_type,
        table_name,
        id_media,
        filepath,
        media_name
        """
        items_selected = self.iconListWidget.selectedItems()
        reperti_list = self.generate_Tombe()
        if not reperti_list:
            return
        for item in items_selected:
            for reperti_data in reperti_list:
                id_orig_item = item.text()  # return the name of original file
                search_dict = {'filename': "'" + str(id_orig_item) + "'"}
                media_data = self.DB_MANAGER.query_bool(search_dict, 'MEDIA')
                self.insert_mediaToEntity_rec(reperti_data[0], reperti_data[1], reperti_data[2], media_data[0].id_media,
                                              media_data[0].filepath, media_data[0].filename)
    
    
    
    def on_pushButton_assignTags_tomba_2_pressed(self):
        """
        id_mediaToEntity,
        id_entity,
        entity_type,
        table_name,
        id_media,
        filepath,
        media_name
        """
        items_selected = self.iconListWidget.selectedItems()
        reperti_list = self.generate_Tombe_2()
        if not reperti_list:
            return
        for item in items_selected:
            for reperti_data in reperti_list:
                id_orig_item = item.text()  # return the name of original file
                search_dict = {'filename': "'" + str(id_orig_item) + "'"}
                media_data = self.DB_MANAGER.query_bool(search_dict, 'MEDIA')
                self.insert_mediaToEntity_rec(reperti_data[0], reperti_data[1], reperti_data[2], media_data[0].id_media,
                                              media_data[0].filepath, media_data[0].filename)
    
    ##################################funzione per eliminare le thumbnail###########################################
    def on_pushButton_remove_thumb_pressed(self):
        items_selected = self.iconListWidget.selectedItems()
        if bool (items_selected):
            if self.L=='it':
            
                msg = QMessageBox.warning(self, "Attenzione",
                                      "Vuoi veramente eliminare la thumb selezionata? \n L'azione è irreversibile",
                                      QMessageBox.Ok | QMessageBox.Cancel)
                if msg == QMessageBox.Cancel:
                    QMessageBox.warning(self, "Info", "Azione Annullata!")
                else:
                    try:
                        for item in items_selected:
                            id_orig_item = item.text()  # return the name of original file
                            s= str(id_orig_item)
                            self.DB_MANAGER.delete_thumb_from_db_sql(s)
                    except Exception as e:
                        QMessageBox.warning(self, "Info", "error: " + str(e))    
                    self.iconListWidget.clear()
                    self.charge_data()
                    self.view_num_rec()
                    QMessageBox.warning(self, "Info", "Thumbnail eliminate")
            elif self.L=='de':
            
                msg = QMessageBox.warning(self, "Warnung",
                                      "Wollen Sie den ausgewählten Daumen wirklich beseitigen? \Die Aktion ist unumkehrbar",
                                      QMessageBox.Ok | QMessageBox.Cancel)
                if msg == QMessageBox.Cancel:
                    QMessageBox.warning(self, "Info", "Aktion abgebrochen")
                else:
                    try:
                        for item in items_selected:
                            id_orig_item = item.text()  # return the name of original file
                            s= str(id_orig_item)
                            self.DB_MANAGER.delete_thumb_from_db_sql(s)
                    except Exception as e:
                        QMessageBox.warning(self, "Info", "error: " + str(e))    
                    self.iconListWidget.clear()
                    self.charge_data()
                    self.view_num_rec()
                    QMessageBox.warning(self, "Info", "Thumbnail gelöscht")
            
            else:
            
                msg = QMessageBox.warning(self, "Warning",
                                      "Do you really want to delete the selected thumb? \n The action is irreversible",
                                      QMessageBox.Ok | QMessageBox.Cancel)
                if msg == QMessageBox.Cancel:
                    QMessageBox.warning(self, "Info", "Action cancelled")
                else:
                    try:
                        for item in items_selected:
                            id_orig_item = item.text()  # return the name of original file
                            s= str(id_orig_item)
                            self.DB_MANAGER.delete_thumb_from_db_sql(s)
                    except Exception as e:
                        QMessageBox.warning(self, "Info", "error: " + str(e))    
                    self.iconListWidget.clear()
                    self.charge_data()
                    self.view_num_rec()
                    QMessageBox.warning(self, "Info", "Thumbnail deleted")
        else:
            if self.L=='it':
                QMessageBox.warning(self, "Info", "devi selezionare una thumbnail!")
            elif self.L=='de':
                QMessageBox.warning(self, "Info", "Sie müssen eine Miniaturansicht auswählen")
            else:
                QMessageBox.warning(self, "Info", "you must select a thumbnail")
    
    ###################funzione poer rimuovere un tag alla volta dal tabklewidget##############
    def on_pushButton_remove_tags_pressed(self):
        if not bool(self.tableWidget_tags.selectedItems()):
            if self.L=='it':
                
                msg = QMessageBox.warning(self, "Attenzione!!!",
                                      "devi selezionare prima un tag",
                                      QMessageBox.Ok)
        
            elif self.L=='de':
                
                msg = QMessageBox.warning(self, "Warnung",
                                      "Sie müssen zuerst ein Tag auswählen",
                                      QMessageBox.Ok)
            else:
                
                msg = QMessageBox.warning(self, "Warning",
                                      "you must first select a tag",
                                      QMessageBox.Ok)
        else:
            if self.L=='it':
                msg = QMessageBox.warning(self, "Warning",
                                          "Vuoi veramente cancellare i tags dalle thumbnail selezionate? \n L'azione è irreversibile",
                                          QMessageBox.Ok | QMessageBox.Cancel)
                if msg == QMessageBox.Cancel:
                    QMessageBox.warning(self, "Messaggio!!!", "Azione Annullata!")
                else:
                    items_selected = self.tableWidget_tags.selectedItems()
                for item in items_selected:
                    id_orig_item = item.text()  # return the name of original file
                    s= self.tableWidget_tags.item(0,0).text()
                    self.DB_MANAGER.remove_tags_from_db_sql(s)
                QMessageBox.warning(self, "Info", "Tags rimossi!")
            elif self.L=='de':
                msg = QMessageBox.warning(self, "Warning",
                                          "Wollen Sie wirklich die Tags aus den ausgewählten Miniaturbildern löschen? \n Die Aktion ist unumkehrbar",
                                          QMessageBox.Ok | QMessageBox.Cancel)
                if msg == QMessageBox.Cancel:
                    QMessageBox.warning(self, "Warnung", "Azione Annullata!")
                else:
                    items_selected = self.tableWidget_tags.selectedItems()
                for item in items_selected:
                    id_orig_item = item.text()  # return the name of original file
                    s= self.tableWidget_tags.item(0,0).text()
                    self.DB_MANAGER.remove_tags_from_db_sql(s)
                QMessageBox.warning(self, "Info", "Tags entfernt")
    
            else:
                msg = QMessageBox.warning(self, "Warning",
                                          "Do you really want to delete the tags from the selected thumbnails? \n The action is irreversible",
                                          QMessageBox.Ok | QMessageBox.Cancel)
                if msg == QMessageBox.Cancel:
                    QMessageBox.warning(self, "Warning", "Action cancelled")
                else:
                    items_selected = self.tableWidget_tags.selectedItems()
                for item in items_selected:
                    id_orig_item = item.text()  # return the name of original file
                    s= self.tableWidget_tags.item(0,0).text()
                    self.DB_MANAGER.remove_tags_from_db_sql(s)
                QMessageBox.warning(self, "Info", "Tags removed")
    
    
    
    
    #######################funzione per rimuovere tutti i tag da una foto da selezione thumbnail#########################
    def on_pushButton_remove_alltag_pressed(self):
        items_selected = self.iconListWidget.selectedItems()
        if bool (items_selected):
            if self.L=='it':
                msg = QMessageBox.warning(self, "Attenzione!!!",
                                          "Vuoi veramente eliminare tutti i tags dalle immagini selezionate? \n L'azione è irreversibile",
                                          QMessageBox.Ok | QMessageBox.Cancel)
                if msg == QMessageBox.Cancel:
                    QMessageBox.warning(self, "Info", "Azione Annullata!")
                else:
                    try:
                        for item in items_selected:
                            id_orig_item = item.text()  # return the name of original file
                            s= str(id_orig_item)
                            self.DB_MANAGER.remove_alltags_from_db_sql(s)
                    except Exception as e:
                        QMessageBox.warning(self, "Info", "error: " + str(e))    
                    self.iconListWidget.clear()
                    self.charge_data()
                    self.view_num_rec()
                    QMessageBox.warning(self, "Info", "Tags eliminati!")
            elif self.L=='de':
                msg = QMessageBox.warning(self, "Warnung",
                                          "Wollen Sie wirklich alle Tags aus den ausgewählten Bildern löschen? \n Die Aktion ist unumkehrbar",
                                          QMessageBox.Ok | QMessageBox.Cancel)
                if msg == QMessageBox.Cancel:
                    QMessageBox.warning(self, "Info", "Aktion abgebrochen")
                else:
                    try:
                        for item in items_selected:
                            id_orig_item = item.text()  # return the name of original file
                            s= str(id_orig_item)
                            self.DB_MANAGER.remove_alltags_from_db_sql(s)
                    except Exception as e:
                        QMessageBox.warning(self, "Info", "error: " + str(e))    
                    self.iconListWidget.clear()
                    self.charge_data()
                    self.view_num_rec()
                    QMessageBox.warning(self, "Info", "Tags entfernt")
        
            else:
                msg = QMessageBox.warning(self, "Worning",
                                          "Do you really want to delete all tags from the selected images? \n The action is irreversible",
                                          QMessageBox.Ok | QMessageBox.Cancel)
                if msg == QMessageBox.Cancel:
                    QMessageBox.warning(self, "Info", "Action cancelled")
                else:
                    try:
                        for item in items_selected:
                            id_orig_item = item.text()  # return the name of original file
                            s= str(id_orig_item)
                            self.DB_MANAGER.remove_alltags_from_db_sql(s)
                    except Exception as e:
                        QMessageBox.warning(self, "Info", "error: " + str(e))    
                    self.iconListWidget.clear()
                    self.charge_data()
                    self.view_num_rec()
                    QMessageBox.warning(self, "Info", "Tags removed")
        
        
        
        
        else:
            
            if self.L=='it':
                QMessageBox.warning(self, "Info", "devi selezionare almeno una thumbnail!")
            elif self.L=='de':
                QMessageBox.warning(self, "Info", "Sie müssen mindestens eine Miniaturansicht auswählen")    
            else:
                QMessageBox.warning(self, "Info", "you must select at least one thumbnail")    
    def on_pushButton_openMedia_pressed(self):
        self.charge_data()
        self.view_num_rec()
    def on_pushButton_next_rec_pressed(self):
        if self.NUM_DATA_END < len(self.DATA):
            self.NUM_DATA_BEGIN += 25
            self.NUM_DATA_END +=25
            self.view_num_rec()
            self.open_images()
    def on_pushButton_prev_rec_pressed(self):
        if self.NUM_DATA_BEGIN > 0:
            self.NUM_DATA_BEGIN -= 25
            self.NUM_DATA_END -= 25
            self.view_num_rec()
            self.open_images()
    def on_pushButton_first_rec_pressed(self):
        self.NUM_DATA_BEGIN = 0
        self.NUM_DATA_END = 25
        self.view_num_rec()
        self.open_images()
    def on_pushButton_last_rec_pressed(self):
        self.NUM_DATA_BEGIN = len(self.DATA) -25
        self.NUM_DATA_END = len(self.DATA)
        self.view_num_rec()
        self.open_images()
    def update_if(self, msg):
        rec_corr = self.REC_CORR
        self.msg = msg
        if self.msg == 1:
            test = self.update_record()
            if test == 1:
                id_list = []
                for i in self.DATA_LIST:
                    id_list.append(eval("i."+ self.ID_TABLE_THUMB))
                self.DATA_LIST = []
                if self.SORT_STATUS == "n":
                    temp_data_list = self.DB_MANAGER.query_sort(id_list, [self.ID_TABLE_THUMB], 'asc', self.MAPPER_TABLE_CLASS_thumb, self.ID_TABLE_THUMB) #self.DB_MANAGER.query_bool(self.SEARCH_DICT_TEMP, self.MAPPER_TABLE_CLASS) #
                else:
                    temp_data_list = self.DB_MANAGER.query_sort(id_list, self.SORT_ITEMS_CONVERTED, self.SORT_MODE, self.MAPPER_TABLE_CLASS_thumb, self.ID_TABLE_THUMB)
                for i in temp_data_list:
                    self.DATA_LIST.append(i)
                self.BROWSE_STATUS = "b"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                if type(self.REC_CORR) == "<type 'str'>":
                    corr = 0
                else:
                    corr = self.REC_CORR
                return 1
            elif test == 0:
                return 0
    def update_record(self):
        try:
            self.DB_MANAGER.update(self.MAPPER_TABLE_CLASS_thumb,
                        self.ID_TABLE_THUMB,
                        [eval("int(self.DATA_LIST[self.REC_CORR]." + self.ID_TABLE_THUMB+")")],
                        self.TABLE_FIELDS,
                        self.rec_toupdate())
            return 1
        except Exception as e:
            str(e)
            save_file='{}{}{}'.format(self.HOME, os.sep,"pyarchinit_Report_folder") 
            file_=os.path.join(save_file,'error_encodig_data_recover.txt')
            with open(file_, "a") as fh:
                try:
                    raise ValueError(str(e))
                except ValueError as s:
                    print(s, file=fh)
            if self.L=='it':
                QMessageBox.warning(self, "Messaggio",
                                    "Problema di encoding: sono stati inseriti accenti o caratteri non accettati dal database. Verrà fatta una copia dell'errore con i dati che puoi recuperare nella cartella pyarchinit_Report _Folder", QMessageBox.Ok)
            
            
            elif self.L=='de':
                QMessageBox.warning(self, "Message",
                                    "Encoding problem: accents or characters not accepted by the database were entered. A copy of the error will be made with the data you can retrieve in the pyarchinit_Report _Folder", QMessageBox.Ok) 
            else:
                QMessageBox.warning(self, "Message",
                                    "Kodierungsproblem: Es wurden Akzente oder Zeichen eingegeben, die von der Datenbank nicht akzeptiert werden. Es wird eine Kopie des Fehlers mit den Daten erstellt, die Sie im pyarchinit_Report _Ordner abrufen können", QMessageBox.Ok)
            return 0
    def rec_toupdate(self):
        rec_to_update = self.UTILITY.pos_none_in_list(self.DATA_LIST_REC_TEMP)
        return rec_to_update
        self.DATA_LIST = []
        id_list = []
        if self.DB_SERVER == 'sqlite':
            for i in self.DB_MANAGER.query(self.MAPPER_TABLE_CLASS_thumb):
                id_list.append(eval("i."+ self.ID_TABLE_THUMB))#for i in self.DB_MANAGER.query(eval(self.MAPPER_TABLE_CLASS_thumb)):
                #self.DATA_LIST.append(i)
        else:
            id_list = []
            for i in self.DB_MANAGER.query(self.MAPPER_TABLE_CLASS_thumb):
                id_list.append(eval("i."+ self.ID_TABLE_THUMB))
            temp_data_list = self.DB_MANAGER.query_sort(id_list, [self.ID_TABLE_THUMB], 'asc', self.MAPPER_TABLE_CLASS_thumb, self.ID_TABLE_THUMB)
            for i in temp_data_list:
                self.DATA_LIST.append(i)
    def table2dict(self, n):
        self.tablename = n
        row = eval(self.tablename+".rowCount()")
        col = eval(self.tablename+".columnCount()")
        lista=[]
        for r in range(row):
            sub_list = []
            for c in range(col):
                value = eval(self.tablename+".item(r,c)")
                if value != None:
                    sub_list.append(unicode(value.text()))
            if bool(sub_list) == True:
                lista.append(sub_list)
        return lista
    def view_num_rec(self):
        num_data_begin = self.NUM_DATA_BEGIN
        num_data_begin +=1
        num_data_end = self.NUM_DATA_END
        if self.NUM_DATA_END < len(self.DATA):
            pass
        else:
            num_data_end = len(self.DATA)
        self.label_num_tot_immagini.setText(str(len(self.DATA)))
        img_visualizzate_txt = ('%s %d to %d') % ("da",num_data_begin,num_data_end )
        self.label_img_visualizzate.setText(img_visualizzate_txt)
    def on_toolButton_tags_on_off_clicked(self):
        items = self.iconListWidget.selectedItems()
        if len(items) > 0:
            # QMessageBox.warning(self, "Errore", "Vai Gigi 1",  QMessageBox.Ok)
            self.open_tags()
    def open_tags(self):
        if self.toolButton_tags_on_off.isChecked():
            items = self.iconListWidget.selectedItems()
            items_list = []
            mediaToEntity_list = []
            for item in items:
                id_orig_item = item.text()  # return the name of original file
                search_dict = {'filename': "'" + str(id_orig_item) + "'"}
                u = Utility()
                search_dict = u.remove_empty_items_fr_dict(search_dict)
                res_media = self.DB_MANAGER.query_bool(search_dict, "MEDIA")
                ##          if bool(items) == True:
                ##              res_media = []
                ##              for item in items:
                ##                  res_media = []
                ##                  id_orig_item = item.text() #return the name of original file
                ##                  search_dict = {'id_media' : "'"+str(id_orig_item)+"'"}
                ##                  u = Utility()
                ##                  search_dict = u.remove_empty_items_fr_dict(search_dict)
                ##                  res_media = self.DB_MANAGER.query_bool(search_dict, "MEDIA")
                if bool(res_media):
                    for sing_media in res_media:
                        search_dict = {'media_name': "'" + str(id_orig_item) + "'"}
                        u = Utility()
                        search_dict = u.remove_empty_items_fr_dict(search_dict)
                        res_mediaToEntity = self.DB_MANAGER.query_bool(search_dict, "MEDIATOENTITY")
                    if bool(res_mediaToEntity):
                        for sing_res_media in res_mediaToEntity:
                            if sing_res_media.entity_type == 'US':
                                search_dict = {'id_us': "'" + str(sing_res_media.id_entity) + "'"}
                                u = Utility()
                                search_dict = u.remove_empty_items_fr_dict(search_dict)
                                us_data = self.DB_MANAGER.query_bool(search_dict, "US")
                                US_string = ('Sito: %s - Area: %s - US: %d') % (
                                    us_data[0].sito, us_data[0].area, us_data[0].us)
                                ##              #else
                                mediaToEntity_list.append(
                                    [str(sing_res_media.id_entity), sing_res_media.entity_type, US_string])
                            elif sing_res_media.entity_type == 'REPERTO':
                                search_dict = {'id_invmat': "'" + str(sing_res_media.id_entity) + "'"}
                                u = Utility()
                                search_dict = u.remove_empty_items_fr_dict(search_dict)
                                rep_data = self.DB_MANAGER.query_bool(search_dict, "INVENTARIO_MATERIALI")
                                Rep_string = ('Sito: %s - N. Inv.: %d') % (
                                    rep_data[0].sito, rep_data[0].numero_inventario)
                                ##              #else
                                mediaToEntity_list.append(
                                    [str(sing_res_media.id_entity), sing_res_media.entity_type, Rep_string])
                                    
                            elif sing_res_media.entity_type == 'TOMBA':
                                search_dict = {'id_tomba': "'" + str(sing_res_media.id_entity) + "'"}
                                u = Utility()
                                search_dict = u.remove_empty_items_fr_dict(search_dict)
                                rep_data = self.DB_MANAGER.query_bool(search_dict, "TOMBA")
                                TMB_string = ('Sito: %s - N. Tomba.: %d') % (
                                    rep_data[0].sito, rep_data[0].nr_scheda_taf)
                                ##              #else
                                mediaToEntity_list.append(
                                    [str(sing_res_media.id_entity), sing_res_media.entity_type, TMB_string])        
                            elif sing_res_media.entity_type == 'STRUTTURA':
                                search_dict = {'id_struttura': "'" + str(sing_res_media.id_entity) + "'"}
                                u = Utility()
                                search_dict = u.remove_empty_items_fr_dict(search_dict)
                                rep_data = self.DB_MANAGER.query_bool(search_dict, "STRUTTURA")
                                ST_string = ('Sito: %s - Sigla St.: %s - Nr St.: %d') % (
                                    rep_data[0].sito, rep_data[0].sigla_struttura, rep_data[0].numero_struttura)
                                ##              #else
                                mediaToEntity_list.append(
                                    [str(sing_res_media.id_entity), sing_res_media.entity_type, ST_string])            
            if bool(mediaToEntity_list):
                tags_row_count = self.tableWidget_tags.rowCount()
                for i in range(tags_row_count):
                    self.tableWidget_tags.removeRow(0)
                self.tableInsertData('self.tableWidget_tags', str(mediaToEntity_list))
            if not bool(items):
                tags_row_count = self.tableWidget_tags.rowCount()
                for i in range(tags_row_count):
                    self.tableWidget_tags.removeRow(0)
            items = []
    def charge_records(self):
        self.DATA_LIST = []
        id_list = []
        if self.DB_SERVER == 'sqlite':
            for i in self.DB_MANAGER.query(self.MAPPER_TABLE_CLASS_thumb):
                id_list.append(eval("i."+ 'media_filename'))#for i in self.DB_MANAGER.query(self.MAPPER_TABLE_CLASS_thumb):
                #self.DATA_LIST.append(i)
        else:
            for i in self.DB_MANAGER.query(self.MAPPER_TABLE_CLASS_thumb):
                id_list.append(eval("i."+ 'media_filename'))
            temp_data_list = self.DB_MANAGER.query_sort(id_list, ['media_filename'], 'asc', self.MAPPER_TABLE_CLASS_thumb, 'media_filename')
            for i in temp_data_list:
                self.DATA_LIST.append(i)
    def datestrfdate(self):
        now = date.today()
        today = now.strftime("%d-%m-%Y")
        return today
    def yearstrfdate(self):
        now = date.today()
        year = now.strftime("%Y")
        return year
    def set_rec_counter(self, t, c):
        self.rec_tot = t
        self.rec_corr = c
        self.label_rec_tot.setText(str(self.rec_tot))
        self.label_rec_corrente.setText(str(self.rec_corr))
    def set_LIST_REC_TEMP(self):
        self.DATA_LIST_REC_TEMP = [
            str(self.comboBox_sito.currentText()),  # 1 - Sito
            str(self.comboBox_area.currentText()),  # 2 - Area
            str(self.comboBox_us.currentText.text()),
            str(self.comboBox_sigla_struttura.currentText()),
            str(self.comboBox_nr_struttura.currentText())]
    def empty_fields(self):
        self.comboBox_sito.setEditText("")  # 1 - Sito
        self.comboBox_area.setEditText("")  # 2 - Area
        self.comboBox_us.setEditText("")  # 1 - US
        self.comboBox_sigla_struttura.setEditText("")
        self.comboBox_nr_struttura.setEditText("")
    def fill_fields(self, n=0):
        self.rec_num = n
        #QMessageBox.warning(self, "check fill fields", str(self.rec_num),  QMessageBox.Ok)
        # try:
            # str(self.comboBox_sito.setEditText(self.DATA_LIST[self.rec_num].sito))  # 1 - Sito
            # str(self.comboBox_area.setEditText(self.DATA_LIST[self.rec_num].area))
            # str(self.comboBox_us.setEditText(self.DATA_LIST[self.rec_num].us))
        # except Exception as  e:
            # QMessageBox.warning(self, "Error Fill Fields", str(e),  QMessageBox.Ok)
    def setComboBoxEnable(self, f, v):
        field_names = f
        value = v
        for fn in field_names:
            cmd = ('%s%s%s%s') % (fn, '.setEnabled(', v, ')')
            eval(cmd)
    def setComboBoxEditable(self, f, n):
        field_names = f
        value = n
        for fn in field_names:
            cmd = '{}{}{}{}'.format(fn, '.setEditable(', n, ')')
            eval(cmd)
    def setTableEnable(self, t, v):
        tab_names = t
        value = v
        for tn in tab_names:
            cmd = ('%s%s%s%s') % (tn, '.setEnabled(', v, ')')
            eval(cmd)
    def set_LIST_REC_CORR(self):
        self.DATA_LIST_REC_CORR = []
        for i in self.TABLE_FIELDS:
            self.DATA_LIST_REC_CORR.append(eval("str(self.DATA_LIST[self.REC_CORR]." + i + ")"))
    def records_equal_check(self):
        #self.set_LIST_REC_TEMP()
        self.set_LIST_REC_CORR()
        #test
        #QMessageBox.warning(self, "ATTENZIONE", str(self.DATA_LIST_REC_CORR) + " temp " + str(self.DATA_LIST_REC_TEMP), QMessageBox.Ok)
        check_str = str(self.DATA_LIST_REC_CORR) + " " + str(self.DATA_LIST_REC_TEMP)
        if self.DATA_LIST_REC_CORR == self.DATA_LIST_REC_TEMP:
            return 0
        else:
            return 1
    def tableInsertData(self, t, d):
        """Set the value into alls Grid"""
        self.table_name = t
        self.data_list = eval(d)
        self.data_list.sort()
        # column table count
        table_col_count_cmd = ("%s.columnCount()") % (self.table_name)
        table_col_count = eval(table_col_count_cmd)
        # clear table
        table_clear_cmd = ("%s.clearContents()") % (self.table_name)
        eval(table_clear_cmd)
        for i in range(table_col_count):
            table_rem_row_cmd = ("%s.removeRow(%d)") % (self.table_name, i)
            eval(table_rem_row_cmd)
            # for i in range(len(self.data_list)):
            # self.insert_new_row(self.table_name)
        for row in range(len(self.data_list)):
            cmd = ('%s.insertRow(%s)') % (self.table_name, row)
            eval(cmd)
            for col in range(len(self.data_list[row])):
                # item = self.comboBox_sito.setEditText(self.data_list[0][col]
                item = QTableWidgetItem(self.data_list[row][col])
                exec_str = ('%s.setItem(%d,%d,item)') % (self.table_name, row, col)
                eval(exec_str)
