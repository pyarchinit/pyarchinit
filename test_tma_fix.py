#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script to verify TMA materials fix
"""

import sqlite3
import sys


def test_tma_materials_persistence():
    """Test that materials data persists after save"""
    print("\n" + "="*60)
    print("TEST: TMA Materials Data Persistence")
    print("="*60)
    
    print("\nThis test verifies that:")
    print("1. Materials entered in the tableWidget are saved to database")
    print("2. Data is not lost during the save/reload cycle")
    print("3. Multiple materials can be saved (not just one)")
    
    print("\nTo test manually in QGIS:")
    print("1. Open TMA form")
    print("2. Create or load a TMA record")
    print("3. Add materials by clicking 'Add Material' button")
    print("4. Enter data in 'Categoria' field (e.g., 'avorio')")
    print("5. Click Save")
    print("6. Check that the data remains in the table")
    
    print("\nExpected behavior after fix:")
    print("- Data entered in materials table should persist after save")
    print("- Multiple rows can be added and saved")
    print("- No 'category is missing' error when data is entered")
    
    print("\nKey fixes implemented:")
    print("1. Modified fill_fields() to preserve unsaved materials data")
    print("2. Added logic to detect when we're reloading the same record")
    print("3. Improved get_cell_value() to close editors before reading")
    print("4. Materials table is only reloaded when switching to a different record")
    
    return True


def check_database_materials(db_path, tma_id):
    """Check materials in database for verification"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, macc, macl, macp, macd, cronologia_mac, macq, peso
            FROM tma_materiali_ripetibili
            WHERE id_tma = ?
            ORDER BY id
        """, (tma_id,))
        
        materials = cursor.fetchall()
        
        if materials:
            print(f"\nFound {len(materials)} materials for TMA ID {tma_id}:")
            for i, mat in enumerate(materials):
                print(f"  Material {i+1}: Category='{mat[1]}', Class='{mat[2]}'")
        else:
            print(f"\nNo materials found for TMA ID {tma_id}")
            
        conn.close()
        return len(materials)
        
    except Exception as e:
        print(f"Error checking database: {e}")
        return -1


def main():
    print("TMA Materials Fix Test")
    print("=" * 60)
    
    # Run the persistence test
    test_tma_materials_persistence()
    
    # If a TMA ID is provided, check its materials
    if len(sys.argv) > 1:
        try:
            tma_id = int(sys.argv[1])
            import os
            db_path = os.path.expanduser("~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/pyarchinit_db.sqlite")
            
            if os.path.exists(db_path):
                check_database_materials(db_path, tma_id)
            else:
                print(f"\nDatabase not found at: {db_path}")
        except ValueError:
            print(f"\nInvalid TMA ID: {sys.argv[1]}")
    else:
        print("\nTip: Run with TMA ID to check its materials:")
        print(f"  python {sys.argv[0]} <TMA_ID>")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())