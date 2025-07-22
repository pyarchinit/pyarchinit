#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Esempio di importazione inventario cassette Festos
"""

import sys
import os

# Aggiungi il path del plugin se necessario
plugin_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if plugin_path not in sys.path:
    sys.path.insert(0, plugin_path)

from modules.db.pyarchinit_conn_strings import Connection
from modules.db.pyarchinit_db_manager import Pyarchinit_db_management
from modules.utility.tma_import_parser_extended import TMAImportManagerExtended


def import_festos_inventory(file_path):
    """
    Importa un inventario cassette di Festos
    
    Args:
        file_path: percorso del file DOCX con l'inventario
    """
    
    print("=" * 60)
    print(f"IMPORTAZIONE INVENTARIO CASSETTE")
    print(f"File: {file_path}")
    print("=" * 60)
    
    try:
        # 1. Connessione al database
        print("\n1. Connessione al database...")
        conn = Connection()
        conn_str = conn.conn_str()
        db_manager = Pyarchinit_db_management(conn_str)
        db_manager.connection()
        print("   ✓ Connesso al database")
        
        # 2. Crea import manager esteso
        print("\n2. Inizializzazione import manager...")
        import_manager = TMAImportManagerExtended(db_manager)
        print("   ✓ Import manager pronto")
        
        # 3. Verifica che il file esista
        if not os.path.exists(file_path):
            print(f"\n❌ ERRORE: File non trovato: {file_path}")
            return
        
        # 4. Importa il file
        print(f"\n3. Importazione file...")
        print(f"   - File: {os.path.basename(file_path)}")
        print(f"   - Dimensione: {os.path.getsize(file_path) / 1024:.1f} KB")
        
        # Esegui importazione
        imported_count, errors, warnings = import_manager.import_file(file_path)
        
        # 5. Mostra risultati
        print(f"\n4. RISULTATI IMPORTAZIONE:")
        print(f"   - Record importati: {imported_count}")
        print(f"   - Errori: {len(errors)}")
        print(f"   - Avvisi: {len(warnings)}")
        
        # Mostra dettagli errori
        if errors:
            print("\n   ERRORI:")
            for i, error in enumerate(errors[:10], 1):  # Mostra max 10 errori
                print(f"   {i}. {error}")
            if len(errors) > 10:
                print(f"   ... e altri {len(errors) - 10} errori")
        
        # Mostra dettagli warning
        if warnings:
            print("\n   AVVISI:")
            for i, warning in enumerate(warnings[:10], 1):  # Mostra max 10 warning
                print(f"   {i}. {warning}")
            if len(warnings) > 10:
                print(f"   ... e altri {len(warnings) - 10} avvisi")
        
        # 6. Statistiche finali
        if imported_count > 0:
            print(f"\n✅ IMPORTAZIONE COMPLETATA CON SUCCESSO!")
            print(f"   {imported_count} cassette sono state importate nel database TMA")
            
            # Mostra alcune statistiche
            try:
                # Conta record per sito
                query = "SELECT sito, COUNT(*) as count FROM tma_materiali_archeologici GROUP BY sito"
                result = db_manager.execute_sql_query_string(query)
                
                print("\n   Distribuzione per sito:")
                for row in result:
                    print(f"   - {row[0]}: {row[1]} record")
                    
            except Exception as e:
                print(f"\n   (Impossibile recuperare statistiche: {e})")
        else:
            print(f"\n❌ NESSUN RECORD IMPORTATO")
            print("   Controlla gli errori sopra riportati")
            
    except Exception as e:
        print(f"\n❌ ERRORE CRITICO: {str(e)}")
        import traceback
        traceback.print_exc()
        
    print("\n" + "=" * 60)


def batch_import_inventories(directory_path):
    """
    Importa tutti i file DOCX di inventario da una directory
    
    Args:
        directory_path: percorso della directory con i file
    """
    
    print("IMPORTAZIONE BATCH INVENTARI")
    print("=" * 60)
    
    # Cerca tutti i file DOCX
    docx_files = []
    for filename in os.listdir(directory_path):
        if filename.endswith('.docx') and not filename.startswith('~'):
            docx_files.append(os.path.join(directory_path, filename))
    
    if not docx_files:
        print(f"Nessun file DOCX trovato in: {directory_path}")
        return
        
    print(f"Trovati {len(docx_files)} file DOCX:")
    for f in docx_files:
        print(f"  - {os.path.basename(f)}")
    
    # Importa ogni file
    total_imported = 0
    total_errors = 0
    
    for file_path in docx_files:
        print(f"\n{'=' * 40}")
        print(f"Importazione: {os.path.basename(file_path)}")
        print(f"{'=' * 40}")
        
        try:
            imported, errors, warnings = import_single_file(file_path)
            total_imported += imported
            total_errors += len(errors)
        except Exception as e:
            print(f"ERRORE: {e}")
            total_errors += 1
    
    # Riepilogo finale
    print(f"\n{'=' * 60}")
    print(f"RIEPILOGO IMPORTAZIONE BATCH")
    print(f"{'=' * 60}")
    print(f"File processati: {len(docx_files)}")
    print(f"Record importati totali: {total_imported}")
    print(f"Errori totali: {total_errors}")


def import_single_file(file_path):
    """Importa un singolo file (funzione helper)"""
    conn = Connection()
    conn_str = conn.conn_str()
    db_manager = Pyarchinit_db_management(conn_str)
    db_manager.connection()
    
    import_manager = TMAImportManagerExtended(db_manager)
    return import_manager.import_file(file_path)


def main():
    """Funzione principale con esempi"""
    
    print("PYARCHINIT - Importazione Inventari TMA")
    print("=======================================\n")
    
    # Esempi di percorsi file
    example_files = [
        "10.docx",
        "inventario_festos.docx",
        "documents/inventari/festos_magazzino_3-4.docx",
        "/path/to/your/inventory.docx"
    ]
    
    # Cerca il primo file esistente
    file_to_import = None
    for file_path in example_files:
        if os.path.exists(file_path):
            file_to_import = file_path
            break
    
    if file_to_import:
        # Importa il file trovato
        import_festos_inventory(file_to_import)
    else:
        print("ISTRUZIONI:")
        print("-----------")
        print("1. Posiziona il file DOCX dell'inventario nella cartella del plugin")
        print("2. Rinomina questo script modificando il percorso del file")
        print("3. Esegui: python import_festos_inventory.py")
        print("\nOppure passa il file come argomento:")
        print("   python import_festos_inventory.py path/to/inventory.docx")
        
        print("\nFile di esempio cercati:")
        for f in example_files:
            print(f"  - {f}")


if __name__ == "__main__":
    # Se viene passato un file come argomento, usa quello
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if os.path.exists(file_path):
            import_festos_inventory(file_path)
        else:
            print(f"File non trovato: {file_path}")
    else:
        main()
