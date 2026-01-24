#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to populate thesaurus for Fauna form in English.
Two terms per code for testing purposes.

Run from QGIS Python console or command line with proper DB connection.
"""

import os
import sys

# Add parent directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
plugin_dir = os.path.dirname(script_dir)
sys.path.insert(0, plugin_dir)

from modules.db.pyarchinit_conn_strings import Connection
from modules.db.pyarchinit_db_manager import Pyarchinit_db_management

# Fauna thesaurus entries for English
FAUNA_THESAURUS_EN = {
    # 13.1 - Context
    '13.1': [
        ('CTX1', 'Primary deposit'),
        ('CTX2', 'Secondary deposit'),
    ],
    # 13.2 - Methodology
    '13.2': [
        ('MTH1', 'Manual collection'),
        ('MTH2', 'Sieving'),
    ],
    # 13.3 - Accumulation type
    '13.3': [
        ('ACC1', 'Natural accumulation'),
        ('ACC2', 'Anthropic accumulation'),
    ],
    # 13.4 - Deposition
    '13.4': [
        ('DEP1', 'Primary deposition'),
        ('DEP2', 'Secondary deposition'),
    ],
    # 13.5 - Fragmentation
    '13.5': [
        ('FRG1', 'Complete'),
        ('FRG2', 'Fragmented'),
    ],
    # 13.6 - Conservation
    '13.6': [
        ('CON1', 'Good'),
        ('CON2', 'Poor'),
    ],
    # 13.7 - Reliability
    '13.7': [
        ('REL1', 'High reliability'),
        ('REL2', 'Low reliability'),
    ],
    # 13.8 - Combustion
    '13.8': [
        ('CMB1', 'Present'),
        ('CMB2', 'Absent'),
    ],
    # 13.9 - Combustion type
    '13.9': [
        ('TCM1', 'Carbonized'),
        ('TCM2', 'Calcined'),
    ],
    # 13.10 - Anatomical connection
    '13.10': [
        ('ANC1', 'In connection'),
        ('ANC2', 'Disarticulated'),
    ],
    # 13.11 - Species (for tableWidget)
    '13.11': [
        ('BT', 'Bos taurus'),
        ('OA', 'Ovis aries'),
    ],
    # 13.12 - PSI (for tableWidget)
    '13.12': [
        ('PSI1', 'Adult'),
        ('PSI2', 'Juvenile'),
    ],
    # 13.13 - Anatomical element (for tableWidget)
    '13.13': [
        ('FEM', 'Femur'),
        ('HUM', 'Humerus'),
    ],
}


def populate_thesaurus():
    """Populate thesaurus table with Fauna terms in English"""

    # Get database connection
    conn = Connection()
    conn_str = conn.conn_str()

    try:
        db_manager = Pyarchinit_db_management(conn_str)
        db_manager.connection()

        print("Connected to database successfully")
        print("=" * 60)

        inserted_count = 0

        for tipologia_sigla, terms in FAUNA_THESAURUS_EN.items():
            print(f"\nProcessing code {tipologia_sigla}:")

            for sigla, sigla_estesa in terms:
                # Check if entry already exists
                search_dict = {
                    'tipologia_sigla': f"'{tipologia_sigla}'",
                    'sigla': f"'{sigla}'",
                    'lingua': "'en'"
                }

                existing = db_manager.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')

                if existing:
                    print(f"  - {sigla} ({sigla_estesa}) - already exists, skipping")
                    continue

                # Insert new entry
                new_id = db_manager.max_num_id('PYARCHINIT_THESAURUS_SIGLE', 'id_thesaurus_sigle') + 1
                data = db_manager.insert_values_thesaurus(
                    new_id,             # id_thesaurus_sigle
                    'fauna_table',      # nome_tabella
                    sigla,              # sigla
                    sigla_estesa,       # sigla_estesa
                    '',                 # descrizione
                    tipologia_sigla,    # tipologia_sigla
                    'en'                # lingua
                )

                print(f"  + {sigla} ({sigla_estesa}) - inserted")
                inserted_count += 1

        print("\n" + "=" * 60)
        print(f"Total entries inserted: {inserted_count}")
        print("Done! Restart QGIS to see the changes in Fauna form.")

    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == '__main__':
    populate_thesaurus()
