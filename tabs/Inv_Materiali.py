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

import math
import traceback
from datetime import date, datetime
import platform


import cv2
import time
import numpy as np
import urllib.parse
import pyvista as pv
import vtk

from pyvistaqt import QtInteractor
import functools
import sys
import subprocess

from qgis.PyQt.QtCore import Qt, QSize, QVariant, QDateTime, QTimer
from qgis.PyQt.QtGui import QIcon, QColor
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.uic import loadUiType
from qgis.core import QgsSettings, Qgis, QgsMessageLog
from qgis.gui import QgsMapCanvas
from collections import OrderedDict

# GPTWindow is imported lazily in sketchgpt to avoid PyMuPDF DLL conflicts on Windows
from ..modules.utility.VideoPlayerArtefact import VideoPlayerWindow
from ..modules.utility.pyarchinit_media_utility import *
from ..modules.db.pyarchinit_conn_strings import Connection
from ..modules.db.pyarchinit_db_manager import get_db_manager
from ..modules.db.concurrency_manager import ConcurrencyManager, RecordLockIndicator
from ..modules.db.pyarchinit_utility import Utility
from ..modules.utility.csv_writer import UnicodeWriter

from ..modules.utility.delegateComboBox import ComboBoxDelegate
from ..modules.utility.pyarchinit_error_check import Error_check
from ..modules.utility.pyarchinit_exp_Findssheet_pdf import generate_reperti_pdf
from ..modules.utility.pyarchinit_exp_Inventario_A5_pdf import generate_inventario_pdf_a5
from ..modules.gis.pyarchinit_pyqgis import Pyarchinit_pyqgis
from ..modules.utility.archaeological_data_mapping import ArchaeologicalDataMapper
from ..gui.imageViewer import ImageViewer
from ..gui.quantpanelmain import QuantPanelMain
from ..gui.sortpanelmain import SortPanelMain
from ..gui.pyarchinitConfigDialog import pyArchInitDialog_Config
from ..modules.utility.remote_image_loader import load_icon, get_image_path, initialize as init_remote_loader
MAIN_DIALOG_CLASS, _ = loadUiType(os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'Inv_Materiali.ui'))


