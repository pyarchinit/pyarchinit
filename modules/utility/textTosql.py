# import requests
# from qgis.PyQt.QtWidgets import QMessageBox
#
# from . import database_schema
#
#
# class MakeSQL:
#     def __init__(self):
#         pass
#     # Funzione per convertire lo schema in formato testuale (esempio semplificato)
#     @staticmethod
#     def schema_to_text(metadata):
#         schema_text = ""
#         for table in metadata.tables.values():
#             # Inizia con il nome della tabella
#             table_description = f"{table.name} ("
#             # Aggiungi ogni colonna e il suo tipo
#             columns_descriptions = [f"{col.name}" for col in table.columns]
#             table_description += ", ".join(columns_descriptions)
#             table_description += ");"
#             # Aggiungi la descrizione della tabella al testo dello schema
#             schema_text += table_description + "\n"
#         return schema_text
#
#     # Utilizzo della funzione per includere lo schema nella richiesta API
#     @staticmethod
#     def make_api_request(prompt,db,apikey):
#         # Preparazione dello schema
#         #schema = Base.metadata  # Assuming Campioni_table is part of Base
#         schema_text = MakeSQL.schema_to_text(database_schema.metadata)  # Converti lo schema in testo
#         #QMessageBox.information(None, "Schema", schema_text)
#         api_key = apikey  # Sostituisci con la tua chiave API
#         url = "https://app2.text2sql.ai/api/external/generate-sql"
#         headers = {
#             "Authorization": f"Bearer {api_key}",
#             "Content-Type": "application/json"
#         }
#         data = {
#             "prompt": prompt,
#             "type": db,
#             "schema": schema_text  # Utilizzo dello schema convertito
#         }
#
#         try:
#             response = requests.post(url, headers=headers, json=data)
#             response.raise_for_status()
#             return response.json().get('output')
#         except requests.exceptions.HTTPError as he:
#             QMessageBox.critical(None, "Error", str(he))
#             return None
#
#
#         except Exception as e:
#             print(f"An error occurred: {e}")
#             QMessageBox.critical(None, "Error", str(e))
#             return None
#
#         return None
#
#     @staticmethod
#     def explain_request(prompt, apikey):
#         # Preparazione dello schema
#         # schema = Base.metadata  # Assuming Campioni_table is part of Base
#         #schema_text = MakeSQL.schema_to_text(database_schema.metadata)  # Converti lo schema in testo
#         # QMessageBox.information(None, "Schema", schema_text)
#         api_key = apikey  # Sostituisci con la tua chiave API
#         url = "https://app2.text2sql.ai/api/external/explain-sql"
#         headers = {
#             "Authorization": f"Bearer {api_key}",
#             "Content-Type": "application/json"
#         }
#         data = {
#             "prompt": prompt
#         }
#
#         try:
#             response = requests.post(url, headers=headers, json=data)
#             response.raise_for_status()
#             return response.json().get('output')
#         except requests.exceptions.HTTPError as he:
#             QMessageBox.critical(None, "Error", str(he))
#             return None
#
#
#         except Exception as e:
#             print(f"An error occurred: {e}")
#             QMessageBox.critical(None, "Error", str(e))
#             return None
#
#         return None
import re
from qgis.PyQt.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                 QPushButton, QRadioButton, QGroupBox,
                                 QTextEdit, QLineEdit, QComboBox, QMessageBox,
                                 QSizePolicy, QSpacerItem)
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QFont
import os
import requests
import shutil
import threading
from qgis.PyQt.QtWidgets import QMessageBox, QProgressDialog, QLabel, QVBoxLayout, QDialog, QPushButton
from qgis.PyQt.QtCore import Qt, QThread, pyqtSignal, QObject

from llama_cpp import Llama
from . import database_schema


