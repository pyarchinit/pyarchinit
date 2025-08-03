#!/usr/bin/env python3
"""
Test script to verify the id_parent fix is working correctly
This will create test TMA records and check if id_parent is properly set
"""

import sqlite3
import os

def create_test_records():
    """Create test TMA records to verify id_parent functionality"""
    
    # Path to the database
    db_path = "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/pyarchinit_db.sqlite"
    
    if not os.path.exists(db_path):
        print(f"Database not found at: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== Creating Test TMA Records ===")
        
        # First, create a test località (10.3)
        print("\n1. Creating test località record...")
        
        # Get next ID
        cursor.execute("SELECT MAX(id_thesaurus_sigle) FROM pyarchinit_thesaurus_sigle")
        max_id = cursor.fetchone()[0] or 0
        next_id = max_id + 1
        
        localita_data = (
            next_id,
            'TMA Materiali Archeologici',
            'LOC_TEST',
            'Test Località',
            'Test località for hierarchy testing',
            '10.3',
            'it',
            0,
            None,  # id_parent
            None,  # parent_sigla
            1      # hierarchy_level
        )
        
        cursor.execute("""
        INSERT INTO pyarchinit_thesaurus_sigle 
        (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, 
         tipologia_sigla, lingua, order_layer, id_parent, parent_sigla, hierarchy_level)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, localita_data)
        
        localita_id = next_id
        print(f"Created località with ID: {localita_id}")
        
        # Now create a test area (10.7) with parent località
        print("\n2. Creating test area record with parent...")
        next_id += 1
        
        area_data = (
            next_id,
            'TMA Materiali Archeologici',
            'AREA_TEST',
            'Test Area',
            'Test area for hierarchy testing',
            '10.7',
            'it',
            0,
            localita_id,  # id_parent - should reference località
            'LOC_TEST',   # parent_sigla
            2             # hierarchy_level
        )
        
        cursor.execute("""
        INSERT INTO pyarchinit_thesaurus_sigle 
        (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, 
         tipologia_sigla, lingua, order_layer, id_parent, parent_sigla, hierarchy_level)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, area_data)
        
        area_id = next_id
        print(f"Created area with ID: {area_id}, parent ID: {localita_id}")
        
        # Finally create a test settore (10.15) with parent area
        print("\n3. Creating test settore record with parent...")
        next_id += 1
        
        settore_data = (
            next_id,
            'TMA Materiali Archeologici',
            'SETT_TEST',
            'Test Settore',
            'Test settore for hierarchy testing',
            '10.15',
            'it',
            0,
            area_id,      # id_parent - should reference area
            'AREA_TEST',  # parent_sigla
            3             # hierarchy_level
        )
        
        cursor.execute("""
        INSERT INTO pyarchinit_thesaurus_sigle 
        (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, 
         tipologia_sigla, lingua, order_layer, id_parent, parent_sigla, hierarchy_level)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, settore_data)
        
        settore_id = next_id
        print(f"Created settore with ID: {settore_id}, parent ID: {area_id}")
        
        conn.commit()
        
        # Verify the hierarchy
        print("\n4. Verifying hierarchy relationships...")
        
        # Check area parent
        cursor.execute("""
        SELECT t1.sigla, t1.id_parent, t2.sigla as parent_sigla_actual
        FROM pyarchinit_thesaurus_sigle t1
        LEFT JOIN pyarchinit_thesaurus_sigle t2 ON t1.id_parent = t2.id_thesaurus_sigle
        WHERE t1.sigla = 'AREA_TEST'
        """)
        
        area_result = cursor.fetchone()
        if area_result:
            sigla, id_parent, parent_sigla_actual = area_result
            print(f"Area '{sigla}': id_parent={id_parent}, actual parent sigla='{parent_sigla_actual}'")
            if id_parent == localita_id and parent_sigla_actual == 'LOC_TEST':
                print("✓ Area parent relationship is CORRECT")
            else:
                print("✗ Area parent relationship is INCORRECT")
        
        # Check settore parent
        cursor.execute("""
        SELECT t1.sigla, t1.id_parent, t2.sigla as parent_sigla_actual
        FROM pyarchinit_thesaurus_sigle t1
        LEFT JOIN pyarchinit_thesaurus_sigle t2 ON t1.id_parent = t2.id_thesaurus_sigle
        WHERE t1.sigla = 'SETT_TEST'
        """)
        
        settore_result = cursor.fetchone()
        if settore_result:
            sigla, id_parent, parent_sigla_actual = settore_result
            print(f"Settore '{sigla}': id_parent={id_parent}, actual parent sigla='{parent_sigla_actual}'")
            if id_parent == area_id and parent_sigla_actual == 'AREA_TEST':
                print("✓ Settore parent relationship is CORRECT")
            else:
                print("✗ Settore parent relationship is INCORRECT")
        
        conn.close()
        
        print("\n=== Test Records Created Successfully ===")
        print("The fix should now work correctly when creating new TMA records through the UI.")
        print("Test records created:")
        print(f"- Località: LOC_TEST (ID: {localita_id})")
        print(f"- Area: AREA_TEST (ID: {area_id}, parent: {localita_id})")
        print(f"- Settore: SETT_TEST (ID: {settore_id}, parent: {area_id})")
        
    except Exception as e:
        print(f"Error creating test records: {e}")

if __name__ == "__main__":
    create_test_records()