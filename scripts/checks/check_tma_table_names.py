#!/usr/bin/env python3
"""
Check what table names are actually stored in the database for TMA records
"""

import sqlite3
import os

def check_tma_table_names():
    """Check the table names used in TMA thesaurus records"""
    
    # Path to the database
    db_path = "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/pyarchinit_db.sqlite"
    
    if not os.path.exists(db_path):
        print(f"Database not found at: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== Checking TMA Table Names in Database ===")
        
        # Check all unique table names that contain "TMA" or "tma"
        print("\n1. All table names containing 'TMA' or 'tma':")
        cursor.execute("""
        SELECT DISTINCT nome_tabella, COUNT(*) as count
        FROM pyarchinit_thesaurus_sigle 
        WHERE UPPER(nome_tabella) LIKE '%TMA%'
        GROUP BY nome_tabella
        ORDER BY nome_tabella
        """)
        
        tma_tables = cursor.fetchall()
        print(f"Found {len(tma_tables)} different TMA table names:")
        
        for table_name, count in tma_tables:
            print(f"  '{table_name}' - {count} records")
        
        # Check specific records for each table name
        print("\n2. Sample records for each TMA table name:")
        for table_name, count in tma_tables:
            print(f"\n   Table: '{table_name}' ({count} records)")
            
            cursor.execute("""
            SELECT tipologia_sigla, COUNT(*) as count
            FROM pyarchinit_thesaurus_sigle 
            WHERE nome_tabella = ?
            GROUP BY tipologia_sigla
            ORDER BY tipologia_sigla
            """, (table_name,))
            
            codes = cursor.fetchall()
            print(f"     Codes used: {', '.join([f'{code}({count})' for code, count in codes])}")
        
        # Check if there are inconsistencies
        print("\n3. Checking for inconsistencies:")
        
        expected_names = [
            'TMA materiali archeologici',
            'TMA Materiali Ripetibili',
            'tma_materiali_archeologici',  # lowercase version
            'tma_materiali_ripetibili'     # lowercase version
        ]
        
        found_names = [name for name, count in tma_tables]
        
        print("Expected table names:")
        for name in expected_names:
            if name in found_names:
                print(f"  ✓ '{name}' - FOUND")
            else:
                print(f"  ✗ '{name}' - NOT FOUND")
        
        print("\nActual table names found:")
        for name in found_names:
            if name in expected_names:
                print(f"  ✓ '{name}' - EXPECTED")
            else:
                print(f"  ⚠️  '{name}' - UNEXPECTED")
        
        conn.close()
        
        print(f"\n=== Summary ===")
        if len(tma_tables) > 2:
            print("⚠️  WARNING: More than 2 TMA table names found - there may be inconsistencies")
        elif len(tma_tables) == 2:
            print("✓ Found 2 TMA table names as expected")
        else:
            print("⚠️  WARNING: Less than 2 TMA table names found")
        
    except Exception as e:
        print(f"Error checking database: {e}")

if __name__ == "__main__":
    check_tma_table_names()