#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dialog per l'importazione dei dati TMA da vari formati
"""

import os
import sys
from typing import Dict, List

from qgis.PyQt.QtCore import Qt, QThread, pyqtSignal
from qgis.PyQt.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                                 QPushButton, QListWidget, QTextEdit, QFileDialog,
                                 QGroupBox, QTableWidget, QTableWidgetItem, 
                                 QProgressBar, QMessageBox, QComboBox, QLineEdit,
                                 QAbstractItemView, QHeaderView, QCheckBox)
from qgis.PyQt.QtGui import QIcon

from ..modules.utility.tma_import_parser import TMAFieldMapping
from ..modules.utility.tma_import_parser_extended import TMAImportManagerExtended
# # Usa il parser esteso invece di quello base
# from modules.utility.tma_import_parser_extended import TMAImportParserExtended
# self.parser = TMAImportParserExtended()
# Usa il parser esteso invece di quello base
# from ..modules.utility.tma_import_parser_extended  import TMAImportParserExtended



class ImportWorker(QThread):
    """Thread worker per l'importazione in background"""
    
    progress = pyqtSignal(int)
    log_message = pyqtSignal(str)
    finished = pyqtSignal(dict)
    
    def __init__(self, import_manager, files, use_festos_parser=False):
        super().__init__()
        self.import_manager = import_manager
        self.files = files
        self.use_festos_parser = use_festos_parser
        self.results = {}
    
    def run(self):
        """Esegue l'importazione"""
        total_files = len(self.files)
        
        for idx, file_path in enumerate(self.files):
            self.log_message.emit(f"Importazione file: {os.path.basename(file_path)}")
            
            # Determina se usare il parser Festos
            use_festos = self.use_festos_parser and file_path.lower().endswith('.docx')
            
            imported, errors, warnings = self.import_manager.import_file(
                file_path, 
                use_festos_parser=use_festos
            )
            
            self.results[file_path] = {
                'imported': imported,
                'errors': errors,
                'warnings': warnings
            }
            
            # Log errori e warning
            for error in errors:
                self.log_message.emit(f"ERRORE: {error}")
            
            for warning in warnings:
                self.log_message.emit(f"AVVISO: {warning}")
            
            self.log_message.emit(f"Importati {imported} record da {os.path.basename(file_path)}")
            self.log_message.emit("-" * 50)
            
            # Aggiorna progress
            progress_value = int((idx + 1) / total_files * 100)
            self.progress.emit(progress_value)
        
        self.finished.emit(self.results)


