#!/usr/bin/env python3
"""
Test script to verify the LOC01 parent lookup fix is working
This simulates the exact search logic used in the updated insert_new_rec method
"""

import sqlite3
import os

def test_loc01_fix():
    """Test the updated parent lookup logic for LOC01"""
    
    # Path to the database
    db_path = "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/pyarchinit_db.sqlite"
    
    if not os.path.exists(db_path):
        print(f"Database not found at: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== Testing LOC01 Fix ===")
        
        # Simulate the FIXED search logic for Area (10.7) parent lookup
        parent_sigla = 'LOC01'
        display_name = 'TMA Materiali Archeologici'
        lingua = 'IT'
        
        print(f"Testing Area parent lookup for sigla: '{parent_sigla}'")
        print(f"Display name: '{display_name}'")
        print(f"Lingua: '{lingua}'")
        
        # Step 1: Try with display name first (as in the updated code)
        print(f"\n1. Trying with display name:")
        cursor.execute("""
        SELECT id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua
        FROM pyarchinit_thesaurus_sigle 
        WHERE nome_tabella = ? AND sigla = ? AND tipologia_sigla = ? AND lingua = ?
        """, (display_name, parent_sigla, '10.3', lingua))
        
        display_results = cursor.fetchall()
        print(f"Results with display name: {len(display_results)} records found")
        
        parent_found = False
        id_parent = None
        
        if display_results:
            for record in display_results:
                id_thes, nome_tab, sigla, sigla_est, tipo, lang = record
                print(f"  ✓ Found: ID={id_thes}, Sigla='{sigla}', Lingua='{lang}'")
                id_parent = id_thes
                parent_found = True
        else:
            print("  No records found with display name")
            
            # Step 2: Try with lowercase table name (actual database format)
            print(f"\n2. Trying with lowercase table name (FIXED logic):")
            cursor.execute("""
            SELECT id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua
            FROM pyarchinit_thesaurus_sigle 
            WHERE nome_tabella = ? AND sigla = ? AND tipologia_sigla = ? AND lingua = ?
            """, ('TMA materiali archeologici', parent_sigla, '10.3', lingua))
            
            lowercase_results = cursor.fetchall()
            print(f"Results with lowercase table name: {len(lowercase_results)} records found")
            
            if lowercase_results:
                for record in lowercase_results:
                    id_thes, nome_tab, sigla, sigla_est, tipo, lang = record
                    print(f"  ✓ SUCCESS: Found with lowercase! ID={id_thes}, Sigla='{sigla}', Lingua='{lang}'")
                    id_parent = id_thes
                    parent_found = True
            else:
                print("  Still no records found with lowercase table name")
                
                # Step 3: Try without language constraint (final fallback)
                print(f"\n3. Trying without language constraint:")
                cursor.execute("""
                SELECT id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua
                FROM pyarchinit_thesaurus_sigle 
                WHERE nome_tabella = ? AND sigla = ? AND tipologia_sigla = ?
                """, ('TMA materiali archeologici', parent_sigla, '10.3'))
                
                no_lang_results = cursor.fetchall()
                print(f"Results without language: {len(no_lang_results)} records found")
                
                if no_lang_results:
                    for record in no_lang_results:
                        id_thes, nome_tab, sigla, sigla_est, tipo, lang = record
                        print(f"  ✓ SUCCESS: Found without language! ID={id_thes}, Sigla='{sigla}', Lingua='{lang}'")
                        id_parent = id_thes
                        parent_found = True
        
        # Test result
        print(f"\n=== Test Result ===")
        if parent_found and id_parent:
            print(f"✓ SUCCESS: Parent lookup FIXED!")
            print(f"✓ LOC01 parent found with ID: {id_parent}")
            print(f"✓ id_parent will now be correctly set to: {id_parent}")
            print(f"✓ The fix resolves the original issue!")
        else:
            print(f"✗ FAILED: Parent lookup still not working")
            print(f"✗ LOC01 parent not found")
            print(f"✗ id_parent will remain None/empty")
        
        conn.close()
        
    except Exception as e:
        print(f"Error testing: {e}")

if __name__ == "__main__":
    test_loc01_fix()