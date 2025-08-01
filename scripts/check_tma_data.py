#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per verificare i dati salvati nelle tabelle TMA
"""

import sqlite3
import sys

def check_tma_data(db_path):
    """Verifica i dati nelle tabelle TMA."""
    print(f"Verifica dati TMA in: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Verifica tma_materiali_archeologici
        print("\n1. Controllo tabella tma_materiali_archeologici:")
        cursor.execute("SELECT COUNT(*) FROM tma_materiali_archeologici")
        count = cursor.fetchone()[0]
        print(f"   Record totali: {count}")
        
        if count > 0:
            print("\n   Ultimi 3 record:")
            cursor.execute("""
                SELECT id, sito, area, localita, settore, ogtm, ldct, ldcn 
                FROM tma_materiali_archeologici 
                ORDER BY id DESC 
                LIMIT 3
            """)
            for row in cursor.fetchall():
                print(f"   ID: {row[0]}, Sito: {row[1]}, Area: {row[2]}")
                print(f"      Località: {row[3]}, Settore: {row[4]}")
                print(f"      OGTM: {row[5]}, LDCT: {row[6]}, LDCN: {row[7]}")
                print()
        
        # 2. Verifica tma_materiali_ripetibili
        print("\n2. Controllo tabella tma_materiali_ripetibili:")
        cursor.execute("SELECT COUNT(*) FROM tma_materiali_ripetibili")
        count_mat = cursor.fetchone()[0]
        print(f"   Record totali: {count_mat}")
        
        if count_mat > 0:
            print("\n   Ultimi 5 materiali:")
            cursor.execute("""
                SELECT id, id_tma, macc, macl, macp, peso 
                FROM tma_materiali_ripetibili 
                ORDER BY id DESC 
                LIMIT 5
            """)
            for row in cursor.fetchall():
                print(f"   ID: {row[0]}, TMA_ID: {row[1]}, Categoria: {row[2]}")
                print(f"      Classe: {row[3]}, Tipo: {row[4]}, Peso: {row[5]}")
        
        # 3. Verifica struttura colonne
        print("\n3. Struttura tabella tma_materiali_archeologici:")
        cursor.execute("PRAGMA table_info(tma_materiali_archeologici)")
        columns = cursor.fetchall()
        
        # Controlla colonne critiche
        column_names = [col[1] for col in columns]
        critical_columns = ['id', 'sito', 'area', 'localita', 'settore', 'created_by', 'updated_by']
        
        for col in critical_columns:
            if col in column_names:
                print(f"   ✓ {col}")
            else:
                print(f"   ✗ {col} MANCANTE!")
        
        # 4. Test query di join
        print("\n4. Test query join TMA + Materiali:")
        cursor.execute("""
            SELECT t.id, t.sito, COUNT(m.id) as n_materiali
            FROM tma_materiali_archeologici t
            LEFT JOIN tma_materiali_ripetibili m ON t.id = m.id_tma
            GROUP BY t.id
            ORDER BY t.id DESC
            LIMIT 3
        """)
        
        for row in cursor.fetchall():
            print(f"   TMA ID: {row[0]}, Sito: {row[1]}, N. Materiali: {row[2]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Errore: {e}")
        import traceback
        traceback.print_exc()

def main():
    db_path = "/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite"
    
    print("Verifica dati TMA")
    print("=" * 60)
    
    check_tma_data(db_path)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())