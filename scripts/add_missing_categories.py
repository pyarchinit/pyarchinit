#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per aggiungere le categorie mancanti
"""

import sqlite3
import os
import sys

def add_missing_categories(db_path):
    """Aggiunge le categorie mancanti."""
    print(f"Aggiunta categorie mancanti: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Categorie complete richieste
        required_categories = [
            ('MACC01', 'ceramica'),
            ('MACC02', 'vetro'),
            ('MACC03', 'metallo'),
            ('MACC04', 'materiale fittile'),
            ('MACC05', 'materiale litico'),
            ('MACC06', 'industria litica'),
            ('MACC07', 'osso'),
            ('MACC08', 'avorio'),
            ('MACC09', 'resti osteologici'),
            ('MACC10', 'legno'),
            ('MACC11', 'materiale organico'),
            ('MACC12', 'campioni di terra'),
            ('MACC13', 'altri materiali')
        ]
        
        # Verifica quali esistono già
        cursor.execute("""
            SELECT sigla FROM pyarchinit_thesaurus_sigle 
            WHERE nome_tabella = 'tma_materiali_archeologici' 
            AND tipologia_sigla = '10.7'
        """)
        existing = set(row[0] for row in cursor.fetchall())
        
        # Trova il prossimo ID
        cursor.execute("SELECT MAX(id_thesaurus_sigle) FROM pyarchinit_thesaurus_sigle")
        max_id = cursor.fetchone()[0] or 0
        next_id = max_id + 1
        
        # Inserisci le mancanti
        inserted = 0
        for sigla, sigla_estesa in required_categories:
            if sigla not in existing:
                cursor.execute("""
                    INSERT INTO pyarchinit_thesaurus_sigle 
                    (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, 
                     tipologia_sigla, lingua, order_layer, id_parent, parent_sigla, hierarchy_level)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    next_id,
                    'tma_materiali_archeologici',
                    sigla,
                    sigla_estesa,
                    '',
                    '10.7',
                    'IT',
                    0,
                    None,
                    None,
                    0
                ))
                next_id += 1
                inserted += 1
                print(f"  Inserita: {sigla} - {sigla_estesa}")
        
        print(f"\n✅ Inserite {inserted} categorie")
        
        # Commit
        conn.commit()
        
        # Verifica finale
        cursor.execute("""
            SELECT sigla, sigla_estesa 
            FROM pyarchinit_thesaurus_sigle 
            WHERE nome_tabella = 'tma_materiali_archeologici' 
            AND tipologia_sigla = '10.7'
            ORDER BY sigla
        """)
        
        print("\nCategorie finali (10.7):")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]}")
            
    except sqlite3.Error as e:
        print(f"❌ Errore: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()
    
    return True

def main():
    # Database path
    db_path = "/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite"
    
    if not os.path.exists(db_path):
        print(f"Database non trovato: {db_path}")
        return 1
    
    print("Aggiunta categorie mancanti TMA")
    print("=" * 60)
    
    if add_missing_categories(db_path):
        print("\n✅ Processo completato con successo!")
    else:
        print("\n❌ Processo fallito.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())