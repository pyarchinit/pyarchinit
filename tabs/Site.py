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

import os
from datetime import date
import requests
import urllib

from ..modules.utility.debug_config import DEBUG
#from pyper import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.uic import *
from qgis.core import *

from ..modules.utility.debug_config import DEBUG
#from qgis.gui import QgsMapLayerComboBox
import shutil
import json
import webbrowser
import glob as glob_module
import csv
from datetime import datetime
import tempfile

from distutils.dir_util import copy_tree
from processing.tools.system import mkdir, userFolder
import processing

# Import movecost layer organizer
try:
    from movecost.layer_organizer import organize_movecost_layers, MovecostLayerOrganizer
except ImportError:
    organize_movecost_layers = None
    MovecostLayerOrganizer = None

# MoveCost language codes mapping
MC_LANGUAGE_CODES = {
    0: 'en',  # English
    1: 'it',  # Italiano
    2: 'fr',  # Francais
    3: 'es',  # Espanol
    4: 'de'   # Deutsch
}


from ..modules.db.pyarchinit_conn_strings import Connection
from ..modules.db.pyarchinit_db_manager import get_db_manager
from ..modules.db.concurrency_manager import ConcurrencyManager, RecordLockIndicator
from ..modules.db.pyarchinit_utility import Utility
from ..modules.gis.pyarchinit_pyqgis import Pyarchinit_pyqgis
from ..modules.utility.print_relazione_pdf import exp_rel_pdf
from ..modules.utility.pyarchinit_error_check import Error_check
from ..modules.utility.Utils import *
from ..gui.sortpanelmain import SortPanelMain
from ..gui.pyarchinitConfigDialog import pyArchInitDialog_Config
from .PlaceSelectionDialog import PlaceSelectionDialog
from .networkaccessmanager import NetworkAccessManager
from ..modules.utility.pyarchinit_theme_manager import ThemeManager
import sys,  json


from ..modules.utility.debug_config import DEBUG
NAM = NetworkAccessManager()
MAIN_DIALOG_CLASS, _ = loadUiType(os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'Site.ui'))


class QgsMapLayerRegistry:
    pass


