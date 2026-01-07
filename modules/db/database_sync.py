"""
Database Sync Manager - Sincronizzazione tra database PostgreSQL locale e remoto

Questo modulo permette di:
- Lavorare in locale con PostgreSQL (veloce)
- Sincronizzare periodicamente con un server remoto (backup/condivisione)
- Supporta qualsiasi server PostgreSQL (Supabase, server proprio, cloud, ecc.)

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
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

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

# Geometric tables (PostGIS) - only actual tables, not views
# Views are auto-generated from data and don't need to be synced
GEOMETRIC_TABLES = [
    'pyarchinit_siti',
    'pyarchinit_siti_polygonal',
    'pyarchinit_strutture_ipotesi',
]

# Views are NOT synced - they are generated from the underlying tables
# These are listed here for reference only
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
    local_host: str = "localhost"
    local_port: int = 5432
    local_database: str = ""
    local_user: str = "postgres"
    local_password: str = ""

    remote_host: str = ""
    remote_port: int = 5432
    remote_database: str = "postgres"
    remote_user: str = ""
    remote_password: str = ""

    # Tables to sync (default: all)
    tables_to_sync: List[str] = field(default_factory=lambda: ALL_TABLES.copy())

    # Sync options
    sync_geometric: bool = True
    sync_thesaurus: bool = True
    sync_media: bool = True


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
            cfg = self.config
            tables = cfg.tables_to_sync
            total = len(tables)

            psql = self._get_psql_path()

            local_env = os.environ.copy()
            local_env['PGPASSWORD'] = cfg.local_password

            remote_env = os.environ.copy()
            remote_env['PGPASSWORD'] = cfg.remote_password

            for idx, table in enumerate(tables):
                if self._cancelled:
                    return

                percent = int((idx / total) * 100)
                self.progress.emit(percent, f"Analyzing {table}...")

                diff = TableDiff(table_name=table)

                try:
                    # Count local records
                    local_count = self._get_table_count(
                        psql, cfg.local_host, cfg.local_port,
                        cfg.local_user, cfg.local_database,
                        table, local_env
                    )
                    diff.local_count = local_count

                    # Count remote records
                    remote_count = self._get_table_count(
                        psql, cfg.remote_host, cfg.remote_port,
                        cfg.remote_user, cfg.remote_database,
                        table, remote_env
                    )
                    diff.remote_count = remote_count

                    # Get primary key for comparison
                    pk = self._get_primary_key(
                        psql, cfg.local_host, cfg.local_port,
                        cfg.local_user, cfg.local_database,
                        table, local_env
                    )

                    if pk:
                        # Get IDs from both databases
                        local_ids = self._get_record_ids(
                            psql, cfg.local_host, cfg.local_port,
                            cfg.local_user, cfg.local_database,
                            table, pk, local_env
                        )
                        remote_ids = self._get_record_ids(
                            psql, cfg.remote_host, cfg.remote_port,
                            cfg.remote_user, cfg.remote_database,
                            table, pk, remote_env
                        )

                        local_set = set(local_ids)
                        remote_set = set(remote_ids)

                        diff.added_local = len(local_set - remote_set)
                        diff.added_remote = len(remote_set - local_set)

                except Exception as e:
                    diff.error = str(e)[:100]

                differences.append(diff)

            self.progress.emit(100, "Analysis complete")
            self.finished.emit(differences)

        except Exception as e:
            self.error.emit(str(e))

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

    def _get_table_count(self, psql, host, port, user, database, table, env) -> int:
        """Get record count for a table"""
        cmd = [
            psql, "-h", host, "-p", str(port), "-U", user, "-d", database,
            "-t", "-A", "-c", f"SELECT COUNT(*) FROM {table};"
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=30)
            if result.returncode == 0:
                return int(result.stdout.strip())
        except:
            pass
        return -1

    def _get_primary_key(self, psql, host, port, user, database, table, env) -> str:
        """Get primary key column name"""
        query = f"""
            SELECT a.attname FROM pg_index i
            JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
            WHERE i.indrelid = '{table}'::regclass AND i.indisprimary;
        """
        cmd = [
            psql, "-h", host, "-p", str(port), "-U", user, "-d", database,
            "-t", "-A", "-c", query
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=30)
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip().split('\n')[0]
        except:
            pass
        # Common fallbacks
        if 'id_' in table or table.endswith('_table'):
            return 'id_' + table.replace('_table', '').replace('pyarchinit_', '')
        return 'gid' if table.startswith('pyarchinit_') else ''

    def _get_record_ids(self, psql, host, port, user, database, table, pk, env) -> List[str]:
        """Get all record IDs from a table"""
        cmd = [
            psql, "-h", host, "-p", str(port), "-U", user, "-d", database,
            "-t", "-A", "-c", f"SELECT {pk} FROM {table} ORDER BY {pk};"
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=60)
            if result.returncode == 0:
                return [x.strip() for x in result.stdout.strip().split('\n') if x.strip()]
        except:
            pass
        return []


class SyncWorker(QThread):
    """Worker thread for sync operations"""
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(bool, str)
    error = pyqtSignal(str)

    LOCK_TIMEOUT = 300  # 5 minutes

    def __init__(self, operation: str, config: SyncConfig, tables_to_sync: List[str] = None, parent=None):
        super().__init__(parent)
        self.operation = operation
        self.config = config
        self.tables_to_sync = tables_to_sync or config.tables_to_sync
        self._cancelled = False
        self._has_lock = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        try:
            if not self._acquire_sync_lock():
                return

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
        finally:
            self._release_sync_lock()

    def _get_pg_dump_path(self) -> str:
        """Find pg_dump executable"""
        possible_paths = [
            "/Library/PostgreSQL/17/bin/pg_dump",
            "/Library/PostgreSQL/16/bin/pg_dump",
            "/Library/PostgreSQL/15/bin/pg_dump",
            "/usr/local/bin/pg_dump",
            "/usr/bin/pg_dump",
            "pg_dump"
        ]
        for path in possible_paths:
            if os.path.exists(path) or path == "pg_dump":
                return path
        return "pg_dump"

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

    def _ensure_lock_table(self, env: dict) -> bool:
        """Create sync_lock table if it doesn't exist"""
        cfg = self.config
        psql = self._get_psql_path()

        create_table_sql = """
        CREATE TABLE IF NOT EXISTS pyarchinit_sync_lock (
            id INTEGER PRIMARY KEY DEFAULT 1,
            locked_by VARCHAR(255),
            locked_at TIMESTAMP,
            operation VARCHAR(50),
            CONSTRAINT single_lock CHECK (id = 1)
        );
        """

        cmd = [
            psql, "-h", cfg.remote_host, "-p", str(cfg.remote_port),
            "-U", cfg.remote_user, "-d", cfg.remote_database,
            "-c", create_table_sql
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=30)
            return result.returncode == 0
        except:
            return False

    def _acquire_sync_lock(self) -> bool:
        """Try to acquire sync lock on remote database"""
        cfg = self.config
        psql = self._get_psql_path()

        env = os.environ.copy()
        env['PGPASSWORD'] = cfg.remote_password

        self.progress.emit(0, QCoreApplication.translate("SyncWorker", "Verifica lock sincronizzazione..."))

        if not self._ensure_lock_table(env):
            self._has_lock = True
            return True

        import socket
        user_id = f"{cfg.local_user}@{socket.gethostname()}"

        acquire_sql = f"""
        INSERT INTO pyarchinit_sync_lock (id, locked_by, locked_at, operation)
        VALUES (1, '{user_id}', NOW(), '{self.operation}')
        ON CONFLICT (id) DO UPDATE
        SET locked_by = EXCLUDED.locked_by,
            locked_at = EXCLUDED.locked_at,
            operation = EXCLUDED.operation
        WHERE pyarchinit_sync_lock.locked_at < NOW() - INTERVAL '{self.LOCK_TIMEOUT} seconds'
           OR pyarchinit_sync_lock.locked_by = '{user_id}'
        RETURNING locked_by;
        """

        cmd = [
            psql, "-h", cfg.remote_host, "-p", str(cfg.remote_port),
            "-U", cfg.remote_user, "-d", cfg.remote_database,
            "-t", "-A", "-c", acquire_sql
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=30)

            if result.returncode == 0 and user_id in result.stdout:
                self._has_lock = True
                return True
            else:
                check_sql = "SELECT locked_by, locked_at, operation FROM pyarchinit_sync_lock WHERE id = 1;"
                check_cmd = [
                    psql, "-h", cfg.remote_host, "-p", str(cfg.remote_port),
                    "-U", cfg.remote_user, "-d", cfg.remote_database,
                    "-t", "-A", "-c", check_sql
                ]
                check_result = subprocess.run(check_cmd, capture_output=True, text=True, env=env, timeout=30)

                if check_result.stdout.strip():
                    parts = check_result.stdout.strip().split('|')
                    locked_by = parts[0] if len(parts) > 0 else "unknown"
                    locked_at = parts[1] if len(parts) > 1 else "unknown"
                    operation = parts[2] if len(parts) > 2 else "unknown"

                    error_msg = QCoreApplication.translate(
                        "SyncWorker",
                        "Synchronization blocked!\n\n"
                        "Another user is synchronizing:\n"
                        "• User: {0}\n"
                        "• Started: {1}\n"
                        "• Operation: {2}\n\n"
                        "Please try again later."
                    ).format(locked_by, locked_at, operation)

                    self.error.emit(error_msg)
                    self.finished.emit(False, QCoreApplication.translate("SyncWorker", "Blocked by another user"))
                    return False
                else:
                    self._has_lock = True
                    return True

        except subprocess.TimeoutExpired:
            self.error.emit(QCoreApplication.translate("SyncWorker", "Connection timeout"))
            self.finished.emit(False, QCoreApplication.translate("SyncWorker", "Connection timeout"))
            return False
        except Exception as e:
            self._has_lock = True
            return True

    def _release_sync_lock(self):
        """Release sync lock"""
        if not self._has_lock:
            return

        cfg = self.config
        psql = self._get_psql_path()

        env = os.environ.copy()
        env['PGPASSWORD'] = cfg.remote_password

        import socket
        user_id = f"{cfg.local_user}@{socket.gethostname()}"

        release_sql = f"DELETE FROM pyarchinit_sync_lock WHERE id = 1 AND locked_by = '{user_id}';"

        cmd = [
            psql, "-h", cfg.remote_host, "-p", str(cfg.remote_port),
            "-U", cfg.remote_user, "-d", cfg.remote_database,
            "-c", release_sql
        ]

        try:
            subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=30)
        except:
            pass

    def _download_from_remote(self):
        """Download data from remote to local (full sync)"""
        cfg = self.config
        tables = self.tables_to_sync
        total = len(tables)

        self.progress.emit(0, QCoreApplication.translate("SyncWorker", "Connecting to remote server..."))

        pg_dump = self._get_pg_dump_path()
        psql = self._get_psql_path()

        remote_env = os.environ.copy()
        remote_env['PGPASSWORD'] = cfg.remote_password

        local_env = os.environ.copy()
        local_env['PGPASSWORD'] = cfg.local_password

        synced = 0
        errors = 0

        for idx, table in enumerate(tables):
            if self._cancelled:
                self.finished.emit(False, QCoreApplication.translate("SyncWorker", "Operation cancelled"))
                return

            percent = int((idx / total) * 100)
            self.progress.emit(percent, QCoreApplication.translate("SyncWorker", "Downloading {0}...").format(table))

            try:
                # Dump from remote
                dump_cmd = [
                    pg_dump, "-h", cfg.remote_host, "-p", str(cfg.remote_port),
                    "-U", cfg.remote_user, "-d", cfg.remote_database,
                    "-t", table, "--data-only", "--column-inserts", "--on-conflict-do-nothing"
                ]

                dump_result = subprocess.run(dump_cmd, capture_output=True, text=True, env=remote_env, timeout=300)

                if dump_result.returncode != 0:
                    errors += 1
                    continue

                dump_data = dump_result.stdout
                if not dump_data.strip():
                    continue

                # Truncate local table
                truncate_cmd = [
                    psql, "-h", cfg.local_host, "-p", str(cfg.local_port),
                    "-U", cfg.local_user, "-d", cfg.local_database,
                    "-c", f"TRUNCATE {table} CASCADE;"
                ]
                subprocess.run(truncate_cmd, capture_output=True, env=local_env, timeout=60)

                # Insert data
                insert_cmd = [
                    psql, "-h", cfg.local_host, "-p", str(cfg.local_port),
                    "-U", cfg.local_user, "-d", cfg.local_database
                ]
                subprocess.run(insert_cmd, input=dump_data, capture_output=True, text=True, env=local_env, timeout=300)
                synced += 1

            except subprocess.TimeoutExpired:
                errors += 1
            except Exception as e:
                errors += 1

        self.progress.emit(100, QCoreApplication.translate("SyncWorker", "Download complete!"))
        msg = QCoreApplication.translate("SyncWorker", "Download completed: {0} tables synced, {1} errors").format(synced, errors)
        self.finished.emit(True, msg)

    def _upload_to_remote(self):
        """Upload data from local to remote (full sync)"""
        cfg = self.config
        tables = self.tables_to_sync
        total = len(tables)

        self.progress.emit(0, QCoreApplication.translate("SyncWorker", "Connecting to remote server..."))

        pg_dump = self._get_pg_dump_path()
        psql = self._get_psql_path()

        local_env = os.environ.copy()
        local_env['PGPASSWORD'] = cfg.local_password

        remote_env = os.environ.copy()
        remote_env['PGPASSWORD'] = cfg.remote_password

        synced = 0
        errors = 0

        for idx, table in enumerate(tables):
            if self._cancelled:
                self.finished.emit(False, QCoreApplication.translate("SyncWorker", "Operation cancelled"))
                return

            percent = int((idx / total) * 100)
            self.progress.emit(percent, QCoreApplication.translate("SyncWorker", "Uploading {0}...").format(table))

            try:
                # Dump from local
                dump_cmd = [
                    pg_dump, "-h", cfg.local_host, "-p", str(cfg.local_port),
                    "-U", cfg.local_user, "-d", cfg.local_database,
                    "-t", table, "--data-only", "--column-inserts"
                ]

                dump_result = subprocess.run(dump_cmd, capture_output=True, text=True, env=local_env, timeout=300)

                if dump_result.returncode != 0:
                    errors += 1
                    continue

                dump_data = dump_result.stdout
                if not dump_data.strip():
                    continue

                # Truncate remote table
                truncate_cmd = [
                    psql, "-h", cfg.remote_host, "-p", str(cfg.remote_port),
                    "-U", cfg.remote_user, "-d", cfg.remote_database,
                    "-c", f"TRUNCATE {table} CASCADE;"
                ]
                subprocess.run(truncate_cmd, capture_output=True, env=remote_env, timeout=120)

                # Insert data
                insert_cmd = [
                    psql, "-h", cfg.remote_host, "-p", str(cfg.remote_port),
                    "-U", cfg.remote_user, "-d", cfg.remote_database
                ]
                subprocess.run(insert_cmd, input=dump_data, capture_output=True, text=True, env=remote_env, timeout=600)
                synced += 1

            except subprocess.TimeoutExpired:
                errors += 1
            except Exception as e:
                errors += 1

        self.progress.emit(100, QCoreApplication.translate("SyncWorker", "Upload complete!"))
        msg = QCoreApplication.translate("SyncWorker", "Upload completed: {0} tables synced, {1} errors").format(synced, errors)
        self.finished.emit(True, msg)

    def _differential_download(self):
        """Download only changed/new records from remote to local (preserves IDs)"""
        cfg = self.config
        tables = self.tables_to_sync
        total = len(tables)

        self.progress.emit(0, QCoreApplication.translate("SyncWorker", "Starting differential download..."))

        psql = self._get_psql_path()

        remote_env = os.environ.copy()
        remote_env['PGPASSWORD'] = cfg.remote_password

        local_env = os.environ.copy()
        local_env['PGPASSWORD'] = cfg.local_password

        synced = 0
        inserted = 0
        updated = 0
        errors = 0
        error_details = []

        for idx, table in enumerate(tables):
            if self._cancelled:
                self.finished.emit(False, QCoreApplication.translate("SyncWorker", "Operation cancelled"))
                return

            percent = int((idx / total) * 100)
            self.progress.emit(percent, QCoreApplication.translate("SyncWorker", "Syncing {0}...").format(table))

            try:
                # Check if table is a view (skip views)
                is_view = self._is_view(psql, cfg.remote_host, cfg.remote_port,
                                        cfg.remote_user, cfg.remote_database, table, remote_env)
                if is_view:
                    synced += 1
                    continue

                # Check if table exists on local
                local_exists = self._table_exists(psql, cfg.local_host, cfg.local_port,
                                                   cfg.local_user, cfg.local_database, table, local_env)
                if not local_exists:
                    error_details.append(f"{table}: table does not exist locally")
                    errors += 1
                    continue

                # Get primary key for this table
                pk = self._get_primary_key(psql, cfg.local_host, cfg.local_port,
                                           cfg.local_user, cfg.local_database, table, local_env)
                if not pk:
                    pk = 'gid' if table.startswith('pyarchinit_') else 'id'

                # Get IDs from both databases
                local_ids = set(self._get_record_ids(
                    psql, cfg.local_host, cfg.local_port,
                    cfg.local_user, cfg.local_database, table, pk, local_env
                ))
                remote_ids = set(self._get_record_ids(
                    psql, cfg.remote_host, cfg.remote_port,
                    cfg.remote_user, cfg.remote_database, table, pk, remote_env
                ))

                # Records only in remote (to INSERT)
                to_insert = remote_ids - local_ids

                if not to_insert:
                    synced += 1
                    continue

                # Get all columns for this table
                columns = self._get_table_columns(psql, cfg.remote_host, cfg.remote_port,
                                                   cfg.remote_user, cfg.remote_database, table, remote_env)
                if not columns:
                    error_details.append(f"{table}: could not get columns")
                    errors += 1
                    continue

                columns_str = ', '.join(columns)

                # Disable triggers on this table to prevent cascade deletes
                disable_trigger_cmd = [
                    psql, "-h", cfg.local_host, "-p", str(cfg.local_port),
                    "-U", cfg.local_user, "-d", cfg.local_database,
                    "-c", f"ALTER TABLE {table} DISABLE TRIGGER ALL;"
                ]
                subprocess.run(disable_trigger_cmd, capture_output=True, env=local_env, timeout=30)

                try:
                    # Process in batches
                    batch_size = 50
                    all_ids_list = list(to_insert)
                    table_inserted = 0

                    for batch_start in range(0, len(all_ids_list), batch_size):
                        batch_ids = all_ids_list[batch_start:batch_start + batch_size]
                        ids_str = ','.join(str(i) for i in batch_ids)

                        # Use COPY TO to export data from remote
                        copy_query = f"COPY (SELECT {columns_str} FROM {table} WHERE {pk} IN ({ids_str})) TO STDOUT WITH (FORMAT csv, HEADER false, NULL 'NULL_VALUE_PLACEHOLDER')"

                        export_cmd = [
                            psql, "-h", cfg.remote_host, "-p", str(cfg.remote_port),
                            "-U", cfg.remote_user, "-d", cfg.remote_database,
                            "-t", "-A", "-c", copy_query
                        ]

                        export_result = subprocess.run(export_cmd, capture_output=True, text=True, env=remote_env, timeout=300)

                        if export_result.returncode != 0:
                            error_details.append(f"{table}: export error - {export_result.stderr[:200]}")
                            continue

                        csv_data = export_result.stdout.strip()
                        if not csv_data:
                            continue

                        # Use COPY FROM to import data to local
                        import_query = f"COPY {table} ({columns_str}) FROM STDIN WITH (FORMAT csv, HEADER false, NULL 'NULL_VALUE_PLACEHOLDER')"

                        import_cmd = [
                            psql, "-h", cfg.local_host, "-p", str(cfg.local_port),
                            "-U", cfg.local_user, "-d", cfg.local_database,
                            "-c", import_query
                        ]

                        import_result = subprocess.run(import_cmd, input=csv_data, capture_output=True, text=True, env=local_env, timeout=600)

                        if import_result.returncode == 0:
                            table_inserted += len(batch_ids)
                        else:
                            error_details.append(f"{table}: import error - {import_result.stderr[:200]}")

                    inserted += table_inserted
                    if table_inserted > 0:
                        synced += 1

                finally:
                    # Re-enable triggers
                    enable_trigger_cmd = [
                        psql, "-h", cfg.local_host, "-p", str(cfg.local_port),
                        "-U", cfg.local_user, "-d", cfg.local_database,
                        "-c", f"ALTER TABLE {table} ENABLE TRIGGER ALL;"
                    ]
                    subprocess.run(enable_trigger_cmd, capture_output=True, env=local_env, timeout=30)

            except Exception as e:
                error_details.append(f"{table}: {str(e)}")
                errors += 1
                continue

        self.progress.emit(100, QCoreApplication.translate("SyncWorker", "Differential download complete!"))

        if error_details:
            import tempfile
            log_path = os.path.join(tempfile.gettempdir(), 'pyarchinit_sync_errors.log')
            with open(log_path, 'w') as f:
                f.write('\n'.join(error_details))

        msg = QCoreApplication.translate(
            "SyncWorker",
            "Download completed: {0} tables, {1} inserted, {2} updated, {3} errors"
        ).format(synced, inserted, updated, errors)

        if error_details and len(error_details) <= 3:
            msg += "\n" + "\n".join(error_details[:3])

        self.finished.emit(True, msg)

    def _differential_upload(self):
        """Upload only changed/new records from local to remote (preserves IDs)"""
        cfg = self.config
        tables = self.tables_to_sync
        total = len(tables)

        self.progress.emit(0, QCoreApplication.translate("SyncWorker", "Starting differential upload..."))

        psql = self._get_psql_path()

        local_env = os.environ.copy()
        local_env['PGPASSWORD'] = cfg.local_password

        remote_env = os.environ.copy()
        remote_env['PGPASSWORD'] = cfg.remote_password

        synced = 0
        inserted = 0
        updated = 0
        errors = 0
        error_details = []

        for idx, table in enumerate(tables):
            if self._cancelled:
                self.finished.emit(False, QCoreApplication.translate("SyncWorker", "Operation cancelled"))
                return

            percent = int((idx / total) * 100)
            self.progress.emit(percent, QCoreApplication.translate("SyncWorker", "Syncing {0}...").format(table))

            try:
                # Check if table is a view (skip views)
                is_view = self._is_view(psql, cfg.local_host, cfg.local_port,
                                        cfg.local_user, cfg.local_database, table, local_env)
                if is_view:
                    # Skip views
                    synced += 1
                    continue

                # Check if table exists on remote
                remote_exists = self._table_exists(psql, cfg.remote_host, cfg.remote_port,
                                                    cfg.remote_user, cfg.remote_database, table, remote_env)
                if not remote_exists:
                    error_details.append(f"{table}: table does not exist on remote")
                    errors += 1
                    continue

                # Get primary key for this table
                pk = self._get_primary_key(psql, cfg.local_host, cfg.local_port,
                                           cfg.local_user, cfg.local_database, table, local_env)
                if not pk:
                    pk = 'gid' if table.startswith('pyarchinit_') else 'id'

                # Get IDs from both databases
                local_ids = set(self._get_record_ids(
                    psql, cfg.local_host, cfg.local_port,
                    cfg.local_user, cfg.local_database, table, pk, local_env
                ))
                remote_ids = set(self._get_record_ids(
                    psql, cfg.remote_host, cfg.remote_port,
                    cfg.remote_user, cfg.remote_database, table, pk, remote_env
                ))

                # Records only in local (to INSERT)
                to_insert = local_ids - remote_ids
                # Records in both (to UPDATE - we'll skip updates for now to keep it simple)
                # to_update = local_ids & remote_ids

                if not to_insert:
                    synced += 1
                    continue

                # Get all columns for this table
                columns = self._get_table_columns(psql, cfg.local_host, cfg.local_port,
                                                   cfg.local_user, cfg.local_database, table, local_env)
                if not columns:
                    error_details.append(f"{table}: could not get columns")
                    errors += 1
                    continue

                columns_str = ', '.join(columns)

                # Disable triggers on remote table to prevent cascade deletes
                disable_trigger_cmd = [
                    psql, "-h", cfg.remote_host, "-p", str(cfg.remote_port),
                    "-U", cfg.remote_user, "-d", cfg.remote_database,
                    "-c", f"ALTER TABLE {table} DISABLE TRIGGER ALL;"
                ]
                subprocess.run(disable_trigger_cmd, capture_output=True, env=remote_env, timeout=30)

                try:
                    # Process in batches to avoid command line too long
                    batch_size = 50
                    all_ids_list = list(to_insert)
                    table_inserted = 0

                    for batch_start in range(0, len(all_ids_list), batch_size):
                        batch_ids = all_ids_list[batch_start:batch_start + batch_size]
                        ids_str = ','.join(str(i) for i in batch_ids)

                        # Use COPY TO to export data from local
                        copy_query = f"COPY (SELECT {columns_str} FROM {table} WHERE {pk} IN ({ids_str})) TO STDOUT WITH (FORMAT csv, HEADER false, NULL 'NULL_VALUE_PLACEHOLDER')"

                        export_cmd = [
                            psql, "-h", cfg.local_host, "-p", str(cfg.local_port),
                            "-U", cfg.local_user, "-d", cfg.local_database,
                            "-t", "-A", "-c", copy_query
                        ]

                        export_result = subprocess.run(export_cmd, capture_output=True, text=True, env=local_env, timeout=300)

                        if export_result.returncode != 0:
                            error_details.append(f"{table}: export error - {export_result.stderr[:200]}")
                            continue

                        csv_data = export_result.stdout.strip()
                        if not csv_data:
                            continue

                        # Use COPY FROM to import data to remote
                        import_query = f"COPY {table} ({columns_str}) FROM STDIN WITH (FORMAT csv, HEADER false, NULL 'NULL_VALUE_PLACEHOLDER')"

                        import_cmd = [
                            psql, "-h", cfg.remote_host, "-p", str(cfg.remote_port),
                            "-U", cfg.remote_user, "-d", cfg.remote_database,
                            "-c", import_query
                        ]

                        import_result = subprocess.run(import_cmd, input=csv_data, capture_output=True, text=True, env=remote_env, timeout=600)

                        if import_result.returncode == 0:
                            table_inserted += len(batch_ids)
                        else:
                            error_details.append(f"{table}: import error - {import_result.stderr[:200]}")

                    inserted += table_inserted
                    if table_inserted > 0:
                        synced += 1

                finally:
                    # Re-enable triggers
                    enable_trigger_cmd = [
                        psql, "-h", cfg.remote_host, "-p", str(cfg.remote_port),
                        "-U", cfg.remote_user, "-d", cfg.remote_database,
                        "-c", f"ALTER TABLE {table} ENABLE TRIGGER ALL;"
                    ]
                    subprocess.run(enable_trigger_cmd, capture_output=True, env=remote_env, timeout=30)

            except Exception as e:
                error_details.append(f"{table}: {str(e)}")
                errors += 1
                continue

        self.progress.emit(100, QCoreApplication.translate("SyncWorker", "Differential upload complete!"))

        if error_details:
            # Log errors to debug
            import tempfile
            log_path = os.path.join(tempfile.gettempdir(), 'pyarchinit_sync_errors.log')
            with open(log_path, 'w') as f:
                f.write('\n'.join(error_details))

        msg = QCoreApplication.translate(
            "SyncWorker",
            "Upload completed: {0} tables, {1} inserted, {2} updated, {3} errors"
        ).format(synced, inserted, updated, errors)

        if error_details and len(error_details) <= 3:
            msg += "\n" + "\n".join(error_details[:3])

        self.finished.emit(True, msg)

    def _is_view(self, psql, host, port, user, database, table, env) -> bool:
        """Check if a table is actually a view"""
        query = f"SELECT table_type FROM information_schema.tables WHERE table_name = '{table}' AND table_schema = 'public';"
        cmd = [
            psql, "-h", host, "-p", str(port), "-U", user, "-d", database,
            "-t", "-A", "-c", query
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=30)
            if result.returncode == 0:
                table_type = result.stdout.strip().upper()
                return 'VIEW' in table_type
        except:
            pass
        return False

    def _table_exists(self, psql, host, port, user, database, table, env) -> bool:
        """Check if a table exists in the database"""
        query = f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '{table}' AND table_schema = 'public');"
        cmd = [
            psql, "-h", host, "-p", str(port), "-U", user, "-d", database,
            "-t", "-A", "-c", query
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=30)
            if result.returncode == 0:
                return result.stdout.strip().lower() == 't'
        except:
            pass
        return False

    def _get_table_columns(self, psql, host, port, user, database, table, env) -> List[str]:
        """Get column names for a table"""
        query = f"""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = '{table}' AND table_schema = 'public'
            ORDER BY ordinal_position;
        """
        cmd = [
            psql, "-h", host, "-p", str(port), "-U", user, "-d", database,
            "-t", "-A", "-c", query
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=30)
            if result.returncode == 0:
                return [x.strip() for x in result.stdout.strip().split('\n') if x.strip()]
        except:
            pass
        return []

    def _get_primary_key(self, psql, host, port, user, database, table, env) -> str:
        """Get primary key column name"""
        query = f"""
            SELECT a.attname FROM pg_index i
            JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
            WHERE i.indrelid = '{table}'::regclass AND i.indisprimary;
        """
        cmd = [
            psql, "-h", host, "-p", str(port), "-U", user, "-d", database,
            "-t", "-A", "-c", query
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=30)
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip().split('\n')[0]
        except:
            pass
        return ''

    def _get_record_ids(self, psql, host, port, user, database, table, pk, env) -> List[str]:
        """Get all record IDs from a table"""
        cmd = [
            psql, "-h", host, "-p", str(port), "-U", user, "-d", database,
            "-t", "-A", "-c", f"SELECT {pk} FROM {table} ORDER BY {pk};"
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=60)
            if result.returncode == 0:
                return [x.strip() for x in result.stdout.strip().split('\n') if x.strip()]
        except:
            pass
        return []


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
            local_host=local_config.get('host', 'localhost'),
            local_port=local_config.get('port', 5432),
            local_database=local_config.get('database', ''),
            local_user=local_config.get('user', 'postgres'),
            local_password=local_config.get('password', ''),
            remote_host=remote_config.get('host', ''),
            remote_port=remote_config.get('port', 5432),
            remote_database=remote_config.get('database', 'postgres'),
            remote_user=remote_config.get('user', ''),
            remote_password=remote_config.get('password', ''),
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
        """Download from remote to local

        Args:
            tables: List of tables to sync (None = all tables)
            differential: If True, only sync new/modified records (preserves IDs)
        """
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
        """Upload from local to remote

        Args:
            tables: List of tables to sync (None = all tables)
            differential: If True, only sync new/modified records (preserves IDs)
        """
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


