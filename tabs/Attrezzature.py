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
from qgis.PyQt.QtWidgets import QDialog, QMessageBox
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
    os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'Attrezzature.ui'))


class pyarchinit_Attrezzature(QDialog, MAIN_DIALOG_CLASS):
    L = QgsSettings().value("locale/userLocale", "it", type=str)[:2]
    if L == 'it':
        MSG_BOX_TITLE = "PyArchInit - Scheda Attrezzature"
    elif L == 'en':
        MSG_BOX_TITLE = "PyArchInit - Equipment Form"
    elif L == 'de':
        MSG_BOX_TITLE = "PyArchInit - Ausruestungsformular"
    elif L == 'es':
        MSG_BOX_TITLE = "PyArchInit - Equipamiento de Obra"
    elif L == 'fr':
        MSG_BOX_TITLE = "PyArchInit - Équipements de Chantier"
    elif L == 'ar':
        MSG_BOX_TITLE = "PyArchInit - معدات الموقع"
    elif L == 'ca':
        MSG_BOX_TITLE = "PyArchInit - Equipament d'Obra"
    elif L == 'ro':
        MSG_BOX_TITLE = "PyArchInit - Echipamente Șantier"
    elif L == 'pt':
        MSG_BOX_TITLE = "PyArchInit - Equipamentos de Obra"
    elif L == 'el':
        MSG_BOX_TITLE = "PyArchInit - Εξοπλισμός Εργοταξίου"
    else:
        MSG_BOX_TITLE = "PyArchInit - Equipment Form"

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
    TABLE_NAME = 'attrezzature_table'
    MAPPER_TABLE_CLASS = "ATTREZZATURE"
    NOME_SCHEDA = "Scheda Attrezzature"
    ID_TABLE = "id_attrezzatura"

    if L == 'it':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Sito": "sito",
            "Codice inventario": "codice_inventario",
            "Nome": "nome",
            "Categoria": "categoria",
            "Marca": "marca",
            "Modello": "modello",
            "Numero di serie": "numero_serie",
            "Proprieta": "proprieta",
            "Data acquisto": "data_acquisto",
            "Costo acquisto": "costo_acquisto",
            "Costo noleggio/giorno": "costo_noleggio_giorno",
            "Stato": "stato",
            "Assegnato a": "assegnato_a",
            "Ultima manutenzione": "data_ultima_manutenzione",
            "Prossima manutenzione": "data_prossima_manutenzione",
            "Note": "note"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Sito",
            "Codice inventario",
            "Nome",
            "Categoria",
            "Stato",
            "Assegnato a"
        ]
    elif L == 'en':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Site": "sito",
            "Inventory Code": "codice_inventario",
            "Name": "nome",
            "Category": "categoria",
            "Brand": "marca",
            "Model": "modello",
            "Serial Number": "numero_serie",
            "Ownership": "proprieta",
            "Purchase Date": "data_acquisto",
            "Purchase Cost": "costo_acquisto",
            "Rental Cost/Day": "costo_noleggio_giorno",
            "Status": "stato",
            "Assigned To": "assegnato_a",
            "Last Maintenance": "data_ultima_manutenzione",
            "Next Maintenance": "data_prossima_manutenzione",
            "Notes": "note"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Site",
            "Inventory Code",
            "Name",
            "Category",
            "Status",
            "Assigned To"
        ]
    elif L == 'de':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Fundort": "sito",
            "Inventarnummer": "codice_inventario",
            "Name": "nome",
            "Kategorie": "categoria",
            "Marke": "marca",
            "Modell": "modello",
            "Seriennummer": "numero_serie",
            "Eigentum": "proprieta",
            "Kaufdatum": "data_acquisto",
            "Kaufpreis": "costo_acquisto",
            "Mietkosten/Tag": "costo_noleggio_giorno",
            "Status": "stato",
            "Zugewiesen an": "assegnato_a",
            "Letzte Wartung": "data_ultima_manutenzione",
            "Naechste Wartung": "data_prossima_manutenzione",
            "Anmerkungen": "note"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Fundort",
            "Inventarnummer",
            "Name",
            "Kategorie",
            "Status",
            "Zugewiesen an"
        ]
    elif L == 'es':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Sitio": "sito",
            "Codigo inventario": "codice_inventario",
            "Nombre": "nome",
            "Categoria": "categoria",
            "Marca": "marca",
            "Modelo": "modello",
            "Numero de serie": "numero_serie",
            "Propiedad": "proprieta",
            "Fecha compra": "data_acquisto",
            "Coste compra": "costo_acquisto",
            "Coste alquiler/dia": "costo_noleggio_giorno",
            "Estado": "stato",
            "Asignado a": "assegnato_a",
            "Ultimo mantenimiento": "data_ultima_manutenzione",
            "Proximo mantenimiento": "data_prossima_manutenzione",
            "Notas": "note"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Sitio",
            "Codigo inventario",
            "Nombre",
            "Categoria",
            "Estado",
            "Asignado a"
        ]
    elif L == 'fr':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Site": "sito",
            "Code inventaire": "codice_inventario",
            "Nom": "nome",
            "Categorie": "categoria",
            "Marque": "marca",
            "Modele": "modello",
            "Numero de serie": "numero_serie",
            "Propriete": "proprieta",
            "Date achat": "data_acquisto",
            "Cout achat": "costo_acquisto",
            "Cout location/jour": "costo_noleggio_giorno",
            "Statut": "stato",
            "Assigne a": "assegnato_a",
            "Derniere maintenance": "data_ultima_manutenzione",
            "Prochaine maintenance": "data_prossima_manutenzione",
            "Notes": "note"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Site",
            "Code inventaire",
            "Nom",
            "Categorie",
            "Statut",
            "Assigne a"
        ]
    elif L == 'ar':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "موقع": "sito",
            "رمز الجرد": "codice_inventario",
            "الاسم": "nome",
            "الفئة": "categoria",
            "العلامة التجارية": "marca",
            "الطراز": "modello",
            "الرقم التسلسلي": "numero_serie",
            "الملكية": "proprieta",
            "تاريخ الشراء": "data_acquisto",
            "تكلفة الشراء": "costo_acquisto",
            "تكلفة الإيجار/يوم": "costo_noleggio_giorno",
            "الحالة": "stato",
            "مخصص لـ": "assegnato_a",
            "آخر صيانة": "data_ultima_manutenzione",
            "الصيانة القادمة": "data_prossima_manutenzione",
            "ملاحظات": "note"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "موقع",
            "رمز الجرد",
            "الاسم",
            "الفئة",
            "الحالة",
            "مخصص لـ"
        ]
    elif L == 'ca':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Jaciment": "sito",
            "Codi inventari": "codice_inventario",
            "Nom": "nome",
            "Categoria": "categoria",
            "Marca": "marca",
            "Model": "modello",
            "Numero de serie": "numero_serie",
            "Propietat": "proprieta",
            "Data compra": "data_acquisto",
            "Cost compra": "costo_acquisto",
            "Cost lloguer/dia": "costo_noleggio_giorno",
            "Estat": "stato",
            "Assignat a": "assegnato_a",
            "Ultim manteniment": "data_ultima_manutenzione",
            "Proper manteniment": "data_prossima_manutenzione",
            "Notes": "note"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Jaciment",
            "Codi inventari",
            "Nom",
            "Categoria",
            "Estat",
            "Assignat a"
        ]
    elif L == 'ro':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Sit": "sito",
            "Cod inventar": "codice_inventario",
            "Nume": "nome",
            "Categorie": "categoria",
            "Marca": "marca",
            "Model": "modello",
            "Numar de serie": "numero_serie",
            "Proprietate": "proprieta",
            "Data achizitie": "data_acquisto",
            "Cost achizitie": "costo_acquisto",
            "Cost inchiriere/zi": "costo_noleggio_giorno",
            "Stare": "stato",
            "Atribuit la": "assegnato_a",
            "Ultima mentenanta": "data_ultima_manutenzione",
            "Urmatoarea mentenanta": "data_prossima_manutenzione",
            "Note": "note"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Sit",
            "Cod inventar",
            "Nume",
            "Categorie",
            "Stare",
            "Atribuit la"
        ]
    elif L == 'pt':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Sitio": "sito",
            "Codigo inventario": "codice_inventario",
            "Nome": "nome",
            "Categoria": "categoria",
            "Marca": "marca",
            "Modelo": "modello",
            "Numero de serie": "numero_serie",
            "Propriedade": "proprieta",
            "Data compra": "data_acquisto",
            "Custo compra": "costo_acquisto",
            "Custo aluguer/dia": "costo_noleggio_giorno",
            "Estado": "stato",
            "Atribuido a": "assegnato_a",
            "Ultima manutencao": "data_ultima_manutenzione",
            "Proxima manutencao": "data_prossima_manutenzione",
            "Notas": "note"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Sitio",
            "Codigo inventario",
            "Nome",
            "Categoria",
            "Estado",
            "Atribuido a"
        ]
    elif L == 'el':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Θέση": "sito",
            "Κωδικός απογραφής": "codice_inventario",
            "Όνομα": "nome",
            "Κατηγορία": "categoria",
            "Μάρκα": "marca",
            "Μοντέλο": "modello",
            "Αριθμός σειράς": "numero_serie",
            "Ιδιοκτησία": "proprieta",
            "Ημερομηνία αγοράς": "data_acquisto",
            "Κόστος αγοράς": "costo_acquisto",
            "Κόστος ενοικίασης/ημέρα": "costo_noleggio_giorno",
            "Κατάσταση": "stato",
            "Ανατέθηκε σε": "assegnato_a",
            "Τελευταία συντήρηση": "data_ultima_manutenzione",
            "Επόμενη συντήρηση": "data_prossima_manutenzione",
            "Σημειώσεις": "note"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Θέση",
            "Κωδικός απογραφής",
            "Όνομα",
            "Κατηγορία",
            "Κατάσταση",
            "Ανατέθηκε σε"
        ]
    else:
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Site": "sito",
            "Inventory Code": "codice_inventario",
            "Name": "nome",
            "Category": "categoria",
            "Brand": "marca",
            "Model": "modello",
            "Serial Number": "numero_serie",
            "Ownership": "proprieta",
            "Purchase Date": "data_acquisto",
            "Purchase Cost": "costo_acquisto",
            "Rental Cost/Day": "costo_noleggio_giorno",
            "Status": "stato",
            "Assigned To": "assegnato_a",
            "Last Maintenance": "data_ultima_manutenzione",
            "Next Maintenance": "data_prossima_manutenzione",
            "Notes": "note"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Site",
            "Inventory Code",
            "Name",
            "Category",
            "Status",
            "Assigned To"
        ]

    TABLE_FIELDS = [
        'sito',
        'codice_inventario',
        'nome',
        'categoria',
        'marca',
        'modello',
        'numero_serie',
        'proprieta',
        'data_acquisto',
        'costo_acquisto',
        'costo_noleggio_giorno',
        'stato',
        'assegnato_a',
        'data_ultima_manutenzione',
        'data_prossima_manutenzione',
        'note'
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

        ThemeManager.apply_theme(self)
        self.theme_toggle_btn = ThemeManager.add_theme_toggle_to_form(self)

        self.currentLayerId = None
        self.retranslate_ui()
        QTimer.singleShot(0, self._deferred_init)

    def _deferred_init(self):
        """Load data after the window is visible."""
        try:
            self.on_pushButton_connect_pressed()
        except:
            pass
        self.fill_fields()
        self.set_sito()
        self.msg_sito()

    def retranslate_ui(self):
        """Translate UI labels based on current locale."""
        lang = self.L
        translations = {
            'it': {
                'title': 'pyArchInit Gestione Cantiere - Attrezzature',
                'sito': 'Sito', 'identificazione': 'Identificazione',
                'codice_inventario': 'Codice Inventario', 'nome': 'Nome',
                'categoria': 'Categoria', 'marca': 'Marca', 'modello': 'Modello',
                'numero_serie': 'Numero Serie',
                'proprieta_costi': 'Proprietà e Costi', 'proprieta': 'Proprietà',
                'data_acquisto': 'Data Acquisto', 'costo_acquisto': 'Costo Acquisto',
                'costo_noleggio': 'Costo Noleggio/Giorno',
                'stato_assegnazione': 'Stato e Assegnazione',
                'stato': 'Stato', 'assegnato_a': 'Assegnato a',
                'manutenzione': 'Manutenzione',
                'ultima_manutenzione': 'Ultima Manutenzione',
                'prossima_manutenzione': 'Prossima Manutenzione',
                'note': 'Note', 'ordinamento': 'Ordinamento',
            },
            'en': {
                'title': 'pyArchInit Site Management - Equipment',
                'sito': 'Site', 'identificazione': 'Identification',
                'codice_inventario': 'Inventory Code', 'nome': 'Name',
                'categoria': 'Category', 'marca': 'Brand', 'modello': 'Model',
                'numero_serie': 'Serial Number',
                'proprieta_costi': 'Ownership & Costs', 'proprieta': 'Ownership',
                'data_acquisto': 'Purchase Date', 'costo_acquisto': 'Purchase Cost',
                'costo_noleggio': 'Rental Cost/Day',
                'stato_assegnazione': 'Status & Assignment',
                'stato': 'Status', 'assegnato_a': 'Assigned To',
                'manutenzione': 'Maintenance',
                'ultima_manutenzione': 'Last Maintenance',
                'prossima_manutenzione': 'Next Maintenance',
                'note': 'Notes', 'ordinamento': 'Sort Order',
            },
            'de': {
                'title': 'pyArchInit Grabungsverwaltung - Ausrüstung',
                'sito': 'Fundstelle', 'identificazione': 'Identifikation',
                'codice_inventario': 'Inventarcode', 'nome': 'Name',
                'categoria': 'Kategorie', 'marca': 'Marke', 'modello': 'Modell',
                'numero_serie': 'Seriennummer',
                'proprieta_costi': 'Eigentum & Kosten', 'proprieta': 'Eigentum',
                'data_acquisto': 'Kaufdatum', 'costo_acquisto': 'Kaufpreis',
                'costo_noleggio': 'Mietkosten/Tag',
                'stato_assegnazione': 'Status & Zuweisung',
                'stato': 'Status', 'assegnato_a': 'Zugewiesen an',
                'manutenzione': 'Wartung',
                'ultima_manutenzione': 'Letzte Wartung',
                'prossima_manutenzione': 'Nächste Wartung',
                'note': 'Notizen', 'ordinamento': 'Sortierung',
            },
            'es': {
                'title': 'pyArchInit Gestión de Obra - Equipamiento',
                'sito': 'Sitio', 'identificazione': 'Identificación',
                'codice_inventario': 'Código de Inventario', 'nome': 'Nombre',
                'categoria': 'Categoría', 'marca': 'Marca', 'modello': 'Modelo',
                'numero_serie': 'Número de Serie',
                'proprieta_costi': 'Propiedad y Costes', 'proprieta': 'Propiedad',
                'data_acquisto': 'Fecha de Compra', 'costo_acquisto': 'Coste de Compra',
                'costo_noleggio': 'Coste Alquiler/Día',
                'stato_assegnazione': 'Estado y Asignación',
                'stato': 'Estado', 'assegnato_a': 'Asignado a',
                'manutenzione': 'Mantenimiento',
                'ultima_manutenzione': 'Último Mantenimiento',
                'prossima_manutenzione': 'Próximo Mantenimiento',
                'note': 'Notas', 'ordinamento': 'Orden',
            },
            'fr': {
                'title': 'pyArchInit Gestion de Chantier - Équipement',
                'sito': 'Site', 'identificazione': 'Identification',
                'codice_inventario': 'Code Inventaire', 'nome': 'Nom',
                'categoria': 'Catégorie', 'marca': 'Marque', 'modello': 'Modèle',
                'numero_serie': 'Numéro de Série',
                'proprieta_costi': 'Propriété et Coûts', 'proprieta': 'Propriété',
                'data_acquisto': "Date d'Achat", 'costo_acquisto': "Coût d'Achat",
                'costo_noleggio': 'Coût Location/Jour',
                'stato_assegnazione': 'État et Affectation',
                'stato': 'État', 'assegnato_a': 'Assigné à',
                'manutenzione': 'Maintenance',
                'ultima_manutenzione': 'Dernière Maintenance',
                'prossima_manutenzione': 'Prochaine Maintenance',
                'note': 'Notes', 'ordinamento': 'Classement',
            },
            'ar': {
                'title': 'pyArchInit إدارة الموقع - المعدات',
                'sito': 'الموقع', 'identificazione': 'التعريف',
                'codice_inventario': 'رمز الجرد', 'nome': 'الاسم',
                'categoria': 'الفئة', 'marca': 'العلامة التجارية', 'modello': 'الموديل',
                'numero_serie': 'الرقم التسلسلي',
                'proprieta_costi': 'الملكية والتكاليف', 'proprieta': 'الملكية',
                'data_acquisto': 'تاريخ الشراء', 'costo_acquisto': 'تكلفة الشراء',
                'costo_noleggio': 'تكلفة الإيجار/يوم',
                'stato_assegnazione': 'الحالة والتخصيص',
                'stato': 'الحالة', 'assegnato_a': 'مخصص لـ',
                'manutenzione': 'الصيانة',
                'ultima_manutenzione': 'آخر صيانة',
                'prossima_manutenzione': 'الصيانة القادمة',
                'note': 'ملاحظات', 'ordinamento': 'الترتيب',
            },
            'ca': {
                'title': "pyArchInit Gestió d'Obra - Equipament",
                'sito': 'Lloc', 'identificazione': 'Identificació',
                'codice_inventario': "Codi d'Inventari", 'nome': 'Nom',
                'categoria': 'Categoria', 'marca': 'Marca', 'modello': 'Model',
                'numero_serie': 'Número de Sèrie',
                'proprieta_costi': 'Propietat i Costos', 'proprieta': 'Propietat',
                'data_acquisto': 'Data de Compra', 'costo_acquisto': 'Cost de Compra',
                'costo_noleggio': 'Cost Lloguer/Dia',
                'stato_assegnazione': 'Estat i Assignació',
                'stato': 'Estat', 'assegnato_a': 'Assignat a',
                'manutenzione': 'Manteniment',
                'ultima_manutenzione': 'Últim Manteniment',
                'prossima_manutenzione': 'Proper Manteniment',
                'note': 'Notes', 'ordinamento': 'Ordenació',
            },
            'ro': {
                'title': 'pyArchInit Gestiune Șantier - Echipamente',
                'sito': 'Sit', 'identificazione': 'Identificare',
                'codice_inventario': 'Cod Inventar', 'nome': 'Nume',
                'categoria': 'Categorie', 'marca': 'Marcă', 'modello': 'Model',
                'numero_serie': 'Număr Serie',
                'proprieta_costi': 'Proprietate și Costuri', 'proprieta': 'Proprietate',
                'data_acquisto': 'Data Achiziției', 'costo_acquisto': 'Cost Achiziție',
                'costo_noleggio': 'Cost Închiriere/Zi',
                'stato_assegnazione': 'Stare și Atribuire',
                'stato': 'Stare', 'assegnato_a': 'Atribuit la',
                'manutenzione': 'Întreținere',
                'ultima_manutenzione': 'Ultima Întreținere',
                'prossima_manutenzione': 'Următoarea Întreținere',
                'note': 'Note', 'ordinamento': 'Ordonare',
            },
            'pt': {
                'title': 'pyArchInit Gestão de Obra - Equipamento',
                'sito': 'Sítio', 'identificazione': 'Identificação',
                'codice_inventario': 'Código de Inventário', 'nome': 'Nome',
                'categoria': 'Categoria', 'marca': 'Marca', 'modello': 'Modelo',
                'numero_serie': 'Número de Série',
                'proprieta_costi': 'Propriedade e Custos', 'proprieta': 'Propriedade',
                'data_acquisto': 'Data de Compra', 'costo_acquisto': 'Custo de Compra',
                'costo_noleggio': 'Custo Aluguer/Dia',
                'stato_assegnazione': 'Estado e Atribuição',
                'stato': 'Estado', 'assegnato_a': 'Atribuído a',
                'manutenzione': 'Manutenção',
                'ultima_manutenzione': 'Última Manutenção',
                'prossima_manutenzione': 'Próxima Manutenção',
                'note': 'Notas', 'ordinamento': 'Ordenação',
            },
            'el': {
                'title': 'pyArchInit Διαχείριση Ανασκαφής - Εξοπλισμός',
                'sito': 'Τοποθεσία', 'identificazione': 'Αναγνώριση',
                'codice_inventario': 'Κωδικός Απογραφής', 'nome': 'Όνομα',
                'categoria': 'Κατηγορία', 'marca': 'Μάρκα', 'modello': 'Μοντέλο',
                'numero_serie': 'Σειριακός Αριθμός',
                'proprieta_costi': 'Ιδιοκτησία & Κόστη', 'proprieta': 'Ιδιοκτησία',
                'data_acquisto': 'Ημ. Αγοράς', 'costo_acquisto': 'Κόστος Αγοράς',
                'costo_noleggio': 'Κόστος Ενοικίασης/Ημέρα',
                'stato_assegnazione': 'Κατάσταση & Ανάθεση',
                'stato': 'Κατάσταση', 'assegnato_a': 'Ανατέθηκε σε',
                'manutenzione': 'Συντήρηση',
                'ultima_manutenzione': 'Τελευταία Συντήρηση',
                'prossima_manutenzione': 'Επόμενη Συντήρηση',
                'note': 'Σημειώσεις', 'ordinamento': 'Ταξινόμηση',
            },
        }
        t = translations.get(lang, translations.get('en', translations['it']))
        self.setWindowTitle(t['title'])
        self.label_sito.setText(t['sito'])
        self.groupBox_identificazione.setTitle(t['identificazione'])
        self.label_codice_inventario.setText(t['codice_inventario'])
        self.label_nome_attr.setText(t['nome'])
        self.label_categoria.setText(t['categoria'])
        self.label_marca.setText(t['marca'])
        self.label_modello.setText(t['modello'])
        self.label_numero_serie.setText(t['numero_serie'])
        self.groupBox_proprieta_costi.setTitle(t['proprieta_costi'])
        self.label_proprieta.setText(t['proprieta'])
        self.label_data_acquisto.setText(t['data_acquisto'])
        self.label_costo_acquisto.setText(t['costo_acquisto'])
        self.label_costo_noleggio_giorno.setText(t['costo_noleggio'])
        self.groupBox_stato_assegnazione.setTitle(t['stato_assegnazione'])
        self.label_stato.setText(t['stato'])
        self.label_assegnato_a.setText(t['assegnato_a'])
        self.groupBox_manutenzione.setTitle(t['manutenzione'])
        self.label_data_ultima_manutenzione.setText(t['ultima_manutenzione'])
        self.label_data_prossima_manutenzione.setText(t['prossima_manutenzione'])
        self.label_note.setText(t['note'])
        self.label_lbl_sort.setText(t['ordinamento'])

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
                        "Benvenuto in pyArchInit " + self.NOME_SCHEDA + ". Il database e' vuoto.",
                        QMessageBox.StandardButton.Ok)
                elif self.L == 'de':
                    QMessageBox.warning(self, "WILLKOMMEN",
                        "WILLKOMMEN in pyArchInit " + self.NOME_SCHEDA + ". Die Datenbank ist leer.",
                        QMessageBox.StandardButton.Ok)
                else:
                    QMessageBox.warning(self, "WELCOME",
                        "Welcome in pyArchInit " + self.NOME_SCHEDA + ". The DB is empty.",
                        QMessageBox.StandardButton.Ok)
                self.charge_list()
                self.BROWSE_STATUS = 'x'
                self.on_pushButton_new_rec_pressed()
        except Exception as e:
            e = str(e)
            if e.find("no such table"):
                if self.L == 'it':
                    msg = "La connessione e' fallita {}. E' NECESSARIO RIAVVIARE QGIS".format(str(e))
                elif self.L == 'de':
                    msg = "Verbindungsfehler {}. QGIS neustarten".format(str(e))
                else:
                    msg = "The connection failed {}. You MUST RESTART QGIS".format(str(e))

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
                'cantiere_attrezzature_table', th_lang)

            categoria_values = [v.sigla_estesa for v in thesaurus.get('14.4', [])]
            self.comboBox_categoria.clear()
            self.comboBox_categoria.addItems(categoria_values)

            stato_values = [v.sigla_estesa for v in thesaurus.get('14.5', [])]
            self.comboBox_stato.clear()
            self.comboBox_stato.addItems(stato_values)

            proprieta_values = [v.sigla_estesa for v in thesaurus.get('14.6', [])]
            self.comboBox_proprieta.clear()
            self.comboBox_proprieta.addItems(proprieta_values)
        except Exception as e:
            pass

    def msg_sito(self):
        conn = Connection()
        sito_set = conn.sito_set()
        sito_set_str = sito_set['sito_set']
        if bool(self.comboBox_sito.currentText()) and self.comboBox_sito.currentText() == sito_set_str:
            if self.L == 'it':
                QMessageBox.information(self, "OK", "Sei connesso al sito: %s" % str(sito_set_str), QMessageBox.StandardButton.Ok)
            elif self.L == 'de':
                QMessageBox.information(self, "OK", "Sie sind mit der Stätte verbunden: %s" % str(sito_set_str), QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.information(self, "OK", "You are connected to the site: %s" % str(sito_set_str), QMessageBox.StandardButton.Ok)
        elif sito_set_str == '':
            if self.L == 'it':
                msg = QMessageBox.information(self, "Attenzione", "Non hai settato alcun sito.",
                    QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            elif self.L == 'de':
                msg = QMessageBox.information(self, "Achtung", "Sie haben keine Stätten eingerichtet.",
                    QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            else:
                msg = QMessageBox.information(self, "Warning", "You have not set up any site.",
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
        except Exception as e:
            QMessageBox.warning(self, "Error", "Error: %s" % str(e), QMessageBox.StandardButton.Ok)

    def check_maintenance_alert(self):
        """Check if next maintenance date is past due and show alert."""
        try:
            next_maint = self.lineEdit_data_prossima_manutenzione.date().toString("yyyy-MM-dd")
            if next_maint:
                maint_date = datetime.strptime(next_maint, "%Y-%m-%d").date()
                if maint_date <= date.today():
                    equipment_name = self.comboBox_nome.currentText()
                    if self.L == 'it':
                        QMessageBox.warning(self, "Attenzione - Manutenzione",
                            "L'attrezzatura '%s' necessita di manutenzione!\nData prevista: %s" % (equipment_name, next_maint),
                            QMessageBox.StandardButton.Ok)
                    elif self.L == 'de':
                        QMessageBox.warning(self, "Achtung - Wartung",
                            "Ausrüstung '%s' benötigt Wartung!\nGeplantes Datum: %s" % (equipment_name, next_maint),
                            QMessageBox.StandardButton.Ok)
                    else:
                        QMessageBox.warning(self, "Warning - Maintenance",
                            "Equipment '%s' needs maintenance!\nScheduled date: %s" % (equipment_name, next_maint),
                            QMessageBox.StandardButton.Ok)
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
                        QMessageBox.warning(self, "ATTENZIONE", "Non è stata realizzata alcuna modifica.", QMessageBox.StandardButton.Ok)
                    elif self.L == 'de':
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
                    self.setComboBoxEnable(["self.comboBox_sito"], "False")
                    self.fill_fields(self.REC_CORR)
                    self.enable_button(1)

    def data_error_check(self):
        test = 0
        if self.L == 'it':
            if self.comboBox_sito.currentText() == "":
                QMessageBox.warning(self, "ATTENZIONE", "Campo Sito obbligatorio!", QMessageBox.StandardButton.Ok)
                test = 1
            if self.comboBox_nome.currentText() == "":
                QMessageBox.warning(self, "ATTENZIONE", "Campo Nome obbligatorio!", QMessageBox.StandardButton.Ok)
                test = 1
        elif self.L == 'de':
            if self.comboBox_sito.currentText() == "":
                QMessageBox.warning(self, "ACHTUNG", "Feld Fundort erforderlich!", QMessageBox.StandardButton.Ok)
                test = 1
            if self.comboBox_nome.currentText() == "":
                QMessageBox.warning(self, "ACHTUNG", "Feld Name erforderlich!", QMessageBox.StandardButton.Ok)
                test = 1
        else:
            if self.comboBox_sito.currentText() == "":
                QMessageBox.warning(self, "WARNING", "Site field required!", QMessageBox.StandardButton.Ok)
                test = 1
            if self.comboBox_nome.currentText() == "":
                QMessageBox.warning(self, "WARNING", "Name field required!", QMessageBox.StandardButton.Ok)
                test = 1
        return test

    def insert_new_rec(self):
        try:
            costo_acquisto = None
            if self.lineEdit_costo_acquisto.text():
                try:
                    costo_acquisto = float(self.lineEdit_costo_acquisto.text())
                except ValueError:
                    costo_acquisto = None

            costo_noleggio = None
            if self.lineEdit_costo_noleggio_giorno.text():
                try:
                    costo_noleggio = float(self.lineEdit_costo_noleggio_giorno.text())
                except ValueError:
                    costo_noleggio = None

            data = self.DB_MANAGER.insert_attrezzature_values(
                self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, self.ID_TABLE) + 1,
                str(self.comboBox_sito.currentText()),
                str(self.lineEdit_codice_inventario.text()),
                str(self.comboBox_nome.currentText()),
                str(self.comboBox_categoria.currentText()),
                str(self.lineEdit_marca.text()),
                str(self.lineEdit_modello.text()),
                str(self.lineEdit_numero_serie.text()),
                str(self.comboBox_proprieta.currentText()),
                str(self.lineEdit_data_acquisto.date().toString("yyyy-MM-dd")),
                costo_acquisto,
                costo_noleggio,
                str(self.comboBox_stato.currentText()),
                int(self.comboBox_assegnato_a.currentText()) if self.comboBox_assegnato_a.currentText().strip() else None,
                str(self.lineEdit_data_ultima_manutenzione.date().toString("yyyy-MM-dd")),
                str(self.lineEdit_data_prossima_manutenzione.date().toString("yyyy-MM-dd")),
                str(self.textEdit_note.toPlainText()))

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
            msg = QMessageBox.warning(self, "Attenzione!!!", "Vuoi veramente eliminare il record?",
                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        elif self.L == 'de':
            msg = QMessageBox.warning(self, "Achtung!!!", "Willst du wirklich diesen Eintrag löschen?",
                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        else:
            msg = QMessageBox.warning(self, "Warning!!!", "Do you really want to delete the record?",
                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)

        if msg == QMessageBox.StandardButton.Cancel:
            return
        try:
            id_to_delete = getattr(self.DATA_LIST[self.REC_CORR], self.ID_TABLE)
            self.DB_MANAGER.delete_one_record(self.TABLE_NAME, self.ID_TABLE, id_to_delete)
            self.charge_records()
        except Exception as e:
            QMessageBox.warning(self, "Error", "error type: " + str(e))
        if not bool(self.DATA_LIST):
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
                QMessageBox.warning(self, "ATTENZIONE", "Per eseguire una nuova ricerca clicca sul pulsante 'new search'", QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.warning(self, "WARNING", "To perform a new search click on the 'new search' button", QMessageBox.StandardButton.Ok)
        else:
            search_dict = {
                'sito': "'" + str(self.comboBox_sito.currentText()) + "'",
                'codice_inventario': "'" + str(self.lineEdit_codice_inventario.text()) + "'",
                'nome': "'" + str(self.comboBox_nome.currentText()) + "'",
                'categoria': "'" + str(self.comboBox_categoria.currentText()) + "'",
                'stato': "'" + str(self.comboBox_stato.currentText()) + "'",
                'assegnato_a': "'" + str(self.comboBox_assegnato_a.currentText()) + "'",
                'note': str(self.textEdit_note.toPlainText()),
            }
            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)
            if not bool(search_dict):
                if self.L == 'it':
                    QMessageBox.warning(self, "ATTENZIONE", "Non è stata impostata nessuna ricerca!!!", QMessageBox.StandardButton.Ok)
                else:
                    QMessageBox.warning(self, "WARNING", "No search has been set!!!", QMessageBox.StandardButton.Ok)
            else:
                res = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
                if not bool(res):
                    if self.L == 'it':
                        QMessageBox.warning(self, "ATTENZIONE", "Non e' stato trovato alcun record!", QMessageBox.StandardButton.Ok)
                    else:
                        QMessageBox.warning(self, "Warning", "The record has not been found", QMessageBox.StandardButton.Ok)
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
                        strings = ("Found", self.REC_TOT, "record")
                    else:
                        strings = ("Found", self.REC_TOT, "records")
                    QMessageBox.warning(self, "Message", "%s %d %s" % strings, QMessageBox.StandardButton.Ok)
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
        self.lineEdit_codice_inventario.clear()
        self.comboBox_nome.setEditText("")
        self.comboBox_categoria.setEditText("")
        self.lineEdit_marca.clear()
        self.lineEdit_modello.clear()
        self.lineEdit_numero_serie.clear()
        self.comboBox_proprieta.setEditText("")
        self.lineEdit_data_acquisto.setDate(QDate(2000, 1, 1))
        self.lineEdit_costo_acquisto.clear()
        self.lineEdit_costo_noleggio_giorno.clear()
        self.comboBox_stato.setEditText("")
        self.comboBox_assegnato_a.setEditText("")
        self.lineEdit_data_ultima_manutenzione.setDate(QDate(2000, 1, 1))
        self.lineEdit_data_prossima_manutenzione.setDate(QDate(2000, 1, 1))
        self.textEdit_note.clear()

    def empty_fields(self):
        self.comboBox_sito.setEditText("")
        self.lineEdit_codice_inventario.clear()
        self.comboBox_nome.setEditText("")
        self.comboBox_categoria.setEditText("")
        self.lineEdit_marca.clear()
        self.lineEdit_modello.clear()
        self.lineEdit_numero_serie.clear()
        self.comboBox_proprieta.setEditText("")
        self.lineEdit_data_acquisto.setDate(QDate(2000, 1, 1))
        self.lineEdit_costo_acquisto.clear()
        self.lineEdit_costo_noleggio_giorno.clear()
        self.comboBox_stato.setEditText("")
        self.comboBox_assegnato_a.setEditText("")
        self.lineEdit_data_ultima_manutenzione.setDate(QDate(2000, 1, 1))
        self.lineEdit_data_prossima_manutenzione.setDate(QDate(2000, 1, 1))
        self.textEdit_note.clear()

    def fill_fields(self, n=0):
        self.rec_num = n
        try:
            self.comboBox_sito.setEditText(str(self.DATA_LIST[self.rec_num].sito))
            self.lineEdit_codice_inventario.setText(str(self.DATA_LIST[self.rec_num].codice_inventario) if self.DATA_LIST[self.rec_num].codice_inventario else "")
            self.comboBox_nome.setEditText(str(self.DATA_LIST[self.rec_num].nome) if self.DATA_LIST[self.rec_num].nome else "")
            self.comboBox_categoria.setEditText(str(self.DATA_LIST[self.rec_num].categoria) if self.DATA_LIST[self.rec_num].categoria else "")
            self.lineEdit_marca.setText(str(self.DATA_LIST[self.rec_num].marca) if self.DATA_LIST[self.rec_num].marca else "")
            self.lineEdit_modello.setText(str(self.DATA_LIST[self.rec_num].modello) if self.DATA_LIST[self.rec_num].modello else "")
            self.lineEdit_numero_serie.setText(str(self.DATA_LIST[self.rec_num].numero_serie) if self.DATA_LIST[self.rec_num].numero_serie else "")
            self.comboBox_proprieta.setEditText(str(self.DATA_LIST[self.rec_num].proprieta) if self.DATA_LIST[self.rec_num].proprieta else "")
            date_str = str(self.DATA_LIST[self.rec_num].data_acquisto) if self.DATA_LIST[self.rec_num].data_acquisto else ""
            if date_str:
                qd = QDate.fromString(date_str, "yyyy-MM-dd")
                if not qd.isValid():
                    qd = QDate.fromString(date_str, "dd/MM/yyyy")
                if qd.isValid():
                    self.lineEdit_data_acquisto.setDate(qd)
                else:
                    self.lineEdit_data_acquisto.setDate(QDate.currentDate())
            else:
                self.lineEdit_data_acquisto.setDate(QDate(2000, 1, 1))

            if self.DATA_LIST[self.rec_num].costo_acquisto is not None:
                self.lineEdit_costo_acquisto.setText(str(self.DATA_LIST[self.rec_num].costo_acquisto))
            else:
                self.lineEdit_costo_acquisto.setText("")

            if self.DATA_LIST[self.rec_num].costo_noleggio_giorno is not None:
                self.lineEdit_costo_noleggio_giorno.setText(str(self.DATA_LIST[self.rec_num].costo_noleggio_giorno))
            else:
                self.lineEdit_costo_noleggio_giorno.setText("")

            self.comboBox_stato.setEditText(str(self.DATA_LIST[self.rec_num].stato) if self.DATA_LIST[self.rec_num].stato else "")
            self.comboBox_assegnato_a.setEditText(str(self.DATA_LIST[self.rec_num].assegnato_a) if self.DATA_LIST[self.rec_num].assegnato_a else "")
            date_str = str(self.DATA_LIST[self.rec_num].data_ultima_manutenzione) if self.DATA_LIST[self.rec_num].data_ultima_manutenzione else ""
            if date_str:
                qd = QDate.fromString(date_str, "yyyy-MM-dd")
                if not qd.isValid():
                    qd = QDate.fromString(date_str, "dd/MM/yyyy")
                if qd.isValid():
                    self.lineEdit_data_ultima_manutenzione.setDate(qd)
                else:
                    self.lineEdit_data_ultima_manutenzione.setDate(QDate.currentDate())
            else:
                self.lineEdit_data_ultima_manutenzione.setDate(QDate(2000, 1, 1))
            date_str = str(self.DATA_LIST[self.rec_num].data_prossima_manutenzione) if self.DATA_LIST[self.rec_num].data_prossima_manutenzione else ""
            if date_str:
                qd = QDate.fromString(date_str, "yyyy-MM-dd")
                if not qd.isValid():
                    qd = QDate.fromString(date_str, "dd/MM/yyyy")
                if qd.isValid():
                    self.lineEdit_data_prossima_manutenzione.setDate(qd)
                else:
                    self.lineEdit_data_prossima_manutenzione.setDate(QDate.currentDate())
            else:
                self.lineEdit_data_prossima_manutenzione.setDate(QDate(2000, 1, 1))
            self.textEdit_note.setText(str(self.DATA_LIST[self.rec_num].note) if self.DATA_LIST[self.rec_num].note else "")

            # Check maintenance alert
            self.check_maintenance_alert()
        except:
            pass

    def set_LIST_REC_TEMP(self):
        costo_acq = str(self.lineEdit_costo_acquisto.text()) if self.lineEdit_costo_acquisto.text() else ''
        costo_nol = str(self.lineEdit_costo_noleggio_giorno.text()) if self.lineEdit_costo_noleggio_giorno.text() else ''

        self.DATA_LIST_REC_TEMP = [
            str(self.comboBox_sito.currentText()),
            str(self.lineEdit_codice_inventario.text()),
            str(self.comboBox_nome.currentText()),
            str(self.comboBox_categoria.currentText()),
            str(self.lineEdit_marca.text()),
            str(self.lineEdit_modello.text()),
            str(self.lineEdit_numero_serie.text()),
            str(self.comboBox_proprieta.currentText()),
            str(self.lineEdit_data_acquisto.date().toString("yyyy-MM-dd")),
            costo_acq,
            costo_nol,
            str(self.comboBox_stato.currentText()),
            int(self.comboBox_assegnato_a.currentText()) if self.comboBox_assegnato_a.currentText().strip() else None,
            str(self.lineEdit_data_ultima_manutenzione.date().toString("yyyy-MM-dd")),
            str(self.lineEdit_data_prossima_manutenzione.date().toString("yyyy-MM-dd")),
            str(self.textEdit_note.toPlainText())
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
            QMessageBox.warning(self, "Message",
                "Encoding problem: accents or characters not accepted by the database.",
                QMessageBox.StandardButton.Ok)
            return 0

    def rec_toupdate(self):
        rec_to_update = self.UTILITY.pos_none_in_list(self.DATA_LIST_REC_TEMP)
        return rec_to_update

    def datestrfdate(self):
        now = date.today()
        today = now.strftime("%d-%m-%Y")
        return today


## Class end

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = pyarchinit_Attrezzature()
    ui.show()
    sys.exit(app.exec())
