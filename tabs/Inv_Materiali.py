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
from datetime import date
import platform
from pdf2docx import parse
import cv2
import numpy as np
import sys
from builtins import range
from builtins import str
from qgis.PyQt.QtCore import Qt, QSize, QVariant
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.uic import loadUiType
from qgis.core import QgsSettings

from ..modules.db.pyarchinit_conn_strings import Connection
from ..modules.db.pyarchinit_db_manager import Pyarchinit_db_management
from ..modules.db.pyarchinit_utility import Utility
from ..modules.utility.csv_writer import UnicodeWriter
from ..modules.utility.media_ponderata_sperimentale import *
from ..modules.utility.delegateComboBox import ComboBoxDelegate
from ..modules.utility.pyarchinit_error_check import Error_check
from ..modules.utility.pyarchinit_exp_Findssheet_pdf import generate_reperti_pdf
from ..modules.gis.pyarchinit_pyqgis import Pyarchinit_pyqgis
from ..gui.imageViewer import ImageViewer
from ..gui.quantpanelmain import QuantPanelMain
from ..gui.sortpanelmain import SortPanelMain
from ..gui.pyarchinitConfigDialog import pyArchInitDialog_Config
MAIN_DIALOG_CLASS, _ = loadUiType(os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'Inv_Materiali.ui'))


