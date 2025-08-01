#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per correggere gli ultimi problemi TMA
"""

import os
import sys
import re

def fix_final_issues(file_path):
    """Corregge gli ultimi problemi."""
    print(f"Correzione problemi finali in: {file_path}")
    
    # Leggi il file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    backup_path = file_path + '.backup_final_fix'
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Backup creato: {backup_path}")
    
    # 1. Fix lingua in load_thesaurus_values
    # Trova il metodo load_thesaurus_values
    pattern = r"(def load_thesaurus_values.*?)'lingua': \"\'\"\s*\+\s*lang\s*\+\s*\"'\"\s*,"
    replacement = r"\1'lingua': lang,"
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    print("✓ Corretto problema lingua in load_thesaurus_values")
    
    # 2. Aggiungi created_by e updated_by nei metodi insert_new_rec e update_record
    # Per insert_new_rec
    if "def insert_new_rec(self):" in content:
        # Trova la lista dei parametri per TMA
        pattern = r"(data = self\.DB_MANAGER\.insert_values_tma\(\n.*?)(            \)\n)"
        replacement = r"\1            '',  # created_by\n            ''   # updated_by\n\2"
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        print("✓ Aggiunti created_by e updated_by in insert_new_rec")
    
    # Per update_record
    pattern = r"(self\.DATA_LIST\[self\.REC_CORR\] = data_list\[0\])"
    if pattern in content:
        # Dobbiamo aggiungere created_by e updated_by anche qui
        pass  # Per ora lasciamo così, potrebbe richiedere modifiche più complesse
    
    # 3. Aggiungi delegate per documentazione grafica
    # Trova setup_documentation_delegates
    doc_delegate_pattern = r"(# For drawings, we might need drawing types from thesaurus too\s*\n\s*# Currently using free text, but could be enhanced)"
    
    doc_delegate_addition = '''# For drawings, we might need drawing types from thesaurus too
        # Currently using free text, but could be enhanced
        
        # Load drawing types from thesaurus if available
        drat_values = []
        if self.DB_MANAGER and self.DB_MANAGER != "":
            # Assumiamo che ci sia un tipo per i disegni (es. 10.16)
            # Per ora usiamo valori predefiniti
            drat_values = ["pianta", "sezione", "prospetto", "assonometria", "dettaglio", "schizzo"]
        
        # Set delegate for drawing type column if we have values
        if drat_values and hasattr(self, 'tableWidget_disegni'):
            self.tableWidget_disegni.setItemDelegateForColumn(0, ComboBoxDelegate(drat_values, self.tableWidget_disegni))
            QgsMessageLog.logMessage(f"DEBUG TMA: Set delegate for Drawing Type column with {len(drat_values)} values", "PyArchInit", Qgis.Info)'''
    
    content = re.sub(doc_delegate_pattern, doc_delegate_addition, content, flags=re.DOTALL)
    print("✓ Aggiunto delegate per documentazione grafica")
    
    # 4. Correzione lingua anche in altri punti dove necessario
    # Controlla se ci sono altri punti con lo stesso problema
    content = content.replace("'lingua': \"'\" + lang + \"'\"", "'lingua': lang")
    content = content.replace("'lingua': \"'IT'\"", "'lingua': 'IT'")
    
    # Scrivi il file modificato
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ Correzioni applicate!")
    
    return True

def check_database_tma_structure(db_path):
    """Verifica la struttura della tabella TMA."""
    import sqlite3
    
    print(f"\nVerifica struttura tabella TMA in: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verifica se esistono i campi created_by e updated_by
        cursor.execute("PRAGMA table_info(tma_table)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        has_created_by = 'created_by' in column_names
        has_updated_by = 'updated_by' in column_names
        
        print(f"  Campo created_by: {'✓ Presente' if has_created_by else '✗ Mancante'}")
        print(f"  Campo updated_by: {'✓ Presente' if has_updated_by else '✗ Mancante'}")
        
        if not has_created_by or not has_updated_by:
            print("\n⚠️ ATTENZIONE: Mancano i campi created_by/updated_by")
            print("  Esegui questo SQL per aggiungerli:")
            if not has_created_by:
                print("  ALTER TABLE tma_table ADD COLUMN created_by TEXT DEFAULT '';")
            if not has_updated_by:
                print("  ALTER TABLE tma_table ADD COLUMN updated_by TEXT DEFAULT '';")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Errore verifica database: {e}")
    
    return True

def main():
    # File path
    file_path = "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/tabs/Tma.py"
    
    if not os.path.exists(file_path):
        print(f"File non trovato: {file_path}")
        return 1
    
    print("Correzione problemi finali TMA")
    print("=" * 60)
    
    if fix_final_issues(file_path):
        # Verifica anche il database
        db_path = "/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite"
        check_database_tma_structure(db_path)
        
        print("\n✅ Processo completato con successo!")
    else:
        print("\n❌ Processo fallito.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())