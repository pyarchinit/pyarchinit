#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
/***************************************************************************
        pyArchInit Plugin  - A QGIS plugin to manage archaeological dataset
                             -------------------
        begin                : 2024
        copyright            : (C) 2024 by Enzo Cocca <enzo.ccc@gmail.com>
        email                : enzo.ccc@gmail.com
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
import shutil
import subprocess
import sys

from qgis.PyQt.QtCore import Qt, QSize
from qgis.PyQt.QtGui import QIcon, QPixmap
from qgis.PyQt.QtWidgets import (
    QDialog, QMessageBox, QListWidgetItem, QApplication, QMenu, QFileDialog
)
from qgis.PyQt.uic import loadUiType

from ..modules.db.pyarchinit_conn_strings import Connection
from ..modules.db.pyarchinit_db_manager import get_db_manager
from ..modules.db.pyarchinit_utility import Utility
from ..modules.utility.pyarchinit_OS_utility import Pyarchinit_OS_Utility
from ..modules.utility.remote_image_loader import load_icon, get_image_path

# Load UI
MAIN_DIALOG_CLASS, _ = loadUiType(
    os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'pyarchinit_image_search_dialog.ui')
)


class pyarchinit_Image_Search(QDialog, MAIN_DIALOG_CLASS):
    """Dialog for global image search across all entity types."""

    ENTITY_TYPE_MAP = {
        '-- Tutti --': None,
        'US': 'US',
        'Pottery': 'CERAMICA',
        'Materiali': 'REPERTO',
        'Tomba': 'TOMBA',
        'Struttura': 'STRUTTURA',
        'UT': 'UT'
    }

    def __init__(self, iface=None, parent=None):
        super().__init__(parent)
        self.iface = iface
        self.setupUi(self)
        self.setWindowTitle("pyArchInit - Ricerca Immagini")

        # Utilities
        self.UTILITY = Utility()

        # Database connection
        self.DB_MANAGER = None
        self.DB_SERVER = "not defined"
        self.connect_to_db()

        # Store search results
        self.search_results = []
        self.current_selection = None

        # Setup UI connections
        self.setup_connections()

        # Setup context menu for right-click export
        self.setup_context_menu()

        # Load initial data
        self.load_sites()

    def connect_to_db(self):
        """Connect to the database."""
        conn = Connection()
        conn_str = conn.conn_str()

        # Determine DB type
        test_conn = conn_str.find('sqlite')
        if test_conn == 0:
            self.DB_SERVER = "sqlite"
        else:
            self.DB_SERVER = "postgres"

        try:
            self.DB_MANAGER = get_db_manager(conn_str, use_singleton=True)
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Connessione al database fallita:\n{str(e)}")
            self.DB_MANAGER = None

    def setup_connections(self):
        """Setup signal/slot connections."""
        self.pushButton_search.clicked.connect(self.perform_search)
        self.pushButton_clear.clicked.connect(self.clear_filters)
        self.pushButton_goto_record.clicked.connect(self.goto_record)
        self.pushButton_open_image.clicked.connect(self.open_image)
        self.pushButton_open_media_manager.clicked.connect(self.open_media_manager)
        self.pushButton_export_image.clicked.connect(self.export_image)

        self.listWidget_results.itemSelectionChanged.connect(self.on_selection_changed)
        self.listWidget_results.itemDoubleClicked.connect(self.open_image)

        self.comboBox_sito.currentTextChanged.connect(self.on_sito_changed)
        self.comboBox_entity_type.currentTextChanged.connect(self.on_entity_type_changed)
        self.checkBox_untagged.toggled.connect(self.on_untagged_toggled)

    def setup_context_menu(self):
        """Setup context menu for right-click on results list."""
        self.listWidget_results.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.listWidget_results.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, pos):
        """Show context menu at the given position."""
        item = self.listWidget_results.itemAt(pos)
        if not item:
            return

        menu = QMenu(self)

        action_open = menu.addAction("Apri immagine")
        action_open.triggered.connect(self.open_image)

        action_export = menu.addAction("Esporta immagine...")
        action_export.triggered.connect(self.export_image)

        menu.addSeparator()

        action_goto = menu.addAction("Vai al record")
        action_goto.triggered.connect(self.goto_record)

        menu.exec(self.listWidget_results.mapToGlobal(pos))

    def load_sites(self):
        """Load available sites into combobox."""
        if not self.DB_MANAGER:
            return

        try:
            # Use the same method as other forms
            sito_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('site_table', 'sito', 'SITE'))
            try:
                sito_vl.remove('')
            except:
                pass

            self.comboBox_sito.clear()
            self.comboBox_sito.addItem('')  # Empty option for "all"
            sito_vl.sort()
            self.comboBox_sito.addItems(sito_vl)
        except Exception as e:
            print(f"Error loading sites: {e}")

    def on_sito_changed(self, sito):
        """Load areas when site changes."""
        if not self.DB_MANAGER:
            return

        self.comboBox_area.clear()
        self.comboBox_area.addItem('')
        self.comboBox_us.clear()
        self.comboBox_us.addItem('')

        if not sito:
            return

        try:
            # Load areas for selected site
            area_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('us_table', 'area', 'US'))
            try:
                area_vl.remove('')
            except:
                pass
            area_vl.sort()
            self.comboBox_area.addItems([str(a) for a in area_vl])

            # Load US for selected site
            us_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('us_table', 'us', 'US'))
            try:
                us_vl.remove('')
            except:
                pass
            us_vl.sort(key=lambda x: int(x) if str(x).isdigit() else 0)
            self.comboBox_us.addItems([str(u) for u in us_vl])
        except Exception as e:
            print(f"Error loading areas/US: {e}")

    def on_entity_type_changed(self, entity_type):
        """Show/hide inventory number field based on entity type."""
        show_inv = entity_type == 'Materiali'
        self.label_inventario.setVisible(show_inv)
        self.lineEdit_inventario.setVisible(show_inv)

    def on_untagged_toggled(self, checked):
        """Enable/disable entity filters when untagged mode is active."""
        enabled = not checked
        self.comboBox_entity_type.setEnabled(enabled)
        self.comboBox_sito.setEnabled(enabled)
        self.comboBox_area.setEnabled(enabled)
        self.comboBox_us.setEnabled(enabled)
        self.lineEdit_inventario.setEnabled(enabled)

    def clear_filters(self):
        """Clear all search filters."""
        self.lineEdit_text_search.clear()
        self.comboBox_entity_type.setCurrentIndex(0)
        self.comboBox_sito.setCurrentIndex(0)
        self.comboBox_area.clear()
        self.comboBox_area.addItem('')
        self.comboBox_us.clear()
        self.comboBox_us.addItem('')
        self.lineEdit_inventario.clear()
        self.checkBox_untagged.setChecked(False)
        self.checkBox_partial.setChecked(True)

    def perform_search(self):
        """Execute the search based on current filters."""
        if not self.DB_MANAGER:
            QMessageBox.warning(self, "Attenzione", "Database non connesso.\nVerificare la connessione al database.")
            return

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

        try:
            text_filter = self.lineEdit_text_search.text().strip() or None
            use_like = self.checkBox_partial.isChecked()

            if self.checkBox_untagged.isChecked():
                # Search untagged images
                results = self.DB_MANAGER.search_untagged_media(text_filter=text_filter)
                self.display_untagged_results(results)
            else:
                # Search tagged images
                entity_type_text = self.comboBox_entity_type.currentText()
                entity_type = self.ENTITY_TYPE_MAP.get(entity_type_text)

                sito = self.comboBox_sito.currentText().strip() or None
                area = self.comboBox_area.currentText().strip() or None
                us = self.comboBox_us.currentText().strip() or None
                numero_inv = self.lineEdit_inventario.text().strip() or None

                results = self.DB_MANAGER.search_tagged_media_flexible(
                    entity_type=entity_type,
                    sito=sito,
                    area=area,
                    us=us,
                    numero_inventario=numero_inv,
                    text_filter=text_filter,
                    use_like=use_like
                )
                self.display_tagged_results(results, entity_type)

        except Exception as e:
            import traceback
            QMessageBox.critical(self, "Errore", f"Errore durante la ricerca:\n{str(e)}\n\n{traceback.format_exc()}")
        finally:
            QApplication.restoreOverrideCursor()

    def display_untagged_results(self, results):
        """Display untagged search results."""
        self.listWidget_results.clear()
        self.search_results = []

        if not results:
            self.label_results_count.setText("0 immagini trovate")
            return

        # Convert to list if needed
        if not isinstance(results, list):
            results = list(results)

        conn = Connection()
        thumb_path_config = conn.thumb_path()
        thumb_path_str = thumb_path_config.get('thumb_path', '')

        for row in results:
            # Untagged: id_media, filename, filepath, thumb_path
            id_media = row[0] if len(row) > 0 else None
            filename = str(row[1]) if len(row) > 1 else ''
            filepath = str(row[2]) if len(row) > 2 else ''
            thumb_path = str(row[3]) if len(row) > 3 and row[3] else ''

            # filepath is stored as absolute in the MEDIA table

            item = QListWidgetItem(filename)
            item.setData(Qt.ItemDataRole.UserRole, {
                'id_media': id_media,
                'filename': filename,
                'filepath': filepath,
                'thumb_path': thumb_path,
                'entity_type': None,
                'sito': None,
                'area': None,
                'us': None,
                'tagged': False
            })

            if thumb_path:
                icon = load_icon(get_image_path(thumb_path_str, thumb_path))
                item.setIcon(icon)

            self.listWidget_results.addItem(item)
            self.search_results.append(row)

        self.label_results_count.setText(f"{len(results)} immagini non taggate trovate")

    def display_tagged_results(self, results, entity_type):
        """Display tagged search results."""
        self.listWidget_results.clear()
        self.search_results = []

        if not results:
            self.label_results_count.setText("0 immagini trovate")
            return

        # Convert to list if needed
        if not isinstance(results, list):
            results = list(results)

        conn = Connection()
        thumb_path_config = conn.thumb_path()
        thumb_path_str = thumb_path_config.get('thumb_path', '')

        for row in results:
            # Tagged: filepath, media_name, sito, area, us/other
            thumb_path = str(row[0]) if len(row) > 0 else ''
            filename = str(row[1]) if len(row) > 1 else ''
            sito = str(row[2]) if len(row) > 2 else ''
            area_or_other = str(row[3]) if len(row) > 3 else ''
            us_or_other = str(row[4]) if len(row) > 4 else ''

            # Try to get the full file path from the database
            filepath = ''
            if filename:
                try:
                    search_dict = {'filename': f"'{filename}'"}
                    media_data = self.DB_MANAGER.query_bool(search_dict, 'MEDIA')
                    if media_data:
                        filepath = media_data[0].filepath
                except:
                    pass

            item = QListWidgetItem(filename)
            item.setData(Qt.ItemDataRole.UserRole, {
                'filename': filename,
                'filepath': filepath,
                'thumb_path': thumb_path,
                'entity_type': entity_type,
                'sito': sito,
                'area': area_or_other,
                'us': us_or_other,
                'tagged': True
            })

            if thumb_path:
                icon = load_icon(get_image_path(thumb_path_str, thumb_path))
                item.setIcon(icon)

            self.listWidget_results.addItem(item)
            self.search_results.append(row)

        self.label_results_count.setText(f"{len(results)} immagini trovate")

    def on_selection_changed(self):
        """Update details panel when selection changes."""
        items = self.listWidget_results.selectedItems()
        if not items:
            self.clear_details()
            return

        item = items[0]
        data = item.data(Qt.ItemDataRole.UserRole)
        self.current_selection = data

        # Update labels
        self.label_filename.setText(data.get('filename', '-'))

        if data.get('tagged'):
            entity_type = data.get('entity_type', '-')
            self.label_entity_info.setText(entity_type if entity_type else 'Varie entità')
            self.label_sito_info.setText(data.get('sito', '-'))
            self.label_area_info.setText(f"{data.get('area', '-')} / {data.get('us', '-')}")
        else:
            self.label_entity_info.setText('Non taggata')
            self.label_sito_info.setText('-')
            self.label_area_info.setText('-')

        # Update preview
        conn = Connection()
        thumb_path_config = conn.thumb_path()
        thumb_path_str = thumb_path_config.get('thumb_path', '')
        thumb_path = data.get('thumb_path', '')

        if thumb_path:
            full_path = get_image_path(thumb_path_str, thumb_path)
            pixmap = QPixmap(full_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.label_preview.setPixmap(scaled)
            else:
                self.label_preview.setText('Anteprima\nnon disponibile')
        else:
            self.label_preview.setText('Anteprima\nnon disponibile')

    def clear_details(self):
        """Clear the details panel."""
        self.label_filename.setText('-')
        self.label_entity_info.setText('-')
        self.label_sito_info.setText('-')
        self.label_area_info.setText('-')
        self.label_preview.setText('Anteprima')
        self.current_selection = None

    def get_original_filepath(self):
        """Get the original file path for the current selection."""
        if not self.current_selection:
            return None

        filepath = self.current_selection.get('filepath', '')

        # If no filepath, try to find it from the database using filename
        if not filepath:
            filename = self.current_selection.get('filename', '')
            if filename and self.DB_MANAGER:
                try:
                    search_dict = {'filename': f"'{filename}'"}
                    media_data = self.DB_MANAGER.query_bool(search_dict, 'MEDIA')
                    if media_data:
                        # filepath is stored as absolute path in MEDIA table
                        filepath = media_data[0].filepath
                except Exception as e:
                    print(f"Error getting filepath: {e}")

        return filepath

    def get_resize_filepath(self):
        """Get the resize image path for the current selection.

        Pattern: thumb_resize_str (from config) + path_resize (from MEDIA_THUMB table)
        """
        if not self.current_selection:
            return None

        filename = self.current_selection.get('filename', '')
        if not filename or not self.DB_MANAGER:
            return None

        try:
            # Get thumb_resize path from config
            conn = Connection()
            thumb_resize = conn.thumb_resize()
            thumb_resize_str = thumb_resize.get('thumb_resize', '')

            # Search MEDIA_THUMB table by media_filename
            search_dict = {'media_filename': f"'{filename}'"}
            thumb_data = self.DB_MANAGER.query_bool(search_dict, 'MEDIA_THUMB')

            if thumb_data:
                # Get path_resize and build full path
                path_resize = str(thumb_data[0].path_resize)
                full_path = os.path.join(thumb_resize_str, path_resize) if thumb_resize_str else path_resize
                return full_path
        except Exception as e:
            print(f"Error getting resize filepath: {e}")

        return None

    def goto_record(self):
        """Open the form for the associated record."""
        if not self.current_selection:
            QMessageBox.information(self, "Info", "Seleziona un'immagine prima")
            return

        if not self.current_selection.get('tagged'):
            QMessageBox.information(self, "Info", "L'immagine non è associata a nessun record.\nUsa il Media Manager per taggarla.")
            return

        entity_type = self.current_selection.get('entity_type')
        sito = self.current_selection.get('sito')
        area = self.current_selection.get('area')
        us = self.current_selection.get('us')

        try:
            if entity_type == 'US':
                self._open_us_form(sito, area, us)
            elif entity_type == 'CERAMICA':
                self._open_pottery_form(sito, us)  # us contains id_number for pottery
            elif entity_type == 'REPERTO':
                self._open_inventario_form(sito, us)  # us contains numero_inventario
            elif entity_type == 'TOMBA':
                self._open_tomba_form(sito, us)  # us contains nr_scheda_taf
            elif entity_type == 'STRUTTURA':
                self._open_struttura_form(sito, area, us)  # area=sigla, us=numero
            elif entity_type == 'UT':
                self._open_ut_form(sito, us)  # sito=progetto, us=nr_ut
            else:
                QMessageBox.information(self, "Info",
                    f"Tipo entità non riconosciuto: {entity_type}")
        except Exception as e:
            QMessageBox.warning(self, "Errore", f"Impossibile aprire la scheda:\n{str(e)}")

    def _open_us_form(self, sito, area, us):
        """Open US form and navigate to record."""
        from .US_USM import pyarchinit_US

        us_form = pyarchinit_US(self.iface)
        us_form.show()

        search_dict = {
            'sito': f"'{sito}'",
            'area': f"'{area}'",
            'us': us
        }

        res = us_form.DB_MANAGER.query_bool(search_dict, 'US')
        if res:
            us_form.DATA_LIST = res
            us_form.REC_TOT = len(res)
            us_form.REC_CORR = 0
            us_form.BROWSE_STATUS = "b"
            us_form.fill_fields(0)
            us_form.set_rec_counter(len(res), 1)
            us_form.label_status.setText("Aperto da Ricerca Immagini")
        else:
            QMessageBox.information(self, "Info", f"US {us} non trovata nel sito {sito}")

    def _open_pottery_form(self, sito, id_number):
        """Open Pottery form and navigate to record."""
        from .pyarchinit_Pottery_mainapp import pyarchinit_Pottery

        pottery_form = pyarchinit_Pottery(self.iface)
        pottery_form.show()

        search_dict = {
            'sito': f"'{sito}'",
            'id_number': f"'{id_number}'"
        }

        res = pottery_form.DB_MANAGER.query_bool(search_dict, 'POTTERY')
        if res:
            pottery_form.DATA_LIST = res
            pottery_form.REC_TOT = len(res)
            pottery_form.REC_CORR = 0
            pottery_form.BROWSE_STATUS = "b"
            pottery_form.fill_fields(0)
            pottery_form.set_rec_counter(len(res), 1)
            pottery_form.label_status.setText("Aperto da Ricerca Immagini")
        else:
            QMessageBox.information(self, "Info", f"Ceramica {id_number} non trovata nel sito {sito}")

    def _open_inventario_form(self, sito, numero_inventario):
        """Open Inventario Materiali form and navigate to record."""
        from .Inv_Materiali import pyarchinit_Inventario_reperti

        inv_form = pyarchinit_Inventario_reperti(self.iface)
        inv_form.show()

        search_dict = {
            'sito': f"'{sito}'",
            'numero_inventario': numero_inventario
        }

        res = inv_form.DB_MANAGER.query_bool(search_dict, 'INVENTARIO_MATERIALI')
        if res:
            inv_form.DATA_LIST = res
            inv_form.REC_TOT = len(res)
            inv_form.REC_CORR = 0
            inv_form.BROWSE_STATUS = "b"
            inv_form.fill_fields(0)
            inv_form.set_rec_counter(len(res), 1)
            inv_form.label_status.setText("Aperto da Ricerca Immagini")
        else:
            QMessageBox.information(self, "Info", f"Reperto {numero_inventario} non trovato nel sito {sito}")

    def _open_tomba_form(self, sito, nr_scheda_taf):
        """Open Tomba form and navigate to record."""
        from .Tomba import pyarchinit_Tomba

        tomba_form = pyarchinit_Tomba(self.iface)
        tomba_form.show()

        search_dict = {
            'sito': f"'{sito}'",
            'nr_scheda_taf': nr_scheda_taf
        }

        res = tomba_form.DB_MANAGER.query_bool(search_dict, 'TOMBA')
        if res:
            tomba_form.DATA_LIST = res
            tomba_form.REC_TOT = len(res)
            tomba_form.REC_CORR = 0
            tomba_form.BROWSE_STATUS = "b"
            tomba_form.fill_fields(0)
            tomba_form.set_rec_counter(len(res), 1)
            tomba_form.label_status.setText("Aperto da Ricerca Immagini")
        else:
            QMessageBox.information(self, "Info", f"Tomba {nr_scheda_taf} non trovata nel sito {sito}")

    def _open_struttura_form(self, sito, sigla, numero):
        """Open Struttura form and navigate to record."""
        from .Struttura import pyarchinit_Struttura

        struttura_form = pyarchinit_Struttura(self.iface)
        struttura_form.show()

        search_dict = {
            'sito': f"'{sito}'",
            'sigla_struttura': f"'{sigla}'",
            'numero_struttura': numero
        }

        res = struttura_form.DB_MANAGER.query_bool(search_dict, 'STRUTTURA')
        if res:
            struttura_form.DATA_LIST = res
            struttura_form.REC_TOT = len(res)
            struttura_form.REC_CORR = 0
            struttura_form.BROWSE_STATUS = "b"
            struttura_form.fill_fields(0)
            struttura_form.set_rec_counter(len(res), 1)
            struttura_form.label_status.setText("Aperto da Ricerca Immagini")
        else:
            QMessageBox.information(self, "Info", f"Struttura {sigla} {numero} non trovata nel sito {sito}")

    def _open_ut_form(self, progetto, nr_ut):
        """Open UT form and navigate to record."""
        from .UT import pyarchinit_UT

        ut_form = pyarchinit_UT(self.iface)
        ut_form.show()

        search_dict = {
            'progetto': f"'{progetto}'",
            'nr_ut': f"'{nr_ut}'"
        }

        res = ut_form.DB_MANAGER.query_bool(search_dict, 'UT')
        if res:
            ut_form.DATA_LIST = res
            ut_form.REC_TOT = len(res)
            ut_form.REC_CORR = 0
            ut_form.BROWSE_STATUS = "b"
            ut_form.fill_fields(0)
            ut_form.set_rec_counter(len(res), 1)
            ut_form.label_status.setText("Aperto da Ricerca Immagini")
        else:
            QMessageBox.information(self, "Info", f"UT {nr_ut} non trovata nel progetto {progetto}")

    def open_image(self):
        """Open the selected image in the ImageViewer dialog."""
        if not self.current_selection:
            QMessageBox.information(self, "Info", "Seleziona un'immagine prima")
            return

        # Use resize filepath (thumb_resize_str + path_resize from MEDIA_THUMB)
        filepath = self.get_resize_filepath()

        if filepath and os.path.exists(filepath):
            from ..gui.imageViewer import ImageViewer
            dlg = ImageViewer()
            dlg.show_image(filepath)
            dlg.exec()
        else:
            # Fallback to original filepath
            filepath = self.get_original_filepath()
            if filepath and os.path.exists(filepath):
                if sys.platform == 'darwin':
                    subprocess.call(['open', filepath])
                elif sys.platform == 'win32':
                    os.startfile(filepath)
                else:
                    subprocess.call(['xdg-open', filepath])
            else:
                QMessageBox.warning(self, "Attenzione", f"File non trovato:\n{filepath}")

    def export_image(self):
        """Export the selected image to a user-chosen location."""
        if not self.current_selection:
            QMessageBox.information(self, "Info", "Seleziona un'immagine prima")
            return

        # Try original filepath first, then resize filepath
        filepath = self.get_original_filepath()
        if not filepath or not os.path.exists(filepath):
            filepath = self.get_resize_filepath()

        if not filepath or not os.path.exists(filepath):
            QMessageBox.warning(self, "Attenzione", "File sorgente non trovato")
            return

        # Get original filename
        filename = self.current_selection.get('filename', os.path.basename(filepath))

        # Ask user for save location
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Esporta immagine",
            os.path.join(os.path.expanduser("~"), "Desktop", filename),
            "Tutti i file (*.*)"
        )

        if save_path:
            try:
                shutil.copy2(filepath, save_path)
                QMessageBox.information(self, "Successo", f"Immagine esportata con successo:\n{save_path}")
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Errore durante l'esportazione:\n{str(e)}")

    def open_media_manager(self):
        """Open the Media Manager dialog."""
        try:
            from .Image_viewer import Main
            dialog = Main(self.iface)
            dialog.show()
        except Exception as e:
            QMessageBox.warning(self, "Errore", f"Impossibile aprire Media Manager:\n{str(e)}")
