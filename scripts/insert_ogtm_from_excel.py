#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per inserire i valori ogtm esatti dall'Excel
"""

import sqlite3
import os
import sys

def insert_ogtm_values(cursor):
    """Inserisce i valori ogtm dal file Excel."""
    
    # Prima rimuovi i valori ogtm esistenti
    cursor.execute("""
        DELETE FROM pyarchinit_thesaurus_sigle 
        WHERE nome_tabella = 'TMA materiali archeologici' 
        AND tipologia_sigla = 'ogtm'
    """)
    print("✓ Rimossi valori ogtm esistenti")
    
    # Valori esatti dall'Excel
    ogtm_values = [
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
    
    print("\nInserimento valori ogtm (Definizione materiale componente):")
    inserted = 0
    
    for id_val, definizione, note in ogtm_values:
        # Usa l'ID come sigla se non specificato diversamente
        sigla = f"MAT{id_val:02d}"
        
        cursor.execute("""
            INSERT INTO pyarchinit_thesaurus_sigle 
            (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
            VALUES ('TMA materiali archeologici', ?, ?, ?, 'ogtm', 'it')
        """, (sigla, definizione, note))
        
        print(f"  ✓ {id_val}. {definizione}" + (f" ({note})" if note else ""))
        inserted += 1
    
    # Inserisci anche gli stessi valori per macc (categoria nella tabella materiali)
    # che deve sincronizzarsi con ogtm
    cursor.execute("""
        DELETE FROM pyarchinit_thesaurus_sigle 
        WHERE nome_tabella = 'TMA materiali ripetibili' 
        AND tipologia_sigla = 'macc'
    """)
    
    print("\nInserimento valori macc (categoria materiali - sincronizza con ogtm):")
    
    for id_val, definizione, note in ogtm_values:
        sigla = f"MAT{id_val:02d}"
        
        cursor.execute("""
            INSERT INTO pyarchinit_thesaurus_sigle 
            (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
            VALUES ('TMA materiali ripetibili', ?, ?, ?, 'macc', 'it')
        """, (sigla, definizione, note))
        
        print(f"  ✓ {id_val}. {definizione}")
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
        print("Inserimento valori ogtm dall'Excel...")
        print("=" * 60)
        
        inserted = insert_ogtm_values(cursor)
        
        conn.commit()
        
        print("\n" + "=" * 60)
        print(f"✅ Operazione completata!")
        print(f"   Totale valori inseriti: {inserted}")
        
        # Verifica
        cursor.execute("""
            SELECT sigla, sigla_estesa, descrizione
            FROM pyarchinit_thesaurus_sigle 
            WHERE tipologia_sigla = 'ogtm'
            ORDER BY sigla
        """)
        
        print("\nVerifica valori ogtm inseriti:")
        for sigla, sigla_estesa, desc in cursor.fetchall():
            print(f"   {sigla}: {sigla_estesa}" + (f" - {desc}" if desc else ""))
            
    except sqlite3.Error as e:
        print(f"\n❌ Errore: {e}")
        conn.rollback()
        return 1
        
    finally:
        conn.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())