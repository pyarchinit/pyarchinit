#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script per analizzare le aree nel database corretto
"""

import sqlite3
import os

# Path al database corretto
db_path = os.path.expanduser("~/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite")

print(f"Analizzando database: {db_path}")
print("=" * 80)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Analizza le aree in TMA
    print("\n1. ANALISI AREE IN tma_materiali_archeologici:")
    
    # Conta aree distinte
    cursor.execute("SELECT COUNT(DISTINCT area) FROM tma_materiali_archeologici WHERE area IS NOT NULL AND area != ''")
    distinct_areas = cursor.fetchone()[0]
    print(f"   Aree distinte (non nulle): {distinct_areas}")
    
    # Mostra prime 20 aree
    cursor.execute("SELECT DISTINCT area FROM tma_materiali_archeologici WHERE area IS NOT NULL AND area != '' ORDER BY area LIMIT 20")
    areas = cursor.fetchall()
    print(f"\n   Prime 20 aree:")
    for i, (area,) in enumerate(areas):
        print(f"     {i+1}. '{area}'")
    
    if distinct_areas > 20:
        print(f"     ... e altre {distinct_areas - 20} aree")
    
    # 2. Analizza US table
    print("\n\n2. ANALISI AREE IN us_table:")
    
    cursor.execute("SELECT COUNT(DISTINCT area) FROM us_table WHERE area IS NOT NULL AND area != ''")
    us_areas = cursor.fetchone()[0]
    print(f"   Aree distinte in US: {us_areas}")
    
    cursor.execute("SELECT DISTINCT area FROM us_table WHERE area IS NOT NULL AND area != '' ORDER BY area")
    areas = cursor.fetchall()
    print(f"\n   Aree trovate:")
    for i, (area,) in enumerate(areas):
        print(f"     {i+1}. '{area}'")
    
    # 3. Verifica perché il sync trova solo 3 aree
    
    # Query esatta usata dal sync
    cursor.execute("""
        SELECT DISTINCT area, sito 
        FROM tma_materiali_archeologici 
        WHERE area IS NOT NULL 
        AND area != ''
        ORDER BY area
    """)
    results = cursor.fetchall()
    print(f"\n   Query sync restituisce {len(results)} risultati")
    print("   Prime 10:")
    for i, (area, sito) in enumerate(results[:10]):
        print(f"     {i+1}. area='{area}', sito='{sito}'")
    
    # 4. Controlla il thesaurus attuale
    print("\n\n4. STATO ATTUALE THESAURUS:")
    
    # Aree TMA nel thesaurus
    cursor.execute("""
        SELECT COUNT(*) 
        FROM pyarchinit_thesaurus_sigle
        WHERE nome_tabella = 'TMA materiali archeologici'
        AND tipologia_sigla = '10.7'
    """)
    tma_thes = cursor.fetchone()[0]
    print(f"   Aree TMA nel thesaurus (10.7): {tma_thes}")
    
    # Aree US nel thesaurus
    cursor.execute("""
        SELECT COUNT(*) 
        FROM pyarchinit_thesaurus_sigle
        WHERE nome_tabella = 'US'
        AND tipologia_sigla = '2.43'
    """)
    us_thes = cursor.fetchone()[0]
    print(f"   Aree US nel thesaurus (2.43): {us_thes}")
    
    # Mostra esempi
    cursor.execute("""
        SELECT sigla, nome_tabella, tipologia_sigla, descrizione
        FROM pyarchinit_thesaurus_sigle
        WHERE tipologia_sigla IN ('10.7', '2.43')
        ORDER BY nome_tabella, sigla
        LIMIT 10
    """)
    print("\n   Esempi dal thesaurus:")
    for sigla, tabella, tipo, desc in cursor.fetchall():
        desc_str = f" - {desc}" if desc else ""
        print(f"     '{sigla}' (tabella: {tabella}, tipo: {tipo}){desc_str}")
    
    conn.close()
    
except Exception as e:
    print(f"ERRORE: {str(e)}")
    import traceback
    traceback.print_exc()