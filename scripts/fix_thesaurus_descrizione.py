#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per correggere i record del thesaurus inseriti senza descrizione
"""

import sqlite3
import os
import sys

def fix_thesaurus_descrizione(db_path):
    """Aggiorna i record con descrizione vuota."""
    print(f"Correzione record thesaurus: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Aggiorna tutti i record con descrizione NULL o vuota
        cursor.execute("""
            UPDATE pyarchinit_thesaurus_sigle 
            SET descrizione = '' 
            WHERE descrizione IS NULL
        """)
        
        updated = cursor.rowcount
        print(f"✅ Aggiornati {updated} record con descrizione NULL")
        
        # Verifica alcuni record
        cursor.execute("""
            SELECT id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, 
                   descrizione, tipologia_sigla, lingua
            FROM pyarchinit_thesaurus_sigle 
            WHERE nome_tabella = 'tma_materiali_archeologici'
            AND tipologia_sigla = '10.1'
            LIMIT 5
        """)
        
        print("\nEsempio record corretti:")
        for row in cursor.fetchall():
            print(f"  ID: {row[0]}, Sigla: {row[2]}, Estesa: {row[3]}, Tipo: {row[5]}")
        
        conn.commit()
        
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
    
    print("Correzione campo descrizione nei record thesaurus")
    print("=" * 60)
    
    if fix_thesaurus_descrizione(db_path):
        print("\n✅ Processo completato con successo!")
    else:
        print("\n❌ Processo fallito.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())