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
import time
from importlib.metadata import distributions
from typing import Dict, List, Optional, Set

# Plugin-local ext_libs directory for dependency isolation
# Must be prepended to sys.path BEFORE any third-party imports
# so that plugin dependencies take priority over QGIS-bundled packages.
# Its compiled packages load only in the Python that installed them: one
# built for another Python (QGIS 3's 3.9 in a QGIS 4 profile) is parked
# aside and a fresh one is started (modules/utility/python_env.py).
from .modules.utility.python_env import ensure_ext_libs, pip_interpreter, probe, write_marker


def _startup_log(message):
    print(message)
    try:
        from qgis.core import Qgis, QgsMessageLog
        levels = getattr(Qgis, 'MessageLevel', Qgis)
        QgsMessageLog.logMessage(message, 'PyArchInit', levels.Warning)
    except Exception:
        pass


_EXT_LIBS_DIR = ensure_ext_libs(os.path.dirname(__file__), log=_startup_log)
if _EXT_LIBS_DIR not in sys.path:
    sys.path.insert(0, _EXT_LIBS_DIR)

from qgis.PyQt.QtCore import QObject, QThread, pyqtSignal, QTimer
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import (QCheckBox, QDialog, QHeaderView, QLabel,
                                 QMessageBox, QProgressBar, QPushButton,
                                 QTableWidget, QTableWidgetItem, QVBoxLayout,
                                 QApplication)
from qgis.core import QgsSettings

from .modules.utility.pyarchinit_OS_utility import Pyarchinit_OS_Utility
from .modules.utility.pyarchinit_folder_installation import pyarchinit_Folder_installation
from .modules.utility.pyarchinit_home import (
    pyarchinit_home, legacy_pyarchinit_home, migrate_db_folder,
    should_offer_migration)
from .modules.utility.startup_ui import (
    ask_yes_no, bring_to_front, exec_on_top, italian, no_console_window)

# Constants for paths
PYARCHINIT_HOME = pyarchinit_home()
# Earliest authority: every later pyarchinit_home() / os.environ read resolves
# to the same value (default ~/pyarchinit_5, or an external override).
os.environ['PYARCHINIT_HOME'] = PYARCHINIT_HOME

