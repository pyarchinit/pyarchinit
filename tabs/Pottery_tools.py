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
                                QListWidgetItem, QTableWidgetItem, QApplication,
                                QCheckBox, QGraphicsScene, QGraphicsPixmapItem, QWidget)
from qgis.PyQt.uic import loadUiType
from qgis.core import QgsMessageLog, Qgis

# Import PyArchInit modules
from ..modules.db.pyarchinit_conn_strings import Connection
from ..modules.db.pyarchinit_db_manager import get_db_manager
from ..modules.db.pyarchinit_utility import Utility
from ..modules.gis.pyarchinit_pyqgis import Pyarchinit_pyqgis
from ..modules.utility.pyarchinit_media_utility import *


# Import pottery processing modules (we'll create simplified versions)
from ..modules.utility.pottery_utilities import (
    PDFExtractor, LayoutGenerator, ImageProcessor, PotteryInkProcessor
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
        
        # Package cache to avoid repeated checks
        self._package_cache = {}
        self._cache_timestamp = None
        self._cache_valid_duration = 300  # 5 minutes
        
        # Show startup progress
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(10)
        self.log_message("Initializing Pottery Tools...")
        self.selected_images = []
        self.current_preview = None
        self.model_path = None
        self.has_gpu = False  # Will be updated after venv setup
        self.external_python = None  # Store the external Python path
        self.venv_path = None  # Virtual environment path
        self.venv_python = None  # Python executable in venv

        # Initialize PotteryInk processor (will be re-initialized with venv_python after setup)
        self.pottery_ink = PotteryInkProcessor()

        # Setup virtual environment for external packages
        self.progressBar.setValue(30)
        self.log_message("Setting up virtual environment...")
        self.setup_pottery_venv()

        # Setup external Python with ultralytics (non-blocking)
        self.progressBar.setValue(60)
        self.log_message("Configuring Python environment...")
        QTimer.singleShot(100, self.setup_external_python)

        # Setup database connection
        self.progressBar.setValue(70)
        self.log_message("Setting up database...")
        self.setup_database()

        # Connect signals
        self.connect_signals()

        # Initialize UI state
        self.progressBar.setValue(90)
        self.log_message("Finalizing UI...")
        self.init_ui_state()

        # Complete initialization
        QTimer.singleShot(500, lambda: (
            self.progressBar.setValue(100),
            self.log_message("✓ Pottery Tools initialized successfully!"),
            QTimer.singleShot(1000, lambda: self.progressBar.setValue(0))
        ))

        QgsMessageLog.logMessage("Pottery Tools initialized", "PyArchInit", Qgis.Info)

    def is_cache_valid(self):
        """Check if package cache is still valid"""
        if not self._cache_timestamp:
            return False
        import time
        return (time.time() - self._cache_timestamp) < self._cache_valid_duration
    
    def update_cache(self, package, status):
        """Update package cache"""
        import time
        if not self._cache_timestamp:
            self._cache_timestamp = time.time()
        self._package_cache[package] = status
    
    def get_cached_status(self, package):
        """Get cached package status"""
        if self.is_cache_valid() and package in self._package_cache:
            return self._package_cache[package]
        return None

    def setup_pottery_venv(self, retry_count=0):
        """Setup virtual environment for Pottery Tools"""
        try:
            # Prevent infinite loops
            if retry_count > 2:
                self.log_message("⚠ Maximum retry attempts reached. Pottery Tools will work with limited functionality.", Qgis.Warning)
                return
                
            # Define venv path
            home_dir = os.path.expanduser('~')
            self.venv_path = os.path.join(home_dir, 'pyarchinit', 'bin', 'pottery_venv')

            # Check if venv exists
            if platform.system() == 'Windows':
                self.venv_python = os.path.join(self.venv_path, 'Scripts', 'python.exe')
            else:
                self.venv_python = os.path.join(self.venv_path, 'bin', 'python')

            # Create venv if it doesn't exist
            if not os.path.exists(self.venv_path):
                self.log_message("Creating Pottery Tools virtual environment...")

                # Use system Python executable to create venv (not QGIS)
                try:
                    # Create the venv using subprocess to avoid QGIS Python issues
                    import subprocess
                    import shutil

                    # Find the actual Python executable, not QGIS
                    python_exe = None
                    
                    # Try to find Python executable in different locations
                    possible_pythons = [
                        'python3',  # System Python on macOS/Linux
                        'python',   # Fallback
                        '/usr/bin/python3',  # macOS system Python
                        '/usr/local/bin/python3',  # Homebrew Python
                        '/opt/homebrew/bin/python3',  # M1 Mac Homebrew
                        '/Applications/QGIS.app/Contents/MacOS/bin/python3'  # QGIS bundled Python
                    ]
                    
                    # Try each Python executable until one works
                    venv_created = False
                    for py in possible_pythons:
                        if not shutil.which(py):
                            continue
                            
                        # Test if Python executable works
                        test_cmd = [py, '--version']
                        test_result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=10)
                        if test_result.returncode != 0:
                            self.log_message(f"Python {py} test failed: {test_result.stderr}", Qgis.Warning)
                            continue
                        
                        self.log_message(f"Testing Python: {py} - {test_result.stdout.strip()}")
                        
                        # Create the directory if it doesn't exist
                        venv_parent = os.path.dirname(self.venv_path)
                        os.makedirs(venv_parent, exist_ok=True)
                        
                        create_cmd = [py, '-m', 'venv', self.venv_path, '--clear']
                        self.log_message(f"Running command: {' '.join(create_cmd)}")
                        result = subprocess.run(create_cmd, capture_output=True, text=True, timeout=30)

                        if result.returncode == 0:
                            self.log_message(f"✓ Virtual environment created at: {self.venv_path}")
                            python_exe = py
                            venv_created = True

                            # Upgrade pip in venv
                            self.upgrade_venv_pip()

                            # Mark for package installation
                            self.need_venv_packages = True
                            break  # Success, exit the loop
                        else:
                            error_msg = result.stderr.strip() if result.stderr.strip() else result.stdout.strip()
                            if not error_msg:
                                error_msg = f"Unknown error (return code: {result.returncode})"
                            self.log_message(f"Failed to create venv with {py}: {error_msg}", Qgis.Warning)
                    
                    if not venv_created:
                        raise Exception("Failed to create virtual environment with any Python executable")

                except Exception as e:
                    self.log_message(f"Error creating venv: {str(e)}", Qgis.Warning)
                    self.venv_path = None
                    self.venv_python = None
                    return
            else:
                self.log_message(f"✓ Virtual environment found: {self.venv_path}")
                # Check if packages are installed
                self.need_venv_packages = not self.check_venv_packages()

            # Set this as the external Python
            if os.path.exists(self.venv_python):
                self.external_python = self.venv_python
                self.log_message(f"✓ Using venv Python: {self.venv_python}")

                # Re-initialize PotteryInk processor with venv_python
                # Force reload the module to get new methods
                import importlib
                import modules.utility.pottery_utilities as pu_module
                importlib.reload(pu_module)
                from modules.utility.pottery_utilities import PotteryInkProcessor
                self.pottery_ink = PotteryInkProcessor(venv_python=self.venv_python)
                self.log_message("✓ PotteryInk processor initialized with venv Python")

        except Exception as e:
            self.log_message(f"Virtual environment setup error: {str(e)}", Qgis.Warning)
            self.venv_path = None
            self.venv_python = None

    def check_venv_packages(self):
        """Check if required packages are installed in virtual environment"""
        if not self.venv_python or not os.path.exists(self.venv_python):
            return False

        try:
            import subprocess

            # Create clean environment without QGIS interference
            clean_env = os.environ.copy()
            for key in ['PYTHONHOME', 'PYTHONPATH', 'PYTHONSTARTUP', 'VIRTUAL_ENV']:
                clean_env.pop(key, None)

            # Check for key packages
            check_packages = ['ultralytics', 'torch', 'diffusers']

            for package in check_packages:
                cmd = [self.venv_python, '-c', f'import {package}']
                # Longer timeout for heavy packages like torch/ultralytics
                timeout = 30 if package in ['torch', 'ultralytics', 'diffusers'] else 10
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=clean_env)
                if result.returncode != 0:
                    self.log_message(f"Package {package} not found in venv")
                    return False

            self.log_message("✓ All required packages found in virtual environment")
            return True

        except Exception as e:
            self.log_message(f"Error checking packages: {str(e)}", Qgis.Warning)
            return False

    def upgrade_venv_pip(self):
        """Upgrade pip in the virtual environment"""
        if not self.venv_python or not os.path.exists(self.venv_python):
            return

        try:
            import subprocess

            # Upgrade pip
            cmd = [self.venv_python, '-m', 'pip', 'install', '--upgrade', 'pip']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode == 0:
                self.log_message("✓ pip upgraded in virtual environment")
            else:
                self.log_message(f"⚠ pip upgrade warning: {result.stderr[:200]}")

        except Exception as e:
            self.log_message(f"pip upgrade error: {str(e)}", Qgis.Warning)

    def auto_install_packages(self):
        """Automatically install packages in virtual environment without user interaction"""
        if not self.venv_python or not os.path.exists(self.venv_python):
            self.setup_pottery_venv()
            return

        try:
            import subprocess
            import threading
            from qgis.PyQt.QtCore import QTimer

            def install_in_background():
                """Install packages in background thread"""
                try:
                    # Create clean environment
                    clean_env = os.environ.copy()
                    for key in ['PYTHONHOME', 'PYTHONPATH', 'PYTHONSTARTUP', 'VIRTUAL_ENV']:
                        clean_env.pop(key, None)

                    # Check if already installed
                    check_cmd = [self.venv_python, '-c', 'import torch, diffusers, ultralytics']
                    result = subprocess.run(check_cmd, capture_output=True, env=clean_env, timeout=30)

                    if result.returncode == 0:
                        # Already installed
                        QTimer.singleShot(100, self.check_pottery_ink_status)
                        return

                    # Essential packages for PotteryInk
                    essential_packages = [
                        'torch', 'torchvision',
                        'diffusers', 'transformers', 'peft',
                        'ultralytics'  # For YOLO
                    ]

                    self.log_message("Auto-installing PotteryInk dependencies in background...")

                    for package in essential_packages:
                        # Check if already installed
                        check_cmd = [self.venv_python, '-c', f'import {package}']
                        result = subprocess.run(check_cmd, capture_output=True, env=clean_env, timeout=5)

                        if result.returncode != 0:
                            # Install the package with progress logging
                            self.log_message(f"Installing {package}...")
                            install_cmd = [self.venv_python, '-m', 'pip', 'install', package, '--no-warn-script-location']
                            result = subprocess.run(install_cmd, capture_output=True, text=True, env=clean_env, timeout=300)
                            
                            if result.returncode == 0:
                                self.log_message(f"✓ {package} installed successfully")
                            else:
                                self.log_message(f"✗ Failed to install {package}: {result.stderr[:200]}", Qgis.Warning)
                        else:
                            self.log_message(f"✓ {package} already installed")

                    # After installation, reset the trigger flag and check status again
                    if hasattr(self, '_auto_install_triggered'):
                        self._auto_install_triggered = False
                    QTimer.singleShot(1000, self.check_pottery_ink_status)
                    self.log_message("✓ PotteryInk dependencies installed successfully")

                except Exception as e:
                    self.log_message(f"Background installation: {str(e)}", Qgis.Warning)
                    if hasattr(self, '_auto_install_triggered'):
                        self._auto_install_triggered = False

            # Run installation in background thread to not block UI
            thread = threading.Thread(target=install_in_background, daemon=True)
            thread.start()

        except Exception as e:
            self.log_message(f"Auto-install setup error: {str(e)}", Qgis.Warning)

    def install_venv_packages(self):
        """Install required packages in the virtual environment"""
        if not self.venv_python or not os.path.exists(self.venv_python):
            self.log_message("Virtual environment not available", Qgis.Warning)
            return False

        try:
            import subprocess

            # First check if packages are already installed
            self.log_message("Checking installed packages...")
            
            # Create clean environment without QGIS Python paths
            clean_env = os.environ.copy()
            # Remove QGIS-specific environment variables that interfere
            for key in ['PYTHONHOME', 'PYTHONPATH', 'PYTHONSTARTUP', 'VIRTUAL_ENV']:
                clean_env.pop(key, None)
            
            # Check core packages
            core_packages = ['ultralytics', 'torch', 'diffusers', 'transformers']
            all_installed = True
            
            for package in core_packages:
                check_cmd = [self.venv_python, '-c', f'import {package}']
                timeout = 30 if package in ['torch', 'ultralytics', 'diffusers'] else 10
                result = subprocess.run(check_cmd, capture_output=True, env=clean_env, timeout=timeout)
                if result.returncode != 0:
                    all_installed = False
                    break
            
            if all_installed:
                self.log_message("✓ All packages are already installed in virtual environment")
                self.check_pottery_ink_status()
                return True

            # Packages to install
            packages = [
                'torch', 'torchvision', 'ultralytics',  # YOLO
                'diffusers', 'transformers', 'peft',    # PotteryInk
                'scikit-image', 'scipy', 'opencv-python' # Image processing
            ]

            self.log_message("Installing missing packages in virtual environment...")
            self.progressBar.setRange(0, len(packages))

            for i, package in enumerate(packages):
                self.log_message(f"Installing {package}...")
                self.progressBar.setValue(i)

                cmd = [self.venv_python, '-m', 'pip', 'install', package]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, env=clean_env)

                if result.returncode == 0:
                    self.log_message(f"✓ {package} installed")
                else:
                    # Log only the error message, not the full path configuration
                    error_lines = result.stderr.split('\n')
                    for line in error_lines:
                        if 'ERROR:' in line or 'error:' in line.lower():
                            self.log_message(f"✗ {package} failed: {line}")
                            break
                    else:
                        self.log_message(f"✗ {package} failed")

                # Update UI
                from qgis.PyQt.QtCore import QCoreApplication
                QCoreApplication.processEvents()

            self.progressBar.setValue(len(packages))
            self.log_message("✓ Package installation complete")
            self.progressBar.setValue(0)
            
            # Update status after installation
            self.check_pottery_ink_status()
            return True

        except Exception as e:
            self.log_message(f"Package installation error: {str(e)}", Qgis.Warning)
            self.progressBar.setValue(0)
            return False

    def check_pottery_ink_status(self):
        """Check PotteryInk availability and status using virtual environment"""
        try:
            # Check if venv packages are available
            if self.venv_python and os.path.exists(self.venv_python):
                # Check if key packages are installed in venv
                import subprocess
                
                # Create clean environment
                clean_env = os.environ.copy()
                for key in ['PYTHONHOME', 'PYTHONPATH', 'PYTHONSTARTUP', 'VIRTUAL_ENV']:
                    clean_env.pop(key, None)
                
                # Check each dependency individually for better logging
                missing_deps = []
                deps_to_check = ['torch', 'torchvision', 'diffusers', 'transformers', 'peft', 'ultralytics']

                for dep in deps_to_check:
                    # Check cache first
                    cached_status = self.get_cached_status(dep)
                    if cached_status is not None:
                        if cached_status == 'missing':
                            missing_deps.append(dep)
                            self.log_message(f"⚠ Missing dependency: {dep} (cached)")
                        else:
                            self.log_message(f"✓ Found: {dep} {cached_status} (cached)")
                        continue
                    
                    # Not in cache, check normally
                    check_cmd = [self.venv_python, '-c', f'import {dep}; print({dep}.__version__)']
                    timeout = 30 if dep in ['torch', 'ultralytics', 'diffusers'] else 10
                    dep_result = subprocess.run(check_cmd, capture_output=True, text=True, env=clean_env, timeout=timeout)
                    if dep_result.returncode != 0:
                        missing_deps.append(dep)
                        self.log_message(f"⚠ Missing dependency: {dep}")
                        self.update_cache(dep, 'missing')
                    else:
                        version = dep_result.stdout.strip()
                        self.log_message(f"✓ Found: {dep} {version}")
                        self.update_cache(dep, version)

                # Quick check for torch and diffusers
                check_cmd = [self.venv_python, '-c',
                           'import torch, diffusers; print(f"torch:{torch.__version__},mps:{torch.backends.mps.is_available() if hasattr(torch.backends, "mps") else False}")']
                result = subprocess.run(check_cmd, capture_output=True, text=True, env=clean_env, timeout=10)

                # If no missing deps, consider it ready even if combined import fails
                if not missing_deps:
                    # Packages installed successfully
                    self.log_message("✓ All PotteryInk dependencies are installed")

                    # Update PotteryInk availability FIRST
                    from modules.utility import pottery_utilities
                    pottery_utilities.HAS_POTTERY_INK = True

                    # Re-initialize PotteryInk processor with venv Python
                    try:
                        # Force reload the module to get new methods
                        import importlib
                        import modules.utility.pottery_utilities as pu_module
                        importlib.reload(pu_module)
                        from modules.utility.pottery_utilities import PotteryInkProcessor
                        self.pottery_ink = PotteryInkProcessor(venv_python=self.venv_python)

                        # Device will be set by _setup_device() in the processor
                        device_name = str(self.pottery_ink.device).upper() if self.pottery_ink.device else 'DEFAULT'
                        self.log_message(f"✓ PotteryInk processor initialized with {device_name} device")
                    except Exception as e:
                        self.log_message(f"Warning: Could not reinitialize processor: {e}")

                    # Now update UI
                    if hasattr(self, 'label_pottery_ink_status'):
                        # Parse the output if torch/diffusers import succeeded
                        if result.returncode == 0:
                            output = result.stdout.strip()
                            if 'torch:' in output:
                                version_info = output.split(',')
                                torch_version = version_info[0].split(':')[1] if ':' in version_info[0] else 'unknown'
                                has_mps = 'mps:True' in output

                                device = "MPS (Apple Silicon)" if has_mps else "CPU"
                                self.label_pottery_ink_status.setText(f"✓ Ready - PyTorch {torch_version} - {device}")
                                self.label_pottery_ink_status.setStyleSheet("color: green; font-weight: bold;")
                                self.log_message(f"✓ PotteryInk ready - {device}")
                            else:
                                self.label_pottery_ink_status.setText("✓ Ready")
                                self.label_pottery_ink_status.setStyleSheet("color: green; font-weight: bold;")
                                self.log_message("✓ PotteryInk ready")
                        else:
                            # Dependencies installed but import had issues
                            self.label_pottery_ink_status.setText("✓ Dependencies installed")
                            self.label_pottery_ink_status.setStyleSheet("color: green; font-weight: bold;")
                            self.log_message("✓ Dependencies installed (import test had warnings)")

                    # Enable PotteryInk controls
                    if hasattr(self, 'btn_pottery_ink_enhance'):
                        self.btn_pottery_ink_enhance.setEnabled(True)
                    if hasattr(self, 'btn_pottery_ink_download_model'):
                        self.btn_pottery_ink_download_model.setEnabled(True)

                elif not hasattr(self, '_auto_install_triggered'):
                    # Packages not installed - install them automatically (only once)
                    self._auto_install_triggered = True
                    if hasattr(self, 'label_pottery_ink_status'):
                        self.label_pottery_ink_status.setText("Installing dependencies...")
                        self.label_pottery_ink_status.setStyleSheet("color: orange; font-weight: bold;")

                    # Auto-install packages without user interaction
                    QTimer.singleShot(100, self.auto_install_packages)

                else:
                    # Already tried to install, show what's missing
                    if hasattr(self, 'label_pottery_ink_status'):
                        if missing_deps:
                            self.label_pottery_ink_status.setText(f"⚠ Missing: {', '.join(missing_deps)}")
                            self.log_message(f"Missing dependencies: {', '.join(missing_deps)}")
                        else:
                            # No missing deps but torch/diffusers check failed - might be import error
                            self.label_pottery_ink_status.setText("⚠ Import check failed - restarting may help")
                            self.log_message(f"Dependencies installed but import failed: {result.stderr[:100] if result.stderr else 'unknown error'}")
                        self.label_pottery_ink_status.setStyleSheet("color: orange; font-weight: bold;")
            else:
                # Venv not found - create it
                if hasattr(self, 'label_pottery_ink_status'):
                    self.label_pottery_ink_status.setText("Setting up environment...")
                    self.label_pottery_ink_status.setStyleSheet("color: orange; font-weight: bold;")
                
                # Setup venv automatically
                self.setup_pottery_venv()

        except Exception as e:
            self.log_message(f"Status check error: {str(e)}", Qgis.Warning)
            if hasattr(self, 'label_pottery_ink_status'):
                self.label_pottery_ink_status.setText("⚠ Check failed")
                self.label_pottery_ink_status.setStyleSheet("color: orange;")

    def setup_database(self):
        """Setup database connection"""
        try:
            conn = Connection()
            conn_str = conn.conn_str()

            try:
                self.DB_MANAGER = get_db_manager(conn_str, use_singleton=True)
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

        # PotteryInk Integration (check if controls exist)
        if hasattr(self, 'checkBox_pottery_ink'):
            self.checkBox_pottery_ink.toggled.connect(self.toggle_pottery_ink_options)
        if hasattr(self, 'pushButton_download_ink_models'):
            self.pushButton_download_ink_models.clicked.connect(self.download_pottery_ink_models)
        if hasattr(self, 'pushButton_batch_enhance'):
            self.pushButton_batch_enhance.clicked.connect(self.batch_enhance_dialog)
        if hasattr(self, 'pushButton_install_venv_packages'):
            self.pushButton_install_venv_packages.clicked.connect(self.install_venv_packages)

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
        self.create_pottery_ink_ui()  # Create PotteryInk UI dynamically
        # Note: check_pottery_ink_status() will be called from setup_external_python()

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

    # PotteryInk Integration Methods
    def enhance_single_pottery_card(self, card_path: str) -> str:
        """Enhance a single pottery card using PotteryInk"""
        if not self.pottery_ink.is_available():
            self.log_message("PotteryInk not available for enhancement", Qgis.Warning)
            return card_path

        try:
            # Create enhanced version path
            base_dir = os.path.dirname(card_path)
            base_name = os.path.splitext(os.path.basename(card_path))[0]
            enhanced_path = os.path.join(base_dir, f"enhanced_{base_name}.png")

            # Apply PotteryInk enhancement
            if self.pottery_ink.enhance_drawing(card_path, enhanced_path):
                self.log_message(f"✓ Enhanced with PotteryInk: {os.path.basename(enhanced_path)}")
                return enhanced_path
            else:
                self.log_message("⚠ PotteryInk enhancement failed", Qgis.Warning)
                return card_path

        except Exception as e:
            self.log_message(f"PotteryInk enhancement error: {str(e)}", Qgis.Warning)
            return card_path

    def batch_enhance_with_pottery_ink(self, image_folder: str, output_folder: str):
        """Batch enhance images using PotteryInk"""
        if not self.pottery_ink.is_available():
            QMessageBox.warning(self, "Warning", "PotteryInk not available. Please install dependencies.")
            return

        try:
            # Show progress dialog for batch processing
            from qgis.PyQt.QtWidgets import QProgressDialog
            from qgis.PyQt.QtCore import Qt

            progress = QProgressDialog("Enhancing drawings with PotteryInk...", "Cancel", 0, 100, self)
            progress.setWindowModality(Qt.WindowModal)
            progress.show()

            def progress_callback(current, total, message):
                progress.setValue(int((current / total) * 100))
                progress.setLabelText(message)
                from qgis.PyQt.QtCore import QCoreApplication
                QCoreApplication.processEvents()
                if progress.wasCanceled():
                    return False
                return True

            # Use default model path (you might want to add UI for this)
            model_path = os.path.join(os.path.expanduser("~"), "pyarchinit", "bin", "pottery_ink_model.pkl")

            # Process images
            results = self.pottery_ink.batch_process(
                image_folder, output_folder, model_path,
                progress_callback=progress_callback
            )

            progress.close()

            if results['success']:
                QMessageBox.information(
                    self, "Success",
                    f"Enhanced {results['processed']} images\n"
                    f"Failed: {results['failed']}\n"
                    f"Output folder: {output_folder}"
                )
                self.log_message(f"✓ Batch enhancement completed: {results['processed']} images")
            else:
                QMessageBox.warning(self, "Error", f"Batch processing failed: {results.get('error', 'Unknown error')}")

        except Exception as e:
            self.log_message(f"Batch enhancement error: {str(e)}", Qgis.Warning)
            QMessageBox.critical(self, "Error", f"Batch enhancement failed:\n{str(e)}")

    def download_pottery_ink_models(self):
        """Download PotteryInk models from HuggingFace"""
        try:
            # Create models directory in the correct location
            models_dir = os.path.join(os.path.expanduser("~"), "pyarchinit", "bin", "models")
            os.makedirs(models_dir, exist_ok=True)

            self.log_message("Downloading PotteryInk models...")

            # Model URLs from PyPotteryInk repository
            models = {
                "10k Model (General)": {
                    "url": "https://huggingface.co/lrncrd/PyPotteryInk/resolve/main/model_10k.pkl?download=true",
                    "filename": "model_10k.pkl"
                },
                "6h-MCG Model (Bronze Age)": {
                    "url": "https://huggingface.co/lrncrd/PyPotteryInk/resolve/main/6h-MCG.pkl?download=true",
                    "filename": "6h-MCG.pkl"
                },
                "6h-MC Model (Protohistoric)": {
                    "url": "https://huggingface.co/lrncrd/PyPotteryInk/resolve/main/6h-MC.pkl?download=true",
                    "filename": "6h-MC.pkl"
                },
                "4h-PAINT Model (Historic/Painted)": {
                    "url": "https://huggingface.co/lrncrd/PyPotteryInk/resolve/main/4h-PAINT.pkl?download=true",
                    "filename": "4h-PAINT.pkl"
                }
            }

            # Get selected model from combo box
            selected_model = self.combo_pottery_ink_model.currentText() if hasattr(self, 'combo_pottery_ink_model') else "10k Model (General)"

            # Log for debugging
            self.log_message(f"Selected model: '{selected_model}'")
            self.log_message(f"Available models: {list(models.keys())}")

            if selected_model in models:
                model_info = models[selected_model]
                model_url = model_info["url"]
                model_path = os.path.join(models_dir, model_info["filename"])

                # Check if already exists
                if os.path.exists(model_path):
                    reply = QMessageBox.question(
                        self,
                        "Model Exists",
                        f"Model {model_info['filename']} already exists.\nDownload again?",
                        QMessageBox.Yes | QMessageBox.No
                    )
                    if reply == QMessageBox.No:
                        return

                self.progressBar.setRange(0, 0)  # Indeterminate progress
                self.log_message(f"Downloading {selected_model}...")

                # Download model
                import urllib.request
                urllib.request.urlretrieve(model_url, model_path)

                self.progressBar.setRange(0, 100)
                self.progressBar.setValue(100)

                self.log_message(f"✓ Downloaded {model_info['filename']} to: {models_dir}")
                QMessageBox.information(
                    self,
                    "Download Complete",
                    f"Model downloaded successfully!\n\nModel: {selected_model}\nLocation: {model_path}"
                )
            else:
                QMessageBox.warning(self, "Error", "Please select a model to download")

        except Exception as e:
            self.log_message(f"Model download error: {str(e)}", Qgis.Warning)
            QMessageBox.critical(self, "Error", f"Failed to download model:\n{str(e)}")
        finally:
            self.progressBar.setValue(0)

    def toggle_pottery_ink_options(self, checked):
        """Toggle PotteryInk options based on checkbox state"""
        # Enable/disable PotteryInk-related controls
        if hasattr(self, 'groupBox_pottery_ink'):
            self.groupBox_pottery_ink.setEnabled(checked)

        if checked and not self.pottery_ink.is_available():
            QMessageBox.information(
                self,
                "PotteryInk Setup",
                "PotteryInk requires additional packages.\n"
                "Click 'Install Packages' to set them up in the virtual environment."
            )

    def batch_enhance_dialog(self):
        """Show dialog for batch enhancement with PotteryInk"""
        # Select input folder
        input_folder = QFileDialog.getExistingDirectory(
            self,
            "Select Input Folder",
            os.path.expanduser("~"),
            QFileDialog.ShowDirsOnly
        )

        if not input_folder:
            return

        # Select output folder
        output_folder = QFileDialog.getExistingDirectory(
            self,
            "Select Output Folder",
            input_folder,
            QFileDialog.ShowDirsOnly
        )

        if not output_folder:
            return

        # Run batch enhancement
        self.batch_enhance_with_pottery_ink(input_folder, output_folder)

    def create_pottery_ink_ui(self):
        """Dynamically create complete PotteryInk tab with all features"""
        try:
            # Check if PotteryInk tab already exists
            if hasattr(self, 'tab_pottery_ink'):
                return

            from qgis.PyQt.QtWidgets import (QWidget, QGroupBox, QVBoxLayout, QHBoxLayout,
                                             QCheckBox, QPushButton, QLabel, QComboBox,
                                             QSpinBox, QTextEdit, QSplitter, QListWidget,
                                             QRadioButton, QSlider, QButtonGroup, QProgressBar)
            from qgis.PyQt.QtCore import Qt

            # Create new tab for PotteryInk
            self.tab_pottery_ink = QWidget()
            self.tab_pottery_ink.setObjectName("tab_pottery_ink")

            # Main layout for the tab
            main_layout = QVBoxLayout(self.tab_pottery_ink)

            # === Status Bar ===
            status_group = QGroupBox("PotteryInk Status")
            status_layout = QVBoxLayout()

            # Status label with better formatting
            self.label_pottery_ink_status = QLabel("Checking status...")
            self.label_pottery_ink_status.setStyleSheet("font-weight: bold; font-size: 12pt;")
            status_layout.addWidget(self.label_pottery_ink_status)

            # Progress bar for operations
            self.pottery_ink_progress = QProgressBar()
            self.pottery_ink_progress.setVisible(False)
            status_layout.addWidget(self.pottery_ink_progress)

            status_group.setLayout(status_layout)
            main_layout.addWidget(status_group)

            # === Input Source Selection ===
            source_group = QGroupBox("Input Source")
            source_layout = QVBoxLayout()

            # Radio buttons for source selection
            self.radio_pottery_lens = QRadioButton("Use PotteryLens processed images")
            self.radio_pottery_lens.setChecked(True)
            self.radio_external_files = QRadioButton("Load external images")
            self.radio_batch_folder = QRadioButton("Batch process folder")

            source_layout.addWidget(self.radio_pottery_lens)
            source_layout.addWidget(self.radio_external_files)
            source_layout.addWidget(self.radio_batch_folder)

            source_group.setLayout(source_layout)
            main_layout.addWidget(source_group)

            # === Model and Settings ===
            settings_group = QGroupBox("Enhancement Settings")
            settings_layout = QVBoxLayout()

            # Model selection
            model_row = QHBoxLayout()
            model_row.addWidget(QLabel("Model:"))
            self.combo_pottery_ink_model = QComboBox()
            self.combo_pottery_ink_model.addItems([
                "10k Model (General)",
                "6h-MCG Model (Bronze Age)",
                "6h-MC Model (Protohistoric)",
                "4h-PAINT Model (Historic/Painted)"
            ])
            model_row.addWidget(self.combo_pottery_ink_model)

            self.btn_download_model = QPushButton("Download")
            self.btn_download_model.clicked.connect(self.download_pottery_ink_models)
            model_row.addWidget(self.btn_download_model)
            settings_layout.addLayout(model_row)

            # Enhancement parameters
            param_row = QHBoxLayout()

            # Patch size
            param_row.addWidget(QLabel("Patch Size:"))
            self.spin_patch_size = QSpinBox()
            self.spin_patch_size.setRange(256, 1024)
            self.spin_patch_size.setSingleStep(128)
            self.spin_patch_size.setValue(512)
            self.spin_patch_size.setToolTip("Larger = better quality but slower")
            param_row.addWidget(self.spin_patch_size)

            # Overlap
            param_row.addWidget(QLabel("Overlap:"))
            self.spin_overlap = QSpinBox()
            self.spin_overlap.setRange(0, 128)
            self.spin_overlap.setValue(64)
            self.spin_overlap.setToolTip("Overlap between patches to reduce seams")
            param_row.addWidget(self.spin_overlap)

            # Stippling control
            param_row.addWidget(QLabel("Stippling:"))
            self.slider_stippling = QSlider(Qt.Horizontal)
            self.slider_stippling.setRange(0, 100)
            self.slider_stippling.setValue(50)
            self.slider_stippling.setToolTip("Control dot pattern density")
            param_row.addWidget(self.slider_stippling)

            settings_layout.addLayout(param_row)

            # Processing options
            options_row = QHBoxLayout()
            self.check_preprocessing = QCheckBox("Preprocessing")
            self.check_preprocessing.setChecked(True)
            self.check_preprocessing.setToolTip("Apply automatic brightness/contrast adjustment")
            self.check_high_res = QCheckBox("High Resolution")
            self.check_element_extraction = QCheckBox("Extract Elements")
            self.check_svg_export = QCheckBox("Export as SVG")

            options_row.addWidget(self.check_preprocessing)
            options_row.addWidget(self.check_high_res)
            options_row.addWidget(self.check_element_extraction)
            options_row.addWidget(self.check_svg_export)
            settings_layout.addLayout(options_row)

            # Preprocessing parameters (shown when preprocessing is enabled)
            preprocess_row = QHBoxLayout()
            preprocess_row.addWidget(QLabel("Preprocessing:"))

            self.check_auto_brightness = QCheckBox("Auto Brightness")
            self.check_auto_brightness.setChecked(True)
            preprocess_row.addWidget(self.check_auto_brightness)

            self.check_auto_contrast = QCheckBox("Auto Contrast")
            self.check_auto_contrast.setChecked(True)
            preprocess_row.addWidget(self.check_auto_contrast)

            self.check_histogram_eq = QCheckBox("Histogram Eq.")
            self.check_histogram_eq.setChecked(True)
            preprocess_row.addWidget(self.check_histogram_eq)

            settings_layout.addLayout(preprocess_row)

            # Connect preprocessing checkbox to show/hide options
            self.check_preprocessing.toggled.connect(lambda checked: [
                self.check_auto_brightness.setEnabled(checked),
                self.check_auto_contrast.setEnabled(checked),
                self.check_histogram_eq.setEnabled(checked)
            ])

            settings_group.setLayout(settings_layout)
            main_layout.addWidget(settings_group)

            # === File Lists with Splitter ===
            splitter = QSplitter(Qt.Horizontal)

            # Input files
            input_group = QGroupBox("Input Images")
            input_layout = QVBoxLayout()

            self.list_pottery_ink_input = QListWidget()
            self.list_pottery_ink_input.setSelectionMode(QListWidget.ExtendedSelection)
            input_layout.addWidget(self.list_pottery_ink_input)

            input_buttons = QHBoxLayout()
            self.btn_add_files = QPushButton("Add Files")
            self.btn_add_files.clicked.connect(self.add_pottery_ink_files)
            self.btn_from_pottery_lens = QPushButton("From PotteryLens")
            self.btn_from_pottery_lens.clicked.connect(self.load_from_pottery_lens)
            self.btn_clear_input = QPushButton("Clear")
            self.btn_clear_input.clicked.connect(self.clear_pottery_ink_input)

            input_buttons.addWidget(self.btn_add_files)
            input_buttons.addWidget(self.btn_from_pottery_lens)
            input_buttons.addWidget(self.btn_clear_input)
            input_layout.addLayout(input_buttons)

            input_group.setLayout(input_layout)
            splitter.addWidget(input_group)

            # Output files
            output_group = QGroupBox("Enhanced Results")
            output_layout = QVBoxLayout()

            self.list_pottery_ink_output = QListWidget()
            self.list_pottery_ink_output.setSelectionMode(QListWidget.ExtendedSelection)
            output_layout.addWidget(self.list_pottery_ink_output)

            output_buttons = QHBoxLayout()
            self.btn_save_results = QPushButton("Save Selected")
            self.btn_save_results.clicked.connect(self.save_pottery_ink_results)
            self.btn_to_layout = QPushButton("To Layout")
            self.btn_to_layout.clicked.connect(self.send_to_layout)
            self.btn_clear_output = QPushButton("Clear")
            self.btn_clear_output.clicked.connect(lambda: self.list_pottery_ink_output.clear())

            output_buttons.addWidget(self.btn_save_results)
            output_buttons.addWidget(self.btn_to_layout)
            output_buttons.addWidget(self.btn_clear_output)
            output_layout.addLayout(output_buttons)

            output_group.setLayout(output_layout)
            splitter.addWidget(output_group)

            main_layout.addWidget(splitter)

            # === Process Buttons ===
            process_layout = QHBoxLayout()
            process_layout.addStretch()

            # Enhance button
            self.btn_pottery_ink_enhance = QPushButton("🎨 Enhance with PotteryInk")
            self.btn_pottery_ink_enhance.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    font-weight: bold;
                    font-size: 14pt;
                    padding: 10px 20px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            self.btn_pottery_ink_enhance.clicked.connect(self.run_pottery_ink_enhancement)
            process_layout.addWidget(self.btn_pottery_ink_enhance)

            # Diagnostic button
            self.btn_pottery_ink_diagnostic = QPushButton("🔍 Run Diagnostic")
            self.btn_pottery_ink_diagnostic.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    font-weight: bold;
                    font-size: 12pt;
                    padding: 10px 15px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
            """)
            self.btn_pottery_ink_diagnostic.clicked.connect(self.run_pottery_ink_diagnostic)
            process_layout.addWidget(self.btn_pottery_ink_diagnostic)

            process_layout.addStretch()
            main_layout.addLayout(process_layout)

            # === Log Area ===
            self.text_pottery_log = QTextEdit()
            self.text_pottery_log.setReadOnly(True)
            self.text_pottery_log.setMaximumHeight(100)
            main_layout.addWidget(self.text_pottery_log)

            # Add the new tab to the main tab widget
            if hasattr(self, 'tabWidget_main'):
                self.tabWidget_main.addTab(self.tab_pottery_ink, "🏺 PotteryInk")

            # Note: Status will be checked once from setup_external_python()
            self.log_message("✓ PotteryInk tab created successfully")

        except Exception as e:
            self.log_message(f"Error creating PotteryInk UI: {str(e)}", Qgis.Warning)

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
        """Setup external Python using virtual environment only"""
        try:
            # Only use virtual environment, no external Python search
            if self.venv_python and os.path.exists(self.venv_python):
                self.external_python = self.venv_python
                self.log_message(f"✓ Using virtual environment: {self.venv_path}")

                # Check if packages need to be installed
                # Disabled the prompt - packages will be checked/installed automatically by check_pottery_ink_status()
                # if hasattr(self, 'need_venv_packages') and self.need_venv_packages:
                #     reply = QMessageBox.question(...)
                #     ...installation logic...

                # Now that venv is ready, detect GPU capabilities
                self.has_gpu = self.detect_gpu()
                
                # Just log that we're using the virtual environment
                self.log_message("✓ Virtual environment packages ready")

            else:
                # Virtual environment not available - disable functionality gracefully
                self.log_message("⚠ Virtual environment not found. Pottery Tools will work with limited functionality.", Qgis.Warning)
                self.external_python = None
                self.venv_python = None

        except Exception as e:
            self.log_message(f"Error setting up virtual environment: {str(e)}", Qgis.Warning)

    def check_ultralytics_async(self):
        """Check if ultralytics is installed in virtual environment (non-blocking)"""
        # This function is no longer needed since we check packages in setup_pottery_venv
        pass

    def detect_gpu(self):
        """Detect if GPU is available for YOLO inference using virtual environment"""
        if not self.venv_python or not os.path.exists(self.venv_python):
            self.log_message("No virtual environment available for GPU detection")
            return False
            
        try:
            import subprocess
            
            # Check for CUDA and MPS using virtual environment
            check_cmd = [
                self.venv_python, '-c',
                '''
import torch
import platform
print("CUDA_AVAILABLE:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("CUDA_DEVICE:", torch.cuda.get_device_name(0))
    
print("MPS_AVAILABLE:", hasattr(torch.backends, "mps") and torch.backends.mps.is_available())
print("PLATFORM:", platform.system())
'''
            ]
            
            result = subprocess.run(check_cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                output = result.stdout
                
                if "CUDA_AVAILABLE: True" in output:
                    # Extract device name
                    for line in output.split('\n'):
                        if line.startswith("CUDA_DEVICE:"):
                            device_name = line.split(":", 1)[1].strip()
                            self.log_message(f"✓ CUDA GPU detected: {device_name}")
                            return True
                
                if "MPS_AVAILABLE: True" in output and "PLATFORM: Darwin" in output:
                    self.log_message("✓ Apple Metal Performance Shaders (MPS) detected")
                    return True
                    
        except Exception as e:
            self.log_message(f"GPU detection error: {e}")

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
            # If we don't have a working virtual environment, try to install ultralytics
            if not self.venv_python or not os.path.exists(self.venv_python):
                self.log_message("No virtual environment available, checking system Python...", Qgis.Warning)
                # Try to find or install ultralytics in system Python
                python_exe = self.find_python_executable()
                if python_exe:
                    self.external_python = python_exe
                    self.log_message(f"Using system Python: {python_exe}")
                else:
                    self.log_message("Could not find suitable Python with ultralytics", Qgis.Warning)
                    return
            
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

            # PotteryInk and YOLO requirements
            required_packages = [
                'torch', 'torchvision', 'ultralytics',  # YOLO requirements
                'diffusers', 'transformers', 'peft',     # PotteryInk AI requirements
                'scikit-image', 'seaborn', 'scipy'       # PotteryInk image processing
            ]

            for package in required_packages:
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
            use_pottery_ink = getattr(self, 'checkBox_pottery_ink', None) and self.checkBox_pottery_ink.isChecked()

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

                # Apply PotteryInk enhancement if enabled
                if use_pottery_ink and self.pottery_ink.is_available():
                    try:
                        # Save temporary image for PotteryInk processing
                        temp_path = os.path.join(processed_dir, f"temp_{idx}.png")
                        img.save(temp_path, "PNG")

                        # Apply PotteryInk enhancement
                        enhanced_filename = f"pottery_ink_{idx:04d}_{pottery_type}.png"
                        enhanced_path = os.path.join(processed_dir, enhanced_filename)

                        if self.pottery_ink.enhance_drawing(temp_path, enhanced_path):
                            self.log_message(f"✓ PotteryInk enhanced: {enhanced_filename}")
                            processed_path = enhanced_path
                        else:
                            self.log_message(f"⚠ PotteryInk failed, using standard: {idx}")
                            processed_filename = f"pottery_proc_{idx:04d}_{pottery_type}.png"
                            processed_path = os.path.join(processed_dir, processed_filename)
                            img.save(processed_path, "PNG")

                        # Clean up temp file
                        if os.path.exists(temp_path):
                            os.remove(temp_path)

                    except Exception as e:
                        self.log_message(f"PotteryInk error on item {idx}: {str(e)}", Qgis.Warning)
                        processed_filename = f"pottery_proc_{idx:04d}_{pottery_type}.png"
                        processed_path = os.path.join(processed_dir, processed_filename)
                        img.save(processed_path, "PNG")
                else:
                    # Save standard processed image
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

    def load_from_pottery_lens(self):
        """Load processed images from PotteryLens"""
        try:
            # Check if we have processed cards from PotteryLens
            if hasattr(self, 'processed_cards') and self.processed_cards:
                for card in self.processed_cards:
                    if os.path.exists(card['path']):
                        item = QListWidgetItem(os.path.basename(card['path']))
                        item.setData(Qt.UserRole, card['path'])

                        # Create thumbnail
                        pixmap = QPixmap(card['path'])
                        if not pixmap.isNull():
                            pixmap = pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                            item.setIcon(QIcon(pixmap))

                        self.list_pottery_ink_input.addItem(item)

                self.text_pottery_log.append(f"Loaded {len(self.processed_cards)} images from PotteryLens")
            else:
                QMessageBox.information(self, "No PotteryLens Images",
                                      "No processed images from PotteryLens.\n"
                                      "Please process images with YOLO first.")
        except Exception as e:
            self.log_message(f"Error loading PotteryLens images: {str(e)}", Qgis.Warning)

    def clear_pottery_ink_input(self):
        """Clear input list"""
        self.list_pottery_ink_input.clear()
        self.text_pottery_log.append("Input list cleared")

    def send_to_layout(self):
        """Send enhanced images to layout creator"""
        try:
            output_count = self.list_pottery_ink_output.count()
            if output_count == 0:
                QMessageBox.warning(self, "No Results", "No enhanced images to send to layout.")
                return

            # Clear and add to layout images
            self.extracted_images = []
            for i in range(output_count):
                item = self.list_pottery_ink_output.item(i)
                image_path = item.data(Qt.UserRole)
                if image_path and os.path.exists(image_path):
                    self.extracted_images.append(image_path)

            # Switch to layout tab
            self.tabWidget_main.setCurrentIndex(1)

            self.text_pottery_log.append(f"Sent {len(self.extracted_images)} images to layout")

        except Exception as e:
            self.log_message(f"Error sending to layout: {str(e)}", Qgis.Warning)

    # PotteryInk Tab Methods
    def add_pottery_ink_files(self):
        """Add files to PotteryInk processing queue"""
        try:
            files, _ = QFileDialog.getOpenFileNames(
                self,
                "Select Pottery Images",
                "",
                "Images (*.png *.jpg *.jpeg *.bmp *.tiff)"
            )

            if files:
                for file_path in files:
                    if os.path.exists(file_path):
                        # Add to list widget
                        item = QListWidgetItem(os.path.basename(file_path))
                        item.setData(Qt.UserRole, file_path)
                        
                        # Create thumbnail
                        pixmap = QPixmap(file_path)
                        if not pixmap.isNull():
                            pixmap = pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                            item.setIcon(QIcon(pixmap))
                        
                        self.list_pottery_ink_input.addItem(item)
                
                self.text_pottery_log.append(f"Added {len(files)} files for enhancement")
                
        except Exception as e:
            self.log_message(f"Error adding files: {str(e)}", Qgis.Warning)
            QMessageBox.warning(self, "Error", f"Failed to add files:\n{str(e)}")

    def clear_pottery_ink_files(self):
        """Clear all files from PotteryInk input list"""
        self.list_pottery_ink_input.clear()
        self.list_pottery_ink_output.clear()
        self.text_pottery_log.append("Cleared all files")

    def run_pottery_ink_enhancement(self):
        """Run PotteryInk AI enhancement on selected files"""
        try:
            # Re-check PotteryInk availability with venv
            if self.venv_python and os.path.exists(self.venv_python):
                # Test if we can import dependencies using venv
                import subprocess
                clean_env = os.environ.copy()
                for key in ['PYTHONHOME', 'PYTHONPATH', 'PYTHONSTARTUP', 'VIRTUAL_ENV']:
                    clean_env.pop(key, None)

                test_cmd = [self.venv_python, '-c', 'import torch, diffusers; print("OK")']
                test_result = subprocess.run(test_cmd, capture_output=True, text=True, env=clean_env, timeout=5)

                if test_result.returncode != 0:
                    QMessageBox.warning(
                        self,
                        "PotteryInk Not Available",
                        "PotteryInk dependencies are not installed.\n"
                        "Click 'Install Dependencies' to set them up."
                    )
                    return

                # Dependencies are available, continue
                self.log_message("✓ PotteryInk dependencies verified")

                # Re-initialize PotteryInk processor with venv to ensure it's ready
                # Force reload the module to get new methods
                import importlib
                import modules.utility.pottery_utilities as pu_module
                importlib.reload(pu_module)
                from modules.utility.pottery_utilities import PotteryInkProcessor
                self.pottery_ink = PotteryInkProcessor(venv_python=self.venv_python)
                self.log_message("✓ PotteryInk processor initialized")
            else:
                QMessageBox.warning(
                    self,
                    "Virtual Environment Not Found",
                    "The pottery virtual environment is not set up. Please restart Pottery Tools."
                )
                return

            # Get input files
            input_count = self.list_pottery_ink_input.count()
            if input_count == 0:
                QMessageBox.warning(self, "No Files", "Please add files to enhance.")
                return

            # Get selected model
            model_name = (self.combo_pottery_ink_model.currentText()
                          if hasattr(self, 'combo_pottery_ink_model')
                          else "10k Model (General)")
            
            # Create output directory
            output_dir = os.path.join(os.path.expanduser("~"), "pyarchinit", "pottery_ink_output")
            os.makedirs(output_dir, exist_ok=True)

            self.text_pottery_log.append(f"\nStarting enhancement with {model_name}...")
            self.progressBar.setRange(0, input_count)
            
            # Process each file
            for i in range(input_count):
                item = self.list_pottery_ink_input.item(i)
                input_path = item.data(Qt.UserRole)
                
                if input_path and os.path.exists(input_path):
                    try:
                        # Generate output filename
                        base_name = os.path.splitext(os.path.basename(input_path))[0]
                        output_path = os.path.join(output_dir, f"{base_name}_enhanced.png")
                        
                        # Get processing options
                        apply_preprocessing = self.check_preprocessing.isChecked() if hasattr(self, 'check_preprocessing') else True
                        high_res = self.check_high_res.isChecked() if hasattr(self, 'check_high_res') else False
                        extract_elements = self.check_element_extraction.isChecked() if hasattr(self, 'check_element_extraction') else False
                        export_svg = self.check_svg_export.isChecked() if hasattr(self, 'check_svg_export') else False
                        patch_size = self.spin_patch_size.value() if hasattr(self, 'spin_patch_size') else 512
                        overlap = self.spin_overlap.value() if hasattr(self, 'spin_overlap') else 64
                        stippling = self.slider_stippling.value() / 100.0 if hasattr(self, 'slider_stippling') else 1.0

                        # Run enhancement
                        self.text_pottery_log.append(f"Enhancing: {os.path.basename(input_path)}")
                        self.text_pottery_log.append(f"  Options: Preprocessing={apply_preprocessing}, High-res={high_res}, Extract={extract_elements}, SVG={export_svg}")
                        self.text_pottery_log.append(f"  Parameters: Patch={patch_size}, Overlap={overlap}, Stippling={stippling}")

                        # Call enhancement with parameters
                        self.log_message(f"Processing with preprocessing={apply_preprocessing}, high_res={high_res}, extract={extract_elements}, svg={export_svg}")

                        # Use high-resolution processing if enabled
                        if high_res:
                            self.log_message("Using high-resolution patch-based processing...")
                            success = self.pottery_ink.enhance_high_res(
                                input_path,
                                output_path,
                                patch_size=patch_size,
                                overlap=overlap,
                                contrast_scale=stippling,
                                apply_preprocessing=apply_preprocessing
                            )
                        else:
                            success = self.pottery_ink.enhance_drawing(
                                input_path,
                                output_path,
                                contrast_scale=stippling,
                                patch_size=patch_size,
                                overlap=overlap,
                                apply_preprocessing=apply_preprocessing
                            )
                        self.log_message(f"Processing returned: {success}")

                        if success:
                            # Add to output list
                            output_item = QListWidgetItem(os.path.basename(output_path))
                            output_item.setData(Qt.UserRole, output_path)

                            # Create thumbnail
                            pixmap = QPixmap(output_path)
                            if not pixmap.isNull():
                                pixmap = pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                                output_item.setIcon(QIcon(pixmap))

                            self.list_pottery_ink_output.addItem(output_item)
                            self.text_pottery_log.append(f"  ✓ Enhanced successfully")

                            # Extract elements if requested
                            if extract_elements:
                                self.text_pottery_log.append(f"  Extracting elements...")
                                elements_dir = os.path.join(output_dir, "elements")
                                os.makedirs(elements_dir, exist_ok=True)
                                elements = self.pottery_ink.extract_elements(output_path, elements_dir)
                                if elements:
                                    self.text_pottery_log.append(f"    ✓ Extracted {len(elements)} elements")
                                else:
                                    self.text_pottery_log.append(f"    ⚠ No elements extracted")

                            # Export to SVG if requested
                            if export_svg:
                                self.text_pottery_log.append(f"  Converting to SVG...")
                                svg_path = output_path.replace('.png', '.svg')
                                if self.pottery_ink.export_to_svg(output_path, svg_path):
                                    self.text_pottery_log.append(f"    ✓ SVG saved: {os.path.basename(svg_path)}")
                                else:
                                    self.text_pottery_log.append(f"    ⚠ SVG conversion failed")

                        else:
                            self.text_pottery_log.append(f"  ✗ Enhancement failed - check dependencies")
                            
                    except Exception as e:
                        self.text_pottery_log.append(f"  ✗ Error: {str(e)}")
                
                self.progressBar.setValue(i + 1)
                QApplication.processEvents()  # Keep UI responsive
            
            self.progressBar.setValue(0)
            self.text_pottery_log.append(f"\nEnhancement complete! Output saved to:\n{output_dir}")
            
            QMessageBox.information(
                self,
                "Enhancement Complete",
                f"Enhanced {self.list_pottery_ink_output.count()} images.\n"
                f"Results saved to:\n{output_dir}"
            )
            
        except Exception as e:
            self.log_message(f"Error during enhancement: {str(e)}", Qgis.Critical)
            self.text_pottery_log.append(f"\n✗ Enhancement error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Enhancement failed:\n{str(e)}")
        finally:
            self.progressBar.setValue(0)

    def save_pottery_ink_results(self):
        """Save enhanced results to a specified folder"""
        try:
            output_count = self.list_pottery_ink_output.count()
            if output_count == 0:
                QMessageBox.warning(self, "No Results", "No enhanced images to save.")
                return

            # Select output folder
            output_folder = QFileDialog.getExistingDirectory(
                self,
                "Select Output Folder",
                os.path.expanduser("~")
            )

            if output_folder:
                copied = 0
                for i in range(output_count):
                    item = self.list_pottery_ink_output.item(i)
                    source_path = item.data(Qt.UserRole)
                    
                    if source_path and os.path.exists(source_path):
                        dest_path = os.path.join(output_folder, os.path.basename(source_path))
                        shutil.copy2(source_path, dest_path)
                        copied += 1
                
                self.text_pottery_log.append(f"\n✓ Saved {copied} enhanced images to:\n{output_folder}")
                QMessageBox.information(self, "Success", f"Saved {copied} images to:\n{output_folder}")
                
        except Exception as e:
            self.log_message(f"Error saving results: {str(e)}", Qgis.Warning)
            QMessageBox.warning(self, "Error", f"Failed to save results:\n{str(e)}")

    def run_pottery_ink_diagnostic(self):
        """Run diagnostic analysis on selected images"""
        try:
            # Check if processor is available
            if not self.pottery_ink or not self.pottery_ink.is_available():
                QMessageBox.warning(
                    self,
                    "PotteryInk Not Available",
                    "Please ensure PotteryInk dependencies are installed."
                )
                return

            # Get selected files
            input_count = self.list_pottery_ink_input.count()
            if input_count == 0:
                QMessageBox.warning(self, "No Files", "Please add files to analyze.")
                return

            self.text_pottery_log.append("\n" + "=" * 50)
            self.text_pottery_log.append("POTTERY DRAWING DIAGNOSTIC ANALYSIS")
            self.text_pottery_log.append("=" * 50)

            # Run diagnostic on each file
            for i in range(input_count):
                item = self.list_pottery_ink_input.item(i)
                input_path = item.data(Qt.UserRole)

                if input_path and os.path.exists(input_path):
                    self.text_pottery_log.append(f"\n📊 Analyzing: {os.path.basename(input_path)}")

                    # Run diagnostic
                    diagnostic = self.pottery_ink.run_diagnostic(input_path)

                    if 'error' in diagnostic:
                        self.text_pottery_log.append(f"  ✗ Error: {diagnostic['error']}")
                        continue

                    # Display image info
                    if 'image_info' in diagnostic:
                        info = diagnostic['image_info']
                        self.text_pottery_log.append("\n  📐 Image Information:")
                        self.text_pottery_log.append(f"    • Size: {info['width']} x {info['height']} pixels")
                        self.text_pottery_log.append(f"    • Channels: {info['channels']}")
                        self.text_pottery_log.append(f"    • File size: {info['file_size'] / 1024:.1f} KB")

                    # Display quality metrics
                    if 'quality_metrics' in diagnostic:
                        metrics = diagnostic['quality_metrics']
                        self.text_pottery_log.append("\n  📈 Quality Metrics:")
                        self.text_pottery_log.append(f"    • Mean intensity: {metrics['mean_intensity']:.1f}")
                        self.text_pottery_log.append(f"    • Std intensity: {metrics['std_intensity']:.1f}")
                        self.text_pottery_log.append(f"    • Contrast ratio: {metrics['contrast']:.2f}")
                        self.text_pottery_log.append(f"    • Edge density: {metrics['edge_ratio']:.3f}")

                    # Display suggestions
                    if 'preprocessing_suggestions' in diagnostic and diagnostic['preprocessing_suggestions']:
                        self.text_pottery_log.append("\n  💡 Suggestions:")
                        for suggestion in diagnostic['preprocessing_suggestions']:
                            self.text_pottery_log.append(f"    • {suggestion}")

                    # Display recommended settings
                    if 'recommended_settings' in diagnostic:
                        settings = diagnostic['recommended_settings']
                        self.text_pottery_log.append("\n  ⚙️ Recommended Settings:")
                        self.text_pottery_log.append(f"    • Contrast scale: {settings['contrast_scale']}")
                        self.text_pottery_log.append(f"    • Use high-res mode: {settings['use_high_res']}")
                        self.text_pottery_log.append(f"    • Patch size: {settings['patch_size']}")

                        # Automatically apply recommended settings
                        if hasattr(self, 'slider_stippling'):
                            self.slider_stippling.setValue(int(settings['contrast_scale'] * 100))
                        if hasattr(self, 'check_high_res'):
                            self.check_high_res.setChecked(settings['use_high_res'])
                        if hasattr(self, 'spin_patch_size'):
                            self.spin_patch_size.setValue(settings['patch_size'])

            # Display device info
            if input_count > 0:
                self.text_pottery_log.append("\n" + "=" * 50)
                self.text_pottery_log.append("🖥️ System Information:")
                first_diagnostic = self.pottery_ink.run_diagnostic(
                    self.list_pottery_ink_input.item(0).data(Qt.UserRole)
                )
                if 'device_info' in first_diagnostic:
                    device_info = first_diagnostic['device_info']
                    self.text_pottery_log.append(f"  • Processing device: {device_info['device']}")
                    self.text_pottery_log.append(f"  • Virtual env active: {device_info['venv_python']}")
                    self.text_pottery_log.append(f"  • PotteryInk available: {device_info['has_pottery_ink']}")

            self.text_pottery_log.append("\n" + "=" * 50)
            self.text_pottery_log.append("✓ Diagnostic analysis complete")

            # Scroll to bottom
            self.text_pottery_log.verticalScrollBar().setValue(
                self.text_pottery_log.verticalScrollBar().maximum()
            )

        except Exception as e:
            self.log_message(f"Diagnostic error: {str(e)}", Qgis.Critical)
            self.text_pottery_log.append(f"\n✗ Diagnostic error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Diagnostic failed:\n{str(e)}")

    def export_pottery_ink_to_layout(self):
        """Export enhanced images to the layout creator"""
        try:
            output_count = self.list_pottery_ink_output.count()
            if output_count == 0:
                QMessageBox.warning(self, "No Results", "No enhanced images to export.")
                return

            # Clear existing images in layout
            self.extracted_images = []
            
            # Add enhanced images to layout
            for i in range(output_count):
                item = self.listWidget_pottery_ink_output.item(i)
                image_path = item.data(Qt.UserRole)
                
                if image_path and os.path.exists(image_path):
                    self.extracted_images.append(image_path)
            
            if self.extracted_images:
                # Switch to layout tab
                self.tabWidget_main.setCurrentIndex(1)  # Assuming layout tab is index 1
                
                # Update layout preview
                if hasattr(self, 'update_catalog_preview'):
                    self.update_catalog_preview()
                
                self.text_pottery_log.append(f"\n✓ Exported {len(self.extracted_images)} images to layout")
                QMessageBox.information(
                    self,
                    "Export Complete",
                    f"Exported {len(self.extracted_images)} images to layout creator.\n"
                    "Switch to the Layout tab to create your catalog."
                )
                
        except Exception as e:
            self.log_message(f"Error exporting to layout: {str(e)}", Qgis.Warning)
            QMessageBox.warning(self, "Error", f"Failed to export to layout:\n{str(e)}")