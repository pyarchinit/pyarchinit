#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script per verificare il mapping corretto dei nomi tabelle
"""

import sqlite3
import os

db_path = os.path.expanduser("~/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite")

# Mapping dal codice Thesaurus.py
TABLE_DISPLAY_MAPPING = {
    'Sito': 'site_table',
    'US': 'us_table',
    'Inventario Materiali': 'inventario_materiali_table',
    'Campioni': 'campioni_table',
    'Inventario Lapidei': 'inventario_lapidei_table',
    'Struttura': 'struttura_table',
    'Tomba': 'tomba_table',
    'Individui': 'individui_table',
    'Documentazione': 'documentazione_table',
    'TMA materiali archeologici': 'tma_materiali_archeologici',
}

# Codici area corretti dal database
AREA_CODES = {
    'US': '2.43',
    'Inventario Materiali': '3.11',
    'Tomba': '7.8',
    'Individui': '8.6',
    'TMA materiali archeologici': '10.7'
}

print("VERIFICA MAPPING THESAURUS")
print("=" * 80)

print("\n1. MAPPING ATTESO:")
print("Database Table Name -> Display Name -> Area Code")
for display, table in TABLE_DISPLAY_MAPPING.items():
    code = AREA_CODES.get(display, 'N/A')
    print(f"  {table:30s} -> {display:25s} -> {code}")

print("\n2. VERIFICA NEL DATABASE:")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Per ogni mapping, verifica cosa c'è nel DB
    for display_name, table_name in TABLE_DISPLAY_MAPPING.items():
        if display_name in AREA_CODES:
            expected_code = AREA_CODES[display_name]
            
            # Cerca con display name
            cursor.execute("""
                SELECT COUNT(*) 
                FROM pyarchinit_thesaurus_sigle
                WHERE nome_tabella = ?
                AND tipologia_sigla = ?
            """, (display_name, expected_code))
            
            count = cursor.fetchone()[0]
            
            print(f"\n'{display_name}' con codice {expected_code}:")
            print(f"  Record trovati: {count}")
            
            if count > 0:
                # Mostra alcuni esempi
                cursor.execute("""
                    SELECT sigla, lingua, descrizione
                    FROM pyarchinit_thesaurus_sigle
                    WHERE nome_tabella = ?
                    AND tipologia_sigla = ?
                    LIMIT 3
                """, (display_name, expected_code))
                
                examples = cursor.fetchall()
                print("  Esempi:")
                for sigla, lingua, desc in examples:
                    desc_str = f" - {desc}" if desc else ""
                    print(f"    {sigla} ({lingua}){desc_str}")
    
    # 3. Verifica codici materiali per Inventario
    print("\n\n3. CODICI INVENTARIO MATERIALI:")
    inv_codes = {
        '3.1': 'TIPO REPERTO',
        '3.2': 'CLASSE MATERIALE', 
        '3.3': 'DEFINIZIONE REPERTO',
        '3.12': 'TIPOLOGIA'
    }
    
    for code, desc in inv_codes.items():
        cursor.execute("""
            SELECT COUNT(*)
            FROM pyarchinit_thesaurus_sigle
            WHERE nome_tabella = 'Inventario Materiali'
            AND tipologia_sigla = ?
        """, (code,))
        
        count = cursor.fetchone()[0]
        print(f"\n  {code} ({desc}): {count} record")
        
        if count > 0:
            cursor.execute("""
                SELECT sigla
                FROM pyarchinit_thesaurus_sigle
                WHERE nome_tabella = 'Inventario Materiali'
                AND tipologia_sigla = ?
                LIMIT 5
            """, (code,))
            
            examples = cursor.fetchall()
            print(f"    Esempi: {', '.join([ex[0] for ex in examples])}")
    
    conn.close()
    
except Exception as e:
    print(f"ERRORE: {str(e)}")

print("\n\nCONCLUSIONE:")
print("Il thesaurus usa i nomi DISPLAY (es. 'Inventario Materiali')")
print("Il codice PyArchInit usa i nomi DATABASE (es. 'inventario_materiali_table')")
print("La sincronizzazione deve convertire tra i due formati!")