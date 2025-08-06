#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script per trovare il database PyArchInit corretto
"""

import os
import glob

home = os.path.expanduser("~")
print(f"Cercando database PyArchInit nella home: {home}")
print("=" * 80)

# Cerca in specifiche directory
search_paths = [
    os.path.join(home, "pyarchinit"),
    os.path.join(home, "pyarchinit_DB_folder"),
    os.path.join(home, "pyarchinit", "pyarchinit_DB_folder"),
    os.path.join(home, ".pyarchinit"),
    os.path.join(home, "Documents", "pyarchinit"),
]

found_dbs = []

for path in search_paths:
    if os.path.exists(path):
        print(f"\nCercando in: {path}")
        # Cerca file .sqlite
        pattern = os.path.join(path, "*.sqlite")
        files = glob.glob(pattern)
        if files:
            print(f"  Trovati {len(files)} file .sqlite:")
            for f in files:
                size = os.path.getsize(f) / 1024 / 1024  # MB
                print(f"    - {os.path.basename(f)} ({size:.1f} MB)")
                found_dbs.append(f)

# Cerca il file menzionato dall'utente
specific_db = os.path.join(home, "pyarchinit", "ppyarchinit_Db_folder", "pyarchinitdddd.sqlite")
if os.path.exists(specific_db):
    print(f"\nTROVATO IL DATABASE SPECIFICATO: {specific_db}")
    size = os.path.getsize(specific_db) / 1024 / 1024
    print(f"  Dimensione: {size:.1f} MB")
else:
    # Prova con variazioni del nome
    variations = [
        "pyarchinit/pyarchinit_DB_folder/pyarchnitDB.sqlite",
        "pyarchinit/pyarchinit_Db_folder/pyarchnitDB.sqlite",
        "pyarchinit/ppyarchinit_Db_folder/pyarchinitdddd.sqlite",
    ]
    for var in variations:
        full_path = os.path.join(home, var)
        if os.path.exists(full_path):
            print(f"\nTROVATO DATABASE: {full_path}")
            size = os.path.getsize(full_path) / 1024 / 1024
            print(f"  Dimensione: {size:.1f} MB")
            found_dbs.append(full_path)

if not found_dbs:
    print("\nNessun database PyArchInit trovato nelle directory standard.")
else:
    print(f"\n\nTOTALE DATABASE TROVATI: {len(found_dbs)}")