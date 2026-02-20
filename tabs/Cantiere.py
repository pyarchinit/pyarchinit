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
from qgis.PyQt.QtWidgets import QDialog, QMessageBox, QTableWidgetItem, QHeaderView
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.uic import loadUiType
from qgis.core import QgsSettings, QgsProject, QgsRasterLayer, QgsVectorLayer

from ..modules.utility.pyarchinit_theme_manager import ThemeManager
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

        # Connect signals
        self.pushButton_refresh.clicked.connect(self.refresh_dashboard)
        self.pushButton_calcola.clicked.connect(self.on_pushButton_calcola_pressed)
        self.pushButton_salva_computo.clicked.connect(self.on_pushButton_salva_computo_pressed)
        self.comboBox_sito.currentTextChanged.connect(self.refresh_dashboard)
        self.comboBox_anno.currentTextChanged.connect(self.refresh_dashboard)

        # Connect to DB
        try:
            self.on_pushButton_connect_pressed()
        except:
            pass

        # Populate combos
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
        """Populate DEM layer comboboxes from QGIS project"""
        self.comboBox_dem_pre.clear()
        self.comboBox_dem_post.clear()
        self.comboBox_dem_pre.addItem("")
        self.comboBox_dem_post.addItem("")
        for layer_id, layer in QgsProject.instance().mapLayers().items():
            if isinstance(layer, QgsRasterLayer):
                self.comboBox_dem_pre.addItem(layer.name(), layer_id)
                self.comboBox_dem_post.addItem(layer.name(), layer_id)

    def populate_vector_combos(self):
        """Populate polygon layer combobox from QGIS project"""
        self.comboBox_layer_poligono.clear()
        self.comboBox_layer_poligono.addItem("")
        for layer_id, layer in QgsProject.instance().mapLayers().items():
            if isinstance(layer, QgsVectorLayer):
                self.comboBox_layer_poligono.addItem(layer.name(), layer_id)

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
            if anno:
                search_dict['anno'] = anno
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

    def refresh_personnel_summary(self, sito):
        """Query presenze_table for today"""
        try:
            today = date.today().isoformat()
            search_dict = {'sito': "'" + sito + "'", 'data': "'" + today + "'"}
            records = self.DB_MANAGER.query_bool(search_dict, 'PRESENZE')

            presenti = sum(1 for r in records if r.tipo_giornata == 'lavorativa')
            ferie = sum(1 for r in records if r.tipo_giornata == 'ferie')
            malattia = sum(1 for r in records if r.tipo_giornata == 'malattia')

            self.label_presenti.setText(str(presenti))
            self.label_ferie.setText(str(ferie))
            self.label_malattia.setText(str(malattia))

            # Monthly totals
            month_prefix = today[:7]  # YYYY-MM
            search_month = {'sito': "'" + sito + "'"}
            all_month = self.DB_MANAGER.query_bool(search_month, 'PRESENZE')
            month_records = [r for r in all_month if r.data and r.data.startswith(month_prefix)]
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
            in_uso = sum(1 for r in records if r.stato == 'in_uso')
            manutenzione = sum(1 for r in records if r.stato == 'manutenzione')

            self.label_totali.setText(str(totali))
            self.label_in_uso.setText(str(in_uso))
            self.label_manutenzione.setText(str(manutenzione))

            # Check overdue maintenance
            today = date.today().isoformat()
            overdue = [r for r in records if r.data_prossima_manutenzione and r.data_prossima_manutenzione < today and r.stato != 'fuori_uso']
            if overdue:
                self.label_alert_manutenzione.setText(
                    f"!! {len(overdue)} scadenze manutenzione!")
                self.label_alert_manutenzione.setStyleSheet("color: red; font-weight: bold;")
            else:
                self.label_alert_manutenzione.setText("Nessuna scadenza")
                self.label_alert_manutenzione.setStyleSheet("")
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
        """Calculate area/volume from DEM layers"""
        if self.radioButton_diff_dem.isChecked():
            self.calculate_dem_difference()
        else:
            self.calculate_dem_polygon()

    def calculate_dem_difference(self):
        """Calculate volume from difference of two DEMs"""
        try:
            from qgis.analysis import QgsRasterCalculator, QgsRasterCalculatorEntry
            import tempfile

            layer_pre_id = self.comboBox_dem_pre.currentData()
            layer_post_id = self.comboBox_dem_post.currentData()

            if not layer_pre_id or not layer_post_id:
                QMessageBox.warning(self, self.MSG_BOX_TITLE, "Select both DEM layers")
                return

            layer_pre = QgsProject.instance().mapLayer(layer_pre_id)
            layer_post = QgsProject.instance().mapLayer(layer_post_id)

            if not layer_pre or not layer_post:
                QMessageBox.warning(self, self.MSG_BOX_TITLE, "Could not load DEM layers")
                return

            # Use raster calculator to compute difference
            extent = layer_pre.extent()
            pixel_x = layer_pre.rasterUnitsPerPixelX()
            pixel_y = layer_pre.rasterUnitsPerPixelY()
            n_cols = layer_pre.width()
            n_rows = layer_pre.height()

            entries = []
            entry_pre = QgsRasterCalculatorEntry()
            entry_pre.ref = 'pre@1'
            entry_pre.raster = layer_pre
            entry_pre.bandNumber = 1
            entries.append(entry_pre)

            entry_post = QgsRasterCalculatorEntry()
            entry_post.ref = 'post@1'
            entry_post.raster = layer_post
            entry_post.bandNumber = 1
            entries.append(entry_post)

            output_path = os.path.join(tempfile.gettempdir(), 'pyarchinit_dem_diff.tif')
            formula = 'pre@1 - post@1'

            calc = QgsRasterCalculator(formula, output_path, 'GTiff',
                                        extent, n_cols, n_rows, entries)
            result = calc.processCalculation()

            if result == 0:
                # Load result and compute volume
                diff_layer = QgsRasterLayer(output_path, 'DEM_diff')
                provider = diff_layer.dataProvider()
                block = provider.block(1, extent, n_cols, n_rows)

                pixel_area = abs(pixel_x * pixel_y)
                total_volume = 0.0
                total_area = 0.0

                for row_idx in range(n_rows):
                    for col_idx in range(n_cols):
                        val = block.value(row_idx, col_idx)
                        if val and not block.isNoData(row_idx, col_idx):
                            total_volume += abs(val) * pixel_area
                            if abs(val) > 0.01:
                                total_area += pixel_area

                self.label_area_mq.setText(f"{total_area:.2f} m\u00b2")
                self.label_volume_mc.setText(f"{total_volume:.2f} m\u00b3")

                # Clean up temp file
                try:
                    os.remove(output_path)
                except:
                    pass
            else:
                QMessageBox.warning(self, self.MSG_BOX_TITLE, "Raster calculation failed")
        except Exception as e:
            QMessageBox.warning(self, self.MSG_BOX_TITLE, f"Error: {str(e)}")

    def calculate_dem_polygon(self):
        """Calculate volume/area from DEM within polygon"""
        try:
            from qgis.analysis import QgsZonalStatistics

            layer_dem_id = self.comboBox_dem_pre.currentData()
            layer_poly_id = self.comboBox_layer_poligono.currentData()

            if not layer_dem_id or not layer_poly_id:
                QMessageBox.warning(self, self.MSG_BOX_TITLE, "Select DEM and polygon layers")
                return

            layer_dem = QgsProject.instance().mapLayer(layer_dem_id)
            layer_poly = QgsProject.instance().mapLayer(layer_poly_id)

            if not layer_dem or not layer_poly:
                QMessageBox.warning(self, self.MSG_BOX_TITLE, "Could not load layers")
                return

            # Run zonal statistics
            zs = QgsZonalStatistics(layer_poly, layer_dem, 'dem_',
                                     1, QgsZonalStatistics.Sum | QgsZonalStatistics.Count |
                                     QgsZonalStatistics.Min | QgsZonalStatistics.Max)
            zs.calculateStatistics(None)

            # Read results from polygon features
            total_area = 0.0
            total_volume = 0.0
            quota_min = float('inf')
            quota_max = float('-inf')

            pixel_area = layer_dem.rasterUnitsPerPixelX() * layer_dem.rasterUnitsPerPixelY()

            for feat in layer_poly.getFeatures():
                count = feat['dem_count'] if feat['dem_count'] else 0
                dem_sum = feat['dem_sum'] if feat['dem_sum'] else 0
                dem_min = feat['dem_min'] if feat['dem_min'] else 0
                dem_max = feat['dem_max'] if feat['dem_max'] else 0

                total_area += count * pixel_area
                total_volume += abs(dem_sum) * pixel_area
                if dem_min < quota_min:
                    quota_min = dem_min
                if dem_max > quota_max:
                    quota_max = dem_max

            self.label_area_mq.setText(f"{total_area:.2f} m\u00b2")
            self.label_volume_mc.setText(f"{total_volume:.2f} m\u00b3")
        except Exception as e:
            QMessageBox.warning(self, self.MSG_BOX_TITLE, f"Error: {str(e)}")

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

    def draw_budget_chart(self, records):
        """Draw matplotlib pie chart embedded in QWidget"""
        try:
            from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
            from matplotlib.figure import Figure

            # Aggregate by category
            cat_totals = {}
            for r in records:
                cat = r.categoria or 'Altro'
                cat_totals[cat] = cat_totals.get(cat, 0) + (r.importo_effettivo or 0)

            if not cat_totals or sum(cat_totals.values()) == 0:
                return

            # Clear existing chart
            layout = self.widget_chart.layout()
            if layout is None:
                from qgis.PyQt.QtWidgets import QVBoxLayout
                layout = QVBoxLayout(self.widget_chart)
                layout.setContentsMargins(0, 0, 0, 0)
            else:
                while layout.count():
                    child = layout.takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()

            fig = Figure(figsize=(4, 3), dpi=80)
            ax = fig.add_subplot(111)
            colors = ['#FF8A65', '#4FC3F7', '#81C784', '#FFD54F',
                      '#CE93D8', '#F48FB1', '#90A4AE', '#A1887F',
                      '#80CBC4', '#FFE082', '#EF9A9A']

            labels = list(cat_totals.keys())
            sizes = list(cat_totals.values())
            ax.pie(sizes, labels=labels, colors=colors[:len(labels)],
                   autopct='%1.0f%%', startangle=90, textprops={'fontsize': 7})
            ax.set_aspect('equal')
            fig.tight_layout()

            canvas = FigureCanvasQTAgg(fig)
            layout.addWidget(canvas)
            canvas.draw()
        except ImportError:
            pass  # matplotlib not available
        except Exception:
            pass


## Class end

if __name__ == "__main__":
    from qgis.PyQt.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    ui = pyarchinit_Cantiere(None)
    ui.show()
    sys.exit(app.exec())
