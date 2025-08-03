#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script to verify area and settore widgets show proper parent options
"""

import sqlite3
import os
import sys

def test_area_widget(cursor):
    """Test that area widget can see località options (10.3)"""
    print("\n=== Testing Area Widget ===")
    print("Area widget should show località options (10.3)")
    
    # Query that area widget would use to get località options
    cursor.execute("""
        SELECT DISTINCT sigla, sigla_estesa
        FROM pyarchinit_thesaurus_sigle
        WHERE nome_tabella IN ('tma_materiali_archeologici', 'TMA materiali archeologici')
        AND tipologia_sigla = '10.3'
        ORDER BY sigla
    """)
    
    localita_options = cursor.fetchall()
    print(f"\nFound {len(localita_options)} località options for area widget:")
    for sigla, sigla_estesa in localita_options:
        print(f"  - {sigla}: {sigla_estesa}")
    
    return len(localita_options) > 0

def test_settore_widget(cursor):
    """Test that settore widget can see both località (10.3) and area (10.7) options"""
    print("\n=== Testing Settore Widget ===")
    print("Settore widget should show both località (10.3) and area (10.7) options")
    
    # Query for località options
    cursor.execute("""
        SELECT DISTINCT sigla, sigla_estesa
        FROM pyarchinit_thesaurus_sigle
        WHERE nome_tabella IN ('tma_materiali_archeologici', 'TMA materiali archeologici')
        AND tipologia_sigla = '10.3'
        ORDER BY sigla
    """)
    
    localita_options = cursor.fetchall()
    print(f"\nFound {len(localita_options)} località options for settore widget:")
    for sigla, sigla_estesa in localita_options[:3]:  # Show first 3
        print(f"  - {sigla}: {sigla_estesa}")
    if len(localita_options) > 3:
        print(f"  ... and {len(localita_options) - 3} more")
    
    # Query for area options (would be filtered by selected località in real widget)
    cursor.execute("""
        SELECT DISTINCT sigla, sigla_estesa, parent_sigla
        FROM pyarchinit_thesaurus_sigle
        WHERE nome_tabella IN ('tma_materiali_archeologici', 'TMA materiali archeologici')
        AND tipologia_sigla = '10.7'
        ORDER BY sigla
    """)
    
    area_options = cursor.fetchall()
    print(f"\nFound {len(area_options)} area options for settore widget:")
    # Group by parent località
    by_localita = {}
    for sigla, sigla_estesa, parent in area_options:
        if parent not in by_localita:
            by_localita[parent] = []
        by_localita[parent].append((sigla, sigla_estesa))
    
    for localita, areas in list(by_localita.items())[:2]:  # Show first 2 località
        print(f"  Under {localita}:")
        for sigla, sigla_estesa in areas[:3]:  # Show first 3 areas
            print(f"    - {sigla}: {sigla_estesa}")
        if len(areas) > 3:
            print(f"    ... and {len(areas) - 3} more areas")
    
    if len(by_localita) > 2:
        print(f"  ... and {len(by_localita) - 2} more località with areas")
    
    return len(localita_options) > 0 and len(area_options) > 0

def test_hierarchy(cursor):
    """Test the hierarchy relationships"""
    print("\n=== Testing Hierarchy Relationships ===")
    
    # Check località → area relationships
    cursor.execute("""
        SELECT 
            loc.sigla as localita_sigla,
            loc.sigla_estesa as localita_name,
            COUNT(DISTINCT area.sigla) as area_count
        FROM pyarchinit_thesaurus_sigle loc
        LEFT JOIN pyarchinit_thesaurus_sigle area 
            ON area.parent_sigla = loc.sigla 
            AND area.tipologia_sigla = '10.7'
        WHERE loc.nome_tabella IN ('tma_materiali_archeologici', 'TMA materiali archeologici')
        AND loc.tipologia_sigla = '10.3'
        GROUP BY loc.sigla, loc.sigla_estesa
        ORDER BY loc.sigla
    """)
    
    print("\nLocalità → Area relationships:")
    for sigla, name, count in cursor.fetchall():
        print(f"  {sigla} ({name}): {count} areas")
    
    # Check area → settore relationships
    cursor.execute("""
        SELECT 
            area.sigla as area_sigla,
            area.sigla_estesa as area_name,
            COUNT(DISTINCT sett.sigla) as settore_count
        FROM pyarchinit_thesaurus_sigle area
        LEFT JOIN pyarchinit_thesaurus_sigle sett 
            ON sett.parent_sigla = area.sigla 
            AND sett.tipologia_sigla = '10.15'
        WHERE area.nome_tabella IN ('tma_materiali_archeologici', 'TMA materiali archeologici')
        AND area.tipologia_sigla = '10.7'
        GROUP BY area.sigla, area.sigla_estesa
        HAVING settore_count > 0
        ORDER BY settore_count DESC
        LIMIT 10
    """)
    
    print("\nTop 10 Areas with Settori:")
    for sigla, name, count in cursor.fetchall():
        print(f"  {sigla} ({name}): {count} settori")

def main():
    # Database path
    db_path = os.path.expanduser("~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/pyarchinit_db.sqlite")
    
    if not os.path.exists(db_path):
        print(f"Database non trovato in: {db_path}")
        return 1
        
    print(f"Testing thesaurus widgets with database: {db_path}")
    print("=" * 60)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Run tests
        area_ok = test_area_widget(cursor)
        settore_ok = test_settore_widget(cursor)
        test_hierarchy(cursor)
        
        print("\n" + "=" * 60)
        print("TEST RESULTS:")
        print(f"  ✓ Area widget can see località: {'YES' if area_ok else 'NO'}")
        print(f"  ✓ Settore widget can see località and areas: {'YES' if settore_ok else 'NO'}")
        
        if not area_ok or not settore_ok:
            print("\n⚠️  Some widgets are not working correctly!")
            print("Please run the corrected insert scripts to populate the data.")
        else:
            print("\n✅ All widgets should work correctly!")
            
    except sqlite3.Error as e:
        print(f"\n❌ Errore: {e}")
        return 1
        
    finally:
        conn.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())