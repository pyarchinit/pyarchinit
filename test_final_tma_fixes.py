#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Final test to verify all TMA fixes are working
"""

import sqlite3
import os
import sys


def test_database_structure(cursor):
    """Test if database has been updated with new columns"""
    print("\n=== Testing Database Structure ===")
    
    # Check thesaurus table columns
    cursor.execute("PRAGMA table_info(pyarchinit_thesaurus_sigle)")
    columns = [row[1] for row in cursor.fetchall()]
    
    required_columns = ['order_layer', 'id_parent', 'parent_sigla', 'hierarchy_level']
    missing_columns = [col for col in required_columns if col not in columns]
    
    if missing_columns:
        print(f"❌ Missing columns in thesaurus: {missing_columns}")
        print("   Run the plugin to trigger database update!")
    else:
        print("✅ All required columns exist in thesaurus table")


def test_table_aliases(cursor):
    """Test if table aliases have been updated"""
    print("\n=== Testing Table Aliases ===")
    
    cursor.execute("""
        SELECT DISTINCT nome_tabella, COUNT(*) as count
        FROM pyarchinit_thesaurus_sigle
        WHERE nome_tabella LIKE '%TMA%' OR nome_tabella LIKE '%tma%'
        GROUP BY nome_tabella
    """)
    
    results = cursor.fetchall()
    
    correct_names = ['TMA materiali archeologici', 'TMA materiali ripetibili']
    wrong_names = ['tma_materiali_archeologici', 'tma_materiali_ripetibili']
    
    for table_name, count in results:
        if table_name in correct_names:
            print(f"✅ '{table_name}': {count} records (correct)")
        elif table_name in wrong_names:
            print(f"❌ '{table_name}': {count} records (needs update)")
        else:
            print(f"? '{table_name}': {count} records")


def test_widget_functionality(cursor):
    """Test if widgets will work correctly"""
    print("\n=== Testing Widget Functionality ===")
    
    # Test località query
    cursor.execute("""
        SELECT COUNT(*) 
        FROM pyarchinit_thesaurus_sigle
        WHERE nome_tabella = 'TMA materiali archeologici'
        AND tipologia_sigla = '10.3'
    """)
    
    localita_count = cursor.fetchone()[0]
    print(f"Località options (10.3): {localita_count}")
    
    # Test area with parent
    cursor.execute("""
        SELECT COUNT(*) 
        FROM pyarchinit_thesaurus_sigle
        WHERE nome_tabella = 'TMA materiali archeologici'
        AND tipologia_sigla = '10.7'
        AND parent_sigla IS NOT NULL
    """)
    
    area_with_parent = cursor.fetchone()[0]
    print(f"Areas with parent località: {area_with_parent}")
    
    # Test settore with parent
    cursor.execute("""
        SELECT COUNT(*) 
        FROM pyarchinit_thesaurus_sigle
        WHERE nome_tabella = 'TMA materiali archeologici'
        AND tipologia_sigla = '10.15'
        AND parent_sigla IS NOT NULL
    """)
    
    settore_with_parent = cursor.fetchone()[0]
    print(f"Settori with parent area: {settore_with_parent}")
    
    # Test specific località filtering
    cursor.execute("""
        SELECT a.sigla_estesa, COUNT(s.sigla) as settore_count
        FROM pyarchinit_thesaurus_sigle l
        JOIN pyarchinit_thesaurus_sigle a ON a.parent_sigla = l.sigla
        LEFT JOIN pyarchinit_thesaurus_sigle s ON s.parent_sigla = a.sigla
        WHERE l.nome_tabella = 'TMA materiali archeologici'
        AND l.tipologia_sigla = '10.3'
        AND l.sigla = 'LOC01'
        AND a.nome_tabella = 'TMA materiali archeologici'
        AND a.tipologia_sigla = '10.7'
        GROUP BY a.sigla_estesa
        LIMIT 5
    """)
    
    print("\nExample: Areas under Festòs (LOC01) with settore count:")
    for area, count in cursor.fetchall():
        print(f"  - {area}: {count} settori")


def test_tipologia_codes(cursor):
    """Test if all tipologia codes are correct"""
    print("\n=== Testing Tipologia Codes ===")
    
    # Check for wrong codes
    cursor.execute("""
        SELECT DISTINCT tipologia_sigla, COUNT(*) as count
        FROM pyarchinit_thesaurus_sigle
        WHERE nome_tabella LIKE '%TMA%'
        AND CAST(SUBSTR(tipologia_sigla, 4) AS INTEGER) > 16
        GROUP BY tipologia_sigla
    """)
    
    wrong_codes = cursor.fetchall()
    if wrong_codes:
        print("❌ Found invalid tipologia codes:")
        for code, count in wrong_codes:
            print(f"   {code}: {count} records")
    else:
        print("✅ No invalid tipologia codes found")


def summary(cursor):
    """Provide summary and recommendations"""
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    # Check if database needs update
    cursor.execute("PRAGMA table_info(pyarchinit_thesaurus_sigle)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'order_layer' not in columns:
        print("\n⚠️  DATABASE NEEDS UPDATE")
        print("1. Start QGIS")
        print("2. Load PyArchInit plugin")
        print("3. Connect to this database")
        print("4. The update should run automatically")
    else:
        print("\n✅ Database structure is up to date")
    
    # Check table names
    cursor.execute("""
        SELECT COUNT(*) 
        FROM pyarchinit_thesaurus_sigle
        WHERE nome_tabella = 'TMA materiali archeologici'
    """)
    
    if cursor.fetchone()[0] > 0:
        print("✅ Table names are correct")
        print("✅ Widget filtering should work properly")
    else:
        print("❌ Table names need to be updated")


def main():
    # Database path
    db_path = os.path.expanduser("~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/pyarchinit_db.sqlite")
    
    if not os.path.exists(db_path):
        print(f"Database non trovato in: {db_path}")
        return 1
        
    print(f"Testing TMA fixes in: {db_path}")
    print("=" * 60)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        test_database_structure(cursor)
        test_table_aliases(cursor)
        test_widget_functionality(cursor)
        test_tipologia_codes(cursor)
        summary(cursor)
        
    except sqlite3.Error as e:
        print(f"\n❌ Errore: {e}")
        return 1
        
    finally:
        conn.close()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())