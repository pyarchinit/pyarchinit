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
from qgis.PyQt.QtGui import QIcon
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
from ..modules.db.pyarchinit_db_manager import Pyarchinit_db_management
from ..modules.db.pyarchinit_utility import Utility
from ..modules.utility.pyarchinit_error_check import Error_check
from ..gui.pyarchinitConfigDialog import pyArchInitDialog_Config


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
            QMessageBox.warning(self, "Database Error",
                f"Could not connect to database: {str(e)}\nPlease check your configuration.")

        # Setup UI
        self.setup_ui()

        # Load initial data
        self.charge_list()
        self.fill_fields()

    def connect_to_db(self):
        """Connect to the pyArchInit database."""
        conn = Connection()
        conn_str = conn.conn_str()

        try:
            self.DB_MANAGER = Pyarchinit_db_management(conn_str)
            self.DB_SERVER = conn.db_server_key
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

        self.comboBox_sito = QComboBox()
        self.comboBox_sito.setEditable(True)
        form_id.addRow(self.tr("Sito") + " *:", self.comboBox_sito)

        self.comboBox_area = QComboBox()
        self.comboBox_area.setEditable(True)
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
            QMessageBox.warning(self, "Error", "Database not connected")
            return

        # TODO: Implement save logic
        QMessageBox.information(self, "Info", "Save functionality to be implemented")

    def on_pushButton_delete_pressed(self):
        """Delete current record."""
        if not self.DB_MANAGER:
            QMessageBox.warning(self, "Error", "Database not connected")
            return

        # TODO: Implement delete logic
        QMessageBox.information(self, "Info", "Delete functionality to be implemented")

    def on_pushButton_view_all_pressed(self):
        """Load all records."""
        if not self.DB_MANAGER:
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
                QMessageBox.information(self, "Info", self.tr("No records found"))
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error loading records: {str(e)}")
