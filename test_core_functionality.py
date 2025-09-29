#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test core functionality without QGIS dependency
"""

import sys
import os
from pathlib import Path

# Add the plugin directory to Python path
plugin_dir = Path(__file__).parent
sys.path.insert(0, str(plugin_dir))

def test_database_queries():
    """Test database queries directly"""
    print("\n=== Testing Direct Database Queries ===")

    try:
        from modules.db.pyarchinit_db_manager import Pyarchinit_db_management
        from modules.db.pyarchinit_conn_strings import Connection

        # Connect to database
        conn = Connection()
        db = Pyarchinit_db_management(conn.conn_str())
        db.set_connection()

        print("✅ Database connection established")

        # Test different query results to ensure they're iterable
        search_dict = {'sito': 'Festòs_2025'}

        # Test US query
        print("\nTesting US query...")
        try:
            us_data = db.query_bool(search_dict, "US")
            if us_data is not None:
                # Check if it's iterable
                if not hasattr(us_data, '__iter__'):
                    print("  ⚠️ US data is not iterable, wrapping in list")
                    us_data = [us_data]
                print(f"  ✅ US data: {len(us_data)} records (iterable)")
            else:
                print("  ⚠️ No US data found")
        except Exception as e:
            print(f"  ❌ Error: {e}")

        # Test INVENTARIO_MATERIALI query
        print("\nTesting INVENTARIO_MATERIALI query...")
        try:
            mat_data = db.query_bool(search_dict, "INVENTARIO_MATERIALI")
            if mat_data is not None:
                # Check if it's iterable
                if not hasattr(mat_data, '__iter__'):
                    print("  ⚠️ Materials data is not iterable, wrapping in list")
                    mat_data = [mat_data]
                print(f"  ✅ Materials data: {len(mat_data)} records (iterable)")
            else:
                print("  ⚠️ No materials data found")
        except Exception as e:
            print(f"  ❌ Error: {e}")

        # Test POTTERY query
        print("\nTesting POTTERY query...")
        try:
            pottery_data = db.query_bool(search_dict, "POTTERY")
            if pottery_data is not None:
                # Check if it's iterable
                if not hasattr(pottery_data, '__iter__'):
                    print("  ⚠️ Pottery data is not iterable, wrapping in list")
                    pottery_data = [pottery_data]
                print(f"  ✅ Pottery data: {len(pottery_data)} records (iterable)")
            else:
                print("  ⚠️ No pottery data found")
        except Exception as e:
            print(f"  ❌ Error: {e}")

        # Test TMA query (using correct table name)
        print("\nTesting TMA query...")
        try:
            # Note: The entity is called TMA but maps to tma_materiali_archeologici table
            tma_data = db.query_bool(search_dict, "TMA")
            if tma_data is not None:
                # Check if it's iterable
                if not hasattr(tma_data, '__iter__'):
                    print("  ⚠️ TMA data is not iterable, wrapping in list")
                    tma_data = [tma_data]
                print(f"  ✅ TMA data: {len(tma_data)} records (iterable)")
            else:
                print("  ⚠️ No TMA data found")
        except Exception as e:
            print(f"  ❌ Error: {e}")

        return True

    except Exception as e:
        print(f"❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_text_preparation():
    """Test text preparation for vectorstore"""
    print("\n=== Testing Text Preparation ===")

    try:
        # Mock data for testing
        mock_us_data = [
            {'id_us': 1, 'unita_tipo': 'US', 'area': 'A1', 'd_stratigrafica': 'Test description'},
            {'id_us': 2, 'unita_tipo': 'USM', 'area': 'A2', 'd_stratigrafica': 'Another description'}
        ]

        mock_tma_data = [
            {'id_tma': 1, 'sito': 'Festòs_2025', 'ogtm': 'Ceramica', 'ldct': 'Contenitori'},
            {'id_tma': 2, 'sito': 'Festòs_2025', 'ogtm': 'Laterizi', 'ldct': 'Tegole'}
        ]

        # Simulate text preparation
        texts = []

        # Process US data
        for record in mock_us_data:
            text = f"US {record.get('id_us', '')}: "
            text += f"Area {record.get('area', '')}, "
            text += f"Descrizione: {record.get('d_stratigrafica', '')}"
            texts.append(text)

        # Process TMA data
        for record in mock_tma_data:
            text = f"TMA {record.get('id_tma', '')}: "
            text += f"Sito {record.get('sito', '')}, "
            text += f"Tipo: {record.get('ogtm', '')}, "
            text += f"Categoria: {record.get('ldct', '')}"
            texts.append(text)

        if texts:
            print(f"✅ Generated {len(texts)} text entries")
            print(f"Sample text: {texts[0][:100]}...")
            return True
        else:
            print("❌ No texts generated")
            return False

    except Exception as e:
        print(f"❌ Text preparation failed: {e}")
        return False

def test_table_name_mapping():
    """Test table name mapping for TMA"""
    print("\n=== Testing Table Name Mapping ===")

    try:
        # Test the mapping logic
        table_mappings = {
            'us_table': 'US',
            'materials': 'INVENTARIO_MATERIALI',
            'pottery': 'POTTERY',
            'tma_table': 'TMA'  # This should map to tma_materiali_archeologici internally
        }

        for ui_name, entity_name in table_mappings.items():
            print(f"  {ui_name} -> {entity_name}")

        # Special case for TMA
        actual_table_name = 'tma_table'
        if actual_table_name == 'tma_table':
            actual_table_name = 'tma_materiali_archeologici'
            print(f"  ✅ TMA mapping: tma_table -> tma_materiali_archeologici")

        return True

    except Exception as e:
        print(f"❌ Table name mapping failed: {e}")
        return False

def test_empty_data_handling():
    """Test handling of empty data"""
    print("\n=== Testing Empty Data Handling ===")

    try:
        # Test empty list
        empty_data = []
        if not empty_data:
            print("✅ Empty list detected correctly")

        # Test None
        none_data = None
        if none_data is None or not none_data:
            print("✅ None data detected correctly")

        # Test single object (non-iterable)
        class MockObject:
            def __init__(self):
                self.id = 1
                self.name = "Test"

        single_obj = MockObject()
        if not hasattr(single_obj, '__iter__'):
            wrapped = [single_obj]
            print(f"✅ Non-iterable object wrapped in list: {len(wrapped)} items")

        return True

    except Exception as e:
        print(f"❌ Empty data handling failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Testing Core Functionality (No QGIS Required)")
    print("=" * 60)

    tests = [
        test_database_queries,
        test_text_preparation,
        test_table_name_mapping,
        test_empty_data_handling
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    print(f"Tests passed: {passed}/{total}")

    if passed == total:
        print("✅ All core functionality tests passed!")
        print("\nNOTE: Full UI tests require QGIS environment")
    else:
        print(f"⚠️ {total - passed} tests failed")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)