class pyarchinit_Site(QDialog, MAIN_DIALOG_CLASS):
    """This class provides to manage the Site Sheet"""

    L=QgsSettings().value("locale/userLocale", "it", type=str)[:2]
    if L=='it':
        MSG_BOX_TITLE = "PyArchInit - Scheda Sito"
    elif L=='en':
        MSG_BOX_TITLE = "PyArchInit - Site form"
    elif L=='de':
        MSG_BOX_TITLE = "PyArchInit - Formular Ausgrabungsstätte"
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
    TABLE_NAME = 'site_table'
    MAPPER_TABLE_CLASS = "SITE"
    NOME_SCHEDA = "Scheda di Sito"
    ID_TABLE = "id_sito"
    SITO = pyArchInitDialog_Config
    if L=='it':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Sito": "sito",
            "Nazione": "nazione",
            "Regione": "regione",
            "Descrizione": "descrizione",
            "Comune": "comune",
            "Provincia": "provincia",
            "Definizione sito": "definizione_sito",
            "Directory Sito": "sito_path"
        }

        SORT_ITEMS = [
            ID_TABLE,
            "Sito",
            "Descrizione",
            "Nazione",
            "Regione",
            "Comune",
            "Provincia",
            "Definizione sito",
            "Directory Sito"
        ]
    elif L=='de':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Ausgrabungsstätte": "sito",
            "Nation": "nazione",
            "Region": "regione",
            "Beschreibung": "descrizione",
            "Ort / Stadt": "comune",
            "Landkreis": "provincia",
            "Definition Ausgrabungsstätte": "definizione_sito",
            "Folder path": "sito_path"
        }

        SORT_ITEMS = [
            ID_TABLE,
            "Ausgrabungsstätte",
            "Nation",
            "Region",
            "Beschreibung",
            "Ort / Stadt",
            "Landkreis",
            "Definition Ausgrabungsstätte",
            "Folder path"
        ]
    elif L=='en':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Site": "sito",
            "Nation": "nazione",
            "Region": "regione",
            "Description": "descrizione",
            "Town": "comune",
            "Provincie": "provincia",
            "Definition site ": "definizione_sito",
            "Directory": "sito_path"
        }

        SORT_ITEMS = [
            ID_TABLE,
            "Site",
            "Nation",
            "Region",
            "Description",
            "Town",
            "Provincie",
            "Definition site ",
            "Directory"
        ]
    elif L=='es':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Sitio": "sito",
            "Nación": "nazione",
            "Región": "regione",
            "Descripción": "descrizione",
            "Municipio": "comune",
            "Provincia": "provincia",
            "Definición del sitio": "definizione_sito",
            "Directorio": "sito_path"
        }

        SORT_ITEMS = [
            ID_TABLE,
            "Sitio",
            "Nación",
            "Región",
            "Descripción",
            "Municipio",
            "Provincia",
            "Definición del sitio",
            "Directorio"
        ]
    elif L=='fr':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Site": "sito",
            "Nation": "nazione",
            "Région": "regione",
            "Description": "descrizione",
            "Commune": "comune",
            "Province": "provincia",
            "Définition du site": "definizione_sito",
            "Répertoire": "sito_path"
        }

        SORT_ITEMS = [
            ID_TABLE,
            "Site",
            "Nation",
            "Région",
            "Description",
            "Commune",
            "Province",
            "Définition du site",
            "Répertoire"
        ]
    elif L=='ar':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "موقع": "sito",
            "دولة": "nazione",
            "منطقة": "regione",
            "وصف": "descrizione",
            "بلدية": "comune",
            "محافظة": "provincia",
            "تعريف الموقع": "definizione_sito",
            "مسار الملفات": "sito_path"
        }

        SORT_ITEMS = [
            ID_TABLE,
            "موقع",
            "دولة",
            "منطقة",
            "وصف",
            "بلدية",
            "محافظة",
            "تعريف الموقع",
            "مسار الملفات"
        ]
    elif L=='ca':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Jaciment": "sito",
            "Nació": "nazione",
            "Regió": "regione",
            "Descripció": "descrizione",
            "Municipi": "comune",
            "Província": "provincia",
            "Definició del jaciment": "definizione_sito",
            "Directori": "sito_path"
        }

        SORT_ITEMS = [
            ID_TABLE,
            "Jaciment",
            "Nació",
            "Regió",
            "Descripció",
            "Municipi",
            "Província",
            "Definició del jaciment",
            "Directori"
        ]
    elif L=='ro':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Sit": "sito",
            "Națiune": "nazione",
            "Regiune": "regione",
            "Descriere": "descrizione",
            "Oraș": "comune",
            "Provincie": "provincia",
            "Definiție sit": "definizione_sito",
            "Director": "sito_path"
        }

        SORT_ITEMS = [
            ID_TABLE,
            "Sit",
            "Națiune",
            "Regiune",
            "Descriere",
            "Oraș",
            "Provincie",
            "Definiție sit",
            "Director"
        ]
    elif L=='pt':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Sítio": "sito",
            "Nação": "nazione",
            "Região": "regione",
            "Descrição": "descrizione",
            "Município": "comune",
            "Província": "provincia",
            "Definição do sítio": "definizione_sito",
            "Diretório": "sito_path"
        }

        SORT_ITEMS = [
            ID_TABLE,
            "Sítio",
            "Nação",
            "Região",
            "Descrição",
            "Município",
            "Província",
            "Definição do sítio",
            "Diretório"
        ]
    elif L=='el':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Θέση": "sito",
            "Έθνος": "nazione",
            "Περιφέρεια": "regione",
            "Περιγραφή": "descrizione",
            "Δήμος": "comune",
            "Νομός": "provincia",
            "Ορισμός θέσης": "definizione_sito",
            "Κατάλογος": "sito_path"
        }

        SORT_ITEMS = [
            ID_TABLE,
            "Θέση",
            "Έθνος",
            "Περιφέρεια",
            "Περιγραφή",
            "Δήμος",
            "Νομός",
            "Ορισμός θέσης",
            "Κατάλογος"
        ]
    else:
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Site": "sito",
            "Nation": "nazione",
            "Region": "regione",
            "Description": "descrizione",
            "Town": "comune",
            "Provincie": "provincia",
            "Definition site ": "definizione_sito",
            "Directory": "sito_path"
        }

        SORT_ITEMS = [
            ID_TABLE,
            "Site",
            "Nation",
            "Region",
            "Description",
            "Town",
            "Provincie",
            "Definition site ",
            "Directory"
        ]
    TABLE_FIELDS = [
        "sito",
        "nazione",
        "regione",
        "comune",
        "descrizione",
        "provincia",
        "definizione_sito",
        "sito_path"
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
        "AR": ['ar_LB', 'ar', 'AR', 'AR_LB', 'ar_AR', 'AR_AR'],
        "CA": ['ca_ES', 'ca', 'CA', 'CA_ES'],
        "PT_BR": ['pt_BR','PT_BR'],
        "SL": ['sl_SL','sl','SL', 'SL_SL'],
        "EL": ['el_GR', 'el', 'EL', 'EL_GR'],
    }

    DB_SERVER = "not defined"  ####nuovo sistema sort
    
    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.pyQGIS = Pyarchinit_pyqgis(iface)
        self.setupUi(self)

        # Apply theme
        ThemeManager.apply_theme(self)

        # Add theme toggle button (positioned in top-right corner)
        self.theme_toggle_btn = ThemeManager.add_theme_toggle_to_form(self)

        self.mDockWidget.setHidden(True)

        # MoveCost initialization
        self.last_algorithm = None
        self.last_params = {}
        self.last_results = {}
        self.current_plot_path = None

        # Initialize layer organizer
        self.layer_organizer = None
        if MovecostLayerOrganizer is not None:
            self.layer_organizer = MovecostLayerOrganizer(self)

        # Connect movecost UI elements (explicit connections for non-auto-connect widgets)
        try:
            self.comboBox_mc_language.currentIndexChanged.connect(self.on_comboBox_mc_language_currentIndexChanged)
        except AttributeError:
            pass

        self.canvas = iface.mapCanvas()
        self.layerid = ''
        #self.layer = None
        self.currentLayerId = None
        self.HOME = os.environ['PYARCHINIT_HOME']
        try:
            self.on_pushButton_connect_pressed()
        except Exception as e:
            QMessageBox.warning(self, "Connection system", str(e), QMessageBox.StandardButton.Ok)

        self.pbnOpenSiteDirectory.clicked.connect(self.openSiteDir)
        self.pbn_browse_folder.clicked.connect(self.setPathToSites)
        self.set_sito()
        self.msg_sito()
        self.config = QgsSettings()
        self.previous_map_tool = self.iface.mapCanvas().mapTool()

        # Initialize concurrency management
        self.concurrency_manager = ConcurrencyManager(self)
        self.lock_indicator = RecordLockIndicator(self)
        self.current_record_version = None
        self.editing_record_id = None
        self.is_saving = False  # Flag to prevent multiple simultaneous saves

        # Setup auto-refresh timer for checking concurrent modifications
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.check_for_updates)
        self.refresh_timer.start(60000)  # Check every 60 seconds

    # =========================================================================
    # MoveCost Algorithm Methods
    # =========================================================================

    def _mc_run_algorithm(self, algorithm_name, display_name):
        """Run a movecost algorithm and update the results tab."""
        self._mc_start_monitoring_if_enabled()
        self.last_algorithm = display_name
        processing.execAlgorithmDialog(algorithm_name)
        self._mc_schedule_organization()
        QTimer.singleShot(5000, self._mc_update_results_tab)

    def on_pushButton_movecost_pressed(self):
        self._mc_run_algorithm('r:movecost', 'movecost')

    def on_pushButton_movecost_p_pressed(self):
        self._mc_run_algorithm('r:movecostbypolygon', 'movecost by polygon')

    def on_pushButton_movebound_pressed(self):
        self._mc_run_algorithm('r:movebound', 'movebound')

    def on_pushButton_movebound_p_pressed(self):
        self._mc_run_algorithm('r:moveboundbypolygon', 'movebound by polygon')

    def on_pushButton_movecorr_pressed(self):
        self._mc_run_algorithm('r:movecorr', 'movecorr')

    def on_pushButton_movecorr_p_pressed(self):
        self._mc_run_algorithm('r:movecorrbypolygon', 'movecorr by polygon')

    def on_pushButton_movealloc_pressed(self):
        self._mc_run_algorithm('r:movealloc', 'movealloc')

    def on_pushButton_movealloc_p_pressed(self):
        self._mc_run_algorithm('r:moveallocbypolygon', 'movealloc by polygon')

    def on_pushButton_movecomp_pressed(self):
        self._mc_run_algorithm('r:movecomp', 'movecomp')

    def on_pushButton_movecomp_p_pressed(self):
        self._mc_run_algorithm('r:movecompbypolygon', 'movecomp by polygon')

    def on_pushButton_movenetw_pressed(self):
        self._mc_run_algorithm('r:movenetw', 'movenetw')

    def on_pushButton_movenetw_p_pressed(self):
        self._mc_run_algorithm('r:movenetwbypolygon', 'movenetw by polygon')

    def on_pushButton_moverank_p_pressed(self):
        self._mc_run_algorithm('r:moverank', 'moverank')

    def on_pushButton_moverank_polygon_pressed(self):
        self._mc_run_algorithm('r:moverankbypolygon', 'moverank by polygon')

    # =========================================================================
    # MoveCost Layer Organization
    # =========================================================================

    def _mc_start_monitoring_if_enabled(self):
        """Start layer monitoring if auto-organize is enabled."""
        try:
            if self.checkBox_auto_organize.isChecked() and self.layer_organizer:
                self.layer_organizer.start_monitoring()
        except AttributeError:
            pass

    def _mc_schedule_organization(self):
        """Schedule layer organization after the algorithm dialog closes."""
        try:
            if self.checkBox_auto_organize.isChecked():
                QTimer.singleShot(3000, self._mc_delayed_organize)
        except AttributeError:
            pass

    def _mc_delayed_organize(self):
        """Organize layers after delay."""
        if organize_movecost_layers is not None:
            try:
                organize_movecost_layers()
            except Exception as e:
                if DEBUG:
                    print(f"Layer organization error: {e}")

    def on_pushButton_organize_pressed(self):
        """Manually organize all movecost layers."""
        if organize_movecost_layers is not None:
            organize_movecost_layers()
            QMessageBox.information(self, "MoveCost",
                                    "Layers have been organized and styled!",
                                    QMessageBox.StandardButton.Ok)
        else:
            QMessageBox.warning(self, "MoveCost",
                                "Layer organizer module not available.\n"
                                "Install the movecost plugin to enable this feature.",
                                QMessageBox.StandardButton.Ok)

    # =========================================================================
    # MoveCost Results Tab
    # =========================================================================

    def _mc_update_results_tab(self):
        """Update the results tab with summary and plot."""
        self._mc_update_summary()
        self._mc_load_latest_plot()

    def _mc_update_summary(self):
        """Generate and display cost summary."""
        if not self.last_algorithm:
            return

        layers = QgsProject.instance().mapLayers().values()
        recent_layers = []
        for layer in layers:
            if layer.type() == QgsMapLayerType.VectorLayer:
                field_names = [f.name().lower() for f in layer.fields()]
                if any(f in field_names for f in ['cost', 'length_m', 'length_km', 'time_converted']):
                    recent_layers.append(layer)

        summary = f"""<h3 style="color: #2c3e50;">Analysis: {self.last_algorithm}</h3>
<p><b>Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
<hr>"""

        if recent_layers:
            for layer in recent_layers[:5]:
                summary += f"<h4 style='color: #3498db;'>{layer.name()}</h4>"
                summary += "<table style='width:100%; border-collapse: collapse;'>"
                for field in layer.fields():
                    fname = field.name().lower()
                    if fname in ['cost', 'length_m', 'length_km', 'area_m2', 'area_km2', 'area_ha']:
                        try:
                            idx = layer.fields().indexOf(field.name())
                            values = [f[idx] for f in layer.getFeatures() if f[idx] is not None]
                            if values:
                                min_val = min(values)
                                max_val = max(values)
                                avg_val = sum(values) / len(values)
                                summary += f"""<tr>
                                    <td style='padding: 4px; border-bottom: 1px solid #eee;'><b>{field.name()}</b></td>
                                    <td style='padding: 4px; border-bottom: 1px solid #eee;'>
                                        Min: {min_val:.2f} | Max: {max_val:.2f} | Avg: {avg_val:.2f}
                                    </td>
                                </tr>"""
                        except Exception:
                            pass
                    elif fname == 'time_converted':
                        try:
                            idx = layer.fields().indexOf(field.name())
                            times = [f[idx] for f in layer.getFeatures() if f[idx] is not None]
                            if times:
                                summary += f"""<tr>
                                    <td style='padding: 4px; border-bottom: 1px solid #eee;'><b>Time Range</b></td>
                                    <td style='padding: 4px; border-bottom: 1px solid #eee;'>
                                        {times[0]} - {times[-1]}
                                    </td>
                                </tr>"""
                        except Exception:
                            pass
                summary += "</table><br>"
        else:
            summary += "<p><i>No cost data available yet. Run an algorithm to see results.</i></p>"

        try:
            self.textEdit_summary.setHtml(summary)
        except AttributeError:
            pass

    def _mc_load_latest_plot(self):
        """Load the latest R plot from the processing directory."""
        profile_home = QgsApplication.qgisSettingsDirPath()
        system_temp = tempfile.gettempdir()

        try:
            processing_temp = QgsProcessingUtils.tempFolder()
        except Exception:
            processing_temp = None

        # Check dedicated movecost plots directory first
        movecost_plot_dir = os.path.join(system_temp, 'movecost_plots')
        plot_file = os.path.join(movecost_plot_dir, 'movecost_latest_plot.png')
        if os.path.exists(plot_file):
            try:
                file_time = os.path.getmtime(plot_file)
                current_time = datetime.now().timestamp()
                if (current_time - file_time) < 600:
                    self.current_plot_path = plot_file
                    pixmap = QPixmap(plot_file)
                    if not pixmap.isNull():
                        scaled_pixmap = pixmap.scaled(
                            self.label_plot.width() if self.label_plot.width() > 100 else 350,
                            self.label_plot.height() if self.label_plot.height() > 100 else 250,
                            Qt.KeepAspectRatio,
                            Qt.SmoothTransformation
                        )
                        self.label_plot.setPixmap(scaled_pixmap)
                        self.label_plot.setToolTip(f"Plot: movecost_latest_plot.png")
                        return
            except (OSError, IOError):
                pass

        # Search various temp directories for R plots
        temp_dirs = [
            processing_temp,
            os.path.join(profile_home, 'processing', 'outputs'),
            os.path.join(profile_home, 'processing'),
            os.path.join(system_temp, 'processing'),
            os.path.join(system_temp, 'processing_r'),
            os.path.join(system_temp, 'qgis'),
            os.path.join(system_temp, 'movecost_plots'),
            system_temp,
        ]
        temp_dirs = [d for d in temp_dirs if d is not None]

        try:
            from processing.core.ProcessingConfig import ProcessingConfig
            r_output = ProcessingConfig.getSetting('R_FOLDER')
            if r_output:
                temp_dirs.insert(0, r_output)
        except Exception:
            pass

        plot_patterns = [
            'Rplots*.png', 'Rplot*.png', 'plot*.png',
            '*movecost*.png', '*movebound*.png', '*movecorr*.png',
            '*movealloc*.png', '*movecomp*.png', '*movenetw*.png',
            '*moverank*.png', 'processing_*.png', 'output*.png',
        ]

        latest_plot = None
        latest_time = 0
        current_time = datetime.now().timestamp()

        for temp_dir in temp_dirs:
            if not os.path.exists(temp_dir):
                continue
            for pattern in plot_patterns:
                try:
                    for pf in glob_module.glob(os.path.join(temp_dir, pattern)):
                        try:
                            file_time = os.path.getmtime(pf)
                            if file_time > latest_time and (current_time - file_time) < 600:
                                if os.path.getsize(pf) > 1000:
                                    latest_time = file_time
                                    latest_plot = pf
                        except (OSError, IOError):
                            continue
                except Exception:
                    continue

        if latest_plot and latest_plot.lower().endswith(('.png', '.jpg', '.jpeg')):
            self.current_plot_path = latest_plot
            pixmap = QPixmap(latest_plot)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    self.label_plot.width() if self.label_plot.width() > 100 else 350,
                    self.label_plot.height() if self.label_plot.height() > 100 else 250,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.label_plot.setPixmap(scaled_pixmap)
                self.label_plot.setToolTip(f"Plot: {os.path.basename(latest_plot)}")
                return

        try:
            self.label_plot.setText("R plots will appear here after running an algorithm\n\nClick 'Refresh Plot' after running an algorithm")
        except AttributeError:
            pass

    def on_pushButton_refresh_plot_pressed(self):
        """Refresh the plot display."""
        modifiers = QApplication.keyboardModifiers()
        try:
            shift_modifier = Qt.KeyboardModifier.ShiftModifier
        except AttributeError:
            shift_modifier = Qt.ShiftModifier

        if modifiers == shift_modifier:
            self._mc_show_search_debug()
            return

        self._mc_load_latest_plot()

        if self.current_plot_path is None or not os.path.exists(self.current_plot_path or ''):
            reply = QMessageBox.question(
                self, "No Plot Found",
                "No recent R plot was found automatically.\n\n"
                "Would you like to manually select an image file?\n\n"
                "(Tip: Hold Shift and click 'Refresh Plot' to see where we're searching)",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self._mc_manual_select_plot()

    def _mc_show_search_debug(self):
        """Show debug info about where we're searching for plots."""
        profile_home = QgsApplication.qgisSettingsDirPath()
        system_temp = tempfile.gettempdir()
        try:
            processing_temp = QgsProcessingUtils.tempFolder()
        except Exception:
            processing_temp = "N/A"

        debug_info = f"""Search directories for R plots:

1. QGIS Profile: {profile_home}
2. System Temp: {system_temp}
3. Processing Temp: {processing_temp}

Current plot path: {self.current_plot_path or 'None'}
"""
        QMessageBox.information(self, "Plot Search Debug Info", debug_info,
                               QMessageBox.StandardButton.Ok)

    def _mc_manual_select_plot(self):
        """Allow user to manually select a plot file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Plot Image", "",
            "Image files (*.png *.jpg *.jpeg);;All files (*.*)"
        )
        if file_path:
            self.current_plot_path = file_path
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    self.label_plot.width() if self.label_plot.width() > 100 else 350,
                    self.label_plot.height() if self.label_plot.height() > 100 else 250,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.label_plot.setPixmap(scaled_pixmap)
                self.label_plot.setToolTip(f"Plot: {os.path.basename(file_path)}")

    def on_pushButton_save_plot_pressed(self):
        """Save the current plot to a file."""
        if self.current_plot_path and os.path.exists(self.current_plot_path):
            save_path, _ = QFileDialog.getSaveFileName(
                self, "Save Plot", "",
                "PNG files (*.png);;JPEG files (*.jpg);;All files (*.*)"
            )
            if save_path:
                shutil.copy2(self.current_plot_path, save_path)
                QMessageBox.information(self, "Success", f"Plot saved to {save_path}",
                                        QMessageBox.StandardButton.Ok)
        else:
            QMessageBox.warning(self, "Warning", "No plot available to save.",
                               QMessageBox.StandardButton.Ok)

    # =========================================================================
    # MoveCost Export
    # =========================================================================

    def on_pushButton_export_csv_pressed(self):
        """Export cost data to CSV."""
        layers = QgsProject.instance().mapLayers().values()
        cost_layers = []
        for layer in layers:
            if layer.type() == QgsMapLayerType.VectorLayer:
                field_names = [f.name().lower() for f in layer.fields()]
                if any(f in field_names for f in ['cost', 'length_m', 'time_converted']):
                    cost_layers.append(layer)

        if not cost_layers:
            QMessageBox.warning(self, "Warning", "No cost layers found to export.",
                               QMessageBox.StandardButton.Ok)
            return

        save_path, _ = QFileDialog.getSaveFileName(
            self, "Export Cost Table", "",
            "CSV files (*.csv);;All files (*.*)"
        )
        if save_path:
            try:
                with open(save_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    for layer in cost_layers:
                        writer.writerow([f"Layer: {layer.name()}"])
                        headers = [f.name() for f in layer.fields()]
                        writer.writerow(headers)
                        for feature in layer.getFeatures():
                            writer.writerow([feature[h] for h in headers])
                        writer.writerow([])
                QMessageBox.information(self, "Success", f"Data exported to {save_path}",
                                        QMessageBox.StandardButton.Ok)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Export failed: {str(e)}",
                                    QMessageBox.StandardButton.Ok)

    def on_pushButton_export_pdf_pressed(self):
        """Export report to PDF (stub)."""
        QMessageBox.information(self, "Info",
            "PDF export requires additional libraries. Use HTML export for now.",
            QMessageBox.StandardButton.Ok)

    def on_pushButton_export_html_pressed(self):
        """Export report to HTML."""
        save_path, _ = QFileDialog.getSaveFileName(
            self, "Export Report", "",
            "HTML files (*.html);;All files (*.*)"
        )
        if save_path:
            try:
                summary_html = ""
                try:
                    summary_html = self.textEdit_summary.toHtml()
                except AttributeError:
                    summary_html = "<p>No summary available</p>"

                html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Movecost Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; color: #2c3e50; }}
        h1 {{ color: #3498db; }}
        h2 {{ color: #2980b9; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #bdc3c7; padding: 8px; text-align: left; }}
        th {{ background-color: #3498db; color: white; }}
        tr:nth-child(even) {{ background-color: #f8f9fa; }}
        .summary {{ background: #f8f9fa; padding: 15px; border-radius: 8px; }}
    </style>
</head>
<body>
    <h1>Movecost Analysis Report</h1>
    <p><b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <div class="summary">
        {summary_html}
    </div>
"""
                layers = QgsProject.instance().mapLayers().values()
                for layer in layers:
                    if layer.type() == QgsMapLayerType.VectorLayer:
                        field_names = [f.name().lower() for f in layer.fields()]
                        if any(f in field_names for f in ['cost', 'length_m', 'time_converted']):
                            html_content += f"<h2>{layer.name()}</h2>"
                            html_content += "<table><tr>"
                            for field in layer.fields():
                                html_content += f"<th>{field.name()}</th>"
                            html_content += "</tr>"
                            for feature in layer.getFeatures():
                                html_content += "<tr>"
                                for field in layer.fields():
                                    html_content += f"<td>{feature[field.name()]}</td>"
                                html_content += "</tr>"
                            html_content += "</table>"
                html_content += "</body></html>"

                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)

                QMessageBox.information(self, "Success", f"Report exported to {save_path}",
                                        QMessageBox.StandardButton.Ok)
                webbrowser.open('file://' + save_path)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Export failed: {str(e)}",
                                    QMessageBox.StandardButton.Ok)

    # =========================================================================
    # MoveCost Settings
    # =========================================================================

    def defaultScriptsFolder(self):
        folder = str(os.path.join(userFolder(), "rscripts"))
        mkdir(folder)
        return os.path.abspath(folder)

    def on_pushButton_add_script_pressed(self):
        """Copy R scripts from movecost plugin to QGIS processing directory."""
        profile_home = QgsApplication.qgisSettingsDirPath()
        source_profile = os.path.join(profile_home, 'python', 'plugins', 'movecost', 'rscripts')

        # Fallback to pyarchinit's own scripts if movecost plugin not installed
        if not os.path.exists(source_profile):
            source_profile = os.path.join(self.HOME, 'bin', 'rscripts')

        if not os.path.exists(source_profile):
            QMessageBox.warning(self, "Warning",
                "R scripts source directory not found.\n"
                "Please install the movecost plugin first.",
                QMessageBox.StandardButton.Ok)
            return

        rs = os.path.join(profile_home, 'processing', 'rscripts')
        if not os.path.exists(rs):
            os.makedirs(rs)

        # Copy each file individually to allow overwriting
        count = 0
        for filename in os.listdir(source_profile):
            source_file = os.path.join(source_profile, filename)
            dest_file = os.path.join(rs, filename)
            if os.path.isfile(source_file):
                shutil.copy2(source_file, dest_file)
                count += 1

        QMessageBox.information(self, "Success",
                                f"{count} R scripts have been copied successfully!",
                                QMessageBox.StandardButton.Ok)

    def on_pushButton_mc_help_pressed(self):
        """Open the movecost help documentation in the default browser."""
        try:
            lang_code = MC_LANGUAGE_CODES.get(self.comboBox_mc_language.currentIndex(), 'en')
        except AttributeError:
            lang_code = 'en'

        profile_home = QgsApplication.qgisSettingsDirPath()
        help_dir = os.path.join(profile_home, 'python', 'plugins', 'movecost', 'help', lang_code)
        help_file = os.path.join(help_dir, 'index.html')

        if not os.path.exists(help_file):
            help_file = os.path.join(profile_home, 'python', 'plugins', 'movecost', 'help', 'en', 'index.html')

        if os.path.exists(help_file):
            webbrowser.open('file://' + help_file)
        else:
            webbrowser.open('https://github.com/enzococca/movecost/wiki')

    def on_comboBox_mc_language_currentIndexChanged(self, index):
        """Update tooltips when language changes."""
        lang_code = MC_LANGUAGE_CODES.get(index, 'en')
        self._mc_update_tooltips(lang_code)

    def _mc_update_tooltips(self, lang_code):
        """Update all movecost button tooltips based on selected language."""
        tooltips = self._mc_get_tooltips(lang_code)

        button_tooltip_map = {
            'pushButton_movecost': 'movecost',
            'pushButton_movecost_p': 'movecost_polygon',
            'pushButton_movebound': 'movebound',
            'pushButton_movebound_p': 'movebound_polygon',
            'pushButton_movecorr': 'movecorr',
            'pushButton_movecorr_p': 'movecorr_polygon',
            'pushButton_movealloc': 'movealloc',
            'pushButton_movealloc_p': 'movealloc_polygon',
            'pushButton_movecomp': 'movecomp',
            'pushButton_movecomp_p': 'movecomp_polygon',
            'pushButton_movenetw': 'movenetw',
            'pushButton_movenetw_p': 'movenetw_polygon',
            'pushButton_moverank_p': 'moverank',
            'pushButton_moverank_polygon': 'moverank_polygon',
        }

        for btn_name, tooltip_key in button_tooltip_map.items():
            try:
                btn = getattr(self, btn_name)
                btn.setToolTip(tooltips.get(tooltip_key, ''))
            except AttributeError:
                pass

    def _mc_get_tooltips(self, lang_code):
        """Get tooltips dictionary for the specified language."""
        profile_home = QgsApplication.qgisSettingsDirPath()
        tooltips_file = os.path.join(
            profile_home, 'python', 'plugins', 'movecost', 'i18n', f'tooltips_{lang_code}.json'
        )

        if os.path.exists(tooltips_file):
            try:
                with open(tooltips_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass

        return {
            'movecost': 'Calculate accumulated anisotropic slope-dependent cost of movement and least-cost paths from a point origin',
            'movecost_polygon': 'Calculate accumulated cost surface using a polygon area to define the DTM extent',
            'movebound': 'Calculate slope-dependent walking cost boundaries around point locations',
            'movebound_polygon': 'Calculate walking cost boundaries using a polygon area to define the DTM extent',
            'movecorr': 'Calculate least-cost corridor between point locations',
            'movecorr_polygon': 'Calculate least-cost corridor using a polygon area to define the DTM extent',
            'movealloc': 'Calculate slope-dependent walking-cost allocation to origins',
            'movealloc_polygon': 'Calculate walking-cost allocation using a polygon area to define the DTM extent',
            'movecomp': 'Compare least-cost paths generated using different cost functions',
            'movecomp_polygon': 'Compare least-cost paths using a polygon area to define the DTM extent',
            'movenetw': 'Calculate least-cost path network between multiple points',
            'movenetw_polygon': 'Calculate least-cost path network using a polygon area to define the DTM extent',
            'moverank': 'Rank destinations by walking cost from an origin',
            'moverank_polygon': 'Rank destinations using a polygon area to define the DTM extent'
        }
    
    def setPathToSites(self):
        s = QgsSettings()
        self.siti_path = QFileDialog.getExistingDirectory(
            self,
            "Set path directory",
            self.HOME,
            QFileDialog.Option.ShowDirsOnly
        )

        if self.siti_path:
            self.lineEdit_sito_path.setText(self.siti_path)

    def openSiteDir(self):
        s = QgsSettings()
        dir = self.lineEdit_sito_path.text()
        if os.path.exists(dir):
            QDesktopServices.openUrl(QUrl.fromLocalFile(dir))
        else:
            QMessageBox.warning(self, "INFO", "Directory not found",
                                QMessageBox.StandardButton.Ok)

    def on_wms_vincoli_pressed(self):
        groupName="Vincoli Archelogici"
        root = QgsProject.instance().layerTreeRoot()
        group = root.addGroup(groupName)
        group.setExpanded(False)
        myGroup5 = group.insertGroup(5, "Vincoli")
        nome_vestizione='Vincoli puntuali'
        url_vestizione ='http://vincoliinrete.beniculturali.it/geoserver/wms_public/ows?layers=v_layer_anagrafica_beniculturali:comune&CQL_FILTER=comune=%27{}%27'.format(self.comboBox_comune.currentText())
        uri_vestizione ='IgnoreGetFeatureInfoUrl=1&IgnoreGetMapUrl=1&contextualWMSLegend=0&crs=EPSG:6875&dpiMode=7&featureCount=10&format=image/png&layers=v_geo_anagrafica_beni_puntuali&styles&url='+requests.utils.quote(url_vestizione)
        rlayer3= QgsRasterLayer(uri_vestizione, nome_vestizione,'wms')
        myGroup5.insertChildNode(-1, QgsLayerTreeLayer(rlayer3))
        
        
        nome_vestizione='Vincoli Lineari'
        url_vestizione ='http://vincoliinrete.beniculturali.it/geoserver/wms_public/ows?layers=v_layer_anagrafica_beniculturali:comune&CQL_FILTER=comune=%27{}%27'.format(self.comboBox_comune.currentText())
        uri_vestizione ='IgnoreGetFeatureInfoUrl=1&IgnoreGetMapUrl=1&contextualWMSLegend=0&crs=EPSG:6875&dpiMode=7&featureCount=10&format=image/png&layers=v_geo_anagrafica_beni_lineari&styles&url='+requests.utils.quote(url_vestizione)
        rlayer4= QgsRasterLayer(uri_vestizione, nome_vestizione,'wms')
        myGroup5.insertChildNode(-1, QgsLayerTreeLayer(rlayer4))
        
        nome_vestizione='Vincoli poligonali'
        url_vestizione ='http://vincoliinrete.beniculturali.it/geoserver/wms_public/ows?layers=v_layer_anagrafica_beniculturali:comune&CQL_FILTER=comune=%27{}%27'.format(self.comboBox_comune.currentText())
        uri_vestizione ='IgnoreGetFeatureInfoUrl=1&IgnoreGetMapUrl=1&contextualWMSLegend=0&crs=EPSG:6875&dpiMode=7&featureCount=10&format=image/png&layers=v_geo_anagrafica_beni_poligonali&styles&url='+requests.utils.quote(url_vestizione)
        rlayer5= QgsRasterLayer(uri_vestizione, nome_vestizione,'wms')
        myGroup5.insertChildNode(-1, QgsLayerTreeLayer(rlayer5))
        QgsProject.instance().addMapLayers([rlayer3,rlayer4,rlayer5],False)
    def internet_on(self):
        try:
            urllib.request.urlopen('https://wms.cartografia.agenziaentrate.gov.it/inspire/wms/ows01.php?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetCapabilities', timeout=0.5)
            return True
        except urllib.error.URLError:
            
            return False
    def on_basemap_pressed(self):
        if self.internet_on():
            groupName="BaseMap"
            root = QgsProject.instance().layerTreeRoot()
            group = root.addGroup(groupName)
            group.setExpanded(False)

            if self.L=='it':
                myGroup7 = group.insertGroup(4, "Toponomastica")
                nome_igm_t = ' Toponomastica IGM 25000'
                url_igm_t = "http://wms.pcn.minambiente.it/ogc?map=/ms_ogc/wfs/Toponimi_2011.map&version=1.1.0&service=wfs&request=getFeature&typename=NG.TOPONIMI.&Filter=%3CFilter%3E%3CPropertyIsEqualTo%3E%3CPropertyName%3Ecomune%3C/PropertyName%3E%3CLiteral%3E{}%3C/Literal%3E%3C/PropertyIsEqualTo%3E%3C/Filter%3E".format(
                    self.comboBox_comune.currentText().upper())

                rlayer11 = QgsVectorLayer(url_igm_t, nome_igm_t, 'wfs')
                myGroup7.insertChildNode(-1, QgsLayerTreeLayer(rlayer11))

                myGroup4 = group.insertGroup(6, "Catasto")
                
                nome_vestizione='Vestizione'
                url_vestizione ='wms.cartografia.agenziaentrate.gov.it/inspire/wms/ows01.php'
                uri_vestizione ='contextualWMSLegend=0&crs=EPSG:25832&dpiMode=7&featureCount=10&format=image/png&layers=vestizioni&styles&url=https://'+requests.utils.quote(url_vestizione)
                rlayer3= QgsRasterLayer(uri_vestizione, nome_vestizione,'wms')
                myGroup4.insertChildNode(-1, QgsLayerTreeLayer(rlayer3))
                
                nome_fabbricati='Fabbricati'
                url_fabbricati ='wms.cartografia.agenziaentrate.gov.it/inspire/wms/ows01.php'
                uri_fabbricati ='contextualWMSLegend=0&crs=EPSG:4258&dpiMode=7&featureCount=10&format=image/png&layers=fabbricati&styles&url=https://'+requests.utils.quote(url_vestizione)
                rlayer4= QgsRasterLayer(uri_fabbricati, nome_fabbricati,'wms')
                myGroup4.insertChildNode(-1, QgsLayerTreeLayer(rlayer4))
                
                nome_Particelle='Particelle'
                url_Particelle ='wms.cartografia.agenziaentrate.gov.it/inspire/wms/ows01.php'
                uri_Particelle ='contextualWMSLegend=0&crs=EPSG:4258&dpiMode=7&featureCount=10&format=image/png&layers=CP.CadastralParcel&styles&url=https://'+requests.utils.quote(url_Particelle)
                rlayer5= QgsRasterLayer(uri_Particelle, nome_Particelle,'wms')
                myGroup4.insertChildNode(-1, QgsLayerTreeLayer(rlayer5))
                
                nome_Strade='Strade'
                url_Strade ='wms.cartografia.agenziaentrate.gov.it/inspire/wms/ows01.php'
                uri_Strade ='contextualWMSLegend=0&crs=EPSG:4258&dpiMode=7&featureCount=10&format=image/png&layers=strade&styles&url=https://'+requests.utils.quote(url_Strade)
                rlayer6= QgsRasterLayer(uri_Strade, nome_Strade,'wms')
                myGroup4.insertChildNode(-1, QgsLayerTreeLayer(rlayer6))
                
                nome_Acque='Acque'
                url_Acque ='wms.cartografia.agenziaentrate.gov.it/inspire/wms/ows01.php'
                uri_Acque ='contextualWMSLegend=0&crs=EPSG:4258&dpiMode=7&featureCount=10&format=image/png&layers=acque&styles&url=https://'+requests.utils.quote(url_Acque)
                rlayer7= QgsRasterLayer(uri_Acque, nome_Acque,'wms')
                myGroup4.insertChildNode(-1, QgsLayerTreeLayer(rlayer7))
                
                nome_Mappe='Mappe'
                url_Mappe ='wms.cartografia.agenziaentrate.gov.it/inspire/wms/ows01.php'
                uri_Mappe ='crs=EPSG:4326&dpiMode=7&format=image/png&layers=CP.CadastralZoning&styles&url=https://'+requests.utils.quote(url_Mappe)
                rlayer8= QgsRasterLayer(uri_Mappe, nome_Mappe,'wms')
                myGroup4.insertChildNode(-1, QgsLayerTreeLayer(rlayer8))
                
                nome_Province='Province'
                url_Province ='wms.cartografia.agenziaentrate.gov.it/inspire/wms/ows01.php'
                uri_Province ='crs=EPSG:4258&dpiMode=7&format=image/png&layers=province&styles&url=https://'+requests.utils.quote(url_Province)
                rlayer9= QgsRasterLayer(uri_Province, nome_Province,'wms')
                myGroup4.insertChildNode(-1, QgsLayerTreeLayer(rlayer9))
                
                myGroup6 = group.insertGroup(7, "IGM 2500")
                nome_igm='IGM 25000'
                url_igm ='wms.pcn.minambiente.it/ogc?map=/ms_ogc/WMS_v1.3/raster/IGM_25000.map'
                uri_igm ='crs=EPSG:4806&dpiMode=7&featureCount=10&format=image/png&layers=CB.IGM25000.32&layers=CB.IGM25000.33&styles&styles&url=http://'+requests.utils.quote(url_igm)
                rlayer10= QgsRasterLayer(uri_igm, nome_igm,'wms')
                myGroup6.insertChildNode(-1, QgsLayerTreeLayer(rlayer10))


            
            else:
                pass
            myGroup5 = group.insertGroup(5, "BaseMap")
            basemap_name = 'Google Maps'
            basemap_wiki = 'Wikimedia Maps'
            basemap_url = 'mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}'
            basemap_url_wiki = 'maps.wikimedia.org/osm-intl/{z}/{x}/{y}.png'
            basemap_uri = "type=xyz&zmin=0&zmax=22&url=http://"+requests.utils.quote(basemap_url)
            basemap_uri_wiki = "type=xyz&zmin=0&zmax=22&url=http://"+requests.utils.quote(basemap_url_wiki)
            
            rlayer_wiki= QgsRasterLayer(basemap_uri_wiki, basemap_wiki,'wms')
            rlayer= QgsRasterLayer(basemap_uri, basemap_name,'wms')
            
            
            if rlayer.isValid() and rlayer_wiki.isValid():
                myGroup5.insertChildNode(-1, QgsLayerTreeLayer(rlayer_wiki))
                myGroup5.insertChildNode(-1, QgsLayerTreeLayer(rlayer))
                if self.L=='it':
                    QgsProject.instance().addMapLayers([rlayer11,rlayer_wiki,rlayer,rlayer3,rlayer4,rlayer5,rlayer6,rlayer7,rlayer8,rlayer9,rlayer10],False)
                else:
                    QgsProject.instance().addMapLayers([rlayer_wiki,rlayer],False)
        
        else:
            QMessageBox.warning(self, "Pyarchinit", "Internet Assente o Lento\n Non verranno caricate le Base Map", QMessageBox.StandardButton.Ok)
    
    def enable_button(self, n):
        """This method Unable or Enable the GUI buttons on browse modality"""

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
        """This method Unable or Enable the GUI buttons on searching modality"""

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

    def on_pushButton_connect_pressed(self):
        """This method establishes a connection between GUI and database"""

        conn = Connection()

        conn_str = conn.conn_str()

        test_conn = conn_str.find('sqlite')

        if test_conn == 0:
            self.DB_SERVER = "sqlite"

        try:
            self.DB_MANAGER = get_db_manager(conn_str, use_singleton=True)

            # Get database username and set it in the concurrency manager
            user_info = conn.datauser()
            db_username = user_info.get('user', 'unknown')
            if hasattr(self, 'concurrency_manager'):
                self.concurrency_manager.set_username(db_username)

            self.charge_records()  # charge records from DB
            # check if DB is empty
            if bool(self.DATA_LIST):
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                self.BROWSE_STATUS = 'b'
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.label_sort.setText(self.SORTED_ITEMS["n"])
                self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                self.charge_list()
                self.fill_fields()
            else:
                if self.L=='it':
                    QMessageBox.warning(self,"BENVENUTO", "Benvenuto in pyArchInit " + self.NOME_SCHEDA + ". Il database e' vuoto. Premi 'Ok' e buon lavoro!",
                                        QMessageBox.StandardButton.Ok)
                
                elif self.L=='de':
                    
                    QMessageBox.warning(self,"WILLKOMMEN","WILLKOMMEN in pyArchInit" + "Munsterformular"+ ". Die Datenbank ist leer. Tippe 'Ok' und aufgehts!",
                                        QMessageBox.StandardButton.Ok) 
                else:
                    QMessageBox.warning(self,"WELCOME", "Welcome in pyArchInit" + "Samples form" + ". The DB is empty. Push 'Ok' and Good Work!",
                                        QMessageBox.StandardButton.Ok) 
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

    def charge_list(self):
        sito_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('site_table', 'sito', 'SITE'))

        try:
            sito_vl.remove('')
        except:
            pass
        self.comboBox_sito.clear()
        sito_vl.sort()
        self.comboBox_sito.addItems(sito_vl)
        if self.L=='it':
            regioni_list = ['Abruzzo', 'Basilicata', 'Calabria', 'Campania', 'Emilia-Romagna', 'Friuli Venezia Giulia',
                            'Lazio', 'Liguria', 'Lombardia', 'Marche', 'Molise', 'Piemonte', 'Puglia', 'Sardegna',
                            'Sicilia', 'Toscana', 'Trentino Alto Adige', 'Umbria', 'Valle d\'Aosta', 'Veneto']
            self.comboBox_regione.clear()
            self.comboBox_regione.addItems(regioni_list)

            province_list = ['Agrigento', 'Alessandria', 'Ancona', 'Aosta', 'Arezzo', 'Ascoli Piceno', 'Asti', 'Avellino',
                             'Bari', 'Barletta-Andria-Trani',  'Belluno', 'Benevento', 'Bergamo', 'Biella',
                             'Bologna', 'Bolzano', 'Brescia', 'Brindisi', 'Cagliari',  'Caltanissetta',
                             'Campobasso', 'Carbonia-Iglesias', 'Caserta', 'Catania', 'Catanzaro', 'Chieti',
                             'Como', 'Cosenza', 'Cremona', 'Crotone', 'Cuneo',  'Enna', 'Fermo', 'Ferrara',
                             'Firenze', 'Foggia', "Forlì-Cesena", 'Frosinone', 'Genova', 'Gorizia', 'Grosseto', 'Imperia',
                             'Isernia', "L'Aquila", 'La Spezia', 'Latina', 'Lecce', 'Lecco', 'Livorno', 'Lodi', 'Lucca',
                             'Macerata', 'Mantova', 'Massa e Carrara', 'Matera', 'Medio Campidano', 'Messina', 'Milano',
                             'Modena', 'Monza e Brianza', 'Napoli', 'Novara', 'Nuoro', 'Ogliastra', 'Olbia-Tempio',
                             'Oristano', 'Padova', 'Palermo', 'Parma', 'Pavia', 'Perugia', 'Pesaro e Urbino', 'Pescara',
                             'Piacenza', 'Pisa', 'Pistoia', 'Pordenone', 'Potenza', 'Prato', 'Ragusa', 'Ravenna',
                             'Reggio Calabria', 'Reggio Emilia', 'Rieti', 'Rimini', 'Roma', 'Rovigo', 'Salerno', 'Sassari',
                             'Savona', 'Siena', 'Siracusa', 'Sondrio', 'Taranto', 'Teramo', 'Terni', 'Torino', 'Trapani',
                             'Trento', 'Treviso', 'Trieste', 'Udine', 'Varese', 'Venezia', 'Verbano-Cusio-Ossola',
                             'Vercelli', 'Verona', 'Vibo Valentia', 'Vicenza', 'Viterbo']
            self.comboBox_provincia.clear()
            self.comboBox_provincia.addItems(province_list)
        else:
            regioni_list = []
            self.comboBox_regione.clear()
            self.comboBox_regione.addItems(regioni_list)

            province_list = []
            self.comboBox_provincia.clear()
            self.comboBox_provincia.addItems(province_list)
        l = QgsSettings().value("locale/userLocale", QVariant)
        lang=""
        for key, values in self.LANG.items():
            if values.__contains__(l):
                lang = str(key)
        lang = "'"+lang+"'"

        # lista definizione_sito
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'site_table' + "'",
            'tipologia_sigla': "'" + '1.1' + "'"
        }
        self.comboBox_definizione_sito.clear()
        d_sito = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')

        d_sito_vl = []

        for i in range(len(d_sito)):
            d_sito_vl.append(d_sito[i].sigla_estesa)

        d_sito_vl.sort()
        self.comboBox_definizione_sito.addItems(d_sito_vl)

        # buttons functions

    def on_pushButton_pdf_pressed(self):
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

    def on_pushButton_new_rec_pressed(self):
        if bool(self.DATA_LIST):
            if self.data_error_check() == 1:
                pass
            else:
                if self.BROWSE_STATUS == "b":
                    if self.DATA_LIST:
                        if self.records_equal_check() == 1:
                            if self.L=='it':
                                self.update_if(QMessageBox.warning(self, 'Errore',
                                                                   "Il record e' stato modificato. Vuoi salvare le modifiche?",QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))
                            elif self.L=='de':
                                self.update_if(QMessageBox.warning(self, 'Error',
                                                                   "Der Record wurde geändert. Möchtest du die Änderungen speichern?",
                                                                   QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))
                                                                   
                            else:
                                self.update_if(QMessageBox.warning(self, 'Error',
                                                                   "The record has been changed. Do you want to save the changes?",
                                                                   QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))
                            # set the GUI for a new record
        if self.BROWSE_STATUS != "n":
            self.BROWSE_STATUS = "n"
            self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
            self.empty_fields()
            self.label_sort.setText(self.SORTED_ITEMS["n"])

            self.setComboBoxEnable(["self.comboBox_sito"], "True")
            self.setComboBoxEditable(["self.comboBox_sito"], 1)
            self.setComboBoxEnable(["self.comboBox_definizione_sito"], "True")
            self.setComboBoxEditable(["self.comboBox_definizione_sito"], 1)

            self.set_rec_counter('', '')
            self.enable_button(0)

    def on_pushButton_save_pressed(self):
        # save record
        if self.BROWSE_STATUS == "b":
            
                    # Check for version conflicts before updating
                    if hasattr(self, 'current_record_version') and self.current_record_version:
                        conflict = self.concurrency_manager.check_version_conflict(
                            'site_table',
                            self.editing_record_id,
                            self.current_record_version,
                            self.DB_MANAGER
                        )

                        if conflict and conflict['has_conflict']:
                            # Handle the conflict
                            record_data = self.fill_record()
                            if self.concurrency_manager.handle_conflict(
                                'site_table',
                                record_data,
                                conflict
                            ):
                                # User chose to reload - refresh the form
                                self.charge_records()
                                self.fill_fields(self.REC_CORR)
                                return
                            # Otherwise continue with save (user chose to overwrite)

                    if self.data_error_check() == 0:
                            if self.records_equal_check() == 1:
                                if self.L=='it':
                                    self.update_if(QMessageBox.warning(self, 'Errore',
                                                                       "Il record e' stato modificato. Vuoi salvare le modifiche?",QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))
                                elif self.L=='de':
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
                                if self.L=='it':
                                    QMessageBox.warning(self, "ATTENZIONE", "Non è stata realizzata alcuna modifica.", QMessageBox.StandardButton.Ok)
                                elif self.L=='de':
                                    QMessageBox.warning(self, "ACHTUNG", "Keine Änderung vorgenommen", QMessageBox.StandardButton.Ok)
                                else:
                                    QMessageBox.warning(self, "Warning", "No changes have been made", QMessageBox.StandardButton.Ok)  
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
                    self.setComboBoxEnable(["self.comboBox_sito"], "False")
                    self.fill_fields(self.REC_CORR)
                    self.enable_button(1)
                else:
                    pass

    def data_error_check(self):
        test = 0
        EC = Error_check()
        if self.L=='it':

            if EC.data_is_empty(str(self.comboBox_sito.currentText())) == 0:
                QMessageBox.warning(self, "ATTENZIONE", "Campo Sito. \n Il campo non deve essere vuoto", QMessageBox.StandardButton.Ok)
                test = 1
        elif self.L=='de':  
            if EC.data_is_empty(str(self.comboBox_sito.currentText())) == 0:
                QMessageBox.warning(self, "ACHTUNG", " Feld Ausgrabungstätte. \n Das Feld darf nicht leer sein", QMessageBox.StandardButton.Ok)
                test = 1    
                
        else:   
            if EC.data_is_empty(str(self.comboBox_sito.currentText())) == 0:
                QMessageBox.warning(self, "WARNING", "Site Field. \n The field must not be empty", QMessageBox.StandardButton.Ok)
                test = 1        
        return test

    def insert_new_rec(self):
        try:
            data = self.DB_MANAGER.insert_site_values(
                self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, self.ID_TABLE) + 1,
                str(self.comboBox_sito.currentText()),  # 1 - Sito
                str(self.comboBox_nazione.currentText()),  # 2 - nazione
                str(self.comboBox_regione.currentText()),  # 3 - regione
                str(self.comboBox_comune.currentText()),  # 4 - comune
                str(self.textEdit_descrizione_site.toPlainText()),  # 5 - descrizione
                str(self.comboBox_provincia.currentText()),  # 6 - comune
                str(self.comboBox_definizione_sito.currentText()),  # 7 - definizione sito
                str(self.lineEdit_sito_path.text()), # 8 - path
                0  # 9 - find check
            )

            try:
                self.DB_MANAGER.insert_data_session(data)
                return 1
            except Exception as e:
                e_str = str(e)
                if e_str.__contains__("IntegrityError"):
                    
                    if self.L=='it':
                        msg = self.ID_TABLE + " gia' presente nel database"
                        QMessageBox.warning(self, "Error", "Error" + str(msg), QMessageBox.StandardButton.Ok)
                    elif self.L=='de':
                        msg = self.ID_TABLE + " bereits in der Datenbank"
                        QMessageBox.warning(self, "Error", "Error" + str(msg), QMessageBox.StandardButton.Ok)  
                    else:
                        msg = self.ID_TABLE + " exist in db"
                        QMessageBox.warning(self, "Error", "Error" + str(msg), QMessageBox.StandardButton.Ok)  
                else:
                    msg = e
                    QMessageBox.warning(self, "Error", "Error 1 \n" + str(msg), QMessageBox.StandardButton.Ok)
                return 0

        except Exception as e:
            QMessageBox.warning(self, "Error", "Error 2 \n" + str(e), QMessageBox.StandardButton.Ok)
            return 0

    def check_record_state(self):
        ec = self.data_error_check()
        if ec == 1:
            return 1  # ci sono errori di immissione
        elif self.records_equal_check() == 1 and ec == 0:
            if self.L=='it':
                self.update_if(
                
                    QMessageBox.warning(self, 'Errore', "Il record e' stato modificato. Vuoi salvare le modifiche?",
                                        QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))
            elif self.L=='de':
                self.update_if(
                    QMessageBox.warning(self, 'Errore', "Der Record wurde geändert. Möchtest du die Änderungen speichern?",
                                        QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))
            else:
                self.update_if(
                    QMessageBox.warning(self, "Error", "The record has been changed. You want to save the changes?",
                                        QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))
            # self.charge_records()
            return 0  # non ci sono errori di immissione

            # records surf functions

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

            # records surf functions

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
                QMessageBox.warning(self, "Errore", str(e), QMessageBox.StandardButton.Ok)

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
                QMessageBox.warning(self, "Errore", str(e), QMessageBox.StandardButton.Ok)

    def on_pushButton_prev_rec_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            self.REC_CORR = self.REC_CORR - 1
            if self.REC_CORR == -1:
                self.REC_CORR = 0
                if self.L=='it':
                    QMessageBox.warning(self, "Attenzione", "Sei al primo record!", QMessageBox.StandardButton.Ok)
                elif self.L=='de':
                    QMessageBox.warning(self, "Achtung", "du befindest dich im ersten Datensatz!", QMessageBox.StandardButton.Ok)
                else:
                    QMessageBox.warning(self, "Warning", "You are to the first record!", QMessageBox.StandardButton.Ok)        
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
                if self.L=='it':
                    QMessageBox.warning(self, "Attenzione", "Sei all'ultimo record!", QMessageBox.StandardButton.Ok)
                elif self.L=='de':
                    QMessageBox.warning(self, "Achtung", "du befindest dich im letzten Datensatz!", QMessageBox.StandardButton.Ok)
                else:
                    QMessageBox.warning(self, "Error", "You are to the first record!", QMessageBox.StandardButton.Ok)  
            else:
                try:
                    self.empty_fields()
                    self.fill_fields(self.REC_CORR)
                    self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
                except Exception as e:
                    QMessageBox.warning(self, "Error", str(e), QMessageBox.StandardButton.Ok)

    def on_pushButton_delete_pressed(self):
        
        
        if self.L=='it':
            msg = QMessageBox.warning(self, "Attenzione!!!",
                                      "Vuoi veramente eliminare il record? \n L'azione è irreversibile",
                                      QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            if msg == QMessageBox.StandardButton.Cancel:
                QMessageBox.warning(self, "Messagio!!!", "Azione Annullata!")
            else:
                try:
                    id_to_delete = getattr(self.DATA_LIST[self.REC_CORR], self.ID_TABLE)
                    self.DB_MANAGER.delete_one_record(self.TABLE_NAME, self.ID_TABLE, id_to_delete)
                    self.charge_records()  # charge records from DB
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
                                      QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            if msg == QMessageBox.StandardButton.Cancel:
                QMessageBox.warning(self, "Message!!!", "Aktion annulliert!")
            else:
                try:
                    id_to_delete = getattr(self.DATA_LIST[self.REC_CORR], self.ID_TABLE)
                    self.DB_MANAGER.delete_one_record(self.TABLE_NAME, self.ID_TABLE, id_to_delete)
                    self.charge_records()  # charge records from DB
                    QMessageBox.warning(self, "Message!!!", "Record gelöscht!")
                except Exception as e:
                    QMessageBox.warning(self, "Message!!!", "Errortyp: " + str(e))
                if not bool(self.DATA_LIST):
                    QMessageBox.warning(self, "Achtung", "Die Datenbank ist leer!", QMessageBox.StandardButton.Ok)
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
                                      QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            if msg == QMessageBox.StandardButton.Cancel:
                QMessageBox.warning(self, "Message!!!", "Action deleted!")
            else:
                try:
                    id_to_delete = getattr(self.DATA_LIST[self.REC_CORR], self.ID_TABLE)
                    self.DB_MANAGER.delete_one_record(self.TABLE_NAME, self.ID_TABLE, id_to_delete)
                    self.charge_records()  # charge records from DB
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
            # set the GUI for a new search
            if self.BROWSE_STATUS != "f":
                self.BROWSE_STATUS = "f"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                ###
                self.setComboBoxEnable(["self.comboBox_sito"], "True")
                self.setComboBoxEnable(["self.comboBox_definizione_sito"], "True")
                self.setComboBoxEnable(["self.textEdit_descrizione_site"], "False")
                ###
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.set_rec_counter('', '')
                self.label_sort.setText(self.SORTED_ITEMS["n"])
                self.charge_list()
                self.empty_fields()

    def msg_sito(self):
        #self.model_a.database().close()
        conn = Connection()
        sito_set= conn.sito_set()
        sito_set_str = sito_set['sito_set']
        if bool(self.comboBox_sito.currentText()) and self.comboBox_sito.currentText()==sito_set_str:
            
            if self.L=='it':
                QMessageBox.information(self, "OK" ,"Sei connesso al sito: %s" % str(sito_set_str),QMessageBox.StandardButton.Ok) 
        
            elif self.L=='de':
                QMessageBox.information(self, "OK", "Sie sind mit der archäologischen Stätte verbunden: %s" % str(sito_set_str),QMessageBox.StandardButton.Ok) 
                
            else:
                QMessageBox.information(self, "OK", "You are connected to the site: %s" % str(sito_set_str),QMessageBox.StandardButton.Ok)     
        
        elif sito_set_str=='':    
            if self.L=='it':
                msg = QMessageBox.information(self, "Attenzione" ,"Non hai settato alcun sito. Vuoi settarne uno? click Ok altrimenti Annulla per  vedere tutti i record",QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel) 
            elif self.L=='de':
                msg = QMessageBox.information(self, "Achtung", "Sie haben keine archäologischen Stätten eingerichtet. Klicken Sie auf OK oder Abbrechen, um alle Datensätze zu sehen",QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel) 
            else:
                msg = QMessageBox.information(self, "Warning" , "You have not set up any archaeological site. Do you want to set one? click Ok otherwise Cancel to see all records",QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel) 
            if msg == QMessageBox.StandardButton.Cancel:
                pass
            else: 
                dlg = pyArchInitDialog_Config(self)
                dlg.charge_list()
                dlg.exec()
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

                # Check if we have results before accessing DATA_LIST[0]
                if len(self.DATA_LIST) == 0:
                    if self.L=='it':
                        QMessageBox.information(self, "Attenzione", f"Il sito '{sito_set_str}' non ha record in questa scheda. Crea un nuovo record o disattiva la 'scelta sito' dalla configurazione.", QMessageBox.StandardButton.Ok)
                    elif self.L=='de':
                        QMessageBox.information(self, "Warnung", f"Die Fundstelle '{sito_set_str}' hat keine Datensätze. Erstellen Sie einen neuen Datensatz oder deaktivieren Sie die 'Site-Wahl'.", QMessageBox.StandardButton.Ok)
                    else:
                        QMessageBox.information(self, "Warning", f"Site '{sito_set_str}' has no records in this tab. Create a new record or disable 'site choice' from configuration.", QMessageBox.StandardButton.Ok)
                    return

                self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                self.fill_fields()
                self.BROWSE_STATUS = "b"
                self.SORT_STATUS = "n"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                self.setComboBoxEnable(["self.comboBox_sito"], "False")
            else:
                pass#
        except Exception as e:
            import traceback
            error_msg = str(e)
            traceback_str = traceback.format_exc()
            print(f"[Site.set_sito] Error: {error_msg}\n{traceback_str}")

            if self.L=='it':
                QMessageBox.warning(self, "Errore", f"Errore nel caricamento del sito '{sito_set_str}':\n{error_msg}", QMessageBox.StandardButton.Ok)
            elif self.L=='de':
                QMessageBox.warning(self, "Fehler", f"Fehler beim Laden der Fundstelle '{sito_set_str}':\n{error_msg}", QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.warning(self, "Error", f"Error loading site '{sito_set_str}':\n{error_msg}", QMessageBox.StandardButton.Ok)   
    def on_pushButton_search_go_pressed(self):
        if self.BROWSE_STATUS != "f":
            if self.L=='it':
                QMessageBox.warning(self, "ATTENZIONE", "Per eseguire una nuova ricerca clicca sul pulsante 'new search' ",
                                    QMessageBox.StandardButton.Ok)
            elif self.L=='de':
                QMessageBox.warning(self, "ACHTUNG", "Um eine neue Abfrage zu starten drücke  'new search' ",
                                    QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.warning(self, "WARNING", "To perform a new search click on the 'new search' button ",
                                    QMessageBox.StandardButton.Ok)  
        else:
            search_dict = {
                'sito': "'" + str(self.comboBox_sito.currentText()) + "'",  # 1 - Sito
                'nazione': "'" + str(self.comboBox_nazione.currentText()) + "'",  # 2 - Nazione
                'regione': "'" + str(self.comboBox_regione.currentText()) + "'",  # 3 - Regione
                'comune': "'" + str(self.comboBox_comune.currentText()) + "'",  # 4 - Comune
                'descrizione': str(self.textEdit_descrizione_site.toPlainText()),  # 5 - Descrizione
                'provincia': "'" + str(self.comboBox_provincia.currentText()) + "'",  # 6 - Provincia
                'definizione_sito': "'" + str(self.comboBox_definizione_sito.currentText()) + "'" # 7- definizione_sito
            }

            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)

            if not bool(search_dict):
                if self.L=='it':
                    QMessageBox.warning(self, "ATTENZIONE", "Non è stata impostata nessuna ricerca!!!", QMessageBox.StandardButton.Ok)
                elif self.L=='de':
                    QMessageBox.warning(self, "ACHTUNG", "Keine Abfrage definiert!!!", QMessageBox.StandardButton.Ok)
                else:
                    QMessageBox.warning(self, " WARNING", "No search has been set!!!", QMessageBox.StandardButton.Ok)      
            else:
                res = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
                if not bool(res):
                    if self.L=='it':
                        QMessageBox.warning(self, "ATTENZIONE", "Non è stato trovato nessun record!", QMessageBox.StandardButton.Ok)
                    elif self.L=='de':
                        QMessageBox.warning(self, "ACHTUNG", "Keinen Record gefunden!", QMessageBox.StandardButton.Ok)
                    else:
                        QMessageBox.warning(self, "WARNING," "No record found!", QMessageBox.StandardButton.Ok) 

                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]

                    self.fill_fields(self.REC_CORR)
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])

                    self.setComboBoxEnable(["self.comboBox_sito"], "False")
                    self.setComboBoxEnable(["self.comboBox_definizione_sito"], "True")
                    self.setComboBoxEnable(["self.textEdit_descrizione_site"], "True")
                else:
                    self.DATA_LIST = []
                    for i in res:
                        self.DATA_LIST.append(i)

                    ##                  if self.DB_SERVER == 'sqlite':
                    ##                      for i in self.DATA_LIST:
                    ##                          self.DB_MANAGER.update(self.MAPPER_TABLE_CLASS, self.ID_TABLE, [i.id_sito], ['find_check'], [1])

                    self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]  ####darivedere
                    self.fill_fields()
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)

                    if self.L=='it':
                        if self.REC_TOT == 1:
                            strings = ("E' stato trovato", self.REC_TOT, "record")
                        if self.toolButton_draw_siti.isChecked():
                            sing_layer = [self.DATA_LIST[self.REC_CORR]]
                            #self.pyQGIS.charge_sites_from_research(sing_layer)
                        else:
                            strings = ("Sono stati trovati", self.REC_TOT, "records")
                            #self.pyQGIS.charge_sites_from_research(self.DATA_LIST)
                    
                    elif self.L=='de':
                        if self.REC_TOT == 1:
                            strings = ("Es wurde gefunden", self.REC_TOT, "record")
                        if self.toolButton_draw_siti.isChecked():
                            sing_layer = [self.DATA_LIST[self.REC_CORR]]
                            #self.pyQGIS.charge_sites_from_research(sing_layer)
                        else:
                            strings = ("Sie wurden gefunden", self.REC_TOT, "records")
                            #self.pyQGIS.charge_sites_from_research(self.DATA_LIST)
                            
                    else:
                        if self.REC_TOT == 1:
                            strings = ("It has been found", self.REC_TOT, "record")
                        if self.toolButton_draw_siti.isChecked():
                            sing_layer = [self.DATA_LIST[self.REC_CORR]]
                            #self.pyQGIS.charge_sites_from_research(sing_layer)
                        else:
                            strings = ("They have been found", self.REC_TOT, "records")
                            #self.pyQGIS.charge_sites_from_research(self.DATA_LIST)      
                    self.setComboBoxEnable(["self.comboBox_sito"], "False")
                    self.setComboBoxEnable(["self.comboBox_definizione_sito"], "True")
                    self.setComboBoxEnable(["self.textEdit_descrizione_site"], "True")

                    QMessageBox.warning(self, "Message", "%s %d %s" % strings, QMessageBox.StandardButton.Ok)

        self.enable_button_search(1)

    def on_pushButton_test_pressed(self):
        # Funzione di test rimossa - Test_area non più necessario
        pass

    def on_pushButton_draw_pressed(self):
        self.pyQGIS.charge_layers_for_draw(["19", "12", "10", "7","8","13","16", "3","1", "2", "4", "5", "9","24","26"])

    def on_pushButton_sites_geometry_pressed(self):
        sito = str(self.comboBox_sito.currentText())
        self.pyQGIS.charge_sites_geometry([ "13", "3", "1", "2", "4","24"],
                                          "sito", sito)

    def on_pushButton_draw_sito_pressed(self):
        sing_layer = [self.DATA_LIST[self.REC_CORR]]
        self.pyQGIS.charge_sites_from_research(sing_layer)

    def on_pushButton_rel_pdf_pressed(self):
        check = QMessageBox.warning(self, "Attention",
                                    "Under testing: this method can contains some bugs. Do you want proceed?",
                                    QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        if check == QMessageBox.StandardButton.Ok:
            erp = exp_rel_pdf(str(self.comboBox_sito.currentText()))
            erp.export_rel_pdf()

    def on_toolButton_draw_siti_toggled(self):
        if self.L=='it':
            if self.toolButton_draw_siti.isChecked():
                QMessageBox.warning(self, "Messaggio",
                                    "Modalita' GIS attiva. Da ora le tue ricerche verranno visualizzate sul GIS",
                                    QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.warning(self, "Messaggio",
                                    "Modalita' GIS disattivata. Da ora le tue ricerche non verranno piu' visualizzate sul GIS",
                                    QMessageBox.StandardButton.Ok)
        elif self.L=='de':
            if self.toolButton_draw_siti.isChecked():
                QMessageBox.warning(self, "Message",
                                    "Modalität' GIS aktiv. Von jetzt wird Deine Untersuchung mit Gis visualisiert",
                                    QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.warning(self, "Message",
                                    "Modalität' GIS deaktiviert. Von jetzt an wird deine Untersuchung nicht mehr mit Gis visualisiert",
                                    QMessageBox.StandardButton.Ok)
                                    
        else:
            if self.toolButton_draw_siti.isChecked():
                QMessageBox.warning(self, "Message",
                                    "GIS mode active. From now on your searches will be displayed on the GIS",
                                    QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.warning(self, "Message",
                                    "GIS mode disabled. From now on, your searches will no longer be displayed on the GIS.",
                                    QMessageBox.StandardButton.Ok)
    def on_pushButton_genera_us_pressed(self):
        self.DB_MANAGER.insert_arbitrary_number_of_us_records(int(self.lineEdit_us_range.text()),
                                                              str(self.comboBox_sito.currentText()),
                                                              int(self.lineEdit_area.text()),
                                                              int(self.lineEdit_n_us.text()),
                                                              str(self.comboBox_t_us.currentText()))

        if self.L=='it':
            QMessageBox.warning(self, "Messaggio",
                                    "US create con successo nella Scheda US", QMessageBox.StandardButton.Ok)

        elif self.L=='de':
            QMessageBox.warning(self, "Message",
                                    "TO TRANSLATE: US create con successo nella Scheda US",
                                    QMessageBox.StandardButton.Ok)


        else:
            QMessageBox.warning(self, "Message",
                                    "SU successfully created on SU Sheet",
                                    QMessageBox.StandardButton.Ok)


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
        # Single ordered query - replaces double query pattern for better performance
        self.DATA_LIST = self.DB_MANAGER.query_ordered(self.MAPPER_TABLE_CLASS, self.ID_TABLE, 'asc')

    def datestrfdate(self):
        now = date.today()
        today = now.strftime("%d-%m-%Y")
        return today

    def table2dict(self, n):
        self.tablename = n
        table = getattr(self, self.tablename.replace("self.", "") if self.tablename.startswith("self.") else self.tablename)
        row = table.rowCount()
        col = table.columnCount()
        lista = []
        for r in range(row):
            sub_list = []
            for c in range(col):
                value = table.item(r, c)
                if bool(value):
                    sub_list.append(str(value.text()))
            lista.append(sub_list)
        return lista

    def empty_fields(self):
        self.comboBox_sito.setEditText("")  # 1 - Sito
        self.comboBox_nazione.setEditText("")  # 2 - Nazione
        self.comboBox_regione.setEditText("")  # 3 - Regione
        self.comboBox_comune.setEditText("")  # 4 - Comune
        self.textEdit_descrizione_site.clear()  # 5 - Descrizione
        self.comboBox_provincia.setEditText("")  # 6 - Provincia
        self.comboBox_definizione_sito.setEditText("")  # 7 - definizione_sito
        self.lineEdit_sito_path.setText("") # 8 - path

    def fill_fields(self, n=0):
        self.rec_num = n

        str(self.comboBox_sito.setEditText(self.DATA_LIST[self.rec_num].sito))  # 1 - Sito
        str(self.comboBox_nazione.setEditText(self.DATA_LIST[self.rec_num].nazione))  # 2 - Nazione
        str(self.comboBox_regione.setEditText(self.DATA_LIST[self.rec_num].regione))  # 3 - Regione
        str(self.comboBox_comune.setEditText(self.DATA_LIST[self.rec_num].comune))  # 4 - Comune
        str(self.textEdit_descrizione_site.setText(self.DATA_LIST[self.rec_num].descrizione))  # 5 - Descrizione
        str(self.comboBox_provincia.setEditText(self.DATA_LIST[self.rec_num].provincia))  # 6 - Provincia
        str(self.comboBox_definizione_sito.setEditText(
            self.DATA_LIST[self.rec_num].definizione_sito))  # 7 - definizione_sito
        str(self.lineEdit_sito_path.setText(self.DATA_LIST[self.rec_num].sito_path)) # 8 - path

        # Track version number and record ID for concurrency
        if hasattr(self, 'concurrency_manager'):
            try:
                if n < len(self.DATA_LIST):
                    current_record = self.DATA_LIST[n]
                    if hasattr(current_record, 'version_number'):
                        self.current_record_version = current_record.version_number
                    if hasattr(current_record, 'id_sito'):
                        self.editing_record_id = getattr(current_record, 'id_sito')

                    # Update lock indicator
                    if hasattr(current_record, 'editing_by'):
                        self.lock_indicator.update_lock_status(
                            current_record.editing_by,
                            current_record.editing_since if hasattr(current_record, 'editing_since') else None
                        )

                    # Set soft lock for this record
                    if self.editing_record_id:
                        import getpass
                        current_user = getpass.getuser()
                        # self.DB_MANAGER.set_editing_lock(
                        #     'site_table',
                        #     self.editing_record_id,
                        #     current_user
                        # )
            except Exception as e:
                QgsMessageLog.logMessage(f"Error setting version tracking: {str(e)}", "PyArchInit", Qgis.Warning)


    def set_rec_counter(self, t, c):
        self.rec_tot = t
        self.rec_corr = c
        self.label_rec_tot.setText(str(self.rec_tot))
        self.label_rec_corrente.setText(str(self.rec_corr))

    def check_for_updates(self):
        """Check if current record has been modified by others"""
        try:
            if self.BROWSE_STATUS == "b" and self.editing_record_id and self.DB_MANAGER:
                # Skip check if we're currently saving to avoid false positives
                if hasattr(self, 'is_saving') and self.is_saving:
                    return

                # Determine table name
                table_name = 'site_table'

                # Get current username to skip self-modifications
                current_user = self.concurrency_manager.get_username() if hasattr(self, 'concurrency_manager') else 'unknown'

                has_conflict, db_version, last_modified_by, last_modified_timestamp = \
                    self.concurrency_manager.check_version_conflict(
                        table_name,
                        self.editing_record_id,
                        self.current_record_version,
                        self.DB_MANAGER
                    )

                # Only show conflict if it's a real conflict:
                # - Not a self-modification (different user)
                # - Not a system update
                # - Has actual version change
                if has_conflict and last_modified_by and \
                   last_modified_by != current_user and \
                   last_modified_by.lower() not in ['system', 'postgres'] and \
                   db_version != self.current_record_version:
                    # Show notification
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Icon.Warning)
                    msg.setWindowTitle("Record Modificato / Record Modified")
                    msg.setText(
                        f"Questo record è stato modificato da {last_modified_by} "
                        f"alle {last_modified_timestamp}.\n\n"
                        f"This record was modified by {last_modified_by} "
                        f"at {last_modified_timestamp}.\n\n"
                        f"Vuoi ricaricare il record? / Do you want to reload?"
                    )
                    msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

                    if msg.exec() == QMessageBox.StandardButton.Yes:
                        # Save current record position
                        current_pos = self.REC_CORR
                        # Reload records
                        self.charge_records()
                        # Restore position and fill fields
                        self.fill_fields(current_pos)
                        # Update version after reload
                        self.current_record_version = db_version
        except Exception as e:
            # Log silently to avoid annoying messages
            pass  # QgsMessageLog.logMessage(f"Update check error: {str(e)}", "PyArchInit", Qgis.Info)

    def closeEvent(self, event):
        """Handle form close event - stop refresh timer"""
        # Stop the refresh timer when closing the form
        if hasattr(self, 'refresh_timer') and self.refresh_timer:
            self.refresh_timer.stop()

        # Clear editing state
        if hasattr(self, 'editing_record_id'):
            self.editing_record_id = None

        # Accept the close event
        event.accept()

    def set_LIST_REC_TEMP(self):
        # data
        self.DATA_LIST_REC_TEMP = [
            str(self.comboBox_sito.currentText()),  # 1 - Sito
            str(self.comboBox_nazione.currentText()),  # 2 - Nazione
            str(self.comboBox_regione.currentText()),  # 3 - Regione
            str(self.comboBox_comune.currentText()),  # 4 - Comune
            str(self.textEdit_descrizione_site.toPlainText()),  # 5 - Descrizione
            str(self.comboBox_provincia.currentText()),  # 6 - Provincia
            str(self.comboBox_definizione_sito.currentText()), # 7 - Definizione sito
            str(self.lineEdit_sito_path.text()) # 8 - path
        ]

    def set_LIST_REC_CORR(self):
        self.DATA_LIST_REC_CORR = []
        for i in self.TABLE_FIELDS:
            self.DATA_LIST_REC_CORR.append(str(getattr(self.DATA_LIST[self.REC_CORR], i)))

    def setComboBoxEnable(self, f, v):
        """Set enabled state for widgets"""
        for fn in f:
            widget_name = fn.replace('self.', '') if fn.startswith('self.') else fn
            widget = getattr(self, widget_name, None)
            if widget is not None:
                widget.setEnabled(v == "True")

    def setComboBoxEditable(self, f, n):
        """Set editable state for widgets - uses getattr instead of eval for security"""
        for fn in f:
            widget_name = fn.replace('self.' , '') if fn.startswith('self.' ) else fn
            widget = getattr(self, widget_name, None)
            if widget is not None:
                widget.setEditable(bool(n))

    def rec_toupdate(self):
        rec_to_update = self.UTILITY.pos_none_in_list(self.DATA_LIST_REC_TEMP)
        return rec_to_update

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
                                    "Problema di encoding: sono stati inseriti accenti o caratteri non accettati dal database. Verrà fatta una copia dell'errore con i dati che puoi recuperare nella cartella pyarchinit_Report _Folder", QMessageBox.StandardButton.Ok)
            
            
            elif self.L=='de':
                QMessageBox.warning(self, "Message",
                                    "Encoding problem: accents or characters not accepted by the database were entered. A copy of the error will be made with the data you can retrieve in the pyarchinit_Report _Folder", QMessageBox.StandardButton.Ok) 
            else:
                QMessageBox.warning(self, "Message",
                                    "Kodierungsproblem: Es wurden Akzente oder Zeichen eingegeben, die von der Datenbank nicht akzeptiert werden. Es wird eine Kopie des Fehlers mit den Daten erstellt, die Sie im pyarchinit_Report _Ordner abrufen können", QMessageBox.StandardButton.Ok)                                               
            return 0

    def testing(self, name_file, message):
        f = open(str(name_file), 'w')
        f.write(str(message))
        f.close()
    def get_config(self,  key, default=''):
        # return a config parameter
        return self.config.value('PythonPlugins/pyarchinit/' + key, default )


    def set_config(self,  key,  value):
        # set a config parameter
        return self.config.setValue('PythonPlugins/pyarchinit/' + key, value)

    def reverse(self):
        # Reverse geocoding
        chk = self.check_settings()
        if len(chk) :
            QMessageBox.information(self.iface.mainWindow(), QCoreApplication.translate('pyarchinit geocoding', "pyarchinit geocoding plugin error"), chk)
            return
        sb = self.iface.mainWindow().statusBar()
        sb.showMessage(QCoreApplication.translate('pyarchinit geocoding', "Click on the map to obtain the address"))
        ct = ClickTool(self.iface,  self.reverse_action);
        self.previous_map_tool = self.iface.mapCanvas().mapTool()
        self.iface.mapCanvas().setMapTool(ct)


   # change settings
    def reverse_action(self, point):

        
        geocoder = self.get_geocoder_instance()

        try:
            # reverse lat/lon
            self.logMessage('Reverse clicked point ' + str(point[0]) + ' ' + str(point[1]))
            pt = pointToWGS84(point, self._get_canvas_crs())
            self.logMessage('Reverse transformed point ' + str(pt[0]) + ' ' + str(pt[1]))
            address = geocoder.reverse(pt[0],pt[1])
            self.logMessage(str(address))
            if len(address) == 0:
                QMessageBox.information(self.iface.mainWindow(), QCoreApplication.translate('pyarchinit geocoding', "Reverse pyarchinit geocoding error"), unicode(QCoreApplication.translate('pyarchinit geocoding', "<strong>Empty result</strong>.<br>")))
            else:
                QMessageBox.information(self.iface.mainWindow(), QCoreApplication.translate('GeoCoding', "Reverse pyarchinit geocoding"),  unicode(QCoreApplication.translate('v', "Reverse geocoding found the following address:<br><strong>%s</strong>")) %  address[0][0])
                # save point
                self.save_point(point, address[0][0])
        except Exception as e:
            QMessageBox.information(self.iface.mainWindow(), QCoreApplication.translate('pyarchinit geocoding', "Reverse pyarchinit geocoding error"), unicode(QCoreApplication.translate('pyarchinit geocoding', "<strong>Unhandled exception</strong>.<br>%s" % e)))
        return
    def on_pushButton_locate_pressed(self):
        
        if self.previous_map_tool:
            self.iface.mapCanvas().setMapTool(self.previous_map_tool)
        chk = self.check_settings()
        if len(chk) :
            QMessageBox.information(self.iface.mainWindow(),QCoreApplication.translate('pyarchinit geocoding', "pyarchinit geocoding error"), chk)
            return

        geocoder = self.get_geocoder_instance()
        
        # # create and show the dialog
        # dlg = GeoCodingDialog()
        # # show the dialog
        # dlg.adjustSize()
        # dlg.show()
        #result = DialogSita.exec()
        # # See if OK was pressed
        # if result == 1 :
        try:
            result = geocoder.geocode(unicode(self.address.text()).encode('utf-8'))
        except Exception as e:
            QMessageBox.information(self.iface.mainWindow(), QCoreApplication.translate('pyarchinit geocoding', "pyarchinit geocoding plugin error"), QCoreApplication.translate('GeoCoding', "Sembra esserci un errore con il servizio geocoding:<br><strong>%s</strong>"% e+"\n\n Controlla l'indirizzo" ))
            return

        if not result:
            QMessageBox.information(self.iface.mainWindow(), QCoreApplication.translate('pyarchinit geocoding', "Not found"), QCoreApplication.translate('pyarchinit geocoding', "Questo indirizzo non esiste: <strong>%s</strong>." % self.address.text()))
            return

        places = {}
        for place, point in result:
            places[place] = point

        if len(places) == 1:
            self.process_point(place, point)
        else:
            #all_str = QCoreApplication.translate('pyarchinit geocoding', 'Tutti')
            place_dlg = PlaceSelectionDialog()
            #place_dlg.placesComboBox.addItem(all_str)
            place_dlg.placesComboBox.addItems(places.keys())
            place_dlg.show()
            result = place_dlg.exec()
            # if result == 1 :
                # if place_dlg.placesComboBox.currentText() == 'Tutti':
                    # for place in places:
                        # self.process_point(place, places[place])
                # else:
            point = places[unicode(place_dlg.placesComboBox.currentText())]
            self.process_point(place_dlg.placesComboBox.currentText(), point)
        return
    
    def logMessage(self, msg):
        if self.get_config('writeDebug'):
            QgsMessageLog.logMessage(msg, 'GeoCoding')
    def get_geocoder_instance(self):
        """
        Loads a concrete Geocoder class
        """

        #geocoder_class = str(self.get_config('GeocoderClass'))

        #if not geocoder_class:
        geocoder_class ='Nominatim'

        #if geocoder_class == 'Nominatim':
        return OsmGeoCoder()
        # else:
            # return GoogleGeoCoder(self.get_config('googleKey'))



    def process_point(self, place, point):
        """
        Transforms the point and save
        """
        # lon lat and transform
        point = QgsPoint(float(point[0]), float(point[1]))
        point = pointFromWGS84(point, self._get_layer_crs())
        
        # Set the extent to our new point
        self.canvas.setCenter(point)

        scale = float(self.get_config('ZoomScale', 200))
        # adjust scale to display correct scale in qgis
        if scale:
            self.canvas.zoomScale(scale)

        # Refresh the map
        self.canvas.refresh()
        # save point
        self.save_point(point, unicode(place))

    def _get_layer_crs(self):
        """get CRS from destination layer or from canvas if the layer does not exist"""
        try:
            return self.currentLayerId.crs()
        except:
            return self._get_canvas_crs()


    def _get_canvas_crs(self):
        """compat"""
        try:
            return self.iface.mapCanvas().mapRenderer().destinationCrs()
        except:
            return self.iface.mapCanvas().mapSettings().destinationCrs()

    def _get_registry(self):
        """compat"""
        try:
            return QgsMapLayerRegistry.instance()
        except:
            return QgsProject.instance()

    # save point to file, point is in project's crs
    def save_point(self, point, address):
        try:
            sourceLYR = QgsProject.instance().mapLayersByName('Pyrchinit localizzazione trovata')[0]
            QgsProject.instance().removeMapLayer(sourceLYR)  
        except:
            pass
        self.logMessage('Saving point ' + str(point[0])  + ' ' + str(point[1]))
        # create and add the point layer if not exists or not set
        if not self._get_registry().mapLayer(self.layerid) :
            # create layer with same CRS as map canvas
            crs = self._get_canvas_crs()
            self.layer = QgsVectorLayer("Point?crs=" + crs.authid(), "Pyrchinit localizzazione trovata", "memory")
            self.provider = self.layer.dataProvider()

            # add fields
            self.provider.addAttributes([QgsField("id", QVariant.Int)])
            self.provider.addAttributes([QgsField("indirizzo", QVariant.String)])

            # BUG: need to explicitly call it, should be automatic!
            self.layer.updateFields()

            # Labels on
            try:
                label_settings = QgsPalLayerSettings()
                label_settings.fieldName = "sito"
                self.layer.setLabeling(QgsVectorLayerSimpleLabeling(label_settings))
                self.layer.setLabelsEnabled(True)
            except:
                self.layer.setCustomProperty("labeling", "pal")
                self.layer.setCustomProperty("labeling/enabled", "true")
                self.layer.setCustomProperty("labeling/fontFamily", "Arial")
                self.layer.setCustomProperty("labeling/fontSize", "12")
                self.layer.setCustomProperty("labeling/multilineAlign", "0" )
                self.layer.layer.setCustomProperty("labeling/bufferDraw", True)
                self.layer.setCustomProperty("labeling/namedStyle", "Bold")
                self.layer.setCustomProperty("labeling/fieldName", "sito")
                self.layer.setCustomProperty("labeling/placement", "2")

            # add layer if not already
            self._get_registry().addMapLayer(self.layer)

            # store layer id
            self.layerid = self.layer.id()


        # add a feature
        try:
            fields=self.layer.pendingFields()
        except:
            fields=self.layer.fields()

        fet = QgsFeature(fields)
        try:
            fet.setGeometry(QgsGeometry.fromPoint(point))
        except:
            fet.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(point)))

        try: # QGIS < 1.9
            
            fet.setAttributeMap({0 : 1})
            fet.setAttributeMap({1 : address})
        except: # QGIS >= 1.9
            fet['id']=1
            fet['indirizzo'] = address

        self.layer.startEditing()
        self.layer.addFeatures([ fet ])
        self.layer.commitChanges()
        self.canvas.refresh()
        # res = QMessageBox.information(self, 'PyArchInit',"Vuoi settarlo come sito?\n Schiaccia ok altrimenti verrà visualizzato solo la localizzazione", QMessageBox.Ok | QMessageBox.Cancel)
            
        # if res==QMessageBox.Ok:
            # conn = Connection()
            # conn_str = conn.conn_str()
            # conn_sqlite = conn.databasename()
            # conn_user = conn.datauser()
            # conn_host = conn.datahost()
            # conn_port = conn.dataport()
            # port_int  = conn_port["port"]
            # port_int.replace("'", "")
            


            
            # self.DB_MANAGER = Pyarchinit_db_management(conn_str)
            # self.DB_MANAGER.connection()
            # test_conn = conn_str.find('sqlite')
            # if test_conn == 0:
                # sqlite_DB_path = '{}{}{}'.format(self.HOME, os.sep,
                                               # "pyarchinit_DB_folder")
                # uri = QgsDataSourceUri()
                # uri.setDatabase(sqlite_DB_path +os.sep+ conn_sqlite["db_name"])
                # schema = ''
                
                    
                # table = 'site_table'
                
                # uri.setDataSource(schema, table,'')
                #sourceLYR = QgsProject.instance().mapLayersByName('Pyrchinit localizzazione trovata')[0]
                #puntiLYR2 = QgsProject.instance().mapLayersByName('Localizzazione siti puntuale')[0]
        layer_provider = self.layer.dataProvider()
        layer_provider.addAttributes([QgsField("sito", QVariant.String)])     
        layer_provider.addAttributes([QgsField("nazione", QVariant.String)])                
        layer_provider.addAttributes([QgsField("regione", QVariant.String)])
        layer_provider.addAttributes([QgsField("comune", QVariant.String)])
        layer_provider.addAttributes([QgsField("descrizione", QVariant.String)])
        layer_provider.addAttributes([QgsField("provincia", QVariant.String)])
        
        self.layer.updateFields()

       
        self.layer.startEditing()
        # ID_Sito = QInputDialog.getText(None, 'Sito', 'Input Nome del sito archeologico')
        # Sito = str(ID_Sito[0])
        features = []
        for f in self.layer.getFeatures():
            s = {2: f['indirizzo'].split(',')[0]}
            layer_provider.changeAttributeValues({f.id(): s})
            nazione = {3: f['indirizzo'].split(',')[-1]}
            layer_provider.changeAttributeValues({f.id(): nazione})
            regione = {4: f['indirizzo'].split(',')[-3]}
            layer_provider.changeAttributeValues({f.id(): regione})                    
            comune = {5: f['indirizzo'].split(',')[1]}
            layer_provider.changeAttributeValues({f.id(): comune})
            provincia = {7: f['indirizzo'].split(',')[-4]}
            layer_provider.changeAttributeValues({f.id(): provincia})
        
        for feature in self.layer.getFeatures():
            
            sito=feature.attributes()[2]
            feature.setAttribute('sito', sito)
            na=feature.attributes()[3]
            feature.setAttribute('nazione', na)
            r=feature.attributes()[4]
            feature.setAttribute('regione', r)             
            comune=feature.attributes()[5]
            feature.setAttribute('comune', comune)
            pr=feature.attributes()[6]
            feature.setAttribute('descrizione','')
            pr=feature.attributes()[7]
            feature.setAttribute('provincia', pr)
            
            self.layer.updateFeature(feature)
            
            features.append(feature)
        self.layer.commitChanges()    
                # destLYR1 = QgsVectorLayer(uri.uri(), table, 'spatialite') 
                # destLYR1.commitChanges()
                # destLYR1.startEditing()
                # data_provider = destLYR1.dataProvider()
                # data_provider.addFeatures(features)
                # destLYR1.commitChanges()
                
                # res = QMessageBox.information(self, 'PyArchInit',"Vuoi salvare il sito", QMessageBox.Ok | QMessageBox.Cancel)
                # if res==QMessageBox.Ok:
                    # f=[]
                    # for feature in self.layer.getFeatures():
                        # f.append(feature)
                    # puntiLYR2 = QgsProject.instance().mapLayersByName('Localizzazione siti puntuale')[0]
                    # puntiLYR2.startEditing()
                    # data_provider2 = puntiLYR2.dataProvider()
                    # data_provider2.addFeatures(f)
                    # puntiLYR2.commitChanges()
                    
            # else:
                # uri = QgsDataSourceUri()
                # uri.setConnection(conn_host["host"], conn_port["port"], conn_sqlite["db_name"], conn_user['user'], conn_password['password'])
                # schema = 'public'
                # table = 'site_table'
                # geom_column = ''
                # uri.setDataSource(schema, table,geom_column)
                # sourceLYR = QgsProject.instance().mapLayersByName('Pyrchinit localizzazione trovata')[0]
                # puntiLYR2 = QgsProject.instance().mapLayersByName('Localizzazione siti puntuale')[0]
                # layer_provider = sourceLYR.dataProvider()
                # layer_provider.addAttributes([QgsField("sito", QVariant.String)])     
                # layer_provider.addAttributes([QgsField("nazione", QVariant.String)])                
                # layer_provider.addAttributes([QgsField("regione", QVariant.String)])
                # layer_provider.addAttributes([QgsField("comune", QVariant.String)])
                # layer_provider.addAttributes([QgsField("descrizione", QVariant.String)])
                # layer_provider.addAttributes([QgsField("provincia", QVariant.String)])
                
                # sourceLYR.updateFields()

               
                # # sourceLYR.startEditing()
                # # ID_Sito = QInputDialog.getText(None, 'Sito', 'Input Nome del sito archeologico')
                # # Sito = str(ID_Sito[0])
                # features = []
                # for f in sourceLYR.getFeatures():
                    # s = {1: f['indirizzo'].split(',')[0]}
                    # layer_provider.changeAttributeValues({f.id(): s})
                    # nazione = {2: f['indirizzo'].split(',')[-1]}
                    # layer_provider.changeAttributeValues({f.id(): nazione})
                    # regione = {3: f['indirizzo'].split(',')[-3]}
                    # layer_provider.changeAttributeValues({f.id(): regione})                    
                    # comune = {4: f['indirizzo'].split(',')[1]}
                    # layer_provider.changeAttributeValues({f.id(): comune})
                    # provincia = {6: f['indirizzo'].split(',')[-4]}
                    # layer_provider.changeAttributeValues({f.id(): provincia})
                # sourceLYR.commitChanges()    
                # for feature in sourceLYR.getFeatures():
                    
                    # sito=feature.attributes()[1]
                    # feature.setAttribute('sito', sito)            
                    # na=feature.attributes()[2]
                    # feature.setAttribute('nazione', na)
                    # r=feature.attributes()[3]
                    # feature.setAttribute('regione', r)             
                    # comune=feature.attributes()[4]
                    # feature.setAttribute('comune', comune)
                    # pr=feature.attributes()[5]
                    # feature.setAttribute('descrizione','')
                    # pr=feature.attributes()[6]
                    # feature.setAttribute('provincia', pr)
                    # features.append(feature)
                    # sourceLYR.updateFeature(feature)
                    
                
                # destLYR = QgsVectorLayer(uri.uri(), table, 'postgres')    
                # destLYR.startEditing()
                # data_provider = destLYR.dataProvider()
                # data_provider.addFeatures(features)
                # destLYR.commitChanges()

                # table2 = 'pyarchinit_siti'
                # geom_column = 'the_geom'
                # uri.setDataSource(schema, table2, geom_column)
                # features2 = []
                # for feature in sourceLYR.getFeatures():
                    # features2.append(feature)
                    # feature.setAttribute('comune', '')
                    # feature.setAttribute('nazione', '')
                    # sito = feature.attributes()[1]
                    # feature.setAttribute('sito', sito)

                    # sourceLYR.updateFeature(feature)
                    
                # #puntiLYR2 = QgsVectorLayer(uri.uri(), table2, 'spatialite')
                # puntiLYR2.startEditing()
                # data_provider2 = puntiLYR2.dataProvider()
                # data_provider2.addFeatures(features2)
                # puntiLYR2.commitChanges()
            # destLYR1.commitChanges()
            
            # #QgsProject.instance().removeMapLayer(sourceLYR)          
        # else:
            # pass
   
        
    def check_settings (self):
        p = QgsProject.instance()
        error = ''
        if QT_VERSION==4:
            if not self.iface.mapCanvas().hasCrsTransformEnabled() and self.iface.mapCanvas().mapRenderer().destinationCrs().authid() != 'EPSG:4326':
                error = QCoreApplication.translate('pyarchinit geocoding', "On-the-fly reprojection must be enabled if the destination CRS is not EPSG:4326. Please enable on-the-fly reprojection.")

        return error
## Class end


def logMessage(msg):
    if QgsSettings().value('PythonPlugins/pyarchinit/writeDebug'):
        QgsMessageLog.logMessage(msg, 'GeoCoding')
class GeoCodeException(Exception):
    pass
class OsmGeoCoder():

    url = 'https://nominatim.openstreetmap.org/search?format=json&q={address}'
    reverse_url = 'https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}'

    def geocode(self, address):
        try: 
            url = self.url.format(**{'address': address.decode('utf8')})
            logMessage(url)
            results = json.loads(NAM.request(url, blocking=True)[1].decode('utf8'))
            return [(rec['display_name'], (rec['lon'], rec['lat'])) for rec in results]
        except Exception as e:
            raise GeoCodeException(str(e))

    def reverse(self, lon, lat):
        """single result"""
        try: 
            url = self.reverse_url.format(**{'lon': lon, 'lat': lat})
            logMessage(url)
            rec = json.loads(NAM.request(url, blocking=True)[1].decode('utf8'))
            return [(rec['display_name'], (rec['lon'], rec['lat']))]
        except Exception as e:
            raise GeoCodeException(str(e))

