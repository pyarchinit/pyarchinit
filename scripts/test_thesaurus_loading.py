#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per testare il caricamento del thesaurus
"""

import sys
import os
sys.path.insert(0, '/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit')

from modules.db.pyarchinit_db_manager import Pyarchinit_db_management
from modules.db.pyarchinit_conn_strings import Connection

def test_thesaurus():
    """Testa il caricamento del thesaurus."""
    print("Test caricamento thesaurus")
    print("=" * 60)
    
    # Connessione al database
    conn = Connection()
    conn_str = conn.conn_str()
    
    try:
        db_manager = Pyarchinit_db_management(conn_str)
        db_manager.connection()
        
        # Test 1: Query semplice senza quotes
        print("\nTest 1: Query semplice")
        search_dict = {
            'lingua': 'IT',
            'nome_tabella': 'tma_materiali_archeologici',
            'tipologia_sigla': '10.1'
        }
        
        records = db_manager.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        print(f"Records trovati (senza quotes): {len(records)}")
        if records:
            for r in records[:3]:
                print(f"  - {r.sigla_estesa}")
        
        # Test 2: Query con quotes (vecchio metodo)
        print("\nTest 2: Query con quotes")
        search_dict_quoted = {
            'lingua': 'IT',
            'nome_tabella': "'tma_materiali_archeologici'",
            'tipologia_sigla': "'10.1'"
        }
        
        records_quoted = db_manager.query_bool(search_dict_quoted, 'PYARCHINIT_THESAURUS_SIGLE')
        print(f"Records trovati (con quotes): {len(records_quoted)}")
        
        # Test 3: Verifica tutti i tipi
        print("\nTest 3: Verifica tutti i tipi di materiale")
        for code in ['10.1', '10.2', '10.3', '10.4', '10.5', '10.6', '10.7', '10.8', '10.9', '10.10', '10.11']:
            search_dict = {
                'lingua': 'IT',
                'nome_tabella': 'tma_materiali_archeologici',
                'tipologia_sigla': code
            }
            records = db_manager.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
            print(f"  Codice {code}: {len(records)} records")
        
    except Exception as e:
        print(f"Errore: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_thesaurus()