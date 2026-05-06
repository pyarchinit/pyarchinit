#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SQLite Database Updater Module
Aggiorna automaticamente database SQLite vecchi quando vengono aperti
"""

import sqlite3
import os
import re
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
        print(f"DEBUG [sqlite_db_updater]: check_and_update_database() chiamato")  # DEBUG
        try:
            # SEMPRE controlla se ci sono tabelle da ripristinare dai backup
            self._check_and_restore_backup_tables()

            # Check if database needs update
            needs_upd = self.needs_update()
            print(f"DEBUG [sqlite_db_updater]: needs_update() = {needs_upd}")  # DEBUG
            if needs_upd:
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

            # Check if inventario_materiali_table has the sub_inv suffix column
            # (older DBs predate this column; the entity expects it).
            self.cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='inventario_materiali_table'
            """)
            if self.cursor.fetchone():
                self.cursor.execute("PRAGMA table_info(inventario_materiali_table)")
                columns = [column[1] for column in self.cursor.fetchall()]
                if 'sub_inv' not in columns:
                    print("DEBUG [sqlite_db_updater]: inventario_materiali_table manca sub_inv, needs_update=True")
                    return True

            # Check if ut_table has analysis fields (v4.9.67+)
            self.cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='ut_table'
            """)
            if self.cursor.fetchone():
                self.cursor.execute("PRAGMA table_info(ut_table)")
                columns = [column[1] for column in self.cursor.fetchall()]
                required_ut_columns = ['potential_score', 'risk_score', 'potential_factors',
                                       'risk_factors', 'analysis_date', 'analysis_method']
                for col in required_ut_columns:
                    if col not in columns:
                        print(f"DEBUG [sqlite_db_updater]: ut_table manca colonna {col}, needs_update=True")  # DEBUG
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
            
            # Check if required tables exist (v5.0.5+)
            site_mgmt_tables = [
                'inventario_lapidei_table',
                'personale_table', 'presenze_table', 'attrezzature_table',
                'budget_table', 'computo_metrico_table'
            ]
            for tbl in site_mgmt_tables:
                self.cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                    (tbl,))
                if not self.cursor.fetchone():
                    self.log_message(f"Tabella mancante: {tbl}")
                    return True

            # Detect string columns that older DBs created as INT/INTEGER but
            # the canonical template (resources/dbfiles/pyarchinit.sqlite)
            # defines as TEXT. The migration coerces them in
            # fix_field_types_in_base_tables; we only need to surface the
            # mismatch here so the migration actually fires.
            columns_must_be_text = [
                ('us_table', 'us'),
                ('inventario_materiali_table', 'area'),
                ('inventario_materiali_table', 'us'),
                ('campioni_table', 'us'),
                ('pyarchinit_quote', 'area_q'),
                ('pyarchinit_quote', 'us_q'),
                ('pyarchinit_quote_usm', 'area_q'),
                ('pyarchinit_quote_usm', 'us_q'),
            ]
            for tbl, col in columns_must_be_text:
                self.cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                    (tbl,))
                if not self.cursor.fetchone():
                    continue
                self.cursor.execute(f"PRAGMA table_info({tbl})")
                for column in self.cursor.fetchall():
                    if column[1] != col:
                        continue
                    declared = (column[2] or '').upper().strip()
                    if declared not in ('TEXT', 'VARCHAR', 'CHAR') and declared:
                        self.log_message(
                            f"Tipo errato {tbl}.{col}={column[2]!r} "
                            f"(atteso TEXT)")
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
            self.update_site_management_thesaurus()
            self.fix_thesaurus_nome_tabella()
            self.update_other_tables()
            self.update_struttura_table()

            # Add concurrency columns for sync with PostgreSQL (v5.0+)
            self.add_concurrency_columns()

            # Create missing tables for sync compatibility
            self.create_missing_tables()

            # Create inventario_lapidei_table if missing (referenced by concurrency SQL)
            self.update_inventario_lapidei_table()

            # Create site management tables (personale, presenze, attrezzature, budget, computo_metrico)
            self.update_personale_table()
            self.update_presenze_table()
            self.update_attrezzature_table()
            self.update_budget_table()
            self.update_computo_metrico_table()

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
        print("DEBUG [sqlite_db_updater]: update_ut_table() chiamato")  # DEBUG
        if self.table_exists('ut_table'):
            print("DEBUG [sqlite_db_updater]: ut_table esiste, aggiungo colonne...")  # DEBUG
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
                ('ut_table', 'intensive', 'مسح مكثف', 'مسح ميداني منهجي مكثف', '12.1', 'ar_LB'),
                ('ut_table', 'extensive', 'مسح موسع', 'مسح استطلاعي موسع', '12.1', 'ar_LB'),
                ('ut_table', 'targeted', 'مسح موجه', 'تحقيق موجه لمناطق محددة', '12.1', 'ar_LB'),
                ('ut_table', 'random', 'عينة عشوائية', 'منهجية أخذ العينات العشوائية', '12.1', 'ar_LB'),
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
                ('ut_table', 'none', 'لا نباتات', 'أرض جرداء بدون نباتات', '12.2', 'ar_LB'),
                ('ut_table', 'sparse', 'نباتات متناثرة', 'تغطية نباتية أقل من 25%', '12.2', 'ar_LB'),
                ('ut_table', 'moderate', 'نباتات معتدلة', 'تغطية نباتية بين 25% و50%', '12.2', 'ar_LB'),
                ('ut_table', 'dense', 'نباتات كثيفة', 'تغطية نباتية بين 50% و75%', '12.2', 'ar_LB'),
                ('ut_table', 'very_dense', 'نباتات كثيفة جداً', 'تغطية نباتية أكثر من 75%', '12.2', 'ar_LB'),
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
                ('ut_table', 'handheld', 'GPS محمول', 'جهاز GPS محمول باليد', '12.3', 'ar_LB'),
                ('ut_table', 'dgps', 'GPS تفاضلي', 'DGPS مع تصحيح محطة القاعدة', '12.3', 'ar_LB'),
                ('ut_table', 'rtk', 'GPS RTK', 'GPS حركي في الوقت الحقيقي', '12.3', 'ar_LB'),
                ('ut_table', 'total_station', 'محطة كاملة', 'مسح بالمحطة الكاملة', '12.3', 'ar_LB'),
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
                ('ut_table', 'ploughed', 'محروث', 'حقل محروث حديثاً', '12.4', 'ar_LB'),
                ('ut_table', 'stubble', 'قش', 'وجود بقايا المحاصيل', '12.4', 'ar_LB'),
                ('ut_table', 'pasture', 'مرعى', 'أرض عشبية/مرعى', '12.4', 'ar_LB'),
                ('ut_table', 'woodland', 'غابة', 'منطقة حرجية', '12.4', 'ar_LB'),
                ('ut_table', 'urban', 'حضري', 'منطقة حضرية/مبنية', '12.4', 'ar_LB'),
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
                ('ut_table', 'easy', 'وصول سهل', 'لا قيود على الوصول', '12.5', 'ar_LB'),
                ('ut_table', 'moderate_access', 'وصول معتدل', 'بعض القيود أو الصعوبات', '12.5', 'ar_LB'),
                ('ut_table', 'difficult', 'وصول صعب', 'مشاكل وصول كبيرة', '12.5', 'ar_LB'),
                ('ut_table', 'restricted', 'وصول مقيد', 'الوصول بإذن فقط', '12.5', 'ar_LB'),
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
                ('ut_table', 'sunny', 'مشمس', 'طقس صافٍ ومشمس', '12.6', 'ar_LB'),
                ('ut_table', 'cloudy', 'غائم', 'ظروف غائمة', '12.6', 'ar_LB'),
                ('ut_table', 'rainy', 'ممطر', 'أمطار أثناء المسح', '12.6', 'ar_LB'),
                ('ut_table', 'windy', 'عاصف', 'رياح قوية', '12.6', 'ar_LB'),
                # Catalan
                ('ut_table', 'sunny', 'Assolellat', 'Temps clar i assolellat', '12.6', 'ca_ES'),
                ('ut_table', 'cloudy', 'Ennuvolat', 'Condicions ennuvolades', '12.6', 'ca_ES'),
                ('ut_table', 'rainy', 'Plujós', 'Pluja durant la prospecció', '12.6', 'ca_ES'),
                ('ut_table', 'windy', 'Ventós', 'Vents forts', '12.6', 'ca_ES'),

                # ========== 12.7 - UT Definition (Definizione UT) ==========
                # Italian
                ('ut_table', 'scatter', 'Area di dispersione materiali', 'Concentrazione diffusa di materiali archeologici', '12.7', 'IT'),
                ('ut_table', 'site', 'Sito archeologico', 'Area con evidenze strutturali o concentrazione significativa', '12.7', 'IT'),
                ('ut_table', 'anomaly', 'Anomalia del terreno', 'Anomalia morfologica potenzialmente archeologica', '12.7', 'IT'),
                ('ut_table', 'structure', 'Struttura affiorante', 'Resti di strutture visibili in superficie', '12.7', 'IT'),
                ('ut_table', 'concentration', 'Concentrazione reperti', 'Alta densità di materiali in area circoscritta', '12.7', 'IT'),
                ('ut_table', 'traces', 'Tracce antropiche', 'Evidenze di attività umana antica', '12.7', 'IT'),
                ('ut_table', 'findspot', 'Rinvenimento sporadico', 'Materiale isolato senza contesto', '12.7', 'IT'),
                ('ut_table', 'negative', 'Esito negativo', 'Area priva di evidenze archeologiche', '12.7', 'IT'),
                # English
                ('ut_table', 'scatter', 'Material scatter', 'Diffuse concentration of archaeological materials', '12.7', 'en_US'),
                ('ut_table', 'site', 'Archaeological site', 'Area with structural evidence or significant concentration', '12.7', 'en_US'),
                ('ut_table', 'anomaly', 'Terrain anomaly', 'Morphological anomaly potentially archaeological', '12.7', 'en_US'),
                ('ut_table', 'structure', 'Outcropping structure', 'Visible structural remains on surface', '12.7', 'en_US'),
                ('ut_table', 'concentration', 'Finds concentration', 'High density of materials in defined area', '12.7', 'en_US'),
                ('ut_table', 'traces', 'Anthropic traces', 'Evidence of ancient human activity', '12.7', 'en_US'),
                ('ut_table', 'findspot', 'Sporadic find', 'Isolated material without context', '12.7', 'en_US'),
                ('ut_table', 'negative', 'Negative result', 'Area without archaeological evidence', '12.7', 'en_US'),
                # German
                ('ut_table', 'scatter', 'Fundstreuung', 'Diffuse Konzentration archäologischer Materialien', '12.7', 'de_DE'),
                ('ut_table', 'site', 'Archäologische Fundstelle', 'Bereich mit Strukturnachweisen oder signifikanter Konzentration', '12.7', 'de_DE'),
                ('ut_table', 'anomaly', 'Geländeanomalie', 'Möglicherweise archäologische morphologische Anomalie', '12.7', 'de_DE'),
                ('ut_table', 'structure', 'Sichtbare Struktur', 'Auf der Oberfläche sichtbare Strukturreste', '12.7', 'de_DE'),
                ('ut_table', 'concentration', 'Fundkonzentration', 'Hohe Funddichte in begrenztem Bereich', '12.7', 'de_DE'),
                ('ut_table', 'traces', 'Anthropogene Spuren', 'Nachweise alter menschlicher Aktivität', '12.7', 'de_DE'),
                ('ut_table', 'findspot', 'Einzelfund', 'Isoliertes Material ohne Kontext', '12.7', 'de_DE'),
                ('ut_table', 'negative', 'Negativer Befund', 'Bereich ohne archäologische Nachweise', '12.7', 'de_DE'),
                # Spanish
                ('ut_table', 'scatter', 'Dispersión de materiales', 'Concentración difusa de materiales arqueológicos', '12.7', 'es_ES'),
                ('ut_table', 'site', 'Yacimiento arqueológico', 'Área con evidencias estructurales o concentración significativa', '12.7', 'es_ES'),
                ('ut_table', 'anomaly', 'Anomalía del terreno', 'Anomalía morfológica potencialmente arqueológica', '12.7', 'es_ES'),
                ('ut_table', 'structure', 'Estructura aflorante', 'Restos de estructuras visibles en superficie', '12.7', 'es_ES'),
                ('ut_table', 'concentration', 'Concentración de hallazgos', 'Alta densidad de materiales en área definida', '12.7', 'es_ES'),
                ('ut_table', 'traces', 'Trazas antrópicas', 'Evidencias de actividad humana antigua', '12.7', 'es_ES'),
                ('ut_table', 'findspot', 'Hallazgo esporádico', 'Material aislado sin contexto', '12.7', 'es_ES'),
                ('ut_table', 'negative', 'Resultado negativo', 'Área sin evidencias arqueológicas', '12.7', 'es_ES'),
                # French
                ('ut_table', 'scatter', 'Épandage de matériel', 'Concentration diffuse de matériaux archéologiques', '12.7', 'fr_FR'),
                ('ut_table', 'site', 'Site archéologique', 'Zone avec preuves structurelles ou concentration significative', '12.7', 'fr_FR'),
                ('ut_table', 'anomaly', 'Anomalie de terrain', 'Anomalie morphologique potentiellement archéologique', '12.7', 'fr_FR'),
                ('ut_table', 'structure', 'Structure affleurante', 'Restes de structures visibles en surface', '12.7', 'fr_FR'),
                ('ut_table', 'concentration', 'Concentration de mobilier', 'Haute densité de matériaux dans une zone définie', '12.7', 'fr_FR'),
                ('ut_table', 'traces', 'Traces anthropiques', 'Preuves d\'activité humaine ancienne', '12.7', 'fr_FR'),
                ('ut_table', 'findspot', 'Découverte isolée', 'Matériel isolé sans contexte', '12.7', 'fr_FR'),
                ('ut_table', 'negative', 'Résultat négatif', 'Zone sans preuves archéologiques', '12.7', 'fr_FR'),
                # Arabic
                ('ut_table', 'scatter', 'انتشار مواد', 'تركيز متفرق للمواد الأثرية', '12.7', 'ar_LB'),
                ('ut_table', 'site', 'موقع أثري', 'منطقة بها أدلة هيكلية أو تركيز كبير', '12.7', 'ar_LB'),
                ('ut_table', 'anomaly', 'شذوذ أرضي', 'شذوذ مورفولوجي محتمل أثرياً', '12.7', 'ar_LB'),
                ('ut_table', 'structure', 'هيكل بارز', 'بقايا هياكل مرئية على السطح', '12.7', 'ar_LB'),
                ('ut_table', 'concentration', 'تركيز لقى', 'كثافة عالية من المواد في منطقة محددة', '12.7', 'ar_LB'),
                ('ut_table', 'traces', 'آثار بشرية', 'دليل على نشاط بشري قديم', '12.7', 'ar_LB'),
                ('ut_table', 'findspot', 'اكتشاف متفرق', 'مادة معزولة بدون سياق', '12.7', 'ar_LB'),
                ('ut_table', 'negative', 'نتيجة سلبية', 'منطقة بدون أدلة أثرية', '12.7', 'ar_LB'),
                # Catalan
                ('ut_table', 'scatter', 'Dispersió de materials', 'Concentració difusa de materials arqueològics', '12.7', 'ca_ES'),
                ('ut_table', 'site', 'Jaciment arqueològic', 'Àrea amb evidències estructurals o concentració significativa', '12.7', 'ca_ES'),
                ('ut_table', 'anomaly', 'Anomalia del terreny', 'Anomalia morfològica potencialment arqueològica', '12.7', 'ca_ES'),
                ('ut_table', 'structure', 'Estructura aflorant', 'Restes d\'estructures visibles en superfície', '12.7', 'ca_ES'),
                ('ut_table', 'concentration', 'Concentració de troballes', 'Alta densitat de materials en àrea definida', '12.7', 'ca_ES'),
                ('ut_table', 'traces', 'Traces antròpiques', 'Evidències d\'activitat humana antiga', '12.7', 'ca_ES'),
                ('ut_table', 'findspot', 'Troballa esporàdica', 'Material aïllat sense context', '12.7', 'ca_ES'),
                ('ut_table', 'negative', 'Resultat negatiu', 'Àrea sense evidències arqueològiques', '12.7', 'ca_ES'),
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

    def update_site_management_thesaurus(self):
        """Seed thesaurus entries for site management (cantiere) tables.
        7 codes (14.1-14.7) × 10 languages = ~470 entries."""
        try:
            self.cursor.execute("""
                SELECT COUNT(*) FROM pyarchinit_thesaurus_sigle
                WHERE tipologia_sigla LIKE '14.%'
            """)
            existing_count = self.cursor.fetchone()[0]

            if existing_count >= 400:
                return

            self.log_message("Aggiunta voci thesaurus gestione cantiere (14.x)...")

            # (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
            entries = [
                # ── 14.1 ruolo (cantiere_personale_table) ──
                # IT
                ('cantiere_personale_table', 'direttore', 'Direttore', '', '14.1', 'IT'),
                ('cantiere_personale_table', 'responsabile_area', 'Responsabile area', '', '14.1', 'IT'),
                ('cantiere_personale_table', 'archeologo', 'Archeologo', '', '14.1', 'IT'),
                ('cantiere_personale_table', 'tecnico', 'Tecnico', '', '14.1', 'IT'),
                ('cantiere_personale_table', 'operaio', 'Operaio', '', '14.1', 'IT'),
                ('cantiere_personale_table', 'restauratore', 'Restauratore', '', '14.1', 'IT'),
                ('cantiere_personale_table', 'topografo', 'Topografo', '', '14.1', 'IT'),
                ('cantiere_personale_table', 'disegnatore', 'Disegnatore', '', '14.1', 'IT'),
                ('cantiere_personale_table', 'fotografo', 'Fotografo', '', '14.1', 'IT'),
                ('cantiere_personale_table', 'studente', 'Studente', '', '14.1', 'IT'),
                # EN
                ('cantiere_personale_table', 'director', 'Director', '', '14.1', 'en_US'),
                ('cantiere_personale_table', 'area_supervisor', 'Area Supervisor', '', '14.1', 'en_US'),
                ('cantiere_personale_table', 'archaeologist', 'Archaeologist', '', '14.1', 'en_US'),
                ('cantiere_personale_table', 'technician', 'Technician', '', '14.1', 'en_US'),
                ('cantiere_personale_table', 'worker', 'Worker', '', '14.1', 'en_US'),
                ('cantiere_personale_table', 'conservator', 'Conservator', '', '14.1', 'en_US'),
                ('cantiere_personale_table', 'surveyor', 'Surveyor', '', '14.1', 'en_US'),
                ('cantiere_personale_table', 'draftsperson', 'Draftsperson', '', '14.1', 'en_US'),
                ('cantiere_personale_table', 'photographer', 'Photographer', '', '14.1', 'en_US'),
                ('cantiere_personale_table', 'student', 'Student', '', '14.1', 'en_US'),
                # DE
                ('cantiere_personale_table', 'direktor', 'Direktor', '', '14.1', 'de_DE'),
                ('cantiere_personale_table', 'bereichsleiter', 'Bereichsleiter', '', '14.1', 'de_DE'),
                ('cantiere_personale_table', 'archaeologe', 'Archäologe', '', '14.1', 'de_DE'),
                ('cantiere_personale_table', 'techniker', 'Techniker', '', '14.1', 'de_DE'),
                ('cantiere_personale_table', 'arbeiter', 'Arbeiter', '', '14.1', 'de_DE'),
                ('cantiere_personale_table', 'restaurator', 'Restaurator', '', '14.1', 'de_DE'),
                ('cantiere_personale_table', 'vermesser', 'Vermesser', '', '14.1', 'de_DE'),
                ('cantiere_personale_table', 'zeichner', 'Zeichner', '', '14.1', 'de_DE'),
                ('cantiere_personale_table', 'fotograf', 'Fotograf', '', '14.1', 'de_DE'),
                ('cantiere_personale_table', 'student_de', 'Student', '', '14.1', 'de_DE'),
                # ES
                ('cantiere_personale_table', 'director_es', 'Director', '', '14.1', 'es_ES'),
                ('cantiere_personale_table', 'responsable_area', 'Responsable de área', '', '14.1', 'es_ES'),
                ('cantiere_personale_table', 'arqueologo', 'Arqueólogo', '', '14.1', 'es_ES'),
                ('cantiere_personale_table', 'tecnico_es', 'Técnico', '', '14.1', 'es_ES'),
                ('cantiere_personale_table', 'obrero', 'Obrero', '', '14.1', 'es_ES'),
                ('cantiere_personale_table', 'restaurador', 'Restaurador', '', '14.1', 'es_ES'),
                ('cantiere_personale_table', 'topografo_es', 'Topógrafo', '', '14.1', 'es_ES'),
                ('cantiere_personale_table', 'dibujante', 'Dibujante', '', '14.1', 'es_ES'),
                ('cantiere_personale_table', 'fotografo_es', 'Fotógrafo', '', '14.1', 'es_ES'),
                ('cantiere_personale_table', 'estudiante', 'Estudiante', '', '14.1', 'es_ES'),
                # FR
                ('cantiere_personale_table', 'directeur', 'Directeur', '', '14.1', 'fr_FR'),
                ('cantiere_personale_table', 'responsable_secteur', 'Responsable de secteur', '', '14.1', 'fr_FR'),
                ('cantiere_personale_table', 'archeologue', 'Archéologue', '', '14.1', 'fr_FR'),
                ('cantiere_personale_table', 'technicien', 'Technicien', '', '14.1', 'fr_FR'),
                ('cantiere_personale_table', 'ouvrier', 'Ouvrier', '', '14.1', 'fr_FR'),
                ('cantiere_personale_table', 'restaurateur', 'Restaurateur', '', '14.1', 'fr_FR'),
                ('cantiere_personale_table', 'geometre', 'Géomètre', '', '14.1', 'fr_FR'),
                ('cantiere_personale_table', 'dessinateur', 'Dessinateur', '', '14.1', 'fr_FR'),
                ('cantiere_personale_table', 'photographe', 'Photographe', '', '14.1', 'fr_FR'),
                ('cantiere_personale_table', 'etudiant', 'Étudiant', '', '14.1', 'fr_FR'),
                # AR
                ('cantiere_personale_table', 'mudir', 'مدير', '', '14.1', 'ar_AR'),
                ('cantiere_personale_table', 'masul_mantaqa', 'مسؤول منطقة', '', '14.1', 'ar_AR'),
                ('cantiere_personale_table', 'athari', 'عالم آثار', '', '14.1', 'ar_AR'),
                ('cantiere_personale_table', 'fanni', 'فني', '', '14.1', 'ar_AR'),
                ('cantiere_personale_table', 'amil', 'عامل', '', '14.1', 'ar_AR'),
                ('cantiere_personale_table', 'murammim', 'مرمم', '', '14.1', 'ar_AR'),
                ('cantiere_personale_table', 'massah', 'مساح', '', '14.1', 'ar_AR'),
                ('cantiere_personale_table', 'rassam', 'رسام', '', '14.1', 'ar_AR'),
                ('cantiere_personale_table', 'musawwir', 'مصور', '', '14.1', 'ar_AR'),
                ('cantiere_personale_table', 'talib', 'طالب', '', '14.1', 'ar_AR'),
                # CA
                ('cantiere_personale_table', 'director_ca', 'Director', '', '14.1', 'ca_ES'),
                ('cantiere_personale_table', 'responsable_area_ca', "Responsable d'àrea", '', '14.1', 'ca_ES'),
                ('cantiere_personale_table', 'arqueoleg', 'Arqueòleg', '', '14.1', 'ca_ES'),
                ('cantiere_personale_table', 'tecnic', 'Tècnic', '', '14.1', 'ca_ES'),
                ('cantiere_personale_table', 'obrer', 'Obrer', '', '14.1', 'ca_ES'),
                ('cantiere_personale_table', 'restaurador_ca', 'Restaurador', '', '14.1', 'ca_ES'),
                ('cantiere_personale_table', 'topograf', 'Topògraf', '', '14.1', 'ca_ES'),
                ('cantiere_personale_table', 'dibuixant', 'Dibuixant', '', '14.1', 'ca_ES'),
                ('cantiere_personale_table', 'fotograf_ca', 'Fotògraf', '', '14.1', 'ca_ES'),
                ('cantiere_personale_table', 'estudiant', 'Estudiant', '', '14.1', 'ca_ES'),
                # RO
                ('cantiere_personale_table', 'director_ro', 'Director', '', '14.1', 'ro_RO'),
                ('cantiere_personale_table', 'responsabil_zona', 'Responsabil zonă', '', '14.1', 'ro_RO'),
                ('cantiere_personale_table', 'arheolog', 'Arheolog', '', '14.1', 'ro_RO'),
                ('cantiere_personale_table', 'tehnician', 'Tehnician', '', '14.1', 'ro_RO'),
                ('cantiere_personale_table', 'muncitor', 'Muncitor', '', '14.1', 'ro_RO'),
                ('cantiere_personale_table', 'restaurator_ro', 'Restaurator', '', '14.1', 'ro_RO'),
                ('cantiere_personale_table', 'topograf_ro', 'Topograf', '', '14.1', 'ro_RO'),
                ('cantiere_personale_table', 'desenator', 'Desenator', '', '14.1', 'ro_RO'),
                ('cantiere_personale_table', 'fotograf_ro', 'Fotograf', '', '14.1', 'ro_RO'),
                ('cantiere_personale_table', 'student_ro', 'Student', '', '14.1', 'ro_RO'),
                # PT
                ('cantiere_personale_table', 'diretor', 'Diretor', '', '14.1', 'pt_PT'),
                ('cantiere_personale_table', 'responsavel_area', 'Responsável de área', '', '14.1', 'pt_PT'),
                ('cantiere_personale_table', 'arqueologo_pt', 'Arqueólogo', '', '14.1', 'pt_PT'),
                ('cantiere_personale_table', 'tecnico_pt', 'Técnico', '', '14.1', 'pt_PT'),
                ('cantiere_personale_table', 'operario', 'Operário', '', '14.1', 'pt_PT'),
                ('cantiere_personale_table', 'restaurador_pt', 'Restaurador', '', '14.1', 'pt_PT'),
                ('cantiere_personale_table', 'topografo_pt', 'Topógrafo', '', '14.1', 'pt_PT'),
                ('cantiere_personale_table', 'desenhador', 'Desenhador', '', '14.1', 'pt_PT'),
                ('cantiere_personale_table', 'fotografo_pt', 'Fotógrafo', '', '14.1', 'pt_PT'),
                ('cantiere_personale_table', 'estudante', 'Estudante', '', '14.1', 'pt_PT'),
                # EL
                ('cantiere_personale_table', 'diefthyntis', 'Διευθυντής', '', '14.1', 'el_GR'),
                ('cantiere_personale_table', 'ypefthynos_tomea', 'Υπεύθυνος τομέα', '', '14.1', 'el_GR'),
                ('cantiere_personale_table', 'archaiologos', 'Αρχαιολόγος', '', '14.1', 'el_GR'),
                ('cantiere_personale_table', 'technikos', 'Τεχνικός', '', '14.1', 'el_GR'),
                ('cantiere_personale_table', 'ergatis', 'Εργάτης', '', '14.1', 'el_GR'),
                ('cantiere_personale_table', 'syntiritis', 'Συντηρητής', '', '14.1', 'el_GR'),
                ('cantiere_personale_table', 'topografos', 'Τοπογράφος', '', '14.1', 'el_GR'),
                ('cantiere_personale_table', 'schediasitis', 'Σχεδιαστής', '', '14.1', 'el_GR'),
                ('cantiere_personale_table', 'fotografos', 'Φωτογράφος', '', '14.1', 'el_GR'),
                ('cantiere_personale_table', 'foititis', 'Φοιτητής', '', '14.1', 'el_GR'),

                # ── 14.2 tipo_contratto (cantiere_personale_table) ──
                # IT
                ('cantiere_personale_table', 'tempo_indeterminato', 'Tempo indeterminato', '', '14.2', 'IT'),
                ('cantiere_personale_table', 'tempo_determinato', 'Tempo determinato', '', '14.2', 'IT'),
                ('cantiere_personale_table', 'collaborazione', 'Collaborazione', '', '14.2', 'IT'),
                ('cantiere_personale_table', 'partita_iva', 'Partita IVA', '', '14.2', 'IT'),
                ('cantiere_personale_table', 'volontario', 'Volontario', '', '14.2', 'IT'),
                ('cantiere_personale_table', 'stage_tirocinio', 'Stage/Tirocinio', '', '14.2', 'IT'),
                # EN
                ('cantiere_personale_table', 'permanent', 'Permanent', '', '14.2', 'en_US'),
                ('cantiere_personale_table', 'fixed_term', 'Fixed-term', '', '14.2', 'en_US'),
                ('cantiere_personale_table', 'collaboration', 'Collaboration', '', '14.2', 'en_US'),
                ('cantiere_personale_table', 'freelance', 'Freelance', '', '14.2', 'en_US'),
                ('cantiere_personale_table', 'volunteer', 'Volunteer', '', '14.2', 'en_US'),
                ('cantiere_personale_table', 'internship', 'Internship', '', '14.2', 'en_US'),
                # DE
                ('cantiere_personale_table', 'unbefristet', 'Unbefristet', '', '14.2', 'de_DE'),
                ('cantiere_personale_table', 'befristet', 'Befristet', '', '14.2', 'de_DE'),
                ('cantiere_personale_table', 'zusammenarbeit', 'Zusammenarbeit', '', '14.2', 'de_DE'),
                ('cantiere_personale_table', 'freiberuflich', 'Freiberuflich', '', '14.2', 'de_DE'),
                ('cantiere_personale_table', 'ehrenamtlich', 'Ehrenamtlich', '', '14.2', 'de_DE'),
                ('cantiere_personale_table', 'praktikum', 'Praktikum', '', '14.2', 'de_DE'),
                # ES
                ('cantiere_personale_table', 'indefinido', 'Indefinido', '', '14.2', 'es_ES'),
                ('cantiere_personale_table', 'temporal', 'Temporal', '', '14.2', 'es_ES'),
                ('cantiere_personale_table', 'colaboracion', 'Colaboración', '', '14.2', 'es_ES'),
                ('cantiere_personale_table', 'autonomo', 'Autónomo', '', '14.2', 'es_ES'),
                ('cantiere_personale_table', 'voluntario_es', 'Voluntario', '', '14.2', 'es_ES'),
                ('cantiere_personale_table', 'practicas', 'Prácticas', '', '14.2', 'es_ES'),
                # FR
                ('cantiere_personale_table', 'cdi', 'CDI', '', '14.2', 'fr_FR'),
                ('cantiere_personale_table', 'cdd', 'CDD', '', '14.2', 'fr_FR'),
                ('cantiere_personale_table', 'collaboration_fr', 'Collaboration', '', '14.2', 'fr_FR'),
                ('cantiere_personale_table', 'independant', 'Indépendant', '', '14.2', 'fr_FR'),
                ('cantiere_personale_table', 'benevole', 'Bénévole', '', '14.2', 'fr_FR'),
                ('cantiere_personale_table', 'stage', 'Stage', '', '14.2', 'fr_FR'),
                # AR
                ('cantiere_personale_table', 'daaim', 'دائم', '', '14.2', 'ar_AR'),
                ('cantiere_personale_table', 'muaqqat', 'مؤقت', '', '14.2', 'ar_AR'),
                ('cantiere_personale_table', 'taawun', 'تعاون', '', '14.2', 'ar_AR'),
                ('cantiere_personale_table', 'amal_hurr', 'عمل حر', '', '14.2', 'ar_AR'),
                ('cantiere_personale_table', 'mutawwi', 'متطوع', '', '14.2', 'ar_AR'),
                ('cantiere_personale_table', 'tadrib', 'تدريب', '', '14.2', 'ar_AR'),
                # CA
                ('cantiere_personale_table', 'indefinit', 'Indefinit', '', '14.2', 'ca_ES'),
                ('cantiere_personale_table', 'temporal_ca', 'Temporal', '', '14.2', 'ca_ES'),
                ('cantiere_personale_table', 'collaboracio', 'Col·laboració', '', '14.2', 'ca_ES'),
                ('cantiere_personale_table', 'autonom', 'Autònom', '', '14.2', 'ca_ES'),
                ('cantiere_personale_table', 'voluntari', 'Voluntari', '', '14.2', 'ca_ES'),
                ('cantiere_personale_table', 'practiques', 'Pràctiques', '', '14.2', 'ca_ES'),
                # RO
                ('cantiere_personale_table', 'nedeterminat', 'Nedeterminat', '', '14.2', 'ro_RO'),
                ('cantiere_personale_table', 'determinat', 'Determinat', '', '14.2', 'ro_RO'),
                ('cantiere_personale_table', 'colaborare', 'Colaborare', '', '14.2', 'ro_RO'),
                ('cantiere_personale_table', 'liber_profesionist', 'Liber profesionist', '', '14.2', 'ro_RO'),
                ('cantiere_personale_table', 'voluntar', 'Voluntar', '', '14.2', 'ro_RO'),
                ('cantiere_personale_table', 'stagiu', 'Stagiu', '', '14.2', 'ro_RO'),
                # PT
                ('cantiere_personale_table', 'efetivo', 'Efetivo', '', '14.2', 'pt_PT'),
                ('cantiere_personale_table', 'termo_certo', 'Termo certo', '', '14.2', 'pt_PT'),
                ('cantiere_personale_table', 'colaboracao', 'Colaboração', '', '14.2', 'pt_PT'),
                ('cantiere_personale_table', 'independente', 'Independente', '', '14.2', 'pt_PT'),
                ('cantiere_personale_table', 'voluntario_pt', 'Voluntário', '', '14.2', 'pt_PT'),
                ('cantiere_personale_table', 'estagio', 'Estágio', '', '14.2', 'pt_PT'),
                # EL
                ('cantiere_personale_table', 'aoristou', 'Αορίστου χρόνου', '', '14.2', 'el_GR'),
                ('cantiere_personale_table', 'orismenou', 'Ορισμένου χρόνου', '', '14.2', 'el_GR'),
                ('cantiere_personale_table', 'synergasia', 'Συνεργασία', '', '14.2', 'el_GR'),
                ('cantiere_personale_table', 'eleftheros', 'Ελεύθερος επαγγελματίας', '', '14.2', 'el_GR'),
                ('cantiere_personale_table', 'ethelontis', 'Εθελοντής', '', '14.2', 'el_GR'),
                ('cantiere_personale_table', 'praktiki', 'Πρακτική', '', '14.2', 'el_GR'),

                # ── 14.3 tipo_giornata (cantiere_presenze_table) ──
                # IT
                ('cantiere_presenze_table', 'lavorativa', 'Lavorativa', '', '14.3', 'IT'),
                ('cantiere_presenze_table', 'ferie', 'Ferie', '', '14.3', 'IT'),
                ('cantiere_presenze_table', 'malattia', 'Malattia', '', '14.3', 'IT'),
                ('cantiere_presenze_table', 'permesso', 'Permesso', '', '14.3', 'IT'),
                ('cantiere_presenze_table', 'riposo', 'Riposo', '', '14.3', 'IT'),
                ('cantiere_presenze_table', 'trasferta', 'Trasferta', '', '14.3', 'IT'),
                # EN
                ('cantiere_presenze_table', 'working', 'Working', '', '14.3', 'en_US'),
                ('cantiere_presenze_table', 'holiday', 'Holiday', '', '14.3', 'en_US'),
                ('cantiere_presenze_table', 'sick_leave', 'Sick leave', '', '14.3', 'en_US'),
                ('cantiere_presenze_table', 'leave', 'Leave', '', '14.3', 'en_US'),
                ('cantiere_presenze_table', 'rest', 'Rest', '', '14.3', 'en_US'),
                ('cantiere_presenze_table', 'travel', 'Travel', '', '14.3', 'en_US'),
                # DE
                ('cantiere_presenze_table', 'arbeitstag', 'Arbeitstag', '', '14.3', 'de_DE'),
                ('cantiere_presenze_table', 'urlaub', 'Urlaub', '', '14.3', 'de_DE'),
                ('cantiere_presenze_table', 'krankheit', 'Krankheit', '', '14.3', 'de_DE'),
                ('cantiere_presenze_table', 'genehmigung', 'Genehmigung', '', '14.3', 'de_DE'),
                ('cantiere_presenze_table', 'ruhetag', 'Ruhetag', '', '14.3', 'de_DE'),
                ('cantiere_presenze_table', 'dienstreise', 'Dienstreise', '', '14.3', 'de_DE'),
                # ES
                ('cantiere_presenze_table', 'laborable', 'Laborable', '', '14.3', 'es_ES'),
                ('cantiere_presenze_table', 'vacaciones', 'Vacaciones', '', '14.3', 'es_ES'),
                ('cantiere_presenze_table', 'enfermedad', 'Enfermedad', '', '14.3', 'es_ES'),
                ('cantiere_presenze_table', 'permiso', 'Permiso', '', '14.3', 'es_ES'),
                ('cantiere_presenze_table', 'descanso', 'Descanso', '', '14.3', 'es_ES'),
                ('cantiere_presenze_table', 'desplazamiento', 'Desplazamiento', '', '14.3', 'es_ES'),
                # FR
                ('cantiere_presenze_table', 'travail', 'Travail', '', '14.3', 'fr_FR'),
                ('cantiere_presenze_table', 'conge', 'Congé', '', '14.3', 'fr_FR'),
                ('cantiere_presenze_table', 'maladie', 'Maladie', '', '14.3', 'fr_FR'),
                ('cantiere_presenze_table', 'autorisation', 'Autorisation', '', '14.3', 'fr_FR'),
                ('cantiere_presenze_table', 'repos', 'Repos', '', '14.3', 'fr_FR'),
                ('cantiere_presenze_table', 'deplacement', 'Déplacement', '', '14.3', 'fr_FR'),
                # AR
                ('cantiere_presenze_table', 'amal', 'عمل', '', '14.3', 'ar_AR'),
                ('cantiere_presenze_table', 'ijaza', 'إجازة', '', '14.3', 'ar_AR'),
                ('cantiere_presenze_table', 'marad', 'مرض', '', '14.3', 'ar_AR'),
                ('cantiere_presenze_table', 'idhn', 'إذن', '', '14.3', 'ar_AR'),
                ('cantiere_presenze_table', 'raha', 'راحة', '', '14.3', 'ar_AR'),
                ('cantiere_presenze_table', 'safar', 'سفر', '', '14.3', 'ar_AR'),
                # CA
                ('cantiere_presenze_table', 'laborable_ca', 'Laborable', '', '14.3', 'ca_ES'),
                ('cantiere_presenze_table', 'vacances', 'Vacances', '', '14.3', 'ca_ES'),
                ('cantiere_presenze_table', 'malaltia', 'Malaltia', '', '14.3', 'ca_ES'),
                ('cantiere_presenze_table', 'permis', 'Permís', '', '14.3', 'ca_ES'),
                ('cantiere_presenze_table', 'descans', 'Descans', '', '14.3', 'ca_ES'),
                ('cantiere_presenze_table', 'desplacament', 'Desplaçament', '', '14.3', 'ca_ES'),
                # RO
                ('cantiere_presenze_table', 'lucratoare', 'Lucrătoare', '', '14.3', 'ro_RO'),
                ('cantiere_presenze_table', 'concediu', 'Concediu', '', '14.3', 'ro_RO'),
                ('cantiere_presenze_table', 'boala', 'Boală', '', '14.3', 'ro_RO'),
                ('cantiere_presenze_table', 'permisiune', 'Permisiune', '', '14.3', 'ro_RO'),
                ('cantiere_presenze_table', 'odihna', 'Odihnă', '', '14.3', 'ro_RO'),
                ('cantiere_presenze_table', 'deplasare', 'Deplasare', '', '14.3', 'ro_RO'),
                # PT
                ('cantiere_presenze_table', 'trabalho', 'Trabalho', '', '14.3', 'pt_PT'),
                ('cantiere_presenze_table', 'ferias', 'Férias', '', '14.3', 'pt_PT'),
                ('cantiere_presenze_table', 'doenca', 'Doença', '', '14.3', 'pt_PT'),
                ('cantiere_presenze_table', 'licenca', 'Licença', '', '14.3', 'pt_PT'),
                ('cantiere_presenze_table', 'descanso_pt', 'Descanso', '', '14.3', 'pt_PT'),
                ('cantiere_presenze_table', 'deslocacao', 'Deslocação', '', '14.3', 'pt_PT'),
                # EL
                ('cantiere_presenze_table', 'ergasimi', 'Εργάσιμη', '', '14.3', 'el_GR'),
                ('cantiere_presenze_table', 'adeia', 'Άδεια', '', '14.3', 'el_GR'),
                ('cantiere_presenze_table', 'astheneia', 'Ασθένεια', '', '14.3', 'el_GR'),
                ('cantiere_presenze_table', 'adeiopoiisi', 'Αδειοδότηση', '', '14.3', 'el_GR'),
                ('cantiere_presenze_table', 'anapafsi', 'Ανάπαυση', '', '14.3', 'el_GR'),
                ('cantiere_presenze_table', 'metakinisi', 'Μετακίνηση', '', '14.3', 'el_GR'),

                # ── 14.4 categoria_attrezzature (cantiere_attrezzature_table) ──
                # IT
                ('cantiere_attrezzature_table', 'macchinario', 'Macchinario', '', '14.4', 'IT'),
                ('cantiere_attrezzature_table', 'strumento_topografico', 'Strumento topografico', '', '14.4', 'IT'),
                ('cantiere_attrezzature_table', 'strumento_fotografico', 'Strumento fotografico', '', '14.4', 'IT'),
                ('cantiere_attrezzature_table', 'attrezzo_manuale', 'Attrezzo manuale', '', '14.4', 'IT'),
                ('cantiere_attrezzature_table', 'attrezzatura_sicurezza', 'Attrezzatura di sicurezza', '', '14.4', 'IT'),
                ('cantiere_attrezzature_table', 'attrezzatura_laboratorio', 'Attrezzatura di laboratorio', '', '14.4', 'IT'),
                ('cantiere_attrezzature_table', 'veicolo', 'Veicolo', '', '14.4', 'IT'),
                # EN
                ('cantiere_attrezzature_table', 'machinery', 'Machinery', '', '14.4', 'en_US'),
                ('cantiere_attrezzature_table', 'survey_instrument', 'Survey instrument', '', '14.4', 'en_US'),
                ('cantiere_attrezzature_table', 'photographic_equipment', 'Photographic equipment', '', '14.4', 'en_US'),
                ('cantiere_attrezzature_table', 'hand_tool', 'Hand tool', '', '14.4', 'en_US'),
                ('cantiere_attrezzature_table', 'safety_equipment', 'Safety equipment', '', '14.4', 'en_US'),
                ('cantiere_attrezzature_table', 'lab_equipment', 'Lab equipment', '', '14.4', 'en_US'),
                ('cantiere_attrezzature_table', 'vehicle', 'Vehicle', '', '14.4', 'en_US'),
                # DE
                ('cantiere_attrezzature_table', 'maschine', 'Maschine', '', '14.4', 'de_DE'),
                ('cantiere_attrezzature_table', 'vermessungsinstrument', 'Vermessungsinstrument', '', '14.4', 'de_DE'),
                ('cantiere_attrezzature_table', 'fotoausruestung', 'Fotoausrüstung', '', '14.4', 'de_DE'),
                ('cantiere_attrezzature_table', 'handwerkzeug', 'Handwerkzeug', '', '14.4', 'de_DE'),
                ('cantiere_attrezzature_table', 'sicherheitsausruestung', 'Sicherheitsausrüstung', '', '14.4', 'de_DE'),
                ('cantiere_attrezzature_table', 'laborausruestung', 'Laborausrüstung', '', '14.4', 'de_DE'),
                ('cantiere_attrezzature_table', 'fahrzeug', 'Fahrzeug', '', '14.4', 'de_DE'),
                # ES
                ('cantiere_attrezzature_table', 'maquinaria', 'Maquinaria', '', '14.4', 'es_ES'),
                ('cantiere_attrezzature_table', 'instrumento_topografico', 'Instrumento topográfico', '', '14.4', 'es_ES'),
                ('cantiere_attrezzature_table', 'equipo_fotografico', 'Equipo fotográfico', '', '14.4', 'es_ES'),
                ('cantiere_attrezzature_table', 'herramienta_manual', 'Herramienta manual', '', '14.4', 'es_ES'),
                ('cantiere_attrezzature_table', 'equipo_seguridad', 'Equipo de seguridad', '', '14.4', 'es_ES'),
                ('cantiere_attrezzature_table', 'equipo_laboratorio', 'Equipo de laboratorio', '', '14.4', 'es_ES'),
                ('cantiere_attrezzature_table', 'vehiculo', 'Vehículo', '', '14.4', 'es_ES'),
                # FR
                ('cantiere_attrezzature_table', 'machine', 'Machine', '', '14.4', 'fr_FR'),
                ('cantiere_attrezzature_table', 'instrument_topographique', 'Instrument topographique', '', '14.4', 'fr_FR'),
                ('cantiere_attrezzature_table', 'equipement_photo', 'Équipement photographique', '', '14.4', 'fr_FR'),
                ('cantiere_attrezzature_table', 'outil_manuel', 'Outil manuel', '', '14.4', 'fr_FR'),
                ('cantiere_attrezzature_table', 'equipement_securite', 'Équipement de sécurité', '', '14.4', 'fr_FR'),
                ('cantiere_attrezzature_table', 'equipement_laboratoire', 'Équipement de laboratoire', '', '14.4', 'fr_FR'),
                ('cantiere_attrezzature_table', 'vehicule', 'Véhicule', '', '14.4', 'fr_FR'),
                # AR
                ('cantiere_attrezzature_table', 'aliya', 'آلية', '', '14.4', 'ar_AR'),
                ('cantiere_attrezzature_table', 'jihaaz_misaahi', 'جهاز مساحي', '', '14.4', 'ar_AR'),
                ('cantiere_attrezzature_table', 'muaddat_taswir', 'معدات تصوير', '', '14.4', 'ar_AR'),
                ('cantiere_attrezzature_table', 'adaat_yadawiya', 'أدوات يدوية', '', '14.4', 'ar_AR'),
                ('cantiere_attrezzature_table', 'muaddat_salama', 'معدات سلامة', '', '14.4', 'ar_AR'),
                ('cantiere_attrezzature_table', 'muaddat_mukhbar', 'معدات مختبر', '', '14.4', 'ar_AR'),
                ('cantiere_attrezzature_table', 'markaba', 'مركبة', '', '14.4', 'ar_AR'),
                # CA
                ('cantiere_attrezzature_table', 'maquinaria_ca', 'Maquinària', '', '14.4', 'ca_ES'),
                ('cantiere_attrezzature_table', 'instrument_topografic', 'Instrument topogràfic', '', '14.4', 'ca_ES'),
                ('cantiere_attrezzature_table', 'equip_fotografic', 'Equip fotogràfic', '', '14.4', 'ca_ES'),
                ('cantiere_attrezzature_table', 'eina_manual', 'Eina manual', '', '14.4', 'ca_ES'),
                ('cantiere_attrezzature_table', 'equip_seguretat', 'Equip de seguretat', '', '14.4', 'ca_ES'),
                ('cantiere_attrezzature_table', 'equip_laboratori', 'Equip de laboratori', '', '14.4', 'ca_ES'),
                ('cantiere_attrezzature_table', 'vehicle_ca', 'Vehicle', '', '14.4', 'ca_ES'),
                # RO
                ('cantiere_attrezzature_table', 'utilaj', 'Utilaj', '', '14.4', 'ro_RO'),
                ('cantiere_attrezzature_table', 'instrument_topografic_ro', 'Instrument topografic', '', '14.4', 'ro_RO'),
                ('cantiere_attrezzature_table', 'echipament_foto', 'Echipament fotografic', '', '14.4', 'ro_RO'),
                ('cantiere_attrezzature_table', 'unealta_manuala', 'Unealtă manuală', '', '14.4', 'ro_RO'),
                ('cantiere_attrezzature_table', 'echipament_siguranta', 'Echipament de siguranță', '', '14.4', 'ro_RO'),
                ('cantiere_attrezzature_table', 'echipament_laborator', 'Echipament de laborator', '', '14.4', 'ro_RO'),
                ('cantiere_attrezzature_table', 'vehicul', 'Vehicul', '', '14.4', 'ro_RO'),
                # PT
                ('cantiere_attrezzature_table', 'maquinaria_pt', 'Maquinaria', '', '14.4', 'pt_PT'),
                ('cantiere_attrezzature_table', 'instrumento_topografico_pt', 'Instrumento topográfico', '', '14.4', 'pt_PT'),
                ('cantiere_attrezzature_table', 'equipamento_fotografico', 'Equipamento fotográfico', '', '14.4', 'pt_PT'),
                ('cantiere_attrezzature_table', 'ferramenta_manual', 'Ferramenta manual', '', '14.4', 'pt_PT'),
                ('cantiere_attrezzature_table', 'equipamento_seguranca', 'Equipamento de segurança', '', '14.4', 'pt_PT'),
                ('cantiere_attrezzature_table', 'equipamento_laboratorio', 'Equipamento de laboratório', '', '14.4', 'pt_PT'),
                ('cantiere_attrezzature_table', 'veiculo', 'Veículo', '', '14.4', 'pt_PT'),
                # EL
                ('cantiere_attrezzature_table', 'michanima', 'Μηχάνημα', '', '14.4', 'el_GR'),
                ('cantiere_attrezzature_table', 'topografiko_organo', 'Τοπογραφικό όργανο', '', '14.4', 'el_GR'),
                ('cantiere_attrezzature_table', 'fotografikos_exoplismos', 'Φωτογραφικός εξοπλισμός', '', '14.4', 'el_GR'),
                ('cantiere_attrezzature_table', 'cheirokinito_ergaleio', 'Χειροκίνητο εργαλείο', '', '14.4', 'el_GR'),
                ('cantiere_attrezzature_table', 'exoplismos_asfaleias', 'Εξοπλισμός ασφαλείας', '', '14.4', 'el_GR'),
                ('cantiere_attrezzature_table', 'exoplismos_ergastiriou', 'Εξοπλισμός εργαστηρίου', '', '14.4', 'el_GR'),
                ('cantiere_attrezzature_table', 'ochima', 'Όχημα', '', '14.4', 'el_GR'),

                # ── 14.5 stato (cantiere_attrezzature_table) ──
                # IT
                ('cantiere_attrezzature_table', 'in_uso', 'In uso', '', '14.5', 'IT'),
                ('cantiere_attrezzature_table', 'in_manutenzione', 'In manutenzione', '', '14.5', 'IT'),
                ('cantiere_attrezzature_table', 'fuori_servizio', 'Fuori servizio', '', '14.5', 'IT'),
                ('cantiere_attrezzature_table', 'disponibile', 'Disponibile', '', '14.5', 'IT'),
                # EN
                ('cantiere_attrezzature_table', 'in_use', 'In use', '', '14.5', 'en_US'),
                ('cantiere_attrezzature_table', 'under_maintenance', 'Under maintenance', '', '14.5', 'en_US'),
                ('cantiere_attrezzature_table', 'out_of_service', 'Out of service', '', '14.5', 'en_US'),
                ('cantiere_attrezzature_table', 'available', 'Available', '', '14.5', 'en_US'),
                # DE
                ('cantiere_attrezzature_table', 'in_benutzung', 'In Benutzung', '', '14.5', 'de_DE'),
                ('cantiere_attrezzature_table', 'in_wartung', 'In Wartung', '', '14.5', 'de_DE'),
                ('cantiere_attrezzature_table', 'ausser_betrieb', 'Außer Betrieb', '', '14.5', 'de_DE'),
                ('cantiere_attrezzature_table', 'verfuegbar', 'Verfügbar', '', '14.5', 'de_DE'),
                # ES
                ('cantiere_attrezzature_table', 'en_uso', 'En uso', '', '14.5', 'es_ES'),
                ('cantiere_attrezzature_table', 'en_mantenimiento', 'En mantenimiento', '', '14.5', 'es_ES'),
                ('cantiere_attrezzature_table', 'fuera_servicio', 'Fuera de servicio', '', '14.5', 'es_ES'),
                ('cantiere_attrezzature_table', 'disponible_es', 'Disponible', '', '14.5', 'es_ES'),
                # FR
                ('cantiere_attrezzature_table', 'en_utilisation', 'En utilisation', '', '14.5', 'fr_FR'),
                ('cantiere_attrezzature_table', 'en_maintenance', 'En maintenance', '', '14.5', 'fr_FR'),
                ('cantiere_attrezzature_table', 'hors_service', 'Hors service', '', '14.5', 'fr_FR'),
                ('cantiere_attrezzature_table', 'disponible_fr', 'Disponible', '', '14.5', 'fr_FR'),
                # AR
                ('cantiere_attrezzature_table', 'qaid_istikhdaam', 'قيد الاستخدام', '', '14.5', 'ar_AR'),
                ('cantiere_attrezzature_table', 'qaid_siyaana', 'قيد الصيانة', '', '14.5', 'ar_AR'),
                ('cantiere_attrezzature_table', 'kharij_khidma', 'خارج الخدمة', '', '14.5', 'ar_AR'),
                ('cantiere_attrezzature_table', 'mutaah', 'متاح', '', '14.5', 'ar_AR'),
                # CA
                ('cantiere_attrezzature_table', 'en_us', 'En ús', '', '14.5', 'ca_ES'),
                ('cantiere_attrezzature_table', 'en_manteniment', 'En manteniment', '', '14.5', 'ca_ES'),
                ('cantiere_attrezzature_table', 'fora_servei', 'Fora de servei', '', '14.5', 'ca_ES'),
                ('cantiere_attrezzature_table', 'disponible_ca', 'Disponible', '', '14.5', 'ca_ES'),
                # RO
                ('cantiere_attrezzature_table', 'in_utilizare', 'În utilizare', '', '14.5', 'ro_RO'),
                ('cantiere_attrezzature_table', 'in_mentenanta', 'În mentenanță', '', '14.5', 'ro_RO'),
                ('cantiere_attrezzature_table', 'scos_din_uz', 'Scos din uz', '', '14.5', 'ro_RO'),
                ('cantiere_attrezzature_table', 'disponibil', 'Disponibil', '', '14.5', 'ro_RO'),
                # PT
                ('cantiere_attrezzature_table', 'em_uso', 'Em uso', '', '14.5', 'pt_PT'),
                ('cantiere_attrezzature_table', 'em_manutencao', 'Em manutenção', '', '14.5', 'pt_PT'),
                ('cantiere_attrezzature_table', 'fora_servico', 'Fora de serviço', '', '14.5', 'pt_PT'),
                ('cantiere_attrezzature_table', 'disponivel', 'Disponível', '', '14.5', 'pt_PT'),
                # EL
                ('cantiere_attrezzature_table', 'se_chrisi', 'Σε χρήση', '', '14.5', 'el_GR'),
                ('cantiere_attrezzature_table', 'se_syntirisi', 'Σε συντήρηση', '', '14.5', 'el_GR'),
                ('cantiere_attrezzature_table', 'ektos_leitourgias', 'Εκτός λειτουργίας', '', '14.5', 'el_GR'),
                ('cantiere_attrezzature_table', 'diathesimo', 'Διαθέσιμο', '', '14.5', 'el_GR'),

                # ── 14.6 proprieta (cantiere_attrezzature_table) ──
                # IT
                ('cantiere_attrezzature_table', 'proprio', 'Proprio', '', '14.6', 'IT'),
                ('cantiere_attrezzature_table', 'noleggio', 'Noleggio', '', '14.6', 'IT'),
                ('cantiere_attrezzature_table', 'comodato', 'Comodato', '', '14.6', 'IT'),
                ('cantiere_attrezzature_table', 'prestito', 'Prestito', '', '14.6', 'IT'),
                # EN
                ('cantiere_attrezzature_table', 'owned', 'Owned', '', '14.6', 'en_US'),
                ('cantiere_attrezzature_table', 'rented', 'Rented', '', '14.6', 'en_US'),
                ('cantiere_attrezzature_table', 'on_loan_free', 'On loan (free)', '', '14.6', 'en_US'),
                ('cantiere_attrezzature_table', 'borrowed', 'Borrowed', '', '14.6', 'en_US'),
                # DE
                ('cantiere_attrezzature_table', 'eigentum', 'Eigentum', '', '14.6', 'de_DE'),
                ('cantiere_attrezzature_table', 'miete', 'Miete', '', '14.6', 'de_DE'),
                ('cantiere_attrezzature_table', 'leihe', 'Leihe', '', '14.6', 'de_DE'),
                ('cantiere_attrezzature_table', 'ausleihe', 'Ausleihe', '', '14.6', 'de_DE'),
                # ES
                ('cantiere_attrezzature_table', 'propio', 'Propio', '', '14.6', 'es_ES'),
                ('cantiere_attrezzature_table', 'alquiler', 'Alquiler', '', '14.6', 'es_ES'),
                ('cantiere_attrezzature_table', 'comodato_es', 'Comodato', '', '14.6', 'es_ES'),
                ('cantiere_attrezzature_table', 'prestamo', 'Préstamo', '', '14.6', 'es_ES'),
                # FR
                ('cantiere_attrezzature_table', 'propriete', 'Propriété', '', '14.6', 'fr_FR'),
                ('cantiere_attrezzature_table', 'location', 'Location', '', '14.6', 'fr_FR'),
                ('cantiere_attrezzature_table', 'pret_gratuit', 'Prêt gratuit', '', '14.6', 'fr_FR'),
                ('cantiere_attrezzature_table', 'emprunt', 'Emprunt', '', '14.6', 'fr_FR'),
                # AR
                ('cantiere_attrezzature_table', 'milkiyya', 'ملكية', '', '14.6', 'ar_AR'),
                ('cantiere_attrezzature_table', 'ijar', 'إيجار', '', '14.6', 'ar_AR'),
                ('cantiere_attrezzature_table', 'iara_majjaniya', 'إعارة مجانية', '', '14.6', 'ar_AR'),
                ('cantiere_attrezzature_table', 'iara', 'إعارة', '', '14.6', 'ar_AR'),
                # CA
                ('cantiere_attrezzature_table', 'propi', 'Propi', '', '14.6', 'ca_ES'),
                ('cantiere_attrezzature_table', 'lloguer', 'Lloguer', '', '14.6', 'ca_ES'),
                ('cantiere_attrezzature_table', 'comodat', 'Comodat', '', '14.6', 'ca_ES'),
                ('cantiere_attrezzature_table', 'prestec', 'Préstec', '', '14.6', 'ca_ES'),
                # RO
                ('cantiere_attrezzature_table', 'propriu', 'Propriu', '', '14.6', 'ro_RO'),
                ('cantiere_attrezzature_table', 'inchiriere', 'Închiriere', '', '14.6', 'ro_RO'),
                ('cantiere_attrezzature_table', 'comodat_ro', 'Comodat', '', '14.6', 'ro_RO'),
                ('cantiere_attrezzature_table', 'imprumut', 'Împrumut', '', '14.6', 'ro_RO'),
                # PT
                ('cantiere_attrezzature_table', 'proprio_pt', 'Próprio', '', '14.6', 'pt_PT'),
                ('cantiere_attrezzature_table', 'aluguer', 'Aluguer', '', '14.6', 'pt_PT'),
                ('cantiere_attrezzature_table', 'comodato_pt', 'Comodato', '', '14.6', 'pt_PT'),
                ('cantiere_attrezzature_table', 'emprestimo', 'Empréstimo', '', '14.6', 'pt_PT'),
                # EL
                ('cantiere_attrezzature_table', 'idioktito', 'Ιδιόκτητο', '', '14.6', 'el_GR'),
                ('cantiere_attrezzature_table', 'enoikiasi', 'Ενοικίαση', '', '14.6', 'el_GR'),
                ('cantiere_attrezzature_table', 'chrisimodaneio', 'Χρησιδάνειο', '', '14.6', 'el_GR'),
                ('cantiere_attrezzature_table', 'daneismo', 'Δανεισμός', '', '14.6', 'el_GR'),

                # ── 14.7 categoria_budget (cantiere_budget_table) ──
                # IT
                ('cantiere_budget_table', 'personale_cat', 'Personale', '', '14.7', 'IT'),
                ('cantiere_budget_table', 'materiali', 'Materiali', '', '14.7', 'IT'),
                ('cantiere_budget_table', 'attrezzature_cat', 'Attrezzature', '', '14.7', 'IT'),
                ('cantiere_budget_table', 'logistica', 'Logistica', '', '14.7', 'IT'),
                ('cantiere_budget_table', 'documentazione', 'Documentazione', '', '14.7', 'IT'),
                ('cantiere_budget_table', 'laboratorio', 'Laboratorio', '', '14.7', 'IT'),
                ('cantiere_budget_table', 'altro', 'Altro', '', '14.7', 'IT'),
                # EN
                ('cantiere_budget_table', 'personnel', 'Personnel', '', '14.7', 'en_US'),
                ('cantiere_budget_table', 'materials', 'Materials', '', '14.7', 'en_US'),
                ('cantiere_budget_table', 'equipment', 'Equipment', '', '14.7', 'en_US'),
                ('cantiere_budget_table', 'logistics', 'Logistics', '', '14.7', 'en_US'),
                ('cantiere_budget_table', 'documentation', 'Documentation', '', '14.7', 'en_US'),
                ('cantiere_budget_table', 'laboratory', 'Laboratory', '', '14.7', 'en_US'),
                ('cantiere_budget_table', 'other', 'Other', '', '14.7', 'en_US'),
                # DE
                ('cantiere_budget_table', 'personal_de', 'Personal', '', '14.7', 'de_DE'),
                ('cantiere_budget_table', 'materialien', 'Materialien', '', '14.7', 'de_DE'),
                ('cantiere_budget_table', 'ausruestung', 'Ausrüstung', '', '14.7', 'de_DE'),
                ('cantiere_budget_table', 'logistik', 'Logistik', '', '14.7', 'de_DE'),
                ('cantiere_budget_table', 'dokumentation', 'Dokumentation', '', '14.7', 'de_DE'),
                ('cantiere_budget_table', 'labor', 'Labor', '', '14.7', 'de_DE'),
                ('cantiere_budget_table', 'sonstiges', 'Sonstiges', '', '14.7', 'de_DE'),
                # ES
                ('cantiere_budget_table', 'personal_es', 'Personal', '', '14.7', 'es_ES'),
                ('cantiere_budget_table', 'materiales', 'Materiales', '', '14.7', 'es_ES'),
                ('cantiere_budget_table', 'equipamiento', 'Equipamiento', '', '14.7', 'es_ES'),
                ('cantiere_budget_table', 'logistica_es', 'Logística', '', '14.7', 'es_ES'),
                ('cantiere_budget_table', 'documentacion', 'Documentación', '', '14.7', 'es_ES'),
                ('cantiere_budget_table', 'laboratorio_es', 'Laboratorio', '', '14.7', 'es_ES'),
                ('cantiere_budget_table', 'otro', 'Otro', '', '14.7', 'es_ES'),
                # FR
                ('cantiere_budget_table', 'personnel_fr', 'Personnel', '', '14.7', 'fr_FR'),
                ('cantiere_budget_table', 'materiaux', 'Matériaux', '', '14.7', 'fr_FR'),
                ('cantiere_budget_table', 'equipements', 'Équipements', '', '14.7', 'fr_FR'),
                ('cantiere_budget_table', 'logistique', 'Logistique', '', '14.7', 'fr_FR'),
                ('cantiere_budget_table', 'documentation_fr', 'Documentation', '', '14.7', 'fr_FR'),
                ('cantiere_budget_table', 'laboratoire', 'Laboratoire', '', '14.7', 'fr_FR'),
                ('cantiere_budget_table', 'autre', 'Autre', '', '14.7', 'fr_FR'),
                # AR
                ('cantiere_budget_table', 'muwazzafin', 'موظفون', '', '14.7', 'ar_AR'),
                ('cantiere_budget_table', 'mawaadd', 'مواد', '', '14.7', 'ar_AR'),
                ('cantiere_budget_table', 'muaddat', 'معدات', '', '14.7', 'ar_AR'),
                ('cantiere_budget_table', 'laujistiyya', 'لوجستية', '', '14.7', 'ar_AR'),
                ('cantiere_budget_table', 'tawthiq', 'توثيق', '', '14.7', 'ar_AR'),
                ('cantiere_budget_table', 'mukhbar', 'مختبر', '', '14.7', 'ar_AR'),
                ('cantiere_budget_table', 'akhar', 'أخرى', '', '14.7', 'ar_AR'),
                # CA
                ('cantiere_budget_table', 'personal_ca', 'Personal', '', '14.7', 'ca_ES'),
                ('cantiere_budget_table', 'materials', 'Materials', '', '14.7', 'ca_ES'),
                ('cantiere_budget_table', 'equipament', 'Equipament', '', '14.7', 'ca_ES'),
                ('cantiere_budget_table', 'logistica_ca', 'Logística', '', '14.7', 'ca_ES'),
                ('cantiere_budget_table', 'documentacio', 'Documentació', '', '14.7', 'ca_ES'),
                ('cantiere_budget_table', 'laboratori', 'Laboratori', '', '14.7', 'ca_ES'),
                ('cantiere_budget_table', 'altre', 'Altre', '', '14.7', 'ca_ES'),
                # RO
                ('cantiere_budget_table', 'personal_ro', 'Personal', '', '14.7', 'ro_RO'),
                ('cantiere_budget_table', 'materiale', 'Materiale', '', '14.7', 'ro_RO'),
                ('cantiere_budget_table', 'echipamente', 'Echipamente', '', '14.7', 'ro_RO'),
                ('cantiere_budget_table', 'logistica_ro', 'Logistică', '', '14.7', 'ro_RO'),
                ('cantiere_budget_table', 'documentatie', 'Documentație', '', '14.7', 'ro_RO'),
                ('cantiere_budget_table', 'laborator', 'Laborator', '', '14.7', 'ro_RO'),
                ('cantiere_budget_table', 'altele', 'Altele', '', '14.7', 'ro_RO'),
                # PT
                ('cantiere_budget_table', 'pessoal', 'Pessoal', '', '14.7', 'pt_PT'),
                ('cantiere_budget_table', 'materiais', 'Materiais', '', '14.7', 'pt_PT'),
                ('cantiere_budget_table', 'equipamentos', 'Equipamentos', '', '14.7', 'pt_PT'),
                ('cantiere_budget_table', 'logistica_pt', 'Logística', '', '14.7', 'pt_PT'),
                ('cantiere_budget_table', 'documentacao', 'Documentação', '', '14.7', 'pt_PT'),
                ('cantiere_budget_table', 'laboratorio_pt', 'Laboratório', '', '14.7', 'pt_PT'),
                ('cantiere_budget_table', 'outro', 'Outro', '', '14.7', 'pt_PT'),
                # EL
                ('cantiere_budget_table', 'prosopiko', 'Προσωπικό', '', '14.7', 'el_GR'),
                ('cantiere_budget_table', 'ylika', 'Υλικά', '', '14.7', 'el_GR'),
                ('cantiere_budget_table', 'exoplismos', 'Εξοπλισμός', '', '14.7', 'el_GR'),
                ('cantiere_budget_table', 'logistiki', 'Εφοδιαστική', '', '14.7', 'el_GR'),
                ('cantiere_budget_table', 'tekmiriosi', 'Τεκμηρίωση', '', '14.7', 'el_GR'),
                ('cantiere_budget_table', 'ergastirio', 'Εργαστήριο', '', '14.7', 'el_GR'),
                ('cantiere_budget_table', 'allo', 'Άλλο', '', '14.7', 'el_GR'),
            ]

            inserted_count = 0
            for entry in entries:
                try:
                    self.cursor.execute("""
                        INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle
                        (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, entry)
                    if self.cursor.rowcount > 0:
                        inserted_count += 1
                except Exception as e:
                    pass

            self.conn.commit()

            if inserted_count > 0:
                self.log_message(f"Aggiunte {inserted_count} voci thesaurus gestione cantiere (14.x)")
                self.updates_made.append(f"cantiere thesaurus ({inserted_count} voci)")

        except Exception as e:
            self.log_message(f"Errore aggiungendo voci thesaurus cantiere: {e}", Qgis.Warning if QGIS_AVAILABLE else None)

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
            # sub_inv: suffisso opzionale (es. "a", "b1", "bis") che si applica a
            # numero_inventario e n_reperto. Se aggiungiamo la colonna dobbiamo anche
            # ricostruire gli indici UNIQUE per includerla.
            self.cursor.execute("PRAGMA table_info(inventario_materiali_table)")
            _had_sub_inv = any(c[1] == 'sub_inv' for c in self.cursor.fetchall())
            self.add_column_if_missing('inventario_materiali_table', 'sub_inv', 'TEXT')
            if not _had_sub_inv:
                self._rebuild_invmat_unique_indexes()

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
                    us_table.quota_max_abs,
                    us_table.quota_max_rel,
                    us_table.quota_min_abs,
                    us_table.quota_min_rel,
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
                ORDER BY us_table.order_layer ASC, pyunitastratigrafiche.stratigraph_index_us ASC
            '''),
            # NOTE: pyarchinit_quote, pyarchinit_quote_usm, pyunitastratigrafiche
            # and pyunitastratigrafiche_usm are TABLES in the canonical pyarchinit
            # template DB (resources/dbfiles/pyarchinit.sqlite), not views derived
            # from us_table. They have their own schemas (gid AUTOINCREMENT, the_geom
            # registered as a Spatialite geometry column, etc.) and are populated
            # independently. Trying to recreate them as views fails with
            # "use DROP TABLE to delete table X" and would also lose user data.
            # They are managed by _check_and_restore_backup_tables / spatialite
            # registration paths instead.
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

        # Coerce key string columns that exist as INT/INTEGER in older DBs.
        # These columns are TEXT in the canonical template DB
        # (resources/dbfiles/pyarchinit.sqlite); when they get created as INT
        # the spatialite views and JOINs against pyunitastratigrafiche.*_s
        # (which are TEXT) silently mis-match.
        columns_to_coerce_to_text = [
            ('us_table', 'us'),
            ('inventario_materiali_table', 'area'),
            ('inventario_materiali_table', 'us'),
            ('campioni_table', 'us'),
            ('pyarchinit_quote', 'area_q'),
            ('pyarchinit_quote', 'us_q'),
            ('pyarchinit_quote_usm', 'area_q'),
            ('pyarchinit_quote_usm', 'us_q'),
        ]
        for tbl, col in columns_to_coerce_to_text:
            self._fix_column_to_text(tbl, col)

    def _fix_column_to_text(self, table_name, column_name):
        """Coerce a column to TEXT type via rebuild (rename → recreate → copy).

        No-op if the table is missing or the column is already TEXT.
        Preserves existing triggers attached to the table by re-issuing them
        after the rebuild. Indexes are restored later by the performance-index
        creation step. Falls back to restoring the renamed copy on failure.

        Uses PRAGMA legacy_alter_table=ON during the rebuild because
        SpatiaLite installs cross-table triggers (e.g. on
        ISO_metadata_reference) whose body parses NEW.* references in a way
        that breaks SQLite 3.25+'s automatic trigger rewriting on RENAME.
        Legacy mode keeps trigger SQL intact and mirrors how older Spatialite
        toolchains performed in-place schema migrations.
        """
        if not self.table_exists(table_name):
            return
        self.cursor.execute(f"PRAGMA table_info({table_name})")
        columns = self.cursor.fetchall()
        target = next((c for c in columns if c[1] == column_name), None)
        if target is None:
            return
        if (target[2] or '').upper().strip() in ('TEXT', 'VARCHAR', 'CHAR'):
            return

        self.log_message(
            f"Correzione campo {column_name} in {table_name} "
            f"da {target[2]} a TEXT...")
        old_table = f"{table_name}_old_typefix"
        # Snapshot pragmas so we can restore them
        self.cursor.execute("PRAGMA legacy_alter_table")
        prev_legacy = self.cursor.fetchone()[0]
        self.cursor.execute("PRAGMA foreign_keys")
        prev_fkeys = self.cursor.fetchone()[0]
        self.cursor.execute("PRAGMA legacy_alter_table=ON")
        self.cursor.execute("PRAGMA foreign_keys=OFF")
        try:
            # Capture triggers + user-defined indexes before rename so they
            # can be re-applied after the rebuild. Auto-indexes generated by
            # PRIMARY KEY / UNIQUE constraints are excluded (SQL is NULL for
            # them; SQLite recreates them implicitly from the CREATE TABLE).
            self.cursor.execute(
                "SELECT sql FROM sqlite_master "
                "WHERE type='trigger' AND tbl_name=? AND sql IS NOT NULL",
                (table_name,))
            trigger_sqls = [row[0] for row in self.cursor.fetchall()]
            self.cursor.execute(
                "SELECT sql FROM sqlite_master "
                "WHERE type='index' AND tbl_name=? AND sql IS NOT NULL",
                (table_name,))
            index_sqls = [row[0] for row in self.cursor.fetchall()]

            create_sql = self._get_create_table_sql(table_name)
            if not create_sql:
                return
            # Replace `<col> INT[EGER]` (with word boundary) inside the CREATE TABLE.
            # The leading lookahead matches the separator (newline/whitespace/comma/`(`)
            # so we don't fire on substrings of other identifiers.
            pattern = re.compile(
                r'(?P<lead>[\s,(])' + re.escape(column_name) +
                r'\s+(?:INTEGER|INT)\b',
                re.IGNORECASE)
            new_sql, n = pattern.subn(
                lambda m: f"{m.group('lead')}{column_name} TEXT",
                create_sql, count=1)
            if n == 0:
                self.log_message(
                    f"Avviso: pattern colonna non trovato per "
                    f"{table_name}.{column_name}, skip")
                return

            self.cursor.execute(
                f"ALTER TABLE {table_name} RENAME TO {old_table}")
            self.cursor.execute(new_sql)
            col_list = ','.join(c[1] for c in columns)
            self.cursor.execute(
                f"INSERT INTO {table_name} ({col_list}) "
                f"SELECT {col_list} FROM {old_table}")
            self.cursor.execute(f"DROP TABLE {old_table}")

            for trig_sql in trigger_sqls:
                try:
                    self.cursor.execute(trig_sql)
                except Exception as te:
                    self.log_message(
                        f"Avviso: impossibile ricreare trigger su "
                        f"{table_name}: {te}")
            for idx_sql in index_sqls:
                try:
                    self.cursor.execute(idx_sql)
                except Exception as ie:
                    self.log_message(
                        f"Avviso: impossibile ricreare indice su "
                        f"{table_name}: {ie}")

            self.updates_made.append(
                f"FIX {table_name}.{column_name} to TEXT")
        except Exception as e:
            self.log_message(
                f"Errore correggendo {table_name}.{column_name}: {e}")
            try:
                self.cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
                self.cursor.execute(
                    f"ALTER TABLE {old_table} RENAME TO {table_name}")
            except Exception:
                pass
        finally:
            self.cursor.execute(
                f"PRAGMA legacy_alter_table={'ON' if prev_legacy else 'OFF'}")
            self.cursor.execute(
                f"PRAGMA foreign_keys={'ON' if prev_fkeys else 'OFF'}")

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
                print(f"DEBUG [sqlite_db_updater]: Aggiunta colonna {table_name}.{column_name} {column_type}")  # DEBUG
                self.cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
                self.log_message(f"Aggiunta colonna {table_name}.{column_name}")
                self.updates_made.append(f"{table_name}.{column_name}")
            except Exception as e:
                self.log_message(f"Errore aggiungendo colonna {table_name}.{column_name}: {e}", Qgis.Warning if QGIS_AVAILABLE else None)

    def _rebuild_invmat_unique_indexes(self):
        """Ricrea gli indici UNIQUE di inventario_materiali_table per includere sub_inv.

        In SQLite i vincoli UNIQUE della CREATE TABLE non possono essere modificati
        con ALTER, ma gli indici UNIQUE creati a parte (idx_n_reperto e simili) si'.
        Sostituiamo l'indice su (sito, n_reperto) con (sito, n_reperto, sub_inv) e
        aggiungiamo un indice equivalente per (sito, numero_inventario, sub_inv).
        I vecchi record senza sub_inv (NULL) non vengono toccati e SQLite considera
        NULL != NULL nei vincoli UNIQUE quindi non ci sono falsi positivi.
        """
        try:
            self.cursor.execute('DROP INDEX IF EXISTS idx_n_reperto')
            self.cursor.execute(
                'CREATE UNIQUE INDEX idx_n_reperto '
                'ON inventario_materiali_table(sito, n_reperto, sub_inv)')
            self.cursor.execute('DROP INDEX IF EXISTS idx_invmat_unico_sub')
            self.cursor.execute(
                'CREATE UNIQUE INDEX idx_invmat_unico_sub '
                'ON inventario_materiali_table(sito, numero_inventario, sub_inv)')
            self.log_message('Ricostruiti indici UNIQUE invmat con sub_inv')
        except Exception as e:
            self.log_message(f"Avviso: impossibile ricostruire UNIQUE invmat: {e}",
                             Qgis.Warning if QGIS_AVAILABLE else None)

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


    def update_personale_table(self):
        """Crea personale_table se non esiste"""
        if not self.table_exists('personale_table'):
            self.log_message("Creazione tabella personale_table...")
            self.cursor.execute('''
                CREATE TABLE personale_table (
                    id_personale INTEGER PRIMARY KEY AUTOINCREMENT,
                    sito TEXT DEFAULT '',
                    nome TEXT DEFAULT '',
                    cognome TEXT DEFAULT '',
                    ruolo TEXT DEFAULT '',
                    qualifica TEXT DEFAULT '',
                    codice_fiscale TEXT DEFAULT '',
                    email TEXT DEFAULT '',
                    telefono TEXT DEFAULT '',
                    data_nascita TEXT DEFAULT '',
                    indirizzo TEXT DEFAULT '',
                    tipo_contratto TEXT DEFAULT '',
                    data_inizio_contratto TEXT DEFAULT '',
                    data_fine_contratto TEXT DEFAULT '',
                    tariffa_oraria REAL DEFAULT 0,
                    tariffa_giornaliera REAL DEFAULT 0,
                    iban TEXT DEFAULT '',
                    note TEXT DEFAULT '',
                    attivo INTEGER DEFAULT 1,
                    entity_uuid TEXT DEFAULT '',
                    UNIQUE(sito, codice_fiscale)
                )
            ''')
            self.updates_made.append("CREATE TABLE personale_table")

    def update_presenze_table(self):
        """Crea presenze_table se non esiste"""
        if not self.table_exists('presenze_table'):
            self.log_message("Creazione tabella presenze_table...")
            self.cursor.execute('''
                CREATE TABLE presenze_table (
                    id_presenza INTEGER PRIMARY KEY AUTOINCREMENT,
                    sito TEXT DEFAULT '',
                    id_personale INTEGER DEFAULT 0,
                    data TEXT DEFAULT '',
                    ora_ingresso TEXT DEFAULT '',
                    ora_uscita TEXT DEFAULT '',
                    ore_ordinarie REAL DEFAULT 0,
                    ore_straordinario REAL DEFAULT 0,
                    tipo_giornata TEXT DEFAULT '',
                    turno TEXT DEFAULT '',
                    area_lavoro TEXT DEFAULT '',
                    note TEXT DEFAULT '',
                    costo_giornata REAL DEFAULT 0,
                    entity_uuid TEXT DEFAULT '',
                    UNIQUE(sito, id_personale, data, turno)
                )
            ''')
            self.updates_made.append("CREATE TABLE presenze_table")

    def update_attrezzature_table(self):
        """Crea attrezzature_table se non esiste"""
        if not self.table_exists('attrezzature_table'):
            self.log_message("Creazione tabella attrezzature_table...")
            self.cursor.execute('''
                CREATE TABLE attrezzature_table (
                    id_attrezzatura INTEGER PRIMARY KEY AUTOINCREMENT,
                    sito TEXT DEFAULT '',
                    codice_inventario TEXT DEFAULT '',
                    nome TEXT DEFAULT '',
                    categoria TEXT DEFAULT '',
                    marca TEXT DEFAULT '',
                    modello TEXT DEFAULT '',
                    numero_serie TEXT DEFAULT '',
                    proprieta TEXT DEFAULT '',
                    data_acquisto TEXT DEFAULT '',
                    costo_acquisto REAL DEFAULT 0,
                    costo_noleggio_giorno REAL DEFAULT 0,
                    stato TEXT DEFAULT '',
                    assegnato_a INTEGER DEFAULT 0,
                    data_ultima_manutenzione TEXT DEFAULT '',
                    data_prossima_manutenzione TEXT DEFAULT '',
                    note TEXT DEFAULT '',
                    entity_uuid TEXT DEFAULT '',
                    UNIQUE(sito, codice_inventario)
                )
            ''')
            self.updates_made.append("CREATE TABLE attrezzature_table")

    def update_budget_table(self):
        """Crea budget_table se non esiste"""
        if not self.table_exists('budget_table'):
            self.log_message("Creazione tabella budget_table...")
            self.cursor.execute('''
                CREATE TABLE budget_table (
                    id_budget INTEGER PRIMARY KEY AUTOINCREMENT,
                    sito TEXT DEFAULT '',
                    anno INTEGER DEFAULT 0,
                    categoria TEXT DEFAULT '',
                    descrizione TEXT DEFAULT '',
                    importo_previsto REAL DEFAULT 0,
                    importo_effettivo REAL DEFAULT 0,
                    data_registrazione TEXT DEFAULT '',
                    data_spesa TEXT DEFAULT '',
                    fornitore TEXT DEFAULT '',
                    numero_fattura TEXT DEFAULT '',
                    note TEXT DEFAULT '',
                    entity_uuid TEXT DEFAULT ''
                )
            ''')
            self.updates_made.append("CREATE TABLE budget_table")

    def update_computo_metrico_table(self):
        """Crea computo_metrico_table se non esiste"""
        if not self.table_exists('computo_metrico_table'):
            self.log_message("Creazione tabella computo_metrico_table...")
            self.cursor.execute('''
                CREATE TABLE computo_metrico_table (
                    id_computo INTEGER PRIMARY KEY AUTOINCREMENT,
                    sito TEXT DEFAULT '',
                    nome_calcolo TEXT DEFAULT '',
                    tipo_calcolo TEXT DEFAULT '',
                    dem_pre TEXT DEFAULT '',
                    dem_post TEXT DEFAULT '',
                    layer_poligono TEXT DEFAULT '',
                    area_mq REAL DEFAULT 0,
                    volume_mc REAL DEFAULT 0,
                    quota_min REAL DEFAULT 0,
                    quota_max REAL DEFAULT 0,
                    data_calcolo TEXT DEFAULT '',
                    fase_scavo TEXT DEFAULT '',
                    note TEXT DEFAULT '',
                    entity_uuid TEXT DEFAULT ''
                )
            ''')
            self.updates_made.append("CREATE TABLE computo_metrico_table")

    def update_inventario_lapidei_table(self):
        """Crea inventario_lapidei_table se non esiste"""
        if not self.table_exists('inventario_lapidei_table'):
            self.log_message("Creazione tabella inventario_lapidei_table...")
            self.cursor.execute('''
                CREATE TABLE inventario_lapidei_table (
                    id_invlap INTEGER PRIMARY KEY AUTOINCREMENT,
                    sito TEXT DEFAULT '',
                    scheda_numero INTEGER DEFAULT 0,
                    collocazione TEXT DEFAULT '',
                    oggetto TEXT DEFAULT '',
                    tipologia TEXT DEFAULT '',
                    materiale TEXT DEFAULT '',
                    d_letto_posa REAL DEFAULT 0,
                    d_letto_attesa REAL DEFAULT 0,
                    toro REAL DEFAULT 0,
                    spessore REAL DEFAULT 0,
                    larghezza REAL DEFAULT 0,
                    lunghezza REAL DEFAULT 0,
                    h REAL DEFAULT 0,
                    descrizione TEXT DEFAULT '',
                    lavorazione_e_stato_di_conservazione TEXT DEFAULT '',
                    confronti TEXT DEFAULT '',
                    cronologia TEXT DEFAULT '',
                    bibliografia TEXT DEFAULT '',
                    compilatore TEXT DEFAULT '',
                    entity_uuid TEXT DEFAULT '',
                    UNIQUE(sito, scheda_numero)
                )
            ''')
            self.updates_made.append("CREATE TABLE inventario_lapidei_table")


def check_and_update_sqlite_db(db_path, parent=None):
    """Funzione helper per verificare e aggiornare un database SQLite"""
    print(f"DEBUG [sqlite_db_updater]: check_and_update_sqlite_db() chiamato con db_path={db_path}")  # DEBUG
    if not db_path.endswith('.sqlite'):
        print("DEBUG [sqlite_db_updater]: Non è un file .sqlite, skip")  # DEBUG
        return True

    updater = SQLiteDBUpdater(db_path, parent)
    result = updater.check_and_update_database()
    print(f"DEBUG [sqlite_db_updater]: check_and_update_database() ritorna {result}")  # DEBUG
    return result