"""
Database Sync Manager - Sincronizzazione tra database PostgreSQL e/o SQLite

Questo modulo permette di sincronizzare dati tra:
- PostgreSQL ↔ PostgreSQL
- SQLite ↔ SQLite
- PostgreSQL → SQLite
- SQLite → PostgreSQL

Utilizzo:
    sync = DatabaseSyncManager(local_conn, remote_conn)

    # Analizza differenze
    diff = sync.analyze_differences()

    # Download da remoto a locale (solo differenze)
    sync.download_from_remote()

    # Upload da locale a remoto (solo differenze)
    sync.upload_to_remote()
"""

import os
import subprocess
import json
import sqlite3
import csv
import io
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

from qgis.PyQt.QtCore import QObject, pyqtSignal, QThread, QCoreApplication
from qgis.PyQt.QtWidgets import QProgressDialog, QMessageBox, QApplication
from qgis.core import QgsSettings


# ============================================================
# COMPLETE LIST OF PYARCHINIT TABLES
# ============================================================

# Data tables (non-geometric)
DATA_TABLES = [
    'site_table',
    'us_table',
    'inventario_materiali_table',
    'tomba_table',
    'struttura_table',
    'periodizzazione_table',
    'individui_table',
    'campioni_table',
    'documentazione_table',
    'tafonomia_table',
    'archeozoology_table',
    'pottery_table',
    'ut_table',
    'pyusm_table',
    'deteta_table',
    'detsesso_table',
    'campione_table',
    'pdf_administrator_table',
    'fauna_table',
    # TMA tables (materiali)
    'tma_materiali_archeologici',
    'tma_materiali_ripetibili',
    # Additional tables
    'inventario_lapidei_table',
    'pyunitastratigrafiche',
    'pyunitastratigrafiche_usm',
    'pyuscaratterizzazioni',
    'pyuscarlinee',
    'relashionship_check_table',
]

# Thesaurus tables
THESAURUS_TABLES = [
    'pyarchinit_thesaurus_sigle',
    'pyarchinit_us_negative_doc',
    'pyarchinit_ripartizioni_spaziali',
    'pyarchinit_tipologia_doc',
    'pyarchinit_colore_legno_quercia',
    'pyarchinit_colore_materite_ite',
    'pyarchinit_colore_materite_ite_1',
]

# Media tables (excluding views)
MEDIA_TABLES = [
    'media_table',
    'media_thumb_table',
    'media_to_entity_table',
    'media_to_us_table',
]

# Geometric tables (PostGIS/Sketlite) - only actual tables, not views
GEOMETRIC_TABLES = [
    'pyarchinit_siti',
    'pyarchinit_siti_polygonal',
    'pyarchinit_strutture_ipotesi',
]

# Views are NOT synced
GEOMETRIC_VIEWS = [
    'pyarchinit_us_view',
    'pyarchinit_usm_view',
    'pyarchinit_strutture_view',
    'pyarchinit_quote_view',
    'pyarchinit_sezioni_view',
    'pyarchinit_linee_rif_view',
    'pyarchinit_punti_rif_view',
    'pyarchinit_ripartizioni_spaziali_view',
    'pyarchinit_tafonomia_view',
    'pyarchinit_documentazione_view',
    'pyarchinit_campionature_view',
    'pyarchinit_individui_view',
    'pyarchinit_reperti_view',
    'pyarchinit_tomba_view',
    'media_to_entity_table_view',
]

# All tables combined
ALL_TABLES = DATA_TABLES + THESAURUS_TABLES + MEDIA_TABLES + GEOMETRIC_TABLES


@dataclass
class TableDiff:
    """Differences for a single table"""
    table_name: str
    local_count: int = 0
    remote_count: int = 0
    added_local: int = 0      # Records in local but not in remote
    added_remote: int = 0     # Records in remote but not in local
    modified: int = 0         # Records that differ
    error: str = ""


@dataclass
class SyncConfig:
    """Configuration for synchronization"""
    # Local database settings
    local_db_type: str = "postgres"  # "postgres" or "sqlite"
    local_host: str = "localhost"
    local_port: int = 5432
    local_database: str = ""
    local_user: str = "postgres"
    local_password: str = ""
    local_db_path: str = ""  # For SQLite

    # Remote database settings
    remote_db_type: str = "postgres"  # "postgres" or "sqlite"
    remote_host: str = ""
    remote_port: int = 5432
    remote_database: str = "postgres"
    remote_user: str = ""
    remote_password: str = ""
    remote_db_path: str = ""  # For SQLite

    # Tables to sync (default: all)
    tables_to_sync: List[str] = field(default_factory=lambda: ALL_TABLES.copy())

    # Sync options
    sync_geometric: bool = True
    sync_thesaurus: bool = True
    sync_media: bool = True


