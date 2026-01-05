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


class pyarchinit_Fauna(QDialog):
    """
    Fauna form for SCHEDA FR (Fauna Record Sheet).

    This module provides:
    - Data entry and management for fauna/archaeozoological data
    - Integration with pyArchInit database
    - Support for both SQLite and PostgreSQL
    """

    L = QgsSettings().value("locale/userLocale", "it")[0:2]

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
    else:
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
        self.comboBox_metodologia.addItems(["", "A MANO", "SETACCIO", "FLOTTAZIONE"])
        form_dep.addRow(self.tr("Metodologia Recupero") + ":", self.comboBox_metodologia)

        self.comboBox_contesto = QComboBox()
        self.comboBox_contesto.setEditable(True)
        self.comboBox_contesto.addItems(["", "FUNERARIO", "ABITATIVO", "PRODUTTIVO", "IPOGEO", "CULTUALE", "ALTRO"])
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
        self.comboBox_connessione.addItems(["", "SI", "NO", "PARZIALE"])
        form.addRow(self.tr("Connessione Anatomica") + ":", self.comboBox_connessione)

        self.comboBox_tipologia_accumulo = QComboBox()
        self.comboBox_tipologia_accumulo.setEditable(True)
        form.addRow(self.tr("Tipologia Accumulo") + ":", self.comboBox_tipologia_accumulo)

        self.comboBox_deposizione = QComboBox()
        self.comboBox_deposizione.setEditable(True)
        self.comboBox_deposizione.addItems(["", "PRIMARIA", "SECONDARIA", "RIMANEGGIATA"])
        form.addRow(self.tr("Deposizione") + ":", self.comboBox_deposizione)

        self.lineEdit_num_stimato = QLineEdit()
        form.addRow(self.tr("Numero Stimato Resti") + ":", self.lineEdit_num_stimato)

        self.spinBox_nmi = QSpinBox()
        self.spinBox_nmi.setMaximum(9999)
        form.addRow("NMI:", self.spinBox_nmi)

        self.comboBox_specie = QComboBox()
        self.comboBox_specie.setEditable(True)
        form.addRow(self.tr("Specie") + ":", self.comboBox_specie)

        self.lineEdit_parti_scheletriche = QLineEdit()
        form.addRow(self.tr("Parti Scheletriche") + ":", self.lineEdit_parti_scheletriche)

        layout.addLayout(form)
        layout.addStretch()

        return widget

    def create_tab_tafonomici(self) -> QWidget:
        """Create the taphonomic data tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        form = QFormLayout()

        self.comboBox_frammentazione = QComboBox()
        self.comboBox_frammentazione.setEditable(True)
        self.comboBox_frammentazione.addItems(["", "SI", "NO", "PARZIALE"])
        form.addRow(self.tr("Stato Frammentazione") + ":", self.comboBox_frammentazione)

        self.comboBox_combustione = QComboBox()
        self.comboBox_combustione.setEditable(True)
        self.comboBox_combustione.addItems(["", "SI", "NO", "SCARSE", "DIFFUSE"])
        form.addRow(self.tr("Tracce Combustione") + ":", self.comboBox_combustione)

        self.checkBox_combustione_altri = QCheckBox()
        form.addRow(self.tr("Combustione Altri Materiali US") + ":", self.checkBox_combustione_altri)

        self.comboBox_tipo_combustione = QComboBox()
        self.comboBox_tipo_combustione.setEditable(True)
        self.comboBox_tipo_combustione.addItems(["", "ACCIDENTALE", "INTENZIONALE", "NATURALE", "ANTROPICA"])
        form.addRow(self.tr("Tipo Combustione") + ":", self.comboBox_tipo_combustione)

        self.comboBox_segni_tafonomici = QComboBox()
        self.comboBox_segni_tafonomici.setEditable(True)
        self.comboBox_segni_tafonomici.addItems(["", "SI", "NO", "SCARSI", "DIFFUSI"])
        form.addRow(self.tr("Segni Tafonomici") + ":", self.comboBox_segni_tafonomici)

        self.comboBox_caratterizzazione = QComboBox()
        self.comboBox_caratterizzazione.setEditable(True)
        self.comboBox_caratterizzazione.addItems(["", "ANTROPICA", "NATURALE"])
        form.addRow(self.tr("Caratterizzazione") + ":", self.comboBox_caratterizzazione)

        self.comboBox_conservazione = QComboBox()
        self.comboBox_conservazione.setEditable(True)
        self.comboBox_conservazione.addItems(["", "0", "1", "2", "3", "4", "5"])
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
        lang_mapping = {
            'it': "'it_IT'",
            'de': "'de_DE'",
            'en': "'en_US'",
            'es': "'es_ES'",
            'fr': "'fr_FR'",
            'ar': "'ar_LB'",
            'ca': "'ca_ES'"
        }
        lang = lang_mapping.get(self.L, "'en_US'")

        # Helper function to load thesaurus values
        def load_thesaurus(tipologia_sigla, use_sigla=False):
            search_dict = {
                'lingua': lang,
                'nome_tabella': "'fauna_table'",
                'tipologia_sigla': "'" + tipologia_sigla + "'"
            }
            try:
                thesaurus_data = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
                values = []
                for item in thesaurus_data:
                    if use_sigla:
                        val = item.sigla.strip() if item.sigla else ''
                    else:
                        val = item.sigla_estesa.strip() if item.sigla_estesa else ''
                    if val and val not in values:
                        values.append(val)
                values.sort()
                return values
            except Exception as e:
                # If thesaurus table doesn't exist or other error, return empty list
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

        if self.comboBox_specie.currentText():
            search_dict['specie'] = "'" + self.comboBox_specie.currentText() + "'"

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
            self.comboBox_specie.setEditText(str(rec.specie) if rec.specie else "")
            self.lineEdit_parti_scheletriche.setText(str(rec.parti_scheletriche) if rec.parti_scheletriche else "")

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
        """Update record counter display."""
        self.REC_TOT = t
        self.REC_CORR = c
        self.label_rec_tot.setText(str(self.REC_TOT))
        self.label_rec_corrente.setText(str(self.REC_CORR))

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
        self.comboBox_specie.setEditText("")
        self.lineEdit_parti_scheletriche.clear()

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

    def update_statistics(self):
        """Calculate and display comprehensive statistics."""
        try:
            records = self.get_all_fauna_records()

            if not records:
                no_data_msg = {
                    'it': "Nessun record presente nel database.",
                    'de': "Keine Datensätze in der Datenbank.",
                    'fr': "Aucun enregistrement dans la base de données.",
                    'es': "No hay registros en la base de datos.",
                    'en': "No records in the database."
                }
                self.txt_statistiche.setText(no_data_msg.get(self.L, no_data_msg['en']))
                return

            stats_text = []
            stats_text.append("=" * 100)
            stats_text.append("STATISTICHE RIEPILOGATIVE - SCHEDE FAUNA")
            stats_text.append("=" * 100)
            stats_text.append("")

            # === GENERAL STATISTICS ===
            stats_text.append("STATISTICHE GENERALI")
            stats_text.append("-" * 100)
            stats_text.append(f"Numero totale record: {len(records)}")

            siti = set(r.get('sito', '') for r in records if r.get('sito'))
            aree = set(r.get('area', '') for r in records if r.get('area'))
            saggi = set(r.get('saggio', '') for r in records if r.get('saggio'))
            us_list = set(r.get('us', '') for r in records if r.get('us'))

            stats_text.append(f"Numero siti univoci: {len(siti)}")
            if siti:
                stats_text.append(f"  Siti: {', '.join(sorted(str(s) for s in siti))}")
            stats_text.append(f"Numero aree univoche: {len(aree)}")
            stats_text.append(f"Numero saggi univoci: {len(saggi)}")
            stats_text.append(f"Numero US univoche: {len(us_list)}")

            # Unique combinations
            combinazioni = set()
            for r in records:
                sito = r.get('sito', '')
                area = r.get('area', '')
                saggio = r.get('saggio', '')
                us = r.get('us', '')
                if sito and area and saggio and us:
                    combinazioni.add((sito, area, saggio, us))
            stats_text.append(f"Numero combinazioni Sito+Area+Saggio+US univoche: {len(combinazioni)}")
            stats_text.append("")

            # === NUMERIC STATISTICS ===
            stats_text.append("STATISTICHE NUMERICHE - RIEPILOGO GENERALE")
            stats_text.append("-" * 100)

            nmi_values = [int(r['numero_minimo_individui']) for r in records
                         if r.get('numero_minimo_individui') not in (None, '', 0)]
            if nmi_values:
                stats_text.append(f"Numero Minimo Individui (NMI):")
                stats_text.append(f"  Totale record con NMI: {len(nmi_values)}")
                stats_text.append(f"  Media: {sum(nmi_values)/len(nmi_values):.1f}")
                stats_text.append(f"  Minimo: {min(nmi_values)}")
                stats_text.append(f"  Massimo: {max(nmi_values)}")
                stats_text.append(f"  Somma totale: {sum(nmi_values)}")

            # Skeletal Parts (PSI) distribution
            all_psi = {}
            for r in records:
                psi_list = self._extract_psi_from_record(r)
                for psi in psi_list:
                    if psi:
                        all_psi[psi] = all_psi.get(psi, 0) + 1

            if all_psi:
                stats_text.append(f"\nParti Scheletriche (PSI) - Distribuzione:")
                stats_text.append(f"  Totale parti identificate: {sum(all_psi.values())}")
                stats_text.append(f"  Tipi di parti univoche: {len(all_psi)}")
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
                stats_text.append(f"\nMisure Ossa (mm) - Riepilogo:")
                stats_text.append(f"  Totale misurazioni: {len(misure_values)}")
                stats_text.append(f"  Media: {sum(misure_values)/len(misure_values):.2f} mm")
                stats_text.append(f"  Minimo: {min(misure_values):.2f} mm")
                stats_text.append(f"  Massimo: {max(misure_values):.2f} mm")

            stats_text.append("")

            # === STATISTICS BY SITE ===
            if siti and len(siti) > 0:
                stats_text.append("STATISTICHE PER SITO")
                stats_text.append("=" * 100)

                for sito in sorted(str(s) for s in siti):
                    sito_records = [r for r in records if str(r.get('sito', '')) == sito]
                    sito_pct = (len(sito_records) / len(records)) * 100

                    stats_text.append(f"\n{'#' * 100}")
                    stats_text.append(f"SITO: {sito}")
                    stats_text.append(f"{'#' * 100}")
                    stats_text.append(f"Totale record: {len(sito_records)} ({sito_pct:.1f}% del totale generale)")

                    # Areas, trenches, SU in the site
                    sito_aree = set(r.get('area', '') for r in sito_records if r.get('area'))
                    sito_saggi = set(r.get('saggio', '') for r in sito_records if r.get('saggio'))
                    sito_us = set(r.get('us', '') for r in sito_records if r.get('us'))

                    stats_text.append(f"Numero aree: {len(sito_aree)}")
                    stats_text.append(f"Numero saggi: {len(sito_saggi)}")
                    stats_text.append(f"Numero US: {len(sito_us)}")

                    # Main species in the site
                    sito_species = {}
                    for r in sito_records:
                        species_list = self._extract_species_from_record(r)
                        for sp in species_list:
                            if sp:
                                sito_species[sp] = sito_species.get(sp, 0) + 1

                    if sito_species:
                        top_species = sorted(sito_species.items(), key=lambda x: x[1], reverse=True)[:5]
                        stats_text.append(f"\nSpecie principali:")
                        for sp, cnt in top_species:
                            sp_pct = (cnt / len(sito_records)) * 100
                            stats_text.append(f"  - {sp}: {cnt} record ({sp_pct:.1f}%)")

                    # NMI total for site
                    sito_nmi = [int(r['numero_minimo_individui']) for r in sito_records
                               if r.get('numero_minimo_individui') not in (None, '', 0)]
                    if sito_nmi:
                        stats_text.append(f"\nNMI totale sito: {sum(sito_nmi)}")
                        stats_text.append(f"NMI medio: {sum(sito_nmi)/len(sito_nmi):.1f}")

                    # PSI for site
                    sito_psi = {}
                    for r in sito_records:
                        psi_list = self._extract_psi_from_record(r)
                        for psi in psi_list:
                            if psi:
                                sito_psi[psi] = sito_psi.get(psi, 0) + 1
                    if sito_psi:
                        top_psi = sorted(sito_psi.items(), key=lambda x: x[1], reverse=True)[:5]
                        stats_text.append(f"\nParti scheletriche principali:")
                        for psi, cnt in top_psi:
                            stats_text.append(f"  - {psi}: {cnt}")

                stats_text.append(f"\n{'=' * 100}\n")

            # === DISTRIBUTION BY CATEGORIES ===
            stats_text.append("DISTRIBUZIONE PER CATEGORIE - RIEPILOGO GENERALE")
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
                    stats_text.append(f"\n{label}: Nessun dato")

            # Species
            all_species = {}
            for r in records:
                species_list = self._extract_species_from_record(r)
                for sp in species_list:
                    if sp and str(sp).strip():
                        all_species[sp] = all_species.get(sp, 0) + 1
            if all_species:
                stats_text.append(f"\nSpecie (Top 10):")
                sorted_species = sorted(all_species.items(), key=lambda x: x[1], reverse=True)
                for val, count in sorted_species[:10]:
                    percentage = (count / len(records)) * 100
                    stats_text.append(f"  {val}: {count} ({percentage:.1f}%)")
            else:
                stats_text.append(f"\nSpecie (Top 10): Nessun dato")

            count_values('contesto', 'Contesto')
            count_values('stato_conservazione', 'Stato di Conservazione')
            count_values('tracce_combustione', 'Tracce di Combustione')
            count_values('stato_frammentazione', 'Stato di Frammentazione')
            count_values('resti_connessione_anatomica', 'Resti in Connessione Anatomica')

            stats_text.append("")

            # === DESCRIPTIVE SUMMARY ===
            stats_text.append("=" * 100)
            stats_text.append("SOMMARIO DESCRITTIVO")
            stats_text.append("=" * 100)
            stats_text.append("")

            summary = self._generate_descriptive_summary(records, nmi_values, misure_values,
                                                        siti, aree, saggi, us_list)
            stats_text.extend(summary)

            stats_text.append("")
            stats_text.append("=" * 100)
            stats_text.append(f"Report generato il: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
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
            error_msg = f"Errore nel calcolo delle statistiche:\n{str(e)}" if self.L == 'it' else f"Error calculating statistics:\n{str(e)}"
            QMessageBox.critical(self, "Errore" if self.L == 'it' else "Error", error_msg)
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

    def _generate_descriptive_summary(self, records, nmi_values, misure_values, siti, aree, saggi, us_list):
        """Generate a descriptive summary of the statistics."""
        summary = []

        # Introduction
        summary.append(f"L'analisi del dataset faunistico comprende {len(records)} record archeologici ")
        summary.append(f"distribuiti su {len(siti)} siti, {len(aree)} aree, {len(saggi)} saggi e {len(us_list)} unita stratigrafiche.")
        summary.append("")

        # Analysis by site
        if len(siti) > 0:
            summary.append("DISTRIBUZIONE PER SITO:")
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

                summary.append(f"Il sito piu rappresentato e '{dominant_site[0]}' con {len(dominant_site[1])} record ({pct:.1f}% del totale).")

                if len(siti) > 1:
                    summary.append(f"Gli altri {len(siti) - 1} siti contribuiscono con il restante {100 - pct:.1f}% dei dati.")

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
            summary.append("ANALISI DELLE SPECIE:")
            summary.append(f"Sono state identificate {len(species_count)} specie diverse. Le specie predominanti sono:")

            for sp, count in top_3_species:
                pct = (count / len(records)) * 100
                summary.append(f"  - {sp}: presente in {count} record ({pct:.1f}% del totale)")

            summary.append("")

        # NMI analysis
        if nmi_values:
            total_nmi = sum(nmi_values)
            avg_nmi = total_nmi / len(nmi_values)
            summary.append("NUMERO MINIMO DI INDIVIDUI (NMI):")
            summary.append(f"Il numero minimo totale di individui e {total_nmi}, con una media di {avg_nmi:.1f} individui ")
            summary.append(f"per record. Il valore minimo registrato e {min(nmi_values)}, mentre il massimo e {max(nmi_values)}.")
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
            summary.append("CONTESTI ARCHEOLOGICI:")
            summary.append(f"Il contesto prevalente e '{dominant_context[0]}' con {dominant_context[1]} occorrenze ")
            summary.append(f"({pct:.1f}% del totale).")
            summary.append("")

        # Conclusion
        summary.append("CONCLUSIONI:")
        summary.append("Il dataset rappresenta un campione significativo per l'analisi archeozoologica del sito.")
        summary.append("I dati raccolti permettono di ricostruire aspetti legati all'economia, all'alimentazione e ")
        summary.append("alle pratiche cultuali delle popolazioni antiche che hanno abitato l'area.")

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
            Fauna_pdf_sheet = generate_fauna_pdf()
            data_list = self.generate_list_pdf()

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

            msg = "Esportazione schede completata" if self.L == 'it' else "Sheet export completed"
            QMessageBox.information(self, "Successo" if self.L == 'it' else "Success", msg)

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
            str(self.comboBox_specie.currentText()),  # specie
            str(self.lineEdit_parti_scheletriche.text()),  # parti_scheletriche
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
                str(rec.specie) if rec.specie else '',
                str(rec.parti_scheletriche) if rec.parti_scheletriche else '',
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
                id_to_update = int(self.DATA_LIST[self.REC_CORR].id_fauna)
                self.update_record(id_to_update)

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
        # Get date
        data_compilazione = self.dateEdit_compilazione.date().toString("yyyy-MM-dd") if self.dateEdit_compilazione.date().isValid() else None

        search_dict = {self.ID_TABLE: "'" + str(id_fauna) + "'"}

        update_dict = {
            'sito': str(self.comboBox_sito.currentText()),
            'area': str(self.comboBox_area.currentText()),
            'saggio': str(self.lineEdit_saggio.text()),
            'us': str(self.lineEdit_us.text()),
            'datazione_us': str(self.lineEdit_datazione_us.text()),
            'responsabile_scheda': str(self.lineEdit_responsabile.text()),
            'data_compilazione': data_compilazione,
            'documentazione_fotografica': str(self.lineEdit_doc_foto.text()),
            'metodologia_recupero': str(self.comboBox_metodologia.currentText()),
            'contesto': str(self.comboBox_contesto.currentText()),
            'descrizione_contesto': str(self.textEdit_desc_contesto.toPlainText()),
            'resti_connessione_anatomica': str(self.comboBox_connessione.currentText()),
            'tipologia_accumulo': str(self.comboBox_tipologia_accumulo.currentText()),
            'deposizione': str(self.comboBox_deposizione.currentText()),
            'numero_stimato_resti': str(self.lineEdit_num_stimato.text()),
            'numero_minimo_individui': int(self.spinBox_nmi.value()) if self.spinBox_nmi.value() else 0,
            'specie': str(self.comboBox_specie.currentText()),
            'parti_scheletriche': str(self.lineEdit_parti_scheletriche.text()),
            'stato_frammentazione': str(self.comboBox_frammentazione.currentText()),
            'tracce_combustione': str(self.comboBox_combustione.currentText()),
            'combustione_altri_materiali_us': 1 if self.checkBox_combustione_altri.isChecked() else 0,
            'tipo_combustione': str(self.comboBox_tipo_combustione.currentText()),
            'segni_tafonomici_evidenti': str(self.comboBox_segni_tafonomici.currentText()),
            'caratterizzazione_segni_tafonomici': str(self.comboBox_caratterizzazione.currentText()),
            'stato_conservazione': str(self.comboBox_conservazione.currentText()),
            'alterazioni_morfologiche': str(self.textEdit_alterazioni.toPlainText()),
            'note_terreno_giacitura': str(self.textEdit_note_terreno.toPlainText()),
            'campionature_effettuate': str(self.lineEdit_campionature.text()),
            'affidabilita_stratigrafica': str(self.comboBox_affidabilita.currentText()),
            'classi_reperti_associazione': str(self.lineEdit_classi_reperti.text()),
            'osservazioni': str(self.textEdit_osservazioni.toPlainText()),
            'interpretazione': str(self.textEdit_interpretazione.toPlainText())
        }

        u = Utility()
        update_dict = u.remove_empty_items_fr_dict(update_dict)
        self.DB_MANAGER.update(self.MAPPER_TABLE_CLASS, search_dict, update_dict)

    def insert_new_rec(self):
        """Insert new record into database."""
        try:
            # Get next ID
            if self.DB_MANAGER.query(self.MAPPER_TABLE_CLASS):
                id_fauna = self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, self.ID_TABLE) + 1
            else:
                id_fauna = 1

            # Get date
            data_compilazione = self.dateEdit_compilazione.date().toString("yyyy-MM-dd") if self.dateEdit_compilazione.date().isValid() else None

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
                str(self.comboBox_specie.currentText()),  # specie
                str(self.lineEdit_parti_scheletriche.text()),  # parti_scheletriche
                '',  # specie_psi
                '',  # misure_ossa
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
