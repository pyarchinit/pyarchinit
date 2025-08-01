#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per aggiungere ComboBoxDelegate alle tabelle documentazione
"""

import os
import sys

def add_documentation_delegates(file_path):
    """Aggiunge delegate per le tabelle documentazione."""
    print(f"Aggiunta delegate documentazione in: {file_path}")
    
    # Leggi il file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    backup_path = file_path + '.backup_doc_delegates'
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Backup creato: {backup_path}")
    
    # Trova la fine del metodo setup_table_delegate
    setup_end = content.find("        # Connect signal to track table changes")
    
    if setup_end == -1:
        print("❌ Non trovato il punto di inserimento")
        return False
    
    # Codice da inserire per le delegate documentazione
    doc_delegates_code = '''
        
        # Setup delegates for documentation tables
        self.setup_documentation_delegates()
    
    def setup_documentation_delegates(self):
        """Setup delegates for photo and drawing documentation tables."""
        from qgis.PyQt.QtWidgets import QStyledItemDelegate, QComboBox
        
        # Load photo types from thesaurus
        ftap_values = []
        if self.DB_MANAGER and self.DB_MANAGER != "":
            search_dict = {
                'lingua': "'IT'",
                'nome_tabella': "'tma_materiali_archeologici'",
                'tipologia_sigla': "'10.12'"
            }
            ftap_res = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
            for rec in ftap_res:
                if hasattr(rec, 'sigla_estesa') and rec.sigla_estesa:
                    ftap_values.append(str(rec.sigla_estesa))
            ftap_values.sort()
        
        # If we have photo types, set delegate for first column of photo table
        if ftap_values and hasattr(self, 'tableWidget_foto'):
            self.tableWidget_foto.setItemDelegateForColumn(0, ComboBoxDelegate(ftap_values, self.tableWidget_foto))
            QgsMessageLog.logMessage(f"DEBUG TMA: Set delegate for Photo Type column with {len(ftap_values)} values", "PyArchInit", Qgis.Info)
        
        # For drawings, we might need drawing types from thesaurus too
        # Currently using free text, but could be enhanced
'''
    
    # Inserisci il nuovo codice
    insert_pos = setup_end
    content = content[:insert_pos] + doc_delegates_code + "\n    " + content[insert_pos:]
    
    # Verifica che ftap sia caricato correttamente
    if "'tipologia_sigla': \"'\" + '10.12' + \"'\"" in content:
        print("✓ FTAP (tipo foto) già caricato con codice 10.12")
    else:
        print("⚠️ FTAP potrebbe non essere caricato correttamente")
    
    # Scrivi il file modificato
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ Delegate documentazione aggiunte!")
    
    return True

def main():
    # File path
    file_path = "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/tabs/Tma.py"
    
    if not os.path.exists(file_path):
        print(f"File non trovato: {file_path}")
        return 1
    
    print("Aggiunta delegate documentazione TMA")
    print("=" * 60)
    
    if add_documentation_delegates(file_path):
        print("\n✅ Processo completato con successo!")
    else:
        print("\n❌ Processo fallito.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())