# ============================================================
# DATABASE ADAPTERS
# ============================================================

class DatabaseAdapter(ABC):
    """Abstract base class for database operations"""

    @abstractmethod
    def get_table_count(self, table: str) -> int:
        pass

    @abstractmethod
    def get_primary_key(self, table: str) -> str:
        pass

    @abstractmethod
    def get_record_ids(self, table: str, pk: str) -> List[str]:
        pass

    @abstractmethod
    def get_table_columns(self, table: str) -> List[str]:
        pass

    @abstractmethod
    def is_view(self, table: str) -> bool:
        pass

    @abstractmethod
    def table_exists(self, table: str) -> bool:
        pass

    @abstractmethod
    def export_records(self, table: str, columns: List[str], pk: str, ids: List[str]) -> List[List[Any]]:
        pass

    @abstractmethod
    def import_records(self, table: str, columns: List[str], records: List[List[Any]]) -> int:
        pass

    @abstractmethod
    def truncate_table(self, table: str) -> bool:
        pass

    @abstractmethod
    def disable_triggers(self, table: str) -> bool:
        pass

    @abstractmethod
    def enable_triggers(self, table: str) -> bool:
        pass


class PostgreSQLAdapter(DatabaseAdapter):
    """PostgreSQL database adapter"""

    def __init__(self, host: str, port: int, database: str, user: str, password: str):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.env = os.environ.copy()
        self.env['PGPASSWORD'] = password
        self.psql = self._get_psql_path()

    def _get_psql_path(self) -> str:
        """Find psql executable"""
        possible_paths = [
            "/Library/PostgreSQL/17/bin/psql",
            "/Library/PostgreSQL/16/bin/psql",
            "/Library/PostgreSQL/15/bin/psql",
            "/usr/local/bin/psql",
            "/usr/bin/psql",
            "psql"
        ]
        for path in possible_paths:
            if os.path.exists(path) or path == "psql":
                return path
        return "psql"

    def _run_query(self, query: str, timeout: int = 30) -> Tuple[bool, str]:
        """Run a SQL query and return success status and output"""
        cmd = [
            self.psql, "-h", self.host, "-p", str(self.port),
            "-U", self.user, "-d", self.database,
            "-t", "-A", "-c", query
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, env=self.env, timeout=timeout)
            return result.returncode == 0, result.stdout.strip()
        except Exception as e:
            return False, str(e)

    def get_table_count(self, table: str) -> int:
        success, output = self._run_query(f"SELECT COUNT(*) FROM {table};")
        if success and output:
            try:
                return int(output)
            except:
                pass
        return -1

    def get_primary_key(self, table: str) -> str:
        query = f"""
            SELECT a.attname FROM pg_index i
            JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
            WHERE i.indrelid = '{table}'::regclass AND i.indisprimary;
        """
        success, output = self._run_query(query)
        if success and output:
            return output.split('\n')[0]
        return ''

    def get_record_ids(self, table: str, pk: str) -> List[str]:
        success, output = self._run_query(f"SELECT {pk} FROM {table} ORDER BY {pk};", timeout=60)
        if success and output:
            return [x.strip() for x in output.split('\n') if x.strip()]
        return []

    def get_table_columns(self, table: str) -> List[str]:
        query = f"""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = '{table}' AND table_schema = 'public'
            ORDER BY ordinal_position;
        """
        success, output = self._run_query(query)
        if success and output:
            return [x.strip() for x in output.split('\n') if x.strip()]
        return []

    def is_view(self, table: str) -> bool:
        query = f"SELECT table_type FROM information_schema.tables WHERE table_name = '{table}' AND table_schema = 'public';"
        success, output = self._run_query(query)
        if success:
            return 'VIEW' in output.upper()
        return False

    def table_exists(self, table: str) -> bool:
        query = f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '{table}' AND table_schema = 'public');"
        success, output = self._run_query(query)
        if success:
            return output.lower() == 't'
        return False

    def export_records(self, table: str, columns: List[str], pk: str, ids: List[str]) -> List[List[Any]]:
        """Export records as list of rows"""
        if not ids:
            return []

        records = []
        batch_size = 100

        for batch_start in range(0, len(ids), batch_size):
            batch_ids = ids[batch_start:batch_start + batch_size]
            ids_str = ','.join(str(i) for i in batch_ids)
            columns_str = ', '.join(columns)

            query = f"COPY (SELECT {columns_str} FROM {table} WHERE {pk} IN ({ids_str})) TO STDOUT WITH (FORMAT csv, HEADER false, NULL '')"

            cmd = [
                self.psql, "-h", self.host, "-p", str(self.port),
                "-U", self.user, "-d", self.database,
                "-c", query
            ]

            try:
                result = subprocess.run(cmd, capture_output=True, text=True, env=self.env, timeout=300)
                if result.returncode == 0 and result.stdout.strip():
                    reader = csv.reader(io.StringIO(result.stdout))
                    for row in reader:
                        records.append(row)
            except Exception as e:
                print(f"Export error for {table}: {e}")

        return records

    def import_records(self, table: str, columns: List[str], records: List[List[Any]]) -> int:
        """Import records into table"""
        if not records:
            return 0

        columns_str = ', '.join(columns)
        imported = 0

        # Write records to CSV string
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerows(records)
        csv_data = output.getvalue()

        query = f"COPY {table} ({columns_str}) FROM STDIN WITH (FORMAT csv, HEADER false, NULL '')"

        cmd = [
            self.psql, "-h", self.host, "-p", str(self.port),
            "-U", self.user, "-d", self.database,
            "-c", query
        ]

        try:
            result = subprocess.run(cmd, input=csv_data, capture_output=True, text=True, env=self.env, timeout=600)
            if result.returncode == 0:
                imported = len(records)
        except Exception as e:
            print(f"Import error for {table}: {e}")

        return imported

    def truncate_table(self, table: str) -> bool:
        cmd = [
            self.psql, "-h", self.host, "-p", str(self.port),
            "-U", self.user, "-d", self.database,
            "-c", f"TRUNCATE {table} CASCADE;"
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, env=self.env, timeout=60)
            return result.returncode == 0
        except:
            return False

    def disable_triggers(self, table: str) -> bool:
        success, _ = self._run_query(f"ALTER TABLE {table} DISABLE TRIGGER ALL;")
        return success

    def enable_triggers(self, table: str) -> bool:
        success, _ = self._run_query(f"ALTER TABLE {table} ENABLE TRIGGER ALL;")
        return success


