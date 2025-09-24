# -*- coding: utf-8 -*-
"""
/***************************************************************************
        pyArchInit Plugin  - A QGIS plugin to manage archaeological dataset
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
 *                                                                       *
 ***************************************************************************/
"""
import os
import platform
import shutil
import subprocess
import sys
from importlib.metadata import distributions
from shlex import quote as shlex_quote
from typing import Dict, List, Optional, Set

from qgis.PyQt.QtCore import QObject, QThread, pyqtSignal
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import (QCheckBox, QDialog, QHeaderView, QLabel,
                                 QMessageBox, QProgressBar, QPushButton,
                                 QTableWidget, QTableWidgetItem, QVBoxLayout)
from qgis.core import QgsSettings

from .modules.utility.pyarchinit_OS_utility import Pyarchinit_OS_Utility
from .modules.utility.pyarchinit_folder_installation import pyarchinit_Folder_installation

# Constants for paths
PYARCHINIT_HOME = os.path.expanduser("~") + os.sep + 'pyarchinit'

# Constants for QGIS paths on MacOS
QGIS_PATHS = {
    'standard': '/Applications/QGIS.app/Contents/MacOS',
    'ltr': '/Applications/QGIS-LTR.app/Contents/MacOS'
}

# Constants for OpenCV paths on MacOS
OPENCV_PATHS = {
    'standard': "/Applications/QGIS.app/Contents/Resources/python/site-packages/opencv_contrib_python-4.3.0.36-py3.9-macosx-10.13.0-x86_64.egg/",
    'ltr': "/Applications/QGIS-LTR.app/Contents/Resources/python/site-packages/opencv_contrib_python-4.3.0.36-py3.9-macosx-10.13.0-x86_64.egg/"
}


class PipManager:
    """Manages pip installation and updates."""

    @staticmethod
    def update_pip(python_path: Optional[str] = None) -> None:
        """
        Update pip to the latest available version.

        Args:
            python_path: Path to the Python executable to use
        """
        command = [python_path if python_path else 'python', '-m', 'pip', 'install', '--upgrade', 'pip']
        try:
            subprocess.call(command)
        except subprocess.SubprocessError as e:
            print(f"Error updating pip: {e}")

    @staticmethod
    def configure_pip() -> None:
        """Configure and update pip based on the operating system."""
        try:
            import pip
        except ImportError:
            system = platform.system()

            if system == 'Darwin':
                for qgis_path in [QGIS_PATHS['standard'], QGIS_PATHS['ltr']]:
                    try:
                        python_exec = os.path.join(qgis_path, 'bin', 'python3')
                        PipManager.update_pip(python_exec)
                        break
                    except Exception:
                        continue

            elif system == 'Windows':
                try:
                    subprocess.call(['python', '-m', 'ensurepip'])
                    PipManager.update_pip()
                except subprocess.SubprocessError as e:
                    print(f"Error configuring pip on Windows: {e}")


