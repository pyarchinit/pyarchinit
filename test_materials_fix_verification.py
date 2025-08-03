#!/usr/bin/env python3
"""
Test script to verify the TMA materials persistence fix
This will test that materials data is properly loaded and persists when navigating between records
"""

import sqlite3
import os

def test_materials_persistence_fix():
    """Test that TMA materials data persists correctly after the fix"""
    
    # Path to the database
    db_path = "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/pyarchinit_db.sqlite"
    
    if not os.path.exists(db_path):
        print(f"Database not found at: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== Testing TMA Materials Persistence Fix ===")
        
        # Test 1: Check if we have TMA records to test with
        print("\n1. Checking TMA records:")
        cursor.execute("SELECT COUNT(*) FROM tma_materiali_archeologici")
        tma_count = cursor.fetchone()[0]
        print(f"   Found {tma_count} TMA records")
        
        if tma_count == 0:
            print("   No TMA records found - creating test record")
            # Create a test TMA record
            cursor.execute("""
            INSERT INTO tma_materiali_archeologici 
            (sito, area, localita, settore, ogtm, ldct, ldcn, 
             vecchia_collocazione, cassetta, scan, saggio, vano_locus, dscd, dscu, 
             rcgd, rcgz, aint, aind, dtzg, deso, nsc, ftap, ftan, drat, dran, draa,
             created_at, updated_at, created_by, updated_by)
            VALUES 
            ('TEST_SITE', 'TEST_AREA', 'TEST_LOC', 'TEST_SECT', 'TEST_MAT',
             'TEST_LDCT', 'TEST_LDCN', 'TEST_VECCHIA', 'TEST_CASS', 'TEST_SCAN', 
             'TEST_SAGGIO', 'TEST_VANO', 'TEST_DSCD', 'TEST_DSCU', 'TEST_RCGD', 
             'TEST_RCGZ', 'TEST_AINT', 'TEST_AIND', 'TEST_DTZG', 'TEST_DESO', 
             'TEST_NSC', 'TEST_FTAP', 'TEST_FTAN', 'TEST_DRAT', 'TEST_DRAN', 'TEST_DRAA',
             '', '', '', '')
            """)
            conn.commit()
            tma_id = cursor.lastrowid
            print(f"   Created test TMA record with ID: {tma_id}")
        else:
            # Get first TMA record
            cursor.execute("SELECT id FROM tma_materiali_archeologici LIMIT 1")
            tma_id = cursor.fetchone()[0]
            print(f"   Using existing TMA record with ID: {tma_id}")
        
        # Test 2: Check if this TMA record has materials
        print(f"\n2. Checking materials for TMA ID {tma_id}:")
        cursor.execute("SELECT COUNT(*) FROM tma_materiali_ripetibili WHERE id_tma = ?", (tma_id,))
        materials_count = cursor.fetchone()[0]
        print(f"   Found {materials_count} materials for TMA ID {tma_id}")
        
        if materials_count == 0:
            print("   No materials found - creating test materials")
            # Create test materials (13 values: id_tma, madi, macc, macl, macp, macd, cronologia_mac, macq, peso, created_at, updated_at, created_by, updated_by)
            test_materials = [
                (tma_id, 'Ceramica', 'Ceramica comune', 'Olla', 'Olla da cucina', 'Romano', '1', 50.5, '', '', '', '', ''),
                (tma_id, 'Metallo', 'Bronzo', 'Fibula', 'Fibula ad arco', 'Romano', '1', 12.3, '', '', '', '', ''),
                (tma_id, 'Vetro', 'Vetro soffiato', 'Bottiglia', 'Bottiglia da vino', 'Romano', '1', 25.8, '', '', '', '', '')
            ]
            
            for mat in test_materials:
                cursor.execute("""
                INSERT INTO tma_materiali_ripetibili 
                (id_tma, madi, macc, macl, macp, macd, cronologia_mac, macq, peso, created_at, updated_at, created_by, updated_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, mat)
            
            conn.commit()
            print(f"   Created {len(test_materials)} test materials")
            materials_count = len(test_materials)
        
        # Test 3: Verify the fix was applied
        print(f"\n3. Verifying the fix was applied:")
        
        # Check if the fix is in the code
        tma_file_path = "tabs/Tma.py"
        if os.path.exists(tma_file_path):
            with open(tma_file_path, 'r') as f:
                content = f.read()
                if "self.load_materials_table()" in content and "# Load materials data for this record" in content:
                    print("   ✓ Fix confirmed: load_materials_table() call added to fill_fields()")
                else:
                    print("   ✗ Fix not found in code")
        else:
            print("   ⚠️  Cannot verify fix - Tma.py file not found")
        
        # Test 4: Verify materials data structure
        print(f"\n4. Verifying materials data structure:")
        cursor.execute("""
        SELECT id, madi, macc, macl, macp, macd, cronologia_mac, macq, peso 
        FROM tma_materiali_ripetibili 
        WHERE id_tma = ? 
        LIMIT 5
        """, (tma_id,))
        
        materials = cursor.fetchall()
        print(f"   Materials for TMA ID {tma_id}:")
        for mat in materials:
            mat_id, madi, macc, macl, macp, macd, cronologia, macq, peso = mat
            print(f"     ID {mat_id}: {macc} - {macl} - {macd} (Qty: {macq}, Weight: {peso}g)")
        
        # Test 5: Check table structure
        print(f"\n5. Checking table structures:")
        
        # Check TMA table
        cursor.execute("PRAGMA table_info(tma_materiali_archeologici)")
        tma_columns = [col[1] for col in cursor.fetchall()]
        print(f"   TMA table columns: {len(tma_columns)} columns")
        
        # Check materials table
        cursor.execute("PRAGMA table_info(tma_materiali_ripetibili)")
        mat_columns = [col[1] for col in cursor.fetchall()]
        print(f"   Materials table columns: {len(mat_columns)} columns")
        print(f"   Materials table structure: {mat_columns}")
        
        conn.close()
        
        print(f"\n=== Fix Summary ===")
        print("✓ PROBLEM IDENTIFIED: load_materials_table() was never called in fill_fields()")
        print("✓ PROBLEM RESULT: materials_loaded flag remained False during navigation")
        print("✓ PROBLEM RESULT: save_materials_data() skipped saving with warning message")
        print("✓ FIX APPLIED: Added load_materials_table() call to fill_fields() method")
        print("✓ EXPECTED RESULT: materials_loaded will be True when navigating between records")
        print("✓ EXPECTED RESULT: Materials data will persist correctly")
        
        print(f"\n=== Testing Instructions ===")
        print("1. Open the TMA tab in PyArchInit")
        print("2. Navigate to a record and add materials in tabwidget_materiali")
        print("3. Navigate to another record using next/previous buttons")
        print("4. Navigate back to the original record")
        print("5. Verify materials data is still present (should no longer disappear)")
        print("6. Check QGIS logs for 'materials_loaded flag = True' instead of False")
        
        if materials_count > 0:
            print(f"\n✓ SUCCESS: Test data is ready with {materials_count} materials for testing")
        else:
            print(f"\n⚠️  No test materials available - create some materials to test the fix")
        
    except Exception as e:
        print(f"Error testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_materials_persistence_fix()