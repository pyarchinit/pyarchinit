#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per forzare l'aggiornamento del database ktm24.sqlite
"""

import os
import sys

# Aggiungi il percorso di PyArchInit al path
plugin_dir = os.path.dirname(os.path.abspath(__file__))
if plugin_dir not in sys.path:
    sys.path.append(plugin_dir)

from modules.db.sqlite_db_updater import SQLiteDBUpdater

def main():
    """Forza l'aggiornamento del database ktm24.sqlite"""
    
    db_path = "/Users/enzo/pyarchinit/pyarchinit_DB_folder/ktm24.sqlite"
    
    print(f"\n{'='*60}")
    print(f"Aggiornamento forzato database ktm24.sqlite")
    print(f"{'='*60}\n")
    
    if not os.path.exists(db_path):
        print(f"✗ Database non trovato: {db_path}")
        return 1
    
    # Crea updater senza parent widget (per uso da command line)
    updater = SQLiteDBUpdater(db_path, parent=None)
    
    # Forza l'aggiornamento bypassando i controlli interattivi
    print("Controllo necessità aggiornamento...")
    if updater.needs_update():
        print("✓ Database necessita aggiornamento")
        print("\nEsecuzione aggiornamento...")
        
        # Modifichiamo temporaneamente il metodo per forzare l'aggiornamento
        # senza richiedere conferma all'utente
        original_check_method = updater.check_and_update_database
        
        def force_update():
            return updater.update_database()
        
        updater.check_and_update_database = force_update
        
        if updater.check_and_update_database():
            print("\n✓ Aggiornamento completato con successo!")
        else:
            print("\n✗ Aggiornamento fallito")
            return 1
    else:
        print("✓ Database già aggiornato")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())