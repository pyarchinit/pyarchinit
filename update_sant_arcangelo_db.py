#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script specifico per aggiornare il database Sant_Arcangelo_La_Pieve94_3004.sqlite
"""

import os
import sys
import shutil

# Aggiungi il percorso di PyArchInit al path
plugin_dir = os.path.dirname(os.path.abspath(__file__))
if plugin_dir not in sys.path:
    sys.path.append(plugin_dir)

# Importa l'updater
from scripts.update_old_sqlite_db import PyArchInitDBUpdater

def main():
    """Aggiorna il database Sant_Arcangelo_La_Pieve94_3004.sqlite"""
    
    # Percorso del database
    db_folder = "/Users/enzo/pyarchinit/pyarchinit_DB_folder"
    db_name = "Sant_Arcangelo_La_Pieve94_3004.sqlite"
    db_path = os.path.join(db_folder, db_name)
    
    print("\n" + "="*60)
    print("Aggiornamento Database PyArchInit")
    print("="*60)
    print(f"\nDatabase: {db_name}")
    print(f"Percorso: {db_path}")
    print("\nQuesto script aggiornerà il database per renderlo compatibile")
    print("con la versione attuale di PyArchInit, includendo:")
    print("- Creazione tabella pyarchinit_thesaurus_sigle")
    print("- Aggiunta colonne mancanti a tutte le tabelle")
    print("- Correzione view dei layer vettoriali")
    print("- Creazione trigger necessari")
    print("\n" + "="*60)
    
    # Verifica che il file esista
    if not os.path.exists(db_path):
        print(f"\n✗ ERRORE: File non trovato: {db_path}")
        return 1
    
    # Procedi automaticamente (o usa un parametro da linea di comando)
    auto_confirm = '--auto' in sys.argv
    if not auto_confirm:
        print("\nUsa --auto per eseguire senza conferma.")
        risposta = 's'  # Per ora procediamo automaticamente
    else:
        risposta = 's'
    
    if risposta.lower() != 's':
        print("\nAggiornamento annullato.")
        return 0
    
    # Crea updater e aggiorna
    updater = PyArchInitDBUpdater(db_path)
    
    try:
        if updater.update_database():
            print("\n✓ Aggiornamento completato con successo!")
            print("\nOra puoi utilizzare il database con PyArchInit.")
            
            # Crea una copia del database aggiornato nel plugin directory
            updated_copy = os.path.join(plugin_dir, f"{db_name}.updated")
            shutil.copy2(db_path, updated_copy)
            print(f"\n✓ Copia del database aggiornato salvata in:")
            print(f"  {updated_copy}")
            
            return 0
        else:
            print("\n✗ Aggiornamento fallito.")
            return 1
            
    except Exception as e:
        print(f"\n✗ Errore durante l'aggiornamento: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())