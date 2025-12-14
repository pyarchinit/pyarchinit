# -*- coding: utf-8 -*-
"""
SAM Stone Segmentation Dialog for PyArchInit

Provides a dialog interface for automatic stone/object segmentation
using SAM (Segment Anything Model) from archaeological orthophotos.

Author: Enzo Cocca <enzo.ccc@gmail.com>
"""

import os
import sys
import subprocess
import tempfile
import json
from datetime import date

from qgis.PyQt.QtCore import Qt, QThread, pyqtSignal, QSettings
from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QLabel, QComboBox, QLineEdit, QPushButton, QProgressBar,
    QRadioButton, QButtonGroup, QSpinBox, QMessageBox,
    QApplication, QFrame
)
from qgis.PyQt.QtGui import QIcon

from qgis.core import (
    QgsProject, QgsVectorLayer, QgsRasterLayer, QgsFeature,
    QgsGeometry, QgsField, QgsFields, QgsWkbTypes,
    QgsCoordinateReferenceSystem, QgsCoordinateTransform,
    QgsVectorFileWriter, QgsMapLayerProxyModel
)
from qgis.gui import QgsMapLayerComboBox, QgsMapCanvas

from qgis.utils import iface


class SamSegmentationWorkerThread(QThread):
    """Worker thread to run SAM segmentation in background"""
    finished = pyqtSignal(bool, str, str)  # success, message, output_file
    progress = pyqtSignal(str)  # status message

    def __init__(self, input_raster, output_gpkg, mode='auto', prompts=None, model='fast'):
        super().__init__()
        self.input_raster = input_raster
        self.output_gpkg = output_gpkg
        self.mode = mode
        self.prompts = prompts
        self.model = model

    def run(self):
        """Run SAM segmentation in subprocess"""
        try:
            venv_python = os.path.expanduser('~/pyarchinit/bin/sam_venv/bin/python')
            worker_script = os.path.expanduser('~/pyarchinit/bin/sam_segmentation_worker.py')

            if not os.path.exists(venv_python):
                self.finished.emit(False, "SAM virtual environment not found", "")
                return

            if not os.path.exists(worker_script):
                self.finished.emit(False, "SAM worker script not found", "")
                return

            # Build command
            cmd = [
                venv_python, worker_script,
                '--input', self.input_raster,
                '--output', self.output_gpkg,
                '--mode', self.mode,
                '--model', self.model
            ]

            if self.prompts:
                cmd.extend(['--prompts', json.dumps(self.prompts)])

            self.progress.emit(f"Starting segmentation...")

            # Clean environment to avoid QGIS Python conflicts
            clean_env = os.environ.copy()
            for var in ['PYTHONHOME', 'PYTHONPATH', 'PYTHONEXECUTABLE']:
                clean_env.pop(var, None)

            # Run subprocess
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,  # 10 minutes timeout
                env=clean_env
            )

            if result.returncode == 0:
                self.finished.emit(True, "Segmentation completed", self.output_gpkg)
            else:
                error_msg = result.stderr[:500] if result.stderr else "Unknown error"
                self.finished.emit(False, f"Segmentation failed: {error_msg}", "")

        except subprocess.TimeoutExpired:
            self.finished.emit(False, "Segmentation timed out", "")
        except Exception as e:
            self.finished.emit(False, f"Error: {str(e)}", "")


