#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Safe SQLite US field migration script with transaction support
This version ensures data integrity by using transactions and validation
"""

import sqlite3
import sys
import os
import shutil
from datetime import datetime
import traceback

def backup_database(db_path):
    """Create a backup of the database"""
    backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(db_path, backup_path)
    print(f"Backup created: {backup_path}")
    return backup_path

def verify_table_exists(conn, table_name):
    """Verify that a table exists and has data"""
    cursor = conn.cursor()
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    if not cursor.fetchone():
        return False, 0
    
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    return True, count

def get_dependent_views(conn):
    """Get all views that might depend on the tables we're migrating"""
    cursor = conn.cursor()
    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='view'")
    views = cursor.fetchall()
    
    view_definitions = {}
    for view_name, view_sql in views:
        view_definitions[view_name] = view_sql
    
    return view_definitions

def drop_all_views(conn):
    """Drop all views to avoid dependency issues"""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='view'")
    views = cursor.fetchall()
    
    # Views to preserve
    preserve_views = ['mediaentity_view']
    
    for view in views:
        view_name = view[0]
        if view_name in preserve_views:
            print(f"  Preserving view: {view_name}")
            continue
        try:
            cursor.execute(f"DROP VIEW IF EXISTS {view_name}")
            print(f"  Dropped view: {view_name}")
        except Exception as e:
            print(f"  Warning: Could not drop view {view_name}: {e}")

def migrate_table_with_validation(conn, table_name, fields_to_migrate):
    """Migrate table with data validation"""
    cursor = conn.cursor()
    
    # Check if table exists
    exists, row_count = verify_table_exists(conn, table_name)
    if not exists:
        print(f"Table {table_name} not found, skipping...")
        return True
    
    print(f"  Table has {row_count} rows")
    
    # Get table structure
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    
    # Check if migration is needed
    needs_migration = False
    for col in columns:
        col_name = col[1]
        col_type = col[2].upper()
        if col_name in fields_to_migrate and ('INTEGER' in col_type or 'BIGINT' in col_type):
            needs_migration = True
            print(f"  Field {col_name} needs migration from {col_type} to TEXT")
    
    if not needs_migration:
        print(f"Table {table_name} already migrated, skipping...")
        return True
    
    # Build new table definition
    new_table_sql = f"CREATE TABLE {table_name}_new ("
    column_defs = []
    
    for col in columns:
        col_id, col_name, col_type, col_notnull, col_default, col_pk = col
        
        # Change field type to TEXT if it's in the migration list
        if col_name in fields_to_migrate:
            col_type = 'TEXT'
        
        col_def = f"{col_name} {col_type}"
        
        if col_pk:
            col_def += " PRIMARY KEY"
            if col_name.startswith('id_'):
                col_def += " AUTOINCREMENT"
        
        if col_notnull and not col_pk:
            col_def += " NOT NULL"
            
        if col_default is not None:
            col_def += f" DEFAULT {col_default}"
            
        column_defs.append(col_def)
    
    new_table_sql += ", ".join(column_defs) + ")"
    
    # Create new table
    print(f"  Creating new table structure...")
    cursor.execute(new_table_sql)
    
    # Copy data
    columns_list = [col[1] for col in columns]
    select_list = []
    for col_name in columns_list:
        if col_name in fields_to_migrate:
            select_list.append(f"CAST({col_name} AS TEXT)")
        else:
            select_list.append(col_name)
    
    columns_str = ", ".join(columns_list)
    select_str = ", ".join(select_list)
    
    print(f"  Copying data to new table...")
    cursor.execute(f"INSERT INTO {table_name}_new ({columns_str}) SELECT {select_str} FROM {table_name}")
    
    # Verify data was copied
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}_new")
    new_count = cursor.fetchone()[0]
    
    if new_count != row_count:
        raise Exception(f"Data validation failed: expected {row_count} rows, got {new_count}")
    
    print(f"  Verified {new_count} rows copied successfully")
    
    # Drop old table and rename new one
    print(f"  Replacing old table with new one...")
    cursor.execute(f"DROP TABLE {table_name}")
    cursor.execute(f"ALTER TABLE {table_name}_new RENAME TO {table_name}")
    
    # Create indexes
    for field in fields_to_migrate:
        try:
            cursor.execute(f"CREATE INDEX idx_{table_name}_{field} ON {table_name}({field})")
        except:
            pass
    
    print(f"✓ Table {table_name} migrated successfully")
    return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python safe_sqlite_migration.py <path_to_sqlite_db>")
        sys.exit(1)
    
    db_path = sys.argv[1]
    
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        sys.exit(1)
    
    print(f"\n=== PyArchInit Safe SQLite Migration Tool ===")
    print(f"Database: {db_path}")
    
    # Create backup
    backup_path = backup_database(db_path)
    
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = OFF")  # Disable foreign key constraints during migration
    
    try:
        # Start transaction
        conn.execute("BEGIN TRANSACTION")
        
        print("\n=== Saving view definitions ===")
        view_definitions = get_dependent_views(conn)
        print(f"Found {len(view_definitions)} views")
        
        print("\n=== Dropping all views ===")
        drop_all_views(conn)
        
        print("\n=== Starting table migrations ===")
        
        # Define migrations
        migrations = [
            ('us_table', ['us', 'area']),
            ('campioni_table', ['us', 'area']),
            ('pottery_table', ['us', 'area']),
            ('inventario_materiali_table', ['us', 'area']),
            ('tomba_table', ['area']),
            ('us_table_toimp', ['us']),
            ('pyarchinit_quote', ['us_q']),
            ('pyarchinit_quote_usm', ['us_q']),
            ('pyunitastratigrafiche', ['us_s']),
            ('pyunitastratigrafiche_usm', ['us_s']),
            ('pyarchinit_us_negative_doc', ['us_n']),
            ('pyuscaratterizzazioni', ['us_c'])
        ]
        
        # Perform migrations
        success_count = 0
        for table_name, fields in migrations:
            print(f"\nMigrating {table_name}...")
            try:
                if migrate_table_with_validation(conn, table_name, fields):
                    success_count += 1
            except Exception as e:
                print(f"✗ Error migrating {table_name}: {e}")
                raise
        
        print("\n=== Recreating views ===")
        for view_name, view_sql in view_definitions.items():
            try:
                print(f"  Recreating view {view_name}...")
                conn.execute(view_sql)
            except Exception as e:
                print(f"  Warning: Could not recreate view {view_name}: {e}")
                # Continue anyway - views can be recreated later
        
        # Commit transaction
        conn.commit()
        print(f"\n=== Migration completed successfully ===")
        print(f"Successfully migrated {success_count} tables")
        print(f"Backup saved at: {backup_path}")
        
    except Exception as e:
        print(f"\n✗ MIGRATION FAILED: {e}")
        print(f"Rolling back all changes...")
        conn.rollback()
        print(f"Database restored to original state")
        print(f"Backup is available at: {backup_path}")
        traceback.print_exc()
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    main()