#!/usr/bin/env python3
"""
Fix TMA table name inconsistencies in the thesaurus database
"""

import sqlite3
import os

def fix_tma_table_names():
    """Fix the inconsistent TMA table names in the database"""
    
    # Path to the database
    db_path = "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/pyarchinit_db.sqlite"
    
    if not os.path.exists(db_path):
        print(f"Database not found at: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== Fixing TMA Table Name Inconsistencies ===")
        
        # First, show current state
        print("\n1. Current state before fixes:")
        cursor.execute("""
        SELECT DISTINCT nome_tabella, COUNT(*) as count
        FROM pyarchinit_thesaurus_sigle 
        WHERE UPPER(nome_tabella) LIKE '%TMA%'
        GROUP BY nome_tabella
        ORDER BY nome_tabella
        """)
        
        current_tables = cursor.fetchall()
        for table_name, count in current_tables:
            print(f"  '{table_name}' - {count} records")
        
        # Fix 1: Update "TMA Materiali Archeologici" (capital M) to "TMA materiali archeologici" (lowercase m)
        print(f"\n2. Fixing 'TMA Materiali Archeologici' -> 'TMA materiali archeologici':")
        cursor.execute("""
        UPDATE pyarchinit_thesaurus_sigle 
        SET nome_tabella = 'TMA materiali archeologici'
        WHERE nome_tabella = 'TMA Materiali Archeologici'
        """)
        
        affected_rows = cursor.rowcount
        print(f"   Updated {affected_rows} records")
        
        # Fix 2: Update "TMA materiali ripetibili" (lowercase) to "TMA Materiali Ripetibili" (proper case)
        print(f"\n3. Fixing 'TMA materiali ripetibili' -> 'TMA Materiali Ripetibili':")
        cursor.execute("""
        UPDATE pyarchinit_thesaurus_sigle 
        SET nome_tabella = 'TMA Materiali Ripetibili'
        WHERE nome_tabella = 'TMA materiali ripetibili'
        """)
        
        affected_rows = cursor.rowcount
        print(f"   Updated {affected_rows} records")
        
        # Commit the changes
        conn.commit()
        
        # Show final state
        print(f"\n4. Final state after fixes:")
        cursor.execute("""
        SELECT DISTINCT nome_tabella, COUNT(*) as count
        FROM pyarchinit_thesaurus_sigle 
        WHERE UPPER(nome_tabella) LIKE '%TMA%'
        GROUP BY nome_tabella
        ORDER BY nome_tabella
        """)
        
        final_tables = cursor.fetchall()
        for table_name, count in final_tables:
            print(f"  '{table_name}' - {count} records")
        
        # Verify the expected names are now correct
        print(f"\n5. Verification:")
        expected_names = ['TMA materiali archeologici', 'TMA Materiali Ripetibili']
        found_names = [name for name, count in final_tables]
        
        all_correct = True
        for expected in expected_names:
            if expected in found_names:
                print(f"  ✓ '{expected}' - CORRECT")
            else:
                print(f"  ✗ '{expected}' - MISSING")
                all_correct = False
        
        if len(final_tables) == 2 and all_correct:
            print(f"\n✓ SUCCESS: Table names are now standardized correctly!")
            print(f"✓ 'TMA materiali archeologici' - for main TMA fields")
            print(f"✓ 'TMA Materiali Ripetibili' - for materials table fields")
        else:
            print(f"\n⚠️  WARNING: There may still be issues with table names")
        
        conn.close()
        
    except Exception as e:
        print(f"Error fixing table names: {e}")

if __name__ == "__main__":
    fix_tma_table_names()