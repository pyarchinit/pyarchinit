#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script to verify TMA thesaurus table naming compatibility
"""

import sqlite3
import os
import sys


def test_tma_table_names(db_path):
    """Test TMA table names in thesaurus"""
    print(f"\nTesting TMA thesaurus compatibility in: {db_path}")
    print("=" * 80)
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at: {db_path}")
        return False
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Test 1: Check what table names exist
        print("\n1. Current TMA table names in thesaurus:")
        cursor.execute("""
            SELECT DISTINCT nome_tabella, COUNT(*) as count
            FROM pyarchinit_thesaurus_sigle
            WHERE nome_tabella LIKE '%TMA%' OR nome_tabella LIKE '%tma%'
            GROUP BY nome_tabella
            ORDER BY nome_tabella
        """)
        
        results = cursor.fetchall()
        for table_name, count in results:
            print(f"   - '{table_name}': {count} records")
        
        # Test 2: Check specific tipologia codes for TMA materiali archeologici
        print("\n2. Testing TMA materiali archeologici entries:")
        test_codes = [
            ('10.1', 'Denominazione collocazione'),
            ('10.2', 'Tipologia collocazione'), 
            ('10.3', 'Località'),
            ('10.7', 'Area'),
            ('10.15', 'Settore')
        ]
        
        for code, description in test_codes:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM pyarchinit_thesaurus_sigle
                WHERE nome_tabella = 'TMA materiali archeologici'
                AND tipologia_sigla = ?
            """, (code,))
            
            count = cursor.fetchone()[0]
            status = "✅" if count > 0 else "❌"
            print(f"   {status} {code} - {description}: {count} entries")
        
        # Test 3: Check TMA Materiali Ripetibili entries
        print("\n3. Testing TMA Materiali Ripetibili entries:")
        material_codes = [
            ('10.4', 'Materiale'),
            ('10.5', 'Categoria'),
            ('10.6', 'Classe'),
            ('10.8', 'Prec. Tipologica'),
            ('10.9', 'Definizione')
        ]
        
        for code, description in material_codes:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM pyarchinit_thesaurus_sigle
                WHERE nome_tabella = 'TMA Materiali Ripetibili'
                AND tipologia_sigla = ?
            """, (code,))
            
            count = cursor.fetchone()[0]
            status = "✅" if count > 0 else "❌"
            print(f"   {status} {code} - {description}: {count} entries")
        
        # Test 4: Check pyarchinit_nome_tabelle entries
        print("\n4. Testing configuration table entries:")
        cursor.execute("""
            SELECT sigla, sigla_estesa
            FROM pyarchinit_thesaurus_sigle
            WHERE nome_tabella = 'pyarchinit_nome_tabelle'
            AND sigla IN ('27', '28')
            ORDER BY sigla
        """)
        
        for sigla, sigla_estesa in cursor.fetchall():
            print(f"   - Table {sigla}: '{sigla_estesa}'")
        
        # Test 5: Check for old/wrong table names
        print("\n5. Checking for old/incorrect table names:")
        old_names = ['tma_table', 'tma_materiali_table', 'tma_materiali_archeologici', 'tma_materiali_ripetibili']
        
        for old_name in old_names:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM pyarchinit_thesaurus_sigle
                WHERE nome_tabella = ?
            """, (old_name,))
            
            count = cursor.fetchone()[0]
            if count > 0:
                print(f"   ⚠️  Found {count} entries with old name: '{old_name}'")
            else:
                print(f"   ✅ No entries found with old name: '{old_name}'")
        
        print("\n" + "=" * 80)
        print("SUMMARY:")
        
        # Check if we need migration
        cursor.execute("""
            SELECT COUNT(*) 
            FROM pyarchinit_thesaurus_sigle
            WHERE nome_tabella IN ('tma_table', 'tma_materiali_table', 'tma_materiali_archeologici', 'tma_materiali_ripetibili')
        """)
        
        old_count = cursor.fetchone()[0]
        
        if old_count > 0:
            print(f"\n⚠️  Found {old_count} entries with old table names.")
            print("   Run the migration script: scripts/migrate_tma_table_names.sql")
        else:
            print("\n✅ No old table names found. Database is up to date!")
        
        return True
        
    except sqlite3.Error as e:
        print(f"\n❌ Database error: {e}")
        return False
        
    finally:
        conn.close()


def main():
    # Test both possible database locations
    db_paths = [
        os.path.expanduser("~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/pyarchinit_db.sqlite"),
        os.path.join(os.path.dirname(__file__), "pyarchinit_db.sqlite")
    ]
    
    for db_path in db_paths:
        if os.path.exists(db_path):
            if test_tma_table_names(db_path):
                break
    else:
        print("❌ No database found in expected locations")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())