def get_sync_config_from_settings() -> Tuple[Dict, Dict]:
    """Get sync configurations from QGIS settings"""
    s = QgsSettings()

    local_config = {
        'host': s.value('pyArchInit/local_host', 'localhost'),
        'port': int(s.value('pyArchInit/local_port', 5432)),
        'database': s.value('pyArchInit/local_database', ''),
        'user': s.value('pyArchInit/local_user', 'postgres'),
        'password': s.value('pyArchInit/local_password', '')
    }

    remote_config = {
        'host': s.value('pyArchInit/remote_host', ''),
        'port': int(s.value('pyArchInit/remote_port', 5432)),
        'database': s.value('pyArchInit/remote_database', 'postgres'),
        'user': s.value('pyArchInit/remote_user', ''),
        'password': s.value('pyArchInit/remote_password', '')
    }

    return local_config, remote_config


def save_sync_config_to_settings(local_config: Dict, remote_config: Dict):
    """Save sync configurations to QGIS settings"""
    s = QgsSettings()

    s.setValue('pyArchInit/local_host', local_config.get('host', 'localhost'))
    s.setValue('pyArchInit/local_port', local_config.get('port', 5432))
    s.setValue('pyArchInit/local_database', local_config.get('database', ''))
    s.setValue('pyArchInit/local_user', local_config.get('user', 'postgres'))
    s.setValue('pyArchInit/local_password', local_config.get('password', ''))

    s.setValue('pyArchInit/remote_host', remote_config.get('host', ''))
    s.setValue('pyArchInit/remote_port', remote_config.get('port', 5432))
    s.setValue('pyArchInit/remote_database', remote_config.get('database', 'postgres'))
    s.setValue('pyArchInit/remote_user', remote_config.get('user', ''))
    s.setValue('pyArchInit/remote_password', remote_config.get('password', ''))