class TMAImportDialog(QDialog):
    """Dialog per l'importazione dei dati TMA"""
    
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.import_manager = TMAImportManagerExtended(db_manager)
        self.files_to_import = []
        self.custom_mapping = {}
        self.init_ui()
    
    def init_ui(self):
        """Inizializza l'interfaccia"""
        self.setWindowTitle("Importazione dati TMA")
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout()
        
        # Sezione selezione file
        file_group = QGroupBox("Selezione file")
        file_layout = QVBoxLayout()
        
        # Pulsanti per aggiungere file
        btn_layout = QHBoxLayout()
        
        self.btn_add_excel = QPushButton("Aggiungi Excel")
        self.btn_add_excel.clicked.connect(lambda: self.add_files("Excel Files (*.xlsx *.xls)"))
        btn_layout.addWidget(self.btn_add_excel)
        
        self.btn_add_csv = QPushButton("Aggiungi CSV")
        self.btn_add_csv.clicked.connect(lambda: self.add_files("CSV Files (*.csv)"))
        btn_layout.addWidget(self.btn_add_csv)
        
        self.btn_add_json = QPushButton("Aggiungi JSON")
        self.btn_add_json.clicked.connect(lambda: self.add_files("JSON Files (*.json)"))
        btn_layout.addWidget(self.btn_add_json)
        
        self.btn_add_xml = QPushButton("Aggiungi XML")
        self.btn_add_xml.clicked.connect(lambda: self.add_files("XML Files (*.xml)"))
        btn_layout.addWidget(self.btn_add_xml)
        
        self.btn_add_docx = QPushButton("Aggiungi DOCX")
        self.btn_add_docx.clicked.connect(lambda: self.add_files("Word Files (*.docx)"))
        btn_layout.addWidget(self.btn_add_docx)
        
        self.btn_clear = QPushButton("Pulisci lista")
        self.btn_clear.clicked.connect(self.clear_files)
        btn_layout.addWidget(self.btn_clear)
        
        file_layout.addLayout(btn_layout)
        
        # Lista file selezionati
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        file_layout.addWidget(self.file_list)
        
        # Pulsante rimuovi file selezionati
        self.btn_remove_selected = QPushButton("Rimuovi selezionati")
        self.btn_remove_selected.clicked.connect(self.remove_selected_files)
        file_layout.addWidget(self.btn_remove_selected)
        
        # Checkbox per parser Festos (solo per DOCX)
        self.check_festos_parser = QCheckBox("Usa parser Festos per file DOCX (inventari cassette)")
        self.check_festos_parser.setToolTip("Abilita il parser specializzato per gli inventari di Festos")
        file_layout.addWidget(self.check_festos_parser)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Sezione mapping personalizzato
        mapping_group = QGroupBox("Mapping campi personalizzato (opzionale)")
        mapping_layout = QVBoxLayout()
        
        # Checkbox per abilitare mapping personalizzato
        self.check_custom_mapping = QCheckBox("Usa mapping personalizzato")
        self.check_custom_mapping.toggled.connect(self.toggle_custom_mapping)
        mapping_layout.addWidget(self.check_custom_mapping)
        
        # Tabella per mapping
        self.mapping_table = QTableWidget()
        self.mapping_table.setColumnCount(2)
        self.mapping_table.setHorizontalHeaderLabels(["Campo file origine", "Campo database TMA"])
        self.mapping_table.horizontalHeader().setStretchLastSection(True)
        self.mapping_table.setEnabled(False)
        
        # Aggiungi alcune righe di esempio
        self.add_mapping_examples()
        
        mapping_layout.addWidget(self.mapping_table)
        
        # Pulsanti per gestire mapping
        mapping_btn_layout = QHBoxLayout()
        
        self.btn_add_mapping = QPushButton("Aggiungi riga")
        self.btn_add_mapping.clicked.connect(self.add_mapping_row)
        self.btn_add_mapping.setEnabled(False)
        mapping_btn_layout.addWidget(self.btn_add_mapping)
        
        self.btn_remove_mapping = QPushButton("Rimuovi riga")
        self.btn_remove_mapping.clicked.connect(self.remove_mapping_row)
        self.btn_remove_mapping.setEnabled(False)
        mapping_btn_layout.addWidget(self.btn_remove_mapping)
        
        self.btn_load_mapping = QPushButton("Carica da file")
        self.btn_load_mapping.clicked.connect(self.load_mapping_from_file)
        self.btn_load_mapping.setEnabled(False)
        mapping_btn_layout.addWidget(self.btn_load_mapping)
        
        self.btn_save_mapping = QPushButton("Salva mapping")
        self.btn_save_mapping.clicked.connect(self.save_mapping_to_file)
        self.btn_save_mapping.setEnabled(False)
        mapping_btn_layout.addWidget(self.btn_save_mapping)
        
        mapping_layout.addLayout(mapping_btn_layout)
        
        mapping_group.setLayout(mapping_layout)
        layout.addWidget(mapping_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Log output
        log_group = QGroupBox("Log importazione")
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        # Pulsanti finali
        button_layout = QHBoxLayout()
        
        self.btn_preview = QPushButton("Anteprima")
        self.btn_preview.clicked.connect(self.preview_import)
        button_layout.addWidget(self.btn_preview)
        
        self.btn_import = QPushButton("Importa")
        self.btn_import.clicked.connect(self.start_import)
        button_layout.addWidget(self.btn_import)
        
        self.btn_close = QPushButton("Chiudi")
        self.btn_close.clicked.connect(self.close)
        button_layout.addWidget(self.btn_close)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def add_files(self, filter_str):
        """Aggiunge file alla lista"""
        files, _ = QFileDialog.getOpenFileNames(self, "Seleziona file", "", filter_str)
        
        for file_path in files:
            if file_path not in self.files_to_import:
                self.files_to_import.append(file_path)
                self.file_list.addItem(os.path.basename(file_path))
    
    def remove_selected_files(self):
        """Rimuove i file selezionati dalla lista"""
        selected_items = self.file_list.selectedItems()
        
        for item in selected_items:
            row = self.file_list.row(item)
            self.file_list.takeItem(row)
            del self.files_to_import[row]
    
    def clear_files(self):
        """Pulisce la lista dei file"""
        self.file_list.clear()
        self.files_to_import = []
    
    def toggle_custom_mapping(self, checked):
        """Abilita/disabilita mapping personalizzato"""
        self.mapping_table.setEnabled(checked)
        self.btn_add_mapping.setEnabled(checked)
        self.btn_remove_mapping.setEnabled(checked)
        self.btn_load_mapping.setEnabled(checked)
        self.btn_save_mapping.setEnabled(checked)
    
    def add_mapping_examples(self):
        """Aggiunge esempi di mapping nella tabella"""
        examples = [
            ("numero_inventario", "madi"),
            ("tipo_materiale", "ogtm"),
            ("unita_stratigrafica", "dscu"),
            ("peso_grammi", "peso")
        ]
        
        for source, target in examples:
            row = self.mapping_table.rowCount()
            self.mapping_table.insertRow(row)
            
            # Crea combo box per campo database
            combo = QComboBox()
            combo.addItems(sorted(TMAFieldMapping.FIELD_MAPPINGS.keys()))
            combo.setCurrentText(target)
            
            self.mapping_table.setItem(row, 0, QTableWidgetItem(source))
            self.mapping_table.setCellWidget(row, 1, combo)
    
    def add_mapping_row(self):
        """Aggiunge una nuova riga di mapping"""
        row = self.mapping_table.rowCount()
        self.mapping_table.insertRow(row)
        
        # Crea combo box per campo database
        combo = QComboBox()
        combo.addItems(sorted(TMAFieldMapping.FIELD_MAPPINGS.keys()))
        
        self.mapping_table.setItem(row, 0, QTableWidgetItem(""))
        self.mapping_table.setCellWidget(row, 1, combo)
    
    def remove_mapping_row(self):
        """Rimuove la riga di mapping selezionata"""
        current_row = self.mapping_table.currentRow()
        if current_row >= 0:
            self.mapping_table.removeRow(current_row)
    
    def get_custom_mapping(self):
        """Ottiene il mapping personalizzato dalla tabella"""
        mapping = {}
        
        if self.check_custom_mapping.isChecked():
            for row in range(self.mapping_table.rowCount()):
                source_item = self.mapping_table.item(row, 0)
                target_widget = self.mapping_table.cellWidget(row, 1)
                
                if source_item and target_widget and source_item.text():
                    source = source_item.text().strip()
                    target = target_widget.currentText()
                    
                    # Aggiorna il mapping globale
                    if target in TMAFieldMapping.FIELD_MAPPINGS:
                        TMAFieldMapping.FIELD_MAPPINGS[target].append(source.lower())
                        mapping[source] = target
        
        return mapping
    
    def load_mapping_from_file(self):
        """Carica mapping da file JSON"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Carica mapping", "", "JSON Files (*.json)")
        
        if file_path:
            try:
                import json
                with open(file_path, 'r') as f:
                    mapping = json.load(f)
                
                # Pulisci tabella
                self.mapping_table.setRowCount(0)
                
                # Popola tabella
                for source, target in mapping.items():
                    self.add_mapping_row()
                    row = self.mapping_table.rowCount() - 1
                    self.mapping_table.setItem(row, 0, QTableWidgetItem(source))
                    combo = self.mapping_table.cellWidget(row, 1)
                    combo.setCurrentText(target)
                
                self.log_text.append(f"Mapping caricato da: {file_path}")
                
            except Exception as e:
                QMessageBox.warning(self, "Errore", f"Errore caricamento mapping: {str(e)}")
    
    def save_mapping_to_file(self):
        """Salva mapping in file JSON"""
        mapping = self.get_custom_mapping()
        
        if mapping:
            file_path, _ = QFileDialog.getSaveFileName(self, "Salva mapping", "", "JSON Files (*.json)")
            
            if file_path:
                try:
                    import json
                    with open(file_path, 'w') as f:
                        json.dump(mapping, f, indent=2)
                    
                    self.log_text.append(f"Mapping salvato in: {file_path}")
                    
                except Exception as e:
                    QMessageBox.warning(self, "Errore", f"Errore salvataggio mapping: {str(e)}")
    
    def preview_import(self):
        """Mostra anteprima dei dati da importare"""
        if not self.files_to_import:
            QMessageBox.warning(self, "Attenzione", "Nessun file selezionato")
            return
        
        # TODO: Implementare dialog di anteprima
        self.log_text.append("Funzione anteprima non ancora implementata")
    
    def start_import(self):
        """Avvia l'importazione"""
        if not self.files_to_import:
            QMessageBox.warning(self, "Attenzione", "Nessun file selezionato")
            return
        
        reply = QMessageBox.question(self, "Conferma", 
                                     f"Importare {len(self.files_to_import)} file?",
                                     QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Applica mapping personalizzato
            self.custom_mapping = self.get_custom_mapping()
            
            # Disabilita controlli durante importazione
            self.btn_import.setEnabled(False)
            self.btn_preview.setEnabled(False)
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            
            # Avvia thread di importazione
            self.import_thread = ImportWorker(
                self.import_manager, 
                self.files_to_import,
                use_festos_parser=self.check_festos_parser.isChecked()
            )
            self.import_thread.progress.connect(self.update_progress)
            self.import_thread.log_message.connect(self.log_message)
            self.import_thread.finished.connect(self.import_finished)
            self.import_thread.start()
    
    def update_progress(self, value):
        """Aggiorna la progress bar"""
        self.progress_bar.setValue(value)
    
    def log_message(self, message):
        """Aggiunge messaggio al log"""
        self.log_text.append(message)
    
    def import_finished(self, results):
        """Gestisce il completamento dell'importazione"""
        # Riabilita controlli
        self.btn_import.setEnabled(True)
        self.btn_preview.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        # Mostra riepilogo
        total_imported = sum(r['imported'] for r in results.values())
        total_errors = sum(len(r['errors']) for r in results.values())
        total_warnings = sum(len(r['warnings']) for r in results.values())
        
        self.log_text.append("\n" + "=" * 50)
        self.log_text.append("RIEPILOGO IMPORTAZIONE")
        self.log_text.append("=" * 50)
        self.log_text.append(f"Record importati: {total_imported}")
        self.log_text.append(f"Errori totali: {total_errors}")
        self.log_text.append(f"Avvisi totali: {total_warnings}")
        
        QMessageBox.information(self, "Importazione completata",
                                f"Importati {total_imported} record\n"
                                f"Errori: {total_errors}\n"
                                f"Avvisi: {total_warnings}")
