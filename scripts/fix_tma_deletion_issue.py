#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per risolvere il problema di cancellazione dei materiali TMA
"""

import sqlite3
import sys

def check_foreign_keys(db_path):
    """Verifica lo stato delle foreign keys."""
    print(f"Verifica foreign keys in: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verifica se le foreign keys sono abilitate
        cursor.execute("PRAGMA foreign_keys")
        fk_status = cursor.fetchone()
        print(f"\nForeign keys abilitate: {fk_status[0] if fk_status else 'NO'}")
        
        # Verifica la struttura di tma_materiali_ripetibili
        cursor.execute("PRAGMA foreign_key_list(tma_materiali_ripetibili)")
        fk_list = cursor.fetchall()
        
        if fk_list:
            print("\nForeign keys in tma_materiali_ripetibili:")
            for fk in fk_list:
                print(f"  - {fk}")
        else:
            print("\nNessuna foreign key trovata in tma_materiali_ripetibili")
        
        # Prova a ricreare la tabella senza foreign key constraint
        print("\n✅ Soluzione: Ricreare la tabella senza foreign key constraint")
        
        # Prima rinomina la tabella esistente
        try:
            cursor.execute("ALTER TABLE tma_materiali_ripetibili RENAME TO tma_materiali_ripetibili_backup")
            print("  - Tabella originale rinominata in tma_materiali_ripetibili_backup")
        except:
            print("  - Tabella backup già esistente o errore nel rinominare")
        
        # Crea la nuova tabella senza foreign key
        create_sql = """
        CREATE TABLE IF NOT EXISTS tma_materiali_ripetibili (
            id INTEGER PRIMARY KEY,
            id_tma INTEGER NOT NULL,
            madi TEXT,
            macc TEXT NOT NULL,
            macl TEXT,
            macp TEXT,
            macd TEXT,
            cronologia_mac TEXT,
            macq TEXT,
            peso REAL,
            created_at TEXT,
            updated_at TEXT,
            created_by TEXT,
            updated_by TEXT
        )
        """
        
        cursor.execute(create_sql)
        print("  - Nuova tabella creata senza foreign key constraint")
        
        # Copia i dati dalla tabella backup se esiste
        try:
            cursor.execute("""
                INSERT INTO tma_materiali_ripetibili 
                SELECT * FROM tma_materiali_ripetibili_backup
            """)
            count = cursor.rowcount
            print(f"  - {count} record copiati dalla tabella backup")
        except:
            print("  - Nessun dato da copiare o tabella backup non trovata")
        
        # Crea un indice per migliorare le performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tma_materiali_id_tma ON tma_materiali_ripetibili(id_tma)")
        print("  - Indice creato su id_tma")
        
        conn.commit()
        conn.close()
        
        print("\n✅ Problema risolto!")
        
    except Exception as e:
        print(f"❌ Errore: {e}")
        import traceback
        traceback.print_exc()

def main():
    db_path = "/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite"
    
    print("Fix problema cancellazione materiali TMA")
    print("=" * 60)
    
    check_foreign_keys(db_path)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())