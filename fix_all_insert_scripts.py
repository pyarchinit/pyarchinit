#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per correggere tutti gli script di insert del thesaurus TMA
"""

import os
import re

# Mapping corretto dei codici tipologia
CORRECT_MAPPING = {
    'aint': '10.5',      # Tipo acquisizione/Altro (era 10.11 o 10.14)
    'area': '10.7',      # Area
    'cronologia': '10.6', # Cronologia specifica (era vario)
    'dtzg': '10.6',      # Fascia cronologica
    'ftap': '10.12',     # Tipo foto (era 10.11)
    'ldcn': '10.1',      # Denominazione collocazione
    'ldct': '10.2',      # Tipologia collocazione (era 10.10)
    'localita': '10.3',  # Località (era 10.18)
    'macc': '10.5',      # Categoria materiali (era 10.14)
    'macd': '10.10',     # Definizione materiali (era 10.17)
    'macl': '10.8',      # Classe materiali (era 10.15)
    'macp': '10.9',      # Prec. tipologica (era 10.16)
    'ogtm': '10.4',      # Materiale/Nome scavo (era vario)
    'saggio': '10.2',    # Saggio (stesso di ldct)
    'vano': '10.2',      # Vano/Locus (stesso di ldct)
    'scan': '10.4',      # Nome scavo
    'settore': '10.15',  # Settore (era 10.19)
}

# Nome tabella corretto
CORRECT_TABLE_NAME = 'TMA materiali archeologici'

def fix_script(filepath):
    """Corregge un singolo script di insert."""
    print(f"\nProcessing: {os.path.basename(filepath)}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    changes_made = []
    
    # 1. Correggi nome tabella
    # Pattern per trovare nome_tabella con vari formati
    patterns_table = [
        (r"nome_tabella\s*=\s*['\"]tma_materiali_archeologici['\"]", f"nome_tabella = '{CORRECT_TABLE_NAME}'"),
        (r"'nome_tabella':\s*['\"]tma_materiali_archeologici['\"]", f"'nome_tabella': '{CORRECT_TABLE_NAME}'"),
        (r"VALUES\s*\(['\"]tma_materiali_archeologici['\"]", f"VALUES ('{CORRECT_TABLE_NAME}'"),
    ]
    
    for pattern, replacement in patterns_table:
        if re.search(pattern, content, re.IGNORECASE):
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
            changes_made.append(f"  ✓ Nome tabella: tma_materiali_archeologici → {CORRECT_TABLE_NAME}")
    
    # 2. Correggi codici tipologia
    # Estrai il tipo dal nome del file
    basename = os.path.basename(filepath).lower()
    field_type = None
    
    for field in CORRECT_MAPPING:
        if field in basename:
            field_type = field
            break
    
    if field_type:
        correct_code = CORRECT_MAPPING[field_type]
        
        # Pattern per trovare tipologia_sigla
        patterns_tipo = [
            (r"tipologia_sigla\s*=\s*['\"]10\.\d+['\"]", f"tipologia_sigla = '{correct_code}'"),
            (r"'tipologia_sigla':\s*['\"]10\.\d+['\"]", f"'tipologia_sigla': '{correct_code}'"),
            (r"tipologia_sigla\s*=\s*'10\.\d+'", f"tipologia_sigla = '{correct_code}'"),
            (r"VALUES\s*\([^,]+,\s*[^,]+,\s*[^,]+,\s*['\"]10\.\d+['\"]", lambda m: m.group(0)[:-6] + f"'{correct_code}'"),
        ]
        
        for pattern, replacement in patterns_tipo:
            matches = re.findall(pattern, content)
            if matches:
                old_codes = set(re.findall(r'10\.\d+', ' '.join(matches)))
                content = re.sub(pattern, replacement, content)
                for old_code in old_codes:
                    if old_code != correct_code:
                        changes_made.append(f"  ✓ Tipologia: {old_code} → {correct_code} ({field_type})")
    
    # 3. Correggi path database se necessario
    db_patterns = [
        (r'/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd\.sqlite', 
         '/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/pyarchinit_db.sqlite'),
    ]
    
    for pattern, replacement in db_patterns:
        if pattern in content:
            content = content.replace(pattern, replacement)
            changes_made.append(f"  ✓ Database path aggiornato")
    
    # Salva se ci sono modifiche
    if content != original_content:
        # Crea backup
        backup_path = filepath + '.backup'
        if not os.path.exists(backup_path):
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
        
        # Salva modifiche
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  Modifiche applicate:")
        for change in changes_made:
            print(change)
    else:
        print("  Nessuna modifica necessaria")
    
    return len(changes_made) > 0

def main():
    scripts_dir = "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/scripts"
    
    # Lista degli script da correggere
    scripts = [
        'insert_aint_from_excel.py',
        'insert_area_from_excel.py',
        'insert_cronologia_from_excel.py',
        'insert_dtzg_from_excel.py',
        'insert_ftap_from_excel.py',
        'insert_ldcn_from_excel.py',
        'insert_ldct_from_excel.py',
        'insert_localita_from_excel.py',
        'insert_localita_from_excel_corrected.py',
        'insert_macc_from_excel.py',
        'insert_macd_from_excel.py',
        'insert_macl_from_excel.py',
        'insert_macp_from_excel.py',
        'insert_missing_ldct.py',
        'insert_ogtm_from_excel.py',
        'insert_remaining_tma_thesaurus.py',
        'insert_saggio_vano_from_excel.py',
        'insert_scan_from_excel.py',
        'insert_settore_from_excel.py',
    ]
    
    print("=== Correzione script insert thesaurus TMA ===")
    print(f"Directory: {scripts_dir}")
    print(f"Script da processare: {len(scripts)}")
    print("\nMapping corretto dei codici:")
    for field, code in sorted(CORRECT_MAPPING.items()):
        print(f"  {field}: {code}")
    print(f"\nNome tabella corretto: {CORRECT_TABLE_NAME}")
    print("=" * 60)
    
    fixed_count = 0
    
    for script in scripts:
        filepath = os.path.join(scripts_dir, script)
        if os.path.exists(filepath):
            if fix_script(filepath):
                fixed_count += 1
        else:
            print(f"\n❌ File non trovato: {script}")
    
    print("\n" + "=" * 60)
    print(f"✅ Completato! Script corretti: {fixed_count}/{len(scripts)}")
    print("\nNOTA: I file originali sono stati salvati con estensione .backup")

if __name__ == "__main__":
    main()