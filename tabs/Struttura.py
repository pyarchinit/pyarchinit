
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
from __future__ import absolute_import

import os
import subprocess
import time
from collections import OrderedDict
from datetime import date
import platform

import cv2
import numpy as np
import urllib.parse
import pyvista as pv
import vtk
from pyvistaqt import QtInteractor

from qgis.PyQt.QtGui import QIcon, QColor
from qgis.PyQt.QtCore import QVariant, QSize, QDateTime, Qt, QTimer
from qgis.PyQt.QtWidgets import QDialog, QListWidgetItem, QListWidget, QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QFrame, \
    QTextEdit, QMessageBox, QTableWidgetItem, QAbstractItemView, QFileDialog, QApplication
from qgis.PyQt.uic import loadUiType
from qgis.core import QgsSettings, Qgis

from ..gui.imageViewer import ImageViewer
from ..modules.utility.VideoPlayerStruttura import VideoPlayerWindow
from ..modules.utility.pyarchinit_media_utility import Media_utility, Media_utility_resize, Video_utility, \
    Video_utility_resize
from ..modules.db.pyarchinit_conn_strings import Connection
from ..modules.db.concurrency_manager import ConcurrencyManager, RecordLockIndicator
from ..modules.db.pyarchinit_db_manager import get_db_manager
from ..modules.db.pyarchinit_utility import Utility
from ..modules.gis.pyarchinit_pyqgis import Pyarchinit_pyqgis
from ..modules.utility.delegateComboBox import ComboBoxDelegate
from ..modules.utility.pyarchinit_error_check import Error_check
from ..modules.utility.pyarchinit_exp_Strutturasheet_pdf import generate_struttura_pdf
from ..gui.sortpanelmain import SortPanelMain
from ..gui.pyarchinitConfigDialog import pyArchInitDialog_Config
from ..modules.utility.remote_image_loader import load_icon, get_image_path, initialize as init_remote_loader
MAIN_DIALOG_CLASS, _ = loadUiType(os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'Struttura.ui'))


