#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script to verify TMA materials save functionality
"""

import sqlite3
import os
from datetime import datetime

# Get the path to the SQLite database
db_path = os.path.join(os.path.dirname(__file__), 'pyarchinit_db.sqlite')

def check_tma_materials():
    """Check TMA materials in the database"""
    if not os.path.exists(db_path):
        print(f"Database not found at: {db_path}")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n=== TMA MATERIALS CHECK ===")
    print(f"Time: {datetime.now()}")
    
    # Check TMA records
    cursor.execute("SELECT COUNT(*) FROM tma_materiali_archeologici")
    tma_count = cursor.fetchone()[0]
    print(f"\nTotal TMA records: {tma_count}")
    
    # Show last 5 TMA records
    cursor.execute("""
        SELECT id, sito, area, dscu, cassetta 
        FROM tma_materiali_archeologici 
        ORDER BY id DESC 
        LIMIT 5
    """)
    print("\nLast 5 TMA records:")
    for row in cursor.fetchall():
        print(f"  ID: {row[0]}, Sito: {row[1]}, Area: {row[2]}, US: {row[3]}, Cassetta: {row[4]}")
    
    # Check materials
    cursor.execute("SELECT COUNT(*) FROM tma_materiali_ripetibili")
    materials_count = cursor.fetchone()[0]
    print(f"\nTotal TMA materials: {materials_count}")
    
    # Show materials grouped by TMA
    cursor.execute("""
        SELECT id_tma, COUNT(*) as material_count
        FROM tma_materiali_ripetibili
        GROUP BY id_tma
        ORDER BY id_tma DESC
        LIMIT 10
    """)
    print("\nMaterials per TMA (last 10):")
    for row in cursor.fetchall():
        print(f"  TMA ID {row[0]}: {row[1]} materials")
    
    # Show detailed materials for the last TMA with materials
    cursor.execute("""
        SELECT id_tma 
        FROM tma_materiali_ripetibili 
        ORDER BY id DESC 
        LIMIT 1
    """)
    last_tma_with_materials = cursor.fetchone()
    
    if last_tma_with_materials:
        tma_id = last_tma_with_materials[0]
        cursor.execute("""
            SELECT id, madi, macc, macl, macp, macd, macq, peso
            FROM tma_materiali_ripetibili
            WHERE id_tma = ?
            ORDER BY id
        """, (tma_id,))
        
        print(f"\nDetailed materials for TMA ID {tma_id}:")
        for row in cursor.fetchall():
            print(f"  Material ID: {row[0]}")
            print(f"    Inventario: {row[1]}, Categoria: {row[2]}, Classe: {row[3]}")
            print(f"    Precisazione: {row[4]}, Definizione: {row[5]}")
            print(f"    Quantità: {row[6]}, Peso: {row[7]}")
    
    conn.close()

if __name__ == "__main__":
    check_tma_materials()