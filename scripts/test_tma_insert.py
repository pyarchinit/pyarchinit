#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per testare l'inserimento diretto di un record TMA
"""

import sys
import os
sys.path.insert(0, '/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit')

from modules.db.pyarchinit_db_manager import Pyarchinit_db_management
from modules.db.pyarchinit_conn_strings import Connection
from modules.db.entities.TMA import TMA

def test_insert():
    """Testa l'inserimento di un record TMA."""
    print("Test inserimento TMA")
    print("=" * 60)
    
    # Connessione al database
    conn = Connection()
    conn_str = conn.conn_str()
    
    try:
        db_manager = Pyarchinit_db_management(conn_str)
        db_manager.connection()
        
        # Crea un record TMA di test
        print("\n1. Creazione record TMA di test...")
        
        # Ottieni il prossimo ID
        max_id = db_manager.max_num_id('TMA', 'id')
        next_id = 1 if max_id is None else max_id + 1
        
        print(f"   Prossimo ID: {next_id}")
        
        # Crea l'oggetto TMA con tutti i parametri richiesti
        tma_data = db_manager.insert_tma_values(
            next_id,           # id
            'Test Site',       # sito
            'Area 1',          # area
            'Roma',            # localita
            'Settore A',       # settore
            '',                # ogtm
            'Collocazione 1',  # ldct
            'Numero 1',        # ldcn
            '',                # vecchia_collocazione
            'C1',              # cassetta
            'SI',              # scan
            'Saggio 1',        # saggio
            'Vano 1',          # vano_locus
            'Descrizione',     # dscd
            'US 1',            # dscu
            'N',               # rcgd
            'Note',            # rcgz
            'SI',              # aint
            '2024',            # aind
            'I sec. d.C.',     # dtzg
            'Descrizione oggetto',  # deso
            '',                # nsc
            '',                # ftap
            '',                # ftan
            '',                # drat
            '',                # dran
            '',                # draa
            '',                # created_at
            '',                # updated_at
            'test_user',       # created_by
            'test_user'        # updated_by
        )
        
        print("   Oggetto TMA creato")
        
        # Inserisci nel database
        print("\n2. Inserimento nel database...")
        db_manager.insert_data_session(tma_data)
        print("   ✓ Record inserito!")
        
        # Verifica inserimento
        print("\n3. Verifica inserimento...")
        records = db_manager.query('TMA')
        print(f"   Record trovati: {len(records)}")
        
        if records:
            last_record = records[-1]
            print(f"   Ultimo record:")
            print(f"     ID: {last_record.id}")
            print(f"     Sito: {last_record.sito}")
            print(f"     Area: {last_record.area}")
            print(f"     Località: {last_record.localita}")
            print(f"     Settore: {last_record.settore}")
        
    except Exception as e:
        print(f"\n❌ Errore: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_insert()