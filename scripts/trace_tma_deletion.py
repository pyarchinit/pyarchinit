#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per tracciare perché i record vengono cancellati quando si apre la scheda
"""

import os
import sys
import re

def add_deletion_traces(file_path):
    """Aggiunge log per tracciare le cancellazioni."""
    print(f"Aggiunta trace per cancellazioni in: {file_path}")
    
    # Leggi il file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    backup_path = file_path + '.backup_trace_deletion'
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Backup creato: {backup_path}")
    
    # Aggiungi log all'inizio di charge_records
    pattern = r"(def charge_records\(self\):)"
    replacement = r"\1\n        QgsMessageLog.logMessage(f\"DEBUG TMA charge_records: Called\", \"PyArchInit\", Qgis.Info)"
    content = re.sub(pattern, replacement, content)
    
    # Aggiungi log quando DATA_LIST viene svuotata
    pattern = r"(self\.DATA_LIST = \[\])"
    replacement = r"QgsMessageLog.logMessage(f\"DEBUG TMA: Clearing DATA_LIST in charge_records\", \"PyArchInit\", Qgis.Info)\n        \1"
    content = re.sub(pattern, replacement, content)
    
    # Aggiungi log quando viene chiamato empty_fields nella init
    init_section = re.search(r"def customize_gui\(self\):.*?(?=def\s|\Z)", content, re.DOTALL)
    if init_section:
        init_content = init_section.group(0)
        if "empty_fields" in init_content:
            print("⚠️ ATTENZIONE: empty_fields viene chiamato in customize_gui")
    
    # Aggiungi log quando viene controllato REC_TOT == 0
    pattern = r"(if self\.REC_TOT == 0:)"
    replacement = r"QgsMessageLog.logMessage(f\"DEBUG TMA: REC_TOT = {self.REC_TOT}, checking if == 0\", \"PyArchInit\", Qgis.Info)\n            \1"
    content = re.sub(pattern, replacement, content)
    
    # Aggiungi log nel metodo che potrebbe cancellare i dati
    if "delete_all_tma_materiali" in content:
        print("⚠️ TROVATO: delete_all_tma_materiali nel codice")
    
    # Scrivi il file modificato
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ Trace aggiunte!")
    
    return True

def check_initialization_flow(file_path):
    """Controlla il flusso di inizializzazione."""
    print(f"\nControllo flusso di inizializzazione...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Trova customize_gui
    customize_match = re.search(r"def customize_gui\(self\):.*?(?=def\s|\Z)", content, re.DOTALL)
    if customize_match:
        customize_content = customize_match.group(0)
        
        # Controlla l'ordine delle chiamate
        charge_pos = customize_content.find("charge_records")
        new_rec_pos = customize_content.find("on_pushButton_new_rec_pressed")
        empty_pos = customize_content.find("empty_fields")
        
        print("\nOrdine chiamate in customize_gui:")
        calls = []
        if charge_pos > -1:
            calls.append((charge_pos, "charge_records"))
        if new_rec_pos > -1:
            calls.append((new_rec_pos, "on_pushButton_new_rec_pressed"))
        if empty_pos > -1:
            calls.append((empty_pos, "empty_fields"))
        
        calls.sort()
        for pos, name in calls:
            print(f"  {name} (posizione: {pos})")
        
        # Verifica se c'è la condizione REC_TOT == 0
        if "self.REC_TOT == 0" in customize_content:
            print("\n✓ Trovata condizione self.REC_TOT == 0")
            if "on_pushButton_new_rec_pressed" in customize_content:
                print("  → Chiama on_pushButton_new_rec_pressed quando non ci sono record")

def main():
    # File path
    file_path = "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/tabs/Tma.py"
    
    if not os.path.exists(file_path):
        print(f"File non trovato: {file_path}")
        return 1
    
    print("Trace cancellazione record TMA")
    print("=" * 60)
    
    if add_deletion_traces(file_path):
        check_initialization_flow(file_path)
        print("\n✅ Processo completato!")
        print("\nOra riavvia QGIS e controlla i log quando apri la scheda TMA.")
    else:
        print("\n❌ Processo fallito.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())