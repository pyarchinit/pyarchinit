#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per verificare lo stato delle geometrie nel database
"""

import sqlite3
import os

def check_geometries(db_path):
    """Verifica lo stato delle colonne geometriche"""
    
    print(f"\nVerifica geometrie in: {os.path.basename(db_path)}")
    print("="*60)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Verifica geometry_columns
    cursor.execute("""
        SELECT f_table_name, f_geometry_column, geometry_type, coord_dimension, srid
        FROM geometry_columns
        ORDER BY f_table_name
    """)
    
    print("\n📐 COLONNE GEOMETRICHE REGISTRATE:")
    print(f"{'Tabella':<30} {'Colonna':<15} {'Tipo':<20} {'Dim':<5} {'SRID':<8}")
    print("-"*80)
    
    for row in cursor.fetchall():
        table, col, geom_type, dim, srid = row
        print(f"{table:<30} {col:<15} {geom_type:<20} {dim:<5} {srid:<8}")
    
    # Verifica tipi di colonna effettivi
    print("\n🔍 VERIFICA TIPI COLONNE EFFETTIVI:")
    
    critical_tables = [
        'pyunitastratigrafiche',
        'pyunitastratigrafiche_usm',
        'pyarchinit_quote',
        'pyarchinit_quote_usm',
        'pyarchinit_us_negative_doc'
    ]
    
    for table in critical_tables:
        cursor.execute(f"""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='{table}'
        """)
        
        if cursor.fetchone():
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            
            for col in columns:
                if col[1] == 'the_geom':
                    print(f"{table}.the_geom: tipo={col[2]}")
                    break
        else:
            print(f"{table}: TABELLA NON TROVATA")
    
    conn.close()

if __name__ == "__main__":
    db_path = "/Users/enzo/pyarchinit/pyarchinit_DB_folder/ktm24.sqlite"
    check_geometries(db_path)