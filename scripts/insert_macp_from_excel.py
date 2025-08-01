#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per inserire i valori macp (Precisazione tipologica) dall'Excel
"""

import sqlite3
import os
import sys

def insert_macp_values(cursor):
    """Inserisce i valori macp dal file Excel."""
    
    # Prima rimuovi i valori macp esistenti
    cursor.execute("""
        DELETE FROM pyarchinit_thesaurus_sigle 
        WHERE nome_tabella = 'tma_materiali_archeologici' 
        AND tipologia_sigla = '10.14'
    """)
    print("✓ Rimossi valori macp (10.14) esistenti")
    
    # Valori esatti dall'Excel
    macp_values = [
        (1, 'Neolitica grezza'),
        (2, 'Neolitica lucidata'),
        (3, 'Partyra'),
        (4, 'Pyrgos'),
        (5, 'Haghios Onouphrios'),
        (6, 'Haghios Onouphrios I'),
        (7, 'Haghios Onouphrios II'),
        (8, 'Lebena'),
        (9, 'Pelos'),
        (10, 'Koumasa'),
        (11, 'Vasiliki'),
        (12, 'Stile bianco'),
        (13, 'Patrikies'),
        (14, 'Kamares eggshell'),
        (15, 'Kamares fine'),
        (16, 'Kamares pareti spesse'),
        (17, 'Kamares rustico'),
        (18, 'Invetriata'),
        (19, 'Stampigliata'),
        (20, 'Maiolica'),
        (21, 'Neo Haghios Onouphrios'),
    ]
    
    print("\nInserimento valori macp (Precisazione tipologica - 10.14):")
    inserted = 0
    
    for id_val, precisazione in macp_values:
        # Usa MACP + numero come sigla
        sigla = f"MACP{id_val:02d}"
        
        cursor.execute("""
            INSERT INTO pyarchinit_thesaurus_sigle 
            (nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua)
            VALUES ('tma_materiali_archeologici', ?, ?, '10.14', 'it')
        """, (sigla, precisazione))
        
        print(f"  ✓ {id_val}. {precisazione}")
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
        print("Inserimento valori macp (Precisazione tipologica) dall'Excel...")
        print("=" * 60)
        
        inserted = insert_macp_values(cursor)
        
        conn.commit()
        
        print("\n" + "=" * 60)
        print(f"✅ Operazione completata!")
        print(f"   Totale valori inseriti: {inserted}")
        
        # Verifica per tipo
        cursor.execute("""
            SELECT COUNT(*) 
            FROM pyarchinit_thesaurus_sigle 
            WHERE tipologia_sigla = '10.14' AND sigla_estesa LIKE '%Kamares%'
        """)
        kamares_count = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) 
            FROM pyarchinit_thesaurus_sigle 
            WHERE tipologia_sigla = '10.14' AND sigla_estesa LIKE '%Haghios Onouphrios%'
        """)
        ho_count = cursor.fetchone()[0]
        
        print(f"\nRiepilogo per stile:")
        print(f"   Stili Kamares: {kamares_count}")
        print(f"   Stili Haghios Onouphrios: {ho_count}")
        print(f"   Altri stili: {inserted - kamares_count - ho_count}")
            
    except sqlite3.Error as e:
        print(f"\n❌ Errore: {e}")
        conn.rollback()
        return 1
        
    finally:
        conn.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())