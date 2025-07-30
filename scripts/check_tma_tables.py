#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to check if TMA tables exist and their structure
"""

import sqlite3
import os

# Path to the database
db_path = "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/pyarchinit_db.sqlite"

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check for TMA tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'tma%' ORDER BY name")
    tables = cursor.fetchall()
    
    print("TMA related tables found:")
    for table in tables:
        print(f"  - {table[0]}")
        
    # Check schema for each table
    for table in tables:
        print(f"\nSchema for {table[0]}:")
        cursor.execute(f"PRAGMA table_info({table[0]})")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[1]} {col[2]} {'NOT NULL' if col[3] else ''} {'PK' if col[5] else ''}")
            
    # Check foreign keys
    for table in tables:
        cursor.execute(f"PRAGMA foreign_key_list({table[0]})")
        fks = cursor.fetchall()
        if fks:
            print(f"\nForeign keys for {table[0]}:")
            for fk in fks:
                print(f"  {fk[3]} -> {fk[2]}.{fk[4]}")
    
    conn.close()
else:
    print(f"Database not found at: {db_path}")