#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per correggere il problema di commit delle sessioni TMA
"""

import os
import sys
import re

def fix_session_commit(file_path):
    """Corregge i problemi di commit nelle sessioni."""
    print(f"Correzione commit sessioni in: {file_path}")
    
    # Leggi il file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    backup_path = file_path + '.backup_session_fix'
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Backup creato: {backup_path}")
    
    # Fix 1: Assicurati che insert_data_session non abbia autocommit=True nel sessionmaker
    old_session = "Session = sessionmaker(bind=self.engine, autoflush=False)"
    new_session = "Session = sessionmaker(bind=self.engine, autoflush=False, autocommit=False)"
    
    content = content.replace(old_session, new_session)
    print("✓ Corretto sessionmaker per insert_data_session")
    
    # Fix 2: Aggiungi dei log per debug
    # Trova insert_data_session e aggiungi log
    pattern = r"(def insert_data_session\(self, data\):.*?session\.close\(\))"
    
    def add_logging(match):
        method = match.group(1)
        # Aggiungi log prima del commit
        method = method.replace(
            "session.commit()",
            """# Log per debug
        try:
            session.commit()
            print(f"DEBUG: Record committed successfully - Type: {type(data).__name__}")
        except Exception as e:
            session.rollback()
            print(f"DEBUG: Commit failed - Error: {str(e)}")
            raise"""
        )
        return method
    
    content = re.sub(pattern, add_logging, content, flags=re.DOTALL)
    print("✓ Aggiunto logging per debug commit")
    
    # Scrivi il file modificato
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ Correzioni applicate!")
    
    return True

def check_insert_method(file_path):
    """Verifica il metodo insert_new_rec in Tma.py."""
    print(f"\nVerifica insert_new_rec in: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Cerca problemi nel metodo insert_new_rec
    if "self.DB_MANAGER.insert_data_session(data)" in content:
        print("✓ insert_data_session viene chiamato")
        
        # Verifica se c'è un try/except che potrebbe nascondere errori
        pattern = r"self\.DB_MANAGER\.insert_data_session\(data\)(.*?)return 1"
        match = re.search(pattern, content, re.DOTALL)
        if match:
            context = match.group(1)
            if "except" not in context:
                print("✓ Nessun except che nasconde errori dopo insert_data_session")
            else:
                print("⚠️ C'è un except dopo insert_data_session che potrebbe nascondere errori")
    
    # Aggiungi log di debug nel metodo insert_new_rec
    backup_path = file_path + '.backup_insert_debug'
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Aggiungi log prima e dopo insert_data_session
    content = content.replace(
        "self.DB_MANAGER.insert_data_session(data)",
        """QgsMessageLog.logMessage(f"DEBUG TMA: About to insert data - Type: {type(data).__name__}", "PyArchInit", Qgis.Info)
            self.DB_MANAGER.insert_data_session(data)
            QgsMessageLog.logMessage(f"DEBUG TMA: Data inserted successfully", "PyArchInit", Qgis.Info)"""
    )
    
    # Aggiungi log dopo max_num_id
    content = content.replace(
        "inserted_id = self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, self.ID_TABLE)",
        """inserted_id = self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, self.ID_TABLE)
            QgsMessageLog.logMessage(f"DEBUG TMA: Inserted record ID: {inserted_id}", "PyArchInit", Qgis.Info)"""
    )
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ Aggiunto logging di debug in insert_new_rec")

def main():
    # File paths
    db_manager_path = "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/modules/db/pyarchinit_db_manager.py"
    tma_path = "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/tabs/Tma.py"
    
    print("Fix problemi commit TMA")
    print("=" * 60)
    
    if os.path.exists(db_manager_path):
        fix_session_commit(db_manager_path)
    else:
        print(f"File non trovato: {db_manager_path}")
    
    if os.path.exists(tma_path):
        check_insert_method(tma_path)
    else:
        print(f"File non trovato: {tma_path}")
    
    print("\n✅ Processo completato!")
    print("\nOra riavvia QGIS e prova a salvare un record TMA.")
    print("Controlla i log di QGIS per vedere i messaggi di debug.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())