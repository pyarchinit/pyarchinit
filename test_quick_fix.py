#!/usr/bin/env python3
"""
Test rapido per verificare che il parser inventario funzioni
"""

import sys
import os

# Test del parser
print("TEST PARSER INVENTARIO TMA")
print("=" * 50)

# Test import classi
try:
    from modules.db.entities.TMA import TMA
    print("✓ Import TMA class OK")
except Exception as e:
    print(f"✗ Errore import TMA: {e}")

try:
    from modules.utility.festos_inventory_parser import FestosInventoryParser
    print("✓ Import FestosInventoryParser OK")
except Exception as e:
    print(f"✗ Errore import FestosInventoryParser: {e}")

try:
    from modules.utility.tma_import_parser_extended import TMAImportManagerExtended
    print("✓ Import TMAImportManagerExtended OK")
except Exception as e:
    print(f"✗ Errore import TMAImportManagerExtended: {e}")

# Test creazione istanze
print("\nTest creazione istanze:")
try:
    parser = FestosInventoryParser()
    print("✓ FestosInventoryParser creato")
except Exception as e:
    print(f"✗ Errore creazione parser: {e}")

# Test parsing range cassette
print("\nTest parsing range cassette:")
try:
    parser = FestosInventoryParser()
    test_ranges = ['1-5', '10', '15a-20']
    for r in test_ranges:
        result = parser._parse_cassette_range(r)
        print(f"  {r} → {result}")
except Exception as e:
    print(f"✗ Errore test range: {e}")

print("\n" + "=" * 50)
print("TEST COMPLETATO")
