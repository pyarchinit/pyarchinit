#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verifica finale di tutti i database PyArchInit
"""

import sqlite3
import os

def verify_database(db_path):
    """Verifica un singolo database"""
    
    print(f"\n{'='*60}")
    print(f"VERIFICA: {os.path.basename(db_path)}")
    print(f"{'='*60}\n")
    
    if not os.path.exists(db_path):
        print(f"⚠ Database non trovato")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Verifica tabelle principali
    print("📋 CAMPI CRITICI:")
    print(f"{'Tabella':<30} {'Campo':<10} {'Tipo':<15} {'Status':<10}")
    print("-"*70)
    
    tables = [
        'us_table',
        'tomba_table',
        'inventario_materiali_table',
        'pottery_table',
        'campioni_table',
        'pyarchinit_us_negative_doc'
    ]
    
    all_ok = True
    
    for table in tables:
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
        if cursor.fetchone():
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            
            for col in columns:
                if col[1] in ['area', 'us', 'us_n', 'area_n']:
                    if col[2] == 'TEXT':
                        status = '✓ OK'
                    else:
                        status = f'✗ ERRORE'
                        all_ok = False
                    
                    print(f"{table:<30} {col[1]:<10} {col[2]:<15} {status:<10}")
    
    # Verifica view
    print("\n🔍 VIEW CON CAST:")
    cursor.execute("""
        SELECT name, sql FROM sqlite_master 
        WHERE type='view' AND sql LIKE '%CAST%'
    """)
    
    cast_views = cursor.fetchall()
    if cast_views:
        for view_name, sql in cast_views:
            if 'CAST' in sql.upper() and 'AS INTEGER' in sql.upper():
                print(f"⚠ {view_name} contiene CAST")
                all_ok = False
    else:
        print("✓ Nessuna view con CAST trovata")
    
    # Verifica tabelle principali
    print("\n📐 TABELLE/VIEW PRINCIPALI:")
    main_objects = [
        ('pyarchinit_quote', 'table'),
        ('pyarchinit_quote_usm', 'table'),
        ('pyunitastratigrafiche', 'table'),
        ('pyunitastratigrafiche_usm', 'table'),
        ('pyarchinit_us_view', 'view'),
        ('pyarchinit_usm_view', 'view'),
        ('pyarchinit_quote_view', 'view'),
        ('pyarchinit_us_negative_doc_view', 'view')
    ]
    
    for obj_name, expected_type in main_objects:
        cursor.execute(f"SELECT type FROM sqlite_master WHERE name='{obj_name}'")
        result = cursor.fetchone()
        if result:
            if result[0] == expected_type:
                print(f"✓ {obj_name}: {result[0]}")
            else:
                print(f"✗ {obj_name}: {result[0]} (dovrebbe essere {expected_type})")
                all_ok = False
        else:
            print(f"✗ {obj_name}: NON TROVATA")
            all_ok = False
    
    conn.close()
    
    if all_ok:
        print(f"\n✅ DATABASE OK!")
    else:
        print(f"\n⚠️ DATABASE CON PROBLEMI")
    
    return all_ok


def main():
    """Verifica tutti i database"""
    databases = [
        "/Users/enzo/pyarchinit/pyarchinit_DB_folder/ktm24.sqlite",
        "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/resources/dbfiles/pyarchinit.sqlite",
        "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/resources/dbfiles/pyarchinit_db.sqlite"
    ]
    
    print("VERIFICA COMPLETA DATABASE PYARCHINIT")
    print("="*60)
    
    results = []
    for db_path in databases:
        results.append((db_path, verify_database(db_path)))
    
    print(f"\n{'='*60}")
    print("RIEPILOGO FINALE:")
    print(f"{'='*60}")
    
    for db_path, ok in results:
        status = "✅ OK" if ok else "⚠️ PROBLEMI"
        print(f"{os.path.basename(db_path):<30} {status}")
    
    print(f"{'='*60}")


if __name__ == "__main__":
    main()