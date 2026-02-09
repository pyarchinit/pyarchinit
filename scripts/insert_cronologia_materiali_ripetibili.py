#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per inserire i valori di cronologia per TMA materiali ripetibili
"""

import sqlite3
import os

def insert_cronologia_values():
    # Database path
    db_path = "/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite"
    
    if not os.path.exists(db_path):
        print(f"Database non trovato in: {db_path}")
        return
        
    print(f"Uso database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Prima copia i valori di cronologia da TMA materiali archeologici
        print("Copio i valori di cronologia da TMA materiali archeologici...")
        
        cursor.execute("""
            INSERT INTO pyarchinit_thesaurus_sigle 
            (nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua, order_layer, id_parent, parent_sigla, hierarchy_level)
            SELECT 
                'TMA materiali ripetibili',
                sigla,
                sigla_estesa,
                tipologia_sigla,
                lingua,
                order_layer,
                id_parent,
                parent_sigla,
                hierarchy_level
            FROM pyarchinit_thesaurus_sigle
            WHERE nome_tabella = 'TMA materiali archeologici'
            AND tipologia_sigla = '10.4'
        """)
        
        inserted = cursor.rowcount
        print(f"✓ Inseriti {inserted} valori di cronologia per TMA materiali ripetibili")
        
        # Verifica
        cursor.execute("""
            SELECT COUNT(*) 
            FROM pyarchinit_thesaurus_sigle
            WHERE nome_tabella = 'TMA materiali ripetibili'
            AND tipologia_sigla = '10.4'
        """)
        
        count = cursor.fetchone()[0]
        print(f"\nVerifica: trovati {count} valori di cronologia in TMA materiali ripetibili")
        
        # Mostra alcuni esempi
        cursor.execute("""
            SELECT sigla, sigla_estesa
            FROM pyarchinit_thesaurus_sigle
            WHERE nome_tabella = 'TMA materiali ripetibili'
            AND tipologia_sigla = '10.4'
            ORDER BY sigla
            LIMIT 10
        """)
        
        print("\nEsempi di valori inseriti:")
        for sigla, sigla_estesa in cursor.fetchall():
            print(f"  - [{sigla}] {sigla_estesa}")
        
        conn.commit()
        print("\n✅ Operazione completata!")
        
    except sqlite3.Error as e:
        print(f"\n❌ Errore: {e}")
        conn.rollback()
        
    finally:
        conn.close()

if __name__ == "__main__":
    insert_cronologia_values()