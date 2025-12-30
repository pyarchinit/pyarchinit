#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
/***************************************************************************
        pyArchInit Plugin - Download Dialog for AI Models
        
        A QGIS plugin to manage archaeological dataset stored in Postgres
        -------------------
    begin                : 2024-12-01
    copyright            : (C) 2024 by Luca Mandolesi; Enzo Cocca <enzo.ccc@gmail.com>
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
import sys
from qgis.PyQt.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QProgressBar, QDialogButtonBox
from qgis.PyQt.QtCore import QThread, pyqtSignal, QTimer
from qgis.PyQt.QtGui import QFont
import requests
import time


class DownloadThread(QThread):
    """Thread for downloading files with progress updates"""
    progress_update = pyqtSignal(int)
    speed_update = pyqtSignal(str)
    status_update = pyqtSignal(str)
    finished_download = pyqtSignal(bool, str)
    
    def __init__(self, url, save_path):
        super().__init__()
        self.url = url
        self.save_path = save_path
        self.is_cancelled = False
        
    def run(self):
        """Download the file with progress tracking"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
            
            self.status_update.emit("Connessione al server...")
            
            # Start download with streaming
            response = requests.get(self.url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Get total file size
            total_size = int(response.headers.get('content-length', 0))
            if total_size == 0:
                self.status_update.emit("Dimensione file sconosciuta, download in corso...")
            
            # Download in chunks
            downloaded_size = 0
            chunk_size = 8192  # 8KB chunks
            start_time = time.time()
            
            with open(self.save_path + '.tmp', 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if self.is_cancelled:
                        self.status_update.emit("Download cancellato")
                        return
                    
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # Update progress
                        if total_size > 0:
                            progress = int((downloaded_size / total_size) * 100)
                            self.progress_update.emit(progress)
                            
                            # Calculate download speed
                            elapsed_time = time.time() - start_time
                            if elapsed_time > 0:
                                speed = downloaded_size / elapsed_time
                                speed_mb = speed / (1024 * 1024)
                                remaining_bytes = total_size - downloaded_size
                                eta_seconds = remaining_bytes / speed if speed > 0 else 0
                                eta_minutes = int(eta_seconds / 60)
                                eta_seconds = int(eta_seconds % 60)
                                
                                speed_text = f"Velocità: {speed_mb:.1f} MB/s - Tempo rimanente: {eta_minutes}:{eta_seconds:02d}"
                                self.speed_update.emit(speed_text)
            
            # Rename temp file to final name
            if os.path.exists(self.save_path + '.tmp'):
                os.rename(self.save_path + '.tmp', self.save_path)
                
            self.finished_download.emit(True, "Download completato con successo!")
            
        except requests.exceptions.Timeout:
            self.finished_download.emit(False, "Timeout: il server non risponde")
        except requests.exceptions.ConnectionError:
            self.finished_download.emit(False, "Errore di connessione al server")
        except Exception as e:
            self.finished_download.emit(False, f"Errore durante il download: {str(e)}")
    
    def cancel(self):
        """Cancel the download"""
        self.is_cancelled = True


class DownloadModelDialog(QDialog):
    """Dialog for downloading AI models with progress tracking"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.save_path = ""
        self.save_dir = ""
        self.download_thread = None
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the dialog UI"""
        self.setWindowTitle("Download Modello AI")
        self.setModal(True)
        self.resize(500, 250)
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Info label
        self.info_label = QLabel("Preparazione download...")
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)
        
        # Speed label
        self.speed_label = QLabel("")
        font = QFont()
        font.setPointSize(9)
        self.speed_label.setFont(font)
        layout.addWidget(self.speed_label)
        
        # Buttons
        self.button_box = QDialogButtonBox()
        self.download_button = QPushButton("Scarica")
        self.cancel_button = QPushButton("Annulla")
        self.button_box.addButton(self.download_button, QDialogButtonBox.AcceptRole)
        self.button_box.addButton(self.cancel_button, QDialogButtonBox.RejectRole)
        
        self.download_button.clicked.connect(self.start_download)
        self.cancel_button.clicked.connect(self.cancel_download)
        
        layout.addWidget(self.button_box)
        
    def start_download(self):
        """Start the download process"""
        # Phi-3 model URL (you should replace this with actual model URL)
        model_url = "https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf"
        
        # Disable download button
        self.download_button.setEnabled(False)
        self.status_label.setText("Avvio download...")
        
        # Create and start download thread
        self.download_thread = DownloadThread(model_url, self.save_path)
        self.download_thread.progress_update.connect(self.update_progress)
        self.download_thread.speed_update.connect(self.update_speed)
        self.download_thread.status_update.connect(self.update_status)
        self.download_thread.finished_download.connect(self.download_finished)
        self.download_thread.start()
        
    def update_progress(self, value):
        """Update progress bar"""
        self.progress_bar.setValue(value)
        
    def update_speed(self, text):
        """Update speed label"""
        self.speed_label.setText(text)
        
    def update_status(self, text):
        """Update status label"""
        self.status_label.setText(text)
        
    def download_finished(self, success, message):
        """Handle download completion"""
        if success:
            self.status_label.setText(message)
            # Auto close after 2 seconds
            QTimer.singleShot(2000, self.accept)
        else:
            self.status_label.setText(message)
            self.download_button.setEnabled(True)
            
    def cancel_download(self):
        """Cancel the download"""
        if self.download_thread and self.download_thread.isRunning():
            self.download_thread.cancel()
            self.download_thread.wait()
            
            # Remove partial file
            temp_file = self.save_path + '.tmp'
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
                    
        self.reject()