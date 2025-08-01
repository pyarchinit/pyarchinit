#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per inserire i valori saggio e vano/locus nel thesaurus
"""

import sqlite3
import os
import sys

def insert_saggio_values(cursor):
    """Inserisce valori di esempio per saggio."""
    
    # Prima rimuovi i valori saggio esistenti
    cursor.execute("""
        DELETE FROM pyarchinit_thesaurus_sigle 
        WHERE nome_tabella = 'tma_materiali_archeologici' 
        AND tipologia_sigla = '10.2'
    """)
    print("✓ Rimossi valori saggio (10.2) esistenti")
    
    # Valori di esempio per saggio
    saggio_values = []
    for i in range(1, 21):
        saggio_values.append((i, f'Saggio {i}'))
    
    print("\nInserimento valori saggio (10.2):")
    inserted = 0
    
    for id_val, saggio in saggio_values:
        # Usa SAGG + numero come sigla
        sigla = f"SAGG{id_val:03d}"
        
        cursor.execute("""
            INSERT INTO pyarchinit_thesaurus_sigle 
            (nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua)
            VALUES ('tma_materiali_archeologici', ?, ?, '10.2', 'it')
        """, (sigla, saggio))
        
        if inserted < 10:
            print(f"  ✓ {id_val}. {saggio}")
        inserted += 1
    
    print(f"  ... (totale {inserted} saggi inseriti)")
    return inserted

def insert_vano_values(cursor):
    """Inserisce valori di esempio per vano/locus."""
    
    # Prima rimuovi i valori vano esistenti
    cursor.execute("""
        DELETE FROM pyarchinit_thesaurus_sigle 
        WHERE nome_tabella = 'tma_materiali_archeologici' 
        AND tipologia_sigla = '10.3' 
        AND sigla LIKE 'VANO%'
    """)
    print("✓ Rimossi valori vano/locus (10.3) esistenti")
    
    # Valori di esempio per vano/locus
    vano_values = []
    # Vani numerati
    for i in range(1, 31):
        vano_values.append((i, f'Vano {i}', 'VANO'))
    
    # Locus con lettere
    locus_id = 31
    for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        vano_values.append((locus_id, f'Locus {letter}', 'LOCUS'))
        locus_id += 1
    
    print("\nInserimento valori vano/locus (10.3):")
    inserted = 0
    
    for id_val, vano_locus, prefix in vano_values:
        # Usa prefix + numero come sigla
        if prefix == 'VANO':
            sigla = f"VANO{id_val:03d}"
        else:
            sigla = f"LOC{chr(64 + id_val - 30)}"  # LOCA, LOCB, etc.
        
        cursor.execute("""
            INSERT INTO pyarchinit_thesaurus_sigle 
            (nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua)
            VALUES ('tma_materiali_archeologici', ?, ?, '10.3', 'it')
        """, (sigla, vano_locus))
        
        if inserted < 15:
            print(f"  ✓ {vano_locus}")
        inserted += 1
    
    print(f"  ... (totale {inserted} vani/locus inseriti)")
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
        print("Inserimento valori saggio e vano/locus...")
        print("=" * 60)
        
        saggio_count = insert_saggio_values(cursor)
        vano_count = insert_vano_values(cursor)
        
        conn.commit()
        
        print("\n" + "=" * 60)
        print(f"✅ Operazione completata!")
        print(f"   Saggi inseriti: {saggio_count}")
        print(f"   Vani/Locus inseriti: {vano_count}")
        
        # Verifica
        cursor.execute("""
            SELECT COUNT(*) 
            FROM pyarchinit_thesaurus_sigle 
            WHERE tipologia_sigla = '10.2'
        """)
        saggio_total = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) 
            FROM pyarchinit_thesaurus_sigle 
            WHERE tipologia_sigla = '10.3' AND sigla LIKE 'VANO%'
        """)
        vano_total = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) 
            FROM pyarchinit_thesaurus_sigle 
            WHERE tipologia_sigla = '10.3' AND sigla LIKE 'LOC%'
        """)
        locus_total = cursor.fetchone()[0]
        
        print(f"\nVerifica database:")
        print(f"   Totale saggi: {saggio_total}")
        print(f"   Totale vani: {vano_total}")
        print(f"   Totale locus: {locus_total}")
            
    except sqlite3.Error as e:
        print(f"\n❌ Errore: {e}")
        conn.rollback()
        return 1
        
    finally:
        conn.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())