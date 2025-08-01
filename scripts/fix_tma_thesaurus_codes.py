#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per correggere i codici tipologia_sigla in Tma.py
"""

import os
import sys
import re

def fix_thesaurus_codes(file_path):
    """Corregge i codici thesaurus nel file Tma.py."""
    print(f"Correzione codici thesaurus in: {file_path}")
    
    # Leggi il file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup del file originale
    backup_path = file_path + '.backup_codes'
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Backup creato: {backup_path}")
    
    # Definisci le sostituzioni
    replacements = [
        # Thesaurus map per i materiali
        ("'materiale': '10.20'", "'materiale': '10.1'"),
        ("'categoria': '10.12'", "'categoria': '10.7'"),
        ("'classe': '10.13'", "'classe': '10.8'"),
        ("'tipologia': '10.14'", "'tipologia': '10.9'"),
        ("'definizione': '10.15'", "'definizione': '10.10'"),
        ("'cronologia_mac': '10.16'", "'cronologia_mac': '10.11'"),
        
        # Codici per località (10.18 -> 10.13)
        ("'tipologia_sigla': \"'10.18'\"", "'tipologia_sigla': \"'10.13'\""),
        
        # Codici per area nella funzione filter_area_by_localita (10.7 -> 10.14)
        # Solo nella funzione filter_area_by_localita
        ("'tipologia_sigla': \"'10.7'\",\n                    'parent_sigla'", 
         "'tipologia_sigla': \"'10.14'\",\n                    'parent_sigla'"),
        
        # Codici per area nella funzione filter_settore_by_area (10.7 -> 10.14)
        # Solo nella riga con sigla_estesa
        ("'tipologia_sigla': \"'10.7'\",\n                'sigla_estesa'", 
         "'tipologia_sigla': \"'10.14'\",\n                'sigla_estesa'"),
        
        # Codici per area in load_area_values (10.7 -> 10.14)
        ("'tipologia_sigla': \"'10.7'\"\n        }\n        area_vl_thesaurus", 
         "'tipologia_sigla': \"'10.14'\"\n        }\n        area_vl_thesaurus"),
        
        # Codici per settore (10.19 -> 10.15)
        ("'tipologia_sigla': \"'10.19'\"", "'tipologia_sigla': \"'10.15'\""),
        
        # Codici per aint (10.11 -> 10.5)
        ("'tipologia_sigla': \"'\" + '10.11' + \"'\"", "'tipologia_sigla': \"'\" + '10.5' + \"'\""),
    ]
    
    # Applica le sostituzioni
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            print(f"  Sostituito: {old} -> {new}")
        else:
            print(f"  Non trovato: {old}")
    
    # Scrivi il file modificato
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ Correzione completata!")
    
    # Verifica i codici finali
    print("\nVerifica codici finali:")
    patterns = [
        (r"'materiale':\s*'([^']+)'", "materiale"),
        (r"'categoria':\s*'([^']+)'", "categoria"),
        (r"'classe':\s*'([^']+)'", "classe"),
        (r"'tipologia':\s*'([^']+)'", "tipologia"),
        (r"'definizione':\s*'([^']+)'", "definizione"),
        (r"'cronologia_mac':\s*'([^']+)'", "cronologia_mac"),
    ]
    
    for pattern, name in patterns:
        match = re.search(pattern, content)
        if match:
            print(f"  {name}: {match.group(1)}")
    
    return True

def main():
    # File path
    file_path = "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/tabs/Tma.py"
    
    if not os.path.exists(file_path):
        print(f"File non trovato: {file_path}")
        return 1
    
    print("Correzione codici tipologia_sigla in Tma.py")
    print("=" * 60)
    
    if fix_thesaurus_codes(file_path):
        print("\n✅ Processo completato con successo!")
    else:
        print("\n❌ Processo fallito.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())