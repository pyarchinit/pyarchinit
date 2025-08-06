#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script per analizzare le aree nel database e capire perché non vengono trovate tutte
"""

import sqlite3
import os

# Path al database
db_path = os.path.expanduser("~/pyarchinit/pyarchinit_DB_folder/pyarchnitDB.sqlite")

print(f"Analizzando database: {db_path}")
print("=" * 80)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Controlla struttura tabella TMA
    print("\n1. STRUTTURA TABELLA tma_materiali_archeologici:")
    cursor.execute("PRAGMA table_info(tma_materiali_archeologici)")
    columns = cursor.fetchall()
    for col in columns:
        print(f"   {col[1]} - {col[2]}")
    
    # 2. Conta tutti i record TMA
    cursor.execute("SELECT COUNT(*) FROM tma_materiali_archeologici")
    total_tma = cursor.fetchone()[0]
    print(f"\n2. TOTALE RECORD TMA: {total_tma}")
    
    # 3. Analizza le aree in TMA
    print("\n3. ANALISI AREE IN TMA:")
    
    # Conta aree non nulle
    cursor.execute("SELECT COUNT(DISTINCT area) FROM tma_materiali_archeologici WHERE area IS NOT NULL AND area != ''")
    distinct_areas = cursor.fetchone()[0]
    print(f"   Aree distinte (non nulle): {distinct_areas}")
    
    # Mostra tutte le aree distinte
    cursor.execute("SELECT DISTINCT area FROM tma_materiali_archeologici WHERE area IS NOT NULL AND area != '' ORDER BY area")
    areas = cursor.fetchall()
    print(f"   Aree trovate:")
    for i, (area,) in enumerate(areas):
        print(f"     {i+1}. '{area}' (tipo: {type(area).__name__})")
    
    # Conta record per area
    print("\n   Record per area:")
    cursor.execute("""
        SELECT area, COUNT(*) as count 
        FROM tma_materiali_archeologici 
        WHERE area IS NOT NULL AND area != ''
        GROUP BY area
        ORDER BY count DESC
    """)
    area_counts = cursor.fetchall()
    for area, count in area_counts:
        print(f"     '{area}': {count} record")
    
    # 4. Analizza US table
    print("\n4. ANALISI AREE IN us_table:")
    
    # Controlla se esiste la tabella
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='us_table'")
    if cursor.fetchone():
        cursor.execute("SELECT COUNT(DISTINCT area) FROM us_table WHERE area IS NOT NULL AND area != ''")
        us_areas = cursor.fetchone()[0]
        print(f"   Aree distinte in US: {us_areas}")
        
        cursor.execute("SELECT DISTINCT area FROM us_table WHERE area IS NOT NULL AND area != '' ORDER BY area")
        areas = cursor.fetchall()
        print(f"   Aree trovate:")
        for i, (area,) in enumerate(areas):
            print(f"     {i+1}. '{area}'")
    else:
        print("   Tabella us_table non trovata!")
    
    # 5. Controlla il thesaurus
    print("\n5. ANALISI THESAURUS:")
    
    # Conta aree nel thesaurus per tipologia
    cursor.execute("""
        SELECT tipologia_sigla, nome_tabella, COUNT(*) as count
        FROM pyarchinit_thesaurus_sigle
        WHERE tipologia_sigla IN ('10.7', '2.43')
        GROUP BY tipologia_sigla, nome_tabella
        ORDER BY tipologia_sigla
    """)
    thesaurus_counts = cursor.fetchall()
    print("   Aree nel thesaurus:")
    for tipo, tabella, count in thesaurus_counts:
        print(f"     Tipo {tipo} - Tabella '{tabella}': {count} record")
    
    # Mostra alcune aree dal thesaurus
    cursor.execute("""
        SELECT sigla, tipologia_sigla, nome_tabella, descrizione
        FROM pyarchinit_thesaurus_sigle
        WHERE tipologia_sigla IN ('10.7', '2.43')
        ORDER BY tipologia_sigla, sigla
        LIMIT 10
    """)
    print("\n   Prime 10 aree nel thesaurus:")
    for sigla, tipo, tabella, desc in cursor.fetchall():
        desc_str = f" - {desc}" if desc else ""
        print(f"     {sigla} (tipo {tipo}, tabella '{tabella}'){desc_str}")
    
    conn.close()
    
except Exception as e:
    print(f"ERRORE: {str(e)}")
    print("\nVerifica che il path del database sia corretto.")
    print("Path utilizzato:", db_path)
    
    # Prova a cercare il database
    import glob
    print("\nCercando file .sqlite nella home directory...")
    home = os.path.expanduser("~")
    sqlite_files = glob.glob(os.path.join(home, "**/*.sqlite"), recursive=True)
    pyarchinit_dbs = [f for f in sqlite_files if "pyarchinit" in f.lower()]
    
    if pyarchinit_dbs:
        print("Database PyArchInit trovati:")
        for db in pyarchinit_dbs[:5]:  # Mostra max 5
            print(f"  - {db}")