class Text2SQLWidget(QWidget):
    """Widget per l'interfaccia Text2SQL con modalità dual (API e locale)"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()

    def setup_ui(self):
        """Configura l'interfaccia utente"""
        # Layout principale
        main_layout = QVBoxLayout(self)

        # Titolo
        title_label = QLabel("Generazione SQL con AI")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(14)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # Modalità di generazione
        mode_group = QGroupBox("Modalità di Generazione")
        mode_layout = QVBoxLayout()

        # RadioButton per scelta modalità
        self.api_radio = QRadioButton("Utilizza API (richiede chiave API)")
        self.api_radio.setChecked(True)
        self.local_radio = QRadioButton("Utilizza modello locale (senza costi)")

        mode_layout.addWidget(self.api_radio)

        # Box per API key
        api_key_layout = QHBoxLayout()
        api_key_layout.addItem(QSpacerItem(20, 10, QSizePolicy.Fixed, QSizePolicy.Minimum))
        api_key_layout.addWidget(QLabel("API Key:"))
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Inserisci la tua chiave API")
        api_key_layout.addWidget(self.api_key_input)
        mode_layout.addLayout(api_key_layout)

        mode_layout.addWidget(self.local_radio)

        # Box per modello locale
        local_model_layout = QHBoxLayout()
        local_model_layout.addItem(QSpacerItem(20, 10, QSizePolicy.Fixed, QSizePolicy.Minimum))

        self.model_status_label = QLabel("Stato modello: Non trovato")
        local_model_layout.addWidget(self.model_status_label)

        self.download_model_btn = QPushButton("Scarica Modello")
        self.download_model_btn.clicked.connect(self.on_download_model_clicked)
        local_model_layout.addWidget(self.download_model_btn)

        mode_layout.addLayout(local_model_layout)
        mode_group.setLayout(mode_layout)
        main_layout.addWidget(mode_group)

        # Controlli per la generazione SQL
        input_group = QGroupBox("Input")
        input_layout = QVBoxLayout()

        # Tipo di database
        db_layout = QHBoxLayout()
        db_layout.addWidget(QLabel("Tipo di Database:"))
        self.db_type_combo = QComboBox()
        self.db_type_combo.addItems(["sqlite", "postgresql", "mysql", "sqlserver"])
        db_layout.addWidget(self.db_type_combo)
        input_layout.addLayout(db_layout)

        # Prompt
        input_layout.addWidget(QLabel("Descrivi la query che vuoi generare:"))
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText(
            "Es: 'Trova tutti i record nella tabella X dove il campo Y è maggiore di 10 e ordina per Z'")
        self.prompt_input.setMinimumHeight(100)
        input_layout.addWidget(self.prompt_input)

        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)

        # Pulsanti
        buttons_layout = QHBoxLayout()

        self.generate_btn = QPushButton("Genera SQL")
        self.generate_btn.clicked.connect(self.on_generate_clicked)
        buttons_layout.addWidget(self.generate_btn)

        self.clear_btn = QPushButton("Pulisci")
        self.clear_btn.clicked.connect(self.on_clear_clicked)
        buttons_layout.addWidget(self.clear_btn)

        main_layout.addLayout(buttons_layout)

        # Output
        output_group = QGroupBox("Query SQL Generata")
        output_layout = QVBoxLayout()

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setPlaceholderText("La query SQL generata apparirà qui")
        output_layout.addWidget(self.output_text)

        # Pulsanti per l'output
        output_buttons = QHBoxLayout()

        self.explain_btn = QPushButton("Spiega Query")
        self.explain_btn.clicked.connect(self.on_explain_clicked)
        self.explain_btn.setEnabled(False)
        output_buttons.addWidget(self.explain_btn)

        self.copy_btn = QPushButton("Copia Query")
        self.copy_btn.clicked.connect(self.on_copy_clicked)
        self.copy_btn.setEnabled(False)
        output_buttons.addWidget(self.copy_btn)

        self.use_btn = QPushButton("Usa Query")
        self.use_btn.clicked.connect(self.on_use_clicked)
        self.use_btn.setEnabled(False)
        output_buttons.addWidget(self.use_btn)

        output_layout.addLayout(output_buttons)
        output_group.setLayout(output_layout)
        main_layout.addWidget(output_group)

        # Spiegazione
        explanation_group = QGroupBox("Spiegazione")
        explanation_layout = QVBoxLayout()

        self.explanation_text = QTextEdit()
        self.explanation_text.setReadOnly(True)
        self.explanation_text.setPlaceholderText("La spiegazione della query apparirà qui")
        explanation_layout.addWidget(self.explanation_text)

        explanation_group.setLayout(explanation_layout)
        main_layout.addWidget(explanation_group)

        # Connetti segnali
        self.api_radio.toggled.connect(self.on_mode_toggled)
        self.local_radio.toggled.connect(self.on_mode_toggled)

        # Controlla lo stato del modello
        self.check_model_status()

    def check_model_status(self):
        """Controlla se il modello locale è disponibile"""
        from .textTosql import MakeSQL

        if MakeSQL.check_local_model():
            self.model_status_label.setText("Stato modello: Installato")
            self.model_status_label.setStyleSheet("color: green;")
            self.download_model_btn.setText("Modello già scaricato")
            self.download_model_btn.setEnabled(False)
        else:
            self.model_status_label.setText("Stato modello: Non trovato")
            self.model_status_label.setStyleSheet("color: red;")
            self.download_model_btn.setText("Scarica Modello")
            self.download_model_btn.setEnabled(True)

    def on_mode_toggled(self):
        """Gestisce il cambio di modalità"""
        api_mode = self.api_radio.isChecked()
        self.api_key_input.setEnabled(api_mode)
        self.download_model_btn.setEnabled(not api_mode and not MakeSQL.check_local_model())

    def on_download_model_clicked(self):
        """Gestisce il click sul pulsante di download del modello"""
        from .textTosql import MakeSQL

        if MakeSQL.download_model_dialog(self):
            self.check_model_status()

    def on_generate_clicked(self):
        """Gestisce il click sul pulsante di generazione"""
        from .textTosql import MakeSQL

        prompt = self.prompt_input.toPlainText().strip()
        if not prompt:
            QMessageBox.warning(self, "Input mancante", "Inserisci una descrizione della query che vuoi generare.")
            return

        # Ottieni il tipo di database
        db_type = self.db_type_combo.currentText()

        # Genera SQL in base alla modalità selezionata
        if self.api_radio.isChecked():
            # Modalità API
            api_key = self.api_key_input.text().strip()
            if not api_key:
                QMessageBox.warning(self, "API Key mancante",
                                    "Inserisci la tua chiave API per utilizzare la modalità API.")
                return

            sql_query = MakeSQL.make_api_request(prompt, db_type, api_key)
        else:
            # Modalità locale
            if not MakeSQL.check_local_model():
                result = QMessageBox.question(
                    self,
                    "Modello non trovato",
                    "Il modello locale non è stato trovato. Vuoi scaricarlo ora?",
                    QMessageBox.Yes | QMessageBox.No
                )

                if result == QMessageBox.Yes:
                    if MakeSQL.download_model_dialog(self):
                        self.check_model_status()
                    else:
                        return
                else:
                    return

            sql_query = MakeSQL.make_local_request(prompt, db_type, self)

        # Mostra il risultato
        if sql_query:
            self.output_text.setPlainText(sql_query)
            self.explanation_text.clear()
            self.explain_btn.setEnabled(True)
            self.copy_btn.setEnabled(True)
            self.use_btn.setEnabled(True)
        else:
            self.output_text.setPlainText("Errore nella generazione della query SQL.")
            self.explain_btn.setEnabled(False)
            self.copy_btn.setEnabled(False)
            self.use_btn.setEnabled(False)

    def on_explain_clicked(self):
        """Gestisce il click sul pulsante di spiegazione"""
        from .textTosql import MakeSQL

        sql_query = self.output_text.toPlainText().strip()
        if not sql_query:
            return

        # Spiega SQL in base alla modalità selezionata
        if self.api_radio.isChecked():
            # Modalità API
            api_key = self.api_key_input.text().strip()
            if not api_key:
                QMessageBox.warning(self, "API Key mancante",
                                    "Inserisci la tua chiave API per utilizzare la modalità API.")
                return

            explanation = MakeSQL.explain_request(sql_query, api_key)
        else:
            # Modalità locale
            if not MakeSQL.check_local_model():
                QMessageBox.warning(self, "Modello non trovato", "Modello locale non trovato.")
                return

            explanation = MakeSQL.explain_local_request(sql_query, self)

        # Mostra il risultato
        if explanation:
            self.explanation_text.setPlainText(explanation)
        else:
            self.explanation_text.setPlainText("Errore nella generazione della spiegazione.")

    def on_clear_clicked(self):
        """Pulisce l'interfaccia"""
        self.prompt_input.clear()
        self.output_text.clear()
        self.explanation_text.clear()
        self.explain_btn.setEnabled(False)
        self.copy_btn.setEnabled(False)
        self.use_btn.setEnabled(False)

    def on_copy_clicked(self):
        """Copia la query negli appunti"""
        sql_query = self.output_text.toPlainText().strip()
        if sql_query:
            from qgis.PyQt.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            clipboard.setText(sql_query)
            QMessageBox.information(self, "Copiato", "La query SQL è stata copiata negli appunti.")

    def on_use_clicked(self):
        """Usa la query generata"""
        sql_query = self.output_text.toPlainText().strip()
        if not sql_query:
            return

        # Esempio: questa funzione dovrebbe essere personalizzata in base all'uso specifico
        # Ad esempio, potresti voler inviare la query al db manager di QGIS
        # o inserirla in un campo di testo specifico della tua interfaccia

        # Se sei nella classe US_USM, puoi fare qualcosa come:
        if hasattr(self.parent, 'lineEdit_sql'):
            self.parent.lineEdit_sql.setText(sql_query)
            QMessageBox.information(self, "Query Utilizzata",
                                    "La query SQL è stata inserita nel campo SQL.")
        else:
            # Altrimenti, semplicemente notifica l'utente
            QMessageBox.information(self, "Query Pronta",
                                    "La query SQL è pronta per l'uso. Puoi copiarla e utilizzarla dove necessario.")

    def apikey_text2sql(self):
        """Restituisce la chiave API (per compatibilità con il codice esistente)"""
        return self.api_key_input.text().strip()




