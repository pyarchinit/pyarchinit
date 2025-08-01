#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per inserire i record LDCT mancanti
"""

import sqlite3
import os
import sys

def insert_ldct_records(db_path):
    """Inserisce i record LDCT."""
    print(f"Inserimento record LDCT: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Prima verifica il prossimo ID
        cursor.execute("SELECT MAX(id_thesaurus_sigle) FROM pyarchinit_thesaurus_sigle")
        max_id = cursor.fetchone()[0] or 0
        next_id = max_id + 1
        
        # Dati LDCT da inserire
        ldct_data = [
            ('LDCT01', 'cassetta'),
            ('LDCT02', 'cassa'),
            ('LDCT03', 'busta')
        ]
        
        print(f"Inserimento di {len(ldct_data)} record LDCT...")
        
        for i, (sigla, sigla_estesa) in enumerate(ldct_data):
            cursor.execute("""
                INSERT INTO pyarchinit_thesaurus_sigle 
                (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, 
                 tipologia_sigla, lingua, order_layer, id_parent, parent_sigla, hierarchy_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                next_id + i,
                'tma_materiali_archeologici',
                sigla,
                sigla_estesa,
                '',  # descrizione vuota
                '10.2',  # tipo LDCT
                'IT',
                0,
                None,
                None,
                0
            ))
        
        print(f"✅ Inseriti {cursor.rowcount} record LDCT")
        
        # Commit
        conn.commit()
        
        # Verifica
        cursor.execute("""
            SELECT sigla, sigla_estesa, tipologia_sigla 
            FROM pyarchinit_thesaurus_sigle 
            WHERE nome_tabella = 'tma_materiali_archeologici'
            AND tipologia_sigla = '10.2'
        """)
        
        print("\nRecord LDCT inseriti:")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]} (tipo {row[2]})")
            
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
    
    print("Inserimento record LDCT mancanti")
    print("=" * 60)
    
    if insert_ldct_records(db_path):
        print("\n✅ Processo completato con successo!")
    else:
        print("\n❌ Processo fallito.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())