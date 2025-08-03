#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Debug script per verificare i valori del thesaurus per le combobox TMA
"""

import sqlite3
import os

def debug_thesaurus_values():
    # Database path
    db_path = "/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite"
    
    if not os.path.exists(db_path):
        print(f"Database non trovato in: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"=== DEBUG THESAURUS VALUES FOR TMA ===")
    print(f"Database: {db_path}")
    print()
    
    # Mapping secondo il nuovo schema
    mappings = {
        'TMA materiali archeologici': {
            '10.1': 'Denominazione collocazione (ldcn)',
            '10.2': 'Tipologia Collocazione (ldct)', 
            '10.3': 'Località',
            '10.4': 'Fascia Cronologica (dtzg)',
            '10.5': 'Denominazione Scavo (scan)',
            '10.6': 'Tipologia Acquisizione (aint)',
            '10.7': 'Area',
            '10.8': 'Tipo foto (ftap)',
            '10.9': 'Tipo disegno (drat)',
            '10.15': 'Settore',
        },
        'TMA materiali ripetibili': {
            '10.10': 'Categoria',
            '10.11': 'Classe',
            '10.12': 'Precisazione tipologica',
            '10.13': 'Definizione',
            '10.4': 'Cronologia'
        }
    }
    
    for table_name, codes in mappings.items():
        print(f"\n{'='*60}")
        print(f"TABELLA: {table_name}")
        print(f"{'='*60}")
        
        for code, description in codes.items():
            print(f"\n{description} ({code}):")
            print("-" * 40)
            
            # Query per ottenere i valori
            cursor.execute("""
                SELECT sigla, sigla_estesa, lingua
                FROM pyarchinit_thesaurus_sigle
                WHERE nome_tabella = ? AND tipologia_sigla = ?
                ORDER BY sigla_estesa
            """, (table_name, code))
            
            results = cursor.fetchall()
            
            if results:
                print(f"Trovati {len(results)} valori:")
                for sigla, sigla_estesa, lingua in results[:10]:  # Mostra solo i primi 10
                    print(f"  - [{sigla}] {sigla_estesa} ({lingua})")
                if len(results) > 10:
                    print(f"  ... e altri {len(results) - 10} valori")
            else:
                print("  ⚠️  NESSUN VALORE TROVATO!")
                
                # Verifica se esistono con varianti del nome tabella
                cursor.execute("""
                    SELECT DISTINCT nome_tabella
                    FROM pyarchinit_thesaurus_sigle
                    WHERE nome_tabella LIKE '%TMA%' AND tipologia_sigla = ?
                """, (code,))
                
                alt_tables = cursor.fetchall()
                if alt_tables:
                    print(f"  ℹ️  Trovati valori in tabelle alternative:")
                    for alt_table in alt_tables:
                        print(f"     - {alt_table[0]}")
    
    # Verifica quali combobox non funzionano
    print("\n\n" + "="*60)
    print("RIEPILOGO PROBLEMI:")
    print("="*60)
    
    problems = []
    for table_name, codes in mappings.items():
        for code, description in codes.items():
            cursor.execute("""
                SELECT COUNT(*)
                FROM pyarchinit_thesaurus_sigle
                WHERE nome_tabella = ? AND tipologia_sigla = ?
            """, (table_name, code))
            
            count = cursor.fetchone()[0]
            if count == 0:
                problems.append(f"❌ {description} ({code}) in {table_name}: NESSUN VALORE")
    
    if problems:
        print("\nCombobox che non funzioneranno:")
        for problem in problems:
            print(f"  {problem}")
    else:
        print("\n✅ Tutti i thesaurus hanno valori!")
    
    conn.close()

if __name__ == "__main__":
    debug_thesaurus_values()