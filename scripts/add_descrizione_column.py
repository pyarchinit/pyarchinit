#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per aggiungere la colonna descrizione alla tabella pyarchinit_thesaurus_sigle
"""

import sqlite3
import os
import sys

def add_descrizione_column(db_path):
    """Aggiunge la colonna descrizione se non esiste."""
    print(f"Aggiornamento database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Verifica se la colonna esiste già
        cursor.execute("PRAGMA table_info(pyarchinit_thesaurus_sigle)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'descrizione' in columns:
            print("La colonna 'descrizione' esiste già.")
            return True
            
        print("Aggiunta colonna 'descrizione'...")
        
        # Aggiungi la colonna descrizione dopo sigla_estesa
        cursor.execute("""
            ALTER TABLE pyarchinit_thesaurus_sigle 
            ADD COLUMN descrizione TEXT
        """)
        
        conn.commit()
        print("✅ Colonna 'descrizione' aggiunta con successo!")
        
        # Verifica
        cursor.execute("PRAGMA table_info(pyarchinit_thesaurus_sigle)")
        columns = cursor.fetchall()
        
        print("\nStruttura attuale della tabella:")
        for col in columns:
            print(f"  {col[1]}: {col[2]}")
            
    except sqlite3.Error as e:
        print(f"❌ Errore: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()
    
    return True

def main():
    # Database path
    db_path = "/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite"
    
    if not os.path.exists(db_path):
        print(f"Database non trovato: {db_path}")
        return 1
    
    print("Aggiunta colonna descrizione a pyarchinit_thesaurus_sigle")
    print("=" * 60)
    
    if add_descrizione_column(db_path):
        print("\n✅ Processo completato con successo!")
    else:
        print("\n❌ Processo fallito.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())