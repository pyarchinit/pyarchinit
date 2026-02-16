# -*- coding: utf-8 -*-
"""
MoveCost Analysis Dialog - Standalone tool for least-cost path analysis
Extracted from the Site form into an independent analysis tool.
"""
import os
import csv
import json
import shutil
import tempfile
import webbrowser
import glob as glob_module
from datetime import datetime

from qgis.PyQt.QtWidgets import (QDialog, QMessageBox, QFileDialog, QApplication)
from qgis.PyQt.QtGui import QPixmap
from qgis.PyQt.QtCore import Qt, QTimer
from qgis.core import (QgsProject, QgsApplication, QgsSettings)
from qgis.utils import iface
from qgis.PyQt.uic import loadUiType
import processing

try:
    from qgis.core import QgsMapLayerType
except ImportError:
    from qgis.core import Qgis
    class QgsMapLayerType:
        VectorLayer = Qgis.LayerType.Vector

try:
    from processing.tools.system import userFolder, mkdir
except ImportError:
    def userFolder():
        return os.path.join(QgsApplication.qgisSettingsDirPath(), 'processing')
    def mkdir(path):
        os.makedirs(path, exist_ok=True)

try:
    from qgis.core import QgsProcessingUtils
except ImportError:
    QgsProcessingUtils = None

# Import movecost layer organizer
try:
    from movecost.layer_organizer import organize_movecost_layers, MovecostLayerOrganizer
except ImportError:
    organize_movecost_layers = None
    MovecostLayerOrganizer = None

DEBUG = os.environ.get('PYARCHINIT_DEBUG', '0') == '1'

MC_LANGUAGE_CODES = {0: 'en', 1: 'it', 2: 'fr', 3: 'es', 4: 'de'}

MAIN_DIALOG_CLASS, _ = loadUiType(
    os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'Movecost.ui'))


class pyarchinit_Movecost(QDialog, MAIN_DIALOG_CLASS):
    HOME = os.environ.get('PYARCHINIT_HOME', os.path.expanduser("~"))

    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.setupUi(self)
        self.last_algorithm = ''
        self.current_plot_path = None

        # Initialize layer organizer
        self.layer_organizer = None
        if MovecostLayerOrganizer is not None:
            self.layer_organizer = MovecostLayerOrganizer(self)

        # Connect language combobox
        try:
            self.comboBox_mc_language.currentIndexChanged.connect(self.on_comboBox_mc_language_currentIndexChanged)
        except AttributeError:
            pass

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
        try:
            if self.checkBox_auto_organize.isChecked() and self.layer_organizer:
                self.layer_organizer.start_monitoring()
        except AttributeError:
            pass

    def _mc_schedule_organization(self):
        try:
            if self.checkBox_auto_organize.isChecked():
                QTimer.singleShot(3000, self._mc_delayed_organize)
        except AttributeError:
            pass

    def _mc_delayed_organize(self):
        if organize_movecost_layers is not None:
            try:
                organize_movecost_layers()
            except Exception as e:
                if DEBUG:
                    print(f"Layer organization error: {e}")

    def on_pushButton_organize_pressed(self):
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
        self._mc_update_summary()
        self._mc_load_latest_plot()

    def _mc_update_summary(self):
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
        profile_home = QgsApplication.qgisSettingsDirPath()
        system_temp = tempfile.gettempdir()
        try:
            processing_temp = QgsProcessingUtils.tempFolder()
        except Exception:
            processing_temp = None

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
        QMessageBox.information(self, "Info",
            "PDF export requires additional libraries. Use HTML export for now.",
            QMessageBox.StandardButton.Ok)

    def on_pushButton_export_html_pressed(self):
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
        profile_home = QgsApplication.qgisSettingsDirPath()
        source_profile = os.path.join(profile_home, 'python', 'plugins', 'movecost', 'rscripts')
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
        lang_code = MC_LANGUAGE_CODES.get(index, 'en')
        self._mc_update_tooltips(lang_code)

    def _mc_update_tooltips(self, lang_code):
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