class SQLiteAdapter(DatabaseAdapter):
    """SQLite database adapter"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"SQLite database not found: {db_path}")

    def _get_connection(self) -> sqlite3.Connection:
        """Get a new database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        # Enable loading extensions for spatialite
        conn.enable_load_extension(True)

        # Find and load SpatiaLite extension
        spatialite_path = self._find_spatialite_path()
        try:
            if spatialite_path:
                conn.execute(f"SELECT load_extension('{spatialite_path}')")
            else:
                conn.execute("SELECT load_extension('mod_spatialite')")
        except:
            try:
                conn.execute("SELECT load_extension('libspatialite')")
            except:
                pass  # Spatialite not available
        return conn

    def _find_spatialite_path(self) -> Optional[str]:
        """Find the path to mod_spatialite library"""
        import glob
        import platform

        # First try QGIS's built-in finder
        try:
            from qgis.find_mod_spatialite import mod_spatialite_path
            path = mod_spatialite_path()
            if path and os.path.exists(path):
                return path
        except Exception:
            pass

        # Platform-specific paths
        if platform.system() == 'Darwin':  # macOS
            search_paths = (
                glob.glob('/Applications/QGIS*.app/Contents/MacOS/lib/mod_spatialite*.so') +
                ['/opt/homebrew/lib/mod_spatialite.dylib',
                 '/opt/homebrew/lib/mod_spatialite.so',
                 '/usr/local/lib/mod_spatialite.dylib',
                 '/usr/local/lib/mod_spatialite.so',
                 '/opt/local/lib/mod_spatialite.dylib',
                 '/opt/local/lib/mod_spatialite.so']
            )
        elif platform.system() == 'Windows':
            search_paths = ['mod_spatialite.dll']
        else:  # Linux
            search_paths = [
                '/usr/lib/x86_64-linux-gnu/mod_spatialite.so',
                '/usr/lib/mod_spatialite.so',
                'mod_spatialite.so'
            ]

        for path in search_paths:
            if os.path.exists(path):
                return path

        return None

    def get_table_count(self, table: str) -> int:
        try:
            conn = self._get_connection()
            cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception as e:
            print(f"Count error for {table}: {e}")
            return -1

    def get_primary_key(self, table: str) -> str:
        try:
            conn = self._get_connection()
            cursor = conn.execute(f"PRAGMA table_info({table})")
            for row in cursor:
                if row['pk'] == 1:
                    conn.close()
                    return row['name']
            conn.close()
        except Exception as e:
            print(f"PK error for {table}: {e}")
        return ''

    def get_record_ids(self, table: str, pk: str) -> List[str]:
        try:
            conn = self._get_connection()
            cursor = conn.execute(f"SELECT {pk} FROM {table} ORDER BY {pk}")
            ids = [str(row[0]) for row in cursor]
            conn.close()
            return ids
        except Exception as e:
            print(f"Get IDs error for {table}: {e}")
            return []

    def get_table_columns(self, table: str) -> List[str]:
        try:
            conn = self._get_connection()
            cursor = conn.execute(f"PRAGMA table_info({table})")
            columns = [row['name'] for row in cursor]
            conn.close()
            return columns
        except Exception as e:
            print(f"Get columns error for {table}: {e}")
            return []

    def is_view(self, table: str) -> bool:
        try:
            conn = self._get_connection()
            cursor = conn.execute(
                "SELECT type FROM sqlite_master WHERE name = ? AND type = 'view'",
                (table,)
            )
            result = cursor.fetchone() is not None
            conn.close()
            return result
        except:
            return False

    def table_exists(self, table: str) -> bool:
        try:
            conn = self._get_connection()
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name = ?",
                (table,)
            )
            result = cursor.fetchone() is not None
            conn.close()
            return result
        except:
            return False

    def export_records(self, table: str, columns: List[str], pk: str, ids: List[str]) -> List[List[Any]]:
        """Export records as list of rows"""
        if not ids:
            return []

        records = []
        try:
            conn = self._get_connection()
            columns_str = ', '.join(columns)

            # Process in batches
            batch_size = 100
            for batch_start in range(0, len(ids), batch_size):
                batch_ids = ids[batch_start:batch_start + batch_size]
                placeholders = ','.join('?' * len(batch_ids))
                query = f"SELECT {columns_str} FROM {table} WHERE {pk} IN ({placeholders})"
                cursor = conn.execute(query, batch_ids)
                for row in cursor:
                    records.append(list(row))

            conn.close()
        except Exception as e:
            print(f"Export error for {table}: {e}")

        return records

    def _get_column_types(self, table: str) -> Dict[str, str]:
        """Get column types for a table"""
        types = {}
        try:
            conn = self._get_connection()
            cursor = conn.execute(f"PRAGMA table_info({table})")
            for row in cursor:
                types[row['name']] = row['type'].upper()
            conn.close()
        except:
            pass
        return types

    def _convert_empty_to_null(self, columns: List[str], record: List[Any], col_types: Dict[str, str]) -> List[Any]:
        """Convert empty strings to None for numeric columns"""
        result = []
        for i, (col, val) in enumerate(zip(columns, record)):
            col_type = col_types.get(col, '')
            # Check if column is numeric
            is_numeric = any(t in col_type for t in ['INT', 'REAL', 'NUM', 'DECIMAL', 'FLOAT', 'DOUBLE'])
            # Convert empty string to None for numeric columns
            if is_numeric and val == '':
                result.append(None)
            else:
                result.append(val)
        return result

    def import_records(self, table: str, columns: List[str], records: List[List[Any]]) -> int:
        """Import records into table"""
        if not records:
            return 0

        imported = 0
        try:
            conn = self._get_connection()
            columns_str = ', '.join(columns)
            placeholders = ', '.join('?' * len(columns))
            query = f"INSERT OR REPLACE INTO {table} ({columns_str}) VALUES ({placeholders})"

            # Get column types for empty string -> NULL conversion
            col_types = self._get_column_types(table)

            for record in records:
                try:
                    # Convert empty strings to None for numeric columns
                    cleaned_record = self._convert_empty_to_null(columns, record, col_types)
                    conn.execute(query, cleaned_record)
                    imported += 1
                except Exception as e:
                    print(f"Insert error for {table}: {e}")

            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Import error for {table}: {e}")

        return imported

    def truncate_table(self, table: str) -> bool:
        try:
            conn = self._get_connection()
            conn.execute(f"DELETE FROM {table}")
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Truncate error for {table}: {e}")
            return False

    def disable_triggers(self, table: str) -> bool:
        # SQLite triggers are always enabled, but we can use PRAGMA
        return True

    def enable_triggers(self, table: str) -> bool:
        return True


