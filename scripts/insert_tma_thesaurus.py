#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per inserire i valori del thesaurus TMA nel database
Verifica prima se i valori esistono già per evitare duplicati
"""

import sqlite3
import os
import sys

# Definizione dei valori del thesaurus TMA
THESAURUS_DATA = {

    '10.9': {  # Tipo disegno (drat)
        'description': 'Tipo disegno',
        'values': [
            ('RIL', 'Rilievo'),
            ('RIC', 'Ricostruzione'),
            ('SEZ', 'Sezione'),
            ('PRO', 'Profilo'),
            ('DEC', 'Decorazione'),
            ('SCH', 'Schema'),
        ]
    },

}

def insert_thesaurus_values(cursor, nome_tabella='TMA materiali archeologici', lingua='it'):
    """Insert thesaurus values into database."""
    inserted_count = 0
    skipped_count = 0
    
    for tipologia_sigla, data in THESAURUS_DATA.items():
        print(f"\n{tipologia_sigla} - {data['description']}:")
        
        for sigla, sigla_estesa in data['values']:
            # Check if value already exists
            cursor.execute("""
                SELECT COUNT(*) FROM pyarchinit_thesaurus_sigle 
                WHERE nome_tabella = ? AND tipologia_sigla = ? AND sigla = ? AND lingua = ?
            """, (nome_tabella, tipologia_sigla, sigla, lingua))
            
            exists = cursor.fetchone()[0] > 0
            
            if not exists:
                cursor.execute("""
                    INSERT INTO pyarchinit_thesaurus_sigle 
                    (nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua)
                    VALUES (?, ?, ?, ?, ?)
                """, (nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua))
                print(f"  ✓ Inserito: {sigla} - {sigla_estesa}")
                inserted_count += 1
            else:
                print(f"  - Esiste già: {sigla} - {sigla_estesa}")
                skipped_count += 1
    
    return inserted_count, skipped_count

def main():
    # Database path
    db_path = os.path.expanduser("/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite")
    
    # Alternative path if running from plugin directory
    if not os.path.exists(db_path):
        plugin_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(plugin_dir, "pyarchinit_db.sqlite")
    
    if not os.path.exists(db_path):
        print(f"Database non trovato in: {db_path}")
        return 1
        
    print(f"Uso database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if thesaurus table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='pyarchinit_thesaurus_sigle'
        """)
        if not cursor.fetchone():
            print("❌ La tabella 'pyarchinit_thesaurus_sigle' non esiste!")
            print("Assicurati che il database PyArchInit sia stato inizializzato correttamente.")
            return 1
        
        print("\nInserimento valori thesaurus TMA...")
        print("=" * 50)
        
        # Insert Italian values
        inserted_it, skipped_it = insert_thesaurus_values(cursor, lingua='it')
        
        # Optionally insert English values (you can customize these)
        # inserted_en, skipped_en = insert_thesaurus_values(cursor, lingua='en')
        
        conn.commit()
        
        print("\n" + "=" * 50)
        print(f"✅ Operazione completata!")
        print(f"   - Valori inseriti: {inserted_it}")
        print(f"   - Valori già esistenti: {skipped_it}")
        print(f"   - Totale valori nel thesaurus: {inserted_it + skipped_it}")
        
    except sqlite3.Error as e:
        print(f"\n❌ Errore durante l'inserimento: {e}")
        conn.rollback()
        return 1
        
    finally:
        conn.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())