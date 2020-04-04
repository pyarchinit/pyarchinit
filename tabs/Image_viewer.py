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
from builtins import range
from builtins import str
import PIL as Image
from PIL import *
from qgis.PyQt.QtCore import Qt,QSize
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QDialog, QMessageBox, QAbstractItemView, QListWidgetItem, QFileDialog, QTableWidgetItem
from qgis.PyQt.uic import loadUiType
from qgis.core import QgsSettings
from ..gui.imageViewer import ImageViewer
from ..modules.db.pyarchinit_conn_strings import *
from ..modules.db.pyarchinit_db_manager import *
from ..modules.db.pyarchinit_utility import *
from ..modules.utility.delegateComboBox import *
from ..modules.utility.pyarchinit_media_utility import *

MAIN_DIALOG_CLASS, _ = loadUiType(
    os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'pyarchinit_image_viewer_dialog.ui'))


class Main(QDialog, MAIN_DIALOG_CLASS):
    L=QgsSettings().value("locale/userLocale")[0:2]
    delegateSites = ''
    DB_MANAGER = ""
    TABLE_NAME = 'media_table'
    MAPPER_TABLE_CLASS = "MEDIA"
    ID_TABLE = "id_media"
    MAPPER_TABLE_CLASS_mediatoentity = 'MEDIATOENTITY'
    ID_TABLE_mediatoentity = 'id_mediaToEntity'
    NOME_SCHEDA = "Scheda Media Manager"

    TABLE_THUMB_NAME = 'media_thumb_table'
    MAPPER_TABLE_CLASS_thumb = 'MEDIA_THUMB'
    ID_TABLE_THUMB = "id_media_thumb"

    DATA_LIST = []
    DATA_LIST_REC_CORR = []
    DATA_LIST_REC_TEMP = []
    REC_CORR = 0
    REC_TOT = 0
    if L=='it':
        STATUS_ITEMS = {"b": "Usa", "f": "Trova", "n": "Nuovo Record"}
    else :
        STATUS_ITEMS = {"b": "Current", "f": "Find", "n": "New Record"}
    BROWSE_STATUS = "b"
    SORT_MODE = 'asc'
    if L=='it':
        SORTED_ITEMS = {"n": "Non ordinati", "o": "Ordinati"}
    else:
        SORTED_ITEMS = {"n": "Not sorted", "o": "Sorted"}
    SORT_STATUS = "n"
    
    
    
    UTILITY = Utility()

    #DATA = ''
    NUM_DATA_BEGIN = 0
    NUM_DATA_END = 25
    CONVERSION_DICT = {
    ID_TABLE_THUMB:ID_TABLE_THUMB,
    "ID Media" : "id_media"
    }
    SORT_ITEMS = [
                ID_TABLE_THUMB,
                "ID Media"
                ]
                
    TABLE_FIELDS = [
                    "id_media"
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
        self.iconListWidget.SelectionMode()
        self.iconListWidget.setSelectionMode(QAbstractItemView.MultiSelection)
        self.iconListWidget.itemDoubleClicked.connect(self.openWide_image)
        # self.connect(self.iconListWidget, SIGNAL("itemClicked(QListWidgetItem *)"),self.open_tags)
        self.iconListWidget.itemSelectionChanged.connect(self.open_tags)
        self.setWindowTitle("pyArchInit - Media Manager")
        self.charge_data()
        self.view_num_rec()

    def customize_gui(self):
        self.tableWidgetTags_US.setColumnWidth(0, 300)
        self.tableWidgetTags_US.setColumnWidth(1, 100)
        self.tableWidgetTags_US.setColumnWidth(2, 100)

        self.tableWidget_tags.setColumnWidth(2, 300)
        self.iconListWidget.setIconSize(QSize(100, 200))
        self.iconListWidget.setLineWidth(2)
        self.iconListWidget.setMidLineWidth(2)
        valuesSites = self.charge_sito_list()
        self.delegateSites = ComboBoxDelegate()
        self.delegateSites.def_values(valuesSites)
        self.delegateSites.def_editable('False')

        self.tableWidgetTags_US.setItemDelegateForColumn(0, self.delegateSites)

        self.tableWidgetTags_MAT.setItemDelegateForColumn(0, self.delegateSites)

        self.charge_sito_list()

    def connection(self):
        QMessageBox.warning(self, "Alert", "system under development", QMessageBox.Ok)

        conn = Connection()
        conn_str = conn.conn_str()
        '''try:
            self.DB_MANAGER = Pyarchinit_db_management(conn_str)
            self.DB_MANAGER.connection()
        except Exception as e:
            e = str(e)
            if e.find("no such table"):
                QMessageBox.warning(self, "Alert",
                                    "La connessione e' fallita <br><br> Tabella non presente. E' NECESSARIO RIAVVIARE QGIS",
                                    QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "Alert",
                                    "Attenzione rilevato bug! Segnalarlo allo sviluppatore<br> Errore: <br>" + str(e),
                                    QMessageBox.Ok)'''
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
                QMessageBox.warning(self, "WELCOME", "Welcome in pyArchInit" + self.NOME_SCHEDA + ". The database is empty. Push 'Ok' and good work!",  QMessageBox.Ok)
                self.charge_sito_list()
                self.BROWSE_STATUS = 'x'
                self.on_pushButton_new_rec_pressed()
        except Exception as  e:
            e = str(e)
    
    def enable_button(self, n):
        
        self.pushButton_view_all.setEnabled(n)

        self.pushButton_first_rec.setEnabled(n)

        self.pushButton_last_rec.setEnabled(n)

        self.pushButton_prev_rec.setEnabled(n)

        self.pushButton_next_rec.setEnabled(n)

        self.pushButton_delete.setEnabled(n)

        self.pushButton_new_search.setEnabled(n)

        self.pushButton_search_go.setEnabled(n)

        self.pushButton_sort.setEnabled(n)

    def enable_button_search(self, n):
        
        self.pushButton_view_all.setEnabled(n)

        self.pushButton_first_rec.setEnabled(n)

        self.pushButton_last_rec.setEnabled(n)

        self.pushButton_prev_rec.setEnabled(n)

        self.pushButton_next_rec.setEnabled(n)

        self.pushButton_delete.setEnabled(n)

        self.pushButton_save.setEnabled(n)

        self.pushButton_sort.setEnabled(n)
    
    def getDirectory(self):
        directory = QFileDialog.getExistingDirectory(self, "Directory", "Choose a directory:",
                                                     QFileDialog.ShowDirsOnly)

        if not directory:
            return 0

        #QMessageBox.warning(self, "Alert", str(dir(directory)), QMessageBox.Ok)
        for image in sorted(os.listdir(directory)):
            if image.endswith(".png") or image.endswith(".PNG") or image.endswith(".JPG") or image.endswith(
                    ".jpg") or image.endswith(".jpeg") or image.endswith(".JPEG") or image.endswith(
                ".tif") or image.endswith(".TIF") or image.endswith(".tiff") or image.endswith(".TIFF"):

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
                conn = Connection()
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
                filename_resize = str(media_max_num_id) + "_" + filename + media_resize_suffix
                
                filepath_thumb =  filename_thumb
                filepath_resize = filename_resize
                self.SORT_ITEMS_CONVERTED = []
                # crea la thumbnail
                try:
                    MU.resample_images(media_max_num_id, filepath, filenameorig, thumb_path_str, media_thumb_suffix)
                    MUR.resample_images(media_max_num_id, filepath, filenameorig, thumb_resize_str, media_resize_suffix)
                except Exception as e:
                    QMessageBox.warning(self, "Cucu", str(e), QMessageBox.Ok)

                    # inserisce i dati nel DB
                self.insert_record_mediathumb(media_max_num_id, mediatype, filename, filename_thumb, filetype,
                                              filepath_thumb, filepath_resize)

                
                item = QListWidgetItem(str(media_max_num_id))
                item.setData(Qt.UserRole, str(media_max_num_id))
                icon = QIcon(str(thumb_path_str)+filepath)  # os.path.join('%s/%s' % (directory.toUtf8(), image)))
                item.setIcon(icon)
                self.iconListWidget.addItem(item)

            elif bool(idunique_image_check):
                

                data = idunique_image_check
                id_media = data[0].id_media

                # visualizza le immagini nella ui
                item = QListWidgetItem(str(id_media))

                data_for_thumb = self.db_search_check(self.MAPPER_TABLE_CLASS_thumb, 'id_media',
                                                      id_media)  # recupera i valori della thumb in base al valore id_media del file originale

                thumb_path = data_for_thumb[0].filepath
                item.setData(Qt.UserRole, thumb_path)
                icon = QIcon(str(thumb_path_str)+filepath)  # os.path.join('%s/%s' % (directory.toUtf8(), image)))
                item.setIcon(icon)
                self.iconListWidget.addItem(item)

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
                QMessageBox.warning(self, "Errore", "Warning 1 ! \n"+ str(msg),  QMessageBox.Ok)
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
                QMessageBox.warning(self, "Error", "warming 1 ! \n"+ str(msg),  QMessageBox.Ok)
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
        self.empty_fields()

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

    def remove_row(self, table_name):
        """insert new row into a table based on table_name"""
        table_row_count_cmd = ("%s.rowCount()") % (table_name)
        table_row_count = eval(table_row_count_cmd)
        row_index = table_row_count - 1
        cmd = ("%s.removeRow(%d)") % (table_name, row_index)
        eval(cmd)

    def openWide_image(self):
        items = self.iconListWidget.selectedItems()
        conn = Connection()
        conn_str = conn.conn_str()
        thumb_resize = conn.thumb_resize()
        thumb_resize_str = thumb_resize['thumb_resize']
        for item in items:
            dlg = ImageViewer()
            id_orig_item = item.text()  # return the name of original file
            
            search_dict = {'media_filename': "'" + str(id_orig_item) + "'"}

            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)

            try:
                res = self.DB_MANAGER.query_bool(search_dict, "MEDIA_THUMB")
                file_path = str(res[0].path_resize)
            except Exception as e:
                QMessageBox.warning(self, "Error", "Warning 1 file: "+ str(e),  QMessageBox.Ok)

            dlg.show_image(str(thumb_resize_str+file_path))  # item.data(QtCore.Qt.UserRole).toString()))
            dlg.exec_()

    def charge_sito_list(self):
        sito_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('site_table', 'sito', 'SITE'))
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
            QMessageBox.warning(self, "Errore", "Scheda US non presente.", QMessageBox.Ok)
            return

        us_list = []
        for r in record_us_list:
            us_list.append([r[0].id_us, 'US', 'us_table'])
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
            QMessageBox.warning(self, "Errore", "Scheda Inventario materiali non presente", QMessageBox.Ok)
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
        conn=Connection()
        
        thumb_path = conn.thumb_path()
        thumb_path_str = thumb_path['thumb_path']
        
        self.clear_thumb_images()

        data_len = len(self.DATA)

        if self.NUM_DATA_BEGIN >= data_len:
            # Sono già state visualizzate tutte le immagini
            self.NUM_DATA_BEGIN = 0
            self.NUM_DATA_END = 1

        elif self.NUM_DATA_BEGIN <= data_len:
            # indica che non sono state visualizzate tutte le immagini

            data = self.DATA[self.NUM_DATA_BEGIN:self.NUM_DATA_END]
            for i in range(len(data)):
                item = QListWidgetItem(str(data[i].media_filename))

                # data_for_thumb = self.db_search_check(self.MAPPER_TABLE_CLASS_thumb, 'id_media', id_media) # recupera i valori della thumb in base al valore id_media del file originale

                thumb_path = data[i].filepath
                # QMessageBox.warning(self, "Errore",str(thumb_path),  QMessageBox.Ok)
                item.setData(Qt.UserRole, str(data[i].media_filename))
                icon = QIcon(thumb_path_str+thumb_path)  # os.path.join('%s/%s' % (directory.toUtf8(), image)))
                item.setIcon(icon)
                self.iconListWidget.addItem(item)

                # Button utility

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
        items_selected = self.iconListWidget.selectedItems()
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

    def on_pushButton_openMedia_pressed(self):
        self.charge_data()
        self.view_num_rec()

    def on_pushButton_next_rec_pressed(self):
        if self.NUM_DATA_BEGIN < len(self.DATA):
            self.NUM_DATA_BEGIN += 25
            self.NUM_DATA_END += 25
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
        self.NUM_DATA_BEGIN = len(self.DATA) - 25
        self.NUM_DATA_END = len(self.DATA)
        self.view_num_rec()
        self.open_images()
    def on_pushButton_view_all_pressed(self):
        self.empty_fields()
        self.charge_records()
        self.fill_fields()
        self.BROWSE_STATUS = "b"
        self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
        # if type(self.REC_CORR) == "<class 'str'>":
            # corr = 0
        # else:
            # corr = self.REC_CORR
        self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
        self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
        self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
        self.SORT_STATUS = "n"
        self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
    
    def on_pushButton_new_search_pressed(self):
        if self.BROWSE_STATUS != "f":
            pass
        else:
            self.enable_button_search(0)
    
        if self.BROWSE_STATUS != "f":
            self.BROWSE_STATUS = "f"
            self.setComboBoxEnable(['self.lineEdit_id_media'], 'True')
            
            
            self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
            self.set_rec_counter('','')
            self.label_sort.setText(self.SORTED_ITEMS["n"])
            self.charge_sito_list()
            self.empty_fields()
                
                
    def on_pushButton_search_go_pressed(self):
        #check_for_buttons = 0
        if self.BROWSE_STATUS != "f":
            QMessageBox.warning(self, "ATTENZIONE", "If you want find new record push 'new search' ",  QMessageBox.Ok)
        else:
            if self.lineEdit_id_media.text() != "":
                id_media = int(self.lineEdit_id_media.text())
            else:
                id_media = ""
            search_dict = {
            self.TABLE_FIELDS[0]  : id_media
            }

            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)

            if not bool(search_dict):
                QMessageBox.warning(self, "Warning", "Insert Value!!!",  QMessageBox.Ok)
            else:
                res = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS_thumb)
                if not bool(res):
                    QMessageBox.warning(self, "Warning", "No records have been found!",  QMessageBox.Ok)

                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR+1)
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]

                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])

                    
                    self.setComboBoxEnable(["self.lineEdit_id_media"],"False")
                    self.fill_fields(self.REC_CORR)#check_for_buttons = 1
                    
                else:
                    self.DATA_LIST = []

                    for i in res:
                        self.DATA_LIST.append(i)

                    self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                    self.fill_fields()
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR+1)
                    if self.REC_TOT == 1:
                        strings = ("Has been found", self.REC_TOT, "record")
                    else:
                        strings = ("Have been found", self.REC_TOT, "records")

                    self.setComboBoxEnable(["self.lineEdit_id_media"],"False")
                    #check_for_buttons = 1

                    QMessageBox.warning(self, "Messaggio", "%s %d %s" % strings, QMessageBox.Ok)
        self.NUM_DATA_BEGIN =  len(self.DATA_LIST)-25
        self.NUM_DATA_END = len(self.DATA_LIST)
        self.view_num_rec()
        self.open_images()  
        #if check_for_buttons == 1:
        self.enable_button_search(1)
        
        
        
        #visualizza le immagini nella gui
        item = QListWidgetItem(str(id_media))
                    
        data_for_thumb = self.db_search_check(self.MAPPER_TABLE_CLASS_thumb, 'id_media', id_media) # recupera i valori della thumb in base al valore id_media del file originale
                    
        thumb_path = data_for_thumb[0].filepath
        item.setData(Qt.UserRole,thumb_path)
        icon = QIcon(thumb_path) #os.path.join('%s/%s' % (directory.toUtf8(), image)))
        item.setIcon(icon)
        self.iconListWidget.addItem(item)
    def on_pushButton_delete_pressed(self):
        msg = QMessageBox.warning(self,"Attenzione!!!",u"Do you want delete? \n the action is irreversibile", QMessageBox.Ok | QMessageBox.Cancel)
        if msg == QMessageBox.Cancel:
            QMessageBox.warning(self,"Message!!!","Action delete!")
        else:
            try:
                id_to_delete = eval("self.DATA_LIST[self.REC_CORR]." + self.ID_TABLE_THUMB)
                self.DB_MANAGER.delete_one_record(self.TABLE_THUMB_NAME, self.ID_TABLE_THUMB,id_to_delete)
                self.charge_records() #charge records from DB
                QMessageBox.warning(self,"Message!!!","Record delete!")
            except Exception as  e:
                QMessageBox.warning(self,"Message!!!","Type of error: "+str(e))
            if bool(self.DATA_LIST) == False:
                QMessageBox.warning(self, "Warning", "The database is empty!",  QMessageBox.Ok)
                self.DATA_LIST = []
                self.DATA_LIST_REC_CORR = []
                self.DATA_LIST_REC_TEMP = []
                self.REC_CORR = 0
                self.REC_TOT = 0
                self.empty_fields()
                self.set_rec_counter(0, 0)
            #check if DB is empty
            if bool(self.DATA_LIST) == True:
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]

                self.BROWSE_STATUS = "b"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR+1)
                #self.charge_list()
                self.fill_fields()
        self.SORT_STATUS = "n"
        self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
    
    
    
    def on_pushButton_save_pressed(self):
        #save record
        if self.BROWSE_STATUS == "b":
            #if self.data_error_check() == 0:
            if self.records_equal_check() == 1:
                self.update_if(QMessageBox.warning(self,'WARNING',"The record has been modify. Do you want save the modify?", QMessageBox.Cancel,1))
                self.SORT_STATUS = "n"
                self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
                self.enable_button(1)
                self.fill_fields(self.REC_CORR)
            else:
                QMessageBox.warning(self, "WARNING", "Has not to be done modify.",  QMessageBox.Ok)
        else:
            #if self.data_error_check() == 0:
                #test_insert = self.insert_new_rec()
            if test_insert == 1:
                self.empty_fields()
                self.SORT_STATUS = "n"
                self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
                self.charge_records()
                #self.charge_list()
                self.BROWSE_STATUS = "b"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), len(self.DATA_LIST)-1
                self.set_rec_counter(self.REC_TOT, self.REC_CORR+1)

                    

                self.fill_fields(self.REC_CORR)
                self.enable_button(1)
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
        except Exception as  e:
            QMessageBox.warning(self, "Message", "Encoding problem: accents or characters that are not accepted by the database have been inserted. If you close the window without correcting the errors the data will be lost. Create a copy of everything on a seperate word document. Error :" + str(e), QMessageBox.Ok)
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
        img_visualizzate_txt = ('%s %d to %d') % ("from",num_data_begin,num_data_end )
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
                id_list.append(eval("i."+ self.ID_TABLE_THUMB))#for i in self.DB_MANAGER.query(self.MAPPER_TABLE_CLASS_thumb):
                #self.DATA_LIST.append(i)
        else:
            
            for i in self.DB_MANAGER.query(self.MAPPER_TABLE_CLASS_thumb):
                id_list.append(eval("i."+ self.ID_TABLE_THUMB))

            temp_data_list = self.DB_MANAGER.query_sort(id_list, [self.ID_TABLE_THUMB], 'asc', self.MAPPER_TABLE_CLASS_thumb, self.ID_TABLE_THUMB)

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
        
        if self.lineEdit_id_media.text() == "":
            id_media = None
        else:
            id_media = self.lineEdit_id_media.text()
    def empty_fields(self):
        #tags = self.tableWidget_tags.rowCount()
        
        self.lineEdit_id_media.clear()      
    def fill_fields(self, n=0):
        self.rec_num = n
        QMessageBox.warning(self, "check fill fields", str(self.rec_num),  QMessageBox.Ok)
        try:
            
            
            if self.DATA_LIST[self.rec_num].id_media == None:                                                                   #8 - US
                self.lineEdit_id_media.setText("")
            else:
                self.lineEdit_id_media.setText(str(self.DATA_LIST[self.rec_num].id_media))
    
        except Exception as  e:
            QMessageBox.warning(self, "Error Fill Fields", str(e),  QMessageBox.Ok)
    
    def setComboBoxEnable(self, f, v):
        field_names = f
        value = v

        for fn in field_names:
            cmd = ('%s%s%s%s') % (fn, '.setEnabled(', v, ')')
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
            self.DATA_LIST_REC_CORR.append(eval("unicode(self.DATA_LIST[self.REC_CORR]." + i + ")"))

    def records_equal_check(self):
        self.set_LIST_REC_TEMP()
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = Main()
    ui.show()
    sys.exit(app.exec_())