class pyarchinit_Inventario_reperti(QDialog, MAIN_DIALOG_CLASS):
    L=QgsSettings().value("locale/userLocale", "it", type=str)[:2]
    if L=='it':
        MSG_BOX_TITLE = "PyArchInit - Scheda Materiali"
    elif L=='en':
        MSG_BOX_TITLE = "PyArchInit - Artefact form"
    elif L=='de':
        MSG_BOX_TITLE = "PyArchInit - Formular Arktefat "
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
    TABLE_NAME = 'inventario_materiali_table'
    MAPPER_TABLE_CLASS = "INVENTARIO_MATERIALI"
    NOME_SCHEDA = "Scheda Inventario Materiali"
    ID_TABLE = "id_invmat"
    if L =='it':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Sito": "sito",
            "Numero inventario": "numero_inventario",
            "Tipo reperto": "tipo_reperto",
            "Classe materiale": "criterio_schedatura",
            "Definizione": "definizione",
            "Descrizione": "descrizione",
            "Area": "area",
            "US": "us",
            "Lavato": "lavato",
            "Numero cassa": "nr_cassa",
            "Luogo di conservazione": "luogo_conservazione",
            "Stato conservazione": "stato_conservazione",
            "Datazione reperto": "datazione_reperto",
            "Forme minime": 'forme_minime',
            "Forme massime": 'forme_massime',
            "Totale frammenti": 'totale_frammenti',
            "Corpo ceramico": 'corpo_ceramico',
            "Rivestimento": 'rivestimento',
            "Diametro orlo": 'diametro_orlo',
            "Peso": 'peso',
            "Tipo": 'tipo',
            "Valore E.v.e. orlo": 'eve_orlo',
            "Repertato": 'repertato',
            "Diagnostico": 'diagnostico',
            "RA":'n_reperto',
            "Tipo contenitore":'tipo_contenitore',
            "Struttura":'struttura',
            "Anno":'years'
        }
        QUANT_ITEMS = ['Tipo reperto',
                       'Classe materiale',
                       'Definizione',
                       'Corpo ceramico',
                       'Rivestimento',
                       "Tipo",
                       "Datazione reperto",
                       "RA",
                       "Anno"]

        SORT_ITEMS = [
            ID_TABLE,
            "Sito",
            "Numero inventario",
            "Tipo reperto",
            "Criterio schedatura",
            "Definizione",
            "Descrizione",
            "Area",
            "US",
            "Lavato",
            "Numero cassa",
            "Luogo di conservazione"
            "Stato conservazione",
            "Datazione reperto",
            "Forme minime",
            "Forme massime",
            "Totale frammenti",
            "Corpo ceramico",
            "Rivestimento",
            "Diametro orlo",
            "Peso",
            "Tipo",
            "Valore E.v.e. orlo",
            "Repertato",
            "Diagnostico",
            "RA",
            "Tipo contenitore",
            "Struttura",
            "Anno"
        ]
    if L =='de':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Ausgrabungsstätte": "sito",
            "Inventar nummer": "numero_inventario",
            "Art des Artefakts": "tipo_reperto",
            "Materialklasse": "criterio_schedatura",
            "Definition": "definizione",
            "Beschreibung": "descrizione",
            "Areal": "area",
            "SE": "us",
            "Gewaschen": "lavato",
            "Box": "nr_cassa",
            "Ort der Erhaltung": "luogo_conservazione",
            "Erhaltungsstatus": "stato_conservazione",
            "Datierung - Artefakt": "datazione_reperto",
            "Minimale Anzahl der Gefäßindividuen": 'forme_minime',
            "Maximale Anzahl der Gefäßindividuen": 'forme_massime',
            "Fragmente insgesamt": 'totale_frammenti',
            "Keramikkörper": 'corpo_ceramico',
            "Oberflächenbehandlung": 'rivestimento',
            "Rand-Durchmesser": 'diametro_orlo',
            "Gewicht": 'peso',
            "Typ": 'tipo',
            "E.V.E. edge": 'eve_orlo',
            "Abgerufen": 'repertato',
            "Diagnose": 'diagnostico',
            "RA":'n_reperto',
            "Behältertyp":'tipo_contenitore',
            "Strukturen":'struttura',
            "Year":'years'
        }
        QUANT_ITEMS = ['Art des Artefakts',
                       'Materialklasse',
                       'Definition',
                       'Keramikkörper',
                       'Oberflächenbehandlung',
                       'Typ',
                       'Datierung - Artefakt',
                       'RA',
                       'Year']

        SORT_ITEMS = [
            ID_TABLE,
            "Ausgrabungsstätte",
            "Inventar nummer",
            "Art des Artefakts",
            "Materialklasse",
            "Definition",
            "Beschreibung",
            "Areal",
            "SE",
            "Gewaschen",
            "Box",
            "Ort der Erhaltung",
            "Erhaltungsstatus",
            "Datierung - Artefakt",
            "Minimale Anzahl der Gefäßindividuen",
            "Maximale Anzahl der Gefäßindividuen",
            "Fragmente insgesamt",
            "Keramikkörper",
            "Oberflächenbehandlung",
            "Rand-Durchmesser",
            "Gewicht",
            "Typ",
            "E.V.E. edge",
            "Abgerufen",
            "Diagnose",
            "RA",
            "Behältertyp",
            "Strukturen",
            "Year"
        ]
    if L =='en':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Site": "sito",
            "Inventary nr": "numero_inventario",
            "Artefact type": "tipo_reperto",
            "Material class": "criterio_schedatura",
            "Definition": "definizione",
            "Description": "descrizione",
            "Area": "area",
            "SU": "us",
            "Washed": "lavato",
            "Box": "nr_cassa",
            "Place of conservation": "luogo_conservazione",
            "Status of conservation": "stato_conservazione",
            "Artefact period": "datazione_reperto",
            "Min shape": 'forme_minime',
            "Max shape": 'forme_massime',
            "Total fragments": 'totale_frammenti',
            "Body sherds": 'corpo_ceramico',
            "Coating ": 'rivestimento',
            "Rim diameter": 'diametro_orlo',
            "Weight": 'peso',
            "Type": 'tipo',
            "Value E.v.e. rim": 'eve_orlo',
            "Reperted": 'repertato',
            "Diagnostic": 'diagnostico',
            "RA":'n_reperto',
            "Type of container":'tipo_contenitore',
            "Structure":'struttura',
            "Year":'years'
        }
        QUANT_ITEMS = ['Artefact type',
                       'Material class',
                       'Definition',
                       'Body sherds',
                       'Coating',
                       'Type',
                       'Artefact period',
                       'RA',
                       'Year']

        SORT_ITEMS = [
            ID_TABLE,
            "Site",
            "Inventary nr",
            "Artefact type",
            "Material class",
            "Definition",
            "Description",
            "Area",
            "SU",
            "Washed",
            "Box",
            "Place of conservation",
            "Status of conservation",
            "Artefact period",
            "Min shape",
            "Max shape",
            "Total fragments",
            "Body sherds",
            "Coating ",
            "Rim diameter",
            "Weight",
            "Type",
            "Value E.v.e. rim",
            "Reperted",
            "Diagnostic",
            "RA",
            "Type of container",
            "Structure",
            "Year"
        ]   
    TABLE_FIELDS = [
        "sito",
        "numero_inventario",
        "tipo_reperto",
        "criterio_schedatura",
        "definizione",
        "descrizione",
        "area",
        "us",
        "lavato",
        "nr_cassa",
        "luogo_conservazione",
        "stato_conservazione",
        "datazione_reperto",
        "elementi_reperto",
        "misurazioni",
        "rif_biblio",
        "tecnologie",
        "forme_minime",
        "forme_massime",
        "totale_frammenti",
        "corpo_ceramico",
        "rivestimento",
        'diametro_orlo',
        'peso',
        'tipo',
        'eve_orlo',
        'repertato',
        'diagnostico',
        'n_reperto',
        'tipo_contenitore',
        'struttura',
        'years'
    ]

    TABLE_FIELDS_UPDATE = [
        "tipo_reperto",
        "criterio_schedatura",
        "definizione",
        "descrizione",
        "area",
        "us",
        "lavato",
        "nr_cassa",
        "luogo_conservazione",
        "stato_conservazione",
        "datazione_reperto",
        "elementi_reperto",
        "misurazioni",
        "rif_biblio",
        "tecnologie",
        "forme_minime",
        "forme_massime",
        "totale_frammenti",
        "corpo_ceramico",
        "rivestimento",
        'diametro_orlo',
        'peso',
        'tipo',
        'eve_orlo',
        'repertato',
        'diagnostico',
        'n_reperto',
        'tipo_contenitore',
        'struttura',
        'year'
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

    SEARCH_DICT_TEMP = ""

    HOME = os.environ['PYARCHINIT_HOME']
    PDFFOLDER = '{}{}{}'.format(HOME, os.sep, "pyarchinit_PDF_folder")
    QUANT_PATH = '{}{}{}'.format(HOME, os.sep, "pyarchinit_Quantificazioni_folder")

    DB_SERVER = 'not defined'

    def __init__(self, iface):
        super().__init__()


        self.iface = iface
        self.setupUi(self)
        self.mapper = None
        self.video_player=None
        self.mDockWidget_export.setHidden(True)
        self.mDockWidget.setHidden(True)
        self.pyQGIS = Pyarchinit_pyqgis(iface)
        self.currentLayerId = None
        self.setAcceptDrops(True)
        self.iconListWidget.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.delegateElRinv = None
        self.delegateTipoMis = None
        self.delegateUnitaMis = None
        self.delegateTipoTec = None
        self.delegateTipoQu = None
        self.delegateUnMis = None
        # Dizionario per memorizzare le immagini in cache
        self.image_cache = OrderedDict()

        # Numero massimo di elementi nella cache
        self.cache_limit = 100
        try:
            self.on_pushButton_connect_pressed()
        except Exception as e:
            QMessageBox.warning(self, "Connection system", str(e), QMessageBox.StandardButton.Ok)
        #self.setnone()
        #self.fill_fields()  # Removed - method doesn't exist, called via set_sito()
        #self.lineEdit_num_inv.setText('')
        #self.lineEdit_num_inv.textChanged.connect(self.update)
        self.lineEdit_num_inv.textChanged.connect(self.charge_struttura)
        self.set_sito()
        self.msg_sito()
        #self.comboBox_repertato.currentTextChanged.connect(self.numero_reperto)
        self.pushButton_sketchgpt.clicked.connect(self.sketchgpt)
        self.toolButton_pdfpath.clicked.connect(self.setPathpdf)
        self.pushButton_esporta_a5.clicked.connect(self.on_pushButton_esporta_a5_pressed)
        self.customize_gui()
        #self.loadMapPreview()
        #self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        # Initialize remote image loader
        init_remote_loader()

    def get_images_for_entities(self, entity_ids, log_signal=None):
        def log(message, level="info"):
            if log_signal:
                log_signal.emit(message, level)
        """Recupera le immagini dalla tabella mediaentity in base agli ID forniti."""
        log(f"Called get_images_for_entities with entity_ids: {entity_ids}")

        if not entity_ids:
            return []

        try:
            images = []
            conn = Connection()
            thumb_resize = conn.thumb_resize()
            thumb_resize_str = thumb_resize['thumb_resize']

            for entity_id in entity_ids:
                log(f"Called id table: {self.ID_TABLE}")
                # Usa la stessa logica di loadMediaPreview
                rec_list = self.ID_TABLE + " = " + str(entity_id)
                log(f"Called rec list: {rec_list}")
                # Usa la stessa logica di loadMediaPreview
                search_dict = {
                    'id_entity': "'" + str(entity_id) + "'",
                    'entity_type': "'REPERTO'"
                }

                record_us_list = self.DB_MANAGER.query_bool(search_dict, 'MEDIATOENTITY')
                log(f"Found {len(record_us_list)} records for entity_id {entity_id}")  # Debug log

                for media_record in record_us_list:
                    search_dict = {'id_media': "'" + str(media_record.id_media) + "'"}
                    u = Utility()
                    search_dict = u.remove_empty_items_fr_dict(search_dict)
                    mediathumb_data = self.DB_MANAGER.query_bool(search_dict, "MEDIA_THUMB")
                    log(f"Found {len(mediathumb_data)} thumbs for media_id {media_record.id_media}")  # Debug log

                    if mediathumb_data:
                        thumb_path = str(mediathumb_data[0].path_resize)
                        images.append({
                            'id': entity_id,
                            'url': thumb_resize_str + thumb_path,
                            'caption': media_record.media_name
                        })
                        log(f"Added image with path: {thumb_resize_str + thumb_path}")  # Debug log

            log(f"Returning total of {len(images)} images")  # Debug log
            return images

        except Exception as e:
            log(f"Error in get_images_for_entities: {str(e)}")
            traceback.print_exc()  # Questo mostrerà lo stack trace completo
            return []


    def setnone(self):
        if self.lineEdit_tipo_contenitore.text=='None' or None:
            self.lineEdit_tipo_contenitore.clear()
            self.lineEdit_tipo_contenitore.setText('')
            self.lineEdit_tipo_contenitore.update()
        if self.lineEdit_n_reperto.text()=='None' or None or 'NULL'or 'Null':
            self.lineEdit_n_reperto.clear()
            self.lineEdit_n_reperto.setText('')
            self.lineEdit_n_reperto.update()
        if self.comboBox_struttura.currentText=='None' or None:
            self.comboBox_struttura.clear()
            self.comboBox_struttura.setEditText('')
            self.comboBox_struttura.update()
        if self.lineEditFormeMax.text=='None' or None:
            self.lineEditFormeMax.clear()
            self.lineEditFormeMax.setText('')
            self.lineEditFormeMax.update()
        if self.lineEditFormeMin.text=='None' or None:
            self.lineEditFormeMin.clear()
            self.lineEditFormeMin.setText('')
            self.lineEditFormeMin.update()
        if self.lineEditTotFram.text=='None' or None:
            self.lineEditTotFram.clear()
            self.lineEditTotFram.setText('')
            self.lineEditTotFram.update()
        if self.lineEdit_nr_cassa.text=='None' or None:
            self.lineEdit_nr_cassa.clear()
            self.lineEdit_nr_cassa.setText('')
            self.lineEdit_nr_cassa.update()
    def on_pushButtonQuant_pressed(self):
        dlg = QuantPanelMain(self)
        dlg.insertItems(self.QUANT_ITEMS)
        dlg.exec()

        dataset = []

        parameter1 = dlg.TYPE_QUANT
        parameters2 = dlg.ITEMS
        #QMessageBox.warning(self, "Test Parametri Quant", str(parameters2),  QMessageBox.Ok)

        contatore = 0
        # tipi di quantificazione
        ##per forme minime
        if self.L=='it':
            if parameter1 == 'Forme minime':
                for i in range(len(self.DATA_LIST)):
                    temp_dataset = ()
                    try:
                        temp_dataset = (self.parameter_quant_creator(parameters2, i), int(self.DATA_LIST[i].forme_minime))

                        contatore += int(self.DATA_LIST[i].forme_minime)  # conteggio totale

                        dataset.append(temp_dataset)
                    except:
                        pass

                        # QMessageBox.warning(self, "Totale", str(contatore),  QMessageBox.Ok)
                if bool(dataset):
                    dataset_sum = self.UTILITY.sum_list_of_tuples_for_value(dataset)
                    csv_dataset = []
                    for sing_tup in dataset_sum:
                        sing_list = [sing_tup[0], str(sing_tup[1])]
                        csv_dataset.append(sing_list)

                    filename = ('%s%squant_forme_minime.csv') % (self.QUANT_PATH, os.sep)
                    #QMessageBox.warning(self, "Esportazione", str(filename), QMessageBox.Ok)
                    with  open(filename, 'wb') as f:
                        Uw = UnicodeWriter(f)
                        Uw.writerows(csv_dataset)
                        f.close()

                    self.plot_chart(dataset_sum, 'Grafico per Forme minime', 'Nr. Forme')
                    #self.torta_chart(dataset_sum, 'Grafico per Forme minime', 'Nr. Forme')
                    #self.matrice_chart(dataset_sum, 'Grafico per Forme minime', 'Nr. Forme')
                else:
                    QMessageBox.warning(self, "Attenzione", "Non ci sono dati da rappresentare", QMessageBox.StandardButton.Ok)

            elif parameter1 == 'Frammenti':
                for i in range(len(self.DATA_LIST)):
                    #temp_dataset = ()

                    temp_dataset = (self.parameter_quant_creator(parameters2, i), int(self.DATA_LIST[i].totale_frammenti))

                    contatore += int(self.DATA_LIST[i].totale_frammenti)  # conteggio totale

                    dataset.append(temp_dataset)

                    # QMessageBox.warning(self, "Totale", str(contatore),  QMessageBox.Ok)
                if bool(dataset):
                    dataset_sum = self.UTILITY.sum_list_of_tuples_for_value(dataset)

                    # csv export block
                    csv_dataset = []
                    for sing_tup in dataset_sum:
                        sing_list = [sing_tup[0], str(sing_tup[1])]
                        csv_dataset.append(sing_list)

                    filename = ('%s%squant_frammenti.csv') % (self.QUANT_PATH, os.sep)
                    f = open(filename, 'wb')
                    Uw = UnicodeWriter(f)
                    Uw.writerows(csv_dataset)
                    f.close()
                    # QMessageBox.warning(self, "Esportazione", "Esportazione del file "+ str(filename) + "avvenuta con successo. I dati si trovano nella cartella pyarchinit_Quantificazioni_folder sotto al vostro Utente", MessageBox.Ok)


                    self.plot_chart(dataset_sum, 'Grafico per Frammenti', 'Nr. Frammenti')
                else:
                    QMessageBox.warning(self, "Attenzione", "Non ci sono dati da rappresentare!!", QMessageBox.StandardButton.Ok)
        elif self.L=='de':
            if parameter1 == 'Minimale Anzahl der Gefäßindividuen':
                for i in range(len(self.DATA_LIST)):
                    temp_dataset = ()
                    try:
                        temp_dataset = (self.parameter_quant_creator(parameters2, i), int(self.DATA_LIST[i].forme_minime))

                        contatore += int(self.DATA_LIST[i].forme_minime)  # conteggio totale

                        dataset.append(temp_dataset)
                    except:
                        pass

                        # QMessageBox.warning(self, "Totale", str(contatore),  QMessageBox.Ok)
                if bool(dataset):
                    dataset_sum = self.UTILITY.sum_list_of_tuples_for_value(dataset)
                    csv_dataset = []
                    for sing_tup in dataset_sum:
                        sing_list = [sing_tup[0], str(sing_tup[1])]
                        csv_dataset.append(sing_list)

                    filename = ('%s%squant_Minimale_Anzahl_der_Gefäßindividuen.csv') % (self.QUANT_PATH, os.sep)
                    QMessageBox.warning(self, "Exportation", str(filename), QMessageBox.StandardButton.Ok)
                    with open(filename, 'wb') as f:
                        Uw = UnicodeWriter(f)
                        Uw.writerows(csv_dataset)
                        f.close()

                    self.plot_chart(dataset_sum, 'Diagramm für Minimale Anzahl der Gefäßindividuen', 'Nr. Anzahl')
                else:
                    QMessageBox.warning(self, "Achtung", "Es gibt keine Daten, die dargestellt werden können", QMessageBox.StandardButton.Ok)

            elif parameter1 == 'Fragmente':
                for i in range(len(self.DATA_LIST)):
                    temp_dataset = ()

                    temp_dataset = (self.parameter_quant_creator(parameters2, i), int(self.DATA_LIST[i].totale_frammenti))

                    contatore += int(self.DATA_LIST[i].totale_frammenti)  # conteggio totale

                    dataset.append(temp_dataset)

                    # QMessageBox.warning(self, "Totale", str(contatore),  QMessageBox.Ok)
                if bool(dataset):
                    dataset_sum = self.UTILITY.sum_list_of_tuples_for_value(dataset)

                    # csv export block
                    csv_dataset = []
                    for sing_tup in dataset_sum:
                        sing_list = [sing_tup[0], str(sing_tup[1])]
                        csv_dataset.append(sing_list)

                    filename = ('%s%squant_Fragmente.csv') % (self.QUANT_PATH, os.sep)
                    with open(filename, 'wb') as f:
                        Uw = UnicodeWriter(f)
                        Uw.writerows(csv_dataset)
                        f.close()
                    # QMessageBox.warning(self, "Esportazione", "Esportazione del file "+ str(filename) + "avvenuta con successo. I dati si trovano nella cartella pyarchinit_Quantificazioni_folder sotto al vostro Utente", MessageBox.Ok)


                    self.plot_chart(dataset_sum, 'Fragmentdiagramm', 'Nr. Fragmente')
                else:
                    QMessageBox.warning(self, "Achtung", "Es gibt keine Daten, die dargestellt werden können", QMessageBox.StandardButton.Ok)  
        else:
            if parameter1 == 'Min shape':
                for i in range(len(self.DATA_LIST)):
                    temp_dataset = ()
                    try:
                        temp_dataset = (self.parameter_quant_creator(parameters2, i), int(self.DATA_LIST[i].forme_minime))

                        contatore += int(self.DATA_LIST[i].forme_minime)  # conteggio totale

                        dataset.append(temp_dataset)
                    except:
                        pass

                        # QMessageBox.warning(self, "Totale", str(contatore),  QMessageBox.Ok)
                if bool(dataset):
                    dataset_sum = self.UTILITY.sum_list_of_tuples_for_value(dataset)
                    csv_dataset = []
                    for sing_tup in dataset_sum:
                        sing_list = [sing_tup[0], str(sing_tup[1])]
                        csv_dataset.append(sing_list)

                    filename = ('%s%squant_min_shape.csv') % (self.QUANT_PATH, os.sep)
                    QMessageBox.warning(self, "Exportation", str(filename), QMessageBox.StandardButton.Ok)
                    with open(filename, 'wb') as f:
                        Uw = UnicodeWriter(f)
                        Uw.writerows(csv_dataset)
                        f.close()

                    self.plot_chart(dataset_sum, 'Graph for min shape', 'Nr. Shape')
                else:
                    QMessageBox.warning(self, "Warning", "There are no data to represent", QMessageBox.StandardButton.Ok)

            elif parameter1 == 'Fragments':
                for i in range(len(self.DATA_LIST)):
                    temp_dataset = ()

                    temp_dataset = (self.parameter_quant_creator(parameters2, i), int(self.DATA_LIST[i].totale_frammenti))

                    contatore += int(self.DATA_LIST[i].totale_frammenti)  # conteggio totale

                    dataset.append(temp_dataset)

                    # QMessageBox.warning(self, "Totale", str(contatore),  QMessageBox.Ok)
                if bool(dataset):
                    dataset_sum = self.UTILITY.sum_list_of_tuples_for_value(dataset)

                    # csv export block
                    csv_dataset = []
                    for sing_tup in dataset_sum:
                        sing_list = [sing_tup[0], str(sing_tup[1])]
                        csv_dataset.append(sing_list)

                    filename = ('%s%squant_fragments.csv') % (self.QUANT_PATH, os.sep)
                    f = open(filename, 'wb')
                    Uw = UnicodeWriter(f)
                    Uw.writerows(csv_dataset)
                    f.close()
                    # QMessageBox.warning(self, "Esportazione", "Esportazione del file "+ str(filename) + "avvenuta con successo. I dati si trovano nella cartella pyarchinit_Quantificazioni_folder sotto al vostro Utente", MessageBox.Ok)


                    self.plot_chart(dataset_sum, 'Graph for fragments', 'Nr. Fragments')
                else:
                    QMessageBox.warning(self, "Warning", "There are no data to represent", QMessageBox.StandardButton.Ok)              
        '''experimental disabled
        wind = QMessageBox.warning(self, "Attenzione", "Vuoi esportare le medie ponderate?",  QMessageBox.Ok|QMessageBox.Cancel)
        if wind == QMessageBox.Ok:
            conversion_dict = {"I sec. a.C." : (-99, 0),
                                                "II sec. a.C.": (-199, -100),
                                                "III sec. a.C.": (-299, -200),
                                                "IV sec. a.C.": (-399, -300),
                                                "V sec. a.C.": (-499, -400),
                                                "VI sec. a.C.": (-599, -500),
                                                "VII sec. a.C.": (-699, -600)}
            data = []
            for sing_rec in self.DATA_LIST:
                if sing_rec.tipo != "" and sing_rec.forme_minime != "" and sing_rec.datazione_reperto != "":
                    data.append([sing_rec.tipo, sing_rec.forme_minime, sing_rec.datazione_reperto])
                #data = [ ["morel 20", 50, "II sec. a.C."], ["morel 22",50, "I sec. a.C."]]

            CC = Cronology_convertion()

            #calcola il totale delle forme minime
            totale_forme_minime = CC.totale_forme_min(data)
            #print "totale_forme_minime: ", totale_forme_minime
            #restituisce una lista di liste con dentro forma e singoli intervalli parziali di tempo
            lista_forme_dataz = []

            for sing_rec in data:
                intervalli = CC.convert_data(sing_rec[2])
                lista_forme_dataz.append([sing_rec[0],intervalli])

            #print "lista_forme_dataz: ", lista_forme_dataz
            #crea la lista di tuple per avere il totale parziale di ogni forma
            lista_tuple_forma_valore = []
            for i in data:
                lista_tuple_forma_valore.append((i[0], i[1]))

            #ottiene la lista di liste con tutti i totali per forma
            totali_per_forma = CC.sum_list_of_tuples_for_value(lista_tuple_forma_valore)
            #print "totali_parziali_per_forma: ", totali_per_forma

            #ottiene la lista di liste con le perc_parziali per forma
            perc_per_forma = []
            for i in totali_per_forma:
                perc = CC.calc_percent(i[1], totale_forme_minime)
                perc_per_forma.append([i[0], perc])

            #print "perc per forma: ", perc_per_forma

            #lista valore, crono_iniz, cron_fin_globale
            lista_intervalli_globali = []
            valore_temp = ""
            for i in lista_forme_dataz:
                if i[0] != valore_temp:
                    intervallo_globale = CC.media_ponderata_perc_intervallo(lista_forme_dataz, i[0])
                    lista_intervalli_globali.append([i[0], intervallo_globale])
                valore_temp = i[0]

            #print "lista_intervalli_globali", lista_intervalli_globali

            #lista valore / Intervallo numerico
            intervallo_numerico = CC.intervallo_numerico(lista_intervalli_globali)
            #print "intervallo_numerico", intervallo_numerico

            #media_ponderata_singoli_valori
            lista_valori_medie = []
            for sing_perc in perc_per_forma:
                for sing_int in intervallo_numerico:
                    if sing_int[0] ==  sing_perc[0]:
                        valore_medio = float(sing_perc[1]) / float(sing_int[1])
                        lista_valori_medie.append([ sing_perc[0], valore_medio])

            #print "lista_valori_medie", lista_valori_medie
            #assegna valori ai singoli cinquatenni
            ##print CC.check_value_parz_in_rif_value([-170, -150], [-500, -400])
            diz_medie_pond = {}
            for forma_parz in lista_valori_medie:
                valore_riferimento = forma_parz[0]
                for sing_int in lista_intervalli_globali:
            ##      print "sing_int", sing_int
                    if sing_int[0] == valore_riferimento:
                        for k,v in conversion_dict.items():
            ##              print sing_int[1][0], sing_int[1][1], v[0], v[1]
                            test = CC.check_value_parz_in_rif_value([sing_int[1][0], sing_int[1][1]], [v[0], v[1]])
                            if test == 1:
                                try:
            ##                      print k, forma_parz
                                    diz_medie_pond[k] =diz_medie_pond[k] + forma_parz[1]
                                except:
                                    diz_medie_pond[k] = forma_parz[1]

                        #csv export block
            csv_dataset = []
            for k,v in diz_medie_pond.items():
                sing_list = [k, str(v)]
                csv_dataset.append(sing_list)

            filename = ('%s%squant_medie_pond.csv') % (self.QUANT_PATH, os.sep)
            with  open(filename, 'wb') as f:
                Uw = UnicodeWriter(f)
                Uw.writerows(csv_dataset)
                f.close()
            '''

    def parameter_quant_creator(self, par_list, n_rec):
        self.parameter_list = par_list
        self.record_number = n_rec

        converted_parameters = []
        for par in self.parameter_list:
            converted_parameters.append(self.CONVERSION_DICT[par])

        parameter2 = ''
        for sing_par_conv in range(len(converted_parameters)):
            exec_str = ('str(self.DATA_LIST[%d].%s)') % (self.record_number, converted_parameters[sing_par_conv])
            paramentro = str(self.parameter_list[sing_par_conv])
            exec_str = ' -' + paramentro[:4] + ": " + eval(exec_str)
            parameter2 += exec_str
        return parameter2

    def plot_chart(self, d, t, yl):
        self.data_list = d
        x, values = [], []
        if isinstance(self.data_list, list):
            teams, values = zip(*self.data_list)
            x = list(range(len(teams)))
        self.widget.canvas.ax.clear()
        bars = self.widget.canvas.ax.bar(x, height=values, width=0.5, align='center', alpha=0.4, picker=5)
        self.widget.canvas.ax.set_title(t)
        self.widget.canvas.ax.set_ylabel(yl)
        l = ['""' for _ in teams]
        for bar, team in zip(bars, teams):
            val = int(bar.get_height())
            x_pos = bar.get_x() + 0.25
            label = f"{team} - {val}"
            y_pos = 0.1
            self.widget.canvas.ax.tick_params(axis='x', labelsize=8)
            self.widget.canvas.ax.text(x_pos, y_pos, label, zorder=0, ha='center', va='bottom', size='x-small', rotation=90)
        self.widget.canvas.draw()


    def torta_chart(self, d, t, yl):
        self.data_list = d
        self.title = t
        self.ylabel = yl
        if isinstance(self.data_list, list):
            data_diz = {item[0]: item[1] for item in self.data_list}
            labels, values = zip(*data_diz.items())

            # Crea un nuovo grafico a torta
            self.widget.canvas.ax.clear()
            self.widget.canvas.ax.pie(values, labels=labels, autopct='%1.1f%%')
            self.widget.canvas.ax.axis('equal')
            self.widget.canvas.ax.set_title(self.title)
            self.widget.canvas.ax.set_ylabel(self.ylabel)
            self.widget.canvas.draw()

    def matrice_chart(self, d, t, yl):
        self.data_list = d
        self.title = t
        self.ylabel = yl
        if type(self.data_list) == list:
            data_diz = {}
            for item in self.data_list:
                data_diz[item[0]] = item[1]

        # Prepara i dati per la matrice di correlazione
        matrix_data = np.array(list(data_diz.values()))

        # Calcola la matrice di correlazione
        correlation_matrix = np.corrcoef(matrix_data)

        # Crea un nuovo grafico per la matrice di correlazione
        self.widget.canvas.ax.clear()
        cax = self.widget.canvas.ax.matshow(correlation_matrix, cmap='coolwarm')
        self.widget.canvas.ax.set_title(self.title)
        self.widget.canvas.ax.set_ylabel(self.ylabel)
        self.widget.canvas.fig.colorbar(cax)
        self.widget.canvas.draw()


    def on_pushButton_connect_pressed(self):
        # self.setComboBoxEditable(["self.comboBox_sito"],1)
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

            self.charge_records()
            # check if DB is empty
            if self.DATA_LIST:
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


    def loadMapPreview(self, mode = 0):
        if not hasattr(self, 'mapPreview'):
            return

        if mode == 0:
            """ if has geometry column load to map canvas """
            try:
                if not self.DATA_LIST or self.REC_CORR >= len(self.DATA_LIST):
                    return

                # Get id directly without using eval
                if hasattr(self.DATA_LIST[int(self.REC_CORR)], self.ID_TABLE):
                    id_val = getattr(self.DATA_LIST[int(self.REC_CORR)], self.ID_TABLE)
                    gidstr = self.ID_TABLE + " = " + str(id_val)
                    layerToSet = self.pyQGIS.loadMapPreviewReperti(gidstr)
                    #QMessageBox.warning(self, "layer to set", '\n'.join([l.name() for l in layerToSet]), QMessageBox.Ok)
                    self.mapPreview.setLayers(layerToSet)
                    self.mapPreview.zoomToFullExtent()
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e), QMessageBox.StandardButton.Ok)
        elif mode == 1:
            self.mapPreview.setLayers([])
            self.mapPreview.zoomToFullExtent()
    def customize_gui(self):

        l = QgsSettings().value("locale/userLocale", QVariant)
        lang = ""
        for key, values in self.LANG.items():
            if values.__contains__(l):
                lang = str(key)
        lang = "'" + lang + "'"

        # Set up area combobox
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'inventario_materiali_table' + "'",
            'tipologia_sigla': "'" + '3.11' + "'"
        }

        area_vl = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        valuesArea = []

        for i in range(len(area_vl)):
            valuesArea.append(area_vl[i].sigla_estesa)

        valuesArea.sort()
        self.comboBox_area.addItems(valuesArea)

        # media prevew system

        #self.iconListWidget.setFrameShape(QFrame.StyledPanel)
        #self.iconListWidget.setFrameShadow(QFrame.Sunken)
        self.iconListWidget.setLineWidth(2)
        self.iconListWidget.setMidLineWidth(2)
        #self.iconListWidget.setProperty("showDropIndicator", False)
        self.iconListWidget.setIconSize(QSize(150, 150))
        #self.iconListWidget.setMovement(QListView.Snap)
        #self.iconListWidget.setResizeMode(QListView.Adjust)
        #self.iconListWidget.setLayoutMode(QListView.Batched)
        #self.iconListWidget.setGridSize(QSize(160, 160))
        #self.iconListWidget.setViewMode(QListView.IconMode)
        #self.iconListWidget.setUniformItemSizes(True)
        #self.iconListWidget.setBatchSize(1000)
        #self.iconListWidget.setObjectName("iconListWidget")
        #self.iconListWidget.SelectionMode()
        #self.iconListWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.iconListWidget.itemDoubleClicked.connect(self.openWide_image)

        # Crea un nuovo widget che conterrà il map canvas
        canvas_widget = QWidget()

        # Crea un layout verticale per il widget
        canvas_layout = QVBoxLayout(canvas_widget)


        # Aggiungi il map canvas al layout

        self.mapPreview = QgsMapCanvas(canvas_widget)
        canvas_layout.addWidget(self.mapPreview)
        #self.mapPreview.setCanvasColor(QColor(225, 225, 225))
        self.tabWidget.addTab(canvas_widget, "Map preview")

        if self.L=='it':
            valuesTE = ["frammento", "frammenti", "intero", "integro"]
            self.delegateTE = ComboBoxDelegate()
            self.delegateTE.def_values(valuesTE)
            self.delegateTE.def_editable('False')
            self.tableWidget_elementi_reperto.setItemDelegateForColumn(1, self.delegateTE)
        elif self.L=='de':
            valuesTE = ["Fragment", "Fragmente", "ganz", "intakt"]
            self.delegateTE = ComboBoxDelegate()
            self.delegateTE.def_values(valuesTE)
            self.delegateTE.def_editable('False')
            self.tableWidget_elementi_reperto.setItemDelegateForColumn(1, self.delegateTE)
        else:
            valuesTE = ["fragment", "fragments" ,"whole", " intact"]
            self.delegateTE = ComboBoxDelegate()
            self.delegateTE.def_values(valuesTE)
            self.delegateTE.def_editable('False')
            self.tableWidget_elementi_reperto.setItemDelegateForColumn(1, self.delegateTE)


        # lista elementi reperto - elemento rinvenuto

        search_dict_a = {
            'lingua': lang,
            'nome_tabella': "'" + 'inventario_materiali_table' + "'",
            'tipologia_sigla': "'" + '3.4' + "'"
        }

        elRinv = self.DB_MANAGER.query_bool(search_dict_a, 'PYARCHINIT_THESAURUS_SIGLE')
        valuesElRinv = []

        for i_a in range(len(elRinv)):
            valuesElRinv.append(elRinv[i_a].sigla_estesa)

        valuesElRinv.sort()

        self.delegateElRinv = ComboBoxDelegate()
        self.delegateElRinv.def_values(valuesElRinv)
        self.delegateElRinv.def_editable('False')
        self.tableWidget_elementi_reperto.setItemDelegateForColumn(0, self.delegateElRinv)

        # lista misurazioni - tipo di misura

        search_dict_b = {
            'lingua': lang,
            'nome_tabella': "'" + 'inventario_materiali_table' + "'",
            'tipologia_sigla': "'" + '3.5' + "'"
        }

        elTipoMis = self.DB_MANAGER.query_bool(search_dict_b, 'PYARCHINIT_THESAURUS_SIGLE')
        valuestipomis = []

        for i_b in range(len(elTipoMis)):
            valuestipomis.append(elTipoMis[i_b].sigla_estesa)

        valuestipomis.sort()

        self.delegateTipoMis = ComboBoxDelegate()
        self.delegateTipoMis.def_values(valuestipomis)
        self.delegateTipoMis.def_editable('False')
        self.tableWidget_misurazioni.setItemDelegateForColumn(0, self.delegateTipoMis)

        # lista misurazioni - unita di misura

        search_dict_c = {
            'lingua': lang,
            'nome_tabella': "'" + 'inventario_materiali_table' + "'",
            'tipologia_sigla': "'" + '3.6' + "'"
        }

        elUnitaMis = self.DB_MANAGER.query_bool(search_dict_c, 'PYARCHINIT_THESAURUS_SIGLE')
        valuesunitamis = []

        for i_c in range(len(elUnitaMis)):
            valuesunitamis.append(elUnitaMis[i_c].sigla_estesa)

        valuesunitamis.sort()

        self.delegateUnitaMis = ComboBoxDelegate()
        self.delegateUnitaMis.def_values(valuesunitamis)
        self.delegateUnitaMis.def_editable('False')
        self.tableWidget_misurazioni.setItemDelegateForColumn(1, self.delegateUnitaMis)

        # lista tecnologie - tipo tecnologia

        search_dict_d = {
            'lingua': lang,
            'nome_tabella': "'" + 'inventario_materiali_table' + "'",
            'tipologia_sigla': "'" + '3.7' + "'"
        }

        elTipoTec = self.DB_MANAGER.query_bool(search_dict_d, 'PYARCHINIT_THESAURUS_SIGLE')
        valuestipotec = []

        for i_d in range(len(elTipoTec)):
            valuestipotec.append(elTipoTec[i_d].sigla_estesa)

        valuestipotec.sort()

        self.delegateTipoTec = ComboBoxDelegate()
        self.delegateTipoTec.def_values(valuestipotec)
        self.delegateTipoTec.def_editable('False')
        self.tableWidget_tecnologie.setItemDelegateForColumn(0, self.delegateTipoTec)

        # lista tecnologie - posizione

        search_dict_e = {
            'lingua': lang,
            'nome_tabella': "'" + 'inventario_materiali_table' + "'",
            'tipologia_sigla': "'" + '3.8' + "'"
        }

        elPosTec = self.DB_MANAGER.query_bool(search_dict_e, 'PYARCHINIT_THESAURUS_SIGLE')
        valuespostec = []

        for i_e in range(len(elPosTec)):
            valuespostec.append(elPosTec[i_e].sigla_estesa)

        valuespostec.sort()

        self.delegatePosTec = ComboBoxDelegate()
        self.delegatePosTec.def_values(valuespostec)
        self.delegatePosTec.def_editable('False')
        self.tableWidget_tecnologie.setItemDelegateForColumn(1, self.delegatePosTec)

        # lista tecnologie - tipo quantita

        search_dict_f = {
            'lingua': lang,
            'nome_tabella': "'" + 'inventario_materiali_table' + "'",
            'tipologia_sigla': "'" + '3.9' + "'"
        }

        elTipoQu = self.DB_MANAGER.query_bool(search_dict_f, 'PYARCHINIT_THESAURUS_SIGLE')
        valuestipoqu = []

        for i_f in range(len(elTipoQu)):
            valuestipoqu.append(elTipoQu[i_f].sigla_estesa)

        valuestipoqu.sort()

        self.delegateTipoQu = ComboBoxDelegate()
        self.delegateTipoQu.def_values(valuestipoqu)
        self.delegateTipoQu.def_editable('False')
        self.tableWidget_tecnologie.setItemDelegateForColumn(2, self.delegateTipoQu)

        # lista tecnologie - unita di misura

        search_dict_g = {
            'lingua': lang,
            'nome_tabella': "'" + 'inventario_materiali_table' + "'",
            'tipologia_sigla': "'" + '3.10' + "'"
        }

        elUnMis = self.DB_MANAGER.query_bool(search_dict_g, 'PYARCHINIT_THESAURUS_SIGLE')
        valueunmis = []

        for i_g in range(len(elUnMis)):
            valueunmis.append(elUnMis[i_g].sigla)

        valueunmis.sort()

        self.delegateUnMis = ComboBoxDelegate()
        self.delegateUnMis.def_values(valueunmis)
        self.delegateUnMis.def_editable('False')
        self.tableWidget_tecnologie.setItemDelegateForColumn(3, self.delegateUnMis)

        # Add filter button for Inventario
        self.setup_filter_button()

        # Setup Statistics Tab
        self.setup_statistics_tab()

    def setup_filter_button(self):
        """Setup the filter button for Inventario Materiali"""
        try:
            self.pushButton_filter_inv = QPushButton(self)
            if self.L == 'it':
                self.pushButton_filter_inv.setText("Filtra Record")
                self.pushButton_filter_inv.setToolTip(self.tr("Filtra i record per Nr. Inventario, Nr. Reperto o Anno"))
            elif self.L == 'de':
                self.pushButton_filter_inv.setText("Filter")
                self.pushButton_filter_inv.setToolTip(self.tr("Datensätze nach Inventarnr., Fundnr. oder Jahr filtern"))
            else:
                self.pushButton_filter_inv.setText("Filter Records")
                self.pushButton_filter_inv.setToolTip(self.tr("Filter records by Inventory Nr., Find Nr. or Year"))

            self.pushButton_filter_inv.setMinimumSize(QSize(80, 25))
            self.pushButton_filter_inv.setMaximumSize(QSize(120, 25))

            # Find pushButton_view_all_2 and insert filter button next to it
            if hasattr(self, 'pushButton_view_all_2'):
                parent_layout = self.pushButton_view_all_2.parent().layout()
                if parent_layout:
                    index = parent_layout.indexOf(self.pushButton_view_all_2)
                    if index >= 0:
                        parent_layout.insertWidget(index + 1, self.pushButton_filter_inv)
                    else:
                        parent_layout.addWidget(self.pushButton_filter_inv)
                else:
                    # Position next to pushButton_view_all_2
                    geo = self.pushButton_view_all_2.geometry()
                    self.pushButton_filter_inv.setGeometry(
                        geo.x() + geo.width() + 5, geo.y(),
                        100, geo.height()
                    )

            self.pushButton_filter_inv.clicked.connect(self.on_pushButton_filter_inv_pressed)

        except Exception as e:
            print(f"Error setting up filter button: {e}")

    def on_pushButton_filter_inv_pressed(self):
        """Open filter dialog for Inventario Materiali"""
        try:
            print(f"[InventarioFilter] Opening filter dialog...")
            print(f"[InventarioFilter] DB_MANAGER type: {type(self.DB_MANAGER)}")
            dialog = InventarioFilterDialog(self.DB_MANAGER, self)
            print(f"[InventarioFilter] Dialog created, showing...")
            if dialog.exec() == QDialog.DialogCode.Accepted:
                selected_ids = dialog.get_selected_ids()
                selected_year = dialog.get_selected_year()
                filter_type = dialog.get_filter_type()

                if selected_ids:
                    # Build search query based on filter type
                    self.filter_records_by_selection(selected_ids, selected_year, filter_type)
        except Exception as e:
            import traceback
            print(f"[InventarioFilter] Error in filter: {e}")
            print(f"[InventarioFilter] Traceback: {traceback.format_exc()}")
            QMessageBox.warning(self, "Error", f"Filter error: {str(e)}", QMessageBox.StandardButton.Ok)

    def filter_records_by_selection(self, selected_ids, selected_year, filter_type):
        """Filter records based on selected IDs and year"""
        try:
            # Build the filtered data list
            filtered_records = []

            for record in self.DB_MANAGER.query(self.MAPPER_TABLE_CLASS):
                match = False

                if filter_type == 'numero_inventario':
                    if record.numero_inventario is not None and record.numero_inventario in selected_ids:
                        match = True
                elif filter_type == 'n_reperto':
                    if record.n_reperto is not None and record.n_reperto in selected_ids:
                        match = True
                elif filter_type == 'years':
                    if record.years is not None and record.years in selected_ids:
                        match = True

                # Also filter by year if specified
                if match and selected_year is not None:
                    if record.years != selected_year:
                        match = False

                if match:
                    filtered_records.append(record)

            if filtered_records:
                self.DATA_LIST = filtered_records
                self.REC_TOT = len(self.DATA_LIST)
                self.REC_CORR = 0
                self.rec_num = 0
                self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
                self.fill_fields()

                if self.L == 'it':
                    msg = f"Trovati {self.REC_TOT} record filtrati"
                elif self.L == 'de':
                    msg = f"{self.REC_TOT} gefilterte Datensätze gefunden"
                else:
                    msg = f"Found {self.REC_TOT} filtered records"

                QMessageBox.information(self, "Filter", msg, QMessageBox.StandardButton.Ok)
            else:
                if self.L == 'it':
                    msg = "Nessun record trovato con i criteri di filtro"
                elif self.L == 'de':
                    msg = "Keine Datensätze mit den Filterkriterien gefunden"
                else:
                    msg = "No records found with filter criteria"
                QMessageBox.warning(self, "Filter", msg, QMessageBox.StandardButton.Ok)

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Filter error: {str(e)}", QMessageBox.StandardButton.Ok)

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
            except Exception as e:
                e_str = str(e)
                if e_str.__contains__("Integrity"):
                    msg = self.filename + ": Image already in the database"
                else:
                    msg = e
                # QMessageBox.warning(self, "Errore", "Warning 1 ! \n"+ str(msg),  QMessageBox.Ok)
                return 0
        except Exception as e:
            QMessageBox.warning(self, "Error", "Warning 2 ! \n" + str(e), QMessageBox.StandardButton.Ok)
            return 0

    def insert_record_mediathumb(self, media_max_num_id, mediatype, filename, filename_thumb, filetype, filepath_thumb,
                                 filepath_resize):
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
                # QMessageBox.warning(self, "Error", "warming 1 ! \n"+ str(msg),  QMessageBox.Ok)
                return 0
        except Exception as e:
            QMessageBox.warning(self, "Error", "Warning 2 ! \n" + str(e), QMessageBox.StandardButton.Ok)
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
            except Exception as e:
                e_str = str(e)
                if e_str.__contains__("Integrity"):
                    msg = self.ID_TABLE + " already present into the database"
                else:
                    msg = e
                QMessageBox.warning(self, "Error", "Warning 1 ! \n" + str(msg), QMessageBox.StandardButton.Ok)
                return 0
        except Exception as e:
            QMessageBox.warning(self, "Error", "Warning 2 ! \n" + str(e), QMessageBox.StandardButton.Ok)
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
                self.DB_MANAGER.max_num_id('MEDIATOENTITY', 'id_mediaToEntity') + 1,
                int(self.id_entity),  # 1 - id_entity
                str(self.entity_type),  # 2 - entity_type
                str(self.table_name),  # 3 - table_name
                int(self.id_media),  # 4 - us
                str(self.filepath),  # 5 - filepath
                str(self.media_name))
        except Exception as e:
            QMessageBox.warning(self, "Error", "Warning 2 ! \n" + str(e), QMessageBox.StandardButton.Ok)
            return 0

    def generate_reperti(self):
        # tags_list = self.table2dict('self.tableWidgetTags_US')
        record_rep_list = []
        sito = self.comboBox_sito.currentText()

        nv = self.lineEdit_num_inv.text()
        # for sing_tags in tags_list:
        search_dict = {'sito': "'" + str(sito) + "'",
                       'numero_inventario': "'" + str(nv) + "'"
                       }
        j = self.DB_MANAGER.query_bool(search_dict, 'INVENTARIO_MATERIALI')
        record_rep_list.append(j)
        # QMessageBox.information(self, 'search db', str(record_us_list))
        rep_list = []
        for r in record_rep_list:
            rep_list.append([r[0].id_invmat, 'REPERTO', 'inventario_materiali_table'])
        return rep_list

    def assignTags_reperti(self, item):

        rep_list = self.generate_reperti()
        # QMessageBox.information(self,'search db',str(us_list))
        if not rep_list:
            return

        for rep_data in rep_list:
            id_orig_item = item.text()  # return the name of original file
            search_dict = {'filename': "'" + str(id_orig_item) + "'"}
            media_data = self.DB_MANAGER.query_bool(search_dict, 'MEDIA')
            self.insert_mediaToEntity_rec(rep_data[0], rep_data[1], rep_data[2], media_data[0].id_media,
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

            # Check and insert record in the database
            idunique_image_check = self.db_search_check('MEDIA', 'filepath', filepath)

            try:
                if bool(idunique_image_check):

                    return
                else:
                    # mediatype = 'image'
                    self.insert_record_media(mediatype, filename, filetype, filepath)
                    MU = Media_utility()
                    MUR = Media_utility_resize()
                    MU_video = Video_utility()
                    MUR_video = Video_utility_resize()
                    media_max_num_id = self.DB_MANAGER.max_num_id('MEDIA', 'id_media')
                    thumb_path = conn.thumb_path()
                    thumb_path_str = thumb_path['thumb_path']
                    thumb_resize = conn.thumb_resize()
                    thumb_resize_str = thumb_resize['thumb_resize']
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

                self.assignTags_reperti(item)




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

    def on_pushButton_search_images_pressed(self):
        """Open the Image Search dialog with pre-filled filters for current Inventario Materiali record."""
        from .Image_search import pyarchinit_Image_Search

        # Get current record context
        sito = self.comboBox_sito.currentText() if hasattr(self, 'comboBox_sito') else ''
        numero_inv = self.lineEdit_num_inv.text() if hasattr(self, 'lineEdit_num_inv') else ''

        # Open Image Search dialog
        dialog = pyarchinit_Image_Search(self.iface, self)

        # Set pre-filled filters
        dialog.comboBox_entity_type.setCurrentText('Materiali')
        if sito:
            index = dialog.comboBox_sito.findText(sito)
            if index >= 0:
                dialog.comboBox_sito.setCurrentIndex(index)
            else:
                dialog.comboBox_sito.setCurrentText(sito)
        if numero_inv:
            dialog.lineEdit_inventario.setText(str(numero_inv))

        dialog.show()

    def on_pushButton_removetags_pressed(self):
        def r_id():
            sito = self.comboBox_sito.currentText()

            record_us_list=[]
            nv = self.lineEdit_num_inv.text()
            # for sing_tags in tags_list:
            search_dict = {'sito': "'" + str(sito) + "'",
                           'numero_inventario': "'" + str(nv) + "'"
                           }
            j = self.DB_MANAGER.query_bool(search_dict, 'INVENTARIO_MATERIALI')
            record_us_list.append(j)
            # QMessageBox.information(self, 'search db', str(record_us_list))
            us_list = []
            for r in record_us_list:
                a=r[0].id_invmat
            #QMessageBox.information(self,'ok',str(a))# QMessageBox.information(self, "Scheda US", str(us_list), QMessageBox.Ok)
            return a

        items_selected = self.iconListWidget.selectedItems()
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
                    # items_selected = self.iconListWidget.selectedItems()
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
                    # items_selected = self.iconListWidget.selectedItems()
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
                    # items_selected = self.iconListWidget.selectedItems()
                    for item in items_selected:
                        id_orig_item = item.text()  # return the name of original file

                        # s = self.iconListWidget.item(0, 0).text()
                        self.DB_MANAGER.remove_tags_from_db_sql_scheda(r_id(), id_orig_item)
                        row = self.iconListWidget.row(item)
                        self.iconListWidget.takeItem(row)  # remove the item from the list

                    QMessageBox.warning(self, "Info", "Tags removed")

    def on_pushButton_all_images_pressed(self):
        record_us_list = self.DB_MANAGER.query('MEDIA_THUMB')

        et = {'entity_type': "'REPERTO'"}
        ser = self.DB_MANAGER.query_bool(et, 'MEDIATOENTITY')
        # Verifica se record_us_list è vuota
        if not record_us_list and not ser:
            QMessageBox.information(self, "Informazione", "Non ci sono immagini da mostrare.")
            return  # Termina la funzione

        # Inizializza la QListWidget fuori dal ciclo
        self.new_list_widget = QListWidget()
        # ##self.new_list_widget.setFixedSize(200, 300)
        self.new_list_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)  # Permette selezioni multiple

        done_button = QPushButton("TAG")

        def update_done_button():
            if not self.new_list_widget.selectedItems():
                done_button.setHidden(True)
            else:
                done_button.setHidden(False)
                done_button.clicked.connect(self.on_done_selecting_all)

        self.new_list_widget.itemSelectionChanged.connect(
            update_done_button)  # Aggiungi un layout per le etichette dei numeri delle pagine
        self.pageLayout = QHBoxLayout()
        self.current_page_label = QLabel()  # Creiamo l'etichetta per la pagina corrente
        self.total_pages_label = QLabel()  # Creiamo l'etichetta per il totale delle pagine

        self.pageLayout.addWidget(self.current_page_label)  # Aggiungiamo l'etichetta della pagina corrente al layout
        self.pageLayout.addWidget(self.total_pages_label)  # Aggiungiamo l'etichetta del totale delle pagine al layout

        # Aggiungi un pulsante "Indietro"
        self.prevButton = QPushButton("<<")
        self.prevButton.clicked.connect(self.go_to_previous_page)
        self.pageLayout.addWidget(self.prevButton)

        # Aggiungi le etichette dei numeri delle pagine
        self.pageLabels = []
        for i in range(1, 6):
            label = QLabel(str(i))
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setMinimumWidth(30)
            label.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Sunken)
            label.setMargin(2)
            label.mousePressEvent = functools.partial(self.on_page_label_clicked, i)
            self.pageLabels.append(label)
            self.pageLayout.addWidget(label)

        # Aggiungi un pulsante "Avanti"
        self.nextButton = QPushButton(">>")
        self.nextButton.clicked.connect(self.go_to_next_page)
        self.pageLayout.addWidget(self.nextButton)

        layout = QVBoxLayout()
        # Crea un campo di input per la ricerca
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Cerca...poi schiaccia invio")
        self.current_filter_text = ""

        self.page_size = 10  # Numero di immagini per pagina
        self.current_page = 1  # Pagina corrente
        self.total_pages = 0  # Numero totale di pagine

        # Aggiungi il campo di ricerca al layout sopra la QListWidget
        layout.insertWidget(0, self.search_field)

        layout.addLayout(self.pageLayout)
        layout.addWidget(self.new_list_widget)
        layout.addWidget(done_button)

        # Imposta il fattore di estensione per i widget nel layout
        # Il primo parametro è l'indice del widget e il secondo parametro è il fattore di estensione
        # In questo caso, new_list_widget ha un indice di 0 e done_button ha un indice di 1
        layout.setStretchFactor(self.new_list_widget, 5)  # new_list_widget avrà 3 volte più spazio di done_button
        layout.setStretchFactor(done_button, 1)  # done_button avrà 1/3 dello spazio di new_list_widget

        # Imposta il layout sulla tua finestra o su un altro widget
        self.setLayout(layout)

        # Crea un nuovo widget per contenere la QListWidget e il pulsante, e applica il layout
        self.widget = QWidget()
        self.widget.setLayout(layout)
        self.widget.adjustSize()
        self.widget.show()

        self.load_images()

        # Connette il campo di ricerca a una funzione di filtraggio
        self.search_field.returnPressed.connect(self.filter_items)

    def load_images(self, filter_text=None):
        conn = Connection()
        thumb_path = conn.thumb_path()
        thumb_path_str = thumb_path['thumb_path']
        u = Utility()

        # Calcola l'offset per la pagina corrente
        # offset = (self.current_page - 1) * self.page_size

        # Ottieni tutti i record delle immagini
        all_images = self.DB_MANAGER.query('MEDIA_THUMB')

        # Ottieni tutte le immagini taggate
        tagged_images = self.DB_MANAGER.query('MEDIATOENTITY')

        # Ottieni gli id_media di tutte le immagini taggate
        tagged_ids = [i.id_media for i in tagged_images]

        # Filtra tutte le immagini per ottenere solo quelle non taggate
        untagged_images = [i for i in all_images if i.id_media not in tagged_ids]

        # Inizializza l'elenco delle immagini 'US' come un duplicato delle immagini non taggate
        us_images = untagged_images[:]

        if len(all_images) > 100:

            if filter_text:  # se il filtro è attivo
                filtered_images = [i for i in untagged_images if filter_text.lower() in i.media_filename.lower()]
            else:
                filtered_images = us_images
            # Calcola gli indici di inizio e fine per la pagina corrente
            start_index = (self.current_page - 1) * self.page_size
            end_index = start_index + self.page_size

            # Ottieni i record delle immagini per la pagina corrente
            self.record_us_list = filtered_images[start_index:end_index]
            # Pulisci la QListWidget prima di aggiungere le nuove immagini
            self.new_list_widget.clear()
            # Aggiungi l'intestazione alla QListWidget
            header_item = QListWidgetItem(
                "Le righe selezionate in giallo indicano immagini non taggate\n Da questo strumento solo le righe selezionate gialle posso essere taggate ")
            header_item.setBackground(QColor('lightgrey'))
            header_item.setFlags(header_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)  # rendi l'item non selezionabile
            self.new_list_widget.addItem(header_item)
            # Aggiungi le immagini alla QListWidget

            for i in self.record_us_list:
                search_dict = {'id_media': "'" + str(i.id_media) + "'"}
                u = Utility()
                search_dict = u.remove_empty_items_fr_dict(search_dict)
                mediathumb_data = self.DB_MANAGER.query_bool(search_dict, "MEDIA_THUMB")
                thumb_path = str(mediathumb_data[0].filepath)
                # Verifica se l'immagine è già in cache
                if thumb_path not in self.image_cache:
                    # Se non è in cache, carica l'immagine
                    icon = load_icon(get_image_path(thumb_path_str, thumb_path))

                    # Se la cache ha raggiunto il limite, rimuove l'elemento più vecchio
                    if len(self.image_cache) >= self.cache_limit:
                        self.image_cache.popitem(last=False)

                    # Aggiunge l'immagine alla cache
                    self.image_cache[thumb_path] = icon
                else:

                    icon = self.image_cache[thumb_path]

                self.image_cache.move_to_end(thumb_path)

                item = QListWidgetItem(str(i.media_filename))
                item.setData(Qt.ItemDataRole.UserRole, str(i.media_filename))
                icon = load_icon(get_image_path(thumb_path_str, thumb_path))
                item.setIcon(icon)

                item.setBackground(QColor("yellow"))

                self.new_list_widget.addItem(item)

        else:
            for image in all_images:
                # Crea un nuovo dizionario di ricerca per MEDIATOENTITY
                search_dict = {'id_media': "'" + str(image.id_media) + "'",
                               'entity_type': "'REPERTO'"}
                search_dict = u.remove_empty_items_fr_dict(search_dict)

                # Recupera l'elenco di 'US' associati all'immagine
                mediatoentity_data = self.DB_MANAGER.query_bool(search_dict, "MEDIATOENTITY")

                # Se l'immagine ha una o più 'US' associate, aggiungila all'elenco
                if mediatoentity_data:
                    us_images.append(image)

            # A questo punto, 'us_images' dovrebbe contenere tutte le immagini non taggate
            # e quelle taggate con almeno un 'US', senza duplicati.

            if filter_text:  # se il filtro è attivo
                filtered_images = [i for i in us_images if filter_text.lower() in i.media_filename.lower()]
            else:
                filtered_images = us_images

            # Calcola gli indici di inizio e fine per la pagina corrente
            start_index = (self.current_page - 1) * self.page_size
            end_index = start_index + self.page_size

            # Ottieni i record delle immagini per la pagina corrente
            self.record_us_list = filtered_images[start_index:end_index]

            # Pulisci la QListWidget prima di aggiungere le nuove immagini
            self.new_list_widget.clear()

            # Aggiungi l'intestazione alla QListWidget
            header_item = QListWidgetItem(
                "Le righe selezionate in giallo indicano immagini non taggate\n Da questo strumento solo le righe selezionate gialle posso essere taggate ")
            header_item.setBackground(QColor('lightgrey'))
            header_item.setFlags(header_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)  # rendi l'item non selezionabile
            self.new_list_widget.addItem(header_item)
            # Aggiungi le immagini alla QListWidget

            for i in self.record_us_list:
                search_dict = {'id_media': "'" + str(i.id_media) + "'"}
                u = Utility()
                search_dict = u.remove_empty_items_fr_dict(search_dict)
                mediathumb_data = self.DB_MANAGER.query_bool(search_dict, "MEDIA_THUMB")
                thumb_path = str(mediathumb_data[0].filepath)
                # Verifica se l'immagine è già in cache
                if thumb_path not in self.image_cache:
                    # Se non è in cache, carica l'immagine
                    icon = load_icon(get_image_path(thumb_path_str, thumb_path))

                    # Se la cache ha raggiunto il limite, rimuove l'elemento più vecchio
                    if len(self.image_cache) >= self.cache_limit:
                        self.image_cache.popitem(last=False)

                    # Aggiunge l'immagine alla cache
                    self.image_cache[thumb_path] = icon
                else:
                    # Se è in cache, utilizza l'icona dalla cache
                    icon = self.image_cache[thumb_path]

                    # Aggiorna l'ordine della cache spostando l'elemento utilizzato alla fine
                    self.image_cache.move_to_end(thumb_path)
                # Crea un nuovo dizionario di ricerca per MEDIATOENTITY
                search_dict = {'id_media': "'" + str(i.id_media) + "'",
                               'entity_type': "'REPERTO'"}
                search_dict = u.remove_empty_items_fr_dict(search_dict)
                # Recupera l'elenco di US associati all'immagine
                mediatoentity_data = self.DB_MANAGER.query_bool(search_dict, "MEDIATOENTITY")
                us_list = [str(g.id_entity) for g in
                           mediatoentity_data]  # Se 'entity_type' è 'US', aggiungi l'id_media a us_images
                # Rimuovi i duplicati dalla lista convertendola in un set e poi di nuovo in una lista
                # us_list = list(set(us_list))

                if us_list:
                    # us_list = [g.id_entity for g in mediatoentity_data if 'US' in g.entity_type]
                    item = QListWidgetItem(str(i.media_filename))
                    item.setData(Qt.ItemDataRole.UserRole, str(i.media_filename))
                    icon = load_icon(get_image_path(thumb_path_str, thumb_path))
                    item.setIcon(icon)

                    item.setBackground(QColor("white"))

                    # Inizializza una lista vuota per i nomi delle US
                    us_names = []

                    for us_id in us_list:
                        # Crea un nuovo dizionario di ricerca per l'US
                        search_dict_us = {'id_invmat': us_id}
                        search_dict_us = u.remove_empty_items_fr_dict(search_dict_us)

                        # Query the US table
                        us_data = self.DB_MANAGER.query_bool(search_dict_us, "INVENTARIO_MATERIALI")

                        # Se l'US esiste, aggiungi il suo nome alla lista
                        if us_data:
                            us_names.extend([str(us.numero_inventario) for us in us_data])

                    # Se ci sono dei nomi US, aggiungi questi all'elemento
                    if us_names:
                        item.setText(item.text() + " - Manufatto: " + ', '.join(us_names))
                    else:
                        pass  # oppure: item.setText(item.text() + " - US: Non trovato")
                # item.setText(item.text() + " - US: Non trovato")

                else:
                    # us_list = [g.id_entity for g in mediatoentity_data if 'US' in g.entity_type]
                    item = QListWidgetItem(str(i.media_filename))
                    item.setData(Qt.ItemDataRole.UserRole, str(i.media_filename))
                    icon = load_icon(get_image_path(thumb_path_str, thumb_path))
                    item.setIcon(icon)

                    item.setBackground(QColor("yellow"))

                    # Aggiungi l'elemento alla QListWidget
                # self.new_list_widget.clear()
                self.new_list_widget.addItem(item)

        # Calcola il numero totale di pagine

        self.total_pages = math.ceil(len(filtered_images) / self.page_size)

        # Aggiorna l'aspetto delle etichette dei numeri delle pagine
        self.update_page_labels()

    def update_page_labels(self):
        # Disabilita il pulsante "Indietro" se siamo alla prima pagina
        self.prevButton.setEnabled(self.current_page > 1)

        # Disabilita il pulsante "Avanti" se siamo all'ultima pagina
        self.nextButton.setEnabled(self.current_page < self.total_pages)

        # Aggiorna l'aspetto delle etichette dei numeri delle pagine
        for label in self.pageLabels:
            page_number = int(label.text())
            label.setEnabled(page_number != self.current_page)

        # Aggiorna l'etichetta della pagina corrente e del totale delle pagine
        self.current_page_label.setText(f"Pagina corrente: {self.current_page}")
        self.total_pages_label.setText(f"Totale pagine: {self.total_pages}")

    def go_to_previous_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_images(self.current_filter_text)

    def go_to_next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_images(self.current_filter_text)

    def on_page_label_clicked(self, page, _=None):
        if page != self.current_page:
            self.current_page = page
            self.load_images(self.current_filter_text)

    def filter_items(self):
        # Ottieni il testo corrente nel campo di ricerca
        self.current_filter_text = self.search_field.text().lower()
        self.load_images(self.current_filter_text)
    def on_done_selecting_all(self):

        def r_list():
            sito = self.comboBox_sito.currentText()
            #area = self.comboBox_area.currentText()
            nv = self.lineEdit_num_inv.text()
            record_us_list=[]
            #for sing_tags in selected_us:
            search_dict = {'sito': "'" + str(sito)+ "'",
                           #'area': "'" + str(area) + "'",
                           'numero_inventario': "'" + str(nv) + "'"
                           }
            j = self.DB_MANAGER.query_bool(search_dict, 'INVENTARIO_MATERIALI')
            record_us_list.append(j)
            us_list = []
            for r in record_us_list:
                us_list.append([r[0].id_invmat, 'REPERTO', 'inventario_materiali_table'])
            # QMessageBox.information(self, "Scheda US", str(us_list), QMessageBox.Ok)
            return us_list

        items_selected = self.new_list_widget.selectedItems()
        for item in items_selected:
            for us_data in r_list():
                id_orig_item = item.text()  # return the name of original file
                search_dict = {'filename': "'" + str(id_orig_item) + "'"}
                media_data = self.DB_MANAGER.query_bool(search_dict, 'MEDIA')

                # Check if media_data is not empty
                if media_data:
                    # Check if this image is already in the database
                    search_dict = {'id_media': "'" + str(media_data[0].id_media) + "'"}
                    existing_entry = self.DB_MANAGER.query_bool(search_dict, 'MEDIATOENTITY')

                    # If this image is already in the database, continue with the next item
                    if existing_entry:
                        continue

                    self.insert_mediaToEntity_rec(us_data[0], us_data[1], us_data[2], media_data[0].id_media,
                                                  media_data[0].filepath, media_data[0].filename)
                else:
                    pass
                    #QMessageBox.warning(self, "Attenzione",
                                        #"Immagine già taggata: " + str(id_orig_item))
                    # After tagging the image, update the corresponding QListWidgetItem

        # After tagging, update the iconListWidget
        self.fill_iconListWidget()
        self.update_list_widget_item(item)
    def update_list_widget_item(self,item):
        #items_selected = self.new_list_widg)et.selectedItems(
        search_dict = {'media_name': "'" + str(item.text()) + "'"}
        u = Utility()
        search_dict = u.remove_empty_items_fr_dict(search_dict)
        mediatoentity_data = self.DB_MANAGER.query_bool(search_dict, "MEDIATOENTITY")

        # Update the QListWidgetItem based on whether it matches
        if mediatoentity_data:
            item.setBackground(QColor("white"))

            # Create a new search dictionary for the US
            search_dict_us = {'id_invmat': "'" + str(mediatoentity_data[0].id_entity) + "'"}
            search_dict_us = u.remove_empty_items_fr_dict(search_dict_us)

            # Query the US table
            us_data = self.DB_MANAGER.query_bool(search_dict_us, "INVENTARIO_MATERIALI")

            # If the US exists, add its name to the item
            if us_data:
                item.setText(item.text() + " - Manufatto: " + str(us_data[0].numero_inventario))
            else:
                item.setText(item.text() + " - Manufatto: Not found")

        else:
            item.setBackground(QColor("yellow"))

    def fill_iconListWidget(self):
        #self.iconListWidget.clear()  # pulisci prima il widget
        items_selected = self.new_list_widget.selectedItems()
        for item in items_selected:
            item.text()
        # Prendi i dati dal tuo database o dalla tua fonte dati
        #data = self.DB_MANAGER.query('MEDIA_THUMB')
        search_dict = {'media_filename': "'" + str(item.text()) + "'"}
        u = Utility()
        search_dict = u.remove_empty_items_fr_dict(search_dict)
        data = self.DB_MANAGER.query_bool(search_dict, "MEDIA_THUMB")
        #QMessageBox.information(self, 'ok',str(item.text()))
        conn = Connection()

        thumb_path = conn.thumb_path()
        thumb_path_str = thumb_path['thumb_path']
        # crea un nuovo QListWidgetItem
        if data:
            list_item = QListWidgetItem(data[0].media_filename)  # utilizza il nome del file come testo dell'elemento
            list_item.setData(Qt.ItemDataRole.UserRole,data[0].media_filename)  # utilizza il nome del file come dati personalizzati dell'elemento

            # crea una QIcon con l'immagine
            #icon = load_icon(get_image_path(thumb_path_str, thumb_path))
            icon = load_icon(get_image_path(thumb_path_str, data[0].filepath))  # utilizza il percorso del file per creare l'icona
            #QMessageBox.information(self,'ok',str(thumb_path_str + data[0].filepath))
            # imposta l'icona dell'elemento
            list_item.setIcon(icon)

            # aggiungi l'elemento al QListWidget
            self.iconListWidget.addItem(list_item)


    def connect_p(self):

        conn = Connection()
        conn_str = conn.conn_str()
        test_conn = conn_str.find('sqlite')
        if test_conn == 0:
            self.DB_SERVER = "sqlite"

        try:
            self.DB_MANAGER = get_db_manager(conn_str, use_singleton=True)
            self.charge_records()  # charge records from DB
            # check if DB is empty
            if self.DATA_LIST:
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                self.BROWSE_STATUS = 'b'
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.label_sort.setText(self.SORTED_ITEMS["n"])
                self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                self.charge_list()
                self.fill_fields()
                self.setComboBoxEnable(["self.comboBox_area"], "False")
                self.setComboBoxEnable(["self.lineEdit_us"], "False")
                self.iconListWidget.update()
            else:
                if self.L=='it':
                    QMessageBox.warning(self,"BENVENUTO", "Benvenuto in pyArchInit " + self.NOME_SCHEDA + ". Il database e' vuoto. Premi 'Ok' e buon lavoro!",
                                        QMessageBox.StandardButton.Ok)
                elif self.L=='de':
                    QMessageBox.warning(self,"WILLKOMMEN","WILLKOMMEN in pyArchInit" + "SE-MSE formular"+ ". Die Datenbank ist leer. Tippe 'Ok' und aufgehts!",
                                        QMessageBox.StandardButton.Ok)
                else:
                    QMessageBox.warning(self,"WELCOME", "Welcome in pyArchInit" + "Samples SU-WSU" + ". The DB is empty. Push 'Ok' and Good Work!",
                                        QMessageBox.StandardButton.Ok)
                self.charge_list()
                self.BROWSE_STATUS = 'x'
                self.setComboBoxEnable(["self.comboBox_area"], "True")
                self.setComboBoxEnable(["self.lineEdit_us"], "True")
                self.on_pushButton_new_rec_pressed()
                self.iconListWidget.update()
        except Exception as e:
            e = str(e)
            if e.find("no such table"):
                if self.L=='it':
                    msg = "La connessione e' fallita {}. " \
                          "E' NECESSARIO RIAVVIARE QGIS oppure rilevato bug! Segnalarlo allo sviluppatore".format(str(e))
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
    def sketchgpt(self):
        """Open GPT Sketch window with lazy import to avoid DLL conflicts on Windows."""
        try:
            # Lazy import to avoid loading PyMuPDF at plugin startup
            from ..modules.utility.skatch_gpt_INVMAT import GPTWindow
        except ImportError as e:
            error_msg = str(e)
            if 'DLL load failed' in error_msg or '_extra' in error_msg or 'pymupdf' in error_msg.lower():
                QMessageBox.warning(
                    self,
                    "GPT Sketch Feature Unavailable",
                    "The GPT Sketch feature cannot be loaded due to a PyMuPDF library conflict on Windows.\n\n"
                    "This is a known issue with PyMuPDF in QGIS environments.\n\n"
                    "Possible solutions:\n"
                    "1. Reinstall PyMuPDF: python -m pip uninstall pymupdf && python -m pip install pymupdf\n"
                    "2. Try installing an older version: python -m pip install pymupdf==1.23.26\n"
                    "3. Install PyMuPDF-binary: python -m pip install --force-reinstall pymupdf\n\n"
                    "The rest of the plugin will continue to work normally.",
                    QMessageBox.StandardButton.Ok
                )
            else:
                QMessageBox.warning(
                    self,
                    "GPT Sketch Import Error",
                    f"Cannot load GPT Sketch feature:\n\n{error_msg}",
                    QMessageBox.StandardButton.Ok
                )
            return
        except Exception as e:
            QMessageBox.warning(
                self,
                "Error",
                f"An unexpected error occurred:\n\n{str(e)}",
                QMessageBox.StandardButton.Ok
            )
            return

        items = self.iconListWidget.selectedItems()
        conn = Connection()
        thumb_resize = conn.thumb_resize()
        thumb_resize_str = thumb_resize['thumb_resize']

        def process_file_path(file_path):
            return urllib.parse.unquote(file_path)

        def query_media(search_dict, table="MEDIA_THUMB"):
            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)
            try:
                return self.DB_MANAGER.query_bool(search_dict, table)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Database query failed: {str(e)}", QMessageBox.StandardButton.Ok)
                return None

        selected_images = []
        for item in items:
            id_orig_item = item.text()
            search_dict = {'media_filename': f"'{id_orig_item}'"}
            res = query_media(search_dict)

            if res:
                file_path = process_file_path(os.path.join(thumb_resize_str, str(res[0].path_resize)))
                media_type = res[0].mediatype

                if media_type == 'image':
                    selected_images.append(file_path)
                elif media_type == '3d_model':
                    # Gestisci i modelli 3D se necessario
                    selected_images.append(file_path)
                elif media_type == 'video':
                    # Gestisci i video se necessario
                    selected_images.append(file_path)
            else:
                QMessageBox.warning(self, "Error", f"File not found: {id_orig_item}", QMessageBox.StandardButton.Ok)

        #if selected_images:
        self.gpt_window = GPTWindow(selected_images, dbmanager=self.DB_MANAGER, main_class=self)
        self.gpt_window.show()
        #else:
            #QMessageBox.warning(self, "Warning", "No valid images selected for analysis.", QMessageBox.Ok)

    def loadMediaPreview(self, mode=0):
        self.iconListWidget.clear()
        conn = Connection()

        thumb_path = conn.thumb_path()
        thumb_path_str = thumb_path['thumb_path']
        if mode == 0:
            """ if has geometry column load to map canvas """
            try:
                if not self.DATA_LIST or self.REC_CORR >= len(self.DATA_LIST):
                    return

                # Get id directly without using eval
                if hasattr(self.DATA_LIST[int(self.REC_CORR)], self.ID_TABLE):
                    id_val = getattr(self.DATA_LIST[int(self.REC_CORR)], self.ID_TABLE)
                    rec_list = self.ID_TABLE + " = " + str(id_val)
                    search_dict = {
                        'id_entity': "'" + str(id_val) + "'",
                        'entity_type': "'REPERTO'"}
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
            except Exception as e:
                pass  # Silently handle errors to avoid popup spam
        elif mode == 1:
            self.iconListWidget.clear()

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

        self.assignTags_reperti(item)

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

        # main_layout.addWidget(debug_widget)

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
                # if edge_visibility(edge):
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
            full_path = os.path.join(thumb_resize_str, file_path)
            if media_type == 'video':
                show_video(full_path)
            elif media_type == 'image':
                show_image(full_path)
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

                file_path = process_file_path(os.path.join(thumb_resize_str, str(res[0].path_resize)))

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


    def numero_invetario(self):
        if self.checkBox_auto_inv.isChecked():
            QMessageBox.information(self, "Attenzione", "Hai attivato l'opzione autoincrementante Numero Inventario", QMessageBox.StandardButton.Ok)
            self.lineEdit_num_inv.setText('')
            self.lineEdit_num_inv.textChanged.connect(self.update)
            # self.set_sito()
            contatore = 0
            list=[]
            if self.lineEdit_num_inv.text()=='':

                for i in range(len(self.DATA_LIST)):
                    #self.lineEdit_n_reperto.clear()
                    contatore = int(self.DATA_LIST[i].numero_inventario)
                    #contatore.sort(reverse=False)
                    list.append(contatore)


                    list[-1]+=1

                    list.sort()
                for e in list:    

                    self.lineEdit_num_inv.setText(str(e))
        else:
            pass
    def charge_list(self):

        l = QgsSettings().value("locale/userLocale", QVariant)
        lang = ""
        for key, values in self.LANG.items():
            if values.__contains__(l):
                lang = str(key)
        lang = "'" + lang + "'"

        #lista sito

        sito_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('site_table', 'sito', 'SITE'))
        try:
            sito_vl.remove('')
        except Exception as e:
            if str(e) == "list.remove(x): x not in list":
                pass
            else:
                if self.L=='it':
                    QMessageBox.warning(self, "Messaggio", "Sistema di aggiornamento lista Sito: " + str(e), QMessageBox.StandardButton.Ok)
                elif self.L=='en':
                    QMessageBox.warning(self, "Message", "Site list update system: " + str(e), QMessageBox.StandardButton.Ok)
                elif self.L=='de':
                    QMessageBox.warning(self, "Nachricht", "Aktualisierungssystem für die Ausgrabungstätte: " + str(e), QMessageBox.StandardButton.Ok)
                else:
                    pass

        self.comboBox_sito.clear()
        sito_vl.sort()
        self.comboBox_sito.addItems(sito_vl)

        #lista tipo reperto

        self.comboBox_tipo_reperto.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'inventario_materiali_table' + "'",
            'tipologia_sigla': "'" + '3.1' + "'"
        }

        tipo_reperto = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        tipo_reperto_vl = []

        for i in range(len(tipo_reperto)):
            tipo_reperto_vl.append(tipo_reperto[i].sigla_estesa)

        tipo_reperto_vl.sort()
        self.comboBox_tipo_reperto.addItems(tipo_reperto_vl)


        #lista tipologia - usa TMA materiali ripetibili codice 10.12
        self.comboBox_tipologia.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'tma_materiali_ripetibili' + "'",
            'tipologia_sigla': "'" + '10.12' + "'"  # Precisazione tipologica da materiali ripetibili
        }

        tipologia_reperto = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        tipologia_reperto_vl = []

        for i in range(len(tipologia_reperto)):
            tipologia_reperto_vl.append(tipologia_reperto[i].sigla_estesa)

        tipologia_reperto_vl.sort()
        self.comboBox_tipologia.addItems(tipologia_reperto_vl)




        # lista classe materiale

        self.comboBox_criterio_schedatura.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'inventario_materiali_table' + "'",
            'tipologia_sigla': "'" + '3.2' + "'"
        }

        criterio_schedatura = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        criterio_schedatura_vl = []

        for i in range(len(criterio_schedatura)):
            criterio_schedatura_vl.append(criterio_schedatura[i].sigla_estesa)

            criterio_schedatura_vl.sort()
        self.comboBox_criterio_schedatura.addItems(criterio_schedatura_vl)

        # lista definizione reperto

        self.comboBox_definizione.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'inventario_materiali_table' + "'",
            'tipologia_sigla': "'" + '3.3' + "'"
        }

        definizione = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        definizione_vl = []

        for i in range(len(definizione)):
            definizione_vl.append(definizione[i].sigla_estesa)

        definizione_vl.sort()
        self.comboBox_definizione.addItems(definizione_vl)

        # lista repertato

        self.comboBox_repertato.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'inventario_materiali_table' + "'",
            'tipologia_sigla': "'" + '301.301' + "'"
        }

        repertato = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        repertato_vl = []

        for i in range(len(repertato)):
            repertato_vl.append(repertato[i].sigla_estesa)

        repertato_vl.sort()
        self.comboBox_repertato.addItems(repertato_vl)

        # lista diagnostico

        self.comboBox_diagnostico.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'inventario_materiali_table' + "'",
            'tipologia_sigla': "'" + '301.301' + "'"
        }

        diagnostico = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        diagnostico_vl = []

        for i in range(len(diagnostico)):
            diagnostico_vl.append(diagnostico[i].sigla_estesa)

        diagnostico_vl.sort()
        self.comboBox_diagnostico.addItems(diagnostico_vl)
        
        # lista area
        self.comboBox_area.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'inventario_materiali_table' + "'",
            'tipologia_sigla': "'" + '3.11' + "'"
        }

        area_vl = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        area_vl_values = []

        for i in range(len(area_vl)):
            area_vl_values.append(area_vl[i].sigla_estesa)

        area_vl_values.sort()
        self.comboBox_area.addItems(area_vl_values)

        # lista lavato

        self.comboBox_lavato.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'inventario_materiali_table' + "'",
            'tipologia_sigla': "'" + '301.301' + "'"
        }

        lavato = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        lavato_vl = []

        for i in range(len(lavato)):
            lavato_vl.append(lavato[i].sigla_estesa)

        lavato_vl.sort()
        self.comboBox_lavato.addItems(lavato_vl)


        # lista anno

        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'inventario_materiali_table' + "'",
            'tipologia_sigla': "'" + '3.13' + "'"
        }

        year_ = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        valuesyear = []

        for i in range(len(year_)):
            valuesyear.append(year_[i].sigla_estesa)

        valuesyear.sort()
        self.comboBox_year.addItems(valuesyear)

        # lista compilatore/schedatore - populate from thesaurus
        self.comboBox_compilatore.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'inventario_materiali_table' + "'",
            'tipologia_sigla': "'" + '3.14' + "'"  # Using 3.14 for compilatore
        }

        compilatore = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        compilatore_vl = []

        for i in range(len(compilatore)):
            compilatore_vl.append(compilatore[i].sigla_estesa)

        compilatore_vl.sort()
        self.comboBox_compilatore.addItems(compilatore_vl)

        # lista datazione - usa fascia cronologica dalla TMA
        self.comboBox_datazione.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'TMA materiali archeologici' + "'",
            'tipologia_sigla': "'" + '10.4' + "'"  # Fascia cronologica (dtzg) dalla TMA
        }

        datazione = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        datazione_vl = []

        for i in range(len(datazione)):
            datazione_vl.append(datazione[i].sigla_estesa)

        datazione_vl.sort()
        self.comboBox_datazione.addItems(datazione_vl)


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
        #self.model_a.database().close()
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
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                # Check if DATA_LIST is empty before accessing index 0
                if len(self.DATA_LIST) == 0:
                    if self.L=='it':
                        QMessageBox.information(self, "Informazione", f"Nessun record trovato per il sito '{sito_set_str}' in questa scheda.", QMessageBox.StandardButton.Ok)
                    elif self.L=='de':
                        QMessageBox.information(self, "Information", f"Keine Datensätze für die Fundstelle '{sito_set_str}' in dieser Registerkarte gefunden.", QMessageBox.StandardButton.Ok)
                    else:
                        QMessageBox.information(self, "Information", f"No records found for site '{sito_set_str}' in this tab.", QMessageBox.StandardButton.Ok)
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
            if self.L=='it':
                QMessageBox.warning(self, "Errore", f"Errore durante il caricamento dei dati: {str(e)}", QMessageBox.StandardButton.Ok)
            elif self.L=='de':
                QMessageBox.warning(self, "Fehler", f"Fehler beim Laden der Daten: {str(e)}", QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.warning(self, "Error", f"Error loading data: {str(e)}", QMessageBox.StandardButton.Ok)  

    def on_pushButton_sort_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            dlg = SortPanelMain(self)
            dlg.insertItems(self.SORT_ITEMS)
            dlg.exec()

            items, order_type = dlg.ITEMS, dlg.TYPE_ORDER

            self.SORT_ITEMS_CONVERTED = []
            for i in items:
                self.SORT_ITEMS_CONVERTED.append(self.CONVERSION_DICT[str(i)])

            self.SORT_MODE = order_type
            self.empty_fields()

            id_list = []
            for i in self.DATA_LIST:
                id_list.append(getattr(i, self.ID_TABLE))
            self.DATA_LIST = []

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

            self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
            self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
            self.SORT_STATUS = "o"
            self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
            self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
            self.fill_fields()

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

        if self.BROWSE_STATUS != "n":
            if bool(self.comboBox_sito.currentText()) and self.comboBox_sito.currentText()==sito_set_str:
                self.BROWSE_STATUS = "n"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.empty_fields_nosite()

                #self.setComboBoxEditable(['self.comboBox_sito'],0)
                # self.setComboBoxEditable(['self.comboBox_sito'], 1)
                self.setComboBoxEnable(['self.comboBox_sito'], 'False')
                self.setComboBoxEnable(['self.lineEdit_num_inv'], 'True')

                self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])

                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.set_rec_counter('', '')
                self.label_sort.setText(self.SORTED_ITEMS["n"])
                self.numero_invetario()
                #self.numero_reperto()
            else:
                self.BROWSE_STATUS = "n"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.empty_fields()

                self.setComboBoxEditable(['self.comboBox_sito'],0)
                # self.setComboBoxEditable(['self.comboBox_sito'], 1)
                self.setComboBoxEnable(['self.comboBox_sito'], 'True')
                self.setComboBoxEnable(['self.lineEdit_num_inv'], 'True')

                self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])

                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.set_rec_counter('', '')
                self.label_sort.setText(self.SORTED_ITEMS["n"])
                #self.numero_invetario()
                #self.numero_reperto()

            self.enable_button(0)

    def on_pushButton_save_pressed(self):
        # duplicates=[]
        # for value in self.DATA_LIST:
            # duplicates.append(value.numero_inventario)
        # if Error_check.checkIfDuplicates_3(duplicates):
            # QMessageBox.warning(self, "INFO", "error",
                                # QMessageBox.Ok)


        if self.BROWSE_STATUS == "b":
            
                    # Check for version conflicts before updating
                    if hasattr(self, 'current_record_version') and self.current_record_version:
                        conflict = self.concurrency_manager.check_version_conflict(
                            'inventario_materiali_table',
                            self.editing_record_id,
                            self.current_record_version,
                            self.DB_MANAGER
                        )

                        if conflict and conflict['has_conflict']:
                            # Handle the conflict
                            record_data = self.fill_record()
                            if self.concurrency_manager.handle_conflict(
                                'inventario_materiali_table',
                                record_data,
                                conflict
                            ):
                                # User chose to reload - refresh the form
                                self.charge_records()
                                self.fill_fields(self.REC_CORR)
                                return
                            # Otherwise continue with save (user chose to overwrite)

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

                    self.setComboBoxEditable(['self.comboBox_sito'], 1)
                    self.setComboBoxEnable(['self.comboBox_sito'], 'False')
                    self.setComboBoxEnable(['self.lineEdit_num_inv'], 'False')

                    self.fill_fields(self.REC_CORR)
                    self.enable_button(1)
            else:
                if self.L=='it':
                    QMessageBox.warning(self, "ATTENZIONE", "Problema nell'inserimento dati", QMessageBox.StandardButton.Ok)
                elif self.L=='de':
                    QMessageBox.warning(self, "ACHTUNG", "Problem der Dateneingabe", QMessageBox.StandardButton.Ok)
                else:
                    QMessageBox.warning(self, "Warning", "Problem with data entry", QMessageBox.StandardButton.Ok) 
    def on_toolButtonGis_toggled(self):
        if self.L=='it':
            if self.toolButtonGis.isChecked():
                QMessageBox.warning(self, "Messaggio",
                                    "Modalita' GIS attiva. Da ora le tue ricerche verranno visualizzate sul GIS",
                                    QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.warning(self, "Messaggio",
                                    "Modalita' GIS disattivata. Da ora le tue ricerche non verranno piu' visualizzate sul GIS",
                                    QMessageBox.StandardButton.Ok)
        elif self.L=='de':
            if self.toolButtonGis.isChecked():
                QMessageBox.warning(self, "Message",
                                    "Modalität' GIS aktiv. Von jetzt wird Deine Untersuchung mit Gis visualisiert",
                                    QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.warning(self, "Message",
                                    "Modalität' GIS deaktiviert. Von jetzt an wird deine Untersuchung nicht mehr mit Gis visualisiert",
                                    QMessageBox.StandardButton.Ok)
        else:
            if self.toolButtonGis.isChecked():
                QMessageBox.warning(self, "Message",
                                    "GIS mode active. From now on your searches will be displayed on the GIS",
                                    QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.warning(self, "Message",
                                    "GIS mode disabled. From now on, your searches will no longer be displayed on the GIS.",
                                    QMessageBox.StandardButton.Ok)


    def generate_list_foto(self):
        data_list_foto = []
        for i in range(len(self.DATA_LIST)):
            try:
                conn = Connection()

                thumb_path = conn.thumb_path()
                thumb_path_str = thumb_path['thumb_path']

                # Check if id_invmat attribute exists
                if hasattr(self.DATA_LIST[i], 'id_invmat'):
                    id_invmat = str(self.DATA_LIST[i].id_invmat)
                    search_dict = {'id_entity': "'"+ id_invmat +"'", 'entity_type' : "'REPERTO'"}

                    record_doc_list = self.DB_MANAGER.query_bool(search_dict, 'MEDIAVIEW')

                    img_list = []

                    for media in record_doc_list:
                        try:
                            thumb = (thumb_path_str + str(media.filepath))

                            img_list.append(thumb)
                        except AssertionError as e:
                            QMessageBox.warning(self, 'message', str(e))

                    if img_list:
                        a = img_list[0]
                    else:
                        a = ''

                    # Get photo_id and drawing_id with safe access
                    photo_id_val = ''
                    drawing_id_val = ''
                    if hasattr(self.DATA_LIST[i], 'photo_id') and self.DATA_LIST[i].photo_id:
                        photo_id_val = str(self.DATA_LIST[i].photo_id)
                    if hasattr(self.DATA_LIST[i], 'drawing_id') and self.DATA_LIST[i].drawing_id:
                        drawing_id_val = str(self.DATA_LIST[i].drawing_id)

                    data_list_foto.append([
                        str(self.DATA_LIST[i].sito.replace('_',' ')), #0
                        str(self.DATA_LIST[i].n_reperto),  #1
                        str(a),  #2 - thumbnail
                        str(self.DATA_LIST[i].us),    #3
                        str(self.DATA_LIST[i].definizione),#4
                        str(self.DATA_LIST[i].datazione_reperto), #5
                        str(self.DATA_LIST[i].stato_conservazione), #6
                        str(self.DATA_LIST[i].tipo_contenitore), #7
                        str(self.DATA_LIST[i].nr_cassa),  #8
                        photo_id_val,  #9 - photo_id
                        drawing_id_val])  #10 - drawing_id
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e), QMessageBox.StandardButton.Ok)

        return data_list_foto

    def generate_list(self):
        data_list = []
        for i in range(len(self.DATA_LIST)):
            # Get photo_id and drawing_id with safe access
            photo_id_val = ''
            drawing_id_val = ''
            if hasattr(self.DATA_LIST[i], 'photo_id') and self.DATA_LIST[i].photo_id:
                photo_id_val = str(self.DATA_LIST[i].photo_id)
            if hasattr(self.DATA_LIST[i], 'drawing_id') and self.DATA_LIST[i].drawing_id:
                drawing_id_val = str(self.DATA_LIST[i].drawing_id)

            data_list.append([
                str(self.DATA_LIST[i].sito.replace('_',' ')),  # 0 - sito
                str(self.DATA_LIST[i].numero_inventario),  # 1 - numero_inventario
                str(self.DATA_LIST[i].area),  # 2 - area
                str(self.DATA_LIST[i].us),  # 3 - us
                str(self.DATA_LIST[i].tipo_reperto),  # 4 - tipo_reperto
                str(self.DATA_LIST[i].repertato),  # 5 - repertato
                str(self.DATA_LIST[i].n_reperto),  # 6 - n_reperto
                str(self.DATA_LIST[i].tipo_contenitore),  # 7 - tipo_contenitore
                str(self.DATA_LIST[i].nr_cassa),  # 8 - nr_cassa
                str(self.DATA_LIST[i].luogo_conservazione),  # 9 - luogo_conservazione
                str(self.DATA_LIST[i].years),  # 10 - years
                photo_id_val,  # 11 - photo_id
                drawing_id_val  # 12 - drawing_id
            ])

        return data_list





    def generate_list_pdf(self):

        data_list = []
        conn = Connection()

        thumb_resize = conn.thumb_resize()
        thumb_path_str = thumb_resize['thumb_resize']


        for i in range(len(self.DATA_LIST)):
            try:
                # Check if id_invmat attribute exists
                if hasattr(self.DATA_LIST[i], 'id_invmat'):
                    id_invmat = str(self.DATA_LIST[i].id_invmat)
                    search_dict = {'id_entity': "'" + id_invmat + "'",
                                'entity_type': "'REPERTO'"}

                    record_doc_list = self.DB_MANAGER.query_bool(search_dict, 'MEDIAVIEW')
                    img_list=[]

                    for media in record_doc_list:
                        try:
                            thumb= (thumb_path_str + str(media.path_resize))

                            img_list.append(thumb)
                        except AssertionError as e:
                            QMessageBox.warning(self,'message',str(e))


                    if img_list:
                        a = img_list[0]
                    else:
                        a=''

                    # Get photo_id and drawing_id values
                    photo_id_val = ''
                    drawing_id_val = ''
                    if hasattr(self.DATA_LIST[i], 'photo_id') and self.DATA_LIST[i].photo_id:
                        photo_id_val = str(self.DATA_LIST[i].photo_id)
                    if hasattr(self.DATA_LIST[i], 'drawing_id') and self.DATA_LIST[i].drawing_id:
                        drawing_id_val = str(self.DATA_LIST[i].drawing_id)

                    data_list.append([
                        str(self.DATA_LIST[i].id_invmat),  # 0 - id_invmat
                        str(self.DATA_LIST[i].sito.replace('_',' ')),  # 1 - sito
                        int(self.DATA_LIST[i].numero_inventario),  # 2 - numero_inventario
                        str(self.DATA_LIST[i].tipo_reperto),  # 3 - tipo_reperto
                        str(self.DATA_LIST[i].criterio_schedatura),  # 4 - criterio_schedatura
                        str(self.DATA_LIST[i].definizione),  # 5 - definizione
                        str(self.DATA_LIST[i].descrizione),  # 6 - descrizione
                        str(self.DATA_LIST[i].area),  # 7 - area
                        str(self.DATA_LIST[i].us),  # 8 - us
                        str(self.DATA_LIST[i].lavato),  # 9 - lavato
                        str(self.DATA_LIST[i].nr_cassa),  # 10 - nr_cassa
                        str(self.DATA_LIST[i].luogo_conservazione),  # 11 - luogo_conservazione
                        str(self.DATA_LIST[i].stato_conservazione),  # 12 - stato_conservazione
                        str(self.DATA_LIST[i].datazione_reperto),  # 13 - datazione_reperto
                        str(self.DATA_LIST[i].elementi_reperto),  # 14 - elementi_reperto
                        str(self.DATA_LIST[i].misurazioni),  # 15 - misurazioni
                        str(self.DATA_LIST[i].rif_biblio),  # 16 - rif_biblio
                        str(self.DATA_LIST[i].tecnologie),  # 17 - tecnologie
                        str(self.DATA_LIST[i].tipo),  # 18 - tipo
                        str(self.DATA_LIST[i].corpo_ceramico),  # 19 - corpo_ceramico
                        str(self.DATA_LIST[i].rivestimento),  # 20 - rivestimento
                        str(self.DATA_LIST[i].repertato),  # 21 - repertato
                        str(self.DATA_LIST[i].diagnostico),  # 22 - diagnostico
                        str(self.DATA_LIST[i].n_reperto),  # 23 - n_reperto
                        str(self.DATA_LIST[i].tipo_contenitore),  # 24 - tipo_contenitore
                        str(self.DATA_LIST[i].struttura),  # 25 - struttura
                        str(self.DATA_LIST[i].years),  # 26 - years
                        str(a),  # 27 - thumbnail
                        photo_id_val,  # 28 - photo_id
                        drawing_id_val  # 29 - drawing_id
                    ])
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e), QMessageBox.StandardButton.Ok)
        #QMessageBox.warning(self, 'message', str(t))
        return data_list
    def on_pushButton_print_pressed(self):
        if self.L=='it':
            if self.checkBox_s_us.isChecked():
                US_pdf_sheet = generate_reperti_pdf()
                data_list = self.generate_list_pdf()
                US_pdf_sheet.build_Finds_sheets(data_list)
                QMessageBox.warning(self, 'Ok',"Esportazione terminata Schede Materiali",QMessageBox.StandardButton.Ok)
            else:   
                pass

            if self.checkBox_e_us.isChecked() :
                # US_index_pdf = generate_reperti_pdf()
                # data_list = self.generate_el_casse_pdf()



                sito_ec = str(self.comboBox_sito.currentText())
                Mat_casse_pdf = generate_reperti_pdf()
                data_list = self.generate_el_casse_pdf(sito_ec)

                Mat_casse_pdf.build_index_Casse(data_list, sito_ec)
                QMessageBox.warning(self, 'Ok',"Esportazione terminata Elenco Casse",QMessageBox.StandardButton.Ok)


            else:
                pass

            if self.checkBox_e_foto_t.isChecked():
                US_index_pdf = generate_reperti_pdf()
                data_list_foto = self.generate_list_foto()

                try:

                    US_index_pdf.build_index_Foto(data_list_foto, data_list_foto[0][0])
                    QMessageBox.warning(self, 'Ok',"Esportazione terminata Elenco Reperti",QMessageBox.StandardButton.Ok)

                        # else:
                            # QMessageBox.warning(self, 'ATTENZIONE',"L'elenco foto non può essere esportato perchè non hai immagini taggate.",QMessageBox.Ok)
                except Exception as e :
                    QMessageBox.warning(self, 'ATTENZIONE',str(e),QMessageBox.StandardButton.Ok)

            if self.checkBox_e_foto.isChecked():
                US_index_pdf = generate_reperti_pdf()
                data_list = self.generate_list()

                try:

                    US_index_pdf.build_index_Foto_2(data_list, data_list[0][0])
                    QMessageBox.warning(self, 'Ok',"Esportazione terminata Elenco Inventario",QMessageBox.StandardButton.Ok)

                        # else:
                            # QMessageBox.warning(self, 'ATTENZIONE',"L'elenco foto non può essere esportato perchè non hai immagini taggate.",QMessageBox.Ok)
                except Exception as e :
                    QMessageBox.warning(self, 'ATTENZIONE',str(e),QMessageBox.StandardButton.Ok)

        elif self.L=='de':
            if self.checkBox_s_us.isChecked():
                US_pdf_sheet = generate_reperti_pdf()
                data_list = self.generate_list_pdf()
                US_pdf_sheet.build_Finds_sheets_de(data_list)
                QMessageBox.warning(self, 'Ok',"Export beendet",QMessageBox.StandardButton.Ok)
            else:   
                pass

            if self.checkBox_e_us.isChecked() :
                # US_index_pdf = generate_reperti_pdf()
                # data_list = self.generate_el_casse_pdf()



                sito_ec = str(self.comboBox_sito.currentText())
                Mat_casse_pdf = generate_reperti_pdf()
                data_list = self.generate_el_casse_pdf(sito_ec)

                Mat_casse_pdf.build_index_Casse_de(data_list, sito_ec)
                QMessageBox.warning(self, 'Ok',"Export beendet",QMessageBox.StandardButton.Ok)


            else:
                pass

            if self.checkBox_e_foto_t.isChecked():
                US_index_pdf = generate_reperti_pdf()
                data_list_foto = self.generate_list_foto()

                try:

                    US_index_pdf.build_index_Foto_de(data_list_foto, data_list_foto[0][0])
                    QMessageBox.warning(self, 'Ok',"Export beendet",QMessageBox.StandardButton.Ok)

                        # else:
                            # QMessageBox.warning(self, 'ATTENZIONE',"L'elenco foto non può essere esportato perchè non hai immagini taggate.",QMessageBox.Ok)
                except Exception as e :
                    QMessageBox.warning(self, 'Warnung',str(e),QMessageBox.StandardButton.Ok)

            if self.checkBox_e_foto.isChecked():
                US_index_pdf = generate_reperti_pdf()
                data_list = self.generate_list()

                try:

                    US_index_pdf.build_index_Foto_2_de(data_list, data_list[0][0])
                    QMessageBox.warning(self, 'Ok',"Export beendet",QMessageBox.StandardButton.Ok)

                        # else:
                            # QMessageBox.warning(self, 'ATTENZIONE',"L'elenco foto non può essere esportato perchè non hai immagini taggate.",QMessageBox.Ok)
                except Exception as e :
                    QMessageBox.warning(self, 'Warnung',str(e),QMessageBox.StandardButton.Ok)

        elif self.L=='fr':
            if self.checkBox_s_us.isChecked():
                US_pdf_sheet = generate_reperti_pdf()
                data_list = self.generate_list_pdf()
                US_pdf_sheet.build_Finds_sheets_fr(data_list)
                QMessageBox.warning(self, 'Ok',"Exportation des fiches terminée",QMessageBox.StandardButton.Ok)
            else:
                pass

        elif self.L=='es':
            if self.checkBox_s_us.isChecked():
                US_pdf_sheet = generate_reperti_pdf()
                data_list = self.generate_list_pdf()
                US_pdf_sheet.build_Finds_sheets_es(data_list)
                QMessageBox.warning(self, 'Ok',"Exportación de fichas completada",QMessageBox.StandardButton.Ok)
            else:
                pass

        elif self.L=='ar':
            if self.checkBox_s_us.isChecked():
                US_pdf_sheet = generate_reperti_pdf()
                data_list = self.generate_list_pdf()
                US_pdf_sheet.build_Finds_sheets_ar(data_list)
                QMessageBox.warning(self, 'Ok',"اكتمل تصدير البطاقات",QMessageBox.StandardButton.Ok)
            else:
                pass

        elif self.L=='ca':
            if self.checkBox_s_us.isChecked():
                US_pdf_sheet = generate_reperti_pdf()
                data_list = self.generate_list_pdf()
                US_pdf_sheet.build_Finds_sheets_ca(data_list)
                QMessageBox.warning(self, 'Ok',"Exportació de fitxes completada",QMessageBox.StandardButton.Ok)
            else:
                pass

        else:
            if self.checkBox_s_us.isChecked():
                US_pdf_sheet = generate_reperti_pdf()
                data_list = self.generate_list_pdf()
                US_pdf_sheet.build_Finds_sheets_en(data_list)
                QMessageBox.warning(self, 'Ok',"Exportation Forms complited",QMessageBox.StandardButton.Ok)
            else:   
                pass

            if self.checkBox_e_us.isChecked() :
                # US_index_pdf = generate_reperti_pdf()
                # data_list = self.generate_el_casse_pdf()



                sito_ec = str(self.comboBox_sito.currentText())
                Mat_casse_pdf = generate_reperti_pdf()
                data_list = self.generate_el_casse_pdf(sito_ec)

                Mat_casse_pdf.build_index_Casse_en(data_list, sito_ec)
                QMessageBox.warning(self, 'Ok',"Exportation list box complited",QMessageBox.StandardButton.Ok)


            else:
                pass

            if self.checkBox_e_foto_t.isChecked():
                US_index_pdf = generate_reperti_pdf()
                data_list_foto = self.generate_list_foto()

                try:

                    US_index_pdf.build_index_Foto_en(data_list_foto, data_list_foto[0][0])
                    QMessageBox.warning(self, 'Ok',"Exportation Artefact complited",QMessageBox.StandardButton.Ok)

                        # else:
                            # QMessageBox.warning(self, 'ATTENZIONE',"L'elenco foto non può essere esportato perchè non hai immagini taggate.",QMessageBox.Ok)
                except Exception as e :
                    QMessageBox.warning(self, 'Warning',str(e),QMessageBox.StandardButton.Ok)

            if self.checkBox_e_foto.isChecked():
                US_index_pdf = generate_reperti_pdf()
                data_list = self.generate_list()

                try:

                    US_index_pdf.build_index_Foto_2_en(data_list, data_list[0][0])
                    QMessageBox.warning(self, 'Ok',"Exportation list complited",QMessageBox.StandardButton.Ok)

                        # else:
                            # QMessageBox.warning(self, 'ATTENZIONE',"L'elenco foto non può essere esportato perchè non hai immagini taggate.",QMessageBox.Ok)
                except Exception as e :
                    QMessageBox.warning(self, 'Warning',str(e),QMessageBox.StandardButton.Ok)

    def setPathpdf(self):
        s = QgsSettings()
        dbpath = QFileDialog.getOpenFileName(
            self,
            "Set file name",
            self.PDFFOLDER,
            " PDF (*.pdf)"
        )[0]

        if dbpath:

            self.lineEdit_pdf_path.setText(dbpath)
            s.setValue('',dbpath)

    # def on_pushButton_convert_pressed(self):
    #     # if not bool(self.setPathpdf()):
    #         # QMessageBox.warning(self, "INFO", "devi scegliere un file pdf",
    #                             # QMessageBox.Ok)
    #
    #     try:
    #         pdf_file = self.lineEdit_pdf_path.text()
    #         filename=pdf_file.split("/")[-1]
    #         docx_file = self.PDFFOLDER+'/'+filename+'.docx'
    #
    #         # convert pdf to docx
    #         parse(pdf_file, docx_file, start=self.lineEdit_pag1.text(), end=self.lineEdit_pag2.text())
    #         QMessageBox.information(self, "INFO", "Conversione terminata",
    #                             QMessageBox.Ok)
    #
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





    # def on_pushButton_elenco_casse_pressed(self):

        # if self.L=='it': 
            # sito_ec = str(self.comboBox_sito.currentText())
            # Mat_casse_pdf = generate_reperti_pdf()
            # data_list = self.generate_el_casse_pdf(sito_ec)

            # Mat_casse_pdf.build_index_Casse(data_list, sito_ec)
            # Mat_casse_pdf.build_box_labels_Finds(data_list, sito_ec)
        # elif self.L=='de': 
            # sito_ec = str(self.comboBox_sito.currentText())
            # Mat_casse_pdf = generate_reperti_pdf()
            # data_list = self.generate_el_casse_pdf(sito_ec)

            # Mat_casse_pdf.build_index_Casse_de(data_list, sito_ec)
            # Mat_casse_pdf.build_box_labels_Finds_de(data_list, sito_ec)
        # else: 
            # sito_ec = str(self.comboBox_sito.currentText())
            # Mat_casse_pdf = generate_reperti_pdf()
            # data_list = self.generate_el_casse_pdf(sito_ec)

            # Mat_casse_pdf.build_index_Casse_en(data_list, sito_ec)
            # Mat_casse_pdf.build_box_labels_Finds_en(data_list, sito_ec)    
        # ********************************************************************************

    def generate_el_casse_pdf(self, sito):
        self.sito_ec = sito
        elenco_casse_res = self.DB_MANAGER.query_distinct('INVENTARIO_MATERIALI',
                                                          [['sito', '"' + str(self.sito_ec) + '"']], ['nr_cassa'])

        elenco_casse_list = []  # accoglie la sigla numerica delle casse presenti per un determinato sito.
        try:
            for i in elenco_casse_res:
                elenco_casse_list.append(i.nr_cassa)

            data_for_pdf = []  # contiene i singoli dati per l'esportazione dell'elenco casse

            # QMessageBox.warning(self,'elenco casse',str(elenco_casse_list), QMessageBox.Ok)
            #elenco_casse_list.sort()
            for cassa in elenco_casse_list:
                single_cassa = []  # contiene i dati della singola cassa

                str_cassa = "<b>" + str(cassa) + "</b>"
                single_cassa.append(str_cassa)  # inserisce la sigla di cassa

                ###cerca le singole area/us presenti in quella cassa
                res_inv = self.DB_MANAGER.query_distinct('INVENTARIO_MATERIALI',
                                                         [['sito', '"' + str(self.sito_ec) + '"'], ['nr_cassa', cassa]],
                                                         ['numero_inventario', 'tipo_reperto'])

                res_inv_list = []
                for i in res_inv:
                    res_inv_list.append(i)

                n_inv_res_list = ""
                for i in range(len(res_inv_list)):
                    if i != len(res_inv_list) - 1:
                        n_inv_res_list += "Nr.inv:" + str(res_inv_list[i].numero_inventario) + "/" + str(
                            res_inv_list[i].tipo_reperto) + ","
                    else:
                        n_inv_res_list += "Nr.inv:" + str(res_inv_list[i].numero_inventario) + "/" + str(
                            res_inv_list[i].tipo_reperto)

                        # inserisce l'elenco degli inventari
                single_cassa.append(n_inv_res_list)

                ###cerca le singole area/us presenti in quella cassa
                res_us = self.DB_MANAGER.query_distinct('INVENTARIO_MATERIALI',
                                                        [['sito', '"' + str(self.sito_ec) + '"'], ['nr_cassa', cassa]],
                                                        ['area', 'us'])

                res_us_list = []
                for i in res_us:
                    res_us_list.append(i)

                us_res_list = ""  # [] #accoglie l'elenco delle US presenti in quella cassa
                for i in range(len(res_us_list)):
                    params_dict = {'sito': '"' + str(self.sito_ec) + '"', 'area': '"' + str(res_us_list[i].area) + '"',
                                   'us': '"' + str(res_us_list[i].us) + '"'}

                    res_struct = self.DB_MANAGER.query_bool(params_dict, 'US')

                    res_struct_list = []
                    for s_strutt in res_struct:
                        res_struct_list.append(s_strutt)

                    structure_string = ""
                    if len(res_struct_list) > 0:
                        for sing_us in res_struct_list:
                            if sing_us.struttura != '':
                                structure_string += "(" + str(sing_us.struttura) + '/'

                        if structure_string != "":
                            structure_string += ")"
                    if self.L=='it':
                        if i != len(res_us_list) - 1:
                            us_res_list += "Area:" + str(res_us_list[i].area) + ",US:" + str(
                                res_us_list[i].us) + structure_string + ", "  # .append("Area:"+str(i.area) + ",US:"+str(i.us))
                        else:
                            us_res_list += "Area:" + str(res_us_list[i].area) + ",US:" + str(
                                res_us_list[i].us) + structure_string  # .append("Area:"+str(i.area) + ",US:"+str(i.us))

                            # us_res_list.sort()
                            # inserisce l'elenco delle us
                    elif self.L=='de':
                        if i != len(res_us_list) - 1:
                            us_res_list += "Areal:" + str(res_us_list[i].area) + ",SE:" + str(
                                res_us_list[i].us) + structure_string + ", "  # .append("Area:"+str(i.area) + ",US:"+str(i.us))
                        else:
                            us_res_list += "Area:" + str(res_us_list[i].area) + ",SE:" + str(
                                res_us_list[i].us) + structure_string  # .append("Area:"+str(i.area) + ",US:"+str(i.us))

                            # us_res_list.sort()
                            # inserisce l'elenco delle us       

                    else:
                        if i != len(res_us_list) - 1:
                            us_res_list += "Area:" + str(res_us_list[i].area) + ",SU:" + str(
                                res_us_list[i].us) + structure_string + ", "  # .append("Area:"+str(i.area) + ",US:"+str(i.us))
                        else:
                            us_res_list += "Area:" + str(res_us_list[i].area) + ",SU:" + str(
                                res_us_list[i].us) + structure_string  # .append("Area:"+str(i.area) + ",US:"+str(i.us))

                            # us_res_list.sort()
                            # inserisce l'elenco delle us           

                single_cassa.append(us_res_list)

                ###cerca il luogo di conservazione della cassa
                params_dict = {'sito': '"' + str(self.sito_ec) + '"', 'nr_cassa': '"' + str(cassa) + '"'}
                res_luogo_conservazione = self.DB_MANAGER.query_bool(params_dict, 'INVENTARIO_MATERIALI')
                luogo_conservazione = res_luogo_conservazione[0].luogo_conservazione
                single_cassa.append(luogo_conservazione)  # inserisce la sigla di cassa

                ##          ###cerca le singole area/us presenti in quella cassa
                ##          res_tip_reperto = self.DB_MANAGER.query_distinct('INVENTARIO_MATERIALI',[['sito','"Sito archeologico"'], ['nr_cassa',cassa]], ['tipo_reperto'])
                ##
                ##          tip_rep_res_list = ""
                ##          for i in res_tip_reperto:
                ##              tip_rep_res_list += str(i.tipo_reperto) +"<br/>"
                ##
                ##          #inserisce l'elenco degli inventari
                ##          single_cassa.append(tip_rep_res_list)


                data_for_pdf.append(single_cassa)

                # QMessageBox.warning(self,'tk',str(data_for_pdf), QMessageBox.Ok)
            return data_for_pdf
        except Exception as e:
            QMessageBox.warning(self,'Warning','Il campo cassa non deve essere vuoto', QMessageBox.StandardButton.Ok)
    ####################################################
    def on_pushButton_esporta_a5_pressed(self):
        """Esporta la scheda inventario in formato A5 con immagine"""
        try:
            # Verifica che ci siano dati
            if not self.DATA_LIST:
                QMessageBox.warning(self, 'ATTENZIONE',
                                   'Non ci sono schede da esportare',
                                   QMessageBox.StandardButton.Ok)
                return

            # Dialog per i titoli dell'intestazione
            dialog = QDialog(self)
            dialog.setWindowTitle('Intestazione PDF')
            dialog.setModal(True)

            layout = QVBoxLayout()

            # Primo titolo (sinistra)
            label1 = QLabel('Titolo sinistro (es. SCUOLA ARCHEOLOGICA ITALIANA DI ATENE):')
            layout.addWidget(label1)

            title_left = QLineEdit()
            title_left.setText('SCUOLA ARCHEOLOGICA ITALIANA DI ATENE')
            layout.addWidget(title_left)

            # Secondo titolo (destra)
            label2 = QLabel('Titolo destro (lasciare vuoto per usare il nome del sito):')
            layout.addWidget(label2)

            title_right = QLineEdit()
            title_right.setPlaceholderText('Es. SCAVI DI FESTOS (CRETA)')
            layout.addWidget(title_right)

            # Bottoni
            button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            button_box.accepted.connect(dialog.accept)
            button_box.rejected.connect(dialog.reject)
            layout.addWidget(button_box)

            dialog.setLayout(layout)

            if dialog.exec() != QDialog.DialogCode.Accepted:
                return

            left_title = title_left.text()
            right_title = title_right.text()

            # Se il titolo destro è vuoto, usa il nome del sito
            if not right_title and self.DATA_LIST:
                right_title = f"SCAVI DI {str(self.DATA_LIST[0].sito).upper()}"

            # Chiedi all'utente se esportare solo il record corrente o tutti
            export_option = QMessageBox.question(self, 'Esportazione A5',
                                                'Vuoi esportare solo la scheda corrente o tutte le schede?\n\n'
                                                'Sì = Solo scheda corrente\n'
                                                'No = Tutte le schede\n'
                                                'Annulla = Annulla operazione',
                                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)

            if export_option == QMessageBox.StandardButton.Cancel:
                return

            records_to_export = []

            if export_option == QMessageBox.StandardButton.Yes:
                # Esporta solo il record corrente
                if self.REC_CORR < 0 or self.REC_CORR >= len(self.DATA_LIST):
                    QMessageBox.warning(self, 'ATTENZIONE',
                                       'Nessun record selezionato',
                                       QMessageBox.StandardButton.Ok)
                    return

                current_record = self.DATA_LIST[self.REC_CORR]
                record_list = self.record_to_list(current_record)
                records_to_export.append(record_list)

            else:
                # Esporta tutti i record
                for record in self.DATA_LIST:
                    record_list = self.record_to_list(record)
                    records_to_export.append(record_list)

            if not records_to_export:
                QMessageBox.warning(self, 'ATTENZIONE',
                                   'Nessun record da esportare',
                                   QMessageBox.StandardButton.Ok)
                return

            # Crea l'oggetto PDF generator
            pdf_generator = generate_inventario_pdf_a5()

            # Ottieni il sito dal primo record
            sito = str(records_to_export[0][1]) if records_to_export else ''

            # Genera il PDF con i titoli personalizzati
            pdf_generator.build_Inventario_a5(records_to_export, sito, left_title, right_title)

            # Mostra messaggio di conferma
            num_records = len(records_to_export)
            msg = f'Esportata {num_records} scheda A5' if num_records == 1 else f'Esportate {num_records} schede A5'
            QMessageBox.information(self, 'ESPORTAZIONE COMPLETATA', msg, QMessageBox.StandardButton.Ok)

            # Apri il PDF generato
            filepath = os.path.join(pdf_generator.PDF_path, 'scheda_Inventario_A5.pdf')
            if sys.platform == "darwin":
                subprocess.Popen(["open", filepath])
            elif sys.platform == "win32":
                os.startfile(filepath)
            else:  # linux
                subprocess.Popen(["xdg-open", filepath])

        except Exception as e:
            QMessageBox.critical(self, 'ERRORE',
                               f'Errore durante l\'esportazione: {str(e)}',
                               QMessageBox.StandardButton.Ok)

    def record_to_list(self, record):
        """Converte un record inventario in lista per il PDF generator"""
        return [
            record.id_invmat,
            record.sito,
            record.numero_inventario,
            record.tipo_reperto,
            record.criterio_schedatura,
            record.definizione,
            record.descrizione,
            record.area,
            record.us,
            record.lavato,
            record.nr_cassa,
            record.luogo_conservazione,
            record.stato_conservazione,
            record.datazione_reperto,
            record.elementi_reperto,
            record.misurazioni,
            record.rif_biblio,
            record.tecnologie,
            record.forme_minime,
            record.forme_massime,
            record.totale_frammenti,
            record.corpo_ceramico,
            record.rivestimento,
            record.diametro_orlo,
            record.peso,
            record.tipo,
            record.eve_orlo,
            record.repertato,
            record.diagnostico
        ]

    def exp_pdf_elenco_casse_main_experimental(self):
        ##campi per generare la lista da passare al pdf
        # experimental to finish
        # self.exp_pdf_elenco_casse_main()
        elenco_casse = self.index_elenco_casse()  # lista
        elenco_us = []  # lista
        diz_strutture_x_us = {}
        diz_us_x_cassa = {}
        diz_usstrutture_x_reperto = {}

        ##

        # QMessageBox.warning(self,'elenco casse',str(elenco_casse), QMessageBox.Ok)
        sito = str(self.comboBox_sito.currentText())
        elenco_casse.sort()

        # crea il dizionario cassa/us che contiene i valori {'cassa':[('area','us'), (area','us')]}

        for cassa in elenco_casse:
            rec_us = self.us_list_from_casse(sito, cassa)
            diz_us_x_cassa[cassa] = rec_us

        ##QMessageBox.warning(self,'us x cassa',str(diz_us_x_cassa), QMessageBox.Ok)

        # elenco us delle casse
        for us_list in list(diz_us_x_cassa.values()):
            for v in us_list:
                elenco_us.append((sito, v[1], v[2]))

                # crea il dizionario us/strutture che contiene i valori {'us':[('sito','struttura'), ('sito','struttura')]}

        for sing_us in elenco_us:
            rec_strutture = self.strutture_list_from_us(sing_us[0], sing_us[1], sing_us[2])
            diz_strutture_x_us[sing_us] = rec_strutture

            # QMessageBox.warning(self,'strutture x us',str(diz_strutture_x_us), QMessageBox.Ok)

            # crea il dizionario reperto/us/struttura che contiene i valori {'reperto':[('sito','area'us','struttura'), ('sito','area','us','struttura')]}

        for rec in range(len(self.DATA_LIST)):
            tup_key = (self.DATA_LIST[rec].sito, self.DATA_LIST[rec].area, self.DATA_LIST[rec].us)

            QMessageBox.warning(self, 'tk', str(tup_key), QMessageBox.StandardButton.Ok)
            QMessageBox.warning(self, 'tk', str(diz_strutture_x_us), QMessageBox.StandardButton.Ok)
            diz_usstrutture_x_reperto[self.DATA_LIST[rec].numero_inventario] = [self.DATA_LIST[rec].sito,
                                                                                self.DATA_LIST[rec].area,
                                                                                self.DATA_LIST[rec].us,
                                                                                diz_strutture_x_us[tup_key]
                                                                                ]
        ##QMessageBox.warning(self,'rep,us_str',str(diz_usstrutture_x_reperto), QMessageBox.Ok)

        # loop per la creazione dei data da passare al sistema di creazione pdf

        us_field = ""
        for cassa in elenco_casse:
            for us in diz_us_x_cassa[cassa]:
                QMessageBox.warning(self, 'Tus', str(us), QMessageBox.StandardButton.Ok)
                strutt_list = diz_strutture_x_us[us]
                strutt_text = "("
                for sing_str in strutt_list:
                    strutt_text += "," + str(sing_str[1])
                strutt_text = ")"
                if self.L=='it':
                    us_field += "US" + str(us[1]) + strutt_text + ", "
                elif self.L=='de':
                    us_field += "SE" + str(us[1]) + strutt_text + ", "
                else:
                    us_field += "SU" + str(us[1]) + strutt_text + ", "  
        QMessageBox.warning(self, 'us_field', str(us_field), QMessageBox.StandardButton.Ok)

    def index_elenco_casse(self):
        elenco_casse = []
        for rec in range(len(self.DATA_LIST)):
            elenco_casse.append(self.DATA_LIST[rec].nr_cassa)

        elenco_casse = self.UTILITY.remove_dup_from_list(elenco_casse)

        return elenco_casse

    def us_list_from_casse(self, sito, cassa):
        self.sito = sito
        self.cassa = cassa

        elenco_us_per_cassa = []

        search_dict = {'sito': "'" + str(self.sito) + "'",
                       'nr_cassa': "'" + str(self.cassa) + "'"
                       }

        search_dict = self.UTILITY.remove_empty_items_fr_dict(search_dict)

        res = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)

        for rec in range(len(res)):
            if bool(res[rec].us):
                elenco_us_per_cassa.append((res[rec].sito, res[rec].area, res[rec].us))
        return elenco_us_per_cassa

    def strutture_list_from_us(self, sito, area, us):
        self.sito = sito
        self.area = area
        self.us = us

        elenco_strutture_per_us = []

        search_dict = {'sito': "'" + str(self.sito) + "'",
                       'area': "'" + str(self.area) + "'",
                       'us': "'" + str(self.us) + "'"
                       }

        search_dict = self.UTILITY.remove_empty_items_fr_dict(search_dict)


        res = self.DB_MANAGER.query_bool(search_dict, "US")

        for rec in range(len(res)):
            if bool(res[rec].struttura):
                elenco_strutture_per_us.append((res[rec].sito, res[rec].struttura))
        return elenco_strutture_per_us

        # ********************************************************************************

    def data_error_check(self):
        test = 0
        EC = Error_check()

        area = self.comboBox_area.currentText()
        us = self.lineEdit_us.text()
        nr_cassa = self.lineEdit_nr_cassa.text()
        nr_inv = self.lineEdit_num_inv.text()

        if self.L=='it':
            if EC.data_is_empty(str(self.comboBox_sito.currentText())) == 0:
                QMessageBox.warning(self, "ATTENZIONE", "Campo Sito. \n Il campo non deve essere vuoto", QMessageBox.StandardButton.Ok)
                test = 1

            if EC.data_is_empty(str(self.lineEdit_num_inv.text())) == 0:
                QMessageBox.warning(self, "ATTENZIONE", "Campo Numero inventario \n Il campo non deve essere vuoto",
                                    QMessageBox.StandardButton.Ok)
                test = 1

            if nr_inv != "":
                if EC.data_is_int(nr_inv) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Campo Numero inventario\nIl valore deve essere di tipo numerico", QMessageBox.StandardButton.Ok)
                    test = 1

            # if area != "":
            #     if EC.data_is_int(area) == 0:
            #         QMessageBox.warning(self, "ATTENZIONE", "Campo Area.\nIl valore deve essere di tipo numerico",
            #                             QMessageBox.Ok)
            #         test = 1
            #
            # if us != "":
            #     if EC.data_is_int(us) == 0:
            #         QMessageBox.warning(self, "ATTENZIONE", "Campo US.\nIl valore deve essere di tipo numerico",
            #                             QMessageBox.Ok)
            #         test = 1

            # nr_cassa ora è un campo text, non serve più il controllo numerico
            # if nr_cassa != "":
            #     if EC.data_is_int(nr_cassa) == 0:
            #         QMessageBox.warning(self, "ATTENZIONE", "Campo Numero Cassa.\nIl valore deve essere di tipo numerico",
            #                             QMessageBox.Ok)
            #         test = 1
        elif self.L=='de':
            if EC.data_is_empty(str(self.comboBox_sito.currentText())) == 0:
                QMessageBox.warning(self, "ACHTUNG", " Feld Ausgrabungstätte \n Das Feld darf nicht leer sein", QMessageBox.StandardButton.Ok)
                test = 1

            if EC.data_is_empty(str(self.lineEdit_num_inv.text())) == 0:
                QMessageBox.warning(self, "ACHTUNG", " Feld Nr. Inv. \n Das Feld darf nicht leer sein", QMessageBox.StandardButton.Ok)
                test = 1

            if nr_inv != "":
                if EC.data_is_int(nr_inv) == 0:
                    QMessageBox.warning(self, "ACHTUNG", "Feld Nr. Inv. \n Der Wert muss numerisch eingegeben werden",
                                        QMessageBox.StandardButton.Ok)
                    test = 1

            # if area != "":
            #     if EC.data_is_int(area) == 0:
            #         QMessageBox.warning(self, "ACHTUNG", "Feld Areal \n Der Wert muss numerisch eingegeben werden",
            #                             QMessageBox.Ok)
            #         test = 1
            #
            # if us != "":
            #     if EC.data_is_int(us) == 0:
            #         QMessageBox.warning(self, "ACHTUNG", "Feld SE. \n Der Wert muss numerisch eingegeben werden",
            #                             QMessageBox.Ok)
            #         test = 1

            # nr_cassa ora è un campo text, non serve più il controllo numerico
            # if nr_cassa != "":
            #     if EC.data_is_int(nr_cassa) == 0:
            #         QMessageBox.warning(self, "ACHTUNG", "Feld Box \n Der Wert muss numerisch eingegeben werden",
            #                             QMessageBox.Ok)
            #         test = 1
        else:
            if EC.data_is_empty(str(self.comboBox_sito.currentText())) == 0:
                QMessageBox.warning(self, "WARNING", "Site Field \n The field must not be empty", QMessageBox.StandardButton.Ok)
                test = 1

            if EC.data_is_empty(str(self.lineEdit_num_inv.text())) == 0:
                QMessageBox.warning(self, "WARNING", "Nr. Inv. Field \n The field must not be empty", QMessageBox.StandardButton.Ok)
                test = 1

            if nr_inv != "":
                if EC.data_is_int(nr_inv) == 0:
                    QMessageBox.warning(self, "WARNING", "Area Field \n The value must be numerical",
                                        QMessageBox.StandardButton.Ok)
                    test = 1

            # if area != "":
            #     if EC.data_is_int(area) == 0:
            #         QMessageBox.warning(self, "WARNING", "Nr. Inv. Field \n The value must be numerical",
            #                             QMessageBox.Ok)
            #         test = 1
            #
            # if us != "":
            #     if EC.data_is_int(us) == 0:
            #         QMessageBox.warning(self, "WARNING", "SU Field \n The value must be numerical",
            #                             QMessageBox.Ok)
            #         test = 1

            # nr_cassa ora è un campo text, non serve più il controllo numerico
            # if nr_cassa != "":
            #     if EC.data_is_int(nr_cassa) == 0:
            #         QMessageBox.warning(self, "WARNING", "Box Field \n The value must be numerical",
            #                             QMessageBox.Ok)
            #         test = 1


        return test

    def insert_new_rec(self):
        ##elementi reperto
        elementi_reperto = self.table2dict("self.tableWidget_elementi_reperto")
        ##misurazioni
        misurazioni = self.table2dict("self.tableWidget_misurazioni")
        ##rif_biblio
        rif_biblio = self.table2dict("self.tableWidget_rif_biblio")
        ##tecnologie
        tecnologie = self.table2dict("self.tableWidget_tecnologie")
        ##negative
        negative = self.table2dict("self.tableWidget_negative")
        ##diapositive
        diapositive = self.table2dict("self.tableWidget_diapositive")

        try:
            if self.lineEdit_num_inv.text() == "":
                inv =None
            else:
                inv = int(self.lineEdit_num_inv.text())

            if self.comboBox_area.currentText() == "":
                area =''
            else:
                area = self.comboBox_area.currentText()

            if self.lineEdit_us.text() == "":
                us =''
            else:
                us = str(self.lineEdit_us.text())

            if self.lineEdit_nr_cassa.text() == "":
                nr_cassa =None
            else:
                nr_cassa = str(self.lineEdit_nr_cassa.text())

            if self.lineEditFormeMin.text() == "":
                forme_minime =None
            else:
                forme_minime = int(self.lineEditFormeMin.text())

            if self.lineEditFormeMax.text() == "":
                forme_massime =None
            else:
                forme_massime = int(self.lineEditFormeMax.text())

            if self.lineEditTotFram.text() == "":
                totale_frammenti =None
            else:
                totale_frammenti = int(self.lineEditTotFram.text())

            if self.lineEdit_diametro_orlo.text() == "":
                diametro_orlo = None
            else:
                diametro_orlo = float(self.lineEdit_diametro_orlo.text())

            if self.lineEdit_peso.text() == "":
                peso = None
            else:
                peso = float(self.lineEdit_peso.text())

            if self.lineEdit_eve_orlo.text() == "":
                eve_orlo = None
            else:
                eve_orlo = float(self.lineEdit_eve_orlo.text())


            if self.lineEdit_n_reperto.text() == "":
                n_reperto =None
            else:
                n_reperto = int(self.lineEdit_n_reperto.text())

            # Get values for new fields
            schedatore = str(self.comboBox_compilatore.currentText())
            date_scheda = self.mDateTimeEdit_date.dateTime().toString('yyyy-MM-dd')
            punto_rinv = str(self.lineEdit_punto_rinv.text())

            # Get quota value if widget exists
            quota_usm = None
            if hasattr(self, 'lineEdit_quota') and self.lineEdit_quota.text():
                try:
                    quota_usm = float(self.lineEdit_quota.text())
                except:
                    quota_usm = None

            # Get unita_misura_quota if widget exists
            unita_misura_quota = None
            if hasattr(self, 'comboBox_unita_quota'):
                unita_misura_quota = str(self.comboBox_unita_quota.currentText()) if self.comboBox_unita_quota.currentText() else 'm s.l.m.'

            data = self.DB_MANAGER.insert_values_reperti(
                self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, self.ID_TABLE) + 1,  # 0 - id_invmat
                str(self.comboBox_sito.currentText()),  # 1 - sito
                inv,  # 2 - numero_inventario
                str(self.comboBox_tipo_reperto.currentText()),  # 3 - tipo_reperto
                str(self.comboBox_criterio_schedatura.currentText()),  # 4 - criterio_schedatura
                str(self.comboBox_definizione.currentText()),  # 5 - definizione
                str(self.textEdit_descrizione_reperto.toPlainText()),  # 6 - descrizione
                area,  # 7 - area
                us,  # 8 - us
                str(self.comboBox_lavato.currentText()),  # 9 - lavato
                nr_cassa,  # 10 - nr_cassa
                str(self.comboBox_magazzino.currentText()),  # 11 - luogo_conservazione
                str(self.comboBox_conservazione.currentText()),  # 12 - stato_conservazione
                str(self.comboBox_datazione.currentText()),  # 13 - datazione_reperto
                str(elementi_reperto),  # 14 - elementi_reperto
                str(misurazioni),  # 15 - misurazioni
                str(rif_biblio),  # 16 - rif_biblio
                str(tecnologie),  # 17 - tecnologie
                forme_minime,  # 18 - forme_minime
                forme_massime,  # 19 - forme_massime
                totale_frammenti,  # 20 - totale_frammenti
                str(self.lineEditCorpoCeramico.text()),  # 21 - corpo_ceramico
                str(self.lineEditRivestimento.text()),  # 22 - rivestimento
                diametro_orlo,  # 23 - diametro_orlo
                peso,  # 24 - peso
                str(self.comboBox_tipologia.currentText()),  # 25 - tipo
                eve_orlo,  # 26 - eve_orlo
                str(self.comboBox_repertato.currentText()),  # 27 - repertato
                str(self.comboBox_diagnostico.currentText()),  # 28 - diagnostico
                n_reperto,  # 29 - n_reperto
                str(self.comboBox_tipo_contenitore.currentText()),  # 30 - tipo_contenitore
                str(self.comboBox_struttura.currentText()),  # 31 - struttura
                str(self.comboBox_year.currentText()),  # 32 - years
                schedatore,  # 33 - schedatore
                date_scheda,  # 34 - date_scheda
                punto_rinv,  # 35 - punto_rinv
                str(negative),  # 36 - negativo_photo
                str(diapositive),  # 37 - diapositiva
                quota_usm,  # 38 - quota_usm
                unita_misura_quota,  # 39 - unita_misura_quota
                None,  # 40 - photo_id (auto-populated)
                None,  # 41 - drawing_id (auto-populated)
            )


            try:
                # duplicate=[]
                # duplicate2=[]
                # for value in range(len(self.DATA_LIST)):
                    # duplicate.append(value.n_reperto)
                    # duplicate2.append(value.numero_inventario)


                # if len(duplicate)!=len(set(duplicate)):



                    # QMessageBox.warning(self, "Error", str(len(set(duplicate))), QMessageBox.Ok)
                    # return 0

                # else:
                self.DB_MANAGER.insert_data_session(data)

                return 1
            except Exception as e:
                e_str = str(e)
                if e_str.__contains__("IntegrityError"):

                    if self.L=='it':
                        msg = "Numero reperto o inventario gia' presente nel database"

                        QMessageBox.warning(self, "Error", "Errore: valore duplicato\n" + str(msg), QMessageBox.StandardButton.Ok)

                    elif self.L=='de':
                        msg = self.ID_TABLE + " bereits in der Datenbank"
                        QMessageBox.warning(self, "Error", "Error " + str(msg), QMessageBox.StandardButton.Ok)  
                    else:
                        msg = self.ID_TABLE + " exist in db"
                        QMessageBox.warning(self, "Error", "Error " + str(msg), QMessageBox.StandardButton.Ok)  
                else:
                    msg = e
                    QMessageBox.warning(self, "Error", "Error 1 \n" + str(msg), QMessageBox.StandardButton.Ok)
                return 0

        except Exception as e:
            QMessageBox.warning(self, "Error", "Error 2 \n" + str(e), QMessageBox.StandardButton.Ok)
            return 0

            # insert new row into tableWidget

    def on_pushButton_insert_row_elementi_pressed(self):
        self.insert_new_row('self.tableWidget_elementi_reperto')

    def on_pushButton_remove_row_elementi_pressed(self):
        self.remove_row('self.tableWidget_elementi_reperto')

        # misurazioni

    def on_pushButton_insert_row_misure_pressed(self):
        self.insert_new_row('self.tableWidget_misurazioni')

    def on_pushButton_remove_row_misure_pressed(self):
        self.remove_row('self.tableWidget_misurazioni')

        # tecnologie

    def on_pushButton_insert_row_tecnologie_pressed(self):
        self.insert_new_row('self.tableWidget_tecnologie')

    def on_pushButton_remove_row_tecnologie_pressed(self):
        self.remove_row('self.tableWidget_tecnologie')

        # rif biblio

    def on_pushButton_insert_row_rif_biblio_pressed(self):
        self.insert_new_row('self.tableWidget_rif_biblio')

    def on_pushButton_remove_row_rif_biblio_pressed(self):
        self.remove_row('self.tableWidget_rif_biblio')

    def on_pushButton_insert_row_negativi_pressed(self):
        self.insert_new_row('self.tableWidget_negative')

    def on_pushButton_remove_row_negativi_pressed(self):
        self.remove_row('self.tableWidget_negative')

    def on_pushButton_insert_row_diapo_pressed(self):
        self.insert_new_row('self.tableWidget_diapositive')

    def on_pushButton_remove_row_diapo_pressed(self):
        self.remove_row('self.tableWidget_diapositive')

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

    def on_pushButton_view_all_2_pressed(self):
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
            pass# if self.toolButtonPreviewMedia.isChecked():
                # self.loadMediaPreview(1)
        else:
            try:
                self.empty_fields()
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                self.fill_fields(0)
                self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
                # if self.toolButtonPreviewMedia.isChecked():
                    # self.loadMediaPreview(0)
            except :
                pass#QMessageBox.warning(self, "Error", str(e), QMessageBox.Ok)

    def on_pushButton_last_rec_pressed(self):
        if self.check_record_state() == 1:
            pass# if self.toolButtonPreviewMedia.isChecked():
                # self.loadMediaPreview(0)
        else:

            try:
                self.empty_fields()
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), len(self.DATA_LIST) - 1
                self.fill_fields(self.REC_CORR)
                self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
                # if self.toolButtonPreviewMedia.isChecked():
                    # self.loadMediaPreview(0)
            except :
                pass#QMessageBox.warning(self, "Error", str(e), QMessageBox.Ok)

    def on_pushButton_prev_rec_pressed(self):
        #self.setnone()
        if self.check_record_state() == 1:
            pass
        else:
            self.REC_CORR = self.REC_CORR - 1
            if self.REC_CORR <= -1:
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
                except:# Exception as e:
                    pass#QMessageBox.warning(self, "Error", str(e), QMessageBox.Ok)

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
                except:# Exception as e:
                    pass#QMessageBox.warning(self, "Error", str(e), QMessageBox.Ok)

    def update_tma_inventario_field(self, sito, n_reperto, action='remove'):
        """Update TMA inventario field when n_reperto is added or removed"""
        try:
            from ..modules.db.structures.Tma_table import Tma_table

            # Query all TMA records for this site
            search_dict = {'sito': sito}
            tma_records = self.DB_MANAGER.query_bool(search_dict, 'TMA_MATERIALI_ARCHEOLOGICI')

            for tma in tma_records:
                if tma.inventario:
                    inventario_list = str(tma.inventario).split(',')
                    inventario_list = [x.strip() for x in inventario_list]

                    if action == 'remove':
                        # Remove n_reperto from the list
                        if n_reperto in inventario_list:
                            inventario_list.remove(n_reperto)
                    elif action == 'add':
                        # Add n_reperto to the list
                        if n_reperto not in inventario_list:
                            inventario_list.append(n_reperto)

                    # Update the inventario field
                    new_inventario = ', '.join(inventario_list) if inventario_list else ''

                    # Update the record in the database
                    update_dict = {'inventario': new_inventario}
                    self.DB_MANAGER.update(Tma_table, tma.id, update_dict, 'id')

            QgsMessageLog.logMessage(f"Updated TMA inventario field for site {sito}, n_reperto {n_reperto}", "PyArchInit", Qgis.Info)

        except Exception as e:
            QgsMessageLog.logMessage(f"Error updating TMA inventario field: {str(e)}", "PyArchInit", Qgis.Warning)

    def on_pushButton_delete_pressed(self):

        if self.L=='it':
            msg = QMessageBox.warning(self, "Attenzione!!!",
                                      "Vuoi veramente eliminare il record? \n L'azione è irreversibile",
                                      QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            if msg == QMessageBox.StandardButton.Cancel:
                QMessageBox.warning(self, "Messagio!!!", "Azione Annullata!")
            else:
                try:
                    # Get n_reperto before deleting to update TMA records
                    n_reperto_to_remove = None
                    sito = None
                    if hasattr(self.DATA_LIST[self.REC_CORR], 'n_reperto') and self.DATA_LIST[self.REC_CORR].n_reperto:
                        n_reperto_to_remove = str(self.DATA_LIST[self.REC_CORR].n_reperto)
                        sito = str(self.DATA_LIST[self.REC_CORR].sito)

                    id_to_delete = getattr(self.DATA_LIST[self.REC_CORR], self.ID_TABLE)
                    self.DB_MANAGER.delete_one_record(self.TABLE_NAME, self.ID_TABLE, id_to_delete)

                    # Update TMA records that reference this n_reperto
                    if n_reperto_to_remove and sito:
                        self.update_tma_inventario_field(sito, n_reperto_to_remove, action='remove')

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
                    # Get n_reperto before deleting to update TMA records
                    n_reperto_to_remove = None
                    sito = None
                    if hasattr(self.DATA_LIST[self.REC_CORR], 'n_reperto') and self.DATA_LIST[self.REC_CORR].n_reperto:
                        n_reperto_to_remove = str(self.DATA_LIST[self.REC_CORR].n_reperto)
                        sito = str(self.DATA_LIST[self.REC_CORR].sito)

                    id_to_delete = getattr(self.DATA_LIST[self.REC_CORR], self.ID_TABLE)
                    self.DB_MANAGER.delete_one_record(self.TABLE_NAME, self.ID_TABLE, id_to_delete)

                    # Update TMA records that reference this n_reperto
                    if n_reperto_to_remove and sito:
                        self.update_tma_inventario_field(sito, n_reperto_to_remove, action='remove')

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
                    # Get n_reperto before deleting to update TMA records
                    n_reperto_to_remove = None
                    sito = None
                    if hasattr(self.DATA_LIST[self.REC_CORR], 'n_reperto') and self.DATA_LIST[self.REC_CORR].n_reperto:
                        n_reperto_to_remove = str(self.DATA_LIST[self.REC_CORR].n_reperto)
                        sito = str(self.DATA_LIST[self.REC_CORR].sito)

                    id_to_delete = getattr(self.DATA_LIST[self.REC_CORR], self.ID_TABLE)
                    self.DB_MANAGER.delete_one_record(self.TABLE_NAME, self.ID_TABLE, id_to_delete)

                    # Update TMA records that reference this n_reperto
                    if n_reperto_to_remove and sito:
                        self.update_tma_inventario_field(sito, n_reperto_to_remove, action='remove')

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
                    #self.setComboBoxEditable(['self.comboBox_sito'], 1)
                    self.setComboBoxEnable(['self.comboBox_sito'], 'False')
                    self.setComboBoxEditable(['self.comboBox_lavato'], 1)
                    self.setComboBoxEnable(['self.comboBox_lavato'], 'True')
                    self.setComboBoxEnable(['self.lineEdit_num_inv'], 'True')
                    self.setComboBoxEnable(["self.textEdit_descrizione_reperto"], "False")
                    self.setTableEnable(
                        ["self.tableWidget_elementi_reperto", "self.tableWidget_misurazioni", "self.tableWidget_rif_biblio",
                         "self.tableWidget_tecnologie"], "False")
                    ###
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.set_rec_counter('', '')
                    self.label_sort.setText(self.SORTED_ITEMS["n"])
                    #self.charge_list()
                    self.empty_fields_nosite()
                else:
                    self.BROWSE_STATUS = "f"
                    ###
                    self.setComboBoxEditable(['self.comboBox_sito'], 1)
                    self.setComboBoxEnable(['self.comboBox_sito'], 'True')
                    self.setComboBoxEditable(['self.comboBox_lavato'], 1)
                    self.setComboBoxEnable(['self.comboBox_lavato'], 'True')
                    self.setComboBoxEnable(['self.lineEdit_num_inv'], 'True')
                    self.setComboBoxEnable(["self.textEdit_descrizione_reperto"], "False")
                    self.setTableEnable(
                        ["self.tableWidget_elementi_reperto", "self.tableWidget_misurazioni", "self.tableWidget_rif_biblio",
                         "self.tableWidget_tecnologie"], "False")
                    ###
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.set_rec_counter('', '')
                    self.label_sort.setText(self.SORTED_ITEMS["n"])
                    self.charge_list()
                    self.empty_fields()

    def on_pushButton_search_go_pressed(self):
        #self.lineEdit_n_reperto.setText('')
        check_for_buttons = 0
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
            ##scavato
            if self.lineEdit_num_inv.text() != "":
                numero_inventario = int(self.lineEdit_num_inv.text())
            else:
                numero_inventario = ""

            if self.comboBox_area.currentText() != "":
                area = self.comboBox_area.currentText()
            else:
                area = ""

            if self.lineEdit_us.text() != "":
                us = int(self.lineEdit_us.text())
            else:
                us = ""

            if self.lineEdit_nr_cassa.text() != "":
                nr_cassa = str(self.lineEdit_nr_cassa.text())
            else:
                nr_cassa = ""

            if self.lineEditFormeMin.text() != "":
                forme_minime = int(self.lineEditFormeMin.text())
            else:
                forme_minime = ""

            if self.lineEditFormeMax.text() != "":
                forme_massime = int(self.lineEditFormeMax.text())
            else:
                forme_massime = ""

            if self.lineEditTotFram.text() != "":
                totale_frammenti = int(self.lineEditTotFram.text())
            else:
                totale_frammenti = ""

            if self.lineEdit_diametro_orlo.text() != "":
                diametro_orlo = float(self.lineEdit_diametro_orlo.text())
            else:
                diametro_orlo = ""

            if self.lineEdit_peso.text() != "":
                peso = float(self.lineEdit_peso.text())
            else:
                peso = ""

            if self.lineEdit_eve_orlo.text() != "":
                eve_orlo = float(self.lineEdit_eve_orlo.text())
            else:
                eve_orlo = ""

            if self.lineEdit_n_reperto.text() != "":
                n_reperto = int(self.lineEdit_n_reperto.text())
            else:
                n_reperto = ""

            search_dict = {
                self.TABLE_FIELDS[0]: "'" + str(self.comboBox_sito.currentText()) + "'",
                self.TABLE_FIELDS[1]: numero_inventario,
                self.TABLE_FIELDS[2]: "'" + str(self.comboBox_tipo_reperto.currentText()) + "'",
                self.TABLE_FIELDS[3]: "'" + str(self.comboBox_criterio_schedatura.currentText()) + "'",
                self.TABLE_FIELDS[4]: "'" + str(self.comboBox_definizione.currentText()) + "'",
                self.TABLE_FIELDS[5]: "'" + str(self.textEdit_descrizione_reperto.toPlainText()) + "'",
                self.TABLE_FIELDS[6]: "'" + str(self.comboBox_area.currentText()) + "'",
                self.TABLE_FIELDS[7]: "'" + str(self.lineEdit_us.text()) + "'",
                self.TABLE_FIELDS[9]: nr_cassa,
                self.TABLE_FIELDS[10]: "'" + str(self.comboBox_magazzino.currentText()) + "'",
                self.TABLE_FIELDS[11]: "'" + str(self.comboBox_conservazione.currentText()) + "'",
                self.TABLE_FIELDS[12]: "'" + str(self.comboBox_datazione.currentText()) + "'",
                self.TABLE_FIELDS[17]: forme_minime,
                self.TABLE_FIELDS[18]: forme_massime,
                self.TABLE_FIELDS[19]: totale_frammenti,
                self.TABLE_FIELDS[20]: "'" + str(self.lineEditCorpoCeramico.text()) + "'",
                self.TABLE_FIELDS[21]: "'" + str(self.lineEditRivestimento.text()) + "'",
                self.TABLE_FIELDS[22]: diametro_orlo,
                self.TABLE_FIELDS[23]: peso,
                self.TABLE_FIELDS[24]: "'" + str(self.comboBox_tipo_reperto.currentText()) + "'",
                self.TABLE_FIELDS[25]: eve_orlo,
                self.TABLE_FIELDS[26]: "'" + str(self.comboBox_repertato.currentText()) + "'",
                self.TABLE_FIELDS[27]: "'" + str(self.comboBox_diagnostico.currentText()) + "'",
                self.TABLE_FIELDS[28]: n_reperto,
                self.TABLE_FIELDS[29]: "'" + str(self.comboBox_tipo_contenitore.currentText()) + "'",
                self.TABLE_FIELDS[30]: "'" + str(self.comboBox_struttura.currentText()) + "'",
                self.TABLE_FIELDS[31]: "'" + str(self.comboBox_year.currentText()) + "'",
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
                        QMessageBox.warning(self, "WARNING", "No record found!", QMessageBox.StandardButton.Ok)

                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]

                    self.fill_fields(self.REC_CORR)

                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])

                    self.setComboBoxEditable(["self.comboBox_sito"], 1)
                    self.setComboBoxEditable(["self.comboBox_lavato"], 1)
                    self.setComboBoxEnable(["self.comboBox_sito"], "False")
                    self.setComboBoxEnable(["self.lineEdit_num_inv"], "False")
                    self.setComboBoxEnable(["self.textEdit_descrizione_reperto"], "True")
                    self.setTableEnable(["self.tableWidget_elementi_reperto", "self.tableWidget_misurazioni",
                                         "self.tableWidget_rif_biblio",
                                         "self.tableWidget_tecnologie"], "True")

                    check_for_buttons = 1

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
                            if self.toolButtonGis.isChecked():
                                self.pyQGIS.charge_reperti_layers(self.DATA_LIST)
                        else:
                            strings = ("Sono stati trovati", self.REC_TOT, "records")
                            if self.toolButtonGis.isChecked():
                                self.pyQGIS.charge_reperti_layers(self.DATA_LIST)
                    elif self.L=='de':
                        if self.REC_TOT == 1:
                            strings = ("Es wurde gefunden", self.REC_TOT, "record")
                            if self.toolButtonGis.isChecked():
                                self.pyQGIS.charge_reperti_layers(self.DATA_LIST)
                        else:
                            strings = ("Sie wurden gefunden", self.REC_TOT, "records")
                            if self.toolButtonGis.isChecked():
                                self.pyQGIS.charge_reperti_layers(self.DATA_LIST)
                    else:
                        if self.REC_TOT == 1:
                            strings = ("It has been found", self.REC_TOT, "record")
                            if self.toolButtonGis.isChecked():
                                self.pyQGIS.charge_reperti_layers(self.DATA_LIST)
                        else:
                            strings = ("They have been found", self.REC_TOT, "records")
                            if self.toolButtonGis.isChecked():
                                self.pyQGIS.charge_reperti_layers(self.DATA_LIST)

                    self.setComboBoxEditable(["self.comboBox_sito"], 1)
                    self.setComboBoxEditable(["self.comboBox_lavato"], 1)

                    self.setComboBoxEnable(['self.lineEdit_num_inv'], "False")
                    self.setComboBoxEnable(['self.comboBox_sito'], "False")
                    self.setComboBoxEnable(["self.textEdit_descrizione_reperto"], "True")
                    self.setTableEnable(["self.tableWidget_elementi_reperto", "self.tableWidget_misurazioni",
                                         "self.tableWidget_rif_biblio",
                                         "self.tableWidget_tecnologie"], "True")

                    check_for_buttons = 1

                    QMessageBox.warning(self, "Message", "%s %d %s" % strings, QMessageBox.StandardButton.Ok)

        if check_for_buttons == 1:
            self.enable_button_search(1)

    def on_pushButton_tot_fram_pressed(self):
        if self.L=='it':
            self.update_tot_frammenti(QMessageBox.warning(self, 'ATTENZIONE',
                                                          "Vuoi aggiornare tutti i frammenti (OK), oppure solo il record corrente (Cancel)?",
                                                          QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))
        elif self.L=='de':
            self.update_tot_frammenti(QMessageBox.warning(self, 'Achtung',
                                                          "Möchten Sie alle Fragmente (OK) oder nur den aktuellen Datensatz (Abbrechen) aktualisieren?",
                                                          QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))

        else:
            self.update_tot_frammenti(QMessageBox.warning(self, 'Warning',
                                                          "Do you want to update all fragments (OK), or just the current record (Cancel)?",
                                                          QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))
        # blocco per quantificare dalla tabella interna il numero totale di frammenti

    def update_tot_frammenti(self, c):
        if c == QMessageBox.StandardButton.Ok:
            for i in range(len(self.DATA_LIST)):
                try:
                    temp_dataset = ()
                    id_invmat = self.DATA_LIST[i].id_invmat

                    # Safely handle elementi_reperto
                    if hasattr(self.DATA_LIST[i], 'elementi_reperto') and self.DATA_LIST[i].elementi_reperto:
                        try:
                            elementi_reperto = eval(self.DATA_LIST[i].elementi_reperto)
                            if bool(elementi_reperto):
                                tot_framm = 0
                                for elrep in elementi_reperto:
                                    if elrep[1] == 'frammenti' or elrep[1] == 'frammento'or elrep[1] == 'fragment' or elrep[1] == 'fragments':
                                        try:
                                            tot_framm += int(elrep[2])
                                        except:
                                            pass
                                self.DB_MANAGER.update(self.MAPPER_TABLE_CLASS, self.ID_TABLE, [int(id_invmat)],
                                                   ['totale_frammenti'], [tot_framm])
                        except Exception as e:
                            QMessageBox.warning(self, "Error", f"Error processing elementi_reperto: {str(e)}", QMessageBox.StandardButton.Ok)
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Error processing record {i}: {str(e)}", QMessageBox.StandardButton.Ok)

            # Get id directly without using eval
            if not self.DATA_LIST or self.REC_CORR >= len(self.DATA_LIST):
                return

            if hasattr(self.DATA_LIST[int(self.REC_CORR)], self.ID_TABLE):
                id_val = getattr(self.DATA_LIST[int(self.REC_CORR)], self.ID_TABLE)
                search_dict = {
                    'id_invmat': "'" + str(id_val) + "'"}
                records = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
                if records and len(records) > 0:
                    self.lineEditTotFram.setText(str(records[0].totale_frammenti))
        else:
            lista_valori = self.table2dict('self.tableWidget_elementi_reperto')

            tot_framm = 0
            for sing_fr in lista_valori:
                if sing_fr[1] == 'frammenti' or sing_fr[1] == 'frammento' or sing_fr[1] == 'fragment' or sing_fr[1] == 'fragments':
                    try:
                        tot_framm += int(sing_fr[2])
                    except:
                        pass

            self.lineEditTotFram.setText(str(tot_framm))

    def update_if(self, msg):
        rec_corr = self.REC_CORR
        if msg == QMessageBox.StandardButton.Ok:
            test = self.update_record()
            if test == 1:
                id_list = []
                for i in self.DATA_LIST:
                    # Get id directly without using eval
                    if hasattr(i, self.ID_TABLE):
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

    def update_record(self):
        try:
            # Check if DATA_LIST exists and REC_CORR is valid
            if not self.DATA_LIST or self.REC_CORR >= len(self.DATA_LIST):
                return 0

            # Get id directly without using eval
            if hasattr(self.DATA_LIST[self.REC_CORR], self.ID_TABLE):
                id_val = int(getattr(self.DATA_LIST[self.REC_CORR], self.ID_TABLE))
                self.DB_MANAGER.update(self.MAPPER_TABLE_CLASS,
                                    self.ID_TABLE,
                                    [id_val],
                                    self.TABLE_FIELDS,
                                    self.rec_toupdate())
                return 1
            else:
                return 0
        except Exception as e:
            error_msg = str(e)

            # Check if we have a permission handler to handle permission errors
            if hasattr(self, 'permission_handler') and self.permission_handler.handle_permission_error(e, 'UPDATE'):
                return 0

            # Determine the actual error type
            if 'InsufficientPrivilege' in str(type(e)) or 'permission denied' in error_msg.lower():
                # Permission error
                if self.L == 'it':
                    QMessageBox.warning(self, "Errore Permessi",
                                        "Non hai i permessi per modificare questo record.", QMessageBox.StandardButton.Ok)
                elif self.L == 'de':
                    QMessageBox.warning(self, "Berechtigungsfehler",
                                        "Sie haben keine Berechtigung, diesen Datensatz zu ändern.", QMessageBox.StandardButton.Ok)
                else:
                    QMessageBox.warning(self, "Permission Error",
                                        "You don't have permission to modify this record.", QMessageBox.StandardButton.Ok)
            elif 'encode' in error_msg.lower() or 'decode' in error_msg.lower() or 'codec' in error_msg.lower():
                # Actual encoding error
                save_file = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_Report_folder")
                file_ = os.path.join(save_file, 'error_encoding_data_recover.txt')
                with open(file_, "a") as fh:
                    print(f"{datetime.now()}: {error_msg}", file=fh)

                if self.L == 'it':
                    QMessageBox.warning(self, "Messaggio",
                                        "Problema di encoding: sono stati inseriti accenti o caratteri non accettati dal database. Verrà fatta una copia dell'errore con i dati che puoi recuperare nella cartella pyarchinit_Report_Folder", QMessageBox.StandardButton.Ok)
                elif self.L == 'de':
                    QMessageBox.warning(self, "Message",
                                        "Kodierungsproblem: Es wurden Akzente oder Zeichen eingegeben, die von der Datenbank nicht akzeptiert werden. Es wird eine Kopie des Fehlers mit den Daten erstellt, die Sie im pyarchinit_Report_Ordner abrufen können", QMessageBox.StandardButton.Ok)
                else:
                    QMessageBox.warning(self, "Message",
                                        "Encoding problem: accents or characters not accepted by the database were entered. A copy of the error will be made with the data you can retrieve in the pyarchinit_Report_Folder", QMessageBox.StandardButton.Ok)
            else:
                # Generic database error
                if self.L == 'it':
                    QMessageBox.warning(self, "Errore Database",
                                        f"Errore durante l'aggiornamento del record: {error_msg}", QMessageBox.StandardButton.Ok)
                elif self.L == 'de':
                    QMessageBox.warning(self, "Datenbankfehler",
                                        f"Fehler beim Aktualisieren des Datensatzes: {error_msg}", QMessageBox.StandardButton.Ok)
                else:
                    QMessageBox.warning(self, "Database Error",
                                        f"Error updating record: {error_msg}", QMessageBox.StandardButton.Ok)
            return 0

    def charge_struttura(self):
        try:
            sito = str(self.comboBox_sito.currentText())
            area = str(self.comboBox_area.currentText())
            us = str(self.lineEdit_us.text())

            # Check if DATA_LIST exists and REC_CORR is valid
            if not self.DATA_LIST or self.REC_CORR >= len(self.DATA_LIST):
                return

            # Get area and us directly without using eval
            if hasattr(self.DATA_LIST[int(self.REC_CORR)], 'area'):
                area_val = str(self.DATA_LIST[int(self.REC_CORR)].area)
            else:
                area_val = ""

            if hasattr(self.DATA_LIST[int(self.REC_CORR)], 'us'):
                us_val = str(self.DATA_LIST[int(self.REC_CORR)].us)
            else:
                us_val = ""

            search_dict = {
                'sito': "'" + sito + "'",
                'area': "'" + area_val + "'",
                'us': "'" + us_val + "'"
            }

            struttura_vl = self.DB_MANAGER.query_bool(search_dict, 'US')
            struttura_list = []
            for i in range(len(struttura_vl)):
                struttura_list.append(str(struttura_vl[i].struttura))
            try:
                struttura_vl.remove('')
            except:
                pass
            self.comboBox_struttura.clear()
            self.comboBox_struttura.addItems(self.UTILITY.remove_dup_from_list(struttura_list))
            if self.STATUS_ITEMS[self.BROWSE_STATUS] == "Trova" or "Finden" or "Find":
                self.comboBox_struttura.setEditText("")
            elif self.STATUS_ITEMS[self.BROWSE_STATUS] == "Usa" or "Aktuell " or "Current":
                if len(self.DATA_LIST) > 0:
                    try:
                        self.comboBox_struttura.setEditText(self.DATA_LIST[self.rec_num].struttura)
                    except:
                        pass  # non vi sono periodi per questo scavo

        except Exception as e:
            QMessageBox.warning(self, "Error", str(e), QMessageBox.StandardButton.Ok)
    # charge_datazione removed - now datazione is loaded from thesaurus in charge_list

    def rec_toupdate(self):
        rec_to_update = self.UTILITY.pos_none_in_list(self.DATA_LIST_REC_TEMP)
        # rec_to_update = rec_to_update[:2]
        return rec_to_update

        # custom functions

    ######old system
    ##  def charge_records(self):
    ##      self.DATA_LIST = []
    ##      id_list = []
    ##      for i in self.DB_MANAGER.query(eval(self.MAPPER_TABLE_CLASS)):
    ##          id_list.append(eval("i."+ self.ID_TABLE))
    ##
    ##      temp_data_list = self.DB_MANAGER.query_sort(id_list, [self.ID_TABLE], 'asc', self.MAPPER_TABLE_CLASS, self.ID_TABLE)
    ##      for i in temp_data_list:
    ##          self.DATA_LIST.append(i)


    def charge_records(self):
        self.DATA_LIST = []

        if self.DB_SERVER == 'sqlite':
            for i in self.DB_MANAGER.query(self.MAPPER_TABLE_CLASS):
                self.DATA_LIST.append(i)
        else:
            id_list = []
            for i in self.DB_MANAGER.query(self.MAPPER_TABLE_CLASS):
                # Get id directly without using eval
                if hasattr(i, self.ID_TABLE):
                    id_list.append(getattr(i, self.ID_TABLE))

            temp_data_list = self.DB_MANAGER.query_sort(id_list, [self.ID_TABLE], 'asc', self.MAPPER_TABLE_CLASS,
                                                        self.ID_TABLE)
            for i in temp_data_list:
                self.DATA_LIST.append(i)

    def fill_fields(self, n=0):
        self.rec_num = n
        try:
            if str(self.DATA_LIST[self.rec_num].numero_inventario) == 'None':
                num_inv = ''
            else:
                num_inv = str(self.DATA_LIST[self.rec_num].numero_inventario)

            if str(self.DATA_LIST[self.rec_num].area) == 'None':
                area = ''
            else:
                area = str(self.DATA_LIST[self.rec_num].area)

            if str(self.DATA_LIST[self.rec_num].us) == 'None':
                us = ''
            else:
                us = str(self.DATA_LIST[self.rec_num].us)

            if str(self.DATA_LIST[self.rec_num].nr_cassa) == 'None':
                nr_cassa = ''
            else:
                nr_cassa = str(self.DATA_LIST[self.rec_num].nr_cassa)

            if str(self.DATA_LIST[self.rec_num].forme_minime) == 'None':
                forme_minime = ''
            else:
                forme_minime = str(self.DATA_LIST[self.rec_num].forme_minime)

            if str(self.DATA_LIST[self.rec_num].forme_massime) == 'None':
                forme_massime = ''
            else:
                forme_massime = str(self.DATA_LIST[self.rec_num].forme_massime)

            if str(self.DATA_LIST[self.rec_num].totale_frammenti) == 'None':
                totale_frammenti = ''
            else:
                totale_frammenti = str(self.DATA_LIST[self.rec_num].totale_frammenti)

            if str(self.DATA_LIST[self.rec_num].n_reperto) == 'None':
                n_reperto = ''
            else:
                n_reperto = str(self.DATA_LIST[self.rec_num].n_reperto)

            self.comboBox_sito.setEditText(self.DATA_LIST[self.rec_num].sito)
            self.lineEdit_num_inv.setText(num_inv)
            self.comboBox_tipo_reperto.setEditText(self.DATA_LIST[self.rec_num].tipo_reperto)
            self.comboBox_criterio_schedatura.setEditText(self.DATA_LIST[self.rec_num].criterio_schedatura)
            self.comboBox_definizione.setEditText(self.DATA_LIST[self.rec_num].definizione)
            self.textEdit_descrizione_reperto.setText(self.DATA_LIST[self.rec_num].descrizione)
            self.comboBox_area.setEditText(area)
            self.lineEdit_us.setText(us)
            self.comboBox_lavato.setEditText(str(self.DATA_LIST[self.rec_num].lavato))
            self.lineEdit_nr_cassa.setText(nr_cassa)
            self.comboBox_magazzino.setEditText(str(self.DATA_LIST[self.rec_num].luogo_conservazione))
            self.comboBox_conservazione.setEditText(str(self.DATA_LIST[self.rec_num].stato_conservazione))
            self.comboBox_datazione.setEditText(str(self.DATA_LIST[self.rec_num].datazione_reperto))

            self.tableInsertData("self.tableWidget_elementi_reperto", self.DATA_LIST[self.rec_num].elementi_reperto)
            self.tableInsertData("self.tableWidget_misurazioni", self.DATA_LIST[self.rec_num].misurazioni)
            self.tableInsertData("self.tableWidget_rif_biblio", self.DATA_LIST[self.rec_num].rif_biblio)
            self.tableInsertData("self.tableWidget_tecnologie", self.DATA_LIST[self.rec_num].tecnologie)

            self.lineEditFormeMin.setText(forme_minime)
            self.lineEditFormeMax.setText(forme_massime)
            self.lineEditTotFram.setText(totale_frammenti)
            self.lineEditRivestimento.setText(str(self.DATA_LIST[self.rec_num].rivestimento))
            self.lineEditCorpoCeramico.setText(str(self.DATA_LIST[self.rec_num].corpo_ceramico))

            if self.DATA_LIST[self.rec_num].diametro_orlo is None:
                self.lineEdit_diametro_orlo.setText("")
            else:
                self.lineEdit_diametro_orlo.setText(str(self.DATA_LIST[self.rec_num].diametro_orlo))

            if self.DATA_LIST[self.rec_num].peso is None:
                self.lineEdit_peso.setText("")
            else:
                self.lineEdit_peso.setText(str(self.DATA_LIST[self.rec_num].peso))

            self.comboBox_tipologia.setEditText(str(self.DATA_LIST[self.rec_num].tipo))

            if self.DATA_LIST[self.rec_num].eve_orlo is None:
                self.lineEdit_eve_orlo.setText("")
            else:
                self.lineEdit_eve_orlo.setText(str(self.DATA_LIST[self.rec_num].eve_orlo))

            self.comboBox_repertato.setEditText(str(self.DATA_LIST[self.rec_num].repertato))
            self.comboBox_diagnostico.setEditText(str(self.DATA_LIST[self.rec_num].diagnostico))
            self.lineEdit_n_reperto.setText(n_reperto)
            self.comboBox_tipo_contenitore.setEditText(str(self.DATA_LIST[self.rec_num].tipo_contenitore))
            self.comboBox_struttura.setEditText(str(self.DATA_LIST[self.rec_num].struttura))
            self.comboBox_year.setEditText(str(self.DATA_LIST[self.rec_num].years))

            if self.toolButtonPreviewMedia.isChecked() == False:
                self.loadMediaPreview()
            self.loadMapPreview()
        except:
            pass

    def set_rec_counter(self, t, c):
        self.rec_tot = t
        self.rec_corr = c
        self.label_rec_tot.setText(str(self.rec_tot))
        self.label_rec_corrente.setText(str(self.rec_corr))

    def insert_new_row(self, table_name):
        """Insert new row into a table - uses getattr instead of eval for security"""
        widget_name = table_name.replace('self.', '') if table_name.startswith('self.') else table_name
        table = getattr(self, widget_name)
        table.insertRow(0)

    def remove_row(self, table_name):
        """Remove selected row from a table - uses getattr instead of eval for security"""
        widget_name = table_name.replace('self.', '') if table_name.startswith('self.') else table_name
        table = getattr(self, widget_name)
        rowSelected = table.selectedIndexes()
        try:
            rowIndex = rowSelected[1].row()
            table.removeRow(rowIndex)
        except:
            if self.L == 'it':
                QMessageBox.warning(self, "Messaggio", "Devi selezionare una riga", QMessageBox.StandardButton.Ok)
            elif self.L == 'de':
                QMessageBox.warning(self, "Message", "Sie müssen eine Zeile markieren.", QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.warning(self, "Message", "You must select a row", QMessageBox.StandardButton.Ok)

    def empty_fields(self):
        elementi_reperto_row_count = self.tableWidget_elementi_reperto.rowCount()
        misurazioni_row_count = self.tableWidget_misurazioni.rowCount()
        rif_biblio_row_count = self.tableWidget_rif_biblio.rowCount()
        tecnologie_row_count = self.tableWidget_tecnologie.rowCount()

        self.comboBox_sito.setEditText("")  # 1 - Sito
        self.lineEdit_num_inv.clear()  # 2 - num_inv
        self.comboBox_tipo_reperto.setEditText("")  # 3 - tipo_reperto
        self.comboBox_criterio_schedatura.setEditText("")  # 4 - criterio
        self.comboBox_definizione.setEditText("")  # 5 - definizione
        self.textEdit_descrizione_reperto.clear()  # 6 - descrizione
        self.comboBox_area.setEditText("")  # 7 - area
        self.lineEdit_us.clear()  # 8 - US
        self.comboBox_lavato.setEditText("")  # 9 - lavato
        self.lineEdit_nr_cassa.clear()  # 10 - nr_cassa
        self.comboBox_magazzino.setEditText("")  # 11 - luogo_conservazione
        self.comboBox_conservazione.setEditText("")  # 12 - stato conservazione
        self.comboBox_datazione.setEditText("")  # 13 - datazione reperto

        self.lineEditFormeMin.clear()
        self.lineEditFormeMax.clear()
        self.lineEditTotFram.clear()
        self.lineEditRivestimento.clear()
        self.lineEditCorpoCeramico.clear()

        self.lineEdit_diametro_orlo.clear()
        self.lineEdit_peso.clear()
        self.comboBox_tipologia.setEditText("")
        self.lineEdit_eve_orlo.clear()

        self.comboBox_repertato.setEditText("")
        self.comboBox_diagnostico.setEditText("")

        for i in range(elementi_reperto_row_count):
            self.tableWidget_elementi_reperto.removeRow(0)
        self.insert_new_row("self.tableWidget_elementi_reperto")

        for i in range(misurazioni_row_count):
            self.tableWidget_misurazioni.removeRow(0)
        self.insert_new_row("self.tableWidget_misurazioni")

        for i in range(rif_biblio_row_count):
            self.tableWidget_rif_biblio.removeRow(0)
        self.insert_new_row("self.tableWidget_rif_biblio")

        for i in range(tecnologie_row_count):
            self.tableWidget_tecnologie.removeRow(0)
        self.insert_new_row("self.tableWidget_tecnologie")

        self.lineEdit_n_reperto.clear()
        self.comboBox_tipo_contenitore.setEditText("")
        self.comboBox_struttura.setEditText("")
        self.comboBox_year.setEditText("")

    def empty_fields_nosite(self):
        elementi_reperto_row_count = self.tableWidget_elementi_reperto.rowCount()
        misurazioni_row_count = self.tableWidget_misurazioni.rowCount()
        rif_biblio_row_count = self.tableWidget_rif_biblio.rowCount()
        tecnologie_row_count = self.tableWidget_tecnologie.rowCount()

        self.lineEdit_num_inv.clear()  # 2 - num_inv
        self.comboBox_tipo_reperto.setEditText("")  # 3 - tipo_reperto
        self.comboBox_criterio_schedatura.setEditText("")  # 4 - criterio
        self.comboBox_definizione.setEditText("")  # 5 - definizione
        self.textEdit_descrizione_reperto.clear()  # 6 - descrizione
        self.comboBox_area.setEditText("")  # 7 - area
        self.lineEdit_us.clear()  # 8 - US
        self.comboBox_lavato.setEditText("")  # 9 - lavato
        self.lineEdit_nr_cassa.clear()  # 10 - nr_cassa
        self.comboBox_magazzino.setEditText("")  # 11 - luogo_conservazione
        self.comboBox_conservazione.setEditText("")  # 12 - stato conservazione
        self.comboBox_datazione.setEditText("")  # 13 - datazione reperto

        self.lineEditFormeMin.clear()
        self.lineEditFormeMax.clear()
        self.lineEditTotFram.clear()
        self.lineEditRivestimento.clear()
        self.lineEditCorpoCeramico.clear()

        self.lineEdit_diametro_orlo.clear()
        self.lineEdit_peso.clear()
        self.comboBox_tipologia.setEditText("")
        self.lineEdit_eve_orlo.clear()

        self.comboBox_repertato.setEditText("")
        self.comboBox_diagnostico.setEditText("")

        for i in range(elementi_reperto_row_count):
            self.tableWidget_elementi_reperto.removeRow(0)
        self.insert_new_row("self.tableWidget_elementi_reperto")

        for i in range(misurazioni_row_count):
            self.tableWidget_misurazioni.removeRow(0)
        self.insert_new_row("self.tableWidget_misurazioni")

        for i in range(rif_biblio_row_count):
            self.tableWidget_rif_biblio.removeRow(0)
        self.insert_new_row("self.tableWidget_rif_biblio")

        for i in range(tecnologie_row_count):
            self.tableWidget_tecnologie.removeRow(0)
        self.insert_new_row("self.tableWidget_tecnologie")

        self.lineEdit_n_reperto.clear()
        self.comboBox_tipo_contenitore.setEditText("")
        self.comboBox_struttura.setEditText("")
        self.comboBox_year.setEditText("")

    def setComboBoxEnable(self, f, v):
        """Set enabled state for widgets"""
        for fn in f:
            widget_name = fn.replace('self.', '') if fn.startswith('self.') else fn
            widget = getattr(self, widget_name, None)
            if widget is not None:
                widget.setEnabled(v == "True")

    def setComboBoxEditable(self, f, n):
        """Set editable state for widgets - uses getattr instead of eval for security"""
        for fn in f:
            widget_name = fn.replace('self.' , '') if fn.startswith('self.' ) else fn
            widget = getattr(self, widget_name, None)
            if widget is not None:
                widget.setEditable(bool(n))

    def table2dict(self, n):
        """Convert table widget data to list - uses getattr instead of eval for security"""
        self.tablename = n
        # n is like 'self.tableWidget_bibliografia', extract widget name
        widget_name = n.replace('self.', '') if n.startswith('self.') else n
        table = getattr(self, widget_name)
        row = table.rowCount()
        col = table.columnCount()
        lista = []
        for r in range(row):
            sub_list = []
            for c in range(col):
                value = table.item(r, c)
                if value != None:
                    sub_list.append(str(value.text()))
            if bool(sub_list):
                lista.append(sub_list)
        return lista

    def set_LIST_REC_TEMP(self):
        # Handle numeric fields - convert empty strings to None for database compatibility
        if self.lineEdit_num_inv.text() == "":
            numero_inventario = None
        else:
            numero_inventario = self.lineEdit_num_inv.text()

        if self.lineEditFormeMin.text() == "":
            forme_minime = None
        else:
            forme_minime = self.lineEditFormeMin.text()

        if self.lineEditFormeMax.text() == "":
            forme_massime = None
        else:
            forme_massime = self.lineEditFormeMax.text()

        if self.lineEditTotFram.text() == "":
            totale_frammenti = None
        else:
            totale_frammenti = self.lineEditTotFram.text()

        if self.lineEdit_n_reperto.text() == "":
            n_reperto = None
        else:
            n_reperto = self.lineEdit_n_reperto.text()

        if self.lineEdit_diametro_orlo.text() == "":
            diametro_orlo = None
        else:
            diametro_orlo = self.lineEdit_diametro_orlo.text()

        if self.lineEdit_peso.text() == "":
            peso = None
        else:
            peso = self.lineEdit_peso.text()

        if self.lineEdit_eve_orlo.text() == "":
            eve_orlo = None
        else:
            eve_orlo = self.lineEdit_eve_orlo.text()

        # Handle years as integer
        if self.comboBox_year.currentText() == "":
            years = None
        else:
            years = self.comboBox_year.currentText()

        # TableWidgets
        elementi_reperto = self.table2dict("self.tableWidget_elementi_reperto")
        misurazioni = self.table2dict("self.tableWidget_misurazioni")
        rif_biblio = self.table2dict("self.tableWidget_rif_biblio")
        tecnologie = self.table2dict("self.tableWidget_tecnologie")

        self.DATA_LIST_REC_TEMP = [
            str(self.comboBox_sito.currentText()),                    # 0 - sito
            numero_inventario,                                         # 1 - numero_inventario (Integer)
            str(self.comboBox_tipo_reperto.currentText()),            # 2 - tipo_reperto
            str(self.comboBox_criterio_schedatura.currentText()),     # 3 - criterio_schedatura
            str(self.comboBox_definizione.currentText()),             # 4 - definizione
            str(self.textEdit_descrizione_reperto.toPlainText()),     # 5 - descrizione
            str(self.comboBox_area.currentText()),                    # 6 - area
            str(self.lineEdit_us.text()),                             # 7 - us
            str(self.comboBox_lavato.currentText()),                  # 8 - lavato
            str(self.lineEdit_nr_cassa.text()),                       # 9 - nr_cassa
            str(self.comboBox_magazzino.currentText()),               # 10 - luogo_conservazione
            str(self.comboBox_conservazione.currentText()),           # 11 - stato_conservazione
            str(self.comboBox_datazione.currentText()),               # 12 - datazione_reperto
            str(elementi_reperto),                                     # 13 - elementi_reperto
            str(misurazioni),                                          # 14 - misurazioni
            str(rif_biblio),                                           # 15 - rif_biblio
            str(tecnologie),                                           # 16 - tecnologie
            forme_minime,                                              # 17 - forme_minime (Integer)
            forme_massime,                                             # 18 - forme_massime (Integer)
            totale_frammenti,                                          # 19 - totale_frammenti (Integer)
            str(self.lineEditCorpoCeramico.text()),                   # 20 - corpo_ceramico
            str(self.lineEditRivestimento.text()),                    # 21 - rivestimento
            diametro_orlo,                                             # 22 - diametro_orlo (Numeric)
            peso,                                                      # 23 - peso (Numeric)
            str(self.comboBox_tipologia.currentText()),               # 24 - tipo
            eve_orlo,                                                  # 25 - eve_orlo (Numeric)
            str(self.comboBox_repertato.currentText()),               # 26 - repertato
            str(self.comboBox_diagnostico.currentText()),             # 27 - diagnostico
            n_reperto,                                                 # 28 - n_reperto (Integer)
            str(self.comboBox_tipo_contenitore.currentText()),        # 29 - tipo_contenitore
            str(self.comboBox_struttura.currentText()),               # 30 - struttura
            years                                                      # 31 - years (Integer)
        ]

    def set_LIST_REC_CORR(self):
        self.DATA_LIST_REC_CORR = []
        # Check if REC_CORR is within valid range
        if self.DATA_LIST and 0 <= self.REC_CORR < len(self.DATA_LIST):
            for i in self.TABLE_FIELDS:
                self.DATA_LIST_REC_CORR.append(str(getattr(self.DATA_LIST[self.REC_CORR], i)))

    def records_equal_check(self):
        self.set_LIST_REC_TEMP()
        self.set_LIST_REC_CORR()

        # If DATA_LIST_REC_CORR is empty, it means there's no current record to compare
        if not self.DATA_LIST_REC_CORR:
            return 0  # No changes detected since there's no record

        check_str = str(self.DATA_LIST_REC_CORR) + " " + str(self.DATA_LIST_REC_TEMP)

        if self.DATA_LIST_REC_CORR == self.DATA_LIST_REC_TEMP:
            return 0
        else:
            return 1

    def testing(self, name_file, message):
        f = open(str(name_file), 'w')
        f.write(str(message))
        f.close()

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

    # def on_pushButton_convert_pressed(self):
    #     # if not bool(self.setPathpdf()):
    #         # QMessageBox.warning(self, "INFO", "devi scegliere un file pdf",
    #                             # QMessageBox.Ok)
    #
    #     try:
    #         pdf_file = self.lineEdit_pdf_path.text()
    #         filename=pdf_file.split("/")[-1]
    #         docx_file = self.PDFFOLDER+'/'+filename+'.docx'
    #
    #         # convert pdf to docx
    #         parse(pdf_file, docx_file, start=self.lineEdit_pag1.text(), end=self.lineEdit_pag2.text())
    #         QMessageBox.information(self, "INFO", "Conversion complite",
    #                             QMessageBox.Ok)
    #
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

    def on_pushButton_export_ica_pressed(self):
        if self.mapper is None:
            self.mapper = ArchaeologicalDataMapper(None)
        self.mapper.show()

    def check_for_updates(self):
        """Check if current record has been modified by others"""
        try:
            if self.BROWSE_STATUS == "b" and self.editing_record_id and self.DB_MANAGER:
                # Skip check if we're currently saving to avoid false positives
                if hasattr(self, 'is_saving') and self.is_saving:
                    return

                # Determine table name
                table_name = 'inventario_materiali_table'

                # Get current username to skip self-modifications
                current_user = self.concurrency_manager.get_username() if hasattr(self, 'concurrency_manager') else 'unknown'

                has_conflict, db_version, last_modified_by, last_modified_timestamp = \
                    self.concurrency_manager.check_version_conflict(
                        table_name,
                        self.editing_record_id,
                        self.current_record_version,
                        self.DB_MANAGER
                    )

                # Only show conflict if it's a real conflict:
                # - Not a self-modification (different user)
                # - Not a system update
                # - Has actual version change
                if has_conflict and last_modified_by and \
                   last_modified_by != current_user and \
                   last_modified_by.lower() not in ['system', 'postgres'] and \
                   db_version != self.current_record_version:
                    # Show notification
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Icon.Warning)
                    msg.setWindowTitle("Record Modificato / Record Modified")
                    msg.setText(
                        f"Questo record è stato modificato da {last_modified_by} "
                        f"alle {last_modified_timestamp}.\n\n"
                        f"This record was modified by {last_modified_by} "
                        f"at {last_modified_timestamp}.\n\n"
                        f"Vuoi ricaricare il record? / Do you want to reload?"
                    )
                    msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

                    if msg.exec() == QMessageBox.StandardButton.Yes:
                        # Save current record position
                        current_pos = self.REC_CORR
                        # Reload records
                        self.charge_records()
                        # Restore position and fill fields
                        self.fill_fields(current_pos)
                        # Update version after reload
                        self.current_record_version = db_version
        except Exception as e:
            # Log silently to avoid annoying messages
            pass  # QgsMessageLog.logMessage(f"Update check error: {str(e)}", "PyArchInit", Qgis.Info)

    # =====================================================
    # STATISTICS TAB METHODS
    # =====================================================

    def setup_statistics_tab(self):
        """Setup the Statistics tab with all necessary widgets"""
        try:
            # Find the Quantificazioni tab (tab_6)
            stats_tab = self.tab_6

            # Create main layout for the statistics tab
            main_layout = QVBoxLayout()

            # Create a splitter for flexible layout
            splitter = QSplitter(Qt.Orientation.Horizontal)

            # ========== LEFT PANEL - Tables and Controls ==========
            left_widget = QWidget()
            left_layout = QVBoxLayout(left_widget)

            # Header with controls
            controls_layout = QHBoxLayout()

            # Refresh button
            self.pushButton_refresh_stats = QPushButton("Aggiorna Statistiche" if self.L == 'it' else
                                                         "Statistiken aktualisieren" if self.L == 'de' else
                                                         "Refresh Statistics")
            self.pushButton_refresh_stats.setMaximumWidth(150)
            self.pushButton_refresh_stats.clicked.connect(self.calculate_statistics)
            controls_layout.addWidget(self.pushButton_refresh_stats)

            # Analysis type combo
            self.comboBox_stats_type = QComboBox()
            if self.L == 'it':
                stats_items = [
                    "Distribuzione per Tipo Reperto",
                    "Distribuzione per Classe Materiale",
                    "Distribuzione per Definizione",
                    "Distribuzione per Area",
                    "Distribuzione per US",
                    "Distribuzione per Datazione",
                    "Distribuzione per Corpo Ceramico",
                    "Distribuzione per Rivestimento"
                ]
            elif self.L == 'de':
                stats_items = [
                    "Verteilung nach Artefakttyp",
                    "Verteilung nach Materialklasse",
                    "Verteilung nach Definition",
                    "Verteilung nach Areal",
                    "Verteilung nach SE",
                    "Verteilung nach Datierung",
                    "Verteilung nach Keramikkörper",
                    "Verteilung nach Beschichtung"
                ]
            else:
                stats_items = [
                    "Distribution by Artefact Type",
                    "Distribution by Material Class",
                    "Distribution by Definition",
                    "Distribution by Area",
                    "Distribution by SU",
                    "Distribution by Dating",
                    "Distribution by Ceramic Body",
                    "Distribution by Coating"
                ]
            self.comboBox_stats_type.addItems(stats_items)
            self.comboBox_stats_type.currentIndexChanged.connect(self.on_stats_combo_changed)

            lbl_text = "Tipo Analisi:" if self.L == 'it' else "Analysetyp:" if self.L == 'de' else "Analysis Type:"
            controls_layout.addWidget(QLabel(lbl_text))
            controls_layout.addWidget(self.comboBox_stats_type)
            controls_layout.addStretch()

            left_layout.addLayout(controls_layout)

            # Summary table
            grp_title = "Riepilogo Generale" if self.L == 'it' else "Allgemeine Zusammenfassung" if self.L == 'de' else "General Summary"
            summary_group = QGroupBox(grp_title)
            summary_layout = QVBoxLayout(summary_group)

            self.tableWidget_stats = QTableWidget()
            self.tableWidget_stats.setColumnCount(3)
            headers = ["Categoria", "Conteggio", "Percentuale"] if self.L == 'it' else \
                      ["Kategorie", "Anzahl", "Prozent"] if self.L == 'de' else \
                      ["Category", "Count", "Percentage"]
            self.tableWidget_stats.setHorizontalHeaderLabels(headers)
            self.tableWidget_stats.horizontalHeader().setStretchLastSection(True)
            self.tableWidget_stats.setAlternatingRowColors(True)
            self.tableWidget_stats.setMinimumHeight(200)
            summary_layout.addWidget(self.tableWidget_stats)

            left_layout.addWidget(summary_group)

            # Measurements statistics table
            measures_title = "Statistiche Quantitative" if self.L == 'it' else "Quantitative Statistiken" if self.L == 'de' else "Quantitative Statistics"
            measures_group = QGroupBox(measures_title)
            measures_layout = QVBoxLayout(measures_group)

            self.tableWidget_measures = QTableWidget()
            self.tableWidget_measures.setColumnCount(5)
            headers_m = ["Misura", "Min", "Max", "Media", "Mediana"] if self.L == 'it' else \
                        ["Maß", "Min", "Max", "Mittel", "Median"] if self.L == 'de' else \
                        ["Measure", "Min", "Max", "Mean", "Median"]
            self.tableWidget_measures.setHorizontalHeaderLabels(headers_m)
            self.tableWidget_measures.horizontalHeader().setStretchLastSection(True)
            self.tableWidget_measures.setAlternatingRowColors(True)
            self.tableWidget_measures.setMinimumHeight(150)
            measures_layout.addWidget(self.tableWidget_measures)

            left_layout.addWidget(measures_group)

            # AI Report section
            ai_title = "Report AI Descrittivo" if self.L == 'it' else "KI-Beschreibender Bericht" if self.L == 'de' else "AI Descriptive Report"
            ai_group = QGroupBox(ai_title)
            ai_layout = QVBoxLayout(ai_group)

            ai_buttons_layout = QHBoxLayout()
            btn_gen = "Genera Report AI" if self.L == 'it' else "KI-Bericht erstellen" if self.L == 'de' else "Generate AI Report"
            self.pushButton_generate_ai_report = QPushButton(btn_gen)
            self.pushButton_generate_ai_report.clicked.connect(self.generate_ai_report)
            ai_buttons_layout.addWidget(self.pushButton_generate_ai_report)

            btn_exp = "Esporta PDF" if self.L == 'it' else "PDF exportieren" if self.L == 'de' else "Export PDF"
            self.pushButton_export_stats_pdf = QPushButton(btn_exp)
            self.pushButton_export_stats_pdf.clicked.connect(self.export_statistics_pdf)
            ai_buttons_layout.addWidget(self.pushButton_export_stats_pdf)
            ai_buttons_layout.addStretch()

            ai_layout.addLayout(ai_buttons_layout)

            self.textEdit_ai_report = QTextEdit()
            placeholder = "Il report AI verrà visualizzato qui dopo la generazione..." if self.L == 'it' else \
                         "Der KI-Bericht wird hier nach der Erstellung angezeigt..." if self.L == 'de' else \
                         "AI report will be displayed here after generation..."
            self.textEdit_ai_report.setPlaceholderText(placeholder)
            self.textEdit_ai_report.setMinimumHeight(150)
            ai_layout.addWidget(self.textEdit_ai_report)

            left_layout.addWidget(ai_group)

            splitter.addWidget(left_widget)

            # ========== RIGHT PANEL - Chart (existing Mplwidget) ==========
            if hasattr(self, 'widget') and self.widget is not None:
                splitter.addWidget(self.widget)

            splitter.setSizes([400, 600])

            # Clear existing layout and set new layout
            if stats_tab.layout():
                old_layout = stats_tab.layout()
                while old_layout.count():
                    item = old_layout.takeAt(0)
                    if item.widget() and item.widget() != self.widget:
                        pass
            else:
                stats_tab.setLayout(QVBoxLayout())

            stats_tab.layout().addWidget(splitter)

            # Keep reference to pushButtonQuant if it exists
            if hasattr(self, 'pushButtonQuant'):
                self.pushButtonQuant.setParent(None)
                controls_layout.addWidget(self.pushButtonQuant)

            self.stats_data = {}

        except Exception as e:
            print(f"Error setting up statistics tab: {e}")
            import traceback
            traceback.print_exc()

    def calculate_statistics(self):
        """Calculate all statistics for the current site"""
        try:
            sito = self.comboBox_sito.currentText()
            if not sito or sito == "Inserisci un valore":
                msg = "Seleziona prima un sito." if self.L == 'it' else \
                      "Bitte wählen Sie zuerst eine Ausgrabungsstätte." if self.L == 'de' else \
                      "Please select a site first."
                QMessageBox.warning(self, "Warning", msg, QMessageBox.StandardButton.Ok)
                return

            search_dict = {'sito': f"'{sito}'"}
            records = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)

            if not records:
                msg = "Nessun record trovato per questo sito." if self.L == 'it' else \
                      "Keine Datensätze für diese Ausgrabungsstätte gefunden." if self.L == 'de' else \
                      "No records found for this site."
                QMessageBox.information(self, "Info", msg, QMessageBox.StandardButton.Ok)
                return

            self.stats_records = records
            self.stats_data = {
                'sito': sito,
                'total': len(records),
                'records': records
            }

            self.on_stats_combo_changed()
            self.generate_measurement_stats()
            self.calculate_provenance_stats()

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error calculating statistics: {e}", QMessageBox.StandardButton.Ok)

    def on_stats_combo_changed(self):
        """Handle statistics type combo box change"""
        if not hasattr(self, 'stats_records') or not self.stats_records:
            return

        stat_type = self.comboBox_stats_type.currentIndex()

        field_mapping = {
            0: "tipo_reperto",
            1: "criterio_schedatura",
            2: "definizione",
            3: "area",
            4: "us",
            5: "datazione_reperto",
            6: "corpo_ceramico",
            7: "rivestimento"
        }

        field = field_mapping.get(stat_type, "tipo_reperto")
        self.generate_category_stats(field)

    def generate_category_stats(self, field):
        """Generate statistics for a specific category field"""
        if not hasattr(self, 'stats_records') or not self.stats_records:
            return

        try:
            counts = {}
            total = len(self.stats_records)

            for record in self.stats_records:
                value = getattr(record, field, None)
                if value is None or str(value).strip() == '' or str(value) == 'None':
                    value = 'N/D'
                else:
                    value = str(value)

                counts[value] = counts.get(value, 0) + 1

            sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)

            self.tableWidget_stats.setRowCount(len(sorted_counts) + 1)

            total_label = "TOTALE" if self.L == 'it' else "GESAMT" if self.L == 'de' else "TOTAL"
            self.tableWidget_stats.setItem(0, 0, QTableWidgetItem(total_label))
            self.tableWidget_stats.setItem(0, 1, QTableWidgetItem(str(total)))
            self.tableWidget_stats.setItem(0, 2, QTableWidgetItem("100%"))

            for col in range(3):
                item = self.tableWidget_stats.item(0, col)
                font = item.font()
                font.setBold(True)
                item.setFont(font)

            for i, (category, count) in enumerate(sorted_counts, 1):
                percentage = (count / total) * 100 if total > 0 else 0
                self.tableWidget_stats.setItem(i, 0, QTableWidgetItem(category))
                self.tableWidget_stats.setItem(i, 1, QTableWidgetItem(str(count)))
                self.tableWidget_stats.setItem(i, 2, QTableWidgetItem(f"{percentage:.1f}%"))

            self.tableWidget_stats.resizeColumnsToContents()

            chart_data = [(cat, cnt) for cat, cnt in sorted_counts[:15]]
            if chart_data:
                field_label = field.replace('_', ' ').title()
                title = f"Distribuzione per {field_label}" if self.L == 'it' else \
                        f"Verteilung nach {field_label}" if self.L == 'de' else \
                        f"Distribution by {field_label}"
                self.plot_chart(chart_data, title, "Qty")

            self.stats_data[field] = sorted_counts

        except Exception as e:
            print(f"Error generating category stats: {e}")

    def calculate_provenance_stats(self):
        """Calculate provenance statistics (area, US distributions)"""
        if not hasattr(self, 'stats_records') or not self.stats_records:
            return

        try:
            for field in ['area', 'us']:
                counts = {}
                for record in self.stats_records:
                    value = getattr(record, field, None)
                    if value is None or str(value).strip() == '' or str(value) == 'None':
                        value = 'N/D'
                    else:
                        value = str(value)
                    counts[value] = counts.get(value, 0) + 1

                sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
                self.stats_data[field] = sorted_counts

        except Exception as e:
            print(f"Error calculating provenance stats: {e}")

    def generate_measurement_stats(self):
        """Generate statistics for measurement fields"""
        if not hasattr(self, 'stats_records') or not self.stats_records:
            return

        try:
            if self.L == 'it':
                measurements = {
                    'Forme Minime': 'forme_minime',
                    'Forme Massime': 'forme_massime',
                    'Totale Frammenti': 'totale_frammenti',
                    'Diametro Orlo': 'diametro_orlo',
                    'Peso': 'peso',
                    'EVE Orlo': 'eve_orlo'
                }
            elif self.L == 'de':
                measurements = {
                    'Min. Formen': 'forme_minime',
                    'Max. Formen': 'forme_massime',
                    'Gesamtfragmente': 'totale_frammenti',
                    'Randdurchmesser': 'diametro_orlo',
                    'Gewicht': 'peso',
                    'EVE Rand': 'eve_orlo'
                }
            else:
                measurements = {
                    'Min Forms': 'forme_minime',
                    'Max Forms': 'forme_massime',
                    'Total Fragments': 'totale_frammenti',
                    'Rim Diameter': 'diametro_orlo',
                    'Weight': 'peso',
                    'EVE Rim': 'eve_orlo'
                }

            self.tableWidget_measures.setRowCount(len(measurements))
            self.stats_data['measurements'] = {}

            for row, (label, field) in enumerate(measurements.items()):
                values = []
                for record in self.stats_records:
                    value = getattr(record, field, None)
                    if value is not None and str(value) not in ['', 'None', 'NULL']:
                        try:
                            values.append(float(value))
                        except (ValueError, TypeError):
                            pass

                self.tableWidget_measures.setItem(row, 0, QTableWidgetItem(label))

                if values:
                    min_val = min(values)
                    max_val = max(values)
                    mean_val = sum(values) / len(values)
                    sorted_vals = sorted(values)
                    median_val = sorted_vals[len(sorted_vals) // 2]

                    self.tableWidget_measures.setItem(row, 1, QTableWidgetItem(f"{min_val:.2f}"))
                    self.tableWidget_measures.setItem(row, 2, QTableWidgetItem(f"{max_val:.2f}"))
                    self.tableWidget_measures.setItem(row, 3, QTableWidgetItem(f"{mean_val:.2f}"))
                    self.tableWidget_measures.setItem(row, 4, QTableWidgetItem(f"{median_val:.2f}"))

                    self.stats_data['measurements'][label] = {
                        'min': min_val, 'max': max_val,
                        'mean': mean_val, 'median': median_val,
                        'count': len(values)
                    }
                else:
                    for col in range(1, 5):
                        self.tableWidget_measures.setItem(row, col, QTableWidgetItem("N/D"))

            self.tableWidget_measures.resizeColumnsToContents()

        except Exception as e:
            print(f"Error generating measurement stats: {e}")

    def build_statistics_prompt(self):
        """Build a prompt for AI report generation with language support"""
        if not hasattr(self, 'stats_data') or not self.stats_data:
            return None

        sito = self.stats_data.get('sito', 'Unknown')
        total = self.stats_data.get('total', 0)

        self.calculate_provenance_stats()

        data_section = f"""
SITE: {sito}
TOTAL ARTEFACTS: {total}

"""
        categories = ['tipo_reperto', 'criterio_schedatura', 'definizione', 'datazione_reperto']
        category_labels = {
            'tipo_reperto': 'ARTEFACT TYPE',
            'criterio_schedatura': 'MATERIAL CLASS',
            'definizione': 'DEFINITION',
            'datazione_reperto': 'DATING'
        }

        for cat in categories:
            if cat in self.stats_data:
                data = self.stats_data[cat]
                data_section += f"\n{category_labels.get(cat, cat.upper())} DISTRIBUTION:\n"
                for item, count in data[:10]:
                    percentage = (count / total) * 100 if total > 0 else 0
                    data_section += f"  - {item}: {count} ({percentage:.1f}%)\n"

        data_section += "\n--- PROVENANCE DATA ---\n"

        provenance_fields = ['area', 'us']
        provenance_labels = {'area': 'AREA', 'us': 'STRATIGRAPHIC UNIT (US)'}

        for field in provenance_fields:
            if field in self.stats_data:
                data = self.stats_data[field]
                data_section += f"\n{provenance_labels.get(field, field.upper())} DISTRIBUTION:\n"
                for item, count in data[:15]:
                    percentage = (count / total) * 100 if total > 0 else 0
                    data_section += f"  - {item}: {count} ({percentage:.1f}%)\n"

        if 'measurements' in self.stats_data:
            data_section += "\nQUANTITATIVE STATISTICS:\n"
            for label, stats in self.stats_data['measurements'].items():
                if isinstance(stats, dict):
                    data_section += f"  - {label}: min={stats['min']:.2f}, max={stats['max']:.2f}, mean={stats['mean']:.2f}, median={stats['median']:.2f} (n={stats['count']})\n"

        if self.L == 'it':
            instructions = """
ISTRUZIONI:
Genera un report descrittivo in ITALIANO (circa 400-600 parole) che:
1. Riassuma le caratteristiche principali del complesso di materiali archeologici
2. Evidenzi le categorie predominanti (tipi di reperti, classi materiali, definizioni)
3. Analizzi la distribuzione spaziale per area e US, identificando concentrazioni significative
4. Discuta le quantità e le datazioni dei reperti
5. Fornisca considerazioni cronologiche e tipologiche
6. Identifichi eventuali pattern significativi nella distribuzione spaziale
7. Proponga interpretazioni archeologiche preliminari

Il tono deve essere professionale e scientifico, adatto a una pubblicazione archeologica.
"""
        elif self.L == 'de':
            instructions = """
ANWEISUNGEN:
Erstellen Sie einen beschreibenden Bericht auf DEUTSCH (ca. 400-600 Wörter), der:
1. Die Hauptmerkmale des archäologischen Fundkomplexes zusammenfasst
2. Die vorherrschenden Kategorien hervorhebt (Artefakttypen, Materialklassen, Definitionen)
3. Die räumliche Verteilung nach Areal und SE analysiert
4. Die Mengen und Datierungen der Funde diskutiert
5. Chronologische und typologische Überlegungen liefert
6. Signifikante Muster in der räumlichen Verteilung identifiziert
7. Vorläufige archäologische Interpretationen vorschlägt

Der Ton sollte professionell und wissenschaftlich sein.
"""
        else:
            instructions = """
INSTRUCTIONS:
Generate a descriptive report in ENGLISH (approximately 400-600 words) that:
1. Summarizes the main characteristics of the archaeological assemblage
2. Highlights the predominant categories (artefact types, material classes, definitions)
3. Analyzes the spatial distribution by area and SU, identifying significant concentrations
4. Discusses the quantities and dating of the finds
5. Provides chronological and typological considerations
6. Identifies any significant patterns in the spatial distribution
7. Proposes preliminary archaeological interpretations

The tone should be professional and scientific, suitable for an archaeological publication.
"""

        prompt = f"""Analyze the following archaeological artefact data from the site:

{data_section}

{instructions}
"""
        return prompt

    def get_openai_api_key(self):
        """Get OpenAI API key from file or prompt user to enter it"""
        HOME = os.environ.get('PYARCHINIT_HOME', os.path.join(os.path.expanduser('~'), 'pyarchinit'))
        BIN = os.path.join(HOME, 'bin')

        if not os.path.exists(BIN):
            os.makedirs(BIN, exist_ok=True)

        path_key = os.path.join(BIN, 'gpt_api_key.txt')
        api_key = ""

        if os.path.exists(path_key):
            with open(path_key, 'r') as f:
                api_key = f.read().strip()

            if api_key:
                return api_key
            else:
                msg = 'Il file gpt_api_key.txt è vuoto.\nInserisci la tua OpenAI API key:' if self.L == 'it' else \
                      'Die Datei gpt_api_key.txt ist leer.\nGeben Sie Ihren OpenAI API-Schlüssel ein:' if self.L == 'de' else \
                      'The gpt_api_key.txt file is empty.\nEnter your OpenAI API key:'
                api_key, ok = QInputDialog.getText(self, 'OpenAI API Key', msg)
                if ok and api_key:
                    with open(path_key, 'w') as f:
                        f.write(api_key)
                    return api_key
        else:
            msg = 'API key non trovata.\nInserisci la tua OpenAI API key:\n\n(Verrà salvata in ~/pyarchinit/bin/gpt_api_key.txt)' if self.L == 'it' else \
                  'API-Schlüssel nicht gefunden.\nGeben Sie Ihren OpenAI API-Schlüssel ein:' if self.L == 'de' else \
                  'API key not found.\nEnter your OpenAI API key:\n\n(Will be saved to ~/pyarchinit/bin/gpt_api_key.txt)'
            api_key, ok = QInputDialog.getText(self, 'OpenAI API Key', msg)
            if ok and api_key:
                with open(path_key, 'w') as f:
                    f.write(api_key)
                return api_key

        return None

    def generate_ai_report(self):
        """Generate AI-based descriptive report with streaming"""
        if not hasattr(self, 'stats_data') or not self.stats_data:
            msg = "Calcola prima le statistiche." if self.L == 'it' else \
                  "Berechnen Sie zuerst die Statistiken." if self.L == 'de' else \
                  "Calculate statistics first."
            QMessageBox.warning(self, "Warning", msg, QMessageBox.StandardButton.Ok)
            return

        try:
            api_key = self.get_openai_api_key()

            if not api_key:
                msg = "È necessaria una API key di OpenAI." if self.L == 'it' else \
                      "Ein OpenAI API-Schlüssel ist erforderlich." if self.L == 'de' else \
                      "An OpenAI API key is required."
                QMessageBox.warning(self, "API Key", msg, QMessageBox.StandardButton.Ok)
                return

            model = 'gpt-4o-mini'

            prompt = self.build_statistics_prompt()
            if not prompt:
                return

            progress_msg = "Generazione report in corso..." if self.L == 'it' else \
                          "Bericht wird erstellt..." if self.L == 'de' else \
                          "Generating report..."

            self.textEdit_ai_report.setText(progress_msg)
            QApplication.processEvents()

            from ..modules.utility.report_generator import ReportGenerator
            if not ReportGenerator.is_connected():
                msg = "Connessione internet non disponibile." if self.L == 'it' else \
                      "Keine Internetverbindung." if self.L == 'de' else \
                      "No internet connection."
                QMessageBox.warning(self, "Connection", msg, QMessageBox.StandardButton.Ok)
                self.textEdit_ai_report.setText("")
                return

            try:
                from openai import OpenAI
                client = OpenAI(api_key=api_key)

                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    stream=True,
                )

                self.textEdit_ai_report.clear()
                full_report = ""

                for chunk in response:
                    if chunk.choices[0].delta.content is not None:
                        content = chunk.choices[0].delta.content
                        full_report += content
                        self.textEdit_ai_report.setText(full_report)
                        QApplication.processEvents()

                if full_report:
                    self.stats_data['ai_report'] = full_report

            except ImportError:
                generator = ReportGenerator()
                report = generator.generate_report_with_openai(prompt, model, api_key)
                if report:
                    self.textEdit_ai_report.setText(report)
                    self.stats_data['ai_report'] = report

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error generating AI report: {e}", QMessageBox.StandardButton.Ok)
            self.textEdit_ai_report.setText("")

    def generate_chart_image(self, data, title, chart_type='bar'):
        """Generate a chart image and return the path"""
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from io import BytesIO

        try:
            fig, ax = plt.subplots(figsize=(8, 4))

            if not data:
                return None

            labels = [str(item[0])[:20] for item in data[:10]]
            values = [item[1] for item in data[:10]]

            if chart_type == 'bar':
                ax.bar(range(len(values)), values, color='steelblue', alpha=0.7)
                ax.set_xticks(range(len(values)))
                ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=8)
                ax.set_ylabel('Count')
            elif chart_type == 'pie':
                ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
                ax.axis('equal')

            ax.set_title(title, fontsize=10, fontweight='bold')
            plt.tight_layout()

            img_buffer = BytesIO()
            plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
            img_buffer.seek(0)
            plt.close(fig)

            return img_buffer

        except Exception as e:
            print(f"Error generating chart: {e}")
            return None

    def export_statistics_pdf(self):
        """Export statistics to PDF with charts and multilingual support"""
        if not hasattr(self, 'stats_data') or not self.stats_data:
            msg = "Calcola prima le statistiche." if self.L == 'it' else \
                  "Berechnen Sie zuerst die Statistiken." if self.L == 'de' else \
                  "Calculate statistics first."
            QMessageBox.warning(self, "Warning", msg, QMessageBox.StandardButton.Ok)
            return

        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
            from reportlab.lib.units import cm

            sito = self.stats_data.get('sito', 'Unknown')
            total = self.stats_data.get('total', 0)

            if self.L == 'it':
                labels = {
                    'title': f"Report Statistico Materiali - {sito}",
                    'summary': "Riepilogo Generale",
                    'total': f"Totale reperti: {total}",
                    'type_dist': "Distribuzione per Tipo Reperto",
                    'class_dist': "Distribuzione per Classe Materiale",
                    'provenance': "Distribuzione per Provenienza",
                    'area_dist': "Distribuzione per Area",
                    'us_dist': "Distribuzione per US",
                    'measures': "Statistiche Quantitative",
                    'ai_report': "Report Descrittivo AI",
                    'category': "Categoria", 'count': "Conteggio", 'percentage': "Percentuale",
                    'measure': "Misura", 'min': "Min", 'max': "Max", 'mean': "Media", 'median': "Mediana",
                    'save_title': "Salva Report PDF", 'success': "Successo",
                    'saved_msg': "Report PDF salvato in:\n"
                }
            elif self.L == 'de':
                labels = {
                    'title': f"Statistischer Materialbericht - {sito}",
                    'summary': "Allgemeine Zusammenfassung",
                    'total': f"Gesamtfunde: {total}",
                    'type_dist': "Verteilung nach Artefakttyp",
                    'class_dist': "Verteilung nach Materialklasse",
                    'provenance': "Verteilung nach Herkunft",
                    'area_dist': "Verteilung nach Areal",
                    'us_dist': "Verteilung nach SE",
                    'measures': "Quantitative Statistiken",
                    'ai_report': "KI-Beschreibender Bericht",
                    'category': "Kategorie", 'count': "Anzahl", 'percentage': "Prozent",
                    'measure': "Maß", 'min': "Min", 'max': "Max", 'mean': "Mittel", 'median': "Median",
                    'save_title': "PDF-Bericht speichern", 'success': "Erfolg",
                    'saved_msg': "PDF-Bericht gespeichert in:\n"
                }
            else:
                labels = {
                    'title': f"Artefacts Statistical Report - {sito}",
                    'summary': "General Summary",
                    'total': f"Total finds: {total}",
                    'type_dist': "Distribution by Artefact Type",
                    'class_dist': "Distribution by Material Class",
                    'provenance': "Distribution by Provenance",
                    'area_dist': "Distribution by Area",
                    'us_dist': "Distribution by SU",
                    'measures': "Quantitative Statistics",
                    'ai_report': "AI Descriptive Report",
                    'category': "Category", 'count': "Count", 'percentage': "Percentage",
                    'measure': "Measure", 'min': "Min", 'max': "Max", 'mean': "Mean", 'median': "Median",
                    'save_title': "Save PDF Report", 'success': "Success",
                    'saved_msg': "PDF report saved to:\n"
                }

            HOME = os.environ.get('PYARCHINIT_HOME', os.path.join(os.path.expanduser('~'), 'pyarchinit'))
            PDFFOLDER = os.path.join(HOME, "pyarchinit_PDF_folder")

            filename, _ = QFileDialog.getSaveFileName(
                self, labels['save_title'],
                os.path.join(PDFFOLDER, f"Artefacts_Statistics_{sito}.pdf"),
                "PDF Files (*.pdf)"
            )

            if not filename:
                return

            doc = SimpleDocTemplate(filename, pagesize=A4,
                                   rightMargin=2*cm, leftMargin=2*cm,
                                   topMargin=2*cm, bottomMargin=2*cm)

            styles = getSampleStyleSheet()
            title_style = ParagraphStyle('Title', parent=styles['Title'], fontSize=16, spaceAfter=20)
            heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=12, spaceAfter=10)
            normal_style = styles['Normal']

            elements = []

            elements.append(Paragraph(labels['title'], title_style))
            elements.append(Spacer(1, 12))
            elements.append(Paragraph(labels['summary'], heading_style))
            elements.append(Paragraph(labels['total'], normal_style))
            elements.append(Spacer(1, 12))

            if 'tipo_reperto' in self.stats_data and self.stats_data['tipo_reperto']:
                elements.append(Paragraph(labels['type_dist'], heading_style))
                chart_buffer = self.generate_chart_image(self.stats_data['tipo_reperto'], labels['type_dist'], 'bar')
                if chart_buffer:
                    img = Image(chart_buffer, width=14*cm, height=7*cm)
                    elements.append(img)
                    elements.append(Spacer(1, 6))

                table_data = [[labels['category'], labels['count'], labels['percentage']]]
                for item, count in self.stats_data['tipo_reperto'][:15]:
                    percentage = (count / total) * 100 if total > 0 else 0
                    table_data.append([str(item), str(count), f"{percentage:.1f}%"])

                table = Table(table_data, colWidths=[8*cm, 3*cm, 3*cm])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                elements.append(table)
                elements.append(Spacer(1, 12))

            elements.append(PageBreak())
            elements.append(Paragraph(labels['provenance'], heading_style))

            if 'area' in self.stats_data and self.stats_data['area']:
                elements.append(Paragraph(labels['area_dist'], heading_style))
                chart_buffer = self.generate_chart_image(self.stats_data['area'], labels['area_dist'], 'bar')
                if chart_buffer:
                    img = Image(chart_buffer, width=14*cm, height=6*cm)
                    elements.append(img)
                    elements.append(Spacer(1, 6))

            if 'us' in self.stats_data and self.stats_data['us']:
                elements.append(Paragraph(labels['us_dist'], heading_style))
                chart_buffer = self.generate_chart_image(self.stats_data['us'], labels['us_dist'], 'bar')
                if chart_buffer:
                    img = Image(chart_buffer, width=14*cm, height=6*cm)
                    elements.append(img)
                    elements.append(Spacer(1, 12))

            if 'measurements' in self.stats_data:
                elements.append(Paragraph(labels['measures'], heading_style))
                table_data = [[labels['measure'], labels['min'], labels['max'], labels['mean'], labels['median']]]
                for label_m, stats in self.stats_data['measurements'].items():
                    if isinstance(stats, dict):
                        table_data.append([label_m, f"{stats['min']:.2f}", f"{stats['max']:.2f}",
                                          f"{stats['mean']:.2f}", f"{stats['median']:.2f}"])

                table = Table(table_data, colWidths=[4*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                elements.append(table)
                elements.append(Spacer(1, 12))

            if 'ai_report' in self.stats_data and self.stats_data['ai_report']:
                elements.append(PageBreak())
                elements.append(Paragraph(labels['ai_report'], heading_style))
                report_text = self.stats_data['ai_report']
                for para in report_text.split('\n\n'):
                    if para.strip():
                        clean_para = para.strip()
                        if clean_para.startswith('##'):
                            clean_para = clean_para.replace('##', '').strip()
                            elements.append(Paragraph(f"<b>{clean_para}</b>", normal_style))
                        elif clean_para.startswith('#'):
                            clean_para = clean_para.replace('#', '').strip()
                            elements.append(Paragraph(f"<b>{clean_para}</b>", normal_style))
                        else:
                            elements.append(Paragraph(clean_para, normal_style))
                        elements.append(Spacer(1, 6))

            doc.build(elements)

            QMessageBox.information(self, labels['success'], labels['saved_msg'] + filename, QMessageBox.StandardButton.Ok)

            if platform.system() == "Windows":
                os.startfile(filename)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", filename])
            else:
                subprocess.Popen(["xdg-open", filename])

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error exporting PDF: {e}", QMessageBox.StandardButton.Ok)

## Class end


class InventarioFilterDialog(QDialog):
    """Dialog for filtering Inventario Materiali records by numero_inventario, n_reperto, or years with checkboxes"""
    L = QgsSettings().value("locale/userLocale", "it", type=str)[:2]

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.selected_ids = []
        self.selected_year = None
        self.filter_type = 'numero_inventario'  # default filter type
        self.inv_records = []
        self.initUI()

    def initUI(self):
        if self.L == 'it':
            self.setWindowTitle("Filtra Record Inventario Materiali")
        elif self.L == 'de':
            self.setWindowTitle("Inventarmaterialien filtern")
        else:
            self.setWindowTitle("Filter Inventory Records")

        self.setMinimumSize(500, 600)
        layout = QVBoxLayout(self)

        # Filter type selection
        filter_type_layout = QHBoxLayout()
        filter_type_label = QLabel(self)
        if self.L == 'it':
            filter_type_label.setText("Filtra per:")
        elif self.L == 'de':
            filter_type_label.setText("Filtern nach:")
        else:
            filter_type_label.setText("Filter by:")
        filter_type_layout.addWidget(filter_type_label)

        self.comboBox_filter_type = QComboBox(self)
        if self.L == 'it':
            self.comboBox_filter_type.addItem("Nr. Inventario", 'numero_inventario')
            self.comboBox_filter_type.addItem("Nr. Reperto (RA)", 'n_reperto')
            self.comboBox_filter_type.addItem("Anno", 'years')
        elif self.L == 'de':
            self.comboBox_filter_type.addItem("Inventarnr.", 'numero_inventario')
            self.comboBox_filter_type.addItem("Fundnr. (RA)", 'n_reperto')
            self.comboBox_filter_type.addItem("Jahr", 'years')
        else:
            self.comboBox_filter_type.addItem("Inventory Nr.", 'numero_inventario')
            self.comboBox_filter_type.addItem("Find Nr. (RA)", 'n_reperto')
            self.comboBox_filter_type.addItem("Year", 'years')

        self.comboBox_filter_type.currentIndexChanged.connect(self.on_filter_type_changed)
        filter_type_layout.addWidget(self.comboBox_filter_type)
        filter_type_layout.addStretch()
        layout.addLayout(filter_type_layout)

        # Year filter section (for additional filtering)
        year_layout = QHBoxLayout()
        year_label = QLabel(self)
        if self.L == 'it':
            year_label.setText("Anno (opzionale):")
        elif self.L == 'de':
            year_label.setText("Jahr (optional):")
        else:
            year_label.setText("Year (optional):")
        year_layout.addWidget(year_label)

        self.comboBox_year = QComboBox(self)
        self.comboBox_year.setMinimumWidth(100)
        self.comboBox_year.currentIndexChanged.connect(self.on_year_changed)
        year_layout.addWidget(self.comboBox_year)
        year_layout.addStretch()
        layout.addLayout(year_layout)

        # Search bar
        self.search_bar = QLineEdit(self)
        if self.L == 'it':
            self.search_bar.setPlaceholderText("Cerca...")
        elif self.L == 'de':
            self.search_bar.setPlaceholderText("Suchen...")
        else:
            self.search_bar.setPlaceholderText("Search...")
        self.search_bar.textChanged.connect(self.filter_list)
        layout.addWidget(self.search_bar)

        # Select All / Deselect All buttons
        btn_layout = QHBoxLayout()
        self.btn_select_all = QPushButton(self)
        self.btn_deselect_all = QPushButton(self)

        if self.L == 'it':
            self.btn_select_all.setText("Seleziona Tutti")
            self.btn_deselect_all.setText("Deseleziona Tutti")
        elif self.L == 'de':
            self.btn_select_all.setText("Alle auswählen")
            self.btn_deselect_all.setText("Alle abwählen")
        else:
            self.btn_select_all.setText("Select All")
            self.btn_deselect_all.setText("Deselect All")

        self.btn_select_all.clicked.connect(self.select_all)
        self.btn_deselect_all.clicked.connect(self.deselect_all)
        btn_layout.addWidget(self.btn_select_all)
        btn_layout.addWidget(self.btn_deselect_all)
        layout.addLayout(btn_layout)

        # List widget with checkboxes
        self.list_widget = QListWidget(self)
        layout.addWidget(self.list_widget)

        # Populate data
        self.populate_data()

        # Status label
        self.label_status = QLabel(self)
        self.update_status_label()
        layout.addWidget(self.label_status)

        # Filter button
        filter_button = QPushButton(self)
        if self.L == 'it':
            filter_button.setText("Applica Filtro")
        elif self.L == 'de':
            filter_button.setText("Filter anwenden")
        else:
            filter_button.setText("Apply Filter")
        filter_button.clicked.connect(self.apply_filter)
        layout.addWidget(filter_button)

        self.setLayout(layout)

    def natural_sort_key(self, text):
        """Natural sorting key that handles alphanumeric values correctly"""
        import re
        return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', str(text))]

    def populate_data(self):
        """Fetch inventory records and populate year combobox and list"""
        try:
            # Get all inventory records
            print(f"[InventarioFilter] Starting populate_data...")
            print(f"[InventarioFilter] db_manager type: {type(self.db_manager)}")

            # Use the same approach as the main class
            self.inv_records = self.db_manager.query('INVENTARIO_MATERIALI')
            print(f"[InventarioFilter] Got {len(self.inv_records)} records")

            # Get unique years and sort them
            unique_years = sorted(
                set(record.years for record in self.inv_records if record.years is not None),
                reverse=True  # Most recent first
            )
            print(f"[InventarioFilter] Found {len(unique_years)} unique years")

            # Populate year combobox
            self.comboBox_year.blockSignals(True)
            self.comboBox_year.clear()
            if self.L == 'it':
                self.comboBox_year.addItem("Tutti gli anni", None)
            elif self.L == 'de':
                self.comboBox_year.addItem("Alle Jahre", None)
            else:
                self.comboBox_year.addItem("All years", None)

            for year in unique_years:
                self.comboBox_year.addItem(str(year), year)
            self.comboBox_year.blockSignals(False)

            # Populate list based on current filter type
            self.update_id_list()
            print(f"[InventarioFilter] populate_data completed successfully")

        except Exception as e:
            import traceback
            print(f"[InventarioFilter] Error populating inventory filter: {e}")
            print(f"[InventarioFilter] Traceback: {traceback.format_exc()}")

    def on_filter_type_changed(self, index):
        """Handle filter type selection change"""
        self.filter_type = self.comboBox_filter_type.currentData()
        self.search_bar.clear()
        self.update_id_list()

    def on_year_changed(self, index):
        """Handle year selection change"""
        self.selected_year = self.comboBox_year.currentData()
        self.search_bar.clear()
        self.update_id_list()

    def get_filtered_records(self):
        """Get records filtered by selected year"""
        if self.selected_year is None:
            return self.inv_records
        return [r for r in self.inv_records if r.years == self.selected_year]

    def update_id_list(self):
        """Update the list based on current filter type and year filter"""
        filtered_records = self.get_filtered_records()

        # Get unique values based on filter type
        if self.filter_type == 'numero_inventario':
            unique_values = sorted(
                set(record.numero_inventario for record in filtered_records if record.numero_inventario is not None),
                key=self.natural_sort_key
            )
        elif self.filter_type == 'n_reperto':
            unique_values = sorted(
                set(record.n_reperto for record in filtered_records if record.n_reperto is not None),
                key=self.natural_sort_key
            )
        else:  # years
            unique_values = sorted(
                set(record.years for record in filtered_records if record.years is not None),
                reverse=True
            )

        self.update_list_widget(unique_values, filtered_records)

    def update_list_widget(self, values, records=None):
        """Update the list widget with the given values"""
        self.list_widget.clear()

        if records is None:
            records = self.get_filtered_records()

        # Create a dict to count occurrences per value
        value_count = {}
        for record in records:
            if self.filter_type == 'numero_inventario':
                val = record.numero_inventario
            elif self.filter_type == 'n_reperto':
                val = record.n_reperto
            else:
                val = record.years

            if val is not None:
                value_count[val] = value_count.get(val, 0) + 1

        # Get label prefix based on filter type
        if self.L == 'it':
            prefixes = {
                'numero_inventario': 'Inv.',
                'n_reperto': 'RA',
                'years': 'Anno'
            }
        elif self.L == 'de':
            prefixes = {
                'numero_inventario': 'Inv.',
                'n_reperto': 'RA',
                'years': 'Jahr'
            }
        else:
            prefixes = {
                'numero_inventario': 'Inv.',
                'n_reperto': 'RA',
                'years': 'Year'
            }

        prefix = prefixes.get(self.filter_type, '')

        for val in values:
            list_item = QListWidgetItem(self.list_widget)
            count = value_count.get(val, 0)
            checkbox = QCheckBox(f"{prefix} {val} ({count} record{'s' if count != 1 else ''})")
            checkbox.filter_value = val
            checkbox.stateChanged.connect(self.update_status_label)
            self.list_widget.addItem(list_item)
            self.list_widget.setItemWidget(list_item, checkbox)

    def filter_list(self, text):
        """Filter the list based on search text"""
        filtered_records = self.get_filtered_records()

        # Get unique values based on filter type
        if self.filter_type == 'numero_inventario':
            all_values = set(record.numero_inventario for record in filtered_records if record.numero_inventario is not None)
        elif self.filter_type == 'n_reperto':
            all_values = set(record.n_reperto for record in filtered_records if record.n_reperto is not None)
        else:
            all_values = set(record.years for record in filtered_records if record.years is not None)

        if not text:
            unique_values = sorted(all_values, key=self.natural_sort_key if self.filter_type != 'years' else lambda x: -x)
        else:
            unique_values = sorted(
                [v for v in all_values if str(v).startswith(text)],
                key=self.natural_sort_key if self.filter_type != 'years' else lambda x: -x
            )

        self.update_list_widget(unique_values, filtered_records)

    def select_all(self):
        """Select all visible checkboxes"""
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            checkbox = self.list_widget.itemWidget(item)
            if checkbox:
                checkbox.setChecked(True)

    def deselect_all(self):
        """Deselect all visible checkboxes"""
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            checkbox = self.list_widget.itemWidget(item)
            if checkbox:
                checkbox.setChecked(False)

    def update_status_label(self):
        """Update the status label with count of selected items"""
        count = self.get_selected_count()
        total = self.list_widget.count()
        year_text = ""
        if self.selected_year:
            year_text = f" ({self.selected_year})"

        if self.L == 'it':
            self.label_status.setText(f"Selezionati: {count} di {total}{year_text}")
        elif self.L == 'de':
            self.label_status.setText(f"Ausgewählt: {count} von {total}{year_text}")
        else:
            self.label_status.setText(f"Selected: {count} of {total}{year_text}")

    def get_selected_count(self):
        """Get the count of selected checkboxes"""
        count = 0
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            checkbox = self.list_widget.itemWidget(item)
            if checkbox and checkbox.isChecked():
                count += 1
        return count

    def apply_filter(self):
        """Apply the filter and close the dialog"""
        self.selected_ids.clear()

        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            checkbox = self.list_widget.itemWidget(item)
            if checkbox and checkbox.isChecked():
                self.selected_ids.append(checkbox.filter_value)

        print(f"Selected values: {self.selected_ids}, Year: {self.selected_year}, Type: {self.filter_type}")
        self.accept()

    def get_selected_ids(self):
        """Return the list of selected values"""
        return self.selected_ids

    def get_selected_year(self):
        """Return the selected year (None if 'All years')"""
        return self.selected_year

    def get_filter_type(self):
        """Return the current filter type"""
        return self.filter_type


# if __name__ == "__main__":
    # app = QApplication(sys.argv)
    # ui = pyarchinit_US()
    # ui.show()
    # sys.exit(app.exec())
