#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per inserire i valori macc (Categoria) dall'Excel
"""

import sqlite3
import os
import sys

def insert_macc_values(cursor):
    """Inserisce i valori macc dal file Excel."""
    
    # Prima rimuovi i valori macc esistenti
    cursor.execute("""
        DELETE FROM pyarchinit_thesaurus_sigle 
        WHERE nome_tabella = 'tma_materiali_archeologici' 
        AND tipologia_sigla = '10.12'
    """)
    print("✓ Rimossi valori macc (10.12) esistenti")
    
    # Valori esatti dall'Excel con note
    macc_values = [
        (1, 'ceramica', ''),
        (2, 'vetro', ''),
        (3, 'metallo', 'argento, bronzo, oro, piombo, rame'),
        (4, 'materiale fittile', 'argilla'),
        (5, 'materiale litico', 'oggetti in pietra'),
        (6, 'industria litica', 'scheggiata, pesante'),
        (7, 'osso', ''),
        (8, 'avorio', ''),
        (9, 'resti osteologici', ''),
        (10, 'legno', ''),
        (11, 'materiale organico', 'carbone, resti animali'),
        (12, 'campioni di terra', ''),
        (13, 'altri materiali', 'pasta vitrea, cristallo di rocca, ocra'),
    ]
    
    print("\nInserimento valori macc (Categoria - 10.12):")
    inserted = 0
    
    for id_val, categoria, note in macc_values:
        # Usa MACC + numero come sigla
        sigla = f"MACC{id_val:02d}"
        
        # Se ci sono note, le aggiungiamo alla sigla_estesa
        if note:
            sigla_estesa = f"{categoria} ({note})"
        else:
            sigla_estesa = categoria
        
        cursor.execute("""
            INSERT INTO pyarchinit_thesaurus_sigle 
            (nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua)
            VALUES ('tma_materiali_archeologici', ?, ?, '10.12', 'it')
        """, (sigla, sigla_estesa))
        
        print(f"  ✓ {id_val}. {categoria}" + (f" - {note}" if note else ""))
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
        print("Inserimento valori macc (Categoria) dall'Excel...")
        print("=" * 60)
        
        inserted = insert_macc_values(cursor)
        
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
        
        print("\nVerifica valori macc inseriti:")
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