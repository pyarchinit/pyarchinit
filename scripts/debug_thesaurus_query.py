#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per debuggare le query del thesaurus
"""

import sqlite3
import sys

def debug_thesaurus(db_path):
    """Debug delle query thesaurus."""
    print("Debug query thesaurus")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Verifica contenuto tabella thesaurus
        print("\n1. Verifica contenuto thesaurus:")
        cursor.execute("SELECT COUNT(*) FROM pyarchinit_thesaurus_sigle")
        count = cursor.fetchone()[0]
        print(f"   Record totali nel thesaurus: {count}")
        
        # 2. Verifica record per TMA
        print("\n2. Record per tma_materiali_archeologici:")
        cursor.execute("""
            SELECT tipologia_sigla, COUNT(*) as cnt
            FROM pyarchinit_thesaurus_sigle
            WHERE nome_tabella = 'tma_materiali_archeologici'
            GROUP BY tipologia_sigla
            ORDER BY tipologia_sigla
        """)
        
        for row in cursor.fetchall():
            print(f"   Tipo {row[0]}: {row[1]} record")
        
        # 3. Verifica con lingua IT
        print("\n3. Record con lingua IT:")
        cursor.execute("""
            SELECT tipologia_sigla, COUNT(*) as cnt
            FROM pyarchinit_thesaurus_sigle
            WHERE nome_tabella = 'tma_materiali_archeologici'
              AND lingua = 'IT'
            GROUP BY tipologia_sigla
        """)
        
        for row in cursor.fetchall():
            print(f"   Tipo {row[0]}: {row[1]} record")
        
        # 4. Mostra esempi di record
        print("\n4. Esempi di record (primi 5):")
        cursor.execute("""
            SELECT nome_tabella, tipologia_sigla, sigla_estesa, lingua
            FROM pyarchinit_thesaurus_sigle
            WHERE nome_tabella = 'tma_materiali_archeologici'
            LIMIT 5
        """)
        
        for row in cursor.fetchall():
            print(f"   Tabella: {row[0]}, Tipo: {row[1]}, Sigla: {row[2]}, Lingua: {row[3]}")
        
        # 5. Test query esatta come nel codice
        print("\n5. Test query come nel codice Python:")
        test_queries = [
            ("Materiale (10.1)", "tma_materiali_archeologici", "10.1", "IT"),
            ("Categoria (10.7)", "tma_materiali_archeologici", "10.7", "IT"),
        ]
        
        for name, table, tipo, lang in test_queries:
            cursor.execute("""
                SELECT COUNT(*)
                FROM pyarchinit_thesaurus_sigle
                WHERE nome_tabella = ?
                  AND tipologia_sigla = ?
                  AND lingua = ?
            """, (table, tipo, lang))
            
            count = cursor.fetchone()[0]
            print(f"   {name}: {count} record")
            
            if count > 0:
                cursor.execute("""
                    SELECT sigla_estesa
                    FROM pyarchinit_thesaurus_sigle
                    WHERE nome_tabella = ?
                      AND tipologia_sigla = ?
                      AND lingua = ?
                    LIMIT 3
                """, (table, tipo, lang))
                
                for row in cursor.fetchall():
                    print(f"      - {row[0]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Errore: {e}")
        import traceback
        traceback.print_exc()

def main():
    db_path = "/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite"
    
    debug_thesaurus(db_path)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())