# Constants for QGIS paths on MacOS
QGIS_PATHS = {
    'standard': '/Applications/QGIS.app/Contents/MacOS',
    'ltr': '/Applications/QGIS-LTR.app/Contents/MacOS',
    'qgis4': '/Applications/QGIS-final-4_0_0.app/Contents/MacOS',
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
            subprocess.call(command, **no_console_window())
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
                    subprocess.call(['python', '-m', 'ensurepip'], **no_console_window())
                    PipManager.update_pip()
                except subprocess.SubprocessError as e:
                    print(f"Error configuring pip on Windows: {e}")


class PackageManager:
    """Manages package installation across different operating systems."""

    # Priority packages that need special handling
    PRIORITY_PACKAGES = ["Pillow", "matplotlib", "numpy", "scipy"]

    # Packages bundled by QGIS that must NOT be installed to ext_libs
    # (overriding them breaks QGIS internals)
    QGIS_PROTECTED_PACKAGES = {"numpy", "scipy", "sip", "pyqt5", "qgis"}

    # Same import package under another distribution name: QGIS 4 ships
    # psycopg2, the requirements ask for psycopg2-binary
    REQUIREMENT_ALIASES = {"psycopg2-binary": ("psycopg2",)}

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

    _cached_windows_python_path = None

    @staticmethod
    def get_windows_qgis_python() -> str:
        """
        Get the path to QGIS Python on Windows (standalone installation).

        Dynamically scans for all QGIS versions from 3.22 to 4.x.
        Supports both PR (latest) and LTR (Long Term Release) versions.
        Result is cached after first call to avoid repeated filesystem scans.

        Returns:
            Path to python.exe or sys.executable if not found
        """
        if PackageManager._cached_windows_python_path is not None:
            return PackageManager._cached_windows_python_path

        if platform.system() != 'Windows':
            PackageManager._cached_windows_python_path = sys.executable
            return sys.executable

        qgis_paths = []

        # Priority 1: Use QGIS_PREFIX_PATH environment variable (most reliable)
        qgis_prefix = os.environ.get('QGIS_PREFIX_PATH')
        if qgis_prefix:
            # QGIS_PREFIX_PATH points to apps/qgis, so go up two levels
            base_path = os.path.dirname(os.path.dirname(qgis_prefix))
            # Check all Python versions from newest to oldest
            for py_ver in ['Python313', 'Python312', 'Python311', 'Python310', 'Python39', 'Python38']:
                qgis_paths.append(os.path.join(base_path, 'apps', py_ver, 'python.exe'))

        # Priority 2: Scan Program Files for all QGIS installations
        program_files_dirs = [
            os.environ.get('PROGRAMFILES', 'C:\\Program Files'),
            os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)'),
        ]

        # Python versions used by different QGIS releases
        python_versions = ['Python313', 'Python312', 'Python311', 'Python310', 'Python39', 'Python38']

        for program_files in program_files_dirs:
            if not os.path.exists(program_files):
                continue

            # Scan for QGIS directories
            try:
                for item in os.listdir(program_files):
                    # Match QGIS 3.x, QGIS 4.x, QGIS-LTR, QGIS-PR, or just QGIS
                    if item.upper().startswith('QGIS'):
                        qgis_dir = os.path.join(program_files, item)
                        if os.path.isdir(qgis_dir):
                            apps_dir = os.path.join(qgis_dir, 'apps')
                            if os.path.exists(apps_dir):
                                # Check for Python in apps folder
                                for py_ver in python_versions:
                                    python_path = os.path.join(apps_dir, py_ver, 'python.exe')
                                    if python_path not in qgis_paths:
                                        qgis_paths.append(python_path)
            except (PermissionError, OSError):
                continue

        # Priority 3: Generic QGIS paths
        for program_files in program_files_dirs:
            for py_ver in python_versions:
                generic_path = os.path.join(program_files, 'QGIS', 'apps', py_ver, 'python.exe')
                if generic_path not in qgis_paths:
                    qgis_paths.append(generic_path)

        # Try to find existing Python installation
        for path in qgis_paths:
            if os.path.exists(path):
                PackageManager._cached_windows_python_path = path
                return path

        # Fallback: use sys.executable (the Python running QGIS)
        PackageManager._cached_windows_python_path = sys.executable
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
    def _python_fallbacks() -> List[str]:
        """Interpreters tried after those of the running QGIS; pip_interpreter
        keeps only one with the running Python's version and architecture."""
        found = []
        if platform.system() == 'Windows':
            if PackageManager.is_osgeo4w():
                found.append(PackageManager.get_osgeo4w_python())
            found.append(PackageManager.get_windows_qgis_python())
        elif platform.system() == 'Darwin':
            names = ('python3', 'python%d.%d' % sys.version_info[:2])
            for qgis_base in QGIS_PATHS.values():
                contents_dir = os.path.dirname(qgis_base)
                for subdir in (os.path.join(qgis_base, 'bin'),
                               os.path.join(contents_dir, 'Resources', 'python', 'bin'),
                               os.path.join(contents_dir, 'Frameworks', 'Python.framework',
                                            'Versions', 'Current', 'bin')):
                    found += [os.path.join(subdir, n) for n in names]
            found += ['/usr/bin/python3', '/opt/homebrew/bin/python3', '/usr/local/bin/python3']
        return found

    @staticmethod
    def _pip_install(args: List[str], timeout: int = 900) -> bool:
        """pip install with a Python of the same version and architecture as
        the one running QGIS: compiled packages built for another Python
        (QGIS 3's 3.9 while QGIS 4 runs 3.12) cannot be imported."""
        found = pip_interpreter(PackageManager._python_fallbacks())
        if found is None:
            print(f"pyArchInit: no Python {sys.version_info[0]}.{sys.version_info[1]} "
                  f"({platform.machine()}) with pip found: {args[-1]} not installed")
            return False
        python_cmd, env = found
        try:
            subprocess.run([python_cmd, "-m", "pip", "install", "--disable-pip-version-check", *args],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, env=env,
                           timeout=timeout, shell=python_cmd.lower().endswith('.bat'),
                           **no_console_window())
            return True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as e:
            err = getattr(e, 'stderr', None)
            detail = err.decode(errors='replace')[-800:] if isinstance(err, bytes) else str(e)
            print(f"Error installing {args[-1]}: {detail}")
            return False

    @staticmethod
    def _reinstall_pillow_in_qgis(package: str) -> bool:
        """macOS: replace a broken Pillow in the QGIS site-packages, only with
        a QGIS Python matching the running one."""
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        want = (sys.version_info[0], sys.version_info[1], platform.machine().lower())
        for qgis_type in ['standard', 'ltr']:
            qgis_base = QGIS_PATHS[qgis_type]
            qgis_python = os.path.join(qgis_base, 'bin', 'python3')
            qgis_site_packages = os.path.join(qgis_base, 'lib', f'python{python_version}', 'site-packages')
            if not os.path.exists(qgis_python) or not os.path.exists(qgis_site_packages):
                continue
            got = probe(qgis_python)
            if not got or got[:3] != want:
                continue
            try:
                # Try to uninstall existing Pillow first
                subprocess.run([qgis_python, "-m", "pip", "uninstall", "-y", "Pillow"],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                # Install with --target to QGIS site-packages
                subprocess.run(
                    [qgis_python, "-m", "pip", "install", "--force-reinstall",
                     "--target", qgis_site_packages, package],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                return True
            except Exception as e:
                print(f"Error reinstalling Pillow: {e}")
        return False

    @staticmethod
    def install(package: str) -> None:
        """
        Install a package for the running Python into the plugin's ext_libs.

        Args:
            package: The package to install
        """
        # Extract package base name for checks
        package_base = package.split('==')[0].split('>=')[0].split('<=')[0].strip()

        # Skip packages that would break QGIS if overridden
        if package_base.lower() in PackageManager.QGIS_PROTECTED_PACKAGES:
            print(f"Skipping {package_base} - protected QGIS package")
            return

        if (package_base == 'Pillow' and platform.system() == 'Darwin'
                and PackageManager._reinstall_pillow_in_qgis(package)):
            return

        if PackageManager.is_ubuntu():
            ubuntu_package = PackageManager.get_ubuntu_package_name(package)
            try:
                subprocess.run(['sudo', 'apt', 'install', '-y', ubuntu_package],
                               check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                return
            except (subprocess.CalledProcessError, OSError):
                print(f"Failed to install {ubuntu_package} via apt. Falling back to pip.")

        # Plugin-local ext_libs (priority over the QGIS packages; no
        # permission issues with the QGIS bundle / Program Files)
        if PackageManager._pip_install(["--upgrade", "--target", _EXT_LIBS_DIR, package]):
            write_marker(_EXT_LIBS_DIR)
        elif platform.system() in ('Windows', 'Linux'):
            # Fallback: the user site of the same Python
            PackageManager._pip_install(["--upgrade", package, "--user"])

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
        Check which required packages are missing or have wrong versions.

        Searches both standard distributions and the plugin ext_libs directory.

        Args:
            requirements_path: Path to the requirements.txt file

        Returns:
            List of missing or outdated packages
        """
        # Build a dict of installed packages: name (lowercase) -> version
        # Priority: ext_libs packages override system packages
        installed_packages = {}
        for pkg in distributions():
            try:
                name = pkg.metadata.get('Name')
                version = pkg.metadata.get('Version')
                if name:
                    installed_packages[name.lower()] = version or ''
            except Exception:
                continue

        # Also scan ext_libs .dist-info directories for packages installed there
        ext_libs = _EXT_LIBS_DIR
        if os.path.isdir(ext_libs):
            ext_versions = {}
            for item in os.listdir(ext_libs):
                if item.endswith('.dist-info'):
                    metadata_file = os.path.join(ext_libs, item, 'METADATA')
                    if not os.path.exists(metadata_file):
                        metadata_file = os.path.join(ext_libs, item, 'PKG-INFO')
                    if os.path.exists(metadata_file):
                        try:
                            with open(metadata_file, 'r', encoding='utf-8') as mf:
                                pkg_name = pkg_version = None
                                for mline in mf:
                                    if mline.startswith('Name:'):
                                        pkg_name = mline.split(':', 1)[1].strip().lower()
                                    elif mline.startswith('Version:'):
                                        pkg_version = mline.split(':', 1)[1].strip()
                                    if pkg_name and pkg_version:
                                        break
                                if pkg_name:
                                    # Stale duplicate dist-infos can survive upgrades
                                    # (listdir order is arbitrary): keep the highest
                                    prev = ext_versions.get(pkg_name)
                                    if prev:
                                        try:
                                            from packaging.version import Version
                                            if Version(pkg_version or '0') <= Version(prev):
                                                continue
                                        except Exception:
                                            if (pkg_version or '') <= prev:
                                                continue
                                    ext_versions[pkg_name] = pkg_version or ''
                        except Exception:
                            continue
            # ext_libs versions take priority over system packages
            installed_packages.update(ext_versions)

        missing_packages = []
        with open(requirements_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                # Strip inline comments (e.g. "opencv-python>=4.8.0  # Optional")
                if ' #' in line:
                    line = line[:line.index(' #')].strip()

                # Handle PEP 508 environment markers (e.g. "pkg>=1.0; python_version<'3.10'")
                if ';' in line:
                    spec_part, marker_str = line.split(';', 1)
                    line = spec_part.strip()
                    marker_str = marker_str.strip()
                    try:
                        from packaging.markers import Marker
                        if not Marker(marker_str).evaluate():
                            continue  # this line's marker doesn't apply to current env
                    except Exception:
                        # If marker can't be parsed, skip this line conservatively
                        continue

                package_spec = line
                package_name = line.split('==')[0].split('>=')[0].split('<=')[0].split('~=')[0].split('!=')[0].strip()
                pkg_lower = package_name.lower()
                for alias in PackageManager.REQUIREMENT_ALIASES.get(pkg_lower, ()):
                    if pkg_lower not in installed_packages and alias in installed_packages:
                        installed_packages[pkg_lower] = installed_packages[alias]

                if pkg_lower not in installed_packages:
                    # Package not installed at all
                    missing_packages.append(package_spec)
                elif '==' in line:
                    # Exact version pinned - check major version mismatch
                    required_version = line.split('==')[1].strip()
                    installed_version = installed_packages[pkg_lower]
                    if installed_version and installed_version != required_version:
                        req_parts = required_version.split('.')
                        inst_parts = installed_version.split('.')
                        req_major = req_parts[0]
                        inst_major = inst_parts[0]
                        if req_major != inst_major:
                            missing_packages.append(package_spec)
                        elif req_major == '0':
                            req_minor = req_parts[1] if len(req_parts) > 1 else '0'
                            inst_minor = inst_parts[1] if len(inst_parts) > 1 else '0'
                            if req_minor != inst_minor:
                                missing_packages.append(package_spec)
                elif '>=' in line:
                    # Minimum version - check if installed version is too old
                    # (tolerate ranges like ">=1.4.27,<2.0": the floor is what we check)
                    min_version = line.split('>=')[1].split(',')[0].strip()
                    installed_version = installed_packages[pkg_lower]
                    if installed_version:
                        try:
                            from packaging.version import Version
                            if Version(installed_version) < Version(min_version):
                                missing_packages.append(package_spec)
                        except Exception:
                            # Fallback: simple tuple comparison
                            min_parts = tuple(int(x) for x in min_version.split('.'))
                            inst_parts = tuple(int(x) for x in installed_version.split('.'))
                            if inst_parts < min_parts:
                                missing_packages.append(package_spec)

        return missing_packages


class Worker(QObject):
    """Worker thread for installing packages."""

    finished = pyqtSignal()  # Signal emitted when the worker is done
    progress = pyqtSignal(int)  # Signal emitted to update the progress bar
    package_status = pyqtSignal(str)  # Signal emitted with current package name

    def install_packages(self, packages: List[str]) -> None:
        """
        Install a list of packages and emit progress signals.

        Args:
            packages: List of packages to install
        """
        total = len(packages)
        template = ("Installazione pacchetti {n}/{total}: {package} — può richiedere alcuni minuti"
                    if italian() else
                    "Installing packages {n}/{total}: {package} — this can take several minutes")
        for i, package in enumerate(packages):
            self.package_status.emit(template.format(n=i + 1, total=total, package=package))
            self.progress.emit(int(i / total * 100))
            PackageManager.install(package)
            self.progress.emit(int((i + 1) / total * 100))

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
        self.splash = None
        self._progress_value = 0
        self._install_started = None
        self._elapsed_timer = None
        self.initUI()

    def initUI(self) -> None:
        """Initialize the UI components."""
        layout = QVBoxLayout()

        self.label = QLabel("Select packages to install:")
        layout.addWidget(self.label)

        self.table = QTableWidget(len(self.packages), 2)
        self.table.setHorizontalHeaderLabels(["Package", "Install"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

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

    def show_splash(self, message: str = "Installing dependencies...") -> None:
        """Show the animated splash screen."""
        try:
            from .gui.pyarchinit_splash import PyArchInitSplash
            self.splash = PyArchInitSplash(self, message)
            self.splash.show()
            self.splash.raise_()
            # progress bar + elapsed time in front: pip takes minutes
            self._install_started = time.monotonic()
            self._refresh_splash_progress()
            self._elapsed_timer = QTimer(self)
            self._elapsed_timer.timeout.connect(self._refresh_splash_progress)
            self._elapsed_timer.start(1000)
            QApplication.processEvents()
        except ImportError:
            # Fallback if splash module not available
            self.splash = None

    def update_splash_message(self, message: str) -> None:
        """Update the splash screen message."""
        if self.splash:
            self.splash.set_message(message)
            QApplication.processEvents()

    def hide_splash(self) -> None:
        """Hide the splash screen."""
        if self._elapsed_timer:
            self._elapsed_timer.stop()
            self._elapsed_timer = None
        if self.splash:
            self.splash.close()
            self.splash = None

    def _refresh_splash_progress(self) -> None:
        """Progress bar and elapsed time on the splash."""
        if not self.splash or self._install_started is None:
            return
        elapsed = int(time.monotonic() - self._install_started)
        self.splash.set_progress(self._progress_value,
                                 f"{self._progress_value}% · {elapsed // 60}:{elapsed % 60:02d}")

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

            # Show animated splash screen
            self.show_splash("Preparing to install packages...")

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
                self.worker.package_status.connect(self.update_splash_message)
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
                self.worker.package_status.connect(self.update_splash_message)
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
        self._progress_value = value
        self._refresh_splash_progress()

    def update_progress_mac(self, value: int) -> None:
        """
        Update the progress bar for macOS with additional event processing.

        Args:
            value: The progress value (0-100)
        """
        # Update the progress bar
        self.progress.setValue(value)
        self.label.setText(f"Installing packages... {value}%")
        self._progress_value = value
        self._refresh_splash_progress()

        # Force UI update on macOS
        from qgis.PyQt.QtCore import QCoreApplication
        QCoreApplication.processEvents()

    def finish_install(self) -> None:
        """Called when installation is complete."""
        # Update splash message before hiding
        self._progress_value = 100
        self._refresh_splash_progress()
        self.update_splash_message("Installation complete!")

        # Small delay to show completion message
        QTimer.singleShot(1000, self._complete_install)

    def _complete_install(self) -> None:
        """Complete the installation process."""
        # Hide splash screen
        self.hide_splash()

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
    def install_fonts(splash=None) -> None:
        """Install required fonts for the system."""
        if platform.system() == "Darwin":
            location = os.path.expanduser("~/Library/Fonts")
            if not os.path.exists(location + '/cambria.ttc'):
                # in front of the splash (always on top) and of QGIS
                result = exec_on_top(QMessageBox(
                    QMessageBox.Icon.Warning, 'Pyarchinit',
                    "INFO: The Cambria font does not appear to be installed. "
                    "Click Ok to install it\nand then double click on cambria.*\n"
                    "After that, reload the plugin",
                    QMessageBox.StandardButton.Ok), splash)
                if result == QMessageBox.StandardButton.Ok:
                    home = os.environ['PYARCHINIT_HOME']
                    path = f"{home}{os.sep}bin"
                    subprocess.Popen(["open", path])


def initialize_environment(splash=None) -> None:
    """Initialize the environment for pyArchInit.

    Args:
        splash: Optional splash screen to update messages and keep animation alive
    """
    def _step(message=None):
        """Process events between steps to keep splash animation fluid."""
        if splash and message:
            splash.set_message(message)
        QApplication.processEvents()

    _step("Configuring Python environment...")

    # Configure and update pip
    PipManager.configure_pip()
    _step()

    # Setup pyArchInit home directory
    s = QgsSettings()
    sys.path.append(os.path.dirname(__file__))
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'resources')))
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'gui', 'ui')))

    _step("Creating project directories...")

    # Create necessary directories
    fi = pyarchinit_Folder_installation()

    # First-run migration: when the new data home is not set up yet (no
    # config.cfg) but a legacy ~/pyarchinit install exists, offer to copy its
    # DB folder (config + databases). Gated on config-file presence — NOT on
    # base-dir existence — so it still fires when the base was pre-created by
    # other code paths (paradata workspace mkdir, bin/ creation) and never
    # nags once the new home has been set up.
    # The question must stay in front: parentless, it opened behind the
    # splash (always on top) and QGIS / the Plugin Manager, above all on
    # Windows, and startup waited for a click nobody could see.
    if should_offer_migration(PYARCHINIT_HOME):
        try:
            if italian():
                text = ("Trovata un'installazione pyArchInit esistente in:\n"
                        f"{legacy_pyarchinit_home()}\n\n"
                        "Vuoi copiare configurazione e database nella nuova "
                        "cartella?\n"
                        f"{PYARCHINIT_HOME}\n\n"
                        "(Gli strumenti AI in bin/ NON vengono copiati: vanno "
                        "reinstallati o copiati manualmente.)")
            else:
                text = ("An existing pyArchInit installation was found in:\n"
                        f"{legacy_pyarchinit_home()}\n\n"
                        "Copy its configuration and databases into the new "
                        "folder?\n"
                        f"{PYARCHINIT_HOME}\n\n"
                        "(The AI tools in bin/ are NOT copied: reinstall "
                        "them or copy them by hand.)")
            if ask_yes_no("pyArchInit", text, splash):
                _step("Copia di configurazione e database..." if italian()
                      else "Copying configuration and databases...")
                migrate_db_folder(legacy_pyarchinit_home(), PYARCHINIT_HOME)
        except Exception as _exc:
            print(f"[pyArchInit] home migration skipped: {_exc}")

    # ALWAYS ensure the full directory tree + bundled files (example DB,
    # config, logos) exist. install_dir() is idempotent — create_dir ignores
    # "already exists" and copy_file skips existing files — so migrated/edited
    # files are preserved while any missing subfolder or bundled file is
    # (re)created. Robust to a base dir pre-created by other code paths (this
    # is why it runs unconditionally, not only when the home is absent).
    os.environ['PYARCHINIT_HOME'] = PYARCHINIT_HOME
    fi.install_dir()
    # Refresh bundled maintenance files (dot.py, dottoxml.py, …) when the
    # plugin shipped a newer version, so fixes reach <home>/bin/.
    try:
        fi.install_or_update_maintenance_files()
    except Exception as _exc:
        # Never block plugin startup on a maintenance refresh.
        print(f"[pyArchInit] maintenance refresh skipped: {_exc}")
    _step()

    # Install configuration files
    config_path = os.path.join(os.sep, PYARCHINIT_HOME, 'pyarchinit_DB_folder', 'config.cfg')
    logo_iccd = os.path.join(os.sep, PYARCHINIT_HOME, 'pyarchinit_DB_folder', 'logo.jpg')
    if not os.path.isfile(config_path):
        fi.installConfigFile(os.path.dirname(config_path))

    fi.installConfigFile(os.path.dirname(logo_iccd))
    _step("Detecting external tools...")

    # Update PATH with graphviz and postgres
    if not Pyarchinit_OS_Utility.checkgraphvizinstallation() and s.value('pyArchInit/graphvizBinPath'):
        os.environ['PATH'] += os.pathsep + os.path.normpath(s.value('pyArchInit/graphvizBinPath'))

    if not Pyarchinit_OS_Utility.checkpostgresinstallation() and s.value('pyArchInit/postgresBinPath'):
        os.environ['PATH'] += os.pathsep + os.path.normpath(s.value('pyArchInit/postgresBinPath'))

    # Check external programs (with timeout to prevent hanging on Windows)
    for cmd, label in [(['pg_dump', '-V'], 'postgres'), (['dot', '-V'], 'graphviz')]:
        try:
            subprocess.run(cmd, timeout=5,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                           **no_console_window())
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
            print(f"Note: {label} not found or timed out: {e}")
        _step()

    _step("Installing fonts...")

    # Install fonts
    FontManager.install_fonts(splash)
    _step()

    # Remove OpenCV directories on macOS
    PackageManager.remove_opencv_directories()
    _step()


def get_missing_packages() -> List[str]:
    """
    Check which packages are missing.

    Returns:
        List of missing packages
    """
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

    return missing_packages


def check_and_install_dependencies(splash=None) -> None:
    """
    Check and install missing dependencies.

    Args:
        splash: Optional splash screen (kept for backward compatibility, not used)
    """
    s = QgsSettings()
    missing_packages = get_missing_packages()

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
    # parentless: without this it opens behind QGIS / the Plugin Manager
    bring_to_front(dialog)
    dialog.exec()


def classFactory(iface):
    """
    Load the PyArchInitPlugin class.

    Args:
        iface: QGIS interface

    Returns:
        PyArchInitPlugin instance
    """
    # STEP 1: Check for missing packages FIRST (before showing splash)
    # This allows the install dialog to appear without being blocked by splash
    missing_packages = get_missing_packages()

    if missing_packages:
        # Show install dialog BEFORE splash screen
        print(f"PyArchInit: {len(missing_packages)} packages need to be installed...")
        show_install_dialog(missing_packages)
        # Mark as installed
        s = QgsSettings()
        s.setValue('pyArchInit/dependenciesInstalled', True)

    # STEP 2: Now show splash screen for the rest of the loading
    import time as _time

    SPLASH_MIN_SECONDS = 5.0
    splash = None
    splash_start = _time.perf_counter()

    try:
        from .gui.pyarchinit_splash import PyArchInitSplash
        splash = PyArchInitSplash(message="Loading PyArchInit...")
        splash.show()
        QApplication.processEvents()
    except Exception as e:
        print(f"Could not show splash screen: {e}")

    try:
        # Initialize environment (splash stays animated via processEvents)
        initialize_environment(splash)

        if splash:
            splash.set_message("Loading plugin modules...")
            QApplication.processEvents()

        from .pyarchinitPlugin import PyArchInitPlugin

        if splash:
            splash.set_message("Building interface...")
            QApplication.processEvents()

        plugin = PyArchInitPlugin(iface)

        if splash:
            splash.set_message("PyArchInit ready!")
            QApplication.processEvents()

            # Keep splash alive for the remaining minimum time
            # with smooth animation (event loop stays responsive)
            loading_messages = [
                "Scanning archaeological databases...",
                "Calibrating GIS projections...",
                "Synchronizing data layers...",
                "Loading stratigraphic modules...",
                "PyArchInit ready!",
            ]
            elapsed = _time.perf_counter() - splash_start
            remaining = SPLASH_MIN_SECONDS - elapsed

            if remaining > 0:
                msg_interval = remaining / len(loading_messages)
                msg_idx = 0
                msg_timer = 0.0
                last_t = _time.perf_counter()

                while True:
                    now = _time.perf_counter()
                    dt = now - last_t
                    last_t = now
                    msg_timer += dt

                    if msg_timer >= msg_interval and msg_idx < len(loading_messages):
                        splash.set_message(loading_messages[msg_idx])
                        msg_idx += 1
                        msg_timer = 0.0

                    QApplication.processEvents()

                    if (_time.perf_counter() - splash_start) >= SPLASH_MIN_SECONDS:
                        break

                    # Sleep briefly to avoid busy-waiting but keep ~60 FPS
                    _time.sleep(0.008)

            # Fade out
            splash.set_message("PyArchInit ready!")
            QApplication.processEvents()
            fade_duration = 0.6
            fade_start = _time.perf_counter()
            while True:
                elapsed_fade = _time.perf_counter() - fade_start
                if elapsed_fade >= fade_duration:
                    break
                opacity = 1.0 - (elapsed_fade / fade_duration)
                splash.setWindowOpacity(opacity)
                QApplication.processEvents()
                _time.sleep(0.016)

            splash.close()

        return plugin

    except Exception as e:
        if splash:
            splash.close()
        raise e