#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pottery Tools Tab
Archaeological pottery image processing and layout generation
"""

import os
import sys
import shutil
import platform
import subprocess
import urllib.request
from pathlib import Path
import traceback

from qgis.PyQt.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from qgis.PyQt.QtGui import QIcon, QPixmap, QImage, QPainter, QFont
from qgis.PyQt.QtWidgets import (QDialog, QMessageBox, QFileDialog,
                                QListWidgetItem, QTableWidgetItem,
                                QCheckBox, QGraphicsScene, QGraphicsPixmapItem)
from qgis.PyQt.uic import loadUiType
from qgis.core import QgsMessageLog, Qgis

# Import PyArchInit modules
from ..modules.db.pyarchinit_conn_strings import Connection
from ..modules.db.pyarchinit_db_manager import Pyarchinit_db_management
from ..modules.db.pyarchinit_utility import Utility
from ..modules.gis.pyarchinit_pyqgis import Pyarchinit_pyqgis
from ..modules.utility.pyarchinit_media_utility import *


# Import pottery processing modules (we'll create simplified versions)
from ..modules.utility.pottery_utilities import (
    PDFExtractor, LayoutGenerator, ImageProcessor
)

# Load the UI
MAIN_DIALOG_CLASS, _ = loadUiType(
    os.path.join(os.path.dirname(__file__),
                 os.pardir, 'gui', 'ui', 'Pottery_tools.ui'))


class PotteryToolsDialog(QDialog, MAIN_DIALOG_CLASS):
    """Main dialog for Pottery Tools functionality"""

    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.setupUi(self)

        # Initialize components
        self.DB_MANAGER = None
        self.extracted_images = []
        self.selected_images = []
        self.current_preview = None
        self.model_path = None
        self.has_gpu = self.detect_gpu()
        self.external_python = None  # Store the external Python path

        # Setup external Python with ultralytics (non-blocking)
        QTimer.singleShot(100, self.setup_external_python)

        # Setup database connection
        self.setup_database()

        # Connect signals
        self.connect_signals()

        # Initialize UI state
        self.init_ui_state()

        QgsMessageLog.logMessage("Pottery Tools initialized", "PyArchInit", Qgis.Info)

    def setup_database(self):
        """Setup database connection"""
        try:
            conn = Connection()
            conn_str = conn.conn_str()

            try:
                self.DB_MANAGER = Pyarchinit_db_management(conn_str)
                self.DB_MANAGER.connection()
            except Exception as e:
                QgsMessageLog.logMessage(f"Database connection error: {e}",
                                        "PyArchInit", Qgis.Critical)
                self.DB_MANAGER = None
        except Exception as e:
            QgsMessageLog.logMessage(f"Database setup error: {e}",
                                    "PyArchInit", Qgis.Critical)

    def connect_signals(self):
        """Connect UI signals to slots"""
        # PDF Extraction tab
        self.pushButton_browse_pdf.clicked.connect(self.browse_pdf)
        self.pushButton_extract.clicked.connect(self.extract_from_pdf)
        self.pushButton_download_model.clicked.connect(self.download_yolo_model)
        self.slider_confidence.valueChanged.connect(self.update_confidence_label)
        # Make extracted images clickable
        self.listWidget_extracted.itemDoubleClicked.connect(self.open_extracted_image)

        # Apply Model tab
        self.pushButton_apply_model.clicked.connect(self.apply_model_to_images)

        # Extract Masks tab
        self.pushButton_extract_masks.clicked.connect(self.extract_pottery_instances)
        self.listWidget_masks.itemDoubleClicked.connect(self.open_mask_image)
        self.listWidget_pottery_cards.itemDoubleClicked.connect(self.open_pottery_card)

        # Tabular Data tab
        self.pushButton_save_tabular.clicked.connect(self.save_tabular_data)

        # Post-Processing tab
        self.pushButton_process_all.clicked.connect(self.process_all_pottery)
        self.listWidget_processed.itemDoubleClicked.connect(self.open_processed_image)

        # Layout Creator tab
        self.radioButton_from_extraction.toggled.connect(self.toggle_image_source)
        self.radioButton_from_folder.toggled.connect(self.toggle_image_source)
        self.radioButton_from_db.toggled.connect(self.toggle_image_source)
        self.pushButton_browse_folder.clicked.connect(self.browse_folder)
        self.comboBox_layout_mode.currentIndexChanged.connect(self.update_layout_options)
        self.pushButton_preview_layout.clicked.connect(self.preview_layout)
        self.pushButton_generate_layout.clicked.connect(self.generate_layout)

        # Database Integration tab
        self.radioButton_pottery.toggled.connect(self.toggle_record_type)
        self.radioButton_inventory.toggled.connect(self.toggle_record_type)
        self.comboBox_site.currentTextChanged.connect(self.update_area_filter)
        self.pushButton_load_records.clicked.connect(self.load_records)
        self.pushButton_select_all.clicked.connect(self.select_all_records)
        self.pushButton_deselect_all.clicked.connect(self.deselect_all_records)
        self.pushButton_add_to_layout.clicked.connect(self.add_selected_to_layout)

    def init_ui_state(self):
        """Initialize UI state"""
        self.update_confidence_label(self.slider_confidence.value())
        self.toggle_image_source()
        self.update_layout_options()
        self.load_sites()
        self.check_model_status()

    def log_message(self, message, level=Qgis.Info):
        """Log message to both QGIS log and UI text edit"""
        QgsMessageLog.logMessage(message, "PyArchInit", level)
        self.textEdit_log.append(message)
        # Auto-scroll to bottom
        cursor = self.textEdit_log.textCursor()
        cursor.movePosition(cursor.End)
        self.textEdit_log.setTextCursor(cursor)

    # PDF Extraction methods
    def browse_pdf(self):
        """Browse for PDF file"""
        pdf_path, _ = QFileDialog.getOpenFileName(
            self, "Select PDF File", "", "PDF Files (*.pdf)")

        if pdf_path:
            self.lineEdit_pdf_path.setText(pdf_path)
            self.log_message(f"Selected PDF: {os.path.basename(pdf_path)}")

    def update_confidence_label(self, value):
        """Update confidence label with slider value"""
        self.label_confidence_value.setText(f"{value}%")

    def extract_from_pdf(self):
        """Extract pottery images from PDF"""
        pdf_path = self.lineEdit_pdf_path.text()

        if not pdf_path or not os.path.exists(pdf_path):
            QMessageBox.warning(self, "Warning", "Please select a valid PDF file")
            return

        try:
            self.log_message("Starting PDF extraction...")
            self.progressBar.setValue(10)

            # Create output directory
            output_dir = os.path.join(os.path.dirname(pdf_path),
                                     f"{Path(pdf_path).stem}_extracted")
            os.makedirs(output_dir, exist_ok=True)

            # Extract images (simplified version for now)
            extractor = PDFExtractor()
            split_pages = self.checkBox_split_pages.isChecked()
            auto_detect = self.checkBox_auto_detect.isChecked()
            confidence = self.slider_confidence.value() / 100.0

            self.progressBar.setValue(30)

            # Perform extraction
            extracted = extractor.extract(
                pdf_path, output_dir,
                split_pages=split_pages,
                auto_detect=auto_detect,
                confidence=confidence
            )

            self.progressBar.setValue(70)

            # Display extracted images
            self.extracted_images = extracted
            self.display_extracted_images()

            self.progressBar.setValue(100)
            self.log_message(f"Extraction complete: {len(extracted)} images found")

        except Exception as e:
            self.log_message(f"Extraction error: {str(e)}", Qgis.Critical)
            QMessageBox.critical(self, "Error", f"Failed to extract from PDF:\n{str(e)}")
        finally:
            self.progressBar.setValue(0)

    def display_extracted_images(self):
        """Display extracted images in list widget"""
        self.listWidget_extracted.clear()

        for img_path in self.extracted_images:
            if os.path.exists(img_path):
                # Create thumbnail
                pixmap = QPixmap(img_path)
                if not pixmap.isNull():
                    pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio,
                                          Qt.SmoothTransformation)

                    # Create list item
                    item = QListWidgetItem()
                    item.setIcon(QIcon(pixmap))
                    item.setText(os.path.basename(img_path))
                    item.setData(Qt.UserRole, img_path)

                    self.listWidget_extracted.addItem(item)

    def open_extracted_image(self, item):
        """Open extracted image when double-clicked"""
        img_path = item.data(Qt.UserRole)
        if img_path and os.path.exists(img_path):
            # Open image with system default viewer
            import subprocess
            import platform

            try:
                if platform.system() == 'Darwin':  # macOS
                    subprocess.run(['open', img_path])
                elif platform.system() == 'Windows':
                    os.startfile(img_path)
                else:  # Linux
                    subprocess.run(['xdg-open', img_path])

                self.log_message(f"Opened image: {os.path.basename(img_path)}")
            except Exception as e:
                self.log_message(f"Failed to open image: {str(e)}", Qgis.Warning)

    def open_mask_image(self, item):
        """Open mask image when double-clicked"""
        img_path, detections = item.data(Qt.UserRole)
        self.open_image_with_system(img_path)

    def open_pottery_card(self, item):
        """Open pottery card when double-clicked"""
        card_data = item.data(Qt.UserRole)
        if isinstance(card_data, dict):
            img_path = card_data.get('path')
        else:
            img_path = card_data
        self.open_image_with_system(img_path)

    def open_processed_image(self, item):
        """Open processed image when double-clicked"""
        card_data = item.data(Qt.UserRole)
        if isinstance(card_data, dict):
            img_path = card_data.get('path')
        else:
            img_path = card_data
        self.open_image_with_system(img_path)

    def open_image_with_system(self, img_path):
        """Open image with system default viewer"""
        if not img_path or not os.path.exists(img_path):
            self.log_message(f"Image not found: {img_path}", Qgis.Warning)
            return

        try:
            import subprocess
            import platform

            if platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', img_path])
                self.log_message(f"Opened: {os.path.basename(img_path)}")
            elif platform.system() == 'Windows':  # Windows
                os.startfile(img_path)
                self.log_message(f"Opened: {os.path.basename(img_path)}")
            else:  # Linux
                subprocess.run(['xdg-open', img_path])
                self.log_message(f"Opened: {os.path.basename(img_path)}")

        except Exception as e:
            self.log_message(f"Failed to open image: {str(e)}", Qgis.Warning)

    # Layout Creator methods
    def toggle_image_source(self):
        """Toggle image source options"""
        from_folder = self.radioButton_from_folder.isChecked()
        self.lineEdit_folder_path.setEnabled(from_folder)
        self.pushButton_browse_folder.setEnabled(from_folder)

        # Switch to database tab if database option selected
        if self.radioButton_from_db.isChecked():
            self.tabWidget_main.setCurrentIndex(2)

    def browse_folder(self):
        """Browse for image folder"""
        folder_path = QFileDialog.getExistingDirectory(
            self, "Select Image Folder")

        if folder_path:
            self.lineEdit_folder_path.setText(folder_path)
            self.load_folder_images(folder_path)

    def load_folder_images(self, folder_path):
        """Load images from folder"""
        try:
            image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']
            self.selected_images = []

            for file in os.listdir(folder_path):
                if any(file.lower().endswith(ext) for ext in image_extensions):
                    self.selected_images.append(os.path.join(folder_path, file))

            self.log_message(f"Loaded {len(self.selected_images)} images from folder")
        except Exception as e:
            self.log_message(f"Error loading folder images: {str(e)}", Qgis.Warning)

    def update_layout_options(self):
        """Update layout options based on mode"""
        is_grid = self.comboBox_layout_mode.currentText() == "Grid"
        self.spinBox_rows.setEnabled(is_grid)
        self.spinBox_cols.setEnabled(is_grid)
        self.label_grid_rows.setEnabled(is_grid)
        self.label_grid_cols.setEnabled(is_grid)

    def preview_layout(self):
        """Preview the layout"""
        try:
            # Gather images based on source
            images = self.gather_images_for_layout()

            if not images:
                QMessageBox.warning(self, "Warning", "No images selected for layout")
                return

            # Create preview
            generator = LayoutGenerator()
            preview = generator.create_preview(
                images,
                mode=self.comboBox_layout_mode.currentText().lower(),
                page_size=self.comboBox_page_size.currentText(),
                rows=self.spinBox_rows.value(),
                cols=self.spinBox_cols.value()
            )

            # Display preview
            if preview:
                scene = QGraphicsScene()
                pixmap = QPixmap.fromImage(preview)
                scene.addPixmap(pixmap)
                self.graphicsView_preview.setScene(scene)
                self.graphicsView_preview.fitInView(scene.itemsBoundingRect(),
                                                   Qt.KeepAspectRatio)

                self.log_message("Preview generated")
        except Exception as e:
            self.log_message(f"Preview error: {str(e)}", Qgis.Warning)

    def generate_layout(self):
        """Generate final layout"""
        try:
            # Gather images
            images = self.gather_images_for_layout()

            if not images:
                QMessageBox.warning(self, "Warning", "No images selected for layout")
                return

            # Get output path
            output_path, _ = QFileDialog.getSaveFileName(
                self, "Save Layout", "", "PDF Files (*.pdf);;PNG Files (*.png)")

            if not output_path:
                return

            self.progressBar.setValue(20)

            # Generate layout
            generator = LayoutGenerator()
            success = generator.generate(
                images,
                output_path,
                mode=self.comboBox_layout_mode.currentText().lower(),
                page_size=self.comboBox_page_size.currentText(),
                rows=self.spinBox_rows.value(),
                cols=self.spinBox_cols.value(),
                add_captions=self.checkBox_add_captions.isChecked(),
                add_scale=self.checkBox_add_scale.isChecked(),
                scale_cm=self.spinBox_scale_cm.value()
            )

            self.progressBar.setValue(100)

            if success:
                self.log_message(f"Layout saved to: {output_path}")
                QMessageBox.information(self, "Success",
                                       f"Layout generated successfully:\n{output_path}")
            else:
                raise Exception("Layout generation failed")

        except Exception as e:
            self.log_message(f"Layout generation error: {str(e)}", Qgis.Critical)
            QMessageBox.critical(self, "Error", f"Failed to generate layout:\n{str(e)}")
        finally:
            self.progressBar.setValue(0)

    def gather_images_for_layout(self):
        """Gather images based on selected source"""
        if self.radioButton_from_extraction.isChecked():
            return self.extracted_images
        elif self.radioButton_from_folder.isChecked():
            return self.selected_images
        elif self.radioButton_from_db.isChecked():
            return self.get_selected_db_images()
        return []

    # Database Integration methods
    def load_sites(self):
        """Load sites from database"""
        if not self.DB_MANAGER:
            return

        try:
            # Use query_bool to get all sites
            sites = self.DB_MANAGER.query_bool({}, 'SITE')

            self.comboBox_site.clear()
            self.comboBox_site.addItem("")

            if sites:
                # Extract unique site names
                site_names = set()
                for site_record in sites:
                    if hasattr(site_record, 'sito') and site_record.sito:
                        site_names.add(site_record.sito)

                # Add sorted sites to combo box
                for site_name in sorted(site_names):
                    self.comboBox_site.addItem(str(site_name))

        except Exception as e:
            self.log_message(f"Error loading sites: {str(e)}", Qgis.Warning)

    def update_area_filter(self):
        """Update area filter based on selected site"""
        if not self.DB_MANAGER:
            return

        site = self.comboBox_site.currentText()
        if not site:
            self.comboBox_area.clear()
            return

        try:
            # Query US records for this site to get areas
            search_dict = {"sito": "'" + str(site) + "'"}
            us_records = self.DB_MANAGER.query_bool(search_dict, 'US')

            self.comboBox_area.clear()
            self.comboBox_area.addItem("")

            if us_records:
                # Extract unique areas
                area_names = set()
                for us_record in us_records:
                    if hasattr(us_record, 'area') and us_record.area:
                        area_names.add(us_record.area)

                # Add sorted areas to combo box
                for area_name in sorted(area_names):
                    self.comboBox_area.addItem(str(area_name))

        except Exception as e:
            self.log_message(f"Error loading areas: {str(e)}", Qgis.Warning)

    def toggle_record_type(self):
        """Toggle between pottery and inventory records"""
        self.tableWidget_records.clear()
        self.tableWidget_records.setRowCount(0)

    def load_records(self):
        """Load records from database"""
        if not self.DB_MANAGER:
            QMessageBox.warning(self, "Warning", "Database not connected")
            return

        try:
            site = self.comboBox_site.currentText()
            area = self.comboBox_area.currentText()

            if not site:
                QMessageBox.warning(self, "Warning", "Please select a site")
                return

            # Clear table
            self.tableWidget_records.setRowCount(0)

            # Build search dict
            search_dict = {"sito": "'" + str(site) + "'"}
            if area:
                search_dict["area"] = "'" + str(area) + "'"

            if self.radioButton_pottery.isChecked():
                # Load pottery records
                records = self.DB_MANAGER.query_bool(search_dict, 'POTTERY')

                # Populate table with pottery records
                for row_num, record in enumerate(records):
                    self.tableWidget_records.insertRow(row_num)

                    # Add pottery data to columns
                    if hasattr(record, 'id_rep'):
                        self.tableWidget_records.setItem(row_num, 0,
                            QTableWidgetItem(str(record.id_rep)))
                    if hasattr(record, 'nr_reperto'):
                        self.tableWidget_records.setItem(row_num, 1,
                            QTableWidgetItem(str(record.nr_reperto)))
                    if hasattr(record, 'tipo_reperto'):
                        self.tableWidget_records.setItem(row_num, 2,
                            QTableWidgetItem(str(record.tipo_reperto)))
                    if hasattr(record, 'classe'):
                        self.tableWidget_records.setItem(row_num, 3,
                            QTableWidgetItem(str(record.classe)))
            else:
                # Load inventory records
                records = self.DB_MANAGER.query_bool(search_dict, 'INVENTARIO_MATERIALI')

                # Populate table with inventory records
                for row_num, record in enumerate(records):
                    self.tableWidget_records.insertRow(row_num)

                    # Add inventory data to columns
                    if hasattr(record, 'id_invmat'):
                        self.tableWidget_records.setItem(row_num, 0,
                            QTableWidgetItem(str(record.id_invmat)))
                    if hasattr(record, 'numero_inventario'):
                        self.tableWidget_records.setItem(row_num, 1,
                            QTableWidgetItem(str(record.numero_inventario)))
                    if hasattr(record, 'tipo_reperto'):
                        self.tableWidget_records.setItem(row_num, 2,
                            QTableWidgetItem(str(record.tipo_reperto)))
                    if hasattr(record, 'classe_materiale'):
                        self.tableWidget_records.setItem(row_num, 3,
                            QTableWidgetItem(str(record.classe_materiale)))

            # Add image status and checkbox for all records
            for row_num in range(len(records)):
                # Add image status
                img_item = QTableWidgetItem("No image")
                self.tableWidget_records.setItem(row_num, 4, img_item)

                # Add checkbox for selection
                checkbox = QCheckBox()
                self.tableWidget_records.setCellWidget(row_num, 5, checkbox)

            self.log_message(f"Loaded {len(records)} records")

        except Exception as e:
            self.log_message(f"Error loading records: {str(e)}", Qgis.Critical)
            QMessageBox.critical(self, "Error", f"Failed to load records:\n{str(e)}")

    def select_all_records(self):
        """Select all records in table"""
        for row in range(self.tableWidget_records.rowCount()):
            checkbox = self.tableWidget_records.cellWidget(row, 5)
            if checkbox:
                checkbox.setChecked(True)

    def deselect_all_records(self):
        """Deselect all records in table"""
        for row in range(self.tableWidget_records.rowCount()):
            checkbox = self.tableWidget_records.cellWidget(row, 5)
            if checkbox:
                checkbox.setChecked(False)

    def add_selected_to_layout(self):
        """Add selected database records to layout"""
        selected = []

        for row in range(self.tableWidget_records.rowCount()):
            checkbox = self.tableWidget_records.cellWidget(row, 5)
            if checkbox and checkbox.isChecked():
                # Get record ID
                record_id = self.tableWidget_records.item(row, 0).text()
                selected.append(record_id)

        if not selected:
            QMessageBox.warning(self, "Warning", "No records selected")
            return

        # TODO: Fetch actual images from media table
        self.log_message(f"Added {len(selected)} records to layout")

        # Switch to layout tab
        self.tabWidget_main.setCurrentIndex(1)
        QMessageBox.information(self, "Success",
                               f"Added {len(selected)} records to layout")

    def get_selected_db_images(self):
        """Get images for selected database records"""
        # TODO: Implement fetching actual images from media table
        return []

    def setup_external_python(self):
        """Setup external Python and check/install ultralytics"""
        try:
            self.log_message("Checking external Python setup...")

            # Find external Python
            self.external_python = self.find_python_executable()

            if self.external_python:
                self.log_message(f"External Python configured: {self.external_python}")

                # Check ultralytics installation in background
                self.check_ultralytics_async()
            else:
                self.log_message("Warning: Could not find suitable external Python", Qgis.Warning)

        except Exception as e:
            self.log_message(f"Error setting up external Python: {str(e)}", Qgis.Warning)

    def check_ultralytics_async(self):
        """Check if ultralytics is installed in external Python (non-blocking)"""
        if not self.external_python:
            return

        try:
            # Quick check if ultralytics is available
            clean_env = self.get_clean_environment()
            result = subprocess.run(
                [self.external_python, '-c', 'import ultralytics; print("OK")'],
                capture_output=True,
                text=True,
                timeout=2,
                env=clean_env
            )

            if result.returncode == 0 and "OK" in result.stdout:
                self.log_message("✓ Ultralytics is installed and ready")
            else:
                self.log_message("Ultralytics not found. Install it when needed.")

        except Exception as e:
            # Silently ignore - will prompt for installation when actually needed
            pass

    def detect_gpu(self):
        """Detect if GPU is available for YOLO inference"""
        try:
            # Check for CUDA (NVIDIA GPU)
            import torch
            if torch.cuda.is_available():
                self.log_message(f"CUDA GPU detected: {torch.cuda.get_device_name(0)}")
                return True

            # Check for MPS (Apple Silicon)
            if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                self.log_message("Apple Metal GPU detected")
                return True

        except ImportError:
            pass

        self.log_message("No GPU detected, will use CPU for inference")
        return False

    def check_model_status(self):
        """Check if YOLO model is installed"""
        # Check in user home directory under pyarchinit/bin
        home_dir = os.path.expanduser('~')
        models_dir = os.path.join(home_dir, 'pyarchinit', 'bin')

        # Check for different possible model names
        model_names = ['BasicModelv8_v01.pt', 'pottery_yolo.pt']
        model_found = False

        for model_name in model_names:
            model_file = os.path.join(models_dir, model_name)
            if os.path.exists(model_file):
                self.model_path = model_file
                self.label_model_status.setText(f"Model installed ✓ ({model_name})")
                self.label_model_status.setStyleSheet("color: green;")
                self.checkBox_auto_detect.setEnabled(True)
                self.log_message(f"YOLO model found at: {model_file}")
                model_found = True
                break

        if not model_found:
            self.label_model_status.setText("Model not installed")
            self.label_model_status.setStyleSheet("color: red;")
            self.checkBox_auto_detect.setEnabled(False)
            self.checkBox_auto_detect.setChecked(False)

    def download_yolo_model(self):
        """Download YOLO model from PyPotteryLens repository"""
        try:
            self.progressBar.setValue(10)
            self.log_message("Downloading YOLO model for pottery detection...")

            # Create models directory in user home if it doesn't exist
            home_dir = os.path.expanduser('~')
            models_dir = os.path.join(home_dir, 'pyarchinit', 'bin')
            os.makedirs(models_dir, exist_ok=True)

            # Model names from PyPotteryLens
            model_name = 'BasicModelv8_v01.pt'
            target_path = os.path.join(models_dir, model_name)

            # Check multiple possible locations for the model
            local_models = [
                f"/Users/enzo/Documents/PyPotteryLens/models_vision/{model_name}",
                os.path.join(os.path.expanduser('~'), 'Documents', 'PyPotteryLens', 'models_vision', model_name),
                os.path.join(os.path.dirname(__file__), '..', 'models', model_name),
            ]

            model_found = False
            for local_model in local_models:
                if os.path.exists(local_model):
                    # Copy from local PyPotteryLens
                    self.progressBar.setValue(50)
                    shutil.copy2(local_model, target_path)
                    self.log_message(f"Model copied from {local_model}")
                    model_found = True
                    break

            if not model_found:
                # Try to download from GitHub
                # Note: GitHub LFS or release assets would be needed for large model files
                model_url = f"https://github.com/enzococca/PyPotteryLens/raw/main/models_vision/{model_name}"
                self.progressBar.setValue(30)
                self.log_message(f"Attempting to download model from {model_url}")

                try:
                    urllib.request.urlretrieve(
                        model_url,
                        target_path,
                        reporthook=self._download_progress
                    )
                    self.log_message("Model downloaded successfully from GitHub")
                except Exception as e:
                    # If download fails, provide instructions
                    raise Exception(
                        f"Could not download model automatically.\n\n"
                        f"Please download the model manually:\n"
                        f"1. Clone PyPotteryLens: git clone https://github.com/enzococca/PyPotteryLens.git\n"
                        f"2. Copy models_vision/{model_name} to {target_path}\n\n"
                        f"Error: {str(e)}"
                    )

            self.progressBar.setValue(100)
            self.log_message("YOLO model downloaded successfully!")

            # Update UI status
            self.check_model_status()

            # Test model loading
            self.test_model_loading()

            QMessageBox.information(self, "Success",
                                   "YOLO model downloaded successfully!\n"
                                   "You can now use ML-based pottery detection.")

        except Exception as e:
            self.log_message(f"Model download error: {str(e)}", Qgis.Critical)
            QMessageBox.critical(self, "Error",
                                f"Failed to download model:\n{str(e)}")
        finally:
            self.progressBar.setValue(0)

    def _download_progress(self, block_num, block_size, total_size):
        """Update progress bar during download"""
        downloaded = block_num * block_size
        if total_size > 0:
            percent = min((downloaded / total_size) * 100, 100)
            self.progressBar.setValue(int(percent))

    def test_model_loading(self):
        """Test if the model can be loaded"""
        try:
            from ultralytics import YOLO
            import torch

            if self.model_path and os.path.exists(self.model_path):
                # Test loading the model
                model = YOLO(self.model_path)

                # Get device info
                if self.has_gpu:
                    if platform.system() == "Darwin" and hasattr(torch.backends, 'mps'):
                        device = 'mps'  # Apple Silicon
                    else:
                        device = 'cuda'  # NVIDIA GPU
                else:
                    device = 'cpu'

                self.log_message(f"Model loaded successfully. Using device: {device}")
                self.log_message(f"Model info: {model}")

                # Store device for later use
                self.inference_device = device

                return True

        except Exception as e:
            self.log_message(f"Model loading test failed: {str(e)}", Qgis.Warning)
            return False

    # Step 2: Apply Model to Images
    def apply_model_to_images(self):
        """Apply YOLO model to detect pottery in images"""
        if not self.extracted_images:
            QMessageBox.warning(self, "Warning", "Please extract images from PDF first")
            return

        if not self.model_path or not os.path.exists(self.model_path):
            QMessageBox.warning(self, "Warning", "YOLO model not found. Please download it first.")
            return

        try:
            self.log_message("Applying model to detect pottery...")
            self.progressBar.setValue(10)

            # Create standalone YOLO runner script
            self.create_yolo_runner_script()

            # Get parameters
            confidence = self.slider_confidence.value() / 100.0
            kernel_size = self.spinBox_kernel.value()
            iterations = self.spinBox_iterations.value()

            # Store detections for each image
            self.pottery_detections = {}

            import subprocess
            import json

            # Use the external Python found during setup or find new one
            if not self.external_python:
                self.external_python = self.find_python_executable()

            python_exe = self.external_python
            if not python_exe:
                self.log_message("Error: No suitable Python found", Qgis.Critical)
                QMessageBox.critical(self, "Error", "No suitable Python installation found.\nPlease install Python 3.9+ with pip.")
                return

            # Get path to runner script
            runner_script = os.path.join(os.path.expanduser("~/pyarchinit/bin"), "yolo_runner.py")

            total_images = len(self.extracted_images)
            for idx, img_path in enumerate(self.extracted_images):
                self.progressBar.setValue(10 + int((idx / total_images) * 80))

                # Log processing
                self.log_message(f"Processing image {idx+1}/{total_images}: {os.path.basename(img_path)}")

                try:
                    # Run YOLO inference using standalone script
                    cmd = [python_exe, runner_script, self.model_path, img_path, str(confidence), str(kernel_size), str(iterations)]

                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=60,
                        env=self.get_clean_environment()
                    )

                    # Try to parse JSON output regardless of return code
                    # Some warnings may cause non-zero exit but still have valid output
                    if result.stdout:
                        try:
                            # Clean output - sometimes there might be warnings before JSON
                            stdout = result.stdout.strip()
                            # Find JSON array in output
                            json_start = stdout.find('[')
                            if json_start >= 0:
                                json_str = stdout[json_start:]
                                detections_raw = json.loads(json_str)
                            else:
                                # Try parsing entire output as JSON
                                detections_raw = json.loads(stdout)

                            # Convert to our format
                            detections = []
                            for det in detections_raw:
                                if isinstance(det, dict) and 'bbox' in det:
                                    x, y, w, h = det['bbox']
                                    detections.append({
                                        'bbox': (x, y, w, h),
                                        'mask': det.get('mask_data'),  # Get mask if available
                                        'confidence': det.get('confidence', 0.5)
                                    })

                            self.pottery_detections[img_path] = detections
                            if detections:
                                # Show detections with confidence
                                conf_info = ", ".join([f"{d.get('confidence', 0.5):.0%}" for d in detections])
                                self.log_message(f"✓ {os.path.basename(img_path)}: {len(detections)} pottery found [{conf_info}]")
                            else:
                                self.log_message(f"○ {os.path.basename(img_path)}: No pottery detected")

                        except (json.JSONDecodeError, ValueError) as e:
                            # If JSON parsing fails, log but continue
                            self.log_message(f"⚠ {os.path.basename(img_path)}: Could not parse results")
                            if result.stderr and 'warning' not in result.stderr.lower():
                                self.log_message(f"  Debug stderr: {result.stderr[:200]}")
                            self.pottery_detections[img_path] = []
                    else:
                        # No output at all
                        self.log_message(f"✗ {os.path.basename(img_path)}: No output from model")
                        if result.stderr:
                            self.log_message(f"  Debug: {result.stderr[:200]}")
                        self.pottery_detections[img_path] = []

                except subprocess.TimeoutExpired:
                    self.log_message(f"Timeout processing {os.path.basename(img_path)}")
                    self.pottery_detections[img_path] = []
                except Exception as e:
                    self.log_message(f"Error processing {os.path.basename(img_path)}: {str(e)}")
                    self.pottery_detections[img_path] = []

            self.progressBar.setValue(100)

            # Show summary
            total_detections = sum(len(d) for d in self.pottery_detections.values())
            self.log_message(f"Model applied successfully! Found {total_detections} pottery instances")

            # Display results in list widget
            self.display_detection_results()

        except Exception as e:
            self.log_message(f"Error applying model: {str(e)}", Qgis.Critical)
            QMessageBox.critical(self, "Error", f"Failed to apply model:\n{str(e)}")
        finally:
            self.progressBar.setValue(0)

    def create_yolo_runner_script(self):
        """Create a standalone YOLO runner script in ~/pyarchinit/bin"""
        bin_dir = os.path.join(os.path.expanduser("~"), "pyarchinit", "bin")
        os.makedirs(bin_dir, exist_ok=True)

        script_path = os.path.join(bin_dir, "yolo_runner.py")

        # Create the runner script if it doesn't exist
        if not os.path.exists(script_path):
            script_content = '''#!/usr/bin/env python3
# Standalone YOLO runner for PyArchInit Pottery Tools
# This script runs outside of QGIS to avoid conflicts

import sys
import json
import os
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')
os.environ['YOLO_VERBOSE'] = 'False'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

def run_yolo_inference(model_path, img_path, confidence, kernel_size, iterations):
    """Run YOLO inference on an image"""
    try:
        # Import libraries only when needed
        from ultralytics import YOLO
        import cv2
        import numpy as np

        # Load model
        model = YOLO(model_path)

        # Run inference
        results = model(img_path, conf=confidence, device='cpu', verbose=False, show=False, save=False)

        detections = []
        for r in results:
            # Try to get masks (for segmentation models)
            if hasattr(r, 'masks') and r.masks is not None:
                if hasattr(r.masks, 'xy'):
                    for idx, xy in enumerate(r.masks.xy):
                        if len(xy) > 0:
                            x_coords = xy[:, 0]
                            y_coords = xy[:, 1]
                            x1, y1 = int(x_coords.min()), int(y_coords.min())
                            x2, y2 = int(x_coords.max()), int(y_coords.max())
                            conf = float(r.boxes.conf[idx]) if r.boxes and idx < len(r.boxes.conf) else confidence

                            # Apply morphological operations if needed
                            mask_data = None
                            if kernel_size > 0 and iterations > 0:
                                # Create binary mask from xy points
                                h, w = r.orig_shape
                                mask = np.zeros((h, w), dtype=np.uint8)
                                pts = np.array(xy, dtype=np.int32)
                                cv2.fillPoly(mask, [pts], 255)

                                # Apply morphological operations
                                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
                                mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=iterations)
                                mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=iterations)

                                # Convert mask to list for JSON serialization
                                mask_data = mask[y1:y2, x1:x2].tolist()

                            detections.append({
                                'bbox': [x1, y1, x2-x1, y2-y1],
                                'confidence': conf,
                                'has_mask': True,
                                'mask_data': mask_data
                            })
            # Try to get boxes (for detection models)
            elif hasattr(r, 'boxes') and r.boxes is not None:
                for box in r.boxes:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    detections.append({
                        'bbox': [int(x1), int(y1), int(x2-x1), int(y2-y1)],
                        'confidence': float(box.conf[0]),
                        'has_mask': False,
                        'mask_data': None
                    })

        return detections

    except Exception as e:
        return {'error': str(e)}

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print(json.dumps({'error': 'Usage: yolo_runner.py <model_path> <img_path> <confidence> [kernel_size] [iterations]'}))
        sys.exit(1)

    model_path = sys.argv[1]
    img_path = sys.argv[2]
    confidence = float(sys.argv[3])
    kernel_size = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    iterations = int(sys.argv[5]) if len(sys.argv) > 5 else 0

    result = run_yolo_inference(model_path, img_path, confidence, kernel_size, iterations)

    if isinstance(result, dict) and 'error' in result:
        print(json.dumps(result))
        sys.exit(1)
    else:
        print(json.dumps(result))
        sys.exit(0)
'''

            with open(script_path, 'w') as f:
                f.write(script_content)

            # Make script executable
            os.chmod(script_path, 0o755)

            self.log_message(f"Created YOLO runner script at {script_path}")

    def find_python_executable(self):
        """Find appropriate Python executable with ultralytics installed"""
        import subprocess
        import shutil
        import platform

        # List of Python executables to try based on platform
        if platform.system() == 'Windows':
            # Windows paths
            candidates = [
                r'C:\ProgramData\Anaconda3\python.exe',
                r'C:\Users\%USERNAME%\Anaconda3\python.exe',
                r'C:\Anaconda3\python.exe',
                r'C:\Python311\python.exe',
                r'C:\Python310\python.exe',
                r'C:\Python39\python.exe',
                r'C:\Program Files\Python311\python.exe',
                r'C:\Program Files\Python310\python.exe',
                r'C:\Program Files\Python39\python.exe',
            ]
            # Expand environment variables
            candidates = [os.path.expandvars(p) for p in candidates]
        else:
            # Unix-like systems (macOS, Linux)
            candidates = [
                '/usr/bin/python3',  # System Python (most common)
                '/usr/local/bin/python3',  # Homebrew Python on Intel Mac
                '/opt/homebrew/bin/python3',  # Homebrew Python on Apple Silicon
                '/opt/anaconda3/bin/python3',  # Anaconda if installed
                '/Library/Frameworks/Python.framework/Versions/3.11/bin/python3',  # Python.org installer
                '/Library/Frameworks/Python.framework/Versions/3.10/bin/python3',
                '/Library/Frameworks/Python.framework/Versions/3.9/bin/python3',
            ]

        # Also check if python/python3 is in PATH
        if platform.system() == 'Windows':
            python_path = shutil.which('python')
            if python_path and python_path not in candidates:
                candidates.insert(0, python_path)
        else:
            python3_path = shutil.which('python3')
            if python3_path and python3_path not in candidates:
                candidates.insert(0, python3_path)

        for python_exe in candidates:
            if not os.path.exists(python_exe):
                continue

            try:
                # Check if Python exists and has ultralytics
                # Use clean environment to avoid QGIS interference
                clean_env = self.get_clean_environment()
                result = subprocess.run(
                    [python_exe, '-c', 'import ultralytics; print("OK")'],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    env=clean_env
                )

                if result.returncode == 0 and "OK" in result.stdout:
                    self.log_message(f"Found Python with ultralytics: {python_exe}")
                    return python_exe
                elif "No module named 'ultralytics'" in result.stderr:
                    # Try to install ultralytics automatically
                    self.log_message(f"Ultralytics not found in {python_exe}, attempting to install...")
                    if self.install_ultralytics(python_exe):
                        return python_exe
                elif result.stderr:
                    # Log why it failed for debugging
                    self.log_message(f"Python {python_exe} check failed: {result.stderr[:100]}")

            except (subprocess.TimeoutExpired, FileNotFoundError) as e:
                self.log_message(f"Failed to check {python_exe}: {e}")
                continue

        # If no Python has ultralytics, try to install it on the first available Python
        self.log_message("No Python found with ultralytics. Attempting to install...")

        for python_exe in candidates:
            if os.path.exists(python_exe):
                self.log_message(f"Trying to install ultralytics on: {python_exe}")
                if self.install_ultralytics(python_exe):
                    return python_exe
                else:
                    self.log_message(f"Could not install on {python_exe}, trying next...")
                    continue

        # Last resort - use python/python3 from PATH
        if platform.system() == 'Windows':
            self.log_message("Warning: Using default python from PATH")
            return 'python'
        else:
            self.log_message("Warning: Using default python3 from PATH")
            return 'python3'

    def install_ultralytics(self, python_exe):
        """Attempt to install ultralytics using pip with streaming output"""
        import subprocess

        try:
            # Ask user for confirmation
            reply = QMessageBox.question(
                self,
                'Install Required Package',
                f'The YOLO model requires the "ultralytics" package.\n\n'
                f'Would you like to install it automatically?\n'
                f'This will run: pip install ultralytics\n\n'
                f'Using Python: {python_exe}',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )

            if reply != QMessageBox.Yes:
                return False

            self.log_message("=" * 50)
            self.log_message("Starting ultralytics installation...")
            self.log_message(f"Using Python: {python_exe}")
            self.log_message("This may take a few minutes...")
            self.log_message("=" * 50)

            self.progressBar.setRange(0, 0)  # Indeterminate progress

            # Use clean environment
            clean_env = self.get_clean_environment()

            # Check what packages are already installed
            self.log_message("Checking current package status...")
            already_installed = []
            packages_to_install = []

            for package in ['torch', 'torchvision', 'ultralytics']:
                try:
                    check_result = subprocess.run(
                        [python_exe, '-c', f'import {package}; print("OK")'],
                        capture_output=True,
                        text=True,
                        timeout=5,
                        env=clean_env
                    )
                    if check_result.returncode == 0:
                        already_installed.append(package)
                        self.log_message(f"✓ {package} already installed")
                    else:
                        packages_to_install.append(package)
                        self.log_message(f"✗ {package} needs installation")
                except:
                    packages_to_install.append(package)
                    self.log_message(f"✗ {package} needs installation")

            if not packages_to_install:
                self.log_message("✓ All required packages already installed!")
                self.progressBar.setRange(0, 100)
                self.progressBar.setValue(100)
                return True

            self.log_message(f"Packages to install: {', '.join(packages_to_install)}")

            # Try different installation strategies
            success = False

            for strategy in ['with_user', 'without_user']:
                if success:
                    break

                self.log_message(f"Trying installation strategy: {strategy}")

                # Build command based on strategy
                if strategy == 'with_user':
                    cmd = [python_exe, '-m', 'pip', 'install', '--user', '--progress-bar', 'off'] + packages_to_install
                else:
                    cmd = [python_exe, '-m', 'pip', 'install', '--progress-bar', 'off'] + packages_to_install

                try:
                    # Initialize terminal/shell session first
                    if platform.system() == 'Windows':
                        # For Windows, use shell=True to initialize properly
                        process = subprocess.Popen(
                            cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            text=True,
                            env=clean_env,
                            shell=True,
                            bufsize=1,
                            universal_newlines=True
                        )
                    else:
                        # For Unix systems, initialize shell environment
                        shell_cmd = f"cd ~ && {' '.join(cmd)}"
                        process = subprocess.Popen(
                            shell_cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            text=True,
                            env=clean_env,
                            shell=True,
                            bufsize=1,
                            universal_newlines=True
                        )

                    # Stream output to log widget
                    while True:
                        line = process.stdout.readline()
                        if not line:
                            break

                        # Clean and display the line
                        line = line.strip()
                        if line:
                            # Filter out some verbose lines but keep important ones
                            if any(keyword in line.lower() for keyword in ['collecting', 'downloading', 'installing', 'successfully', 'error', 'warning', 'requirement']):
                                self.log_message(f"  {line}")

                            # Force UI update
                            from qgis.PyQt.QtCore import QCoreApplication
                            QCoreApplication.processEvents()

                    # Wait for process to complete
                    process.wait(timeout=600)  # 10 minutes for all packages
                    result_code = process.returncode

                    if result_code == 0:
                        self.log_message(f"✓ Strategy '{strategy}' completed successfully")
                        success = True
                        break
                    else:
                        self.log_message(f"✗ Strategy '{strategy}' failed with code {result_code}")

                except subprocess.TimeoutExpired:
                    self.log_message(f"✗ Strategy '{strategy}' timed out")
                    process.kill()
                    continue
                except Exception as e:
                    self.log_message(f"✗ Strategy '{strategy}' error: {str(e)}")
                    continue

            if not success:
                self.log_message("✗ All installation strategies failed")
                self.progressBar.setRange(0, 100)
                self.progressBar.setValue(0)
                QMessageBox.warning(
                    self,
                    "Installation Failed",
                    f"Failed to install required packages.\n\n"
                    f"Please install manually using:\n"
                    f"{python_exe} -m pip install torch torchvision ultralytics\n\n"
                    f"Or try with --user flag:\n"
                    f"{python_exe} -m pip install --user torch torchvision ultralytics"
                )
                return False

            # If we get here, installation was successful
            self.log_message("✓ Installation completed successfully!")

            # Verify installation
            self.log_message("Verifying installation...")
            try:
                verify_result = subprocess.run(
                    [python_exe, '-c', 'import ultralytics; import torch; import torchvision; print("OK")'],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    env=clean_env
                )

                if verify_result.returncode == 0 and "OK" in verify_result.stdout:
                    self.log_message("✓ All packages verified and ready to use")
                    self.log_message("✓ torch, torchvision, ultralytics installed successfully")
                    self.log_message("=" * 50)
                    self.progressBar.setRange(0, 100)
                    self.progressBar.setValue(100)
                    return True
                else:
                    self.log_message("⚠ Installation completed but verification failed")
                    self.log_message(f"Verify stderr: {verify_result.stderr}")
                    self.progressBar.setRange(0, 100)
                    self.progressBar.setValue(0)
                    return False

            except Exception as e:
                self.log_message(f"⚠ Verification error: {str(e)}")
                self.progressBar.setRange(0, 100)
                self.progressBar.setValue(0)
                return False

        except subprocess.TimeoutExpired:
            self.log_message("✗ Installation timed out")
            QMessageBox.warning(
                self,
                "Installation Timeout",
                "Installation took too long.\n\n"
                "Please install ultralytics manually using:\n"
                "pip install ultralytics"
            )
            return False
        except Exception as e:
            self.log_message(f"✗ Installation error: {str(e)}")
            return False
        finally:
            self.progressBar.setValue(0)

    def get_clean_environment(self):
        """Get a clean environment for subprocess without QGIS paths"""
        env = os.environ.copy()

        # CRITICAL: Remove PYTHONHOME set by QGIS - this is causing the issue!
        if 'PYTHONHOME' in env:
            del env['PYTHONHOME']

        # Remove PYTHONPATH set by QGIS
        if 'PYTHONPATH' in env:
            del env['PYTHONPATH']

        # Remove other Python-related vars that might interfere
        for var in ['PYTHONSTARTUP', 'PYTHONUSERBASE', 'VIRTUAL_ENV']:
            if var in env:
                del env[var]

        # Set environment variables to suppress output
        env['YOLO_VERBOSE'] = 'False'
        env['TF_CPP_MIN_LOG_LEVEL'] = '3'
        env['PYTHONWARNINGS'] = 'ignore'
        env['PYTHONDONTWRITEBYTECODE'] = '1'

        return env

    def display_detection_results(self):
        """Display detection results with masks overlay"""
        self.listWidget_masks.clear()

        for img_path, detections in self.pottery_detections.items():
            # Create list item for each image with detections and confidence
            if detections:
                conf_avg = sum(d.get('confidence', 0.5) for d in detections) / len(detections)
                item_text = f"{os.path.basename(img_path)} - {len(detections)} pottery (avg. {conf_avg:.0%} conf.)"
            else:
                item_text = f"{os.path.basename(img_path)} - No pottery detected"

            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, (img_path, detections))
            self.listWidget_masks.addItem(item)

    # Step 3: Extract Individual Pottery Instances
    def extract_pottery_instances(self):
        """Extract each detected pottery as a separate image"""
        if not hasattr(self, 'pottery_detections') or not self.pottery_detections:
            QMessageBox.warning(self, "Warning", "Please apply model first to detect pottery")
            return

        try:
            from PIL import Image
            import numpy as np
            import cv2

            self.log_message("Extracting individual pottery instances...")
            self.progressBar.setValue(10)

            # Create output directory for pottery cards
            base_dir = os.path.dirname(self.extracted_images[0]) if self.extracted_images else os.getcwd()
            cards_dir = os.path.join(base_dir, "pottery_cards")
            os.makedirs(cards_dir, exist_ok=True)

            self.pottery_cards = []
            card_idx = 0

            for img_path, detections in self.pottery_detections.items():
                if not detections:
                    continue

                # Open source image
                img = Image.open(img_path)
                img_array = np.array(img)

                for det_idx, detection in enumerate(detections):
                    x, y, w, h = detection['bbox']

                    # Extract pottery region
                    if detection['mask'] is not None:
                        # Use mask for precise extraction
                        # The mask is already cropped to bbox size from yolo_runner
                        mask = np.array(detection['mask'])

                        # Crop the image region first
                        cropped_img = img_array[y:y+h, x:x+w].copy()

                        # Ensure mask dimensions match cropped image
                        if mask.shape[:2] != cropped_img.shape[:2]:
                            # Resize mask to match cropped image if needed
                            import cv2
                            mask = cv2.resize(mask.astype(np.uint8),
                                            (cropped_img.shape[1], cropped_img.shape[0]),
                                            interpolation=cv2.INTER_NEAREST)

                        # Normalize mask to 0-1 range
                        mask_normalized = (mask > 0).astype(np.float32)

                        # Create mask for all channels
                        if len(mask_normalized.shape) == 2:
                            mask_3d = np.stack([mask_normalized]*3, axis=2)
                        else:
                            mask_3d = mask_normalized

                        # Create white background
                        white_bg = np.ones_like(cropped_img) * 255

                        # Apply mask: pottery pixels from image, background pixels white
                        masked_img = (cropped_img * mask_3d + white_bg * (1 - mask_3d)).astype(np.uint8)

                        # Convert to PIL Image
                        cropped = Image.fromarray(masked_img)
                    else:
                        # Simple crop using bounding box
                        cropped = img.crop((x, y, x+w, y+h))

                    # Save pottery card
                    card_filename = f"pottery_{card_idx:04d}.png"
                    card_path = os.path.join(cards_dir, card_filename)
                    cropped.save(card_path, "PNG")

                    self.pottery_cards.append({
                        'path': card_path,
                        'source': img_path,
                        'confidence': detection['confidence'],
                        'bbox': detection['bbox']
                    })

                    card_idx += 1

            self.progressBar.setValue(100)
            self.log_message(f"Extracted {len(self.pottery_cards)} pottery instances to {cards_dir}")

            # Display pottery cards
            self.display_pottery_cards()

            # Initialize tabular data
            self.init_tabular_data()

        except Exception as e:
            self.log_message(f"Error extracting pottery: {str(e)}", Qgis.Critical)
            QMessageBox.critical(self, "Error", f"Failed to extract pottery:\n{str(e)}")
        finally:
            self.progressBar.setValue(0)

    def display_pottery_cards(self):
        """Display extracted pottery cards"""
        self.listWidget_pottery_cards.clear()

        for card in self.pottery_cards:
            if os.path.exists(card['path']):
                pixmap = QPixmap(card['path'])
                if not pixmap.isNull():
                    pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)

                    item = QListWidgetItem()
                    item.setIcon(QIcon(pixmap))
                    # Show filename with confidence if available
                    conf_text = f" [{card.get('confidence', 0.5):.0%}]" if 'confidence' in card else ""
                    item.setText(f"{os.path.basename(card['path'])}{conf_text}")
                    item.setData(Qt.UserRole, card)

                    self.listWidget_pottery_cards.addItem(item)

    # Step 4: Tabular Data Management
    def init_tabular_data(self):
        """Initialize tabular data for pottery cards"""
        self.tableWidget_pottery_data.setRowCount(len(self.pottery_cards))

        for idx, card in enumerate(self.pottery_cards):
            # ID
            self.tableWidget_pottery_data.setItem(idx, 0,
                QTableWidgetItem(f"P{idx+1:04d}"))

            # Image filename
            self.tableWidget_pottery_data.setItem(idx, 1,
                QTableWidgetItem(os.path.basename(card['path'])))

            # Type (default to FRAG)
            self.tableWidget_pottery_data.setItem(idx, 2,
                QTableWidgetItem("FRAG"))

            # Notes (empty for now)
            self.tableWidget_pottery_data.setItem(idx, 3,
                QTableWidgetItem(""))

    def save_tabular_data(self):
        """Save tabular data to CSV"""
        try:
            import csv

            # Get save path
            csv_path, _ = QFileDialog.getSaveFileName(
                self, "Save Tabular Data", "", "CSV Files (*.csv)")

            if not csv_path:
                return

            # Write CSV
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)

                # Header
                headers = []
                for col in range(self.tableWidget_pottery_data.columnCount()):
                    headers.append(self.tableWidget_pottery_data.horizontalHeaderItem(col).text())
                writer.writerow(headers)

                # Data
                for row in range(self.tableWidget_pottery_data.rowCount()):
                    row_data = []
                    for col in range(self.tableWidget_pottery_data.columnCount()):
                        item = self.tableWidget_pottery_data.item(row, col)
                        row_data.append(item.text() if item else "")
                    writer.writerow(row_data)

            self.log_message(f"Tabular data saved to {csv_path}")
            QMessageBox.information(self, "Success", "Tabular data saved successfully!")

        except Exception as e:
            self.log_message(f"Error saving tabular data: {str(e)}", Qgis.Critical)
            QMessageBox.critical(self, "Error", f"Failed to save data:\n{str(e)}")

    # Step 5: Post-Processing
    def process_all_pottery(self):
        """Apply post-processing to all pottery cards"""
        if not hasattr(self, 'pottery_cards') or not self.pottery_cards:
            QMessageBox.warning(self, "Warning", "No pottery cards to process")
            return

        try:
            from PIL import Image
            import numpy as np

            self.log_message("Processing pottery cards...")
            self.progressBar.setValue(10)

            # Create processed directory
            base_dir = os.path.dirname(self.pottery_cards[0]['path'])
            processed_dir = os.path.join(base_dir, "..", "pottery_processed")
            os.makedirs(processed_dir, exist_ok=True)

            auto_flip_v = self.checkBox_auto_flip_v.isChecked()
            auto_flip_h = self.checkBox_auto_flip_h.isChecked()
            auto_classify = self.checkBox_classify.isChecked()

            self.processed_cards = []

            for idx, card in enumerate(self.pottery_cards):
                self.progressBar.setValue(10 + int((idx / len(self.pottery_cards)) * 80))

                img = Image.open(card['path'])

                # Auto vertical flip (ensure mouth is up)
                if auto_flip_v:
                    # Simple heuristic: check if more content is at bottom
                    img_array = np.array(img.convert('L'))
                    top_half = np.mean(img_array[:img_array.shape[0]//2])
                    bottom_half = np.mean(img_array[img_array.shape[0]//2:])

                    if bottom_half > top_half * 1.2:  # More content at bottom
                        img = img.transpose(Image.FLIP_TOP_BOTTOM)

                # Auto horizontal flip (ensure profile faces left)
                if auto_flip_h:
                    # Simple heuristic: check balance
                    img_array = np.array(img.convert('L'))
                    left_half = np.mean(img_array[:, :img_array.shape[1]//2])
                    right_half = np.mean(img_array[:, img_array.shape[1]//2:])

                    if right_half > left_half * 1.1:  # More content on right
                        img = img.transpose(Image.FLIP_LEFT_RIGHT)

                # Auto classify ENT/FRAG
                pottery_type = "FRAG"  # Default
                if auto_classify:
                    # Simple heuristic: check if image is mostly complete
                    img_array = np.array(img.convert('L'))
                    non_empty = np.count_nonzero(img_array > 10)
                    total_pixels = img_array.size

                    if non_empty / total_pixels > 0.6:  # More than 60% filled
                        pottery_type = "ENT"

                # Save processed image
                processed_filename = f"pottery_proc_{idx:04d}_{pottery_type}.png"
                processed_path = os.path.join(processed_dir, processed_filename)
                img.save(processed_path, "PNG")

                self.processed_cards.append({
                    'path': processed_path,
                    'type': pottery_type,
                    'original': card['path']
                })

            self.progressBar.setValue(100)
            self.log_message(f"Processed {len(self.processed_cards)} pottery cards")

            # Update display
            self.display_processed_cards()

        except Exception as e:
            self.log_message(f"Error processing pottery: {str(e)}", Qgis.Critical)
            QMessageBox.critical(self, "Error", f"Failed to process pottery:\n{str(e)}")
        finally:
            self.progressBar.setValue(0)

    def display_processed_cards(self):
        """Display processed pottery cards"""
        self.listWidget_processed.clear()

        for card in self.processed_cards:
            if os.path.exists(card['path']):
                pixmap = QPixmap(card['path'])
                if not pixmap.isNull():
                    pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)

                    item = QListWidgetItem()
                    item.setIcon(QIcon(pixmap))
                    item.setText(f"{os.path.basename(card['path'])} [{card['type']}]")
                    item.setData(Qt.UserRole, card)

                    self.listWidget_processed.addItem(item)

        # Update images for layout
        if hasattr(self, 'processed_cards'):
            self.extracted_images = [card['path'] for card in self.processed_cards]