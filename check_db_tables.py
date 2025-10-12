#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per verificare quali tabelle sono presenti in un database SQLite
"""

import sqlite3
import sys

def check_tables(db_path):
    """Elenca tutte le tabelle nel database"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Ottieni lista delle tabelle
        cursor.execute("""
            SELECT name, type 
            FROM sqlite_master 
            WHERE type IN ('table', 'view')
            ORDER BY type, name
        """)
        
        results = cursor.fetchall()
        
        print(f"\nDatabase: {db_path}")
        print("=" * 60)
        
        tables = [r for r in results if r[1] == 'table']
        views = [r for r in results if r[1] == 'view']
        
        print(f"\nTabelle ({len(tables)}):")
        for name, _ in tables:
            if not name.startswith('sqlite_'):
                print(f"  - {name}")
        
        print(f"\nView ({len(views)}):")
        for name, _ in views:
            print(f"  - {name}")
            
        # Cerca specificamente us_table
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='us_table'
        """)
        
        if not cursor.fetchone():
            print("\n⚠️  ATTENZIONE: Tabella 'us_table' NON TROVATA!")
            print("    Questo potrebbe essere un database di tipo diverso")
            print("    o potrebbe utilizzare nomi di tabella differenti.")
        
        conn.close()
        
    except Exception as e:
        print(f"Errore: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        db_path = "/Users/enzo/pyarchinit/pyarchinit_DB_folder/Sant_Arcangelo_La_Pieve94_3004.sqlite"
    else:
        db_path = sys.argv[1]
    
    check_tables(db_path)