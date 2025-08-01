#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per correggere la foreign key nella tabella tma_materiali_ripetibili
"""

import os
import sys

def fix_foreign_key(file_path):
    """Corregge la foreign key per puntare alla tabella corretta."""
    print(f"Correzione foreign key in: {file_path}")
    
    # Leggi il file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    backup_path = file_path + '.backup_fk_fix'
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Backup creato: {backup_path}")
    
    # Correggi la foreign key
    old_fk = "Column('id_tma', Integer, ForeignKey('tma_materiali_archeologici.id'), nullable=False),"
    new_fk = "Column('id_tma', Integer, ForeignKey('tma_materiali_archeologici.id'), nullable=False),"
    
    # Prima verifichiamo qual è il nome corretto della tabella TMA principale
    # Potrebbe essere 'tma_table' o altro
    print("\nVerifica: cercando il nome corretto della tabella TMA principale...")
    
    # Sostituiamo con il nome corretto della tabella
    # Basandoci sui file precedenti, sembra che la tabella si chiami 'tma_materiali_archeologici'
    # ma dobbiamo verificare
    
    content_modified = content
    
    # Scrivi il file modificato
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content_modified)
    
    print("\n⚠️ ATTENZIONE: Verifica il nome della tabella TMA principale!")
    print("La foreign key attualmente punta a 'tma_materiali_archeologici'")
    print("Se il nome della tabella è diverso, dovrai modificarlo manualmente.")
    
    return True

def check_tma_table_name():
    """Verifica il nome della tabella TMA principale."""
    tma_table_path = "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/modules/db/structures/Tma_table.py"
    
    if os.path.exists(tma_table_path):
        with open(tma_table_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Cerca il nome della tabella
        import re
        match = re.search(r"Table\('([^']+)'", content)
        if match:
            table_name = match.group(1)
            print(f"\n✓ Tabella TMA principale trovata: '{table_name}'")
            return table_name
    
    return None

def main():
    # File path
    file_path = "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/modules/db/structures/Tma_materiali_table.py"
    
    if not os.path.exists(file_path):
        print(f"File non trovato: {file_path}")
        return 1
    
    print("Correzione foreign key TMA materiali")
    print("=" * 60)
    
    # Prima verifica il nome della tabella TMA
    tma_table_name = check_tma_table_name()
    
    if tma_table_name and tma_table_name != 'tma_materiali_archeologici':
        print(f"\n⚠️ ATTENZIONE: La tabella TMA si chiama '{tma_table_name}'")
        print(f"   ma la foreign key punta a 'tma_materiali_archeologici'")
        print(f"   Correzione necessaria!")
        
        # Correggi il file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Backup
        backup_path = file_path + '.backup_fk_fix'
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Sostituisci il nome della tabella
        content = content.replace(
            "ForeignKey('tma_materiali_archeologici.id')",
            f"ForeignKey('{tma_table_name}.id')"
        )
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"\n✅ Foreign key corretta per puntare a '{tma_table_name}'")
    else:
        print("\n✓ La foreign key sembra corretta")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())