#!/usr/bin/env python3
"""
Test standalone del parser inventario senza dipendenze QGIS
"""

import sys
import os

# Test parser inventario base
print("TEST PARSER INVENTARIO STANDALONE")
print("=" * 50)

# 1. Test import parser Festos
try:
    from modules.utility.festos_inventory_parser import FestosInventoryParser
    print("✓ Import FestosInventoryParser OK")
    
    # Crea istanza
    parser = FestosInventoryParser()
    print("✓ Parser creato")
    
    # Test metodi base
    print("\nTest metodi parser:")
    
    # Test range cassette
    ranges = ['1-5', '10', '100-102', '15a']
    for r in ranges:
        result = parser._parse_cassette_range(r)
        print(f"  Range '{r}' → {result}")
    
    # Test estrazione materiale
    descriptions = [
        "Frammenti ceramici",
        "Ossa animali", 
        "Blocchi di pietra",
        "Oggetti in ferro"
    ]
    print("\nTest estrazione tipo materiale:")
    for desc in descriptions:
        material = parser._extract_tipo_materiale(desc)
        print(f"  '{desc}' → {material}")
    
    # Test estrazione area
    area_descriptions = [
        "Vano XCIV strato pavimentale",
        "Area B settore nord",
        "Piazzale I"
    ]
    print("\nTest estrazione area:")
    for desc in area_descriptions:
        area = parser._extract_area(desc)
        print(f"  '{desc}' → '{area}'")
    
except Exception as e:
    print(f"✗ Errore: {e}")
    import traceback
    traceback.print_exc()

# 2. Test creazione record
print("\n\nTest creazione record inventario:")
try:
    parser = FestosInventoryParser()
    
    # Simula una riga di inventario
    cells = ['1-3', 'Frammenti ceramici dal vano XCIV', '1965']
    headers = ['Cassette', 'Descrizione', 'Anno']
    
    records = parser._parse_row(cells, headers, 'Festos', 'Magazzino 3-4', 1, 2)
    
    print(f"Record generati: {len(records)}")
    if records:
        print("\nPrimo record:")
        for key, value in records[0].items():
            if value:  # Mostra solo campi valorizzati
                print(f"  {key:20}: {value}")
                
except Exception as e:
    print(f"✗ Errore: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("TEST COMPLETATO")
print("\nSe tutti i test sono passati, il parser è pronto per l'uso.")
print("Riavvia QGIS e riprova l'importazione.")
