#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to add localita and settore columns to existing TMA table
"""

import sqlite3
import os
import sys
from datetime import datetime

def check_column_exists(cursor, table_name, column_name):
    """Check if a column exists in a table."""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    return any(col[1] == column_name for col in columns)

def main():
    # Database path
    db_path = os.path.expanduser("~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/pyarchinit_db.sqlite")
    
    # Alternative path if running from plugin directory
    if not os.path.exists(db_path):
        plugin_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(plugin_dir, "pyarchinit_db.sqlite")
    
    if not os.path.exists(db_path):
        print(f"Database not found at: {db_path}")
        return 1
        
    print(f"Using database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")
        
        print("\nChecking TMA table structure...")
        
        # Check if table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='tma_materiali_archeologici'
        """)
        if not cursor.fetchone():
            print("❌ Table 'tma_materiali_archeologici' does not exist!")
            print("Please run the initial migration script first.")
            return 1
        
        # Check if columns already exist
        localita_exists = check_column_exists(cursor, 'tma_materiali_archeologici', 'localita')
        settore_exists = check_column_exists(cursor, 'tma_materiali_archeologici', 'settore')
        
        if localita_exists and settore_exists:
            print("✓ Columns 'localita' and 'settore' already exist. No migration needed.")
            return 0
        
        # Add localita column if it doesn't exist
        if not localita_exists:
            print("Adding 'localita' column...")
            cursor.execute("""
                ALTER TABLE tma_materiali_archeologici 
                ADD COLUMN localita TEXT
            """)
            print("✓ Added 'localita' column")
        
        # Add settore column if it doesn't exist
        if not settore_exists:
            print("Adding 'settore' column...")
            cursor.execute("""
                ALTER TABLE tma_materiali_archeologici 
                ADD COLUMN settore TEXT
            """)
            print("✓ Added 'settore' column")
        
        # Commit changes
        conn.commit()
        
        # Verify the changes
        print("\nVerifying table structure...")
        cursor.execute("PRAGMA table_info(tma_materiali_archeologici)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'localita' in column_names and 'settore' in column_names:
            print("✅ Migration completed successfully!")
            print("\nCurrent table structure:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
        else:
            print("❌ Migration may have failed. Please check the table structure.")
            return 1
        
    except sqlite3.Error as e:
        print(f"\n❌ Error during migration: {e}")
        conn.rollback()
        return 1
        
    finally:
        conn.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())