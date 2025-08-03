#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test finale del fix per le combobox ldct e aint
"""

import sys
import os

# Add the plugin directory to Python path
plugin_dir = os.path.dirname(os.path.abspath(__file__))
if plugin_dir not in sys.path:
    sys.path.insert(0, plugin_dir)

# Test del sistema dei language settings come nel codice Tma.py
def test_language_system():
    print("=== TEST LANGUAGE SYSTEM ===\n")
    
    # Simulazione del LANG dictionary da Tma.py
    LANG = {
        "it": ["it_IT", "it", "IT", "it-IT", "it_IT.UTF-8"],
        "en": ["en_EN", "en", "EN", "en-EN", "en_EN.UTF-8", "en_US", "en-US", "en_US.UTF-8"],
        "de": ["de_DE", "de", "DE", "de-DE", "de_DE.UTF-8"],
    }
    
    # Test diversi valori di locale
    test_locales = ["it_IT", "en_US", "de_DE", "it", "IT", "fr_FR"]
    
    for locale in test_locales:
        print(f"\nTest con locale = '{locale}':")
        
        # Simula il codice di Tma.py
        lang = ""
        for key, values in LANG.items():
            if values.__contains__(locale):
                lang = str(key)
        
        print(f"  Risultato: lang = '{lang}'")
        
        # Con il vecchio codice avrebbe aggiunto apici
        # lang_old = "'" + lang + "'"
        # print(f"  Vecchio codice: lang = {lang_old}")

def test_database_query():
    print("\n\n=== TEST DATABASE QUERY ===\n")
    
    import sqlite3
    
    # Database path
    db_path = "/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite"
    
    if not os.path.exists(db_path):
        print(f"Database non trovato in: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Simula la lingua ottenuta dal sistema
    lang = "it"  # Senza apici extra
    
    # Query per ldct (10.2)
    search_dict = {
        'lingua': lang,
        'nome_tabella': 'TMA materiali archeologici',
        'tipologia_sigla': '10.2'
    }
    
    print(f"Query ldct con search_dict = {search_dict}")
    
    query = """
        SELECT sigla, sigla_estesa
        FROM pyarchinit_thesaurus_sigle
        WHERE lingua = ? AND nome_tabella = ? AND tipologia_sigla = ?
        ORDER BY sigla_estesa
    """
    
    cursor.execute(query, (search_dict['lingua'], search_dict['nome_tabella'], search_dict['tipologia_sigla']))
    results = cursor.fetchall()
    
    print(f"Trovati {len(results)} valori per ldct:")
    for sigla, sigla_estesa in results:
        print(f"  - [{sigla}] {sigla_estesa}")
    
    # Query per aint (10.6)
    search_dict['tipologia_sigla'] = '10.6'
    
    print(f"\nQuery aint con search_dict = {search_dict}")
    
    cursor.execute(query, (search_dict['lingua'], search_dict['nome_tabella'], search_dict['tipologia_sigla']))
    results = cursor.fetchall()
    
    print(f"Trovati {len(results)} valori per aint:")
    for sigla, sigla_estesa in results:
        print(f"  - [{sigla}] {sigla_estesa}")
    
    conn.close()

if __name__ == "__main__":
    test_language_system()
    test_database_query()