def create_adapter(config: SyncConfig, is_local: bool) -> DatabaseAdapter:
    """Factory function to create the appropriate database adapter"""
    if is_local:
        db_type = config.local_db_type
        if db_type == "sqlite":
            return SQLiteAdapter(config.local_db_path)
        else:
            return PostgreSQLAdapter(
                config.local_host, config.local_port,
                config.local_database, config.local_user, config.local_password
            )
    else:
        db_type = config.remote_db_type
        if db_type == "sqlite":
            return SQLiteAdapter(config.remote_db_path)
        else:
            return PostgreSQLAdapter(
                config.remote_host, config.remote_port,
                config.remote_database, config.remote_user, config.remote_password
            )


# ============================================================
# SYNC ANALYZER
# ============================================================

class SyncAnalyzer(QThread):
    """Thread to analyze differences between databases"""
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(list)  # List of TableDiff
    error = pyqtSignal(str)

    def __init__(self, config: SyncConfig, parent=None):
        super().__init__(parent)
        self.config = config
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        try:
            differences = []
            tables = self.config.tables_to_sync
            total = len(tables)

            # Create adapters
            try:
                local_adapter = create_adapter(self.config, is_local=True)
                remote_adapter = create_adapter(self.config, is_local=False)
            except Exception as e:
                self.error.emit(f"Connection error: {str(e)}")
                return

            for idx, table in enumerate(tables):
                if self._cancelled:
                    return

                percent = int((idx / total) * 100)
                self.progress.emit(percent, f"Analyzing {table}...")

                diff = TableDiff(table_name=table)

                try:
                    # Skip views
                    if local_adapter.is_view(table) or remote_adapter.is_view(table):
                        continue

                    # Count records
                    diff.local_count = local_adapter.get_table_count(table)
                    diff.remote_count = remote_adapter.get_table_count(table)

                    # Get primary key
                    pk = local_adapter.get_primary_key(table)
                    if not pk:
                        pk = remote_adapter.get_primary_key(table)

                    if pk:
                        # Get IDs from both databases
                        local_ids = set(local_adapter.get_record_ids(table, pk))
                        remote_ids = set(remote_adapter.get_record_ids(table, pk))

                        diff.added_local = len(local_ids - remote_ids)
                        diff.added_remote = len(remote_ids - local_ids)

                except Exception as e:
                    diff.error = str(e)[:100]

                differences.append(diff)

            self.progress.emit(100, "Analysis complete")
            self.finished.emit(differences)

        except Exception as e:
            self.error.emit(str(e))


