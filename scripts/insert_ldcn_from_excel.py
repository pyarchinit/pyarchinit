#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per inserire i valori ldcn (Denominazione collocazione) dall'Excel
"""

import sqlite3
import os
import sys

def insert_ldcn_values(cursor):
    """Inserisce i valori ldcn dal file Excel."""
    
    # Prima rimuovi i valori ldcn esistenti
    cursor.execute("""
        DELETE FROM pyarchinit_thesaurus_sigle 
        WHERE nome_tabella = 'TMA materiali archeologici' 
        AND tipologia_sigla = '10.1'
    """)
    print("✓ Rimossi valori ldcn (10.1) esistenti")
    
    # Valori esatti dall'Excel
    ldcn_values = [
        (1, 'Magazzino 1'),
        (2, 'Magazzino 2'),
        (3, 'Magazzino 3'),
        (4, 'Magazzino 4'),
        (5, 'Magazzino 5'),
        (6, 'Magazzino 6'),
        (7, 'Magazzino 7'),
    ]
    
    print("\nInserimento valori ldcn (Denominazione collocazione - 10.1):")
    inserted = 0
    
    for id_val, denominazione in ldcn_values:
        # Usa MAG + numero come sigla
        sigla = f"MAG{id_val:02d}"
        
        cursor.execute("""
            INSERT INTO pyarchinit_thesaurus_sigle 
            (nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua)
            VALUES ('TMA materiali archeologici', ?, ?, '10.1', 'it')
        """, (sigla, denominazione))
        
        print(f"  ✓ {id_val}. {denominazione}")
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
        print("Inserimento valori ldcn (Denominazione collocazione) dall'Excel...")
        print("=" * 60)
        
        inserted = insert_ldcn_values(cursor)
        
        conn.commit()
        
        print("\n" + "=" * 60)
        print(f"✅ Operazione completata!")
        print(f"   Totale valori inseriti: {inserted}")
        
        # Verifica
        cursor.execute("""
            SELECT sigla, sigla_estesa
            FROM pyarchinit_thesaurus_sigle 
            WHERE tipologia_sigla = '10.1'
            ORDER BY sigla
        """)
        
        print("\nVerifica valori ldcn inseriti:")
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