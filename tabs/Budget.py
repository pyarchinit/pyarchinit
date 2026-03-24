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
from datetime import date
import json
from collections import defaultdict
from qgis.PyQt.QtCore import QDate, QTimer, Qt
from qgis.PyQt.QtWidgets import (QDialog, QMessageBox, QTableWidgetItem,
                                  QHeaderView, QVBoxLayout, QApplication)
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
    os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'Budget.ui'))


class pyarchinit_Budget(QDialog, MAIN_DIALOG_CLASS):
    L = QgsSettings().value("locale/userLocale", "it", type=str)[:2]
    if L == 'it':
        MSG_BOX_TITLE = "PyArchInit - Scheda Budget"
    elif L == 'en':
        MSG_BOX_TITLE = "PyArchInit - Budget Form"
    elif L == 'de':
        MSG_BOX_TITLE = "PyArchInit - Budgetformular"
    elif L == 'es':
        MSG_BOX_TITLE = "PyArchInit - Presupuesto de Obra"
    elif L == 'fr':
        MSG_BOX_TITLE = "PyArchInit - Budget de Chantier"
    elif L == 'ar':
        MSG_BOX_TITLE = "PyArchInit - ميزانية الموقع"
    elif L == 'ca':
        MSG_BOX_TITLE = "PyArchInit - Pressupost d'Obra"
    elif L == 'ro':
        MSG_BOX_TITLE = "PyArchInit - Buget Șantier"
    elif L == 'pt':
        MSG_BOX_TITLE = "PyArchInit - Orçamento de Obra"
    elif L == 'el':
        MSG_BOX_TITLE = "PyArchInit - Προϋπολογισμός Εργοταξίου"
    else:
        MSG_BOX_TITLE = "PyArchInit - Budget Form"

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
    TABLE_NAME = 'budget_table'
    MAPPER_TABLE_CLASS = "BUDGET"
    NOME_SCHEDA = "Scheda Budget"
    ID_TABLE = "id_budget"

    if L == 'it':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Sito": "sito",
            "Anno": "anno",
            "Categoria": "categoria",
            "Descrizione": "descrizione",
            "Importo previsto": "importo_previsto",
            "Importo effettivo": "importo_effettivo",
            "Data registrazione": "data_registrazione",
            "Data spesa": "data_spesa",
            "Fornitore": "fornitore",
            "Numero fattura": "numero_fattura",
            "Note": "note"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Sito",
            "Anno",
            "Categoria",
            "Fornitore",
            "Data spesa"
        ]
    elif L == 'en':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Site": "sito",
            "Year": "anno",
            "Category": "categoria",
            "Description": "descrizione",
            "Estimated Amount": "importo_previsto",
            "Actual Amount": "importo_effettivo",
            "Registration Date": "data_registrazione",
            "Expense Date": "data_spesa",
            "Supplier": "fornitore",
            "Invoice Number": "numero_fattura",
            "Notes": "note"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Site",
            "Year",
            "Category",
            "Supplier",
            "Expense Date"
        ]
    elif L == 'de':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Fundort": "sito",
            "Jahr": "anno",
            "Kategorie": "categoria",
            "Beschreibung": "descrizione",
            "Geplanter Betrag": "importo_previsto",
            "Tatsaechlicher Betrag": "importo_effettivo",
            "Registrierungsdatum": "data_registrazione",
            "Ausgabendatum": "data_spesa",
            "Lieferant": "fornitore",
            "Rechnungsnummer": "numero_fattura",
            "Anmerkungen": "note"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Fundort",
            "Jahr",
            "Kategorie",
            "Lieferant",
            "Ausgabendatum"
        ]
    elif L == 'es':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Sitio": "sito",
            "Ano": "anno",
            "Categoria": "categoria",
            "Descripcion": "descrizione",
            "Importe previsto": "importo_previsto",
            "Importe efectivo": "importo_effettivo",
            "Fecha registro": "data_registrazione",
            "Fecha gasto": "data_spesa",
            "Proveedor": "fornitore",
            "Numero factura": "numero_fattura",
            "Notas": "note"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Sitio",
            "Ano",
            "Categoria",
            "Proveedor",
            "Fecha gasto"
        ]
    elif L == 'fr':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Site": "sito",
            "Annee": "anno",
            "Categorie": "categoria",
            "Description": "descrizione",
            "Montant prevu": "importo_previsto",
            "Montant effectif": "importo_effettivo",
            "Date enregistrement": "data_registrazione",
            "Date depense": "data_spesa",
            "Fournisseur": "fornitore",
            "Numero facture": "numero_fattura",
            "Notes": "note"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Site",
            "Annee",
            "Categorie",
            "Fournisseur",
            "Date depense"
        ]
    elif L == 'ar':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "موقع": "sito",
            "السنة": "anno",
            "الفئة": "categoria",
            "الوصف": "descrizione",
            "المبلغ المتوقع": "importo_previsto",
            "المبلغ الفعلي": "importo_effettivo",
            "تاريخ التسجيل": "data_registrazione",
            "تاريخ الإنفاق": "data_spesa",
            "المورد": "fornitore",
            "رقم الفاتورة": "numero_fattura",
            "ملاحظات": "note"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "موقع",
            "السنة",
            "الفئة",
            "المورد",
            "تاريخ الإنفاق"
        ]
    elif L == 'ca':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Jaciment": "sito",
            "Any": "anno",
            "Categoria": "categoria",
            "Descripcio": "descrizione",
            "Import previst": "importo_previsto",
            "Import efectiu": "importo_effettivo",
            "Data registre": "data_registrazione",
            "Data despesa": "data_spesa",
            "Proveidor": "fornitore",
            "Numero factura": "numero_fattura",
            "Notes": "note"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Jaciment",
            "Any",
            "Categoria",
            "Proveidor",
            "Data despesa"
        ]
    elif L == 'ro':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Sit": "sito",
            "An": "anno",
            "Categorie": "categoria",
            "Descriere": "descrizione",
            "Suma prevazuta": "importo_previsto",
            "Suma efectiva": "importo_effettivo",
            "Data inregistrare": "data_registrazione",
            "Data cheltuiala": "data_spesa",
            "Furnizor": "fornitore",
            "Numar factura": "numero_fattura",
            "Note": "note"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Sit",
            "An",
            "Categorie",
            "Furnizor",
            "Data cheltuiala"
        ]
    elif L == 'pt':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Sitio": "sito",
            "Ano": "anno",
            "Categoria": "categoria",
            "Descricao": "descrizione",
            "Valor previsto": "importo_previsto",
            "Valor efetivo": "importo_effettivo",
            "Data registo": "data_registrazione",
            "Data despesa": "data_spesa",
            "Fornecedor": "fornitore",
            "Numero fatura": "numero_fattura",
            "Notas": "note"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Sitio",
            "Ano",
            "Categoria",
            "Fornecedor",
            "Data despesa"
        ]
    elif L == 'el':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Θέση": "sito",
            "Έτος": "anno",
            "Κατηγορία": "categoria",
            "Περιγραφή": "descrizione",
            "Εκτιμώμενο ποσό": "importo_previsto",
            "Πραγματικό ποσό": "importo_effettivo",
            "Ημερομηνία καταχώρησης": "data_registrazione",
            "Ημερομηνία δαπάνης": "data_spesa",
            "Προμηθευτής": "fornitore",
            "Αριθμός τιμολογίου": "numero_fattura",
            "Σημειώσεις": "note"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Θέση",
            "Έτος",
            "Κατηγορία",
            "Προμηθευτής",
            "Ημερομηνία δαπάνης"
        ]
    else:
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Site": "sito",
            "Year": "anno",
            "Category": "categoria",
            "Description": "descrizione",
            "Estimated Amount": "importo_previsto",
            "Actual Amount": "importo_effettivo",
            "Registration Date": "data_registrazione",
            "Expense Date": "data_spesa",
            "Supplier": "fornitore",
            "Invoice Number": "numero_fattura",
            "Notes": "note"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Site",
            "Year",
            "Category",
            "Supplier",
            "Expense Date"
        ]

    TABLE_FIELDS = [
        'sito',
        'anno',
        'categoria',
        'descrizione',
        'importo_previsto',
        'importo_effettivo',
        'data_registrazione',
        'data_spesa',
        'fornitore',
        'numero_fattura',
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

        # Analytics tab signals
        try:
            self.tabWidget_budget.currentChanged.connect(self.on_tab_changed)
            self.pushButton_refresh_analytics.clicked.connect(self.refresh_analytics)
            self.pushButton_export_analytics_pdf.clicked.connect(self.export_analytics_pdf)
        except:
            pass

    def retranslate_ui(self):
        """Translate UI labels based on current locale."""
        lang = self.L
        translations = {
            'it': {
                'title': 'pyArchInit Gestione Cantiere - Budget',
                'sito': 'Sito', 'anno': 'Anno',
                'voce_spesa': 'Voce di Spesa', 'categoria': 'Categoria',
                'descrizione': 'Descrizione', 'fornitore': 'Fornitore',
                'numero_fattura': 'Numero Fattura', 'data_spesa': 'Data Spesa',
                'data_registrazione': 'Data Registrazione',
                'importi': 'Importi', 'importo_previsto': 'Importo Previsto',
                'importo_effettivo': 'Importo Effettivo',
                'note': 'Note', 'ordinamento': 'Ordinamento',
            },
            'en': {
                'title': 'pyArchInit Site Management - Budget',
                'sito': 'Site', 'anno': 'Year',
                'voce_spesa': 'Expense Item', 'categoria': 'Category',
                'descrizione': 'Description', 'fornitore': 'Supplier',
                'numero_fattura': 'Invoice Number', 'data_spesa': 'Expense Date',
                'data_registrazione': 'Registration Date',
                'importi': 'Amounts', 'importo_previsto': 'Budgeted Amount',
                'importo_effettivo': 'Actual Amount',
                'note': 'Notes', 'ordinamento': 'Sort Order',
            },
            'de': {
                'title': 'pyArchInit Grabungsverwaltung - Budget',
                'sito': 'Fundstelle', 'anno': 'Jahr',
                'voce_spesa': 'Kostenposition', 'categoria': 'Kategorie',
                'descrizione': 'Beschreibung', 'fornitore': 'Lieferant',
                'numero_fattura': 'Rechnungsnummer', 'data_spesa': 'Ausgabendatum',
                'data_registrazione': 'Erfassungsdatum',
                'importi': 'Beträge', 'importo_previsto': 'Geplanter Betrag',
                'importo_effettivo': 'Tatsächlicher Betrag',
                'note': 'Notizen', 'ordinamento': 'Sortierung',
            },
            'es': {
                'title': 'pyArchInit Gestión de Obra - Presupuesto',
                'sito': 'Sitio', 'anno': 'Año',
                'voce_spesa': 'Partida de Gasto', 'categoria': 'Categoría',
                'descrizione': 'Descripción', 'fornitore': 'Proveedor',
                'numero_fattura': 'Número de Factura', 'data_spesa': 'Fecha de Gasto',
                'data_registrazione': 'Fecha de Registro',
                'importi': 'Importes', 'importo_previsto': 'Importe Previsto',
                'importo_effettivo': 'Importe Efectivo',
                'note': 'Notas', 'ordinamento': 'Orden',
            },
            'fr': {
                'title': 'pyArchInit Gestion de Chantier - Budget',
                'sito': 'Site', 'anno': 'Année',
                'voce_spesa': 'Poste de Dépense', 'categoria': 'Catégorie',
                'descrizione': 'Description', 'fornitore': 'Fournisseur',
                'numero_fattura': 'Numéro de Facture', 'data_spesa': 'Date de Dépense',
                'data_registrazione': "Date d'Enregistrement",
                'importi': 'Montants', 'importo_previsto': 'Montant Prévu',
                'importo_effettivo': 'Montant Effectif',
                'note': 'Notes', 'ordinamento': 'Classement',
            },
            'ar': {
                'title': 'pyArchInit إدارة الموقع - الميزانية',
                'sito': 'الموقع', 'anno': 'السنة',
                'voce_spesa': 'بند المصروف', 'categoria': 'الفئة',
                'descrizione': 'الوصف', 'fornitore': 'المورد',
                'numero_fattura': 'رقم الفاتورة', 'data_spesa': 'تاريخ المصروف',
                'data_registrazione': 'تاريخ التسجيل',
                'importi': 'المبالغ', 'importo_previsto': 'المبلغ المخطط',
                'importo_effettivo': 'المبلغ الفعلي',
                'note': 'ملاحظات', 'ordinamento': 'الترتيب',
            },
            'ca': {
                'title': "pyArchInit Gestió d'Obra - Pressupost",
                'sito': 'Lloc', 'anno': 'Any',
                'voce_spesa': 'Partida de Despesa', 'categoria': 'Categoria',
                'descrizione': 'Descripció', 'fornitore': 'Proveïdor',
                'numero_fattura': 'Número de Factura', 'data_spesa': 'Data de Despesa',
                'data_registrazione': "Data d'Enregistrament",
                'importi': 'Imports', 'importo_previsto': 'Import Previst',
                'importo_effettivo': 'Import Efectiu',
                'note': 'Notes', 'ordinamento': 'Ordenació',
            },
            'ro': {
                'title': 'pyArchInit Gestiune Șantier - Buget',
                'sito': 'Sit', 'anno': 'An',
                'voce_spesa': 'Articol de Cheltuială', 'categoria': 'Categorie',
                'descrizione': 'Descriere', 'fornitore': 'Furnizor',
                'numero_fattura': 'Număr Factură', 'data_spesa': 'Data Cheltuielii',
                'data_registrazione': 'Data Înregistrării',
                'importi': 'Sume', 'importo_previsto': 'Sumă Planificată',
                'importo_effettivo': 'Sumă Efectivă',
                'note': 'Note', 'ordinamento': 'Ordonare',
            },
            'pt': {
                'title': 'pyArchInit Gestão de Obra - Orçamento',
                'sito': 'Sítio', 'anno': 'Ano',
                'voce_spesa': 'Rubrica de Despesa', 'categoria': 'Categoria',
                'descrizione': 'Descrição', 'fornitore': 'Fornecedor',
                'numero_fattura': 'Número da Fatura', 'data_spesa': 'Data da Despesa',
                'data_registrazione': 'Data de Registo',
                'importi': 'Montantes', 'importo_previsto': 'Montante Previsto',
                'importo_effettivo': 'Montante Efetivo',
                'note': 'Notas', 'ordinamento': 'Ordenação',
            },
            'el': {
                'title': 'pyArchInit Διαχείριση Ανασκαφής - Προϋπολογισμός',
                'sito': 'Τοποθεσία', 'anno': 'Έτος',
                'voce_spesa': 'Στοιχείο Δαπάνης', 'categoria': 'Κατηγορία',
                'descrizione': 'Περιγραφή', 'fornitore': 'Προμηθευτής',
                'numero_fattura': 'Αριθμός Τιμολογίου', 'data_spesa': 'Ημ. Δαπάνης',
                'data_registrazione': 'Ημ. Καταχώρησης',
                'importi': 'Ποσά', 'importo_previsto': 'Προϋπολογισθέν Ποσό',
                'importo_effettivo': 'Πραγματικό Ποσό',
                'note': 'Σημειώσεις', 'ordinamento': 'Ταξινόμηση',
            },
        }
        # Analytics translations for all 10 languages
        analytics_translations = {
            'it': {
                'tab_data': 'Dati', 'tab_analytics': 'Analisi',
                'total_planned': 'Totale Previsto', 'total_actual': 'Totale Effettivo',
                'variance': 'Scostamento', 'budget_usage': 'Utilizzo Budget',
                'under_budget': 'Sotto Budget', 'over_budget': 'Sopra Budget', 'on_budget': 'In Budget',
                'btn_refresh_analytics': 'Aggiorna Analisi', 'btn_export_analytics': 'Esporta PDF Analisi',
                'chart_category_title': 'Spesa per Categoria',
                'chart_timeline_title': 'Andamento Mensile Spese',
                'chart_variance_title': 'Scostamento per Categoria',
            },
            'en': {
                'tab_data': 'Data', 'tab_analytics': 'Analytics',
                'total_planned': 'Total Planned', 'total_actual': 'Total Actual',
                'variance': 'Variance', 'budget_usage': 'Budget Usage',
                'under_budget': 'Under Budget', 'over_budget': 'Over Budget', 'on_budget': 'On Budget',
                'btn_refresh_analytics': 'Refresh Analytics', 'btn_export_analytics': 'Export Analytics PDF',
                'chart_category_title': 'Spending by Category',
                'chart_timeline_title': 'Monthly Spending Trend',
                'chart_variance_title': 'Variance by Category',
            },
            'de': {
                'tab_data': 'Daten', 'tab_analytics': 'Analytik',
                'total_planned': 'Gesamt Geplant', 'total_actual': 'Gesamt Tatsächlich',
                'variance': 'Abweichung', 'budget_usage': 'Budgetauslastung',
                'under_budget': 'Unter Budget', 'over_budget': 'Über Budget', 'on_budget': 'Im Budget',
                'btn_refresh_analytics': 'Analytik Aktualisieren', 'btn_export_analytics': 'Analytik PDF Exportieren',
                'chart_category_title': 'Ausgaben nach Kategorie',
                'chart_timeline_title': 'Monatlicher Ausgabentrend',
                'chart_variance_title': 'Abweichung nach Kategorie',
            },
            'es': {
                'tab_data': 'Datos', 'tab_analytics': 'Análisis',
                'total_planned': 'Total Previsto', 'total_actual': 'Total Efectivo',
                'variance': 'Desviación', 'budget_usage': 'Uso del Presupuesto',
                'under_budget': 'Bajo Presupuesto', 'over_budget': 'Sobre Presupuesto', 'on_budget': 'En Presupuesto',
                'btn_refresh_analytics': 'Actualizar Análisis', 'btn_export_analytics': 'Exportar PDF Análisis',
                'chart_category_title': 'Gasto por Categoría',
                'chart_timeline_title': 'Tendencia Mensual de Gastos',
                'chart_variance_title': 'Desviación por Categoría',
            },
            'fr': {
                'tab_data': 'Données', 'tab_analytics': 'Analytique',
                'total_planned': 'Total Prévu', 'total_actual': 'Total Effectif',
                'variance': 'Écart', 'budget_usage': 'Utilisation du Budget',
                'under_budget': 'Sous Budget', 'over_budget': 'Hors Budget', 'on_budget': 'Dans le Budget',
                'btn_refresh_analytics': 'Actualiser Analytique', 'btn_export_analytics': 'Exporter PDF Analytique',
                'chart_category_title': 'Dépenses par Catégorie',
                'chart_timeline_title': 'Tendance Mensuelle des Dépenses',
                'chart_variance_title': 'Écart par Catégorie',
            },
            'ar': {
                'tab_data': 'بيانات', 'tab_analytics': 'تحليلات',
                'total_planned': 'إجمالي مخطط', 'total_actual': 'إجمالي فعلي',
                'variance': 'الانحراف', 'budget_usage': 'استخدام الميزانية',
                'under_budget': 'تحت الميزانية', 'over_budget': 'فوق الميزانية', 'on_budget': 'ضمن الميزانية',
                'btn_refresh_analytics': 'تحديث التحليلات', 'btn_export_analytics': 'تصدير PDF التحليلات',
                'chart_category_title': 'الإنفاق حسب الفئة',
                'chart_timeline_title': 'اتجاه الإنفاق الشهري',
                'chart_variance_title': 'الانحراف حسب الفئة',
            },
            'ca': {
                'tab_data': 'Dades', 'tab_analytics': 'Analítica',
                'total_planned': 'Total Previst', 'total_actual': 'Total Efectiu',
                'variance': 'Desviació', 'budget_usage': "Ús del Pressupost",
                'under_budget': 'Sota Pressupost', 'over_budget': 'Sobre Pressupost', 'on_budget': 'En Pressupost',
                'btn_refresh_analytics': 'Actualitzar Analítica', 'btn_export_analytics': 'Exportar PDF Analítica',
                'chart_category_title': 'Despesa per Categoria',
                'chart_timeline_title': 'Tendència Mensual de Despeses',
                'chart_variance_title': 'Desviació per Categoria',
            },
            'ro': {
                'tab_data': 'Date', 'tab_analytics': 'Analiză',
                'total_planned': 'Total Planificat', 'total_actual': 'Total Efectiv',
                'variance': 'Abatere', 'budget_usage': 'Utilizare Buget',
                'under_budget': 'Sub Buget', 'over_budget': 'Peste Buget', 'on_budget': 'În Buget',
                'btn_refresh_analytics': 'Actualizare Analiză', 'btn_export_analytics': 'Exportare PDF Analiză',
                'chart_category_title': 'Cheltuieli pe Categorie',
                'chart_timeline_title': 'Tendința Lunară a Cheltuielilor',
                'chart_variance_title': 'Abatere pe Categorie',
            },
            'pt': {
                'tab_data': 'Dados', 'tab_analytics': 'Análise',
                'total_planned': 'Total Previsto', 'total_actual': 'Total Efetivo',
                'variance': 'Desvio', 'budget_usage': 'Utilização do Orçamento',
                'under_budget': 'Abaixo do Orçamento', 'over_budget': 'Acima do Orçamento', 'on_budget': 'No Orçamento',
                'btn_refresh_analytics': 'Atualizar Análise', 'btn_export_analytics': 'Exportar PDF Análise',
                'chart_category_title': 'Despesa por Categoria',
                'chart_timeline_title': 'Tendência Mensal de Despesas',
                'chart_variance_title': 'Desvio por Categoria',
            },
            'el': {
                'tab_data': 'Δεδομένα', 'tab_analytics': 'Αναλυτικά',
                'total_planned': 'Συνολικός Προϋπολογισμός', 'total_actual': 'Συνολικό Πραγματικό',
                'variance': 'Απόκλιση', 'budget_usage': 'Χρήση Προϋπολογισμού',
                'under_budget': 'Κάτω του Προϋπολογισμού', 'over_budget': 'Πάνω του Προϋπολογισμού', 'on_budget': 'Εντός Προϋπολογισμού',
                'btn_refresh_analytics': 'Ανανέωση Αναλυτικών', 'btn_export_analytics': 'Εξαγωγή PDF Αναλυτικών',
                'chart_category_title': 'Δαπάνες ανά Κατηγορία',
                'chart_timeline_title': 'Μηνιαία Τάση Δαπανών',
                'chart_variance_title': 'Απόκλιση ανά Κατηγορία',
            },
        }
        # Store analytics translations for use in chart methods
        self._analytics_t = analytics_translations.get(lang, analytics_translations.get('en', analytics_translations['it']))

        t = translations.get(lang, translations.get('en', translations['it']))
        self.setWindowTitle(t['title'])
        self.label_sito.setText(t['sito'])
        self.label_anno.setText(t['anno'])
        self.groupBox_voce_spesa.setTitle(t['voce_spesa'])
        self.label_categoria.setText(t['categoria'])
        self.label_descrizione.setText(t['descrizione'])
        self.label_fornitore.setText(t['fornitore'])
        self.label_numero_fattura.setText(t['numero_fattura'])
        self.label_data_spesa.setText(t['data_spesa'])
        self.label_data_registrazione.setText(t['data_registrazione'])
        self.groupBox_importi.setTitle(t['importi'])
        self.label_importo_previsto.setText(t['importo_previsto'])
        self.label_importo_effettivo.setText(t['importo_effettivo'])
        self.label_note.setText(t['note'])
        self.label_lbl_sort.setText(t['ordinamento'])

        # Apply analytics tab labels
        try:
            at = self._analytics_t
            self.tabWidget_budget.setTabText(0, at['tab_data'])
            self.tabWidget_budget.setTabText(1, at['tab_analytics'])
            self.pushButton_refresh_analytics.setText(at['btn_refresh_analytics'])
            self.pushButton_export_analytics_pdf.setText(at['btn_export_analytics'])
        except:
            pass

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
                'cantiere_budget_table', th_lang)

            categoria_values = [v.sigla_estesa for v in thesaurus.get('14.7', [])]
            self.comboBox_categoria.clear()
            self.comboBox_categoria.addItems(categoria_values)
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
        EC = Error_check()

        if self.L == 'it':
            if self.comboBox_sito.currentText() == "":
                QMessageBox.warning(self, "ATTENZIONE", "Campo Sito obbligatorio!", QMessageBox.StandardButton.Ok)
                test = 1
            if self.comboBox_anno.currentText() == "":
                QMessageBox.warning(self, "ATTENZIONE", "Campo Anno obbligatorio!", QMessageBox.StandardButton.Ok)
                test = 1
            elif EC.data_is_int(self.comboBox_anno.currentText()) == 0:
                QMessageBox.warning(self, "ATTENZIONE", "Campo Anno: il valore deve essere numerico", QMessageBox.StandardButton.Ok)
                test = 1
        elif self.L == 'de':
            if self.comboBox_sito.currentText() == "":
                QMessageBox.warning(self, "ACHTUNG", "Feld Fundort erforderlich!", QMessageBox.StandardButton.Ok)
                test = 1
            if self.comboBox_anno.currentText() == "":
                QMessageBox.warning(self, "ACHTUNG", "Feld Jahr erforderlich!", QMessageBox.StandardButton.Ok)
                test = 1
            elif EC.data_is_int(self.comboBox_anno.currentText()) == 0:
                QMessageBox.warning(self, "ACHTUNG", "Feld Jahr: Der Wert muss numerisch sein", QMessageBox.StandardButton.Ok)
                test = 1
        else:
            if self.comboBox_sito.currentText() == "":
                QMessageBox.warning(self, "WARNING", "Site field required!", QMessageBox.StandardButton.Ok)
                test = 1
            if self.comboBox_anno.currentText() == "":
                QMessageBox.warning(self, "WARNING", "Year field required!", QMessageBox.StandardButton.Ok)
                test = 1
            elif EC.data_is_int(self.comboBox_anno.currentText()) == 0:
                QMessageBox.warning(self, "WARNING", "Year field: the value must be numeric", QMessageBox.StandardButton.Ok)
                test = 1

        return test

    def insert_new_rec(self):
        try:
            importo_previsto = None
            if self.lineEdit_importo_previsto.text():
                try:
                    importo_previsto = float(self.lineEdit_importo_previsto.text())
                except ValueError:
                    importo_previsto = None

            importo_effettivo = None
            if self.lineEdit_importo_effettivo.text():
                try:
                    importo_effettivo = float(self.lineEdit_importo_effettivo.text())
                except ValueError:
                    importo_effettivo = None

            data = self.DB_MANAGER.insert_budget_values(
                self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, self.ID_TABLE) + 1,
                str(self.comboBox_sito.currentText()),
                int(self.comboBox_anno.currentText()),
                str(self.comboBox_categoria.currentText()),
                str(self.lineEdit_descrizione.text()),
                importo_previsto,
                importo_effettivo,
                str(self.lineEdit_data_registrazione.date().toString("yyyy-MM-dd")),
                str(self.lineEdit_data_spesa.date().toString("yyyy-MM-dd")),
                str(self.lineEdit_fornitore.text()),
                str(self.lineEdit_numero_fattura.text()),
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
            if self.comboBox_anno.currentText() != "":
                anno = "'" + str(self.comboBox_anno.currentText()) + "'"
            else:
                anno = ""

            search_dict = {
                'sito': "'" + str(self.comboBox_sito.currentText()) + "'",
                'anno': anno,
                'categoria': "'" + str(self.comboBox_categoria.currentText()) + "'",
                'descrizione': str(self.lineEdit_descrizione.text()),
                'fornitore': "'" + str(self.lineEdit_fornitore.text()) + "'",
                'numero_fattura': "'" + str(self.lineEdit_numero_fattura.text()) + "'",
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
        self.comboBox_anno.setEditText("")
        self.comboBox_categoria.setEditText("")
        self.lineEdit_descrizione.clear()
        self.lineEdit_importo_previsto.clear()
        self.lineEdit_importo_effettivo.clear()
        self.lineEdit_data_registrazione.setDate(QDate(2000, 1, 1))
        self.lineEdit_data_spesa.setDate(QDate(2000, 1, 1))
        self.lineEdit_fornitore.clear()
        self.lineEdit_numero_fattura.clear()
        self.textEdit_note.clear()

    def empty_fields(self):
        self.comboBox_sito.setEditText("")
        self.comboBox_anno.setEditText("")
        self.comboBox_categoria.setEditText("")
        self.lineEdit_descrizione.clear()
        self.lineEdit_importo_previsto.clear()
        self.lineEdit_importo_effettivo.clear()
        self.lineEdit_data_registrazione.setDate(QDate(2000, 1, 1))
        self.lineEdit_data_spesa.setDate(QDate(2000, 1, 1))
        self.lineEdit_fornitore.clear()
        self.lineEdit_numero_fattura.clear()
        self.textEdit_note.clear()

    def fill_fields(self, n=0):
        self.rec_num = n
        try:
            self.comboBox_sito.setEditText(str(self.DATA_LIST[self.rec_num].sito))

            if self.DATA_LIST[self.rec_num].anno is not None:
                self.comboBox_anno.setEditText(str(self.DATA_LIST[self.rec_num].anno))
            else:
                self.comboBox_anno.setEditText("")

            self.comboBox_categoria.setEditText(str(self.DATA_LIST[self.rec_num].categoria) if self.DATA_LIST[self.rec_num].categoria else "")
            self.lineEdit_descrizione.setText(str(self.DATA_LIST[self.rec_num].descrizione) if self.DATA_LIST[self.rec_num].descrizione else "")

            if self.DATA_LIST[self.rec_num].importo_previsto is not None:
                self.lineEdit_importo_previsto.setText(str(self.DATA_LIST[self.rec_num].importo_previsto))
            else:
                self.lineEdit_importo_previsto.setText("")

            if self.DATA_LIST[self.rec_num].importo_effettivo is not None:
                self.lineEdit_importo_effettivo.setText(str(self.DATA_LIST[self.rec_num].importo_effettivo))
            else:
                self.lineEdit_importo_effettivo.setText("")

            date_str = str(self.DATA_LIST[self.rec_num].data_registrazione) if self.DATA_LIST[self.rec_num].data_registrazione else ""
            if date_str:
                qd = QDate.fromString(date_str, "yyyy-MM-dd")
                if not qd.isValid():
                    qd = QDate.fromString(date_str, "dd/MM/yyyy")
                if qd.isValid():
                    self.lineEdit_data_registrazione.setDate(qd)
                else:
                    self.lineEdit_data_registrazione.setDate(QDate.currentDate())
            else:
                self.lineEdit_data_registrazione.setDate(QDate(2000, 1, 1))
            date_str = str(self.DATA_LIST[self.rec_num].data_spesa) if self.DATA_LIST[self.rec_num].data_spesa else ""
            if date_str:
                qd = QDate.fromString(date_str, "yyyy-MM-dd")
                if not qd.isValid():
                    qd = QDate.fromString(date_str, "dd/MM/yyyy")
                if qd.isValid():
                    self.lineEdit_data_spesa.setDate(qd)
                else:
                    self.lineEdit_data_spesa.setDate(QDate.currentDate())
            else:
                self.lineEdit_data_spesa.setDate(QDate(2000, 1, 1))
            self.lineEdit_fornitore.setText(str(self.DATA_LIST[self.rec_num].fornitore) if self.DATA_LIST[self.rec_num].fornitore else "")
            self.lineEdit_numero_fattura.setText(str(self.DATA_LIST[self.rec_num].numero_fattura) if self.DATA_LIST[self.rec_num].numero_fattura else "")
            self.textEdit_note.setText(str(self.DATA_LIST[self.rec_num].note) if self.DATA_LIST[self.rec_num].note else "")
        except:
            pass

    def set_LIST_REC_TEMP(self):
        anno = str(self.comboBox_anno.currentText()) if self.comboBox_anno.currentText() else ''
        imp_prev = str(self.lineEdit_importo_previsto.text()) if self.lineEdit_importo_previsto.text() else ''
        imp_eff = str(self.lineEdit_importo_effettivo.text()) if self.lineEdit_importo_effettivo.text() else ''

        self.DATA_LIST_REC_TEMP = [
            str(self.comboBox_sito.currentText()),
            anno,
            str(self.comboBox_categoria.currentText()),
            str(self.lineEdit_descrizione.text()),
            imp_prev,
            imp_eff,
            str(self.lineEdit_data_registrazione.date().toString("yyyy-MM-dd")),
            str(self.lineEdit_data_spesa.date().toString("yyyy-MM-dd")),
            str(self.lineEdit_fornitore.text()),
            str(self.lineEdit_numero_fattura.text()),
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

    # -------------------------------------------------------------------------
    # Analytics methods
    # -------------------------------------------------------------------------

    def on_tab_changed(self, index):
        """When analytics tab is selected, refresh analytics data."""
        if index == 1:
            self.refresh_analytics()

    def refresh_analytics(self):
        """Refresh all analytics widgets with current data."""
        try:
            sito = self.comboBox_sito.currentText()
            if not sito:
                return

            # Query all budget records for the site
            search_dict = {'sito': "'" + str(sito) + "'"}
            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)
            records = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)

            if not records:
                return

            # Populate year filter combobox from available data
            try:
                current_filter = self.comboBox_filter_anno.currentText()
                self.comboBox_filter_anno.blockSignals(True)
                self.comboBox_filter_anno.clear()
                self.comboBox_filter_anno.addItem("")  # All years
                years = sorted(set(str(r.anno) for r in records if r.anno), reverse=True)
                self.comboBox_filter_anno.addItems(years)
                if current_filter:
                    idx = self.comboBox_filter_anno.findText(current_filter)
                    if idx >= 0:
                        self.comboBox_filter_anno.setCurrentIndex(idx)
                self.comboBox_filter_anno.blockSignals(False)
            except AttributeError:
                pass

            # Filter by year if selected
            try:
                anno_filter = self.comboBox_filter_anno.currentText()
                if anno_filter and anno_filter.strip():
                    records = [r for r in records if str(r.anno) == str(anno_filter)]
            except AttributeError:
                pass

            if not records:
                return

            self.update_summary_cards(records)
            self.update_summary_table(records)
            self.draw_category_chart(records)
            self.draw_timeline_chart(records)
            self.draw_variance_chart(records)
        except Exception as e:
            pass

    def update_summary_cards(self, records):
        """Calculate and display summary statistics on card labels."""
        try:
            total_planned = sum(float(r.importo_previsto or 0) for r in records)
            total_actual = sum(float(r.importo_effettivo or 0) for r in records)
            variance = total_planned - total_actual

            self.label_total_planned.setText("{}{:,.2f}".format(chr(8364) + " ", total_planned))
            self.label_total_actual.setText("{}{:,.2f}".format(chr(8364) + " ", total_actual))

            variance_text = "{}{:,.2f}".format(chr(8364) + " ", abs(variance))
            if variance > 0:
                self.label_total_variance.setText("+" + variance_text)
                self.label_total_variance.setStyleSheet("color: #2E7D32; font-weight: bold;")
            elif variance < 0:
                self.label_total_variance.setText("-" + variance_text)
                self.label_total_variance.setStyleSheet("color: #C62828; font-weight: bold;")
            else:
                self.label_total_variance.setText(variance_text)
                self.label_total_variance.setStyleSheet("color: #555555; font-weight: bold;")

            # Progress bar: percentage of budget used
            if total_planned > 0:
                usage_pct = min(int((total_actual / total_planned) * 100), 999)
                self.progressBar_budget_usage.setValue(usage_pct)
                if usage_pct > 100:
                    self.progressBar_budget_usage.setStyleSheet(
                        "QProgressBar::chunk { background-color: #C62828; }")
                else:
                    self.progressBar_budget_usage.setStyleSheet(
                        "QProgressBar::chunk { background-color: #2E7D32; }")
            else:
                self.progressBar_budget_usage.setValue(0)
        except Exception:
            pass

    def update_summary_table(self, records):
        """Populate the budget summary table grouped by category."""
        try:
            at = getattr(self, '_analytics_t', {})
            # Group by category
            cat_data = defaultdict(lambda: {'planned': 0.0, 'actual': 0.0})
            for r in records:
                cat = str(r.categoria) if r.categoria else 'N/A'
                cat_data[cat]['planned'] += float(r.importo_previsto or 0)
                cat_data[cat]['actual'] += float(r.importo_effettivo or 0)

            table = self.tableWidget_budget_summary
            table.clear()
            table.setRowCount(len(cat_data) + 1)  # +1 for totals row
            table.setColumnCount(6)

            # Headers
            headers_map = {
                'it': ['Categoria', 'Previsto', 'Effettivo', 'Scostamento', '%', 'Stato'],
                'en': ['Category', 'Planned', 'Actual', 'Variance', '%', 'Status'],
                'de': ['Kategorie', 'Geplant', 'Tatsächlich', 'Abweichung', '%', 'Status'],
                'es': ['Categoría', 'Previsto', 'Efectivo', 'Desviación', '%', 'Estado'],
                'fr': ['Catégorie', 'Prévu', 'Effectif', 'Écart', '%', 'Statut'],
                'ar': ['الفئة', 'مخطط', 'فعلي', 'انحراف', '%', 'الحالة'],
                'ca': ['Categoria', 'Previst', 'Efectiu', 'Desviació', '%', 'Estat'],
                'ro': ['Categorie', 'Planificat', 'Efectiv', 'Abatere', '%', 'Stare'],
                'pt': ['Categoria', 'Previsto', 'Efetivo', 'Desvio', '%', 'Estado'],
                'el': ['Κατηγορία', 'Προϋπ.', 'Πραγμ.', 'Απόκλιση', '%', 'Κατάσταση'],
            }
            headers = headers_map.get(self.L, headers_map['en'])
            table.setHorizontalHeaderLabels(headers)

            grand_planned = 0.0
            grand_actual = 0.0
            row = 0

            for cat, vals in sorted(cat_data.items()):
                planned = vals['planned']
                actual = vals['actual']
                var = planned - actual
                pct = ((actual / planned) * 100) if planned != 0 else 0.0
                grand_planned += planned
                grand_actual += actual

                table.setItem(row, 0, QTableWidgetItem(cat))
                table.setItem(row, 1, QTableWidgetItem("{:,.2f}".format(planned)))
                table.setItem(row, 2, QTableWidgetItem("{:,.2f}".format(actual)))

                var_item = QTableWidgetItem("{:+,.2f}".format(var))
                pct_item = QTableWidgetItem("{:.1f}%".format(pct))

                if var < 0:
                    color = Qt.GlobalColor.red
                    status_text = at.get('over_budget', 'Over Budget')
                elif var > 0:
                    color = Qt.GlobalColor.darkGreen
                    status_text = at.get('under_budget', 'Under Budget')
                else:
                    color = Qt.GlobalColor.darkGray
                    status_text = at.get('on_budget', 'On Budget')

                var_item.setForeground(color)
                pct_item.setForeground(color)
                table.setItem(row, 3, var_item)
                table.setItem(row, 4, pct_item)
                table.setItem(row, 5, QTableWidgetItem(status_text))
                row += 1

            # Totals row (bold)
            grand_var = grand_planned - grand_actual
            grand_pct = ((grand_actual / grand_planned) * 100) if grand_planned != 0 else 0.0
            totals_label = {'it': 'TOTALE', 'en': 'TOTAL', 'de': 'GESAMT', 'es': 'TOTAL',
                            'fr': 'TOTAL', 'ar': 'المجموع', 'ca': 'TOTAL', 'ro': 'TOTAL',
                            'pt': 'TOTAL', 'el': 'ΣΥΝΟΛΟ'}

            bold_items = [
                QTableWidgetItem(totals_label.get(self.L, 'TOTAL')),
                QTableWidgetItem("{:,.2f}".format(grand_planned)),
                QTableWidgetItem("{:,.2f}".format(grand_actual)),
                QTableWidgetItem("{:+,.2f}".format(grand_var)),
                QTableWidgetItem("{:.1f}%".format(grand_pct)),
                QTableWidgetItem(""),
            ]
            from qgis.PyQt.QtGui import QFont
            bold_font = QFont()
            bold_font.setBold(True)
            for col, item in enumerate(bold_items):
                item.setFont(bold_font)
                if col in (3, 4) and grand_var < 0:
                    item.setForeground(Qt.GlobalColor.red)
                elif col in (3, 4) and grand_var > 0:
                    item.setForeground(Qt.GlobalColor.darkGreen)
                table.setItem(row, col, item)

            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            table.setSortingEnabled(True)
        except Exception:
            pass

    # Professional color palette for all charts
    CHART_COLORS = [
        '#1565C0', '#00897B', '#EF6C00', '#8E24AA', '#C62828',
        '#00838F', '#558B2F', '#6D4C41', '#F9A825', '#AD1457',
    ]

    def draw_category_chart(self, records):
        """Draw a donut chart of actual spending by category using matplotlib (primary)."""
        try:
            at = getattr(self, '_analytics_t', {})
            cat_totals = defaultdict(float)
            for r in records:
                cat = str(r.categoria) if r.categoria else 'N/A'
                cat_totals[cat] += float(r.importo_effettivo or 0)

            if not cat_totals or sum(cat_totals.values()) == 0:
                return

            title_text = at.get('chart_category_title', 'Spending by Category')

            # Primary: matplotlib
            try:
                from matplotlib.figure import Figure
                labels = list(cat_totals.keys())
                sizes = list(cat_totals.values())
                colors = self.CHART_COLORS[:len(labels)]

                fig = Figure(figsize=(4, 3), dpi=80, tight_layout=True)
                fig.patch.set_facecolor('white')
                ax = fig.add_subplot(111)

                wedges, texts, autotexts = ax.pie(
                    sizes, labels=None, colors=colors,
                    autopct='%1.1f%%', startangle=90, pctdistance=0.78,
                    wedgeprops={'width': 0.45, 'edgecolor': 'white', 'linewidth': 2},
                    textprops={'fontsize': 9, 'fontfamily': 'sans-serif'},
                )
                for autotext in autotexts:
                    autotext.set_fontsize(8)
                    autotext.set_color('#333333')

                ax.legend(
                    wedges, ['{} ({}{:,.0f})'.format(l, chr(8364), v) for l, v in zip(labels, sizes)],
                    title=None, loc='center left', bbox_to_anchor=(1.0, 0.5),
                    fontsize=8, frameon=False,
                )
                ax.set_title(title_text, fontsize=12, fontweight='bold',
                             color='#2c3e50', fontfamily='sans-serif', pad=12)
                ax.set_aspect('equal')
                fig.tight_layout()
                self._render_matplotlib_chart(self.widget_chart_category, fig)
                return
            except ImportError:
                pass

            # Fallback: Plotly via QWebEngineView
            self._draw_category_chart_plotly(cat_totals, title_text)
        except Exception:
            pass

    def _draw_category_chart_plotly(self, cat_totals, title_text):
        """Optional Plotly fallback for category chart."""
        try:
            labels = list(cat_totals.keys())
            values = list(cat_totals.values())
            colors = self.CHART_COLORS

            plotly_data = json.dumps([{
                'labels': labels, 'values': values, 'type': 'pie', 'hole': 0.4,
                'marker': {'colors': colors[:len(labels)], 'line': {'color': '#ffffff', 'width': 2}},
                'textinfo': 'label+percent',
                'textfont': {'size': 11, 'family': 'Segoe UI, Helvetica, Arial, sans-serif'},
                'sort': False,
            }])
            plotly_layout = json.dumps({
                'title': {'text': title_text, 'font': {'size': 14, 'color': '#2c3e50'}, 'x': 0.5},
                'margin': {'l': 10, 'r': 10, 't': 40, 'b': 10},
                'paper_bgcolor': 'rgba(0,0,0,0)', 'plot_bgcolor': 'rgba(0,0,0,0)',
                'showlegend': True,
                'legend': {'font': {'size': 10}, 'orientation': 'h', 'y': -0.15, 'x': 0.5, 'xanchor': 'center'},
            })
            html = self._plotly_html_template(plotly_data, plotly_layout)
            self._render_plotly_chart(self.widget_chart_category, html)
        except Exception:
            pass

    def draw_timeline_chart(self, records):
        """Draw a bar+line chart of monthly spending trend using matplotlib (primary)."""
        try:
            at = getattr(self, '_analytics_t', {})
            monthly_actual = defaultdict(float)
            monthly_planned = defaultdict(float)

            for r in records:
                date_str = str(r.data_spesa) if r.data_spesa else ''
                if date_str and len(date_str) >= 7:
                    month_key = date_str[:7]  # yyyy-MM
                else:
                    continue
                monthly_actual[month_key] += float(r.importo_effettivo or 0)
                monthly_planned[month_key] += float(r.importo_previsto or 0)

            if not monthly_actual:
                return

            months = sorted(set(list(monthly_actual.keys()) + list(monthly_planned.keys())))
            actual_vals = [monthly_actual.get(m, 0) for m in months]
            planned_vals = [monthly_planned.get(m, 0) for m in months]

            # Cumulative planned
            cumulative_planned = []
            cum = 0
            for v in planned_vals:
                cum += v
                cumulative_planned.append(cum)

            title_text = at.get('chart_timeline_title', 'Monthly Spending Trend')
            actual_label = at.get('total_actual', 'Actual')
            planned_label = at.get('total_planned', 'Planned (cumul.)')

            # Primary: matplotlib
            try:
                import numpy as np
                from matplotlib.figure import Figure

                fig = Figure(figsize=(4, 3), dpi=80, tight_layout=True)
                fig.patch.set_facecolor('white')
                ax = fig.add_subplot(111)

                x = np.arange(len(months))
                bar_width = 0.6

                bars = ax.bar(x, actual_vals, bar_width, color='#1565C0', edgecolor='white',
                              linewidth=0.5, label=actual_label, zorder=3)

                ax2 = ax.twinx()
                ax2.plot(x, cumulative_planned, color='#EF6C00', linewidth=2.5,
                         marker='o', markersize=5, label=planned_label, zorder=4)
                ax2.set_ylabel(planned_label, fontsize=9, color='#EF6C00', fontfamily='sans-serif')
                ax2.tick_params(axis='y', labelcolor='#EF6C00', labelsize=8)

                ax.set_xticks(x)
                ax.set_xticklabels(months, rotation=45, ha='right', fontsize=8, fontfamily='sans-serif')
                ax.set_ylabel(actual_label, fontsize=9, color='#1565C0', fontfamily='sans-serif')
                ax.tick_params(axis='y', labelcolor='#1565C0', labelsize=8)
                ax.set_title(title_text, fontsize=12, fontweight='bold',
                             color='#2c3e50', fontfamily='sans-serif', pad=12)

                ax.grid(axis='y', alpha=0.3, linestyle='--', zorder=0)
                ax.set_axisbelow(True)

                # Combined legend
                lines_1, labels_1 = ax.get_legend_handles_labels()
                lines_2, labels_2 = ax2.get_legend_handles_labels()
                ax.legend(lines_1 + lines_2, labels_1 + labels_2,
                          loc='upper left', fontsize=8, frameon=True, framealpha=0.9)

                fig.tight_layout()
                self._render_matplotlib_chart(self.widget_chart_timeline, fig)
                return
            except ImportError:
                pass

            # Fallback: Plotly
            self._draw_timeline_chart_plotly(months, actual_vals, cumulative_planned,
                                             title_text, actual_label, planned_label)
        except Exception:
            pass

    def _draw_timeline_chart_plotly(self, months, actual_vals, cumulative_planned,
                                    title_text, actual_label, planned_label):
        """Optional Plotly fallback for timeline chart."""
        try:
            plotly_data = json.dumps([
                {'x': months, 'y': actual_vals, 'type': 'bar', 'name': actual_label,
                 'marker': {'color': '#1565C0'}},
                {'x': months, 'y': cumulative_planned, 'type': 'scatter',
                 'mode': 'lines+markers', 'name': planned_label,
                 'line': {'color': '#EF6C00', 'width': 3}, 'marker': {'size': 6}},
            ])
            plotly_layout = json.dumps({
                'title': {'text': title_text, 'font': {'size': 14, 'color': '#2c3e50'}, 'x': 0.5},
                'margin': {'l': 60, 'r': 20, 't': 40, 'b': 50},
                'paper_bgcolor': 'rgba(0,0,0,0)', 'plot_bgcolor': 'rgba(0,0,0,0)',
                'barmode': 'group', 'showlegend': True,
                'legend': {'font': {'size': 10}, 'orientation': 'h', 'y': -0.25, 'x': 0.5, 'xanchor': 'center'},
                'xaxis': {'tickangle': -45}, 'yaxis': {'tickformat': ',.0f'},
            })
            html = self._plotly_html_template(plotly_data, plotly_layout)
            self._render_plotly_chart(self.widget_chart_timeline, html)
        except Exception:
            pass

    def draw_variance_chart(self, records):
        """Draw a horizontal grouped bar chart for planned vs actual by category using matplotlib (primary)."""
        try:
            at = getattr(self, '_analytics_t', {})
            cat_data = defaultdict(lambda: {'planned': 0.0, 'actual': 0.0})
            for r in records:
                cat = str(r.categoria) if r.categoria else 'N/A'
                cat_data[cat]['planned'] += float(r.importo_previsto or 0)
                cat_data[cat]['actual'] += float(r.importo_effettivo or 0)

            if not cat_data:
                return

            categories = sorted(cat_data.keys())
            planned_vals = [cat_data[c]['planned'] for c in categories]
            actual_vals = [cat_data[c]['actual'] for c in categories]

            title_text = at.get('chart_variance_title', 'Variance by Category')
            planned_label = at.get('total_planned', 'Planned')
            actual_label = at.get('total_actual', 'Actual')

            # Primary: matplotlib
            try:
                import numpy as np
                from matplotlib.figure import Figure

                fig = Figure(figsize=(4, max(2.5, len(categories) * 0.5 + 1)), dpi=80, tight_layout=True)
                fig.patch.set_facecolor('white')
                ax = fig.add_subplot(111)

                y = np.arange(len(categories))
                bar_height = 0.35

                # Planned bars (blue)
                ax.barh(y + bar_height / 2, planned_vals, bar_height, color='#1565C0',
                        edgecolor='white', linewidth=0.5, label=planned_label, zorder=3)

                # Actual bars (green if under budget, red if over)
                actual_colors = ['#C62828' if cat_data[c]['actual'] > cat_data[c]['planned']
                                 else '#00897B' for c in categories]
                ax.barh(y - bar_height / 2, actual_vals, bar_height, color=actual_colors,
                        edgecolor='white', linewidth=0.5, label=actual_label, zorder=3)

                ax.set_yticks(y)
                ax.set_yticklabels(categories, fontsize=9, fontfamily='sans-serif')
                ax.set_title(title_text, fontsize=12, fontweight='bold',
                             color='#2c3e50', fontfamily='sans-serif', pad=12)
                ax.tick_params(axis='x', labelsize=8)

                ax.grid(axis='x', alpha=0.3, linestyle='--', zorder=0)
                ax.set_axisbelow(True)

                # Format x-axis with currency-like numbers
                from matplotlib.ticker import FuncFormatter
                ax.xaxis.set_major_formatter(
                    FuncFormatter(lambda x, p: '{:,.0f}'.format(x)))

                ax.legend(fontsize=8, loc='lower right', frameon=True, framealpha=0.9)
                ax.invert_yaxis()

                fig.tight_layout()
                self._render_matplotlib_chart(self.widget_chart_variance, fig)
                return
            except ImportError:
                pass

            # Fallback: Plotly
            self._draw_variance_chart_plotly(categories, planned_vals, actual_vals, cat_data,
                                             title_text, planned_label, actual_label)
        except Exception:
            pass

    def _draw_variance_chart_plotly(self, categories, planned_vals, actual_vals, cat_data,
                                    title_text, planned_label, actual_label):
        """Optional Plotly fallback for variance chart."""
        try:
            actual_colors = ['#C62828' if cat_data[c]['actual'] > cat_data[c]['planned']
                             else '#00897B' for c in categories]
            plotly_data = json.dumps([
                {'y': categories, 'x': planned_vals, 'type': 'bar', 'name': planned_label,
                 'orientation': 'h', 'marker': {'color': '#1565C0'}},
                {'y': categories, 'x': actual_vals, 'type': 'bar', 'name': actual_label,
                 'orientation': 'h', 'marker': {'color': actual_colors}},
            ])
            plotly_layout = json.dumps({
                'title': {'text': title_text, 'font': {'size': 14, 'color': '#2c3e50'}, 'x': 0.5},
                'margin': {'l': 120, 'r': 20, 't': 40, 'b': 30},
                'paper_bgcolor': 'rgba(0,0,0,0)', 'plot_bgcolor': 'rgba(0,0,0,0)',
                'barmode': 'group', 'showlegend': True,
                'legend': {'font': {'size': 10}, 'orientation': 'h', 'y': -0.2, 'x': 0.5, 'xanchor': 'center'},
                'xaxis': {'tickformat': ',.0f'},
            })
            html = self._plotly_html_template(plotly_data, plotly_layout)
            self._render_plotly_chart(self.widget_chart_variance, html)
        except Exception:
            pass

    @staticmethod
    def _plotly_html_template(plotly_data, plotly_layout):
        """Generate the Plotly HTML wrapper."""
        return '''<!DOCTYPE html>
<html><head>
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
</head><body style="margin:0;padding:0;">
<div id="chart" style="width:100%%;height:100%%;"></div>
<script>
var data = %s;
var layout = %s;
Plotly.newPlot('chart', data, layout, {responsive:true, displayModeBar:false});
</script></body></html>''' % (plotly_data, plotly_layout)

    def _render_plotly_chart(self, widget, fig_html):
        """Render Plotly HTML into a QWebEngineView inside the given widget. Returns True on success."""
        try:
            # Import QWebEngineView from multiple possible paths
            QWebEngineView = None
            for _import_path in [
                ('qgis.PyQt.QtWebEngineWidgets', 'QWebEngineView'),
                ('PyQt5.QtWebEngineWidgets', 'QWebEngineView'),
                ('PyQt6.QtWebEngineWidgets', 'QWebEngineView'),
            ]:
                try:
                    mod = __import__(_import_path[0], fromlist=[_import_path[1]])
                    QWebEngineView = getattr(mod, _import_path[1])
                    break
                except (ImportError, AttributeError):
                    continue

            if QWebEngineView is None:
                return False

            # Clear existing layout
            layout = widget.layout()
            if layout is None:
                layout = QVBoxLayout(widget)
                layout.setContentsMargins(0, 0, 0, 0)
                widget.setLayout(layout)
            else:
                while layout.count():
                    child = layout.takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()

            web_view = QWebEngineView()
            web_view.setHtml(fig_html)
            layout.addWidget(web_view)
            return True
        except Exception:
            return False

    def _render_matplotlib_chart(self, widget, fig):
        """Render a matplotlib Figure into the given widget using FigureCanvasQTAgg."""
        try:
            from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

            layout = widget.layout()
            if layout is None:
                layout = QVBoxLayout(widget)
                layout.setContentsMargins(0, 0, 0, 0)
                widget.setLayout(layout)
            else:
                while layout.count():
                    child = layout.takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()

            canvas = FigureCanvasQTAgg(fig)
            from qgis.PyQt.QtWidgets import QSizePolicy
            canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            canvas.setMinimumHeight(150)
            canvas.setMaximumHeight(300)
            layout.addWidget(canvas)
            canvas.draw()
        except Exception:
            pass

    def export_analytics_pdf(self):
        """Export analytics summary to PDF using ReportLab."""
        try:
            from qgis.PyQt.QtWidgets import QFileDialog
            at = getattr(self, '_analytics_t', {})

            sito = self.comboBox_sito.currentText()
            if not sito:
                QMessageBox.warning(self, "Warning", "Select a site first.", QMessageBox.StandardButton.Ok)
                return

            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Analytics PDF", "",
                "PDF Files (*.pdf);;All Files (*)")
            if not file_path:
                return

            if not file_path.lower().endswith('.pdf'):
                file_path += '.pdf'

            # Get records
            search_dict = {'sito': "'" + str(sito) + "'"}
            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)
            records = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
            if not records:
                QMessageBox.warning(self, "Warning", "No data to export.", QMessageBox.StandardButton.Ok)
                return

            # Filter by year if available
            try:
                anno_filter = self.comboBox_filter_anno.currentText()
                if anno_filter and anno_filter.strip():
                    records = [r for r in records if str(r.anno) == str(anno_filter)]
            except AttributeError:
                pass

            from reportlab.lib.pagesizes import A4
            from reportlab.lib import colors as rl_colors
            from reportlab.lib.units import cm
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet

            doc = SimpleDocTemplate(file_path, pagesize=A4)
            elements = []
            styles = getSampleStyleSheet()

            # Title
            title_text = "Budget Analytics - " + sito
            elements.append(Paragraph(title_text, styles['Title']))
            elements.append(Spacer(1, 0.5 * cm))

            # Summary
            total_planned = sum(float(r.importo_previsto or 0) for r in records)
            total_actual = sum(float(r.importo_effettivo or 0) for r in records)
            variance = total_planned - total_actual

            summary_data = [
                [at.get('total_planned', 'Total Planned'), "{} {:,.2f}".format(chr(8364), total_planned)],
                [at.get('total_actual', 'Total Actual'), "{} {:,.2f}".format(chr(8364), total_actual)],
                [at.get('variance', 'Variance'), "{} {:+,.2f}".format(chr(8364), variance)],
            ]
            summary_table = Table(summary_data, colWidths=[8 * cm, 8 * cm])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), rl_colors.HexColor('#f0f0f0')),
                ('TEXTCOLOR', (0, 0), (-1, -1), rl_colors.black),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, rl_colors.grey),
            ]))
            elements.append(summary_table)
            elements.append(Spacer(1, 1 * cm))

            # Category breakdown table
            cat_data = defaultdict(lambda: {'planned': 0.0, 'actual': 0.0})
            for r in records:
                cat = str(r.categoria) if r.categoria else 'N/A'
                cat_data[cat]['planned'] += float(r.importo_previsto or 0)
                cat_data[cat]['actual'] += float(r.importo_effettivo or 0)

            headers_map = {
                'it': ['Categoria', 'Previsto', 'Effettivo', 'Scostamento', '%'],
                'en': ['Category', 'Planned', 'Actual', 'Variance', '%'],
                'de': ['Kategorie', 'Geplant', 'Tatsächlich', 'Abweichung', '%'],
            }
            headers = headers_map.get(self.L, headers_map['en'])
            table_data = [headers]

            for cat in sorted(cat_data.keys()):
                vals = cat_data[cat]
                var = vals['planned'] - vals['actual']
                pct = ((vals['actual'] / vals['planned']) * 100) if vals['planned'] != 0 else 0
                table_data.append([
                    cat,
                    "{:,.2f}".format(vals['planned']),
                    "{:,.2f}".format(vals['actual']),
                    "{:+,.2f}".format(var),
                    "{:.1f}%".format(pct),
                ])

            detail_table = Table(table_data, colWidths=[5 * cm, 3 * cm, 3 * cm, 3 * cm, 2 * cm])
            detail_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), rl_colors.HexColor('#2c3e50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), rl_colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('GRID', (0, 0), (-1, -1), 0.5, rl_colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [rl_colors.white, rl_colors.HexColor('#f5f5f5')]),
                ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ]))
            elements.append(detail_table)

            doc.build(elements)

            if self.L == 'it':
                msg = "PDF esportato con successo in:\n" + file_path
            elif self.L == 'de':
                msg = "PDF erfolgreich exportiert nach:\n" + file_path
            else:
                msg = "PDF exported successfully to:\n" + file_path
            QMessageBox.information(self, "OK", msg, QMessageBox.StandardButton.Ok)
        except ImportError:
            QMessageBox.warning(self, "Error",
                "ReportLab is required for PDF export. Install it with: pip install reportlab",
                QMessageBox.StandardButton.Ok)
        except Exception as e:
            QMessageBox.warning(self, "Error", "PDF export failed: " + str(e),
                QMessageBox.StandardButton.Ok)


## Class end

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = pyarchinit_Budget()
    ui.show()
    sys.exit(app.exec())
