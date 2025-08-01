#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per aggiungere debug dettagliato alle query thesaurus
"""

import os
import sys
import re

def add_thesaurus_debug(file_path):
    """Aggiunge debug alle query thesaurus."""
    print(f"Aggiunta debug thesaurus in: {file_path}")
    
    # Leggi il file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    backup_path = file_path + '.backup_thesaurus_debug'
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Backup creato: {backup_path}")
    
    # Trova load_thesaurus_values e aggiungi più debug
    pattern = r"(thesaurus_records = self\.DB_MANAGER\.query_bool\(search_dict, 'PYARCHINIT_THESAURUS_SIGLE'\))"
    
    debug_code = """# DEBUG: Log the exact query
            QgsMessageLog.logMessage(f"DEBUG TMA thesaurus query: search_dict = {search_dict}", "PyArchInit", Qgis.Info)
            QgsMessageLog.logMessage(f"DEBUG TMA thesaurus: lang = '{lang}', type = {type(lang)}", "PyArchInit", Qgis.Info)
            QgsMessageLog.logMessage(f"DEBUG TMA thesaurus: table_name = '{table_name}', type = {type(table_name)}", "PyArchInit", Qgis.Info)
            QgsMessageLog.logMessage(f"DEBUG TMA thesaurus: tipologia_sigla = '{thesaurus_map[field_type]}', type = {type(thesaurus_map[field_type])}", "PyArchInit", Qgis.Info)
            
            thesaurus_records = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
            
            # DEBUG: Check what was returned
            QgsMessageLog.logMessage(f"DEBUG TMA thesaurus result: type = {type(thesaurus_records)}, len = {len(thesaurus_records) if thesaurus_records else 0}", "PyArchInit", Qgis.Info)"""
    
    content = re.sub(pattern, debug_code, content)
    
    # Aggiungi debug anche nel db_manager per query_bool
    print("\n✓ Aggiunto debug in load_thesaurus_values")
    
    # Scrivi il file modificato
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def add_db_manager_debug(file_path):
    """Aggiunge debug nel db_manager."""
    print(f"\nAggiunta debug in: {file_path}")
    
    # Leggi il file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Trova query_bool e aggiungi debug
    pattern = r"(def query_bool\(self, params, table_class_str\):)"
    
    debug_code = r"""\1
        # DEBUG TMA
        if table_class_str == 'PYARCHINIT_THESAURUS_SIGLE':
            print(f"DEBUG query_bool TMA: params = {params}")
            print(f"DEBUG query_bool TMA: table_class_str = {table_class_str}")"""
    
    content = re.sub(pattern, debug_code, content)
    
    # Trova dove viene costruita la query
    pattern2 = r"(query_str = \"session\.query\(\" \+ table_class_str \+ \"\)\")"
    debug_code2 = r"""print(f"DEBUG query_bool: Building query for {table_class_str}")
        \1
        print(f"DEBUG query_bool: query_str = {query_str}")"""
    
    content = re.sub(pattern2, debug_code2, content)
    
    # Scrivi il file modificato
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ Aggiunto debug in query_bool")
    
    return True

def main():
    # File paths
    tma_path = "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/tabs/Tma.py"
    db_manager_path = "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/modules/db/pyarchinit_db_manager.py"
    
    print("Aggiunta debug dettagliato thesaurus")
    print("=" * 60)
    
    if os.path.exists(tma_path):
        add_thesaurus_debug(tma_path)
    else:
        print(f"File non trovato: {tma_path}")
    
    if os.path.exists(db_manager_path):
        add_db_manager_debug(db_manager_path)
    else:
        print(f"File non trovato: {db_manager_path}")
    
    print("\n✅ Debug aggiunto!")
    print("\nRiavvia QGIS e controlla:")
    print("1. I log nella console Python (Plugins → Python Console)")
    print("2. I messaggi nel pannello dei log")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())