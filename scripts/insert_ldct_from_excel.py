#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per inserire i valori ldct (Tipologia collocazione) dall'Excel
"""

import sqlite3
import os
import sys

def insert_ldct_values(cursor):
    """Inserisce i valori ldct dal file Excel."""
    
    # Prima rimuovi i valori ldct esistenti
    cursor.execute("""
        DELETE FROM pyarchinit_thesaurus_sigle 
        WHERE nome_tabella = 'TMA materiali archeologici' 
        AND tipologia_sigla = '10.2'
    """)
    print("✓ Rimossi valori ldct (10.10) esistenti")
    
    # Valori esatti dall'Excel
    ldct_values = [
        (1, 'Magazzino'),
        (2, 'Materiali all\'aperto'),
        (3, 'Museo di Heraklion'),
    ]
    
    print("\nInserimento valori ldct (Tipologia collocazione - 10.10):")
    inserted = 0
    
    for id_val, tipologia in ldct_values:
        # Usa l'ID come sigla
        sigla = f"LDCT{id_val:02d}"
        
        cursor.execute("""
            INSERT INTO pyarchinit_thesaurus_sigle 
            (nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua)
            VALUES ('TMA materiali archeologici', ?, ?, '10.2', 'it')
        """, (sigla, tipologia))
        
        print(f"  ✓ {id_val}. {tipologia}")
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
        print("Inserimento valori ldct (Tipologia collocazione) dall'Excel...")
        print("=" * 60)
        
        inserted = insert_ldct_values(cursor)
        
        conn.commit()
        
        print("\n" + "=" * 60)
        print(f"✅ Operazione completata!")
        print(f"   Totale valori inseriti: {inserted}")
        
        # Verifica
        cursor.execute("""
            SELECT sigla, sigla_estesa
            FROM pyarchinit_thesaurus_sigle 
            WHERE tipologia_sigla = '10.2'
            ORDER BY sigla
        """)
        
        print("\nVerifica valori ldct inseriti:")
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