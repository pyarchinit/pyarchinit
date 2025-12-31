#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
/***************************************************************************
    pyArchInit Plugin - Archaeological GIS Tools
    Archeozoology Module - Zooarchaeological Quantification Analysis
    -------------------
    begin                : 2010-12-01
    copyright            : (C) 2008-2024 by Enzo Cocca
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
from datetime import date

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import (
    QDialog, QMessageBox, QTableWidgetItem, QFileDialog, QApplication
)
from qgis.PyQt.uic import loadUiType
from qgis.core import QgsSettings

from ..modules.utility.pyarchinit_OS_utility import Pyarchinit_OS_Utility
from ..modules.db.pyarchinit_conn_strings import Connection
from ..modules.db.pyarchinit_db_manager import Pyarchinit_db_management
from ..modules.db.concurrency_manager import ConcurrencyManager, RecordLockIndicator
from ..modules.db.pyarchinit_utility import Utility
from ..modules.gis.pyarchinit_pyqgis_archeozoo import Pyarchinit_pyqgis
from ..modules.utility.pyarchinit_error_check import Error_check
from ..gui.sortpanelmain import SortPanelMain
from ..gui.pyarchinitConfigDialog import pyArchInitDialog_Config

# Import R integration module
try:
    from ..modules.r_integration.r_session_manager import RSessionManager
    from ..modules.r_integration.archeozoo_r_analysis import ArcheozooRAnalysis
    R_AVAILABLE = True
except ImportError:
    R_AVAILABLE = False

# Load UI from file
MAIN_DIALOG_CLASS, _ = loadUiType(
    os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'Archeozoology.ui'))


class pyarchinit_Archeozoology(QDialog, MAIN_DIALOG_CLASS):
    """
    Archeozoology form for zooarchaeological quantification analysis.

    This module provides:
    - Data entry and management for archeozoological quantification data
    - Geostatistical analysis using R (semivariograms, kriging)
    - Statistical visualizations (histograms, boxplots, coplots)
    - Integration with QGIS for spatial visualization
    """

    L = QgsSettings().value("locale/userLocale", "it")[0:2]

    MSG_BOX_TITLE = "PyArchInit - Scheda Archeozoologia Quantificazioni"

    DATA_LIST = []
    DATA_LIST_REC_CORR = []
    DATA_LIST_REC_TEMP = []
    REC_CORR = 0
    REC_TOT = 0

    STATUS_ITEMS = {"b": "Usa", "f": "Trova", "n": "Nuovo Record"}
    BROWSE_STATUS = "b"
    SORT_MODE = 'asc'
    SORTED_ITEMS = {"n": "Non ordinati", "o": "Ordinati"}
    SORT_STATUS = "n"

    UTILITY = Utility()
    DB_MANAGER = ""
    TABLE_NAME = 'archeozoology_table'
    MAPPER_TABLE_CLASS = "ARCHEOZOOLOGY"
    NOME_SCHEDA = "Scheda Archeozoologia"
    ID_TABLE = "id_archzoo"

    # Field mapping
    CONVERSION_DICT = {
        ID_TABLE: ID_TABLE,
        "Sito": "sito",
        "Area": "area",
        "US": "us",
        "Quadrato": "quadrato",
        "Coord X": "coord_x",
        "Coord Y": "coord_y",
        "Coord Z": "coord_z",
        "Bos/Bison": "bos_bison",
        "Calcinati": "calcinati",
        "Camoscio": "camoscio",
        "Capriolo": "capriolo",
        "Cervo": "cervo",
        "Combusto": "combusto",
        "Coni": "coni",
        "PDI": "pdi",
        "Stambecco": "stambecco",
        "Strie": "strie",
        "Canidi": "canidi",
        "Ursidi": "ursidi",
        "Megacero": "megacero"
    }

    SORT_ITEMS = [
        ID_TABLE,
        "Sito",
        "Area",
        "US",
        "Quadrato",
        "Coord X",
        "Coord Y",
        "Coord Z",
        "Bos/Bison",
        "Calcinati",
        "Camoscio",
        "Capriolo",
        "Cervo",
        "Combusto",
        "Coni",
        "PDI",
        "Stambecco",
        "Strie",
        "Canidi",
        "Ursidi",
        "Megacero"
    ]

    TABLE_FIELDS = [
        "sito",
        "area",
        "us",
        "quadrato",
        "coord_x",
        "coord_y",
        "coord_z",
        "bos_bison",
        "calcinati",
        "camoscio",
        "capriolo",
        "cervo",
        "combusto",
        "coni",
        "pdi",
        "stambecco",
        "strie",
        "canidi",
        "ursidi",
        "megacero"
    ]

    # Numeric fields for analysis
    NUMERIC_FIELDS = [
        "bos_bison", "calcinati", "camoscio", "capriolo", "cervo",
        "combusto", "coni", "pdi", "stambecco", "strie",
        "canidi", "ursidi", "megacero"
    ]

    def __init__(self, iface):
        """Initialize the Archeozoology form."""
        super(pyarchinit_Archeozoology, self).__init__()
        self.iface = iface
        self.pyQGIS = Pyarchinit_pyqgis(self.iface)
        self.setupUi(self)
        self.currentLayerId = None

        # Initialize R integration
        self.r_analysis = None
        if R_AVAILABLE:
            try:
                self.r_analysis = ArcheozooRAnalysis()
                self._setup_r_buttons()
            except Exception as e:
                print(f"R integration error: {e}")

        # Disable R buttons if R not available
        if not R_AVAILABLE or self.r_analysis is None or not self.r_analysis.is_r_available():
            self._disable_r_buttons()

        # Connect to database
        try:
            self.on_pushButton_connect_pressed()
        except Exception as e:
            QMessageBox.warning(self, "Connection Error", str(e), QMessageBox.Ok)

        # Setup UI
        self.fill_fields()
        self.customize_GUI()
        self.set_sito()
        self.msg_sito()

    def _setup_r_buttons(self):
        """Setup R analysis button connections."""
        # Connect R analysis buttons if they exist in the UI
        buttons_methods = {
            'pushButton_calcola': self.on_calcola_pressed,
            'pushButton_automap': self.on_automap_pressed,
            'pushButton_hist': self.on_hist_pressed,
            'pushButton_boxplot': self.on_boxplot_pressed,
            'pushButton_coplot': self.on_coplot_pressed,
            'pushButton_matrix': self.on_matrix_pressed,
            'pushButton_report': self.on_report_pressed,
        }

        for btn_name, method in buttons_methods.items():
            btn = getattr(self, btn_name, None)
            if btn:
                btn.clicked.connect(method)

    def _disable_r_buttons(self):
        """Disable R analysis buttons when R is not available."""
        r_buttons = [
            'pushButton_calcola', 'pushButton_automap', 'pushButton_hist',
            'pushButton_boxplot', 'pushButton_coplot', 'pushButton_matrix',
            'pushButton_report'
        ]

        tooltip = self.tr("R not available. Install R and PyPER to enable statistical analysis.")

        for btn_name in r_buttons:
            btn = getattr(self, btn_name, None)
            if btn:
                btn.setEnabled(False)
                btn.setToolTip(tooltip)

    def customize_GUI(self):
        """Customize the GUI elements."""
        # Set window properties
        self.setWindowTitle(self.MSG_BOX_TITLE)

        # Populate site combobox
        sito_values = self.charge_list()
        if sito_values:
            self.comboBox_sito.addItems(sito_values)

    def charge_list(self):
        """Load site list from database."""
        try:
            search_dict = {}
            sito_list = self.DB_MANAGER.query_distinct('SITE', search_dict)
            return [str(item.sito) for item in sito_list]
        except:
            return []

    def set_sito(self):
        """Set the current site from settings."""
        try:
            self.comboBox_sito.setEditText(str(self.DB_MANAGER.get_config_value('sito')))
        except:
            pass

    def msg_sito(self):
        """Show site configuration message if needed."""
        try:
            sito = str(self.comboBox_sito.currentText())
            if not sito:
                QMessageBox.warning(
                    self, "Attenzione",
                    self.tr("Please configure a site first."),
                    QMessageBox.Ok
                )
        except:
            pass

    def on_pushButton_connect_pressed(self):
        """Connect to database."""
        conn = Connection()
        conn_str = conn.conn_str()

        try:
            self.DB_MANAGER = Pyarchinit_db_management(conn_str)
            self.DB_MANAGER.connection()
            self.charge_records()
            self.BROWSE_STATUS = "b"
            self.label_status.setText("Connected")
        except Exception as e:
            QMessageBox.critical(
                self, "Database Error",
                f"Connection failed: {str(e)}",
                QMessageBox.Ok
            )

    def charge_records(self):
        """Load all records from database."""
        try:
            self.DATA_LIST = self.DB_MANAGER.query(self.MAPPER_TABLE_CLASS)
            self.REC_TOT = len(self.DATA_LIST)
            self.REC_CORR = 0
            if self.REC_TOT > 0:
                self.fill_fields()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e), QMessageBox.Ok)

    def fill_fields(self, n=0):
        """Fill form fields with record data."""
        if not self.DATA_LIST:
            return

        try:
            rec = self.DATA_LIST[n]

            self.comboBox_sito.setEditText(str(rec.sito) if rec.sito else "")
            self.lineEdit_area.setText(str(rec.area) if rec.area else "")
            self.lineEdit_us.setText(str(rec.us) if rec.us else "")
            self.lineEdit_quadrato.setText(str(rec.quadrato) if rec.quadrato else "")
            self.lineEdit_coord_x.setText(str(rec.coord_x) if rec.coord_x else "")
            self.lineEdit_coord_y.setText(str(rec.coord_y) if rec.coord_y else "")
            self.lineEdit_coord_z.setText(str(rec.coord_z) if rec.coord_z else "")

            # Faunal counts
            self.spinBox_bos_bison.setValue(int(rec.bos_bison) if rec.bos_bison else 0)
            self.spinBox_calcinati.setValue(int(rec.calcinati) if rec.calcinati else 0)
            self.spinBox_camoscio.setValue(int(rec.camoscio) if rec.camoscio else 0)
            self.spinBox_capriolo.setValue(int(rec.capriolo) if rec.capriolo else 0)
            self.spinBox_cervo.setValue(int(rec.cervo) if rec.cervo else 0)
            self.spinBox_combusto.setValue(int(rec.combusto) if rec.combusto else 0)
            self.spinBox_coni.setValue(int(rec.coni) if rec.coni else 0)
            self.spinBox_pdi.setValue(int(rec.pdi) if rec.pdi else 0)
            self.spinBox_stambecco.setValue(int(rec.stambecco) if rec.stambecco else 0)
            self.spinBox_strie.setValue(int(rec.strie) if rec.strie else 0)
            self.spinBox_canidi.setValue(int(rec.canidi) if rec.canidi else 0)
            self.spinBox_ursidi.setValue(int(rec.ursidi) if rec.ursidi else 0)
            self.spinBox_megacero.setValue(int(rec.megacero) if rec.megacero else 0)

            # Update record counter
            self.label_rec_tot.setText(str(self.REC_TOT))
            self.label_rec_corr.setText(str(n + 1))

        except Exception as e:
            QMessageBox.warning(self, "Error filling fields", str(e), QMessageBox.Ok)

    def empty_fields(self):
        """Clear all form fields."""
        self.comboBox_sito.setEditText("")
        self.lineEdit_area.clear()
        self.lineEdit_us.clear()
        self.lineEdit_quadrato.clear()
        self.lineEdit_coord_x.clear()
        self.lineEdit_coord_y.clear()
        self.lineEdit_coord_z.clear()

        self.spinBox_bos_bison.setValue(0)
        self.spinBox_calcinati.setValue(0)
        self.spinBox_camoscio.setValue(0)
        self.spinBox_capriolo.setValue(0)
        self.spinBox_cervo.setValue(0)
        self.spinBox_combusto.setValue(0)
        self.spinBox_coni.setValue(0)
        self.spinBox_pdi.setValue(0)
        self.spinBox_stambecco.setValue(0)
        self.spinBox_strie.setValue(0)
        self.spinBox_canidi.setValue(0)
        self.spinBox_ursidi.setValue(0)
        self.spinBox_megacero.setValue(0)

    # R Analysis Methods
    def on_calcola_pressed(self):
        """Calculate and display semivariogram."""
        if not self.r_analysis:
            QMessageBox.warning(self, "R Error", "R integration not available.", QMessageBox.Ok)
            return

        output_path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if not output_path:
            return

        try:
            # Connect to database
            conn = Connection()
            # Parse connection parameters...
            # For now, show a message
            QMessageBox.information(
                self, "Semivariogram",
                "Semivariogram analysis would be performed here.\n"
                "Requires R with gstat package installed.",
                QMessageBox.Ok
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e), QMessageBox.Ok)

    def on_automap_pressed(self):
        """Run automated kriging analysis."""
        if not self.r_analysis:
            QMessageBox.warning(self, "R Error", "R integration not available.", QMessageBox.Ok)
            return

        output_path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if not output_path:
            return

        QMessageBox.information(
            self, "AutoKrige",
            "Automated kriging analysis would be performed here.\n"
            "Requires R with automap package installed.",
            QMessageBox.Ok
        )

    def on_hist_pressed(self):
        """Generate histogram for selected variable."""
        if not self.r_analysis:
            QMessageBox.warning(self, "R Error", "R integration not available.", QMessageBox.Ok)
            return

        output_path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if not output_path:
            return

        QMessageBox.information(
            self, "Histogram",
            "Histogram would be generated here.\n"
            "Requires R with lattice package installed.",
            QMessageBox.Ok
        )

    def on_boxplot_pressed(self):
        """Generate boxplot for selected variable."""
        if not self.r_analysis:
            QMessageBox.warning(self, "R Error", "R integration not available.", QMessageBox.Ok)
            return

        output_path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if not output_path:
            return

        QMessageBox.information(
            self, "Boxplot",
            "Boxplot would be generated here.\n"
            "Requires R with lattice package installed.",
            QMessageBox.Ok
        )

    def on_coplot_pressed(self):
        """Generate conditional plot."""
        if not self.r_analysis:
            QMessageBox.warning(self, "R Error", "R integration not available.", QMessageBox.Ok)
            return

        output_path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if not output_path:
            return

        QMessageBox.information(
            self, "Coplot",
            "Conditional plot would be generated here.\n"
            "Requires R with lattice package installed.",
            QMessageBox.Ok
        )

    def on_matrix_pressed(self):
        """Generate correlation matrix."""
        if not self.r_analysis:
            QMessageBox.warning(self, "R Error", "R integration not available.", QMessageBox.Ok)
            return

        output_path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if not output_path:
            return

        QMessageBox.information(
            self, "Correlation Matrix",
            "Correlation matrix would be generated here.\n"
            "Requires R with lattice package installed.",
            QMessageBox.Ok
        )

    def on_report_pressed(self):
        """Generate HTML report."""
        if not self.r_analysis:
            QMessageBox.warning(self, "R Error", "R integration not available.", QMessageBox.Ok)
            return

        output_path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if not output_path:
            return

        QMessageBox.information(
            self, "HTML Report",
            "HTML report would be generated here.\n"
            "Requires R with R2HTML package installed.",
            QMessageBox.Ok
        )

    # Navigation methods
    def on_pushButton_first_rec_pressed(self):
        """Go to first record."""
        if self.DATA_LIST:
            self.REC_CORR = 0
            self.fill_fields(self.REC_CORR)

    def on_pushButton_last_rec_pressed(self):
        """Go to last record."""
        if self.DATA_LIST:
            self.REC_CORR = self.REC_TOT - 1
            self.fill_fields(self.REC_CORR)

    def on_pushButton_prev_rec_pressed(self):
        """Go to previous record."""
        if self.DATA_LIST and self.REC_CORR > 0:
            self.REC_CORR -= 1
            self.fill_fields(self.REC_CORR)

    def on_pushButton_next_rec_pressed(self):
        """Go to next record."""
        if self.DATA_LIST and self.REC_CORR < self.REC_TOT - 1:
            self.REC_CORR += 1
            self.fill_fields(self.REC_CORR)

    def on_pushButton_new_rec_pressed(self):
        """Create a new record."""
        self.BROWSE_STATUS = "n"
        self.empty_fields()
        self.label_status.setText("New Record")

    def on_pushButton_save_pressed(self):
        """Save the current record."""
        if self.BROWSE_STATUS == "n":
            # Insert new record
            try:
                data = self.collect_form_data()
                self.DB_MANAGER.insert_values(self.MAPPER_TABLE_CLASS, data)
                self.charge_records()
                self.REC_CORR = self.REC_TOT - 1
                self.fill_fields(self.REC_CORR)
                self.BROWSE_STATUS = "b"
                self.label_status.setText("Record saved")
                QMessageBox.information(self, "Success", "Record saved successfully.", QMessageBox.Ok)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Save failed: {str(e)}", QMessageBox.Ok)

    def collect_form_data(self):
        """Collect data from form fields."""
        return {
            'sito': str(self.comboBox_sito.currentText()),
            'area': str(self.lineEdit_area.text()) if self.lineEdit_area.text() else None,
            'us': str(self.lineEdit_us.text()) if self.lineEdit_us.text() else None,
            'quadrato': str(self.lineEdit_quadrato.text()) if self.lineEdit_quadrato.text() else None,
            'coord_x': int(self.lineEdit_coord_x.text()) if self.lineEdit_coord_x.text() else None,
            'coord_y': int(self.lineEdit_coord_y.text()) if self.lineEdit_coord_y.text() else None,
            'coord_z': float(self.lineEdit_coord_z.text()) if self.lineEdit_coord_z.text() else None,
            'bos_bison': self.spinBox_bos_bison.value() or None,
            'calcinati': self.spinBox_calcinati.value() or None,
            'camoscio': self.spinBox_camoscio.value() or None,
            'capriolo': self.spinBox_capriolo.value() or None,
            'cervo': self.spinBox_cervo.value() or None,
            'combusto': self.spinBox_combusto.value() or None,
            'coni': self.spinBox_coni.value() or None,
            'pdi': self.spinBox_pdi.value() or None,
            'stambecco': self.spinBox_stambecco.value() or None,
            'strie': self.spinBox_strie.value() or None,
            'canidi': self.spinBox_canidi.value() or None,
            'ursidi': self.spinBox_ursidi.value() or None,
            'megacero': self.spinBox_megacero.value() or None,
        }

    def on_pushButton_delete_pressed(self):
        """Delete the current record."""
        if not self.DATA_LIST:
            return

        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this record?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                id_to_delete = self.DATA_LIST[self.REC_CORR].id_archzoo
                self.DB_MANAGER.delete_one_record(
                    self.TABLE_NAME, self.ID_TABLE, id_to_delete
                )
                self.charge_records()
                if self.REC_CORR > 0:
                    self.REC_CORR -= 1
                self.fill_fields(self.REC_CORR)
                QMessageBox.information(self, "Success", "Record deleted.", QMessageBox.Ok)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Delete failed: {str(e)}", QMessageBox.Ok)

    def on_pushButton_view_all_pressed(self):
        """View all records."""
        self.charge_records()
        if self.DATA_LIST:
            self.fill_fields(0)
