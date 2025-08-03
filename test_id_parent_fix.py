#!/usr/bin/env python3
"""
Simple test to verify the id_parent fix is working
This script will check if TMA records have proper id_parent values
"""

import sqlite3
import os

def test_id_parent_fix():
    """Test if id_parent is being saved correctly in TMA records"""
    
    # Path to the database
    db_path = "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/pyarchinit_db.sqlite"
    
    if not os.path.exists(db_path):
        print(f"Database not found at: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== Testing ID_Parent Fix ===")
        
        # Check if the table exists and has the required columns
        cursor.execute("PRAGMA table_info(pyarchinit_thesaurus_sigle)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"Available columns: {columns}")
        
        if 'id_parent' not in columns:
            print("ERROR: id_parent column not found in table!")
            return
        
        # Check TMA records with hierarchy
        print("\n1. Checking TMA records with hierarchy:")
        query = """
        SELECT id_thesaurus_sigle, sigla, sigla_estesa, tipologia_sigla, 
               parent_sigla, id_parent, hierarchy_level
        FROM pyarchinit_thesaurus_sigle 
        WHERE nome_tabella = 'TMA Materiali Archeologici'
        AND tipologia_sigla IN ('10.3', '10.7', '10.15')
        ORDER BY tipologia_sigla, sigla
        """
        
        cursor.execute(query)
        records = cursor.fetchall()
        
        print(f"Found {len(records)} TMA hierarchy records:")
        
        localita_records = []
        area_records = []
        settore_records = []
        
        for record in records:
            id_thes, sigla, sigla_estesa, tipologia, parent_sigla, id_parent, hierarchy_level = record
            print(f"  ID: {id_thes}, Sigla: {sigla}, Tipo: {tipologia}, Parent: {parent_sigla}, ID_Parent: {id_parent}, Level: {hierarchy_level}")
            
            if tipologia == '10.3':  # Località
                localita_records.append(record)
            elif tipologia == '10.7':  # Area
                area_records.append(record)
            elif tipologia == '10.15':  # Settore
                settore_records.append(record)
        
        # Check if areas have proper parent IDs
        print("\n2. Checking Area parent relationships:")
        for area_record in area_records:
            id_thes, sigla, sigla_estesa, tipologia, parent_sigla, id_parent, hierarchy_level = area_record
            
            if parent_sigla and not id_parent:
                print(f"  ISSUE: Area '{sigla}' has parent_sigla '{parent_sigla}' but no id_parent!")
                
                # Try to find the parent
                cursor.execute("""
                SELECT id_thesaurus_sigle FROM pyarchinit_thesaurus_sigle 
                WHERE nome_tabella = 'TMA Materiali Archeologici' 
                AND sigla = ? AND tipologia_sigla = '10.3'
                """, (parent_sigla,))
                
                parent_result = cursor.fetchone()
                if parent_result:
                    print(f"    Found parent ID: {parent_result[0]} - should be linked!")
                else:
                    print(f"    Parent record not found for sigla: {parent_sigla}")
            elif parent_sigla and id_parent:
                print(f"  OK: Area '{sigla}' correctly linked to parent ID {id_parent}")
            else:
                print(f"  INFO: Area '{sigla}' has no parent (root level)")
        
        # Check if settori have proper parent IDs
        print("\n3. Checking Settore parent relationships:")
        for settore_record in settore_records:
            id_thes, sigla, sigla_estesa, tipologia, parent_sigla, id_parent, hierarchy_level = settore_record
            
            if parent_sigla and not id_parent:
                print(f"  ISSUE: Settore '{sigla}' has parent_sigla '{parent_sigla}' but no id_parent!")
                
                # Try to find the parent
                cursor.execute("""
                SELECT id_thesaurus_sigle FROM pyarchinit_thesaurus_sigle 
                WHERE nome_tabella = 'TMA Materiali Archeologici' 
                AND sigla = ? AND tipologia_sigla = '10.7'
                """, (parent_sigla,))
                
                parent_result = cursor.fetchone()
                if parent_result:
                    print(f"    Found parent ID: {parent_result[0]} - should be linked!")
                else:
                    print(f"    Parent record not found for sigla: {parent_sigla}")
            elif parent_sigla and id_parent:
                print(f"  OK: Settore '{sigla}' correctly linked to parent ID {id_parent}")
            else:
                print(f"  INFO: Settore '{sigla}' has no parent (root level)")
        
        conn.close()
        
        print("\n=== Test Complete ===")
        print("If you see 'ISSUE' messages above, the id_parent fix needs more work.")
        print("If you see 'OK' messages, the fix is working correctly.")
        
    except Exception as e:
        print(f"Error testing database: {e}")

if __name__ == "__main__":
    test_id_parent_fix()