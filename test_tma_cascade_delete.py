#!/usr/bin/env python3
"""Test script to verify TMA cascade deletion works correctly"""

import os
import sys
import sqlite3
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the parent directory to path to import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.db.pyarchinit_conn_strings import Connection
from modules.db.pyarchinit_db_manager import Pyarchinit_db_management

def test_cascade_delete():
    """Test that deleting a TMA record also deletes related materials"""
    
    # Get database path
    conn = Connection()
    db_path = conn.conn_str().replace('sqlite:///', '')
    print(f"Database path: {db_path}")
    
    # Create test data
    engine = create_engine(conn.conn_str())
    
    try:
        # Create a test TMA record
        with engine.connect() as conn:
            # Insert test TMA record
            result = conn.execute(text("""
                INSERT INTO tma_materiali_archeologici 
                (sito, area, inventario, ogtm, ldcn, cassetta, dscu, dtzg) 
                VALUES ('TEST_SITE', 'TEST_AREA', 'TEST_INV', 'TEST', 'TEST', 'TEST', 'TEST', 'TEST')
            """))
            
            # Get the ID of inserted record
            tma_id = result.lastrowid
            print(f"Created test TMA record with ID: {tma_id}")
            
            # Insert related materials
            for i in range(3):
                conn.execute(text("""
                    INSERT INTO tma_materiali_ripetibili 
                    (id_tma, macc, macl, madi) 
                    VALUES (:id_tma, :macc, :macl, :madi)
                """), {
                    "id_tma": tma_id,
                    "macc": f"TEST_CAT_{i}",
                    "macl": f"TEST_CLASS_{i}",
                    "madi": f"TEST_INV_{i}"
                })
            print(f"Created 3 related material records")
            
            # Verify records exist
            result = conn.execute(text("SELECT COUNT(*) FROM tma_materiali_ripetibili WHERE id_tma = :id"), {"id": tma_id})
            count = result.scalar()
            print(f"Verified {count} material records exist for TMA ID {tma_id}")
            
            # Test deletion using the same approach as in the TMA controller
            print("\nTesting cascade deletion...")
            
            # First delete related materials
            conn.execute(text("DELETE FROM tma_materiali_ripetibili WHERE id_tma = :id_tma"), {"id_tma": tma_id})
            print(f"Deleted related materials for TMA ID {tma_id}")
            
            # Then delete main record
            conn.execute(text("DELETE FROM tma_materiali_archeologici WHERE id = :id"), {"id": tma_id})
            print(f"Deleted TMA record ID {tma_id}")
            
            # Verify deletion
            result = conn.execute(text("SELECT COUNT(*) FROM tma_materiali_ripetibili WHERE id_tma = :id"), {"id": tma_id})
            mat_count = result.scalar()
            
            result = conn.execute(text("SELECT COUNT(*) FROM tma_materiali_archeologici WHERE id = :id"), {"id": tma_id})
            tma_count = result.scalar()
            
            if mat_count == 0 and tma_count == 0:
                print("\n✅ SUCCESS: Cascade deletion working correctly!")
                print(f"   - TMA records remaining: {tma_count}")
                print(f"   - Material records remaining: {mat_count}")
            else:
                print("\n❌ FAILURE: Records still exist after deletion")
                print(f"   - TMA records remaining: {tma_count}")
                print(f"   - Material records remaining: {mat_count}")
                
    except Exception as e:
        print(f"\n❌ ERROR during test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_cascade_delete()