#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per verificare i tipi di campo nelle tabelle e view
"""

import sqlite3
import os

def check_field_types(db_path):
    """Verifica i tipi di campo in tabelle e view"""
    
    print(f"\nVerifica tipi di campo in: {os.path.basename(db_path)}")
    print("="*60)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Tabelle da verificare
    tables_to_check = [
        'us_table',
        'pyunitastratigrafiche', 
        'pyunitastratigrafiche_usm',
        'pyarchinit_quote',
        'pyarchinit_quote_usm',
        'inventario_materiali_table',
        'tomba_table'
    ]
    
    print("\n📋 VERIFICA CAMPI CRITICI:")
    print(f"{'Tabella/View':<30} {'Campo':<15} {'Tipo':<15} {'Status':<20}")
    print("-"*80)
    
    for table in tables_to_check:
        # Verifica se esiste come tabella o view
        cursor.execute("""
            SELECT type FROM sqlite_master 
            WHERE name=? AND type IN ('table', 'view')
        """, (table,))
        
        result = cursor.fetchone()
        if not result:
            print(f"{table:<30} {'---':<15} {'---':<15} {'NON TROVATA':<20}")
            continue
            
        object_type = result[0]
        
        # Ottieni info colonne
        try:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
        except Exception as e:
            print(f"{table:<30} {'---':<15} {'---':<15} {'ERRORE LETTURA':<20}")
            continue
        
        # Campi critici da verificare
        critical_fields = ['area', 'us', 'the_geom']
        
        for col in columns:
            col_name = col[1]
            col_type = col[2]
            
            if col_name in critical_fields:
                # Determina lo stato
                if col_name in ['area', 'us']:
                    expected = 'TEXT'
                    if col_type == 'TEXT':
                        status = '✓ OK'
                    else:
                        status = f'❌ ERRORE (dovrebbe essere TEXT)'
                elif col_name == 'the_geom':
                    if col_type in ['BLOB', 'GEOMETRY']:
                        status = '✓ OK'
                    else:
                        status = f'❌ ERRORE (è {col_type}, dovrebbe essere BLOB)'
                else:
                    status = ''
                    
                print(f"{table:<30} {col_name:<15} {col_type:<15} {status:<20}")
    
    # Verifica view problematiche
    print("\n\n🔍 ANALISI VIEW CON CAST:")
    
    problem_views = [
        'pyarchinit_quote',
        'pyunitastratigrafiche',
        'pyunitastratigrafiche_usm',
        'pyarchinit_quote_usm'
    ]
    
    for view_name in problem_views:
        cursor.execute("""
            SELECT sql FROM sqlite_master 
            WHERE type='view' AND name=?
        """, (view_name,))
        
        result = cursor.fetchone()
        if result and result[0]:
            sql = result[0]
            if 'CAST(' in sql:
                print(f"\n❌ VIEW {view_name} contiene CAST:")
                # Estrai i CAST
                import re
                casts = re.findall(r'CAST\([^)]+\)', sql)
                for cast in casts:
                    print(f"   - {cast}")
            else:
                print(f"\n✓ VIEW {view_name} - Nessun CAST trovato")
    
    conn.close()

if __name__ == "__main__":
    db_path = "/Users/enzo/pyarchinit/pyarchinit_DB_folder/ktm24.sqlite"
    check_field_types(db_path)