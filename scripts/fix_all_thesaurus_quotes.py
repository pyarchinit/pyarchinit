#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per rimuovere TUTTE le virgolette extra nel thesaurus
"""

import os
import sys
import re

def fix_all_quotes(file_path):
    """Rimuove tutte le virgolette extra."""
    print(f"Rimozione di tutte le virgolette extra in: {file_path}")
    
    # Leggi il file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    backup_path = file_path + '.backup_all_quotes_fix'
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Backup creato: {backup_path}")
    
    # Pattern per trovare 'nome_tabella': "'" + ... + "'"
    pattern1 = r"'nome_tabella': \"\'\"\s*\+\s*'tma_materiali_archeologici'\s*\+\s*\"'\""
    replacement1 = "'nome_tabella': 'tma_materiali_archeologici'"
    content = re.sub(pattern1, replacement1, content)
    
    # Pattern per trovare 'tipologia_sigla': "'" + '...' + "'"
    pattern2 = r"'tipologia_sigla': \"\'\"\s*\+\s*'(\d+\.\d+)'\s*\+\s*\"'\""
    replacement2 = r"'tipologia_sigla': '\1'"
    content = re.sub(pattern2, replacement2, content)
    
    # Fix specifici per load_localita_values e simili
    fixes = [
        ("'tipologia_sigla': \"'\" + '10.2' + \"'\"", "'tipologia_sigla': '10.2'"),
        ("'tipologia_sigla': \"'\" + '10.3' + \"'\"", "'tipologia_sigla': '10.3'"),
        ("'tipologia_sigla': \"'\" + '10.4' + \"'\"", "'tipologia_sigla': '10.4'"),
        ("'tipologia_sigla': \"'\" + '10.5' + \"'\"", "'tipologia_sigla': '10.5'"),
        ("'tipologia_sigla': \"'10.12'\"", "'tipologia_sigla': '10.12'"),
        ("'nome_tabella': \"'tma_materiali_archeologici'\"", "'nome_tabella': 'tma_materiali_archeologici'"),
    ]
    
    for old, new in fixes:
        content = content.replace(old, new)
    
    # Conta le modifiche
    changes = 0
    for line in content.split('\n'):
        if "'nome_tabella': \"'\"" in line or "'tipologia_sigla': \"'\"" in line:
            print(f"  Ancora da sistemare: {line.strip()}")
            changes += 1
    
    if changes > 0:
        print(f"\n⚠️ Trovate {changes} linee ancora da sistemare")
    else:
        print("\n✓ Tutte le virgolette sono state rimosse")
    
    # Scrivi il file modificato
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ Modifiche applicate!")
    
    return True

def main():
    # File path
    file_path = "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/tabs/Tma.py"
    
    if not os.path.exists(file_path):
        print(f"File non trovato: {file_path}")
        return 1
    
    print("Rimozione di tutte le virgolette extra")
    print("=" * 60)
    
    if fix_all_quotes(file_path):
        print("\n✅ Processo completato con successo!")
    else:
        print("\n❌ Processo fallito.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())