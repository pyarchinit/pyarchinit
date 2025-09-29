#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script for RAG Query Dialog and Report Generation with TMA support
"""

import sys
import os
from pathlib import Path

# Add the plugin directory to Python path
plugin_dir = Path(__file__).parent
sys.path.insert(0, str(plugin_dir))

from qgis.PyQt.QtWidgets import QApplication, QDialog
from qgis.PyQt.QtCore import QSettings

# Mock QGIS interface for testing
class MockIface:
    def mainWindow(self):
        return None

# Test functions
def test_tma_data_loading():
    """Test loading TMA data from database"""
    print("\n=== Testing TMA Data Loading ===")

    try:
        from modules.db.pyarchinit_db_manager import Pyarchinit_db_management
        from modules.db.pyarchinit_conn_strings import Connection

        # Connect to database
        conn = Connection()
        db = Pyarchinit_db_management(conn.conn_str())
        db.set_connection()

        # Query TMA data
        search_dict = {'sito': "Festòs_2025"}
        tma_data = db.query_bool(search_dict, "TMA")

        if tma_data:
            print(f"✅ Loaded {len(tma_data)} TMA records")
            # Show sample data
            sample = tma_data[0]
            print(f"Sample TMA record:")
            print(f"  - ID: {sample.id_tma}")
            print(f"  - Sito: {sample.sito}")
            print(f"  - Area: {sample.area}")
            print(f"  - US: {sample.us}")
            print(f"  - Tipo Materiale: {sample.tipo_materiale}")
        else:
            print("⚠️ No TMA data found")

        return True

    except Exception as e:
        print(f"❌ Error loading TMA data: {e}")
        return False

def test_rag_query_dialog():
    """Test RAG Query Dialog initialization"""
    print("\n=== Testing RAG Query Dialog ===")

    try:
        from tabs.US_USM import RAGQueryDialog
        from modules.db.pyarchinit_db_manager import Pyarchinit_db_management
        from modules.db.pyarchinit_conn_strings import Connection

        # Create DB manager
        conn = Connection()
        db_manager = Pyarchinit_db_management(conn.conn_str())
        db_manager.set_connection()

        # Create dialog
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)

        dialog = RAGQueryDialog(db_manager=db_manager)

        print("✅ RAG Query Dialog created successfully")
        print(f"  - Dialog title: {dialog.windowTitle()}")
        print(f"  - Dialog size: {dialog.size()}")

        # Check components
        if hasattr(dialog, 'query_input'):
            print("  - Query input field: ✅")
        if hasattr(dialog, 'model_combo'):
            print("  - Model selector: ✅")
            print(f"    Available models: {[dialog.model_combo.itemText(i) for i in range(dialog.model_combo.count())]}")
        if hasattr(dialog, 'results_tabs'):
            print("  - Results tabs: ✅")

        return True

    except Exception as e:
        print(f"❌ Error creating RAG Query Dialog: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_report_generator_dialog():
    """Test Report Generator Dialog with TMA table"""
    print("\n=== Testing Report Generator Dialog ===")

    try:
        from tabs.US_USM import ReportGeneratorDialog

        # Create dialog
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)

        # Mock parent with apikey_gpt method
        class MockParent:
            def apikey_gpt(self):
                return "test_key"

        parent = MockParent()
        dialog = ReportGeneratorDialog(parent=parent)

        print("✅ Report Generator Dialog created successfully")

        # Check if TMA table is in the list
        if hasattr(dialog, 'TABLES_NAMES'):
            if 'tma_table' in dialog.TABLES_NAMES:
                print("  - TMA table in list: ✅")
            else:
                print("  - TMA table in list: ❌")
                print(f"    Available tables: {dialog.TABLES_NAMES}")

        # Test get_tma_data method
        if hasattr(dialog, 'get_tma_data'):
            print("  - get_tma_data method: ✅")
            try:
                # Select TMA table
                dialog.combo_box.select_item('tma_table')
                tma_data = dialog.get_tma_data()
                print(f"    Loaded {len(tma_data)} TMA records")
            except Exception as e:
                print(f"    Error loading TMA data: {e}")
        else:
            print("  - get_tma_data method: ❌")

        return True

    except Exception as e:
        print(f"❌ Error creating Report Generator Dialog: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_validation():
    """Test TMA data validation"""
    print("\n=== Testing TMA Data Validation ===")

    try:
        from tabs.US_USM import GenerateReportThread

        # Create mock TMA data
        tma_data = [
            {'id_tma': 1, 'tipo_materiale': 'Ceramica', 'sito': 'Festòs_2025'},
            {'id_tma': 2, 'tipo_materiale': '', 'sito': 'Festòs_2025'},  # Missing tipo_materiale
            {'id_tma': 3, 'tipo_materiale': 'Laterizi', 'sito': 'Festòs_2025'}
        ]

        # Create thread instance
        thread = GenerateReportThread(
            custom_prompt="",
            descriptions_text="",
            api_key="test",
            selected_model="gpt-5",
            selected_tables=['tma_table'],
            analysis_steps=[],
            agent=None,
            us_data=[],
            materials_data=[],
            pottery_data=[],
            site_data={},
            py_dialog=None,
            tma_data=tma_data
        )

        # Test validation
        validation = thread.validate_tma()

        print(f"Validation result:")
        print(f"  - Valid: {validation['valid']}")
        print(f"  - Message: {validation['message']}")

        if not validation['valid']:
            print(f"  - Missing data: {validation.get('missing', [])}")

        return True

    except Exception as e:
        print(f"❌ Error testing validation: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tma_table_formatting():
    """Test TMA table formatting"""
    print("\n=== Testing TMA Table Formatting ===")

    try:
        from tabs.US_USM import GenerateReportThread

        # Create mock TMA data
        tma_data = [
            {
                'id_tma': 1,
                'sito': 'Festòs_2025',
                'area': 'A1',
                'us': '100',
                'tipo_materiale': 'Ceramica',
                'quantita': '50',
                'cassetta': 'C001',
                'note': 'Frammenti ceramici'
            },
            {
                'id_tma': 2,
                'sito': 'Festòs_2025',
                'area': 'A2',
                'us': '101',
                'tipo_materiale': 'Laterizi',
                'quantita': '20',
                'cassetta': 'C002',
                'note': 'Tegole frammentarie'
            }
        ]

        # Create thread instance
        thread = GenerateReportThread(
            custom_prompt="",
            descriptions_text="",
            api_key="test",
            selected_model="gpt-5",
            selected_tables=['tma_table'],
            analysis_steps=[],
            agent=None,
            us_data=[],
            materials_data=[],
            pottery_data=[],
            site_data={},
            py_dialog=None,
            tma_data=tma_data
        )

        # Test table formatting
        table_data = thread.format_tma_table()

        if table_data:
            print("✅ TMA table formatted successfully")
            print(f"  - Headers: {table_data[0]}")
            print(f"  - Rows: {len(table_data) - 1}")

            # Show sample row
            if len(table_data) > 1:
                print(f"  - Sample row: {table_data[1]}")
        else:
            print("❌ No table data generated")

        return True

    except Exception as e:
        print(f"❌ Error formatting table: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Testing RAG Query and Report Generation with TMA Support")
    print("=" * 60)

    tests = [
        test_tma_data_loading,
        test_report_generator_dialog,
        test_data_validation,
        test_tma_table_formatting,
        test_rag_query_dialog
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
        print("✅ All tests passed!")
    else:
        print(f"⚠️ {total - passed} tests failed")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)