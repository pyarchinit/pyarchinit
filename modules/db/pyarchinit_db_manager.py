#!/usr/bin/python
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

import math
import os
import time
import traceback
import sqlite3
from datetime import datetime
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.PyQt.QtWidgets import QProgressBar, QApplication
from qgis.core import *

import psycopg2
from geoalchemy2 import *
from sqlalchemy import and_, or_, asc, desc, func, select, Table, text
from sqlalchemy.engine import create_engine
from sqlalchemy.event import listen
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from sqlalchemy.sql.schema import MetaData

from modules.db.pyarchinit_db_mapper import US, UT, SITE, PERIODIZZAZIONE, POTTERY, TMA, TMA_MATERIALI, \
    STRUTTURA, SCHEDAIND, INVENTARIO_MATERIALI, DETSESSO, DOCUMENTAZIONE, DETETA, MEDIA, \
    MEDIA_THUMB, MEDIATOENTITY, MEDIAVIEW, TOMBA, CAMPIONI, PYARCHINIT_THESAURUS_SIGLE, \
    INVENTARIO_LAPIDEI, PDF_ADMINISTRATOR, PYUS, PYUSM, PYSITO_POINT, PYSITO_POLYGON, PYQUOTE, PYQUOTEUSM, \
    PYUS_NEGATIVE, PYSTRUTTURE, PYREPERTI, PYINDIVIDUI, PYCAMPIONI, PYTOMBA, PYDOCUMENTAZIONE, PYLINEERIFERIMENTO, \
    PYRIPARTIZIONI_SPAZIALI, PYSEZIONI, POTTERY_EMBEDDING_METADATA, FAUNA
from modules.db.pyarchinit_db_update import DB_update
from modules.db.pyarchinit_utility import Utility
from modules.utility.pyarchinit_OS_utility import Pyarchinit_OS_Utility


class DbConnectionSingleton:
    """Singleton per gestire connessioni database globali"""
    _instances = {}
    
    @classmethod
    def get_instance(cls, conn_str):
        """Ottieni istanza singleton per una specifica connection string"""
        import datetime
        log_file = '/Users/enzo/pyarchinit_debug.log'
        def log_debug(msg):
            try:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(f"[{timestamp}] [SINGLETON] {msg}\n")
                    f.flush()
            except:
                pass
        
        if conn_str not in cls._instances:
            log_debug(f"Creating NEW singleton instance for conn_str")
            cls._instances[conn_str] = Pyarchinit_db_management(conn_str, _singleton=True)
            cls._instances[conn_str].connection()
        else:
            log_debug(f"Reusing EXISTING singleton instance")
        return cls._instances[conn_str]
    
    @classmethod
    def clear_instances(cls):
        """Pulisci tutte le istanze (per reset/disconnessione)"""
        for instance in cls._instances.values():
            try:
                if hasattr(instance, 'engine') and instance.engine:
                    instance.engine.dispose()
            except:
                pass
        cls._instances.clear()


def get_db_manager(conn_str, use_singleton=True):
    """
    Factory function per ottenere DB Manager
    Se use_singleton=True usa il singleton (per performance)
    Se use_singleton=False crea nuova istanza (per operazioni specifiche)
    """
    if use_singleton:
        return DbConnectionSingleton.get_instance(conn_str)
    else:
        return Pyarchinit_db_management(conn_str)