# ============================================================
# SYNC WORKER
# ============================================================

class SyncWorker(QThread):
    """Worker thread for sync operations"""
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(bool, str)
    error = pyqtSignal(str)

    def __init__(self, operation: str, config: SyncConfig, tables_to_sync: List[str] = None, parent=None):
        super().__init__(parent)
        self.operation = operation
        self.config = config
        self.tables_to_sync = tables_to_sync or config.tables_to_sync
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        try:
            if self.operation == "download":
                self._download_from_remote()
            elif self.operation == "upload":
                self._upload_to_remote()
            elif self.operation == "differential_download":
                self._differential_download()
            elif self.operation == "differential_upload":
                self._differential_upload()
        except Exception as e:
            self.error.emit(str(e))
            self.finished.emit(False, str(e))

    def _download_from_remote(self):
        """Download data from remote to local (full sync)"""
        tables = self.tables_to_sync
        total = len(tables)

        self.progress.emit(0, QCoreApplication.translate("SyncWorker", "Connecting..."))

        try:
            local_adapter = create_adapter(self.config, is_local=True)
            remote_adapter = create_adapter(self.config, is_local=False)
        except Exception as e:
            self.error.emit(f"Connection error: {str(e)}")
            self.finished.emit(False, str(e))
            return

        synced = 0
        errors = 0

        for idx, table in enumerate(tables):
            if self._cancelled:
                self.finished.emit(False, QCoreApplication.translate("SyncWorker", "Operation cancelled"))
                return

            percent = int((idx / total) * 100)
            self.progress.emit(percent, QCoreApplication.translate("SyncWorker", "Downloading {0}...").format(table))

            try:
                # Skip views
                if remote_adapter.is_view(table):
                    continue

                # Check if table exists
                if not remote_adapter.table_exists(table):
                    continue
                if not local_adapter.table_exists(table):
                    errors += 1
                    continue

                # Get columns and pk from both databases
                remote_columns = remote_adapter.get_table_columns(table)
                local_columns = local_adapter.get_table_columns(table)
                pk = remote_adapter.get_primary_key(table)
                if not remote_columns or not local_columns or not pk:
                    errors += 1
                    continue

                # Use only columns that exist in BOTH databases (preserving remote column order)
                local_columns_set = set(local_columns)
                columns = [c for c in remote_columns if c in local_columns_set]
                if not columns:
                    errors += 1
                    continue

                # Get all remote IDs
                remote_ids = remote_adapter.get_record_ids(table, pk)
                if not remote_ids:
                    continue

                # Truncate local table
                local_adapter.truncate_table(table)

                # Export from remote and import to local
                records = remote_adapter.export_records(table, columns, pk, remote_ids)
                if records:
                    imported = local_adapter.import_records(table, columns, records)
                    if imported > 0:
                        synced += 1
                    else:
                        errors += 1

            except Exception as e:
                print(f"Download error for {table}: {e}")
                errors += 1

        self.progress.emit(100, QCoreApplication.translate("SyncWorker", "Download complete!"))
        msg = QCoreApplication.translate("SyncWorker", "Download completed: {0} tables synced, {1} errors").format(synced, errors)
        self.finished.emit(True, msg)

    def _upload_to_remote(self):
        """Upload data from local to remote (full sync)"""
        tables = self.tables_to_sync
        total = len(tables)

        self.progress.emit(0, QCoreApplication.translate("SyncWorker", "Connecting..."))

        try:
            local_adapter = create_adapter(self.config, is_local=True)
            remote_adapter = create_adapter(self.config, is_local=False)
        except Exception as e:
            self.error.emit(f"Connection error: {str(e)}")
            self.finished.emit(False, str(e))
            return

        synced = 0
        errors = 0

        for idx, table in enumerate(tables):
            if self._cancelled:
                self.finished.emit(False, QCoreApplication.translate("SyncWorker", "Operation cancelled"))
                return

            percent = int((idx / total) * 100)
            self.progress.emit(percent, QCoreApplication.translate("SyncWorker", "Uploading {0}...").format(table))

            try:
                # Skip views
                if local_adapter.is_view(table):
                    continue

                # Check if table exists
                if not local_adapter.table_exists(table):
                    continue
                if not remote_adapter.table_exists(table):
                    errors += 1
                    continue

                # Get columns and pk from both databases
                local_columns = local_adapter.get_table_columns(table)
                remote_columns = remote_adapter.get_table_columns(table)
                pk = local_adapter.get_primary_key(table)
                if not local_columns or not remote_columns or not pk:
                    errors += 1
                    continue

                # Use only columns that exist in BOTH databases (preserving local column order)
                remote_columns_set = set(remote_columns)
                columns = [c for c in local_columns if c in remote_columns_set]
                if not columns:
                    errors += 1
                    continue

                # Get all local IDs
                local_ids = local_adapter.get_record_ids(table, pk)
                if not local_ids:
                    continue

                # Truncate remote table
                remote_adapter.truncate_table(table)

                # Export from local and import to remote
                records = local_adapter.export_records(table, columns, pk, local_ids)
                if records:
                    imported = remote_adapter.import_records(table, columns, records)
                    if imported > 0:
                        synced += 1
                    else:
                        errors += 1

            except Exception as e:
                print(f"Upload error for {table}: {e}")
                errors += 1

        self.progress.emit(100, QCoreApplication.translate("SyncWorker", "Upload complete!"))
        msg = QCoreApplication.translate("SyncWorker", "Upload completed: {0} tables synced, {1} errors").format(synced, errors)
        self.finished.emit(True, msg)

    def _differential_download(self):
        """Download only changed/new records from remote to local"""
        tables = self.tables_to_sync
        total = len(tables)

        self.progress.emit(0, QCoreApplication.translate("SyncWorker", "Starting differential download..."))

        try:
            local_adapter = create_adapter(self.config, is_local=True)
            remote_adapter = create_adapter(self.config, is_local=False)
        except Exception as e:
            self.error.emit(f"Connection error: {str(e)}")
            self.finished.emit(False, str(e))
            return

        synced = 0
        inserted = 0
        errors = 0
        error_details = []

        for idx, table in enumerate(tables):
            if self._cancelled:
                self.finished.emit(False, QCoreApplication.translate("SyncWorker", "Operation cancelled"))
                return

            percent = int((idx / total) * 100)
            self.progress.emit(percent, QCoreApplication.translate("SyncWorker", "Syncing {0}...").format(table))

            try:
                # Skip views
                if remote_adapter.is_view(table):
                    synced += 1
                    continue

                # Check if tables exist
                if not local_adapter.table_exists(table):
                    error_details.append(f"{table}: table does not exist locally")
                    errors += 1
                    continue

                if not remote_adapter.table_exists(table):
                    continue

                # Get columns and pk from both databases
                remote_columns = remote_adapter.get_table_columns(table)
                local_columns = local_adapter.get_table_columns(table)
                pk = remote_adapter.get_primary_key(table)
                if not pk:
                    pk = local_adapter.get_primary_key(table)
                if not remote_columns or not local_columns or not pk:
                    error_details.append(f"{table}: could not get columns or pk")
                    errors += 1
                    continue

                # Use only columns that exist in BOTH databases (preserving remote column order)
                local_columns_set = set(local_columns)
                columns = [c for c in remote_columns if c in local_columns_set]

                if not columns:
                    error_details.append(f"{table}: no common columns between databases")
                    errors += 1
                    continue

                # Get IDs from both databases
                local_ids = set(local_adapter.get_record_ids(table, pk))
                remote_ids = set(remote_adapter.get_record_ids(table, pk))

                # Records only in remote (to INSERT)
                to_insert = list(remote_ids - local_ids)

                if not to_insert:
                    synced += 1
                    continue

                # Export from remote and import to local
                local_adapter.disable_triggers(table)
                try:
                    records = remote_adapter.export_records(table, columns, pk, to_insert)
                    if records:
                        table_inserted = local_adapter.import_records(table, columns, records)
                        inserted += table_inserted
                        if table_inserted > 0:
                            synced += 1
                finally:
                    local_adapter.enable_triggers(table)

            except Exception as e:
                error_details.append(f"{table}: {str(e)}")
                errors += 1

        self.progress.emit(100, QCoreApplication.translate("SyncWorker", "Differential download complete!"))

        msg = QCoreApplication.translate(
            "SyncWorker",
            "Download completed: {0} tables, {1} inserted, {2} errors"
        ).format(synced, inserted, errors)

        if error_details and len(error_details) <= 3:
            msg += "\n" + "\n".join(error_details[:3])

        self.finished.emit(True, msg)

    def _differential_upload(self):
        """Upload only changed/new records from local to remote"""
        tables = self.tables_to_sync
        total = len(tables)

        self.progress.emit(0, QCoreApplication.translate("SyncWorker", "Starting differential upload..."))

        try:
            local_adapter = create_adapter(self.config, is_local=True)
            remote_adapter = create_adapter(self.config, is_local=False)
        except Exception as e:
            self.error.emit(f"Connection error: {str(e)}")
            self.finished.emit(False, str(e))
            return

        synced = 0
        inserted = 0
        errors = 0
        error_details = []

        for idx, table in enumerate(tables):
            if self._cancelled:
                self.finished.emit(False, QCoreApplication.translate("SyncWorker", "Operation cancelled"))
                return

            percent = int((idx / total) * 100)
            self.progress.emit(percent, QCoreApplication.translate("SyncWorker", "Syncing {0}...").format(table))

            try:
                # Skip views
                if local_adapter.is_view(table):
                    synced += 1
                    continue

                # Check if tables exist
                if not local_adapter.table_exists(table):
                    continue

                if not remote_adapter.table_exists(table):
                    error_details.append(f"{table}: table does not exist on remote")
                    errors += 1
                    continue

                # Get columns and pk from both databases
                local_columns = local_adapter.get_table_columns(table)
                remote_columns = remote_adapter.get_table_columns(table)
                pk = local_adapter.get_primary_key(table)
                if not pk:
                    pk = remote_adapter.get_primary_key(table)
                if not local_columns or not remote_columns or not pk:
                    error_details.append(f"{table}: could not get columns or pk")
                    errors += 1
                    continue

                # Use only columns that exist in BOTH databases (preserving local column order)
                remote_columns_set = set(remote_columns)
                columns = [c for c in local_columns if c in remote_columns_set]

                if not columns:
                    error_details.append(f"{table}: no common columns between databases")
                    errors += 1
                    continue

                # Get IDs from both databases
                local_ids = set(local_adapter.get_record_ids(table, pk))
                remote_ids = set(remote_adapter.get_record_ids(table, pk))

                # Records only in local (to INSERT)
                to_insert = list(local_ids - remote_ids)

                if not to_insert:
                    synced += 1
                    continue

                # Export from local and import to remote
                remote_adapter.disable_triggers(table)
                try:
                    records = local_adapter.export_records(table, columns, pk, to_insert)
                    if records:
                        table_inserted = remote_adapter.import_records(table, columns, records)
                        inserted += table_inserted
                        if table_inserted > 0:
                            synced += 1
                finally:
                    remote_adapter.enable_triggers(table)

            except Exception as e:
                error_details.append(f"{table}: {str(e)}")
                errors += 1

        self.progress.emit(100, QCoreApplication.translate("SyncWorker", "Differential upload complete!"))

        msg = QCoreApplication.translate(
            "SyncWorker",
            "Upload completed: {0} tables, {1} inserted, {2} errors"
        ).format(synced, inserted, errors)

        if error_details and len(error_details) <= 3:
            msg += "\n" + "\n".join(error_details[:3])

        self.finished.emit(True, msg)


