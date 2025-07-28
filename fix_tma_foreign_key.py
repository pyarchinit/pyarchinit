#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to fix TMA foreign key issue
"""

import sqlite3
import os

# Default SQLite database path
db_path = "/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinit_db.sqlite"

def fix_foreign_key():
    if not os.path.exists(db_path):
        print(f"Database not found at: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("=== Fixing TMA Foreign Key Issue ===")
        
        # Check current foreign keys
        cursor.execute("PRAGMA foreign_key_list(tma_materiali_ripetibili)")
        fks = cursor.fetchall()
        print(f"Current foreign keys: {fks}")
        
        # Check if both tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('tma_materiali_archeologici', 'tma_materiali_ripetibili')")
        tables = cursor.fetchall()
        print(f"Tables found: {tables}")
        
        if len(tables) != 2:
            print("Error: Required tables not found!")
            return
        
        # Backup existing data
        print("\n--- Backing up existing data ---")
        cursor.execute("SELECT * FROM tma_materiali_ripetibili")
        materials_data = cursor.fetchall()
        print(f"Found {len(materials_data)} records to backup")
        
        # Get table structure
        cursor.execute("PRAGMA table_info(tma_materiali_ripetibili)")
        columns_info = cursor.fetchall()
        columns = [col[1] for col in columns_info]
        
        # Create temporary table with correct structure
        print("\n--- Creating temporary table ---")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tma_materiali_ripetibili_temp (
                id INTEGER PRIMARY KEY,
                id_tma INTEGER NOT NULL,
                madi TEXT,
                macc TEXT NOT NULL,
                macl TEXT,
                macp TEXT,
                macd TEXT,
                cronologia_mac TEXT,
                macq TEXT,
                peso FLOAT,
                created_at TEXT,
                updated_at TEXT,
                created_by TEXT,
                updated_by TEXT,
                FOREIGN KEY (id_tma) REFERENCES tma_materiali_archeologici(id) ON DELETE CASCADE
            )
        """)
        
        # Copy data to temporary table
        if materials_data:
            placeholders = ','.join(['?' for _ in columns])
            cursor.executemany(f"INSERT INTO tma_materiali_ripetibili_temp VALUES ({placeholders})", materials_data)
            print(f"Copied {len(materials_data)} records to temporary table")
        
        # Get list of triggers on the table
        cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='trigger' AND tbl_name='tma_materiali_ripetibili'")
        triggers = cursor.fetchall()
        print(f"\n--- Found {len(triggers)} triggers ---")
        
        # Drop triggers first
        for trigger_name, trigger_sql in triggers:
            print(f"Dropping trigger: {trigger_name}")
            cursor.execute(f"DROP TRIGGER IF EXISTS {trigger_name}")
        
        # Drop old table
        print("\n--- Dropping old table ---")
        cursor.execute("DROP TABLE tma_materiali_ripetibili")
        
        # Rename temporary table
        print("--- Renaming temporary table ---")
        cursor.execute("ALTER TABLE tma_materiali_ripetibili_temp RENAME TO tma_materiali_ripetibili")
        
        # Recreate triggers if needed
        for trigger_name, trigger_sql in triggers:
            print(f"Recreating trigger: {trigger_name}")
            try:
                cursor.execute(trigger_sql)
            except Exception as e:
                print(f"Warning: Could not recreate trigger {trigger_name}: {e}")
        
        # Verify new structure
        cursor.execute("PRAGMA foreign_key_list(tma_materiali_ripetibili)")
        new_fks = cursor.fetchall()
        print(f"\nNew foreign keys: {new_fks}")
        
        # Commit changes
        conn.commit()
        print("\n✓ Foreign key fixed successfully!")
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_foreign_key()