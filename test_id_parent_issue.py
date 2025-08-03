#!/usr/bin/env python3
"""
Test script to reproduce the id_parent issue in TMA thesaurus
"""

import sys
import os
sys.path.append('/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit')

from modules.db.pyarchinit_conn_strings import Connection
from modules.db.pyarchinit_db_manager import Pyarchinit_db_management
from modules.db.entities.PYARCHINIT_THESAURUS_SIGLE import PYARCHINIT_THESAURUS_SIGLE

def test_parent_search():
    """Test searching for parent records in thesaurus"""
    
    # Initialize database connection
    conn = Connection()
    conn_str = conn.conn_str()
    db_manager = Pyarchinit_db_management(conn_str)
    
    print("=== Testing Parent Record Search ===")
    
    # First, let's see what TMA records exist
    print("\n1. Checking existing TMA records:")
    search_all_tma = {
        'nome_tabella': "'TMA Materiali Archeologici'"
    }
    
    all_tma_records = db_manager.query_bool(search_all_tma, PYARCHINIT_THESAURUS_SIGLE)
    print(f"Found {len(all_tma_records) if all_tma_records else 0} TMA records")
    
    if all_tma_records:
        for record in all_tma_records[:10]:  # Show first 10
            print(f"  ID: {record.id_thesaurus_sigle}, Sigla: {record.sigla}, "
                  f"Tipologia: {record.tipologia_sigla}, Parent: {record.parent_sigla}, "
                  f"ID_Parent: {record.id_parent}")
    
    # Test searching for località (10.3)
    print("\n2. Searching for località records (10.3):")
    search_localita = {
        'nome_tabella': "'TMA Materiali Archeologici'",
        'tipologia_sigla': "'10.3'"
    }
    
    localita_records = db_manager.query_bool(search_localita, PYARCHINIT_THESAURUS_SIGLE)
    print(f"Found {len(localita_records) if localita_records else 0} località records")
    
    if localita_records:
        for record in localita_records:
            print(f"  ID: {record.id_thesaurus_sigle}, Sigla: {record.sigla}, "
                  f"Estesa: {record.sigla_estesa}")
    
    # Test searching for area records (10.7)
    print("\n3. Searching for area records (10.7):")
    search_area = {
        'nome_tabella': "'TMA Materiali Archeologici'",
        'tipologia_sigla': "'10.7'"
    }
    
    area_records = db_manager.query_bool(search_area, PYARCHINIT_THESAURUS_SIGLE)
    print(f"Found {len(area_records) if area_records else 0} area records")
    
    if area_records:
        for record in area_records:
            print(f"  ID: {record.id_thesaurus_sigle}, Sigla: {record.sigla}, "
                  f"Estesa: {record.sigla_estesa}, Parent: {record.parent_sigla}, "
                  f"ID_Parent: {record.id_parent}")
    
    # Test specific parent search like the code does
    if localita_records:
        test_parent_sigla = localita_records[0].sigla
        print(f"\n4. Testing parent search for sigla '{test_parent_sigla}':")
        
        search_dict = {
            'nome_tabella': "'TMA Materiali Archeologici'",
            'sigla': "'" + test_parent_sigla + "'",
            'tipologia_sigla': "'10.3'"
        }
        
        print(f"Search dict: {search_dict}")
        parent_records = db_manager.query_bool(search_dict, PYARCHINIT_THESAURUS_SIGLE)
        print(f"Found {len(parent_records) if parent_records else 0} parent records")
        
        if parent_records:
            parent_record = parent_records[0]
            print(f"  Parent ID: {parent_record.id_thesaurus_sigle}")
            print(f"  Parent Sigla: {parent_record.sigla}")
            print(f"  Parent Estesa: {parent_record.sigla_estesa}")
        else:
            print("  No parent record found!")
            
            # Try alternative searches
            print("\n  Trying alternative searches:")
            
            # Search without quotes
            search_alt1 = {
                'nome_tabella': 'TMA Materiali Archeologici',
                'sigla': test_parent_sigla,
                'tipologia_sigla': '10.3'
            }
            print(f"  Alt search 1: {search_alt1}")
            alt_records1 = db_manager.query_bool(search_alt1, PYARCHINIT_THESAURUS_SIGLE)
            print(f"  Found {len(alt_records1) if alt_records1 else 0} records")
            
            # Search with just sigla
            search_alt2 = {
                'sigla': "'" + test_parent_sigla + "'"
            }
            print(f"  Alt search 2: {search_alt2}")
            alt_records2 = db_manager.query_bool(search_alt2, PYARCHINIT_THESAURUS_SIGLE)
            print(f"  Found {len(alt_records2) if alt_records2 else 0} records")

if __name__ == "__main__":
    test_parent_search()