#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script to debug località disappearing issue in TMA records
"""

import sqlite3
import os
import sys

def check_tma_records(cursor):
    """Check all TMA records and their località values"""
    print("\n=== Checking TMA Records ===")
    
    cursor.execute("""
        SELECT id, sito, localita, area, settore, scan, created_at, updated_at
        FROM tma_materiali_archeologici
        ORDER BY id DESC
        LIMIT 10
    """)
    
    records = cursor.fetchall()
    print(f"Found {len(records)} recent TMA records:")
    
    for rec in records:
        id_val, sito, localita, area, settore, scan, created, updated = rec
        print(f"\nRecord ID: {id_val}")
        print(f"  Sito: {sito}")
        print(f"  Località: '{localita}' (empty: {localita == '' or localita is None})")
        print(f"  Area: '{area}'")
        print(f"  Settore: '{settore}'")
        print(f"  Scan: {scan}")
        print(f"  Created: {created}")
        print(f"  Updated: {updated}")
        
    return records

def check_second_record(cursor):
    """Specifically check if there's a pattern with second records"""
    print("\n=== Checking Second Records Pattern ===")
    
    # Get records grouped by sito and scan
    cursor.execute("""
        SELECT sito, scan, COUNT(*) as count
        FROM tma_materiali_archeologici
        GROUP BY sito, scan
        HAVING count > 1
        ORDER BY sito, scan
    """)
    
    groups = cursor.fetchall()
    print(f"Found {len(groups)} groups with multiple records:")
    
    for sito, scan, count in groups[:5]:  # Show first 5
        print(f"\nSito: {sito}, Scan: {scan} - {count} records")
        
        # Get the records for this group
        cursor.execute("""
            SELECT id, localita, area, settore, created_at
            FROM tma_materiali_archeologici
            WHERE sito = ? AND scan = ?
            ORDER BY id
        """, (sito, scan))
        
        group_records = cursor.fetchall()
        for idx, (id_val, localita, area, settore, created) in enumerate(group_records):
            print(f"  Record {idx+1} (ID: {id_val}): località='{localita}', area='{area}', created={created}")

def check_thesaurus_values(cursor):
    """Check if thesaurus values are properly available"""
    print("\n=== Checking Thesaurus Values ===")
    
    # Check località values
    cursor.execute("""
        SELECT sigla, sigla_estesa
        FROM pyarchinit_thesaurus_sigle
        WHERE nome_tabella IN ('tma_materiali_archeologici', 'TMA materiali archeologici')
        AND tipologia_sigla = '10.3'
        ORDER BY sigla
    """)
    
    localita_values = cursor.fetchall()
    print(f"\nAvailable località values ({len(localita_values)}):")
    for sigla, sigla_estesa in localita_values:
        print(f"  {sigla}: {sigla_estesa}")

def analyze_empty_localita(cursor):
    """Analyze records with empty località"""
    print("\n=== Analyzing Empty Località ===")
    
    cursor.execute("""
        SELECT COUNT(*) 
        FROM tma_materiali_archeologici
        WHERE localita IS NULL OR localita = ''
    """)
    
    empty_count = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(*) 
        FROM tma_materiali_archeologici
    """)
    
    total_count = cursor.fetchone()[0]
    
    print(f"Records with empty località: {empty_count} out of {total_count} ({empty_count/total_count*100:.1f}% if total_count > 0 else 0)")
    
    # Check pattern by position
    cursor.execute("""
        WITH numbered_records AS (
            SELECT 
                id, sito, scan, localita,
                ROW_NUMBER() OVER (PARTITION BY sito, scan ORDER BY id) as position
            FROM tma_materiali_archeologici
        )
        SELECT position, 
               COUNT(*) as total,
               SUM(CASE WHEN localita IS NULL OR localita = '' THEN 1 ELSE 0 END) as empty_count
        FROM numbered_records
        WHERE position <= 5
        GROUP BY position
        ORDER BY position
    """)
    
    print("\nEmpty località by record position within sito/scan group:")
    for position, total, empty in cursor.fetchall():
        percent = (empty/total*100) if total > 0 else 0
        print(f"  Position {position}: {empty}/{total} empty ({percent:.1f}%)")

def main():
    # Database path
    db_path = os.path.expanduser("~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/pyarchinit_db.sqlite")
    
    if not os.path.exists(db_path):
        print(f"Database non trovato in: {db_path}")
        return 1
        
    print(f"Analyzing TMA località issue in: {db_path}")
    print("=" * 60)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        check_tma_records(cursor)
        check_second_record(cursor)
        check_thesaurus_values(cursor)
        analyze_empty_localita(cursor)
        
        print("\n" + "=" * 60)
        print("Analysis complete!")
        
    except sqlite3.Error as e:
        print(f"\n❌ Errore: {e}")
        return 1
        
    finally:
        conn.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())