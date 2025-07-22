#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script di test per l'importazione inventari TMA
"""

import sys
import os

# Aggiungi il path del plugin al Python path
plugin_path = os.path.dirname(os.path.abspath(__file__))
if plugin_path not in sys.path:
    sys.path.insert(0, plugin_path)

from modules.utility.tma_import_parser_extended import InventoryDocxParser


def test_inventory_parser():
    """Test del parser inventario con dati simulati"""
    
    print("TEST PARSER INVENTARIO CASSETTE")
    print("=" * 50)
    
    # Simula dati di test
    test_data = {
        'sito': 'Festos',
        'magazzino': 'Magazzino 3-4',
        'rows': [
            {
                'cassette': '1-72',
                'descrizione': 'Chalara',
                'anno': '1960'
            },
            {
                'cassette': '457',
                'descrizione': 'Frammenti scelti e siglati dai vani ellenistici ad Ovest del Piazzale I e da Ambeli',
                'anno': '1965-66'
            },
            {
                'cassette': '801-805',
                'descrizione': 'Ossa e conchiglie dalla Strada dal Nord e dall\'area a Sud della Casa della rampa',
                'anno': '2001'
            }
        ]
    }
    
    # Crea un parser mock per testare i metodi
    class MockParser(InventoryDocxParser):
        def __init__(self):
            super().__init__('test.docx')
    
    parser = MockParser()
    
    # Test parsing range cassette
    print("\nTest parsing range cassette:")
    test_ranges = ['1-72', '457', '246d-259', '801-805']
    for range_str in test_ranges:
        result = parser._parse_cassette_range(range_str)
        print(f"  {range_str} -> {len(result)} cassette: {result[:3]}{'...' if len(result) > 3 else ''}")
    
    # Test estrazione tipo materiale
    print("\nTest estrazione tipo materiale:")
    test_descriptions = [
        'Frammenti ceramici',
        'Ossa e conchiglie',
        'Blocchi di astraki',
        'Frammenti di ferro',
        'Materiale vario'
    ]
    for desc in test_descriptions:
        material = parser._extract_tipo_materiale(desc)
        print(f"  '{desc}' -> {material}")
    
    # Test estrazione area
    print("\nTest estrazione area:")
    test_areas = [
        'Vano XCIV strato pavimentale',
        'Area a Sud del vano XCI',
        'Settore Nord-Est',
        'Piazzale I'
    ]
    for area_desc in test_areas:
        area = parser._extract_area(area_desc)
        print(f"  '{area_desc}' -> '{area}'")
    
    # Test record completo
    print("\nTest creazione record completo:")
    cells = ['1-3', 'Frammenti ceramici dal vano XCIV', '1965']
    headers = ['Cassette', 'Descrizione', 'Anno']
    
    records = parser._parse_inventory_row(cells, headers, 'Festos', 'Magazzino 3-4')
    
    if records:
        print(f"\nGenerati {len(records)} record")
        print("\nEsempio primo record:")
        for key, value in records[0].items():
            if value:  # Mostra solo campi valorizzati
                print(f"  {key:20}: {value}")
    
    print("\n" + "=" * 50)
    print("TEST COMPLETATO")


def test_with_real_file():
    """Test con un file DOCX reale se disponibile"""
    
    # Cerca un file di test
    test_files = [
        '10.docx',
        'inventario_festos.docx',
        'test_inventory.docx'
    ]
    
    file_found = None
    for test_file in test_files:
        if os.path.exists(test_file):
            file_found = test_file
            break
    
    if file_found:
        print(f"\nTest con file reale: {file_found}")
        print("=" * 50)
        
        parser = InventoryDocxParser(file_found)
        records = parser.parse()
        
        print(f"Record trovati: {len(records)}")
        print(f"Errori: {len(parser.errors)}")
        print(f"Warning: {len(parser.warnings)}")
        
        if parser.errors:
            print("\nErrori:")
            for error in parser.errors[:5]:
                print(f"  - {error}")
                
        if parser.warnings:
            print("\nWarning:")
            for warning in parser.warnings[:5]:
                print(f"  - {warning}")
                
        if records:
            print(f"\nPrimi 3 record:")
            for i, record in enumerate(records[:3], 1):
                print(f"\nRecord {i}:")
                for key, value in record.items():
                    if value:
                        print(f"  {key:20}: {value}")
    else:
        print("\nNessun file di test trovato. Crea un file DOCX di inventario per testare.")


if __name__ == "__main__":
    # Test con dati simulati
    test_inventory_parser()
    
    # Test con file reale se disponibile
    test_with_real_file()
