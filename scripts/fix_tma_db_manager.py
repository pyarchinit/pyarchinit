#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per correggere insert_tma_values in pyarchinit_db_manager.py
"""

import os
import sys
import re

def fix_db_manager(file_path):
    """Corregge il metodo insert_tma_values."""
    print(f"Correzione insert_tma_values in: {file_path}")
    
    # Leggi il file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    backup_path = file_path + '.backup_fix_insert'
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Backup creato: {backup_path}")
    
    # Trova e correggi insert_tma_values
    old_method = """    def insert_tma_values(self, *arg):
        \"\"\"Istanzia la classe TMA da pyarchinit_db_mapper\"\"\"
        tma = TMA(arg[0],  # id
                  arg[1],  # sito
                  arg[2],  # area
                  arg[3],  # ogtm
                  arg[4],  # ldct
                  arg[5],  # ldcn
                  arg[6],  # vecchia_collocazione
                  arg[7],  # cassetta
                  arg[8],  # scan
                  arg[9],  # saggio
                  arg[10], # vano_locus
                  arg[11], # dscd
                  arg[12], # dscu
                  arg[13], # rcgd
                  arg[14], # rcgz
                  arg[15], # aint
                  arg[16], # aind
                  arg[17], # dtzg
                  arg[18], # deso
                  arg[19], # nsc
                  arg[20], # ftap
                  arg[21], # ftan
                  arg[22], # drat
                  arg[23], # dran
                  arg[24], # draa
                  arg[25], # created_at
                  arg[26], # updated_at
                  arg[27], # created_by
                  arg[28]) # updated_by

        return tma"""
    
    new_method = """    def insert_tma_values(self, *arg):
        \"\"\"Istanzia la classe TMA da pyarchinit_db_mapper\"\"\"
        tma = TMA(arg[0],  # id
                  arg[1],  # sito
                  arg[2],  # area
                  arg[3],  # localita
                  arg[4],  # settore
                  arg[5],  # ogtm
                  arg[6],  # ldct
                  arg[7],  # ldcn
                  arg[8],  # vecchia_collocazione
                  arg[9],  # cassetta
                  arg[10], # scan
                  arg[11], # saggio
                  arg[12], # vano_locus
                  arg[13], # dscd
                  arg[14], # dscu
                  arg[15], # rcgd
                  arg[16], # rcgz
                  arg[17], # aint
                  arg[18], # aind
                  arg[19], # dtzg
                  arg[20], # deso
                  arg[21], # nsc
                  arg[22], # ftap
                  arg[23], # ftan
                  arg[24], # drat
                  arg[25], # dran
                  arg[26], # draa
                  arg[27], # created_at
                  arg[28], # updated_at
                  arg[29], # created_by
                  arg[30]) # updated_by

        return tma"""
    
    content = content.replace(old_method, new_method)
    
    # Scrivi il file modificato
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ insert_tma_values corretto!")
    
    return True

def main():
    # File path
    file_path = "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/modules/db/pyarchinit_db_manager.py"
    
    if not os.path.exists(file_path):
        print(f"File non trovato: {file_path}")
        return 1
    
    print("Correzione insert_tma_values")
    print("=" * 60)
    
    if fix_db_manager(file_path):
        print("\n✅ Processo completato con successo!")
    else:
        print("\n❌ Processo fallito.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())