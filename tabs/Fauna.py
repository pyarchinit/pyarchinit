#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
/***************************************************************************
    pyArchInit Plugin - Archaeological GIS Tools
    Fauna Module - SCHEDA FR (Fauna Record Sheet)
    -------------------
    begin                : 2024
    copyright            : (C) 2024 by Enzo Cocca
    email                : enzo.ccc@gmail.com
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

import os
import json
from datetime import date, datetime

from qgis.PyQt.QtCore import Qt, QDate
from qgis.PyQt.QtGui import QIcon, QFont
from qgis.PyQt.QtWidgets import (
    QDialog, QMessageBox, QTableWidgetItem, QFileDialog, QApplication,
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel, QLineEdit,
    QComboBox, QTextEdit, QDateEdit, QSpinBox, QDoubleSpinBox, QCheckBox,
    QPushButton, QToolBar, QTableWidget, QFormLayout, QDialogButtonBox,
    QHeaderView, QAction, QGroupBox, QGridLayout, QSplitter, QSizePolicy
)
from qgis.core import QgsSettings

from ..modules.utility.pyarchinit_OS_utility import Pyarchinit_OS_Utility
from ..modules.db.pyarchinit_conn_strings import Connection
from ..modules.db.pyarchinit_db_manager import get_db_manager
from ..modules.db.pyarchinit_utility import Utility
from ..modules.utility.pyarchinit_error_check import Error_check
from ..gui.pyarchinitConfigDialog import pyArchInitDialog_Config
from ..modules.utility.pyarchinit_exp_Faunasheet_pdf import generate_fauna_pdf
from ..modules.utility.pyarchinit_theme_manager import ThemeManager


class pyarchinit_Fauna(QDialog):
    """
    Fauna form for SCHEDA FR (Fauna Record Sheet).

    This module provides:
    - Data entry and management for fauna/archaeozoological data
    - Integration with pyArchInit database
    - Support for both SQLite and PostgreSQL
    """

    # Supported languages: IT, EN, DE, ES, FR, AR, CA
    # Default to Italian if language not supported
    SUPPORTED_LANGUAGES = ['it', 'en', 'de', 'es', 'fr', 'ar', 'ca']
    _raw_locale = QgsSettings().value("locale/userLocale", "it")[0:2]
    L = _raw_locale if _raw_locale in SUPPORTED_LANGUAGES else 'it'

    # Localized messages
    if L == 'it':
        MSG_BOX_TITLE = "PyArchInit - Scheda Fauna"
        STATUS_ITEMS = {"b": "Usa", "f": "Trova", "n": "Nuovo Record", "x": "Nessun record"}
        SORTED_ITEMS = {"n": "Non ordinati", "o": "Ordinati"}
    elif L == 'de':
        MSG_BOX_TITLE = "PyArchInit - Fauna Formular"
        STATUS_ITEMS = {"b": "Aktuell", "f": "Finden", "n": "Neuer Rekord", "x": "Kein Rekord"}
        SORTED_ITEMS = {"n": "Nicht sortiert", "o": "Sortiert"}
    elif L == 'fr':
        MSG_BOX_TITLE = "PyArchInit - Fiche Faune"
        STATUS_ITEMS = {"b": "Utiliser", "f": "Chercher", "n": "Nouveau", "x": "Aucun enregistrement"}
        SORTED_ITEMS = {"n": "Non triés", "o": "Triés"}
    elif L == 'es':
        MSG_BOX_TITLE = "PyArchInit - Ficha Fauna"
        STATUS_ITEMS = {"b": "Usar", "f": "Buscar", "n": "Nuevo Registro", "x": "Sin registro"}
        SORTED_ITEMS = {"n": "No ordenados", "o": "Ordenados"}
    elif L == 'ar':
        MSG_BOX_TITLE = "PyArchInit - استمارة الحيوانات"
        STATUS_ITEMS = {"b": "استخدام", "f": "بحث", "n": "سجل جديد", "x": "لا يوجد سجل"}
        SORTED_ITEMS = {"n": "غير مرتب", "o": "مرتب"}
    elif L == 'ca':
        MSG_BOX_TITLE = "PyArchInit - Fitxa Fauna"
        STATUS_ITEMS = {"b": "Usar", "f": "Cercar", "n": "Nou Registre", "x": "Sense registre"}
        SORTED_ITEMS = {"n": "No ordenats", "o": "Ordenats"}
    else:  # English as fallback for supported languages
        MSG_BOX_TITLE = "PyArchInit - Fauna Form"
        STATUS_ITEMS = {"b": "Use", "f": "Find", "n": "New Record", "x": "No record"}
        SORTED_ITEMS = {"n": "Not sorted", "o": "Sorted"}

    DATA_LIST = []
    DATA_LIST_REC_CORR = []
    DATA_LIST_REC_TEMP = []
    REC_CORR = 0
    REC_TOT = 0

    BROWSE_STATUS = "b"
    SORT_MODE = 'asc'
    SORT_STATUS = "n"

    UTILITY = Utility()
    DB_MANAGER = ""
    TABLE_NAME = 'fauna_table'
    MAPPER_TABLE_CLASS = "FAUNA"
    NOME_SCHEDA = "Scheda Fauna"
    ID_TABLE = "id_fauna"

    CONVERSION_DICT = {
        ID_TABLE: ID_TABLE,
        "Sito": "sito",
        "Area": "area",
        "Saggio": "saggio",
        "US": "us",
        "Datazione US": "datazione_us",
        "Responsabile": "responsabile_scheda",
        "Data Compilazione": "data_compilazione",
        "Contesto": "contesto",
        "Specie": "specie",
        "NMI": "numero_minimo_individui"
    }

    SORT_ITEMS = [
        ID_TABLE,
        "Sito",
        "Area",
        "US",
        "Contesto",
        "Specie",
        "NMI"
    ]

    TABLE_FIELDS = [
        "id_us",
        "sito",
        "area",
        "saggio",
        "us",
        "datazione_us",
        "responsabile_scheda",
        "data_compilazione",
        "documentazione_fotografica",
        "metodologia_recupero",
        "contesto",
        "descrizione_contesto",
        "resti_connessione_anatomica",
        "tipologia_accumulo",
        "deposizione",
        "numero_stimato_resti",
        "numero_minimo_individui",
        "specie",
        "parti_scheletriche",
        "specie_psi",
        "misure_ossa",
        "stato_frammentazione",
        "tracce_combustione",
        "combustione_altri_materiali_us",
        "tipo_combustione",
        "segni_tafonomici_evidenti",
        "caratterizzazione_segni_tafonomici",
        "stato_conservazione",
        "alterazioni_morfologiche",
        "note_terreno_giacitura",
        "campionature_effettuate",
        "affidabilita_stratigrafica",
        "classi_reperti_associazione",
        "osservazioni",
        "interpretazione"
    ]

    DB_SERVER = "not defined"

    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.pyQGIS = Pyarchinit_OS_Utility()

        # Try to connect to database
        try:
            self.connect_to_db()
        except Exception as e:
            if self.L == 'it':
                QMessageBox.warning(self, "Errore Database",
                    f"Impossibile connettersi al database: {str(e)}\nVerifica la configurazione.")
            elif self.L == 'de':
                QMessageBox.warning(self, "Datenbankfehler",
                    f"Datenbankverbindung fehlgeschlagen: {str(e)}\nBitte überprüfen Sie die Konfiguration.")
            elif self.L == 'fr':
                QMessageBox.warning(self, "Erreur Base de données",
                    f"Impossible de se connecter à la base de données: {str(e)}\nVérifiez votre configuration.")
            elif self.L == 'es':
                QMessageBox.warning(self, "Error de Base de datos",
                    f"No se pudo conectar a la base de datos: {str(e)}\nPor favor verifique su configuración.")
            else:
                QMessageBox.warning(self, "Database Error",
                    f"Could not connect to database: {str(e)}\nPlease check your configuration.")

        # Setup UI
        self.setup_ui()

        # Apply theme
        ThemeManager.apply_theme(self)
        self.theme_toggle_btn = ThemeManager.add_theme_toggle_to_form(self)

        # Load initial data
        self.charge_list()
        self.set_sito()
        self.fill_fields()

    def connect_to_db(self):
        """Connect to the pyArchInit database."""
        conn = Connection()
        conn_str = conn.conn_str()

        try:
            self.DB_MANAGER = get_db_manager(conn_str, use_singleton=True)
            # Determine DB server type
            test_conn = conn_str.find('sqlite')
            if test_conn == 0:
                self.DB_SERVER = "sqlite"
            else:
                self.DB_SERVER = "postgres"
        except Exception as e:
            self.DB_MANAGER = None
            raise e

    def setup_ui(self):
        """Setup the user interface."""
        self.setWindowTitle(self.MSG_BOX_TITLE)
        self.setMinimumSize(900, 700)

        main_layout = QVBoxLayout(self)

        # Toolbar
        self.create_toolbar()
        main_layout.addWidget(self.toolbar)

        # Status and record info
        status_layout = QHBoxLayout()
        self.label_status = QLabel(self.STATUS_ITEMS[self.BROWSE_STATUS])
        self.label_status.setStyleSheet("font-weight: bold; color: #2c3e50;")
        status_layout.addWidget(QLabel("Status:"))
        status_layout.addWidget(self.label_status)
        status_layout.addStretch()

        self.label_rec_corrente = QLabel("0")
        self.label_rec_tot = QLabel("0")
        status_layout.addWidget(QLabel("Record:"))
        status_layout.addWidget(self.label_rec_corrente)
        status_layout.addWidget(QLabel("/"))
        status_layout.addWidget(self.label_rec_tot)

        main_layout.addLayout(status_layout)

        # Tab widget
        self.tabWidget = QTabWidget()

        # Tab 1: Dati Identificativi
        self.tab_identificativi = self.create_tab_identificativi()
        self.tabWidget.addTab(self.tab_identificativi, self.tr("Dati Identificativi"))

        # Tab 2: Dati Archeozoologici
        self.tab_archeozoologici = self.create_tab_archeozoologici()
        self.tabWidget.addTab(self.tab_archeozoologici, self.tr("Dati Archeozoologici"))

        # Tab 3: Dati Tafonomici
        self.tab_tafonomici = self.create_tab_tafonomici()
        self.tabWidget.addTab(self.tab_tafonomici, self.tr("Dati Tafonomici"))

        # Tab 4: Dati Contestuali
        self.tab_contestuali = self.create_tab_contestuali()
        self.tabWidget.addTab(self.tab_contestuali, self.tr("Dati Contestuali"))

        # Tab 5: Statistiche
        self.tab_statistiche = self.create_tab_statistiche()
        self.tabWidget.addTab(self.tab_statistiche, self.tr("Statistiche"))

        main_layout.addWidget(self.tabWidget)

    def create_toolbar(self):
        """Create the main toolbar."""
        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)

        # Navigation
        self.pushButton_first_rec = self.toolbar.addAction("⏮")
        self.pushButton_first_rec.setToolTip(self.tr("First record"))
        self.pushButton_first_rec.triggered.connect(self.on_pushButton_first_rec_pressed)

        self.pushButton_prev_rec = self.toolbar.addAction("◀")
        self.pushButton_prev_rec.setToolTip(self.tr("Previous record"))
        self.pushButton_prev_rec.triggered.connect(self.on_pushButton_prev_rec_pressed)

        self.pushButton_next_rec = self.toolbar.addAction("▶")
        self.pushButton_next_rec.setToolTip(self.tr("Next record"))
        self.pushButton_next_rec.triggered.connect(self.on_pushButton_next_rec_pressed)

        self.pushButton_last_rec = self.toolbar.addAction("⏭")
        self.pushButton_last_rec.setToolTip(self.tr("Last record"))
        self.pushButton_last_rec.triggered.connect(self.on_pushButton_last_rec_pressed)

        self.toolbar.addSeparator()

        # Actions
        self.pushButton_new_rec = self.toolbar.addAction("➕")
        self.pushButton_new_rec.setToolTip(self.tr("New record"))
        self.pushButton_new_rec.triggered.connect(self.on_pushButton_new_rec_pressed)

        self.pushButton_save = self.toolbar.addAction("💾")
        self.pushButton_save.setToolTip(self.tr("Save"))
        self.pushButton_save.triggered.connect(self.on_pushButton_save_pressed)

        self.pushButton_delete = self.toolbar.addAction("🗑")
        self.pushButton_delete.setToolTip(self.tr("Delete record"))
        self.pushButton_delete.triggered.connect(self.on_pushButton_delete_pressed)

        self.toolbar.addSeparator()

        self.pushButton_view_all = self.toolbar.addAction("📋")
        self.pushButton_view_all.setToolTip(self.tr("View all records"))
        self.pushButton_view_all.triggered.connect(self.on_pushButton_view_all_pressed)

        self.toolbar.addSeparator()

        # Search
        self.pushButton_new_search = self.toolbar.addAction("🔍")
        self.pushButton_new_search.setToolTip(self.tr("New search"))
        self.pushButton_new_search.triggered.connect(self.on_pushButton_new_search_pressed)

        self.pushButton_search_go = self.toolbar.addAction("▶🔍")
        self.pushButton_search_go.setToolTip(self.tr("Execute search"))
        self.pushButton_search_go.triggered.connect(self.on_pushButton_search_go_pressed)

        self.toolbar.addSeparator()

        # PDF Export
        self.pushButton_exp_pdf_sheet = self.toolbar.addAction("📄")
        self.pushButton_exp_pdf_sheet.setToolTip(self.tr("Export PDF sheets"))
        self.pushButton_exp_pdf_sheet.triggered.connect(self.on_pushButton_exp_pdf_sheet_pressed)

    def create_tab_identificativi(self) -> QWidget:
        """Create the identification data tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Identification Group
        group_id = QGroupBox(self.tr("Dati Identificativi (da US)"))
        form_id = QFormLayout(group_id)

        self.lineEdit_id_fauna = QLineEdit()
        self.lineEdit_id_fauna.setReadOnly(True)
        form_id.addRow("ID:", self.lineEdit_id_fauna)

        # ComboBox to select US (shows "sito - area - us")
        self.comboBox_us_select = QComboBox()
        self.comboBox_us_select.setEditable(False)
        self.comboBox_us_select.currentIndexChanged.connect(self.on_us_selected)
        form_id.addRow(self.tr("Seleziona US") + " *:", self.comboBox_us_select)

        self.comboBox_sito = QComboBox()
        self.comboBox_sito.setEditable(True)
        self.comboBox_sito.currentIndexChanged.connect(self.on_sito_changed)
        form_id.addRow(self.tr("Sito") + " *:", self.comboBox_sito)

        self.comboBox_area = QComboBox()
        self.comboBox_area.setEditable(True)
        self.comboBox_area.currentIndexChanged.connect(self.on_area_changed)
        form_id.addRow(self.tr("Area") + ":", self.comboBox_area)

        self.lineEdit_saggio = QLineEdit()
        form_id.addRow(self.tr("Saggio") + ":", self.lineEdit_saggio)

        self.lineEdit_us = QLineEdit()
        form_id.addRow("US:", self.lineEdit_us)

        self.lineEdit_datazione_us = QLineEdit()
        form_id.addRow(self.tr("Datazione US") + ":", self.lineEdit_datazione_us)

        layout.addWidget(group_id)

        # Depositional Group
        group_dep = QGroupBox(self.tr("Dati Deposizionali"))
        form_dep = QFormLayout(group_dep)

        self.lineEdit_responsabile = QLineEdit()
        form_dep.addRow(self.tr("Responsabile") + ":", self.lineEdit_responsabile)

        self.dateEdit_compilazione = QDateEdit()
        self.dateEdit_compilazione.setDate(QDate.currentDate())
        self.dateEdit_compilazione.setCalendarPopup(True)
        form_dep.addRow(self.tr("Data Compilazione") + ":", self.dateEdit_compilazione)

        self.lineEdit_doc_foto = QLineEdit()
        form_dep.addRow(self.tr("Doc. Fotografica") + ":", self.lineEdit_doc_foto)

        self.comboBox_metodologia = QComboBox()
        self.comboBox_metodologia.setEditable(True)
        self.comboBox_metodologia.addItem("")  # Empty default, thesaurus will populate
        form_dep.addRow(self.tr("Metodologia Recupero") + ":", self.comboBox_metodologia)

        self.comboBox_contesto = QComboBox()
        self.comboBox_contesto.setEditable(True)
        self.comboBox_contesto.addItem("")  # Empty default, thesaurus will populate
        form_dep.addRow(self.tr("Contesto") + ":", self.comboBox_contesto)

        self.textEdit_desc_contesto = QTextEdit()
        self.textEdit_desc_contesto.setMaximumHeight(80)
        form_dep.addRow(self.tr("Descrizione Contesto") + ":", self.textEdit_desc_contesto)

        layout.addWidget(group_dep)
        layout.addStretch()

        return widget

    def create_tab_archeozoologici(self) -> QWidget:
        """Create the archaeozoological data tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        form = QFormLayout()

        self.comboBox_connessione = QComboBox()
        self.comboBox_connessione.setEditable(True)
        self.comboBox_connessione.addItem("")  # Empty default, thesaurus will populate
        form.addRow(self.tr("Connessione Anatomica") + ":", self.comboBox_connessione)

        self.comboBox_tipologia_accumulo = QComboBox()
        self.comboBox_tipologia_accumulo.setEditable(True)
        form.addRow(self.tr("Tipologia Accumulo") + ":", self.comboBox_tipologia_accumulo)

        self.comboBox_deposizione = QComboBox()
        self.comboBox_deposizione.setEditable(True)
        self.comboBox_deposizione.addItem("")  # Empty default, thesaurus will populate
        form.addRow(self.tr("Deposizione") + ":", self.comboBox_deposizione)

        self.lineEdit_num_stimato = QLineEdit()
        form.addRow(self.tr("Numero Stimato Resti") + ":", self.lineEdit_num_stimato)

        self.spinBox_nmi = QSpinBox()
        self.spinBox_nmi.setMaximum(9999)
        form.addRow("NMI:", self.spinBox_nmi)

        layout.addLayout(form)

        # ========== TABELLA SPECIE E PSI ==========
        label_specie = QLabel("<b>" + self.tr("Specie e Parti Scheletriche (PSI)") + ":</b>")
        layout.addWidget(label_specie)

        # Toolbar per tabella specie/PSI
        toolbar_specie = QToolBar()
        toolbar_specie.setMovable(False)
        btn_add_specie = QPushButton("+ " + self.tr("Aggiungi Riga"))
        btn_add_specie.clicked.connect(self.add_specie_psi_row)
        toolbar_specie.addWidget(btn_add_specie)
        btn_remove_specie = QPushButton("- " + self.tr("Rimuovi Riga"))
        btn_remove_specie.clicked.connect(self.remove_specie_psi_row)
        toolbar_specie.addWidget(btn_remove_specie)
        layout.addWidget(toolbar_specie)

        # Tabella Specie e PSI
        self.tableWidget_specie_psi = QTableWidget()
        self.tableWidget_specie_psi.setColumnCount(2)
        self.tableWidget_specie_psi.setHorizontalHeaderLabels([self.tr("Specie"), self.tr("PSI (Parti Scheletriche)")])
        self.tableWidget_specie_psi.horizontalHeader().setStretchLastSection(True)
        self.tableWidget_specie_psi.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tableWidget_specie_psi.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tableWidget_specie_psi.setMinimumHeight(120)
        self.tableWidget_specie_psi.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.tableWidget_specie_psi)

        # ========== TABELLA MISURE OSSA ==========
        label_misure = QLabel("<b>" + self.tr("Misure Ossa") + ":</b>")
        layout.addWidget(label_misure)

        # Toolbar per tabella misure
        toolbar_misure = QToolBar()
        toolbar_misure.setMovable(False)
        btn_add_misura = QPushButton("+ " + self.tr("Aggiungi Riga"))
        btn_add_misura.clicked.connect(self.add_misura_row)
        toolbar_misure.addWidget(btn_add_misura)
        btn_remove_misura = QPushButton("- " + self.tr("Rimuovi Riga"))
        btn_remove_misura.clicked.connect(self.remove_misura_row)
        toolbar_misure.addWidget(btn_remove_misura)
        layout.addWidget(toolbar_misure)

        # Tabella Misure (6 colonne)
        self.tableWidget_misure = QTableWidget()
        self.tableWidget_misure.setColumnCount(6)
        self.tableWidget_misure.setHorizontalHeaderLabels([
            self.tr("Elemento Anatomico"), self.tr("Specie"),
            "GL (mm)", "GB (mm)", "Bp (mm)", "Bd (mm)"
        ])
        self.tableWidget_misure.horizontalHeader().setStretchLastSection(True)
        for i in range(6):
            self.tableWidget_misure.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)
        self.tableWidget_misure.setMinimumHeight(120)
        self.tableWidget_misure.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.tableWidget_misure)

        layout.addStretch()

        return widget

    def create_tab_tafonomici(self) -> QWidget:
        """Create the taphonomic data tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        form = QFormLayout()

        self.comboBox_frammentazione = QComboBox()
        self.comboBox_frammentazione.setEditable(True)
        self.comboBox_frammentazione.addItem("")  # Empty default, thesaurus will populate
        form.addRow(self.tr("Stato Frammentazione") + ":", self.comboBox_frammentazione)

        self.comboBox_combustione = QComboBox()
        self.comboBox_combustione.setEditable(True)
        self.comboBox_combustione.addItem("")  # Empty default, thesaurus will populate
        form.addRow(self.tr("Tracce Combustione") + ":", self.comboBox_combustione)

        self.checkBox_combustione_altri = QCheckBox()
        form.addRow(self.tr("Combustione Altri Materiali US") + ":", self.checkBox_combustione_altri)

        self.comboBox_tipo_combustione = QComboBox()
        self.comboBox_tipo_combustione.setEditable(True)
        self.comboBox_tipo_combustione.addItem("")  # Empty default, thesaurus will populate
        form.addRow(self.tr("Tipo Combustione") + ":", self.comboBox_tipo_combustione)

        self.comboBox_segni_tafonomici = QComboBox()
        self.comboBox_segni_tafonomici.setEditable(True)
        self.comboBox_segni_tafonomici.addItem("")  # Empty default, thesaurus will populate
        form.addRow(self.tr("Segni Tafonomici") + ":", self.comboBox_segni_tafonomici)

        self.comboBox_caratterizzazione = QComboBox()
        self.comboBox_caratterizzazione.setEditable(True)
        self.comboBox_caratterizzazione.addItem("")  # Empty default, thesaurus will populate
        form.addRow(self.tr("Caratterizzazione") + ":", self.comboBox_caratterizzazione)

        self.comboBox_conservazione = QComboBox()
        self.comboBox_conservazione.setEditable(True)
        form.addRow(self.tr("Stato Conservazione") + ":", self.comboBox_conservazione)

        self.textEdit_alterazioni = QTextEdit()
        self.textEdit_alterazioni.setMaximumHeight(80)
        form.addRow(self.tr("Alterazioni Morfologiche") + ":", self.textEdit_alterazioni)

        layout.addLayout(form)
        layout.addStretch()

        return widget

    def create_tab_contestuali(self) -> QWidget:
        """Create the contextual data tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        form = QFormLayout()

        self.textEdit_note_terreno = QTextEdit()
        self.textEdit_note_terreno.setMaximumHeight(80)
        form.addRow(self.tr("Note Terreno Giacitura") + ":", self.textEdit_note_terreno)

        self.lineEdit_campionature = QLineEdit()
        form.addRow(self.tr("Campionature Effettuate") + ":", self.lineEdit_campionature)

        self.comboBox_affidabilita = QComboBox()
        self.comboBox_affidabilita.setEditable(True)
        form.addRow(self.tr("Affidabilità Stratigrafica") + ":", self.comboBox_affidabilita)

        self.lineEdit_classi_reperti = QLineEdit()
        form.addRow(self.tr("Classi Reperti Associazione") + ":", self.lineEdit_classi_reperti)

        self.textEdit_osservazioni = QTextEdit()
        self.textEdit_osservazioni.setMaximumHeight(100)
        form.addRow(self.tr("Osservazioni") + ":", self.textEdit_osservazioni)

        self.textEdit_interpretazione = QTextEdit()
        self.textEdit_interpretazione.setMaximumHeight(100)
        form.addRow(self.tr("Interpretazione") + ":", self.textEdit_interpretazione)

        layout.addLayout(form)
        layout.addStretch()

        return widget

    def set_sito(self):
        """Filter records by selected site."""
        conn = Connection()
        sito_set = conn.sito_set()
        sito_set_str = sito_set['sito_set']

        try:
            if sito_set_str:
                search_dict = {'sito': "'" + str(sito_set_str) + "'"}
                u = Utility()
                search_dict = u.remove_empty_items_fr_dict(search_dict)
                res = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
                self.DATA_LIST = list(res)
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0

                # Check if DATA_LIST is empty before accessing index 0
                if len(self.DATA_LIST) == 0:
                    # Set the comboBox to show the site even with no records
                    if hasattr(self, 'comboBox_sito'):
                        self.comboBox_sito.setEditText(sito_set_str)
                        self.setComboBoxEnable(["self.comboBox_sito"], "False")
                    if self.L == 'it':
                        QMessageBox.information(self, "Informazione",
                            f"Nessun record trovato per il sito '{sito_set_str}' in questa scheda.",
                            QMessageBox.StandardButton.Ok)
                    elif self.L == 'de':
                        QMessageBox.information(self, "Information",
                            f"Keine Datensätze für die Fundstelle '{sito_set_str}' in dieser Registerkarte gefunden.",
                            QMessageBox.StandardButton.Ok)
                    elif self.L == 'fr':
                        QMessageBox.information(self, "Information",
                            f"Aucun enregistrement trouvé pour le site '{sito_set_str}' dans cet onglet.",
                            QMessageBox.StandardButton.Ok)
                    elif self.L == 'es':
                        QMessageBox.information(self, "Información",
                            f"No se encontraron registros para el sitio '{sito_set_str}' en esta pestaña.",
                            QMessageBox.StandardButton.Ok)
                    else:
                        QMessageBox.information(self, "Information",
                            f"No records found for site '{sito_set_str}' in this tab.",
                            QMessageBox.StandardButton.Ok)
                    return

                self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                self.fill_fields()
                self.BROWSE_STATUS = "b"
                self.SORT_STATUS = "n"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                self.setComboBoxEnable(["self.comboBox_sito"], "False")
            else:
                pass  # No site filter set
        except Exception as e:
            if self.L == 'it':
                QMessageBox.warning(self, "Errore",
                    f"Errore durante il caricamento dei dati: {str(e)}",
                    QMessageBox.StandardButton.Ok)
            elif self.L == 'de':
                QMessageBox.warning(self, "Fehler",
                    f"Fehler beim Laden der Daten: {str(e)}",
                    QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.warning(self, "Error",
                    f"Error loading data: {str(e)}",
                    QMessageBox.StandardButton.Ok)

    def setComboBoxEnable(self, combo_box_list, enabled):
        """Enable/disable combo boxes."""
        for combo_str in combo_box_list:
            try:
                combo = eval(combo_str)
                if enabled == "True":
                    combo.setEnabled(True)
                else:
                    combo.setEnabled(False)
            except:
                pass

    def charge_list(self):
        """Load list values for combo boxes."""
        if not self.DB_MANAGER:
            return

        try:
            # Load sites
            sito_list = self.DB_MANAGER.query_distinct('SITE', ['sito'])
            if sito_list:
                self.comboBox_sito.clear()
                self.comboBox_sito.addItem("")
                for s in sito_list:
                    self.comboBox_sito.addItem(str(s.sito))
        except Exception as e:
            pass

        # Load US combo with all US records
        self.charge_us_combo()

        # Load thesaurus values for Fauna comboboxes
        self.charge_thesaurus_combos()

    def charge_thesaurus_combos(self):
        """Load thesaurus values for Fauna comboboxes"""
        # Determine language code for thesaurus queries
        # Database uses simple format: IT, EN, DE, etc.
        lang_mapping = {
            'it': "'IT'",
            'de': "'DE'",
            'en': "'EN'",
            'es': "'ES'",
            'fr': "'FR'",
            'ar': "'AR'",
            'ca': "'CA'"
        }
        lang = lang_mapping.get(self.L, "'EN'")

        print(f"[Fauna DEBUG] charge_combo_thesaurus: L={self.L}, lang={lang}")

        # Helper function to load thesaurus values
        def load_thesaurus(tipologia_sigla, use_sigla=False):
            search_dict = {
                'lingua': lang,
                'nome_tabella': "'fauna_table'",
                'tipologia_sigla': "'" + tipologia_sigla + "'"
            }
            try:
                print(f"[Fauna DEBUG] Loading thesaurus for {tipologia_sigla} with search_dict: {search_dict}")
                thesaurus_data = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
                print(f"[Fauna DEBUG] Thesaurus query returned {len(thesaurus_data) if thesaurus_data else 0} items")

                # If no results with language filter, try without language filter
                if not thesaurus_data:
                    print(f"[Fauna DEBUG] No results with language filter, trying without language...")
                    search_dict_no_lang = {
                        'nome_tabella': "'fauna_table'",
                        'tipologia_sigla': "'" + tipologia_sigla + "'"
                    }
                    thesaurus_data = self.DB_MANAGER.query_bool(search_dict_no_lang, 'PYARCHINIT_THESAURUS_SIGLE')
                    print(f"[Fauna DEBUG] Thesaurus query without lang returned {len(thesaurus_data) if thesaurus_data else 0} items")

                values = []
                for item in thesaurus_data:
                    if use_sigla:
                        val = item.sigla.strip() if item.sigla else ''
                    else:
                        val = item.sigla_estesa.strip() if item.sigla_estesa else ''
                    if val and val not in values:
                        values.append(val)
                values.sort()
                print(f"[Fauna DEBUG] Thesaurus values for {tipologia_sigla}: {values}")
                return values
            except Exception as e:
                # If thesaurus table doesn't exist or other error, return empty list
                print(f"[Fauna DEBUG] Thesaurus error for {tipologia_sigla}: {e}")
                import traceback
                traceback.print_exc()
                return []

        # 13.1 - Contesto
        if hasattr(self, 'comboBox_contesto'):
            contesto_vl = load_thesaurus('13.1')
            if contesto_vl:
                self.comboBox_contesto.clear()
                self.comboBox_contesto.addItem("")
                self.comboBox_contesto.addItems(contesto_vl)

        # 13.2 - Metodologia Recupero
        if hasattr(self, 'comboBox_metodologia'):
            metodologia_vl = load_thesaurus('13.2')
            if metodologia_vl:
                self.comboBox_metodologia.clear()
                self.comboBox_metodologia.addItem("")
                self.comboBox_metodologia.addItems(metodologia_vl)

        # 13.3 - Tipologia Accumulo
        if hasattr(self, 'comboBox_tipologia_accumulo'):
            accumulo_vl = load_thesaurus('13.3')
            if accumulo_vl:
                self.comboBox_tipologia_accumulo.clear()
                self.comboBox_tipologia_accumulo.addItem("")
                self.comboBox_tipologia_accumulo.addItems(accumulo_vl)

        # 13.4 - Deposizione
        if hasattr(self, 'comboBox_deposizione'):
            deposizione_vl = load_thesaurus('13.4')
            if deposizione_vl:
                self.comboBox_deposizione.clear()
                self.comboBox_deposizione.addItem("")
                self.comboBox_deposizione.addItems(deposizione_vl)

        # 13.5 - Stato Frammentazione
        if hasattr(self, 'comboBox_frammentazione'):
            framm_vl = load_thesaurus('13.5')
            if framm_vl:
                self.comboBox_frammentazione.clear()
                self.comboBox_frammentazione.addItem("")
                self.comboBox_frammentazione.addItems(framm_vl)

        # 13.6 - Stato Conservazione
        if hasattr(self, 'comboBox_conservazione'):
            conserv_vl = load_thesaurus('13.6')
            if conserv_vl:
                self.comboBox_conservazione.clear()
                self.comboBox_conservazione.addItem("")
                self.comboBox_conservazione.addItems(conserv_vl)

        # 13.7 - Affidabilità Stratigrafica
        if hasattr(self, 'comboBox_affidabilita'):
            affid_vl = load_thesaurus('13.7')
            if affid_vl:
                self.comboBox_affidabilita.clear()
                self.comboBox_affidabilita.addItem("")
                self.comboBox_affidabilita.addItems(affid_vl)

        # 13.8 - Tracce Combustione
        if hasattr(self, 'comboBox_combustione'):
            comb_vl = load_thesaurus('13.8')
            if comb_vl:
                self.comboBox_combustione.clear()
                self.comboBox_combustione.addItem("")
                self.comboBox_combustione.addItems(comb_vl)

        # 13.9 - Tipo Combustione
        if hasattr(self, 'comboBox_tipo_combustione'):
            tipo_comb_vl = load_thesaurus('13.9')
            if tipo_comb_vl:
                self.comboBox_tipo_combustione.clear()
                self.comboBox_tipo_combustione.addItem("")
                self.comboBox_tipo_combustione.addItems(tipo_comb_vl)

        # 13.10 - Resti Connessione Anatomica
        if hasattr(self, 'comboBox_connessione'):
            conn_vl = load_thesaurus('13.10')
            if conn_vl:
                self.comboBox_connessione.clear()
                self.comboBox_connessione.addItem("")
                self.comboBox_connessione.addItems(conn_vl)

        # 13.11 - Specie (for tableWidget_specie_psi)
        self.thesaurus_specie = load_thesaurus('13.11') or []

        # 13.12 - Parti Scheletriche / PSI (for tableWidget_specie_psi)
        self.thesaurus_psi = load_thesaurus('13.12') or []

        # 13.13 - Elemento Anatomico (for tableWidget_misure)
        self.thesaurus_elemento = load_thesaurus('13.13') or []

        # 13.14 - Segni Tafonomici
        segni_taf_vl = load_thesaurus('13.14')
        if segni_taf_vl and hasattr(self, 'comboBox_segni_tafonomici'):
            self.comboBox_segni_tafonomici.clear()
            self.comboBox_segni_tafonomici.addItem("")
            self.comboBox_segni_tafonomici.addItems(segni_taf_vl)

        # 13.15 - Caratterizzazione Segni Tafonomici
        caratt_vl = load_thesaurus('13.15')
        if caratt_vl and hasattr(self, 'comboBox_caratterizzazione'):
            self.comboBox_caratterizzazione.clear()
            self.comboBox_caratterizzazione.addItem("")
            self.comboBox_caratterizzazione.addItems(caratt_vl)

        # 13.16 - Numero Stimato Resti (optional thesaurus for suggestions)
        num_stimato_vl = load_thesaurus('13.16')
        if num_stimato_vl and hasattr(self, 'lineEdit_num_stimato'):
            # Convert lineEdit to comboBox for thesaurus support
            pass  # lineEdit_num_stimato remains a free text field

    def charge_us_combo(self, sito=None, area=None):
        """Load US data into comboBox_us_select with format 'sito - area - us'"""
        if not self.DB_MANAGER:
            return

        try:
            self.comboBox_us_select.blockSignals(True)
            self.comboBox_us_select.clear()
            self.comboBox_us_select.addItem("", None)  # Empty option

            # Build search conditions
            search_dict = {}
            if sito:
                search_dict['sito'] = "'" + sito + "'"
            if area:
                search_dict['area'] = "'" + area + "'"

            if search_dict:
                us_list = self.DB_MANAGER.query_bool(search_dict, 'US')
            else:
                us_list = self.DB_MANAGER.query('US')

            if us_list:
                for us in us_list:
                    # Format: "sito - area - us"
                    display_text = f"{us.sito} - {us.area} - US {us.us}"
                    # Store id_us as data
                    self.comboBox_us_select.addItem(display_text, us.id_us)

            self.comboBox_us_select.blockSignals(False)
        except Exception as e:
            self.comboBox_us_select.blockSignals(False)

    def on_us_selected(self, index):
        """Handle US selection - auto-populate sito, area, saggio, datazione fields"""
        if not self.DB_MANAGER:
            return

        id_us = self.comboBox_us_select.currentData()

        if id_us:
            try:
                # Query us_table for the selected US
                search_dict = {'id_us': id_us}
                us_data = self.DB_MANAGER.query_bool(search_dict, 'US')

                if us_data and len(us_data) > 0:
                    us = us_data[0]
                    # Block signals to avoid triggering cascading updates
                    self.comboBox_sito.blockSignals(True)
                    self.comboBox_area.blockSignals(True)

                    self.comboBox_sito.setEditText(str(us.sito) if us.sito else "")
                    self.comboBox_area.setEditText(str(us.area) if us.area else "")
                    self.lineEdit_saggio.setText(str(us.saggio) if us.saggio else "")
                    self.lineEdit_us.setText(str(us.us) if us.us else "")
                    self.lineEdit_datazione_us.setText(str(us.datazione) if us.datazione else "")

                    self.comboBox_sito.blockSignals(False)
                    self.comboBox_area.blockSignals(False)
            except Exception as e:
                pass
        else:
            # Clear fields if no US selected
            self.lineEdit_saggio.clear()
            self.lineEdit_us.clear()
            self.lineEdit_datazione_us.clear()

    def on_sito_changed(self, index):
        """Handle site selection change - update area and US combos"""
        if not self.DB_MANAGER:
            return

        sito = self.comboBox_sito.currentText()

        # Update area combo
        try:
            self.comboBox_area.blockSignals(True)
            self.comboBox_area.clear()
            self.comboBox_area.addItem("")

            if sito:
                # Get distinct areas for this site
                search_dict = {'sito': "'" + sito + "'"}
                us_list = self.DB_MANAGER.query_bool(search_dict, 'US')
                if us_list:
                    areas = sorted(set(str(us.area) for us in us_list if us.area))
                    self.comboBox_area.addItems(areas)

            self.comboBox_area.blockSignals(False)
        except Exception as e:
            self.comboBox_area.blockSignals(False)

        # Update US combo
        self.charge_us_combo(sito if sito else None)

    def on_area_changed(self, index):
        """Handle area selection change - update US combo"""
        if not self.DB_MANAGER:
            return

        sito = self.comboBox_sito.currentText()
        area = self.comboBox_area.currentText()

        # Update US combo
        self.charge_us_combo(
            sito if sito else None,
            area if area else None
        )

    def on_pushButton_new_search_pressed(self):
        """Start a new search - clear form and set to search mode"""
        if self.BROWSE_STATUS != "f":
            self.BROWSE_STATUS = "f"
            self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
            self.empty_fields()
            self.setComboBoxEnable(["self.comboBox_sito"], "True")
            self.setComboBoxEnable(["self.comboBox_area"], "True")
            self.setComboBoxEnable(["self.comboBox_us_select"], "True")

            if self.L == 'it':
                QMessageBox.information(self, "Info", "Compila i campi per la ricerca e clicca su 'Esegui ricerca'",
                                       QMessageBox.StandardButton.Ok)
            elif self.L == 'de':
                QMessageBox.information(self, "Info", "Füllen Sie die Felder für die Suche aus und klicken Sie auf 'Suche ausführen'",
                                       QMessageBox.StandardButton.Ok)
            elif self.L == 'fr':
                QMessageBox.information(self, "Info", "Remplissez les champs de recherche et cliquez sur 'Exécuter la recherche'",
                                       QMessageBox.StandardButton.Ok)
            elif self.L == 'es':
                QMessageBox.information(self, "Info", "Complete los campos de búsqueda y haga clic en 'Ejecutar búsqueda'",
                                       QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.information(self, "Info", "Fill in the search fields and click 'Execute search'",
                                       QMessageBox.StandardButton.Ok)

    def on_pushButton_search_go_pressed(self):
        """Execute the search with current form values as filters"""
        if self.BROWSE_STATUS != "f":
            if self.L == 'it':
                QMessageBox.warning(self, "Attenzione", "Per eseguire una ricerca clicca prima su 'Nuova ricerca'",
                                   QMessageBox.StandardButton.Ok)
            elif self.L == 'de':
                QMessageBox.warning(self, "Achtung", "Um eine Suche durchzuführen, klicken Sie zuerst auf 'Neue Suche'",
                                   QMessageBox.StandardButton.Ok)
            elif self.L == 'fr':
                QMessageBox.warning(self, "Attention", "Pour effectuer une recherche, cliquez d'abord sur 'Nouvelle recherche'",
                                   QMessageBox.StandardButton.Ok)
            elif self.L == 'es':
                QMessageBox.warning(self, "Atención", "Para realizar una búsqueda, haga clic primero en 'Nueva búsqueda'",
                                   QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.warning(self, "Warning", "To perform a search, first click on 'New search'",
                                   QMessageBox.StandardButton.Ok)
            return

        # Build search dictionary from form fields
        search_dict = {}

        if self.comboBox_sito.currentText():
            search_dict['sito'] = "'" + self.comboBox_sito.currentText() + "'"

        if self.comboBox_area.currentText():
            search_dict['area'] = "'" + self.comboBox_area.currentText() + "'"

        if self.lineEdit_saggio.text():
            search_dict['saggio'] = "'" + self.lineEdit_saggio.text() + "'"

        if self.lineEdit_us.text():
            search_dict['us'] = "'" + self.lineEdit_us.text() + "'"

        if self.comboBox_contesto.currentText():
            search_dict['contesto'] = "'" + self.comboBox_contesto.currentText() + "'"

        # Note: specie search is now done via tableWidget_specie_psi (JSON field)
        # Search by specie is available in the specie_psi JSON field

        if self.comboBox_metodologia.currentText():
            search_dict['metodologia_recupero'] = "'" + self.comboBox_metodologia.currentText() + "'"

        if self.comboBox_connessione.currentText():
            search_dict['resti_connessione_anatomica'] = "'" + self.comboBox_connessione.currentText() + "'"

        if self.comboBox_deposizione.currentText():
            search_dict['deposizione'] = "'" + self.comboBox_deposizione.currentText() + "'"

        if self.comboBox_frammentazione.currentText():
            search_dict['stato_frammentazione'] = "'" + self.comboBox_frammentazione.currentText() + "'"

        if self.comboBox_conservazione.currentText():
            search_dict['stato_conservazione'] = "'" + self.comboBox_conservazione.currentText() + "'"

        if self.comboBox_combustione.currentText():
            search_dict['tracce_combustione'] = "'" + self.comboBox_combustione.currentText() + "'"

        if self.comboBox_affidabilita.currentText():
            search_dict['affidabilita_stratigrafica'] = "'" + self.comboBox_affidabilita.currentText() + "'"

        # Execute search
        try:
            if search_dict:
                self.DATA_LIST = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
            else:
                self.DATA_LIST = self.DB_MANAGER.query(self.MAPPER_TABLE_CLASS)

            if self.DATA_LIST:
                self.REC_TOT = len(self.DATA_LIST)
                self.REC_CORR = 0
                self.BROWSE_STATUS = "b"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
                self.fill_fields(self.REC_CORR)

                if self.L == 'it':
                    QMessageBox.information(self, "Risultati", f"Trovati {self.REC_TOT} record",
                                           QMessageBox.StandardButton.Ok)
                elif self.L == 'de':
                    QMessageBox.information(self, "Ergebnisse", f"{self.REC_TOT} Datensätze gefunden",
                                           QMessageBox.StandardButton.Ok)
                elif self.L == 'fr':
                    QMessageBox.information(self, "Résultats", f"{self.REC_TOT} enregistrements trouvés",
                                           QMessageBox.StandardButton.Ok)
                elif self.L == 'es':
                    QMessageBox.information(self, "Resultados", f"Se encontraron {self.REC_TOT} registros",
                                           QMessageBox.StandardButton.Ok)
                else:
                    QMessageBox.information(self, "Results", f"Found {self.REC_TOT} records",
                                           QMessageBox.StandardButton.Ok)
            else:
                self.REC_TOT = 0
                self.REC_CORR = 0
                self.BROWSE_STATUS = "b"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.set_rec_counter(0, 0)

                if self.L == 'it':
                    QMessageBox.information(self, "Risultati", "Nessun record trovato",
                                           QMessageBox.StandardButton.Ok)
                elif self.L == 'de':
                    QMessageBox.information(self, "Ergebnisse", "Keine Datensätze gefunden",
                                           QMessageBox.StandardButton.Ok)
                elif self.L == 'fr':
                    QMessageBox.information(self, "Résultats", "Aucun enregistrement trouvé",
                                           QMessageBox.StandardButton.Ok)
                elif self.L == 'es':
                    QMessageBox.information(self, "Resultados", "No se encontraron registros",
                                           QMessageBox.StandardButton.Ok)
                else:
                    QMessageBox.information(self, "Results", "No records found",
                                           QMessageBox.StandardButton.Ok)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Search error: {str(e)}", QMessageBox.StandardButton.Ok)

    def fill_fields(self, n=0):
        """Fill form fields with current record data."""
        if not self.DATA_LIST or n >= len(self.DATA_LIST):
            return

        try:
            rec = self.DATA_LIST[n]

            self.lineEdit_id_fauna.setText(str(rec.id_fauna) if rec.id_fauna else "")
            self.comboBox_sito.setEditText(str(rec.sito) if rec.sito else "")
            self.comboBox_area.setEditText(str(rec.area) if rec.area else "")
            self.lineEdit_saggio.setText(str(rec.saggio) if rec.saggio else "")
            self.lineEdit_us.setText(str(rec.us) if rec.us else "")
            self.lineEdit_datazione_us.setText(str(rec.datazione_us) if rec.datazione_us else "")
            self.lineEdit_responsabile.setText(str(rec.responsabile_scheda) if rec.responsabile_scheda else "")

            if rec.data_compilazione:
                try:
                    date_val = QDate.fromString(str(rec.data_compilazione), "yyyy-MM-dd")
                    self.dateEdit_compilazione.setDate(date_val)
                except:
                    pass

            self.lineEdit_doc_foto.setText(str(rec.documentazione_fotografica) if rec.documentazione_fotografica else "")
            self.comboBox_metodologia.setEditText(str(rec.metodologia_recupero) if rec.metodologia_recupero else "")
            self.comboBox_contesto.setEditText(str(rec.contesto) if rec.contesto else "")
            self.textEdit_desc_contesto.setText(str(rec.descrizione_contesto) if rec.descrizione_contesto else "")

            self.comboBox_connessione.setEditText(str(rec.resti_connessione_anatomica) if rec.resti_connessione_anatomica else "")
            self.comboBox_tipologia_accumulo.setEditText(str(rec.tipologia_accumulo) if rec.tipologia_accumulo else "")
            self.comboBox_deposizione.setEditText(str(rec.deposizione) if rec.deposizione else "")
            self.lineEdit_num_stimato.setText(str(rec.numero_stimato_resti) if rec.numero_stimato_resti else "")
            self.spinBox_nmi.setValue(int(rec.numero_minimo_individui) if rec.numero_minimo_individui else 0)

            # Populate tableWidget_specie_psi from JSON
            if hasattr(self, 'tableWidget_specie_psi'):
                specie_psi_json = getattr(rec, 'specie_psi', '') or ''
                if specie_psi_json and str(specie_psi_json).strip():
                    try:
                        specie_psi_data = json.loads(specie_psi_json)
                        self.set_specie_psi_data(specie_psi_data)
                    except:
                        self.tableWidget_specie_psi.setRowCount(0)
                else:
                    self.tableWidget_specie_psi.setRowCount(0)

            # Populate tableWidget_misure from JSON
            if hasattr(self, 'tableWidget_misure'):
                misure_ossa_json = getattr(rec, 'misure_ossa', '') or ''
                if misure_ossa_json and str(misure_ossa_json).strip():
                    try:
                        misure_ossa_data = json.loads(misure_ossa_json)
                        self.set_misure_data(misure_ossa_data)
                    except:
                        self.tableWidget_misure.setRowCount(0)
                else:
                    self.tableWidget_misure.setRowCount(0)

            self.comboBox_frammentazione.setEditText(str(rec.stato_frammentazione) if rec.stato_frammentazione else "")
            self.comboBox_combustione.setEditText(str(rec.tracce_combustione) if rec.tracce_combustione else "")
            self.checkBox_combustione_altri.setChecked(bool(rec.combustione_altri_materiali_us) if rec.combustione_altri_materiali_us else False)
            self.comboBox_tipo_combustione.setEditText(str(rec.tipo_combustione) if rec.tipo_combustione else "")
            self.comboBox_segni_tafonomici.setEditText(str(rec.segni_tafonomici_evidenti) if rec.segni_tafonomici_evidenti else "")
            self.comboBox_caratterizzazione.setEditText(str(rec.caratterizzazione_segni_tafonomici) if rec.caratterizzazione_segni_tafonomici else "")
            self.comboBox_conservazione.setEditText(str(rec.stato_conservazione) if rec.stato_conservazione else "")
            self.textEdit_alterazioni.setText(str(rec.alterazioni_morfologiche) if rec.alterazioni_morfologiche else "")

            self.textEdit_note_terreno.setText(str(rec.note_terreno_giacitura) if rec.note_terreno_giacitura else "")
            self.lineEdit_campionature.setText(str(rec.campionature_effettuate) if rec.campionature_effettuate else "")
            self.comboBox_affidabilita.setEditText(str(rec.affidabilita_stratigrafica) if rec.affidabilita_stratigrafica else "")
            self.lineEdit_classi_reperti.setText(str(rec.classi_reperti_associazione) if rec.classi_reperti_associazione else "")
            self.textEdit_osservazioni.setText(str(rec.osservazioni) if rec.osservazioni else "")
            self.textEdit_interpretazione.setText(str(rec.interpretazione) if rec.interpretazione else "")

        except Exception as e:
            pass

    def set_rec_counter(self, t, c):
        """Update record counter display.

        Args:
            t: Total number of records
            c: Current record number (1-based for display)

        Note: REC_CORR is 0-based index, c is 1-based display value.
        This method only updates display labels, not REC_CORR.
        """
        self.REC_TOT = t
        # Don't modify REC_CORR here - it's a 0-based index
        # c is the 1-based display value
        self.label_rec_tot.setText(str(self.REC_TOT))
        self.label_rec_corrente.setText(str(c))

    # ========== GESTIONE TABELLE SPECIE/PSI E MISURE ==========

    def add_specie_psi_row(self):
        """Aggiunge una riga alla tabella Specie/PSI"""
        row_position = self.tableWidget_specie_psi.rowCount()
        self.tableWidget_specie_psi.insertRow(row_position)

        # Combo Specie (with thesaurus values from 13.11)
        combo_specie = QComboBox()
        combo_specie.setEditable(True)
        combo_specie.addItem("")
        if hasattr(self, 'thesaurus_specie') and self.thesaurus_specie:
            combo_specie.addItems(self.thesaurus_specie)
        self.tableWidget_specie_psi.setCellWidget(row_position, 0, combo_specie)

        # Combo PSI (with thesaurus values from 13.12)
        combo_psi = QComboBox()
        combo_psi.setEditable(True)
        combo_psi.addItem("")
        if hasattr(self, 'thesaurus_psi') and self.thesaurus_psi:
            combo_psi.addItems(self.thesaurus_psi)
        self.tableWidget_specie_psi.setCellWidget(row_position, 1, combo_psi)

    def remove_specie_psi_row(self):
        """Rimuove la riga selezionata dalla tabella Specie/PSI"""
        current_row = self.tableWidget_specie_psi.currentRow()
        if current_row >= 0:
            self.tableWidget_specie_psi.removeRow(current_row)

    def get_specie_psi_data(self) -> list:
        """Estrae i dati dalla tabella Specie/PSI come lista di liste"""
        data = []
        for row in range(self.tableWidget_specie_psi.rowCount()):
            specie_widget = self.tableWidget_specie_psi.cellWidget(row, 0)
            psi_widget = self.tableWidget_specie_psi.cellWidget(row, 1)

            if specie_widget and psi_widget:
                specie = specie_widget.currentText()
                psi = psi_widget.currentText()
                if specie or psi:  # Include solo righe non vuote
                    data.append([specie, psi])
        return data

    def set_specie_psi_data(self, data: list):
        """Popola la tabella Specie/PSI da una lista di liste"""
        # Svuota la tabella
        self.tableWidget_specie_psi.setRowCount(0)

        # Aggiungi righe con i dati
        for row_data in data:
            if len(row_data) >= 2:
                row_position = self.tableWidget_specie_psi.rowCount()
                self.tableWidget_specie_psi.insertRow(row_position)

                # Combo Specie (with thesaurus values from 13.11)
                combo_specie = QComboBox()
                combo_specie.setEditable(True)
                combo_specie.addItem("")
                if hasattr(self, 'thesaurus_specie') and self.thesaurus_specie:
                    combo_specie.addItems(self.thesaurus_specie)
                combo_specie.setCurrentText(str(row_data[0]) if row_data[0] else "")
                self.tableWidget_specie_psi.setCellWidget(row_position, 0, combo_specie)

                # Combo PSI (with thesaurus values from 13.12)
                combo_psi = QComboBox()
                combo_psi.setEditable(True)
                combo_psi.addItem("")
                if hasattr(self, 'thesaurus_psi') and self.thesaurus_psi:
                    combo_psi.addItems(self.thesaurus_psi)
                combo_psi.setCurrentText(str(row_data[1]) if row_data[1] else "")
                self.tableWidget_specie_psi.setCellWidget(row_position, 1, combo_psi)

    def add_misura_row(self):
        """Aggiunge una riga alla tabella Misure"""
        row_position = self.tableWidget_misure.rowCount()
        self.tableWidget_misure.insertRow(row_position)

        # Combo Elemento Anatomico (with thesaurus values from 13.13)
        combo_elemento = QComboBox()
        combo_elemento.setEditable(True)
        combo_elemento.addItem("")
        if hasattr(self, 'thesaurus_elemento') and self.thesaurus_elemento:
            combo_elemento.addItems(self.thesaurus_elemento)
        self.tableWidget_misure.setCellWidget(row_position, 0, combo_elemento)

        # Combo Specie (with thesaurus values from 13.11)
        combo_specie = QComboBox()
        combo_specie.setEditable(True)
        combo_specie.addItem("")
        if hasattr(self, 'thesaurus_specie') and self.thesaurus_specie:
            combo_specie.addItems(self.thesaurus_specie)
        self.tableWidget_misure.setCellWidget(row_position, 1, combo_specie)

        # Line edit per misure (GL, GB, Bp, Bd)
        for col in range(2, 6):
            line_edit = QLineEdit()
            line_edit.setPlaceholderText("0.00")
            self.tableWidget_misure.setCellWidget(row_position, col, line_edit)

    def remove_misura_row(self):
        """Rimuove la riga selezionata dalla tabella Misure"""
        current_row = self.tableWidget_misure.currentRow()
        if current_row >= 0:
            self.tableWidget_misure.removeRow(current_row)

    def get_misure_data(self) -> list:
        """Estrae i dati dalla tabella Misure come lista di liste"""
        data = []
        for row in range(self.tableWidget_misure.rowCount()):
            elemento_widget = self.tableWidget_misure.cellWidget(row, 0)
            specie_widget = self.tableWidget_misure.cellWidget(row, 1)

            if elemento_widget and specie_widget:
                elemento = elemento_widget.currentText()
                specie = specie_widget.currentText()

                # Leggi misure (GL, GB, Bp, Bd)
                misure = []
                for col in range(2, 6):
                    widget = self.tableWidget_misure.cellWidget(row, col)
                    if widget:
                        text = widget.text().strip()
                        misure.append(text if text else "")
                    else:
                        misure.append("")

                # Include solo righe con almeno elemento o specie
                if elemento or specie or any(misure):
                    data.append([elemento, specie] + misure)
        return data

    def set_misure_data(self, data: list):
        """Popola la tabella Misure da una lista di liste"""
        # Svuota la tabella
        self.tableWidget_misure.setRowCount(0)

        # Aggiungi righe con i dati
        for row_data in data:
            if len(row_data) >= 6:
                row_position = self.tableWidget_misure.rowCount()
                self.tableWidget_misure.insertRow(row_position)

                # Combo Elemento Anatomico (with thesaurus values from 13.13)
                combo_elemento = QComboBox()
                combo_elemento.setEditable(True)
                combo_elemento.addItem("")
                if hasattr(self, 'thesaurus_elemento') and self.thesaurus_elemento:
                    combo_elemento.addItems(self.thesaurus_elemento)
                combo_elemento.setCurrentText(str(row_data[0]) if row_data[0] else "")
                self.tableWidget_misure.setCellWidget(row_position, 0, combo_elemento)

                # Combo Specie (with thesaurus values from 13.11)
                combo_specie = QComboBox()
                combo_specie.setEditable(True)
                combo_specie.addItem("")
                if hasattr(self, 'thesaurus_specie') and self.thesaurus_specie:
                    combo_specie.addItems(self.thesaurus_specie)
                combo_specie.setCurrentText(str(row_data[1]) if row_data[1] else "")
                self.tableWidget_misure.setCellWidget(row_position, 1, combo_specie)

                # Line edit per misure (GL, GB, Bp, Bd)
                for col in range(2, 6):
                    line_edit = QLineEdit()
                    line_edit.setPlaceholderText("0.00")
                    line_edit.setText(str(row_data[col]) if row_data[col] else "")
                    self.tableWidget_misure.setCellWidget(row_position, col, line_edit)

    def empty_fields(self):
        """Clear all form fields."""
        self.lineEdit_id_fauna.clear()
        if hasattr(self, 'comboBox_us_select'):
            self.comboBox_us_select.setCurrentIndex(0)
        self.comboBox_sito.setEditText("")
        self.comboBox_area.setEditText("")
        self.lineEdit_saggio.clear()
        self.lineEdit_us.clear()
        self.lineEdit_datazione_us.clear()
        self.lineEdit_responsabile.clear()
        self.dateEdit_compilazione.setDate(QDate.currentDate())
        self.lineEdit_doc_foto.clear()
        self.comboBox_metodologia.setEditText("")
        self.comboBox_contesto.setEditText("")
        self.textEdit_desc_contesto.clear()

        self.comboBox_connessione.setEditText("")
        self.comboBox_tipologia_accumulo.setEditText("")
        self.comboBox_deposizione.setEditText("")
        self.lineEdit_num_stimato.clear()
        self.spinBox_nmi.setValue(0)

        # Clear tableWidgets for specie/PSI and misure
        if hasattr(self, 'tableWidget_specie_psi'):
            self.tableWidget_specie_psi.setRowCount(0)
        if hasattr(self, 'tableWidget_misure'):
            self.tableWidget_misure.setRowCount(0)

        self.comboBox_frammentazione.setEditText("")
        self.comboBox_combustione.setEditText("")
        self.checkBox_combustione_altri.setChecked(False)
        self.comboBox_tipo_combustione.setEditText("")
        self.comboBox_segni_tafonomici.setEditText("")
        self.comboBox_caratterizzazione.setEditText("")
        self.comboBox_conservazione.setEditText("")
        self.textEdit_alterazioni.clear()

        self.textEdit_note_terreno.clear()
        self.lineEdit_campionature.clear()
        self.comboBox_affidabilita.setEditText("")
        self.lineEdit_classi_reperti.clear()
        self.textEdit_osservazioni.clear()
        self.textEdit_interpretazione.clear()

    # Navigation handlers
    def on_pushButton_first_rec_pressed(self):
        if self.DATA_LIST:
            self.REC_CORR = 0
            self.fill_fields(self.REC_CORR)
            self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)

    def on_pushButton_prev_rec_pressed(self):
        if self.DATA_LIST and self.REC_CORR > 0:
            self.REC_CORR -= 1
            self.fill_fields(self.REC_CORR)
            self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)

    def on_pushButton_next_rec_pressed(self):
        if self.DATA_LIST and self.REC_CORR < len(self.DATA_LIST) - 1:
            self.REC_CORR += 1
            self.fill_fields(self.REC_CORR)
            self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)

    def on_pushButton_last_rec_pressed(self):
        if self.DATA_LIST:
            self.REC_CORR = len(self.DATA_LIST) - 1
            self.fill_fields(self.REC_CORR)
            self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)

    def on_pushButton_new_rec_pressed(self):
        self.BROWSE_STATUS = "n"
        self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
        self.empty_fields()

    def on_pushButton_save_pressed(self):
        """Save current record."""
        if not self.DB_MANAGER:
            if self.L == 'it':
                QMessageBox.warning(self, "Errore", "Database non connesso")
            elif self.L == 'de':
                QMessageBox.warning(self, "Fehler", "Datenbankverbindung nicht vorhanden")
            elif self.L == 'fr':
                QMessageBox.warning(self, "Erreur", "Base de données non connectée")
            elif self.L == 'es':
                QMessageBox.warning(self, "Error", "Base de datos no conectada")
            else:
                QMessageBox.warning(self, "Error", "Database not connected")
            return

        if self.BROWSE_STATUS == "b":
            # Update existing record
            if self.data_error_check() == 0:
                if self.records_equal_check() == 1:
                    if self.L == 'it':
                        self.update_if(QMessageBox.warning(self, 'Errore',
                            "Il record è stato modificato. Vuoi salvare le modifiche?",
                            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))
                    elif self.L == 'de':
                        self.update_if(QMessageBox.warning(self, 'Fehler',
                            "Der Datensatz wurde geändert. Möchten Sie die Änderungen speichern?",
                            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))
                    elif self.L == 'fr':
                        self.update_if(QMessageBox.warning(self, 'Erreur',
                            "L'enregistrement a été modifié. Voulez-vous enregistrer les modifications?",
                            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))
                    elif self.L == 'es':
                        self.update_if(QMessageBox.warning(self, 'Error',
                            "El registro ha sido modificado. ¿Desea guardar los cambios?",
                            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))
                    else:
                        self.update_if(QMessageBox.warning(self, 'Error',
                            "The record has been modified. Do you want to save the changes?",
                            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))
                    self.SORT_STATUS = "n"
                    self.fill_fields(self.REC_CORR)
                else:
                    if self.L == 'it':
                        QMessageBox.warning(self, "ATTENZIONE", "Non è stata realizzata alcuna modifica.",
                                          QMessageBox.StandardButton.Ok)
                    elif self.L == 'de':
                        QMessageBox.warning(self, "ACHTUNG", "Es wurden keine Änderungen vorgenommen.",
                                          QMessageBox.StandardButton.Ok)
                    elif self.L == 'fr':
                        QMessageBox.warning(self, "ATTENTION", "Aucune modification n'a été effectuée.",
                                          QMessageBox.StandardButton.Ok)
                    elif self.L == 'es':
                        QMessageBox.warning(self, "ATENCIÓN", "No se ha realizado ninguna modificación.",
                                          QMessageBox.StandardButton.Ok)
                    else:
                        QMessageBox.warning(self, "Warning", "No changes have been made.",
                                          QMessageBox.StandardButton.Ok)
        else:
            # Insert new record
            if self.data_error_check() == 0:
                test_insert = self.insert_new_rec()
                if test_insert == 1:
                    self.empty_fields()
                    self.SORT_STATUS = "n"
                    self.charge_records()
                    self.charge_list()
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), len(self.DATA_LIST) - 1
                    self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
                    self.fill_fields(self.REC_CORR)

    def on_pushButton_delete_pressed(self):
        """Delete current record."""
        if not self.DB_MANAGER:
            if self.L == 'it':
                QMessageBox.warning(self, "Errore", "Database non connesso")
            elif self.L == 'de':
                QMessageBox.warning(self, "Fehler", "Datenbankverbindung nicht vorhanden")
            elif self.L == 'fr':
                QMessageBox.warning(self, "Erreur", "Base de données non connectée")
            elif self.L == 'es':
                QMessageBox.warning(self, "Error", "Base de datos no conectada")
            else:
                QMessageBox.warning(self, "Error", "Database not connected")
            return

        if not self.DATA_LIST:
            if self.L == 'it':
                QMessageBox.warning(self, "Attenzione", "Nessun record da eliminare")
            elif self.L == 'de':
                QMessageBox.warning(self, "Achtung", "Kein Datensatz zum Löschen")
            elif self.L == 'fr':
                QMessageBox.warning(self, "Attention", "Aucun enregistrement à supprimer")
            elif self.L == 'es':
                QMessageBox.warning(self, "Atención", "No hay registro para eliminar")
            else:
                QMessageBox.warning(self, "Warning", "No record to delete")
            return

        if self.L == 'it':
            msg = "Vuoi veramente eliminare il record?"
            title = "Conferma eliminazione"
        elif self.L == 'de':
            msg = "Möchten Sie den Datensatz wirklich löschen?"
            title = "Löschbestätigung"
        elif self.L == 'fr':
            msg = "Voulez-vous vraiment supprimer cet enregistrement?"
            title = "Confirmer la suppression"
        elif self.L == 'es':
            msg = "¿Realmente desea eliminar este registro?"
            title = "Confirmar eliminación"
        else:
            msg = "Do you really want to delete this record?"
            title = "Confirm deletion"

        reply = QMessageBox.question(self, title, msg,
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            try:
                id_to_delete = int(self.DATA_LIST[self.REC_CORR].id_fauna)
                self.DB_MANAGER.delete_one_record(self.TABLE_NAME, self.ID_TABLE, id_to_delete)

                if self.L == 'it':
                    QMessageBox.information(self, "Successo", "Record eliminato correttamente")
                elif self.L == 'de':
                    QMessageBox.information(self, "Erfolg", "Datensatz erfolgreich gelöscht")
                elif self.L == 'fr':
                    QMessageBox.information(self, "Succès", "Enregistrement supprimé avec succès")
                elif self.L == 'es':
                    QMessageBox.information(self, "Éxito", "Registro eliminado correctamente")
                else:
                    QMessageBox.information(self, "Success", "Record deleted successfully")

                # Reload records
                self.charge_records()
                self.charge_list()

                if self.DATA_LIST:
                    self.REC_TOT = len(self.DATA_LIST)
                    if self.REC_CORR >= self.REC_TOT:
                        self.REC_CORR = self.REC_TOT - 1
                    self.fill_fields(self.REC_CORR)
                    self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
                else:
                    self.REC_TOT = 0
                    self.REC_CORR = 0
                    self.empty_fields()
                    self.set_rec_counter(0, 0)

            except Exception as e:
                if self.L == 'it':
                    QMessageBox.critical(self, "Errore", f"Errore durante l'eliminazione: {str(e)}")
                elif self.L == 'de':
                    QMessageBox.critical(self, "Fehler", f"Fehler beim Löschen: {str(e)}")
                elif self.L == 'fr':
                    QMessageBox.critical(self, "Erreur", f"Erreur lors de la suppression: {str(e)}")
                elif self.L == 'es':
                    QMessageBox.critical(self, "Error", f"Error durante la eliminación: {str(e)}")
                else:
                    QMessageBox.critical(self, "Error", f"Error during deletion: {str(e)}")

    def on_pushButton_view_all_pressed(self):
        """Load all records."""
        if not self.DB_MANAGER:
            if self.L == 'it':
                QMessageBox.warning(self, "Errore", "Database non connesso")
            elif self.L == 'de':
                QMessageBox.warning(self, "Fehler", "Datenbankverbindung nicht vorhanden")
            elif self.L == 'fr':
                QMessageBox.warning(self, "Erreur", "Base de données non connectée")
            elif self.L == 'es':
                QMessageBox.warning(self, "Error", "Base de datos no conectada")
            else:
                QMessageBox.warning(self, "Error", "Database not connected")
            return

        try:
            self.DATA_LIST = self.DB_MANAGER.query(self.MAPPER_TABLE_CLASS)
            if self.DATA_LIST:
                self.REC_TOT = len(self.DATA_LIST)
                self.REC_CORR = 0
                self.fill_fields(0)
                self.set_rec_counter(self.REC_TOT, 1)
                self.BROWSE_STATUS = "b"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
            else:
                if self.L == 'it':
                    QMessageBox.information(self, "Info", "Nessun record trovato")
                elif self.L == 'de':
                    QMessageBox.information(self, "Info", "Keine Datensätze gefunden")
                elif self.L == 'fr':
                    QMessageBox.information(self, "Info", "Aucun enregistrement trouvé")
                elif self.L == 'es':
                    QMessageBox.information(self, "Info", "No se encontraron registros")
                else:
                    QMessageBox.information(self, "Info", "No records found")
        except Exception as e:
            if self.L == 'it':
                QMessageBox.warning(self, "Errore", f"Errore nel caricamento dei record: {str(e)}")
            elif self.L == 'de':
                QMessageBox.warning(self, "Fehler", f"Fehler beim Laden der Datensätze: {str(e)}")
            elif self.L == 'fr':
                QMessageBox.warning(self, "Erreur", f"Erreur lors du chargement des enregistrements: {str(e)}")
            elif self.L == 'es':
                QMessageBox.warning(self, "Error", f"Error al cargar los registros: {str(e)}")
            else:
                QMessageBox.warning(self, "Error", f"Error loading records: {str(e)}")

    def create_tab_statistiche(self) -> QWidget:
        """Create the statistics tab with summary reports."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Toolbar with buttons to refresh and export
        toolbar_layout = QHBoxLayout()

        btn_refresh = QPushButton("Aggiorna Statistiche" if self.L == 'it' else "Refresh Statistics")
        btn_refresh.clicked.connect(self.update_statistics)
        toolbar_layout.addWidget(btn_refresh)

        btn_export_excel = QPushButton("Esporta Excel" if self.L == 'it' else "Export Excel")
        btn_export_excel.clicked.connect(self.export_statistics_excel)
        toolbar_layout.addWidget(btn_export_excel)

        btn_export_pdf = QPushButton("Esporta PDF" if self.L == 'it' else "Export PDF")
        btn_export_pdf.clicked.connect(self.export_statistics_pdf)
        toolbar_layout.addWidget(btn_export_pdf)

        toolbar_layout.addStretch()
        layout.addLayout(toolbar_layout)

        # Text area for statistics
        self.txt_statistiche = QTextEdit()
        self.txt_statistiche.setReadOnly(True)
        self.txt_statistiche.setFont(QFont("Courier", 9))
        layout.addWidget(self.txt_statistiche)

        # Variables to store current statistics
        self.current_stats_text = []
        self.current_stats_data = {}

        return widget

    def get_all_fauna_records(self):
        """Get all fauna records as dictionaries."""
        if not self.DB_MANAGER:
            return []

        try:
            records = self.DB_MANAGER.query(self.MAPPER_TABLE_CLASS)
            result = []
            for rec in records:
                rec_dict = {
                    'id_fauna': rec.id_fauna,
                    'sito': rec.sito,
                    'area': rec.area,
                    'saggio': rec.saggio,
                    'us': rec.us,
                    'datazione_us': rec.datazione_us,
                    'responsabile_scheda': rec.responsabile_scheda,
                    'data_compilazione': rec.data_compilazione,
                    'contesto': rec.contesto,
                    'descrizione_contesto': rec.descrizione_contesto,
                    'resti_connessione_anatomica': rec.resti_connessione_anatomica,
                    'tipologia_accumulo': rec.tipologia_accumulo,
                    'deposizione': rec.deposizione,
                    'numero_stimato_resti': rec.numero_stimato_resti,
                    'numero_minimo_individui': rec.numero_minimo_individui,
                    'specie': rec.specie,
                    'parti_scheletriche': rec.parti_scheletriche,
                    'specie_psi': getattr(rec, 'specie_psi', ''),
                    'misure_ossa': getattr(rec, 'misure_ossa', ''),
                    'stato_frammentazione': rec.stato_frammentazione,
                    'tracce_combustione': rec.tracce_combustione,
                    'stato_conservazione': rec.stato_conservazione,
                }
                result.append(rec_dict)
            return result
        except Exception as e:
            print(f"Error getting fauna records: {str(e)}")
            return []

    def _get_stats_labels(self):
        """Return localized statistics labels for all 7 supported languages."""
        labels = {
            'it': {
                'title': "STATISTICHE RIEPILOGATIVE - SCHEDE FAUNA",
                'general_stats': "STATISTICHE GENERALI",
                'total_records': "Numero totale record",
                'unique_sites': "Numero siti univoci",
                'sites': "Siti",
                'unique_areas': "Numero aree univoche",
                'unique_trenches': "Numero saggi univoci",
                'unique_su': "Numero US univoche",
                'unique_combinations': "Numero combinazioni Sito+Area+Saggio+US univoche",
                'numeric_stats': "STATISTICHE NUMERICHE - RIEPILOGO GENERALE",
                'nmi': "Numero Minimo Individui (NMI)",
                'records_with_nmi': "Totale record con NMI",
                'average': "Media",
                'minimum': "Minimo",
                'maximum': "Massimo",
                'total_sum': "Somma totale",
                'skeletal_parts': "Parti Scheletriche (PSI) - Distribuzione",
                'total_parts': "Totale parti identificate",
                'unique_parts': "Tipi di parti univoche",
                'measurements': "Misure Ossa (mm) - Riepilogo",
                'total_measurements': "Totale misurazioni",
                'stats_by_site': "STATISTICHE PER SITO",
                'site': "SITO",
                'total_records_site': "Totale record",
                'of_total': "del totale generale",
                'num_areas': "Numero aree",
                'num_trenches': "Numero saggi",
                'num_su': "Numero US",
                'main_species': "Specie principali",
                'records_label': "record",
                'nmi_total_site': "NMI totale sito",
                'nmi_average': "NMI medio",
                'main_skeletal_parts': "Parti scheletriche principali",
                'category_distribution': "DISTRIBUZIONE PER CATEGORIE - RIEPILOGO GENERALE",
                'species_top10': "Specie (Top 10)",
                'no_data': "Nessun dato",
                'context': "Contesto",
                'preservation': "Stato di Conservazione",
                'combustion': "Tracce di Combustione",
                'fragmentation': "Stato di Frammentazione",
                'anatomical_connection': "Resti in Connessione Anatomica",
                'descriptive_summary': "SOMMARIO DESCRITTIVO",
                'report_generated': "Report generato il",
                'error_stats': "Errore nel calcolo delle statistiche"
            },
            'en': {
                'title': "SUMMARY STATISTICS - FAUNA RECORDS",
                'general_stats': "GENERAL STATISTICS",
                'total_records': "Total number of records",
                'unique_sites': "Number of unique sites",
                'sites': "Sites",
                'unique_areas': "Number of unique areas",
                'unique_trenches': "Number of unique trenches",
                'unique_su': "Number of unique SU",
                'unique_combinations': "Number of unique Site+Area+Trench+SU combinations",
                'numeric_stats': "NUMERIC STATISTICS - GENERAL SUMMARY",
                'nmi': "Minimum Number of Individuals (MNI)",
                'records_with_nmi': "Total records with MNI",
                'average': "Average",
                'minimum': "Minimum",
                'maximum': "Maximum",
                'total_sum': "Total sum",
                'skeletal_parts': "Skeletal Parts (PSI) - Distribution",
                'total_parts': "Total identified parts",
                'unique_parts': "Unique part types",
                'measurements': "Bone Measurements (mm) - Summary",
                'total_measurements': "Total measurements",
                'stats_by_site': "STATISTICS BY SITE",
                'site': "SITE",
                'total_records_site': "Total records",
                'of_total': "of total",
                'num_areas': "Number of areas",
                'num_trenches': "Number of trenches",
                'num_su': "Number of SU",
                'main_species': "Main species",
                'records_label': "records",
                'nmi_total_site': "Total MNI for site",
                'nmi_average': "Average MNI",
                'main_skeletal_parts': "Main skeletal parts",
                'category_distribution': "DISTRIBUTION BY CATEGORIES - GENERAL SUMMARY",
                'species_top10': "Species (Top 10)",
                'no_data': "No data",
                'context': "Context",
                'preservation': "Preservation State",
                'combustion': "Combustion Traces",
                'fragmentation': "Fragmentation State",
                'anatomical_connection': "Anatomical Connection Remains",
                'descriptive_summary': "DESCRIPTIVE SUMMARY",
                'report_generated': "Report generated on",
                'error_stats': "Error calculating statistics"
            },
            'de': {
                'title': "ZUSAMMENFASSENDE STATISTIKEN - FAUNA-DATENSÄTZE",
                'general_stats': "ALLGEMEINE STATISTIKEN",
                'total_records': "Gesamtzahl der Datensätze",
                'unique_sites': "Anzahl einzigartiger Fundorte",
                'sites': "Fundorte",
                'unique_areas': "Anzahl einzigartiger Bereiche",
                'unique_trenches': "Anzahl einzigartiger Schnitte",
                'unique_su': "Anzahl einzigartiger SE",
                'unique_combinations': "Anzahl einzigartiger Fundort+Bereich+Schnitt+SE Kombinationen",
                'numeric_stats': "NUMERISCHE STATISTIKEN - ALLGEMEINE ZUSAMMENFASSUNG",
                'nmi': "Mindestindividuenzahl (MIZ)",
                'records_with_nmi': "Gesamtdatensätze mit MIZ",
                'average': "Durchschnitt",
                'minimum': "Minimum",
                'maximum': "Maximum",
                'total_sum': "Gesamtsumme",
                'skeletal_parts': "Skelettteile (PSI) - Verteilung",
                'total_parts': "Gesamtzahl identifizierter Teile",
                'unique_parts': "Einzigartige Teiletypen",
                'measurements': "Knochenmaße (mm) - Zusammenfassung",
                'total_measurements': "Gesamtmessungen",
                'stats_by_site': "STATISTIKEN NACH FUNDORT",
                'site': "FUNDORT",
                'total_records_site': "Gesamtdatensätze",
                'of_total': "vom Gesamtergebnis",
                'num_areas': "Anzahl Bereiche",
                'num_trenches': "Anzahl Schnitte",
                'num_su': "Anzahl SE",
                'main_species': "Hauptarten",
                'records_label': "Datensätze",
                'nmi_total_site': "Gesamt-MIZ für Fundort",
                'nmi_average': "Durchschnittliche MIZ",
                'main_skeletal_parts': "Haupt-Skelettteile",
                'category_distribution': "VERTEILUNG NACH KATEGORIEN - ALLGEMEINE ZUSAMMENFASSUNG",
                'species_top10': "Arten (Top 10)",
                'no_data': "Keine Daten",
                'context': "Kontext",
                'preservation': "Erhaltungszustand",
                'combustion': "Brandspuren",
                'fragmentation': "Fragmentierungszustand",
                'anatomical_connection': "Anatomische Verbindungsreste",
                'descriptive_summary': "BESCHREIBENDE ZUSAMMENFASSUNG",
                'report_generated': "Bericht erstellt am",
                'error_stats': "Fehler bei der Statistikberechnung"
            },
            'es': {
                'title': "ESTADISTICAS RESUMIDAS - REGISTROS DE FAUNA",
                'general_stats': "ESTADISTICAS GENERALES",
                'total_records': "Numero total de registros",
                'unique_sites': "Numero de sitios unicos",
                'sites': "Sitios",
                'unique_areas': "Numero de areas unicas",
                'unique_trenches': "Numero de sondeos unicos",
                'unique_su': "Numero de UE unicas",
                'unique_combinations': "Numero de combinaciones Sitio+Area+Sondeo+UE unicas",
                'numeric_stats': "ESTADISTICAS NUMERICAS - RESUMEN GENERAL",
                'nmi': "Numero Minimo de Individuos (NMI)",
                'records_with_nmi': "Total registros con NMI",
                'average': "Media",
                'minimum': "Minimo",
                'maximum': "Maximo",
                'total_sum': "Suma total",
                'skeletal_parts': "Partes Esqueleticas (PSI) - Distribucion",
                'total_parts': "Total partes identificadas",
                'unique_parts': "Tipos de partes unicas",
                'measurements': "Medidas Oseas (mm) - Resumen",
                'total_measurements': "Total mediciones",
                'stats_by_site': "ESTADISTICAS POR SITIO",
                'site': "SITIO",
                'total_records_site': "Total registros",
                'of_total': "del total",
                'num_areas': "Numero de areas",
                'num_trenches': "Numero de sondeos",
                'num_su': "Numero de UE",
                'main_species': "Especies principales",
                'records_label': "registros",
                'nmi_total_site': "NMI total del sitio",
                'nmi_average': "NMI promedio",
                'main_skeletal_parts': "Partes esqueleticas principales",
                'category_distribution': "DISTRIBUCION POR CATEGORIAS - RESUMEN GENERAL",
                'species_top10': "Especies (Top 10)",
                'no_data': "Sin datos",
                'context': "Contexto",
                'preservation': "Estado de Conservacion",
                'combustion': "Trazas de Combustion",
                'fragmentation': "Estado de Fragmentacion",
                'anatomical_connection': "Restos en Conexion Anatomica",
                'descriptive_summary': "RESUMEN DESCRIPTIVO",
                'report_generated': "Informe generado el",
                'error_stats': "Error al calcular estadisticas"
            },
            'fr': {
                'title': "STATISTIQUES RECAPITULATIVES - FICHES FAUNE",
                'general_stats': "STATISTIQUES GENERALES",
                'total_records': "Nombre total d'enregistrements",
                'unique_sites': "Nombre de sites uniques",
                'sites': "Sites",
                'unique_areas': "Nombre de zones uniques",
                'unique_trenches': "Nombre de sondages uniques",
                'unique_su': "Nombre d'US uniques",
                'unique_combinations': "Nombre de combinaisons Site+Zone+Sondage+US uniques",
                'numeric_stats': "STATISTIQUES NUMERIQUES - RESUME GENERAL",
                'nmi': "Nombre Minimum d'Individus (NMI)",
                'records_with_nmi': "Total enregistrements avec NMI",
                'average': "Moyenne",
                'minimum': "Minimum",
                'maximum': "Maximum",
                'total_sum': "Somme totale",
                'skeletal_parts': "Parties Squelettiques (PSI) - Distribution",
                'total_parts': "Total parties identifiees",
                'unique_parts': "Types de parties uniques",
                'measurements': "Mesures Osseuses (mm) - Resume",
                'total_measurements': "Total mesures",
                'stats_by_site': "STATISTIQUES PAR SITE",
                'site': "SITE",
                'total_records_site': "Total enregistrements",
                'of_total': "du total",
                'num_areas': "Nombre de zones",
                'num_trenches': "Nombre de sondages",
                'num_su': "Nombre d'US",
                'main_species': "Especes principales",
                'records_label': "enregistrements",
                'nmi_total_site': "NMI total du site",
                'nmi_average': "NMI moyen",
                'main_skeletal_parts': "Parties squelettiques principales",
                'category_distribution': "DISTRIBUTION PAR CATEGORIES - RESUME GENERAL",
                'species_top10': "Especes (Top 10)",
                'no_data': "Pas de donnees",
                'context': "Contexte",
                'preservation': "Etat de Conservation",
                'combustion': "Traces de Combustion",
                'fragmentation': "Etat de Fragmentation",
                'anatomical_connection': "Restes en Connexion Anatomique",
                'descriptive_summary': "RESUME DESCRIPTIF",
                'report_generated': "Rapport genere le",
                'error_stats': "Erreur lors du calcul des statistiques"
            },
            'ar': {
                'title': "إحصائيات ملخصة - سجلات الحيوانات",
                'general_stats': "إحصائيات عامة",
                'total_records': "إجمالي عدد السجلات",
                'unique_sites': "عدد المواقع الفريدة",
                'sites': "المواقع",
                'unique_areas': "عدد المناطق الفريدة",
                'unique_trenches': "عدد الحفريات الفريدة",
                'unique_su': "عدد الوحدات الطبقية الفريدة",
                'unique_combinations': "عدد التركيبات الفريدة",
                'numeric_stats': "إحصائيات رقمية - ملخص عام",
                'nmi': "الحد الأدنى لعدد الأفراد",
                'records_with_nmi': "إجمالي السجلات مع الحد الأدنى",
                'average': "المتوسط",
                'minimum': "الحد الأدنى",
                'maximum': "الحد الأقصى",
                'total_sum': "المجموع الكلي",
                'skeletal_parts': "الأجزاء الهيكلية - التوزيع",
                'total_parts': "إجمالي الأجزاء المحددة",
                'unique_parts': "أنواع الأجزاء الفريدة",
                'measurements': "قياسات العظام (مم) - ملخص",
                'total_measurements': "إجمالي القياسات",
                'stats_by_site': "إحصائيات حسب الموقع",
                'site': "الموقع",
                'total_records_site': "إجمالي السجلات",
                'of_total': "من الإجمالي",
                'num_areas': "عدد المناطق",
                'num_trenches': "عدد الحفريات",
                'num_su': "عدد الوحدات الطبقية",
                'main_species': "الأنواع الرئيسية",
                'records_label': "سجلات",
                'nmi_total_site': "إجمالي الحد الأدنى للموقع",
                'nmi_average': "متوسط الحد الأدنى",
                'main_skeletal_parts': "الأجزاء الهيكلية الرئيسية",
                'category_distribution': "التوزيع حسب الفئات - ملخص عام",
                'species_top10': "الأنواع (أعلى 10)",
                'no_data': "لا توجد بيانات",
                'context': "السياق",
                'preservation': "حالة الحفظ",
                'combustion': "آثار الاحتراق",
                'fragmentation': "حالة التجزئة",
                'anatomical_connection': "بقايا في اتصال تشريحي",
                'descriptive_summary': "ملخص وصفي",
                'report_generated': "تم إنشاء التقرير في",
                'error_stats': "خطأ في حساب الإحصائيات"
            },
            'ca': {
                'title': "ESTADISTIQUES RESUMIDES - FITXES FAUNA",
                'general_stats': "ESTADISTIQUES GENERALS",
                'total_records': "Nombre total de registres",
                'unique_sites': "Nombre de jaciments unics",
                'sites': "Jaciments",
                'unique_areas': "Nombre d'arees uniques",
                'unique_trenches': "Nombre de sondeigs unics",
                'unique_su': "Nombre d'UE uniques",
                'unique_combinations': "Nombre de combinacions Jaciment+Area+Sondeig+UE uniques",
                'numeric_stats': "ESTADISTIQUES NUMERIQUES - RESUM GENERAL",
                'nmi': "Nombre Minim d'Individus (NMI)",
                'records_with_nmi': "Total registres amb NMI",
                'average': "Mitjana",
                'minimum': "Minim",
                'maximum': "Maxim",
                'total_sum': "Suma total",
                'skeletal_parts': "Parts Esqueletiques (PSI) - Distribucio",
                'total_parts': "Total parts identificades",
                'unique_parts': "Tipus de parts uniques",
                'measurements': "Mesures Ossies (mm) - Resum",
                'total_measurements': "Total mesures",
                'stats_by_site': "ESTADISTIQUES PER JACIMENT",
                'site': "JACIMENT",
                'total_records_site': "Total registres",
                'of_total': "del total",
                'num_areas': "Nombre d'arees",
                'num_trenches': "Nombre de sondeigs",
                'num_su': "Nombre d'UE",
                'main_species': "Especies principals",
                'records_label': "registres",
                'nmi_total_site': "NMI total del jaciment",
                'nmi_average': "NMI mitja",
                'main_skeletal_parts': "Parts esqueletiques principals",
                'category_distribution': "DISTRIBUCIO PER CATEGORIES - RESUM GENERAL",
                'species_top10': "Especies (Top 10)",
                'no_data': "Sense dades",
                'context': "Context",
                'preservation': "Estat de Conservacio",
                'combustion': "Traces de Combustio",
                'fragmentation': "Estat de Fragmentacio",
                'anatomical_connection': "Restes en Connexio Anatomica",
                'descriptive_summary': "RESUM DESCRIPTIU",
                'report_generated': "Informe generat el",
                'error_stats': "Error en calcular estadistiques"
            }
        }
        # Return Italian labels as fallback if language not found
        return labels.get(self.L, labels['it'])

    def update_statistics(self):
        """Calculate and display comprehensive statistics."""
        try:
            records = self.get_all_fauna_records()
            lbl = self._get_stats_labels()  # Get translated labels

            if not records:
                no_data_msg = {
                    'it': "Nessun record presente nel database.",
                    'en': "No records in the database.",
                    'de': "Keine Datensätze in der Datenbank.",
                    'es': "No hay registros en la base de datos.",
                    'fr': "Aucun enregistrement dans la base de données.",
                    'ar': "لا توجد سجلات في قاعدة البيانات.",
                    'ca': "No hi ha registres a la base de dades."
                }
                self.txt_statistiche.setText(no_data_msg.get(self.L, no_data_msg['it']))
                return

            stats_text = []
            stats_text.append("=" * 100)
            stats_text.append(lbl['title'])
            stats_text.append("=" * 100)
            stats_text.append("")

            # === GENERAL STATISTICS ===
            stats_text.append(lbl['general_stats'])
            stats_text.append("-" * 100)
            stats_text.append(f"{lbl['total_records']}: {len(records)}")

            siti = set(r.get('sito', '') for r in records if r.get('sito'))
            aree = set(r.get('area', '') for r in records if r.get('area'))
            saggi = set(r.get('saggio', '') for r in records if r.get('saggio'))
            us_list = set(r.get('us', '') for r in records if r.get('us'))

            stats_text.append(f"{lbl['unique_sites']}: {len(siti)}")
            if siti:
                stats_text.append(f"  {lbl['sites']}: {', '.join(sorted(str(s) for s in siti))}")
            stats_text.append(f"{lbl['unique_areas']}: {len(aree)}")
            stats_text.append(f"{lbl['unique_trenches']}: {len(saggi)}")
            stats_text.append(f"{lbl['unique_su']}: {len(us_list)}")

            # Unique combinations
            combinazioni = set()
            for r in records:
                sito = r.get('sito', '')
                area = r.get('area', '')
                saggio = r.get('saggio', '')
                us = r.get('us', '')
                if sito and area and saggio and us:
                    combinazioni.add((sito, area, saggio, us))
            stats_text.append(f"{lbl['unique_combinations']}: {len(combinazioni)}")
            stats_text.append("")

            # === NUMERIC STATISTICS ===
            stats_text.append(lbl['numeric_stats'])
            stats_text.append("-" * 100)

            nmi_values = [int(r['numero_minimo_individui']) for r in records
                         if r.get('numero_minimo_individui') not in (None, '', 0)]
            if nmi_values:
                stats_text.append(f"{lbl['nmi']}:")
                stats_text.append(f"  {lbl['records_with_nmi']}: {len(nmi_values)}")
                stats_text.append(f"  {lbl['average']}: {sum(nmi_values)/len(nmi_values):.1f}")
                stats_text.append(f"  {lbl['minimum']}: {min(nmi_values)}")
                stats_text.append(f"  {lbl['maximum']}: {max(nmi_values)}")
                stats_text.append(f"  {lbl['total_sum']}: {sum(nmi_values)}")

            # Skeletal Parts (PSI) distribution
            all_psi = {}
            for r in records:
                psi_list = self._extract_psi_from_record(r)
                for psi in psi_list:
                    if psi:
                        all_psi[psi] = all_psi.get(psi, 0) + 1

            if all_psi:
                stats_text.append(f"\n{lbl['skeletal_parts']}:")
                stats_text.append(f"  {lbl['total_parts']}: {sum(all_psi.values())}")
                stats_text.append(f"  {lbl['unique_parts']}: {len(all_psi)}")
                sorted_psi = sorted(all_psi.items(), key=lambda x: x[1], reverse=True)[:10]
                for psi, cnt in sorted_psi:
                    pct = (cnt / sum(all_psi.values())) * 100
                    stats_text.append(f"  - {psi}: {cnt} ({pct:.1f}%)")

            # Measurements
            misure_values = []
            for r in records:
                measurements = self._extract_measurements_from_record(r)
                misure_values.extend(measurements)

            if misure_values:
                stats_text.append(f"\n{lbl['measurements']}:")
                stats_text.append(f"  {lbl['total_measurements']}: {len(misure_values)}")
                stats_text.append(f"  {lbl['average']}: {sum(misure_values)/len(misure_values):.2f} mm")
                stats_text.append(f"  {lbl['minimum']}: {min(misure_values):.2f} mm")
                stats_text.append(f"  {lbl['maximum']}: {max(misure_values):.2f} mm")

            stats_text.append("")

            # === STATISTICS BY SITE ===
            if siti and len(siti) > 0:
                stats_text.append(lbl['stats_by_site'])
                stats_text.append("=" * 100)

                for sito in sorted(str(s) for s in siti):
                    sito_records = [r for r in records if str(r.get('sito', '')) == sito]
                    sito_pct = (len(sito_records) / len(records)) * 100

                    stats_text.append(f"\n{'#' * 100}")
                    stats_text.append(f"{lbl['site']}: {sito}")
                    stats_text.append(f"{'#' * 100}")
                    stats_text.append(f"{lbl['total_records_site']}: {len(sito_records)} ({sito_pct:.1f}% {lbl['of_total']})")

                    # Areas, trenches, SU in the site
                    sito_aree = set(r.get('area', '') for r in sito_records if r.get('area'))
                    sito_saggi = set(r.get('saggio', '') for r in sito_records if r.get('saggio'))
                    sito_us = set(r.get('us', '') for r in sito_records if r.get('us'))

                    stats_text.append(f"{lbl['num_areas']}: {len(sito_aree)}")
                    stats_text.append(f"{lbl['num_trenches']}: {len(sito_saggi)}")
                    stats_text.append(f"{lbl['num_su']}: {len(sito_us)}")

                    # Main species in the site
                    sito_species = {}
                    for r in sito_records:
                        species_list = self._extract_species_from_record(r)
                        for sp in species_list:
                            if sp:
                                sito_species[sp] = sito_species.get(sp, 0) + 1

                    if sito_species:
                        top_species = sorted(sito_species.items(), key=lambda x: x[1], reverse=True)[:5]
                        stats_text.append(f"\n{lbl['main_species']}:")
                        for sp, cnt in top_species:
                            sp_pct = (cnt / len(sito_records)) * 100
                            stats_text.append(f"  - {sp}: {cnt} {lbl['records_label']} ({sp_pct:.1f}%)")

                    # NMI total for site
                    sito_nmi = [int(r['numero_minimo_individui']) for r in sito_records
                               if r.get('numero_minimo_individui') not in (None, '', 0)]
                    if sito_nmi:
                        stats_text.append(f"\n{lbl['nmi_total_site']}: {sum(sito_nmi)}")
                        stats_text.append(f"{lbl['nmi_average']}: {sum(sito_nmi)/len(sito_nmi):.1f}")

                    # PSI for site
                    sito_psi = {}
                    for r in sito_records:
                        psi_list = self._extract_psi_from_record(r)
                        for psi in psi_list:
                            if psi:
                                sito_psi[psi] = sito_psi.get(psi, 0) + 1
                    if sito_psi:
                        top_psi = sorted(sito_psi.items(), key=lambda x: x[1], reverse=True)[:5]
                        stats_text.append(f"\n{lbl['main_skeletal_parts']}:")
                        for psi, cnt in top_psi:
                            stats_text.append(f"  - {psi}: {cnt}")

                stats_text.append(f"\n{'=' * 100}\n")

            # === DISTRIBUTION BY CATEGORIES ===
            stats_text.append(lbl['category_distribution'])
            stats_text.append("-" * 100)

            def count_values(field_name, label, top_n=10):
                values_count = {}
                for r in records:
                    val = r.get(field_name, '')
                    if val and str(val).strip():
                        values_count[str(val)] = values_count.get(str(val), 0) + 1

                if values_count:
                    stats_text.append(f"\n{label}:")
                    sorted_items = sorted(values_count.items(), key=lambda x: x[1], reverse=True)
                    for val, count in sorted_items[:top_n]:
                        percentage = (count / len(records)) * 100
                        stats_text.append(f"  {val}: {count} ({percentage:.1f}%)")
                else:
                    stats_text.append(f"\n{label}: {lbl['no_data']}")

            # Species
            all_species = {}
            for r in records:
                species_list = self._extract_species_from_record(r)
                for sp in species_list:
                    if sp and str(sp).strip():
                        all_species[sp] = all_species.get(sp, 0) + 1
            if all_species:
                stats_text.append(f"\n{lbl['species_top10']}:")
                sorted_species = sorted(all_species.items(), key=lambda x: x[1], reverse=True)
                for val, count in sorted_species[:10]:
                    percentage = (count / len(records)) * 100
                    stats_text.append(f"  {val}: {count} ({percentage:.1f}%)")
            else:
                stats_text.append(f"\n{lbl['species_top10']}: {lbl['no_data']}")

            count_values('contesto', lbl['context'])
            count_values('stato_conservazione', lbl['preservation'])
            count_values('tracce_combustione', lbl['combustion'])
            count_values('stato_frammentazione', lbl['fragmentation'])
            count_values('resti_connessione_anatomica', lbl['anatomical_connection'])

            stats_text.append("")

            # === DESCRIPTIVE SUMMARY ===
            stats_text.append("=" * 100)
            stats_text.append(lbl['descriptive_summary'])
            stats_text.append("=" * 100)
            stats_text.append("")

            summary = self._generate_descriptive_summary(records, nmi_values, misure_values,
                                                        siti, aree, saggi, us_list)
            stats_text.extend(summary)

            stats_text.append("")
            stats_text.append("=" * 100)
            stats_text.append(f"{lbl['report_generated']}: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            stats_text.append("=" * 100)

            # Save for export
            self.current_stats_text = stats_text
            self.current_stats_data = {
                'records': records,
                'total': len(records),
                'siti': siti,
                'aree': aree,
                'saggi': saggi,
                'us': us_list,
                'nmi_values': nmi_values,
                'misure_values': misure_values
            }

            # Display
            self.txt_statistiche.setText("\n".join(stats_text))

        except Exception as e:
            error_labels = self._get_stats_labels()
            error_msg = f"{error_labels['error_stats']}:\n{str(e)}"
            QMessageBox.critical(self, "Error", error_msg)
            import traceback
            traceback.print_exc()

    def _extract_species_from_record(self, record: dict) -> list:
        """Extract all species from a record (supports both JSON and single field)."""
        species = []

        # Try first with JSON format
        specie_psi_json = record.get('specie_psi', '')
        if specie_psi_json and str(specie_psi_json).strip():
            try:
                specie_psi_data = json.loads(specie_psi_json)
                for row in specie_psi_data:
                    if len(row) > 0 and row[0]:
                        species.append(row[0])
            except:
                pass

        # Fallback: use old specie field
        if not species:
            sp = record.get('specie', '')
            if sp:
                species.append(str(sp))

        return species

    def _extract_measurements_from_record(self, record: dict) -> list:
        """Extract all measurements from a record (supports both JSON and single field)."""
        measurements = []

        # Try first with JSON format
        misure_json = record.get('misure_ossa', '')
        if misure_json and str(misure_json).strip():
            try:
                misure_data = json.loads(misure_json)
                for row in misure_data:
                    if len(row) >= 6:
                        for i in range(2, 6):
                            try:
                                val = float(row[i]) if row[i] else 0
                                if val > 0:
                                    measurements.append(val)
                            except (ValueError, TypeError):
                                pass
            except:
                pass

        return measurements

    def _extract_psi_from_record(self, record: dict) -> list:
        """Extract all skeletal parts (PSI) from a record."""
        psi_list = []

        # Try first with JSON format
        specie_psi_json = record.get('specie_psi', '')
        if specie_psi_json and str(specie_psi_json).strip():
            try:
                specie_psi_data = json.loads(specie_psi_json)
                for row in specie_psi_data:
                    if len(row) > 1 and row[1]:
                        psi_list.append(row[1])
            except:
                pass

        # Fallback: use old parti_scheletriche field
        if not psi_list:
            psi = record.get('parti_scheletriche', '')
            if psi:
                psi_list.append(str(psi))

        return psi_list

    def _safe_float(self, value) -> float:
        """Safely convert a value to float."""
        try:
            return float(value) if value else 0.0
        except (ValueError, TypeError):
            return 0.0

    def _get_summary_texts(self):
        """Return localized summary texts for all 7 supported languages."""
        texts = {
            'it': {
                'intro': "L'analisi del dataset faunistico comprende {records} record archeologici distribuiti su {sites} siti, {areas} aree, {trenches} saggi e {su} unita stratigrafiche.",
                'site_distribution': "DISTRIBUZIONE PER SITO:",
                'dominant_site': "Il sito piu rappresentato e '{site}' con {count} record ({pct}% del totale).",
                'other_sites': "Gli altri {count} siti contribuiscono con il restante {pct}% dei dati.",
                'species_analysis': "ANALISI DELLE SPECIE:",
                'species_identified': "Sono state identificate {count} specie diverse. Le specie predominanti sono:",
                'species_present': "  - {species}: presente in {count} record ({pct}% del totale)",
                'nmi_title': "NUMERO MINIMO DI INDIVIDUI (NMI):",
                'nmi_text': "Il numero minimo totale di individui e {total}, con una media di {avg} individui per record. Il valore minimo registrato e {min}, mentre il massimo e {max}.",
                'context_title': "CONTESTI ARCHEOLOGICI:",
                'context_text': "Il contesto prevalente e '{context}' con {count} occorrenze ({pct}% del totale).",
                'conclusion_title': "CONCLUSIONI:",
                'conclusion_text': "Il dataset rappresenta un campione significativo per l'analisi archeozoologica del sito. I dati raccolti permettono di ricostruire aspetti legati all'economia, all'alimentazione e alle pratiche cultuali delle popolazioni antiche che hanno abitato l'area."
            },
            'en': {
                'intro': "The faunal dataset analysis comprises {records} archaeological records distributed across {sites} sites, {areas} areas, {trenches} trenches and {su} stratigraphic units.",
                'site_distribution': "DISTRIBUTION BY SITE:",
                'dominant_site': "The most represented site is '{site}' with {count} records ({pct}% of total).",
                'other_sites': "The other {count} sites contribute the remaining {pct}% of the data.",
                'species_analysis': "SPECIES ANALYSIS:",
                'species_identified': "{count} different species have been identified. The predominant species are:",
                'species_present': "  - {species}: present in {count} records ({pct}% of total)",
                'nmi_title': "MINIMUM NUMBER OF INDIVIDUALS (MNI):",
                'nmi_text': "The total minimum number of individuals is {total}, with an average of {avg} individuals per record. The minimum value recorded is {min}, while the maximum is {max}.",
                'context_title': "ARCHAEOLOGICAL CONTEXTS:",
                'context_text': "The prevalent context is '{context}' with {count} occurrences ({pct}% of total).",
                'conclusion_title': "CONCLUSIONS:",
                'conclusion_text': "The dataset represents a significant sample for the archaeozoological analysis of the site. The collected data allow reconstruction of aspects related to economy, diet, and cultic practices of the ancient populations that inhabited the area."
            },
            'de': {
                'intro': "Die Analyse des Faunadatensatzes umfasst {records} archaeologische Datensatze, verteilt auf {sites} Fundorte, {areas} Bereiche, {trenches} Schnitte und {su} stratigraphische Einheiten.",
                'site_distribution': "VERTEILUNG NACH FUNDORT:",
                'dominant_site': "Der am meisten vertretene Fundort ist '{site}' mit {count} Datensatzen ({pct}% der Gesamtzahl).",
                'other_sites': "Die anderen {count} Fundorte tragen die restlichen {pct}% der Daten bei.",
                'species_analysis': "ARTENANALYSE:",
                'species_identified': "Es wurden {count} verschiedene Arten identifiziert. Die vorherrschenden Arten sind:",
                'species_present': "  - {species}: in {count} Datensatzen vorhanden ({pct}% der Gesamtzahl)",
                'nmi_title': "MINDESTINDIVIDUENZAHL (MIZ):",
                'nmi_text': "Die Gesamtmindestindividuenzahl betragt {total}, mit einem Durchschnitt von {avg} Individuen pro Datensatz. Der minimale Wert ist {min}, der maximale ist {max}.",
                'context_title': "ARCHAOLOGISCHE KONTEXTE:",
                'context_text': "Der vorherrschende Kontext ist '{context}' mit {count} Vorkommen ({pct}% der Gesamtzahl).",
                'conclusion_title': "SCHLUSSFOLGERUNGEN:",
                'conclusion_text': "Der Datensatz stellt eine bedeutende Stichprobe fur die archaozoologische Analyse des Fundortes dar. Die gesammelten Daten ermoglichen die Rekonstruktion von Aspekten der Wirtschaft, Ernahrung und kultischen Praktiken der antiken Bevolkerungen."
            },
            'es': {
                'intro': "El analisis del conjunto de datos faunisticos comprende {records} registros arqueologicos distribuidos en {sites} sitios, {areas} areas, {trenches} sondeos y {su} unidades estratigraficas.",
                'site_distribution': "DISTRIBUCION POR SITIO:",
                'dominant_site': "El sitio mas representado es '{site}' con {count} registros ({pct}% del total).",
                'other_sites': "Los otros {count} sitios contribuyen con el {pct}% restante de los datos.",
                'species_analysis': "ANALISIS DE ESPECIES:",
                'species_identified': "Se han identificado {count} especies diferentes. Las especies predominantes son:",
                'species_present': "  - {species}: presente en {count} registros ({pct}% del total)",
                'nmi_title': "NUMERO MINIMO DE INDIVIDUOS (NMI):",
                'nmi_text': "El numero minimo total de individuos es {total}, con un promedio de {avg} individuos por registro. El valor minimo registrado es {min}, mientras que el maximo es {max}.",
                'context_title': "CONTEXTOS ARQUEOLOGICOS:",
                'context_text': "El contexto prevalente es '{context}' con {count} ocurrencias ({pct}% del total).",
                'conclusion_title': "CONCLUSIONES:",
                'conclusion_text': "El conjunto de datos representa una muestra significativa para el analisis arqueozoologico del sitio. Los datos recopilados permiten reconstruir aspectos relacionados con la economia, la alimentacion y las practicas cultuales de las poblaciones antiguas."
            },
            'fr': {
                'intro': "L'analyse du jeu de donnees fauniques comprend {records} enregistrements archeologiques repartis sur {sites} sites, {areas} zones, {trenches} sondages et {su} unites stratigraphiques.",
                'site_distribution': "DISTRIBUTION PAR SITE:",
                'dominant_site': "Le site le plus represente est '{site}' avec {count} enregistrements ({pct}% du total).",
                'other_sites': "Les {count} autres sites contribuent aux {pct}% restants des donnees.",
                'species_analysis': "ANALYSE DES ESPECES:",
                'species_identified': "{count} especes differentes ont ete identifiees. Les especes predominantes sont:",
                'species_present': "  - {species}: present dans {count} enregistrements ({pct}% du total)",
                'nmi_title': "NOMBRE MINIMUM D'INDIVIDUS (NMI):",
                'nmi_text': "Le nombre minimum total d'individus est de {total}, avec une moyenne de {avg} individus par enregistrement. La valeur minimale enregistree est {min}, tandis que la maximale est {max}.",
                'context_title': "CONTEXTES ARCHEOLOGIQUES:",
                'context_text': "Le contexte prevalent est '{context}' avec {count} occurrences ({pct}% du total).",
                'conclusion_title': "CONCLUSIONS:",
                'conclusion_text': "Le jeu de donnees represente un echantillon significatif pour l'analyse archeozoologique du site. Les donnees collectees permettent de reconstituer des aspects lies a l'economie, l'alimentation et les pratiques cultuelles des populations anciennes."
            },
            'ar': {
                'intro': "يشمل تحليل بيانات الحيوانات {records} سجلاً أثرياً موزعة على {sites} مواقع، {areas} مناطق، {trenches} حفريات و{su} وحدات طبقية.",
                'site_distribution': "التوزيع حسب الموقع:",
                'dominant_site': "الموقع الأكثر تمثيلاً هو '{site}' بـ {count} سجل ({pct}% من الإجمالي).",
                'other_sites': "تساهم المواقع الأخرى البالغ عددها {count} بنسبة {pct}% المتبقية من البيانات.",
                'species_analysis': "تحليل الأنواع:",
                'species_identified': "تم تحديد {count} نوعاً مختلفاً. الأنواع السائدة هي:",
                'species_present': "  - {species}: موجود في {count} سجل ({pct}% من الإجمالي)",
                'nmi_title': "الحد الأدنى لعدد الأفراد:",
                'nmi_text': "إجمالي الحد الأدنى لعدد الأفراد هو {total}، بمتوسط {avg} فرد لكل سجل. القيمة الدنيا المسجلة هي {min}، بينما القصوى هي {max}.",
                'context_title': "السياقات الأثرية:",
                'context_text': "السياق السائد هو '{context}' بـ {count} حالة ({pct}% من الإجمالي).",
                'conclusion_title': "الاستنتاجات:",
                'conclusion_text': "تمثل مجموعة البيانات عينة مهمة للتحليل الأثري الحيواني للموقع. تسمح البيانات المجمعة بإعادة بناء جوانب تتعلق بالاقتصاد والتغذية والممارسات الطقوسية للسكان القدماء."
            },
            'ca': {
                'intro': "L'analisi del conjunt de dades faunistiques compren {records} registres arqueologics distribuits en {sites} jaciments, {areas} arees, {trenches} sondeigs i {su} unitats estratigrafiques.",
                'site_distribution': "DISTRIBUCIO PER JACIMENT:",
                'dominant_site': "El jaciment mes representat es '{site}' amb {count} registres ({pct}% del total).",
                'other_sites': "Els altres {count} jaciments contribueixen amb el {pct}% restant de les dades.",
                'species_analysis': "ANALISI D'ESPECIES:",
                'species_identified': "S'han identificat {count} especies diferents. Les especies predominants son:",
                'species_present': "  - {species}: present en {count} registres ({pct}% del total)",
                'nmi_title': "NOMBRE MINIM D'INDIVIDUS (NMI):",
                'nmi_text': "El nombre minim total d'individus es {total}, amb una mitjana de {avg} individus per registre. El valor minim registrat es {min}, mentre que el maxim es {max}.",
                'context_title': "CONTEXTOS ARQUEOLOGICS:",
                'context_text': "El context prevalent es '{context}' amb {count} ocurrencies ({pct}% del total).",
                'conclusion_title': "CONCLUSIONS:",
                'conclusion_text': "El conjunt de dades representa una mostra significativa per a l'analisi arqueozoologica del jaciment. Les dades recollides permeten reconstruir aspectes relacionats amb l'economia, l'alimentacio i les practiques cultuals de les poblacions antigues."
            }
        }
        return texts.get(self.L, texts['it'])

    def _generate_descriptive_summary(self, records, nmi_values, misure_values, siti, aree, saggi, us_list):
        """Generate a descriptive summary of the statistics."""
        summary = []
        txt = self._get_summary_texts()

        # Introduction
        summary.append(txt['intro'].format(
            records=len(records), sites=len(siti), areas=len(aree),
            trenches=len(saggi), su=len(us_list)
        ))
        summary.append("")

        # Analysis by site
        if len(siti) > 0:
            summary.append(txt['site_distribution'])
            site_records = {}
            for r in records:
                site = r.get('sito', '')
                if site:
                    if str(site) not in site_records:
                        site_records[str(site)] = []
                    site_records[str(site)].append(r)

            # Dominant site
            sorted_sites = sorted(site_records.items(), key=lambda x: len(x[1]), reverse=True)
            if sorted_sites:
                dominant_site = sorted_sites[0]
                pct = (len(dominant_site[1]) / len(records)) * 100

                summary.append(txt['dominant_site'].format(
                    site=dominant_site[0], count=len(dominant_site[1]), pct=f"{pct:.1f}"
                ))

                if len(siti) > 1:
                    summary.append(txt['other_sites'].format(
                        count=len(siti) - 1, pct=f"{100 - pct:.1f}"
                    ))

            summary.append("")

        # Species analysis
        species_count = {}
        for r in records:
            species_list = self._extract_species_from_record(r)
            for sp in species_list:
                if sp:
                    species_count[sp] = species_count.get(sp, 0) + 1

        if species_count:
            top_3_species = sorted(species_count.items(), key=lambda x: x[1], reverse=True)[:3]
            summary.append(txt['species_analysis'])
            summary.append(txt['species_identified'].format(count=len(species_count)))

            for sp, count in top_3_species:
                pct = (count / len(records)) * 100
                summary.append(txt['species_present'].format(
                    species=sp, count=count, pct=f"{pct:.1f}"
                ))

            summary.append("")

        # NMI analysis
        if nmi_values:
            total_nmi = sum(nmi_values)
            avg_nmi = total_nmi / len(nmi_values)
            summary.append(txt['nmi_title'])
            summary.append(txt['nmi_text'].format(
                total=total_nmi, avg=f"{avg_nmi:.1f}",
                min=min(nmi_values), max=max(nmi_values)
            ))
            summary.append("")

        # Context analysis
        context_count = {}
        for r in records:
            ctx = r.get('contesto', '')
            if ctx:
                context_count[str(ctx)] = context_count.get(str(ctx), 0) + 1

        if context_count:
            dominant_context = max(context_count.items(), key=lambda x: x[1])
            pct = (dominant_context[1] / len(records)) * 100
            summary.append(txt['context_title'])
            summary.append(txt['context_text'].format(
                context=dominant_context[0], count=dominant_context[1], pct=f"{pct:.1f}"
            ))
            summary.append("")

        # Conclusion
        summary.append(txt['conclusion_title'])
        summary.append(txt['conclusion_text'])

        return summary

    def export_statistics_excel(self):
        """Export statistics to Excel (CSV) format."""
        if not self.current_stats_text:
            msg = "Genera prima le statistiche con 'Aggiorna Statistiche'" if self.L == 'it' else "Generate statistics first with 'Refresh Statistics'"
            QMessageBox.warning(self, "Attenzione" if self.L == 'it' else "Warning", msg)
            return

        try:
            import csv

            # File dialog
            default_name = f"statistiche_fauna_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Salva statistiche Excel" if self.L == 'it' else "Save Statistics Excel",
                default_name,
                "File CSV (*.csv);;Tutti i file (*)" if self.L == 'it' else "CSV Files (*.csv);;All Files (*)"
            )

            if not file_path:
                return

            # Create CSV with structured data
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)

                # Header
                writer.writerow(['STATISTICHE FAUNA - EXPORT'])
                writer.writerow(['Data generazione', datetime.now().strftime('%d/%m/%Y %H:%M:%S')])
                writer.writerow([])

                # General statistics
                writer.writerow(['STATISTICHE GENERALI'])
                writer.writerow(['Totale record', self.current_stats_data.get('total', 0)])
                writer.writerow(['Numero siti', len(self.current_stats_data.get('siti', []))])
                writer.writerow(['Numero aree', len(self.current_stats_data.get('aree', []))])
                writer.writerow(['Numero saggi', len(self.current_stats_data.get('saggi', []))])
                writer.writerow(['Numero US', len(self.current_stats_data.get('us', []))])
                writer.writerow([])

                # NMI
                nmi_vals = self.current_stats_data.get('nmi_values', [])
                if nmi_vals:
                    writer.writerow(['NUMERO MINIMO INDIVIDUI (NMI)'])
                    writer.writerow(['Totale record con NMI', len(nmi_vals)])
                    writer.writerow(['Media', f"{sum(nmi_vals)/len(nmi_vals):.1f}"])
                    writer.writerow(['Minimo', min(nmi_vals)])
                    writer.writerow(['Massimo', max(nmi_vals)])
                    writer.writerow(['Somma totale', sum(nmi_vals)])
                    writer.writerow([])

                # Species distribution
                records = self.current_stats_data.get('records', [])
                if records:
                    species_count = {}
                    for r in records:
                        species_list = self._extract_species_from_record(r)
                        for sp in species_list:
                            if sp:
                                species_count[sp] = species_count.get(sp, 0) + 1

                    if species_count:
                        writer.writerow(['DISTRIBUZIONE SPECIE'])
                        writer.writerow(['Specie', 'Conteggio', 'Percentuale'])
                        sorted_species = sorted(species_count.items(), key=lambda x: x[1], reverse=True)
                        for sp, count in sorted_species:
                            pct = (count / len(records)) * 100
                            writer.writerow([sp, count, f"{pct:.1f}%"])
                        writer.writerow([])

                # Full text report
                writer.writerow(['REPORT COMPLETO'])
                for line in self.current_stats_text:
                    writer.writerow([line])

            success_msg = f"Statistiche esportate in:\n{file_path}" if self.L == 'it' else f"Statistics exported to:\n{file_path}"
            QMessageBox.information(self, "Successo" if self.L == 'it' else "Success", success_msg)

        except Exception as e:
            error_msg = f"Errore nell'esportazione Excel:\n{str(e)}" if self.L == 'it' else f"Error exporting Excel:\n{str(e)}"
            QMessageBox.critical(self, "Errore" if self.L == 'it' else "Error", error_msg)
            import traceback
            traceback.print_exc()

    def export_statistics_pdf(self):
        """Export statistics to PDF format."""
        if not self.current_stats_text:
            msg = "Genera prima le statistiche con 'Aggiorna Statistiche'" if self.L == 'it' else "Generate statistics first with 'Refresh Statistics'"
            QMessageBox.warning(self, "Attenzione" if self.L == 'it' else "Warning", msg)
            return

        try:
            # File dialog
            default_name = f"statistiche_fauna_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Salva statistiche PDF" if self.L == 'it' else "Save Statistics PDF",
                default_name,
                "File PDF (*.pdf);;Tutti i file (*)" if self.L == 'it' else "PDF Files (*.pdf);;All Files (*)"
            )

            if not file_path:
                return

            # Try to use ReportLab
            try:
                from reportlab.lib.pagesizes import A4
                from reportlab.lib import colors
                from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                from reportlab.lib.units import cm

                # Create PDF
                doc = SimpleDocTemplate(file_path, pagesize=A4,
                                       leftMargin=1.5*cm, rightMargin=1.5*cm,
                                       topMargin=2*cm, bottomMargin=2*cm)

                styles = getSampleStyleSheet()
                story = []

                # Title
                title_style = ParagraphStyle(
                    'CustomTitle',
                    parent=styles['Heading1'],
                    fontSize=16,
                    textColor=colors.HexColor('#2c3e50'),
                    spaceAfter=30,
                    alignment=1
                )

                story.append(Paragraph("STATISTICHE RIEPILOGATIVE - SCHEDE FAUNA", title_style))
                story.append(Spacer(1, 0.5*cm))

                # Date
                date_style = ParagraphStyle(
                    'DateStyle',
                    parent=styles['Normal'],
                    fontSize=10,
                    textColor=colors.grey,
                    alignment=1
                )
                story.append(Paragraph(f"Report generato il: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", date_style))
                story.append(Spacer(1, 1*cm))

                # Content
                mono_style = ParagraphStyle(
                    'MonoStyle',
                    parent=styles['Normal'],
                    fontSize=8,
                    fontName='Courier',
                    leading=10
                )

                for line in self.current_stats_text:
                    if line.strip():
                        story.append(Paragraph(line, mono_style))
                    else:
                        story.append(Spacer(1, 0.2*cm))

                doc.build(story)

                success_msg = f"Statistiche esportate in:\n{file_path}" if self.L == 'it' else f"Statistics exported to:\n{file_path}"
                QMessageBox.information(self, "Successo" if self.L == 'it' else "Success", success_msg)

            except ImportError:
                # Fallback: save as text file with PDF extension
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(self.current_stats_text))

                fallback_msg = (f"Statistiche salvate in formato testo:\n{file_path}\n\n"
                               "Nota: Installa 'reportlab' per esportare in formato PDF vero:\n"
                               "pip install reportlab") if self.L == 'it' else (
                               f"Statistics saved in text format:\n{file_path}\n\n"
                               "Note: Install 'reportlab' to export as true PDF:\n"
                               "pip install reportlab")

                QMessageBox.information(
                    self,
                    "Esportazione completata" if self.L == 'it' else "Export completed",
                    fallback_msg
                )

        except Exception as e:
            error_msg = f"Errore nell'esportazione PDF:\n{str(e)}" if self.L == 'it' else f"Error exporting PDF:\n{str(e)}"
            QMessageBox.critical(self, "Errore" if self.L == 'it' else "Error", error_msg)
            import traceback
            traceback.print_exc()

    def on_pushButton_exp_pdf_sheet_pressed(self):
        """Export Fauna records to PDF sheets."""
        if len(self.DATA_LIST) == 0:
            msg = "Nessun record da esportare" if self.L == 'it' else "No records to export"
            QMessageBox.warning(self, "Attenzione" if self.L == 'it' else "Warning", msg)
            return

        try:
            import os

            # Get PYARCHINIT_HOME
            pyarchinit_home = os.environ.get('PYARCHINIT_HOME', '')
            if not pyarchinit_home:
                raise Exception("PYARCHINIT_HOME environment variable is not set")

            # Determine the filename based on language
            pdf_filenames = {
                'it': 'scheda_Fauna.pdf',
                'de': 'Fauna_formular.pdf',
                'fr': 'fiche_Faune.pdf',
                'es': 'ficha_Fauna.pdf',
                'ar': 'fauna_bitaqa.pdf',
                'ca': 'fitxa_Fauna.pdf',
                'en': 'Fauna_record.pdf'
            }
            pdf_filename = pdf_filenames.get(self.L, pdf_filenames['en'])
            pdf_folder = os.path.join(pyarchinit_home, 'pyarchinit_PDF_folder')
            pdf_path = os.path.join(pdf_folder, pdf_filename)

            # Ensure the PDF folder exists
            if not os.path.exists(pdf_folder):
                os.makedirs(pdf_folder)
                print(f"Created PDF folder: {pdf_folder}")

            # Check if logo exists (required for PDF generation)
            db_folder = os.path.join(pyarchinit_home, 'pyarchinit_DB_folder')
            logo_path = os.path.join(db_folder, 'logo.jpg')
            if not os.path.exists(logo_path):
                # Try alternative logo names
                alt_logos = ['logo.png', 'logo_en.jpg', 'logo_de.jpg']
                logo_found = False
                for alt in alt_logos:
                    alt_path = os.path.join(db_folder, alt)
                    if os.path.exists(alt_path):
                        logo_found = True
                        break
                if not logo_found:
                    raise Exception(f"Logo file not found in {db_folder}. Required: logo.jpg")

            Fauna_pdf_sheet = generate_fauna_pdf()
            data_list = self.generate_list_pdf()

            print(f"Generating PDF with {len(data_list)} records...")
            print(f"Target path: {pdf_path}")

            if self.L == 'it':
                Fauna_pdf_sheet.build_Fauna_sheets(data_list)
            elif self.L == 'de':
                Fauna_pdf_sheet.build_Fauna_sheets_de(data_list)
            elif self.L == 'fr':
                Fauna_pdf_sheet.build_Fauna_sheets_fr(data_list)
            elif self.L == 'es':
                Fauna_pdf_sheet.build_Fauna_sheets_es(data_list)
            elif self.L == 'ar':
                Fauna_pdf_sheet.build_Fauna_sheets_ar(data_list)
            elif self.L == 'ca':
                Fauna_pdf_sheet.build_Fauna_sheets_ca(data_list)
            else:
                Fauna_pdf_sheet.build_Fauna_sheets_en(data_list)

            # Verify file was created
            if os.path.exists(pdf_path):
                file_size = os.path.getsize(pdf_path)
                print(f"PDF created successfully: {pdf_path} ({file_size} bytes)")

                # Show success message with file path
                if self.L == 'it':
                    msg = f"Esportazione schede completata!\n\nFile salvato in:\n{pdf_path}\n\nDimensione: {file_size} bytes"
                elif self.L == 'de':
                    msg = f"Export abgeschlossen!\n\nDatei gespeichert unter:\n{pdf_path}\n\nGrosse: {file_size} bytes"
                elif self.L == 'fr':
                    msg = f"Export termine!\n\nFichier enregistre dans:\n{pdf_path}\n\nTaille: {file_size} bytes"
                elif self.L == 'es':
                    msg = f"Exportacion completada!\n\nArchivo guardado en:\n{pdf_path}\n\nTamano: {file_size} bytes"
                elif self.L == 'ar':
                    msg = f"اكتمل التصدير!\n\nتم حفظ الملف في:\n{pdf_path}\n\nالحجم: {file_size} bytes"
                elif self.L == 'ca':
                    msg = f"Exportacio completada!\n\nFitxer desat a:\n{pdf_path}\n\nMida: {file_size} bytes"
                else:
                    msg = f"Sheet export completed!\n\nFile saved to:\n{pdf_path}\n\nSize: {file_size} bytes"

                QMessageBox.information(self, "Success" if self.L != 'it' else "Successo", msg)
            else:
                raise Exception(f"PDF file was not created at: {pdf_path}")

        except Exception as e:
            error_msg = f"Errore nell'esportazione:\n{str(e)}" if self.L == 'it' else f"Export error:\n{str(e)}"
            QMessageBox.critical(self, "Errore" if self.L == 'it' else "Error", error_msg)
            import traceback
            traceback.print_exc()

    def generate_list_pdf(self):
        """Generate data list for PDF export."""
        data_list = []
        for i in range(len(self.DATA_LIST)):
            data_list.append([
                str(self.DATA_LIST[i].id_fauna),  # 0
                str(self.DATA_LIST[i].id_us) if self.DATA_LIST[i].id_us else '',  # 1
                str(self.DATA_LIST[i].sito) if self.DATA_LIST[i].sito else '',  # 2
                str(self.DATA_LIST[i].area) if self.DATA_LIST[i].area else '',  # 3
                str(self.DATA_LIST[i].saggio) if self.DATA_LIST[i].saggio else '',  # 4
                str(self.DATA_LIST[i].us) if self.DATA_LIST[i].us else '',  # 5
                str(self.DATA_LIST[i].datazione_us) if self.DATA_LIST[i].datazione_us else '',  # 6
                str(self.DATA_LIST[i].responsabile_scheda) if self.DATA_LIST[i].responsabile_scheda else '',  # 7
                str(self.DATA_LIST[i].data_compilazione) if self.DATA_LIST[i].data_compilazione else '',  # 8
                str(self.DATA_LIST[i].documentazione_fotografica) if self.DATA_LIST[i].documentazione_fotografica else '',  # 9
                str(self.DATA_LIST[i].metodologia_recupero) if self.DATA_LIST[i].metodologia_recupero else '',  # 10
                str(self.DATA_LIST[i].contesto) if self.DATA_LIST[i].contesto else '',  # 11
                str(self.DATA_LIST[i].descrizione_contesto) if self.DATA_LIST[i].descrizione_contesto else '',  # 12
                str(self.DATA_LIST[i].resti_connessione_anatomica) if self.DATA_LIST[i].resti_connessione_anatomica else '',  # 13
                str(self.DATA_LIST[i].tipologia_accumulo) if self.DATA_LIST[i].tipologia_accumulo else '',  # 14
                str(self.DATA_LIST[i].deposizione) if self.DATA_LIST[i].deposizione else '',  # 15
                str(self.DATA_LIST[i].numero_stimato_resti) if self.DATA_LIST[i].numero_stimato_resti else '',  # 16
                self.DATA_LIST[i].numero_minimo_individui if self.DATA_LIST[i].numero_minimo_individui else 0,  # 17
                str(self.DATA_LIST[i].specie) if self.DATA_LIST[i].specie else '',  # 18
                str(self.DATA_LIST[i].parti_scheletriche) if self.DATA_LIST[i].parti_scheletriche else '',  # 19
                str(self.DATA_LIST[i].specie_psi) if self.DATA_LIST[i].specie_psi else '',  # 20
                str(self.DATA_LIST[i].misure_ossa) if self.DATA_LIST[i].misure_ossa else '',  # 21
                str(self.DATA_LIST[i].stato_frammentazione) if self.DATA_LIST[i].stato_frammentazione else '',  # 22
                str(self.DATA_LIST[i].tracce_combustione) if self.DATA_LIST[i].tracce_combustione else '',  # 23
                self.DATA_LIST[i].combustione_altri_materiali_us if self.DATA_LIST[i].combustione_altri_materiali_us else 0,  # 24
                str(self.DATA_LIST[i].tipo_combustione) if self.DATA_LIST[i].tipo_combustione else '',  # 25
                str(self.DATA_LIST[i].segni_tafonomici_evidenti) if self.DATA_LIST[i].segni_tafonomici_evidenti else '',  # 26
                str(self.DATA_LIST[i].caratterizzazione_segni_tafonomici) if self.DATA_LIST[i].caratterizzazione_segni_tafonomici else '',  # 27
                str(self.DATA_LIST[i].stato_conservazione) if self.DATA_LIST[i].stato_conservazione else '',  # 28
                str(self.DATA_LIST[i].alterazioni_morfologiche) if self.DATA_LIST[i].alterazioni_morfologiche else '',  # 29
                str(self.DATA_LIST[i].note_terreno_giacitura) if self.DATA_LIST[i].note_terreno_giacitura else '',  # 30
                str(self.DATA_LIST[i].campionature_effettuate) if self.DATA_LIST[i].campionature_effettuate else '',  # 31
                str(self.DATA_LIST[i].affidabilita_stratigrafica) if self.DATA_LIST[i].affidabilita_stratigrafica else '',  # 32
                str(self.DATA_LIST[i].classi_reperti_associazione) if self.DATA_LIST[i].classi_reperti_associazione else '',  # 33
                str(self.DATA_LIST[i].osservazioni) if self.DATA_LIST[i].osservazioni else '',  # 34
                str(self.DATA_LIST[i].interpretazione) if self.DATA_LIST[i].interpretazione else ''  # 35
            ])
        return data_list

    # =====================================================
    # CRUD Helper Methods
    # =====================================================

    def data_error_check(self):
        """Check for data errors before save."""
        test = 0
        # Check required fields
        if not self.comboBox_sito.currentText():
            if self.L == 'it':
                QMessageBox.warning(self, "Attenzione", "Campo Sito obbligatorio", QMessageBox.StandardButton.Ok)
            elif self.L == 'de':
                QMessageBox.warning(self, "Achtung", "Feld Fundstelle ist erforderlich", QMessageBox.StandardButton.Ok)
            elif self.L == 'fr':
                QMessageBox.warning(self, "Attention", "Le champ Site est obligatoire", QMessageBox.StandardButton.Ok)
            elif self.L == 'es':
                QMessageBox.warning(self, "Atención", "Campo Sitio obligatorio", QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.warning(self, "Warning", "Site field is required", QMessageBox.StandardButton.Ok)
            test = 1
        return test

    def charge_records(self):
        """Load all records from database."""
        try:
            self.DATA_LIST = self.DB_MANAGER.query(self.MAPPER_TABLE_CLASS)
            if self.DATA_LIST:
                self.DATA_LIST_REC_TEMP = []
                for rec in self.DATA_LIST:
                    self.DATA_LIST_REC_TEMP.append(rec)
        except Exception as e:
            print(f"Error charging records: {str(e)}")
            self.DATA_LIST = []

    def records_equal_check(self):
        """Check if record has been modified."""
        self.set_LIST_REC_TEMP()
        self.set_LIST_REC_CORR()

        if self.DATA_LIST_REC_TEMP == self.DATA_LIST_REC_CORR:
            return 0
        else:
            return 1

    def set_LIST_REC_TEMP(self):
        """Store current form data for comparison."""
        # Get date string
        data_compilazione = self.dateEdit_compilazione.date().toString("yyyy-MM-dd") if self.dateEdit_compilazione.date().isValid() else ""

        self.DATA_LIST_REC_TEMP = [
            str(self.comboBox_sito.currentText()),  # sito
            str(self.comboBox_area.currentText()),  # area
            str(self.lineEdit_saggio.text()),  # saggio
            str(self.lineEdit_us.text()),  # us
            str(self.lineEdit_datazione_us.text()),  # datazione_us
            str(self.lineEdit_responsabile.text()),  # responsabile_scheda
            str(data_compilazione),  # data_compilazione
            str(self.lineEdit_doc_foto.text()),  # documentazione_fotografica
            str(self.comboBox_metodologia.currentText()),  # metodologia_recupero
            str(self.comboBox_contesto.currentText()),  # contesto
            str(self.textEdit_desc_contesto.toPlainText()),  # descrizione_contesto
            str(self.comboBox_connessione.currentText()),  # resti_connessione_anatomica
            str(self.comboBox_tipologia_accumulo.currentText()),  # tipologia_accumulo
            str(self.comboBox_deposizione.currentText()),  # deposizione
            str(self.lineEdit_num_stimato.text()),  # numero_stimato_resti
            str(self.spinBox_nmi.value()),  # numero_minimo_individui
            json.dumps(self.get_specie_psi_data()) if hasattr(self, 'tableWidget_specie_psi') else '',  # specie_psi
            json.dumps(self.get_misure_data()) if hasattr(self, 'tableWidget_misure') else '',  # misure_ossa
            str(self.comboBox_frammentazione.currentText()),  # stato_frammentazione
            str(self.comboBox_combustione.currentText()),  # tracce_combustione
            str(1 if self.checkBox_combustione_altri.isChecked() else 0),  # combustione_altri_materiali_us
            str(self.comboBox_tipo_combustione.currentText()),  # tipo_combustione
            str(self.comboBox_segni_tafonomici.currentText()),  # segni_tafonomici_evidenti
            str(self.comboBox_caratterizzazione.currentText()),  # caratterizzazione_segni_tafonomici
            str(self.comboBox_conservazione.currentText()),  # stato_conservazione
            str(self.textEdit_alterazioni.toPlainText()),  # alterazioni_morfologiche
            str(self.textEdit_note_terreno.toPlainText()),  # note_terreno_giacitura
            str(self.lineEdit_campionature.text()),  # campionature_effettuate
            str(self.comboBox_affidabilita.currentText()),  # affidabilita_stratigrafica
            str(self.lineEdit_classi_reperti.text()),  # classi_reperti_associazione
            str(self.textEdit_osservazioni.toPlainText()),  # osservazioni
            str(self.textEdit_interpretazione.toPlainText())  # interpretazione
        ]

    def set_LIST_REC_CORR(self):
        """Store current database record for comparison."""
        self.DATA_LIST_REC_CORR = []
        if self.DATA_LIST and self.REC_CORR < len(self.DATA_LIST):
            rec = self.DATA_LIST[self.REC_CORR]
            self.DATA_LIST_REC_CORR = [
                str(rec.sito) if rec.sito else '',
                str(rec.area) if rec.area else '',
                str(rec.saggio) if rec.saggio else '',
                str(rec.us) if rec.us else '',
                str(rec.datazione_us) if rec.datazione_us else '',
                str(rec.responsabile_scheda) if rec.responsabile_scheda else '',
                str(rec.data_compilazione) if rec.data_compilazione else '',
                str(rec.documentazione_fotografica) if rec.documentazione_fotografica else '',
                str(rec.metodologia_recupero) if rec.metodologia_recupero else '',
                str(rec.contesto) if rec.contesto else '',
                str(rec.descrizione_contesto) if rec.descrizione_contesto else '',
                str(rec.resti_connessione_anatomica) if rec.resti_connessione_anatomica else '',
                str(rec.tipologia_accumulo) if rec.tipologia_accumulo else '',
                str(rec.deposizione) if rec.deposizione else '',
                str(rec.numero_stimato_resti) if rec.numero_stimato_resti else '',
                str(rec.numero_minimo_individui) if rec.numero_minimo_individui else '0',
                str(getattr(rec, 'specie_psi', '') or ''),  # specie_psi
                str(getattr(rec, 'misure_ossa', '') or ''),  # misure_ossa
                str(rec.stato_frammentazione) if rec.stato_frammentazione else '',
                str(rec.tracce_combustione) if rec.tracce_combustione else '',
                str(rec.combustione_altri_materiali_us) if rec.combustione_altri_materiali_us else '0',
                str(rec.tipo_combustione) if rec.tipo_combustione else '',
                str(rec.segni_tafonomici_evidenti) if rec.segni_tafonomici_evidenti else '',
                str(rec.caratterizzazione_segni_tafonomici) if rec.caratterizzazione_segni_tafonomici else '',
                str(rec.stato_conservazione) if rec.stato_conservazione else '',
                str(rec.alterazioni_morfologiche) if rec.alterazioni_morfologiche else '',
                str(rec.note_terreno_giacitura) if rec.note_terreno_giacitura else '',
                str(rec.campionature_effettuate) if rec.campionature_effettuate else '',
                str(rec.affidabilita_stratigrafica) if rec.affidabilita_stratigrafica else '',
                str(rec.classi_reperti_associazione) if rec.classi_reperti_associazione else '',
                str(rec.osservazioni) if rec.osservazioni else '',
                str(rec.interpretazione) if rec.interpretazione else ''
            ]

    def update_if(self, msg):
        """Handle update confirmation."""
        if msg == QMessageBox.StandardButton.Ok:
            try:
                print(f"[Fauna DEBUG] update_if: REC_CORR={self.REC_CORR}, DATA_LIST length={len(self.DATA_LIST)}")

                # Ensure REC_CORR is within valid range
                if self.REC_CORR >= len(self.DATA_LIST):
                    self.REC_CORR = len(self.DATA_LIST) - 1
                    print(f"[Fauna DEBUG] update_if: Adjusted REC_CORR to {self.REC_CORR}")
                if self.REC_CORR < 0:
                    self.REC_CORR = 0

                id_to_update = int(self.DATA_LIST[self.REC_CORR].id_fauna)
                print(f"[Fauna DEBUG] update_if: id_to_update={id_to_update}")
                self.update_record(id_to_update)
                print(f"[Fauna DEBUG] update_if: update_record completed successfully")

                # Refresh data after successful update
                self.charge_records()
                print(f"[Fauna DEBUG] update_if: charge_records completed, DATA_LIST length={len(self.DATA_LIST)}")
                self.charge_list()
                print(f"[Fauna DEBUG] update_if: charge_list completed")

                # Restore position - ensure REC_CORR is still valid after refresh
                if self.REC_CORR >= len(self.DATA_LIST):
                    self.REC_CORR = len(self.DATA_LIST) - 1 if self.DATA_LIST else 0

                if self.DATA_LIST and self.REC_CORR < len(self.DATA_LIST):
                    self.fill_fields(self.REC_CORR)
                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                    print(f"[Fauna DEBUG] update_if: fill_fields completed for REC_CORR={self.REC_CORR}")

                if self.L == 'it':
                    QMessageBox.information(self, "Successo", "Record aggiornato correttamente")
                elif self.L == 'de':
                    QMessageBox.information(self, "Erfolg", "Datensatz erfolgreich aktualisiert")
                elif self.L == 'fr':
                    QMessageBox.information(self, "Succès", "Enregistrement mis à jour avec succès")
                elif self.L == 'es':
                    QMessageBox.information(self, "Éxito", "Registro actualizado correctamente")
                else:
                    QMessageBox.information(self, "Success", "Record updated successfully")

            except Exception as e:
                if self.L == 'it':
                    QMessageBox.critical(self, "Errore", f"Errore durante l'aggiornamento: {str(e)}")
                else:
                    QMessageBox.critical(self, "Error", f"Error during update: {str(e)}")

    def update_record(self, id_fauna):
        """Update record in database."""
        try:
            values = self.rec_toupdate()
            print(f"[Fauna DEBUG] update_record: id_fauna={id_fauna}")
            print(f"[Fauna DEBUG] update_record: TABLE_FIELDS count={len(self.TABLE_FIELDS)}")
            print(f"[Fauna DEBUG] update_record: values count={len(values)}")
            print(f"[Fauna DEBUG] update_record: TABLE_FIELDS={self.TABLE_FIELDS}")
            print(f"[Fauna DEBUG] update_record: values={values}")
            self.DB_MANAGER.update(self.MAPPER_TABLE_CLASS,
                                   self.ID_TABLE,
                                   [int(id_fauna)],
                                   self.TABLE_FIELDS,
                                   values)
            print(f"[Fauna DEBUG] update_record: DB_MANAGER.update completed")
        except Exception as e:
            print(f"[Fauna DEBUG] update_record: EXCEPTION={str(e)}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Update failed: {str(e)}")

    def rec_toupdate(self):
        """Return list of current field values for update."""
        import datetime

        # Get date as Python date object for SQLite compatibility
        data_compilazione = None
        if self.dateEdit_compilazione.date().isValid():
            qdate = self.dateEdit_compilazione.date()
            # Create Python date object (not datetime.datetime.date!)
            data_compilazione = datetime.date(qdate.year(), qdate.month(), qdate.day())

        return [
            None,  # id_us
            str(self.comboBox_sito.currentText()),  # sito
            str(self.comboBox_area.currentText()),  # area
            str(self.lineEdit_saggio.text()),  # saggio
            str(self.lineEdit_us.text()),  # us
            str(self.lineEdit_datazione_us.text()),  # datazione_us
            str(self.lineEdit_responsabile.text()),  # responsabile_scheda
            data_compilazione,  # data_compilazione
            str(self.lineEdit_doc_foto.text()),  # documentazione_fotografica
            str(self.comboBox_metodologia.currentText()),  # metodologia_recupero
            str(self.comboBox_contesto.currentText()),  # contesto
            str(self.textEdit_desc_contesto.toPlainText()),  # descrizione_contesto
            str(self.comboBox_connessione.currentText()),  # resti_connessione_anatomica
            str(self.comboBox_tipologia_accumulo.currentText()),  # tipologia_accumulo
            str(self.comboBox_deposizione.currentText()),  # deposizione
            str(self.lineEdit_num_stimato.text()),  # numero_stimato_resti
            int(self.spinBox_nmi.value()) if self.spinBox_nmi.value() else 0,  # numero_minimo_individui
            '',  # specie (deprecated)
            '',  # parti_scheletriche (deprecated)
            json.dumps(self.get_specie_psi_data()) if hasattr(self, 'tableWidget_specie_psi') else '',  # specie_psi
            json.dumps(self.get_misure_data()) if hasattr(self, 'tableWidget_misure') else '',  # misure_ossa
            str(self.comboBox_frammentazione.currentText()),  # stato_frammentazione
            str(self.comboBox_combustione.currentText()),  # tracce_combustione
            1 if self.checkBox_combustione_altri.isChecked() else 0,  # combustione_altri_materiali_us
            str(self.comboBox_tipo_combustione.currentText()),  # tipo_combustione
            str(self.comboBox_segni_tafonomici.currentText()),  # segni_tafonomici_evidenti
            str(self.comboBox_caratterizzazione.currentText()),  # caratterizzazione_segni_tafonomici
            str(self.comboBox_conservazione.currentText()),  # stato_conservazione
            str(self.textEdit_alterazioni.toPlainText()),  # alterazioni_morfologiche
            str(self.textEdit_note_terreno.toPlainText()),  # note_terreno_giacitura
            str(self.lineEdit_campionature.text()),  # campionature_effettuate
            str(self.comboBox_affidabilita.currentText()),  # affidabilita_stratigrafica
            str(self.lineEdit_classi_reperti.text()),  # classi_reperti_associazione
            str(self.textEdit_osservazioni.toPlainText()),  # osservazioni
            str(self.textEdit_interpretazione.toPlainText())  # interpretazione
        ]

    def insert_new_rec(self):
        """Insert new record into database."""
        import datetime

        try:
            # Get next ID
            if self.DB_MANAGER.query(self.MAPPER_TABLE_CLASS):
                id_fauna = self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, self.ID_TABLE) + 1
            else:
                id_fauna = 1

            # Get date as Python date object for SQLite compatibility
            data_compilazione = None
            if self.dateEdit_compilazione.date().isValid():
                qdate = self.dateEdit_compilazione.date()
                data_compilazione = datetime.date(qdate.year(), qdate.month(), qdate.day())

            # Create fauna record
            data = self.DB_MANAGER.insert_values_fauna(
                id_fauna,  # id_fauna
                None,  # id_us
                str(self.comboBox_sito.currentText()),  # sito
                str(self.comboBox_area.currentText()),  # area
                str(self.lineEdit_saggio.text()),  # saggio
                str(self.lineEdit_us.text()),  # us
                str(self.lineEdit_datazione_us.text()),  # datazione_us
                str(self.lineEdit_responsabile.text()),  # responsabile_scheda
                data_compilazione,  # data_compilazione
                str(self.lineEdit_doc_foto.text()),  # documentazione_fotografica
                str(self.comboBox_metodologia.currentText()),  # metodologia_recupero
                str(self.comboBox_contesto.currentText()),  # contesto
                str(self.textEdit_desc_contesto.toPlainText()),  # descrizione_contesto
                str(self.comboBox_connessione.currentText()),  # resti_connessione_anatomica
                str(self.comboBox_tipologia_accumulo.currentText()),  # tipologia_accumulo
                str(self.comboBox_deposizione.currentText()),  # deposizione
                str(self.lineEdit_num_stimato.text()),  # numero_stimato_resti
                int(self.spinBox_nmi.value()) if self.spinBox_nmi.value() else 0,  # numero_minimo_individui
                '',  # specie (deprecated, kept for compatibility)
                '',  # parti_scheletriche (deprecated, kept for compatibility)
                json.dumps(self.get_specie_psi_data()) if hasattr(self, 'tableWidget_specie_psi') else '',  # specie_psi
                json.dumps(self.get_misure_data()) if hasattr(self, 'tableWidget_misure') else '',  # misure_ossa
                str(self.comboBox_frammentazione.currentText()),  # stato_frammentazione
                str(self.comboBox_combustione.currentText()),  # tracce_combustione
                1 if self.checkBox_combustione_altri.isChecked() else 0,  # combustione_altri_materiali_us
                str(self.comboBox_tipo_combustione.currentText()),  # tipo_combustione
                str(self.comboBox_segni_tafonomici.currentText()),  # segni_tafonomici_evidenti
                str(self.comboBox_caratterizzazione.currentText()),  # caratterizzazione_segni_tafonomici
                str(self.comboBox_conservazione.currentText()),  # stato_conservazione
                str(self.textEdit_alterazioni.toPlainText()),  # alterazioni_morfologiche
                str(self.textEdit_note_terreno.toPlainText()),  # note_terreno_giacitura
                str(self.lineEdit_campionature.text()),  # campionature_effettuate
                str(self.comboBox_affidabilita.currentText()),  # affidabilita_stratigrafica
                str(self.lineEdit_classi_reperti.text()),  # classi_reperti_associazione
                str(self.textEdit_osservazioni.toPlainText()),  # osservazioni
                str(self.textEdit_interpretazione.toPlainText())  # interpretazione
            )

            self.DB_MANAGER.insert_data_session(data)
            return 1

        except Exception as e:
            e_str = str(e)
            if "IntegrityError" in e_str:
                if "UNIQUE constraint" in e_str or "duplicate key" in e_str:
                    if self.L == 'it':
                        QMessageBox.warning(self, "Errore", "Record già esistente nel database",
                                          QMessageBox.StandardButton.Ok)
                    elif self.L == 'de':
                        QMessageBox.warning(self, "Fehler", "Datensatz existiert bereits in der Datenbank",
                                          QMessageBox.StandardButton.Ok)
                    elif self.L == 'fr':
                        QMessageBox.warning(self, "Erreur", "L'enregistrement existe déjà dans la base de données",
                                          QMessageBox.StandardButton.Ok)
                    elif self.L == 'es':
                        QMessageBox.warning(self, "Error", "El registro ya existe en la base de datos",
                                          QMessageBox.StandardButton.Ok)
                    else:
                        QMessageBox.warning(self, "Error", "Record already exists in database",
                                          QMessageBox.StandardButton.Ok)
            else:
                if self.L == 'it':
                    QMessageBox.warning(self, "Errore", f"Errore durante l'inserimento: {e_str}",
                                      QMessageBox.StandardButton.Ok)
                else:
                    QMessageBox.warning(self, "Error", f"Error during insert: {e_str}",
                                      QMessageBox.StandardButton.Ok)
            return 0