class pyarchinit_Inventario_reperti(QDialog, MAIN_DIALOG_CLASS):
    L=QgsSettings().value("locale/userLocale")[0:2]
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
            "Struttura":'struttura'
        }
        QUANT_ITEMS = ['Tipo reperto',
                       'Classe materiale',
                       'Definizione',
                       'Corpo ceramico',
                       'Rivestimento',
                       "Tipo",
                       "Datazione reperto",
                       "RA"]

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
            "Struttura"
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
            "Strukturen":'struttura'
        }
        QUANT_ITEMS = ['Art des Artefakts',
                       'Materialklasse',
                       'Definition',
                       'Keramikkörper',
                       'Oberflächenbehandlung',
                       'Typ',
                       'Datierung - Artefakt',
                       'RA']

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
            "Strukturen"
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
            "Structure":'struttura'
        }
        QUANT_ITEMS = ['Artefact type',
                       'Material class',
                       'Definition',
                       'Body sherds',
                       'Coating',
                       'Type',
                       'Artefact period',
                       'RA']

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
            "Structure"
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
        'struttura'
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
        'struttura'
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
        "AR": ['ar_AR','ar','AR', 'AR_AR'],
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
        self.mDockWidget_export.setHidden(True)
        self.mDockWidget.setHidden(True)
        self.pyQGIS = Pyarchinit_pyqgis(iface)
        self.currentLayerId = None
        
        
        try:
            self.on_pushButton_connect_pressed()
        except Exception as e:
            QMessageBox.warning(self, "Connection system", str(e), QMessageBox.Ok)
        #self.setnone()
        self.fill_fields()
        #self.lineEdit_num_inv.setText('')
        #self.lineEdit_num_inv.textChanged.connect(self.update)
        self.lineEdit_num_inv.textChanged.connect(self.charge_struttura)
        self.set_sito()
        self.msg_sito()
        #self.comboBox_repertato.currentTextChanged.connect(self.numero_reperto)
        #self.numero_invetario()
        self.toolButton_pdfpath.clicked.connect(self.setPathpdf)
        self.customize_gui()
    
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
        dlg.exec_()

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
                    f = open(filename, 'wb')
                    Uw = UnicodeWriter(f)
                    Uw.writerows(csv_dataset)
                    f.close()

                    self.plot_chart(dataset_sum, 'Grafico per Forme minime', 'Nr. Forme')
                else:
                    QMessageBox.warning(self, "Attenzione", "Non ci sono dati da rappresentare", QMessageBox.Ok)

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
                    QMessageBox.warning(self, "Attenzione", "Non ci sono dati da rappresentare!!", QMessageBox.Ok)
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
                    QMessageBox.warning(self, "Exportation", str(filename), QMessageBox.Ok)
                    f = open(filename, 'wb')
                    Uw = UnicodeWriter(f)
                    Uw.writerows(csv_dataset)
                    f.close()

                    self.plot_chart(dataset_sum, 'Diagramm für Minimale Anzahl der Gefäßindividuen', 'Nr. Anzahl')
                else:
                    QMessageBox.warning(self, "Achtung", "Es gibt keine Daten, die dargestellt werden können", QMessageBox.Ok)

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
                    f = open(filename, 'wb')
                    Uw = UnicodeWriter(f)
                    Uw.writerows(csv_dataset)
                    f.close()
                    # QMessageBox.warning(self, "Esportazione", "Esportazione del file "+ str(filename) + "avvenuta con successo. I dati si trovano nella cartella pyarchinit_Quantificazioni_folder sotto al vostro Utente", MessageBox.Ok)


                    self.plot_chart(dataset_sum, 'Fragmentdiagramm', 'Nr. Fragmente')
                else:
                    QMessageBox.warning(self, "Achtung", "Es gibt keine Daten, die dargestellt werden können", QMessageBox.Ok)  
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
                    QMessageBox.warning(self, "Exportation", str(filename), QMessageBox.Ok)
                    f = open(filename, 'wb')
                    Uw = UnicodeWriter(f)
                    Uw.writerows(csv_dataset)
                    f.close()

                    self.plot_chart(dataset_sum, 'Graph for min shape', 'Nr. Shape')
                else:
                    QMessageBox.warning(self, "Warning", "There are no data to represent", QMessageBox.Ok)

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
                    QMessageBox.warning(self, "Warning", "There are no data to represent", QMessageBox.Ok)              
        """experimental disabled
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
            f = open(filename, 'wb')
            Uw = UnicodeWriter(f)
            Uw.writerows(csv_dataset)
            f.close()
            """

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
        self.title = t
        self.ylabel = yl
        if type(self.data_list) == list:
            data_diz = {}
            for item in self.data_list:
                data_diz[item[0]] = item[1]
        x = list(range(len(data_diz)))
        n_bars = len(data_diz)
        values = list(data_diz.values())
        teams = list(data_diz.keys())
        ind = np.arange(n_bars)
        #randomNumbers = random.sample(range(0, 10), 10)
        self.widget.canvas.ax.clear()
        #QMessageBox.warning(self, "Alert", str(teams) ,  QMessageBox.Ok)
        bars = self.widget.canvas.ax.bar(x, height=values, width=0.5, align='center', alpha=0.4,picker=5)
        #guardare il metodo barh per barre orizzontali
        self.widget.canvas.ax.set_title(self.title)
        self.widget.canvas.ax.set_ylabel(self.ylabel)
        l = []
        for team in teams:
            l.append('""')
        #self.widget.canvas.ax.set_xticklabels(x , ""   ,size = 'x-small', rotation = 0)
        n = 0
        for bar in bars:
            val = int(bar.get_height())
            x_pos = bar.get_x() + 0.25
            label  = teams[n]+ ' - ' + str(val)
            y_pos = 0.1 #bar.get_height() - bar.get_height() + 1
            self.widget.canvas.ax.tick_params(axis='x', labelsize=8)
            #self.widget.canvas.ax.set_xticklabels(ind + x, ['fg'], position = (x_pos,y_pos), xsize = 'small', rotation = 90)
            self.widget.canvas.ax.text(x_pos, y_pos, label,zorder=0, ha='center', va='bottom',size = 'x-small', rotation = 90)
            n+=1
        #self.widget.canvas.ax.plot(randomNumbers)
        self.widget.canvas.draw()

    def on_pushButton_connect_pressed(self):
        # self.setComboBoxEditable(["self.comboBox_sito"],1)
        conn = Connection()
        conn_str = conn.conn_str()

        test_conn = conn_str.find('sqlite')

        if test_conn == 0:
            self.DB_SERVER = "sqlite"

        try:
            self.DB_MANAGER = Pyarchinit_db_management(conn_str)
            self.DB_MANAGER.connection()
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
                                        QMessageBox.Ok)
                
                elif self.L=='de':
                    
                    QMessageBox.warning(self,"WILLKOMMEN","WILLKOMMEN in pyArchInit" + "Munsterformular"+ ". Die Datenbank ist leer. Tippe 'Ok' und aufgehts!",
                                        QMessageBox.Ok) 
                else:
                    QMessageBox.warning(self,"WELCOME", "Welcome in pyArchInit" + "Samples form" + ". The DB is empty. Push 'Ok' and Good Work!",
                                        QMessageBox.Ok)    
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

    def customize_gui(self):

        l = QgsSettings().value("locale/userLocale", QVariant)
        lang = ""
        for key, values in self.LANG.items():
            if values.__contains__(l):
                lang = str(key)
        lang = "'" + lang + "'"

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

        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'inventario_materiali_table' + "'",
            'tipologia_sigla': "'" + '3.4' + "'"
        }

        elRinv = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        valuesElRinv = []

        for i in range(len(elRinv)):
            valuesElRinv.append(elRinv[i].sigla_estesa)

        valuesElRinv.sort()

        self.delegateElRinv = ComboBoxDelegate()
        self.delegateElRinv.def_values(valuesElRinv)
        self.delegateElRinv.def_editable('False')
        self.tableWidget_elementi_reperto.setItemDelegateForColumn(0, self.delegateElRinv)

        # lista misurazioni - tipo di misura

        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'inventario_materiali_table' + "'",
            'tipologia_sigla': "'" + '3.5' + "'"
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

        # lista misurazioni - unita di misura

        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'inventario_materiali_table' + "'",
            'tipologia_sigla': "'" + '3.6' + "'"
        }

        elUnitaMis = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        valuesUnitaMis = []

        for i in range(len(elUnitaMis)):
            valuesUnitaMis.append(elUnitaMis[i].sigla)

        valuesUnitaMis.sort()

        self.delegateUnitaMis = ComboBoxDelegate()
        self.delegateUnitaMis.def_values(valuesUnitaMis)
        self.delegateUnitaMis.def_editable('False')
        self.tableWidget_misurazioni.setItemDelegateForColumn(1, self.delegateUnitaMis)

        # lista tecnologie - tipo tecnologia

        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'inventario_materiali_table' + "'",
            'tipologia_sigla': "'" + '3.7' + "'"
        }

        elTipoTec = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        valuesTipoTec = []

        for i in range(len(elTipoTec)):
            valuesTipoTec.append(elTipoTec[i].sigla_estesa)

        valuesTipoTec.sort()

        self.delegateTipoTec = ComboBoxDelegate()
        self.delegateTipoTec.def_values(valuesTipoTec)
        self.delegateTipoTec.def_editable('False')
        self.tableWidget_tecnologie.setItemDelegateForColumn(0, self.delegateTipoTec)

        # lista tecnologie - posizione

        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'inventario_materiali_table' + "'",
            'tipologia_sigla': "'" + '3.8' + "'"
        }

        elPosTec = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        valuesPosTec = []

        for i in range(len(elPosTec)):
            valuesPosTec.append(elPosTec[i].sigla_estesa)

        valuesPosTec.sort()

        self.delegatePosTec = ComboBoxDelegate()
        self.delegatePosTec.def_values(valuesPosTec)
        self.delegatePosTec.def_editable('False')
        self.tableWidget_tecnologie.setItemDelegateForColumn(1, self.delegatePosTec)

        # lista tecnologie - tipo quantita

        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'inventario_materiali_table' + "'",
            'tipologia_sigla': "'" + '3.9' + "'"
        }

        elTipoQu = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        valuesTipoQu = []

        for i in range(len(elTipoQu)):
            valuesTipoQu.append(elTipoQu[i].sigla_estesa)

        valuesTipoQu.sort()

        self.delegateTipoQu = ComboBoxDelegate()
        self.delegateTipoQu.def_values(valuesTipoQu)
        self.delegateTipoQu.def_editable('False')
        self.tableWidget_tecnologie.setItemDelegateForColumn(2, self.delegateTipoQu)

        # lista tecnologie - unita di misura

        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'inventario_materiali_table' + "'",
            'tipologia_sigla': "'" + '3.10' + "'"
        }

        elUnMis = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        valuesUnMis = []

        for i in range(len(elUnMis)):
            valuesUnMis.append(elUnMis[i].sigla)

        valuesUnMis.sort()

        self.delegateUnMis = ComboBoxDelegate()
        self.delegateUnMis.def_values(valuesUnMis)
        self.delegateUnMis.def_editable('False')
        self.tableWidget_tecnologie.setItemDelegateForColumn(3, self.delegateUnMis)


    def loadMediaPreview(self, mode=0):
        self.iconListWidget.clear()
        conn = Connection()
        
        thumb_path = conn.thumb_path()
        thumb_path_str = thumb_path['thumb_path']
        if mode == 0:
            """ if has geometry column load to map canvas """

            rec_list = self.ID_TABLE + " = " + str(
                eval("self.DATA_LIST[int(self.REC_CORR)]." + self.ID_TABLE))
            search_dict = {
                'id_entity': "'" + str(eval("self.DATA_LIST[int(self.REC_CORR)]." + self.ID_TABLE)) + "'",
                'entity_type': "'REPERTO'"}
            record_us_list = self.DB_MANAGER.query_bool(search_dict, 'MEDIATOENTITY')
            for i in record_us_list:
                search_dict = {'id_media': "'" + str(i.id_media) + "'"}

                u = Utility()
                search_dict = u.remove_empty_items_fr_dict(search_dict)
                mediathumb_data = self.DB_MANAGER.query_bool(search_dict, "MEDIA_THUMB")
                thumb_path = str(mediathumb_data[0].filepath)

                item = QListWidgetItem(str(i.media_name))

                item.setData(Qt.UserRole, str(i.media_name))
                icon = QIcon(thumb_path_str+thumb_path)
                item.setIcon(icon)
                self.iconListWidget.addItem(item)
        elif mode == 1:
            self.iconListWidget.clear()

    def openWide_image(self):
        items = self.iconListWidget.selectedItems()
        conn = Connection()
        conn_str = conn.conn_str()
        thumb_resize = conn.thumb_resize()
        thumb_resize_str = thumb_resize['thumb_resize']
        for item in items:
            dlg = ImageViewer()
            id_orig_item = item.text()  # return the name of original file
            search_dict = {'media_filename': "'" + str(id_orig_item) + "'" , 'mediatype': "'" + 'video' + "'"} 
            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)
            #try:
            res = self.DB_MANAGER.query_bool(search_dict, "MEDIA_THUMB")
            
            
            search_dict_2 = {'media_filename': "'" + str(id_orig_item) + "'" , 'mediatype': "'" + 'image' + "'"}  
            
            search_dict_2 = u.remove_empty_items_fr_dict(search_dict_2)
            #try:
            res_2 = self.DB_MANAGER.query_bool(search_dict_2, "MEDIA_THUMB")
            
            search_dict_3 = {'media_filename': "'" + str(id_orig_item) + "'"}  
            
            search_dict_3 = u.remove_empty_items_fr_dict(search_dict_3)
            #try:
            res_3 = self.DB_MANAGER.query_bool(search_dict_3, "MEDIA_THUMB")
            
            # file_path = str(res[0].path_resize)
            # file_path_2 = str(res_2[0].path_resize)
            file_path_3 = str(res_3[0].path_resize)
            if bool(res):
                os.startfile(str(thumb_resize_str+file_path_3))
            elif bool(res_2):
                dlg.show_image(str(thumb_resize_str+file_path_3))  
                dlg.exec_()

    
    # def numero_reperto(self):
        # # self.set_sito()
        # contatore = 0
        # list=[]
        
        
        
        
        
        # if self.comboBox_repertato.currentText()=='No':
            # self.lineEdit_n_reperto.clear()
            # self.lineEdit_n_reperto.setText('0')
            # self.lineEdit_n_reperto.update()
        
        
            
        # elif self.comboBox_repertato.currentText()!='No' or '':    
            # self.lineEdit_n_reperto.clear()
            # self.lineEdit_n_reperto.setText('1')
            # self.lineEdit_n_reperto.update()
            # for i in range(len(self.DATA_LIST)):
                # self.lineEdit_n_reperto.clear()
                # contatore = int(self.DATA_LIST[i].n_reperto)
                
                # #contatore.sort(reverse=False)
                # list.append(contatore)
                
               
                # list[-1]+=1
                
                # list.sort()
            # for e in list:    
                
                # self.lineEdit_n_reperto.setText(str(e))
                # self.lineEdit_n_reperto.update()
        # elif self.comboBox_repertato.currentText()=='':
            # self.lineEdit_n_reperto.clear()
            # self.lineEdit_n_reperto.setText('')
            # self.lineEdit_n_reperto.update()
        
        
    def numero_invetario(self):
        if self.checkBox_auto_inv.isChecked():
            QMessageBox.information(self, "Attenzione", "Hai attivato l'opzione autoincrementante Numero Inventario", QMessageBox.Ok)
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
                    QMessageBox.warning(self, "Messaggio", "Sistema di aggiornamento lista Sito: " + str(e), QMessageBox.Ok)
                elif self.L=='en':
                    QMessageBox.warning(self, "Message", "Site list update system: " + str(e), QMessageBox.Ok)
                elif self.L=='de':
                    QMessageBox.warning(self, "Nachricht", "Aktualisierungssystem für die Ausgrabungstätte: " + str(e), QMessageBox.Ok)
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


    def msg_sito(self):
        #self.model_a.database().close()
        conn = Connection()
        sito_set= conn.sito_set()
        sito_set_str = sito_set['sito_set']
        if bool(self.comboBox_sito.currentText()) and self.comboBox_sito.currentText()==sito_set_str:
            
            if self.L=='it':
                QMessageBox.information(self, "OK" ,"Sei connesso al sito: %s" % str(sito_set_str),QMessageBox.Ok) 
        
            elif self.L=='de':
                QMessageBox.information(self, "OK", "Sie sind mit der archäologischen Stätte verbunden: %s" % str(sito_set_str),QMessageBox.Ok) 
                
            else:
                QMessageBox.information(self, "OK", "You are connected to the site: %s" % str(sito_set_str),QMessageBox.Ok)     
        
        elif sito_set_str=='':    
            if self.L=='it':
                msg = QMessageBox.information(self, "Attenzione" ,"Non hai settato alcun sito. Vuoi settarne uno? click Ok altrimenti Annulla per  vedere tutti i record",QMessageBox.Ok | QMessageBox.Cancel) 
            elif self.L=='de':
                msg = QMessageBox.information(self, "Achtung", "Sie haben keine archäologischen Stätten eingerichtet. Klicken Sie auf OK oder Abbrechen, um alle Datensätze zu sehen",QMessageBox.Ok | QMessageBox.Cancel) 
            else:
                msg = QMessageBox.information(self, "Warning" , "You have not set up any archaeological site. Do you want to set one? click Ok otherwise Cancel to see all records",QMessageBox.Ok | QMessageBox.Cancel) 
            if msg == QMessageBox.Cancel:
                pass
            else: 
                dlg = pyArchInitDialog_Config(self)
                dlg.charge_list()
                dlg.exec_()
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
                self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]  ####darivedere
                self.fill_fields()
                self.BROWSE_STATUS = "b"
                self.SORT_STATUS = "n"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                self.setComboBoxEnable(["self.comboBox_sito"], "False")
            else:
                pass#
        except:
            if self.L=='it':
            
                QMessageBox.information(self, "Attenzione" ,"Non esiste questo sito: "'"'+ str(sito_set_str) +'"'" in questa scheda, Per favore distattiva la 'scelta sito' dalla scheda di configurazione plugin per vedere tutti i record oppure crea la scheda",QMessageBox.Ok) 
            elif self.L=='de':
            
                QMessageBox.information(self, "Warnung" , "Es gibt keine solche archäologische Stätte: "'""'+ str(sito_set_str) +'"'" in dieser Registerkarte, Bitte deaktivieren Sie die 'Site-Wahl' in der Plugin-Konfigurationsregisterkarte, um alle Datensätze zu sehen oder die Registerkarte zu erstellen",QMessageBox.Ok) 
            else:
            
                QMessageBox.information(self, "Warning" , "There is no such site: "'"'+ str(sito_set_str) +'"'" in this tab, Please disable the 'site choice' from the plugin configuration tab to see all records or create the tab",QMessageBox.Ok)  

    def on_pushButton_sort_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            dlg = SortPanelMain(self)
            dlg.insertItems(self.SORT_ITEMS)
            dlg.exec_()

            items, order_type = dlg.ITEMS, dlg.TYPE_ORDER

            self.SORT_ITEMS_CONVERTED = []
            for i in items:
                self.SORT_ITEMS_CONVERTED.append(self.CONVERSION_DICT[str(i)])

            self.SORT_MODE = order_type
            self.empty_fields()

            id_list = []
            for i in self.DATA_LIST:
                id_list.append(eval("i." + self.ID_TABLE))
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

    def on_toolButtonPreviewMedia_toggled(self):
        if self.L=='it':
            if self.toolButtonPreviewMedia.isChecked():
                QMessageBox.warning(self, "Messaggio",
                                    "Modalita' Preview Media US attivata. Le immagini delle US saranno visualizzate nella sezione Media",
                                    QMessageBox.Ok)
                self.loadMediaPreview()
            else:
                self.loadMediaPreview(1)
        elif self.L=='de':
            if self.toolButtonPreviewMedia.isChecked():
                QMessageBox.warning(self, "Message",
                                    "Modalität' Preview Media SE aktiviert. Die Bilder der SE werden in der Preview media Auswahl visualisiert",
                                    QMessageBox.Ok)
                self.loadMediaPreview()
            else:
                self.loadMediaPreview(1)
        else:
            if self.toolButtonPreviewMedia.isChecked():
                QMessageBox.warning(self, "Message",
                                    "SU Media Preview mode enabled. US images will be displayed in the Media section",
                                    QMessageBox.Ok)
                self.loadMediaPreview()
            else:
                self.loadMediaPreview(1) 

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
            if self.data_error_check() == 0:
                if self.records_equal_check() == 1:
                    if self.L=='it':
                        self.update_if(QMessageBox.warning(self, 'Errore',
                                                           "Il record e' stato modificato. Vuoi salvare le modifiche?",QMessageBox.Ok | QMessageBox.Cancel))
                    elif self.L=='de':
                        self.update_if(QMessageBox.warning(self, 'Error',
                                                           "Der Record wurde geändert. Möchtest du die Änderungen speichern?",
                                                           QMessageBox.Ok | QMessageBox.Cancel))
                                                    
                    else:
                        self.update_if(QMessageBox.warning(self, 'Error',
                                                           "The record has been changed. Do you want to save the changes?",
                                                           QMessageBox.Ok | QMessageBox.Cancel))
                    self.empty_fields()
                    self.SORT_STATUS = "n"
                    self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
                    self.enable_button(1)
                    self.fill_fields(self.REC_CORR)
                else:
                    if self.L=='it':
                        QMessageBox.warning(self, "ATTENZIONE", "Non è stata realizzata alcuna modifica.", QMessageBox.Ok)
                    elif self.L=='de':
                        QMessageBox.warning(self, "ACHTUNG", "Keine Änderung vorgenommen", QMessageBox.Ok)
                    else:
                        QMessageBox.warning(self, "Warning", "No changes have been made", QMessageBox.Ok)
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
                    QMessageBox.warning(self, "ATTENZIONE", "Problema nell'inserimento dati", QMessageBox.Ok)
                elif self.L=='de':
                    QMessageBox.warning(self, "ACHTUNG", "Problem der Dateneingabe", QMessageBox.Ok)
                else:
                    QMessageBox.warning(self, "Warning", "Problem with data entry", QMessageBox.Ok) 
    def on_toolButtonGis_toggled(self):
        if self.L=='it':
            if self.toolButtonGis.isChecked():
                QMessageBox.warning(self, "Messaggio",
                                    "Modalita' GIS attiva. Da ora le tue ricerche verranno visualizzate sul GIS",
                                    QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "Messaggio",
                                    "Modalita' GIS disattivata. Da ora le tue ricerche non verranno piu' visualizzate sul GIS",
                                    QMessageBox.Ok)
        elif self.L=='de':
            if self.toolButtonGis.isChecked():
                QMessageBox.warning(self, "Message",
                                    "Modalität' GIS aktiv. Von jetzt wird Deine Untersuchung mit Gis visualisiert",
                                    QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "Message",
                                    "Modalität' GIS deaktiviert. Von jetzt an wird deine Untersuchung nicht mehr mit Gis visualisiert",
                                    QMessageBox.Ok)
        else:
            if self.toolButtonGis.isChecked():
                QMessageBox.warning(self, "Message",
                                    "GIS mode active. From now on your searches will be displayed on the GIS",
                                    QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "Message",
                                    "GIS mode disabled. From now on, your searches will no longer be displayed on the GIS.",
                                    QMessageBox.Ok)
    
    
    def generate_list_foto(self):
        data_list_foto = []
        for i in range(len(self.DATA_LIST)):
        
            # conn = Connection()
            
            
            # thumb_path = conn.thumb_path()
            # thumb_path_str = thumb_path['thumb_path']
            
            # search_dict = {'id_entity': "'"+ str(eval("self.DATA_LIST[i].id_invmat"))+"'", 'entity_type' : "'REPERTO'"}
            
            # record_doc_list = self.DB_MANAGER.query_bool(search_dict, 'MEDIAVIEW')
        
         
            
            # for media in record_doc_list:
            
                # thumbnail = (thumb_path_str+media.filepath)
                
                    
                
                
            data_list_foto.append([
                
                str(self.DATA_LIST[i].sito.replace('_',' ')), #1
                str(self.DATA_LIST[i].n_reperto),  #6 
                #str(thumbnail),
                str(self.DATA_LIST[i].us),    #3
                str(self.DATA_LIST[i].definizione),#4
                str(self.DATA_LIST[i].datazione_reperto), #5
                str(self.DATA_LIST[i].stato_conservazione), #5
                str(self.DATA_LIST[i].tipo_contenitore), #7
                str(self.DATA_LIST[i].nr_cassa)])
            
        return data_list_foto
            
    def generate_list(self):
        data_list = []
        for i in range(len(self.DATA_LIST)):
        
            
                
            
            data_list.append([
                str(self.DATA_LIST[i].sito.replace('_',' ')), #0
                str(self.DATA_LIST[i].numero_inventario), #1
                str(self.DATA_LIST[i].area), #2
                str(self.DATA_LIST[i].us),    #3
                str(self.DATA_LIST[i].tipo_reperto),#4
                str(self.DATA_LIST[i].repertato), #5
                str(self.DATA_LIST[i].n_reperto),  #6 
                str(self.DATA_LIST[i].tipo_contenitore), #7
                str(self.DATA_LIST[i].nr_cassa), #8
                str(self.DATA_LIST[i].luogo_conservazione)])#9
                    
            
        return data_list
    def generate_list_pdf(self):
        data_list = []
        for i in range(len(self.DATA_LIST)):
            data_list.append([
                str(self.DATA_LIST[i].id_invmat),  # 1 - id_invmat
                str(self.DATA_LIST[i].sito.replace('_',' ')),  # 2 - sito
                int(self.DATA_LIST[i].numero_inventario),  # 3 - numero_inventario
                str(self.DATA_LIST[i].tipo_reperto),  # 4 - tipo_reperto
                str(self.DATA_LIST[i].criterio_schedatura),  # 5 - criterio_schedatura
                str(self.DATA_LIST[i].definizione),  # 6 - definizione
                str(self.DATA_LIST[i].descrizione),  # 7 - descrizione
                str(self.DATA_LIST[i].area),  # 8 - area
                str(self.DATA_LIST[i].us),  # 9 - us
                str(self.DATA_LIST[i].lavato),  # 10 - lavato
                str(self.DATA_LIST[i].nr_cassa),  # 11 - nr_cassa
                str(self.DATA_LIST[i].luogo_conservazione),  # 12 - luogo_conservazione
                str(self.DATA_LIST[i].stato_conservazione),  # 13 - stato_conservazione
                str(self.DATA_LIST[i].datazione_reperto),  # 14 - datazione_reperto
                str(self.DATA_LIST[i].elementi_reperto),  # 15 - elementi_reperto
                str(self.DATA_LIST[i].misurazioni),  # 16 - misurazioni
                str(self.DATA_LIST[i].rif_biblio),  # 17 - rif_biblio
                str(self.DATA_LIST[i].tecnologie),  # 18 - misurazioni
                str(self.DATA_LIST[i].tipo),  # 19 - tipo
                str(self.DATA_LIST[i].corpo_ceramico),  # 20 - corpo_ceramico
                str(self.DATA_LIST[i].rivestimento),  # 21 - rivestimento
                str(self.DATA_LIST[i].repertato),  # 22 - repertato
                str(self.DATA_LIST[i].diagnostico),
                str(self.DATA_LIST[i].n_reperto),
                str(self.DATA_LIST[i].tipo_contenitore)# 23 - diagnostico
            ])
        return data_list
    def on_pushButton_print_pressed(self):
        if self.L=='it':
            if self.checkBox_s_us.isChecked():
                US_pdf_sheet = generate_reperti_pdf()
                data_list = self.generate_list_pdf()
                US_pdf_sheet.build_Finds_sheets(data_list)
                QMessageBox.warning(self, 'Ok',"Esportazione terminata Schede Materiali",QMessageBox.Ok)
            else:   
                pass
        
            if self.checkBox_e_us.isChecked() :
                # US_index_pdf = generate_reperti_pdf()
                # data_list = self.generate_el_casse_pdf()
                               
                    
                        
                sito_ec = str(self.comboBox_sito.currentText())
                Mat_casse_pdf = generate_reperti_pdf()
                data_list = self.generate_el_casse_pdf(sito_ec)

                Mat_casse_pdf.build_index_Casse(data_list, sito_ec)
                QMessageBox.warning(self, 'Ok',"Esportazione terminata Elenco Casse",QMessageBox.Ok)
        
                
            else:
                pass
        
            if self.checkBox_e_foto_t.isChecked():
                US_index_pdf = generate_reperti_pdf()
                data_list_foto = self.generate_list_foto()
        
                try:
                        
                    US_index_pdf.build_index_Foto(data_list_foto, data_list_foto[0][0])
                    QMessageBox.warning(self, 'Ok',"Esportazione terminata Elenco Reperti",QMessageBox.Ok)
                                       
                        # else:
                            # QMessageBox.warning(self, 'ATTENZIONE',"L'elenco foto non può essere esportato perchè non hai immagini taggate.",QMessageBox.Ok)
                except Exception as e :
                    QMessageBox.warning(self, 'ATTENZIONE',str(e),QMessageBox.Ok)
            
            if self.checkBox_e_foto.isChecked():
                US_index_pdf = generate_reperti_pdf()
                data_list = self.generate_list()
        
                try:
                        
                    US_index_pdf.build_index_Foto_2(data_list, data_list[0][0])
                    QMessageBox.warning(self, 'Ok',"Esportazione terminata Elenco Inventario",QMessageBox.Ok)
                                       
                        # else:
                            # QMessageBox.warning(self, 'ATTENZIONE',"L'elenco foto non può essere esportato perchè non hai immagini taggate.",QMessageBox.Ok)
                except Exception as e :
                    QMessageBox.warning(self, 'ATTENZIONE',str(e),QMessageBox.Ok)
        
        elif self.L=='de':
            if self.checkBox_s_us.isChecked():
                US_pdf_sheet = generate_reperti_pdf()
                data_list = self.generate_list_pdf()
                US_pdf_sheet.build_Finds_sheets_de(data_list)
                QMessageBox.warning(self, 'Ok',"Export beendet",QMessageBox.Ok)
            else:   
                pass
        
            if self.checkBox_e_us.isChecked() :
                # US_index_pdf = generate_reperti_pdf()
                # data_list = self.generate_el_casse_pdf()
                               
                    
                        
                sito_ec = str(self.comboBox_sito.currentText())
                Mat_casse_pdf = generate_reperti_pdf()
                data_list = self.generate_el_casse_pdf(sito_ec)

                Mat_casse_pdf.build_index_Casse_de(data_list, sito_ec)
                QMessageBox.warning(self, 'Ok',"Export beendet",QMessageBox.Ok)
        
                
            else:
                pass
        
            if self.checkBox_e_foto_t.isChecked():
                US_index_pdf = generate_reperti_pdf()
                data_list_foto = self.generate_list_foto()
        
                try:
                        
                    US_index_pdf.build_index_Foto(data_list_foto, data_list_foto[0][0])
                    QMessageBox.warning(self, 'Ok',"Export beendet",QMessageBox.Ok)
                                       
                        # else:
                            # QMessageBox.warning(self, 'ATTENZIONE',"L'elenco foto non può essere esportato perchè non hai immagini taggate.",QMessageBox.Ok)
                except Exception as e :
                    QMessageBox.warning(self, 'Warnung',str(e),QMessageBox.Ok)
            
            if self.checkBox_e_foto.isChecked():
                US_index_pdf = generate_reperti_pdf()
                data_list = self.generate_list()
        
                try:
                        
                    US_index_pdf.build_index_Foto_2_de(data_list, data_list[0][0])
                    QMessageBox.warning(self, 'Ok',"Export beendet",QMessageBox.Ok)
                                       
                        # else:
                            # QMessageBox.warning(self, 'ATTENZIONE',"L'elenco foto non può essere esportato perchè non hai immagini taggate.",QMessageBox.Ok)
                except Exception as e :
                    QMessageBox.warning(self, 'Warnung',str(e),QMessageBox.Ok)
        
        
        else:
            if self.checkBox_s_us.isChecked():
                US_pdf_sheet = generate_reperti_pdf()
                data_list = self.generate_list_pdf()
                US_pdf_sheet.build_Finds_sheets_en(data_list)
                QMessageBox.warning(self, 'Ok',"Exportation Forms complited",QMessageBox.Ok)
            else:   
                pass
        
            if self.checkBox_e_us.isChecked() :
                # US_index_pdf = generate_reperti_pdf()
                # data_list = self.generate_el_casse_pdf()
                               
                    
                        
                sito_ec = str(self.comboBox_sito.currentText())
                Mat_casse_pdf = generate_reperti_pdf()
                data_list = self.generate_el_casse_pdf(sito_ec)

                Mat_casse_pdf.build_index_Casse_en(data_list, sito_ec)
                QMessageBox.warning(self, 'Ok',"Exportation list box complited",QMessageBox.Ok)
        
                
            else:
                pass
        
            if self.checkBox_e_foto_t.isChecked():
                US_index_pdf = generate_reperti_pdf()
                data_list_foto = self.generate_list_foto()
        
                try:
                        
                    US_index_pdf.build_index_Foto(data_list_foto, data_list_foto[0][0])
                    QMessageBox.warning(self, 'Ok',"Exportation Artefact complited",QMessageBox.Ok)
                                       
                        # else:
                            # QMessageBox.warning(self, 'ATTENZIONE',"L'elenco foto non può essere esportato perchè non hai immagini taggate.",QMessageBox.Ok)
                except Exception as e :
                    QMessageBox.warning(self, 'Warning',str(e),QMessageBox.Ok)
            
            if self.checkBox_e_foto.isChecked():
                US_index_pdf = generate_reperti_pdf()
                data_list = self.generate_list()
        
                try:
                        
                    US_index_pdf.build_index_Foto_2_en(data_list, data_list[0][0])
                    QMessageBox.warning(self, 'Ok',"Exportation list complited",QMessageBox.Ok)
                                       
                        # else:
                            # QMessageBox.warning(self, 'ATTENZIONE',"L'elenco foto non può essere esportato perchè non hai immagini taggate.",QMessageBox.Ok)
                except Exception as e :
                    QMessageBox.warning(self, 'Warning',str(e),QMessageBox.Ok)
    
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
   
    def on_pushButton_convert_pressed(self):
        # if not bool(self.setPathpdf()):    
            # QMessageBox.warning(self, "INFO", "devi scegliere un file pdf",
                                # QMessageBox.Ok)
        
        try:
            pdf_file = self.lineEdit_pdf_path.text()
            filename=pdf_file.split("/")[-1]
            docx_file = self.PDFFOLDER+'/'+filename+'.docx'

            # convert pdf to docx
            parse(pdf_file, docx_file, start=self.lineEdit_pag1.text(), end=self.lineEdit_pag2.text())
            QMessageBox.information(self, "INFO", "Conversione terminata",
                                QMessageBox.Ok)
                                
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e),
                                QMessageBox.Ok)
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
            QMessageBox.warning(self,'Warning','Il campo cassa non deve essere vuoto', QMessageBox.Ok)
    ####################################################
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

            QMessageBox.warning(self, 'tk', str(tup_key), QMessageBox.Ok)
            QMessageBox.warning(self, 'tk', str(diz_strutture_x_us), QMessageBox.Ok)
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
                QMessageBox.warning(self, 'Tus', str(us), QMessageBox.Ok)
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
        QMessageBox.warning(self, 'us_field', str(us_field), QMessageBox.Ok)

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

        area = self.lineEdit_area.text()
        us = self.lineEdit_us.text()
        nr_cassa = self.lineEdit_nr_cassa.text()
        nr_inv = self.lineEdit_num_inv.text()
        
        if self.L=='it':
            if EC.data_is_empty(str(self.comboBox_sito.currentText())) == 0:
                QMessageBox.warning(self, "ATTENZIONE", "Campo Sito. \n Il campo non deve essere vuoto", QMessageBox.Ok)
                test = 1

            if EC.data_is_empty(str(self.lineEdit_num_inv.text())) == 0:
                QMessageBox.warning(self, "ATTENZIONE", "Campo Numero inventario \n Il campo non deve essere vuoto",
                                    QMessageBox.Ok)
                test = 1

            if nr_inv != "":
                if EC.data_is_int(nr_inv) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Campo Numero inventario\nIl valore deve essere di tipo numerico", QMessageBox.Ok)
                    test = 1

            if area != "":
                if EC.data_is_int(area) == 0:
                    QMessageBox.warning(self, "ATTENZIONE", "Campo Area.\nIl valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

            if us != "":
                if EC.data_is_int(us) == 0:
                    QMessageBox.warning(self, "ATTENZIONE", "Campo US.\nIl valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

            if nr_cassa != "":
                if EC.data_is_int(nr_cassa) == 0:
                    QMessageBox.warning(self, "ATTENZIONE", "Campo Numero Cassa.\nIl valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1
        elif self.L=='de':
            if EC.data_is_empty(str(self.comboBox_sito.currentText())) == 0:
                QMessageBox.warning(self, "ACHTUNG", " Feld Ausgrabungstätte \n Das Feld darf nicht leer sein", QMessageBox.Ok)
                test = 1

            if EC.data_is_empty(str(self.lineEdit_num_inv.text())) == 0:
                QMessageBox.warning(self, "ACHTUNG", " Feld Nr. Inv. \n Das Feld darf nicht leer sein", QMessageBox.Ok)
                test = 1

            if nr_inv != "":
                if EC.data_is_int(nr_inv) == 0:
                    QMessageBox.warning(self, "ACHTUNG", "Feld Nr. Inv. \n Der Wert muss numerisch eingegeben werden",
                                        QMessageBox.Ok)
                    test = 1

            if area != "":
                if EC.data_is_int(area) == 0:
                    QMessageBox.warning(self, "ACHTUNG", "Feld Areal \n Der Wert muss numerisch eingegeben werden",
                                        QMessageBox.Ok)
                    test = 1

            if us != "":
                if EC.data_is_int(us) == 0:
                    QMessageBox.warning(self, "ACHTUNG", "Feld SE. \n Der Wert muss numerisch eingegeben werden",
                                        QMessageBox.Ok)
                    test = 1

            if nr_cassa != "":
                if EC.data_is_int(nr_cassa) == 0:
                    QMessageBox.warning(self, "ACHTUNG", "Feld Box \n Der Wert muss numerisch eingegeben werden",
                                        QMessageBox.Ok)
                    test = 1
        else:
            if EC.data_is_empty(str(self.comboBox_sito.currentText())) == 0:
                QMessageBox.warning(self, "WARNING", "Site Field \n The field must not be empty", QMessageBox.Ok)
                test = 1

            if EC.data_is_empty(str(self.lineEdit_num_inv.text())) == 0:
                QMessageBox.warning(self, "WARNING", "Nr. Inv. Field \n The field must not be empty", QMessageBox.Ok)
                test = 1

            if nr_inv != "":
                if EC.data_is_int(nr_inv) == 0:
                    QMessageBox.warning(self, "WARNING", "Area Field \n The value must be numerical",
                                        QMessageBox.Ok)
                    test = 1

            if area != "":
                if EC.data_is_int(area) == 0:
                    QMessageBox.warning(self, "WARNING", "Nr. Inv. Field \n The value must be numerical",
                                        QMessageBox.Ok)
                    test = 1

            if us != "":
                if EC.data_is_int(us) == 0:
                    QMessageBox.warning(self, "WARNING", "SU Field \n The value must be numerical",
                                        QMessageBox.Ok)
                    test = 1

            if nr_cassa != "":
                if EC.data_is_int(nr_cassa) == 0:
                    QMessageBox.warning(self, "WARNING", "Box Field \n The value must be numerical",
                                        QMessageBox.Ok)
                    test = 1
        
        
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

        try:
            if self.lineEdit_num_inv.text() == "":
                inv =None
            else:
                inv = int(self.lineEdit_num_inv.text())
            
            if self.lineEdit_area.text() == "":
                area =None
            else:
                area = int(self.lineEdit_area.text())

            if self.lineEdit_us.text() == "":
                us =None
            else:
                us = int(self.lineEdit_us.text())

            if self.lineEdit_nr_cassa.text() == "":
                nr_cassa =None
            else:
                nr_cassa = int(self.lineEdit_nr_cassa.text())

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

            data = self.DB_MANAGER.insert_values_reperti(
                self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, self.ID_TABLE) + 1,  # 0 - IDsito
                str(self.comboBox_sito.currentText()),  # 1 - Sito
                inv,  # 2 - num_inv
                str(self.comboBox_tipo_reperto.currentText()),  # 3 - tipo_reperto
                str(self.comboBox_criterio_schedatura.currentText()),  # 4 - criterio
                str(self.comboBox_definizione.currentText()),  # 5 - definizione
                str(self.textEdit_descrizione_reperto.toPlainText()),  # 6 - descrizione
                area,
                us,
                str(self.comboBox_lavato.currentText()),  # 9 - lavato
                nr_cassa,
                str(self.lineEdit_luogo_conservazione.text()),  # 11 - luogo conservazione
                str(self.comboBox_conservazione.currentText()),  # 12 - stato di conservazione
                str(self.lineEdit_datazione_rep.text()),  # 13 - datazione reperto
                str(elementi_reperto),  # 14 - elementi reperto
                str(misurazioni),  # 15 - misurazioni
                str(rif_biblio),  # 16 - rif biblio
                str(tecnologie),  # 17 - tecnologie
                forme_minime,
                forme_massime,
                totale_frammenti,
                str(self.lineEditCorpoCeramico.text()),  # 20 - corpo ceramico
                str(self.lineEditRivestimento.text()),  # 21   rivestimento
                diametro_orlo,  # 22 - diametro orlo
                peso,  # 23- peso
                str(self.lineEdit_tipo.text()),  # 24 - tipo
                eve_orlo,  # 25 - eve_orlo,
                str(self.comboBox_repertato.currentText()),  # 9 - lavato
                str(self.comboBox_diagnostico.currentText()),  # 9 - lavato
                n_reperto,
                str(self.lineEdit_tipo_contenitore.text()),
                str(self.comboBox_struttura.currentText()),
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
                        
                        QMessageBox.warning(self, "Error", "Errore: valore duplicato\n" + str(msg), QMessageBox.Ok)
                        
                    elif self.L=='de':
                        msg = self.ID_TABLE + " bereits in der Datenbank"
                        QMessageBox.warning(self, "Error", "Error " + str(msg), QMessageBox.Ok)  
                    else:
                        msg = self.ID_TABLE + " exist in db"
                        QMessageBox.warning(self, "Error", "Error " + str(msg), QMessageBox.Ok)  
                else:
                    msg = e
                    QMessageBox.warning(self, "Error", "Error 1 \n" + str(msg), QMessageBox.Ok)
                return 0
            
        except Exception as e:
            QMessageBox.warning(self, "Error", "Error 2 \n" + str(e), QMessageBox.Ok)
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

    def check_record_state(self):
        ec = self.data_error_check()
        if ec == 1:
            return 1  # ci sono errori di immissione
        elif self.records_equal_check() == 1 and ec == 0:
            if self.L=='it':
                self.update_if(
                
                    QMessageBox.warning(self, 'Errore', "Il record e' stato modificato. Vuoi salvare le modifiche?",
                                        QMessageBox.Ok | QMessageBox.Cancel))
            elif self.L=='de':
                self.update_if(
                    QMessageBox.warning(self, 'Errore', "Der Record wurde geändert. Möchtest du die Änderungen speichern?",
                                        QMessageBox.Ok | QMessageBox.Cancel))
            else:
                self.update_if(
                    QMessageBox.warning(self, "Error", "The record has been changed. You want to save the changes?",
                                        QMessageBox.Ok | QMessageBox.Cancel))
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
            if self.toolButtonPreviewMedia.isChecked():
                self.loadMediaPreview(1)

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
                    QMessageBox.warning(self, "Attenzione", "Sei al primo record!", QMessageBox.Ok)
                elif self.L=='de':
                    QMessageBox.warning(self, "Achtung", "du befindest dich im ersten Datensatz!", QMessageBox.Ok)
                else:
                    QMessageBox.warning(self, "Warning", "You are to the first record!", QMessageBox.Ok)        
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
                    QMessageBox.warning(self, "Attenzione", "Sei all'ultimo record!", QMessageBox.Ok)
                elif self.L=='de':
                    QMessageBox.warning(self, "Achtung", "du befindest dich im letzten Datensatz!", QMessageBox.Ok)
                else:
                    QMessageBox.warning(self, "Error", "You are to the first record!", QMessageBox.Ok)  
            else:
                try:
                    self.empty_fields()
                    self.fill_fields(self.REC_CORR)
                    self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
                except:# Exception as e:
                    pass#QMessageBox.warning(self, "Error", str(e), QMessageBox.Ok)

    def on_pushButton_delete_pressed(self):
        
        if self.L=='it':
            msg = QMessageBox.warning(self, "Attenzione!!!",
                                      "Vuoi veramente eliminare il record? \n L'azione è irreversibile",
                                      QMessageBox.Ok | QMessageBox.Cancel)
            if msg == QMessageBox.Cancel:
                QMessageBox.warning(self, "Messagio!!!", "Azione Annullata!")
            else:
                try:
                    id_to_delete = eval("self.DATA_LIST[self.REC_CORR]." + self.ID_TABLE)
                    self.DB_MANAGER.delete_one_record(self.TABLE_NAME, self.ID_TABLE, id_to_delete)
                    self.charge_records()  # charge records from DB
                    QMessageBox.warning(self, "Messaggio!!!", "Record eliminato!")
                except Exception as e:
                    QMessageBox.warning(self, "Messaggio!!!", "Tipo di errore: " + str(e))
                if not bool(self.DATA_LIST):
                    QMessageBox.warning(self, "Attenzione", "Il database è vuoto!", QMessageBox.Ok)
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
                                      QMessageBox.Ok | QMessageBox.Cancel)
            if msg == QMessageBox.Cancel:
                QMessageBox.warning(self, "Message!!!", "Aktion annulliert!")
            else:
                try:
                    id_to_delete = eval("self.DATA_LIST[self.REC_CORR]." + self.ID_TABLE)
                    self.DB_MANAGER.delete_one_record(self.TABLE_NAME, self.ID_TABLE, id_to_delete)
                    self.charge_records()  # charge records from DB
                    QMessageBox.warning(self, "Message!!!", "Record gelöscht!")
                except Exception as e:
                    QMessageBox.warning(self, "Messagge!!!", "Errortyp: " + str(e))
                if not bool(self.DATA_LIST):
                    QMessageBox.warning(self, "Achtung", "Die Datenbank ist leer!", QMessageBox.Ok)
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
                                      QMessageBox.Ok | QMessageBox.Cancel)
            if msg == QMessageBox.Cancel:
                QMessageBox.warning(self, "Message!!!", "Action deleted!")
            else:
                try:
                    id_to_delete = eval("self.DATA_LIST[self.REC_CORR]." + self.ID_TABLE)
                    self.DB_MANAGER.delete_one_record(self.TABLE_NAME, self.ID_TABLE, id_to_delete)
                    self.charge_records()  # charge records from DB
                    QMessageBox.warning(self, "Message!!!", "Record deleted!")
                except Exception as e:
                    QMessageBox.warning(self, "Message!!!", "error type: " + str(e))
                if not bool(self.DATA_LIST):
                    QMessageBox.warning(self, "Warning", "the db is empty!", QMessageBox.Ok)
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
                                    QMessageBox.Ok)
            elif self.L=='de':
                QMessageBox.warning(self, "ACHTUNG", "Um eine neue Abfrage zu starten drücke  'new search' ",
                                    QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "WARNING", "To perform a new search click on the 'new search' button ",
                                    QMessageBox.Ok) 
        else:
            ##scavato
            if self.lineEdit_num_inv.text() != "":
                numero_inventario = int(self.lineEdit_num_inv.text())
            else:
                numero_inventario = ""

            if self.lineEdit_area.text() != "":
                area = int(self.lineEdit_area.text())
            else:
                area = ""

            if self.lineEdit_us.text() != "":
                us = int(self.lineEdit_us.text())
            else:
                us = ""

            if self.lineEdit_nr_cassa.text() != "":
                nr_cassa = int(self.lineEdit_nr_cassa.text())
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
                self.TABLE_FIELDS[6]: area,
                self.TABLE_FIELDS[7]: us,
                self.TABLE_FIELDS[8]: "'" + str(self.comboBox_lavato.currentText()) + "'",
                self.TABLE_FIELDS[9]: nr_cassa,
                self.TABLE_FIELDS[10]: "'" + str(self.lineEdit_luogo_conservazione.text()) + "'",
                self.TABLE_FIELDS[11]: "'" + str(self.comboBox_conservazione.currentText()) + "'",
                self.TABLE_FIELDS[12]: "'" + str(self.lineEdit_datazione_rep.text()) + "'",
                self.TABLE_FIELDS[17]: forme_minime,
                self.TABLE_FIELDS[18]: forme_massime,
                self.TABLE_FIELDS[19]: totale_frammenti,
                self.TABLE_FIELDS[20]: "'" + str(self.lineEditCorpoCeramico.text()) + "'",
                self.TABLE_FIELDS[21]: "'" + str(self.lineEditRivestimento.text()) + "'",
                self.TABLE_FIELDS[22]: diametro_orlo,
                self.TABLE_FIELDS[23]: peso,
                self.TABLE_FIELDS[24]: "'" + str(self.lineEdit_tipo.text()) + "'",
                self.TABLE_FIELDS[25]: eve_orlo,
                self.TABLE_FIELDS[26]: "'" + str(self.comboBox_repertato.currentText()) + "'",
                self.TABLE_FIELDS[27]: "'" + str(self.comboBox_diagnostico.currentText()) + "'",
                self.TABLE_FIELDS[28]: n_reperto,
                self.TABLE_FIELDS[29]: "'" + str(self.lineEdit_tipo_contenitore.text()) + "'",
                self.TABLE_FIELDS[30]: "'" + str(self.comboBox_struttura.currentText()) + "'",
            }

            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)

            if not bool(search_dict):
                if self.L=='it':
                    QMessageBox.warning(self, "ATTENZIONE", "Non è stata impostata nessuna ricerca!!!", QMessageBox.Ok)
                elif self.L=='de':
                    QMessageBox.warning(self, "ACHTUNG", "Keine Abfrage definiert!!!", QMessageBox.Ok)
                else:
                    QMessageBox.warning(self, " WARNING", "No search has been set!!!", QMessageBox.Ok)      
            else:
                res = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
                if not bool(res):
                    if self.L=='it':
                        QMessageBox.warning(self, "ATTENZIONE", "Non è stato trovato nessun record!", QMessageBox.Ok)
                    elif self.L=='de':
                        QMessageBox.warning(self, "ACHTUNG", "Keinen Record gefunden!", QMessageBox.Ok)
                    else:
                        QMessageBox.warning(self, "WARNING", "No record found!", QMessageBox.Ok)

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

                    QMessageBox.warning(self, "Message", "%s %d %s" % strings, QMessageBox.Ok)

        if check_for_buttons == 1:
            self.enable_button_search(1)

    def on_pushButton_tot_fram_pressed(self):
        if self.L=='it':
            self.update_tot_frammenti(QMessageBox.warning(self, 'ATTENZIONE',
                                                          "Vuoi aggiornare tutti i frammenti (OK), oppure solo il record corrente (Cancel)?",
                                                          QMessageBox.Ok | QMessageBox.Cancel))
        elif self.L=='de':
            self.update_tot_frammenti(QMessageBox.warning(self, 'Achtung',
                                                          "Möchten Sie alle Fragmente (OK) oder nur den aktuellen Datensatz (Abbrechen) aktualisieren?",
                                                          QMessageBox.Ok | QMessageBox.Cancel))
        
        else:
            self.update_tot_frammenti(QMessageBox.warning(self, 'Warning',
                                                          "Do you want to update all fragments (OK), or just the current record (Cancel)?",
                                                          QMessageBox.Ok | QMessageBox.Cancel))
        # blocco per quantificare dalla tabella interna il numero totale di frammenti

    def update_tot_frammenti(self, c):
        if c == QMessageBox.Ok:
            for i in range(len(self.DATA_LIST)):
                temp_dataset = ()
                id_invmat = self.DATA_LIST[i].id_invmat
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

            search_dict = {
                'id_invmat': "'" + str(eval("self.DATA_LIST[int(self.REC_CORR)]." + self.ID_TABLE)) + "'"}
            records = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
            self.lineEditTotFram.setText(str(records[0].totale_frammenti))
        else:
            lista_valori = self.table2dict('self.tableWidget_elementi_reperto')

            tot_framm = 0
            for sing_fr in lista_valori:
                if sing_fr[1] == 'frammenti' or 'frammento'or 'fragment' or 'fragments':
                    tot_framm += int(sing_fr[2])

            self.lineEditTotFram.setText(str(tot_framm))

    def update_if(self, msg):
        rec_corr = self.REC_CORR
        if msg == QMessageBox.Ok:
            test = self.update_record()
            if test == 1:
                id_list = []
                for i in self.DATA_LIST:
                    id_list.append(eval("i." + self.ID_TABLE))
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
            self.DB_MANAGER.update(self.MAPPER_TABLE_CLASS,
                                   self.ID_TABLE,
                                   [eval("int(self.DATA_LIST[self.REC_CORR]." + self.ID_TABLE + ")")],
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

    def charge_struttura(self):
        try:
            sito = str(self.comboBox_sito.currentText())
            area = str(self.lineEdit_area.text())
            us = str(self.lineEdit_us.text())
            search_dict = {
                'sito': "'" + sito + "'",
                'area': "'" + str(eval("self.DATA_LIST[int(self.REC_CORR)].area"))+ "'",
                'us': "'" + str(eval("self.DATA_LIST[int(self.REC_CORR)].us"))+"'"
                
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
            
        except:
            pass
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
                id_list.append(eval("i." + self.ID_TABLE))

            temp_data_list = self.DB_MANAGER.query_sort(id_list, [self.ID_TABLE], 'asc', self.MAPPER_TABLE_CLASS,
                                                        self.ID_TABLE)
            for i in temp_data_list:
                self.DATA_LIST.append(i)

    def setComboBoxEditable(self, f, n):
        field_names = f
        value = n

        for fn in field_names:
            cmd = '{}{}{}{}'.format(fn, '.setEditable(', n, ')')
            eval(cmd)

    def setComboBoxEnable(self, f, v):
        field_names = f
        value = v

        for fn in field_names:
            cmd = '{}{}{}{}'.format(fn, '.setEnabled(', v, ')')
            eval(cmd)

    def datestrfdate(self):
        now = date.today()
        today = now.strftime("%d-%m-%Y")
        return today

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
                item = QTableWidgetItem(str(self.data_list[row][col]))
                exec_str = ('%s.setItem(%d,%d,item)') % (self.table_name, row, col)
                eval(exec_str)

    def insert_new_row(self, table_name):
        """insert new row into a table based on table_name"""
        cmd = table_name + ".insertRow(0)"
        eval(cmd)

    def remove_row(self, table_name):
        """insert new row into a table based on table_name"""

        table_row_count_cmd = ("%s.rowCount()") % (table_name)
        table_row_count = eval(table_row_count_cmd)
        rowSelected_cmd = ("%s.selectedIndexes()") % (table_name)
        rowSelected = eval(rowSelected_cmd)
        try:
            rowIndex = (rowSelected[1].row())
            cmd = ("%s.removeRow(%d)") % (table_name, rowIndex)
            eval(cmd)
        except:
            if self.L=='it':
                QMessageBox.warning(self, "Messaggio", "Devi selezionare una riga", QMessageBox.Ok)
            elif self.L=='de':
                QMessageBox.warning(self, "Message", "Sie müssen eine Zeile markieren.", QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "Message", "You must select a row", QMessageBox.Ok)   

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
        self.lineEdit_area.clear()  # 7 - area
        self.lineEdit_us.clear()  # 8 - US
        self.comboBox_lavato.setEditText("")  # 9 - lavato
        self.lineEdit_nr_cassa.clear  # 10 - nr_cassa
        self.lineEdit_luogo_conservazione.clear()  # 11 - luogo_conservazione
        self.comboBox_conservazione.setEditText("")  # 12 - stato conservazione
        self.lineEdit_datazione_rep.clear()  # 13 - datazione reperto

        self.lineEditFormeMin.clear()
        self.lineEditFormeMax.clear()
        self.lineEditTotFram.clear()
        self.lineEditRivestimento.clear()
        self.lineEditCorpoCeramico.clear()

        self.lineEdit_diametro_orlo.clear()
        self.lineEdit_peso.clear()
        self.lineEdit_tipo.clear()
        self.lineEdit_eve_orlo.clear()

        self.comboBox_repertato.setEditText("")  # 9 - repertato
        self.comboBox_diagnostico.setEditText("")  # 9 - diagnostico
        
        for i in range(elementi_reperto_row_count):
            self.tableWidget_elementi_reperto.removeRow(0)
        self.insert_new_row("self.tableWidget_elementi_reperto")  # 14 - elementi reperto

        for i in range(misurazioni_row_count):
            self.tableWidget_misurazioni.removeRow(0)
        self.insert_new_row("self.tableWidget_misurazioni")  # 15 - misurazioni

        for i in range(rif_biblio_row_count):
            self.tableWidget_rif_biblio.removeRow(0)
        self.insert_new_row("self.tableWidget_rif_biblio")  # 16 - rif_biblio

        for i in range(tecnologie_row_count):
            self.tableWidget_tecnologie.removeRow(0)
        self.insert_new_row("self.tableWidget_tecnologie")  # 17 - misurazioni
        self.lineEdit_n_reperto.clear()
        self.lineEdit_tipo_contenitore.clear()
        self.comboBox_struttura.setEditText("")  # 9 - diagnostico
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
        self.lineEdit_area.clear()  # 7 - area
        self.lineEdit_us.clear()  # 8 - US
        self.comboBox_lavato.setEditText("")  # 9 - lavato
        self.lineEdit_nr_cassa.clear()  # 10 - nr_cassa
        self.lineEdit_luogo_conservazione.clear()  # 11 - luogo_conservazione
        self.comboBox_conservazione.setEditText("")  # 12 - stato conservazione
        self.lineEdit_datazione_rep.clear()  # 13 - datazione reperto

        self.lineEditFormeMin.clear()
        self.lineEditFormeMax.clear()
        self.lineEditTotFram.clear()
        self.lineEditRivestimento.clear()
        self.lineEditCorpoCeramico.clear()

        self.lineEdit_diametro_orlo.clear()
        self.lineEdit_peso.clear()
        self.lineEdit_tipo.clear()
        self.lineEdit_eve_orlo.clear()

        self.comboBox_repertato.setEditText("")  # 9 - repertato
        self.comboBox_diagnostico.setEditText("")  # 9 - diagnostico
        
        for i in range(elementi_reperto_row_count):
            self.tableWidget_elementi_reperto.removeRow(0)
        self.insert_new_row("self.tableWidget_elementi_reperto")  # 14 - elementi reperto

        for i in range(misurazioni_row_count):
            self.tableWidget_misurazioni.removeRow(0)
        self.insert_new_row("self.tableWidget_misurazioni")  # 15 - misurazioni

        for i in range(rif_biblio_row_count):
            self.tableWidget_rif_biblio.removeRow(0)
        self.insert_new_row("self.tableWidget_rif_biblio")  # 16 - rif_biblio

        for i in range(tecnologie_row_count):
            self.tableWidget_tecnologie.removeRow(0)
        self.insert_new_row("self.tableWidget_tecnologie")  # 17 - misurazioni
        self.lineEdit_n_reperto.clear()
        self.lineEdit_tipo_contenitore.clear()
        self.comboBox_struttura.setEditText("")  # 9 - diagnostico
    def fill_fields(self, n=0):
        self.rec_num = n
        # QMessageBox.warning(self, "check fill fields", str(self.rec_num),  QMessageBox.Ok)
        try:
            
            
            if str(self.DATA_LIST[self.rec_num].numero_inventario) =='None':
                num_inv=''
            else:
                num_inv=str(self.DATA_LIST[self.rec_num].numero_inventario)
            
            if str(self.DATA_LIST[self.rec_num].area) =='None':
                area=''
            else:
                area=str(self.DATA_LIST[self.rec_num].area)
            
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
            
            
            if str(self.DATA_LIST[self.rec_num].totale_frammenti) == 'None':
                totale_frammenti = ''
            else:
                totale_frammenti = str(self.DATA_LIST[self.rec_num].totale_frammenti)
            
            if str(self.DATA_LIST[self.rec_num].n_reperto) == 'None':
                n_reperto = ''
            else:
                n_reperto = str(self.DATA_LIST[self.rec_num].n_reperto)
            
            
            
            
            
            
            str(self.comboBox_sito.setEditText(self.DATA_LIST[self.rec_num].sito))  # 1 - Sito
            str(self.lineEdit_num_inv.setText(num_inv))  # 2 - num_inv
            
            
            str(self.comboBox_tipo_reperto.setEditText(self.DATA_LIST[self.rec_num].tipo_reperto))  # 3 - Tipo reperto
            str(self.comboBox_criterio_schedatura.setEditText(
                self.DATA_LIST[self.rec_num].criterio_schedatura))  # 4 - Criterio schedatura
            str(self.comboBox_definizione.setEditText(self.DATA_LIST[self.rec_num].definizione))  # 5 - definizione
            str(self.textEdit_descrizione_reperto.setText(self.DATA_LIST[self.rec_num].descrizione))  # 6 - descrizione
            
            str(self.lineEdit_area.setText(area))
            
            str(self.lineEdit_us.setText(us))
            
            

            self.comboBox_lavato.setEditText(str(self.DATA_LIST[self.rec_num].lavato))

            str(self.lineEdit_nr_cassa.setText(nr_cassa))
            
            
            str(self.lineEdit_luogo_conservazione.setText(
                self.DATA_LIST[self.rec_num].luogo_conservazione))  # 11 - luogo_conservazione

            self.comboBox_conservazione.setEditText(
                str(self.DATA_LIST[self.rec_num].stato_conservazione))  # 12 - stato conservazione

            str(self.lineEdit_datazione_rep.setText(
                self.DATA_LIST[self.rec_num].datazione_reperto))  # 13 - datazione reperto

            self.tableInsertData("self.tableWidget_elementi_reperto",
                                 self.DATA_LIST[self.rec_num].elementi_reperto)  # 14 - elementi_reperto

            self.tableInsertData("self.tableWidget_misurazioni",
                                 self.DATA_LIST[self.rec_num].misurazioni)  # 15 - campioni

            self.tableInsertData("self.tableWidget_rif_biblio",
                                 self.DATA_LIST[self.rec_num].rif_biblio)  # 16 - rif biblio

            self.tableInsertData("self.tableWidget_tecnologie",
                                 self.DATA_LIST[self.rec_num].tecnologie)  # 17 - rapporti
            
            
            str(self.lineEditFormeMin.setText(forme_minime))
            
            
            str(self.lineEditFormeMax.setText(forme_massime))
            

            str(self.lineEditTotFram.setText(totale_frammenti))

            
            self.lineEditRivestimento.setText(str(self.DATA_LIST[self.rec_num].rivestimento))

            self.lineEditCorpoCeramico.setText(str(self.DATA_LIST[self.rec_num].corpo_ceramico))

            if self.DATA_LIST[self.rec_num].diametro_orlo == None:  # 10 - nr_cassa
                self.lineEdit_diametro_orlo.setText("")
            else:
                self.lineEdit_diametro_orlo.setText(str(self.DATA_LIST[self.rec_num].diametro_orlo))

            if self.DATA_LIST[self.rec_num].peso == None:  # 10 - nr_cassa
                self.lineEdit_peso.setText("")
            else:
                self.lineEdit_peso.setText(str(self.DATA_LIST[self.rec_num].peso))

            self.lineEdit_tipo.setText(str(self.DATA_LIST[self.rec_num].tipo))

            if self.DATA_LIST[self.rec_num].eve_orlo == None:  # 10 - nr_cassa
                self.lineEdit_eve_orlo.setText("")
            else:
                self.lineEdit_eve_orlo.setText(str(self.DATA_LIST[self.rec_num].eve_orlo))
            
            
            self.comboBox_repertato.setEditText(str(self.DATA_LIST[self.rec_num].repertato))
            
            
            self.comboBox_diagnostico.setEditText(str(self.DATA_LIST[self.rec_num].diagnostico))
            
            str(self.lineEdit_n_reperto.setText(n_reperto))
            
            self.lineEdit_tipo_contenitore.setText(str(self.DATA_LIST[self.rec_num].tipo_contenitore))
            self.comboBox_struttura.setEditText(
                str(self.DATA_LIST[self.rec_num].struttura))
            if self.toolButtonPreviewMedia.isChecked():
                self.loadMediaPreview()
            self.comboBox_struttura.setEditText(
                str(self.DATA_LIST[self.rec_num].struttura))
        except :
            pass#QMessageBox.warning(self, "Error Fill Fields", str(e), QMessageBox.Ok)

    def set_rec_counter(self, t, c):
        self.rec_tot = t
        self.rec_corr = c
        self.label_rec_tot.setText(str(self.rec_tot))
        self.label_rec_corrente.setText(str(self.rec_corr))

    def set_LIST_REC_TEMP(self):
        # TableWidget

        # elementi reperto
        elementi_reperto = self.table2dict("self.tableWidget_elementi_reperto")
        ##misurazioni
        misurazioni = self.table2dict("self.tableWidget_misurazioni")
        ##rif_biblio
        rif_biblio = self.table2dict("self.tableWidget_rif_biblio")
        ##tecnologie
        tecnologie = self.table2dict("self.tableWidget_tecnologie")

        ##scavato
        if self.lineEdit_num_inv.text() == "":
            inv =None
        else:
            inv = int(self.lineEdit_num_inv.text())
        
        if self.lineEdit_area.text() == "":
            area =None
        else:
            area = int(self.lineEdit_area.text())

        if self.lineEdit_us.text() == "":
            us =None
        else:
            us = int(self.lineEdit_us.text())

        if self.lineEdit_nr_cassa.text() == "":
            nr_cassa =None
        else:
            nr_cassa = int(self.lineEdit_nr_cassa.text())

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
        # data
        self.DATA_LIST_REC_TEMP = [
            str(self.comboBox_sito.currentText()),  # 1 - Sito
            str(inv),  # 2 - num_inv
            str(self.comboBox_tipo_reperto.currentText()),  # 3 - tipo_reperto
            str(self.comboBox_criterio_schedatura.currentText()),  # 4 - criterio schedatura
            str(self.comboBox_definizione.currentText()),  # 5 - definizione
            str(self.textEdit_descrizione_reperto.toPlainText()),  # 6 - descrizione
            str(area),
            str(us),

            str(self.comboBox_lavato.currentText()),  # 9 - lavato
            str(nr_cassa),
            str(self.lineEdit_luogo_conservazione.text()),  # 11 - luogo conservazione
            str(self.comboBox_conservazione.currentText()),  # 12 - stato conservazione
            str(self.lineEdit_datazione_rep.text()),  # 13 - datazione reperto
            str(elementi_reperto),  # 14 - elementi reperto
            str(misurazioni),  # 15 - misurazioni
            str(rif_biblio),  # 16 - rif_biblio
            str(tecnologie),  # 17 - tecnologie
            str(forme_minime),  # 18 - forme minime
            str(forme_massime),  # 19 - forme massime
            str(totale_frammenti),  # 20 - totale frammenti
            str(self.lineEditCorpoCeramico.text()),  # 21 - corpoceramico
            str(self.lineEditRivestimento.text()),  # 22 - riverstimento
            str(diametro_orlo),  # 23 - diametro orlo
            str(peso),  # 24 - peso
            str(self.lineEdit_tipo.text()),  # 25 - tipo
            str(eve_orlo),  # 26 - eve orlo
            str(self.comboBox_repertato.currentText()),  # 27 - repertato
            str(self.comboBox_diagnostico.currentText()),
            str(n_reperto),
            str(self.lineEdit_tipo_contenitore.text()),# 28 - diagnostico
            str(self.comboBox_struttura.currentText()),
        ]

    def enable_button(self, n):
        self.pushButton_connect.setEnabled(n)

        self.pushButton_new_rec.setEnabled(n)

        self.pushButton_view_all_2.setEnabled(n)

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

        self.pushButton_view_all_2.setEnabled(n)

        self.pushButton_first_rec.setEnabled(n)

        self.pushButton_last_rec.setEnabled(n)

        self.pushButton_prev_rec.setEnabled(n)

        self.pushButton_next_rec.setEnabled(n)

        self.pushButton_delete.setEnabled(n)

        self.pushButton_save.setEnabled(n)

        self.pushButton_sort.setEnabled(n)

    def setTableEnable(self, t, v):
        tab_names = t
        value = v

        for tn in tab_names:
            cmd = '{}{}{}{}'.format(tn, '.setEnabled(', v, ')')
            eval(cmd)

    def set_LIST_REC_CORR(self):
        self.DATA_LIST_REC_CORR = []
        for i in self.TABLE_FIELDS:
            self.DATA_LIST_REC_CORR.append(eval("unicode(self.DATA_LIST[self.REC_CORR]." + i + ")"))

    def records_equal_check(self):
        self.set_LIST_REC_TEMP()
        self.set_LIST_REC_CORR()


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
   
    def on_pushButton_convert_pressed(self):
        # if not bool(self.setPathpdf()):    
            # QMessageBox.warning(self, "INFO", "devi scegliere un file pdf",
                                # QMessageBox.Ok)
        
        try:
            pdf_file = self.lineEdit_pdf_path.text()
            filename=pdf_file.split("/")[-1]
            docx_file = self.PDFFOLDER+'/'+filename+'.docx'

            # convert pdf to docx
            parse(pdf_file, docx_file, start=self.lineEdit_pag1.text(), end=self.lineEdit_pag2.text())
            QMessageBox.information(self, "INFO", "Conversion complite",
                                QMessageBox.Ok)
                                
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e),
                                QMessageBox.Ok)
    def openpdfDir(self):
        HOME = os.environ['PYARCHINIT_HOME']
        path = '{}{}{}'.format(HOME, os.sep, "pyarchinit_PDF_folder")

        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])


## Class end

# if __name__ == "__main__":
    # app = QApplication(sys.argv)
    # ui = pyarchinit_US()
    # ui.show()
    # sys.exit(app.exec_())
