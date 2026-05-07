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
 *                                                                         *
 ***************************************************************************/
"""

import os
from os.path import expanduser
import zipfile
from .pyarchinit_OS_utility import Pyarchinit_OS_Utility


class pyarchinit_Folder_installation(object):
    HOME = expanduser("~")
    HOME += os.sep + 'pyarchinit'
    os.environ['PYARCHINIT_HOME'] = HOME
    RESOURCES_PATH = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'resources')

    OS_UTILITY = Pyarchinit_OS_Utility()

    # Bundled maintenance files in ~/pyarchinit/bin/ that the plugin
    # owns end-to-end (utility code + templates the user does NOT
    # customise). When the plugin ships a newer version of any of
    # these, install_or_update_maintenance_files() overwrites the
    # copy in HOME so bug fixes (e.g. dot.py edge parser) propagate
    # on plugin reload. Files NOT in this list (epoche_storiche.csv,
    # thesaurus_template.csv, template_report_adarte.docx) are left
    # alone after the first install — they are user-editable.
    MAINTENANCE_BIN_FILES = (
        'dot.py',
        'dottoxml.py',
        'X11Colors.py',
        'EM_palette.graphml',
    )

    def _safe_copy(self, src, dst, description=""):
        """Copy file with error handling - continues even if file is missing/corrupted"""
        try:
            self.OS_UTILITY.copy_file(src, dst)
            return True
        except Exception as e:
            print(f"[pyArchInit] Warning: Could not copy {description or src}: {e}")
            return False

    def _safe_copy_img(self, src, dst, description=""):
        """Copy file (overwrite) with error handling"""
        try:
            self.OS_UTILITY.copy_file_img(src, dst)
            return True
        except Exception as e:
            print(f"[pyArchInit] Warning: Could not copy {description or src}: {e}")
            return False

    def _safe_extract_zip(self, zip_path, extract_to, description=""):
        """Extract zip with error handling"""
        try:
            if os.path.exists(zip_path) and os.path.getsize(zip_path) > 1000:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_to)
                return True
            else:
                print(f"[pyArchInit] Warning: ZIP file missing or too small: {description or zip_path}")
                return False
        except Exception as e:
            print(f"[pyArchInit] Warning: Could not extract {description or zip_path}: {e}")
            return False

    def install_dir(self):
        """Install all pyArchInit directories and copy resource files.

        Creates directories first, then copies files with error handling
        so installation continues even if some files are missing/corrupted.
        """
        # === PHASE 1: Create ALL directories first ===
        home_DB_path = os.path.join(self.HOME, 'pyarchinit_DB_folder')
        home_bin_export_path = os.path.join(self.HOME, 'bin')
        doc_bin_export_path = os.path.join(self.HOME, 'DosCo')
        home_excel_path = os.path.join(self.HOME, 'pyarchinit_EXCEL_folder')
        home_PDF_path = os.path.join(self.HOME, 'pyarchinit_PDF_folder')
        home_MATRIX_path = os.path.join(self.HOME, 'pyarchinit_Matrix_folder')
        home_THUMBNAILS_path = os.path.join(self.HOME, 'pyarchinit_Thumbnails_folder')
        home_MAPS_path = os.path.join(self.HOME, 'pyarchinit_MAPS_folder')
        home_REPORT_path = os.path.join(self.HOME, 'pyarchinit_Report_folder')
        home_QUANT_path = os.path.join(self.HOME, 'pyarchinit_Quantificazioni_folder')
        home_TEST_path = os.path.join(self.HOME, 'pyarchinit_Test_folder')
        home_BACKUP_linux_path = os.path.join(self.HOME, 'pyarchinit_db_backup')
        home_image_export_path = os.path.join(self.HOME, 'pyarchinit_image_export')
        home_R_export_path = os.path.join(self.HOME, 'pyarchinit_R_export')

        # Create all directories
        for dir_path in [home_DB_path, home_bin_export_path, doc_bin_export_path,
                         home_excel_path, home_PDF_path, home_MATRIX_path,
                         home_THUMBNAILS_path, home_MAPS_path, home_REPORT_path,
                         home_QUANT_path, home_TEST_path, home_BACKUP_linux_path,
                         home_image_export_path, home_R_export_path]:
            self.OS_UTILITY.create_dir(dir_path)

        # === PHASE 2: Copy files to bin folder (with error handling) ===
        dbfiles_path = os.path.join(self.RESOURCES_PATH, 'dbfiles')

        # Files to copy to bin folder
        bin_files = [
            ('pyarchinit.sqlite', 'pyarchinit.sqlite'),
            ('EM_palette.graphml', 'EM_palette.graphml'),
            ('dottoxml.py', 'dottoxml.py'),
            ('dot.py', 'dot.py'),
            ('X11Colors.py', 'X11Colors.py'),
            ('thesaurus_template.csv', 'thesaurus_template.csv'),
            ('epoche_storiche.csv', 'epoche_storiche.csv'),
            ('template_report_adarte.docx', 'template_report_adarte.docx'),
        ]

        for src_name, dst_name in bin_files:
            src = os.path.join(dbfiles_path, src_name)
            dst = os.path.join(home_bin_export_path, dst_name)
            self._safe_copy(src, dst, src_name)

        # === PHASE 3: Copy files to DB folder ===
        db_files = [
            ('pyarchinit_db.sqlite', 'pyarchinit_db.sqlite'),
            ('logo.jpg', 'logo.jpg'),
            ('logo_2.png', 'logo_2.png'),
            ('logo_de.jpg', 'logo_de.jpg'),
        ]

        for src_name, dst_name in db_files:
            src = os.path.join(dbfiles_path, src_name)
            dst = os.path.join(home_DB_path, dst_name)
            self._safe_copy(src, dst, src_name)

        # === PHASE 4: Install config and additional files ===
        self.installConfigFile(home_DB_path)

    def installConfigFile(self, path):
        """Install config file and extract ZIP archives with error handling."""
        dbfiles_path = os.path.join(self.RESOURCES_PATH, 'dbfiles')
        home_bin_export_path = os.path.join(self.HOME, 'bin')

        # Copy config file
        self._safe_copy(
            os.path.join(dbfiles_path, 'config.cfg'),
            os.path.join(path, 'config.cfg'),
            'config.cfg'
        )

        # Copy logo files to DB path
        for logo_file in ['logo.jpg', 'logo_2.png', 'logo_de.jpg']:
            self._safe_copy(
                os.path.join(dbfiles_path, logo_file),
                os.path.join(path, logo_file),
                logo_file
            )

        # Refresh bundled maintenance files (dot.py, dottoxml.py, …) if
        # the plugin shipped a newer version. Idempotent.
        self.install_or_update_maintenance_files()

        # Extract ZIP archives (profile, rscripts, cambria fonts)
        zip_extracts = [
            ('profile.zip', 'profile'),
            ('rscripts.zip', 'rscripts'),
            ('cambria.zip', 'cambria'),
        ]

        for zip_name, folder_name in zip_extracts:
            zip_path = os.path.join(dbfiles_path, zip_name)
            extract_test = os.path.join(home_bin_export_path, folder_name)
            if not os.path.exists(extract_test):
                self._safe_extract_zip(zip_path, home_bin_export_path, zip_name)

        # Copy template file (after profile extraction)
        template_src = os.path.join(dbfiles_path, 'layout_TimeManager.qpt')
        template_dst = os.path.join(home_bin_export_path, 'profile', 'template', 'layout_TimeManager.qpt')
        # Ensure template directory exists
        template_dir = os.path.dirname(template_dst)
        if os.path.exists(template_dir):
            self._safe_copy(template_src, template_dst, 'layout_TimeManager.qpt')

    def install_or_update_maintenance_files(self):
        """Refresh bundled maintenance files in ~/pyarchinit/bin/ when the
        plugin ships a newer version.

        Compares mtime + size between the bundled source under
        resources/dbfiles/ and the installed copy under
        ~/pyarchinit/bin/. Overwrites the destination only when the
        source is strictly newer (mtime), or when sizes differ
        (covers the cross-machine case where mtime can't be trusted —
        e.g. after a fresh git checkout that resets all mtimes to
        check-out time).

        Safe to call on every plugin reload — idempotent when the
        bundled file equals the installed copy. Files NOT in
        MAINTENANCE_BIN_FILES are left untouched (user-editable
        templates and CSVs).

        This closes the gap that prevented bug fixes in dot.py /
        dottoxml.py from reaching ~/pyarchinit/bin/ on existing
        installations: install_dir() runs only on first install,
        and copy_file() is a no-op when the destination already
        exists. install_or_update_maintenance_files() runs on every
        reload via initialize_environment() in __init__.py.
        """
        home_bin = os.path.join(self.HOME, 'bin')
        dbfiles = os.path.join(self.RESOURCES_PATH, 'dbfiles')
        if not os.path.isdir(home_bin):
            # First install hasn't run yet; install_dir() is the
            # right entry point in that case (it calls us at the end).
            return
        if not os.path.isdir(dbfiles):
            return
        for name in self.MAINTENANCE_BIN_FILES:
            src = os.path.join(dbfiles, name)
            dst = os.path.join(home_bin, name)
            if not os.path.exists(src):
                continue
            if not os.path.exists(dst):
                # Bin folder existed but this specific file is missing
                # — install it now (use overwrite-capable helper).
                self._safe_copy_img(src, dst, name)
                continue
            try:
                src_mtime = os.path.getmtime(src)
                dst_mtime = os.path.getmtime(dst)
                src_size = os.path.getsize(src)
                dst_size = os.path.getsize(dst)
            except OSError:
                continue
            if src_mtime > dst_mtime or src_size != dst_size:
                self._safe_copy_img(src, dst, name)
