#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per verificare e correggere i codici tipologia in TMA
"""

import sqlite3
import os
import sys

def verify_tipologia_codes():
    """Verifica i codici tipologia attualmente nel database."""
    
    # Database path
    db_path = os.path.expanduser("~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/pyarchinit_db.sqlite")
    
    if not os.path.exists(db_path):
        print(f"Database non trovato in: {db_path}")
        return False
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=== Verifica Codici Tipologia nel Database ===\n")
    
    # Query tutti i codici tipologia per TMA
    cursor.execute("""
        SELECT tipologia_sigla, 
               COUNT(*) as count,
               GROUP_CONCAT(sigla || ' (' || sigla_estesa || ')', ' | ') as esempi
        FROM pyarchinit_thesaurus_sigle
        WHERE nome_tabella = 'TMA materiali archeologici'
        GROUP BY tipologia_sigla
        ORDER BY tipologia_sigla
    """)
    
    results = cursor.fetchall()
    
    print("Codici tipologia attualmente nel database:")
    print("-" * 80)
    
    # Mapping dei campi TMA alle tipologie
    tma_field_mapping = {
        '10.1': 'ldcn - Denominazione collocazione',
        '10.2': 'ldct - Tipologia collocazione', 
        '10.3': 'Località',
        '10.4': 'scan - Nome scavo',
        '10.5': 'macc - Categoria materiali',
        '10.6': 'dtzg - Fascia cronologica / Cronologia',
        '10.7': 'Area',
        '10.8': 'macl - Classe materiali',
        '10.9': 'macp - Prec. tipologica materiali',
        '10.10': 'macd - Definizione materiali',
        '10.11': 'Cronologia specifica materiali',
        '10.12': 'ftap/drat - Tipo foto/disegno',
        '10.15': 'Settore'
    }
    
    for tipo, count, esempi in results:
        desc = tma_field_mapping.get(tipo, "SCONOSCIUTO")
        print(f"{tipo} - {desc}")
        print(f"   Count: {count}")
        print(f"   Esempi: {esempi[:100]}...")
        print()
    
    # Verifica i campi utilizzati in TMA.py
    print("\n=== Mappatura corretta per TMA.py ===")
    print("-" * 80)
    
    correct_mapping = {
        # Main TMA fields
        'ldcn': ('10.1', 'Denominazione collocazione'),
        'ldct': ('10.2', 'Tipologia collocazione'),
        'località': ('10.3', 'Località'),
        'scan': ('10.4', 'Nome scavo'),
        'area': ('10.7', 'Area'),
        'settore': ('10.15', 'Settore'),
        'dtzg': ('10.6', 'Fascia cronologica'),
        'aint': ('10.5', 'Tipo acquisizione/Altro'),  # Da verificare
        
        # Material table fields
        'categoria': ('10.5', 'Categoria materiali'),
        'classe': ('10.8', 'Classe materiali'),
        'tipologia': ('10.9', 'Prec. tipologica'),
        'definizione': ('10.10', 'Definizione'),
        'cronologia_mac': ('10.6', 'Cronologia'),  # Usa lo stesso di dtzg
        
        # Photo/Drawing fields
        'ftap': ('10.12', 'Tipo foto'),
        'drat': ('10.12', 'Tipo disegno')  # Stesso codice per foto e disegno
    }
    
    print("Mappatura da usare in TMA.py:")
    for field, (code, desc) in correct_mapping.items():
        cursor.execute("""
            SELECT COUNT(*) 
            FROM pyarchinit_thesaurus_sigle
            WHERE nome_tabella = 'TMA materiali archeologici'
            AND tipologia_sigla = ?
        """, (code,))
        count = cursor.fetchone()[0]
        status = "✅" if count > 0 else "❌"
        print(f"{status} {field} -> {code} ({desc}) - {count} valori")
    
    # Genera il codice corretto per TMA.py
    print("\n=== Codice corretto per TMA.py ===")
    print("-" * 80)
    
    print("""
# In charge_list_from_thesaurus():
# 10.1 - Denominazione collocazione
search_dict_ldcn = {
    'nome_tabella': 'TMA materiali archeologici',
    'tipologia_sigla': "'10.1'"  # Denominazione collocazione
}

# In load_thesaurus_values():
thesaurus_map = {
    'materiale': '10.1',      # Non usato nella tabella
    'categoria': '10.5',      # Categoria (macc)
    'classe': '10.8',         # Classe (macl)
    'tipologia': '10.9',      # Prec. tipologica (macp)
    'definizione': '10.10',   # Definizione (macd)
    'cronologia_mac': '10.6'  # Cronologia
}

# Per i combobox principali:
# comboBox_ldct -> search with tipologia_sigla '10.2'
# comboBox_aint -> search with tipologia_sigla '10.5' (o altro?)
# comboBox_ftap -> search with tipologia_sigla '10.12'
# comboBox_drat -> search with tipologia_sigla '10.12'
""")
    
    conn.close()
    return True

if __name__ == "__main__":
    verify_tipologia_codes()