#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to insert TMA vocabularies into pyarchinit_thesaurus_sigle table
Based on TMA_vocabolari.xlsx from desktop
"""

import sys
import os
import pandas as pd

# Add parent directory to path to import pyarchinit modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from modules.db.pyarchinit_conn_strings import Connection
from modules.db.pyarchinit_db_manager import Pyarchinit_db_Management
from modules.db.pyarchinit_utility import Utility

def insert_tma_vocabularies():
    """Insert TMA vocabularies into thesaurus table."""
    
    # Initialize database connection
    conn = Connection()
    db_manager = Pyarchinit_db_Management(conn.conn_str())
    db_manager.connection()
    
    # Read vocabularies from Excel file
    excel_path = "/Users/enzo/Desktop/TMA_vocabolari.xlsx"
    if os.path.exists(excel_path):
        df = pd.read_excel(excel_path)
        materials = df['Definzione materiale componente'].tolist()
        notes = df['NOTE'].fillna('').tolist()
    else:
        # Fallback to hardcoded values if Excel not found
        materials = [
            'ceramica', 'vetro', 'metallo', 'materiale fittile', 
            'materiale litico', 'industria litica', 'osso', 'avorio',
            'resti osteologici', 'legno', 'materiale organico',
            'campioni di terra', 'altri materiali'
        ]
        notes = [
            '', '', 'argento, bronzo, oro, piombo, rame', 'argilla',
            'oggetti in pietra', 'scheggiata, pesante', '', '',
            '', '', 'carbone, resti animali', '', 
            'pasta vitrea, cristallo di rocca, ocra'
        ]
    
    # Counter for inserted records
    inserted = 0
    
    # Insert vocabularies for ogtm field in main TMA table
    print("Inserting TMA vocabularies for ogtm field...")
    for material, note in zip(materials, notes):
        try:
            data = {
                'nome_tabella': 'TMA materiali archeologici',
                'sigla': '',
                'sigla_estesa': material,
                'descrizione': note,
                'tipologia_sigla': 'ogtm',
                'lingua': 'it'
            }
            
            # Check if already exists
            search_dict = {
                'nome_tabella': "'tma_materiali_archeologici'",
                'sigla_estesa': f"'{material}'",
                'tipologia_sigla': "'ogtm'"
            }
            
            existing = db_manager.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
            
            if not existing:
                db_manager.insert_values_to_db('PYARCHINIT_THESAURUS_SIGLE', data)
                inserted += 1
                print(f"  Inserted: {material}")
            else:
                print(f"  Already exists: {material}")
                
        except Exception as e:
            print(f"  Error inserting {material}: {str(e)}")
    
    # Insert vocabularies for materials table fields (macc)
    print("\nInserting TMA vocabularies for macc field...")
    for material, note in zip(materials, notes):
        try:
            data = {
                'nome_tabella': 'TMA materiali ripetibili',
                'sigla': '',
                'sigla_estesa': material,
                'descrizione': note,
                'tipologia_sigla': 'macc',
                'lingua': 'it'
            }
            
            # Check if already exists
            search_dict = {
                'nome_tabella': "'TMA materiali ripetibili'",
                'sigla_estesa': f"'{material}'",
                'tipologia_sigla': "'macc'"
            }
            
            existing = db_manager.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
            
            if not existing:
                db_manager.insert_values_to_db('PYARCHINIT_THESAURUS_SIGLE', data)
                inserted += 1
                print(f"  Inserted: {material}")
            else:
                print(f"  Already exists: {material}")
                
        except Exception as e:
            print(f"  Error inserting {material}: {str(e)}")
    
    # Insert additional vocabularies for macl (class)
    print("\nInserting additional vocabularies for macl field...")
    macl_values = [
        # Ceramica classes
        ('ceramica comune', ''),
        ('ceramica fine', ''),
        ('ceramica da cucina', ''),
        ('ceramica da mensa', ''),
        ('anfore', ''),
        ('lucerne', ''),
        # Vetro classes
        ('vetro da finestra', ''),
        ('vetro da mensa', ''),
        ('vetro decorativo', ''),
        # Metallo classes
        ('monete', ''),
        ('oggetti di ornamento', ''),
        ('utensili', ''),
        ('armi', ''),
        # Osso classes
        ('oggetti lavorati', ''),
        ('resti faunistici', ''),
        ('strumenti', '')
    ]
    
    for value, desc in macl_values:
        try:
            data = {
                'nome_tabella': 'TMA materiali ripetibili',
                'sigla': '',
                'sigla_estesa': value,
                'descrizione': desc,
                'tipologia_sigla': 'macl',
                'lingua': 'it'
            }
            
            # Check if already exists
            search_dict = {
                'nome_tabella': "'TMA materiali ripetibili'",
                'sigla_estesa': f"'{value}'",
                'tipologia_sigla': "'macl'"
            }
            
            existing = db_manager.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
            
            if not existing:
                db_manager.insert_values_to_db('PYARCHINIT_THESAURUS_SIGLE', data)
                inserted += 1
                print(f"  Inserted: {value}")
                
        except Exception as e:
            print(f"  Error inserting {value}: {str(e)}")
    
    # Insert additional vocabularies for macd (definition)
    print("\nInserting additional vocabularies for macd field...")
    macd_values = [
        # Ceramica definitions
        'piatto', 'ciotola', 'coppa', 'brocca', 'olla', 'pentola',
        'tegola', 'mattone',
        # Metallo definitions
        'fibula', 'anello', 'bracciale', 'chiodo', 'lama',
        # Vetro definitions
        'bottiglia', 'bicchiere', 'perla',
        # Osso definitions
        'ago', 'spillone', 'pettine'
    ]
    
    for value in macd_values:
        try:
            data = {
                'nome_tabella': 'TMA materiali ripetibili',
                'sigla': '',
                'sigla_estesa': value,
                'descrizione': '',
                'tipologia_sigla': 'macd',
                'lingua': 'it'
            }
            
            # Check if already exists
            search_dict = {
                'nome_tabella': "'TMA materiali ripetibili'",
                'sigla_estesa': f"'{value}'",
                'tipologia_sigla': "'macd'"
            }
            
            existing = db_manager.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
            
            if not existing:
                db_manager.insert_values_to_db('PYARCHINIT_THESAURUS_SIGLE', data)
                inserted += 1
                print(f"  Inserted: {value}")
                
        except Exception as e:
            print(f"  Error inserting {value}: {str(e)}")
    
    # Insert additional vocabularies for macp (typological specification)
    print("\nInserting additional vocabularies for macp field...")
    macp_values = [
        # Ceramic types
        'sigillata italica', 'sigillata africana', 'vernice nera',
        'pareti sottili', 'terra sigillata',
        # Glass types
        'vetro soffiato', 'vetro pressato', 'vetro mosaico',
        # Metal types
        'bronzo', 'ferro', 'argento', 'oro', 'piombo', 'rame'
    ]
    
    for value in macp_values:
        try:
            data = {
                'nome_tabella': 'TMA materiali ripetibili',
                'sigla': '',
                'sigla_estesa': value,
                'descrizione': '',
                'tipologia_sigla': 'macp',
                'lingua': 'it'
            }
            
            # Check if already exists
            search_dict = {
                'nome_tabella': "'TMA materiali ripetibili'",
                'sigla_estesa': f"'{value}'",
                'tipologia_sigla': "'macp'"
            }
            
            existing = db_manager.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
            
            if not existing:
                db_manager.insert_values_to_db('PYARCHINIT_THESAURUS_SIGLE', data)
                inserted += 1
                print(f"  Inserted: {value}")
                
        except Exception as e:
            print(f"  Error inserting {value}: {str(e)}")
    
    print(f"\nTotal records inserted: {inserted}")
    
    # Verify insertion
    try:
        search_dict = {
            'nome_tabella': "'tma_materiali_archeologici'"
        }
        tma_main_records = db_manager.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        
        search_dict = {
            'nome_tabella': "'TMA materiali ripetibili'"
        }
        tma_materials_records = db_manager.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
        
        print(f"\nVerification:")
        print(f"  TMA main table vocabularies: {len(tma_main_records)}")
        print(f"  TMA materials table vocabularies: {len(tma_materials_records)}")
        
    except Exception as e:
        print(f"Error verifying insertion: {str(e)}")

if __name__ == "__main__":
    print("Inserting TMA vocabularies into PyArchInit thesaurus...")
    insert_tma_vocabularies()
    print("\nScript completed!")