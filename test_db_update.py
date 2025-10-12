#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script per aggiornare database SQLite di PyArchInit
"""

import sys
import os

# Aggiungi il percorso di PyArchInit al path
plugin_dir = os.path.dirname(os.path.abspath(__file__))
if plugin_dir not in sys.path:
    sys.path.append(plugin_dir)

# Importa l'updater
from scripts.update_old_sqlite_db import PyArchInitDBUpdater

def test_update():
    """Test the database update"""
    # Percorso del database da testare
    db_path = input("Inserisci il percorso completo del database SQLite da aggiornare: ").strip()
    
    if not os.path.exists(db_path):
        print(f"File non trovato: {db_path}")
        return
    
    if not db_path.endswith('.sqlite'):
        print("Il file deve avere estensione .sqlite")
        return
    
    # Crea updater e aggiorna
    updater = PyArchInitDBUpdater(db_path)
    updater.update_database()

if __name__ == "__main__":
    test_update()