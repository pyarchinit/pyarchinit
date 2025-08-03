#!/usr/bin/env python3
"""
Test script to verify the table name fixes are working correctly
"""

import sqlite3
import os

def test_table_name_fixes():
    """Test that the table name fixes are working correctly"""
    
    # Path to the database
    db_path = "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/pyarchinit_db.sqlite"
    
    if not os.path.exists(db_path):
        print(f"Database not found at: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== Testing Table Name Fixes ===")
        
        # Test 1: Verify final database state
        print("\n1. Verifying database table names:")
        cursor.execute("""
        SELECT DISTINCT nome_tabella, COUNT(*) as count
        FROM pyarchinit_thesaurus_sigle 
        WHERE UPPER(nome_tabella) LIKE '%TMA%'
        GROUP BY nome_tabella
        ORDER BY nome_tabella
        """)
        
        tma_tables = cursor.fetchall()
        print(f"Found {len(tma_tables)} TMA table names:")
        
        expected_tables = ['TMA Materiali Ripetibili', 'TMA materiali archeologici']
        found_tables = [name for name, count in tma_tables]
        
        for table_name, count in tma_tables:
            status = "✓" if table_name in expected_tables else "✗"
            print(f"  {status} '{table_name}' - {count} records")
        
        # Test 2: Test thesaurus queries for main TMA fields
        print(f"\n2. Testing main TMA field queries:")
        main_field_codes = ['10.1', '10.2', '10.4', '10.5', '10.6']
        
        for code in main_field_codes:
            cursor.execute("""
            SELECT COUNT(*) FROM pyarchinit_thesaurus_sigle 
            WHERE nome_tabella = 'TMA materiali archeologici' AND tipologia_sigla = ?
            """, (code,))
            
            count = cursor.fetchone()[0]
            status = "✓" if count > 0 else "✗"
            print(f"  {status} Code {code}: {count} records in 'TMA materiali archeologici'")
        
        # Test 3: Test thesaurus queries for materials fields
        print(f"\n3. Testing materials field queries:")
        materials_field_codes = ['10.10', '10.11', '10.12', '10.13', '10.4']
        
        for code in materials_field_codes:
            cursor.execute("""
            SELECT COUNT(*) FROM pyarchinit_thesaurus_sigle 
            WHERE nome_tabella = 'TMA Materiali Ripetibili' AND tipologia_sigla = ?
            """, (code,))
            
            count = cursor.fetchone()[0]
            status = "✓" if count > 0 else "✗"
            print(f"  {status} Code {code}: {count} records in 'TMA Materiali Ripetibili'")
        
        # Test 4: Check for any remaining inconsistencies
        print(f"\n4. Checking for remaining inconsistencies:")
        
        # Check for any records with old table names
        old_names = ['TMA Materiali Archeologici', 'tma_materiali_archeologici', 'tma_materiali_ripetibili']
        inconsistencies_found = False
        
        for old_name in old_names:
            cursor.execute("""
            SELECT COUNT(*) FROM pyarchinit_thesaurus_sigle 
            WHERE nome_tabella = ?
            """, (old_name,))
            
            count = cursor.fetchone()[0]
            if count > 0:
                print(f"  ⚠️  Found {count} records with old table name: '{old_name}'")
                inconsistencies_found = True
        
        if not inconsistencies_found:
            print("  ✓ No old table names found - all records updated correctly")
        
        # Test 5: Sample some actual thesaurus values
        print(f"\n5. Sample thesaurus values:")
        
        # Sample from main TMA table
        cursor.execute("""
        SELECT tipologia_sigla, sigla_estesa FROM pyarchinit_thesaurus_sigle 
        WHERE nome_tabella = 'TMA materiali archeologici' AND tipologia_sigla = '10.4'
        LIMIT 3
        """)
        
        main_samples = cursor.fetchall()
        print(f"  Main TMA (10.4 - Fascia Cronologica):")
        for code, value in main_samples:
            print(f"    - {value}")
        
        # Sample from materials table
        cursor.execute("""
        SELECT tipologia_sigla, sigla_estesa FROM pyarchinit_thesaurus_sigle 
        WHERE nome_tabella = 'TMA Materiali Ripetibili' AND tipologia_sigla = '10.10'
        LIMIT 3
        """)
        
        materials_samples = cursor.fetchall()
        print(f"  Materials (10.10 - Categoria):")
        for code, value in materials_samples:
            print(f"    - {value}")
        
        conn.close()
        
        # Final assessment
        print(f"\n=== Final Assessment ===")
        if len(tma_tables) == 2 and all(name in expected_tables for name, count in tma_tables):
            print("✓ SUCCESS: Table names are correctly standardized!")
            print("✓ Database now uses:")
            print("  - 'TMA materiali archeologici' for main TMA fields")
            print("  - 'TMA Materiali Ripetibili' for materials table fields")
            print("✓ Code should now work correctly with consistent table names")
        else:
            print("⚠️  WARNING: There may still be table name issues")
        
    except Exception as e:
        print(f"Error testing: {e}")

if __name__ == "__main__":
    test_table_name_fixes()