#! /usr/bin/env python
# -*- coding: utf 8 -*-
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
 *                                                                          *
 *   This program is free software; you can redistribute it and/or modify   *
 *   it under the terms of the GNU General Public License as published by   *
 *   the Free Software Foundation; either version 2 of the License, or      *
 *   (at your option) any later version.                                    *                                                                       *
 ***************************************************************************/
"""
from __future__ import absolute_import
from pathlib import Path
from builtins import range
from builtins import str
import psycopg2
import sqlite3  as sq
from sqlite3 import Error
import os
import sys
import subprocess
import platform
import time
import pandas as pd
import numpy as np
from pdf2docx import parse
from datetime import date
import xml.etree.ElementTree as ET
from lxml import etree
import cv2
from distutils.dir_util import copy_tree
from random import randrange as rand
from PyQt5 import QtCore, QtGui, QtWidgets
from qgis import processing
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import QColor, QIcon
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.uic import loadUiType
from qgis.core import *
from qgis.gui import QgsMapCanvas, QgsMapToolPan
from qgis.PyQt.QtSql import QSqlDatabase, QSqlTableModel
import re
from .Interactive_matrix import *
from ..modules.utility.pyarchinit_OS_utility import Pyarchinit_OS_Utility
from ..modules.db.pyarchinit_conn_strings import Connection
from ..modules.db.pyarchinit_db_manager import Pyarchinit_db_management
from ..modules.db.pyarchinit_utility import Utility
from ..modules.gis.pyarchinit_pyqgis import Pyarchinit_pyqgis, Order_layer_v2
from ..modules.utility.delegateComboBox import ComboBoxDelegate
from ..modules.utility.pyarchinit_error_check import Error_check
#from ..modules.utility.pyarchinit_exp_Periodosheet_pdf import generate_US_pdf
from ..modules.utility.pyarchinit_exp_USsheet_pdf import generate_US_pdf
from ..modules.utility.pyarchinit_print_utility import Print_utility
from ..modules.utility.settings import Settings
#from ..modules.utility.layout_loader import LayoutLoader
from .pyarchinit_setting_matrix import Setting_Matrix
from ..searchLayers import SearchLayers
from ..gui.imageViewer import ImageViewer
from ..gui.pyarchinitConfigDialog import pyArchInitDialog_Config
from ..gui.sortpanelmain import SortPanelMain
from ..resources.resources_rc import *

MAIN_DIALOG_CLASS, _ = loadUiType(
    os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'US_USM.ui'))
class pyarchinit_US(QDialog, MAIN_DIALOG_CLASS):
    L=QgsSettings().value("locale/userLocale")[0:2]
    if L=='it':
        MSG_BOX_TITLE = "PyArchInit - Scheda US"
    elif L=='en':
        MSG_BOX_TITLE = "PyArchInit - SU form"
    elif L=='de':
        MSG_BOX_TITLE = "PyArchInit - SE formular"  
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
    TABLE_NAME = 'us_table'
    MAPPER_TABLE_CLASS = "US"
    HOME = os.environ['PYARCHINIT_HOME']
    PDFFOLDER = '{}{}{}'.format(HOME, os.sep, "pyarchinit_PDF_folder")
    NOME_SCHEDA = "Scheda US"
    ID_TABLE = "id_us"
    ID_SITO ="sito"
    if L=='it':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Sito": "sito",
            "Area": "area",
            "US": "us",
            "Definizione stratigrafica": "d_stratigrafica",
            "Definizione interpretata": "d_interpretativa",
            "Descrizione": "descrizione",
            "Interpretazione": "interpretazione",
            "Periodo Iniziale": "periodo_iniziale",
            "Periodo Finale": "periodo_finale",
            "Fase Iniziale": "fase_iniziale",
            "Fase finale": "fase_finale",
            "Attività": "attivita",
            "Anno di scavo": "anno_scavo",
            "Sigla struttura": "struttura",
            "Scavato": "scavato",
            "Codice periodo": "cont_per",
            "Tipo unità": "unita_tipo",  # nuovi campi per USM
            "Settore": "settore",
            "Quadrato-Parete": "quad_par",
            "Ambiente": "ambient",
            "Saggio": "saggio",
            "Elementi datanti": "elem_datanti",
            "Funzione statica": "funz_statica",
            "Lavorazione": "lavorazione",
            "Spessore giunti": "spess_giunti",
            "Letti di posa": "letti_posa",
            "Altezza modulo": "alt_mod",
            "Unità edile rissuntiva": "un_ed_riass",
            "Reimpiego": "reimp",
            "Posa in opera": "posa_opera",
            "Quota minima USM": "quota_min_usm",
            "Quota max USM": "quota_max_usm",
            "Consistenza legante": "cons_legante",
            "Colore legante": "col_legante",
            "Aggregati legante": "aggreg_legante",
            "Consistenza-Texture": "con_text_mat",
            "Colore materiale": "col_materiale",
            "Inclusi materiali usm": "inclusi_materiali_usm",
            "n catalogo generale" : "n_catalogo_generale",  # campi aggiunti per archeo 3.0 e allineamento ICCD
            "n catalogo interno" : "n_catalogo_interno",
            "n catalogo internazionale" : "n_catalogo_internazionale",
            "soprintendenza" : "soprintendenza",
            "quota relativa" : "quota_relativa",
            "quota abs" : "quota_abs",
            "ref tm" : "ref_tm",
            "ref ra" : "ref_ra",
            "ref n" : "ref_n",
            "posizione" : "posizione",
            "criteri distinzione" : "criteri_distinzione",
            "modo formazione" : "modo_formazione",
            #"componenti organici" : "componenti_organici",
            #"componenti inorganici" : "componenti_inorganici",
            "lunghezza max" : "lunghezza_max",
            "altezza max" : "altezza_max",
            "altezza min" : "altezza_min",
            "profondita max" : "profondita_max",
            "profondita min" : "profondita_min",
            "larghezza media" : "larghezza_media",
            "quota max abs" : "quota_max_abs",
            "quota max rel" : "quota_max_rel",
            "quota min abs" : "quota_min_abs",
            "quota min rel" : "quota_min_rel",
            "osservazioni" : "osservazioni",
            "datazione" : "datazione",
            "flottazione" : "flottazione",
            "setacciatura" : "setacciatura",
            "affidabilita" : "affidabilita",
            "direttore us" : "direttore_us",
            "responsabile us" : "responsabile_us",
            "cod ente schedatore" : "cod_ente_schedatore",
            "data rilevazione" : "data_rilevazione",
            "data rielaborazione" : "data_rielaborazione",
            "lunghezza usm" : "lunghezza_usm",
            "altezza usm" : "altezza_usm",
            "spessore usm" : "spessore_usm",
            "tecnica muraria usm" : "tecnica_muraria_usm",
            "modulo usm" : "modulo_usm",
            "campioni malta usm" : "campioni_malta_usm",
            "campioni mattone usm" : "campioni_mattone_usm",
            "campioni pietra usm" : "campioni_pietra_usm",
            "provenienza materiali usm" : "provenienza_materiali_usm",
            "criteri distinzione usm" : "criteri_distinzione_usm",
            "uso primario usm" : "uso_primario_usm"
        }
    elif L=='de':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Ausgrabungsstätte": "sito",
            "Areal": "area",
            "SE": "us",
            "Stratigraphische Definition": "d_stratigrafica",
            "Interpretierte Definition": "d_interpretativa",
            "Beschreibung": "descrizione",
            "Deutung": "interpretazione",
            "Zeitraum Beginnend": "periodo_iniziale",
            "Zeitraum Ende": "periodo_finale",
            "Phase Beginnend": "fase_iniziale",
            "Phase Ende": "fase_finale",
            "Aktivität": "attivita",
            "Jahr": "anno_scavo",
            "Strukturcode": "struttura",
            "Ausgegraben": "scavato",
            "Periodencode erstellen": "cont_per",
            "Einheit eingeben": "unita_tipo",  # nuovi campi per USM
            "Sektor": "settore",
            "Quadrat / Wand": "quad_par",
            "Raum": "ambient",
            "Graben": "saggio",
            "Datierungselemente": "elem_datanti",
            "Statische Funktion": "funz_statica",
            "Verarbeitung": "lavorazione",
            "Stärke der Fugen": "spess_giunti",
            "Bett": "letti_posa",
            "Höhenmodul": "alt_mod",
            "Zusammenfassung der Baueinheit": "un_ed_riass",
            "Wiederverwendung": "reimp",
            "Verlegung": "posa_opera",
            "Mindesthöhe MSE": "quota_min_usm",
            "max. Höhe MSE": "quota_max_usm",
            "Konsistenz Bindemittel": "cons_legante",
            "Kleur Bindemittel": "col_legante",
            "Aggregat Bindemittel": "aggreg_legante",
            "Konsistenz-Texture": "con_text_mat",
            "Kleur material": "col_materiale",
            "Einschlüsse material mse": "inclusi_materiali_usm",
            "n catalogo generale" : "n_catalogo_generale",  # campi aggiunti per archeo 3.0 e allineamento ICCD
            "N °. Cat. Int." : "n_catalogo_interno",
            "N °. Cat. Internat." : "n_catalogo_internazionale",
            "Landesamt" : "soprintendenza",
            "Relative Höhe" : "quota_relativa",
            "Absolute Höhe" : "quota_abs",
            "Materialformular Referenz" : "ref_tm",
            "Archäologische Funde Referenz" : "ref_ra",
            "Ref. N." : "ref_n",
            "Lange" : "posizione",
            "Unterscheidungskriterien" : "criteri_distinzione",
            "Trainingsmodus" : "modo_formazione",
            #"componenti organici" : "componenti_organici",
            #"componenti inorganici" : "componenti_inorganici",
            "Max.Länge" : "lunghezza_max",
            "Max. Höhe" : "altezza_max",
            "Min. Höhe" : "altezza_min",
            "Max. Tiefe" : "profondita_max",
            "Min. Tiefe" : "profondita_min",
            "Durchschnittliche Breite" : "larghezza_media",
            "Absolute maximale Höhe" : "quota_max_abs",
            "Relative maximale Höhe" : "quota_max_rel",
            "Absolute min Höhe" : "quota_min_abs",
            "Relative min Höhe" : "quota_min_rel",
            "Beobachtungen" : "osservazioni",
            "Datierung" : "datazione",
            "Flotation" : "flottazione",
            "Siebanlage" : "setacciatura",
            "Zuverlässigkeit" : "affidabilita",
            "SE-Direktor" : "direttore_us",
            "SE Leiter" : "responsabile_us",
            "Verfasser Firma's Code" : "cod_ente_schedatore",
            "Datum der Entdeckung" : "data_rilevazione",
            "Überarbeitetes Datum" : "data_rielaborazione",
            "MSE Länge" : "lunghezza_usm",
            "MSE Höhe" : "altezza_usm",
            "MSE Dicke" : "spessore_usm",
            "MSE Maurer-Technik" : "tecnica_muraria_usm",
            "MSE modul" : "modulo_usm",
            "Mörtelproben" : "campioni_malta_usm",
            "Ziegelsteinproben" : "campioni_mattone_usm",
            "Steinproben" : "campioni_pietra_usm",
            "Materieller Ursprung" : "provenienza_materiali_usm",
            "MSE Kriterien für die Unterscheidung" : "criteri_distinzione_usm",
            "Hauptanwendung MSE" : "uso_primario_usm"
        }
    else:
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Site": "sito",
            "Area": "area",
            "SU": "us",
            "Stratigraphic definition": "d_stratigrafica",
            "Interpreted definition": "d_interpretativa",
            "Description": "descrizione",
            "Interpretation": "interpretazione",
            "Initial Period": "periodo_iniziale",
            "Final Period": "periodo_finale",
            "Starting Phase": "fase_iniziale",
            "Final Phase": "fase_finale",
            "Activity": "attivita",
            "Year of excavation": "anno_scavo",
            "Structure code": "struttura",
            "Excavated": "scavato",
            "Period code": "cont_per",
            "Unit type": "unita_tipo",  # nuovi campi per USM
            "Sector": "settore",
            "Square-profile": "quad_par",
            "Room": "ambient",
            "Trench": "saggio",
            "Dating elements": "elem_datanti",
            "Static function": "funz_statica",
            "Processing": "lavorazione",
            "Joint thickness": "spess_giunti",
            "Laying beds": "letti_posa",
            "Module height": "alt_mod",
            "Resurgent Building Unit": "un_ed_riass",
            "Reuse": "reimp",
            "Laying": "posa_opera",
            "Minimum WSU elevation": "quota_min_usm",
            "Max WSU elevation": "quota_max_usm",
            "Binder consistency": "cons_legante",
            "Binder color": "col_legante",
            "Binder aggregates": "aggreg_legante",
            "Consistency-Texture": "con_text_mat",
            "Material color": "col_materiale",
            "Including wsu materials": "inclusi_materiali_usm",
            "n general catalogue" : "n_catalogo_generale",  # campi aggiunti per archeo 3.0 e allineamento ICCD
            "n internal catalogue" : "n_catalogo_interno",
            "n international catalogue" : "n_catalogo_internazionale",
            "superintendence" : "soprintendenza",
            "Relative elevation" : "quota_relativa",
            "abs elevation" : "quota_abs",
            "ref tm" : "ref_tm",
            "ref ra" : "ref_ra",
            "ref n" : "ref_n",
            "position" : "posizione",
            "distinction criteria" : "criteri_distinzione",
            "formation mode" : "modo_formazione",
            #"componenti organici" : "componenti_organici",
            #"componenti inorganici" : "componenti_inorganici",
            "max length" : "lunghezza_max",
            "Max height" : "altezza_max",
            "min height" : "altezza_min",
            "Max depth" : "profondita_max",
            "Min depth" : "profondita_min",
            "average width" : "larghezza_media",
            "elevation max abs" : "quota_max_abs",
            "elevation max relative" : "quota_max_rel",
            "elevation min abs" : "quota_min_abs",
            "elevation min relative" : "quota_min_rel",
            "observation" : "osservazioni",
            "Dating" : "datazione",
            "Flotation" : "flottazione",
            "Sieving" : "setacciatura",
            "Reliability" : "affidabilita",
            "Director SU" : "direttore_us",
            "Responsible SU" : "responsabile_us",
            "Company system code" : "cod_ente_schedatore",
            "date of detection" : "data_rilevazione",
            "date reworked" : "data_rielaborazione",
            "wsu length" : "lunghezza_usm",
            "wsu height" : "altezza_usm",
            "wsu thickness" : "spessore_usm",
            "wsu masonry technique" : "tecnica_muraria_usm",
            "wsu module" : "modulo_usm",
            "wsu mortar samples" : "campioni_malta_usm",
            "wsu brick samples" : "campioni_mattone_usm",
            "wsu stone samples" : "campioni_pietra_usm",
            "wsu material source" : "provenienza_materiali_usm",
            "wsu distinction criteria" : "criteri_distinzione_usm",
            "primary use wsu" : "uso_primario_usm"
        }       
    if L=='it':
        SORT_ITEMS = [
            ID_TABLE,  #0
            "Sito", #1
            "Area", #2
            'US', #3
            "Definizione stratigrafica", #4
            "Definizione interpretata",  #5
            "Descrizione",               #6
            "Interpretazione",           #7
            "Periodo Iniziale",          #8
            "Periodo Finale",            #9
            "Fase Iniziale",             #10
            "Fase Finale",               #11
            "Attività",
            "Anno di scavo",
            "Sigla struttura",
            "Scavato",
            "Codice periodo",
            "Indice di ordinamento",
            "Tipo unità",  # nuovi campi per USM
            "Settore",
            "Quadrato-Parete",
            "Ambiente",
            "Saggio",
            "Elementi datanti",
            "Funzione statica",
            "Lavorazione",
            "Spessore giunti",
            "Letti di posa",
            "Altezza modulo",
            "Unità edile rissuntiva",
            "Reimpiego",
            "Posa in opera",
            "Quota minima USM",
            "Quota max USM",
            "Consistenza legante",
            "Colore legante",
            "Aggregati legante",
            "Consistenza-Texture",
            "Colore materiale",
            "Inclusi materiali usm",
            "n catalogo generale",  #campi aggiunti per archeo 3.0 e allineamento ICCD
            "n catalogo interno",
            "n catalogo internazionale",
            "soprintendenza",
            "quota relativa",
            "quota abs",
            "ref tm",
            "ref ra",
            "ref n",
            "posizione",
            "criteri distinzione",
            "modo formazione",
            #"organici",
            #"inorganici",
            "lunghezza max",
            "altezza max",
            "altezza min",
            "profondita max",
            "profondita min",
            "larghezza media",
            "quota max abs",
            "quota max rel",
            "quota min abs",
            "quota min rel",
            "osservazioni",
            "datazione",
            "flottazione",
            "setacciatura",
            "affidabilita",
            "direttore us",
            "responsabile us",
            "cod ente schedatore",
            "data rilevazione",
            "data rielaborazione",
            "lunghezza usm",
            "altezza usm",
            "spessore usm",
            "tecnica muraria usm",
            "modulo usm",
            "campioni malta usm",
            "campioni mattone usm",
            "campioni pietra usm",
            "provenienza materiali usm",
            "criteri distinzione usm",
            "uso primario usm"]
    elif L == 'de':
        SORT_ITEMS = [
            ID_TABLE,  #0
            "Ausgrabungsstätte",
            "Areal",
            "SE",
            "Stratigraphische Definition",
            "Interpretierte Definition",
            "Beschreibung",
            "Deutung",
            "Zeitraum Beginnend",
            "Zeitraum Ende",
            "Phase Beginnend",
            "Phase Ende",
            "Aktivität",
            "Jahr",
            "Strukturcode",
            "Ausgegraben",
            "Periodencode erstellen",
            "Einheit eingeben",
            "Sektor",
            "Quadrat / Wand",
            "Raum",
            "Graben",
            "Datierungselemente",
            "Statische Funktion",
            "Verarbeitung",
            "Stärke der Fugen",
            "Bett",
            "Höhenmodul",
            "Zusammenfassung der Baueinheit",
            "Wiederverwendung",
            "Verlegung",
            "Mindesthöhe MSE",
            "max. Höhe MSE",
            "Konsistenz Bindemittel",
            "Kleur Bindemittel",
            "Aggregat Bindemittel",
            "Konsistenz-Texture",
            "Kleur material",
            "Einschlüsse material mse",
            "n catalogo generale",
            "N °. Cat. Int." ,
            "N °. Cat. Internat." ,
            "Landesamt" ,
            "Relative Höhe" ,
            "Absolute Höhe" ,
            "Materialformular Referenz",
            "Archäologische Funde Referenz",
            "Ref. N." ,
            "Lange" ,
            "Unterscheidungskriterien" ,
            "Trainingsmodus" ,
            #"componenti organici",
            #"componenti inorganici",
            "Max.Länge" ,
            "Max. Höhe" ,
            "Min. Höhe" ,
            "Max. Tiefe" ,
            "Min. Tiefe" ,
            "Durchschnittliche Breite" ,
            "Absolute maximale Höhe",
            "Relative maximale Höhe",
            "Absolute min Höhe" ,
            "Relative min Höhe",
            "Beobachtungen",
            "Datierung" ,
            "Flotation" ,
            "Siebanlage" ,
            "Zuverlässigkeit" ,
            "SE-Direktor",
            "SE Leiter",
            "Verfasser Firma's Code",
            "Datum der Entdeckung",
            "Überarbeitetes Datum",
            "MSE Länge",
            "MSE Höhe",
            "MSE Dicke",
            "MSE Maurer-Technik",
            "MSE modul" ,
            "Mörtelproben",
            "Ziegelsteinproben",
            "Steinproben",
            "Materieller Ursprung",
            "MSE Kriterien für die Unterscheidung",
            "Hauptanwendung MSE"]
    else:
        SORT_ITEMS = [
            ID_TABLE,  #0
            "Site", #1
            "Area", #2
            "SU", #3
            "Stratigraphic definition", #4
            "Interpreted definition," #5
            "Description", #6
            "Interpretation", #7
            "Initial Period", #8
            "Final Period",#9
            "Starting Phase", #10
            "Final Phase", #11
            "Activity",
            "Year of excavation",
            "Structure code",
            "Excavated",
            "Period code",
            "Sorting index",
            "Unit type", # new fields for USM
            "Sector",
            "Square-profile",
            "Room",
            "Trench",
            "Dating elements",
            "Static function",
            "Processing",
            "Joint thickness",
            "Laying beds",
            "Module height",
            "Resurgent Building Unit",
            "Reuse",
            "Laying",
            "Minimum WSU elevation",
            "Max WSU elevation",
            "Binder consistency",
            "Binder color",
            "Binder aggregates",
            "Consistency-Texture",
            "Material color",
            "Including wsu material",
            "n general catalogue", #added fields for arch 3.0 and ICCD alignment
            "n internal catalogue",
            "n international catalogue",
            "superintendence",
            "Relative elevation",
            "abs elevation",
            "ref tm",
            "ref ra",
            "ref n",
            "position",
            "distinction criteria",
            "formation mode",
            #Organic,
            #Inorganic,
            "max length",
            "Max height",
            "min height",
            "Max depth",
            "Min depth",
            "average width",
            "elevation max abs",
            "elevation max relative",
            "elevation min abs",
            "elevation min relative",
            "observation",
            "Dating",
            "Flotation",
            "Sieving",
            "Reliability",
            "Director SU",
            "Responsible SU",
            "Company system code",
            "date of detection",
            "date reworked",
            "wsu length",
            "wsu height",
            "wsu thickness",
            "wsu masonry technique",
            "wsu module",
            "wsu mortar samples",
            "wsu brick samples",
            "wsu stone samples",
            "wsu material source",
            "wsu distinction criteria",
            "primary use wsu",
    ]
    TABLE_FIELDS = [
        'sito',  # 0
        'area',  # 1
        'us',
        'd_stratigrafica',
        'd_interpretativa',
        'descrizione',
        'interpretazione',
        'periodo_iniziale',
        'fase_iniziale',
        'periodo_finale',
        'fase_finale',
        'scavato',
        'attivita',
        'anno_scavo',
        'metodo_di_scavo',
        'inclusi',
        'campioni',
        'rapporti',
        #'organici',
        #'inorganici',
        'data_schedatura',
        'schedatore',
        'formazione',
        'stato_di_conservazione',
        'colore',
        'consistenza',
        'struttura',
        'cont_per',
        'order_layer',
        'documentazione',
        'unita_tipo',  # nuovi campi per USM
        'settore',
        'quad_par',
        'ambient',
        'saggio',
        'elem_datanti',
        'funz_statica',
        'lavorazione',
        'spess_giunti',
        'letti_posa',
        'alt_mod',
        'un_ed_riass',
        'reimp',
        'posa_opera',
        'quota_min_usm',
        'quota_max_usm',
        'cons_legante',
        'col_legante',
        'aggreg_legante',
        'con_text_mat',
        'col_materiale', #48
        'inclusi_materiali_usm', #49
        'n_catalogo_generale',  # 51 campi aggiunti per archeo 3.0 e allineamento ICCD #50
        'n_catalogo_interno',  # 52
        'n_catalogo_internazionale',  # 53
        'soprintendenza',  # 54
        'quota_relativa',  # 55
        'quota_abs',  # 56
        'ref_tm',  # 57
        'ref_ra',  # 58
        'ref_n',  # 59
        'posizione',  # 60
        'criteri_distinzione',  # 61
        'modo_formazione',  # 62
        'componenti_organici',  # 63
        'componenti_inorganici',  # 64
        'lunghezza_max',  # 65
        'altezza_max',  # 66
        'altezza_min',  # 67
        'profondita_max',  # 68
        'profondita_min',  # 69
        'larghezza_media',  # 70
        'quota_max_abs',  # 71
        'quota_max_rel',  # 72
        'quota_min_abs',  # 73
        'quota_min_rel',  # 74
        'osservazioni',  # 75
        'datazione',  # 76
        'flottazione',  # 77
        'setacciatura',  # 78
        'affidabilita',  # 79
        'direttore_us',  # 80
        'responsabile_us',  # 81
        'cod_ente_schedatore',  # 82
        'data_rilevazione',  # 83
        'data_rielaborazione',  # 84
        'lunghezza_usm',  # 85
        'altezza_usm',  # 86
        'spessore_usm',  # 87
        'tecnica_muraria_usm',  # 88
        'modulo_usm',  # 89
        'campioni_malta_usm',  # 90
        'campioni_mattone_usm',  # 91
        'campioni_pietra_usm',  # 92
        'provenienza_materiali_usm',  # 93
        'criteri_distinzione_usm',  # 94
        'uso_primario_usm',
        'tipologia_opera',
        'sezione_muraria',
        'superficie_analizzata',
        'orientamento',
        'materiali_lat',
        'lavorazione_lat',
        'consistenza_lat',
        'forma_lat',
        'colore_lat',
        'impasto_lat',
        'forma_p',
        'colore_p',
        'taglio_p',
        'posa_opera_p',
        'inerti_usm',
        'tipo_legante_usm',
        'rifinitura_usm',
        'materiale_p',
        'consistenza_p',
        'rapporti2',
        'doc_usv',
        ]
    LANG = {
        "IT": ['it_IT', 'IT', 'it', 'IT_IT'],
        "EN_US": ['en_US','EN_US','en','EN'],
        "DE": ['de_DE','de','DE', 'DE_DE']
    }
    
    REPORT_PATH = '{}{}{}'.format(HOME, os.sep, "pyarchinit_Report_folder")
    MATRIX_PATH = '{}{}{}'.format(HOME, os.sep, "pyarchinit_Matrix_folder")
    BIN = '{}{}{}'.format(HOME, os.sep, "bin")
    DB_SERVER = "not defined"  ####nuovo sistema sort
    
    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.pyQGIS = Pyarchinit_pyqgis(iface)
        self.setupUi(self)
        self.mDockWidget_2.setHidden(True)
        self.mDockWidget_export.setHidden(True)
        self.mDockWidget_3.setHidden(True)
        self.mDockWidget_4.setHidden(True)
        self.mDockWidget_h_check.setHidden(True)
        self.mQgsFileWidget.setHidden(True)
        self.toolButton_file_doc.setHidden(True)
        self.mDockWidget_5.setHidden(True)
        self.tableWidget_rapporti2.setHidden(True)
        self.pushButton_insert_row_rapporti2.setHidden(True)
        self.pushButton_remove_row_rapporti2.setHidden(True)
        self.pushButton_update.setHidden(True)
        self.progressBar_2.setHidden(True)
        self.progressBar_3.setHidden(True)
        # if self.comboBox_per_iniz.currentText() =='':
            # self.checkBox_validate.setHidden(True)
        # else:
            # self.checkBox_validate.setHidden(False)
        # lstSelection = [0,1]
        #self.pushButton_next_rec.pressed.connect(self.selectRows(lstSelection))
        self.currentLayerId = None
        self.search = SearchLayers(iface)
        
        try:
            self.on_pushButton_connect_pressed()
        except Exception as e:
            QMessageBox.warning(self, "Connection System", str(e), QMessageBox.Ok)
            # SIGNALS & SLOTS Functions
        if len(self.DATA_LIST)==0:
            self.comboBox_sito.setCurrentIndex(0)
        else:
            self.comboBox_sito.setCurrentIndex(1)
        
            
        self.comboBox_sito.currentIndexChanged.connect(self.charge_periodo_iniz_list)
        self.comboBox_sito.currentTextChanged.connect(self.charge_periodo_iniz_list)
        self.comboBox_per_iniz.currentIndexChanged.connect(self.charge_periodo_fin_list)
        self.comboBox_sito.currentIndexChanged.connect(self.charge_struttura_list)
        self.comboBox_sito.currentTextChanged.connect(self.charge_struttura_list)
        self.comboBox_per_iniz.currentIndexChanged.connect(self.charge_periodo_fin_list)
        self.comboBox_per_iniz.currentIndexChanged.connect(self.charge_fase_iniz_list)
        self.comboBox_per_iniz.currentIndexChanged.connect(self.charge_datazione_list)
        self.comboBox_fas_iniz.currentIndexChanged.connect(self.charge_datazione_list)
        self.comboBox_sito.currentTextChanged.connect(self.geometry_unitastratigrafiche)### rallenta molto
        
        self.comboBox_sito.currentIndexChanged.connect(self.geometry_unitastratigrafiche)### rallenta molto
        self.comboBox_sito.currentIndexChanged.connect(self.charge_insert_ra)
        self.comboBox_sito.currentTextChanged.connect(self.charge_insert_ra)
        #self.charge_insert_ra()
        self.search_1.currentTextChanged.connect(self.update_filter)
        self.comboBox_per_fin.currentIndexChanged.connect(self.charge_fase_fin_list)
        self.toolButton_pdfpath.clicked.connect(self.setPathpdf)
        self.toolButton_input.clicked.connect(self.setPathdot)
        self.toolButton_output.clicked.connect(self.setPathgraphml)
        self.toolButton_file_doc.clicked.connect(self.setDoc_ref)
        self.pbnOpenpdfDirectory.clicked.connect(self.openpdfDir)
        self.progressBar.setTextVisible(True)
        sito = self.comboBox_sito.currentText()
        self.comboBox_sito.setEditText(sito)
        self.fill_fields()
        self.customize_GUI()
        self.msg_sito()
        self.set_sito()
        self.show()
        self.checkBox_query.update()
        self.checkBox_query.stateChanged.connect(self.listview_us)###anche questo
        
        self.tableWidget_rapporti.itemSelectionChanged.connect(self.us_t)
        
        self.comboBox_unita_tipo.currentTextChanged.connect(self.change_label)
        self.field.currentTextChanged.connect(self.value_check)
        
        
        self.comboBox_per_iniz.currentTextChanged.connect(self.check_v)
        # self.checkBox_validation_rapp.update()
        # self.checkBox_validation_rapp.stateChanged.connect(self.check_listoflist)
        self.tableWidget_rapporti.itemChanged.connect(self.check_listoflist)
        # self.tableWidget_rapporti.itemChanged.connect(self.search_l)
    def on_pushButton_fix_pressed(self):
        sito = "'"+self.comboBox_sito.currentText()+"'"
        area = "'"+self.comboBox_area.currentText()+"'"
        search_dict = {'sito': sito, 'area': area}
        records = self.DB_MANAGER.query_bool(search_dict,
                                             self.MAPPER_TABLE_CLASS)
                                          
        #self.on_pushButton_next_rec_pressed()
        for rec in range(len(records)):
            self.checkBox_validation_rapp.setChecked(True)
            #self.on_pushButton_next_rec_pressed()
            for row in range(self.tableWidget_rapporti.rowCount()):
                table_item = self.tableWidget_rapporti.item(row, 1)
                # row_data = table_item.data(QtCore.Qt.UserRole)
                # row_id = row_data
                self.tableWidget_rapporti.selectRow(row)  
                
            self.check_listoflist()
            #self.on_pushButton_next_rec_pressed()
                
            value = (float(row)/float(self.tableWidget_rapporti.rowCount()))*100
            self.progressBar_3.setValue(value)
            QApplication.processEvents()
        self.progressBar_3.reset()       
    def unit_type_select(self):
        try: 
            dialog = QInputDialog()
            dialog.resize(QtCore.QSize(200, 100))
            if self.L=='it':
                items_st=('US','USM','USVA','USVB','USVC','USD','CON','VSF','SF','SUS','Combinar','Extractor','DOC','property')
            else:
                items_st=('SU','WSU','USVA','USVB','USVC','USD','CON','VSF','SF','SUS','Combinar','Extractor','DOC','property')
            ID_U = dialog.getItem(self, 'Type Unit', "Insert Unit Type",items_st, 0, False)
            Unit = str(ID_U[0])
            return Unit
        except KeyError as e:
            print(str(e))
    
    def search_rapp(self):
        # Clear current selection.
        #self.tableWidget_rapporti.setCurrentItem(None)

        if not s:
            # Empty string, don't search.
            return

        matching_items = self.tableWidget_rapporti.findItems('1',MatchContains)
        if matching_items:
            # We have found something.
            item = matching_items[0]  # Take the first.
            self.tableWidget_rapporti.setCurrentItem(item)

    def check_listoflist(self):
        if self.checkBox_validation_rapp.isChecked():
            try:
                
                
                table_name = "self.tableWidget_rapporti"
                rowSelected_cmd = ("%s.selectedItems()") % (table_name)
                rowSelected = eval(rowSelected_cmd)
                rowIndex = (rowSelected[0].row())
                sito = str(self.comboBox_sito.currentText())
                area = str(self.comboBox_area.currentText())
                us_current=str(self.lineEdit_us.text())
                print(us_current)
                unit = str(self.comboBox_unita_tipo.currentText())
                us_item = self.tableWidget_rapporti.item(rowIndex, 1)
                us = str(us_item.text())
                #print(us)
                rapp_item = self.tableWidget_rapporti.item(rowIndex,0)
                rapp = str(rapp_item.text())
                
                
                self.save_rapp()
                
                if rapp =='Riempito da':
                    rapp='Riempie'             
                elif rapp =='Tagliato da':
                    rapp='Taglia' 
                elif rapp =='Coperto da':
                    rapp='Copre' 
                elif rapp =='Si appoggia a':
                    rapp='Gli si appoggia' 
                elif rapp =='Riempie':
                    rapp='Riempito da'             
                elif rapp =='Taglia':
                    rapp='Tagliato da' 
                elif rapp =='Copre':
                    rapp='Coperto da' 
                elif rapp =='Gli si appoggia':
                    rapp='Si appoggia a'             
                elif rapp =='Filled by':
                    rapp='Fills'             
                elif rapp =='Cutted by':
                    rapp='Cuts' 
                elif rapp =='Covered by':
                    rapp='Covers' 
                elif rapp =='Abuts':
                    rapp='Supports' 
                elif rapp =='Fills':
                    rapp='Filled by'             
                elif rapp =='Cuts':
                    rapp='Cutted by' 
                elif rapp =='Covers':
                    rapp='Covered by' 
                elif rapp =='Supports':
                    rapp='Abuts'    
                
                elif rapp =='>>':
                    rapp='<<'     
                elif rapp =='<<':
                    rapp='>>'
                elif rapp =='>':
                    rapp='<'     
                elif rapp =='<':
                    rapp='>'
                search_dict = {'sito': "'" + str(sito) + "'",
                               'area': "'" + str(area) + "'",
                               'us': us}
                u = Utility()
                search_dict = u.remove_empty_items_fr_dict(search_dict)
                res = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
                
                
                if bool(res):
                    #self.tableWidget_rapporti.setCurrentItem(None)
                    #items = self.tableWidget_rapporti.findItems(us, Qt.MatchCase)
                    items = self.tableWidget_rapporti.findItems(us,Qt.MatchExactly)
                    #QMessageBox.warning(self,'',str(len(items)))
                    
                    self.on_pushButton_go_to_us_pressed()
                    self.checkBox_validation_rapp.setChecked(False)
                    items2 = self.tableWidget_rapporti.findItems(us_current,Qt.MatchExactly)
                    #QMessageBox.warning(self,'',str(len(items2)))
                    
                    if str(len(items))=='1' and str(len(items2))=='1':
                        try:
                            item=items2[0]
                            self.tableWidget_rapporti.setCurrentItem(item)
                        except:
                            pass
                        y=self.tableWidget_rapporti.currentRow()
                        self.tableWidget_rapporti.setItem(y,0,QtWidgets.QTableWidgetItem(rapp))
                        self.tableWidget_rapporti.setItem(y,1,QtWidgets.QTableWidgetItem(us_current))
                        self.save_rapp()
                        
                        self.tableWidget_rapporti.selectRow(y)
                        self.on_pushButton_go_to_us_pressed() 
                        #self.checkBox_validation_rapp.setChecked(False)
                        
                    elif str(len(items))=='1' and str(len(items2))=='0':
                    
                        self.on_pushButton_insert_row_rapporti_pressed()
                        self.tableWidget_rapporti.currentRow()
                        self.tableWidget_rapporti.setItem(0,0,QtWidgets.QTableWidgetItem(rapp))
                        self.tableWidget_rapporti.setItem(0,1,QtWidgets.QTableWidgetItem(us_current))
                        self.save_rapp()
                        self.tableWidget_rapporti.selectRow(0)
                        self.on_pushButton_go_to_us_pressed()    
                    else:
                        QMessageBox.warning(self,'','controlla hai US duplicata')
                    
                elif not bool(res): 
                    
                    tf=self.unit_type_select()
                            
                    self.DB_MANAGER.insert_number_of_us_records(sito,area,us,tf)
                    
                    self.on_pushButton_go_to_us_pressed() 
                    self.on_pushButton_insert_row_rapporti_pressed()
                    self.tableWidget_rapporti.currentRow()
                    
                    a=self.tableWidget_rapporti.setItem(0,0,QtWidgets.QTableWidgetItem(rapp))
                    b=self.tableWidget_rapporti.setItem(0,1,QtWidgets.QTableWidgetItem(us_current))
                    
                    self.save_rapp()
                    self.tableWidget_rapporti.selectRow(0)
                    self.on_pushButton_go_to_us_pressed()
                   
            except:         
                pass
    
        else:
            pass
    def check_v(self):
        if self.comboBox_per_iniz.currentText() =='':
            self.checkBox_validate.setHidden(True)
        else:
            self.checkBox_validate.setHidden(False)
    
    
    def change_label(self):
        if self.comboBox_unita_tipo.currentText()=='DOC':
            self.label_5.setText('Riferimento documentazione')
            self.comboBox_def_intepret.setHidden(True)
            self.mQgsFileWidget.setGeometry(486,128,334,20)
            self.mQgsFileWidget.show()
            self.toolButton_file_doc.show()
        else:
            self.mQgsFileWidget.setHidden(True)
            self.toolButton_file_doc.setHidden(True)
            self.comboBox_def_intepret.show()
        if self.comboBox_unita_tipo.currentText()=='property':
            self.label_5.setText('Descrizione della proprietà')
        if self.comboBox_unita_tipo.currentText().startswith('USV'):
            self.label_5.setText('Descrizione della Unità Str. Virtuale')
        if self.comboBox_unita_tipo.currentText()=='CON':
            self.label_5.setText('Riferimento alla Unità Continuativa')
        if self.comboBox_unita_tipo.currentText()=='CON':
            self.label_5.setText('Riferimento alla Unità Continuativa')
        if self.comboBox_unita_tipo.currentText()=='Combinar':
            self.label_5.setText('Descrizione connettore')
        if self.comboBox_unita_tipo.currentText()=='Extractor':
            self.label_5.setText('Descrizione estrattore')
        if self.comboBox_unita_tipo.currentText()=='SUS':
            self.label_5.setText('Descrizione')    
        if self.comboBox_unita_tipo.currentText()=='SF':
            self.label_5.setText('Descrizione')
        
        
    def refresh(self):
        
        for i in self.DATA_LIST:
            self.us_t()
        return
    def charge_insert_ra(self):
        try:
            
            us =str(self.lineEdit_us.text())
        
            search_dict_inv = {
                
                'sito': "'" +str(self.comboBox_sito.currentText()) + "'",
                'area': "'" + str(eval("self.DATA_LIST[int(self.REC_CORR)].area"))+ "'",
                'us': "'" + str(eval("self.DATA_LIST[int(self.REC_CORR)].us"))+"'"
            }
        
            inv_vl = self.DB_MANAGER.query_bool(search_dict_inv,'INVENTARIO_MATERIALI')
            inv_list = []
            for i in range(len(inv_vl)):
                inv_list.append(str(inv_vl[i].n_reperto))
                inv_list.sort()
            try:
                inv_vl.remove('')
            except :
                pass
            self.comboBox_ref_ra.clear()
            self.comboBox_ref_ra.addItems(self.UTILITY.remove_dup_from_list(inv_list))
            if self.STATUS_ITEMS[self.BROWSE_STATUS] == "Trova" or "Finden" or "Find":
                self.comboBox_ref_ra.setEditText("")
            elif self.STATUS_ITEMS[self.BROWSE_STATUS] == "Usa" or "Aktuell " or "Current":
                if len(self.DATA_LIST) > 0:
                    try:
                        self.comboBox_ref_ra.setEditText(self.DATA_LIST[self.rec_num].ref_ra)
                    except :
                        pass
        except:
            pass                
    def listview_us(self):
        if self.checkBox_query.isChecked():
            conn = Connection()
            conn_str = conn.conn_str()
            conn_sqlite = conn.databasename()
            conn_user = conn.datauser()
            conn_host = conn.datahost()
            conn_port = conn.dataport()
            port_int  = conn_port["port"]
            port_int.replace("'", "")
            conn_password = conn.datapassword()
            sito_set= conn.sito_set()
            sito_set_str = sito_set['sito_set']
            test_conn = conn_str.find('sqlite')
            if test_conn == 0:
                sqlite_DB_path = '{}{}{}'.format(self.HOME, os.sep,
                                           "pyarchinit_DB_folder")
                
                db = QSqlDatabase("QSQLITE") 
                db.setDatabaseName(sqlite_DB_path +os.sep+ conn_sqlite["db_name"])
                db.open()
                self.model_a = QSqlTableModel(db = db) 
                self.table.setModel(self.model_a) 
                self.model_a.setTable("us_table") 
                self.model_a.setEditStrategy(QSqlTableModel.OnManualSubmit)
                self.pushButton_submit.clicked.connect(self.submit)
                self.pushButton_revert.clicked.connect(self.model_a.revertAll)
                column_titles = { 
                    "sito": "SITO", 
                    "area": "Area", 
                    "us": "US"} 
                for n, t in column_titles.items(): 
                    idx = self.model_a.fieldIndex( n) 
                    self.model_a.setHeaderData( idx, Qt.Horizontal, t)
                if bool (sito_set_str):
                    filter_str = "sito = '{}'".format(str(self.comboBox_sito.currentText())) 
                    self.model_a.setFilter(filter_str)
                    self.model_a.select() 
                else:
                    self.model_a.select() 
            
                uri = QgsDataSourceUri()
                uri.setDatabase(sqlite_DB_path +os.sep+ conn_sqlite["db_name"])
                schema = ''
                table = 'us_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.field.clear()
                self.field.addItems(fi)
                try:
                    self.search_1.clearEditText()
                    self.search_1.update()
                    self.value_check()
                except:
                    pass
            else:
                
                
                db = QSqlDatabase.addDatabase("QPSQL")
                db.setHostName(conn_host["host"])
                db.setDatabaseName(conn_sqlite["db_name"])
                db.setPort(int(port_int))
                db.setUserName(conn_user['user'])
                db.setPassword(conn_password['password']) 
                db.open()
                self.model_a = QSqlTableModel(db = db) 
                self.table.setModel(self.model_a) 
                self.model_a.setTable("us_table")
                self.model_a.setEditStrategy(QSqlTableModel.OnManualSubmit)
                self.pushButton_submit.clicked.connect(self.submit)
                self.pushButton_revert.clicked.connect(self.model_a.revertAll)
                if bool (sito_set_str):
                    filter_str = "sito = '{}'".format(str(self.comboBox_sito.currentText())) 
                    self.model_a.setFilter(filter_str)
                    self.model_a.select()
                else:
                    self.model_a.select() 
        
                uri = QgsDataSourceUri()
                uri.setConnection(conn_host["host"], conn_port["port"], conn_sqlite["db_name"], conn_user['user'], conn_password['password'])
                schema = 'public'                
                table = 'us_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.field.clear()
                self.field.addItems(fi)
                try:
                    self.search_1.clearEditText()
                    self.search_1.update()
                    self.value_check()
                except:
                    pass
        else:
            self.checkBox_query.setChecked(False)
    def submit(self):
        if self.checkBox_query.isChecked():
            self.model_a.database().transaction()
            if self.model_a.submitAll():
                self.model_a.database().commit()
                if self.L=='it':
                    QMessageBox.information(self, "Record",  "record salvato")
                elif self.L=='de':
                    QMessageBox.information(self, "Datensatz",  "Datensatz gespeichert")
                else:
                    QMessageBox.information(self, "Record",  "record saved")
            
            else:
                self.model_a.database().rollback()
                if self.L=='it':
                    QMessageBox.warning(self, "Cached Table",
                            "Il db ha segnalato un errore: %s" % self.model_a.lastError().text())    
        
                elif self.L=='de':
                    QMessageBox.warning(self, "Cached Table",
                            "Die Datenbank meldete einen Fehler: %s" % self.model_a.lastError().text())    
                            
                else:
                    QMessageBox.warning(self, "Cached Table",
                            "The database reported an error: %s" % self.model_a.lastError().text())                
        
        else:    
            self.checkBox_query.setChecked(False)
    
    
    def value_check(self):
        try:
            
            if self.field.currentTextChanged:
                sito_vl2 = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('us_table', self.field.currentText(),'US'))

            try:
                sito_vl2.remove('')
            except:
                pass
            self.search_1.clear()
            sito_vl2.sort()
            
            self.search_1.addItems(sito_vl2)
            self.search_1.update()
        except :
            pass#QMessageBox.warning(self, "Attenzione", str(e), QMessageBox.Ok)  
    def update_filter(self, s): 
        if self.checkBox_query.isChecked():
            conn = Connection()            
            conn_str = conn.conn_str()    
            sito_set= conn.sito_set()
            sito_set_str = sito_set['sito_set']
            test_conn = conn_str.find('sqlite')
            s_field = self.field.currentText()
            s = re.sub("[\w_][\W_] +", "", s)
            if test_conn == 0:
                
                
                try:
                    if bool(sito_set_str):
                        filter_str = "{} LIKE '%{}%' and sito = '{}'".format(s_field,s,str(self.comboBox_sito.currentText())) 
                        if bool(filter_str):
                            self.model_a.setFilter(filter_str)
                            self.model_a.select()
                        else:
                            pass
                    
                    else:
                        filter_str = "{} LIKE '%{}%'".format(s_field,s) 
                        if bool(filter_str):
                            self.model_a.setFilter(filter_str)
                            self.model_a.select() 
                        else:
                            pass
                except :
                    pass#QMessageBox.warning(self, "Warning", str(e), QMessageBox.Ok)
            else:
                try:
                    if bool(sito_set_str):
                        filter_str = "{} LIKE '%{}%' and sito = '{}'".format(s_field,s,str(self.comboBox_sito.currentText()))
                        if bool(filter_str):
                            self.model_a.setFilter(filter_str)
                            self.model_a.select()
                        else:
                            pass
                    else:
                        filter_str = "{} LIKE '%{}%'".format(s_field,s) 
                        if bool(filter_str):
                            self.model_a.setFilter(filter_str)
                            self.model_a.select() 
                        else:
                            pass
                except :
                    pass#QMessageBox.warning(self, "Warning", str(e), QMessageBox.Ok)
        else:    
            self.checkBox_query.setChecked(False)
    def on_pushButton_globalsearch_pressed(self):
        self.search.showSearchDialog()    
    def charge_struttura_list(self):
         
        sito = str(self.comboBox_sito.currentText())
        search_dict = {
            'sito': "'" + sito + "'"
        }
        struttura_vl = self.DB_MANAGER.query_bool(search_dict, 'STRUTTURA')
        struttura_list = []
        for i in range(len(struttura_vl)):
            struttura_list.append(str(struttura_vl[i].sigla_struttura+'-'+str(struttura_vl[i].numero_struttura)))
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
                    self.comboBox_struttura.setEditText(self.DATA_LIST[self.rec_num].sigla_struttura+'-'+numero_struttura)
                except:
                    pass  # non vi sono periodi per questo scavo
    def geometry_unitastratigrafiche(self):
        try:
            sito = str(self.comboBox_sito.currentText())
            area = str(self.comboBox_area.currentText())
            us = str(self.lineEdit_us.text())
        
            search_dict = {
                'scavo_s': "'" +str(self.comboBox_sito.currentText()) + "'",
                'area_s': "'" + str(eval("self.DATA_LIST[int(self.REC_CORR)].area")) + "'",
                'us_s': "'" + str(eval("self.DATA_LIST[int(self.REC_CORR)].us"))+"'"
                
            }
        
            geometry_vl = self.DB_MANAGER.query_bool(search_dict,'PYUS')
            geometry_list = []
            
            for i in range(len(geometry_vl)):
                geometry_list.append(str(geometry_vl[i].coord))
            try:
                geometry_vl.remove('')
            except:
                pass
        
            self.comboBox_posizione.clear()
            self.comboBox_posizione.addItems(self.UTILITY.remove_dup_from_list(geometry_list))
            if self.STATUS_ITEMS[self.BROWSE_STATUS] == "Trova" or "Finden" or "Find":
                self.comboBox_posizione.setEditText("")
            elif self.STATUS_ITEMS[self.BROWSE_STATUS] == "Usa" or "Aktuell " or "Current":     
                if len(self.DATA_LIST) > 0:
                    try:
                        self.comboBox_posizione.setEditText(self.DATA_LIST[self.rec_num].posizione)
                        self.comboBox_posizione.show()
                    except:
                        pass  # non vi sono periodi per questo scavo
        except:
            pass
    def charge_periodo_iniz_list(self):
        
        try: 
            
            sito = str(self.comboBox_sito.currentText())
            area = str(self.comboBox_area.currentText())
            search_dict = {
                'sito': "'" + sito + "'",
                #'area': "'" + str(eval("self.DATA_LIST[int(self.REC_CORR)].area")) + "'",
            }
            periodo_vl = self.DB_MANAGER.query_bool(search_dict, 'PERIODIZZAZIONE')
            periodo_list = []
            for i in range(len(periodo_vl)):
                periodo_list.append(str(periodo_vl[i].periodo))
            try:
                periodo_vl.remove('')
            except:
                pass
            #
            self.comboBox_per_iniz.clear()
            self.comboBox_per_iniz.addItems(self.UTILITY.remove_dup_from_list(periodo_list))
            if self.STATUS_ITEMS[self.BROWSE_STATUS] == "Trova" or "Finden" or "Find":
                self.comboBox_per_iniz.setEditText("")
            elif self.STATUS_ITEMS[self.BROWSE_STATUS] == "Usa" or "Aktuell " or "Current": 
                if len(self.DATA_LIST) > 0:
                    try:
                        self.comboBox_per_iniz.setEditText(self.DATA_LIST[self.rec_num].periodo_iniziale)
                        self.comboBox_per_iniz.show()
                    except:
                        pass  # non vi sono periodi per questo scavo
        except:
            pass  
    def charge_periodo_fin_list(self):
        
        try:
            
            sito = str(self.comboBox_sito.currentText())
            area = str(self.comboBox_area.currentText())
            search_dict = {
                'sito': "'" + sito + "'",
                #'area': "'" + str(eval("self.DATA_LIST[int(self.REC_CORR)].area")) + "'",
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
            if self.STATUS_ITEMS[self.BROWSE_STATUS] == "Trova" or "Finden" or "Find":
                self.comboBox_per_fin.setEditText("")
            elif self.STATUS_ITEMS[self.BROWSE_STATUS] == "Usa" or "Aktuell " or "Current": 
                if len(self.DATA_LIST) > 0:
                    try:
                        self.comboBox_per_fin.setEditText(self.DATA_LIST[self.rec_num].periodo_iniziale)
                    except:
                        pass
        except:
            pass  # non vi sono periodi per questo scavo
    def charge_fase_iniz_list(self):
        #if self.comboBox_fas_iniz.activated: 
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
            if self.STATUS_ITEMS[self.BROWSE_STATUS] == "Trova" or "Finden" or "Find":
                self.comboBox_fas_iniz.setEditText("")
            else:
                self.comboBox_fas_iniz.setEditText(self.DATA_LIST[self.rec_num].fase_iniziale)
        except:
            pass
    def charge_fase_fin_list(self):
        #if self.comboBox_fas_fin.activated: 
        try:
            search_dict = {
                'sito': "'" + str(self.comboBox_sito.currentText()) + "'",
                'periodo': "'" + str(self.comboBox_per_fin.currentText()) + "'"
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
            if self.STATUS_ITEMS[self.BROWSE_STATUS] == "Trova" or "Finden" or "Find":
                self.comboBox_fas_fin.setEditText("")
            else:
                self.comboBox_fas_fin.setEditText(self.DATA_LIST[self.rec_num].fase_finale)
        except:
            pass
    def charge_datazione_list(self):
        #if self.comboBox_datazione.activated: 
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
            self.comboBox_datazione.clear()
            datazione_list.sort()
            self.comboBox_datazione.addItems(self.UTILITY.remove_dup_from_list(datazione_list))
            if self.STATUS_ITEMS[self.BROWSE_STATUS] == "Trova" or "Finden" or "Find":
                self.comboBox_datazione.setEditText("")
            else:
                self.comboBox_datazione.setEditText(self.DATA_LIST[self.rec_num].datazione_estesa)
        except:
            pass
    def on_pushButton_draw_doc_pressed(self):
        sito = str(self.comboBox_sito.currentText())
        area = str(self.comboBox_area.currentText())
        us = str(self.lineEdit_us.text())
        table_name = "self.tableWidget_documentazione"
        rowSelected_cmd = ("%s.selectedIndexes()") % (table_name)
        rowSelected = eval(rowSelected_cmd)
        rowIndex = (rowSelected[0].row())
        tipo_doc_item = self.tableWidget_documentazione.item(rowIndex, 0)
        nome_doc_item = self.tableWidget_documentazione.item(rowIndex, 1)
        tipo_doc = str(tipo_doc_item.text())
        nome_doc = str(nome_doc_item.text())
        lista_draw_doc = [sito, area, us, tipo_doc, nome_doc]
        self.pyQGIS.charge_vector_layers_doc_from_scheda_US(lista_draw_doc)
    def save_us(self):
        self.checkBox_query.setChecked(False)
        if self.checkBox_query.isChecked():
            self.model_a.database().close()
        if self.BROWSE_STATUS == "b":
            if self.data_error_check() == 0:
                if self.records_equal_check() == 1:
                    if self.L=='it':
                        self.update_if(QMessageBox.warning(self, 'Attenzione',
                                                           "Il record e' stato modificato. Vuoi salvare le modifiche? \n Clicca OK per salvare o Annulla per abortire.\n Poi riselezione l'US su cui vuoi andare",QMessageBox.Ok | QMessageBox.Cancel))
                    elif self.L=='de':
                        self.update_if(QMessageBox.warning(self, 'Error',
                                                           "Der Record wurde geändert. Möchtest du die Änderungen speichern?",
                                                           QMessageBox.Ok | QMessageBox.Cancel))
                                                           
                    else:
                        self.update_if(QMessageBox.warning(self, 'Error',
                                                           "The record has been changed. Do you want to save the changes?",
                                                           QMessageBox.Ok | QMessageBox.Cancel))
                    self.SORT_STATUS = "n"
                    self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
                    self.enable_button(1)
                    self.fill_fields(self.REC_CORR)
                    
            else:
                pass
                
        
        else:
            if self.data_error_check() == 0:
                test_insert = self.insert_new_rec()
                if test_insert == 1:
                    self.empty_fields()
                    self.label_sort.setText(self.SORTED_ITEMS["n"])
                    self.charge_list()
                    self.set_sito()
                    self.charge_records()
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), len(self.DATA_LIST) - 1
                    self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)

                    self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
                    self.setComboBoxEditable(["self.comboBox_sito"], 1)
                    
                    self.fill_fields(self.REC_CORR)
                    self.enable_button(1)
                    
            else:
                pass
                
  
        
    
    def selectRows(self):
        # seleziona tutte le row della tablewidget dei rapporti
        for row in range(self.tableWidget_rapporti.rowCount()):
            table_item = self.tableWidget_rapporti.item(row, 1)
            row_data = table_item.data(QtCore.Qt.UserRole)
            row_id = row_data
            self.tableWidget_rapporti.selectRow(row)  

    def on_pushButton_update_pressed(self):
        sito = "'"+self.comboBox_sito.currentText()+"'"
        area = "'"+self.comboBox_area.currentText()+"'"
        search_dict = {'sito': sito, 'area': area}
        records = self.DB_MANAGER.query_bool(search_dict,
                                             self.MAPPER_TABLE_CLASS)  # carica tutti i dati di uno scavo ordinati per numero di US
        self.selectRows()
        for rec in range(len(records)):
            self.selectRows()
            self.on_pushButton_next_rec_pressed()
            self.us_t()
                
            self.save_rapp()
            value = (float(rec)/float(len(records)))*100
            self.progressBar_2.setValue(value)
            QApplication.processEvents()
        self.progressBar_2.reset()        
    def us_t(self):
        if self.checkBox_validate.isChecked():
            try:
                
                table_name = "self.tableWidget_rapporti"
                
                rowSelected_cmd = ("%s.selectedItems()") % (table_name)
                rowSelected = eval(rowSelected_cmd)
                
                for i  in rowSelected:
                    self.tableWidget_rapporti2.setRowCount(200)
                    rowIndex = (i.row())
                    sito = str(self.comboBox_sito.currentText())
                    area = str(self.comboBox_area.currentText())
                    area_item = self.tableWidget_rapporti.item(rowIndex, 2)
                    area_ = str(area_item.text())
                    us_item = self.tableWidget_rapporti.item(rowIndex, 1)
                   
                    us_ = str(us_item.text())
                    rapp_item = self.tableWidget_rapporti.item(rowIndex, 0)
                    rapp_ = str(rapp_item.text())
                
                    search_dict = {'sito': "'" + str(sito) + "'",
                                   'area': area_,
                                   'us': us_}
                    u = Utility()
                    search_dict = u.remove_empty_items_fr_dict(search_dict)
                    res = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
                
               
            
                    for p in res:
                        #
                        
                        self.tableWidget_rapporti2.setItem(rowIndex,0,QtWidgets.QTableWidgetItem(rapp_))
                        self.tableWidget_rapporti2.setItem(rowIndex,1,QtWidgets.QTableWidgetItem(us_))
                        self.tableWidget_rapporti2.setItem(rowIndex,2,QtWidgets.QTableWidgetItem(p.unita_tipo))
                        self.tableWidget_rapporti2.setItem(rowIndex,3,QtWidgets.QTableWidgetItem(p.d_interpretativa))
                        self.tableWidget_rapporti2.setItem(rowIndex,4,QtWidgets.QTableWidgetItem(p.periodo_iniziale+'-'+p.fase_iniziale))
                        if area_!='':
                            self.tableWidget_rapporti2.setItem(rowIndex,5,QtWidgets.QTableWidgetItem(area_))
                        else:
                            pass
                        if p.struttura !='':
                            self.tableWidget_rapporti2.setItem(rowIndex,6,QtWidgets.QTableWidgetItem(p.struttura))
                        else:
                            pass
                    self.tableWidget_rapporti2.update()
                    
            except Exception as e:
                QMessageBox.warning(self,'',str(e))
        else:
            pass
    
    
    
    
    
    
    
    
    
    def on_pushButton_go_to_us_pressed(self):    
        #self.save_us()
        try:
            table_name = "self.tableWidget_rapporti"
            rowSelected_cmd = ("%s.selectedIndexes()") % (table_name)
            rowSelected = eval(rowSelected_cmd)
            rowIndex = (rowSelected[0].row())
            sito = str(self.comboBox_sito.currentText())
            area = str(self.comboBox_area.currentText())
            us_item = self.tableWidget_rapporti.item(rowIndex, 1)
            us = str(us_item.text())
            search_dict = {'sito': "'" + str(sito) + "'",
                           'area': "'" + str(area) + "'",
                           'us': us}
            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)
            res = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
            if not bool(res):
                
                #self.DB_MANAGER.insert_number_of_us_records(sito,area,us,'US')
                        
                if self.L=='it':
                    QMessageBox.warning(self, "ATTENZIONE", "Non e' stato trovato alcun record!", QMessageBox.Ok)
                    
                elif self.L=='de':
                    QMessageBox.warning(self, "ACHTUNG", "kein Eintrag gefunden!", QMessageBox.Ok)
                else:
                    QMessageBox.warning(self, "Warning", "The record has not been found ", QMessageBox.Ok)
                self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                self.fill_fields(self.REC_CORR)
                self.BROWSE_STATUS = "b"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.setComboBoxEnable(["self.comboBox_sito"], "False")
                self.setComboBoxEnable(["self.comboBox_area"], "False")
                self.setComboBoxEnable(["self.lineEdit_us"], "False")
            else:
                self.empty_fields()
                self.DATA_LIST = []
                for i in res:
                    self.DATA_LIST.append(i)
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                self.fill_fields()
                self.BROWSE_STATUS = "b"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                if self.REC_TOT == 1:
                    if self.L=='it':
                        strings = ("E' stato trovato", self.REC_TOT, "record")
                    elif self.L=='de':
                        strings = ("Es wurde gefunden", self.REC_TOT, "record")
                    else:
                        strings = ("has been found", self.REC_TOT, "record")
                    if self.toolButtonGis.isChecked():
                        self.pyQGIS.charge_vector_layers(self.DATA_LIST)
                
                    if self.toolButton_usm.isChecked():
                        self.pyQGIS.charge_usm_layers(self.DATA_LIST)
                else:
                    if self.L=='it':
                        strings = ("Sono stati trovati", self.REC_TOT, "records")
                    elif self.L=='de':
                        strings = ("Sie wurden gefunden", self.REC_TOT, "records")
                    else:
                        strings = ("Have been found", self.REC_TOT, "records")
                    if self.toolButtonGis.isChecked():
                        self.pyQGIS.charge_vector_layers(self.DATA_LIST)
                    if self.toolButton_usm.isChecked():
                        self.pyQGIS.charge_usm_layers(self.DATA_LIST)
                
                self.setComboBoxEnable(["self.comboBox_sito"], "False")
                self.setComboBoxEnable(["self.comboBox_area"], "False")
                self.setComboBoxEnable(["self.lineEdit_us"], "False")
        except:
            pass

        
    def on_pushButton_go_to_scheda_pressed(self):
        try:
            #table_name = "self.table"
            #rowSelected_cmd = ("%s.selectedIndexes()") % (table_name)
            rowSelected = self.table.currentIndex()#eval(rowSelected_cmd)
            rowIndex = rowSelected.row()
            sito_item = self.table.model().index(rowIndex,1)
            area_item = self.table.model().index(rowIndex,2)
            #us = str(self.lineEdit_us.text())
            us_item = self.table.model().index(rowIndex,3)
            #for i in us_item:
            sito =self.table.model().data(sito_item)
            area= self.table.model().data(area_item)
            us = self.table.model().data(us_item)
            search_dict = {'sito': "'" + str(sito) + "'",
                           'area': "'" + str(area) + "'",
                           'us': us}
            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)
            res = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
            self.empty_fields()
            self.DATA_LIST = []
            for i in res:
                self.DATA_LIST.append(i)
            self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
            self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
            self.fill_fields()
            self.BROWSE_STATUS = "b"
            self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
            self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
        except Exception as e:
            e = str(e)
            if self.L=='it':
                QMessageBox.warning(self, "Alert", "Non hai selezionato nessuna riga. Errore python: %s " % (str(e)),
                                QMessageBox.Ok)
            elif self.L=='de':
                QMessageBox.warning(self, "ACHTUNG", "Keine Spalte ausgewält. Error python: %s " % (str(e)),
                                QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "Alert", "You didn't select any row. Python error: %s " % (str(e)),
                                QMessageBox.Ok)  
    def enable_button(self, n):
        self.pushButton_list.setEnabled(n)
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
        # self.pushButton_connect.setEnabled(n)
        self.pushButton_new_rec.setEnabled(n)
        self.pushButton_view_all.setEnabled(n)
        self.pushButton_first_rec.setEnabled(n)
        self.pushButton_last_rec.setEnabled(n)
        self.pushButton_prev_rec.setEnabled(n)
        self.pushButton_next_rec.setEnabled(n)
        self.pushButton_delete.setEnabled(n)
        self.pushButton_save.setEnabled(n)
        self.pushButton_sort.setEnabled(n)
        self.pushButton_sort.setEnabled(n)
        self.pushButton_insert_row_rapporti.setEnabled(n)
        self.pushButton_remove_row_rapporti.setEnabled(n)
        self.pushButton_insert_row_inclusi.setEnabled(n)
        self.pushButton_remove_row_inclusi.setEnabled(n)
        self.pushButton_insert_row_campioni.setEnabled(n)
        self.pushButton_remove_row_campioni.setEnabled(n)
        self.pushButton_insert_row_organici.setEnabled(n)
        self.pushButton_remove_row_organici.setEnabled(n)
        self.pushButton_insert_row_inorganici.setEnabled(n)
        self.pushButton_remove_row_inorganici.setEnabled(n)
        self.pushButton_insert_row_documentazione.setEnabled(n)
        self.pushButton_remove_row_documentazione.setEnabled(n)
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
            else:
                if self.L=='it':
                    QMessageBox.warning(self,"BENVENUTO", "Benvenuto in pyArchInit " + self.NOME_SCHEDA + ". Il database e' vuoto. Premi 'Ok' e buon lavoro!",
                                        QMessageBox.Ok)
                elif self.L=='de':
                    QMessageBox.warning(self,"WILLKOMMEN","WILLKOMMEN in pyArchInit" + "SE-MSE formular"+ ". Die Datenbank ist leer. Tippe 'Ok' und aufgehts!",
                                        QMessageBox.Ok) 
                else:
                    QMessageBox.warning(self,"WELCOME", "Welcome in pyArchInit" + "Samples SU-WSU" + ". The DB is empty. Push 'Ok' and Good Work!",
                                        QMessageBox.Ok)    
                self.charge_list()
                self.BROWSE_STATUS = 'x'
                self.setComboBoxEnable(["self.comboBox_area"], "True")
                self.setComboBoxEnable(["self.lineEdit_us"], "True")
                self.on_pushButton_new_rec_pressed()
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
    def customize_GUI(self):
        l = QgsSettings().value("locale/userLocale", QVariant)[0:2]
        lang = ""
        for key, values in self.LANG.items():
            if values.__contains__(l):
                lang = str(key)
        lang = "'" + lang + "'"
        if not Pyarchinit_OS_Utility.checkGraphvizInstallation():
            self.pushButton_export_matrix.setEnabled(False)
            self.pushButton_export_matrix.setToolTip("Funzione disabilitata")
        self.tableWidget_rapporti.setColumnWidth(0, 120)
        self.tableWidget_rapporti.setColumnWidth(1, 80)
        self.tableWidget_rapporti.setColumnWidth(2, 80)
        self.tableWidget_rapporti2.setColumnWidth(0, 80)
        self.tableWidget_rapporti2.setColumnWidth(1, 50)
        self.tableWidget_rapporti2.setColumnWidth(2, 80)
        self.tableWidget_rapporti2.setColumnWidth(3, 200)
        self.tableWidget_rapporti2.setColumnWidth(4, 100)
        self.tableWidget_rapporti2.setColumnWidth(5, 50)
        self.tableWidget_rapporti2.setColumnWidth(6, 120)
        # self.tableWidget_rapporti2.sortItems(0,QtCore.Qt.AscendingOrder)
        # self.tableWidget_rapporti.sortItems(0,QtCore.Qt.AscendingOrder)
        self.tableWidget_documentazione.setColumnWidth(0, 150)
        self.tableWidget_documentazione.setColumnWidth(1, 300)
        
        self.mapPreview = QgsMapCanvas(self)
        self.mapPreview.setCanvasColor(QColor(225, 225, 225))
        self.tabWidget.addTab(self.mapPreview, "Piante")
        # media prevew system
        
        self.iconListWidget.setLineWidth(2)
        self.iconListWidget.setMidLineWidth(2)
        self.iconListWidget.setProperty("showDropIndicator", False)
        self.iconListWidget.setIconSize(QSize(430, 570))
        
        self.iconListWidget.setUniformItemSizes(True)
        self.iconListWidget.setObjectName("iconListWidget")
        self.iconListWidget.SelectionMode()
        self.iconListWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.iconListWidget.itemDoubleClicked.connect(self.openWide_image)
        #self.listWidget_2.itemDoubleClicked.connect(self.opentepmplatePreview)
        # comboBox customizations
        
        self.setComboBoxEditable(["self.comboBox_per_fin"], 1)
        self.setComboBoxEditable(["self.comboBox_fas_fin"], 1)
        self.setComboBoxEditable(["self.comboBox_per_iniz"], 1)
        self.setComboBoxEditable(["self.comboBox_fas_iniz"], 1)
        self.setComboBoxEditable(["self.comboBox_struttura"], 1)
        self.setComboBoxEditable(["self.comboBox_ref_ra"], 1)
        self.setComboBoxEditable(["self.comboBox_datazione"],1)
        # lista tipo rapporti stratigrafici
        if self.L=='it':
            valuesRS = ["Uguale a", "Si lega a", "Copre", "Coperto da", "Riempie", "Riempito da", "Taglia", "Tagliato da", "Si appoggia a", "Gli si appoggia", ">","<","<<",">>","<->",""]
            self.delegateRS = ComboBoxDelegate()
            self.delegateRS.def_values(valuesRS)
            self.delegateRS.def_editable('False')
            self.tableWidget_rapporti.setItemDelegateForColumn(0,self.delegateRS)
           
        elif self.L=='en':
            valuesRS = ["Same as", "Connected to", "Covers", "Covered by", "Fills", "Filled by", "Cuts", "Cutted by", "Abuts", "Supports", ">","<","<<",">>","<->",""]
            self.delegateRS = ComboBoxDelegate()
            self.delegateRS.def_values(valuesRS)
            self.delegateRS.def_editable('False')
            self.tableWidget_rapporti.setItemDelegateForColumn(0,self.delegateRS)
        elif self.L=='de':
            valuesRS = ["Entspricht", "Bindet an", "Liegt über", "Liegt unter", "Verfüllt", "Wird verfüllt durch", "Schneidet", "Wird geschnitten", "Stützt sich auf", "Wird gestüzt von", ">","<","<<",">>","<->",""]
            self.delegateRS = ComboBoxDelegate()
            self.delegateRS.def_values(valuesRS)
            self.delegateRS.def_editable('False')
            self.tableWidget_rapporti.setItemDelegateForColumn(0,self.delegateRS)
        else:
            valuesRS = ["Same as", "Connected to", "Covers", "Covered by", "Fills", "Filled by", "Cuts", "Cutted by", "Abuts", "Supports", ">","<","<<",">>","<->",""]
            self.delegateRS = ComboBoxDelegate()
            self.delegateRS.def_values(valuesRS)
            self.delegateRS.def_editable('False')
            self.tableWidget_rapporti.setItemDelegateForColumn(0,self.delegateRS)
        # lista tipo documentazione
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'us_table' + "'",
            'tipologia_sigla': "'" + '2.19' + "'"
        }
        tipo_di_documentazione = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        valuesDoc = []
        if self.L=='it':
            valuesDoc.append("ICCD-Piante")
            valuesDoc.append("ICCD-Sezioni")
            valuesDoc.append("ICCD-Prospetti")
            valuesDoc.append("ICCD-Foto")
        elif self.L=='de':
            valuesDoc.append("Pflanzen")
            valuesDoc.append("Sektionen")
            valuesDoc.append("Prospekte")
            valuesDoc.append("Foto")
        else:
            valuesDoc.append("Maps")
            valuesDoc.append("Sections")
            valuesDoc.append("Elevations")
            valuesDoc.append("Photo")
        
        for i in range(len(tipo_di_documentazione)):
            valuesDoc.append(tipo_di_documentazione[i].sigla_estesa)
        #valuesDoc.sort()
        self.delegateDoc = ComboBoxDelegate()
        self.delegateDoc.def_values(valuesDoc)
        self.delegateDoc.def_editable('False')
        self.tableWidget_documentazione.setItemDelegateForColumn(0, self.delegateDoc)
        
        
        
        
        # lista colore legante usm
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'us_table' + "'",
            'tipologia_sigla': "'" + '201.201' + "'"
        }
        colore = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        valuesCol = []
        for i in range(len(colore)):
            valuesCol.append(colore[i].sigla_estesa)
        valuesCol.sort()
        self.delegateCol = ComboBoxDelegate()
        self.delegateCol.def_values(valuesCol)
        self.delegateCol.def_editable('False')
        self.tableWidget_colore_legante_usm.setItemDelegateForColumn(0, self.delegateCol)
        # lista colore materiale usm
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'us_table' + "'",
            'tipologia_sigla': "'" + '201.201' + "'"
        }
        colore = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        valuesCol = []
        for i in range(len(colore)):
            valuesCol.append(colore[i].sigla_estesa)
        valuesCol.sort()
        self.delegateCol = ComboBoxDelegate()
        self.delegateCol.def_values(valuesCol)
        self.delegateCol.def_editable('False')
        self.tableWidget_colore_materiale_usm.setItemDelegateForColumn(0, self.delegateCol)
        # lista inclusi leganti usm
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'us_table' + "'",
            'tipologia_sigla': "'" + '202.202' + "'"
        }
        # inclusi = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        # valuesInclusi = []
        # for i in range(len(inclusi)):
            # valuesInclusi.append(inclusi[i].sigla_estesa)
        # valuesCol.sort()
        # self.delegateInclusi = ComboBoxDelegate()
        # self.delegateInclusi.def_values(valuesInclusi)
        # self.delegateInclusi.def_editable('False')
        # self.tableWidget_inclusi_leganti_usm.setItemDelegateForColumn(0, self.delegateInclusi)
        # # lista inclusi materiali usm
        # search_dict = {
            # 'lingua': lang,
            # 'nome_tabella': "'" + 'us_table' + "'",
            # 'tipologia_sigla': "'" + '202.202' + "'"
        # }
        inclusi = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        valuesInclusi = []
        for i in range(len(inclusi)):
            valuesInclusi.append(inclusi[i].sigla_estesa)
        valuesCol.sort()
        self.delegateInclusi = ComboBoxDelegate()
        self.delegateInclusi.def_values(valuesInclusi)
        self.delegateInclusi.def_editable('False')
        self.tableWidget_inclusi_materiali_usm.setItemDelegateForColumn(0, self.delegateInclusi)
        # lista consistenza/texture materiale usm
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'us_table' + "'",
            'tipologia_sigla': "'" + '2.7' + "'"
        }
        constex = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        valuesCTX = []
        for i in range(len(constex)):
            valuesCTX.append(constex[i].sigla_estesa)
        valuesCol.sort()
        self.delegateCons = ComboBoxDelegate()
        self.delegateCons.def_values(valuesCTX)
        self.delegateCons.def_editable('False')
        self.tableWidget_consistenza_texture_mat_usm.setItemDelegateForColumn(0, self.delegateCons)
        # lista componenti organici
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'us_table' + "'",
            'tipologia_sigla': "'" + '2.14' + "'"
        }
        comporg = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        valuesCOG = []
        for i in range(len(comporg)):
            valuesCOG.append(comporg[i].sigla_estesa)
        valuesCOG.sort()
        self.delegateCOG = ComboBoxDelegate()
        self.delegateCOG.def_values(valuesCOG)
        self.delegateCOG.def_editable('False')
        self.tableWidget_organici.setItemDelegateForColumn(0, self.delegateCOG)
        # lista componenti inorganici
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'us_table' + "'",
            'tipologia_sigla': "'" + '2.15' + "'"
        }
        compinorg = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        valuesCINOG = []
        for i in range(len(compinorg)):
            valuesCINOG.append(compinorg[i].sigla_estesa)
        valuesCINOG.sort()
        self.delegateCINOG = ComboBoxDelegate()
        self.delegateCINOG.def_values(valuesCINOG)
        self.delegateCINOG.def_editable('False')
        self.tableWidget_inorganici.setItemDelegateForColumn(0, self.delegateCINOG)
        #lista campioni
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'us_table' + "'",
            'tipologia_sigla': "'" + '2.13' + "'"
        }
        tipo_inclusi_campioni = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        valuesINCL_CAMP = []
        for i in range(len(tipo_inclusi_campioni)):
            valuesINCL_CAMP.append(tipo_inclusi_campioni[i].sigla_estesa)
        valuesINCL_CAMP.sort()
        #valuesINCL_CAMP = ["Terra",
         #                  "Pietre",
         #                  "Laterizio",
         #                  "Ciottoli",
         #                  "Calcare",
         #                  "Calce",
          #                 "Carboni",
         #                  "Concotto",
         #                  "Ghiaia",
         #                  "Cariossidi",
         #                  "Malacofauna",
          #                 "Sabbia",
          #                 "Malta",
          #                 "Ceramica",
          #                 "Metalli",
          #                 "Fr. ossei umani",
           #                "Fr. ossei animali",
           #                "Fr. lapidei"]
        self.delegateINCL_CAMP = ComboBoxDelegate()
        valuesINCL_CAMP.sort()
        self.delegateINCL_CAMP.def_values(valuesINCL_CAMP)
        self.delegateINCL_CAMP.def_editable('False')
        self.tableWidget_campioni.setItemDelegateForColumn(0, self.delegateINCL_CAMP)
        # lista inclusi
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'us_table' + "'",
            'tipologia_sigla': "'" + '202.202' + "'"
        }
        tipo_inclusi = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        valuesINCL = []
        for i in range(len(tipo_inclusi)):
            valuesINCL.append(tipo_inclusi[i].sigla_estesa)
        valuesINCL.sort()
        self.delegateINCL = ComboBoxDelegate()
        self.delegateINCL.def_values(valuesINCL)
        self.delegateINCL.def_editable('False')
        self.tableWidget_inclusi.setItemDelegateForColumn(0, self.delegateINCL)
    # def loadMedialist(self):
        # self.tableWidget_foto.clear()
        # col =['Sito','Area','US','Definizione']
        # self.tableWidget_foto.setHorizontalHeaderLabels(col)
        # numRows = self.tableWidget_foto.setRowCount(100)
        # try: 
            # search_dict = {
                # 'sito': "'" + str(eval("self.DATA_LIST[int(self.REC_CORR)]. " + self.ID_SITO)) + "'"}
            # record_us_list = self.DB_MANAGER.query_bool(search_dict, 'US')
            # nus=0
            # for b in record_us_list:
                # if nus== 0:
                    # self.tableWidget_foto.setItem(nus, 0, QTableWidgetItem(str(b.sito)))
                    # self.tableWidget_foto.setItem(nus, 1, QTableWidgetItem(str(b.area)))
                    # self.tableWidget_foto.setItem(nus, 3, QTableWidgetItem(str(b.d_stratigrafica)))
                    # self.tableWidget_foto.setItem(nus, 2, QTableWidgetItem(str(b.us)))    
                    # nus+=1
                # else:
                    # self.tableWidget_foto.setItem(nus, 0, QTableWidgetItem(str(b.sito)))
                    # self.tableWidget_foto.setItem(nus, 1, QTableWidgetItem(str(b.area)))
                    # self.tableWidget_foto.setItem(nus, 3, QTableWidgetItem(str(b.d_stratigrafica)))
                    # self.tableWidget_foto.setItem(nus, 2, QTableWidgetItem(str(b.us)))    
                    # nus+=1 
        # except:
            # pass
        # search_dict = {
            # 'id_entity': "'" + str(eval("self.DATA_LIST[int(self.REC_CORR)]." + self.ID_TABLE)) + "'",
            # 'entity_type': "'US'"}
        # record_media_list = self.DB_MANAGER.query_bool(search_dict, 'MEDIATOENTITY')
        # n=0
        # for a in record_media_list:
            # if n== 0:
                # self.tableWidget_foto.setItem(n, 3,QTableWidgetItem(str(a.media_name)))
                # n+=1
            # else:
                # self.tableWidget_foto.setItem(n, 3,QTableWidgetItem(str(a.media_name)))
                # n+=1
    def loadMapPreview(self, mode=0):
        if mode == 0:
            """ if has geometry column load to map canvas """
            gidstr = self.ID_TABLE + " = " + str(
                eval("self.DATA_LIST[int(self.REC_CORR)]." + self.ID_TABLE))
            layerToSet = self.pyQGIS.loadMapPreview(gidstr)
            QMessageBox.warning(self, "layer to set", '\n'.join([l.name() for l in layerToSet]), QMessageBox.Ok)
            self.mapPreview.setLayers(layerToSet)
            self.mapPreview.zoomToFullExtent()
        elif mode == 1:
            self.mapPreview.setLayers([])
            self.mapPreview.zoomToFullExtent()
    def loadMediaPreview(self):
        self.iconListWidget.clear()
        conn = Connection()
        thumb_path = conn.thumb_path()
        thumb_path_str = thumb_path['thumb_path']
        # if mode == 0:
        # """ if has geometry column load to map canvas """
        rec_list = self.ID_TABLE + " = " + str(
            eval("self.DATA_LIST[int(self.REC_CORR)]." + self.ID_TABLE))
        search_dict = {
            'id_entity': "'" + str(eval("self.DATA_LIST[int(self.REC_CORR)]." + self.ID_TABLE)) + "'",
            'entity_type': "'US'"}
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
        # elif mode == 1:
            # self.iconListWidget.clear()
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
    def charge_list(self):
        l = QgsSettings().value("locale/userLocale", QVariant)
        lang = ""
        for key, values in self.LANG.items():
            if values.__contains__(l):
                lang = str(key)
        lang = "'" + lang + "'"
        # lista sito
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
        self.comboBox_sito_rappcheck.clear()
        sito_vl.sort()
        self.comboBox_sito.addItems(sito_vl)
        self.comboBox_sito_rappcheck.addItems(sito_vl)
        
        responsabile_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('us_table', 'schedatore', 'US'))
        try:
            responsabile_vl.remove('')
        except:
            pass
            
        self.comboBox_schedatore.clear()
        responsabile_vl.sort()
        self.comboBox_schedatore.addItems(responsabile_vl)
        
        
        responsabile2_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('us_table', 'direttore_us', 'US'))
        try:
            responsabile2_vl.remove('')
        except:
            pass
            
        self.comboBox_direttore_us.clear()
        responsabile2_vl.sort()
        self.comboBox_direttore_us.addItems(responsabile2_vl)
        
        
        responsabile3_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('us_table', 'responsabile_us', 'US'))
        try:
            responsabile3_vl.remove('')
        except:
            pass
            
        self.comboBox_responsabile_us.clear()
        responsabile3_vl.sort()
        self.comboBox_responsabile_us.addItems(responsabile3_vl)
        
        
        
        
        
        self.comboBox_settore.clear()       
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'us_table' + "'",
            'tipologia_sigla': "'" + '2.1' + "'"
        }
        settore = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        settore_vl = []
        for i in range(len(settore)):
            settore_vl.append(settore[i].sigla)
        settore_vl.sort()
        self.comboBox_settore.addItems(settore_vl)
        # lista soprintendenza
        self.comboBox_soprintendenza.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'us_table' + "'",
            'tipologia_sigla': "'" + '2.2' + "'"
        }
        soprintendenza = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        soprintendenza_vl = []
        for i in range(len(soprintendenza)):
            soprintendenza_vl.append(soprintendenza[i].sigla_estesa)
        soprintendenza_vl.sort()
        self.comboBox_soprintendenza.addItems(soprintendenza_vl)
        # lista definizione_stratigrafica
        self.comboBox_def_strat.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'us_table' + "'",
            'tipologia_sigla': "'" + '2.3' + "'"
        }
        d_stratigrafica = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        d_stratigrafica_vl = []
        for i in range(len(d_stratigrafica)):
            d_stratigrafica_vl.append(d_stratigrafica[i].sigla_estesa)
        d_stratigrafica_vl.sort()
        self.comboBox_def_strat.addItems(d_stratigrafica_vl)
        # lista definizione interpretata
        self.comboBox_def_intepret.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'us_table' + "'",
            'tipologia_sigla': "'" + '2.4' + "'"
        }
        d_interpretativa = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        d_interpretativa_vl = []
        for i in range(len(d_interpretativa)):
            d_interpretativa_vl.append(d_interpretativa[i].sigla_estesa)
        d_interpretativa_vl.sort()
        self.comboBox_def_intepret.addItems(d_interpretativa_vl)
        # lista funzione statica
        self.comboBox_funz_statica_usm.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'us_table' + "'",
            'tipologia_sigla': "'" + '2.5' + "'"
        }
        funz_statica = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        funz_statica_vl = []
        for i in range(len(funz_statica)):
            if funz_statica[i].sigla_estesa not in funz_statica_vl:
                funz_statica_vl.append(funz_statica[i].sigla_estesa)
        funz_statica_vl.sort()
        self.comboBox_funz_statica_usm.addItems(funz_statica_vl)
        #lista consistenza legante usm
        self.comboBox_consistenza_legante_usm.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'us_table' + "'",
            'tipologia_sigla': "'" + '2.6' + "'"
        }
        consistenza_legante_usm = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        consistenza_legante_usm_vl = []
        for i in range(len(consistenza_legante_usm)):
            if consistenza_legante_usm[i].sigla_estesa not in consistenza_legante_usm_vl:
                consistenza_legante_usm_vl.append(consistenza_legante_usm[i].sigla_estesa)
        consistenza_legante_usm_vl.sort()
        self.comboBox_consistenza_legante_usm.addItems(consistenza_legante_usm_vl)
        # lista scavato
        self.comboBox_scavato.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'us_table' + "'",
            'tipologia_sigla': "'" + '203.203' + "'"
        }
        scavato = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        scavato_vl = []
        for i in range(len(scavato)):
            if scavato[i].sigla_estesa not in scavato_vl:
                scavato_vl.append(scavato[i].sigla_estesa)
        scavato_vl.sort()
        self.comboBox_scavato.addItems(scavato_vl)
        # lista metodo di scavo
        self.comboBox_metodo.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'us_table' + "'",
            'tipologia_sigla': "'" + '2.8' + "'"
        }
        metodo = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        metodo_vl = []
        for i in range(len(metodo)):
            if metodo[i].sigla_estesa not in metodo_vl:
                metodo_vl.append(metodo[i].sigla_estesa)
        metodo_vl.sort()
        self.comboBox_metodo.addItems(metodo_vl)
        # lista formazione
        self.comboBox_formazione.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'us_table' + "'",
            'tipologia_sigla': "'" + '2.9' + "'"
        }
        formazione = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        formazione_vl = []
        for i in range(len(formazione)):
            if formazione[i].sigla_estesa not in formazione_vl:
                formazione_vl.append(formazione[i].sigla_estesa)
        formazione_vl.sort()
        self.comboBox_formazione.addItems(formazione_vl)
        # lista modo formazione
        self.comboBox_modo_formazione.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'us_table' + "'",
            'tipologia_sigla': "'" + '2.10' + "'"
        }
        modo_formazione = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        modo_formazione_vl = []
        for i in range(len(modo_formazione)):
            if modo_formazione[i].sigla_estesa not in modo_formazione_vl:
                modo_formazione_vl.append(modo_formazione[i].sigla_estesa)
        modo_formazione_vl.sort()
        self.comboBox_modo_formazione.addItems(modo_formazione_vl)
        # lista colore
        self.comboBox_colore.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'us_table' + "'",
            'tipologia_sigla': "'" + '201.201' + "'"
        }
        colore = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        colore_vl = []
        for i in range(len(colore)):
            if colore[i].sigla_estesa not in colore_vl:
                colore_vl.append(colore[i].sigla_estesa)
        colore_vl.sort()
        self.comboBox_colore.addItems(colore_vl)
        # lista consistenza
        self.comboBox_consistenza.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'us_table' + "'",
            'tipologia_sigla': "'" + '2.11' + "'"
        }
        consistenza = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        consistenza_vl = []
        for i in range(len(consistenza)):
            if consistenza[i].sigla_estesa not in consistenza_vl:
                consistenza_vl.append(consistenza[i].sigla_estesa)
        consistenza_vl.sort()
        self.comboBox_consistenza.addItems(consistenza_vl)
        # lista stato di conservazione
        self.comboBox_conservazione.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'us_table' + "'",
            'tipologia_sigla': "'" + '2.12' + "'"
        }
        conservazione = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        conservazione_vl = []
        for i in range(len(conservazione)):
            if conservazione[i].sigla_estesa not in conservazione_vl:
                conservazione_vl.append(conservazione[i].sigla_estesa)
        conservazione_vl.sort()
        self.comboBox_conservazione.addItems(conservazione_vl)
        # lista schedatore
        # self.comboBox_schedatore.clear()
        # search_dict = {
            # 'lingua': lang,
            # 'nome_tabella': "'" + 'us_table' + "'",
            # 'tipologia_sigla': "'" + '2.16' + "'"
        #}
        # schedatore = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        # schedatore_vl = []
        # for i in range(len(schedatore)):
            # if schedatore[i].sigla_estesa not in schedatore_vl:
                # schedatore_vl.append(schedatore[i].sigla_estesa)
        # schedatore_vl.sort()
        # self.comboBox_schedatore.addItems(schedatore_vl)
        # # lista direttore us
        # self.comboBox_direttore_us.clear()
        # search_dict = {
            # 'lingua': lang,
            # 'nome_tabella': "'" + 'us_table' + "'",
            # 'tipologia_sigla': "'" + '2.17' + "'"
        # }
        # direttore_us = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        # direttore_us_vl = []
        # for i in range(len(direttore_us)):
            # if direttore_us[i].sigla_estesa not in direttore_us_vl:
                # direttore_us_vl.append(direttore_us[i].sigla_estesa)
        # direttore_us_vl.sort()
        # self.comboBox_direttore_us.addItems(direttore_us_vl)
        # # lista responsabile us
        # self.comboBox_responsabile_us.clear()
        # search_dict = {
            # 'lingua': lang,
            # 'nome_tabella': "'" + 'us_table' + "'",
            # 'tipologia_sigla': "'" + '2.18' + "'"
        # }
        # responsabile_us = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        # responsabile_us_vl = []
        # for i in range(len(responsabile_us)):
            # if responsabile_us[i].sigla_estesa not in responsabile_us_vl:
                # responsabile_us_vl.append(responsabile_us[i].sigla_estesa)
        # responsabile_us_vl.sort()
        # self.comboBox_responsabile_us.addItems(responsabile_us_vl)
        
        
        # # lista tipologia_opera
        self.comboBox_tipologia_opera.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'us_table' + "'",
            'tipologia_sigla': "'" + '2.20' + "'"
        }
        tipologia_opera = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        tipologia_opera_us_vl = []
        for i in range(len(tipologia_opera)):
            if tipologia_opera[i].sigla_estesa not in tipologia_opera_us_vl:
                tipologia_opera_us_vl.append(tipologia_opera[i].sigla_estesa)
        tipologia_opera_us_vl.sort()
        self.comboBox_tipologia_opera.addItems(tipologia_opera_us_vl)
        # lista sezione muraria
        self.comboBox_sezione_muraria.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'us_table' + "'",
            'tipologia_sigla': "'" + '2.21' + "'"
        }
        sezione_muraria = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        sezione_muraria_us_vl = []
        for i in range(len(sezione_muraria)):
            if sezione_muraria[i].sigla_estesa not in sezione_muraria_us_vl:
                sezione_muraria_us_vl.append(sezione_muraria[i].sigla_estesa)
        sezione_muraria_us_vl.sort()
        self.comboBox_sezione_muraria.addItems(sezione_muraria_us_vl)
        # lista superficie_analizzata
        self.comboBox_superficie_analizzata.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'us_table' + "'",
            'tipologia_sigla': "'" + '2.22' + "'"
        }
        sup_analiz = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        sup_analiz_vl = []
        for i in range(len(sezione_muraria)):
            if sup_analiz[i].sigla_estesa not in sup_analiz_vl:
                sup_analiz_vl.append(sup_analiz[i].sigla_estesa)
        sezione_muraria_us_vl.sort()
        self.comboBox_superficie_analizzata.addItems(sup_analiz_vl)
        # lista orientamento
        self.comboBox_orientamento.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'us_table' + "'",
            'tipologia_sigla': "'" + '2.23' + "'"
        }
        orientamento = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        orientamento_us_vl = []
        for i in range(len(orientamento)):
            if orientamento[i].sigla_estesa not in orientamento_us_vl:
                orientamento_us_vl.append(orientamento[i].sigla_estesa)
        orientamento_us_vl.sort()
        self.comboBox_orientamento.addItems(orientamento_us_vl)
        # lista materiali_laterizi
        self.comboBox_materiali_lat.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'us_table' + "'",
            'tipologia_sigla': "'" + '2.24' + "'"
        }
        materiali_lat = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        materiali_lat_us_vl = []
        for i in range(len(materiali_lat)):
            if materiali_lat[i].sigla_estesa not in materiali_lat_us_vl:
                materiali_lat_us_vl.append(materiali_lat[i].sigla_estesa)
        materiali_lat_us_vl.sort()
        self.comboBox_materiali_lat.addItems(materiali_lat_us_vl)
        # lista lavorazione laterizi
        self.comboBox_lavorazione_lat.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'us_table' + "'",
            'tipologia_sigla': "'" + '2.25' + "'"
        }
        lavorazione_lat = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        lavorazione_lat_us_vl = []
        for i in range(len(lavorazione_lat)):
            if lavorazione_lat[i].sigla_estesa not in lavorazione_lat_us_vl:
                lavorazione_lat_us_vl.append(lavorazione_lat[i].sigla_estesa)
        lavorazione_lat_us_vl.sort()
        self.comboBox_lavorazione_lat.addItems(lavorazione_lat_us_vl)
        # lista consistenza laterizi
        self.comboBox_consistenza_lat.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'us_table' + "'",
            'tipologia_sigla': "'" + '2.26' + "'"
        }
        consistenza_lat = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        consistenza_lat_us_vl = []
        for i in range(len(consistenza_lat)):
            if consistenza_lat[i].sigla_estesa not in consistenza_lat_us_vl:
                consistenza_lat_us_vl.append(consistenza_lat[i].sigla_estesa)
        consistenza_lat_us_vl.sort()
        self.comboBox_consistenza_lat.addItems(consistenza_lat_us_vl)
        # lista forma laterizi
        self.comboBox_forma_lat.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'us_table' + "'",
            'tipologia_sigla': "'" + '2.27' + "'"
        }
        forma_lat = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        forma_lat_us_vl = []
        for i in range(len(forma_lat)):
            if forma_lat[i].sigla_estesa not in forma_lat_us_vl:
                forma_lat_us_vl.append(forma_lat[i].sigla_estesa)
        forma_lat_us_vl.sort()
        self.comboBox_forma_lat.addItems(forma_lat_us_vl)
        # lista colore laterizi
        self.comboBox_colore_lat.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'us_table' + "'",
            'tipologia_sigla': "'" + '2.28' + "'"
        }
        colore_lat = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        colore_lat_us_vl = []
        for i in range(len(colore_lat)):
            if colore_lat[i].sigla_estesa not in colore_lat_us_vl:
                colore_lat_us_vl.append(colore_lat[i].sigla_estesa)
        colore_lat_us_vl.sort()
        self.comboBox_colore_lat.addItems(colore_lat_us_vl)
        # lista impasto laterizi
        self.comboBox_impasto_lat.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'us_table' + "'",
            'tipologia_sigla': "'" + '2.29' + "'"
        }
        impasto_lat = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        impasto_lat_us_vl = []
        for i in range(len(impasto_lat)):
            if impasto_lat[i].sigla_estesa not in impasto_lat_us_vl:
                impasto_lat_us_vl.append(impasto_lat[i].sigla_estesa)
        impasto_lat_us_vl.sort()
        self.comboBox_impasto_lat.addItems(impasto_lat_us_vl)
        # lista materiali litici
        self.comboBox_materiale_p.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'us_table' + "'",
            'tipologia_sigla': "'" + '2.30' + "'"
        }
        materiale_p = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        materiale_p_us_vl = []
        for i in range(len(materiale_p)):
            if materiale_p[i].sigla_estesa not in materiale_p_us_vl:
                materiale_p_us_vl.append(materiale_p[i].sigla_estesa)
        materiale_p_us_vl.sort()
        self.comboBox_materiale_p.addItems(materiale_p_us_vl)
        # lista consistenza materiali litici
        self.comboBox_consistenza_p.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'us_table' + "'",
            'tipologia_sigla': "'" + '2.31' + "'"
        }
        consistenza_p = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        consistenza_p_us_vl = []
        for i in range(len(consistenza_p)):
            if consistenza_p[i].sigla_estesa not in consistenza_p_us_vl:
                consistenza_p_us_vl.append(consistenza_p[i].sigla_estesa)
        consistenza_p_us_vl.sort()
        self.comboBox_consistenza_p.addItems(consistenza_p_us_vl)
        # lista forma materiali litici
        self.comboBox_forma_p.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'us_table' + "'",
            'tipologia_sigla': "'" + '2.32' + "'"
        }
        forma_p = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        forma_p_us_vl = []
        for i in range(len(forma_p)):
            if forma_p[i].sigla_estesa not in forma_p_us_vl:
                forma_p_us_vl.append(forma_p[i].sigla_estesa)
        forma_p_us_vl.sort()
        self.comboBox_forma_p.addItems(forma_p_us_vl)
        # lista colore materiali litici
        self.comboBox_colore_p.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'us_table' + "'",
            'tipologia_sigla': "'" + '2.33' + "'"
        }
        colore_p = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        colore_p_us_vl = []
        for i in range(len(colore_p)):
            if colore_p[i].sigla_estesa not in colore_p_us_vl:
                colore_p_us_vl.append(colore_p[i].sigla_estesa)
        colore_p_us_vl.sort()
        self.comboBox_colore_p.addItems(colore_p_us_vl)
        # lista taglio materiali litici
        self.comboBox_taglio_p.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'us_table' + "'",
            'tipologia_sigla': "'" + '2.34' + "'"
        }
        taglio_p = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        taglio_p_us_vl = []
        for i in range(len(taglio_p)):
            if taglio_p[i].sigla_estesa not in taglio_p_us_vl:
                taglio_p_us_vl.append(taglio_p[i].sigla_estesa)
        taglio_p_us_vl.sort()
        self.comboBox_taglio_p.addItems(taglio_p_us_vl)
        # lista posa opera materiali litici
        self.comboBox_posa_opera_p.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'us_table' + "'",
            'tipologia_sigla': "'" + '2.35' + "'"
        }
        posa_opera_p = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        posa_opera_p_us_vl = []
        for i in range(len(posa_opera_p)):
            if posa_opera_p[i].sigla_estesa not in posa_opera_p_us_vl:
                posa_opera_p_us_vl.append(posa_opera_p[i].sigla_estesa)
        posa_opera_p_us_vl.sort()
        self.comboBox_posa_opera_p.addItems(posa_opera_p_us_vl)
        # lista posa opera materiali laterizi
        self.comboBox_posa_in_opera_usm.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'us_table' + "'",
            'tipologia_sigla': "'" + '2.36' + "'"
        }
        posa_opera_usm = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        posa_opera_usm_us_vl = []
        for i in range(len(posa_opera_usm)):
            if posa_opera_usm[i].sigla_estesa not in posa_opera_usm_us_vl:
                posa_opera_usm_us_vl.append(posa_opera_usm[i].sigla_estesa)
        posa_opera_usm_us_vl.sort()
        self.comboBox_posa_in_opera_usm.addItems(posa_opera_usm_us_vl)
        # lista tecniche costruttive
        self.comboBox_tecnica_muraria_usm.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'us_table' + "'",
            'tipologia_sigla': "'" + '2.37' + "'"
        }
        t_costruttiva = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        t_costruttiva_us_vl = []
        for i in range(len(t_costruttiva)):
            if t_costruttiva[i].sigla_estesa not in t_costruttiva_us_vl:
                t_costruttiva_us_vl.append(t_costruttiva[i].sigla_estesa)
        t_costruttiva_us_vl.sort()
        self.comboBox_tecnica_muraria_usm.addItems(t_costruttiva_us_vl)
        # lista modulo
        self.comboBox_modulo_usm.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'us_table' + "'",
            'tipologia_sigla': "'" + '2.38' + "'"
        }
        modulo = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        modulo_us_vl = []
        for i in range(len(modulo)):
            if modulo[i].sigla_estesa not in modulo_us_vl:
                modulo_us_vl.append(modulo[i].sigla_estesa)
        modulo_us_vl.sort()
        self.comboBox_modulo_usm.addItems(modulo_us_vl)
        # lista inerti
        self.comboBox_inerti_usm.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'us_table' + "'",
            'tipologia_sigla': "'" + '2.39' + "'"
        }
        inerti = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        inerti_us_vl = []
        for i in range(len(inerti)):
            if inerti[i].sigla_estesa not in inerti_us_vl:
                inerti_us_vl.append(inerti[i].sigla_estesa)
        inerti_us_vl.sort()
        self.comboBox_inerti_usm.addItems(inerti_us_vl)
        # lista tipologia legante
        self.comboBox_tipo_legante_usm.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'us_table' + "'",
            'tipologia_sigla': "'" + '2.40' + "'"
        }
        tipo_legante = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        tipo_legante_us_vl = []
        for i in range(len(tipo_legante)):
            if tipo_legante[i].sigla_estesa not in tipo_legante_us_vl:
                tipo_legante_us_vl.append(tipo_legante[i].sigla_estesa)
        tipo_legante_us_vl.sort()
        self.comboBox_tipo_legante_usm.addItems(tipo_legante_us_vl)
        # lista rifinitura
        self.comboBox_rifinitura_usm.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'us_table' + "'",
            'tipologia_sigla': "'" + '2.41' + "'"
        }
        rifinitura = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        rifinitura_us_vl = []
        for i in range(len(rifinitura)):
            if rifinitura[i].sigla_estesa not in rifinitura_us_vl:
                rifinitura_us_vl.append(rifinitura[i].sigla_estesa)
        rifinitura_us_vl.sort()
        self.comboBox_rifinitura_usm.addItems(rifinitura_us_vl)
        # lista lavorazione litica
        self.comboBox_lavorazione_usm.clear()
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'us_table' + "'",
            'tipologia_sigla': "'" + '2.42' + "'"
        }
        lavorazione_p = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        lavorazione_p_us_vl = []
        for i in range(len(lavorazione_p)):
            if lavorazione_p[i].sigla_estesa not in lavorazione_p_us_vl:
                lavorazione_p_us_vl.append(lavorazione_p[i].sigla_estesa)
        lavorazione_p_us_vl.sort()
        self.comboBox_lavorazione_usm.addItems(lavorazione_p_us_vl)
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
        except Exception as e:
            if self.L=='it':
            
                QMessageBox.information(self, "Attenzione" ,"Non esiste questo sito: "'"'+str(sito_set_str) +'"'" in questa scheda, Per favore distattiva la 'scelta sito' dalla scheda di configurazione plugin per vedere tutti i record oppure crea la scheda",QMessageBox.Ok) 
            elif self.L=='de':
            
                QMessageBox.information(self, "Warnung" , "Es gibt keine solche archäologische Stätte: "'""'+ str(sito_set_str) +'"'" in dieser Registerkarte, Bitte deaktivieren Sie die 'Site-Wahl' in der Plugin-Konfigurationsregisterkarte, um alle Datensätze zu sehen oder die Registerkarte zu erstellen",QMessageBox.Ok) 
            else:
            
                QMessageBox.information(self, "Warning" , "There is no such site: "'"'+ str(sito_set_str) +'"'" in this tab, Please disable the 'site choice' from the plugin configuration tab to see all records or create the tab",QMessageBox.Ok) 
    def generate_list_foto(self):
        data_list_foto = []
        for i in range(len(self.DATA_LIST)):
            conn = Connection()
            thumb_path = conn.thumb_path()
            thumb_path_str = thumb_path['thumb_path']
            if thumb_path_str=='':
                if self.L=='it':
                    QMessageBox.information(self, "Info", "devi settare prima la path per salvare le thumbnail . Vai in impostazioni di sistema/ path setting ")
                elif self.L=='de':
                    QMessageBox.information(self, "Info", "müssen Sie zuerst den Pfad zum Speichern der Miniaturansichten und Videos festlegen. Gehen Sie zu System-/Pfad-Einstellung")
                else:
                    QMessageBox.information(self, "Message", "you must first set the path to save the thumbnails and videos. Go to system/path setting")
            else:    
                search_dict = {'id_entity': "'"+ str(eval("self.DATA_LIST[i].id_us"))+"'", 'entity_type' : "'US'"}
                record_doc_list = self.DB_MANAGER.query_bool(search_dict, 'MEDIAVIEW')
                for media in record_doc_list:
                    thumbnail = (thumb_path_str+media.filepath)
                    foto= (media.id_media)
                    # #sito= (media.sito)
                    # area= (media.area)
                    # us= (media.us)
                    # d_stratigrafica= ''
                    # unita_tipo = (media.unita_tipo)
                    data_list_foto.append([
                        str(self.DATA_LIST[i].sito.replace('_',' ')), #0
                        str(self.DATA_LIST[i].area), #1
                        str(self.DATA_LIST[i].us),    #2
                        str(self.DATA_LIST[i].unita_tipo),#3
                        str(self.DATA_LIST[i].d_stratigrafica),  #4 
                        str(foto),#5
                        str(thumbnail)])#6
        return data_list_foto
            # #####################fine########################
    def generate_list_pdf(self):
        data_list = []
        #############inserimento nome fiel media############
        for i in range(len(self.DATA_LIST)):
            # assegnazione valori di quota mn e max
            id_us = str(self.DATA_LIST[i].id_us)
            sito = str(self.DATA_LIST[i].sito)#.replace('_',' '))
            area = str(self.DATA_LIST[i].area)
            us = str(self.DATA_LIST[i].us)
            res = self.DB_MANAGER.select_quote_from_db_sql(sito, area, us)
            quote = []
            for sing_us in res:
                sing_quota_value = str(sing_us[5])
                if sing_quota_value[0] == '-':
                    sing_quota_value = sing_quota_value[:7]
                else:
                    sing_quota_value = sing_quota_value[:6]
                sing_quota = [sing_quota_value, sing_us[4]]
                quote.append(sing_quota)
            quote.sort()
            #QMessageBox.information(self, "Message", str(quote))
            if bool(quote):
                quota_min = '%s %s' % (quote[0][0], quote[0][1])
                quota_max = '%s %s' % (quote[-1][0], quote[-1][1])
                
            else:
                if self.L=='it':
                    quota_min = ""
                    quota_max = ""
                elif self.L == 'de':
                    quota_min = ""
                    quota_max = ""
                else :
                    quota_min = ""
                    quota_max = ""
                # assegnazione numero di pianta
            resus = self.DB_MANAGER.select_us_from_db_sql(sito, area, us, "2")
            elenco_record = []
            for us in resus:
                elenco_record.append(us)
            if bool(elenco_record):
                sing_rec = elenco_record[0]
                elenco_piante = sing_rec[6]
                if elenco_piante != None:
                    piante = elenco_piante
                else:
                    if self.L=='it':
                        piante = "US disegnata su base GIS" 
                    elif self.L=='de':
                        piante = "SE im GIS gezeichnet" 
                    else:
                        piante= "SU draft on GIS"
            else:
                if self.L=='it':
                    piante = "US disegnata su base GIS" 
                elif self.L=='de':
                    piante = "SE im GIS gezeichnet" 
                else:
                    piante= "SU draft on GIS"
            if self.DATA_LIST[i].quota_min_usm == None:
                quota_min_usm = ""
            else:
                quota_min_usm = str(self.DATA_LIST[i].quota_min_usm)
            if self.DATA_LIST[i].quota_max_usm == None:
                quota_max_usm = ""
            else:
                quota_max_usm = str(self.DATA_LIST[i].quota_max_usm)
            #nuovi campi per Archeo3
            if not self.DATA_LIST[i].quota_relativa:
                quota_relativa = ""  # 55
            else:
                quota_relativa = str(self.DATA_LIST[i].quota_relativa)
            if not self.DATA_LIST[i].quota_abs:
                quota_abs = ""  # 56
            else:
                quota_abs = str(self.DATA_LIST[i].quota_abs)
            if not self.DATA_LIST[i].lunghezza_max:
                lunghezza_max = ""
            else:
                lunghezza_max = str(self.DATA_LIST[i].lunghezza_max)  # 65 lunghezza max
            if not self.DATA_LIST[i].altezza_max:
                altezza_max = ""
            else:
                altezza_max = str(self.DATA_LIST[i].altezza_max)  # 66 altezza max
            if not self.DATA_LIST[i].altezza_min:
                altezza_min = ""
            else:
                altezza_min = str(self.DATA_LIST[i].altezza_min)  # 67 altezza min
            if not self.DATA_LIST[i].profondita_max:
                profondita_max = ""
            else:
                profondita_max = str(self.DATA_LIST[i].profondita_max)  # 68 profondita_max
            if not self.DATA_LIST[i].profondita_min:
                profondita_min = ""
            else:
                profondita_min = str(self.DATA_LIST[i].profondita_min)  # 69 profondita min
            if not self.DATA_LIST[i].larghezza_media:
                larghezza_media = ""
            else:
                larghezza_media = str(self.DATA_LIST[i].larghezza_media)  # 70 larghezza media
            if not self.DATA_LIST[i].quota_max_abs:
                quota_max_abs = ""
            else:
                quota_max_abs = str(self.DATA_LIST[i].quota_max_abs)  # 71 quota_max_abs
            if not self.DATA_LIST[i].quota_max_rel:
                quota_max_rel = ""
            else:
                quota_max_rel = str(self.DATA_LIST[i].quota_max_rel)  # 72 quota_max_rel
            if not self.DATA_LIST[i].quota_min_abs:
                quota_min_abs = ""
            else:
                quota_min_abs = str(self.DATA_LIST[i].quota_min_abs)  # 73 quota_min_abs
            if not self.DATA_LIST[i].quota_min_rel:
                quota_min_rel = ""
            else:
                quota_min_rel = str(self.DATA_LIST[i].quota_min_rel)  # 74 quota_min_rel
            if not self.DATA_LIST[i].lunghezza_usm:
                lunghezza_usm = ""
            else:
                lunghezza_usm = str(self.DATA_LIST[i].lunghezza_usm)  # 85 lunghezza usm
            if not self.DATA_LIST[i].altezza_usm:
                altezza_usm = ""
            else:
                altezza_usm = str(self.DATA_LIST[i].altezza_usm)  # 86 altezza usm
            if not self.DATA_LIST[i].spessore_usm:
                spessore_usm = ""
            else:
                spessore_usm = str(self.DATA_LIST[i].spessore_usm)  # 87 spessore usm
            data_list.append([
                str(self.DATA_LIST[i].sito.replace('_',' ')),  # 0 - Sito
                str(self.DATA_LIST[i].area),  # 1 - Area
                int(self.DATA_LIST[i].us),  # 2 - US
                str(self.DATA_LIST[i].d_stratigrafica),  # 3 - definizione stratigrafica
                str(self.DATA_LIST[i].d_interpretativa),  # 4 - definizione intepretata
                str(self.DATA_LIST[i].descrizione),  # 5 - descrizione
                str(self.DATA_LIST[i].interpretazione),  # 6 - interpretazione
                str(self.DATA_LIST[i].periodo_iniziale),  # 7 - periodo iniziale
                str(self.DATA_LIST[i].fase_iniziale),  # 8 - fase iniziale
                str(self.DATA_LIST[i].periodo_finale),  # 9 - periodo finale iniziale
                str(self.DATA_LIST[i].fase_finale),  # 10 - fase finale
                str(self.DATA_LIST[i].scavato),  # 11 - scavato
                str(self.DATA_LIST[i].attivita),  # 12 - attivita
                str(self.DATA_LIST[i].anno_scavo),  # 13 - anno scavo
                str(self.DATA_LIST[i].metodo_di_scavo),  # 14 - metodo
                str(self.DATA_LIST[i].inclusi),  # 15 - inclusi
                str(self.DATA_LIST[i].campioni),  # 16 - campioni
                str(self.DATA_LIST[i].rapporti),            # 17 - rapporti
                #str(self.DATA_LIST[i].organici),  # organici
                #str(self.DATA_LIST[i].inorganici),  # inorganici
                str(self.DATA_LIST[i].data_schedatura),  # 18 - data schedatura
                str(self.DATA_LIST[i].schedatore),  # 19 - schedatore
                str(self.DATA_LIST[i].formazione),  # 20 - formazione
                str(self.DATA_LIST[i].stato_di_conservazione),  # 21 - conservazione
                str(self.DATA_LIST[i].colore),  # 22 - colore
                str(self.DATA_LIST[i].consistenza),  # 23 - consistenza
                str(self.DATA_LIST[i].struttura),  # 24 - struttura
                str(quota_min),  # 25 - quota_min
                str(quota_max),  # 26 - quota_max
                str(piante),  # 27 - piante CAMPO RICAVATO DA GIS CON VALORI SI/NO
                str(self.DATA_LIST[i].documentazione),  # 28 - documentazione
                #campi USM
                str(self.DATA_LIST[i].unita_tipo),  # 29 - unita tipo
                str(self.DATA_LIST[i].settore),  # 30 - settore
                str(self.DATA_LIST[i].quad_par),  # 31 quadrato
                str(self.DATA_LIST[i].ambient),  # 32 ambiente
                str(self.DATA_LIST[i].saggio),  # 33 saggio
                str(self.DATA_LIST[i].elem_datanti),  # 34 - elem_datanti
                str(self.DATA_LIST[i].funz_statica),  # 35 - funz_statica
                str(self.DATA_LIST[i].lavorazione),  # 36 lavorazione
                str(self.DATA_LIST[i].spess_giunti),  # 37 spess_giunti
                str(self.DATA_LIST[i].letti_posa),            #38 letti posa
                str(self.DATA_LIST[i].alt_mod),               #39  al modulo
                str(self.DATA_LIST[i].un_ed_riass),           #40 unita edilizia riassuntiva
                str(self.DATA_LIST[i].reimp),                 #41 reimpiego
                str(self.DATA_LIST[i].posa_opera),            #42 posa opera
                str(quota_min_usm),                           #43 quota min usm
                str(quota_max_usm),                           #44 quota max usm
                str(self.DATA_LIST[i].cons_legante),          #45 cons legante
                str(self.DATA_LIST[i].col_legante),           #46 col legante
                str(self.DATA_LIST[i].aggreg_legante),        #47 aggreg legante
                str(self.DATA_LIST[i].con_text_mat),          #48  con text mat
                str(self.DATA_LIST[i].col_materiale),         #49  col materiale
                str(self.DATA_LIST[i].inclusi_materiali_usm),  #50 inclusi materili usm
                #NUOVI CAMPI PER ARCHEO3
                str(self.DATA_LIST[i].n_catalogo_generale),  # 51 nr catalogo generale campi aggiunti per archeo 3.0 e allineamento ICCD
                str(self.DATA_LIST[i].n_catalogo_interno),  # 52 nr catalogo interno
                str(self.DATA_LIST[i].n_catalogo_internazionale),  # 53 nr catalogo internazionale
                str(self.DATA_LIST[i].soprintendenza),  # 54 nr soprintendenza
                str(quota_relativa), #55 quota relativa
                str(quota_abs),   #56 quota assoluta
                str(self.DATA_LIST[i].ref_tm),  # 57 ref tm
                str(self.DATA_LIST[i].ref_ra),  # 58 ref ra
                str(self.DATA_LIST[i].ref_n),  # 59 ref n
                str(self.DATA_LIST[i].posizione),  # 60 posizione
                str(self.DATA_LIST[i].criteri_distinzione),  #61 criteri distinzione
                str(self.DATA_LIST[i].modo_formazione),  # 62 modo formazione
                str(self.DATA_LIST[i].componenti_organici),  # 63 componenti organici
                str(self.DATA_LIST[i].componenti_inorganici),  # 64 #  componenti inorganici
                str(lunghezza_max), #65 lunghezza max
                str(altezza_max), #66 altezza max
                str(altezza_min),  #67 altezza min
                str(profondita_max),  #68 profondita max
                str(profondita_min),  #69 profondita min
                str(larghezza_media),  #70 larghezza media
                str(quota_max_abs),   #71 quota max assoluta
                str(quota_max_rel),   #72 quota max rel
                str(quota_min_abs),   #73 quota min assoluta
                str(quota_min_rel),   #74 quota min relativa
                str(self.DATA_LIST[i].osservazioni),  # 75 osservazioni
                str(self.DATA_LIST[i].datazione), # 76 datazione
                str(self.DATA_LIST[i].flottazione),  # 77 flottazione
                str(self.DATA_LIST[i].setacciatura),  # 78 setacciatura
                str(self.DATA_LIST[i].affidabilita),  # 79 affidabilita
                str(self.DATA_LIST[i].direttore_us),  # 80 direttore us
                str(self.DATA_LIST[i].responsabile_us),  # 81 responsabile us
                str(self.DATA_LIST[i].cod_ente_schedatore),  # 82 cod ente schedatore
                str(self.DATA_LIST[i].data_rilevazione),  # 83 data rilevazione
                str(self.DATA_LIST[i].data_rielaborazione),  # 84 data rielaborazione
                str(lunghezza_usm), #85 lunghezza usm
                str(altezza_usm),  #86 altezza usm
                str(spessore_usm),  #87 spessore usm
                str(self.DATA_LIST[i].tecnica_muraria_usm),  # 88 tecnica muraria usm
                str(self.DATA_LIST[i].modulo_usm),  # 89 modulo usm
                str(self.DATA_LIST[i].campioni_malta_usm),  # 90 campioni malta usm
                str(self.DATA_LIST[i].campioni_mattone_usm),  # 91 campioni mattone usm
                str(self.DATA_LIST[i].campioni_pietra_usm),  # 92 campioni pietra usm
                str(self.DATA_LIST[i].provenienza_materiali_usm),  # 93 provenienza_materiali_usm
                str(self.DATA_LIST[i].criteri_distinzione_usm),  # 94 criteri distinzione usm
                str(self.DATA_LIST[i].uso_primario_usm),  #95 uso primario
                str(self.DATA_LIST[i].tipologia_opera),
                str(self.DATA_LIST[i].sezione_muraria),
                str(self.DATA_LIST[i].superficie_analizzata),
                str(self.DATA_LIST[i].orientamento),
                str(self.DATA_LIST[i].materiali_lat),
                str(self.DATA_LIST[i].lavorazione_lat),
                str(self.DATA_LIST[i].consistenza_lat),
                str(self.DATA_LIST[i].forma_lat),
                str(self.DATA_LIST[i].colore_lat),
                str(self.DATA_LIST[i].impasto_lat),
                str(self.DATA_LIST[i].forma_p),
                str(self.DATA_LIST[i].colore_p),
                str(self.DATA_LIST[i].taglio_p),
                str(self.DATA_LIST[i].posa_opera_p),
                str(self.DATA_LIST[i].inerti_usm),
                str(self.DATA_LIST[i].tipo_legante_usm),
                str(self.DATA_LIST[i].rifinitura_usm),
                str(self.DATA_LIST[i].materiale_p),
                str(self.DATA_LIST[i].consistenza_p),
            ])
        return data_list
    def on_pushButton_exp_tavole_pressed(self):
        conn = Connection()
        conn_str = conn.conn_str()
        # QMessageBox.warning(self, "Messaggio", str(conn_str), QMessageBox.Ok)
        PU = Print_utility(self.iface, self.DATA_LIST)
        PU.progressBarUpdated.connect(self.updateProgressBar)
        if conn_str.find("postgresql") == 0:
            PU.first_batch_try("postgres")
        else:
            PU.first_batch_try("sqlite")
    @pyqtSlot(int, int)
    def updateProgressBar(self, tav, tot):
        value = (float(tav) / float(tot)) * 100
        self.progressBar.setValue(value)
        # text = ' di '.join([str(tav), str(tot)])
        # self.countLabel.setText(text)
    def on_pushButton_print_pressed(self):
        if self.L=='it':
            if self.checkBox_s_us.isChecked():
                US_pdf_sheet = generate_US_pdf()
                data_list = self.generate_list_pdf()
                US_pdf_sheet.build_US_sheets(data_list)
                QMessageBox.warning(self, 'Ok',"Esportazione terminata Schede US",QMessageBox.Ok)
            else:   
                pass
            if self.checkBox_e_us.isChecked() :
                US_index_pdf = generate_US_pdf()
                data_list = self.generate_list_pdf()
                try:               
                    if bool(data_list):
                        US_index_pdf.build_index_US(data_list, data_list[0][0])
                        QMessageBox.warning(self, 'Ok',"Esportazione terminata Elenco US",QMessageBox.Ok)
                    else:
                        QMessageBox.warning(self, 'ATTENZIONE',"L'elenco US non può essere esportato devi riempire prima le schede US",QMessageBox.Ok)
                except Exception as e :
                    QMessageBox.warning(self, 'ATTENZIONE',str(e),QMessageBox.Ok)
            else:
                pass
            if self.checkBox_e_foto_t.isChecked():
                US_index_pdf = generate_US_pdf()
                data_list_foto = self.generate_list_foto()
                try:
                        if bool(data_list_foto):
                            US_index_pdf.build_index_Foto(data_list_foto, data_list_foto[0][0])
                            QMessageBox.warning(self, 'Ok',"Esportazione terminata Elenco Foto",QMessageBox.Ok)
                        else:
                            QMessageBox.warning(self, 'ATTENZIONE',"L'elenco foto non può essere esportato perchè non hai immagini taggate.",QMessageBox.Ok)
                except Exception as e :
                    QMessageBox.warning(self, 'ATTENZIONE',str(e),QMessageBox.Ok)
            if self.checkBox_e_foto.isChecked():
                US_index_pdf = generate_US_pdf()
                data_list_foto = self.generate_list_foto()
                try:
                        if bool(data_list_foto):
                            US_index_pdf.build_index_Foto_2(data_list_foto, data_list_foto[0][0])
                            QMessageBox.warning(self, 'Ok',"Esportazione terminata Elenco Foto senza thumbanil",QMessageBox.Ok)
                        else:
                            QMessageBox.warning(self, 'ATTENZIONE',"L'elenco foto non può essere esportato perchè non hai immagini taggate.",QMessageBox.Ok)
                except Exception as e :
                    QMessageBox.warning(self, 'ATTENZIONE',str(e),QMessageBox.Ok)
        elif self.L=='en':  
            if self.checkBox_s_us.isChecked():
                US_pdf_sheet = generate_US_pdf()
                data_list = self.generate_list_pdf()
                US_pdf_sheet.build_US_sheets_en(data_list)
                QMessageBox.warning(self, 'Ok',"Export finished SU Forms",QMessageBox.Ok)
            else:   
                pass
            if self.checkBox_e_us.isChecked() :
                US_index_pdf = generate_US_pdf()
                data_list = self.generate_list_pdf()
                try:               
                    if bool(data_list):
                        US_index_pdf.build_index_US_en(data_list, data_list[0][0])
                        QMessageBox.warning(self, 'Ok',"Export finished SU List",QMessageBox.Ok)
                    else:
                        QMessageBox.warning(self, 'WARNING',"The SU list cannot be exported you have to fill in the SU tabs before",QMessageBox.Ok)
                except Exception as e :
                    QMessageBox.warning(self, 'WARNING',str(e),QMessageBox.Ok)
            else:
                pass
            if self.checkBox_e_foto_t.isChecked():
                US_index_pdf = generate_US_pdf()
                data_list_foto = self.generate_list_foto()
                try:
                        if bool(data_list_foto):
                            US_index_pdf.build_index_Foto_en(data_list_foto, data_list_foto[0][0])
                            QMessageBox.warning(self, 'Ok',"Export finished SU List",QMessageBox.Ok)
                        else:
                            QMessageBox.warning(self, 'WARNING', 'The photo list cannot be exported because you do not have tagged images.',QMessageBox.Ok)
                except Exception as e :
                    QMessageBox.warning(self, 'WARNING',str(e),QMessageBox.Ok)
            if self.checkBox_e_foto.isChecked():
                US_index_pdf = generate_US_pdf()
                data_list_foto = self.generate_list_foto()
                try:
                        if bool(data_list_foto):
                            US_index_pdf.build_index_Foto_2_en(data_list_foto, data_list_foto[0][0])
                            QMessageBox.warning(self, 'Ok', "Export finished Photo List without thumbanil",QMessageBox.Ok)
                        else:
                            QMessageBox.warning(self, 'WARNING', "The photo list cannot be exported because you do not have tagged images.",QMessageBox.Ok)
                except Exception as e :
                    QMessageBox.warning(self, 'WARNING',str(e),QMessageBox.Ok)
        elif self.L=='de':
            if self.checkBox_s_us.isChecked():
                US_pdf_sheet = generate_US_pdf()
                data_list = self.generate_list_pdf()
                US_pdf_sheet.build_US_sheets_de(data_list)
                QMessageBox.warning(self, "Okay", "Export beendet",QMessageBox.Ok)
            else:   
                pass
            if self.checkBox_e_us.isChecked() :
                US_index_pdf = generate_US_pdf()
                data_list = self.generate_list_pdf()
                try:               
                    if bool(data_list):
                        US_index_pdf.build_index_US_de(data_list, data_list[0][0])
                        QMessageBox.warning(self, "Okay", "Export beendet",QMessageBox.Ok)
                    else:
                        QMessageBox.warning(self, 'WARNUNG', 'Die SE-Liste kann nicht exportiert werden, Sie müssen zuerst die SE-Formulare ausfüllen',QMessageBox.Ok)
                except Exception as e :
                    QMessageBox.warning(self, 'WARNUNG',str(e),QMessageBox.Ok)
            else:
                pass
            if self.checkBox_e_foto_t.isChecked():
                US_index_pdf = generate_US_pdf()
                data_list_foto = self.generate_list_foto()
                try:
                        if bool(data_list_foto):
                            US_index_pdf.build_index_Foto_de(data_list_foto, data_list_foto[0][0])
                            QMessageBox.warning(self, "Okay", "Fertige Fotoliste exportieren",QMessageBox.Ok)
                        else:
                            QMessageBox.warning(self, 'WARNUNG', 'Die Fotoliste kann nicht exportiert werden, da Sie keine markierten Bilder haben.',QMessageBox.Ok)
                except Exception as e :
                    QMessageBox.warning(self, 'WARNUNG',str(e),QMessageBox.Ok)
            if self.checkBox_e_foto.isChecked():
                US_index_pdf = generate_US_pdf()
                data_list_foto = self.generate_list_foto()
                try:
                        if bool(data_list_foto):
                            US_index_pdf.build_index_Foto_2_de(data_list_foto, data_list_foto[0][0])
                            QMessageBox.warning(self, 'Ok', 'Fertige Fotoliste ohne Daumenballen exportieren',QMessageBox.Ok)
                        else:
                            QMessageBox.warning(self, 'WARNUNG', 'Die Fotoliste kann nicht exportiert werden, da Sie keine markierten Bilder haben.',QMessageBox.Ok)
                except Exception as e :
                    QMessageBox.warning(self, 'WARNUNG',str(e),QMessageBox.Ok)
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
            
            QMessageBox.information(self, "INFO", "Conversion completed",
                                QMessageBox.Ok)
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e),
                                QMessageBox.Ok)
    
    def setPathdot(self):
        s = QgsSettings()
        dbpath = QFileDialog.getOpenFileName(
            self,
            "Set file name",
            self.MATRIX_PATH,
            " Dot (*.dot)"
        )[0]
        #filename=dbpath.split("/")[-1]
        if dbpath:
            self.lineEdit_input.setText(dbpath)
            s.setValue('',dbpath)
    
    def setPathgraphml(self):
        s = QgsSettings()
        dbpath = QFileDialog.getSaveFileName(
            self,
            "Set file name",
            self.MATRIX_PATH,
            " Graphml (*.graphml)"
        )[0]
        #filename=dbpath.split("/")[-1]
        if dbpath:
            self.lineEdit_output.setText(dbpath)
            s.setValue('',dbpath)
    
    def setDoc_ref(self):
        s = QgsSettings()
        dbpath = QFileDialog.getSaveFileName(
            self,
            "Set file name",
            self.MATRIX_PATH,
            " All files (*.*)"
        )[0]
        filename=dbpath.split("/")[-1]
        if dbpath:
            self.mQgsFileWidget.setText('DosCo\\'+filename)
            s.setValue('',dbpath)
    def list2pipe(self,x):
        lista =[]
        if isinstance(x,str) and x.startswith('[') and '], ['  and ', ' in x:
            
            return ', '.join(str(e) for e in eval(x)).replace("]",'').replace("['Copre',",'').replace("['Coperto da',",'').replace("['Riempie',",'').replace("['Riempito da',",'').replace("['Taglia',",'').replace("['Tagliato da',",'').replace("['Si appoggia a',",'').replace("['Gli si appoggia',",'').replace("['Si lega a',",'').replace("['Uguale a',",'').replace("'",'').replace("Copre,",'').replace("Coperto da,",'').replace("Riempie,",'').replace("Riempito da,",'').replace("Taglia,",'').replace("Tagliato da,",'').replace("Si appoggia a,",'').replace("Gli si appoggia,",'').replace("Si lega a,",'').replace("Uguale a,",'')
        
        
        elif isinstance(x,str) and x.startswith('['):    
            return ', '.join(str(e) for e in eval(x)[0])
        else: 
            return x
    def on_pushButton_graphml_pressed(self):
        # if not bool(self.setPathpdf()):    
            # QMessageBox.warning(self, "INFO", "devi scegliere un file pdf",
                                # QMessageBox.Ok)
        
        dottoxml='{}{}{}'.format(self.BIN, os.sep, 'dottoxml.py')
        try:
            input_file = self.lineEdit_input.text()
            output_file = self.lineEdit_output.text()
            
            python_path = sys.exec_prefix
            python_version = sys.version[:3]

            if platform.system()=='Windows':
                cmd = '{}\python'.format(python_path)
            elif platform.system()=='Darwin':
                cmd = '{}/bin/python{}'.format(python_path, python_version)
            else:
                cmd = '{}/bin/python{}'.format(python_path, python_version)
            subprocess.call(['python', dottoxml,'-f', 'Graphml',input_file, output_file], shell=True)
            
            with open(output_file, 'r') as file :
                filedata = file.read()
            
                # Replace the target string
                filedata = filedata.replace("b'", '')
                filedata = filedata.replace("graphml>'", 'graphml>')
                # Write the file out again
                
            
            with open(output_file, 'w') as file:
              
                file.write(filedata)
                
           
            sito_location = str(self.comboBox_sito.currentText())
            cfg_rel_path = os.path.join(os.sep, 'pyarchinit_DB_folder', 'config.cfg')
            file_path = '{}{}'.format(self.HOME, cfg_rel_path)
            conf = open(file_path, "r")
            data = conf.read()
            settings = Settings(data)
            settings.set_configuration()
            conf.close()    
            
            db_username = settings.USER
            host = settings.HOST
            port = settings.PORT
            database_password=settings.PASSWORD
            db_names = settings.DATABASE
            server=settings.SERVER    
            
            if server=='postgres':
                connessione ="dbname=%s user=%s host=%s password=%s port=%s" % (db_names,db_username,host,database_password,port)
                
                
                conn = psycopg2.connect(connessione)
                cur = conn.cursor()
                # WITH RECURSIVE cte AS (
                  # SELECT id,
                         # SUBSTR(test, 1, STRPOS(test || ';', ';') - 1) col,
                         # SUBSTR(test, STRPOS(test || ';', ';') + 1) rest
                  # FROM (SELECT id, REPLACE(REPLACE(REPLACE(test, '[[', '['), ']]', ']'), '],[', '];[') test FROM tablename) t
                  # UNION ALL
                  # SELECT id,
                         # SUBSTR(rest, 1, STRPOS(rest || ';', ';') - 1),
                         # SUBSTR(rest, STRPOS(rest || ';', ';') + 1)
                  # FROM cte
                  # WHERE LENGTH(rest) > 0
                # )
                # SELECT STRING_AGG(CASE WHEN col LIKE '[''a'',%' OR col LIKE '[''b'',%' THEN col END, ',') x,
                       # STRING_AGG(CASE WHEN col LIKE '[''c'',%' THEN col END, ',') y,
                       # STRING_AGG(CASE WHEN col LIKE '[''d'',%' THEN col END, ',') z
                # FROM cte
                # GROUP BY id
        
            elif server=='sqlite':        
            
                
                sqlite_DB_path = '{}{}{}'.format(self.HOME, os.sep,"pyarchinit_DB_folder")
                
                file_path_sqlite = sqlite_DB_path+os.sep+db_names
                conn = sq.connect(file_path_sqlite)
                conn.enable_load_extension(True)
                
                
                #now we can load the extension
                # depending on your OS and sqlite/spatialite version you might need to add 
                # '.so' (Linux) or '.dll' (Windows) to the extension name

                #mod_spatialite (recommended)
                conn.execute('SELECT load_extension("mod_spatialite")')   
                conn.execute('SELECT InitSpatialMetaData(1);')  
                cur = conn.cursor()
                cur2 = conn.cursor()
                
                name_= '%s' % (sito_location+'_' +  time.strftime('%Y%m%d_') + '.xlsx')
                dump_dir=os.path.join(self.MATRIX_PATH, name_)
                writer = pd.ExcelWriter(dump_dir, engine='xlsxwriter')
                workbook  = writer.book
                
                
                cur.execute("SELECT  area, us, attivita,datazione From us_table where sito='%s' order by rowid;" % sito_location)
                rows1 = cur.fetchall()
                col_names1 = ['Area','US','Attività','Epoca']
                t1=pd.DataFrame(rows1,columns=col_names1).applymap(self.list2pipe)
                t1.to_excel(writer, sheet_name='US',index=False)
                
                cur2.execute("""WITH cte AS 
                    (   SELECT rowid ,
                   SUBSTR(rapporti,  1, INSTR(rapporti || ';', ';') -1) col,
                   SUBSTR(rapporti, INSTR(rapporti || ';', ';') + 1) rest
                   FROM (SELECT rowid, REPLACE(REPLACE(REPLACE(rapporti, '[[', '['), ']]', ']'), '], [', '];[') rapporti FROM us_table
                   WHERE sito = """+"'"+sito_location+"'"+""")
                   UNION all
                   SELECT rowid us,
                   SUBSTR(rest, 1, INSTR(rest || ';', ';')  -1),
                   SUBSTR(rest, INSTR(rest || ';', ';') + 1)   FROM cte   WHERE LENGTH(rest) > 0 )
                   SELECT 
                   GROUP_CONCAT(CASE WHEN col LIKE '[''Copre'',%' OR col LIKE '[''Taglia'',%'
                   OR col LIKE '[''Riempie'',%' OR col LIKE '[''Si appoggia a'',%'  THEN col END) post,
                   
                   GROUP_CONCAT(CASE WHEN col LIKE '[''Coperto da'',%' OR col LIKE '[''Riempito da'',%'
                   OR col LIKE '[''Tagliato da'',%' OR col LIKE '[''Gli si appoggia'',%' THEN col END) ante,
                   
                   GROUP_CONCAT(CASE WHEN col LIKE '[''Si lega a'',%' or col LIKE '[''Uguale a'',%' THEN col END) contemp
            
                    FROM cte GROUP BY rowid order by rowid""")
                rows2 = cur2.fetchall()
                col_names2 = ['Rapporto Posteriore','Rapporto Anteriore', 'Rapporto Contemporaneo']
                t2=pd.DataFrame(rows2,columns=col_names2).applymap(self.list2pipe)
                t2.to_excel(writer, sheet_name='Rapporti',index=False)
                
                worksheet1 = writer.sheets['US']
                worksheet1.set_column('A:A', 30, None)
                worksheet1.set_column('B:B', 30, None)
                worksheet1.set_column('C:C', 30, None)
                worksheet1.set_column('D:D', 30, None)
                worksheet1.set_column('E:E', 30, None)
                
                
                worksheet2 = writer.sheets['Rapporti']
                worksheet2.set_column('A:A', 30, None)
                worksheet2.set_column('B:B', 30, None)
                worksheet2.set_column('C:C', 30, None)
                writer.save()
            QMessageBox.information(self, "INFO", "Conversion completed",
                                    QMessageBox.Ok)
        except KeyError as e:
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
    def on_pushButton_export_matrix_pressed(self):
        if self.checkBox_ED.isChecked():
            
            id_us_dict = {}
            for i in range(len(self.DATA_LIST)):
                id_us_dict[self.DATA_LIST[i].us] = self.DATA_LIST[i].id_us
                
            dlg = pyarchinit_Interactive_Matrix(self.iface, self.DATA_LIST, id_us_dict)
            data_plot=dlg.generate_matrix_2()
            
            # ###interactive matrix###
            # matrix_path = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_Matrix_folder")
            # filename='Harris_matrix2ED_graphml.dot'
            # hm=os.path.join(matrix_path, filename)
            # gv = pgv.AGraph(hm, strict=False, directed=False)
            # dlg.plot_matrix(gv)
            # dlg.exec_()
        if not self.checkBox_ED.isChecked():
            id_us_dict = {}
            for i in range(len(self.DATA_LIST)):
                id_us_dict[self.DATA_LIST[i].us] = self.DATA_LIST[i].id_us
            dlg = pyarchinit_Interactive_Matrix(self.iface, self.DATA_LIST, id_us_dict)
            data_plot=dlg.generate_matrix()
            
            ###interactive matrix###
        # if self.checkBox_IM.isChecked():    
            # matrix_path = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_Matrix_folder")
            # filename='Harris_matrix_tred.dot'
            # hm=os.path.join(matrix_path, filename)
            # gv = pgv.AGraph(hm, strict=False, directed=True)
            # dlg.plot_matrix(gv)
            # dlg.exec_()
    def launch_matrix_exp_if(self, msg):
        if msg == QMessageBox.Ok:
            self.on_pushButton_export_matrix_pressed()
        else:
            pass
    def on_pushButton_orderLayers_pressed(self):
        # QMessageBox.warning(self, 'ATTENZIONE',
        #                     """Il sistema accetta come dataset da elaborare ricerche su singolo SITO e AREA. Se state lanciando il sistema su siti o aree differenti, i dati di siti differenti saranno sovrascritti. Per terminare il sistema dopo l'Ok premere Cancel.""",
        #                     QMessageBox.Ok)
        # self.launch_matrix_exp_if(QMessageBox.warning(self, 'ATTENZIONE',
        #                                               "Si consiglia di lanciare il matrix e controllare se sono presenti paradossi stratigrafici prima di proseguire",
        #                                               QMessageBox.Ok | QMessageBox.Cancel))
        if self.L=='it':
            self.launch_order_layer_if(QMessageBox.warning(self, 'ATTENZIONE',
                                                       "Se saranno presenti paradossi stratigrafici l'order layer non andrà a buon fine",
                                                       QMessageBox.Ok))
        elif self.L=='de':
            self.launch_order_layer_if(QMessageBox.warning(self, 'ACHTUNG',
                                                       "Bist du sicher das du fortfahren möchtest? Wenn aktuell stratigraphische Paradoxa auftauchen Könnte das System zusammenbrechen!",
                                                       QMessageBox.Ok | QMessageBox.Cancel))
        else:
            self.launch_order_layer_if(QMessageBox.warning(self, 'ATTENZIONE',
                                                       "Are you sure you want to go on? If there are stratigraphic paradoxes, the system could crush!",
                                                       QMessageBox.Ok | QMessageBox.Cancel))
    def launch_order_layer_if(self, msg):
        if msg == QMessageBox.Ok:
            # report errori rapporti stratigrafici
            if self.L=='it':
                msg_tipo_rapp = "Manca il tipo di rapporto nell'US: \n"
                msg_nr_rapp = "Manca il numero del rapporto nell'US: \n"
                msg_paradx_rapp = "Paradosso nei rapporti: \n"
                msg_us_mancanti = "Mancano le seguenti schede US presenti nei rapporti: \n"
            elif self.L=='de':
                msg_tipo_rapp = "Der Beziehungstyp fehlt in den SE: \n"
                msg_nr_rapp = "Die Berichtsnummer fehlt in den SE: \n"
                msg_paradx_rapp = "Paradox in Beziehungen: \n"
                msg_us_mancanti = "Folgende SE-formular fehlen in den Berichten: \n"
            else:
                msg_tipo_rapp = "The relationship type is missing in the SU: \n"
                msg_nr_rapp = "The report number is missing in the SU: \n"
                msg_paradx_rapp = "Paradox in relationships: \n"
                msg_us_mancanti = "The following SU forms are missing from the reports: \n"
            # report errori rapporti stratigrafici
            data = []
            # Blocca il sistema di ordinamento su un sito ed area specifci in base alla ricerca eseguita sulla scheda US
            
            
            
            
            
            for sing_rec in self.DATA_LIST:
                us = sing_rec.us
                rapporti_stratigrafici = eval(sing_rec.rapporti)
                # [l.pop(4) for l in rapporti_stratigrafici]
                # [l.pop(3) for l in rapporti_stratigrafici]
                # [l.pop(2) for l in rapporti_stratigrafici]
                
                for sing_rapp in rapporti_stratigrafici:
                    
                    
                    if len(sing_rapp) !=2:##cambiato da 2 a 5
                        if self.L=='it':
                            msg_nr_rapp = msg_nr_rapp + str(sing_rapp[0]) + "relativo a: " + str(us) + " \n"
                        elif self.L=='de':
                            msg_nr_rapp = msg_nr_rapp + str(sing_rapp[0]) + "bezüglich: " + str(us) + " \n"
                        else:
                            msg_nr_rapp = msg_nr_rapp + str(sing_rapp[0]) + "concerning: " + str(us) + " \n"
                    try:
                        if sing_rapp[0] == 'Cuts' or  sing_rapp[0] == 'Covers' or  sing_rapp[0] == 'Abuts' or  sing_rapp[0] == 'Fills' or sing_rapp[0] == 'Taglia' or  sing_rapp[0] == 'Copre' or  sing_rapp[0] == 'Si appoggia a' or  sing_rapp[0] == 'Riempie'  or  sing_rapp[0] == 'Schneidet' or  sing_rapp[0] == 'Liegt über' or  sing_rapp[0] == 'Stützt sich auf' or  sing_rapp[0] == 'Verfüllt':
                            try:
                                if sing_rapp[1] != '':
                                    harris_rapp = (int(us), int(sing_rapp[1]))
                                    ##                                  if harris_rapp== (1, 67):
                                    ##                                      QMessageBox.warning(self, "Messaggio", "Magagna", QMessageBox.Ok)
                                    data.append(harris_rapp)
                            except:
                                msg_nr_rapp = msg_nr_rapp + str(us) + " \n"
                    except:
                        msg_tipo_rapp = msg_tipo_rapp + str(us) + " \n"
            for i in data:
                temp_tup = (i[1], i[
                    0])  # controlla che nn vi siano rapporti inversi dentro la lista DA PROBLEMI CON GLI UGUALE A E I SI LEGA A
                # QMessageBox.warning(self, "Messaggio", "Temp_tup" + str(temp_tup), QMessageBox.Ok)
                if data.count(temp_tup) != 0:
                    msg_paradx_rapp = msg_paradx_rapp + '\n' + str(i) + '\n' + str(temp_tup)
                    data.remove(i)
                    # OK
                    ## QMessageBox.warning(self, "Messaggio", "DATA LIST" + str(data), QMessageBox.Ok)
                    # Blocca il sistema di ordinamento su un sito ed area specifci in base alla ricerca eseguita sulla scheda US
            
            
            sito = self.DATA_LIST[0].sito  # self.comboBox_sito_rappcheck.currentText()
            area = self.DATA_LIST[0].area  # self.comboBox_area.currentText()
            # script order layer from pyqgis
            OL = Order_layer_v2(self.DB_MANAGER, sito, area)
            # QMessageBox.warning(None, "Messaggio", "DATA LIST" + str(OL), QMessageBox.Ok)
            order_layer_dict = OL.main_order_layer()
            #QMessageBox.warning(None, "Messaggio", "DATA LIST" + str(order_layer_dict), QMessageBox.Ok)
            # order_number = ""
            # us = ""
            for k, v in order_layer_dict.items():#era iteritems prima 
                order_number = str(k)
                us = v
                # QMessageBox.warning(None, "Messaggio", "DATA LIST" + str(k)+str(v), QMessageBox.Ok)
                for sing_us in v:
                    search_dict = {'sito': "'"+str(sito)+"'", 'area': "'"+str(area)+"'",
                                   'us': int(sing_us)}
                    #QMessageBox.warning(None, "Messaggio", "DATA LIST" + str(search_dict), QMessageBox.Ok)
                    try:
                        records = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)  # carica tutti i dati di uno scavo ordinati per numero di US
                        #QMessageBox.warning(None, "Messaggio", "records" + str(records), QMessageBox.Ok)
                        a= self.DB_MANAGER.update(self.MAPPER_TABLE_CLASS, self.ID_TABLE, [int(records[0].id_us)], ['order_layer'], [order_number])
                        #QMessageBox.warning(None, "Messaggio", "records" + str(a), QMessageBox.Ok)
                        self.on_pushButton_view_all_pressed()
                    except Exception as e:
                        QMessageBox.warning(self, u'ACHTUNG', str(e), QMessageBox.Ok)
            # blocco output errori
            if self.L=='it':
                filename_tipo_rapporti_mancanti = '{}{}{}'.format(self.REPORT_PATH, os.sep, 'tipo_rapporti_mancanti.txt')
                filename_nr_rapporti_mancanti = '{}{}{}'.format(self.REPORT_PATH, os.sep, 'nr_rapporti_mancanti.txt')
                filename_paradosso_rapporti = '{}{}{}'.format(self.REPORT_PATH, os.sep, 'paradosso_rapporti.txt')
                filename_us_mancanti = '{}{}{}'.format(self.REPORT_PATH, os.sep, 'us_mancanti.txt')
            elif self.L=='de':
                filename_tipo_rapporti_mancanti = '{}{}{}'.format(self.REPORT_PATH, os.sep, 'type_missing_relationships.txt')
                filename_nr_rapporti_mancanti = '{}{}{}'.format(self.REPORT_PATH, os.sep, 'nr_missing relashionships.txt')
                filename_paradosso_rapporti = '{}{}{}'.format(self.REPORT_PATH, os.sep, 'relashionships_paradox.txt')
                filename_us_mancanti = '{}{}{}'.format(self.REPORT_PATH, os.sep, 'su_missing.txt')
            else:
                filename_tipo_rapporti_mancanti = '{}{}{}'.format(self.REPORT_PATH, os.sep, 'type_missing_relationships.txt')
                filename_nr_rapporti_mancanti = '{}{}{}'.format(self.REPORT_PATH, os.sep, 'nr_missing relashionships.txt')
                filename_paradosso_rapporti = '{}{}{}'.format(self.REPORT_PATH, os.sep, 'relashionships_paradox.txt')
                filename_us_mancanti = '{}{}{}'.format(self.REPORT_PATH, os.sep, 'su_missing.txt')
            self.testing(filename_tipo_rapporti_mancanti, str(msg_tipo_rapp))
            self.testing(filename_nr_rapporti_mancanti, str(msg_nr_rapp))
            self.testing(filename_paradosso_rapporti, str(msg_paradx_rapp))
            self.testing(filename_us_mancanti, str(msg_us_mancanti))
            if self.L=='it':
                QMessageBox.warning(self, u'ATTENZIONE', u"Sistema di ordinamento Terminato", QMessageBox.Ok)
            elif self.L=='de':
                QMessageBox.warning(self, u'ACHTUNG', "Ordnungssystem beendet", QMessageBox.Ok)
            else:
                QMessageBox.warning(self, u'WARNING', "Sorting system Complete", QMessageBox.Ok)
        else:
            if self.L=='it':
                QMessageBox.warning(self, u'ATTENZIONE', u"Sistema di ordinamento US abortito", QMessageBox.Ok)
            elif self.L=='de':
                QMessageBox.warning(self, 'ACHTUNG', u"Ordnungssystem verlassen", QMessageBox.Ok)
            else:
                QMessageBox.warning(self, 'WARNING', "SU aborted sorting system", QMessageBox.Ok)
           # blocco output errori
    def on_toolButtonPan_toggled(self):
        self.toolPan = QgsMapToolPan(self.mapPreview)
        self.mapPreview.setMapTool(self.toolPan)
    def on_pushButton_showSelectedFeatures_pressed(self):
        # field_position = self.pyQGIS.findFieldFrDict(self.ID_TABLE) #ricava la posizione del campo
        try:
            layer = self.iface.mapCanvas().currentLayer()
            fieldname = self.ID_TABLE
            if not layer:
                if self.L=='it':
                    QMessageBox.warning(self, 'ATTENZIONE', "Nessun elemento selezionato", QMessageBox.Ok)
                elif self.L=='de':
                    QMessageBox.warning(self, 'ACHTUNG', "keine Elemente ausgewählt", QMessageBox.Ok)
                else:
                    QMessageBox.warning(self, 'WARNING', "No items selected", QMessageBox.Ok)
            features_list = layer.selectedFeatures()
            field_position = ""
            for single in layer.getFeatures():
                field_position = single.fieldNameIndex(fieldname)
            id_list = []
            for feat in features_list:
                attr_list = feat.attributes()
                id_list.append(attr_list[field_position])
                # viene impostata la query per il database
            items, order_type = [self.ID_TABLE], "asc"
            self.empty_fields()
            self.DATA_LIST = []
            temp_data_list = self.DB_MANAGER.query_sort(id_list, items, order_type, self.MAPPER_TABLE_CLASS, self.ID_TABLE)
            for us in temp_data_list:
                self.DATA_LIST.append(us)
                # vengono riempiti i campi con i dati trovati
            self.fill_fields()
            self.BROWSE_STATUS = 'b'
            self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
            if type(self.REC_CORR) == "<type 'str'>":
                corr = 0
            else:
                corr = self.REC_CORR
            self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
            self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
            self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
        except Exception as e:
            QMessageBox.warning(self, 'ATTENZIONE', str(e), QMessageBox.Ok)
    
    def on_pushButton_sort_pressed(self):
        self.checkBox_query.setChecked(False)
        if self.checkBox_query.isChecked():
            self.model_a.database().close()
        if self.check_record_state() == 1:
            pass
        else:
            dlg = SortPanelMain(self)
            dlg.insertItems(self.SORT_ITEMS)
            dlg.exec_()
            items, order_type = dlg.ITEMS, dlg.TYPE_ORDER
            self.SORT_ITEMS_CONVERTED = []
            for i in items:
                # QMessageBox.warning(self, "Messaggio",i, QMessageBox.Ok)
                self.SORT_ITEMS_CONVERTED.append(
                    self.CONVERSION_DICT[str(i)])  # apportare la modifica nellle altre schede
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
            self.BROWSE_STATUS = 'b'
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
    # def on_toolButtonPreviewMedia_toggled(self):
        # if self.L=='it':
            # if self.toolButtonPreviewMedia.isChecked() == True:
                # QMessageBox.warning(self, "Messaggio",
                                    # "Modalita' Preview Media US attivata. Le immagini delle US saranno visualizzate nella sezione Media",
                                    # QMessageBox.Ok)
                # self.loadMediaPreview()
            # else:
                # self.loadMediaPreview(1)
        # elif self.L=='de':
            # if self.toolButtonPreviewMedia.isChecked()== True:
                # QMessageBox.warning(self, "Message",
                                    # "Modalität' Preview Media SE aktiviert. Die Bilder der SE werden in der Preview media Auswahl visualisiert",
                                    # QMessageBox.Ok)
                # self.loadMediaPreview()
            # else:
                # self.loadMediaPreview(1)
        # else:
            # if self.toolButtonPreviewMedia.isChecked()== True:
                # QMessageBox.warning(self, "Message",
                                    # "SU Media Preview mode enabled. US images will be displayed in the Media section",
                                    # QMessageBox.Ok)
                # self.loadMediaPreview()
            # else:
                # self.loadMediaPreview(1)        
    def on_pushButton_addRaster_pressed(self):
        if self.toolButtonGis.isChecked():
            self.pyQGIS.addRasterLayer()
    def on_pushButton_new_rec_pressed(self):
        conn = Connection()
        
        sito_set= conn.sito_set()
        sito_set_str = sito_set['sito_set']
        if bool(self.DATA_LIST):
            if self.data_error_check() == 1:
                pass
            # else:
                # if self.BROWSE_STATUS == "b":
                    # if self.DATA_LIST:
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
                
                self.setComboBoxEditable(["self.comboBox_area"], 1)
                self.setComboBoxEditable(["self.comboBox_unita_tipo"], 1)
                self.setComboBoxEnable(["self.comboBox_sito"], False)
                self.setComboBoxEnable(["self.comboBox_area"], True)
                self.setComboBoxEnable(["self.lineEdit_us"], True)
                self.setComboBoxEnable(["self.comboBox_unita_tipo"], True)
                self.SORT_STATUS = "n"
                self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.set_rec_counter('', '')
                self.label_sort.setText(self.SORTED_ITEMS["n"])
                
            else:
                self.BROWSE_STATUS = "n"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.empty_fields()
                self.setComboBoxEditable(["self.comboBox_sito"], 1)
                self.setComboBoxEditable(["self.comboBox_area"], 1)
                self.setComboBoxEditable(["self.comboBox_unita_tipo"], 1)
                self.setComboBoxEnable(["self.comboBox_sito"], "True")
                self.setComboBoxEnable(["self.comboBox_area"], "True")
                self.setComboBoxEnable(["self.lineEdit_us"], "True")
                self.setComboBoxEnable(["self.comboBox_unita_tipo"], "True")
                self.SORT_STATUS = "n"
                self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
                
                self.set_rec_counter('', '')
                self.label_sort.setText(self.SORTED_ITEMS["n"])
                
            
            self.enable_button(0)
    
    def save_rapp(self):
        
        
        self.checkBox_query.setChecked(False)
        if self.checkBox_query.isChecked():
            self.model_a.database().close()
        if self.BROWSE_STATUS == "b":
            if self.data_error_check() == 0:
                if self.records_equal_check() == 1:
                    
                    if self.update_if(QMessageBox.Ok):
                        QMessageBox.Ok
                        
                    
                    # self.empty_fields()
                    # self.SORT_STATUS = "n"
                    # self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
                    # self.enable_button(1)
                    
                    # self.fill_fields(self.REC_CORR)
                # else:
                    # if self.L=='it':
                        # QMessageBox.warning(self, "ATTENZIONE", "Non è stata realizzata alcuna modifica.", QMessageBox.Ok)
                    # elif self.L=='de':
                        # QMessageBox.warning(self, "ACHTUNG", "Keine Änderung vorgenommen", QMessageBox.Ok)
                    # else:
                        # QMessageBox.warning(self, "Warning", "No changes have been made", QMessageBox.Ok)       
        # else:
            # if self.data_error_check() == 0:
                # test_insert = self.insert_new_rec()
                # if test_insert == 1:
                    # self.empty_fields()
                    # self.SORT_STATUS = "n"
                    # self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
                    # self.charge_records()
                    # self.charge_list()
                    # self.set_sito()
                    # self.BROWSE_STATUS = "b"
                    # self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    # self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), len(self.DATA_LIST) - 1
                    # self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
                    # self.setComboBoxEditable(["self.comboBox_sito"], 1)
                    # self.setComboBoxEditable(["self.comboBox_area"], 1)
                    # self.setComboBoxEditable(["self.comboBox_unita_tipo"], 1)
                    # self.setComboBoxEnable(["self.comboBox_sito"], "False")
                    # self.setComboBoxEnable(["self.comboBox_area"], "False")
                    # self.setComboBoxEnable(["self.lineEdit_us"], "False")
                    # self.setComboBoxEnable(["self.comboBox_unita_tipo"], "True")
                    # self.fill_fields(self.REC_CORR)
                    # self.enable_button(1)
            # else:
                # if self.L=='it':
                    # QMessageBox.warning(self, "ATTENZIONE", "Problema nell'inserimento dati", QMessageBox.Ok)
                # elif self.L=='de':
                    # QMessageBox.warning(self, "ACHTUNG", "Problem der Dateneingabe", QMessageBox.Ok)
                # else:
                    # QMessageBox.warning(self, "Warning", "Problem with data entry", QMessageBox.Ok) 
    def on_pushButton_save_pressed(self):
        
        
        self.checkBox_query.setChecked(False)
        if self.checkBox_query.isChecked():
            self.model_a.database().close()
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
                    self.setComboBoxEditable(["self.comboBox_sito"], 1)
                    self.setComboBoxEditable(["self.comboBox_area"], 1)
                    self.setComboBoxEditable(["self.comboBox_unita_tipo"], 1)
                    self.setComboBoxEnable(["self.comboBox_sito"], "False")
                    self.setComboBoxEnable(["self.comboBox_area"], "False")
                    self.setComboBoxEnable(["self.lineEdit_us"], "False")
                    self.setComboBoxEnable(["self.comboBox_unita_tipo"], "True")
                    self.fill_fields(self.REC_CORR)
                    self.enable_button(1)
            else:
                if self.L=='it':
                    QMessageBox.warning(self, "ATTENZIONE", "Problema nell'inserimento dati", QMessageBox.Ok)
                elif self.L=='de':
                    QMessageBox.warning(self, "ACHTUNG", "Problem der Dateneingabe", QMessageBox.Ok)
                else:
                    QMessageBox.warning(self, "Warning", "Problem with data entry", QMessageBox.Ok) 
    def on_pushButton_rapp_check_pressed(self):
        sito_check = str(self.comboBox_sito_rappcheck.currentText())
        area_check = str(self.comboBox_area_rappcheck.currentText())
        try:
            self.rapporti_stratigrafici_check(sito_check, area_check)
            self.def_strati_to_rapporti_stratigrafici_check(sito_check, area_check)  # SPERIMENTALE
        except Exception as e:
            QMessageBox.warning(self, "Initial Message", str(e), QMessageBox.Ok)
        else:
            if self.L=='it':
                QMessageBox.warning(self, "Messaggio",
                                    "Controllo Rapporti Stratigrafici. \n Controllo eseguito con successo", QMessageBox.Ok)
            elif self.L=='de':
                QMessageBox.warning(self, "Message",
                                    "Prüfen der stratigraphischen Beziehung.  Kontrolle erfolgereich", QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "Message",
                                    "Monitoring of stratigraphic relationships. \n Control performed successfully", QMessageBox.Ok)                     
    
    def on_pushButton_h_check_pressed(self):
        self.listWidget_rapp.clear()
        sito_check = str(self.comboBox_sito.currentText())
        area_check = str(self.comboBox_area.currentText())
        try:
            
            self.rapporti_stratigrafici_check(sito_check, area_check)
            self.def_strati_to_rapporti_stratigrafici_check(sito_check, area_check)  # SPERIMENTALE
            self.periodi_to_rapporti_stratigrafici_check(sito_check, area_check)
            self.automaticform_check(sito_check, area_check)
        except Exception as e:
            self.listWidget_rapp.addItem(str(e))
        else:
            if self.L=='it':
                self.listWidget_rapp.addItem("Controllo Rapporti Stratigrafici.\nControllo eseguito con successo.")
            elif self.L=='de':
                Qself.listWidget_rapp.addItem("Prüfen der stratigraphischen Beziehung.  Kontrolle erfolgereich")
            else:
                self.listWidget_rapp.addItem("Monitoring of stratigraphic relationships. \n Control performed successfully")  
    
    
    def data_error_check(self):
        test = 0
        EC = Error_check()
        if self.L=='it':
            if EC.data_is_empty(str(self.comboBox_sito.currentText())) == 0:
                QMessageBox.warning(self, "ATTENZIONE", "Campo Sito. \n Il campo non deve essere vuoto", QMessageBox.Ok)
                test = 1
            if EC.data_is_empty(str(self.comboBox_area.currentText())) == 0:
                QMessageBox.warning(self, "ATTENZIONE", "Campo Area. \n Il campo non deve essere vuoto", QMessageBox.Ok)
                test = 1
            if EC.data_is_empty(str(self.lineEdit_us.text())) == 0:
                QMessageBox.warning(self, "ATTENZIONE", "Campo US. \n Il campo non deve essere vuoto", QMessageBox.Ok)
                test = 1
            if EC.data_is_empty(str(self.comboBox_unita_tipo.currentText())) == 0:
                QMessageBox.warning(self, "ATTENZIONE", "Campo Tipo US/USM. \n Il campo non deve essere vuoto",
                                    QMessageBox.Ok)
                test = 1
            """controllo campi numerici"""
            area = self.comboBox_area.currentText()
            us = self.lineEdit_us.text()
            if area != "":
                if EC.data_is_int(area) == 0:
                    QMessageBox.warning(self, "ATTENZIONE", "Campo Area. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1
            if us != "" :
                if EC.data_is_int(us) == 0:
                    QMessageBox.warning(self, "ATTENZIONE", "Campo US. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.Ok)
                    test = 1
            """controllo campi numerici float"""
            #TAB USM
            spessore_usm = self.lineEdit_spessore_usm.text()
            qmin_usm = self.lineEdit_qmin_usm.text()
            qmax_usm = self.lineEdit_qmax_usm.text()
            lunghezza_usm = self.lineEdit_lunghezza_usm.text()
            altezza_usm = self.lineEdit_altezza_usm.text()
            #TAB MISURE
            quota_abs = self.lineEdit_quota_abs.text()
            quota_relativa = self.lineEdit_quota_relativa.text()
            quota_max_abs = self.lineEdit_quota_max_abs.text()
            quota_max_rel = self.lineEdit_quota_max_rel.text()
            quota_min_abs = self.lineEdit_quota_min_abs.text()
            quota_min_rel = self.lineEdit_quota_min_rel.text()
            larghezza_media = self.lineEdit_larghezza_media.text()
            lunghezza_max = self.lineEdit_lunghezza_max.text()
            profondita_min = self.lineEdit_profondita_min.text()
            profondita_max = self.lineEdit_profondita_max.text()
            altezza_max = self.lineEdit_altezza_max.text()
            altezza_min = self.lineEdit_altezza_min.text()
            if spessore_usm != "":
                if EC.data_is_float(spessore_usm) == 0:
                    QMessageBox.warning(self, "ATTENZIONE", "Campo USM-Spessore USM. \n Il valore deve essere di tipo numerico. \n (Sono stati inserite lettere, virgole, accenti o caratteri non numerici.",
                                        QMessageBox.Ok)
                    test = 1
            if qmin_usm != "":
                if EC.data_is_float(qmin_usm) == 0:
                    QMessageBox.warning(self, "ATTENZIONE", "Campo USM 3-Quota minima USM. \n Il valore deve essere di tipo numerico. \n (Sono stati inserite lettere, virgole, accenti o caratteri non numerici.",
                                        QMessageBox.Ok)
                    test = 1
            if qmax_usm != "":
                if EC.data_is_float(qmax_usm) == 0:
                    QMessageBox.warning(self, "ATTENZIONE", "Campo USM 3-Quota max USM. \n Il valore deve essere di tipo numerico. \n (Sono stati inserite lettere, virgole, accenti o caratteri non numerici.",
                                        QMessageBox.Ok)
                    test = 1
            if lunghezza_usm != "":
                if EC.data_is_float(lunghezza_usm) == 0:
                    QMessageBox.warning(self, "ATTENZIONE", "Campo USM 3-Lunghezza USM. \n Il valore deve essere di tipo numerico. \n (Sono stati inserite lettere, virgole, accenti o caratteri non numerici.",
                                        QMessageBox.Ok)
                    test = 1
            if altezza_usm != "":
                if EC.data_is_float(altezza_usm) == 0:
                    QMessageBox.warning(self, "ATTENZIONE", "Campo USM 3-Altezza USM. \n Il valore deve essere di tipo numerico. \n (Sono stati inserite lettere, virgole, accenti o caratteri non numerici.",
                                        QMessageBox.Ok)
                    test = 1
            ###########################
            if quota_abs != "":
                if EC.data_is_float(quota_abs) == 0:
                    QMessageBox.warning(self, "ATTENZIONE", "Campo Quota Assoluta. \n Il valore deve essere di tipo numerico. \n (Sono stati inserite lettere, virgole, accenti o caratteri non numerici.",
                                        QMessageBox.Ok)
                    test = 1
            if quota_relativa != "":
                if EC.data_is_float(quota_relativa) == 0:
                    QMessageBox.warning(self, "ATTENZIONE", "Campo Quota Relativa. \n Il valore deve essere di tipo numerico. \n (Sono stati inserite lettere, virgole, accenti o caratteri non numerici.",
                                        QMessageBox.Ok)
                    test = 1
            if quota_max_abs != "":
                if EC.data_is_float(quota_max_abs) == 0:
                    QMessageBox.warning(self, "ATTENZIONE", "Campo Quota Massima Assoluta. \n Il valore deve essere di tipo numerico. \n (Sono stati inserite lettere, virgole, accenti o caratteri non numerici.",
                                        QMessageBox.Ok)
                    test = 1
            if quota_max_rel != "":
                if EC.data_is_float(quota_max_rel) == 0:
                    QMessageBox.warning(self, "ATTENZIONE", "Campo Quota Massima Relativa. \n Il valore deve essere di tipo numerico. \n (Sono stati inserite lettere, virgole, accenti o caratteri non numerici.",
                                        QMessageBox.Ok)
                    test = 1
            if quota_min_abs != "":
                if EC.data_is_float(quota_min_abs) == 0:
                    QMessageBox.warning(self, "ATTENZIONE", "Campo Quota Minima Assoluta. \n Il valore deve essere di tipo numerico. \n (Sono stati inserite lettere, virgole, accenti o caratteri non numerici.",
                                        QMessageBox.Ok)
                    test = 1
            if quota_min_rel != "":
                if EC.data_is_float(quota_min_rel) == 0:
                    QMessageBox.warning(self, "ATTENZIONE", "Campo Quota Minima Relativa. \n Il valore deve essere di tipo numerico. \n (Sono stati inserite lettere, virgole, accenti o caratteri non numerici.",
                                        QMessageBox.Ok)
                    test = 1
            if larghezza_media != "":
                if EC.data_is_float(larghezza_media) == 0:
                    QMessageBox.warning(self, "ATTENZIONE", "Campo Larghezza Media. \n Il valore deve essere di tipo numerico. \n (Sono stati inserite lettere, virgole, accenti o caratteri non numerici.",
                                        QMessageBox.Ok)
                    test = 1
            if lunghezza_max != "":
                if EC.data_is_float(lunghezza_max) == 0:
                    QMessageBox.warning(self, "ATTENZIONE", "Campo Lunghezza Massima. \n Il valore deve essere di tipo numerico. \n (Sono stati inserite lettere, virgole, accenti o caratteri non numerici.",
                                        QMessageBox.Ok)
                    test = 1
            if profondita_min != "":
                if EC.data_is_float(profondita_min) == 0:
                    QMessageBox.warning(self, "ATTENZIONE", "Campo Profondità Minima. \n Il valore deve essere di tipo numerico. \n (Sono stati inserite lettere, virgole, accenti o caratteri non numerici.",
                                        QMessageBox.Ok)
                    test = 1
            if profondita_max != "":
                if EC.data_is_float(profondita_max) == 0:
                    QMessageBox.warning(self, "ATTENZIONE", "Campo Profondità Massima. \n Il valore deve essere di tipo numerico. \n (Sono stati inserite lettere, virgole, accenti o caratteri non numerici.",
                                        QMessageBox.Ok)
                    test = 1
            if altezza_max != "":
                if EC.data_is_float(altezza_max) == 0:
                    QMessageBox.warning(self, "ATTENZIONE", "Campo Spessore. \n Il valore deve essere di tipo numerico. \n (Sono stati inserite lettere, virgole, accenti o caratteri non numerici.",
                                        QMessageBox.Ok)
                    test = 1
            if altezza_min != "":
                if EC.data_is_float(altezza_min) == 0:
                    QMessageBox.warning(self, "ATTENZIONE", "Campo Spessore Minima. \n Il valore deve essere di tipo numerico. \n (Sono stati inserite lettere, virgole, accenti o caratteri non numerici.",
                                        QMessageBox.Ok)
                    test = 1
            """controllo lunghezza campo alfanumerico"""
            attivita = self.lineEdit_attivita.text()
            colore = self.comboBox_colore.currentText()
            anno_scavo = self.lineEdit_anno.text()
            formazione = self.comboBox_formazione.currentText()
            stato_conservazione = self.comboBox_conservazione.currentText()
            colore = self.comboBox_colore.currentText()
            consistenza = self.comboBox_consistenza.currentText()
            struttura = self.comboBox_struttura.currentText()
            cont_per = self.lineEdit_codice_periodo.text()
            d_interpretativa=self.comboBox_def_intepret.currentText()
            d_stratigrafica=self.comboBox_def_strat.currentText()
            if attivita != "":
                if EC.data_lenght(attivita, 3) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Campo Attivita. \n Il valore non deve superare i 4 caratteri alfanumerici",
                                        QMessageBox.Ok)
                    test = 1
            # if anno_scavo != "":
            # if EC.data_lenght(anno_scavo,3) == 0:
            #       QMessageBox.warning(self, "ATTENZIONE", "Campo Anno. \n immettere una sola data (es. 2014)",  QMessageBox.Ok)
            #       test = 1
            
            if formazione != "":
                if EC.data_lenght(d_interpretativa, 254) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Campo definizione interpreta. \n Il valore non deve superare i 255 caratteri alfanumerici",
                                        QMessageBox.Ok)
                    test = 1
            
            if formazione != "":
                if EC.data_lenght(d_stratigrafica, 254) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Campo definizione stratigrafica. \n Il valore non deve superare i 255 caratteri alfanumerici",
                                        QMessageBox.Ok)
                    test = 1
            
            if formazione != "":
                if EC.data_lenght(formazione, 19) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Campo Formazione. \n Il valore non deve superare i 20 caratteri alfanumerici",
                                        QMessageBox.Ok)
                    test = 1
            if stato_conservazione != "":
                if EC.data_lenght(stato_conservazione, 19) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Campo Conservazione. \n Il valore non deve superare i 20 caratteri alfanumerici",
                                        QMessageBox.Ok)
                    test = 1
            if colore != "":
                if EC.data_lenght(colore, 19) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Campo Colore. \n Il valore non deve superare i 20 caratteri alfanumerici",
                                        QMessageBox.Ok)
                    test = 1
            if consistenza != "":
                if EC.data_lenght(consistenza, 19) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Campo Consistenza. \n Il valore non deve superare i 20 caratteri alfanumerici",
                                        QMessageBox.Ok)
                    test = 1
            if struttura != "":
                if EC.data_lenght(struttura, 29) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Campo Struttura. \n Il valore non deve superare i 30 caratteri alfanumerici",
                                        QMessageBox.Ok)
                    test = 1
        elif self.L=='de':
            if EC.data_is_empty(str(self.comboBox_sito.currentText())) == 0:
                QMessageBox.warning(self, "ACHTUNG", " Feld Ausgrabungstätte. \n Das Feld darf nicht leer sein", QMessageBox.Ok)
                test = 1
            if EC.data_is_empty(str(self.comboBox_area.currentText())) == 0:
                QMessageBox.warning(self, "ACHTUNG", "Feld Areal. \n Das Feld darf nicht leer sein", QMessageBox.Ok)
                test = 1
            if EC.data_is_empty(str(self.lineEdit_us.text())) == 0:
                QMessageBox.warning(self, "ACHTUNG", "Feld SE. \n Das Feld darf nicht leer sein", QMessageBox.Ok)
                test = 1
            if EC.data_is_empty(str(self.comboBox_unita_tipo.currentText())) == 0:
                QMessageBox.warning(self, "ACHTUNG", "Feld SE/MSE Typ. \n Das Feld darf nicht leer sein",   QMessageBox.Ok)
                test = 1
            area = self.comboBox_area.currentText()
            us = self.lineEdit_us.text()
            attivita = self.lineEdit_attivita.text()
            colore = self.comboBox_colore.currentText()
            anno_scavo = self.lineEdit_anno.text()
            formazione = self.comboBox_formazione.currentText()
            stato_conservazione = self.comboBox_conservazione.currentText()
            colore = self.comboBox_colore.currentText()
            consistenza = self.comboBox_consistenza.currentText()
            struttura = self.comboBox_struttura.currentText()
            cont_per = self.lineEdit_codice_periodo.text()
            if area != "":
                if EC.data_is_int(area) == 0:
                    QMessageBox.warning(self, "ACHTUNG", "Feld Areal. \n Der Wert muss numerisch eingegeben werden",
                                        QMessageBox.Ok)
                    test = 1
            if us != "":
                if EC.data_is_int(us) == 0:
                    QMessageBox.warning(self, "ACHTUNG", "Feld SE. \n Der Wert muss numerisch eingegeben werden",
                                        QMessageBox.Ok)
                    test = 1
            if attivita != "":
                if EC.data_lenght(attivita, 3) == 0:
                    QMessageBox.warning(self, "ACHTUNG",
                                        "Feld aktiviert. \n Der Wert darf nicht mehr als 4 alphanumerische Zeichen enthalten",
                                        QMessageBox.Ok)
                    test = 1
                    # if anno_scavo != "":
            # if EC.data_lenght(anno_scavo,3) == 0:
            #       QMessageBox.warning(self, "ATTENZIONE", "Campo Anno. \n immettere una sola data (es. 2014)",  QMessageBox.Ok)
            #       test = 1
            if formazione != "":
                if EC.data_lenght(formazione, 19) == 0:
                    QMessageBox.warning(self, "ACHTUNG",
                                        "Feld Bodenart. \n Der Wert darf nicht mehr als 20 alphanumerische Zeichen enthalten",
                                        QMessageBox.Ok)
                    test = 1
            if stato_conservazione != "":
                if EC.data_lenght(stato_conservazione, 19) == 0:
                    QMessageBox.warning(self, "ACHTUNG",
                                        "Feld Erhaltungszustand.  Der Wert darf nicht mehr als 20 alphanumerische Zeichen enthalten",
                                        QMessageBox.Ok)
                    test = 1
            if colore != "":
                if EC.data_lenght(colore, 19) == 0:
                    QMessageBox.warning(self, "ACHTUNG",
                                        "Feld Farbe. \n Der Wert darf nicht mehr als 20 alphanumerische Zeichen enthalten",
                                        QMessageBox.Ok)
                    test = 1
            if consistenza != "":
                if EC.data_lenght(consistenza, 19) == 0:
                    QMessageBox.warning(self, "ACHTUNG",
                                        "Feld Konsistenz. \n Der Wert darf nicht mehr als 20 alphanumerische Zeichen enthalten",
                                        QMessageBox.Ok)
                    test = 1
            if struttura != "":
                if EC.data_lenght(struttura, 29) == 0:
                    QMessageBox.warning(self, "ACHTUNG",
                                        "Feld Struktur. \n Der Wert darf nicht mehr als 30 alphanumerische Zeichen enthalten",
                                        QMessageBox.Ok)
                    test = 1
        else:   
            if EC.data_is_empty(str(self.comboBox_sito.currentText())) == 0:
                QMessageBox.warning(self, "WARNING", "Site Field. \n The field must not be empty", QMessageBox.Ok)
                test = 1
            if EC.data_is_empty(str(self.comboBox_area.currentText())) == 0:
                QMessageBox.warning(self, "WARNING", "Area Field. \n The field must not be empty", QMessageBox.Ok)
                test = 1
            if EC.data_is_empty(str(self.lineEdit_us.text())) == 0:
                QMessageBox.warning(self, "WARNING", "SU Field. \n The field must not be empty", QMessageBox.Ok)
                test = 1
            if EC.data_is_empty(str(self.comboBox_unita_tipo.currentText())) == 0:
                QMessageBox.warning(self, "WARNING", "SU-WSU Field. \n The field must not be empty",
                                    QMessageBox.Ok)
                test = 1
            area = self.comboBox_area.currentText()
            us = self.lineEdit_us.text()
            attivita = self.lineEdit_attivita.text()
            colore = self.comboBox_colore.currentText()
            anno_scavo = self.lineEdit_anno.text()
            formazione = self.comboBox_formazione.currentText()
            stato_conservazione = self.comboBox_conservazione.currentText()
            colore = self.comboBox_colore.currentText()
            consistenza = self.comboBox_consistenza.currentText()
            struttura = self.comboBox_struttura.currentText()
            cont_per = self.lineEdit_codice_periodo.text()
            if area != "":
                if EC.data_is_int(area) == 0:
                    QMessageBox.warning(self, "WARNING", "Area Field. \n The value must be numerical",
                                        QMessageBox.Ok)
                    test = 1
            if us != "":
                if EC.data_is_int(us) == 0:
                    QMessageBox.warning(self, "WARNING", "SU Field. \n The value must be numerical",
                                        QMessageBox.Ok)
                    test = 1
            if attivita != "":
                if EC.data_lenght(attivita, 3) == 0:
                    QMessageBox.warning(self, "WARNING",
                                        "Activity Field. \n The value must not exceed 4 alphanumeric characters",
                                        QMessageBox.Ok)
                    test = 1
                    # if anno_scavo != "":
            # if EC.data_lenght(anno_scavo,3) == 0:
            #       QMessageBox.warning(self, "ATTENZIONE", "Campo Anno. \n immettere una sola data (es. 2014)",  QMessageBox.Ok)
            #       test = 1
            if formazione != "":
                if EC.data_lenght(formazione, 19) == 0:
                    QMessageBox.warning(self, "WARNING",
                                        "Formation Field. \n The value must not exceed 20 alphanumeric characters",
                                        QMessageBox.Ok)
                    test = 1
            if stato_conservazione != "":
                if EC.data_lenght(stato_conservazione, 19) == 0:
                    QMessageBox.warning(self, "WARNING",
                                        "Conservation Field. \n The value must not exceed 20 alphanumeric characters",
                                        QMessageBox.Ok)
                    test = 1
            if colore != "":
                if EC.data_lenght(colore, 19) == 0:
                    QMessageBox.warning(self, "WARNING",
                                        "Color Field. \n The value must not exceed 20 alphanumeric characters",
                                        QMessageBox.Ok)
                    test = 1
            if consistenza != "":
                if EC.data_lenght(consistenza, 19) == 0:
                    QMessageBox.warning(self, "WARNING",
                                        "Texture Field. \n The value must not exceed 20 alphanumeric characters",
                                        QMessageBox.Ok)
                    test = 1
            if struttura != "":
                if EC.data_lenght(struttura, 29) == 0:
                    QMessageBox.warning(self, "WARNING",
                                        "Structure Field. \n The value must not exceed 20 alphanumeric characters",
                                        QMessageBox.Ok)
                    test = 1
                # if cont_per != "":
                #   if EC.data_lenght(cont_per,199) == 0:
                #       QMessageBox.warning(self, "ATTENZIONE", "Campo codice periodo. \n Il valore non deve superare i 200 caratteri numerici",  QMessageBox.Ok)
                #       test = 1
                # PERIODIZZAZIONE CHECK
                # periodo iniz compilato e fase vuota  il blocco deve essere utilizzato meglio a partire dai signals
        """
        if self.comboBox_per_iniz.currentText() != "" and self.comboBox_fas_iniz.currentText() == "":
            QMessageBox.warning(self, "ATTENZIONE", "Campo Fase iniziale \n Specificare la Fase iniziale oltre al Periodo",  QMessageBox.Ok)
            test = 1
        if self.comboBox_per_fin.currentText()  != "" and self.comboBox_fas_fin.currentText() == "":
            QMessageBox.warning(self, "ATTENZIONE", "Campo Fase finale \n Specificare la Fase finale oltre al Periodo",  QMessageBox.Ok)
            test = 1
        if self.comboBox_per_iniz.currentText()  == "" and self.comboBox_fas_iniz.currentText() != "":
            QMessageBox.warning(self, "ATTENZIONE", "Campo Periodo iniziale \n Specificare un Periodo iniziale oltre alla Fase",  QMessageBox.Ok)
            test = 1
        if self.comboBox_per_fin.currentText()  == "" and self.comboBox_fas_fin.currentText() != "":
            QMessageBox.warning(self, "ATTENZIONE", "Campo Periodo iniziale \n Specificare un Periodo finale oltre alla Fase",  QMessageBox.Ok)
            test = 1
        if self.comboBox_per_fin.currentText()  != "" and self.comboBox_fas_fin.currentText() != "" and self.comboBox_per_iniz.currentText()  == "" and self.comboBox_fas_iniz.currentText() == "":
            QMessageBox.warning(self, "ATTENZIONE", "Campi Periodo e Fase iniziali \n Specificare un Periodo e Fase iniziali se si vuole inserire un Periodo e Fase finali",  QMessageBox.Ok)
            test = 1
        if self.comboBox_per_fin.currentText()  != "" and self.comboBox_fas_fin.currentText() != "" and self.comboBox_per_iniz.currentText()  == "" and self.comboBox_fas_iniz.currentText() == "":
            QMessageBox.warning(self, "ATTENZIONE", "Campi Periodo e Fase iniziali \n Specificare un Periodo e Fase iniziali se si vuole inserire un Periodo e Fase finali",  QMessageBox.Ok)
            test = 1
        if self.comboBox_per_iniz.currentText()  != "" and self.comboBox_fas_iniz.currentText() != "":
            search_dict = {
            'sito'  : "'"+str(self.comboBox_sito.currentText())+"'",
            'periodo'  : "'"+str(self.comboBox_per_iniz.currentText())+"'",
            }
            if  bool(self.DB_MANAGER.query_bool(search_dict, 'PERIODIZZAZIONE')) == False:
                QMessageBox.warning(self, "ATTENZIONE", "Campi Periodo e Fase iniziali \n E' stata inserita una periodizzazione inesistente",  QMessageBox.Ok)
                test = 1
        """
        return test
    
    def automaticform_check(self, sito_check, area_check):
        
        search_dict = {'sito': "'" + str(sito_check) + "'", 'area': "'" + str(area_check) + "'"}
        records = self.DB_MANAGER.query_bool(search_dict,
                                             self.MAPPER_TABLE_CLASS)  # carica tutti i dati di uno scavo ordinati per numero di US
        if self.L=='it':
            report_rapporti3 = 'Report controllo e conteggio delle Schede create automatcamente - Sito: %s \n' % (
                sito_check)
        elif self.L=='de':
            report_rapporti3 = 'Kontrollbericht Definition Stratigraphische zu Stratigraphische Berichte - Ausgrabungsstätte: %s \n' % (
                sito_check)
        else:
            report_rapporti3 = 'Control and count of forms automatically created - Site: %s \n' % (
                sito_check)     
        for rec in range(len(records)):
            sito = "'" + str(records[rec].sito) + "'"
            area = "'" + str(records[rec].area) + "'"
            us = int(records[rec].us)
            def_stratigrafica = "'" + str(records[rec].d_stratigrafica) + "'"
            rapporti = records[rec].rapporti  # caricati i rapporti nella variabile
            rapporti = eval(def_stratigrafica)
            #for sing_rapp in range(len(records)):  # itera sulla serie di rapporti
            report3 = ""
            if def_stratigrafica.find('SCHEDA CREATA IN AUTOMATICO')>=0:
                
                    
                report3 = 'Sito: %s, Area: %s, US: %d - %s. Da rivedere ' % (
                    sito, area, int(us), def_stratigrafica)
            
            if report3 != "":
                report_rapporti3 = report_rapporti3 + report3 + '\n' 
                # self.listWidget_rapp.item(0).setForeground(QtCore.Qt.blue)
                # self.listWidget_rapp.item(1).setForeground(QtCore.Qt.blue)
                #self.listWidget_rapp.clear() 
        self.listWidget_rapp.addItem(report_rapporti3)    
        HOME = os.environ['PYARCHINIT_HOME']
        report_path = '{}{}{}'.format(HOME, os.sep, "pyarchinit_Report_folder")
        if self.L=='it':
            filename = '{}{}{}'.format(report_path, os.sep, 'log_schedeautomatiche.txt')
        elif self.L=='de':
            filename = '{}{}{}'.format(report_path, os.sep, 'log_def_strat_to_SE relation.txt')
        elif self.L=='en':
            filename = '{}{}{}'.format(report_path, os.sep, 'log_strat_def_to_SU relation.txt') 
        f = open(filename, "w")
        f.write(report_rapporti3)
        f.close()
    
    def rapporti_stratigrafici_check(self, sito_check, area_check):
        self.listWidget_rapp.clear()
        conversion_dict = {'Covers':'Covered by',
                           'Covered by': 'Covers',
                           'Fills': 'Filled by',
                           'Filled by':'Fills', 
                           'Cuts': 'Cutted by',
                           'Cutted by': 'Cuts',
                           'Abuts': 'Supports',
                           'Supports': 'Abuts', 
                           'Connected to': 'Connected to',
                           'Same as':'Same as',
                           'Copre':'Coperto da',
                           'Coperto da': 'Copre',
                           'Riempie': 'Riempito da',
                           'Riempito da' : 'Riempie',
                           'Taglia': 'Tagliato da',
                           'Tagliato da': 'Taglia',
                           'Si appoggia a': 'Gli si appoggia',
                           'Gli si appoggia': 'Si appoggia a',
                           'Si lega a': 'Si lega a',
                           'Uguale a':'Uguale a',
                           'Liegt über':'Liegt unter',
                           'Liegt unter':'Liegt über',
                           'Schneidet':'Wird geschnitten',
                           'Wird geschnitten':'Schneidet',
                           'Verfüllt':'Wird verfüllt durch',
                           'Wird verfüllt durch':'Verfüllt',
                           'Stützt sich auf':'Wird gestüzt von',
                           'Wird gestüzt von':'Stützt sich auf',
                           'Bindet an':'Bindet an',
                           'Entspricht':'Entspricht',
                           '>>':'<<',
                           '<<':'>>',
                           '<':'>',
                           '>':'<',
                           '<->':'<->'
                           }
        search_dict = {'sito': "'" + str(sito_check) + "'", 'area': "'" + str(area_check) + "'"}
        records = self.DB_MANAGER.query_bool(search_dict,
                                             self.MAPPER_TABLE_CLASS)  # carica tutti i dati di uno scavo ordinati per numero di US
        if self.L=='it':
            report_rapporti = 'Report controllo Rapporti Stratigrafici - Sito: %s \n' % (sito_check)
        elif self.L=='de':
            report_rapporti = 'Kontrollbericht Stratigraphische Beziehungen - Ausgrabungsstätte: %s \n' % (sito_check)
        else:
            report_rapporti = 'Control report Stratigraphic relationships - Site: %s \n' % (sito_check)   
        for rec in range(len(records)):
            sito = "'" + str(records[rec].sito) + "'"
            area = "'" + str(records[rec].area) + "'"
            us = int(records[rec].us)
            rapporti = records[rec].rapporti  # caricati i rapporti nella variabile
            rapporti = eval(rapporti)
            report = ''
            for sing_rapp in rapporti:  # itera sulla serie di rapporti
                
                
                if str(us).find('0') or str(us).find('1') >=0:
                    if len(sing_rapp) == 2:
                        
                        rapp_converted = conversion_dict[sing_rapp[0]]
                        
                        serch_dict_rapp = {'sito': sito, 'area': area, 'us': sing_rapp[1]}
                        us_rapp = self.DB_MANAGER.query_bool(serch_dict_rapp, self.MAPPER_TABLE_CLASS)
                        
                        if not bool(us_rapp):
                            if self.L=='it':
                                report = 'Sito: %s, Area: %s, US: %d %s US: %d: Scheda US non esistente' % (
                                    sito, area, int(us), sing_rapp[0], int(sing_rapp[1]))
                            elif self.L=='de':
                                report = 'Ausgrabungsstätte: %s, Areal: %s, SE: %d %s SE: %d: SE formular nicht existent' % (
                                    sito, area, int(us), sing_rapp[0], int(sing_rapp[1]))
                            else:
                                report = 'Site: %s, Area: %s, SU: %d %s SU: %d: SU form not-existent' % (
                                    sito, area, int(us), sing_rapp[0], int(sing_rapp[1]))       
                            # new system rapp_check
                        else:
                            rapporti_check = eval(us_rapp[0].rapporti)
                            
                            us_rapp_check=('%s') % str(us)
                            
                            if rapporti_check.count([rapp_converted, us_rapp_check]) == 1:
                                report = ""
                            else:
                                if self.L=='it':
                                    report = 'Sito: %s, Area: %s, US: %d %s US: %d: Rapporto non verificato' % (
                                        sito, area, int(us), sing_rapp[0], int(sing_rapp[1]))
                                elif self.L=='de':
                                    report = 'Ausgrabungsstätte: %s, Areal: %s, SE: %d %s SE: %d: nicht geprüfter Bericht' % (
                                        sito, area, int(us), sing_rapp[0], int(sing_rapp[1]))
                                else:
                                    report = 'Site: %s, Area: %s, SU: %d %s SU: %d: relashionships not verified' % (
                                        sito, area, int(us), sing_rapp[0], int(sing_rapp[1]))       
                        
                if report != "":
                    report_rapporti = report_rapporti + report + '\n'
                   
        self.listWidget_rapp.addItem(report_rapporti)
            
            # self.progressBar_3.setHidden(False)
            # value = (float(rec)/float(len(records)))*100
            # self.progressBar_3.setValue(value)
            # QApplication.processEvents()
        # self.progressBar_3.reset()           
        
        HOME = os.environ['PYARCHINIT_HOME']
        report_path = '{}{}{}'.format(HOME, os.sep, "pyarchinit_Report_folder")
        if self.L=='it':
            filename = '{}{}{}'.format(report_path, os.sep, 'log_rapporti_US.txt')
        elif self.L=='de':
            filename = '{}{}{}'.format(report_path, os.sep, 'log_SE.txt')
        else:
            filename = '{}{}{}'.format(report_path, os.sep, 'log_SU_relations.txt')     
        f = open(filename, "w")
        f.write(report_rapporti)
        f.close()
    def def_strati_to_rapporti_stratigrafici_check(self, sito_check, area_check):
        conversion_dict = {'Covers':'Covered by',
                           'Covered by': 'Covers',
                           'Fills': 'Filled by',
                           'Filled by':'Fills', 
                           'Cuts': 'Cutted by',
                           'Cutted by': 'Cuts',
                           'Abuts': 'Supports',
                           'Supports': 'Abuts', 
                           'Connected to': 'Connected to',
                           'Same as':'Same as',
                           'Copre':'Coperto da',
                           'Coperto da': 'Copre',
                           'Riempie': 'Riempito da',
                           'Riempito da' : 'Riempie',
                           'Taglia': 'Tagliato da',
                           'Tagliato da': 'Taglia',
                           'Si appoggia a': 'Gli si appoggia',
                           'Gli si appoggia': 'Si appoggia a',
                           'Si lega a': 'Si lega a',
                           'Uguale a':'Uguale a',
                           'Liegt über':'Liegt unter',
                           'Liegt unter':'Liegt über',
                           'Schneidet':'Wird geschnitten',
                           'Wird geschnitten':'Schneidet',
                           'Verfüllt':'Wird verfüllt durch',
                           'Wird verfüllt durch':'Verfüllt',
                           'Stützt sich auf':'Wird gestüzt von',
                           'Wird gestüzt von':'Stützt sich auf',
                           'Bindet an':'Bindet an',
                           'Entspricht':'Entspricht',
                           '>>':'<<',
                           '<<':'>>',
                           '<':'>',
                           '>':'<',
                           '<->':'<->'
                           }
        search_dict = {'sito': "'" + str(sito_check) + "'", 'area': "'" + str(area_check) + "'"}
        records = self.DB_MANAGER.query_bool(search_dict,
                                             self.MAPPER_TABLE_CLASS)  # carica tutti i dati di uno scavo ordinati per numero di US
        if self.L=='it':
            report_rapporti1 = 'Report controllo Definizione Stratigrafica a Rapporti Stratigrafici - Sito: %s \n' % (
                sito_check)
        elif self.L=='de':
            report_rapporti1 = 'Kontrollbericht Definition Stratigraphische zu Stratigraphische Berichte - Ausgrabungsstätte: %s \n' % (
                sito_check)
        else:
            report_rapporti1 = 'Control report Definition Stratigraphic to Stratigraphic Reports - Site: %s \n' % (
                sito_check)     
        for rec in range(len(records)):
            sito = "'" + str(records[rec].sito) + "'"
            area = "'" + str(records[rec].area) + "'"
            us = int(records[rec].us)
            def_stratigrafica = "'" + str(records[rec].d_stratigrafica) + "'"
            rapporti = records[rec].rapporti  # caricati i rapporti nella variabile
            rapporti = eval(rapporti)
            
           
            for sing_rapp in rapporti:  # itera sulla serie di rapporti
                report = ""
                if def_stratigrafica.find('Strato') >= 0:  # Paradosso strati che tagliano o si legano
                    if sing_rapp[0] == 'Si lega a':
                        report = 'Sito: %s, Area: %s, US: %d - %s: lo strato %s US: %d: ' % (
                            sito, area, int(us), def_stratigrafica, sing_rapp[0], int(sing_rapp[1]))
                if def_stratigrafica.find('Riempimento') >= 0:  # Paradosso riempimentiche tagliano o si legano
                    if sing_rapp[0] == 'Taglia' or sing_rapp[0] == 'Si lega a'or sing_rapp[0] == 'Si appoggia a' or sing_rapp[0] == 'Gli si appoggia' or sing_rapp[0] == 'Taglia':
                        report = 'Sito: %s, Area: %s, US: %d - %s: lo strato %s US: %d: ' % (
                            sito, area, int(us), def_stratigrafica, sing_rapp[0], int(sing_rapp[1]))
                if def_stratigrafica.find('Taglio') >= 0:  # Paradosso riempimentiche tagliano o si legano
                    if sing_rapp[0] == 'Riempie' or sing_rapp[0] == 'Si lega a' or sing_rapp[0] == 'Si appoggia a'  or sing_rapp[0] == 'Gli si appoggia':
                        report = 'Sito: %s, Area: %s, US: %d - %s: lo strato %s US: %d: ' % (
                            sito, area, int(us), def_stratigrafica, sing_rapp[0], int(sing_rapp[1]))
                if report != "":
                    report_rapporti1 = report_rapporti1 + report + '\n'
                #versione inglese
                elif def_stratigrafica.find('Stra') >= 0:  # Paradosso strati che tagliano o si legano
                    if sing_rapp[0] == 'Connected to':
                        report = 'Site: %s, Area: %s, SU: %d - %s: the stratum %s SU: %d: ' % (
                            sito, area, int(us), def_stratigrafica, sing_rapp[0], int(sing_rapp[1]))
                if def_stratigrafica.find('Fills') >= 0:  # Paradosso riempimentiche tagliano o si legano
                    if sing_rapp[0] == 'Cuts' or sing_rapp[0] == 'Connected to':
                        report = 'Site: %s, Area: %s, SU: %d - %s: the startum %s SU: %d: ' % (
                            sito, area, int(us), def_stratigrafica, sing_rapp[0], int(sing_rapp[1]))
                # if def_stratigrafica.find('Filling') >= 0:  # Paradosso riempimentiche tagliano o si legano
                    # if sing_rapp[0] == 'Cuts' or sing_rapp[0] == 'Connected to':
                        # report = 'Site: %s, Area: %s, SU: %d - %s: the stratum %s SU: %d: ' % (
                            # sito, area, int(us), def_stratigrafica, sing_rapp[0], int(sing_rapp[1]))
                if report != "":
                    report_rapporti1 = report_rapporti1 + report + '\n'
                #versione tedesca   
                elif def_stratigrafica.find('Stratum') >= 0:  # Paradosso strati che tagliano o si legano
                    if sing_rapp[0] == 'Bindet an':
                        report = 'Sito: %s, Area: %s, SE: %d - %s: die startum %s US: %d: ' % (
                            sito, area, int(us), def_stratigrafica, sing_rapp[0], int(sing_rapp[1]))
                if def_stratigrafica.find('Verfullüng') >= 0:  # Paradosso riempimentiche tagliano o si legano
                    if sing_rapp[0] == 'Schneidet' or sing_rapp[0] == 'Bindet an':
                        report = 'Sito: %s, Area: %s, SE: %d - %s: die stratum %s US: %d: ' % (
                            sito, area, int(us), def_stratigrafica, sing_rapp[0], int(sing_rapp[1]))
                # if def_stratigrafica.find('Verfullüng') >= 0:  # Paradosso riempimentiche tagliano o si legano
                    # if sing_rapp[0] == 'Schneidet' or sing_rapp[0] == 'Bindet an':
                        # report = 'Sito: %s, Area: %s, SE: %d - %s: die startum %s US: %d: ' % (
                            # sito, area, int(us), def_stratigrafica, sing_rapp[0], int(sing_rapp[1]))
                if report != "":
                    report_rapporti1 = report_rapporti1 + report + '\n' 
                
        self.listWidget_rapp.addItem(report_rapporti1)    
             
        HOME = os.environ['PYARCHINIT_HOME']
        report_path = '{}{}{}'.format(HOME, os.sep, "pyarchinit_Report_folder")
        if self.L=='it':
            filename = '{}{}{}'.format(report_path, os.sep, 'log_def_strat_a_rapporti_US.txt')
        elif self.L=='de':
            filename = '{}{}{}'.format(report_path, os.sep, 'log_def_strat_to_SE relation.txt')
        elif self.L=='en':
            filename = '{}{}{}'.format(report_path, os.sep, 'log_strat_def_to_SU relation.txt') 
        f = open(filename, "w")
        f.write(report_rapporti1)
        f.close()
    
    def concat(self,a, b):
        return eval(f"{a}{b}")
    
    def periodi_to_rapporti_stratigrafici_check(self, sito_check, area_check):
        conversion_dict = {'Covers':'Covered by',
                           'Covered by': 'Covers',
                           'Fills': 'Filled by',
                           'Filled by':'Fills', 
                           'Cuts': 'Cutted by',
                           'Cutted by': 'Cuts',
                           'Abuts': 'Supports',
                           'Supports': 'Abuts', 
                           'Connected to': 'Connected to',
                           'Same as':'Same as',
                           'Copre':'Coperto da',
                           'Coperto da': 'Copre',
                           'Riempie': 'Riempito da',
                           'Riempito da' : 'Riempie',
                           'Taglia': 'Tagliato da',
                           'Tagliato da': 'Taglia',
                           'Si appoggia a': 'Gli si appoggia',
                           'Gli si appoggia': 'Si appoggia a',
                           'Si lega a': 'Si lega a',
                           'Uguale a':'Uguale a',
                           'Liegt über':'Liegt unter',
                           'Liegt unter':'Liegt über',
                           'Schneidet':'Wird geschnitten',
                           'Wird geschnitten':'Schneidet',
                           'Verfüllt':'Wird verfüllt durch',
                           'Wird verfüllt durch':'Verfüllt',
                           'Stützt sich auf':'Wird gestüzt von',
                           'Wird gestüzt von':'Stützt sich auf',
                           'Bindet an':'Bindet an',
                           'Entspricht':'Entspricht',
                           '>>':'<<',
                           '<<':'>>',
                           '<':'>',
                           '>':'<',
                           '<->':'<->'
                           }
        search_dict = {'sito': "'" + str(sito_check) + "'", 'area': "'" + str(area_check) + "'"}
        records = self.DB_MANAGER.query_bool(search_dict,
                                             self.MAPPER_TABLE_CLASS)  # carica tutti i dati di uno scavo ordinati per numero di US
        if self.L=='it':
            report_rapporti2 = 'Report controllo Periodi/Unità Tipo a Rapporti Stratigrafici - Sito: %s \n' % (
                sito_check)
        elif self.L=='de':
            report_rapporti2 = 'Kontrollbericht Periodization/Type Unit zu Stratigraphische Berichte - Ausgrabungsstätte: %s \n' % (
                sito_check)
        else:
            report_rapporti2 = 'Control report Periodization/Type Unit to Stratigraphic Reports - Site: %s \n' % (
                sito_check)     
        for rec in range(len(records)):
            sito = "'" + str(records[rec].sito) + "'"
            area = "'" + str(records[rec].area) + "'"
            us = int(records[rec].us)
            periodo_in = str(records[rec].periodo_iniziale)
            fase_in = str(records[rec].fase_iniziale)
            periodo_fin =  str(records[rec].periodo_finale) 
            fase_fin =  str(records[rec].fase_iniziale) 
            ut=str(records[rec].unita_tipo)
            rapporti = records[rec].rapporti  # caricati i rapporti nella variabile
            rapporti = eval(rapporti)
            rapporti2 = records[rec].rapporti2  # caricati i rapporti nella variabile
            rapporti2 = eval(rapporti2)
            
            
            for sing_rapp in rapporti2:  # itera sulla serie di rapporti
                report = ""
                report2 = ""
                
                # rapp_sing=sing_rapp[4].split()
                # QMessageBox.information(self,'',str(rapp_sing))
                if str(periodo_in).find('1') or str(periodo_in).find('2') or str(periodo_in).find('3') or str(periodo_in).find('4') or str(periodo_in).find('5') or str(periodo_in).find('6') or str(periodo_in).find('7') or str(periodo_in).find('8') or str(periodo_in).find('9') or str(periodo_in).find('10') or str(periodo_in).find('11') or str(periodo_in).find('12') or str(periodo_in).find('13') or str(periodo_in).find('14') or str(periodo_in).find('15')>=0:
                    
                    if str(periodo_in)+'-'+str(fase_in)!=sing_rapp[4]:
                        if sing_rapp[0] == 'Si lega a' or sing_rapp[0] == 'Uguale a' or sing_rapp[0] == 'Same as' or sing_rapp[0] == 'Connected to':
                            report = 'Sito: %s, Area: %s, %s: %d -  Il periodo e fase iniziale %s: deve essere: %s corrispondente con la %s : %d: ' % (
                                sito, area, ut, int(us), str(periodo_in)+'-'+str(fase_in), sing_rapp[0], sing_rapp[2], int(sing_rapp[1]))
                    
                    # if not bool(sing_rapp):
                        # report2:'la table widget deve essere riempita' 
                    if sing_rapp[0] == 'Si lega a' and sing_rapp[2]=='US':
                    
                        report2 = '%s : %d - %s : %d: devono essere USM' % (
                            ut, int(us), sing_rapp[2], int(sing_rapp[1]))
                    
                    if sing_rapp[0] == 'Connected to' and sing_rapp[2]=='SU':
                    
                        report2 = '%s : %d - %s : %d: should be WSU' % (
                            ut, int(us), sing_rapp[2], int(sing_rapp[1]))
                    
                    if sing_rapp[0] == 'Uguale a' and sing_rapp[2]=='USM':
                    
                        report2 = '%s : %d - %s : %d: devono essere US' % (
                            ut, int(us), sing_rapp[2], int(sing_rapp[1]))
            
                    if sing_rapp[0] == 'Same as' and sing_rapp[2]=='WSU':
                    
                        report2 = '%s : %d - %s : %d: should be SU' % (
                            ut, int(us), sing_rapp[2], int(sing_rapp[1]))
                    
                    if sing_rapp[0] == 'Si appoggia a' and sing_rapp[2]=='US':
                    
                        report2 = '%s : %d - %s : %d: devono essere USM' % (
                            ut, int(us), sing_rapp[2], int(sing_rapp[1]))
                            
                    if sing_rapp[0] == 'Gli si appoggia' and sing_rapp[2]=='US':
                    
                        report2 = '%s : %d - %s : %d: devono essere USM' % (
                            ut, int(us), sing_rapp[2], int(sing_rapp[1]))
                
                    if sing_rapp[0] == 'Abuts' and sing_rapp[2]=='SU':
                    
                        report2 = '%s : %d - %s : %d: should be WSU' % (
                            ut, int(us), sing_rapp[2], int(sing_rapp[1]))
                            
                    if sing_rapp[0] == 'Supports' and sing_rapp[2]=='SU':
                    
                        report2 = '%s : %d - %s : %d: should be WSU' % (
                            ut, int(us), sing_rapp[2], int(sing_rapp[1]))
                
                    if sing_rapp[4]!='-':
                    
                        if sing_rapp[0] == 'Covers' and int(sing_rapp[4].replace('-',''))<self.concat(int(periodo_in),int(fase_in)):
                            
                            report2 = '%s : %d : %s- should be Covered by %s : %s-%s' % (
                                ut, int(us),str(sing_rapp[4]), sing_rapp[1],  str(periodo_in),str(fase_in))
                                
                        if sing_rapp[0] == 'Covered by' and int(sing_rapp[4].replace('-',''))>self.concat(int(periodo_in),int(fase_in)):
                        
                            report2 = '%s : %d : %s- should be Covers %s : %s-%s' % (
                                ut, int(us),str(sing_rapp[4]), sing_rapp[1], str(periodo_in),str(fase_in))
                    
                        if sing_rapp[0] == 'Fills' and int(sing_rapp[4].replace('-',''))<self.concat(int(periodo_in),int(fase_in)):
                            
                            report2 = '%s : %d : %s- Should be Filled by %s : %s-%s' % (
                                ut, int(us),str(sing_rapp[4]), sing_rapp[1],  str(periodo_in),str(fase_in))
                                
                        if sing_rapp[0] == 'Filled by' and int(sing_rapp[4].replace('-',''))>self.concat(int(periodo_in),int(fase_in)):
                        
                            report2 = '%s : %d : %s- Shuld be Fills %s : %s-%s' % (
                                ut, int(us),str(sing_rapp[4]), sing_rapp[1], str(periodo_in),str(fase_in))
                    
                        if sing_rapp[0] == 'Cuts' and int(sing_rapp[4].replace('-',''))<self.concat(int(periodo_in),int(fase_in)):
                            
                            report2 = '%s : %d : %s- Shuld be Cutted by %s : %s-%s' % (
                                ut, int(us),str(sing_rapp[4]), sing_rapp[1],  str(periodo_in),str(fase_in))
                                
                        if sing_rapp[0] == 'Cutted by' and int(sing_rapp[4].replace('-',''))>self.concat(int(periodo_in),int(fase_in)):
                        
                            report2 = '%s : %d : %s- Shuld be Cuts %s : %s-%s' % (
                                ut, int(us),str(sing_rapp[4]), sing_rapp[1], str(periodo_in),str(fase_in))
                        
                        if sing_rapp[0] == 'Abuts' and int(sing_rapp[4].replace('-',''))<self.concat(int(periodo_in),int(fase_in)):
                            
                            report2 = '%s : %d : %s- Shuld be Supports %s : %s-%s' % (
                                ut, int(us),str(sing_rapp[4]), sing_rapp[1],  str(periodo_in),str(fase_in))
                                
                        if sing_rapp[0] == 'Supports' and int(sing_rapp[4].replace('-',''))>self.concat(int(periodo_in),int(fase_in)):
                        
                            report2 = '%s : %d : %s- Shuld be Abuts %s : %s-%s' % (
                                ut, int(us),str(sing_rapp[4]), sing_rapp[1], str(periodo_in),str(fase_in))
                                          
                        if sing_rapp[0] == 'Copre' and int(sing_rapp[4].replace('-',''))<self.concat(int(periodo_in),int(fase_in)):
                            
                            report2 = '%s : %d : %s- Dovrebbe essere Coperto da %s : %s-%s' % (
                                ut, int(us),str(sing_rapp[4]), sing_rapp[1],  str(periodo_in),str(fase_in))
                                
                        if sing_rapp[0] == 'Coperto da' and int(sing_rapp[4].replace('-',''))>self.concat(int(periodo_in),int(fase_in)):
                        
                            report2 = '%s : %d : %s- Dovrebbe Coprire %s : %s-%s' % (
                                ut, int(us),str(sing_rapp[4]), sing_rapp[1], str(periodo_in),str(fase_in))
                    
                        if sing_rapp[0] == 'Riempie' and int(sing_rapp[4].replace('-',''))<self.concat(int(periodo_in),int(fase_in)):
                            
                            report2 = '%s : %d : %s- Dovrebbe essere Riempito da %s : %s-%s' % (
                                ut, int(us),str(sing_rapp[4]), sing_rapp[1],  str(periodo_in),str(fase_in))
                                
                        if sing_rapp[0] == 'Riempito da' and int(sing_rapp[4].replace('-',''))>self.concat(int(periodo_in),int(fase_in)):
                        
                            report2 = '%s : %d : %s- Dovrebbe Riempire %s : %s-%s' % (
                                ut, int(us),str(sing_rapp[4]), sing_rapp[1], str(periodo_in),str(fase_in))
                    
                        if sing_rapp[0] == 'Taglia' and int(sing_rapp[4].replace('-',''))<self.concat(int(periodo_in),int(fase_in)):
                            
                            report2 = '%s : %d : %s- Dovrebbe essere Tagliato da %s : %s-%s' % (
                                ut, int(us),str(sing_rapp[4]), sing_rapp[1],  str(periodo_in),str(fase_in))
                                
                        if sing_rapp[0] == 'Tagliato da' and int(sing_rapp[4].replace('-',''))>self.concat(int(periodo_in),int(fase_in)):
                        
                            report2 = '%s : %d : %s- Dovrebbe Tagliare %s : %s-%s' % (
                                ut, int(us),str(sing_rapp[4]), sing_rapp[1], str(periodo_in),str(fase_in))
                    
                        if sing_rapp[0] == 'Si appoggia a' and int(sing_rapp[4].replace('-',''))<self.concat(int(periodo_in),int(fase_in)):
                            
                            report2 = '%s : %d : %s- Dovrebbe essere Gli si appoggia %s : %s-%s' % (
                                ut, int(us),str(sing_rapp[4]), sing_rapp[1],  str(periodo_in),str(fase_in))
                                
                        if sing_rapp[0] == 'Gli si appoggia' and int(sing_rapp[4].replace('-',''))>self.concat(int(periodo_in),int(fase_in)):
                        
                            report2 = '%s : %d : %s- Dovrebbe Si appoggia a %s : %s-%s' % (
                                ut, int(us),str(sing_rapp[4]), sing_rapp[1], str(periodo_in),str(fase_in))
                    if sing_rapp[4]=='-':
                        if self.L=='it':
                            report2 = 'Manca la peridizzazione in %s %s'% (sing_rapp[2], sing_rapp[1])
                        else:
                            report2 = 'Missing the periodization in %s %s'% (sing_rapp[2], sing_rapp[1])
                
                
                
                if report2 != "":
                    report_rapporti2 = report_rapporti2 + report + report2+'\n'
                
        self.listWidget_rapp.addItem(report_rapporti2)    
        
           
          
        HOME = os.environ['PYARCHINIT_HOME']
        report_path = '{}{}{}'.format(HOME, os.sep, "pyarchinit_Report_folder")
        if self.L=='it':
            filename = '{}{}{}'.format(report_path, os.sep, 'log_per_ut_a_rapporti_US.txt')
        elif self.L=='de':
            filename = '{}{}{}'.format(report_path, os.sep, 'log_per_ut_to_SE relation.txt')
        elif self.L=='en':
            filename = '{}{}{}'.format(report_path, os.sep, 'log_per_ut_to_SU relation.txt') 
        f = open(filename, "w")
        f.write(report_rapporti2)
        f.close()
   
    def insert_new_rec(self):
        # TableWidget
        #Rapporti
        rapporti = self.table2dict("self.tableWidget_rapporti")
        rapporti2 = self.table2dict("self.tableWidget_rapporti2")
        #Inclusi
        inclusi = self.table2dict("self.tableWidget_inclusi")
        #Campioni
        campioni = self.table2dict("self.tableWidget_campioni")
        #organici
        organici = self.table2dict("self.tableWidget_organici")
        #inorganici
        inorganici = self.table2dict("self.tableWidget_inorganici")
        #Documentazione
        documentazione = self.table2dict("self.tableWidget_documentazione")
        #Colore legante usm
        colore_legante_usm = self.table2dict("self.tableWidget_colore_legante_usm")
        #Inclusi leganti usm
        aggreg_legante_usm = self.table2dict("self.tableWidget_inclusi_leganti_usm")
        #Consistenza texture mat_usm
        consistenza_texture_mat_usm = self.table2dict("self.tableWidget_consistenza_texture_mat_usm")
        #inclusi_materiali_usm
        inclusi_materiali_usm = self.table2dict("self.tableWidget_inclusi_materiali_usm")
        #colore_materiale_usm
        colore_materiale_usm = self.table2dict("self.tableWidget_colore_materiale_usm")
        if self.lineEditOrderLayer.text() == "":
            order_layer = 0
        else:
            order_layer = int(self.lineEditOrderLayer.text())
        ##quota min usm
        if self.lineEdit_qmin_usm.text() == "":
            qmin_usm = None
        else:
            qmin_usm = float(self.lineEdit_qmin_usm.text())
        ##quota max usm
        if self.lineEdit_qmax_usm.text() == "":
            qmax_usm = None
        else:
            qmax_usm = float(self.lineEdit_qmax_usm.text())
        ##quota relativa
        if self.lineEdit_quota_relativa.text() == "":
            quota_relativa = None
        else:
            quota_relativa = float(self.lineEdit_quota_relativa.text())
        ##quota abs
        if self.lineEdit_quota_abs.text() == "":
            quota_abs = None
        else:
            quota_abs = float(self.lineEdit_quota_abs.text())
        ##lunghezza max
        if self.lineEdit_lunghezza_max.text() == "":
            lunghezza_max = None
        else:
            lunghezza_max = float(self.lineEdit_lunghezza_max.text())
        ##altezza max
        if self.lineEdit_altezza_max.text() == "":
            altezza_max = None
        else:
            altezza_max = float(self.lineEdit_altezza_max.text())
        ##altezza min
        if self.lineEdit_altezza_min.text() == "":
            altezza_min = None
        else:
            altezza_min = float(self.lineEdit_altezza_min.text())
        ##profondita max
        if self.lineEdit_profondita_max.text() == "":
            profondita_max = None
        else:
            profondita_max = float(self.lineEdit_profondita_max.text())
        ##profondita min
        if self.lineEdit_profondita_min.text() == "":
            profondita_min = None
        else:
            profondita_min = float(self.lineEdit_profondita_min.text())
        ##larghezza media
        if self.lineEdit_larghezza_media.text() == "":
            larghezza_media = None
        else:
            larghezza_media = float(self.lineEdit_larghezza_media.text())
        ##quota max abs
        if self.lineEdit_quota_max_abs.text() == "":
            quota_max_abs = None
        else:
            quota_max_abs = float(self.lineEdit_quota_max_abs.text())
        ##quota max relativa
        if self.lineEdit_quota_max_rel.text() == "":
            quota_max_rel = None
        else:
            quota_max_rel = float(self.lineEdit_quota_max_rel.text())
        ##quota min abs
        if self.lineEdit_quota_min_abs.text() == "":
            quota_min_abs = None
        else:
            quota_min_abs = float(self.lineEdit_quota_min_abs.text())
        ##quota min relativa
        if self.lineEdit_quota_min_rel.text() == "":
            quota_min_rel = None
        else:
            quota_min_rel = float(self.lineEdit_quota_min_rel.text())
        ##lunghezza usm
        if self.lineEdit_lunghezza_usm.text() == "":
            lunghezza_usm = None
        else:
            lunghezza_usm = float(self.lineEdit_lunghezza_usm.text())
        ##altezza usm
        if self.lineEdit_altezza_usm.text() == "":
            altezza_usm = None
        else:
            altezza_usm = float(self.lineEdit_altezza_usm.text())
        ##spessore usm
        if self.lineEdit_spessore_usm.text() == "":
            spessore_usm = None
        else:
            spessore_usm = float(self.lineEdit_spessore_usm.text())
        try:
            # data
            data = self.DB_MANAGER.insert_values(
                self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, self.ID_TABLE) + 1,
                str(self.comboBox_sito.currentText()),  # 1 - Sito
                str(self.comboBox_area.currentText()),  # 2 - Area
                int(self.lineEdit_us.text()),  # 3 - US
                str(self.comboBox_def_strat.currentText()),  # 4 - Definizione stratigrafica
                str(self.comboBox_def_intepret.currentText()),  # 5 - Definizione intepretata
                str(self.textEdit_descrizione.toPlainText()),  # 6 - descrizione
                str(self.textEdit_interpretazione.toPlainText()),  # 7 - interpretazione
                str(self.comboBox_per_iniz.currentText()),  # 8 - periodo iniziale
                str(self.comboBox_fas_iniz.currentText()),  # 9 - fase iniziale
                str(self.comboBox_per_fin.currentText()),  # 10 - periodo finale iniziale
                str(self.comboBox_fas_fin.currentText()),  # 11 - fase finale
                str(self.comboBox_scavato.currentText()),  # 12 - scavato
                str(self.lineEdit_attivita.text()),  # 13 - attivita
                str(self.lineEdit_anno.text()),  # 14 - anno scavo
                str(self.comboBox_metodo.currentText()),  # 15 - metodo
                str(inclusi),  # 16 - inclusi
                str(campioni),  # 17 - campioni
                str(rapporti),  # 18 - rapporti
                #str(organici), # componenti organici
                #str(inorganici), #componenti inorganici
                str(self.lineEdit_data_schedatura.text()),  # 19 - data schedatura
                str(self.comboBox_schedatore.currentText()),  # 20 - schedatore
                str(self.comboBox_formazione.currentText()),  # 21 - formazione
                str(self.comboBox_conservazione.currentText()),  # 22 - conservazione
                str(self.comboBox_colore.currentText()),  # 23 - colore
                str(self.comboBox_consistenza.currentText()),  # 24 - consistenza
                str(self.comboBox_struttura.currentText()),  # 25 - struttura
                str(self.lineEdit_codice_periodo.text()),  # 26 - continuita  periodo
                order_layer,  # 27 - order layer
                str(documentazione),  # 28 - documentazione
                str(self.comboBox_unita_tipo.currentText()),  # 29 us_tipo            NUOVI CAMPI NUOVI CAMPI
                str(self.comboBox_settore.currentText()),  # 30 settore
                str(self.lineEdit_quadrato.text()),  # 31 quadrato
                str(self.lineEdit_ambiente.text()),  # 32 ambiente
                str(self.lineEdit_saggio.text()),  # 33 saggio
                str(self.textEdit_elementi_datanti.toPlainText()),  # 34 elementi datanti
                str(self.comboBox_funz_statica_usm.currentText()),  # 35 funzione statica
                str(self.comboBox_lavorazione_usm.currentText()),  # 36 lavorazione usm
                str(self.lineEdit_spessore_giunti_usm.text()),  # 37 spessore giunti
                str(self.lineEdit_letti_di_posa_giunti_usm.text()),  # 38 letti posa giunti usm
                str(self.lineEdit_h_modulo_c_corsi_usm.text()),  # 39 altezza modulo corsi usm
                str(self.comboBox_unita_edilizia_riassuntiva_usm.currentText()),  # 40 unita edilizia riassuntiva
                str(self.comboBox_reimpiego_usm.currentText()),  # 41 unita edilizia riassuntiva
                str(self.comboBox_posa_in_opera_usm.currentText()),  # 42 posa in opera
                qmin_usm,  # 43 quota minima
                qmax_usm,  # 44 quota massima
                str(self.comboBox_consistenza_legante_usm.currentText()),  #  1 45 consitenza legante usm
                str(colore_legante_usm),  # 2 46 colore legante usm
                str(aggreg_legante_usm),  # 47 3 aggreg legante usm
                str(consistenza_texture_mat_usm),  # 4 48 consistenza text mat
                str(colore_materiale_usm),  # 5 49 colore materiale usm
                str(inclusi_materiali_usm), # 6 50 inclusi_mat_usm
                str(self.lineEdit_n_catalogo_generale.text()), # 51 nr catalogo generale campi aggiunti per archeo 3.0 e allineamento ICCD
                str(self.lineEdit_n_catalogo_interno.text()), # 52 nr catalogo interno
                str(self.lineEdit_n_catalogo_internazionale.text()), # 53 nr catalogo internazionale
                str(self.comboBox_soprintendenza.currentText()), # 54 nr soprintendenza
                quota_relativa, #55 quota relativa
                quota_abs, #56 quota abs
                str(self.lineEdit_ref_tm.text()),  # 57 ref tm
                str(self.comboBox_ref_ra.currentText()),  # 58 ref ra
                str(self.lineEdit_ref_n.text()),  # 59 ref n
                str(self.comboBox_posizione.currentText()),  # 60 posizione
                str(self.lineEdit_criteri_distinzione.text()),  # 61 criteri distinzione
                str(self.comboBox_modo_formazione.currentText()),  # 62 modo formazione
                str(organici),  # 63 componenti organici
                str(inorganici),  # 64 componenti inorganici
                lunghezza_max,  # 65
                altezza_max,  # 66
                altezza_min,  # 67
                profondita_max,  # 68
                profondita_min,  # 69
                larghezza_media,  # 70
                quota_max_abs,  # 71
                quota_max_rel,  # 72
                quota_min_abs,  # 73
                quota_min_rel,  # 74
                str(self.textEdit_osservazioni.toPlainText()),  # 75 osservazioni
                str(self.comboBox_datazione.currentText()),  # 76 datazione
                str(self.comboBox_flottazione.currentText()),  # 77 flottazione
                str(self.comboBox_setacciatura.currentText()),  # 78 setacciatura
                str(self.comboBox_affidabilita.currentText()),  # 79 affidabilita
                str(self.comboBox_direttore_us.currentText()),  # 80 direttore us
                str(self.comboBox_responsabile_us.currentText()),  # 81 responsabile us
                str(self.lineEdit_cod_ente_schedatore.text()),  # 82 cod ente schedatore
                str(self.lineEdit_data_rilevazione.text()),  # 83 data rilevazione
                str(self.lineEdit_data_rielaborazione.text()),  # 84 data rielaborazione
                lunghezza_usm,  # 85
                altezza_usm,  # 86
                spessore_usm,  # 87
                str(self.comboBox_tecnica_muraria_usm.currentText()),  # 88 tecnica muraria usm
                str(self.comboBox_modulo_usm.currentText()),  # 89 modulo usm
                str(self.lineEdit_campioni_malta_usm.text()),  # 90 campioni malta usm
                str(self.lineEdit_campioni_mattone_usm.text()),  # 91 campioni mattone usm
                str(self.lineEdit_campioni_pietra_usm.text()),  # 92 campioni pietra usm
                str(self.lineEdit_provenienza_materiali_usm.text()),  # 93 provenienza_materiali_usm
                str(self.lineEdit_criteri_distinzione_usm.text()),  # 94 criteri distinzione usm
                str(self.comboBox_uso_primario_usm.currentText()),
                str(self.comboBox_tipologia_opera.currentText()),
                str(self.comboBox_sezione_muraria.currentText()),
                str(self.comboBox_superficie_analizzata.currentText()),
                str(self.comboBox_orientamento.currentText()),
                str(self.comboBox_materiali_lat.currentText()),
                str(self.comboBox_lavorazione_lat.currentText()),
                str(self.comboBox_consistenza_lat.currentText()),
                str(self.comboBox_forma_lat.currentText()),
                str(self.comboBox_colore_lat.currentText()),
                str(self.comboBox_impasto_lat.currentText()),
                str(self.comboBox_forma_p.currentText()),
                str(self.comboBox_colore_p.currentText()),
                str(self.comboBox_taglio_p.currentText()),
                str(self.comboBox_posa_opera_p.currentText()),
                str(self.comboBox_inerti_usm.currentText()),  # 95 uso primario usm
                str(self.comboBox_tipo_legante_usm.currentText()),  # 95 uso primario usm
                str(self.comboBox_rifinitura_usm.currentText()),  # 95 uso primario usm
                str(self.comboBox_materiale_p.currentText()),  # 95 uso primario usm
                str(self.comboBox_consistenza_p.currentText()),  # 95 uso primario usm
                str(rapporti2),
                str(self.mQgsFileWidget.text())
                )
            # todelete
            # f = open("C:\\Users\\Luca\\pyarchinit_Report_folder\\data_insert_list.txt", "w")
            # f.write(str(data))
            # f.close
            # todelete
            try:
                self.DB_MANAGER.insert_data_session(data)
                return 1
            except Exception as e:
                e_str = str(e)
                if e_str.__contains__("IntegrityError"):
                    if self.L=='it':
                        msg = "US già presente nel database"
                        QMessageBox.warning(self, "Error", "Error: " + str(msg), QMessageBox.Ok)
                    elif self.L=='de':
                        msg = self.ID_TABLE + " bereits in der Datenbank"
                        QMessageBox.warning(self, "Error", "Error: " + str(msg), QMessageBox.Ok)  
                    else:
                        msg = self.ID_TABLE + " exist in db"
                        QMessageBox.warning(self, "Error", "Error: " + str(msg), QMessageBox.Ok)  
                else:
                    msg = e
                    QMessageBox.warning(self, "Error", "Error 1 \n" + str(msg), QMessageBox.Ok)
                return 0
        except Exception as e:
            QMessageBox.warning(self, "Error", "Error 2 \n" + str(e), QMessageBox.Ok)
            return 0
            # insert new row into tableWidget
    def on_pushButton_insert_row_rapporti_pressed(self):
        self.insert_new_row('self.tableWidget_rapporti')
        
    def on_pushButton_remove_row_rapporti_pressed(self):
        self.remove_row('self.tableWidget_rapporti')
        
    def on_pushButton_insert_row_rapporti2_pressed(self):
       
        self.insert_new_row('self.tableWidget_rapporti2')
    def on_pushButton_remove_row_rapporti2_pressed(self):
        
        self.remove_row('self.tableWidget_rapporti2')
    
    def on_pushButton_insert_row_inclusi_pressed(self):
        self.insert_new_row('self.tableWidget_inclusi')
    def on_pushButton_remove_row_inclusi_pressed(self):
        self.remove_row('self.tableWidget_inclusi')
    def on_pushButton_insert_row_campioni_pressed(self):
        self.insert_new_row('self.tableWidget_campioni')
    def on_pushButton_remove_row_campioni_pressed(self):
        self.remove_row('self.tableWidget_campioni')
    def on_pushButton_insert_row_organici_pressed(self):
        self.insert_new_row('self.tableWidget_organici')
    def on_pushButton_remove_row_organici_pressed(self):
        self.remove_row('self.tableWidget_organici')
    def on_pushButton_insert_row_inorganici_pressed(self):
        self.insert_new_row('self.tableWidget_inorganici')
    def on_pushButton_remove_row_inorganici_pressed(self):
        self.remove_row('self.tableWidget_inorganici')
    def on_pushButton_insert_row_documentazione_pressed(self):
        self.insert_new_row('self.tableWidget_documentazione')
    def on_pushButton_remove_row_documentazione_pressed(self):
        self.remove_row('self.tableWidget_documentazione')
    def on_pushButton_insert_row_inclusi_materiali_pressed(self):
        self.insert_new_row('self.tableWidget_inclusi_materiali_usm')
    def on_pushButton_remove_row_inclusi_materiali_pressed(self):
        self.remove_row('self.tableWidget_inclusi_materiali_usm')
    def on_pushButton_insert_row_inclusi_leganti_pressed(self):
        self.insert_new_row('self.tableWidget_inclusi_leganti_usm')
    def on_pushButton_remove_row_inclusi_leganti_pressed(self):
        self.remove_row('self.tableWidget_inclusi_leganti_usm')
    def on_pushButton_insert_row_colore_legante_usm_pressed(self):
        self.insert_new_row('self.tableWidget_colore_legante_usm')
    def on_pushButton_remove_row_colore_legante_usm_pressed(self):
        self.remove_row('self.tableWidget_colore_legante_usm')
    def on_pushButton_insert_row_consistenza_texture_mat_usm_pressed(self):
        self.insert_new_row('self.tableWidget_consistenza_texture_mat_usm')
    def on_pushButton_remove_row_consistenza_texture_mat_usm_pressed(self):
        self.remove_row('self.tableWidget_consistenza_texture_mat_usm')
    def on_pushButton_insert_row_colore_materiale_usm_pressed(self):
        self.insert_new_row('self.tableWidget_colore_materiale_usm')
    def on_pushButton_remove_row_colore_materiale_usm_pressed(self):
        self.remove_row('self.tableWidget_colore_materiale_usm')
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
            return 0  
            # records surf functions
    def on_pushButton_view_all_pressed(self):
        
        self.checkBox_query.setChecked(False)
        if self.checkBox_query.isChecked():
            self.model_a.database().close()
        self.empty_fields()
        self.charge_records()
        self.fill_fields()
        self.BROWSE_STATUS = "b"
        self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
        if type(self.REC_CORR) == "<class 'str'>":
            corr = 0
        else:
            corr = self.REC_CORR
        self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
        self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
        self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
        self.SORT_STATUS = "n"
        self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
        # records surf functions
    def on_pushButton_first_rec_pressed(self):
        
        self.checkBox_query.setChecked(False)
        if self.checkBox_query.isChecked():
            self.model_a.database().close()
        if self.check_record_state() == 1:
            pass
        else:
            try:
                self.empty_fields()
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                self.fill_fields(0)
                self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
            except :
                pass
    def on_pushButton_last_rec_pressed(self):
        self.checkBox_query.setChecked(False)
        if self.checkBox_query.isChecked():
            self.model_a.database().close()
        if self.check_record_state() == 1:
            pass
        else:
            try:
                self.empty_fields()
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), len(self.DATA_LIST) - 1
                self.fill_fields(self.REC_CORR)
                self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
            except:
                pass
    def on_pushButton_prev_rec_pressed(self):
        self.checkBox_query.setChecked(False)
        if self.checkBox_query.isChecked():
            self.model_a.database().close()
        rec_goto = int(self.lineEdit_goto.text())
        if self.check_record_state() == 1:
            pass
        else:
            self.REC_CORR = self.REC_CORR - rec_goto
        if self.REC_CORR <= -1:
            self.REC_CORR = self.REC_CORR + rec_goto
            QMessageBox.warning(self, "Attenzione", "Numero Rec Step troppo elevato", QMessageBox.Ok)
        else:
            try:
                self.empty_fields()
                self.fill_fields(self.REC_CORR)
                self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
            except:# Exception as e:
                pass#QMessageBox.warning(self, "Error", str(e), QMessageBox.Ok)
    def on_pushButton_next_rec_pressed(self):
        self.checkBox_query.setChecked(False)
        if self.checkBox_query.isChecked():
            self.model_a.database().close()
        rec_goto = int(self.lineEdit_goto.text())
        
        
        
        if self.check_record_state() == 1:
            pass
        else:
            self.REC_CORR = self.REC_CORR + rec_goto
        if self.REC_CORR >= self.REC_TOT:
            self.REC_CORR = self.REC_CORR - rec_goto
            QMessageBox.warning(self, "Attenzione", "Numero Rec Step troppo elevato", QMessageBox.Ok)
        else:
            try:
                self.empty_fields()
                self.fill_fields(self.REC_CORR)
                self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
            except :#Exception as e:
                pass#QMessageBox.warning(self, "Error", str(e), QMessageBox.Ok)
    
    
        if self.checkBox_validate.isChecked():
            self.selectRows()
            # while True:
                # try:
                    # self.empty_fields()
                    # self.fill_fields(self.REC_CORR)
                    # self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
                # except :#Exception as e:
                    # pass#QMessageBox.warning(self, "Error", str(e), QMessageBox.Ok)
                # #continue
                # else:
                    # break
    def on_pushButton_delete_pressed(self):
        self.checkBox_query.setChecked(False)
        if self.checkBox_query.isChecked():
            self.model_a.database().close()
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
                    QMessageBox.warning(self, "Attenzione", "Die Datenbank ist leer!", QMessageBox.Ok)
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
                    QMessageBox.warning(self, "Message", "error type: " + str(e))
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
            #
    def on_pushButton_new_search_pressed(self):
        self.checkBox_query.setChecked(False)
        if self.checkBox_query.isChecked():
            self.model_a.database().close()
        if self.BROWSE_STATUS != "f" and self.check_record_state() == 1:
            pass
        else:
            self.enable_button_search(0)
            conn = Connection()
        
            sito_set= conn.sito_set()
            sito_set_str = sito_set['sito_set']
            if self.BROWSE_STATUS != "f":
                if bool(self.comboBox_sito.currentText()) and self.comboBox_sito.currentText()==sito_set_str:
                    self.BROWSE_STATUS = "f"
                    self.empty_fields_nosite()
                    self.lineEdit_data_schedatura.setText("")
                    self.lineEdit_anno.setText("")
                    self.comboBox_formazione.setEditText("")
                    self.comboBox_metodo.setEditText("")
                    #self.setComboBoxEditable(["self.comboBox_sito"], 1)
                    self.setComboBoxEditable(["self.comboBox_area"], 1)
                    self.setComboBoxEditable(["self.comboBox_unita_tipo"],1)
                    self.setComboBoxEnable(["self.comboBox_sito"], "False")
                    self.setComboBoxEnable(["self.comboBox_area"], "True")
                    self.setComboBoxEnable(["self.comboBox_unita_tipo"], "True")
                    self.setComboBoxEnable(["self.lineEdit_us"], "True")
                    self.setComboBoxEnable(["self.textEdit_descrizione"], "False")
                    self.setComboBoxEnable(["self.textEdit_interpretazione"], "False")
                    self.setTableEnable(
                        ["self.tableWidget_campioni",
                         "self.tableWidget_rapporti",
                         "self.tableWidget_inclusi",
                         "self.tableWidget_organici",
                         "self.tableWidget_inorganici",
                         "self.tableWidget_documentazione",
                         "self.tableWidget_inclusi_materiali_usm",
                         "self.tableWidget_colore_legante_usm",
                         "self.tableWidget_inclusi_leganti_usm",
                         "self.tableWidget_consistenza_texture_mat_usm",
                         "self.tableWidget_colore_materiale_usm","self.tableWidget_rapporti2"], "False")
                    ###
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.set_rec_counter('', '')
                    self.label_sort.setText(self.SORTED_ITEMS["n"])
                    #self.charge_list()
                    
                else:
                    self.BROWSE_STATUS = "f"
                    ###
                    self.lineEdit_data_schedatura.setText("")
                    self.lineEdit_anno.setText("")
                    self.comboBox_formazione.setEditText("")
                    self.comboBox_metodo.setEditText("")
                    self.setComboBoxEditable(["self.comboBox_sito"], 1)
                    self.setComboBoxEditable(["self.comboBox_area"], 1)
                    self.setComboBoxEditable(["self.comboBox_unita_tipo"], 1)
                    self.setComboBoxEnable(["self.comboBox_sito"], "True")
                    self.setComboBoxEnable(["self.comboBox_area"], "True")
                    self.setComboBoxEnable(["self.comboBox_unita_tipo"], "True")
                    self.setComboBoxEnable(["self.lineEdit_us"], "True")
                    self.setComboBoxEnable(["self.textEdit_descrizione"], "False")
                    self.setComboBoxEnable(["self.textEdit_interpretazione"], "False")
                    self.setTableEnable(
                        ["self.tableWidget_campioni",
                         "self.tableWidget_rapporti",
                         "self.tableWidget_inclusi",
                         "self.tableWidget_organici",
                         "self.tableWidget_inorganici",
                         "self.tableWidget_documentazione",
                         "self.tableWidget_inclusi_materiali_usm",
                         "self.tableWidget_colore_legante_usm",
                         "self.tableWidget_inclusi_leganti_usm",
                         "self.tableWidget_consistenza_texture_mat_usm",
                         "self.tableWidget_colore_materiale_usm","self.tableWidget_rapporti2"], "False")
                    ###
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.set_rec_counter('', '')
                    self.label_sort.setText(self.SORTED_ITEMS["n"])
                    self.charge_list()
                    self.empty_fields()
    def on_pushButton_showLayer_pressed(self):
        """
        for sing_us in range(len(self.DATA_LIST)):
            sing_layer = [self.DATA_LIST[sing_us]]
            self.pyQGIS.charge_vector_layers(sing_layer)
        """
        sing_layer = [self.DATA_LIST[self.REC_CORR]]
        self.pyQGIS.charge_vector_layers(sing_layer)
        self.pyQGIS.charge_usm_layers(sing_layer)
    def on_pushButton_crea_codice_periodo_pressed(self):
        try:
            self.set_sito()
            sito = str(self.comboBox_sito.currentText())
            self.DB_MANAGER.update_cont_per(sito)
            self.empty_fields()
            #self.charge_records()
            self.fill_fields(self.REC_CORR)  # ricaricare tutti i record in uso e passare il valore REC_CORR a fill_fields
            if self.L=='it':
                QMessageBox.warning(self, "INFO", "Codice periodo aggiornato per lo scavo %s" % (sito), QMessageBox.Ok)
            elif self.L=='de':
                QMessageBox.warning(self, "INFO", "Der Zeitstellungscode wurde für die Ausgrabung hochgeladen %s" % (sito), QMessageBox.Ok)
            elif self.L=='en':   
                QMessageBox.warning(self, "INFO", "Updated period code for excavation %s" % (sito), QMessageBox.Ok)
        except KeyError as e:
            if self.L=='it':
                QMessageBox.warning(self, "Attenzione", str(e), QMessageBox.Ok)
            elif self.L=='de':
                QMessageBox.warning(self, "Achtung", str(e), QMessageBox.Ok)
            elif self.L=='en':   
                QMessageBox.warning(self, "Attention", str(e), QMessageBox.Ok)
    def on_pushButton_search_go_pressed(self):
        self.checkBox_query.setChecked(False)
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
            if self.lineEdit_us.text() != "":
                us = int(self.lineEdit_us.text())
            else:
                us = ""
            ##qmin_usm
            if self.lineEdit_qmin_usm.text() != "":
                qmin_usm = float(self.lineEdit_qmin_usm.text())
            else:
                qmin_usm = None
            ##qmax_usm
            if self.lineEdit_qmax_usm.text() != "":
                qmax_usm = float(self.lineEdit_qmax_usm.text())
            else:
                qmax_usm = None
            #pre pyarchinit 3.0
            ##quota relativa
            if self.lineEdit_quota_relativa.text() == "":
                quota_relativa = None
            else:
                quota_relativa = float(self.lineEdit_quota_relativa.text())
            ##quota abs
            if self.lineEdit_quota_abs.text() == "":
                quota_abs = None
            else:
                quota_abs = float(self.lineEdit_quota_abs.text())
            ##lunghezza max
            if self.lineEdit_lunghezza_max.text() == "":
                lunghezza_max = None
            else:
                lunghezza_max = float(self.lineEdit_lunghezza_max.text())
            ##altezza max
            if self.lineEdit_altezza_max.text() == "":
                altezza_max = None
            else:
                altezza_max = float(self.lineEdit_altezza_max.text())
            ##altezza min
            if self.lineEdit_altezza_min.text() == "":
                altezza_min = None
            else:
                altezza_min = float(self.lineEdit_altezza_min.text())
            ##profondita max
            if self.lineEdit_profondita_max.text() == "":
                profondita_max = None
            else:
                profondita_max = float(self.lineEdit_profondita_max.text())
            ##profondita min
            if self.lineEdit_profondita_min.text() == "":
                profondita_min = None
            else:
                profondita_min = float(self.lineEdit_profondita_min.text())
            ##larghezza media
            if self.lineEdit_larghezza_media.text() == "":
                larghezza_media = None
            else:
                larghezza_media = float(self.lineEdit_larghezza_media.text())
            ##quota max abs
            if self.lineEdit_quota_max_abs.text() == "":
                quota_max_abs = None
            else:
                quota_max_abs = float(self.lineEdit_quota_max_abs.text())
            ##quota max relativa
            if self.lineEdit_quota_max_rel.text() == "":
                quota_max_rel = None
            else:
                quota_max_rel = float(self.lineEdit_quota_max_rel.text())
            ##quota min abs
            if self.lineEdit_quota_min_abs.text() == "":
                quota_min_abs = None
            else:
                quota_min_abs = float(self.lineEdit_quota_min_abs.text())
            ##quota min relativa
            if self.lineEdit_quota_min_rel.text() == "":
                quota_min_rel = None
            else:
                quota_min_rel = float(self.lineEdit_quota_min_rel.text())
            ##lunghezza usm
            if self.lineEdit_lunghezza_usm.text() == "":
                lunghezza_usm = None
            else:
                lunghezza_usm = float(self.lineEdit_lunghezza_usm.text())
            ##altezza usm
            if self.lineEdit_altezza_usm.text() == "":
                altezza_usm = None
            else:
                altezza_usm = float(self.lineEdit_altezza_usm.text())
            ##spessore usm
            if self.lineEdit_spessore_usm.text() == "":
                spessore_usm = None
            else:
                spessore_usm = float(self.lineEdit_spessore_usm.text())
            search_dict = {
                self.TABLE_FIELDS[0]: "'" + str(self.comboBox_sito.currentText()) + "'",  # 1 - Sito
                self.TABLE_FIELDS[1]: "'" + str(self.comboBox_area.currentText()) + "'",  # 2 - Area
                self.TABLE_FIELDS[2]: us,  # 3 - US
                self.TABLE_FIELDS[3]: "'" + str(self.comboBox_def_strat.currentText()) + "'",
                # 4 - Definizione stratigrafica
                self.TABLE_FIELDS[4]: "'" + str(self.comboBox_def_intepret.currentText()) + "'",
                # 5 - Definizione intepretata
                self.TABLE_FIELDS[5]: str(self.textEdit_descrizione.toPlainText()),  # 6 - descrizione
                self.TABLE_FIELDS[6]: str(self.textEdit_interpretazione.toPlainText()),  # 7 - interpretazione
                self.TABLE_FIELDS[7]: "'" + str(self.comboBox_per_iniz.currentText()) + "'",  # 8 - periodo iniziale
                self.TABLE_FIELDS[8]: "'" + str(self.comboBox_fas_iniz.currentText()) + "'",  # 9 - fase iniziale
                self.TABLE_FIELDS[9]: "'" + str(self.comboBox_per_fin.currentText()) + "'",
                # 10 - periodo finale iniziale
                self.TABLE_FIELDS[10]: "'" + str(self.comboBox_fas_fin.currentText()) + "'",  # 11 - fase finale
                self.TABLE_FIELDS[11]: "'" + str(self.comboBox_scavato.currentText()) + "'",  # 12 - scavato
                self.TABLE_FIELDS[12]: "'" + str(self.lineEdit_attivita.text()) + "'",  # 13 - attivita
                self.TABLE_FIELDS[13]: "'" + str(self.lineEdit_anno.text()) + "'",  # 14 - anno scavo
                self.TABLE_FIELDS[14]: "'" + str(self.comboBox_metodo.currentText()) + "'",  # 15 - metodo
                self.TABLE_FIELDS[18]: "'" + str(self.lineEdit_data_schedatura.text()) + "'",  # 16 - data schedatura
                self.TABLE_FIELDS[19]: "'" + str(self.comboBox_schedatore.currentText()) + "'",  # 17 - schedatore
                self.TABLE_FIELDS[20]: "'" + str(self.comboBox_formazione.currentText()) + "'",  # 18 - formazione
                self.TABLE_FIELDS[21]: "'" + str(self.comboBox_conservazione.currentText()) + "'",  # 19 - conservazione
                self.TABLE_FIELDS[22]: "'" + str(self.comboBox_colore.currentText()) + "'",  # 20 - colore
                self.TABLE_FIELDS[23]: "'" + str(self.comboBox_consistenza.currentText()) + "'",  # 21 - consistenza
                self.TABLE_FIELDS[24]: "'" + str(self.comboBox_struttura.currentText()) + "'",  # 22 - struttura
                self.TABLE_FIELDS[25]: "'" + str(self.lineEdit_codice_periodo.text()) + "'",  # 23 - codice_periodo
                self.TABLE_FIELDS[26]: "'" + str(self.lineEditOrderLayer.text()) + "'",  # 24 - order layer
                self.TABLE_FIELDS[28]: "'" + str(self.comboBox_unita_tipo.currentText()) + "'",  # 24 - order layer
                self.TABLE_FIELDS[29]: "'" + str(self.comboBox_settore.currentText()) + "'",  # 24 - order layer
                self.TABLE_FIELDS[30]: "'" + str(self.lineEdit_quadrato.text()) + "'",  # 30 quadrato
                self.TABLE_FIELDS[31]: "'" + str(self.lineEdit_ambiente.text()) + "'",  # 30 quadrato
                self.TABLE_FIELDS[32]: "'" + str(self.lineEdit_saggio.text()) + "'",  # 30 quadrato
                self.TABLE_FIELDS[33]: str(self.textEdit_elementi_datanti.toPlainText()),  # 6 - descrizione
                self.TABLE_FIELDS[34]: "'" + str(self.comboBox_funz_statica_usm.currentText()) + "'",
                # 24 - order layer
                self.TABLE_FIELDS[35]: "'" + str(self.comboBox_lavorazione_usm.currentText()) + "'",  # 30 quadrato
                self.TABLE_FIELDS[36]: "'" + str(self.lineEdit_spessore_giunti_usm.text()) + "'",  # 30 quadrato
                self.TABLE_FIELDS[37]: "'" + str(self.lineEdit_letti_di_posa_giunti_usm.text()) + "'",
                self.TABLE_FIELDS[38]: "'" + str(self.lineEdit_h_modulo_c_corsi_usm.text()) + "'",
                self.TABLE_FIELDS[39]: "'" + str(self.comboBox_unita_edilizia_riassuntiva_usm.currentText()) + "'",
                self.TABLE_FIELDS[40]: "'" + str(self.comboBox_reimpiego_usm.currentText()) + "'",
                self.TABLE_FIELDS[41]: "'" + str(self.comboBox_posa_in_opera_usm.currentText()) + "'",
                self.TABLE_FIELDS[42]: qmin_usm,
                self.TABLE_FIELDS[43]: qmax_usm,
                self.TABLE_FIELDS[44]: "'" + str(self.comboBox_consistenza_legante_usm.currentText()) + "'",
                self.TABLE_FIELDS[50]: "'" + str(self.lineEdit_n_catalogo_generale.text()) + "'",
            # 51 nr catalogo generale campi aggiunti per archeo 3.0 e allineamento ICCD
                self.TABLE_FIELDS[51]: "'" + str(self.lineEdit_n_catalogo_interno.text()) + "'",
            # 52 nr catalogo interno
                self.TABLE_FIELDS[52]: "'" + str(self.lineEdit_n_catalogo_internazionale.text()) + "'",
            # 53 nr catalogo internazionale
                self.TABLE_FIELDS[53]: "'" + str(self.comboBox_soprintendenza.currentText()) + "'",
            # 54 nr soprintendenza
                self.TABLE_FIELDS[54]:  quota_relativa,  # 55 quota relativa
                self.TABLE_FIELDS[55]:  quota_abs,  # 56 quota abs
                self.TABLE_FIELDS[56]: "'" + str(self.lineEdit_ref_tm.text()) + "'",  # 57 ref tm
                self.TABLE_FIELDS[57]: "'" + str(self.comboBox_ref_ra.currentText()) + "'",  # 58 ref ra
                self.TABLE_FIELDS[58]: "'" + str(self.lineEdit_ref_n.text()) + "'",  # 59 ref n
                self.TABLE_FIELDS[59]: "'" + str(self.comboBox_posizione.currentText()) + "'",  # 60 posizione
                self.TABLE_FIELDS[60]: "'" + str(self.lineEdit_criteri_distinzione.text()) + "'",
            # 61 criteri distinzione
                self.TABLE_FIELDS[61]: "'" + str(self.comboBox_modo_formazione.currentText()) + "'",
            # 62 modo formazione
            #    self.TABLE_FIELDS[62]: "'" + str(self.comboBox_componenti_organici.currentText()) + "'",
            # 63 componenti organici
            #    self.TABLE_FIELDS[63]: "'" + str(self.comboBox_componenti_inorganici.currentText()) + "'",
            # 64 componenti inorganici
                self.TABLE_FIELDS[62]:lunghezza_max,  # 65
                self.TABLE_FIELDS[63]:altezza_max,  # 66
                self.TABLE_FIELDS[64]:altezza_min,  # 67
                self.TABLE_FIELDS[65]:profondita_max,  # 68
                self.TABLE_FIELDS[66]:profondita_min,  # 69
                self.TABLE_FIELDS[67]:larghezza_media,  # 70
                self.TABLE_FIELDS[68]:quota_max_abs,  # 71
                self.TABLE_FIELDS[69]:quota_max_rel,  # 72
                self.TABLE_FIELDS[70]:quota_min_abs,  # 73
                self.TABLE_FIELDS[71]:quota_min_rel,  # 74
                self.TABLE_FIELDS[72]: "'" + str(self.textEdit_osservazioni.toPlainText()) + "'",  # 75 osservazioni
                self.TABLE_FIELDS[73]: "'" + str(self.comboBox_datazione.currentText()) + "'",  # 76 datazione
                self.TABLE_FIELDS[74]: "'" + str(self.comboBox_flottazione.currentText()) + "'",  # 77 flottazione
                self.TABLE_FIELDS[75]: "'" + str(self.comboBox_setacciatura.currentText()) + "'",  # 78 setacciatura
                self.TABLE_FIELDS[76]: "'" + str(self.comboBox_affidabilita.currentText()) + "'",  # 79 affidabilita
                self.TABLE_FIELDS[77]: "'" + str(self.comboBox_direttore_us.currentText()) + "'",  # 80 direttore us
                self.TABLE_FIELDS[78]: "'" + str(self.comboBox_responsabile_us.currentText()) + "'", # 81 responsabile us
                self.TABLE_FIELDS[79]: "'" + str(self.lineEdit_cod_ente_schedatore.text()) + "'", # 82 cod ente schedatore
                self.TABLE_FIELDS[80]: "'" + str(self.lineEdit_data_rilevazione.text()) + "'",  # 83 data rilevazione
                self.TABLE_FIELDS[81]: "'" + str(self.lineEdit_data_rielaborazione.text()) + "'", # 84 data rielaborazione
                self.TABLE_FIELDS[82]: lunghezza_usm,  # 85
                self.TABLE_FIELDS[83]: altezza_usm,  # 86
                self.TABLE_FIELDS[84]: spessore_usm,  # 87
                self.TABLE_FIELDS[85]: "'" + str(self.comboBox_tecnica_muraria_usm.currentText()) + "'", # 88 tecnica muraria usm
                self.TABLE_FIELDS[86]: "'" + str(self.comboBox_modulo_usm.currentText()) + "'", # 89 modulo usm
                self.TABLE_FIELDS[87]: "'" + str(self.lineEdit_campioni_malta_usm.text()) + "'", # 90 campioni malta usm
                self.TABLE_FIELDS[88]: "'" + str(self.lineEdit_campioni_mattone_usm.text()) + "'", # 91 campioni mattone usm
                self.TABLE_FIELDS[89]: "'" + str(self.lineEdit_campioni_pietra_usm.text()) + "'", # 92 campioni pietra usm
                self.TABLE_FIELDS[90]: "'" + str(self.lineEdit_provenienza_materiali_usm.text()) + "'", # 93 provenienza_materiali_usm
                self.TABLE_FIELDS[91]: "'" + str(self.lineEdit_criteri_distinzione_usm.text()) + "'", # 94 criteri distinzione usm
                self.TABLE_FIELDS[92]: "'" + str(self.comboBox_uso_primario_usm.currentText()) + "'",  # 95 uso primario usm
                self.TABLE_FIELDS[93]: "'" + str(self.comboBox_tipologia_opera.currentText()) + "'",  # 95 uso primario usm
                self.TABLE_FIELDS[94]: "'" + str(self.comboBox_sezione_muraria.currentText()) + "'" , # 95 uso primario usm
                self.TABLE_FIELDS[95]: "'" + str(self.comboBox_superficie_analizzata.currentText()) + "'" , # 95 uso primario usm
                self.TABLE_FIELDS[96]: "'" + str(self.comboBox_orientamento.currentText()) + "'" , # 95 uso primario usm
                self.TABLE_FIELDS[97]: "'" + str(self.comboBox_materiali_lat.currentText()) + "'",  # 95 uso primario usm
                self.TABLE_FIELDS[98]: "'" + str(self.comboBox_lavorazione_lat.currentText()) + "'",  # 95 uso primario usm
                self.TABLE_FIELDS[99]: "'" + str(self.comboBox_consistenza_lat.currentText()) + "'",  # 95 uso primario usm
                self.TABLE_FIELDS[100]: "'" + str(self.comboBox_forma_lat.currentText()) + "'" , # 95 uso primario usm
                self.TABLE_FIELDS[101]: "'" + str(self.comboBox_colore_lat.currentText()) + "'",  # 95 uso primario usm
                self.TABLE_FIELDS[102]: "'" + str(self.comboBox_impasto_lat.currentText()) + "'", # 95 uso primario usm
                self.TABLE_FIELDS[103]: "'" + str(self.comboBox_forma_p.currentText()) + "'" , # 95 uso primario usm
                self.TABLE_FIELDS[104]: "'" + str(self.comboBox_colore_p.currentText()) + "'",  # 95 uso primario usm
                self.TABLE_FIELDS[105]: "'" + str(self.comboBox_taglio_p.currentText()) + "'" , # 95 uso primario usm
                self.TABLE_FIELDS[106]: "'" + str(self.comboBox_posa_opera_p.currentText()) + "'",  # 95 uso primario usm
                self.TABLE_FIELDS[107]: "'" + str(self.comboBox_inerti_usm.currentText()) + "'",  # 95 uso primario usm
                self.TABLE_FIELDS[108]: "'" + str(self.comboBox_tipo_legante_usm.currentText()) + "'",  # 95 uso primario usm
                self.TABLE_FIELDS[109]: "'" + str(self.comboBox_rifinitura_usm.currentText()) + "'",  # 95 uso primario usm
                self.TABLE_FIELDS[110]: "'" + str(self.comboBox_materiale_p.currentText()) + "'",  # 95 uso primario usm
                self.TABLE_FIELDS[111]: "'" + str(self.comboBox_consistenza_p.currentText()) + "'",  # 95 uso primario usm
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
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.setComboBoxEnable(["self.comboBox_sito"], "False")
                    self.setComboBoxEnable(["self.comboBox_area"], "False")
                    self.setComboBoxEnable(["self.comboBox_unita_tipo"], "True")
                    self.setComboBoxEnable(["self.lineEdit_us"], "False")
                    self.setComboBoxEnable(["self.textEdit_descrizione"], "True")
                    self.setComboBoxEnable(["self.textEdit_interpretazione"], "True")
                    self.setTableEnable(
                        ["self.tableWidget_campioni", "self.tableWidget_rapporti", "self.tableWidget_inclusi",
                         "self.tableWidget_organici", "self.tableWidget_inorganici", "self.tableWidget_documentazione","self.tableWidget_rapporti2"], "True")
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
                            if self.toolButtonGis.isChecked():
                                self.pyQGIS.charge_vector_layers(self.DATA_LIST)
                            if self.toolButton_usm.isChecked():    
                                self.pyQGIS.charge_usm_layers(self.DATA_LIST)
                        else:
                            strings = ("Sono stati trovati", self.REC_TOT, "records")
                            if self.toolButtonGis.isChecked():
                                self.pyQGIS.charge_vector_layers(self.DATA_LIST)
                            if self.toolButton_usm.isChecked():    
                                self.pyQGIS.charge_usm_layers(self.DATA_LIST)
                    elif self.L=='de':
                        if self.REC_TOT == 1:
                            strings = ("Es wurde gefunden", self.REC_TOT, "record")
                            if self.toolButtonGis.isChecked():
                                self.pyQGIS.charge_vector_layers(self.DATA_LIST)
                            if self.toolButton_usm.isChecked():    
                                self.pyQGIS.charge_usm_layers(self.DATA_LIST)
                        else:
                            strings = ("Sie wurden gefunden", self.REC_TOT, "records")
                            if self.toolButtonGis.isChecked():
                                self.pyQGIS.charge_vector_layers(self.DATA_LIST)
                            if self.toolButton_usm.isChecked():    
                                self.pyQGIS.charge_usm_layers(self.DATA_LIST)
                    else:
                        if self.REC_TOT == 1:
                            strings = ("It has been found", self.REC_TOT, "record")
                            if self.toolButtonGis.isChecked():
                                self.pyQGIS.charge_vector_layers(self.DATA_LIST)
                            if self.toolButton_usm.isChecked():    
                                self.pyQGIS.charge_usm_layers(self.DATA_LIST)
                        else:
                            strings = ("They have been found", self.REC_TOT, "records")
                            if self.toolButtonGis.isChecked():
                                self.pyQGIS.charge_vector_layers(self.DATA_LIST)
                            if self.toolButton_usm.isChecked():    
                                self.pyQGIS.charge_usm_layers(self.DATA_LIST)
                    
                    self.setComboBoxEnable(["self.comboBox_sito"], "False")
                    self.setComboBoxEnable(["self.comboBox_area"], "False")
                    self.setComboBoxEnable(["self.lineEdit_us"], "False")
                    self.setComboBoxEnable(["self.comboBox_unita_tipo"], "True")
                    self.setTableEnable(
                        ["self.tableWidget_campioni",
                         "self.tableWidget_rapporti",
                         "self.tableWidget_inclusi",
                         "self.tableWidget_organici",
                         "self.tableWidget_inorganici",
                         "self.tableWidget_documentazione",
                         "self.tableWidget_inclusi_materiali_usm",
                         "self.tableWidget_colore_legante_usm",
                         "self.tableWidget_inclusi_leganti_usm",
                         "self.tableWidget_consistenza_texture_mat_usm",
                         "self.tableWidget_colore_materiale_usm","self.tableWidget_rapporti2"], "True")
                    self.setComboBoxEnable(["self.textEdit_descrizione"], "True")
                    self.setComboBoxEnable(["self.textEdit_interpretazione"], "True")
                    QMessageBox.warning(self, "Message", "%s %d %s" % strings, QMessageBox.Ok)
        self.enable_button_search(1)
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
                                                                self.ID_TABLE)  
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
    def rec_toupdate(self):
        rec_to_update = self.UTILITY.pos_none_in_list(self.DATA_LIST_REC_TEMP)
        return rec_to_update
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
    def yearstrfdate(self):
        now = date.today()
        year = now.strftime("%Y")
        return year
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
        table_col_count_cmd = "{}.columnCount()".format(self.table_name)
        table_col_count = eval(table_col_count_cmd)
        # clear table
        table_clear_cmd = "{}.clearContents()".format(self.table_name)
        eval(table_clear_cmd)
        for i in range(table_col_count):
            table_rem_row_cmd = "{}.removeRow(int({}))".format(self.table_name, i)
            eval(table_rem_row_cmd)
        for row in range(len(self.data_list)):
            cmd = '{}.insertRow(int({}))'.format(self.table_name, row)
            eval(cmd)
            for col in range(len(self.data_list[row])):
                # item = self.comboBox_sito.setEditText(self.data_list[0][col]
                # item = QTableWidgetItem(self.data_list[row][col])
                # TODO SL: evauation of QTableWidget does not work porperly
                exec_str = '{}.setItem(int({}),int({}),QTableWidgetItem(self.data_list[row][col]))'.format(self.table_name, row, col)
                eval(exec_str)
        max_row_num = len(self.data_list)
        value = eval(self.table_name+".item(max_row_num,1)")
        if value == '':
            cmd = ("%s.removeRow(%d)") % (self.table_name, max_row_num)
            eval(cmd)
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
        rowIndex = (rowSelected[0].row())
        cmd = ("%s.removeRow(%d)") % (table_name, rowIndex)
        eval(cmd)
    def empty_fields(self):
        rapporti_row_count = self.tableWidget_rapporti.rowCount()
        rapporti_row_count2 = self.tableWidget_rapporti2.rowCount()
        campioni_row_count = self.tableWidget_campioni.rowCount()
        inclusi_row_count = self.tableWidget_inclusi.rowCount()
        organici_row_count = self.tableWidget_organici.rowCount()
        inorganici_row_count = self.tableWidget_inorganici.rowCount()
        documentazione_row_count = self.tableWidget_documentazione.rowCount()
        self.comboBox_sito.setEditText("")  # 1 - Sito
        self.comboBox_area.setEditText("")  # 2 - Area
        self.lineEdit_us.clear()  # 3 - US
        self.comboBox_def_strat.setEditText("")  # 4 - Definizione stratigrafica
        self.comboBox_def_intepret.setEditText("")  # 5 - Definizione intepretata
        self.textEdit_descrizione.clear()  # 6 - descrizione
        self.textEdit_interpretazione.clear()  # 7 - interpretazione
        self.comboBox_per_iniz.setEditText("")  # 8 - periodo iniziale
        self.comboBox_fas_iniz.setEditText("")  # 9 - fase iniziale
        self.comboBox_per_fin.setEditText("")  # 10 - periodo finale iniziale
        self.comboBox_fas_fin.setEditText("")  # 11 - fase finale
        self.comboBox_scavato.setEditText("")  # 12 - scavato
        self.lineEdit_attivita.clear()  # 13 - attivita
        if self.BROWSE_STATUS == "n":
            self.lineEdit_anno.setText(self.yearstrfdate())  # 14 - anno scavo
        else:
            self.lineEdit_anno.clear()
        self.comboBox_metodo.setEditText("")  # 15 - metodo
        for i in range(inclusi_row_count):
            self.tableWidget_inclusi.removeRow(0)
        self.insert_new_row("self.tableWidget_inclusi")  # 16 - inclusi
        for i in range(campioni_row_count):
            self.tableWidget_campioni.removeRow(0)
        self.insert_new_row("self.tableWidget_campioni")  # 17 - campioni
        for i in range(organici_row_count):
            self.tableWidget_organici.removeRow(0)
        self.insert_new_row("self.tableWidget_organici")  # organici
        for i in range(inorganici_row_count):
            self.tableWidget_inorganici.removeRow(0)
        self.insert_new_row("self.tableWidget_inorganici")  # inorganici
        for i in range(rapporti_row_count):
            self.tableWidget_rapporti.removeRow(0)
        self.insert_new_row("self.tableWidget_rapporti")                #18 - rapporti
        for i in range(documentazione_row_count):
            self.tableWidget_documentazione.removeRow(0)
        self.insert_new_row("self.tableWidget_documentazione")  # 19 - documentazione
        for i in range(rapporti_row_count2):
            self.tableWidget_rapporti2.removeRow(0)
        self.insert_new_row("self.tableWidget_rapporti2")
        
        colore_legante_usm_row_count = self.tableWidget_colore_legante_usm.rowCount()
        for i in range(colore_legante_usm_row_count):
            self.tableWidget_colore_legante_usm.removeRow(0)
        self.insert_new_row("self.tableWidget_colore_legante_usm")  # 19 - aggregati
        inclusi_leganti_usm_row_count = self.tableWidget_inclusi_leganti_usm.rowCount()
        for i in range(inclusi_leganti_usm_row_count):
            self.tableWidget_inclusi_leganti_usm.removeRow(0)
        self.insert_new_row("self.tableWidget_inclusi_leganti_usm")  # 19 - aggregati
        cont_text_mat_row_count = self.tableWidget_consistenza_texture_mat_usm.rowCount()
        for i in range(cont_text_mat_row_count):
            self.tableWidget_consistenza_texture_mat_usm.removeRow(0)
        self.insert_new_row("self.tableWidget_consistenza_texture_mat_usm")  # 19 - colore legante usm
        aggreg_inclusi_materiale_row_count = self.tableWidget_inclusi_materiali_usm.rowCount()
        for i in range(aggreg_inclusi_materiale_row_count):
            self.tableWidget_inclusi_materiali_usm.removeRow(0)
        self.insert_new_row("self.tableWidget_inclusi_materiali_usm")  # 19 - aggregati
        colore_materiali_usm_row_count = self.tableWidget_colore_materiale_usm.rowCount()
        for i in range(colore_materiali_usm_row_count):
            self.tableWidget_colore_materiale_usm.removeRow(0)
        self.insert_new_row("self.tableWidget_colore_materiale_usm")  # 19 - aggregati
        if self.BROWSE_STATUS == "n":
            self.lineEdit_data_schedatura.setText(self.datestrfdate())  # 20 - data schedatura
        else:
            self.lineEdit_data_schedatura.setText("")  # 20 - data schedatura
       
        self.comboBox_schedatore.setEditText("")  # 21 - schedatore
        self.comboBox_formazione.setEditText("")  # 22 - formazione
        self.comboBox_conservazione.setEditText("")  # 23 - conservazione
        self.comboBox_colore.setEditText("")  # 24 - colore
        self.comboBox_consistenza.setEditText("")  # 25 - consistenza
        self.comboBox_struttura.setEditText("")  # 26 - struttura
        self.lineEdit_codice_periodo.clear()  # 27 - codice periodo
        self.lineEditOrderLayer.clear()  # 28 - order layer
        self.comboBox_unita_tipo.setEditText("")  # 29 us_tipo            NUOVI CAMPI NUOVI CAMPI
        self.comboBox_settore.setEditText("")  # 30 settore
        self.lineEdit_quadrato.clear()  # 31 quadrato
        self.lineEdit_ambiente.clear()  # 32 ambiente
        self.lineEdit_saggio.clear()  # 33 saggio
        self.textEdit_elementi_datanti.clear()  # 34 elementi datanti
        self.comboBox_funz_statica_usm.setEditText("")  # 35 funzione statica
        self.comboBox_lavorazione_usm.setEditText("")  # 36 lavorazione usm
        self.lineEdit_spessore_giunti_usm.clear()  # 37 spessore giunti
        self.lineEdit_letti_di_posa_giunti_usm.clear()  # 38 letti posa giunti usm
        self.lineEdit_h_modulo_c_corsi_usm.clear()  # 39 altezza modulo corsi usm
        self.comboBox_unita_edilizia_riassuntiva_usm.setEditText("")  # 40 unita edilizia riassuntiva
        self.comboBox_reimpiego_usm.setEditText("")  # 41 unita edilizia riassuntiva
        self.comboBox_posa_in_opera_usm.setEditText("")  # 42 posa in opera
        self.lineEdit_qmin_usm.clear()  # 3 - US
        self.lineEdit_qmax_usm.clear()  # 3 - US
        self.comboBox_consistenza_legante_usm.setEditText("")  # 45 consitenza legante usm
        self.lineEdit_n_catalogo_generale.clear()  # 51 nr catalogo generale campi aggiunti per archeo 3.0 e allineamento ICCD
        self.lineEdit_n_catalogo_interno.clear()  # 52 nr catalogo interno
        self.lineEdit_n_catalogo_internazionale.clear()  # 53 nr catalogo internazionale
        self.comboBox_soprintendenza.setEditText("")  # 54 nr soprintendenza
        self.lineEdit_quota_relativa.clear()  # 55
        self.lineEdit_quota_abs.clear()  # 56
        self.lineEdit_ref_tm.clear()  # 57 ref tm
        self.comboBox_ref_ra.setEditText("")   # 58 ref ra
        self.lineEdit_ref_n.clear()  # 59 ref n
        self.comboBox_posizione.setEditText("")  # 60 posizione
        self.lineEdit_criteri_distinzione.clear()  # 61 criteri distinzione
        self.comboBox_modo_formazione.setEditText("")  # 62 modo formazione
        #self.comboBox_componenti_organici.setEditText("")  # 63 componenti organici
        #self.comboBox_componenti_inorganici.setEditText("")  # 64 componenti inorganici
        self.lineEdit_lunghezza_max.clear()  # 65
        self.lineEdit_altezza_max.clear()  # 66
        self.lineEdit_altezza_min.clear()  # 67
        self.lineEdit_profondita_max.clear()  # 68
        self.lineEdit_profondita_min.clear()  # 69
        self.lineEdit_larghezza_media.clear()  # 70
        self.lineEdit_quota_max_abs.clear()  # 71
        self.lineEdit_quota_max_rel.clear()  # 72
        self.lineEdit_quota_min_abs.clear()  # 73
        self.lineEdit_quota_min_rel.clear()  # 74
        self.textEdit_osservazioni.clear()  # 75 osservazioni
        self.comboBox_datazione.setEditText("")  # 76 datazione
        self.comboBox_flottazione.setEditText("")  # 77 flottazione
        self.comboBox_setacciatura.setEditText("")   # 78 setacciatura
        self.comboBox_affidabilita.setEditText("")   # 79 affidabilita
        self.comboBox_direttore_us.setEditText("")  # 80 direttore us
        self.comboBox_responsabile_us.setEditText("")  # 81 responsabile us
        self.lineEdit_cod_ente_schedatore.clear()  # 82 cod ente schedatore
        self.lineEdit_data_rilevazione.clear()  # 83 data rilevazione
        self.lineEdit_data_rielaborazione.clear()  # 84 data rielaborazione
        self.lineEdit_lunghezza_usm.clear()  # 85
        self.lineEdit_altezza_usm.clear()  # 86
        self.lineEdit_spessore_usm.clear()  # 87
        self.comboBox_tecnica_muraria_usm.setEditText("")  # 88 tecnica muraria usm
        self.comboBox_modulo_usm.setEditText("")  # 89 modulo usm
        self.lineEdit_campioni_malta_usm.clear()  # 90 campioni malta usm
        self.lineEdit_campioni_mattone_usm.clear()  # 91 campioni mattone usm
        self.lineEdit_campioni_pietra_usm.clear()  # 92 campioni pietra usm
        self.lineEdit_provenienza_materiali_usm.clear()  # 93 provenienza_materiali_usm
        self.lineEdit_criteri_distinzione_usm.clear()  # 94 criteri distinzione usm
        self.comboBox_uso_primario_usm.setEditText("")  # 95 uso primario usm
        self.comboBox_tipologia_opera.setEditText("")  # 95 uso primario usm
        self.comboBox_sezione_muraria.setEditText("")  # 95 uso primario usm
        self.comboBox_superficie_analizzata.setEditText("")  # 95 uso primario usm
        self.comboBox_orientamento.setEditText("")  # 95 uso primario usm
        self.comboBox_materiali_lat.setEditText("")  # 95 uso primario usm
        self.comboBox_lavorazione_lat.setEditText("")  # 95 uso primario usm
        self.comboBox_consistenza_lat.setEditText("")  # 95 uso primario usm
        self.comboBox_forma_lat.setEditText("")  # 95 uso primario usm
        self.comboBox_colore_lat.setEditText("")  # 95 uso primario usm
        self.comboBox_impasto_lat.setEditText("")  # 95 uso primario usm
        self.comboBox_forma_p.setEditText("")  # 95 uso primario usm
        self.comboBox_colore_p.setEditText("")  # 95 uso primario usm
        self.comboBox_taglio_p.setEditText("")  # 95 uso primario usm
        self.comboBox_posa_opera_p.setEditText("")  # 95 uso primario usm
        self.comboBox_inerti_usm.setEditText("")  # 95 uso primario usm
        self.comboBox_tipo_legante_usm.setEditText("")  # 95 uso primario usm
        self.comboBox_rifinitura_usm.setEditText("")  # 95 uso primario usm
        self.comboBox_materiale_p.setEditText("")  # 95 uso primario usm
        self.comboBox_consistenza_p.setEditText("")  # 95 uso primario usm
        self.mQgsFileWidget.clear()
    def empty_fields_nosite(self):
        rapporti_row_count = self.tableWidget_rapporti.rowCount()
        rapporti_row_count2 = self.tableWidget_rapporti2.rowCount()
        campioni_row_count = self.tableWidget_campioni.rowCount()
        inclusi_row_count = self.tableWidget_inclusi.rowCount()
        organici_row_count = self.tableWidget_organici.rowCount()
        inorganici_row_count = self.tableWidget_inorganici.rowCount()
        documentazione_row_count = self.tableWidget_documentazione.rowCount()
        
        self.comboBox_area.setEditText("")  # 2 - Area
        self.lineEdit_us.clear()  # 3 - US
        self.comboBox_def_strat.setEditText("")  # 4 - Definizione stratigrafica
        self.comboBox_def_intepret.setEditText("")  # 5 - Definizione intepretata
        self.textEdit_descrizione.clear()  # 6 - descrizione
        self.textEdit_interpretazione.clear()  # 7 - interpretazione
        self.comboBox_per_iniz.setEditText("")  # 8 - periodo iniziale
        self.comboBox_fas_iniz.setEditText("")  # 9 - fase iniziale
        self.comboBox_per_fin.setEditText("")  # 10 - periodo finale iniziale
        self.comboBox_fas_fin.setEditText("")  # 11 - fase finale
        self.comboBox_scavato.setEditText("")  # 12 - scavato
        self.lineEdit_attivita.clear()  # 13 - attivita
        if self.BROWSE_STATUS == "n":
            self.lineEdit_anno.setText(self.yearstrfdate())  # 14 - anno scavo
        else:
            self.lineEdit_anno.clear()
        self.comboBox_metodo.setEditText("")  # 15 - metodo
        for i in range(inclusi_row_count):
            self.tableWidget_inclusi.removeRow(0)
        self.insert_new_row("self.tableWidget_inclusi")  # 16 - inclusi
        for i in range(campioni_row_count):
            self.tableWidget_campioni.removeRow(0)
        self.insert_new_row("self.tableWidget_campioni")  # 17 - campioni
        for i in range(organici_row_count):
            self.tableWidget_organici.removeRow(0)
        self.insert_new_row("self.tableWidget_organici")  # organici
        for i in range(inorganici_row_count):
            self.tableWidget_inorganici.removeRow(0)
        self.insert_new_row("self.tableWidget_inorganici")  # inorganici
        for i in range(rapporti_row_count):
            self.tableWidget_rapporti.removeRow(0)
        self.insert_new_row("self.tableWidget_rapporti")                #18 - rapporti
        for i in range(documentazione_row_count):
            self.tableWidget_documentazione.removeRow(0)
        for i in range(rapporti_row_count2):
            self.tableWidget_rapporti2.removeRow(0)
        self.insert_new_row("self.tableWidget_rapporti2")     
        
        self.insert_new_row("self.tableWidget_documentazione")  # 19 - documentazione
        colore_legante_usm_row_count = self.tableWidget_colore_legante_usm.rowCount()
        for i in range(colore_legante_usm_row_count):
            self.tableWidget_colore_legante_usm.removeRow(0)
        self.insert_new_row("self.tableWidget_colore_legante_usm")  # 19 - aggregati
        inclusi_leganti_usm_row_count = self.tableWidget_inclusi_leganti_usm.rowCount()
        for i in range(inclusi_leganti_usm_row_count):
            self.tableWidget_inclusi_leganti_usm.removeRow(0)
        self.insert_new_row("self.tableWidget_inclusi_leganti_usm")  # 19 - aggregati
        cont_text_mat_row_count = self.tableWidget_consistenza_texture_mat_usm.rowCount()
        for i in range(cont_text_mat_row_count):
            self.tableWidget_consistenza_texture_mat_usm.removeRow(0)
        self.insert_new_row("self.tableWidget_consistenza_texture_mat_usm")  # 19 - colore legante usm
        aggreg_inclusi_materiale_row_count = self.tableWidget_inclusi_materiali_usm.rowCount()
        for i in range(aggreg_inclusi_materiale_row_count):
            self.tableWidget_inclusi_materiali_usm.removeRow(0)
        self.insert_new_row("self.tableWidget_inclusi_materiali_usm")  # 19 - aggregati
        colore_materiali_usm_row_count = self.tableWidget_colore_materiale_usm.rowCount()
        for i in range(colore_materiali_usm_row_count):
            self.tableWidget_colore_materiale_usm.removeRow(0)
        self.insert_new_row("self.tableWidget_colore_materiale_usm")  # 19 - aggregati
        if self.BROWSE_STATUS == "n":
            self.lineEdit_data_schedatura.setText(self.datestrfdate())  # 20 - data schedatura
        else:
            self.lineEdit_data_schedatura.setText("")  # 20 - data schedatura
        
        self.comboBox_schedatore.setEditText("")  # 21 - schedatore
        self.comboBox_formazione.setEditText("")  # 22 - formazione
        self.comboBox_conservazione.setEditText("")  # 23 - conservazione
        self.comboBox_colore.setEditText("")  # 24 - colore
        self.comboBox_consistenza.setEditText("")  # 25 - consistenza
        self.comboBox_struttura.setEditText("")  # 26 - struttura
        self.lineEdit_codice_periodo.clear()  # 27 - codice periodo
        self.lineEditOrderLayer.clear()  # 28 - order layer
        self.comboBox_unita_tipo.setEditText("")  # 29 us_tipo            NUOVI CAMPI NUOVI CAMPI
        self.comboBox_settore.setEditText("")  # 30 settore
        self.lineEdit_quadrato.clear()  # 31 quadrato
        self.lineEdit_ambiente.clear()  # 32 ambiente
        self.lineEdit_saggio.clear()  # 33 saggio
        self.textEdit_elementi_datanti.clear()  # 34 elementi datanti
        self.comboBox_funz_statica_usm.setEditText("")  # 35 funzione statica
        self.comboBox_lavorazione_usm.setEditText("")  # 36 lavorazione usm
        self.lineEdit_spessore_giunti_usm.clear()  # 37 spessore giunti
        self.lineEdit_letti_di_posa_giunti_usm.clear()  # 38 letti posa giunti usm
        self.lineEdit_h_modulo_c_corsi_usm.clear()  # 39 altezza modulo corsi usm
        self.comboBox_unita_edilizia_riassuntiva_usm.setEditText("")  # 40 unita edilizia riassuntiva
        self.comboBox_reimpiego_usm.setEditText("")  # 41 unita edilizia riassuntiva
        self.comboBox_posa_in_opera_usm.setEditText("")  # 42 posa in opera
        self.lineEdit_qmin_usm.clear()  # 3 - US
        self.lineEdit_qmax_usm.clear()  # 3 - US
        self.comboBox_consistenza_legante_usm.setEditText("")  # 45 consitenza legante usm
        self.lineEdit_n_catalogo_generale.clear()  # 51 nr catalogo generale campi aggiunti per archeo 3.0 e allineamento ICCD
        self.lineEdit_n_catalogo_interno.clear()  # 52 nr catalogo interno
        self.lineEdit_n_catalogo_internazionale.clear()  # 53 nr catalogo internazionale
        self.comboBox_soprintendenza.setEditText("")  # 54 nr soprintendenza
        self.lineEdit_quota_relativa.clear()  # 55
        self.lineEdit_quota_abs.clear()  # 56
        self.lineEdit_ref_tm.clear()  # 57 ref tm
        self.comboBox_ref_ra.setEditText("")   # 58 ref ra
        self.lineEdit_ref_n.clear()  # 59 ref n
        self.comboBox_posizione.setEditText("")  # 60 posizione
        self.lineEdit_criteri_distinzione.clear()  # 61 criteri distinzione
        self.comboBox_modo_formazione.setEditText("")  # 62 modo formazione
        #self.comboBox_componenti_organici.setEditText("")  # 63 componenti organici
        #self.comboBox_componenti_inorganici.setEditText("")  # 64 componenti inorganici
        self.lineEdit_lunghezza_max.clear()  # 65
        self.lineEdit_altezza_max.clear()  # 66
        self.lineEdit_altezza_min.clear()  # 67
        self.lineEdit_profondita_max.clear()  # 68
        self.lineEdit_profondita_min.clear()  # 69
        self.lineEdit_larghezza_media.clear()  # 70
        self.lineEdit_quota_max_abs.clear()  # 71
        self.lineEdit_quota_max_rel.clear()  # 72
        self.lineEdit_quota_min_abs.clear()  # 73
        self.lineEdit_quota_min_rel.clear()  # 74
        self.textEdit_osservazioni.clear()  # 75 osservazioni
        self.comboBox_datazione.setEditText("")  # 76 datazione
        self.comboBox_flottazione.setEditText("")   # 77 flottazione
        self.comboBox_setacciatura.setEditText("")  # 78 setacciatura
        self.comboBox_affidabilita.setEditText("")  # 79 affidabilita
        self.comboBox_direttore_us.setEditText("")  # 80 direttore us
        self.comboBox_responsabile_us.setEditText("")  # 81 responsabile us
        self.lineEdit_cod_ente_schedatore.clear()  # 82 cod ente schedatore
        self.lineEdit_data_rilevazione.clear()  # 83 data rilevazione
        self.lineEdit_data_rielaborazione.clear()  # 84 data rielaborazione
        self.lineEdit_lunghezza_usm.clear()  # 85
        self.lineEdit_altezza_usm.clear()  # 86
        self.lineEdit_spessore_usm.clear()  # 87
        self.comboBox_tecnica_muraria_usm.setEditText("")  # 88 tecnica muraria usm
        self.comboBox_modulo_usm.setEditText("")  # 89 modulo usm
        self.lineEdit_campioni_malta_usm.clear()  # 90 campioni malta usm
        self.lineEdit_campioni_mattone_usm.clear()  # 91 campioni mattone usm
        self.lineEdit_campioni_pietra_usm.clear()  # 92 campioni pietra usm
        self.lineEdit_provenienza_materiali_usm.clear()  # 93 provenienza_materiali_usm
        self.lineEdit_criteri_distinzione_usm.clear()  # 94 criteri distinzione usm
        self.comboBox_uso_primario_usm.setEditText("")  # 95 uso primario usm
        self.comboBox_tipologia_opera.setEditText("")  # 95 uso primario usm
        self.comboBox_sezione_muraria.setEditText("")  # 95 uso primario usm
        self.comboBox_superficie_analizzata.setEditText("")  # 95 uso primario usm
        self.comboBox_orientamento.setEditText("")  # 95 uso primario usm
        self.comboBox_materiali_lat.setEditText("")  # 95 uso primario usm
        self.comboBox_lavorazione_lat.setEditText("")  # 95 uso primario usm
        self.comboBox_consistenza_lat.setEditText("")  # 95 uso primario usm
        self.comboBox_forma_lat.setEditText("")  # 95 uso primario usm
        self.comboBox_colore_lat.setEditText("")  # 95 uso primario usm
        self.comboBox_impasto_lat.setEditText("")  # 95 uso primario usm
        self.comboBox_forma_p.setEditText("")  # 95 uso primario usm
        self.comboBox_colore_p.setEditText("")  # 95 uso primario usm
        self.comboBox_taglio_p.setEditText("")  # 95 uso primario usm
        self.comboBox_posa_opera_p.setEditText("")  # 95 uso primario usm
        self.comboBox_inerti_usm.setEditText("")  # 95 uso primario usm
        self.comboBox_tipo_legante_usm.setEditText("")  # 95 uso primario usm
        self.comboBox_rifinitura_usm.setEditText("")  # 95 uso primario usm
        self.comboBox_materiale_p.setEditText("")  # 95 uso primario usm
        self.comboBox_consistenza_p.setEditText("")  # 95 uso primario usm
        self.mQgsFileWidget.clear()
    def fill_fields(self, n=0):
        self.rec_num = n
        try:
            str(self.comboBox_sito.setEditText(self.DATA_LIST[self.rec_num].sito))  # 1 - Sito
            str(self.comboBox_area.setEditText(self.DATA_LIST[self.rec_num].area))  # 2 - Area
            self.lineEdit_us.setText(str(self.DATA_LIST[self.rec_num].us))  # 3 - US
            str(self.comboBox_def_strat.setEditText(self.DATA_LIST[self.rec_num].d_stratigrafica))  # 4 - Definizione stratigrafica
            str(self.comboBox_def_intepret.setEditText(self.DATA_LIST[self.rec_num].d_interpretativa))  # 5 - Definizione intepretata
            str(self.textEdit_descrizione.setText(self.DATA_LIST[self.rec_num].descrizione))  # 6 - descrizione
            str(self.textEdit_interpretazione.setText(self.DATA_LIST[self.rec_num].interpretazione))  # 7 - interpretazione
            str(self.comboBox_per_iniz.setEditText(self.DATA_LIST[self.rec_num].periodo_iniziale))  # 8 - periodo iniziale
            str(self.comboBox_fas_iniz.setEditText(self.DATA_LIST[self.rec_num].fase_iniziale))  # 9 - fase iniziale
            str(self.comboBox_per_fin.setEditText(self.DATA_LIST[self.rec_num].periodo_finale))  # 10 - periodo finale iniziale
            str(self.comboBox_fas_fin.setEditText(self.DATA_LIST[self.rec_num].fase_finale))  # 11 - fase finale
            str(self.comboBox_scavato.setEditText(self.DATA_LIST[self.rec_num].scavato))  # 12 - scavato
            str(self.lineEdit_attivita.setText(self.DATA_LIST[self.rec_num].attivita))  # 13 - attivita
            str(self.lineEdit_anno.setText(self.DATA_LIST[self.rec_num].anno_scavo))  # 14 - anno scavo
            str(self.comboBox_metodo.setEditText(self.DATA_LIST[self.rec_num].metodo_di_scavo))  # 15 - metodo
            self.tableInsertData("self.tableWidget_inclusi", self.DATA_LIST[self.rec_num].inclusi)  # 16 - inclusi
            self.tableInsertData("self.tableWidget_campioni", self.DATA_LIST[self.rec_num].campioni)  # 17 - campioni
            self.tableInsertData("self.tableWidget_organici", self.DATA_LIST[self.rec_num].componenti_organici)  # organici
            self.tableInsertData("self.tableWidget_inorganici", self.DATA_LIST[self.rec_num].componenti_inorganici)  # inorganici
            self.tableInsertData("self.tableWidget_rapporti", self.DATA_LIST[self.rec_num].rapporti)  # 18 - rapporti
            str(self.lineEdit_data_schedatura.setText(self.DATA_LIST[self.rec_num].data_schedatura))  # 19 - data schedatura
            str(self.comboBox_schedatore.setEditText(self.DATA_LIST[self.rec_num].schedatore))  # 20 - schedatore
            str(self.comboBox_formazione.setEditText(self.DATA_LIST[self.rec_num].formazione))  # 21 - formazione
            str(self.comboBox_conservazione.setEditText(self.DATA_LIST[self.rec_num].stato_di_conservazione))  # 22 - conservazione
            str(self.comboBox_colore.setEditText(self.DATA_LIST[self.rec_num].colore))  # 23 - colore
            str(self.comboBox_consistenza.setEditText(self.DATA_LIST[self.rec_num].consistenza))  # 24 - consistenza
            str(self.comboBox_struttura.setEditText(self.DATA_LIST[self.rec_num].struttura)) # 25 - struttura
            if not self.DATA_LIST[self.rec_num].cont_per:
                self.lineEdit_codice_periodo.setText("")
            else:
                self.lineEdit_codice_periodo.setText(str(self.DATA_LIST[self.rec_num].cont_per))  # 26 - codice periodo
            if not self.DATA_LIST[self.rec_num].order_layer:
                self.lineEditOrderLayer.setText("")
            else:
                self.lineEditOrderLayer.setText(str(self.DATA_LIST[self.rec_num].order_layer))  # 27 - order layer
            self.tableInsertData("self.tableWidget_documentazione",self.DATA_LIST[self.rec_num].documentazione)  # 28 - documentazione
            str(self.comboBox_unita_tipo.setEditText(self.DATA_LIST[self.rec_num].unita_tipo))  # 29 unita tipo
            str(self.comboBox_settore.setEditText(self.DATA_LIST[self.rec_num].settore))  # 30 - settore
            str(self.lineEdit_quadrato.setText(self.DATA_LIST[self.rec_num].quad_par))  # 31 quadrato
            str(self.lineEdit_ambiente.setText(self.DATA_LIST[self.rec_num].ambient))  # 32 ambiente
            str(self.lineEdit_saggio.setText(self.DATA_LIST[self.rec_num].saggio))  # 33 saggio
            str(self.textEdit_elementi_datanti.setText(self.DATA_LIST[self.rec_num].elem_datanti))  # 34 - elemtenti_datanti
            str(self.comboBox_funz_statica_usm.setEditText(self.DATA_LIST[self.rec_num].funz_statica))  # 35 - funz statica
            str(self.comboBox_lavorazione_usm.setEditText(self.DATA_LIST[self.rec_num].lavorazione))  # 36 lavorazione usm
            str(self.lineEdit_spessore_giunti_usm.setText(self.DATA_LIST[self.rec_num].spess_giunti))  # 37 spessore giunti usm
            str(self.lineEdit_letti_di_posa_giunti_usm.setText(self.DATA_LIST[self.rec_num].letti_posa)) #38 letti_posa
            str(self.lineEdit_h_modulo_c_corsi_usm.setText(self.DATA_LIST[self.rec_num].alt_mod)) #39 altezza modulo corsi
            str(self.comboBox_unita_edilizia_riassuntiva_usm.setEditText(self.DATA_LIST[self.rec_num].un_ed_riass)) #40 unita edilizia riassuntiva
            str(self.comboBox_reimpiego_usm.setEditText(self.DATA_LIST[self.rec_num].reimp))  #41 reimpiego
            str(self.comboBox_posa_in_opera_usm.setEditText(self.DATA_LIST[self.rec_num].posa_opera)) #42 posa opera
            if not self.DATA_LIST[self.rec_num].quota_min_usm:
                str(self.lineEdit_qmin_usm.setText(""))
            else:
                self.lineEdit_qmin_usm.setText(str(self.DATA_LIST[self.rec_num].quota_min_usm))  # 43 - qmin usm
            if not self.DATA_LIST[self.rec_num].quota_max_usm:
               str(self.lineEdit_qmax_usm.setText(""))
            else:
               self.lineEdit_qmax_usm.setText(str(self.DATA_LIST[self.rec_num].quota_max_usm))  # 44 - qmax usm
            str(self.comboBox_consistenza_legante_usm.setEditText(self.DATA_LIST[self.rec_num].cons_legante))  # 45 - cons legante
            self.tableInsertData("self.tableWidget_colore_legante_usm", self.DATA_LIST[self.rec_num].col_legante) ## 46 - col legante usm
            self.tableInsertData("self.tableWidget_inclusi_leganti_usm", self.DATA_LIST[self.rec_num].aggreg_legante) # 47 aggregati legante usm
            self.tableInsertData("self.tableWidget_consistenza_texture_mat_usm", self.DATA_LIST[self.rec_num].con_text_mat) # 48 - con text mat
            self.tableInsertData("self.tableWidget_colore_materiale_usm", self.DATA_LIST[self.rec_num].col_materiale) # 49 - col mat
            self.tableInsertData("self.tableWidget_inclusi_materiali_usm",self.DATA_LIST[self.rec_num].inclusi_materiali_usm)  # 50  inclusi materiali usm
            str(self.lineEdit_n_catalogo_generale.setText(self.DATA_LIST[self.rec_num].n_catalogo_generale))  # 51 nr catalogo generale campi aggiunti per archeo 3.0 e allineamento ICCD
            str(self.lineEdit_n_catalogo_interno.setText(self.DATA_LIST[self.rec_num].n_catalogo_interno))  # 52 nr catalogo interno
            str(self.lineEdit_n_catalogo_internazionale.setText(self.DATA_LIST[self.rec_num].n_catalogo_internazionale))  # 53 nr catalogo internazionale
            str(self.comboBox_soprintendenza.setEditText(self.DATA_LIST[self.rec_num].soprintendenza))  # 54 nr soprintendenza
            if not self.DATA_LIST[self.rec_num].quota_relativa:
                str(self.lineEdit_quota_relativa.setText(""))                   # 55
            else:
                self.lineEdit_quota_relativa.setText(str(self.DATA_LIST[self.rec_num].quota_relativa))
            if not self.DATA_LIST[self.rec_num].quota_abs:
                str(self.lineEdit_quota_abs.setText(""))                   # 56
            else:
                self.lineEdit_quota_abs.setText(str(self.DATA_LIST[self.rec_num].quota_abs))
            str(self.lineEdit_ref_tm.setText(self.DATA_LIST[self.rec_num].ref_tm))  # 57 ref tm
            str(self.comboBox_ref_ra.setDefaultText(self.DATA_LIST[self.rec_num].ref_ra))  # 58 ref ra
            str(self.lineEdit_ref_n.setText(self.DATA_LIST[self.rec_num].ref_n))  # 59 ref n
            str(self.comboBox_posizione.setEditText(self.DATA_LIST[self.rec_num].posizione))  # 60 posizione
            str(self.lineEdit_criteri_distinzione.setText(self.DATA_LIST[self.rec_num].criteri_distinzione))  # 61 criteri distinzione
            str(self.comboBox_modo_formazione.setEditText(self.DATA_LIST[self.rec_num].modo_formazione))  # 62 modo formazione
            if not self.DATA_LIST[self.rec_num].lunghezza_max:
                str(self.lineEdit_lunghezza_max.setText(""))
            else:
                self.lineEdit_lunghezza_max.setText(str(self.DATA_LIST[self.rec_num].lunghezza_max))  # 65 lunghezza max
            if not self.DATA_LIST[self.rec_num].altezza_max:
                str(self.lineEdit_altezza_max.setText(""))
            else:
                self.lineEdit_altezza_max.setText(str(self.DATA_LIST[self.rec_num].altezza_max))  # 66 altezza max
            if not self.DATA_LIST[self.rec_num].altezza_min:
                str(self.lineEdit_altezza_min.setText(""))
            else:
                self.lineEdit_altezza_min.setText(str(self.DATA_LIST[self.rec_num].altezza_min))  # 67 altezza min
            if not self.DATA_LIST[self.rec_num].profondita_max:
                str(self.lineEdit_profondita_max.setText(""))
            else:
                self.lineEdit_profondita_max.setText(str(
                    self.DATA_LIST[self.rec_num].profondita_max))  # 68 profondita_max
            if not self.DATA_LIST[self.rec_num].profondita_min:
                str(self.lineEdit_profondita_min.setText(""))
            else:
                self.lineEdit_profondita_min.setText(str(
                    self.DATA_LIST[self.rec_num].profondita_min))  # 69 profondita min
            if not self.DATA_LIST[self.rec_num].larghezza_media:
                str(self.lineEdit_larghezza_media.setText(""))
            else:
                self.lineEdit_larghezza_media.setText(str(
                    self.DATA_LIST[self.rec_num].larghezza_media))  # 70 larghezza media
            if not self.DATA_LIST[self.rec_num].quota_max_abs:
                str(self.lineEdit_quota_max_abs.setText(""))
            else:
                self.lineEdit_quota_max_abs.setText(str(self.DATA_LIST[self.rec_num].quota_max_abs))  # 71 quota_max_abs
            if not self.DATA_LIST[self.rec_num].quota_max_rel:
                str(self.lineEdit_quota_max_rel.setText(""))
            else:
                self.lineEdit_quota_max_rel.setText(str(
                    self.DATA_LIST[self.rec_num].quota_max_rel))  # 72 quota_max_rel
            if not self.DATA_LIST[self.rec_num].quota_min_abs:
                str(self.lineEdit_quota_min_abs.setText(""))
            else:
                self.lineEdit_quota_min_abs.setText(str(self.DATA_LIST[self.rec_num].quota_min_abs))  # 73 quota_min_abs
            if not self.DATA_LIST[self.rec_num].quota_min_rel:
                str(self.lineEdit_quota_min_rel.setText(""))
            else:
                self.lineEdit_quota_min_rel.setText(str(self.DATA_LIST[self.rec_num].quota_min_rel))  # 74 quota_min_rel
            str(self.textEdit_osservazioni.setText(self.DATA_LIST[self.rec_num].osservazioni))  # 75 osservazioni
            str(self.comboBox_datazione.setEditText(self.DATA_LIST[self.rec_num].datazione))  # 76 datazione
            str(self.comboBox_flottazione.setEditText(self.DATA_LIST[self.rec_num].flottazione))  # 77 flottazione
            str(self.comboBox_setacciatura.setEditText(self.DATA_LIST[self.rec_num].setacciatura))  # 78 setacciatura
            str(self.comboBox_affidabilita.setEditText(self.DATA_LIST[self.rec_num].affidabilita))        # 79 affidabilita
            str(self.comboBox_direttore_us.setEditText(self.DATA_LIST[self.rec_num].direttore_us))  # 80 direttore us
            str(self.comboBox_responsabile_us.setEditText(self.DATA_LIST[self.rec_num].responsabile_us))  # 81 responsabile us
            str(self.lineEdit_cod_ente_schedatore.setText(self.DATA_LIST[self.rec_num].cod_ente_schedatore))  # 82 cod ente schedatore
            str(self.lineEdit_data_rilevazione.setText(self.DATA_LIST[self.rec_num].data_rilevazione))  # 83 data rilevazione
            str(self.lineEdit_data_rielaborazione.setText(self.DATA_LIST[self.rec_num].data_rielaborazione))  # 84 data rielaborazione
            if not self.DATA_LIST[self.rec_num].lunghezza_usm:
                str(self.lineEdit_lunghezza_usm.setText(""))
            else:
                self.lineEdit_lunghezza_usm.setText(str(self.DATA_LIST[self.rec_num].lunghezza_usm))  # 85 lunghezza usm
            if not self.DATA_LIST[self.rec_num].altezza_usm:
                str(self.lineEdit_altezza_usm.setText(""))
            else:
                self.lineEdit_altezza_usm.setText(str(self.DATA_LIST[self.rec_num].altezza_usm))  # 86 altezza usm
            if not self.DATA_LIST[self.rec_num].spessore_usm:
                str(self.lineEdit_spessore_usm.setText(""))
            else:
                self.lineEdit_spessore_usm.setText(str(self.DATA_LIST[self.rec_num].spessore_usm))  # 87 spessore usm
            str(self.comboBox_tecnica_muraria_usm.setEditText(self.DATA_LIST[self.rec_num].tecnica_muraria_usm))  # 88 tecnica muraria usm
            str(self.comboBox_modulo_usm.setEditText(self.DATA_LIST[self.rec_num].modulo_usm))  # 89 modulo usm
            str(self.lineEdit_campioni_malta_usm.setText(self.DATA_LIST[self.rec_num].campioni_malta_usm))  # 90 campioni malta usm
            str(self.lineEdit_campioni_mattone_usm.setText(self.DATA_LIST[self.rec_num].campioni_mattone_usm))  # 91 campioni mattone usm
            str(self.lineEdit_campioni_pietra_usm.setText(self.DATA_LIST[self.rec_num].campioni_pietra_usm))  # 92 campioni pietra usm
            str(self.lineEdit_provenienza_materiali_usm.setText(self.DATA_LIST[self.rec_num].provenienza_materiali_usm))  # 93 provenienza_materiali_usm
            str(self.lineEdit_criteri_distinzione_usm.setText(self.DATA_LIST[self.rec_num].criteri_distinzione_usm))  # 94 criteri distinzione usm
            str(self.comboBox_uso_primario_usm.setEditText(self.DATA_LIST[self.rec_num].uso_primario_usm))  # 95 uso primario usm
            str(self.comboBox_tipologia_opera.setEditText(self.DATA_LIST[self.rec_num].tipologia_opera)) 
            str(self.comboBox_sezione_muraria.setEditText(self.DATA_LIST[self.rec_num].sezione_muraria)) 
            str(self.comboBox_superficie_analizzata.setEditText(self.DATA_LIST[self.rec_num].superficie_analizzata)) 
            str(self.comboBox_orientamento.setEditText(self.DATA_LIST[self.rec_num].orientamento)) 
            str(self.comboBox_materiali_lat.setEditText(self.DATA_LIST[self.rec_num].materiali_lat)) 
            str(self.comboBox_lavorazione_lat.setEditText(self.DATA_LIST[self.rec_num].lavorazione_lat)) 
            str(self.comboBox_consistenza_lat.setEditText(self.DATA_LIST[self.rec_num].consistenza_lat)) 
            str(self.comboBox_forma_lat.setEditText(self.DATA_LIST[self.rec_num].forma_lat)) 
            str(self.comboBox_colore_lat.setEditText(self.DATA_LIST[self.rec_num].colore_lat)) 
            str(self.comboBox_impasto_lat.setEditText(self.DATA_LIST[self.rec_num].impasto_lat)) 
            str(self.comboBox_forma_p.setEditText(self.DATA_LIST[self.rec_num].forma_p)) 
            str(self.comboBox_colore_p.setEditText(self.DATA_LIST[self.rec_num].colore_p)) 
            str(self.comboBox_taglio_p.setEditText(self.DATA_LIST[self.rec_num].taglio_p)) 
            str(self.comboBox_posa_opera_p.setEditText(self.DATA_LIST[self.rec_num].posa_opera_p)) 
            str(self.comboBox_inerti_usm.setEditText(self.DATA_LIST[self.rec_num].inerti_usm)) 
            str(self.comboBox_tipo_legante_usm.setEditText(self.DATA_LIST[self.rec_num].tipo_legante_usm)) 
            str(self.comboBox_rifinitura_usm.setEditText(self.DATA_LIST[self.rec_num].rifinitura_usm)) 
            str(self.comboBox_materiale_p.setEditText(self.DATA_LIST[self.rec_num].materiale_p)) 
            str(self.comboBox_consistenza_p.setEditText(self.DATA_LIST[self.rec_num].consistenza_p)) 
            self.tableInsertData("self.tableWidget_rapporti2", self.DATA_LIST[self.rec_num].rapporti2)
            str(self.mQgsFileWidget.setText(self.DATA_LIST[self.rec_num].doc_usv)) # 18 - rapporti
            # gestione tool
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
        # QMessageBox.warning(self, "Errore", str(self.comboBox_per_fin.currentText()),  QMessageBox.Ok)
        # TableWidget
        ##Rapporti
        rapporti = self.table2dict("self.tableWidget_rapporti")
        rapporti2 = self.table2dict("self.tableWidget_rapporti2")
        ##Inclusi
        inclusi = self.table2dict("self.tableWidget_inclusi")
        ##Campioni
        campioni = self.table2dict("self.tableWidget_campioni")
        ##Organici
        organici = self.table2dict("self.tableWidget_organici")
        ##Inorganici
        inorganici = self.table2dict("self.tableWidget_inorganici")
        ##Documentazione
        documentazione = self.table2dict("self.tableWidget_documentazione")
        ##Inclusi materiali aggregati
        inclusi_mat_usm = self.table2dict("self.tableWidget_inclusi_materiali_usm")
        ##Inclusi leganti usm
        inclusi_leganti_usm = self.table2dict("self.tableWidget_inclusi_leganti_usm")
        colore_legante_usm = self.table2dict("self.tableWidget_colore_legante_usm")
        con_text_materiale_usm = self.table2dict("self.tableWidget_consistenza_texture_mat_usm")
        col_materiale_usm = self.table2dict("self.tableWidget_colore_materiale_usm")
        #list_foto = self.table2dict("self.tableWidget_foto")
        if self.lineEditOrderLayer.text() == "":
            order_layer = 0
        else:
            order_layer = self.lineEditOrderLayer.text()
        if self.lineEdit_qmin_usm.text() == "":
            qmin_usm = None
        else:
            qmin_usm = self.lineEdit_qmin_usm.text()
        if self.lineEdit_qmax_usm.text() == "":
            qmax_usm = None
        else:
            qmax_usm = self.lineEdit_qmax_usm.text()
        ##quota relativa
        if self.lineEdit_quota_relativa.text() == "":
            quota_relativa = None
        else:
            quota_relativa = self.lineEdit_quota_relativa.text()
        ##quota abs
        if self.lineEdit_quota_abs.text() == "":
            quota_abs = None
        else:
            quota_abs = self.lineEdit_quota_abs.text().replace(",", ".")
        ##lunghezza max
        if self.lineEdit_lunghezza_max.text() == "":
            lunghezza_max = None
        else:
            lunghezza_max = self.lineEdit_lunghezza_max.text()
        ##altezza max
        if self.lineEdit_altezza_max.text() == "":
            altezza_max = None
        else:
            altezza_max = self.lineEdit_altezza_max.text()
        ##altezza min
        if self.lineEdit_altezza_min.text() == "":
            altezza_min = None
        else:
            altezza_min = self.lineEdit_altezza_min.text()
        ##profondita max
        if self.lineEdit_profondita_max.text() == "":
            profondita_max = None
        else:
            profondita_max = self.lineEdit_profondita_max.text()
        ##profondita min
        if self.lineEdit_profondita_min.text() == "":
            profondita_min = None
        else:
            profondita_min = self.lineEdit_profondita_min.text()
        ##larghezza media
        if self.lineEdit_larghezza_media.text() == "":
            larghezza_media = None
        else:
            larghezza_media = self.lineEdit_larghezza_media.text()
        ##quota max abs
        if self.lineEdit_quota_max_abs.text() == "":
            quota_max_abs = None
        else:
            quota_max_abs = self.lineEdit_quota_max_abs.text()
        ##quota max relativa
        if self.lineEdit_quota_max_rel.text() == "":
            quota_max_rel = None
        else:
            quota_max_rel = self.lineEdit_quota_max_rel.text()
        ##quota min abs
        if self.lineEdit_quota_min_abs.text() == "":
            quota_min_abs = None
        else:
            quota_min_abs = self.lineEdit_quota_min_abs.text()
        ##quota min relativa
        if self.lineEdit_quota_min_rel.text() == "":
            quota_min_rel = None
        else:
            quota_min_rel = self.lineEdit_quota_min_rel.text()
        ##lunghezza usm
        if self.lineEdit_lunghezza_usm.text() == "":
            lunghezza_usm = None
        else:
            lunghezza_usm = self.lineEdit_lunghezza_usm.text()
        ##altezza usm
        if self.lineEdit_altezza_usm.text() == "":
            altezza_usm = None
        else:
            altezza_usm = self.lineEdit_altezza_usm.text()
        ##spessore usm
        if self.lineEdit_spessore_usm.text() == "":
            spessore_usm = None
        else:
            spessore_usm = self.lineEdit_spessore_usm.text()
            # data
        self.DATA_LIST_REC_TEMP = [
            str(self.comboBox_sito.currentText()),  # 1 - Sito
            str(self.comboBox_area.currentText()),  # 2 - Area
            str(self.lineEdit_us.text()),  # 3 - US
            str(self.comboBox_def_strat.currentText()),  # 4 - Definizione stratigrafica
            str(self.comboBox_def_intepret.currentText()),  # 5 - Definizione intepretata
            str(self.textEdit_descrizione.toPlainText()),  # 6 - descrizione
            str(self.textEdit_interpretazione.toPlainText()),  # 7 - interpretazione
            str(self.comboBox_per_iniz.currentText()),  # 8 - periodo iniziale
            str(self.comboBox_fas_iniz.currentText()),  # 9 - fase iniziale
            str(self.comboBox_per_fin.currentText()),  # 10 - periodo finale iniziale
            str(self.comboBox_fas_fin.currentText()),  # 11 - fase finale
            str(self.comboBox_scavato.currentText()),  # 12 - scavato
            str(self.lineEdit_attivita.text()),  # 13 - attivita
            str(self.lineEdit_anno.text()),  # 14 - anno scavo
            str(self.comboBox_metodo.currentText()),  # 15 - metodo
            str(inclusi),  # 16 - inclusi
            str(campioni),  # 17 - campioni
            str(rapporti),  # 18 - rapporti
            #str(organici),
            #str(inorganici),
            str(self.lineEdit_data_schedatura.text()),  # 19 - data schedatura
            str(self.comboBox_schedatore.currentText()),  # 20 - schedatore
            str(self.comboBox_formazione.currentText()),  # 21 - formazione
            str(self.comboBox_conservazione.currentText()),  # 22 - conservazione
            str(self.comboBox_colore.currentText()),  # 23 - colore
            str(self.comboBox_consistenza.currentText()),  # 24 - consistenza
            str(self.comboBox_struttura.currentText()),  # 25 - struttura
            str(self.lineEdit_codice_periodo.text()),  # 26 - codice periodo
            str(order_layer),  # 27 - order layer era str(order_layer)
            str(documentazione),
            str(self.comboBox_unita_tipo.currentText()),  # 29 us_tipo            NUOVI CAMPI NUOVI CAMPI
            str(self.comboBox_settore.currentText()),  # 30 settore
            str(self.lineEdit_quadrato.text()),  # 31 quadrato
            str(self.lineEdit_ambiente.text()),  # 32 ambiente
            str(self.lineEdit_saggio.text()),  # 33 saggio
            str(self.textEdit_elementi_datanti.toPlainText()),  # 34 elementi datanti
            str(self.comboBox_funz_statica_usm.currentText()),  # 35 funzione statica
            str(self.comboBox_lavorazione_usm.currentText()),  # 36 lavorazione usm
            str(self.lineEdit_spessore_giunti_usm.text()),  # 37 spessore giunti
            str(self.lineEdit_letti_di_posa_giunti_usm.text()),  # 38 letti posa giunti usm
            str(self.lineEdit_h_modulo_c_corsi_usm.text()),  # 39 altezza modulo corsi usm
            str(self.comboBox_unita_edilizia_riassuntiva_usm.currentText()),  # 40 unita edilizia riassuntiva
            str(self.comboBox_reimpiego_usm.currentText()),  # 41 unita edilizia riassuntiva
            str(self.comboBox_posa_in_opera_usm.currentText()),  # 42 posa in opera
            str(qmin_usm),  # 43 quota minima
            str(qmax_usm),  # 44 quota massima
            str(self.comboBox_consistenza_legante_usm.currentText()),  # 45 consitenza legante usm
            str(colore_legante_usm),  # 46 colore legante usm
            str(inclusi_leganti_usm),  # 47 aggregati leganti usm
            str(con_text_materiale_usm),  # 48 consistenza text mat
            str(col_materiale_usm),  # 49 colore materiale usm
            str(inclusi_mat_usm), # 50 inclusi_mat_usm
            str(self.lineEdit_n_catalogo_generale.text()), # 51 nr catalogo generale campi aggiunti per archeo 3.0 e allineamento ICCD
            str(self.lineEdit_n_catalogo_interno.text()), # 52 nr catalogo interno
            str(self.lineEdit_n_catalogo_internazionale.text()), # 53 nr catalogo internazionale
            str(self.comboBox_soprintendenza.currentText()), # 54 nr soprintendenza
            str(quota_relativa),  # 55 quota relativa
            str(quota_abs),  # 56 quota abs
            str(self.lineEdit_ref_tm.text()),  # 57 ref tm
            str(self.comboBox_ref_ra.currentText()),  # 58 ref ra
            str(self.lineEdit_ref_n.text()),  # 59 ref n
            str(self.comboBox_posizione.currentText()),  # 60 posizione
            str(self.lineEdit_criteri_distinzione.text()), # 61 criteri distinzione
            str(self.comboBox_modo_formazione.currentText()), # 62 modo formazione
            str(organici), # 63 componenti organici
            str(inorganici), # 64 componenti inorganici
            str(lunghezza_max),  # 65
            str(altezza_max),  # 66
            str(altezza_min),  # 67
            str(profondita_max),  # 68
            str(profondita_min),  # 69
            str(larghezza_media),  # 70
            str(quota_max_abs),  # 71
            str(quota_max_rel),  # 72
            str(quota_min_abs),  # 73
            str(quota_min_rel),  # 74
            str(self.textEdit_osservazioni.toPlainText()),  # 75 osservazioni
            str(self.comboBox_datazione.currentText()),  # 76 datazione
            str(self.comboBox_flottazione.currentText()),  # 77 flottazione
            str(self.comboBox_setacciatura.currentText()),  # 78 setacciatura
            str(self.comboBox_affidabilita.currentText()),  # 79 affidabilita
            str(self.comboBox_direttore_us.currentText()),  # 80 direttore us
            str(self.comboBox_responsabile_us.currentText()), # 81 responsabile us
            str(self.lineEdit_cod_ente_schedatore.text()), # 82 cod ente schedatore
            str(self.lineEdit_data_rilevazione.text()),  # 83 data rilevazione
            str(self.lineEdit_data_rielaborazione.text()), # 84 data rielaborazione
            str(lunghezza_usm),  # 85
            str(altezza_usm),  # 86
            str(spessore_usm),  # 87
            str(self.comboBox_tecnica_muraria_usm.currentText()), # 88 tecnica muraria usm
            str(self.comboBox_modulo_usm.currentText()),  # 89 modulo usm
            str(self.lineEdit_campioni_malta_usm.text()), # 90 campioni malta usm
            str(self.lineEdit_campioni_mattone_usm.text()), # 91 campioni mattone usm
            str(self.lineEdit_campioni_pietra_usm.text()), # 92 campioni pietra usm
            str(self.lineEdit_provenienza_materiali_usm.text()), # 93 provenienza_materiali_usm
            str(self.lineEdit_criteri_distinzione_usm.text()), # 94 criteri distinzione usm
            str(self.comboBox_uso_primario_usm.currentText()),  # 95 uso primario usm
            str(self.comboBox_tipologia_opera.currentText()),  # 95 uso primario usm
            str(self.comboBox_sezione_muraria.currentText()),  # 95 uso primario usm
            str(self.comboBox_superficie_analizzata.currentText()),  # 95 uso primario usm
            str(self.comboBox_orientamento.currentText()),  # 95 uso primario usm
            str(self.comboBox_materiali_lat.currentText()),  # 95 uso primario usm
            str(self.comboBox_lavorazione_lat.currentText()),  # 95 uso primario usm
            str(self.comboBox_consistenza_lat.currentText()),  # 95 uso primario usm
            str(self.comboBox_forma_lat.currentText()),  # 95 uso primario usm
            str(self.comboBox_colore_lat.currentText()),  # 95 uso primario usm
            str(self.comboBox_impasto_lat.currentText()),  # 95 uso primario usm
            str(self.comboBox_forma_p.currentText()),  # 95 uso primario usm
            str(self.comboBox_colore_p.currentText()),  # 95 uso primario usm
            str(self.comboBox_taglio_p.currentText()),  # 95 uso primario usm
            str(self.comboBox_posa_opera_p.currentText()),  # 95 uso primario usm
            #str(list_foto)
            str(self.comboBox_inerti_usm.currentText()),  # 95 uso primario usm
            str(self.comboBox_tipo_legante_usm.currentText()),  # 95 uso primario usm
            str(self.comboBox_rifinitura_usm.currentText()),  # 95 uso primario usm
            str(self.comboBox_materiale_p.currentText()),  # 95 uso primario usm
            str(self.comboBox_consistenza_p.currentText()),  # 95 uso primario usm
            str(rapporti2),
            str(self.mQgsFileWidget.text()),# 18 - rapporti
        ]
    def set_LIST_REC_CORR(self):
        self.DATA_LIST_REC_CORR = []
        for i in self.TABLE_FIELDS:
            self.DATA_LIST_REC_CORR.append(eval("unicode(self.DATA_LIST[self.REC_CORR]." + i + ")"))
    def records_equal_check(self):
        # self.set_sito()
        self.set_LIST_REC_TEMP()
        self.set_LIST_REC_CORR()
        """
        area TEST
        tes = str(self.DATA_LIST_REC_CORR) + str(self.DATA_LIST_REC_TEMP)
        self.testing("C:\\Users\\Luca\\pyarchinit_Test_folder\\tes_equal.txt", tes)
        #QMessageBox.warning(self, "Errore", str(self.DATA_LIST_REC_CORR) + str(self.DATA_LIST_REC_TEMP),  QMessageBox.Ok)
        """
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
    def setTableEnable(self, t, v):
        tab_names = t
        value = v
        for tn in tab_names:
            cmd = '{}{}{}{}'.format(tn, '.setEnabled(', v, ')')
            eval(cmd)
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
    def on_pushButton_open_dir_matrix_pressed(self):
        HOME = os.environ['PYARCHINIT_HOME']
        path = '{}{}{}'.format(HOME, os.sep, "pyarchinit_Matrix_folder")
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path]) 
    def on_pushButton_open_dir_tavole_pressed(self):
        HOME = os.environ['PYARCHINIT_HOME']
        path = '{}{}{}'.format(HOME, os.sep, "pyarchinit_MAPS_folder")
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])         
