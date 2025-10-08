import os
import re
import requests
import threading
from typing import Optional, Dict, Any
from qgis.PyQt.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout,
                                 QRadioButton, QGroupBox,
                                 QTextEdit, QLineEdit, QComboBox,
                                 QSizePolicy, QSpacerItem, QMessageBox, 
                                 QProgressDialog, QLabel, QDialog, QPushButton,
                                 QInputDialog, QApplication)
from qgis.PyQt.QtGui import QFont
from qgis.PyQt.QtCore import Qt, pyqtSignal, QObject

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
        self.openai_radio = QRadioButton("OpenAI GPT-4 (API già configurata)")
        self.openai_radio.setChecked(True)
        self.ollama_radio = QRadioButton("Ollama (modello locale)")
        self.free_radio = QRadioButton("API gratuita (se disponibile)")

        mode_layout.addWidget(self.openai_radio)
        mode_layout.addWidget(self.ollama_radio)
        mode_layout.addWidget(self.free_radio)

        # Box per Ollama
        ollama_layout = QHBoxLayout()
        ollama_layout.addItem(QSpacerItem(20, 10, QSizePolicy.Fixed, QSizePolicy.Minimum))
        ollama_layout.addWidget(QLabel("Modello Ollama:"))
        self.ollama_model_combo = QComboBox()
        self.ollama_model_combo.setEditable(True)
        self.ollama_model_combo.addItems(["llama3.2", "mistral", "codellama", "phi3", "qwen2.5-coder"])
        self.ollama_model_combo.setEnabled(False)
        ollama_layout.addWidget(self.ollama_model_combo)
        
        self.ollama_status_label = QLabel("Stato: Non verificato")
        ollama_layout.addWidget(self.ollama_status_label)
        
        self.check_ollama_btn = QPushButton("Verifica Ollama")
        self.check_ollama_btn.clicked.connect(self.check_ollama_status)
        self.check_ollama_btn.setEnabled(False)
        ollama_layout.addWidget(self.check_ollama_btn)
        
        mode_layout.addLayout(ollama_layout)
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
            "Es: 'Trova tutti i reperti ceramici dal sito con ID 1 che hanno datazione tra 100 e 200 d.C.' \n"
            "oppure 'Mostra le US che si trovano entro 50 metri dalla struttura STR001'")
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
        explanation_group = QGroupBox("Spiegazione della Query")
        explanation_layout = QVBoxLayout()

        self.explanation_text = QTextEdit()
        self.explanation_text.setReadOnly(True)
        self.explanation_text.setPlaceholderText("La spiegazione della query apparirà qui")
        explanation_layout.addWidget(self.explanation_text)

        explanation_group.setLayout(explanation_layout)
        main_layout.addWidget(explanation_group)

        # Connetti segnali
        self.openai_radio.toggled.connect(self.on_mode_toggled)
        self.ollama_radio.toggled.connect(self.on_mode_toggled)
        self.free_radio.toggled.connect(self.on_mode_toggled)

    def on_mode_toggled(self):
        """Gestisce il cambio di modalità"""
        ollama_mode = self.ollama_radio.isChecked()
        self.ollama_model_combo.setEnabled(ollama_mode)
        self.check_ollama_btn.setEnabled(ollama_mode)
        
    def check_ollama_status(self):
        """Verifica lo stato di Ollama"""
        from .textTosql import MakeSQL
        
        if MakeSQL.check_ollama_status():
            self.ollama_status_label.setText("Stato: Connesso")
            self.ollama_status_label.setStyleSheet("color: green;")
            # Aggiorna la lista dei modelli disponibili
            models = MakeSQL.get_ollama_models()
            if models:
                self.ollama_model_combo.clear()
                self.ollama_model_combo.addItems(models)
        else:
            self.ollama_status_label.setText("Stato: Non disponibile")
            self.ollama_status_label.setStyleSheet("color: red;")
            QMessageBox.warning(self, "Ollama non disponibile", 
                              "Ollama non è in esecuzione o non è installato.\n"
                              "Installa Ollama da https://ollama.ai e assicurati che sia in esecuzione.")

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
        if self.openai_radio.isChecked():
            # Modalità OpenAI
            sql_query, explanation = MakeSQL.make_openai_request(prompt, db_type, self.parent)
            
        elif self.ollama_radio.isChecked():
            # Modalità Ollama
            model = self.ollama_model_combo.currentText()
            sql_query, explanation = MakeSQL.make_ollama_request(prompt, db_type, model, self)
            
        elif self.free_radio.isChecked():
            # Modalità API gratuita (da implementare)
            QMessageBox.information(self, "Non disponibile", 
                                  "Le API gratuite non sono ancora implementate.\n"
                                  "Usa OpenAI o Ollama per ora.")
            return

        # Mostra il risultato
        if sql_query:
            self.output_text.setPlainText(sql_query)
            if explanation:
                self.explanation_text.setPlainText(explanation)
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
        if self.openai_radio.isChecked():
            # Modalità OpenAI
            explanation = MakeSQL.explain_openai_request(sql_query, self.parent)
            
        elif self.ollama_radio.isChecked():
            # Modalità Ollama
            model = self.ollama_model_combo.currentText()
            explanation = MakeSQL.explain_ollama_request(sql_query, model, self)

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
            clipboard = QApplication.clipboard()
            clipboard.setText(sql_query)
            QMessageBox.information(self, "Copiato", "La query SQL è stata copiata negli appunti.")

    def on_use_clicked(self):
        """Usa la query generata"""
        sql_query = self.output_text.toPlainText().strip()
        if not sql_query:
            return

        # Se sei nella classe US_USM, puoi fare qualcosa come:
        if hasattr(self.parent, 'lineEdit_sql'):
            self.parent.lineEdit_sql.setText(sql_query)
            QMessageBox.information(self, "Query Utilizzata",
                                    "La query SQL è stata inserita nel campo SQL.")
        else:
            # Altrimenti, semplicemente notifica l'utente
            QMessageBox.information(self, "Query Pronta",
                                    "La query SQL è pronta per l'uso. Puoi copiarla e utilizzarla dove necessario.")


