#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Check database structure for TMA tables
"""
import sqlite3
import os

def check_db_structure(db_path):
    """Check the structure of TMA tables in the database."""
    if not os.path.exists(db_path):
        print(f"Database not found: {db_path}")
        return
    
    print(f"Checking database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    print("\nTables in database:")
    for table in sorted(tables):
        print(f"  - {table}")
    
    # Check TMA table structure
    if 'tma_materiali_archeologici' in tables:
        print("\ntma_materiali_archeologici structure:")
        cursor.execute("PRAGMA table_info(tma_materiali_archeologici)")
        for row in cursor.fetchall():
            print(f"  {row[1]} {row[2]} {'NOT NULL' if row[3] else 'NULL'} {'PK' if row[5] else ''}")
    
    # Check TMA_MATERIALI table structure
    if 'tma_materiali_ripetibili' in tables:
        print("\ntma_materiali_ripetibili structure:")
        cursor.execute("PRAGMA table_info(tma_materiali_ripetibili)")
        for row in cursor.fetchall():
            print(f"  {row[1]} {row[2]} {'NOT NULL' if row[3] else 'NULL'} {'PK' if row[5] else ''}")
    
    # Check for any TMA records
    if 'tma_materiali_archeologici' in tables:
        cursor.execute("SELECT COUNT(*) FROM tma_materiali_archeologici")
        count = cursor.fetchone()[0]
        print(f"\nTMA records: {count}")
        
        if count > 0:
            cursor.execute("SELECT id, sito, area, dscu FROM tma_materiali_archeologici LIMIT 5")
            print("\nFirst 5 TMA records:")
            for row in cursor.fetchall():
                print(f"  ID: {row[0]}, Sito: {row[1]}, Area: {row[2]}, US: {row[3]}")
    
    # Check for any materials records
    if 'tma_materiali_ripetibili' in tables:
        cursor.execute("SELECT COUNT(*) FROM tma_materiali_ripetibili")
        count = cursor.fetchone()[0]
        print(f"\nTMA_MATERIALI records: {count}")
        
        if count > 0:
            cursor.execute("SELECT id, id_tma, madi, macc FROM tma_materiali_ripetibili LIMIT 5")
            print("\nFirst 5 TMA_MATERIALI records:")
            for row in cursor.fetchall():
                print(f"  ID: {row[0]}, ID_TMA: {row[1]}, MADI: {row[2]}, MACC: {row[3]}")
    
    conn.close()

if __name__ == "__main__":
    # Check the database the user mentioned
    db_path = "/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite"
    check_db_structure(db_path)