class SamSegmentationDialog(QDialog):
    """
    Dialog for SAM-based stone/object segmentation

    Allows users to:
    - Select a raster layer (orthophoto)
    - Choose target layer (pyunitastratigrafiche or _usm)
    - Set area and default attributes
    - Choose segmentation mode (auto, click, box)
    - Run segmentation and add results to target layer
    """

    def __init__(self, db_manager=None, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.worker_thread = None
        self.temp_output = None
        self.initUI()
        self.load_settings()

    def initUI(self):
        """Initialize the user interface"""
        self.setWindowTitle("SAM Stone Segmentation")
        self.setMinimumSize(500, 450)

        layout = QVBoxLayout(self)

        # Header
        header = QLabel(
            "<h3>Automatic Stone Segmentation</h3>"
            "<p>Use SAM (Segment Anything Model) to automatically detect and digitize stones.</p>"
        )
        header.setWordWrap(True)
        layout.addWidget(header)

        # Input group
        input_group = QGroupBox("Input")
        input_layout = QGridLayout()

        # Raster layer selection
        input_layout.addWidget(QLabel("Raster Layer:"), 0, 0)
        self.comboBox_raster = QgsMapLayerComboBox()
        self.comboBox_raster.setFilters(QgsMapLayerProxyModel.RasterLayer)
        self.comboBox_raster.setToolTip("Select the orthophoto or image to segment")
        input_layout.addWidget(self.comboBox_raster, 0, 1)

        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

        # Target layer group
        target_group = QGroupBox("Target Layer")
        target_layout = QGridLayout()

        target_layout.addWidget(QLabel("Layer:"), 0, 0)
        self.comboBox_target = QComboBox()
        self.comboBox_target.addItems([
            "pyunitastratigrafiche",
            "pyunitastratigrafiche_usm"
        ])
        self.comboBox_target.setToolTip("Select the target layer for polygons")
        target_layout.addWidget(self.comboBox_target, 0, 1)

        target_group.setLayout(target_layout)
        layout.addWidget(target_group)

        # Attributes group
        attr_group = QGroupBox("Default Attributes")
        attr_layout = QGridLayout()

        # Site (from config)
        attr_layout.addWidget(QLabel("Site (sito):"), 0, 0)
        self.lineEdit_site = QLineEdit()
        self.lineEdit_site.setReadOnly(True)
        self.lineEdit_site.setToolTip("Site from configuration (read-only)")
        self._load_site_from_config()
        attr_layout.addWidget(self.lineEdit_site, 0, 1)

        # Area
        attr_layout.addWidget(QLabel("Area:"), 1, 0)
        self.lineEdit_area = QLineEdit()
        self.lineEdit_area.setPlaceholderText("e.g., 1")
        self.lineEdit_area.setToolTip("Area number")
        attr_layout.addWidget(self.lineEdit_area, 1, 1)

        # Stratigraphic Index
        attr_layout.addWidget(QLabel("Stratigraphic Index:"), 2, 0)
        self.spinBox_strat_index = QSpinBox()
        self.spinBox_strat_index.setRange(1, 10)
        self.spinBox_strat_index.setValue(1)
        self.spinBox_strat_index.setToolTip("1 = stones/objects, 2 = soil/area")
        attr_layout.addWidget(self.spinBox_strat_index, 2, 1)

        # Type US
        attr_layout.addWidget(QLabel("Type US:"), 3, 0)
        self.comboBox_tipo_us = QComboBox()
        self.comboBox_tipo_us.addItems(["pietra", "layer", "accumulo", "taglio"])
        self.comboBox_tipo_us.setToolTip("Type of stratigraphic unit")
        attr_layout.addWidget(self.comboBox_tipo_us, 3, 1)

        attr_group.setLayout(attr_layout)
        layout.addWidget(attr_group)

        # Segmentation mode group
        mode_group = QGroupBox("Segmentation Mode")
        mode_layout = QVBoxLayout()

        self.radio_auto = QRadioButton("Automatic (detect all stones)")
        self.radio_auto.setToolTip("Automatically segment all detected objects in the visible area")
        self.radio_auto.setChecked(True)

        self.radio_click = QRadioButton("Click mode (click on each stone)")
        self.radio_click.setToolTip("Click on individual stones to segment them")
        self.radio_click.setEnabled(False)  # TODO: implement map tool

        self.radio_box = QRadioButton("Box mode (draw rectangle)")
        self.radio_box.setToolTip("Draw a rectangle to segment all stones within")
        self.radio_box.setEnabled(False)  # TODO: implement map tool

        self.mode_group = QButtonGroup()
        self.mode_group.addButton(self.radio_auto, 1)
        self.mode_group.addButton(self.radio_click, 2)
        self.mode_group.addButton(self.radio_box, 3)

        mode_layout.addWidget(self.radio_auto)
        mode_layout.addWidget(self.radio_click)
        mode_layout.addWidget(self.radio_box)

        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)

        # Model selection
        model_group = QGroupBox("Model")
        model_layout = QHBoxLayout()

        self.comboBox_model = QComboBox()
        self.comboBox_model.addItems([
            "fast (FastSAM - CPU friendly)",
            "sam (Standard SAM - more accurate)",
            "opencv (Fallback - edge detection)"
        ])
        self.comboBox_model.setToolTip("Select the segmentation model")
        model_layout.addWidget(self.comboBox_model)

        model_group.setLayout(model_layout)
        layout.addWidget(model_group)

        # Progress section
        self.label_status = QLabel("Ready")
        self.label_status.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(self.label_status)

        self.progressBar = QProgressBar()
        self.progressBar.setVisible(False)
        self.progressBar.setRange(0, 0)  # Indeterminate
        layout.addWidget(self.progressBar)

        # Buttons
        btn_layout = QHBoxLayout()

        self.btn_segment = QPushButton("Start Segmentation")
        self.btn_segment.setToolTip("Run segmentation on the selected raster")
        self.btn_segment.clicked.connect(self.on_segment_clicked)
        btn_layout.addWidget(self.btn_segment)

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)

        layout.addLayout(btn_layout)

    def _load_site_from_config(self):
        """Load site from PyArchInit config"""
        try:
            config_path = os.path.expanduser('~/pyarchinit/pyarchinit_DB_folder/config.cfg')
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config_str = f.read()
                    config = eval(config_str)
                    site = config.get('SITE_SET', '')
                    self.lineEdit_site.setText(site)
        except Exception as e:
            print(f"Error loading config: {e}")

    def load_settings(self):
        """Load saved settings"""
        s = QSettings()
        self.lineEdit_area.setText(s.value('pyArchInit/sam_last_area', ''))

    def save_settings(self):
        """Save settings"""
        s = QSettings()
        s.setValue('pyArchInit/sam_last_area', self.lineEdit_area.text())

    def get_mode(self):
        """Get selected segmentation mode"""
        if self.radio_auto.isChecked():
            return 'auto'
        elif self.radio_click.isChecked():
            return 'points'
        elif self.radio_box.isChecked():
            return 'box'
        return 'auto'

    def get_model(self):
        """Get selected model"""
        model_text = self.comboBox_model.currentText()
        if 'fast' in model_text.lower():
            return 'fast'
        elif 'opencv' in model_text.lower():
            return 'opencv'
        return 'sam'

    def on_segment_clicked(self):
        """Start segmentation process"""
        # Validate inputs
        raster_layer = self.comboBox_raster.currentLayer()
        if not raster_layer:
            QMessageBox.warning(self, "Error", "Please select a raster layer")
            return

        area = self.lineEdit_area.text().strip()
        if not area:
            QMessageBox.warning(self, "Error", "Please enter an area number")
            return

        # Get raster file path
        raster_path = raster_layer.source()
        if not os.path.exists(raster_path):
            QMessageBox.warning(self, "Error", f"Raster file not found: {raster_path}")
            return

        # Create temp output file
        self.temp_output = tempfile.mktemp(suffix='.gpkg')

        # Save settings
        self.save_settings()

        # Start worker thread
        self.btn_segment.setEnabled(False)
        self.progressBar.setVisible(True)
        self.label_status.setText("Segmentation in progress...")

        self.worker_thread = SamSegmentationWorkerThread(
            input_raster=raster_path,
            output_gpkg=self.temp_output,
            mode=self.get_mode(),
            prompts=None,  # For auto mode
            model=self.get_model()
        )
        self.worker_thread.finished.connect(self.on_segmentation_finished)
        self.worker_thread.progress.connect(self.on_progress)
        self.worker_thread.start()

    def on_progress(self, message):
        """Handle progress updates"""
        self.label_status.setText(message)

    def on_segmentation_finished(self, success, message, output_file):
        """Handle segmentation completion"""
        self.progressBar.setVisible(False)
        self.btn_segment.setEnabled(True)

        if not success:
            self.label_status.setText("Segmentation failed")
            QMessageBox.warning(self, "Segmentation Failed", message)
            return

        self.label_status.setText("Loading results...")
        QApplication.processEvents()

        # Load results and add to target layer
        try:
            self.add_polygons_to_target(output_file)
            self.label_status.setText("Segmentation complete!")
            QMessageBox.information(self, "Success",
                f"Segmentation complete!\n\n"
                "Polygons have been added to the target layer.\n"
                "Edit the attribute table to assign US numbers.")

        except Exception as e:
            self.label_status.setText("Error adding polygons")
            QMessageBox.warning(self, "Error", f"Failed to add polygons: {str(e)}")

        # Cleanup
        if self.temp_output and os.path.exists(self.temp_output):
            try:
                os.remove(self.temp_output)
            except:
                pass

    def add_polygons_to_target(self, gpkg_path):
        """Add segmented polygons to the target layer"""
        # Load segmented polygons
        temp_layer = QgsVectorLayer(gpkg_path, "sam_segments", "ogr")
        if not temp_layer.isValid():
            raise Exception(f"Could not load segmented polygons from {gpkg_path}")

        # Get target layer
        target_name = self.comboBox_target.currentText()
        target_layer = None

        for layer in QgsProject.instance().mapLayers().values():
            if layer.name() == target_name or target_name in layer.source():
                target_layer = layer
                break

        if not target_layer:
            raise Exception(f"Target layer '{target_name}' not found in project")

        # Get attributes
        site = self.lineEdit_site.text()
        area = self.lineEdit_area.text()
        strat_index = self.spinBox_strat_index.value()
        tipo_us = self.comboBox_tipo_us.currentText()

        # Start editing
        target_layer.startEditing()

        # Get field indices
        fields = target_layer.fields()

        # Add features
        added = 0
        for feature in temp_layer.getFeatures():
            geom = feature.geometry()

            # Transform CRS if needed
            if temp_layer.crs() != target_layer.crs():
                transform = QgsCoordinateTransform(
                    temp_layer.crs(),
                    target_layer.crs(),
                    QgsProject.instance()
                )
                geom.transform(transform)

            # Convert to MultiPolygon if needed
            if geom.type() == QgsWkbTypes.PolygonGeometry:
                if not geom.isMultipart():
                    geom.convertToMultiType()

            # Create new feature
            new_feature = QgsFeature(fields)
            new_feature.setGeometry(geom)

            # Set attributes
            if 'scavo_s' in [f.name() for f in fields]:
                new_feature.setAttribute('scavo_s', site)
            if 'area_s' in [f.name() for f in fields]:
                new_feature.setAttribute('area_s', area)
            if 'us_s' in [f.name() for f in fields]:
                new_feature.setAttribute('us_s', '')  # User will edit later
            if 'stratigraph_index_us' in [f.name() for f in fields]:
                new_feature.setAttribute('stratigraph_index_us', strat_index)
            if 'tipo_us_s' in [f.name() for f in fields]:
                new_feature.setAttribute('tipo_us_s', tipo_us)
            if 'disegnatore' in [f.name() for f in fields]:
                new_feature.setAttribute('disegnatore', 'SAM Auto-segmentation')
            if 'data' in [f.name() for f in fields]:
                new_feature.setAttribute('data', date.today().isoformat())

            target_layer.addFeature(new_feature)
            added += 1

        # Commit changes
        target_layer.commitChanges()
        target_layer.triggerRepaint()

        print(f"Added {added} polygons to {target_name}")

    def reject(self):
        """Handle dialog rejection (cancel)"""
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.terminate()
            self.worker_thread.wait()

        # Cleanup temp file
        if self.temp_output and os.path.exists(self.temp_output):
            try:
                os.remove(self.temp_output)
            except:
                pass

        super().reject()
