#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per rimuovere le virgolette extra nel thesaurus
"""

import os
import sys

def fix_thesaurus_quotes(file_path):
    """Rimuove le virgolette extra nei parametri del thesaurus."""
    print(f"Rimozione virgolette extra in: {file_path}")
    
    # Leggi il file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    backup_path = file_path + '.backup_quotes_fix'
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Backup creato: {backup_path}")
    
    # Fix 1: Rimuovi quotes da nome_tabella
    content = content.replace(
        "'nome_tabella': \"'\" + table_name + \"'\"",
        "'nome_tabella': table_name"
    )
    
    # Fix 2: Rimuovi quotes da tipologia_sigla  
    content = content.replace(
        "'tipologia_sigla': \"'\" + thesaurus_map[field_type] + \"'\"",
        "'tipologia_sigla': thesaurus_map[field_type]"
    )
    
    # Fix 3: Sistema anche altre occorrenze simili
    content = content.replace(
        "'nome_tabella': \"'tma_materiali_archeologici'\"",
        "'nome_tabella': 'tma_materiali_archeologici'"
    )
    
    # Fix 4: Sistema load_localita_values e simili
    content = content.replace(
        "'tipologia_sigla': \"'\" + '10.2' + \"'\"",
        "'tipologia_sigla': '10.2'"
    )
    content = content.replace(
        "'tipologia_sigla': \"'\" + '10.3' + \"'\"",
        "'tipologia_sigla': '10.3'"
    )
    content = content.replace(
        "'tipologia_sigla': \"'\" + '10.4' + \"'\"",
        "'tipologia_sigla': '10.4'"
    )
    content = content.replace(
        "'tipologia_sigla': \"'\" + '10.5' + \"'\"",
        "'tipologia_sigla': '10.5'"
    )
    
    # Scrivi il file modificato
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ Virgolette rimosse!")
    
    return True

def main():
    # File path
    file_path = "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/tabs/Tma.py"
    
    if not os.path.exists(file_path):
        print(f"File non trovato: {file_path}")
        return 1
    
    print("Rimozione virgolette extra thesaurus")
    print("=" * 60)
    
    if fix_thesaurus_quotes(file_path):
        print("\n✅ Processo completato con successo!")
    else:
        print("\n❌ Processo fallito.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())