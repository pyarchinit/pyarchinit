#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per testare l'inserimento diretto con SQL
"""

import sqlite3
import sys

def test_direct_insert(db_path):
    """Test inserimento diretto con SQL."""
    print("Test inserimento diretto TMA")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verifica record esistenti
        cursor.execute("SELECT COUNT(*) FROM tma_materiali_archeologici")
        count_before = cursor.fetchone()[0]
        print(f"\nRecord prima dell'inserimento: {count_before}")
        
        # Inserisci un record di test
        insert_sql = """
        INSERT INTO tma_materiali_archeologici (
            sito, area, localita, settore, ogtm, ldct, ldcn,
            vecchia_collocazione, cassetta, scan, saggio, vano_locus,
            dscd, dscu, rcgd, rcgz, aint, aind, dtzg, deso, nsc,
            ftap, ftan, drat, dran, draa,
            created_at, updated_at, created_by, updated_by
        ) VALUES (
            'Test Site SQL', 'Area Test', 'Roma Test', 'Settore Test', '',
            'Collocazione Test', 'Numero Test', '', 'C1', 'SI',
            'Saggio Test', 'Vano Test', 'Descrizione Test', 'US Test',
            'N', 'Note Test', 'SI', '2024', 'I sec. d.C.', 'Descrizione oggetto test',
            '', '', '', '', '', '',
            datetime('now'), datetime('now'), 'test_sql', 'test_sql'
        )
        """
        
        cursor.execute(insert_sql)
        conn.commit()
        
        # Verifica inserimento
        cursor.execute("SELECT COUNT(*) FROM tma_materiali_archeologici")
        count_after = cursor.fetchone()[0]
        print(f"Record dopo l'inserimento: {count_after}")
        
        if count_after > count_before:
            print("\n✅ Inserimento riuscito!")
            
            # Mostra l'ultimo record
            cursor.execute("""
                SELECT id, sito, area, localita, settore 
                FROM tma_materiali_archeologici 
                ORDER BY id DESC 
                LIMIT 1
            """)
            row = cursor.fetchone()
            print(f"\nUltimo record inserito:")
            print(f"  ID: {row[0]}")
            print(f"  Sito: {row[1]}")
            print(f"  Area: {row[2]}")
            print(f"  Località: {row[3]}")
            print(f"  Settore: {row[4]}")
        else:
            print("\n❌ Inserimento fallito!")
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Errore: {e}")
        import traceback
        traceback.print_exc()

def main():
    db_path = "/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite"
    
    test_direct_insert(db_path)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())