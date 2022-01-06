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

from builtins import range
from builtins import str
from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtWidgets import QDialog, QMessageBox
from qgis.PyQt.uic import loadUiType
from qgis.gui import QgsMapToolPan
from qgis.core import QgsSettings, Qgis
from ..modules.db.pyarchinit_conn_strings import Connection
from ..modules.db.pyarchinit_db_manager import Pyarchinit_db_management
from ..modules.db.pyarchinit_utility import Utility
from ..modules.gis.pyarchinit_pyqgis import Pyarchinit_pyqgis
from ..modules.utility.pyarchinit_error_check import Error_check
from ..gui.imageViewer import ImageViewer
from ..gui.sortpanelmain import SortPanelMain
from ..gui.pyarchinitConfigDialog import pyArchInitDialog_Config
MAIN_DIALOG_CLASS, _ = loadUiType(os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'Deteta.ui'))


class pyarchinit_Deteta(QDialog, MAIN_DIALOG_CLASS):
    L=QgsSettings().value("locale/userLocale")[0:2]
    if L=='it':
        MSG_BOX_TITLE = "PyArchInit - Scheda US"
    elif L=='en':
        MSG_BOX_TITLE = "PyArchInit - Age form"
    elif L=='de':
        MSG_BOX_TITLE = "PyArchInit - Formular Todesalter"
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
    SORT_ITEMS_CONVERTED = ''
    UTILITY = Utility()
    DB_MANAGER = ""
    TABLE_NAME = 'deteta_table'
    MAPPER_TABLE_CLASS = "DETETA"
    NOME_SCHEDA = "Scheda Determinazione dell'età di morte"
    ID_TABLE = "id_det_eta"
    if L =='it':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Sito": "sito",
            "Num individuo": "nr_individuo",
            "Range sinfisi min": "sinf_min",
            "Range sinfisi max": "sinf_max",
            "Range sinfisi min 2": "sinf_min_2",
            "Range sinfisi max 2": "sinf_max_2",
            "SSPIA eta\'": "SSPIA",
            "SSPIB eta\'": "SSPIB",
            "SSPIC eta\'": "SSPIC",
            "SSPID eta\'": "SSPID",
            "Range superficie auricolare min": "sup_aur_min",
            "Range superficie auricolare max": "sup_aur_max",
            "Range superficie auricolare min 2": "sup_aur_min_2",
            "Range superficie auricolare max 2": "sup_aur_max_2",
            "Range mascellare superiore min": "ms_sup_min",
            "Range mascellare superiore max": "ms_sup_max",
            "Range mascellare inferiore min": "ms_inf_min",
            "Range mascellare inferiore max": "ms_inf_max",
            "Range usura dentaria min": "usura_min",
            "Range usura dentaria max": "usura_max",
            "Id suture endocraniche": "Id_endo",
            "Is suture endocraniche": "Is_endo",
            "IId suture endocraniche": "IId_endo",
            "IIs suture endocraniche": "IIs_endo",
            "IIId suture endocraniche": "IIId_endo",
            "IIIs suture endocraniche": "IIIs_endo",
            "IV suture endocraniche": "IV_endo",
            "V suture endocraniche": "V_endo",
            "VI suture endocraniche": "VI_endo",
            "VII suture endocraniche": "VII_endo",
            "VIIId suture endocraniche": "VIIId_endo",
            "VIIIs suture endocraniche": "VIIIs_endo",
            "IXd suture endocraniche": "IXd_endo",
            "IXs suture endocraniche": "IXs_endo",
            "Xd suture endocraniche": "Xd_endo",
            "Xs suture endocraniche": "Xs_endo",
            "Range suture endocraniche min": "endo_min",
            "Range suture endocraniche max": "endo_max",
            "Suture volta 1": "volta_1",
            "Suture volta 2": "volta_2",
            "Suture volta 3": "volta_3",
            "Suture volta 4": "volta_4",
            "Suture volta 5": "volta_5",
            "Suture volta 6": "volta_6",
            "Suture volta 7": "volta_7",
            "Suture antero laterali 6": "lat_6",
            "Suture antero laterali 7": "lat_7",
            "Suture antero laterali 8": "lat_8",
            "Suture antero laterali 9": "lat_9",
            "Suture antero laterali 10": "lat_10",
            "Range suture volta min": "volta_min",
            "Range suture volta max": "volta_max",
            "Range suture antero laterali min": "ant_lat_min",
            "Range suture antero laterali max": "ant_lat_max",
            "Range suture ectocraniche min": "ecto_min",
            "Range suture ectocraniche max": "ecto_max"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Sito",
            "Num individuo",
            "Range sinfisi min",
            "Range sinfisi max",
            "Range sinfisi min 2",
            "Range sinfisi max 2",
            "SSPIA eta\'",
            "SSPIB eta\'",
            "SSPIC eta\'",
            "SSPID eta\'",
            "Range superficie auricolare min",
            "Range superficie auricolare max"
            "Range superficie auricolare min 2",
            "Range superficie auricolare max 2",
            "Range mascellare superiore min",
            "Range mascellare superiore max",
            "Range mascellare inferiore min",
            "Range mascellare inferiore max",
            "Range usura dentaria min",
            "Range usura dentaria max",
            "Id suture endocraniche",
            "Is suture endocraniche",
            "IId suture endocraniche",
            "IIs suture endocraniche",
            "IIId suture endocraniche",
            "IIIs suture endocraniche",
            "IV suture endocraniche",
            "V suture endocraniche",
            "VI suture endocraniche",
            "VII suture endocraniche",
            "VIIId suture endocraniche",
            "VIIIs suture endocraniche",
            "IXd suture endocraniche",
            "IXs suture endocraniche",
            "Xd suture endocraniche",
            "Xs suture endocraniche",
            "Range suture endocraniche min",
            "Range suture endocraniche max",
            "Suture volta 1",
            "Suture volta 2",
            "Suture volta 3",
            "Suture volta 4",
            "Suture volta 5",
            "Suture volta 6",
            "Suture volta 7",
            "Suture antero laterali 6",
            "Suture antero laterali 7",
            "Suture antero laterali 8",
            "Suture antero laterali 9",
            "Suture antero laterali 10",
            "Range suture volta min",
            "Range suture volta max",
            "Range suture antero laterali min",
            "Range suture antero laterali max",
            "Range suture ectocraniche min",
            "Range suture ectocraniche max"
        ]
    elif L =='de':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Ausgrabungsstätte": "sito",
            "N. Individuell": "nr_individuo",
            "Zustand Symphyse min": "sinf_min",
            "Zustand Symphyse max": "sinf_max",
            "Zustand Symphyse min 2": "sinf_min_2",
            "Zustand Symphyse max 2": "sinf_max_2",
            "SSPIA'": "SSPIA",
            "SSPIB'": "SSPIB",
            "SSPIC'": "SSPIC",
            "SSPID'": "SSPID",
            "Zustand der Artikulationsflächen min": "sup_aur_min",
            "Zustand der Artikulationsflächen max": "sup_aur_max",
            "Zustand der Artikulationsflächen min 2": "sup_aur_min_2",
            "Zustand der Artikulationsflächen max 2": "sup_aur_max_2",
            "Zustand des Unterkiefers untere min": "ms_sup_min",
            "Zustand des Unterkiefers untere max": "ms_sup_max",
            "Zustand des Unterkiefers obere": "ms_inf_min",
            "Zustand des Unterkiefers obere max": "ms_inf_max",
            "Abkauungsgrad min": "usura_min",
            "Abkauungsgrad max": "usura_max",
            "Id Suturae im endocranialen Bereich": "Id_endo",
            "Is Suturae im endocranialen Bereich": "Is_endo",
            "IId Suturae im endocranialen Bereich": "IId_endo",
            "IIs Suturae im endocranialen Bereich": "IIs_endo",
            "IIId Suturae im endocranialen Bereich": "IIId_endo",
            "IIIs Suturae im endocranialen Bereich": "IIIs_endo",
            "IV Suturae im endocranialen Bereich": "IV_endo",
            "V Suturae im endocranialen Bereich": "V_endo",
            "VI Suturae im endocranialen Bereich": "VI_endo",
            "VII Suturae im endocranialen Bereich": "VII_endo",
            "VIIId Suturae im endocranialen Bereich": "VIIId_endo",
            "VIIIs Suturae im endocranialen Bereich": "VIIIs_endo",
            "IXd Suturae im endocranialen Bereich": "IXd_endo",
            "IXs Suturae im endocranialen Bereich": "IXs_endo",
            "Xd Suturae im endocranialen Bereich": "Xd_endo",
            "Xs Suturae im endocranialen Bereich": "Xs_endo",
            "Zustand Suturae im endocranialen Bereich min": "endo_min",
            "Zustand Suturae im endocranialen Bereich max": "endo_max",
            "Zeit Suturae 1": "volta_1",
            "Zeit Suturae 2": "volta_2",
            "Zeit Suturae 3": "volta_3",
            "Zeit Suturae 4": "volta_4",
            "Zeit Suturae 5": "volta_5",
            "Zeit Suturae 6": "volta_6",
            "Zeit Suturae 7": "volta_7",
            "Antero-lateral Suturae 6": "lat_6",
            "Antero-lateral Suturae 7": "lat_7",
            "Antero-lateral Suturae 8": "lat_8",
            "Antero-lateral Suturae 9": "lat_9",
            "Antero-lateral Suturae 10": "lat_10",
            "Zustand Zeit Suturae min": "volta_min",
            "Zustand Zeit Suturae max": "volta_max",
            "Zustand Antero-lateral Suturae min": "ant_lat_min",
            "Zustand Antero-lateral Suturae max": "ant_lat_max",
            "Zustand Ectocraniale Suturae min": "ecto_min",
            "Zustand Ectocraniale Suturae max": "ecto_max"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Ausgrabungsstätte",
            "N. Individuell",
            "Zustand Symphyse min",
            "Zustand Symphyse max",
            "Zustand Symphyse min 2",
            "Zustand Symphyse max 2",
            "SSPIA'",
            "SSPIB'",
            "SSPIC'",
            "SSPID'",
            "Zustand der Artikulationsflächen min",
            "Zustand der Artikulationsflächen max",
            "Zustand der Artikulationsflächen min 2",
            "Zustand der Artikulationsflächen max 2",
            "Zustand des Unterkiefers untere min",
            "Zustand des Unterkiefers untere max",
            "Zustand des Unterkiefers obere",
            "Zustand des Unterkiefers obere max",
            "Abkauungsgrad min",
            "Abkauungsgrad max",
            "Id Suturae im endocranialen Bereich",
            "Is Suturae im endocranialen Bereich",
            "IId Suturae im endocranialen Bereich",
            "IIs Suturae im endocranialen Bereich",
            "IIId Suturae im endocranialen Bereich",
            "IIIs Suturae im endocranialen Bereich",
            "IV Suturae im endocranialen Bereich",
            "V Suturae im endocranialen Bereich",
            "VI Suturae im endocranialen Bereich",
            "VII Suturae im endocranialen Bereich",
            "VIIId Suturae im endocranialen Bereich",
            "VIIIs Suturae im endocranialen Bereich",
            "IXd Suturae im endocranialen Bereich",
            "IXs Suturae im endocranialen Bereich",
            "Xd Suturae im endocranialen Bereich",
            "Xs Suturae im endocranialen Bereich",
            "Zustand Suturae im endocranialen Bereich min",
            "Zustand Suturae im endocranialen Bereich max",
            "Zeit Suturae 1",
            "Zeit Suturae 2",
            "Zeit Suturae 3",
            "Zeit Suturae 4",
            "Zeit Suturae 5",
            "Zeit Suturae 6",
            "Zeit Suturae 7",
            "Antero-lateral Suturae 6",
            "Antero-lateral Suturae 7",
            "Antero-lateral Suturae 8",
            "Antero-lateral Suturae 9",
            "Antero-lateral Suturae 10",
            "Zustand Zeit Suturae min",
            "Zustand Zeit Suturae max",
            "Zustand Antero-lateral Suturae min",
            "Zustand Antero-lateral Suturae max",
            "Zustand Ectocraniale Suturae min",
            "Zustand Ectocraniale Suturae max"
        ]
    else:
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Site": "sito",
            "Individual nr.": "nr_individuo",
            "Range symphysis min": "sinf_min",
            "Range symphysis max": "sinf_max",
            "Range symphysis min 2": "sinf_min_2",
            "Range symphysis max 2": "sinf_max_2",
            "SSPIA'": "SSPIA",
            "SSPIB'": "SSPIB",
            "SSPIC'": "SSPIC",
            "SSPID'": "SSPID",
            "Range earmold surface min": "sup_aur_min",
            "Range earmold surface max": "sup_aur_max",
            "Range earmold surface min 2": "sup_aur_min_2",
            "Range earmold surface max 2": "sup_aur_max_2",
            "Range upper maxillary min": "ms_sup_min",
            "Range upper maxillary max": "ms_sup_max",
            "Range lower maxillary min": "ms_inf_min",
            "Range lower maxillary max": "ms_inf_max",
            "Range dental wear min": "usura_min",
            "Range dental wear max": "usura_max",
            "Id endocrine sutures": "Id_endo",
            "Is endocrine sutures": "Is_endo",
            "IId endocrine sutures": "IId_endo",
            "IIs endocrine sutures": "IIs_endo",
            "IIId endocrine sutures": "IIId_endo",
            "IIIs endocrine sutures": "IIIs_endo",
            "IV endocrine sutures": "IV_endo",
            "V endocrine sutures": "V_endo",
            "VI endocrine sutures": "VI_endo",
            "VII endocrine sutures": "VII_endo",
            "VIIId endocrine sutures": "VIIId_endo",
            "VIIIs endocrine sutures": "VIIIs_endo",
            "IXd endocrine sutures": "IXd_endo",
            "IXs endocrine sutures": "IXs_endo",
            "Xd endocrine sutures": "Xd_endo",
            "Xs endocrine sutures": "Xs_endo",
            "Range endocrine sutures min": "endo_min",
            "Range endocrine sutures max": "endo_max",
            "sutures vault 1": "volta_1",
            "sutures vault 2": "volta_2",
            "sutures vault 3": "volta_3",
            "sutures vault 4": "volta_4",
            "sutures vault 5": "volta_5",
            "sutures vault 6": "volta_6",
            "sutures vault 7": "volta_7",
            "sutures antero lateral 6": "lat_6",
            "sutures antero lateral 7": "lat_7",
            "sutures antero lateral 8": "lat_8",
            "sutures antero lateral 9": "lat_9",
            "sutures antero lateral 10": "lat_10",
            "Range sutures vault min": "volta_min",
            "Range sutures vault max": "volta_max",
            "Range sutures antero laterali min": "ant_lat_min",
            "Range sutures antero laterali max": "ant_lat_max",
            "Range sutures ectocrine min": "ecto_min",
            "Range sutures ectocrine max": "ecto_max"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Site",
            "Individual nr.",
            "Range symphysis min",
            "Range symphysis max",
            "Range symphysis min 2",
            "Range symphysis max 2",
            "SSPIA'",
            "SSPIB'",
            "SSPIC'",
            "SSPID'",
            "Range earmold surface min",
            "Range earmold surface max",
            "Range earmold surface min 2",
            "Range earmold surface max 2",
            "Range upper maxillary min",
            "Range upper maxillary max",
            "Range lower maxillary min",
            "Range lower maxillary max",
            "Range dental wear min",
            "Range dental wear max",
            "Id endocrine sutures",
            "Is endocrine sutures",
            "IId endocrine sutures",
            "IIs endocrine sutures",
            "IIId endocrine sutures",
            "IIIs endocrine sutures",
            "IV endocrine sutures",
            "V endocrine sutures",
            "VI endocrine sutures",
            "VII endocrine sutures",
            "VIIId endocrine sutures",
            "VIIIs endocrine sutures",
            "IXd endocrine sutures",
            "IXs endocrine sutures",
            "Xd endocrine sutures",
            "Xs endocrine sutures",
            "Range endocrine sutures min",
            "Range endocrine sutures max",
            "sutures vault 1",
            "sutures vault 2",
            "sutures vault 3",
            "sutures vault 4",
            "sutures vault 5",
            "sutures vault 6",
            "sutures vault 7",
            "sutures antero lateral 6",
            "sutures antero lateral 7",
            "sutures antero lateral 8",
            "sutures antero lateral 9",
            "sutures antero lateral 10",
            "Range sutures vault min",
            "Range sutures vault max",
            "Range sutures antero laterali min",
            "Range sutures antero laterali max",
            "Range sutures ectocrine min",
            "Range sutures ectocrine max"
        ]   
    TABLE_FIELDS = [
        'sito',
        'nr_individuo',
        "sinf_min",
        "sinf_max",
        "sinf_min_2",
        "sinf_max_2",
        "SSPIA",
        "SSPIB",
        "SSPIC",
        "SSPID",
        "sup_aur_min",
        "sup_aur_max",
        "sup_aur_min_2",
        "sup_aur_max_2",
        "ms_sup_min",
        "ms_sup_max",
        "ms_inf_min",
        "ms_inf_max",
        "usura_min",
        "usura_max",
        "Id_endo",
        "Is_endo",
        "IId_endo",
        "IIs_endo",
        "IIId_endo",
        "IIIs_endo",
        "IV_endo",
        "V_endo",
        "VI_endo",
        "VII_endo",
        "VIIId_endo",
        "VIIIs_endo",
        "IXd_endo",
        "IXs_endo",
        "Xd_endo",
        "Xs_endo",
        "endo_min",
        "endo_max",
        "volta_1",
        "volta_2",
        "volta_3",
        "volta_4",
        "volta_5",
        "volta_6",
        "volta_6",
        "volta_7",
        "lat_7",
        "lat_8",
        "lat_9",
        "lat_10",
        "volta_min",
        "volta_max",
        "ant_lat_min",
        "ant_lat_max",
        "ecto_max",
        "ecto_min"
    ]

    DIZ_VALORI_SINFISI_FEMMINA_Suchey_Brooks = {1: (15, 24),
                                                2: (19, 40),
                                                3: (21, 53),
                                                4: (26, 70),
                                                5: (25, 83),
                                                6: (42, 87)}

    DIZ_VALORI_SINFISI_MASCHIO_Suchey_Brooks = {1: (15, 23),
                                                2: (19, 34),
                                                3: (21, 46),
                                                4: (23, 57),
                                                5: (27, 66),
                                                6: (34, 86)}

    DIZ_VALORI_SINFISI_2_FEMMINA_Kimmerle = {1: (20, 28),
                                             2: (30, 36),
                                             3: (44, 44),
                                             4: (45, 48),
                                             5: (50, 55),
                                             6: (60, 66),
                                             7: (81, 86),
                                             8: (90, 96)}

    DIZ_VALORI_SINFISI_2_MASCHIO_Kimmerle = {1: (25, 27),
                                             2: (30, 35),
                                             3: (40, 46),
                                             4: (50, 55),
                                             5: (60, 65),
                                             6: (70, 74),
                                             7: (81, 86)}

    DIZ_VALORI_SUP_AUR = {'[1, 1, 1, 1]': (20, 29),
                          '[1, 1, 1, 2]': (20, 39),
                          '[1, 1, 2, 1]': (20, 29),
                          '[1, 1, 2, 2]': (20, 49),
                          '[1, 2, 1, 1]': (20, 49),
                          '[1, 2, 1, 2]': (20, 60),
                          '[1, 2, 2, 1]': (20, 60),
                          '[1, 2, 2, 2]': (30, 59),
                          '[2, 1, 1, 2]': (20, 49),
                          '[2, 1, 2, 1]': (20, 39),
                          '[2, 1, 2, 2]': (20, 49),
                          '[2, 1, 1, 1]': (20, 39),
                          '[2, 2, 1, 1]': (20, 49),
                          '[2, 2, 1, 2]': (30, 59),
                          '[2, 2, 2, 1]': (30, 59),
                          '[2, 2, 2, 2]': (30, 59),
                          '[1, 3, 1, 1]': (30, 59),
                          '[1, 3, 1, 2]': (40, 100),
                          '[1, 3, 2, 1]': (40, 100),
                          '[1, 3, 2, 2]': (40, 100),
                          '[2, 3, 1, 1]': (40, 100),
                          '[2, 3, 1, 2]': (40, 100),
                          '[2, 3, 2, 1]': (40, 100),
                          '[2, 3, 2, 2]': (50, 100),
                          '[1, 4, 1, 1]': (30, 100),
                          '[1, 4, 1, 2]': (40, 100),
                          '[1, 4, 2, 1]': (50, 100),
                          '[1, 4, 2, 2]': (50, 100),
                          '[2, 4, 1, 1]': (40, 100),
                          '[2, 4, 2, 1]': (50, 100),
                          '[2, 4, 1, 2]': (50, 100),
                          '[2, 4, 2, 2]': (50, 100),
                          '[0, 1, 1, 1]': (20, 39),
                          '[0, 1, 1, 2]': (20, 49),
                          '[0, 1, 2, 1]': (20, 39),
                          '[0, 1, 2, 2]': (20, 49),
                          '[0, 2, 1, 1]': (20, 49),
                          '[0, 2, 1, 2]': (30, 60),
                          '[0, 2, 2, 1]': (30, 60),
                          '[0, 2, 2, 2]': (30, 59),
                          '[2, 0, 1, 2]': (20, 49),
                          '[2, 0, 2, 1]': (20, 59),
                          '[2, 0, 2, 2]': (20, 40),
                          '[2, 0, 1, 1]': (20, 50),
                          '[2, 2, 0, 1]': (20, 59),
                          '[2, 2, 0, 2]': (30, 59),
                          '[2, 2, 2, 0]': (30, 59),
                          '[0, 3, 1, 1]': (30, 59),
                          '[0, 3, 1, 2]': (40, 100),
                          '[0, 3, 2, 1]': (40, 100),
                          '[0, 3, 2, 2]': (40, 100),
                          '[2, 3, 0, 1]': (40, 100),
                          '[2, 3, 0, 2]': (40, 100),
                          '[2, 3, 2, 0]': (40, 100),
                          '[0, 4, 1, 1]': (30, 100),
                          '[0, 4, 1, 2]': (40, 100),
                          '[0, 4, 2, 1]': (50, 100),
                          '[0, 4, 2, 2]': (50, 100),
                          '[2, 4, 0, 1]': (40, 100),
                          '[2, 4, 2, 0]': (50, 100),
                          '[2, 4, 0, 2]': (50, 100)}

    DIZ_VALORI_SUP_AUR_2 = {'[1, 1, 1, 1]': (20, 29),
                            '[1, 1, 1, 2]': (20, 49),
                            '[1, 1, 2, 1]': (20, 29),
                            '[1, 1, 2, 2]': (20, 60),
                            '[1, 2, 1, 1]': (20, 39),
                            '[1, 2, 1, 2]': (30, 59),
                            '[1, 2, 2, 1]': (20, 60),
                            '[1, 2, 2, 2]': (40, 100),
                            '[2, 1, 1, 2]': (20, 49),
                            '[2, 1, 2, 1]': (20, 49),
                            '[2, 1, 2, 2]': (30, 59),
                            '[2, 1, 1, 1]': (20, 39),
                            '[2, 2, 1, 1]': (20, 49),
                            '[2, 2, 1, 2]': (30, 100),
                            '[2, 2, 2, 1]': (30, 100),
                            '[2, 2, 2, 2]': (40, 100),
                            '[1, 3, 1, 1]': (20, 60),
                            '[1, 3, 1, 2]': (40, 100),
                            '[1, 3, 2, 1]': (40, 100),
                            '[1, 3, 2, 2]': (50, 100),
                            '[2, 3, 1, 1]': (40, 100),
                            '[2, 3, 1, 2]': (50, 100),
                            '[2, 3, 2, 1]': (50, 100),
                            '[2, 3, 2, 2]': (60, 100),
                            '[1, 4, 1, 1]': (40, 100),
                            '[1, 4, 1, 2]': (50, 100),
                            '[1, 4, 2, 1]': (50, 100),
                            '[1, 4, 2, 2]': (50, 100),
                            '[2, 4, 1, 1]': (50, 100),
                            '[2, 4, 2, 1]': (60, 100),
                            '[2, 4, 1, 2]': (60, 100),
                            '[2, 4, 2, 2]': (60, 100),
                            '[0, 1, 1, 1]': (20, 39),
                            '[0, 1, 1, 2]': (20, 49),
                            '[0, 1, 2, 1]': (20, 49),
                            '[0, 1, 2, 2]': (30, 59),
                            '[0, 2, 1, 1]': (20, 49),
                            '[0, 2, 1, 2]': (30, 59),
                            '[0, 2, 2, 1]': (30, 60),
                            '[0, 2, 2, 2]': (40, 100),
                            '[2, 0, 1, 2]': (20, 49),
                            '[2, 0, 2, 1]': (20, 49),
                            '[2, 0, 2, 2]': (30, 59),
                            '[2, 0, 1, 1]': (20, 49),
                            '[2, 2, 0, 1]': (20, 49),
                            '[2, 2, 0, 2]': (30, 100),
                            '[2, 2, 2, 0]': (30, 100),
                            '[0, 3, 1, 1]': (40, 60),
                            '[0, 3, 1, 2]': (40, 100),
                            '[0, 3, 2, 1]': (40, 100),
                            '[0, 3, 2, 2]': (50, 100),
                            '[2, 3, 0, 1]': (40, 100),
                            '[2, 3, 0, 2]': (50, 100),
                            '[2, 3, 2, 0]': (50, 100),
                            '[0, 4, 1, 1]': (40, 100),
                            '[0, 4, 1, 2]': (50, 100),
                            '[0, 4, 2, 1]': (50, 100),
                            '[0, 4, 2, 2]': (50, 100),
                            '[2, 4, 0, 1]': (50, 100),
                            '[2, 4, 2, 0]': (60, 100),
                            '[2, 4, 0, 2]': (60, 100)}

    DB_SERVER = "not defined"  ####nuovo sistema sort

    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.pyQGIS = Pyarchinit_pyqgis(iface)
        self.setupUi(self)

        self.currentLayerId = None
        try:
            self.on_pushButton_connect_pressed()
        except Exception as e:
            QMessageBox.warning(self, "Connection System", str(e), QMessageBox.Ok)

        self.fill_fields()
        self.customize_GUI()
        self.set_sito()
        self.msg_sito()

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

    def enable_button_Suchey_Brooks(self, n):
        self.pushButton_I_fase.setEnabled(n)
        self.pushButton_II_fase.setEnabled(n)
        self.pushButton_III_fase.setEnabled(n)
        self.pushButton_IV_fase.setEnabled(n)
        self.pushButton_V_fase.setEnabled(n)
        self.pushButton_VI_fase.setEnabled(n)

    def enable_button_Kimmerle_m(self, n):
        self.pushButton_m_1.setEnabled(n)
        self.pushButton_m_2.setEnabled(n)
        self.pushButton_m_3.setEnabled(n)
        self.pushButton_m_4.setEnabled(n)
        self.pushButton_m_5.setEnabled(n)
        self.pushButton_m_6.setEnabled(n)
        self.pushButton_m_7.setEnabled(n)

    def enable_button_Kimmerle_f(self, n):
        self.pushButton_f_1.setEnabled(n)
        self.pushButton_f_2.setEnabled(n)
        self.pushButton_f_3.setEnabled(n)
        self.pushButton_f_4.setEnabled(n)
        self.pushButton_f_5.setEnabled(n)
        self.pushButton_f_6.setEnabled(n)
        self.pushButton_f_7.setEnabled(n)
        self.pushButton_f_8.setEnabled(n)

    def on_pushButton_connect_pressed(self):
        conn = Connection()
        conn_str = conn.conn_str()
        test_conn = conn_str.find('sqlite')

        if test_conn == 0:
            self.DB_SERVER = "sqlite"

        try:
            self.DB_MANAGER = Pyarchinit_db_management(conn_str)
            self.DB_MANAGER.connection()
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

    def customize_GUI(self):
        query_res = self.sex_from_individuo_table()
        if not bool(query_res):
            self.enable_button_Kimmerle_f(0)
            self.enable_button_Kimmerle_m(0)
            self.enable_button_Suchey_Brooks(0)
        else:
            sesso = query_res[0].sesso
            if self.L=='it':
                if sesso == "Maschio":
                    self.enable_button_Kimmerle_m(1)
                    self.enable_button_Kimmerle_f(0)
                    self.enable_button_Suchey_Brooks(1)
                elif sesso == "Femmina":
                    self.enable_button_Kimmerle_f(1)
                    self.enable_button_Kimmerle_m(0)
                    self.enable_button_Suchey_Brooks(1)
                else:
                    self.enable_button_Kimmerle_f(0)
                    self.enable_button_Kimmerle_m(0)
                    self.enable_button_Suchey_Brooks(0)
            elif self.L=='de':
                if sesso == "Männlich":
                    self.enable_button_Kimmerle_m(1)
                    self.enable_button_Kimmerle_f(0)
                    self.enable_button_Suchey_Brooks(1)
                elif sesso == "Weiblich":
                    self.enable_button_Kimmerle_f(1)
                    self.enable_button_Kimmerle_m(0)
                    self.enable_button_Suchey_Brooks(1)
                else:
                    self.enable_button_Kimmerle_f(0)
                    self.enable_button_Kimmerle_m(0)
                    self.enable_button_Suchey_Brooks(0) 
            else:
                if sesso == "Male":
                    self.enable_button_Kimmerle_m(1)
                    self.enable_button_Kimmerle_f(0)
                    self.enable_button_Suchey_Brooks(1)
                elif sesso == "Female":
                    self.enable_button_Kimmerle_f(1)
                    self.enable_button_Kimmerle_m(0)
                    self.enable_button_Suchey_Brooks(1)
                else:
                    self.enable_button_Kimmerle_f(0)
                    self.enable_button_Kimmerle_m(0)
                    self.enable_button_Suchey_Brooks(0)     

    def loadMapPreview(self, mode=0):
        pass

    def charge_list(self):
        sito_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('site_table', 'sito', 'SITE'))
        try:
            sito_vl.remove('')
        except:
            pass

        self.comboBox_sito.clear()

        sito_vl.sort()
        self.comboBox_sito.addItems(sito_vl)

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
            
                QMessageBox.information(self, "Warnung" , "Es gibt keine solche archäologische Stätte: "'""'+ str(site_set_str) +'"'" in dieser Registerkarte, Bitte deaktivieren Sie die 'Site-Wahl' in der Plugin-Konfigurationsregisterkarte, um alle Datensätze zu sehen oder die Registerkarte zu erstellen",QMessageBox.Ok) 
            else:
            
                QMessageBox.information(self, "Warning" , "There is no such site: "'"'+ str(site_set_str) +'"'" in this tab, Please disable the 'site choice' from the plugin configuration tab to see all records or create the tab",QMessageBox.Ok) 
    def charge_periodo_list(self):
        pass

    def charge_fase_iniz_list(self):
        pass

    def charge_fase_fin_list(self):
        pass

        # buttons functions

    def generate_list_pdf(self):
        data_list = []
        for i in range(len(self.DATA_LIST)):
            data_list.append([
                str(self.DATA_LIST[i].sito.replace('_',' ')),  # 1 - Sito
                int(self.DATA_LIST[i].nr_individuo),  # 2 - num individuo
                int(self.DATA_LIST[i].sinf_min),  # 11 - Range sinfisi min
                int(self.DATA_LIST[i].sinf_max),  # 12 - Range sinfisi max
                int(self.DATA_LIST[i].sinf_min_2),  # 11 - Range sinfisi min
                int(self.DATA_LIST[i].sinf_max_2),  # 12 - Range sinfisi max
                int(self.DATA_LIST[i].SSPIA),  # 13 - SSPIA età
                int(self.DATA_LIST[i].SSPIB),  # 14 - SSPIB età
                int(self.DATA_LIST[i].SSPIC),  # 15 - SSPIC età
                int(self.DATA_LIST[i].SSPID),  # 16 - SSPID età
                int(self.DATA_LIST[i].sup_aur_min),  # 18 - Range superficie auricolare min
                int(self.DATA_LIST[i].sup_aur_max),  # 19 - Range superficie auricolare max
                int(self.DATA_LIST[i].sup_aur_min_2),  # 18 - Range superficie auricolare min
                int(self.DATA_LIST[i].sup_aur_max_2),  # 19 - Range superficie auricolare max
                int(self.DATA_LIST[i].ms_sup_min),  # 28 - Range mascellare superiore min
                int(self.DATA_LIST[i].ms_sup_max),  # 29 - Range mascellare superiore max
                int(self.DATA_LIST[i].ms_inf_min),  # 39 - Range mascellare inferiore min
                int(self.DATA_LIST[i].ms_inf_max),  # 40 - Range mascellare inferiore max
                int(self.DATA_LIST[i].usura_min),  # 41 - Range usura dentaria min
                int(self.DATA_LIST[i].usura_max),  # 42 - Range usura dentaria max
                int(self.DATA_LIST[i].Id_endo),  # 43 - 1d suture endocraniche
                int(self.DATA_LIST[i].Is_endo),  # 44 - 1s suture endocraniche
                int(self.DATA_LIST[i].IId_endo),  # 45 - 2d suture endocraniche
                int(self.DATA_LIST[i].IIs_endo),  # 46 - 2s suture endocraniche
                int(self.DATA_LIST[i].IIIs_endo),  # 47 - 3d suture endocraniche
                int(self.DATA_LIST[i].IIIs_endo),  # 48 - 3s suture endocraniche
                int(self.DATA_LIST[i].IV_endo),  # 49 - 4 suture endocraniche
                int(self.DATA_LIST[i].V_endo),  # 50 - 5 suture endocraniche
                int(self.DATA_LIST[i].VI_endo),  # 51 - 6 suture endocraniche
                int(self.DATA_LIST[i].VII_endo),  # 52 - 7 suture endocraniche
                int(self.DATA_LIST[i].VIIId_endo),  # 53 - 8d suture endocraniche
                int(self.DATA_LIST[i].VIIIs_endo),  # 54 - 8s suture endocraniche
                int(self.DATA_LIST[i].IXd_endo),  # 55 - 9d suture endocraniche
                int(self.DATA_LIST[i].IXs_endo),  # 56 - 9s suture endocraniche
                int(self.DATA_LIST[i].Xd_endo),  # 57 - 10d suture endocraniche
                int(self.DATA_LIST[i].Xs_endo),  # 58 - 10s suture endocraniche
                int(self.DATA_LIST[i].endo_min),  # 59 - Range suture endocraniche min
                int(self.DATA_LIST[i].endo_max),  # 60 - Range suture endocraniche max
                int(self.DATA_LIST[i].volta_1),  # 61 - Suture volta 1
                int(self.DATA_LIST[i].volta_2),  # 62 - Suture volta 2
                int(self.DATA_LIST[i].volta_3),  # 63 - Suture volta 3
                int(self.DATA_LIST[i].volta_4),  # 64 - Suture volta 4
                int(self.DATA_LIST[i].volta_5),  # 65 - Suture volta 5
                int(self.DATA_LIST[i].volta_6),  # 66 - Suture volta 6
                int(self.DATA_LIST[i].volta_7),  # 67 - Suture volta 7
                int(self.DATA_LIST[i].lat_6),  # 68 - Suture antero laterali 6
                int(self.DATA_LIST[i].lat_7),  # 69 - Suture antero laterali 7
                int(self.DATA_LIST[i].lat_8),  # 70 - Suture antero laterali 8
                int(self.DATA_LIST[i].lat_9),  # 71 - Suture antero laterali 9
                int(self.DATA_LIST[i].lat_10),  # 72 - Suture antero laterali 10
                int(self.DATA_LIST[i].volta_min),  # 73 - Range suture volta min
                int(self.DATA_LIST[i].volta_max),  # 74 - Range suture volta max
                int(self.DATA_LIST[i].ant_lat_min),  # 75 - Range suture antero laterali min
                int(self.DATA_LIST[i].ant_lat_max),  # 76 - Range suture antero laterali max
                int(self.DATA_LIST[i].ecto_min),  # 77 - Range suture ectocraniche min
                int(self.DATA_LIST[i].ecto_max)  # 78 - Range suture ectocraniche max
            ])
        return data_list

    def on_toolButtonPan_toggled(self):
        self.toolPan = QgsMapToolPan(self.mapPreview)
        self.mapPreview.setMapTool(self.toolPan)

        # buttons functions

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
            self.customize_GUI()

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

    def on_toolButtonPreview_toggled(self):
        if self.L=='it':
            if self.toolButtonPreview.isChecked():
                QMessageBox.warning(self, "Messaggio",
                                    "Modalita' Preview US attivata. Le piante delle US saranno visualizzate nella sezione Piante",
                                    QMessageBox.Ok)
                self.loadMapPreview()
            else:
                self.loadMapPreview(1)
        elif self.L=='de':
            if self.toolButtonPreview.isChecked():
                QMessageBox.warning(self, "Message",
                                    "Modalität' Preview der aktivierten SE. Die Plana der SE werden in der Auswahl der Plana visualisiert",
                                    QMessageBox.Ok)
                self.loadMapPreview()
            else:
                self.loadMapPreview(1)
                
        else:
            if self.toolButtonPreview.isChecked():
                QMessageBox.warning(self, "Message",
                                    "Preview SU mode enabled. US plants will be displayed in the Plants section",
                                    QMessageBox.Ok)
                self.loadMapPreview()
            else:
                self.loadMapPreview(1)

    """
    def on_pushButton_addRaster_pressed(self):
        if self.toolButtonGis.isChecked() == True:
            self.pyQGIS.addRasterLayer()
    """

    def on_pushButton_new_rec_pressed(self):
        if bool(self.DATA_LIST):
            if self.data_error_check() == 1:
                pass
            else:
                if self.BROWSE_STATUS == "b":
                    if bool(self.DATA_LIST):
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

                            # set the GUI for a new record
        if self.BROWSE_STATUS != "n":
            self.BROWSE_STATUS = "n"
            self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
            self.empty_fields()
            self.label_sort.setText(self.SORTED_ITEMS["n"])

            self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])

            self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
            self.set_rec_counter('', '')
            self.label_sort.setText(self.SORTED_ITEMS["n"])
            self.empty_fields()

            self.enable_button(0)

    def on_pushButton_save_pressed(self):
        # save record
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
                    self.label_sort.setText(self.SORTED_ITEMS["n"])
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

                    self.fill_fields(self.REC_CORR)
                    self.enable_button(1)
                else:
                    pass

    def data_error_check(self):
        test = 0

        EC = Error_check()

        if self.L=='it':
            if EC.data_is_empty(str(self.comboBox_sito.currentText())) == 0:
                QMessageBox.warning(self, "ATTENZIONE", "Campo Sito. \n Il campo non deve essere vuoto", QMessageBox.Ok)
                test = 1

            if EC.data_is_empty(str(self.lineEdit_nr_individuo.text())) == 0:
                QMessageBox.warning(self, "ATTENZIONE", "Campo Individuo. \n Il campo non deve essere vuoto",
                                    QMessageBox.Ok)
                test = 1

            nr_individuo = self.lineEdit_nr_individuo.text()
            sinf_min = self.lineEdit_sinf_min.text()
            sinf_max = self.lineEdit_sinf_max.text()
            sinf_min2 = self.lineEdit_sinf_min_2.text()
            sinf_max2 = self.lineEdit_sinf_max_2.text()
            sspia = self.comboBox_SSPIA.currentText()
            sspib = self.comboBox_SSPIB.currentText()
            sspic = self.comboBox_SSPIC.currentText()
            sspid = self.comboBox_SSPID.currentText()
            sup_aur_min = self.lineEdit_sup_aur_min.text()
            sup_aur_max = self.lineEdit_sup_aur_max.text()
            sup_aur_min2 = self.lineEdit_sup_aur_min_2.text()
            sup_aur_max2 = self.lineEdit_sup_aur_max_2.text()
            ms_sup_min = self.lineEdit_ms_sup_min.text()
            ms_sup_max = self.lineEdit_ms_sup_max.text()
            ms_inf_min = self.lineEdit_ms_inf_min.text()
            ms_inf_max = self.lineEdit_ms_inf_max.text()
            usura_min = self.lineEdit_usura_min.text()
            usura_max = self.lineEdit_usura_max.text()
            id_endo = self.comboBox_Id_endo.currentText()
            is_endo = self.comboBox_Is_endo.currentText()
            iid_endo = self.comboBox_IId_endo.currentText()
            iis_endo = self.comboBox_IIs_endo.currentText()
            iiid_endo = self.comboBox_IIId_endo.currentText()
            iiis_endo = self.comboBox_IIIs_endo.currentText()
            iv_endo = self.comboBox_IV_endo.currentText()
            v_endo = self.comboBox_V_endo.currentText()
            vi_endo = self.comboBox_VI_endo.currentText()
            vii_endo = self.comboBox_VII_endo.currentText()
            viiid_endo = self.comboBox_VIIId_endo.currentText()
            viiis_endo = self.comboBox_VIIIs_endo.currentText()
            ixd_endo = self.comboBox_IXd_endo.currentText()
            ixs_endo = self.comboBox_IXs_endo.currentText()
            xd_endo = self.comboBox_Xd_endo.currentText()
            xs_endo = self.comboBox_Xs_endo.currentText()
            endo_min = self.lineEdit_endo_min.text()
            endo_max = self.lineEdit_endo_max.text()
            v1 = self.comboBox_volta_1.currentText()
            v2 = self.comboBox_volta_2.currentText()
            v3 = self.comboBox_volta_3.currentText()
            v4 = self.comboBox_volta_4.currentText()
            v5 = self.comboBox_volta_5.currentText()
            v6 = self.comboBox_volta_6.currentText()
            v7 = self.comboBox_volta_7.currentText()
            l6 = self.comboBox_lat_6.currentText()
            l7 = self.comboBox_lat_7.currentText()
            l8 = self.comboBox_lat_8.currentText()
            l9 = self.comboBox_lat_9.currentText()
            l10 = self.comboBox_lat_10.currentText()
            v_min = self.lineEdit_volta_min.text()
            v_max = self.lineEdit_volta_max.text()
            a_l_min = self.lineEdit_ant_lat_min.text()
            a_l_max = self.lineEdit_ant_lat_max.text()
            ecto_min = self.lineEdit_ecto_min.text()
            ecto_max = self.lineEdit_ecto_max.text()

            if nr_individuo != "":
                if EC.data_is_int(nr_individuo) == 0:
                    QMessageBox.warning(self, "ATTENZIONE", "Campo Individuo. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

            if sinf_min != "":
                if EC.data_is_int(sinf_min) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Tutti i parametri da inserire. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

            if sinf_max != "":
                if EC.data_is_int(sinf_max) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Tutti i parametri da inserire. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

            if sinf_min2 != "":
                if EC.data_is_int(sinf_min2) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Tutti i parametri da inserire. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

            if sinf_max2 != "":
                if EC.data_is_int(sinf_max2) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Tutti i parametri da inserire. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

            if sspia != "":
                if EC.data_is_int(sspia) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Tutti i parametri da inserire. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

            if sspib != "":
                if EC.data_is_int(sspib) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Tutti i parametri da inserire. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

            if sspic != "":
                if EC.data_is_int(sspic) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Tutti i parametri da inserire. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

            if sspid != "":
                if EC.data_is_int(sspid) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Tutti i parametri da inserire. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

            if sup_aur_min != "":
                if EC.data_is_int(sup_aur_min) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Tutti i parametri da inserire. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

            if sup_aur_max != "":
                if EC.data_is_int(sup_aur_max) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Tutti i parametri da inserire. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

            if sup_aur_min2 != "":
                if EC.data_is_int(sup_aur_min2) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Tutti i parametri da inserire. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

            if sup_aur_max2 != "":
                if EC.data_is_int(sup_aur_max2) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Tutti i parametri da inserire. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

            if ms_sup_min != "":
                if EC.data_is_int(ms_sup_min) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Tutti i parametri da inserire. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

            if ms_sup_max != "":
                if EC.data_is_int(ms_sup_max) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Tutti i parametri da inserire. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

            if ms_inf_min != "":
                if EC.data_is_int(ms_inf_min) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Tutti i parametri da inserire. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

            if ms_inf_max != "":
                if EC.data_is_int(ms_inf_max) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Tutti i parametri da inserire. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

            if usura_min != "":
                if EC.data_is_int(usura_min) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Tutti i parametri da inserire. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

            if usura_max != "":
                if EC.data_is_int(usura_max) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Tutti i parametri da inserire. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

            if id_endo != "":
                if EC.data_is_int(id_endo) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Tutti i parametri da inserire. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

            if is_endo != "":
                if EC.data_is_int(is_endo) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Tutti i parametri da inserire. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

            if iid_endo != "":
                if EC.data_is_int(iid_endo) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Tutti i parametri da inserire. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

            if iis_endo != "":
                if EC.data_is_int(iis_endo) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Tutti i parametri da inserire. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

            if iiid_endo != "":
                if EC.data_is_int(iiid_endo) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Tutti i parametri da inserire. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

            if iiis_endo != "":
                if EC.data_is_int(iiis_endo) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Tutti i parametri da inserire. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

            if iv_endo != "":
                if EC.data_is_int(iv_endo) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Tutti i parametri da inserire. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

            if v_endo != "":
                if EC.data_is_int(v_endo) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Tutti i parametri da inserire. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

            if vi_endo != "":
                if EC.data_is_int(vi_endo) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Tutti i parametri da inserire. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

            if vii_endo != "":
                if EC.data_is_int(vii_endo) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Tutti i parametri da inserire. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

            if viiid_endo != "":
                if EC.data_is_int(viiid_endo) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Tutti i parametri da inserire. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

            if viiis_endo != "":
                if EC.data_is_int(viiis_endo) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Tutti i parametri da inserire. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

            if ixd_endo != "":
                if EC.data_is_int(ixd_endo) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Tutti i parametri da inserire. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

            if ixs_endo != "":
                if EC.data_is_int(ixs_endo) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Tutti i parametri da inserire. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

            if xd_endo != "":
                if EC.data_is_int(xd_endo) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Tutti i parametri da inserire. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

            if xs_endo != "":
                if EC.data_is_int(xs_endo) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Tutti i parametri da inserire. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

            if endo_min != "":
                if EC.data_is_int(endo_min) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Tutti i parametri da inserire. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

            if endo_max != "":
                if EC.data_is_int(endo_max) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Tutti i parametri da inserire. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

            if v1 != "":
                if EC.data_is_int(v1) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Tutti i parametri da inserire. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

            if v2 != "":
                if EC.data_is_int(v2) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Tutti i parametri da inserire. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

            if v3 != "":
                if EC.data_is_int(v3) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Tutti i parametri da inserire. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

            if v4 != "":
                if EC.data_is_int(v4) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Tutti i parametri da inserire. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

            if v5 != "":
                if EC.data_is_int(v5) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Tutti i parametri da inserire. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

            if v6 != "":
                if EC.data_is_int(v6) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Tutti i parametri da inserire. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

            if v7 != "":
                if EC.data_is_int(v7) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Tutti i parametri da inserire. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

            if l6 != "":
                if EC.data_is_int(l6) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Tutti i parametri da inserire. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

            if l7 != "":
                if EC.data_is_int(l7) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Tutti i parametri da inserire. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

            if l8 != "":
                if EC.data_is_int(l8) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Tutti i parametri da inserire. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

            if l9 != "":
                if EC.data_is_int(l9) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Tutti i parametri da inserire. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

            if l10 != "":
                if EC.data_is_int(l10) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Tutti i parametri da inserire. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

            if v_min != "":
                if EC.data_is_int(v_min) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Tutti i parametri da inserire. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

            if v_max != "":
                if EC.data_is_int(v_max) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Tutti i parametri da inserire. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

            if a_l_min != "":
                if EC.data_is_int(a_l_min) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Tutti i parametri da inserire. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

            if a_l_max != "":
                if EC.data_is_int(a_l_max) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Tutti i parametri da inserire. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

            if ecto_min != "":
                if EC.data_is_int(ecto_min) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Tutti i parametri da inserire. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1

            if ecto_max != "":
                if EC.data_is_int(ecto_max) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Tutti i parametri da inserire. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1
        
        
        elif self.L=='de':
            if EC.data_is_empty(str(self.comboBox_sito.currentText())) == 0:
                QMessageBox.warning(self, "ACHTUNG", " Feld Ausgrabungstätte. \n Das Feld darf nicht leer sein", QMessageBox.Ok)
                test = 1

            if EC.data_is_empty(str(self.lineEdit_nr_individuo.text())) == 0:
                QMessageBox.warning(self, "ACHTUNG", " Feld Individuell. \n Das Feld darf nicht leer sein", QMessageBox.Ok)
                test = 1

            nr_individuo = self.lineEdit_nr_individuo.text()
            sinf_min = self.lineEdit_sinf_min.text()
            sinf_max = self.lineEdit_sinf_max.text()
            sinf_min2 = self.lineEdit_sinf_min_2.text()
            sinf_max2 = self.lineEdit_sinf_max_2.text()
            sspia = self.comboBox_SSPIA.currentText()
            sspib = self.comboBox_SSPIB.currentText()
            sspic = self.comboBox_SSPIC.currentText()
            sspid = self.comboBox_SSPID.currentText()
            sup_aur_min = self.lineEdit_sup_aur_min.text()
            sup_aur_max = self.lineEdit_sup_aur_max.text()
            sup_aur_min2 = self.lineEdit_sup_aur_min_2.text()
            sup_aur_max2 = self.lineEdit_sup_aur_max_2.text()
            ms_sup_min = self.lineEdit_ms_sup_min.text()
            ms_sup_max = self.lineEdit_ms_sup_max.text()
            ms_inf_min = self.lineEdit_ms_inf_min.text()
            ms_inf_max = self.lineEdit_ms_inf_max.text()
            usura_min = self.lineEdit_usura_min.text()
            usura_max = self.lineEdit_usura_max.text()
            id_endo = self.comboBox_Id_endo.currentText()
            is_endo = self.comboBox_Is_endo.currentText()
            iid_endo = self.comboBox_IId_endo.currentText()
            iis_endo = self.comboBox_IIs_endo.currentText()
            iiid_endo = self.comboBox_IIId_endo.currentText()
            iiis_endo = self.comboBox_IIIs_endo.currentText()
            iv_endo = self.comboBox_IV_endo.currentText()
            v_endo = self.comboBox_V_endo.currentText()
            vi_endo = self.comboBox_VI_endo.currentText()
            vii_endo = self.comboBox_VII_endo.currentText()
            viiid_endo = self.comboBox_VIIId_endo.currentText()
            viiis_endo = self.comboBox_VIIIs_endo.currentText()
            ixd_endo = self.comboBox_IXd_endo.currentText()
            ixs_endo = self.comboBox_IXs_endo.currentText()
            xd_endo = self.comboBox_Xd_endo.currentText()
            xs_endo = self.comboBox_Xs_endo.currentText()
            endo_min = self.lineEdit_endo_min.text()
            endo_max = self.lineEdit_endo_max.text()
            v1 = self.comboBox_volta_1.currentText()
            v2 = self.comboBox_volta_2.currentText()
            v3 = self.comboBox_volta_3.currentText()
            v4 = self.comboBox_volta_4.currentText()
            v5 = self.comboBox_volta_5.currentText()
            v6 = self.comboBox_volta_6.currentText()
            v7 = self.comboBox_volta_7.currentText()
            l6 = self.comboBox_lat_6.currentText()
            l7 = self.comboBox_lat_7.currentText()
            l8 = self.comboBox_lat_8.currentText()
            l9 = self.comboBox_lat_9.currentText()
            l10 = self.comboBox_lat_10.currentText()
            v_min = self.lineEdit_volta_min.text()
            v_max = self.lineEdit_volta_max.text()
            a_l_min = self.lineEdit_ant_lat_min.text()
            a_l_max = self.lineEdit_ant_lat_max.text()
            ecto_min = self.lineEdit_ecto_min.text()
            ecto_max = self.lineEdit_ecto_max.text()

            if nr_individuo != "":
                if EC.data_is_int(nr_individuo) == 0:
                    QMessageBox.warning(self, "Achtung", "Feld individuell. \n Der Wert muss numerisch sein",
                                        QMessageBox.Ok)
                    test = 1

            if sinf_min != "":
                if EC.data_is_int(sinf_min) == 0:
                    QMessageBox.warning(self, "Achtung",
                                        "Alle Parameter sind einzugeben. \n Der Wert muss numerisch sein.",
                                        QMessageBox.Ok)
                    test = 1

            if sinf_max != "":
                if EC.data_is_int(sinf_max) == 0:
                    QMessageBox.warning(self, "Achtung",
                                        "Alle Parameter sind einzugeben. \n Der Wert muss numerisch sein.",
                                        QMessageBox.Ok)
                    test = 1

            if sinf_min2 != "":
                if EC.data_is_int(sinf_min2) == 0:
                    QMessageBox.warning(self, "Achtung",
                                        "Alle Parameter sind einzugeben. \n Der Wert muss numerisch sein.",
                                        QMessageBox.Ok)
                    test = 1

            if sinf_max2 != "":
                if EC.data_is_int(sinf_max2) == 0:
                    QMessageBox.warning(self, "Achtung",
                                        "Alle Parameter sind einzugeben. \n Der Wert muss numerisch sein.",
                                        QMessageBox.Ok)
                    test = 1

            if sspia != "":
                if EC.data_is_int(sspia) == 0:
                    QMessageBox.warning(self, "Achtung",
                                        "Alle Parameter sind einzugeben. \n Der Wert muss numerisch sein.",
                                        QMessageBox.Ok)
                    test = 1

            if sspib != "":
                if EC.data_is_int(sspib) == 0:
                    QMessageBox.warning(self, "Achtung",
                                        "Alle Parameter sind einzugeben. \n Der Wert muss numerisch sein.",
                                        QMessageBox.Ok)
                    test = 1

            if sspic != "":
                if EC.data_is_int(sspic) == 0:
                    QMessageBox.warning(self, "Achtung",
                                        "Alle Parameter sind einzugeben. \n Der Wert muss numerisch sein.",
                                        QMessageBox.Ok)
                    test = 1

            if sspid != "":
                if EC.data_is_int(sspid) == 0:
                    QMessageBox.warning(self, "Achtung",
                                        "Alle Parameter sind einzugeben. \n Der Wert muss numerisch sein.",
                                        QMessageBox.Ok)
                    test = 1

            if sup_aur_min != "":
                if EC.data_is_int(sup_aur_min) == 0:
                    QMessageBox.warning(self, "Achtung",
                                        "Alle Parameter sind einzugeben. \n Der Wert muss numerisch sein.",
                                        QMessageBox.Ok)
                    test = 1

            if sup_aur_max != "":
                if EC.data_is_int(sup_aur_max) == 0:
                    QMessageBox.warning(self, "Achtung",
                                        "Alle Parameter sind einzugeben. \n Der Wert muss numerisch sein.",
                                        QMessageBox.Ok)
                    test = 1

            if sup_aur_min2 != "":
                if EC.data_is_int(sup_aur_min2) == 0:
                    QMessageBox.warning(self, "Achtung",
                                        "Alle Parameter sind einzugeben. \n Der Wert muss numerisch sein.",
                                        QMessageBox.Ok)
                    test = 1

            if sup_aur_max2 != "":
                if EC.data_is_int(sup_aur_max2) == 0:
                    QMessageBox.warning(self, "Achtung",
                                        "Alle Parameter sind einzugeben. \n Der Wert muss numerisch sein.",
                                        QMessageBox.Ok)
                    test = 1

            if ms_sup_min != "":
                if EC.data_is_int(ms_sup_min) == 0:
                    QMessageBox.warning(self, "Achtung",
                                        "Alle Parameter sind einzugeben. \n Der Wert muss numerisch sein.",
                                        QMessageBox.Ok)
                    test = 1

            if ms_sup_max != "":
                if EC.data_is_int(ms_sup_max) == 0:
                    QMessageBox.warning(self, "Achtung",
                                        "Alle Parameter sind einzugeben. \n Der Wert muss numerisch sein.",
                                        QMessageBox.Ok)
                    test = 1

            if ms_inf_min != "":
                if EC.data_is_int(ms_inf_min) == 0:
                    QMessageBox.warning(self, "Achtung",
                                        "Alle Parameter sind einzugeben. \n Der Wert muss numerisch sein.",
                                        QMessageBox.Ok)
                    test = 1

            if ms_inf_max != "":
                if EC.data_is_int(ms_inf_max) == 0:
                    QMessageBox.warning(self, "Achtung",
                                        "Alle Parameter sind einzugeben. \n Der Wert muss numerisch sein.",
                                        QMessageBox.Ok)
                    test = 1

            if usura_min != "":
                if EC.data_is_int(usura_min) == 0:
                    QMessageBox.warning(self, "Achtung",
                                        "Alle Parameter sind einzugeben. \n Der Wert muss numerisch sein.",
                                        QMessageBox.Ok)
                    test = 1

            if usura_max != "":
                if EC.data_is_int(usura_max) == 0:
                    QMessageBox.warning(self, "Achtung",
                                        "Alle Parameter sind einzugeben. \n Der Wert muss numerisch sein.",
                                        QMessageBox.Ok)
                    test = 1

            if id_endo != "":
                if EC.data_is_int(id_endo) == 0:
                    QMessageBox.warning(self, "Achtung",
                                        "Alle Parameter sind einzugeben. \n Der Wert muss numerisch sein.",
                                        QMessageBox.Ok)
                    test = 1

            if is_endo != "":
                if EC.data_is_int(is_endo) == 0:
                    QMessageBox.warning(self, "Achtung",
                                        "Alle Parameter sind einzugeben. \n Der Wert muss numerisch sein.",
                                        QMessageBox.Ok)
                    test = 1

            if iid_endo != "":
                if EC.data_is_int(iid_endo) == 0:
                    QMessageBox.warning(self, "Achtung",
                                        "Alle Parameter sind einzugeben. \n Der Wert muss numerisch sein.",
                                        QMessageBox.Ok)
                    test = 1

            if iis_endo != "":
                if EC.data_is_int(iis_endo) == 0:
                    QMessageBox.warning(self, "Achtung",
                                        "Alle Parameter sind einzugeben. \n Der Wert muss numerisch sein.",
                                        QMessageBox.Ok)
                    test = 1

            if iiid_endo != "":
                if EC.data_is_int(iiid_endo) == 0:
                    QMessageBox.warning(self, "Achtung",
                                        "Alle Parameter sind einzugeben. \n Der Wert muss numerisch sein.",
                                        QMessageBox.Ok)
                    test = 1

            if iiis_endo != "":
                if EC.data_is_int(iiis_endo) == 0:
                    QMessageBox.warning(self, "Achtung",
                                        "Alle Parameter sind einzugeben. \n Der Wert muss numerisch sein.",
                                        QMessageBox.Ok)
                    test = 1

            if iv_endo != "":
                if EC.data_is_int(iv_endo) == 0:
                    QMessageBox.warning(self, "Achtung",
                                        "Alle Parameter sind einzugeben. \n Der Wert muss numerisch sein.",
                                        QMessageBox.Ok)
                    test = 1

            if v_endo != "":
                if EC.data_is_int(v_endo) == 0:
                    QMessageBox.warning(self, "Achtung",
                                        "Alle Parameter sind einzugeben. \n Der Wert muss numerisch sein.",
                                        QMessageBox.Ok)
                    test = 1

            if vi_endo != "":
                if EC.data_is_int(vi_endo) == 0:
                    QMessageBox.warning(self, "Achtung",
                                        "Alle Parameter sind einzugeben. \n Der Wert muss numerisch sein.",
                                        QMessageBox.Ok)
                    test = 1

            if vii_endo != "":
                if EC.data_is_int(vii_endo) == 0:
                    QMessageBox.warning(self, "Achtung",
                                        "Alle Parameter sind einzugeben. \n Der Wert muss numerisch sein.",
                                        QMessageBox.Ok)
                    test = 1

            if viiid_endo != "":
                if EC.data_is_int(viiid_endo) == 0:
                    QMessageBox.warning(self, "Achtung",
                                        "Alle Parameter sind einzugeben. \n Der Wert muss numerisch sein.",
                                        QMessageBox.Ok)
                    test = 1

            if viiis_endo != "":
                if EC.data_is_int(viiis_endo) == 0:
                    QMessageBox.warning(self, "Achtung",
                                        "Alle Parameter sind einzugeben. \n Der Wert muss numerisch sein.",
                                        QMessageBox.Ok)
                    test = 1

            if ixd_endo != "":
                if EC.data_is_int(ixd_endo) == 0:
                    QMessageBox.warning(self, "Achtung",
                                        "Alle Parameter sind einzugeben. \n Der Wert muss numerisch sein.",
                                        QMessageBox.Ok)
                    test = 1

            if ixs_endo != "":
                if EC.data_is_int(ixs_endo) == 0:
                    QMessageBox.warning(self, "Achtung",
                                        "Alle Parameter sind einzugeben. \n Der Wert muss numerisch sein.",
                                        QMessageBox.Ok)
                    test = 1

            if xd_endo != "":
                if EC.data_is_int(xd_endo) == 0:
                    QMessageBox.warning(self, "Achtung",
                                        "Alle Parameter sind einzugeben. \n Der Wert muss numerisch sein.",
                                        QMessageBox.Ok)
                    test = 1

            if xs_endo != "":
                if EC.data_is_int(xs_endo) == 0:
                    QMessageBox.warning(self, "Achtung",
                                        "Alle Parameter sind einzugeben. \n Der Wert muss numerisch sein.",
                                        QMessageBox.Ok)
                    test = 1

            if endo_min != "":
                if EC.data_is_int(endo_min) == 0:
                    QMessageBox.warning(self, "Achtung",
                                        "Alle Parameter sind einzugeben. \n Der Wert muss numerisch sein.",
                                        QMessageBox.Ok)
                    test = 1

            if endo_max != "":
                if EC.data_is_int(endo_max) == 0:
                    QMessageBox.warning(self, "Achtung",
                                        "Alle Parameter sind einzugeben. \n Der Wert muss numerisch sein.",
                                        QMessageBox.Ok)
                    test = 1

            if v1 != "":
                if EC.data_is_int(v1) == 0:
                    QMessageBox.warning(self, "Achtung",
                                        "Alle Parameter sind einzugeben. \n Der Wert muss numerisch sein.",
                                        QMessageBox.Ok)
                    test = 1

            if v2 != "":
                if EC.data_is_int(v2) == 0:
                    QMessageBox.warning(self, "Achtung",
                                        "Alle Parameter sind einzugeben. \n Der Wert muss numerisch sein.",
                                        QMessageBox.Ok)
                    test = 1

            if v3 != "":
                if EC.data_is_int(v3) == 0:
                    QMessageBox.warning(self, "Achtung",
                                        "Alle Parameter sind einzugeben. \n Der Wert muss numerisch sein.",
                                        QMessageBox.Ok)
                    test = 1

            if v4 != "":
                if EC.data_is_int(v4) == 0:
                    QMessageBox.warning(self, "Achtung",
                                        "Alle Parameter sind einzugeben. \n Der Wert muss numerisch sein.",
                                        QMessageBox.Ok)
                    test = 1

            if v5 != "":
                if EC.data_is_int(v5) == 0:
                    QMessageBox.warning(self, "Achtung",
                                        "Alle Parameter sind einzugeben. \n Der Wert muss numerisch sein.",
                                        QMessageBox.Ok)
                    test = 1

            if v6 != "":
                if EC.data_is_int(v6) == 0:
                    QMessageBox.warning(self, "Achtung",
                                        "Alle Parameter sind einzugeben. \n Der Wert muss numerisch sein.",
                                        QMessageBox.Ok)
                    test = 1

            if v7 != "":
                if EC.data_is_int(v7) == 0:
                    QMessageBox.warning(self, "Achtung",
                                        "Alle Parameter sind einzugeben. \n Der Wert muss numerisch sein.",
                                        QMessageBox.Ok)
                    test = 1

            if l6 != "":
                if EC.data_is_int(l6) == 0:
                    QMessageBox.warning(self, "Achtung",
                                        "Alle Parameter sind einzugeben. \n Der Wert muss numerisch sein.",
                                        QMessageBox.Ok)
                    test = 1

            if l7 != "":
                if EC.data_is_int(l7) == 0:
                    QMessageBox.warning(self, "Achtung",
                                        "Alle Parameter sind einzugeben. \n Der Wert muss numerisch sein.",
                                        QMessageBox.Ok)
                    test = 1

            if l8 != "":
                if EC.data_is_int(l8) == 0:
                    QMessageBox.warning(self, "Achtung",
                                        "Alle Parameter sind einzugeben. \n Der Wert muss numerisch sein.",
                                        QMessageBox.Ok)
                    test = 1

            if l9 != "":
                if EC.data_is_int(l9) == 0:
                    QMessageBox.warning(self, "Achtung",
                                        "Alle Parameter sind einzugeben. \n Der Wert muss numerisch sein.",
                                        QMessageBox.Ok)
                    test = 1

            if l10 != "":
                if EC.data_is_int(l10) == 0:
                    QMessageBox.warning(self, "Achtung",
                                        "Alle Parameter sind einzugeben. \n Der Wert muss numerisch sein.",
                                        QMessageBox.Ok)
                    test = 1

            if v_min != "":
                if EC.data_is_int(v_min) == 0:
                    QMessageBox.warning(self, "Achtung",
                                        "Alle Parameter sind einzugeben. \n Der Wert muss numerisch sein.",
                                        QMessageBox.Ok)
                    test = 1

            if v_max != "":
                if EC.data_is_int(v_max) == 0:
                    QMessageBox.warning(self, "Achtung",
                                        "Alle Parameter sind einzugeben. \n Der Wert muss numerisch sein.",
                                        QMessageBox.Ok)
                    test = 1

            if a_l_min != "":
                if EC.data_is_int(a_l_min) == 0:
                    QMessageBox.warning(self, "Achtung",
                                        "Alle Parameter sind einzugeben. \n Der Wert muss numerisch sein.",
                                        QMessageBox.Ok)
                    test = 1

            if a_l_max != "":
                if EC.data_is_int(a_l_max) == 0:
                    QMessageBox.warning(self, "Achtung",
                                        "Alle Parameter sind einzugeben. \n Der Wert muss numerisch sein.",
                                        QMessageBox.Ok)
                    test = 1

            if ecto_min != "":
                if EC.data_is_int(ecto_min) == 0:
                    QMessageBox.warning(self, "Achtung",
                                        "Alle Parameter sind einzugeben. \n Der Wert muss numerisch sein.",
                                        QMessageBox.Ok)
                    test = 1

            if ecto_max != "":
                if EC.data_is_int(ecto_max) == 0:
                    QMessageBox.warning(self, "Achtung",
                                        "Alle Parameter sind einzugeben. \n Der Wert muss numerisch sein.",
                                        QMessageBox.Ok)
                    test = 1
        
        
        else:
            if EC.data_is_empty(str(self.comboBox_sito.currentText())) == 0:
                QMessageBox.warning(self, "Warning", "Site field. \n The field must not be empty", QMessageBox.Ok)
                test = 1

            if EC.data_is_empty(str(self.lineEdit_nr_individuo.text())) == 0:
                QMessageBox.warning(self, "Warning", "Individual field. \n The field must not be empty",
                                    QMessageBox.Ok)
                test = 1

            nr_individuo = self.lineEdit_nr_individuo.text()
            sinf_min = self.lineEdit_sinf_min.text()
            sinf_max = self.lineEdit_sinf_max.text()
            sinf_min2 = self.lineEdit_sinf_min_2.text()
            sinf_max2 = self.lineEdit_sinf_max_2.text()
            sspia = self.comboBox_SSPIA.currentText()
            sspib = self.comboBox_SSPIB.currentText()
            sspic = self.comboBox_SSPIC.currentText()
            sspid = self.comboBox_SSPID.currentText()
            sup_aur_min = self.lineEdit_sup_aur_min.text()
            sup_aur_max = self.lineEdit_sup_aur_max.text()
            sup_aur_min2 = self.lineEdit_sup_aur_min_2.text()
            sup_aur_max2 = self.lineEdit_sup_aur_max_2.text()
            ms_sup_min = self.lineEdit_ms_sup_min.text()
            ms_sup_max = self.lineEdit_ms_sup_max.text()
            ms_inf_min = self.lineEdit_ms_inf_min.text()
            ms_inf_max = self.lineEdit_ms_inf_max.text()
            usura_min = self.lineEdit_usura_min.text()
            usura_max = self.lineEdit_usura_max.text()
            id_endo = self.comboBox_Id_endo.currentText()
            is_endo = self.comboBox_Is_endo.currentText()
            iid_endo = self.comboBox_IId_endo.currentText()
            iis_endo = self.comboBox_IIs_endo.currentText()
            iiid_endo = self.comboBox_IIId_endo.currentText()
            iiis_endo = self.comboBox_IIIs_endo.currentText()
            iv_endo = self.comboBox_IV_endo.currentText()
            v_endo = self.comboBox_V_endo.currentText()
            vi_endo = self.comboBox_VI_endo.currentText()
            vii_endo = self.comboBox_VII_endo.currentText()
            viiid_endo = self.comboBox_VIIId_endo.currentText()
            viiis_endo = self.comboBox_VIIIs_endo.currentText()
            ixd_endo = self.comboBox_IXd_endo.currentText()
            ixs_endo = self.comboBox_IXs_endo.currentText()
            xd_endo = self.comboBox_Xd_endo.currentText()
            xs_endo = self.comboBox_Xs_endo.currentText()
            endo_min = self.lineEdit_endo_min.text()
            endo_max = self.lineEdit_endo_max.text()
            v1 = self.comboBox_volta_1.currentText()
            v2 = self.comboBox_volta_2.currentText()
            v3 = self.comboBox_volta_3.currentText()
            v4 = self.comboBox_volta_4.currentText()
            v5 = self.comboBox_volta_5.currentText()
            v6 = self.comboBox_volta_6.currentText()
            v7 = self.comboBox_volta_7.currentText()
            l6 = self.comboBox_lat_6.currentText()
            l7 = self.comboBox_lat_7.currentText()
            l8 = self.comboBox_lat_8.currentText()
            l9 = self.comboBox_lat_9.currentText()
            l10 = self.comboBox_lat_10.currentText()
            v_min = self.lineEdit_volta_min.text()
            v_max = self.lineEdit_volta_max.text()
            a_l_min = self.lineEdit_ant_lat_min.text()
            a_l_max = self.lineEdit_ant_lat_max.text()
            ecto_min = self.lineEdit_ecto_min.text()
            ecto_max = self.lineEdit_ecto_max.text()

            if nr_individuo != "":
                if EC.data_is_int(nr_individuo) == 0:
                    QMessageBox.warning(self, "Warning", "Indivisual field. \n The value must be numerical.",
                                        QMessageBox.Ok)
                    test = 1

            if sinf_min != "":
                if EC.data_is_int(sinf_min) == 0:
                    QMessageBox.warning(self, "Warning",
                                        "All parameters to be entered. \n The value must be numerical.",
                                        QMessageBox.Ok)
                    test = 1

            if sinf_max != "":
                if EC.data_is_int(sinf_max) == 0:
                    QMessageBox.warning(self, "Warning",
                                        "All parameters to be entered. \n The value must be numerical.",
                                        QMessageBox.Ok)
                    test = 1

            if sinf_min2 != "":
                if EC.data_is_int(sinf_min2) == 0:
                    QMessageBox.warning(self, "Warning",
                                        "All parameters to be entered. \n The value must be numerical.",
                                        QMessageBox.Ok)
                    test = 1

            if sinf_max2 != "":
                if EC.data_is_int(sinf_max2) == 0:
                    QMessageBox.warning(self, "Warning",
                                        "All parameters to be entered. \n The value must be numerical.",
                                        QMessageBox.Ok)
                    test = 1

            if sspia != "":
                if EC.data_is_int(sspia) == 0:
                    QMessageBox.warning(self, "Warning",
                                        "All parameters to be entered. \n The value must be numerical.",
                                        QMessageBox.Ok)
                    test = 1

            if sspib != "":
                if EC.data_is_int(sspib) == 0:
                    QMessageBox.warning(self, "Warning",
                                        "All parameters to be entered. \n The value must be numerical.",
                                        QMessageBox.Ok)
                    test = 1

            if sspic != "":
                if EC.data_is_int(sspic) == 0:
                    QMessageBox.warning(self, "Warning",
                                        "All parameters to be entered. \n The value must be numerical.",
                                        QMessageBox.Ok)
                    test = 1

            if sspid != "":
                if EC.data_is_int(sspid) == 0:
                    QMessageBox.warning(self, "Warning",
                                        "All parameters to be entered. \n The value must be numerical.",
                                        QMessageBox.Ok)
                    test = 1

            if sup_aur_min != "":
                if EC.data_is_int(sup_aur_min) == 0:
                    QMessageBox.warning(self, "Warning",
                                        "All parameters to be entered. \n The value must be numerical.",
                                        QMessageBox.Ok)
                    test = 1

            if sup_aur_max != "":
                if EC.data_is_int(sup_aur_max) == 0:
                    QMessageBox.warning(self, "Warning",
                                        "All parameters to be entered. \n The value must be numerical.",
                                        QMessageBox.Ok)
                    test = 1

            if sup_aur_min2 != "":
                if EC.data_is_int(sup_aur_min2) == 0:
                    QMessageBox.warning(self, "Warning",
                                        "All parameters to be entered. \n The value must be numerical.",
                                        QMessageBox.Ok)
                    test = 1

            if sup_aur_max2 != "":
                if EC.data_is_int(sup_aur_max2) == 0:
                    QMessageBox.warning(self, "Warning",
                                        "All parameters to be entered. \n The value must be numerical.",
                                        QMessageBox.Ok)
                    test = 1

            if ms_sup_min != "":
                if EC.data_is_int(ms_sup_min) == 0:
                    QMessageBox.warning(self, "Warning",
                                        "All parameters to be entered. \n The value must be numerical.",
                                        QMessageBox.Ok)
                    test = 1

            if ms_sup_max != "":
                if EC.data_is_int(ms_sup_max) == 0:
                    QMessageBox.warning(self, "Warning",
                                        "All parameters to be entered. \n The value must be numerical.",
                                        QMessageBox.Ok)
                    test = 1

            if ms_inf_min != "":
                if EC.data_is_int(ms_inf_min) == 0:
                    QMessageBox.warning(self, "Warning",
                                        "All parameters to be entered. \n The value must be numerical.",
                                        QMessageBox.Ok)
                    test = 1

            if ms_inf_max != "":
                if EC.data_is_int(ms_inf_max) == 0:
                    QMessageBox.warning(self, "Warning",
                                        "All parameters to be entered. \n The value must be numerical.",
                                        QMessageBox.Ok)
                    test = 1

            if usura_min != "":
                if EC.data_is_int(usura_min) == 0:
                    QMessageBox.warning(self, "Warning",
                                        "All parameters to be entered. \n The value must be numerical.",
                                        QMessageBox.Ok)
                    test = 1

            if usura_max != "":
                if EC.data_is_int(usura_max) == 0:
                    QMessageBox.warning(self, "Warning",
                                        "All parameters to be entered. \n The value must be numerical.",
                                        QMessageBox.Ok)
                    test = 1

            if id_endo != "":
                if EC.data_is_int(id_endo) == 0:
                    QMessageBox.warning(self, "Warning",
                                        "All parameters to be entered. \n The value must be numerical.",
                                        QMessageBox.Ok)
                    test = 1

            if is_endo != "":
                if EC.data_is_int(is_endo) == 0:
                    QMessageBox.warning(self, "Warning",
                                        "All parameters to be entered. \n The value must be numerical.",
                                        QMessageBox.Ok)
                    test = 1

            if iid_endo != "":
                if EC.data_is_int(iid_endo) == 0:
                    QMessageBox.warning(self, "Warning",
                                        "All parameters to be entered. \n The value must be numerical.",
                                        QMessageBox.Ok)
                    test = 1

            if iis_endo != "":
                if EC.data_is_int(iis_endo) == 0:
                    QMessageBox.warning(self, "Warning",
                                        "All parameters to be entered. \n The value must be numerical.",
                                        QMessageBox.Ok)
                    test = 1

            if iiid_endo != "":
                if EC.data_is_int(iiid_endo) == 0:
                    QMessageBox.warning(self, "Warning",
                                        "All parameters to be entered. \n The value must be numerical.",
                                        QMessageBox.Ok)
                    test = 1

            if iiis_endo != "":
                if EC.data_is_int(iiis_endo) == 0:
                    QMessageBox.warning(self, "Warning",
                                        "All parameters to be entered. \n The value must be numerical.",
                                        QMessageBox.Ok)
                    test = 1

            if iv_endo != "":
                if EC.data_is_int(iv_endo) == 0:
                    QMessageBox.warning(self, "Warning",
                                        "All parameters to be entered. \n The value must be numerical.",
                                        QMessageBox.Ok)
                    test = 1

            if v_endo != "":
                if EC.data_is_int(v_endo) == 0:
                    QMessageBox.warning(self, "Warning",
                                        "All parameters to be entered. \n The value must be numerical.",
                                        QMessageBox.Ok)
                    test = 1

            if vi_endo != "":
                if EC.data_is_int(vi_endo) == 0:
                    QMessageBox.warning(self, "Warning",
                                        "All parameters to be entered. \n The value must be numerical.",
                                        QMessageBox.Ok)
                    test = 1

            if vii_endo != "":
                if EC.data_is_int(vii_endo) == 0:
                    QMessageBox.warning(self, "Warning",
                                        "All parameters to be entered. \n The value must be numerical.",
                                        QMessageBox.Ok)
                    test = 1

            if viiid_endo != "":
                if EC.data_is_int(viiid_endo) == 0:
                    QMessageBox.warning(self, "Warning",
                                        "All parameters to be entered. \n The value must be numerical.",
                                        QMessageBox.Ok)
                    test = 1

            if viiis_endo != "":
                if EC.data_is_int(viiis_endo) == 0:
                    QMessageBox.warning(self, "Warning",
                                        "All parameters to be entered. \n The value must be numerical.",
                                        QMessageBox.Ok)
                    test = 1

            if ixd_endo != "":
                if EC.data_is_int(ixd_endo) == 0:
                    QMessageBox.warning(self, "Warning",
                                        "All parameters to be entered. \n The value must be numerical.",
                                        QMessageBox.Ok)
                    test = 1

            if ixs_endo != "":
                if EC.data_is_int(ixs_endo) == 0:
                    QMessageBox.warning(self, "Warning",
                                        "All parameters to be entered. \n The value must be numerical.",
                                        QMessageBox.Ok)
                    test = 1

            if xd_endo != "":
                if EC.data_is_int(xd_endo) == 0:
                    QMessageBox.warning(self, "Warning",
                                        "All parameters to be entered. \n The value must be numerical.",
                                        QMessageBox.Ok)
                    test = 1

            if xs_endo != "":
                if EC.data_is_int(xs_endo) == 0:
                    QMessageBox.warning(self, "Warning",
                                        "All parameters to be entered. \n The value must be numerical.",
                                        QMessageBox.Ok)
                    test = 1

            if endo_min != "":
                if EC.data_is_int(endo_min) == 0:
                    QMessageBox.warning(self, "Warning",
                                        "All parameters to be entered. \n The value must be numerical.",
                                        QMessageBox.Ok)
                    test = 1

            if endo_max != "":
                if EC.data_is_int(endo_max) == 0:
                    QMessageBox.warning(self, "Warning",
                                        "All parameters to be entered. \n The value must be numerical.",
                                        QMessageBox.Ok)
                    test = 1

            if v1 != "":
                if EC.data_is_int(v1) == 0:
                    QMessageBox.warning(self, "Warning",
                                        "All parameters to be entered. \n The value must be numerical.",
                                        QMessageBox.Ok)
                    test = 1

            if v2 != "":
                if EC.data_is_int(v2) == 0:
                    QMessageBox.warning(self, "Warning",
                                        "All parameters to be entered. \n The value must be numerical.",
                                        QMessageBox.Ok)
                    test = 1

            if v3 != "":
                if EC.data_is_int(v3) == 0:
                    QMessageBox.warning(self, "Warning",
                                        "All parameters to be entered. \n The value must be numerical.",
                                        QMessageBox.Ok)
                    test = 1

            if v4 != "":
                if EC.data_is_int(v4) == 0:
                    QMessageBox.warning(self, "Warning",
                                        "All parameters to be entered. \n The value must be numerical.",
                                        QMessageBox.Ok)
                    test = 1

            if v5 != "":
                if EC.data_is_int(v5) == 0:
                    QMessageBox.warning(self, "Warning",
                                        "All parameters to be entered. \n The value must be numerical.",
                                        QMessageBox.Ok)
                    test = 1

            if v6 != "":
                if EC.data_is_int(v6) == 0:
                    QMessageBox.warning(self, "Warning",
                                        "All parameters to be entered. \n The value must be numerical.",
                                        QMessageBox.Ok)
                    test = 1

            if v7 != "":
                if EC.data_is_int(v7) == 0:
                    QMessageBox.warning(self, "Warning",
                                        "All parameters to be entered. \n The value must be numerical.",
                                        QMessageBox.Ok)
                    test = 1

            if l6 != "":
                if EC.data_is_int(l6) == 0:
                    QMessageBox.warning(self, "Warning",
                                        "All parameters to be entered. \n The value must be numerical.",
                                        QMessageBox.Ok)
                    test = 1

            if l7 != "":
                if EC.data_is_int(l7) == 0:
                    QMessageBox.warning(self, "Warning",
                                        "All parameters to be entered. \n The value must be numerical.",
                                        QMessageBox.Ok)
                    test = 1

            if l8 != "":
                if EC.data_is_int(l8) == 0:
                    QMessageBox.warning(self, "Warning",
                                        "All parameters to be entered. \n The value must be numerical.",
                                        QMessageBox.Ok)
                    test = 1

            if l9 != "":
                if EC.data_is_int(l9) == 0:
                    QMessageBox.warning(self, "Warning",
                                        "All parameters to be entered. \n The value must be numerical.",
                                        QMessageBox.Ok)
                    test = 1

            if l10 != "":
                if EC.data_is_int(l10) == 0:
                    QMessageBox.warning(self, "Warning",
                                        "All parameters to be entered. \n The value must be numerical.",
                                        QMessageBox.Ok)
                    test = 1

            if v_min != "":
                if EC.data_is_int(v_min) == 0:
                    QMessageBox.warning(self, "Warning",
                                        "All parameters to be entered. \n The value must be numerical.",
                                        QMessageBox.Ok)
                    test = 1

            if v_max != "":
                if EC.data_is_int(v_max) == 0:
                    QMessageBox.warning(self, "Warning",
                                        "All parameters to be entered. \n The value must be numerical.",
                                        QMessageBox.Ok)
                    test = 1

            if a_l_min != "":
                if EC.data_is_int(a_l_min) == 0:
                    QMessageBox.warning(self, "Warning",
                                        "All parameters to be entered. \n The value must be numerical.",
                                        QMessageBox.Ok)
                    test = 1

            if a_l_max != "":
                if EC.data_is_int(a_l_max) == 0:
                    QMessageBox.warning(self, "Warning",
                                        "All parameters to be entered. \n The value must be numerical.",
                                        QMessageBox.Ok)
                    test = 1

            if ecto_min != "":
                if EC.data_is_int(ecto_min) == 0:
                    QMessageBox.warning(self, "Warning",
                                        "All parameters to be entered. \n The value must be numerical.",
                                        QMessageBox.Ok)
                    test = 1

            if ecto_max != "":
                if EC.data_is_int(ecto_max) == 0:
                    QMessageBox.warning(self, "Warning",
                                        "All parameters to be entered. \n The value must be numerical.",
                                        QMessageBox.Ok)
                    test = 1
        return test

    def insert_new_rec(self):
        if self.lineEdit_sinf_min.text() == "":
            sinf_min = None
        else:
            sinf_min = int(self.lineEdit_sinf_min.text())

        if self.lineEdit_sinf_max.text() == "":
            sinf_max = None
        else:
            sinf_max = int(self.lineEdit_sinf_max.text())

        if self.lineEdit_sinf_min_2.text() == "":
            sinf_min_2 = None
        else:
            sinf_min_2 = int(self.lineEdit_sinf_min_2.text())

        if self.lineEdit_sinf_max_2.text() == "":
            sinf_max_2 = None
        else:
            sinf_max_2 = int(self.lineEdit_sinf_max_2.text())

        if self.comboBox_SSPIA.currentText() == "":
            SSPIA = None
        else:
            SSPIA = int(self.comboBox_SSPIA.currentText())

        if self.comboBox_SSPIB.currentText() == "":
            SSPIB = None
        else:
            SSPIB = int(self.comboBox_SSPIB.currentText())

        if self.comboBox_SSPIC.currentText() == "":
            SSPIC = None
        else:
            SSPIC = int(self.comboBox_SSPIC.currentText())

        if self.comboBox_SSPID.currentText() == "":
            SSPID = None
        else:
            SSPID = int(self.comboBox_SSPID.currentText())

        if self.lineEdit_sup_aur_min.text() == "":
            sup_aur_min = None
        else:
            sup_aur_min = int(self.lineEdit_sup_aur_min.text())

        if self.lineEdit_sup_aur_max.text() == "":
            sup_aur_max = None
        else:
            sup_aur_max = int(self.lineEdit_sup_aur_max.text())

        if self.lineEdit_sup_aur_min_2.text() == "":
            sup_aur_min_2 = None
        else:
            sup_aur_min_2 = int(self.lineEdit_sup_aur_min_2.text())

        if self.lineEdit_sup_aur_max_2.text() == "":
            sup_aur_max_2 = None
        else:
            sup_aur_max_2 = int(self.lineEdit_sup_aur_max_2.text())

        if self.lineEdit_ms_sup_min.text() == "":
            ms_sup_min = None
        else:
            ms_sup_min = int(self.lineEdit_ms_sup_min.text())

        if self.lineEdit_ms_sup_max.text() == "":
            ms_sup_max = None
        else:
            ms_sup_max = int(self.lineEdit_ms_sup_max.text())

        if self.lineEdit_ms_inf_min.text() == "":
            ms_inf_min = None
        else:
            ms_inf_min = int(self.lineEdit_ms_inf_min.text())

        if self.lineEdit_ms_inf_max.text() == "":
            ms_inf_max = None
        else:
            ms_inf_max = int(self.lineEdit_ms_inf_max.text())

        if self.lineEdit_usura_min.text() == "":
            usura_min = None
        else:
            usura_min = int(self.lineEdit_usura_min.text())

        if self.lineEdit_usura_max.text() == "":
            usura_max = None
        else:
            usura_max = int(self.lineEdit_usura_max.text())

        if self.comboBox_Id_endo.currentText() == "":
            Id_endo = None
        else:
            Id_endo = int(self.comboBox_Id_endo.currentText())

        if self.comboBox_Is_endo.currentText() == "":
            Is_endo = None
        else:
            Is_endo = int(self.comboBox_Is_endo.currentText())

        if self.comboBox_IId_endo.currentText() == "":
            IId_endo = None
        else:
            IId_endo = int(self.comboBox_IId_endo.currentText())

        if self.comboBox_IIs_endo.currentText() == "":
            IIs_endo = None
        else:
            IIs_endo = int(self.comboBox_IIs_endo.currentText())

        if self.comboBox_IIId_endo.currentText() == "":
            IIId_endo = None
        else:
            IIId_endo = int(self.comboBox_IIId_endo.currentText())

        if self.comboBox_IIIs_endo.currentText() == "":
            IIIs_endo = None
        else:
            IIIs_endo = int(self.comboBox_IIIs_endo.currentText())

        if self.comboBox_IV_endo.currentText() == "":
            IV_endo = None
        else:
            IV_endo = int(self.comboBox_IV_endo.currentText())

        if self.comboBox_V_endo.currentText() == "":
            V_endo = None
        else:
            V_endo = int(self.comboBox_V_endo.currentText())

        if self.comboBox_VI_endo.currentText() == "":
            VI_endo = None
        else:
            VI_endo = int(self.comboBox_VI_endo.currentText())

        if self.comboBox_VII_endo.currentText() == "":
            VII_endo = None
        else:
            VII_endo = int(self.comboBox_VII_endo.currentText())

        if self.comboBox_VIIId_endo.currentText() == "":
            VIIId_endo = None
        else:
            VIIId_endo = int(self.comboBox_VIIId_endo.currentText())

        if self.comboBox_VIIIs_endo.currentText() == "":
            VIIIs_endo = None
        else:
            VIIIs_endo = int(self.comboBox_VIIIs_endo.currentText())

        if self.comboBox_IXd_endo.currentText() == "":
            IXd_endo = None
        else:
            IXd_endo = int(self.comboBox_IXd_endo.currentText())

        if self.comboBox_IXs_endo.currentText() == "":
            IXs_endo = None
        else:
            IXs_endo = int(self.comboBox_IXs_endo.currentText())

        if self.comboBox_Xd_endo.currentText() == "":
            Xd_endo = None
        else:
            Xd_endo = int(self.comboBox_Xd_endo.currentText())

        if self.comboBox_Xs_endo.currentText() == "":
            Xs_endo = None
        else:
            Xs_endo = int(self.comboBox_Xs_endo.currentText())

        if self.lineEdit_endo_min.text() == "":
            endo_min = None
        else:
            endo_min = int(self.lineEdit_endo_min.text())

        if self.lineEdit_endo_max.text() == "":
            endo_max = None
        else:
            endo_max = int(self.lineEdit_endo_max.text())

        if self.comboBox_volta_1.currentText() == "":
            volta_1 = None
        else:
            volta_1 = int(self.comboBox_volta_1.currentText())

        if self.comboBox_volta_2.currentText() == "":
            volta_2 = None
        else:
            volta_2 = int(self.comboBox_volta_2.currentText())

        if self.comboBox_volta_3.currentText() == "":
            volta_3 = None
        else:
            volta_3 = int(self.comboBox_volta_3.currentText())

        if self.comboBox_volta_4.currentText() == "":
            volta_4 = None
        else:
            volta_4 = int(self.comboBox_volta_4.currentText())

        if self.comboBox_volta_5.currentText() == "":
            volta_5 = None
        else:
            volta_5 = int(self.comboBox_volta_5.currentText())

        if self.comboBox_volta_6.currentText() == "":
            volta_6 = None
        else:
            volta_6 = int(self.comboBox_volta_6.currentText())

        if self.comboBox_volta_7.currentText() == "":
            volta_7 = None
        else:
            volta_7 = int(self.comboBox_volta_7.currentText())

        if self.comboBox_lat_6.currentText() == "":
            lat_6 = None
        else:
            lat_6 = int(self.comboBox_lat_6.currentText())

        if self.comboBox_lat_7.currentText() == "":
            lat_7 = None
        else:
            lat_7 = int(self.comboBox_lat_7.currentText())

        if self.comboBox_lat_8.currentText() == "":
            lat_8 = None
        else:
            lat_8 = int(self.comboBox_lat_8.currentText())

        if self.comboBox_lat_9.currentText() == "":
            lat_9 = None
        else:
            lat_9 = int(self.comboBox_lat_9.currentText())

        if self.comboBox_lat_10.currentText() == "":
            lat_10 = None
        else:
            lat_10 = int(self.comboBox_lat_10.currentText())

        if self.lineEdit_volta_min.text() == "":
            volta_min = None
        else:
            volta_min = int(self.lineEdit_volta_min.text())

        if self.lineEdit_volta_max.text() == "":
            volta_max = None
        else:
            volta_max = int(self.lineEdit_volta_max.text())

        if self.lineEdit_ant_lat_min.text() == "":
            ant_lat_min = None
        else:
            ant_lat_min = int(self.lineEdit_ant_lat_min.text())

        if self.lineEdit_ant_lat_max.text() == "":
            ant_lat_max = None
        else:
            ant_lat_max = int(self.lineEdit_ant_lat_max.text())

        if self.lineEdit_ecto_min.text() == "":
            ecto_min = None
        else:
            ecto_min = int(self.lineEdit_ecto_min.text())

        if self.lineEdit_ecto_max.text() == "":
            ecto_max = None
        else:
            ecto_max = int(self.lineEdit_ecto_max.text())

        try:
            data = self.DB_MANAGER.insert_values_deteta(
                self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, self.ID_TABLE) + 1,
                str(self.comboBox_sito.currentText()),  # 1 - Sito
                int(self.lineEdit_nr_individuo.text()),  # 2 - Num individuo
                sinf_min,  # 3 - Num individuo
                sinf_max,  # 4
                sinf_min_2,  # 5
                sinf_max_2,  # 6
                SSPIA,  # 7
                SSPIB,  # 8
                SSPIC,  # 9
                SSPID,  # 10
                sup_aur_min,  # 11
                sup_aur_max,  # 12
                sup_aur_min_2,  # 13
                sup_aur_max_2,  # 14
                ms_sup_min,  # 15
                ms_sup_max,  # 16
                ms_inf_min,  # 17
                ms_inf_max,  # 18
                usura_min,  # 19
                usura_max,  # 20
                Id_endo,  # 21
                Is_endo,  # 22
                IId_endo,  # 23
                IIs_endo,  # 24
                IIId_endo,  # 25
                IIIs_endo,  # 26
                IV_endo,  # 27
                V_endo,  # 28
                VI_endo,  # 29
                VII_endo,  # 30
                VIIId_endo,  # 31
                VIIIs_endo,  # 32
                IXd_endo,  # 33
                IXs_endo,  # 34
                Xd_endo,  # 35
                Xs_endo,  # 36
                endo_min,  # 37
                endo_max,  # 38
                volta_1,  # 39
                volta_2,  # 40
                volta_3,  # 41
                volta_4,  # 42
                volta_5,  # 43
                volta_6,  # 44
                volta_7,  # 45
                lat_6,  # 46
                lat_7,  # 47
                lat_8,  # 48
                lat_9,  # 49
                lat_10,  # 50
                volta_min,  # 51
                volta_max,  # 52
                ant_lat_min,  # 53
                ant_lat_max,  # 54
                ecto_min,  # 55
                ecto_max  # 56
            )

            try:
                self.DB_MANAGER.insert_data_session(data)
                return 1
            except Exception as e:
                e_str = str(e)
                if e_str.__contains__("IntegrityError"):
                    
                    if self.L=='it':
                        msg = self.ID_TABLE + " gia' presente nel database"
                        QMessageBox.warning(self, "Error", "Error" + str(msg), QMessageBox.Ok)
                    elif self.L=='de':
                        msg = self.ID_TABLE + " bereits in der Datenbank"
                        QMessageBox.warning(self, "Error", "Error" + str(msg), QMessageBox.Ok)  
                    else:
                        msg = self.ID_TABLE + " exist in db"
                        QMessageBox.warning(self, "Error", "Error" + str(msg), QMessageBox.Ok)  
                else:
                    msg = e
                    QMessageBox.warning(self, "Error", "Error 1 \n" + str(msg), QMessageBox.Ok)
                return 0

        except Exception as e:
            QMessageBox.warning(self, "Error", "Error 2 \n" + str(e), QMessageBox.Ok)
            return 0

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

    def on_pushButton_insert_row_rapporti_pressed(self):
        self.insert_new_row('self.tableWidget_rapporti')

    def on_pushButton_insert_row_inclusi_pressed(self):
        self.insert_new_row('self.tableWidget_inclusi')

    def on_pushButton_insert_row_campioni_pressed(self):
        self.insert_new_row('self.tableWidget_campioni')

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
            self.customize_GUI()

            # records surf functions

    def on_pushButton_first_rec_pressed(self):
        if self.check_record_state() == 1:
            self.customize_GUI()
        else:
            try:
                self.empty_fields()
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                self.fill_fields(0)
                self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e), QMessageBox.Ok)

    def on_pushButton_last_rec_pressed(self):
        if self.check_record_state() == 1:
            self.customize_GUI()
        else:
            try:
                self.empty_fields()
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), len(self.DATA_LIST) - 1
                self.fill_fields(self.REC_CORR)
                self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e), QMessageBox.Ok)

    def on_pushButton_prev_rec_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            self.REC_CORR = self.REC_CORR - 1
            if self.REC_CORR == -1:
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
                except Exception as e:
                    QMessageBox.warning(self, "Errore", str(e), QMessageBox.Ok)
        self.customize_GUI()

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
                except Exception as e:
                    QMessageBox.warning(self, "Error", str(e), QMessageBox.Ok)
        self.customize_GUI()

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
                QMessageBox.warning(self, "Messagio!!!", "Action deleted!")
            else:
                try:
                    id_to_delete = eval("self.DATA_LIST[self.REC_CORR]." + self.ID_TABLE)
                    self.DB_MANAGER.delete_one_record(self.TABLE_NAME, self.ID_TABLE, id_to_delete)
                    self.charge_records()  # charge records from DB
                    QMessageBox.warning(self, "Messaggio!!!", "Record deleted!")
                except Exception as e:
                    QMessageBox.warning(self, "Messaggio!!!", "error type: " + str(e))
                if not bool(self.DATA_LIST):
                    QMessageBox.warning(self, "Attenzione", "the db is empty!", QMessageBox.Ok)
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
        self.customize_GUI()

    def on_pushButton_new_search_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            self.enable_button_search(0)

            self.setComboBoxEditable(["self.comboBox_sito"], 1)

            # set the GUI for a new search

            if self.BROWSE_STATUS != "f":
                self.BROWSE_STATUS = "f"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.empty_fields()
                self.set_rec_counter('', '')
                self.label_sort.setText(self.SORTED_ITEMS["n"])

                # self.setComboBoxEditable(["self.comboBox_sito"],1)
                # self.setComboBoxEnable(["self.comboBox_sito"],"True")
                # self.setComboBoxEnable(["self.lineEdit_us"],"True")
                # self.setComboBoxEnable(["self.lineEdit_individuo"],"True")

    def on_pushButton_search_go_pressed(self):
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

            # TableWidget

            if self.lineEdit_individuo.text() != "":
                individuo = int(self.lineEdit_individuo.text())
            else:
                individuo = ""

            if self.comboBox_eta_min.currentText() != "":
                eta_min = int(self.comboBox_eta_min.currentText())
            else:
                eta_min = ""

            if self.comboBox_eta_max.currentText() != "":
                eta_max = int(self.comboBox_eta_max.currentText())
            else:
                eta_max = ""

            search_dict = {
                self.TABLE_FIELDS[0]: "'" + str(self.comboBox_sito.currentText()) + "'",  # 0 - Sito
                self.TABLE_FIELDS[1]: int(self.lineEdit_nr_individuo.text()),  # 1 - Num individuo
                self.TABLE_FIELDS[2]: int(self.lineEdit_sinf_min.text()),  # 10 - Sinfisi pubica tot
                self.TABLE_FIELDS[3]: int(self.lineEdit_sinf_max.text()),  # 11 - Sinfisi pubica tot
                self.TABLE_FIELDS[4]: int(self.lineEdit_sinf_min_2.text()),  # 10 - Sinfisi pubica tot
                self.TABLE_FIELDS[5]: int(self.lineEdit_sinf_max_2.text()),  # 11 - Sinfisi pubica tot
                self.TABLE_FIELDS[6]: int(self.comboBox_SSPIA.currentText()),  # 12 - SSPIA età
                self.TABLE_FIELDS[7]: int(self.comboBox_SSPIB.currentText()),  # 13 - SSPIB età
                self.TABLE_FIELDS[8]: int(self.comboBox_SSPIC.currentText()),  # 14 - SSPIC età
                self.TABLE_FIELDS[9]: int(self.comboBox_SSPID.currentText()),  # 15 - SSPID età
                self.TABLE_FIELDS[10]: int(self.lineEdit_sup_aur_min.text()),  # 17 - Mascellare superiore tot
                self.TABLE_FIELDS[11]: int(self.lineEdit_sup_aur_max.text()),  # 18 - Mascellare inferiore tot
                self.TABLE_FIELDS[12]: int(self.lineEdit_sup_aur_min_2.text()),  # 17 - Mascellare superiore tot
                self.TABLE_FIELDS[13]: int(self.lineEdit_sup_aur_max_2.text()),  # 18 - Mascellare inferiore tot
                self.TABLE_FIELDS[14]: int(self.lineEdit_ms_sup_min.text()),  # 27 - Usura dentaria tot
                self.TABLE_FIELDS[15]: int(self.lineEdit_ms_sup_max.text()),  # 28 - Usura dentaria tot
                self.TABLE_FIELDS[16]: int(self.lineEdit_ms_inf_min.text()),  # 38 - Usura dentaria tot
                self.TABLE_FIELDS[17]: int(self.lineEdit_ms_inf_max.text()),  # 39 - Usura dentaria tot
                self.TABLE_FIELDS[18]: int(self.lineEdit_usura_min.text()),  # 40 - Usura dentaria tot
                self.TABLE_FIELDS[19]: int(self.lineEdit_usura_max.text()),  # 41 - Usura dentaria tot
                self.TABLE_FIELDS[20]: int(self.comboBox_Id_endo.currentText()),  # 42 - 1d suture endocraniche
                self.TABLE_FIELDS[21]: int(self.comboBox_Is_endo.currentText()),  # 43 - 1s suture endocraniche
                self.TABLE_FIELDS[22]: int(self.comboBox_IId_endo.currentText()),  # 44 - 2d suture endocraniche
                self.TABLE_FIELDS[23]: int(self.comboBox_IIs_endo.currentText()),  # 45 - 2s suture endocraniche
                self.TABLE_FIELDS[24]: int(self.comboBox_IIId_endo.currentText()),  # 46 - 3d suture endocraniche
                self.TABLE_FIELDS[25]: int(self.comboBox_IIIs_endo.currentText()),  # 47 - 3s suture endocraniche
                self.TABLE_FIELDS[26]: int(self.comboBox_IV_endo.currentText()),  # 48 - 4 suture endocraniche
                self.TABLE_FIELDS[27]: int(self.comboBox_V_endo.currentText()),  # 49 - 5 suture endocraniche
                self.TABLE_FIELDS[28]: int(self.comboBox_VI_endo.currentText()),  # 50 - 6 suture endocraniche
                self.TABLE_FIELDS[29]: int(self.comboBox_VII_endo.currentText()),  # 51 - 7 suture endocraniche
                self.TABLE_FIELDS[30]: int(self.comboBox_VIIId_endo.currentText()),  # 52 - 8d suture endocraniche
                self.TABLE_FIELDS[31]: int(self.comboBox_VIIIs_endo.currentText()),  # 53 - 8s suture endocraniche
                self.TABLE_FIELDS[32]: int(self.comboBox_IXd_endo.currentText()),  # 54 - 9d suture endocraniche
                self.TABLE_FIELDS[33]: int(self.comboBox_IXs_endo.currentText()),  # 55 - 9s suture endocraniche
                self.TABLE_FIELDS[34]: int(self.comboBox_Xd_endo.currentText()),  # 56 - 10d suture endocraniche
                self.TABLE_FIELDS[35]: int(self.comboBox_Xs_endo.currentText()),  # 57 - 10s suture endocraniche
                self.TABLE_FIELDS[36]: int(self.lineEdit_endo_min.text()),  # 58 - Range suture endocraniche
                self.TABLE_FIELDS[37]: int(self.lineEdit_endo_max.text()),  # 59 - Range suture endocraniche
                self.TABLE_FIELDS[38]: int(self.comboBox_volta_1.currentText()),  # 60 - Suture volta 1
                self.TABLE_FIELDS[39]: int(self.comboBox_volta_2.currentText()),  # 61 - Suture volta 2
                self.TABLE_FIELDS[40]: int(self.comboBox_volta_3.currentText()),  # 62 - Suture volta 3
                self.TABLE_FIELDS[41]: int(self.comboBox_volta_4.currentText()),  # 63 - Suture volta 4
                self.TABLE_FIELDS[42]: int(self.comboBox_volta_5.currentText()),  # 64 - Suture volta 5
                self.TABLE_FIELDS[43]: int(self.comboBox_volta_6.currentText()),  # 65 - Suture volta 6
                self.TABLE_FIELDS[44]: int(self.comboBox_volta_7.currentText()),  # 66 - Suture volta 7
                self.TABLE_FIELDS[45]: int(self.comboBox_lat_6.currentText()),  # 67 - Suture antero laterali 6
                self.TABLE_FIELDS[46]: int(self.comboBox_lat_7.currentText()),  # 68 - Suture antero laterali 7
                self.TABLE_FIELDS[47]: int(self.comboBox_lat_8.currentText()),  # 69 - Suture antero laterali 8
                self.TABLE_FIELDS[48]: int(self.comboBox_lat_9.currentText()),  # 70 - Suture antero laterali 9
                self.TABLE_FIELDS[49]: int(self.comboBox_lat_10.currentText()),  # 71 - Suture antero laterali 10
                self.TABLE_FIELDS[50]: int(self.lineEdit_volta_min.text()),  # 72 - Volta totale
                self.TABLE_FIELDS[51]: int(self.lineEdit_volta_max.text()),  # 73 - Antero laterali totale
                self.TABLE_FIELDS[52]: int(self.lineEdit_ant_lat_min.text()),  # 74 - Range suture ectocraniche
                self.TABLE_FIELDS[53]: int(self.lineEdit_ant_lat_max.text()),  # 75 - Range suture ectocraniche
                self.TABLE_FIELDS[54]: int(self.lineEdit_ecto_min.text()),  # 76 - Range suture ectocraniche
                self.TABLE_FIELDS[55]: int(self.lineEdit_ecto_max.text())  # 77 - Range suture ectocraniche
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
                        QMessageBox.warning(self, "WARNING," "No record found!", QMessageBox.Ok)

                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                    self.fill_fields(self.REC_CORR)
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])

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
                                id_us_list = self.charge_id_us_for_individuo()
                                self.pyQGIS.charge_individui_us(id_us_list)
                        else:
                            strings = ("Sono stati trovati", self.REC_TOT, "records")
                            if self.toolButtonGis.isChecked():
                                id_us_list = self.charge_id_us_for_individuo()
                                self.pyQGIS.charge_individui_us(id_us_list)
                    
                    elif self.L=='de':
                        if self.REC_TOT == 1:
                            strings = ("Es wurde gefunden", self.REC_TOT, "record")
                            if self.toolButtonGis.isChecked():
                                id_us_list = self.charge_id_us_for_individuo()
                                self.pyQGIS.charge_individui_us(id_us_list)
                        else:
                            strings = ("Sie wurden gefunden", self.REC_TOT, "records")
                            if self.toolButtonGis.isChecked():
                                id_us_list = self.charge_id_us_for_individuo()
                                self.pyQGIS.charge_individui_us(id_us_list)
                    
                    else:
                        if self.REC_TOT == 1:
                            strings = ("It has been found", self.REC_TOT, "record")
                            if self.toolButtonGis.isChecked():
                                id_us_list = self.charge_id_us_for_individuo()
                                self.pyQGIS.charge_individui_us(id_us_list)
                        else:
                            strings = ("They have been found", self.REC_TOT, "records")
                            if self.toolButtonGis.isChecked():
                                id_us_list = self.charge_id_us_for_individuo()
                                self.pyQGIS.charge_individui_us(id_us_list)
                    
                    QMessageBox.warning(self, "Message", "%s %d %s" % strings, QMessageBox.Ok)

        self.enable_button_search(1)
        self.customize_GUI()

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

                # custom functions

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
        pass

    def insert_new_row(self, table_name):
        """insert new row into a table based on table_name"""
        cmd = table_name + ".insertRow(0)"
        eval(cmd)

    def empty_fields(self):
        # rapporti_row_count = self.tableWidget_rapporti.rowCount()
        # campioni_row_count = self.tableWidget_campioni.rowCount()
        # inclusi_row_count = self.tableWidget_inclusi.rowCount()

        self.comboBox_sito.setEditText("")  # 1 - Sito
        self.lineEdit_nr_individuo.clear()  # 2 - Num individuo
        self.lineEdit_sinf_min.clear()  # 11 - Sinfisi pubica tot
        self.lineEdit_sinf_max.clear()  # 12 - Sinfisi pubica tot
        self.lineEdit_sinf_min_2.clear()  # 11 - Sinfisi pubica tot
        self.lineEdit_sinf_max_2.clear()  # 12 - Sinfisi pubica tot
        self.comboBox_SSPIA.setEditText("")  # 13 - SSPIA età
        self.comboBox_SSPIB.setEditText("")  # 14 - SSPIB età
        self.comboBox_SSPIC.setEditText("")  # 15 - SSPIC età
        self.comboBox_SSPID.setEditText("")  # 16 - SSPID età
        self.lineEdit_sup_aur_min.clear()  # 18 - Mascellare superiore tot
        self.lineEdit_sup_aur_max.clear()  # 19 - Mascellare inferiore tot
        self.lineEdit_sup_aur_min_2.clear()  # 18 - Mascellare superiore tot
        self.lineEdit_sup_aur_max_2.clear()  # 19 - Mascellare inferiore tot
        self.lineEdit_ms_sup_min.clear()  # 28 - Mascellare superiore 12-18
        self.lineEdit_ms_sup_max.clear()  # 29 - Mascellare superiore 12-18
        self.lineEdit_ms_inf_min.clear()  # 39 - Mascellare superiore 12-18
        self.lineEdit_ms_inf_max.clear()  # 40 - Mascellare superiore 12-18
        self.lineEdit_usura_min.clear()  # 41 - Mascellare superiore 12-18
        self.lineEdit_usura_max.clear()  # 42 - Mascellare superiore 12-18
        self.comboBox_Id_endo.setEditText("")  # 43 - 1d suture endocraniche
        self.comboBox_Is_endo.setEditText("")  # 44 - 1s suture endocraniche
        self.comboBox_IId_endo.setEditText("")  # 45 - 2d suture endocraniche
        self.comboBox_IIs_endo.setEditText("")  # 46 - 2s suture endocraniche
        self.comboBox_IIId_endo.setEditText("")  # 47 - 3d suture endocraniche
        self.comboBox_IIIs_endo.setEditText("")  # 48 - 3s suture endocraniche
        self.comboBox_IV_endo.setEditText("")  # 49 - 4 suture endocraniche
        self.comboBox_V_endo.setEditText("")  # 50 - 5 suture endocraniche
        self.comboBox_VI_endo.setEditText("")  # 51 - 6 suture endocraniche
        self.comboBox_VII_endo.setEditText("")  # 52 - 7 suture endocraniche
        self.comboBox_VIIId_endo.setEditText("")  # 53 - 8d suture endocraniche
        self.comboBox_VIIIs_endo.setEditText("")  # 54 - 8s suture endocraniche
        self.comboBox_IXd_endo.setEditText("")  # 55 - 9d suture endocraniche
        self.comboBox_IXs_endo.setEditText("")  # 56 - 9s suture endocraniche
        self.comboBox_Xd_endo.setEditText("")  # 57 - 10d suture endocraniche
        self.comboBox_Xs_endo.setEditText("")  # 58 - 10s suture endocraniche
        self.lineEdit_endo_min.clear()  # 59 - Range suture endocraniche
        self.lineEdit_endo_max.clear()  # 60 - Range suture endocraniche
        self.comboBox_volta_1.setEditText("")  # 61 - Suture volta 1
        self.comboBox_volta_2.setEditText("")  # 62 - Suture volta 2
        self.comboBox_volta_3.setEditText("")  # 63 - Suture volta 3
        self.comboBox_volta_4.setEditText("")  # 64 - Suture volta 4
        self.comboBox_volta_5.setEditText("")  # 65 - Suture volta 5
        self.comboBox_volta_6.setEditText("")  # 66 - Suture volta 6
        self.comboBox_volta_7.setEditText("")  # 67 - Suture volta 7
        self.comboBox_lat_6.setEditText("")  # 68 - Suture antero laterali 6
        self.comboBox_lat_7.setEditText("")  # 69 - Suture antero laterali 7
        self.comboBox_lat_8.setEditText("")  # 70 - Suture antero laterali 8
        self.comboBox_lat_9.setEditText("")  # 71 - Suture antero laterali 9
        self.comboBox_lat_10.setEditText("")  # 72 - Suture antero laterali 10
        self.lineEdit_volta_min.clear()  # 73 - Volta totale
        self.lineEdit_volta_max.clear()  # 74 - Antero laterali totale
        self.lineEdit_ant_lat_min.clear()  # 75 - Range suture ectocraniche
        self.lineEdit_ant_lat_max.clear()  # 76 - Range suture ectocraniche
        self.lineEdit_ecto_min.clear()  # 77 - Range suture ectocraniche
        self.lineEdit_ecto_max.clear()  # 78 - Range suture ectocraniche

    def fill_fields(self, n=0):
        self.rec_num = n
        try:

            self.comboBox_sito.setEditText(str(self.DATA_LIST[self.rec_num].sito))  # 1 - Sito
            self.lineEdit_nr_individuo.setText(str(self.DATA_LIST[self.rec_num].nr_individuo))

            if self.DATA_LIST[self.rec_num].sinf_min == None:  # 3
                self.lineEdit_sinf_min.setText("")
            else:
                self.lineEdit_sinf_min.setText(str(self.DATA_LIST[self.rec_num].sinf_min))

            if self.DATA_LIST[self.rec_num].sinf_max == None:  # 4
                self.lineEdit_sinf_max.setText("")
            else:
                self.lineEdit_sinf_max.setText(str(self.DATA_LIST[self.rec_num].sinf_max))

            if self.DATA_LIST[self.rec_num].sinf_min_2 == None:  # 5
                self.lineEdit_sinf_min_2.setText("")
            else:
                self.lineEdit_sinf_min_2.setText(str(self.DATA_LIST[self.rec_num].sinf_min_2))

            if self.DATA_LIST[self.rec_num].sinf_max_2 == None:  # 6
                self.lineEdit_sinf_max_2.setText("")
            else:
                self.lineEdit_sinf_max_2.setText(str(self.DATA_LIST[self.rec_num].sinf_max_2))

            if self.DATA_LIST[self.rec_num].SSPIA == None:  # 7
                self.comboBox_SSPIA.setEditText("")
            else:
                self.comboBox_SSPIA.setEditText(str(self.DATA_LIST[self.rec_num].SSPIA))

            if self.DATA_LIST[self.rec_num].SSPIB == None:  # 8
                self.comboBox_SSPIB.setEditText("")
            else:
                self.comboBox_SSPIB.setEditText(str(self.DATA_LIST[self.rec_num].SSPIB))

            if self.DATA_LIST[
                self.rec_num].SSPIC == None:  # 9
                self.comboBox_SSPIC.setEditText("")
            else:
                self.comboBox_SSPIC.setEditText(str(self.DATA_LIST[self.rec_num].SSPIC))

            if self.DATA_LIST[self.rec_num].SSPID == None:  # 10
                self.comboBox_SSPID.setEditText("")
            else:
                self.comboBox_SSPID.setEditText(str(self.DATA_LIST[self.rec_num].SSPID))

            if self.DATA_LIST[self.rec_num].sup_aur_min == None:  # 11
                self.lineEdit_sup_aur_min.setText("")
            else:
                self.lineEdit_sup_aur_min.setText(str(self.DATA_LIST[self.rec_num].sup_aur_min))

            if self.DATA_LIST[self.rec_num].sup_aur_max == None:  # 12
                self.lineEdit_sup_aur_max.setText("")
            else:
                self.lineEdit_sup_aur_max.setText(str(self.DATA_LIST[self.rec_num].sup_aur_max))

            if self.DATA_LIST[self.rec_num].sup_aur_min_2 == None:  # 13
                self.lineEdit_sup_aur_min_2.setText("")
            else:
                self.lineEdit_sup_aur_min_2.setText(str(self.DATA_LIST[self.rec_num].sup_aur_min_2))

            if self.DATA_LIST[self.rec_num].sup_aur_max_2 == None:  # 14
                self.lineEdit_sup_aur_max_2.setText("")
            else:
                self.lineEdit_sup_aur_max_2.setText(str(self.DATA_LIST[self.rec_num].sup_aur_max_2))

            if self.DATA_LIST[self.rec_num].ms_sup_min == None:  # 15
                self.lineEdit_ms_sup_min.setText("")
            else:
                self.lineEdit_ms_sup_min.setText(str(self.DATA_LIST[self.rec_num].ms_sup_min))

            if self.DATA_LIST[self.rec_num].ms_sup_max == None:  # 16
                self.lineEdit_ms_sup_max.setText("")
            else:
                self.lineEdit_ms_sup_max.setText(str(self.DATA_LIST[self.rec_num].ms_sup_max))

            if self.DATA_LIST[self.rec_num].ms_inf_min == None:  # 17
                self.lineEdit_ms_inf_min.setText("")
            else:
                self.lineEdit_ms_inf_min.setText(str(self.DATA_LIST[self.rec_num].ms_inf_min))

            if self.DATA_LIST[self.rec_num].ms_inf_max == None:  # 18
                self.lineEdit_ms_inf_max.setText("")
            else:
                self.lineEdit_ms_inf_max.setText(str(self.DATA_LIST[self.rec_num].ms_inf_max))

            if self.DATA_LIST[self.rec_num].usura_min == None:  # 19
                self.lineEdit_usura_min.setText("")
            else:
                self.lineEdit_usura_min.setText(str(self.DATA_LIST[self.rec_num].usura_min))

            if self.DATA_LIST[self.rec_num].usura_max == None:  # 20
                self.lineEdit_usura_max.setText("")
            else:
                self.lineEdit_usura_max.setText(str(self.DATA_LIST[self.rec_num].usura_max))

            if self.DATA_LIST[self.rec_num].Id_endo == None:  # 21
                self.comboBox_Id_endo.setEditText("")
            else:
                self.comboBox_Id_endo.setEditText(str(self.DATA_LIST[self.rec_num].Id_endo))

            if self.DATA_LIST[self.rec_num].Is_endo == None:  # 22
                self.comboBox_Is_endo.setEditText("")
            else:
                self.comboBox_Is_endo.setEditText(str(self.DATA_LIST[self.rec_num].Is_endo))

            if self.DATA_LIST[self.rec_num].IId_endo == None:  # 23
                self.comboBox_IId_endo.setEditText("")
            else:
                self.comboBox_IId_endo.setEditText(str(self.DATA_LIST[self.rec_num].IId_endo))

            if self.DATA_LIST[self.rec_num].IIs_endo == None:  # 24
                self.comboBox_IIs_endo.setEditText("")
            else:
                self.comboBox_IIs_endo.setEditText(str(self.DATA_LIST[self.rec_num].IIs_endo))

            if self.DATA_LIST[self.rec_num].IIId_endo == None:  # 25
                self.comboBox_IIId_endo.setEditText("")
            else:
                self.comboBox_IIId_endo.setEditText(str(self.DATA_LIST[self.rec_num].IIId_endo))

            if self.DATA_LIST[self.rec_num].IIIs_endo == None:  # 26
                self.comboBox_IIIs_endo.setEditText("")
            else:
                self.comboBox_IIIs_endo.setEditText(str(self.DATA_LIST[self.rec_num].IIIs_endo))

            if self.DATA_LIST[self.rec_num].IV_endo == None:  # 27
                self.comboBox_IV_endo.setEditText("")
            else:
                self.comboBox_IV_endo.setEditText(str(self.DATA_LIST[self.rec_num].IV_endo))

            if self.DATA_LIST[self.rec_num].V_endo == None:  # 28
                self.comboBox_V_endo.setEditText("")
            else:
                self.comboBox_V_endo.setEditText(str(self.DATA_LIST[self.rec_num].V_endo))

            if self.DATA_LIST[self.rec_num].VI_endo == None:  # 29
                self.comboBox_VI_endo.setEditText("")
            else:
                self.comboBox_VI_endo.setEditText(str(self.DATA_LIST[self.rec_num].VI_endo))

            if self.DATA_LIST[self.rec_num].VII_endo == None:  # 30
                self.comboBox_VII_endo.setEditText("")
            else:
                self.comboBox_VII_endo.setEditText(str(self.DATA_LIST[self.rec_num].VII_endo))

            if self.DATA_LIST[self.rec_num].VIIId_endo == None:  # 31
                self.comboBox_VIIId_endo.setEditText("")
            else:
                self.comboBox_VIIId_endo.setEditText(str(self.DATA_LIST[self.rec_num].VIIId_endo))

            if self.DATA_LIST[self.rec_num].VIIIs_endo == None:  # 32
                self.comboBox_VIIIs_endo.setEditText("")
            else:
                self.comboBox_VIIIs_endo.setEditText(str(self.DATA_LIST[self.rec_num].VIIIs_endo))

            if self.DATA_LIST[self.rec_num].IXd_endo == None:  # 33
                self.comboBox_IXd_endo.setEditText("")
            else:
                self.comboBox_IXd_endo.setEditText(str(self.DATA_LIST[self.rec_num].IXd_endo))

            if self.DATA_LIST[self.rec_num].IXs_endo == None:  # 34
                self.comboBox_IXs_endo.setEditText("")
            else:
                self.comboBox_IXs_endo.setEditText(str(self.DATA_LIST[self.rec_num].IXs_endo))

            if self.DATA_LIST[self.rec_num].Xd_endo == None:  # 35
                self.comboBox_Xd_endo.setEditText("")
            else:
                self.comboBox_Xd_endo.setEditText(str(self.DATA_LIST[self.rec_num].Xd_endo))

            if self.DATA_LIST[self.rec_num].Xs_endo == None:  # 36
                self.comboBox_Xs_endo.setEditText("")
            else:
                self.comboBox_Xs_endo.setEditText(str(self.DATA_LIST[self.rec_num].Xs_endo))

            if self.DATA_LIST[self.rec_num].endo_min == None:  # 37
                self.lineEdit_endo_min.setText("")
            else:
                self.lineEdit_endo_min.setText(str(self.DATA_LIST[self.rec_num].endo_min))

            if self.DATA_LIST[self.rec_num].endo_max == None:  # 38
                self.lineEdit_endo_max.setText("")
            else:
                self.lineEdit_endo_max.setText(str(self.DATA_LIST[self.rec_num].endo_max))

            if self.DATA_LIST[self.rec_num].volta_1 == None:  # 39
                self.comboBox_volta_1.setEditText("")
            else:
                self.comboBox_volta_1.setEditText(str(self.DATA_LIST[self.rec_num].volta_1))

            if self.DATA_LIST[self.rec_num].volta_2 == None:  # 40
                self.comboBox_volta_2.setEditText("")
            else:
                self.comboBox_volta_2.setEditText(str(self.DATA_LIST[self.rec_num].volta_2))

            if self.DATA_LIST[
                self.rec_num].volta_3 == None:  # 41
                self.comboBox_volta_3.setEditText("")
            else:
                self.comboBox_volta_3.setEditText(str(self.DATA_LIST[self.rec_num].volta_3))

            if self.DATA_LIST[self.rec_num].volta_4 == None:  # 42
                self.comboBox_volta_4.setEditText("")
            else:
                self.comboBox_volta_4.setEditText(str(self.DATA_LIST[self.rec_num].volta_4))

            if self.DATA_LIST[self.rec_num].volta_5 == None:  # 43
                self.comboBox_volta_5.setEditText("")
            else:
                self.comboBox_volta_5.setEditText(str(self.DATA_LIST[self.rec_num].volta_5))

            if self.DATA_LIST[self.rec_num].volta_6 == None:  # 44
                self.comboBox_volta_6.setEditText("")
            else:
                self.comboBox_volta_6.setEditText(str(self.DATA_LIST[self.rec_num].volta_6))

            if self.DATA_LIST[self.rec_num].volta_7 == None:  # 45
                self.comboBox_volta_7.setEditText("")
            else:
                self.comboBox_volta_7.setEditText(str(self.DATA_LIST[self.rec_num].volta_7))

            if self.DATA_LIST[self.rec_num].lat_6 == None:  # 46
                self.comboBox_lat_6.setEditText("")
            else:
                self.comboBox_lat_6.setEditText(str(self.DATA_LIST[self.rec_num].lat_6))

            if self.DATA_LIST[self.rec_num].lat_7 == None:  # 47
                self.comboBox_lat_7.setEditText("")
            else:
                self.comboBox_lat_7.setEditText(str(self.DATA_LIST[self.rec_num].lat_7))

            if self.DATA_LIST[self.rec_num].lat_8 == None:  # 48
                self.comboBox_lat_8.setEditText("")
            else:
                self.comboBox_lat_8.setEditText(str(self.DATA_LIST[self.rec_num].lat_8))

            if self.DATA_LIST[self.rec_num].lat_9 == None:  # 49
                self.comboBox_lat_9.setEditText("")
            else:
                self.comboBox_lat_9.setEditText(str(self.DATA_LIST[self.rec_num].lat_9))

            if self.DATA_LIST[self.rec_num].lat_10 == None:  # 50
                self.comboBox_lat_10.setEditText("")
            else:
                self.comboBox_lat_10.setEditText(str(self.DATA_LIST[self.rec_num].lat_10))

            if self.DATA_LIST[self.rec_num].volta_min == None:  # 51
                self.lineEdit_volta_min.setText("")
            else:
                self.lineEdit_volta_min.setText(str(self.DATA_LIST[self.rec_num].volta_min))

            if self.DATA_LIST[self.rec_num].volta_max == None:  # 52
                self.lineEdit_volta_max.setText("")
            else:
                self.lineEdit_volta_max.setText(str(self.DATA_LIST[self.rec_num].volta_max))

            if self.DATA_LIST[self.rec_num].ant_lat_min == None:  # 53
                self.lineEdit_ant_lat_min.setText("")
            else:
                self.lineEdit_ant_lat_min.setText(str(self.DATA_LIST[self.rec_num].ant_lat_min))

            if self.DATA_LIST[self.rec_num].ant_lat_max == None:  # 54
                self.lineEdit_ant_lat_max.setText("")
            else:
                self.lineEdit_ant_lat_max.setText(str(self.DATA_LIST[self.rec_num].ant_lat_max))

            if self.DATA_LIST[self.rec_num].ecto_min == None:  # 55
                self.lineEdit_ecto_min.setText("")
            else:
                self.lineEdit_ecto_min.setText(str(self.DATA_LIST[self.rec_num].ecto_min))

            if self.DATA_LIST[self.rec_num].ecto_max == None:  # 56
                self.lineEdit_ecto_max.setText("")
            else:
                self.lineEdit_ecto_max.setText(str(self.DATA_LIST[self.rec_num].ecto_max))

            """
            if self.toolButtonPreview.isChecked() == True:
                self.loadMapPreview()
            """

        except :
            pass#QMessageBox.warning(self, "Error", str(e), QMessageBox.Ok)

    def set_rec_counter(self, t, c):
        self.rec_tot = t
        self.rec_corr = c
        self.label_rec_tot.setText(str(self.rec_tot))
        self.label_rec_corrente.setText(str(self.rec_corr))

    def set_LIST_REC_TEMP(self):
        if self.lineEdit_sinf_min.text() == "":
            sinf_min = None
        else:
            sinf_min = str(self.lineEdit_sinf_min.text())

        if self.lineEdit_sinf_max.text() == "":
            sinf_max = None
        else:
            sinf_max = str(self.lineEdit_sinf_max.text())

        if self.lineEdit_sinf_min_2.text() == "":
            sinf_min_2 = None
        else:
            sinf_min_2 = str(self.lineEdit_sinf_min_2.text())

        if self.lineEdit_sinf_max_2.text() == "":
            sinf_max_2 = None
        else:
            sinf_max_2 = str(self.lineEdit_sinf_max_2.text())

        if self.comboBox_SSPIA.currentText() == "":
            SSPIA = None
        else:
            SSPIA = str(self.comboBox_SSPIA.currentText())

        if self.comboBox_SSPIB.currentText() == "":
            SSPIB = None
        else:
            SSPIB = str(self.comboBox_SSPIB.currentText())

        if self.comboBox_SSPIC.currentText() == "":
            SSPIC = None
        else:
            SSPIC = str(self.comboBox_SSPIC.currentText())

        if self.comboBox_SSPID.currentText() == "":
            SSPID = None
        else:
            SSPID = str(self.comboBox_SSPID.currentText())

        if self.lineEdit_sup_aur_min.text() == "":
            sup_aur_min = None
        else:
            sup_aur_min = str(self.lineEdit_sup_aur_min.text())

        if self.lineEdit_sup_aur_max.text() == "":
            sup_aur_max = None
        else:
            sup_aur_max = str(self.lineEdit_sup_aur_max.text())

        if self.lineEdit_sup_aur_min_2.text() == "":
            sup_aur_min_2 = None
        else:
            sup_aur_min_2 = str(self.lineEdit_sup_aur_min_2.text())

        if self.lineEdit_sup_aur_max_2.text() == "":
            sup_aur_max_2 = None
        else:
            sup_aur_max_2 = str(self.lineEdit_sup_aur_max_2.text())

        if self.lineEdit_ms_sup_min.text() == "":
            ms_sup_min = None
        else:
            ms_sup_min = str(self.lineEdit_ms_sup_min.text())

        if self.lineEdit_ms_sup_max.text() == "":
            ms_sup_max = None
        else:
            ms_sup_max = str(self.lineEdit_ms_sup_max.text())

        if self.lineEdit_ms_inf_min.text() == "":
            ms_inf_min = None
        else:
            ms_inf_min = str(self.lineEdit_ms_inf_min.text())

        if self.lineEdit_ms_inf_max.text() == "":
            ms_inf_max = None
        else:
            ms_inf_max = str(self.lineEdit_ms_inf_max.text())

        if self.lineEdit_usura_min.text() == "":
            usura_min = None
        else:
            usura_min = str(self.lineEdit_usura_min.text())

        if self.lineEdit_usura_max.text() == "":
            usura_max = None
        else:
            usura_max = str(self.lineEdit_usura_max.text())

        if self.comboBox_Id_endo.currentText() == "":
            Id_endo = None
        else:
            Id_endo = str(self.comboBox_Id_endo.currentText())

        if self.comboBox_Is_endo.currentText() == "":
            Is_endo = None
        else:
            Is_endo = str(self.comboBox_Is_endo.currentText())

        if self.comboBox_IId_endo.currentText() == "":
            IId_endo = None
        else:
            IId_endo = str(self.comboBox_IId_endo.currentText())

        if self.comboBox_IIs_endo.currentText() == "":
            IIs_endo = None
        else:
            IIs_endo = str(self.comboBox_IIs_endo.currentText())

        if self.comboBox_IIId_endo.currentText() == "":
            IIId_endo = None
        else:
            IIId_endo = str(self.comboBox_IIId_endo.currentText())

        if self.comboBox_IIIs_endo.currentText() == "":
            IIIs_endo = None
        else:
            IIIs_endo = str(self.comboBox_IIIs_endo.currentText())

        if self.comboBox_IV_endo.currentText() == "":
            IV_endo = None
        else:
            IV_endo = str(self.comboBox_IV_endo.currentText())

        if self.comboBox_V_endo.currentText() == "":
            V_endo = None
        else:
            V_endo = str(self.comboBox_V_endo.currentText())

        if self.comboBox_VI_endo.currentText() == "":
            VI_endo = None
        else:
            VI_endo = str(self.comboBox_VI_endo.currentText())

        if self.comboBox_VII_endo.currentText() == "":
            VII_endo = None
        else:
            VII_endo = str(self.comboBox_VII_endo.currentText())

        if self.comboBox_VIIId_endo.currentText() == "":
            VIIId_endo = None
        else:
            VIIId_endo = str(self.comboBox_VIIId_endo.currentText())

        if self.comboBox_VIIIs_endo.currentText() == "":
            VIIIs_endo = None
        else:
            VIIIs_endo = str(self.comboBox_VIIIs_endo.currentText())

        if self.comboBox_IXd_endo.currentText() == "":
            IXd_endo = None
        else:
            IXd_endo = str(self.comboBox_IXd_endo.currentText())

        if self.comboBox_IXs_endo.currentText() == "":
            IXs_endo = None
        else:
            IXs_endo = str(self.comboBox_IXs_endo.currentText())

        if self.comboBox_Xd_endo.currentText() == "":
            Xd_endo = None
        else:
            Xd_endo = str(self.comboBox_Xd_endo.currentText())

        if self.comboBox_Xs_endo.currentText() == "":
            Xs_endo = None
        else:
            Xs_endo = str(self.comboBox_Xs_endo.currentText())

        if self.lineEdit_endo_min.text() == "":
            endo_min = None
        else:
            endo_min = str(self.lineEdit_endo_min.text())

        if self.lineEdit_endo_max.text() == "":
            endo_max = None
        else:
            endo_max = str(self.lineEdit_endo_max.text())

        if self.comboBox_volta_1.currentText() == "":
            volta_1 = None
        else:
            volta_1 = str(self.comboBox_volta_1.currentText())

        if self.comboBox_volta_2.currentText() == "":
            volta_2 = None
        else:
            volta_2 = str(self.comboBox_volta_2.currentText())

        if self.comboBox_volta_3.currentText() == "":
            volta_3 = None
        else:
            volta_3 = str(self.comboBox_volta_3.currentText())

        if self.comboBox_volta_4.currentText() == "":
            volta_4 = None
        else:
            volta_4 = str(self.comboBox_volta_4.currentText())

        if self.comboBox_volta_5.currentText() == "":
            volta_5 = None
        else:
            volta_5 = str(self.comboBox_volta_5.currentText())

        if self.comboBox_volta_6.currentText() == "":
            volta_6 = None
        else:
            volta_6 = str(self.comboBox_volta_6.currentText())

        if self.comboBox_volta_7.currentText() == "":
            volta_7 = None
        else:
            volta_7 = str(self.comboBox_volta_7.currentText())

        if self.comboBox_lat_6.currentText() == "":
            lat_6 = None
        else:
            lat_6 = str(self.comboBox_lat_6.currentText())

        if self.comboBox_lat_7.currentText() == "":
            lat_7 = None
        else:
            lat_7 = str(self.comboBox_lat_7.currentText())

        if self.comboBox_lat_8.currentText() == "":
            lat_8 = None
        else:
            lat_8 = str(self.comboBox_lat_8.currentText())

        if self.comboBox_lat_9.currentText() == "":
            lat_9 = None
        else:
            lat_9 = str(self.comboBox_lat_9.currentText())

        if self.comboBox_lat_10.currentText() == "":
            lat_10 = None
        else:
            lat_10 = str(self.comboBox_lat_10.currentText())

        if self.lineEdit_volta_min.text() == "":
            volta_min = None
        else:
            volta_min = str(self.lineEdit_volta_min.text())

        if self.lineEdit_volta_max.text() == "":
            volta_max = None
        else:
            volta_max = str(self.lineEdit_volta_max.text())

        if self.lineEdit_ant_lat_min.text() == "":
            ant_lat_min = None
        else:
            ant_lat_min = str(self.lineEdit_ant_lat_min.text())

        if self.lineEdit_ant_lat_max.text() == "":
            ant_lat_max = None
        else:
            ant_lat_max = str(self.lineEdit_ant_lat_max.text())

        if self.lineEdit_ecto_min.text() == "":
            ecto_min = None
        else:
            ecto_min = str(self.lineEdit_ecto_min.text())

        if self.lineEdit_ecto_max.text() == "":
            ecto_max = None
        else:
            ecto_max = str(self.lineEdit_ecto_max.text())

            # data
        self.DATA_LIST_REC_TEMP = [
            str(self.comboBox_sito.currentText()),  # 1 - Sito
            str(self.lineEdit_nr_individuo.text()),  # 2 - Num individuo
            str(sinf_min),  # 11 - Sinfisi pubica tot
            str(sinf_max),  # 12 - Sinfisi pubica tot
            str(sinf_min_2),  # 11 - Sinfisi pubica tot
            str(sinf_max_2),  # 12 - Sinfisi pubica tot
            str(SSPIA),  # 13 - SSPIA età
            str(SSPIB),  # 14 - SSPIB età
            str(SSPIC),  # 15 - SSPIC età
            str(SSPID),  # 16 - SSPID età
            str(sup_aur_min),  # 18 - Mascellare superiore tot
            str(sup_aur_max),  # 19 - Mascellare inferiore tot
            str(sup_aur_min_2),  # 18 - Mascellare superiore tot
            str(sup_aur_max_2),  # 19 - Mascellare inferiore tot
            str(ms_sup_min),  # 28 - Usura dentaria tot
            str(ms_sup_max),  # 29 - Usura dentaria tot
            str(ms_inf_min),  # 39 - Usura dentaria tot
            str(ms_inf_max),  # 40 - Usura dentaria tot
            str(usura_min),  # 41 - Usura dentaria tot
            str(usura_max),  # 42 - Usura dentaria tot
            str(Id_endo),  # 43 - 1d suture endocraniche
            str(Is_endo),  # 44 - 1s suture endocraniche
            str(IId_endo),  # 45 - 2d suture endocraniche
            str(IIs_endo),  # 46 - 2s suture endocraniche
            str(IIId_endo),  # 47 - 3d suture endocraniche
            str(IIIs_endo),  # 48 - 3s suture endocraniche
            str(IV_endo),  # 49 - 4 suture endocraniche
            str(V_endo),  # 50 - 5 suture endocraniche
            str(VI_endo),  # 51 - 6 suture endocraniche
            str(VII_endo),  # 52 - 7 suture endocraniche
            str(VIIId_endo),  # 53 - 8d suture endocraniche
            str(VIIIs_endo),  # 54 - 8s suture endocraniche
            str(IXd_endo),  # 55 - 9d suture endocraniche
            str(IXs_endo),  # 56 - 9s suture endocraniche
            str(Xd_endo),  # 57 - 10d suture endocraniche
            str(Xs_endo),  # 58 - 10s suture endocraniche
            str(endo_min),  # 59 - Range suture endocraniche
            str(endo_max),  # 60 - Range suture endocraniche
            str(volta_1),  # 61 - Suture volta 1
            str(volta_2),  # 62 - Suture volta 2
            str(volta_3),  # 63 - Suture volta 3
            str(volta_4),  # 64 - Suture volta 4
            str(volta_5),  # 65 - Suture volta 5
            str(volta_6),  # 66 - Suture volta 6
            str(volta_7),  # 67 - Suture volta 7
            str(lat_6),  # 68 - Suture antero laterali 6
            str(lat_7),  # 69 - Suture antero laterali 7
            str(lat_8),  # 70 - Suture antero laterali 8
            str(lat_9),  # 71 - Suture antero laterali 9
            str(lat_10),  # 72 - Suture antero laterali 10
            str(volta_min),  # 73 - Arco composito sesso
            str(volta_max),  # 74 - Ramo ischio pubico I
            str(ant_lat_min),  # 75 - Ramo ischio pubico I
            str(ant_lat_max),  # 76 - Ramo ischio pubico I
            str(ecto_min),  # 77 - Ramo ischio pubico I
            str(ecto_max)]  # 78 - Ramo ischio pubico I

    def set_LIST_REC_CORR(self):
        self.DATA_LIST_REC_CORR = []
        for i in self.TABLE_FIELDS:
            self.DATA_LIST_REC_CORR.append(eval("str(self.DATA_LIST[self.REC_CORR]." + i + ")"))

    def records_equal_check(self):
        self.set_LIST_REC_TEMP()
        self.set_LIST_REC_CORR()
        # f = open('/test_rec_corr.txt', 'w')
        # test = str(self.DATA_LIST_REC_CORR) + " " + str(self.DATA_LIST_REC_TEMP)
        # f.write(test)
        # f.close()

        if self.DATA_LIST_REC_CORR == self.DATA_LIST_REC_TEMP:
            return 0
        else:
            return 1

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

    def rec_toupdate(self):
        rec_to_update = self.UTILITY.pos_none_in_list(self.DATA_LIST_REC_TEMP)
        return rec_to_update

    def charge_id_us_for_individuo(self):
        data_list_us = []
        for rec in range(len(self.DATA_LIST)):
            sito = "'" + str(self.DATA_LIST[rec].sito) + "'"
            us = int(self.DATA_LIST[rec].us)

            serch_dict_us = {'sito': sito, 'area': area, 'us': us}
            us_ind = self.DB_MANAGER.query_bool(serch_dict_us, "US")
            data_list_us.append(us_ind)

        data_list_id_us = []
        for us in range(len(data_list_us)):
            data_list_id_us.append(data_list_us[us][0].id_us)

        return data_list_id_us

    def on_pushButton_openSinfisi_pubica_pressed(self):
        # apre la tabella di determinazione dell'eta in base al sesso ricavato dalla scheda individuo
        query_res = self.sex_from_individuo_table()
        if not bool(query_res):
            QMessageBox.warning(self, "Errore",
                                "Crea prima la scheda individuo e segnala il sesso per poter utilizzare la determinazione dell'eta' in base alla sinfisi pubica",
                                QMessageBox.Ok)
        else:
            sesso = query_res[0].sesso
            if sesso == "Maschio":
                self.open_tables_det_eta(2)
            elif sesso == "Femmina":
                self.open_tables_det_eta(1)
            else:
                QMessageBox.warning(self, "Errore", "Tipo di sesso: " + str(
                    sesso) + "\nNon e' possibile stimare l'eta' di morte in base alla sinfisi pubica", QMessageBox.Ok)

    def on_pushButton_openSinfisi_pubica_2_pressed(self):
        # apre la tabella di determinazione dell'eta in base al sesso ricavato dalla scheda individuo
        query_res = self.sex_from_individuo_table()
        if not bool(query_res):
            QMessageBox.warning(self, "Errore",
                                "Crea prima la scheda individuo e segnala il sesso per poter utilizzare la determinazione dell'eta' in base alla sinfisi pubica",
                                QMessageBox.Ok)
        else:
            sesso = query_res[0].sesso
            if sesso == "Maschio":
                self.open_tables_det_eta(4)
            elif sesso == "Femmina":
                self.open_tables_det_eta(3)
            else:
                QMessageBox.warning(self, "Errore", "Tipo di sesso: " + str(
                    sesso) + "\nNon e' possibile stimare l'eta' di morte in base alla sinfisi pubica", QMessageBox.Ok)

    def sex_from_individuo_table(self):
        # ricava il sesso dell'individuo segnalato nella scheda di individuo
        sito = str(self.comboBox_sito.currentText())
        nr_individuo = str(self.lineEdit_nr_individuo.text())

        # lista definizione_stratigrafica
        search_dict = {
            'sito': "'" + sito + "'",
            'nr_individuo': "'" + nr_individuo + "'"
        }
        query_res = self.DB_MANAGER.query_bool(search_dict, 'SCHEDAIND')

        return query_res

    def on_pushButton_SSPIA_pressed(self):
        self.open_tables_det_eta(5)

    def on_pushButton_SSPIB_pressed(self):
        self.open_tables_det_eta(6)

    def on_pushButton_SSPIC_pressed(self):
        self.open_tables_det_eta(7)

    def on_pushButton_SSPID_pressed(self):
        self.open_tables_det_eta(8)

    def on_pushButton_mascellare_superiore_pressed(self):
        self.open_tables_det_eta(9)

    def on_pushButton_mascellare_inferiore_pressed(self):
        self.open_tables_det_eta(10)

    def on_pushButton_suture_endocraniche_pressed(self):
        self.open_tables_det_eta(11)

    def on_pushButton_suture_ectocraniche_pressed(self):
        self.open_tables_det_eta(12)

        # PULSANTI IMMAGINI

    def open_tables_det_eta(self, n):
        # apre la finestra di visualizzazione delle immagini in base al valore n
        filepath = os.path.join(os.path.dirname(__file__), os.pardir)
        dlg = ImageViewer(self)

        if n == 1:  # tavola sinfisi pubica femmminile
            try:
                anthropo_images_path = '{}{}'.format(
                    filepath, os.path.join(os.sep, os.pardir, 'resources/anthropo_images/det_eta_sinfisi_pubica_femmine.jpg'))
                dlg.show_image(str(anthropo_images_path))  # item.data(QtCore.Qt.UserRole).toString()))
                dlg.exec_()
            except Exception as e:
                QMessageBox.warning(self, "Error",  "Warning1 file: " + str(e), QMessageBox.Ok)

        if n == 2:  # tavola sinfisi pubica maschile
            try:
                anthropo_images_path = '{}{}'.format(
                    filepath, os.path.join(os.sep, os.pardir, 'resources/anthropo_images/det_eta_sinfisi_pubica_maschi.jpg'))
                dlg.show_image(str(anthropo_images_path))  # item.data(QtCore.Qt.UserRole).toString()))
                dlg.exec_()
            except Exception as e:
                QMessageBox.warning(self, "Error",  "Warning1 file: " + str(e), QMessageBox.Ok)

        if n == 3:  # tavola sinfisi pubica femmminile Kimmerle
            try:
                anthropo_images_path = '{}{}'.format(
                    filepath, os.path.join(os.sep, os.pardir, 'resources/anthropo_images/det_eta_Kimmerle_femmine.jpg'))
                dlg.show_image(str(anthropo_images_path))  # item.data(QtCore.Qt.UserRole).toString()))
                dlg.exec_()
            except Exception as e:
                QMessageBox.warning(self, "Error",  "Warning1 file: " + str(e), QMessageBox.Ok)

        if n == 4:  # tavola sinfisi pubica maschi Kimmerle
            try:
                anthropo_images_path = '{}{}'.format(
                    filepath, os.path.join(os.sep, os.pardir, 'resources/anthropo_images/det_eta_Kimmerle_maschi.jpg'))
                dlg.show_image(str(anthropo_images_path))  # item.data(QtCore.Qt.UserRole).toString()))
                dlg.exec_()
            except Exception as e:
                QMessageBox.warning(self, "Error",  "Warning1 file: " + str(e), QMessageBox.Ok)

        if n == 5:  # tavola superficie auricolare SSPIA
            try:
                anthropo_images_path = '{}{}'.format(filepath, os.path.join(os.sep, os.pardir, 'resources/anthropo_images/deteta_SSPIA.jpg'))
                dlg.show_image(str(anthropo_images_path))  # item.data(QtCore.Qt.UserRole).toString()))
                dlg.exec_()
            except Exception as e:
                QMessageBox.warning(self, "Error",  "Warning1 file: " + str(e), QMessageBox.Ok)

        if n == 6:  # tavola superficie auricolare SSPIB
            try:
                anthropo_images_path = '{}{}'.format(filepath, os.path.join(os.sep, os.pardir, 'resources/anthropo_images/deteta_SSPIB.jpg'))
                dlg.show_image(str(anthropo_images_path))  # item.data(QtCore.Qt.UserRole).toString()))
                dlg.exec_()
            except Exception as e:
                QMessageBox.warning(self, "Error",  "Warning1 file: " + str(e), QMessageBox.Ok)

        if n == 7:  # tavola superficie auricolare SSPIC
            try:
                anthropo_images_path = '{}{}'.format(filepath, os.path.join(os.sep, os.pardir, 'resources/anthropo_images/deteta_SSPIC.jpg'))
                dlg.show_image(str(anthropo_images_path))  # item.data(QtCore.Qt.UserRole).toString()))
                dlg.exec_()
            except Exception as e:
                QMessageBox.warning(self, "Error",  "Warning1 file: " + str(e), QMessageBox.Ok)

        if n == 8:  # tavola superficie auricolare SSPID
            try:
                anthropo_images_path = '{}{}'.format(filepath, os.path.join(os.sep, os.pardir, 'resources/anthropo_images/deteta_SSPID.jpg'))
                dlg.show_image(str(anthropo_images_path))  # item.data(QtCore.Qt.UserRole).toString()))
                dlg.exec_()
            except Exception as e:
                QMessageBox.warning(self, "Error",  "Warning1 file: " + str(e), QMessageBox.Ok)

        if n == 9:  # tavola usura dentaria mascellare superiore
            try:
                anthropo_images_path = '{}{}'.format(
                    filepath, os.path.join(os.sep, os.pardir, 'resources/anthropo_images/deteta_usura_masc_superiore.jpg'))
                dlg.show_image(str(anthropo_images_path))  # item.data(QtCore.Qt.UserRole).toString()))
                dlg.exec_()
            except Exception as e:
                QMessageBox.warning(self, "Error",  "Warning1 file: " + str(e), QMessageBox.Ok)

        if n == 10:  # tavola usura dentaria mascellare inferiore
            try:
                anthropo_images_path = '{}{}'.format(
                    filepath, os.path.join(os.sep, os.pardir, 'resources/anthropo_images/deteta_usura_masc_inferiore.jpg'))
                dlg.show_image(str(anthropo_images_path))  # item.data(QtCore.Qt.UserRole).toString()))
                dlg.exec_()
            except Exception as e:
                QMessageBox.warning(self, "Error",  "Warning1 file: " + str(e), QMessageBox.Ok)

        if n == 11:  # tavola suture endocraniche
            try:
                anthropo_images_path = '{}{}'.format(
                    filepath, os.path.join(os.sep, os.pardir, 'resources/anthropo_images/deteta_suture_endocraniche.jpg'))
                dlg.show_image(str(anthropo_images_path))  # item.data(QtCore.Qt.UserRole).toString()))
                dlg.exec_()
            except Exception as e:
                QMessageBox.warning(self, "Error",  "Warning1 file: " + str(e), QMessageBox.Ok)

        if n == 12:  # tavola suture ectocraniche
            try:
                anthropo_images_path = '{}{}'.format(
                    filepath, os.path.join(os.sep, os.pardir, 'resources/anthropo_images/deteta_suture_ectocraniche.jpg'))
                dlg.show_image(str(anthropo_images_path))  # item.data(QtCore.Qt.UserRole).toString()))
                dlg.exec_()
            except Exception as e:
                QMessageBox.warning(self, "Error",  "Warning1 file: " + str(e), QMessageBox.Ok)

    def on_pushButton_I_fase_pressed(self):
        query_res = self.sex_from_individuo_table()
        if not bool(query_res):
            QMessageBox.warning(self, "Errore",
                                "Crea prima la scheda individuo e segnala il sesso per poter utilizzare la determinazione dell'eta' in base alla sinfisi pubica",
                                QMessageBox.Ok)
        else:
            sesso = query_res[0].sesso
            if sesso == "Maschio":
                range_sex = self.DIZ_VALORI_SINFISI_MASCHIO_Suchey_Brooks[1]

            elif sesso == "Femmina":
                range_sex = self.DIZ_VALORI_SINFISI_FEMMINA_Suchey_Brooks[1]
            else:
                QMessageBox.warning(self, "Errore", "Tipo di sesso: " + str(
                    sesso) + "\nNon e' possibile stimare l'eta' di morte in base alla sinfisi pubica", QMessageBox.Ok)

            if bool(range_sex):
                val_min, val_max = range_sex[0], range_sex[1]
                self.lineEdit_sinf_min.setText(str(val_min))
                self.lineEdit_sinf_max.setText(str(val_max))
                self.on_pushButton_save_pressed()

    def on_pushButton_II_fase_pressed(self):
        query_res = self.sex_from_individuo_table()
        if not bool(query_res):
            QMessageBox.warning(self, "Errore",
                                "Crea prima la scheda individuo e segnala il sesso per poter utilizzare la determinazione dell'eta' in base alla sinfisi pubica",
                                QMessageBox.Ok)
        else:
            sesso = query_res[0].sesso
            if sesso == "Maschio":
                range_sex = self.DIZ_VALORI_SINFISI_MASCHIO_Suchey_Brooks[2]

            elif sesso == "Femmina":
                range_sex = self.DIZ_VALORI_SINFISI_FEMMINA_Suchey_Brooks[2]
            else:
                QMessageBox.warning(self, "Errore", "Tipo di sesso: " + str(
                    sesso) + "\nNon e' possibile stimare l'eta' di morte in base alla sinfisi pubica", QMessageBox.Ok)

            if bool(range_sex):
                val_min, val_max = range_sex[0], range_sex[1]
                self.lineEdit_sinf_min.setText(str(val_min))
                self.lineEdit_sinf_max.setText(str(val_max))
                self.on_pushButton_save_pressed()

    def on_pushButton_III_fase_pressed(self):
        query_res = self.sex_from_individuo_table()
        if not bool(query_res):
            QMessageBox.warning(self, "Errore",
                                "Crea prima la scheda individuo e segnala il sesso per poter utilizzare la determinazione dell'eta' in base alla sinfisi pubica",
                                QMessageBox.Ok)
        else:
            sesso = query_res[0].sesso
            if sesso == "Maschio":
                range_sex = self.DIZ_VALORI_SINFISI_MASCHIO_Suchey_Brooks[3]

            elif sesso == "Femmina":
                range_sex = self.DIZ_VALORI_SINFISI_FEMMINA_Suchey_Brooks[3]
            else:
                QMessageBox.warning(self, "Errore", "Tipo di sesso: " + str(
                    sesso) + "\nNon e' possibile stimare l'eta' di morte in base alla sinfisi pubica", QMessageBox.Ok)

            if bool(range_sex):
                val_min, val_max = range_sex[0], range_sex[1]
                self.lineEdit_sinf_min.setText(str(val_min))
                self.lineEdit_sinf_max.setText(str(val_max))
                self.on_pushButton_save_pressed()

    def on_pushButton_IV_fase_pressed(self):
        query_res = self.sex_from_individuo_table()
        if not bool(query_res):
            QMessageBox.warning(self, "Errore",
                                "Crea prima la scheda individuo e segnala il sesso per poter utilizzare la determinazione dell'eta' in base alla sinfisi pubica",
                                QMessageBox.Ok)
        else:
            sesso = query_res[0].sesso
            if sesso == "Maschio":
                range_sex = self.DIZ_VALORI_SINFISI_MASCHIO_Suchey_Brooks[4]

            elif sesso == "Femmina":
                range_sex = self.DIZ_VALORI_SINFISI_FEMMINA_Suchey_Brooks[4]
            else:
                QMessageBox.warning(self, "Errore", "Tipo di sesso: " + str(
                    sesso) + "\nNon e' possibile stimare l'eta' di morte in base alla sinfisi pubica", QMessageBox.Ok)

            if bool(range_sex):
                val_min, val_max = range_sex[0], range_sex[1]
                self.lineEdit_sinf_min.setText(str(val_min))
                self.lineEdit_sinf_max.setText(str(val_max))
                self.on_pushButton_save_pressed()

    def on_pushButton_V_fase_pressed(self):
        query_res = self.sex_from_individuo_table()
        if not bool(query_res):
            QMessageBox.warning(self, "Errore",
                                "Crea prima la scheda individuo e segnala il sesso per poter utilizzare la determinazione dell'eta' in base alla sinfisi pubica",
                                QMessageBox.Ok)
        else:
            sesso = query_res[0].sesso
            if sesso == "Maschio":
                range_sex = self.DIZ_VALORI_SINFISI_MASCHIO_Suchey_Brooks[5]

            elif sesso == "Femmina":
                range_sex = self.DIZ_VALORI_SINFISI_FEMMINA_Suchey_Brooks[5]
            else:
                QMessageBox.warning(self, "Errore", "Tipo di sesso: " + str(
                    sesso) + "\nNon e' possibile stimare l'eta' di morte in base alla sinfisi pubica", QMessageBox.Ok)

            if bool(range_sex):
                val_min, val_max = range_sex[0], range_sex[1]
                self.lineEdit_sinf_min.setText(str(val_min))
                self.lineEdit_sinf_max.setText(str(val_max))
                self.on_pushButton_save_pressed()

    def on_pushButton_VI_fase_pressed(self):
        query_res = self.sex_from_individuo_table()
        if not bool(query_res):
            QMessageBox.warning(self, "Errore",
                                "Crea prima la scheda individuo e segnala il sesso per poter utilizzare la determinazione dell'eta' in base alla sinfisi pubica",
                                QMessageBox.Ok)
        else:
            sesso = query_res[0].sesso
            if sesso == "Maschio":
                range_sex = self.DIZ_VALORI_SINFISI_MASCHIO_Suchey_Brooks[6]

            elif sesso == "Femmina":
                range_sex = self.DIZ_VALORI_SINFISI_FEMMINA_Suchey_Brooks[6]
            else:
                QMessageBox.warning(self, "Errore", "Tipo di sesso: " + str(
                    sesso) + "\nNon e' possibile stimare l'eta' di morte in base alla sinfisi pubica", QMessageBox.Ok)

            if bool(range_sex):
                val_min, val_max = range_sex[0], range_sex[1]
                self.lineEdit_sinf_min.setText(str(val_min))
                self.lineEdit_sinf_max.setText(str(val_max))
                self.on_pushButton_save_pressed()

    def on_pushButton_f_1_pressed(self):
        range_sex = self.DIZ_VALORI_SINFISI_2_FEMMINA_Kimmerle[1]
        val_min, val_max = range_sex[0], range_sex[1]
        self.lineEdit_sinf_min_2.setText(str(val_min))
        self.lineEdit_sinf_max_2.setText(str(val_max))
        self.on_pushButton_save_pressed()

    def on_pushButton_f_2_pressed(self):
        range_sex = self.DIZ_VALORI_SINFISI_2_FEMMINA_Kimmerle[2]
        val_min, val_max = range_sex[0], range_sex[1]
        self.lineEdit_sinf_min_2.setText(str(val_min))
        self.lineEdit_sinf_max_2.setText(str(val_max))
        self.on_pushButton_save_pressed()

    def on_pushButton_f_3_pressed(self):
        range_sex = self.DIZ_VALORI_SINFISI_2_FEMMINA_Kimmerle[3]
        val_min, val_max = range_sex[0], range_sex[1]
        self.lineEdit_sinf_min_2.setText(str(val_min))
        self.lineEdit_sinf_max_2.setText(str(val_max))
        self.on_pushButton_save_pressed()

    def on_pushButton_f_4_pressed(self):
        range_sex = self.DIZ_VALORI_SINFISI_2_FEMMINA_Kimmerle[4]
        val_min, val_max = range_sex[0], range_sex[1]
        self.lineEdit_sinf_min_2.setText(str(val_min))
        self.lineEdit_sinf_max_2.setText(str(val_max))
        self.on_pushButton_save_pressed()

    def on_pushButton_f_5_pressed(self):
        range_sex = self.DIZ_VALORI_SINFISI_2_FEMMINA_Kimmerle[5]
        val_min, val_max = range_sex[0], range_sex[1]
        self.lineEdit_sinf_min_2.setText(str(val_min))
        self.lineEdit_sinf_max_2.setText(str(val_max))
        self.on_pushButton_save_pressed()

    def on_pushButton_f_6_pressed(self):
        range_sex = self.DIZ_VALORI_SINFISI_2_FEMMINA_Kimmerle[6]
        val_min, val_max = range_sex[0], range_sex[1]
        self.lineEdit_sinf_min_2.setText(str(val_min))
        self.lineEdit_sinf_max_2.setText(str(val_max))
        self.on_pushButton_save_pressed()

    def on_pushButton_f_7_pressed(self):
        range_sex = self.DIZ_VALORI_SINFISI_2_FEMMINA_Kimmerle[7]
        val_min, val_max = range_sex[0], range_sex[1]
        self.lineEdit_sinf_min_2.setText(str(val_min))
        self.lineEdit_sinf_max_2.setText(str(val_max))
        self.on_pushButton_save_pressed()

    def on_pushButton_f_8_pressed(self):
        range_sex = self.DIZ_VALORI_SINFISI_2_FEMMINA_Kimmerle[8]
        val_min, val_max = range_sex[0], range_sex[1]
        self.lineEdit_sinf_min_2.setText(str(val_min))
        self.lineEdit_sinf_max_2.setText(str(val_max))
        self.on_pushButton_save_pressed()

    def on_pushButton_sup_aur_pressed(self):
        lista_sup_aur = [int(self.comboBox_SSPIA.currentText()), int(self.comboBox_SSPIB.currentText()),
                         int(self.comboBox_SSPIC.currentText()), int(self.comboBox_SSPID.currentText())]
        # self.testing("/test_sup_aur.txt", str(lista_sup_aur))
        lista_sup_aur_str = str(lista_sup_aur)

        sup_aur_min, sup_aur_max = self.DIZ_VALORI_SUP_AUR[lista_sup_aur_str][0], \
                                   self.DIZ_VALORI_SUP_AUR[lista_sup_aur_str][1]
        sup_aur_min_2, sup_aur_max_2 = self.DIZ_VALORI_SUP_AUR_2[lista_sup_aur_str][0], \
                                       self.DIZ_VALORI_SUP_AUR_2[lista_sup_aur_str][1]

        self.lineEdit_sup_aur_min.setText(str(sup_aur_min))
        self.lineEdit_sup_aur_max.setText(str(sup_aur_max))
        self.lineEdit_sup_aur_min_2.setText(str(sup_aur_min_2))
        self.lineEdit_sup_aur_max_2.setText(str(sup_aur_max_2))
        self.on_pushButton_save_pressed()

    def on_pushButton_ms_sup_12_18_pressed(self):
        self.lineEdit_ms_sup_min.setText('12')
        self.lineEdit_ms_sup_max.setText('18')
        self.on_pushButton_save_pressed()

    def on_pushButton_ms_sup_16_20_pressed(self):
        self.lineEdit_ms_sup_min.setText('16')
        self.lineEdit_ms_sup_max.setText('20')
        self.on_pushButton_save_pressed()

    def on_pushButton_ms_sup_18_22_pressed(self):
        self.lineEdit_ms_sup_min.setText('18')
        self.lineEdit_ms_sup_max.setText('22')
        self.on_pushButton_save_pressed()

    def on_pushButton_ms_sup_20_24_pressed(self):
        self.lineEdit_ms_sup_min.setText('20')
        self.lineEdit_ms_sup_max.setText('24')
        self.on_pushButton_save_pressed()

    def on_pushButton_ms_sup_24_30_pressed(self):
        self.lineEdit_ms_sup_min.setText('24')
        self.lineEdit_ms_sup_max.setText('30')
        self.on_pushButton_save_pressed()

    def on_pushButton_ms_sup_30_35_pressed(self):
        self.lineEdit_ms_sup_min.setText('30')
        self.lineEdit_ms_sup_max.setText('35')
        self.on_pushButton_save_pressed()

    def on_pushButton_ms_sup_35_40_pressed(self):
        self.lineEdit_ms_sup_min.setText('35')
        self.lineEdit_ms_sup_max.setText('40')
        self.on_pushButton_save_pressed()

    def on_pushButton_ms_sup_40_50_pressed(self):
        self.lineEdit_ms_sup_min.setText('40')
        self.lineEdit_ms_sup_max.setText('50')
        self.on_pushButton_save_pressed()

    def on_pushButton_ms_inf_12_18_pressed(self):
        self.lineEdit_ms_inf_min.setText('12')
        self.lineEdit_ms_inf_max.setText('18')
        self.on_pushButton_save_pressed()

    def on_pushButton_ms_inf_16_20_pressed(self):
        self.lineEdit_ms_inf_min.setText('16')
        self.lineEdit_ms_inf_max.setText('20')
        self.on_pushButton_save_pressed()

    def on_pushButton_ms_inf_18_22_pressed(self):
        self.lineEdit_ms_inf_min.setText('18')
        self.lineEdit_ms_inf_max.setText('22')
        self.on_pushButton_save_pressed()

    def on_pushButton_ms_inf_20_24_pressed(self):
        self.lineEdit_ms_inf_min.setText('20')
        self.lineEdit_ms_inf_max.setText('24')
        self.on_pushButton_save_pressed()

    def on_pushButton_ms_inf_24_30_pressed(self):
        self.lineEdit_ms_inf_min.setText('24')
        self.lineEdit_ms_inf_max.setText('30')
        self.on_pushButton_save_pressed()

    def on_pushButton_ms_inf_30_35_pressed(self):
        self.lineEdit_ms_inf_min.setText('30')
        self.lineEdit_ms_inf_max.setText('35')
        self.on_pushButton_save_pressed()

    def on_pushButton_ms_inf_35_40_pressed(self):
        self.lineEdit_ms_inf_min.setText('35')
        self.lineEdit_ms_inf_max.setText('40')
        self.on_pushButton_save_pressed()

    def on_pushButton_ms_inf_40_45_pressed(self):
        self.lineEdit_ms_inf_min.setText('40')
        self.lineEdit_ms_inf_max.setText('45')
        self.on_pushButton_save_pressed()

    def on_pushButton_ms_inf_45_55_pressed(self):
        self.lineEdit_ms_inf_min.setText('45')
        self.lineEdit_ms_inf_max.setText('55')
        self.on_pushButton_save_pressed()

    def on_pushButton_range_sut_end_pressed(self):

        valore_dividendo = 0
        valore_divisore_media = 0

        if self.comboBox_Id_endo.currentText() != "":
            valore_dividendo += int(self.comboBox_Id_endo.currentText())
            valore_divisore_media += 1

        if self.comboBox_Is_endo.currentText() != "":
            valore_dividendo += int(self.comboBox_Is_endo.currentText())
            valore_divisore_media += 1

        if self.comboBox_IId_endo.currentText() != "":
            valore_dividendo += int(self.comboBox_IId_endo.currentText())
            valore_divisore_media += 1

        if self.comboBox_IIs_endo.currentText() != "":
            valore_dividendo += int(self.comboBox_IIs_endo.currentText())
            valore_divisore_media += 1

        if self.comboBox_IIId_endo.currentText() != "":
            valore_dividendo += int(self.comboBox_IIId_endo.currentText())
            valore_divisore_media += 1

        if self.comboBox_IIIs_endo.currentText() != "":
            valore_dividendo += int(self.comboBox_IIIs_endo.currentText())
            valore_divisore_media += 1

        if self.comboBox_IV_endo.currentText() != "":
            valore_dividendo += int(self.comboBox_IV_endo.currentText())
            valore_divisore_media += 1

        if self.comboBox_V_endo.currentText() != "":
            valore_dividendo += int(self.comboBox_V_endo.currentText())
            valore_divisore_media += 1

        if self.comboBox_VI_endo.currentText() != "":
            valore_dividendo += int(self.comboBox_VI_endo.currentText())
            valore_divisore_media += 1

        if self.comboBox_VII_endo.currentText() != "":
            valore_dividendo += int(self.comboBox_VII_endo.currentText())
            valore_divisore_media += 1

        if self.comboBox_VIIId_endo.currentText() != "":
            valore_dividendo += int(self.comboBox_VIIId_endo.currentText())
            valore_divisore_media += 1

        if self.comboBox_VIIIs_endo.currentText() != "":
            valore_dividendo += int(self.comboBox_VIIIs_endo.currentText())
            valore_divisore_media += 1

        if self.comboBox_IXd_endo.currentText() != "":
            valore_dividendo += int(self.comboBox_IXd_endo.currentText())
            valore_divisore_media += 1

        if self.comboBox_IXs_endo.currentText() != "":
            valore_dividendo += int(self.comboBox_IXs_endo.currentText())
            valore_divisore_media += 1

        if self.comboBox_Xd_endo.currentText() != "":
            valore_dividendo += int(self.comboBox_Xd_endo.currentText())
            valore_divisore_media += 1

        if self.comboBox_Xs_endo.currentText() != "":
            valore_dividendo += int(self.comboBox_Xs_endo.currentText())
            valore_divisore_media += 1

        range_eta = 0

        media = float(valore_dividendo) / float(valore_divisore_media)

        if 0.400 <= media <= 1.599:
            range_eta = (15, 40)
        elif 1.600 <= media <= 2.599:
            range_eta = (30, 60)
        elif 2.600 <= media <= 2.999:
            range_eta = (35, 65)
        elif 3.000 <= media <= 3.999:
            range_eta = (45, 75)
        elif media >= 4.000:
            range_eta = (50, 80)

        if range_eta == "non id.":
            self.lineEdit_endo_min.setText(range_eta)
            self.lineEdit_endo_max.setText(range_eta)
        else:
            self.lineEdit_endo_min.setText(str(range_eta[0]))
            self.lineEdit_endo_max.setText(str(range_eta[1]))
            self.lineEdit_valore_medio.setText(str(media))

        self.on_pushButton_save_pressed()

    def on_pushButton_calcola_volta_ant_lat_clicked(self):

        somma_volta = 0
        somma_ant_lat = 0

        if self.comboBox_volta_1.currentText() == "" and self.comboBox_volta_2.currentText() == "" and self.comboBox_volta_3.currentText() == "" and self.comboBox_volta_4.currentText() == "" and self.comboBox_volta_5.currentText() == "" and self.comboBox_volta_6.currentText() == "" and self.comboBox_volta_7.currentText() == "":

            self.lineEdit_volta_min.setText(str(""))
            self.lineEdit_volta_max.setText(str(""))
        else:
            if self.comboBox_volta_1.currentText() != "":
                somma_volta += int(self.comboBox_volta_1.currentText())

            if self.comboBox_volta_2.currentText() != "":
                somma_volta += int(self.comboBox_volta_2.currentText())

            if self.comboBox_volta_3.currentText() != "":
                somma_volta += int(self.comboBox_volta_3.currentText())

            if self.comboBox_volta_4.currentText() != "":
                somma_volta += int(self.comboBox_volta_4.currentText())

            if self.comboBox_volta_5.currentText() != "":
                somma_volta += int(self.comboBox_volta_5.currentText())

            if self.comboBox_volta_6.currentText() != "":
                somma_volta += int(self.comboBox_volta_6.currentText())

            if self.comboBox_volta_7.currentText() != "":
                somma_volta += int(self.comboBox_volta_7.currentText())

            if somma_volta == 0:
                range_eta_volta = (0, 35)
            elif somma_volta == 1 or somma_volta == 2:
                range_eta_volta = (19, 44)
            elif 3 <= somma_volta <= 6:
                range_eta_volta = (23, 45)
            elif 7 <= somma_volta <= 11:
                range_eta_volta = (28, 44)
            elif 12 <= somma_volta <= 15:
                range_eta_volta = (31, 65)
            elif 16 <= somma_volta <= 18:
                range_eta_volta = (35, 60)
            elif 19 <= somma_volta <= 20:
                range_eta_volta = (34, 63)
            elif somma_volta == 21:
                range_eta_volta = (43, 100)

            self.lineEdit_volta_min.setText(str(range_eta_volta[0]))
            self.lineEdit_volta_max.setText(str(range_eta_volta[1]))

        if self.comboBox_lat_6.currentText() == "" and self.comboBox_lat_7.currentText() == "" and self.comboBox_lat_8.currentText() == "" and self.comboBox_lat_9.currentText() == "" and self.comboBox_lat_10.currentText() == "":

            self.lineEdit_ant_lat_min.setText(str(""))
            self.lineEdit_ant_lat_max.setText(str(""))
        else:
            if self.comboBox_lat_6.currentText() != "":
                somma_ant_lat += int(self.comboBox_lat_6.currentText())

            if self.comboBox_lat_7.currentText() != "":
                somma_ant_lat += int(self.comboBox_lat_7.currentText())

            if self.comboBox_lat_8.currentText() != "":
                somma_ant_lat += int(self.comboBox_lat_8.currentText())

            if self.comboBox_lat_9.currentText() != "":
                somma_ant_lat += int(self.comboBox_lat_9.currentText())

            if self.comboBox_lat_10.currentText() != "":
                somma_ant_lat += int(self.comboBox_lat_10.currentText())

            if somma_ant_lat == 0:
                range_eta_ant_lat = (0, 43)
            elif somma_ant_lat == 1:
                range_eta_ant_lat = (21, 42)
            elif somma_ant_lat == 2:
                range_eta_ant_lat = (29, 44)
            elif 3 <= somma_ant_lat <= 5:
                range_eta_ant_lat = (28, 52)
            elif somma_ant_lat == 6:
                range_eta_ant_lat = (30, 54)
            elif somma_ant_lat == 7 or somma_ant_lat == 8:
                range_eta_ant_lat = (35, 57)
            elif somma_ant_lat == 9 or somma_ant_lat == 10:
                range_eta_ant_lat = (39, 69)
            elif 11 <= somma_ant_lat <= 14:
                range_eta_ant_lat = (49, 65)
            elif somma_ant_lat == 15:
                range_eta_ant_lat = ("", "")

            self.lineEdit_ant_lat_min.setText(str(range_eta_ant_lat[0]))
            self.lineEdit_ant_lat_max.setText(str(range_eta_ant_lat[1]))

        self.on_pushButton_save_pressed()

    def testing(self, name_file, message):
        f = open(str(name_file), 'w')
        f.write(str(message))
        f.close()

## Class end
