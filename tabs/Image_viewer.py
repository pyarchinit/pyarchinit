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
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QDialog, QMessageBox, QAbstractItemView, QListWidgetItem, QFileDialog, QTableWidgetItem
from qgis.PyQt.uic import loadUiType

from gui.imageViewer import ImageViewer
from ..modules.db.pyarchinit_conn_strings import Connection
from ..modules.db.pyarchinit_db_manager import Pyarchinit_db_management
from ..modules.db.pyarchinit_utility import Utility
from ..modules.utility.delegateComboBox import ComboBoxDelegate
from ..modules.utility.pyarchinit_media_utility import Media_utility

MAIN_DIALOG_CLASS, _ = loadUiType(
    os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'pyarchinit_image_viewer_dialog.ui'))


class Main(QDialog, MAIN_DIALOG_CLASS):
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

    UTILITY = Utility()

    DATA = ''
    NUM_DATA_BEGIN = 0
    NUM_DATA_END = 25

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
        self.tableWidgetTags_US.setColumnWidth(1, 50)
        self.tableWidgetTags_US.setColumnWidth(2, 50)

        self.tableWidget_tags.setColumnWidth(2, 300)

        valuesSites = self.charge_sito_list()
        self.delegateSites = ComboBoxDelegate()
        self.delegateSites.def_values(valuesSites)
        self.delegateSites.def_editable('False')

        self.tableWidgetTags_US.setItemDelegateForColumn(0, self.delegateSites)

        self.tableWidgetTags_MAT.setItemDelegateForColumn(0, self.delegateSites)

        self.charge_sito_list()

    def connection(self):
        QMessageBox.warning(self, "Alert", "Sistema solo per sperimentazioni per lo sviluppo", QMessageBox.Ok)

        conn = Connection()
        conn_str = conn.conn_str()
        try:
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
                                    QMessageBox.Ok)

    def getDirectory(self):
        directory = QFileDialog.getExistingDirectory(self, "Scegli una directory", "Seleziona una directory:",
                                                     QFileDialog.ShowDirsOnly)

        if not directory:
            return

        QMessageBox.warning(self, "Alert", str(dir(directory)), QMessageBox.Ok)
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
                    conn = Connection()
                    media_max_num_id = self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS,
                                                                  self.ID_TABLE)  # db recupera il valore più alto ovvero l'ultimo immesso per l'immagine originale

                    thumb_path = conn.thumb_path()
                    thumb_path_str = thumb_path['thumb_path']

                    media_thumb_suffix = '_pay.png'

                    filenameorig = filename
                    filename_thumb = str(media_max_num_id) + "_" + filename + media_thumb_suffix
                    filepath_thumb = thumb_path_str + filename_thumb
                    # crea la thumbnail
                    try:
                        MU.resample_images(media_max_num_id, filepath, filenameorig, thumb_path_str, media_thumb_suffix)
                    except Exception as e:
                        QMessageBox.warning(self, "Cucu", str(e), QMessageBox.Ok)

                        # inserisce i dati nel DB
                    self.insert_record_mediathumb(media_max_num_id, mediatype, filename, filename_thumb, filetype,
                                                  filepath_thumb)

                    # visualizza le immagini nella ui
                    item = QListWidgetItem(str(media_max_num_id))
                    item.setData(Qt.UserRole, str(media_max_num_id))
                    icon = QIcon(filepath_thumb)  # os.path.join('%s/%s' % (directory.toUtf8(), image)))
                    item.setIcon(icon)
                    self.iconListWidget.addItem(item)

                elif bool(idunique_image_check):

                    # recupero il valore id_media basato sul path dell'immagine

                    data = idunique_image_check
                    id_media = data[0].id_media

                    # visualizza le immagini nella ui
                    item = QListWidgetItem(str(id_media))

                    data_for_thumb = self.db_search_check(self.MAPPER_TABLE_CLASS_thumb, 'id_media',
                                                          id_media)  # recupera i valori della thumb in base al valore id_media del file originale

                    thumb_path = data_for_thumb[0].filepath
                    item.setData(Qt.UserRole, thumb_path)
                    icon = QIcon(thumb_path)  # os.path.join('%s/%s' % (directory.toUtf8(), image)))
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
                str('Inserisci una descrizione'),  # 5 - descrizione
                str("['immagine']"))  # 6 - tags
            try:
                self.DB_MANAGER.insert_data_session(data)
                return 1
            except Exception as e:
                e_str = str(e)
                if e_str.__contains__("Integrity"):
                    msg = self.filename + ": immagine gia' presente nel database"
                else:
                    msg = e
                QMessageBox.warning(self, "Errore", "Attenzione 1 ! \n" + str(msg), QMessageBox.Ok)
                return 0

        except Exception as e:
            QMessageBox.warning(self, "Errore", "Attenzione 2 ! \n" + str(e), QMessageBox.Ok)
            return 0

    def insert_record_mediathumb(self, media_max_num_id, mediatype, filename, filename_thumb, filetype, filepath_thumb):
        self.media_max_num_id = media_max_num_id
        self.mediatype = mediatype
        self.filename = filename
        self.filename_thumb = filename_thumb
        self.filetype = filetype
        self.filepath_thumb = filepath_thumb

        try:
            data = self.DB_MANAGER.insert_mediathumb_values(
                self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS_thumb, self.ID_TABLE_THUMB) + 1,
                str(self.media_max_num_id),  # 1 - media_max_num_id
                str(self.mediatype),  # 2 - mediatype
                str(self.filename),  # 3 - filename
                str(self.filename_thumb),  # 4 - filename_thumb
                str(self.filetype),  # 5 - filetype
                str(self.filepath_thumb))  # 6 - filepath_thumb

            try:
                self.DB_MANAGER.insert_data_session(data)
                return 1
            except Exception as e:
                e_str = str(e)
                if e_str.__contains__("Integrity"):
                    msg = self.filename + ": thumb gia' presente nel database"
                else:
                    msg = e
                QMessageBox.warning(self, "Errore", "Attenzione 1 ! \n" + str(msg), QMessageBox.Ok)
                return 0

        except Exception as e:
            QMessageBox.warning(self, "Errore", "Attenzione 2 ! \n" + str(e), QMessageBox.Ok)
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
            except Exception as e:
                e_str = str(e)
                if e_str.__contains__("Integrity"):
                    msg = self.ID_TABLE + " gia' presente nel database"
                else:
                    msg = e
                QMessageBox.warning(self, "Errore", "Attenzione 1 ! \n" + str(msg), QMessageBox.Ok)
                return 0
        except Exception as e:
            QMessageBox.warning(self, "Errore", "Attenzione 2 ! \n" + str(e), QMessageBox.Ok)
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
        for item in items:
            dlg = ImageViewer(self)
            id_orig_item = item.text()  # return the name of original file

            search_dict = {'id_media': "'" + str(id_orig_item) + "'"}

            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)

            try:
                res = self.DB_MANAGER.query_bool(search_dict, "MEDIA")
                file_path = str(res[0].filepath)
            except Exception as e:
                QMessageBox.warning(self, "Errore", "Attenzione 1 file: " + str(e), QMessageBox.Ok)

            dlg.show_image(str(file_path))  # item.data(QtCore.Qt.UserRole).toString()))
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

        if not record_us_list:
            QMessageBox.warning(self, "Errore", "Scheda US non presente.", QMessageBox.Ok)

        us_list = []
        for r in record_us_list:
            us_list.append([r[0].id_us, 'US', 'us_table'])
        return us_list

    def generate_Reperti(self):
        tags_list = self.table2dict('self.tableWidgetTags_MAT')
        record_rep_list = []
        for sing_tags in tags_list:
            search_dict = {'sito': "'" + str(sing_tags[0]) + "'",
                           'numero_inventario': "'" + str(sing_tags[1]) + "'"
                           }
            record_rep_list.append(self.DB_MANAGER.query_bool(search_dict, 'INVENTARIO_MATERIALI'))

        if not record_rep_list:
            QMessageBox.warning(self, "Errore", "Scheda Inventario materiali non presente", QMessageBox.Ok)

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
        self.clear_thumb_images()

        data_len = len(self.DATA)

        if self.NUM_DATA_BEGIN >= data_len:
            # Sono già state visualizzate tutte le immagini
            self.NUM_DATA_BEGIN = 0
            self.NUM_DATA_END = 25

        elif self.NUM_DATA_BEGIN <= data_len:
            # indica che non sono state visualizzate tutte le immagini

            data = self.DATA[self.NUM_DATA_BEGIN:self.NUM_DATA_END]
            for i in range(len(data)):
                item = QListWidgetItem(str(data[i].id_media))

                # data_for_thumb = self.db_search_check(self.MAPPER_TABLE_CLASS_thumb, 'id_media', id_media) # recupera i valori della thumb in base al valore id_media del file originale

                thumb_path = data[i].filepath
                # QMessageBox.warning(self, "Errore",str(thumb_path),  QMessageBox.Ok)
                item.setData(Qt.UserRole, str(data[i].media_filename))
                icon = QIcon(thumb_path)  # os.path.join('%s/%s' % (directory.toUtf8(), image)))
                item.setIcon(icon)
                self.iconListWidget.addItem(item)

                # Button utility

    def on_pushButton_chose_dir_pressed(self):

        self.getDirectory()

    def on_pushButton_addRow_US_pressed(self):
        self.insert_new_row('self.tableWidgetTags_US')

    def on_pushButton_removeRow_US_pressed(self):
        self.remove_row('self.tableWidgetTags_US')

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

        for item in items_selected:
            for us_data in us_list:
                id_orig_item = item.text()  # return the name of original file
                search_dict = {'id_media': "'" + str(id_orig_item) + "'"}
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

        for item in items_selected:
            for reperti_data in reperti_list:
                id_orig_item = item.text()  # return the name of original file
                search_dict = {'id_media': "'" + str(id_orig_item) + "'"}
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

    def view_num_rec(self):
        num_data_begin = self.NUM_DATA_BEGIN
        num_data_begin += 1

        num_data_end = self.NUM_DATA_END
        if self.NUM_DATA_END < len(self.DATA):
            pass
        else:
            num_data_end = len(self.DATA)

        self.label_num_tot_immagini.setText(str(len(self.DATA)))
        img_visualizzate_txt = ('%s %d - a %d') % ("Da", num_data_begin, num_data_end)
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
                search_dict = {'id_media': "'" + str(id_orig_item) + "'"}
                u = Utility()
                search_dict = u.remove_empty_items_fr_dict(search_dict)
                res_media = self.DB_MANAGER.query_bool(search_dict, "MEDIA")
                ##			if bool(items) == True:
                ##				res_media = []
                ##				for item in items:
                ##					res_media = []
                ##					id_orig_item = item.text() #return the name of original file
                ##					search_dict = {'id_media' : "'"+str(id_orig_item)+"'"}
                ##					u = Utility()
                ##					search_dict = u.remove_empty_items_fr_dict(search_dict)
                ##					res_media = self.DB_MANAGER.query_bool(search_dict, "MEDIA")
                if bool(res_media):

                    for sing_media in res_media:
                        search_dict = {'id_media': "'" + str(id_orig_item) + "'"}
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
                                ##				#else
                                mediaToEntity_list.append(
                                    [str(sing_res_media.id_entity), sing_res_media.entity_type, US_string])
                            elif sing_res_media.entity_type == 'REPERTO':
                                search_dict = {'id_invmat': "'" + str(sing_res_media.id_entity) + "'"}
                                u = Utility()
                                search_dict = u.remove_empty_items_fr_dict(search_dict)
                                rep_data = self.DB_MANAGER.query_bool(search_dict, "INVENTARIO_MATERIALI")

                                Rep_string = ('Sito: %s - N. Inv.: %d') % (
                                    rep_data[0].sito, rep_data[0].numero_inventario)
                                ##				#else
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
