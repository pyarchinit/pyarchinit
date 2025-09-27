#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Add versioning support to PyArchInit tables for handling concurrent modifications

Created by: Assistant
Date: 2024
Purpose: Add timestamp columns to all tables for optimistic locking
"""

import sys
import os
from datetime import datetime
from sqlalchemy import create_engine, MetaData, Table, Column, DateTime, Integer, text, inspect
from sqlalchemy.exc import SQLAlchemyError

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(parent_dir)

from modules.db.pyarchinit_conn_strings import Connection

class VersioningSupport:
    """Add versioning support to database tables"""

    def __init__(self):
        self.conn = Connection()
        self.engine = create_engine(self.conn.conn_str(), echo=True)
        self.metadata = MetaData()
        self.inspector = inspect(self.engine)

    def get_all_tables(self):
        """Get all tables that need versioning support"""
        tables_to_update = [
            'us_table',
            'us_table_usm',
            'site_table',
            'periodizzazione_table',
            'inventario_materiali_table',
            'struttura_table',
            'tomba_table',
            'individui_table',
            'campioni_table',
            'documentazione_table',
            'linearizzo_table',
            'ripartizioni_temporali_table',
            'unita_tipo_table',
            'inventario_lapidei_table',
            'tafonomia_table',
            'archeozoology_table',
            'tecnica_muraria_usm_table',
            'tma_table',
            'pottery_table'
        ]

        # Filter only existing tables
        existing_tables = []
        for table_name in tables_to_update:
            if self.inspector.has_table(table_name):
                existing_tables.append(table_name)
                print(f"Found table: {table_name}")
            else:
                print(f"Table not found: {table_name}")

        return existing_tables

    def add_versioning_columns(self, table_name):
        """Add versioning columns to a table"""
        try:
            # Check if columns already exist
            columns = [col['name'] for col in self.inspector.get_columns(table_name)]

            with self.engine.begin() as conn:
                # Add last_modified_timestamp column if not exists
                if 'last_modified_timestamp' not in columns:
                    if 'postgres' in self.conn.conn_str().lower():
                        # PostgreSQL
                        conn.execute(text(f"""
                            ALTER TABLE {table_name}
                            ADD COLUMN IF NOT EXISTS last_modified_timestamp TIMESTAMP
                            DEFAULT CURRENT_TIMESTAMP
                        """))
                        print(f"Added last_modified_timestamp to {table_name}")

                        # Create trigger to auto-update timestamp on modification
                        conn.execute(text(f"""
                            CREATE OR REPLACE FUNCTION update_{table_name}_timestamp()
                            RETURNS TRIGGER AS $$
                            BEGIN
                                NEW.last_modified_timestamp = CURRENT_TIMESTAMP;
                                RETURN NEW;
                            END;
                            $$ LANGUAGE plpgsql;
                        """))

                        conn.execute(text(f"""
                            DROP TRIGGER IF EXISTS update_{table_name}_timestamp_trigger ON {table_name};
                        """))

                        conn.execute(text(f"""
                            CREATE TRIGGER update_{table_name}_timestamp_trigger
                            BEFORE UPDATE ON {table_name}
                            FOR EACH ROW
                            EXECUTE FUNCTION update_{table_name}_timestamp();
                        """))
                        print(f"Created timestamp trigger for {table_name}")
                    else:
                        # SQLite
                        conn.execute(text(f"""
                            ALTER TABLE {table_name}
                            ADD COLUMN last_modified_timestamp DATETIME
                            DEFAULT CURRENT_TIMESTAMP
                        """))
                        print(f"Added last_modified_timestamp to {table_name}")

                        # SQLite doesn't support triggers for updating timestamps easily,
                        # so we'll handle this in the application layer

                # Add modified_by column to track who made changes
                if 'last_modified_by' not in columns:
                    conn.execute(text(f"""
                        ALTER TABLE {table_name}
                        ADD COLUMN last_modified_by VARCHAR(100)
                        DEFAULT 'system'
                    """))
                    print(f"Added last_modified_by to {table_name}")

                # Add version number for optimistic locking
                if 'version_number' not in columns:
                    conn.execute(text(f"""
                        ALTER TABLE {table_name}
                        ADD COLUMN version_number INTEGER
                        DEFAULT 1
                    """))
                    print(f"Added version_number to {table_name}")

        except SQLAlchemyError as e:
            print(f"Error updating table {table_name}: {str(e)}")
            return False

        return True

    def update_all_tables(self):
        """Update all tables with versioning support"""
        tables = self.get_all_tables()
        success_count = 0

        for table in tables:
            if self.add_versioning_columns(table):
                success_count += 1

        print(f"\nSuccessfully updated {success_count} out of {len(tables)} tables")
        return success_count == len(tables)

def main():
    """Main function to add versioning support"""
    print("Adding versioning support to PyArchInit database...")
    print("-" * 50)

    versioning = VersioningSupport()
    if versioning.update_all_tables():
        print("\nVersioning support added successfully!")
        print("\nNext steps:")
        print("1. Update the entity classes to include the new fields")
        print("2. Update the forms to handle version conflicts")
        print("3. Test with multiple users")
    else:
        print("\nSome tables could not be updated. Please check the errors above.")

if __name__ == "__main__":
    main()