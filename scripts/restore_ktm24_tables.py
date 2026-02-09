#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per ripristinare le tabelle mancanti nel database ktm24.sqlite
"""

import sqlite3
import os
import sys
from datetime import datetime

def restore_missing_tables(db_path):
    """Ripristina tutte le tabelle che esistono solo come backup"""
    
    print(f"\n{'='*60}")
    print(f"Ripristino tabelle mancanti in: {os.path.basename(db_path)}")
    print(f"{'='*60}\n")
    
    if not os.path.exists(db_path):
        print(f"✗ Database non trovato: {db_path}")
        return False
    
    # Crea backup prima di modificare
    backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    import shutil
    shutil.copy2(db_path, backup_path)
    print(f"✓ Backup creato: {backup_path}\n")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Lista delle tabelle da ripristinare
    tables_to_restore = {
        'inventario_materiali_table': 'inventario_materiali_table_backup_1760016525',  # usa il più recente
        'pyarchinit_quote': 'pyarchinit_quote_backup_1760015737',
        'pyarchinit_quote_usm': 'pyarchinit_quote_usm_backup_1760015738',
        'pyarchinit_us_negative_doc': 'pyarchinit_us_negative_doc_backup_1760015738',
        'pyunitastratigrafiche': 'pyunitastratigrafiche_backup_1760015738',
        'pyunitastratigrafiche_usm': 'pyunitastratigrafiche_usm_backup_1760015738',
        'tomba_table': 'tomba_table_backup_1760016525',  # usa il più recente
        'us_table_toimp': 'us_table_toimp_backup_1760015737'
    }
    
    restored = []
    errors = []
    
    for target_table, backup_table in tables_to_restore.items():
        # Verifica se la tabella target già esiste
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=?
        """, (target_table,))
        
        if cursor.fetchone():
            print(f"⚠ Tabella {target_table} già esiste, skip")
        else:
            # Verifica che il backup esista
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name=?
            """, (backup_table,))
            
            if cursor.fetchone():
                try:
                    # Ripristina la tabella
                    print(f"Ripristino {target_table} da {backup_table}...")
                    cursor.execute(f"CREATE TABLE {target_table} AS SELECT * FROM {backup_table}")
                    restored.append(target_table)
                    print(f"✓ {target_table} ripristinata con successo")
                except Exception as e:
                    errors.append(f"{target_table}: {e}")
                    print(f"✗ Errore ripristinando {target_table}: {e}")
            else:
                print(f"✗ Backup {backup_table} non trovato")
    
    # Commit delle modifiche
    conn.commit()
    
    print(f"\n{'='*60}")
    print(f"Riepilogo:")
    print(f"- Tabelle ripristinate: {len(restored)}")
    if restored:
        for table in restored:
            print(f"  ✓ {table}")
    
    if errors:
        print(f"\n- Errori: {len(errors)}")
        for error in errors:
            print(f"  ✗ {error}")
    
    print(f"{'='*60}\n")
    
    conn.close()
    return len(restored) > 0

if __name__ == "__main__":
    db_path = "/Users/enzo/pyarchinit/pyarchinit_DB_folder/ktm24.sqlite"
    if restore_missing_tables(db_path):
        print("✓ Ripristino completato con successo!")
        print("\nOra il database dovrebbe funzionare correttamente in PyArchInit.")
    else:
        print("⚠ Nessuna tabella ripristinata.")