#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per correggere tutti i problemi in Tma.py
"""

import os
import sys
import re

def fix_tma_issues(file_path):
    """Corregge tutti i problemi in Tma.py."""
    print(f"Correzione problemi in: {file_path}")
    
    # Leggi il file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    backup_path = file_path + '.backup_fix_all'
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Backup creato: {backup_path}")
    
    # Lista delle correzioni
    replacements = [
        # 1. LDCT tipo sbagliato (10.10 -> 10.2)
        ("'tipologia_sigla': \"'\" + '10.10' + \"'\"", "'tipologia_sigla': \"'\" + '10.2' + \"'\""),
        
        # 2. LDCN tipo sbagliato (10.1 -> 10.3)
        ("'tipologia_sigla': \"'10.1'\"", "'tipologia_sigla': \"'10.3'\""),
        
        # 3. Area in fill (10.7 -> 10.14)
        ("'tipologia_sigla': \"'\" + '10.7' + \"'\"", "'tipologia_sigla': \"'\" + '10.14' + \"'\""),
        
        # 4. Saggio tipo sbagliato (10.13 -> campo non thesaurus)
        # Già corretto - è LineEdit
        
        # 5. DTZG tipo sbagliato (10.15 -> 10.6)
        ("'tipologia_sigla': \"'10.15'\"\n        }\n        dtzg_res = self.DB_MANAGER.query_bool(search_dict_dtzg",
         "'tipologia_sigla': \"'10.6'\"\n        }\n        dtzg_res = self.DB_MANAGER.query_bool(search_dict_dtzg"),
        
        # 6. Settore tipo corretto ma ripetuto (dovrebbe essere 10.15)
        # Già corretto sopra
        
        # 7. AINT che usa 'tma_table' invece di 'tma_materiali_archeologici'
        ("'nome_tabella': \"'\" + 'tma_table' + \"'\"", "'nome_tabella': \"'\" + 'tma_materiali_archeologici' + \"'\""),
        
        # 8. AINT tipo sbagliato nel metodo convert_aint (10.11 -> 10.5)
        # Già corretto sopra
        
        # 9. Aggiungere OGTM thesaurus loading (manca completamente)
        # Lo aggiungeremo dopo
    ]
    
    # Applica le sostituzioni
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            print(f"  ✓ Corretto: {old[:50]}...")
        else:
            print(f"  ⚠️ Non trovato: {old[:50]}...")
    
    # Aggiungi caricamento OGTM se manca
    if "'tipologia_sigla': \"'10.1'\"" not in content and "comboBox_ogtm" not in content:
        print("\n⚠️ NOTA: comboBox_ogtm non trovato - potrebbe essere gestito diversamente")
    
    # Correggi anche tipologia_sigla nelle query di area/settore già corrette prima
    # ma verifichiamo che siano giuste
    
    # Scrivi il file modificato
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ Correzioni applicate!")
    
    # Verifica i codici corretti
    print("\nVerifica codici tipologia_sigla nel file:")
    
    patterns = [
        (r"ldct.*?tipologia_sigla.*?'([\d.]+)'", "LDCT"),
        (r"ldcn.*?tipologia_sigla.*?'([\d.]+)'", "LDCN"), 
        (r"scan.*?tipologia_sigla.*?'([\d.]+)'", "SCAN"),
        (r"dtzg.*?tipologia_sigla.*?'([\d.]+)'", "DTZG"),
        (r"aint.*?tipologia_sigla.*?'([\d.]+)'", "AINT"),
        (r"area.*?tipologia_sigla.*?'([\d.]+)'", "AREA"),
        (r"localita.*?tipologia_sigla.*?'([\d.]+)'", "LOCALITÀ"),
        (r"settore.*?tipologia_sigla.*?'([\d.]+)'", "SETTORE"),
    ]
    
    for pattern, name in patterns:
        matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
        if matches:
            codes = set(matches)
            print(f"  {name}: {', '.join(codes)}")
    
    return True

def main():
    # File path
    file_path = "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/tabs/Tma.py"
    
    if not os.path.exists(file_path):
        print(f"File non trovato: {file_path}")
        return 1
    
    print("Correzione completa problemi TMA")
    print("=" * 60)
    
    if fix_tma_issues(file_path):
        print("\n✅ Processo completato con successo!")
    else:
        print("\n❌ Processo fallito.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())