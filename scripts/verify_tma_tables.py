#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per verificare l'esistenza delle tabelle TMA nel database
"""

import sqlite3
import sys

def verify_tables(db_path):
    """Verifica l'esistenza delle tabelle TMA."""
    print(f"Verifica tabelle TMA in: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Lista tutte le tabelle
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        all_tables = cursor.fetchall()
        
        print("\nTutte le tabelle nel database:")
        tma_tables = []
        for table in all_tables:
            table_name = table[0]
            if 'tma' in table_name.lower():
                tma_tables.append(table_name)
                print(f"  ➤ {table_name} (TMA)")
            else:
                print(f"    {table_name}")
        
        print(f"\nTabelle TMA trovate: {len(tma_tables)}")
        for t in tma_tables:
            print(f"  - {t}")
        
        # Verifica se esiste tma_materiali_archeologici
        if 'tma_materiali_archeologici' in [t[0] for t in all_tables]:
            print("\n✓ Tabella 'tma_materiali_archeologici' ESISTE")
            
            # Verifica struttura
            cursor.execute("PRAGMA table_info(tma_materiali_archeologici)")
            columns = cursor.fetchall()
            print("\nColonne di tma_materiali_archeologici:")
            for col in columns[:5]:  # Prime 5 colonne
                print(f"  {col[1]} ({col[2]})")
            print(f"  ... ({len(columns)} colonne totali)")
        else:
            print("\n❌ Tabella 'tma_materiali_archeologici' NON TROVATA!")
        
        # Verifica se esiste tma_materiali_ripetibili
        if 'tma_materiali_ripetibili' in [t[0] for t in all_tables]:
            print("\n✓ Tabella 'tma_materiali_ripetibili' ESISTE")
        else:
            print("\n❌ Tabella 'tma_materiali_ripetibili' NON TROVATA!")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Errore: {e}")
        import traceback
        traceback.print_exc()

def main():
    db_path = "/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite"
    
    print("Verifica esistenza tabelle TMA")
    print("=" * 60)
    
    verify_tables(db_path)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())