class MakeSQL:
    """Classe per generare SQL da linguaggio naturale usando diversi LLM"""
    
    @staticmethod
    def schema_to_text(metadata):
        """Converte lo schema del database in formato testuale"""
        schema_text = "Database Schema:\n\n"
        for table in metadata.tables.values():
            # Nome della tabella con descrizione
            table_description = f"Table: {table.name}\n"
            table_description += "Columns:\n"
            
            # Aggiungi ogni colonna con tipo e descrizione
            for col in table.columns:
                col_type = str(col.type)
                nullable = "NULL" if col.nullable else "NOT NULL"
                primary = " PRIMARY KEY" if col.primary_key else ""
                foreign = ""
                if col.foreign_keys:
                    fk = list(col.foreign_keys)[0]
                    foreign = f" REFERENCES {fk.column.table.name}({fk.column.name})"
                
                table_description += f"  - {col.name}: {col_type} {nullable}{primary}{foreign}\n"
            
            table_description += "\n"
            schema_text += table_description
            
        # Aggiungi informazioni specifiche per query geometriche
        schema_text += "\nNote per query geometriche:\n"
        schema_text += "- Le tabelle con colonne 'the_geom' supportano query spaziali PostGIS/Spatialite\n"
        schema_text += "- Usa ST_DWithin per query di prossimità\n"
        schema_text += "- Usa ST_Contains, ST_Intersects per relazioni spaziali\n"
        schema_text += "- Le coordinate sono in EPSG:4326 (WGS84)\n"
        
        return schema_text

    @staticmethod
    def get_api_key(parent):
        """Ottiene l'API key di OpenAI dal file di configurazione"""
        api_key = ""
        
        # Usa il percorso corretto: home_utente/pyarchinit/bin
        HOME = os.path.expanduser("~")
        PYARCHINIT_HOME = os.path.join(HOME, "pyarchinit")
        BIN = os.path.join(PYARCHINIT_HOME, "bin")
        path_key = os.path.join(BIN, 'gpt_api_key.txt')
        
        # Verifica se il file esiste
        if os.path.exists(path_key):
            try:
                with open(path_key, 'r') as f:
                    api_key = f.read().strip()
                    
                if api_key:
                    return api_key
            except Exception as e:
                print(f"Errore lettura API key: {e}")
        
        # Se non troviamo l'API key e c'è un parent con il metodo apikey_gpt, usalo
        if not api_key and parent and hasattr(parent, 'apikey_gpt'):
            try:
                api_key = parent.apikey_gpt()
                if api_key:
                    return api_key
            except:
                pass
                
        # Se ancora non abbiamo l'API key, chiediamola all'utente
        if not api_key:
            reply = QMessageBox.question(None, 'API Key OpenAI non trovata', 
                                       f'Il file {path_key} non esiste o è vuoto.\n'
                                       'Vuoi inserire ora la tua API key OpenAI?',
                                       QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                api_key, ok = QInputDialog.getText(None, 'OpenAI API Key', 
                                                  'Inserisci la tua API key OpenAI:')
                if ok and api_key:
                    try:
                        # Crea la directory se non esiste
                        os.makedirs(BIN, exist_ok=True)
                        # Salva l'API key
                        with open(path_key, 'w') as f:
                            f.write(api_key)
                        print(f"API key salvata in: {path_key}")
                    except Exception as e:
                        QMessageBox.critical(None, "Errore", 
                                           f"Impossibile salvare l'API key: {str(e)}")
                        
        return api_key

    @staticmethod
    def make_openai_request(prompt, db_type, parent=None):
        """Genera SQL usando OpenAI GPT-4"""
        try:
            from openai import OpenAI
        except ImportError:
            QMessageBox.critical(None, "Libreria mancante",
                               "La libreria 'openai' non è installata.\n"
                               "Installala con: pip install openai")
            return None, None
            
        api_key = MakeSQL.get_api_key(parent)
        if not api_key:
            return None, None
            
        try:
            client = OpenAI(api_key=api_key)
            
            # Prepara lo schema
            schema_text = MakeSQL.schema_to_text(database_schema.metadata)
            
            # Costruisci il prompt di sistema
            system_prompt = f"""Sei un esperto di SQL e database archeologici PyArchInit.
Database type: {db_type}

{schema_text}

Regole importanti:
1. Genera SOLO la query SQL, senza commenti o formattazione markdown
2. La query deve essere eseguibile direttamente
3. Per query geometriche usa le funzioni PostGIS/Spatialite appropriate
4. Considera sempre il contesto archeologico dei dati
5. Dopo la query, su una nuova riga preceduta da "---", fornisci una spiegazione dettagliata in italiano di cosa fa la query, con esempi di risultati attesi"""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
            
            # Progress dialog
            progress = QProgressDialog("Generazione SQL in corso...", "Annulla", 0, 0, parent)
            progress.setWindowTitle("Attendi")
            progress.setWindowModality(Qt.WindowModal)
            progress.show()
            
            try:
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=messages,
                    temperature=0.1,
                    max_tokens=1500
                )
                
                content = response.choices[0].message.content
                
                # Separa query e spiegazione
                if "---" in content:
                    parts = content.split("---", 1)
                    sql_query = parts[0].strip()
                    explanation = parts[1].strip() if len(parts) > 1 else ""
                else:
                    sql_query = content.strip()
                    explanation = ""
                
                # Pulisci la query
                sql_query = MakeSQL.clean_sql_query(sql_query)
                
                return sql_query, explanation
                
            finally:
                progress.close()
                
        except Exception as e:
            error_msg = str(e)
            if "api_key" in error_msg.lower() or "unauthorized" in error_msg.lower():
                QMessageBox.critical(parent, "Errore API Key", 
                                   f"Errore di autenticazione OpenAI.\n\n"
                                   f"Verifica che l'API key sia valida nel file:\n"
                                   f"~/pyarchinit/bin/gpt_api_key.txt\n\n"
                                   f"Errore: {error_msg}")
            else:
                QMessageBox.critical(parent, "Errore", f"Errore OpenAI: {error_msg}")
            return None, None

    @staticmethod
    def explain_openai_request(sql_query, parent=None):
        """Spiega una query SQL usando OpenAI"""
        try:
            from openai import OpenAI
        except ImportError:
            return None
            
        api_key = MakeSQL.get_api_key(parent)
        if not api_key:
            return None
            
        try:
            client = OpenAI(api_key=api_key)
            
            system_prompt = """Sei un esperto di SQL e database archeologici.
Spiega la query SQL fornita in modo chiaro e dettagliato in italiano.
Includi:
1. Cosa fa ogni parte della query
2. Quali tabelle vengono interrogate
3. Quali filtri vengono applicati
4. Che tipo di risultati ci si può aspettare
5. Esempi concreti nel contesto archeologico"""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Spiega questa query SQL:\n{sql_query}"}
            ]
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.3,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Errore nella spiegazione: {str(e)}"

    @staticmethod
    def check_ollama_status():
        """Verifica se Ollama è disponibile"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False

    @staticmethod
    def get_ollama_models():
        """Ottiene la lista dei modelli Ollama disponibili"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
        except:
            pass
        return []

    @staticmethod
    def make_ollama_request(prompt, db_type, model="llama3.2", parent=None):
        """Genera SQL usando Ollama"""
        if not MakeSQL.check_ollama_status():
            QMessageBox.critical(parent, "Ollama non disponibile",
                               "Ollama non è in esecuzione. Avvialo con 'ollama serve'")
            return None, None
            
        try:
            # Prepara lo schema
            schema_text = MakeSQL.schema_to_text(database_schema.metadata)
            
            # Costruisci il prompt
            full_prompt = f"""You are an SQL expert for archaeological databases.
Database type: {db_type}

{schema_text}

Task: Convert this natural language query to SQL: {prompt}

Rules:
1. Generate ONLY the SQL query, no comments or markdown
2. The query must be directly executable
3. For geometric queries use PostGIS/Spatialite functions
4. Consider the archaeological context
5. After the query, on a new line preceded by "---", provide a detailed explanation in Italian

SQL Query:"""

            # Progress dialog
            progress = QProgressDialog("Generazione SQL con Ollama...", "Annulla", 0, 0, parent)
            progress.setWindowTitle("Attendi")
            progress.setWindowModality(Qt.WindowModal)
            progress.show()
            
            try:
                response = requests.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": model,
                        "prompt": full_prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.1,
                            "num_predict": 1500
                        }
                    },
                    timeout=60
                )
                
                if response.status_code == 200:
                    content = response.json().get('response', '')
                    
                    # Separa query e spiegazione
                    if "---" in content:
                        parts = content.split("---", 1)
                        sql_query = parts[0].strip()
                        explanation = parts[1].strip() if len(parts) > 1 else ""
                    else:
                        sql_query = content.strip()
                        explanation = ""
                    
                    # Pulisci la query
                    sql_query = MakeSQL.clean_sql_query(sql_query)
                    
                    return sql_query, explanation
                else:
                    QMessageBox.critical(parent, "Errore Ollama", 
                                       f"Errore nella risposta: {response.status_code}")
                    return None, None
                    
            finally:
                progress.close()
                
        except Exception as e:
            QMessageBox.critical(parent, "Errore", f"Errore Ollama: {str(e)}")
            return None, None

    @staticmethod
    def explain_ollama_request(sql_query, model="llama3.2", parent=None):
        """Spiega una query SQL usando Ollama"""
        if not MakeSQL.check_ollama_status():
            return None
            
        try:
            prompt = f"""Explain this SQL query in Italian, providing:
1. What each part of the query does
2. Which tables are queried
3. What filters are applied
4. What results to expect
5. Concrete examples in archaeological context

SQL Query:
{sql_query}

Explanation in Italian:"""

            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 1000
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json().get('response', '')
            
        except Exception as e:
            return f"Errore nella spiegazione: {str(e)}"
            
        return None

    @staticmethod
    def clean_sql_query(sql_query):
        """Pulisce la query SQL rimuovendo elementi non necessari"""
        # Rimuovi blocchi di codice markdown
        sql_query = re.sub(r'```sql\s*', '', sql_query)
        sql_query = re.sub(r'```\s*', '', sql_query)
        
        # Rimuovi commenti SQL
        sql_query = re.sub(r'--.*$', '', sql_query, flags=re.MULTILINE)
        sql_query = re.sub(r'/\*.*?\*/', '', sql_query, flags=re.DOTALL)
        
        # Rimuovi spiegazioni testuali all'inizio
        lines = sql_query.strip().split('\n')
        clean_lines = []
        sql_started = False
        
        for line in lines:
            stripped = line.strip().upper()
            # Controlla se la linea inizia con una keyword SQL
            if any(stripped.startswith(kw) for kw in ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'WITH', 'CREATE']):
                sql_started = True
                
            if sql_started or (stripped and not any(word in stripped for word in ['HERE', 'THIS', 'QUERY', 'SQL'])):
                clean_lines.append(line)
        
        return '\n'.join(clean_lines).strip()

    @staticmethod
    def make_api_request(prompt, db, apikey):
        """Metodo legacy per compatibilità - ora usa OpenAI GPT-4 invece di text2sql.ai"""
        # Ignora l'apikey passata e usa quella di OpenAI da ~/pyarchinit/bin/gpt_api_key.txt
        # Questo metodo è mantenuto solo per compatibilità con il codice esistente
        
        print("Info: Text2SQL ora usa OpenAI GPT-4 con l'API key da ~/pyarchinit/bin/gpt_api_key.txt")
        
        # Usa il nuovo metodo OpenAI
        sql_query, explanation = MakeSQL.make_openai_request(prompt, db, None)
        
        # Restituisci solo la query SQL per compatibilità
        return sql_query

    @staticmethod
    def explain_request(prompt, apikey):
        """Metodo legacy per compatibilità - ora usa OpenAI GPT-4 invece di text2sql.ai"""
        # Ignora l'apikey passata e usa quella di OpenAI
        # Questo metodo è mantenuto solo per compatibilità con il codice esistente
        
        # Ottieni il parent dal contesto se possibile
        parent = None
        
        # Usa il nuovo metodo OpenAI
        return MakeSQL.explain_openai_request(prompt, parent)


# Backward compatibility - mantieni le vecchie funzioni globali per non rompere il codice esistente
def make_api_request(prompt, db, apikey):
    """Funzione legacy per compatibilità"""
    return MakeSQL.make_api_request(prompt, db, apikey)

def explain_request(prompt, apikey):
    """Funzione legacy per compatibilità"""
    return MakeSQL.explain_request(prompt, apikey)