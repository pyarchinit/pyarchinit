#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per inserire i valori località dall'Excel
"""

import sqlite3
import os
import sys

def insert_localita_values(cursor):
    """Inserisce i valori località dal file Excel."""
    
    # Prima rimuovi i valori località esistenti
    cursor.execute("""
        DELETE FROM pyarchinit_thesaurus_sigle 
        WHERE nome_tabella = 'tma_materiali_archeologici' 
        AND tipologia_sigla = '10.18'
    """)
    print("✓ Rimossi valori località (10.18) esistenti")
    
    # Valori esatti dall'Excel
    localita_values = [
        (1, 'Festòs'),
        (2, 'Haghia Triada'),
        (3, 'Kamilari'),
        (4, 'Kannia'),
        (5, 'Territorio'),
        (6, 'Sporadico'),
    ]
    
    print("\nInserimento valori località (10.18):")
    inserted = 0
    
    for id_val, localita in localita_values:
        # Usa LOC + numero come sigla
        sigla = f"LOC{id_val:02d}"
        # ID per la gerarchia (1000 + id)
        id_thesaurus = 1000 + id_val
        
        cursor.execute("""
            INSERT INTO pyarchinit_thesaurus_sigle 
            (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua, hierarchy_level)
            VALUES (?, 'tma_materiali_archeologici', ?, ?, '10.18', 'it', 1)
        """, (id_thesaurus, sigla, localita))
        
        print(f"  ✓ {id_val}. {localita}")
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
        print("Inserimento valori località dall'Excel...")
        print("=" * 60)
        
        inserted = insert_localita_values(cursor)
        
        conn.commit()
        
        print("\n" + "=" * 60)
        print(f"✅ Operazione completata!")
        print(f"   Totale valori inseriti: {inserted}")
        
        # Verifica
        cursor.execute("""
            SELECT id_thesaurus_sigle, sigla, sigla_estesa
            FROM pyarchinit_thesaurus_sigle 
            WHERE tipologia_sigla = '10.18'
            ORDER BY sigla
        """)
        
        print("\nVerifica valori località inseriti:")
        for id_t, sigla, sigla_estesa in cursor.fetchall():
            print(f"   {sigla}: {sigla_estesa} (ID: {id_t})")
            
    except sqlite3.Error as e:
        print(f"\n❌ Errore: {e}")
        conn.rollback()
        return 1
        
    finally:
        conn.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())