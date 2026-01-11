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
            ('spatialite_convert.exe', 'spatialite_convert.exe'),
            ('sqldiff.exe', 'sqldiff.exe'),
            ('sqldiff_linux', 'sqldiff_linux'),
            ('sqldiff_osx', 'sqldiff_osx'),
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
