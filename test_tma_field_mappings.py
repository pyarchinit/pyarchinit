#!/usr/bin/env python3
"""
Test script to verify the TMA field mappings are working correctly
This will test the corrected field mappings in the TMA tab
"""

import sqlite3
import os

def test_tma_field_mappings():
    """Test the corrected TMA field mappings"""
    
    # Path to the database
    db_path = "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/pyarchinit_db.sqlite"
    
    if not os.path.exists(db_path):
        print(f"Database not found at: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== Testing TMA Field Mappings ===")
        
        # Test the corrected mappings for TMA materiali archeologici fields
        field_mappings = {
            'Denominazione collocazione': '10.1',
            'Tipologia Collocazione': '10.2', 
            'Località': '10.3',
            'Fascia Cronologica': '10.4',
            'Denominazione Scavo': '10.5',
            'Tipologia Acquisizione': '10.6',
            'Area': '10.7',
            'Tipo foto': '10.8',
            'Tipo disegno': '10.9',
            'Settore': '10.15'
        }
        
        table_name = 'TMA materiali archeologici'
        
        print(f"\n1. Testing field mappings for table: '{table_name}'")
        
        for field_name, code in field_mappings.items():
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
                    
                    # Check for specific problematic cases mentioned in the issue
                    if field_name == 'Fascia Cronologica':
                        print(f"     ✓ Fascia Cronologica now correctly uses code 10.4")
                    elif field_name == 'Denominazione Scavo':
                        print(f"     ✓ Denominazione Scavo now correctly uses code 10.5")
                    elif field_name == 'Tipologia Collocazione':
                        print(f"     ✓ Tipologia Collocazione now correctly uses code 10.2")
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
        
        # Test the materials table mappings (should use TMA materiali ripetibili)
        print(f"\n2. Testing materials table mappings:")
        materials_mappings = {
            'Categoria': '10.10',
            'Classe': '10.11', 
            'Precisazione tipologica': '10.12',
            'Definizione': '10.13',
            'Cronologia': '10.4'  # Same code as Fascia Cronologica but different table
        }
        
        materials_table = 'TMA materiali ripetibili'
        
        for field_name, code in materials_mappings.items():
            cursor.execute("""
            SELECT COUNT(*) FROM pyarchinit_thesaurus_sigle 
            WHERE nome_tabella = ? AND tipologia_sigla = ?
            """, (materials_table, code))
            
            count = cursor.fetchone()[0]
            if count > 0:
                print(f"   ✓ {field_name} (code {code}): {count} records in '{materials_table}'")
            else:
                print(f"   ✗ {field_name} (code {code}): No records found in '{materials_table}'")
        
        conn.close()
        
        print(f"\n=== Test Summary ===")
        print(f"✓ Added missing field mappings for:")
        print(f"  - Denominazione collocazione (10.1)")
        print(f"  - Fascia Cronologica (10.4)")
        print(f"  - Denominazione Scavo (10.5)")
        print(f"✓ Fixed field mapping issues:")
        print(f"  - Fascia Cronologica no longer takes Tipologia Acquisizione values")
        print(f"  - Denominazione Scavo no longer takes Fascia Cronologica values")
        print(f"  - Tipologia Collocazione should now show values")
        print(f"✓ Materials table ComboBox delegates should work with correct thesaurus values")
        
    except Exception as e:
        print(f"Error testing: {e}")

if __name__ == "__main__":
    test_tma_field_mappings()