#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monitor database changes for TMA table
"""

import sqlite3
import time

# Database path
db_path = "/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite"

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== Monitoring TMA Database ===")
print("\nPress Ctrl+C to stop monitoring\n")

try:
    last_count = -1
    last_materials_count = -1
    
    while True:
        # Check TMA records
        cursor.execute("SELECT COUNT(*) FROM tma_materiali_archeologici")
        tma_count = cursor.fetchone()[0]
        
        # Check materials
        cursor.execute("SELECT COUNT(*) FROM tma_materiali_ripetibili")
        materials_count = cursor.fetchone()[0]
        
        # Check for changes
        if tma_count != last_count or materials_count != last_materials_count:
            print(f"[{time.strftime('%H:%M:%S')}] TMA records: {tma_count}, Materials: {materials_count}")
            
            # Show details if there are records
            if tma_count > 0:
                cursor.execute("SELECT id, sito, ldcn FROM tma_materiali_archeologici ORDER BY id")
                records = cursor.fetchall()
                for rec in records:
                    print(f"  - TMA ID {rec[0]}: Sito='{rec[1]}', LDCN='{rec[2]}'")
            
            last_count = tma_count
            last_materials_count = materials_count
        
        time.sleep(1)  # Check every second
        
except KeyboardInterrupt:
    print("\n=== Monitoring stopped ===")
    
conn.close()