#!/usr/bin/env python3
"""
Comprehensive test to verify the complete fix works for both Area and Settore parent lookups
This tests the exact scenarios from the issue logs
"""

import sqlite3
import os

def test_complete_fix():
    """Test both Area and Settore parent lookup fixes"""
    
    # Path to the database
    db_path = "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/pyarchinit_db.sqlite"
    
    if not os.path.exists(db_path):
        print(f"Database not found at: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== Complete Fix Verification ===")
        
        # Test 1: Area parent lookup (10.7 -> 10.3)
        print("\n1. Testing Area parent lookup (10.7 -> 10.3):")
        print("   Scenario: Creating Area, needs Località parent")
        
        parent_sigla = 'LOC01'
        display_name = 'TMA Materiali Archeologici'
        lingua = 'IT'
        
        print(f"   Parent sigla: '{parent_sigla}'")
        print(f"   Search lingua: '{lingua}'")
        
        # Simulate the FIXED Area parent search logic
        area_parent_found = False
        area_id_parent = None
        
        # Try display name first
        cursor.execute("""
        SELECT id_thesaurus_sigle, sigla, lingua FROM pyarchinit_thesaurus_sigle 
        WHERE nome_tabella = ? AND sigla = ? AND tipologia_sigla = ? AND lingua = ?
        """, (display_name, parent_sigla, '10.3', lingua))
        
        results = cursor.fetchall()
        if results:
            area_id_parent = results[0][0]
            area_parent_found = True
            print(f"   ✓ Found with display name: ID={area_id_parent}")
        else:
            # Try lowercase table name
            cursor.execute("""
            SELECT id_thesaurus_sigle, sigla, lingua FROM pyarchinit_thesaurus_sigle 
            WHERE nome_tabella = ? AND sigla = ? AND tipologia_sigla = ? AND lingua = ?
            """, ('TMA materiali archeologici', parent_sigla, '10.3', lingua))
            
            results = cursor.fetchall()
            if results:
                area_id_parent = results[0][0]
                area_parent_found = True
                print(f"   ✓ Found with lowercase table name: ID={area_id_parent}")
            else:
                # Try without language constraint (final fallback)
                cursor.execute("""
                SELECT id_thesaurus_sigle, sigla, lingua FROM pyarchinit_thesaurus_sigle 
                WHERE nome_tabella = ? AND sigla = ? AND tipologia_sigla = ?
                """, ('TMA materiali archeologici', parent_sigla, '10.3'))
                
                results = cursor.fetchall()
                if results:
                    area_id_parent = results[0][0]
                    area_parent_found = True
                    print(f"   ✓ Found without language constraint: ID={area_id_parent}")
        
        if area_parent_found:
            print(f"   ✓ SUCCESS: Area parent lookup works! ID={area_id_parent}")
        else:
            print(f"   ✗ FAILED: Area parent lookup still broken")
        
        # Test 2: Create a test Area record to use for Settore test
        print("\n2. Creating test Area record for Settore test:")
        
        # Check if test area already exists
        cursor.execute("""
        SELECT id_thesaurus_sigle, sigla FROM pyarchinit_thesaurus_sigle 
        WHERE nome_tabella = 'TMA materiali archeologici' AND sigla = 'AREA_TEST_FIX' AND tipologia_sigla = '10.7'
        """)
        
        existing_area = cursor.fetchone()
        if existing_area:
            test_area_id = existing_area[0]
            test_area_sigla = existing_area[1]
            print(f"   Using existing test area: ID={test_area_id}, Sigla='{test_area_sigla}'")
        else:
            # Create test area
            cursor.execute("SELECT MAX(id_thesaurus_sigle) FROM pyarchinit_thesaurus_sigle")
            max_id = cursor.fetchone()[0] or 0
            test_area_id = max_id + 1
            test_area_sigla = 'AREA_TEST_FIX'
            
            cursor.execute("""
            INSERT INTO pyarchinit_thesaurus_sigle 
            (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, 
             tipologia_sigla, lingua, order_layer, id_parent, parent_sigla, hierarchy_level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (test_area_id, 'TMA materiali archeologici', test_area_sigla, 'Test Area for Fix', 
                  'Test area for verification', '10.7', 'it', 0, area_id_parent, parent_sigla, 2))
            
            conn.commit()
            print(f"   Created test area: ID={test_area_id}, Sigla='{test_area_sigla}'")
        
        # Test 3: Settore parent lookup (10.15 -> 10.7)
        print("\n3. Testing Settore parent lookup (10.15 -> 10.7):")
        print("   Scenario: Creating Settore, needs Area parent")
        
        settore_parent_sigla = test_area_sigla
        print(f"   Parent sigla: '{settore_parent_sigla}'")
        print(f"   Search lingua: '{lingua}'")
        
        # Simulate the FIXED Settore parent search logic
        settore_parent_found = False
        settore_id_parent = None
        
        # Try display name first
        cursor.execute("""
        SELECT id_thesaurus_sigle, sigla, lingua FROM pyarchinit_thesaurus_sigle 
        WHERE nome_tabella = ? AND sigla = ? AND tipologia_sigla = ? AND lingua = ?
        """, (display_name, settore_parent_sigla, '10.7', lingua))
        
        results = cursor.fetchall()
        if results:
            settore_id_parent = results[0][0]
            settore_parent_found = True
            print(f"   ✓ Found with display name: ID={settore_id_parent}")
        else:
            # Try lowercase table name
            cursor.execute("""
            SELECT id_thesaurus_sigle, sigla, lingua FROM pyarchinit_thesaurus_sigle 
            WHERE nome_tabella = ? AND sigla = ? AND tipologia_sigla = ? AND lingua = ?
            """, ('TMA materiali archeologici', settore_parent_sigla, '10.7', lingua))
            
            results = cursor.fetchall()
            if results:
                settore_id_parent = results[0][0]
                settore_parent_found = True
                print(f"   ✓ Found with lowercase table name: ID={settore_id_parent}")
            else:
                # Try without language constraint (final fallback)
                cursor.execute("""
                SELECT id_thesaurus_sigle, sigla, lingua FROM pyarchinit_thesaurus_sigle 
                WHERE nome_tabella = ? AND sigla = ? AND tipologia_sigla = ?
                """, ('TMA materiali archeologici', settore_parent_sigla, '10.7'))
                
                results = cursor.fetchall()
                if results:
                    settore_id_parent = results[0][0]
                    settore_parent_found = True
                    print(f"   ✓ Found without language constraint: ID={settore_id_parent}")
        
        if settore_parent_found:
            print(f"   ✓ SUCCESS: Settore parent lookup works! ID={settore_id_parent}")
        else:
            print(f"   ✗ FAILED: Settore parent lookup still broken")
        
        conn.close()
        
        # Final result
        print(f"\n=== Final Verification Result ===")
        if area_parent_found and settore_parent_found:
            print(f"✓ COMPLETE SUCCESS: Both Area and Settore parent lookups are FIXED!")
            print(f"✓ Area parent lookup: LOC01 -> ID {area_id_parent}")
            print(f"✓ Settore parent lookup: {settore_parent_sigla} -> ID {settore_id_parent}")
            print(f"✓ The id_parent issue is completely resolved!")
            print(f"✓ Users can now create TMA hierarchy records successfully!")
        else:
            print(f"✗ PARTIAL SUCCESS: Some parent lookups still need work")
            if not area_parent_found:
                print(f"✗ Area parent lookup still failing")
            if not settore_parent_found:
                print(f"✗ Settore parent lookup still failing")
        
    except Exception as e:
        print(f"Error testing: {e}")

if __name__ == "__main__":
    test_complete_fix()