#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Debug script per verificare i widget ldct e aint
"""

import sqlite3
import os

def debug_widgets():
    # Database path
    db_path = "/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite"
    
    if not os.path.exists(db_path):
        print(f"Database non trovato in: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=== DEBUG WIDGETS LDCT E AINT ===\n")
    
    # Verifica ldct (Tipologia Collocazione) - 10.2
    print("1. Tipologia Collocazione (ldct) - Codice 10.2:")
    print("-" * 50)
    
    cursor.execute("""
        SELECT sigla, sigla_estesa, lingua
        FROM pyarchinit_thesaurus_sigle
        WHERE nome_tabella = 'TMA materiali archeologici' 
        AND tipologia_sigla = '10.2'
        ORDER BY sigla_estesa
    """)
    
    ldct_values = cursor.fetchall()
    print(f"Trovati {len(ldct_values)} valori:")
    for sigla, sigla_estesa, lingua in ldct_values:
        print(f"  - [{sigla}] {sigla_estesa} ({lingua})")
    
    # Verifica aint (Tipologia Acquisizione) - 10.6
    print("\n2. Tipologia Acquisizione (aint) - Codice 10.6:")
    print("-" * 50)
    
    cursor.execute("""
        SELECT sigla, sigla_estesa, lingua
        FROM pyarchinit_thesaurus_sigle
        WHERE nome_tabella = 'TMA materiali archeologici' 
        AND tipologia_sigla = '10.6'
        ORDER BY sigla_estesa
    """)
    
    aint_values = cursor.fetchall()
    print(f"Trovati {len(aint_values)} valori:")
    for sigla, sigla_estesa, lingua in aint_values:
        print(f"  - [{sigla}] {sigla_estesa} ({lingua})")
    
    # Verifica le lingue
    print("\n3. Verifica lingue utilizzate:")
    print("-" * 50)
    
    cursor.execute("""
        SELECT DISTINCT lingua, COUNT(*)
        FROM pyarchinit_thesaurus_sigle
        WHERE nome_tabella = 'TMA materiali archeologici' 
        AND tipologia_sigla IN ('10.2', '10.6')
        GROUP BY lingua
    """)
    
    lingue = cursor.fetchall()
    for lingua, count in lingue:
        print(f"  - Lingua '{lingua}': {count} valori")
    
    # Verifica case sensitive della lingua
    print("\n4. Test case-sensitive lingua 'it' vs 'IT':")
    print("-" * 50)
    
    for lang in ['it', 'IT', 'It', 'iT']:
        cursor.execute("""
            SELECT COUNT(*)
            FROM pyarchinit_thesaurus_sigle
            WHERE nome_tabella = 'TMA materiali archeologici' 
            AND tipologia_sigla IN ('10.2', '10.6')
            AND lingua = ?
        """, (lang,))
        
        count = cursor.fetchone()[0]
        print(f"  - lingua = '{lang}': {count} valori")
    
    conn.close()

if __name__ == "__main__":
    debug_widgets()