class PackageManager:
    """Manages package installation across different operating systems."""

    # Priority packages that need special handling
    PRIORITY_PACKAGES = ["Pillow", "matplotlib", "numpy", "scipy"]

    @staticmethod
    def is_osgeo4w() -> bool:
        """Check if running in OSGeo4W environment."""
        return 'OSGEO4W_ROOT' in os.environ

    @staticmethod
    def get_osgeo4w_python() -> str:
        """Get the path to the OSGeo4W Python executable."""
        osgeo4w_root = os.environ.get('OSGEO4W_ROOT')
        if osgeo4w_root:
            # Check if python-qgis-ltr.bat exists
            ltr_path = os.path.join(osgeo4w_root, 'bin', 'python-qgis-ltr.bat')
            if os.path.exists(ltr_path):
                return ltr_path
            # Otherwise use python-qgis.bat
            return os.path.join(osgeo4w_root, 'bin', 'python-qgis.bat')
        return sys.executable

    @staticmethod
    def is_ubuntu() -> bool:
        """Check if running on Ubuntu."""
        return platform.system() == 'Linux' and 'Ubuntu' in platform.version()

    @staticmethod
    def get_ubuntu_package_name(package: str) -> str:
        """
        Map pip package names to Ubuntu package names.

        Args:
            package: The pip package name

        Returns:
            The corresponding Ubuntu package name or the original name if not found
        """
        ubuntu_packages = {
            'SQLAlchemy': 'python3-sqlalchemy',
            'SQLAlchemy-Utils': 'python3-sqlalchemy-utils',
            'GeoAlchemy2': 'python3-geoalchemy2',
            'reportlab': 'python3-reportlab',
            'graphviz': 'python3-graphviz',
            'XlsxWriter': 'python3-xlsxwriter',
            'opencv-python': 'python3-opencv',
            'pytesseract': 'python3-pytesseract',
            'psutil': 'python3-psutil',
            'openai': 'python3-openai',
            'openpyxl': 'python3-openpyxl',
            'matplotlib': 'python3-matplotlib',
            'pandas': 'python3-pandas',
            'requests': 'python3-requests',
            'PyMuPDF': 'python3-fitz',
            'nltk': 'python3-nltk',
            'python-docx': 'python3-docx',
        }
        return ubuntu_packages.get(package.split('==')[0], package)

    @staticmethod
    def install(package: str) -> None:
        """
        Install a package using the appropriate method for the current OS.

        Args:
            package: The package to install
        """
        # Special handling for Pillow on macOS
        package_base = package.split('==')[0].split('>=')[0]
        if package_base == 'Pillow' and platform.system() == 'Darwin':
            # First attempt to uninstall any existing Pillow
            for qgis_type in ['standard', 'ltr']:
                try:
                    python_executable = os.path.join(QGIS_PATHS[qgis_type], 'bin', 'python3')
                    # Try to uninstall existing Pillow first
                    subprocess.run([python_executable, "-m", "pip", "uninstall", "-y", "Pillow"],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    # Then install the requested version
                    subprocess.run(
                        [python_executable, "-m", "pip", "install", "--force-reinstall", shlex_quote(package)],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                    break
                except Exception as e:
                    print(f"Error reinstalling Pillow on {qgis_type}: {e}")
            return

        # Regular installation process
        if PackageManager.is_ubuntu():
            ubuntu_package = PackageManager.get_ubuntu_package_name(package)
            try:
                subprocess.run(['sudo', 'apt', 'install', '-y', ubuntu_package],
                               check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except subprocess.CalledProcessError:
                print(f"Failed to install {ubuntu_package} via apt. Falling back to pip.")
                subprocess.run([sys.executable, "-m", "pip", "install", shlex_quote(package)],
                               check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        elif platform.system() == 'Windows' and PackageManager.is_osgeo4w():
            python_executable = PackageManager.get_osgeo4w_python()
            subprocess.run([python_executable, "-m", "pip", "install", shlex_quote(package)],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, shell=True)
        elif platform.system() == 'Windows':
            python_executable = 'python'
            subprocess.run([python_executable, "-m", "pip", "install", shlex_quote(package), "--user"],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, shell=True)
        elif platform.system() == 'Darwin':
            for qgis_type in ['standard', 'ltr']:
                try:
                    python_executable = os.path.join(QGIS_PATHS[qgis_type], 'bin', 'python3')
                    subprocess.run([python_executable, "-m", "pip", "install", shlex_quote(package)],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                    break
                except Exception as e:
                    print(f"Error installing {package} on {qgis_type}: {e}")

    @staticmethod
    def remove_opencv_directories() -> None:
        """
        Remove OpenCV directories if they exist on macOS.
        Does nothing on other operating systems.
        """
        if platform.system() != 'Darwin':
            return

        for path in OPENCV_PATHS.values():
            try:
                if os.path.exists(path):
                    shutil.rmtree(path)
                    print(f"Directory {path} has been successfully removed.")
                else:
                    print(f"Directory {path} does not exist.")
            except Exception as e:
                print(f"Error removing directory {path}: {e}")

    @staticmethod
    def check_required_packages(requirements_path: str) -> List[str]:
        """
        Check which required packages are missing.

        Args:
            requirements_path: Path to the requirements.txt file

        Returns:
            List of missing packages
        """
        installed_packages = {pkg.metadata['Name'] + '==' + pkg.version for pkg in distributions()}

        with open(requirements_path, 'r') as f:
            # Filter out comment lines (starting with #) and empty lines
            required_packages = set(
                line.strip() for line in f 
                if line.strip() and not line.strip().startswith('#')
            )

        missing_packages = required_packages - installed_packages
        return list(missing_packages)


class Worker(QObject):
    """Worker thread for installing packages."""

    finished = pyqtSignal()  # Signal emitted when the worker is done
    progress = pyqtSignal(int)  # Signal emitted to update the progress bar

    def install_packages(self, packages: List[str]) -> None:
        """
        Install a list of packages and emit progress signals.

        Args:
            packages: List of packages to install
        """
        total = len(packages)
        for i, package in enumerate(packages):
            self.progress.emit(int((i + 1) / total * 100))  # Emit progress signal
            PackageManager.install(package)

        self.finished.emit()  # Emit finished signal


class InstallDialog(QDialog):
    """Dialog for selecting and installing packages."""

    def __init__(self, packages: List[str]):
        """
        Initialize the dialog.

        Args:
            packages: List of packages that can be installed
        """
        super().__init__()
        self.packages = packages
        self.initUI()

    def initUI(self) -> None:
        """Initialize the UI components."""
        layout = QVBoxLayout()

        self.label = QLabel("Select packages to install:")
        layout.addWidget(self.label)

        self.table = QTableWidget(len(self.packages), 2)
        self.table.setHorizontalHeaderLabels(["Package", "Install"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        for i, package in enumerate(self.packages):
            self.table.setItem(i, 0, QTableWidgetItem(package))
            checkbox = QCheckBox()
            checkbox.setChecked(True)
            self.table.setCellWidget(i, 1, checkbox)

        layout.addWidget(self.table)

        self.install_button = QPushButton("Install Packages")
        self.install_button.clicked.connect(self.install_selected_packages)
        layout.addWidget(self.install_button)

        self.progress = QProgressBar()
        layout.addWidget(self.progress)

        self.setLayout(layout)
        self.setWindowTitle("PyArchInit - Package Installation")
        self.set_icon(os.path.abspath(os.path.join(os.path.dirname(__file__), "logo_pyarchinit.png")))
        self.setGeometry(300, 300, 400, 300)

    def set_icon(self, icon_path: str) -> None:
        """
        Set the dialog icon.

        Args:
            icon_path: Path to the icon file
        """
        self.setWindowIcon(QIcon(icon_path))

    def install_selected_packages(self) -> None:
        """Install the packages selected in the table."""
        selected_packages = []
        for i in range(self.table.rowCount()):
            if self.table.cellWidget(i, 1).isChecked():
                selected_packages.append(self.table.item(i, 0).text())

        if selected_packages:
            # Disable the install button during installation
            self.install_button.setEnabled(False)
            self.install_button.setText("Installing...")

            # On macOS, we need to create a more reliable progress reporting
            if platform.system() == 'Darwin':
                # Initialize progress bar
                self.progress.setValue(0)
                self.progress.setTextVisible(True)
                self.label.setText("Preparing to install packages...")

                # Process events to ensure UI updates
                from qgis.PyQt.QtCore import QCoreApplication
                QCoreApplication.processEvents()

                # Create and start thread with special handling for macOS
                self.thread = QThread(self)
                self.worker = Worker()
                self.worker.moveToThread(self.thread)

                # Connect signals with extra event processing for macOS
                self.thread.started.connect(lambda: self.worker.install_packages(selected_packages))
                self.worker.progress.connect(self.update_progress_mac)
                self.worker.finished.connect(self.thread.quit)
                self.worker.finished.connect(self.worker.deleteLater)
                self.thread.finished.connect(self.thread.deleteLater)
                self.worker.finished.connect(self.finish_install)

                self.thread.start()
            else:
                # Standard approach for Windows and Linux
                self.thread = QThread(self)
                self.worker = Worker()
                self.worker.moveToThread(self.thread)
                self.thread.started.connect(lambda: self.worker.install_packages(selected_packages))

                self.worker.finished.connect(self.thread.quit)
                self.worker.finished.connect(self.worker.deleteLater)
                self.thread.finished.connect(self.thread.deleteLater)
                self.worker.progress.connect(self.update_progress)
                self.worker.finished.connect(self.finish_install)

                self.thread.start()

    def update_progress(self, value: int) -> None:
        """
        Update the progress bar for Windows and Linux.

        Args:
            value: The progress value (0-100)
        """
        self.progress.setValue(value)
        self.label.setText(f"Installing packages... {value}%")

    def update_progress_mac(self, value: int) -> None:
        """
        Update the progress bar for macOS with additional event processing.

        Args:
            value: The progress value (0-100)
        """
        # Update the progress bar
        self.progress.setValue(value)
        self.label.setText(f"Installing packages... {value}%")

        # Force UI update on macOS
        from qgis.PyQt.QtCore import QCoreApplication
        QCoreApplication.processEvents()

    def finish_install(self) -> None:
        """Called when installation is complete."""
        self.progress.setValue(100)
        self.label.setText("Installation complete")
        self.install_button.setEnabled(True)
        self.install_button.setText("Install Packages")

        # Force UI update on macOS
        if platform.system() == 'Darwin':
            from qgis.PyQt.QtCore import QCoreApplication
            QCoreApplication.processEvents()

        self.accept()


class FontManager:
    """Manages font installation."""

    @staticmethod
    def install_fonts() -> None:
        """Install required fonts for the system."""
        if platform.system() == "Darwin":
            location = os.path.expanduser("~/Library/Fonts")
            if not os.path.exists(location + '/cambria.ttc'):
                result = QMessageBox.warning(None, 'Pyarchinit',
                                             "INFO: The Cambria font does not appear to be installed. "
                                             "Click Ok to install it\nand then double click on cambria.*\n"
                                             "After that, reload the plugin",
                                             QMessageBox.Ok)
                if result == QMessageBox.Ok:
                    home = os.environ['PYARCHINIT_HOME']
                    path = f"{home}{os.sep}bin"
                    subprocess.Popen(["open", path])


def initialize_environment() -> None:
    """Initialize the environment for pyArchInit."""
    # Configure and update pip
    PipManager.configure_pip()

    # Setup pyArchInit home directory
    s = QgsSettings()
    sys.path.append(os.path.dirname(__file__))
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'resources')))
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'gui', 'ui')))

    # Create necessary directories
    fi = pyarchinit_Folder_installation()
    if not os.path.exists(PYARCHINIT_HOME):
        fi.install_dir()
    else:
        os.environ['PYARCHINIT_HOME'] = PYARCHINIT_HOME

    # Install configuration files
    config_path = os.path.join(os.sep, PYARCHINIT_HOME, 'pyarchinit_DB_folder', 'config.cfg')
    logo_iccd = os.path.join(os.sep, PYARCHINIT_HOME, 'pyarchinit_DB_folder', 'logo.jpg')
    if not os.path.isfile(config_path):
        fi.installConfigFile(os.path.dirname(config_path))

    fi.installConfigFile(os.path.dirname(logo_iccd))

    # Update PATH with graphviz and postgres
    if not Pyarchinit_OS_Utility.checkgraphvizinstallation() and s.value('pyArchInit/graphvizBinPath'):
        os.environ['PATH'] += os.pathsep + os.path.normpath(s.value('pyArchInit/graphvizBinPath'))

    if not Pyarchinit_OS_Utility.checkpostgresinstallation() and s.value('pyArchInit/postgresBinPath'):
        os.environ['PATH'] += os.pathsep + os.path.normpath(s.value('pyArchInit/postgresBinPath'))

    # Check external programs
    packages_to_check = ['postgres', 'graphviz']
    for package in packages_to_check:
        if package.startswith('postgres'):
            try:
                subprocess.call(['pg_dump', '-V'])
            except Exception as e:
                print(f"Error checking postgres: {e}")

        if package.startswith('graphviz'):
            try:
                subprocess.call(['dot', '-V'])
            except Exception as e:
                print(f"Error checking graphviz: {e}")

    # Install fonts
    FontManager.install_fonts()

    # Remove OpenCV directories on macOS
    PackageManager.remove_opencv_directories()


def check_and_install_dependencies() -> None:
    """Check and install missing dependencies."""
    s = QgsSettings()
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    missing_packages = PackageManager.check_required_packages(requirements_path)

    # Add fix for PIL/Pillow issue on macOS
    if platform.system() == 'Darwin':
        try:
            import PIL
            # Test if PIL.Image is accessible
            try:
                from PIL import Image
            except ImportError:
                # Reinstall Pillow if Image can't be imported
                print("PIL installation is corrupted. Fixing Pillow...")
                pillow_version = "Pillow>=9.0.0"
                if pillow_version not in missing_packages:
                    missing_packages.append(pillow_version)
        except ImportError:
            # Add Pillow to missing packages if PIL is not installed
            pillow_version = "Pillow>=9.0.0"
            if pillow_version not in missing_packages:
                missing_packages.append(pillow_version)

    if missing_packages:
        show_install_dialog(missing_packages)
    else:
        print("All required packages are already installed.")
        s.setValue('pyArchInit/dependenciesInstalled', True)


def show_install_dialog(packages: List[str]) -> None:
    """
    Show the dialog for installing packages.

    Args:
        packages: List of packages to install
    """
    dialog = InstallDialog(packages)
    dialog.exec_()


def classFactory(iface):
    """
    Load the PyArchInitPlugin class.

    Args:
        iface: QGIS interface

    Returns:
        PyArchInitPlugin instance
    """
    initialize_environment()
    check_and_install_dependencies()

    from .pyarchinitPlugin import PyArchInitPlugin
    return PyArchInitPlugin(iface)