#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script di test per verificare la sincronizzazione del thesaurus TMA
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.db.pyarchinit_conn_strings import Connection
from modules.db.pyarchinit_db_manager import Pyarchinit_db_management
from sqlalchemy import text

def test_area_count():
    """Verifica il numero di aree in tutte le tabelle"""
    try:
        conn = Connection()
        db_manager = Pyarchinit_db_management(conn)
        engine = db_manager.engine
        session = engine.connect()
        
        tables = [
            ('us_table', 'area'),
            ('inventario_materiali_table', 'area'),
            ('tomba_table', 'area'),
            ('individui_table', 'area'),
            ('tma_materiali_archeologici', 'area')
        ]
        
        print("\n=== CONTEGGIO AREE PER TABELLA ===")
        total_areas = set()
        
        for table_name, field_name in tables:
            try:
                # Count distinct areas
                query = text(f"""
                    SELECT COUNT(DISTINCT {field_name}) as count, 
                           GROUP_CONCAT(DISTINCT {field_name}) as areas
                    FROM {table_name} 
                    WHERE {field_name} IS NOT NULL 
                    AND {field_name} != ''
                """)
                
                result = session.execute(query)
                row = result.fetchone()
                count = row[0] if row else 0
                areas_str = row[1] if row and row[1] else ""
                
                print(f"\n{table_name}:")
                print(f"  Numero aree distinte: {count}")
                
                if areas_str:
                    areas_list = [a.strip() for a in areas_str.split(',')]
                    total_areas.update(areas_list)
                    print(f"  Aree: {', '.join(sorted(areas_list[:10]))}")
                    if len(areas_list) > 10:
                        print(f"  ... e altre {len(areas_list) - 10} aree")
                        
            except Exception as e:
                print(f"  Errore: {str(e)}")
                
        print(f"\n=== TOTALE AREE UNICHE: {len(total_areas)} ===")
        
        # Check thesaurus
        try:
            query = text("""
                SELECT COUNT(DISTINCT sigla) as count
                FROM pyarchinit_thesaurus_sigle
                WHERE nome_tabella = 'TMA materiali archeologici'
                AND tipologia_sigla = 'area'
            """)
            
            result = session.execute(query)
            thesaurus_count = result.scalar()
            
            print(f"\n=== AREE NEL THESAURUS TMA: {thesaurus_count} ===")
            
            # Show some examples
            query = text("""
                SELECT sigla, sigla_estesa, descrizione
                FROM pyarchinit_thesaurus_sigle
                WHERE nome_tabella = 'TMA materiali archeologici'
                AND tipologia_sigla = 'area'
                ORDER BY sigla
                LIMIT 10
            """)
            
            result = session.execute(query)
            print("\nPrime 10 aree nel thesaurus:")
            for row in result:
                desc = f" - {row[2]}" if row[2] else ""
                print(f"  {row[0]} ({row[1]}){desc}")
                
        except Exception as e:
            print(f"\nErrore accesso thesaurus: {str(e)}")
            
        session.close()
        
    except Exception as e:
        print(f"Errore generale: {str(e)}")

if __name__ == "__main__":
    test_area_count()