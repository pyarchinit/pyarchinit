#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per correggere l'errore dell'attributo inventario mancante
"""

import os
import sys

def fix_inventario_error(file_path):
    """Corregge l'errore dell'attributo inventario."""
    print(f"Correzione errore inventario in: {file_path}")
    
    # Leggi il file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    backup_path = file_path + '.backup_inventario_fix'
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Backup creato: {backup_path}")
    
    # Fix 1: Sostituisci current_tma.inventario con current_tma.id
    old_line = 'filename = f"Etichetta_TMA_{current_tma.inventario}_{datetime.datetime.now().strftime(\'%Y%m%d_%H%M%S\')}.pdf"'
    new_line = 'filename = f"Etichetta_TMA_{current_tma.id}_{datetime.datetime.now().strftime(\'%Y%m%d_%H%M%S\')}.pdf"'
    
    if old_line in content:
        content = content.replace(old_line, new_line)
        print("✓ Sostituito current_tma.inventario con current_tma.id")
    else:
        print("⚠️ Linea con inventario non trovata, provo ricerca alternativa...")
        # Prova con regex per essere più flessibile
        import re
        pattern = r'current_tma\.inventario'
        replacement = 'current_tma.id'
        content = re.sub(pattern, replacement, content)
        print("✓ Sostituito tutte le occorrenze di current_tma.inventario")
    
    # Fix 2: Verifica se ci sono altri usi di .inventario su oggetti TMA
    if '.inventario' in content and 'inventario_materiali' not in content.split('.inventario')[0]:
        print("⚠️ ATTENZIONE: Trovate altre occorrenze di .inventario che potrebbero essere problematiche")
    
    # Scrivi il file modificato
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ Correzione applicata!")
    
    return True

def check_fill_fields_method(file_path):
    """Verifica se fill_fields potrebbe causare problemi."""
    print(f"\nVerifica metodo fill_fields...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Cerca se fill_fields accede a campi non esistenti
    import re
    pattern = r'def fill_fields.*?(?=def\s|\Z)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        fill_fields_content = match.group(0)
        if 'inventario' in fill_fields_content:
            print("⚠️ ATTENZIONE: fill_fields potrebbe accedere al campo inventario")
        else:
            print("✓ fill_fields non accede al campo inventario")

def main():
    # File path
    file_path = "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/tabs/Tma.py"
    
    if not os.path.exists(file_path):
        print(f"File non trovato: {file_path}")
        return 1
    
    print("Fix errore attributo inventario TMA")
    print("=" * 60)
    
    if fix_inventario_error(file_path):
        check_fill_fields_method(file_path)
        print("\n✅ Processo completato!")
        print("\nOra riavvia QGIS e prova ad aprire una scheda TMA.")
    else:
        print("\n❌ Processo fallito.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())