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
    QApplication, QFrame, QCheckBox
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

# Import map tools for interactive modes
try:
    from modules.gis.sam_map_tools import SamPointMapTool, SamBoxMapTool
    HAS_MAP_TOOLS = True
    print("DEBUG SAM: Map tools imported successfully")
except ImportError as e:
    HAS_MAP_TOOLS = False
    print(f"Warning: SAM map tools not available: {e}")


class SamApiWorkerThread(QThread):
    """Worker thread to run SAM segmentation via Replicate API using external script"""
    finished = pyqtSignal(bool, str, str)  # success, message, output_file
    progress = pyqtSignal(str)  # status message

    def __init__(self, input_raster, output_gpkg, api_key, mode='auto'):
        super().__init__()
        self.input_raster = input_raster
        self.output_gpkg = output_gpkg
        self.api_key = api_key
        self.mode = mode

    def run(self):
        """Run SAM API segmentation via external subprocess"""
        try:
            venv_python = os.path.expanduser('~/pyarchinit/bin/sam_venv/bin/python')
            worker_script = os.path.expanduser('~/pyarchinit/bin/sam_api_worker.py')

            if not os.path.exists(venv_python):
                self.finished.emit(False, "SAM virtual environment not found", "")
                return

            if not os.path.exists(worker_script):
                self.finished.emit(False, "SAM API worker script not found", "")
                return

            # Build command
            cmd = [
                venv_python, worker_script,
                '--input', self.input_raster,
                '--output', self.output_gpkg,
                '--api-key', self.api_key
            ]

            self.progress.emit("Starting API segmentation...")

            # Clean environment to avoid QGIS Python conflicts
            clean_env = os.environ.copy()
            for var in ['PYTHONHOME', 'PYTHONPATH', 'PYTHONEXECUTABLE']:
                clean_env.pop(var, None)

            # Run subprocess
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=900,  # 15 minutes timeout for API
                env=clean_env
            )

            if result.returncode == 0:
                self.finished.emit(True, "Segmentation completed", self.output_gpkg)
            else:
                error_msg = result.stderr[:500] if result.stderr else result.stdout[:500] if result.stdout else "Unknown error"
                self.finished.emit(False, f"Segmentation failed: {error_msg}", "")

        except subprocess.TimeoutExpired:
            self.finished.emit(False, "Segmentation timed out (15 min)", "")
        except Exception as e:
            self.finished.emit(False, f"Error: {str(e)}", "")


