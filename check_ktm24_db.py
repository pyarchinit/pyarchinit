#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per verificare lo stato del database ktm24.sqlite
"""

import sqlite3
import os

def check_database(db_path):
    """Verifica lo stato del database"""
    if not os.path.exists(db_path):
        print(f"Database non trovato: {db_path}")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"\nAnalisi database: {os.path.basename(db_path)}")
    print("=" * 60)
    
    # Ottieni tutte le tabelle
    cursor.execute("""
        SELECT name, type FROM sqlite_master 
        WHERE type IN ('table', 'view') 
        ORDER BY type, name
    """)
    
    all_items = cursor.fetchall()
    tables = [(name, type_) for name, type_ in all_items if type_ == 'table' and not name.startswith('idx_') and not name.startswith('sqlite_')]
    views = [(name, type_) for name, type_ in all_items if type_ == 'view']
    
    # Cerca backup
    backup_tables = {}
    main_tables = []
    
    for name, _ in tables:
        if '_backup_' in name:
            main_name = name.split('_backup_')[0]
            if main_name not in backup_tables:
                backup_tables[main_name] = []
            backup_tables[main_name].append(name)
        else:
            main_tables.append(name)
    
    print("\n📊 TABELLE PRINCIPALI:")
    for table in sorted(main_tables):
        print(f"  ✓ {table}")
    
    print(f"\n🔄 TABELLE CON BACKUP (ma senza tabella principale):")
    missing_main_tables = []
    for main_name, backups in sorted(backup_tables.items()):
        if main_name not in main_tables:
            missing_main_tables.append(main_name)
            print(f"  ❌ {main_name} - MANCANTE! (backup: {', '.join(backups)})")
    
    print(f"\n📋 TABELLE PRINCIPALI CON BACKUP:")
    for main_name, backups in sorted(backup_tables.items()):
        if main_name in main_tables:
            print(f"  ✓ {main_name} (backup: {', '.join(backups)})")
    
    # Controlla tabelle critiche
    critical_tables = ['us_table', 'tomba_table', 'pyunitastratigrafiche', 'pyunitastratigrafiche_usm']
    print(f"\n🔍 CONTROLLO TABELLE CRITICHE:")
    for table in critical_tables:
        if table in main_tables:
            print(f"  ✓ {table} - OK")
        elif table in backup_tables:
            print(f"  ⚠️  {table} - SOLO BACKUP!")
        else:
            print(f"  ❌ {table} - MANCANTE COMPLETAMENTE")
    
    # Suggerimenti
    if missing_main_tables:
        print(f"\n💡 AZIONE RICHIESTA:")
        print(f"  Il database ha {len(missing_main_tables)} tabelle che esistono solo come backup.")
        print(f"  L'updater automatico dovrebbe ripristinarle alla connessione.")
        print(f"  Se non succede, esegui manualmente il ripristino.")
    
    conn.close()

if __name__ == "__main__":
    # Percorso del database
    db_path = "/Users/enzo/pyarchinit/pyarchinit_DB_folder/ktm24.sqlite"
    check_database(db_path)