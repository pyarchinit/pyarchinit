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
from datetime import datetime, date
from qgis.PyQt.QtWidgets import (
    QDialog, QMessageBox, QTableWidgetItem, QHeaderView, QFileDialog,
    QPushButton, QHBoxLayout, QVBoxLayout, QDoubleSpinBox, QLabel,
    QGroupBox, QFormLayout, QTabWidget, QWidget, QButtonGroup,
)
from qgis.PyQt.QtCore import Qt, QTimer
from qgis.PyQt.uic import loadUiType
from qgis.core import QgsSettings, QgsProject, QgsRasterLayer, QgsVectorLayer

from ..modules.utility.pyarchinit_theme_manager import ThemeManager
from ..modules.utility import pyarchinit_dem_visualizer as dem_viz
from ..modules.db.pyarchinit_conn_strings import Connection
from ..modules.db.pyarchinit_db_manager import get_db_manager
from ..modules.db.pyarchinit_utility import Utility

MAIN_DIALOG_CLASS, _ = loadUiType(
    os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'Cantiere.ui'))


class pyarchinit_Cantiere(QDialog, MAIN_DIALOG_CLASS):
    L = QgsSettings().value("locale/userLocale", "it", type=str)[:2]
    DB_MANAGER = None
    DB_SERVER = "not defined"
    UTILITY = Utility()

    # i18n titles (10 languages)
    if L == 'it':
        MSG_BOX_TITLE = "PyArchInit - Dashboard Cantiere"
    elif L == 'en':
        MSG_BOX_TITLE = "PyArchInit - Site Dashboard"
    elif L == 'de':
        MSG_BOX_TITLE = "PyArchInit - Baustellen-Dashboard"
    elif L == 'es':
        MSG_BOX_TITLE = "PyArchInit - Panel de Obra"
    elif L == 'fr':
        MSG_BOX_TITLE = "PyArchInit - Tableau de Bord"
    elif L == 'ar':
        MSG_BOX_TITLE = "PyArchInit - \u0644\u0648\u062d\u0629 \u0627\u0644\u0642\u064a\u0627\u062f\u0629"
    elif L == 'ca':
        MSG_BOX_TITLE = "PyArchInit - Tauler d'Obra"
    elif L == 'ro':
        MSG_BOX_TITLE = "PyArchInit - Panou Santier"
    elif L == 'pt':
        MSG_BOX_TITLE = "PyArchInit - Painel de Obra"
    elif L == 'el':
        MSG_BOX_TITLE = "PyArchInit - \u03a0\u03af\u03bd\u03b1\u03ba\u03b1\u03c2 \u0395\u03c1\u03b3\u03bf\u03c4\u03b1\u03be\u03af\u03bf\u03c5"
    else:
        MSG_BOX_TITLE = "PyArchInit - Site Dashboard"

    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.setupUi(self)
        ThemeManager.apply_theme(self)
        self.theme_toggle_btn = ThemeManager.add_theme_toggle_to_form(self)
        self.retranslate_ui()

        # State tracking for 2D / 3D visualization
        # populated after each successful "Calcola" run
        self._last_calc = {
            'diff_raster_path': None,
            'diff_raster_layer': None,
            'poly_layer': None,
            'terrain_layer': None,
            'layer_post': None,
            'clip_poly_layer': None,
            'mesh_pre_layer': None,
            'mesh_post_layer': None,
            'stats': None,
            'sito': None,
            'tipo': None,
        }

        # Programmatically inject extra dashboard buttons (2D/3D visualize)
        # so existing .ui files remain backward-compatible.
        self._inject_viz_buttons()
        self._inject_walls_combo()
        self._inject_cost_panel()
        # Force the two calculation-mode radio buttons into an explicit
        # QButtonGroup so mutual exclusion is guaranteed regardless of
        # reparenting / theme quirks. Also hard-set the default to
        # "Differenza DEM" after setupUi in case the .ui default did
        # not survive the theme/style round-trip.
        self._wire_calc_mode_radios()
        # Reorganize the dense top-level layout into a QTabWidget AFTER
        # the cost panel + viz buttons are injected, so those widgets are
        # moved along with the Computo Metrico group box.
        self._reorganize_into_tabs()

    def _wire_calc_mode_radios(self):
        """
        Historical: the Computo Metrico panel exposed two radio buttons
        (``radioButton_diff_dem`` / ``radioButton_dem_poligono``) to
        choose between the DEM-difference workflow (two DEMs) and a
        single-DEM zonal-stats workflow. The polygon-only mode turned
        out to be a UX trap: users habitually clicked the wrong radio
        and then complained that "it clips the same DEM".

        The polygon-only code path is still present in
        ``calculate_dem_polygon()`` for backward compatibility (existing
        `COMPUTO_METRICO` records of that type still render correctly),
        but the radio is **hidden** — the dispatcher in
        ``on_pushButton_calcola_pressed`` now always runs the
        DEM-difference flow. A polygon layer picked in "Layer Poligono"
        is used as a clip mask for that flow (and walls as exclusion).
        """
        try:
            rb_diff = getattr(self, 'radioButton_diff_dem', None)
            rb_poly = getattr(self, 'radioButton_dem_poligono', None)
            if rb_diff is not None:
                rb_diff.setChecked(True)
                rb_diff.setVisible(False)
            if rb_poly is not None:
                rb_poly.setChecked(False)
                rb_poly.setVisible(False)
        except Exception:
            pass

        # Connect signals
        self.pushButton_refresh.clicked.connect(self.refresh_dashboard)
        self.pushButton_calcola.clicked.connect(self.on_pushButton_calcola_pressed)
        self.pushButton_salva_computo.clicked.connect(self.on_pushButton_salva_computo_pressed)
        self.comboBox_sito.currentTextChanged.connect(self.refresh_dashboard)
        self.comboBox_sito.currentTextChanged.connect(self._load_cost_settings)
        self.comboBox_anno.currentTextChanged.connect(self.refresh_dashboard)
        self.pushButton_export_pdf.clicked.connect(self.on_pushButton_export_pdf_pressed)
        self.pushButton_export_excel.clicked.connect(self.on_pushButton_export_excel_pressed)

        # Defer DB loading so the window shows instantly
        QTimer.singleShot(0, self._deferred_init)

    def _inject_viz_buttons(self):
        """Add "Show 2D" and "Show 3D" buttons next to Calcola, if missing."""
        try:
            parent_layout = self.pushButton_calcola.parent().layout()
            if parent_layout is None:
                return
            labels = {
                'it': ('Mostra 2D', 'Mostra 3D', 'Esporta 2DM + 3D'),
                'en': ('Show 2D', 'Show 3D', 'Export 2DM + 3D'),
                'de': ('2D anzeigen', '3D anzeigen', '2DM-Export + 3D'),
                'es': ('Ver 2D', 'Ver 3D', 'Exportar 2DM + 3D'),
                'fr': ('Voir 2D', 'Voir 3D', 'Exporter 2DM + 3D'),
                'ar': ('عرض 2D', 'عرض 3D', 'تصدير 2DM + 3D'),
                'ca': ('Veure 2D', 'Veure 3D', 'Exportar 2DM + 3D'),
                'ro': ('Vezi 2D', 'Vezi 3D', 'Export 2DM + 3D'),
                'pt': ('Ver 2D', 'Ver 3D', 'Exportar 2DM + 3D'),
                'el': ('Προβολή 2D', 'Προβολή 3D', 'Εξαγωγή 2DM + 3D'),
            }
            lbl_2d, lbl_3d, lbl_mesh = labels.get(self.L, labels['en'])

            self.pushButton_show_2d = QPushButton(lbl_2d)
            self.pushButton_show_2d.setEnabled(False)
            self.pushButton_show_2d.setToolTip(
                "Zoom the map canvas to the last computed DEM difference.")
            self.pushButton_show_2d.clicked.connect(self._on_show_2d)

            self.pushButton_show_3d = QPushButton(lbl_3d)
            self.pushButton_show_3d.setEnabled(False)
            self.pushButton_show_3d.setToolTip(
                "Open an interactive 3D view of the DEM difference.")
            self.pushButton_show_3d.clicked.connect(self._on_show_3d)

            self.pushButton_build_mesh = QPushButton(lbl_mesh)
            self.pushButton_build_mesh.setEnabled(False)
            self.pushButton_build_mesh.setToolTip(
                "Export a 2DM mesh of pre/post DEMs to disk and open "
                "the 3D surface view. Does NOT load the mesh in QGIS "
                "(avoids crashes on some builds).")
            self.pushButton_build_mesh.clicked.connect(self._on_build_mesh)

            # Compact styling to match existing buttons
            for btn in (self.pushButton_show_2d, self.pushButton_show_3d,
                        self.pushButton_build_mesh):
                f = btn.font()
                f.setPointSize(8)
                btn.setFont(f)

            # Insert after the Calcola button (which sits in its own row
            # layout). We insert them into the same row in order.
            idx = -1
            for i in range(parent_layout.count()):
                item = parent_layout.itemAt(i)
                if item and item.widget() is self.pushButton_calcola:
                    idx = i
                    break
            if idx >= 0:
                parent_layout.insertWidget(idx + 1, self.pushButton_show_2d)
                parent_layout.insertWidget(idx + 2, self.pushButton_show_3d)
                parent_layout.insertWidget(idx + 3, self.pushButton_build_mesh)
            else:
                parent_layout.addWidget(self.pushButton_show_2d)
                parent_layout.addWidget(self.pushButton_show_3d)
                parent_layout.addWidget(self.pushButton_build_mesh)
        except Exception:
            # Non-fatal: dashboard still works without the visualize buttons.
            pass

    # --------------------------------------------- walls combo (inject) --

    def _inject_walls_combo(self):
        """
        Add a second polygon combo box below the existing "Layer Poligono"
        combo, used to pick a layer of walls / built structures that must
        be **excluded** from the volume calculation (their cells get
        rasterised to NODATA on the clipped diff raster so they are not
        counted as earth).
        """
        try:
            # The existing layer-poligono combo lives in gridLayout_computo
            # (row 2, col 1 per the .ui). We find its parent grid layout
            # and append a new row below it.
            anchor = getattr(self, 'comboBox_layer_poligono', None)
            if anchor is None:
                return
            # Walk up to find the QGridLayout the combo is placed in.
            parent_widget = anchor.parentWidget()
            if parent_widget is None:
                return
            grid = parent_widget.layout()
            from qgis.PyQt.QtWidgets import QGridLayout, QComboBox
            if not isinstance(grid, QGridLayout):
                # Fall back: append below instead of in-grid
                grid = None

            labels = {
                'it': 'Muri / Strutture:',
                'en': 'Walls / Structures:',
                'de': 'Mauern / Strukturen:',
                'es': 'Muros / Estructuras:',
                'fr': 'Murs / Structures:',
                'ar': '\u062c\u062f\u0631\u0627\u0646 / \u0647\u064a\u0627\u0643\u0644:',
                'ca': 'Murs / Estructures:',
                'ro': 'Ziduri / Structuri:',
                'pt': 'Muros / Estruturas:',
                'el': '\u03a4\u03bf\u03af\u03c7\u03bf\u03b9 / \u0394\u03bf\u03bc\u03ad\u03c2:',
            }
            lbl_text = labels.get(self.L, labels['en'])

            self.label_layer_muri = QLabel(lbl_text)
            self.comboBox_layer_muri = QComboBox()
            self.comboBox_layer_muri.setEditable(True)
            self.comboBox_layer_muri.addItem('')
            self.comboBox_layer_muri.setToolTip(
                'Polygon layer of walls or built structures to '
                'EXCLUDE from the cubic-meter calculation. The cells '
                'inside these polygons are burned as NODATA on the '
                'clipped DEM-difference raster.')

            # Place it in the grid just below the existing polygon row
            if grid is not None:
                # Find the row of comboBox_layer_poligono
                row_found = -1
                for r in range(grid.rowCount()):
                    for c in range(grid.columnCount()):
                        it = grid.itemAtPosition(r, c)
                        if it is not None and it.widget() is anchor:
                            row_found = r
                            break
                    if row_found >= 0:
                        break
                if row_found >= 0:
                    # Shift any subsequent rows down by 1 is hard with
                    # QGridLayout; simplest: just add at the last row + 1.
                    last_row = grid.rowCount()
                    grid.addWidget(self.label_layer_muri, last_row, 0)
                    grid.addWidget(self.comboBox_layer_muri, last_row, 1)
                else:
                    grid.addWidget(self.label_layer_muri, grid.rowCount(), 0)
                    grid.addWidget(self.comboBox_layer_muri, grid.rowCount(), 1)
            else:
                # Append to whatever layout we have
                parent_widget.layout().addWidget(self.label_layer_muri)
                parent_widget.layout().addWidget(self.comboBox_layer_muri)
        except Exception:
            pass

    def _populate_walls_combo(self):
        """Populate the walls combo with polygon vector layers from the project."""
        if not hasattr(self, 'comboBox_layer_muri'):
            return
        prev = self.comboBox_layer_muri.currentData()
        self.comboBox_layer_muri.blockSignals(True)
        self.comboBox_layer_muri.clear()
        self.comboBox_layer_muri.addItem('')
        for layer_id, layer in QgsProject.instance().mapLayers().items():
            if isinstance(layer, QgsVectorLayer):
                self.comboBox_layer_muri.addItem(layer.name(), layer_id)
        if prev:
            idx = self.comboBox_layer_muri.findData(prev)
            if idx >= 0:
                self.comboBox_layer_muri.setCurrentIndex(idx)
        self.comboBox_layer_muri.blockSignals(False)

    # -------------------------------------------------- cost panel (inject) --

    # Settings keys (persisted per-site via QgsSettings)
    _COST_SETTINGS_PREFIX = 'pyArchInit/site_dashboard/costs'

    def _inject_cost_panel(self):
        """
        Add a small "Analisi Costi / Cost Analysis" group-box to the
        Computo Metrico panel with:
          - €/m³ input (unit cost)
          - m³/day input (production rate)
          - computed labels: total cost, estimated days, daily cost

        Values are persisted per-site in QgsSettings under
        ``pyArchInit/site_dashboard/costs/<sito>/*``.
        """
        try:
            # Insertion target: the same vertical layout that holds the
            # Computo Metrico grid. We piggy-back on the layout of the
            # salva_computo button's parent.
            anchor = getattr(self, 'pushButton_salva_computo', None)
            if anchor is None:
                return
            parent_layout = anchor.parent().layout()
            if parent_layout is None:
                return

            labels = self._cost_labels()

            self.groupBox_costi = QGroupBox(labels['title'])
            form = QFormLayout(self.groupBox_costi)
            form.setContentsMargins(6, 6, 6, 6)
            form.setSpacing(4)

            self.spinBox_cost_per_m3 = QDoubleSpinBox()
            self.spinBox_cost_per_m3.setRange(0.0, 99_999.99)
            self.spinBox_cost_per_m3.setDecimals(2)
            self.spinBox_cost_per_m3.setSingleStep(1.0)
            self.spinBox_cost_per_m3.setSuffix(' \u20ac/m\u00b3')
            self.spinBox_cost_per_m3.valueChanged.connect(self._recompute_costs)
            form.addRow(QLabel(labels['cost_m3']), self.spinBox_cost_per_m3)

            self.spinBox_prod_m3_day = QDoubleSpinBox()
            self.spinBox_prod_m3_day.setRange(0.0, 9_999.99)
            self.spinBox_prod_m3_day.setDecimals(2)
            self.spinBox_prod_m3_day.setSingleStep(0.5)
            self.spinBox_prod_m3_day.setSuffix(' m\u00b3/day')
            self.spinBox_prod_m3_day.valueChanged.connect(self._recompute_costs)
            form.addRow(QLabel(labels['prod_rate']), self.spinBox_prod_m3_day)

            self.label_costo_totale = QLabel('\u2014')
            self.label_costo_totale.setStyleSheet('font-weight:bold;')
            form.addRow(QLabel(labels['total_cost']), self.label_costo_totale)

            self.label_giorni_stimati = QLabel('\u2014')
            self.label_giorni_stimati.setStyleSheet('font-weight:bold;')
            form.addRow(QLabel(labels['days']), self.label_giorni_stimati)

            self.label_costo_giornaliero = QLabel('\u2014')
            self.label_costo_giornaliero.setStyleSheet('font-weight:bold;')
            form.addRow(QLabel(labels['daily_cost']), self.label_costo_giornaliero)

            # Insert the groupbox right after the Salva Computo button
            idx = -1
            for i in range(parent_layout.count()):
                item = parent_layout.itemAt(i)
                if item and item.widget() is anchor:
                    idx = i
                    break
            if idx >= 0:
                parent_layout.insertWidget(idx + 1, self.groupBox_costi)
            else:
                parent_layout.addWidget(self.groupBox_costi)

            # Load persisted values for the current site + recompute
            self._load_cost_settings()
        except Exception:
            pass

    def _cost_labels(self):
        """Locale-aware labels for the cost panel."""
        T = {
            'it': {
                'title': 'Analisi Costi',
                'cost_m3': 'Costo unitario:',
                'prod_rate': 'Produttivit\u00e0:',
                'total_cost': 'Costo totale:',
                'days': 'Giorni stimati:',
                'daily_cost': 'Costo giornaliero:',
            },
            'en': {
                'title': 'Cost Analysis',
                'cost_m3': 'Unit cost:',
                'prod_rate': 'Production rate:',
                'total_cost': 'Total cost:',
                'days': 'Estimated days:',
                'daily_cost': 'Daily cost:',
            },
            'de': {
                'title': 'Kostenanalyse',
                'cost_m3': 'Einheitskosten:',
                'prod_rate': 'Leistung:',
                'total_cost': 'Gesamtkosten:',
                'days': 'Gesch\u00e4tzte Tage:',
                'daily_cost': 'Tageskosten:',
            },
            'es': {
                'title': 'An\u00e1lisis de Costes',
                'cost_m3': 'Coste unitario:',
                'prod_rate': 'Productividad:',
                'total_cost': 'Coste total:',
                'days': 'D\u00edas estimados:',
                'daily_cost': 'Coste diario:',
            },
            'fr': {
                'title': 'Analyse des co\u00fbts',
                'cost_m3': 'Co\u00fbt unitaire:',
                'prod_rate': 'Productivit\u00e9:',
                'total_cost': 'Co\u00fbt total:',
                'days': 'Jours estim\u00e9s:',
                'daily_cost': 'Co\u00fbt journalier:',
            },
            'ar': {
                'title': '\u062a\u062d\u0644\u064a\u0644 \u0627\u0644\u062a\u0643\u0627\u0644\u064a\u0641',
                'cost_m3': '\u0627\u0644\u062a\u0643\u0644\u0641\u0629 \u0644\u0644\u0648\u062d\u062f\u0629:',
                'prod_rate': '\u0627\u0644\u0625\u0646\u062a\u0627\u062c\u064a\u0629:',
                'total_cost': '\u0627\u0644\u062a\u0643\u0644\u0641\u0629 \u0627\u0644\u0625\u062c\u0645\u0627\u0644\u064a\u0629:',
                'days': '\u0627\u0644\u0623\u064a\u0627\u0645 \u0627\u0644\u0645\u062a\u0648\u0642\u0639\u0629:',
                'daily_cost': '\u0627\u0644\u062a\u0643\u0644\u0641\u0629 \u0627\u0644\u064a\u0648\u0645\u064a\u0629:',
            },
            'ca': {
                'title': "An\u00e0lisi de costos",
                'cost_m3': 'Cost unitari:',
                'prod_rate': 'Productivitat:',
                'total_cost': 'Cost total:',
                'days': 'Dies estimats:',
                'daily_cost': 'Cost diari:',
            },
            'ro': {
                'title': 'Analiza costurilor',
                'cost_m3': 'Cost unitar:',
                'prod_rate': 'Productivitate:',
                'total_cost': 'Cost total:',
                'days': 'Zile estimate:',
                'daily_cost': 'Cost zilnic:',
            },
            'pt': {
                'title': 'An\u00e1lise de custos',
                'cost_m3': 'Custo unit\u00e1rio:',
                'prod_rate': 'Produtividade:',
                'total_cost': 'Custo total:',
                'days': 'Dias estimados:',
                'daily_cost': 'Custo di\u00e1rio:',
            },
            'el': {
                'title': '\u0391\u03bd\u03ac\u03bb\u03c5\u03c3\u03b7 \u039a\u03cc\u03c3\u03c4\u03bf\u03c5\u03c2',
                'cost_m3': '\u039c\u03bf\u03bd\u03b1\u03b4\u03b9\u03b1\u03af\u03bf \u03ba\u03cc\u03c3\u03c4\u03bf\u03c2:',
                'prod_rate': '\u03a0\u03b1\u03c1\u03b1\u03b3\u03c9\u03b3\u03b9\u03ba\u03cc\u03c4\u03b7\u03c4\u03b1:',
                'total_cost': '\u03a3\u03c5\u03bd\u03bf\u03bb\u03b9\u03ba\u03cc \u03ba\u03cc\u03c3\u03c4\u03bf\u03c2:',
                'days': '\u0395\u03ba\u03c4\u03b9\u03bc\u03ce\u03bc\u03b5\u03bd\u03b5\u03c2 \u03b7\u03bc\u03ad\u03c1\u03b5\u03c2:',
                'daily_cost': '\u0397\u03bc\u03b5\u03c1\u03ae\u03c3\u03b9\u03bf \u03ba\u03cc\u03c3\u03c4\u03bf\u03c2:',
            },
        }
        return T.get(self.L, T['en'])

    def _load_cost_settings(self):
        """Load persisted cost rate + production rate for the current site."""
        try:
            sito = self.comboBox_sito.currentText() or 'site'
            settings = QgsSettings()
            cost = float(settings.value(
                f"{self._COST_SETTINGS_PREFIX}/{sito}/cost_per_m3", 0.0))
            prod = float(settings.value(
                f"{self._COST_SETTINGS_PREFIX}/{sito}/prod_m3_day", 0.0))
            if hasattr(self, 'spinBox_cost_per_m3'):
                self.spinBox_cost_per_m3.blockSignals(True)
                self.spinBox_prod_m3_day.blockSignals(True)
                self.spinBox_cost_per_m3.setValue(cost)
                self.spinBox_prod_m3_day.setValue(prod)
                self.spinBox_cost_per_m3.blockSignals(False)
                self.spinBox_prod_m3_day.blockSignals(False)
            self._recompute_costs()
        except Exception:
            pass

    def _save_cost_settings(self):
        """Persist current cost inputs for the current site."""
        try:
            sito = self.comboBox_sito.currentText() or 'site'
            settings = QgsSettings()
            settings.setValue(
                f"{self._COST_SETTINGS_PREFIX}/{sito}/cost_per_m3",
                self.spinBox_cost_per_m3.value())
            settings.setValue(
                f"{self._COST_SETTINGS_PREFIX}/{sito}/prod_m3_day",
                self.spinBox_prod_m3_day.value())
        except Exception:
            pass

    def _recompute_costs(self):
        """
        Recompute cost totals from the current volume_mc label and the
        two user-settable spinboxes, then update the display labels.
        """
        if not hasattr(self, 'label_costo_totale'):
            return
        try:
            vol_txt = self.label_volume_mc.text()
            vol_txt = vol_txt.replace('m\u00b3', '').replace('m3', '').strip()
            vol_txt = vol_txt.replace(',', '')
            try:
                volume_mc = float(vol_txt)
            except ValueError:
                volume_mc = 0.0

            cost_per_m3 = self.spinBox_cost_per_m3.value()
            prod_m3_day = self.spinBox_prod_m3_day.value()

            total_cost = volume_mc * cost_per_m3
            days = (volume_mc / prod_m3_day) if prod_m3_day > 0 else 0.0
            daily_cost = (cost_per_m3 * prod_m3_day) if prod_m3_day > 0 else 0.0

            self.label_costo_totale.setText(f"\u20ac {total_cost:,.2f}")
            self.label_giorni_stimati.setText(f"{days:,.2f}")
            self.label_costo_giornaliero.setText(f"\u20ac {daily_cost:,.2f}")

            # Persist changes
            self._save_cost_settings()
        except Exception:
            pass

    # -------------------------------------------------- tabbed reorg --

    def _tab_labels(self):
        """Locale-aware labels for the dashboard tabs."""
        T = {
            'it': ('Riepilogo', 'Computo Metrico', 'Esportazione'),
            'en': ('Overview', 'Quantity Surveying', 'Export'),
            'de': ('\u00dcbersicht', 'Mengenermittlung', 'Export'),
            'es': ('Resumen', 'Mediciones', 'Exportar'),
            'fr': ('Vue d\'ensemble', 'M\u00e9tr\u00e9', 'Exportation'),
            'ar': ('\u0646\u0638\u0631\u0629 \u0639\u0627\u0645\u0629',
                   '\u062d\u0633\u0627\u0628 \u0627\u0644\u0643\u0645\u064a\u0627\u062a',
                   '\u062a\u0635\u062f\u064a\u0631'),
            'ca': ('Resum', 'Amidament', 'Exportaci\u00f3'),
            'ro': ('Rezumat', 'M\u0103sur\u0103tori', 'Export'),
            'pt': ('Resumo', 'Medi\u00e7\u00e3o', 'Exporta\u00e7\u00e3o'),
            'el': ('\u03a3\u03cd\u03bd\u03bf\u03c8\u03b7',
                   '\u0395\u03c0\u03b9\u03bc\u03b5\u03c4\u03c1\u03ae\u03c3\u03b5\u03b9\u03c2',
                   '\u0395\u03be\u03b1\u03b3\u03c9\u03b3\u03ae'),
        }
        return T.get(self.L, T['en'])

    def _reorganize_into_tabs(self):
        """
        Take the flat Cantiere.ui layout and reorganize its top-level
        widgets into a ``QTabWidget`` with three tabs:

            1. Overview     - Budget + Personnel + Equipment summaries
            2. Computo      - DEM inputs, cost analysis, viz buttons,
                              history table, area / volume labels
            3. Export       - PDF + CSV buttons

        This is done at runtime (after ``setupUi``) so the .ui file
        does not need to be changed and old profiles keep working.
        If anything goes wrong the original flat layout is kept.
        """
        try:
            # Find the form's top-level vertical layout. The existing UI
            # is built around this (see gui/ui/Cantiere.ui).
            main_layout = self.layout()
            if main_layout is None:
                return

            # The widgets / layouts we want to move
            overview_group_names = (
                'groupBox_riepilogo_budget',
                'groupBox_personale_oggi',
                'groupBox_attrezzature',
            )
            computo_group_name = 'groupBox_computo_metrico'
            table_name = 'tableWidget_computi'

            overview_widgets = [
                getattr(self, n, None) for n in overview_group_names
            ]
            overview_widgets = [w for w in overview_widgets if w is not None]
            computo_group = getattr(self, computo_group_name, None)
            table = getattr(self, table_name, None)

            if computo_group is None:
                return  # nothing we can usefully rearrange

            labels = self._tab_labels()

            # Build the three tab pages
            tabs = QTabWidget(self)

            # --- Tab 1: Overview ---
            # Layout: Budget (top, full width) + Personnel + Equipment
            # (side by side below).
            overview_page = QWidget()
            overview_layout = QVBoxLayout(overview_page)
            overview_layout.setContentsMargins(6, 6, 6, 6)
            overview_layout.setSpacing(6)

            # Detach all overview group boxes from their current layout first
            for w in overview_widgets:
                parent = w.parentWidget()
                if parent is not None and parent.layout() is not None:
                    parent.layout().removeWidget(w)
                w.setParent(overview_page)

            # Budget on top (full width) if present
            budget_gb = getattr(self, 'groupBox_riepilogo_budget', None)
            if budget_gb is not None:
                overview_layout.addWidget(budget_gb)

            # Bottom row: Personnel | Equipment
            bottom_row = QHBoxLayout()
            pers_gb = getattr(self, 'groupBox_personale_oggi', None)
            eq_gb = getattr(self, 'groupBox_attrezzature', None)
            if pers_gb is not None:
                bottom_row.addWidget(pers_gb, 1)
            if eq_gb is not None:
                bottom_row.addWidget(eq_gb, 1)
            if pers_gb is not None or eq_gb is not None:
                overview_layout.addLayout(bottom_row)
            overview_layout.addStretch(1)
            tabs.addTab(overview_page, labels[0])

            # --- Tab 2: Computo Metrico ---
            computo_page = QWidget()
            computo_page_layout = QVBoxLayout(computo_page)
            computo_page_layout.setContentsMargins(6, 6, 6, 6)
            computo_page_layout.setSpacing(6)

            # Re-parent the Computo group box
            parent = computo_group.parentWidget()
            if parent is not None and parent.layout() is not None:
                parent.layout().removeWidget(computo_group)
            computo_group.setParent(computo_page)
            computo_page_layout.addWidget(computo_group)

            # Re-parent the history table
            if table is not None:
                parent = table.parentWidget()
                if parent is not None and parent.layout() is not None:
                    parent.layout().removeWidget(table)
                table.setParent(computo_page)
                computo_page_layout.addWidget(table, 1)
            tabs.addTab(computo_page, labels[1])

            # --- Tab 3: Export ---
            export_page = QWidget()
            export_page_layout = QVBoxLayout(export_page)
            export_page_layout.setContentsMargins(6, 6, 6, 6)
            export_page_layout.setSpacing(6)

            export_info = QLabel({
                'it': 'Esportazione report del cruscotto:',
                'en': 'Dashboard report export:',
                'de': 'Dashboard-Export:',
                'es': 'Exportaci\u00f3n del panel:',
                'fr': 'Exportation du tableau de bord:',
                'ar': '\u062a\u0635\u062f\u064a\u0631 \u0627\u0644\u0644\u0648\u062d\u0629:',
                'ca': "Exportaci\u00f3 del tauler:",
                'ro': 'Export panou:',
                'pt': 'Exporta\u00e7\u00e3o do painel:',
                'el': '\u0395\u03be\u03b1\u03b3\u03c9\u03b3\u03ae \u03c0\u03af\u03bd\u03b1\u03ba\u03b1:',
            }.get(self.L, 'Dashboard report export:'))
            f = export_info.font()
            f.setPointSize(11)
            f.setBold(True)
            export_info.setFont(f)
            export_page_layout.addWidget(export_info)

            export_help = QLabel({
                'it': ('Esporta in PDF (con sezione Analisi Costi) o in '
                       'CSV (UTF-8 BOM, separatore ;).'),
                'en': ('Export to PDF (with Cost Analysis section) or '
                       'to CSV (UTF-8 BOM, semicolon separator).'),
            }.get(self.L,
                   'Export to PDF or CSV.'))
            export_help.setWordWrap(True)
            export_help.setStyleSheet('color:#607d8b;')
            export_page_layout.addWidget(export_help)

            # Move the two existing export buttons into this page
            btn_row = QHBoxLayout()
            btn_row.addStretch(1)
            for btn_name in ('pushButton_export_pdf', 'pushButton_export_excel'):
                btn = getattr(self, btn_name, None)
                if btn is not None:
                    cur_parent = btn.parentWidget()
                    if cur_parent is not None and cur_parent.layout() is not None:
                        cur_parent.layout().removeWidget(btn)
                    btn.setParent(export_page)
                    btn_row.addWidget(btn)
            btn_row.addStretch(1)
            export_page_layout.addLayout(btn_row)
            export_page_layout.addStretch(1)
            tabs.addTab(export_page, labels[2])

            # Clear the original main layout (everything that's left)
            # and install the tab widget as the only content. We
            # preserve the top "Site / Year / Refresh" header row by
            # rebuilding it from its known widget names below.
            # Remove every item currently in main_layout. The widgets
            # we care about have already been re-parented into the tab
            # pages above; anything that's left (empty sub-layouts,
            # separators, dangling widgets) is detached here.
            orphans = []
            while main_layout.count():
                item = main_layout.takeAt(0)
                if item is None:
                    continue
                w = item.widget()
                if w is not None:
                    # Track and re-parent orphans so Qt does not
                    # delete them out of order.
                    w.setParent(self)
                    orphans.append(w)
                # Sub-layouts: just detach, widgets inside have been
                # reparented already in the tab construction.
                del item

            # Hide every left-over orphan that we are NOT going to put
            # back into the new header row. Without this, leftover
            # ``QFrame::Line`` separators (``line_sep1``, ``line_sep2``)
            # render at their default geometry of (0, 0) and visually
            # block the header widgets in the top-left corner.
            keep_visible = set()
            for n in ('label_sito', 'comboBox_sito', 'label_anno',
                      'comboBox_anno', 'pushButton_refresh'):
                w = getattr(self, n, None)
                if w is not None:
                    keep_visible.add(id(w))
            # The theme toggle button is also kept visible — but it's
            # absolutely-positioned by ThemeManager, not part of the
            # layout, so handled separately further down.
            if getattr(self, 'theme_toggle_btn', None) is not None:
                keep_visible.add(id(self.theme_toggle_btn))

            for w in orphans:
                if id(w) not in keep_visible:
                    try:
                        w.hide()
                    except Exception:
                        pass

            # Belt and braces: explicitly hide the two QFrame::Line
            # separators that the .ui places between the original
            # vertical sections. They are no longer needed inside the
            # tab layout and would otherwise float in the top-left.
            for sep_name in ('line_sep1', 'line_sep2'):
                sep = getattr(self, sep_name, None)
                if sep is not None:
                    try:
                        sep.setParent(self)
                        sep.hide()
                    except Exception:
                        pass

            # Re-add the header row: build a horizontal layout with
            # the known header widgets if they exist.
            header_row = QHBoxLayout()
            header_row.setContentsMargins(0, 0, 0, 0)
            header_row.setSpacing(6)
            for n in ('label_sito', 'comboBox_sito', 'label_anno',
                      'comboBox_anno'):
                w = getattr(self, n, None)
                if w is not None:
                    w.setParent(self)
                    header_row.addWidget(w)
            header_row.addStretch(1)
            refresh_btn = getattr(self, 'pushButton_refresh', None)
            if refresh_btn is not None:
                refresh_btn.setParent(self)
                header_row.addWidget(refresh_btn)
            # IMPORTANT: we deliberately do NOT include the ThemeManager
            # theme toggle button in this header row. ThemeManager
            # positions the button absolutely via ``button.move()`` and
            # hooks ``resizeEvent`` — trying to put it inside a layout
            # produces a visible conflict where the button flickers
            # between the layout position and the absolute position,
            # and it ends up overlapping the site label in the top-left
            # corner on first show. Leaving the button alone lets
            # ThemeManager keep it anchored to the bottom-right corner
            # of the form, which is where the user expects it.

            main_layout.addLayout(header_row)
            main_layout.addWidget(tabs, 1)

            # Let the comboBox_sito expand
            try:
                self.comboBox_sito.setMinimumWidth(220)
            except Exception:
                pass

            # Make sure the theme toggle button is raised above any
            # widget we just re-parented, and nudge it to its correct
            # absolute position by re-triggering the form resize.
            try:
                if getattr(self, 'theme_toggle_btn', None) is not None:
                    self.theme_toggle_btn.setParent(self)
                    self.theme_toggle_btn.raise_()
                    QTimer.singleShot(0, lambda: self.resize(self.size()))
            except Exception:
                pass
        except Exception:
            # If reorganization fails for any reason, keep the original
            # flat layout — the dashboard remains fully functional.
            pass

    def _deferred_init(self):
        """Load data after the window is visible."""
        try:
            self.on_pushButton_connect_pressed()
        except:
            pass
        self.charge_list()
        self.apply_sito_set()
        self.populate_raster_combos()
        self.populate_vector_combos()
        self.refresh_dashboard()

    def on_pushButton_connect_pressed(self):
        """Connect to database using singleton pattern"""
        conn = Connection()
        conn_str = conn.conn_str()
        test_conn = conn_str.find('sqlite')
        if test_conn == 0:
            self.DB_SERVER = "sqlite"
        try:
            self.DB_MANAGER = get_db_manager(conn_str, use_singleton=True)
        except Exception as e:
            QMessageBox.warning(self, "Connection Error", str(e))

    def charge_list(self):
        """Populate site and year dropdowns"""
        if not self.DB_MANAGER:
            return
        # Sites
        try:
            sito_vl = self.UTILITY.tup_2_list_III(
                self.DB_MANAGER.group_by('site_table', 'sito', 'SITE'))
            try:
                sito_vl.remove('')
            except:
                pass
            self.comboBox_sito.clear()
            sito_vl.sort()
            self.comboBox_sito.addItems(sito_vl)
        except:
            pass
        # Years
        current_year = date.today().year
        years = [str(y) for y in range(current_year, current_year - 10, -1)]
        self.comboBox_anno.clear()
        self.comboBox_anno.addItems(years)

    def apply_sito_set(self):
        """Pre-select the configured site if set"""
        try:
            conn = Connection()
            sito_set = conn.sito_set()
            sito_set_str = sito_set['sito_set']
            if bool(sito_set_str):
                idx = self.comboBox_sito.findText(sito_set_str)
                if idx >= 0:
                    self.comboBox_sito.setCurrentIndex(idx)
        except Exception:
            pass

    def populate_raster_combos(self):
        """
        Refresh DEM combos from the current QGIS project while preserving
        the user's current selection (so calling this right before Calcola
        does not reset the chosen layers).
        """
        prev_pre = self.comboBox_dem_pre.currentData()
        prev_post = self.comboBox_dem_post.currentData()

        self.comboBox_dem_pre.blockSignals(True)
        self.comboBox_dem_post.blockSignals(True)

        self.comboBox_dem_pre.clear()
        self.comboBox_dem_post.clear()
        self.comboBox_dem_pre.addItem("")
        self.comboBox_dem_post.addItem("")
        for layer_id, layer in QgsProject.instance().mapLayers().items():
            if isinstance(layer, QgsRasterLayer):
                self.comboBox_dem_pre.addItem(layer.name(), layer_id)
                self.comboBox_dem_post.addItem(layer.name(), layer_id)

        # Restore previous selection when the layer is still present
        if prev_pre:
            idx = self.comboBox_dem_pre.findData(prev_pre)
            if idx >= 0:
                self.comboBox_dem_pre.setCurrentIndex(idx)
        if prev_post:
            idx = self.comboBox_dem_post.findData(prev_post)
            if idx >= 0:
                self.comboBox_dem_post.setCurrentIndex(idx)

        self.comboBox_dem_pre.blockSignals(False)
        self.comboBox_dem_post.blockSignals(False)

    def populate_vector_combos(self):
        """
        Refresh the polygon combo from the current QGIS project while
        preserving the selection (see ``populate_raster_combos``).
        """
        prev_poly = self.comboBox_layer_poligono.currentData()

        self.comboBox_layer_poligono.blockSignals(True)
        self.comboBox_layer_poligono.clear()
        self.comboBox_layer_poligono.addItem("")
        for layer_id, layer in QgsProject.instance().mapLayers().items():
            if isinstance(layer, QgsVectorLayer):
                self.comboBox_layer_poligono.addItem(layer.name(), layer_id)
        if prev_poly:
            idx = self.comboBox_layer_poligono.findData(prev_poly)
            if idx >= 0:
                self.comboBox_layer_poligono.setCurrentIndex(idx)
        self.comboBox_layer_poligono.blockSignals(False)
        # Keep the walls combo in sync with the same project layers
        self._populate_walls_combo()

    def retranslate_ui(self):
        """Translate all dashboard labels based on current locale."""
        lang = self.L
        t = {
            'it': {
                'title': 'pyArchInit - Dashboard Cantiere',
                'sito': 'Sito', 'anno': 'Anno',
                'budget_group': 'Riepilogo Budget',
                'budget_prev': 'Budget Previsto:', 'budget_spent': 'Budget Speso:',
                'personnel_group': 'Personale',
                'presenti': 'Presenti:', 'ferie': 'Ferie:', 'malattia': 'Malattia:',
                'ore_mese': 'Ore Totali:', 'costo_mese': 'Costo Totale:',
                'equip_group': 'Attrezzature',
                'totali': 'Totali:', 'in_uso': 'In Uso:', 'manutenzione': 'In Manutenzione:',
                'computo_group': 'Computo Metrico',
                'btn_calcola': 'Calcola', 'btn_salva': 'Salva Computo',
                'btn_refresh': 'Aggiorna', 'btn_pdf': 'Esporta PDF', 'btn_excel': 'Esporta CSV',
            },
            'en': {
                'title': 'pyArchInit - Site Dashboard',
                'sito': 'Site', 'anno': 'Year',
                'budget_group': 'Budget Summary',
                'budget_prev': 'Budget Forecast:', 'budget_spent': 'Budget Spent:',
                'personnel_group': 'Personnel',
                'presenti': 'Present:', 'ferie': 'On Leave:', 'malattia': 'Sick:',
                'ore_mese': 'Total Hours:', 'costo_mese': 'Total Cost:',
                'equip_group': 'Equipment',
                'totali': 'Total:', 'in_uso': 'In Use:', 'manutenzione': 'Under Maintenance:',
                'computo_group': 'Quantity Surveying',
                'btn_calcola': 'Calculate', 'btn_salva': 'Save Record',
                'btn_refresh': 'Refresh', 'btn_pdf': 'Export PDF', 'btn_excel': 'Export CSV',
            },
            'de': {
                'title': 'pyArchInit - Baustellen-Dashboard',
                'sito': 'Fundstelle', 'anno': 'Jahr',
                'budget_group': 'Budget-Übersicht',
                'budget_prev': 'Geplant:', 'budget_spent': 'Ausgegeben:',
                'personnel_group': 'Personal',
                'presenti': 'Anwesend:', 'ferie': 'Urlaub:', 'malattia': 'Krank:',
                'ore_mese': 'Stunden Gesamt:', 'costo_mese': 'Kosten Gesamt:',
                'equip_group': 'Ausrüstung',
                'totali': 'Gesamt:', 'in_uso': 'In Gebrauch:', 'manutenzione': 'In Wartung:',
                'computo_group': 'Mengenermittlung',
                'btn_calcola': 'Berechnen', 'btn_salva': 'Speichern',
                'btn_refresh': 'Aktualisieren', 'btn_pdf': 'PDF Export', 'btn_excel': 'CSV Export',
            },
            'es': {
                'title': 'pyArchInit - Panel de Obra',
                'sito': 'Sitio', 'anno': 'Año',
                'budget_group': 'Resumen de Presupuesto',
                'budget_prev': 'Previsto:', 'budget_spent': 'Gastado:',
                'personnel_group': 'Personal',
                'presenti': 'Presentes:', 'ferie': 'Vacaciones:', 'malattia': 'Baja:',
                'ore_mese': 'Horas Totales:', 'costo_mese': 'Coste Total:',
                'equip_group': 'Equipamiento',
                'totali': 'Total:', 'in_uso': 'En Uso:', 'manutenzione': 'En Mantenimiento:',
                'computo_group': 'Mediciones',
                'btn_calcola': 'Calcular', 'btn_salva': 'Guardar',
                'btn_refresh': 'Actualizar', 'btn_pdf': 'Exportar PDF', 'btn_excel': 'Exportar CSV',
            },
            'fr': {
                'title': 'pyArchInit - Tableau de Bord',
                'sito': 'Site', 'anno': 'Année',
                'budget_group': 'Résumé Budget',
                'budget_prev': 'Prévu:', 'budget_spent': 'Dépensé:',
                'personnel_group': 'Personnel',
                'presenti': 'Présents:', 'ferie': 'Congé:', 'malattia': 'Maladie:',
                'ore_mese': 'Heures Totales:', 'costo_mese': 'Coût Total:',
                'equip_group': 'Équipement',
                'totali': 'Total:', 'in_uso': 'En Usage:', 'manutenzione': 'En Maintenance:',
                'computo_group': 'Métré',
                'btn_calcola': 'Calculer', 'btn_salva': 'Enregistrer',
                'btn_refresh': 'Actualiser', 'btn_pdf': 'Exporter PDF', 'btn_excel': 'Exporter CSV',
            },
            'ar': {
                'title': 'pyArchInit - لوحة القيادة',
                'sito': 'الموقع', 'anno': 'السنة',
                'budget_group': 'ملخص الميزانية',
                'budget_prev': 'المخطط:', 'budget_spent': 'المنفق:',
                'personnel_group': 'الموظفون',
                'presenti': 'حاضرون:', 'ferie': 'إجازة:', 'malattia': 'مرضى:',
                'ore_mese': 'إجمالي الساعات:', 'costo_mese': 'إجمالي التكلفة:',
                'equip_group': 'المعدات',
                'totali': 'الإجمالي:', 'in_uso': 'قيد الاستخدام:', 'manutenzione': 'قيد الصيانة:',
                'computo_group': 'حساب الكميات',
                'btn_calcola': 'احسب', 'btn_salva': 'احفظ',
                'btn_refresh': 'تحديث', 'btn_pdf': 'تصدير PDF', 'btn_excel': 'تصدير CSV',
            },
            'ca': {
                'title': "pyArchInit - Tauler d'Obra",
                'sito': 'Lloc', 'anno': 'Any',
                'budget_group': 'Resum Pressupost',
                'budget_prev': 'Previst:', 'budget_spent': 'Gastat:',
                'personnel_group': 'Personal',
                'presenti': 'Presents:', 'ferie': 'Vacances:', 'malattia': 'Malaltia:',
                'ore_mese': 'Hores Totals:', 'costo_mese': 'Cost Total:',
                'equip_group': 'Equipament',
                'totali': 'Total:', 'in_uso': 'En Ús:', 'manutenzione': 'En Manteniment:',
                'computo_group': 'Amidament',
                'btn_calcola': 'Calcular', 'btn_salva': 'Desar',
                'btn_refresh': 'Actualitzar', 'btn_pdf': 'Exportar PDF', 'btn_excel': 'Exportar CSV',
            },
            'ro': {
                'title': 'pyArchInit - Panou Șantier',
                'sito': 'Sit', 'anno': 'An',
                'budget_group': 'Rezumat Buget',
                'budget_prev': 'Planificat:', 'budget_spent': 'Cheltuit:',
                'personnel_group': 'Personal',
                'presenti': 'Prezenți:', 'ferie': 'Concediu:', 'malattia': 'Medical:',
                'ore_mese': 'Ore Totale:', 'costo_mese': 'Cost Total:',
                'equip_group': 'Echipamente',
                'totali': 'Total:', 'in_uso': 'În Uz:', 'manutenzione': 'În Întreținere:',
                'computo_group': 'Măsurători',
                'btn_calcola': 'Calculează', 'btn_salva': 'Salvează',
                'btn_refresh': 'Actualizează', 'btn_pdf': 'Export PDF', 'btn_excel': 'Export CSV',
            },
            'pt': {
                'title': 'pyArchInit - Painel de Obra',
                'sito': 'Sítio', 'anno': 'Ano',
                'budget_group': 'Resumo Orçamento',
                'budget_prev': 'Previsto:', 'budget_spent': 'Gasto:',
                'personnel_group': 'Pessoal',
                'presenti': 'Presentes:', 'ferie': 'Férias:', 'malattia': 'Baixa:',
                'ore_mese': 'Horas Totais:', 'costo_mese': 'Custo Total:',
                'equip_group': 'Equipamento',
                'totali': 'Total:', 'in_uso': 'Em Uso:', 'manutenzione': 'Em Manutenção:',
                'computo_group': 'Medição',
                'btn_calcola': 'Calcular', 'btn_salva': 'Guardar',
                'btn_refresh': 'Atualizar', 'btn_pdf': 'Exportar PDF', 'btn_excel': 'Exportar CSV',
            },
            'el': {
                'title': 'pyArchInit - Πίνακας Εργοταξίου',
                'sito': 'Τοποθεσία', 'anno': 'Έτος',
                'budget_group': 'Σύνοψη Προϋπολογισμού',
                'budget_prev': 'Προβλεπόμενο:', 'budget_spent': 'Δαπανηθέν:',
                'personnel_group': 'Προσωπικό',
                'presenti': 'Παρόντες:', 'ferie': 'Άδεια:', 'malattia': 'Ασθένεια:',
                'ore_mese': 'Σύνολο Ωρών:', 'costo_mese': 'Συνολικό Κόστος:',
                'equip_group': 'Εξοπλισμός',
                'totali': 'Σύνολο:', 'in_uso': 'Σε Χρήση:', 'manutenzione': 'Σε Συντήρηση:',
                'computo_group': 'Επιμετρήσεις',
                'btn_calcola': 'Υπολογισμός', 'btn_salva': 'Αποθήκευση',
                'btn_refresh': 'Ανανέωση', 'btn_pdf': 'Εξαγωγή PDF', 'btn_excel': 'Εξαγωγή CSV',
            },
        }.get(lang, None)
        if t is None:
            t = {  # fallback to English
                'title': 'pyArchInit - Site Dashboard',
                'sito': 'Site', 'anno': 'Year',
                'budget_group': 'Budget Summary', 'budget_prev': 'Budget Forecast:', 'budget_spent': 'Budget Spent:',
                'personnel_group': 'Personnel',
                'presenti': 'Present:', 'ferie': 'On Leave:', 'malattia': 'Sick:',
                'ore_mese': 'Total Hours:', 'costo_mese': 'Total Cost:',
                'equip_group': 'Equipment',
                'totali': 'Total:', 'in_uso': 'In Use:', 'manutenzione': 'Under Maintenance:',
                'computo_group': 'Quantity Surveying',
                'btn_calcola': 'Calculate', 'btn_salva': 'Save Record',
                'btn_refresh': 'Refresh', 'btn_pdf': 'Export PDF', 'btn_excel': 'Export CSV',
            }
        self.setWindowTitle(t['title'])
        self.label_sito.setText(t['sito'])
        self.label_anno.setText(t['anno'])
        self.groupBox_riepilogo_budget.setTitle(t['budget_group'])
        self.label_lbl_budget_previsto.setText(t['budget_prev'])
        self.label_lbl_budget_speso.setText(t['budget_spent'])
        self.groupBox_personale_oggi.setTitle(t['personnel_group'])
        self.label_lbl_presenti.setText(t['presenti'])
        self.label_lbl_ferie.setText(t['ferie'])
        self.label_lbl_malattia.setText(t['malattia'])
        self.label_lbl_ore_mese.setText(t['ore_mese'])
        self.label_lbl_costo_mese.setText(t['costo_mese'])
        self.groupBox_attrezzature.setTitle(t['equip_group'])
        self.label_lbl_totali.setText(t['totali'])
        self.label_lbl_in_uso.setText(t['in_uso'])
        self.label_lbl_manutenzione.setText(t['manutenzione'])
        self.groupBox_computo_metrico.setTitle(t['computo_group'])
        self.pushButton_calcola.setText(t['btn_calcola'])
        self.pushButton_salva_computo.setText(t['btn_salva'])
        self.pushButton_refresh.setText(t['btn_refresh'])
        self.pushButton_export_pdf.setText(t['btn_pdf'])
        self.pushButton_export_excel.setText(t['btn_excel'])

    def refresh_dashboard(self):
        """Refresh all dashboard sections"""
        sito = self.comboBox_sito.currentText()
        anno = self.comboBox_anno.currentText()
        if not sito or not self.DB_MANAGER:
            return
        self.refresh_budget_summary(sito, anno)
        self.refresh_personnel_summary(sito)
        self.refresh_equipment_summary(sito)
        self.refresh_computo_history(sito)

    def refresh_budget_summary(self, sito, anno):
        """Query budget_table, calculate totals, update progress bar"""
        try:
            search_dict = {'sito': "'" + sito + "'"}
            if anno and anno.strip():
                try:
                    search_dict['anno'] = int(anno)
                except ValueError:
                    pass
            records = self.DB_MANAGER.query_bool(search_dict, 'BUDGET')

            totale_previsto = sum(r.importo_previsto or 0 for r in records)
            totale_effettivo = sum(r.importo_effettivo or 0 for r in records)

            self.label_budget_previsto.setText(f"\u20ac {totale_previsto:,.2f}")
            self.label_budget_speso.setText(f"\u20ac {totale_effettivo:,.2f}")

            if totale_previsto > 0:
                pct = int((totale_effettivo / totale_previsto) * 100)
                self.progressBar_budget.setValue(min(pct, 100))
            else:
                self.progressBar_budget.setValue(0)

            # Draw pie chart
            self.draw_budget_chart(records)
        except Exception as e:
            pass

    # Multilingual terms for filtering attendance and equipment records (10 languages)
    # it, en, de, es, fr, ar, ca, ro, pt, el
    WORKING_DAY_TERMS = {
        'ordinaria', 'regular day', 'regulärer tag', 'jornada ordinaria',
        'journée ordinaire', 'يوم عادي', 'jornada ordinària', 'zi normală',
        'dia regular', 'κανονική ημέρα',
        'regular', 'overtime day', 'straordinaria', 'half day', 'mezza giornata',
        'training day', 'formazione', 'überstundentag', 'jornada extraordinaria',
        'journée supplémentaire', 'يوم إضافي', 'jornada extraordinària', 'zi cu ore suplimentare',
        'dia de horas extra', 'υπερωριακή ημέρα',
        'halber tag', 'media jornada', 'demi-journée', 'نصف يوم', 'mitja jornada',
        'jumătate de zi', 'meio dia', 'μισή ημέρα',
        'schulungstag', 'día de formación', 'journée de formation', 'يوم تدريب',
        'jornada de formació', 'zi de formare', 'dia de formação', 'ημέρα εκπαίδευσης',
        'trasferta', 'travel day', 'reisetag', 'día de viaje', 'journée de déplacement',
        'يوم سفر', 'jornada de viatge', 'zi de deplasare', 'dia de viagem', 'ημέρα μετακίνησης',
    }
    HOLIDAY_TERMS = {
        'ferie', 'holiday', 'holiday/leave', 'urlaub', 'vacaciones', 'congé', 'إجازة',
        'vacances', 'concediu', 'férias', 'άδεια',
    }
    SICK_TERMS = {
        'malattia', 'sick leave', 'krankheit', 'baja médica', 'maladie', 'إجازة مرضية',
        'malaltia', 'concediu medical', 'baixa médica', 'αναρρωτική',
    }
    DAYOFF_TERMS = {
        'permesso', 'day off', 'freistellung', 'permiso', 'permission', 'إذن',
        'permís', 'permisie', 'licença', 'ρεπό',
        'festivo', 'public holiday', 'feiertag', 'festivo', 'jour férié', 'يوم عطلة',
        'festiu', 'zi liberă', 'feriado', 'αργία',
        'assente', 'absent', 'abwesend', 'ausente', 'absent', 'غائب',
        'absent', 'absent', 'ausente', 'απών',
    }
    IN_USE_TERMS = {
        'in uso', 'in use', 'in gebrauch', 'en uso', 'en utilisation', 'قيد الاستخدام',
        'en ús', 'în uz', 'em uso', 'σε χρήση',
    }
    MAINTENANCE_TERMS = {
        'in manutenzione', 'under maintenance', 'in wartung', 'en mantenimiento',
        'en maintenance', 'قيد الصيانة', 'en manteniment', 'în întreținere',
        'em manutenção', 'σε συντήρηση',
    }
    DECOMMISSIONED_TERMS = {
        'dismessa', 'decommissioned', 'fuori_uso', 'fuori uso', 'außer betrieb',
        'fuera de servicio', 'hors service', 'خارج الخدمة', 'fora de servei',
        'scos din uz', 'fora de serviço', 'εκτός λειτουργίας',
    }

    def refresh_personnel_summary(self, sito):
        """Query presenze_table - show all-time stats if no records today"""
        try:
            # First try today's records
            today = date.today().isoformat()
            search_dict = {'sito': "'" + sito + "'", 'data': "'" + today + "'"}
            records = self.DB_MANAGER.query_bool(search_dict, 'PRESENZE')

            # If no records today, show all records for the site
            if not records:
                search_dict = {'sito': "'" + sito + "'"}
                records = self.DB_MANAGER.query_bool(search_dict, 'PRESENZE')

            presenti = sum(1 for r in records if r.tipo_giornata and r.tipo_giornata.lower() in self.WORKING_DAY_TERMS)
            ferie = sum(1 for r in records if r.tipo_giornata and r.tipo_giornata.lower() in self.HOLIDAY_TERMS)
            malattia = sum(1 for r in records if r.tipo_giornata and r.tipo_giornata.lower() in self.SICK_TERMS)

            self.label_presenti.setText(str(presenti))
            self.label_ferie.setText(str(ferie))
            self.label_malattia.setText(str(malattia))

            # Monthly totals - use current month or latest month with data
            month_prefix = today[:7]  # YYYY-MM
            search_all = {'sito': "'" + sito + "'"}
            all_records = self.DB_MANAGER.query_bool(search_all, 'PRESENZE')
            month_records = [r for r in all_records if r.data and r.data.startswith(month_prefix)]

            # If no records this month, use all records
            if not month_records:
                month_records = all_records

            ore_mese = sum(r.ore_ordinarie or 0 for r in month_records) + sum(r.ore_straordinario or 0 for r in month_records)
            costo_mese = sum(r.costo_giornata or 0 for r in month_records)

            self.label_ore_mese.setText(f"{ore_mese:.1f}")
            self.label_costo_mese.setText(f"\u20ac {costo_mese:,.2f}")
        except:
            pass

    def refresh_equipment_summary(self, sito):
        """Query attrezzature_table"""
        try:
            search_dict = {'sito': "'" + sito + "'"}
            records = self.DB_MANAGER.query_bool(search_dict, 'ATTREZZATURE')

            totali = len(records)
            in_uso = sum(1 for r in records if r.stato and r.stato.lower() in self.IN_USE_TERMS)
            manutenzione = sum(1 for r in records if r.stato and r.stato.lower() in self.MAINTENANCE_TERMS)

            self.label_totali.setText(str(totali))
            self.label_in_uso.setText(str(in_uso))
            self.label_manutenzione.setText(str(manutenzione))

            # Check overdue maintenance
            today = date.today().isoformat()
            overdue = [r for r in records if r.data_prossima_manutenzione and r.data_prossima_manutenzione < today
                       and not (r.stato and r.stato.lower() in self.DECOMMISSIONED_TERMS)]
            if overdue:
                alert_msgs = {'it': 'scadenze manutenzione!', 'en': 'maintenance overdue!',
                              'de': 'Wartung überfällig!', 'es': 'mantenimiento vencido!',
                              'fr': 'maintenance en retard!', 'ar': 'صيانة متأخرة!'}
                msg = alert_msgs.get(self.L, alert_msgs['en'])
                self.label_alert_manutenzione.setText(f"⚠ {len(overdue)} {msg}")
                self.label_alert_manutenzione.setStyleSheet("color: red; font-weight: bold;")
            else:
                ok_msgs = {'it': 'Nessuna scadenza', 'en': 'No overdue', 'de': 'Keine Überfälligkeiten',
                           'es': 'Sin vencimientos', 'fr': 'Aucun retard', 'ar': 'لا تأخير'}
                self.label_alert_manutenzione.setText(ok_msgs.get(self.L, ok_msgs['en']))
                self.label_alert_manutenzione.setStyleSheet("color: green;")
        except:
            pass

    def refresh_computo_history(self, sito):
        """Load computo metrico history into table widget"""
        try:
            search_dict = {'sito': "'" + sito + "'"}
            records = self.DB_MANAGER.query_bool(search_dict, 'COMPUTO_METRICO')

            self.tableWidget_computi.setRowCount(0)
            for r in records:
                row = self.tableWidget_computi.rowCount()
                self.tableWidget_computi.insertRow(row)
                self.tableWidget_computi.setItem(row, 0, QTableWidgetItem(str(r.data_calcolo or '')))
                self.tableWidget_computi.setItem(row, 1, QTableWidgetItem(str(r.tipo_calcolo or '')))
                self.tableWidget_computi.setItem(row, 2, QTableWidgetItem(f"{r.area_mq or 0:.2f}"))
                self.tableWidget_computi.setItem(row, 3, QTableWidgetItem(f"{r.volume_mc or 0:.2f}"))
                self.tableWidget_computi.setItem(row, 4, QTableWidgetItem(str(r.note or '')))
        except:
            pass

    def on_pushButton_calcola_pressed(self):
        """
        Run the DEM-difference workflow. The previous polygon-only mode
        is no longer exposed by the UI (see ``_wire_calc_mode_radios``)
        — when the user picks a polygon in "Layer Poligono" it is used
        as a clip mask, not as a selector for a different calculation.
        """
        self._notify_info('Calcola', 'running differenza_dem')
        self.calculate_dem_difference()

    def calculate_dem_difference(self):
        """
        Compute the volume/area from the difference of two DEMs AND
        build the 2D visualization (persistent raster + polygon) in the
        map canvas. Enables the 3D visualization button on success.

        If a polygon layer is also selected in ``comboBox_layer_poligono``,
        both DEMs are clipped to that polygon first (via ``gdal.Warp``)
        so that the calculation, the 2D section viewer, the 3D view and
        the mesh all operate on the intervention area only.
        """
        try:
            # Always refresh the combos first so layers loaded AFTER
            # the dashboard was opened (including polygons drawn on the
            # fly) are picked up automatically.
            self.populate_raster_combos()
            self.populate_vector_combos()

            layer_pre_id = self.comboBox_dem_pre.currentData()
            layer_post_id = self.comboBox_dem_post.currentData()

            if not layer_pre_id or not layer_post_id:
                QMessageBox.warning(self, self.MSG_BOX_TITLE,
                                    "Select both DEM layers")
                return

            # Explicit check: the user may have picked the SAME layer
            # in both combos by mistake. In that case pre == post and
            # every downstream step produces identical "clipped" files
            # — exactly the "sta clippando sempre lo stesso DEM" bug.
            if layer_pre_id == layer_post_id:
                QMessageBox.warning(
                    self, self.MSG_BOX_TITLE,
                    "DEM pre and DEM post are the SAME layer.\n\n"
                    "Please pick two DIFFERENT DEM rasters in the two "
                    "combo boxes (one for the pre-excavation surface, "
                    "one for the post-excavation surface)."
                )
                return

            layer_pre = QgsProject.instance().mapLayer(layer_pre_id)
            layer_post = QgsProject.instance().mapLayer(layer_post_id)
            if not layer_pre or not layer_post:
                QMessageBox.warning(self, self.MSG_BOX_TITLE,
                                    "Could not load DEM layers")
                return

            # Same check on the underlying source file — catches
            # accidental aliasing when two different QGIS layers
            # actually point to the same raster on disk.
            try:
                pre_src_raw = layer_pre.source() or ''
                post_src_raw = layer_post.source() or ''
                pre_src_clean = dem_viz._clean_raster_path(pre_src_raw)
                post_src_clean = dem_viz._clean_raster_path(post_src_raw)
                if (pre_src_clean and post_src_clean
                        and os.path.normcase(os.path.realpath(pre_src_clean))
                        == os.path.normcase(os.path.realpath(post_src_clean))):
                    QMessageBox.warning(
                        self, self.MSG_BOX_TITLE,
                        "DEM pre and DEM post are two QGIS layers but "
                        "point to the SAME raster file on disk:\n"
                        f"{pre_src_clean}\n\n"
                        "The difference between them would be zero.\n"
                        "Please load and select TWO different DEM files."
                    )
                    return
            except Exception:
                pass

            sito = self.comboBox_sito.currentText() or 'site'
            out_dir = dem_viz.ensure_output_dir(sito)
            group_name = (
                dem_viz.GROUP_NAME_IT if self.L == 'it' else dem_viz.GROUP_NAME_EN
            )

            # ---- Optional clipping by polygon ----
            # If the user also picked a polygon layer in the "Layer Poligono"
            # combo, clip both DEMs to it first. Every subsequent step
            # (diff, section, 3D, mesh) then operates on the intervention
            # area only. Failures are reported explicitly so the user can
            # see why clipping did not kick in.
            clip_poly_layer = None
            clip_messages = []
            layer_poly_id = self.comboBox_layer_poligono.currentData()
            if layer_poly_id:
                clip_poly_layer = QgsProject.instance().mapLayer(layer_poly_id)
                if clip_poly_layer is None:
                    clip_messages.append(
                        f"Polygon layer id {layer_poly_id} not found in project")

            if clip_poly_layer is not None:
                # Use the pre-DEM native pixel grid as the reference so
                # that both clipped outputs are aligned and can be
                # subtracted cell-by-cell by QgsRasterCalculator.
                try:
                    ref_x_res = layer_pre.rasterUnitsPerPixelX()
                    ref_y_res = layer_pre.rasterUnitsPerPixelY()
                except Exception:
                    ref_x_res = ref_y_res = None

                # Use explicit filenames with counter so pre/post files
                # cannot collide even when timestamps fall in the same
                # second.
                _ts = datetime.now().strftime('%Y%m%d_%H%M%S')

                # Capture the raw source paths BEFORE any swap so they
                # survive into the diagnostic message bar and we can
                # verify the two clips come from different files.
                pre_source_before = dem_viz._clean_raster_path(
                    layer_pre.source() or '')
                post_source_before = dem_viz._clean_raster_path(
                    layer_post.source() or '')
                clip_messages.append(
                    f"pre source: {os.path.basename(pre_source_before)}")
                clip_messages.append(
                    f"post source: {os.path.basename(post_source_before)}")

                pre_clipped_path = os.path.join(
                    out_dir, f'dem_pre_clipped_{_ts}.tif')
                pre_clipped_path, pre_err = dem_viz.clip_raster_by_polygon(
                    pre_source_before, clip_poly_layer, pre_clipped_path,
                    target_x_res=ref_x_res, target_y_res=ref_y_res,
                )
                if pre_clipped_path:
                    clipped_pre = QgsRasterLayer(
                        pre_clipped_path, f"DEM pre clipped - {sito}")
                    if clipped_pre.isValid():
                        dem_viz.add_layer_to_group(
                            clipped_pre, group_name=group_name)
                        layer_pre = clipped_pre  # swap
                        try:
                            sz = os.path.getsize(pre_clipped_path)
                        except Exception:
                            sz = 0
                        clip_messages.append(
                            f"pre clipped: "
                            f"{os.path.basename(pre_clipped_path)} "
                            f"({sz // 1024} KB)")
                    else:
                        clip_messages.append(
                            'pre DEM clipped file is not a valid raster')
                else:
                    clip_messages.append(f'pre DEM clip failed: {pre_err}')

                post_clipped_path = os.path.join(
                    out_dir, f'dem_post_clipped_{_ts}.tif')
                post_clipped_path, post_err = dem_viz.clip_raster_by_polygon(
                    post_source_before, clip_poly_layer, post_clipped_path,
                    target_x_res=ref_x_res, target_y_res=ref_y_res,
                )
                if post_clipped_path:
                    clipped_post = QgsRasterLayer(
                        post_clipped_path, f"DEM post clipped - {sito}")
                    if clipped_post.isValid():
                        dem_viz.add_layer_to_group(
                            clipped_post, group_name=group_name)
                        layer_post = clipped_post  # swap
                        try:
                            sz = os.path.getsize(post_clipped_path)
                        except Exception:
                            sz = 0
                        clip_messages.append(
                            f"post clipped: "
                            f"{os.path.basename(post_clipped_path)} "
                            f"({sz // 1024} KB)")
                    else:
                        clip_messages.append(
                            'post DEM clipped file is not a valid raster')
                else:
                    clip_messages.append(f'post DEM clip failed: {post_err}')

            # Log clip diagnostics to the QGIS message bar so the user
            # can see at a glance what happened
            if clip_messages:
                self._notify_info(
                    'Clip polygon', ' | '.join(clip_messages))

            diff_name = dem_viz.timestamped_name('dem_diff', 'tif')
            diff_path = os.path.join(out_dir, diff_name)

            result = dem_viz.compute_dem_difference(layer_pre, layer_post, diff_path)
            if result != 0 or not os.path.exists(diff_path):
                QMessageBox.warning(self, self.MSG_BOX_TITLE,
                                    "Raster calculation failed")
                return

            # ---- Optional walls / structures exclusion ----
            # If the user picked a walls polygon layer in the injected
            # "Muri / Strutture" combo, rasterise its features over the
            # just-computed diff raster using NODATA so the walls are
            # not counted in the volume.
            walls_layer = None
            walls_id = None
            if hasattr(self, 'comboBox_layer_muri'):
                walls_id = self.comboBox_layer_muri.currentData()
                if walls_id:
                    walls_layer = QgsProject.instance().mapLayer(walls_id)
            if walls_layer is not None:
                ok, w_err = dem_viz.exclude_polygons_from_raster(
                    diff_path, walls_layer)
                if ok:
                    clip_messages.append(
                        f"walls masked: {walls_layer.name()}")
                else:
                    clip_messages.append(
                        f"walls masking failed: {w_err}")
                if clip_messages:
                    self._notify_info(
                        'Clip polygon', ' | '.join(clip_messages))

            diff_layer = QgsRasterLayer(
                diff_path, f"DEM diff - {sito} - {datetime.now().strftime('%H:%M:%S')}")
            if not diff_layer.isValid():
                QMessageBox.warning(self, self.MSG_BOX_TITLE,
                                    "Could not open the computed difference raster")
                return

            # Compute stats from persisted raster (after walls masking)
            stats = dem_viz.compute_volume_stats(diff_layer)

            # Update UI labels
            self.label_area_mq.setText(f"{stats['total_area_m2']:.2f} m\u00b2")
            self.label_volume_mc.setText(f"{stats['total_volume_m3']:.2f} m\u00b3")
            self._recompute_costs()

            # 2D visualization: style and add to project
            # (group_name already defined above, reused here)
            dem_viz.style_diff_raster(diff_layer, max_abs=stats['max_abs'])
            dem_viz.add_layer_to_group(diff_layer, group_name=group_name)

            # Polygonize the intervention area
            poly_path = os.path.join(out_dir,
                                     dem_viz.timestamped_name('cut_area', 'gpkg'))
            poly_layer = None
            if dem_viz.polygonize_cut_area(diff_path, poly_path, threshold=0.01):
                poly_layer = QgsVectorLayer(
                    poly_path, f"Cut area - {sito}", 'ogr')
                if poly_layer.isValid():
                    dem_viz.style_cut_polygon(poly_layer)
                    dem_viz.add_layer_to_group(poly_layer, group_name=group_name)
                else:
                    poly_layer = None

            # Zoom canvas to the computed extent
            dem_viz.zoom_canvas_to(self.iface, diff_layer.extent())

            # Track state for 3D viewer / saving
            self._last_calc.update({
                'diff_raster_path': diff_path,
                'diff_raster_layer': diff_layer,
                'poly_layer': poly_layer,
                'terrain_layer': layer_pre,     # may already be clipped
                'layer_post': layer_post,       # may already be clipped
                'clip_poly_layer': clip_poly_layer,  # user-drawn clip mask
                'mesh_pre_layer': None,
                'mesh_post_layer': None,
                'stats': stats,
                'sito': sito,
                'tipo': 'differenza_dem',
            })
            self._enable_viz_buttons(True, mesh_ready=False)

        except Exception as e:
            QMessageBox.warning(self, self.MSG_BOX_TITLE, f"Error: {str(e)}")

    def calculate_dem_polygon(self):
        """
        Polygon mode: clip a single DEM to a polygon layer, compute
        area + volume (zonal stats) and feed the clipped DEM to the
        2D section / 3D viewers so the visualisations show only the
        intervention area.
        """
        try:
            from qgis.analysis import QgsZonalStatistics

            # Always refresh combos first so freshly-loaded layers show up
            self.populate_raster_combos()
            self.populate_vector_combos()

            layer_dem_id = self.comboBox_dem_pre.currentData()
            layer_poly_id = self.comboBox_layer_poligono.currentData()

            if not layer_dem_id or not layer_poly_id:
                QMessageBox.warning(self, self.MSG_BOX_TITLE,
                                    "Select DEM and polygon layers")
                return

            layer_dem = QgsProject.instance().mapLayer(layer_dem_id)
            layer_poly = QgsProject.instance().mapLayer(layer_poly_id)
            if not layer_dem or not layer_poly:
                QMessageBox.warning(self, self.MSG_BOX_TITLE,
                                    "Could not load layers")
                return

            sito = self.comboBox_sito.currentText() or 'site'
            out_dir = dem_viz.ensure_output_dir(sito)
            group_name = (
                dem_viz.GROUP_NAME_IT if self.L == 'it' else dem_viz.GROUP_NAME_EN
            )

            # ---- Clip the DEM to the polygon ----
            # This is what makes the section / 3D viewers show only the
            # intervention area. Clip failures are surfaced to the
            # message bar so the user can see why.
            clipped_dem_layer = None
            clipped_dem_path = None
            clip_messages = []

            clipped_dem_path_out = os.path.join(
                out_dir, dem_viz.timestamped_name('dem_clipped', 'tif'))
            clipped_dem_path, clip_err = dem_viz.clip_raster_by_polygon(
                layer_dem.source(), layer_poly, clipped_dem_path_out)
            if clipped_dem_path:
                clipped_dem_layer = QgsRasterLayer(
                    clipped_dem_path, f"DEM clipped - {sito}")
                if clipped_dem_layer.isValid():
                    dem_viz.add_layer_to_group(
                        clipped_dem_layer, group_name=group_name)
                    clip_messages.append(
                        f"DEM clipped: {os.path.basename(clipped_dem_path)}")
                else:
                    clipped_dem_layer = None
                    clip_messages.append('clipped DEM file is not a valid raster')
            else:
                clip_messages.append(f'DEM clip failed: {clip_err}')

            if clip_messages:
                self._notify_info('Clip polygon', ' | '.join(clip_messages))

            # Zonal statistics on the ORIGINAL DEM (accurate figures)
            def _zstat(name):
                enum_cls = getattr(QgsZonalStatistics, 'Statistic', None)
                if enum_cls is not None and hasattr(enum_cls, name):
                    return getattr(enum_cls, name)
                return getattr(QgsZonalStatistics, name)

            stats_flags = (_zstat('Sum') | _zstat('Count') |
                           _zstat('Min') | _zstat('Max'))
            zs = QgsZonalStatistics(layer_poly, layer_dem, 'dem_', 1, stats_flags)
            zs.calculateStatistics(None)

            total_area = 0.0
            total_volume = 0.0
            quota_min = float('inf')
            quota_max = float('-inf')
            pixel_area = abs(
                layer_dem.rasterUnitsPerPixelX() * layer_dem.rasterUnitsPerPixelY()
            )

            for feat in layer_poly.getFeatures():
                count = feat['dem_count'] if feat['dem_count'] else 0
                dem_sum = feat['dem_sum'] if feat['dem_sum'] else 0
                dem_min = feat['dem_min'] if feat['dem_min'] else 0
                dem_max = feat['dem_max'] if feat['dem_max'] else 0
                total_area += count * pixel_area
                # Volume = Σ(max_elev − cell_elev) × pixel_area
                #        = (dem_max × count − dem_sum) × pixel_area
                # Interpretation: volume of the depression below the
                # polygon's highest point — the archaeological standard
                # for computing cubic metres from a single DEM, treating
                # the polygon's peak elevation as the original surface.
                #
                # The previous formula used ``abs(dem_sum) * pixel_area``
                # which is the integral of absolute elevation over the
                # polygon area — a meaningless number that gave results
                # like 70 000 m³ for a trench of a few dozen m² because
                # every cell contributed its ~1130 m elevation instead
                # of its depth.
                if count and dem_max is not None and dem_sum is not None:
                    try:
                        feat_volume = (float(dem_max) * float(count)
                                        - float(dem_sum)) * pixel_area
                        # Guard against floating-point rounding into
                        # slightly-negative territory
                        if feat_volume < 0:
                            feat_volume = 0.0
                        total_volume += feat_volume
                    except (TypeError, ValueError):
                        pass
                if dem_min is not None and dem_min < quota_min:
                    quota_min = dem_min
                if dem_max is not None and dem_max > quota_max:
                    quota_max = dem_max

            if quota_min == float('inf'):
                quota_min = 0.0
            if quota_max == float('-inf'):
                quota_max = 0.0

            self.label_area_mq.setText(f"{total_area:.2f} m\u00b2")
            self.label_volume_mc.setText(f"{total_volume:.2f} m\u00b3")
            self._recompute_costs()

            # Make sure the polygon layer is in the dashboard group
            root = QgsProject.instance().layerTreeRoot()
            if not root.findLayer(layer_poly.id()):
                dem_viz.add_layer_to_group(layer_poly, group_name=group_name)

            # Use the clipped DEM extent for the zoom when possible
            zoom_layer = clipped_dem_layer if clipped_dem_layer else layer_poly
            dem_viz.zoom_canvas_to(self.iface, zoom_layer.extent())

            # Pass the CLIPPED DEM to the viewers so they show only the
            # intervention area. In polygon mode there is no "post" DEM,
            # so the section viewer falls back to the single-DEM layout
            # (elevation heatmap + histogram + elevation profiles).
            terrain_for_viewers = clipped_dem_layer or layer_dem
            self._last_calc.update({
                'diff_raster_path': (clipped_dem_path
                                     if clipped_dem_path else None),
                'diff_raster_layer': clipped_dem_layer,
                'poly_layer': layer_poly,
                'terrain_layer': terrain_for_viewers,
                'layer_post': None,
                'clip_poly_layer': layer_poly,
                'mesh_pre_layer': None,
                'mesh_post_layer': None,
                'stats': {
                    'total_area_m2': total_area,
                    'total_volume_m3': total_volume,
                    'cut_volume_m3': 0.0,
                    'fill_volume_m3': 0.0,
                    'max_abs': max(abs(quota_min), abs(quota_max), 0.5),
                    'min_value': quota_min,
                    'max_value': quota_max,
                },
                'sito': sito,
                'tipo': 'dem_poligono',
            })
            self._enable_viz_buttons(True, mesh_ready=False)

        except Exception as e:
            QMessageBox.warning(self, self.MSG_BOX_TITLE, f"Error: {str(e)}")

    # -------------------------------------------------------------- 2D / 3D --

    def _enable_viz_buttons(self, enabled, mesh_ready=False):
        """Enable/disable the 2D/3D/mesh buttons."""
        for btn_name in ('pushButton_show_2d', 'pushButton_show_3d',
                         'pushButton_build_mesh'):
            btn = getattr(self, btn_name, None)
            if btn is not None:
                btn.setEnabled(enabled)

    def _notify_info(self, title, text):
        """
        Push a non-blocking info message to the QGIS message bar and
        mirror it to the pyArchInit log tab. The message bar's
        ``pushMessage`` sometimes writes its own log line too; we only
        explicitly log when the message bar is NOT available so we
        avoid duplicate log entries.
        """
        pushed = False
        try:
            bar = self.iface.messageBar() if self.iface else None
            if bar is not None:
                bar.pushMessage(title, text, level=0, duration=12)
                pushed = True
        except Exception:
            pass
        if not pushed:
            try:
                from qgis.core import QgsMessageLog
                QgsMessageLog.logMessage(f"{title}: {text}", 'pyArchInit')
            except Exception:
                pass

    def _on_show_2d(self):
        """
        Open a matplotlib-based section viewer on the last calculation:
        heat-map of the DEM difference, longitudinal + transverse sections
        through the DEMs (pre, post, excavated volume) and a cut/fill
        histogram. Falls back to a plain canvas zoom if matplotlib is
        missing.
        """
        terrain = self._last_calc.get('terrain_layer')
        post = self._last_calc.get('layer_post')
        diff_path = self._last_calc.get('diff_raster_path')
        if terrain is None and diff_path is None:
            QMessageBox.information(self, self.MSG_BOX_TITLE,
                                    "Run 'Calcola' first.")
            return
        try:
            from .DemPlotDialogs import DemSectionViewerDialog
            dlg = DemSectionViewerDialog(
                self,
                dem_pre_layer=terrain,
                dem_post_layer=post,
                diff_raster_path=diff_path,
                lang=self.L,
            )
            dlg.exec()
            return
        except Exception as e:
            # Fall back: zoom the main canvas to the diff layer
            layer = (self._last_calc.get('diff_raster_layer') or
                     self._last_calc.get('poly_layer') or terrain)
            if layer is not None:
                try:
                    dem_viz.zoom_canvas_to(self.iface, layer.extent())
                    if hasattr(self.iface, 'setActiveLayer'):
                        self.iface.setActiveLayer(layer)
                    return
                except Exception:
                    pass
            QMessageBox.warning(self, self.MSG_BOX_TITLE,
                                f"Section viewer failed: {e}")

    def _on_show_3d(self):
        """
        Open a 3D viewer on the last calculation.

        Preference order:
          1. **PyVista** (native VTK in a Qt widget) — best quality,
             real lighting, handles NaN cleanly, GPU-accelerated.
             Bundled in ``ext_libs/`` so this is normally chosen.
          2. **Plotly** in a ``QWebEngineView`` — interactive,
             handles NaN, but needs ``plotly`` installed and Qt
             WebEngine available.
          3. **Qgs3DMapCanvas** (``qgis._3d``) — only when available,
             kept for completeness.
          4. **Matplotlib** ``mpl_toolkits.mplot3d`` — always works
             (matplotlib is a plugin dependency) but produces edge
             spikes at polygon-clip boundaries.
        """
        terrain = self._last_calc.get('terrain_layer')
        post = self._last_calc.get('layer_post')
        if terrain is None:
            QMessageBox.information(self, self.MSG_BOX_TITLE,
                                    "Run 'Calcola' first.")
            return

        # Pick a 3D backend. Each attempt logs the outcome so the user
        # can see — via View ▸ Panels ▸ Log Messages ▸ pyArchInit — why
        # a given backend was skipped.

        # 1. PyVista (preferred — native VTK, perfect NaN handling)
        pyvista_err = None
        try:
            import pyvista as _pv  # noqa: F401
            from pyvistaqt import QtInteractor as _QtInteractor  # noqa: F401
        except ImportError as e:
            pyvista_err = f'pyvista / pyvistaqt not installed ({e}).'
        except Exception as e:
            pyvista_err = f'pyvista import error: {e}'

        if pyvista_err is None:
            try:
                from .DemPlotDialogs import DemPyVista3dDialog
                self._notify_info('3D', 'using PyVista (VTK)')
                dlg = DemPyVista3dDialog(
                    self,
                    dem_pre_layer=terrain,
                    dem_post_layer=post,
                    diff_raster_path=self._last_calc.get('diff_raster_path'),
                    lang=self.L,
                )
                dlg.exec()
                return
            except Exception as e:
                self._notify_info(
                    '3D', f'PyVista dialog crashed: {e} - falling back')
        else:
            self._notify_info('3D', f'PyVista not used: {pyvista_err}')

        # 2. Plotly (when QWebEngine is available)
        plotly_err = None
        try:
            import plotly.graph_objects as _pgo  # noqa: F401
        except ImportError as e:
            plotly_err = f'plotly not installed ({e}).'
        except Exception as e:
            plotly_err = f'plotly import error: {e}'

        webview_err = None
        if plotly_err is None:
            try:
                from .DemPlotDialogs import (
                    DemPlotly3dDialog,
                    _import_qt_webengine,
                )
                if _import_qt_webengine() is None:
                    webview_err = (
                        'QWebEngineView not available in this QGIS '
                        'profile (Qt WebEngine missing)')
            except Exception as e:
                webview_err = f'DemPlotly3dDialog import failed: {e}'

        if plotly_err is None and webview_err is None:
            try:
                self._notify_info('3D', 'using Plotly (QWebEngineView)')
                dlg = DemPlotly3dDialog(
                    self,
                    dem_pre_layer=terrain,
                    dem_post_layer=post,
                    diff_raster_path=self._last_calc.get('diff_raster_path'),
                    lang=self.L,
                )
                dlg.exec()
                return
            except Exception as e:
                self._notify_info(
                    '3D', f'Plotly dialog crashed: {e} - falling back')
        else:
            reason = plotly_err or webview_err
            self._notify_info('3D', f'Plotly not used: {reason}')

        # 3. Qgs3DMapCanvas (when available)
        try:
            from .Dem3dViewerDialog import Dem3dViewerDialog, _HAS_3D
            if _HAS_3D:
                self._notify_info('3D', 'using Qgs3DMapCanvas')
                dlg = Dem3dViewerDialog(
                    self,
                    terrain_layer=terrain,
                    drape_layer=self._last_calc.get('diff_raster_layer'),
                    mesh_pre_layer=self._last_calc.get('mesh_pre_layer'),
                    mesh_post_layer=self._last_calc.get('mesh_post_layer'),
                    lang=self.L,
                )
                dlg.exec()
                return
            else:
                self._notify_info('3D', 'qgis._3d not available - trying matplotlib')
        except Exception as e:
            self._notify_info('3D', f'Qgs3DMapCanvas error: {e}')

        # 3. Matplotlib fallback
        try:
            from .DemPlotDialogs import DemMatplotlib3dDialog
            self._notify_info('3D', 'using matplotlib (spike artefacts expected at clip edges)')
            dlg = DemMatplotlib3dDialog(
                self,
                dem_pre_layer=terrain,
                dem_post_layer=post,
                diff_raster_path=self._last_calc.get('diff_raster_path'),
                lang=self.L,
            )
            dlg.exec()
        except Exception as e:
            QMessageBox.warning(
                self, self.MSG_BOX_TITLE,
                f"3D viewer unavailable: {e}")

    def _on_build_mesh(self):
        """
        Level 3: export a 2DM mesh for each DEM **to disk** (for use in
        external tools) and then open the matplotlib 3D surface viewer
        on the calculated DEMs.

        Historical note / segfault fix
        ------------------------------
        Previous versions loaded the 2DM files back as
        ``QgsMeshLayer`` instances and added them to the layer tree.
        On several QGIS builds this crashed the whole application,
        because the mesh layer provider (MDAL) or the subsequent
        ``QgsMeshRendererScalarSettings`` calls invoked from Python
        segfaulted. To make this button safe on *every* profile, the
        2DM file is now only written to disk (for export use) and the
        actual 3D visualisation is delegated to the matplotlib 3D
        fallback, which never touches any mesh APIs.
        """
        terrain = self._last_calc.get('terrain_layer')
        post = self._last_calc.get('layer_post')
        clip_poly = self._last_calc.get('clip_poly_layer')
        if terrain is None:
            QMessageBox.information(self, self.MSG_BOX_TITLE,
                                    "Run 'Calcola' first.")
            return
        sito = self._last_calc.get('sito') or 'site'
        out_dir = dem_viz.ensure_output_dir(sito)

        # Busy cursor
        try:
            from qgis.PyQt.QtGui import QCursor
            self.setCursor(QCursor(Qt.CursorShape.WaitCursor
                                   if hasattr(Qt, 'CursorShape')
                                   else Qt.WaitCursor))
        except Exception:
            pass

        built_files = []
        errors = []
        try:
            # Write the 2DM files silently in the background — purely
            # as an on-disk export artefact. We never load them into
            # the QGIS project.
            try:
                pre_2dm = os.path.join(
                    out_dir, dem_viz.timestamped_name('mesh_pre', '2dm'))
                pre_2dm = dem_viz.create_tin_mesh_from_dem(
                    terrain, pre_2dm, clip_poly_layer=clip_poly)
                if pre_2dm:
                    built_files.append(('Pre', pre_2dm))
            except Exception as e:
                errors.append(f"pre 2DM: {e}")

            if post is not None:
                try:
                    post_2dm = os.path.join(
                        out_dir, dem_viz.timestamped_name('mesh_post', '2dm'))
                    post_2dm = dem_viz.create_tin_mesh_from_dem(
                        post, post_2dm, clip_poly_layer=clip_poly)
                    if post_2dm:
                        built_files.append(('Post', post_2dm))
                except Exception as e:
                    errors.append(f"post 2DM: {e}")

            # Now open the 3D viewer on the DEMs (what the user
            # actually wants to see). Prefer PyVista, then Plotly,
            # fall back to matplotlib. Does NOT touch any mesh layer
            # API.
            try:
                opened = False
                # 1. PyVista
                try:
                    import pyvista as _pv  # noqa: F401
                    from pyvistaqt import QtInteractor as _Qti  # noqa: F401
                    from .DemPlotDialogs import DemPyVista3dDialog
                    dlg = DemPyVista3dDialog(
                        self,
                        dem_pre_layer=terrain,
                        dem_post_layer=post,
                        diff_raster_path=self._last_calc.get(
                            'diff_raster_path'),
                        lang=self.L,
                    )
                    dlg.exec()
                    opened = True
                except Exception:
                    opened = False
                # 2. Plotly
                if not opened:
                    try:
                        import plotly.graph_objects as _pgo  # noqa: F401
                        from .DemPlotDialogs import (
                            DemPlotly3dDialog, _import_qt_webengine,
                        )
                        if _import_qt_webengine() is not None:
                            dlg = DemPlotly3dDialog(
                                self,
                                dem_pre_layer=terrain,
                                dem_post_layer=post,
                                diff_raster_path=self._last_calc.get(
                                    'diff_raster_path'),
                                lang=self.L,
                            )
                            dlg.exec()
                            opened = True
                    except Exception:
                        opened = False
                # 3. Matplotlib fallback
                if not opened:
                    from .DemPlotDialogs import DemMatplotlib3dDialog
                    dlg = DemMatplotlib3dDialog(
                        self,
                        dem_pre_layer=terrain,
                        dem_post_layer=post,
                        diff_raster_path=self._last_calc.get(
                            'diff_raster_path'),
                        lang=self.L,
                    )
                    dlg.exec()
            except Exception as e:
                errors.append(f"3D viewer: {e}")

            # Report what happened — non-blocking message bar if we
            # have files + no viewer error, blocking dialog otherwise
            if built_files and not errors:
                file_list = '\n'.join(f"  {n}: {p}" for n, p in built_files)
                QMessageBox.information(
                    self, self.MSG_BOX_TITLE,
                    {
                        'it': ("Mesh 2DM salvate su disco:\n{files}\n\n"
                               "Le mesh non sono caricate nel progetto "
                               "QGIS per evitare i noti crash della "
                               "libreria mesh su alcune build. La vista "
                               "3D matplotlib \u00e8 gi\u00e0 aperta "
                               "sui DEM clippati."),
                        'en': ("2DM meshes saved to disk:\n{files}\n\n"
                               "They are NOT loaded into the QGIS "
                               "project to avoid the known mesh-library "
                               "crash on some builds. The matplotlib 3D "
                               "view is already open on the clipped "
                               "DEMs."),
                    }.get(self.L,
                          "2DM meshes saved:\n{files}\n\n"
                          "Not loaded in the project to avoid mesh crashes. "
                          "The matplotlib 3D view is open.")
                    .format(files=file_list)
                )
            elif errors:
                QMessageBox.warning(
                    self, self.MSG_BOX_TITLE,
                    "Mesh build finished with issues:\n- "
                    + '\n- '.join(errors)
                )
        finally:
            try:
                self.unsetCursor()
            except Exception:
                pass

    def on_pushButton_salva_computo_pressed(self):
        """Save computo metrico result to database"""
        try:
            sito = self.comboBox_sito.currentText()
            if not sito or not self.DB_MANAGER:
                return

            area_text = self.label_area_mq.text().replace(' m\u00b2', '').replace(' m2', '')
            volume_text = self.label_volume_mc.text().replace(' m\u00b3', '').replace(' m3', '')

            try:
                area_val = float(area_text)
                volume_val = float(volume_text)
            except ValueError:
                QMessageBox.warning(self, self.MSG_BOX_TITLE, "No calculation results to save")
                return

            tipo = 'differenza_dem' if self.radioButton_diff_dem.isChecked() else 'dem_poligono'
            dem_pre_name = self.comboBox_dem_pre.currentText()
            dem_post_name = self.comboBox_dem_post.currentText()
            poly_name = self.comboBox_layer_poligono.currentText()

            next_id = self.DB_MANAGER.max_num_id('COMPUTO_METRICO', 'id_computo') + 1

            data = self.DB_MANAGER.insert_computo_metrico_values(
                next_id,
                sito,
                f"Calcolo {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                tipo,
                dem_pre_name,
                dem_post_name,
                poly_name,
                area_val,
                volume_val,
                0.0,  # quota_min
                0.0,  # quota_max
                date.today().isoformat(),
                '',   # fase_scavo
                ''    # note
            )
            self.DB_MANAGER.insert_data_session(data)
            self.refresh_computo_history(sito)
            QMessageBox.information(self, self.MSG_BOX_TITLE, "Computo saved!")
        except Exception as e:
            QMessageBox.warning(self, self.MSG_BOX_TITLE, f"Error saving: {str(e)}")

    def _clear_chart_layout(self):
        """Clear existing widgets from widget_chart layout, creating one if needed."""
        from qgis.PyQt.QtWidgets import QVBoxLayout
        layout = self.widget_chart.layout()
        if layout is None:
            layout = QVBoxLayout(self.widget_chart)
            layout.setContentsMargins(0, 0, 0, 0)
        else:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
        return layout

    def _aggregate_budget_by_category(self, records):
        """Aggregate budget records by category, returning dict of {category: total}."""
        cat_totals = {}
        default_label = 'Altro' if self.L == 'it' else 'Other'
        for r in records:
            cat = r.categoria or default_label
            cat_totals[cat] = cat_totals.get(cat, 0) + (r.importo_effettivo or 0)
        return cat_totals

    def _get_chart_title(self):
        """Return locale-aware chart title."""
        titles = {
            'it': 'Budget per Categoria',
            'en': 'Budget by Category',
            'de': 'Budget nach Kategorie',
            'es': 'Presupuesto por Categoría',
            'fr': 'Budget par Catégorie',
            'ar': 'الميزانية حسب الفئة',
            'ca': 'Pressupost per Categoria',
            'ro': 'Buget pe Categorie',
            'pt': 'Orçamento por Categoria',
            'el': 'Προϋπολογισμός ανά Κατηγορία',
        }
        return titles.get(self.L, titles['en'])

    def draw_budget_chart(self, records):
        """Draw an interactive Plotly pie chart in QWebEngineView, with matplotlib fallback."""
        cat_totals = self._aggregate_budget_by_category(records)
        if not cat_totals or sum(cat_totals.values()) == 0:
            return

        # Try Plotly + QWebEngineView first
        if self._draw_budget_chart_plotly(cat_totals):
            return

        # Fallback to matplotlib
        self._draw_budget_chart_matplotlib(cat_totals)

    def _draw_budget_chart_plotly(self, cat_totals):
        """Render an interactive Plotly pie chart inside QWebEngineView. Returns True on success."""
        try:
            import plotly.graph_objects as go
        except ImportError:
            return False

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

        try:
            layout = self._clear_chart_layout()

            labels = list(cat_totals.keys())
            values = list(cat_totals.values())

            # Professional color palette (Material Design inspired)
            colors = [
                '#1565C0', '#00897B', '#EF6C00', '#6A1B9A',
                '#C62828', '#2E7D32', '#AD1457', '#4527A0',
                '#00838F', '#F9A825', '#4E342E',
            ]

            title_text = self._get_chart_title()

            fig = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                hole=0.4,
                marker=dict(
                    colors=colors[:len(labels)],
                    line=dict(color='#ffffff', width=2),
                ),
                textinfo='label+percent',
                textfont=dict(size=11, family='Segoe UI, Helvetica, Arial, sans-serif'),
                hovertemplate='<b>%{label}</b><br>€ %{value:,.2f}<br>%{percent}<extra></extra>',
                sort=False,
            )])

            fig.update_layout(
                title=dict(
                    text=title_text,
                    font=dict(size=14, family='Segoe UI, Helvetica, Arial, sans-serif', color='#2c3e50'),
                    x=0.5,
                    xanchor='center',
                ),
                margin=dict(l=10, r=10, t=40, b=10),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                showlegend=True,
                legend=dict(
                    font=dict(size=10, family='Segoe UI, Helvetica, Arial, sans-serif'),
                    orientation='h',
                    yanchor='bottom',
                    y=-0.15,
                    xanchor='center',
                    x=0.5,
                ),
            )

            html_content = fig.to_html(
                include_plotlyjs='cdn',
                full_html=True,
                config={
                    'displayModeBar': False,
                    'responsive': True,
                },
            )

            # Inject responsive viewport meta and body style
            html_content = html_content.replace(
                '<head>',
                '<head><meta name="viewport" content="width=device-width, initial-scale=1">'
                '<style>body{margin:0;padding:0;overflow:hidden;}'
                '.plotly-graph-div{width:100%!important;height:100%!important;}</style>',
            )

            web_view = QWebEngineView()
            web_view.setHtml(html_content)
            layout.addWidget(web_view)
            return True

        except Exception:
            return False

    def _draw_budget_chart_matplotlib(self, cat_totals):
        """Fallback: render a matplotlib pie chart on a Qt canvas."""
        try:
            # backend_qtagg auto-detects Qt5/Qt6 (matplotlib >= 3.5)
            try:
                from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
            except ImportError:
                from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
            from matplotlib.figure import Figure

            layout = self._clear_chart_layout()

            fig = Figure(figsize=(4, 3), dpi=80)
            ax = fig.add_subplot(111)
            colors = ['#1565C0', '#00897B', '#EF6C00', '#6A1B9A',
                      '#C62828', '#2E7D32', '#AD1457', '#4527A0',
                      '#00838F', '#F9A825', '#4E342E']

            labels = list(cat_totals.keys())
            sizes = list(cat_totals.values())
            ax.pie(sizes, labels=labels, colors=colors[:len(labels)],
                   autopct='%1.0f%%', startangle=90, textprops={'fontsize': 7})
            ax.set_title(self._get_chart_title(), fontsize=9)
            ax.set_aspect('equal')
            fig.tight_layout()

            canvas = FigureCanvasQTAgg(fig)
            layout.addWidget(canvas)
            canvas.draw()
        except ImportError:
            pass
        except Exception:
            pass


    # ---------------------------------------------------------------- fonts --
    @staticmethod
    def _register_unicode_fonts():
        """
        Register DejaVu Sans TTF family with ReportLab so the dashboard
        PDF can render the full Unicode range (Romanian, Greek, Arabic,
        Cyrillic, ...). Returns the 4 font names to use for body / bold /
        italic / bold-italic. Falls back to the PDF core Helvetica family
        if DejaVu cannot be loaded.

        DejaVu is shipped with matplotlib (``ext_libs/matplotlib/mpl-data/
        fonts/ttf``), which is a hard dependency of the plugin, so it is
        virtually always available.
        """
        regular = 'Helvetica'
        bold = 'Helvetica-Bold'
        italic = 'Helvetica-Oblique'
        bold_italic = 'Helvetica-BoldOblique'
        try:
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont

            # Already registered in a previous export call?
            already = set(pdfmetrics.getRegisteredFontNames())
            if 'DejaVuSans' in already:
                return 'DejaVuSans', 'DejaVuSans-Bold', \
                       'DejaVuSans-Oblique', 'DejaVuSans-BoldOblique'

            # Search for DejaVu TTFs inside matplotlib's bundled font dir
            try:
                import matplotlib
                mpl_font_dir = os.path.join(
                    os.path.dirname(matplotlib.__file__),
                    'mpl-data', 'fonts', 'ttf'
                )
            except Exception:
                mpl_font_dir = None

            candidates = {
                'DejaVuSans':              'DejaVuSans.ttf',
                'DejaVuSans-Bold':         'DejaVuSans-Bold.ttf',
                'DejaVuSans-Oblique':      'DejaVuSans-Oblique.ttf',
                'DejaVuSans-BoldOblique':  'DejaVuSans-BoldOblique.ttf',
            }
            registered = 0
            for name, filename in candidates.items():
                path = None
                if mpl_font_dir and os.path.exists(
                        os.path.join(mpl_font_dir, filename)):
                    path = os.path.join(mpl_font_dir, filename)
                if path:
                    try:
                        pdfmetrics.registerFont(TTFont(name, path))
                        registered += 1
                    except Exception:
                        pass
            if registered >= 1:
                try:
                    pdfmetrics.registerFontFamily(
                        'DejaVuSans',
                        normal='DejaVuSans',
                        bold='DejaVuSans-Bold',
                        italic='DejaVuSans-Oblique',
                        boldItalic='DejaVuSans-BoldOblique',
                    )
                except Exception:
                    pass
                regular = 'DejaVuSans'
                bold = 'DejaVuSans-Bold' if registered >= 2 else regular
                italic = 'DejaVuSans-Oblique' if registered >= 3 else regular
                bold_italic = 'DejaVuSans-BoldOblique' if registered == 4 else bold
        except Exception:
            pass
        return regular, bold, italic, bold_italic

    def on_pushButton_export_pdf_pressed(self):
        """Export a professional dashboard PDF with budget, personnel,
        equipment and computo metrico sections.

        Uses DejaVu Sans (bundled with matplotlib) for full Unicode
        support - correctly renders Romanian (ă, ț, ș), Greek, Arabic, etc.
        """
        sito = self.comboBox_sito.currentText()
        anno = self.comboBox_anno.currentText()
        if not sito:
            QMessageBox.warning(self, "Warning", "Select a site first.", QMessageBox.StandardButton.Ok)
            return

        home = os.environ.get('PYARCHINIT_HOME', os.path.expanduser('~'))
        # Sanitize filename for cross-OS safety but keep Unicode site name
        safe_sito = ''.join(c if c not in '\\/:*?"<>|' else '_' for c in sito)
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export PDF",
            os.path.join(home, f"site_dashboard_{safe_sito}_{anno}.pdf"),
            "PDF (*.pdf)")
        if not file_path:
            return

        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.units import cm, mm
            from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
                                            Paragraph, Spacer, PageBreak, KeepTogether)
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
            from reportlab.platypus.flowables import HRFlowable
            from reportlab.graphics.shapes import Drawing, Rect, String, Line, Group
            from reportlab.graphics import renderPDF
            from datetime import datetime

            # Register Unicode fonts and use them throughout the document
            F_REG, F_BOLD, F_ITAL, F_BI = self._register_unicode_fonts()

            lang = self.L
            page_w, page_h = A4  # 595.27, 841.89 points

            # --- Color scheme ---
            CLR_HEADER = colors.HexColor('#1a237e')
            CLR_ACCENT = colors.HexColor('#e3f2fd')
            CLR_ROW_ALT = colors.HexColor('#f5f7fa')
            CLR_TEXT_LIGHT = colors.white
            CLR_BORDER = colors.HexColor('#bbdefb')
            CLR_BUDGET = colors.HexColor('#1565c0')
            CLR_ACTUAL = colors.HexColor('#e65100')
            CLR_SUMMARY_BG = colors.HexColor('#e8eaf6')
            CLR_SECTION_LINE = colors.HexColor('#3949ab')

            # --- i18n ---
            i18n = {
                'it': {
                    'title': 'Dashboard Cantiere',
                    'subtitle': 'Riepilogo operativo del cantiere',
                    'site': 'Cantiere', 'year': 'Anno', 'generated': 'Generato il',
                    'budget_section': 'Riepilogo Budget',
                    'budget_headers': ['Categoria', 'Descrizione', 'Preventivato', 'Effettivo', 'Differenza'],
                    'total': 'TOTALE', 'budgeted': 'Preventivato', 'actual': 'Effettivo',
                    'personnel_section': 'Personale',
                    'pers_headers': ['Nome', 'Cognome', 'Ruolo', 'Contratto', 'Email', 'Tariffa Giorn.'],
                    'equip_section': 'Inventario Attrezzature',
                    'equip_headers': ['Codice', 'Nome', 'Categoria', 'Marca', 'Modello', 'Stato'],
                    'statistics': 'Statistiche',
                    'total_personnel': 'Totale Personale',
                    'total_equipment': 'Totale Attrezzature',
                    'budget_variance': 'Variazione Budget',
                    'budget_chart': 'Grafico Budget per Categoria',
                    'page': 'Pagina',
                    'footer': 'pyArchInit - Gestione Dati Archeologici',
                    'no_data': 'Nessun dato disponibile',
                    'computo_section': 'Computo Metrico',
                    'computo_headers': ['Data', 'Tipo', 'Nome', 'Area (m\u00b2)',
                                         'Volume (m\u00b3)', 'Quota min', 'Quota max', 'Note'],
                    'total_area': 'Area totale',
                    'total_volume': 'Volume totale',
                    'cut_volume': 'Scavo (cut)',
                    'fill_volume': 'Riporto (fill)',
                    'total_computi': 'N. Computi',
                },
                'en': {
                    'title': 'Site Dashboard',
                    'subtitle': 'Operational site summary',
                    'site': 'Site', 'year': 'Year', 'generated': 'Generated on',
                    'budget_section': 'Budget Summary',
                    'budget_headers': ['Category', 'Description', 'Budgeted', 'Actual', 'Variance'],
                    'total': 'TOTAL', 'budgeted': 'Budgeted', 'actual': 'Actual',
                    'personnel_section': 'Personnel',
                    'pers_headers': ['First Name', 'Last Name', 'Role', 'Contract', 'Email', 'Daily Rate'],
                    'equip_section': 'Equipment Inventory',
                    'equip_headers': ['Code', 'Name', 'Category', 'Brand', 'Model', 'Status'],
                    'statistics': 'Statistics',
                    'total_personnel': 'Total Personnel',
                    'total_equipment': 'Total Equipment',
                    'budget_variance': 'Budget Variance',
                    'budget_chart': 'Budget by Category',
                    'page': 'Page',
                    'footer': 'pyArchInit - Archaeological Data Management',
                    'no_data': 'No data available',
                    'computo_section': 'Quantity Surveying',
                    'computo_headers': ['Date', 'Type', 'Name', 'Area (m\u00b2)',
                                         'Volume (m\u00b3)', 'Min elev.', 'Max elev.', 'Notes'],
                    'total_area': 'Total area',
                    'total_volume': 'Total volume',
                    'cut_volume': 'Cut volume',
                    'fill_volume': 'Fill volume',
                    'total_computi': '# Records',
                },
                'de': {
                    'title': 'Fundstellen-Dashboard',
                    'subtitle': 'Operative Zusammenfassung',
                    'site': 'Fundstelle', 'year': 'Jahr', 'generated': 'Erstellt am',
                    'budget_section': 'Budget\u00fcbersicht',
                    'budget_headers': ['Kategorie', 'Beschreibung', 'Geplant', 'Tats\u00e4chlich', 'Differenz'],
                    'total': 'GESAMT', 'budgeted': 'Geplant', 'actual': 'Tats\u00e4chlich',
                    'personnel_section': 'Personal',
                    'pers_headers': ['Vorname', 'Nachname', 'Rolle', 'Vertrag', 'E-Mail', 'Tagessatz'],
                    'equip_section': 'Ausr\u00fcstungsinventar',
                    'equip_headers': ['Code', 'Name', 'Kategorie', 'Marke', 'Modell', 'Status'],
                    'statistics': 'Statistiken',
                    'total_personnel': 'Gesamtpersonal',
                    'total_equipment': 'Gesamtausr\u00fcstung',
                    'budget_variance': 'Budgetabweichung',
                    'budget_chart': 'Budget nach Kategorie',
                    'page': 'Seite',
                    'footer': 'pyArchInit - Arch\u00e4ologische Datenverwaltung',
                    'no_data': 'Keine Daten verf\u00fcgbar',
                    'computo_section': 'Mengenermittlung',
                    'computo_headers': ['Datum', 'Typ', 'Name', 'Fl\u00e4che (m\u00b2)',
                                         'Volumen (m\u00b3)', 'Min H\u00f6he', 'Max H\u00f6he', 'Notizen'],
                    'total_area': 'Gesamtfl\u00e4che',
                    'total_volume': 'Gesamtvolumen',
                    'cut_volume': 'Abtrag',
                    'fill_volume': 'Auftrag',
                    'total_computi': 'Datens\u00e4tze',
                },
                'es': {
                    'title': 'Panel del Sitio',
                    'subtitle': 'Resumen operativo del sitio',
                    'site': 'Sitio', 'year': 'A\u00f1o', 'generated': 'Generado el',
                    'budget_section': 'Resumen Presupuesto',
                    'budget_headers': ['Categor\u00eda', 'Descripci\u00f3n', 'Presupuestado', 'Real', 'Diferencia'],
                    'total': 'TOTAL', 'budgeted': 'Presupuestado', 'actual': 'Real',
                    'personnel_section': 'Personal',
                    'pers_headers': ['Nombre', 'Apellido', 'Rol', 'Contrato', 'Email', 'Tarifa Diaria'],
                    'equip_section': 'Inventario de Equipos',
                    'equip_headers': ['C\u00f3digo', 'Nombre', 'Categor\u00eda', 'Marca', 'Modelo', 'Estado'],
                    'statistics': 'Estad\u00edsticas',
                    'total_personnel': 'Total Personal',
                    'total_equipment': 'Total Equipos',
                    'budget_variance': 'Variaci\u00f3n Presupuesto',
                    'budget_chart': 'Presupuesto por Categor\u00eda',
                    'page': 'P\u00e1gina',
                    'footer': 'pyArchInit - Gesti\u00f3n de Datos Arqueol\u00f3gicos',
                    'no_data': 'Sin datos disponibles',
                    'computo_section': 'Mediciones',
                    'computo_headers': ['Fecha', 'Tipo', 'Nombre', '\u00c1rea (m\u00b2)',
                                         'Volumen (m\u00b3)', 'Cota m\u00edn', 'Cota m\u00e1x', 'Notas'],
                    'total_area': '\u00c1rea total',
                    'total_volume': 'Volumen total',
                    'cut_volume': 'Excavaci\u00f3n',
                    'fill_volume': 'Relleno',
                    'total_computi': 'N. Registros',
                },
                'fr': {
                    'title': 'Tableau de Bord du Chantier',
                    'subtitle': 'R\u00e9sum\u00e9 op\u00e9rationnel du chantier',
                    'site': 'Chantier', 'year': 'Ann\u00e9e', 'generated': 'G\u00e9n\u00e9r\u00e9 le',
                    'budget_section': 'R\u00e9sum\u00e9 du Budget',
                    'budget_headers': ['Cat\u00e9gorie', 'Description', 'Pr\u00e9vu', 'R\u00e9el', '\u00c9cart'],
                    'total': 'TOTAL', 'budgeted': 'Pr\u00e9vu', 'actual': 'R\u00e9el',
                    'personnel_section': 'Personnel',
                    'pers_headers': ['Pr\u00e9nom', 'Nom', 'R\u00f4le', 'Contrat', 'Email', 'Tarif Journalier'],
                    'equip_section': 'Inventaire des \u00c9quipements',
                    'equip_headers': ['Code', 'Nom', 'Cat\u00e9gorie', 'Marque', 'Mod\u00e8le', '\u00c9tat'],
                    'statistics': 'Statistiques',
                    'total_personnel': 'Total Personnel',
                    'total_equipment': 'Total \u00c9quipements',
                    'budget_variance': '\u00c9cart Budg\u00e9taire',
                    'budget_chart': 'Budget par Cat\u00e9gorie',
                    'page': 'Page',
                    'footer': 'pyArchInit - Gestion des Donn\u00e9es Arch\u00e9ologiques',
                    'no_data': 'Aucune donn\u00e9e disponible',
                    'computo_section': 'M\u00e9tr\u00e9',
                    'computo_headers': ['Date', 'Type', 'Nom', 'Aire (m\u00b2)',
                                         'Volume (m\u00b3)', 'Cote min', 'Cote max', 'Notes'],
                    'total_area': 'Aire totale',
                    'total_volume': 'Volume total',
                    'cut_volume': 'D\u00e9blai',
                    'fill_volume': 'Remblai',
                    'total_computi': 'Nb enreg.',
                },
                'ca': {
                    'title': "Tauler d'Obra",
                    'subtitle': "Resum operatiu de l'obra",
                    'site': 'Lloc', 'year': 'Any', 'generated': 'Generat el',
                    'budget_section': 'Resum Pressupost',
                    'budget_headers': ['Categoria', 'Descripci\u00f3', 'Pressupostat', 'Real', 'Difer\u00e8ncia'],
                    'total': 'TOTAL', 'budgeted': 'Pressupostat', 'actual': 'Real',
                    'personnel_section': 'Personal',
                    'pers_headers': ['Nom', 'Cognom', 'Rol', 'Contracte', 'Email', 'Tarifa Di\u00e0ria'],
                    'equip_section': "Inventari d'Equipament",
                    'equip_headers': ['Codi', 'Nom', 'Categoria', 'Marca', 'Model', 'Estat'],
                    'statistics': 'Estad\u00edstiques',
                    'total_personnel': 'Total Personal',
                    'total_equipment': 'Total Equipament',
                    'budget_variance': 'Variaci\u00f3 Pressupost',
                    'budget_chart': 'Pressupost per Categoria',
                    'page': 'P\u00e0gina',
                    'footer': 'pyArchInit - Gesti\u00f3 de Dades Arqueol\u00f2giques',
                    'no_data': 'Sense dades disponibles',
                    'computo_section': 'Amidament',
                    'computo_headers': ['Data', 'Tipus', 'Nom', '\u00c0rea (m\u00b2)',
                                         'Volum (m\u00b3)', 'Cota min', 'Cota max', 'Notes'],
                    'total_area': '\u00c0rea total',
                    'total_volume': 'Volum total',
                    'cut_volume': 'Excavaci\u00f3',
                    'fill_volume': 'Reompliment',
                    'total_computi': 'N. Registres',
                },
                'ro': {
                    'title': '\u0218antier - Panou',
                    'subtitle': 'Rezumat operativ al \u0219antierului',
                    'site': 'Sit', 'year': 'An', 'generated': 'Generat la',
                    'budget_section': 'Rezumat Buget',
                    'budget_headers': ['Categorie', 'Descriere', 'Planificat', 'Realizat', 'Diferen\u021b\u0103'],
                    'total': 'TOTAL', 'budgeted': 'Planificat', 'actual': 'Realizat',
                    'personnel_section': 'Personal',
                    'pers_headers': ['Nume', 'Prenume', 'Rol', 'Contract', 'Email', 'Tarif Zilnic'],
                    'equip_section': 'Inventar Echipamente',
                    'equip_headers': ['Cod', 'Nume', 'Categorie', 'Marc\u0103', 'Model', 'Stare'],
                    'statistics': 'Statistici',
                    'total_personnel': 'Total Personal',
                    'total_equipment': 'Total Echipamente',
                    'budget_variance': 'Varia\u021bie Buget',
                    'budget_chart': 'Buget pe Categorie',
                    'page': 'Pagina',
                    'footer': 'pyArchInit - Gestiune Date Arheologice',
                    'no_data': 'Nu exist\u0103 date disponibile',
                    'computo_section': 'M\u0103sur\u0103tori',
                    'computo_headers': ['Data', 'Tip', 'Nume', 'Suprafa\u021b\u0103 (m\u00b2)',
                                         'Volum (m\u00b3)', 'Cot\u0103 min', 'Cot\u0103 max', 'Note'],
                    'total_area': 'Suprafa\u021b\u0103 total\u0103',
                    'total_volume': 'Volum total',
                    'cut_volume': 'S\u0103pare',
                    'fill_volume': 'Umplere',
                    'total_computi': 'Nr. \u00cenregistr\u0103ri',
                },
                'pt': {
                    'title': 'Painel de Obra',
                    'subtitle': 'Resumo operacional do s\u00edtio',
                    'site': 'S\u00edtio', 'year': 'Ano', 'generated': 'Gerado em',
                    'budget_section': 'Resumo Or\u00e7amento',
                    'budget_headers': ['Categoria', 'Descri\u00e7\u00e3o', 'Previsto', 'Real', 'Diferen\u00e7a'],
                    'total': 'TOTAL', 'budgeted': 'Previsto', 'actual': 'Real',
                    'personnel_section': 'Pessoal',
                    'pers_headers': ['Nome', 'Apelido', 'Fun\u00e7\u00e3o', 'Contrato', 'Email', 'Tarifa Di\u00e1ria'],
                    'equip_section': 'Invent\u00e1rio de Equipamento',
                    'equip_headers': ['C\u00f3digo', 'Nome', 'Categoria', 'Marca', 'Modelo', 'Estado'],
                    'statistics': 'Estat\u00edsticas',
                    'total_personnel': 'Total Pessoal',
                    'total_equipment': 'Total Equipamento',
                    'budget_variance': 'Varia\u00e7\u00e3o Or\u00e7amento',
                    'budget_chart': 'Or\u00e7amento por Categoria',
                    'page': 'P\u00e1gina',
                    'footer': 'pyArchInit - Gest\u00e3o de Dados Arqueol\u00f3gicos',
                    'no_data': 'Sem dados dispon\u00edveis',
                    'computo_section': 'Medi\u00e7\u00e3o',
                    'computo_headers': ['Data', 'Tipo', 'Nome', '\u00c1rea (m\u00b2)',
                                         'Volume (m\u00b3)', 'Cota m\u00edn', 'Cota m\u00e1x', 'Notas'],
                    'total_area': '\u00c1rea total',
                    'total_volume': 'Volume total',
                    'cut_volume': 'Corte',
                    'fill_volume': 'Aterro',
                    'total_computi': 'N. Registos',
                },
                'el': {
                    'title': '\u03a0\u03af\u03bd\u03b1\u03ba\u03b1\u03c2 \u0395\u03c1\u03b3\u03bf\u03c4\u03b1\u03be\u03af\u03bf\u03c5',
                    'subtitle': '\u039b\u03b5\u03b9\u03c4\u03bf\u03c5\u03c1\u03b3\u03b9\u03ba\u03ae \u03c3\u03cd\u03bd\u03bf\u03c8\u03b7',
                    'site': '\u0398\u03ad\u03c3\u03b7', 'year': '\u0388\u03c4\u03bf\u03c2',
                    'generated': '\u0394\u03b7\u03bc\u03b9\u03bf\u03c5\u03c1\u03b3\u03ae\u03b8\u03b7\u03ba\u03b5',
                    'budget_section': '\u03a0\u03c1\u03bf\u03cb\u03c0\u03bf\u03bb\u03bf\u03b3\u03b9\u03c3\u03bc\u03cc\u03c2',
                    'budget_headers': ['\u039a\u03b1\u03c4\u03b7\u03b3\u03bf\u03c1\u03af\u03b1',
                                       '\u03a0\u03b5\u03c1\u03b9\u03b3\u03c1\u03b1\u03c6\u03ae',
                                       '\u03a0\u03c1\u03bf\u03cb\u03c0\u03bf\u03bb.',
                                       '\u03a0\u03c1\u03b1\u03b3\u03bc.',
                                       '\u0394\u03b9\u03b1\u03c6\u03bf\u03c1\u03ac'],
                    'total': '\u03a3\u03a5\u039d\u039f\u039b\u039f',
                    'budgeted': '\u03a0\u03c1\u03bf\u03cb\u03c0\u03bf\u03bb.',
                    'actual': '\u03a0\u03c1\u03b1\u03b3\u03bc.',
                    'personnel_section': '\u03a0\u03c1\u03bf\u03c3\u03c9\u03c0\u03b9\u03ba\u03cc',
                    'pers_headers': ['\u038c\u03bd\u03bf\u03bc\u03b1', '\u0395\u03c0\u03ce\u03bd\u03c5\u03bc\u03bf',
                                     '\u03a1\u03cc\u03bb\u03bf\u03c2',
                                     '\u03a3\u03c5\u03bc\u03b2\u03cc\u03bb\u03b1\u03b9\u03bf',
                                     'Email',
                                     '\u0397\u03bc\u03b5\u03c1\u03ae\u03c3\u03b9\u03bf'],
                    'equip_section': '\u0395\u03be\u03bf\u03c0\u03bb\u03b9\u03c3\u03bc\u03cc\u03c2',
                    'equip_headers': ['\u039a\u03c9\u03b4\u03b9\u03ba\u03cc\u03c2', '\u038c\u03bd\u03bf\u03bc\u03b1',
                                      '\u039a\u03b1\u03c4\u03b7\u03b3\u03bf\u03c1\u03af\u03b1',
                                      '\u039c\u03ac\u03c1\u03ba\u03b1',
                                      '\u039c\u03bf\u03bd\u03c4\u03ad\u03bb\u03bf',
                                      '\u039a\u03b1\u03c4\u03ac\u03c3\u03c4\u03b1\u03c3\u03b7'],
                    'statistics': '\u03a3\u03c4\u03b1\u03c4\u03b9\u03c3\u03c4\u03b9\u03ba\u03ac',
                    'total_personnel': '\u03a3\u03cd\u03bd\u03bf\u03bb\u03bf \u03a0\u03c1\u03bf\u03c3\u03c9\u03c0.',
                    'total_equipment': '\u03a3\u03cd\u03bd\u03bf\u03bb\u03bf \u0395\u03be\u03bf\u03c0\u03bb.',
                    'budget_variance': '\u0391\u03c0\u03cc\u03ba\u03bb\u03b9\u03c3\u03b7',
                    'budget_chart': '\u03a0\u03c1\u03bf\u03cb\u03c0\u03bf\u03bb\u03bf\u03b3\u03b9\u03c3\u03bc\u03cc\u03c2 \u03b1\u03bd\u03ac \u03ba\u03b1\u03c4\u03b7\u03b3\u03bf\u03c1\u03af\u03b1',
                    'page': '\u03a3\u03b5\u03bb\u03af\u03b4\u03b1',
                    'footer': 'pyArchInit - \u0394\u03b9\u03b1\u03c7\u03b5\u03af\u03c1\u03b9\u03c3\u03b7 \u0391\u03c1\u03c7\u03b1\u03b9\u03bf\u03bb\u03bf\u03b3\u03b9\u03ba\u03ce\u03bd \u0394\u03b5\u03b4\u03bf\u03bc\u03ad\u03bd\u03c9\u03bd',
                    'no_data': '\u0394\u03b5\u03bd \u03c5\u03c0\u03ac\u03c1\u03c7\u03bf\u03c5\u03bd \u03b4\u03b9\u03b1\u03b8\u03ad\u03c3\u03b9\u03bc\u03b1 \u03b4\u03b5\u03b4\u03bf\u03bc\u03ad\u03bd\u03b1',
                    'computo_section': '\u0395\u03c0\u03b9\u03bc\u03b5\u03c4\u03c1\u03ae\u03c3\u03b5\u03b9\u03c2',
                    'computo_headers': ['\u0397\u03bc/\u03bd\u03af\u03b1', '\u03a4\u03cd\u03c0\u03bf\u03c2', '\u038c\u03bd\u03bf\u03bc\u03b1',
                                         '\u0395\u03bc\u03b2\u03b1\u03b4\u03cc (m\u00b2)',
                                         '\u038c\u03b3\u03ba\u03bf\u03c2 (m\u00b3)',
                                         'Min', 'Max', '\u03a3\u03b7\u03bc.'],
                    'total_area': '\u03a3\u03c5\u03bd\u03bf\u03bb\u03b9\u03ba\u03cc \u03b5\u03bc\u03b2\u03b1\u03b4\u03cc',
                    'total_volume': '\u03a3\u03c5\u03bd\u03bf\u03bb\u03b9\u03ba\u03cc\u03c2 \u03cc\u03b3\u03ba\u03bf\u03c2',
                    'cut_volume': '\u0395\u03ba\u03c3\u03ba\u03b1\u03c6\u03ae',
                    'fill_volume': '\u03a0\u03bb\u03ae\u03c1\u03c9\u03c3\u03b7',
                    'total_computi': 'N. \u0395\u03b3\u03b3\u03c1\u03b1\u03c6\u03ce\u03bd',
                },
                'ar': {
                    'title': '\u0644\u0648\u062d\u0629 \u0627\u0644\u0642\u064a\u0627\u062f\u0629',
                    'subtitle': '\u0645\u0644\u062e\u0635 \u062a\u0634\u063a\u064a\u0644\u064a \u0644\u0644\u0645\u0648\u0642\u0639',
                    'site': '\u0627\u0644\u0645\u0648\u0642\u0639', 'year': '\u0627\u0644\u0633\u0646\u0629',
                    'generated': '\u062a\u0645 \u0627\u0644\u0625\u0646\u0634\u0627\u0621 \u0641\u064a',
                    'budget_section': '\u0645\u0644\u062e\u0635 \u0627\u0644\u0645\u064a\u0632\u0627\u0646\u064a\u0629',
                    'budget_headers': ['\u0627\u0644\u0641\u0626\u0629', '\u0627\u0644\u0648\u0635\u0641',
                                        '\u0627\u0644\u0645\u062e\u0637\u0637',
                                        '\u0627\u0644\u0641\u0639\u0644\u064a',
                                        '\u0627\u0644\u0641\u0631\u0642'],
                    'total': '\u0627\u0644\u0625\u062c\u0645\u0627\u0644\u064a',
                    'budgeted': '\u0627\u0644\u0645\u062e\u0637\u0637',
                    'actual': '\u0627\u0644\u0641\u0639\u0644\u064a',
                    'personnel_section': '\u0627\u0644\u0645\u0648\u0638\u0641\u0648\u0646',
                    'pers_headers': ['\u0627\u0644\u0627\u0633\u0645', '\u0627\u0644\u0644\u0642\u0628',
                                     '\u0627\u0644\u062f\u0648\u0631',
                                     '\u0627\u0644\u0639\u0642\u062f',
                                     '\u0627\u0644\u0628\u0631\u064a\u062f',
                                     '\u0627\u0644\u0623\u062c\u0631 \u0627\u0644\u064a\u0648\u0645\u064a'],
                    'equip_section': '\u0645\u062e\u0632\u0648\u0646 \u0627\u0644\u0645\u0639\u062f\u0627\u062a',
                    'equip_headers': ['\u0627\u0644\u0631\u0645\u0632', '\u0627\u0644\u0627\u0633\u0645',
                                      '\u0627\u0644\u0641\u0626\u0629',
                                      '\u0627\u0644\u0645\u0627\u0631\u0643\u0629',
                                      '\u0627\u0644\u0646\u0645\u0648\u0630\u062c',
                                      '\u0627\u0644\u062d\u0627\u0644\u0629'],
                    'statistics': '\u0625\u062d\u0635\u0627\u0626\u064a\u0627\u062a',
                    'total_personnel': '\u0625\u062c\u0645\u0627\u0644\u064a \u0627\u0644\u0645\u0648\u0638\u0641\u064a\u0646',
                    'total_equipment': '\u0625\u062c\u0645\u0627\u0644\u064a \u0627\u0644\u0645\u0639\u062f\u0627\u062a',
                    'budget_variance': '\u0627\u0646\u062d\u0631\u0627\u0641 \u0627\u0644\u0645\u064a\u0632\u0627\u0646\u064a\u0629',
                    'budget_chart': '\u0627\u0644\u0645\u064a\u0632\u0627\u0646\u064a\u0629 \u062d\u0633\u0628 \u0627\u0644\u0641\u0626\u0629',
                    'page': '\u0635\u0641\u062d\u0629',
                    'footer': 'pyArchInit',
                    'no_data': '\u0644\u0627 \u062a\u0648\u062c\u062f \u0628\u064a\u0627\u0646\u0627\u062a',
                    'computo_section': '\u062d\u0633\u0627\u0628 \u0627\u0644\u0643\u0645\u064a\u0627\u062a',
                    'computo_headers': ['\u0627\u0644\u062a\u0627\u0631\u064a\u062e', '\u0627\u0644\u0646\u0648\u0639',
                                         '\u0627\u0644\u0627\u0633\u0645',
                                         '\u0627\u0644\u0645\u0633\u0627\u062d\u0629 (m\u00b2)',
                                         '\u0627\u0644\u062d\u062c\u0645 (m\u00b3)',
                                         'Min', 'Max', '\u0645\u0644\u0627\u062d\u0638\u0627\u062a'],
                    'total_area': '\u0625\u062c\u0645\u0627\u0644\u064a \u0627\u0644\u0645\u0633\u0627\u062d\u0629',
                    'total_volume': '\u0625\u062c\u0645\u0627\u0644\u064a \u0627\u0644\u062d\u062c\u0645',
                    'cut_volume': '\u0627\u0644\u062d\u0641\u0631',
                    'fill_volume': '\u0627\u0644\u0631\u062f\u0645',
                    'total_computi': '\u0639\u062f\u062f \u0627\u0644\u0633\u062c\u0644\u0627\u062a',
                },
            }
            tr = i18n.get(lang, i18n['en'])

            # --- Styles ---
            styles = getSampleStyleSheet()
            style_title = ParagraphStyle('DashTitle', parent=styles['Title'],
                                         fontName=F_BOLD, fontSize=22,
                                         textColor=CLR_HEADER, spaceAfter=1 * mm)
            style_subtitle = ParagraphStyle('DashSubtitle', parent=styles['Normal'],
                                            fontName=F_REG, fontSize=11,
                                            textColor=colors.HexColor('#546e7a'), spaceAfter=1 * mm)
            style_section = ParagraphStyle('DashSection', parent=styles['Heading2'],
                                           fontName=F_BOLD, fontSize=14,
                                           textColor=CLR_HEADER, spaceBefore=6 * mm, spaceAfter=3 * mm)
            style_cell = ParagraphStyle('DCell', fontName=F_REG, fontSize=8,
                                        leading=10, alignment=TA_LEFT)
            style_cell_right = ParagraphStyle('DCellR', fontName=F_REG, fontSize=8,
                                              leading=10, alignment=TA_RIGHT)
            style_cell_center = ParagraphStyle('DCellC', fontName=F_REG, fontSize=8,
                                               leading=10, alignment=TA_CENTER)
            style_cell_bold = ParagraphStyle('DCellB', fontName=F_BOLD, fontSize=8,
                                             leading=10, alignment=TA_LEFT)
            style_cell_bold_right = ParagraphStyle('DCellBR', fontName=F_BOLD, fontSize=8,
                                                    leading=10, alignment=TA_RIGHT)
            style_header_cell = ParagraphStyle('DHdrCell', fontName=F_BOLD, fontSize=8.5,
                                               leading=11, textColor=CLR_TEXT_LIGHT, alignment=TA_CENTER)
            style_stat_label = ParagraphStyle('StatLbl', fontName=F_BOLD, fontSize=10,
                                              textColor=CLR_HEADER)
            style_stat_val = ParagraphStyle('StatVal', fontName=F_BOLD, fontSize=12,
                                            textColor=colors.HexColor('#0d47a1'), alignment=TA_RIGHT)

            def make_table_style():
                """Return standard professional table style commands."""
                return [
                    ('BACKGROUND', (0, 0), (-1, 0), CLR_HEADER),
                    ('TEXTCOLOR', (0, 0), (-1, 0), CLR_TEXT_LIGHT),
                    ('FONTNAME', (0, 0), (-1, 0), F_BOLD),
                    ('FONTSIZE', (0, 0), (-1, 0), 8.5),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
                    ('TOPPADDING', (0, 0), (-1, 0), 5),
                    ('FONTNAME', (0, 1), (-1, -1), F_REG),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('TOPPADDING', (0, 1), (-1, -1), 3),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 3),
                    ('LEFTPADDING', (0, 0), (-1, -1), 4),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, CLR_ROW_ALT]),
                    ('GRID', (0, 0), (-1, 0), 0.5, CLR_HEADER),
                    ('LINEBELOW', (0, 0), (-1, 0), 1.5, CLR_SECTION_LINE),
                    ('INNERGRID', (0, 1), (-1, -1), 0.25, CLR_BORDER),
                    ('BOX', (0, 0), (-1, -1), 0.75, CLR_HEADER),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]

            # --- Header/Footer ---
            def _trim(text, max_chars):
                if len(text) > max_chars:
                    return text[:max_chars - 1] + '\u2026'
                return text

            def header_footer(canvas, doc):
                canvas.saveState()

                # Header bar
                canvas.setFillColor(CLR_HEADER)
                canvas.rect(0, page_h - 16 * mm, page_w, 16 * mm, fill=1, stroke=0)
                canvas.setFillColor(CLR_SECTION_LINE)
                canvas.rect(0, page_h - 17 * mm, page_w, 1 * mm, fill=1, stroke=0)

                canvas.setFillColor(CLR_TEXT_LIGHT)
                canvas.setFont(F_BOLD, 13)
                canvas.drawString(12 * mm, page_h - 11 * mm, "pyArchInit")

                canvas.setFont(F_REG, 9)
                middle_text = (
                    f"{tr['site']}: {_trim(str(sito), 32)}"
                    f"   \u2022   {tr['year']}: {anno}"
                )
                canvas.drawString(48 * mm, page_h - 11 * mm, middle_text)

                gen_date = datetime.now().strftime('%Y-%m-%d %H:%M')
                canvas.drawRightString(page_w - 12 * mm, page_h - 11 * mm,
                                       f"{tr['generated']}: {gen_date}")

                # Footer
                canvas.setFillColor(CLR_HEADER)
                canvas.rect(0, 0, page_w, 10 * mm, fill=1, stroke=0)
                canvas.setFont(F_REG, 7)
                canvas.setFillColor(CLR_TEXT_LIGHT)
                canvas.drawString(12 * mm, 3.5 * mm, tr['footer'])
                canvas.drawRightString(page_w - 12 * mm, 3.5 * mm,
                                       f"{tr['page']} {canvas.getPageNumber()}")
                canvas.restoreState()

            # --- Build document ---
            doc = SimpleDocTemplate(
                file_path, pagesize=A4,
                topMargin=22 * mm, bottomMargin=15 * mm,
                leftMargin=12 * mm, rightMargin=12 * mm,
            )
            usable_w = page_w - 24 * mm
            elements = []

            # ========== TITLE PAGE ==========
            # Cleaner cover: card box containing title, site, year, subtitle,
            # date. No overlapping HRFlowable/underline artifacts.
            elements.append(Spacer(1, 45 * mm))

            cover_title = Paragraph(tr['title'], ParagraphStyle(
                'BigTitle', fontName=F_BOLD, fontSize=30,
                textColor=CLR_HEADER, alignment=TA_CENTER,
                leading=36, spaceAfter=2 * mm))
            cover_line = HRFlowable(width="50%", thickness=1.5,
                                    color=CLR_SECTION_LINE,
                                    spaceBefore=3 * mm, spaceAfter=6 * mm,
                                    hAlign='CENTER')
            cover_site = Paragraph(f"{tr['site']}: <b>{sito}</b>", ParagraphStyle(
                'TitleSite', fontName=F_REG, fontSize=16,
                textColor=colors.HexColor('#37474f'),
                alignment=TA_CENTER, spaceAfter=2 * mm))
            cover_year = Paragraph(f"{tr['year']}: <b>{anno}</b>", ParagraphStyle(
                'TitleYear', fontName=F_REG, fontSize=14,
                textColor=colors.HexColor('#546e7a'),
                alignment=TA_CENTER, spaceAfter=6 * mm))
            cover_sub = Paragraph(tr['subtitle'], ParagraphStyle(
                'TitleSub', fontName=F_ITAL, fontSize=11,
                textColor=colors.HexColor('#78909c'),
                alignment=TA_CENTER, spaceAfter=4 * mm))

            cover_tbl = Table(
                [[cover_title], [cover_line], [cover_site],
                 [cover_year], [cover_sub]],
                colWidths=[usable_w - 40 * mm],
                hAlign='CENTER',
            )
            cover_tbl.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f5f7fa')),
                ('BOX', (0, 0), (-1, -1), 1.5, CLR_SECTION_LINE),
                ('TOPPADDING', (0, 0), (-1, -1), 10 * mm),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10 * mm),
                ('LEFTPADDING', (0, 0), (-1, -1), 10 * mm),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10 * mm),
            ]))
            elements.append(cover_tbl)

            gen_date = datetime.now().strftime('%Y-%m-%d %H:%M')
            elements.append(Spacer(1, 14 * mm))
            elements.append(Paragraph(f"{tr['generated']}: {gen_date}", ParagraphStyle(
                'TitleDate', fontName=F_REG, fontSize=10,
                textColor=colors.HexColor('#90a4ae'), alignment=TA_CENTER)))

            elements.append(PageBreak())

            # ========== BUDGET SECTION ==========
            budget_recs = []
            tot_prev = 0.0
            tot_eff = 0.0
            try:
                search_dict = {'sito': "'" + sito + "'"}
                if anno:
                    search_dict['anno'] = anno
                budget_recs = self.DB_MANAGER.query_bool(search_dict, 'BUDGET')
                tot_prev = sum(float(r.importo_previsto or 0) for r in budget_recs)
                tot_eff = sum(float(r.importo_effettivo or 0) for r in budget_recs)
            except Exception:
                pass

            elements.append(Paragraph(tr['budget_section'], style_section))

            if budget_recs:
                # Budget table
                bhdrs = tr['budget_headers']
                bheader_row = [Paragraph(h, style_header_cell) for h in bhdrs]
                bdata = [bheader_row]
                for r in budget_recs:
                    prev = float(r.importo_previsto or 0)
                    eff = float(r.importo_effettivo or 0)
                    diff = prev - eff
                    diff_color = '#2e7d32' if diff >= 0 else '#c62828'
                    bdata.append([
                        Paragraph(str(r.categoria or ''), style_cell),
                        Paragraph(str(r.descrizione or ''), style_cell),
                        Paragraph(f"\u20ac {prev:,.2f}", style_cell_right),
                        Paragraph(f"\u20ac {eff:,.2f}", style_cell_right),
                        Paragraph(f'<font color="{diff_color}">\u20ac {diff:,.2f}</font>', style_cell_right),
                    ])
                # Total row
                total_diff = tot_prev - tot_eff
                diff_color = '#2e7d32' if total_diff >= 0 else '#c62828'
                bdata.append([
                    Paragraph(f"<b>{tr['total']}</b>", style_cell_bold),
                    Paragraph('', style_cell),
                    Paragraph(f"<b>\u20ac {tot_prev:,.2f}</b>", style_cell_bold_right),
                    Paragraph(f"<b>\u20ac {tot_eff:,.2f}</b>", style_cell_bold_right),
                    Paragraph(f'<b><font color="{diff_color}">\u20ac {total_diff:,.2f}</font></b>', style_cell_bold_right),
                ])

                bcol_widths = [30 * mm, 55 * mm, 30 * mm, 30 * mm, 28 * mm]
                btbl = Table(bdata, colWidths=bcol_widths, repeatRows=1)
                ts = make_table_style()
                ts.extend([
                    ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#c5cae9')),
                    ('FONTNAME', (0, -1), (-1, -1), F_BOLD),
                ])
                btbl.setStyle(TableStyle(ts))
                elements.append(btbl)

                # ========== BUDGET BAR CHART ==========
                elements.append(Spacer(1, 5 * mm))
                elements.append(Paragraph(tr['budget_chart'], ParagraphStyle(
                    'ChartTitle', fontName=F_BOLD, fontSize=11,
                    textColor=CLR_HEADER, spaceBefore=3 * mm, spaceAfter=3 * mm)))

                # Build bar chart using ReportLab Drawing
                categories = []
                budgeted_vals = []
                actual_vals = []
                for r in budget_recs:
                    cat_name = str(r.categoria or '?')
                    if len(cat_name) > 15:
                        cat_name = cat_name[:14] + '..'
                    categories.append(cat_name)
                    budgeted_vals.append(float(r.importo_previsto or 0))
                    actual_vals.append(float(r.importo_effettivo or 0))

                num_cats = len(categories)
                if num_cats > 0:
                    chart_w = float(usable_w)
                    bar_area_w = chart_w - 25 * mm  # leave space for labels
                    chart_h = max(80, num_cats * 22 + 40)
                    drawing = Drawing(chart_w, chart_h)

                    max_val = max(max(budgeted_vals, default=1), max(actual_vals, default=1), 1)
                    bar_height = 7
                    group_spacing = 22
                    x_offset = 25 * mm
                    y_start = chart_h - 25

                    # Legend
                    drawing.add(Rect(x_offset, chart_h - 12, 10, 6,
                                     fillColor=CLR_BUDGET, strokeColor=None))
                    drawing.add(String(x_offset + 13, chart_h - 11,
                                       tr['budgeted'], fontName=F_REG, fontSize=7,
                                       fillColor=colors.HexColor('#333333')))
                    drawing.add(Rect(x_offset + 55, chart_h - 12, 10, 6,
                                     fillColor=CLR_ACTUAL, strokeColor=None))
                    drawing.add(String(x_offset + 68, chart_h - 11,
                                       tr['actual'], fontName=F_REG, fontSize=7,
                                       fillColor=colors.HexColor('#333333')))

                    for i, cat in enumerate(categories):
                        y_pos = y_start - i * group_spacing

                        # Category label
                        drawing.add(String(2, y_pos - 1, cat,
                                           fontName=F_REG, fontSize=7,
                                           fillColor=colors.HexColor('#333333')))

                        # Budgeted bar
                        bw = (budgeted_vals[i] / max_val) * float(bar_area_w) if max_val else 0
                        drawing.add(Rect(x_offset, y_pos, max(bw, 1), bar_height,
                                         fillColor=CLR_BUDGET, strokeColor=None))
                        if bw > 2:
                            drawing.add(String(x_offset + bw + 2, y_pos + 1,
                                               f"\u20ac{budgeted_vals[i]:,.0f}",
                                               fontName=F_REG, fontSize=6,
                                               fillColor=CLR_BUDGET))

                        # Actual bar
                        aw = (actual_vals[i] / max_val) * float(bar_area_w) if max_val else 0
                        drawing.add(Rect(x_offset, y_pos - bar_height - 1, max(aw, 1), bar_height,
                                         fillColor=CLR_ACTUAL, strokeColor=None))
                        if aw > 2:
                            drawing.add(String(x_offset + aw + 2, y_pos - bar_height,
                                               f"\u20ac{actual_vals[i]:,.0f}",
                                               fontName=F_REG, fontSize=6,
                                               fillColor=CLR_ACTUAL))

                    elements.append(drawing)
            else:
                elements.append(Paragraph(f"<i>{tr['no_data']}</i>", style_cell))

            elements.append(Spacer(1, 4 * mm))
            elements.append(HRFlowable(width="100%", thickness=0.5, color=CLR_BORDER,
                                       spaceAfter=2 * mm))

            # ========== PERSONNEL SECTION ==========
            pers_recs = []
            try:
                search_dict = {'sito': "'" + sito + "'"}
                pers_recs = self.DB_MANAGER.query_bool(search_dict, 'PERSONALE')
            except Exception:
                pass

            elements.append(Paragraph(tr['personnel_section'], style_section))
            if pers_recs:
                phdrs = tr['pers_headers']
                pheader_row = [Paragraph(h, style_header_cell) for h in phdrs]
                pdata = [pheader_row]
                for r in pers_recs:
                    rate_str = ''
                    try:
                        if r.tariffa_giornaliera:
                            rate_str = f"\u20ac {float(r.tariffa_giornaliera):,.2f}"
                    except (ValueError, TypeError):
                        rate_str = str(r.tariffa_giornaliera) if r.tariffa_giornaliera else ''
                    pdata.append([
                        Paragraph(str(r.nome or ''), style_cell),
                        Paragraph(str(r.cognome or ''), style_cell),
                        Paragraph(str(r.ruolo or ''), style_cell_center),
                        Paragraph(str(r.tipo_contratto or ''), style_cell_center),
                        Paragraph(str(r.email or ''), style_cell),
                        Paragraph(rate_str, style_cell_right),
                    ])

                pcol_widths = [28 * mm, 32 * mm, 32 * mm, 28 * mm, 40 * mm, 22 * mm]
                ptbl = Table(pdata, colWidths=pcol_widths, repeatRows=1)
                ptbl.setStyle(TableStyle(make_table_style()))
                elements.append(ptbl)
            else:
                elements.append(Paragraph(f"<i>{tr['no_data']}</i>", style_cell))

            elements.append(Spacer(1, 4 * mm))
            elements.append(HRFlowable(width="100%", thickness=0.5, color=CLR_BORDER,
                                       spaceAfter=2 * mm))

            # ========== EQUIPMENT SECTION ==========
            equip_recs = []
            try:
                search_dict = {'sito': "'" + sito + "'"}
                equip_recs = self.DB_MANAGER.query_bool(search_dict, 'ATTREZZATURE')
            except Exception:
                pass

            elements.append(Paragraph(tr['equip_section'], style_section))
            if equip_recs:
                ehdrs = tr['equip_headers']
                eheader_row = [Paragraph(h, style_header_cell) for h in ehdrs]
                edata = [eheader_row]
                for r in equip_recs:
                    # Color-code status
                    status_str = str(r.stato or '')
                    status_lower = status_str.lower()
                    if status_lower in ('in uso', 'in use', 'im einsatz', 'en uso', 'en utilisation'):
                        status_str = f'<font color="#2e7d32">{status_str}</font>'
                    elif status_lower in ('manutenzione', 'maintenance', 'wartung', 'mantenimiento', 'entretien'):
                        status_str = f'<font color="#e65100">{status_str}</font>'
                    elif status_lower in ('dismesso', 'decommissioned', 'ausgemustert', 'dado de baja', 'hors service'):
                        status_str = f'<font color="#c62828">{status_str}</font>'

                    edata.append([
                        Paragraph(str(r.codice_inventario or ''), style_cell_center),
                        Paragraph(str(r.nome or ''), style_cell),
                        Paragraph(str(r.categoria or ''), style_cell_center),
                        Paragraph(str(r.marca or ''), style_cell),
                        Paragraph(str(r.modello or ''), style_cell),
                        Paragraph(status_str, style_cell_center),
                    ])

                ecol_widths = [25 * mm, 38 * mm, 30 * mm, 28 * mm, 30 * mm, 28 * mm]
                etbl = Table(edata, colWidths=ecol_widths, repeatRows=1)
                etbl.setStyle(TableStyle(make_table_style()))
                elements.append(etbl)
            else:
                elements.append(Paragraph(f"<i>{tr['no_data']}</i>", style_cell))

            elements.append(Spacer(1, 4 * mm))
            elements.append(HRFlowable(width="100%", thickness=0.5, color=CLR_BORDER,
                                       spaceAfter=2 * mm))

            # ========== COMPUTO METRICO SECTION ==========
            computi_recs = []
            try:
                search_dict = {'sito': "'" + sito + "'"}
                computi_recs = self.DB_MANAGER.query_bool(search_dict, 'COMPUTO_METRICO')
            except Exception:
                pass

            elements.append(Paragraph(tr['computo_section'], style_section))

            tot_area_computi = 0.0
            tot_volume_computi = 0.0
            tot_cut_computi = 0.0
            tot_fill_computi = 0.0

            if computi_recs:
                chdrs = tr['computo_headers']
                cheader_row = [Paragraph(h, style_header_cell) for h in chdrs]
                cdata = [cheader_row]
                for r in computi_recs:
                    area_v = float(r.area_mq or 0)
                    vol_v = float(r.volume_mc or 0)
                    tot_area_computi += area_v
                    tot_volume_computi += vol_v
                    # tipo_calcolo 'differenza_dem' => treat as cut
                    if (r.tipo_calcolo or '') == 'differenza_dem':
                        tot_cut_computi += vol_v
                    else:
                        tot_fill_computi += vol_v
                    q_min_str = (f"{float(r.quota_min):.2f}" if r.quota_min not in (None, '')
                                 else '\u2014')
                    q_max_str = (f"{float(r.quota_max):.2f}" if r.quota_max not in (None, '')
                                 else '\u2014')
                    cdata.append([
                        Paragraph(str(r.data_calcolo or ''), style_cell_center),
                        Paragraph(str(r.tipo_calcolo or ''), style_cell_center),
                        Paragraph(str(r.nome_calcolo or ''), style_cell),
                        Paragraph(f"{area_v:,.2f}", style_cell_right),
                        Paragraph(f"{vol_v:,.2f}", style_cell_right),
                        Paragraph(q_min_str, style_cell_right),
                        Paragraph(q_max_str, style_cell_right),
                        Paragraph(str(r.note or ''), style_cell),
                    ])

                # Totals row
                cdata.append([
                    Paragraph(f"<b>{tr['total']}</b>", style_cell_bold),
                    Paragraph('', style_cell),
                    Paragraph('', style_cell),
                    Paragraph(f"<b>{tot_area_computi:,.2f}</b>", style_cell_bold_right),
                    Paragraph(f"<b>{tot_volume_computi:,.2f}</b>", style_cell_bold_right),
                    Paragraph('', style_cell),
                    Paragraph('', style_cell),
                    Paragraph('', style_cell),
                ])

                ccol_widths = [20 * mm, 24 * mm, 28 * mm, 22 * mm, 22 * mm,
                               17 * mm, 17 * mm, 21 * mm]
                ctbl = Table(cdata, colWidths=ccol_widths, repeatRows=1)
                cts = make_table_style()
                cts.extend([
                    ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#c5cae9')),
                    ('FONTNAME', (0, -1), (-1, -1), F_BOLD),
                ])
                ctbl.setStyle(TableStyle(cts))
                elements.append(ctbl)
            else:
                elements.append(Paragraph(f"<i>{tr['no_data']}</i>", style_cell))

            # ========== COST ANALYSIS SECTION ==========
            # Per-site unit cost and production rate come from QgsSettings
            # and apply uniformly to every COMPUTO_METRICO record (first
            # implementation — a per-record override could be added later
            # via the COMPUTO_METRICO table).
            try:
                cost_per_m3 = float(getattr(
                    self, 'spinBox_cost_per_m3', None).value()) \
                    if hasattr(self, 'spinBox_cost_per_m3') else 0.0
            except Exception:
                cost_per_m3 = 0.0
            try:
                prod_m3_day = float(getattr(
                    self, 'spinBox_prod_m3_day', None).value()) \
                    if hasattr(self, 'spinBox_prod_m3_day') else 0.0
            except Exception:
                prod_m3_day = 0.0

            # i18n fall-backs for the cost section - inline so we don't
            # have to touch every language dict
            cost_i18n = {
                'it': {
                    'sec': 'Analisi Costi', 'cost_m3': 'Costo unitario',
                    'prod': 'Produttivit\u00e0', 'cost_tot': 'Costo totale',
                    'days': 'Giorni stimati', 'cost_day': 'Costo giornaliero',
                    'record_headers': ['Data', 'Tipo', 'Volume (m\u00b3)',
                                        'Costo (\u20ac)', 'Giorni',
                                        'Costo/giorno (\u20ac)'],
                },
                'en': {
                    'sec': 'Cost Analysis', 'cost_m3': 'Unit cost',
                    'prod': 'Production rate', 'cost_tot': 'Total cost',
                    'days': 'Estimated days', 'cost_day': 'Daily cost',
                    'record_headers': ['Date', 'Type', 'Volume (m\u00b3)',
                                        'Cost (\u20ac)', 'Days',
                                        'Cost/day (\u20ac)'],
                },
                'de': {
                    'sec': 'Kostenanalyse', 'cost_m3': 'Einheitskosten',
                    'prod': 'Leistung', 'cost_tot': 'Gesamtkosten',
                    'days': 'Gesch\u00e4tzte Tage',
                    'cost_day': 'Tageskosten',
                    'record_headers': ['Datum', 'Typ', 'Volumen (m\u00b3)',
                                        'Kosten (\u20ac)', 'Tage',
                                        'Kosten/Tag (\u20ac)'],
                },
                'es': {
                    'sec': 'An\u00e1lisis de Costes', 'cost_m3': 'Coste unitario',
                    'prod': 'Productividad', 'cost_tot': 'Coste total',
                    'days': 'D\u00edas estimados', 'cost_day': 'Coste diario',
                    'record_headers': ['Fecha', 'Tipo', 'Volumen (m\u00b3)',
                                        'Coste (\u20ac)', 'D\u00edas',
                                        'Coste/d\u00eda (\u20ac)'],
                },
                'fr': {
                    'sec': 'Analyse des co\u00fbts', 'cost_m3': 'Co\u00fbt unitaire',
                    'prod': 'Productivit\u00e9', 'cost_tot': 'Co\u00fbt total',
                    'days': 'Jours estim\u00e9s', 'cost_day': 'Co\u00fbt journalier',
                    'record_headers': ['Date', 'Type', 'Volume (m\u00b3)',
                                        'Co\u00fbt (\u20ac)', 'Jours',
                                        'Co\u00fbt/jour (\u20ac)'],
                },
                'ro': {
                    'sec': 'Analiza costurilor', 'cost_m3': 'Cost unitar',
                    'prod': 'Productivitate', 'cost_tot': 'Cost total',
                    'days': 'Zile estimate', 'cost_day': 'Cost zilnic',
                    'record_headers': ['Data', 'Tip', 'Volum (m\u00b3)',
                                        'Cost (\u20ac)', 'Zile',
                                        'Cost/zi (\u20ac)'],
                },
                'pt': {
                    'sec': 'An\u00e1lise de custos', 'cost_m3': 'Custo unit\u00e1rio',
                    'prod': 'Produtividade', 'cost_tot': 'Custo total',
                    'days': 'Dias estimados', 'cost_day': 'Custo di\u00e1rio',
                    'record_headers': ['Data', 'Tipo', 'Volume (m\u00b3)',
                                        'Custo (\u20ac)', 'Dias',
                                        'Custo/dia (\u20ac)'],
                },
                'ca': {
                    'sec': "An\u00e0lisi de costos", 'cost_m3': 'Cost unitari',
                    'prod': 'Productivitat', 'cost_tot': 'Cost total',
                    'days': 'Dies estimats', 'cost_day': 'Cost diari',
                    'record_headers': ['Data', 'Tipus', 'Volum (m\u00b3)',
                                        'Cost (\u20ac)', 'Dies',
                                        'Cost/dia (\u20ac)'],
                },
                'el': {
                    'sec': '\u0391\u03bd\u03ac\u03bb\u03c5\u03c3\u03b7 \u039a\u03cc\u03c3\u03c4\u03bf\u03c5\u03c2',
                    'cost_m3': '\u039c\u03bf\u03bd\u03b1\u03b4\u03b9\u03b1\u03af\u03bf \u03ba\u03cc\u03c3\u03c4\u03bf\u03c2',
                    'prod': '\u03a0\u03b1\u03c1\u03b1\u03b3\u03c9\u03b3\u03b9\u03ba\u03cc\u03c4\u03b7\u03c4\u03b1',
                    'cost_tot': '\u03a3\u03c5\u03bd\u03bf\u03bb\u03b9\u03ba\u03cc \u03ba\u03cc\u03c3\u03c4\u03bf\u03c2',
                    'days': '\u0395\u03ba\u03c4\u03b9\u03bc\u03ce\u03bc\u03b5\u03bd\u03b5\u03c2 \u03b7\u03bc\u03ad\u03c1\u03b5\u03c2',
                    'cost_day': '\u0397\u03bc\u03b5\u03c1\u03ae\u03c3\u03b9\u03bf \u03ba\u03cc\u03c3\u03c4\u03bf\u03c2',
                    'record_headers': ['\u0397\u03bc/\u03bd\u03af\u03b1', '\u03a4\u03cd\u03c0\u03bf\u03c2',
                                        '\u038c\u03b3\u03ba\u03bf\u03c2 (m\u00b3)',
                                        '\u039a\u03cc\u03c3\u03c4\u03bf\u03c2 (\u20ac)',
                                        '\u0397\u03bc\u03ad\u03c1\u03b5\u03c2',
                                        '\u039a\u03cc\u03c3\u03c4\u03bf\u03c2/\u03b7\u03bc (\u20ac)'],
                },
                'ar': {
                    'sec': '\u062a\u062d\u0644\u064a\u0644 \u0627\u0644\u062a\u0643\u0627\u0644\u064a\u0641',
                    'cost_m3': '\u0627\u0644\u062a\u0643\u0644\u0641\u0629 \u0644\u0644\u0648\u062d\u062f\u0629',
                    'prod': '\u0627\u0644\u0625\u0646\u062a\u0627\u062c\u064a\u0629',
                    'cost_tot': '\u0627\u0644\u062a\u0643\u0644\u0641\u0629 \u0627\u0644\u0625\u062c\u0645\u0627\u0644\u064a\u0629',
                    'days': '\u0627\u0644\u0623\u064a\u0627\u0645',
                    'cost_day': '\u0627\u0644\u062a\u0643\u0644\u0641\u0629 \u0627\u0644\u064a\u0648\u0645\u064a\u0629',
                    'record_headers': ['\u0627\u0644\u062a\u0627\u0631\u064a\u062e', '\u0627\u0644\u0646\u0648\u0639',
                                        '\u0627\u0644\u062d\u062c\u0645 (m\u00b3)',
                                        '\u0627\u0644\u062a\u0643\u0644\u0641\u0629 (\u20ac)',
                                        '\u0623\u064a\u0627\u0645',
                                        '\u062a\u0643\u0644\u0641\u0629/\u064a\u0648\u0645 (\u20ac)'],
                },
            }.get(lang, None)
            if cost_i18n is None:
                cost_i18n = {
                    'sec': 'Cost Analysis', 'cost_m3': 'Unit cost',
                    'prod': 'Production rate', 'cost_tot': 'Total cost',
                    'days': 'Estimated days', 'cost_day': 'Daily cost',
                    'record_headers': ['Date', 'Type', 'Volume (m\u00b3)',
                                        'Cost (\u20ac)', 'Days',
                                        'Cost/day (\u20ac)'],
                }

            elements.append(Spacer(1, 4 * mm))
            elements.append(HRFlowable(width="100%", thickness=0.5,
                                        color=CLR_BORDER, spaceAfter=2 * mm))
            elements.append(Paragraph(cost_i18n['sec'], style_section))

            # Parameter card: unit cost + production rate
            param_data = [[
                Paragraph(f"<b>{cost_i18n['cost_m3']}</b>", style_stat_label),
                Paragraph(f"\u20ac {cost_per_m3:,.2f} / m\u00b3", style_stat_val),
                Paragraph(f"<b>{cost_i18n['prod']}</b>", style_stat_label),
                Paragraph(f"{prod_m3_day:,.2f} m\u00b3/day", style_stat_val),
            ]]
            param_tbl = Table(param_data,
                              colWidths=[38 * mm, 40 * mm, 38 * mm, 40 * mm])
            param_tbl.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fff3e0')),
                ('BOX', (0, 0), (-1, -1), 0.8, colors.HexColor('#e65100')),
                ('INNERGRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#ffcc80')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(param_tbl)
            elements.append(Spacer(1, 3 * mm))

            # Per-record breakdown table
            total_cost_all = 0.0
            total_days_all = 0.0
            if computi_recs and cost_per_m3 > 0:
                chdrs_cost = cost_i18n['record_headers']
                hrow = [Paragraph(h, style_header_cell) for h in chdrs_cost]
                cdata_cost = [hrow]
                for r in computi_recs:
                    vol_v = float(r.volume_mc or 0)
                    rec_cost = vol_v * cost_per_m3
                    rec_days = (vol_v / prod_m3_day) if prod_m3_day > 0 else 0.0
                    rec_daily = (cost_per_m3 * prod_m3_day) if prod_m3_day > 0 else 0.0
                    total_cost_all += rec_cost
                    total_days_all += rec_days
                    cdata_cost.append([
                        Paragraph(str(r.data_calcolo or ''), style_cell_center),
                        Paragraph(str(r.tipo_calcolo or ''), style_cell_center),
                        Paragraph(f"{vol_v:,.2f}", style_cell_right),
                        Paragraph(f"\u20ac {rec_cost:,.2f}", style_cell_right),
                        Paragraph(f"{rec_days:,.2f}", style_cell_right),
                        Paragraph(f"\u20ac {rec_daily:,.2f}", style_cell_right),
                    ])
                # Totals row
                total_daily_all = (cost_per_m3 * prod_m3_day) if prod_m3_day > 0 else 0.0
                cdata_cost.append([
                    Paragraph(f"<b>{tr['total']}</b>", style_cell_bold),
                    Paragraph('', style_cell),
                    Paragraph(f"<b>{tot_volume_computi:,.2f}</b>",
                              style_cell_bold_right),
                    Paragraph(f"<b>\u20ac {total_cost_all:,.2f}</b>",
                              style_cell_bold_right),
                    Paragraph(f"<b>{total_days_all:,.2f}</b>",
                              style_cell_bold_right),
                    Paragraph(f"<b>\u20ac {total_daily_all:,.2f}</b>",
                              style_cell_bold_right),
                ])
                cost_col_widths = [24 * mm, 28 * mm, 26 * mm,
                                    28 * mm, 22 * mm, 28 * mm]
                cost_tbl = Table(cdata_cost, colWidths=cost_col_widths,
                                  repeatRows=1)
                cost_ts = make_table_style()
                cost_ts.extend([
                    ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#ffe0b2')),
                    ('FONTNAME', (0, -1), (-1, -1), F_BOLD),
                ])
                cost_tbl.setStyle(TableStyle(cost_ts))
                elements.append(cost_tbl)
            else:
                elements.append(Paragraph(
                    f"<i>{tr['no_data']}</i>", style_cell))

            # ========== SUMMARY STATISTICS ==========
            elements.append(Spacer(1, 6 * mm))
            elements.append(Paragraph(tr['statistics'], style_section))

            variance = tot_prev - tot_eff
            var_color = '#2e7d32' if variance >= 0 else '#c62828'

            stat_data = [
                [Paragraph(tr['total_personnel'], style_stat_label),
                 Paragraph(str(len(pers_recs)), style_stat_val),
                 Paragraph(tr['total_equipment'], style_stat_label),
                 Paragraph(str(len(equip_recs)), style_stat_val)],
                [Paragraph(tr['budget_headers'][2], style_stat_label),
                 Paragraph(f"\u20ac {tot_prev:,.2f}", style_stat_val),
                 Paragraph(tr['budget_headers'][3], style_stat_label),
                 Paragraph(f"\u20ac {tot_eff:,.2f}", style_stat_val)],
                [Paragraph(tr['budget_variance'], style_stat_label),
                 Paragraph(f'<font color="{var_color}">\u20ac {variance:,.2f}</font>',
                           ParagraphStyle('VarVal', fontName=F_BOLD, fontSize=12,
                                          textColor=colors.HexColor(var_color), alignment=TA_RIGHT)),
                 Paragraph(tr['total_computi'], style_stat_label),
                 Paragraph(str(len(computi_recs)), style_stat_val)],
                [Paragraph(tr['total_area'], style_stat_label),
                 Paragraph(f"{tot_area_computi:,.2f} m\u00b2", style_stat_val),
                 Paragraph(tr['total_volume'], style_stat_label),
                 Paragraph(f"{tot_volume_computi:,.2f} m\u00b3", style_stat_val)],
                [Paragraph(tr['cut_volume'], style_stat_label),
                 Paragraph(f"{tot_cut_computi:,.2f} m\u00b3", style_stat_val),
                 Paragraph(tr['fill_volume'], style_stat_label),
                 Paragraph(f"{tot_fill_computi:,.2f} m\u00b3", style_stat_val)],
                [Paragraph(cost_i18n['cost_tot'], style_stat_label),
                 Paragraph(f"\u20ac {total_cost_all:,.2f}", style_stat_val),
                 Paragraph(cost_i18n['days'], style_stat_label),
                 Paragraph(f"{total_days_all:,.2f}", style_stat_val)],
            ]

            stat_col_widths = [42 * mm, 35 * mm, 42 * mm, 35 * mm]
            stat_tbl = Table(stat_data, colWidths=stat_col_widths)
            stat_tbl.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), CLR_SUMMARY_BG),
                ('BOX', (0, 0), (-1, -1), 1, CLR_HEADER),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, CLR_BORDER),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                # Highlight computo-related rows (indices 3 and 4: area/vol + cut/fill)
                ('BACKGROUND', (0, 3), (-1, 4), colors.HexColor('#e8f5e9')),
            ]))
            elements.append(stat_tbl)

            # Build with header/footer
            doc.build(elements, onFirstPage=header_footer, onLaterPages=header_footer)

            QMessageBox.information(self, "OK", f"PDF exported: {file_path}", QMessageBox.StandardButton.Ok)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"PDF export failed: {str(e)}", QMessageBox.StandardButton.Ok)

    def on_pushButton_export_excel_pressed(self):
        """
        Export dashboard data to CSV including the Computo Metrico section.

        - UTF-8 with BOM ("utf-8-sig") so that Microsoft Excel and LibreOffice
          on any locale correctly decode Unicode characters (Romanian,
          Greek, Arabic, ...).
        - Semicolon separator (European Excel default, avoids confusion with
          decimal commas).
        - A top metadata block with site, year and generation timestamp.
        - Dedicated sections for Budget, Personnel, Equipment and
          Computo Metrico plus an aggregated summary.
        """
        sito = self.comboBox_sito.currentText()
        anno = self.comboBox_anno.currentText()
        if not sito:
            QMessageBox.warning(self, "Warning", "Select a site first.",
                                QMessageBox.StandardButton.Ok)
            return

        home = os.environ.get('PYARCHINIT_HOME', os.path.expanduser('~'))
        safe_sito = ''.join(c if c not in '\\/:*?"<>|' else '_' for c in sito)
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export CSV",
            os.path.join(home, f"site_dashboard_{safe_sito}_{anno}.csv"),
            "CSV (*.csv)")
        if not file_path:
            return

        # Localized section headers for the CSV (same keys as PDF)
        csv_i18n = {
            'it': {
                'meta': 'METADATI', 'site': 'Sito', 'year': 'Anno',
                'generated': 'Generato il',
                'budget': 'BUDGET', 'personnel': 'PERSONALE',
                'equipment': 'ATTREZZATURE', 'computi': 'COMPUTO METRICO',
                'costs': 'ANALISI COSTI', 'summary': 'RIEPILOGO',
                'b_hdr': ['Categoria', 'Descrizione', 'Preventivato', 'Effettivo',
                          'Fornitore', 'Fattura', 'Data'],
                'p_hdr': ['Nome', 'Cognome', 'Ruolo', 'Email', 'Telefono',
                          'Contratto', 'Tariffa giornaliera'],
                'e_hdr': ['Codice', 'Nome', 'Categoria', 'Marca', 'Modello',
                          'Stato', 'Proprieta'],
                'c_hdr': ['Data', 'Tipo', 'Nome', 'DEM pre', 'DEM post',
                          'Poligono', 'Area (m2)', 'Volume (m3)',
                          'Quota min', 'Quota max', 'Fase', 'Note'],
                'k_hdr': ['Data', 'Tipo', 'Volume (m3)', 'Costo (EUR)',
                          'Giorni', 'Costo/giorno (EUR)'],
                'k_params': ['Costo unitario (EUR/m3)',
                             'Produttivita (m3/giorno)'],
                's_lbl': ['Totale Budget Previsto', 'Totale Budget Effettivo',
                          'Variazione Budget', 'Totale Personale',
                          'Totale Attrezzature', 'Num. Computi',
                          'Area totale (m2)', 'Volume totale (m3)',
                          'Costo totale (EUR)', 'Giorni totali'],
            },
            'en': {
                'meta': 'METADATA', 'site': 'Site', 'year': 'Year',
                'generated': 'Generated on',
                'budget': 'BUDGET', 'personnel': 'PERSONNEL',
                'equipment': 'EQUIPMENT', 'computi': 'QUANTITY SURVEYING',
                'costs': 'COST ANALYSIS', 'summary': 'SUMMARY',
                'b_hdr': ['Category', 'Description', 'Budgeted', 'Actual',
                          'Supplier', 'Invoice', 'Date'],
                'p_hdr': ['First Name', 'Last Name', 'Role', 'Email', 'Phone',
                          'Contract', 'Daily Rate'],
                'e_hdr': ['Code', 'Name', 'Category', 'Brand', 'Model',
                          'Status', 'Ownership'],
                'c_hdr': ['Date', 'Type', 'Name', 'DEM pre', 'DEM post',
                          'Polygon', 'Area (m2)', 'Volume (m3)',
                          'Min elev.', 'Max elev.', 'Phase', 'Notes'],
                'k_hdr': ['Date', 'Type', 'Volume (m3)', 'Cost (EUR)',
                          'Days', 'Cost/day (EUR)'],
                'k_params': ['Unit cost (EUR/m3)',
                             'Production rate (m3/day)'],
                's_lbl': ['Total Budget Forecast', 'Total Budget Actual',
                          'Budget Variance', 'Total Personnel',
                          'Total Equipment', '# Records',
                          'Total area (m2)', 'Total volume (m3)',
                          'Total cost (EUR)', 'Total days'],
            },
        }
        tr = csv_i18n.get(self.L, csv_i18n['en'])

        def fmt_num(x, decimals=2):
            try:
                return f"{float(x or 0):.{decimals}f}"
            except (TypeError, ValueError):
                return ''

        try:
            import csv
            # utf-8-sig writes a BOM so Excel opens Unicode CSVs correctly
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)

                gen_ts = datetime.now().strftime('%Y-%m-%d %H:%M')

                # ---- Metadata block ----
                writer.writerow([f"=== {tr['meta']} ==="])
                writer.writerow([tr['site'], sito])
                writer.writerow([tr['year'], anno])
                writer.writerow([tr['generated'], gen_ts])
                writer.writerow([])

                # ---- Budget ----
                writer.writerow([f"=== {tr['budget']} ==="])
                writer.writerow(tr['b_hdr'])
                tot_prev = 0.0
                tot_eff = 0.0
                try:
                    search_dict = {'sito': "'" + sito + "'"}
                    if anno:
                        search_dict['anno'] = anno
                    budget_rows = list(self.DB_MANAGER.query_bool(search_dict, 'BUDGET'))
                    for r in budget_rows:
                        writer.writerow([
                            r.categoria or '',
                            r.descrizione or '',
                            fmt_num(r.importo_previsto),
                            fmt_num(r.importo_effettivo),
                            r.fornitore or '',
                            r.numero_fattura or '',
                            r.data_spesa or '',
                        ])
                        tot_prev += float(r.importo_previsto or 0)
                        tot_eff += float(r.importo_effettivo or 0)
                except Exception:
                    budget_rows = []

                writer.writerow([])

                # ---- Personnel ----
                writer.writerow([f"=== {tr['personnel']} ==="])
                writer.writerow(tr['p_hdr'])
                try:
                    search_dict = {'sito': "'" + sito + "'"}
                    pers_rows = list(self.DB_MANAGER.query_bool(search_dict, 'PERSONALE'))
                    for r in pers_rows:
                        writer.writerow([
                            r.nome or '', r.cognome or '', r.ruolo or '',
                            r.email or '', r.telefono or '',
                            r.tipo_contratto or '',
                            fmt_num(r.tariffa_giornaliera),
                        ])
                except Exception:
                    pers_rows = []

                writer.writerow([])

                # ---- Equipment ----
                writer.writerow([f"=== {tr['equipment']} ==="])
                writer.writerow(tr['e_hdr'])
                try:
                    search_dict = {'sito': "'" + sito + "'"}
                    equip_rows = list(self.DB_MANAGER.query_bool(search_dict, 'ATTREZZATURE'))
                    for r in equip_rows:
                        writer.writerow([
                            r.codice_inventario or '', r.nome or '',
                            r.categoria or '', r.marca or '',
                            r.modello or '', r.stato or '',
                            r.proprieta or '',
                        ])
                except Exception:
                    equip_rows = []

                writer.writerow([])

                # ---- Computo Metrico ----
                writer.writerow([f"=== {tr['computi']} ==="])
                writer.writerow(tr['c_hdr'])
                tot_area = 0.0
                tot_volume = 0.0
                try:
                    search_dict = {'sito': "'" + sito + "'"}
                    comp_rows = list(self.DB_MANAGER.query_bool(search_dict, 'COMPUTO_METRICO'))
                    for r in comp_rows:
                        tot_area += float(r.area_mq or 0)
                        tot_volume += float(r.volume_mc or 0)
                        writer.writerow([
                            r.data_calcolo or '', r.tipo_calcolo or '',
                            r.nome_calcolo or '', r.dem_pre or '',
                            r.dem_post or '', r.layer_poligono or '',
                            fmt_num(r.area_mq), fmt_num(r.volume_mc),
                            fmt_num(r.quota_min, 3), fmt_num(r.quota_max, 3),
                            r.fase_scavo or '', r.note or '',
                        ])
                except Exception:
                    comp_rows = []

                writer.writerow([])

                # ---- Cost analysis ----
                try:
                    cost_per_m3 = float(self.spinBox_cost_per_m3.value()) \
                        if hasattr(self, 'spinBox_cost_per_m3') else 0.0
                except Exception:
                    cost_per_m3 = 0.0
                try:
                    prod_m3_day = float(self.spinBox_prod_m3_day.value()) \
                        if hasattr(self, 'spinBox_prod_m3_day') else 0.0
                except Exception:
                    prod_m3_day = 0.0

                writer.writerow([f"=== {tr['costs']} ==="])
                writer.writerow([tr['k_params'][0], fmt_num(cost_per_m3)])
                writer.writerow([tr['k_params'][1], fmt_num(prod_m3_day)])
                writer.writerow([])
                writer.writerow(tr['k_hdr'])
                tot_cost_all = 0.0
                tot_days_all = 0.0
                daily = cost_per_m3 * prod_m3_day if prod_m3_day > 0 else 0.0
                for r in comp_rows:
                    vol_v = float(r.volume_mc or 0)
                    rec_cost = vol_v * cost_per_m3
                    rec_days = (vol_v / prod_m3_day) if prod_m3_day > 0 else 0.0
                    tot_cost_all += rec_cost
                    tot_days_all += rec_days
                    writer.writerow([
                        r.data_calcolo or '', r.tipo_calcolo or '',
                        fmt_num(vol_v),
                        fmt_num(rec_cost),
                        fmt_num(rec_days),
                        fmt_num(daily),
                    ])

                writer.writerow([])

                # ---- Summary ----
                writer.writerow([f"=== {tr['summary']} ==="])
                values = [
                    fmt_num(tot_prev),
                    fmt_num(tot_eff),
                    fmt_num(tot_prev - tot_eff),
                    str(len(pers_rows)),
                    str(len(equip_rows)),
                    str(len(comp_rows)),
                    fmt_num(tot_area),
                    fmt_num(tot_volume),
                    fmt_num(tot_cost_all),
                    fmt_num(tot_days_all),
                ]
                for label, value in zip(tr['s_lbl'], values):
                    writer.writerow([label, value])

            QMessageBox.information(
                self, "OK", f"Export completed: {file_path}",
                QMessageBox.StandardButton.Ok)
        except Exception as e:
            QMessageBox.warning(
                self, "Error", f"Export failed: {str(e)}",
                QMessageBox.StandardButton.Ok)


## Class end

if __name__ == "__main__":
    from qgis.PyQt.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    ui = pyarchinit_Cantiere(None)
    ui.show()
    sys.exit(app.exec())
