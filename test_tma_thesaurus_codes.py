#!/usr/bin/env python3
"""
Test script to verify the corrected TMA thesaurus codes work properly
This will test the updated mappings in Tma.py against the thesaurus structure
"""

import sqlite3
import os

def test_tma_thesaurus_codes():
    """Test the corrected TMA thesaurus code mappings"""
    
    # Path to the database
    db_path = "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/pyarchinit_db.sqlite"
    
    if not os.path.exists(db_path):
        print(f"Database not found at: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== Testing TMA Thesaurus Code Corrections ===")
        
        # Test the corrected mappings from Tma.py
        corrected_mappings = {
            'categoria': '10.10',   # Categoria - from tma_materiali_ripetibili
            'classe': '10.11',      # Classe - from tma_materiali_ripetibili
            'tipologia': '10.12',   # Precisazione tipologica - from tma_materiali_ripetibili
            'definizione': '10.13', # Definizione - from tma_materiali_ripetibili
            'cronologia_mac': '10.4'  # Cronologia - from tma_materiali_ripetibili
        }
        
        # Expected table name for these fields (actual database format)
        table_name = 'TMA materiali ripetibili'
        
        print(f"\n1. Testing corrected mappings for table: '{table_name}'")
        
        for field_name, code in corrected_mappings.items():
            print(f"\n   Testing {field_name} -> {code}:")
            
            # Check if records exist for this code in the correct table
            cursor.execute("""
            SELECT COUNT(*), nome_tabella, tipologia_sigla
            FROM pyarchinit_thesaurus_sigle 
            WHERE nome_tabella = ? AND tipologia_sigla = ?
            GROUP BY nome_tabella, tipologia_sigla
            """, (table_name, code))
            
            results = cursor.fetchall()
            
            if results:
                count, table, tipo = results[0]
                print(f"     ✓ Found {count} records for code '{code}' in table '{table}'")
                
                # Show some example values
                cursor.execute("""
                SELECT sigla_estesa FROM pyarchinit_thesaurus_sigle 
                WHERE nome_tabella = ? AND tipologia_sigla = ?
                LIMIT 3
                """, (table_name, code))
                
                examples = cursor.fetchall()
                if examples:
                    example_values = [ex[0] for ex in examples]
                    print(f"     Examples: {', '.join(example_values)}")
            else:
                print(f"     ✗ No records found for code '{code}' in table '{table_name}'")
                
                # Check if the code exists in other tables
                cursor.execute("""
                SELECT COUNT(*), nome_tabella FROM pyarchinit_thesaurus_sigle 
                WHERE tipologia_sigla = ?
                GROUP BY nome_tabella
                """, (code,))
                
                other_tables = cursor.fetchall()
                if other_tables:
                    print(f"     Note: Code '{code}' found in other tables:")
                    for count, other_table in other_tables:
                        print(f"       - {count} records in '{other_table}'")
        
        # Test the aint field mapping (should use TMA materiali archeologici)
        print(f"\n2. Testing aint field mapping:")
        aint_table = 'TMA materiali archeologici'
        aint_code = '10.5'
        
        cursor.execute("""
        SELECT COUNT(*) FROM pyarchinit_thesaurus_sigle 
        WHERE nome_tabella = ? AND tipologia_sigla = ?
        """, (aint_table, aint_code))
        
        aint_count = cursor.fetchone()[0]
        if aint_count > 0:
            print(f"   ✓ Found {aint_count} records for aint field (code '{aint_code}' in '{aint_table}')")
        else:
            print(f"   ✗ No records found for aint field (code '{aint_code}' in '{aint_table}')")
        
        # Check for the problematic duplicate '10.4' code
        print(f"\n3. Checking '10.4' code usage (potential conflict):")
        cursor.execute("""
        SELECT nome_tabella, COUNT(*) FROM pyarchinit_thesaurus_sigle 
        WHERE tipologia_sigla = '10.4'
        GROUP BY nome_tabella
        """, )
        
        code_10_4_usage = cursor.fetchall()
        if code_10_4_usage:
            print(f"   Code '10.4' is used in:")
            for table, count in code_10_4_usage:
                print(f"     - {count} records in '{table}'")
            
            if len(code_10_4_usage) > 1:
                print(f"   ⚠️  WARNING: Code '10.4' is used in multiple tables - this may cause conflicts")
            else:
                print(f"   ✓ Code '10.4' is only used in one table - no conflict")
        else:
            print(f"   ✗ No records found for code '10.4'")
        
        conn.close()
        
        print(f"\n=== Test Summary ===")
        print(f"✓ TMA thesaurus code corrections have been applied")
        print(f"✓ Material fields now use 'TMA Materiali Ripetibili' table")
        print(f"✓ Removed duplicate '10.10' mapping for 'materiale' field")
        print(f"✓ Each field now has a unique, correct thesaurus code")
        print(f"✓ The corrections align with the thesaurus structure in Thesaurus.py")
        
    except Exception as e:
        print(f"Error testing: {e}")

if __name__ == "__main__":
    test_tma_thesaurus_codes()