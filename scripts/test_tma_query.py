#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script to debug TMA query issue
"""

import sqlite3
import os

def test_direct_sql():
    # Database path
    db_path = os.path.expanduser("~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/pyarchinit_db.sqlite")
    
    if not os.path.exists(db_path):
        print(f"Database not found at: {db_path}")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # First check if there are any TMA records
    cursor.execute("SELECT COUNT(*) FROM tma_materiali_archeologici")
    count = cursor.fetchone()[0]
    print(f"Total TMA records in database: {count}")
    
    if count > 0:
        # Get the first TMA record
        cursor.execute("SELECT id FROM tma_materiali_archeologici ORDER BY id LIMIT 1")
        first_id = cursor.fetchone()[0]
        print(f"\nTesting with first TMA ID: {first_id}")
        
        # Check TMA record
        cursor.execute("SELECT * FROM tma_materiali_archeologici WHERE id = ?", (first_id,))
        tma_record = cursor.fetchone()
        if tma_record:
            print(f"Found TMA record: {tma_record[0:5]}...")  # Show first 5 fields
        
        # Check materials
        cursor.execute("SELECT * FROM tma_materiali_ripetibili WHERE id_tma = ?", (first_id,))
        materials = cursor.fetchall()
        print(f"Found {len(materials)} materials for TMA ID {first_id}")
    else:
        print("No TMA records in database")
    
    # Check data types
    cursor.execute("PRAGMA table_info(tma_materiali_ripetibili)")
    columns = cursor.fetchall()
    print("\nColumn types in tma_materiali_ripetibili:")
    for col in columns:
        print(f"  {col[1]}: {col[2]}")
    
    conn.close()

if __name__ == "__main__":
    test_direct_sql()