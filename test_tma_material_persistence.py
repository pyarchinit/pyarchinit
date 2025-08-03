#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify TMA materials persistence issue
"""

import sqlite3
import sys
import os

# Database path
db_path = "/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite"

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== Testing TMA Materials Persistence ===\n")

# 1. Check if there are any TMA records
cursor.execute("SELECT COUNT(*) FROM tma_materiali_archeologici")
tma_count = cursor.fetchone()[0]
print(f"Total TMA records: {tma_count}")

# 2. Check materials count
cursor.execute("SELECT COUNT(*) FROM tma_materiali_ripetibili")
materials_count = cursor.fetchone()[0]
print(f"Total materials: {materials_count}")

# 3. Show TMA records with their material counts
print("\n=== TMA Records and Material Counts ===")
cursor.execute("""
    SELECT 
        t.id, 
        t.sito,
        t.ldcn,
        t.cassetta,
        COUNT(m.id) as material_count
    FROM tma_materiali_archeologici t
    LEFT JOIN tma_materiali_ripetibili m ON t.id = m.id_tma
    GROUP BY t.id
    ORDER BY t.id DESC
    LIMIT 10
""")

results = cursor.fetchall()
print(f"{'ID':<5} {'Sito':<15} {'LDCN':<20} {'Cassetta':<10} {'Materials':<10}")
print("-" * 70)
for row in results:
    print(f"{row[0]:<5} {row[1] or '':<15} {row[2] or '':<20} {row[3] or '':<10} {row[4]:<10}")

# 4. Check for orphaned materials (materials without valid TMA parent)
print("\n=== Checking for Orphaned Materials ===")
cursor.execute("""
    SELECT COUNT(*) 
    FROM tma_materiali_ripetibili m
    WHERE NOT EXISTS (
        SELECT 1 FROM tma_materiali_archeologici t 
        WHERE t.id = m.id_tma
    )
""")
orphaned_count = cursor.fetchone()[0]
print(f"Orphaned materials (no valid TMA parent): {orphaned_count}")

# 5. Show a sample TMA with materials
if results and results[0][4] > 0:  # If first TMA has materials
    tma_id = results[0][0]
    print(f"\n=== Sample Materials for TMA ID {tma_id} ===")
    cursor.execute("""
        SELECT id, madi, macc, macl, macp, macd, macq, peso
        FROM tma_materiali_ripetibili
        WHERE id_tma = ?
        LIMIT 5
    """, (tma_id,))
    
    materials = cursor.fetchall()
    print(f"{'ID':<5} {'MADI':<15} {'MACC':<20} {'MACL':<15} {'MACP':<15}")
    print("-" * 85)
    for mat in materials:
        print(f"{mat[0]:<5} {mat[1] or '':<15} {mat[2] or '':<20} {mat[3] or '':<15} {mat[4] or '':<15}")

# 6. Check for potential issues with material IDs
print("\n=== Material ID Analysis ===")
cursor.execute("SELECT MIN(id), MAX(id) FROM tma_materiali_ripetibili")
min_id, max_id = cursor.fetchone()
print(f"Material ID range: {min_id} to {max_id}")

# Check for gaps in IDs that might indicate deletions
cursor.execute("""
    SELECT COUNT(*) as gap_count
    FROM (
        SELECT id + 1 as gap_start
        FROM tma_materiali_ripetibili m1
        WHERE NOT EXISTS (
            SELECT 1 FROM tma_materiali_ripetibili m2 
            WHERE m2.id = m1.id + 1
        )
        AND id < (SELECT MAX(id) FROM tma_materiali_ripetibili)
    )
""")
gap_count = cursor.fetchone()[0]
print(f"Number of gaps in material IDs (indicating deletions): {gap_count}")

conn.close()

print("\n=== Test Complete ===")