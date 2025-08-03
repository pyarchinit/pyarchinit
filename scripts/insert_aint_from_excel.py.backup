#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per inserire i valori aint (Tipo di acquisizione) dall'Excel
"""

import sqlite3
import os
import sys

def insert_aint_values(cursor):
    """Inserisce i valori aint dal file Excel."""
    
    # Prima rimuovi i valori aint esistenti
    cursor.execute("""
        DELETE FROM pyarchinit_thesaurus_sigle 
        WHERE nome_tabella = 'tma_materiali_archeologici' 
        AND tipologia_sigla = '10.11'
    """)
    print("✓ Rimossi valori aint (10.11) esistenti")
    
    # Valori esatti dall'Excel
    aint_values = [
        (1, 'carotaggio'),
        (2, 'prospezione geoelettrica'),
        (3, 'prospezione magnetica'),
        (4, 'radargrafia'),
        (5, 'rilevamento geologico'),
        (6, 'rilevamento geomorfologico'),
        (7, 'rilevamento geopedologico'),
        (8, 'rilevamento pedologico'),
        (9, 'termografia'),
    ]
    
    print("\nInserimento valori aint (Tipo di acquisizione - 10.11):")
    inserted = 0
    
    for id_val, tipo in aint_values:
        # Usa AINT + numero come sigla
        sigla = f"AINT{id_val:02d}"
        
        cursor.execute("""
            INSERT INTO pyarchinit_thesaurus_sigle 
            (nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua)
            VALUES ('tma_materiali_archeologici', ?, ?, '10.11', 'it')
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
        print("Inserimento valori aint (Tipo di acquisizione) dall'Excel...")
        print("=" * 60)
        
        inserted = insert_aint_values(cursor)
        
        conn.commit()
        
        print("\n" + "=" * 60)
        print(f"✅ Operazione completata!")
        print(f"   Totale valori inseriti: {inserted}")
        
        # Verifica
        cursor.execute("""
            SELECT sigla, sigla_estesa
            FROM pyarchinit_thesaurus_sigle 
            WHERE tipologia_sigla = '10.11'
            ORDER BY sigla
        """)
        
        print("\nVerifica valori aint inseriti:")
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