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
        if QGIS_AVAILABLE and level is not None:
            QgsMessageLog.logMessage(message, "PyArchInit SQLite Updater", level)
        print(message)
    
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
            
            # Add missing columns to various tables
            self.update_us_table()
            self.update_site_table()
            self.update_other_tables()
            
            # Fix vector layer views
            self.fix_vector_layer_views()
            
            # Commit changes
            self.conn.commit()
            self.conn.close()
            
            # Show result
            if QGIS_AVAILABLE and self.parent:
                QMessageBox.information(
                    self.parent,
                    "Aggiornamento Completato",
                    f"Database aggiornato con successo!\n\n"
                    f"Modifiche effettuate: {len(self.updates_made)}\n"
                    f"Backup salvato con estensione .backup"
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
        
        # pottery_table
        if self.table_exists('pottery_table'):
            self.add_column_if_missing('pottery_table', 'anno', 'TEXT')
            self.add_column_if_missing('pottery_table', 'fabric', 'TEXT')
            self.add_column_if_missing('pottery_table', 'percent', 'TEXT')
            self.add_column_if_missing('pottery_table', 'material', 'TEXT')
            self.add_column_if_missing('pottery_table', 'form', 'TEXT')
    
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
    
    def fix_vector_layer_views(self):
        """Corregge i tipi di campo nelle view dei layer vettoriali"""
        # Prima correggi i tipi di campo nelle tabelle base
        self.fix_field_types_in_base_tables()
        
        views_to_fix = [
            ('pyarchinit_quote', '''
                CREATE VIEW pyarchinit_quote AS
                SELECT 
                    sito,
                    area,  -- Mantieni come TEXT
                    us,    -- Mantieni come TEXT
                    unita_tipo,
                    quota_min,
                    quota_max,
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
                # Check if view exists
                self.cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='view' AND name=?", 
                    (view_name,)
                )
                if self.cursor.fetchone():
                    self.log_message(f"Dropping and recreating view {view_name}")
                    self.cursor.execute(f"DROP VIEW IF EXISTS {view_name}")
                    self.cursor.execute(create_sql)
                    self.updates_made.append(f"RECREATE VIEW {view_name}")
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


def check_and_update_sqlite_db(db_path, parent=None):
    """Funzione helper per verificare e aggiornare un database SQLite"""
    if not db_path.endswith('.sqlite'):
        return True
    
    updater = SQLiteDBUpdater(db_path, parent)
    return updater.check_and_update_database()