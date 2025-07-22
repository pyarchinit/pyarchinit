#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Esempio di utilizzo del sistema di importazione TMA
"""

import sys
import os

# Aggiungi il percorso di pyarchinit al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from modules.db.pyarchinit_conn_strings import Connection
from modules.db.pyarchinit_db_manager import Pyarchinit_db_management
from modules.utility.tma_import_parser import TMAImportManager, TMAFieldMapping

# Esempio 1: Importazione singolo file Excel
def import_excel_example():
    """Esempio di importazione da Excel"""
    
    # Connessione al database
    conn = Connection()
    conn_str = conn.conn_str()
    db_manager = Pyarchinit_db_management(conn_str)
    db_manager.connection()
    
    # Crea il manager di importazione
    import_manager = TMAImportManager(db_manager)
    
    # File da importare
    file_path = "path/to/your/tma_data.xlsx"
    
    # Importa il file
    imported, errors, warnings = import_manager.import_file(file_path)
    
    print(f"Record importati: {imported}")
    print(f"Errori: {errors}")
    print(f"Avvisi: {warnings}")


# Esempio 2: Importazione con mapping personalizzato
def import_with_custom_mapping():
    """Esempio di importazione con mapping personalizzato dei campi"""
    
    # Connessione al database
    conn = Connection()
    conn_str = conn.conn_str()
    db_manager = Pyarchinit_db_management(conn_str)
    db_manager.connection()
    
    # Crea il manager di importazione
    import_manager = TMAImportManager(db_manager)
    
    # Definisci mapping personalizzato
    custom_mapping = {
        'numero_inventario_museo': 'madi',  # Mappa il campo del file al campo database
        'tipo_di_materiale': 'ogtm',
        'peso_grammi': 'peso',
        'unita_stratigrafica': 'dscu'
    }
    
    # File da importare
    file_path = "path/to/your/custom_format.csv"
    
    # Importa con mapping personalizzato
    imported, errors, warnings = import_manager.import_file(file_path, custom_mapping)
    
    print(f"Record importati: {imported}")


# Esempio 3: Importazione batch di multipli file
def import_batch_example():
    """Esempio di importazione di multipli file"""
    
    # Connessione al database
    conn = Connection()
    conn_str = conn.conn_str()
    db_manager = Pyarchinit_db_management(conn_str)
    db_manager.connection()
    
    # Crea il manager di importazione
    import_manager = TMAImportManager(db_manager)
    
    # Lista di file da importare
    files_to_import = [
        "path/to/data1.xlsx",
        "path/to/data2.csv",
        "path/to/data3.json",
        "path/to/data4.xml"
    ]
    
    # Importa tutti i file
    results = import_manager.import_batch(files_to_import)
    
    print(f"Totale record importati: {results['total_imported']}")
    
    for file_path, result in results['file_results'].items():
        print(f"\nFile: {file_path}")
        print(f"  Importati: {result['imported']}")
        print(f"  Errori: {len(result['errors'])}")
        print(f"  Avvisi: {len(result['warnings'])}")


# Esempio 4: Creazione file di esempio per test
def create_example_files():
    """Crea file di esempio per testare l'importazione"""
    
    import pandas as pd
    import json
    
    # Crea esempio Excel
    excel_data = {
        'Sito': ['Roma', 'Roma', 'Pompei'],
        'Area': ['A', 'B', 'C'],
        'US': ['101', '102', '201'],
        'Materiale': ['CERAMICA', 'METALLO', 'CERAMICA'],
        'Cassetta': ['C001', 'C002', 'C003'],
        'Località': ['Roma Centro', 'Roma Centro', 'Pompei Scavi'],
        'Denominazione collocazione': ['Magazzino 1', 'Magazzino 1', 'Magazzino 2'],
        'Fascia cronologica': ['I sec. d.C.', 'II sec. d.C.', 'I sec. d.C.'],
        'Categoria': ['Ceramica comune', 'Bronzo', 'Terra sigillata'],
        'N. reperti': ['15', '3', '25'],
        'Peso': ['250', '120', '340']
    }
    
    df = pd.DataFrame(excel_data)
    df.to_excel('tma_example.xlsx', index=False)
    print("Creato file: tma_example.xlsx")
    
    # Crea esempio CSV
    df.to_csv('tma_example.csv', index=False)
    print("Creato file: tma_example.csv")
    
    # Crea esempio JSON
    json_data = []
    for _, row in df.iterrows():
        json_data.append(row.to_dict())
    
    with open('tma_example.json', 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    print("Creato file: tma_example.json")
    
    # Crea esempio XML
    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n<records>\n'
    for _, row in df.iterrows():
        xml_content += '  <record>\n'
        for col, value in row.items():
            xml_content += f'    <{col}>{value}</{col}>\n'
        xml_content += '  </record>\n'
    xml_content += '</records>'
    
    with open('tma_example.xml', 'w', encoding='utf-8') as f:
        f.write(xml_content)
    print("Creato file: tma_example.xml")


# Esempio 5: Verifica mapping disponibili
def show_available_mappings():
    """Mostra tutti i mapping di campo disponibili"""
    
    print("MAPPATURA CAMPI DISPONIBILI")
    print("=" * 50)
    
    for db_field, aliases in TMAFieldMapping.FIELD_MAPPINGS.items():
        print(f"\nCampo database: {db_field}")
        print(f"  Alias accettati: {', '.join(aliases)}")


if __name__ == "__main__":
    # Crea file di esempio
    create_example_files()
    
    # Mostra mapping disponibili
    show_available_mappings()
    
    # Per eseguire l'importazione, decommenta le righe seguenti:
    # import_excel_example()
    # import_with_custom_mapping()
    # import_batch_example()
