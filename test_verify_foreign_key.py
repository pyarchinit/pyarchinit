#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify foreign key issue in TMA tables
"""

import sqlite3
import sys
import os

# Database path
db_path = "/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite"

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== Verifying TMA Foreign Key Issue ===")

# Enable foreign key support
cursor.execute("PRAGMA foreign_keys = ON")

# Check if foreign keys are enabled
cursor.execute("PRAGMA foreign_keys")
fk_enabled = cursor.fetchone()[0]
print(f"\nForeign keys enabled: {bool(fk_enabled)}")

# Check table existence
print("\n=== Checking Tables ===")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('tma_materiali_archeologici', 'tma_materiali_ripetibili')")
tables = cursor.fetchall()
for table in tables:
    print(f"Table found: {table[0]}")

# Check foreign key constraints
print("\n=== Foreign Key Constraints ===")
cursor.execute("PRAGMA foreign_key_list(tma_materiali_ripetibili)")
fk_list = cursor.fetchall()
if fk_list:
    for fk in fk_list:
        print(f"Foreign key: {fk}")
else:
    print("No foreign key constraints found")

# Check TMA records
print("\n=== TMA Records ===")
cursor.execute("SELECT id, ldcn, sito FROM tma_materiali_archeologici ORDER BY id DESC LIMIT 5")
records = cursor.fetchall()
if records:
    for rec in records:
        print(f"ID: {rec[0]}, LDCN: {rec[1]}, Sito: {rec[2]}")
else:
    print("No TMA records found")

# Check if we can insert a material with existing TMA ID
if records:
    tma_id = records[0][0]
    print(f"\n=== Testing Material Insert with TMA ID {tma_id} ===")
    try:
        cursor.execute("""
            INSERT INTO tma_materiali_ripetibili 
            (id_tma, madi, macc, macl, macp, macd, macq, peso)
            VALUES (?, 'TEST', 'C', 'CC', 'Test', 'Test material', '1', 10.0)
        """, (tma_id,))
        print("Material insert successful")
        # Delete the test record
        cursor.execute("DELETE FROM tma_materiali_ripetibili WHERE madi = 'TEST'")
        conn.commit()
    except Exception as e:
        print(f"Material insert failed: {e}")
        conn.rollback()

# Check SQLAlchemy metadata issue
print("\n=== SQLAlchemy Metadata Check ===")
try:
    # Import PyArchInit modules
    sys.path.insert(0, '/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit')
    from modules.db.structures.TMA_table import Tma_table
    from modules.db.structures.TMA_materiali_table import Tma_materiali_table
    
    print(f"TMA table metadata: {id(Tma_table.metadata)}")
    print(f"TMA materials table metadata: {id(Tma_materiali_table.metadata)}")
    
    if Tma_table.metadata is not Tma_materiali_table.metadata:
        print("WARNING: Tables use different metadata objects!")
        print("This can cause foreign key issues in SQLAlchemy")
    else:
        print("Tables share the same metadata")
        
except Exception as e:
    print(f"Could not import modules: {e}")

conn.close()

print("\n=== Verification Complete ===")