class Pyarchinit_db_management(object):
    metadata = ''
    engine = ''
    boolean = False  # SQLAlchemy echo parameter (True for debug SQL output)
    Session = None  # Session factory
    _query_cache = {}  # Cache per query frequenti

    if os.name == 'posix':
        boolean = True
    elif os.name == 'nt':
        boolean = True
    L = QgsSettings().value("locale/userLocale", "it", type=str)[:2]

    def __init__(self, c, _singleton=False):
        self.conn_str = c
        self.Session = None
        self.engine = None
        self.metadata = None
        self._is_singleton = _singleton
        self._local_cache = {}  # Cache locale per questa istanza
        
    def _get_cache_key(self, method_name, *args, **kwargs):
        """Genera una chiave di cache per metodo e parametri"""
        import hashlib
        key_data = f"{method_name}_{str(args)}_{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_cached_result(self, cache_key, cache_timeout=300):
        """Ottieni risultato dalla cache se valido (default 5 minuti)"""
        if cache_key in self._local_cache:
            result, timestamp = self._local_cache[cache_key]
            import time
            if time.time() - timestamp < cache_timeout:
                return result
        return None
    
    def _set_cached_result(self, cache_key, result):
        """Salva risultato nella cache"""
        import time
        self._local_cache[cache_key] = (result, time.time())

    def _execute_sql(self, sql, **params):
        """SQLAlchemy 2.0 compatible execute wrapper.

        Replaces engine.execute() which was removed in SQLAlchemy 2.0.
        Uses connection context manager for proper resource handling.

        Args:
            sql: SQL string or text() object
            **params: Named parameters to bind to the query

        Returns:
            ResultWrapper object with fetchone(), fetchall(), scalar() methods
        """
        class ResultWrapper:
            """Wrapper to maintain compatibility with old engine.execute() API"""
            def __init__(self, rows):
                self._rows = list(rows) if rows else []
                self._index = 0

            def fetchall(self):
                return self._rows

            def fetchone(self):
                if self._index < len(self._rows):
                    row = self._rows[self._index]
                    self._index += 1
                    return row
                return None

            def scalar(self):
                if self._rows:
                    first_row = self._rows[0]
                    if first_row:
                        return first_row[0]
                return None

            def __iter__(self):
                return iter(self._rows)

        # Convert string to text if needed
        if isinstance(sql, str):
            sql = text(sql)

        # Determine if this is a write operation (DDL/DML)
        sql_str = str(sql).strip().upper()
        is_write = sql_str.startswith(('INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 'TRUNCATE'))

        try:
            if is_write:
                # Use begin() for auto-commit on write operations
                with self.engine.begin() as conn:
                    result = conn.execute(sql, params) if params else conn.execute(sql)
                    try:
                        rows = result.fetchall()
                        return ResultWrapper(rows)
                    except:
                        return ResultWrapper([])
            else:
                # Use connect() for read operations
                with self.engine.connect() as conn:
                    result = conn.execute(sql, params) if params else conn.execute(sql)
                    try:
                        rows = result.fetchall()
                        return ResultWrapper(rows)
                    except:
                        return ResultWrapper([])
        except Exception as e:
            # Log the error and re-raise
            import traceback
            print(f"SQL execution error: {e}\nSQL: {sql}\nParams: {params}")
            traceback.print_exc()
            raise

    def load_spatialite(self,dbapi_conn, connection_record):
        dbapi_conn.enable_load_extension(True)

        if Pyarchinit_OS_Utility.isWindows()== True:
            dbapi_conn.load_extension('mod_spatialite.dll')

        elif Pyarchinit_OS_Utility.isMac()== True:
            # macOS hardened apps require full path to extension
            spatialite_paths = [
                '/opt/homebrew/lib/mod_spatialite.dylib',
                '/usr/local/lib/mod_spatialite.dylib',
                '/opt/local/lib/mod_spatialite.dylib',
            ]
            loaded = False
            for path in spatialite_paths:
                if os.path.exists(path):
                    try:
                        dbapi_conn.load_extension(path)
                        loaded = True
                        break
                    except Exception:
                        continue
            if not loaded:
                # Fallback - try without path (may work in some environments)
                dbapi_conn.load_extension('mod_spatialite')
        else:
            dbapi_conn.load_extension('mod_spatialite.so')
        
        # Enable foreign keys for SQLite
        dbapi_conn.execute("PRAGMA foreign_keys=ON")




    def connection(self):
        # Add debug logging
        import datetime
        log_file = '/Users/enzo/pyarchinit_debug.log'
        def log_debug(msg):
            try:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(f"[{timestamp}] [DB_MANAGER] {msg}\n")
                    f.flush()
            except:
                pass
        
        # Se è un singleton e già connesso, non rifarlo
        log_debug(f"connection() called - singleton: {getattr(self, '_is_singleton', False)}, has_engine: {hasattr(self, 'engine')}, engine_valid: {bool(getattr(self, 'engine', None))}")
        
        if getattr(self, '_is_singleton', False) and hasattr(self, 'engine') and self.engine:
            log_debug("Reusing existing singleton connection")
            return True
            
        # Continue with new connection
        log_debug("connection() method started")
        conn = None
        test = True

        try:
            if self.conn_str is None:
                raise Exception("Connection string is not configured")
            log_debug(f"Connection string: {self.conn_str[:50]}...")
            test_conn = self.conn_str.find("sqlite")
            if test_conn == 0:
                log_debug("Creating SQLite engine")
                
                # Check and update SQLite database if needed
                db_path = self.conn_str.replace('sqlite:///', '')
                if os.path.exists(db_path):
                    log_debug(f"Checking SQLite database for updates: {db_path}")
                    try:
                        from .sqlite_db_updater import check_and_update_sqlite_db
                        # Run updater silently (no parent widget for background operation)
                        if check_and_update_sqlite_db(db_path):
                            log_debug("SQLite database updated successfully")
                        else:
                            log_debug("SQLite database update not needed or failed")
                    except Exception as e:
                        log_debug(f"Error checking SQLite database updates: {e}")
                        # Continue anyway - don't block connection
                
                # SQLite doesn't support connection pooling parameters
                self.engine = create_engine(
                    self.conn_str, 
                    echo=self.boolean
                )
                listen(self.engine, 'connect', self.load_spatialite)
            else:
                log_debug("Creating PostgreSQL engine")
                # Ottimizzazioni specifiche per database remoti
                is_remote_db = any(host in self.conn_str for host in [
                    'supabase.com', 'amazonaws.com', 'azure.com', 'cloud.google.com',
                    'heroku.com', 'planetscale.com', 'neon.tech'
                ])
                
                if is_remote_db:
                    # Configurazione ottimizzata per database remoti/cloud
                    self.engine = create_engine(
                        self.conn_str, 
                        echo=self.boolean,
                        pool_size=10,           # Pool più grande per connessioni remote
                        max_overflow=20,        # Più overflow per latenza
                        pool_timeout=60,        # Timeout più lungo per connessioni remote
                        pool_recycle=1800,      # Ricrea connessioni ogni 30 min
                        pool_pre_ping=True,     # Verifica connessioni prima dell'uso
                        connect_args={
                            "connect_timeout": 10,
                            "application_name": "PyArchInit",
                            "options": "-c statement_timeout=30000"  # 30 sec timeout per query
                        }
                    )
                else:
                    # Configurazione per database locali
                    self.engine = create_engine(
                        self.conn_str, 
                        echo=self.boolean,
                        pool_size=5,
                        max_overflow=10,
                        pool_timeout=30,
                        pool_recycle=3600,
                        pool_pre_ping=True
                    )
                
                # Check and update PostgreSQL database if needed
                # Always run for PostgreSQL databases (local or remote)
                log_debug("Checking PostgreSQL database for updates")
                try:
                    from .postgres_db_updater import check_and_update_postgres_db
                    if check_and_update_postgres_db(self):
                        log_debug("PostgreSQL database updated successfully")
                    else:
                        log_debug("PostgreSQL database update not needed or failed")
                except Exception as e:
                    log_debug(f"Error checking PostgreSQL database updates: {e}")
                    # Continue anyway - don't block connection

            log_debug("Creating metadata")
            self.metadata = MetaData()
            
            # Create session factory once
            log_debug("Creating session factory")
            self.Session = sessionmaker(bind=self.engine, autoflush=False, autocommit=False)
            
            log_debug("Connecting to database")
            conn = self.engine.connect()
            log_debug("Connection successful")

        except Exception as e:
            log_debug(f"Connection failed: {e}")
            error_message = f"Error. Problema nella connessione con il db: {e}\nTraceback: {traceback.format_exc()}"
            QMessageBox.warning(None, "Message", error_message, QMessageBox.Ok)
            test = False
        finally:
            if conn:
                log_debug("Closing initial connection")
                conn.close()

        # If connection failed, return early
        if not test:
            log_debug("Connection failed, returning early")
            return test

        # Skip DB_update for remote databases to avoid slow operations
        is_remote_db = any(host in self.conn_str for host in [
            'supabase.com', 'amazonaws.com', 'azure.com', 'cloud.google.com',
            'heroku.com', 'planetscale.com', 'neon.tech'
        ])
        
        if not is_remote_db:
            try:
                log_debug("Starting DB_update")
                db_upd = DB_update(self.conn_str)
                log_debug("Calling update_table()")
                db_upd.update_table()
                log_debug("DB_update completed")
            except Exception as e:
                error_message = f"Error. problema nell' aggiornamento del db: {e}\nTraceback: {traceback.format_exc()}"
                QMessageBox.warning(None, "Message", error_message, QMessageBox.Ok)
                test = False
        else:
            log_debug("Skipping DB_update for remote/cloud database")
        
        # If DB update failed, return early
        if not test:
            log_debug("DB update failed, returning early")
            return test
            
        try:

            # Skip trigger updates for remote databases
            if not is_remote_db:
                # Update triggers for multi-user permission compatibility
                try:
                    log_debug("Starting trigger update check")
                    from .db_updater import DatabaseUpdater
                    updater = DatabaseUpdater(self)
                    updater.check_and_update_triggers()
                    log_debug("Trigger update check completed")
                except Exception as e:
                    log_debug(f"Trigger update check failed (non-critical): {e}")
                
                # After database update, we need to refresh metadata to reflect the changes
                # Only if we have a valid engine
                if hasattr(self, 'engine') and self.engine:
                    # Clear existing metadata if it's a MetaData object
                    if hasattr(self, 'metadata') and hasattr(self.metadata, 'clear'):
                        self.metadata.clear()
                    
                    # Recreate metadata with updated table structures
                    self.metadata = MetaData()
                    
                    # Force metadata to reflect all tables
                    self.metadata.reflect(bind=self.engine)
                
                print("Database metadata refreshed after update")
            else:
                log_debug("Skipping trigger update check for remote/cloud database")
                # For remote databases, skip metadata reflection for faster startup
                # Metadata will be loaded on-demand when needed
                pass
            
        except Exception as e:
            error_message = f"Error. problema nell' aggiornamento del db: {e}\nTraceback: {traceback.format_exc()}"
            QMessageBox.warning(None, "Message", error_message, QMessageBox.Ok)
            test = False
            
        # Force creation of TMA tables
        try:
            self.ensure_tma_tables_exist()
        except Exception as e:
            print(f"Error ensuring TMA tables exist: {e}")

        # Fix macc field for SQLite databases
        try:
            self.fix_macc_field_sqlite()
        except Exception as e:
            print(f"Error fixing macc field: {e}")

        return test
    
    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around a series of operations."""
        if not self.Session:
            raise RuntimeError("Database not connected. Call connection() first.")
        
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def get_session(self):
        """Get a new session - use session_scope() for transactions"""
        if not self.Session:
            raise RuntimeError("Database not connected. Call connection() first.")
        return self.Session()
    
    def ensure_tma_tables_exist(self):
        """Ensure TMA tables are created if they don't exist"""
        try:
            # Import the table structures to trigger their creation
            from modules.db.structures.Tma_table import Tma_table
            from modules.db.structures.Tma_materiali_table import Tma_materiali_table

            # Force metadata creation
            Tma_table.metadata.create_all(self.engine)
            Tma_materiali_table.metadata.create_all(self.engine)

        except Exception as e:
            print(f"Error in ensure_tma_tables_exist: {str(e)}")

    def fix_macc_field_sqlite(self):
        """Fix macc field in tma_materiali_ripetibili table for SQLite databases"""
        # Only run for SQLite databases
        if not self.conn_str.startswith("sqlite"):
            return

        try:
            # Extract database path from connection string
            # Format: sqlite:///path/to/database.sqlite
            db_path = self.conn_str.replace("sqlite:///", "")
            db_name = os.path.basename(db_path)

            QgsMessageLog.logMessage(f"PyArchInit - Checking macc field for database: {db_name}", "PyArchInit", Qgis.Info)

            # Connect directly with sqlite3 to check schema
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Check if table exists
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='tma_materiali_ripetibili'"
            )
            if not cursor.fetchone():
                QgsMessageLog.logMessage(f"PyArchInit - Table tma_materiali_ripetibili does not exist in {db_name}", "PyArchInit", Qgis.Info)
                conn.close()
                return

            # Check macc field properties
            cursor.execute("PRAGMA table_info(tma_materiali_ripetibili)")
            columns = cursor.fetchall()

            macc_info = None
            for col in columns:
                if col[1] == 'macc':  # col[1] is the column name
                    macc_info = col
                    break

            if not macc_info:
                QgsMessageLog.logMessage(f"PyArchInit - Column 'macc' not found in {db_name}", "PyArchInit", Qgis.Info)
                conn.close()
                return

            # Check if macc is NOT NULL (col[3] is the notnull flag)
            if macc_info[3] == 0:
                QgsMessageLog.logMessage(f"PyArchInit - Column 'macc' is already nullable in {db_name}. No changes needed.", "PyArchInit", Qgis.Info)
                conn.close()
                return

            QgsMessageLog.logMessage(f"PyArchInit - Column 'macc' is NOT NULL in {db_name}. Starting fix...", "PyArchInit", Qgis.Warning)

            # Begin transaction
            cursor.execute("BEGIN TRANSACTION")

            try:
                # Check and drop the view if it exists
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='view' AND name='pyarchinit_uscaratterizzazioni_view'"
                )
                if cursor.fetchone():
                    cursor.execute("DROP VIEW IF EXISTS pyarchinit_uscaratterizzazioni_view")
                    QgsMessageLog.logMessage(f"PyArchInit - Dropped view pyarchinit_uscaratterizzazioni_view in {db_name}", "PyArchInit", Qgis.Info)

                # Create temporary table with correct schema
                cursor.execute("""
                    CREATE TABLE tma_materiali_ripetibili_temp (
                        id             INTEGER PRIMARY KEY,
                        id_tma         INTEGER NOT NULL
                                       REFERENCES tma_materiali_archeologici(id)
                                       ON UPDATE NO ACTION
                                       ON DELETE NO ACTION,
                        madi           TEXT,
                        macc           TEXT,  -- Now nullable
                        macl           TEXT,
                        macp           TEXT,
                        macd           TEXT,
                        cronologia_mac TEXT,
                        macq           TEXT,
                        peso           FLOAT,
                        created_at     TEXT,
                        updated_at     TEXT,
                        created_by     TEXT,
                        updated_by     TEXT
                    )
                """)

                # Copy data from original table
                cursor.execute("""
                    INSERT INTO tma_materiali_ripetibili_temp
                    SELECT * FROM tma_materiali_ripetibili
                """)

                # Drop original table
                cursor.execute("DROP TABLE tma_materiali_ripetibili")

                # Rename temp table to original name
                cursor.execute(
                    "ALTER TABLE tma_materiali_ripetibili_temp RENAME TO tma_materiali_ripetibili"
                )

                # Commit transaction
                cursor.execute("COMMIT")
                QgsMessageLog.logMessage(f"PyArchInit - Successfully fixed 'macc' field to accept NULL values in {db_name}", "PyArchInit", Qgis.Success)

            except Exception as e:
                cursor.execute("ROLLBACK")
                QgsMessageLog.logMessage(f"PyArchInit - Error during migration in {db_name}, rolled back: {str(e)}", "PyArchInit", Qgis.Critical)
                raise

            finally:
                conn.close()

        except Exception as e:
            QgsMessageLog.logMessage(f"PyArchInit - Error in fix_macc_field_sqlite: {str(e)}", "PyArchInit", Qgis.Critical)
            # Don't raise the error to avoid blocking the connection

        # insert statement

    def insert_pottery_values(self, *arg):
        """Istanzia la classe POTTERY da pyarchinit_db_mapper"""
        pottery = POTTERY(arg[0],
                  arg[1],
                  arg[2],
                  arg[3],
                  arg[4],
                  arg[5],
                  arg[6],
                  arg[7],
                  arg[8],
                  arg[9],
                  arg[10],
                  arg[11],
                  arg[12],
                  arg[13],
                  arg[14],
                  arg[15],
                  arg[16],
                  arg[17],
                  arg[18],
                  arg[19],
                  arg[20],
                  arg[21],
                  arg[22],
                  arg[23],
                  arg[24],
                  arg[25],
                  arg[26],
                  arg[27],
                  arg[28],
                  arg[29],
                  arg[30],
                  arg[31],
                  arg[32],
                  arg[33],
                  arg[34],
                  arg[35])

        return pottery

    # ============== POTTERY EMBEDDING METADATA METHODS ==============

    def insert_pottery_embedding_metadata(self, id_rep, id_media, image_hash, model_name, search_type, embedding_version='1.0'):
        """Insert a new pottery embedding metadata record"""
        from datetime import datetime
        metadata = POTTERY_EMBEDDING_METADATA(
            None,  # id_embedding - auto generated
            id_rep,
            id_media,
            image_hash,
            model_name,
            search_type,
            embedding_version,
            datetime.now()
        )
        return metadata

    def get_pottery_embedding_metadata(self, id_media, model_name, search_type):
        """Get embedding metadata for a specific media/model/search_type combination"""
        session = self.Session()
        try:
            result = session.query(POTTERY_EMBEDDING_METADATA).filter(
                POTTERY_EMBEDDING_METADATA.id_media == id_media,
                POTTERY_EMBEDDING_METADATA.model_name == model_name,
                POTTERY_EMBEDDING_METADATA.search_type == search_type
            ).first()
            return result
        except Exception as e:
            print(f"Error getting embedding metadata: {e}")
            return None
        finally:
            session.close()

    def get_all_pottery_embedding_metadata(self, model_name=None, search_type=None):
        """Get all embedding metadata, optionally filtered by model and search type"""
        session = self.Session()
        try:
            query = session.query(POTTERY_EMBEDDING_METADATA)
            if model_name:
                query = query.filter(POTTERY_EMBEDDING_METADATA.model_name == model_name)
            if search_type:
                query = query.filter(POTTERY_EMBEDDING_METADATA.search_type == search_type)
            return query.all()
        except Exception as e:
            print(f"Error getting all embedding metadata: {e}")
            return []
        finally:
            session.close()

    def get_unindexed_pottery_images(self, model_name, search_type):
        """Get pottery images that don't have embeddings for the specified model/search_type"""
        session = self.Session()
        try:
            # Get all pottery with media links
            sql = """
                SELECT DISTINCT p.id_rep, m.id_media, m.filepath
                FROM pottery_table p
                JOIN media_to_entity_table mte ON p.id_rep = mte.id_entity AND mte.entity_type = 'CERAMICA'
                JOIN media_table m ON mte.id_media = m.id_media
                WHERE m.mediatype = 'image'
                AND NOT EXISTS (
                    SELECT 1 FROM pottery_embeddings_metadata_table pem
                    WHERE pem.id_media = m.id_media
                    AND pem.model_name = :model_name
                    AND pem.search_type = :search_type
                )
            """
            result = session.execute(sql, {'model_name': model_name, 'search_type': search_type})
            return [{'id_rep': row[0], 'id_media': row[1], 'filepath': row[2]} for row in result]
        except Exception as e:
            print(f"Error getting unindexed pottery images: {e}")
            return []
        finally:
            session.close()

    def get_all_pottery_with_images(self):
        """Get all pottery records that have associated images.
        Returns path_resize from media_thumb_table (relative filename to be joined with THUMB_RESIZE from config)
        """
        session = self.Session()
        try:
            sql = """
                SELECT p.id_rep, p.id_number, p.sito, p.area, p.us, p.anno,
                       p.form, p.specific_form, p.specific_shape, p.ware,
                       p.exdeco, p.intdeco, p.fabric,
                       m.id_media, mt.path_resize as filepath, m.filename
                FROM pottery_table p
                JOIN media_to_entity_table mte ON p.id_rep = mte.id_entity AND mte.entity_type = 'CERAMICA'
                JOIN media_table m ON mte.id_media = m.id_media
                LEFT JOIN media_thumb_table mt ON m.id_media = mt.id_media
                WHERE m.mediatype = 'image' AND mt.path_resize IS NOT NULL
                ORDER BY p.id_rep
            """
            result = session.execute(sql)
            return [dict(row) for row in result]
        except Exception as e:
            print(f"Error getting pottery with images: {e}")
            return []
        finally:
            session.close()

    def delete_pottery_embedding_metadata(self, id_media, model_name=None, search_type=None):
        """Delete embedding metadata for a media item"""
        session = self.Session()
        try:
            query = session.query(POTTERY_EMBEDDING_METADATA).filter(
                POTTERY_EMBEDDING_METADATA.id_media == id_media
            )
            if model_name:
                query = query.filter(POTTERY_EMBEDDING_METADATA.model_name == model_name)
            if search_type:
                query = query.filter(POTTERY_EMBEDDING_METADATA.search_type == search_type)
            deleted = query.delete()
            session.commit()
            return deleted
        except Exception as e:
            print(f"Error deleting embedding metadata: {e}")
            session.rollback()
            return 0
        finally:
            session.close()

    def count_pottery_embeddings(self, model_name=None, search_type=None):
        """Count total embeddings, optionally by model/search_type"""
        session = self.Session()
        try:
            query = session.query(POTTERY_EMBEDDING_METADATA)
            if model_name:
                query = query.filter(POTTERY_EMBEDDING_METADATA.model_name == model_name)
            if search_type:
                query = query.filter(POTTERY_EMBEDDING_METADATA.search_type == search_type)
            return query.count()
        except Exception as e:
            print(f"Error counting embeddings: {e}")
            return 0
        finally:
            session.close()

    def get_pottery_by_id_rep(self, id_rep):
        """Get a single pottery record by id_rep"""
        session = self.Session()
        try:
            return session.query(POTTERY).filter(POTTERY.id_rep == id_rep).first()
        except Exception as e:
            print(f"Error getting pottery by id_rep: {e}")
            return None
        finally:
            session.close()

    def get_pottery_image_path(self, id_rep):
        """Get the first image path_resize for a pottery record (relative filename)"""
        session = self.Session()
        try:
            sql = """
                SELECT mt.path_resize
                FROM pottery_table p
                JOIN media_to_entity_table mte ON p.id_rep = mte.id_entity AND mte.entity_type = 'CERAMICA'
                JOIN media_table m ON mte.id_media = m.id_media
                LEFT JOIN media_thumb_table mt ON m.id_media = mt.id_media
                WHERE p.id_rep = :id_rep AND m.mediatype = 'image' AND mt.path_resize IS NOT NULL
                LIMIT 1
            """
            result = session.execute(sql, {'id_rep': id_rep}).fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"Error getting pottery image path: {e}")
            return None
        finally:
            session.close()

    def get_image_path_by_media_id(self, media_id):
        """Get image path_resize by media_id (for similarity search results)"""
        session = self.Session()
        try:
            sql = """
                SELECT mt.path_resize
                FROM media_thumb_table mt
                WHERE mt.id_media = :media_id AND mt.path_resize IS NOT NULL
                LIMIT 1
            """
            result = session.execute(sql, {'media_id': media_id}).fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"Error getting image path by media_id: {e}")
            return None
        finally:
            session.close()

    def get_all_pottery_images(self, id_rep):
        """Get ALL image paths for a pottery record (for multi-image similarity search)"""
        session = self.Session()
        try:
            sql = """
                SELECT m.id_media, mt.path_resize, m.filename
                FROM pottery_table p
                JOIN media_to_entity_table mte ON p.id_rep = mte.id_entity AND mte.entity_type = 'CERAMICA'
                JOIN media_table m ON mte.id_media = m.id_media
                LEFT JOIN media_thumb_table mt ON m.id_media = mt.id_media
                WHERE p.id_rep = :id_rep AND m.mediatype = 'image' AND mt.path_resize IS NOT NULL
            """
            results = session.execute(sql, {'id_rep': id_rep}).fetchall()
            return [{'id_media': r[0], 'path_resize': r[1], 'filename': r[2]} for r in results]
        except Exception as e:
            print(f"Error getting all pottery images: {e}")
            return []
        finally:
            session.close()

    # ============== END POTTERY EMBEDDING METADATA METHODS ==============

    def insert_pyus(self, *arg):
        pyus = PYUS(arg[0],
                arg[1],
                arg[2],
                arg[3],
                arg[4],
                arg[5],
                arg[6],
                arg[7],
                arg[8],
                arg[9],
                arg[10],
                arg[11],
                arg[12],
                arg[13])
        return pyus
    def insert_pyusm(self, *arg):
        pyusm = PYUSM(arg[0],
                arg[1],
                arg[2],
                arg[3],
                arg[4],
                arg[5],
                arg[6],
                arg[7],
                arg[8],
                arg[9],
                arg[10],
                arg[11],
                arg[12],
                arg[13])
        return pyusm
    def insert_pysito_point(self, *arg):
        pysito_point = PYSITO_POINT(arg[0],
                arg[1],
                arg[2])
        return pysito_point
    
    
    def insert_pysito_polygon(self, *arg):
        pysito_polygon = PYSITO_POLYGON(arg[0],
                arg[1],
                arg[2])
        return pysito_polygon
        
    def insert_pyquote(self, *arg):
        pyquote = PYQUOTE(arg[0],
                arg[1],
                arg[2],
                arg[3],
                arg[4],
                arg[5],
                arg[6],
                arg[7],
                arg[8],
                arg[9],
                arg[10])
        return pyquote    
    def insert_pyquote_usm(self, *arg):
        pyquote_usm = PYQUOTEUSM(arg[0],
                arg[1],
                arg[2],
                arg[3],
                arg[4],
                arg[5],
                arg[6],
                arg[7],
                arg[8],
                arg[9],
                arg[10])
        return pyquote_usm    
    def insert_pyus_negative(self, *arg):
        pyus_negative = PYUS_NEGATIVE(arg[0],
                arg[1],
                arg[2],
                arg[3],
                arg[4],
                arg[5],
                arg[6])
        return pyus_negative
    
    def insert_pystrutture(self, *arg):
        pystrutture = PYSTRUTTURE(arg[0],
                arg[1],
                arg[2],
                arg[3],
                arg[4],
                arg[5],
                arg[6],
                arg[7],
                arg[8],
                arg[9],
                arg[10],
                arg[11])
        return pystrutture
    
    def insert_pyreperti(self, *arg):
        pyreperti = PYREPERTI(arg[0],
                arg[1],
                arg[2],
                arg[3],
                arg[4])
        return pyreperti
    
    def insert_pyindividui(self, *arg):
        pyindividui = PYINDIVIDUI(arg[0],
                arg[1],
                arg[2],
                arg[3],
                arg[4],
                arg[5])
        return pyindividui
    
    def insert_pycampioni(self, *arg):
        pycampioni = PYCAMPIONI(arg[0],
                arg[1],
                arg[2],
                arg[3],
                arg[4],
                arg[5],
                arg[6],
                arg[7],
                arg[8])
        return pycampioni
    
    def insert_pytomba(self, *arg):
        pytomba = PYTOMBA(arg[0],
                arg[1],
                arg[2],
                arg[3])
        return pytomba
    
    def insert_pydocumentazione(self, *arg):
        pydocumentazione = PYDOCUMENTAZIONE(arg[0],
                arg[1],
                arg[2],
                arg[3],
                arg[4],
                arg[5],
                arg[6])
        return pydocumentazione
    
    def insert_pylineeriferimento(self, *arg):
        pylineeriferimento = PYLINEERIFERIMENTO(arg[0],
                arg[1],
                arg[2],
                arg[3],
                arg[4])
        return pylineeriferimento
    
    def insert_pyripartizioni_spaziali(self, *arg):
        pyripartizioni_spaziali = PYRIPARTIZIONI_SPAZIALI(arg[0],
                arg[1],
                arg[2],
                arg[3],
                arg[4],
                arg[5])
        return pyripartizioni_spaziali
    
    def insert_pysezioni(self, *arg):
        pysezioni = PYSEZIONI(arg[0],
                arg[1],
                arg[2],
                arg[3],
                arg[4],
                arg[5],
                arg[6],
                arg[7])
        return pysezioni
    
    
    
    def insert_values(self, *arg):
        """Istanzia la classe US da pyarchinit_db_mapper"""

        us = US(arg[0],
                arg[1],
                arg[2],
                arg[3],
                arg[4],
                arg[5],
                arg[6],
                arg[7],
                arg[8],
                arg[9],
                arg[10],
                arg[11],
                arg[12],
                arg[13],
                arg[14],
                arg[15],
                arg[16],
                arg[17],
                arg[18],
                arg[19],
                arg[20],
                arg[21],
                arg[22],
                arg[23],
                arg[24],
                arg[25],
                arg[26],
                arg[27],
                arg[28],
                arg[29],
                arg[30],
                arg[31],
                arg[32],
                arg[33],
                arg[34],
                arg[35],
                arg[36],
                arg[37],
                arg[38],
                arg[39],
                arg[40],
                arg[41],
                arg[42],
                arg[43],
                arg[44],
                arg[45],
                arg[46],
                arg[47],
                arg[48],
                arg[49],
                arg[50],
                arg[51],    # 51 campi aggiunti per archeo 3.0 e allineamento ICCD
                arg[52],
                arg[53],
                arg[54],
                arg[55],
                arg[56],
                arg[57],
                arg[58],
                arg[59],
                arg[60],
                arg[61],
                arg[62],
                arg[63],
                arg[64],
                arg[65],
                arg[66],
                arg[67],
                arg[68],
                arg[69],
                arg[70],
                arg[71],
                arg[72],
                arg[73],
                arg[74],
                arg[75],
                arg[76],
                arg[77],
                arg[78],
                arg[79],
                arg[80],
                arg[81],
                arg[82],
                arg[83],
                arg[84],
                arg[85],
                arg[86],
                arg[87],
                arg[88],
                arg[89],
                arg[90],
                arg[91],
                arg[92],
                arg[93],
                arg[94],
                arg[95],
                arg[96],
                arg[97],
                arg[98],
                arg[99],
                arg[100],
                arg[101],
                arg[102],
                arg[103],
                arg[104],
                arg[105],
                arg[106],
                arg[107],
                arg[108],
                arg[109],
                arg[110],
                arg[111],
                arg[112],
                arg[113],
                arg[114],
                arg[115],
                arg[116],
                )

        return us

    def insert_ut_values(self, *arg):
        """Istanzia la classe UT da pyarchinit_db_mapper"""

        ut = UT(arg[0],
                arg[1],
                arg[2],
                arg[3],
                arg[4],
                arg[5],
                arg[6],
                arg[7],
                arg[8],
                arg[9],
                arg[10],
                arg[11],
                arg[12],
                arg[13],
                arg[14],
                arg[15],
                arg[16],
                arg[17],
                arg[18],
                arg[19],
                arg[20],
                arg[21],
                arg[22],
                arg[23],
                arg[24],
                arg[25],
                arg[26],
                arg[27],
                arg[28],
                arg[29],
                arg[30],
                arg[31],
                arg[32],
                arg[33],
                arg[34],
                arg[35],
                arg[36],
                arg[37],
                arg[38],
                arg[39],
                arg[40],
                arg[41],
                # New survey fields (v4.9.21+)
                arg[42] if len(arg) > 42 else None,  # visibility_percent
                arg[43] if len(arg) > 43 else '',    # vegetation_coverage
                arg[44] if len(arg) > 44 else '',    # gps_method
                arg[45] if len(arg) > 45 else None,  # coordinate_precision
                arg[46] if len(arg) > 46 else '',    # survey_type
                arg[47] if len(arg) > 47 else '',    # surface_condition
                arg[48] if len(arg) > 48 else '',    # accessibility
                arg[49] if len(arg) > 49 else 0,     # photo_documentation
                arg[50] if len(arg) > 50 else '',    # weather_conditions
                arg[51] if len(arg) > 51 else '',    # team_members
                arg[52] if len(arg) > 52 else '')    # foglio_catastale

        return ut

    def insert_site_values(self, *arg):
        """Istanzia la classe SITE da pyarchinit_db_mapper"""
        sito = SITE(arg[0],
                    arg[1],
                    arg[2],
                    arg[3],
                    arg[4],
                    arg[5],
                    arg[6],
                    arg[7],
                    arg[8],
                    arg[9])

        return sito

    def insert_periodizzazione_values(self, *arg):
        """Istanzia la classe Periodizzazione da pyarchinit_db_mapper"""
        periodizzazione = PERIODIZZAZIONE(arg[0],
                                          arg[1],
                                          arg[2],
                                          arg[3],
                                          arg[4],
                                          arg[5],
                                          arg[6],
                                          arg[7],
                                          arg[8])

        return periodizzazione

    def _convert_empty_to_none(self, value, field_type='text'):
        """Convert empty strings to None for numeric fields"""
        if field_type in ['integer', 'bigint', 'numeric', 'float']:
            if value == '' or value == '""' or (isinstance(value, str) and value.strip() == ''):
                return None
            if value is None:
                return None
            try:
                if field_type in ['integer', 'bigint']:
                    return int(value) if value != '' else None
                elif field_type in ['numeric', 'float']:
                    return float(value) if value != '' else None
            except (ValueError, TypeError):
                return None
        else:
            return value if value is not None else ''

    def insert_values_reperti(self, *arg):
        """Istanzia la classe Reperti da pyarchinit_db_mapper"""
        inventario_materiali = INVENTARIO_MATERIALI(
            arg[0],  # id_invmat
            arg[1],  # sito
            arg[2],  # numero_inventario
            arg[3],  # tipo_reperto
            arg[4],  # criterio_schedatura
            arg[5],  # definizione
            arg[6],  # descrizione
            arg[7],  # area (now TEXT)
            arg[8],  # us (now TEXT)
            arg[9],  # lavato
            arg[10],  # nr_cassa (now TEXT)
            arg[11],  # luogo_conservazione
            arg[12],  # stato_conservazione
            arg[13],  # datazione_reperto
            arg[14],  # elementi_reperto
            arg[15],  # misurazioni
            arg[16],  # rif_biblio
            arg[17],  # tecnologie
            self._convert_empty_to_none(arg[18], 'integer'),  # forme_minime
            self._convert_empty_to_none(arg[19], 'integer'),  # forme_massime
            self._convert_empty_to_none(arg[20], 'integer'),  # totale_frammenti
            arg[21],  # corpo_ceramico
            arg[22],  # rivestimento
            self._convert_empty_to_none(arg[23], 'float'),  # diametro_orlo
            self._convert_empty_to_none(arg[24], 'float'),  # peso
            arg[25],  # tipo
            self._convert_empty_to_none(arg[26], 'float'),  # eve_orlo
            arg[27],  # repertato
            arg[28],  # diagnostico
            self._convert_empty_to_none(arg[29], 'bigint'),  # n_reperto
            arg[30],  # tipo_contenitore
            arg[31],  # struttura
            self._convert_empty_to_none(arg[32], 'integer'),  # years
            arg[33] if len(arg) > 33 else None,  # schedatore
            arg[34] if len(arg) > 34 else None,  # date_scheda
            arg[35] if len(arg) > 35 else None,  # punto_rinv
            arg[36] if len(arg) > 36 else None,  # negativo_photo
            arg[37] if len(arg) > 37 else None,  # diapositiva
            self._convert_empty_to_none(arg[38], 'float') if len(arg) > 38 else None,  # quota_usm
            arg[39] if len(arg) > 39 else None,  # unita_misura_quota
            arg[40] if len(arg) > 40 else None,  # photo_id
            arg[41] if len(arg) > 41 else None   # drawing_id
        )

        return inventario_materiali

    def insert_struttura_values(self, *arg):
        """Istanzia la classe Struttura da pyarchinit_db_mapper"""
        struttura = STRUTTURA(arg[0],
                              arg[1],
                              arg[2],
                              arg[3],
                              arg[4],
                              arg[5],
                              arg[6],
                              arg[7],
                              arg[8],
                              arg[9],
                              arg[10],
                              arg[11],
                              arg[12],
                              arg[13],
                              arg[14],
                              arg[15],
                              arg[16],
                              arg[17])

        return struttura

    def insert_values_ind(self, *arg):
        """Istanzia la classe SCHEDAIND da pyarchinit_db_mapper"""
        schedaind = SCHEDAIND(arg[0],
                              arg[1],
                              arg[2],
                              arg[3],
                              arg[4],
                              arg[5],
                              arg[6],
                              arg[7],
                              arg[8],
                              arg[9],
                              arg[10],
                              arg[11],
                              arg[12],
                              arg[13],
                              arg[14],
                              arg[15],
                              arg[16],
                              arg[17],
                              arg[18],
                              arg[19],
                              arg[20],
                              arg[21],
                              arg[22],
                              arg[23])

        return schedaind

    def insert_values_detsesso(self, *arg):
        """Istanzia la classe DETSESSO da pyarchinit_db_mapper"""
        detsesso = DETSESSO(arg[0],
                            arg[1],
                            arg[2],
                            arg[3],
                            arg[4],
                            arg[5],
                            arg[6],
                            arg[7],
                            arg[8],
                            arg[9],
                            arg[10],
                            arg[11],
                            arg[12],
                            arg[13],
                            arg[14],
                            arg[15],
                            arg[16],
                            arg[17],
                            arg[18],
                            arg[19],
                            arg[20],
                            arg[21],
                            arg[22],
                            arg[23],
                            arg[24],
                            arg[25],
                            arg[26],
                            arg[27],
                            arg[28],
                            arg[29],
                            arg[30],
                            arg[31],
                            arg[32],
                            arg[33],
                            arg[34],
                            arg[35],
                            arg[36],
                            arg[37],
                            arg[38],
                            arg[39],
                            arg[40],
                            arg[41],
                            arg[42],
                            arg[43],
                            arg[44],
                            arg[45],
                            arg[46],
                            arg[47],
                            arg[48],
                            arg[49],
                            arg[50],
                            arg[51],
                            arg[52],
                            arg[53])

        return detsesso

    def insert_values_deteta(self, *arg):
        """Istanzia la classe DETETA da pyarchinit_db_mapper"""
        deteta = DETETA(arg[0],
                        arg[1],
                        arg[2],
                        arg[3],
                        arg[4],
                        arg[5],
                        arg[6],
                        arg[7],
                        arg[8],
                        arg[9],
                        arg[10],
                        arg[11],
                        arg[12],
                        arg[13],
                        arg[14],
                        arg[15],
                        arg[16],
                        arg[17],
                        arg[18],
                        arg[19],
                        arg[20],
                        arg[21],
                        arg[22],
                        arg[23],
                        arg[24],
                        arg[25],
                        arg[26],
                        arg[27],
                        arg[28],
                        arg[29],
                        arg[30],
                        arg[31],
                        arg[32],
                        arg[33],
                        arg[34],
                        arg[35],
                        arg[36],
                        arg[37],
                        arg[38],
                        arg[39],
                        arg[40],
                        arg[41],
                        arg[42],
                        arg[43],
                        arg[44],
                        arg[45],
                        arg[46],
                        arg[47],
                        arg[48],
                        arg[49],
                        arg[50],
                        arg[51],
                        arg[52],
                        arg[53],
                        arg[54],
                        arg[55],
                        arg[56])

        return deteta

    def insert_media_values(self, *arg):
        """Istanzia la classe MEDIA da pyarchinit_db_mapper"""
        media = MEDIA(arg[0],
                      arg[1],
                      arg[2],
                      arg[3],
                      arg[4],
                      arg[5],
                      arg[6])

        return media

    def insert_mediathumb_values(self, *arg):
        """Istanzia la classe MEDIA da pyarchinit_db_mapper"""
        media_thumb = MEDIA_THUMB(arg[0],
                                  arg[1],
                                  arg[2],
                                  arg[3],
                                  arg[4],
                                  arg[5],
                                  arg[6],
                                  arg[7])

        return media_thumb

    def insert_media2entity_values(self, *arg):
        """Istanzia la classe MEDIATOENTITY da pyarchinit_db_mapper"""
        mediatoentity = MEDIATOENTITY(arg[0],
                                      arg[1],
                                      arg[2],
                                      arg[3],
                                      arg[4],
                                      arg[5],
                                      arg[6])

        return mediatoentity

    
    def insert_media2entity_view_values(self, *arg):
        """Istanzia la classe MEDIATOENTITY da pyarchinit_db_mapper"""
        mediaentity_view= MEDIAVIEW(arg[0],
                arg[1],
                arg[2],
                arg[3],
                arg[4],
                arg[5],
                arg[6])

        return mediaentity_view 
    
    def insert_values_tomba(self, *arg):
        """Istanzia la classe TOMBA da pyarchinit_db_mapper"""

        tomba = TOMBA(arg[0],
                              arg[1],
                              arg[2],
                              arg[3],
                              arg[4],
                              arg[5],
                              arg[6],
                              arg[7],
                              arg[8],
                              arg[9],
                              arg[10],
                              arg[11],
                              arg[12],
                              arg[13],
                              arg[14],
                              arg[15],
                              arg[16],
                              arg[17],
                              arg[18],
                              arg[19],
                              arg[20],
                              arg[21],
                              arg[22],
                              arg[23],
                              arg[24],
                              arg[25],)

        return tomba

    def insert_values_campioni(self, *arg):
        """Istanzia la classe CAMPIONI da pyarchinit_db_mapper"""

        campioni = CAMPIONI(arg[0],
                            arg[1],
                            arg[2],
                            arg[3],
                            arg[4],
                            arg[5],
                            arg[6],
                            arg[7],
                            arg[8],
                            arg[9])

        return campioni

    def insert_values_thesaurus(self, *arg):
        """Istanzia la classe PYARCHINIT_THESAURUS_SIGLE da pyarchinit_db_mapper"""

        # Standard format with all required fields
        if len(arg) == 7:
            # Basic format with descrizione
            thesaurus = PYARCHINIT_THESAURUS_SIGLE(
                arg[0],  # id_thesaurus_sigle
                arg[1],  # nome_tabella
                arg[2],  # sigla
                arg[3],  # sigla_estesa
                arg[4],  # descrizione
                arg[5],  # tipologia_sigla
                arg[6]   # lingua
            )
        elif len(arg) >= 8:
            # Extended format with hierarchy fields
            thesaurus = PYARCHINIT_THESAURUS_SIGLE(
                arg[0],  # id_thesaurus_sigle
                arg[1],  # nome_tabella
                arg[2],  # sigla
                arg[3],  # sigla_estesa
                arg[4],  # descrizione
                arg[5],  # tipologia_sigla
                arg[6],  # lingua
                self._convert_empty_to_none(arg[7], 'integer') if len(arg) > 7 else 0,  # order_layer
                self._convert_empty_to_none(arg[8], 'integer') if len(arg) > 8 else None,  # id_parent
                arg[9] if len(arg) > 9 else None,  # parent_sigla
                self._convert_empty_to_none(arg[10], 'integer') if len(arg) > 10 else 0  # hierarchy_level
            )
        else:
            # Handle legacy format or missing descrizione
            raise ValueError(f"Invalid number of arguments for thesaurus: {len(arg)}. Expected at least 7.")

        return thesaurus

    # def insert_values_archeozoology(self, *arg):
        # """Istanzia la classe ARCHEOZOOLOGY da pyarchinit_db_mapper"""

        # archeozoology = ARCHEOZOOLOGY(arg[0],
                                        # arg[1],
                                        # arg[2],
                                        # arg[3],
                                        # arg[4],
                                        # arg[5],
                                        # arg[6],
                                        # arg[7],
                                        # arg[8],
                                        # arg[9],
                                        # arg[10],
                                        # arg[11],
                                        # arg[12],
                                        # arg[13],
                                        # arg[14],
                                        # arg[15],
                                        # arg[16],
                                        # arg[17],
                                        # arg[18],
                                        # arg[19],
                                        # arg[20],
                                        # arg[21],
                                        # arg[22],
                                        # arg[23],
                                        # arg[24],
                                        # arg[25],
                                        # arg[26],
                                        # arg[27],
                                        # arg[28],
                                        # arg[29],
                                        # arg[30])

        # return archeozoology

    def insert_values_Lapidei(self, *arg):
        """Istanzia la classe Inventario_Lapidei da pyarchinit_db_mapper"""

        inventario_lapidei = INVENTARIO_LAPIDEI(arg[0],
                                                arg[1],
                                                arg[2],
                                                arg[3],
                                                arg[4],
                                                arg[5],
                                                arg[6],
                                                arg[7],
                                                arg[8],
                                                arg[9],
                                                arg[10],
                                                arg[11],
                                                arg[12],
                                                arg[13],
                                                arg[14],
                                                arg[15],
                                                arg[16],
                                                arg[17],
                                                arg[18],
                                                arg[19])

        return inventario_lapidei

    def insert_values_documentazione(self, *arg):
        """Istanzia la classe DOCUMENTAZIONE da pyarchinit_db_mapper"""

        documentazione = DOCUMENTAZIONE(arg[0],
                                        arg[1],
                                        arg[2],
                                        arg[3],
                                        arg[4],
                                        arg[5],
                                        arg[6],
                                        arg[7],
                                        arg[8])

        return documentazione

    def insert_pdf_administrator_values(self, *arg):
        """Istanzia la classe PDF_ADMINISTRATOR da pyarchinit_db_mapper"""
        pdf_administrator = PDF_ADMINISTRATOR(arg[0],
                                              arg[1],
                                              arg[2],
                                              arg[3],
                                              arg[4])

        return pdf_administrator

    def insert_campioni_values(self, *arg):
        """Istanzia la classe CAMPIONI da pyarchinit_db_mapper"""
        campioni = CAMPIONI(arg[0],
                            arg[1],
                            arg[2],
                            arg[3],
                            arg[4],
                            arg[5],
                            arg[6],
                            arg[7],
                            arg[8],
                            arg[9])

        return campioni
        
    def insert_tma_values(self, *arg):
        """Istanzia la classe TMA da pyarchinit_db_mapper"""
        tma = TMA(int(arg[0]) if arg[0] else None,  # id - convert to int
                  arg[1],  # sito
                  arg[2],  # area
                  arg[3],  # localita
                  arg[4],  # settore
                  arg[5],  # inventario
                  arg[6],  # ogtm
                  arg[7],  # ldct
                  arg[8],  # ldcn
                  arg[9],  # vecchia_collocazione
                  arg[10], # cassetta
                  arg[11], # scan
                  arg[12], # saggio
                  arg[13], # vano_locus
                  arg[14], # dscd
                  arg[15], # dscu
                  arg[16], # rcgd
                  arg[17], # rcgz
                  arg[18], # aint
                  arg[19], # aind
                  arg[20], # dtzg
                  arg[21], # deso
                  arg[22], # nsc
                  arg[23], # ftap
                  arg[24], # ftan
                  arg[25], # drat
                  arg[26], # dran
                  arg[27], # draa
                  arg[28], # created_at
                  arg[29], # updated_at
                  arg[30], # created_by
                  arg[31]) # updated_by

        return tma

    def insert_tma_materiali_values(self, *arg):
        """Istanzia la classe TMA_MATERIALI da pyarchinit_db_mapper"""
        from modules.db.entities.TMA_MATERIALI import TMA_MATERIALI
        tma_materiali = TMA_MATERIALI(arg[0],  # id
                                     arg[1],  # id_tma
                                     arg[2],  # madi
                                     arg[3],  # macc
                                     arg[4],  # macl
                                     arg[5],  # macp
                                     arg[6],  # macd
                                     arg[7],  # cronologia_mac
                                     arg[8],  # macq
                                     self._convert_empty_to_none(arg[9], 'float'),  # peso
                                     arg[10], # created_at
                                     arg[11], # updated_at
                                     arg[12], # created_by
                                     arg[13]) # updated_by

        return tma_materiali

    def insert_media_to_entity_values(self, *arg):
        """Istanzia la classe MEDIATOENTITY da pyarchinit_db_mapper"""
        mediatoentity = MEDIATOENTITY(arg[0],  # id_mediaToEntity
                                      arg[1],  # id_entity
                                      arg[2],  # entity_type
                                      arg[3],  # table_name
                                      arg[4],  # id_media
                                      arg[5],  # filepath
                                      arg[6]   # media_name
                                      )
        return mediatoentity

    ##  def insert_relationship_check_values(self, *arg):
    ##      """Istanzia la classe RELATIONSHIP_CHECK da pyarchinit_db_mapper"""
    ##      relationship_check = RELATIONSHIP_CHECK(arg[0],
    ##                                              arg[1],
    ##                                              arg[2],
    ##                                              arg[3],
    ##                                              arg[4],
    ##                                              arg[5],
    ##                                              arg[6],
    ##                                              arg[7],
    ##                                              arg[8],
    ##                                              arg[9])
    ##
    ##      return relationship_check


    def execute_sql_create_db(self):
        path = os.path.dirname(__file__)
        rel_path = os.path.join(os.sep, 'query_sql', 'pyarchinit_create_db.sql')
        qyery_sql_path = '{}{}'.format(path, rel_path)
        create = open(qyery_sql_path, "r")
        stringa = create.read()
        create.close()
        self.engine.raw_connection().set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        self.engine.text(stringa).execute()

    def execute_sql_create_spatialite_db(self):
        path = os.path.dirname(__file__)
        rel_path = os.path.join(os.sep, 'query_sql', 'pyarchinit_create_spatialite_db.sql')
        qyery_sql_path = '{}{}'.format(path, rel_path)
        create = open(qyery_sql_path, "r")
        stringa = create.read()
        create.close()

        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()
        session.begin()
        session.execute(stringa)
        session.commit()
        session.close()

    def execute_sql_create_layers(self):
        path = os.path.dirname(__file__)
        rel_path = os.path.join(os.sep, 'query_sql', 'pyarchinit_layers_postgis.sql')
        qyery_sql_path = '{}{}'.format(path, rel_path)
        create = open(qyery_sql_path, "r")
        stringa = create.read()
        create.close()

        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()
        session.begin()
        session.execute(stringa)
        session.commit()
        session.close()

        # query statement

    def execute_sql(self, query_string, params=None):
        """Execute a raw SQL query and return results"""
        try:
            from sqlalchemy import text
            Session = sessionmaker(bind=self.engine)
            session = Session()
            if params:
                result = session.execute(text(query_string), params)
            else:
                result = session.execute(text(query_string))

            # If it's a SELECT query, fetch results
            if query_string.strip().upper().startswith('SELECT'):
                rows = result.fetchall()
                session.close()
                # Return empty list instead of None if no results
                return rows if rows else []
            else:
                # For INSERT/UPDATE/DELETE, commit and return affected rows
                session.commit()
                affected = result.rowcount
                session.close()
                return affected if affected else 0
        except Exception as e:
            print(f"Error executing SQL: {e}")
            if 'session' in locals():
                session.close()
            # Return empty list for SELECT, 0 for other operations
            if query_string.strip().upper().startswith('SELECT'):
                return []
            return 0

    def query(self, n):
        class_name = eval(n)
        # Usa session factory ottimizzata ma mantieni compatibilità
        session = self.get_session()
        try:
            query = session.query(class_name)
            res = query.all()
            return res
        finally:
            session.close()

    def query_limit_offset(self, table_name, filter_text=None, limit=None, offset=None):
        # Usa session factory ottimizzata
        session = self.get_session()
        try:
            # Ottieni la tabella
            table = Table(table_name, MetaData(bind=self.engine), autoload_with=self.engine)

            # Costruisci la query
            query = select(table)

            # Se c'è un testo da filtrare
            if filter_text:
                query = query.where(table.c.media_filename.ilike(f"%{filter_text}%")).order_by(table.c.media_filename)

            # Se c'è un limite e un offset
            if limit is not None and offset is not None:
                query = query.limit(limit).offset(offset)

            # Esegui la query e ottieni i risultati
            records = session.execute(query).fetchall()
            return records
        finally:
            session.close()

    def count_total_images(self, table_name, filter_text=None):
        # Usa session factory ottimizzata
        session = self.get_session()
        try:
            # Ottieni la tabella
            table = Table(table_name, MetaData(bind=self.engine), autoload_with=self.engine)

            # Costruisci la query per ottenere il conteggio totale delle immagini
            query = select(func.count('*')).select_from(table)

            # Se c'è un testo da filtrare
            if filter_text:
                query = query.where(table.c.title.ilike(f"%{filter_text}%"))

            # Esegui la query e ottieni il conteggio
            total_images = session.execute(query).scalar()
            return total_images
        finally:
            session.close()

    def query_bool_us(self, params, table_class):

        u = Utility()
        params = u.remove_empty_items_fr_dict(params)

        # Create a session
        Session = sessionmaker(bind=self.engine)
        session = Session()

        # Start with an empty list of conditions
        conditions = []

        # Iterate over the parameters to create conditions
        for key, value in params.items():
            column = getattr(table_class, key)
            if isinstance(value, str):
                conditions.append(column.like(value))
            else:
                conditions.append(column == value)

        # Construct the query with the conditions
        query = session.query(table_class).filter(and_(*conditions))

        # Execute the query and fetch all results
        res = query.all()

        # Close the session
        session.close()

        return res

    def query_bool_like(self, params, table, join_operator='or'):

        meta = MetaData(bind=self.engine)
        table_to_query = Table(table, meta, autoload_with=self.engine)

        u = Utility()
        params = u.remove_empty_items_fr_dict(params)

        list_keys_values = list(params.items())
        sito_filter = None  # This will hold the 'sito' filter
        filters = []
        for sing_couple_n in range(len(list_keys_values)):
            key, value = list_keys_values[sing_couple_n]
            column = getattr(table_to_query.c, key)
            if key == "settore" or key == "struttura" or key == "quad_par" or key == "ambient" or key == "saggio" or key == "area":
                value_list = value.split(", ")
                filters.append(or_(*[column.ilike(f'%{field_value}%') for field_value in value_list]))
            else:
                if key == 'sito':
                    sito_filter = column.ilike(f'%{value}%')
                else:
                    filters.append(column.ilike(f'%{value}%'))

        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()

        # choose join_operator based on given argument


        join_operator_func = and_ if join_operator == 'and' else or_
        # Add 'sito' filter
        if sito_filter is not None:
            filters.insert(0, sito_filter)

        query = session.query(table_to_query).filter(and_(*[filters.pop(0)]), join_operator_func(*filters))
        # Convert query to a SQL string
        # sql_query_str = str(query.statement.compile(dialect=self.engine.dialect))
        #
        # with open("C:\\Users\\enzoc\\Desktop\\test_import.txt", "w") as t:
        #     t.write(str(sql_query_str))

        # Execute query
        res = query.all()

        session.close()
        return res

    def query_bool_postgres(self, params, table):
        u = Utility()
        params = u.remove_empty_items_fr_dict(params)

        conditions = []
        query_params = {}

        for key, value in params.items():
            if isinstance(value, str):
                conditions.append(text(f"{table}.{key} = :{key}"))
            else:
                conditions.append(text(f"{table}.{key} = :{key}"))
            query_params[key] = value

        try:
            Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
            with Session() as session:
                query = session.query(table).filter(and_(*conditions))
                res = query.params(**query_params).all()
            return res
        except SQLAlchemyError as e:
            print(f"Database error: {str(e)}")
            return []
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return []

    def query_sql(self, query):
        """Execute raw SQL query and return results"""
        try:
            from sqlalchemy import text
            Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=False)
            session = Session()
            result = session.execute(text(query))
            rows = result.fetchall()
            session.commit()
            session.close()
            return rows
        except Exception as e:
            print(f"Error executing SQL: {e}")
            if 'session' in locals():
                session.rollback()
                session.close()
            return None

    def query_bool(self, params, table_class_name):
        # Cache per query_bool (molto usato nelle schede)
        cache_key = self._get_cache_key('query_bool', params, table_class_name)
        cached_result = self._get_cached_result(cache_key, cache_timeout=300)  # 5 minuti
        if cached_result is not None:
            return cached_result
        
        u = Utility()
        params = u.remove_empty_items_fr_dict(params)

        # Handle thesaurus table name compatibility
        if table_class_name == 'PYARCHINIT_THESAURUS_SIGLE' and 'nome_tabella' in params:
            # Import compatibility helper
            try:
                from modules.utility.pyarchinit_thesaurus_compatibility import get_compatible_names
                
                nome_tabella = params['nome_tabella'].strip("'")
                compatible_names = get_compatible_names(nome_tabella)
                
                # If we have multiple compatible names, we need to query for all of them
                if len(compatible_names) > 1:
                    # Create a session
                    Session = sessionmaker(bind=self.engine)
                    session = Session()
                    
                    # Build query with OR condition for all compatible names
                    # Get the mapped table for column access fallback
                    from sqlalchemy.orm import class_mapper
                    try:
                        mapper_obj = class_mapper(PYARCHINIT_THESAURUS_SIGLE)
                        mapped_table = mapper_obj.mapped_table
                    except Exception:
                        mapped_table = None

                    all_results = []
                    for compat_name in compatible_names:
                        temp_params = params.copy()
                        temp_params['nome_tabella'] = f"'{compat_name}'"

                        conditions = []
                        for key, value in temp_params.items():
                            column = None
                            # Try to get column from mapped class first
                            if hasattr(PYARCHINIT_THESAURUS_SIGLE, key):
                                attr = getattr(PYARCHINIT_THESAURUS_SIGLE, key)
                                if hasattr(attr, '__clause_element__') or hasattr(attr, 'property'):
                                    column = attr
                            # Fallback to mapped table
                            if column is None and mapped_table is not None:
                                if key in mapped_table.c:
                                    column = mapped_table.c[key]
                            if column is None:
                                continue  # Skip unknown columns
                            if isinstance(value, str) and value.startswith("'") and value.endswith("'"):
                                value = value.strip("'")
                            conditions.append(column == value)

                        if not conditions:
                            continue
                        query = session.query(PYARCHINIT_THESAURUS_SIGLE).filter(and_(*conditions))
                        results = query.all()
                        all_results.extend(results)
                    
                    session.close()
                    # Remove duplicates based on sigla
                    seen = set()
                    unique_results = []
                    for result in all_results:
                        if result.sigla not in seen:
                            seen.add(result.sigla)
                            unique_results.append(result)
                    
                    return unique_results
                    
            except ImportError:
                # If compatibility module not available, continue with normal flow
                pass
        
        # Create a session
        Session = sessionmaker(bind=self.engine)
        session = Session()
        
        # Mapping of table class names to class references
        table_classes = {
            'US':US, 'UT': UT, 'SITE': SITE, 'PERIODIZZAZIONE': PERIODIZZAZIONE, 'POTTERY': POTTERY,
            'STRUTTURA': STRUTTURA, 'SCHEDAIND': SCHEDAIND, 'INVENTARIO_MATERIALI': INVENTARIO_MATERIALI,
            'DETSESSO': DETSESSO, 'DOCUMENTAZIONE': DOCUMENTAZIONE, 'DETETA': DETETA, 'MEDIA': MEDIA,
            'MEDIA_THUMB': MEDIA_THUMB, 'MEDIATOENTITY': MEDIATOENTITY, 'MEDIAVIEW': MEDIAVIEW,
            'TOMBA': TOMBA, 'CAMPIONI': CAMPIONI, 'PYARCHINIT_THESAURUS_SIGLE': PYARCHINIT_THESAURUS_SIGLE,
            'INVENTARIO_LAPIDEI': INVENTARIO_LAPIDEI, 'PDF_ADMINISTRATOR': PDF_ADMINISTRATOR,
            'PYUS': PYUS, 'PYUSM': PYUSM, 'PYSITO_POINT': PYSITO_POINT, 'PYSITO_POLYGON': PYSITO_POLYGON,
            'PYQUOTE': PYQUOTE, 'PYQUOTEUSM': PYQUOTEUSM, 'PYUS_NEGATIVE': PYUS_NEGATIVE,
            'PYSTRUTTURE': PYSTRUTTURE, 'PYREPERTI': PYREPERTI, 'PYINDIVIDUI': PYINDIVIDUI,
            'PYCAMPIONI': PYCAMPIONI, 'PYTOMBA': PYTOMBA, 'PYDOCUMENTAZIONE': PYDOCUMENTAZIONE,
            'PYLINEERIFERIMENTO': PYLINEERIFERIMENTO, 'PYRIPARTIZIONI_SPAZIALI': PYRIPARTIZIONI_SPAZIALI,
            'PYSEZIONI': PYSEZIONI, 'TMA': TMA, 'TMA_MATERIALI': TMA_MATERIALI, 'FAUNA': FAUNA
            # Add other table class mappings here
        }
        
        # Get the table class from the mapping
        table_class = table_classes.get(table_class_name)
        if not table_class:
            raise ValueError(f"No table class found for {table_class_name}")
        
        # Start with an empty list of conditions
        conditions = []

        # Get the underlying table from the mapper to access columns directly
        from sqlalchemy.orm import class_mapper
        try:
            mapper_obj = class_mapper(table_class)
            mapped_table = mapper_obj.mapped_table
        except Exception:
            mapped_table = None

        # Iterate over the parameters to create conditions
        for key, value in params.items():
            column = None
            # Try to get column from mapped class first
            if hasattr(table_class, key):
                attr = getattr(table_class, key)
                # Check if it's an InstrumentedAttribute (SQLAlchemy column)
                if hasattr(attr, '__clause_element__') or hasattr(attr, 'property'):
                    column = attr

            # If not found on class, try the mapped table directly
            if column is None and mapped_table is not None:
                if key in mapped_table.c:
                    column = mapped_table.c[key]

            # If still not found, skip this condition
            if column is None:
                # Column not found - might be a new column not yet mapped
                print(f"[PyArchInit] Column {key} not found for {table_class_name}, skipping in search")
                continue

            # Clean the value if it's a string with quotes
            if isinstance(value, str) and value.startswith("'") and value.endswith("'"):
                value = value.strip("'")
            conditions.append(column == value)
        
        # Construct the query with the conditions
        query = session.query(table_class).filter(and_(*conditions))
        
        # Execute the query and fetch all results
        res = query.all()

        # Close the session
        session.close()

        # Salva nella cache
        self._set_cached_result(cache_key, res)
        return res

    def select_mediapath_from_id(self, media_id):
        sql_query = "SELECT filepath FROM media_table WHERE id_media = :media_id"
        res = self._execute_sql(sql_query, media_id=media_id)
        row = res.fetchone()
        return row[0] if row else None


    def query_all_us(self, table_class_str, column_name='us'):
        """
        Retrieve all records from a specified table and return values of a specific column.

        :param table_class_str: The name of the table class as a string.
        :param column_name: The name of the column to retrieve values from.
        :return: A list of values from the specified column of all records.
        """
        # Reflect the table from the database
        table = Table(table_class_str, self.metadata, autoload_with=self.engine)

        # Create a session
        Session = sessionmaker(bind=self.engine)
        session = Session()

        try:
            # Query all records from the table
            query = session.query(table).all()
            # Extract the 'us' column values
            us_values = [getattr(record, column_name, None) for record in query]
            return us_values
        except Exception as e:
            print(f"An error occurred while querying all records: {e}")
            return []
        finally:
            # Close the session
            session.close()
    def query_all(self, table_class_str):
        """
        Retrieve all records from a specified table.

        :param table_class_str: The name of the table class as a string.
        :return: A list of all records from the specified table.
        """
        # Reflect the table from the database
        table = Table(table_class_str, self.metadata, autoload_with=self.engine)

        # Create a session
        Session = sessionmaker(bind=self.engine)
        session = Session()

        try:
            # Query all records from the table
            query = session.query(table).all()
            return query
        except Exception as e:
            print(f"An error occurred while querying all records: {e}")
            return []
        finally:
            # Close the session
            session.close()
    
    def query_bool_special(self, params, table):
        u = Utility()
        params = u.remove_empty_items_fr_dict(params)

        list_keys_values = list(params.items())

        field_value_string = ""

        for sing_couple_n in range(len(list_keys_values)):
            if sing_couple_n == 0:
                if type(list_keys_values[sing_couple_n][1]) != "<type 'str'>":
                    field_value_string = table + ".%s == %s" % (
                    list_keys_values[sing_couple_n][0], list_keys_values[sing_couple_n][1])
                else:
                    field_value_string = table + ".%s == u%s" % (
                    list_keys_values[sing_couple_n][0], list_keys_values[sing_couple_n][1])
            else:
                if type(list_keys_values[sing_couple_n][1]) == "<type 'str'>":
                    field_value_string = field_value_string + "," + table + ".%s == %s" % (
                    list_keys_values[sing_couple_n][0], list_keys_values[sing_couple_n][1])
                else:
                    field_value_string = field_value_string + "," + table + ".%s == %s" % (
                    list_keys_values[sing_couple_n][0], list_keys_values[sing_couple_n][1])

                    # field_value_string = ", ".join([table + ".%s == u%s" % (k, v) for k, v in params.items()])

        """
        Per poter utilizzare l'operatore LIKE è necessario fare una iterazione attraverso il dizionario per discriminare tra
        stringhe e numeri
        #field_value_string = ", ".join([table + ".%s.like(%s)" % (k, v) for k, v in params.items()])
        """
        # self.connection()
        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()
        query_str = "session.query(" + table + ").filter(and_(" + field_value_string + ")).all()"
        res = eval(query_str)

        '''
        t = open("/test_import.txt", "w")
        t.write(str(query_str))
        t.close()
        '''
        session.close()
        return res
    def query_operator(self, params, table):
        u = Utility()
        #params = u.remove_empty_items_fr_dict(params)
        field_value_string = ''
        for i in params:
            if field_value_string == '':
                field_value_string = '%s.%s %s %s' % (table, i[0], i[1], i[2])
            else:
                field_value_string = field_value_string + ', %s.%s %s %s' % (table, i[0], i[1], i[2])

        query_str = "session.query(" + table + ").filter(and_(" + field_value_string + ")).all()"

        # self.connection()
        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()
        session.close()
        return eval(query_str)

    def query_distinct(self, table, query_params, distinct_field_name_params):
        # u = Utility()
        # params = u.remove_empty_items_fr_dict(params)
        ##      return session.query(INVENTARIO_MATERIALI.area,INVENTARIO_MATERIALI.us ).filter(INVENTARIO_MATERIALI.sito=='Sito archeologico').distinct().order_by(INVENTARIO_MATERIALI.area,INVENTARIO_MATERIALI.us )

        query_string = ""
        for i in query_params:
            if query_string == '':
                query_string = '%s.%s==%s' % (table, i[0], i[1])
            else:
                query_string = query_string + ',%s.%s==%s' % (table, i[0], i[1])

        distinct_string = ""
        for i in distinct_field_name_params:
            if distinct_string == '':
                distinct_string = '%s.%s' % (table, i)
            else:
                distinct_string = distinct_string + ',%s.%s' % (table, i)

        query_cmd = "session.query(" + distinct_string + ").filter(and_(" + query_string + ")).distinct().order_by(" + distinct_string + ")"
        # self.connection()
        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()
        session.close()
        return eval(query_cmd)

    def query_distinct_sql(self, table, query_params, distinct_field_name_params):
        # u = Utility()
        # params = u.remove_empty_items_fr_dict(params)
        ##      return session.query(INVENTARIO_MATERIALI.area,INVENTARIO_MATERIALI.us ).filter(INVENTARIO_MATERIALI.sito=='Sito archeologico').distinct().order_by(INVENTARIO_MATERIALI.area,INVENTARIO_MATERIALI.us )

        query_string = ""
        for i in query_params:
            if query_string == '':
                query_string = '%s=%s' % (i[0], i[1])
            else:
                query_string = query_string + ' AND %s=%s' % (i[0], i[1])

        distinct_string = ""
        for i in distinct_field_name_params:
            if distinct_string == '':
                distinct_string = '%s' % (i)
            else:
                distinct_string = distinct_string + ',%s' % (i)

        query_cmd = "SELECT DISTINCT " + distinct_string + " FROM " + table + ' WHERE ' + query_string
        # self.connection()
        res = self._execute_sql(query_cmd)
        return res

    # count distinct "name" values

    # session statement
    def insert_data_session(self, data):
        with self.session_scope() as session:
            session.add(data)
            # Log per debug
            try:
                # Try to flush first to get better error messages
                session.flush()
                # No need to commit here - session_scope handles it
            except Exception as e:
                if hasattr(data, '__dict__'):
                    # Check id field specifically
                    if hasattr(data, 'id'):
                        pass  # Previously had debug print here
                # Try to get the actual database error
                if hasattr(e, 'orig'):
                    pass  # Previously had debug print here
                raise
    def insert_data_conflict(self, data):
        with self.session_scope() as session:
            session.begin_nested()
            session.merge(data)
            # session_scope handles commit
    def update(self, table_class_str, id_table_str, value_id_list, columns_name_list, values_update_list):
        """
        Receives 5 values then putted in a list. The values must be passed
        in this order: table name->string, column_name_where->list containin'
        one value
        ('site_table', 'id_sito', [1], ['sito', 'nazione', 'regione', 'comune', 'descrizione', 'provincia'], ['Sito archeologico 1', 'Italiauiodsds', 'Emilia-Romagna', 'Riminijk', 'Sito di epoca altomedievale....23', 'Riminikljlks'])
        self.set_update = arg
        #self.connection()
        table = Table(self.set_update[0], self.metadata, autoload=True)
        changes_dict= {}
        u = Utility()
        set_update_4 = u.deunicode_list(self.set_update[4])

        u.add_item_to_dict(changes_dict,zip(self.set_update[3], set_update_4))

        f = open("test_update.txt", "w")
        f.write(str(self.set_update))
        f.close()

        exec_str = ('%s%s%s%s%s%s%s') % ("table.update(table.c.",
                                          self.set_update[1],
                                         " == '",
                                         self.set_update[2][0],
                                         "').execute(",
                                         changes_dict ,")")

        #session.query(SITE).filter(and_(SITE.id_sito == '1')).update(values = {SITE.sito:"updatetest"})
        """

        self.table_class_str = table_class_str
        self.id_table_str = id_table_str
        self.value_id_list = value_id_list
        self.columns_name_list = columns_name_list
        self.values_update_list = values_update_list

        changes_dict = {}
        u = Utility()
        update_value_list = u.deunicode_list(self.values_update_list)

        column_list = []
        for field in self.columns_name_list:
            column_str = ('%s.%s') % (table_class_str, field)
            column_list.append(column_str)

        u.add_item_to_dict(changes_dict, list(zip(self.columns_name_list, update_value_list)))

        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()
        # session.query(SITE).filter(and_(SITE.id_sito == '1')).update(values = {SITE.sito:"updatetest"})

        # Ensure the ID value is properly typed
        id_value = self.value_id_list[0]
        # If it's a numeric ID field and the value is a string, convert to int
        if self.id_table_str.lower() in ['id', 'id_tma', 'id_us', 'id_site', 'id_invmat', 'id_media']:
            try:
                id_value = int(id_value)
            except (ValueError, TypeError):
                pass  # Keep original value if conversion fails
        
        session_exec_str = 'session.query(%s).filter(and_(%s.%s == %s)).update(values = %s)' % (
        self.table_class_str, self.table_class_str, self.id_table_str, id_value, changes_dict)

        
        eval(session_exec_str)
        session.close()

    def update_tomba_dating_from_periodizzazione(self, site_name):
        # Reflect the tables from the database
        tomba_table = Table('tomba_table', self.metadata, autoload_with=self.engine)
        periodizzazione_table = Table('periodizzazione_table', self.metadata, autoload_with=self.engine)

        # Create a session
        Session = sessionmaker(bind=self.engine)
        session = Session()

        try:
            # Start a transaction
            with session.begin():
                # Select records from tomba_table for the specified site
                tomba_records = session.query(tomba_table).filter_by(sito=site_name).all()

                updates_made = 0
                for tomba_record in tomba_records:
                    # Skip records with empty 'periodo' or 'fase'
                    if not tomba_record.periodo_iniziale or not tomba_record.fase_iniziale:
                        continue

                    # Find the corresponding periodizzazione records for the specific site
                    periodizzazione_iniziale = session.query(periodizzazione_table). \
                        filter_by(sito=site_name, periodo=tomba_record.periodo_iniziale,
                                  fase=tomba_record.fase_iniziale).first()

                    periodizzazione_finale = None
                    if bool(tomba_record.periodo_finale):
                        periodizzazione_finale = session.query(periodizzazione_table). \
                            filter_by(sito=site_name, periodo=tomba_record.periodo_finale,
                                      fase=tomba_record.fase_finale).first()

                    # Concatenate the 'datazione_estesa' values if both are present
                    datazione_string = ""
                    if periodizzazione_iniziale and periodizzazione_finale:
                        datazione_string = f"{periodizzazione_iniziale.datazione_estesa}/{periodizzazione_finale.datazione_estesa}"
                    elif periodizzazione_iniziale:
                        datazione_string = periodizzazione_iniziale.datazione_estesa

                    if periodizzazione_iniziale or periodizzazione_finale:
                        # Check if the current 'Dating' value is different from the new value
                        current_dating = getattr(tomba_record, 'datazione_estesa', None)
                        if datazione_string and current_dating != datazione_string:
                            # Update the 'Dating' field in tomba_table
                            session.query(tomba_table). \
                                filter_by(id_tomba=tomba_record.id_tomba). \
                                update({'datazione_estesa': datazione_string}, synchronize_session=False)
                            updates_made += 1

                # Print the number of updates made
                print(
                    f"'Dating' fields for tombs in site '{site_name}' have been updated successfully. Total updates made: {updates_made}")

            # Commit the changes
            session.commit()
            return updates_made  # Return the count of updates made
        except Exception as e:
            # Rollback the transaction on error
            session.rollback()
            QMessageBox.warning(None, 'Error',
                                f"An error occurred while updating 'Dating' for tombs in site '{site_name}': {e}")
            raise e  # Re-raise the exception to be handled by the calling function
        finally:
            # Close the session
            session.close()

    # def update_us_dating_from_periodizzazione(self):
    #     # Reflect the tables from the database
    #     us_table = Table('us_table', self.metadata, autoload_with=self.engine)
    #     periodizzazione_table = Table('periodizzazione_table', self.metadata, autoload_with=self.engine)
    #
    #     # Create a session
    #     Session = sessionmaker(bind=self.engine)
    #     session = Session()
    #
    #     try:
    #         # Start a transaction
    #         with session.begin():
    #             # Select all records from us_table
    #             us_records = session.query(us_table).all()
    #
    #             updates_made = 0
    #             for us_record in us_records:
    #                 periodizzazione_iniziale, periodizzazione_finale = None, None
    #
    #                 if us_record.periodo_iniziale and us_record.fase_iniziale:
    #                     periodizzazione_iniziale = session.query(periodizzazione_table). \
    #                         filter_by(periodo=us_record.periodo_iniziale, fase=us_record.fase_iniziale).first()
    #
    #                 if not periodizzazione_iniziale:
    #                     # Update the 'Dating' field in us_table to None if periodizzazione_iniziale does not exist
    #                     session.query(us_table). \
    #                         filter_by(id_us=us_record.id_us). \
    #                         update({'datazione': None}, synchronize_session=False)
    #                     updates_made += 1
    #                     continue
    #
    #                 if us_record.periodo_finale and us_record.fase_finale:
    #                     periodizzazione_finale = session.query(periodizzazione_table). \
    #                         filter_by(periodo=us_record.periodo_finale, fase=us_record.fase_finale).first()
    #
    #                 datazione_string = ""
    #                 if periodizzazione_iniziale and periodizzazione_finale:
    #                     datazione_string = f"{periodizzazione_iniziale.datazione_estesa}/{periodizzazione_finale.datazione_estesa}"
    #                 elif periodizzazione_iniziale:
    #                     datazione_string = periodizzazione_iniziale.datazione_estesa
    #
    #                 current_dating = getattr(us_record, 'datazione', None)
    #                 if datazione_string != current_dating:
    #                     # Update the 'Dating' field in us_table
    #                     session.query(us_table). \
    #                         filter_by(id_us=us_record.id_us). \
    #                         update({'datazione': datazione_string}, synchronize_session=False)
    #                     updates_made += 1
    #
    #             # Print the number of updates made
    #             print(f"All 'Dating' fields have been updated successfully. Total updates made: {updates_made}")
    #
    #         session.commit()
    #         return updates_made  # Return the count of updates made
    #     except Exception as e:
    #         # Rollback the transaction in case of error
    #         session.rollback()
    #         QMessageBox.warning(None, 'ok', f"An error occurred while updating 'Dating': {e}")
    #         raise e  # Re-raise the exception
    #     finally:
    #         # Close the session
    #         session.close()

    def update_us_dating_from_periodizzazione(self, site_name):
        # Reflect the tables from the database
        us_table = Table('us_table', self.metadata, autoload_with=self.engine)
        periodizzazione_table = Table('periodizzazione_table', self.metadata, autoload_with=self.engine)

        # Create a session
        Session = sessionmaker(bind=self.engine)
        session = Session()

        try:
            # Start a transaction
            with session.begin():
                # Select only records from the specified site
                us_records = session.query(us_table).filter_by(sito=site_name).all()

                updates_made = 0
                for us_record in us_records:
                    periodizzazione_iniziale, periodizzazione_finale = None, None

                    if us_record.periodo_iniziale and us_record.fase_iniziale:
                        periodizzazione_iniziale = session.query(periodizzazione_table). \
                            filter_by(sito=site_name, periodo=us_record.periodo_iniziale,
                                      fase=us_record.fase_iniziale).first()

                    if not periodizzazione_iniziale:
                        # Update the 'Dating' field in us_table to None if periodizzazione_iniziale does not exist
                        session.query(us_table). \
                            filter_by(id_us=us_record.id_us). \
                            update({'datazione': None}, synchronize_session=False)
                        updates_made += 1
                        continue

                    if us_record.periodo_finale and us_record.fase_finale:
                        periodizzazione_finale = session.query(periodizzazione_table). \
                            filter_by(sito=site_name, periodo=us_record.periodo_finale,
                                      fase=us_record.fase_finale).first()

                    datazione_string = ""
                    if periodizzazione_iniziale and periodizzazione_finale:
                        datazione_string = f"{periodizzazione_iniziale.datazione_estesa}/{periodizzazione_finale.datazione_estesa}"
                    elif periodizzazione_iniziale:
                        datazione_string = periodizzazione_iniziale.datazione_estesa

                    current_dating = getattr(us_record, 'datazione', None)
                    if datazione_string != current_dating:
                        # Update the 'Dating' field in us_table
                        session.query(us_table). \
                            filter_by(id_us=us_record.id_us). \
                            update({'datazione': datazione_string}, synchronize_session=False)
                        updates_made += 1

                # Print the number of updates made
                print(
                    f"'Dating' fields for site '{site_name}' have been updated successfully. Total updates made: {updates_made}")

            session.commit()
            return updates_made  # Return the count of updates made
        except Exception as e:
            # Rollback the transaction in case of error
            session.rollback()
            QMessageBox.warning(None, 'Error', f"An error occurred while updating 'Dating' for site '{site_name}': {e}")
            raise e  # Re-raise the exception
        finally:
            # Close the session
            session.close()

    def update_find_check(self, table_class_str, id_table_str, value_id, find_check_value):
        self.table_class_str = table_class_str
        self.id_table_str = id_table_str
        self.value_id = value_id
        self.find_check_value = find_check_value

        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()

        session_exec_str = 'session.query(%s).filter(%s.%s == %s)).update(values = {"find_check": %d})' % (
        self.table_class_str, self.table_class_str, self.id_table_str, self.value_id, find_check_value)

        eval(session_exec_str)
        session.close()
    def empty_find_check(self, table_class_str, find_check_value):
        self.table_class_str = table_class_str
        self.find_check_value = find_check_value

        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()

        session_exec_str = 'session.query(%s).update(values = {"find_check": %d})' % (self.table_class_str, 0)

        eval(session_exec_str)
        session.close()
    def delete_one_record(self, tn, id_col, id_rec):
        
        self.table_name = tn
        self.id_column = id_col
        self.id_rec = id_rec
        # self.connection()
        table = Table(self.table_name, self.metadata, autoload=True)
        exec_str = ('%s%s%s%d%s') % ('table.delete(table.c.', self.id_column, ' == ', self.id_rec, ').execute()')

        eval(exec_str)
    
    def delete_record_by_field(self, table_name, field_name, field_value):
        """Delete records from a table where field matches value"""
        try:
            Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
            session = Session()
            
            # Map table names to entity classes
            table_classes = {
                'TMA_MATERIALI': TMA_MATERIALI
            }
            
            if table_name in table_classes:
                entity_class = table_classes[table_name]
                # Build the query dynamically
                query = session.query(entity_class).filter(getattr(entity_class, field_name) == field_value)
                records_deleted = query.count()
                query.delete()
                session.close()
                return records_deleted
            else:
                # For tables without entity class, use raw SQL
                # Get the correct table name
                actual_table_name = 'tma_materiali_ripetibili' if table_name == 'TMA_MATERIALI' else table_name.lower()
                
                # Always use raw SQL for tma_materiali_ripetibili to avoid foreign key issues
                from sqlalchemy import text
                sql = text(f"DELETE FROM {actual_table_name} WHERE {field_name} = :field_value")
                with self.engine.begin() as conn:
                    result = conn.execute(sql, {"field_value": field_value})
                return result.rowcount
                
        except Exception as e:
            if 'session' in locals():
                session.close()
            raise Exception(f"Error deleting records: {str(e)}")
        
    def max_num_id(self, tc, f):
        self.table_class = tc
        self.field_id = f

        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()
        exec_str = "session.query(func.max({}.{}))".format(self.table_class, self.field_id)
        max_id_func = eval(exec_str)
        res_all = max_id_func.all()
        res_max_num_id = res_all[0][0]
        session.close()
        if not res_max_num_id:
            return 0
        else:
            return int(res_max_num_id)


    def dir_query(self):
        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()

        # session.query(SITE).filter(SITE.id_sito == '1').update(values = {SITE.sito:"updatetest"})
        # return session.query(SITE).filter(and_(SITE.id_sito == 1)).all()
        # return os.environ['HOME']

        session.close()# managements utilities
        
    def fields_list(self, t, s=''):
        """return the list of columns in a table. If s is set a int,
        return only one column"""
        self.table_name = t
        self.sing_column = s
        table = Table(self.table_name, self.metadata, autoload=True)

        if not str(s):
            return [c.name for c in table.columns]
        else:
            return [c.name for c in table.columns][int(s)]

    def query_in_idus(self, id_list):
        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()
        res = session.query(US).filter(US.id_us.in_(id_list)).all()

        session.close()

        return res

    def query_sort(self, id_list, op, to, tc, idn):
        self.order_params = op
        self.type_order = to
        self.table_class = tc
        self.id_name = idn



        # Mappa delle classi
        class_map = {
            'US': US,

            'SITE': SITE,
            'PERIODIZZAZIONE': PERIODIZZAZIONE,
            'INVENTARIO_MATERIALI': INVENTARIO_MATERIALI,
            'STRUTTURA': STRUTTURA,
            'TOMBA': TOMBA,
            'SCHEDAIND': SCHEDAIND,
            'DETSESSO': DETSESSO,
            'DETETA': DETETA,
            'POTTERY': POTTERY,
            'CAMPIONI': CAMPIONI,
            'TMA': TMA,
            'DOCUMENTAZIONE': DOCUMENTAZIONE,
            'PYARCHINIT_THESAURUS_SIGLE': PYARCHINIT_THESAURUS_SIGLE
        }

        # Ottieni la classe corretta
        table_class_obj = class_map.get(self.table_class)
        if not table_class_obj:
            raise ValueError(f"Classe {self.table_class} non supportata")

        # Costruisci la lista dei parametri di ordinamento
        order_by_list = []

        for param in self.order_params:
            # Ottieni l'attributo della colonna
            column_attr = getattr(table_class_obj, param)

            # Applica la funzione di ordinamento appropriata
            if self.type_order.lower() == 'asc':
                order_by_list.append(asc(column_attr))
            elif self.type_order.lower() == 'desc':
                order_by_list.append(desc(column_attr))
            else:
                order_by_list.append(asc(column_attr))

        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()

        try:
            # Costruisci ed esegui la query
            id_column = getattr(table_class_obj, self.id_name)

            query = session.query(table_class_obj).filter(
                id_column.in_(id_list)
            ).order_by(*order_by_list)

            result = query.all()

            return result

        except Exception as e:
            print(f"Errore in query_sort: {str(e)}")
            raise
        finally:
            session.close()


    def run(self, stmt):
        rs = stmt.execute()
        res_list = []
        for row in rs:
            res_list.append(row[0])
        #session.close()
        return res_list

    def update_for(self):
        """
        table = Table('us_table_toimp', self.metadata, autoload=True)
        s = table.select(table.c.id_us > 0)
        res_list = self.run(s)
        cont = 11900
        for i in res_list:
            self.update('US_toimp', 'id_us', [i], ['id_us'], [cont])
            cont = cont+1
        """
        table = Table('inventario_materiali_table_toimp', self.metadata, autoload=True)
        s = table.select(table.c.id_invmat > 0)
        res_list = self.run(s)
        cont = 900
        for i in res_list:
            self.update('INVENTARIO_MATERIALI_TOIMP', 'id_invmat', [i], ['id_invmat'], [cont])
            cont = cont + 1

    def group_by(self, tn, fn, CD):
        """Group by the values by table name - string, field name - string, table class DB from mapper - string"""
        # Aggiungi caching per group_by (spesso usato per dropdown)
        cache_key = self._get_cache_key('group_by', tn, fn, CD)
        cached_result = self._get_cached_result(cache_key, cache_timeout=600)  # 10 minuti
        if cached_result is not None:
            return cached_result

        self.table_name = tn
        self.field_name = fn
        self.table_class = CD

        session = self.get_session()
        try:
            # Get the table class from the mapping
            table_classes = {
                'US': US, 'UT': UT, 'SITE': SITE, 'PERIODIZZAZIONE': PERIODIZZAZIONE, 'POTTERY': POTTERY,
                'STRUTTURA': STRUTTURA, 'SCHEDAIND': SCHEDAIND, 'INVENTARIO_MATERIALI': INVENTARIO_MATERIALI,
                'DETSESSO': DETSESSO, 'DOCUMENTAZIONE': DOCUMENTAZIONE, 'DETETA': DETETA, 'MEDIA': MEDIA,
                'MEDIA_THUMB': MEDIA_THUMB, 'MEDIATOENTITY': MEDIATOENTITY, 'MEDIAVIEW': MEDIAVIEW,
                'TOMBA': TOMBA, 'CAMPIONI': CAMPIONI, 'PYARCHINIT_THESAURUS_SIGLE': PYARCHINIT_THESAURUS_SIGLE,
                'INVENTARIO_LAPIDEI': INVENTARIO_LAPIDEI, 'PDF_ADMINISTRATOR': PDF_ADMINISTRATOR,
                'PYUS': PYUS, 'PYUSM': PYUSM, 'PYSITO_POINT': PYSITO_POINT, 'PYSITO_POLYGON': PYSITO_POLYGON,
                'PYQUOTE': PYQUOTE, 'PYQUOTEUSM': PYQUOTEUSM, 'PYUS_NEGATIVE': PYUS_NEGATIVE,
                'PYSTRUTTURE': PYSTRUTTURE, 'PYREPERTI': PYREPERTI, 'PYINDIVIDUI': PYINDIVIDUI,
                'PYCAMPIONI': PYCAMPIONI, 'PYTOMBA': PYTOMBA, 'PYDOCUMENTAZIONE': PYDOCUMENTAZIONE,
                'PYLINEERIFERIMENTO': PYLINEERIFERIMENTO, 'PYRIPARTIZIONI_SPAZIALI': PYRIPARTIZIONI_SPAZIALI,
                'PYSEZIONI': PYSEZIONI, 'TMA': TMA, 'TMA_MATERIALI': TMA_MATERIALI, 'FAUNA': FAUNA
            }

            table_class = table_classes.get(CD)
            if not table_class:
                raise ValueError(f"No table class found for {CD}")

            # Get the column from the mapped table (SQLAlchemy 2.0 compatible)
            from sqlalchemy.orm import class_mapper
            try:
                mapper_obj = class_mapper(table_class)
                mapped_table = mapper_obj.mapped_table
                column = mapped_table.c[fn]
            except Exception as e:
                # Fallback to class attribute if available
                if hasattr(table_class, fn):
                    column = getattr(table_class, fn)
                else:
                    raise AttributeError(f"Column {fn} not found for {CD}: {e}")

            # Build the select statement
            s = select(column).group_by(column)
            result = self._execute_sql(s).fetchall()

            # Salva nella cache
            self._set_cached_result(cache_key, result)
            return result
        finally:
            session.close()

    def query_where_text(self, c, v):
        self.c = c
        self.v = v
        # self.connection()
        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()

        string = ('%s%s%s%s%s') % ('session.query(PERIODIZZAZIONE).filter_by(', self.c, "='", self.v, "')")

        res = eval(string)
        session.close()
        return res

    def update_cont_per(self, s):
        self.sito = s



        # Lista per raccogliere tutti gli errori
        errori = []
        avvisi = []

        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()

        try:
            # Otteniamo la query
            string = ('%s%s%s%s%s') % ('session.query(US).filter_by(', 'sito', "='", str(self.sito), "')")
            query_us = eval(string)

            # Convertiamo la query in lista per poter usare len()
            lista_us = list(query_us)
            total_records = len(lista_us)

            if total_records == 0:
                # Se non ci sono record, mostra un messaggio e termina
                if hasattr(self, 'L') and self.L == 'it':
                    QMessageBox.information(None, "Informazione", "Nessun record da elaborare", QMessageBox.Ok)
                else:
                    QMessageBox.information(None, "Information", "No records to process", QMessageBox.Ok)
                return

            # Creiamo una progress bar
            progress = QProgressBar()
            progress.setWindowTitle("Aggiornamento Continuità Periodi")
            progress.setGeometry(300, 300, 400, 40)

            # Utilizziamo la classe Qt di QGIS
            try:
                progress.setWindowModality(Qt.WindowModal)
                progress.setAlignment(Qt.AlignmentFlag.AlignCenter)
            except AttributeError:
                pass

            progress.setMinimum(0)
            progress.setMaximum(total_records)
            progress.setValue(0)
            progress.show()
            QApplication.processEvents()

            # Contatore per tenere traccia dell'avanzamento
            count = 0
            last_update_time = time.time()

            # Procediamo con l'elaborazione
            for i in lista_us:
                # Incrementiamo il contatore
                count += 1

                # Aggiorniamo la progress bar ogni 10 record o ogni secondo
                current_time = time.time()
                if count % 10 == 0 or (current_time - last_update_time) >= 1.0:
                    progress.setValue(count)
                    percentage = int((count / total_records) * 100)
                    progress.setFormat(f"Elaborazione record {count} di {total_records} ({percentage}%)")
                    QApplication.processEvents()
                    last_update_time = current_time

                try:
                    # Logica originale di elaborazione record
                    if not i.periodo_finale and i.periodo_iniziale:
                        periodiz = self.query_bool(
                            {'sito': "'" + str(self.sito) + "'", 'periodo': i.periodo_iniziale,
                             'fase': "'" + str(i.fase_iniziale) + "'"},
                            'PERIODIZZAZIONE')
                        if periodiz and len(periodiz) > 0:
                            self.update('US', 'id_us', [int(i.id_us)], ['cont_per'], [periodiz[0].cont_per])
                        else:
                            errori.append(f"US {i.us}: Nessun dato di periodizzazione trovato")

                    elif not i.periodo_iniziale:
                        continue

                    elif i.periodo_finale and i.periodo_iniziale:
                        cod_cont_iniz_temp = self.query_bool(
                            {'sito': "'" + str(self.sito) + "'", 'periodo': int(i.periodo_iniziale),
                             'fase': int(i.fase_iniziale)}, 'PERIODIZZAZIONE')

                        cod_cont_fin_temp = self.query_bool(
                            {'sito': "'" + str(self.sito) + "'", 'periodo': int(i.periodo_finale),
                             'fase': int(i.fase_finale)},
                            'PERIODIZZAZIONE')

                        if not cod_cont_iniz_temp or not cod_cont_fin_temp:
                            errori.append(f"US {i.us}: Dati di periodizzazione mancanti")
                            continue

                        cod_cont_iniz = cod_cont_iniz_temp[0].cont_per
                        cod_cont_fin = cod_cont_fin_temp[0].cont_per

                        # Controllo che i valori siano numeri
                        try:
                            start_val = int(cod_cont_iniz)
                            end_val = int(cod_cont_fin)
                        except (ValueError, TypeError):
                            errori.append(
                                f"US {i.us}: Errore di conversione - cod_cont_iniz: {cod_cont_iniz}, cod_cont_fin: {cod_cont_fin}")

                            # Se non sono numeri, usiamo i valori originali senza calcolare range
                            if cod_cont_iniz != cod_cont_fin:
                                cod_cont_var_txt = f"{cod_cont_iniz}/{cod_cont_fin}"
                            else:
                                cod_cont_var_txt = str(cod_cont_iniz)
                            self.update('US', 'id_us', [int(i.id_us)], ['cont_per'], [cod_cont_var_txt])
                            continue

                        # Se start_val > end_val, invertiamo i valori per evitare loop infiniti
                        if start_val > end_val:
                            #avvisi.append(
                               # f"US {i.us}: Valore iniziale ({start_val}) maggiore del finale ({end_val}). Inversione effettuata.")
                            start_val, end_val = end_val, start_val

                        # Generiamo la sequenza completa di valori
                        if start_val == end_val:
                            cod_cont_var_txt = str(start_val)
                        else:
                            values = list(range(start_val, end_val + 1))
                            cod_cont_var_txt = "/".join(str(v) for v in values)

                        self.update('US', 'id_us', [int(i.id_us)], ['cont_per'], [cod_cont_var_txt])

                except Exception as e:
                    errori.append(f"US {i.us}: {str(e)}")
                    continue

            # Al termine dell'elaborazione, aggiorniamo la progress bar
            progress.setValue(total_records)
            progress.setFormat("Elaborazione completata (100%)")
            QApplication.processEvents()

            # Chiudiamo la progress bar
            progress.close()

            # Mostriamo un riepilogo degli errori/avvisi
            if errori:
                error_text = ""
                if errori:
                    error_text += f"ERRORI ({len(errori)}):\n" + "\n".join(errori) + "\n\n"
                #if avvisi:
                    #error_text += f"AVVISI ({len(avvisi)}):\n" + "\n".join(avvisi)

                # Creiamo una finestra di dialogo per mostrare tutti gli errori
                if hasattr(self, 'L') and self.L == 'it':
                    QMessageBox.warning(None, "Completato con errori",
                                        f"Elaborazione completata con {len(errori)} errori.\n\n{error_text}",
                                        QMessageBox.Ok)
                else:
                    QMessageBox.warning(None, "Completed with errors/warnings",
                                        f"Processing completed with {len(errori)} errors.\n\n{error_text}",
                                        QMessageBox.Ok)
            else:
                # Nessun errore
                if hasattr(self, 'L') and self.L == 'it':
                    QMessageBox.information(None, "Completato",
                                            f"Elaborazione completata con successo. {count} record aggiornati.",
                                            QMessageBox.Ok)
                else:
                    QMessageBox.information(None, "Completed",
                                            f"Processing completed successfully. {count} records updated.",
                                            QMessageBox.Ok)

        except Exception as e:
            # Gestiamo eccezioni generali
            error_msg = f"Errore durante l'aggiornamento: {str(e)}"
            print(error_msg)
            if 'progress' in locals() and progress:
                progress.close()
            QMessageBox.critical(None, "Errore", error_msg, QMessageBox.Ok)

        finally:
            # Assicuriamoci che la sessione venga chiusa
            if 'session' in locals():
                session.close()

    # def update_cont_per(self, s):
    #     '''
    #     Esegue l'operazione per aggiornare la continuità dei periodi per un sito specificato. Esegue operazioni sul
    #     database e gestisce l'elaborazione dei record con un feedback visivo sul progresso.
    #
    #     Attributi:
    #         sito (str): L'identificatore del sito per i record da elaborare.
    #
    #     Parametri:
    #         s (str): L'identificatore del sito da aggiornare.
    #
    #     Eccezioni sollevate:
    #         Exception: Eccezione generale sollevata per errori imprevisti che si verificano durante l'operazione.
    #
    #     Dettagli:
    #         Questa operazione recupera i record corrispondenti all'identificatore del sito fornito, li elabora e
    #         aggiorna la continuità dei periodi secondo una logica specificata. Fornisce aggiornamenti sul progresso in
    #         tempo reale utilizzando una barra di avanzamento e gestisce potenziali eccezioni per garantire
    #         un'elaborazione senza interruzioni.
    #
    #     Effetti collaterali:
    #         Aggiorna il campo 'cont_per' nel database per ciascun record elaborato. Mostra il progresso visivo e
    #         messaggi di notifica sia per le informazioni che per gli errori.
    #
    #     Note:
    #         - Il metodo gestisce sia set di record vuoti che eccezioni di record individuali senza interrompere
    #         l'elaborazione dei record successivi.
    #         - Elabora le interazioni con il database tramite una sessione e garantisce la corretta chiusura della
    #         sessione dopo l'operazione.
    #         - Implementa messaggi localizzati per notifiche interattive dove applicabile.
    #
    #     '''
    #
    #     self.sito = s
    #
    #     Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
    #     session = Session()
    #
    #     try:
    #         # Otteniamo la query
    #         string = ('%s%s%s%s%s') % ('session.query(US).filter_by(', 'sito', "='", str(self.sito), "')")
    #         query_us = eval(string)
    #
    #         # Convertiamo la query in lista per poter usare len()
    #         lista_us = list(query_us)
    #         total_records = len(lista_us)
    #
    #         # Debug - verifichiamo che ci siano effettivamente dei record
    #         print(f"Totale record da elaborare: {total_records}")
    #
    #         if total_records == 0:
    #             # Se non ci sono record, mostra un messaggio e termina
    #             if hasattr(self, 'L') and self.L == 'it':
    #                 QMessageBox.information(None, "Informazione", "Nessun record da elaborare", QMessageBox.Ok)
    #             else:
    #                 QMessageBox.information(None, "Information", "No records to process", QMessageBox.Ok)
    #             return
    #
    #         # Creiamo una progress bar
    #         progress = QProgressBar()
    #         progress.setWindowTitle("Aggiornamento Continuità Periodi")
    #         progress.setGeometry(300, 300, 300, 40)
    #         progress.setWindowModality(Qt.WindowModal)
    #         progress.setMinimum(0)
    #         progress.setMaximum(total_records)
    #         progress.setValue(0)
    #         #progress.setAlignment(Qt.AlignmentFlag.AlignCenter)
    #         progress.show()
    #         QApplication.processEvents()
    #
    #         # Contatore per tenere traccia dell'avanzamento
    #         count = 0
    #         last_update_time = time.time()
    #
    #         # Procediamo con l'elaborazione
    #         for i in lista_us:
    #             # Incrementiamo il contatore
    #             count += 1
    #
    #             # Aggiorniamo la progress bar ogni 10 record o ogni secondo
    #             current_time = time.time()
    #             if count % 10 == 0 or (current_time - last_update_time) >= 1.0:
    #                 progress.setValue(count)
    #                 percentage = int((count / total_records) * 100)
    #                 progress.setFormat(f"Elaborazione record {count} di {total_records} ({percentage}%)")
    #                 QApplication.processEvents()
    #                 last_update_time = current_time
    #
    #             try:
    #                 # Logica originale di elaborazione record
    #                 if not i.periodo_finale and i.periodo_iniziale:
    #                     periodiz = self.query_bool(
    #                         {'sito': "'" + str(self.sito) + "'", 'periodo': i.periodo_iniziale,
    #                          'fase': "'" + str(i.fase_iniziale) + "'"},
    #                         'PERIODIZZAZIONE')
    #                     if periodiz and len(periodiz) > 0:
    #                         self.update('US', 'id_us', [int(i.id_us)], ['cont_per'], [periodiz[0].cont_per])
    #                     else:
    #                         print(f"Nessun dato di periodizzazione trovato per US {i.us}")
    #
    #                 elif not i.periodo_iniziale:
    #                     print(f"US {i.us} senza periodo iniziale, continuo...")
    #                     continue
    #
    #                 elif i.periodo_finale and i.periodo_iniziale:
    #                     cod_cont_iniz_temp = self.query_bool(
    #                         {'sito': "'" + str(self.sito) + "'", 'periodo': int(i.periodo_iniziale),
    #                          'fase': int(i.fase_iniziale)}, 'PERIODIZZAZIONE')
    #
    #                     cod_cont_fin_temp = self.query_bool(
    #                         {'sito': "'" + str(self.sito) + "'", 'periodo': int(i.periodo_finale),
    #                          'fase': int(i.fase_finale)},
    #                         'PERIODIZZAZIONE')
    #
    #                     if not cod_cont_iniz_temp or not cod_cont_fin_temp:
    #                         print(f"Dati di periodizzazione mancanti per US {i.us}")
    #                         continue
    #
    #                     cod_cont_iniz = cod_cont_iniz_temp[0].cont_per
    #                     cod_cont_fin = cod_cont_fin_temp[0].cont_per
    #
    #                     # Debug - vediamo i valori reali
    #                     print(f"US {i.us} - Continuità iniziale: {cod_cont_iniz}, Continuità finale: {cod_cont_fin}")
    #
    #                     # Controllo che i valori siano numeri
    #                     try:
    #                         start_val = int(cod_cont_iniz)
    #                         end_val = int(cod_cont_fin)
    #                     except (ValueError, TypeError):
    #                         print(
    #                             f"Errore di conversione - cod_cont_iniz: {cod_cont_iniz}, cod_cont_fin: {cod_cont_fin}")
    #                         # Se non sono numeri, usiamo i valori originali senza calcolare range
    #                         if cod_cont_iniz != cod_cont_fin:
    #                             cod_cont_var_txt = f"{cod_cont_iniz}/{cod_cont_fin}"
    #                         else:
    #                             cod_cont_var_txt = str(cod_cont_iniz)
    #                         self.update('US', 'id_us', [int(i.id_us)], ['cont_per'], [cod_cont_var_txt])
    #                         continue
    #
    #                     # Se start_val > end_val, invertiamo i valori per evitare loop infiniti
    #                     if start_val > end_val:
    #                         print(
    #                             f"Attenzione: valore iniziale ({start_val}) maggiore del valore finale ({end_val}). Inversione.")
    #                         start_val, end_val = end_val, start_val
    #
    #                     # Generiamo la sequenza completa di valori
    #                     if start_val == end_val:
    #                         cod_cont_var_txt = str(start_val)
    #                     else:
    #                         values = list(range(start_val, end_val + 1))
    #                         cod_cont_var_txt = "/".join(str(v) for v in values)
    #
    #                     print(f"US {i.us} - Risultato: {cod_cont_var_txt}")
    #                     self.update('US', 'id_us', [int(i.id_us)], ['cont_per'], [cod_cont_var_txt])
    #
    #             except Exception as e:
    #                 print(f"Errore nell'elaborazione del record {count} (US {i.us}): {str(e)}")
    #                 # Continuiamo con il prossimo record invece di interrompere tutto
    #                 continue
    #
    #         # Al termine dell'elaborazione, aggiorniamo e chiudiamo la progress bar
    #         progress.setValue(total_records)
    #         progress.setFormat("Elaborazione completata (100%)")
    #         QApplication.processEvents()
    #
    #         # Mostriamo un messaggio di completamento
    #         if hasattr(self, 'L') and self.L == 'it':
    #             QMessageBox.information(None, "Completato", f"Elaborazione completata. {count} record aggiornati.",
    #                                     QMessageBox.Ok)
    #         else:
    #             QMessageBox.information(None, "Completed", f"Processing completed. {count} records updated.",
    #                                     QMessageBox.Ok)
    #
    #         # Chiudiamo la progress bar
    #         progress.close()
    #
    #     except Exception as e:
    #         # Gestiamo eccezioni generali
    #         error_msg = f"Errore durante l'aggiornamento: {str(e)}"
    #         print(error_msg)
    #         QMessageBox.critical(None, "Errore", error_msg, QMessageBox.Ok)
    #
    #     finally:
    #         # Assicuriamoci che la sessione venga chiusa
    #         if 'session' in locals():
    #             session.close()
                

    def remove_alltags_from_db_sql(self,s):
        sql_query_string = ("DELETE FROM media_to_entity_table WHERE media_name  = '%s'") % (s)
    
        res = self._execute_sql(sql_query_string)
        # rows= res.fetchall()
        return res    
    
    def remove_tags_from_db_sql(self,s):
        sql_query_string = ("DELETE FROM media_to_entity_table WHERE id_entity  = '%s'") % (s)
    
        res = self._execute_sql(sql_query_string)
        # rows= res.fetchall()
        return res

    def remove_tags_from_db_sql_scheda(self, s,n):
        sql_query_string = ("DELETE FROM media_to_entity_table WHERE id_entity  = '%s' and media_name= '%s' ") % (s,n)

        res = self._execute_sql(sql_query_string)
        # rows= res.fetchall()
        return res
    def delete_thumb_from_db_sql(self,s):
        sql_query_string = ("DELETE FROM media_thumb_table WHERE media_filename  = '%s'") % (s)
    
        res = self._execute_sql(sql_query_string)
        # rows= res.fetchall()
        return res    
    def select_medianame_from_st_sql(self,sito,sigla,numero):
        sql_query_string = ("SELECT c.filepath, a.media_name FROM media_to_entity_table as a,  struttura_table as b, media_thumb_table as c WHERE b.id_struttura=a.id_entity and c.id_media=a.id_media  and b.sito= '%s' and b.sigla_struttura='%s' and b.numero_struttura='%s' and entity_type='STRUTTURA'")%(sito,sigla,numero) 
        
        res = self._execute_sql(sql_query_string)
        rows= res.fetchall()
        return rows    
    def select_medianame_from_db_sql(self,sito,area):
        sql_query_string = ("SELECT c.filepath, b.us,a.media_name FROM media_to_entity_table as a,  us_table as b, media_thumb_table as c WHERE b.id_us=a.id_entity and c.id_media=a.id_media  and b.sito= '%s' and b.area='%s'")%(sito,area) 
        
        res = self._execute_sql(sql_query_string)
        rows= res.fetchall()
        return rows
    def select_medianame_tb_from_db_sql(self,sito,area):
        sql_query_string = ("SELECT c.filepath, a.media_name FROM media_to_entity_table as a,  tomba_table as b, media_thumb_table as c WHERE b.id_tomba=a.id_entity and c.id_media=a.id_media  and b.sito= '%s' and b.area='%s'and entity_type='TOMBA'")%(sito,area) 
        
        res = self._execute_sql(sql_query_string)
        rows= res.fetchall()
        return rows

    def select_medianame_pot_from_db_sql(self, sito, area, us):
        sql_query_string = (
                               "SELECT c.filepath, a.media_name FROM media_to_entity_table as a,  pottery_table as b, media_thumb_table as c WHERE b.id_rep=a.id_entity and c.id_media=a.id_media  and b.sito= '%s' and b.area='%s' and b.us = '%s' and entity_type='CERAMICA'") % (
                           sito, area, us)

        res = self._execute_sql(sql_query_string)
        rows = res.fetchall()
        return rows


    def select_medianame_ra_from_db_sql(self,sito,area,us):
        sql_query_string = ("SELECT c.filepath, a.media_name FROM media_to_entity_table as a,  inventario_materiali_table as b, media_thumb_table as c WHERE b.id_invmat=a.id_entity and c.id_media=a.id_media  and b.sito= '%s' and b.area='%s' and b.us = '%s' and entity_type='REPERTO'")%(sito,area,us) 
        
        res = self._execute_sql(sql_query_string)
        rows= res.fetchall()
        return rows
    
    def select_medianame_2_from_db_sql(self,sito,area,us):
        sql_query_string = ("SELECT c.filepath, a.media_name FROM media_to_entity_table as a,  us_table as b, media_thumb_table as c WHERE b.id_us=a.id_entity and c.id_media=a.id_media  and b.sito= '%s' and b.area='%s' and b.us = '%s' and entity_type='US'")%(sito,area,us)

        res = self._execute_sql(sql_query_string)
        rows= res.fetchall()
        return rows

    # =====================================================
    # ADVANCED MEDIA SEARCH METHODS
    # =====================================================

    def search_untagged_media(self, text_filter=None):
        """
        Search for untagged images (not associated with any entity).
        Returns images in media_table that have no entry in media_to_entity_table.

        Args:
            text_filter: Optional text to filter by filename (LIKE pattern)
        """
        if text_filter:
            sql_query_string = """
                SELECT DISTINCT m.id_media, m.filename, m.filepath, t.filepath as thumb_path
                FROM media_table m
                LEFT JOIN media_thumb_table t ON m.id_media = t.id_media
                WHERE m.id_media NOT IN (SELECT DISTINCT id_media FROM media_to_entity_table)
                AND (m.filename LIKE :filter OR m.descrizione LIKE :filter)
                ORDER BY m.filename
            """
            with self.engine.connect() as connection:
                res = connection.execute(text(sql_query_string), {"filter": f"%{text_filter}%"})
                rows = res.fetchall()
        else:
            sql_query_string = """
                SELECT DISTINCT m.id_media, m.filename, m.filepath, t.filepath as thumb_path
                FROM media_table m
                LEFT JOIN media_thumb_table t ON m.id_media = t.id_media
                WHERE m.id_media NOT IN (SELECT DISTINCT id_media FROM media_to_entity_table)
                ORDER BY m.filename
            """
            with self.engine.connect() as connection:
                res = connection.execute(text(sql_query_string))
                rows = res.fetchall()
        return rows

    def search_tagged_media_flexible(self, entity_type=None, sito=None, area=None, us=None,
                                      numero_inventario=None, text_filter=None, use_like=True):
        """
        Flexible search for tagged images with optional parameters and LIKE patterns.

        Args:
            entity_type: 'US', 'CERAMICA', 'REPERTO', 'TOMBA', 'STRUTTURA', 'UT' or None for all
            sito: Site name (exact or LIKE pattern if use_like=True)
            area: Area (exact or LIKE pattern if use_like=True)
            us: Stratigraphic unit (exact or LIKE pattern if use_like=True)
            numero_inventario: Inventory number for materials (exact or LIKE)
            text_filter: Text to filter by filename/description
            use_like: If True, use LIKE for partial matching
        """
        conditions = []

        # Build base query - join with appropriate entity table based on type
        if entity_type == 'US':
            base_query = """
                SELECT DISTINCT c.filepath, a.media_name, b.sito, b.area, b.us
                FROM media_to_entity_table a
                JOIN us_table b ON b.id_us = a.id_entity
                JOIN media_thumb_table c ON c.id_media = a.id_media
                WHERE a.entity_type = 'US'
            """
            if sito:
                if use_like:
                    conditions.append("b.sito LIKE '%{0}%'".format(sito.replace("'", "''")))
                else:
                    conditions.append("b.sito = '{0}'".format(sito.replace("'", "''")))
            if area:
                if use_like:
                    conditions.append("b.area LIKE '%{0}%'".format(area.replace("'", "''")))
                else:
                    conditions.append("b.area = '{0}'".format(area.replace("'", "''")))
            if us:
                if use_like:
                    conditions.append("CAST(b.us AS TEXT) LIKE '%{0}%'".format(str(us).replace("'", "''")))
                else:
                    conditions.append("b.us = '{0}'".format(str(us).replace("'", "''")))

        elif entity_type == 'CERAMICA':
            base_query = """
                SELECT DISTINCT c.filepath, a.media_name, b.sito, b.area, b.us
                FROM media_to_entity_table a
                JOIN pottery_table b ON b.id_rep = a.id_entity
                JOIN media_thumb_table c ON c.id_media = a.id_media
                WHERE a.entity_type = 'CERAMICA'
            """
            if sito:
                if use_like:
                    conditions.append("b.sito LIKE '%{0}%'".format(sito.replace("'", "''")))
                else:
                    conditions.append("b.sito = '{0}'".format(sito.replace("'", "''")))
            if area:
                if use_like:
                    conditions.append("b.area LIKE '%{0}%'".format(area.replace("'", "''")))
                else:
                    conditions.append("b.area = '{0}'".format(area.replace("'", "''")))
            if us:
                if use_like:
                    conditions.append("CAST(b.us AS TEXT) LIKE '%{0}%'".format(str(us).replace("'", "''")))
                else:
                    conditions.append("b.us = '{0}'".format(str(us).replace("'", "''")))

        elif entity_type == 'REPERTO':
            base_query = """
                SELECT DISTINCT c.filepath, a.media_name, b.sito, b.area, b.us, b.numero_inventario
                FROM media_to_entity_table a
                JOIN inventario_materiali_table b ON b.id_invmat = a.id_entity
                JOIN media_thumb_table c ON c.id_media = a.id_media
                WHERE a.entity_type = 'REPERTO'
            """
            if sito:
                if use_like:
                    conditions.append("b.sito LIKE '%{0}%'".format(sito.replace("'", "''")))
                else:
                    conditions.append("b.sito = '{0}'".format(sito.replace("'", "''")))
            if area:
                if use_like:
                    conditions.append("b.area LIKE '%{0}%'".format(area.replace("'", "''")))
                else:
                    conditions.append("b.area = '{0}'".format(area.replace("'", "''")))
            if us:
                if use_like:
                    conditions.append("CAST(b.us AS TEXT) LIKE '%{0}%'".format(str(us).replace("'", "''")))
                else:
                    conditions.append("b.us = '{0}'".format(str(us).replace("'", "''")))
            if numero_inventario:
                if use_like:
                    conditions.append("CAST(b.numero_inventario AS TEXT) LIKE '%{0}%'".format(str(numero_inventario).replace("'", "''")))
                else:
                    conditions.append("b.numero_inventario = {0}".format(int(numero_inventario)))

        elif entity_type == 'TOMBA':
            base_query = """
                SELECT DISTINCT c.filepath, a.media_name, b.sito, b.area, b.nr_scheda_taf
                FROM media_to_entity_table a
                JOIN tomba_table b ON b.id_tomba = a.id_entity
                JOIN media_thumb_table c ON c.id_media = a.id_media
                WHERE a.entity_type = 'TOMBA'
            """
            if sito:
                if use_like:
                    conditions.append("b.sito LIKE '%{0}%'".format(sito.replace("'", "''")))
                else:
                    conditions.append("b.sito = '{0}'".format(sito.replace("'", "''")))
            if area:
                if use_like:
                    conditions.append("b.area LIKE '%{0}%'".format(area.replace("'", "''")))
                else:
                    conditions.append("b.area = '{0}'".format(area.replace("'", "''")))

        elif entity_type == 'STRUTTURA':
            base_query = """
                SELECT DISTINCT c.filepath, a.media_name, b.sito, b.sigla_struttura, b.numero_struttura
                FROM media_to_entity_table a
                JOIN struttura_table b ON b.id_struttura = a.id_entity
                JOIN media_thumb_table c ON c.id_media = a.id_media
                WHERE a.entity_type = 'STRUTTURA'
            """
            if sito:
                if use_like:
                    conditions.append("b.sito LIKE '%{0}%'".format(sito.replace("'", "''")))
                else:
                    conditions.append("b.sito = '{0}'".format(sito.replace("'", "''")))

        elif entity_type == 'UT':
            base_query = """
                SELECT DISTINCT c.filepath, a.media_name, b.progetto, b.nr_ut
                FROM media_to_entity_table a
                JOIN ut_table b ON b.id_ut = a.id_entity
                JOIN media_thumb_table c ON c.id_media = a.id_media
                WHERE a.entity_type = 'UT'
            """
            if sito:
                if use_like:
                    conditions.append("b.progetto LIKE '%{0}%'".format(sito.replace("'", "''")))
                else:
                    conditions.append("b.progetto = '{0}'".format(sito.replace("'", "''")))

        else:
            # All entity types - generic search
            base_query = """
                SELECT DISTINCT c.filepath, a.media_name, a.entity_type
                FROM media_to_entity_table a
                JOIN media_thumb_table c ON c.id_media = a.id_media
                WHERE 1=1
            """

        # Add text filter on media name
        if text_filter:
            conditions.append("(a.media_name LIKE '%{0}%')".format(text_filter.replace("'", "''")))

        # Build final query
        sql_query_string = base_query
        if conditions:
            sql_query_string += " AND " + " AND ".join(conditions)
        sql_query_string += " ORDER BY a.media_name"

        with self.engine.connect() as connection:
            res = connection.execute(text(sql_query_string))
            rows = res.fetchall()
        return rows

    def search_all_media(self, text_filter=None, tagged_only=None):
        """
        Search all media with optional text filter and tagged/untagged filter.

        Args:
            text_filter: Text to filter by filename
            tagged_only: True=only tagged, False=only untagged, None=all
        """
        if tagged_only is True:
            # Only tagged images
            base_query = """
                SELECT DISTINCT m.id_media, m.filename, m.filepath, t.filepath as thumb_path, 'tagged' as status
                FROM media_table m
                JOIN media_thumb_table t ON m.id_media = t.id_media
                WHERE m.id_media IN (SELECT DISTINCT id_media FROM media_to_entity_table)
            """
        elif tagged_only is False:
            # Only untagged images
            base_query = """
                SELECT DISTINCT m.id_media, m.filename, m.filepath, t.filepath as thumb_path, 'untagged' as status
                FROM media_table m
                LEFT JOIN media_thumb_table t ON m.id_media = t.id_media
                WHERE m.id_media NOT IN (SELECT DISTINCT id_media FROM media_to_entity_table)
            """
        else:
            # All images
            base_query = """
                SELECT DISTINCT m.id_media, m.filename, m.filepath, t.filepath as thumb_path,
                    CASE WHEN m.id_media IN (SELECT DISTINCT id_media FROM media_to_entity_table)
                         THEN 'tagged' ELSE 'untagged' END as status
                FROM media_table m
                LEFT JOIN media_thumb_table t ON m.id_media = t.id_media
                WHERE 1=1
            """

        if text_filter:
            base_query += " AND (m.filename LIKE '%{0}%' OR m.descrizione LIKE '%{0}%')".format(
                text_filter.replace("'", "''"))

        base_query += " ORDER BY m.filename"

        with self.engine.connect() as connection:
            res = connection.execute(text(base_query))
            rows = res.fetchall()
        return rows

    def search_media_by_inventario(self, sito=None, numero_inventario=None, text_filter=None):
        """
        Search media specifically for Inventario Materiali by numero_inventario.
        """
        conditions = ["a.entity_type = 'REPERTO'"]

        if sito:
            conditions.append("b.sito LIKE '%{0}%'".format(sito.replace("'", "''")))
        if numero_inventario:
            conditions.append("CAST(b.numero_inventario AS TEXT) LIKE '%{0}%'".format(
                str(numero_inventario).replace("'", "''")))
        if text_filter:
            conditions.append("a.media_name LIKE '%{0}%'".format(text_filter.replace("'", "''")))

        sql_query_string = """
            SELECT DISTINCT c.filepath, a.media_name, b.sito, b.area, b.us, b.numero_inventario
            FROM media_to_entity_table a
            JOIN inventario_materiali_table b ON b.id_invmat = a.id_entity
            JOIN media_thumb_table c ON c.id_media = a.id_media
            WHERE {0}
            ORDER BY b.numero_inventario, a.media_name
        """.format(" AND ".join(conditions))

        with self.engine.connect() as connection:
            res = connection.execute(text(sql_query_string))
            rows = res.fetchall()
        return rows

    def get_total_pages(self, filter_query, page_size):
        # Esegui una query per contare il numero totale di record che corrispondono al filtro
        sql_query_string = (
                               "SELECT COUNT(*) FROM media_thumb_table as a, media_to_entity_table as b  %s") % filter_query
        res = self._execute_sql(sql_query_string)
        total_records = res.scalar()  # .scalar() restituisce il primo elemento della prima riga, che in questo caso è il conteggio

        # Calcola e restituisci il numero totale di pagine
        total_pages = math.ceil(total_records / page_size)
        return total_pages

    def select_thumb(self, page_number, page_size):
        start_index = (page_number - 1) * page_size
        sql_query_string = (
            "SELECT * FROM media_thumb_table LIMIT {} OFFSET {}"
        ).format( page_size, start_index)
        res = self._execute_sql(sql_query_string)
        rows = res.fetchall()
        return rows
    def select_original(self, page_number, page_size):
        start_index = (page_number - 1) * page_size
        sql_query_string = (
            "SELECT * FROM media_to_entity_table LIMIT {} OFFSET {}"
        ).format( page_size, start_index)
        res = self._execute_sql(sql_query_string)
        rows = res.fetchall()
        return rows
    def select_ra_from_db_sql(self,sito,area,us):
        sql_query_string = ("SELECT n_reperto from inventario_materiali_table WHERE sito = '%s' and area = '%s' and us = '%s'")%(sito,area,us) 
        
        res = self._execute_sql(sql_query_string)
        rows= res.fetchall()
        return rows
    def select_coord_from_db_sql(self,sito,area,us):
        sql_query_string = ("SELECT coord from pyunitastratigrafiche WHERE scavo_s = '%s' and area_s = '%s' and us_s = '%s'")%(sito,area,us) 
        
        res = self._execute_sql(sql_query_string)
        rows= res.fetchall()
        return rows
    
    def select_medianame_3_from_db_sql(self,sito,area,us):
        sql_query_string = ("SELECT c.filepath, b.us,a.media_name FROM media_to_entity_table as a,  inventario_materiali_table as b, media_thumb_table as c WHERE b.id_invmat=a.id_entity and c.id_media=a.id_media  and b.sito= '%s' and b.area='%s' and us = '%s'")%(sito,area,us) 
        
        res = self._execute_sql(sql_query_string)
        rows= res.fetchall()
        return rows
    
    def select_thumbnail_from_db_sql(self,sito):
        sql_query_string = ("SELECT c.filepath, group_concat ((select us from us_table where id_us like id_entity))as us,a.media_name,b.area,b.unita_tipo FROM  media_to_entity_table as a,  us_table as b, media_thumb_table as c WHERE b.id_us=a.id_entity and c.id_media=a.id_media and sito='%s' group by a.media_name order by a.media_name asc")%(sito)
        res = self._execute_sql(sql_query_string)
        rows= res.fetchall()
        return rows
    
    def select_quote_from_db_sql(self, sito, area, us):
        sql_query_string = ("SELECT * FROM pyarchinit_quote WHERE sito_q = '%s' AND area_q = '%s' AND us_q = '%s'") % (
        sito, area, us)
        res = self._execute_sql(sql_query_string)
        return res
    def select_us_from_db_sql(self, sito, area, us, stratigraph_index_us):
        sql_query_string = (
                           "SELECT * FROM pyunitastratigrafiche WHERE scavo_s = '%s' AND area_s = '%s' AND us_s = '%s' AND stratigraph_index_us = '%s'") % (
                           sito, area, us, stratigraph_index_us)
        res = self._execute_sql(sql_query_string)
        return res

    # def select_us_doc_from_db_sql(self, sito, tipo_doc, nome_doc):
    #     sql_query_string = (
    #                        "SELECT * FROM pyunitastratigrafiche WHERE scavo_s = '%s' AND tipo_doc = '%s' AND nome_doc = '%s'") % (
    #                        sito, tipo_doc, nome_doc)
    #     res = self._execute_sql(sql_query_string)
    #     return res
    #
    # def select_usneg_doc_from_db_sql(self, sito, tipo_doc, nome_doc):
    #     sql_query_string = (
    #                        "SELECT * FROM pyarchinit_us_negative_doc WHERE sito_n = '%s' AND  tipo_doc_n = '%s' AND nome_doc_n = '%s'") % (
    #                        sito, tipo_doc, nome_doc)
    #     res = self._execute_sql(sql_query_string)
    #     return res
    def select_us_doc_from_db_sql(self, sito, tipo_doc, nome_doc):


        sql_query = text(
            "SELECT * FROM pyunitastratigrafiche WHERE scavo_s = :sito AND tipo_doc = :tipo_doc AND nome_doc = :nome_doc")

        res = self._execute_sql(sql_query, sito=sito, tipo_doc=tipo_doc, nome_doc=nome_doc)
        return res

    def select_usneg_doc_from_db_sql(self, sito, tipo_doc, nome_doc):


        sql_query = text(
            "SELECT * FROM pyarchinit_us_negative_doc WHERE sito_n = :sito AND tipo_doc_n = :tipo_doc AND nome_doc_n = :nome_doc")

        res = self._execute_sql(sql_query, sito=sito, tipo_doc=tipo_doc, nome_doc=nome_doc)
        return res

    def select_db_sql(self, table):
        sql_query_string = ("SELECT * FROM %s") % table
        res = self._execute_sql(sql_query_string)
        return res
    
    def select_db_sql_2(self, sito,area,us,d_stratigrafica):
        sql_query_string = ("SELECT * FROM us_table as a where a.sito='%s' AND a.area='%s' AND a.us='%s' AND a.d_stratigrafica='%s'") % (sito,area,us,d_stratigrafica)
        res = self._execute_sql(sql_query_string)
        rows= res.fetchall()
        
        return rows
    
    
    def test_ut_sql(self,unita_tipo):
        sql_query_string = ("SELECT %s FROM us_table")% (unita_tipo)
        res = self._execute_sql(sql_query_string)
        return res





    def query_in_contains_onlysqlite(self, value_list, sitof, areaf, chunk_size=100):
        """
        Esegue una query suddividendo la lista dei valori in chunk per evitare il limite di profondità di SQLite.

        Args:
            value_list (list): Lista di valori da cercare.
            sitof (str): Valore per il filtro 'sito'.
            areaf (str): Valore per il filtro 'area'.
            chunk_size (int): Dimensione dei chunk. Default è 100.

        Returns:
            list: Lista dei risultati della query.
        """
        self.value_list = value_list

        # Configura la sessione
        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()

        res_list = []

        while self.value_list:
            # Suddividi la lista in chunk
            chunk = self.value_list[:chunk_size]
            self.value_list = self.value_list[chunk_size:]

            # Esegui la query per il chunk
            results = session.query(US) \
                .filter_by(sito=sitof, area=areaf) \
                .filter(or_(*[US.rapporti.contains(v) for v in chunk])) \
                .all()

            res_list.extend(results)

        session.close()
        return res_list
    def query_in_contains(self, value_list, sitof, areaf):
        self.value_list = value_list
        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()
        res_list = []
        n = 500  # smaller chunk size

        while self.value_list:
            chunk = self.value_list[:n]
            self.value_list = self.value_list[n:]
            chunk_query = session.query(US).filter_by(sito=sitof).filter_by(area=areaf).filter(
                or_(*[US.rapporti.contains(v) for v in chunk])).all()
            res_list.extend(chunk_query)

        session.close()
        return res_list


    # def query_in_contains(self, value_list, sitof, areaf):
    #     # use a copy of the list to avoid emptying the input list
    #     values = value_list[:]
    #     Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
    #     session = Session()
    #     res_list = []
    #     n = len(values) - 1 if values else 0  # handle empty list
    #     while values:
    #         chunk = values[0:n]
    #         values = values[n:]
    #         try:
    #             res_list.extend(session.query(US).filter_by(sito=sitof).filter_by(area=areaf).filter(
    #                 or_(*[US.rapporti.contains(v) for v in chunk])))
    #         except Exception as e:
    #             print(f"Error while executing query: {e}")
    #             continue
    #     session.close()
    #     return res_list

    # def query_in_contains(self, value_list, sitof, areaf):
    #
    #     self.value_list = value_list
    #
    #     Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
    #     session = Session()
    #
    #     res_list = []
    #     n = len(self.value_list) - 1
    #
    #     while self.value_list:
    #
    #         chunk = self.value_list[0:n]
    #         self.value_list = self.value_list[n:]
    #         res_list.extend(session.query(US).filter_by(sito=sitof).filter_by(area=areaf).filter(
    #             or_(*[US.rapporti.contains(v) for v in chunk])))
    #         # res_list.extend(us for us, in session.query(US.us).filter(or_(*[US.rapporti.contains(v) for v in chunk])))
    #     session.close()
    #     return res_list

    def insert_arbitrary_number_of_us_records(self, us_range, sito, area, n_us, unita_tipo):
        id_us = self.max_num_id('US', 'id_us')
        
        l=QgsSettings().value("locale/userLocale", "it", type=str)[:2]

        for i in range(us_range):
            id_us += 1

            data_ins = self.insert_values(id_us, sito, area, n_us, '', '', '', '', '', '', '', '', '', '', '', '', '[]',
                                          '[]', '[]', '', '', '', '', '', '', '', '', '0', '[]', unita_tipo, '', '', '', '',
                                          '', '', '', '', '', '', '', '', '', None, None, '', '[]','[]', '[]', '[]', '[]','','','','',None,None,'','','','','','','[]','[]',None,None,None,None,None,None,None,None,None,None,'','','','','','','','','','',None,None,None,'','','','','','','','','','','','','','','','','','','','','','','','','','','','','')
                                           
            self.insert_data_session(data_ins)
            n_us += 1
        return

    def insert_number_of_rapporti_records(self, sito, area, n_us, n_rapporti, unita_tipo):
        id_us = self.max_num_id('US', 'id_us')
        l = QgsSettings().value("locale/userLocale", "it", type=str)[:2]

        if l == 'it':
            text = "SCHEDA CREATA IN AUTOMATICO"
        else:
            text = "FORM MADE AUTOMATIC"

        id_us += 1

        # Inseriamo `n_rapporti` nella posizione corretta come lista di liste
        rapporti_list = [[rapporto_tipo, rapporto_n_us, rapporto_area, rapporto_sito] for
                         rapporto_tipo, rapporto_n_us, rapporto_area, rapporto_sito in n_rapporti]

        data_ins = self.insert_values(id_us, sito, area, n_us, text, '', '', '', '', '', '', '', '', '', '', '',
                                      '[]', '[]', str(rapporti_list), '', '', '', '', '', '', '', '', '0', '[]',
                                      unita_tipo,
                                      '', '', '', '',
                                      '', '', '', '', '', '', '', '', '', None, None, '', '[]', '[]', '[]', '[]', '[]',
                                      '', '', '', '', None, None, '', '', '', '', '', '', '[]', '[]', None, None, None,
                                      None, None, None, None, None, None, None, '', '', '', '', '', '', '', '', '', '',
                                      None, None, None, '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
                                      '', '', '', '', '', '', '', '', '', '', '', '', '')

        self.insert_data_session(data_ins)

        return



    def insert_number_of_us_records(self, sito, area, n_us,unita_tipo):
        id_us = self.max_num_id('US', 'id_us')
        #text = "SCHEDA CREATA IN AUTOMATICO"
        l=QgsSettings().value("locale/userLocale", "it", type=str)[:2]

        if l == 'it':
            text = "SCHEDA CREATA IN AUTOMATICO"
            #unita_tipo
        else:
            text = "FORM MADE AUTOMATIC"
            #unita_tipo = 'SU'
        id_us += 1

        data_ins = self.insert_values(id_us, sito, area, n_us, text, '', '', '', '', '', '', '', '', '', '', '', '[]',
                                      '[]', '[]', '', '', '', '', '', '', '', '', '0', '[]', unita_tipo, '', '', '', '',
                                      '', '', '', '', '', '', '', '', '', None, None, '', '[]', '[]', '[]', '[]', '[]',
                                      '', '', '', '', None, None, '', '', '', '', '', '', '[]', '[]', None, None, None,
                                      None, None, None, None, None, None, None, '', '', '', '', '', '', '', '', '', '',
                                      None, None, None, '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
                                      '', '', '', '', '', '', '', '', '', '', '', '', '')

        self.insert_data_session(data_ins)

        return
    
    def insert_number_of_reperti_records(self, sito, numero_inventario):
        id_invmat = self.max_num_id('INVENTARIO_MATERIALI', 'id_invmat')
        
        l=QgsSettings().value("locale/userLocale", "it", type=str)[:2]

        
        id_invmat += 1

        data_ins = self.insert_values_reperti(id_invmat, sito, numero_inventario, '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', None, None, '', None, '', '','0','','','')
                                           
        self.insert_data_session(data_ins)
        
        
        return

    def insert_number_of_pottery_records(self,  id_number,sito, area,us):
        id_rep = self.max_num_id('POTTERY', 'id_rep')

        l = QgsSettings().value("locale/userLocale", "it", type=str)[:2]

        id_rep += 1

        data_ins = self.insert_pottery_values(id_rep, id_number, sito, area, us, 0, '', '', 0, '', '', '', '',
                                              '', '', '', '', '', '', '', '', '', '', None, 0, None, None, None, None, '',
                                              0, '', '', '', '')

        self.insert_data_session(data_ins)

        return
    
    
    
    def insert_number_of_tomba_records(self, sito, nr_scheda_taf):
        id_tomba = self.max_num_id('TOMBA', 'id_tomba')
        
        l=QgsSettings().value("locale/userLocale", "it", type=str)[:2]

        
        id_tomba += 1

        data_ins = self.insert_values_tomba(id_tomba, sito, '', nr_scheda_taf, '', '', '', '', '', '', '', '', '', '', '', '', '','', '', '', '', '', '', '', '','')
                                           
        self.insert_data_session(data_ins)
        
        return
    def insert_struttura_records(self, sito, sigla_struttura,numero_struttura):
        id_struttura = self.max_num_id('STRUTTURA', 'id_struttura')
        
        l=QgsSettings().value("locale/userLocale", "it", type=str)[:2]

        
        id_struttura += 1

        data_ins = self.insert_struttura_values(id_struttura, sito, sigla_struttura, numero_struttura, '', '', '', '', '', '', '', '', '', '', '', '', '', '')
                                           
        self.insert_data_session(data_ins)
        
        return
    def select_like_from_db_sql(self, rapp_list, us_rapp_list):
        # this is a test
        pass

    ##      self.us_rapp_list = us_rapp_list
    ##      rapp_type = rapp_list
    ##      query_string_base = """session.query(US).filter(or_("""
    ##      query_list = []
    ##
    ##      #costruisce la stringa che trova i like
    ##      for sing_us_rapp in self.us_rapp_list:
    ##          for sing_rapp in rapp_type:
    ##              sql_query_string = """US.rapporti.contains("[u'%s', u'%s']")""" % (sing_rapp,sing_us_rapp) #funziona!!!
    ##              query_list.append(sql_query_string)
    ##
    ##      string_contains = ""
    ##      for sing_contains in range(len(query_list)):
    ##          if sing_contains == 0:
    ##              string_contains = query_list[sing_contains]
    ##          else:
    ##              string_contains = string_contains + "," + query_list[sing_contains]
    ##
    ##      query_string_execute = query_string_base + string_contains + '))'
    ##
    ##      Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
    ##      session = Session()
    ##      res = eval(query_string_execute)
    ##
    ##      return res

    # def select_not_like_from_db_sql(self, sitof, areaf):
    #     # NB per funzionare con postgres è necessario che al posto di " ci sia '
    #     l=QgsSettings().value("locale/userLocale", "it", type=str)[:2]
    #     Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
    #     session = Session()
    #
    #     if l=='it':
    #         res = session.query(US).filter_by(sito=sitof).filter_by(area=areaf).filter(
    #             and_(~US.rapporti.like("%'>>'%"),~US.rapporti.like("%'Copre'%"), ~US.rapporti.like("%'Riempie'%"),
    #                  ~US.rapporti.like("%'Taglia'%"), ~US.rapporti.like("%'Si appoggia a'%")))
    #             # MyModel.query.filter(sqlalchemy.not_(Mymodel.name.contains('a_string')))
    #     elif l=='en':
    #         res = session.query(US).filter_by(sito=sitof).filter_by(area=areaf).filter(
    #             and_(~US.rapporti.like("%'Cuts'%"), ~US.rapporti.like("%'Abuts'%"),
    #                  ~US.rapporti.like("%'Covers'%"), ~US.rapporti.like("%'Fills'%")))
    #         # MyModel.query.filter(sqlalchemy.not_(Mymodel.name.contains('a_string')))
    #     elif l=='de':
    #         res = session.query(US).filter_by(sito=sitof).filter_by(area=areaf).filter(
    #             and_(~US.rapporti.like("%'Schneidet'%"), ~US.rapporti.like("%'Stützt sich auf'%"),
    #                  ~US.rapporti.like("%'Liegt über'%"), ~US.rapporti.like("%'Verfüllt'%")))
    #         # MyModel.query.filter(sqlalchemy.not_(Mymodel.name.contains('a_string')))
    #     session.close()
    #     #QMessageBox.warning(None, "Messaggio", "DATA LIST" + str(res), QMessageBox.Ok)
    #     return res

    def select_not_like_from_db_sql(self, sitof, areaf):
        l = QgsSettings().value("locale/userLocale", "it", type=str)[:2]
        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()
        res = None

        if l == 'it':
            filters = ["%'>>'%", "%'Copre'%", "%'Riempie'%", "%'Taglia'%", "%'Si appoggia a'%"]
        elif l == 'en':
            filters = ["%'>>'%","%'Cuts'%", "%'Abuts'%", "%'Covers'%", "%'Fills'%"]
        elif l == 'de':
            filters = ["%'>>'%","%'Schneidet'%", "%'Stützt sich auf'%", "%'Liegt über'%", "%'Verfüllt'%"]
        else:
            filters = []  # Add fallback filters or handle this case differently.

        for f in filters:
            res = session.query(US).filter_by(sito=sitof).filter_by(area=areaf).filter(~US.rapporti.like(f))

        session.close()
        return res

    def query_in_idusb(self):
        pass


# def main():
    # db = Pyarchinit_db_management('sqlite:////Users//Luca//pyarchinit_DB_folder//pyarchinit_db.sqlite')
    # db.connection()

    # db.insert_arbitrary_number_of_records(10, 'Giorgio', 1, 1, 'US')  # us_range, sito, area, n_us)
    

# if __name__ == '__main__':
    # main()
class ANSI():
    def background(code):
        return "\33[{code}m".format(code=code)
  
    def style_text(code):
        return "\33[{code}m".format(code=code)
  
    def color_text(code):
        return "\33[{code}m".format(code=code)
  
  