# ============================================================
# SYNC MANAGER
# ============================================================

class DatabaseSyncManager(QObject):
    """Manager for database synchronization"""

    sync_started = pyqtSignal()
    sync_progress = pyqtSignal(int, str)
    sync_finished = pyqtSignal(bool, str)
    sync_error = pyqtSignal(str)

    analysis_started = pyqtSignal()
    analysis_progress = pyqtSignal(int, str)
    analysis_finished = pyqtSignal(list)  # List of TableDiff
    analysis_error = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self.analyzer = None
        self.config = None

    def configure(self, local_config: Dict, remote_config: Dict, tables: List[str] = None):
        """Configure sync connections"""
        self.config = SyncConfig(
            # Local settings
            local_db_type=local_config.get('db_type', 'postgres'),
            local_host=local_config.get('host', 'localhost'),
            local_port=int(local_config.get('port', 5432)),
            local_database=local_config.get('database', ''),
            local_user=local_config.get('user', 'postgres'),
            local_password=local_config.get('password', ''),
            local_db_path=local_config.get('db_path', ''),
            # Remote settings
            remote_db_type=remote_config.get('db_type', 'postgres'),
            remote_host=remote_config.get('host', ''),
            remote_port=int(remote_config.get('port', 5432)),
            remote_database=remote_config.get('database', 'postgres'),
            remote_user=remote_config.get('user', ''),
            remote_password=remote_config.get('password', ''),
            remote_db_path=remote_config.get('db_path', ''),
            # Tables
            tables_to_sync=tables if tables else ALL_TABLES.copy()
        )

    def analyze_differences(self):
        """Analyze differences between local and remote databases"""
        if not self.config:
            self.analysis_error.emit("Configuration missing")
            return

        self.analysis_started.emit()

        self.analyzer = SyncAnalyzer(self.config)
        self.analyzer.progress.connect(self.analysis_progress.emit)
        self.analyzer.finished.connect(self._on_analysis_finished)
        self.analyzer.error.connect(self.analysis_error.emit)
        self.analyzer.start()

    def _on_analysis_finished(self, differences: List[TableDiff]):
        self.analysis_finished.emit(differences)

    def download_from_remote(self, tables: List[str] = None, differential: bool = False):
        """Download from remote to local"""
        if not self.config:
            self.sync_error.emit("Configuration missing")
            return

        self.sync_started.emit()

        operation = "differential_download" if differential else "download"
        self.worker = SyncWorker(operation, self.config, tables)
        self.worker.progress.connect(self.sync_progress.emit)
        self.worker.finished.connect(self._on_finished)
        self.worker.error.connect(self.sync_error.emit)
        self.worker.start()

    def upload_to_remote(self, tables: List[str] = None, differential: bool = False):
        """Upload from local to remote"""
        if not self.config:
            self.sync_error.emit("Configuration missing")
            return

        self.sync_started.emit()

        operation = "differential_upload" if differential else "upload"
        self.worker = SyncWorker(operation, self.config, tables)
        self.worker.progress.connect(self.sync_progress.emit)
        self.worker.finished.connect(self._on_finished)
        self.worker.error.connect(self.sync_error.emit)
        self.worker.start()

    def cancel(self):
        """Cancel current operation"""
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
        if self.analyzer and self.analyzer.isRunning():
            self.analyzer.cancel()

    def _on_finished(self, success: bool, message: str):
        self.sync_finished.emit(success, message)

    def is_running(self) -> bool:
        """Check if an operation is running"""
        return (self.worker is not None and self.worker.isRunning()) or \
               (self.analyzer is not None and self.analyzer.isRunning())


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_sync_config_from_settings() -> Tuple[Dict, Dict]:
    """Get sync configurations from QGIS settings"""
    s = QgsSettings()

    local_config = {
        'db_type': s.value('pyArchInit/local_db_type', 'postgres'),
        'host': s.value('pyArchInit/local_host', 'localhost'),
        'port': int(s.value('pyArchInit/local_port', 5432)),
        'database': s.value('pyArchInit/local_database', ''),
        'user': s.value('pyArchInit/local_user', 'postgres'),
        'password': s.value('pyArchInit/local_password', ''),
        'db_path': s.value('pyArchInit/local_db_path', '')
    }

    remote_config = {
        'db_type': s.value('pyArchInit/remote_db_type', 'postgres'),
        'host': s.value('pyArchInit/remote_host', ''),
        'port': int(s.value('pyArchInit/remote_port', 5432)),
        'database': s.value('pyArchInit/remote_database', 'postgres'),
        'user': s.value('pyArchInit/remote_user', ''),
        'password': s.value('pyArchInit/remote_password', ''),
        'db_path': s.value('pyArchInit/remote_db_path', '')
    }

    return local_config, remote_config