class DownloadModelWorker(QObject):
    """Worker per il download del modello in background"""
    progress_updated = pyqtSignal(int, str)
    download_complete = pyqtSignal(bool, str)

    def __init__(self):
        super().__init__()
        self.stop_requested = False

    def download_model(self, download_url, save_path):
        try:
            # Crea la directory se non esiste
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            # Invia una richiesta HEAD per ottenere la dimensione del file
            response = requests.head(download_url)
            total_size = int(response.headers.get('content-length', 0))

            # Scarica il file
            response = requests.get(download_url, stream=True)
            response.raise_for_status()

            # Apri il file di destinazione
            with open(save_path, 'wb') as f:
                downloaded = 0
                chunk_size = 1024 * 1024  # 1MB

                for chunk in response.iter_content(chunk_size=chunk_size):
                    if self.stop_requested:
                        f.close()
                        os.remove(save_path)
                        self.download_complete.emit(False, "Download annullato")
                        return

                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

                        # Emetti progresso
                        percent = int(100 * downloaded / total_size) if total_size > 0 else 0
                        self.progress_updated.emit(
                            percent,
                            f"Scaricato {downloaded / (1024 * 1024):.1f} MB / {total_size / (1024 * 1024):.1f} MB"
                        )

            self.download_complete.emit(True, save_path)

        except Exception as e:
            self.download_complete.emit(False, str(e))

    def stop(self):
        self.stop_requested = True


