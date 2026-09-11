"""Self-healing of SpatiaLite spatial indexes in pyArchInit SQLite DBs.

A geometry column registered with ``spatial_index_enabled = 1`` whose R*Tree
maintenance triggers (``gii_/giu_/gid_<table>_<column>``) are missing, or
whose R*Tree is out of sync with the table, is INVISIBLE in QGIS: the
SpatiaLite provider selects the features to draw through the R*Tree.
Scripts and updaters that recreate tables (a plain DROP TABLE + CREATE
TABLE keeps the geometry_columns row but loses the triggers) left many
databases in that state, including — from 2025-10-12 — the template used
for new SQLite databases. Geometry columns registered with no index at all
(``spatial_index_enabled = 0``) get one too: without it OGR filters with
SpatiaLite SQL functions that some GDAL builds lack (QGIS 3.x on macOS) and
draws nothing.

``ensure_spatial_indexes`` runs once per session when a SQLite DB is
connected. The audit uses plain sqlite3 (no SpatiaLite, negligible cost on
a healthy DB); only when something is broken it loads SpatiaLite, backs the
file up and rebuilds each broken index with DisableSpatialIndex +
CreateSpatialIndex (which also restores the ggi_/ggu_ type/SRID guards).
It never raises: a failed repair must not prevent the connection.
"""
from __future__ import annotations

import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone

#: SpatiaLite's own ISO-metadata table: never drawn by pyArchInit, and
#: CreateSpatialIndex does not attach triggers to it.
IGNORED_TABLES = frozenset({'iso_metadata'})

_checked = set()


@dataclass(frozen=True)
class IndexStatus:
    table: str
    column: str
    geometries: int
    indexed: int | None
    triggers: int

    @property
    def ok(self) -> bool:
        return self.triggers == 3 and self.indexed == self.geometries


def reset_session_cache() -> None:
    _checked.clear()


def audit_spatial_indexes(con) -> list:
    """Status of every geometry column with an R*Tree index or with none
    (MbrCache columns, spatial_index_enabled = 2, are left alone). Plain
    sqlite3 is enough: the triggers live in sqlite_master and the R*Tree is
    a built-in module."""
    try:
        columns = con.execute(
            "SELECT f_table_name, f_geometry_column FROM geometry_columns "
            "WHERE spatial_index_enabled IN (0, 1) "
            "ORDER BY f_table_name, f_geometry_column").fetchall()
    except sqlite3.Error:
        return []  # not a SpatiaLite database
    statuses = []
    for table, column in columns:
        if table.lower() in IGNORED_TABLES:
            continue
        try:
            geometries = con.execute(
                f'SELECT count(*) FROM "{table}" WHERE "{column}" IS NOT NULL').fetchone()[0]
        except sqlite3.Error:
            continue  # registered but the table is gone
        try:
            indexed = con.execute(f'SELECT count(*) FROM "idx_{table}_{column}"').fetchone()[0]
        except sqlite3.Error:
            indexed = None
        names = [f'{p}_{table}_{column}'.lower() for p in ('gii', 'giu', 'gid')]
        triggers = con.execute(
            "SELECT count(*) FROM sqlite_master WHERE type = 'trigger' "
            "AND lower(tbl_name) = lower(?) AND lower(name) IN (?, ?, ?)",
            (table, *names)).fetchone()[0]
        statuses.append(IndexStatus(table, column, geometries, indexed, triggers))
    return statuses


