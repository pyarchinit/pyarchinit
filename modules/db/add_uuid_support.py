#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Add entity_uuid support to PyArchInit tables for StratiGraph integration.

Adds a persistent UUID v4 column (entity_uuid) to all main data tables.
Existing records receive a generated UUID. New records get UUIDs
assigned at creation time.

Usage:
    python add_uuid_support.py

Or call programmatically:
    from modules.db.add_uuid_support import UUIDSupport
    uuid_support = UUIDSupport()
    uuid_support.update_all_tables()
"""

import sys
import os
import uuid

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError

try:
    from qgis.core import QgsMessageLog, Qgis
    def _uuid_log(msg, level=Qgis.MessageLevel.Info):
        QgsMessageLog.logMessage(f"[UUID] {msg}", 'PyArchInit', level)
except ImportError:
    def _uuid_log(msg, level=None):
        print(f"[UUID] {msg}")

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(parent_dir)

from modules.db.pyarchinit_conn_strings import Connection


# Tables that need entity_uuid column
TABLES_TO_UPDATE = [
    'site_table',
    'us_table',
    'inventario_materiali_table',
    'tomba_table',
    'periodizzazione_table',
    'struttura_table',
    'campioni_table',
    'individui_table',
    'pottery_table',
    'media_table',
    'media_thumb_table',
    'media_to_entity_table',
    'fauna_table',
    'ut_table',
    'tma_materiali_archeologici',
    'tma_materiali_ripetibili',
    'archeozoology_table',
    'documentazione_table',
    'inventario_lapidei_table',
]


class UUIDSupport:
    """Add entity_uuid support to database tables."""

    def __init__(self, engine=None):
        if engine is not None:
            self.engine = engine
            self.inspector = inspect(self.engine)
            self.is_postgres = 'postgresql' in str(self.engine.url)
        else:
            self.conn = Connection()
            self.engine = create_engine(self.conn.conn_str(), echo=False)
            self.inspector = inspect(self.engine)
            self.is_postgres = 'postgres' in self.conn.conn_str().lower()

    def get_tables_to_update(self):
        """Get list of existing tables that need UUID support."""
        existing = []
        for table_name in TABLES_TO_UPDATE:
            if self.inspector.has_table(table_name):
                existing.append(table_name)
        return existing

    def add_uuid_column(self, table_name):
        """Add entity_uuid column to a table if not already present."""
        try:
            columns = [col['name'] for col in self.inspector.get_columns(table_name)]

            if 'entity_uuid' in columns:
                return True

            with self.engine.begin() as conn:
                if self.is_postgres:
                    conn.execute(text(
                        f"ALTER TABLE {table_name} "
                        f"ADD COLUMN IF NOT EXISTS entity_uuid TEXT"
                    ))
                else:
                    conn.execute(text(
                        f"ALTER TABLE {table_name} "
                        f"ADD COLUMN entity_uuid TEXT"
                    ))

        except SQLAlchemyError as e:
            _uuid_log(f"  {table_name}: ERROR adding column - {e}")
            return False

        return True

    def populate_existing_uuids(self, table_name):
        """Generate UUIDs for existing records that don't have one."""
        try:
            with self.engine.begin() as conn:
                # Count records without UUID
                result = conn.execute(text(
                    f"SELECT COUNT(*) FROM {table_name} "
                    f"WHERE entity_uuid IS NULL OR entity_uuid = ''"
                ))
                count = result.scalar()

                if count == 0:
                    return True

                # Get primary key column name
                pk_cols = self.inspector.get_pk_constraint(table_name)
                has_pk = pk_cols and pk_cols.get('constrained_columns')

                if has_pk:
                    pk_col = pk_cols['constrained_columns'][0]
                    # Fetch IDs of records without UUID
                    result = conn.execute(text(
                        f"SELECT {pk_col} FROM {table_name} "
                        f"WHERE entity_uuid IS NULL OR entity_uuid = ''"
                    ))
                    rows = result.fetchall()

                    # Update each record with a new UUID
                    for row in rows:
                        new_uuid = str(uuid.uuid4())
                        conn.execute(text(
                            f"UPDATE {table_name} "
                            f"SET entity_uuid = :uuid "
                            f"WHERE {pk_col} = :pk_id"
                        ), {"uuid": new_uuid, "pk_id": row[0]})
                elif self.is_postgres:
                    # No PK — use ctid for PostgreSQL
                    result = conn.execute(text(
                        f"SELECT ctid FROM {table_name} "
                        f"WHERE entity_uuid IS NULL OR entity_uuid = ''"
                    ))
                    rows = result.fetchall()
                    for row in rows:
                        new_uuid = str(uuid.uuid4())
                        conn.execute(text(
                            f"UPDATE {table_name} "
                            f"SET entity_uuid = :uuid "
                            f"WHERE ctid = :rid"
                        ), {"uuid": new_uuid, "rid": row[0]})
                else:
                    # No PK — SQLite: use rowid
                    result = conn.execute(text(
                        f"SELECT rowid FROM {table_name} "
                        f"WHERE entity_uuid IS NULL OR entity_uuid = ''"
                    ))
                    rows = result.fetchall()
                    for row in rows:
                        new_uuid = str(uuid.uuid4())
                        conn.execute(text(
                            f"UPDATE {table_name} "
                            f"SET entity_uuid = :uuid "
                            f"WHERE rowid = :rid"
                        ), {"uuid": new_uuid, "rid": row[0]})

        except SQLAlchemyError as e:
            _uuid_log(f"  {table_name}: ERROR populating UUIDs - {e}")
            return False

        return True

    def update_all_tables(self):
        """Add entity_uuid column and populate UUIDs for all tables."""
        tables = self.get_tables_to_update()
        success_count = 0
        total = len(tables)

        for table in tables:
            ok = self.add_uuid_column(table)
            if ok:
                ok = self.populate_existing_uuids(table)
            if ok:
                success_count += 1

        if success_count < total:
            _uuid_log(f"UUID check: {success_count}/{total} tables OK (some failed)")
        return success_count == total


def main():
    """Main function to add UUID support."""
    print("Adding entity_uuid support to PyArchInit database...")
    print("(StratiGraph integration - persistent identifiers)")

    support = UUIDSupport()
    if support.update_all_tables():
        print("\nUUID support added successfully!")
    else:
        print("\nSome tables could not be updated. Check errors above.")


if __name__ == "__main__":
    main()
