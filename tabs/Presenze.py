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
import sys
from datetime import date, datetime
from qgis.PyQt.QtCore import QDate, QTimer
from qgis.PyQt.QtWidgets import QDialog, QMessageBox, QFileDialog
from qgis.PyQt.uic import loadUiType
from qgis.core import QgsSettings

from ..gui.pyarchinitConfigDialog import pyArchInitDialog_Config
from ..gui.sortpanelmain import SortPanelMain
from ..modules.db.pyarchinit_conn_strings import Connection
from ..modules.db.pyarchinit_db_manager import get_db_manager
from ..modules.db.pyarchinit_utility import Utility
from ..modules.utility.pyarchinit_error_check import Error_check
from ..modules.utility.pyarchinit_theme_manager import ThemeManager

MAIN_DIALOG_CLASS, _ = loadUiType(
    os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'Presenze.ui'))


class pyarchinit_Presenze(QDialog, MAIN_DIALOG_CLASS):
    L = QgsSettings().value("locale/userLocale", "it", type=str)[:2]
    if L == 'it':
        MSG_BOX_TITLE = "PyArchInit - Scheda Presenze"
    elif L == 'en':
        MSG_BOX_TITLE = "PyArchInit - Attendance Form"
    elif L == 'de':
        MSG_BOX_TITLE = "PyArchInit - Anwesenheitsformular"
    elif L == 'es':
        MSG_BOX_TITLE = "PyArchInit - Asistencia de Obra"
    elif L == 'fr':
        MSG_BOX_TITLE = "PyArchInit - Présences de Chantier"
    elif L == 'ar':
        MSG_BOX_TITLE = "PyArchInit - حضور الموقع"
    elif L == 'ca':
        MSG_BOX_TITLE = "PyArchInit - Assistència d'Obra"
    elif L == 'ro':
        MSG_BOX_TITLE = "PyArchInit - Prezențe Șantier"
    elif L == 'pt':
        MSG_BOX_TITLE = "PyArchInit - Presenças de Obra"
    elif L == 'el':
        MSG_BOX_TITLE = "PyArchInit - Παρουσίες Εργοταξίου"
    else:
        MSG_BOX_TITLE = "PyArchInit - Attendance Form"

    DATA_LIST = []
    DATA_LIST_REC_CORR = []
    DATA_LIST_REC_TEMP = []
    REC_CORR = 0
    REC_TOT = 0
    SITO = pyArchInitDialog_Config

    if L == 'it':
        STATUS_ITEMS = {"b": "Usa", "f": "Trova", "n": "Nuovo Record"}
    elif L == 'de':
        STATUS_ITEMS = {"b": "Aktuell", "f": "Finden", "n": "Neuer Rekord"}
    elif L == 'es':
        STATUS_ITEMS = {"b": "navegar", "f": "buscar", "n": "nuevo registro"}
    elif L == 'fr':
        STATUS_ITEMS = {"b": "parcourir", "f": "rechercher", "n": "nouveau"}
    elif L == 'ar':
        STATUS_ITEMS = {"b": "تصفح", "f": "بحث", "n": "جديد"}
    elif L == 'ca':
        STATUS_ITEMS = {"b": "navegar", "f": "cercar", "n": "nou registre"}
    elif L == 'ro':
        STATUS_ITEMS = {"b": "navigare", "f": "căutare", "n": "înregistrare nouă"}
    elif L == 'pt':
        STATUS_ITEMS = {"b": "navegar", "f": "pesquisar", "n": "novo registo"}
    elif L == 'el':
        STATUS_ITEMS = {"b": "περιήγηση", "f": "αναζήτηση", "n": "νέα εγγραφή"}
    else:
        STATUS_ITEMS = {"b": "Current", "f": "Find", "n": "New Record"}

    BROWSE_STATUS = "b"
    SORT_MODE = 'asc'

    if L == 'it':
        SORTED_ITEMS = {"n": "Non ordinati", "o": "Ordinati"}
    elif L == 'de':
        SORTED_ITEMS = {"n": "Nicht sortiert", "o": "Sortiert"}
    elif L == 'es':
        SORTED_ITEMS = {"n": "No ordenados", "o": "Ordenados"}
    elif L == 'fr':
        SORTED_ITEMS = {"n": "Non triés", "o": "Triés"}
    elif L == 'ar':
        SORTED_ITEMS = {"n": "غير مرتب", "o": "مرتب"}
    elif L == 'ca':
        SORTED_ITEMS = {"n": "No ordenats", "o": "Ordenats"}
    elif L == 'ro':
        SORTED_ITEMS = {"n": "Nesortat", "o": "Sortat"}
    elif L == 'pt':
        SORTED_ITEMS = {"n": "Não ordenados", "o": "Ordenados"}
    elif L == 'el':
        SORTED_ITEMS = {"n": "Μη ταξινομημένα", "o": "Ταξινομημένα"}
    else:
        SORTED_ITEMS = {"n": "Not sorted", "o": "Sorted"}

    SORT_STATUS = "n"
    UTILITY = Utility()
    DB_MANAGER = ""
    TABLE_NAME = 'presenze_table'
    MAPPER_TABLE_CLASS = "PRESENZE"
    NOME_SCHEDA = "Scheda Presenze"
    ID_TABLE = "id_presenza"

    if L == 'it':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Sito": "sito",
            "ID Personale": "id_personale",
            "Data": "data",
            "Ora ingresso": "ora_ingresso",
            "Ora uscita": "ora_uscita",
            "Ore ordinarie": "ore_ordinarie",
            "Ore straordinario": "ore_straordinario",
            "Tipo giornata": "tipo_giornata",
            "Turno": "turno",
            "Area di lavoro": "area_lavoro",
            "Note": "note",
            "Costo giornata": "costo_giornata"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Sito",
            "ID Personale",
            "Data",
            "Tipo giornata",
            "Turno",
            "Area di lavoro"
        ]
    elif L == 'en':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Site": "sito",
            "Personnel ID": "id_personale",
            "Date": "data",
            "Clock In": "ora_ingresso",
            "Clock Out": "ora_uscita",
            "Regular Hours": "ore_ordinarie",
            "Overtime Hours": "ore_straordinario",
            "Day Type": "tipo_giornata",
            "Shift": "turno",
            "Work Area": "area_lavoro",
            "Notes": "note",
            "Day Cost": "costo_giornata"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Site",
            "Personnel ID",
            "Date",
            "Day Type",
            "Shift",
            "Work Area"
        ]
    elif L == 'de':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Fundort": "sito",
            "Personal-ID": "id_personale",
            "Datum": "data",
            "Arbeitsbeginn": "ora_ingresso",
            "Arbeitsende": "ora_uscita",
            "Regelstunden": "ore_ordinarie",
            "Ueberstunden": "ore_straordinario",
            "Tagesart": "tipo_giornata",
            "Schicht": "turno",
            "Arbeitsbereich": "area_lavoro",
            "Anmerkungen": "note",
            "Tageskosten": "costo_giornata"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Fundort",
            "Personal-ID",
            "Datum",
            "Tagesart",
            "Schicht",
            "Arbeitsbereich"
        ]
    elif L == 'es':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Sitio": "sito",
            "ID Personal": "id_personale",
            "Fecha": "data",
            "Hora entrada": "ora_ingresso",
            "Hora salida": "ora_uscita",
            "Horas ordinarias": "ore_ordinarie",
            "Horas extras": "ore_straordinario",
            "Tipo de jornada": "tipo_giornata",
            "Turno": "turno",
            "Area de trabajo": "area_lavoro",
            "Notas": "note",
            "Coste diario": "costo_giornata"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Sitio",
            "ID Personal",
            "Fecha",
            "Tipo de jornada",
            "Turno",
            "Area de trabajo"
        ]
    elif L == 'fr':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Site": "sito",
            "ID Personnel": "id_personale",
            "Date": "data",
            "Heure arrivee": "ora_ingresso",
            "Heure depart": "ora_uscita",
            "Heures normales": "ore_ordinarie",
            "Heures supplementaires": "ore_straordinario",
            "Type de journee": "tipo_giornata",
            "Equipe": "turno",
            "Zone de travail": "area_lavoro",
            "Notes": "note",
            "Cout journalier": "costo_giornata"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Site",
            "ID Personnel",
            "Date",
            "Type de journee",
            "Equipe",
            "Zone de travail"
        ]
    elif L == 'ar':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "موقع": "sito",
            "معرف الموظف": "id_personale",
            "التاريخ": "data",
            "وقت الدخول": "ora_ingresso",
            "وقت الخروج": "ora_uscita",
            "ساعات عادية": "ore_ordinarie",
            "ساعات إضافية": "ore_straordinario",
            "نوع اليوم": "tipo_giornata",
            "الوردية": "turno",
            "منطقة العمل": "area_lavoro",
            "ملاحظات": "note",
            "تكلفة اليوم": "costo_giornata"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "موقع",
            "معرف الموظف",
            "التاريخ",
            "نوع اليوم",
            "الوردية",
            "منطقة العمل"
        ]
    elif L == 'ca':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Jaciment": "sito",
            "ID Personal": "id_personale",
            "Data": "data",
            "Hora entrada": "ora_ingresso",
            "Hora sortida": "ora_uscita",
            "Hores ordinaries": "ore_ordinarie",
            "Hores extres": "ore_straordinario",
            "Tipus de jornada": "tipo_giornata",
            "Torn": "turno",
            "Area de treball": "area_lavoro",
            "Notes": "note",
            "Cost diari": "costo_giornata"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Jaciment",
            "ID Personal",
            "Data",
            "Tipus de jornada",
            "Torn",
            "Area de treball"
        ]
    elif L == 'ro':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Sit": "sito",
            "ID Personal": "id_personale",
            "Data": "data",
            "Ora intrare": "ora_ingresso",
            "Ora iesire": "ora_uscita",
            "Ore normale": "ore_ordinarie",
            "Ore suplimentare": "ore_straordinario",
            "Tip zi": "tipo_giornata",
            "Tura": "turno",
            "Zona de lucru": "area_lavoro",
            "Note": "note",
            "Cost zilnic": "costo_giornata"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Sit",
            "ID Personal",
            "Data",
            "Tip zi",
            "Tura",
            "Zona de lucru"
        ]
    elif L == 'pt':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Sitio": "sito",
            "ID Pessoal": "id_personale",
            "Data": "data",
            "Hora entrada": "ora_ingresso",
            "Hora saida": "ora_uscita",
            "Horas normais": "ore_ordinarie",
            "Horas extra": "ore_straordinario",
            "Tipo de dia": "tipo_giornata",
            "Turno": "turno",
            "Area de trabalho": "area_lavoro",
            "Notas": "note",
            "Custo diario": "costo_giornata"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Sitio",
            "ID Pessoal",
            "Data",
            "Tipo de dia",
            "Turno",
            "Area de trabalho"
        ]
    elif L == 'el':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Θέση": "sito",
            "ID Προσωπικού": "id_personale",
            "Ημερομηνία": "data",
            "Ώρα εισόδου": "ora_ingresso",
            "Ώρα εξόδου": "ora_uscita",
            "Κανονικές ώρες": "ore_ordinarie",
            "Υπερωρίες": "ore_straordinario",
            "Τύπος ημέρας": "tipo_giornata",
            "Βάρδια": "turno",
            "Περιοχή εργασίας": "area_lavoro",
            "Σημειώσεις": "note",
            "Κόστος ημέρας": "costo_giornata"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Θέση",
            "ID Προσωπικού",
            "Ημερομηνία",
            "Τύπος ημέρας",
            "Βάρδια",
            "Περιοχή εργασίας"
        ]
    else:
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Site": "sito",
            "Personnel ID": "id_personale",
            "Date": "data",
            "Clock In": "ora_ingresso",
            "Clock Out": "ora_uscita",
            "Regular Hours": "ore_ordinarie",
            "Overtime Hours": "ore_straordinario",
            "Day Type": "tipo_giornata",
            "Shift": "turno",
            "Work Area": "area_lavoro",
            "Notes": "note",
            "Day Cost": "costo_giornata"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Site",
            "Personnel ID",
            "Date",
            "Day Type",
            "Shift",
            "Work Area"
        ]

    TABLE_FIELDS = [
        'sito',
        'id_personale',
        'data',
        'ora_ingresso',
        'ora_uscita',
        'ore_ordinarie',
        'ore_straordinario',
        'tipo_giornata',
        'turno',
        'area_lavoro',
        'note',
        'costo_giornata'
    ]

    LANG_TO_THESAURUS = {
        'it': 'IT', 'en': 'en_US', 'de': 'de_DE', 'es': 'es_ES',
        'fr': 'fr_FR', 'ar': 'ar_AR', 'ca': 'ca_ES', 'ro': 'ro_RO',
        'pt': 'pt_PT', 'el': 'el_GR'
    }

    DB_SERVER = "not defined"
    HOME = os.environ['PYARCHINIT_HOME']

    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.setupUi(self)

        # Apply theme
        ThemeManager.apply_theme(self)
        self.theme_toggle_btn = ThemeManager.add_theme_toggle_to_form(self)

        self.currentLayerId = None
        self.retranslate_ui()

        # Reload personnel list when site changes
        self.comboBox_sito.currentTextChanged.connect(self.charge_personale_list)

        # Defer DB loading so the window shows instantly
        QTimer.singleShot(0, self._deferred_init)

        # Connect export buttons
        self.pushButton_export_pdf.clicked.connect(self.on_pushButton_export_pdf_pressed)
        self.pushButton_export_excel.clicked.connect(self.on_pushButton_export_excel_pressed)

        # Connect quick register buttons
        self.pushButton_registra_oggi.clicked.connect(lambda: self.quick_register('regular'))
        self.pushButton_registra_ferie.clicked.connect(lambda: self.quick_register('holiday'))
        self.pushButton_registra_malattia.clicked.connect(lambda: self.quick_register('sick'))
        self.pushButton_registra_permesso.clicked.connect(lambda: self.quick_register('dayoff'))

    def _deferred_init(self):
        """Load data after the window is visible."""
        try:
            self.on_pushButton_connect_pressed()
        except:
            pass
        self.fill_fields()
        self.set_sito()
        self.msg_sito()

    def quick_register(self, reg_type):
        """Quick-fill attendance form for today with selected type."""
        from datetime import datetime as dt

        # Set today's date
        self.lineEdit_data.setDate(QDate.currentDate())

        # Map type to thesaurus values based on language
        type_map = {
            'regular': {'it': 'Ordinaria', 'en': 'Regular Day', 'de': 'Regulärer Tag',
                        'es': 'Jornada Ordinaria', 'fr': 'Journée Ordinaire', 'ar': 'يوم عادي',
                        'ca': 'Jornada Ordinària', 'ro': 'Zi Normală', 'pt': 'Dia Regular', 'el': 'Κανονική Ημέρα'},
            'holiday': {'it': 'Ferie', 'en': 'Holiday/Leave', 'de': 'Urlaub',
                        'es': 'Vacaciones', 'fr': 'Congé', 'ar': 'إجازة',
                        'ca': 'Vacances', 'ro': 'Concediu', 'pt': 'Férias', 'el': 'Άδεια'},
            'sick': {'it': 'Malattia', 'en': 'Sick Leave', 'de': 'Krankheit',
                     'es': 'Baja Médica', 'fr': 'Maladie', 'ar': 'إجازة مرضية',
                     'ca': 'Malaltia', 'ro': 'Concediu Medical', 'pt': 'Baixa Médica', 'el': 'Αναρρωτική'},
            'dayoff': {'it': 'Permesso', 'en': 'Day Off', 'de': 'Freistellung',
                       'es': 'Permiso', 'fr': 'Permission', 'ar': 'إذن',
                       'ca': 'Permís', 'ro': 'Permisie', 'pt': 'Licença', 'el': 'Ρεπό'},
        }

        tipo_vals = type_map.get(reg_type, type_map['regular'])
        tipo = tipo_vals.get(self.L, tipo_vals['en'])

        # Set tipo_giornata
        idx = self.comboBox_tipo_giornata.findText(tipo)
        if idx >= 0:
            self.comboBox_tipo_giornata.setCurrentIndex(idx)
        else:
            self.comboBox_tipo_giornata.setEditText(tipo)

        # For regular day, pre-fill standard work hours
        if reg_type == 'regular':
            now = dt.now()
            self.lineEdit_ora_ingresso.setText(now.strftime("%H:%M"))
            self.lineEdit_ore_ordinarie.setText("8")
            self.lineEdit_ore_straordinario.setText("0")
            self.comboBox_turno.setEditText("Morning")
        elif reg_type in ('holiday', 'sick', 'dayoff'):
            self.lineEdit_ora_ingresso.setText("")
            self.lineEdit_ora_uscita.setText("")
            self.lineEdit_ore_ordinarie.setText("0")
            self.lineEdit_ore_straordinario.setText("0")
            self.lineEdit_costo_giornata.setText("0")

        # Switch to new record mode if browsing
        if self.BROWSE_STATUS != 'n':
            self.on_pushButton_new_rec_pressed()
            # Re-apply the quick fill after new record
            self.lineEdit_data.setDate(QDate.currentDate())
            idx = self.comboBox_tipo_giornata.findText(tipo)
            if idx >= 0:
                self.comboBox_tipo_giornata.setCurrentIndex(idx)
            else:
                self.comboBox_tipo_giornata.setEditText(tipo)
            if reg_type == 'regular':
                self.lineEdit_ora_ingresso.setText(dt.now().strftime("%H:%M"))
                self.lineEdit_ore_ordinarie.setText("8")
                self.lineEdit_ore_straordinario.setText("0")

    def retranslate_ui(self):
        """Translate UI labels based on current locale."""
        lang = self.L
        translations = {
            'it': {
                'title': 'pyArchInit Gestione Cantiere - Presenze',
                'sito': 'Sito', 'personale': 'Personale', 'data': 'Data',
                'turno': 'Turno', 'area_lavoro': 'Area Lavoro',
                'ora_ingresso': 'Ora Ingresso', 'ora_uscita': 'Ora Uscita',
                'ore_ordinarie': 'Ore Ordinarie', 'ore_straordinario': 'Ore Straordinario',
                'tipo_giornata': 'Tipo Giornata', 'costo_giornata': 'Costo Giornata',
                'note': 'Note', 'ordinamento': 'Ordinamento',
                'btn_oggi': 'Registra Oggi', 'btn_ferie': 'Ferie',
                'btn_malattia': 'Malattia', 'btn_permesso': 'Permesso',
                'btn_export_pdf': 'Esporta PDF', 'btn_export_excel': 'Esporta Excel',
            },
            'en': {
                'title': 'pyArchInit Site Management - Attendance',
                'sito': 'Site', 'personale': 'Personnel', 'data': 'Date',
                'turno': 'Shift', 'area_lavoro': 'Work Area',
                'ora_ingresso': 'Clock In', 'ora_uscita': 'Clock Out',
                'ore_ordinarie': 'Regular Hours', 'ore_straordinario': 'Overtime Hours',
                'tipo_giornata': 'Day Type', 'costo_giornata': 'Daily Cost',
                'note': 'Notes', 'ordinamento': 'Sort Order',
                'btn_oggi': 'Register Today', 'btn_ferie': 'Holiday',
                'btn_malattia': 'Sick Leave', 'btn_permesso': 'Day Off',
                'btn_export_pdf': 'Export PDF', 'btn_export_excel': 'Export Excel',
            },
            'de': {
                'title': 'pyArchInit Grabungsverwaltung - Anwesenheit',
                'sito': 'Fundstelle', 'personale': 'Personal', 'data': 'Datum',
                'turno': 'Schicht', 'area_lavoro': 'Arbeitsbereich',
                'ora_ingresso': 'Arbeitsbeginn', 'ora_uscita': 'Arbeitsende',
                'ore_ordinarie': 'Regelarbeitszeit', 'ore_straordinario': 'Überstunden',
                'tipo_giornata': 'Tagestyp', 'costo_giornata': 'Tageskosten',
                'note': 'Notizen', 'ordinamento': 'Sortierung',
                'btn_oggi': 'Heute Erfassen', 'btn_ferie': 'Urlaub',
                'btn_malattia': 'Krankheit', 'btn_permesso': 'Freistellung',
                'btn_export_pdf': 'PDF Export', 'btn_export_excel': 'Excel Export',
            },
            'es': {
                'title': 'pyArchInit Gestión de Obra - Asistencia',
                'sito': 'Sitio', 'personale': 'Personal', 'data': 'Fecha',
                'turno': 'Turno', 'area_lavoro': 'Área de Trabajo',
                'ora_ingresso': 'Hora Entrada', 'ora_uscita': 'Hora Salida',
                'ore_ordinarie': 'Horas Ordinarias', 'ore_straordinario': 'Horas Extra',
                'tipo_giornata': 'Tipo de Jornada', 'costo_giornata': 'Coste Diario',
                'note': 'Notas', 'ordinamento': 'Orden',
                'btn_oggi': 'Registrar Hoy', 'btn_ferie': 'Vacaciones',
                'btn_malattia': 'Baja Médica', 'btn_permesso': 'Permiso',
                'btn_export_pdf': 'Exportar PDF', 'btn_export_excel': 'Exportar Excel',
            },
            'fr': {
                'title': 'pyArchInit Gestion de Chantier - Présences',
                'sito': 'Site', 'personale': 'Personnel', 'data': 'Date',
                'turno': 'Équipe', 'area_lavoro': 'Zone de Travail',
                'ora_ingresso': 'Heure Arrivée', 'ora_uscita': 'Heure Départ',
                'ore_ordinarie': 'Heures Normales', 'ore_straordinario': 'Heures Supplémentaires',
                'tipo_giornata': 'Type de Journée', 'costo_giornata': 'Coût Journalier',
                'note': 'Notes', 'ordinamento': 'Classement',
                'btn_oggi': "Enregistrer Aujourd'hui", 'btn_ferie': 'Congé',
                'btn_malattia': 'Maladie', 'btn_permesso': 'Permission',
                'btn_export_pdf': 'Exporter PDF', 'btn_export_excel': 'Exporter Excel',
            },
            'ar': {
                'title': 'pyArchInit إدارة الموقع - الحضور',
                'sito': 'الموقع', 'personale': 'الموظف', 'data': 'التاريخ',
                'turno': 'الوردية', 'area_lavoro': 'منطقة العمل',
                'ora_ingresso': 'وقت الدخول', 'ora_uscita': 'وقت الخروج',
                'ore_ordinarie': 'ساعات عادية', 'ore_straordinario': 'ساعات إضافية',
                'tipo_giornata': 'نوع اليوم', 'costo_giornata': 'التكلفة اليومية',
                'note': 'ملاحظات', 'ordinamento': 'الترتيب',
                'btn_oggi': 'تسجيل اليوم', 'btn_ferie': 'إجازة',
                'btn_malattia': 'إجازة مرضية', 'btn_permesso': 'إذن',
                'btn_export_pdf': 'تصدير PDF', 'btn_export_excel': 'تصدير Excel',
            },
            'ca': {
                'title': "pyArchInit Gestió d'Obra - Assistència",
                'sito': 'Lloc', 'personale': 'Personal', 'data': 'Data',
                'turno': 'Torn', 'area_lavoro': 'Àrea de Treball',
                'ora_ingresso': 'Hora Entrada', 'ora_uscita': 'Hora Sortida',
                'ore_ordinarie': 'Hores Ordinàries', 'ore_straordinario': 'Hores Extres',
                'tipo_giornata': 'Tipus de Jornada', 'costo_giornata': 'Cost Diari',
                'note': 'Notes', 'ordinamento': 'Ordenació',
                'btn_oggi': "Registrar Avui", 'btn_ferie': 'Vacances',
                'btn_malattia': 'Malaltia', 'btn_permesso': 'Permís',
                'btn_export_pdf': 'Exportar PDF', 'btn_export_excel': 'Exportar Excel',
            },
            'ro': {
                'title': 'pyArchInit Gestiune Șantier - Prezențe',
                'sito': 'Sit', 'personale': 'Personal', 'data': 'Data',
                'turno': 'Tură', 'area_lavoro': 'Zona de Lucru',
                'ora_ingresso': 'Ora Intrare', 'ora_uscita': 'Ora Ieșire',
                'ore_ordinarie': 'Ore Normale', 'ore_straordinario': 'Ore Suplimentare',
                'tipo_giornata': 'Tip Zi', 'costo_giornata': 'Cost Zilnic',
                'note': 'Note', 'ordinamento': 'Ordonare',
                'btn_oggi': 'Înregistrează Azi', 'btn_ferie': 'Concediu',
                'btn_malattia': 'Concediu Medical', 'btn_permesso': 'Permisie',
                'btn_export_pdf': 'Export PDF', 'btn_export_excel': 'Export Excel',
            },
            'pt': {
                'title': 'pyArchInit Gestão de Obra - Presenças',
                'sito': 'Sítio', 'personale': 'Pessoal', 'data': 'Data',
                'turno': 'Turno', 'area_lavoro': 'Área de Trabalho',
                'ora_ingresso': 'Hora de Entrada', 'ora_uscita': 'Hora de Saída',
                'ore_ordinarie': 'Horas Normais', 'ore_straordinario': 'Horas Extra',
                'tipo_giornata': 'Tipo de Dia', 'costo_giornata': 'Custo Diário',
                'note': 'Notas', 'ordinamento': 'Ordenação',
                'btn_oggi': 'Registar Hoje', 'btn_ferie': 'Férias',
                'btn_malattia': 'Baixa Médica', 'btn_permesso': 'Licença',
                'btn_export_pdf': 'Exportar PDF', 'btn_export_excel': 'Exportar Excel',
            },
            'el': {
                'title': 'pyArchInit Διαχείριση Ανασκαφής - Παρουσίες',
                'sito': 'Τοποθεσία', 'personale': 'Προσωπικό', 'data': 'Ημερομηνία',
                'turno': 'Βάρδια', 'area_lavoro': 'Περιοχή Εργασίας',
                'ora_ingresso': 'Ώρα Προσέλευσης', 'ora_uscita': 'Ώρα Αποχώρησης',
                'ore_ordinarie': 'Κανονικές Ώρες', 'ore_straordinario': 'Υπερωρίες',
                'tipo_giornata': 'Τύπος Ημέρας', 'costo_giornata': 'Ημερήσιο Κόστος',
                'note': 'Σημειώσεις', 'ordinamento': 'Ταξινόμηση',
                'btn_oggi': 'Καταχώρηση Σήμερα', 'btn_ferie': 'Άδεια',
                'btn_malattia': 'Αναρρωτική', 'btn_permesso': 'Ρεπό',
                'btn_export_pdf': 'Εξαγωγή PDF', 'btn_export_excel': 'Εξαγωγή Excel',
            },
        }
        t = translations.get(lang, translations.get('en', translations['it']))
        self.setWindowTitle(t['title'])
        self.label_sito.setText(t['sito'])
        self.label_personale.setText(t['personale'])
        self.label_data.setText(t['data'])
        self.label_turno.setText(t['turno'])
        self.label_area_lavoro.setText(t['area_lavoro'])
        self.label_ora_ingresso.setText(t['ora_ingresso'])
        self.label_ora_uscita.setText(t['ora_uscita'])
        self.label_ore_ordinarie.setText(t['ore_ordinarie'])
        self.label_ore_straordinario.setText(t['ore_straordinario'])
        self.label_tipo_giornata.setText(t['tipo_giornata'])
        self.label_costo_giornata.setText(t['costo_giornata'])
        self.label_note.setText(t['note'])
        self.label_lbl_sort.setText(t['ordinamento'])
        self.pushButton_registra_oggi.setText(t['btn_oggi'])
        self.pushButton_registra_ferie.setText(t['btn_ferie'])
        self.pushButton_registra_malattia.setText(t['btn_malattia'])
        self.pushButton_registra_permesso.setText(t['btn_permesso'])
        self.pushButton_export_pdf.setText(t['btn_export_pdf'])
        self.pushButton_export_excel.setText(t['btn_export_excel'])

    def enable_button(self, n):
        self.pushButton_connect.setEnabled(n)
        self.pushButton_new_rec.setEnabled(n)
        self.pushButton_show_all.setEnabled(n)
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
        self.pushButton_show_all.setEnabled(n)
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
            self.charge_records()
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
                if self.L == 'it':
                    QMessageBox.warning(self, "BENVENUTO",
                                        "Benvenuto in pyArchInit " + self.NOME_SCHEDA + ". Il database e' vuoto. Premi 'Ok' e buon lavoro!",
                                        QMessageBox.StandardButton.Ok)
                elif self.L == 'de':
                    QMessageBox.warning(self, "WILLKOMMEN",
                                        "WILLKOMMEN in pyArchInit " + self.NOME_SCHEDA + ". Die Datenbank ist leer. Tippe 'Ok' und aufgehts!",
                                        QMessageBox.StandardButton.Ok)
                else:
                    QMessageBox.warning(self, "WELCOME",
                                        "Welcome in pyArchInit " + self.NOME_SCHEDA + ". The DB is empty. Push 'Ok' and Good Work!",
                                        QMessageBox.StandardButton.Ok)
                self.charge_list()
                self.BROWSE_STATUS = 'x'
                self.on_pushButton_new_rec_pressed()
        except Exception as e:
            e = str(e)
            if e.find("no such table"):
                if self.L == 'it':
                    msg = "La connessione e' fallita {}. " \
                          "E' NECESSARIO RIAVVIARE QGIS oppure rilevato bug! Segnalarlo allo sviluppatore".format(str(e))
                elif self.L == 'de':
                    msg = "Verbindungsfehler {}. " \
                          " QGIS neustarten oder es wurde ein bug gefunden! Fehler einsenden".format(str(e))
                else:
                    msg = "The connection failed {}. " \
                          "You MUST RESTART QGIS or bug detected! Report it to the developer".format(str(e))
            else:
                if self.L == 'it':
                    msg = "Attenzione rilevato bug! Segnalarlo allo sviluppatore. Errore: ".format(str(e))
                elif self.L == 'de':
                    msg = "ACHTUNG. Es wurde ein bug gefunden! Fehler einsenden: ".format(str(e))
                else:
                    msg = "Warning bug detected! Report it to the developer. Error: ".format(str(e))

    def charge_list(self):
        sito_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('site_table', 'sito', 'SITE'))
        try:
            sito_vl.remove('')
        except:
            pass
        self.comboBox_sito.clear()
        sito_vl.sort()
        self.comboBox_sito.addItems(sito_vl)

        # Thesaurus-based combobox population
        th_lang = self.LANG_TO_THESAURUS.get(self.L, 'en_US')
        try:
            thesaurus = self.DB_MANAGER.query_thesaurus_batch(
                'cantiere_presenze_table', th_lang)

            giornata_values = [v.sigla_estesa for v in thesaurus.get('14.3', [])]
            self.comboBox_tipo_giornata.clear()
            self.comboBox_tipo_giornata.addItems(giornata_values)
        except Exception as e:
            pass

        # Populate personnel combobox from personale_table
        self.charge_personale_list()

    def charge_personale_list(self):
        """Populate comboBox_personale from personale_table."""
        try:
            sito = self.comboBox_sito.currentText()
            if sito:
                search_dict = {'sito': "'" + str(sito) + "'"}
                u = Utility()
                search_dict = u.remove_empty_items_fr_dict(search_dict)
                res = self.DB_MANAGER.query_bool(search_dict, "PERSONALE")
            else:
                res = self.DB_MANAGER.query_ordered("PERSONALE", "id_personale", 'asc')

            self.comboBox_personale.clear()
            for r in res:
                display_text = "%d - %s %s" % (r.id_personale, r.nome, r.cognome)
                self.comboBox_personale.addItem(display_text, r.id_personale)
        except Exception as e:
            pass

    def msg_sito(self):
        conn = Connection()
        sito_set = conn.sito_set()
        sito_set_str = sito_set['sito_set']
        if bool(self.comboBox_sito.currentText()) and self.comboBox_sito.currentText() == sito_set_str:
            if self.L == 'it':
                QMessageBox.information(self, "OK", "Sei connesso al sito: %s" % str(sito_set_str),
                                        QMessageBox.StandardButton.Ok)
            elif self.L == 'de':
                QMessageBox.information(self, "OK",
                                        "Sie sind mit der archäologischen Stätte verbunden: %s" % str(sito_set_str),
                                        QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.information(self, "OK", "You are connected to the site: %s" % str(sito_set_str),
                                        QMessageBox.StandardButton.Ok)
        elif sito_set_str == '':
            if self.L == 'it':
                msg = QMessageBox.information(self, "Attenzione",
                                              "Non hai settato alcun sito. Vuoi settarne uno?",
                                              QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            elif self.L == 'de':
                msg = QMessageBox.information(self, "Achtung",
                                              "Sie haben keine archäologischen Stätten eingerichtet.",
                                              QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            else:
                msg = QMessageBox.information(self, "Warning",
                                              "You have not set up any archaeological site.",
                                              QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
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

                if len(self.DATA_LIST) == 0:
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
                QMessageBox.warning(self, "Errore", "Errore: %s" % str(e), QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.warning(self, "Error", "Error: %s" % str(e), QMessageBox.StandardButton.Ok)

    def calculate_hours(self):
        """Auto-calculate ore_ordinarie from ora_ingresso and ora_uscita."""
        try:
            ingresso = self.lineEdit_ora_ingresso.text().strip()
            uscita = self.lineEdit_ora_uscita.text().strip()
            if ingresso and uscita:
                fmt = "%H:%M"
                t_in = datetime.strptime(ingresso, fmt)
                t_out = datetime.strptime(uscita, fmt)
                delta = t_out - t_in
                hours = delta.total_seconds() / 3600.0
                if hours < 0:
                    hours += 24  # handle overnight shifts
                # Standard 8-hour day
                ore_ordinarie = min(hours, 8.0)
                ore_straordinario = max(hours - 8.0, 0.0)
                self.lineEdit_ore_ordinarie.setText("%.2f" % ore_ordinarie)
                self.lineEdit_ore_straordinario.setText("%.2f" % ore_straordinario)
        except (ValueError, TypeError):
            pass

    def calculate_cost(self):
        """Auto-calculate costo_giornata from hours * tariffa (query personale_table)."""
        try:
            id_pers_text = self.comboBox_personale.currentData()
            if id_pers_text is None:
                return
            id_pers = int(id_pers_text)
            search_dict = {'id_personale': "'" + str(id_pers) + "'"}
            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)
            res = self.DB_MANAGER.query_bool(search_dict, "PERSONALE")
            if res:
                persona = res[0]
                tariffa_oraria = float(persona.tariffa_oraria) if persona.tariffa_oraria else 0.0
                ore_ord = float(self.lineEdit_ore_ordinarie.text()) if self.lineEdit_ore_ordinarie.text() else 0.0
                ore_str = float(self.lineEdit_ore_straordinario.text()) if self.lineEdit_ore_straordinario.text() else 0.0
                costo = (ore_ord + ore_str * 1.25) * tariffa_oraria
                self.lineEdit_costo_giornata.setText("%.2f" % costo)
        except (ValueError, TypeError):
            pass

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
            self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
            self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
            self.SORT_STATUS = "o"
            self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
            self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
            self.fill_fields()

    def on_pushButton_new_rec_pressed(self):
        conn = Connection()
        sito_set = conn.sito_set()
        sito_set_str = sito_set['sito_set']

        if bool(self.DATA_LIST):
            if self.data_error_check() == 1:
                pass
            else:
                if self.BROWSE_STATUS == "b":
                    if bool(self.DATA_LIST):
                        if self.records_equal_check() == 1:
                            if self.L == 'it':
                                self.update_if(QMessageBox.warning(self, 'Errore',
                                    "Il record e' stato modificato. Vuoi salvare le modifiche?",
                                    QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))
                            elif self.L == 'de':
                                self.update_if(QMessageBox.warning(self, 'Error',
                                    "Der Record wurde geändert. Möchtest du die Änderungen speichern?",
                                    QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))
                            else:
                                self.update_if(QMessageBox.warning(self, 'Error',
                                    "The record has been changed. Do you want to save the changes?",
                                    QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))

        if self.BROWSE_STATUS != "n":
            if bool(self.comboBox_sito.currentText()) and self.comboBox_sito.currentText() == sito_set_str:
                self.BROWSE_STATUS = "n"
                self.setComboBoxEnable(["self.comboBox_sito"], "False")
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.set_rec_counter('', '')
                self.label_sort.setText(self.SORTED_ITEMS["n"])
                self.empty_fields_nosite()
            else:
                self.BROWSE_STATUS = "n"
                self.setComboBoxEnable(["self.comboBox_sito"], "True")
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.set_rec_counter('', '')
                self.label_sort.setText(self.SORTED_ITEMS["n"])
                self.empty_fields()

            self.enable_button(0)

    def on_pushButton_save_pressed(self):
        if self.BROWSE_STATUS == "b":
            if self.data_error_check() == 0:
                if self.records_equal_check() == 1:
                    if self.L == 'it':
                        self.update_if(QMessageBox.warning(self, 'Errore',
                            "Il record e' stato modificato. Vuoi salvare le modifiche?",
                            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))
                    elif self.L == 'de':
                        self.update_if(QMessageBox.warning(self, 'Error',
                            "Der Record wurde geändert. Möchtest du die Änderungen speichern?",
                            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))
                    else:
                        self.update_if(QMessageBox.warning(self, 'Error',
                            "The record has been changed. Do you want to save the changes?",
                            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))
                    self.SORT_STATUS = "n"
                    self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
                    self.enable_button(1)
                    self.fill_fields(self.REC_CORR)
                else:
                    if self.L == 'it':
                        QMessageBox.warning(self, "ATTENZIONE", "Non è stata realizzata alcuna modifica.",
                                            QMessageBox.StandardButton.Ok)
                    elif self.L == 'de':
                        QMessageBox.warning(self, "ACHTUNG", "Keine Änderung vorgenommen",
                                            QMessageBox.StandardButton.Ok)
                    else:
                        QMessageBox.warning(self, "Warning", "No changes have been made",
                                            QMessageBox.StandardButton.Ok)
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
                    self.setComboBoxEnable(["self.comboBox_sito"], "False")
                    self.fill_fields(self.REC_CORR)
                    self.enable_button(1)

    def data_error_check(self):
        test = 0
        EC = Error_check()

        if self.L == 'it':
            if self.comboBox_sito.currentText() == "":
                QMessageBox.warning(self, "ATTENZIONE", "Campo Sito obbligatorio!", QMessageBox.StandardButton.Ok)
                test = 1
            if self.lineEdit_data.date() == QDate(2000, 1, 1):
                QMessageBox.warning(self, "ATTENZIONE", "Campo Data obbligatorio!", QMessageBox.StandardButton.Ok)
                test = 1
        elif self.L == 'de':
            if self.comboBox_sito.currentText() == "":
                QMessageBox.warning(self, "ACHTUNG", "Feld Fundort erforderlich!", QMessageBox.StandardButton.Ok)
                test = 1
            if self.lineEdit_data.date() == QDate(2000, 1, 1):
                QMessageBox.warning(self, "ACHTUNG", "Feld Datum erforderlich!", QMessageBox.StandardButton.Ok)
                test = 1
        else:
            if self.comboBox_sito.currentText() == "":
                QMessageBox.warning(self, "WARNING", "Site field required!", QMessageBox.StandardButton.Ok)
                test = 1
            if self.lineEdit_data.date() == QDate(2000, 1, 1):
                QMessageBox.warning(self, "WARNING", "Date field required!", QMessageBox.StandardButton.Ok)
                test = 1

        return test

    def insert_new_rec(self):
        try:
            # Get personale ID from combobox data
            id_personale = self.comboBox_personale.currentData()
            if id_personale is None:
                id_personale = 0
            else:
                id_personale = int(id_personale)

            ore_ordinarie = None
            if self.lineEdit_ore_ordinarie.text():
                try:
                    ore_ordinarie = float(self.lineEdit_ore_ordinarie.text())
                except ValueError:
                    ore_ordinarie = None

            ore_straordinario = None
            if self.lineEdit_ore_straordinario.text():
                try:
                    ore_straordinario = float(self.lineEdit_ore_straordinario.text())
                except ValueError:
                    ore_straordinario = None

            costo_giornata = None
            if self.lineEdit_costo_giornata.text():
                try:
                    costo_giornata = float(self.lineEdit_costo_giornata.text())
                except ValueError:
                    costo_giornata = None

            data = self.DB_MANAGER.insert_presenze_values(
                self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, self.ID_TABLE) + 1,
                str(self.comboBox_sito.currentText()),                  # sito
                id_personale,                                           # id_personale
                str(self.lineEdit_data.date().toString("yyyy-MM-dd")),                         # data
                str(self.lineEdit_ora_ingresso.text()),                 # ora_ingresso
                str(self.lineEdit_ora_uscita.text()),                   # ora_uscita
                ore_ordinarie,                                          # ore_ordinarie
                ore_straordinario,                                      # ore_straordinario
                str(self.comboBox_tipo_giornata.currentText()),         # tipo_giornata
                str(self.comboBox_turno.currentText()),                        # turno
                str(self.lineEdit_area_lavoro.text()),                  # area_lavoro
                str(self.textEdit_note.toPlainText()),                  # note
                costo_giornata)                                         # costo_giornata

            try:
                self.DB_MANAGER.insert_data_session(data)
                return 1
            except Exception as e:
                e_str = str(e)
                if e_str.__contains__("IntegrityError"):
                    if self.L == 'it':
                        msg = self.ID_TABLE + " gia' presente nel database"
                    elif self.L == 'de':
                        msg = self.ID_TABLE + " bereits in der Datenbank"
                    else:
                        msg = self.ID_TABLE + " exist in db"
                    QMessageBox.warning(self, "Error", "Error" + str(msg), QMessageBox.StandardButton.Ok)
                else:
                    QMessageBox.warning(self, "Error", "Error 1 \n" + str(e), QMessageBox.StandardButton.Ok)
                return 0
        except Exception as e:
            QMessageBox.warning(self, "Error", "Error 2 \n" + str(e), QMessageBox.StandardButton.Ok)
            return 0

    def check_record_state(self):
        ec = self.data_error_check()
        if ec == 1:
            return 1
        elif self.records_equal_check() == 1 and ec == 0:
            if self.L == 'it':
                self.update_if(QMessageBox.warning(self, 'Errore',
                    "Il record e' stato modificato. Vuoi salvare le modifiche?",
                    QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))
            elif self.L == 'de':
                self.update_if(QMessageBox.warning(self, 'Errore',
                    "Der Record wurde geändert. Möchtest du die Änderungen speichern?",
                    QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))
            else:
                self.update_if(QMessageBox.warning(self, "Error",
                    "The record has been changed. You want to save the changes?",
                    QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))
            return 0

    def on_pushButton_view_all_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            self.empty_fields()
            self.charge_records()
            self.fill_fields()
            self.BROWSE_STATUS = "b"
            self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
            self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
            self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
            self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
            self.label_sort.setText(self.SORTED_ITEMS["n"])

    on_pushButton_show_all_pressed = on_pushButton_view_all_pressed

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
                if self.L == 'it':
                    QMessageBox.warning(self, "Attenzione", "Sei al primo record!", QMessageBox.StandardButton.Ok)
                elif self.L == 'de':
                    QMessageBox.warning(self, "Achtung", "du befindest dich im ersten Datensatz!", QMessageBox.StandardButton.Ok)
                else:
                    QMessageBox.warning(self, "Warning", "You are at the first record!", QMessageBox.StandardButton.Ok)
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
                if self.L == 'it':
                    QMessageBox.warning(self, "Attenzione", "Sei all'ultimo record!", QMessageBox.StandardButton.Ok)
                elif self.L == 'de':
                    QMessageBox.warning(self, "Achtung", "du befindest dich im letzten Datensatz!", QMessageBox.StandardButton.Ok)
                else:
                    QMessageBox.warning(self, "Warning", "You are at the last record!", QMessageBox.StandardButton.Ok)
            else:
                try:
                    self.empty_fields()
                    self.fill_fields(self.REC_CORR)
                    self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
                except Exception as e:
                    QMessageBox.warning(self, "Error", str(e), QMessageBox.StandardButton.Ok)

    def on_pushButton_delete_pressed(self):
        if self.L == 'it':
            msg = QMessageBox.warning(self, "Attenzione!!!",
                "Vuoi veramente eliminare il record? \n L'azione è irreversibile",
                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            if msg == QMessageBox.StandardButton.Cancel:
                QMessageBox.warning(self, "Messaggio!!!", "Azione Annullata!")
            else:
                try:
                    id_to_delete = getattr(self.DATA_LIST[self.REC_CORR], self.ID_TABLE)
                    self.DB_MANAGER.delete_one_record(self.TABLE_NAME, self.ID_TABLE, id_to_delete)
                    self.charge_records()
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
                if bool(self.DATA_LIST):
                    self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                    self.charge_list()
                    self.fill_fields()
                    self.set_sito()
        elif self.L == 'de':
            msg = QMessageBox.warning(self, "Achtung!!!",
                "Willst du wirklich diesen Eintrag löschen? \n Der Vorgang ist unumkehrbar",
                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            if msg == QMessageBox.StandardButton.Cancel:
                QMessageBox.warning(self, "Message!!!", "Aktion annulliert!")
            else:
                try:
                    id_to_delete = getattr(self.DATA_LIST[self.REC_CORR], self.ID_TABLE)
                    self.DB_MANAGER.delete_one_record(self.TABLE_NAME, self.ID_TABLE, id_to_delete)
                    self.charge_records()
                    QMessageBox.warning(self, "Message!!!", "Record gelöscht!")
                except Exception as e:
                    QMessageBox.warning(self, "Message!!!", "Errortyp: " + str(e))
                if not bool(self.DATA_LIST):
                    QMessageBox.warning(self, "Warning", "Die Datenbank ist leer!", QMessageBox.StandardButton.Ok)
                    self.DATA_LIST = []
                    self.DATA_LIST_REC_CORR = []
                    self.DATA_LIST_REC_TEMP = []
                    self.REC_CORR = 0
                    self.REC_TOT = 0
                    self.empty_fields()
                    self.set_rec_counter(0, 0)
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
                "Do you really want to delete the record? \n Action is irreversible.",
                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            if msg == QMessageBox.StandardButton.Cancel:
                QMessageBox.warning(self, "Message!!!", "Action deleted!")
            else:
                try:
                    id_to_delete = getattr(self.DATA_LIST[self.REC_CORR], self.ID_TABLE)
                    self.DB_MANAGER.delete_one_record(self.TABLE_NAME, self.ID_TABLE, id_to_delete)
                    self.charge_records()
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
            sito_set = conn.sito_set()
            sito_set_str = sito_set['sito_set']

            if self.BROWSE_STATUS != "f":
                if bool(self.comboBox_sito.currentText()) and self.comboBox_sito.currentText() == sito_set_str:
                    self.BROWSE_STATUS = "f"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.empty_fields_nosite()
                    self.set_rec_counter('', '')
                    self.label_sort.setText(self.SORTED_ITEMS["n"])
                    self.setComboBoxEnable(["self.comboBox_sito"], "False")
                else:
                    self.BROWSE_STATUS = "f"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.empty_fields()
                    self.set_rec_counter('', '')
                    self.label_sort.setText(self.SORTED_ITEMS["n"])
                    self.setComboBoxEnable(["self.comboBox_sito"], "True")
                    self.charge_list()

    def on_pushButton_search_go_pressed(self):
        if self.BROWSE_STATUS != "f":
            if self.L == 'it':
                QMessageBox.warning(self, "ATTENZIONE", "Per eseguire una nuova ricerca clicca sul pulsante 'new search' ",
                                    QMessageBox.StandardButton.Ok)
            elif self.L == 'de':
                QMessageBox.warning(self, "ACHTUNG", "Um eine neue Abfrage zu starten drücke 'new search' ",
                                    QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.warning(self, "WARNING", "To perform a new search click on the 'new search' button ",
                                    QMessageBox.StandardButton.Ok)
        else:
            search_dict = {
                'sito': "'" + str(self.comboBox_sito.currentText()) + "'",
                'data': "'" + str(self.lineEdit_data.date().toString("yyyy-MM-dd")) + "'",
                'tipo_giornata': "'" + str(self.comboBox_tipo_giornata.currentText()) + "'",
                'turno': "'" + str(self.comboBox_turno.currentText()) + "'",
                'area_lavoro': "'" + str(self.lineEdit_area_lavoro.text()) + "'",
                'note': str(self.textEdit_note.toPlainText()),
            }

            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)
            if not bool(search_dict):
                if self.L == 'it':
                    QMessageBox.warning(self, "ATTENZIONE", "Non è stata impostata nessuna ricerca!!!",
                                        QMessageBox.StandardButton.Ok)
                elif self.L == 'de':
                    QMessageBox.warning(self, "ACHTUNG", "Keine Abfrage definiert!!!", QMessageBox.StandardButton.Ok)
                else:
                    QMessageBox.warning(self, "WARNING", "No search has been set!!!", QMessageBox.StandardButton.Ok)
            else:
                res = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
                if not bool(res):
                    if self.L == 'it':
                        QMessageBox.warning(self, "ATTENZIONE", "Non e' stato trovato alcun record!",
                                            QMessageBox.StandardButton.Ok)
                    elif self.L == 'de':
                        QMessageBox.warning(self, "ACHTUNG", "kein Eintrag gefunden!", QMessageBox.StandardButton.Ok)
                    else:
                        QMessageBox.warning(self, "Warning", "The record has not been found",
                                            QMessageBox.StandardButton.Ok)

                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                    self.fill_fields(self.REC_CORR)
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.setComboBoxEnable(["self.comboBox_sito"], "False")
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
                    self.setComboBoxEnable(["self.comboBox_sito"], "False")

                    if self.REC_TOT == 1:
                        strings = ("E' stato trovato", self.REC_TOT, "record")
                    else:
                        strings = ("Sono stati trovati", self.REC_TOT, "records")
                    QMessageBox.warning(self, "Messaggio", "%s %d %s" % strings, QMessageBox.StandardButton.Ok)

        self.enable_button_search(1)

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
                                                                self.MAPPER_TABLE_CLASS, self.ID_TABLE)
                else:
                    temp_data_list = self.DB_MANAGER.query_sort(id_list, self.SORT_ITEMS_CONVERTED, self.SORT_MODE,
                                                                self.MAPPER_TABLE_CLASS, self.ID_TABLE)
                for i in temp_data_list:
                    self.DATA_LIST.append(i)
                self.BROWSE_STATUS = "b"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                return 1
            elif test == 0:
                return 0

    def charge_records(self):
        self.DATA_LIST = self.DB_MANAGER.query_ordered(self.MAPPER_TABLE_CLASS, self.ID_TABLE, 'asc')

    def setComboBoxEditable(self, f, n):
        for fn in f:
            widget_name = fn.replace('self.', '') if fn.startswith('self.') else fn
            widget = getattr(self, widget_name, None)
            if widget is not None:
                widget.setEditable(bool(n))

    def setComboBoxEnable(self, f, v):
        for fn in f:
            widget_name = fn.replace('self.', '') if fn.startswith('self.') else fn
            widget = getattr(self, widget_name, None)
            if widget is not None:
                widget.setEnabled(v == "True")

    def set_rec_counter(self, t, c):
        self.rec_tot = t
        self.rec_corr = c
        self.label_rec_tot.setText(str(self.rec_tot))
        self.label_rec_corrente.setText(str(self.rec_corr))

    def empty_fields_nosite(self):
        self.comboBox_personale.setCurrentIndex(-1)
        self.lineEdit_data.setDate(QDate(2000, 1, 1))
        self.lineEdit_ora_ingresso.clear()
        self.lineEdit_ora_uscita.clear()
        self.lineEdit_ore_ordinarie.clear()
        self.lineEdit_ore_straordinario.clear()
        self.comboBox_tipo_giornata.setEditText("")
        self.comboBox_turno.setEditText("")
        self.lineEdit_area_lavoro.clear()
        self.textEdit_note.clear()
        self.lineEdit_costo_giornata.clear()

    def empty_fields(self):
        self.comboBox_sito.setEditText("")
        self.comboBox_personale.setCurrentIndex(-1)
        self.lineEdit_data.setDate(QDate(2000, 1, 1))
        self.lineEdit_ora_ingresso.clear()
        self.lineEdit_ora_uscita.clear()
        self.lineEdit_ore_ordinarie.clear()
        self.lineEdit_ore_straordinario.clear()
        self.comboBox_tipo_giornata.setEditText("")
        self.comboBox_turno.setEditText("")
        self.lineEdit_area_lavoro.clear()
        self.textEdit_note.clear()
        self.lineEdit_costo_giornata.clear()

    def fill_fields(self, n=0):
        self.rec_num = n
        try:
            self.comboBox_sito.setEditText(str(self.DATA_LIST[self.rec_num].sito))

            # Set personale combobox by id_personale
            id_pers = self.DATA_LIST[self.rec_num].id_personale
            idx = self.comboBox_personale.findData(id_pers)
            if idx >= 0:
                self.comboBox_personale.setCurrentIndex(idx)
            else:
                self.comboBox_personale.setCurrentIndex(-1)

            date_str = str(self.DATA_LIST[self.rec_num].data) if self.DATA_LIST[self.rec_num].data else ""
            if date_str:
                qd = QDate.fromString(date_str, "yyyy-MM-dd")
                if not qd.isValid():
                    qd = QDate.fromString(date_str, "dd/MM/yyyy")
                if not qd.isValid():
                    qd = QDate.fromString(date_str, "dd-MM-yyyy")
                if qd.isValid():
                    self.lineEdit_data.setDate(qd)
                else:
                    self.lineEdit_data.setDate(QDate.currentDate())
            else:
                self.lineEdit_data.setDate(QDate(2000, 1, 1))
            self.lineEdit_ora_ingresso.setText(str(self.DATA_LIST[self.rec_num].ora_ingresso) if self.DATA_LIST[self.rec_num].ora_ingresso else "")
            self.lineEdit_ora_uscita.setText(str(self.DATA_LIST[self.rec_num].ora_uscita) if self.DATA_LIST[self.rec_num].ora_uscita else "")

            if self.DATA_LIST[self.rec_num].ore_ordinarie is not None:
                self.lineEdit_ore_ordinarie.setText(str(self.DATA_LIST[self.rec_num].ore_ordinarie))
            else:
                self.lineEdit_ore_ordinarie.setText("")

            if self.DATA_LIST[self.rec_num].ore_straordinario is not None:
                self.lineEdit_ore_straordinario.setText(str(self.DATA_LIST[self.rec_num].ore_straordinario))
            else:
                self.lineEdit_ore_straordinario.setText("")

            self.comboBox_tipo_giornata.setEditText(str(self.DATA_LIST[self.rec_num].tipo_giornata) if self.DATA_LIST[self.rec_num].tipo_giornata else "")
            self.comboBox_turno.setEditText(str(self.DATA_LIST[self.rec_num].turno) if self.DATA_LIST[self.rec_num].turno else "")
            self.lineEdit_area_lavoro.setText(str(self.DATA_LIST[self.rec_num].area_lavoro) if self.DATA_LIST[self.rec_num].area_lavoro else "")
            self.textEdit_note.setText(str(self.DATA_LIST[self.rec_num].note) if self.DATA_LIST[self.rec_num].note else "")

            if self.DATA_LIST[self.rec_num].costo_giornata is not None:
                self.lineEdit_costo_giornata.setText(str(self.DATA_LIST[self.rec_num].costo_giornata))
            else:
                self.lineEdit_costo_giornata.setText("")
        except:
            pass

    def set_LIST_REC_TEMP(self):
        ore_ord = str(self.lineEdit_ore_ordinarie.text()) if self.lineEdit_ore_ordinarie.text() else ''
        ore_str = str(self.lineEdit_ore_straordinario.text()) if self.lineEdit_ore_straordinario.text() else ''
        costo = str(self.lineEdit_costo_giornata.text()) if self.lineEdit_costo_giornata.text() else ''
        id_pers = self.comboBox_personale.currentData()
        id_pers_str = str(id_pers) if id_pers is not None else ''

        self.DATA_LIST_REC_TEMP = [
            str(self.comboBox_sito.currentText()),
            id_pers_str,
            str(self.lineEdit_data.date().toString("yyyy-MM-dd")),
            str(self.lineEdit_ora_ingresso.text()),
            str(self.lineEdit_ora_uscita.text()),
            ore_ord,
            ore_str,
            str(self.comboBox_tipo_giornata.currentText()),
            str(self.comboBox_turno.currentText()),
            str(self.lineEdit_area_lavoro.text()),
            str(self.textEdit_note.toPlainText()),
            costo
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

    def update_record(self):
        try:
            self.DB_MANAGER.update(self.MAPPER_TABLE_CLASS,
                                   self.ID_TABLE,
                                   [int(getattr(self.DATA_LIST[self.REC_CORR], self.ID_TABLE))],
                                   self.TABLE_FIELDS,
                                   self.rec_toupdate())
            return 1
        except Exception as e:
            save_file = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_Report_folder")
            file_ = os.path.join(save_file, 'error_encodig_data_recover.txt')
            with open(file_, "a") as fh:
                try:
                    raise ValueError(str(e))
                except ValueError as s:
                    print(s, file=fh)
            if self.L == 'it':
                QMessageBox.warning(self, "Messaggio",
                    "Problema di encoding: sono stati inseriti accenti o caratteri non accettati dal database.",
                    QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.warning(self, "Message",
                    "Encoding problem: accents or characters not accepted by the database were entered.",
                    QMessageBox.StandardButton.Ok)
            return 0

    def rec_toupdate(self):
        rec_to_update = self.UTILITY.pos_none_in_list(self.DATA_LIST_REC_TEMP)
        return rec_to_update

    def datestrfdate(self):
        now = date.today()
        today = now.strftime("%d-%m-%Y")
        return today


    def on_pushButton_export_pdf_pressed(self):
        """Export attendance records to a professional full-page landscape PDF."""
        if not bool(self.DATA_LIST):
            QMessageBox.warning(self, "Warning", "No records to export.", QMessageBox.StandardButton.Ok)
            return

        home = os.environ['PYARCHINIT_HOME']
        default_name = "attendance_report.pdf"
        file_path, _ = QFileDialog.getSaveFileName(self, "Export PDF", os.path.join(home, default_name), "PDF (*.pdf)")
        if not file_path:
            return

        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.lib.units import cm, mm
            from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
                                            Paragraph, Spacer, PageBreak, KeepTogether)
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
            from reportlab.platypus.flowables import HRFlowable
            from datetime import datetime

            lang = self.L
            sito = self.comboBox_sito.currentText()

            # --- Color scheme ---
            CLR_HEADER = colors.HexColor('#1a237e')       # dark blue
            CLR_ACCENT = colors.HexColor('#e3f2fd')        # light blue
            CLR_ROW_ALT = colors.HexColor('#f5f7fa')       # subtle grey
            CLR_TEXT_LIGHT = colors.white
            CLR_BORDER = colors.HexColor('#bbdefb')        # medium blue
            CLR_SUMMARY_BG = colors.HexColor('#e8eaf6')    # indigo tint
            CLR_TOTAL_ROW = colors.HexColor('#c5cae9')     # stronger indigo

            # --- i18n strings ---
            i18n = {
                'it': {
                    'title': 'Report Presenze',
                    'subtitle': 'Riepilogo delle presenze del personale',
                    'site': 'Cantiere', 'generated': 'Generato il',
                    'period': 'Periodo', 'to': 'a',
                    'headers': ['Data', 'Personale', 'Ingresso', 'Uscita',
                                'Ore Ord.', 'Ore Str.', 'Tipo', 'Turno', 'Area', 'Costo'],
                    'summary_title': 'Riepilogo',
                    'total_regular': 'Totale Ore Ordinarie',
                    'total_overtime': 'Totale Ore Straordinarie',
                    'total_cost': 'Costo Totale',
                    'days_worked': 'Giorni Lavorati',
                    'personnel_count': 'Personale Coinvolto',
                    'page': 'Pagina',
                    'of': 'di',
                    'footer': 'pyArchInit - Gestione Dati Archeologici',
                },
                'en': {
                    'title': 'Attendance Report',
                    'subtitle': 'Personnel attendance summary',
                    'site': 'Site', 'generated': 'Generated on',
                    'period': 'Period', 'to': 'to',
                    'headers': ['Date', 'Personnel', 'Clock In', 'Clock Out',
                                'Regular Hrs', 'Overtime', 'Type', 'Shift', 'Area', 'Cost'],
                    'summary_title': 'Summary',
                    'total_regular': 'Total Regular Hours',
                    'total_overtime': 'Total Overtime Hours',
                    'total_cost': 'Total Cost',
                    'days_worked': 'Days Worked',
                    'personnel_count': 'Personnel Involved',
                    'page': 'Page',
                    'of': 'of',
                    'footer': 'pyArchInit - Archaeological Data Management',
                },
                'de': {
                    'title': 'Anwesenheitsbericht',
                    'subtitle': 'Zusammenfassung der Personalanwesenheit',
                    'site': 'Fundstelle', 'generated': 'Erstellt am',
                    'period': 'Zeitraum', 'to': 'bis',
                    'headers': ['Datum', 'Personal', 'Eingang', 'Ausgang',
                                'Std. Reg.', 'Uberstd.', 'Typ', 'Schicht', 'Bereich', 'Kosten'],
                    'summary_title': 'Zusammenfassung',
                    'total_regular': 'Regulare Stunden Gesamt',
                    'total_overtime': 'Uberstunden Gesamt',
                    'total_cost': 'Gesamtkosten',
                    'days_worked': 'Arbeitstage',
                    'personnel_count': 'Beteiligtes Personal',
                    'page': 'Seite',
                    'of': 'von',
                    'footer': 'pyArchInit - Archaologische Datenverwaltung',
                },
                'es': {
                    'title': 'Informe de Asistencia',
                    'subtitle': 'Resumen de asistencia del personal',
                    'site': 'Sitio', 'generated': 'Generado el',
                    'period': 'Periodo', 'to': 'a',
                    'headers': ['Fecha', 'Personal', 'Entrada', 'Salida',
                                'Hrs Ord.', 'Hrs Extra', 'Tipo', 'Turno', 'Area', 'Coste'],
                    'summary_title': 'Resumen',
                    'total_regular': 'Total Horas Ordinarias',
                    'total_overtime': 'Total Horas Extras',
                    'total_cost': 'Coste Total',
                    'days_worked': 'Dias Trabajados',
                    'personnel_count': 'Personal Involucrado',
                    'page': 'Pagina',
                    'of': 'de',
                    'footer': 'pyArchInit - Gestion de Datos Arqueologicos',
                },
                'fr': {
                    'title': 'Rapport de Presences',
                    'subtitle': 'Resume des presences du personnel',
                    'site': 'Chantier', 'generated': 'Genere le',
                    'period': 'Periode', 'to': 'a',
                    'headers': ['Date', 'Personnel', 'Entree', 'Sortie',
                                'Hrs Ord.', 'Hrs Sup.', 'Type', 'Equipe', 'Zone', 'Cout'],
                    'summary_title': 'Resume',
                    'total_regular': 'Total Heures Ordinaires',
                    'total_overtime': 'Total Heures Supplementaires',
                    'total_cost': 'Cout Total',
                    'days_worked': 'Jours Travailles',
                    'personnel_count': 'Personnel Implique',
                    'page': 'Page',
                    'of': 'de',
                    'footer': 'pyArchInit - Gestion des Donnees Archeologiques',
                },
            }
            t = i18n.get(lang, i18n['en'])

            # --- Resolve personnel names from personale_table ---
            personnel_map = {}
            try:
                pers_search = {'sito': "'" + sito + "'"}
                pers_recs = self.DB_MANAGER.query_bool(pers_search, "PERSONALE")
                for p in pers_recs:
                    personnel_map[p.id_personale] = f"{p.nome} {p.cognome}"
            except Exception:
                pass

            def resolve_name(id_pers):
                if id_pers in personnel_map:
                    return personnel_map[id_pers]
                try:
                    pid = int(id_pers)
                    if pid in personnel_map:
                        return personnel_map[pid]
                except (ValueError, TypeError):
                    pass
                return str(id_pers) if id_pers else ''

            # --- Custom styles ---
            styles = getSampleStyleSheet()
            style_title = ParagraphStyle('PDFTitle', parent=styles['Title'],
                                         fontName='Helvetica-Bold', fontSize=20,
                                         textColor=CLR_HEADER, spaceAfter=2 * mm)
            style_subtitle = ParagraphStyle('PDFSubtitle', parent=styles['Normal'],
                                            fontName='Helvetica', fontSize=11,
                                            textColor=colors.HexColor('#546e7a'), spaceAfter=1 * mm)
            style_section = ParagraphStyle('PDFSection', parent=styles['Heading2'],
                                           fontName='Helvetica-Bold', fontSize=13,
                                           textColor=CLR_HEADER, spaceBefore=6 * mm, spaceAfter=3 * mm)
            style_cell = ParagraphStyle('CellStyle', fontName='Helvetica', fontSize=7.5,
                                        leading=9, alignment=TA_LEFT)
            style_cell_right = ParagraphStyle('CellRight', fontName='Helvetica', fontSize=7.5,
                                              leading=9, alignment=TA_RIGHT)
            style_cell_center = ParagraphStyle('CellCenter', fontName='Helvetica', fontSize=7.5,
                                               leading=9, alignment=TA_CENTER)
            style_header_cell = ParagraphStyle('HeaderCell', fontName='Helvetica-Bold', fontSize=8,
                                               leading=10, textColor=CLR_TEXT_LIGHT, alignment=TA_CENTER)
            style_summary_label = ParagraphStyle('SumLabel', fontName='Helvetica-Bold', fontSize=10,
                                                  textColor=CLR_HEADER)
            style_summary_val = ParagraphStyle('SumVal', fontName='Helvetica-Bold', fontSize=11,
                                                textColor=colors.HexColor('#0d47a1'), alignment=TA_RIGHT)

            # --- Compute date range ---
            dates = [str(rec.data) for rec in self.DATA_LIST if rec.data]
            date_min = min(dates) if dates else '-'
            date_max = max(dates) if dates else '-'

            # --- Compute summary stats ---
            total_regular = 0.0
            total_overtime = 0.0
            total_cost = 0.0
            unique_dates = set()
            unique_personnel = set()
            for rec in self.DATA_LIST:
                try:
                    total_regular += float(rec.ore_ordinarie or 0)
                except (ValueError, TypeError):
                    pass
                try:
                    total_overtime += float(rec.ore_straordinario or 0)
                except (ValueError, TypeError):
                    pass
                try:
                    total_cost += float(rec.costo_giornata or 0)
                except (ValueError, TypeError):
                    pass
                if rec.data:
                    unique_dates.add(str(rec.data))
                if rec.id_personale:
                    unique_personnel.add(rec.id_personale)

            # --- Page header/footer callbacks ---
            def header_footer(canvas, doc):
                canvas.saveState()
                page_w, page_h = landscape(A4)

                # Header bar
                canvas.setFillColor(CLR_HEADER)
                canvas.rect(0, page_h - 18 * mm, page_w, 18 * mm, fill=1, stroke=0)

                # Header accent line
                canvas.setFillColor(colors.HexColor('#3949ab'))
                canvas.rect(0, page_h - 19 * mm, page_w, 1 * mm, fill=1, stroke=0)

                # Logo area / site name in header
                canvas.setFont('Helvetica-Bold', 14)
                canvas.setFillColor(CLR_TEXT_LIGHT)
                canvas.drawString(15 * mm, page_h - 12 * mm, f"pyArchInit")

                canvas.setFont('Helvetica', 10)
                canvas.drawString(55 * mm, page_h - 12 * mm,
                                  f"|  {t['site']}: {sito}  |  {t['period']}: {date_min} {t['to']} {date_max}")

                # Date generated (right side)
                gen_date = datetime.now().strftime('%Y-%m-%d %H:%M')
                canvas.setFont('Helvetica', 9)
                canvas.drawRightString(page_w - 15 * mm, page_h - 12 * mm,
                                       f"{t['generated']}: {gen_date}")

                # Footer
                canvas.setFillColor(CLR_HEADER)
                canvas.rect(0, 0, page_w, 10 * mm, fill=1, stroke=0)

                canvas.setFont('Helvetica', 7)
                canvas.setFillColor(CLR_TEXT_LIGHT)
                canvas.drawString(15 * mm, 3.5 * mm, t['footer'])

                # Page number
                page_num = canvas.getPageNumber()
                canvas.drawRightString(page_w - 15 * mm, 3.5 * mm,
                                       f"{t['page']} {page_num}")

                canvas.restoreState()

            # --- Build document ---
            doc = SimpleDocTemplate(
                file_path,
                pagesize=landscape(A4),
                topMargin=25 * mm,
                bottomMargin=15 * mm,
                leftMargin=12 * mm,
                rightMargin=12 * mm,
            )
            elements = []

            # Title block
            elements.append(Spacer(1, 2 * mm))
            elements.append(Paragraph(t['title'], style_title))
            elements.append(Paragraph(
                f"{t['site']}: <b>{sito}</b> &nbsp;&nbsp;|&nbsp;&nbsp; "
                f"{t['period']}: <b>{date_min}</b> {t['to']} <b>{date_max}</b>",
                style_subtitle))
            elements.append(HRFlowable(width="100%", thickness=0.5, color=CLR_BORDER,
                                       spaceAfter=4 * mm, spaceBefore=2 * mm))

            # --- Data table ---
            headers = t['headers']
            header_row = [Paragraph(h, style_header_cell) for h in headers]
            data_table = [header_row]

            for rec in self.DATA_LIST:
                cost_val = ''
                try:
                    if rec.costo_giornata:
                        cost_val = f"{float(rec.costo_giornata):,.2f}"
                except (ValueError, TypeError):
                    cost_val = str(rec.costo_giornata) if rec.costo_giornata else ''

                row = [
                    Paragraph(str(rec.data) if rec.data else '', style_cell_center),
                    Paragraph(resolve_name(rec.id_personale), style_cell),
                    Paragraph(str(rec.ora_ingresso) if rec.ora_ingresso else '', style_cell_center),
                    Paragraph(str(rec.ora_uscita) if rec.ora_uscita else '', style_cell_center),
                    Paragraph(str(rec.ore_ordinarie) if rec.ore_ordinarie else '', style_cell_center),
                    Paragraph(str(rec.ore_straordinario) if rec.ore_straordinario else '', style_cell_center),
                    Paragraph(str(rec.tipo_giornata) if rec.tipo_giornata else '', style_cell_center),
                    Paragraph(str(rec.turno) if rec.turno else '', style_cell_center),
                    Paragraph(str(rec.area_lavoro) if rec.area_lavoro else '', style_cell),
                    Paragraph(cost_val, style_cell_right),
                ]
                data_table.append(row)

            col_widths = [22 * mm, 42 * mm, 20 * mm, 20 * mm, 20 * mm, 20 * mm,
                          28 * mm, 22 * mm, 38 * mm, 25 * mm]

            tbl = Table(data_table, colWidths=col_widths, repeatRows=1)
            tbl.setStyle(TableStyle([
                # Header row
                ('BACKGROUND', (0, 0), (-1, 0), CLR_HEADER),
                ('TEXTCOLOR', (0, 0), (-1, 0), CLR_TEXT_LIGHT),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
                ('TOPPADDING', (0, 0), (-1, 0), 4),

                # Data rows
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 7.5),
                ('TOPPADDING', (0, 1), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 3),
                ('LEFTPADDING', (0, 0), (-1, -1), 3),
                ('RIGHTPADDING', (0, 0), (-1, -1), 3),

                # Alternating row colors
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, CLR_ROW_ALT]),

                # Grid
                ('GRID', (0, 0), (-1, 0), 0.5, CLR_HEADER),
                ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.HexColor('#3949ab')),
                ('INNERGRID', (0, 1), (-1, -1), 0.25, CLR_BORDER),
                ('BOX', (0, 0), (-1, -1), 0.75, CLR_HEADER),

                # Vertical alignment
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(tbl)

            # --- Summary section ---
            elements.append(Spacer(1, 6 * mm))
            elements.append(Paragraph(t['summary_title'], style_section))

            summary_data = [
                [Paragraph(t['total_regular'], style_summary_label),
                 Paragraph(f"{total_regular:,.1f}", style_summary_val),
                 Paragraph(t['total_overtime'], style_summary_label),
                 Paragraph(f"{total_overtime:,.1f}", style_summary_val)],
                [Paragraph(t['days_worked'], style_summary_label),
                 Paragraph(str(len(unique_dates)), style_summary_val),
                 Paragraph(t['personnel_count'], style_summary_label),
                 Paragraph(str(len(unique_personnel)), style_summary_val)],
                [Paragraph(t['total_cost'], style_summary_label),
                 Paragraph(f"\u20ac {total_cost:,.2f}", style_summary_val),
                 Paragraph('', style_summary_label),
                 Paragraph('', style_summary_val)],
            ]

            summary_col_widths = [55 * mm, 35 * mm, 55 * mm, 35 * mm]
            summary_tbl = Table(summary_data, colWidths=summary_col_widths)
            summary_tbl.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), CLR_SUMMARY_BG),
                ('BOX', (0, 0), (-1, -1), 1, CLR_HEADER),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, CLR_BORDER),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                # Highlight total cost row
                ('BACKGROUND', (0, -1), (1, -1), CLR_TOTAL_ROW),
            ]))
            elements.append(summary_tbl)

            # Build with header/footer
            doc.build(elements, onFirstPage=header_footer, onLaterPages=header_footer)

            QMessageBox.information(self, "OK", f"PDF exported: {file_path}", QMessageBox.StandardButton.Ok)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"PDF export failed: {str(e)}", QMessageBox.StandardButton.Ok)

    def on_pushButton_export_excel_pressed(self):
        """Export attendance records to Excel."""
        if not bool(self.DATA_LIST):
            QMessageBox.warning(self, "Warning", "No records to export.", QMessageBox.StandardButton.Ok)
            return

        home = os.environ['PYARCHINIT_HOME']
        default_name = "attendance_report.csv"
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Excel/CSV", os.path.join(home, default_name), "CSV (*.csv);;Excel (*.xlsx)")
        if not file_path:
            return

        try:
            import csv

            lang = self.L
            hdrs = {'it': ['Data', 'ID Personale', 'Ora Ingresso', 'Ora Uscita', 'Ore Ordinarie', 'Ore Straordinario', 'Tipo Giornata', 'Turno', 'Area Lavoro', 'Costo Giornata', 'Note'],
                    'en': ['Date', 'Personnel ID', 'Clock In', 'Clock Out', 'Regular Hours', 'Overtime Hours', 'Day Type', 'Shift', 'Work Area', 'Daily Cost', 'Notes']}
            headers = hdrs.get(lang, hdrs['en'])

            if file_path.endswith('.xlsx'):
                try:
                    import openpyxl
                    wb = openpyxl.Workbook()
                    ws = wb.active
                    ws.title = "Attendance"
                    ws.append(headers)
                    for rec in self.DATA_LIST:
                        ws.append([
                            str(rec.data) if rec.data else '',
                            rec.id_personale,
                            str(rec.ora_ingresso) if rec.ora_ingresso else '',
                            str(rec.ora_uscita) if rec.ora_uscita else '',
                            rec.ore_ordinarie,
                            rec.ore_straordinario,
                            str(rec.tipo_giornata) if rec.tipo_giornata else '',
                            str(rec.turno) if rec.turno else '',
                            str(rec.area_lavoro) if rec.area_lavoro else '',
                            rec.costo_giornata,
                            str(rec.note) if rec.note else '',
                        ])
                    wb.save(file_path)
                except ImportError:
                    QMessageBox.warning(self, "Warning", "openpyxl not installed. Saving as CSV instead.", QMessageBox.StandardButton.Ok)
                    file_path = file_path.replace('.xlsx', '.csv')

            if file_path.endswith('.csv'):
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(headers)
                    for rec in self.DATA_LIST:
                        writer.writerow([
                            str(rec.data) if rec.data else '',
                            rec.id_personale,
                            str(rec.ora_ingresso) if rec.ora_ingresso else '',
                            str(rec.ora_uscita) if rec.ora_uscita else '',
                            rec.ore_ordinarie,
                            rec.ore_straordinario,
                            str(rec.tipo_giornata) if rec.tipo_giornata else '',
                            str(rec.turno) if rec.turno else '',
                            str(rec.area_lavoro) if rec.area_lavoro else '',
                            rec.costo_giornata,
                            str(rec.note) if rec.note else '',
                        ])

            QMessageBox.information(self, "OK", f"Export completed: {file_path}", QMessageBox.StandardButton.Ok)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Export failed: {str(e)}", QMessageBox.StandardButton.Ok)


## Class end

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = pyarchinit_Presenze()
    ui.show()
    sys.exit(app.exec())
