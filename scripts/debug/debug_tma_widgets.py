#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Debug script for TMA widget filtering issues
"""

import sqlite3
import os
import sys


def check_thesaurus_data(cursor):
    """Check thesaurus data for correct nome_tabella values"""
    print("\n=== Checking Thesaurus Table Names ===")
    
    cursor.execute("""
        SELECT DISTINCT nome_tabella, COUNT(*) as count
        FROM pyarchinit_thesaurus_sigle
        GROUP BY nome_tabella
        ORDER BY nome_tabella
    """)
    
    print("Table names in thesaurus:")
    for table_name, count in cursor.fetchall():
        print(f"  '{table_name}': {count} records")
    
    # Check specifically for TMA tables
    print("\n=== Checking TMA Table Records ===")
    cursor.execute("""
        SELECT nome_tabella, tipologia_sigla, COUNT(*) as count
        FROM pyarchinit_thesaurus_sigle
        WHERE nome_tabella LIKE '%tma%' OR nome_tabella LIKE '%TMA%'
        GROUP BY nome_tabella, tipologia_sigla
        ORDER BY nome_tabella, tipologia_sigla
    """)
    
    print("TMA-related records:")
    for table_name, tipo, count in cursor.fetchall():
        print(f"  Table: '{table_name}', Type: {tipo}, Count: {count}")


def test_localita_query(cursor):
    """Test the exact query used in filter_area_by_localita"""
    print("\n=== Testing Località Query ===")
    
    # Test query for località "Festòs"
    test_localita = "Festòs"
    
    # Try different table name variations
    table_variations = [
        'tma_materiali_archeologici',
        'TMA materiali archeologici',
        'tma_materiali_ripetibili',
        'TMA materiali ripetibili'
    ]
    
    for table_name in table_variations:
        cursor.execute("""
            SELECT sigla, sigla_estesa, id_parent, parent_sigla
            FROM pyarchinit_thesaurus_sigle
            WHERE nome_tabella = ?
            AND tipologia_sigla = '10.3'
            AND sigla_estesa = ?
        """, (table_name, test_localita))
        
        result = cursor.fetchone()
        if result:
            print(f"\nFound '{test_localita}' with table name '{table_name}':")
            print(f"  Sigla: {result[0]}")
            print(f"  ID Parent: {result[2]}")
            print(f"  Parent Sigla: {result[3]}")
            
            # Now check for areas with this parent
            cursor.execute("""
                SELECT sigla, sigla_estesa
                FROM pyarchinit_thesaurus_sigle
                WHERE nome_tabella = ?
                AND tipologia_sigla = '10.7'
                AND parent_sigla = ?
            """, (table_name, result[0]))
            
            areas = cursor.fetchall()
            print(f"  Found {len(areas)} areas for this località:")
            for area_sigla, area_name in areas[:5]:  # Show first 5
                print(f"    - {area_sigla}: {area_name}")
            if len(areas) > 5:
                print(f"    ... and {len(areas) - 5} more")


def check_hierarchy(cursor):
    """Check if hierarchy is properly set up"""
    print("\n=== Checking Hierarchy Setup ===")
    
    # Check località records
    cursor.execute("""
        SELECT sigla, sigla_estesa, id_parent, parent_sigla, hierarchy_level
        FROM pyarchinit_thesaurus_sigle
        WHERE tipologia_sigla = '10.3'
        ORDER BY sigla
    """)
    
    print("\nLocalità records (10.3):")
    for record in cursor.fetchall():
        print(f"  {record[0]}: {record[1]} (parent: {record[3]}, level: {record[4]})")
    
    # Check area records with parents
    cursor.execute("""
        SELECT sigla, sigla_estesa, parent_sigla, hierarchy_level
        FROM pyarchinit_thesaurus_sigle
        WHERE tipologia_sigla = '10.7'
        AND parent_sigla IS NOT NULL
        ORDER BY parent_sigla, sigla
        LIMIT 10
    """)
    
    print("\nArea records with parents (10.7):")
    for record in cursor.fetchall():
        print(f"  {record[0]}: {record[1]} (parent: {record[2]}, level: {record[3]})")


def suggest_fixes(cursor):
    """Suggest SQL fixes if needed"""
    print("\n=== Suggested Fixes ===")
    
    # Check if we need to update nome_tabella
    cursor.execute("""
        SELECT COUNT(*) 
        FROM pyarchinit_thesaurus_sigle
        WHERE nome_tabella = 'tma_materiali_archeologici'
    """)
    
    old_count = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(*) 
        FROM pyarchinit_thesaurus_sigle
        WHERE nome_tabella = 'TMA materiali archeologici'
    """)
    
    new_count = cursor.fetchone()[0]
    
    if old_count > 0 and new_count == 0:
        print("\nNeed to update table names from 'tma_materiali_archeologici' to 'TMA materiali archeologici'")
        print("Run this SQL:")
        print("UPDATE pyarchinit_thesaurus_sigle")
        print("SET nome_tabella = 'TMA materiali archeologici'")
        print("WHERE nome_tabella = 'tma_materiali_archeologici';")
    elif old_count == 0 and new_count > 0:
        print("\nTable names are already updated to 'TMA materiali archeologici'")
    else:
        print(f"\nMixed state: {old_count} old format, {new_count} new format")


def main():
    # Database path
    db_path = os.path.expanduser("~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/pyarchinit_db.sqlite")
    
    if not os.path.exists(db_path):
        print(f"Database non trovato in: {db_path}")
        return 1
        
    print(f"Debugging TMA widget issues in: {db_path}")
    print("=" * 60)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        check_thesaurus_data(cursor)
        test_localita_query(cursor)
        check_hierarchy(cursor)
        suggest_fixes(cursor)
        
        print("\n" + "=" * 60)
        print("Debug complete!")
        
    except sqlite3.Error as e:
        print(f"\n❌ Errore: {e}")
        return 1
        
    finally:
        conn.close()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())