def save_sync_config_to_settings(local_config: Dict, remote_config: Dict):
    """Save sync configurations to QGIS settings"""
    s = QgsSettings()

    s.setValue('pyArchInit/local_db_type', local_config.get('db_type', 'postgres'))
    s.setValue('pyArchInit/local_host', local_config.get('host', 'localhost'))
    s.setValue('pyArchInit/local_port', local_config.get('port', 5432))
    s.setValue('pyArchInit/local_database', local_config.get('database', ''))
    s.setValue('pyArchInit/local_user', local_config.get('user', 'postgres'))
    s.setValue('pyArchInit/local_password', local_config.get('password', ''))
    s.setValue('pyArchInit/local_db_path', local_config.get('db_path', ''))

    s.setValue('pyArchInit/remote_db_type', remote_config.get('db_type', 'postgres'))
    s.setValue('pyArchInit/remote_host', remote_config.get('host', ''))
    s.setValue('pyArchInit/remote_port', remote_config.get('port', 5432))
    s.setValue('pyArchInit/remote_database', remote_config.get('database', 'postgres'))
    s.setValue('pyArchInit/remote_user', remote_config.get('user', ''))
    s.setValue('pyArchInit/remote_password', remote_config.get('password', ''))
    s.setValue('pyArchInit/remote_db_path', remote_config.get('db_path', ''))
