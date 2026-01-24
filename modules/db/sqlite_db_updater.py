#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SQLite Database Updater Module
Aggiorna automaticamente database SQLite vecchi quando vengono aperti
"""

import sqlite3
import os
from datetime import datetime

# Make QGIS imports optional
try:
    from qgis.core import QgsMessageLog, Qgis
    from qgis.PyQt.QtWidgets import QMessageBox, QProgressDialog
    from qgis.PyQt.QtCore import Qt
    QGIS_AVAILABLE = True
except ImportError:
    QGIS_AVAILABLE = False


class SQLiteDBUpdater:
    """Gestisce l'aggiornamento automatico dei database SQLite vecchi"""
    
    def __init__(self, db_path, parent=None):
        self.db_path = db_path
        self.parent = parent
        self.conn = None
        self.cursor = None
        self.updates_made = []
        
    def log_message(self, message, level=None):
        """Log message to QGIS if available"""
        if QGIS_AVAILABLE:
            QgsMessageLog.logMessage(message, "PyArchInit SQLite Updater", level or Qgis.Info)
    
    def check_and_update_database(self):
        """Verifica e aggiorna il database se necessario"""
        try:
            # SEMPRE controlla se ci sono tabelle da ripristinare dai backup
            self._check_and_restore_backup_tables()
            
            # Check if database needs update
            if self.needs_update():
                self.log_message(f"Database {os.path.basename(self.db_path)} necessita aggiornamento")
                
                if QGIS_AVAILABLE and self.parent:
                    reply = QMessageBox.question(
                        self.parent,
                        "Database Vecchio",
                        "Il database sembra essere di una versione precedente.\n"
                        "Vuoi aggiornarlo automaticamente?\n\n"
                        "Verrà creato un backup prima dell'aggiornamento.",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.Yes
                    )
                    
                    if reply == QMessageBox.Yes:
                        return self.update_database()
                    else:
                        return False
                else:
                    # Console mode - update automatically
                    return self.update_database()
            
            return True
            
        except Exception as e:
            self.log_message(f"Errore durante controllo database: {e}", Qgis.Critical if QGIS_AVAILABLE else None)
            return False
    
    def needs_update(self):
        """Verifica se il database necessita di aggiornamento"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            
            # Check if pyarchinit_thesaurus_sigle table exists
            self.cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='pyarchinit_thesaurus_sigle'
            """)
            
            if not self.cursor.fetchone():
                # Table doesn't exist - definitely needs update
                return True
            
            # Check for missing columns in pyarchinit_thesaurus_sigle
            self.cursor.execute("PRAGMA table_info(pyarchinit_thesaurus_sigle)")
            columns = [column[1] for column in self.cursor.fetchall()]
            
            required_columns = ['n_tipologia', 'n_sigla', 'hierarchy_level']
            for col in required_columns:
                if col not in columns:
                    return True
            
            # Check if us_table exists (for cases where tables are in backup)
            self.cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='us_table'
            """)
            if not self.cursor.fetchone():
                # Check for backup tables
                self.cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name LIKE 'us_table_backup_%'
                """)
                if self.cursor.fetchone():
                    # Has backups but no main table - needs restoration
                    return True
            
            # Check if pyarchinit_reperti has quota field
            self.cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='pyarchinit_reperti'
            """)
            if self.cursor.fetchone():
                self.cursor.execute("PRAGMA table_info(pyarchinit_reperti)")
                columns = [column[1] for column in self.cursor.fetchall()]
                if 'quota' not in columns:
                    return True

            # Check if pottery_table has decoration fields
            self.cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='pottery_table'
            """)
            if self.cursor.fetchone():
                self.cursor.execute("PRAGMA table_info(pottery_table)")
                columns = [column[1] for column in self.cursor.fetchall()]
                required_pottery_columns = ['decoration_type', 'decoration_motif', 'decoration_position']
                for col in required_pottery_columns:
                    if col not in columns:
                        return True

            # Check if struttura_table has AR fields
            self.cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='struttura_table'
            """)
            if self.cursor.fetchone():
                self.cursor.execute("PRAGMA table_info(struttura_table)")
                columns = [column[1] for column in self.cursor.fetchall()]
                required_struttura_columns = ['data_compilazione', 'stato_conservazione', 'fasi_funzionali']
                for col in required_struttura_columns:
                    if col not in columns:
                        return True

            # Check if pyarchinit_us_view exists and has order_layer field
            self.cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='view' AND name='pyarchinit_us_view'
            """)
            if not self.cursor.fetchone():
                # View doesn't exist - needs update
                return True
            else:
                # Check if view has order_layer field
                try:
                    # Prima verifica se le tabelle sottostanti esistono
                    self.cursor.execute("""
                        SELECT name FROM sqlite_master 
                        WHERE type IN ('table', 'view') 
                        AND name IN ('pyunitastratigrafiche', 'us_table')
                    """)
                    tables = [row[0] for row in self.cursor.fetchall()]
                    if len(tables) < 2:
                        # Mancano tabelle necessarie
                        self.log_message(f"Tabelle mancanti per pyarchinit_us_view: trovate {tables}")
                        return False  # Non possiamo creare la view senza le tabelle
                    
                    # Verifica se us_table ha order_layer
                    self.cursor.execute("PRAGMA table_info(us_table)")
                    us_columns = [column[1] for column in self.cursor.fetchall()]
                    if 'order_layer' not in us_columns:
                        self.log_message("Campo order_layer non trovato in us_table")
                        return False  # Dobbiamo prima aggiungere il campo alla tabella
                    
                    # Prova a selezionare sia order_layer che cont_per
                    self.cursor.execute("SELECT order_layer, cont_per FROM pyarchinit_us_view LIMIT 1")
                except sqlite3.OperationalError as e:
                    error_msg = str(e)
                    if "no such column: order_layer" in error_msg or "no such column: cont_per" in error_msg:
                        self.log_message(f"View pyarchinit_us_view mancante di colonne: {error_msg}")
                        return True
            
            return False
            
        except Exception as e:
            self.log_message(f"Errore verifica database: {e}", Qgis.Warning if QGIS_AVAILABLE else None)
            return True
        finally:
            if self.conn:
                self.conn.close()
    
    def _check_and_restore_backup_tables(self):
        """Controlla e ripristina silenziosamente tabelle mancanti dai backup"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Lista delle tabelle critiche che devono esistere
            critical_tables = [
                'inventario_materiali_table',
                'pyarchinit_quote',
                'pyarchinit_quote_usm',
                'pyarchinit_us_negative_doc',
                'pyunitastratigrafiche',
                'pyunitastratigrafiche_usm',
                'tomba_table',
                'us_table_toimp'
            ]
            
            restored_any = False
            
            for table_name in critical_tables:
                # Verifica se la tabella esiste
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name=?
                """, (table_name,))
                
                if not cursor.fetchone():
                    # Cerca backup più recente
                    cursor.execute("""
                        SELECT name FROM sqlite_master 
                        WHERE type='table' AND name LIKE ?
                        ORDER BY name DESC LIMIT 1
                    """, (f"{table_name}_backup_%",))
                    
                    result = cursor.fetchone()
                    if result:
                        backup_name = result[0]
                        try:
                            cursor.execute(f"CREATE TABLE {table_name} AS SELECT * FROM {backup_name}")
                            conn.commit()
                            self.log_message(f"Ripristinata tabella {table_name} da {backup_name}")
                            restored_any = True
                        except Exception as e:
                            # Ignora errori - non bloccare l'operazione
                            pass
            
            conn.close()
            
            if restored_any:
                self.log_message("Tabelle mancanti ripristinate dai backup")
                
        except Exception as e:
            # Non bloccare per errori nel controllo backup
            pass
    
    def backup_database(self):
        """Crea un backup del database"""
        backup_path = self.db_path + f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            self.log_message(f"Backup creato: {backup_path}")
            return True
        except Exception as e:
            self.log_message(f"Errore creazione backup: {e}", Qgis.Critical)
            return False
    
    def update_database(self):
        """Esegue l'aggiornamento del database"""
        try:
            # Create backup first
            if not self.backup_database():
                if QGIS_AVAILABLE and self.parent:
                    QMessageBox.warning(
                        self.parent,
                        "Backup Fallito",
                        "Impossibile creare il backup del database.\n"
                        "L'aggiornamento è stato annullato."
                    )
                return False
            
            # Connect to database
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            
            # SEMPRE ripristina tabelle mancanti dai backup se necessario
            # (anche se needs_update() non lo rileva)
            self.restore_tables_from_backups()
            
            # Create/update pyarchinit_thesaurus_sigle table
            self.create_or_update_thesaurus_table()

            # Add pottery thesaurus entries
            self.update_pottery_thesaurus()

            # Add missing columns to various tables
            self.update_us_table()
            self.update_site_table()
            self.update_ut_table()
            self.update_fauna_table()
            self.update_fauna_thesaurus()
            self.update_ut_thesaurus()
            self.fix_thesaurus_nome_tabella()
            self.update_other_tables()
            self.update_struttura_table()

            # Add concurrency columns for sync with PostgreSQL (v5.0+)
            self.add_concurrency_columns()

            # Create missing tables for sync compatibility
            self.create_missing_tables()

            # Create pottery embeddings metadata table for visual similarity search
            self.create_pottery_embeddings_metadata_table()

            # Fix vector layer views
            self.fix_vector_layer_views()

            # Create performance indexes
            self.create_performance_indexes()

            # Commit changes
            self.conn.commit()
            self.conn.close()
            
            # Show result
            if QGIS_AVAILABLE and self.parent:
                message = f"Database aggiornato con successo!\n\n"
                message += f"Modifiche effettuate: {len(self.updates_made)}\n"
                message += f"Backup salvato con estensione .backup\n\n"
                
                # Se abbiamo ricreato delle view, suggerisci di ricaricare
                if any("VIEW" in update for update in self.updates_made):
                    message += "IMPORTANTE: Sono state aggiornate delle view.\n"
                    message += "Si consiglia di:\n"
                    message += "1. Rimuovere e riaggiungere i layer dalle view aggiornate\n"
                    message += "2. O riavviare QGIS per assicurarsi che le modifiche siano caricate"
                
                QMessageBox.information(
                    self.parent,
                    "Aggiornamento Completato",
                    message
                )
            
            self.log_message(
                f"Database aggiornato: {os.path.basename(self.db_path)} ({len(self.updates_made)} modifiche)", 
                Qgis.Success if QGIS_AVAILABLE else None
            )
            
            return True
            
        except Exception as e:
            self.log_message(f"Errore aggiornamento database: {e}", Qgis.Critical if QGIS_AVAILABLE else None)
            if self.conn:
                self.conn.rollback()
                self.conn.close()
            if QGIS_AVAILABLE and self.parent:
                QMessageBox.critical(
                    self.parent,
                    "Errore Aggiornamento",
                    f"Errore durante l'aggiornamento del database:\n{str(e)}"
                )
            return False
    
    def create_or_update_thesaurus_table(self):
        """Crea o aggiorna la tabella pyarchinit_thesaurus_sigle"""
        # Check if table exists
        self.cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='pyarchinit_thesaurus_sigle'
        """)
        
        if not self.cursor.fetchone():
            # Create table
            self.log_message("Creazione tabella pyarchinit_thesaurus_sigle...")
            self.cursor.execute('''
                CREATE TABLE pyarchinit_thesaurus_sigle (
                    id_thesaurus_sigle INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome_tabella TEXT,
                    sigla TEXT,
                    sigla_estesa TEXT,
                    descrizione TEXT,
                    tipologia_sigla TEXT,
                    lingua TEXT,
                    order_layer INTEGER DEFAULT 0,
                    id_parent INTEGER,
                    parent_sigla TEXT,
                    hierarchy_level INTEGER DEFAULT 0,
                    n_tipologia INTEGER,
                    n_sigla INTEGER
                )
            ''')
            self.updates_made.append("CREATE TABLE pyarchinit_thesaurus_sigle")
            
            # Insert default values
            self.cursor.execute('''
                INSERT INTO pyarchinit_thesaurus_sigle 
                (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
                VALUES 
                ('us_table', '1', 'Strato', 'Unità stratigrafica di accumulo', '2.19', 'IT'),
                ('us_table', '2', 'Taglio', 'Unità stratigrafica negativa', '2.19', 'IT'),
                ('us_table', '3', 'Struttura', 'Unità stratigrafica muraria', '2.19', 'IT')
            ''')
        else:
            # Add missing columns
            self.add_column_if_missing('pyarchinit_thesaurus_sigle', 'n_tipologia', 'INTEGER')
            self.add_column_if_missing('pyarchinit_thesaurus_sigle', 'n_sigla', 'INTEGER')
            self.add_column_if_missing('pyarchinit_thesaurus_sigle', 'hierarchy_level', 'INTEGER DEFAULT 0')
            self.add_column_if_missing('pyarchinit_thesaurus_sigle', 'id_parent', 'INTEGER')
            self.add_column_if_missing('pyarchinit_thesaurus_sigle', 'parent_sigla', 'TEXT')
            self.add_column_if_missing('pyarchinit_thesaurus_sigle', 'order_layer', 'INTEGER DEFAULT 0')
    
    def update_us_table(self):
        """Aggiorna la tabella us_table"""
        # Check if table exists
        self.cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='us_table'
        """)
        
        if self.cursor.fetchone():
            # Colonne base
            self.add_column_if_missing('us_table', 'order_layer', 'INTEGER DEFAULT 0')
            self.add_column_if_missing('us_table', 'rapporti2', 'TEXT')
            self.add_column_if_missing('us_table', 'quantificazioni', 'TEXT')
            self.add_column_if_missing('us_table', 'unita_edilizie', 'TEXT')
            self.add_column_if_missing('us_table', 'settore', 'TEXT')
            self.add_column_if_missing('us_table', 'attivita', 'TEXT')
            self.add_column_if_missing('us_table', 'anno_scavo', 'TEXT')
            self.add_column_if_missing('us_table', 'metodo_di_scavo', 'TEXT')
            self.add_column_if_missing('us_table', 'data_schedatura', 'TEXT')
            self.add_column_if_missing('us_table', 'schedatore', 'TEXT')
            self.add_column_if_missing('us_table', 'struttura', 'TEXT')
            
            # Colonne aggiuntive
            self.add_column_if_missing('us_table', 'documentazione', 'TEXT')
            self.add_column_if_missing('us_table', 'unita_tipo', "TEXT DEFAULT 'US'")
            self.add_column_if_missing('us_table', 'quota_min_usm', 'REAL')
            self.add_column_if_missing('us_table', 'quota_max_usm', 'REAL')
            self.add_column_if_missing('us_table', 'doc_usv', "TEXT DEFAULT ''")
            self.add_column_if_missing('us_table', 'organici', 'TEXT')
            self.add_column_if_missing('us_table', 'inorganici', 'TEXT')
            self.add_column_if_missing('us_table', 'cont_per', 'TEXT')
    
    def update_site_table(self):
        """Aggiorna la tabella site_table"""
        # Check if table exists
        self.cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='site_table'
        """)

        if self.cursor.fetchone():
            self.add_column_if_missing('site_table', 'provincia', 'TEXT')
            self.add_column_if_missing('site_table', 'comune', 'TEXT')
            self.add_column_if_missing('site_table', 'toponimo', 'TEXT')
            self.add_column_if_missing('site_table', 'latitudine', 'REAL')
            self.add_column_if_missing('site_table', 'longitudine', 'REAL')
            self.add_column_if_missing('site_table', 'geom', 'TEXT')

    def update_ut_table(self):
        """Aggiorna la tabella ut_table con i nuovi campi survey (v4.9.21+) e analisi (v4.9.67+)"""
        if self.table_exists('ut_table'):
            # New survey fields (v4.9.21+)
            self.add_column_if_missing('ut_table', 'visibility_percent', 'INTEGER')
            self.add_column_if_missing('ut_table', 'vegetation_coverage', 'VARCHAR(255)')
            self.add_column_if_missing('ut_table', 'gps_method', 'VARCHAR(100)')
            self.add_column_if_missing('ut_table', 'coordinate_precision', 'FLOAT')
            self.add_column_if_missing('ut_table', 'survey_type', 'VARCHAR(100)')
            self.add_column_if_missing('ut_table', 'surface_condition', 'VARCHAR(255)')
            self.add_column_if_missing('ut_table', 'accessibility', 'VARCHAR(255)')
            self.add_column_if_missing('ut_table', 'photo_documentation', 'INTEGER')
            self.add_column_if_missing('ut_table', 'weather_conditions', 'VARCHAR(255)')
            self.add_column_if_missing('ut_table', 'team_members', 'TEXT')
            self.add_column_if_missing('ut_table', 'foglio_catastale', 'VARCHAR(100)')
            # Analysis fields (v4.9.67+)
            self.add_column_if_missing('ut_table', 'potential_score', 'REAL')
            self.add_column_if_missing('ut_table', 'risk_score', 'REAL')
            self.add_column_if_missing('ut_table', 'potential_factors', 'TEXT')
            self.add_column_if_missing('ut_table', 'risk_factors', 'TEXT')
            self.add_column_if_missing('ut_table', 'analysis_date', 'TEXT')
            self.add_column_if_missing('ut_table', 'analysis_method', 'TEXT')

    def update_fauna_table(self):
        """Crea o aggiorna la tabella fauna_table (v4.9.21+)"""
        if not self.table_exists('fauna_table'):
            self.log_message("Creazione tabella fauna_table...")
            self.cursor.execute('''
                CREATE TABLE fauna_table (
                    id_fauna INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_us INTEGER,
                    sito TEXT,
                    area TEXT,
                    saggio TEXT,
                    us TEXT,
                    datazione_us TEXT,
                    responsabile_scheda TEXT DEFAULT '',
                    data_compilazione TEXT,
                    documentazione_fotografica TEXT DEFAULT '',
                    metodologia_recupero TEXT DEFAULT '',
                    contesto TEXT DEFAULT '',
                    descrizione_contesto TEXT DEFAULT '',
                    resti_connessione_anatomica TEXT DEFAULT '',
                    tipologia_accumulo TEXT DEFAULT '',
                    deposizione TEXT DEFAULT '',
                    numero_stimato_resti TEXT DEFAULT '',
                    numero_minimo_individui INTEGER DEFAULT 0,
                    specie TEXT DEFAULT '',
                    parti_scheletriche TEXT DEFAULT '',
                    specie_psi TEXT DEFAULT '',
                    misure_ossa TEXT DEFAULT '',
                    stato_frammentazione TEXT DEFAULT '',
                    tracce_combustione TEXT DEFAULT '',
                    combustione_altri_materiali_us INTEGER DEFAULT 0,
                    tipo_combustione TEXT DEFAULT '',
                    segni_tafonomici_evidenti TEXT DEFAULT '',
                    caratterizzazione_segni_tafonomici TEXT DEFAULT '',
                    stato_conservazione TEXT DEFAULT '',
                    alterazioni_morfologiche TEXT DEFAULT '',
                    note_terreno_giacitura TEXT DEFAULT '',
                    campionature_effettuate TEXT DEFAULT '',
                    affidabilita_stratigrafica TEXT DEFAULT '',
                    classi_reperti_associazione TEXT DEFAULT '',
                    osservazioni TEXT DEFAULT '',
                    interpretazione TEXT DEFAULT '',
                    UNIQUE (sito, area, us, id_fauna)
                )
            ''')
            self.updates_made.append("CREATE TABLE fauna_table")

    def update_fauna_thesaurus(self):
        """Installa/aggiorna le voci thesaurus per la tabella fauna_table (v4.9.21+)"""
        try:
            # Check if fauna thesaurus entries exist
            self.cursor.execute("""
                SELECT COUNT(*) FROM pyarchinit_thesaurus_sigle
                WHERE nome_tabella = 'fauna_table'
            """)
            fauna_count = self.cursor.fetchone()[0]

            if fauna_count >= 50:  # Expected ~65 entries for fauna fields
                self.log_message(f"Voci thesaurus fauna_table già presenti ({fauna_count} voci)")
                return

            self.log_message("Aggiunta voci thesaurus per fauna_table...")

            # Fauna thesaurus entries
            fauna_entries = [
                # 13.1 - Contesto
                ('fauna_table', 'DOMESTICO', 'Contesto domestico', 'Contesto residenziale/abitativo', '13.1', 'IT'),
                ('fauna_table', 'RITUALE', 'Contesto rituale', 'Contesto cerimoniale/rituale', '13.1', 'IT'),
                ('fauna_table', 'FUNERARIO', 'Contesto funerario', 'Contesto sepolcrale/funerario', '13.1', 'IT'),
                ('fauna_table', 'PRODUTTIVO', 'Contesto produttivo', 'Contesto artigianale/industriale', '13.1', 'IT'),
                ('fauna_table', 'RIFIUTI', 'Deposito rifiuti', 'Scarico/deposito di rifiuti', '13.1', 'IT'),
                # 13.2 - Metodologia Recupero
                ('fauna_table', 'MANUALE', 'Raccolta manuale', 'Recupero manuale durante lo scavo', '13.2', 'IT'),
                ('fauna_table', 'SETACCIO', 'Setacciatura', 'Recupero mediante setacciatura', '13.2', 'IT'),
                ('fauna_table', 'FLOTTAZIONE', 'Flottazione', 'Recupero mediante flottazione', '13.2', 'IT'),
                # 13.3 - Tipologia Accumulo
                ('fauna_table', 'NATURALE', 'Accumulo naturale', 'Accumulo per cause naturali', '13.3', 'IT'),
                ('fauna_table', 'ANTROPICO', 'Accumulo antropico', 'Accumulo per attività umana', '13.3', 'IT'),
                ('fauna_table', 'MISTO', 'Accumulo misto', 'Accumulo di origine mista', '13.3', 'IT'),
                # 13.4 - Deposizione
                ('fauna_table', 'PRIMARIA', 'Deposizione primaria', 'Deposizione in situ', '13.4', 'IT'),
                ('fauna_table', 'SECONDARIA', 'Deposizione secondaria', 'Deposizione dopo spostamento', '13.4', 'IT'),
                ('fauna_table', 'RIMANEGGIATA', 'Deposizione rimaneggiata', 'Deposizione disturbata', '13.4', 'IT'),
                # 13.5 - Stato Frammentazione
                ('fauna_table', 'INTEGRO', 'Integro', 'Osso completo', '13.5', 'IT'),
                ('fauna_table', 'FRAMMENTATO', 'Frammentato', 'Osso frammentato', '13.5', 'IT'),
                ('fauna_table', 'PARZIALE', 'Parziale', 'Osso parzialmente conservato', '13.5', 'IT'),
                # 13.6 - Stato Conservazione
                ('fauna_table', 'BUONO', 'Buono', 'Buono stato di conservazione', '13.6', 'IT'),
                ('fauna_table', 'MEDIOCRE', 'Mediocre', 'Stato di conservazione mediocre', '13.6', 'IT'),
                ('fauna_table', 'CATTIVO', 'Cattivo', 'Cattivo stato di conservazione', '13.6', 'IT'),
                # 13.7 - Affidabilità Stratigrafica
                ('fauna_table', 'ALTA', 'Alta affidabilità', 'Alta affidabilità stratigrafica', '13.7', 'IT'),
                ('fauna_table', 'MEDIA', 'Media affidabilità', 'Media affidabilità stratigrafica', '13.7', 'IT'),
                ('fauna_table', 'BASSA', 'Bassa affidabilità', 'Bassa affidabilità stratigrafica', '13.7', 'IT'),
                # 13.8 - Tracce Combustione
                ('fauna_table', 'ASSENTI', 'Assenti', 'Nessuna traccia di combustione', '13.8', 'IT'),
                ('fauna_table', 'PRESENTI', 'Presenti', 'Tracce di combustione presenti', '13.8', 'IT'),
                ('fauna_table', 'DIFFUSE', 'Diffuse', 'Tracce di combustione diffuse', '13.8', 'IT'),
                # 13.9 - Tipo Combustione
                ('fauna_table', 'CARBONIZZAZIONE', 'Carbonizzazione', 'Combustione con carbonizzazione', '13.9', 'IT'),
                ('fauna_table', 'CALCINAZIONE', 'Calcinazione', 'Combustione con calcinazione', '13.9', 'IT'),
                ('fauna_table', 'PARZIALE', 'Parziale', 'Combustione parziale', '13.9', 'IT'),
                # 13.10 - Connessione Anatomica
                ('fauna_table', 'SI', 'In connessione', 'Ossa in connessione anatomica', '13.10', 'IT'),
                ('fauna_table', 'NO', 'Non in connessione', 'Ossa disarticolate', '13.10', 'IT'),
                ('fauna_table', 'PARZIALE', 'Parziale', 'Connessione anatomica parziale', '13.10', 'IT'),
                # 13.11 - Specie
                ('fauna_table', 'BOS_TAURUS', 'Bos taurus', 'Bovino domestico', '13.11', 'IT'),
                ('fauna_table', 'OVIS_ARIES', 'Ovis aries', 'Pecora domestica', '13.11', 'IT'),
                ('fauna_table', 'CAPRA_HIRCUS', 'Capra hircus', 'Capra domestica', '13.11', 'IT'),
                ('fauna_table', 'SUS_DOMESTICUS', 'Sus domesticus', 'Maiale domestico', '13.11', 'IT'),
                ('fauna_table', 'OVIS_CAPRA', 'Ovis/Capra', 'Ovicaprino indeterminato', '13.11', 'IT'),
                ('fauna_table', 'CERVUS_ELAPHUS', 'Cervus elaphus', 'Cervo', '13.11', 'IT'),
                ('fauna_table', 'EQUUS_CABALLUS', 'Equus caballus', 'Cavallo', '13.11', 'IT'),
                ('fauna_table', 'CANIS_FAMILIARIS', 'Canis familiaris', 'Cane domestico', '13.11', 'IT'),
                ('fauna_table', 'INDET', 'Indeterminato', 'Specie indeterminata', '13.11', 'IT'),
                # 13.12 - Parti Scheletriche (PSI)
                ('fauna_table', 'CRANIO', 'Cranio', 'Cranio/elementi craniali', '13.12', 'IT'),
                ('fauna_table', 'MANDIBOLA', 'Mandibola', 'Mandibola/mascella', '13.12', 'IT'),
                ('fauna_table', 'VERTEBRE', 'Vertebre', 'Elementi vertebrali', '13.12', 'IT'),
                ('fauna_table', 'COSTE', 'Coste', 'Costole', '13.12', 'IT'),
                ('fauna_table', 'SCAPOLA', 'Scapola', 'Scapola', '13.12', 'IT'),
                ('fauna_table', 'OMERO', 'Omero', 'Omero', '13.12', 'IT'),
                ('fauna_table', 'RADIO', 'Radio', 'Radio', '13.12', 'IT'),
                ('fauna_table', 'ULNA', 'Ulna', 'Ulna', '13.12', 'IT'),
                ('fauna_table', 'PELVI', 'Pelvi', 'Bacino', '13.12', 'IT'),
                ('fauna_table', 'FEMORE', 'Femore', 'Femore', '13.12', 'IT'),
                ('fauna_table', 'TIBIA', 'Tibia', 'Tibia', '13.12', 'IT'),
                ('fauna_table', 'METAPODIO', 'Metapodio', 'Metacarpo/Metatarso', '13.12', 'IT'),
                ('fauna_table', 'FALANGI', 'Falangi', 'Falangi', '13.12', 'IT'),
                # 13.13 - Elemento Anatomico
                ('fauna_table', 'HUM', 'Humerus', 'Omero', '13.13', 'IT'),
                ('fauna_table', 'RAD', 'Radius', 'Radio', '13.13', 'IT'),
                ('fauna_table', 'FEM', 'Femur', 'Femore', '13.13', 'IT'),
                ('fauna_table', 'TIB', 'Tibia', 'Tibia', '13.13', 'IT'),
                ('fauna_table', 'MTC', 'Metacarpus', 'Metacarpo', '13.13', 'IT'),
                ('fauna_table', 'MTT', 'Metatarsus', 'Metatarso', '13.13', 'IT'),
                ('fauna_table', 'AST', 'Astragalus', 'Astragalo', '13.13', 'IT'),
                ('fauna_table', 'CAL', 'Calcaneus', 'Calcagno', '13.13', 'IT'),
                ('fauna_table', 'PHI', 'Phalanx I', 'Prima falange', '13.13', 'IT'),
                ('fauna_table', 'PHII', 'Phalanx II', 'Seconda falange', '13.13', 'IT'),
                ('fauna_table', 'PHIII', 'Phalanx III', 'Terza falange', '13.13', 'IT'),
            ]

            inserted_count = 0
            for entry in fauna_entries:
                try:
                    self.cursor.execute("""
                        INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle
                        (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, entry)
                    inserted_count += 1
                except Exception as e:
                    pass  # Ignore duplicates

            if inserted_count > 0:
                self.log_message(f"Voci thesaurus fauna_table inserite ({inserted_count} voci)")
                self.updates_made.append(f"fauna_table thesaurus ({inserted_count} voci)")

        except Exception as e:
            self.log_message(f"Errore aggiungendo voci thesaurus fauna: {e}", Qgis.Warning if QGIS_AVAILABLE else None)

    def update_ut_thesaurus(self):
        """Installa/aggiorna le voci thesaurus per la tabella ut_table in tutte le 7 lingue supportate (v4.9.68+)"""
        try:
            # Check if UT thesaurus entries exist
            self.cursor.execute("""
                SELECT COUNT(*) FROM pyarchinit_thesaurus_sigle
                WHERE nome_tabella = 'ut_table'
            """)
            ut_count = self.cursor.fetchone()[0]

            if ut_count >= 100:  # Expected ~150+ entries for all languages
                self.log_message(f"Voci thesaurus ut_table già presenti ({ut_count} voci)")
                return

            self.log_message("Aggiunta voci thesaurus per ut_table in tutte le lingue...")

            # UT thesaurus entries in all 7 languages
            # Format: (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
            ut_entries = [
                # ========== 12.1 - Survey Type (Tipo di ricognizione) ==========
                # Italian
                ('ut_table', 'intensive', 'Ricognizione intensiva', 'Ricognizione sistematica intensiva del territorio', '12.1', 'IT'),
                ('ut_table', 'extensive', 'Ricognizione estensiva', 'Ricognizione estensiva a campionamento', '12.1', 'IT'),
                ('ut_table', 'targeted', 'Ricognizione mirata', 'Indagine mirata su aree specifiche', '12.1', 'IT'),
                ('ut_table', 'random', 'Campionamento casuale', 'Metodologia a campionamento casuale', '12.1', 'IT'),
                # English
                ('ut_table', 'intensive', 'Intensive Survey', 'Intensive systematic field walking survey', '12.1', 'en_US'),
                ('ut_table', 'extensive', 'Extensive Survey', 'Extensive reconnaissance survey', '12.1', 'en_US'),
                ('ut_table', 'targeted', 'Targeted Survey', 'Targeted investigation of specific areas', '12.1', 'en_US'),
                ('ut_table', 'random', 'Random Sampling', 'Random sampling methodology', '12.1', 'en_US'),
                # German
                ('ut_table', 'intensive', 'Intensive Begehung', 'Intensive systematische Feldbegehung', '12.1', 'de_DE'),
                ('ut_table', 'extensive', 'Extensive Begehung', 'Extensive Erkundungsbegehung', '12.1', 'de_DE'),
                ('ut_table', 'targeted', 'Gezielte Untersuchung', 'Gezielte Untersuchung bestimmter Gebiete', '12.1', 'de_DE'),
                ('ut_table', 'random', 'Zufallsstichprobe', 'Zufällige Stichprobenmethodik', '12.1', 'de_DE'),
                # Spanish
                ('ut_table', 'intensive', 'Prospección intensiva', 'Prospección sistemática intensiva del territorio', '12.1', 'es_ES'),
                ('ut_table', 'extensive', 'Prospección extensiva', 'Prospección extensiva por muestreo', '12.1', 'es_ES'),
                ('ut_table', 'targeted', 'Prospección dirigida', 'Investigación dirigida en áreas específicas', '12.1', 'es_ES'),
                ('ut_table', 'random', 'Muestreo aleatorio', 'Metodología de muestreo aleatorio', '12.1', 'es_ES'),
                # French
                ('ut_table', 'intensive', 'Prospection intensive', 'Prospection pédestre systématique intensive', '12.1', 'fr_FR'),
                ('ut_table', 'extensive', 'Prospection extensive', 'Prospection de reconnaissance extensive', '12.1', 'fr_FR'),
                ('ut_table', 'targeted', 'Prospection ciblée', 'Investigation ciblée de zones spécifiques', '12.1', 'fr_FR'),
                ('ut_table', 'random', 'Échantillonnage aléatoire', 'Méthodologie d\'échantillonnage aléatoire', '12.1', 'fr_FR'),
                # Arabic
                ('ut_table', 'intensive', 'مسح مكثف', 'مسح ميداني منهجي مكثف', '12.1', 'ar_AR'),
                ('ut_table', 'extensive', 'مسح موسع', 'مسح استطلاعي موسع', '12.1', 'ar_AR'),
                ('ut_table', 'targeted', 'مسح موجه', 'تحقيق موجه لمناطق محددة', '12.1', 'ar_AR'),
                ('ut_table', 'random', 'عينة عشوائية', 'منهجية أخذ العينات العشوائية', '12.1', 'ar_AR'),
                # Catalan
                ('ut_table', 'intensive', 'Prospecció intensiva', 'Prospecció sistemàtica intensiva del territori', '12.1', 'ca_ES'),
                ('ut_table', 'extensive', 'Prospecció extensiva', 'Prospecció extensiva per mostreig', '12.1', 'ca_ES'),
                ('ut_table', 'targeted', 'Prospecció dirigida', 'Investigació dirigida en àrees específiques', '12.1', 'ca_ES'),
                ('ut_table', 'random', 'Mostreig aleatori', 'Metodologia de mostreig aleatori', '12.1', 'ca_ES'),

                # ========== 12.2 - Vegetation Coverage (Copertura vegetale) ==========
                # Italian
                ('ut_table', 'none', 'Assente', 'Terreno nudo senza vegetazione', '12.2', 'IT'),
                ('ut_table', 'sparse', 'Rada', 'Copertura vegetale inferiore al 25%', '12.2', 'IT'),
                ('ut_table', 'moderate', 'Moderata', 'Copertura vegetale tra 25% e 50%', '12.2', 'IT'),
                ('ut_table', 'dense', 'Densa', 'Copertura vegetale tra 50% e 75%', '12.2', 'IT'),
                ('ut_table', 'very_dense', 'Molto densa', 'Copertura vegetale superiore al 75%', '12.2', 'IT'),
                # English
                ('ut_table', 'none', 'No vegetation', 'Bare ground with no vegetation', '12.2', 'en_US'),
                ('ut_table', 'sparse', 'Sparse vegetation', 'Less than 25% vegetation coverage', '12.2', 'en_US'),
                ('ut_table', 'moderate', 'Moderate vegetation', '25-50% vegetation coverage', '12.2', 'en_US'),
                ('ut_table', 'dense', 'Dense vegetation', '50-75% vegetation coverage', '12.2', 'en_US'),
                ('ut_table', 'very_dense', 'Very dense vegetation', 'Over 75% vegetation coverage', '12.2', 'en_US'),
                # German
                ('ut_table', 'none', 'Keine Vegetation', 'Kahler Boden ohne Vegetation', '12.2', 'de_DE'),
                ('ut_table', 'sparse', 'Spärliche Vegetation', 'Weniger als 25% Vegetationsbedeckung', '12.2', 'de_DE'),
                ('ut_table', 'moderate', 'Mäßige Vegetation', '25-50% Vegetationsbedeckung', '12.2', 'de_DE'),
                ('ut_table', 'dense', 'Dichte Vegetation', '50-75% Vegetationsbedeckung', '12.2', 'de_DE'),
                ('ut_table', 'very_dense', 'Sehr dichte Vegetation', 'Über 75% Vegetationsbedeckung', '12.2', 'de_DE'),
                # Spanish
                ('ut_table', 'none', 'Sin vegetación', 'Suelo desnudo sin vegetación', '12.2', 'es_ES'),
                ('ut_table', 'sparse', 'Vegetación dispersa', 'Cobertura vegetal inferior al 25%', '12.2', 'es_ES'),
                ('ut_table', 'moderate', 'Vegetación moderada', 'Cobertura vegetal entre 25% y 50%', '12.2', 'es_ES'),
                ('ut_table', 'dense', 'Vegetación densa', 'Cobertura vegetal entre 50% y 75%', '12.2', 'es_ES'),
                ('ut_table', 'very_dense', 'Vegetación muy densa', 'Cobertura vegetal superior al 75%', '12.2', 'es_ES'),
                # French
                ('ut_table', 'none', 'Absente', 'Sol nu sans végétation', '12.2', 'fr_FR'),
                ('ut_table', 'sparse', 'Clairsemée', 'Couverture végétale inférieure à 25%', '12.2', 'fr_FR'),
                ('ut_table', 'moderate', 'Modérée', 'Couverture végétale entre 25% et 50%', '12.2', 'fr_FR'),
                ('ut_table', 'dense', 'Dense', 'Couverture végétale entre 50% et 75%', '12.2', 'fr_FR'),
                ('ut_table', 'very_dense', 'Très dense', 'Couverture végétale supérieure à 75%', '12.2', 'fr_FR'),
                # Arabic
                ('ut_table', 'none', 'لا نباتات', 'أرض جرداء بدون نباتات', '12.2', 'ar_AR'),
                ('ut_table', 'sparse', 'نباتات متناثرة', 'تغطية نباتية أقل من 25%', '12.2', 'ar_AR'),
                ('ut_table', 'moderate', 'نباتات معتدلة', 'تغطية نباتية بين 25% و50%', '12.2', 'ar_AR'),
                ('ut_table', 'dense', 'نباتات كثيفة', 'تغطية نباتية بين 50% و75%', '12.2', 'ar_AR'),
                ('ut_table', 'very_dense', 'نباتات كثيفة جداً', 'تغطية نباتية أكثر من 75%', '12.2', 'ar_AR'),
                # Catalan
                ('ut_table', 'none', 'Absent', 'Terreny nu sense vegetació', '12.2', 'ca_ES'),
                ('ut_table', 'sparse', 'Escassa', 'Cobertura vegetal inferior al 25%', '12.2', 'ca_ES'),
                ('ut_table', 'moderate', 'Moderada', 'Cobertura vegetal entre 25% i 50%', '12.2', 'ca_ES'),
                ('ut_table', 'dense', 'Densa', 'Cobertura vegetal entre 50% i 75%', '12.2', 'ca_ES'),
                ('ut_table', 'very_dense', 'Molt densa', 'Cobertura vegetal superior al 75%', '12.2', 'ca_ES'),

                # ========== 12.3 - GPS Method (Metodo GPS) ==========
                # Italian
                ('ut_table', 'handheld', 'GPS portatile', 'Dispositivo GPS portatile', '12.3', 'IT'),
                ('ut_table', 'dgps', 'GPS differenziale', 'DGPS con correzione da stazione base', '12.3', 'IT'),
                ('ut_table', 'rtk', 'GPS RTK', 'GPS cinematico in tempo reale', '12.3', 'IT'),
                ('ut_table', 'total_station', 'Stazione totale', 'Rilievo con stazione totale', '12.3', 'IT'),
                # English
                ('ut_table', 'handheld', 'Handheld GPS', 'Handheld GPS device', '12.3', 'en_US'),
                ('ut_table', 'dgps', 'Differential GPS', 'DGPS with base station correction', '12.3', 'en_US'),
                ('ut_table', 'rtk', 'RTK GPS', 'Real-time kinematic GPS', '12.3', 'en_US'),
                ('ut_table', 'total_station', 'Total Station', 'Total station survey', '12.3', 'en_US'),
                # German
                ('ut_table', 'handheld', 'Hand-GPS', 'Tragbares GPS-Gerät', '12.3', 'de_DE'),
                ('ut_table', 'dgps', 'Differentielles GPS', 'DGPS mit Basisstationskorrektur', '12.3', 'de_DE'),
                ('ut_table', 'rtk', 'RTK-GPS', 'Echtzeit-kinematisches GPS', '12.3', 'de_DE'),
                ('ut_table', 'total_station', 'Totalstation', 'Vermessung mit Totalstation', '12.3', 'de_DE'),
                # Spanish
                ('ut_table', 'handheld', 'GPS portátil', 'Dispositivo GPS portátil', '12.3', 'es_ES'),
                ('ut_table', 'dgps', 'GPS diferencial', 'DGPS con corrección de estación base', '12.3', 'es_ES'),
                ('ut_table', 'rtk', 'GPS RTK', 'GPS cinemático en tiempo real', '12.3', 'es_ES'),
                ('ut_table', 'total_station', 'Estación total', 'Levantamiento con estación total', '12.3', 'es_ES'),
                # French
                ('ut_table', 'handheld', 'GPS portable', 'Appareil GPS portable', '12.3', 'fr_FR'),
                ('ut_table', 'dgps', 'GPS différentiel', 'DGPS avec correction de station de base', '12.3', 'fr_FR'),
                ('ut_table', 'rtk', 'GPS RTK', 'GPS cinématique en temps réel', '12.3', 'fr_FR'),
                ('ut_table', 'total_station', 'Station totale', 'Levé avec station totale', '12.3', 'fr_FR'),
                # Arabic
                ('ut_table', 'handheld', 'GPS محمول', 'جهاز GPS محمول باليد', '12.3', 'ar_AR'),
                ('ut_table', 'dgps', 'GPS تفاضلي', 'DGPS مع تصحيح محطة القاعدة', '12.3', 'ar_AR'),
                ('ut_table', 'rtk', 'GPS RTK', 'GPS حركي في الوقت الحقيقي', '12.3', 'ar_AR'),
                ('ut_table', 'total_station', 'محطة كاملة', 'مسح بالمحطة الكاملة', '12.3', 'ar_AR'),
                # Catalan
                ('ut_table', 'handheld', 'GPS portàtil', 'Dispositiu GPS portàtil', '12.3', 'ca_ES'),
                ('ut_table', 'dgps', 'GPS diferencial', 'DGPS amb correcció d\'estació base', '12.3', 'ca_ES'),
                ('ut_table', 'rtk', 'GPS RTK', 'GPS cinemàtic en temps real', '12.3', 'ca_ES'),
                ('ut_table', 'total_station', 'Estació total', 'Aixecament amb estació total', '12.3', 'ca_ES'),

                # ========== 12.4 - Surface Condition (Condizione del suolo) ==========
                # Italian
                ('ut_table', 'ploughed', 'Arato', 'Campo arato di recente', '12.4', 'IT'),
                ('ut_table', 'stubble', 'Stoppie', 'Presenza di stoppie', '12.4', 'IT'),
                ('ut_table', 'pasture', 'Pascolo', 'Terreno a pascolo/prato', '12.4', 'IT'),
                ('ut_table', 'woodland', 'Bosco', 'Area boscata', '12.4', 'IT'),
                ('ut_table', 'urban', 'Urbano', 'Area urbana/edificata', '12.4', 'IT'),
                # English
                ('ut_table', 'ploughed', 'Ploughed', 'Recently ploughed field', '12.4', 'en_US'),
                ('ut_table', 'stubble', 'Stubble', 'Crop stubble present', '12.4', 'en_US'),
                ('ut_table', 'pasture', 'Pasture', 'Grassland/pasture', '12.4', 'en_US'),
                ('ut_table', 'woodland', 'Woodland', 'Wooded area', '12.4', 'en_US'),
                ('ut_table', 'urban', 'Urban', 'Urban/built area', '12.4', 'en_US'),
                # German
                ('ut_table', 'ploughed', 'Gepflügt', 'Kürzlich gepflügtes Feld', '12.4', 'de_DE'),
                ('ut_table', 'stubble', 'Stoppelfeld', 'Stoppeln vorhanden', '12.4', 'de_DE'),
                ('ut_table', 'pasture', 'Weideland', 'Grünland/Weide', '12.4', 'de_DE'),
                ('ut_table', 'woodland', 'Waldgebiet', 'Bewaldetes Gebiet', '12.4', 'de_DE'),
                ('ut_table', 'urban', 'Städtisch', 'Städtisches/bebautes Gebiet', '12.4', 'de_DE'),
                # Spanish
                ('ut_table', 'ploughed', 'Arado', 'Campo arado recientemente', '12.4', 'es_ES'),
                ('ut_table', 'stubble', 'Rastrojo', 'Presencia de rastrojo', '12.4', 'es_ES'),
                ('ut_table', 'pasture', 'Pasto', 'Pradera/pastizal', '12.4', 'es_ES'),
                ('ut_table', 'woodland', 'Bosque', 'Zona boscosa', '12.4', 'es_ES'),
                ('ut_table', 'urban', 'Urbano', 'Zona urbana/edificada', '12.4', 'es_ES'),
                # French
                ('ut_table', 'ploughed', 'Labouré', 'Champ labouré récemment', '12.4', 'fr_FR'),
                ('ut_table', 'stubble', 'Chaume', 'Présence de chaume', '12.4', 'fr_FR'),
                ('ut_table', 'pasture', 'Pâturage', 'Prairie/pâturage', '12.4', 'fr_FR'),
                ('ut_table', 'woodland', 'Boisé', 'Zone boisée', '12.4', 'fr_FR'),
                ('ut_table', 'urban', 'Urbain', 'Zone urbaine/bâtie', '12.4', 'fr_FR'),
                # Arabic
                ('ut_table', 'ploughed', 'محروث', 'حقل محروث حديثاً', '12.4', 'ar_AR'),
                ('ut_table', 'stubble', 'قش', 'وجود بقايا المحاصيل', '12.4', 'ar_AR'),
                ('ut_table', 'pasture', 'مرعى', 'أرض عشبية/مرعى', '12.4', 'ar_AR'),
                ('ut_table', 'woodland', 'غابة', 'منطقة حرجية', '12.4', 'ar_AR'),
                ('ut_table', 'urban', 'حضري', 'منطقة حضرية/مبنية', '12.4', 'ar_AR'),
                # Catalan
                ('ut_table', 'ploughed', 'Llautat', 'Camp llautat recentment', '12.4', 'ca_ES'),
                ('ut_table', 'stubble', 'Rostoll', 'Presència de rostoll', '12.4', 'ca_ES'),
                ('ut_table', 'pasture', 'Pastura', 'Prat/pastura', '12.4', 'ca_ES'),
                ('ut_table', 'woodland', 'Bosc', 'Àrea boscosa', '12.4', 'ca_ES'),
                ('ut_table', 'urban', 'Urbà', 'Àrea urbana/edificada', '12.4', 'ca_ES'),

                # ========== 12.5 - Accessibility (Accessibilità) ==========
                # Italian
                ('ut_table', 'easy', 'Facile accesso', 'Nessuna restrizione di accesso', '12.5', 'IT'),
                ('ut_table', 'moderate_access', 'Accesso moderato', 'Alcune restrizioni o difficoltà', '12.5', 'IT'),
                ('ut_table', 'difficult', 'Accesso difficile', 'Significativi problemi di accesso', '12.5', 'IT'),
                ('ut_table', 'restricted', 'Accesso ristretto', 'Accesso solo su autorizzazione', '12.5', 'IT'),
                # English
                ('ut_table', 'easy', 'Easy access', 'No restrictions on access', '12.5', 'en_US'),
                ('ut_table', 'moderate_access', 'Moderate access', 'Some restrictions or difficulties', '12.5', 'en_US'),
                ('ut_table', 'difficult', 'Difficult access', 'Significant access problems', '12.5', 'en_US'),
                ('ut_table', 'restricted', 'Restricted access', 'Access by permission only', '12.5', 'en_US'),
                # German
                ('ut_table', 'easy', 'Leichter Zugang', 'Keine Zugangsbeschränkungen', '12.5', 'de_DE'),
                ('ut_table', 'moderate_access', 'Mäßiger Zugang', 'Einige Einschränkungen oder Schwierigkeiten', '12.5', 'de_DE'),
                ('ut_table', 'difficult', 'Schwieriger Zugang', 'Erhebliche Zugangsprobleme', '12.5', 'de_DE'),
                ('ut_table', 'restricted', 'Eingeschränkter Zugang', 'Zugang nur mit Genehmigung', '12.5', 'de_DE'),
                # Spanish
                ('ut_table', 'easy', 'Acceso fácil', 'Sin restricciones de acceso', '12.5', 'es_ES'),
                ('ut_table', 'moderate_access', 'Acceso moderado', 'Algunas restricciones o dificultades', '12.5', 'es_ES'),
                ('ut_table', 'difficult', 'Acceso difícil', 'Problemas significativos de acceso', '12.5', 'es_ES'),
                ('ut_table', 'restricted', 'Acceso restringido', 'Acceso solo con permiso', '12.5', 'es_ES'),
                # French
                ('ut_table', 'easy', 'Accès facile', 'Aucune restriction d\'accès', '12.5', 'fr_FR'),
                ('ut_table', 'moderate_access', 'Accès modéré', 'Quelques restrictions ou difficultés', '12.5', 'fr_FR'),
                ('ut_table', 'difficult', 'Accès difficile', 'Problèmes d\'accès importants', '12.5', 'fr_FR'),
                ('ut_table', 'restricted', 'Accès restreint', 'Accès sur autorisation uniquement', '12.5', 'fr_FR'),
                # Arabic
                ('ut_table', 'easy', 'وصول سهل', 'لا قيود على الوصول', '12.5', 'ar_AR'),
                ('ut_table', 'moderate_access', 'وصول معتدل', 'بعض القيود أو الصعوبات', '12.5', 'ar_AR'),
                ('ut_table', 'difficult', 'وصول صعب', 'مشاكل وصول كبيرة', '12.5', 'ar_AR'),
                ('ut_table', 'restricted', 'وصول مقيد', 'الوصول بإذن فقط', '12.5', 'ar_AR'),
                # Catalan
                ('ut_table', 'easy', 'Accés fàcil', 'Sense restriccions d\'accés', '12.5', 'ca_ES'),
                ('ut_table', 'moderate_access', 'Accés moderat', 'Algunes restriccions o dificultats', '12.5', 'ca_ES'),
                ('ut_table', 'difficult', 'Accés difícil', 'Problemes significatius d\'accés', '12.5', 'ca_ES'),
                ('ut_table', 'restricted', 'Accés restringit', 'Accés només amb permís', '12.5', 'ca_ES'),

                # ========== 12.6 - Weather Conditions (Condizioni meteo) ==========
                # Italian
                ('ut_table', 'sunny', 'Soleggiato', 'Tempo sereno e soleggiato', '12.6', 'IT'),
                ('ut_table', 'cloudy', 'Nuvoloso', 'Condizioni nuvolose', '12.6', 'IT'),
                ('ut_table', 'rainy', 'Piovoso', 'Pioggia durante la ricognizione', '12.6', 'IT'),
                ('ut_table', 'windy', 'Ventoso', 'Vento forte', '12.6', 'IT'),
                # English
                ('ut_table', 'sunny', 'Sunny', 'Clear and sunny weather', '12.6', 'en_US'),
                ('ut_table', 'cloudy', 'Cloudy', 'Overcast conditions', '12.6', 'en_US'),
                ('ut_table', 'rainy', 'Rainy', 'Rain during survey', '12.6', 'en_US'),
                ('ut_table', 'windy', 'Windy', 'Strong winds', '12.6', 'en_US'),
                # German
                ('ut_table', 'sunny', 'Sonnig', 'Klares und sonniges Wetter', '12.6', 'de_DE'),
                ('ut_table', 'cloudy', 'Bewölkt', 'Bedeckte Verhältnisse', '12.6', 'de_DE'),
                ('ut_table', 'rainy', 'Regnerisch', 'Regen während der Begehung', '12.6', 'de_DE'),
                ('ut_table', 'windy', 'Windig', 'Starker Wind', '12.6', 'de_DE'),
                # Spanish
                ('ut_table', 'sunny', 'Soleado', 'Tiempo despejado y soleado', '12.6', 'es_ES'),
                ('ut_table', 'cloudy', 'Nublado', 'Condiciones nubladas', '12.6', 'es_ES'),
                ('ut_table', 'rainy', 'Lluvioso', 'Lluvia durante la prospección', '12.6', 'es_ES'),
                ('ut_table', 'windy', 'Ventoso', 'Vientos fuertes', '12.6', 'es_ES'),
                # French
                ('ut_table', 'sunny', 'Ensoleillé', 'Temps clair et ensoleillé', '12.6', 'fr_FR'),
                ('ut_table', 'cloudy', 'Nuageux', 'Conditions nuageuses', '12.6', 'fr_FR'),
                ('ut_table', 'rainy', 'Pluvieux', 'Pluie pendant la prospection', '12.6', 'fr_FR'),
                ('ut_table', 'windy', 'Venteux', 'Vents forts', '12.6', 'fr_FR'),
                # Arabic
                ('ut_table', 'sunny', 'مشمس', 'طقس صافٍ ومشمس', '12.6', 'ar_AR'),
                ('ut_table', 'cloudy', 'غائم', 'ظروف غائمة', '12.6', 'ar_AR'),
                ('ut_table', 'rainy', 'ممطر', 'أمطار أثناء المسح', '12.6', 'ar_AR'),
                ('ut_table', 'windy', 'عاصف', 'رياح قوية', '12.6', 'ar_AR'),
                # Catalan
                ('ut_table', 'sunny', 'Assolellat', 'Temps clar i assolellat', '12.6', 'ca_ES'),
                ('ut_table', 'cloudy', 'Ennuvolat', 'Condicions ennuvolades', '12.6', 'ca_ES'),
                ('ut_table', 'rainy', 'Plujós', 'Pluja durant la prospecció', '12.6', 'ca_ES'),
                ('ut_table', 'windy', 'Ventós', 'Vents forts', '12.6', 'ca_ES'),
            ]

            inserted_count = 0
            for entry in ut_entries:
                try:
                    self.cursor.execute("""
                        INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle
                        (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, entry)
                    if self.cursor.rowcount > 0:
                        inserted_count += 1
                except Exception as e:
                    pass  # Ignore duplicates

            if inserted_count > 0:
                self.log_message(f"Voci thesaurus ut_table inserite ({inserted_count} voci)")
                self.updates_made.append(f"ut_table thesaurus ({inserted_count} voci)")

        except Exception as e:
            self.log_message(f"Errore aggiungendo voci thesaurus UT: {e}", Qgis.Warning if QGIS_AVAILABLE else None)

    def fix_thesaurus_nome_tabella(self):
        """Fix thesaurus entries that have display names instead of actual table names.

        This migration fixes a bug where the Thesaurus form was saving entries with
        display names (e.g., 'Fauna') instead of actual table names (e.g., 'fauna_table').
        Forms query using actual table names, so entries with display names were not found.
        """
        try:
            # Mapping from display names to actual table names
            display_to_table = {
                'Fauna': 'fauna_table',
                'US': 'us_table',
                'USM': 'us_table_usm',
                'Sito': 'site_table',
                'Periodizzazione': 'periodizzazione_table',
                'Inventario Materiali': 'inventario_materiali_table',
                'Inventario Lapidei': 'inventario_lapidei_table',
                'Struttura': 'struttura_table',
                'Tomba': 'tomba_table',
                'Campioni': 'campioni_table',
                'UT': 'ut_table',
                'Tafonomia': 'tafonomia_table',
                'Individui': 'individui_table',
                'Pottery': 'pottery_table',
                'Archeozoologia': 'archeozoo_table',
            }

            total_fixed = 0
            for display_name, table_name in display_to_table.items():
                try:
                    self.cursor.execute("""
                        UPDATE pyarchinit_thesaurus_sigle
                        SET nome_tabella = ?
                        WHERE nome_tabella = ?
                    """, (table_name, display_name))
                    rows_updated = self.cursor.rowcount
                    if rows_updated > 0:
                        total_fixed += rows_updated
                        self.log_message(f"Fixed {rows_updated} thesaurus entries: '{display_name}' -> '{table_name}'")
                except Exception as e:
                    self.log_message(f"Error fixing '{display_name}': {e}", Qgis.Warning if QGIS_AVAILABLE else None)

            if total_fixed > 0:
                self.log_message(f"Thesaurus nome_tabella fix: {total_fixed} entries corrected")
                self.updates_made.append(f"thesaurus nome_tabella fix ({total_fixed} voci)")

        except Exception as e:
            self.log_message(f"Error fixing thesaurus nome_tabella: {e}", Qgis.Warning if QGIS_AVAILABLE else None)

    def update_other_tables(self):
        """Aggiorna altre tabelle"""
        # inventario_materiali_table
        if self.table_exists('inventario_materiali_table'):
            self.add_column_if_missing('inventario_materiali_table', 'years', 'TEXT')
            self.add_column_if_missing('inventario_materiali_table', 'weight', 'REAL')
            self.add_column_if_missing('inventario_materiali_table', 'forme_minime', 'INTEGER')
            self.add_column_if_missing('inventario_materiali_table', 'forme_massime', 'INTEGER')
            self.add_column_if_missing('inventario_materiali_table', 'totale_frammenti', 'INTEGER')
            self.add_column_if_missing('inventario_materiali_table', 'stato_conservazione', 'TEXT')
            # Nuovi campi per nomi foto e disegni
            self.add_column_if_missing('inventario_materiali_table', 'photo_id', 'TEXT')
            self.add_column_if_missing('inventario_materiali_table', 'drawing_id', 'TEXT')
        
        # pottery_table
        if self.table_exists('pottery_table'):
            self.add_column_if_missing('pottery_table', 'anno', 'TEXT')
            self.add_column_if_missing('pottery_table', 'fabric', 'TEXT')
            self.add_column_if_missing('pottery_table', 'percent', 'TEXT')
            self.add_column_if_missing('pottery_table', 'material', 'TEXT')
            self.add_column_if_missing('pottery_table', 'form', 'TEXT')
            self.add_column_if_missing('pottery_table', 'decoration_type', 'TEXT')
            self.add_column_if_missing('pottery_table', 'decoration_motif', 'TEXT')
            self.add_column_if_missing('pottery_table', 'decoration_position', 'TEXT')
        
        # pyarchinit_reperti
        if self.table_exists('pyarchinit_reperti'):
            self.add_column_if_missing('pyarchinit_reperti', 'quota', 'REAL')
            # Ricrea la view con il nuovo campo quota
            self._recreate_reperti_view()

    def update_struttura_table(self):
        """Aggiorna la tabella struttura_table con i nuovi campi per scheda AR"""
        if self.table_exists('struttura_table'):
            # Campi generali
            self.add_column_if_missing('struttura_table', 'data_compilazione', 'TEXT')
            self.add_column_if_missing('struttura_table', 'nome_compilatore', 'TEXT')
            # Stato conservazione
            self.add_column_if_missing('struttura_table', 'stato_conservazione', 'TEXT')
            # Dati generali architettura
            self.add_column_if_missing('struttura_table', 'quota', 'REAL')
            self.add_column_if_missing('struttura_table', 'relazione_topografica', 'TEXT')
            self.add_column_if_missing('struttura_table', 'prospetto_ingresso', 'TEXT')
            self.add_column_if_missing('struttura_table', 'orientamento_ingresso', 'TEXT')
            self.add_column_if_missing('struttura_table', 'articolazione', 'TEXT')
            self.add_column_if_missing('struttura_table', 'n_ambienti', 'INTEGER')
            self.add_column_if_missing('struttura_table', 'orientamento_ambienti', 'TEXT')
            self.add_column_if_missing('struttura_table', 'sviluppo_planimetrico', 'TEXT')
            self.add_column_if_missing('struttura_table', 'elementi_costitutivi', 'TEXT')
            self.add_column_if_missing('struttura_table', 'motivo_decorativo', 'TEXT')
            # Dati archeologici
            self.add_column_if_missing('struttura_table', 'potenzialita_archeologica', 'TEXT')
            self.add_column_if_missing('struttura_table', 'manufatti', 'TEXT')
            self.add_column_if_missing('struttura_table', 'elementi_datanti', 'TEXT')
            self.add_column_if_missing('struttura_table', 'fasi_funzionali', 'TEXT')

            # Aggiorna la view pyarchinit_strutture_view
            self._update_strutture_view()

    def _update_strutture_view(self):
        """Aggiorna/ricrea la view pyarchinit_strutture_view con i nuovi campi AR"""
        try:
            # Verifica se la view esiste e se ha i nuovi campi AR
            self.cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='view' AND name='pyarchinit_strutture_view'
            """)
            view_exists = self.cursor.fetchone() is not None

            # Verifica se le tabelle necessarie esistono
            geo_exists = self.table_exists('pyarchinit_strutture_ipotesi')
            if not geo_exists or not self.table_exists('struttura_table'):
                self.log_message("Tabelle necessarie per pyarchinit_strutture_view non trovate, skip")
                return

            # Controlla se la view ha già i campi AR
            if view_exists:
                try:
                    self.cursor.execute("SELECT data_compilazione FROM pyarchinit_strutture_view LIMIT 1")
                    self.log_message("View pyarchinit_strutture_view già aggiornata con campi AR")
                    return
                except:
                    pass  # La view non ha i campi, dobbiamo ricrearla

            # Drop e ricrea la view
            self.cursor.execute("DROP VIEW IF EXISTS pyarchinit_strutture_view")

            create_view_sql = """
                CREATE VIEW pyarchinit_strutture_view AS
                SELECT a.gid,
                    a.sito,
                    a.id_strutt,
                    a.per_iniz,
                    a.per_fin,
                    a.dataz_ext,
                    a.fase_iniz,
                    a.fase_fin,
                    a.descrizione,
                    a.the_geom,
                    a.sigla_strut,
                    a.nr_strut,
                    b.id_struttura,
                    b.sito AS sito_1,
                    b.sigla_struttura,
                    b.numero_struttura,
                    b.categoria_struttura,
                    b.tipologia_struttura,
                    b.definizione_struttura,
                    b.descrizione AS descrizione_1,
                    b.interpretazione,
                    b.periodo_iniziale,
                    b.fase_iniziale,
                    b.periodo_finale,
                    b.fase_finale,
                    b.datazione_estesa,
                    b.materiali_impiegati,
                    b.elementi_strutturali,
                    b.rapporti_struttura,
                    b.misure_struttura,
                    b.data_compilazione,
                    b.nome_compilatore,
                    b.stato_conservazione,
                    b.quota,
                    b.relazione_topografica,
                    b.prospetto_ingresso,
                    b.orientamento_ingresso,
                    b.articolazione,
                    b.n_ambienti,
                    b.orientamento_ambienti,
                    b.sviluppo_planimetrico,
                    b.elementi_costitutivi,
                    b.motivo_decorativo,
                    b.potenzialita_archeologica,
                    b.manufatti,
                    b.elementi_datanti,
                    b.fasi_funzionali
                FROM pyarchinit_strutture_ipotesi a
                JOIN struttura_table b ON a.sito = b.sito
                    AND a.sigla_strut = b.sigla_struttura
                    AND a.nr_strut = b.numero_struttura
            """
            self.cursor.execute(create_view_sql)
            self.log_message("View pyarchinit_strutture_view aggiornata con campi AR")
            self.updates_made.append("pyarchinit_strutture_view: aggiornata con campi AR")

        except Exception as e:
            self.log_message(f"Errore durante l'aggiornamento della view strutture: {e}")

    def restore_tables_from_backups(self):
        """Ripristina tabelle mancanti dai backup se necessario"""
        # Lista delle tabelle che potrebbero dover essere ripristinate
        tables_to_check = {
            'us_table': 'us_table_backup_%',
            'campioni_table': 'campioni_table_backup_%',
            'inventario_materiali_table': 'inventario_materiali_table_backup_%',
            'pottery_table': 'pottery_table_backup_%',
            'pyarchinit_quote': 'pyarchinit_quote_backup_%',
            'pyarchinit_quote_usm': 'pyarchinit_quote_usm_backup_%',
            'pyunitastratigrafiche': 'pyunitastratigrafiche_backup_%',
            'pyunitastratigrafiche_usm': 'pyunitastratigrafiche_usm_backup_%',
            'tomba_table': 'tomba_table_backup_%'
        }
        
        # Tabelle che hanno geometrie
        geometry_tables = {
            'pyunitastratigrafiche': ('the_geom', 'MULTIPOLYGON'),
            'pyunitastratigrafiche_usm': ('the_geom', 'MULTIPOLYGON'),
            'pyarchinit_quote': ('the_geom', 'POINT'),
            'pyarchinit_quote_usm': ('the_geom', 'POINT')
        }
        
        restored_geometry_tables = []
        
        for table_name, backup_pattern in tables_to_check.items():
            # Verifica se la tabella principale esiste
            if not self.table_exists(table_name):
                # Cerca backup disponibili
                self.cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name LIKE ?
                    ORDER BY name DESC LIMIT 1
                """, (backup_pattern.replace('%', '%'),))
                
                result = self.cursor.fetchone()
                if result:
                    backup_name = result[0]
                    try:
                        # Ripristina la tabella dal backup
                        self.cursor.execute(f"CREATE TABLE {table_name} AS SELECT * FROM {backup_name}")
                        self.log_message(f"Ripristinata tabella {table_name} da {backup_name}")
                        self.updates_made.append(f"RESTORE TABLE {table_name}")
                        
                        # Segna se ha geometrie da recuperare
                        if table_name in geometry_tables:
                            restored_geometry_tables.append(table_name)
                            
                    except Exception as e:
                        self.log_message(f"Errore ripristinando {table_name}: {e}", Qgis.Warning if QGIS_AVAILABLE else None)
        
        # Se abbiamo ripristinato tabelle con geometrie, proviamo a recuperarle
        if restored_geometry_tables:
            self._recover_geometry_columns(restored_geometry_tables, geometry_tables)
    
    def _recover_geometry_columns(self, tables_list, geometry_definitions):
        """Recupera le colonne geometriche dopo il ripristino"""
        try:
            # Ottieni SRID dal database
            self.cursor.execute("SELECT srid FROM geometry_columns LIMIT 1")
            result = self.cursor.fetchone()
            srid = result[0] if result else 3004  # Default SRID Italia
            
            for table_name in tables_list:
                if table_name in geometry_definitions:
                    geom_col, geom_type = geometry_definitions[table_name]
                    
                    # Verifica se la colonna è già registrata
                    self.cursor.execute("""
                        SELECT * FROM geometry_columns 
                        WHERE f_table_name = ? AND f_geometry_column = ?
                    """, (table_name, geom_col))
                    
                    if not self.cursor.fetchone():
                        # Prova a recuperare la colonna geometrica
                        try:
                            self.cursor.execute(
                                f"SELECT RecoverGeometryColumn('{table_name}', '{geom_col}', {srid}, '{geom_type}', 'XY')"
                            )
                            self.log_message(f"Recuperata geometria per {table_name}.{geom_col}")
                            
                            # Crea indice spaziale
                            self.cursor.execute(f"SELECT CreateSpatialIndex('{table_name}', '{geom_col}')")
                            
                        except Exception as e:
                            self.log_message(f"Non riesco a recuperare geometria per {table_name}: {e}")
                            
        except Exception as e:
            self.log_message(f"Errore nel recupero geometrie: {e}")

    def create_pottery_embeddings_metadata_table(self):
        """Create pottery embeddings metadata table for visual similarity search"""
        # Check if table exists
        self.cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='pottery_embeddings_metadata_table'
        """)

        if not self.cursor.fetchone():
            # Create table
            self.log_message("Creazione tabella pottery_embeddings_metadata_table...")
            self.cursor.execute('''
                CREATE TABLE pottery_embeddings_metadata_table (
                    id_embedding INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_rep INTEGER NOT NULL,
                    id_media INTEGER NOT NULL,
                    image_hash TEXT NOT NULL,
                    model_name TEXT NOT NULL,
                    search_type TEXT NOT NULL,
                    embedding_version TEXT DEFAULT '1.0',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(id_media, model_name, search_type)
                )
            ''')
            # Create indexes for faster queries
            self.cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_pottery_emb_id_rep
                ON pottery_embeddings_metadata_table(id_rep)
            ''')
            self.cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_pottery_emb_model
                ON pottery_embeddings_metadata_table(model_name, search_type)
            ''')
            self.updates_made.append("CREATE TABLE pottery_embeddings_metadata_table")

    def fix_vector_layer_views(self):
        """Corregge i tipi di campo nelle view dei layer vettoriali"""
        # Prima correggi i tipi di campo nelle tabelle base
        self.fix_field_types_in_base_tables()
        
        views_to_fix = [
            ('pyarchinit_us_view', '''
                CREATE VIEW pyarchinit_us_view AS
                SELECT 
                    CAST(pyunitastratigrafiche.gid AS INTEGER) as gid,
                    pyunitastratigrafiche.the_geom,
                    pyunitastratigrafiche.tipo_us_s,
                    pyunitastratigrafiche.scavo_s,
                    pyunitastratigrafiche.area_s,
                    pyunitastratigrafiche.us_s,
                    pyunitastratigrafiche.stratigraph_index_us,
                    us_table.id_us,
                    us_table.sito,
                    us_table.area,
                    us_table.us,
                    us_table.struttura,
                    us_table.d_stratigrafica,
                    us_table.d_interpretativa,
                    us_table.descrizione,
                    us_table.interpretazione,
                    us_table.rapporti,
                    us_table.periodo_iniziale,
                    us_table.fase_iniziale,
                    us_table.periodo_finale,
                    us_table.fase_finale,
                    us_table.attivita,
                    us_table.anno_scavo,
                    us_table.metodo_di_scavo,
                    us_table.inclusi,
                    us_table.campioni,
                    us_table.organici,
                    us_table.inorganici,
                    us_table.data_schedatura,
                    us_table.schedatore,
                    us_table.formazione,
                    us_table.stato_di_conservazione,
                    us_table.colore,
                    us_table.consistenza,
                    us_table.unita_tipo,
                    us_table.settore,
                    us_table.quad_par,
                    us_table.ambient,
                    us_table.saggio,
                    us_table.elem_datanti,
                    us_table.funz_statica,
                    us_table.lavorazione,
                    us_table.spess_giunti,
                    us_table.letti_posa,
                    us_table.alt_mod,
                    us_table.un_ed_riass,
                    us_table.reimp,
                    us_table.posa_opera,
                    us_table.quota_min_usm,
                    us_table.quota_max_usm,
                    us_table.cons_legante,
                    us_table.col_legante,
                    us_table.aggreg_legante,
                    us_table.con_text_mat,
                    us_table.col_materiale,
                    us_table.inclusi_materiali_usm,
                    us_table.n_catalogo_generale,
                    us_table.n_catalogo_interno,
                    us_table.n_catalogo_internazionale,
                    us_table.soprintendenza,
                    us_table.quota_relativa,
                    us_table.quota_abs,
                    us_table.ref_tm,
                    us_table.ref_ra,
                    us_table.ref_n,
                    us_table.posizione,
                    us_table.criteri_distinzione,
                    us_table.modo_formazione,
                    us_table.componenti_organici,
                    us_table.componenti_inorganici,
                    us_table.lunghezza_max,
                    us_table.altezza_max,
                    us_table.altezza_min,
                    us_table.profondita_max,
                    us_table.profondita_min,
                    us_table.larghezza_media,
                    us_table.quota_max,
                    us_table.quota_min,
                    us_table.piante,
                    us_table.documentazione,
                    us_table.scavato,
                    us_table.cont_per,
                    us_table.order_layer,
                    us_table.rapporti2,
                    us_table.sing_doc,
                    us_table.unita_edilizie,
                    us_table.quantificazioni,
                    us_table.doc_usv,
                    us_table.datazione
                FROM pyunitastratigrafiche
                JOIN us_table ON 
                    pyunitastratigrafiche.scavo_s = us_table.sito AND 
                    pyunitastratigrafiche.area_s = us_table.area AND 
                    pyunitastratigrafiche.us_s = us_table.us
            '''),
            ('pyarchinit_quote', '''
                CREATE VIEW pyarchinit_quote AS
                SELECT 
                    sito,
                    area,  -- Mantieni come TEXT
                    us,    -- Mantieni come TEXT
                    unita_tipo,
                    quota_min,
                    quota_max,
                    cont_per,
                    order_layer,
                    datazione,
                    the_geom
                FROM us_table
                WHERE quota_min IS NOT NULL OR quota_max IS NOT NULL
            '''),
            ('pyarchinit_quote_usm', '''
                CREATE VIEW pyarchinit_quote_usm AS
                SELECT 
                    sito,
                    area,  -- Mantieni come TEXT
                    us,    -- Mantieni come TEXT
                    unita_tipo,
                    quota_min_usm,
                    quota_max_usm,
                    the_geom
                FROM us_table
                WHERE unita_tipo = 'USM' AND (quota_min_usm IS NOT NULL OR quota_max_usm IS NOT NULL)
            '''),
            ('pyunitastratigrafiche', '''
                CREATE VIEW pyunitastratigrafiche AS
                SELECT 
                    id_us,
                    sito,
                    area,  -- Mantieni come TEXT
                    us,    -- Mantieni come TEXT
                    d_stratigrafica,
                    d_interpretativa,
                    descrizione,
                    interpretazione,
                    periodo_iniziale,
                    fase_iniziale,
                    periodo_finale,
                    fase_finale,
                    scavato,
                    attivita,
                    anno_scavo,
                    metodo_di_scavo,
                    inclusi,
                    campioni,
                    rapporti,
                    organici,
                    inorganici,
                    data_schedatura,
                    schedatore,
                    formazione,
                    stato_di_conservazione,
                    colore,
                    consistenza,
                    struttura,
                    cont_per,
                    order_layer,
                    the_geom
                FROM us_table
                WHERE unita_tipo = 'US'
            '''),
            ('pyunitastratigrafiche_usm', '''
                CREATE VIEW pyunitastratigrafiche_usm AS
                SELECT 
                    id_us,
                    sito,
                    area,  -- Mantieni come TEXT
                    us,    -- Mantieni come TEXT
                    unita_tipo,
                    d_stratigrafica,
                    d_interpretativa,
                    descrizione,
                    interpretazione,
                    periodo_iniziale,
                    fase_iniziale,
                    periodo_finale,
                    fase_finale,
                    scavato,
                    attivita,
                    anno_scavo,
                    metodo_di_scavo,
                    inclusi,
                    campioni,
                    rapporti,
                    organici,
                    inorganici,
                    data_schedatura,
                    schedatore,
                    formazione,
                    stato_di_conservazione,
                    colore,
                    consistenza,
                    struttura,
                    cont_per,
                    order_layer,
                    the_geom
                FROM us_table
                WHERE unita_tipo = 'USM'
            ''')
        ]
        
        for view_name, create_sql in views_to_fix:
            try:
                # Always drop and recreate views during update
                self.log_message(f"Dropping and recreating view {view_name}")
                self.cursor.execute(f"DROP VIEW IF EXISTS {view_name}")
                # Commit the drop to ensure it's completed
                self.conn.commit()
                
                self.cursor.execute(create_sql)
                # Commit the create to ensure it's saved
                self.conn.commit()
                
                self.updates_made.append(f"RECREATE VIEW {view_name}")
                self.log_message(f"View {view_name} ricreata con successo")
                
                # Verifica che la view sia stata creata correttamente
                if view_name == 'pyarchinit_us_view':
                    try:
                        # Prima verifica le tabelle sottostanti
                        self.cursor.execute("PRAGMA table_info(pyunitastratigrafiche)")
                        pyunit_cols = [col[1] for col in self.cursor.fetchall()]
                        self.log_message(f"Colonne in pyunitastratigrafiche: {', '.join(pyunit_cols[:5])}...")
                        
                        self.cursor.execute("PRAGMA table_info(us_table)")
                        us_cols = [col[1] for col in self.cursor.fetchall()]
                        has_order_layer = 'order_layer' in us_cols
                        has_cont_per = 'cont_per' in us_cols
                        self.log_message(f"us_table ha order_layer: {has_order_layer}, cont_per: {has_cont_per}")
                        
                        # Prova a fare select dalla view
                        self.cursor.execute("SELECT order_layer, cont_per FROM pyarchinit_us_view LIMIT 1")
                        self.log_message("Verifica: pyarchinit_us_view contiene order_layer e cont_per")
                    except Exception as verify_error:
                        self.log_message(f"ATTENZIONE: Verifica fallita per {view_name}: {verify_error}")
                        
            except Exception as e:
                self.log_message(f"Error fixing view {view_name}: {e}", Qgis.Warning if QGIS_AVAILABLE else None)
    
    def fix_field_types_in_base_tables(self):
        """Corregge i tipi di campo nelle tabelle base prima di ricreare le view"""
        # Fix tomba_table area field if it's INTEGER
        if self.table_exists('tomba_table'):
            self.cursor.execute("PRAGMA table_info(tomba_table)")
            columns = self.cursor.fetchall()
            for col in columns:
                if col[1] == 'area' and col[2] != 'TEXT':
                    self.log_message("Correzione campo area in tomba_table da INTEGER a TEXT...")
                    try:
                        # Crea nuova tabella con struttura corretta
                        self.cursor.execute("ALTER TABLE tomba_table RENAME TO tomba_table_old")
                        
                        # Ricrea la tabella con area come TEXT
                        create_sql = self._get_create_table_sql('tomba_table_old').replace('area INTEGER', 'area TEXT').replace('area INT', 'area TEXT')
                        if create_sql:
                            self.cursor.execute(create_sql.replace('tomba_table_old', 'tomba_table'))
                            
                            # Copia i dati
                            cols = [c[1] for c in columns]
                            self.cursor.execute(f"INSERT INTO tomba_table ({','.join(cols)}) SELECT {','.join(cols)} FROM tomba_table_old")
                            
                            # Elimina tabella vecchia
                            self.cursor.execute("DROP TABLE tomba_table_old")
                            self.updates_made.append("FIX tomba_table.area to TEXT")
                    except Exception as e:
                        self.log_message(f"Errore correggendo tomba_table: {e}")
                        # Ripristina se fallisce
                        try:
                            self.cursor.execute("DROP TABLE IF EXISTS tomba_table")
                            self.cursor.execute("ALTER TABLE tomba_table_old RENAME TO tomba_table")
                        except:
                            pass
    
    def _get_create_table_sql(self, table_name):
        """Ottiene l'SQL CREATE TABLE da una tabella esistente"""
        self.cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        result = self.cursor.fetchone()
        return result[0] if result else None
    
    def table_exists(self, table_name):
        """Check if a table exists"""
        self.cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=?
        """, (table_name,))
        return self.cursor.fetchone() is not None
    
    def add_column_if_missing(self, table_name, column_name, column_type):
        """Add column to table if it doesn't exist"""
        # Check if column exists
        self.cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [column[1] for column in self.cursor.fetchall()]
        
        if column_name not in columns:
            try:
                self.cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
                self.log_message(f"Aggiunta colonna {table_name}.{column_name}")
                self.updates_made.append(f"{table_name}.{column_name}")
            except Exception as e:
                self.log_message(f"Errore aggiungendo colonna {table_name}.{column_name}: {e}", Qgis.Warning if QGIS_AVAILABLE else None)
    
    def _recreate_reperti_view(self):
        """Ricrea la view pyarchinit_reperti_view con il campo quota"""
        try:
            # Drop existing view if any
            self.cursor.execute("DROP VIEW IF EXISTS pyarchinit_reperti_view")
            
            # Create view with all fields including quota
            self.cursor.execute("""
                CREATE VIEW pyarchinit_reperti_view AS 
                SELECT
                    a.gid,
                    a.the_geom,
                    a.id_rep,
                    a.siti,
                    a.quota,
                    b.id_invmat,
                    b.sito,
                    b.numero_inventario,
                    b.tipo_reperto,
                    b.criterio_schedatura,
                    b.definizione,
                    b.descrizione,
                    b.area,
                    b.us,
                    b.lavato,
                    b.nr_cassa,
                    b.luogo_conservazione,
                    b.stato_conservazione,
                    b.datazione_reperto,
                    b.elementi_reperto,
                    b.misurazioni,
                    b.rif_biblio,
                    b.tecnologie,
                    b.forme_minime,
                    b.forme_massime,
                    b.totale_frammenti,
                    b.corpo_ceramico,
                    b.rivestimento,
                    b.diametro_orlo,
                    b.peso,
                    b.tipo,
                    b.eve_orlo,
                    b.repertato,
                    b.diagnostico,
                    b.n_reperto,
                    b.tipo_contenitore,
                    b.struttura,
                    b.years
                FROM pyarchinit_reperti a
                JOIN inventario_materiali_table b ON 
                    a.siti = b.sito AND 
                    a.id_rep = b.numero_inventario
            """)
            self.log_message("Ricreata view pyarchinit_reperti_view con campo quota")
            self.updates_made.append("pyarchinit_reperti_view")
        except Exception as e:
            self.log_message(f"Errore ricreando pyarchinit_reperti_view: {e}", Qgis.Warning if QGIS_AVAILABLE else None)

    def update_pottery_thesaurus(self):
        """Installa/aggiorna le voci thesaurus per la tabella Pottery"""
        try:
            # Check if new decoration thesaurus entries exist (11.14, 11.15, 11.16)
            self.cursor.execute("""
                SELECT COUNT(*) FROM pyarchinit_thesaurus_sigle
                WHERE nome_tabella = 'Pottery' AND tipologia_sigla IN ('11.14', '11.15', '11.16')
            """)
            new_decoration_count = self.cursor.fetchone()[0]

            if new_decoration_count >= 30:  # Expected ~31 entries for decoration fields
                self.log_message(f"Voci thesaurus Pottery decorazione già presenti ({new_decoration_count} voci)")
                return

            # Path to pottery thesaurus SQL file (SQLite version)
            thesaurus_file = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir,
                                          'sql', 'pottery_thesaurus_sqlite.sql')

            if not os.path.exists(thesaurus_file):
                self.log_message(f"File thesaurus pottery non trovato: {thesaurus_file}")
                return

            # Read and execute the thesaurus SQL
            with open(thesaurus_file, 'r', encoding='utf-8') as f:
                thesaurus_sql = f.read()

            # Execute the SQL script - split by semicolons
            statements = thesaurus_sql.split(';')
            inserted_count = 0
            for stmt in statements:
                stmt = stmt.strip()
                if stmt and not stmt.startswith('--') and 'INSERT' in stmt.upper():
                    try:
                        self.cursor.execute(stmt)
                        inserted_count += 1
                    except Exception as stmt_error:
                        # Skip errors for duplicate entries
                        if 'unique constraint' not in str(stmt_error).lower():
                            self.log_message(f"Warning inserendo voce thesaurus: {str(stmt_error)[:100]}")

            if inserted_count > 0:
                self.log_message(f"Voci thesaurus Pottery installate ({inserted_count} voci)")
                self.updates_made.append("pottery_thesaurus")

        except Exception as e:
            self.log_message(f"Errore installando voci thesaurus Pottery: {e}", Qgis.Warning if QGIS_AVAILABLE else None)

    def add_concurrency_columns(self):
        """Aggiunge le colonne di concurrency per la sincronizzazione con PostgreSQL (v5.0+)"""
        # Tabelle che necessitano delle colonne di concurrency
        tables_with_full_concurrency = [
            'site_table', 'us_table', 'inventario_materiali_table',
            'periodizzazione_table', 'tomba_table', 'struttura_table',
            'pottery_table', 'pyarchinit_thesaurus_sigle'
        ]

        tables_with_basic_concurrency = [
            'campioni_table', 'individui_table', 'documentazione_table',
            'archeozoology_table', 'tafonomia_table'
        ]

        # Colonne complete di concurrency
        full_concurrency_cols = [
            ('version_number', 'INTEGER DEFAULT 1'),
            ('editing_by', 'TEXT'),
            ('editing_since', 'TEXT'),
            ('last_modified_by', 'TEXT'),
            ('last_modified_timestamp', 'TEXT'),
            ('audit_trail', 'TEXT')
        ]

        # Colonne base di concurrency
        basic_concurrency_cols = [
            ('version_number', 'INTEGER DEFAULT 1'),
            ('editing_by', 'TEXT'),
            ('editing_since', 'TEXT'),
            ('audit_trail', 'TEXT')
        ]

        # Aggiungi colonne complete
        for table in tables_with_full_concurrency:
            if self.table_exists(table):
                for col_name, col_type in full_concurrency_cols:
                    self.add_column_if_missing(table, col_name, col_type)

        # Aggiungi colonne base
        for table in tables_with_basic_concurrency:
            if self.table_exists(table):
                for col_name, col_type in basic_concurrency_cols:
                    self.add_column_if_missing(table, col_name, col_type)

        # us_table ha anche colonne funzionali extra
        if self.table_exists('us_table'):
            self.add_column_if_missing('us_table', 'quantificazioni', 'TEXT')
            self.add_column_if_missing('us_table', 'sing_doc', 'TEXT')
            self.add_column_if_missing('us_table', 'unita_edilizie', 'TEXT')

        # inventario_materiali_table ha colonne extra
        if self.table_exists('inventario_materiali_table'):
            self.add_column_if_missing('inventario_materiali_table', 'quota_usm', 'REAL')
            self.add_column_if_missing('inventario_materiali_table', 'unita_misura_quota', 'TEXT')

        # pottery_table ha colonne extra
        if self.table_exists('pottery_table'):
            self.add_column_if_missing('pottery_table', 'datazione', 'TEXT')

    def create_missing_tables(self):
        """Crea tabelle mancanti per compatibilità con PostgreSQL (v5.0+)"""

        # pyarchinit_access_log
        if not self.table_exists('pyarchinit_access_log'):
            self.cursor.execute('''
                CREATE TABLE pyarchinit_access_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    username TEXT,
                    action TEXT,
                    table_accessed TEXT,
                    operation TEXT,
                    record_id INTEGER,
                    ip_address TEXT,
                    timestamp TEXT,
                    success INTEGER,
                    error_message TEXT
                )
            ''')
            self.log_message("Creata tabella pyarchinit_access_log")
            self.updates_made.append("CREATE TABLE pyarchinit_access_log")

        # pyarchinit_audit_log
        if not self.table_exists('pyarchinit_audit_log'):
            self.cursor.execute('''
                CREATE TABLE pyarchinit_audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    table_name TEXT NOT NULL,
                    record_id INTEGER,
                    operation TEXT NOT NULL,
                    user_name TEXT,
                    timestamp TEXT,
                    old_data TEXT,
                    new_data TEXT,
                    changes TEXT
                )
            ''')
            self.log_message("Creata tabella pyarchinit_audit_log")
            self.updates_made.append("CREATE TABLE pyarchinit_audit_log")

        # pyarchinit_sync_lock
        if not self.table_exists('pyarchinit_sync_lock'):
            self.cursor.execute('''
                CREATE TABLE pyarchinit_sync_lock (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    table_name TEXT NOT NULL,
                    record_id INTEGER NOT NULL,
                    locked_by TEXT NOT NULL,
                    locked_at TEXT NOT NULL,
                    lock_type TEXT DEFAULT 'edit',
                    expires_at TEXT
                )
            ''')
            self.log_message("Creata tabella pyarchinit_sync_lock")
            self.updates_made.append("CREATE TABLE pyarchinit_sync_lock")

        # pyarchinit_users
        if not self.table_exists('pyarchinit_users'):
            self.cursor.execute('''
                CREATE TABLE pyarchinit_users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    full_name TEXT,
                    email TEXT,
                    role_id INTEGER,
                    is_active INTEGER DEFAULT 1,
                    created_at TEXT,
                    last_login TEXT,
                    default_site TEXT
                )
            ''')
            self.log_message("Creata tabella pyarchinit_users")
            self.updates_made.append("CREATE TABLE pyarchinit_users")

        # pyarchinit_roles
        if not self.table_exists('pyarchinit_roles'):
            self.cursor.execute('''
                CREATE TABLE pyarchinit_roles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role_name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    default_can_insert INTEGER DEFAULT 1,
                    default_can_update INTEGER DEFAULT 1,
                    default_can_delete INTEGER DEFAULT 0,
                    default_can_view INTEGER DEFAULT 1,
                    is_system_role INTEGER DEFAULT 0
                )
            ''')
            self.log_message("Creata tabella pyarchinit_roles")
            self.updates_made.append("CREATE TABLE pyarchinit_roles")

        # pyarchinit_permissions
        if not self.table_exists('pyarchinit_permissions'):
            self.cursor.execute('''
                CREATE TABLE pyarchinit_permissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    table_name TEXT NOT NULL,
                    can_insert INTEGER DEFAULT 1,
                    can_update INTEGER DEFAULT 1,
                    can_delete INTEGER DEFAULT 0,
                    can_view INTEGER DEFAULT 1,
                    site_filter TEXT,
                    area_filter TEXT,
                    created_at TEXT,
                    created_by TEXT
                )
            ''')
            self.log_message("Creata tabella pyarchinit_permissions")
            self.updates_made.append("CREATE TABLE pyarchinit_permissions")

        # media_to_us_table
        if not self.table_exists('media_to_us_table'):
            self.cursor.execute('''
                CREATE TABLE media_to_us_table (
                    id_mediaToUs INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_us INTEGER,
                    sito TEXT,
                    area TEXT,
                    us INTEGER,
                    id_media INTEGER,
                    filepath TEXT
                )
            ''')
            self.log_message("Creata tabella media_to_us_table")
            self.updates_made.append("CREATE TABLE media_to_us_table")

        # tma_materiali_archeologici
        if not self.table_exists('tma_materiali_archeologici'):
            self.cursor.execute('''
                CREATE TABLE tma_materiali_archeologici (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sito TEXT,
                    area TEXT,
                    localita TEXT,
                    settore TEXT,
                    inventario TEXT,
                    ogtm TEXT,
                    ldct TEXT,
                    ldcn TEXT,
                    vecchia_collocazione TEXT,
                    cassetta TEXT,
                    scan TEXT,
                    saggio TEXT,
                    vano_locus TEXT,
                    dscd TEXT,
                    dscu TEXT,
                    rcgd TEXT,
                    rcgz TEXT,
                    aint TEXT,
                    aind TEXT,
                    dtzg TEXT,
                    deso TEXT,
                    nsc TEXT,
                    ftap TEXT,
                    ftan TEXT,
                    drat TEXT,
                    dran TEXT,
                    draa TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    created_by TEXT,
                    updated_by TEXT,
                    version_number INTEGER DEFAULT 1,
                    editing_by TEXT,
                    editing_since TEXT,
                    last_modified_by TEXT,
                    last_modified_timestamp TEXT,
                    audit_trail TEXT
                )
            ''')
            self.log_message("Creata tabella tma_materiali_archeologici")
            self.updates_made.append("CREATE TABLE tma_materiali_archeologici")

        # tma_materiali_ripetibili
        if not self.table_exists('tma_materiali_ripetibili'):
            self.cursor.execute('''
                CREATE TABLE tma_materiali_ripetibili (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_tma INTEGER NOT NULL,
                    madi TEXT,
                    macc TEXT,
                    macl TEXT,
                    macp TEXT,
                    macd TEXT,
                    cronologia_mac TEXT,
                    macq TEXT,
                    peso REAL,
                    created_at TEXT,
                    updated_at TEXT,
                    created_by TEXT,
                    updated_by TEXT,
                    version_number INTEGER DEFAULT 1,
                    editing_by TEXT,
                    editing_since TEXT,
                    last_modified_by TEXT,
                    last_modified_timestamp TEXT
                )
            ''')
            self.log_message("Creata tabella tma_materiali_ripetibili")
            self.updates_made.append("CREATE TABLE tma_materiali_ripetibili")

        # pyarchinit_ripartizioni_temporali
        if not self.table_exists('pyarchinit_ripartizioni_temporali'):
            self.cursor.execute('''
                CREATE TABLE pyarchinit_ripartizioni_temporali (
                    id_periodo INTEGER PRIMARY KEY AUTOINCREMENT,
                    sito TEXT,
                    sigla_periodo TEXT,
                    sigla_fase TEXT,
                    cronologia_numerica INTEGER,
                    cronologia_numerica_finale INTEGER,
                    datazione_estesa_stringa TEXT,
                    descrizione TEXT
                )
            ''')
            self.log_message("Creata tabella pyarchinit_ripartizioni_temporali")
            self.updates_made.append("CREATE TABLE pyarchinit_ripartizioni_temporali")

    def create_performance_indexes(self):
        """Crea indici di performance per query frequenti"""
        self.log_message("Creazione indici di performance...")

        # Lista degli indici da creare con formato: (nome_indice, tabella, colonne)
        indexes = [
            # Indici principali per ricerche per sito
            ('idx_us_table_sito', 'us_table', 'sito'),
            ('idx_inventario_sito', 'inventario_materiali_table', 'sito'),
            ('idx_site_table_sito', 'site_table', 'sito'),
            ('idx_thesaurus_tipologia', 'pyarchinit_thesaurus_sigle', 'tipologia_sigla'),
            ('idx_quote_sito', 'pyarchinit_quote', 'sito_q, area_q, us_q'),
            ('idx_reperti_siti', 'pyarchinit_reperti', 'siti'),

            # Indici aggiuntivi per query comuni
            ('idx_us_table_area', 'us_table', 'area'),
            ('idx_us_table_sito_area', 'us_table', 'sito, area'),
            ('idx_inventario_area', 'inventario_materiali_table', 'area'),
            ('idx_tomba_sito', 'tomba_table', 'sito'),
            ('idx_periodizzazione_sito', 'periodizzazione_table', 'sito'),
            ('idx_struttura_sito', 'struttura_table', 'sito'),
            ('idx_documentazione_sito', 'documentazione_table', 'sito'),
            ('idx_campioni_sito', 'campioni_table', 'sito'),
        ]

        indexes_created = 0

        for idx_name, table_name, columns in indexes:
            try:
                # Verifica se la tabella esiste
                if not self.table_exists(table_name):
                    continue

                # SQLite supporta CREATE INDEX IF NOT EXISTS
                self.cursor.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table_name}({columns})")
                indexes_created += 1

            except Exception as e:
                # Ignora errori per singoli indici (es. colonna non esiste)
                pass

        if indexes_created > 0:
            self.log_message(f"Creati/verificati {indexes_created} indici di performance")

            # Esegui ANALYZE per aggiornare le statistiche
            try:
                self.cursor.execute("ANALYZE")
            except:
                pass


def check_and_update_sqlite_db(db_path, parent=None):
    """Funzione helper per verificare e aggiornare un database SQLite"""
    if not db_path.endswith('.sqlite'):
        return True
    
    updater = SQLiteDBUpdater(db_path, parent)
    return updater.check_and_update_database()