class SamSegmentationWorkerThread(QThread):
    """Worker thread to run SAM segmentation in background using official segment-anything"""
    finished = pyqtSignal(bool, str, str)  # success, message, output_file
    progress = pyqtSignal(str)  # status message

    def __init__(self, input_raster, output_gpkg, mode='auto', prompts=None, model='vit_b'):
        super().__init__()
        self.input_raster = input_raster
        self.output_gpkg = output_gpkg
        self.mode = mode
        self.prompts = prompts
        self.model = model  # vit_b, vit_l, or vit_h

    def run(self):
        """Run SAM segmentation in subprocess using official segment-anything"""
        try:
            venv_python = os.path.expanduser('~/pyarchinit/bin/sam_venv/bin/python')
            # Use new local worker that uses official segment-anything
            worker_script = os.path.expanduser('~/pyarchinit/bin/sam_local_worker.py')

            if not os.path.exists(venv_python):
                self.finished.emit(False, "SAM virtual environment not found at ~/pyarchinit/bin/sam_venv/", "")
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
        self.map_tool = None  # Current active map tool
        self.collected_prompts = None  # Prompts collected from interactive modes
        self.previous_map_tool = None  # Store previous tool to restore
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
        self.radio_click.setToolTip("Click on individual stones to segment them. Right-click or press Enter when done.")

        self.radio_box = QRadioButton("Box mode (draw rectangle)")
        self.radio_box.setToolTip("Draw a rectangle to segment all stones within that area")

        self.mode_group = QButtonGroup()
        self.mode_group.addButton(self.radio_auto, 1)
        self.mode_group.addButton(self.radio_click, 2)
        self.mode_group.addButton(self.radio_box, 3)

        mode_layout.addWidget(self.radio_auto)
        mode_layout.addWidget(self.radio_click)
        mode_layout.addWidget(self.radio_box)

        # Instructions label for interactive modes
        self.label_instructions = QLabel("")
        self.label_instructions.setStyleSheet("color: #0066cc; font-style: italic;")
        self.label_instructions.setWordWrap(True)
        self.label_instructions.setVisible(False)
        mode_layout.addWidget(self.label_instructions)

        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)

        # Connect mode change to update instructions
        self.mode_group.buttonClicked.connect(self._on_mode_changed)

        # Model selection
        model_group = QGroupBox("Model")
        model_layout = QGridLayout()

        model_layout.addWidget(QLabel("Method:"), 0, 0)
        self.comboBox_model = QComboBox()
        self.comboBox_model.addItems([
            "API: Replicate SAM-2 (cloud, recommended)",
            "Local: SAM vit_b (fast, ~375MB)",
            "Local: SAM vit_l (balanced, ~1.2GB)",
            "Local: SAM vit_h (best quality, ~2.5GB)",
            "Local: OpenCV (edge detection fallback)"
        ])
        self.comboBox_model.setToolTip(
            "Cloud API is recommended.\n"
            "Local SAM requires downloading model weights on first use.\n"
            "vit_b = fastest, vit_h = most accurate"
        )
        self.comboBox_model.currentIndexChanged.connect(self._on_model_changed)
        model_layout.addWidget(self.comboBox_model, 0, 1)

        # API Key (shown by default since API is first option)
        self.label_api_key = QLabel("API Key:")
        self.label_api_key.setVisible(True)
        model_layout.addWidget(self.label_api_key, 1, 0)

        self.lineEdit_api_key = QLineEdit()
        self.lineEdit_api_key.setPlaceholderText("Replicate API key")
        self.lineEdit_api_key.setEchoMode(QLineEdit.Password)
        self.lineEdit_api_key.setToolTip("Get your API key from replicate.com")
        self.lineEdit_api_key.setVisible(True)
        model_layout.addWidget(self.lineEdit_api_key, 1, 1)

        # Link to get API key
        self.label_api_link = QLabel('<a href="https://replicate.com/account/api-tokens">Get API key</a>')
        self.label_api_link.setOpenExternalLinks(True)
        self.label_api_link.setVisible(True)
        model_layout.addWidget(self.label_api_link, 2, 1)

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

    def _on_model_changed(self, index):
        """Show/hide API key field based on model selection"""
        is_api = 'API' in self.comboBox_model.currentText()
        self.label_api_key.setVisible(is_api)
        self.lineEdit_api_key.setVisible(is_api)
        self.label_api_link.setVisible(is_api)

    def _on_mode_changed(self, button):
        """Update UI when segmentation mode changes"""
        if self.radio_click.isChecked():
            self.label_instructions.setText(
                "Click mode: Click 'Start' then click on stones in the map. "
                "Right-click or press Enter when done. Press Escape to cancel."
            )
            self.label_instructions.setVisible(True)
            self.btn_segment.setText("Start Selection")
        elif self.radio_box.isChecked():
            self.label_instructions.setText(
                "Box mode: Click 'Start' then draw a rectangle on the map. "
                "Press Escape to cancel."
            )
            self.label_instructions.setVisible(True)
            self.btn_segment.setText("Start Selection")
        else:
            self.label_instructions.setVisible(False)
            self.btn_segment.setText("Start Segmentation")

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
        self.lineEdit_api_key.setText(s.value('pyArchInit/sam_api_key', ''))

    def save_settings(self):
        """Save settings"""
        s = QSettings()
        s.setValue('pyArchInit/sam_last_area', self.lineEdit_area.text())
        # Save API key if provided
        if self.lineEdit_api_key.text().strip():
            s.setValue('pyArchInit/sam_api_key', self.lineEdit_api_key.text().strip())

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
        if 'vit_b' in model_text:
            return 'vit_b'
        elif 'vit_l' in model_text:
            return 'vit_l'
        elif 'vit_h' in model_text:
            return 'vit_h'
        elif 'OpenCV' in model_text:
            return 'opencv'
        elif 'API' in model_text:
            return 'api'
        return 'vit_b'  # default

    def is_api_mode(self):
        """Check if API mode is selected"""
        return 'API' in self.comboBox_model.currentText()

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

        # Check API key if API mode
        if self.is_api_mode():
            api_key = self.lineEdit_api_key.text().strip()
            if not api_key:
                QMessageBox.warning(self, "Error",
                    "Please enter your Replicate API key.\n\n"
                    "Get one at: https://replicate.com/account/api-tokens")
                return

        # Get raster file path
        raster_path = raster_layer.source()
        if not os.path.exists(raster_path):
            QMessageBox.warning(self, "Error", f"Raster file not found: {raster_path}")
            return

        # Save settings
        self.save_settings()

        # Handle interactive modes (click or box)
        mode = self.get_mode()
        if mode in ['points', 'box'] and HAS_MAP_TOOLS:
            self._start_interactive_selection(raster_layer, mode)
            return

        # For auto mode or if map tools not available, run directly
        self._run_segmentation(raster_path, None)

    def _start_interactive_selection(self, raster_layer, mode):
        """Start interactive map tool for point or box selection"""
        print(f"DEBUG SAM: _start_interactive_selection called with mode={mode}")
        print(f"DEBUG SAM: HAS_MAP_TOOLS={HAS_MAP_TOOLS}")
        print(f"DEBUG SAM: raster_layer={raster_layer}, name={raster_layer.name() if raster_layer else 'None'}")

        canvas = iface.mapCanvas()
        print(f"DEBUG SAM: canvas={canvas}")

        # Store previous tool to restore later
        self.previous_map_tool = canvas.mapTool()
        print(f"DEBUG SAM: previous_map_tool={self.previous_map_tool}")

        # Hide dialog temporarily
        self.hide()
        print("DEBUG SAM: Dialog hidden")

        # Create appropriate map tool
        if mode == 'points':
            print("DEBUG SAM: Creating SamPointMapTool...")
            try:
                self.map_tool = SamPointMapTool(canvas, raster_layer)
                print(f"DEBUG SAM: SamPointMapTool created: {self.map_tool}")
                self.map_tool.pointsCollected.connect(self._on_points_collected)
                self.map_tool.pointAdded.connect(self._on_point_added)
                self.map_tool.cancelled.connect(self._on_selection_cancelled)
                print("DEBUG SAM: Signals connected for point tool")
            except Exception as e:
                print(f"DEBUG SAM ERROR: Failed to create SamPointMapTool: {e}")
                import traceback
                traceback.print_exc()
                self.show()
                return

            # Show info message
            iface.messageBar().pushInfo(
                "SAM Click Mode",
                "Click on stones to mark them. Right-click or press Enter when done. Press Escape to cancel."
            )
        else:  # box mode
            print("DEBUG SAM: Creating SamBoxMapTool...")
            try:
                self.map_tool = SamBoxMapTool(canvas, raster_layer)
                print(f"DEBUG SAM: SamBoxMapTool created: {self.map_tool}")
                self.map_tool.boxDrawn.connect(self._on_box_drawn)
                self.map_tool.cancelled.connect(self._on_selection_cancelled)
                print("DEBUG SAM: Signals connected for box tool")
            except Exception as e:
                print(f"DEBUG SAM ERROR: Failed to create SamBoxMapTool: {e}")
                import traceback
                traceback.print_exc()
                self.show()
                return

            # Show info message
            iface.messageBar().pushInfo(
                "SAM Box Mode",
                "Click and drag to draw a rectangle. Press Escape to cancel."
            )

        # Activate the tool
        print(f"DEBUG SAM: Setting map tool on canvas...")
        canvas.setMapTool(self.map_tool)
        print(f"DEBUG SAM: Map tool set. Current tool: {canvas.mapTool()}")

    def _on_points_collected(self, points):
        """Handle collected points from click mode"""
        print(f"Points collected: {len(points)} points")
        self.collected_prompts = points

        # Restore previous map tool
        self._restore_map_tool()

        # Show dialog again
        self.show()

        if len(points) == 0:
            QMessageBox.warning(self, "Warning", "No points were selected.")
            return

        # Run segmentation with prompts
        raster_layer = self.comboBox_raster.currentLayer()
        if raster_layer:
            self._run_segmentation(raster_layer.source(), points)

    def _on_point_added(self, count):
        """Handle point added event for feedback"""
        iface.messageBar().pushInfo("SAM", f"{count} point(s) selected")

    def _on_box_drawn(self, boxes):
        """Handle drawn box from box mode"""
        print(f"Box drawn: {boxes}")
        self.collected_prompts = boxes

        # Restore previous map tool
        self._restore_map_tool()

        # Show dialog again
        self.show()

        if not boxes or len(boxes) == 0:
            QMessageBox.warning(self, "Warning", "No box was drawn or box was outside raster bounds.")
            return

        # Run segmentation with box prompt
        raster_layer = self.comboBox_raster.currentLayer()
        if raster_layer:
            self._run_segmentation(raster_layer.source(), boxes)

    def _on_selection_cancelled(self):
        """Handle cancellation of interactive selection"""
        print("Selection cancelled")

        # Restore previous map tool
        self._restore_map_tool()

        # Show dialog again
        self.show()

        iface.messageBar().pushInfo("SAM", "Selection cancelled")

    def _restore_map_tool(self):
        """Restore the previous map tool"""
        canvas = iface.mapCanvas()

        if self.map_tool:
            self.map_tool.deactivate()
            self.map_tool = None

        if self.previous_map_tool:
            canvas.setMapTool(self.previous_map_tool)
            self.previous_map_tool = None

    def _run_segmentation(self, raster_path, prompts):
        """Run the segmentation with optional prompts"""
        # Create temp output file
        self.temp_output = tempfile.mktemp(suffix='.gpkg')

        # Start worker thread
        self.btn_segment.setEnabled(False)
        self.progressBar.setVisible(True)
        self.label_status.setText("Segmentation in progress...")

        mode = self.get_mode()

        if self.is_api_mode():
            # Use API worker
            self.worker_thread = SamApiWorkerThread(
                input_raster=raster_path,
                output_gpkg=self.temp_output,
                api_key=self.lineEdit_api_key.text().strip(),
                mode=mode
            )
        else:
            # Use local worker
            self.worker_thread = SamSegmentationWorkerThread(
                input_raster=raster_path,
                output_gpkg=self.temp_output,
                mode=mode,
                prompts=prompts,
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
        """Add segmented polygons to the target layer or load as new layer"""
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
            # Target layer not found - load as new layer in QGIS
            print(f"Target layer '{target_name}' not found, loading as new layer")

            # Copy to permanent location in pyarchinit folder
            import shutil
            pyarchinit_dir = os.path.expanduser('~/pyarchinit/pyarchinit_DB_folder')
            os.makedirs(pyarchinit_dir, exist_ok=True)

            timestamp = __import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')
            layer_name = f"SAM_Segments_{self.lineEdit_area.text()}_{timestamp}"
            permanent_path = os.path.join(pyarchinit_dir, f"{layer_name}.gpkg")

            shutil.copy2(gpkg_path, permanent_path)
            print(f"Saved to: {permanent_path}")

            new_layer = QgsVectorLayer(permanent_path, layer_name, "ogr")

            if new_layer.isValid():
                QgsProject.instance().addMapLayer(new_layer)
                iface.mapCanvas().refresh()
                iface.setActiveLayer(new_layer)
                iface.zoomToActiveLayer()
                print(f"Added {new_layer.featureCount()} polygons as new layer '{layer_name}'")
            else:
                raise Exception("Could not load segmented polygons as layer")
            return

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
