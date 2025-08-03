#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug script to trace TMA deletion issue
"""

import sqlite3
import time

# Database path
db_path = "/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite"

print("=== TMA Deletion Debug ===\n")

# First create a test record
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check initial state
cursor.execute("SELECT COUNT(*) FROM tma_materiali_archeologici")
initial_count = cursor.fetchone()[0]
print(f"Initial TMA records: {initial_count}")

# Create test record if none exist
if initial_count == 0:
    cursor.execute("""
        INSERT INTO tma_materiali_archeologici 
        (sito, area, localita, settore, ogtm, ldct, ldcn, cassetta, dscu, dtzg)
        VALUES 
        ('Test Site', 'Area 1', 'Località Test', 'Settore A', 'Test Material', 
         'Magazzino', 'LDCN001', 'C001', 'US001', 'I secolo d.C.')
    """)
    conn.commit()
    print("Created test TMA record")

# Now monitor for changes
print("\nMonitoring for deletions...")
print("Check the QGIS plugin now\n")

last_count = cursor.execute("SELECT COUNT(*) FROM tma_materiali_archeologici").fetchone()[0]

for i in range(30):  # Monitor for 30 seconds
    time.sleep(1)
    current_count = cursor.execute("SELECT COUNT(*) FROM tma_materiali_archeologici").fetchone()[0]
    
    if current_count != last_count:
        print(f"[{time.strftime('%H:%M:%S')}] CHANGE DETECTED! Count: {last_count} -> {current_count}")
        
        if current_count < last_count:
            print("RECORDS WERE DELETED!")
            
            # Try to find what might have caused it
            cursor.execute("SELECT name FROM sqlite_master WHERE type='trigger'")
            triggers = cursor.fetchall()
            if triggers:
                print("Database triggers found:")
                for t in triggers:
                    print(f"  - {t[0]}")
                    
        last_count = current_count
    else:
        print(f"[{time.strftime('%H:%M:%S')}] No change. Count: {current_count}")

conn.close()