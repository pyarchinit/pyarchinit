#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script finale per correggere qualsiasi riferimento rimanente ai nomi tabella vecchi
"""

import os
import re

def fix_remaining_references():
    """Corregge tutti i riferimenti rimanenti ai nomi tabella vecchi."""
    
    scripts_dir = "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/scripts"
    
    replacements = [
        # Fix DELETE statements
        ("WHERE nome_tabella = 'tma_materiali_archeologici'", 
         "WHERE nome_tabella = 'TMA materiali archeologici'"),
        
        # Fix general nome_tabella assignments
        ("nome_tabella = 'tma_materiali_archeologici'", 
         "nome_tabella = 'TMA materiali archeologici'"),
        
        # Fix nome_tabella in dict format
        ("'nome_tabella': 'tma_materiali_archeologici'", 
         "'nome_tabella': 'TMA materiali archeologici'"),
         
        # Fix tma_materiali_ripetibili
        ("'tma_materiali_ripetibili'", 
         "'TMA materiali ripetibili'"),
        
        ("tma_materiali_ripetibili", 
         "TMA materiali ripetibili"),
    ]
    
    # Process all Python files in scripts directory
    for filename in os.listdir(scripts_dir):
        if filename.endswith('.py') and filename.startswith('insert_'):
            filepath = os.path.join(scripts_dir, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                changes_made = []
                
                for old_text, new_text in replacements:
                    if old_text in content:
                        content = content.replace(old_text, new_text)
                        changes_made.append(f"  ✓ Sostituito: {old_text[:50]}...")
                
                if content != original_content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"\n{filename}:")
                    for change in changes_made:
                        print(change)
                        
            except Exception as e:
                print(f"\n❌ Errore con {filename}: {e}")
    
    print("\n✅ Correzione completata!")

if __name__ == "__main__":
    print("=== Correzione finale riferimenti tabelle ===")
    fix_remaining_references()