class pyarchinit_Struttura(QDialog, MAIN_DIALOG_CLASS):
    L=QgsSettings().value("locale/userLocale", "it", type=str)[:2]
    if L=='it':
        MSG_BOX_TITLE = "PyArchInit - Scheda Struttura"
    elif L=='en':
        MSG_BOX_TITLE = "PyArchInit - Structure form"
    elif L=='de':
        MSG_BOX_TITLE = "PyArchInit - Struktur formular"
    DATA_LIST = []
    DATA_LIST_REC_CORR = []
    DATA_LIST_REC_TEMP = []
    REC_CORR = 0
    REC_TOT = 0
    SITO = pyArchInitDialog_Config
    if L=='it':
        STATUS_ITEMS = {"b": "Usa", "f": "Trova", "n": "Nuovo Record"}
    
    if L=='de':
        STATUS_ITEMS = {"b": "Aktuell ", "f": "Finden", "n": "Neuer Rekord"}
    
    else :
        STATUS_ITEMS = {"b": "Current", "f": "Find", "n": "New Record"}
    BROWSE_STATUS = "b"
    SORT_MODE = 'asc'
    if L=='it':
        SORTED_ITEMS = {"n": "Non ordinati", "o": "Ordinati"}
    if L=='de':
        SORTED_ITEMS = {"n": "Nicht sortiert", "o": "Sortiert"}
    else:
        SORTED_ITEMS = {"n": "Not sorted", "o": "Sorted"}
    SORT_STATUS = "n"
    UTILITY = Utility()
    DB_MANAGER = ""
    TABLE_NAME = 'struttura_table'
    MAPPER_TABLE_CLASS = 'STRUTTURA'
    NOME_SCHEDA = "Scheda Struttura"
    ID_TABLE = "id_struttura"
    if L=='it':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Sito": "sito",
            "Sigla struttura": "sigla_struttura",
            "Numero struttura": "numero_struttura",
            "Categoria struttura": "categoria_struttura",
            "Tipologia struttura": "tipologia_struttura",
            "Definizione struttura": "definizione_struttura",
            "Descrizione": "descrizione",
            "Interpretazione": "interpretazione",
            "Periodo iniziale": "periodo_iniziale",
            "Fase iniziale": "fase_iniziale",
            "Periodo finale": "periodo_finale",
            "Fase_finale": "fase_finale",
            "Datazione estesa": "datazione_estesa"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Sito",
            "Sigla struttura",
            "Numero struttura",
            "Categoria struttura",
            "Tipologia struttura",
            "Definizione struttura",
            "Descrizione",
            "Interpretazione",
            "Periodo iniziale",
            "Fase iniziale",
            "Periodo finale",
            "Fase_finale",
            "Datazione estesa"
        ]
    elif L=='de':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Ausgrabungsstätte": "sito",
            "Strukturcode": "sigla_struttura",
            "Nr. Struktur": "numero_struttura",
            "Kategorie Struktur": "categoria_struttura",
            "Typologie Struktur": "tipologia_struttura",
            "Definition": "definizione_struttura",
            "Beschreibung": "descrizione",
            "Deutung": "interpretazione",
            "Anfangszeitraum": "periodo_iniziale",
            "Anfangsphase": "fase_iniziale",
            "Letzte zeitraum": "periodo_finale",
            "Letzte phase": "fase_finale",
            "Erweiterte Datierung": "datazione_estesa"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Ausgrabungsstätte",
            "Strukturcode",
            "Nr. Struktur",
            "Kategorie Struktur",
            "Typologie Struktur",
            "Definition",
            "Beschreibung",
            "Deutung",
            "Anfangszeitraum",
            "Anfangsphase",
            "Letzte zeitraum",
            "Letzte phase",
            "Erweiterte Datierung"
        ]
    else:
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Site": "sito",
            "Structure code": "sigla_struttura",
            "Structure number": "numero_struttura",
            "Structure categories": "categoria_struttura",
            "Structure typology": "tipologia_struttura",
            "Definition": "definizione_struttura",
            "Description": "descrizione",
            "Interpretation": "interpretazione",
            "Starting period": "periodo_iniziale",
            "Starting phase": "fase_iniziale",
            "Final period": "periodo_finale",
            "Final phase": "fase_finale",
            "Letteral datetion": "datazione_estesa"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Site",
            "Structure code",
            "Structure number",
            "Structure categories",
            "Structure typology",
            "Definition",
            "Description",
            "Interpretation",
            "Starting period",
            "Starting phase",
            "Final period",
            "Final phase",
            "Letteral datetion"]
    TABLE_FIELDS = [
        "sito",
        "sigla_struttura",
        "numero_struttura",
        "categoria_struttura",
        "tipologia_struttura",
        "definizione_struttura",
        "descrizione",
        "interpretazione",
        "periodo_iniziale",
        "fase_iniziale",
        "periodo_finale",
        "fase_finale",
        "datazione_estesa",
        "materiali_impiegati",
        "elementi_strutturali",
        "rapporti_struttura",
        "misure_struttura"
    ]

    LANG = {
       "IT": ['it_IT', 'IT', 'it', 'IT_IT'],
        "EN_US": ['en_US','EN_US'],
        "DE": ['de_DE','de','DE', 'DE_DE'],
        "FR": ['fr_FR','fr','FR', 'FR_FR'],
        "ES": ['es_ES','es','ES', 'ES_ES'],
        "PT": ['pt_PT','pt','PT', 'PT_PT'],
        "SV": ['sv_SV','sv','SV', 'SV_SV'],
        "RU": ['ru_RU','ru','RU', 'RU_RU'],
        "RO": ['ro_RO','ro','RO', 'RO_RO'],
        "AR": ['ar_LB', 'ar', 'AR', 'AR_LB', 'ar_AR', 'AR_AR'],
        "CA": ['ca_ES', 'ca', 'CA', 'CA_ES'],
        "PT_BR": ['pt_BR','PT_BR'],
        "SL": ['sl_SL','sl','SL', 'SL_SL'],
    }

    DB_SERVER = "not defined"  ####nuovo sistema sort
    HOME = os.environ['PYARCHINIT_HOME']


    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.pyQGIS = Pyarchinit_pyqgis(iface)
        self.setupUi(self)
        self.currentLayerId = None
        self.mDockWidget_export.setHidden(True)
        self.mDockWidget_3.setHidden(True)
        self.video_player = None

        try:
            self.on_pushButton_connect_pressed()
        except Exception as e:
            QMessageBox.warning(self, "Connection system", str(e), QMessageBox.StandardButton.Ok)

            # SIGNALS & SLOTS Functions
        self.pyQGIS = Pyarchinit_pyqgis(iface)
        self.currentLayerId = None
        self.setAcceptDrops(True)
        self.iconListWidget.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        # Dizionario per memorizzare le immagini in cache
        self.image_cache = OrderedDict()

        # Numero massimo di elementi nella cache
        self.cache_limit = 100
        try:
            self.on_pushButton_connect_pressed()
        except Exception as e:
            QMessageBox.warning(self, "Connection system", str(e), QMessageBox.StandardButton.Ok)

        self.comboBox_sigla_struttura.editTextChanged.connect(self.add_value_to_categoria)
        if len(self.DATA_LIST)==0:
            self.comboBox_sito.setCurrentIndex(0)
        else:
            self.comboBox_sito.setCurrentIndex(1)

        self.comboBox_sito.currentIndexChanged.connect(self.charge_periodo_iniz_list)
        self.comboBox_sito.currentIndexChanged.connect(self.charge_periodo_fin_list)
        self.comboBox_per_iniz.currentIndexChanged.connect(self.charge_fase_iniz_list)
        self.comboBox_per_fin.currentIndexChanged.connect(self.charge_fase_fin_list)
        self.comboBox_per_iniz.currentIndexChanged.connect(self.charge_datazione_list)
        self.comboBox_fas_iniz.currentIndexChanged.connect(self.charge_datazione_list)
        self.toolButton_pdfpath.clicked.connect(self.setPathpdf)
        self.pbnOpenpdfDirectory.clicked.connect(self.openpdfDir)
        sito = self.comboBox_sito.currentText()
        self.comboBox_sito.setEditText(sito)
        self.customize_GUI()
        self.set_sito()
        self.msg_sito()
        init_remote_loader()

    def loadMediaPreview(self):
        self.iconListWidget.clear()
        conn = Connection()
        thumb_path = conn.thumb_path()
        thumb_path_str = thumb_path['thumb_path']
        # if mode == 0:
        # """ if has geometry column load to map canvas """
        rec_list = self.ID_TABLE + " = " + str(
            getattr(self.DATA_LIST[int(self.REC_CORR)], self.ID_TABLE))
        search_dict = {
            'id_entity': "'" + str(getattr(self.DATA_LIST[int(self.REC_CORR)], self.ID_TABLE)) + "'",
            'entity_type': "'STRUTTURA'"}
        record_us_list = self.DB_MANAGER.query_bool(search_dict, 'MEDIATOENTITY')
        for i in record_us_list:
            search_dict = {'id_media': "'" + str(i.id_media) + "'"}
            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)
            mediathumb_data = self.DB_MANAGER.query_bool(search_dict, "MEDIA_THUMB")
            thumb_path = str(mediathumb_data[0].filepath)
            item = QListWidgetItem(str(i.media_name))
            item.setData(Qt.ItemDataRole.UserRole, str(i.media_name))
            icon = load_icon(get_image_path(thumb_path_str, thumb_path))
            item.setIcon(icon)
            self.iconListWidget.addItem(item)

    def loadMapPreview(self, mode=0):
        if mode == 0:
            """ if has geometry column load to map canvas """
            gidstr = self.ID_TABLE + " = " + str(
                getattr(self.DATA_LIST[int(self.REC_CORR)], self.ID_TABLE))
            layerToSet = self.pyQGIS.loadMapPreview(gidstr)
            #QMessageBox.warning(self, "layer to set", '\n'.join([l.name() for l in layerToSet]), QMessageBox.Ok)
            self.mapPreview.setLayers(layerToSet)
            self.mapPreview.zoomToFullExtent()
        elif mode == 1:
            self.mapPreview.setLayers([])
            self.mapPreview.zoomToFullExtent()

    def dropEvent(self, event):
        mimeData = event.mimeData()
        accepted_formats = ["jpg", "jpeg", "png", "tiff", "tif", "bmp", "mp4", "avi", "mov", "mkv", "flv", "obj", "stl",
                            "ply", "fbx", "3ds"]

        if mimeData.hasUrls():
            for url in mimeData.urls():
                try:
                    path = url.toLocalFile()
                    if os.path.isfile(path):
                        filename = os.path.basename(path)
                        filetype = filename.split(".")[-1]
                        if filetype.lower() in accepted_formats:
                            self.load_and_process_image(path)
                        else:
                            QMessageBox.warning(self, "Error", f"Unsupported file type: {filetype}", QMessageBox.StandardButton.Ok)
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Failed to process the file: {str(e)}", QMessageBox.StandardButton.Ok)
        super().dropEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()
    def insert_record_media(self, mediatype, filename, filetype, filepath):
        self.mediatype = mediatype
        self.filename = filename
        self.filetype = filetype
        self.filepath = filepath
        try:
            data = self.DB_MANAGER.insert_media_values(
                self.DB_MANAGER.max_num_id('MEDIA', 'id_media') + 1,
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
            QMessageBox.warning(self, "Error", "Warning 2 ! \n"+str(e),  QMessageBox.StandardButton.Ok)
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
                self.DB_MANAGER.max_num_id('MEDIA_THUMB', 'id_media_thumb') + 1,
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
            QMessageBox.warning(self, "Error", "Warning 2 ! \n"+str(e),  QMessageBox.StandardButton.Ok)
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
                self.DB_MANAGER.max_num_id('MEDIATOENTITY', 'id_mediaToEntity') + 1,
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
                QMessageBox.warning(self, "Error", "Warning 1 ! \n"+ str(msg),  QMessageBox.StandardButton.Ok)
                return 0
        except Exception as  e:
            QMessageBox.warning(self, "Error", "Warning 2 ! \n"+str(e),  QMessageBox.StandardButton.Ok)
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
            self.DB_MANAGER.max_num_id('MEDIATOENTITY', 'id_mediaToEntity')+1,
            int(self.id_entity),                                                    #1 - id_entity
            str(self.entity_type),                                              #2 - entity_type
            str(self.table_name),                                               #3 - table_name
            int(self.id_media),                                                     #4 - us
            str(self.filepath),                                                     #5 - filepath
            str(self.media_name))
        except Exception as  e:
            QMessageBox.warning(self, "Error", "Warning 2 ! \n"+str(e),  QMessageBox.StandardButton.Ok)
            return 0

    def generate_US(self):

        record_us_list = []
        sito = self.comboBox_sito.currentText()
        sigla = self.comboBox_sigla_struttura.currentText()
        nv = self.numero_struttura.text()

        search_dict = {'sito': "'" + str(sito) + "'",
                       'sigla_struttura': "'" + str(sigla) + "'",
                       'numero_struttura': "'" + str(nv) + "'"

                       }
        j = self.DB_MANAGER.query_bool(search_dict, 'STRUTTURA')
        record_us_list.append(j)
        #QMessageBox.information(self, 'search db', str(record_us_list))
        us_list = []
        for r in record_us_list:
            us_list.append([r[0].id_struttura, 'STRUTTURA', 'struttura_table'])
        #QMessageBox.information(self, "Scheda US", str(us_list), QMessageBox.Ok)
        return us_list
    def assignTags_US(self, item):

        us_list = self.generate_US()

        if not us_list:
            return

        for us_data in us_list:
            id_orig_item = item.text()  # return the name of original file
            search_dict = {'filename': "'" + str(id_orig_item) + "'"}
            media_data = self.DB_MANAGER.query_bool(search_dict, 'MEDIA')
            self.insert_mediaToEntity_rec(us_data[0], us_data[1], us_data[2], media_data[0].id_media,
                                          media_data[0].filepath, media_data[0].filename)

    def load_and_process_image(self, filepath):
        media_resize_suffix = ''
        media_thumb_suffix = ''
        conn = Connection()
        thumb_path = conn.thumb_path()
        thumb_path_str = thumb_path['thumb_path']
        if thumb_path_str == '':
            if self.L == 'it':
                QMessageBox.information(self, "Info",
                                        "devi settare prima la path per salvare le thumbnail e i video. Vai in impostazioni di sistema/ path setting ")
            elif self.L == 'de':
                QMessageBox.information(self, "Info",
                                        "müssen Sie zuerst den Pfad zum Speichern der Miniaturansichten und Videos festlegen. Gehen Sie zu System-/Pfad-Einstellung")
            else:
                QMessageBox.information(self, "Message",
                                        "you must first set the path to save the thumbnails and videos. Go to system/path setting")
        else:
            filename = os.path.basename(filepath)
            filename, filetype = filename.split(".")[0], filename.split(".")[1]
            # Check the media type based on the file extension
            accepted_image_formats = ["jpg", "jpeg", "png", "tiff", "tif", "bmp"]
            accepted_video_formats = ["mp4", "avi", "mov", "mkv", "flv"]
            accepted_3d_formats = ["obj", "stl", "ply", "fbx", "3ds"]

            if filetype.lower() in accepted_image_formats:
                mediatype = 'image'
                media_thumb_suffix = '_thumb.png'
                media_resize_suffix = '.png'
            elif filetype.lower() in accepted_video_formats:
                mediatype = 'video'
                media_thumb_suffix = '_video.png'
                media_resize_suffix = '.' + filetype.lower()
            elif filetype.lower() in accepted_3d_formats:
                mediatype = '3d_model'
                media_thumb_suffix = '_3d_thumb.png'
                media_resize_suffix = '.' + filetype.lower()
            else:
                raise ValueError(f"Unrecognized media type for file {filename}.{filetype}")

            if mediatype == 'video':
                if filetype.lower() == 'mp4':
                    media_resize_suffix = '.mp4'
                elif filetype.lower() == 'avi':
                    media_resize_suffix = '.avi'
                elif filetype.lower() == 'mov':
                    media_resize_suffix = '.mov'
                elif filetype.lower() == 'mkv':
                    media_resize_suffix = '.mkv'
                elif filetype.lower() == 'flv':
                    media_resize_suffix = '.flv'

            elif mediatype == '3d_model':
                if filetype.lower() == 'obj':
                    media_resize_suffix = '.obj'
                elif filetype.lower() == 'ply':
                    media_resize_suffix = '.ply'
                elif filetype.lower() == 'fbx':
                    media_resize_suffix = '.fbx'
                elif filetype.lower() == '3ds':
                    media_resize_suffix = '.3ds'
                elif filetype.lower() == 'stl':
                    media_resize_suffix = '.stl'
            # Check and insert record in the database
            idunique_image_check = self.db_search_check('MEDIA', 'filepath', filepath)

            try:
                if bool(idunique_image_check):

                    return
                else:
                    MU = Media_utility()
                    MUR = Media_utility_resize()
                    MU_video = Video_utility()
                    MUR_video = Video_utility_resize()
                    thumb_path = conn.thumb_path()
                    thumb_path_str = thumb_path['thumb_path']
                    thumb_resize = conn.thumb_resize()
                    thumb_resize_str = thumb_resize['thumb_resize']

                    # Check if remote storage is configured (UNIBO or other)
                    is_remote_storage = thumb_resize_str.startswith(('unibo://', 'gdrive://', 'dropbox://', 's3://', 'webdav://'))

                    # Determine the filepath to store in database
                    if is_remote_storage:
                        try:
                            from ..modules.utility.pyarchinit_media_utility import get_storage_manager
                            storage = get_storage_manager()
                            if storage:
                                remote_original_path = f"{thumb_resize_str}{filename}.{filetype}"
                                backend = storage.get_backend(remote_original_path)
                                with open(filepath, 'rb') as f:
                                    file_data = f.read()
                                _, _, relative_path = storage.parse_path(remote_original_path)
                                upload_filename = relative_path if relative_path else f"{filename}.{filetype}"
                                if backend.write(upload_filename, file_data):
                                    filepath_for_db = remote_original_path
                                    print(f"Uploaded original file to: {remote_original_path}")
                                else:
                                    filepath_for_db = filepath
                            else:
                                filepath_for_db = filepath
                        except Exception as e:
                            print(f"Error uploading to remote storage: {e}")
                            filepath_for_db = filepath
                    else:
                        filepath_for_db = filepath

                    self.insert_record_media(mediatype, filename, filetype, filepath_for_db)
                    media_max_num_id = self.DB_MANAGER.max_num_id('MEDIA', 'id_media')
                    filenameorig = filename
                    filename_thumb = str(media_max_num_id) + "_" + filename + media_thumb_suffix
                    filename_resize = str(media_max_num_id) + "_" + filename + media_resize_suffix
                    filepath_thumb = filename_thumb
                    filepath_resize = filename_resize
                    self.SORT_ITEMS_CONVERTED = []

                    try:

                        if mediatype == '3d_model':
                            self.process_3d_model(media_max_num_id, filepath, filename, thumb_path_str,
                                                  thumb_resize_str,
                                                  media_thumb_suffix, media_resize_suffix)

                        elif mediatype == 'video':
                            vcap = cv2.VideoCapture(filepath)
                            res, im_ar = vcap.read()
                            while im_ar.mean() < 1 and res:
                                res, im_ar = vcap.read()
                            im_ar = cv2.resize(im_ar, (100, 100), 0, 0, cv2.INTER_LINEAR)
                            # to save we have two options
                            outputfile = '{}.png'.format(os.path.dirname(filepath) + '/' + filename)
                            cv2.imwrite(outputfile, im_ar)
                            MU_video.resample_images(media_max_num_id, outputfile, filenameorig, thumb_path_str,
                                                     media_thumb_suffix)
                            MUR_video.resample_images(media_max_num_id, filepath, filenameorig, thumb_resize_str,
                                                      media_resize_suffix)
                        else:
                            MU.resample_images(media_max_num_id, filepath, filenameorig, thumb_path_str,
                                               media_thumb_suffix)
                            MUR.resample_images(media_max_num_id, filepath, filenameorig, thumb_resize_str,
                                                media_resize_suffix)
                    except Exception as e:
                        QMessageBox.warning(self, "Cucu", str(e), QMessageBox.StandardButton.Ok)
                    self.insert_record_mediathumb(media_max_num_id, mediatype, filename, filename_thumb, filetype,
                                                  filepath_thumb, filepath_resize)

                    item = QListWidgetItem(str(filenameorig))
                    item.setData(Qt.ItemDataRole.UserRole, str(media_max_num_id))
                    icon = QIcon(str(thumb_path_str) + filepath_thumb)
                    item.setIcon(icon)
                    self.iconListWidget.addItem(item)

                self.assignTags_US(item)




            except AssertionError as e:

                if self.L == 'it':
                    QMessageBox.warning(self, "Warning", "controlla che il nome del file non abbia caratteri speciali",

                                        QMessageBox.StandardButton.Ok)

                if self.L == 'de':

                    QMessageBox.warning(self, "Warning", "prüfen, ob der Dateiname keine Sonderzeichen enthält",
                                        QMessageBox.StandardButton.Ok)

                else:

                    QMessageBox.warning(self, "Warning", str(e), QMessageBox.StandardButton.Ok)


    def db_search_check(self, table_class, field, value):
        self.table_class = table_class
        self.field = field
        self.value = value
        search_dict = {self.field: "'" + str(self.value) + "'"}
        u = Utility()
        search_dict = u.remove_empty_items_fr_dict(search_dict)
        res = self.DB_MANAGER.query_bool(search_dict, self.table_class)
        return res
    def on_pushButton_assigntags_pressed(self):

        # Check the locale and set the button text and message box content
        L = QgsSettings().value("locale/userLocale", "it", type=str)[:2]
        if L == 'it':
            done_button_text = "Fatto"
            warning_title = "Attenzione"
            warning_text = "Devi selezionare una o più US"
        elif L == 'de':
            done_button_text = "Fertig"
            warning_title = "Achtung"
            warning_text = "Sie müssen eine oder mehrere US auswählen"
        else:  # Default to English
            done_button_text = "Done"
            warning_title = "Attention"
            warning_text = "You must select one or more US"
        # Check if there are selected items in the iconListWidget
        if not self.iconListWidget.selectedItems():
            QMessageBox.warning(self, warning_title, warning_text)
            return  # Exit the function if there are no selected images

        # Query all US records from the database and sort them
        all_us = self.DB_MANAGER.query('STRUTTURA')
        sorted_us = sorted(all_us, key=lambda x: (x.sito, x.area, x.us))

        # Create a QListWidget and populate it with sorted US records
        self.us_listwidget = QListWidget()
        header_item = QListWidgetItem("Sito - Sigla - Struttura")
        header_item.setBackground(QColor('lightgrey'))
        header_item.setFlags(header_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
        self.us_listwidget.addItem(header_item)
        for us in sorted_us:
            item_string = f"{us.sito} - {us.sigla_struttura} - {us.numero_struttura}"
            self.us_listwidget.addItem(QListWidgetItem(item_string))

        # Set selection mode to allow multiple selections
        self.us_listwidget.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)

        # Create a "Done" button and connect it to the slot
        done_button = QPushButton(done_button_text)
        done_button.clicked.connect(self.on_done_selecting)

        # Create a layout and add the QListWidget and "Done" button
        layout = QVBoxLayout()
        layout.addWidget(self.us_listwidget)
        layout.addWidget(done_button)

        # Create a widget to contain the QListWidget and button, and set the layout
        self.widget = QWidget()
        self.widget.setLayout(layout)
        self.widget.show()

    def on_done_selecting(self):
        # Check the locale and set the button text and message box content
        L = QgsSettings().value("locale/userLocale", "it", type=str)[:2]
        if L == 'it':
            done_button_text = "Fatto"
            warning_title = "Attenzione"
            warning_text = "Devi selezionare una o più US"
        elif L == 'de':
            done_button_text = "Fertig"
            warning_title = "Achtung"
            warning_text = "Sie müssen eine oder mehrere US auswählen"
        else:  # Default to English
            done_button_text = "Done"
            warning_title = "Attention"
            warning_text = "You must select one or more US"

        # Handle the event when the "Done" button is clicked
        selected_items = self.us_listwidget.selectedItems()
        if not selected_items:
            # Show a warning message if no items are selected
            QMessageBox.warning(self, warning_title, warning_text)
        else:
            # Process the selected items
            pass  # Replace with the code to handle the selected US records

        def r_list():

            # Ottieni le US selezionate dall'utente
            selected_us = [item.text().split(' - ') for item in self.us_listwidget.selectedItems()]
            record_us_list=[]
            for sing_tags in selected_us:
                search_dict = {'sito': "'" + str(sing_tags[0]) + "'",
                               'sigla_struttura': "'" + str(sing_tags[1]) + "'",
                               'numero_struttura': "'" + str(sing_tags[2]) + "'"
                               }
                j = self.DB_MANAGER.query_bool(search_dict, 'STRUTTURA')
                record_us_list.append(j)
            us_list = []
            for r in record_us_list:
                us_list.append([r[0].id_struttura, 'STRUTTURA', 'struttura_table'])
            # QMessageBox.information(self, "Scheda US", str(us_list), QMessageBox.Ok)
            return us_list


        #QMessageBox.information(self, 'ok', str(r_list()))
        items_selected=self.iconListWidget.selectedItems()
        for item in items_selected:
            for us_data in r_list():



                id_orig_item = item.text()  # return the name of original file
                search_dict = {'filename': "'" + str(id_orig_item) + "'"}
                media_data = self.DB_MANAGER.query_bool(search_dict, 'MEDIA')
                self.insert_mediaToEntity_rec(us_data[0], us_data[1], us_data[2], media_data[0].id_media,
                                              media_data[0].filepath, media_data[0].filename)

        self.widget.close()  # Chiude il widget dopo che l'utente ha premuto "Fatto"

    def on_pushButton_search_images_pressed(self):
        """Open the Image Search dialog with pre-filled filters for current Struttura record."""
        from .Image_search import pyarchinit_Image_Search

        # Get current record context
        sito = self.comboBox_sito.currentText() if hasattr(self, 'comboBox_sito') else ''

        # Open Image Search dialog
        dialog = pyarchinit_Image_Search(self.iface, self)

        # Set pre-filled filters
        dialog.comboBox_entity_type.setCurrentText('Struttura')
        if sito:
            index = dialog.comboBox_sito.findText(sito)
            if index >= 0:
                dialog.comboBox_sito.setCurrentIndex(index)
            else:
                dialog.comboBox_sito.setCurrentText(sito)

        dialog.show()

    def on_pushButton_removetags_pressed(self):
        def r_id():
            record_us_list=[]
            sito = self.comboBox_sito.currentText()
            sigla = self.comboBox_sigla_struttura.currentText()
            nv = self.numero_struttura.text()

            search_dict = {'sito': "'" + str(sito) + "'",
                           'sigla_struttura': "'" + str(sigla) + "'",
                           'numero_struttura': "'" + str(nv) + "'"

                           }
            j = self.DB_MANAGER.query_bool(search_dict, 'STRUTTURA')
            record_us_list.append(j)
            # QMessageBox.information(self, 'search db', str(record_us_list))
            us_list = []
            for r in record_us_list:
                a=r[0].id_us
            #QMessageBox.information(self,'ok',str(a))# QMessageBox.information(self, "Scheda US", str(us_list), QMessageBox.Ok)
            return a
        items_selected=self.iconListWidget.selectedItems()
        if not bool(items_selected):
            if self.L == 'it':

                msg = QMessageBox.warning(self, "Attenzione!!!",
                                          "devi selezionare prima l'immagine",
                                          QMessageBox.StandardButton.Ok)

            elif self.L == 'de':

                msg = QMessageBox.warning(self, "Warnung",
                                          "moet je eerst de afbeelding selecteren",
                                          QMessageBox.StandardButton.Ok)
            else:

                msg = QMessageBox.warning(self, "Warning",
                                          "you must first select an image",
                                          QMessageBox.StandardButton.Ok)
        else:
            if self.L == 'it':
                msg = QMessageBox.warning(self, "Warning",
                                          "Vuoi veramente cancellare i tags dalle thumbnail selezionate? \n L'azione è irreversibile",
                                          QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
                if msg == QMessageBox.StandardButton.Cancel:
                    QMessageBox.warning(self, "Messaggio!!!", "Azione Annullata!")
                else:
                    #items_selected = self.iconListWidget.selectedItems()
                    for item in items_selected:
                        id_orig_item = item.text()  # return the name of original file

                        # s = self.iconListWidget.item(0, 0).text()
                        self.DB_MANAGER.remove_tags_from_db_sql_scheda(r_id(), id_orig_item)
                        row = self.iconListWidget.row(item)
                        self.iconListWidget.takeItem(row)
                    QMessageBox.warning(self, "Info", "Tags rimossi!")
            elif self.L == 'de':
                msg = QMessageBox.warning(self, "Warning",
                                          "Wollen Sie wirklich die Tags aus den ausgewählten Miniaturbildern löschen? \n Die Aktion ist unumkehrbar",
                                          QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
                if msg == QMessageBox.StandardButton.Cancel:
                    QMessageBox.warning(self, "Warnung", "Azione Annullata!")
                else:
                    #items_selected = self.iconListWidget.selectedItems()
                    for item in items_selected:
                        id_orig_item = item.text()  # return the name of original file

                        # s = self.iconListWidget.item(0, 0).text()
                        self.DB_MANAGER.remove_tags_from_db_sql_scheda(r_id(), id_orig_item)
                        row = self.iconListWidget.row(item)
                        self.iconListWidget.takeItem(row)
                    QMessageBox.warning(self, "Info", "Tags entfernt")

            else:
                msg = QMessageBox.warning(self, "Warning",
                                          "Do you really want to delete the tags from the selected thumbnails? \n The action is irreversible",
                                          QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
                if msg == QMessageBox.StandardButton.Cancel:
                    QMessageBox.warning(self, "Warning", "Action cancelled")
                else:
                    #items_selected = self.iconListWidget.selectedItems()
                    for item in items_selected:
                        id_orig_item = item.text()  # return the name of original file

                        #s = self.iconListWidget.item(0, 0).text()
                        self.DB_MANAGER.remove_tags_from_db_sql_scheda(r_id(),id_orig_item)
                        row = self.iconListWidget.row(item)
                        self.iconListWidget.takeItem(row)  # remove the item from the list

                    QMessageBox.warning(self, "Info", "Tags removed")


    def load_and_process_3d_model(self, filepath):
        filename = os.path.basename(filepath)
        filename, filetype = filename.split(".")[0], filename.split(".")[1]
        mediatype = '3d_model'

        # Inserisci il record nel database
        self.insert_record_media(mediatype, filename, filetype, filepath)

        # Genera una thumbnail del modello 3D
        thumbnail_path = self.generate_3d_thumbnail(filepath)

        # Inserisci il record della thumbnail
        media_max_num_id = self.DB_MANAGER.max_num_id('MEDIA', 'id_media')
        self.insert_record_mediathumb(media_max_num_id, mediatype, filename, f"{filename}_thumb.png", 'png',
                                      thumbnail_path, filepath)

        # Aggiungi l'item alla lista
        item = QListWidgetItem(str(filename))
        item.setData(Qt.ItemDataRole.UserRole, str(media_max_num_id))
        icon = QIcon(thumbnail_path)
        item.setIcon(icon)
        self.iconListWidget.addItem(item)

        self.assignTags_US(item)


    def show_3d_model(self, file_path):
        mesh = pv.read(file_path)
        points = []
        measuring = False
        measurement_objects = []


        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)

        frame = QFrame()
        layout = QVBoxLayout()

        plotter = QtInteractor(frame)

        debug_widget = QTextEdit()
        debug_widget.setReadOnly(True)

        def add_debug_message(message, important=False):
            timestamp = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
            formatted_message = f"[{timestamp}] {message}"
            if important:
                formatted_message = f"<b>{formatted_message}</b>"
            debug_widget.append(formatted_message)
            debug_widget.ensureCursorVisible()

            max_messages = 1000
            if debug_widget.document().blockCount() > max_messages:
                cursor = debug_widget.textCursor()
                cursor.movePosition(cursor.Start)
                cursor.select(cursor.LineUnderCursor)
                cursor.removeSelectedText()
                cursor.deletePreviousChar()
                cursor.movePosition(cursor.End)
                debug_widget.setTextCursor(cursor)

        def mouse_click_callback(obj, event):
            nonlocal measuring, points
            if event == "LeftButtonPressEvent" and measuring:
                x, y = plotter.interactor.GetEventPosition()
                add_debug_message(f"Evento di clic a posizione schermo: (x: {x}, y: {y})")

                picker = vtk.vtkCellPicker()
                picker.SetTolerance(10)  # Aumenta la tolleranza per migliorare il picking
                picker.Pick(x, y, 0, plotter.renderer)

                if picker.GetCellId() != -1:
                    point = np.array(picker.GetPickPosition())
                    add_debug_message(f"Punto selezionato nello spazio del modello: {point}")

                    closest_point_id = mesh.find_closest_point(point)
                    closest_point = mesh.points[closest_point_id]
                    add_debug_message(f"Punto più vicino sulla superficie della mesh: {closest_point}")

                    on_left_click(closest_point)
                else:
                    add_debug_message("Nessun punto sulla superficie trovato", important=True)

        plotter.interactor.AddObserver(vtk.vtkCommand.LeftButtonPressEvent, mouse_click_callback)

        layout.addWidget(plotter.interactor)
        plotter.clear()

        texture_file = os.path.splitext(file_path)[0] + '.jpg'
        if os.path.exists(texture_file):
            texture = pv.read_texture(texture_file)
            plotter.add_mesh(mesh, texture=texture, show_edges=False)
        else:
            plotter.add_mesh(mesh, show_edges=False)

        instructions_widget = QTextEdit()
        instructions_widget.setReadOnly(True)
        instructions_widget.hide()

        instructions = (
            "Trackball Controls:\n"
            "- Rotate: Left-click and drag\n"
            "- Pan: Right-click and drag\n"
            "- Zoom: Mouse wheel or middle-click and drag\n"
            "- Reset view: 'r'\n"
            "- Start/Stop measuring: 'o'\n"
            "- Show bounding box measures: 'm'\n"
            "- Export image: 'e'\n"
            "- Clear measurements: 'c'\n"
            "\nMain Views:\n"
            "- XY View (top): 'z'\n"
            "- YZ View (front): 'x'\n"
            "- XZ View (side): 'y'\n"
            "- ZY View (back): 'w'\n"
            "- ZX View (opposite side): 'v'\n"
            "- YX View (bottom): 'b'"
        )
        instructions_widget.setText(instructions)

        def toggle_instructions():
            if instructions_widget.isHidden():
                instructions_widget.show()
            else:
                instructions_widget.hide()

        instructions_button = QPushButton("Toggle Instructions")
        instructions_button.clicked.connect(toggle_instructions)
        layout.addWidget(instructions_button)

        frame.setLayout(layout)
        main_layout.addWidget(frame)
        main_layout.addWidget(instructions_widget)
        #main_layout.addWidget(debug_widget)

        def toggle_measure():
            nonlocal measuring, points
            measuring = not measuring
            points.clear()
            if measuring:
                add_debug_message("Misurazione iniziata", important=True)
            else:
                add_debug_message("Misurazione terminata", important=True)

        def on_left_click(picked_point):
            nonlocal points
            if not measuring:
                return

            add_debug_message(f"Punto selezionato: {picked_point}")

            if picked_point is not None:
                points.append(picked_point)
                sphere = pv.Sphere(radius=mesh.length * 0.005,
                                   center=picked_point)  # Aumenta leggermente il raggio della sfera per una miglior visibilità
                sphere_actor = plotter.add_mesh(sphere, color='red')
                measurement_objects.append(sphere_actor)

                add_debug_message(f"Punto aggiunto. Totale punti: {len(points)}")
                if len(points) == 2:
                    add_debug_message("Due punti raccolti. Misurazione in corso...", important=True)
                    measure_distance(points[0], points[1])
                    points.clear()
            else:
                add_debug_message("Nessun punto selezionato", important=True)

        def verify_coordinates(coord1, coord2):
            add_debug_message(f"Verifica delle coordinate:\nPunto1: {coord1}\nPunto2: {coord2}", important=True)

        def measure_distance(point1, point2):
            add_debug_message(f"Misurazione della distanza tra {point1} e {point2}")
            distance = np.linalg.norm(np.array(point1) - np.array(point2))

            line = pv.Line(point1, point2)
            line_actor = plotter.add_mesh(line, color='red', line_width=2)
            measurement_objects.append(line_actor)
            add_debug_message("Linea aggiunta")

            labels = plotter.add_point_labels([point1, point2], ["P1", "P2"], point_size=1, font_size=6)
            measurement_objects.append(labels)
            add_debug_message("Etichette dei punti aggiunte")

            mid_point = (np.array(point1) + np.array(point2)) / 2
            distance_label = plotter.add_point_labels([mid_point], [f"{distance:.2f} cm"], point_size=0, font_size=6)
            measurement_objects.append(distance_label)
            add_debug_message("Etichetta della distanza aggiunta")

            verify_coordinates(point1, mid_point)  # Verifica le coordinate durante la misura

            plotter.render()
            add_debug_message(f"Distanza misurata: {distance:.2f} cm", important=True)

        def clear_measurements():
            nonlocal measurement_objects, points
            for obj in measurement_objects:
                plotter.remove_actor(obj)
            measurement_objects.clear()
            points.clear()
            plotter.render()

        def export_image():
            try:
                options = QFileDialog.Options()
                file_path, _ = QFileDialog.getSaveFileName(self, "Save Image", "",
                                                           "PNG Files (*.png);;All Files (*)", options=options)
                if file_path:
                    camera = plotter.camera_position
                    width_cm, height_cm = 15, 10
                    width_inches, height_inches = width_cm / 2.54, height_cm / 2.54
                    dpi = 300
                    width_pixels, height_pixels = int(width_inches * dpi), int(height_inches * dpi)
                    plotter.screenshot(file_path, transparent_background=False,
                                       window_size=(width_pixels, height_pixels),
                                       return_img=False)
                    plotter.camera_position = camera
                    add_debug_message(f"Immagine salvata come {file_path}", important=True)
                    QMessageBox.information(self, "Success", f"Image saved {file_path} to 300 DPI (15x10 cm)")
            except Exception as e:
                add_debug_message(f'Error: {str(e)}', important=True)
                QMessageBox.warning(self, "Error", f"Error saving image: {str(e)}")



        def get_visible_faces(plotter, mesh):
            camera_position = np.array(plotter.camera_position[0])
            center = np.array(mesh.center)
            direction = camera_position - center
            normals = np.array([
                [1, 0, 0], [-1, 0, 0],
                [0, 1, 0], [0, -1, 0],
                [0, 0, 1], [0, 0, -1]
            ])
            return [i for i, normal in enumerate(normals) if np.dot(direction, normal) > 0]

        def edge_visibility(edge, visible_faces):
            edge_to_faces = {
                (0, 1): [0, 2, 4], (1, 2): [0, 1, 4], (2, 3): [0, 3, 4], (3, 0): [0, 2, 4],
                (4, 5): [1, 2, 5], (5, 6): [1, 3, 5], (6, 7): [1, 3, 5], (7, 4): [1, 2, 5],
                (0, 4): [2, 4, 5], (1, 5): [1, 4, 5], (2, 6): [1, 3, 5], (3, 7): [2, 3, 5]
            }
            return any(face in visible_faces for face in edge_to_faces[edge])

        def calculate_label_position(p1, p2, offset_factor=0.1):
            mid_point = (p1 + p2) / 2
            direction = p2 - p1
            length = np.linalg.norm(direction)
            normalized_direction = direction / length
            perpendicular = np.cross(normalized_direction, [0, 0, 1])
            if np.allclose(perpendicular, 0):
                perpendicular = np.cross(normalized_direction, [0, 1, 0])
            perpendicular = perpendicular / np.linalg.norm(perpendicular)
            return mid_point + perpendicular * (length * offset_factor)

        def create_oriented_label(plotter, position, text, direction, is_vertical=False):
            vtk_text = vtk.vtkBillboardTextActor3D()
            vtk_text.SetPosition(position)
            vtk_text.SetInput(text)
            vtk_text.GetTextProperty().SetFontSize(6)
            vtk_text.GetTextProperty().SetColor(0, 0, 0)  # Testo nero
            vtk_text.GetTextProperty().SetBackgroundColor(1, 1, 1)  # Sfondo bianco
            vtk_text.GetTextProperty().SetBackgroundOpacity(0.8)
            vtk_text.GetTextProperty().SetJustificationToCentered()
            vtk_text.GetTextProperty().SetVerticalJustificationToCentered()

            if is_vertical:
                angle = 90
            else:
                angle = np.degrees(np.arctan2(direction[1], direction[0]))
            vtk_text.SetOrientation(0, 0, angle)

            plotter.add_actor(vtk_text)
            return vtk_text

        self.last_update_time = 0
        self.update_interval = 0.5  # Secondi tra gli aggiornamenti
        bounding_box_visible = False

        def show_measures():
            nonlocal bounding_box_visible, measurement_objects
            if not bounding_box_visible:
                return

            current_time = time.time()
            if current_time - self.last_update_time < self.update_interval:
                return
            self.last_update_time = current_time

            # Rimuovi le misure esistenti
            for obj in measurement_objects:
                plotter.remove_actor(obj)
            measurement_objects = []

            bounds = mesh.bounds
            x_min, x_max, y_min, y_max, z_min, z_max = bounds
            point = np.array([
                [x_min, y_min, z_min], [x_max, y_min, z_min], [x_max, y_max, z_min], [x_min, y_max, z_min],
                [x_min, y_min, z_max], [x_max, y_min, z_max], [x_max, y_max, z_max], [x_min, y_max, z_max]
            ])

            edges = [
                (0, 1),  # Larghezza (X)
                (0, 3),  # Profondità (Y)
                (0, 4)  # Altezza (Z)
            ]

            get_visible_faces(plotter, mesh)

            for i, edge in enumerate(edges):
                #if edge_visibility(edge):
                p1, p2 = point[edge[0]], point[edge[1]]
                distance = np.linalg.norm(p2 - p1) * 100

                label_position = calculate_label_position(p1, p2)

                line = pv.Line(p1, p2)
                line_actor = plotter.add_mesh(line, color='black', line_width=0.8)
                measurement_objects.append(line_actor)

                label = f"{distance:.2f} cm"
                is_vertical = (i == 2)  # L'etichetta verticale è per l'altezza (Z)
                label_actor = create_oriented_label(plotter, label_position, label, p2 - p1, is_vertical)
                measurement_objects.append(label_actor)

            plotter.render()

        def toggle_bounding_box_measures():
            nonlocal bounding_box_visible
            bounding_box_visible = not bounding_box_visible
            if bounding_box_visible:
                show_measures()
                add_debug_message("Misure del bounding box attivate", important=True)
            else:
                for obj in measurement_objects:
                    plotter.remove_actor(obj)
                measurement_objects.clear()
                plotter.render()
                add_debug_message("Misure del bounding box disattivate", important=True)

        def camera_changed(obj, event):
            if bounding_box_visible:
                show_measures()

        plotter.iren.add_observer('InteractionEvent', camera_changed)

        def reset_view():
            plotter.reset_camera()

        def change_view(direction):
            getattr(plotter, f'view_{direction}')()

        plotter.add_key_event("o", toggle_measure)
        plotter.add_key_event("c", clear_measurements)
        plotter.add_key_event('e', export_image)
        plotter.add_key_event('m', toggle_bounding_box_measures)
        plotter.add_key_event('r', reset_view)
        plotter.add_key_event('x', lambda: change_view('yz'))
        plotter.add_key_event('y', lambda: change_view('xz'))
        plotter.add_key_event('z', lambda: change_view('xy'))
        plotter.add_key_event('w', lambda: change_view('zy'))
        plotter.add_key_event('v', lambda: change_view('zx'))
        plotter.add_key_event('b', lambda: change_view('yx'))

        plotter.add_orientation_widget(plotter.enable_trackball_style())
        plotter.enable_trackball_style()
        frame.show()
        return main_widget

    def generate_3d_thumbnail(self, filepath):

        mesh = pv.read(filepath)
        plotter = pv.Plotter(off_screen=True)
        plotter.add_mesh(mesh)
        plotter.camera_position = 'xy'

        # Genera un nome file unico per la thumbnail
        thumbnail_filename = f"{os.path.splitext(os.path.basename(filepath))[0]}_thumb.png"
        thumbnail_path = os.path.join(self.thumb_path, thumbnail_filename)

        plotter.screenshot(thumbnail_path)
        return thumbnail_path

    def process_3d_model(self, media_max_num_id, filepath, filename, thumb_path_str, thumb_resize_str,
                         media_thumb_suffix, media_resize_suffix):
        import pyvista as pv

        # Carica il modello 3D
        mesh = pv.read(filepath)

        # Genera una thumbnail
        plotter = pv.Plotter(off_screen=True)
        plotter.add_mesh(mesh)
        plotter.camera_position = 'xy'
        thumbnail_path = os.path.join(thumb_path_str, f"{media_max_num_id}_{filename}{media_thumb_suffix}")
        plotter.screenshot(thumbnail_path)

        # Copia il file originale nella cartella di resize (non possiamo ridimensionare un modello 3D come un'immagine)
        import shutil
        resize_path = os.path.join(thumb_resize_str, f"{media_max_num_id}_{filename}{media_resize_suffix}")
        shutil.copy(filepath, resize_path)
        # Controlla se esiste una texture JPG con lo stesso nome del modello
        texture_filename = os.path.splitext(filename)[0] + ".jpg"
        texture_filepath = os.path.join(os.path.dirname(filepath), texture_filename)

        if os.path.exists(texture_filepath):
            # Se la texture esiste, copiala nella cartella di resize
            texture_resize_path = os.path.join(thumb_resize_str, f"{media_max_num_id}_{texture_filename}")
            shutil.copy(texture_filepath, texture_resize_path)

        return thumbnail_path, resize_path

    def openWide_image(self):
        items = self.iconListWidget.selectedItems()
        conn = Connection()

        thumb_resize = conn.thumb_resize()
        thumb_resize_str = thumb_resize['thumb_resize']

        def process_file_path(file_path):
            return urllib.parse.unquote(file_path)

        def show_image(file_path):
            dlg = ImageViewer(self)
            dlg.show_image(file_path)
            dlg.exec()

        def show_video(file_path):
            if self.video_player is None:
                self.video_player = VideoPlayerWindow(self, db_manager=self.DB_MANAGER,
                                                      icon_list_widget=self.iconListWidget,
                                                      main_class=self)
            self.video_player.set_video(file_path)
            self.video_player.show()

        def show_media(file_path, media_type):
            # Check if file_path is already a full path (starts with protocol)
            if file_path.startswith(('unibo://', 'http://', 'https://', 'cloudinary://', '/')):
                full_path = file_path
            elif thumb_resize_str and thumb_resize_str.startswith(('unibo://', 'http://', 'https://', 'cloudinary://')):
                full_path = thumb_resize_str.rstrip('/') + '/' + file_path.lstrip('/')
            else:
                full_path = os.path.join(thumb_resize_str, file_path)


            if media_type == 'video':
                show_video(full_path)
            elif media_type == 'image':
                show_image(full_path)
            elif media_type == '3d_model':
                self.show_3d_model(file_path)
            else:
                QMessageBox.warning(self, "Error", f"Unsupported media type: {media_type}", QMessageBox.StandardButton.Ok)

        def query_media(search_dict, table="MEDIA_THUMB"):
            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)
            try:
                return self.DB_MANAGER.query_bool(search_dict, table)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Database query failed: {str(e)}", QMessageBox.StandardButton.Ok)
                return None

        for item in items:
            id_orig_item = item.text()
            search_dict = {'media_filename': f"'{id_orig_item}'"}
            res = query_media(search_dict)

            if res:
                # Construct path properly for remote URLs
                path_resize = str(res[0].path_resize)
                # Check if path_resize is already a full path
                if path_resize.startswith(('unibo://', 'http://', 'https://', 'cloudinary://', '/')):
                    file_path = process_file_path(path_resize)
                elif thumb_resize_str and thumb_resize_str.startswith(('unibo://', 'http://', 'https://', 'cloudinary://')):
                    file_path = process_file_path(thumb_resize_str.rstrip('/') + '/' + path_resize.lstrip('/'))
                else:
                    file_path = process_file_path(os.path.join(thumb_resize_str, path_resize))

                media_type = res[0].mediatype

                if media_type == '3d_model':
                    widget_3d = self.show_3d_model(file_path)

                    # Crea un nuovo QDialog per contenere il widget 3D
                    dialog = QDialog(self)
                    dialog.setWindowTitle("3D Model Viewer")
                    dialog_layout = QVBoxLayout()
                    dialog_layout.addWidget(widget_3d)
                    dialog.setLayout(dialog_layout)

                    # Imposta le dimensioni del dialog
                    dialog.resize(800, 600)  # Puoi modificare queste dimensioni come preferisci

                    # Mostra il dialog
                    dialog.exec()
                else:
                    show_media(file_path, media_type)
            else:
                QMessageBox.warning(self, "Error", f"File not found: {id_orig_item}", QMessageBox.StandardButton.Ok)

    def on_pushButton_print_pressed(self):
        if self.L=='it':
            if self.checkBox_s_us.isChecked():
                Struttura_pdf_sheet = generate_struttura_pdf()
                data_list = self.generate_list_pdf()
                Struttura_pdf_sheet.build_Struttura_sheets(data_list)
                QMessageBox.warning(self, 'Ok',"Esportazione terminata Schede Struttura",QMessageBox.StandardButton.Ok)
            else:
                pass
            if self.checkBox_e_us.isChecked() :
                Struttura_index_pdf = generate_struttura_pdf()
                data_list = self.generate_list_pdf()
                try:
                    if bool(data_list):
                        Struttura_index_pdf.build_index_Struttura(data_list, data_list[0][0])
                        QMessageBox.warning(self, 'Ok',"Esportazione terminata Elenco Struttura",QMessageBox.StandardButton.Ok)
                    else:
                        QMessageBox.warning(self, 'ATTENZIONE',"L'elenco Struttura non può essere esportato devi riempire prima la scheda Struttura",QMessageBox.StandardButton.Ok)
                except Exception as e :
                    QMessageBox.warning(self, 'ATTENZIONE',str(e),QMessageBox.StandardButton.Ok)
            else:
                pass

        elif self.L=='de':
            if self.checkBox_s_us.isChecked():
                Struttura_pdf_sheet = generate_struttura_pdf()
                data_list = self.generate_list_pdf()
                Struttura_pdf_sheet.build_Struttura_sheets_de(data_list)
                QMessageBox.warning(self, 'Ok', "Export beendet Struktur-Formular", QMessageBox.StandardButton.Ok)
            else:
                pass

        elif self.L=='fr':
            if self.checkBox_s_us.isChecked():
                Struttura_pdf_sheet = generate_struttura_pdf()
                data_list = self.generate_list_pdf()
                Struttura_pdf_sheet.build_Struttura_sheets_fr(data_list)
                QMessageBox.warning(self, 'Ok', "Exportation terminée Fiche Structure", QMessageBox.StandardButton.Ok)
            else:
                pass

        elif self.L=='es':
            if self.checkBox_s_us.isChecked():
                Struttura_pdf_sheet = generate_struttura_pdf()
                data_list = self.generate_list_pdf()
                Struttura_pdf_sheet.build_Struttura_sheets_es(data_list)
                QMessageBox.warning(self, 'Ok', "Exportación completada Ficha Estructura", QMessageBox.StandardButton.Ok)
            else:
                pass

        elif self.L=='ar':
            if self.checkBox_s_us.isChecked():
                Struttura_pdf_sheet = generate_struttura_pdf()
                data_list = self.generate_list_pdf()
                Struttura_pdf_sheet.build_Struttura_sheets_ar(data_list)
                QMessageBox.warning(self, 'Ok', "اكتمل تصدير بطاقة البنية", QMessageBox.StandardButton.Ok)
            else:
                pass

        elif self.L=='ca':
            if self.checkBox_s_us.isChecked():
                Struttura_pdf_sheet = generate_struttura_pdf()
                data_list = self.generate_list_pdf()
                Struttura_pdf_sheet.build_Struttura_sheets_ca(data_list)
                QMessageBox.warning(self, 'Ok', "Exportació completada Fitxa Estructura", QMessageBox.StandardButton.Ok)
            else:
                pass

        else:  # English and other languages
            if self.checkBox_s_us.isChecked():
                Struttura_pdf_sheet = generate_struttura_pdf()
                data_list = self.generate_list_pdf()
                Struttura_pdf_sheet.build_Struttura_sheets_en(data_list)
                QMessageBox.warning(self, 'Ok', "Export finished Structure Form", QMessageBox.StandardButton.Ok)
            else:
                pass
            if self.checkBox_e_us.isChecked() :
                Struttura_index_pdf = generate_struttura_pdf()
                data_list = self.generate_list_pdf()
                try:
                    if bool(data_list):
                        Struttura_index_pdf.build_index_Struttura_en(data_list, data_list[0][0])
                        QMessageBox.warning(self, 'Ok',"Export finished Structure List",QMessageBox.StandardButton.Ok)
                    else:
                        QMessageBox.warning(self, 'Warning',"The Structure list cannot be exported you have to fill in the Structure tabs before",QMessageBox.StandardButton.Ok)
                except Exception as e :
                    QMessageBox.warning(self, 'Warning',str(e),QMessageBox.StandardButton.Ok)
            else:
                pass
            # if self.checkBox_e_foto_t.isChecked():
                # US_index_pdf = generate_US_pdf()
                # data_list_foto = self.generate_list_foto()
                # try:
                        # if bool(data_list_foto):
                            # US_index_pdf.build_index_Foto(data_list_foto, data_list_foto[0][0])
                            # QMessageBox.warning(self, 'Ok',"Esportazione terminata Elenco Foto",QMessageBox.Ok)
                        # else:
                            # QMessageBox.warning(self, 'ATTENZIONE',"L'elenco foto non può essere esportato perchè non hai immagini taggate.",QMessageBox.Ok)
                # except Exception as e :
                    # QMessageBox.warning(self, 'ATTENZIONE',str(e),QMessageBox.Ok)
            # if self.checkBox_e_foto.isChecked():
                # US_index_pdf = generate_US_pdf()
                # data_list_foto = self.generate_list_foto()
                # try:
                        # if bool(data_list_foto):
                            # US_index_pdf.build_index_Foto_2(data_list_foto, data_list_foto[0][0])
                            # QMessageBox.warning(self, 'Ok',"Esportazione terminata Elenco Foto senza thumbanil",QMessageBox.Ok)
                        # else:
                            # QMessageBox.warning(self, 'ATTENZIONE',"L'elenco foto non può essere esportato perchè non hai immagini taggate.",QMessageBox.Ok)
                # except Exception as e :
                    # QMessageBox.warning(self, 'ATTENZIONE',str(e),QMessageBox.Ok)
        # elif self.L=='en':  
            # if self.checkBox_s_us.isChecked():
                # US_pdf_sheet = generate_US_pdf()
                # data_list = self.generate_list_pdf()
                # US_pdf_sheet.build_US_sheets_en(data_list)
                # QMessageBox.warning(self, 'Ok',"Export finished Forms",QMessageBox.Ok)
            # else:   
                # pass
            # if self.checkBox_e_us.isChecked() :
                # US_index_pdf = generate_US_pdf()
                # data_list = self.generate_list_pdf()
                # try:               
                    # if bool(data_list):
                        # US_index_pdf.build_index_US_en(data_list, data_list[0][0])
                        # QMessageBox.warning(self, 'Ok',"Export finished Grave List",QMessageBox.Ok)
                    # else:
                        # QMessageBox.warning(self, 'WARNING',"The Grave list cannot be exported you have to fill in the Grave tabs first",QMessageBox.Ok)
                # except Exception as e :
                    # QMessageBox.warning(self, 'WARNING',str(e),QMessageBox.Ok)
            # else:
                # pass
            # if self.checkBox_e_foto_t.isChecked():
                # US_index_pdf = generate_US_pdf()
                # data_list_foto = self.generate_list_foto()
                # try:
                        # if bool(data_list_foto):
                            # US_index_pdf.build_index_Foto_en(data_list_foto, data_list_foto[0][0])
                            # QMessageBox.warning(self, 'Ok',"Export finished Grave List",QMessageBox.Ok)
                        # else:
                            # QMessageBox.warning(self, 'WARNING', 'The photo list cannot be exported because you do not have tagged images.',QMessageBox.Ok)
                # except Exception as e :
                    # QMessageBox.warning(self, 'WARNING',str(e),QMessageBox.Ok)
            # if self.checkBox_e_foto.isChecked():
                # US_index_pdf = generate_US_pdf()
                # data_list_foto = self.generate_list_foto()
                # try:
                        # if bool(data_list_foto):
                            # US_index_pdf.build_index_Foto_2_en(data_list_foto, data_list_foto[0][0])
                            # QMessageBox.warning(self, 'Ok', "Export finished Photo List without thumbanil",QMessageBox.Ok)
                        # else:
                            # QMessageBox.warning(self, 'WARNING', "The photo list cannot be exported because you do not have tagged images.",QMessageBox.Ok)
                # except Exception as e :
                    # QMessageBox.warning(self, 'WARNING',str(e),QMessageBox.Ok)
        # elif self.L=='de':
            # if self.checkBox_s_us.isChecked():
                # US_pdf_sheet = generate_US_pdf()
                # data_list = self.generate_list_pdf()
                # US_pdf_sheet.build_US_sheets_de(data_list)
                # QMessageBox.warning(self, 'Ok',"Esportazione terminata Schede US",QMessageBox.Ok)
            # else:   
                # pass
            # if self.checkBox_e_us.isChecked() :
                # US_index_pdf = generate_US_pdf()
                # data_list = self.generate_list_pdf()
                # try:               
                    # if bool(data_list):
                        # US_index_pdf.build_index_US_de(data_list, data_list[0][0])
                        # QMessageBox.warning(self, "Okay", "Export beendet",QMessageBox.Ok)
                    # else:
                        # QMessageBox.warning(self, 'WARNUNG', 'Die Liste kann nicht exportiert werden, Sie müssen zuerst die Formulare ausfüllen',QMessageBox.Ok)
                # except Exception as e :
                    # QMessageBox.warning(self, 'WARNUNG',str(e),QMessageBox.Ok)
            # else:
                # pass
            # if self.checkBox_e_foto_t.isChecked():
                # US_index_pdf = generate_US_pdf()
                # data_list_foto = self.generate_list_foto()
                # try:
                        # if bool(data_list_foto):
                            # US_index_pdf.build_index_Foto_de(data_list_foto, data_list_foto[0][0])
                            # QMessageBox.warning(self, "Okay", "Fertige Fotoliste exportieren",QMessageBox.Ok)
                        # else:
                            # QMessageBox.warning(self, 'WARNUNG', 'Die Fotoliste kann nicht exportiert werden, da Sie keine markierten Bilder haben.',QMessageBox.Ok)
                # except Exception as e :
                    # QMessageBox.warning(self, 'WARNUNG',str(e),QMessageBox.Ok)
            # if self.checkBox_e_foto.isChecked():
                # US_index_pdf = generate_US_pdf()
                # data_list_foto = self.generate_list_foto()
                # try:
                        # if bool(data_list_foto):
                            # US_index_pdf.build_index_Foto_2_de(data_list_foto, data_list_foto[0][0])
                            # QMessageBox.warning(self, 'Ok', 'Fertige Fotoliste ohne Daumenballen exportieren',QMessageBox.Ok)
                        # else:
                            # QMessageBox.warning(self, 'WARNUNG', 'Die Fotoliste kann nicht exportiert werden, da Sie keine markierten Bilder haben.',QMessageBox.Ok)
                # except Exception as e :
                    # QMessageBox.warning(self, 'WARNUNG',str(e),QMessageBox.Ok)
    # def on_pushButton_convert_pressed(self):
    #     # if not bool(self.setPathpdf()):
    #         # QMessageBox.warning(self, "INFO", "devi scegliere un file pdf",
    #                             # QMessageBox.Ok)
    #     try:
    #         pdf_file = self.lineEdit_pdf_path.text()
    #         filename=pdf_file.split("/")[-1]
    #         docx_file = self.PDFFOLDER+'/'+filename+'.docx'
    #         # convert pdf to docx
    #         parse(pdf_file, docx_file, start=self.lineEdit_pag1.text(), end=self.lineEdit_pag2.text())
    #         QMessageBox.information(self, "INFO", "Conversion completed",
    #                             QMessageBox.Ok)
    #     except Exception as e:
    #         QMessageBox.warning(self, "Error", str(e),
    #                             QMessageBox.Ok)
    
    def openpdfDir(self):
        HOME = os.environ['PYARCHINIT_HOME']
        path = '{}{}{}'.format(HOME, os.sep, "pyarchinit_PDF_folder")
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
    
    def on_pushButton_open_dir_pressed(self):
        HOME = os.environ['PYARCHINIT_HOME']
        path = '{}{}{}'.format(HOME, os.sep, "pyarchinit_PDF_folder")
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

    
    def setPathpdf(self):
        s = QgsSettings()
        dbpath = QFileDialog.getOpenFileName(
            self,
            "Set file name",
            self.PDFFOLDER,
            " PDF (*.pdf)"
        )[0]
        #filename=dbpath.split("/")[-1]
        if dbpath:
            self.lineEdit_pdf_path.setText(dbpath)
            s.setValue('',dbpath)
    
    def enable_button(self, n):
        self.pushButton_connect.setEnabled(n)

        self.pushButton_new_rec.setEnabled(n)

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
        self.pushButton_connect.setEnabled(n)

        self.pushButton_new_rec.setEnabled(n)

        self.pushButton_view_all.setEnabled(n)

        self.pushButton_first_rec.setEnabled(n)

        self.pushButton_last_rec.setEnabled(n)

        self.pushButton_prev_rec.setEnabled(n)

        self.pushButton_next_rec.setEnabled(n)

        self.pushButton_delete.setEnabled(n)

        self.pushButton_save.setEnabled(n)

        self.pushButton_sort.setEnabled(n)

    def on_pushButton_connect_pressed(self):
        conn = Connection()
        conn_str = conn.conn_str()
        test_conn = conn_str.find('sqlite')

        if test_conn == 0:
            self.DB_SERVER = "sqlite"

        try:
            self.DB_MANAGER = get_db_manager(conn_str, use_singleton=True)

            # Get database username and set it in the concurrency manager
            user_info = conn.datauser()
            db_username = user_info.get('user', 'unknown')
            if hasattr(self, 'concurrency_manager'):
                self.concurrency_manager.set_username(db_username)

            self.charge_records()  # charge records from DB
            # check if DB is empty
            if bool(self.DATA_LIST):
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                self.BROWSE_STATUS = "b"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.label_sort.setText(self.SORTED_ITEMS["n"])
                self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                self.charge_list()
                self.fill_fields()
            else:
                if self.L=='it':
                    QMessageBox.warning(self,"BENVENUTO", "Benvenuto in pyArchInit " + self.NOME_SCHEDA + ". Il database e' vuoto. Premi 'Ok' e buon lavoro!",
                                        QMessageBox.StandardButton.Ok)
                
                elif self.L=='de':
                    
                    QMessageBox.warning(self,"WILLKOMMEN","WILLKOMMEN in pyArchInit" + "Munsterformular"+ ". Die Datenbank ist leer. Tippe 'Ok' und aufgehts!",
                                        QMessageBox.StandardButton.Ok) 
                else:
                    QMessageBox.warning(self,"WELCOME", "Welcome in pyArchInit" + "Samples form" + ". The DB is empty. Push 'Ok' and Good Work!",
                                        QMessageBox.StandardButton.Ok)
                self.charge_list()
                self.BROWSE_STATUS = 'x'
                self.on_pushButton_new_rec_pressed()
        except Exception as e:
            e = str(e)
            if e.find("no such table"):
                if self.L=='it':
                    msg = "La connessione e' fallita {}. " \
                          "E' NECESSARIO RIAVVIARE QGIS oppure rilevato bug! Segnalarlo allo sviluppatore".format(str(e))
                    self.iface.messageBar().pushMessage(self.tr(msg), Qgis.Warning, 0)
                
                    self.iface.messageBar().pushMessage(self.tr(msg), Qgis.Warning, 0)
                elif self.L=='de':
                    msg = "Verbindungsfehler {}. " \
                          " QGIS neustarten oder es wurde ein bug gefunden! Fehler einsenden".format(str(e))
                    self.iface.messageBar().pushMessage(self.tr(msg), Qgis.Warning, 0)
                else:
                    msg = "The connection failed {}. " \
                          "You MUST RESTART QGIS or bug detected! Report it to the developer".format(str(e))        
            else:
                if self.L=='it':
                    msg = "Attenzione rilevato bug! Segnalarlo allo sviluppatore. Errore: ".format(str(e))
                    self.iface.messageBar().pushMessage(self.tr(msg), Qgis.Warning, 0)
                
                elif self.L=='de':
                    msg = "ACHTUNG. Es wurde ein bug gefunden! Fehler einsenden: ".format(str(e))
                    self.iface.messageBar().pushMessage(self.tr(msg), Qgis.Warning, 0)  
                else:
                    msg = "Warning bug detected! Report it to the developer. Error: ".format(str(e))
                    self.iface.messageBar().pushMessage(self.tr(msg), Qgis.Warning, 0)    

    def customize_GUI(self):

        l = QgsSettings().value("locale/userLocale", QVariant)
        lang = ""
        for key, values in self.LANG.items():
            if values.__contains__(l):
                lang = str(key)
        lang = "'" + lang + "'"

        # media prevew system
        self.iconListWidget.setDragEnabled(True)
        self.iconListWidget.setAcceptDrops(True)
        self.iconListWidget.setDropIndicatorShown(True)

        self.iconListWidget.setLineWidth(2)
        self.iconListWidget.setMidLineWidth(2)
        # self.iconListWidget.setProperty("showDropIndicator", False)
        self.iconListWidget.setIconSize(QSize(430, 570))

        self.iconListWidget.setUniformItemSizes(True)
        self.iconListWidget.setObjectName("iconListWidget")
        #self.iconListWidget.SelectionMode()  # Removed for Qt6 compatibility
        self.iconListWidget.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.iconListWidget.itemDoubleClicked.connect(self.openWide_image)


        self.tableWidget_rapporti.setColumnWidth(0, 220)
        self.tableWidget_rapporti.setColumnWidth(1, 220)
        self.tableWidget_rapporti.setColumnWidth(2, 150)
        self.tableWidget_rapporti.setColumnWidth(3, 100)

        self.tableWidget_materiali_impiegati.setColumnWidth(0, 200)

        self.tableWidget_elementi_strutturali.setColumnWidth(0, 150)
        self.tableWidget_elementi_strutturali.setColumnWidth(1, 100)

        self.tableWidget_misurazioni.setColumnWidth(0, 280)
        self.tableWidget_misurazioni.setColumnWidth(1, 200)
        self.tableWidget_misurazioni.setColumnWidth(2, 130)

        self.setComboBoxEditable(["self.comboBox_per_iniz"], 1)
        self.setComboBoxEditable(["self.comboBox_fas_iniz"], 1)
        self.setComboBoxEditable(["self.comboBox_per_fin"], 1)
        self.setComboBoxEditable(["self.comboBox_fas_fin"], 1)

        if self.L=='it':
            valuesRapporti = ["Si appoggia a", "Gli si appoggia", "Connesso con", "Si sovrappone a", "Gli si sovrappone",
                              "Ampliato da", "Amplia", "Uguale a",""]
            self.delegateRapporti = ComboBoxDelegate()
            self.delegateRapporti.def_values(valuesRapporti)
            self.delegateRapporti.def_editable('True')
            self.tableWidget_rapporti.setItemDelegateForColumn(0, self.delegateRapporti)
        elif self.L=='de':
            valuesRapporti = ["Stützt sich auf", "Wird gestüzt von", "Bindet an", "Überschneidungen sich auf", "Wird Überschneidungen von",
                              "Erweitert um", "Erweitert", "Entspricht", ""]
            self.delegateRapporti = ComboBoxDelegate()
            self.delegateRapporti.def_values(valuesRapporti)
            self.delegateRapporti.def_editable('True')
            self.tableWidget_rapporti.setItemDelegateForColumn(0, self.delegateRapporti)
            
        else:
            valuesRapporti = ["Abuts", "Supports", "Connected to", "Overlaps", "Overlaid by",
                              "Extend by", "Extend", "Same as", ""]
            self.delegateRapporti = ComboBoxDelegate()
            self.delegateRapporti.def_values(valuesRapporti)
            self.delegateRapporti.def_editable('True')
            self.tableWidget_rapporti.setItemDelegateForColumn(0, self.delegateRapporti)    
        # lista materiali

        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'struttura_table' + "'",
            'tipologia_sigla': "'" + '6.5' + "'"
        }

        materiali = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        valuesMateriali = []

        for i in range(len(materiali)):
            valuesMateriali.append(materiali[i].sigla_estesa)

        valuesMateriali.sort()

        #valuesMateriali = ["Terra", "Pietre", "Laterizio", "Ciottoli", "Calcare", "Calce", "Legno", "Concotto",
        #                   "Ghiaia", "Sabbia", "Malta", "Metallo", "Gesso"]
        self.delegateMateriali = ComboBoxDelegate()
        self.delegateMateriali.def_values(valuesMateriali)
        self.delegateMateriali.def_editable('False')
        self.tableWidget_materiali_impiegati.setItemDelegateForColumn(0, self.delegateMateriali)

        # lista elementi strutturali - tipologia elemento

        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'struttura_table' + "'",
            'tipologia_sigla': "'" + '6.6' + "'"
        }

        tipEl = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        valuesTipEl = []

        for i in range(len(tipEl)):
            valuesTipEl.append(tipEl[i].sigla_estesa)

        valuesTipEl.sort()

        # valuesMateriali = ["Terra", "Pietre", "Laterizio", "Ciottoli", "Calcare", "Calce", "Legno", "Concotto",
        #                   "Ghiaia", "Sabbia", "Malta", "Metallo", "Gesso"]
        self.delegateTipEl = ComboBoxDelegate()
        self.delegateTipEl.def_values(valuesTipEl)
        self.delegateTipEl.def_editable('False')
        self.tableWidget_elementi_strutturali.setItemDelegateForColumn(0, self.delegateTipEl)

        # lista misurazione - tipo misura

        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'struttura_table' + "'",
            'tipologia_sigla': "'" + '6.7' + "'"
        }

        elTipoMis = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        valuesTipoMis = []

        for i in range(len(elTipoMis)):
            valuesTipoMis.append(elTipoMis[i].sigla_estesa)

        valuesTipoMis.sort()

        self.delegateTipoMis = ComboBoxDelegate()
        self.delegateTipoMis.def_values(valuesTipoMis)
        self.delegateTipoMis.def_editable('False')
        self.tableWidget_misurazioni.setItemDelegateForColumn(0, self.delegateTipoMis)

        # lista misurazione - unita' di misura

        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'struttura_table' + "'",
            'tipologia_sigla': "'" + '6.8' + "'"
        }

        elUnitaMis = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        valuesUnitaMis = []

        for i in range(len(elUnitaMis)):
            valuesUnitaMis.append(elUnitaMis[i].sigla_estesa)

        valuesUnitaMis.sort()

        self.delegateUnitaMis = ComboBoxDelegate()
        self.delegateUnitaMis.def_values(valuesUnitaMis)
        self.delegateUnitaMis.def_editable('False')
        self.tableWidget_misurazioni.setItemDelegateForColumn(1, self.delegateUnitaMis)

        # lista rapporti struttura - sigla

        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'struttura_table' + "'",
            'tipologia_sigla': "'" + '6.1' + "'"
        }

        elSig = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        valuesSig = []

        for i in range(len(elSig)):
            valuesSig.append(elSig[i].sigla_estesa)

        valuesSig.sort()

        self.delegateSig = ComboBoxDelegate()
        self.delegateSig.def_values(valuesSig)
        self.delegateSig.def_editable('False')
        self.tableWidget_rapporti.setItemDelegateForColumn(2, self.delegateSig)

    def charge_list(self):

        #lista sito

        sito_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('site_table', 'sito', 'SITE'))

        try:
            sito_vl.remove('')
        except:
            pass
        self.comboBox_sito.clear()
        sito_vl.sort()
        self.comboBox_sito.addItems(sito_vl)

        #lista rapporti struttura - sito

        self.delegateSito = ComboBoxDelegate()
        self.delegateSito.def_values(sito_vl)
        self.delegateSito.def_editable('False')
        self.tableWidget_rapporti.setItemDelegateForColumn(1, self.delegateSito)

        #lista sigla struttura

        l = QgsSettings().value("locale/userLocale", QVariant)
        lang = ""
        for key, values in self.LANG.items():
            if values.__contains__(l):
                lang = str(key)
        lang = "'" + lang + "'"

        self.comboBox_sigla_struttura.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'struttura_table' + "'",
            'tipologia_sigla': "'" + '6.1' + "'"
        }

        sigla_struttura = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        sigla_struttura_vl = []

        for i in range(len(sigla_struttura)):
            sigla_struttura_vl.append(sigla_struttura[i].sigla)

        sigla_struttura_vl.sort()
        self.comboBox_sigla_struttura.addItems(sigla_struttura_vl)

        # lista categoria struttura

        self.comboBox_categoria_struttura.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'struttura_table' + "'",
            'tipologia_sigla': "'" + '6.2' + "'"
        }

        categoria_struttura = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        categoria_struttura_vl = []

        for i in range(len(categoria_struttura)):
            categoria_struttura_vl.append(categoria_struttura[i].sigla_estesa)

        categoria_struttura_vl.sort()
        self.comboBox_categoria_struttura.addItems(categoria_struttura_vl)

        # lista tipologia struttura

        self.comboBox_tipologia_struttura.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'struttura_table' + "'",
            'tipologia_sigla': "'" + '6.3' + "'"
        }

        tipologia_struttura = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        tipologia_struttura_vl = []

        for i in range(len(tipologia_struttura)):
            tipologia_struttura_vl.append(tipologia_struttura[i].sigla_estesa)

        tipologia_struttura_vl.sort()
        self.comboBox_tipologia_struttura.addItems(tipologia_struttura_vl)

        # lista definizione struttura

        self.comboBox_definizione_struttura.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'struttura_table' + "'",
            'tipologia_sigla': "'" + '6.4' + "'"
        }

        definizione_struttura = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        definizione_struttura_vl = []

        for i in range(len(definizione_struttura)):
            definizione_struttura_vl.append(definizione_struttura[i].sigla_estesa)

        definizione_struttura_vl.sort()
        self.comboBox_definizione_struttura.addItems(definizione_struttura_vl)

    def msg_sito(self):
        #self.model_a.database().close()
        conn = Connection()
        sito_set= conn.sito_set()
        sito_set_str = sito_set['sito_set']
        if bool(self.comboBox_sito.currentText()) and self.comboBox_sito.currentText()==sito_set_str:
            
            if self.L=='it':
                QMessageBox.information(self, "OK" ,"Sei connesso al sito: %s" % str(sito_set_str),QMessageBox.StandardButton.Ok) 
        
            elif self.L=='de':
                QMessageBox.information(self, "OK", "Sie sind mit der archäologischen Stätte verbunden: %s" % str(sito_set_str),QMessageBox.StandardButton.Ok) 
                
            else:
                QMessageBox.information(self, "OK", "You are connected to the site: %s" % str(sito_set_str),QMessageBox.StandardButton.Ok)     
        
        elif sito_set_str=='':    
            if self.L=='it':
                msg = QMessageBox.information(self, "Attenzione" ,"Non hai settato alcun sito. Vuoi settarne uno? click Ok altrimenti Annulla per  vedere tutti i record",QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel) 
            elif self.L=='de':
                msg = QMessageBox.information(self, "Achtung", "Sie haben keine archäologischen Stätten eingerichtet. Klicken Sie auf OK oder Abbrechen, um alle Datensätze zu sehen",QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel) 
            else:
                msg = QMessageBox.information(self, "Warning" , "You have not set up any archaeological site. Do you want to set one? click Ok otherwise Cancel to see all records",QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel) 
            if msg == QMessageBox.StandardButton.Cancel:
                pass
            else: 
                dlg = pyArchInitDialog_Config(self)
                dlg.charge_list()
                dlg.exec()
    def set_sito(self):
        conn = Connection()
        sito_set = conn.sito_set()
        sito_set_str = sito_set['sito_set']
        try:
            if bool(sito_set_str):
                search_dict = {'sito': "'" + str(sito_set_str) + "'"}
                u = Utility()
                search_dict = u.remove_empty_items_fr_dict(search_dict)
                res = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
                self.DATA_LIST = []
                for i in res:
                    self.DATA_LIST.append(i)
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0

                # Check if we have results before accessing DATA_LIST[0]
                if len(self.DATA_LIST) == 0:
                    if self.L == 'it':
                        QMessageBox.information(self, "Attenzione", f"Il sito '{sito_set_str}' non ha record in questa scheda. Crea un nuovo record o disattiva la 'scelta sito' dalla configurazione.", QMessageBox.StandardButton.Ok)
                    elif self.L == 'de':
                        QMessageBox.information(self, "Warnung", f"Die Fundstelle '{sito_set_str}' hat keine Datensätze. Erstellen Sie einen neuen Datensatz oder deaktivieren Sie die 'Site-Wahl'.", QMessageBox.StandardButton.Ok)
                    else:
                        QMessageBox.information(self, "Warning", f"Site '{sito_set_str}' has no records in this tab. Create a new record or disable 'site choice' from configuration.", QMessageBox.StandardButton.Ok)
                    return

                self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                self.fill_fields()
                self.BROWSE_STATUS = "b"
                self.SORT_STATUS = "n"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                self.setComboBoxEnable(["self.comboBox_sito"], "False")
            else:
                pass
        except Exception as e:
            if self.L == 'it':
                QMessageBox.warning(self, "Errore", f"Errore nel caricamento del sito '{sito_set_str}':\n{str(e)}", QMessageBox.StandardButton.Ok)
            elif self.L == 'de':
                QMessageBox.warning(self, "Fehler", f"Fehler beim Laden der Fundstelle '{sito_set_str}':\n{str(e)}", QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.warning(self, "Error", f"Error loading site '{sito_set_str}':\n{str(e)}", QMessageBox.StandardButton.Ok)

    def setComboBoxEnable(self, f, v):
        """Set enabled state for widgets"""
        for fn in f:
            widget_name = fn.replace('self.', '') if fn.startswith('self.') else fn
            widget = getattr(self, widget_name, None)
            if widget is not None:
                # Handle both boolean and string values
                if isinstance(v, bool):
                    widget.setEnabled(v)
                else:
                    widget.setEnabled(v == "True")

    def tableInsertData(self, t, d):
        """Set the value into table widget"""
        self.table_name = t
        self.data_list = eval(d) if isinstance(d, str) else d
        if self.data_list:
            self.data_list.sort()

        # Get table widget
        table_widget = getattr(self, self.table_name.replace("self.", "") if self.table_name.startswith("self.") else self.table_name)
        table_col_count = table_widget.columnCount()

        # Clear table
        table_widget.clearContents()
        table_widget.setRowCount(0)

        if self.data_list:
            for row in range(len(self.data_list)):
                table_widget.insertRow(row)
                for col in range(len(self.data_list[row])):
                    item = QTableWidgetItem(str(self.data_list[row][col]))
                    table_widget.setItem(row, col, item)

    def table2dict(self, n):
        """Convert a QTableWidget to a list of lists"""
        self.tablename = n
        table = getattr(self, self.tablename.replace("self.", "") if self.tablename.startswith("self.") else self.tablename)
        row = table.rowCount()
        col = table.columnCount()
        lista = []
        for r in range(row):
            sub_list = []
            for c in range(col):
                value = table.item(r, c)
                if bool(value):
                    sub_list.append(str(value.text()))
            if sub_list:  # Only add non-empty rows
                lista.append(sub_list)
        return lista

    def empty_fields_nosite(self):
        """Clear all fields except sito"""
        self.comboBox_sigla_struttura.setEditText("")
        self.numero_struttura.clear()
        self.comboBox_categoria_struttura.setEditText("")
        self.comboBox_tipologia_struttura.setEditText("")
        self.comboBox_definizione_struttura.setEditText("")
        self.textEdit_descrizione_struttura.clear()
        self.textEdit_interpretazione_struttura.clear()
        self.comboBox_datazione_estesa.setEditText("")
        self.comboBox_per_iniz.setEditText("")
        self.comboBox_fas_iniz.setEditText("")
        self.comboBox_per_fin.setEditText("")
        self.comboBox_fas_fin.setEditText("")
        self.tableWidget_materiali_impiegati.setRowCount(0)
        self.tableWidget_elementi_strutturali.setRowCount(0)
        self.tableWidget_rapporti.setRowCount(0)
        self.tableWidget_misurazioni.setRowCount(0)

    def empty_fields(self):
        """Clear all fields including sito"""
        self.comboBox_sito.setEditText("")
        self.empty_fields_nosite()

    def fill_fields(self, n=0):
        self.rec_num = n
        try:
            self.comboBox_sito.setEditText(self.DATA_LIST[self.rec_num].sito)
            self.comboBox_sigla_struttura.setEditText(str(self.DATA_LIST[self.rec_num].sigla_struttura))
            self.numero_struttura.setText(str(self.DATA_LIST[self.rec_num].numero_struttura))
            self.comboBox_categoria_struttura.setEditText(str(self.DATA_LIST[self.rec_num].categoria_struttura))
            self.comboBox_tipologia_struttura.setEditText(str(self.DATA_LIST[self.rec_num].tipologia_struttura))
            self.comboBox_definizione_struttura.setEditText(str(self.DATA_LIST[self.rec_num].definizione_struttura))
            self.textEdit_descrizione_struttura.setText(self.DATA_LIST[self.rec_num].descrizione)
            self.textEdit_interpretazione_struttura.setText(self.DATA_LIST[self.rec_num].interpretazione)
            self.comboBox_datazione_estesa.setEditText(str(self.DATA_LIST[self.rec_num].datazione_estesa))

            self.tableInsertData("self.tableWidget_materiali_impiegati", self.DATA_LIST[self.rec_num].materiali_impiegati)
            self.tableInsertData("self.tableWidget_elementi_strutturali", self.DATA_LIST[self.rec_num].elementi_strutturali)
            self.tableInsertData("self.tableWidget_rapporti", self.DATA_LIST[self.rec_num].rapporti_struttura)
            self.tableInsertData("self.tableWidget_misurazioni", self.DATA_LIST[self.rec_num].misure_struttura)

            if self.DATA_LIST[self.rec_num].periodo_iniziale is None:
                self.comboBox_per_iniz.setEditText("")
            else:
                self.comboBox_per_iniz.setEditText(str(self.DATA_LIST[self.rec_num].periodo_iniziale))

            if self.DATA_LIST[self.rec_num].fase_iniziale is None:
                self.comboBox_fas_iniz.setEditText("")
            else:
                self.comboBox_fas_iniz.setEditText(str(self.DATA_LIST[self.rec_num].fase_iniziale))

            if self.DATA_LIST[self.rec_num].periodo_finale is None:
                self.comboBox_per_fin.setEditText("")
            else:
                self.comboBox_per_fin.setEditText(str(self.DATA_LIST[self.rec_num].periodo_finale))

            if self.DATA_LIST[self.rec_num].fase_finale is None:
                self.comboBox_fas_fin.setEditText("")
            else:
                self.comboBox_fas_fin.setEditText(str(self.DATA_LIST[self.rec_num].fase_finale))

            if self.toolButtonPreview.isChecked():
                self.loadMapPreview()
            if self.toolButtonPreviewMedia.isChecked():
                self.loadMediaPreview()
        except:
            pass

    def set_rec_counter(self, t, c):
        self.rec_tot = t
        self.rec_corr = c
        self.label_rec_tot.setText(str(self.rec_tot))
        self.label_rec_corrente.setText(str(self.rec_corr))

    def set_LIST_REC_TEMP(self):
        # Get periodo values
        if not self.comboBox_per_iniz.currentText():
            periodo_iniziale = None
        else:
            periodo_iniziale = str(self.comboBox_per_iniz.currentText())

        if not self.comboBox_fas_iniz.currentText():
            fase_iniziale = None
        else:
            fase_iniziale = str(self.comboBox_fas_iniz.currentText())

        if not self.comboBox_per_fin.currentText():
            periodo_finale = None
        else:
            periodo_finale = str(self.comboBox_per_fin.currentText())

        if not self.comboBox_fas_fin.currentText():
            fase_finale = None
        else:
            fase_finale = str(self.comboBox_fas_fin.currentText())

        # Build temporary record list matching TABLE_FIELDS order
        self.DATA_LIST_REC_TEMP = [
            str(self.comboBox_sito.currentText()),  # sito
            str(self.comboBox_sigla_struttura.currentText()),  # sigla_struttura
            str(self.numero_struttura.text()),  # numero_struttura
            str(self.comboBox_categoria_struttura.currentText()),  # categoria_struttura
            str(self.comboBox_tipologia_struttura.currentText()),  # tipologia_struttura
            str(self.comboBox_definizione_struttura.currentText()),  # definizione_struttura
            str(self.textEdit_descrizione_struttura.toPlainText()),  # descrizione
            str(self.textEdit_interpretazione_struttura.toPlainText()),  # interpretazione
            str(periodo_iniziale),  # periodo_iniziale
            str(fase_iniziale),  # fase_iniziale
            str(periodo_finale),  # periodo_finale
            str(fase_finale),  # fase_finale
            str(self.comboBox_datazione_estesa.currentText()),  # datazione_estesa
            str(self.table2dict("self.tableWidget_materiali_impiegati")),  # materiali_impiegati
            str(self.table2dict("self.tableWidget_elementi_strutturali")),  # elementi_strutturali
            str(self.table2dict("self.tableWidget_rapporti")),  # rapporti_struttura
            str(self.table2dict("self.tableWidget_misurazioni"))  # misure_struttura
        ]

    def set_LIST_REC_CORR(self):
        self.DATA_LIST_REC_CORR = []
        for i in self.TABLE_FIELDS:
            self.DATA_LIST_REC_CORR.append(str(getattr(self.DATA_LIST[self.REC_CORR], i)))

    def records_equal_check(self):
        self.set_LIST_REC_TEMP()
        self.set_LIST_REC_CORR()

        if self.DATA_LIST_REC_CORR == self.DATA_LIST_REC_TEMP:
            return 0
        else:
            return 1

    def charge_periodo_iniz_list(self):
        sito = str(self.comboBox_sito.currentText())
        # sitob = sito.decode('utf-8')

        search_dict = {
            'sito': "'" + sito + "'"
        }

        periodo_vl = self.DB_MANAGER.query_bool(search_dict, 'PERIODIZZAZIONE')

        periodo_list = []

        for i in range(len(periodo_vl)):
            periodo_list.append(str(periodo_vl[i].periodo))
        try:
            periodo_vl.remove('')
        except:
            pass

        self.comboBox_per_iniz.clear()
        self.comboBox_per_iniz.addItems(self.UTILITY.remove_dup_from_list(periodo_list))

        if self.STATUS_ITEMS[self.BROWSE_STATUS] == "Trova" or "Find":
            self.comboBox_per_iniz.setEditText("")
        elif self.STATUS_ITEMS[self.BROWSE_STATUS] == "Usa" or "Current":
            if len(self.DATA_LIST) > 0:
                try:
                    self.comboBox_per_iniz.setEditText(self.DATA_LIST[self.rec_num].periodo_iniziale)
                except:
                    pass  # non vi sono periodi per questo scavo

    def charge_periodo_fin_list(self):
        search_dict = {
            'sito': "'" + str(self.comboBox_sito.currentText()) + "'"
        }

        periodo_vl = self.DB_MANAGER.query_bool(search_dict, 'PERIODIZZAZIONE')
        periodo_list = []

        for i in range(len(periodo_vl)):
            periodo_list.append(str(periodo_vl[i].periodo))
        try:
            periodo_vl.remove('')
        except:
            pass

        self.comboBox_per_fin.clear()
        self.comboBox_per_fin.addItems(self.UTILITY.remove_dup_from_list(periodo_list))

        if self.STATUS_ITEMS[self.BROWSE_STATUS] == "Trova" or "Find":
            self.comboBox_per_fin.setEditText("")
        elif self.STATUS_ITEMS[self.BROWSE_STATUS] == "Usa" or "Current":
            if len(self.DATA_LIST) > 0:
                try:
                    self.comboBox_per_fin.setEditText(self.DATA_LIST[self.rec_num].periodo_iniziale)
                except:
                    pass

    def charge_fase_iniz_list(self):
        try:
            search_dict = {
                'sito': "'" + str(self.comboBox_sito.currentText()) + "'",
                'periodo': "'" + str(self.comboBox_per_iniz.currentText()) + "'",
            }

            fase_list_vl = self.DB_MANAGER.query_bool(search_dict, 'PERIODIZZAZIONE')

            fase_list = []

            for i in range(len(fase_list_vl)):
                fase_list.append(str(fase_list_vl[i].fase))

            try:
                fase_list.remove('')
            except:
                pass

            self.comboBox_fas_iniz.clear()

            fase_list.sort()
            self.comboBox_fas_iniz.addItems(self.UTILITY.remove_dup_from_list(fase_list))

            if self.STATUS_ITEMS[self.BROWSE_STATUS] == "Trova" or "Find":
                self.comboBox_fas_iniz.setEditText("")
            else:
                self.comboBox_fas_iniz.setEditText(self.DATA_LIST[self.rec_num].fase_iniziale)
        except:
            pass


    def charge_fase_fin_list(self):
        try:
            search_dict = {
                'sito': "'" + str(self.comboBox_sito.currentText()) + "'",
                'periodo': "'" + str(self.comboBox_per_fin.currentText()) + "'",
            }

            fase_list_vl = self.DB_MANAGER.query_bool(search_dict, 'PERIODIZZAZIONE')

            fase_list = []

            for i in range(len(fase_list_vl)):
                fase_list.append(str(fase_list_vl[i].fase))

            try:
                fase_list.remove('')
            except:
                pass

            self.comboBox_fas_fin.clear()
            fase_list.sort()
            self.comboBox_fas_fin.addItems(self.UTILITY.remove_dup_from_list(fase_list))

            if self.STATUS_ITEMS[self.BROWSE_STATUS] == "Trova" or "Find":
                self.comboBox_fas_fin.setEditText("")
            else:
                self.comboBox_fas_fin.setEditText(self.DATA_LIST[self.rec_num].fase_finale)
        except:
            pass

            # buttons functions

    def charge_datazione_list(self):
        if self.comboBox_sito.editTextChanged: 
            try:
                search_dict = {
                    'sito': "'" + str(self.comboBox_sito.currentText()) + "'",
                    'periodo': "'" + str(self.comboBox_per_iniz.currentText()) + "'",
                    'fase': "'" + str(self.comboBox_fas_iniz.currentText()) + "'"
                }
                datazione_list_vl = self.DB_MANAGER.query_bool(search_dict, 'PERIODIZZAZIONE')
                datazione_list = []
                for i in range(len(datazione_list_vl)):
                    datazione_list.append(str(datazione_list_vl[i].datazione_estesa))
                try:
                    datazione_list.remove('')
                except:
                    pass
                self.comboBox_datazione_estesa.clear()
                datazione_list.sort()
                self.comboBox_datazione_estesa.addItems(self.UTILITY.remove_dup_from_list(datazione_list))
                if self.STATUS_ITEMS[self.BROWSE_STATUS] == "Trova" or "Find":
                    self.comboBox_datazione_estesa.setEditText("")
                else:
                    self.comboBox_datazione_estesa.setEditText(self.DATA_LIST[self.rec_num].datazione_estesa)
            except:
                pass
    
    def on_pushButton_sort_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            dlg = SortPanelMain(self)
            dlg.insertItems(self.SORT_ITEMS)
            dlg.exec()

            items, order_type = dlg.ITEMS, dlg.TYPE_ORDER

            items_converted = []
            for i in items:
                items_converted.append(self.CONVERSION_DICT[i])

            self.SORT_MODE = order_type
            self.empty_fields()

            id_list = []
            for i in self.DATA_LIST:
                id_list.append(getattr(i, self.ID_TABLE))
            self.DATA_LIST = []

            temp_data_list = self.DB_MANAGER.query_sort(id_list, items_converted, order_type, self.MAPPER_TABLE_CLASS,
                                                        self.ID_TABLE)

            for i in temp_data_list:
                self.DATA_LIST.append(i)
            self.BROWSE_STATUS = "b"
            self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
            if type(self.REC_CORR) == "<type 'str'>":
                corr = 0
            else:
                corr = self.REC_CORR

            self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
            self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
            self.label_sort.setText(self.SORTED_ITEMS["o"])
            self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
            self.fill_fields()

    def add_value_to_categoria(self):
        if str(self.comboBox_sigla_struttura.currentText()) == '':
            self.setComboBoxEditable(["self.comboBox_sigla_struttura"], 1)

    def on_pushButton_new_rec_pressed(self):
        conn = Connection()
        
        sito_set= conn.sito_set()
        sito_set_str = sito_set['sito_set']
        
        if bool(self.DATA_LIST):
            if self.data_error_check() == 1:
                pass
            # else:
                # if self.BROWSE_STATUS == "b":
                    # if bool(self.DATA_LIST):
                        # if self.records_equal_check() == 1:
                            # if self.L=='it':
                                # self.update_if(QMessageBox.warning(self, 'Errore',
                                                                   # "Il record e' stato modificato. Vuoi salvare le modifiche?",QMessageBox.Ok | QMessageBox.Cancel))
                            # elif self.L=='de':
                                # self.update_if(QMessageBox.warning(self, 'Error',
                                                                   # "Der Record wurde geändert. Möchtest du die Änderungen speichern?",
                                                                   # QMessageBox.Ok | QMessageBox.Cancel))
                                                                   
                            # else:
                                # self.update_if(QMessageBox.warning(self, 'Error',
                                                                   # "The record has been changed. Do you want to save the changes?",
                                                                   # QMessageBox.Ok | QMessageBox.Cancel))
                            # set the GUI for a new record
        if self.BROWSE_STATUS != "n":
            if bool(self.comboBox_sito.currentText()) and self.comboBox_sito.currentText()==sito_set_str:
                self.BROWSE_STATUS = "n"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.empty_fields_nosite()
                self.label_sort.setText(self.SORTED_ITEMS["n"])
                self.SORT_STATUS = "n"
                #self.setComboBoxEditable(["self.comboBox_sito"], 1)
                self.setComboBoxEditable(["self.comboBox_sigla_struttura"], 0)
                self.setComboBoxEnable(["self.comboBox_sito"], False)
                self.setComboBoxEnable(["self.comboBox_sigla_struttura"], True)
                self.setComboBoxEnable(["self.numero_struttura"], True)

                self.set_rec_counter('', '')
            else:
                self.BROWSE_STATUS = "n"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
                self.empty_fields()
                self.label_sort.setText(self.SORTED_ITEMS["n"])

                self.setComboBoxEditable(["self.comboBox_sito"], 1)
                self.setComboBoxEditable(["self.comboBox_sigla_struttura"], 1)
                self.setComboBoxEnable(["self.comboBox_sito"], True)
                self.setComboBoxEnable(["self.comboBox_sigla_struttura"], True)
                self.setComboBoxEnable(["self.numero_struttura"], True)

                self.set_rec_counter('', '')
            self.enable_button(0)

    def on_pushButton_save_pressed(self):
        # save record
        # save record
        if self.BROWSE_STATUS == "b":
            if self.data_error_check() == 0:
                if self.records_equal_check() == 1:
                    if self.L=='it':
                        self.update_if(QMessageBox.warning(self, 'Errore',
                                                           "Il record e' stato modificato. Vuoi salvare le modifiche?",QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))
                    elif self.L=='de':
                        self.update_if(QMessageBox.warning(self, 'Error',
                                                           "Der Record wurde geändert. Möchtest du die Änderungen speichern?",
                                                           QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))
                                                    
                    else:
                        self.update_if(QMessageBox.warning(self, 'Error',
                                                           "The record has been changed. Do you want to save the changes?",
                                                           QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))
                    self.empty_fields()
                    self.SORT_STATUS = "n"
                    self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
                    self.enable_button(1)
                    self.fill_fields(self.REC_CORR)
                else:
                    if self.L=='it':
                        QMessageBox.warning(self, "ATTENZIONE", "Non è stata realizzata alcuna modifica.", QMessageBox.StandardButton.Ok)
                    elif self.L=='de':
                        QMessageBox.warning(self, "ACHTUNG", "Keine Änderung vorgenommen", QMessageBox.StandardButton.Ok)
                    else:
                        QMessageBox.warning(self, "Warning", "No changes have been made", QMessageBox.StandardButton.Ok)   
        else:
            if self.data_error_check() == 0:
                test_insert = self.insert_new_rec()
                if test_insert == 1:
                    self.empty_fields()
                    self.SORT_STATUS = "n"
                    self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
                    self.charge_records()
                    self.charge_list()
                    self.set_sito()
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), len(self.DATA_LIST) - 1
                    self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)

                    self.setComboBoxEditable(["self.comboBox_sito"], 1)
                    self.setComboBoxEditable(["self.comboBox_sigla_struttura"], 1)
                    self.setComboBoxEnable(["self.comboBox_sito"], False)
                    self.setComboBoxEnable(["self.comboBox_sigla_struttura"], False)
                    self.setComboBoxEnable(["self.numero_struttura"], False)

                    self.fill_fields(self.REC_CORR)
                    self.enable_button(1)

                    if self.L=='it':
                        QMessageBox.information(self, "Messaggio", "Record inserito con successo!", QMessageBox.StandardButton.Ok)
                    elif self.L=='de':
                        QMessageBox.information(self, "Nachricht", "Datensatz erfolgreich eingefügt!", QMessageBox.StandardButton.Ok)
                    else:
                        QMessageBox.information(self, "Message", "Record inserted successfully!", QMessageBox.StandardButton.Ok)
            else:
                    if self.L=='it':
                        QMessageBox.warning(self, "ATTENZIONE", "Problema nell'inserimento dati", QMessageBox.StandardButton.Ok)
                    elif self.L=='de':
                        QMessageBox.warning(self, "ACHTUNG", "Problem der Dateneingabe", QMessageBox.StandardButton.Ok)
                    else:
                        QMessageBox.warning(self, "Warning", "Problem with data entry", QMessageBox.StandardButton.Ok)    

    def data_error_check(self):
        test = 0
        EC = Error_check()

        nr_struttura = self.numero_struttura.text()
        if self.L=='it':
            if EC.data_is_empty(str(self.comboBox_sito.currentText())) == 0:
                QMessageBox.warning(self, "ATTENZIONE", "Campo Sito \n Il campo non deve essere vuoto", QMessageBox.StandardButton.Ok)
                test = 1

            if EC.data_is_empty(str(self.comboBox_sigla_struttura.currentText())) == 0:
                QMessageBox.warning(self, "ATTENZIONE", "Campo Sigla Struttura \n Il campo non deve essere vuoto",
                                    QMessageBox.StandardButton.Ok)
                test = 1

            if EC.data_is_empty(str(self.numero_struttura.text())) == 0:
                QMessageBox.warning(self, "ATTENZIONE", "Campo Nr Struttura \n Il campo non deve essere vuoto",
                                    QMessageBox.StandardButton.Ok)
                test = 1

            if nr_struttura != "":
                if EC.data_is_int(nr_struttura) == 0:
                    QMessageBox.warning(self, "ATTENZIONE", "Campo Nr Struttura. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.StandardButton.Ok)
                    test = 1

        elif self.L=='de':
            if EC.data_is_empty(str(self.comboBox_sito.currentText())) == 0:
                QMessageBox.warning(self, "ACHTUNG", " Feld Ausgrabungstätte \n Das Feld darf nicht leer sein", QMessageBox.StandardButton.Ok)
                test = 1

            if EC.data_is_empty(str(self.comboBox_sigla_struttura.currentText())) == 0:
                QMessageBox.warning(self, "ACHTUNG", " Feld Strukturcode \n Das Feld darf nicht leer sein",QMessageBox.StandardButton.Ok)
                test = 1

            if EC.data_is_empty(str(self.numero_struttura.text())) == 0:
                QMessageBox.warning(self, "ACHTUNG", " Feld Strukturcode \n Das Feld darf nicht leer sein",QMessageBox.StandardButton.Ok)
                test = 1

            if nr_struttura != "":
                if EC.data_is_int(nr_struttura) == 0:
                    QMessageBox.warning(self,"ACHTUNG", " Feld Strukturcode \n Der Wert muss numerisch eingegeben werden", QMessageBox.StandardButton.Ok)
                    test = 1
        
        else:
            if EC.data_is_empty(str(self.comboBox_sito.currentText())) == 0:
                QMessageBox.warning(self, "WARNING", "Site Field \n The field must not be empty", QMessageBox.StandardButton.Ok)
                test = 1  

            if EC.data_is_empty(str(self.comboBox_sigla_struttura.currentText())) == 0:
                QMessageBox.warning(self, "WARNING", "Structure code Field \n The field must not be empty",QMessageBox.StandardButton.Ok)
                test = 1

            if EC.data_is_empty(str(self.numero_struttura.text())) == 0:
                QMessageBox.warning(self, "WARNING", "Structure Nr. Field \n The field must not be empty", QMessageBox.StandardButton.Ok)
                test = 1

            if nr_struttura != "":
                if EC.data_is_int(nr_struttura) == 0:
                    QMessageBox.warning(self, "WARNING", "Structure Nr. Field \n The value must be numerical",QMessageBox.StandardButton.Ok)
                    test = 1
        
        return test

    def insert_new_rec(self):

        # TableWidget
        ##Materiali_impiegati
        materiali_impiegati = self.table2dict("self.tableWidget_materiali_impiegati")
        ##Elementi_strutturali
        elementi_strutturali = self.table2dict("self.tableWidget_elementi_strutturali")
        ##Rapporti_struttura
        rapporti_struttura = self.table2dict("self.tableWidget_rapporti")
        ##Misurazioni
        misurazioni = self.table2dict("self.tableWidget_misurazioni")

        if self.comboBox_per_iniz.currentText() == "":
            per_iniz = None
        else:
            per_iniz = int(self.comboBox_per_iniz.currentText())

        if self.comboBox_fas_iniz.currentText() == "":
            fas_iniz = None
        else:
            fas_iniz = int(self.comboBox_fas_iniz.currentText())

        if self.comboBox_per_fin.currentText() == "":
            per_fin = None
        else:
            per_fin = int(self.comboBox_per_fin.currentText())

        if self.comboBox_fas_fin.currentText() == "":
            fas_fin = None
        else:
            fas_fin = int(self.comboBox_fas_fin.currentText())

        try:
            data = self.DB_MANAGER.insert_struttura_values(
                self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, self.ID_TABLE) + 1,  # 0
                str(self.comboBox_sito.currentText()),  # 1 - Sito
                str(self.comboBox_sigla_struttura.currentText()),  # 2 - sigla_struttura
                int(self.numero_struttura.text()),  # 3 - numero_struttura
                str(self.comboBox_categoria_struttura.currentText()),  # 4 - categoria_struttura
                str(self.comboBox_tipologia_struttura.currentText()),  # 5 - tipologia_struttura
                str(self.comboBox_definizione_struttura.currentText()),  # 6 - definizione_struttura
                str(self.textEdit_descrizione_struttura.toPlainText()),  # 7 - descrizione
                str(self.textEdit_interpretazione_struttura.toPlainText()),  # 8 - interpretazione
                per_iniz,  # 9 - periodo iniziale
                fas_iniz,  # 10 - fase iniziale
                per_fin,  # 11 - periodo finale iniziale
                fas_fin,  # 12 - fase finale
                str(self.comboBox_datazione_estesa.currentText()),  # 13 - datazione estesa
                str(materiali_impiegati),  # 14 - materiali impiegati
                str(elementi_strutturali),  # 15 - elementi_strutturali
                str(rapporti_struttura),  # 16 - rapporti struttura
                str(misurazioni))  # 17 - misurazioni

            try:
                self.DB_MANAGER.insert_data_session(data)
                return 1
            except Exception as e:
                e_str = str(e)
                if e_str.__contains__("IntegrityError"):
                    
                    if self.L=='it':
                        msg = self.ID_TABLE + " gia' presente nel database"
                        QMessageBox.warning(self, "Error", "Error" + str(msg), QMessageBox.StandardButton.Ok)
                    elif self.L=='de':
                        msg = self.ID_TABLE + " bereits in der Datenbank"
                        QMessageBox.warning(self, "Error", "Error" + str(msg), QMessageBox.StandardButton.Ok)  
                    else:
                        msg = self.ID_TABLE + " exist in db"
                        QMessageBox.warning(self, "Error", "Error" + str(msg), QMessageBox.StandardButton.Ok)  
                else:
                    msg = e
                    QMessageBox.warning(self, "Error", "Error 1 \n" + str(msg), QMessageBox.StandardButton.Ok)
                return 0

        except Exception as e:
            QMessageBox.warning(self, "Error", "Error 2 \n" + str(e), QMessageBox.StandardButton.Ok)
            return 0

    def check_record_state(self):
        ec = self.data_error_check()
        if ec == 1:
            return 1  # ci sono errori di immissione
        elif self.records_equal_check() == 1 and ec == 0:
            if self.L=='it':
                self.update_if(
                
                    QMessageBox.warning(self, 'Errore', "Il record e' stato modificato. Vuoi salvare le modifiche?",
                                        QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))
            elif self.L=='de':
                self.update_if(
                    QMessageBox.warning(self, 'Errore', "Der Record wurde geändert. Möchtest du die Änderungen speichern?",
                                        QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))
            else:
                self.update_if(
                    QMessageBox.warning(self, "Error", "The record has been changed. You want to save the changes?",
                                        QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))
            # self.charge_records()
            return 0  # non ci sono errori di immissione

            # records surf functions

    def on_pushButton_view_all_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            self.empty_fields()
            self.charge_records()
            self.fill_fields()
            self.BROWSE_STATUS = "b"
            self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
            if type(self.REC_CORR) == "<type 'str'>":
                corr = 0
            else:
                corr = self.REC_CORR
            self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
            self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
            self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
            self.label_sort.setText(self.SORTED_ITEMS["n"])

            # records surf functions

    def on_pushButton_first_rec_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            try:
                self.empty_fields()
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                self.fill_fields(0)
                self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e), QMessageBox.StandardButton.Ok)

    def on_pushButton_last_rec_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            try:
                self.empty_fields()
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), len(self.DATA_LIST) - 1
                self.fill_fields(self.REC_CORR)
                self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e), QMessageBox.StandardButton.Ok)

    def on_pushButton_prev_rec_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            self.REC_CORR = self.REC_CORR - 1
            if self.REC_CORR == -1:
                self.REC_CORR = 0
                if self.L=='it':
                    QMessageBox.warning(self, "Attenzione", "Sei al primo record!", QMessageBox.StandardButton.Ok)
                elif self.L=='de':
                    QMessageBox.warning(self, "Achtung", "du befindest dich im ersten Datensatz!", QMessageBox.StandardButton.Ok)
                else:
                    QMessageBox.warning(self, "Warning", "You are to the first record!", QMessageBox.StandardButton.Ok)        
            else:
                try:
                    self.empty_fields()
                    self.fill_fields(self.REC_CORR)
                    self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
                except Exception as e:
                    QMessageBox.warning(self, "Error", str(e), QMessageBox.StandardButton.Ok)

    def on_pushButton_next_rec_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            self.REC_CORR = self.REC_CORR + 1
            if self.REC_CORR >= self.REC_TOT:
                self.REC_CORR = self.REC_CORR - 1
                if self.L=='it':
                    QMessageBox.warning(self, "Attenzione", "Sei all'ultimo record!", QMessageBox.StandardButton.Ok)
                elif self.L=='de':
                    QMessageBox.warning(self, "Achtung", "du befindest dich im letzten Datensatz!", QMessageBox.StandardButton.Ok)
                else:
                    QMessageBox.warning(self, "Error", "You are to the first record!", QMessageBox.StandardButton.Ok)  
            else:
                try:
                    self.empty_fields()
                    self.fill_fields(self.REC_CORR)
                    self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
                except Exception as e:
                    QMessageBox.warning(self, "Error", str(e), QMessageBox.StandardButton.Ok)

    def on_pushButton_delete_pressed(self):
        
        if self.L=='it':
            msg = QMessageBox.warning(self, "Attenzione!!!",
                                      "Vuoi veramente eliminare il record? \n L'azione è irreversibile",
                                      QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            if msg == QMessageBox.StandardButton.Cancel:
                QMessageBox.warning(self, "Messagio!!!", "Azione Annullata!")
            else:
                try:
                    id_to_delete = getattr(self.DATA_LIST[self.REC_CORR], self.ID_TABLE)
                    self.DB_MANAGER.delete_one_record(self.TABLE_NAME, self.ID_TABLE, id_to_delete)
                    self.charge_records()  # charge records from DB
                    QMessageBox.warning(self, "Messaggio!!!", "Record eliminato!")
                except Exception as e:
                    QMessageBox.warning(self, "Messaggio!!!", "Tipo di errore: " + str(e))
                if not bool(self.DATA_LIST):
                    QMessageBox.warning(self, "Attenzione", "Il database è vuoto!", QMessageBox.StandardButton.Ok)
                    self.DATA_LIST = []
                    self.DATA_LIST_REC_CORR = []
                    self.DATA_LIST_REC_TEMP = []
                    self.REC_CORR = 0
                    self.REC_TOT = 0
                    self.empty_fields()
                    self.set_rec_counter(0, 0)
                    # check if DB is empty
                if bool(self.DATA_LIST):
                    self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                    self.charge_list()
                    self.fill_fields()
                    self.set_sito()
        elif self.L=='de':
            msg = QMessageBox.warning(self, "Achtung!!!",
                                      "Willst du wirklich diesen Eintrag löschen? \n Der Vorgang ist unumkehrbar",
                                      QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            if msg == QMessageBox.StandardButton.Cancel:
                QMessageBox.warning(self, "Message!!!", "Aktion annulliert!")
            else:
                try:
                    id_to_delete = getattr(self.DATA_LIST[self.REC_CORR], self.ID_TABLE)
                    self.DB_MANAGER.delete_one_record(self.TABLE_NAME, self.ID_TABLE, id_to_delete)
                    self.charge_records()  # charge records from DB
                    QMessageBox.warning(self, "Message!!!", "Record gelöscht!")
                except Exception as e:
                    QMessageBox.warning(self, "Messagge!!!", "Errortyp: " + str(e))
                if not bool(self.DATA_LIST):
                    QMessageBox.warning(self, "Achtung", "Die Datenbank ist leer!", QMessageBox.StandardButton.Ok)
                    self.DATA_LIST = []
                    self.DATA_LIST_REC_CORR = []
                    self.DATA_LIST_REC_TEMP = []
                    self.REC_CORR = 0
                    self.REC_TOT = 0
                    self.empty_fields()
                    self.set_rec_counter(0, 0)
                    # check if DB is empty
                if bool(self.DATA_LIST):
                    self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                    self.charge_list()
                    self.fill_fields()
                    self.set_sito()
        else:
            msg = QMessageBox.warning(self, "Warning!!!",
                                      "Do you really want to break the record? \n Action is irreversible.",
                                      QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            if msg == QMessageBox.StandardButton.Cancel:
                QMessageBox.warning(self, "Message!!!", "Action deleted!")
            else:
                try:
                    id_to_delete = getattr(self.DATA_LIST[self.REC_CORR], self.ID_TABLE)
                    self.DB_MANAGER.delete_one_record(self.TABLE_NAME, self.ID_TABLE, id_to_delete)
                    self.charge_records()  # charge records from DB
                    QMessageBox.warning(self, "Message!!!", "Record deleted!")
                except Exception as e:
                    QMessageBox.warning(self, "Message!!!", "error type: " + str(e))
                if not bool(self.DATA_LIST):
                    QMessageBox.warning(self, "Warning", "the db is empty!", QMessageBox.StandardButton.Ok)
                    self.DATA_LIST = []
                    self.DATA_LIST_REC_CORR = []
                    self.DATA_LIST_REC_TEMP = []
                    self.REC_CORR = 0
                    self.REC_TOT = 0
                    self.empty_fields()
                    self.set_rec_counter(0, 0)
                    # check if DB is empty
                if bool(self.DATA_LIST):
                    self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                    self.charge_list()
                    self.fill_fields()
                    self.set_sito()                    
            
            
            
            self.SORT_STATUS = "n"
            self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])

    def on_pushButton_new_search_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            self.enable_button_search(0)
            conn = Connection()
        
            sito_set= conn.sito_set()
            sito_set_str = sito_set['sito_set']
            if self.BROWSE_STATUS != "f":
                if bool(self.comboBox_sito.currentText()) and self.comboBox_sito.currentText()==sito_set_str:
                    self.BROWSE_STATUS = "f"
                    ###
                    #self.setComboBoxEditable(["self.comboBox_sito"], 1)
                    self.setComboBoxEditable(["self.comboBox_sigla_struttura"], 1)
                    self.setComboBoxEnable(["self.comboBox_sito"], False)
                    self.setComboBoxEnable(["self.comboBox_sigla_struttura"], True)
                    self.setComboBoxEnable(["self.numero_struttura"], True)

                    self.setComboBoxEnable(["self.textEdit_descrizione_struttura"], False)
                    self.setComboBoxEnable(["self.textEdit_interpretazione_struttura"], False)
                    self.setTableEnable(["self.tableWidget_materiali_impiegati", "self.tableWidget_elementi_strutturali",
                                         "self.tableWidget_rapporti",
                                         "self.tableWidget_misurazioni"], False)

                    ###
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.set_rec_counter('', '')
                    self.label_sort.setText(self.SORTED_ITEMS["n"])
                    #self.charge_list()
                    self.empty_fields_nosite()
                else:
                    self.BROWSE_STATUS = "f"
                    ###
                    self.setComboBoxEditable(["self.comboBox_sito"], 0)
                    self.setComboBoxEditable(["self.comboBox_sigla_struttura"], 1)
                    self.setComboBoxEnable(["self.comboBox_sito"], True)
                    self.setComboBoxEnable(["self.comboBox_sigla_struttura"], True)
                    self.setComboBoxEnable(["self.numero_struttura"], True)

                    self.setComboBoxEnable(["self.textEdit_descrizione_struttura"], False)
                    self.setComboBoxEnable(["self.textEdit_interpretazione_struttura"], False)
                    self.setTableEnable(["self.tableWidget_materiali_impiegati", "self.tableWidget_elementi_strutturali",
                                         "self.tableWidget_rapporti",
                                         "self.tableWidget_misurazioni"], False)

                    ###
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.set_rec_counter('', '')
                    self.label_sort.setText(self.SORTED_ITEMS["n"])
                    self.charge_list()
                    self.empty_fields()
    def on_pushButton_search_go_pressed(self):
        if self.BROWSE_STATUS != "f":
            if self.L=='it':
                QMessageBox.warning(self, "ATTENZIONE", "Per eseguire una nuova ricerca clicca sul pulsante 'new search' ",
                                    QMessageBox.StandardButton.Ok)
            elif self.L=='de':
                QMessageBox.warning(self, "ACHTUNG", "Um eine neue Abfrage zu starten drücke  'new search' ",
                                    QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.warning(self, "WARNING", "To perform a new search click on the 'new search' button ",
                                    QMessageBox.StandardButton.Ok) 
        else:
            if self.numero_struttura.text() != "":
                numero_struttura = int(self.numero_struttura.text())
            else:
                numero_struttura = ""

            if self.comboBox_per_iniz.currentText() != "":
                periodo_iniziale = int(self.comboBox_per_iniz.currentText())
            else:
                periodo_iniziale = ""

            if self.comboBox_fas_iniz.currentText() != "":
                fase_iniziale = int(self.comboBox_fas_iniz.currentText())
            else:
                fase_iniziale = ""

            if self.comboBox_per_fin.currentText() != "":
                periodo_finale = int(self.comboBox_per_fin.currentText())
            else:
                periodo_finale = ""

            if self.comboBox_fas_fin.currentText() != "":
                fase_finale = int(self.comboBox_fas_fin.currentText())
            else:
                fase_finale = ""

            search_dict = {
                self.TABLE_FIELDS[0]: "'" + str(self.comboBox_sito.currentText()) + "'",  # 1 - Sito
                self.TABLE_FIELDS[1]: "'" + str(self.comboBox_sigla_struttura.currentText()) + "'",
                # 2 - Sigla struttura
                self.TABLE_FIELDS[2]: numero_struttura,  # 3 - numero struttura
                self.TABLE_FIELDS[3]: "'" + str(self.comboBox_categoria_struttura.currentText()) + "'",
                # 4 - categoria struttura
                self.TABLE_FIELDS[4]: "'" + str(self.comboBox_tipologia_struttura.currentText()) + "'",
                # 5 - tipologia struttura
                self.TABLE_FIELDS[5]: "'" + str(self.comboBox_definizione_struttura.currentText()) + "'",
                # 6 - definizione struttura
                # self.TABLE_FIELDS[6] : str(self.textEdit_descrizione_struttura.toPlainText()),                                #7 - descrizione struttura
                # self.TABLE_FIELDS[7] : str(self.textEdit_interpretazione_struttura.toPlainText()),                            #8 - intepretazione struttura
                self.TABLE_FIELDS[8]: periodo_iniziale,  # 9 - periodo iniziale
                self.TABLE_FIELDS[9]: fase_iniziale,  # 10 - fase iniziale
                self.TABLE_FIELDS[10]: periodo_finale,  # 11 - periodo finale
                self.TABLE_FIELDS[11]: fase_finale,  # 12 - fase finale
                self.TABLE_FIELDS[12]: "'" + str(self.comboBox_datazione_estesa.currentText()) + "'"  # 10 - datazione_estesa
            }

            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)

            if not bool(search_dict):
                if self.L=='it':
                    QMessageBox.warning(self, "ATTENZIONE", "Non è stata impostata nessuna ricerca!!!", QMessageBox.StandardButton.Ok)
                elif self.L=='de':
                    QMessageBox.warning(self, "ACHTUNG", "Keine Abfrage definiert!!!", QMessageBox.StandardButton.Ok)
                else:
                    QMessageBox.warning(self, " WARNING", "No search has been set!!!", QMessageBox.StandardButton.Ok)      
            else:
                res = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
                if not bool(res):
                    if self.L=='it':
                        QMessageBox.warning(self, "ATTENZIONE", "Non è stato trovato nessun record!", QMessageBox.StandardButton.Ok)
                    elif self.L=='de':
                        QMessageBox.warning(self, "ACHTUNG", "Keinen Record gefunden!", QMessageBox.StandardButton.Ok)
                    else:
                        QMessageBox.warning(self, "WARNING," "No record found!", QMessageBox.StandardButton.Ok)

                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]

                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])

                    self.setComboBoxEnable(["self.comboBox_sito"], False)
                    self.setComboBoxEnable(["self.comboBox_sigla_struttura"], False)
                    self.setComboBoxEnable(["self.numero_struttura"], False)
                    self.setComboBoxEditable(["self.comboBox_sito"], 1)
                    self.setComboBoxEditable(["self.comboBox_sigla_struttura"], 1)

                    self.setComboBoxEnable(["self.textEdit_descrizione_struttura"], True)
                    self.setComboBoxEnable(["self.textEdit_interpretazione_struttura"], True)
                    self.setTableEnable(
                        ["self.tableWidget_materiali_impiegati", "self.tableWidget_elementi_strutturali",
                         "self.tableWidget_rapporti",
                         "self.tableWidget_misurazioni"], True)

                    self.fill_fields(self.REC_CORR)
                else:
                    self.DATA_LIST = []
                    for i in res:
                        self.DATA_LIST.append(i)
                    self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                    self.fill_fields()
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                    if self.L=='it':
                        if self.REC_TOT == 1:
                            strings = ("E' stato trovato", self.REC_TOT, "record")
                            if self.toolButton_draw_strutture.isChecked():
                                # sing_layer = [self.DATA_LIST[self.REC_CORR]]
                                self.pyQGIS.charge_structure_from_research(self.DATA_LIST)
                        else:
                            strings = ("Sono stati trovati", self.REC_TOT, "records")
                            if self.toolButton_draw_strutture.isChecked():
                                # sing_layer = [self.DATA_LIST[self.REC_CORR]]
                                self.pyQGIS.charge_structure_from_research(self.DATA_LIST)
                    elif self.L=='de':
                        if self.REC_TOT == 1:
                            strings = ("Es wurde gefunden", self.REC_TOT, "record")
                            if self.toolButton_draw_strutture.isChecked():
                                # sing_layer = [self.DATA_LIST[self.REC_CORR]]
                                self.pyQGIS.charge_structure_from_research(self.DATA_LIST)
                        else:
                            strings = ("Sie wurden gefunden", self.REC_TOT, "records")
                            if self.toolButton_draw_strutture.isChecked():
                                # sing_layer = [self.DATA_LIST[self.REC_CORR]]
                                self.pyQGIS.charge_structure_from_research(self.DATA_LIST)
                                
                    else:
                        if self.REC_TOT == 1:
                            strings = ("It has been found", self.REC_TOT, "record")
                            if self.toolButton_draw_strutture.isChecked():
                                # sing_layer = [self.DATA_LIST[self.REC_CORR]]
                                self.pyQGIS.charge_structure_from_research(self.DATA_LIST)
                        else:
                            strings = ("They have been found", self.REC_TOT, "records")
                            if self.toolButton_draw_strutture.isChecked():
                                # sing_layer = [self.DATA_LIST[self.REC_CORR]]
                                self.pyQGIS.charge_structure_from_research(self.DATA_LIST)          
                    self.setComboBoxEditable(["self.comboBox_sito"], 1)
                    self.setComboBoxEditable(["self.comboBox_sigla_struttura"], 1)
                    self.setComboBoxEnable(["self.comboBox_sito"], False)
                    self.setComboBoxEnable(["self.comboBox_sigla_struttura"], False)
                    self.setComboBoxEnable(["self.numero_struttura"], False)

                    self.setComboBoxEnable(["self.textEdit_descrizione_struttura"], True)
                    self.setComboBoxEnable(["self.textEdit_interpretazione_struttura"], True)
                    self.setTableEnable(
                        ["self.tableWidget_materiali_impiegati", "self.tableWidget_elementi_strutturali",
                         "self.tableWidget_rapporti",
                         "self.tableWidget_misurazioni"], True)

                    QMessageBox.warning(self, "Message", "%s %d %s" % strings, QMessageBox.StandardButton.Ok)
        self.enable_button_search(1)

    # def on_pushButton_pdf_index_exp_pressed(self):
        # if self.L=='it':
            # Struttura_index_pdf = generate_struttura_pdf()
            # data_list = self.generate_list_pdf()
            # Struttura_index_pdf.build_index_Struttura(data_list, data_list[0][0])
        # elif self.L=='de':
            # Struttura_index_pdf = generate_struttura_pdf()
            # data_list = self.generate_list_pdf()
            # Struttura_index_pdf.build_index_Struttura_de(data_list, data_list[0][0])    
        # else:
            # Struttura_index_pdf = generate_struttura_pdf()
            # data_list = self.generate_list_pdf()
            # Struttura_index_pdf.build_index_Struttura_en(data_list, data_list[0][0])
    # def on_pushButton_pdf_exp_pressed(self):
        # if self.L=='it':
            # if self.checkBox_s_us.isChecked():
                # Struttura_pdf_sheet = generate_struttura_pdf()  # deve essere importata la classe
                # data_list = self.generate_list_pdf()  # deve essere aggiunta la funzione
                # Struttura_pdf_sheet.build_Struttura_sheets(data_list)  # deve essere aggiunto il file per generare i pdf
                # QMessageBox.warning(self, 'Ok',"Esportazione terminata Schede Struttura",QMessageBox.Ok)
            # else:   
                # pass
            # if self.checkBox_e_us.isChecked() :
                # Struttura_index_pdf = generate_struttura_pdf()
                # data_list = self.generate_list_pdf()
            
                # try:               
                    # if bool(data_list):
                        # Struttura_index_pdf.build_index_Struttura(data_list, data_list[0][0])
                        # QMessageBox.warning(self, 'Ok',"Esportazione terminata Elenco Struttura",QMessageBox.Ok)
                    # else:
                        # QMessageBox.warning(self, 'ATTENZIONE',"L'elenco Struttura non può essere esportato devi riempire prima la scheda Struttura",QMessageBox.Ok)
                # except Exception as e :
                    # QMessageBox.warning(self, 'ATTENZIONE',str(e),QMessageBox.Ok)
            # else:
                # pass
            
        
        # else:
            # if self.checkBox_s_us.isChecked():
                # Struttura_pdf_sheet = generate_struttura_pdf()  # deve essere importata la classe
                # data_list = self.generate_list_pdf()  # deve essere aggiunta la funzione
                # Struttura_pdf_sheet.build_Struttura_sheets(data_list)  # deve essere aggiunto il file per generare i pdf
                # QMessageBox.warning(self, 'Ok',"Exportation Done",QMessageBox.Ok)
            # else:   
                # pass
            # if self.checkBox_e_us.isChecked() :
                # Struttura_index_pdf = generate_struttura_pdf()
                # data_list = self.generate_list_pdf()
            
                # try:               
                    # if bool(data_list):
                        # Struttura_index_pdf.build_index_Struttura(data_list, data_list[0][0])
                        # QMessageBox.warning(self, 'Ok',"Exportation list done",QMessageBox.Ok)
                    # else:
                        # QMessageBox.warning(self, 'Warning',"The Structure list cannot be exported you have to fill in the Structure tabs before",QMessageBox.Ok)
                # except Exception as e :
                    # QMessageBox.warning(self, 'Warning',str(e),QMessageBox.Ok)
            # else:
                # pass
            
    def generate_list_pdf(self):
        data_list = []

        for i in range(len(self.DATA_LIST)):
            sito = str(self.DATA_LIST[i].sito)
            sigla_st = '{}{}{}'.format(str(self.DATA_LIST[i].sigla_struttura),'-', str(self.DATA_LIST[i].numero_struttura))            
            res_strutt = self.DB_MANAGER.query_bool({"sito": "'" + str(sito) + "'", "struttura": "'" + str(sigla_st) + "'"}, "US")
            us_strutt_list = []
            #if bool(res_strutt):
            for rs in res_strutt:
                us_strutt_list.append([str(rs.sito), str(rs.area), int(rs.us)])
                
            res_quote_strutt=''
            quote_strutt = []
            #if bool(us_strutt_list):
            for sing_us in us_strutt_list:
                res_quote_strutt = self.DB_MANAGER.select_quote_from_db_sql(sing_us[0], sing_us[1], sing_us[2])
                
            #if bool(res_quote_strutt):
            for sing_us2 in res_quote_strutt:
                sing_quota_value = str(sing_us2[5])
               
                if sing_quota_value[0] == '-':
                    sing_quota_value = sing_quota_value[:7]
                else:
                    sing_quota_value = sing_quota_value[:6]

                sing_quota = [sing_quota_value, sing_us2[4]]
                quote_strutt.append(sing_quota)
            quote_strutt.sort()

            if bool(quote_strutt):
                quota_min_strutt = '%s %s' % (quote_strutt[0][0], quote_strutt[0][1])
                quota_max_strutt = '%s %s' % (quote_strutt[-1][0], quote_strutt[-1][1])
            else:
                if self.L=='it':
                
                    quota_min_strutt = "Non inserita su GIS"
                    quota_max_strutt = "Non inserita su GIS"
                elif self.L == 'de':
                    quota_min_strutt = "Nicht im GIS einbinden "
                    quota_max_strutt = "Nicht im GIS einbinden "
                else :
                    quota_min_strutt = "Not inserted in GIS "
                    quota_max_strutt = "Not inserted in GIS  "

            data_list.append([
                str(self.DATA_LIST[i].sito.replace('_',' ')),  # 1 - Sito
                str(self.DATA_LIST[i].sigla_struttura),  # 2 -  sigla struttura
                int(self.DATA_LIST[i].numero_struttura),  # 3 - numero struttura
                str(self.DATA_LIST[i].categoria_struttura),  # 4 - categoria
                str(self.DATA_LIST[i].tipologia_struttura),  # 5 - tipologia
                str(self.DATA_LIST[i].definizione_struttura),  # 6 - definizione
                str(self.DATA_LIST[i].descrizione),  # 7 - descrizione
                str(self.DATA_LIST[i].interpretazione),  # 7 - iintepretazione
                str(self.DATA_LIST[i].periodo_iniziale),  # 8 - periodo iniziale
                str(self.DATA_LIST[i].fase_iniziale),  # 9 - fase iniziale
                str(self.DATA_LIST[i].periodo_finale),  # 10 - periodo finale
                str(self.DATA_LIST[i].fase_finale),  # 11 - fase finale
                str(self.DATA_LIST[i].datazione_estesa),  # 12 - datazione estesa
                str(self.DATA_LIST[i].materiali_impiegati),  # 13 - materiali impiegati
                str(self.DATA_LIST[i].elementi_strutturali),  # 14 - elementi strutturali
                str(self.DATA_LIST[i].rapporti_struttura),  # 15 - rapporti struttura
                str(self.DATA_LIST[i].misure_struttura),  # 16 - misure
                quota_min_strutt,  # 17 - quota min
                quota_max_strutt  # 18 - quota max
            ])
        return data_list

    def on_toolButton_draw_strutture_toggled(self):
        if self.L=='it':    
            if self.toolButton_draw_strutture.isChecked():
                QMessageBox.warning(self, "Messaggio",
                                    "Modalita' GIS attiva. Da ora le tue ricerche verranno visualizzate sul GIS",
                                    QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.warning(self, "Messaggio",
                                    "Modalita' GIS disattivata. Da ora le tue ricerche non verranno piu' visualizzate sul GIS",
                                    QMessageBox.StandardButton.Ok)
        elif self.L=='de':  
            if self.toolButton_draw_strutture.isChecked():
                QMessageBox.warning(self, "Message",
                                    "Modalität' GIS aktiv. Von jetzt wird Deine Untersuchung mit Gis visualisiert",
                                    QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.warning(self, "Message",
                                    "Modalität' GIS deaktiviert. Von jetzt an wird deine Untersuchung nicht mehr mit Gis visualisiert",
                                    QMessageBox.StandardButton.Ok)
                                    
                                    
        else:   
            if self.toolButton_draw_strutture.isChecked():
                QMessageBox.warning(self, "Message",
                                    "GIS mode active. From now on your searches will be displayed on the GIS",
                                    QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.warning(self, "Message",
                                    "GIS mode disabled. From now on, your searches will no longer be displayed on the GIS.",
                                    QMessageBox.StandardButton.Ok)                     
    def on_pushButton_draw_struttura_pressed(self):
        
        sing_layer = [self.DATA_LIST[self.REC_CORR]]
        self.pyQGIS.charge_structure_from_research(sing_layer)

    
    def on_pushButton_view_all_st_pressed(self):
        
        lista=[]
        conn = Connection()
        sito_set= conn.sito_set()
        sito_set_str = sito_set['sito_set']
        try:
            if bool (sito_set_str):
                search_dict = {
                    'sito': "'" + str(sito_set_str) + "'"}  # 1 - Sito
                u = Utility()
                search_dict = u.remove_empty_items_fr_dict(search_dict)
                res = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
                self.DATA_LIST = []
            for i in res:
                self.DATA_LIST.append(i)
        
        
            for e in self.DATA_LIST:
            
                sito_p = e.sito
                sigla_st = e.sigla_struttura
                n_st = e.numero_struttura
            
            
                self.pyQGIS.charge_vector_layers_all_st(sito_p, sigla_st,n_st)

        except Exception as e:
            pass

    def update_if(self, msg):
        rec_corr = self.REC_CORR
        if msg == QMessageBox.StandardButton.Ok:
            test = self.update_record()
            if test == 1:
                id_list = []
                for i in self.DATA_LIST:
                    id_list.append(getattr(i, self.ID_TABLE))
                self.DATA_LIST = []
                if self.SORT_STATUS == "n":
                    temp_data_list = self.DB_MANAGER.query_sort(id_list, [self.ID_TABLE], 'asc',
                                                                self.MAPPER_TABLE_CLASS,
                                                                self.ID_TABLE)  # self.DB_MANAGER.query_bool(self.SEARCH_DICT_TEMP, self.MAPPER_TABLE_CLASS) #
                else:
                    temp_data_list = self.DB_MANAGER.query_sort(id_list, self.SORT_ITEMS_CONVERTED, self.SORT_MODE,
                                                                self.MAPPER_TABLE_CLASS, self.ID_TABLE)
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

                # custom functions

    def charge_records(self):
        self.DATA_LIST = []

        if self.DB_SERVER == 'sqlite':
            for i in self.DB_MANAGER.query(self.MAPPER_TABLE_CLASS):
                self.DATA_LIST.append(i)
        else:
            id_list = []
            for i in self.DB_MANAGER.query(self.MAPPER_TABLE_CLASS):
                id_list.append(getattr(i, self.ID_TABLE))

            temp_data_list = self.DB_MANAGER.query_sort(id_list, [self.ID_TABLE], 'asc', self.MAPPER_TABLE_CLASS,
                                                        self.ID_TABLE)

            for i in temp_data_list:
                self.DATA_LIST.append(i)

    def setComboBoxEditable(self, f, n):
        """Set editable state for widgets - uses getattr instead of eval for security"""
        for fn in f:
            widget_name = fn.replace('self.' , '') if fn.startswith('self.' ) else fn
            widget = getattr(self, widget_name, None)
            if widget is not None:
                widget.setEditable(bool(n))

    def update_record(self):
        
        try:
            self.DB_MANAGER.update(self.MAPPER_TABLE_CLASS,
                                   self.ID_TABLE,
                                   [int(getattr(self.DATA_LIST[self.REC_CORR], self.ID_TABLE))],
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
                    pass
            if self.L=='it':
                QMessageBox.warning(self, "Messaggio",
                                    "Problema di encoding: sono stati inseriti accenti o caratteri non accettati dal database. Verrà fatta una copia dell'errore con i dati che puoi recuperare nella cartella pyarchinit_Report _Folder", QMessageBox.StandardButton.Ok)
            
            
            elif self.L=='de':
                QMessageBox.warning(self, "Message",
                                    "Encoding problem: accents or characters not accepted by the database were entered. A copy of the error will be made with the data you can retrieve in the pyarchinit_Report _Folder", QMessageBox.StandardButton.Ok) 
            else:
                QMessageBox.warning(self, "Message",
                                    "Kodierungsproblem: Es wurden Akzente oder Zeichen eingegeben, die von der Datenbank nicht akzeptiert werden. Es wird eine Kopie des Fehlers mit den Daten erstellt, die Sie im pyarchinit_Report _Ordner abrufen können", QMessageBox.StandardButton.Ok)
            return 0
