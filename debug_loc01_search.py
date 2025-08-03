#!/usr/bin/env python3
"""
Debug script to investigate why LOC01 parent search is failing
Based on the logs showing "Found 0 parent records" for LOC01
"""

import sqlite3
import os

def debug_loc01_search():
    """Debug why LOC01 parent search is failing"""
    
    # Path to the database
    db_path = "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/pyarchinit_db.sqlite"
    
    if not os.path.exists(db_path):
        print(f"Database not found at: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== Debugging LOC01 Search Issue ===")
        
        # First, check if LOC01 exists at all
        print("\n1. Checking if LOC01 exists anywhere in the database:")
        cursor.execute("""
        SELECT id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua
        FROM pyarchinit_thesaurus_sigle 
        WHERE sigla LIKE '%LOC01%' OR sigla LIKE '%loc01%'
        """)
        
        loc01_records = cursor.fetchall()
        print(f"Found {len(loc01_records)} records containing 'LOC01':")
        
        for record in loc01_records:
            id_thes, nome_tab, sigla, sigla_est, tipo, lingua = record
            print(f"  ID: {id_thes}, Tabella: '{nome_tab}', Sigla: '{sigla}', Tipo: '{tipo}', Lingua: '{lingua}'")
        
        # Check all TMA località records (10.3)
        print("\n2. Checking all TMA località records (10.3):")
        cursor.execute("""
        SELECT id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua
        FROM pyarchinit_thesaurus_sigle 
        WHERE nome_tabella = 'TMA Materiali Archeologici' AND tipologia_sigla = '10.3'
        ORDER BY sigla
        """)
        
        localita_records = cursor.fetchall()
        print(f"Found {len(localita_records)} località records:")
        
        for record in localita_records:
            id_thes, nome_tab, sigla, sigla_est, tipo, lingua = record
            print(f"  ID: {id_thes}, Sigla: '{sigla}', Estesa: '{sigla_est}', Lingua: '{lingua}'")
        
        # Test the exact search that's failing according to the logs
        print("\n3. Testing the exact search from the logs:")
        search_params = {
            'nome_tabella': 'TMA Materiali Archeologici',
            'sigla': 'LOC01',
            'tipologia_sigla': '10.3',
            'lingua': 'IT'
        }
        
        print(f"Search parameters: {search_params}")
        
        cursor.execute("""
        SELECT id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua
        FROM pyarchinit_thesaurus_sigle 
        WHERE nome_tabella = ? AND sigla = ? AND tipologia_sigla = ? AND lingua = ?
        """, (search_params['nome_tabella'], search_params['sigla'], search_params['tipologia_sigla'], search_params['lingua']))
        
        exact_results = cursor.fetchall()
        print(f"Exact search results: {len(exact_results)} records found")
        
        if exact_results:
            for record in exact_results:
                id_thes, nome_tab, sigla, sigla_est, tipo, lingua = record
                print(f"  Found: ID={id_thes}, Sigla='{sigla}', Lingua='{lingua}'")
        else:
            print("  No records found with exact search")
            
            # Try variations
            print("\n4. Trying search variations:")
            
            # Try with lowercase lingua
            print("4a. Trying with lowercase lingua 'it':")
            cursor.execute("""
            SELECT id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua
            FROM pyarchinit_thesaurus_sigle 
            WHERE nome_tabella = ? AND sigla = ? AND tipologia_sigla = ? AND lingua = ?
            """, (search_params['nome_tabella'], search_params['sigla'], search_params['tipologia_sigla'], 'it'))
            
            lowercase_results = cursor.fetchall()
            print(f"  Results with 'it': {len(lowercase_results)} records")
            
            # Try without language constraint
            print("4b. Trying without language constraint:")
            cursor.execute("""
            SELECT id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua
            FROM pyarchinit_thesaurus_sigle 
            WHERE nome_tabella = ? AND sigla = ? AND tipologia_sigla = ?
            """, (search_params['nome_tabella'], search_params['sigla'], search_params['tipologia_sigla']))
            
            no_lang_results = cursor.fetchall()
            print(f"  Results without language: {len(no_lang_results)} records")
            
            if no_lang_results:
                for record in no_lang_results:
                    id_thes, nome_tab, sigla, sigla_est, tipo, lingua = record
                    print(f"    Found: ID={id_thes}, Sigla='{sigla}', Lingua='{lingua}'")
            
            # Try case-insensitive search
            print("4c. Trying case-insensitive search:")
            cursor.execute("""
            SELECT id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua
            FROM pyarchinit_thesaurus_sigle 
            WHERE UPPER(nome_tabella) = UPPER(?) AND UPPER(sigla) = UPPER(?) AND tipologia_sigla = ?
            """, (search_params['nome_tabella'], search_params['sigla'], search_params['tipologia_sigla']))
            
            case_insensitive_results = cursor.fetchall()
            print(f"  Results with case-insensitive: {len(case_insensitive_results)} records")
            
            if case_insensitive_results:
                for record in case_insensitive_results:
                    id_thes, nome_tab, sigla, sigla_est, tipo, lingua = record
                    print(f"    Found: ID={id_thes}, Sigla='{sigla}', Lingua='{lingua}'")
        
        conn.close()
        
        print(f"\n=== Debug Complete ===")
        if not loc01_records:
            print("ISSUE: LOC01 record does not exist in the database!")
            print("Solution: Create the LOC01 località record first, or use an existing località sigla.")
        elif not exact_results:
            print("ISSUE: LOC01 exists but search criteria don't match exactly.")
            print("Check for case sensitivity, language mismatch, or other field differences.")
        
    except Exception as e:
        print(f"Error debugging: {e}")

if __name__ == "__main__":
    debug_loc01_search()