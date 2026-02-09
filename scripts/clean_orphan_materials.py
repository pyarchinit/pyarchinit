#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clean orphan materials records
"""

import sqlite3

# Database path
db_path = "/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite"

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== Cleaning Orphan Materials ===\n")

# Find orphan materials
cursor.execute("""
    SELECT DISTINCT tmr.id_tma 
    FROM tma_materiali_ripetibili tmr
    LEFT JOIN tma_materiali_archeologici tma ON tmr.id_tma = tma.id
    WHERE tma.id IS NULL
""")

orphan_tma_ids = cursor.fetchall()
print(f"Found {len(orphan_tma_ids)} orphan TMA IDs in materials table")

if orphan_tma_ids:
    # Delete orphan records
    for (tma_id,) in orphan_tma_ids:
        print(f"Deleting materials for non-existent TMA ID: {tma_id}")
        cursor.execute("DELETE FROM tma_materiali_ripetibili WHERE id_tma = ?", (tma_id,))
    
    conn.commit()
    print(f"\nDeleted materials for {len(orphan_tma_ids)} non-existent TMA records")

# Show current state
cursor.execute("SELECT COUNT(*) FROM tma_materiali_archeologici")
tma_count = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM tma_materiali_ripetibili")
mat_count = cursor.fetchone()[0]

print(f"\nCurrent state:")
print(f"TMA records: {tma_count}")
print(f"Materials records: {mat_count}")

conn.close()