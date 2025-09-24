#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script to monitor TMA materials persistence
Run this before and after operations to check if materials are being preserved
"""

import sqlite3
import os
from datetime import datetime

# Get the path to the SQLite database
db_path = os.path.join(os.path.dirname(__file__), 'pyarchinit_db.sqlite')

def monitor_materials():
    """Monitor TMA materials in the database"""
    if not os.path.exists(db_path):
        print(f"Database not found at: {db_path}")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n" + "="*60)
    print(f"TMA MATERIALS MONITOR - {datetime.now()}")
    print("="*60)
    
    # Check total materials
    cursor.execute("SELECT COUNT(*) FROM tma_materiali_ripetibili")
    total_materials = cursor.fetchone()[0]
    print(f"\n📊 Total materials in database: {total_materials}")
    
    # Show materials grouped by TMA with details
    cursor.execute("""
        SELECT 
            t.id,
            t.sito,
            t.area,
            t.dscu,
            t.cassetta,
            COUNT(m.id) as material_count
        FROM tma_materiali_archeologici t
        LEFT JOIN tma_materiali_ripetibili m ON t.id = m.id_tma
        GROUP BY t.id
        ORDER BY t.id DESC
        LIMIT 10
    """)
    
    print("\n📋 TMA records with material counts (last 10):")
    print("-" * 60)
    for row in cursor.fetchall():
        print(f"TMA ID: {row[0]}")
        print(f"  Sito: {row[1]}, Area: {row[2]}, US: {row[3]}, Cassetta: {row[4]}")
        print(f"  Materials: {row[5]}")
    
    # Show all materials with details
    cursor.execute("""
        SELECT 
            m.id,
            m.id_tma,
            m.madi,
            m.macc,
            m.macl,
            m.macd,
            m.macq,
            m.peso,
            t.sito,
            t.area,
            t.dscu
        FROM tma_materiali_ripetibili m
        JOIN tma_materiali_archeologici t ON m.id_tma = t.id
        ORDER BY m.id DESC
        LIMIT 20
    """)
    
    print("\n📦 Material details (last 20):")
    print("-" * 60)
    materials = cursor.fetchall()
    if materials:
        for mat in materials:
            print(f"Material ID: {mat[0]} (TMA: {mat[1]})")
            print(f"  TMA Info: {mat[8]} - Area {mat[9]} - US {mat[10]}")
            print(f"  Inventario: {mat[2]}")
            print(f"  Categoria: {mat[3]}, Classe: {mat[4]}, Definizione: {mat[5]}")
            print(f"  Quantità: {mat[6]}, Peso: {mat[7]}")
            print()
    else:
        print("  No materials found in database")
    
    # Check for orphaned materials
    cursor.execute("""
        SELECT COUNT(*) 
        FROM tma_materiali_ripetibili m
        WHERE NOT EXISTS (
            SELECT 1 FROM tma_materiali_archeologici t 
            WHERE t.id = m.id_tma
        )
    """)
    orphaned = cursor.fetchone()[0]
    if orphaned > 0:
        print(f"\n⚠️  WARNING: {orphaned} orphaned materials found (TMA record deleted)")
    
    conn.close()
    print("\n" + "="*60)

if __name__ == "__main__":
    monitor_materials()
    
    print("\n💡 Tips:")
    print("- Run this script before and after TMA operations")
    print("- Look for 'materials_loaded' flag status in the logs")