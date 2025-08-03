#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per inserire i valori macl (Classe) dall'Excel
"""

import sqlite3
import os
import sys

def insert_macl_values(cursor):
    """Inserisce i valori macl dal file Excel."""
    
    # Prima rimuovi i valori macl esistenti
    cursor.execute("""
        DELETE FROM pyarchinit_thesaurus_sigle 
        WHERE nome_tabella = 'tma_materiali_archeologici' 
        AND tipologia_sigla = '10.13'
    """)
    print("✓ Rimossi valori macl (10.13) esistenti")
    
    # Valori esatti dall'Excel
    macl_values = [
        (1, 'Ceramica fine'),
        (2, 'Ceramica decorata fine'),
        (3, 'Ceramica acroma fine'),
        (4, 'Ceramica semifine'),
        (5, 'Ceramica grezza'),
        (6, 'Ceramica decorata grezza'),
        (7, 'Ceramica acroma grezza'),
        (8, 'Ceramica da fuoco'),
        (9, 'Vasi per illuminare/riscaldare'),
        (10, 'Vasi plastici (vasi configurati)'),
        (11, 'Vasi miniaturistici'),
        (12, 'Vasi e oggetti ceramici vari'),
        (13, 'Statuine e figurine'),
        (14, 'Attrezzi per la tessitura'),
        (15, 'Altri rinvenimenti (ex small finds)'),
        (16, 'Incerti'),
    ]
    
    print("\nInserimento valori macl (Classe - 10.13):")
    inserted = 0
    
    for id_val, classe in macl_values:
        # Usa MACL + numero come sigla
        sigla = f"MACL{id_val:02d}"
        
        cursor.execute("""
            INSERT INTO pyarchinit_thesaurus_sigle 
            (nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua)
            VALUES ('tma_materiali_archeologici', ?, ?, '10.13', 'it')
        """, (sigla, classe))
        
        print(f"  ✓ {id_val}. {classe}")
        inserted += 1
    
    return inserted

def main():
    # Database path
    db_path = "/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite"
    
    if not os.path.exists(db_path):
        print(f"Database non trovato in: {db_path}")
        return 1
        
    print(f"Uso database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("Inserimento valori macl (Classe) dall'Excel...")
        print("=" * 60)
        
        inserted = insert_macl_values(cursor)
        
        conn.commit()
        
        print("\n" + "=" * 60)
        print(f"✅ Operazione completata!")
        print(f"   Totale valori inseriti: {inserted}")
        
        # Verifica
        cursor.execute("""
            SELECT sigla, sigla_estesa
            FROM pyarchinit_thesaurus_sigle 
            WHERE tipologia_sigla = '10.13'
            ORDER BY sigla
        """)
        
        print("\nVerifica valori macl inseriti:")
        for sigla, sigla_estesa in cursor.fetchall():
            print(f"   {sigla}: {sigla_estesa}")
            
    except sqlite3.Error as e:
        print(f"\n❌ Errore: {e}")
        conn.rollback()
        return 1
        
    finally:
        conn.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())