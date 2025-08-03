#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per inserire i valori ftap (Tipo fotografia) dall'Excel
"""

import sqlite3
import os
import sys

def insert_ftap_values(cursor):
    """Inserisce i valori ftap dal file Excel."""
    
    # Prima rimuovi i valori ftap esistenti
    cursor.execute("""
        DELETE FROM pyarchinit_thesaurus_sigle 
        WHERE nome_tabella = 'TMA materiali archeologici' 
        AND tipologia_sigla = '10.8'
    """)
    print("✓ Rimossi valori ftap (10.8) esistenti")
    
    # Valori esatti dall'Excel
    ftap_values = [
        (1, 'fotografia b/n'),
        (2, 'diapositiva b/n'),
        (3, 'diapositiva colore'),
        (4, 'fotografia colore'),
        (5, 'fotografia a raggi infrarossi'),
        (6, 'fotografia digitale'),
    ]
    
    print("\nInserimento valori ftap (Tipo fotografia - 10.8):")
    inserted = 0
    
    for id_val, tipo in ftap_values:
        # Usa FTAP + numero come sigla
        sigla = f"FTAP{id_val:02d}"
        
        cursor.execute("""
            INSERT INTO pyarchinit_thesaurus_sigle 
            (nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua)
            VALUES ('TMA materiali archeologici', ?, ?, '10.8', 'it')
        """, (sigla, tipo))
        
        print(f"  ✓ {id_val}. {tipo}")
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
        print("Inserimento valori ftap (Tipo fotografia) dall'Excel...")
        print("=" * 60)
        
        inserted = insert_ftap_values(cursor)
        
        conn.commit()
        
        print("\n" + "=" * 60)
        print(f"✅ Operazione completata!")
        print(f"   Totale valori inseriti: {inserted}")
        
        # Verifica
        cursor.execute("""
            SELECT sigla, sigla_estesa
            FROM pyarchinit_thesaurus_sigle 
            WHERE tipologia_sigla = '10.12'
            ORDER BY sigla
        """)
        
        print("\nVerifica valori ftap inseriti:")
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