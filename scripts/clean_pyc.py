#!/usr/bin/env python3
"""
Script per pulire i file .pyc che potrebbero causare problemi con cache
"""

import os
import shutil

def clean_pyc_files(root_dir='.'):
    """Rimuove tutti i file .pyc e le directory __pycache__"""
    
    removed_files = 0
    removed_dirs = 0
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Rimuovi file .pyc
        for filename in filenames:
            if filename.endswith('.pyc'):
                filepath = os.path.join(dirpath, filename)
                try:
                    os.remove(filepath)
                    removed_files += 1
                    print(f"Rimosso: {filepath}")
                except Exception as e:
                    print(f"Errore rimozione {filepath}: {e}")
        
        # Rimuovi directory __pycache__
        if '__pycache__' in dirnames:
            pycache_dir = os.path.join(dirpath, '__pycache__')
            try:
                shutil.rmtree(pycache_dir)
                removed_dirs += 1
                print(f"Rimossa directory: {pycache_dir}")
            except Exception as e:
                print(f"Errore rimozione {pycache_dir}: {e}")
            
            # Rimuovi dalla lista per non entrarci
            dirnames.remove('__pycache__')
    
    print(f"\nPulizia completata!")
    print(f"File .pyc rimossi: {removed_files}")
    print(f"Directory __pycache__ rimosse: {removed_dirs}")
    print("\nRiavvia QGIS per applicare le modifiche.")

if __name__ == "__main__":
    print("PULIZIA FILE PYTHON COMPILATI")
    print("=" * 50)
    
    # Pulisci dalla directory corrente
    clean_pyc_files()
