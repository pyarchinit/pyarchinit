#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per ripristinare le tabelle dai backup nel database PyArchInit
"""

import sqlite3
import sys
import os

def restore_backup_tables(db_path):
    """Ripristina le tabelle principali dai backup"""
    
    print(f"\n{'='*60}")
    print(f"Ripristino tabelle da backup")
    print(f"Database: {os.path.basename(db_path)}")
    print(f"{'='*60}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Lista delle tabelle da ripristinare
        tables_to_restore = {
            'us_table': 'us_table_backup_1760006637',
            'campioni_table': 'campioni_table_backup_1760006637', 
            'inventario_materiali_table': 'inventario_materiali_table_backup_1760006637',
            'pottery_table': 'pottery_table_backup_1760006863',
            'pyarchinit_quote': 'pyarchinit_quote_backup_1760006607',
            'pyarchinit_quote_usm': 'pyarchinit_quote_usm_backup_1760006607',
            'pyarchinit_us_negative_doc': 'pyarchinit_us_negative_doc_backup_1760006607',
            'pyunitastratigrafiche': 'pyunitastratigrafiche_backup_1760006607',
            'pyunitastratigrafiche_usm': 'pyunitastratigrafiche_usm_backup_1760006607',
            'tomba_table': 'tomba_table_backup_1760006637',
            'us_table_toimp': 'us_table_toimp_backup_1760006607'
        }
        
        restored = []
        
        for target_table, backup_table in tables_to_restore.items():
            # Verifica se il backup esiste
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name=?
            """, (backup_table,))
            
            if cursor.fetchone():
                # Verifica se la tabella target esiste già
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name=?
                """, (target_table,))
                
                if cursor.fetchone():
                    print(f"  ⚠ Tabella {target_table} già esiste, skip")
                else:
                    # Crea la tabella copiando la struttura e i dati dal backup
                    print(f"  ✓ Ripristino {target_table} da {backup_table}")
                    cursor.execute(f"CREATE TABLE {target_table} AS SELECT * FROM {backup_table}")
                    restored.append(target_table)
            else:
                print(f"  ⚠ Backup {backup_table} non trovato")
        
        # Commit delle modifiche
        conn.commit()
        
        print(f"\n✓ Ripristinate {len(restored)} tabelle:")
        for table in restored:
            print(f"  - {table}")
            
        conn.close()
        
        return len(restored) > 0
        
    except Exception as e:
        print(f"\n✗ Errore durante il ripristino: {e}")
        return False

def main():
    """Main function"""
    if len(sys.argv) < 2:
        db_path = "/Users/enzo/pyarchinit/pyarchinit_DB_folder/Sant_Arcangelo_La_Pieve94_3004.sqlite"
    else:
        db_path = sys.argv[1]
    
    if not os.path.exists(db_path):
        print(f"✗ Database non trovato: {db_path}")
        return 1
    
    if restore_backup_tables(db_path):
        print("\n✓ Ripristino completato con successo!")
        print("\nOra puoi eseguire nuovamente l'updater per aggiornare le tabelle.")
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())