def repair_spatial_indexes(con, statuses=None) -> list:
    """Rebuild every broken index; ``con`` must have SpatiaLite loaded and
    be in autocommit mode (``isolation_level = None``): each column is
    repaired inside its own SAVEPOINT. Returns the repaired "table.column"."""
    if statuses is None:
        statuses = audit_spatial_indexes(con)
    repaired = []
    for status in statuses:
        if status.ok:
            continue
        table, column = status.table, status.column
        con.execute("SAVEPOINT spatial_index_repair")
        try:
            con.execute("SELECT DisableSpatialIndex(?, ?)", (table, column))
            con.execute(f'DROP TABLE IF EXISTS "idx_{table}_{column}"')
            created = con.execute("SELECT CreateSpatialIndex(?, ?)", (table, column)).fetchone()[0]
            if created != 1:
                raise sqlite3.OperationalError(f"CreateSpatialIndex returned {created}")
            indexed = con.execute(f'SELECT count(*) FROM "idx_{table}_{column}"').fetchone()[0]
            if indexed != status.geometries:
                con.execute("SELECT RecoverSpatialIndex(?, ?)", (table, column))
            con.execute("SELECT UpdateLayerStatistics(?, ?)", (table, column))
            con.execute("RELEASE spatial_index_repair")
            repaired.append(f'{table}.{column}')
        except sqlite3.Error:
            con.execute("ROLLBACK TO spatial_index_repair")
            con.execute("RELEASE spatial_index_repair")
    return repaired


def _backup(con, db_path) -> str:
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    backup_path = f"{db_path}.pre_spatial_index_repair_{stamp}"
    dest = sqlite3.connect(backup_path)
    try:
        con.backup(dest)  # consistent copy, WAL content included
    finally:
        dest.close()
    return backup_path


def _default_log(message, warning=False) -> None:
    print(message)
    try:
        from qgis.core import Qgis, QgsMessageLog
        levels = getattr(Qgis, 'MessageLevel', Qgis)
        QgsMessageLog.logMessage(message, 'PyArchInit',
                                 levels.Warning if warning else levels.Info)
    except Exception:
        pass


def ensure_spatial_layers(db_path, load_spatialite, force=False, backup=True, log=None,
                          canonical_views=None) -> list:
    """Check the SQLite DB at ``db_path`` once per session and repair its
    broken spatial indexes and spatial views (spatial_view_repair: view key
    not the ROWID of the geometry table, stale/orphan registrations, missing
    views, base tables without spatial index). ``load_spatialite(con)``
    loads the extension into a sqlite3 connection (the plugin passes its
    own loader). The audit writes nothing; one backup precedes any change.
    Returns what was repaired (empty when nothing had to be done or the
    repair was not possible); never raises."""
    from .spatial_view_repair import audit_spatial_views, has_work, repair_spatial_views

    log = log or _default_log
    key = os.path.abspath(db_path)
    if not force and key in _checked:
        return []
    _checked.add(key)
    try:
        if not os.path.isfile(db_path):
            return []
        con = sqlite3.connect(db_path, timeout=30)
        try:
            broken = [s for s in audit_spatial_indexes(con) if not s.ok]
            views = audit_spatial_views(con, canonical_views)
            view_work = has_work(views)
            if not broken and not view_work:
                return []
            todo = [f'{s.table}.{s.column}' for s in broken] + \
                   [f'{s.view} ({s.state})' for s in views if s.state not in ('ok', 'unsafe')]
            try:
                load_spatialite(con)
            except Exception as e:
                log(f"PyArchInit: layer spaziali da riparare in {db_path} ({', '.join(todo)}) "
                    f"ma SpatiaLite non è caricabile: {e}", warning=True)
                return []
            backup_path = _backup(con, db_path) if backup else None
            con.isolation_level = None
            repaired = repair_spatial_indexes(con, broken)
            if view_work:
                views = audit_spatial_views(con, canonical_views)  # base indexes just rebuilt
                repaired += repair_spatial_views(con, views, canonical_views)
            failed = sorted(set(f'{s.table}.{s.column}' for s in broken) - set(repaired))
            log(f"PyArchInit: layer spaziali riparati in {os.path.basename(db_path)}: "
                f"{'; '.join(repaired) or 'nessuno'}"
                + (f"; indici NON riparati: {', '.join(failed)}" if failed else "")
                + (f" (backup: {backup_path})" if backup_path else ""),
                warning=bool(failed))
            return repaired
        finally:
            con.close()
    except Exception as e:
        log(f"PyArchInit: controllo dei layer spaziali non riuscito su {db_path}: {e}", warning=True)
        return []


#: Former name, kept for callers of the index-only version.
ensure_spatial_indexes = ensure_spatial_layers
