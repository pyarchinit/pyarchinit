#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick check for TMA records in database
"""

import sqlite3

# Database path
db_path = "/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite"

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== TMA Database Check ===\n")

# Check TMA records
cursor.execute("SELECT COUNT(*) FROM tma_materiali_archeologici")
tma_count = cursor.fetchone()[0]
print(f"Total TMA records: {tma_count}")

# Show TMA records
if tma_count > 0:
    cursor.execute("SELECT id, sito, ldcn, area, dscu FROM tma_materiali_archeologici ORDER BY id")
    records = cursor.fetchall()
    print("\nTMA Records:")
    for rec in records:
        print(f"  ID {rec[0]}: Sito='{rec[1]}', LDCN='{rec[2]}', Area='{rec[3]}', US='{rec[4]}'")

# Check materials
cursor.execute("SELECT COUNT(*) FROM tma_materiali_ripetibili")
materials_count = cursor.fetchone()[0]
print(f"\nTotal Materials: {materials_count}")

# Show materials grouped by TMA
if materials_count > 0:
    cursor.execute("""
        SELECT id_tma, COUNT(*) as mat_count 
        FROM tma_materiali_ripetibili 
        GROUP BY id_tma
        ORDER BY id_tma
    """)
    mat_groups = cursor.fetchall()
    print("\nMaterials by TMA:")
    for mg in mat_groups:
        print(f"  TMA ID {mg[0]}: {mg[1]} materials")

conn.close()