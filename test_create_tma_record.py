#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to create a test TMA record with materials
"""

import sqlite3
from datetime import datetime

# Database path
db_path = "/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite"

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== Creating Test TMA Record ===")

# Create a TMA record with correct columns
tma_data = {
    'sito': 'Roma',
    'area': 'Area 1',
    'localita': 'ROM',
    'settore': 'A',
    'ogtm': 'Materiali misti',
    'ldct': 'Ceramica',
    'ldcn': 'TEST-001',
    'cassetta': 'CASS-001',
    'scan': 'Scan001',
    'saggio': 'Saggio 1',
    'vano_locus': 'Locus 1',
    'dscd': 'Desc1',
    'dscu': 'Unit1',
    'rcgd': 'RCG1',
    'rcgz': 'Zone1',
    'aint': 'Int1',
    'aind': 'Ind1',
    'dtzg': datetime.now().strftime('%Y-%m-%d')
}

# Insert TMA record
columns = ', '.join(tma_data.keys())
placeholders = ', '.join(['?' for _ in tma_data])
values = list(tma_data.values())

try:
    cursor.execute(f"INSERT INTO tma_materiali_archeologici ({columns}) VALUES ({placeholders})", values)
    tma_id = cursor.lastrowid
    print(f"Created TMA record with ID: {tma_id}")
    
    # Add materials to this TMA record
    materials_data = [
        (tma_id, 'C', 'CC', 'CF', 'Piatto', 'Frammenti di piatto', '5', 250.5),
        (tma_id, 'C', 'CF', 'Sigillata', 'Coppa', 'Coppa verniciata', '3', 120.0),
        (tma_id, 'V', 'VB', 'Verde', 'Bottiglia', 'Collo di bottiglia', '2', 80.0),
        (tma_id, 'M', 'MF', 'Ferro', 'Chiodo', 'Chiodi vari', '10', 150.0),
        (tma_id, 'L', 'L', 'Tegola', 'Tegola', 'Frammento di tegola', '1', 450.0)
    ]
    
    for mat in materials_data:
        cursor.execute("""
            INSERT INTO tma_materiali_ripetibili 
            (id_tma, madi, macc, macl, macp, macd, macq, peso)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, mat)
    
    print(f"Added {len(materials_data)} materials to TMA record")
    
    conn.commit()
    
    # Verify the insertion
    cursor.execute("""
        SELECT t.id, t.ldcn, COUNT(m.id) as material_count
        FROM tma_materiali_archeologici t
        LEFT JOIN tma_materiali_ripetibili m ON t.id = m.id_tma
        WHERE t.id = ?
        GROUP BY t.id
    """, (tma_id,))
    
    result = cursor.fetchone()
    print(f"\nVerification: TMA ID {result[0]}, LDCN: {result[1]}, Materials: {result[2]}")
    
    # Show the materials
    print("\n=== Materials Added ===")
    cursor.execute("""
        SELECT madi, macc, macl, macp, macd, macq, peso
        FROM tma_materiali_ripetibili
        WHERE id_tma = ?
    """, (tma_id,))
    
    materials = cursor.fetchall()
    for mat in materials:
        print(f"{mat[0]} - {mat[1]} ({mat[2]}) - {mat[4]}: {mat[5]} pezzi, {mat[6]}g")
    
except sqlite3.Error as e:
    print(f"Error creating TMA record: {e}")
    conn.rollback()

conn.close()

print("\n=== Test TMA Record Created Successfully ===")
print("\nNOTE: Now you can:")
print("1. Open the TMA form in QGIS")
print("2. Load this record (LDCN: TEST-001)")
print("3. Close and reopen the form")
print("4. Check if the materials are still there")