class DownloadModelDialog(QDialog):
    """Dialog per scaricare il modello"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Download Modello Text2SQL")
        self.setMinimumWidth(500)

        # URL del modello
        self.model_url = "https://huggingface.co/dmedhi/Phi-3-mini-text2SQL-4k-instruct-GGUF-f16/resolve/main/unsloth.F16.gguf"

        # Path dove salvare il modello
        self.home_dir = os.path.expanduser("~")
        self.save_dir = os.path.join(self.home_dir, "pyarchinit", "bin")
        self.save_path = os.path.join(self.save_dir, "phi3_text2sql.gguf")

        # Crea il layout
        layout = QVBoxLayout()

        # Informazioni sul download
        self.info_label = QLabel(f"Il modello verrà scaricato in:\n{self.save_path}\n\nDimensione: circa 2 GB. "
                                 "Questo potrebbe richiedere tempo in base alla tua connessione internet.")
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)

        # Stato del download
        self.status_label = QLabel("Pronto per iniziare il download")
        layout.addWidget(self.status_label)

        # Bottoni
        button_layout = QVBoxLayout()

        self.download_button = QPushButton("Avvia Download")
        self.download_button.clicked.connect(self.start_download)
        button_layout.addWidget(self.download_button)

        self.cancel_button = QPushButton("Annulla")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Progress dialog
        self.progress = QProgressDialog(self)
        self.progress.setWindowTitle("Download in Corso")
        self.progress.setLabelText("Inizializzazione download...")
        self.progress.setMinimum(0)
        self.progress.setMaximum(100)
        self.progress.setWindowModality(Qt.WindowModal)
        self.progress.setAutoClose(False)
        self.progress.canceled.connect(self.cancel_download)

        # Thread di download
        self.download_thread = None
        self.download_worker = None

    def start_download(self):
        """Avvia il download del modello"""
        # Disabilita il pulsante di download
        self.download_button.setEnabled(False)
        self.status_label.setText("Avvio download...")

        # Crea e avvia il worker
        self.download_worker = DownloadModelWorker()
        self.download_worker.progress_updated.connect(self.update_progress)
        self.download_worker.download_complete.connect(self.download_finished)

        # Crea e avvia il thread
        self.download_thread = threading.Thread(
            target=self.download_worker.download_model,
            args=(self.model_url, self.save_path)
        )
        self.download_thread.start()

        # Mostra la progress dialog
        self.progress.setValue(0)
        self.progress.setLabelText("Inizializzazione download...")
        self.progress.show()

    def update_progress(self, percent, status):
        """Aggiorna il progresso del download"""
        self.progress.setValue(percent)
        self.progress.setLabelText(status)
        self.status_label.setText(status)

    def download_finished(self, success, message):
        """Gestisce il completamento del download"""
        self.progress.close()

        if success:
            self.status_label.setText(f"Download completato! Modello salvato in:\n{message}")
            QMessageBox.information(self, "Download Completato",
                                    f"Il modello è stato scaricato con successo in:\n{message}")
            self.accept()
        else:
            self.status_label.setText(f"Errore durante il download: {message}")
            self.download_button.setEnabled(True)
            QMessageBox.critical(self, "Errore Download",
                                 f"Si è verificato un errore durante il download:\n{message}")

    def cancel_download(self):
        """Annulla il download in corso"""
        if self.download_worker:
            self.download_worker.stop()
            self.status_label.setText("Download annullato")
            self.download_button.setEnabled(True)


class MakeSQL:
    def __init__(self):
        pass

    # Funzione per convertire lo schema in formato testuale (esempio semplificato)
    @staticmethod
    def schema_to_text(metadata):
        schema_text = ""
        for table in metadata.tables.values():
            # Inizia con il nome della tabella
            table_description = f"{table.name} ("
            # Aggiungi ogni colonna e il suo tipo
            columns_descriptions = [f"{col.name}" for col in table.columns]
            table_description += ", ".join(columns_descriptions)
            table_description += ");"
            # Aggiungi la descrizione della tabella al testo dello schema
            schema_text += table_description + "\n"
        return schema_text

    # Utilizzo della funzione per includere lo schema nella richiesta API
    @staticmethod
    def make_api_request(prompt, db, apikey):
        # Preparazione dello schema
        schema_text = MakeSQL.schema_to_text(database_schema.metadata)  # Converti lo schema in testo

        api_key = apikey  # Sostituisci con la tua chiave API
        url = "https://app2.text2sql.ai/api/external/generate-sql"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "prompt": prompt,
            "type": db,
            "schema": schema_text  # Utilizzo dello schema convertito
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json().get('output')
        except requests.exceptions.HTTPError as he:
            QMessageBox.critical(None, "Error", str(he))
            return None
        except Exception as e:
            print(f"An error occurred: {e}")
            QMessageBox.critical(None, "Error", str(e))
            return None

        return None

    @staticmethod
    def explain_request(prompt, apikey):
        api_key = apikey  # Sostituisci con la tua chiave API
        url = "https://app2.text2sql.ai/api/external/explain-sql"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "prompt": prompt
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json().get('output')
        except requests.exceptions.HTTPError as he:
            QMessageBox.critical(None, "Error", str(he))
            return None
        except Exception as e:
            print(f"An error occurred: {e}")
            QMessageBox.critical(None, "Error", str(e))
            return None

        return None

    @staticmethod
    def check_local_model():
        """Verifica se il modello locale esiste"""
        model_path = os.path.join(os.path.expanduser("~"), "pyarchinit", "bin", "phi3_text2sql.gguf")
        return os.path.exists(model_path)

    @staticmethod
    def download_model_dialog(parent=None):
        """Mostra il dialog per scaricare il modello"""
        dialog = DownloadModelDialog(parent)
        return dialog.exec_()


    @staticmethod
    def make_local_request(prompt, db, parent=None):
        """
        Genera una query SQL usando il modello locale Phi-3

        Args:
            prompt: La domanda in linguaggio naturale
            db: Tipo di database (sqlite, postgresql, etc.)
            parent: Widget genitore per i dialoghi

        Returns:
            La query SQL generata o None in caso di errore
        """
        # Verifica che il modello esista localmente
        HOME = os.path.expanduser("~")
        #BIN = '{}{}{}'.format(HOME, os.sep, "bin")BIN = '{}{}{}'.format(HOME, os.sep, "bin")
        model_path = os.path.join(HOME, "pyarchinit", "bin", "phi3_text2sql.gguf")

        if not os.path.exists(model_path):
            QMessageBox.critical(parent, "Modello non trovato",
                                 f"Il modello non è stato trovato in {model_path}.\n"
                                 "Usa il pulsante 'Scarica Modello' prima di procedere.")
            return None

        try:
            # Importa llama_cpp solo quando necessario
            # try:
            #     from llama_cpp import Llama
            # except ImportError:
            #     QMessageBox.critical(parent, "Libreria mancante",
            #                          "La libreria 'llama_cpp' non è installata.\n"
            #                          "Installala con: pip install llama-cpp-python")
            #     return None

            # Carica il modello (questo può richiedere tempo)
            progress = QProgressDialog("Caricamento del modello in corso...", "Annulla", 0, 0, parent)
            progress.setWindowTitle("Attendi")
            progress.setWindowModality(Qt.WindowModal)
            progress.show()

            try:
                llm = Llama(
                    model_path=model_path,
                    n_ctx=4096,
                    n_gpu_layers=-1
                )
            finally:
                progress.close()

            # Preparazione dello schema
            schema_text = MakeSQL.schema_to_text(database_schema.metadata)

            # Costruisci il prompt per il modello
            system_prompt = f"""You are a SQL expert. You translate natural language questions into SQL queries.
    Database type: {db}
    Database schema:
    {schema_text}

    IMPORTANT: Generate ONLY the SQL query code. Do not include ANY comments, explanation, or markdown formatting. 
    Return ONLY the raw SQL query, nothing more."""

            user_prompt = prompt

            # Crea il messaggio di chat
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            # Progress dialog per generazione
            progress = QProgressDialog("Generazione SQL in corso...", "Annulla", 0, 0, parent)
            progress.setWindowTitle("Attendi")
            progress.setWindowModality(Qt.WindowModal)
            progress.show()

            try:
                # Genera la query SQL
                response = llm.create_chat_completion(
                    messages=messages,
                    temperature=0.1,
                    max_tokens=512
                )

                # Estrai la query SQL dalla risposta
                sql_query = response.get("choices", [{}])[0].get("message", {}).get("content", "")

                # Pulisci la query
                # Rimuovi blocchi di codice markdown
                sql_query = sql_query.replace("```sql", "").replace("```", "")

                # Rimuovi commenti
                sql_query = re.sub(r'--.*$', '', sql_query, flags=re.MULTILINE)  # Rimuovi commenti SQL di tipo --
                sql_query = re.sub(r'/\*.*?\*/', '', sql_query, flags=re.DOTALL)  # Rimuovi commenti SQL tipo /* */

                # Rimuovi spiegazioni testuali (spesso incluse prima o dopo la query)
                sql_lines = sql_query.strip().split('\n')
                clean_lines = []

                # Filtra solo le linee che sembrano essere SQL
                for line in sql_lines:
                    stripped = line.strip()
                    if stripped and not stripped.startswith('Here') and not stripped.startswith(
                            'This') and not stripped.startswith('Note'):
                        clean_lines.append(line)

                # Ricomponi la query
                sql_query = '\n'.join(clean_lines).strip()

                return sql_query
            finally:
                progress.close()

        except Exception as e:
            QMessageBox.critical(parent, "Errore", f"Si è verificato un errore: {str(e)}")
            return None

    @staticmethod
    def explain_local_request(prompt, parent=None):
        """
        Spiega una query SQL usando il modello locale Phi-3

        Args:
            prompt: La query SQL da spiegare
            parent: Widget genitore per i dialoghi

        Returns:
            Spiegazione della query o None in caso di errore
        """
        # Verifica che il modello esista localmente
        model_path = os.path.join(os.path.expanduser("~"), "pyarchinit", "bin", "phi3_text2sql.gguf")

        if not os.path.exists(model_path):
            QMessageBox.critical(parent, "Modello non trovato",
                                 f"Il modello non è stato trovato in {model_path}.\n"
                                 "Usa il pulsante 'Scarica Modello' prima di procedere.")
            return None

        try:
            # Importa llama_cpp solo quando necessario
            try:
                from llama_cpp import Llama
            except ImportError:
                QMessageBox.critical(parent, "Libreria mancante",
                                     "La libreria 'llama_cpp' non è installata.\n"
                                     "Installala con: pip install llama-cpp-python")
                return None

            # Carica il modello (questo può richiedere tempo)
            progress = QProgressDialog("Caricamento del modello in corso...", "Annulla", 0, 0, parent)
            progress.setWindowTitle("Attendi")
            progress.setWindowModality(Qt.WindowModal)
            progress.show()

            try:
                llm = Llama(
                    model_path=model_path,
                    n_ctx=4096,
                    n_gpu_layers=-1
                )
            finally:
                progress.close()

            system_prompt = """You are a SQL expert. Explain the provided SQL query in simple terms.
Break down what each part of the query does in clear, non-technical language."""

            user_prompt = f"Explain this SQL query: {prompt}"

            # Crea il messaggio di chat
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            # Progress dialog per generazione
            progress = QProgressDialog("Generazione spiegazione in corso...", "Annulla", 0, 0, parent)
            progress.setWindowTitle("Attendi")
            progress.setWindowModality(Qt.WindowModal)
            progress.show()

            try:
                # Genera la spiegazione
                response = llm.create_chat_completion(
                    messages=messages,
                    temperature=0.3,
                    max_tokens=1024
                )

                # Estrai la spiegazione dalla risposta
                explanation = response.get("choices", [{}])[0].get("message", {}).get("content", "")

                return explanation
            finally:
                progress.close()

        except Exception as e:
            QMessageBox.critical(parent, "Errore", f"Si è verificato un errore: {str(e)}")
            return None
