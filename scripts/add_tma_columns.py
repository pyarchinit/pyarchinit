#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per aggiungere colonne mancanti a tma_table
"""

import sqlite3
import sys

def add_columns(db_path):
    """Aggiunge le colonne created_by e updated_by."""
    print(f"Aggiunta colonne a: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Usa il nome corretto della tabella TMA
        table_name = 'tma_materiali_archeologici'
        print(f"Utilizzo tabella: {table_name}")
        
        # Verifica colonne esistenti
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        # Aggiungi created_by se manca
        if 'created_by' not in column_names:
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN created_by TEXT DEFAULT ''")
            print("✓ Aggiunta colonna created_by")
        else:
            print("  Colonna created_by già presente")
            
        # Aggiungi updated_by se manca
        if 'updated_by' not in column_names:
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN updated_by TEXT DEFAULT ''")
            print("✓ Aggiunta colonna updated_by")
        else:
            print("  Colonna updated_by già presente")
        
        conn.commit()
        conn.close()
        
        print("\n✅ Colonne aggiunte con successo!")
        return True
        
    except Exception as e:
        print(f"❌ Errore: {e}")
        return False

def main():
    db_path = "/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite"
    
    print("Aggiunta colonne mancanti TMA")
    print("=" * 60)
    
    if add_columns(db_path):
        print("\n✅ Processo completato!")
    else:
        print("\n❌ Processo fallito.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())