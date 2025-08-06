#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script per mostrare tutte le aree nel thesaurus
"""

import sqlite3
import os

db_path = os.path.expanduser("~/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite")

print(f"Database: {db_path}")
print("=" * 80)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Mostra tutte le aree TMA (10.7)
    print("\nAREE TMA NEL THESAURUS (tipologia 10.7):")
    cursor.execute("""
        SELECT sigla, sigla_estesa, descrizione
        FROM pyarchinit_thesaurus_sigle
        WHERE nome_tabella = 'TMA materiali archeologici'
        AND tipologia_sigla = '10.7'
        ORDER BY sigla
    """)
    
    tma_areas = cursor.fetchall()
    print(f"Totale: {len(tma_areas)} aree\n")
    
    for i, (sigla, sigla_estesa, desc) in enumerate(tma_areas):
        desc_str = f" | {desc}" if desc else ""
        print(f"{i+1:3d}. {sigla:20s} - {sigla_estesa:30s}{desc_str}")
    
    # 2. Mostra tutte le aree US (2.43)
    print("\n\nAREE US NEL THESAURUS (tipologia 2.43):")
    cursor.execute("""
        SELECT sigla, sigla_estesa, descrizione
        FROM pyarchinit_thesaurus_sigle
        WHERE nome_tabella = 'US'
        AND tipologia_sigla = '2.43'
        ORDER BY sigla
    """)
    
    us_areas = cursor.fetchall()
    print(f"Totale: {len(us_areas)} aree\n")
    
    for i, (sigla, sigla_estesa, desc) in enumerate(us_areas):
        desc_str = f" | {desc}" if desc else ""
        print(f"{i+1:3d}. {sigla:20s} - {sigla_estesa:30s}{desc_str}")
    
    # 3. Confronto con i dati reali
    print("\n\nCONFRONTO CON I DATI REALI:")
    
    # Aree nel thesaurus ma non nei dati TMA
    cursor.execute("""
        SELECT t.sigla 
        FROM pyarchinit_thesaurus_sigle t
        WHERE t.nome_tabella = 'TMA materiali archeologici'
        AND t.tipologia_sigla = '10.7'
        AND t.sigla NOT IN (
            SELECT DISTINCT area 
            FROM tma_materiali_archeologici 
            WHERE area IS NOT NULL AND area != ''
        )
        ORDER BY t.sigla
    """)
    
    orphan_areas = cursor.fetchall()
    if orphan_areas:
        print(f"\nAree nel thesaurus TMA ma NON presenti nei dati: {len(orphan_areas)}")
        print("Queste sono probabilmente aree predefinite o importate precedentemente:")
        for i, (area,) in enumerate(orphan_areas[:20]):
            print(f"  - {area}")
        if len(orphan_areas) > 20:
            print(f"  ... e altre {len(orphan_areas) - 20}")
    
    conn.close()
    
except Exception as e:
    print(f"ERRORE: {str(e)}")