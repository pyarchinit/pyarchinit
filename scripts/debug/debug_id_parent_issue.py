#!/usr/bin/env python3
"""
Debug script to test the exact parent lookup logic used in insert_new_rec
This will help identify why id_parent is not being set despite parent_sigla being found
"""

import sqlite3
import os

def debug_parent_lookup():
    """Debug the parent lookup logic exactly as used in insert_new_rec"""
    
    # Path to the database
    db_path = "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/pyarchinit_db.sqlite"
    
    if not os.path.exists(db_path):
        print(f"Database not found at: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== Debugging Parent Lookup Logic ===")
        
        # First, check what TMA records exist
        print("\n1. Checking existing TMA records:")
        cursor.execute("""
        SELECT id_thesaurus_sigle, sigla, sigla_estesa, tipologia_sigla, nome_tabella, lingua
        FROM pyarchinit_thesaurus_sigle 
        WHERE nome_tabella = 'TMA Materiali Archeologici'
        AND tipologia_sigla IN ('10.3', '10.7', '10.15')
        ORDER BY tipologia_sigla, sigla
        """)
        
        records = cursor.fetchall()
        print(f"Found {len(records)} TMA hierarchy records:")
        
        localita_records = []
        for record in records:
            id_thes, sigla, sigla_estesa, tipologia, nome_tabella, lingua = record
            print(f"  ID: {id_thes}, Sigla: {sigla}, Tipo: {tipologia}, Tabella: '{nome_tabella}', Lingua: '{lingua}'")
            if tipologia == '10.3':  # Località
                localita_records.append(record)
        
        if not localita_records:
            print("\nNo località records found - cannot test parent lookup")
            return
        
        # Test the exact search logic used in insert_new_rec for Area (10.7)
        print(f"\n2. Testing Area parent lookup logic:")
        test_localita = localita_records[0]
        parent_sigla = test_localita[1]  # sigla
        display_name = "TMA Materiali Archeologici"
        lingua = "it"
        
        print(f"Testing with parent_sigla: '{parent_sigla}'")
        print(f"Display name: '{display_name}'")
        print(f"Lingua: '{lingua}'")
        
        # First search - with language constraint (as in the code)
        print(f"\n2a. Search with language constraint:")
        search_query = """
        SELECT id_thesaurus_sigle, sigla, nome_tabella, tipologia_sigla, lingua
        FROM pyarchinit_thesaurus_sigle 
        WHERE nome_tabella = ? AND sigla = ? AND tipologia_sigla = ? AND lingua = ?
        """
        
        cursor.execute(search_query, (display_name, parent_sigla, '10.3', lingua))
        results_with_lang = cursor.fetchall()
        
        print(f"Query: {search_query}")
        print(f"Params: ('{display_name}', '{parent_sigla}', '10.3', '{lingua}')")
        print(f"Results: {len(results_with_lang)} records found")
        
        if results_with_lang:
            for result in results_with_lang:
                id_thes, sigla, nome_tab, tipo, lang = result
                print(f"  Found: ID={id_thes}, Sigla='{sigla}', Tabella='{nome_tab}', Tipo='{tipo}', Lingua='{lang}'")
                print(f"  -> id_parent would be set to: {id_thes}")
        else:
            print("  No records found with language constraint")
            
            # Second search - without language constraint (fallback)
            print(f"\n2b. Fallback search without language constraint:")
            search_query_no_lang = """
            SELECT id_thesaurus_sigle, sigla, nome_tabella, tipologia_sigla, lingua
            FROM pyarchinit_thesaurus_sigle 
            WHERE nome_tabella = ? AND sigla = ? AND tipologia_sigla = ?
            """
            
            cursor.execute(search_query_no_lang, (display_name, parent_sigla, '10.3'))
            results_no_lang = cursor.fetchall()
            
            print(f"Query: {search_query_no_lang}")
            print(f"Params: ('{display_name}', '{parent_sigla}', '10.3')")
            print(f"Results: {len(results_no_lang)} records found")
            
            if results_no_lang:
                for result in results_no_lang:
                    id_thes, sigla, nome_tab, tipo, lang = result
                    print(f"  Found: ID={id_thes}, Sigla='{sigla}', Tabella='{nome_tab}', Tipo='{tipo}', Lingua='{lang}'")
                    print(f"  -> id_parent would be set to: {id_thes}")
            else:
                print("  No records found even without language constraint")
        
        # Test what happens if we simulate the exact search dict format from the code
        print(f"\n3. Testing with exact search dict format from code:")
        
        # This simulates the search_dict format used in the actual code
        print("The code uses query_bool with search_dict containing quoted values:")
        print(f"search_dict = {{")
        print(f"    'nome_tabella': \"'{display_name}'\",")
        print(f"    'sigla': \"'{parent_sigla}'\",")
        print(f"    'tipologia_sigla': \"'10.3'\",")
        print(f"    'lingua': \"'{lingua}'\"")
        print(f"}}")
        
        # Let's see if the issue is with the quoted format
        cursor.execute("""
        SELECT id_thesaurus_sigle, sigla, nome_tabella, tipologia_sigla, lingua
        FROM pyarchinit_thesaurus_sigle 
        WHERE nome_tabella = ? AND sigla = ? AND tipologia_sigla = ? AND lingua = ?
        """, (f"'{display_name}'", f"'{parent_sigla}'", "'10.3'", f"'{lingua}'"))
        
        quoted_results = cursor.fetchall()
        print(f"Results with quoted format: {len(quoted_results)} records found")
        
        if quoted_results:
            for result in quoted_results:
                id_thes, sigla, nome_tab, tipo, lang = result
                print(f"  Found: ID={id_thes}, Sigla='{sigla}', Tabella='{nome_tab}', Tipo='{tipo}', Lingua='{lang}'")
        
        conn.close()
        
        print(f"\n=== Debug Complete ===")
        print("If no records were found in any search, the parent lookup is failing.")
        print("If records were found, then id_parent should be set correctly.")
        
    except Exception as e:
        print(f"Error debugging: {e}")

if __name__ == "__main__":
    debug_parent_lookup()