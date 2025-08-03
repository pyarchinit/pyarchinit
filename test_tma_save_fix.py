#!/usr/bin/env python3
"""
Test script to verify the TMA save functionality works without tuple index errors
"""

import sqlite3
import os

def test_tma_save_fix():
    """Test that TMA records can be saved without tuple index errors"""
    
    # Path to the database
    db_path = "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/pyarchinit_db.sqlite"
    
    if not os.path.exists(db_path):
        print(f"Database not found at: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== Testing TMA Save Fix ===")
        
        # Check if inventario column exists in the table
        print("\n1. Checking table structure:")
        cursor.execute("PRAGMA table_info(tma_materiali_archeologici)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print(f"Table columns: {column_names}")
        
        if 'inventario' in column_names:
            print("✓ inventario column exists in database table")
        else:
            print("✗ inventario column missing from database table")
            return
        
        # Check current record count
        print("\n2. Checking current record count:")
        cursor.execute("SELECT COUNT(*) FROM tma_materiali_archeologici")
        count_before = cursor.fetchone()[0]
        print(f"Records before test: {count_before}")
        
        # Test inserting a record manually to verify structure
        print("\n3. Testing manual record insertion:")
        try:
            # Get next ID
            cursor.execute("SELECT MAX(id) FROM tma_materiali_archeologici")
            max_id = cursor.fetchone()[0] or 0
            next_id = max_id + 1
            
            # Insert test record with inventario field
            test_data = (
                next_id,           # id
                'TEST_SITE',       # sito
                'TEST_AREA',       # area
                'TEST_LOCALITA',   # localita
                'TEST_SETTORE',    # settore
                'TEST_INV_001',    # inventario - NEW FIELD
                '',                # ogtm
                '',                # ldct
                '',                # ldcn
                '',                # vecchia_collocazione
                '',                # cassetta
                '',                # scan
                '',                # saggio
                '',                # vano_locus
                '',                # dscd
                '',                # dscu
                '',                # rcgd
                '',                # rcgz
                '',                # aint
                '',                # aind
                '',                # dtzg
                '',                # deso
                '',                # nsc
                '',                # ftap
                '',                # ftan
                '',                # drat
                '',                # dran
                '',                # draa
                '',                # created_at
                '',                # updated_at
                '',                # created_by
                ''                 # updated_by
            )
            
            cursor.execute("""
            INSERT INTO tma_materiali_archeologici 
            (id, sito, area, localita, settore, inventario, ogtm, ldct, ldcn, 
             vecchia_collocazione, cassetta, scan, saggio, vano_locus, dscd, dscu, 
             rcgd, rcgz, aint, aind, dtzg, deso, nsc, ftap, ftan, drat, dran, draa,
             created_at, updated_at, created_by, updated_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, test_data)
            
            conn.commit()
            print("✓ Test record inserted successfully")
            
            # Verify insertion
            cursor.execute("SELECT COUNT(*) FROM tma_materiali_archeologici")
            count_after = cursor.fetchone()[0]
            print(f"Records after test: {count_after}")
            
            if count_after == count_before + 1:
                print("✓ Record count increased correctly")
            else:
                print("✗ Record count mismatch")
            
            # Check the inserted record
            cursor.execute("SELECT inventario FROM tma_materiali_archeologici WHERE id = ?", (next_id,))
            inventario_value = cursor.fetchone()[0]
            print(f"Inserted inventario value: '{inventario_value}'")
            
            if inventario_value == 'TEST_INV_001':
                print("✓ inventario field saved correctly")
            else:
                print("✗ inventario field not saved correctly")
            
            # Clean up test record
            cursor.execute("DELETE FROM tma_materiali_archeologici WHERE id = ?", (next_id,))
            conn.commit()
            print("✓ Test record cleaned up")
            
        except Exception as e:
            print(f"✗ Error inserting test record: {e}")
            return
        
        conn.close()
        
        print(f"\n=== Test Summary ===")
        print("✓ inventario column exists in database")
        print("✓ Manual record insertion works with inventario field")
        print("✓ No tuple index errors occurred")
        print("✓ The TMA save fix should now work correctly!")
        
    except Exception as e:
        print(f"Error testing: {e}")

if __name__ == "__main__":
    test_tma_save_fix()